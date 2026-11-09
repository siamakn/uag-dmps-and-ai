"""Human-review pilot support: the PILOT-01 task, record validation and append-only storage.

The dashboard's *Review (pilot)* mode lets a person record a criterion assessment. This module is
its Python side:

- `pilot_task()` builds the PILOT-01 form fixture (PathOS D3.5 v2.0, criterion 1b, end-project
  cell) from research/paired-dmp-study/pilot-template.json and the draft anchors in
  pilot-start.md, with file checksums. It carries no score, no evidence and no suggestion.
- `schema_validate()` applies research/paired-dmp-study/human-review-record.schema.json with a
  small stdlib implementation of the JSON-Schema keywords that file uses. The dashboard has a
  JavaScript copy; dashboard/review-fixtures.json keeps the two in step.
- `pilot_checks()` adds the record rules the schema cannot express (scope versus criterion rows,
  artifact references, content hash, supersession).
- `submit()` stores a locked record with O_EXCL: a submitted record is never rewritten. A
  correction is a new record whose provenance.supersedes_record_id names the original.

The user deferred the pilot on 2026-11-04. Nothing here creates a record, a score or a
disposition by itself; only a human submission through the form does.

    python scripts/review.py task                 # print the PILOT-01 fixture
    python scripts/review.py validate FILE.json   # check a record or submission file
    python scripts/review.py list [--state-dir DIR]

Stdlib only.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

RESEARCH = os.path.join(common.ROOT, "research", "paired-dmp-study")
SCHEMA_PATH = os.path.join(RESEARCH, "human-review-record.schema.json")
TEMPLATE_PATH = os.path.join(RESEARCH, "pilot-template.json")
PILOT_START = os.path.join(RESEARCH, "pilot-start.md")
PROTOCOL = os.path.join(RESEARCH, "human-review-protocol-draft.md")

STATE_SCHEMA = "dmpbench.review-state"
SUBMISSION_SCHEMA = "dmpbench.review-submission"
VERSION = 1
REVIEW_DIR = "review"
STATE_FILE = "review_state.json"
RECORDS_DIR = "records"
FRAMEWORK16 = ["1a", "1b", "2a", "2b", "3a", "3b", "3c", "4a", "4b", "4c", "5a", "5b", "5c", "5d", "6a", "6b"]
SERVABLE_ROOT = os.path.join("data", "paired-dmp-corpus")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(obj):
    """Same canonical form as the dashboard: sorted keys, indent 1, UTF-8, trailing newline."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1) + "\n"


def _read(path):
    with open(path, "rb") as f:
        return f.read()


def load_schema():
    return json.loads(_read(SCHEMA_PATH).decode("utf-8"))


# ------------------------------------------------------------------ JSON-Schema subset
DATE_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")


def _is_type(x, t):
    if t == "null":
        return x is None
    if t == "boolean":
        return isinstance(x, bool)
    if t == "integer":
        return isinstance(x, int) and not isinstance(x, bool)
    if t == "number":
        return isinstance(x, (int, float)) and not isinstance(x, bool)
    if t == "string":
        return isinstance(x, str)
    if t == "array":
        return isinstance(x, list)
    if t == "object":
        return isinstance(x, dict)
    return False


def _same(a, b):
    """JSON equality: true is not 1, false is not 0."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    return type(a) is type(b) and a == b if not isinstance(a, (dict, list)) else \
        json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def schema_validate(schema, inst, root=None):
    """Validate inst against schema. Supports the keywords the record schema uses:
    $ref (local), allOf, anyOf, if/then/else, const, enum, type, required, properties,
    additionalProperties (false), items, minItems, maxItems, uniqueItems, minLength,
    pattern, minimum, maximum, format date-time. Returns a list of "path: message" strings."""
    root = root if root is not None else schema
    errs = []

    def v(s, x, p):
        if s is True or s == {}:
            return
        if "$ref" in s:
            ref = s["$ref"]
            if not ref.startswith("#/"):
                errs.append("%s: unsupported $ref %s" % (p, ref))
            else:
                t = root
                for part in ref[2:].split("/"):
                    t = t[part]
                v(t, x, p)
        for sub in s.get("allOf", []):
            v(sub, x, p)
        if "anyOf" in s and not any(not sub_errs(sub, x, p) for sub in s["anyOf"]):
            errs.append("%s: matches none of the allowed alternatives" % p)
        if "if" in s:
            if not sub_errs(s["if"], x, p):
                if "then" in s:
                    v(s["then"], x, p)
            elif "else" in s:
                v(s["else"], x, p)
        if "const" in s and not _same(x, s["const"]):
            errs.append("%s: must be %s" % (p, json.dumps(s["const"])))
        if "enum" in s and not any(_same(x, e) for e in s["enum"]):
            errs.append("%s: %s is not one of %s" % (p, json.dumps(x), json.dumps(s["enum"])))
        if "type" in s:
            types = s["type"] if isinstance(s["type"], list) else [s["type"]]
            if not any(_is_type(x, t) for t in types):
                errs.append("%s: expected %s, got %s" % (p, "/".join(types), json.dumps(x)[:60]))
                return
        if isinstance(x, dict):
            for k in s.get("required", []):
                if k not in x:
                    errs.append("%s: missing required field %s" % (p, k))
            props = s.get("properties", {})
            for k, val in x.items():
                if k in props:
                    v(props[k], val, p + "." + k)
                elif s.get("additionalProperties") is False:
                    errs.append("%s: unexpected field %s" % (p, k))
        if isinstance(x, list):
            if "minItems" in s and len(x) < s["minItems"]:
                errs.append("%s: needs at least %d item(s)" % (p, s["minItems"]))
            if "maxItems" in s and len(x) > s["maxItems"]:
                errs.append("%s: allows at most %d item(s)" % (p, s["maxItems"]))
            if s.get("uniqueItems"):
                seen = [json.dumps(i, sort_keys=True) for i in x]
                if len(seen) != len(set(seen)):
                    errs.append("%s: items must be unique" % p)
            if "items" in s:
                for i, item in enumerate(x):
                    v(s["items"], item, "%s[%d]" % (p, i))
        if isinstance(x, str):
            if "minLength" in s and len(x) < s["minLength"]:
                errs.append("%s: must not be empty" % p if s["minLength"] == 1 else
                            "%s: shorter than %d" % (p, s["minLength"]))
            if "pattern" in s and not re.search(s["pattern"], x):
                errs.append("%s: does not match %s" % (p, s["pattern"]))
            if s.get("format") == "date-time" and not DATE_TIME.match(x):
                errs.append("%s: not an RFC 3339 date-time" % p)
        if _is_type(x, "number"):
            if "minimum" in s and x < s["minimum"]:
                errs.append("%s: below %s" % (p, s["minimum"]))
            if "maximum" in s and x > s["maximum"]:
                errs.append("%s: above %s" % (p, s["maximum"]))

    def sub_errs(s, x, p):
        before = len(errs)
        v(s, x, p)
        got = errs[before:]
        del errs[before:]
        return got

    v(schema, inst, "$")
    return errs


# ------------------------------------------------------------------ record rules beyond the schema
def content_hash(record):
    r = json.loads(json.dumps(record))
    r.setdefault("provenance", {})["record_content_sha256"] = None
    return hashlib.sha256(canonical(r).encode("utf-8")).hexdigest()


def pilot_checks(record, existing_ids=()):
    """Cross-field rules the JSON Schema cannot state. Returns problem strings."""
    out = []
    if record.get("record_kind") != "pilot_calibration":
        out.append("this review mode only accepts pilot_calibration records")
    ins = record.get("instrument") or {}
    rows = [c.get("criterion_id") for c in record.get("criteria") or []]
    scope = record.get("assessment_scope") or {}
    if len(set(rows)) != len(rows):
        out.append("a criterion appears twice")
    if any(r not in (ins.get("criterion_ids") or []) for r in rows):
        out.append("a criterion row is not in the declared instrument")
    if sorted(scope.get("assessed_criterion_ids") or []) != sorted(rows):
        out.append("assessment_scope.assessed_criterion_ids must list exactly the criterion rows")
    if scope.get("scope") == "single_criterion_pilot" and len(rows) != 1:
        out.append("a single-criterion pilot has exactly one criterion row")
    ids = {a.get("artifact_id") for a in record.get("artifacts") or []}
    doc = record.get("document") or {}
    ctx = record.get("assessment_context") or {}
    refs = list(doc.get("source_document_artifact_ids") or []) + [
        ctx.get("packet_artifact_id"), ctx.get("canonical_full_text_artifact_id"), ins.get("rubric_artifact_id")]
    for c in record.get("criteria") or []:
        refs.append((c.get("score") or {}).get("anchors_artifact_id"))
        for loc in c.get("evidence") or []:
            refs.append(loc.get("artifact_id"))
            if loc.get("text_start") is not None:
                if loc.get("text_end_exclusive") is None or loc["text_end_exclusive"] < loc["text_start"] \
                        or not loc.get("offset_units"):
                    out.append("a text offset needs an end at or after its start and named units")
    for r in refs:
        if r is not None and r not in ids:
            out.append("artifact %s is referenced but not listed in artifacts" % r)
    if record.get("record_status") == "submitted_locked":
        for c in record.get("criteria") or []:
            if (c.get("score") or {}).get("entry_status") == "not_entered":
                out.append("criterion %s: a submitted record needs an explicit choice (a score, NA, uncertain "
                           "or withheld); 'not entered' only exists in drafts" % c.get("criterion_id"))
    prov = record.get("provenance") or {}
    if prov.get("record_content_sha256") and prov["record_content_sha256"] != content_hash(record):
        out.append("record_content_sha256 does not match the record content")
    if record.get("record_status") == "submitted_locked" and not prov.get("record_content_sha256"):
        out.append("a locked record needs record_content_sha256")
    sup = prov.get("supersedes_record_id")
    if sup is not None and sup not in existing_ids:
        out.append("supersedes_record_id %s does not name a stored record" % sup)
    if sup is not None and sup == record.get("record_id"):
        out.append("a record cannot supersede itself")
    return out


def validate_record(record, existing_ids=(), schema=None):
    return schema_validate(schema or load_schema(), record) + pilot_checks(record, existing_ids)


# ------------------------------------------------------------------ the PILOT-01 fixture
def parse_anchor_table(path=PILOT_START):
    """The draft anchors exactly as written in pilot-start.md. Raises if the table is gone."""
    rows, inside = [], False
    for line in _read(path).decode("utf-8").splitlines(True):
        line = line.rstrip("\n")
        if line.startswith("| Response |"):
            inside = True
            continue
        if inside:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in line.strip("|").split("|")]
            if set(cells[0]) <= {"-", " ", ":"}:
                continue
            rows.append({"response": cells[0], "interpretation": cells[1]})
    if len(rows) != 5:
        raise ValueError("expected 5 anchor rows (0, 1, 2, NA, Uncertain) in %s, found %d" % (path, len(rows)))
    return rows


def _artifact(aid, rel, expected, media, role):
    full = os.path.join(common.ROOT, rel)
    got = sha256_file(full) if os.path.isfile(full) else None
    return {"artifact_id": aid, "path_or_uri": rel, "sha256": got or expected, "media_type": media,
            "role": role, "transformation_manifest_ref": None, "length_utf16_code_units": None,
            "_present": got is not None, "_matches_expected": (got == expected) if expected else None,
            "_expected_sha256": expected}


def pilot_task():
    tpl = json.loads(_read(TEMPLATE_PATH).decode("utf-8"))
    doc, ins = tpl["document"], tpl["instrument"]
    rows = {r["id"]: r for r in common.load_dataset()} if os.path.exists(
        os.path.join(common.DATA, "dmp_dataset.json")) else {}
    row = rows.get(doc["record_id"], {})
    src = _artifact("src-%s" % doc["record_id"], doc["local_pdf"], doc["sha256"], "application/pdf",
                    "source_document")
    fw = _artifact("framework-v1.0", "data/paired-dmp-corpus/framework/DMP_Evaluation_V1.0.pdf",
                   ins["framework_sha256"], "application/pdf", "rubric")
    an = _artifact("anchors-pilot-01", "research/paired-dmp-study/pilot-start.md", None, "text/markdown", "anchors")
    proto_sha = sha256_file(PROTOCOL) if os.path.exists(PROTOCOL) else None
    artifacts = [src, fw, an]
    clean = [{k: a[k] for k in a if not k.startswith("_")} for a in artifacts]
    rubric_cell = "framework physical PDF p%d (printed p%s), Table 2, row %s, End-Project column" % (
        ins["framework_physical_page"], ins["framework_printed_page"], ins["criterion_id"])
    return {
        "task_id": "PILOT-01",
        "title": "PILOT-01 · criterion %s · %s %s" % (ins["criterion_id"], doc["project"], doc["version"]),
        "status": "deferred",
        "status_text": "Deferred by the user on 2026-11-04. No reading or response is needed now. The form "
                       "stays blank until a person chooses to use it; deferral is not a score, NA or "
                       "uncertain assessment.",
        "reviewer_role": tpl["reviewer_role"],
        "reviewer_name": tpl["reviewer_name"],
        "formal_reviewers": "not assigned",
        "criterion_id": ins["criterion_id"],
        "criterion_label": "Data types, formats and volumes",
        "criterion_note": "Its general heading concerns data kinds, formats and volumes, but the End-Project cell "
                          "addresses the final technical/metadata documentation archive and the technical fidelity "
                          "of final data for reuse. Use the exact checklist in that cell.",
        "phase": ins["intended_rubric_phase"],
        "phase_text": "End-project rubric phase: a working pilot choice because this version is a documented "
                      "post-project update. It is not the benchmark phase policy.",
        "rubric_cell": rubric_cell,
        "framework_page": ins["framework_physical_page"],
        "document": {
            "record_id": doc["record_id"], "project": doc["project"], "grant": row.get("grant") or "101058728",
            "version": doc["version"], "title": row.get("title") or "PathOS - D3.5 Data Management Plan (update)",
            "source_url": doc["source_url"], "pages": 102, "issue_date": "2025-11-10",
            "publication_date": row.get("date") or "2025-11-10",
            "project_start": row.get("proj_start") or "2022-09-01", "project_end": row.get("proj_end") or "2025-08-31",
        },
        "framework": {"doi": ins["framework_doi"], "url": "https://doi.org/" + ins["framework_doi"]},
        "artifacts_status": [{"artifact_id": a["artifact_id"], "present": a["_present"],
                              "matches_expected": a["_matches_expected"]} for a in artifacts],
        "scale": {"id": "ordinal_012_calibration_v1", "version": "v1", "approval": "approved_for_calibration",
                  "labels": {"0": "not evidenced", "1": "partial", "2": "sufficient"}},
        "anchors": parse_anchor_table(),
        "anchors_status": "draft calibration aids, open to criticism; not supplied by the framework",
        "record_template": {
            "schema_version": "0.2.0-draft",
            "study_id": "paired-dmp-study",
            "campaign_id": "calibration-pilot-PILOT-01",
            "cohort_manifest_ref": None,
            "protocol_id": "human-review-protocol-draft",
            "protocol_version": "2026-11-04 draft" + (" (sha256 %s)" % proto_sha[:16] if proto_sha else ""),
            "protocol_approval": "draft",
            "record_kind": "pilot_calibration",
            "document": {
                "document_id": "zenodo:%s" % doc["record_id"], "pair_id": None, "project_id": row.get("grant") or "101058728",
                "source_document_artifact_ids": [src["artifact_id"]],
                "sampling_bin": "calibration_outside_final_cohort",
                "issue_date_raw": "2025-11-10", "publication_date_raw": row.get("date") or "2025-11-10",
                "latest_project_end_date_raw": row.get("proj_end") or "2025-08-31",
                "eligibility_manifest_artifact_id": None, "date_anomaly_refs": [], "discipline_assignment_ref": None,
            },
            "instrument": {
                "instrument_id": "dmp-evaluation-framework", "version": "1.0", "kind": "framework16",
                "rubric_artifact_id": fw["artifact_id"], "rubric_sha256": fw["sha256"],
                "criterion_ids": list(FRAMEWORK16), "intended_human_rubric_phase": ins["intended_rubric_phase"],
                "phase_mapping_version": "pilot-working-choice-2026-11-04",
                "phase_mapping_rationale": "Working pilot choice: the selected version is a documented post-project "
                                           "update. Not the benchmark phase policy.",
                "score_policy_id": "ordinal_012_calibration_v1", "score_policy_version": "v1",
                "score_policy_approval": "approved_for_calibration",
                "na_policy_version": "human-review-protocol-draft 2026-11-04",
                "crosswalk_version": "human-review-protocol-draft 2026-11-04",
                "anchors_status": "calibration_draft", "phase_mapping_status": "calibration_draft",
            },
            "assessment_context": {
                "condition_id": "pilot-full-source", "human_view": "full_source_packet",
                "packet_artifact_id": src["artifact_id"],
                # No extraction was made for the calibration PDF: the full source PDF is the canonical text.
                "canonical_full_text_artifact_id": src["artifact_id"],
                "tool_visible_text_artifact_id": None, "submitted_prompt_artifact_id": None,
                "packet_complete": True, "omitted_or_unreadable_regions": [],
                "model_truncation_state": "not_applicable", "model_input_transformations_ref": None,
                "masking_protocol_version": "none (single-reviewer pilot)", "masked_fields": [],
                "known_unmasked_fields": ["project name", "grant", "dates", "revision history"],
                "presentation_order": 1, "matched_input_prior_full_exposure": "not_applicable",
                "carryover_design_ref": None,
            },
            "comparison_context": {
                "tool_name": "DMP-EVA", "working_software_commit": "b80b43de820d46440d982eb99b2b3da8f4c2f818",
                "native_rubric_sha256": None, "tool_run_manifest_ref": None, "intended_tool_ui_phase": None,
                "observed_effective_criteria_phase": None, "observed_effective_prompt_phase": None,
                "native_instrument_omitted_ids": ["3c", "5d"],
                "comparison_notes": "No tool run is linked to this pilot record; model outputs were not shown.",
            },
            "artifacts": clean,
            "criterion": {
                "criterion_id": ins["criterion_id"], "assessment_phase": ins["intended_rubric_phase"],
                "rubric_cell_locator": rubric_cell, "native_crosswalk_status": "shared_id_semantics_to_check",
                "score_scale_id": "ordinal_012_calibration_v1", "score_scale_version": "v1",
                "anchors_artifact_id": an["artifact_id"],
                "entry_context": "dashboard Review (pilot) mode, PILOT-01 form",
            },
            "assessment_scope": {"scope": "single_criterion_pilot", "assessed_criterion_ids": [ins["criterion_id"]]},
        },
        "no_suggestions": "No AI-generated rating, evidence quotation or expected answer is supplied.",
    }


def boot():
    return {"tasks": [pilot_task()], "schema": load_schema(),
            "state_schema": STATE_SCHEMA, "submission_schema": SUBMISSION_SCHEMA, "version": VERSION}


def servable_artifact(artifact_id):
    """Repo-relative path of a task artifact that may be served, or None."""
    for task in boot()["tasks"]:
        for a in task["record_template"]["artifacts"]:
            if a["artifact_id"] == artifact_id:
                rel = a["path_or_uri"]
                full = os.path.abspath(os.path.join(common.ROOT, rel))
                base = os.path.abspath(os.path.join(common.ROOT, SERVABLE_ROOT))
                if os.path.commonpath([full, base]) == base and os.path.isfile(full):
                    return full
    return None


# ------------------------------------------------------------------ storage
def paths(state_dir):
    d = os.path.join(state_dir, REVIEW_DIR)
    return {"dir": d, "state": os.path.join(d, STATE_FILE), "records": os.path.join(d, RECORDS_DIR)}


def check_state(obj):
    if not isinstance(obj, dict):
        return "not a JSON object"
    if obj.get("schema") != STATE_SCHEMA:
        return "not a review-state file (schema is %r)" % obj.get("schema")
    if obj.get("schema_version") != VERSION:
        return "unsupported schema_version %r (this code reads %d)" % (obj.get("schema_version"), VERSION)
    if not isinstance(obj.get("drafts"), dict):
        return "drafts must be an object"
    return None


def read_state(state_dir):
    """(state, error). A corrupt or unsupported file gives an error and is left untouched."""
    p = paths(state_dir)["state"]
    if not os.path.exists(p):
        return None, None
    try:
        obj = json.loads(_read(p).decode("utf-8"))
    except Exception as e:
        return None, "the review draft file is not valid JSON (%s); its bytes are untouched" % e
    why = check_state(obj)
    return (None, why + "; the file is untouched") if why else (obj, None)


def write_state(state_dir, state, replace_corrupt=False):
    why = check_state(state)
    if why:
        return 400, {"error": "refused: " + why}
    p = paths(state_dir)
    os.makedirs(p["dir"], exist_ok=True)
    _, err = read_state(state_dir)
    kept = None
    if err:
        if not replace_corrupt:
            return 409, {"error": err, "corrupt": True}
        kept = p["state"].replace(".json", ".corrupt-%s.json" % datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
        os.replace(p["state"], kept)
    state["updated"] = now_iso()
    tmp = p["state"] + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(canonical(state))
    os.replace(tmp, p["state"])
    return 200, {"ok": True, "file": p["state"], "kept_corrupt_file": kept}


def list_records(state_dir):
    """(submissions, unreadable). Unreadable or unsupported files are reported, never removed."""
    d = paths(state_dir)["records"]
    subs, bad = [], []
    if not os.path.isdir(d):
        return subs, bad
    for name in sorted(os.listdir(d)):
        if not name.endswith(".json"):
            continue
        try:
            obj = json.loads(_read(os.path.join(d, name)).decode("utf-8"))
        except Exception as e:
            bad.append({"file": name, "error": "not valid JSON (%s)" % e})
            continue
        if obj.get("schema") != SUBMISSION_SCHEMA or obj.get("schema_version") != VERSION \
                or not isinstance(obj.get("record"), dict):
            bad.append({"file": name, "error": "unsupported submission format (schema %r, version %r)" % (
                obj.get("schema"), obj.get("schema_version"))})
            continue
        subs.append(obj)
    subs.sort(key=lambda s: (s["record"].get("submitted_at") or "", s["record"].get("record_id") or ""))
    return subs, bad


def submit(state_dir, submission):
    """Validate and store a locked submission. Returns (code, result)."""
    if not isinstance(submission, dict) or not isinstance(submission.get("record"), dict):
        return 400, {"error": "expected {\"record\": {...}, \"raw_response\": {...}}"}
    rec = submission["record"]
    if rec.get("record_status") != "submitted_locked":
        return 400, {"error": "only a submitted_locked record can be stored; drafts live in the draft file"}
    subs, _ = list_records(state_dir)
    existing = {s["record"]["record_id"] for s in subs}
    rid = rec.get("record_id") or ""
    if not re.match(r"^[A-Za-z0-9._-]{1,120}$", rid):
        return 400, {"error": "record_id must be 1-120 characters of letters, digits, . _ -"}
    if rid in existing:
        return 409, {"error": "record %s is already stored and locked; a correction needs a new record" % rid}
    problems = validate_record(rec, existing)
    if problems:
        return 422, {"error": "record does not satisfy the contract", "problems": problems}
    p = paths(state_dir)
    os.makedirs(p["records"], exist_ok=True)
    stored = {"schema": SUBMISSION_SCHEMA, "schema_version": VERSION, "stored_at": now_iso(),
              "record": rec, "raw_response": submission.get("raw_response") or {}}
    target = os.path.join(p["records"], rid + ".json")
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return 409, {"error": "record %s is already stored and locked" % rid}
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(canonical(stored))
    return 200, {"ok": True, "record_id": rid, "file": target}


# ------------------------------------------------------------------ cli
def main():
    ap = argparse.ArgumentParser(description="Human-review pilot support.")
    ap.add_argument("cmd", choices=["task", "validate", "list"])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--state-dir", default=common.DATA)
    a = ap.parse_args()
    if a.cmd == "task":
        sys.stdout.write(canonical(pilot_task()))
    elif a.cmd == "validate":
        obj = json.load(open(a.file, encoding="utf-8"))
        rec = obj.get("record", obj)
        problems = validate_record(rec, {s["record"]["record_id"] for s in list_records(a.state_dir)[0]})
        print("\n".join(problems) if problems else "valid")
        sys.exit(1 if problems else 0)
    else:
        subs, bad = list_records(a.state_dir)
        for s in subs:
            r = s["record"]
            c = (r.get("criteria") or [{}])[0]
            print("%s  %s  %s  score=%s  supersedes=%s" % (
                r["record_id"], r.get("submitted_at"), c.get("criterion_id"),
                (c.get("score") or {}).get("original_value_as_entered"), r["provenance"].get("supersedes_record_id")))
        for b in bad:
            print("UNREADABLE %s: %s" % (b["file"], b["error"]))
        if not subs and not bad:
            print("no submitted review records")


if __name__ == "__main__":
    main()
