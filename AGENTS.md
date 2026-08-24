# AGENTS.md — orientation for AI assistants

Read this before answering questions about this repository or changing anything in it.
It is written for an AI assistant working with someone who has just cloned the repo.
Everything here was verified against the data in the repo, not assumed.

---

## 1. What this repository is

A personal working repository for one contributor's slice of the **UAG work on DMPs and AI**.
It does not cover everything the UAG does.

The concrete goal: build a small, transparent **test set of ~10 open Data Management Plans**
that can be used to evaluate automated and AI-assisted DMP review tools. The selected DMPs
will be reviewed manually against the Infra-DMP criteria matrix
(https://doi.org/10.5281/zenodo.19630859); those manual reviews become the reference
standard that automated review can be compared against.

So the repo is **not** a DMP review tool. It is the machinery for *choosing what to review*:
harvest a candidate pool, enrich it with the metadata the selection criteria need, and give a
human a dashboard to pick from.

**Current status:** the pool is built and the dashboard works. The 10 DMPs are *not* selected yet.
If the user asks "which 10 did we pick?", the answer is that nothing is picked yet — the
selection would live in `data/selection.json`, which is absent until they make one.

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
| `serve.py` | runs the dashboard locally with a small JSON API | serves `/`, writes `data/selection.json` |

### Dashboard

Two ways to run, one shared template (`dashboard/template.html`):

- **Served** — `python scripts/serve.py`, UI on `http://127.0.0.1:8756`. Rows come from the API;
  the selection is written to `data/selection.json` on every change; maDMP files are served from
  the local corpus so inspecting one needs no round trip to Zenodo.
- **Standalone** — open `dashboard/dashboard.html`. The whole dataset is embedded, so it works
  offline; the selection lives in browser storage only.

Features:

- Filter by funder tier, publication year range, format, discipline, lifecycle stage, sensitive-data
  flags, and full-text search across title, project, grant, DOI, call id and description
- Four presets that set every filter at once
- Sortable columns — click a header, click again to reverse
- **Editable columns**: 13 available, 8 shown by default; show/hide, reorder, reset. Choice
  persists in browser storage. The checkbox and DMP-title columns are locked.
- Live 3 × 3 coverage matrix over the current selection, plus a challenging-case slot
- Warnings for duplicate projects, a fourth discipline, missing lifecycle stage, and going over 10
- Export as Markdown table, CSV or JSON (clipboard, with a visible fallback box)
- **Hover documentation on every control** — filter chips, column headers, column-editor rows,
  coloured tags and counters each carry a one-line explanation; keyboard focus shows it too,
  Escape dismisses. A **Guide** button opens a short panel about the pool and the two axes.
- Light and dark themes, responsive down to a single column

### Test suite

`dashboard/selftest.js` — **131 assertions, all passing.** Served only at `/selftest`, never part
of a built file. It drives the real UI through both the internal API and real DOM clicks: filters,
search, sorting, columns, paging, row expansion, selection, matrix, warnings, all three export
formats, tooltips and the API round trip. It also asserts that *no control is undocumented*, so a
new filter without a tooltip fails the suite.

```bash
python scripts/serve.py --no-open
chrome --headless=new --dump-dom "http://127.0.0.1:8756/selftest"
```

Results go to `#testlog` and the document title (`SELFTEST 131/131 fail=0`), so it greps cleanly.
`/selftest` rebuilds from disk on every request — editing the template or harness needs no restart.

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

Derived axes: `disc` (primary EuroSciVoc field), `disc_all`, `disc2` (sub-fields),
`stage`, `stage_frac`, `stage_src`.

maDMP: `madmp` (bool), `madmp_file`, `n_datasets`, `n_dist` (**populated** distributions only),
`schema_ok`, `n_findings`, `personal`, `sensitive`, `ethics`.

Challenging case: `challenging`, `ch_meta`.

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

**`disc`** — most frequent top-level EuroSciVoc term for the project. Empty when there is no
CORDIS match.

**`ch_meta`** — the strict test: the maDMP itself sets `personal_data`, `sensitive_data`,
`security_and_privacy` or `ethical_issues_exist`. **`challenging`** — looser: `ch_meta` OR a
regex hit for GDPR / personal data / sensitive / ethics / consent / patient / clinical wording in
the title, description or subjects. Treat `challenging` alone as a *lead to check*, not evidence.

### Current numbers

| | |
|---|---|
| DMP records | 2,650 |
| Horizon Europe | 722 — of which **574 published 2024 or later**, across 445 projects |
| Horizon 2020 / Other EU / DFG | 525 / 69 / 27 |
| Other funder / no funder metadata | 267 / 1,040 |
| machine-actionable (validated RDA-DCS) | 376 |
| with a CORDIS discipline | 1,034 |
| lifecycle known | 1,243 (early 521, mid 362, late 360) |

Horizon Europe 2024+, discipline × stage:

| discipline | early | mid | late |
|---|---|---|---|
| natural sciences | 62 | 71 | 52 |
| social sciences | 30 | 40 | 27 |
| engineering and technology | 41 | 36 | 16 |
| agricultural sciences | 11 | 12 | 9 |
| medical and health sciences | 11 | 10 | 11 |
| humanities | 8 | 1 | 1 |

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

---

## 6. Conventions for changing things

- **No third-party dependencies.** Everything is Python 3 stdlib and vanilla JS. Do not add
  `requests`, `pandas`, a bundler or a framework. If something needs a library, say so and let the
  user decide.
- **`dashboard/dashboard.html` is generated.** Never edit it. Edit `dashboard/template.html` and
  run `python scripts/05_build_dashboard.py`. The template has three placeholders —
  `__BOOT__`, `__DATA__`, `__COUNT__` — filled differently by the standalone build and by
  `serve.py`. Both must keep working.
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
data/selection.json    written by the dashboard when served (absent until you pick something)
data/cordis/           CORDIS bulk downloads (git-ignored)
dashboard/template.html     the single source for both builds
dashboard/dashboard.html    generated standalone build
dashboard/selftest.js       the 131-assertion suite
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
```

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
