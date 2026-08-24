"""Shared helpers for the DMP harvesting pipeline: paths and Zenodo API access.

Set ZENODO_TOKEN in the environment to raise the anonymous page-size cap of 25
records per request to 100 and to get a higher rate limit. Everything works
without a token, just more slowly.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(DATA, "raw")
CORPUS = os.path.join(DATA, "madmp-corpus")
CORDIS = os.path.join(DATA, "cordis")
DASHBOARD = os.path.join(ROOT, "dashboard")

API = "https://zenodo.org/api/records"
TOKEN = os.environ.get("ZENODO_TOKEN")
PAGE_SIZE = 100 if TOKEN else 25
HEADERS = {
    "User-Agent": "uag-dmps-and-ai/1.0 (research; https://github.com/siamakn/uag-dmps-and-ai)",
    "Accept": "application/vnd.inveniordm.v1+json",
}
if TOKEN:
    HEADERS["Authorization"] = "Bearer " + TOKEN


def ensure_dirs():
    for d in (DATA, RAW, CORPUS, CORDIS, DASHBOARD):
        os.makedirs(d, exist_ok=True)


def fetch(url, headers=None, timeout=90):
    req = urllib.request.Request(url, headers=headers or HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url, timeout=90):
    return json.loads(fetch(url, timeout=timeout).decode("utf-8"))


def clean_text(x, limit=1800):
    """Strip HTML and collapse whitespace; Zenodo descriptions are HTML."""
    if not x:
        return ""
    if isinstance(x, dict):
        x = x.get("en") or next(iter(x.values()), "")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(x))).strip()[:limit]


def slim(hit):
    """Reduce an InvenioRDM record to the fields the pipeline needs."""
    m = hit.get("metadata", {})
    funding = []
    for f in m.get("funding", []) or []:
        a = f.get("award", {}) or {}
        funding.append({
            "funder": (f.get("funder") or {}).get("name"),
            "number": a.get("number"),
            "program": a.get("program"),
            "acronym": a.get("acronym"),
            "title": (a.get("title") or {}).get("en"),
        })
    files = []
    for k, v in ((hit.get("files") or {}).get("entries") or {}).items():
        files.append({
            "key": k, "ext": v.get("ext"), "size": v.get("size"),
            "link": (v.get("links") or {}).get("content"),
        })
    return {
        "id": hit.get("id"),
        "doi": (hit.get("pids", {}).get("doi") or {}).get("identifier"),
        "title": m.get("title"),
        "date": m.get("publication_date"),
        "type": (m.get("resource_type") or {}).get("id"),
        "access": (hit.get("access") or {}).get("record"),
        "version": m.get("version"),
        "desc": clean_text(m.get("description")),
        "subjects": [
            (s.get("subject") or s.get("title") or "") if isinstance(s, dict) else str(s)
            for s in (m.get("subject") or [])
        ][:25],
        "creators": [(c.get("person_or_org") or {}).get("name")
                     for c in (m.get("creators") or [])][:6],
        "funding": funding,
        "files": files,
    }


def search(q, sort="newest", max_pages=250, pause=0.5, verbose=True):
    """Page through a Zenodo search, returning slimmed records."""
    out, page = [], 1
    total = None
    while page <= max_pages:
        url = API + "?" + urllib.parse.urlencode(
            {"q": q, "size": PAGE_SIZE, "page": page, "sort": sort})
        d = get_json(url)
        hits = d["hits"]["hits"]
        total = d["hits"]["total"]
        out.extend(slim(h) for h in hits)
        if len(out) >= total or not hits:
            break
        page += 1
        time.sleep(pause)
    if verbose:
        print("  %-70s %d/%d" % (q[:70], len(out), total or 0))
    return out, total


def count(q):
    url = API + "?" + urllib.parse.urlencode({"q": q, "size": 1})
    return get_json(url)["hits"]["total"]


def write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def corpus_name(record_id, file_key):
    """Deterministic local filename for a downloaded maDMP file."""
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", file_key)[:80]
    name = "%s__%s" % (record_id, safe)
    return name if name.endswith(".json") else name + ".json"


# Fields the dashboard needs. Shared by the static build and the local server so
# the two can never drift apart.
DASHBOARD_FIELDS = [
    "id", "doi", "title", "date", "year", "tier", "program", "grant", "acronym",
    "proj_title", "call", "legal", "proj_status", "proj_start", "proj_end",
    "disc", "disc_all", "disc2", "stage", "stage_frac", "madmp", "n_datasets",
    "n_dist", "schema_ok", "n_findings", "personal", "sensitive", "ethics",
    "challenging", "ch_meta", "n_json", "n_pdf", "url", "dl", "access", "type",
    "madmp_file",
]


def payload_rows(rows):
    """Trim the full dataset down to what the dashboard renders."""
    out = []
    for r in rows:
        o = {k: r.get(k) for k in DASHBOARD_FIELDS}
        o["title"] = (r.get("title") or "")[:180]
        o["proj_title"] = (r.get("proj_title") or "")[:120]
        o["desc"] = (r.get("desc") or "")[:320]
        o["disc_all"] = (r.get("disc_all") or [])[:4]
        o["disc2"] = (r.get("disc2") or [])[:2]
        out.append(o)
    return out


def load_dataset():
    path = os.path.join(DATA, "dmp_dataset.json")
    if not os.path.exists(path):
        raise SystemExit("data/dmp_dataset.json is missing - run "
                         "scripts/04_build_dataset.py first")
    return json.load(open(path, encoding="utf-8"))
