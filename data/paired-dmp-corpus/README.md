# Local copies of the proposed paired DMP corpus

These are third-party source PDFs and CORDIS evidence snapshots for
`research/paired-dmp-study/cohort-proposal.json`. Each PDF keeps its original terms;
the repository's MIT documentation/code licence does not license these documents.
The manifest records source links, attribution metadata, exact SHA-256 hashes,
local paths and rights evidence. AGRICORE's blanket reuse licence is unknown;
public accessibility does not establish permission for every intended use.

PDFs and downloaded source snapshots are ignored by Git. Do not publish this
directory as a source-document bundle without checking the recorded terms.
The public proposal consists of metadata, source links and checksums.

`python3 research/paired-dmp-study/prepare-cohort.py` preserves inspected bytes from
the current research caches, or checks already preserved copies. It does not fetch
new sources or change the historical dashboard selection. On a fresh clone,
retrieve the linked source files and verify their hashes with
`python3 research/paired-dmp-study/verify-cohort.py` before relying on a local copy.
Changed remote bytes represent a different source version; retain the old
manifest rather than silently accepting them as the inspected documents.
