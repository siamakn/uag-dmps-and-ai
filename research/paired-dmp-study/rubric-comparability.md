# Rubric comparability: publication cells and pinned native criteria

Prepared 2026-11-06. **Source audit and unapproved methods options; no human ratings, AI quality scores, model calls, instrument changes or phase decisions.** The important discrepancy is semantic as well as numerical: identical criterion IDs can hide omitted requirements, altered alternatives and lost applicability qualifiers. Even cells whose source requirements are retained need calibrated anchors before numeric agreement can be defined. The [machine-readable companion](rubric-comparability.json) gives per-phase classifications, physical/printed page locators, native JSON pointers and exact source hashes.

## Evidence and limits

The publication is Mansour et al., PDF Version 1.0, [Zenodo record 19630859](https://zenodo.org/records/19630859). Table 2 spans **physical pp7–22**, printed pp6–21. Lifecycle explanations are on physical p6, printed p5. I read the complete relevant text and visually inspected every Table 2 page, including continuation cells. These are 16 subsection IDs, not 48 independent criteria: each has phase-specific wording, with one blank cell.

The native comparison is default [eva.json at b80b43de820d46440d982eb99b2b3da8f4c2f818](https://github.com/usadellab/dmp-eva/blob/b80b43de820d46440d982eb99b2b3da8f4c2f818/eva.json), not fallback/custom instruments. This is a local pinned-byte audit; the existing live latest check was 2026-11-03, and campaign HEAD still needs the previously planned freeze-time refresh. No candidate DMP content was assessed.

| Source | Retained local path | SHA-256 |
| --- | --- | --- |
| publication | `data/paired-dmp-corpus/framework/DMP_Evaluation_V1.0.pdf` | `465a894b06bb67abea19acf16eba02dca8d665855a01572a7762ec3bb0e3fc26` |
| native_rubric | `data/paired-dmp-corpus/upstream/dmp-eva-b80b43de820d46440d982eb99b2b3da8f4c2f818/latest--eva.json` | `8f0c169d51219a80d6fcb13bb517eb7f65c0a6471853e1b32d20f5cc92c612f9` |
| native_extractor | `data/paired-dmp-corpus/upstream/dmp-eva-b80b43de820d46440d982eb99b2b3da8f4c2f818/latest--js--criteria-extractor.js` | `6c33859a7ae0be13b63cea52b436cd8a46f83aa54892a5a042457ff9f8999006` |
| native_prompt_assembler | `data/paired-dmp-corpus/upstream/dmp-eva-b80b43de820d46440d982eb99b2b3da8f4c2f818/latest--js--llm-service.js` | `9af182a7249222aaff30e57e9e686839a4f67c6c67ee861d136ae5a58df8608b` |

Exact native source locations below use this hashed `latest--eva.json`. JSON pointer `/data_management_plan/i/subsections/j/stages/PHASE` identifies a phase cell; the rows give each subsection prefix and stage line numbers. Column order is **E = proposal_early_stage, M = mid_project, L = end_project**. PDF locations are physical page numbers, including continuation pages. “Retained” means no material requirement difference found in the source cell, not validated scoring equivalence. Examples and recommendations must not silently become mandatory anchor elements.

[criteria-extractor.js lines 715–762](https://github.com/usadellab/dmp-eva/blob/b80b43de820d46440d982eb99b2b3da8f4c2f818/js/criteria-extractor.js#L715-L762) loads the identified stage cells. **The loaded source rubric is not the model-visible rubric**: [llm-service.js lines 74–109](https://github.com/usadellab/dmp-eva/blob/b80b43de820d46440d982eb99b2b3da8f4c2f818/js/llm-service.js#L74-L109) extracts IDs and appends phase guidance, without inserting complete criterion wording. The existing [actual-function preflight](tool-preflight.md) confirms this. Thus even source-retained cells do not establish that the native model was instructed to apply those requirements. Intended rubric phase, loaded stage, prompt guidance and final prompt bytes remain separate provenance fields; this report does not patch their mismatch.

## Criterion crosswalk

### 1a

Publication Table 2, physical pp **E 7,8; M 7; L 7**. Native subsection `/data_management_plan/0/subsections/0`; stage lines **11, 12, 13** (E/M/L).

- **E — omitted requirement.** Native omits the explicit personal-data-subject permission justification. Generic sources/access/permissions remain; they do not explicitly restore that check.
- **M — retained.** Produced/reused data, changes, provenance and evolving documentation are retained.
- **L — retained.** Final datasets and justification of deviations are retained.

### 1b

Publication Table 2, physical pp **E 8; M 8; L 8**. Native subsection `/data_management_plan/0/subsections/1`; stage lines **20, 21, 22** (E/M/L).

- **E — retained.** Expected types, formats, volumes, proprietary-format justification and a no-new-data explanation are retained.
- **M — retained.** Workflow monitoring, actual technical characteristics and format-conversion strategy are retained.
- **L — retained.** Final technical documentation/metadata and technical fidelity for reuse are retained. This cell is not simply a final volume inventory.

### 2a

Publication Table 2, physical pp **E 8,9; M 8,9; L 8,9**. Native subsection `/data_management_plan/1/subsections/0`; stage lines **35, 36, 37** (E/M/L).

- **E — retained.** Descriptive/process metadata, community standards, suitability, creation tools and metadata formats are retained, despite the shortened question.
- **M — retained.** Standards/tools, QA/QC, selection rationale, conditional schema justification and metadata storage/sharing are retained.
- **L — retained.** Documentation evidence, QA outcomes and post-project metadata maintenance are retained.

### 2b

Publication Table 2, physical pp **E 9,10; M 9; L 9,10**. Native subsection `/data_management_plan/1/subsections/1`; stage lines **44, 45, 46** (E/M/L).

- **E — retained.** Verification/validation, versioning, QC procedures and conditional ethics-review reference are retained.
- **M — retained.** The implementation report requirement is retained.
- **L — retained.** QC measures and integration with ethical/legal/preservation criteria are retained.

### 3a

Publication Table 2, physical pp **E 10,11; M 10,11; L 10,11**. Native subsection `/data_management_plan/2/subsections/0`; stage lines **59, 60, 61** (E/M/L).

- **E — omitted requirement.** Native retains storage/backup and the conditional security statement, but omits specifying whether an external-storage Data Processing Agreement is needed.
- **M — omitted requirement.** Native retains actual locations/procedures/security tests, but omits documenting and approving institutional-policy deviations.
- **L — retained.** Final arrangements and transfer to preservation meeting security/integrity standards are retained; the publication adds emphasis on personal data.

### 3b

Publication Table 2, physical pp **E 11; M 11,12; L 11**. Native subsection `/data_management_plan/2/subsections/1`; stage lines **68, 69, 70** (E/M/L).

- **E — less operational detail.** Roles, access levels, sensitive-data justification and grant/documentation process remain. Publication additionally gives confidentiality/IP and account/authentication examples; do not turn examples into mandatory subtests.
- **M — omitted requirement.** Native omits explicit authentication/authorization, removal of users no longer requiring access, and identification of the project/IT audit-log custodian.
- **L — retained.** Discontinuing access and handling post-completion external requests are retained.

### 3c

Publication Table 2, physical pp **E 12,13; M 12,13; L 12**. **Absent from the complete default native instrument**; no stage pointer or score exists.

- **E — not in native instrument.** No native 3c stage cell. Related security material in 3a/4a is overlap, not complete coverage of classification, safeguards, support and incident planning.
- **M — not in native instrument.** No native 3c stage cell. Other IDs do not restore explicit incident/near-miss reporting, response and secured-transfer checks.
- **L — not in native instrument.** No native 3c stage cell. Do not infer a criterion result from other IDs or count absence as zero/NA.

### 4a

Publication Table 2, physical pp **E 13,14,15; M 13,14,15; L 13,14**. Native subsection `/data_management_plan/3/subsections/0`; stage lines **83, 84, 85** (E/M/L).

- **E — omitted requirements and conditions.** Native compresses legal basis to Article 6/9 and omits the detailed conditional basis/subject-information checks, DPIA timing, safeguards, support and planned agreements. The publication explicitly accepts an inapplicability statement; the native question is conditional but lacks that instruction.
- **M — omitted requirements and conditions.** Native retains ROPA/basis/consent/DPIA/TOM headings but drops conditional qualifications and detail on approved locations, international-transfer assessment, agreements, oversight and changes in processing scope. Generic consent wording must not become a universal consent requirement.
- **L — changed acceptance routes.** Native requires anonymized published outputs, while the publication also permits appropriate controlled access and documented exceptions for public outputs. Native also omits retention-schedule alignment, future-reuse basis, compliance-record archiving and lifecycle monitoring. This is altered acceptance logic, not just abbreviation.

### 4b

Publication Table 2, physical pp **E 15,16; M 15,16; L 15,16**. Native subsection `/data_management_plan/3/subsections/1`; stage lines **92, 93, 94** (E/M/L).

- **E — omitted requirements and conditions.** Native keeps IPR, third-party licensing, ownership and legal frameworks, but drops the no-restriction statement route, agreement/contract ownership context and TTO/legal-department handling.
- **M — omitted requirement.** Native keeps licensing/agreements/access, but omits post-completion publication/reuse rights and responsibility for IP records.
- **L — omitted requirement.** Native keeps ownership/post-project access/registered IP, but omits fulfillment of obligations and collaborators/institutions awareness of continuing rights/restrictions.

### 4c

Publication Table 2, physical pp **E 17,18; M 17; L 17**. Native subsection `/data_management_plan/3/subsections/2`; stage lines **101, 102, 103** (E/M/L).

- **E — omitted requirement.** Native keeps broad ethics approval/recruitment/safeguards/codes, but drops approval application status, participant information/risk detail, cultural/community considerations, vulnerable-group safeguards and responsible person/procedures.
- **M — omitted requirement.** Native omits naming the approving body and explicit recruitment/sampling changes. Ethical/study-population changes remain.
- **L — omitted requirement.** Native omits participant agreements in the published-material check. Broad fulfillment/documentation and end-of-study obligations remain.

The original PDF itself has no printed 4c heading/question above this ethics block, not merely a failed text extraction. Attribution follows its location between 4b and section 5 and the content/native ID. Preserve that attribution caveat; the visible cell wording is unambiguous.

### 5a

Publication Table 2, physical pp **E 18; M 18; L 18**. Native subsection `/data_management_plan/4/subsections/0`; stage lines **116, 117, 118** (E/M/L).

- **E — changed logical connector.** For unshareable data, publication has separate metadata-sharing and ten-year-storage explanations; native joins them as alternatives with OR. A plan meeting just one can meet the native wording while leaving a publication check unanswered.
- **M — mixed scope change.** Native drops selected-but-not-yet-used repositories, timeline-format changes and internal data sharing (retains metadata sharing). This both narrows the repository route and reduces other checks.
- **L — omitted requirement.** Native retains licenses/restrictions/embargoes/sensitive-access conditions, but drops access procedures and an explicit availability-timing/embargo-justification check.

### 5b

Publication Table 2, physical pp **E 18,19; M 18,19; L 18,19**. Native subsection `/data_management_plan/4/subsections/1`; stage lines **125, 126, 127** (E/M/L).

- **E — qualifier removed and omissions.** Native drops metadata selection and a detailed no-repository storage route. It presents 10+ years without the publication example qualifier or alignment to funder/community expectations; calibrate whether this is being read as a fixed minimum.
- **M — omitted requirement.** Native keeps dataset selection/criteria and archive confirmation but drops retention-period updates.
- **L — omitted requirement.** Native keeps deposit/metadata/license/PID confirmation but drops explaining deviations. PID mention here does not replace full 5d coverage.

### 5c

Publication Table 2, physical pp **E 19; M 19; L 19,20**. Native subsection `/data_management_plan/4/subsections/2`; stage lines **134, 135, 136** (E/M/L).

- **E — omitted requirement.** Native keeps planned formats/tools and open-format preference but drops acknowledgement/justification of proprietary formats.
- **M — omitted requirement.** Native keeps tool/format updates and open-source preference, but omits alternatives or rationale when proprietary tools are required.
- **L — mixed scope and conditionality change.** Native keeps preservation formats/access mechanisms/code links, but omits explicitly naming needed tools and the conditional small-dataset dual-format recommendation. It drops the applicability qualifier for code/workflows and the open-license preference. Conditional recommendations require distinct treatment from obligations.

### 5d

Publication Table 2, physical pp **E 20; M 20; L 20**. **Absent from the complete default native instrument**; no stage pointer or score exists.

- **E — not in native instrument.** No native 5d stage cell; publication has PID planning and a justification route for no PIDs.
- **M — instrument undefined and not in native instrument.** Publication middle cell is visibly blank. Instrument undefined is distinct from both native omission and document-level inapplicability; do not infer wording from early/end or 5b.
- **L — not in native instrument.** No native 5d stage cell; the publication checks published-dataset PIDs and linkage to metadata. The 5b deposit/PID mention is only partial conceptual overlap.

A publication mid-project row is retained as **instrument undefined** with no score. Native absence remains a separate coverage field. Neither means that PID practice is inapplicable to a project.

### 6a

Publication Table 2, physical pp **E 20,21; M 20; L 20**. Native subsection `/data_management_plan/5/subsections/0`; stage lines **149, 150, 151** (E/M/L).

- **E — omitted requirement.** Native keeps roles/task assignment/post-project responsibility, but task examples omit acquisition, recovery and compliance responsibilities.
- **M — omitted requirement.** Native keeps actual roles/effort, bottlenecks and onboarding, but omits explicit fulfillment monitoring, overlaps, replacements and updating RDM documentation for the team.
- **L — omitted requirement.** Native omits institutional support in the final contributor list and adequacy of responsibilities (retains resource adequacy).

### 6b

Publication Table 2, physical pp **E 21,22; M 21; L 21**. Native subsection `/data_management_plan/5/subsections/1`; stage lines **158, 159, 160** (E/M/L).

- **E — less operational detail.** Resource estimates and planned support remain. Native drops the illustrative quantification detail and separate acknowledgement of existing institutional infrastructure/services; generic planned support does not necessarily cover the latter.
- **M — omitted requirement.** Native drops expenditures, adjustments, software sufficiency and additional support acquired; allocation/workload/storage/training remain.
- **L — omitted requirement.** Native drops impact of resources on effectiveness; total spending, cost-efficiency, FAIR adequacy and support reporting remain.

## Consequences for scientific comparison

The most material acceptance changes are **4a end** (controlled-access/exception routes lost), **5a early** (two conditional checks become alternatives), **5b early** (retention example qualifier lost), and **5c end** (code/workflow applicability qualifier lost). Such differences can change what would count as sufficient evidence. Security or PID mentions under another ID do not silently restore the omitted 3c/5d instrument rows. Do not treat a complete 14-ID output as coverage of all 16 framework IDs, or add zeros for the missing two.

Some cells are more closely aligned than the blanket description “abbreviated rubric” suggests: all three phase cells of 1b, 2a and 2b retain the substantive requirements, as do 1a mid/end, 3a end and 3b end. That narrows the semantic problem for those cells, but provides no validated numerical conversion. Native evidence-unit 0–100 scores/aggregation and the approved-for-calibration human criterion-level 0/1/2 scale remain different measurement systems. **All 14 shared IDs require future anchor/scale calibration and phase-specific crosswalk review before numeric human/native agreement is claimed.** No mapping, thresholds, adjusted score or approved common aggregate is supplied here. For 3c/5d there is no native numeric counterpart to calibrate in this default instrument.

Source comparisons here classify what the framework/native text asks a reviewer to examine. References to GDPR, agreements or ethical approvals are not this audit's legal advice, proof of legally binding obligations in a particular case, or a finding of actual project compliance. Review evidence is necessarily bounded by the packet. Full Table 2 cells, not the short navigation labels or this analytical summary, remain the authoritative source for future anchor calibration.

## Phase-policy alternatives for this paired study

The sampling arithmetic and rubric phase are separate. **Early ≤50% does not mean proposal-stage**; the selected early documents are post-award DMPs. Equally, the publication explicitly combines *proposal/early* in one category, so post-award status alone does not rule that category out. Physical p6 defines strategies, implementation/progress and final outcomes, without duration thresholds. **Late >100%** coheres with an end-project concept, but an issue date alone cannot demonstrate completed actions or their documentation.

No option below is approved or selected. Fix the primary policy and calibration anchors before final-cohort scoring, keep each sensitivity condition separate, and do not select the phase that gives favorable results.

| Option | Concrete assignment | Scientific benefit | Main cost or interpretation limit |
| --- | --- | --- | --- |
| P1 Initial strategy versus final outcomes | All sampled early documents: proposal_early_stage; all late documents: end_project. | Uses the publication combined proposal/early category for initial strategies and its end category for documented outcomes. Post-award status does not itself exclude the combined early category. | The <=50% bin can contain established implementation; early anchors may under-demand evidence. Different early/end requirements prevent a common-scale improvement interpretation. |
| P2 Implementation checkpoint versus final outcomes | All sampled early documents: mid_project; all late documents: end_project. | Makes implementation/progress central for post-award DMPs and avoids treating every early sample as a proposal. | An initial deliverable may legitimately contain plans before substantial data production; mid requirements can over-demand evidence. Also changes expectations across versions. |
| P3 Common end-state readiness lens | Both versions: end_project, explicitly labelled readiness against end-state expectations. | Holds criterion wording constant for a descriptive within-pair change in documented readiness. | Early plans are intentionally assessed before outcomes are due; this changes the construct from stage-appropriate sufficiency to end-state readiness. It cannot be described as the framework stage-sensitive evaluation. |
| P4 Declared phase sensitivity analysis | For each early document retain separate proposal_early_stage and mid_project conditions; all late documents use end_project. | Shows whether the conclusion depends on early-phase interpretation without pretending <=50% resolves it. | More human/model assessments, correlated repeat exposure and multiplicity; the primary interpretation still must be chosen before results. Mid-project 5d is instrument undefined in this condition. |

A per-document early/mid assignment is another possible policy, but it would require an advance rule using independently documented milestones or version purpose, applied before quality review. Choosing the phase because the DMP already contains more implementation detail would make the assessment depend on the content it is meant to assess. With only six project pairs, additional heterogeneous phase assignments also make already limited comparisons harder to interpret.

End-phase cells often point beyond a standalone DMP: 1b requests archiving technical records; 2a requests documentation evidence; 4a includes compliance records and output safeguards; 5b/5d concern actual deposits/PIDs; 6b concerns resources spent and support. Under a DMP-only packet, the measurable construct is **what the DMP documents about these outcomes**, not proof that the practices occurred. If linked repositories/annexes are to be evidence, freeze which external artifacts and retrieval dates are allowed and supply the same evidence to the conditions intended to be comparable. A missing external artifact is `unavailable_in_packet`, not automatically “not reported,” a zero, or a legal-compliance failure. Restricted compliance material must not be presumed publicly accessible.

Before any numerical comparison: approve a phase policy and evidence boundary; calibrate criterion/phase anchors on outside-cohort material; retain source changes and acceptance routes explicitly; justify any native/human scale crosswalk separately; and keep native omissions, instrument-undefined cells, document NA, unavailable evidence and missing model output as distinct dispositions. A second human condition using native source wording is possible only as a separately identified instrument/record, not a replacement of the publication reference. These are preparation requirements and future methods decisions, not a current human task.

## Verification scope

Mechanical checks verified 16 unique IDs, 14 native presences, all 42 exact native stage pointers/line numbers, all four source hashes and the distinct blank mid-project 5d disposition. A second reader independently checked primary rendered cells for 4a end, 5a early, 5b early and blank mid-project 5d against these claims, with no material correction. This is a bounded check, not a second exhaustive semantic review of all 16 IDs.
