# Independent review of the paired-DMP planning package

Reviewed 2026-11-03. This is a bounded independent check of planning evidence, not approval of a frozen cohort or an executed benchmark. No final pairs have been verified by this review.

## Conclusion

The local audit calculations and the crucial pinned-source findings withstand independent cross-checking. No numerical correction to the corpus summaries is needed. The package appropriately separates same-grant discovery leads from same-scope version pairs and limits six-project conclusions to exploratory case-study evidence. Final reconciliation found no remaining blocker to delivering this planning package; the execution/protocol gates below still apply.

The user's subsequent confirmations govern continuation: issue-date timing with early `fraction <= 0.50` and late `fraction > 1`; a fresh whole-pool search with the old selection preserved as history; and DMP-EVA as the immediate human-versus-tool evaluation target. The proposed lower bound of zero excludes pre-start versions but was not an explicit user answer; retain that distinction and resolve it before freeze if material. These choices do not turn the publication-date audit into an eligible issue-date cohort. Protocol and software-version decisions remain before evaluation.

## Findings by severity

| Severity / state | Finding and evidence | Correction or required action |
| --- | --- | --- |
| High, execution gate | DMP-EVA is not a single reproducible experimental condition. Archived v0.1 at `db85e5a71271239f8fbe3e271e4aa8b7e71d6321` includes rubric wording in its prompt and maps short phase names; inspected current main at `b80b43de820d46440d982eb99b2b3da8f4c2f818` omits that wording by default and has inconsistent phase representations. | Declare the target release/commit, loaded rubric, prompt, and actual request before human/tool comparisons. Distinguish evaluation of the unmodified release from any patched or full-matrix configuration. Silently fixing these paths would change the evaluated intervention. |
| High, execution gate | Both inspected evaluators omit all zero-scoring categories from the overall mean. Current main `js/evaluator.20260423a.js:192–197`; v0.1 `js/evaluator.js:171` onward. Thus a single positive category can dominate the headline while missing categories contribute nothing. | Retain the native score if studying the tool as released, report coverage and criterion scores alongside it, and label any separately recomputed aggregate. Do not treat the native overall score as a validated complete-rubric quality measure. |
| Medium, protocol gate | The confirmed issue-date rule differs from the audit's publication-date discovery screen. Delayed deposition can change either role; the current humanities/medical counts therefore do not establish issue-date feasibility or infeasibility. | Preserve the audit as a snapshot of discovery leads. Obtain issue dates and scope/lineage evidence before classifying pairs as eligible; do not infer issue date from repository publication or update time. |
| Medium, reporting requirement | `<=50%` and `>100%` are operational sampling strata, not empirically validated stage definitions supplied by Mansour et al. Strict `>100%` deliberately excludes documents issued on the project end date and final plans issued before it. | Explain this convention and its consequences: first-half versus post-end document versions, availability/late-reporting bias, possible scarcity, and no causal or population claim. Preserve exact day arithmetic, date uncertainty, and extension provenance. Any alternative threshold is a separate declared protocol decision. |
| Medium, corrected during reconciliation | The new timing rationale distinguished the proposed zero lower bound from the confirmed `<=50%` cutoff, while the initial plan and Claude brief described the full `0–50%` interval as user-confirmed. | The coordinator corrected attribution in the plan and brief, including the ready-to-paste prompt. Zero remains a proposed default, with explicit pre-start treatment before freeze if material. |
| Medium, addressed in source report | Current main transforms double quotes in DMP text to single quotes while constructing the prompt (`js/llm-service.js:95–101`). This means identical extracted files need not imply identical model-visible text across implementations. | The revised source report now identifies the transformation. Save/hash the final assembled model-visible prompt as well as canonical extraction; do not call returned quotations exact reproductions without checking. |
| Low, corrected during review | Original `source-provenance.json` labelled the queried commit as `tree_sha`. The commit object's actual tree is `b4ec23af67aa8129d2e001799e37dede9a897042`. | Source worker corrected `tree_sha` and retained `queried_tree_ref`. Every inspected main file also independently matched its pinned Git-tree blob SHA-1 and reported SHA-256. |

These are execution/protocol gates and resolved reporting issues, not reasons to stop metadata discovery or draft platform work.

## Independently checked calculations

An independent stdlib Python calculation read `data/dmp_dataset.json` directly, without importing the audit's functions or rewriting its output. It implemented the documented metadata filters, calendar intervals, and integer day comparisons. It matched all six summaries, including every primary-branch and overlapping `disc_all` count:

| Discovery condition | EU grants / record combinations | Horizon Europe grants / combinations |
| --- | ---:| ---:|
| Complete publication dates, all years | 19 / 26 | 11 / 14 |
| Both publication years 2024+ | 2 / 3 | 2 / 3 |
| Entire partial-date intervals qualify | 21 / 28 | 13 / 16 |

The 19 complete-date groups had consistent project start/end dates, primary discipline, discipline memberships and tier within each grant. Distinct early/late records were checked. All recorded audit input hashes matched bytes at the calculation cross-check, before the coordinator's later orientation-document edits. These tests establish internal reproducibility, not correctness of external CORDIS dates, issue dates, grant association, or document lineage.

The saved selection resolves to 12 distinct grants. Its SHA-256 remained `a4a54dba18af7d8a28c1b60e4c317921c7768573735adcd7d44eafa66007edeb`. Neither the dashboard selftest nor any selection-writing endpoint was run.

## Independently checked source claims

Static inspection of the cached pinned files confirms:

- Both default `eva.json` files have 14 subsection IDs and omit 3c and 5d; the published matrix has 16. A custom/fallback rubric is a different condition and must be identified.
- Current main uses criteria IDs without automatically inserting criterion wording or `criteriaContext`; archived v0.1 includes them. The release distinction is essential.
- Main's single-run UI supplies `proposal/mid/end`; its prompt instructions recognize long names. Batch mode supplies long names; the EVA JSON extractor recognizes short names. Each unmatched map defaults to early-stage handling.
- Main's parser has no PDF case, pretty-prints JSON, and truncates text at 30,720 JavaScript string units. This is not a 30,720-byte or token limit. No such truncation claim was extrapolated to v0.1.
- Main's request builder does not transmit the profile temperature or a seed. The native export lacks sufficient information for reproducing an exact request.
- The supplied implementation DOI identifies a software archive, not an empirical evaluation paper. The preprint describes stage-aware criteria; its inspected text does not validate a 0–100 human reference scale or the proposed numerical stage cutoffs.

This review checked the preprint's extracted text and the source worker's recorded scope, rather than independently re-rendering all 28 pages. The source worker visually checked the matrix layout. Source cache hashes matched the provenance report, including the PDF and v0.1 ZIP; current source file bytes additionally matched the pinned tree's Git blob identifiers. No application, prompt assembly, provider or model was executed.

## Reviewed scope and remaining uncertainty

Read `AGENTS.md`, study README, plan, decisions, timing rationale, Claude platform brief, audit script/report/JSON, source report/provenance, status JSON, and relevant cached main/v0.1 code. A final reconciliation read confirms that D01–D03 are now recorded as answered and that the issue-date basis, fresh whole-pool search and DMP-EVA target are propagated. Earlier pending-choice wording must not override those confirmations. The zero-lower-bound attribution has also been corrected, and the plan/status explicitly distinguish publication-date discovery from issue-date eligibility.

The platform brief's preservation of legacy state, separate paired-study storage, exact date calculations, file/version identity, partial-date handling, immutable freeze evidence, and isolated tests address the main implementation risks. No platform implementation or test results are implied by this assessment.

Not independently verified: live Zenodo version completeness or file access; any candidate's original files, licence, issue dates or common scope; CORDIS source dates/classifications and extensions; full linked Google minutes; supplementary discipline DOCX guidance; account allowance/model availability; Mainz infrastructure; runtime behavior of DMP-EVA. No selected six-pair cohort, paid evaluation, or generalization across disciplines is established.
