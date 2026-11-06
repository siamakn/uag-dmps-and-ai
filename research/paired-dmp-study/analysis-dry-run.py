#!/usr/bin/env python3
"""Draft synthetic-only arithmetic check; never a human-review/production adapter."""
import argparse
from collections import Counter
import json
from pathlib import Path

MARKER = "SYNTHETIC_ONLY_NOT_HUMAN_REFERENCE_NOT_SCIENTIFIC_RESULTS"
STATES = ("score", "NA", "uncertainty", "missing", "failure", "instrument_undefined")
CONDITIONS = ("F0", "F1")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fields(obj, expected, where):
    require(isinstance(obj, dict) and set(obj) == set(expected),
            "{}: expected fields {}".format(where, sorted(expected)))


def synthetic_id(value):
    return isinstance(value, str) and value.startswith("SYNTHETIC_") and len(value) > 10


def unique_ids(values, where):
    require(isinstance(values, list) and values and all(synthetic_id(x) for x in values),
            where + ": nonempty synthetic ID list required")
    require(len(set(values)) == len(values), where + ": duplicate ID")


def validate(data):
    fields(data, ("notice", "repeat_count", "projects", "criteria", "reference", "models"), "input")
    require(data["notice"] == MARKER, "synthetic-only notice required")
    require(type(data["repeat_count"]) is int and data["repeat_count"] == 1,
            "only repeat_count integer 1 is supported")
    unique_ids(data["criteria"], "criteria")
    criteria = set(data["criteria"])
    projects = data["projects"]
    require(isinstance(projects, list) and len(projects) == 6, "exactly six synthetic projects required")
    project_ids, docs = set(), {}
    for project in projects:
        fields(project, ("project", "documents"), "project")
        pid = project["project"]
        require(synthetic_id(pid) and pid not in project_ids, "invalid/duplicate project ID")
        project_ids.add(pid)
        require(isinstance(project["documents"], list) and len(project["documents"]) == 2,
                "each project requires exactly two documents")
        phases = set()
        for doc in project["documents"]:
            fields(doc, ("document", "phase", "defined_criteria"), "document")
            did = doc["document"]
            require(synthetic_id(did) and did not in docs, "invalid/duplicate document ID")
            require(doc["phase"] in ("early", "late") and doc["phase"] not in phases,
                    "one early and one late document required")
            phases.add(doc["phase"])
            defined = doc["defined_criteria"]
            require(isinstance(defined, list) and all(isinstance(x, str) for x in defined),
                    "defined_criteria must be an ID list")
            require(len(set(defined)) == len(defined) and set(defined) <= criteria,
                    "duplicate/unknown defined criterion")
            docs[did] = (pid, set(defined))
    expected = {(did, cid) for did in docs for cid in criteria}

    def index(rows, model):
        require(isinstance(rows, list), "rows must be a list")
        indexed = {}
        for row in rows:
            keys = ("document", "criterion", "state", "value", "reason", "applicability")
            fields(row, keys + (("condition",) if model else ()), "row")
            did, cid = row["document"], row["criterion"]
            require(isinstance(did, str) and isinstance(cid, str) and (did, cid) in expected,
                    "unknown document/criterion")
            state = row["state"]
            require(isinstance(state, str) and state in STATES, "unknown state")
            require(isinstance(row["reason"], str), "reason must be a string")
            if state == "score":
                require(type(row["value"]) is int and row["value"] in (0, 1, 2),
                        "score must be ordinal integer 0/1/2 (bool/float/native 0-100 excluded)")
                require(row["reason"] == "", "numeric rows require an empty reason")
            else:
                require(row["value"] is None and bool(row["reason"].strip()),
                        "non-score rows require null value and an explicit reason")
            applicability = row["applicability"]
            require(isinstance(applicability, str) and applicability in
                    ("applicable", "NA", "unknown", "instrument_undefined"), "invalid applicability")
            implied = {"score": "applicable", "NA": "NA", "instrument_undefined": "instrument_undefined"}
            require(applicability == implied[state] if state in implied else applicability in ("applicable", "unknown"),
                    "state/applicability contradiction")
            defined = cid in docs[did][1]
            require((state == "instrument_undefined") == (not defined),
                    "instrument_undefined must match anticipated instrument mask")
            if model:
                require(isinstance(row["condition"], str) and row["condition"] in CONDITIONS,
                        "only F0/F1 ordinal conditions supported; native N0 excluded")
                key = (row["condition"], did, cid)
            else:
                key = (did, cid)
            require(key not in indexed, "duplicate row")
            indexed[key] = row
        return indexed

    reference = index(data["reference"], False)
    require(set(reference) == expected, "complete reference roster required; missing reference rows")
    models = index(data["models"], True)
    return docs, reference, models


def fraction(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator,
            "rate": numerator / denominator if denominator else None}


def average(values):
    return sum(values) / len(values) if values and all(x is not None for x in values) else None


def analyze(data):
    docs, reference, models = validate(data)
    criteria = sorted(data["criteria"])
    documents, excluded, common_excluded = [], [], []
    all_counts = {condition: Counter() for condition in CONDITIONS}
    all_reference = Counter()
    reference_applicability = Counter()
    for did in sorted(docs):
        pid, defined = docs[did]
        refs = {cid: reference[(did, cid)] for cid in criteria}
        all_reference.update(row["state"] for row in refs.values())
        reference_applicability.update(row["applicability"] for row in refs.values())
        applicable = [cid for cid in criteria if refs[cid]["applicability"] == "applicable" and cid in defined]
        condition_rows, counts = {}, {}
        for condition in CONDITIONS:
            rows, count = {}, Counter()
            for cid in criteria:
                supplied = (condition, did, cid) in models
                row = models.get((condition, did, cid))
                if row is None:
                    state = "missing" if cid in defined else "instrument_undefined"
                    row = {"state": state, "value": None,
                           "applicability": "unknown" if cid in defined else "instrument_undefined",
                           "reason": "missing_model_row" if cid in defined else "anticipated_undefined_cell"}
                rows[cid] = row
                human = refs[cid]
                count["anticipated_rows"] += 1
                count["supplied_rows"] += int(supplied)
                count["defined_rows"] += int(cid in defined)
                count["all_state_" + row["state"]] += 1
                count["human_applicable_defined"] += int(cid in applicable)
                if cid in applicable:
                    count["on_fixed_denominator_" + row["state"]] += 1
                    if row["state"] != "score":
                        count["fixed_reason_" + row["reason"]] += 1
                if human["applicability"] in ("applicable", "NA") and row["applicability"] in ("applicable", "NA"):
                    count["joint_known_applicability"] += 1
                    count["applicability_disagreements"] += int(human["applicability"] != row["applicability"])
                count["human_NA_model_numeric"] += int(human["state"] == "NA" and row["state"] == "score")
                count["human_numeric_model_NA"] += int(human["state"] == "score" and row["state"] == "NA")
                if human["state"] != "score" or row["state"] != "score":
                    excluded.append({"document": did, "criterion": cid, "condition": condition,
                                     "human_state": human["state"], "human_reason": human["reason"],
                                     "human_applicability": human["applicability"],
                                     "model_applicability": row["applicability"],
                                     "model_state": row["state"], "model_reason": row["reason"],
                                     "model_row_supplied": supplied, "on_fixed_denominator": cid in applicable})
            condition_rows[condition] = rows
            counts[condition] = count
            all_counts[condition].update(count)
        common = [cid for cid in applicable if refs[cid]["state"] == "score" and all(condition_rows[c][cid]["state"] == "score"
                                                    for c in CONDITIONS)]
        for cid in criteria:
            if cid not in common:
                common_excluded.append({"document": did, "criterion": cid,
                                        "on_fixed_denominator": cid in applicable,
                                        "reference": refs[cid],
                                        "conditions": {c: condition_rows[c][cid] for c in CONDITIONS}})
        errors = {c: sum(condition_rows[c][cid]["value"] != refs[cid]["value"] for cid in common)
                  for c in CONDITIONS}
        rates = {c: fraction(errors[c], len(common)) for c in CONDITIONS}
        delta = (errors["F1"] - errors["F0"]) / len(common) if common else None
        documents.append({"project": pid, "document": did,
                          "human_applicable_defined": len(applicable),
                          "common_coverage": fraction(len(common), len(applicable)),
                          "common_criteria": common, "disagreement": rates,
                          "F1_minus_F0": delta, "conditions": {c: summarize(counts[c]) for c in CONDITIONS},
                          "undefined_reason": None if common else "no_common_applicable_numeric_criteria"})
    project_results = []
    reasons = []
    for pid in sorted({value[0] for value in docs.values()}):
        selected = [d for d in documents if d["project"] == pid]
        undefined_docs = [d["document"] for d in selected if d["F1_minus_F0"] is None]
        if undefined_docs:
            reasons.append({"project": pid, "documents": undefined_docs,
                            "reason": "required_document_contrast_undefined"})
        project_results.append({"project": pid, "documents": [d["document"] for d in selected],
                                "F1_minus_F0": average([d["F1_minus_F0"] for d in selected]),
                                "common_coverage": fraction(sum(len(d["common_criteria"]) for d in selected),
                                                            sum(d["human_applicable_defined"] for d in selected)),
                                "condition_numeric_coverage": {
                                    c: fraction(sum(d["conditions"][c]["numeric_coverage"]["numerator"] for d in selected),
                                                sum(d["human_applicable_defined"] for d in selected)) for c in CONDITIONS},
                                "disagreement": {c: average([d["disagreement"][c]["rate"] for d in selected])
                                                 for c in CONDITIONS}})
    fixed_total = sum(d["human_applicable_defined"] for d in documents)
    common_total = sum(len(d["common_criteria"]) for d in documents)
    return {"notice": MARKER, "status": "draft_arithmetic_prototype_R1_only",
            "primary_conditional_F1_minus_F0": average([p["F1_minus_F0"] for p in project_results]),
            "undefined_reasons": reasons, "required_projects": 6, "required_documents": 12,
            "common_coverage": fraction(common_total, fixed_total),
            "reference_states": {s: all_reference[s] for s in STATES},
            "reference_applicability": {s: reference_applicability[s] for s in
                                        ("applicable", "NA", "unknown", "instrument_undefined")},
            "conditions": {c: summarize(all_counts[c]) for c in CONDITIONS},
            "projects": project_results, "documents": documents,
            "condition_specific_nonnumeric_rows": excluded,
            "excluded_from_common_primary": common_excluded,
            "not_estimated": ["request_attempt_or_completion_counts", "native_0_100_agreement",
                              "human_human_agreement", "repeat_variation", "inference_or_ranking"]}


def summarize(count):
    fixed = count["human_applicable_defined"]
    return {"anticipated_rows": count["anticipated_rows"], "supplied_rows": count["supplied_rows"],
            "defined_rows": count["defined_rows"], "human_applicable_defined": fixed,
            "all_states": {s: count["all_state_" + s] for s in STATES},
            "fixed_denominator_states": {s: count["on_fixed_denominator_" + s] for s in STATES},
            "numeric_coverage": fraction(count["on_fixed_denominator_score"], fixed),
            "fixed_denominator_exclusion_reasons": {k[len("fixed_reason_"):]: count[k]
                                                   for k in sorted(count) if k.startswith("fixed_reason_")},
            "human_NA_model_numeric": count["human_NA_model_numeric"],
            "human_numeric_model_NA": count["human_numeric_model_NA"],
            "applicability_disagreement_on_joint_known_states": fraction(
                count["applicability_disagreements"], count["joint_known_applicability"])}


def example():
    """Artificial roster: criterion IDs have no link to the actual rubric."""
    criteria = ["SYNTHETIC_CRITERION_A", "SYNTHETIC_CRITERION_B", "SYNTHETIC_CRITERION_C"]
    data = {"notice": MARKER, "repeat_count": 1, "criteria": criteria,
            "projects": [], "reference": [], "models": []}
    for number in range(1, 7):
        pid = "SYNTHETIC_PROJECT_{:02d}".format(number)
        project = {"project": pid, "documents": []}
        for phase in ("early", "late"):
            did = pid + "_" + phase.upper()
            project["documents"].append({"document": did, "phase": phase, "defined_criteria": criteria[:]})
            for cid in criteria:
                row = {"document": did, "criterion": cid, "state": "score", "value": 0, "reason": "", "applicability": "applicable"}
                data["reference"].append(row)
                for condition in CONDITIONS:
                    model = dict(row, condition=condition)
                    if number == 1 and phase == "early" and cid == criteria[0] and condition == "F1":
                        model["value"] = 1
                    data["models"].append(model)
        data["projects"].append(project)
    return data


def reject_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON object key: " + key)
        result[key] = value
    return result


def reject_nonfinite_json(value):
    raise ValueError("nonfinite JSON number forbidden: " + value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--example", action="store_true", help="analyze built-in artificial fixture")
    source.add_argument("--input", type=Path, help="synthetic-only internal JSON fixture")
    parser.add_argument("--output", type=Path, help="result JSON; defaults to stdout")
    args = parser.parse_args()
    try:
        data = example() if args.example else json.loads(
            args.input.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_json_keys,
            parse_constant=reject_nonfinite_json)
        output = json.dumps(analyze(data), indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    except (ValueError, OSError, TypeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
