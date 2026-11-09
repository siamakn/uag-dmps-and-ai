# Work completed alongside Claude's platform work

Checkpoint: 2026-11-06, Europe/Berlin. Read this with the study README, decisions
and [previous preparation checkpoint](parallel-preparation.md). The human pilot
remains deferred; there is no immediate reading or rating task for Siamak.

## New completed work

1. **Executable analysis check with artificial data.** The
   [method and commands](analysis-dry-run.md) describe a local, synthetic-only
   prototype of the proposed F1-minus-F0 disagreement calculation. Six projects
   each receive equal weight after averaging their two documents. Fixed coverage
   denominators, genuine zero scores, applicability, uncertainty, absent outputs
   and undefined comparisons stay distinct. Sixteen tests pass, with additional
   hand-calculated checks in the [independent review](analysis-dry-run-review.md).
   The checker identified two omissions during development, both corrected:
   applicable but nonnumeric human ratings must remain in coverage denominators;
   the common-analysis exclusion audit must show both conditions even when only
   one has a missing output. These are software checks, not benchmark findings.

2. **Additional candidate search using recovered versions.** The
   [reproducible screen](version-followup-screen.md) identifies ten
   publication-date leads in the saved version discovery, six with cached
   discipline membership. Four later PDFs were checked against document dates.
   TWEET-IE and e-DIPLOMA fall exactly at project end; D1-Glia falls before it.
   None of these files meets strict >100%. MultiMiner has an early version in
   the first half and a post-end revision-history entry, but a conflicting
   control-table date falls exactly at project end. It is a
   [conditional alternative](version-followup-documents.md), not a verified
   replacement. The date hierarchy must be settled consistently before using
   this case. Source hashes, alternative date labels and limitations are saved.

The six-pair proposal, experiment draft/matrix, packet manifest and historical
selection retain their prior hashes. No platform code, actual review labels,
source PDFs in the proposal, model calls, messages to collaborators, or frozen
cohort were created or changed by this continuation. Five additional source PDFs
were retained locally for the bounded follow-up: two MultiMiner versions and one
later file from each of the other three projects. Third-party source files remain
in the ignored corpus directory; public notes retain links and hashes.

## Platform coordination

The saved [Claude implementation report](claude-platform-results.md) now exists
and describes completed selection-platform features and tests. The user reports
that Claude is currently working; this continuation therefore did not edit or
test the shared platform. Its report is implementation evidence, not this
continuation's independent acceptance review. The older preparation checkpoint's
statement that no report existed was true at that earlier checkpoint and is
superseded here. A whitespace check of the shared working tree reports a trailing
blank line in `scripts/README.md`; it was left untouched during concurrent work.

## Next actions and actual dependencies

- After Claude's work is stable, independently review its final changes against
  the brief and run relevant tests using isolated storage. Do not test against
  the real selection.
- When Mainz documentation/model availability is supplied, fill the
  [backend profile](mainz-readiness.md) and check complete assembled requests
  against the actual tokenizer and context limits. No credentials are requested.
- Retain MultiMiner as conditional until the issue-date evidence hierarchy is
  agreed; apply that hierarchy across all candidates. No threshold is relaxed.
- Resume calibration when people are ready. Genuine human reference judgments
  remain necessary for empirical human/tool agreement claims; this technical
  dry run does not substitute for them.

There is no new required user action at this checkpoint. Scientific proposals
remain proposals. No new decision or approval was inferred from these checks.
The adjacent [machine checkpoint](continuation-2026-11-06.json) records the new
outputs without replacing the study's earlier decision history.
