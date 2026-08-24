"""Step 2 - download the candidate .json files and keep the real maDMPs.

A .json file in a DMP record is not necessarily a maDMP: records also carry
ro-crate-metadata.json, codemeta.json, Zenodo metadata exports and plain
research data. The only reliable test is opening the file and looking for a
top-level "dmp" object, which is what the RDA DMP Common Standard mandates.

Downloads are skipped when the file already exists, so re-running is cheap.

    python scripts/02_download_madmps.py
"""
import glob
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

MAX_BYTES = 2_000_000
DMP_WORDS = ("dmp", "data management plan", "datamanagementplan", "data_management")


def looks_like_dmp(text):
    t = (text or "").lower()
    return any(w in t for w in DMP_WORDS)


def collect_candidates():
    records = {}
    for path in glob.glob(os.path.join(common.RAW, "*.jsonl")):
        for r in common.read_jsonl(path):
            records[str(r["id"])] = r
    cands = []
    for r in records.values():
        for f in r["files"]:
            if (f.get("ext") or "").lower() != "json":
                continue
            if (f.get("size") or 0) > MAX_BYTES:
                continue
            if (r["type"] == "publication-datamanagementplan"
                    or looks_like_dmp(f["key"]) or looks_like_dmp(r["title"])):
                cands.append({"rec": str(r["id"]), "key": f["key"],
                              "size": f["size"], "link": f["link"]})
    return records, cands


def content_url(rec, key, link):
    return link or ("https://zenodo.org/api/records/%s/files/%s/content"
                    % (rec, urllib.parse.quote(key, safe="")))


def main():
    common.ensure_dirs()
    records, cands = collect_candidates()
    print("%d records -> %d candidate .json files" % (len(records), len(cands)))

    saved = skipped = failed = 0
    for i, c in enumerate(cands, 1):
        path = os.path.join(common.CORPUS, common.corpus_name(c["rec"], c["key"]))
        if os.path.exists(path):
            skipped += 1
            continue
        try:
            blob = common.fetch(content_url(c["rec"], c["key"], c["link"]),
                                headers={"User-Agent": common.HEADERS["User-Agent"]})
            with open(path, "wb") as f:
                f.write(blob)
            saved += 1
        except Exception as e:
            failed += 1
            print("  ! %s/%s: %s" % (c["rec"], c["key"][:40], str(e)[:70]))
        if i % 50 == 0:
            print("  %d/%d" % (i, len(cands)))
        time.sleep(0.25)

    kinds = {"rda-dcs": 0, "other": 0, "unparseable": 0}
    for p in glob.glob(os.path.join(common.CORPUS, "*.json")):
        try:
            o = json.load(open(p, encoding="utf-8-sig"))
        except Exception:
            kinds["unparseable"] += 1
            continue
        kinds["rda-dcs" if isinstance(o, dict) and isinstance(o.get("dmp"), dict)
              else "other"] += 1

    json.dump(cands, open(os.path.join(common.DATA, "candidates.json"), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=1)
    print("downloaded %d, already present %d, failed %d" % (saved, skipped, failed))
    print("corpus contents: %s" % kinds)


if __name__ == "__main__":
    main()
