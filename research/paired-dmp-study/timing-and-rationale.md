# Timing rule and scientific rationale

2026-11-03. User-confirmed issue-date rule; implementation and final selection remain future work. The rationale below is a proposed study justification, not a claim of established validity or global novelty.

## Exact definition

Let **S** be the project's authoritative start date, **E** its authoritative end date, and **D** the documented issue date of the specific DMP version. For E > S:

`project_position_percent = 100 × elapsed_calendar_days(S, D) / elapsed_calendar_days(S, E)`

Use elapsed days, without adding one to either interval, and retain the integer numerator and denominator. This percentage describes **temporal position relative to the recorded project duration**. It is not the percentage of work completed, funding spent, DMP completeness, or scientific quality.

- Early sampling window: `0 ≤ project_position_percent ≤ 50`. The user accepted ≤50%; exclusion of pre-start versions is the proposed operational boundary and should be explicitly confirmed before freeze if any such candidate matters.
- Later sampling window: `project_position_percent > 100`, strictly. This means a version issued after the chosen project end date. Exactly 100% does not qualify.
- No tolerance around 50% or 100% is implied by rounding. Show rounded values, compare exact values.

For an illustrative project running from 2024-01-01 to 2025-01-01 (366 elapsed days), a DMP issued 2024-07-02 is at 183/366 = 50%; one issued 2025-01-01 is at 100%; one issued 2025-01-02 is at 367/366 ≈100.273% and meets the later date criterion. These examples illustrate arithmetic, not candidate documents.

## Evidence and uncertainty

Use the issue date explicitly tied to that revision in its cover, revision table or equivalent authoritative document metadata. Save the page/section or JSON field, original date string, precision and source URL. Resolve contradictory dates rather than picking whichever makes the document qualify. A scheduled deliverable deadline is not proof of actual issue. A revision table date must refer to the selected revision, not a copied original date.

Retain repository publication, creation/update and retrieval dates as distinct fields. They can support discovery and expose delayed deposition, but cannot replace issue date under the accepted rule. If issue date cannot be evidenced, mark timing unresolved. Two files uploaded on different dates can contain the same version; two versions can be deposited on the same date.

For month/year dates, represent the whole valid interval. Assign a stage only if every possible date satisfies the same threshold; otherwise request better evidence or leave it indeterminate. Apply the same caution to uncertain project dates. A malformed date remains invalid, not an interval invented by the agent.

Project extensions can move a DMP from above to below 100%. User-confirmed policy (D09): use the latest authoritative project end date, including extensions, at the frozen evidence snapshot; retain original dates and extension evidence and show sensitivity calculations where eligibility changes. Do not confuse administrative end with scientific work completion or infer an end date from the DMP itself. Fix a search cutoff and use only documents issued and accessible by it; reject future-dated anomalies until resolved.

## Why sample this way?

Normalizing by duration makes the timing criterion comparable across projects of different lengths. Matching versions within the same project and DMP scope reduces differences in topic, consortium and obligations that would arise from comparing unrelated plans. Six different discipline branches deliberately broaden the test cases.

The first-half window samples documentation produced while substantial project time remains. The strict post-end window samples documentation issued after the recorded project duration has elapsed. This operational contrast is transparent and reproducible, but **does not by itself establish that a document reports finalized practice**. Verify revision identity and scope separately. Do not assume a later issue is a “final” DMP solely from its date.

The ≤50% and >100% thresholds are this study's sampling convention. They are not thresholds established or validated by the [Mansour et al. framework](https://doi.org/10.5281/zenodo.19630859). The framework describes stage-sensitive expectations, while a DMP at 45% may already be reporting implementation. Therefore the numerical sampling bin and the DMP-EVA rubric phase must be stored separately. Decide their mapping before human or model scoring; do not automatically route every ≤50% document to proposal-stage prompts.

The strict >100% condition excludes final DMPs issued on or shortly before the end date and may favor delayed reporting, public deposits, or projects with certain release practices. Report that selection bias. If six valid pairs cannot be found, document the gap and ask whether a near-end comparison should be a separate sensitivity cohort; do not silently broaden the primary rule. Age/programme differences and document format may still confound a small paired study.

## Proposed study questions

1. How closely do DMP-EVA's criterion-level assessments agree with independent, adjudicated human assessments under a frozen rubric and explicit applicability rules?
2. Within the same project and DMP scope, do the tool's disagreements, missed evidence and unsupported claims differ between the two sampled times?
3. How sensitive are these findings to model backend and prompt structure, holding document input, rubric and the rest of the pipeline fixed?
4. Which errors arise from extraction, missing rubric content, phase handling, score aggregation or model judgment? Distinguish these before attributing differences to a model.

Primary outcome and score mapping must be fixed after rubric calibration. Proposed primary reporting is criterion-level human/tool agreement and discrepancy counts; a 0–100 overall score is secondary until its interpretation and aggregation are justified. The same project's two versions are dependent observations. Six projects cannot estimate general discipline effects; repeated model runs and many criteria do not increase the number of independent projects.

## Potential scientific and community value

- **A reusable, traceable paired benchmark:** version-family evidence, exact lifecycle dates, source identifiers and exclusions let others reproduce selection and compare later tool releases without selecting polished DMPs.
- **Evidence about stage-sensitive evaluation:** a documented human reference can show where a tool mistakes planned actions for completed practice, overlooks acceptable inapplicability, or makes claims unsupported by the document. Later versions need not score higher; the reference is human assessment, not monotonic improvement.
- **Actionable DMP-EVA development evidence:** separating extraction, prompt, rubric, phase and aggregation issues from model judgment directs improvements and enables regression tests on a versioned evaluation set.
- **Reusable material for the AI/DMP subgroup and NFDI:** a criterion crosswalk, reviewer instructions, evidence-linked annotations and an error taxonomy can support training and discussion across consortia. Relevance to NFDI does not demonstrate generalization to German-funded DMPs; this is an EU-funded open-document sample.
- **A credible pilot publication:** a transparent protocol, independently reviewed human labels, uncertainty and negative findings can support a methods/case-study contribution. Novelty must be checked through a separate related-work search; the supplied preprint alone does not establish that no similar benchmark exists.

The local platform changes are infrastructure for these outputs, not the scientific contribution by themselves. Useful release outputs are a protocol, cohort manifest, permitted source files or resolvable links, extraction provenance, rubric and adjudication records, full run specifications, results and explicit limitations.

## Draft methods wording

> We designed a purposive paired case study comprising six projects, one assigned to each of six broad EuroSciVoc disciplines. For each project, we sought two distinct versions of the same-scope DMP. Temporal position was defined as elapsed calendar days from the project start to the documented DMP issue date divided by elapsed calendar days from project start to end. The earlier version was required to fall within the first half of the project and the later version after its recorded end. Repository publication dates were retained as provenance and were not substituted for issue dates. Selection used project and document metadata rather than assessed DMP quality. This operational timing contrast does not measure project completion or establish that later versions are higher quality.

This paragraph describes the design, not a completed sample. After selection, report actual numbers screened, exclusions, unresolved cases, date-source and extension policy, language restrictions and any deviations; do not present a planned twelve-document set as achieved.
