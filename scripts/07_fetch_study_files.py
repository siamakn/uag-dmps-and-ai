"""Step 7 (paired study) - capture the selected files and their checksums.

    python scripts/07_fetch_study_files.py                      # check data/paired_selection.json
    python scripts/07_fetch_study_files.py --proposal           # check the cohort proposal's 12 PDFs
    python scripts/07_fetch_study_files.py --download           # also fetch files missing locally
    python scripts/07_fetch_study_files.py --download --write   # and record the checksums in the study

Only files explicitly selected in the study (or the proposal) are touched. Downloads go
to data/paired-dmp-corpus/ (git-ignored; the documents keep their own licences) and are
hashed with SHA-256. A recorded checksum that no longer matches the bytes on disk is
reported, never silently replaced: changed remote bytes are a different source version.
The repository's own checksum (e.g. md5) is kept separately from the local digest.

--write rewrites the study file atomically. Do not run it while the dashboard is open
on the same file, or the next save from the browser will overwrite these updates; the
dashboard's own "Check files" button does the same thing without that race.

Stdlib only.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import paired  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Check, fetch and hash the paired study's selected files.")
    ap.add_argument("--study", default=os.path.join(common.DATA, paired.STUDY_FILE))
    ap.add_argument("--proposal", action="store_true", help="use the cohort proposal instead of a study file")
    ap.add_argument("--download", action="store_true", help="fetch files that are missing locally")
    ap.add_argument("--write", action="store_true", help="record checksums back into the study file")
    a = ap.parse_args()

    if a.proposal:
        study = paired.proposal_to_study()
        if a.write:
            raise SystemExit("--write is for a study file; the proposal is a research input and stays as it is")
    else:
        study, err = paired.read_study(a.study)
        if err or study is None:
            raise SystemExit(err or "no study at %s" % a.study)

    facts = paired.file_facts(study)
    if a.download:
        facts = paired.download_missing(study, facts)

    ok = missing = mismatch = 0
    for key in sorted(facts):
        f = facts[key]
        doc = study["documents"][f["doc_id"]]
        rec = doc["files"][f["index"]]
        if f.get("present"):
            if rec.get("sha256") and rec["sha256"] != f["sha256"]:
                mismatch += 1
                state = "MISMATCH (recorded %s…, on disk %s…)" % (rec["sha256"][:12], f["sha256"][:12])
                rec["access"] = "contradictory"
            else:
                ok += 1
                state = "ok %s…" % f["sha256"][:12]
                rec.update(sha256=f["sha256"], bytes=f["bytes"], local_path=f["local_path"], access="verified")
                if f.get("retrieved"):
                    rec["retrieved"] = f["retrieved"]
        else:
            missing += 1
            state = "missing" + (" (%s)" % f["error"] if f.get("error") else "")
            if f.get("access") == "failed":
                rec["access"] = "failed"
        print("%-28s %-40s %s" % (f["doc_id"][:28], (rec.get("name") or "")[:40], state))
    print("%d ok, %d missing, %d mismatched" % (ok, missing, mismatch))

    manifest = os.path.join(common.ROOT, paired.CORPUS_DIR, "files-manifest.json")
    os.makedirs(os.path.dirname(manifest), exist_ok=True)
    paired.write_atomic(manifest, paired.canonical({"generated": paired.now_iso(), "facts": facts}))
    if a.write:
        study["updated"] = paired.now_iso()
        paired.write_atomic(a.study, paired.canonical(study))
        print("recorded checksums in %s" % a.study)
    sys.exit(1 if mismatch else 0)


if __name__ == "__main__":
    main()
