# DMP-EVA: changes to consider after the native baseline

Prepared 2026-11-04 for maintainer/Claude review. This is a concrete improvement brief,
not a patch, an upstream issue submission or permission to relabel changed behavior
as the unchanged tool. It concerns the evaluation tool, separately from the local
selection-dashboard brief.

Evidence: [tool-preflight.md](tool-preflight.md) and its reproducible harness exercise
the actual functions at commit `b80b43de820d46440d982eb99b2b3da8f4c2f818` without model
requests. All 44 assertions confirm the reported behavior, including limitations.
The paper-associated archive and current code are compared in tool-evolution.md.

## Priorities and acceptance criteria

| Priority | Observed trigger and effect | Proposed change and reviewable acceptance criterion |
| --- | --- | --- |
| 1 | Loading the default 14-ID rubric does not insert its names/descriptions into the assembled prompt. | Make effective criterion definitions and intended stage wording explicit in the submitted prompt. Test that unique criterion/context markers survive assembly, and archive the exact prompt and rubric hash. Keep the native prompt as a separate baseline condition. |
| 1 | UI short phase names and batch long names are interpreted differently by rubric extraction and prompt guidance. | Normalize phase once at the boundary to one documented internal representation. For early/mid/end, verify that the loaded criterion text and prompt guidance correspond in both single and batch paths; reject unknown phases rather than silently defaulting. |
| 1 | Native TXT parsing retains only the first 30,720 UTF-16 units. Eleven of twelve reading-order candidate extractions exceed this limit. | Define input handling explicitly. A complete-document condition must preserve all relevant material, or use a documented chunking/retrieval policy with coverage reporting. Before submission, show and archive omitted regions, input/context budget and effective text hash. Never label prefix-only output a full-document assessment. Preserve a native-prefix condition for diagnosis. |
| 2 | Category scores 90/0/0 produce native overall 90 while a separate summary reports 30. | Decide what the aggregate measures and its denominator. If it intentionally averages only positive/addressed categories, name it accordingly and show coverage; if all applicable criteria are intended, preserve genuine zeros and distinguish unknown, absent, NA and tool-failure states. Report native and revised aggregates separately. |
| 2 | Default rubric lacks framework IDs 3c and 5d. | Version the rubric and document its crosswalk. Either include the omitted criteria with approved stage wording or explicitly describe the narrower instrument. An undefined mid-project framework cell must remain undefined until an instrument decision supplies wording. |
| 2 | Request construction sends the output cap but omits configured temperature; the probe seed is not sent. | Propagate only supported provider parameters, report unsupported settings clearly, and save actual sent parameters. Do not imply a seed guarantees determinism or is supported by a provider merely because a UI field exists. |
| 2 | Native result exports lack enough context for exact reproduction. | Export a run manifest with code/rubric/prompt/input hashes, model/checkpoint/provider settings, intended/effective phase, truncation/coverage, raw output, parsed output, errors and timings. Exclude credentials and authentication headers from saved/shared manifests. |
| 3 | PDFs are unsupported by the native parser, while all proposed source documents are PDFs. | Provide an explicit preprocessing workflow or a separately scoped ingestion feature. Preserve source bytes and extraction version, inspect tables/annexes/reading order, and retain source-page references. Do not hide conversion behind a generic file-upload success message. |
| 3 | A prefix slice can end with half a Unicode surrogate pair. | Apply boundaries that preserve complete Unicode characters and test a supplementary-plane character exactly at the limit. Context limits should be measured in the units the provider actually enforces, with a documented safety budget. |

## Consequence for the scientific design

The native end-to-end condition is still measurable: it assesses what the pinned tool
actually does to the documents supplied. Its results cannot be interpreted as a
controlled test of model quality on the complete DMP and complete publication rubric.
Attribution of failures must distinguish extraction/input loss, criterion omission,
phase handling, aggregation and model judgment.

A main full-input/full-rubric condition would be an explicitly configured or changed
intervention, with its own prompt/settings or commit and a frozen analysis plan.
Human reference labels and any diagnostic native results must remain separate from
prompt development. Use calibration examples outside the six core projects; retain
native outputs rather than overwriting them after an improvement.

No code changes to DMP-EVA or the local dashboard have been made for this brief. A
future implementation should rerun the focused preflight and record changed outcomes
under the new version, then validate provider behavior separately before benchmark
execution. The absence of model calls in this preflight is not evidence of empirical
human/tool agreement.
