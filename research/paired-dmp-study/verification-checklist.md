# Verification checklist — six proposal pairs

Generated 2026-11-06 by `verification-checklist.py` from `cohort-proposal.json` and the local corpus. **Nothing here is verified.** A pair becomes *verified* in the dashboard only when a person has done the steps below and recorded them.

## How to use it

1. Start the dashboard: `python scripts/serve.py`. Choose *Paired study* and press **Load proposal** (once; it replaces an empty draft).
2. For each pair, open the PDFs listed below at the given physical pages (the page count of the PDF file, not the printed page number).
3. In the pair's **Evidence** editor:
   - **Same-scope descriptor**: what both documents cover, e.g. `project-wide DMP, whole consortium`. Enter the same text in each document's *Document scope* only if the document states it.
   - **Issue date** for each document: confirm the value at the locator. Under D16 an explicitly labelled issue / submission / delivery date wins, then a dated cover, then the version's revision-history row. If the PDF shows something else, correct the value and locator. Then set *Issue-date state* to `verified` and enter your name.
   - **Lineage**: confirm that the later document revises or succeeds the earlier one (revision table, 'updates D1.2', same deliverable series). Add an evidence entry (locator + one-line note), set *Lineage state* to `verified`, enter your name.
   - If something contradicts the proposal, set the state to `contradictory` and say why in *Notes*. The pair turns *rejected*; that is a valid outcome.
4. Press **Check files** (re-hashes the 12 PDFs on disk).
5. When all six pairs show *verified*, the protocol must still be approved in the protocol panel before **Freeze** is allowed.

The quoted lines come from automatic text extraction and can be garbled or in a different order from the page. They only help you find the date; the PDF page is the evidence.

## natural sciences — iMagine (grant 101058625)

- Project run (latest authoritative end, D09): **2022-09-01 → 2025-08-31** (1095 days). End source: https://cordis.europa.eu/project/id/101058625
- CORDIS branches: natural sciences; dominant: natural sciences.
- Claim to check (agent review, `pair-review.json`): *Late physical p7 expressly builds upon and updates D1.2; both project-wide, eight use cases.*
- Rights note: CC BY 4.0 in early physical p2 and late physical p3

### early · `zenodo:7759984` · iMagine D1.2 Data Management Plan

- PDF: `data/paired-dmp-corpus/101058625/7759984.pdf` (481463 bytes, sha256 `475634f9fdd5ed0e…`)
- Record: https://zenodo.org/records/7759984
- Chosen issue date: **2023-03-09** — Actual delivery date, version 1.0 — physical PDF p2 → **17.26%** of the run (rule: early ≤ 50%)
  - text on that page: `Due date  28/02/2023  Actual delivery date:  09/03/2023`
- Other labelled date: 2023-02-28 — unlabelled dated cover; also due date — physical PDF p1 → 16.44% (same verdict)
- Repository publication date (not used): 2023-03-22
- [ ] issue date confirmed at the page   - [ ] scope noted

### late · `zenodo:17055683` · iMagine D1.4 Final Data Management Plan

- PDF: `data/paired-dmp-corpus/101058625/17055683.pdf` (1003166 bytes, sha256 `5655797dbbf1392a…`)
- Record: https://zenodo.org/records/17055683
- Chosen issue date: **2025-09-05** — dated cover and Actual delivery date, version 1.0 — physical PDF p1 → **100.46%** of the run (rule: late > 100%)
  - text on that page: `05/09/2025`
- Repository publication date (not used): 2025-09-05
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

Known uncertainties from the proposal:
- iMagine late is only5days after current CORDIS end; new authoritative end evidence could change qualification.

## engineering and technology — EGI-ACE (grant 101017567)

- Project run (latest authoritative end, D09): **2021-01-01 → 2023-06-30** (910 days). End source: https://cordis.europa.eu/project/id/101017567
- CORDIS branches: engineering and technology, natural sciences; dominant: natural sciences.
- Claim to check (agent review, `pair-review.json`): *Late physical p4 expressly updates D1.2; project research-data scope in both.*
- Rights note: CC BY 4.0 in both physical p2

### early · `zenodo:6602163` · EGI-ACE D1.2 Data management plan

- PDF: `data/paired-dmp-corpus/101017567/6602163.pdf` (513551 bytes, sha256 `4a0a8a2aa3ce0be1…`)
- Record: https://zenodo.org/records/6602163
- Chosen issue date: **2021-08-04** — Document Log, Issue 1, Final version addressing review comments — physical PDF p2 → **23.63%** of the run (rule: early ≤ 50%)
- Repository publication date (not used): 2021-08-04
- [ ] issue date confirmed at the page   - [ ] scope noted

### late · `zenodo:19402005` · EGI-ACE D1.5 Data Management Plan

- PDF: `data/paired-dmp-corpus/101017567/19402005.pdf` (776995 bytes, sha256 `a827195d2d40780d…`)
- Record: https://zenodo.org/records/19402005
- Chosen issue date: **2023-11-08** — Document Log, Issue v1.1, appendix added following final review — physical PDF p2 → **114.40%** of the run (rule: late > 100%)
  - text on that page: `v1.1  08/11/2023  Added the Appendix I with the data/datasets  G. La Rocca`
- Repository publication date (not used): 2023-11-17
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

## medical and health sciences — NANOFACTS (grant 952259)

- Project run (latest authoritative end, D09): **2021-01-01 → 2024-06-30** (1276 days). End source: https://cordis.europa.eu/project/id/952259
- Original end printed or inferred: 2023-12-31 (sensitivity only).
- CORDIS branches: engineering and technology, medical and health sciences; dominant: engineering and technology.
- Claim to check (agent review, `pair-review.json`): *Early physicalp5 describes first project-wide DMP; late physicalp5 explicitly identifies first version and updates project data-management practices across consortium.*
- Rights note: Both cached full Zenodo API metadata declare CC0; both PDF legal notices authorize reproduction provided source acknowledged. Preserve both; attribution retained.

### early · `zenodo:13847570` · D1.2 Data Management Plan (DMP)

- PDF: `data/paired-dmp-corpus/952259/13847570.pdf` (408860 bytes, sha256 `a91d74c33cd1078f…`)
- Record: https://zenodo.org/records/13847570
- Chosen issue date: **2021-06-30** — Explicit issue date in repeated early footer; first occurrence physicalp2 — physical PDF p2 → **14.11%** of the run (rule: early ≤ 50%)
  - text on that page: `30/06/2021`
- Other labelled date: 2021-06-19 — Revision v1.5 date on early cover; late physicalp5 narrative says first version issued on this date — physical PDF p1 → 13.24% (same verdict)
- Repository publication date (not used): 2024-09-27
- [ ] issue date confirmed at the page   - [ ] scope noted

### late · `zenodo:13857898` · Data Management Plan (DMP)v2

- PDF: `data/paired-dmp-corpus/952259/13857898.pdf` (442267 bytes, sha256 `717de7b70110d2d3…`)
- Record: https://zenodo.org/records/13857898
- Chosen issue date: **2024-09-29** — Explicit issue-date footer and revision v2.3 date — physical PDF p1 → **107.13%** of the run (rule: late > 100%)
  - text on that page: `2.3 29/09/2024  Nikola Knežević (PC) (proof-reading)`
  - text on that page: `29/09/2024`
- Repository publication date (not used): 2024-09-29
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

Known uncertainties from the proposal:
- Early explicit footer issue30Jun2021 differs from early revision and later first-issued narrative19Jun2021. All retained date choices are early.
- Early cover36months and late cover42months corroborate duration change. Original end31Dec2023 inferred from start+36months, not independent amendment-register proof.

## agricultural sciences — AGRICORE (grant 816078)

- Project run (latest authoritative end, D09): **2019-09-01 → 2024-06-30** (1764 days). End source: https://cordis.europa.eu/project/id/816078
- Original end printed or inferred: 2023-08-31 (sensitivity only).
- CORDIS branches: natural sciences, agricultural sciences; dominant: agricultural sciences = natural sciences.
- Claim to check (agent review, `pair-review.json`): *Late physicalp2 versionhistory initialversionfromD9.2; physicalp3 andp7 explicitly final project-wide DMP based on initialD9.2; earlyp3 andp6 same consortium/project-data scope.*
- Rights note: Both covers label dissemination Public; exact project-hosted PDFs downloaded by source worker. No explicit blanket document reuse licence found in full text; latep2 disclaimer concerns contributor originality/referencing, not a document reuse grant or consent prohibition.

### early · `AGRICORE-D9.2-v1.0` · D9.2 Data Management Plan

- PDF: `data/paired-dmp-corpus/816078/AGRICORE-D9.2-v1.0.pdf` (698672 bytes, sha256 `83a0aaa24f920828…`)
- Chosen issue date: **2020-02-28** — Version History Date, v1.0 Final draft version — physical PDF p2 → **10.20%** of the run (rule: early ≤ 50%)
  - text on that page: `1.0  Final draft version  IDE  28/02/2020`
- Other labelled date: 2020-02-29 — Ares receipt on physicalp1 → 10.26% (same verdict)
- Repository publication date (not used): none
- [ ] issue date confirmed at the page   - [ ] scope noted

### late · `AGRICORE-D9.3-v1.0` · D9.3 Final Data Management Plan

- PDF: `data/paired-dmp-corpus/816078/AGRICORE-D9.3-v1.0.pdf` (807671 bytes, sha256 `b4081e3a26704a53…`)
- Chosen issue date: **2024-08-31** — Version History Date, v1.0 Final version; original string31-ago-2024 — physical PDF p2 → **103.51%** of the run (rule: late > 100%)
- Repository publication date (not used): none
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

Known uncertainties from the proposal:
- No local dominant branch exists; current CORDIS paths tie natural/agricultural; agricultural assignment permitted under D08.
- Early finaldraft revision28Feb2020 and Aresreceipt29Feb2020 are separate labelled dates, not proof that receipt is issue. Both lie in early window.
- Both PDFs retain original projectend31Aug2023, whereas latest CORDIS end30Jun2024 governs under D09.
- Unknown blanket document licence is not an extra exclusion under public-download inclusion criterion; no permission for model submission or public redistribution is inferred.

## social sciences — SUSTRACK (grant 101081823)

- Project run (latest authoritative end, D09): **2022-11-01 → 2025-10-31** (1095 days). End source: https://cordis.europa.eu/project/id/101081823
- CORDIS branches: natural sciences, social sciences; dominant: social sciences.
- Claim to check (agent review, `pair-review.json`): *Late physical p12 expressly describes updates since D7.1/M6; same project, WP7 and task T7.4.*
- Rights note: CC BY 4.0 in both freshly retrieved Zenodo record pages

### early · `zenodo:14497074` · Data Management Plan

- PDF: `data/paired-dmp-corpus/101081823/14497074.pdf` (960776 bytes, sha256 `f1220cde868b34a4…`)
- Record: https://zenodo.org/records/14497074
- Chosen issue date: **2023-04-29** — Submission date, version V6.0 — physical PDF p2 → **16.35%** of the run (rule: early ≤ 50%)
  - text on that page: `Submission date  29.04.2023`
- Other labelled date: 2023-04-27 — Document Revision History version 6.0, Final version — physical PDF p2 → 16.16% (same verdict)
- Repository publication date (not used): 2024-05-01
- [ ] issue date confirmed at the page   - [ ] scope noted

### late · `zenodo:19161966` · Data Management Plan (V2)

- PDF: `data/paired-dmp-corpus/101081823/19161966.pdf` (1340985 bytes, sha256 `701789cbd909a8bd…`)
- Record: https://zenodo.org/records/19161966
- Chosen issue date: **2026-02-06** — Document Revision History version 3.0 Revised version submission, agreeing with Submission date — physical PDF p2 → **108.95%** of the run (rule: late > 100%)
  - text on that page: `Submission date  06/02/2026`
  - text on that page: `3.0  06/02/2026  Revised version submission  UNIT`
- Repository publication date (not used): 2026-03-09
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

## humanities — RECHARGE (grant 101061233)

- Project run (latest authoritative end, D09): **2022-10-01 → 2025-09-30** (1095 days). End source: https://cordis.europa.eu/project/id/101061233
- CORDIS branches: medical and health sciences, humanities; dominant: humanities = medical and health sciences.
- Claim to check (agent review, `pair-review.json`): *Same project D6.1 and scope; final physical p2 expressly final update, preserving v1.1/v1.2 history; common Zenodo concept 17733865.*
- Rights note: CC BY 4.0 in both cached full Zenodo API metadata

### early · `zenodo:17733866` · RECHARGE: Data Management Plan

- PDF: `data/paired-dmp-corpus/101061233/17733866.pdf` (236054 bytes, sha256 `9556e4b789668a2f…`)
- Record: https://zenodo.org/records/17733866
- Chosen issue date: **2023-03-29** — Submission date in deliverable description — physical PDF p2 → **16.35%** of the run (rule: early ≤ 50%)
  - text on that page: `Submission date  29/03/2023`
- Other labelled date: 2023-03-31 — Revisions table V1.0 Submission version — physical PDF p5 → 16.53% (same verdict)
- Repository publication date (not used): 2025-11-27
- [ ] issue date confirmed at the page   - [ ] scope noted

### late · `zenodo:18403735` · RECHARGE: Data Management Plan (final update)

- PDF: `data/paired-dmp-corpus/101061233/18403735.pdf` (1114561 bytes, sha256 `bbbcd8847d7514ae…`)
- Record: https://zenodo.org/records/18403735
- Chosen issue date: **2026-02-02** — Date on cover, version 2.0 — physical PDF p1 → **111.42%** of the run (rule: late > 100%)
  - text on that page: `Date:  02 February 2026`
- Repository publication date (not used): 2026-01-28
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

Known uncertainties from the proposal:
- Early header 29Mar vs V1.0 revision-table31Mar is retained as same-bin interval.
- Final dated cover2Feb2026 occurs after repository publication/creation/update28Jan2026. Actual release chronology not resolved; cover date evidence retained without replacing it by publication.
- Initial p2 unrelated ENHANCED/D6.2 template header does not erase otherwise consistent cover/grant/body/D6.1 identity.
