# Reconciliation with UAG meeting minutes

Read 2026-11-03. Source: [UAG 9 — DMPs and AI, supplied Google Doc](https://docs.google.com/document/d/1weSr-2fSnyMoOCq-AynX9tzCVwhxgh6woGyttz4i91w/edit?tab=t.0#heading=h.rahed0egsi0l).

## Access and provenance

The ordinary web reader failed, but a direct read-only Google Docs TXT export returned HTTP 200, `text/plain; charset=utf-8`, 13,964 bytes. Source SHA-256: `440080d67adbee24eecc03645fb3b55f849babadf03cc4668de343a1374dd74f`. Export endpoint: `https://docs.google.com/document/d/1weSr-2fSnyMoOCq-AynX9tzCVwhxgh6woGyttz4i91w/export?format=txt`.

**No user login, sharing change or plugin connection is required for this successful retrieval.** The earlier access limitation is resolved. The temporary source is `/tmp/uag-meeting-minutes-response`; it is a retrieval cache, not a durable repository artifact. This report records relevant scientific decisions without duplicating the attendee contact list or meeting-access credentials. An agent can retrieve the export again and compare its hash; a later hash difference indicates a changed source snapshot, not necessarily an error.

Scope read: the exported text contains meetings from 2026-07-13 through 2026-11-02 in the supplied document. This does not establish that other Google Docs tabs, comments or revision history were inspected. Links represented only as labels in the text export were not followed or guessed.

## Relevant evidence and current interpretation

| Meeting | Recorded study-relevant point, paraphrased | Consequence for this study |
| --- | --- | --- |
| 2026-11-02 | Propose six projects across six disciplines, each with a late DMP and one before half of project duration; present limitations and alternatives. | Supports the six-project paired design and explicit feasibility reporting. The user's subsequent issue-date ≤50%/>100% rule supplies the exact current thresholds. |
| 2026-09-07 | Twelve DMPs across six categories, with one around project end and one before halfway. A deliberately incomplete example was also considered if no poor example appeared naturally. | Historical approximate timing differs from the current strict rule. Keep any synthetic stress test separate and clearly labelled; do not select naturally occurring documents based on perceived quality or count synthetic variants among the six longitudinal pairs. |
| 2026-08-24 | Selection should consider discipline, recency, stage, programme and format while avoiding preference for plans that look good. A metadata dashboard supports discovery. | Confirms metadata-based selection and the role of the existing platform. Wider institutional/DFG sourcing was discussed, but is not mandatory for the user's current EU-focused cohort. |
| 2026-08-10 | Manual review using the Infra-DMP matrix was suggested, including an example of two reviewers, 1–10 ratings and averaging. A Horizon 2020 DMP collection was identified. | Two reviewers are supported as an earlier proposal; the numerical scale and averaging are examples, not an established validated reference. Retain independent ratings and settle scoring/adjudication after calibration. |
| 2026-07-27 | Mansour et al., Science Europe and several related studies were listed; DMP-EVA was demonstrated and its repository identified for reporting issues. | Establishes the intended tool and a starting literature list. It does not authorize this agent to post issues or contact authors. |
| 2026-07-13 | The group aims to develop responsible-AI recommendations for data/software management planning, supported by observations and case studies; data stewards and researchers are target audiences. Fast tool/model change was explicitly recognized. A first draft around May 2027 was discussed. | Supports a versioned case-study design and actionable recommendations. The timeline is context, not a new deadline or an authorized schedule. |

The separate 2026-10-07 colleague minutes pasted by the user remain an additional source. They specify standardized overall/criterion prompts, human assessment, open-weight models, Mainz UI/API and a reviewer GUI. They are not a meeting entry in the retrieved biweekly document and must not be attributed to it.

## Related-work leads recovered from the minutes

These are **leads named in the minutes**, not publications newly reviewed in this reconciliation:

- Science Europe (2021), [Practical Guide to the International Alignment of Research Data Management](https://doi.org/10.5281/zenodo.4915862).
- Repo et al. (2026), [Human-Centred AI for Data Management Plan Assessment and Support](https://doi.org/10.5281/zenodo.21401065). The minutes indicate existing group contact with these authors; no new outreach was performed.
- Gajbe, Tiwari and Singh (2021), [Evaluation and analysis of data management plan tools: a parametric approach](https://doi.org/10.1016/j.ipm.2020.102480).
- Vandenberk (2025), [Data management plan completion and reviewing through human-in-the-loop AI](https://documentserver.uhasselt.be/handle/1942/46881).
- [University of Vienna Horizon 2020 DMP collection](https://phaidra.univie.ac.at/o:1140797), a potential discovery source rather than a guarantee of eligible paired versions.

Review these selectively for human-reference methods, evidence traceability, lifecycle handling and source corpora before making novelty claims. Other responsible-AI readings in the minutes can inform reporting practice; they need not delay the initial paired-version search.

## Methodological recommendations

1. Use the user's current explicit decisions where they refine historical meeting suggestions; preserve the differences in the decision log.
2. Keep the real-document cohort independent of synthetic stress tests. A later synthetic omission experiment can measure sensitivity, with parent document, transformation and expected affected criteria documented separately.
3. Do not average reviewer scores before checking disagreement, scale interpretation and applicability. Save original judgments and evidence; use a declared reconciliation procedure.
4. Connect findings to practical recommendations for reviewers and DMP-EVA maintainers: reliable evidence citation, stage handling, uncertainty, model variability and reproducible tool versions.
5. Report tool/publication differences candidly without requiring them to converge. The latest pinned tool is the confirmed working target; the publication supplies methodological context and a rubric reference, while actual behavior is evidenced independently.
