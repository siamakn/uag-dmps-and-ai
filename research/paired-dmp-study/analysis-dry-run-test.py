#!/usr/bin/env python3
"""Hand-calculated synthetic checks; no source PDFs, actual labels or network."""
import copy
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("analysis-dry-run.py")
SPEC = importlib.util.spec_from_file_location("synthetic_analysis", str(SCRIPT))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SyntheticAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.data = MODULE.example()
        self.did = self.data["projects"][0]["documents"][0]["document"]
        self.late = self.data["projects"][0]["documents"][1]["document"]
        self.cid = self.data["criteria"][0]

    def row(self, condition, did=None, cid=None):
        rows = self.data["reference"] if condition == "human" else self.data["models"]
        return next(r for r in rows if r["document"] == (did or self.did)
                    and r["criterion"] == (cid or self.cid)
                    and (condition == "human" or r["condition"] == condition))

    def disposition(self, condition, state, did=None, cid=None):
        applicability = {"NA": "NA", "instrument_undefined": "instrument_undefined"}.get(
            state, "applicable" if condition == "human" else "unknown")
        self.row(condition, did, cid).update(state=state, value=None, reason="SYNTHETIC_" + state,
                                            applicability=applicability)

    def doc_result(self, result, did=None):
        return next(r for r in result["documents"] if r["document"] == (did or self.did))

    def test_builtin_and_genuine_zero(self):
        result = MODULE.analyze(self.data)
        # One error in 3 rows, half of first project, one of 6 projects.
        self.assertAlmostEqual(result["primary_conditional_F1_minus_F0"], 1 / 36)
        self.assertEqual(result["common_coverage"], {"numerator": 36, "denominator": 36, "rate": 1.0})
        self.assertEqual(result["reference_states"]["score"], 36)
        self.assertEqual(result["conditions"]["F0"]["numeric_coverage"]["numerator"], 36)

    def test_equal_documents_then_equal_projects_not_pooled(self):
        # First early doc: one comparable row, +1. Late: three rows, -1/3.
        for cid in self.data["criteria"][1:]:
            for condition in ("human", "F0", "F1"):
                self.disposition(condition, "NA", cid=cid)
        self.row("F0", self.late)["value"] = 1
        result = MODULE.analyze(self.data)
        self.assertAlmostEqual(result["projects"][0]["F1_minus_F0"], 1 / 3)
        self.assertAlmostEqual(result["primary_conditional_F1_minus_F0"], 1 / 18)
        self.assertEqual(result["common_coverage"]["denominator"], 34)
        pooled_difference = sum(d["disagreement"]["F1"]["numerator"] -
                                d["disagreement"]["F0"]["numerator"] for d in result["documents"])
        self.assertEqual(pooled_difference, 0)
        self.assertNotEqual(result["primary_conditional_F1_minus_F0"], 0)

    def test_missing_model_row_keeps_fixed_denominator(self):
        self.data["models"].remove(self.row("F1"))
        result = MODULE.analyze(self.data)
        counts = result["conditions"]["F1"]
        self.assertEqual(counts["numeric_coverage"], {"numerator": 35, "denominator": 36, "rate": 35 / 36})
        self.assertEqual(counts["fixed_denominator_states"]["missing"], 1)
        self.assertEqual(counts["fixed_denominator_exclusion_reasons"], {"missing_model_row": 1})
        self.assertEqual(self.doc_result(result)["common_criteria"], self.data["criteria"][1:])
        self.assertEqual(result["primary_conditional_F1_minus_F0"], 0)
        self.assertEqual(len(result["condition_specific_nonnumeric_rows"]), 1)
        audit = result["excluded_from_common_primary"]
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["conditions"]["F0"]["state"], "score")
        self.assertEqual(audit[0]["conditions"]["F1"]["reason"], "missing_model_row")

    def test_whole_missing_doc_makes_required_project_and_overall_undefined(self):
        self.data["models"] = [r for r in self.data["models"]
                               if not (r["document"] == self.did and r["condition"] == "F1")]
        result = MODULE.analyze(self.data)
        self.assertIsNone(result["primary_conditional_F1_minus_F0"])
        self.assertIsNone(result["projects"][0]["F1_minus_F0"])
        self.assertEqual(len(result["projects"]), 6)
        self.assertEqual(len(result["documents"]), 12)
        self.assertEqual(result["conditions"]["F1"]["numeric_coverage"]["denominator"], 36)
        self.assertEqual(result["undefined_reasons"][0]["documents"], [self.did])

    def test_applicability_both_directions_not_missingness(self):
        second = self.data["criteria"][1]
        self.disposition("human", "NA")
        self.disposition("F0", "NA", cid=second)
        self.disposition("F1", "uncertainty", cid=second)
        result = MODULE.analyze(self.data)
        f0, f1 = result["conditions"]["F0"], result["conditions"]["F1"]
        self.assertEqual(f0["human_NA_model_numeric"], 1)
        self.assertEqual(f1["human_NA_model_numeric"], 1)
        self.assertEqual(f0["human_numeric_model_NA"], 1)
        self.assertEqual(f0["applicability_disagreement_on_joint_known_states"]["numerator"], 2)
        self.assertEqual(f1["applicability_disagreement_on_joint_known_states"]["denominator"], 35)
        self.assertEqual(f1["fixed_denominator_states"]["uncertainty"], 1)
        self.assertEqual(f1["human_applicable_defined"], 35)

    def test_undefined_instrument_is_not_NA_or_zero(self):
        self.data["projects"][0]["documents"][0]["defined_criteria"].remove(self.cid)
        for condition in ("human", "F0", "F1"):
            self.disposition(condition, "instrument_undefined")
        result = MODULE.analyze(self.data)
        self.assertEqual(result["reference_states"]["instrument_undefined"], 1)
        self.assertEqual(result["common_coverage"]["denominator"], 35)
        self.assertEqual(result["conditions"]["F1"]["all_states"]["instrument_undefined"], 1)
        self.assertEqual(result["conditions"]["F1"]["fixed_denominator_states"]["instrument_undefined"], 0)
        self.row("F0").update(state="score", value=0, reason="", applicability="applicable")
        with self.assertRaisesRegex(ValueError, "instrument"):
            MODULE.analyze(self.data)

    def test_failure_missing_uncertainty_distinct_never_zero(self):
        for cid, state in zip(self.data["criteria"], ("failure", "missing", "uncertainty")):
            self.disposition("F1", state, cid=cid)
        result = MODULE.analyze(self.data)
        self.assertIsNone(result["primary_conditional_F1_minus_F0"])
        f1 = result["conditions"]["F1"]
        self.assertEqual(f1["numeric_coverage"]["numerator"], 33)
        self.assertEqual(f1["numeric_coverage"]["denominator"], 36)
        for state in ("failure", "missing", "uncertainty"):
            self.assertEqual(f1["fixed_denominator_states"][state], 1)
        self.assertEqual(len(f1["fixed_denominator_exclusion_reasons"]), 3)

    def test_applicable_reference_non_score_stays_in_fixed_denominator(self):
        for state in ("failure", "missing", "uncertainty"):
            with self.subTest(state=state):
                self.disposition("human", state)
                result = MODULE.analyze(self.data)
                self.assertEqual(result["common_coverage"]["denominator"], 36)
                self.assertEqual(result["common_coverage"]["numerator"], 35)
                self.assertEqual(result["reference_states"][state], 1)

    def test_unknown_human_applicability_separate_from_applicable_uncertainty(self):
        self.disposition("human", "uncertainty")
        self.row("human")["applicability"] = "unknown"
        result = MODULE.analyze(self.data)
        self.assertEqual(result["common_coverage"]["denominator"], 35)
        self.assertEqual(result["reference_applicability"]["unknown"], 1)

    def test_all_model_rows_missing_preserves_roster_and_denominator(self):
        self.data["models"] = []
        result = MODULE.analyze(self.data)
        self.assertIsNone(result["primary_conditional_F1_minus_F0"])
        self.assertEqual(len(result["undefined_reasons"]), 6)
        for condition in MODULE.CONDITIONS:
            self.assertEqual(result["conditions"][condition]["numeric_coverage"],
                             {"numerator": 0, "denominator": 36, "rate": 0.0})
            self.assertEqual(result["conditions"][condition]["supplied_rows"], 0)

    def test_negative_contrast_sign(self):
        for row in self.data["models"]:
            row["value"] = 1 if row["condition"] == "F0" else 0
        self.assertEqual(MODULE.analyze(self.data)["primary_conditional_F1_minus_F0"], -1)

    def test_all_human_NA_document_is_undefined(self):
        for cid in self.data["criteria"]:
            self.disposition("human", "NA", cid=cid)
        result = MODULE.analyze(self.data)
        self.assertIsNone(result["primary_conditional_F1_minus_F0"])
        self.assertIsNone(self.doc_result(result)["common_coverage"]["rate"])
        self.assertEqual(self.doc_result(result)["human_applicable_defined"], 0)

    def test_input_order_invariance(self):
        result = MODULE.analyze(self.data)
        rng = random.Random(123)
        for key in ("projects", "criteria", "reference", "models"):
            rng.shuffle(self.data[key])
        for project in self.data["projects"]:
            rng.shuffle(project["documents"])
            for doc in project["documents"]:
                rng.shuffle(doc["defined_criteria"])
        self.assertEqual(MODULE.analyze(self.data), result)

    def test_malformed_values(self):
        for value in (True, False, -1, 3, 100, 0.0, 1.0, "0", None, float("nan"), float("inf")):
            with self.subTest(value=value):
                self.row("F0")["value"] = value
                with self.assertRaisesRegex(ValueError, "ordinal integer"):
                    MODULE.analyze(self.data)

    def test_malformed_contracts(self):
        mutations = [
            lambda d: d["reference"].pop(),
            lambda d: d["reference"].append(copy.deepcopy(d["reference"][0])),
            lambda d: d["models"].append(copy.deepcopy(d["models"][0])),
            lambda d: d["models"][0].update(condition="N0"),
            lambda d: d["models"][0].update(document="SYNTHETIC_UNKNOWN"),
            lambda d: d["models"][0].update(criterion="SYNTHETIC_UNKNOWN"),
            lambda d: d["models"][0].update(state="unknown"),
            lambda d: d["models"][0].update(state="NA", reason="SYNTHETIC_NA"),
            lambda d: d["models"][0].update(state="failure", value=None, reason=""),
            lambda d: d["models"][0].update(unexpected=1),
            lambda d: d.update(repeat_count=True),
            lambda d: d.update(repeat_count=2),
            lambda d: d.update(repeat_count=1.0),
            lambda d: d.update(projects=[]),
            lambda d: d.update(criteria=[]),
            lambda d: d["projects"][0]["documents"].pop(),
            lambda d: d["projects"][0]["documents"][0].update(phase="late"),
            lambda d: d["projects"][0]["documents"][0].update(document=d["projects"][1]["documents"][0]["document"]),
            lambda d: d["projects"][0].update(project=d["projects"][1]["project"]),
            lambda d: d["criteria"].append(d["criteria"][0]),
            lambda d: d["projects"][0]["documents"][0]["defined_criteria"].append("SYNTHETIC_UNKNOWN"),
            lambda d: d["reference"][0].update(document="ACTUAL_PROJECT_NOT_ALLOWED"),
            lambda d: d.update(notice="real_labels"),
        ]
        for number, mutation in enumerate(mutations):
            with self.subTest(mutation=number):
                data = copy.deepcopy(self.data)
                mutation(data)
                with self.assertRaises(ValueError):
                    MODULE.analyze(data)

    def test_cli_json_and_rejections(self):
        with tempfile.TemporaryDirectory(prefix="synthetic-analysis-") as temp:
            source, output = Path(temp) / "input.json", Path(temp) / "output.json"
            source.write_text(json.dumps(self.data), encoding="utf-8")
            run = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--output", str(output)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(output.read_text()), MODULE.analyze(self.data))
            for invalid in ('{"notice":1,"notice":2}', '{"value":NaN}', '{"value":Infinity}', '{', '[]'):
                source.write_text(invalid, encoding="utf-8")
                run = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source)],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.assertNotEqual(run.returncode, 0)
                self.assertNotIn(b"Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
