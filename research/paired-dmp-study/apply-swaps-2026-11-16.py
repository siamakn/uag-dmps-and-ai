#!/usr/bin/env python3
"""Proposal v2 (2026-11-16): apply decisions D23 and D24 to cohort-proposal.json.

D23 changes "late" from "issued after the project end" to "the project's final DMP, issued
at 90% of the project run or later". D24 replaces three pairs so that each slot is the
project's main (or only) CORDIS discipline and every document has an open licence on its
repository record:
    engineering and technology   EGI-ACE   -> ColdSpark  (101069931)
    medical and health sciences  NANOFACTS -> BY-COVID   (101046203)
    agricultural sciences        AGRICORE  -> ASTEP      (884411)
iMagine, SUSTRACK and RECHARGE are unchanged.

The previous proposal is kept byte-for-byte as cohort-proposal-v1-2026-11-04.json. Source
PDFs and CORDIS snapshots are copied from data/paired-dmp-corpus/reserve-check/ (downloaded
2026-11-16) into the usual git-ignored corpus folders and hashed. Issue dates and lineage
statements were read from the PDFs by Claude and are NOT verified by a person. No network.

    python3 research/paired-dmp-study/apply-swaps-2026-11-16.py
"""
import datetime
import hashlib
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
CORPUS = ROOT / "data" / "paired-dmp-corpus"
SRC = CORPUS / "reserve-check"
PROPOSAL = BASE / "cohort-proposal.json"
V1 = BASE / "cohort-proposal-v1-2026-11-04.json"
RETRIEVED = "2026-11-16"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def day(s):
    return datetime.date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def doc(grant, start, dur, role, rid, dates, others=()):
    meta = json.loads((SRC / ("%s.json" % rid)).read_text(encoding="utf-8"))
    m = meta["metadata"]
    f = next(x for x in meta["files"] if x["key"].lower().endswith(".pdf"))
    dest = CORPUS / grant / ("%s.pdf" % rid)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC / ("%s.pdf" % rid), dest)
    shutil.copy2(SRC / ("%s.txt" % rid), dest.with_suffix(".txt"))
    snap = CORPUS / "sources" / ("zenodo-%s.json" % rid)
    shutil.copy2(SRC / ("%s.json" % rid), snap)

    def entry(date, label, page):
        n = (day(date) - day(start)).days
        ok = (0 <= 2 * n <= dur) if role == "early" else (10 * n >= 9 * dur)
        return {"date": date, "label": label, "physical_pdf_page": page, "numerator_days": n,
                "fraction": n / dur, "threshold_pass": ok}
    dd = [entry(*d) for d in dates]
    out = {
        "record_id": str(rid), "record_url": "https://zenodo.org/records/%s" % rid,
        "bytes": dest.stat().st_size, "sha256": sha(dest),
        "md5": f["checksum"].split(":")[-1], "repository_checksum_matches":
            hashlib.md5(dest.read_bytes()).hexdigest() == f["checksum"].split(":")[-1],
        "document_dates": dd, "fraction_interval": [min(x["fraction"] for x in dd), max(x["fraction"] for x in dd)],
        "local_pdf": str(dest.relative_to(ROOT)),
        "bibliographic_snapshot": {
            "title": m["title"], "doi": meta.get("doi"),
            "creators": [c["name"] for c in m.get("creators", [])][:8],
            "publication_date": m.get("publication_date"),
            "files": [{"name": f["key"], "size": f["size"], "source_file_url": f["links"]["self"]}],
            "funding_tier": "Horizon 2020" if grant == "884411" else "Horizon Europe",
            "source": "full_Zenodo_record_retrieved_%s" % RETRIEVED, "source_sha256": sha(snap),
        },
        "metadata_snapshot_local": str(snap.relative_to(ROOT)), "metadata_snapshot_sha256": sha(snap),
        "metadata_license_id": (m.get("license") or {}).get("id"),
        "source_filename": f["key"], "source_file_url": f["links"]["self"],
        "source_url_note": "content link from the retrieved Zenodo record", "retrieved_date": RETRIEVED,
    }
    if others:
        out["other_date_fields"] = []
        for date, label in others:
            n = (day(date) - day(start)).days
            out["other_date_fields"].append({"date": date, "label": label, "used_as_selected_revision_issue_date": False,
                                             "numerator_days": n, "fraction": n / dur})
    return out


def pair(project, grant, slot, start, end, paths, local_dominant, lineage, licence, uncertainties, early, late,
         extensions):
    dur = (day(end) - day(start)).days
    snap = CORPUS / "sources" / ("cordis-%s.json" % grant)
    snap.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC / ("cordis-%s.json" % grant), snap)
    counts = {}
    for p in paths:
        counts[p[0]] = counts.get(p[0], 0) + 1
    top = max(counts.values())
    return {
        "project": project, "grant": grant, "proposed_slot": slot, "local_dominant_branch": local_dominant,
        "live_CORDIS_branches": list(counts), "one_slot_only": True,
        "project_start": start, "latest_authoritative_end": end, "duration_days": dur,
        "end_evidence": {"url": "https://cordis.europa.eu/project/id/%s" % grant, "sha256": sha(snap),
                         "retrieved_date": RETRIEVED, "date_and_membership_checked": True,
                         "local_path": str(snap.relative_to(ROOT)), "format": "CORDIS project JSON (?format=json)"},
        "historical_extensions_status": extensions,
        "lineage_check": "supported", "lineage_evidence": lineage,
        "date_evidence_clarity": "explicitly_labelled_issue_submission_or_delivery_date_on_first_page",
        "licence_evidence": licence,
        "threshold_check": "early_at_or_below_50_percent; final_DMP_at_or_above_90_percent (D23)",
        "eligibility_status": "supported_candidate_not_verified_by_a_person_not_frozen",
        "early": doc(grant, start, dur, "early", *early), "late": doc(grant, start, dur, "late", *late),
        "uncertainties": uncertainties, "proposed_slot_membership_supported": slot in counts,
        "current_classification": {
            "paths": paths, "branch_path_counts": counts,
            "dominant_branches": [b for b, c in counts.items() if c == top],
            "dominance_rule": "most_frequent_top_level_branch_among_current_leaf_paths; ties_retained"},
        "added_by": "apply-swaps-2026-11-16.py (D24)", "review": "single_agent_reading_not_independently_rechecked",
    }


def main():
    if not V1.exists():
        shutil.copy2(PROPOSAL, V1)
    prop = json.loads(V1.read_text(encoding="utf-8"))
    new = {
        "engineering and technology": pair(
            "ColdSpark", "101069931", "engineering and technology", "2022-06-01", "2025-11-30",
            [["engineering and technology", "environmental engineering", "energy and fuels", "renewable energy",
              "hydrogen energy"]], "engineering and technology",
            "Late physical p4: 'Build on the M6 and M24 versions, this final DMP consolidates the practices "
            "implemented by all consortium partners'. Both are project deliverables D8.x 'Data Management Plan' of "
            "the whole consortium (M6 and M42).",
            "CC BY 4.0 on both Zenodo records. Both PDFs carry '© ColdSpark Consortium' without a reuse statement.",
            ["Final DMP is dated one day before the project end (99.92%); it qualifies only under D23.",
             "An intermediate M24 version (Zenodo 15543633) exists and is not used.",
             "PDF copyright line and the Zenodo CC BY licence are both retained; the depositor's licence is taken "
             "as the reuse basis."],
            ("14178018", [("2022-11-30", "Issue date on cover page (also Ares stamp 30/11/2022)", 1)]),
            ("19845992", [("2025-11-29", "Issue date on cover page (also Ares stamp 29/11/2025)", 1)]),
            "current_CORDIS_end_verified; complete_amendment_history_not_reviewed"),
        "medical and health sciences": pair(
            "BY-COVID", "101046203", "medical and health sciences", "2021-10-01", "2024-09-30",
            [["medical and health sciences", "health sciences", "infectious diseases", "viral diseases",
              "RNA viruses", "coronaviruses"],
             ["medical and health sciences", "health sciences", "public health", "epidemiology", "pandemics"]],
            "medical and health sciences",
            "Late physical p3: 'This document builds on the previous versions of the Data Management Plan' and "
            "'is the third version of the BY-COVID DMP delivered in month 34, being an update of the second version "
            "delivered in month 15'; it cites D8.2 (the early document) by title. Same deliverable series D8.2.",
            "CC BY 4.0 on both Zenodo records.",
            ["Final DMP was delivered two months before the project end (94.43%); it qualifies only under D23 "
             "and is the lowest late position in the set.",
             "The early record's Zenodo publication date reads 2021-03-31, before the project started; the record "
             "was created 2022-07-22 and the document itself says 30/03/2022. The document date is used.",
             "A second version D8.2.2 (Zenodo 7476926, delivered 2022-12-23, 40.9%) exists and is not used.",
             "The WP5 use-case DMPs on Zenodo are a different scope and are not part of this pair."],
            ("6884816", [("2022-03-30", "Actual Delivery date on cover page", 1)]),
            ("13981358", [("2024-07-31", "Actual Delivery date on cover page (also Ares stamp 31/07/2024)", 1)],
             [("2024-07-19", "Log of changes: 'Final version' (physical p2)")]),
            "current_CORDIS_end_verified; complete_amendment_history_not_reviewed"),
        "agricultural sciences": pair(
            "ASTEP", "884411", "agricultural sciences", "2020-05-01", "2025-06-30",
            [["agricultural sciences", "animal and dairy science", "dairy"],
             ["engineering and technology", "environmental engineering", "energy and fuels", "renewable energy",
              "solar energy", "solar thermal"]], "agricultural sciences",
            "Early physical p2: 'This is the initial Report of ASTEP's Data Management Plan D9.6'. Late physical p2: "
            "'This is the follow-up report of the ASTEP's Data Management Plan (DMP) D9.6 ... being the current "
            "deliverable the last update'. Same deliverable D9.6 (D9.6.1 and D9.6.3), whole project.",
            "CC BY 4.0 on both Zenodo records. Both PDFs say '© ASTEP Consortium. All rights reserved.' The two "
            "statements conflict; the depositor's Zenodo licence is taken as the reuse basis and the conflict is "
            "recorded.",
            ["CORDIS paths tie agricultural (dairy) and engineering (solar thermal); the local dataset's dominant "
             "branch is agricultural. The project is a solar-heat project with a dairy application.",
             "Late: submission date 2025-07-24 (101.27%) and last revision row 2025-06-26 (99.79%) both qualify "
             "under D23.",
             "CORDIS duration is 62 months; the early PDF plans updates at M24 and M48, which suggests an "
             "extension. The amendment history was not reviewed.",
             "An intermediate version D9.6.2 (Zenodo 8161456) exists and is not used.",
             "Conflicting rights statements (PDF versus Zenodo record), as noted under licence."],
            ("5772790", [("2020-10-31", "Submission date in the document summary", 1)],
             [("2020-10-30", "Revision history V3.1 'Final changes after peer review' (physical p3)")]),
            ("16411304", [("2025-07-24", "Submission date in the document summary", 1)],
             [("2025-06-26", "Revision history V3.0 'Last release of the deliverable' (physical p3)")]),
            "current_CORDIS_end_2025-06-30_62_months; likely_extended_from_48_months; amendments_not_reviewed"),
    }
    replaced = {}
    for i, p in enumerate(prop["pairs"]):
        if p["proposed_slot"] in new:
            replaced[p["proposed_slot"]] = p["project"]
            prop["pairs"][i] = new[p["proposed_slot"]]
    prop.update({
        "proposal_id": "paired-dmp-proposal-v2-2026-11-16", "prepared_date": "2026-11-16",
        "supersedes": {"proposal_id": "paired-dmp-proposal-v1-2026-11-04", "file": V1.name, "sha256": sha(V1),
                       "replaced_pairs": replaced, "decisions": ["D23", "D24"]},
    })
    prop["protocol"]["late_fraction_min_inclusive"] = 0.9
    prop["protocol"].pop("late_fraction_min_exclusive", None)
    prop["protocol"]["late_definition"] = "project's final DMP version, issued at >= 90% of the project run (D23)"
    prop["review"]["v2_new_pairs"] = "ColdSpark, BY-COVID and ASTEP were read by one agent on 2026-11-16; not independently rechecked"
    prop["unresolved_before_model_execution"] = [
        "human_reference_protocol_and_labels", "actual_model_provider_configuration",
        "ASTEP_PDF_all_rights_reserved_versus_Zenodo_CC_BY_4.0"]
    prop["reserves"] = [r for r in prop.get("reserves", [])] + [
        {"project": p, "slot": s, "status": "replaced_in_v2_kept_as_reserve; passes_the_strict_after_end_rule"}
        for s, p in replaced.items()]
    prop["input_sha256"]["data/dmp_dataset.json"] = sha(ROOT / "data" / "dmp_dataset.json")
    PROPOSAL.write_text(json.dumps(prop, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for p in prop["pairs"]:
        print("%-28s %-10s early %6.2f%%  late %6.2f%%" % (
            p["proposed_slot"], p["project"], 100 * p["early"]["document_dates"][0]["fraction"],
            100 * p["late"]["document_dates"][0]["fraction"]))


if __name__ == "__main__":
    main()
