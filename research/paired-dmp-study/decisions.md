# Decisions and open questions

Updated 2026-11-06. User answers override recommendations below.

## Confirmed from user's request

- Six distinct projects, twelve DMP documents, one project for each of the six existing discipline categories.
- Each pair must represent the same DMP at two stages, not unrelated DMPs in one category. Same-project evidence alone is insufficient where partner/pilot scopes differ.
- Focus on European DMPs; prefer newer material. Existing repository preference for Horizon Europe over H2020 and for maDMPs remains a preference, subject to feasibility.
- Choose using metadata, not perceived quality. The older extra challenging-case slot is not part of the new twelve-document target; sensitive-data flags can be descriptive metadata.
- Read Mansour et al. and DMP-EVA; support overall and criterion-based prompts, open-weight model comparison and human reference assessments, as recorded in pasted 7 October minutes.
- Plan in stages now; save agent-readable progress; supply platform recommendations as Markdown for Claude. Use lighter worker agents with independent checking.
- User accepts spending roughly a week's subscription allowance, but this is not a fixed measurable token or money budget and does not authorize paid API calls or purchases.

## Confirmed interactive decisions (2026-11-03)

| ID | Question | User decision | Consequence |
| --- | --- | --- | --- |
| D01 | Which date establishes stage, and is late strictly >100%? | Use the documented DMP issue date: early ≤50%, late >100%; retain publication dates separately. User requests a precise, scientifically defensible rule and rationale in reports. | Publication-only screening is provisional; delayed deposits do not establish a later revision. See timing-and-rationale.md. |
| D02 | How to use current 12-record selection? | Start a fresh search across the full pool. | Preserve historical selection; do not privilege its projects. |
| D03 | What is the benchmark's main tool? | DMP-EVA, the supplied repository and the team's own work, evaluated against human assessment. Mainz resources may support later model comparisons. | This is human-vs-tool validation, not competition among tools. Pin the evaluated DMP-EVA version and actual model backend before execution. |

All three answers were explicitly supplied by the user on 2026-11-03. Questions about other policies below remain proposals; no answer is inferred from elapsed time. The user invites justified improvements and asks for scientific/community/NFDI value.

## Confirmed continuation decisions (2026-11-03–04)

| ID | User decision | Operational consequence |
| --- | --- | --- |
| D04 | Ignore the historical twelve-document selection where it does not satisfy requirements. | Fresh discovery may exclude all its records; preserve the file as history without giving it priority. |
| D05 | Use the latest DMP-EVA version, compare it with the publication-associated state, note discrepancies and whether latest resolves them. | Resolve live latest once per campaign, pin its commit and configuration, and maintain tool-evolution.md/json. Do not ask again whether to use archived versus latest. |
| D06 | A robust study can proceed even when publication and tool diverge; report needed improvements honestly and concisely. | Convergence is not an execution gate. Record native tool behavior, rubric crosswalk and limits; any altered configuration/code is a distinct condition. See software-baseline-policy.md. |
| D07 | This conversation remains the orchestrator; use appropriately capable worker and checking agents. | Parent is now GPT-6.1 Sol; bounded extraction uses Terra high and complex source/review work uses Sol high. |
| D08 | Allow any documented CORDIS discipline membership; assign each project to one slot and report its dominant branch too. | Eligibility can use an evidenced secondary branch, but no project may fill two final slots. Preserve the full classification and provenance. |
| D09 | Use the latest authoritative end date, including extensions; preserve original dates and show sensitivity if eligibility changes. | Calculate primary timing against the latest evidenced end date; retain historical dates and alternative fractions. |
| D10 | Continue autonomously until a necessary decision or blocker, rather than ending at routine progress checkpoints. | Save interim evidence and keep retrieval/review moving; report concrete access or quota blockers plainly. |
| D11 | Keep FAIR-EASE provisional while the user obtains clarification using the saved draft; continue alternatives. | No agent outreach. AGRICORE is an alternative that meets public-access, timing and lineage criteria; its unknown blanket reuse terms remain explicit. |
| D12 | Approve criterion-level 0 = not evidenced, 1 = partial, 2 = sufficient, with separate NA and uncertainty states, for calibration. | Use named scale ordinal_012_calibration_v1; criterion/phase-specific anchors still need calibration and versioning. No automatic conversion to native 0–100 scores. |
| D13 | Formal human assessors are not yet decided; likely UAG DMP/AI members or assisting librarians. Siamak is available to test and provide human evaluation. | Assign Siamak only to a pilot role R-PILOT-01. Keep benchmark reviewers and reconciliation/adjudication allocation unassigned; do not assume Andrej agreed. A one-person pilot can proceed without becoming an independent human reference dataset. |
| D14 | Defer Siamak’s pilot review for now; he needs time to read and familiarize himself with the publication. | No immediate reading or rating task is required. Continue corpus/source preparation, technical checks and handoffs. Preserve the blank pilot for later; deferral is not a score, NA, uncertainty judgment or project-wide pause. Human reference assessments remain necessary later for empirical human/tool agreement claims. |

## Confirmed parallel-preparation decision (2026-11-06)

| ID | User decision | Operational consequence |
| --- | --- | --- |
| D15 | Prepare both early-phase interpretations as separate calibration conditions, accepting more reviewer work. | Prepare proposal/early and mid-project expectations for the same outside-cohort early calibration document, keeping both conditions distinct; retain end-project expectations for later calibration material. This authorizes preparation for calibration, not the main benchmark phase policy, detailed anchor approval, reviewer assignment, model calls or experiment freeze. D14's human-pilot deferral remains in force. |

The user also clarified that scientific work should progress while Claude implements
the platform. Independent platform acceptance review is postponed until that work
is stable. Source studies and rubric comparability were advanced in separate
research files; no platform tests were run after this clarification.

The Google meeting minutes have now been retrieved successfully through their direct text export. No user login or sharing change is needed. See meeting-reconciliation.md for source hash, scope and reconciliation.

## Confirmed protocol decisions (2026-11-06)

Asked interactively by Claude after the platform implementation; answered by the user.

| ID | User decision | Operational consequence |
| --- | --- | --- |
| D16 | Issue-date evidence hierarchy: an explicitly labelled issue / submission / delivery date wins, then the dated cover, then that version's revision-history row. Other labelled dates stay as alternatives. | `scripts/paired.py:date_rank` chooses the issue date on import. Under it, iMagine early moves from the unlabelled cover (2023-02-28) to the labelled delivery date (2023-03-09, 17.26%) and SUSTRACK early from the revision-history row (2023-04-27) to the submission date (2023-04-29, 16.35%). NANOFACTS keeps 2021-06-30. All verdicts are unchanged. An alternative that would flip a verdict keeps the pair unresolved. |
| D17 | Partial dates (YYYY, YYYY-MM) are intervals; a range straddling 50% or 100% is indeterminate. | As implemented. An indeterminate pair cannot be frozen. |
| D18 | When one version has both a PDF and a maDMP JSON, the PDF is the analysis file; mixed formats within a pair only if recorded as a confounder. | All twelve proposal documents are single PDFs; no change today. |
| D19 | A document issued before its project started cannot fill an early slot. | The proposed lower bound `n >= 0` is now confirmed. No proposal document is affected. |

These four were the open decisions in the platform's protocol panel; they are now marked resolved
there. The protocol as a whole is still **not approved** (approval is a separate, explicit act), and
no pair is verified.

## Selection protocol approval (2026-11-09)

| ID | User decision | Operational consequence |
| --- | --- | --- |
| D20 | The user approves the selection protocol as a whole: documented issue-date timing (early `2n <= d`, late `n > d`, no publication-date fallback), D08, D09 and D16–D19. | `scripts/paired.py:default_protocol` now carries `approved: true`, approver Siamak Nakhaie, 2026-11-09, with the approval scope recorded. The approval covers **selection only**, not the experiment protocol (rubric phase mapping, score anchors, model configuration, repetitions). Freezing still needs all six pairs verified by a person. |

## Proposals to settle after feasibility

- Apply recency primarily to the later version; permit an older early version, explicitly recorded. Do not silently impose 2024+ on both.
- Confirm project-wide DMPs as the preferred scope. If partner-specific DMPs are included, require the same partner and coverage across both versions and label the limitation.
- D08 resolves the classification rule: any documented CORDIS membership, one final slot per project, dominant branch also reported.
- D09 resolves the project-end rule: latest authoritative date including extensions, original dates retained with sensitivity calculations.
- Accept PDF/JSON mixtures if needed, but record representation as a possible confounder; never require clean schema validation for inclusion.
- Declare language inclusion, authoritative scheduled/extended project-end basis, how to rank equally eligible pairs, reviewer availability, calibration examples and model-run repetitions before freezing the benchmark.
- Pin the latest DMP-EVA commit under D05, record its actual configuration, and complete the rubric crosswalk and stage-to-rubric mapping. ≤50% sampling does not automatically mean proposal-stage scoring. An adjusted or corrected condition is optional and must be labelled separately.
- If strict thresholds cannot fill six categories, present documented gaps and explicit alternatives (broader EU programmes, older pairs, more repositories, or a changed late window). Do not relax a threshold automatically.

## Meeting evidence available

User pasted 2026-10-07 notes: compare open-weight LLMs with standardized prompts and human reference; Mainz UI for demonstrations and API for systematic testing; compare overall and criterion-based prompts; read Mansour et al. and DMP-EVA; build human reviewer GUI; propose six projects across six disciplines with a late DMP and a version before 50%; discuss limitations and invite alternatives at UAG; timeline flexible.

The pasted notes say “late-stage”; the user explicitly confirmed the narrower “above 100%” criterion using issue dates. Full linked minutes were subsequently read through the TXT export; see meeting-reconciliation.md. Historical approximate thresholds do not override the current explicit rule.
