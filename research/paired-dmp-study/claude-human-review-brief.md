# Claude handoff: human-review support with pilot deferred

Updated 2026-11-04. Documentation-only handoff; no review GUI has been implemented.
This complements the selection-platform brief and uses the current protocol rather
than replacing it.

## Confirmed scope

The user approved criterion scores **0 = not evidenced, 1 = partial, 2 = sufficient**
for calibration, with separate NA and uncertainty states. Criterion/phase anchors
remain drafts until tested. **The user explicitly deferred the pilot because reading
and familiarization take time. No pilot response or publication reading is required
now; do not issue a new pilot request.** Retain blank materials and `R-PILOT-01` as
Siamak's ID if a future pilot is resumed.
Formal independent reviewers are not yet assigned; they may be UAG DMP/AI members
or assisting librarians. Do not assume Andrej is assigned. Recruitment remains open.
No score, NA or uncertainty judgment follows from the user's deferral.

Start with [pilot-start.md](pilot-start.md), [pilot-template.json](pilot-template.json),
[pilot-review.md](pilot-review.md), the updated [protocol](human-review-protocol-draft.md)
and [record schema](human-review-record.schema.json). The blank form wrapper is not
an assessment record. Only an actual human response may create a human judgment.

## Small first implementation

Add a separate review mode to the existing local platform using Python stdlib and
vanilla JS. Reuse its theme, tooltip and served/standalone patterns. The first
screen can use the prepared PathOS document and criterion 1b as an empty form fixture;
do not require the user to complete it before implementation or scaling to the cohort.
Show the pilot as **deferred**, not overdue, failed, or assessed. Two readiness tracks
remain separate: corpus/evidence/input preparation, software checks and GUI
implementation can proceed; actual human calibration, labels, reliability and
AI-human agreement require real human participation and the relevant frozen protocol.

- Show the source PDF link, exact document version and the framework's relevant
  physical page/stage cell. Keep the full source accessible; a shortened extraction
  must not silently become the human packet.
- Show approved scale labels and draft criterion anchors from the pilot instructions.
  Leave the initial response **not assessed**, with no preselected numeric score.
- Collect applicability, evidence state, explicit human score or null, physical
  pages/sections, rationale, confidence and usability feedback. NA and uncertainty
  have null numeric scores. Missing input never becomes zero.
- For a zero, require a human statement that a relevant criterion-specific search
  was completed and retain its scope. Relevant but incomplete evidence belongs to
  the partial category; inability to search or judge can be recorded as uncertainty.
- For future voluntary use, offer **Save draft**, **Preview response**, **Submit pilot
  response** and **Export** actions. A one-criterion pilot is a valid scope. Deferral
  creates no assessment record and must leave the form blank. A human submission
  locks its original record; later corrections create a new revision linked to it.
- Save the raw human wording alongside structured fields. Preserve source hashes,
  instrument/scale/anchor version, intended rubric phase and pilot status. Do not
  interpret a pilot response as a completed two-reviewer reference assessment.
- Keep pilot state under its own storage key and served API/data path. Preserve
  `data/selection.json`, the paired proposal and existing review records. Missing
  records, unsupported versions or invalid JSON must not be silently reset.
- Show only human-review material in the reference-label flow. Do not prefill scores,
  evidence quotations or suggested judgments from agents or DMP-EVA. Keep model
  outputs hidden from independent reference reviewers until their labels/adjudication
  are locked. This does not bar separately authorized technical model smoke tests
  before labels exist; isolate and log them as diagnostics, with no accuracy claim.
  Substantive held-out agreement needs real independent labels and a frozen protocol;
  never tune prompts on final-cohort gold labels. Use outside-cohort development data
  and record any final-cohort exposure relevant to held-out status.

Every new control needs `data-tip`, keyboard access and a visible save/error state.
Use ordinary labels in the interface; schema field names and storage details belong
in implementation documentation. Do not add authentication, messaging, hosting,
model calls or a new framework for this pilot.

## Meaningful acceptance checks

Use real DOM interaction and isolated test storage. Verify that an untouched form
has no score; explicit zero survives save/export; a partial score is distinct from
zero; NA/uncertain stay null; absent pages/rationale are retained as missing draft
fields rather than fabricated; score/evidence inconsistencies are explained before
submission; draft reload is lossless; a submitted record cannot be overwritten;
corrections retain the original; future single-criterion submission does not require
recruited benchmark reviewers; deferred status does not create a rating/disposition or
block unrelated corpus/software/GUI work. Exercise served and standalone persistence separately.
The historical selection must stay byte-identical after tests.

The large JSON Schema is a portable contract, not a reason to introduce a new runtime
dependency. Implement the needed pilot validation in stdlib/vanilla JS and document
which cross-record rules remain for benchmark mode. Rebuild the generated dashboard
from its template; do not edit the generated file directly. The existing `/selftest`
writes selection and must run only with isolated storage.

## Ready-to-paste task

> Read AGENTS.md, the paired-study README, current decisions, this brief and the review
> protocol/schema. The user deferred the pilot; no response or publication reading is
> required now. Implement a minimal review-mode extension with the prepared PILOT-01
> (PathOS criterion 1b) as an empty optional future form fixture. Preserve all existing selections and source
> files, isolate tests, reuse Python stdlib/vanilla JS and the shared template. The
> approved base scale is 0/1/2 for calibration; anchors and phase policy remain draft.
> Begin with no judgment selected. Keep NA/uncertainty null, raw human responses and
> immutable submissions/revisions. Do not generate human scores or call a model.
> Mark the pilot deferred, retain blank materials, and do not request or fabricate a
> score, NA or uncertainty judgment. Formal benchmark reviewer assignment remains open.
> Preparation and GUI/software work can proceed without labels. Real independent human
> labels and a frozen protocol are required later for empirical reliability/AI-human
> agreement. Keep any separately authorized technical model smoke tests isolated from
> the reference-review flow; do not tune prompts on final gold labels or claim held-out
> accuracy from diagnostics. No model call is part of this implementation task.
> Record changed files, exact tests/results, limitations and questions in
> research/paired-dmp-study/claude-human-review-results.md. Preserve research reports
> and mark the prototype as pilot support, not completed reference validation.

Deferral update, 2026-11-04: this brief and the review protocol now separate preparation
from future human validation. No pilot response, rating record, model call or production
edit was made in this documentation update.
