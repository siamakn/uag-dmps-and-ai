# AGENTS.md — orientation for AI assistants

**Active study update (2026-11-04):** Read
[`research/paired-dmp-study/README.md`](research/paired-dmp-study/README.md) and its
decision/status files first for the current research task. The user now requests six
distinct projects across all six disciplines, each with two same-scope DMP versions
(twelve documents), using documented issue dates at ≤50% and >100% of project duration.
This supersedes the historical selection design below, while repository conventions
remain applicable. `data/selection.json` currently exists and must be preserved; it is
a historical twelve-project shortlist, not six verified pairs. A new six-pair
working proposal is now documented in
[`cohort-proposal.md`](research/paired-dmp-study/cohort-proposal.md), prepared
2026-11-04 with independent provenance checks; human reference labels and experiment
freeze remain pending. Source PDFs are retained separately in the ignored local
`data/paired-dmp-corpus/` directory.

**Platform status (2026-11-04):** the selection platform now supports the paired study —
`scripts/paired.py` (schema, exact timing, validation, freeze), a *Paired study* mode in the
dashboard (six discipline rows × early/late slots, evidence editor, validation, separate
storage), `scripts/06_discover_versions.py` and `scripts/07_fetch_study_files.py`. What was
built, how it was tested and what is still undecided is in
[`claude-platform-results.md`](research/paired-dmp-study/claude-platform-results.md). No pair
is verified and nothing is frozen: verification needs a person to record evidence.

Read this before answering questions about this repository or changing anything in it.
It is written for an AI assistant working with someone who has just cloned the repo.
Everything here was verified against the data in the repo, not assumed.

---

## 1. What this repository is

A working repository for one part of the **UAG work on DMPs and AI**, maintained by Siamak
Nakhaie (FAIRmat, HU Berlin) and Andrej Berg (JGU Mainz). It does not cover everything the
UAG does.

Code and documentation are MIT-licensed; the derived dataset is CC BY 4.0; the downloaded
maDMP files in `data/madmp-corpus/` keep their depositors' own licences and cannot be
relicensed. See `LICENSE`.

The concrete goal: build a small, transparent **test set of ~10 open Data Management Plans**
that can be used to evaluate automated and AI-assisted DMP review tools. The selected DMPs
will be reviewed manually against the Infra-DMP criteria matrix
(https://doi.org/10.5281/zenodo.19630859); those manual reviews become the reference
standard that automated review can be compared against.

So the repo is **not** a DMP review tool. It is the machinery for *choosing what to review*:
harvest a candidate pool, enrich it with the metadata the selection criteria need, and give a
human a dashboard to pick from.

**Current status:** the pool is built and the dashboard works. The historical 10-DMP design was
superseded by the paired study (see the top of this file). `data/selection.json` exists, is
untracked, and holds a historical 12-record pick from 12 grants (2026-11-02); it is preserved
byte-for-byte (backup in `data/backups/`) and confers nothing on the paired study. The paired
draft lives in `data/paired_selection.json` (absent until someone saves one).

### Selection criteria (the spec everything serves)

- 10 open DMPs
- Prefer machine-actionable DMPs (maDMPs) with structured JSON / RDA-DCS
- Prefer Horizon Europe over Horizon 2020
- Prefer recent DMPs, ideally 2024 or newer
- Select on **metadata, not on perceived DMP quality** — this is the load-bearing constraint
- Cover 3 broad scientific disciplines
- Cover 3 project lifecycle stages: early, mid, late/final
- Target a 3 × 3 matrix = 9 DMPs
- Add 1 challenging DMP: personal/sensitive data, GDPR or ethical constraints, restricted access
- DMPs must be openly accessible and downloadable
- Prefer sources with a large candidate pool and API-accessible metadata

The "metadata, not quality" rule is why both axes come from external authorities rather than
judgement: **discipline** is the project's EuroSciVoc classification in CORDIS, and **lifecycle
stage** is arithmetic on the CORDIS project start and end dates. Do not propose selection
heuristics based on how good a DMP looks — that would defeat the design.

---

## 2. What the product currently does

### Harvesting pipeline (`scripts/`)

Five re-runnable steps, plain Python 3, **no third-party dependencies**. Downloads already on
disk are skipped, so re-running is cheap.

| step | does | writes |
|---|---|---|
| `01_harvest_records.py` | five Zenodo API queries for DMP records | `data/raw/*.jsonl` |
| `02_download_madmps.py` | downloads candidate `.json` files, keeps the real maDMPs | `data/madmp-corpus/` |
| `03_check_schema.py` | checks each maDMP against RDA DMP Common Standard 1.2 | `data/schema_findings.json` |
| `04_build_dataset.py` | joins Zenodo records to CORDIS, derives discipline and lifecycle | `data/dmp_dataset.{json,csv}` |
| `05_build_dashboard.py` | embeds the dataset in a standalone HTML page | `dashboard/dashboard.html` |
| `06_discover_versions.py` | paired study: groups plans by grant, walks Zenodo version chains, registers external documents | `data/paired-discovery/`, `data/study-documents.json` |
| `07_fetch_study_files.py` | paired study: checks, fetches and hashes only the selected files | `data/paired-dmp-corpus/` |
| `paired.py` | paired-study schema, timing, validation, export, freeze (module + CLI) | `data/paired-snapshots/` |
| `serve.py` | runs the dashboard locally with a small JSON API | serves `/`, writes `data/selection.json` and `data/paired_selection.json` |

### Dashboard

Two ways to run, one shared template (`dashboard/template.html`):

- **Served** — `python scripts/serve.py`, UI on `http://127.0.0.1:8756`. Rows come from the API;
  the selection is written to `data/selection.json` on every change; maDMP files are served from
  the local corpus so inspecting one needs no round trip to Zenodo.
- **Standalone** — open `dashboard/dashboard.html`. The whole dataset is embedded, so it works
  offline; the selection lives in browser storage only.

Features:

- Filter by **record kind** (actual DMP / template / guidance / about / unclear — defaults to
  actual DMPs only), funder tier, publication year range, format, **discipline branch and its
  EuroSciVoc sub-field**, lifecycle stage,
  sensitive-data flags, and full-text search across title, project, grant, DOI, call id and
  description
- **Metadata sheet** on every row: click a title for authors, abstract, DOI, Zenodo type, project
  and run dates, call, all funders, discipline and sub-fields, keywords, maDMP statistics, and the
  file list with sizes and direct links
- Four presets that set every filter at once
- Sortable columns — click a header, click again to reverse
- **Editable columns**: 14 available, 8 shown by default; show/hide, reorder, reset. Choice
  persists in browser storage. The checkbox and DMP-title columns are locked.
- Live 3 × 3 coverage matrix over the current selection, plus a challenging-case slot
- Warnings for duplicate projects, a fourth discipline, missing lifecycle stage, and going over 10
- Export as Markdown table, CSV or JSON (clipboard, with a visible fallback box)
- **Hover documentation on every control** — filter chips, column headers, column-editor rows,
  coloured tags and counters each carry a one-line explanation; keyboard focus shows it too,
  Escape dismisses. A **Guide** button opens a short panel about the pool and the two axes.
- Light and dark themes, responsive down to a single column
- **Two modes** (header switch, remembered in `dmpbench.mode`): *Paired study* (default) and
  *Legacy 3×3*. Paired mode replaces the row checkbox with an assignment menu, shows registry
  documents as extra candidates, and swaps the tray for six discipline rows with early/late
  slots, per-pair status (empty / pending / verified / rejected) and the reasons, an evidence
  editor (scope, lineage with locators, issue dates with page locators and verification state,
  analysis file), a protocol panel, exports, file checks and **Freeze** (served only). The legacy
  matrix, duplicate-project warning and challenging slot only appear in legacy mode.
- Paired storage is separate: `data/paired_selection.json` served, `dmpbench.paired.v1` standalone.
  A corrupt or unsupported draft blocks the panel instead of being overwritten.

### Test suite

Three layers, all stdlib / headless Chrome. Results recorded in
`research/paired-dmp-study/claude-platform-results.md`.

- `dashboard/selftest.js` — the browser suite. Served only at `/selftest` (or in a standalone
  test build), never part of a shipped page. It drives the real UI through the internal API and
  real DOM clicks: the original filters/sorting/columns/selection/matrix/export/tooltip checks
  (run in legacy mode), plus the paired study — shared timing fixtures, escaping, a synthetic
  six-pair cohort and 18 failing mutations, assignment/removal through the table, the evidence
  editor, exports and JSON round trip, malformed input, legacy import, browser-storage
  persistence and corruption recovery, and (served) Python-vs-JS validation agreement, API
  persistence, freeze refusal and a real two-page reload. **The harness writes and clears
  selections, so `/selftest` refuses to run unless the server uses a temporary state dir.**
- `scripts/test_paired.py` — unittest for timing, validation, exports, freeze immutability,
  legacy import and the server endpoints, all against temporary directories. It asserts that
  `data/selection.json` is byte-identical afterwards.
- `dashboard/paired-fixtures.json` — the timing cases, escaping expectations and synthetic cohort
  both suites share, so the Python and JavaScript rules cannot drift apart unnoticed.

```bash
python scripts/test_paired.py
python scripts/serve.py --test --no-open --port 8790          # temporary state dir
chrome --headless=new --dump-dom "http://127.0.0.1:8790/selftest"
chrome --headless=new --dump-dom "http://127.0.0.1:8790/selftest?phase=reload"
python scripts/05_build_dashboard.py --selftest /tmp/st.html  # standalone test build
chrome --headless=new --user-data-dir=/tmp/prof --dump-dom file:///tmp/st.html
chrome --headless=new --user-data-dir=/tmp/prof --dump-dom "file:///tmp/st.html?phase=reload"
```

Results go to `#testlog` and the document title (`SELFTEST n/n fail=0 skip=k`), so it greps
cleanly. Standalone runs skip the API assertions and say so. `/selftest` rebuilds from disk on
every request.

---

## 3. The data

### Where it comes from

- **Zenodo REST API** (InvenioRDM) — DMP records and their files. 3,268 unique records across five
  queries; 2,650 survive the DMP filter in step 04.
- **CORDIS bulk datasets** — Horizon Europe and H2020 project CSVs, 58,840 projects
  (23,451 HORIZON + 35,389 H2020). Joined on grant number. ~90 MB, git-ignored, re-downloaded on
  demand by step 04.
- **RDA DMP Common Standard 1.2 JSON schema** — fetched from GitHub by step 03.

### Zenodo query fields that actually work

These are InvenioRDM fields, verified against the live API — not the legacy Zenodo ones, and
poorly documented upstream:

| field | meaning |
|---|---|
| `metadata.resource_type.id:"publication-datamanagementplan"` | Zenodo's own DMP type |
| `files.types:json` | record contains a `.json` file — **extension only, not content** |
| `metadata.funding.award.program` | `HORIZON.2.5` = Horizon Europe, `H2020-EU…` = H2020 |
| `metadata.funding.funder.id` | `00k4n6c32` European Commission, `018mejw64` DFG |
| `metadata.publication_date:[2024 TO 2026]` | date range |

Anonymous requests cap page size at 25; `ZENODO_TOKEN` raises it to 100 and cuts a full harvest
from ~4 minutes to under one.

### `data/dmp_dataset.json` — one object per DMP record

Identity and record: `id`, `doi`, `url`, `title`, `date`, `year`, `type`, `access`, `version`,
`desc`, `subjects`, `n_json`, `n_pdf`, `dl`.

Funding: `tier`, `program`, `grant`, `acronym`.

CORDIS project: `proj_title`, `proj_start`, `proj_end`, `proj_status`, `call`, `legal`.

Derived axes: `disc` (the project's most frequent EuroSciVoc branch, used for the coverage
matrix), `disc_all` (every branch the project carries), `fields` (every `[branch, sub-field]`
pair, so a sub-field is never displayed under a branch it does not belong to),
`stage`, `stage_frac`, `stage_src`.

maDMP: `madmp` (bool), `madmp_file`, `n_datasets`, `n_dist` (**populated** distributions only),
`schema_ok`, `n_findings`, `personal`, `sensitive`, `ethics`.

Challenging case: `challenging`, `ch_meta`.

Record classification: `kind`, `kind_why`. Bibliographic detail: `creators`, `files`
(name, ext, size), `funders` (every funding entry, not just the matched one), `subjects`.

### How the derived fields are computed

Read `scripts/04_build_dataset.py` for the authoritative version. In short:

**`tier`** — first match wins: CORDIS says HORIZON → `Horizon Europe`; CORDIS says H2020 →
`Horizon 2020`; else Zenodo `award.program` starts `HORIZON` / `H2020`; else funder is the
European Commission → `Other EU`; else DFG → `DFG`; else `Other funder`; else
`No funder metadata`.

**Grant numbers come from two places** — the Zenodo funding metadata *and*
`dmp.project.funding.grant_id` inside the maDMP file itself. The second source matters: roughly
half the Horizon Europe maDMPs are not tagged as EU-funded in their Zenodo record.

**`stage`** — position of the publication date between `proj_start` and `proj_end`:
`≤ 0.34` early, `≤ 0.70` mid, above late; negative is `pre-start`; no dates is `unknown`.
`stage_src` says whether the dates came from `cordis` or from the maDMP itself.

**`disc`** — the project's most frequent top-level EuroSciVoc branch. Empty when there is no
CORDIS match. It is only a summary: **filtering uses `disc_all` and `fields`, not `disc`**, so
picking "engineering and technology" returns every project carrying any engineering term rather
than only those where engineering won the majority vote. EuroSciVoc has 6 branches, 41 level-2
sub-fields (37 present in this pool) and 256 level-3 terms; the dashboard filters at levels 1
and 2, and level 3 is not carried in the dataset.

**`kind`** — what the record actually *is*, because a search for "data management plan"
returns far more literature about DMPs than plans. Decided from the Zenodo resource type plus
the shape of the title, in this order: a title saying template/workbook wins; a maDMP file
describing datasets means `dmp`; a title like "DMP Evaluation Service" or an opener like
"Towards…"/"Identification of…" means it is `about` DMPs; poster/presentation/paper/software
types are `about`; the Zenodo DMP type means `dmp`; a title that opens by naming itself a plan
("D1.1 Data Management Plan v2", "NOVAFERT Data Management Plan") means `dmp`, unless a guide
word sits in front of or at the end of it; then guide words mean `guidance`; then a deliverable
or report with a DMP title means `dmp`; anything left is `unclear`. `kind_why` records which
rule fired, and the dashboard shows it on every row. **It is a heuristic** — the dashboard
exposes it as a filter, a column and a tag precisely so it can be overridden by eye. The
dashboard shows only `kind == "dmp"` by default.

**`ch_meta`** — the strict test: the maDMP itself sets `personal_data`, `sensitive_data`,
`security_and_privacy` or `ethical_issues_exist`. **`challenging`** — looser: `ch_meta` OR a
regex hit for GDPR / personal data / sensitive / ethics / consent / patient / clinical wording in
the title, description or subjects. Treat `challenging` alone as a *lead to check*, not evidence.

### Current numbers

| | |
|---|---|
| DMP-related records | 2,650 — of which **2,504 are actual plans** |
| by kind | dmp 2,504 · about 64 · template 35 · guidance 32 · unclear 15 |
| Horizon Europe | 722 (700 plans) — of which **574 published 2024 or later, 555 of them plans**, across 445 projects |
| Horizon 2020 / Other EU / DFG | 525 / 69 / 27 — the DFG 27 contain only **6 actual plans** |
| Other funder / no funder metadata | 267 / 1,040 |
| machine-actionable (validated RDA-DCS) | 376 |
| with a CORDIS discipline | 1,034 |
| lifecycle known | 1,243 (early 521, mid 362, late 360) |

Horizon Europe 2024+, discipline × stage:

| discipline | early | mid | late |
|---|---|---|---|
| natural sciences | 61 | 67 | 47 |
| social sciences | 30 | 39 | 26 |
| engineering and technology | 41 | 36 | 15 |
| agricultural sciences | 11 | 11 | 9 |
| medical and health sciences | 11 | 10 | 10 |
| humanities | 8 | 1 | 1 |

(actual plans only; add the other kinds back with the Record kind filter)

---

## 4. Findings and limitations — read before advising

**The DFG is a dead end on Zenodo.** 7,931 DFG-funded records exist, but only 27 mention a DMP,
only 4 are typed as one, and **none is machine-actionable** (one of the four is a template).
If DFG DMPs are needed they must come from elsewhere: RDMO instances, institutional repositories,
GEPRIS-linked outputs. Do not suggest "search Zenodo harder" — it has been done.

**maDMPs are scarce and concentrated.** Only 47 of the 574 Horizon Europe 2024+ records are
machine-actionable, and one project (CERTAINTY) contributes 24 of them as separate per-partner
DMPs. **Filling all nine matrix cells with maDMPs alone is not possible.** A mixed set of maDMPs
and PDF DMPs is. The criteria say *prefer* maDMPs, so this is consistent — but it is a real
decision the user should make deliberately.

**Most maDMPs are structurally hollow.** Only **25 of 377** pass RDA schema 1.2 with no findings.
The rest are correct at the top level but incomplete underneath — most commonly
`distribution.title` and `distribution.data_access` absent, and about half of all distribution
objects are empty `{}` placeholders emitted by the exporting tool. This is worth keeping, not
filtering out: real-world incompleteness is exactly what a DMP review tool should detect.

**The sensitive-data pool is thin.** Across the Horizon Europe 2024+ maDMPs: 2 files flag
`personal_data=yes`, 3 flag `sensitive_data=yes`, 1 sets `ethical_issues_exist=yes`. The realistic
candidates for the challenging slot are ThrombUS+, SeaMark and ECRAID-Prime.

**PDFs are not downloaded.** `data/madmp-corpus/` holds the maDMP JSON files only. For PDF DMPs
the repo has metadata and a Zenodo link, nothing local. Adding a PDF fetcher is a small,
well-scoped change — the file names and sizes are already in `data/raw/*.jsonl`.

**Publication dates can be partial.** Some Zenodo records carry `2024` or `2024-06` rather than a
full date. Sorting is lexicographic, which treats a partial date as the earliest point in its
period. Acceptable, but do not assume every `date` is 10 characters.

**`n_dist` counts populated distributions only.** The raw count including empty placeholders is
much higher. Do not compare it against numbers from elsewhere without checking which is meant.

---

## 5. Two bugs already found and fixed — do not reintroduce

**Filter chips captured their state object at bind time.** `applyPreset` and the clear buttons
*replace* `state.tiers`, `state.fmt` etc. rather than mutating them, so a handler holding the old
object silently did nothing after any preset click. Handlers now look the bucket up by name on
every click. If you add a filter group, follow that pattern.

**`HTTPServer` sets `allow_reuse_address`**, which on Windows lets a second process bind a port
another process already holds — making the busy-port fallback quietly steal the port instead of
stepping past it. `serve.py` defines its own `Server` class with `allow_reuse_address = False`.
Do not remove it.

**The discipline column once showed sub-fields under the wrong branch** — a project tagged
with both computer science and sociology rendered as "natural sciences / biological sciences,
sociology", which reads as though sociology were a natural science. The dataset now keeps
`[branch, sub-field]` pairs rather than two flat lists. If you touch that rendering, keep the
pairing.

**The pool once included anything whose title mentioned a DMP**, which meant posters, workshop
guides, templates and papers about DMPs were offered as candidates. Filtering to DFG returned 27
records of which only 6 were plans. Fixed by the `kind` classifier; keep it in mind when adding
a query to step 01, since a wider net pulls in more literature.

---

## 6. Conventions for changing things

- **Python 3.7+, stdlib only, no third-party dependencies.** Everything is stdlib Python and
  vanilla JS. The code is platform-neutral: the only difference between Windows and Ubuntu is
  whether the interpreter is invoked as `python` or `python3`. Do not add
  `requests`, `pandas`, a bundler or a framework. If something needs a library, say so and let the
  user decide.
- **`dashboard/dashboard.html` is generated.** Never edit it. Edit `dashboard/template.html` and
  run `python scripts/05_build_dashboard.py`. The template has four placeholders —
  `__BOOT__`, `__DATA__`, `__PAIRED__`, `__COUNT__` — filled differently by the standalone build
  and by `serve.py`. Both must keep working.
- **Paired-study rules live twice**: `scripts/paired.py` (timing, validate, exports) and their
  JavaScript mirror in the template. Change both, and extend `dashboard/paired-fixtures.json`;
  the served suite fails if the two validators disagree.
- **Never run the self-test against real state.** Use `serve.py --test` (or `--state-dir`), and a
  throwaway `--user-data-dir` for the standalone build.
- **Every new control needs a `data-tip`.** The test suite fails otherwise, by design.
- **Add tests for what you change**, in `dashboard/selftest.js`, then run the headless suite.
  Prefer real DOM clicks over calling internals — the one bug the internal-API tests missed was in
  the click wiring.
- **Do not commit `data/cordis/`** — ~90 MB, git-ignored, re-downloadable.
- The scripts are numbered and meant to run in order; each is independently re-runnable.

### Things to check before answering

If the question names a file, function or field, verify it still exists rather than trusting this
document. The numbers here were current when written and change if the pipeline is re-run
against a live Zenodo.

---

## 7. Layout

```
AGENTS.md              this file
README.md              the human-facing overview
scripts/               the pipeline, plus serve.py and its own README
data/raw/              Zenodo record metadata, one .jsonl per query
data/madmp-corpus/     384 downloaded .json files, 377 real maDMPs
data/dmp_dataset.json  the joined dataset the dashboard renders
data/dmp_dataset.csv   the same, flattened
data/schema_findings.json   per-file RDA schema results
data/selection.json    legacy selection (historical 12-record pick, untracked; preserve it)
data/backups/          byte-preserving backup of the legacy selection (git-ignored)
data/paired_selection.json  the paired-study draft, when served (absent until saved)
data/paired-snapshots/ immutable frozen cohorts + CSV/MD derivatives (none yet)
data/study-documents.json   registry of study documents absent from the dataset (3 now)
data/paired-discovery/ grant groups and Zenodo version-chain leads; cache/ is git-ignored
data/paired-dmp-corpus/     source PDFs and CORDIS snapshots for the proposal (git-ignored)
data/cordis/           CORDIS bulk downloads (git-ignored)
dashboard/template.html     the single source for both builds
dashboard/dashboard.html    generated standalone build
dashboard/selftest.js       the browser suite (test builds only)
dashboard/paired-fixtures.json   shared timing/escaping fixtures and synthetic cohort
research/paired-dmp-study/  the paired-study research record and handoffs
```

## 8. API surface (`scripts/serve.py`)

Binds to `127.0.0.1` only. Ports default to 8756 (UI) and 8757 (API), stepping up if busy.

```
GET  /                    the dashboard
GET  /selftest            the dashboard plus the test harness
GET  /api/health          liveness, record count, whether the corpus is present
GET  /api/dmps            the dataset the dashboard renders
GET  /api/stats           pool counts and the Horizon Europe 2024+ matrix
GET  /api/selection       saved selection, resolved to full records
PUT  /api/selection       {"ids": [...]} -> writes data/selection.json
GET  /api/madmp/<file>    one maDMP file from the local corpus
GET  /api/paired          the paired draft; 409 with the reason if the file is corrupt
PUT  /api/paired          {"study": {...}, "replace_corrupt": false} -> data/paired_selection.json
POST /api/paired/validate {"study": {...}} -> Python validation result
POST /api/paired/files    {"study": {...}, "download": false} -> checksums of selected files
POST /api/paired/freeze   {"study": {...}} -> immutable data/paired-snapshots/<id>.json, or 422 + reasons
GET  /api/paired/snapshots  frozen snapshots and whether their content hash still matches
```

`--state-dir DIR` moves `selection.json`, `paired_selection.json` and `paired-snapshots/` to DIR;
`--test` uses a fresh temporary one. `/selftest` returns 409 against the default `data/`.

## 9. Glossary

- **DMP** — Data Management Plan. **maDMP** — machine-actionable DMP: a JSON file following the
  **RDA DMP Common Standard** (RDA-DCS), whose defining feature is a top-level `dmp` object.
- **Horizon Europe** — EU framework programme 2021–2027. **Horizon 2020** — its 2014–2020
  predecessor.
- **CORDIS** — the EU's project database; source of project dates, calls and classifications.
- **EuroSciVoc** — the EU science vocabulary; its top level is the OECD field of science, used
  here as the discipline axis.
- **Infra-DMP criteria matrix** — the manual review rubric the selected DMPs will be assessed
  against.
- **UAG** — the advisory group this work contributes to. The repo covers one contributor's part
  of it, not the whole effort.
