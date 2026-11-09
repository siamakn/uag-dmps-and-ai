# Platform implementation results — paired DMP study

Implemented 2026-11-04 by Claude (Opus 5.5) from
[`claude-platform-brief.md`](claude-platform-brief.md). This file records what was built, how it
was tested, what was preserved, and what remains undecided. **No pair has been verified and no
cohort is frozen.** Verification needs a person to record evidence in the dashboard.

## 1. State preserved before any change

| item | value |
|---|---|
| legacy selection | `data/selection.json`, untracked, 12 ids from 12 grants |
| SHA-256 before work | `a4a54dba18af7d8a28c1b60e4c317921c7768573735adcd7d44eafa66007edeb` |
| byte-preserving backup | `data/backups/selection.legacy-2026-11-02.json` (same hash; `data/backups/` is git-ignored) |
| SHA-256 after all tests | `a4a54dba18af7d8a28c1b60e4c317921c7768573735adcd7d44eafa66007edeb` (unchanged) |

The legacy file is never written by the paired study. The served self-test can no longer reach it:
`/selftest` returns 409 unless `serve.py` runs with `--test` or `--state-dir`. The Python suite
asserts the hash is unchanged after its run. `research/paired-dmp-study/verify-cohort.py` (which
checks the same hash) still passes.

Two legacy behaviours changed so that ids are never discarded silently. Neither alters the
current file's 12 ids, which all resolve:
- the server now keeps ids that the dataset does not know, adding an `unresolved` list instead of
  dropping them;
- the page no longer filters unknown ids out of the in-memory selection. The legacy tray notes how
  many it is holding.

## 2. What was built

| file | change |
|---|---|
| `scripts/paired.py` | **new.** Study schema (`dmpbench.paired-study` v1), protocol defaults, exact timing, validation, CSV/Markdown/JSON export, local file checks, downloads limited to `data/paired-dmp-corpus/`, immutable freeze plus snapshot verification, cohort-proposal → draft conversion, registry seeding, legacy → historical import. Module and CLI. |
| `scripts/06_discover_versions.py` | **new.** `groups` (whole pool by grant, no publication-date window), `versions` (Zenodo version chains, paged, cached, coverage and failures recorded), `register` (external document → registry with provenance). |
| `scripts/07_fetch_study_files.py` | **new.** Checks, downloads and hashes only explicitly selected files. Reports checksum mismatches and never replaces a recorded checksum. |
| `scripts/test_paired.py` | **new.** 33 unittest cases (stdlib), temporary directories only. |
| `data/study-documents.json` | **new, tracked.** Registry of the three proposal documents absent from the dataset: `zenodo:17733866` (RECHARGE early, found through Zenodo concept 17733865), `AGRICORE-D9.2-v1.0` and `AGRICORE-D9.3-v1.0` (project website; `record_id` null, no Zenodo id invented). Each has its source URL, SHA-256, byte count and local path. |
| `dashboard/paired-fixtures.json` | **new.** Shared timing cases, expected CSV/Markdown escaping (generated from Python) and a synthetic valid six-pair cohort. |
| `dashboard/template.html` | Paired-study mode (default) beside *Legacy 3×3*: assignment menu per row, registry documents as candidates, six-row panel, evidence editor, protocol panel, exports, load JSON, attach/detach legacy, file check/fetch, freeze. JavaScript mirror of timing, validation and export. Publication positions above 100% are printed in full. Guide, preset and tooltip text updated. New `__PAIRED__` boot block. |
| `dashboard/selftest.js` | Legacy tests pinned to legacy mode. Browser storage snapshotted and restored. New paired block (see §6). |
| `scripts/serve.py` | `/api/paired` GET/PUT, `/validate`, `/files`, `/freeze`, `/snapshots`. `--state-dir` and `--test` options. `/selftest` guard. Corrupt-file protection. Unknown legacy ids kept. |
| `scripts/common.py` | `slim()` keeps concept id/DOI, version index, related identifiers and file checksums for future harvests. `DASHBOARD_FIELDS` adds `version` and `stage_src`. `boot_json()` and `selftest_block()` helpers. |
| `scripts/05_build_dashboard.py` | Fills `__PAIRED__`. `--selftest OUT` writes a standalone test build and refuses to overwrite `dashboard/dashboard.html`. |
| `dashboard/dashboard.html` | Regenerated with `python3 scripts/05_build_dashboard.py`. Not hand-edited. |
| `data/.gitignore` | Ignores `backups/`, `paired-discovery/cache/`, set-aside corrupt drafts, `*.tmp`. |
| `AGENTS.md`, `README.md`, `scripts/README.md`, this directory's `README.md` | Updated to describe the platform. Existing research reports are untouched apart from one index row. |

Nothing was added outside the Python stdlib and vanilla JavaScript. No scoring, AI review,
review GUI or new web stack was built.

## 3. Data model

A draft is one JSON object (`schema: "dmpbench.paired-study"`, `schema_version: 1`,
`status: "draft"`). It is stored in `data/paired_selection.json` when served and under the
browser key `dmpbench.paired.v1` when standalone. The legacy selection keeps its own file and its
own key (`dmpbench.sel`), and the mode switch uses `dmpbench.mode`.

- **protocol**: id, `approved` / by / on, six disciplines, issue-date timing basis,
  `publication_date_fallback: false`, early rule `2n <= d`, late rule `n > d`, proposed lower bound
  `n >= 0`, pre-start policy (`exclude`, *proposed*), D08 and D09 as *confirmed*, and four open
  decisions (each `open` / `resolved` / `not_material`, with a note).
- **pairs**: six fixed rows in discipline order. Each row has a stable `pair_id` (the discipline
  slug), `project` (grant, acronym, programme, start, latest end, end basis, original end, end
  source URL/hash/path), `cordis` (branches, paths, dominant branches with ties, source), `scope`,
  `early` / `late` document ids, `lineage` (state, evidence list of locator + note, verified by/on,
  prior agent checks) and `notes`.
- **documents**: keyed by stable document id (`zenodo:<record>` or a registry id). Each has record
  id/URL, DOI, version label, title, grant, scope, publication date, `issue_date` (value with its
  precision kept, label, locator, source URL, state, verified by/on), alternative labelled dates,
  `files` (name, URL, format, bytes, local SHA-256, repository checksum, retrieval time, local
  path, licence, access state, analysis flag) and prior checks.
- **historical** (optional): the legacy selection attached as `historical, unverified; confers no
  eligibility or selection priority`. Every id is kept, with unresolved ids listed. It fills no
  slot and can be detached.
- **Verification states** everywhere: `not_checked`, `verified`, `contradictory`, `unavailable`.
  Unknown values stay `null`.

A snapshot (`dmpbench.paired-snapshot`) contains the study (status `frozen`), its validation, the
file manifest with recorded and locally re-computed SHA-256, the SHA-256 of `data/dmp_dataset.json`,
`data/study-documents.json` and `cohort-proposal.json`, a `content_sha256` over the canonical body,
and CSV/MD derivatives. Snapshots are created with `O_EXCL`, so an existing one is never rewritten.
Source files are referenced by repo-relative path and checksum, not included.

## 4. Rules as implemented

**Timing.** `n = issue − project start` and `d = latest end − start`, in whole days.
- Early is `0 <= n` and `2n <= d`.
- Late is `n > d`.

Integer comparisons decide everything; percentages are only for display. A date exactly at the
end is 100% and is not late. Partial dates (`YYYY`, `YYYY-MM`) become an interval of possible
days: the verdict is `yes` only if every possible day passes, `no` if none does, otherwise
`indeterminate`. A missing issue date is `unknown`. There is no fallback to the publication date.
Publication-date positions remain in the table, labelled as a discovery aid.

**Validation.** A pair is *verified* only when none of the conditions below applies. *Pending*
means evidence is missing. *Rejected* means a hard failure.

- Pending:
  - no project, empty slot or missing project dates;
  - no CORDIS branch recorded;
  - scope not recorded;
  - issue date missing, without a locator, or not verified by a person;
  - timing unknown or indeterminate;
  - an alternative labelled date that would flip the verdict;
  - lineage not verified, or marked verified without evidence;
  - no checksummed file, or several files with no analysis file chosen.
- Rejected:
  - timing fails, or a date or duration is invalid;
  - the same document in both roles, or a document reused in another slot;
  - a project reused in another discipline;
  - a document grant that differs from the pair's grant;
  - the two documents record different scopes (same grant, different partner);
  - two study documents with identical bytes;
  - the assigned discipline is not among the project's CORDIS branches;
  - any evidence marked contradictory or unavailable;
  - a file that failed to download or no longer matches its checksum.

The cohort is freezable only with six verified pairs, an approved protocol, no open decision, and,
if any document predates its project, a confirmed pre-start policy. The server's freeze also
re-hashes every selected file on disk. Two documents from one grant are never auto-verified as a
pair, and a second version from the same project raises no duplicate warning.

**Consistency between Python and JavaScript.** Both run the 18 shared timing fixtures and the
escaping expectations. The served suite posts the synthetic cohort and 18 mutations to
`/api/paired/validate` and requires identical pair statuses, issue code/severity sets and counts.

## 5. The cohort proposal inside the platform

**Load proposal** (or `python3 scripts/paired.py proposal`) turns `cohort-proposal.json` into a
draft:
- 6 projects and 12 distinct documents, all at **pending**;
- 0 verified pairs and 0 verified issue dates;
- the agent checks from `pair-review.json` are kept as `prior_checks`, and its lineage notes as
  evidence entries.

The issue date is chosen by the D16 hierarchy (§7b): an explicitly labelled issue / submission /
delivery date, then the dated cover, then the revision-history row. The other labelled dates
become alternatives. Each computed day count equals the proposal's `numerator_days` for the chosen
date, which is asserted in `test_paired.py`. Positions shown:

| project | early | late |
|---|---|---|
| iMagine | 17.26% | 100.46% |
| EGI-ACE | 23.63% | 114.40% |
| NANOFACTS | 14.11% | 107.13% |
| AGRICORE | 10.20% | 103.51% |
| SUSTRACK | 16.35% | 108.95% |
| RECHARGE | 16.35% | 111.42% |

`python3 scripts/07_fetch_study_files.py --proposal` result: **12 ok, 0 missing, 0 mismatched.**
Every local PDF in `data/paired-dmp-corpus/` matches its recorded SHA-256.

What a person must still do in the dashboard for each pair:
1. Record the same-scope descriptor.
2. Read and verify both issue dates at their locators.
3. Mark lineage verified, with their name and the date.
4. Run **Check files**.

Separately, the group must approve the protocol and settle the open decisions. Only then will
**Freeze** succeed.

## 6. Commands run and actual results

Environment: Linux, Python 3.14.4, Google Chrome headless.

```bash
python3 scripts/test_paired.py
#   Ran 33 tests ... OK

python3 scripts/05_build_dashboard.py --selftest $TMP/st.html
google-chrome --headless=new --user-data-dir=$TMP/prof --dump-dom "file://$TMP/st.html"
#   SELFTEST 293/293 fail=0 skip=2
#   (skipped: legacy API round trip, paired API persistence - no API in a standalone build)
google-chrome --headless=new --user-data-dir=$TMP/prof --dump-dom "file://$TMP/st.html?phase=reload"
#   SELFTEST 3/3 fail=0 skip=0   (draft survives a real page reload; marker removed)

python3 scripts/serve.py --test --no-open --port 8790
google-chrome --headless=new --user-data-dir=$TMP/prof2 --dump-dom "http://127.0.0.1:8790/selftest"
#   SELFTEST 319/319 fail=0 skip=0
google-chrome --headless=new --user-data-dir=$TMP/prof2 --dump-dom "http://127.0.0.1:8790/selftest?phase=reload"
#   SELFTEST 3/3 fail=0 skip=0

python3 scripts/serve.py --no-open --port 8791 ; curl http://127.0.0.1:8791/selftest
#   409 "/selftest writes and clears selections, so it will not run against data/ ..."

python3 research/paired-dmp-study/verify-cohort.py
#   PASS: six distinct projects, six disciplines, twelve distinct PDF hashes, ... historical
#   dashboard selection unchanged.

python3 scripts/07_fetch_study_files.py --proposal
#   12 ok, 0 missing, 0 mismatched
```

The 319 served assertions include the original legacy checks, updated for the mode switch. Do not
compare them with the old "180 assertions" figure; that suite has changed.

Acceptance criteria from the brief, as tested:

| # | criterion | where |
|---|---|---|
| 1 | legacy file byte-identical; 12 ids recoverable; separate browser namespaces | `test_paired.py` (hash), backup, selftest (`dmpbench.sel` vs `dmpbench.paired.v1`) |
| 2 | synthetic valid cohort passes; incomplete saveable but not freezable, with reasons | both suites |
| 3 | partner scope, repeated bytes, project in two disciplines, document in two roles fail; second version does not | both suites + served cross-check |
| 4 | 0%, 50%, >50%, exactly 100%, end+1 day, >100% display, partial dates, invalid/missing duration, pre-start, deposit-after-end, missing issue date | shared fixtures + mutations |
| 5 | DOM clicks: assignment/removal, evidence editing, filters after presets, save/reload, legacy import, export, error recovery | selftest |
| 6 | served and standalone share fields and validation; served API only against temporary storage; standalone persistence actually tested | both runs; `/selftest` guard; two-phase reload |
| 7 | JSON round trip keeps assignments, provenance, unknowns, day counts; CSV/MD escaping; snapshot checksum stable and tamper-evident | both suites |
| 8 | rebuilt from template; tests run and recorded; `allow_reuse_address = False` and branch/sub-field pairing kept | this section; legacy assertions still pass |

## 7. Discovery run

`python3 scripts/06_discover_versions.py groups`:
- 2,504 actual plans, 1,503 of them with a grant number, in 1,148 grant groups;
- **225 groups have 2+ records, 173 of them with a CORDIS branch.**

These are candidate groups, not pairs.

`python3 scripts/06_discover_versions.py versions` (scope: the 1,503 plans with a grant number,
one request per second, cached under `data/paired-discovery/cache/`), completed 2026-11-04:

| measure | value |
|---|---|
| records in scope / processed | 1,503 / 1,503 |
| concepts fetched | 1,503 |
| failures | 0 |
| incomplete pagination | 0 |
| concepts with 2+ versions | **226** (127 of them for projects with a CORDIS branch) |
| versions absent from the saved harvest | **331**, spread over all 226 multi-version concepts |
| versions per multi-version concept | 2 (158), 3 (47), 4 (12), 5 (6), 7 (2), 8 (1) |

**Finding: the saved harvest is almost entirely latest versions.** Zenodo search returns only the
latest version of each concept. As a result:
- the 1,503 granted plans fall into 1,503 distinct concepts;
- 210 of the 226 in-dataset records in multi-version concepts are the latest version;
- every earlier version is missing from `data/dmp_dataset.json`.

This is the main reason the saved pool looked thin for early documents. The run recovers the
RECHARGE early version (17733866) that the proposal found by hand, which supports the method. The
leads, with file names, repository checksums and content links, are in
`data/paired-discovery/versions.json`. A lead becomes a candidate in the dashboard only once
registered (`06_discover_versions.py register`). That step was not done in bulk: it is a selection
decision, not a mechanical one.

Zenodo API behaviour verified before relying on it:
- anonymous requests reject `size=100` with HTTP 400, so the script uses the shared page size (25
  anonymous, 100 with `ZENODO_TOKEN`);
- `links.next` is absent on a single page, and pages beyond the end return empty hits; the
  script pages until the reported total;
- the legacy JSON serialisation carries the parent concept id, version index, file checksums and
  content links, whereas the InvenioRDM serialisation omits content links.

A known blind spot confirmed on real data: iMagine D1.2 (7759984) and D1.4 (17055683) are separate
concepts, each with `total: 1`. Version chains are one lead among several, and absence from them
proves nothing.

## 7b. Follow-up on 2026-11-06

The user answered the open questions interactively.

- **Protocol decisions D16–D19 confirmed** (recorded in `decisions.md`; the research agent had
  already used D15 the same day). They cover the issue-date hierarchy, partial dates as intervals,
  the PDF as analysis file, and excluding pre-start documents. The protocol panel now shows all four
  as resolved, with the pre-start policy confirmed. `scripts/paired.py:date_rank` applies the
  hierarchy on import. It moves two chosen early dates, with no verdict changing:
  - iMagine: unlabelled cover 2023-02-28 → labelled delivery date 2023-03-09 (17.26%);
  - SUSTRACK: revision row 2023-04-27 → submission date 2023-04-29 (16.35%).

  It reproduces the proposal's own hand-chosen NANOFACTS date. The protocol as a whole was
  not yet approved at that point (it was approved on 2026-11-09, D20; see below).
- **Verification checklist**: [`verification-checklist.md`](verification-checklist.md), generated by
  `verification-checklist.py`. For each pair it gives the PDF paths and hashes, the chosen issue
  date with label and physical page, the extracted-text line at that page (found for all 12), other
  labelled dates and whether they would change the verdict, the lineage claim to check, and
  tick-boxes. It tells the verifier what to enter in the dashboard. Nothing is marked verified.
- **Reserve shortlist**: [`lead-shortlist.md`](lead-shortlist.md) / `.json`, generated by
  `lead-triage.py` from the version-chain run. Of 226 multi-version concepts:
  - 99 lack a CORDIS discipline or dates;
  - 109 have no version deposited after the project end, and so can never supply a late document;
  - **18 remain**: 6 tier A (early by deposit date), 6 tier B, 6 tier D.

  The screen independently re-finds two proposal pairs, EGI-ACE and RECHARGE. Reserves outside the
  proposal exist for every discipline, including agricultural sciences (PAPILLONS, tier B) and
  humanities (RitualModes, GOLDEN-ROM, tier D). Nothing was registered or selected.

**2026-11-09: protocol approved (D20).** The user approved the selection protocol (issue-date
timing, D08, D09, D16–D19). The approval is recorded in `scripts/paired.py:default_protocol` with
its scope: selection only, not the experiment protocol. On the proposal draft the cohort now
reports a single remaining blocker: `0 of 6 pairs verified`.

## 8. Limitations

- **Verification is manual by design.** The platform records evidence; it cannot read PDFs. No
  PDF parsing or OCR was added.
- **Project ends added from the dataset are not D09-checked.** When a document is assigned from
  the table, the project end comes from the local CORDIS bulk snapshot. Extensions are not
  checked, and the row's end basis says so. The proposal's six pairs carry the checked CORDIS end
  dates and snapshot hashes.
- **Same-scope checking is only as good as what people record.** Scope mismatch is detected from
  the recorded scope strings. Two different partner plans with empty scope fields stay *pending*
  (scope not recorded), not *rejected*.
- **Standalone mode cannot read files from disk.** It cannot hash files or freeze, and it says so.
  Its drafts live only in that browser.
- **Running both writers at once loses updates.** `07_fetch_study_files.py --write` and an open
  dashboard on the same draft overwrite each other. The dashboard's *Check files* button avoids
  this.
- **Timing and validation exist in two languages.** The shared fixtures and the served
  cross-check guard against drift, but a rule change must be made in both.
- **Date precision covers ISO forms only.** `YYYY`, `YYYY-MM` and `YYYY-MM-DD` are understood.
  Other formats (`28/02/2020`) must be normalised by the person entering them; the original string
  can go in the label.
- **Python 3.7 compatibility is unverified.** The tests ran on 3.14; the code avoids features
  newer than 3.7, but no 3.7 run was done.

## 9. Decisions still needed before a freeze

These match the protocol panel's open decisions. None was resolved here.

Items 1–4 were settled on 2026-11-06 as D16–D19 (see §7b). What remains:

1. ~~Issue-date evidence hierarchy~~: D16.
2. ~~Partial-date interpretation~~: D17.
3. ~~Representation~~: D18.
4. ~~Pre-start policy~~: D19.
5. ~~Protocol approval~~: approved by Siamak Nakhaie on 2026-11-09 (D20), covering selection only.
6. **Per-pair human verification** of scope, both issue dates and lineage (the four steps in §5),
   plus a decision on the AGRICORE model-submission terms and the FAIR-EASE rights clarification
   before any model run.
