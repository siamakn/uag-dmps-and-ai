# Candidate page-mapped input packets

**Preparation only; not a frozen benchmark input or an evaluation protocol.** The 12 proposed PDFs produced 521 physical pages and 79 whole-page chunks. All source hashes match the six-pair proposal. No chunk exceeds the 24,000 UTF-16-unit engineering budget, but this does not establish that any provider, prompt, or model can accept it. No document quality judgments, human labels, OCR, uploads, model calls, or automatic score aggregation were performed.

## Method

`input-packets.py` reads the proposal and checks each original PDF's SHA-256 before running `pdftotext -bbox-layout -enc UTF-8 <pdf> -`. The ignored local `data/paired-dmp-corpus/input-packets/` holds, per document, the **unaltered command output** as `bbox.xml`, a `pages.json` mapping, a page-marked `pages.txt`, and numbered chunk text files. Original PDFs are neither edited nor copied. The machine manifest [input-packets.json](input-packets.json) records the proposal and script hashes, Poppler and Python versions, source and asset hashes, page dimensions, and document, page and chunk counts.

Pages are physical, 1-based PDF pages. Flow, block and line numbers are 1-based ordinals within their parent in Poppler's XML; line IDs include all four levels, and word IDs add their within-line ordinal. `pages.json` retains each extracted word's text and Poppler-reported bounding-box attributes, line bounding boxes, and page dimensions; the raw XML retains the complete extractor output, including block geometry. `pages.txt` marks every page and line, joins the word elements in each extracted line with single spaces, and ends each line with a newline. These navigation markers and normalized separators are added text. Thus “lossless” here means all **extracted word strings and line boundaries** are represented in order, not that PDF typography, whitespace, or visual content is preserved.

Chunks concatenate complete consecutive marked pages greedily up to 24,000 UTF-16 code units, counting markers and newlines. A page exceeding the budget is kept whole in its own explicitly flagged oversized chunk, never silently cut. Manifest flags and counts identify such cases; this run has none. Whole-page boundaries can still divide a table across pages. Chunking, multiple submissions, or bypassing a native parser cap would be a separately declared candidate input intervention, not an unchanged full-document native run. No rule for combining chunk outcomes is specified.

## Checks and limits

The build rejects unexpected XML hierarchies that leave any word or line unmapped. Verification reparses the stored XML, regenerates every page and chunk in memory, compares all asset bytes and manifest fields, checks the exact ordered page sequence, and checks concatenated chunk text against the full page-marked text. This covers every extracted line and word once in the derived text, and verifies page mapping and source PDF hashes. It does not independently establish that Poppler extracted every item in the PDF, nor rerun Poppler during `--verify`; raw XML integrity is checked against the recorded manifest. A synthetic fixture checks Unicode including a surrogate-pair character, an empty page, an oversized page, coverage and detection of corrupted output.

The extraction QA found table/form relationships and visual cues can be lost even in layout text. Coordinates are evidence for navigation, not semantic table reconstruction or full visual fidelity; reading order, figures, checkboxes, hidden content, scanned text and whole-document fidelity remain unvalidated. The earlier sampled [extraction QA](extraction-qa.md) and [native parser preflight](tool-preflight.md) apply. Human review, representation choice, rights and submission terms, final prompt and actual provider capacity remain open before a campaign. The proposal itself is not frozen.

| Project | Version | Pages | Lines | Words | Chunks | Largest chunk UTF-16 units |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| iMagine | early | 57 | 2,841 | 13,306 | 8 | 23,654 |
| iMagine | late | 74 | 3,504 | 17,367 | 10 | 23,946 |
| EGI-ACE | early | 54 | 2,447 | 12,891 | 7 | 23,693 |
| EGI-ACE | late | 71 | 2,619 | 15,638 | 8 | 23,879 |
| NANOFACTS | early | 26 | 949 | 8,131 | 4 | 23,019 |
| NANOFACTS | late | 24 | 951 | 8,204 | 4 | 23,730 |
| AGRICORE | early | 19 | 826 | 4,902 | 3 | 23,698 |
| AGRICORE | late | 34 | 1,729 | 11,155 | 6 | 23,234 |
| SUSTRACK | early | 61 | 3,001 | 22,024 | 11 | 23,932 |
| SUSTRACK | late | 70 | 3,551 | 22,012 | 12 | 23,748 |
| RECHARGE | early | 14 | 834 | 4,127 | 3 | 23,582 |
| RECHARGE | late | 17 | 873 | 5,013 | 3 | 22,802 |

## Reproduce locally

From repository root, with Python 3.7+ and Poppler `pdftotext` installed, and the exact proposal PDFs already in their local paths:

```sh
python3 research/paired-dmp-study/input-packets.py
python3 research/paired-dmp-study/input-packets.py --verify
python3 research/paired-dmp-study/input-packets-selfcheck.py
```

The build replaces only generated files in the packet directories and their numbered chunks; it never downloads or changes the source PDFs or historical selection. `--verify` reads existing assets without extraction, downloads or writes. Regeneration with another Poppler version can change extraction and hashes; it must be treated as a new candidate representation and checked again. The manifest and report describe this run, not a claim of cross-version bitwise reproducibility.
