# uag-dmps-and-ai

This is my personal working repository for the part of the UAG work on DMPs and AI that I am contributing to. It does not cover everything the UAG is doing — only the pieces I am actually involved in, so I can keep track of what I do, why I did it, and what came out of it.

Right now that means one thing: putting together a small test set of DMPs for evaluating automated review tools.

## Working with an AI assistant

Nobody reads documentation any more, so the real documentation is written for the thing that will.

**[AGENTS.md](AGENTS.md)** is an orientation document for AI assistants. Point yours at it — "read AGENTS.md" — and it can answer questions about this repo without guessing: what the data means field by field, how the discipline and lifecycle axes are derived, what the known limitations are, which numbers are current, and what the conventions are for changing anything. It also records the bugs that were already found and fixed, so an assistant doesn't reintroduce them.

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

| | records | of which actual plans |
|---|---|---|
| DMP-related records in total | 2 650 | 2 504 |
| Horizon Europe | 722 | 700 |
| — published 2024 or later | 574 | **555** |
| Horizon 2020 | 525 | — |
| Other EU | 69 | — |
| DFG | 27 | **6** |
| machine-actionable (RDA-DCS JSON, validated) | 376 | — |

**Discipline works at two levels.** The six OECD fields are only the top of the EuroSciVoc
tree; the useful granularity is the 37 sub-fields beneath them — materials engineering,
nanotechnology, physical sciences, health sciences and so on. Pick a branch and its sub-fields
appear underneath it as a second row of chips. A project that spans several branches is listed
under each of them rather than being forced into whichever one happens to have the most terms,
and each sub-field is always shown under the branch it actually belongs to.

**Not everything that mentions a DMP is one.** A search for "data management plan" also returns
posters, workshop guides, blank templates and papers *about* DMPs. Every record is therefore
classified from its Zenodo resource type and the shape of its title into one of five kinds —
`actual DMP`, `template`, `guidance`, `about DMPs`, `unclear` — and the dashboard shows only
actual plans by default. It matters most at the small end: the DFG tier goes from 27 mixed
records down to 6 real plans.

Horizon Europe from 2024 onward covers **445 distinct projects**, which is a large enough pool
that the 3 × 3 matrix is comfortable rather than exhaustive (actual plans only):

| discipline (EuroSciVoc) | early | mid | late |
|---|---|---|---|
| natural sciences | 61 | 67 | 47 |
| social sciences | 30 | 39 | 26 |
| engineering and technology | 41 | 36 | 15 |
| agricultural sciences | 11 | 11 | 9 |
| medical and health sciences | 11 | 10 | 10 |
| humanities | 8 | 1 | 1 |

Two things to know before selecting:

**maDMPs are scarce.** Only 47 of those 574 Horizon Europe records are machine-actionable, and one project (CERTAINTY) contributes 24 of them as separate per-partner DMPs. Filling all nine matrix cells with maDMPs alone is not possible; a mixed set of maDMPs and PDF DMPs is.

**The DFG is not a usable source here.** Zenodo holds 7 931 DFG-funded records, but only 27 mention a DMP — and of those just 6 are actual plans, the rest being templates, workshop guides and posters. None is machine-actionable. If DFG DMPs are needed, they will have to come from somewhere else — RDMO instances, institutional repositories, or GEPRIS-linked outputs.

## Selection dashboard

Filters the pool by funder, year, format, discipline, lifecycle stage and sensitive-data flags, and tracks the 3 × 3 matrix live as DMPs are ticked — warning about duplicate projects or a fourth discipline creeping in. The selection can be copied out as Markdown, CSV or JSON.

Clicking any title opens a full metadata sheet — authors, abstract, DOI, Zenodo type, project and its run dates, call, funders, discipline, keywords, maDMP statistics and the file list with sizes — so a candidate can be judged without opening Zenodo at all.

Everything explains itself on hover: each filter chip, column header, column-editor row and coloured tag carries a one-line description of exactly what it does and where the value comes from. The **Guide** button in the header opens a short panel covering the pool, how the discipline and lifecycle axes are derived, how to read a row, and where the selection is saved. Column layout and hover text are covered by the test suite, so a filter cannot be added without documenting it.

### Running it

Python 3.7 or newer, and nothing else — no `pip install`, no virtualenv, no Node. The only
difference between platforms is whether the interpreter is called `python` or `python3`.

**Windows** (PowerShell, from the repo root):

```powershell
git clone https://github.com/siamakn/uag-dmps-and-ai.git
cd uag-dmps-and-ai
python scripts\serve.py
```

**Ubuntu / Debian:**

```bash
sudo apt install -y python3 git          # both are usually already there
git clone https://github.com/siamakn/uag-dmps-and-ai.git
cd uag-dmps-and-ai
python3 scripts/serve.py
```

Either way it prints where it is listening and opens your browser:

```
DMP Selection Bench
  dashboard   http://127.0.0.1:8756/
  api         http://127.0.0.1:8756/api
  dataset     2650 records, 376 maDMPs
  selection   .../data/selection.json
  ctrl-c to stop
```

Options, identical on both platforms:

```
--api-port 8757   run the API on its own port instead of sharing the UI port
--port 9000       choose the UI port
--no-open         do not launch a browser (use this on a headless box)
--verbose         log every request
```

Ports default to 8756 and 8757 to stay clear of the usual 3000/5000/8000/8080 crowd. If a port
is taken the server steps up to the next free one and tells you which it took, so a forgotten
instance never blocks a restart. It binds to `127.0.0.1` only — nothing is exposed off the machine.

Running it this way saves your selection to **`data/selection.json`** — a real file you can commit
and diff — and serves the maDMP files from the local corpus, so inspecting one costs no round trip
to Zenodo.

**Or without a server:** open `dashboard/dashboard.html` in any browser — double-click it on
Windows, `xdg-open dashboard/dashboard.html` on Ubuntu. The whole dataset is embedded in the file,
so it works offline; the only difference is that the selection lives in browser storage instead of
a file.

Two Ubuntu-specific notes: on a headless machine or WSL without a desktop there is no browser to
open, so pass `--no-open` and point your own browser at the URL; and because the server
deliberately refuses to reuse a busy address, restarting within a few seconds can find the old
socket still in `TIME_WAIT` and quietly move to 8757. That is the fallback working, not a
failure — the banner tells you which port it took.

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

The repo ships with the harvested data, so cloning and running `serve.py` is enough. Rebuilding
everything from scratch against a live Zenodo takes five steps:

```bash
python3 scripts/01_harvest_records.py   # ~4 min without a Zenodo token
python3 scripts/02_download_madmps.py
python3 scripts/03_check_schema.py
python3 scripts/04_build_dataset.py     # downloads ~90 MB of CORDIS data on first run
python3 scripts/05_build_dashboard.py
```

On Windows use `python` instead of `python3`. Each step is independently re-runnable and skips
downloads already on disk.

A Zenodo token cuts the harvest to under a minute by raising the anonymous page size from 25
records to 100:

```bash
export ZENODO_TOKEN=...          # Ubuntu
$env:ZENODO_TOKEN = "..."        # Windows PowerShell
```

## A note on maDMP quality

Every downloaded `.json` was checked against the RDA DMP Common Standard 1.2 schema. Only **25 of 377** pass with no findings. The rest are structurally correct at the top level but hollow underneath — the most common gaps are `distribution.title` and `distribution.data_access`, and about half of all distribution objects are empty placeholders emitted by the exporting tool.

That is worth keeping rather than filtering out. Real-world incompleteness is exactly what an automated DMP review tool should be able to detect.

## Status

Work in progress. The pool is built; the 10 DMPs are not selected yet.

## No license

This repository is deliberately published without a licence. That is a choice, not an oversight: the work is in progress and I am not granting rights to reuse, modify or redistribute it while it is still moving. Default copyright applies.

If you want to use something here, ask me.
