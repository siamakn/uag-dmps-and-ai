#!/usr/bin/env python3
"""Write verification-checklist.md: what a person must read to verify the six proposal pairs.

For every document it lists the chosen issue date (D16 hierarchy), the other labelled dates,
and the lines of extracted text on the cited physical page that mention that year, so the
reader knows what to look for. The extracted text is a finding aid only: the verifier reads
the PDF page itself. Nothing here marks anything verified. No network access; reads the
local corpus and the proposal.

    python3 research/paired-dmp-study/verification-checklist.py
"""
import datetime
import json
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import paired  # noqa: E402

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def page_text(pdf_rel, page):
    txt = ROOT / re.sub(r"\.pdf$", ".txt", pdf_rel)
    if not txt.exists() or not page:
        return None
    pages = txt.read_text(encoding="utf-8", errors="replace").split("\f")
    return pages[page - 1] if 0 < page <= len(pages) else None


def hits(text, iso):
    """Lines on the page that look like they carry this date (any common notation)."""
    if not text or not iso:
        return []
    y, m, d = iso[:4], int(iso[5:7]), int(iso[8:10])
    pats = [iso, "%02d/%02d/%s" % (d, m, y), "%d/%d/%s" % (d, m, y), "%02d.%02d.%s" % (d, m, y),
            "%02d-%02d-%s" % (d, m, y)]
    out = []
    for line in text.splitlines():
        low = line.lower()
        if y not in line:
            continue
        if any(p in line for p in pats) or (str(d) in line and MONTHS[m - 1] in low):
            out.append(re.sub(r"\s{2,}", "  ", line.strip())[:160])
    return out[:3]


def main():
    prop = json.loads((BASE / "cohort-proposal.json").read_text(encoding="utf-8"))
    study = paired.proposal_to_study(prop)
    v = paired.validate(study)
    by_slot = {p["proposed_slot"]: p for p in prop["pairs"]}
    L = [
        "# Verification checklist — six proposal pairs",
        "",
        "Generated %s by `verification-checklist.py` from `cohort-proposal.json` and the local "
        "corpus. **Nothing here is verified.** A pair becomes *verified* in the dashboard only when "
        "a person has done the steps below and recorded them." % datetime.date.today().isoformat(),
        "",
        "## How to use it",
        "",
        "1. Start the dashboard: `python scripts/serve.py`. Choose *Paired study* and press "
        "**Load proposal** (once; it replaces an empty draft).",
        "2. For each pair, open the PDFs listed below at the given physical pages (the page count of "
        "the PDF file, not the printed page number).",
        "3. In the pair's **Evidence** editor:",
        "   - **Same-scope descriptor**: what both documents cover, e.g. `project-wide DMP, whole "
        "consortium`. Enter the same text in each document's *Document scope* only if the document "
        "states it.",
        "   - **Issue date** for each document: confirm the value at the locator. Under D16 an "
        "explicitly labelled issue / submission / delivery date wins, then a dated cover, then the "
        "version's revision-history row. If the PDF shows something else, correct the value and "
        "locator. Then set *Issue-date state* to `verified` and enter your name.",
        "   - **Lineage**: confirm that the later document revises or succeeds the earlier one (revision "
        "table, 'updates D1.2', same deliverable series). Add an evidence entry (locator + one-line "
        "note), set *Lineage state* to `verified`, enter your name.",
        "   - If something contradicts the proposal, set the state to `contradictory` and say why in "
        "*Notes*. The pair turns *rejected*; that is a valid outcome.",
        "4. Press **Check files** (re-hashes the 12 PDFs on disk).",
        "5. When all six pairs show *verified*, press **Freeze** (served mode only). The selection "
        "protocol is already approved (D20, 2026-11-09), so verified pairs are the only remaining "
        "requirement.",
        "",
        "The quoted lines come from automatic text extraction and can be garbled or in a different "
        "order from the page. They only help you find the date; the PDF page is the evidence.",
        "",
    ]
    for pair in study["pairs"]:
        src = by_slot[pair["discipline"]]
        proj = pair["project"]
        res = v["pairs"][pair["pair_id"]]
        L += ["## %s — %s (grant %s)" % (pair["discipline"], proj["acronym"], proj["grant"]), ""]
        L.append("- Project run (latest authoritative end, D09): **%s → %s** (%d days). End source: %s"
                 % (proj["start"], proj["end"], src["duration_days"], proj["end_source"]["url"]))
        if proj.get("original_end"):
            L.append("- Original end printed or inferred: %s (sensitivity only)." % proj["original_end"])
        L.append("- CORDIS branches: %s; dominant: %s." % (
            ", ".join(pair["cordis"]["branches"]), " = ".join(pair["cordis"]["dominant"]) or "n/a"))
        L.append("- Claim to check (agent review, `pair-review.json`): *%s*" % src["lineage_evidence"])
        if src.get("licence_evidence"):
            L.append("- Rights note: %s" % src["licence_evidence"])
        L.append("")
        for role in ("early", "late"):
            doc = study["documents"][pair[role]]
            t = res["timing"][role]
            f = doc["files"][0]
            iss = doc["issue_date"]
            L.append("### %s · `%s` · %s" % (role, doc["doc_id"], doc["title"]))
            L.append("")
            L.append("- PDF: `%s` (%s bytes, sha256 `%s…`)" % (f["local_path"], f["bytes"], f["sha256"][:16]))
            if doc.get("record_url"):
                L.append("- Record: %s" % doc["record_url"])
            L.append("- Chosen issue date: **%s** — %s — %s → **%s** of the run (rule: %s)" % (
                iss["value"], iss["label"], iss["locator"] or "no locator",
                paired._fmt_pct(t), "early ≤ 50%" if role == "early" else "late > 100%"))
            page = int(re.search(r"\d+", iss["locator"]).group()) if re.search(r"\d+", iss["locator"] or "") else None
            for line in hits(page_text(f["local_path"], page), iss["value"]):
                L.append("  - text on that page: `%s`" % line.replace("`", "'"))
            for alt in doc.get("alt_dates") or []:
                ta = paired.timing(alt["value"], proj["start"], proj["end"])
                L.append("- Other labelled date: %s — %s%s → %s (%s)" % (
                    alt["value"], alt["label"], " — " + alt["locator"] if alt.get("locator") else "",
                    paired._fmt_pct(ta), "same verdict" if ta[role] == t[role] else "**would change the verdict**"))
            L.append("- Repository publication date (not used): %s" % (doc.get("publication_date") or "none"))
            L.append("- [ ] issue date confirmed at the page   - [ ] scope noted")
            L.append("")
        L.append("- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run")
        unc = src.get("uncertainties") or []
        if unc:
            L.append("")
            L.append("Known uncertainties from the proposal:")
            L += ["- %s" % u for u in unc]
        L.append("")
    out = BASE / "verification-checklist.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
