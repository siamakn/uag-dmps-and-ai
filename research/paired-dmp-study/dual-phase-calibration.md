# Separate early-phase calibration conditions

Prepared 2026-11-06. **D15 approves preparation of both early-phase interpretations as separate calibration conditions.** This is a blank preparation package: the pilot remains deferred, reviewers are unassigned, detailed anchors remain draft, and the main benchmark phase policy/model matrix is unchanged. No current reading or rating task is requested. [JSON companion](dual-phase-calibration.json) contains the three explicit 16-ID rosters and all blank response fields; it is a form wrapper, not a human assessment record or replacement schema.

## Documents, identity and access

The package reuses the two outside-cohort sources in [calibration-proposal.json](calibration-proposal.json), without a download or model submission. Exact local bytes were rehashed and their cover/metadata/revision pages visually checked. The existing [screening report](natural-engineering-social-search.md) supplies project dates and rights observations; those web facts were not refreshed here.

| Source | Exact retained PDF / SHA-256 | Verified identity and timing context |
| --- | --- | --- |
| [AD4GD 10839334](https://zenodo.org/records/10839334) | `data/paired-dmp-corpus/calibration/10839334.pdf`<br>`7c3d64d506c4c5a1db61ffc8c3abad716f616ff5a0fa32d35ee0519dcd9b4d93` | Grant 101061001; physical pp1–2. Issue/update 2024-02-29; 546/1095 = 49.863% against reported 2022-09-01–2025-08-31 dates. |
| [PathOS 17578116](https://zenodo.org/records/17578116) | `data/paired-dmp-corpus/calibration/17578116.pdf`<br>`732074dc327f114356c5cff1ccc7f6846d79480eabe8daa2b53951058e4e94fa` | Grant 101058728; physical pp1–2. Issue/update 2025-11-10; 1166/1095 = 106.484% against reported 2022-09-01–2025-08-31 dates. |

AD4GD cover and metadata identify D8.3 and deliverable version 3; p2 also lists document version 1 and retains a D8.2 running header. Preserve those details rather than silently resolving them. Its physical p3 abstract explicitly describes an intermediate report and implementation of the initial strategy; this declared purpose makes the two phase interpretations useful to calibrate, without deciding which phase should govern the benchmark. It is not an initial plan merely because its timing is below 50%. PathOS is D3.5 v2.0: pp1–2 distinguish its 2025-11-10 update from 2024-04-11 original delivery. Grants **101061001** and **101058728** differ from every grant in the current [six-project proposal](cohort-proposal.json): 101058625, 101017567, 952259, 816078, 101081823 and 101061233. Neither calibration source is added to that cohort.

AD4GD p2 marks dissemination Public; no blanket reuse licence is established in the existing screening evidence. PathOS landing pages were reported CC BY 4.0 in the 2026-11-03 screening. Public access does not infer external-model upload or redistribution permission. This package points to existing local PDFs, adds no external evidence artifacts and submits nothing externally. It does not freeze an extracted-text packet; any future representation/GUI adapter still needs its own provenance and validation.

## Conditions and approval boundary

| Condition | Source bytes | Framework phase | Status |
| --- | --- | --- | --- |
| `CAL-AD4GD-E` | AD4GD 10839334, hash above | `proposal_early_stage` | Approved to prepare under D15; anchors remain draft |
| `CAL-AD4GD-M` | **Same AD4GD 10839334 and identical hash** | `mid_project` | Approved to prepare under D15; anchors remain draft |
| `CAL-PATHOS-L` | PathOS 17578116, hash above | `end_project` | Retained proposed end-phase calibration context; no new general end-phase approval inferred |

These are **three condition rosters over two source documents/projects**. The AD4GD pair of labels identifies two calibration interpretations of one DMP, not two independent DMPs or an early/late version pair. PathOS is not AD4GD’s later document. The ≤50% sampling bin does not decide whether post-award AD4GD is better understood through initial-strategy or implementation expectations. D15 prepares both interpretations for later calibration; it does not approve either as the main benchmark policy or authorize extra main-model calls.

## Explicit criterion roster and exact source cells

Framework: Mansour et al., PDF Version 1.0, Table 2; SHA-256 `465a894b06bb67abea19acf16eba02dca8d665855a01572a7762ec3bb0e3fc26`. [Semantic crosswalk](rubric-comparability.md) and [JSON source locators](rubric-comparability.json) provide the audited physical/printed page mapping and pinned native pointers. Each column below is the complete 16-ID roster for that condition. **Numbers are physical PDF pages, not human scores.** Native coverage is separate source metadata and does not determine whether the publication row exists.

| ID | Navigation label only | `CAL-AD4GD-E` source cell pages | `CAL-AD4GD-M` source cell pages | `CAL-PATHOS-L` source cell pages | Default native ID present? |
| --- | --- | --- | --- | --- | --- |
| 1a | New data production and existing-data reuse | 7,8 | 7 | 7 | yes |
| 1b | Data types, formats and volumes | 8 | 8 | 8 | yes |
| 2a | Metadata and documentation | 8,9 | 8,9 | 8,9 | yes |
| 2b | Data quality control | 9,10 | 9 | 9,10 | yes |
| 3a | Storage and backup | 10,11 | 10,11 | 10,11 | yes |
| 3b | Access and relevant restrictions | 11 | 11,12 | 11 | yes |
| 3c | Security and sensitive-data protection | 12,13 | 12,13 | 12 | **no** |
| 4a | Personal-data compliance | 13,14,15 | 13,14,15 | 13,14 | yes |
| 4b | Intellectual property and other legal issues | 15,16 | 15,16 | 15,16 | yes |
| 4c | Ethical issues and approvals | 17,18 | 17 | 17 | yes |
| 5a | Sharing timing and restrictions | 18 | 18 | 18 | yes |
| 5b | Preservation selection and repositories | 18,19 | 18,19 | 18,19 | yes |
| 5c | Tools needed for access and reuse | 19 | 19 | 19,20 | yes |
| 5d | Persistent identifiers | 20 | 20 **blank: instrument undefined** | 20 | **no** |
| 6a | Responsibilities | 20,21 | 20 | 20 | yes |
| 6b | Resources for data management | 21,22 | 21 | 21 | yes |

Publication 4c refers to the unlabelled ethics block on physical pp17–18; the original PDF lacks its printed heading/question. The crosswalk preserves that attribution caveat. Read the full original phase cell when calibrating anchors; navigation labels and this wrapper are not replacement rubric wording.

`CAL-AD4GD-M/5d` has `instrument_defined=false` because the publication mid-project cell is blank. That fact is known **instrument metadata**, not a reviewer’s response. Its response remains blank like every other row. Do not inherit the early PID plan, end PID outcome or native 5b wording to fill it. Native 3c/5d absence is separately `native_present=false`; it is not a human score, document NA or a tool-failure label.

## Blank response contract

All **48 rows** retain `entry_state="not_entered"`, `score=null`, `applicability=null`, `evidence_state=null`, empty rationale/reasons/comments and empty evidence/search-section lists. Confidence and completed-search confirmation are null. No NA, uncertainty, absence claim or instrument disposition is prefilled as a human response. There are **47 defined cells** in total: 16 AD4GD-E, 15 AD4GD-M and 16 PathOS-L; one mid 5d cell is source undefined. There are zero entered responses, human assessment records or model outputs.

The approved scale is `ordinal_012_calibration_v1`; criterion/phase-specific anchors still require real human calibration. No expected answer, AI score or gold label is attached. The JSON wrapper is **not an instance of** `human-review-record.schema.json`. A future versioned adapter must create a valid assessment record only from an actual human response, retaining condition, exact document and rubric-phase provenance. This preparation changes neither that schema nor the GUI.

## Proposed order and carryover handling

No reviewer is assigned or session scheduled. If more than one reviewer later participates, counterbalance first AD4GD exposure across **E→M** and **M→E** sequences. Prefer separate first-pass reviewers initially seeing only one phase’s instructions, source cells and blank form; lock/save that pass before other-phase material or reconciliation. A later second phase from the same reviewer is explicitly repeated exposure, not a new independent human observation.

Choose and log an interval before a second pass; no untested interval guarantees washout. Do not show prior ratings or prefill the second form. Keep full source bytes identical, keep model outputs withheld, and record sequence, dates, prior familiarity and any access to the other condition. Phase instructions necessarily reveal the task, so no phase blinding is claimed. Balance PathOS’s position if practicable; a different document is not a proven washout mechanism. With one reviewer, one sequence supplies usability/calibration observations only, not a counterbalanced phase experiment or reliability estimate.

Calibration discussion should first compare what each phase asks for, which evidence was found, applicability interpretation and proposed anchors. Preserve independent first passes before revising anchors. The extra reviewer work is real: per reviewer the proposed full package contains 48 rows, with at most 47 source-defined scoring opportunities before applicability/evidence dispositions are known. Do not call this 48 completed ratings or imply that the three condition rosters are three independent DMPs.

## Interpretation and next boundary

Holding AD4GD bytes constant isolates the document from the phase-lens change, but phase requirements differ. A later E/M score difference would reflect judgments under different expectations, not evidence that AD4GD improved. Equal 0/1/2 values do not yet have calibrated equivalent meanings across phases; ordinal categories do not establish interval distances. Keep conditions separate rather than averaging them into a reference score. No automatic mapping to native 0–100 is defined or approved.

Preparation is complete when the blank rosters and source identity checks are reviewable; human calibration remains deferred. Later methods work must settle phase anchors, evidence-packet boundaries and review exposure/order before scores are entered, then distinguish any main benchmark choice from these calibration conditions. No main matrix, selection, prompt, model call count, platform or existing instrument is changed by this package.
