"""Step 6 (paired study) - discovery: group the pool by project and walk version chains.

    python scripts/06_discover_versions.py groups
    python scripts/06_discover_versions.py versions [--scope granted|all] [--limit N] [--pause 1.0]
    python scripts/06_discover_versions.py register --doc-id ID --title T --grant G --url URL
                                                    [--file PATH] [--record-id N] ...

groups    Groups every actual plan (kind == dmp) in data/dmp_dataset.json by grant. No
          publication-date window is applied: a pair is decided by issue dates read from the
          documents, so a 2024+ filter here could hide the earlier version. Sharing a grant
          makes documents candidates, never a verified pair.
          -> data/paired-discovery/groups.json

versions  For every plan in scope, asks Zenodo for all versions of the record's concept
          (GET /api/records/<id>/versions, paged until the reported total is reached). Each
          concept is fetched once; raw responses are cached with retrieval timestamps, and a
          re-run reuses the cache. Versions missing from the saved harvest are listed as
          leads. Coverage and failures are recorded, because absence from this report is not
          evidence that no other version exists: a revised DMP is often deposited as a new
          concept (iMagine D1.2 and D1.4 are two unrelated Zenodo concepts).
          -> data/paired-discovery/versions.json, cache/ (git-ignored)

register  Adds an externally found document to data/study-documents.json with provenance,
          so the dashboard offers it as a candidate. Never invents a Zenodo id. With --file,
          the local copy's size and SHA-256 are recorded.

Stdlib only. Read-only against Zenodo.
"""
import argparse
import collections
import datetime
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import paired  # noqa: E402

OUT = os.path.join(common.DATA, "paired-discovery")
CACHE = os.path.join(OUT, "cache")
# The legacy JSON serialisation carries parent (concept) ids, version indexes, file
# checksums and content links; the InvenioRDM one leaves content links out.
VHEADERS = {"User-Agent": common.HEADERS["User-Agent"], "Accept": "application/json"}


def now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def plans():
    return [r for r in common.load_dataset() if r.get("kind") == "dmp"]


def cmd_groups(_):
    rows = plans()
    by = collections.defaultdict(list)
    for r in rows:
        if r.get("grant"):
            by[str(r["grant"])].append(r)
    groups = []
    for g, rs in sorted(by.items()):
        rs.sort(key=lambda r: (r.get("date") or "", r["id"]))
        f = rs[0]
        groups.append({
            "grant": g, "acronym": f.get("acronym"), "tier": f.get("tier"),
            "cordis_branches": f.get("disc_all") or [], "dominant": f.get("disc"),
            "project_start": f.get("proj_start"), "project_end": f.get("proj_end"),
            "n_records": len(rs),
            "records": [{"id": r["id"], "title": r.get("title"), "version": r.get("version"),
                         "published": r.get("date"), "files": [x.get("name") for x in r.get("files") or []]}
                        for r in rs],
        })
    multi = [x for x in groups if x["n_records"] >= 2]
    doc = {
        "generated": now(), "source": "data/dmp_dataset.json",
        "source_sha256": paired.sha256_or_none(paired.DATASET),
        "procedure": "all records with kind == dmp, grouped by grant; no publication-date filter",
        "coverage": {
            "plans": len(rows), "plans_with_grant": sum(len(v) for v in by.values()),
            "plans_without_grant": len(rows) - sum(len(v) for v in by.values()),
            "grants": len(groups), "grants_with_2plus_records": len(multi),
            "grants_with_2plus_and_cordis_branch": sum(1 for x in multi if x["cordis_branches"]),
        },
        "note": "Same grant = candidate group only. Partner DMPs of one consortium are not versions of "
                "each other; lineage needs document evidence.",
        "groups": groups,
    }
    os.makedirs(OUT, exist_ok=True)
    paired.write_atomic(os.path.join(OUT, "groups.json"), paired.canonical(doc))
    c = doc["coverage"]
    print("groups: %d plans, %d with a grant in %d groups; %d groups have 2+ records (%d with a CORDIS branch)"
          % (c["plans"], c["plans_with_grant"], c["grants"], c["grants_with_2plus_records"],
             c["grants_with_2plus_and_cordis_branch"]))


def fetch_versions(record_id, pause):
    """All versions of the concept a record belongs to. Pages until the reported total."""
    hits, page, total = [], 1, None
    while True:
        url = "%s/%s/versions?%s" % (common.API, record_id, urllib.parse.urlencode(
            {"size": common.PAGE_SIZE, "page": page, "sort": "version", "allversions": "true"}))
        d = json.loads(common.fetch(url, headers=VHEADERS).decode("utf-8"))
        batch = d["hits"]["hits"]
        total = d["hits"]["total"]
        hits.extend(batch)
        if len(hits) >= total or not batch:
            break
        page += 1
        time.sleep(pause)
    return hits, total


def summarise(h):
    files = h.get("files") if isinstance(h.get("files"), list) else []
    return {
        "id": str(h.get("id")), "doi": h.get("doi"), "title": (h.get("metadata") or {}).get("title"),
        "published": (h.get("metadata") or {}).get("publication_date"),
        "version": (h.get("metadata") or {}).get("version"),
        "version_index": (((h.get("metadata") or {}).get("relations") or {}).get("version") or [{}])[0].get("index"),
        "files": [{"name": f.get("key"), "bytes": f.get("size"), "repository_checksum": f.get("checksum"),
                   "url": (f.get("links") or {}).get("self")} for f in files],
    }


def cmd_versions(a):
    os.makedirs(CACHE, exist_ok=True)
    rows = plans()
    if a.scope == "granted":
        rows = [r for r in rows if r.get("grant")]
    rows.sort(key=lambda r: r["id"])
    known = {r["id"] for r in common.load_dataset()}
    index_path = os.path.join(CACHE, "record-to-concept.json")
    rec2con = json.load(open(index_path)) if os.path.exists(index_path) else {}
    concepts, failures, fetched, reused = {}, [], 0, 0
    todo = rows[:a.limit] if a.limit else rows
    for i, r in enumerate(todo, 1):
        rid = r["id"]
        con = rec2con.get(rid)
        if con and os.path.exists(os.path.join(CACHE, "concept-%s.json" % con)):
            if con not in concepts:
                concepts[con] = json.load(open(os.path.join(CACHE, "concept-%s.json" % con)))
                reused += 1
            continue
        try:
            hits, total = fetch_versions(rid, a.pause)
        except Exception as e:
            failures.append({"record_id": rid, "error": str(e)[:200], "at": now()})
            time.sleep(a.pause)
            continue
        fetched += 1
        con = str((hits[0].get("conceptrecid") if hits else None) or
                  ((((hits[0].get("metadata") or {}).get("relations") or {}).get("version") or [{}])[0]
                   .get("parent") or {}).get("pid_value") if hits else rid)
        entry = {"concept": con, "retrieved": now(), "reported_total": total, "fetched": len(hits),
                 "complete": len(hits) >= (total or 0), "via_record": rid,
                 "versions": [summarise(h) for h in hits]}
        with open(os.path.join(CACHE, "concept-%s.json" % con), "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
        for v in entry["versions"]:
            rec2con[v["id"]] = con
        rec2con[rid] = con
        concepts[con] = entry
        if i % 50 == 0:
            paired.write_atomic(index_path, json.dumps(rec2con))
            print("  %d/%d records, %d concepts fetched, %d failures" % (i, len(todo), fetched, len(failures)))
            sys.stdout.flush()
        time.sleep(a.pause)
    paired.write_atomic(index_path, json.dumps(rec2con))

    leads, multi = [], 0
    for con, e in sorted(concepts.items()):
        if len(e["versions"]) > 1:
            multi += 1
        missing = [v for v in e["versions"] if v["id"] not in known]
        if missing and len(e["versions"]) > 1:
            leads.append({"concept": con, "in_dataset": [v["id"] for v in e["versions"] if v["id"] in known],
                          "absent_from_dataset": missing})
    doc = {
        "generated": now(), "scope": a.scope,
        "procedure": "GET /api/records/<id>/versions for each plan in scope, sort=version, size=25 anonymous (100 with ZENODO_TOKEN), paged to "
                     "the reported total; one fetch per concept; cached",
        "coverage": {"records_in_scope": len(rows), "records_processed": len(todo),
                     "concepts": len(concepts), "fetched_now": fetched, "reused_from_cache": reused,
                     "failures": len(failures),
                     "incomplete_pagination": sum(1 for e in concepts.values() if not e["complete"]),
                     "concepts_with_2plus_versions": multi, "concepts_with_versions_absent": len(leads)},
        "limits": "Only Zenodo version chains. A revised DMP deposited as a separate concept, or hosted "
                  "elsewhere, is not found here. A lead is not a verified pair.",
        "failures": failures, "leads": leads,
    }
    paired.write_atomic(os.path.join(OUT, "versions.json"), paired.canonical(doc))
    print("versions: %s" % json.dumps(doc["coverage"]))


def cmd_register(a):
    reg = paired.load_registry()
    docs = reg.setdefault("documents", [])
    if any(d["doc_id"] == a.doc_id for d in docs) and not a.replace:
        raise SystemExit("%s is already registered; pass --replace to overwrite it" % a.doc_id)
    f = {"name": a.file_name or os.path.basename(urllib.parse.urlparse(a.url).path) or a.doc_id,
         "url": a.url, "format": a.format, "bytes": None, "sha256": None, "local_path": None}
    if a.file:
        full = os.path.abspath(a.file)
        f.update(bytes=os.path.getsize(full), sha256=paired.sha256_file(full),
                 local_path=os.path.relpath(full, common.ROOT).replace(os.sep, "/"))
    entry = {
        "doc_id": a.doc_id, "record_id": a.record_id, "record_url": a.record_url, "doi": a.doi,
        "title": a.title, "version_label": a.version_label or "", "grant": a.grant, "acronym": a.acronym,
        "tier": a.tier, "project_start": a.project_start, "project_end": a.project_end,
        "cordis_branches": [b.strip() for b in (a.branches or "").split(";") if b.strip()],
        "publication_date": a.publication_date, "creators": [], "files": [f],
        "provenance": {"found_via": a.found_via, "source_url": a.url, "registered": now()[:10],
                       "registered_by": a.by, "note": a.note or ""},
    }
    docs[:] = [d for d in docs if d["doc_id"] != a.doc_id] + [entry]
    docs.sort(key=lambda d: d["doc_id"])
    paired.write_atomic(paired.REGISTRY, paired.canonical(reg))
    print("registered %s in %s" % (a.doc_id, paired.REGISTRY))


def main():
    ap = argparse.ArgumentParser(description="Paired-study discovery.")
    sub = ap.add_subparsers(dest="cmd")
    sub.required = True
    sub.add_parser("groups")
    v = sub.add_parser("versions")
    v.add_argument("--scope", choices=["granted", "all"], default="granted",
                   help="granted: plans with a grant number (the only ones that can fill a pair)")
    v.add_argument("--limit", type=int, default=0)
    v.add_argument("--pause", type=float, default=1.0, help="seconds between requests")
    r = sub.add_parser("register")
    for name in ("doc-id", "title", "grant", "url", "found-via"):
        r.add_argument("--" + name, required=True)
    for name in ("record-id", "record-url", "doi", "version-label", "acronym", "project-start", "project-end",
                 "publication-date", "branches", "file", "file-name", "note"):
        r.add_argument("--" + name)
    r.add_argument("--tier", default="Other EU")
    r.add_argument("--format", default="pdf")
    r.add_argument("--by", default=os.environ.get("USER", "unknown"))
    r.add_argument("--replace", action="store_true")
    a = ap.parse_args()
    {"groups": cmd_groups, "versions": cmd_versions, "register": cmd_register}[a.cmd](a)


if __name__ == "__main__":
    main()
