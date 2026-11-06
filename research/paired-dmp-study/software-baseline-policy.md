# Software baseline and discrepancy policy

User-confirmed continuation decision, 2026-11-03: work with the **latest DMP-EVA version**, record its immutable identity, compare it with the publication-associated software state, and document whether previously identified differences have been resolved. Publication/tool convergence is not a prerequisite for a useful study.

## Baseline rule

At the start of an experimental campaign, resolve the latest upstream default-branch commit and record the full SHA, commit time, source tree, retrieval time, release/tag if any, exact configuration, rubric, prompt and dependency identities. A release label alone is insufficient where newer development exists. The current live check and baseline are recorded in `tool-evolution.md` and `tool-evolution.json`.

“Use latest” means latest verified when the campaign is frozen, not a moving target during its runs. Discovery can proceed against the current pinned baseline. Before model execution, check upstream once more. If it changed, append the change and review its relevance before freezing. Once execution begins, use the same pinned code and configuration throughout comparable runs. A subsequent upstream change becomes a separate dated campaign or explicitly reported sensitivity experiment.

Keep the publication's exact record/version/PDF hash and its linked software archive/tag/commit separately. If a paper does not explicitly name a commit, say so; mapping its software link to a tagged commit is a provenance reconstruction, not a quotation from the paper. Record any later publication revisions without silently replacing the source originally used.

## Discrepancy register

For each finding, retain:

- The expected behavior or statement, with publication page/section or software documentation locator.
- The actual source behavior and immutable code location, configuration/path and affected version.
- Evidence type: static inspection, controlled local test or observed inference result. Static inspection is not runtime validation.
- Latest status: persists, resolved, changed, uncertain or not comparable; include evidence supporting that status.
- Possible scientific effect, known limits and whether it affects input, rubric, stage, scoring, output or reproducibility.
- How the study handles it: report native output, add a separately labelled diagnostic, configure an existing feature, or evaluate a changed implementation in a distinct condition.

Do not label every difference a defect: the framework may intentionally cover more than one software configuration, and settings may change behavior. Distinguish explicit contradiction, undocumented divergence, implementation limitation and untested hypothesis. Do not claim an upstream resolution solely because a commit message says “fixed”; inspect or test the relevant path.

## Working with a divergent implementation

The primary target is the pinned latest upstream implementation under an explicit configuration. Preserve its native outputs and errors. Document the tool's actual rubric and score aggregation. Human/tool comparisons must have a declared crosswalk for shared criteria, with missing criteria and unscored evidence visible rather than treated as equivalent judgments.

Do not silently modify code, inject missing criteria, change phase identifiers or recompute totals and call the result the unchanged tool. Existing supported custom-prompt/rubric settings may be studied, but their full content and purpose must be recorded as a specific configuration. An independently recomputed score is a diagnostic result and must be shown separately from the native score. A corrected-code experiment, if useful and authorized later, gets its own commit and condition.

Some findings can be measured as limitations of the latest tool; others may prevent a planned condition from running or make a comparison uninterpretable. Resolve that distinction through a small preflight on documents outside the final cohort. If a path cannot execute, report failure for that condition and decide whether an explicitly labelled alternative is scientifically useful. Do not require all differences to be repaired before discovery, reference-label preparation or descriptive evaluation can progress.

No upstream issues, emails or other external communications are sent by this policy. The register can support a later human-approved report to developers.
