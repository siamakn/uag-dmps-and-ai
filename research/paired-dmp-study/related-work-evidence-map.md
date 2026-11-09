# Focused evidence map for the paired DMP study

Checked 2026-11-06. This extends the [initial seed review](related-work-initial.md).
It is a documented, targeted web search and methods reading, **not a systematic
review, complete citation search or proof of novelty**. Search strings, reading
scope, exclusions and source hashes are in
[the machine-readable map](related-work-evidence-map.json). No platform review,
human scoring or model execution is part of this work.

## Additional primary evidence actually inspected

| Source | Methods evidence | Consequence for our proposed study |
| --- | --- | --- |
| [Pham et al. (2023), DOI 10.5334/dsj-2023-002](https://datascience.codata.org/articles/10.5334/dsj-2023-002), HTML sections 4.1–4.2 | Compares text mining with manual scoring of 21 funded Belmont Forum DMPs. Manual scoring uses 16 criteria and 0/1/2; team discussion resolves differences. | Automated/manual DMP comparison has prior work. A numerically similar scale does not validate our phase-specific anchors. Retain pre-adjudication ratings rather than describing reconciled unanimity as independent agreement. |
| [Sharma et al. (2023), DOI 10.1007/978-3-031-28032-0_3](https://doi.org/10.1007/978-3-031-28032-0_3), [NSF-hosted full text](https://par.nsf.gov/servlets/purl/10546297), physical pp1–2, 6–9 | Applies DART and Belmont instruments to 150 plans across five NSF programs and 2011–2021 award years. Two coders divide the plans; each plan is scored once per instrument. | Its longitudinal sample spans award years; the inspected methods do not establish same-project version pairing. Instrument effects deserve attention alongside model effects. |
| [Miksa et al. (2023), DOI 10.5334/dsj-2023-028](https://doi.org/10.5334/dsj-2023-028), physical pp2–9, especially p9 Table 1 | Maps maDMP validation methods to reviewer goals, separating expected and achieved FAIRness. It excludes narrative-language checking from its implemented method coverage. | DMP text review and validation of linked research outputs are different tasks. Keep any external-resource verification separate from document-only assessment. |

The Sharma chapter is **2023**, despite the deposited PDF's 2024 modification
timestamp and a search result's relative date. The title page supplies the
publication year and DOI. Similarly, a statement that every plan was scored
twice refers to two different instruments; it is not evidence that every plan
received two independent ratings with the same instrument.

The two closest seed studies receive a separate deeper
[methods report](prior-study-methods.md): Repo et al.'s 2026 DMP Analyser
presentation and Vandenberk's 2025 thesis. That report distinguishes material
actually read from inaccessible methods. Its existence does not imply that both
full texts were successfully obtained.

## Newly identified, incompletely inspected work

[Frnka's 2025 CTU thesis](https://dspace.cvut.cz/handle/10467/122627) explicitly
addresses extractive question answering for DMP template questions and reports
human-annotated resources in the institutional abstract. The abstract was read;
the methods were not. The direct live landing response was only a JavaScript
application shell, not readable thesis content. Model rankings, annotation
quality and test-set independence have therefore not been audited here.

A separate [Frnka and Suchánek article](https://doi.org/10.3724/2096-7004.di.2025.1132)
is verified in the publisher-registered Crossref record as a 2026 publication.
The DOI's embedded 2025 is not its publication year. Crossref supplies publication
date 2026-06-01 and online date 2026-06-18. Its publisher PDF link returned HTTP
200 with **zero bytes**; the article was not obtained or read. It remains a
priority follow-up. A common author/topic does not prove identical thesis and
article methods or datasets. No conclusions about missing lifecycle analysis
can be drawn from these access failures.

## Defensible positioning now

The contribution should be described as a **small, auditable paired case study**:
six metadata-selected projects, twelve same-scope versions with evidenced issue
dates, a lifecycle-sensitive reference process, and reproducible evaluation of
a pinned current DMP-EVA configuration. This is a proposed contribution, pending
reference assessments and experiment execution. Do not claim the first automated
DMP assessment, first human/AI comparison, first longitudinal DMP study, or a
validated general-purpose benchmark.

Practical value for the UAG, NFDI and other data-support groups can come from
reusable provenance records, calibrated reviewer instructions, traceable error
examples and versioned fixes. Such value depends on releasing usable materials
with their rights and limits, rather than a favorable overall score. One project
per discipline supports coverage of cases, not discipline rankings.

## Methods consequences to carry forward

1. Keep the question answered by each instrument explicit. Extracting a relevant
   answer, judging its sufficiency, and verifying implementation are separate
   targets. Do not combine their scores as interchangeable accuracy measures.
2. Preserve independent ratings, applicability and uncertainty before discussion;
   later consensus is not a replacement for reporting initial disagreement.
3. Separate lifecycle sampling windows from rubric phases, and phase expectations
   from input exposure. See the [semantic audit](rubric-comparability.md).
4. Report native-tool behavior separately from full-rubric configured conditions.
   Otherwise an instrument or information change could be attributed to a model.
5. Complete the high-priority full-text and citation follow-ups before writing a
   manuscript novelty claim. Current evidence is enough to narrow our claims,
   not enough to establish that no other paired-version study exists.

Source captures remain under the ignored
`data/paired-dmp-corpus/methods-2026-11-06/` directory. Links and hashes identify
evidence; no third-party document is relicensed or bundled for public release.
No new scientific decision, reviewer assignment or human task is created here.
