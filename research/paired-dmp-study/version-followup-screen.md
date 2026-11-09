# Follow-up of the recovered version records

Checked 2026-11-06. This is an additional discovery pass, not a change to the
six-pair proposal or a quality assessment. Claude's saved version-chain discovery
now permits a reproducible search for newer alternatives while platform work
continues. The source files were read without changing them.

## Offline screen

`python3 research/paired-dmp-study/version-followup-screen.py` reads the saved
dataset and `data/paired-discovery/versions.json`, pins both hashes, and writes
[the queue](version-followup-screen.json). Of 226 saved version-chain leads, 163
EU grant/concept families were screened. Ten have at least one full publication
date in the first half and one after the cached project end; six also have a
cached CORDIS branch. These are **publication-only leads**, not eligible pairs.
Dates of incomplete precision are recorded as incomplete rather than assigned
a day. The original six-pair proposal is unchanged.

| Project | Programme | Cached broad branches | Follow-up |
| --- | --- | --- | --- |
| D1-Glia | Horizon Europe | medical | Final PDF issue date fails strict post-end rule; checked below |
| MultiMiner | Horizon Europe | engineering; natural | Separate bounded [source check](version-followup-documents.md) |
| TWEET-IE | Horizon Europe | engineering | Final PDF date equals project end; checked below |
| e-DIPLOMA | Horizon Europe | natural; social | Separate bounded [source check](version-followup-documents.md) |
| SteamBioAfrica | H2020 | engineering; social | Issue dates, latest end and lineage not checked in this pass |
| ExPaNDS | H2020 | natural; social | Issue dates, latest end and lineage not checked in this pass |
| FORWARD | Horizon Europe | absent | Current classification and document evidence needed |
| eDNAqua-plan | Horizon Europe | absent | Current classification and document evidence needed |
| WorldFAIR | Horizon Europe | absent | Current classification and document evidence needed |
| EOSC-Pillar | H2020 | absent | Current classification and document evidence needed |

This is a bounded screen of version chains. Separate-concept revisions, external
documents, projects without cached dates, and partial-date records can be missed.
A later publication date is neither necessary nor sufficient evidence of a later
DMP issue date. No claim of exhaustive absence follows from this queue.

## Two document checks by the orchestrator

Exact dates, evidence locators, source byte counts and SHA-256 values are retained
in [the date-check record](version-followup-date-checks.json). PDFs, live Zenodo
API responses and fresh CORDIS HTML responses are retained under the ignored
`data/paired-dmp-corpus/followup-2026-11-06/` directory with their original terms.
Relevant date pages were rendered and visually inspected.

**TWEET-IE, grant 101079125.** The
[final record 17361082](https://zenodo.org/records/17361082) is published
2025-12-31. Its PDF cover (physical page 1) gives M36, 31/10/2025; the most recent
History of Changes entry (physical page 3) gives version 4.1, 31/10/2025. The
repository version label is 5.0; both labels are retained rather than conflated.
Fresh [CORDIS](https://cordis.europa.eu/project/id/101079125) gives start
2022-11-01 and end 2025-10-31. The documented PDF date therefore falls at exactly
100%, not strictly above it. This file cannot supply the late slot. An early
file was not downloaded because that would not repair this late-slot failure.

**D1-Glia, grant 101090280.** The
[final record 15392557](https://zenodo.org/records/15392557) is published
2025-05-12. Physical PDF page 2 explicitly gives final delivery and version-3
issue date 9/3/2025. The table's 29/6/2023 entry establishes day/month convention,
so this is 2025-03-09. Fresh
[CORDIS](https://cordis.europa.eu/project/id/101090280) gives start 2023-04-01 and
end 2025-03-31: 708/730 elapsed days, approximately 96.99%. This is a pre-end
issue, so this file cannot supply the late slot. Its early files and full
lineage were not checked after this exclusion.

An access discrepancy was resolved during the D1-Glia check: the web search
service rendered a restricted record, but a fresh live API response says open
and the linked PDF downloaded successfully with HTTP 200. The exclusion rests
on its explicit issue date, not that stale access rendering. This also shows
why fresh primary responses matter before excluding apparently restricted files.

Neither exclusion applies to every possible document from the project. A future
verified later revision could change the conclusion for that revision. This pass
does not replace, freeze, or assign any study documents.
