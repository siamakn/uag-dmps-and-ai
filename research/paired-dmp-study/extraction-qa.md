# Bounded extraction-fidelity QA

**Status: neither representation is ready to freeze as a benchmark input.** Layout generally preserves the sampled table relationships better, but both flatten meaningful visual structure and the separate native input limit can truncate content. This is source preparation, not a DMP assessment, a human reference label, or a model run.

## Method and limits

Compare existing UTF-8 pdftotext -layout and default extracts, split on form feeds, against page images rendered with pdftoppm -f PAGE -l PAGE -scale-to 1250 -singlefile -png; physical PDF page numbers are 1-based. Selection was purposive: one table/body and one annex or near-end page per document, not random. SHA-256 of all three files verified against text-extraction.json.

The sample comprises exactly two physical pages per PDF: a table/body example and an annex or late/end example. It is purposive and cannot establish whole-document fidelity. The chosen near-end page is not necessarily an annex; contents lists were not exhaustively reconciled against annexes. No OCR, correction, external upload or model call was performed. PDF, layout and reading-order file paths and verified SHA-256 hashes are in [extraction-qa.json](extraction-qa.json); extraction commands and tool version are in [text-extraction.json](text-extraction.json). Temporary rendered page images were placed in `/tmp/dmp-qa/` and are not durable evidence.

No clear mathematical expressions, non-Latin scripts or checked checkboxes were encountered on sampled pages; those features therefore remain untested. Accented “GIOŚ” on AGRICORE early p10 survived both extracts. Empty form rectangles in NANOFACTS and color/highlight in SUSTRACK demonstrate visual information that neither plain text preserves. Figures, links, hidden text, and other pages remain unchecked.

All layout versions and 11 of 12 default reading-order versions exceed the separately documented 30,720 UTF-16-unit pre-trim threshold. See [tool-preflight.json](tool-preflight.json) for actual parser-path evidence; the smaller extraction alone does not ensure the full document reaches a model.

## Sample observations

| Project/version | Physical pages | Better on sampled pages | Observation |
| --- | --- | --- | --- |
| iMagine early | 13, 50 | Layout | p13 two-column prompt and answer interleave line-by-line in reading order; layout keeps columns aligned. p50 reading order moves the second Yes below the following question; layout places it beside its question. |
| iMagine late | 25, 65 | Layout | p25 reading order interleaves the availability question with answer text; p65 reorders lines within the image-processing question and collects bullet glyphs apart from their text. Layout preserves columns and bullets better, although it still flattens cells. |
| EGI-ACE early | 20, 54 | Layout | p20 both retain field names and answer prose; layout preserves left-column labels. p54 reading order detaches bullet glyphs from the two target groups; layout keeps each on its line. |
| EGI-ACE late | 33, 71 | Layout | p33 layout preserves field-to-content alignment and bullet lines; reading order separates bullet glyphs and content. p71 final field and answer are recognizable in both. |
| NANOFACTS early | 8, 26 | Layout | p8 reading order fragments the final table row across columns; layout retains spatial association. p26 shows two empty response boxes in the image, absent as boxes in both text files; question text remains. |
| NANOFACTS late | 7, 24 | Layout | p7 reading order interleaves dataset types, formats and sizes across rows; layout retains approximate columns. p24 contains empty response boxes absent as boxes in both; visible questions remain. |
| AGRICORE early | 10, 19 | Layout | p10 reading order groups all category labels before dataset names, weakening associations; layout preserves column placement. p19 layout maintains deliverable table row; reading order separates headers and fields. GIOŚ is retained in both. |
| AGRICORE late | 17, 34 | Layout | p17 reading order lists field labels together before their respective values; layout preserves associations. p34 reading order groups the two IDs and mixes row values; layout keeps rows spatially aligned. |
| SUSTRACK early | 24, 54 | Layout | p24 reading order separates dataset identifiers, fields and formats; layout preserves approximate rows. p54 annex form text and placeholders are present, but color and yellow highlighting that distinguish instructions and placeholders are lost in both, and table structure is flattened. |
| SUSTRACK late | 29, 67 | Layout | p29 reading order separates row fields and identifiers; layout retains spatial cues. p67 annex inventory is heavily fragmented in both; reading order loses row relationships more severely. Both break DOIs across lines, so reconstructing identifiers requires care. |
| RECHARGE early | 7, 14 | Layout | p7 reading order lists metadata names before their descriptions, losing row associations; layout aligns them. p14 closing prose reads coherently in both. |
| RECHARGE late | 9, 17 | Similar; layout retains columns | p9 both retain metadata label/description sequence, layout additionally preserves columns; p17 closing prose reads coherently in both. This is a sample-only comparison, not a whole-document choice. |

## Implications for preparation

Do not freeze either text as a full-document benchmark input on these samples. Retain both exact candidate files and PDFs. Before choosing a representation, inspect the remaining content with emphasis on complex tables, forms, figures and annexes, and establish a reproducible method that preserves their relationships and fits the actual evaluator input path. Verify any transformed representation against the source and document what reaches the model. These are preparation checks; they do not decide criterion scores.
