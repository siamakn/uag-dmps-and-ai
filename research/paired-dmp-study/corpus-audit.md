# Local corpus audit for a six-project paired-DMP study

Audit date: 2026-11-03. This is preliminary discovery for planning, **not a selection**. No live harvesting, PDF download, pipeline regeneration, dashboard change, or change to `data/selection.json` was performed.

## Subsequent protocol decision

The user subsequently confirmed documented **issue-date** eligibility (≤50%, >100%) and a fresh whole-pool search. This audit uses repository publication dates because issue dates are not in the current dataset. Its counts and gaps are therefore discovery diagnostics only, not eligibility counts or evidence that any discipline lacks issue-date pairs. Search version families throughout the pool, including late or simultaneous deposits that fail the publication-date windows.

## Main finding

The current local pool does not establish six qualifying same-scope project pairs. It supplies same-grant leads for four of six **primary** EuroSciVoc branches using complete publication dates; medical sciences gains one scope-ambiguous lead when partial dates are treated as intervals; humanities has no lead even under that treatment. These are availability findings for this snapshot, not evidence that qualifying DMP pairs do not exist elsewhere or in omitted Zenodo versions.

## Reproducible method and provenance

Run from the repository root:

```bash
python3 research/paired-dmp-study/corpus-audit.py
```

The stdlib-only script reads existing data and writes only `corpus-audit.json` alongside itself. The JSON records SHA-256 hashes of the dataset, saved selection, raw files, and inspected pipeline/template files; exact integer date numerators and denominators; every lead record and its file metadata; and selection records. Counts can be checked without a network connection. The dataset has 2,650 records, including 2,504 classified as `kind=dmp`; the five raw query files contain 3,268 unique record IDs. `data/cordis/` currently contains no bulk files, so this audit uses the CORDIS-derived dates and branches already embedded in the dataset; it does not independently recheck the source classification or dates against a bulk download.

For discovery, require `kind=dmp`, EU funding tier (`Horizon Europe`, `Horizon 2020`, or `Other EU`), nonempty grant and primary CORDIS discipline, `access=public`, and at least one listed file. These last two conditions are **metadata checks only**: record access is not proof that a file is public and currently downloadable. No schema result, content completeness, or perceived DMP quality was used.

Group by grant; require at least one distinct early record and one late record. For full ISO dates define `n=(publication-start).days`, `d=(end-start).days` and require `d>0`. Early means **`0 <= 2*n <= d`**; late means **`n>d`**. This excludes pre-start publications and treats the end date itself as exactly 100%, not late. The early cutoff is an explicit provisional interpretation of “around <=50%”; no undocumented tolerance was added. The denominator is the current saved project date interval, not an inclusive-day duration or a reconstructed historical grant duration.

All pair counts below mean record combinations sharing a grant, **not verified versions of the same DMP**. Primary-branch counts use `disc`; membership counts use `disc_all` and are overlapping. A project carrying several branches could eventually fill only one of the six project slots.

## Availability

Full publication dates, all years:

| EuroSciVoc broad branch | EU primary grants | EU `disc_all` grants | HE primary grants | HE `disc_all` grants |
|---|---:|---:|---:|---:|
| natural sciences | 10 | 17 | 8 | 10 |
| engineering and technology | 6 | 11 | 2 | 5 |
| medical and health sciences | 0 | 0 | 0 | 0 |
| agricultural sciences | 2 | 5 | 0 | 1 |
| social sciences | 1 | 3 | 1 | 2 |
| humanities | 0 | 0 | 0 | 0 |

There are **19 EU grants / 26 combinations**, of which **11 grants / 14 combinations** are Horizon Europe. Requiring **both** publications to be 2024 or newer leaves only **AD4GD and SUSTRACK** (both HE), with three combinations because SUSTRACK has two late records. Recent publication therefore needs to remain a preference if broader discovery is intended. No full-date lead has maDMP JSON for both endpoints; only ERIES and GraspOS have any endpoint marked `madmp=true`.

Primary-branch lead projects, all years:

| Branch | Horizon Europe leads | Horizon 2020 leads |
|---|---|---|
| natural sciences | MAPWORMS, GraspOS, PathOS, EuroScienceGateway, FAIR-EASE, AD4GD, interTwin, iMagine | EGI-ACE, HIT2GAP |
| engineering and technology | ERIES, EM-TECH | CURE, PIXEL, DIANA, RECAP |
| agricultural sciences | none | VIRTIGATION, ASTEP |
| social sciences | SUSTRACK | none |
| medical and health sciences | none with full dates | none |
| humanities | none | none |

FAIR-EASE supplies the one HE `disc_all` agriculture lead, while its primary branch is natural sciences. It also carries social sciences. Assignment rules must be fixed before choosing among such overlaps; these memberships do not create additional distinct projects.

## Candidate leads and identity checks still needed

The JSON inventory contains every record, DOI, title, exact position, funding identifier, discipline membership, and saved file list. Examples worth targeted checking:

| Project / primary branch | Early record | Late record | Evidence limit |
|---|---|---|---|
| AD4GD / natural | [10839334](https://zenodo.org/records/10839334), 2024-02-29, 546/1095 = 49.863% | [17201854](https://zenodo.org/records/17201854), 2025-09-25, 1120/1095 = 102.283% | Titles describe D8.3 and final D8.4; predecessor/scope evidence still needed. Earlier initial record 10843720 is also available. |
| ERIES / engineering | [21382158](https://zenodo.org/records/21382158), 2022-12-20, 202/1460 = 13.836% | [21336370](https://zenodo.org/records/21336370), 2026-07-13, 1503/1460 = 102.945% | Early is PDF metadata, late is maDMP; verify that they cover the same project-wide scope. D3.5 record 21382168 is dated before project end and does not pass strict >100%. |
| SUSTRACK / social | [14497074](https://zenodo.org/records/14497074), 2024-05-01, 547/1095 = 49.954% | [19161921](https://zenodo.org/records/19161921) or [19161966](https://zenodo.org/records/19161966), both 2026-03-09, 1224/1095 = 111.781% | Two late records named V1 and V2 have the same publication date; inspect lineage, document issue dates, and contents solely to establish identity/scope. |
| VIRTIGATION / agriculture | 14506057 or 14506240 | 17970028 | Early records explicitly say “Public summary”; final is “Final Data Management Plan.” Do not assume a summary and full plan are comparable versions. |
| GraspOS / natural | 8095578 or 11098069 | 18679355 | Late title is a **CNR pilot** DMP, unlike early project DMP titles. Same-grant grouping may be a false same-scope match. |

Reading covers, version histories, deliverable references, and scope statements to verify document identity is compatible with metadata-based selection. Such inspection must not become a quality score or a reason to prefer polished plans. Concept/version relations, project grant, deliverable lineage, scope/partner identifier, document revision/date, and file checksum should be retained separately rather than collapsed into a single inferred “same DMP” flag.

## Partial dates

There are 44 `YYYY-MM` dates, 16 `YYYY` dates, and one malformed nine-character `2026/2027` value. The current pipeline's `datetime.date.fromisoformat(published[:10])` rejects partial dates and returns lifecycle unknown; the malformed value must not be imputed as a year.

For a sensitivity check, treat a month/year as its entire calendar interval and accept a role only if **all** possible days qualify. This adds exactly two HE grants, yielding **21 EU grants / 28 combinations** and **13 HE grants / 16 combinations**:

- **PoDIUM / natural sciences**: early 10518610, 2024-01-16; late 19593084, publication `2026`, after saved project end 2025-12-31 for every day in that year.
- **EIRENE PPP / medical and health sciences**: early 17864615, `2023-03`; late 17866885, `2025-10`, after saved end 2025-09-30. The early title is “Data Management Plan of EIRENE PPP Project” (D9.2), while the late title is “Data policy and Data Management Plan of EIRENE” (D3.1). This may change from the preparatory project to the wider infrastructure, so identity/scope is explicitly unverified.

Humanities remains zero. The JSON preserves original partial date strings; no invented exact dates are written to the dataset. Medical-science feasibility cannot be claimed from this one scope-ambiguous lead.

## Existing selection is a different design

`data/selection.json` exists despite the older AGENTS.md statement that it is absent. It is untracked, saved 2026-11-02T15:30:59, and contains 12 resolved records from **12 different grants**. Its apparent six early/late branch slots therefore do not establish paired versions. Its six earlier records all fall at <=50% by exact date arithmetic; the six later records all fall strictly >100%, but none is paired with its own project within the saved selection.

Of selected projects, only ERIES and SUSTRACK have a full-date early/late same-grant lead in the local pool. REFOREST has an earlier record at 57.9%, outside the provisional early limit; SPPELME has only its final record locally; DIAMAS has two records at the same 2023-12-19 publication date and neither is >100%. Other selected projects need targeted predecessor/successor discovery if retained.

Selection SHA-256: `a4a54dba18af7d8a28c1b60e4c317921c7768573735adcd7d44eafa66007edeb`. The selection was read only and left byte-for-byte unchanged.

## Pipeline gaps relevant to planning

- `scripts/04_build_dataset.py:lifecycle` rounds `n/d` to three decimals before assigning the existing <=34%/<=70%/late labels. Those labels do not implement <=50%/>100%; “late” currently includes records between 70% and project end. This audit recomputes from dates using integer comparisons. No current full-date row crosses the proposed 50% or 100% cutoff solely because of rounding, but rounding could hide a near-boundary case in a refreshed pool.
- `scripts/common.py:search` sends query, size, page, and sort only; there is no explicit all-versions request or concept-chain traversal. Whether the upstream default search returned older versions cannot be established from saved results. `slim` retains a free-text `metadata.version` string but drops concept identifiers, version relations, related identifiers, record timestamps, revision information, checksums, and file access flags. The persisted raw JSONL is therefore already reduced metadata, not full API responses. Do not infer that absent earlier versions do not exist.
- Searches are bounded to 250 pages. At anonymous page size 25 this caps each query at 6,250 results, and the caller discards the reported total. No current query's saved size reaches that cap, but a future broadened all-version harvest needs explicit total/completeness logging and pagination validation.
- The build picks the **first** CORDIS-matched grant from funding metadata plus maDMP grant candidates. A record may have several funders/grants (84 current dataset rows contain multiple funding entries). A project-pair study needs a checked grant association rather than treating this first match as definitive.
- `parse_corpus` reduces each record to one maDMP file, preferring the file with more dataset-description characters when several exist. That representation does not preserve file-level scope distinctions. CERTAINTY's multiple partner DMPs illustrate why grant-only pairing is unsafe even when records are genuine maDMPs.
- PDFs remain remote; saved dataset descriptions and file lists are truncated. Follow up on full metadata and exact files for identity, access/licensing, and checksums before freezing a benchmark. Saved project dates may incorporate extensions; dates need a pinned CORDIS source and an explicit rule for extensions before final eligibility decisions.

No UI or production code was changed, so dashboard self-tests were not run. The audit script was executed and its counts independently cross-checked by a separate direct grouping of the dataset; it leaves the benchmark and saved selection untouched.
