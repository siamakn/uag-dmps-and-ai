# Pilot materials independent check

Checked 2026-11-04. This is a provenance and workflow check, not a DMP quality assessment or a human reference judgment.

## Source checks

- The preserved [PathOS D3.5 v2.0 PDF](../../data/paired-dmp-corpus/calibration/17578116.pdf) has SHA-256 `732074dc327f114356c5cff1ccc7f6846d79480eabe8daa2b53951058e4e94fa`, matching [calibration-proposal.json](calibration-proposal.json). Its first two pages identify the update dated 2025-11-10 and distinguish the earlier 2024 delivery.
- The preserved [framework PDF](../../data/paired-dmp-corpus/framework/DMP_Evaluation_V1.0.pdf) has SHA-256 `465a894b06bb67abea19acf16eba02dca8d665855a01572a7762ec3bb0e3fc26`, matching [criteria-index.json](criteria-index.json). Visual inspection confirms the 1b End-Project cell is on physical PDF page 8, printed page 7, and contains two distinct checklist items concerning final technical documentation and metadata, and technical fidelity for reuse. Consult the original cell for the precise wording.
- The PathOS record is outside the six-project proposal; its project timing and update context are documented in [natural-engineering-social-search.md](natural-engineering-social-search.md). The post-end sampling designation and rubric phase are different variables; a pilot End-Project phase assignment is not a general study-wide phase mapping.

## Pilot packet check

[pilot-start.md](pilot-start.md) correctly points to the 1b End-Project cell and distinguishes the pilot phase choice from the sampling designation. It asks for one criterion on one document, page and section evidence, uncertainty and usability feedback, and does not claim a two-reviewer reference. Formal benchmark reviewer allocation remains open. The source links to both local PDFs exist; public record and framework links are supplied but were not rechecked over the network in this local review.

[pilot-template.json](pilot-template.json) parses successfully, is explicitly a blank form rather than a completed assessment record, and contains no score, evidence, rationale or confidence. [calibration-worksheet.md](calibration-worksheet.md) is likewise blank and separates NA and uncertain from numeric scores. No assessment has been made by this check.

The initially overlapping 0/1 draft anchors were corrected after review: 0 now requires a completed criterion-specific search with no relevant evidence for either component, and 1 requires relevant but incomplete or insufficient evidence. The response asks whether the search was complete, and the blank template leaves that field null. These criterion-specific anchors remain pilot aids requiring calibration; they are not supplied by the framework itself. The pilot can be conducted by one reviewer to test instructions and record usability, but it cannot establish inter-reviewer agreement or a benchmark reference. No substantive issue remains for starting this single-reviewer pilot.
