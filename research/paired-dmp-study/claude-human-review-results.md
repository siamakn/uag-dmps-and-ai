# Human-review pilot support — implementation results

Implemented 2026-11-09 by Claude (Opus 5.5) from
[`claude-human-review-brief.md`](claude-human-review-brief.md).

**This is pilot support, not completed reference validation.** No human judgment, score,
NA or uncertainty disposition was created. No model was called. The pilot remains
**deferred** by the user's 2026-11-04 decision (D14), and no new pilot request was issued.
The form is blank until a person chooses to use it.

## What was built

A third dashboard mode, **Review (pilot)**, next to *Paired study* and *Legacy 3×3*. It uses the
same template, theme, tooltip system and served/standalone patterns, with Python stdlib and
vanilla JavaScript only.

| file | change |
|---|---|
| `scripts/review.py` | **new.** Builds the PILOT-01 task from `pilot-template.json`; the draft anchors are parsed verbatim from `pilot-start.md`, and the source and framework PDF hashes are checked against the template. Also: a stdlib JSON-Schema subset validator that applies `human-review-record.schema.json` itself, pilot cross-field checks, content hashing, draft-file storage and append-only record storage (O_EXCL). Module and CLI. |
| `scripts/test_review.py` | **new.** 15 unittest classes/cases plus the generator for `dashboard/review-fixtures.json`. |
| `dashboard/review-fixtures.json` | **new.** A synthetic, clearly labelled test record, 31 validity cases, and SHA-256 vectors. Shared by the Python and JavaScript tests. |
| `dashboard/template.html` | Review mode: status, source, rubric cell, scale and anchors panels; the form; Save draft / Preview response / Submit pilot response / Export / Discard draft; typed confirmation; records list with "Start a correction". Also a JavaScript copy of the validator, pure-JS SHA-256, a `__REVIEW__` boot block, and a Guide paragraph. |
| `dashboard/selftest.js` | Review tests (DOM clicks, both modes), the review draft added to the two-phase reload check, and storage restore extended to a list of keys. |
| `scripts/serve.py` | `GET /api/review`, `PUT /api/review/state`, `POST /api/review/submit`, `POST /api/review/validate`, `GET /api/review/source/<artifact_id>` (whitelisted PDFs only). |
| `scripts/05_build_dashboard.py`, `scripts/common.py` | Fill `__REVIEW__`; inject the review fixtures into test builds only. |
| `dashboard/dashboard.html` | Regenerated from the template. |
| `AGENTS.md`, `scripts/README.md`, this directory's `README.md` | Documented. |

## How it behaves

- **Status**: the pilot is shown as *Deferred — nothing needed now*, never as overdue, failed or
  assessed. Deferral creates no draft and no record. A voluntary submission is counted separately
  ("1 voluntary response submitted"), and the deferred status stays.
- **Source**: links to the full PathOS PDF (102 pages; SHA-256 shown) and to the framework at
  physical page 8 (`#page=8`), plus the public record and publication. Served mode serves both PDFs
  through a whitelist; standalone uses relative paths. No extraction is shown. The record's
  canonical full-text artifact is the PDF itself, because no text extraction exists for the
  calibration document, so a shortened text cannot silently become the packet.
- **Scale and anchors**: 0/1/2 (approved for calibration) with NA and uncertain as separate
  null-score states. The five draft anchors are quoted from `pilot-start.md` and labelled as drafts.
  The page states that no AI rating, quotation or expected answer is supplied, and none is.
- **Form**, in ordinary language:
  - assessment, starting at *Not assessed yet*, with options 0, 1, 2, NA, Uncertain, Withhold;
  - applicability and its reason;
  - what the document shows (the evidence state);
  - evidence entries: physical page, printed page, section, optional excerpt, note;
  - whether the search was complete, and what was searched;
  - reasoning, confidence and the reason for it, other uncertainties;
  - prior familiarity;
  - three independence questions (model output, other reviewers' labels, other versions seen);
  - usability feedback;
  - the response in the reviewer's own words, kept verbatim beside the record.
- **Drafts** keep exactly what was entered; empty stays empty. Served drafts go to
  `data/review/review_state.json`; standalone drafts to the browser key `dmpbench.review.v1`.
- **Before submission**, a live list explains every missing item and inconsistency, for example:
  - a 2 or 1 with the wrong evidence state, or without an evidence entry;
  - a 0 without a completed search or a search note;
  - NA while applicability says "applies";
  - a numeric score with an "unreadable" or "unsure" evidence state.

  Nothing is coerced.
- **Submit**: the response is checked first. The reviewer then types `R-PILOT-01` to confirm, and
  the record is built to the schema, hashed (canonical JSON, SHA-256) and stored once:
  - served: `data/review/records/<id>.json`, created with O_EXCL; the server re-validates the record
    and its hash;
  - standalone: `dmpbench.review.v1.record.<id>`, written only if the key is absent.

  A one-criterion submission needs no recruited benchmark reviewers.
- **Corrections**: "Start a correction" prefills a draft from the reviewer's own record. Submitting
  it creates a new record with `supersedes_record_id`. The original stays byte-identical and is
  shown as superseded.
- **Errors**:
  - an unreadable or unsupported draft file blocks the form with an explanation, and is set aside
    (never overwritten) only when the reviewer chooses to start over;
  - unreadable record files are listed and left in place;
  - a submission that would overwrite a stored ID is refused (409 when served).

## Tests run and results

Environment: Linux, Python 3.14.4, Google Chrome headless, isolated storage throughout.

```bash
python3 scripts/test_review.py                    # Ran 15 tests ... OK  (incl. 31 fixture cases)
python3 scripts/test_paired.py                    # Ran 33 tests ... OK
python3 scripts/05_build_dashboard.py --selftest $TMP/st.html
google-chrome --headless=new --user-data-dir=$TMP/p --dump-dom "file://$TMP/st.html"
#   SELFTEST 387/387 fail=0 skip=2   (the 2 skips are server-only API checks)
google-chrome --headless=new --user-data-dir=$TMP/p --dump-dom "file://$TMP/st.html?phase=reload"
#   SELFTEST 4/4 fail=0 skip=0       (paired and review drafts survive a real reload)
python3 scripts/serve.py --test --no-open --port 8795
google-chrome --headless=new --user-data-dir=$TMP/q --dump-dom "http://127.0.0.1:8795/selftest"
#   SELFTEST 409/409 fail=0 skip=0
google-chrome --headless=new --user-data-dir=$TMP/q --dump-dom "http://127.0.0.1:8795/selftest?phase=reload"
#   SELFTEST 4/4 fail=0 skip=0
```

After all runs, `data/selection.json` still hashes to
`a4a54dba18af7d8a28c1b60e4c317921c7768573735adcd7d44eafa66007edeb`, and `data/review/` does not
exist (`python3 scripts/review.py list` → "no submitted review records"). The test records were
written only to temporary directories and to a throwaway browser profile.

The brief's acceptance checks, as tested (DOM clicks unless noted):

| check | result |
|---|---|
| untouched form has no score | the preview shows `value: null`, `entry_status: not_entered`; "not assessed" is checked |
| explicit zero survives save/export | 0 survives save + reload as the number 0, and appears in the export |
| partial distinct from zero | 1 is stored as 1 with "partly evidenced" |
| NA / uncertain stay null | `value: null` with the original label kept (`"NA"`, `"uncertain"`) |
| absent pages/rationale kept as missing | they survive reload as `""` / `[]` and are listed as missing; nothing is invented |
| inconsistencies explained before submission | a 2 with "not reported", and a 0 without a completed search, are both explained and blocked |
| draft reload lossless | save → reload round trip, plus a real two-page reload in both modes |
| submitted record cannot be overwritten | refused by the client, the server (409) and browser storage; the stored bytes are unchanged |
| corrections retain the original | a second record has `supersedes_record_id`; the original is byte-identical and shown as superseded |
| single-criterion submission without recruited reviewers | stored as a `pilot_calibration` record from R-PILOT-01 |
| deferral creates no rating and blocks nothing | no draft or record at start; the paired and legacy modes keep working |
| served and standalone persistence tested separately | both suites run, each with its own reload phase |
| Python and JS agree | 31 fixture cases in both languages, plus the served `/api/review/validate` comparison; the JS content hash equals the Python hash; a JS-built record is accepted by the Python server |
| every control has `data-tip` | asserted, including the confirmation box |
| historical selection byte-identical | asserted in both Python suites |

## Validation coverage, and what remains for benchmark mode

Enforced now, for pilot records:
- the full JSON Schema (draft 2020-12 keywords used by the file: `$ref`, `allOf`, `anyOf`,
  `if`/`then`, `const`, `enum`, `type`, `required`, `properties`, `additionalProperties`,
  `items`, `min`/`maxItems`, `uniqueItems`, `minLength`, `pattern`, `minimum`/`maximum`,
  `date-time`);
- the pilot rules beyond the schema:
  - the scope equals the criterion rows, and a single-criterion pilot has exactly one row;
  - every row belongs to the declared instrument;
  - every artifact reference resolves;
  - text offsets are well formed;
  - a locked record contains no "not entered" score;
  - the content hash matches;
  - `supersedes_record_id` names a stored record;
  - IDs are unique, and locked records are immutable.

Not implemented; needed before benchmark (cohort) records:
1. Complete criterion coverage for full assessments: 16 unique framework rows, or the declared
   instrument's exact IDs, including an `instrument_undefined` row for mid-project 5d.
2. Offset validity against the hashed canonical text artifact. Only well-formedness is checked
   now, because the pilot cites pages, not offsets.
3. Independent reviewer allocation: two distinct assigned reviewers (R1/R2) per document, an
   adjudicator, and no reviewer seeing the other's labels or model outputs before lock.
4. Adjudication links: at least two original independent records for the same document and
   criterion, with both stored, unresolved criteria kept, and originals untouched.
5. Presentation-order randomisation, masking and recording of familiarity across the 12 documents
   (pair versions kept apart).
6. Benchmark approvals (`approved_for_benchmark` scale, frozen anchors and phase mapping). The
   schema already gates locked cohort records on these, but this mode accepts only
   `pilot_calibration` records.
7. Human-human disagreement metrics, computed before reconciliation.

## Limitations

- The form records one criterion for one task. Further tasks would need entries in
  `review.py:boot()`: the AD4GD dual-phase calibration conditions prepared under D15
  (`dual-phase-calibration.json`), or cohort documents. Those need assigned reviewers and the
  benchmark rules above, so they were not added.
- The schema requires a non-empty `confidence_reason` even for "prefer not to say", and an
  `applicability_reason` even when the criterion applies. The form asks for both rather than
  inventing text.
- `relevant_packet_search_completed` is a boolean in the schema. The form's *Unsure* answer is
  stored as `false`, plus the uncertainty line "Reviewer was unsure whether the criterion-specific
  search was complete."
- Standalone records live only in that browser's storage. Browser storage is append-only by code
  convention, not by an operating-system guarantee; use served mode for records meant to be kept.
- The JavaScript validator covers the keywords the current schema uses. A schema change that
  introduces other keywords needs both validators extended; the fixtures will show the gap.
- No accessibility audit beyond keyboard-reachable native controls and labels was done.

## Decisions taken with the user (2026-11-09)

1. **Pilot records stay local.** `data/review/` is git-ignored because the repository is public and
   the responses are personal calibration judgments. Export them deliberately if needed.
2. **Schema unchanged for the pilot (D21).** The current mapping stays: a confidence reason is always
   required, and "unsure" search answers are stored as `false` plus an uncertainty note.
   Revisit after real pilot feedback.
3. **DMP-EVA brief left for now (D22).** The native tool stays unchanged as the baseline.
4. **This work is added to PR #1**, together with the paired-study platform.

Still open, waiting on reviewer recruitment rather than on a question: whether the AD4GD dual-phase
calibration conditions (D15) become review tasks. They need assigned reviewers and the benchmark
rules listed above.
