# Independent review of the synthetic analysis dry run

Reviewed 2026-11-06. **No blocking defect was identified in the reviewed synthetic arithmetic and validation.** The program implements the draft R=1, F1-minus-F0 project-balanced exact-disagreement calculation and exposes its coverage and missingness limits. This is software verification using artificial labels, not an executed benchmark, a human reference, an approved estimand or scientific evidence favoring either condition.

Scope: [implementation](analysis-dry-run.py), [tests](analysis-dry-run-test.py), [method report](analysis-dry-run.md), and the candidate analysis in [protocol](experiment-protocol-draft.md) and [matrix](experiment-matrix.json). The built-in fixture supplies six artificial projects, twelve artificial documents and three artificial criteria. There is no separate saved fixture/result artifact to review. This review adds only this report; no existing research or platform source was edited. No source PDF, real score, network request or model execution was used.

## Arithmetic and independent checks

Code inspection confirms that each document uses the same intersection of defined, human-applicable, numeric human/F0/F1 rows for both disagreement rates. The two document contrasts receive equal weight within a project; all six project contrasts receive equal weight in the main result. Criterion counts and pooled coverage counts do not weight that result. A genuine numeric zero is retained.

A document with no comparable criteria has a null contrast. Its project and the required six-project result also remain null; averaging the other document or the five remaining projects is not allowed by this prototype. The complete anticipated roster is validated independently of the available model rows, so an absent condition cannot remove a document or project.

An independent fixture was constructed from scratch without using the program's example generator. Hand calculations and observed output agreed:

| Artificial scenario | Independently checked result |
| --- | --- |
| All human/model values are numeric zero | Main contrast 0; common coverage 36/36 |
| First project: early contrast +1 on one criterion; late contrast −1/3 on three criteria; remaining projects 0 | First-project contrast +1/3; main +1/18, although the pooled criterion contrast is 0 |
| Swap F0/F1 labels in the preceding fixture | Main contrast −1/18 |
| One project has contrast +1 in both documents; remaining five projects 0 | Main contrast +1/6 |
| All F1 rows absent | Six projects and twelve documents remain; main contrast null; 36 F1 missing rows retained |
| One human-applicable reference row has uncertainty instead of a number | Common coverage 35/36; fixed denominator remains 36 |
| Human NA with a numeric model judgment | Applicability disagreement counted; that row does not enter the human-applicable numeric denominator |
| F1 fails where human/F0 are numeric | Common-exclusion audit retains both the valid F0 row and F1 failure |
| All reference rows NA, or all instrument cells undefined | Main contrast and zero-denominator common coverage are null, never zero |

Eleven additional malformed mutations were independently rejected, including boolean/float/nonfinite scores, contradictory applicability, unsupported repeats, missing project/reference rows, duplicate model rows, native N0 and unexpected fields. Both Python files parse under Python 3.7 syntax rules. This is a syntax check, not execution under a Python 3.7 interpreter.

The supplied command passed **16 tests**, including parameterized rejection cases:

```sh
python3 research/paired-dmp-study/analysis-dry-run-test.py
```

Its CLI tests cover JSON input/output, duplicate object keys, NaN/Infinity and malformed input. A separate final `--example` invocation matched the function result exactly. Final per-project coverage denominators and reference-applicability totals were also checked.

## Missingness and validation findings

Two issues identified in the initial implementation were corrected before this verdict. Applicability is now explicit rather than inferred from the existence of a numeric human score. A known human-applicable but uncertain/missing numeric rating stays in the fixed human-applicable, instrument-defined coverage denominator; unknown human applicability is separately counted. The common-primary exclusion table now includes reference/F0/F1 states and reasons, including a valid F0 row excluded because F1 is nonnumeric.

The reviewed output separates the conditional numeric contrast from its mandatory companions: common and condition-specific coverage, state/reason counts, applicability disagreement on jointly known states, both directions of human/model NA disagreement, and row-level exclusions. In particular, human NA/model numeric mismatches remain visible even though they fall outside the fixed human-applicable denominator. Unknown applicability is not automatically called disagreement. Undefined instrument cells remain distinct from NA, failure and a genuine zero.

Complete reference rows are mandatory; omitted model rows become explicit missing rows on defined cells. Undefined cells are determined by the anticipated mask, including when no model row is supplied. Six-project/two-document structure, unique identifiers and rows, allowed fields, integer 0/1/2 scores, null non-scores with reasons, and disposition consistency are validated. R>1 and native N0 are rejected; no repeat or native-score aggregation is silently introduced.

## Interpretation and remaining work

The method report accurately identifies the implementation as an internal synthetic contract, not an adapter for real human assessments or model execution logs. It correctly declines to infer scheduled/attempted/completed request counts from row availability. Failure reasons are preserved, but their truth and request histories cannot be verified by this arithmetic program.

The common numeric mask is conditional on observed output. The supplied missing-row test illustrates why coverage is mandatory: removing the only erroneous F1 row changes the conditional contrast to zero while reducing F1 coverage to 35/36. Reporting both quantities exposes that mechanism; it does not eliminate selection bias or establish unconditional accuracy. Project coverage pools counts descriptively while the main contrast keeps equal document/project weights.

Before real use, the estimand, comparison mask, undefined-handling rule and full analysis still require approval and freeze. Final human anchors, phase assignment, semantic crosswalk, native-score mapping if ever proposed, real-record/run-log adapters and independent human reference judgments remain pending. This review approves none of those decisions, creates no human task, and establishes no model ranking, population accuracy, stochastic stability or inferential claim.

## Reviewed identities

SHA-256 values at review:

| Artifact | SHA-256 |
| --- | --- |
| `analysis-dry-run.py` | `81caca0ac16481714a13306d878ce2ffb9f53325ea9d469984d575353763cb94` |
| `analysis-dry-run-test.py` | `85f70786f65b2418aabce187a5f6b6bb149f9ea2e15582dd5605f1c3180e3423` |
| `analysis-dry-run.md` | `fc23ac4b1b4ff4693482d7687347d8f2b1869fda3876b07b3b35d64442716c07` |
| `experiment-protocol-draft.md` | `3d2ea9c7d69b470d2b7512119513fbe19022de0eef8a3904c431822f96b744a6` |
| `experiment-matrix.json` | `5ad513c11400704dc3e8abf627d583d2340ca613a01c411a9e4024fffbf54f10` |

Later changes require checking the affected claims again.
