# Evaluation preparation alongside Claude's platform work

Prepared 2026-11-04. Read this in addition to the study README/status. The user
reported assigning `claude-platform-brief.md` to Claude. Changes to platform files
are visible in the shared working tree, but no completed implementation report was
available at this checkpoint. This work uses separate research files and ignored
input assets; it does not review or overwrite Claude's in-progress implementation.

The human pilot remains deferred. No human judgments, model/provider requests,
external messages or experimental results were generated.

## Concrete outputs

| Work | Output | What is ready, and what is not |
| --- | --- | --- |
| Experiment design | [Protocol draft](experiment-protocol-draft.md), [matrix](experiment-matrix.json) | Defines native diagnostic versus configured full-input conditions, controlled overall/criterion comparisons, later model comparison, six-project analysis units, request counts, failures and provenance. All unconfirmed design choices remain proposals; no campaign is approved or frozen. |
| Input preparation | [Packet method](input-packets.md), [manifest](input-packets.json), `input-packets.py` | Candidate page/line/word mappings and whole-page chunks for all twelve source PDFs: 521 physical pages and 79 chunks. Coverage and hashes pass; this preserves extracted strings, not full visual/table meaning. |
| Backend information | [Mainz readiness note](mainz-readiness.md), [unfilled profile](mainz-profile-template.json) | A short information request for model/checkpoint identity, API schema, actual tokenizer/context, accepted settings and run accounting. No model availability or endpoint is invented, and no credentials or request are supplied. |
| Independent checking | [Review](parallel-preparation-review.md) | Independently checked source hashes, actual PDF page counts, XML/JSON mapping, chunk coverage/UTF-16 budgets, experiment units and request arithmetic. The agreement/disagreement wording inconsistency was corrected. |

## Important distinctions

The unchanged native DMP-EVA condition measures the actual instrument/prompt, phase
handling, parser prefix and native aggregation. A configured full-rubric/full-input
condition is a different intervention. Comparing them cannot isolate one particular
fix or a model effect. The proposed overall-versus-criterion contrast holds model,
input, rubric context, anchors and output-scale semantics constant and changes the
target task scope. Later model comparison holds the chosen prompt/input constant.

Packet preparation does not solve the evaluator's input problem by itself. The
24,000 UTF-16-unit budget is an engineering limit, not a provider token capacity.
Whole-page chunks can divide a multi-page table, coordinates do not reconstruct its
semantics, and no automatic chunk-score averaging is approved. Prefer a verified
full-context request when the actual backend permits it. If chunking is used, an
explicit evidence and final-judgment policy must be specified first.

The first proposed model/prompt stage would have at most 216 logical requests at
one repetition, assuming full-input conditions fit and all 16 criteria are defined.
That is a planning bound, not a run, charge or estimate of OpenAI subscription use.
Six projects remain six analysis clusters regardless of how many criteria, chunks
or repeats are generated.

## Practical next work

1. When Mainz documentation/model availability is known, resolve the unfilled
   profile and check complete request sizes with the actual tokenizer and limits.
2. Choose and validate a source-faithful full-document representation and the exact
   input/prompt condition before any configured inference. Current packet assets
   remain candidates, with the extraction-QA limitations visible.
3. After Claude supplies `claude-platform-results.md`, independently review the
   completed platform changes against its brief and test evidence using isolated
   storage. Do not infer completion from files merely changing in the working tree.
4. Resume human calibration/recruitment when people are ready. It is required for
   reference-based agreement claims, not for these technical preparation tasks.

The separate [machine status](parallel-preparation-status.json) records this track
without rewriting Claude-owned platform files or concurrent work. The original
study status still supplies the cohort history, confirmed decisions and pilot
deferral. This note introduces no new scientific approvals or human obligations.
