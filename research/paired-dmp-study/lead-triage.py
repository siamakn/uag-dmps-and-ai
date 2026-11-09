#!/usr/bin/env python3
"""Triage the Zenodo version-chain leads into a reserve shortlist (no selection, no registration).

Input: data/paired-discovery/versions.json and its cache (scripts/06_discover_versions.py),
plus data/dmp_dataset.json for each project's CORDIS branches and dates.
Output: lead-shortlist.json and lead-shortlist.md next to this file.

The screen uses repository publication dates only, and only in the direction that is
logically safe, assuming a document is issued no later than it is deposited:
  - a version deposited at or before the project end cannot have been issued after it, so a
    late (>100%) document needs a version deposited after the end (necessary, not sufficient);
  - a version deposited at or before 50% was issued at or before 50% (pre-start aside), so it
    is an early candidate; a version deposited later may still have been issued early.
A concept can therefore yield a pair only if it has 2+ versions and at least one deposited
after the project end. Those are kept, in three tiers:
  A  an early-by-deposit version and a post-end version: the late issue date must be checked
  B  a version deposited between 50% and 100% and a post-end version: both issue dates
  D  only post-end versions: both issue dates (the proposal's RECHARGE pair looks like this)
Same concept is a stronger lineage lead than same grant, but it is still only a lead. Project
ends are the local CORDIS bulk dates; D09 (latest authoritative end) is not checked here.
"""
import datetime
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
DISC = ROOT / "data" / "paired-discovery"
BRANCHES = ["natural sciences", "engineering and technology", "medical and health sciences",
            "agricultural sciences", "social sciences", "humanities"]
TIER_TEXT = {
    "A": "early by deposit date; late issue date must be checked",
    "B": "deposit between 50% and 100%, plus a post-end deposit; both issue dates must be checked",
    "D": "only post-end deposits; both issue dates must be checked",
}


def day(s):
    try:
        return datetime.date(int(s[:4]), int(s[5:7]), int(s[8:10]))
    except (TypeError, ValueError):
        return None


def main():
    rows = {r["id"]: r for r in json.loads((ROOT / "data" / "dmp_dataset.json").read_text(encoding="utf-8"))}
    versions = json.loads((DISC / "versions.json").read_text(encoding="utf-8"))
    proposal = json.loads((BASE / "cohort-proposal.json").read_text(encoding="utf-8"))
    in_proposal = {p["grant"]: p["proposed_slot"] for p in proposal["pairs"]}

    counts = {"leads": len(versions["leads"]), "no_cordis_or_dates": 0, "no_post_end_version": 0}
    keep = []
    for lead in versions["leads"]:
        row = rows[lead["in_dataset"][0]]
        s, e = day(row.get("proj_start")), day(row.get("proj_end"))
        if not row.get("disc_all") or not s or not e or (e - s).days <= 0:
            counts["no_cordis_or_dates"] += 1
            continue
        d = (e - s).days
        concept = json.loads((DISC / "cache" / ("concept-%s.json" % lead["concept"])).read_text(encoding="utf-8"))
        vers = []
        for v in concept["versions"]:
            p = day(v.get("published"))
            n = (p - s).days if p else None
            vers.append({
                "id": v["id"], "title": v.get("title"), "published": v.get("published"),
                "version_index": v.get("version_index"), "in_dataset": v["id"] in rows,
                "publication_position": None if n is None else round(100.0 * n / d, 2),
                "deposit_screen": None if n is None else ("early-by-deposit" if 0 <= 2 * n <= d else
                                                          "pre-start" if n < 0 else
                                                          "post-end" if n > d else "mid"),
                "record_url": "https://zenodo.org/records/%s" % v["id"],
                "files": [f.get("name") for f in v.get("files") or []],
            })
        vers.sort(key=lambda x: (x["published"] or "", x["id"]))
        screens = {v["deposit_screen"] for v in vers}
        if "post-end" not in screens:
            counts["no_post_end_version"] += 1
            continue
        tier = "A" if "early-by-deposit" in screens else ("B" if "mid" in screens else "D")
        keep.append({
            "tier": tier, "tier_meaning": TIER_TEXT[tier], "concept": lead["concept"],
            "grant": row.get("grant"), "acronym": row.get("acronym"), "programme": row.get("tier"),
            "cordis_branches": row.get("disc_all"), "dominant_branch": row.get("disc"),
            "project_start": row.get("proj_start"), "project_end_local_cordis": row.get("proj_end"),
            "in_cohort_proposal": in_proposal.get(row.get("grant")),
            "versions": vers,
        })
    prog = {"Horizon Europe": 0, "Horizon 2020": 1}
    keep.sort(key=lambda k: (k["tier"], prog.get(k["programme"], 2), -(int((k["versions"][-1]["published"] or "0")[:4]))))
    coverage = {b: [k["acronym"] for k in keep if b in (k["cordis_branches"] or []) and not k["in_cohort_proposal"]]
                for b in BRANCHES}
    out = {
        "generated": datetime.date.today().isoformat(),
        "inputs": {"versions.json_generated": versions.get("generated"), "scope": versions.get("scope")},
        "screen": "publication dates as a one-directional screen only (see script docstring); no issue date read",
        "counts": dict(counts, kept=len(keep), tier_A=sum(k["tier"] == "A" for k in keep),
                       tier_B=sum(k["tier"] == "B" for k in keep), tier_D=sum(k["tier"] == "D" for k in keep)),
        "reserve_coverage_by_branch_excluding_proposal_projects": coverage,
        "not_done": ["no issue dates read", "no lineage or scope checked", "no D09 end-date check",
                     "same-grant pairs across different concepts not considered here (see corpus-audit.md)",
                     "nothing registered in data/study-documents.json"],
        "shortlist": keep,
    }
    (BASE / "lead-shortlist.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    c = out["counts"]
    L = ["# Reserve shortlist from Zenodo version chains", "",
         "Generated %s by `lead-triage.py`. **A screen, not a selection.** No issue date, scope or "
         "lineage has been read, nothing is registered in the dashboard, and the six proposal pairs are "
         "unaffected." % out["generated"], "",
         "## Method", "",
         "`scripts/06_discover_versions.py versions` fetched the Zenodo version chain of every plan with a "
         "grant number (1,503 records, 0 failures). %d concepts have earlier versions missing from the saved "
         "harvest. Of these, %d belong to projects without a CORDIS discipline or project dates (D08 needs "
         "one) and %d have no version deposited after the project end. A document deposited before the end "
         "cannot have been issued after it, so those can never supply a late document. **%d concepts remain**:"
         % (c["leads"], c["no_cordis_or_dates"], c["no_post_end_version"], c["kept"]), "",
         "| tier | meaning | concepts |", "|---|---|---|"]
    for t in "ABD":
        L.append("| %s | %s | %d |" % (t, TIER_TEXT[t], c["tier_" + t]))
    L += ["", "Publication positions use the local CORDIS dates (extensions not checked, D09). Same concept "
          "means the depositor uploaded it as a new version of the same Zenodo record, which is a stronger "
          "lineage lead than a shared grant. It still needs a person to confirm that the later document "
          "revises the earlier one and has the same scope.", "",
          "## Reserve coverage by discipline (projects outside the proposal)", ""]
    for b in BRANCHES:
        L.append("- **%s**: %s" % (b, ", ".join(coverage[b]) or "none"))
    L += ["", "## Shortlist", ""]
    for k in keep:
        L.append("### Tier %s · %s (grant %s, %s)%s" % (
            k["tier"], k["acronym"], k["grant"], k["programme"],
            " — already the proposal's %s pair" % k["in_cohort_proposal"] if k["in_cohort_proposal"] else ""))
        L.append("")
        L.append("CORDIS branches: %s (dominant: %s). Project %s → %s (local CORDIS). Zenodo concept %s." % (
            ", ".join(k["cordis_branches"]), k["dominant_branch"] or "n/a", k["project_start"],
            k["project_end_local_cordis"], k["concept"]))
        L.append("")
        L.append("| record | published | position | screen | in dataset | title |")
        L.append("|---|---|---|---|---|---|")
        for v in k["versions"]:
            L.append("| [%s](%s) | %s | %s | %s | %s | %s |" % (
                v["id"], v["record_url"], v["published"] or "?",
                "" if v["publication_position"] is None else "%.2f%%" % v["publication_position"],
                v["deposit_screen"] or "?", "yes" if v["in_dataset"] else "no",
                (v["title"] or "").replace("|", "\\|")[:90]))
        L.append("")
    L += ["## To turn a lead into a candidate", "",
          "Read both issue dates. Register a missing version with "
          "`python scripts/06_discover_versions.py register --doc-id zenodo:<id> --record-id <id> ...` "
          "so it appears in the dashboard, then assign it and record the evidence there. Registering is a "
          "selection decision and has not been done for any lead."]
    (BASE / "lead-shortlist.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps(out["counts"]))
    print(json.dumps(coverage))


if __name__ == "__main__":
    main()
