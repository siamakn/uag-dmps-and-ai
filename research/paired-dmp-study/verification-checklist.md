# Verification checklist — six proposal pairs

Generated 2026-11-16 by `verification-checklist.py` from `cohort-proposal.json` and the local corpus. **Nothing here is verified.** A pair becomes *verified* in the dashboard only when a person has done the steps below and recorded them.

## How to use it

1. Start the dashboard: `python scripts/serve.py`. Choose *Paired study* and press **Load proposal** (once; it replaces an empty draft).
2. For each pair, open the PDFs listed below at the given physical pages (the page count of the PDF file, not the printed page number).
3. In the pair's **Evidence** editor:
   - **Same-scope descriptor**: what both documents cover, e.g. `project-wide DMP, whole consortium`. Enter the same text in each document's *Document scope* only if the document states it.
   - **Issue date** for each document: confirm the value at the locator. Under D16 an explicitly labelled issue / submission / delivery date wins, then a dated cover, then the version's revision-history row. If the PDF shows something else, correct the value and locator. Then set *Issue-date state* to `verified` and enter your name.
   - **Lineage**: confirm that the later document revises or succeeds the earlier one (revision table, 'updates D1.2', same deliverable series). Add an evidence entry (locator + one-line note), set *Lineage state* to `verified`, enter your name.
   - If something contradicts the proposal, set the state to `contradictory` and say why in *Notes*. The pair turns *rejected*; that is a valid outcome.
4. Press **Check files** (re-hashes the 12 PDFs on disk).
5. When all six pairs show *verified*, press **Freeze** (served mode only). The selection protocol is already approved (D20, 2026-11-09), so verified pairs are the only remaining requirement.

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
- Chosen issue date: **2025-09-05** — dated cover and Actual delivery date, version 1.0 — physical PDF p1 → **100.46%** of the run (rule: late = final DMP at ≥ 90%)
  - text on that page: `05/09/2025`
- Repository publication date (not used): 2025-09-05
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

Known uncertainties from the proposal:
- iMagine late is only5days after current CORDIS end; new authoritative end evidence could change qualification.

## engineering and technology — ColdSpark (grant 101069931)

- Project run (latest authoritative end, D09): **2022-06-01 → 2025-11-30** (1278 days). End source: https://cordis.europa.eu/project/id/101069931
- CORDIS branches: engineering and technology; dominant: engineering and technology.
- Claim to check (agent review, `pair-review.json`): *Late physical p4: 'Build on the M6 and M24 versions, this final DMP consolidates the practices implemented by all consortium partners'. Both are project deliverables D8.x 'Data Management Plan' of the whole consortium (M6 and M42).*
- Rights note: CC BY 4.0 on both Zenodo records. Both PDFs carry '© ColdSpark Consortium' without a reuse statement.

### early · `zenodo:14178018` · ColdSpark project Deliverable D8.2. Data Management Plan (M6)

- PDF: `data/paired-dmp-corpus/101069931/14178018.pdf` (350345 bytes, sha256 `5557d39f89d7d4c4…`)
- Record: https://zenodo.org/records/14178018
- Chosen issue date: **2022-11-30** — Issue date on cover page (also Ares stamp 30/11/2022) — physical PDF p1 → **14.24%** of the run (rule: early ≤ 50%)
  - text on that page: `Ref. Ares(2022)8284060 - 30/11/2022`
  - text on that page: `Due date  30 November 2022`
  - text on that page: `Issue date  30 November 2022`
- Repository publication date (not used): 2024-11-18
- [ ] issue date confirmed at the page   - [ ] scope noted

### late · `zenodo:19845992` · ColdSpark Project Deliverable D8.4 Data Management Plan (M42)

- PDF: `data/paired-dmp-corpus/101069931/19845992.pdf` (587381 bytes, sha256 `0c20384b7afa7f28…`)
- Record: https://zenodo.org/records/19845992
- Chosen issue date: **2025-11-29** — Issue date on cover page (also Ares stamp 29/11/2025) — physical PDF p1 → **99.92%** of the run (rule: late = final DMP at ≥ 90%)
  - text on that page: `Ref. Ares(2025)10485399 - 29/11/2025`
  - text on that page: `Issue date  29.11.2025`
- Repository publication date (not used): 2026-04-28
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

Known uncertainties from the proposal:
- Final DMP is dated one day before the project end (99.92%); it qualifies only under D23.
- An intermediate M24 version (Zenodo 15543633) exists and is not used.
- PDF copyright line and the Zenodo CC BY licence are both retained; the depositor's licence is taken as the reuse basis.

## medical and health sciences — BY-COVID (grant 101046203)

- Project run (latest authoritative end, D09): **2021-10-01 → 2024-09-30** (1095 days). End source: https://cordis.europa.eu/project/id/101046203
- CORDIS branches: medical and health sciences; dominant: medical and health sciences.
- Claim to check (agent review, `pair-review.json`): *Late physical p3: 'This document builds on the previous versions of the Data Management Plan' and 'is the third version of the BY-COVID DMP delivered in month 34, being an update of the second version delivered in month 15'; it cites D8.2 (the early document) by title. Same deliverable series D8.2.*
- Rights note: CC BY 4.0 on both Zenodo records.

### early · `zenodo:6884816` · BY-COVID - D8.2 - Data Management Plan

- PDF: `data/paired-dmp-corpus/101046203/6884816.pdf` (2263145 bytes, sha256 `a4c2196eee2c98db…`)
- Record: https://zenodo.org/records/6884816
- Chosen issue date: **2022-03-30** — Actual Delivery date on cover page — physical PDF p1 → **16.44%** of the run (rule: early ≤ 50%)
  - text on that page: `Contractual delivery date 31/03/2022  Actual Delivery  30/03/2022`
- Repository publication date (not used): 2021-03-31
- [ ] issue date confirmed at the page   - [ ] scope noted

### late · `zenodo:13981358` · BY-COVID D8.2.3 Project Data Management Plan initial release and periodic updates

- PDF: `data/paired-dmp-corpus/101046203/13981358.pdf` (839741 bytes, sha256 `1404606e9c84b9d9…`)
- Record: https://zenodo.org/records/13981358
- Chosen issue date: **2024-07-31** — Actual Delivery date on cover page (also Ares stamp 31/07/2024) — physical PDF p1 → **94.43%** of the run (rule: late = final DMP at ≥ 90%)
  - text on that page: `Ref. Ares(2024)5554962 - 31/07/2024`
  - text on that page: `Contractual delivery date 31/07/2024  Actual Delivery  31/07/2024`
- Other labelled date: 2024-07-19 — Log of changes: 'Final version' (physical p2) → 93.33% (same verdict)
- Repository publication date (not used): 2024-10-23
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

Known uncertainties from the proposal:
- Final DMP was delivered two months before the project end (94.43%); it qualifies only under D23 and is the lowest late position in the set.
- The early record's Zenodo publication date reads 2021-03-31, before the project started; the record was created 2022-07-22 and the document itself says 30/03/2022. The document date is used.
- A second version D8.2.2 (Zenodo 7476926, delivered 2022-12-23, 40.9%) exists and is not used.
- The WP5 use-case DMPs on Zenodo are a different scope and are not part of this pair.

## agricultural sciences — ASTEP (grant 884411)

- Project run (latest authoritative end, D09): **2020-05-01 → 2025-06-30** (1886 days). End source: https://cordis.europa.eu/project/id/884411
- CORDIS branches: agricultural sciences, engineering and technology; dominant: agricultural sciences = engineering and technology.
- Claim to check (agent review, `pair-review.json`): *Early physical p2: 'This is the initial Report of ASTEP's Data Management Plan D9.6'. Late physical p2: 'This is the follow-up report of the ASTEP's Data Management Plan (DMP) D9.6 ... being the current deliverable the last update'. Same deliverable D9.6 (D9.6.1 and D9.6.3), whole project.*
- Rights note: CC BY 4.0 on both Zenodo records. Both PDFs say '© ASTEP Consortium. All rights reserved.' The two statements conflict; the depositor's Zenodo licence is taken as the reuse basis and the conflict is recorded.

### early · `zenodo:5772790` · D9.6.1 Data Management Plan

- PDF: `data/paired-dmp-corpus/884411/5772790.pdf` (744985 bytes, sha256 `fa37f2cb2d249483…`)
- Record: https://zenodo.org/records/5772790
- Chosen issue date: **2020-10-31** — Submission date in the document summary — physical PDF p1 → **9.70%** of the run (rule: early ≤ 50%)
  - text on that page: `Submission date  2020-10-31  Due date  2020-10-31`
- Other labelled date: 2020-10-30 — Revision history V3.1 'Final changes after peer review' (physical p3) → 9.65% (same verdict)
- Repository publication date (not used): 2020-10-30
- [ ] issue date confirmed at the page   - [ ] scope noted

### late · `zenodo:16411304` · D9.6.3 'Data Management Plan'

- PDF: `data/paired-dmp-corpus/884411/16411304.pdf` (834284 bytes, sha256 `35eeee9492f7db3f…`)
- Record: https://zenodo.org/records/16411304
- Chosen issue date: **2025-07-24** — Submission date in the document summary — physical PDF p1 → **101.27%** of the run (rule: late = final DMP at ≥ 90%)
  - text on that page: `Submission date  2025-07-24  Due date  2025-6-30`
- Other labelled date: 2025-06-26 — Revision history V3.0 'Last release of the deliverable' (physical p3) → 99.79% (same verdict)
- Repository publication date (not used): 2025-07-24
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

Known uncertainties from the proposal:
- CORDIS paths tie agricultural (dairy) and engineering (solar thermal); the local dataset's dominant branch is agricultural. The project is a solar-heat project with a dairy application.
- Late: submission date 2025-07-24 (101.27%) and last revision row 2025-06-26 (99.79%) both qualify under D23.
- CORDIS duration is 62 months; the early PDF plans updates at M24 and M48, which suggests an extension. The amendment history was not reviewed.
- An intermediate version D9.6.2 (Zenodo 8161456) exists and is not used.
- Conflicting rights statements (PDF versus Zenodo record), as noted under licence.

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
- Chosen issue date: **2026-02-06** — Document Revision History version 3.0 Revised version submission, agreeing with Submission date — physical PDF p2 → **108.95%** of the run (rule: late = final DMP at ≥ 90%)
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
- Chosen issue date: **2026-02-02** — Date on cover, version 2.0 — physical PDF p1 → **111.42%** of the run (rule: late = final DMP at ≥ 90%)
  - text on that page: `Date:  02 February 2026`
- Repository publication date (not used): 2026-01-28
- [ ] issue date confirmed at the page   - [ ] scope noted

- [ ] lineage confirmed (later revises earlier, same scope)   - [ ] Check files run

Known uncertainties from the proposal:
- Early header 29Mar vs V1.0 revision-table31Mar is retained as same-bin interval.
- Final dated cover2Feb2026 occurs after repository publication/creation/update28Jan2026. Actual release chronology not resolved; cover date evidence retained without replacing it by publication.
- Initial p2 unrelated ENHANCED/D6.2 template header does not erase otherwise consistent cover/grant/body/D6.1 identity.
