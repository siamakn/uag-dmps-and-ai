"""Step 4 - join the Zenodo records to CORDIS and write the selection dataset.

Zenodo alone cannot answer the two questions the selection criteria depend on:
which discipline a DMP belongs to, and where in the project's life it was
written. CORDIS answers both. Joining on the EU grant number gives:

  * project start and end dates -> the DMP's publication date becomes a
    position on the project timeline, which is the lifecycle stage
  * EuroSciVoc terms -> the OECD field of science, used as the discipline axis

Grant numbers come from two places: the Zenodo funding metadata, and the
dmp.project.funding.grant_id field inside the maDMP file itself. The second
source matters - roughly half the Horizon Europe maDMPs are not tagged as EU
funded in their Zenodo record.

The CORDIS bulk files are ~90 MB and are downloaded on first run.

    python scripts/04_build_dataset.py
"""
import collections
import csv
import datetime
import glob
import io
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

csv.field_size_limit(10 ** 8)

CORDIS_SETS = [
    ("he.zip", "HORIZON", "https://cordis.europa.eu/data/cordis-HORIZONprojects-csv.zip"),
    ("h2020.zip", "H2020", "https://cordis.europa.eu/data/cordis-h2020projects-csv.zip"),
]
DMP_REQUIRED = ["contact", "created", "dataset", "dmp_id", "ethical_issues_exist",
                "language", "modified", "title"]
DMP_TITLE = re.compile(r"\bdmp\b|data\s*manage?ment\s*plan|datamanagementplan|madmp", re.I)

# A record whose title mentions "data management plan" is very often *about* DMPs
# rather than being one: posters, workshop guides, templates, project reports.
# These signals separate the plans from the literature. Metadata only - resource
# type and title - so the split stays reproducible and free of quality judgement.
TEMPLATE_TITLE = re.compile(
    r"\btemplates?\b|\bvorlage|boilerplate|\bworkbook\b|\bchecklist\b|\bmuster\b|"
    r"\bexample\s+(ma)?dmp\b|\bsample\s+dmp\b|\bskeleton\b", re.I)
GUIDE_TITLE = re.compile(
    r"\bhow\s+to\b|\bguide\b|\bguidelines?\b|\bhandbook\b|\binstructions?\b|"
    r"\brecommendations?\b|\btraining\b|\bworkshop\b|\btutorial\b|\bcourse\b|"
    r"\blesson\b|\bprimer\b|best\s+practice|\bleitfaden\b|\banleitung\b|\bfaq\b", re.I)
GUIDE_TAIL = re.compile(
    r"\b(handbook|guide|guidelines?|tutorial|course|manual|instructions?)\s*$", re.I)
# Scholarly output that talks about DMPs; it is not itself a plan.
ABOUT_TYPES = {
    "poster", "presentation", "publication-conferencepaper", "publication-article",
    "publication-preprint", "publication-book", "publication-section",
    "publication-thesis", "lesson", "software", "video", "image",
    "publication-workingpaper", "publication-technicalnote", "publication-patent",
}
# Record types that can plausibly *be* a plan. Deliverables, reports, milestones
# and standards are where project DMPs actually live.
STRONG_PLAN_TYPES = {
    "publication-datamanagementplan", "publication-deliverable", "publication-report",
    "publication-milestone", "publication-standard", "publication-projectdeliverable",
}
WEAK_PLAN_TYPES = {"publication", "publication-other", "other", "dataset", "workflow"}

# The title opens by naming itself a plan: "D1.1 Data Management Plan v2",
# "NOVAFERT Data Management Plan", "Final data management plan".
PLAN_HEAD = re.compile(
    r"^\W*"
    r"(deliverable\s*)?"
    r"([A-Za-z0-9][\w&+.-]{0,18}[\s:_–-]{1,3}){0,5}"      # optional acronym / deliverable code
    r"(final|initial|preliminary|updated?|revised|open|research|first|second|third)?\s*"
    r"(data\s*(and\s+[\w ]{0,20}?\s*)?manage?ment\s*plan|dmp|ddomp|rdmp)\b", re.I)
# ... but "DMP Evaluation Service" or "DMP Writing Made Easy" is about the activity,
# not a plan. If one of these follows the plan phrase, it is not a plan.
ACTIVITY_AFTER = re.compile(
    r"\b(data\s*manage?ment\s*plan|dmp|rdmp)s?\W+"
    r"(writing|creation|creating|authoring|development|developing|evaluation|evaluating|"
    r"assessment|assessing|analysis|comparison|tool|tools|service|services|"
    r"training|workshop|course|support|automation|generator|checker|interoperability|"
    r"requirements|landscape|survey|study)\b", re.I)
# Titles that announce a piece of scholarship about DMPs.
ABOUT_HEAD = re.compile(
    r"^\W*(towards?|identification|identifying|evaluation|evaluating|assessment|assessing|"
    r"analysis|analysing|analyzing|comparison|comparing|collecting|building|standardi[sz]ing|"
    r"exploring|understanding|introducing|implementing|developing|designing|measuring|"
    r"a\s+(study|review|survey|framework|comparison)|on\s+the\b|lessons\b|"
    r"experiences?\b|reflections?\b|what\b|why\b|how\b)", re.I)


def classify_kind(title, rtype, madmp, n_datasets):
    """Sort records into dmp / template / guidance / about / unclear.

    Metadata only - Zenodo resource type plus title shape - so the split is
    reproducible and carries no judgement about DMP quality. It is a heuristic:
    the dashboard shows the verdict and its reason on every row so it can be
    overridden by eye.
    """
    title = (title or "").strip()
    if TEMPLATE_TITLE.search(title):
        return "template", "title says template or workbook"
    if madmp and (n_datasets or 0) > 0:
        return "dmp", "machine-actionable file describing datasets"
    if ACTIVITY_AFTER.search(title):
        return ("about" if rtype in ABOUT_TYPES else "guidance",
                "title is about DMP work rather than being a plan")
    if ABOUT_HEAD.search(title):
        return ("about" if rtype in ABOUT_TYPES else "about",
                "title opens like a paper about DMPs")
    if rtype in ABOUT_TYPES:
        return "about", "resource type is %s, so it is output about DMPs" % rtype
    if rtype == "publication-datamanagementplan":
        return "dmp", "Zenodo resource type is data management plan"
    head_match = PLAN_HEAD.search(title)
    if head_match:
        # "NFDI-MatWerk Guide: Research Data Management Plan" - the guide word sits
        # in front of the plan phrase, so the record is guidance about a plan.
        if GUIDE_TITLE.search(title[:head_match.end()]):
            return "guidance", "a guide to writing a plan rather than a plan"
        # "... Data Management Plan Handbook" - trailing guide word. But
        # "... Data management plan & ethical guidelines" is a compound deliverable.
        tail = GUIDE_TAIL.search(title)
        if tail and not re.search(r"(&|\band\b|\+)\s*\w*\s*$", title[:tail.start()]):
            return "guidance", "titled as a plan but the record is a handbook or guide"
        return "dmp", "title names itself a data management plan"
    if GUIDE_TITLE.search(title):
        return "guidance", "title says guide, handbook, training or similar"
    if madmp:
        return "dmp", "carries a machine-actionable DMP file"
    if rtype in STRONG_PLAN_TYPES and DMP_TITLE.search(title):
        return "dmp", "project deliverable or report with a DMP title"
    if rtype in WEAK_PLAN_TYPES and DMP_TITLE.search(title):
        return "unclear", "mentions a DMP but the record type does not confirm it is one"
    return "unclear", "mentions DMP but nothing confirms it is one"


SENSITIVE_WORDS = re.compile(
    r"\bgdpr\b|personal data|sensitive data|pseudonym|anonymi|ethic|informed consent|"
    r"patient|clinical|special categor", re.I)


# --------------------------------------------------------------- CORDIS
def load_cordis(path, framework):
    z = zipfile.ZipFile(path)
    proj = {}
    with z.open("project.csv") as f:
        for x in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"), delimiter=";"):
            pid = (x.get("id") or "").strip()
            if not pid:
                continue
            proj[pid] = {
                "fp": framework,
                "acronym": x.get("acronym") or "",
                "title": x.get("title") or "",
                "start": (x.get("startDate") or "")[:10],
                "end": (x.get("endDate") or "")[:10],
                "status": x.get("status") or "",
                "legal": x.get("legalBasis") or "",
                "call": x.get("masterCall") or x.get("topics") or "",
                "_l1": [], "_l2": [], "_pairs": [],
            }
    if "euroSciVoc.csv" in z.namelist():
        with z.open("euroSciVoc.csv") as f:
            for x in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"), delimiter=";"):
                p = proj.get((x.get("projectID") or "").strip())
                if not p:
                    continue
                parts = [q for q in (x.get("euroSciVocPath") or "").split("/") if q]
                if parts:
                    p["_l1"].append(parts[0])
                    if len(parts) > 1:
                        p["_l2"].append(parts[1])
                        p["_pairs"].append((parts[0], parts[1]))
    for p in proj.values():
        p["disc_all"] = [d for d, _ in collections.Counter(p["_l1"]).most_common()]
        p["disc_primary"] = p["disc_all"][0] if p["disc_all"] else ""
        p["disc2_all"] = [d for d, _ in collections.Counter(p["_l2"]).most_common(4)]
        # every (branch, sub-field) pair, most used first, so a sub-field is never
        # shown under a branch it does not belong to
        p["fields"] = [list(k) for k, _ in collections.Counter(p["_pairs"]).most_common(14)]
        del p["_l1"], p["_l2"], p["_pairs"]
    return proj


def cordis_index():
    index = {}
    for fname, framework, url in CORDIS_SETS:
        path = os.path.join(common.CORDIS, fname)
        if not os.path.exists(path):
            print("downloading CORDIS %s bulk data (~50 MB)" % framework)
            with open(path, "wb") as f:
                f.write(common.fetch(url, headers={"User-Agent": common.HEADERS["User-Agent"]},
                                     timeout=600))
        for k, v in load_cordis(path, framework).items():
            index.setdefault(k, v)
    return index


# --------------------------------------------------------------- maDMP corpus
def parse_corpus(findings):
    out = {}
    for p in glob.glob(os.path.join(common.CORPUS, "*.json")):
        try:
            o = json.load(open(p, encoding="utf-8-sig"))
        except Exception:
            continue
        if not (isinstance(o, dict) and isinstance(o.get("dmp"), dict)):
            continue
        d = o["dmp"]
        base = os.path.basename(p)
        rid = base.split("__")[0]
        datasets = d.get("dataset") or []
        datasets = datasets if isinstance(datasets, list) else [datasets]
        datasets = [x for x in datasets if isinstance(x, dict)]
        dist = [x for y in datasets for x in (y.get("distribution") or [])]
        populated = [x for x in dist if isinstance(x, dict) and x]

        def yes(v):
            return str(v).strip().lower() in ("yes", "true")

        grants, start, end = set(), "", ""
        projects = d.get("project") or []
        projects = projects if isinstance(projects, list) else [projects]
        for pr in projects:
            if not isinstance(pr, dict):
                continue
            start = start or (pr.get("start") or "")[:10]
            end = end or (pr.get("end") or "")[:10]
            for fu in (pr.get("funding") or []):
                g = fu.get("grant_id")
                g = g.get("identifier") if isinstance(g, dict) else g
                grants.update(re.findall(r"\b(\d{6,9})\b", str(g or "")))

        errs = findings.get(base, [])
        entry = {
            "file": base,
            "n_datasets": len(datasets),
            "n_dist": len(dist),
            "n_dist_real": len(populated),
            "personal": sum(1 for y in datasets if yes(y.get("personal_data"))),
            "sensitive": sum(1 for y in datasets if yes(y.get("sensitive_data"))),
            "secpriv": sum(1 for y in datasets if y.get("security_and_privacy")),
            "ethics": str(d.get("ethical_issues_exist", "")).lower(),
            "grants": sorted(grants),
            "p_start": start, "p_end": end,
            "missing_top": [k for k in DMP_REQUIRED
                            if k not in d or d[k] in (None, "", [])],
            "n_findings": len(errs),
            "schema_ok": errs == [],
            "desc_chars": sum(len(y.get("description") or "") for y in datasets),
        }
        cur = out.get(rid)
        if not cur or entry["desc_chars"] > cur["desc_chars"]:
            out[rid] = entry
    return out


# --------------------------------------------------------------- lifecycle
def lifecycle(published, start, end):
    """Where the DMP sits in the project's run: <=34% early, <=70% mid, else late."""
    try:
        p = datetime.date.fromisoformat(published[:10])
        s = datetime.date.fromisoformat(start)
        e = datetime.date.fromisoformat(end)
    except Exception:
        return "unknown", None
    span = (e - s).days
    if span <= 0:
        return "unknown", None
    frac = round((p - s).days / span, 3)
    if frac < 0:
        return "pre-start", frac
    if frac <= 0.34:
        return "early", frac
    if frac <= 0.70:
        return "mid", frac
    return "late", frac


def funding_tier(project, programs, funders):
    if project and project["fp"] == "HORIZON":
        return "Horizon Europe", "HORIZON"
    if project and project["fp"] == "H2020":
        return "Horizon 2020", "H2020"
    if any(p.startswith("HORIZON") for p in programs):
        return "Horizon Europe", "HORIZON"
    if any(p.upper().startswith("H2020") for p in programs):
        return "Horizon 2020", "H2020"
    if "European Commission" in funders:
        return "Other EU", "EC"
    if any("Deutsche Forschungsgemeinschaft" in f for f in funders):
        return "DFG", "DFG"
    return ("Other funder", "") if funders else ("No funder metadata", "")


def main():
    common.ensure_dirs()
    cordis = cordis_index()
    print("CORDIS projects: %d %s" % (
        len(cordis), collections.Counter(p["fp"] for p in cordis.values())))

    records = {}
    for path in glob.glob(os.path.join(common.RAW, "*.jsonl")):
        for r in common.read_jsonl(path):
            records[str(r["id"])] = r
    print("zenodo records: %d" % len(records))

    fpath = os.path.join(common.DATA, "schema_findings.json")
    findings = json.load(open(fpath, encoding="utf-8")) if os.path.exists(fpath) else {}
    madmp = parse_corpus(findings)
    print("maDMP files parsed: %d" % len(madmp))

    rows = []
    for rid, r in records.items():
        md = madmp.get(rid)
        title = r.get("title") or ""
        if not (r.get("type") == "publication-datamanagementplan"
                or md or DMP_TITLE.search(title)):
            continue
        zenodo_grants = [str(f["number"]).strip()
                         for f in (r.get("funding") or []) if f.get("number")]
        cand = [g for g in dict.fromkeys(zenodo_grants + (md or {}).get("grants", []))
                if g in cordis]
        project = cordis.get(cand[0]) if cand else None
        funders = {(f.get("funder") or "") for f in (r.get("funding") or [])}
        programs = {(f.get("program") or "") for f in (r.get("funding") or [])}
        tier, program = funding_tier(project, programs, funders)

        stage, frac, source = "unknown", None, ""
        if project and project["start"] and project["end"]:
            stage, frac = lifecycle(r["date"], project["start"], project["end"])
            source = "cordis"
        if stage == "unknown" and md and md["p_start"] and md["p_end"]:
            stage, frac = lifecycle(r["date"], md["p_start"], md["p_end"])
            source = "madmp"

        blob = " ".join([title, r.get("desc") or "", " ".join(r.get("subjects") or [])])
        flagged = bool(md and (md["personal"] or md["sensitive"]
                               or md["ethics"] in ("yes", "true") or md["secpriv"]))
        json_files = [f for f in (r.get("files") or [])
                      if (f.get("ext") or "").lower() == "json"]
        pdfs = [f for f in (r.get("files") or []) if (f.get("ext") or "").lower() == "pdf"]
        kind, kind_why = classify_kind(title, r.get("type"), bool(md),
                                       (md or {}).get("n_datasets"))
        files = [{"name": f.get("key"), "ext": f.get("ext"), "size": f.get("size")}
                 for f in (r.get("files") or [])][:12]
        funders = [{"funder": f.get("funder"), "number": f.get("number"),
                    "acronym": f.get("acronym"), "program": f.get("program"),
                    "title": f.get("title")}
                   for f in (r.get("funding") or [])][:8]

        rows.append({
            "id": rid, "doi": r.get("doi"), "title": title, "date": r.get("date"),
            "year": (r.get("date") or "")[:4], "type": r.get("type"),
            "access": r.get("access"), "version": r.get("version"),
            "desc": (r.get("desc") or "")[:1600], "subjects": (r.get("subjects") or [])[:12],
            "creators": (r.get("creators") or [])[:8],
            "files": files, "funders": funders,
            "kind": kind, "kind_why": kind_why,
            "tier": tier, "program": program,
            "grant": cand[0] if cand else (zenodo_grants[0] if zenodo_grants else ""),
            "acronym": (project or {}).get("acronym") or next(
                (f.get("acronym") for f in (r.get("funding") or []) if f.get("acronym")), ""),
            "proj_title": (project or {}).get("title", ""),
            "call": (project or {}).get("call", ""),
            "legal": (project or {}).get("legal", ""),
            "proj_status": (project or {}).get("status", ""),
            "proj_start": (project or {}).get("start", "") or (md or {}).get("p_start", ""),
            "proj_end": (project or {}).get("end", "") or (md or {}).get("p_end", ""),
            "disc": (project or {}).get("disc_primary", ""),
            "disc_all": (project or {}).get("disc_all", [])[:6],
            "disc2": (project or {}).get("disc2_all", [])[:3],
            "fields": (project or {}).get("fields", []),
            "stage": stage, "stage_frac": frac, "stage_src": source,
            "madmp": bool(md), "n_datasets": (md or {}).get("n_datasets"),
            "n_dist": (md or {}).get("n_dist_real"),
            "schema_ok": (md or {}).get("schema_ok"),
            "n_findings": (md or {}).get("n_findings"),
            "personal": (md or {}).get("personal", 0),
            "sensitive": (md or {}).get("sensitive", 0),
            "ethics": (md or {}).get("ethics", ""),
            "madmp_file": (md or {}).get("file", ""),
            "challenging": flagged or bool(SENSITIVE_WORDS.search(blob)),
            "ch_meta": flagged,
            "n_json": len(json_files), "n_pdf": len(pdfs),
            "url": "https://zenodo.org/records/" + rid,
            "dl": ("https://zenodo.org/api/records/%s/files/%s/content"
                   % (rid, json_files[0]["key"]) if json_files else ""),
        })

    rows.sort(key=lambda x: (x["date"] or ""), reverse=True)
    json.dump(rows, open(os.path.join(common.DATA, "dmp_dataset.json"), "w",
                         encoding="utf-8"), ensure_ascii=False)

    cols = ["doi", "title", "kind", "date", "tier", "program", "grant", "acronym", "call",
            "disc", "stage", "stage_frac", "proj_start", "proj_end", "proj_status",
            "madmp", "schema_ok", "n_datasets", "n_dist", "personal", "sensitive",
            "ethics", "challenging", "access", "url", "dl"]
    with open(os.path.join(common.DATA, "dmp_dataset.csv"), "w", encoding="utf-8",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c) for c in cols])

    print("rows: %d" % len(rows))
    print("funding tiers: %s" % collections.Counter(r["tier"] for r in rows).most_common())
    print("maDMPs: %d | with CORDIS discipline: %d"
          % (sum(1 for r in rows if r["madmp"]), sum(1 for r in rows if r["disc"])))
    print("lifecycle: %s" % collections.Counter(r["stage"] for r in rows).most_common())
    print("record kind: %s" % collections.Counter(r["kind"] for r in rows).most_common())
    l2 = {p[1] for r in rows for p in (r["fields"] or [])}
    print("EuroSciVoc level-2 fields present: %d" % len(l2))


if __name__ == "__main__":
    main()
