# Research activity and handoff log

## 2026-11-04: concrete proposal and preflight

- Consolidated six independently supported same-scope pairs in `cohort-proposal.md/json`: iMagine, EGI-ACE, NANOFACTS, AGRICORE, SUSTRACK, RECHARGE. No DMP quality scores were used for selection. This is a proposed pilot set, not an executed or frozen benchmark.
- Preserved twelve exact PDFs, six CORDIS snapshots, available complete record metadata, the framework PDF, and two separate calibration PDFs under the ignored `data/paired-dmp-corpus/`. Public-facing material consists of source links, attribution metadata and hashes; third-party source terms remain in force.
- Computed current CORDIS path counts and dominance/ties separately from the older dataset. RECAP's current agricultural membership is unsupported, so it does not fill that slot. AGRICORE supplies agricultural membership; RECHARGE and AGRICORE each have a current branch-frequency tie.
- Recorded D11: the user will seek FAIR-EASE rights clarification using the saved draft. It remains provisional; AGRICORE is the working agricultural alternative. AGRICORE has no identified blanket reuse licence, an explicit unresolved intended-use limitation rather than an extra public-download exclusion.
- Verified six unique projects/slots, twelve distinct PDF hashes and every retained date alternative with exact integer arithmetic. Historical `data/selection.json` remains byte-identical. `prepare-cohort.py` and `verify-cohort.py` use Python stdlib and no network.
- Prepared a human reference protocol draft, portable record schema, blank calibration worksheet and criterion-navigation index. AD4GD and PathOS are proposed calibration projects outside the final six. No human judgments were generated.
- Isolated Chrome execution of six hash-verified DMP-EVA files at the pinned working commit completed 44 assertions with no model/provider request. It confirmed default rubric/prompt differences, phase-key mismatches, zero-excluding aggregation, parameter propagation and native parsing behavior. These assertions verify observed behavior, including anomalies; they do not validate model quality.
- All twelve layout TXT extractions and eleven of twelve reading-order alternatives were truncated by the native 30,720 UTF-16-unit parser. Source text/table QA remains pending. Native-prefix results must not be called full-document assessment, and input limitations must not be attributed to DMP quality.
- Saved `dmp-eva-improvement-brief.md` for a separately identified intervention; no changes were made to upstream DMP-EVA or the local dashboard. Model comparison still requires the human reference, actual model configuration and an approved analysis/input condition.

## Earlier calibration-choice checkpoint (subsequently resolved)

Interactive questions ask (1) whether to calibrate an anchored 0/1/2 criterion scale,
use the earlier 1–10 suggestion, or compare both during calibration; and (2) who will
provide independent human assessments. Recommendations are not approvals. Actual
human ratings cannot be supplied by agents. Continue after recording those answers,
then use calibration to settle phase-specific anchors and analysis choices.

## Earlier evidence

The 2026-11-03 reports retain their bounded search histories and original source
hashes. Some early reports describe publication-date leads or access failures; the
current README, status and later reconciliation reports identify what supersedes
them. The full meeting minutes were successfully retrieved through Google Docs TXT
export; no user login or sharing change was needed. Worker quota failures occurred
intermittently, and later retries recovered and persisted the substantive evidence.

No external messages, source-document publication, commits, deployments or benchmark
model runs were performed. The original dashboard's twelve-project shortlist remains
historical and separate from the new paired proposal.

## 2026-11-04: approved scale and Siamak pilot

The user approved criterion-level 0/1/2 for calibration with separate NA/uncertainty. Formal assessors remain undecided (UAG members or assisting librarians); Siamak is available for testing/evaluation. D12/D13 preserve that distinction. A worker updated the protocol/schema, and a separate agent checked the source/navigation/blank form. The draft 0/1 anchor overlap was corrected. `pilot-start.md` now requests one actual human judgment on PathOS criterion 1b using the end-project cell, with evidence/search scope and usability feedback. No human response or score has yet been entered. A one-person pilot is not inter-reviewer validation. The next action is the human pilot response; reviewer recruitment need not block it.

## 2026-11-04: pilot deferred; independent preparation continues

D14 records the user’s preference to defer the pilot because reading the publication and becoming familiar with the framework requires time. The previous presentation of this pilot as the immediate prerequisite was too strong: selection, source/input preparation, technical checks, documentation and platform work do not require human ratings. No assessment, NA or uncertainty label was inferred from deferral. The pending rating request is cleared. Human calibration and genuine reference judgments remain future requirements for human/tool agreement claims, and recruitment is open. Technical extraction QA and a meeting-ready progress note proceed independently.

Technical preparation continued during deferral: a separate worker compared 24 sampled source-PDF pages to both text alternatives and checked 36 file hashes. Layout generally retained sampled table relationships better, but neither representation is ready to freeze; whole-document fidelity was not established. The meeting-ready `uag-progress-note.md` now summarizes the six-pair proposal, operational timing rule, actual technical findings and future human work. It has not been sent.
