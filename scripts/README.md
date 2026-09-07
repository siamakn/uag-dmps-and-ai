# Harvesting pipeline

Five steps, run in order. Each one is re-runnable: downloads that already exist
on disk are skipped, so a repeat run only fetches what changed.

```bash
python scripts/01_harvest_records.py    # Zenodo record metadata      -> data/raw/*.jsonl
python scripts/02_download_madmps.py    # the .json files themselves  -> data/madmp-corpus/
python scripts/03_check_schema.py       # RDA DMP Common Standard 1.2 -> data/schema_findings.json
python scripts/04_build_dataset.py      # join to CORDIS              -> data/dmp_dataset.{json,csv}
python scripts/05_build_dashboard.py    # selection UI                -> dashboard/dashboard.html
```

No third-party packages. Python 3.9+ and a network connection are enough.

Set `ZENODO_TOKEN` to raise the page size from 25 to 100 records per request —
a full harvest drops from about four minutes to under one.

## What each step is for

**01 — harvest.** Five separate Zenodo queries, because no single one finds all
DMPs. Some records are typed `publication-datamanagementplan`, some are project
deliverables with a DMP title, some are bare `.json` exports from a DMP tool.
The union is deduplicated by record id in step 04.

**02 — download.** A `.json` file in a DMP record is often not a maDMP: records
also carry `ro-crate-metadata.json`, `codemeta.json` and plain research data.
The only reliable test is opening the file and looking for a top-level `dmp`
object. Of 384 candidates, 377 are real RDA-DCS files.

**03 — schema check.** A small checker walks the official RDA schema and reports
absent or empty required properties, enum violations and wrong types. It has no
dependencies, which is why it is not a full JSON Schema validator. Findings are
informational — most real maDMPs have some, and that incompleteness is part of
what a DMP review benchmark should contain.

**04 — join to CORDIS.** Zenodo cannot say which discipline a DMP belongs to or
where in the project's life it was written. CORDIS can, joined on grant number:

- `startDate`/`endDate` turn the DMP's publication date into a position on the
  project timeline — the lifecycle stage (≤34 % early, ≤70 % mid, above late)
- EuroSciVoc terms give the OECD field of science — the discipline axis

Grant numbers are read from two places: the Zenodo funding metadata, and
`dmp.project.funding.grant_id` inside the maDMP file. The second source matters —
roughly half the Horizon Europe maDMPs are not tagged as EU-funded on Zenodo.

**05 — dashboard.** Embeds the dataset in a single self-contained HTML file that
opens from disk with no server. Selection lives in browser storage.

## Running it locally

```bash
python3 scripts/serve.py                  # UI + API on http://127.0.0.1:8756
python3 scripts/serve.py --api-port 8757  # split: UI on 8756, API on 8757
python3 scripts/serve.py --port 9000      # pick your own
python3 scripts/serve.py --no-open        # do not launch a browser (headless)
```

On Windows the interpreter is `python`, on Ubuntu `python3`; nothing else differs. Python 3.7+,
stdlib only. See the README for the per-platform walkthrough.

Ports default to 8756 and 8757, away from the usual 3000/5000/8000/8080 crowd.
If a port is taken the server steps up to the next free one and says which it
took, so a stale instance never blocks a restart.

Served this way the page fetches its rows from the API rather than carrying them
inline, and your selection is written to `data/selection.json` — a real file you
can commit and diff, instead of browser storage that vanishes with the cache.
The saved file records the ids, the resolved records and the discipline x stage
matrix at the time of saving.

| endpoint | |
|---|---|
| `GET /` | the dashboard |
| `GET /api/health` | liveness, record count, whether the corpus is present |
| `GET /api/dmps` | the dataset the dashboard renders |
| `GET /api/stats` | pool counts and the Horizon Europe 2024+ matrix |
| `GET /api/selection` | saved selection, resolved to full records |
| `PUT /api/selection` | `{"ids": [...]}` → writes `data/selection.json` |
| `GET /api/madmp/<file>` | one maDMP straight from `data/madmp-corpus/` |

Stdlib only, binds to 127.0.0.1, nothing exposed off the machine. The same
`dashboard/template.html` produces both builds: `__DATA__` becomes the embedded
dataset for the standalone file, or `null` plus a `window.DMP_API` pointer when
served.

## Testing the dashboard

`dashboard/selftest.js` drives the real UI - filters, search, sorting, column
show/hide/reorder, selection, the coverage matrix, all three export formats, the
hover documentation and the API round trip - through both the internal API and
real DOM clicks. It also asserts that no control is left undocumented: every rail
control, column header and column-editor row must carry a tooltip, so adding a
filter without explaining it fails the suite. It is
served only at `/selftest` and is never part of a built file.

```bash
python scripts/serve.py --no-open
chrome --headless=new --dump-dom "http://127.0.0.1:8756/selftest"
```

The page prints `SELFTEST <passed>/<total>` into `#testlog` and the document
title, so it greps cleanly from a headless dump. Open the same URL in a normal
browser to read the results on screen. `/selftest` rebuilds the page from disk on
every request, so editing the template or the harness needs no restart.

Current status: **180/180 passing.**

It has already earned its keep. Bugs it caught:

- filter chips captured their state object at bind time, but presets and the
  clear buttons replace those objects - so after clicking any preset, every chip
  silently stopped filtering
- `HTTPServer` sets `allow_reuse_address`, which on Windows lets a second process
  bind a port another process already holds, making the busy-port fallback
  quietly steal the port instead of stepping past it

## Zenodo query fields worth knowing

Verified against the live API; these are InvenioRDM fields, not the legacy ones.

| Field | Use |
|---|---|
| `metadata.resource_type.id:"publication-datamanagementplan"` | Zenodo's own DMP type |
| `files.types:json` | record contains a `.json` file (extension only, not content) |
| `metadata.funding.award.program` | `HORIZON.2.5` for Horizon Europe, `H2020-EU…` for H2020 |
| `metadata.funding.funder.id` | `00k4n6c32` European Commission, `018mejw64` DFG |
| `metadata.publication_date:[2024 TO 2026]` | date range |

Anonymous requests are capped at 25 records per page; a token raises it to 100.
