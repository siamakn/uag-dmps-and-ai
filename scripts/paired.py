"""Paired DMP study: schema, exact timing, validation, import/export and freeze.

The paired study asks for six EU projects, one per broad EuroSciVoc discipline, each
contributing two versions of the same DMP: one issued at or before half the project
run, one issued after the project ended. This module is the authoritative Python
side of that design. The dashboard carries a JavaScript mirror of `timing` and
`validate`; `dashboard/paired-fixtures.json` pins both to the same expected results.

    python scripts/paired.py validate  [--study data/paired_selection.json]
    python scripts/paired.py proposal  > draft.json      # cohort proposal as an unverified draft
    python scripts/paired.py export    --format csv|md|json [--study ...]
    python scripts/paired.py freeze    [--study ...] [--state-dir data]
    python scripts/paired.py seed-registry               # writes data/study-documents.json

Nothing here reads a publication date as an issue date, rounds before classifying, or
marks lineage as verified on its own. A study that is missing evidence stays a draft.
Stdlib only.
"""
import argparse
import copy
import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

SCHEMA = "dmpbench.paired-study"
SCHEMA_VERSION = 1
REGISTRY_SCHEMA = "dmpbench.study-documents"
SNAPSHOT_SCHEMA = "dmpbench.paired-snapshot"

DISCIPLINES = [
    "natural sciences", "engineering and technology", "medical and health sciences",
    "agricultural sciences", "social sciences", "humanities",
]
STATES = ("not_checked", "verified", "contradictory", "unavailable")

STUDY_FILE = "paired_selection.json"
SNAPSHOT_DIR = "paired-snapshots"
REGISTRY = os.path.join(common.DATA, "study-documents.json")
PROPOSAL = os.path.join(common.ROOT, "research", "paired-dmp-study", "cohort-proposal.json")
DATASET = os.path.join(common.DATA, "dmp_dataset.json")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha256_or_none(path):
    return sha256_file(path) if os.path.isfile(path) else None


# ------------------------------------------------------------------ protocol
def default_protocol():
    return {
        "id": "paired-dmp-protocol-draft-2026-11-04",
        "approved": False,
        "approved_by": "",
        "approved_on": "",
        "disciplines": list(DISCIPLINES),
        "timing_basis": "documented DMP issue date; repository publication dates kept separately",
        "publication_date_fallback": False,
        "early_rule": "2*n <= d, i.e. fraction <= 0.50 (confirmed D01)",
        "late_rule": "n > d, i.e. fraction > 1, strict (confirmed D01)",
        "early_lower_bound": {"rule": "n >= 0", "status": "confirmed", "decision": "D19"},
        "pre_start_policy": {"value": "exclude", "status": "confirmed", "decision": "D19"},
        "project_end": {"rule": "latest authoritative end date including extensions; original dates "
                                "retained with sensitivity", "decision": "D09", "status": "confirmed"},
        "discipline": {"rule": "any documented CORDIS branch membership; one slot per project; dominant "
                               "branch also reported", "decision": "D08", "status": "confirmed"},
        # D16-D19 were confirmed by the user on 2026-11-06; see research/paired-dmp-study/decisions.md
        "open_decisions": [
            {"id": "issue-date-hierarchy", "status": "resolved", "decision": "D16",
             "note": "confirmed by Siamak Nakhaie 2026-11-06",
             "text": "An explicitly labelled issue / submission / delivery date wins, then the dated cover, "
                     "then that version's revision-history row. Other labelled dates are kept as "
                     "alternatives; if one would change the verdict the pair stays unresolved."},
            {"id": "partial-dates", "status": "resolved", "decision": "D17",
             "note": "confirmed by Siamak Nakhaie 2026-11-06",
             "text": "Partial dates (YYYY, YYYY-MM) are carried as intervals and stay indeterminate when "
                     "they straddle a threshold; an indeterminate pair cannot be frozen."},
            {"id": "representation", "status": "resolved", "decision": "D18",
             "note": "confirmed by Siamak Nakhaie 2026-11-06",
             "text": "When one version has both a PDF and a maDMP JSON, the PDF is the analysis file. A "
                     "pair may mix formats only if recorded as a confounder."},
            {"id": "pre-start", "status": "resolved", "decision": "D19",
             "note": "confirmed by Siamak Nakhaie 2026-11-06",
             "text": "A document issued before its project started cannot fill an early slot."},
        ],
    }


def empty_pair(discipline):
    return {
        "pair_id": slug(discipline),
        "discipline": discipline,
        "project": None,
        "cordis": None,
        "scope": "",
        "early": None,
        "late": None,
        "lineage": {"state": "not_checked", "evidence": [], "verified_by": "", "verified_on": "",
                    "prior_checks": []},
        "notes": "",
    }


def new_study(origin="empty"):
    t = now_iso()
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "draft",
        "study_id": "paired-draft-" + t[:10],
        "created": t,
        "updated": t,
        "origin": origin,
        "protocol": default_protocol(),
        "sources": {},
        "pairs": [empty_pair(d) for d in DISCIPLINES],
        "documents": {},
    }


def check_study(obj):
    """Return None if obj is a study this code understands, else a reason string."""
    if not isinstance(obj, dict):
        return "not a JSON object"
    if obj.get("schema") != SCHEMA:
        return "not a paired-study file (schema is %r)" % obj.get("schema")
    if obj.get("schema_version") != SCHEMA_VERSION:
        return "unsupported schema_version %r (this code reads %d)" % (
            obj.get("schema_version"), SCHEMA_VERSION)
    if not isinstance(obj.get("pairs"), list) or not isinstance(obj.get("documents"), dict):
        return "pairs must be a list and documents an object"
    return None


# ------------------------------------------------------------------ dates
DATE_RE = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$")


def parse_date(s):
    """Parse YYYY, YYYY-MM or YYYY-MM-DD into its earliest and latest possible day.

    A partial date is never widened into an observed day: '2023-03' means somewhere
    between 1 and 31 March, and stays that way through the arithmetic.
    """
    if s is None or str(s).strip() == "":
        return None
    m = DATE_RE.match(str(s).strip())
    if not m:
        return {"error": "unparseable date %r" % s}
    y, mo, d = m.group(1), m.group(2), m.group(3)
    try:
        if d:
            day = datetime.date(int(y), int(mo), int(d))
            return {"lo": day, "hi": day, "precision": "day"}
        if mo:
            lo = datetime.date(int(y), int(mo), 1)
            nxt = datetime.date(int(y) + (int(mo) == 12), int(mo) % 12 + 1, 1)
            return {"lo": lo, "hi": nxt - datetime.timedelta(days=1), "precision": "month"}
        return {"lo": datetime.date(int(y), 1, 1), "hi": datetime.date(int(y), 12, 31),
                "precision": "year"}
    except ValueError:
        return {"error": "impossible date %r" % s}


def _verdict(all_pass, none_pass):
    return "yes" if all_pass else ("no" if none_pass else "indeterminate")


def timing(issue, start, end, pre_start="exclude"):
    """Exact position of an issue date in a project run.

    n = issue - start and d = end - start, both whole days. Early is 2*n <= d (and n >= 0
    unless pre-start documents are allowed); late is n > d. A partial issue date gives an
    interval [n_lo, n_hi]: a verdict is 'yes' only if every possible day passes, 'no' if
    none does, otherwise 'indeterminate'. Percentages are for display only.
    """
    out = {"state": "unknown", "reason": "", "n_lo": None, "n_hi": None, "d": None,
           "early": "unknown", "late": "unknown", "precision": None}
    ps, pe = parse_date(start), parse_date(end)
    if not ps or not pe:
        out["reason"] = "project start or end date missing"
        return out
    if "error" in ps or "error" in pe:
        out.update(state="invalid", reason="project date unparseable")
        return out
    if ps["precision"] != "day" or pe["precision"] != "day":
        out["reason"] = "project dates must be exact days"
        return out
    d = (pe["lo"] - ps["lo"]).days
    out["d"] = d
    if d <= 0:
        out.update(state="invalid", reason="project duration is not positive (%d days)" % d)
        return out
    pi = parse_date(issue)
    if not pi:
        out["reason"] = "no documented issue date"
        return out
    if "error" in pi:
        out.update(state="invalid", reason=pi["error"])
        return out
    n_lo, n_hi = (pi["lo"] - ps["lo"]).days, (pi["hi"] - ps["lo"]).days
    lower = 0 if pre_start == "exclude" else None
    early_all = (lower is None or n_lo >= lower) and 2 * n_hi <= d
    early_none = (lower is not None and n_hi < lower) or 2 * n_lo > d
    out.update(state="ok", n_lo=n_lo, n_hi=n_hi, precision=pi["precision"],
               early=_verdict(early_all, early_none),
               late=_verdict(n_lo > d, n_hi <= d))
    return out


def pct(n, d):
    return None if n is None or not d else round(100.0 * n / d, 2)


# ------------------------------------------------------------------ validation
def _issue(code, severity, text, role=None):
    i = {"code": code, "severity": severity, "text": text}
    if role:
        i["role"] = role
    return i


def _doc_files_ok(doc):
    files = doc.get("files") or []
    hashed = [f for f in files if f.get("sha256")]
    return files, hashed


def validate(study):
    """Validate a study. Returns {pairs: {pair_id: {...}}, cohort: [...], counts, freezable}.

    severity 'hard' = the pair is rejected as it stands (wrong timing, reuse, contradiction);
    severity 'pending' = evidence is missing or unverified. A pair is 'verified' only when it
    has neither.
    """
    proto = study.get("protocol") or {}
    pre = (proto.get("pre_start_policy") or {}).get("value", "exclude")
    docs = study.get("documents") or {}
    pairs = study.get("pairs") or []

    grant_slots, doc_slots, hash_slots = {}, {}, {}
    for p in pairs:
        g = (p.get("project") or {}).get("grant")
        if g:
            grant_slots.setdefault(str(g), []).append(p.get("pair_id"))
        for role in ("early", "late"):
            did = p.get(role)
            if did:
                doc_slots.setdefault(did, []).append("%s/%s" % (p.get("pair_id"), role))
                for f in (docs.get(did) or {}).get("files") or []:
                    if f.get("sha256"):
                        hash_slots.setdefault(f["sha256"], set()).add(did)

    res, n_verified, distinct, negative_n = {}, 0, set(), False
    for p in pairs:
        issues, tim = [], {}
        proj = p.get("project")
        disc = p.get("discipline")
        if not proj or not proj.get("grant"):
            issues.append(_issue("no_project", "pending", "no project assigned"))
        else:
            g = str(proj["grant"])
            if len(grant_slots.get(g, [])) > 1:
                issues.append(_issue("project_reused", "hard",
                                     "project %s also fills %s" % (
                                         g, ", ".join(x for x in grant_slots[g] if x != p.get("pair_id")))))
            cordis = p.get("cordis") or {}
            branches = cordis.get("branches") or []
            if not branches:
                issues.append(_issue("discipline_source_missing", "pending",
                                     "no documented CORDIS branch membership recorded"))
            elif disc not in branches:
                issues.append(_issue("discipline_unsupported", "hard",
                                     "%s is not among the project's CORDIS branches (%s)" % (
                                         disc, ", ".join(branches))))
            if not proj.get("start") or not proj.get("end"):
                issues.append(_issue("project_dates_missing", "pending", "project start/end missing"))
        if not (p.get("scope") or "").strip():
            issues.append(_issue("scope_missing", "pending", "same-scope descriptor not recorded"))

        early, late = p.get("early"), p.get("late")
        if early and late and early == late:
            issues.append(_issue("same_document_both_roles", "hard",
                                 "the same document fills both roles"))
        scopes = set()
        for role in ("early", "late"):
            did = p.get(role)
            if not did:
                issues.append(_issue("no_" + role, "pending", "%s slot empty" % role, role))
                continue
            distinct.add(did)
            doc = docs.get(did)
            if doc is None:
                issues.append(_issue("document_missing", "hard",
                                     "%s document %s is not in the study" % (role, did), role))
                continue
            if len(doc_slots.get(did, [])) > 1:
                issues.append(_issue("document_reused", "hard",
                                     "%s document also used in %s" % (role, ", ".join(
                                         x for x in doc_slots[did] if x != "%s/%s" % (p.get("pair_id"), role))),
                                     role))
            if proj and proj.get("grant") and doc.get("grant") and str(doc["grant"]) != str(proj["grant"]):
                issues.append(_issue("grant_mismatch", "hard",
                                     "%s document belongs to grant %s, pair is %s" % (
                                         role, doc["grant"], proj["grant"]), role))
            if (doc.get("scope") or "").strip():
                scopes.add(doc["scope"].strip().lower())
            iss = doc.get("issue_date") or {}
            st = iss.get("state") or "not_checked"
            t = timing(iss.get("value"), (proj or {}).get("start"), (proj or {}).get("end"), pre)
            tim[role] = t
            if t["state"] == "ok" and t["n_lo"] is not None and t["n_lo"] < 0:
                negative_n = True
            if not iss.get("value"):
                issues.append(_issue("issue_date_missing", "pending",
                                     "%s document has no documented issue date" % role, role))
            elif t["state"] == "invalid":
                issues.append(_issue("timing_invalid", "hard", "%s timing: %s" % (role, t["reason"]), role))
            elif t["state"] == "unknown":
                issues.append(_issue("timing_unknown", "pending", "%s timing: %s" % (role, t["reason"]), role))
            else:
                verdict = t[role]
                if verdict == "no":
                    rule = "<= 50%" if role == "early" else "> 100%"
                    issues.append(_issue("timing_fail", "hard",
                                         "%s document is at %s, outside %s" % (
                                             role, _fmt_pct(t), rule), role))
                elif verdict == "indeterminate":
                    issues.append(_issue("timing_indeterminate", "pending",
                                         "%s date precision (%s) straddles the threshold" % (
                                             role, t["precision"]), role))
                for alt in doc.get("alt_dates") or []:
                    ta = timing(alt.get("value"), proj.get("start"), proj.get("end"), pre)
                    if ta["state"] == "ok" and ta[role] != verdict:
                        issues.append(_issue("alt_date_conflict", "pending",
                                             "%s alternative date %s (%s) gives a different verdict" % (
                                                 role, alt.get("value"), alt.get("label") or "unlabelled"),
                                             role))
                        break
            if iss.get("value") and not (iss.get("locator") or "").strip():
                issues.append(_issue("issue_date_no_locator", "pending",
                                     "%s issue date has no page/section locator" % role, role))
            if st in ("contradictory", "unavailable"):
                issues.append(_issue("issue_date_" + st, "hard", "%s issue date marked %s" % (role, st), role))
            elif iss.get("value") and st != "verified":
                issues.append(_issue("issue_date_unverified", "pending",
                                     "%s issue date not verified by a person" % role, role))
            files, hashed = _doc_files_ok(doc)
            if not hashed:
                issues.append(_issue("files_missing", "pending",
                                     "%s document has no selected file with a checksum" % role, role))
            else:
                if len(files) > 1 and not any(f.get("analysis") for f in files):
                    issues.append(_issue("representation_unchosen", "pending",
                                         "%s document has several files and no analysis file chosen" % role,
                                         role))
                for f in hashed:
                    if len(hash_slots.get(f["sha256"], ())) > 1:
                        issues.append(_issue("repeated_bytes", "hard",
                                             "%s file %s has the same bytes as another study document" % (
                                                 role, f.get("name") or ""), role))
                        break
                for f in files:
                    if f.get("access") in ("failed", "unavailable", "contradictory"):
                        issues.append(_issue("file_unavailable", "hard",
                                             "%s file %s could not be retrieved or does not match its checksum" % (
                                                 role, f.get("name") or ""), role))
        if len(scopes) > 1:
            issues.append(_issue("scope_mismatch", "hard",
                                 "the two documents record different scopes: " + " / ".join(sorted(scopes))))
        lin = p.get("lineage") or {}
        lst = lin.get("state") or "not_checked"
        if lst in ("contradictory", "unavailable"):
            issues.append(_issue("lineage_" + lst, "hard", "lineage evidence marked " + lst))
        elif early and late and lst != "verified":
            issues.append(_issue("lineage_unverified", "pending",
                                 "no person has verified that the later document revises the earlier one"))
        elif lst == "verified" and not (lin.get("evidence") or []):
            issues.append(_issue("lineage_no_evidence", "pending", "lineage marked verified without evidence"))

        hard = [i for i in issues if i["severity"] == "hard"]
        empty = not proj and not early and not late
        status = "empty" if empty else ("rejected" if hard else ("pending" if issues else "verified"))
        if status == "verified":
            n_verified += 1
        res[p.get("pair_id")] = {
            "status": status, "issues": issues,
            "timing": {r: dict(t, pct_lo=pct(t["n_lo"], t["d"]), pct_hi=pct(t["n_hi"], t["d"]))
                       for r, t in tim.items()},
        }

    cohort = []
    if [p.get("discipline") for p in pairs] != DISCIPLINES:
        cohort.append(_issue("disciplines", "hard", "the study must have exactly the six fixed discipline rows"))
    if n_verified < 6:
        cohort.append(_issue("incomplete", "pending", "%d of 6 pairs verified" % n_verified))
    if not proto.get("approved"):
        cohort.append(_issue("protocol_unapproved", "pending", "protocol not approved"))
    for dcn in proto.get("open_decisions") or []:
        if dcn.get("status") == "open":
            cohort.append(_issue("decision_open", "pending", "open decision: " + dcn.get("id", "?")))
    if negative_n and (proto.get("pre_start_policy") or {}).get("status") != "confirmed":
        cohort.append(_issue("pre_start_unsettled", "pending",
                             "a document predates its project start and the pre-start policy is not confirmed"))
    return {"pairs": res, "cohort": cohort,
            "counts": {"verified_pairs": n_verified, "distinct_documents": len(distinct)},
            "freezable": not cohort and n_verified == 6}


def _fmt_pct(t):
    lo, hi = pct(t["n_lo"], t["d"]), pct(t["n_hi"], t["d"])
    return ("%.2f%%" % lo) if lo == hi else ("%.2f%%-%.2f%%" % (lo, hi))


# ------------------------------------------------------------------ exports
EXPORT_COLS = ["pair_id", "discipline", "grant", "acronym", "status",
               "early_document", "early_issue_date", "early_position", "early_link",
               "late_document", "late_issue_date", "late_position", "late_link",
               "lineage", "missing_or_failing"]


def _doc_link(doc):
    if not doc:
        return ""
    if doc.get("doi"):
        return "https://doi.org/" + doc["doi"]
    if doc.get("record_url"):
        return doc["record_url"]
    for f in doc.get("files") or []:
        if f.get("url"):
            return f["url"]
    return ""


def export_rows(study, v=None):
    v = v or validate(study)
    docs = study.get("documents") or {}
    out = []
    for p in study.get("pairs") or []:
        r = v["pairs"].get(p.get("pair_id"), {})
        proj = p.get("project") or {}
        row = {"pair_id": p.get("pair_id"), "discipline": p.get("discipline"),
               "grant": proj.get("grant") or "", "acronym": proj.get("acronym") or "",
               "status": r.get("status", ""), "lineage": (p.get("lineage") or {}).get("state", "")}
        for role in ("early", "late"):
            doc = docs.get(p.get(role) or "") if p.get(role) else None
            t = (r.get("timing") or {}).get(role)
            row[role + "_document"] = p.get(role) or ""
            row[role + "_issue_date"] = ((doc or {}).get("issue_date") or {}).get("value") or ""
            row[role + "_position"] = _fmt_pct(t) if t and t.get("state") == "ok" else ""
            row[role + "_link"] = _doc_link(doc)
        row["missing_or_failing"] = "; ".join(i["text"] for i in r.get("issues") or [])
        out.append(row)
    return out


def to_csv(rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(EXPORT_COLS)
    for r in rows:
        w.writerow([r.get(c, "") for c in EXPORT_COLS])
    return buf.getvalue()


def md_cell(v):
    return re.sub(r"\r?\n", " ", str(v if v is not None else "")).replace("\\", "\\\\").replace("|", "\\|")


def to_md(rows):
    lines = ["| " + " | ".join(EXPORT_COLS) + " |", "|" + "|".join("---" for _ in EXPORT_COLS) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(md_cell(r.get(c, "")) for c in EXPORT_COLS) + " |")
    return "\n".join(lines) + "\n"


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1) + "\n"


# ------------------------------------------------------------------ files
def resolve_local(path, root=None):
    """Resolve a repo-relative local path, refusing anything that escapes the root."""
    root = os.path.abspath(root or common.ROOT)
    if not path:
        return None
    full = os.path.abspath(os.path.join(root, path))
    if os.path.commonpath([full, root]) != root:
        return None
    return full


def file_facts(study, root=None):
    """Hash every selected file that exists locally. Never downloads."""
    facts = {}
    for did, doc in sorted((study.get("documents") or {}).items()):
        for i, f in enumerate(doc.get("files") or []):
            full = resolve_local(f.get("local_path"), root)
            fact = {"doc_id": did, "index": i, "local_path": f.get("local_path"), "present": False}
            if full and os.path.isfile(full):
                fact.update(present=True, bytes=os.path.getsize(full), sha256=sha256_file(full))
            facts["%s#%d" % (did, i)] = fact
    return facts


CORPUS_DIR = os.path.join("data", "paired-dmp-corpus")


def _safe(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s or "")[:90]


def download_file(url, dest, timeout=120):
    """Fetch one file to dest atomically. Returns facts; checks file-level availability
    rather than trusting the repository record's access label."""
    fact = {"url": url, "retrieved": now_iso()}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": common.HEADERS["User-Agent"]})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            fact["http_status"] = r.status
            data = r.read()
    except Exception as e:
        fact.update(access="failed", error=str(e)[:300])
        return fact
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, dest)
    fact.update(access="verified", bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    return fact


def download_missing(study, facts, root=None):
    """Download selected files that are not on disk yet, into data/paired-dmp-corpus/ only."""
    root = os.path.abspath(root or common.ROOT)
    corpus = os.path.join(root, CORPUS_DIR)
    for did, doc in sorted((study.get("documents") or {}).items()):
        for i, f in enumerate(doc.get("files") or []):
            key = "%s#%d" % (did, i)
            if facts.get(key, {}).get("present") or not f.get("url"):
                continue
            rel = f.get("local_path") or os.path.join(
                CORPUS_DIR, _safe(doc.get("grant") or "unassigned"), _safe(did) + "__" + _safe(f.get("name")))
            full = resolve_local(rel, root)
            if not full or os.path.commonpath([full, corpus]) != corpus:
                facts[key] = dict(facts.get(key, {}), error="refused: downloads only go to " + CORPUS_DIR)
                continue
            fact = download_file(f["url"], full)
            fact.update(doc_id=did, index=i, local_path=os.path.relpath(full, root).replace(os.sep, "/"),
                        present=fact.get("access") == "verified")
            facts[key] = fact
    return facts


# ------------------------------------------------------------------ freeze
def source_hashes(state_dir=None):
    return {
        "data/dmp_dataset.json": sha256_or_none(DATASET),
        "data/study-documents.json": sha256_or_none(REGISTRY),
        "research/paired-dmp-study/cohort-proposal.json": sha256_or_none(PROPOSAL),
    }


def freeze(study, state_dir=None, root=None):
    """Write an immutable snapshot, or return the reasons it cannot be frozen.

    Returns (ok, result). On success result has snapshot_id and path. A snapshot is never
    rewritten: the file is created with O_EXCL and a later edit has to make a new one.
    """
    reason = check_study(study)
    if reason:
        return False, {"reasons": [reason]}
    v = validate(study)
    reasons = [i["text"] for i in v["cohort"] if i["code"] != "incomplete"]
    for pid, r in sorted(v["pairs"].items()):
        if r["status"] != "verified":
            reasons.append("%s: %s" % (pid, "; ".join(i["text"] for i in r["issues"]) or r["status"]))
    manifest = []
    for p in study["pairs"]:
        for role in ("early", "late"):
            did = p.get(role)
            doc = (study["documents"].get(did) or {}) if did else {}
            for f in doc.get("files") or []:
                if not f.get("sha256"):
                    continue
                full = resolve_local(f.get("local_path"), root)
                entry = {"pair_id": p["pair_id"], "role": role, "doc_id": did, "name": f.get("name"),
                         "url": f.get("url"), "local_path": f.get("local_path"),
                         "recorded_sha256": f["sha256"], "repository_checksum": f.get("repo_checksum"),
                         "analysis": bool(f.get("analysis")) or len(doc.get("files") or []) == 1}
                if not full or not os.path.isfile(full):
                    reasons.append("%s/%s: file %s is not on disk at %s" % (
                        p["pair_id"], role, f.get("name"), f.get("local_path")))
                else:
                    got = sha256_file(full)
                    entry.update(local_sha256=got, bytes=os.path.getsize(full))
                    if got != f["sha256"]:
                        reasons.append("%s/%s: file %s bytes differ from the recorded checksum" % (
                            p["pair_id"], role, f.get("name")))
                manifest.append(entry)
    if reasons:
        return False, {"reasons": reasons, "validation": v}

    frozen_at = now_iso()
    body = {
        "schema": SNAPSHOT_SCHEMA, "schema_version": 1,
        "frozen_at": frozen_at,
        "study": copy.deepcopy(study),
        "validation": v,
        "file_manifest": manifest,
        "source_hashes": source_hashes(),
        "note": "Immutable. Edit the draft and freeze again to make a new snapshot. Source files are "
                "referenced by repo-relative path and checksum, not included.",
    }
    body["study"]["status"] = "frozen"
    digest = hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()
    sid = "paired-%s-%s" % (frozen_at.replace(":", "").replace("-", "")[:15], digest[:10])
    body["snapshot_id"] = sid
    body["content_sha256"] = digest
    out_dir = os.path.join(state_dir or common.DATA, SNAPSHOT_DIR)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, sid + ".json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(canonical(body))
    rows = export_rows(body["study"], v)
    for ext, text in (("csv", to_csv(rows)), ("md", to_md(rows))):
        fd = os.open(os.path.join(out_dir, sid + "." + ext), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
    return True, {"snapshot_id": sid, "path": path, "content_sha256": digest}


def verify_snapshot(path):
    """Recompute a snapshot's content hash. True when it still matches."""
    body = json.load(open(path, encoding="utf-8"))
    claimed = body.pop("content_sha256", None)
    body.pop("snapshot_id", None)
    return claimed == hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ persistence
def read_study(path):
    """(study, error). error is set, and study None, for corrupt or unsupported files."""
    if not os.path.exists(path):
        return None, None
    raw = open(path, "rb").read()
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception as e:
        return None, "the study file is not valid JSON (%s); its bytes are untouched" % e
    reason = check_study(obj)
    if reason:
        return None, reason + "; the file is untouched"
    return obj, None


def write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


# ------------------------------------------------------------------ registry
def load_registry():
    if not os.path.exists(REGISTRY):
        return {"schema": REGISTRY_SCHEMA, "schema_version": 1, "documents": []}
    return json.load(open(REGISTRY, encoding="utf-8"))


def registry_rows(registry=None):
    """Registry documents shaped like dataset rows, so the candidate table can show them."""
    reg = registry or load_registry()
    out = []
    for d in reg.get("documents") or []:
        files = d.get("files") or []
        out.append({
            "id": d["doc_id"], "src": "registry", "doi": d.get("doi"), "title": d.get("title") or d["doc_id"],
            "date": d.get("publication_date"), "year": (d.get("publication_date") or "")[:4] or None,
            "tier": d.get("tier") or "Other EU", "program": d.get("programme"), "grant": d.get("grant"),
            "acronym": d.get("acronym"), "proj_title": d.get("project_title") or "",
            "proj_start": d.get("project_start"), "proj_end": d.get("project_end"),
            "disc": None, "disc_all": d.get("cordis_branches") or [], "fields": [],
            "stage": "unknown", "stage_frac": None, "stage_src": None, "version": d.get("version_label"),
            "madmp": False, "kind": "dmp", "kind_why": "registered study document (not harvested)",
            "url": d.get("record_url") or (files[0].get("url") if files else None),
            "files": [{"name": f.get("name"), "ext": (f.get("format") or "").lower(), "size": f.get("bytes")}
                      for f in files],
            "n_pdf": sum(1 for f in files if (f.get("format") or "").lower() == "pdf"), "n_json": 0,
            "access": "public", "type": "registry", "creators": d.get("creators") or [],
            "funders": [], "desc": d.get("description") or "", "subjects": [],
            "registry": d,
        })
    return out


# ------------------------------------------------------------------ proposal import
EXPLICIT_DATE = re.compile(r"\b(issue[- ]date|submission date|delivery date)\b", re.I)
COVER_DATE = re.compile(r"\bcover\b", re.I)
HISTORY_DATE = re.compile(r"\b(revision|version history|document log)\b", re.I)


def date_rank(label):
    """D16: explicit issue/submission/delivery label (0) > dated cover (1) > revision-history
    row (2) > anything else (3). Ties keep the order the source listed them in."""
    label = label or ""
    if EXPLICIT_DATE.search(label):
        return 0
    if COVER_DATE.search(label):
        return 1
    if HISTORY_DATE.search(label):
        return 2
    return 3


def _proposal_doc(pair, role):
    src = pair[role]
    bib = src.get("bibliographic_snapshot") or {}
    rid = src.get("record_id")
    did = "zenodo:%s" % rid if rid else src.get("document_id")
    dates = src.get("document_dates") or []
    chosen = min(dates, key=lambda x: date_rank(x.get("label"))) if dates else None
    alts = [{"value": x["date"], "label": x.get("label") or "",
             "locator": "physical PDF p%s" % x["physical_pdf_page"] if x.get("physical_pdf_page") else ""}
            for x in dates if x is not chosen]
    for x in src.get("other_date_fields") or []:
        alts.append({"value": x["date"], "label": x.get("label") or "", "locator": ""})
    name = src.get("source_filename") or ((bib.get("files") or [{}])[0].get("name")) or \
        os.path.basename(src.get("local_pdf") or "")
    return did, {
        "doc_id": did, "source": "cohort-proposal", "record_id": rid, "record_url": src.get("record_url"),
        "doi": bib.get("doi"), "concept_id": None,
        "version_label": src.get("document_version") or "",
        "title": src.get("title") or bib.get("title") or did, "grant": pair["grant"], "scope": "",
        "publication_date": bib.get("publication_date") or src.get("metadata_publication_date"),
        "issue_date": {
            "value": chosen["date"] if chosen else None,
            "label": (chosen or {}).get("label") or "",
            "locator": ("physical PDF p%s" % chosen["physical_pdf_page"]) if chosen and chosen.get(
                "physical_pdf_page") else "",
            "source_url": src.get("source_file_url") or src.get("record_url") or "",
            "state": "not_checked", "verified_by": "", "verified_on": "",
            "chosen_by": "D16 hierarchy, rank %d of the labelled dates" % date_rank((chosen or {}).get("label")),
        },
        "alt_dates": alts,
        "files": [{
            "name": name, "url": src.get("source_file_url"), "format": "pdf", "bytes": src.get("bytes"),
            "sha256": src.get("sha256"), "repo_checksum": ("md5:" + src["md5"]) if src.get("md5") else None,
            "retrieved": src.get("retrieved_date"), "local_path": src.get("local_pdf"),
            "licence": src.get("metadata_license_id") or "", "access": "not_checked", "analysis": True,
        }],
        "prior_checks": [{"by": "agent check, research/paired-dmp-study/pair-review.json",
                          "result": "document dates read from the PDF", "date": "2026-11-04"}],
    }


def proposal_to_study(proposal=None):
    """The 2026-11-04 cohort proposal as a draft. Nothing in it is marked verified."""
    prop = proposal or json.load(open(PROPOSAL, encoding="utf-8"))
    st = new_study(origin="imported from research/paired-dmp-study/cohort-proposal.json (%s); "
                          "agent-checked, not yet verified by a person" % prop.get("proposal_id"))
    by_disc = {p["proposed_slot"]: p for p in prop["pairs"]}
    for pair in st["pairs"]:
        src = by_disc.get(pair["discipline"])
        if not src:
            continue
        cls = src.get("current_classification") or {}
        ext = src.get("extension_sensitivity") or {}
        ev = src.get("end_evidence") or {}
        pair["project"] = {
            "grant": src["grant"], "acronym": src["project"], "title": "",
            "programme": (src["early"].get("bibliographic_snapshot") or {}).get("funding_tier") or "",
            "start": src["project_start"], "end": src["latest_authoritative_end"],
            "end_basis": "latest authoritative CORDIS end including extensions (D09)",
            "original_end": ext.get("original_end_printed_in_both_PDFs") or ext.get("inferred_original_end"),
            "end_source": {"url": ev.get("url"), "sha256": ev.get("sha256"), "local_path": ev.get("local_path"),
                           "retrieved": ev.get("retrieved_date") or "2026-11-03"},
            "extension_note": src.get("historical_extensions_status") or "",
        }
        pair["cordis"] = {
            "branches": src.get("live_CORDIS_branches") or [],
            "paths": cls.get("paths") or src.get("classification_paths_current") or [],
            "dominant": cls.get("dominant_branches") or [],
            "local_dominant": src.get("local_dominant_branch"),
            "source": ev.get("url") or "", "retrieved": ev.get("retrieved_date") or "2026-11-03",
        }
        pair["scope"] = ""
        pair["lineage"] = {
            "state": "not_checked", "verified_by": "", "verified_on": "",
            "evidence": [{"locator": "pair-review.json", "note": src.get("lineage_evidence") or ""}],
            "prior_checks": [{"by": "agent check, research/paired-dmp-study/pair-review.json",
                              "result": src.get("lineage_check"), "date": "2026-11-04"}],
        }
        pair["notes"] = "; ".join(src.get("uncertainties") or [])
        for role in ("early", "late"):
            did, doc = _proposal_doc(src, role)
            st["documents"][did] = doc
            pair[role] = did
    return st


def seed_registry():
    """Registry entries for the three proposal documents with no row in the dataset."""
    prop = json.load(open(PROPOSAL, encoding="utf-8"))
    ids = {r["id"] for r in common.load_dataset()}
    docs = []
    for pair in prop["pairs"]:
        for role in ("early", "late"):
            src = pair[role]
            rid = src.get("record_id")
            if rid and rid in ids:
                continue
            did, doc = _proposal_doc(pair, role)
            bib = src.get("bibliographic_snapshot") or {}
            docs.append({
                "doc_id": did, "record_id": rid, "record_url": src.get("record_url"), "doi": doc["doi"],
                "title": doc["title"], "version_label": doc["version_label"], "grant": pair["grant"],
                "acronym": pair["project"],
                "tier": "Horizon Europe" if (bib.get("funding_tier") == "Horizon Europe" or
                                             str(pair["grant"]).startswith("101")) else "Horizon 2020",
                "project_start": pair["project_start"], "project_end": pair["latest_authoritative_end"],
                "cordis_branches": pair.get("live_CORDIS_branches") or [],
                "publication_date": doc["publication_date"], "creators": bib.get("creators") or [],
                "files": [{k: f[k] for k in ("name", "url", "format", "bytes", "sha256", "local_path")}
                          for f in doc["files"]],
                "provenance": {
                    "found_via": "cohort proposal 2026-11-04 (%s)" % (
                        "Zenodo version chain of concept %s" % (pair.get("repository_version_list") or {}).get(
                            "concept") if rid else "project website"),
                    "source_url": doc["files"][0]["url"], "registered": "2026-11-04",
                    "registered_by": "scripts/paired.py seed-registry",
                    "note": "absent from data/dmp_dataset.json; no Zenodo id is invented" if not rid else
                            "Zenodo record absent from the saved harvest",
                },
            })
    reg = {"schema": REGISTRY_SCHEMA, "schema_version": 1,
           "note": "Study documents that are not rows of data/dmp_dataset.json. Metadata and checksums "
                   "only; source files keep their own terms and are not stored in git.",
           "documents": sorted(docs, key=lambda d: d["doc_id"])}
    write_atomic(REGISTRY, canonical(reg))
    return reg


# ------------------------------------------------------------------ legacy
def legacy_historical(selection_path, known_ids):
    """Read the legacy selection as historical material. All ids survive, resolved or not."""
    raw = open(selection_path, "rb").read()
    d = json.loads(raw.decode("utf-8"))
    ids = [str(i) for i in (d.get("ids") or [])]
    return {
        "source": os.path.relpath(selection_path, common.ROOT),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "label": "historical, unverified; confers no eligibility or selection priority",
        "imported_at": now_iso(), "ids": ids,
        "unresolved": [i for i in ids if i not in known_ids],
    }


# ------------------------------------------------------------------ cli
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["validate", "proposal", "export", "freeze", "seed-registry", "verify-snapshot"])
    ap.add_argument("--study", default=os.path.join(common.DATA, STUDY_FILE))
    ap.add_argument("--state-dir", default=common.DATA)
    ap.add_argument("--format", default="md", choices=["md", "csv", "json"])
    ap.add_argument("--snapshot")
    a = ap.parse_args()

    if a.cmd == "proposal":
        sys.stdout.write(canonical(proposal_to_study()))
        return
    if a.cmd == "seed-registry":
        reg = seed_registry()
        print("wrote %s (%d documents)" % (REGISTRY, len(reg["documents"])))
        return
    if a.cmd == "verify-snapshot":
        ok = verify_snapshot(a.snapshot)
        print("snapshot content hash %s" % ("matches" if ok else "DOES NOT MATCH"))
        sys.exit(0 if ok else 1)
    study, err = read_study(a.study)
    if err or study is None:
        raise SystemExit(err or "no study at %s" % a.study)
    if a.cmd == "validate":
        v = validate(study)
        for p in study["pairs"]:
            r = v["pairs"][p["pair_id"]]
            print("%-28s %-9s %s" % (p["discipline"], r["status"],
                                     "; ".join(i["text"] for i in r["issues"])))
        for i in v["cohort"]:
            print("cohort: " + i["text"])
        print("verified pairs %d/6, distinct documents %d/12, freezable %s" % (
            v["counts"]["verified_pairs"], v["counts"]["distinct_documents"], v["freezable"]))
    elif a.cmd == "export":
        if a.format == "json":
            sys.stdout.write(canonical({"study": study, "validation": validate(study)}))
        else:
            rows = export_rows(study)
            sys.stdout.write(to_csv(rows) if a.format == "csv" else to_md(rows))
    elif a.cmd == "freeze":
        ok, res = freeze(study, a.state_dir)
        if not ok:
            print("not frozen:")
            for r in res["reasons"]:
                print("  - " + r)
            sys.exit(1)
        print("frozen: %s" % res["path"])


if __name__ == "__main__":
    main()
