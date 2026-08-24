# uag-dmps-and-ai

This is my personal working repository for the part of the UAG work on DMPs and AI that I am contributing to. It does not cover everything the UAG is doing — only the pieces I am actually involved in, so I can keep track of what I do, why I did it, and what came out of it.

Right now that means one thing: putting together a small test set of DMPs for evaluating automated review tools.

## Working with an AI assistant

Nobody reads documentation any more, so the real documentation is written for the thing that will.

**[AGENTS.md](AGENTS.md)** is an orientation document for AI assistants. Point yours at it — "read AGENTS.md" — and it can answer questions about this repo without guessing: what the data means field by field, how the discipline and lifecycle axes are derived, what the known limitations are, which numbers are current, and what the conventions are for changing anything. It also records two bugs that were already found and fixed, so an assistant doesn't reintroduce them.

`CLAUDE.md` is a one-line pointer to the same file, so Claude Code picks it up automatically.

## DMP evaluation test set

The idea is a small, transparent benchmark of around **10 open DMPs** that can be used to check how well automated (or AI-assisted) DMP review works.

### Selection criteria

- 10 open DMPs
- Prefer **machine-actionable DMPs (maDMPs)** with structured JSON / RDA-DCS
- Prefer **Horizon Europe** over Horizon 2020
- Prefer **recent DMPs**, ideally 2024 or newer
- Select on **metadata**, not on perceived DMP quality
- Cover **3 broad scientific disciplines**
- Cover **3 project lifecycle stages** — early, mid, late/final
- Target a **3 × 3 matrix = 9 DMPs**
- Add **1 challenging DMP**, preferably involving personal/sensitive data, GDPR or ethical constraints, or restricted access
- DMPs must be openly accessible and downloadable
- Prefer sources with a large candidate pool and API-accessible metadata

Picking "nice-looking" DMPs would bias the whole evaluation, so selection runs off metadata only. Both the discipline and the lifecycle axis come from external authorities rather than my judgement: EuroSciVoc field of science, and the DMP's publication date measured against the project's CORDIS start and end dates.

## How they will be evaluated

The selected DMPs will be reviewed manually against the **Infra-DMP criteria matrix**:

https://doi.org/10.5281/zenodo.19630859

Those manual reviews are the reference point. Once they exist, automated or AI-assisted review approaches can be compared against them.

## The candidate pool

Harvested from Zenodo and joined to CORDIS. Current state:

| | records |
|---|---|
| DMP records in total | 2 650 |
| Horizon Europe | 722 — of which **574 published 2024 or later** |
| Horizon 2020 | 525 |
| Other EU | 69 |
| DFG | 27 |
| machine-actionable (RDA-DCS JSON, validated) | 376 |

Horizon Europe from 2024 onward covers **445 distinct projects**, which is a large enough pool that the 3 × 3 matrix is comfortable rather than exhaustive:

| discipline (EuroSciVoc) | early | mid | late |
|---|---|---|---|
| natural sciences | 62 | 71 | 52 |
| social sciences | 30 | 40 | 27 |
| engineering and technology | 41 | 36 | 16 |
| agricultural sciences | 11 | 12 | 9 |
| medical and health sciences | 11 | 10 | 11 |
| humanities | 8 | 1 | 1 |

Two things to know before selecting:

**maDMPs are scarce.** Only 47 of those 574 Horizon Europe records are machine-actionable, and one project (CERTAINTY) contributes 24 of them as separate per-partner DMPs. Filling all nine matrix cells with maDMPs alone is not possible; a mixed set of maDMPs and PDF DMPs is.

**The DFG is not a usable source here.** Zenodo holds 7 931 DFG-funded records, but only 27 mention a DMP, only 4 are typed as one, and none is machine-actionable. If DFG DMPs are needed, they will have to come from somewhere else — RDMO instances, institutional repositories, or GEPRIS-linked outputs.

## Selection dashboard

Filters the pool by funder, year, format, discipline, lifecycle stage and sensitive-data flags, and tracks the 3 × 3 matrix live as DMPs are ticked — warning about duplicate projects or a fourth discipline creeping in. The selection can be copied out as Markdown, CSV or JSON.

Everything explains itself on hover: each filter chip, column header, column-editor row and coloured tag carries a one-line description of exactly what it does and where the value comes from. The **Guide** button in the header opens a short panel covering the pool, how the discipline and lifecycle axes are derived, how to read a row, and where the selection is saved. Column layout and hover text are covered by the test suite, so a filter cannot be added without documenting it.

**Run it locally:**

```bash
python scripts/serve.py                  # http://127.0.0.1:8756, opens a browser
python scripts/serve.py --api-port 8757  # UI and API on separate ports
python scripts/serve.py --port 9000      # pick your own
```

Ports default to 8756 and 8757 to stay clear of the usual 3000/5000/8000/8080 crowd, and the server steps up to the next free port if one is taken rather than failing. This mode saves your selection to **`data/selection.json`** — a real file you can commit and diff — and serves the maDMP files from the local corpus, so inspecting one costs no round trip to Zenodo.

**Or without a server:** open `dashboard/dashboard.html` directly. The whole dataset is embedded in the file, so it works offline; the only difference is that the selection lives in browser storage instead of a file.

## Repository layout

```
scripts/            the five-step harvesting pipeline (see scripts/README.md)
scripts/serve.py    local server for the dashboard, with a small JSON API
data/raw/           Zenodo record metadata, one .jsonl per query
data/madmp-corpus/  384 downloaded .json files, 377 of them real maDMPs
data/dmp_dataset.*  the joined dataset, JSON and CSV
data/selection.json written by the dashboard when served locally
data/cordis/        CORDIS bulk downloads (git-ignored, ~90 MB, re-fetched on demand)
dashboard/          template and built dashboard
```

Everything is reproducible from scratch with plain Python 3, no dependencies:

```bash
python scripts/01_harvest_records.py   # ~4 min without a Zenodo token
python scripts/02_download_madmps.py
python scripts/03_check_schema.py
python scripts/04_build_dataset.py     # downloads ~90 MB of CORDIS data on first run
python scripts/05_build_dashboard.py
python scripts/serve.py
```

Set `ZENODO_TOKEN` to cut the harvest to under a minute — it raises the anonymous page size from 25 records to 100.

## A note on maDMP quality

Every downloaded `.json` was checked against the RDA DMP Common Standard 1.2 schema. Only **25 of 377** pass with no findings. The rest are structurally correct at the top level but hollow underneath — the most common gaps are `distribution.title` and `distribution.data_access`, and about half of all distribution objects are empty placeholders emitted by the exporting tool.

That is worth keeping rather than filtering out. Real-world incompleteness is exactly what an automated DMP review tool should be able to detect.

## Status

Work in progress. The pool is built; the 10 DMPs are not selected yet.

## No license

This repository is deliberately published without a licence. That is a choice, not an oversight: the work is in progress and I am not granting rights to reuse, modify or redistribute it while it is still moving. Default copyright applies.

If you want to use something here, ask me.
