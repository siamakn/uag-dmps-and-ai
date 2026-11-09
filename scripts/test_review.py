"""Tests for the human-review pilot support (scripts/review.py and its server endpoints).

    python scripts/test_review.py                    # run the tests
    python scripts/test_review.py --write-fixtures   # regenerate dashboard/review-fixtures.json

All writes go to temporary directories. The synthetic records below are TEST FIXTURES with
made-up values, clearly labelled as such; they are never human responses and are never
written to real storage. data/selection.json must be byte-identical after the run.
"""
import copy
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import paired  # noqa: E402
import review  # noqa: E402

FIXTURE_PATH = os.path.join(common.DASHBOARD, "review-fixtures.json")
LEGACY = os.path.join(common.DATA, "selection.json")
LEGACY_BEFORE = paired.sha256_or_none(LEGACY)
SYNTH = "SYNTHETIC TEST FIXTURE - not a human response"


def synthetic_record():
    """A complete, valid pilot record with invented values, for validator tests only."""
    t = review.pilot_task()["record_template"]
    c = t["criterion"]
    src = t["document"]["source_document_artifact_ids"][0]
    rec = {k: copy.deepcopy(t[k]) for k in ("schema_version", "study_id", "campaign_id", "cohort_manifest_ref",
                                            "protocol_id", "protocol_version", "protocol_approval", "record_kind",
                                            "document", "instrument", "comparison_context", "artifacts",
                                            "assessment_scope")}
    rec["study_id"] = "synthetic-test"
    rec.update({
        "record_id": "SYNTHETIC-TEST-0001", "record_status": "submitted_locked",
        "created_at": "2026-01-01T10:00:00+00:00", "submitted_at": "2026-01-01T10:30:00+00:00",
        "assessor": {"reviewer_id": "R-PILOT-01", "role": "human_reviewer",
                     "expertise_and_conflicts_private_ref": None, "prior_familiarity": "none_reported",
                     "prior_familiarity_note": ""},
        "assessment_context": dict(copy.deepcopy(t["assessment_context"]),
                                   other_version_shown_before_submission=False,
                                   other_reviewer_labels_seen_before_submission=False,
                                   model_outputs_seen_before_submission=False, independence_deviations=[]),
        "criteria": [{
            "criterion_id": c["criterion_id"], "assessment_phase": c["assessment_phase"],
            "rubric_cell_locator": c["rubric_cell_locator"], "native_crosswalk_status": c["native_crosswalk_status"],
            "applicability": "applicable", "applicability_reason": SYNTH,
            "evidence_state": "partly_evidenced",
            "score": {"value": 1, "scale_id": c["score_scale_id"], "scale_version": c["score_scale_version"],
                      "anchors_artifact_id": c["anchors_artifact_id"], "original_value_as_entered": "1",
                      "entry_context": c["entry_context"], "entry_status": "human_entered"},
            "confidence": "low", "confidence_reason": SYNTH,
            "evidence": [{"artifact_id": src, "physical_page_1based": 1, "printed_page_label": None,
                          "section_or_table": "synthetic section", "json_pointer": None, "text_start": None,
                          "text_end_exclusive": None, "offset_units": None, "excerpt": None, "note": SYNTH}],
            "absence_search_scope": "", "rationale": SYNTH, "uncertainties": [],
            "relevant_packet_search_completed": False,
        }],
        "provenance": {"supersedes_record_id": None, "original_independent_record_ids": [],
                       "adjudication_reason": None, "unresolved_criterion_ids": [], "adjudication_meeting_at": None,
                       "reviewer_confirmation_ref": "synthetic test confirmation", "record_content_sha256": None},
        "overall_comments": SYNTH,
    })
    rec["provenance"]["record_content_sha256"] = review.content_hash(rec)
    return rec


S = ["criteria", 0, "score"]
C = ["criteria", 0]
CASES = [
    ("base record (score 1, partly evidenced, one evidence entry)", [], True),
    ("explicit zero with a completed search and its scope", [
        (S + ["value"], 0), (S + ["original_value_as_entered"], "0"), (C + ["evidence_state"], "not_reported"),
        (C + ["evidence"], []), (C + ["relevant_packet_search_completed"], True),
        (C + ["absence_search_scope"], "synthetic: sections 1-4 and annex A")], True),
    ("zero without a completed search", [
        (S + ["value"], 0), (S + ["original_value_as_entered"], "0"), (C + ["evidence_state"], "not_reported"),
        (C + ["evidence"], []), (C + ["absence_search_scope"], "synthetic scope")], False),
    ("zero without a search scope", [
        (S + ["value"], 0), (S + ["original_value_as_entered"], "0"), (C + ["evidence_state"], "not_reported"),
        (C + ["evidence"], []), (C + ["relevant_packet_search_completed"], True)], False),
    ("two with evidence only partly shown", [(S + ["value"], 2), (S + ["original_value_as_entered"], "2")], False),
    ("two with no evidence entry", [
        (S + ["value"], 2), (S + ["original_value_as_entered"], "2"), (C + ["evidence_state"], "evidenced"),
        (C + ["evidence"], [])], False),
    ("two, evidenced, with evidence", [
        (S + ["value"], 2), (S + ["original_value_as_entered"], "2"), (C + ["evidence_state"], "evidenced")], True),
    ("NA keeps a null score", [
        (C + ["applicability"], "not_applicable"), (S + ["value"], None), (S + ["original_value_as_entered"], "NA"),
        (C + ["evidence_state"], "not_reported"), (C + ["evidence"], [])], True),
    ("NA with a numeric score", [(C + ["applicability"], "not_applicable")], False),
    ("uncertain applicability with a numeric score", [(C + ["applicability"], "uncertain")], False),
    ("uncertain evidence keeps a null score", [
        (C + ["evidence_state"], "uncertain"), (S + ["value"], None),
        (S + ["original_value_as_entered"], "uncertain")], True),
    ("uncertain evidence with a numeric score", [(C + ["evidence_state"], "uncertain")], False),
    ("withheld score", [
        (S + ["value"], None), (S + ["entry_status"], "withheld"), (S + ["original_value_as_entered"], "withheld")], True),
    ("withheld with a numeric score", [(S + ["entry_status"], "withheld")], False),
    ("number marked as not entered", [(S + ["entry_status"], "not_entered")], False),
    ("number without the value as entered", [(S + ["original_value_as_entered"], None)], False),
    ("score 3 is outside the scale", [(S + ["value"], 3), (S + ["original_value_as_entered"], "3")], False),
    ("boolean true is not the score 1", [(S + ["value"], True)], False),
    ("the string '1' is not the score 1", [(S + ["value"], "1")], False),
    ("locked record with no score entered", [
        (S + ["value"], None), (S + ["entry_status"], "not_entered"), (S + ["original_value_as_entered"], None)], False),
    ("draft record with no score entered", [
        (S + ["value"], None), (S + ["entry_status"], "not_entered"), (S + ["original_value_as_entered"], None),
        (["record_status"], "draft"), (["submitted_at"], None), (["provenance", "record_content_sha256"], None)], True),
    ("pilot reviewer must be R-PILOT-01", [(["assessor", "reviewer_id"], "R1")], False),
    ("pilot cannot claim the full instrument", [(["assessment_scope", "scope"], "full_instrument")], False),
    ("locked record needs a confirmation reference", [(["provenance", "reviewer_confirmation_ref"], None)], False),
    ("locked record needs a submission time", [(["submitted_at"], None)], False),
    ("unknown field is refused", [(["surprise"], 1)], False),
    ("empty rationale is refused", [(C + ["rationale"], "")], False),
    ("scope must list exactly the criterion rows", [(["assessment_scope", "assessed_criterion_ids"], ["1a"])], False),
    ("evidence must point at a listed artifact", [(C + ["evidence", 0, "artifact_id"], "nowhere")], False),
    ("tampered content no longer matches its hash", [(C + ["rationale"], "changed after locking")], False, False),
    ("non-ASCII text hashes the same in both languages", [(C + ["rationale"], "Grüße – “quoted” ✓ 数据")], True),
]


def apply_case(rec, sets, rehash=True):
    r = copy.deepcopy(rec)
    for path, value in sets:
        o = r
        for k in path[:-1]:
            o = o[k]
        o[path[-1]] = value
    if rehash and r.get("provenance", {}).get("record_content_sha256"):
        r["provenance"]["record_content_sha256"] = review.content_hash(r)
    return r


def build_fixtures():
    cases = []
    for case in CASES:
        name, sets, valid = case[:3]
        rehash = case[3] if len(case) > 3 else True
        cases.append({"name": name, "set": [[p, v] for p, v in sets], "valid": valid, "rehash": rehash})
    return {"note": "Shared review-validation fixtures. Generated by scripts/test_review.py --write-fixtures. "
                    "The base record is a SYNTHETIC TEST FIXTURE with invented values, never a human response. "
                    "Python (review.schema_validate + pilot_checks) and the dashboard's JavaScript copy must "
                    "agree on every case.",
            "sha256_vectors": [["", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"],
                               ["abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"],
                               ["Grüße ✓", __import__("hashlib").sha256("Grüße ✓".encode()).hexdigest()]],
            "base_record": synthetic_record(), "cases": cases}


FIX = json.load(open(FIXTURE_PATH, encoding="utf-8")) if os.path.exists(FIXTURE_PATH) else None


class Fixtures(unittest.TestCase):
    def test_fixtures_are_current(self):
        self.assertIsNotNone(FIX, "run with --write-fixtures first")
        self.assertEqual(FIX["base_record"], synthetic_record(), "fixtures are stale; regenerate them")

    def test_cases(self):
        schema = review.load_schema()
        for case in FIX["cases"]:
            with self.subTest(case["name"]):
                r = apply_case(FIX["base_record"], case["set"], case["rehash"])
                problems = review.validate_record(r, schema=schema)
                self.assertEqual(not problems, case["valid"], problems)


class Task(unittest.TestCase):
    def test_pilot_task_is_blank_and_deferred(self):
        t = review.pilot_task()
        self.assertEqual(t["status"], "deferred")
        self.assertEqual([a["response"] for a in t["anchors"]], ["0", "1", "2", "NA", "Uncertain"])
        self.assertTrue(all(s["present"] for s in t["artifacts_status"]))
        self.assertTrue(all(s["matches_expected"] in (True, None) for s in t["artifacts_status"]))
        blob = json.dumps(t)
        for word in ('"value"', "human_entered", "expected_answer\": \""):
            self.assertNotIn(word, blob)

    def test_template_is_still_blank(self):
        tpl = json.load(open(review.TEMPLATE_PATH, encoding="utf-8"))
        self.assertIsNone(tpl["fields_to_be_supplied_by_human"]["numeric_score"])
        self.assertFalse(tpl["human_response_received"])

    def test_schema_validator_basics(self):
        s = {"type": "object", "required": ["a"], "additionalProperties": False,
             "properties": {"a": {"type": "integer", "minimum": 0}, "b": {"enum": [0, 1]}}}
        self.assertEqual(review.schema_validate(s, {"a": 1}), [])
        self.assertTrue(review.schema_validate(s, {"a": True}))
        self.assertTrue(review.schema_validate(s, {"a": 1, "b": False}))
        self.assertTrue(review.schema_validate(s, {}))
        self.assertTrue(review.schema_validate(s, {"a": -1}))


class Storage(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="review-store-")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_locked_records_are_never_overwritten(self):
        rec = FIX["base_record"]
        code, res = review.submit(self.d, {"record": rec, "raw_response": {"text": SYNTH}})
        self.assertEqual(code, 200, res)
        before = open(res["file"], "rb").read()
        changed = apply_case(rec, [(["criteria", 0, "rationale"], "second attempt")])
        code2, res2 = review.submit(self.d, {"record": changed})
        self.assertEqual(code2, 409)
        self.assertEqual(open(res["file"], "rb").read(), before)

    def test_correction_links_and_keeps_original(self):
        rec = FIX["base_record"]
        review.submit(self.d, {"record": rec})
        orig = open(os.path.join(review.paths(self.d)["records"], rec["record_id"] + ".json"), "rb").read()
        fix = apply_case(rec, [(["record_id"], "SYNTHETIC-TEST-0002"),
                               (["provenance", "supersedes_record_id"], rec["record_id"])])
        self.assertEqual(review.submit(self.d, {"record": fix})[0], 200)
        dangling = apply_case(rec, [(["record_id"], "SYNTHETIC-TEST-0003"),
                                    (["provenance", "supersedes_record_id"], "missing")])
        self.assertEqual(review.submit(self.d, {"record": dangling})[0], 422)
        self.assertEqual(open(os.path.join(review.paths(self.d)["records"], rec["record_id"] + ".json"), "rb").read(),
                         orig)
        subs, bad = review.list_records(self.d)
        self.assertEqual([s["record"]["record_id"] for s in subs], ["SYNTHETIC-TEST-0001", "SYNTHETIC-TEST-0002"])

    def test_drafts_are_not_stored_as_records(self):
        draft = apply_case(FIX["base_record"], [(["record_status"], "draft")])
        self.assertEqual(review.submit(self.d, {"record": draft})[0], 400)

    def test_unreadable_files_are_reported_not_removed(self):
        p = review.paths(self.d)
        os.makedirs(p["records"])
        with open(os.path.join(p["records"], "broken.json"), "w") as f:
            f.write("{nope")
        with open(os.path.join(p["records"], "future.json"), "w") as f:
            json.dump({"schema": review.SUBMISSION_SCHEMA, "schema_version": 99, "record": {}}, f)
        subs, bad = review.list_records(self.d)
        self.assertEqual(subs, [])
        self.assertEqual(sorted(b["file"] for b in bad), ["broken.json", "future.json"])
        self.assertTrue(os.path.exists(os.path.join(p["records"], "broken.json")))

    def test_corrupt_state_is_kept(self):
        p = review.paths(self.d)
        os.makedirs(p["dir"])
        with open(p["state"], "w") as f:
            f.write("{corrupt")
        state, err = review.read_state(self.d)
        self.assertIsNone(state)
        self.assertIn("untouched", err)
        good = {"schema": review.STATE_SCHEMA, "schema_version": 1, "drafts": {}}
        self.assertEqual(review.write_state(self.d, dict(good))[0], 409)
        self.assertEqual(open(p["state"]).read(), "{corrupt")
        code, res = review.write_state(self.d, dict(good), replace_corrupt=True)
        self.assertEqual(code, 200)
        self.assertEqual(open(res["kept_corrupt_file"]).read(), "{corrupt")
        bad = dict(good, schema_version=2)
        self.assertEqual(review.write_state(self.d, bad)[0], 400)


class Server(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import serve
        cls.serve = serve
        cls.state = tempfile.mkdtemp(prefix="review-serve-")
        serve.set_state_dir(cls.state)
        serve.load_state("/api")
        cls.httpd, cls.port = serve.bind(18890, serve.Handler)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:%d" % cls.port

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.serve.set_state_dir(common.DATA)
        shutil.rmtree(cls.state)

    def call(self, method, path, body=None, raw=False):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                code, payload = r.status, r.read()
        except urllib.error.HTTPError as e:
            code, payload = e.code, e.read()
        if raw:
            return code, payload
        try:
            return code, json.loads(payload.decode() or "null")
        except ValueError:
            return code, payload.decode()

    def test_review_round_trip(self):
        code, d = self.call("GET", "/api/review")
        self.assertEqual((code, d["state"], d["records"]), (200, None, []))
        st = {"schema": review.STATE_SCHEMA, "schema_version": 1,
              "drafts": {"PILOT-01": {"task_id": "PILOT-01", "fields": {"rationale": ""}}}}
        self.assertEqual(self.call("PUT", "/api/review/state", {"state": st})[0], 200)
        self.assertEqual(self.call("GET", "/api/review")[1]["state"]["drafts"]["PILOT-01"]["fields"]["rationale"], "")
        rec = apply_case(FIX["base_record"], [(["record_id"], "SYNTHETIC-TEST-SRV")])
        code, d = self.call("POST", "/api/review/submit", {"submission": {"record": rec, "raw_response": {}}})
        self.assertEqual(code, 200, d)
        self.assertEqual(self.call("POST", "/api/review/submit", {"submission": {"record": rec}})[0], 409)
        self.assertEqual(len(self.call("GET", "/api/review")[1]["records"]), 1)

    def test_validate_endpoint_matches_module(self):
        for case in FIX["cases"]:
            r = apply_case(FIX["base_record"], case["set"], case["rehash"])
            code, d = self.call("POST", "/api/review/validate", {"record": r})
            self.assertEqual(d["valid"], case["valid"], case["name"])

    def test_corrupt_state_over_http(self):
        p = review.paths(self.state)
        os.makedirs(p["dir"], exist_ok=True)
        with open(p["state"], "w") as f:
            f.write("{corrupt")
        try:
            code, d = self.call("GET", "/api/review")
            self.assertEqual((code, d.get("corrupt")), (409, True))
            st = {"schema": review.STATE_SCHEMA, "schema_version": 1, "drafts": {}}
            self.assertEqual(self.call("PUT", "/api/review/state", {"state": st})[0], 409)
            self.assertEqual(open(p["state"]).read(), "{corrupt")
        finally:
            os.remove(p["state"])

    def test_source_files_are_whitelisted(self):
        code, body = self.call("GET", "/api/review/source/src-17578116", raw=True)
        self.assertEqual(code, 200)
        self.assertTrue(body.startswith(b"%PDF-"))
        self.assertEqual(self.call("GET", "/api/review/source/..%2F..%2Fdata%2Fselection.json")[0], 404)
        self.assertEqual(self.call("GET", "/api/review/source/anchors-pilot-01")[0], 404)


class LegacyUntouched(unittest.TestCase):
    def test_zz_legacy_selection_byte_identical(self):
        self.assertEqual(paired.sha256_or_none(LEGACY), LEGACY_BEFORE)


if __name__ == "__main__":
    if "--write-fixtures" in sys.argv:
        with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(build_fixtures(), ensure_ascii=False, indent=1) + "\n")
        print("wrote %s" % FIXTURE_PATH)
    else:
        unittest.main(verbosity=1)
