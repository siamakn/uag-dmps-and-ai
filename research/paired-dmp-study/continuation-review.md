# Independent review of the continuation

Reviewed 2026-11-03. This supplements the historical [review.md](review.md); it does not replace that report or its earlier scope boundaries. No application, model, dashboard self-test or candidate download was run, and no production data was changed by this review.

## Assessment

The continuation is scientifically useful if framed as a small paired human-versus-DMP-EVA pilot. Use the latest inspected DMP-EVA commit as the baseline, as the user now requests. Differences from the publication and its linked software archive are observations to record, not a requirement to make software and paper converge before evaluation. A changed rubric, repaired implementation or prompt intervention would be a separately identified condition.

Keep the six-project/twelve-document target and same-scope pairing requirement explicit. Neither the historical twelve-project selection nor same-grant records establish the requested cohort. Whole-pool version-family discovery must precede issue-date eligibility checks; repository publication dates cannot exclude families or substitute for document issue dates. Six projects support descriptive pilot findings, not discipline-level estimates or causal effects of project stage.

## Independent checks

The refreshed source cache at `/tmp/dmp-eva-evolution/` establishes the following at its retrieval snapshot:

- `commits/main` identifies `b80b43de820d46440d982eb99b2b3da8f4c2f818`, committed 2026-10-21T08:07:01Z. All ten inspected latest source files match the Git blob identifiers in the pinned tree.
- The tag list identifies v0.1 at `db85e5a71271239f8fbe3e271e4aa8b7e71d6321`. Its GitHub release is a prerelease; `/releases/latest` returning 404 does not establish that no release exists. All ten inspected archived source files match the downloaded ZIP.
- The refreshed preprint and software Zenodo version endpoints each report one version. The PDF and software ZIP are byte-identical to the earlier reviewed copies: SHA-256 `465a894b06bb67abea19acf16eba02dca8d665855a01572a7762ec3bb0e3fc26` and `50be0554e0e79a96c546954365e4e88e129a8c1432c0970b88a9f46f6abd1eb0`, respectively. Unchanged hashes justify retaining the earlier full-source review without repeating it.
- The archive and latest `eva.json`, criteria extractor and export service are byte-identical. The default JSON rubric's absent 3c/5d sections and limited export provenance therefore must not be described as resolved in latest.
- Direct source diffs confirm that archived prompt assembly inserted criterion wording/context, whereas latest uses criterion IDs and omits the automatic wording/context insertion. Latest also changes phase-name handling. These are version differences, not evidence that the archive had the current behavior.
- Latest adds `max_tokens` propagation from the API profile. This narrowly resolves an archived output-cap configuration omission; it does not establish that temperature or seed is sent, or that provider behavior is reproducible.
- Latest introduces the parser's truncation at 30,720 JavaScript UTF-16 code units, rather than bytes or tokens. It is absent from the archived parser. Neither inspected parser has a PDF branch. Keep these two observations separate rather than implying that truncation was a historical limitation fixed by latest.

These checks concern source bytes and static control flow. They do not establish runtime correctness, provider availability, output quality or successful benchmark execution. Immutable URLs and retrieval metadata belong in the companion tool-evolution provenance report.

The new offline version inventory was independently recalculated directly from `data/dmp_dataset.json`, without importing its script. The independent grouping matches 1,234 EU-tier DMP records in 908 stored-grant families, 208 multi-record and 700 single-record, and all 24 primary/all-membership branch-table cells. This confirms internal arithmetic, not external grant correctness or document identity. The historical selection still has SHA-256 `a4a54dba18af7d8a28c1b60e4c317921c7768573735adcd7d44eafa66007edeb`.

## Meeting reconciliation

The actual linked Google Doc text export is readable and contains the scientific discussions summarized below. This independently overturns the earlier access limitation, which remains valid only as historical context. Do not publish the full raw export: it includes personal contact information and meeting access details unrelated to the study.

- The 7 September discussion proposed approximately 100% and below 50% timing. The user's subsequent documented-issue-date rule, early ≤50% and late >100%, controls the current protocol. The strict post-end condition is therefore a later explicit choice, not a quotation from the minutes.
- The 10 August discussion offered two reviewers, a 1–10 scale and their mean as an example. Independent review and adjudication are defensible proposals, but must remain visibly proposed until the team fixes the reference protocol. Preserve initial individual ratings whichever aggregation is chosen; do not silently relabel adjudicated ratings as the meeting's agreed mean.
- The suggested deliberately incomplete DMP can become a separate synthetic stress test. It must not enter the metadata-selected natural-document cohort or be used to force a low-quality case into it.
- The minutes already identify close related work, including Repo et al.'s 2026 LIBER DMP Analyser work and Vandenberk's 2025 thesis. Start the related-work comparison there before claiming novelty. This is a lead from the minutes, not an independent reading of those works.

## Actionable reporting requirements

1. Propagate the latest-baseline decision through README, decisions, plan, source-report orientation, status and Claude handoff. Remove current-tense claims that the tool-version choice is still archived/current/corrected; preserve historical reports with a clear supersession note where needed.
2. Replace current access-failure claims with the successful text-export result and reconcile the relevant scientific decisions. Do not imply that a connected Drive plugin was necessary or used when retrieval succeeded without it.
3. Record discrepancies under the exact version and path inspected. Do not call a change a scientific improvement merely because it is newer, and do not present static fixes as runtime-verified resolutions.
4. Keep native DMP-EVA outputs, missing criterion coverage and human reference judgments distinguishable. A criterion crosswalk supports interpretation; it does not authorize silently filling missing rubric sections, changing the native aggregate, or repairing the baseline before measuring it.
5. Keep the immediate scientific work small: recover version families, verify one candidate pair per branch with evidence, then calibrate a reference protocol on separate examples. The larger platform and model comparison remain supporting work, not evidence of completed selection or validation.

The reviewed [meeting reconciliation](meeting-reconciliation.md) and [software baseline policy](software-baseline-policy.md) implement the principal methodological corrections: source access is resolved with a bounded export scope; historical suggestions remain distinct from confirmed choices; latest is pinned per campaign; native and modified conditions remain identifiable; tool/publication convergence is not imposed. The inventory report also correctly distinguishes its internally confirmed stored-grant consistency check from independent association verification.

The final [tool-evolution report](tool-evolution.md) agrees with the independent source checks above. Its “persists” status is explicitly relative to the prior latest-source inspection, while its only “resolved” status is narrowly limited to output-cap propagation from the archive. This avoids falsely attributing current behavior to the archive or claiming runtime validation.

## Bounded humanities source check

The [first humanities batch](humanities-batch-01.md) was checked against all four cached PDF extractions, the rendered E-RIHS D1.2 version-history page and DIAMAS D1.5 version-history page, and the three cached CORDIS fact sheets. The report's central conclusions withstand this check:

- HeriTACE's CORDIS end is 2027-12-31, so an issue dated by 2026-11-03 cannot satisfy strict post-end eligibility against that snapshot.
- E-RIHS D1.2 describes project data, whereas D5.2 describes infrastructure/ERIC data. Common same-scope revision lineage is not established. The inspected issue-log dates are 2023-06-02 and 2024-06-12; the conflicting D1.2 actual-delivery field is correctly retained rather than substituted silently. Neither issue log establishes a post-end endpoint.
- DIAMAS D1.5 explicitly identifies itself as an update of D1.1. Its October 2023 created/modified label and the original October 2022 label support a version sequence, while remaining distinct from explicitly labelled issue dates. Both complete calendar-month intervals precede the recorded project end. Their invalid cover end date is correctly flagged. The Update 2 cache begins as HTML rather than a PDF, so its contents and date remain unknown.
- Independent day arithmetic confirms `244/822`, `620/822`, `30–60/1095` and `395–425/1095` and the displayed percentages. The two DIAMAS PDFs have different bytes.

Thus “no qualifying post-end same-scope pair verified in this batch” is supported; “no humanities pair exists” would not be. The failed version/search requests and unreviewed extension histories appropriately limit the report. Recovering DIAMAS Update 2 is a concrete next retrieval task, not evidence that it qualifies.

The remaining substantive uncertainty is cohort feasibility under issue dates and same-scope lineage. No valid six-pair cohort, human reference dataset, runtime validation or generalization across disciplines is established by this continuation review.
