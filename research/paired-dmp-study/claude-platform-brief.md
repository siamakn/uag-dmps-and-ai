# Claude handoff: necessary platform changes for a paired DMP study

Planning brief, 3 November 2026. Continuation decisions: D08 permits any documented CORDIS discipline membership, one final slot per project with dominant branch reported; D09 uses the latest authoritative project end including extensions, retaining originals and sensitivity. Use latest pinned DMP-EVA (tool-evolution.md), record discrepancies under software-baseline-policy.md, and use the successfully retrieved minutes (meeting-reconciliation.md). Publication/tool convergence is not a prerequisite for this study. No platform changes have been implemented for this brief. Read `AGENTS.md`, the actual code, and the other reports in this directory before implementation. The new study design below supersedes the old 3 × 3 plus challenging-case selection target; repository conventions remain applicable.

## Scientific deliverable and scope

### Concrete proposal now available (2026-11-04)

Use `cohort-proposal.json` and `cohort-proposal.md` as the reviewed working input:
iMagine/natural, EGI-ACE/engineering, NANOFACTS/medical, AGRICORE/agricultural,
SUSTRACK/social and RECHARGE/humanities. `pair-review.json` provides independent
identity, timing and current classification checks. Twelve exact source PDFs and six
CORDIS snapshots are preserved under the ignored local `data/paired-dmp-corpus/`.
Run `verify-cohort.py` to check them without writing the old selection.

Three proposed document versions are absent from the original dataset: RECHARGE's
early Zenodo record `17733866`, plus AGRICORE D9.2 and D9.3 from project-hosted URLs
with no Zenodo record IDs. Import them into the separate study-document registry
with source URLs, stable study document IDs and hashes. Do not invent Zenodo IDs,
overwrite generated dataset files by hand, or reharvest the entire pool to represent
these three documents. The remaining nine versions already have rows in the dataset.

The manifest now contains current classification paths and counts, historical local
dominant branches and explicit ties. AGRICORE ties natural/agricultural, and RECHARGE
ties humanities/medical in the current snapshots. Preserve both current and older
derived classifications; current RECAP does not have the agricultural membership
previously present in the dataset, so it is excluded from that slot.

The base 0/1/2 scale is now approved for calibration, and Siamak can test PILOT-01; formal benchmark reviewers remain unassigned. See claude-human-review-brief.md for a minimal pilot review-mode handoff. The proposal is not yet an experimental freeze: criterion/phase calibration and
model configuration remain pending. FAIR-EASE is a provisional reserve; the user
will obtain clarification of its conflicting rights statements. AGRICORE meets the
public-download condition but has no identified blanket reuse licence, so do not
automatically publish a source-document bundle or infer model-submission permission.
The instrument draft, empty calibration worksheet and record schema are provided in
`human-review-protocol-draft.md`, `calibration-worksheet.md` and
`human-review-record.schema.json`; do not populate them with synthetic human labels.

Support a transparent selection of **six different EU-funded projects, one assigned to each of the six broad EuroSciVoc disciplines, with two verified versions of the same-scope DMP per project: 12 distinct documents in six pairs**. The six disciplines are natural sciences, engineering and technology, medical and health sciences, agricultural sciences, social sciences, and humanities.

**User-confirmed timing: use the documented DMP issue date; the early upper bound is `fraction <= 0.50`, and late means `fraction > 1`.** The proposed default early lower bound is 0; pre-start inclusion has not been explicitly decided and must be settled if material before freeze. Keep repository publication dates separately; no publication-date fallback is approved. A missing evidenced issue date leaves eligibility unknown. The current dashboard's “late” label does not establish the required post-end condition. D09 settles extensions: use the latest authoritative end date including extensions, retaining originals and sensitivity calculations. Date precision and conflicting source evidence still need explicit provenance.

Prefer Horizon Europe, recent documents, and maDMPs, while allowing Horizon 2020 and PDF DMPs when needed. Metadata and verified document lineage govern selection; perceived DMP quality and schema completeness must never be eligibility rules. Sharing a grant establishes a candidate group, not a version pair. Separate partner DMPs from one consortium cannot be paired solely because their project matches. Different file formats may represent the same version and must not be counted as two versions.

**Search afresh across the full candidate pool.** The existing selection is historical material to preserve, not a privileged shortlist or a requirement to retain its six late projects. Start the paired-study draft empty and apply the same discovery/eligibility rules to all projects, broadening targeted repository/version discovery where the saved pool is incomplete.

The platform is still selection and evidence machinery. **DMP-EVA is the evaluation target to compare against human reference assessments; the Mainz work is a future model-comparison phase.** Do not create a competing tool/comparator track or substitute Mainz as the immediate evaluation target. A manual-review GUI for the Infra-DMP criteria is a separate phase after the cohort, document identity, protocol and files are frozen. Do not build scoring, AI review, or a new web stack during the selection phase.

## Verified gaps in the current implementation

| Component | Current behavior | Required consequence |
|---|---|---|
| `scripts/04_build_dataset.py:lifecycle` | Publication date only; ratio rounded to three decimals before classification; early ≤ 0.34, mid ≤ 0.70; everything above is late | Recompute from source dates for the paired study. Never infer >100% eligibility from `stage` or rounded `stage_frac`. |
| `scripts/common.py:slim` | Keeps a version label, but drops repository version relations/concept identifiers and file checksums | Targeted metadata enrichment is needed for lineage and file provenance; existing slimmed harvest cannot prove pairing. |
| Project/file association | The dataset takes the first matching CORDIS grant; corpus parsing reduces multiple maDMP files to one representation | Verify the project association and select exact files/scope for each study document rather than inheriting these summary choices as proof. |
| Dataset and `common.DASHBOARD_FIELDS` | Dataset has `version` and `stage_src`, but current shared dashboard payload omits both | Propagate required evidence through both served and standalone paths. |
| File and text payloads | Lists/descriptions are truncated; derived files omit original content URLs | Use a separate complete evidence manifest for selected files; truncated UI metadata is not the scientific record. |
| `dashboard/template.html:renderTray` | Counts independent record IDs in a 3 × 3 matrix; warns about a second document from a grant and >10 records | Add a six-pair study view with explicit assignments and validation. Two verified versions in one project are expected. |
| `serve.py:write_selection`, browser `dmpbench.sel` | Flat list of record IDs with derived summaries, no pair assignments or evidence | Add separately versioned paired-study storage without overwriting the legacy selection. |
| Existing exports | Record summaries omit pairing, timing sources, selected files, lineage and verification | Export a reproducible study manifest plus readable derivatives. |
| `dashboard/selftest.js` | Served API test saves sample IDs and then clears `/api/selection` | Tests must use isolated storage; running this harness against the user's current selection is unsafe. |

At inspection, `data/selection.json` exists and is **untracked**. It contains 12 resolved selected records from **12 unique grants**. It is a historical selection, not six verified pairs or the starting shortlist for the fresh search. Do not delete it, overwrite it, reinterpret its 12 entries as satisfying this design, or let a test change it. This supersedes `AGENTS.md`'s statement that the file is absent.

The companion [local corpus audit](corpus-audit.md) finds no established six-pair cohort in the saved pool: same-grant leads cover four primary branches with full publication dates, a scope-ambiguous medical lead appears with partial-date intervals, and humanities remains missing. Its publication-date calculations are a discovery aid only and do not establish eligibility under the now-confirmed issue-date rule. These are discovery limits, not verified pair counts or proof that other repository versions do not exist. The platform must support a visibly incomplete study and external/version discovery rather than manufacture a full matrix.

## Minimal implementation sequence

### 1. Preserve state and define a small study schema

Before any write or test, record a checksum of the legacy selection and make a byte-preserving backup outside the active selection path. Use an isolated temporary data root for tests. Keep `data/selection.json` and the existing browser key intact. Store paired-study drafts under a new path and namespaced browser key, for example `data/paired_selection.json` and `dmpbench.paired.v1`. Document actual paths rather than introducing needless abstraction.

Keep the legacy selection readable as historical material. Any optional import must be explicit and reversible, labelled historical/unverified, and must confer no eligibility or selection priority. Original IDs and unresolved references must survive import. Never discard unknown IDs silently. Loading a corrupt or unsupported study file must show an error, retain the original bytes, and avoid overwriting it with an empty draft. Use atomic file replacement as the current server does.

A compact JSON schema should distinguish:

| Entity | Minimum fields |
|---|---|
| Study/protocol | Schema version; draft/frozen status; protocol identifier; six-discipline target; issue-date timing basis; early upper bound `<=0.50`, proposed lower bound `>=0` and explicit pre-start policy status; late `>1` rule; no publication fallback; remaining date-extension/precision policy decisions; dataset/source snapshot identifiers |
| Project/pair | Stable pair ID; grant and EU programme; acronym; assigned discipline; original CORDIS branches/field pairs and source; same-scope descriptor; early and late document references; lineage evidence; verification state and reason |
| Document version | Stable document ID; record ID/URL; version-specific DOI where available; concept DOI/related identifiers where available; explicit version label; title; scope/partner; publication date; document issue date; selected file identities and formats |
| Dates/calculation | Raw dates and precision; source URLs and retrieval dates; page/section or JSON path for document dates; project start/end and source snapshot; chosen basis; elapsed days and duration days; displayed fraction; eligibility and ambiguity reasons |
| Evidence/files | Evidence URL/locator and short factual note; person/date of verification; file content URL, name, byte length, checksum algorithm/value, retrieval timestamp and local relative path; licence/access status; download failure/unknown state |

Keep values unavailable from evidence null/unknown. Distinguish “not checked,” “verified,” “contradictory,” and “unavailable.” A proposed pair can be saved while incomplete; it cannot be presented as verified or frozen. One record may contain multiple files/versions, so use document/file identity rather than requiring two different record IDs. Conversely two records containing the same bytes do not prove two different versions.

### 2. Add targeted evidence enrichment and exact timing

Reuse existing harvest and CORDIS code. Scan/group the full saved pool afresh without favoring the historical selection, then enrich candidates as needed, caching source responses with retrieval timestamps. Retain repository version relationships, identifiers and complete file metadata where provided. Add targeted traversal of a candidate's repository version chain and a way to register an externally found document with provenance; do not equate absence from the saved pool with absence of a predecessor. Verify the upstream API's version/pagination behavior before relying on it and record discovery coverage and failures. A fresh search does not require downloading every file or blindly rerunning the whole harvest; apply a documented, consistent discovery procedure across the full pool.

For every proposed pair, require evidence that both documents concern the same project and scope and that the second revises/succeeds the first. Evidence can include explicit revision history, matching deliverable identifiers with documented revision, document cross-reference, or a repository version relationship corroborated against the files' scope. Save locators and a human verification note. Automated same-grant grouping, title similarity and `v1`/`v2` labels are leads; they must not auto-verify lineage. Do not compare DMP quality to decide eligibility.

Compute timing from `(document_issue_date - project_start).days / (project_end - project_start).days`. Store integer numerator `n` and positive denominator `d` so the result is reproducible. Under the proposed nonnegative early window, early eligibility is exactly `0 <= 2*n <= d`; late eligibility is `n > d`. Label pre-start handling as proposed until settled. Apply integer comparisons, rounding for presentation only. A date exactly at project end is 100% and fails strict >100%. Show percentages above 100% without hiding them behind the existing clipped bar. Keep documented issue and repository publication dates side by side; publication-based calculations may be displayed as labelled discovery/sensitivity information only. Missing or ambiguous issue dates must never silently fall back to publication, deposition or update timestamps. A delayed deposit cannot establish a later-issued version.

Partial dates (`YYYY`, `YYYY-MM`) must retain their precision. Use earliest/latest possible dates to produce a possible fraction interval, or mark eligibility indeterminate; do not invent January 1 or the first of the month as an observed date. Explicitly handle missing dates, nonpositive project durations, conflicting source dates, project extensions, and negative fractions. Where project-end sources disagree, preserve the alternatives and chosen source/reason rather than overwriting the history. A field's presence in JSON does not establish its correctness.

### 3. Add the six-by-two view and validation

Keep the working candidate table, metadata sheets, filtering, sub-field pairing and local corpus access. Add the smallest sufficient paired-study panel:

- Six fixed discipline rows with project identity and early/late slots; show 0–6 complete pairs and 0–12 distinct documents separately.
- Assign/remove a candidate document to a pair and role; inspect both documents, scope/lineage evidence, dates and calculations together. Necessary evidence notes can be entered here without building a review system.
- Show pending, verified and rejected/contradictory states and the reason each slot is incomplete. Surface uncertain dates, wrong timing, missing files, unverified lineage, reused project, reused document and unsupported discipline assignment.
- Require six unique projects, each assigned to one of the six disciplines, and two distinct same-scope versions in each completed pair. A multidisciplinary project fills only its assigned row. Preserve all CORDIS classifications. D08 permits any documented CORDIS branch membership, with a single final slot per project and its dominant branch also reported. Do not infer discipline from DMP text.
- Make a true missing discipline/pair visible. Never fill a gap by relaxing timing or scope rules without a recorded protocol decision.

Replace the old target, duplicate-project warning and required challenging-case slot **within paired-study mode**. Sensitive-data flags may remain descriptive; a thirteenth challenging document is not part of the new target. Preserve old selection access rather than confusing the two studies. Every new control needs `data-tip`, keyboard access and a visible save/error state. Update relevant Guide text and obsolete preset descriptions.

### 4. Freeze the selected corpus and export it reproducibly

Add a small re-runnable stdlib downloader for explicitly selected files, including PDFs. Do not add PDF parsing/OCR dependencies for this phase: a human can read the cover/revision pages and record evidence. Check file-level availability instead of relying only on the repository record's access label. Preserve depositor licences; do not relicense source documents.

An explicit freeze action should validate the six pairs and approved protocol, then write a **new immutable snapshot** containing the protocol, pair assignments, source evidence, exact dates/calculations and selected-file manifest. Hash downloaded bytes with stdlib `hashlib`; distinguish any repository checksum from the locally computed digest. A checksum identifies bytes, not lineage. Missing required files or documented issue dates, incomplete lineage or unresolved eligibility block a valid freeze, while draft export remains available and labelled incomplete. Later edits create a new draft/snapshot; they must not mutate an earlier frozen cohort.

Provide downloadable JSON as the canonical manifest plus CSV and Markdown summaries carrying pair/project ID, assigned discipline, early/late document identity and date basis, percentages, lineage/verification state, DOI/file links and missing-evidence reasons. Keep evidence fields in JSON even when summaries are shortened. Use deterministic ordering, schema/protocol versions, snapshot timestamp and hashes of the relevant dataset/source snapshots. Reload/import must reproduce the same assignments without a live network lookup; exports must not regenerate historical evidence from today's dataset. Describe whether source files are included or referenced by relative paths, and make clear that an offline dashboard with links alone does not include the documents.

## Acceptance criteria and tests

1. Existing `data/selection.json` remains byte-identical after implementation tests and legacy-import trials; all 12 original IDs remain recoverable. Both browser selection namespaces remain distinguishable.
2. A synthetic valid six-project/twelve-document cohort fills all six rows and passes validation; incomplete cohorts stay saveable drafts but fail freeze with specific reasons. Tests need not find a real valid cohort to test the mechanism.
3. Same-grant/different-partner documents, repeated bytes, a project reused in another discipline, and one document used in two roles fail appropriate validation. A legitimate second version from the same project does not trigger the old duplicate-project warning.
4. Timing fixtures cover exactly 0% and 50% as early, any value above 50% as non-early, exactly 100% as non-late, one day after end as late, >100% display, partial dates spanning a threshold, invalid/missing duration, and pre-start dates governed by the explicitly recorded policy (non-early under the proposed default). A document issued before end but deposited after end must not qualify as late. Missing issue date stays unknown despite a complete publication date. Classification uses documented issue dates and integer arithmetic; unresolved extensions/precision conflicts cannot yield an unjustified valid freeze.
5. Real DOM clicks cover pair assignment/removal, evidence editing, filters after presets, save/reload, legacy import, export and error recovery. Test malformed/unsupported state and missing record/file references without data loss.
6. Served and standalone modes carry the same study fields and validations. Served API persistence is exercised only against temporary test storage. Standalone save/reload/import/export and its browser storage namespace are actually tested; skipping the API assertion does not demonstrate standalone persistence.
7. JSON round-trip preserves assignments, provenance, unknowns and exact day counts. CSV/Markdown escaping works for commas, quotes, pipes and newlines. Frozen snapshot checksums stay stable; a later live metadata change cannot silently alter it.
8. Rebuild `dashboard/dashboard.html` with `python3 scripts/05_build_dashboard.py`; edit only the template/source. Run appropriate Python checks and the headless UI suite, recording actual commands/results. Do not claim the old “180 assertions passing” as a new test result. Keep all existing applicable regressions, `allow_reuse_address = False`, and branch/sub-field pairing.

## Decisions to document before cohort freeze

- Evidence hierarchy for conflicting document issue dates (cover, revision history or structured fields), partial-date interpretation, and how ambiguous cases remain unknown. The confirmed governing basis is issue date, with early ≤50% (proposed lower bound 0) and late >100%; no publication fallback is approved.
- Apply confirmed D09 (latest authoritative end including extensions); retain source evidence and original dates, documenting conflicting authoritative sources if any.
- Apply confirmed D08 (any documented CORDIS membership, one final slot, report dominant branch); verify the source membership rather than silently extrapolating the topic.
- Whether a pair may change file format and which representation is the analysis document when PDF and maDMP accompany one version.

These questions do not prevent building explicit draft states, evidence capture and policy configuration. They do prevent claiming a scientifically eligible final set. Do not expand into authentication, hosting, collaboration, AI review, automated PDF extraction or a review GUI to avoid resolving selection evidence.

## Ready-to-paste prompt for Claude

> Work in this repository and read `AGENTS.md`, `research/paired-dmp-study/claude-platform-brief.md`, `research/paired-dmp-study/decisions.md`, and the companion research reports in that directory. Implement only the necessary selection-platform changes described in this brief, in small reviewable steps. The new target is six unique EU projects, one per broad discipline, with two verified same-scope DMP versions each. Confirmed timing uses documented DMP issue dates: early upper bound `fraction <= 0.50`, late `fraction > 1`; the proposed early lower bound is 0, with pre-start policy to be settled if relevant; retain publication dates separately and do not use them as a fallback. Search afresh across the full pool without filtering out possible issue-date pairs based on publication-date windows; preserve the historical selection without favoring its projects or requiring its six late projects. DMP-EVA is the evaluation target against human reference assessments; Mainz model comparison is future work, not a competing tool track. Preserve metadata-only selection and explicit unknowns. Do not invent resolutions for remaining precision/scope policies; apply D08/D09 for discipline and project-end dates, finalize a cohort, or use old `stage` labels as proof of eligibility. Start by preserving the untracked legacy `data/selection.json`; it contains 12 records from 12 grants and must remain recoverable. Isolate tests before running `/selftest`, because the current harness writes and clears the real selection endpoint. Reuse Python 3.7+ stdlib and vanilla JS, and the shared template/build flow; add no framework or dependency. Build a versioned pair/evidence model, targeted provenance enrichment, exact timing calculations, a six-by-two draft/validation view, safe separate persistence, selected-file capture, and reproducible manifest/export/freeze support. Keep manual-review GUI work out of this phase. Add meaningful tests including real DOM clicks and both served/standalone persistence. Record implementation results, changed files, commands and actual test outcomes, migration/backup details, limitations, unresolved methodological questions, and the exact decisions still needed in a dedicated `research/paired-dmp-study/claude-platform-results.md`. Preserve existing research reports. Do not claim candidates are verified pairs without saved evidence, and do not select on DMP quality. Finish with a concise report linking that results file.
