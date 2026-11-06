"""Tests for the paired-study module and its server endpoints. Stdlib unittest only.

    python scripts/test_paired.py

Every test that writes uses a temporary directory. The legacy data/selection.json is
hashed before and after the run and must come out byte-identical.
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

FIXTURES = json.load(open(os.path.join(common.DASHBOARD, "paired-fixtures.json"), encoding="utf-8"))
LEGACY = os.path.join(common.DATA, "selection.json")


def legacy_hash():
    return paired.sha256_or_none(LEGACY)


LEGACY_BEFORE = legacy_hash()


def syn():
    return copy.deepcopy(FIXTURES["synthetic_cohort"])


def codes(v, pid):
    return [i["code"] for i in v["pairs"][pid]["issues"]]


class Timing(unittest.TestCase):
    def test_shared_fixtures(self):
        for f in FIXTURES["timing"]:
            with self.subTest(f["name"]):
                t = paired.timing(f["issue"], f["start"], f["end"], f.get("pre_start", "exclude"))
                self.assertEqual(t["early"], f["early"])
                self.assertEqual(t["late"], f["late"])
                self.assertEqual(t["state"], f.get("state", "ok"))
                for k in ("n_lo", "n_hi", "d"):
                    if k in f:
                        self.assertEqual(t[k], f[k])
                if "pct_lo" in f:
                    self.assertEqual(paired.pct(t["n_lo"], t["d"]), f["pct_lo"])

    def test_partial_dates_keep_precision(self):
        self.assertEqual(paired.parse_date("2023-02")["precision"], "month")
        self.assertEqual(str(paired.parse_date("2023-02")["hi"]), "2023-02-28")
        self.assertEqual(str(paired.parse_date("2024-02")["hi"]), "2024-02-29")
        self.assertIn("error", paired.parse_date("2023-13"))
        self.assertIn("error", paired.parse_date("23-01-01"))

    def test_integer_rule_not_rounded(self):
        # d = 1095; 2n <= d means n <= 547 (2*547 = 1094); n = 548 is 50.05% and not early,
        # although a two-decimal rounding of 547.5/1095 would read 50.00%.
        t = paired.timing("2021-07-02", "2020-01-01", "2022-12-31")  # n = 548
        self.assertEqual((t["n_lo"], t["d"], t["early"]), (548, 1095, "no"))
        t = paired.timing("2021-07-01", "2020-01-01", "2022-12-31")  # n = 547
        self.assertEqual(t["early"], "yes")


class Validation(unittest.TestCase):
    def test_synthetic_cohort_is_valid(self):
        v = paired.validate(syn())
        self.assertEqual(v["counts"], {"verified_pairs": 6, "distinct_documents": 12})
        self.assertTrue(v["freezable"], v["cohort"])

    def mutate(self, fn):
        s = syn()
        fn(s)
        return paired.validate(s)

    def test_partner_scope(self):
        v = self.mutate(lambda s: s["documents"]["SYN1-late"].update(scope="partner: X"))
        self.assertEqual(v["pairs"]["natural-sciences"]["status"], "rejected")
        self.assertIn("scope_mismatch", codes(v, "natural-sciences"))

    def test_repeated_bytes(self):
        def f(s):
            s["documents"]["SYN2-late"]["files"][0]["sha256"] = s["documents"]["SYN2-early"]["files"][0]["sha256"]
        self.assertIn("repeated_bytes", codes(self.mutate(f), "engineering-and-technology"))

    def test_project_in_two_disciplines(self):
        def f(s):
            s["pairs"][1]["project"]["grant"] = "SYN1"
            for r in ("early", "late"):
                s["documents"]["SYN2-" + r]["grant"] = "SYN1"
        v = self.mutate(f)
        self.assertIn("project_reused", codes(v, "natural-sciences"))
        self.assertIn("project_reused", codes(v, "engineering-and-technology"))

    def test_document_in_two_roles(self):
        def f(s):
            s["pairs"][0]["late"] = s["pairs"][0]["early"]
        v = self.mutate(f)
        self.assertIn("same_document_both_roles", codes(v, "natural-sciences"))
        self.assertIn("document_reused", codes(v, "natural-sciences"))

    def test_two_versions_of_one_project_are_fine(self):
        v = paired.validate(syn())
        for pid in v["pairs"]:
            self.assertNotIn("project_reused", codes(v, pid))

    def test_deposited_after_end_is_not_late(self):
        def f(s):
            s["documents"]["SYN3-late"]["issue_date"]["value"] = "2022-12-01"
            s["documents"]["SYN3-late"]["publication_date"] = "2023-06-01"
        self.assertIn("timing_fail", codes(self.mutate(f), "medical-and-health-sciences"))

    def test_missing_issue_date_does_not_fall_back(self):
        def f(s):
            s["documents"]["SYN5-early"]["issue_date"]["value"] = None
            s["documents"]["SYN5-early"]["publication_date"] = "2020-03-01"
        v = self.mutate(f)
        self.assertIn("issue_date_missing", codes(v, "social-sciences"))
        self.assertEqual(v["pairs"]["social-sciences"]["timing"]["early"]["state"], "unknown")
        self.assertEqual(v["pairs"]["social-sciences"]["status"], "pending")

    def test_unverified_lineage_and_dates(self):
        def f(s):
            s["pairs"][0]["lineage"]["state"] = "not_checked"
            s["documents"]["SYN1-late"]["issue_date"]["state"] = "not_checked"
        v = self.mutate(f)
        self.assertIn("lineage_unverified", codes(v, "natural-sciences"))
        self.assertIn("issue_date_unverified", codes(v, "natural-sciences"))
        self.assertFalse(v["freezable"])

    def test_alternative_date_flipping_verdict(self):
        def f(s):
            s["documents"]["SYN1-late"]["alt_dates"] = [{"value": "2022-12-20", "label": "cover", "locator": "p1"}]
        self.assertIn("alt_date_conflict", codes(self.mutate(f), "natural-sciences"))

    def test_unsupported_discipline(self):
        self.assertIn("discipline_unsupported", codes(
            self.mutate(lambda s: s["pairs"][3]["cordis"].update(branches=["natural sciences"])),
            "agricultural-sciences"))

    def test_pre_start_policy(self):
        v = self.mutate(lambda s: s["documents"]["SYN1-early"]["issue_date"].update(value="2019-12-15"))
        self.assertIn("timing_fail", codes(v, "natural-sciences"))
        self.assertIn("pre_start_unsettled", [i["code"] for i in v["cohort"]])

    def test_incomplete_cohort(self):
        v = self.mutate(lambda s: s["pairs"][5].update(late=None))
        self.assertFalse(v["freezable"])
        self.assertEqual(v["counts"]["verified_pairs"], 5)

    def test_proposal_draft_is_not_verified(self):
        st = paired.proposal_to_study()
        v = paired.validate(st)
        self.assertEqual(v["counts"]["distinct_documents"], 12)
        self.assertEqual(v["counts"]["verified_pairs"], 0)
        prop = json.load(open(paired.PROPOSAL, encoding="utf-8"))
        # every computed day count matches the proposal's own numerator for the chosen date
        for src in prop["pairs"]:
            pair = next(p for p in st["pairs"] if p["discipline"] == src["proposed_slot"])
            for role in ("early", "late"):
                doc = st["documents"][pair[role]]
                want = next(x["numerator_days"] for x in src[role]["document_dates"]
                            if x["date"] == doc["issue_date"]["value"])
                self.assertEqual(v["pairs"][pair["pair_id"]]["timing"][role]["n_lo"], want)
                self.assertEqual(v["pairs"][pair["pair_id"]]["timing"][role][role], "yes")

    def test_registry_invents_no_ids(self):
        reg = paired.load_registry()
        by = {d["doc_id"]: d for d in reg["documents"]}
        self.assertEqual(set(by), {"AGRICORE-D9.2-v1.0", "AGRICORE-D9.3-v1.0", "zenodo:17733866"})
        self.assertIsNone(by["AGRICORE-D9.2-v1.0"]["record_id"])
        self.assertTrue(all(d["files"][0]["sha256"] for d in reg["documents"]))
        ids = {r["id"] for r in common.load_dataset()}
        self.assertFalse(ids & {"17733866"}, "registry documents must be absent from the dataset")


class Exports(unittest.TestCase):
    def test_escaping_matches_fixture(self):
        import csv
        import io
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\n").writerow(FIXTURES["escape"])
        self.assertEqual(buf.getvalue()[:-1], FIXTURES["escape_expected"]["csv_row"])
        self.assertEqual("| " + " | ".join(paired.md_cell(x) for x in FIXTURES["escape"]) + " |",
                         FIXTURES["escape_expected"]["md_row"])

    def test_csv_round_trips_awkward_text(self):
        import csv
        import io
        s = syn()
        s["pairs"][0]["project"]["acronym"] = 'A,"B"|C\nD'
        rows = paired.export_rows(s)
        back = list(csv.reader(io.StringIO(paired.to_csv(rows))))
        self.assertEqual(back[1][3], 'A,"B"|C\nD')
        md = paired.to_md(rows).splitlines()
        self.assertEqual(len(md), 8)
        self.assertIn("A,\"B\"\\|C D", md[2])

    def test_json_round_trip(self):
        s = syn()
        back = json.loads(paired.canonical(s))
        self.assertEqual(back, s)
        self.assertEqual(paired.validate(back)["pairs"]["natural-sciences"]["timing"]["early"]["n_lo"], 152)


class Freeze(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="paired-root-")
        self.state = tempfile.mkdtemp(prefix="paired-state-")
        for did, doc in syn()["documents"].items():
            path = os.path.join(self.root, doc["files"][0]["local_path"])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            g, role = did.split("-")
            with open(path, "wb") as f:
                f.write(("synthetic %s %s" % (g, role)).encode())

    def tearDown(self):
        shutil.rmtree(self.root)
        shutil.rmtree(self.state)

    def test_freeze_writes_immutable_snapshot(self):
        ok, res = paired.freeze(syn(), self.state, self.root)
        self.assertTrue(ok, res.get("reasons"))
        body = json.load(open(res["path"], encoding="utf-8"))
        self.assertEqual(body["study"]["status"], "frozen")
        self.assertEqual(len(body["file_manifest"]), 12)
        self.assertTrue(all(e["local_sha256"] == e["recorded_sha256"] for e in body["file_manifest"]))
        self.assertTrue(paired.verify_snapshot(res["path"]))
        for ext in ("csv", "md"):
            self.assertTrue(os.path.exists(res["path"][:-5] + "." + ext))
        before = open(res["path"], "rb").read()
        # editing the draft and freezing again makes a new snapshot, never a rewrite
        s2 = syn()
        s2["pairs"][0]["notes"] = "edited after the first freeze"
        ok2, res2 = paired.freeze(s2, self.state, self.root)
        self.assertTrue(ok2)
        self.assertNotEqual(res2["path"], res["path"])
        self.assertEqual(open(res["path"], "rb").read(), before)
        # a tampered snapshot no longer verifies
        tampered = json.load(open(res["path"], encoding="utf-8"))
        tampered["study"]["pairs"][0]["scope"] = "changed"
        path3 = os.path.join(self.state, "tampered.json")
        with open(path3, "w", encoding="utf-8") as f:
            f.write(paired.canonical(tampered))
        self.assertFalse(paired.verify_snapshot(path3))

    def test_freeze_refuses_changed_bytes(self):
        with open(os.path.join(self.root, "synthetic", "SYN1-early.pdf"), "ab") as f:
            f.write(b"!")
        ok, res = paired.freeze(syn(), self.state, self.root)
        self.assertFalse(ok)
        self.assertTrue(any("differ from the recorded checksum" in r for r in res["reasons"]))
        self.assertFalse(os.path.isdir(os.path.join(self.state, paired.SNAPSHOT_DIR)) and
                         os.listdir(os.path.join(self.state, paired.SNAPSHOT_DIR)))

    def test_freeze_refuses_incomplete_draft(self):
        s = syn()
        s["protocol"]["approved"] = False
        s["pairs"][2]["early"] = None
        ok, res = paired.freeze(s, self.state, self.root)
        self.assertFalse(ok)
        self.assertTrue(any("protocol not approved" in r for r in res["reasons"]))
        self.assertTrue(any(r.startswith("medical-and-health-sciences") for r in res["reasons"]))

    def test_paths_cannot_escape_root(self):
        self.assertIsNone(paired.resolve_local("../outside.pdf", self.root))


class Legacy(unittest.TestCase):
    def test_legacy_import_keeps_every_id(self):
        tmp = tempfile.mkdtemp()
        try:
            p = os.path.join(tmp, "selection.json")
            with open(p, "w") as f:
                json.dump({"ids": ["18849166", "not-in-dataset"]}, f)
            h = paired.legacy_historical(p, {"18849166"})
            self.assertEqual(h["ids"], ["18849166", "not-in-dataset"])
            self.assertEqual(h["unresolved"], ["not-in-dataset"])
            self.assertIn("confers no eligibility", h["label"])
        finally:
            shutil.rmtree(tmp)


class Server(unittest.TestCase):
    """The served API, against a temporary state dir only."""

    @classmethod
    def setUpClass(cls):
        import serve
        cls.serve = serve
        cls.state = tempfile.mkdtemp(prefix="paired-serve-")
        serve.set_state_dir(cls.state)
        serve.load_state("/api")
        cls.httpd, cls.port = serve.bind(18790, serve.Handler)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:%d" % cls.port

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.serve.set_state_dir(common.DATA)
        shutil.rmtree(cls.state)

    def call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                code, raw = r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            code, raw = e.code, e.read().decode()
        try:
            return code, json.loads(raw or "null")
        except ValueError:
            return code, raw

    def test_round_trip_and_corruption(self):
        path = os.path.join(self.state, paired.STUDY_FILE)
        if os.path.exists(path):
            os.remove(path)
        code, d = self.call("GET", "/api/paired")
        self.assertEqual((code, d["study"]), (200, None))
        code, d = self.call("PUT", "/api/paired", {"study": syn()})
        self.assertEqual(code, 200)
        code, d = self.call("GET", "/api/paired")
        self.assertEqual(d["study"]["study_id"], "synthetic-cohort")
        self.assertTrue(d["study"]["sources"]["data/dmp_dataset.json"])
        # unsupported study: refused, previous file kept
        bad = syn()
        bad["schema_version"] = 99
        code, d = self.call("PUT", "/api/paired", {"study": bad})
        self.assertEqual(code, 400)
        self.assertEqual(self.call("GET", "/api/paired")[1]["study"]["study_id"], "synthetic-cohort")
        # corrupt file on disk: GET reports it, PUT refuses, bytes untouched
        with open(path, "wb") as f:
            f.write(b"{corrupt")
        code, d = self.call("GET", "/api/paired")
        self.assertEqual((code, d.get("corrupt")), (409, True))
        code, d = self.call("PUT", "/api/paired", {"study": syn()})
        self.assertEqual(code, 409)
        self.assertEqual(open(path, "rb").read(), b"{corrupt")
        # explicit replacement keeps the unreadable bytes beside it
        code, d = self.call("PUT", "/api/paired", {"study": syn(), "replace_corrupt": True})
        self.assertEqual(code, 200)
        self.assertEqual(open(d["kept_corrupt_file"], "rb").read(), b"{corrupt")

    def test_validate_matches_module(self):
        code, d = self.call("POST", "/api/paired/validate", {"study": syn()})
        self.assertEqual(d["counts"], paired.validate(syn())["counts"])

    def test_freeze_endpoint_refuses_without_files(self):
        code, d = self.call("POST", "/api/paired/freeze", {"study": syn()})
        self.assertEqual(code, 422)
        self.assertFalse(d["ok"])
        self.assertEqual(sum("not on disk" in r for r in d["reasons"]), 12)
        self.assertEqual(self.call("GET", "/api/paired/snapshots")[1]["snapshots"], [])

    def test_frozen_study_cannot_be_saved_as_draft(self):
        s = syn()
        s["status"] = "frozen"
        self.assertEqual(self.call("PUT", "/api/paired", {"study": s})[0], 400)

    def test_selection_keeps_unknown_ids(self):
        code, d = self.call("PUT", "/api/selection", {"ids": ["18849166", "nope"]})
        self.assertEqual(code, 200)
        saved = json.load(open(os.path.join(self.state, "selection.json")))
        self.assertEqual(saved["ids"], ["18849166", "nope"])
        self.assertEqual(saved["unresolved"], ["nope"])

    def test_selftest_needs_a_temporary_state_dir(self):
        self.serve.set_state_dir(common.DATA)
        try:
            code, body = self.call("GET", "/selftest")
            self.assertEqual(code, 409)
        finally:
            self.serve.set_state_dir(self.state)
        self.assertEqual(self.call("GET", "/selftest")[0], 200)


class LegacyFileUntouched(unittest.TestCase):
    def test_zz_legacy_selection_byte_identical(self):
        self.assertEqual(legacy_hash(), LEGACY_BEFORE)


if __name__ == "__main__":
    unittest.main(verbosity=1)
