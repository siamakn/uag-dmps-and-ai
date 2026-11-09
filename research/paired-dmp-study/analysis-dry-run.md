# Synthetic analysis dry run — draft arithmetic only

Prepared 2026-11-06. **All labels and identifiers are artificial. This is neither a
human reference nor scientific results, and it approves no analysis plan.** No
source PDFs, actual reference labels, selections, prompts or model endpoints are
consumed. This local preparation follows the candidate analysis in
[experiment-protocol-draft.md](experiment-protocol-draft.md) and
[experiment-matrix.json](experiment-matrix.json). Existing research/platform files
are unchanged by this task.

Run with Python 3.7+ and the standard library:

```bash
python3 research/paired-dmp-study/analysis-dry-run-test.py
python3 research/paired-dmp-study/analysis-dry-run.py --example
python3 research/paired-dmp-study/analysis-dry-run.py --input /tmp/synthetic-fixture.json --output /tmp/synthetic-result.json
```

The example is built into [analysis-dry-run.py](analysis-dry-run.py); no fixture
file or saved scientific-looking results are needed. The program has no network
code. Without `--output`, it prints JSON. Explicit output paths are written only
when supplied; use a new synthetic result path.

## Internal synthetic input contract

This narrowly scoped JSON contract exercises analysis arithmetic. It is **not a
replacement human-review schema, production adapter or execution log**. Adaptation
of eventual real records remains pending.

- `notice` must equal `SYNTHETIC_ONLY_NOT_HUMAN_REFERENCE_NOT_SCIENTIFIC_RESULTS`.
- `repeat_count` must be integer `1`. Booleans, floats and other repeat counts fail;
  there is no implemented R>1 estimator.
- `projects` explicitly anticipates exactly six unique synthetic projects, each
  with exactly one `early` and one `late` document. Each document declares its
  `defined_criteria` independently of observed output. A nonempty `criteria` roster
  anticipates every criterion for every document. Project/document/criterion IDs
  all start `SYNTHETIC_`; none corresponds to actual projects or rubric criteria.
- `reference` must contain exactly one row per anticipated document × criterion,
  including non-score and undefined cells. Omitting a reference row fails validation.
- `models` contains only F0/F1 rows for those anticipated cells; omitted model rows
  become `missing_model_row` on defined cells. Undefined cells remain undefined,
  even if no model row is supplied. Duplicate or unknown rows/fields fail.
- Every row contains `document`, `criterion`, `applicability`, `state`, `value`,
  `reason`; model rows also contain `condition`. `applicability` is `applicable`,
  `NA`, `unknown` or `instrument_undefined`. `state` is `score`, `NA`, `uncertainty`,
  `missing`, `failure` or `instrument_undefined`. A score requires applicable status,
  an integer 0/1/2 (excluding booleans/floats) and an empty reason. Other states require
  JSON null and an explicit reason. NA and instrument-undefined states require
  matching applicability; uncertainty/missing/failure can have known applicable
  or unknown applicability. Undefined states must match the anticipated mask.

A human-applicable but uncertain/missing numeric judgment stays in the fixed
coverage denominator. It cannot enter numeric agreement. Unknown human applicability
has its own count/audit and cannot be asserted applicable. This distinction avoids
silently treating every unavailable human rating as inapplicable.

Native N0 and 0–100 scores are rejected. Duplicate JSON object keys, NaN and Infinity
are rejected by the CLI. No real human labels are created or adapted.

## Proposed arithmetic exercised

For document d, define C(d) using the intersection of instrument-defined,
human-applicable rows with numeric human, F0 and F1 judgments. For condition c:

`e(c,d) = count(model label != reference label on C(d)) / count(C(d))`.

Compute each document contrast `e(F1,d) - e(F0,d)`. Average its two document
contrasts equally within each project, then average all six project contrasts
equally. Genuine numeric zero participates normally. A document with no common
numeric rows is undefined; its project and the required six-project result are
undefined with explicit reasons. The implementation never drops a required
project/document or replaces missing labels with zero.

The result is conditional numerical agreement on the observed common set. Negative
contrast denotes less F1 exact disagreement on that set; it establishes no ranking,
superiority, unconditional accuracy or population effect. No inference, kappa,
bootstrap, p-value or human quality aggregate is computed.

Mandatory companion outputs accompany every synthetic contrast:

- Common numeric coverage and condition-specific numeric coverage on the fixed
  human-applicable, instrument-defined denominator, including per-document and
  per-project counts. Project coverage pools counts descriptively; it never weights
  the primary project/document means.
- All anticipated/supplied row counts, state counts, fixed-denominator exclusions
  and reasons by condition; absent rows cannot shrink the roster.
- Applicability disagreement on jointly determinate applicability states, with
  its own denominator; human NA/model numeric and human numeric/model NA counts
  are explicit. Unknown applicability is unassessed, not automatic disagreement.
- Reference state/applicability totals, condition-specific nonnumeric audit rows,
  and the complete common-analysis exclusion table showing human/F0/F1 states and
  reasons. A valid F0 numeric row excluded solely because F1 is missing is visible
  in this common-analysis audit.

Row availability is not a request-attempt/completion count. Those run-log summaries
remain unimplemented because no request log is part of this arithmetic fixture.
The output explicitly lists this limitation. The synthetic failure reason field
can preserve transport, provider/context, refusal, parse/schema, input/rights or
other named failure causes; it does not infer request history or retry outcomes.

## Observed local verification

`python3 research/paired-dmp-study/analysis-dry-run-test.py` passes **16 tests**,
including parameterized rejection cases. Hand-calculated checks include:

| Artificial scenario | Expected arithmetic |
| --- | --- |
| Built-in all-zero reference; F1 differs on one of three criteria in one early document | Document +1/3; project +1/6; six-project contrast +1/36; common coverage 36/36 |
| First project early document has one common row, contrast +1; late has three, contrast −1/3; all other documents zero | Project +1/3; six-project contrast +1/18, while pooled criterion difference is zero |
| Omit the only erroneous F1 row | Conditional contrast becomes 0, but F1 coverage is 35/36; missing count/reason and common-mask exclusion remain visible |
| Omit all F1 rows from one document | Required project and six-project contrast undefined; denominator remains 36 |
| Omit every model row | All six required projects undefined; each condition has coverage 0/36 |

Additional checks cover genuine zero, both NA disagreement directions,
applicable-but-nonnumeric references versus unknown applicability, undefined
instrument cells, distinct failure/missing/uncertainty counts, negative contrast
sign, permutation invariance, empty rosters, missing/duplicate/unknown records,
bool/range/type errors, contradictory dispositions, unsupported repeats, and CLI
JSON parsing/output.

## Remaining decisions and scope

These checks verify arithmetic and validation, not the scientific validity of the
estimand. Before real use, the comparison mask and undefined-handling policy,
benchmark anchors/phase/crosswalk, human-reference process, condition definitions
and full analysis must still be approved and frozen. The observed common-set mask
is the protocol's current candidate, not a newly approved policy. Differential
missingness may change the conditional contrast even when missingness is exposed.
No model execution or current human task follows from these files. No native-score
mapping, repeat extension, request-log adapter or real-record adapter is approved
or implemented here.
