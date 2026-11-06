# UAG DMPs and AI — progress note

Prepared 2026-11-04 for discussion; no message or publication has been sent.

## Proposed test set

A working proposal now contains **six distinct European projects and twelve DMP
documents**: two versions of the same project-wide DMP for each discipline slot.
The [proposal and source links](cohort-proposal.md) and [machine-readable manifest](cohort-proposal.json)
preserve document versions, exact file hashes, dates, lineage evidence and caveats.

| Discipline slot | Project | Earlier position | Later position |
| --- | --- | ---: | ---: |
| Natural sciences | iMagine | 16.44–17.26% | 100.46% |
| Engineering and technology | EGI-ACE | 23.63% | 114.40% |
| Medical and health sciences | NANOFACTS | 13.24–14.11% | 107.13% |
| Agricultural sciences | AGRICORE | 10.20% | 103.51% |
| Social sciences | SUSTRACK | 16.16–16.35% | 108.95% |
| Humanities | RECHARGE | 16.35–16.53% | 111.42% |

Position is elapsed calendar days from project start to the documented version
date, divided by the duration to the **latest authoritative project end**, including
extensions. Earlier versions must be ≤50%; later versions strictly >100%.
Repository deposit dates do not substitute for version dates. Ranges retain
differently labelled dates that remain within the same eligibility window.

Selection used metadata and version/scope evidence, without rating DMP quality.
Any documented current CORDIS discipline membership is allowed, but each project
fills one slot. Dominant branches and ties are reported; the slots do not imply
that one project represents a whole discipline. Three projects are Horizon Europe
and three Horizon 2020; all chosen representations are PDFs, and five later
versions are from 2024 onward. Pairing and timing take priority over these
programme, format and recency preferences.

## Evidence and limitations

Independent agent checks support source identity, revision lineage, current CORDIS
membership and date arithmetic. Twelve exact PDFs and their evidence snapshots are
retained locally. Human reference assessments have **not** been collected.
RECHARGE's cover/publication chronology discrepancy and several differently labelled
early dates remain explicit. AGRICORE's blanket reuse terms are unknown; the public
proposal uses links and checksums. FAIR-EASE remains a provisional reserve while
Siamak seeks clarification of conflicting repository/PDF rights statements. Current
CORDIS does not support RECAP's older stored agricultural classification, so it is
excluded from that slot.

The proposed human calibration scale is now approved: **0 not evidenced, 1 partial,
2 sufficient**, with separate NA and uncertainty states. Criterion/phase anchors and
formal reviewer allocation remain open. Possible reviewers are UAG members and
assisting librarians. Siamak's optional pilot is deferred while he becomes familiar
with the framework; this does not block the preparation work.

## Tool and input preparation

The working DMP-EVA source pin is `b80b43de820d46440d982eb99b2b3da8f4c2f818`, verified
against latest main on 2026-11-03 and to be rechecked before an experimental campaign.
Publication/archive/latest differences are recorded rather than requiring agreement
between them. [Isolated browser preflight](tool-preflight.md) completed 44 observed-
behavior assertions with no model requests. It confirmed rubric/prompt and phase
differences, zero-excluding aggregation and input-prefix behavior; this is not an
empirical performance result.

Eleven of twelve default reading-order extractions exceed the native 30,720 UTF-16
unit input cap. [Bounded extraction QA](extraction-qa.md), using two sampled pages per
document, also found table/field relationships that plain text can weaken or reorder.
Layout generally preserved those samples better but remains a draft representation.
Neither extraction is yet frozen as a full-document model input. Full-document and
native-prefix evaluation conditions must be distinguished before interpreting model
or human/tool differences.

## Next steps

1. Resolve input representation/coverage and keep the software/input conditions
   reproducible; selection-platform and tool-improvement briefs are ready for Claude.
2. Recruit interested human reviewers and calibrate the approved scale on documents
   outside the proposed six projects when people are available.
3. Freeze the reference protocol, cohort, actual model configuration and analysis
   before claiming human/tool agreement. Mainz backend-model comparisons remain a
   later stage.

The intended contribution is a traceable paired pilot and actionable evidence about
stage-sensitive DMP evaluation. Six projects support case-study findings, not
discipline rankings or population-level accuracy claims. Close related work is
already identified; a fuller literature comparison is still needed before novelty
claims.
