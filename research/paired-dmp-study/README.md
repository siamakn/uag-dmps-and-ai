# Paired DMP benchmark — start here

Updated: 2026-11-04 (Europe/Berlin). **Six-pair proposal prepared and independently checked; human reference protocol/calibration pending.** The human pilot is **deferred at the user’s request**; there is no immediate reading or rating task for Siamak. Corpus/source preparation and technical work continue independently. The approved 0/1/2 scale and blank pilot are retained for later; formal benchmark reviewers remain unassigned. The [cohort proposal](cohort-proposal.md) and status.json retain the study evidence. The twelve exact PDFs and CORDIS evidence snapshots are retained locally; this is not an executed benchmark or an experimental freeze.

## Current task and precedence

The user's 2026-11-03 request supersedes the old 10-document, three-discipline, three-stage design for this study. Target **six distinct European projects, one per each of six EuroSciVoc broad disciplines, with two versions of the same DMP scope per project: twelve documents**. User confirmed early ≤50% and later >100% of project duration, using the documented DMP issue date; publication dates are retained separately. Start a fresh search across the whole pool. D08 permits any documented CORDIS branch membership, one final slot per project with dominant branch also reported; D09 uses latest authoritative project end including extensions, preserving originals and sensitivity. The target is the latest pinned DMP-EVA commit assessed against human reference judgments, with publication/software differences documented rather than requiring convergence. Keep selection independent of perceived DMP quality.

Read `../../AGENTS.md` for repository conventions, then this file and `decisions.md`. Historical design text remains in the root README/AGENTS with an active-study pointer. The repository remains Python 3.7+ stdlib and vanilla JavaScript. Dashboard changes are a separate Claude implementation handoff, not implemented in this research pass.

## Readable project memory

**Latest continuation (2026-11-06):**
[scientific preparation alongside Claude](scientific-preparation-2026-11-06.md) and
[machine checkpoint](scientific-preparation-2026-11-06.json). This adds prior-study
methods reading, the publication/tool semantic crosswalk, independent source checks
and D15's separate early-phase calibration preparation. The human pilot stays
deferred; main benchmark phases, anchors and experiment freeze remain pending.
The [earlier checkpoint](continuation-2026-11-06.md) retains synthetic analysis
verification and bounded follow-up of recovered version records.
The earlier [parallel preparation](parallel-preparation.md) retains the experiment,
input-packet and Mainz readiness materials.

| File | Purpose |
| --- | --- |
| `uag-progress-note.md` | Concise meeting-ready selection, evidence, limitations and next steps; not sent |
| `extraction-qa.md` / `.json` | Technical comparison of 24 sampled source pages with both text extractions; no quality ratings |
| `pilot-start.md` | Deferred optional single-criterion calibration task, retained for later |
| `pilot-template.json` | Blank form wrapper with null responses, not a human assessment |
| `pilot-review.md` | Independent source/navigation/anchor check; initial 0/1 overlap resolved |
| `verification-checklist.md` / `.py` | Per-pair reading list for the person who verifies the six proposal pairs; nothing marked verified |
| `lead-shortlist.md` / `.json`, `lead-triage.py` | Reserve pairs screened from Zenodo version chains (18 concepts); nothing registered or selected |
| `claude-platform-results.md` | What the platform implementation built, test commands and results, backups, limits and decisions still needed |
| `claude-human-review-brief.md` | Minimal review-mode pilot implementation handoff for Claude |
| `cohort-proposal.md` / `.json` | Concrete six-project/twelve-document proposal, source links, dates, hashes and caveats |
| `pair-review.md` / `.json` | Independent verification of current memberships, version lineage, dates and exact source bytes |
| `prepare-cohort.py` / `verify-cohort.py` | Local preservation and verification of the proposal; no network or dashboard-selection writes |
| `human-review-protocol-draft.md` | Proposed independent human assessment/calibration workflow and instrument crosswalk |
| `human-review-record.schema.json` | Draft record contract; no human labels |
| `calibration-worksheet.md` / `calibration-proposal.json` | Blank worksheet and two projects outside the core cohort |
| `criteria-index.json` | Navigation to pinned framework cells and native criterion coverage |
| `rights-clarification.md` | FAIR-EASE conflict and user-owned clarification draft |
| `related-work-initial.md` | Bounded primary-source positioning; not an exhaustive novelty review |
| `plan.md` | Stages, responsibilities, completion gates and proposed scientific protocol |
| `decisions.md` | Confirmed requirements, pending choices and proposed defaults |
| `timing-and-rationale.md` | Precise timing rule, reporting language, scientific value and limits |
| `corpus-audit.md` | Reproducible local feasibility evidence and candidate leads |
| `study-sources.md` | Publication and original pinned DMP-EVA source findings |
| `tool-evolution.md` / `.json` | Live latest-commit check and publication/archive/latest discrepancy status |
| `tool-preflight.md` / `.json` / `.py` | Actual browser function checks without model requests; native input truncation measured on both text representations |
| `text-extraction.json` | Candidate extraction versions, hashes and pending reading-order/table QA |
| `dmp-eva-improvement-brief.md` | Evidence-backed tool improvements, separately versioned from the native baseline |
| `software-baseline-policy.md` | Latest-version pinning, native outputs and transparent discrepancy handling |
| `meeting-reconciliation.md` | Successfully retrieved full minutes, source hash and decision reconciliation |
| `version-inventory.md` / `.json` | Fresh full-pool version-family discovery queues without publication windows |
| `humanities-batch-01.md` / `.json` | Bounded live issue-date and scope checks, when completed |
| `claude-platform-brief.md` | Necessary platform changes and acceptance criteria |
| `review.md` | Independent review of initial planning package |
| `continuation-review.md` | Independent check of latest-software, minutes and continuation work |
| `status.json` | Compact machine-readable status and next actions |

Reports may be created during this planning session; consult status.json before treating a report as complete. The corpus audit's supporting files have the `corpus-` prefix.

## What collaborators can ask an agent

“Read research/paired-dmp-study/README.md and status.json. What is decided, what evidence do we have, what remains unresolved, and what is the next smallest task?” No code reading should be required for that summary. For factual verification, follow report source paths, hashes, URLs and calculation methods.

## Handoff rules

1. Do not treat candidate leads or current dashboard selections as validated pairs.
2. Record every user answer in decisions.md, then update affected plan/status fields. Never promote an unanswered recommendation to an approved rule.
3. Preserve data/selection.json. It already exists, is untracked, and represents twelve different projects. No overwrite, clearing, or silent migration. The current selftest writes selection; use isolated test storage for future testing.
4. Each task report must distinguish observed evidence, inference, recommendation and missing information. Record provenance and concrete next steps.
5. Keep candidate discovery, eligibility checking, human quality assessment and model evaluation separate. Assessing identity, version, scope, dates and extractability is allowed during screening; rating quality is not.
6. Update this index, decisions and status at each completed stage. Do not rely on conversation memory or agent IDs for continuation.

## Meeting access resolved

The full supplied Google Doc text was retrieved successfully on 2026-11-03 through the read-only TXT export (HTTP 200). No user login, sharing change or plugin connection is needed. See meeting-reconciliation.md for provenance and interpretation. Earlier reports of failed web/browser access describe the initial attempt and are superseded by this successful retrieval.

Google Doc: https://docs.google.com/document/d/1weSr-2fSnyMoOCq-AynX9tzCVwhxgh6woGyttz4i91w/edit?tab=t.0#heading=h.rahed0egsi0l

Source PDFs and downloaded evidence under `data/paired-dmp-corpus/` keep third-party terms and are ignored by Git; the public proposal uses links and hashes. AGRICORE has unknown blanket reuse terms. FAIR-EASE remains provisional while the user seeks clarification and is not required for the core proposal.

Baseline repository commit: `784712eff138f719a888451f2cee728085cd4bcd`. No benchmark model runs, external messages, commits, deployments, platform edits or final selection were performed in this planning pass.
