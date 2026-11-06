# Independent review of input packets and experimental preparation

Reviewed 2026-11-04. **The input packets pass structural and byte-integrity checks, and the experimental draft is coherent as a proposal. No blocking preparation defect remains.** The findings do not establish extraction fidelity, approved benchmark inputs, a frozen experiment, human labels or successful model execution. The human pilot remains deferred; this review creates no task for a human assessor.

Scope: [packet implementation](input-packets.py), [self-check](input-packets-selfcheck.py), [manifest](input-packets.json), [method report](input-packets.md), all twelve generated packet directories and original PDFs, [experiment draft](experiment-protocol-draft.md), [matrix](experiment-matrix.json), and relevant decision/provenance records. Only this review report was written. No dashboard, production script, README/status or Claude handoff was edited. No network, model or provider request was made.

## Input checks and findings

The following existing checks were run successfully:

```sh
python3 research/paired-dmp-study/input-packets.py --verify
python3 research/paired-dmp-study/input-packets-selfcheck.py
```

Code inspection confirms that `--verify` reads stored assets, checks source PDF and proposal hashes, reparses stored XML and compares regenerated assets/manifest without extracting again or writing files. The self-check writes only a temporary fixture directory under the ignored packet tree and removes it. It covers a non-BMP character counted as two UTF-16 units, an empty page, an oversized page, whole-page coverage and corrupted-output detection.

An additional independent calculation did not import the builder. It compared `pdfinfo` page counts, all raw XML word/line sequences, the mapped JSON, chunk page assignments and stored text. It confirmed:

| Property | Observed result |
| --- | ---: |
| Exact proposed source PDFs | 12; all SHA-256 values match |
| Physical pages | 521; each PDF count matches XML, mapped JSON and manifest |
| Extracted lines | 24,125; same ordered word sequence per line |
| Extracted word elements | 144,770; each mapped once, in extractor order |
| Word bounding boxes | 144,770; required coordinates present, finite and ordered |
| Whole-page chunks | 79; contiguous page sequence with no omission or duplicate assignment |
| Largest chunk | 23,946 UTF-16 code units |
| Oversized chunks / empty pages in this corpus | 0 / 0 |

Line and word IDs are unique within each document. Concatenating each document's chunk files reproduces its complete `pages.txt` exactly. This validates preservation of the **stored extraction**, not that Poppler captured every source item. The real corpus contains no non-BMP extracted characters or empty extracted pages; those edge cases are covered by the synthetic fixture rather than inferred from real documents. Additional deliberately malformed XML fixtures confirmed rejection of words/lines outside the expected hierarchy. Both Python files also parse under Python 3.7 syntax rules.

The implementation retains raw extractor bytes, word strings, line/page navigation, coordinates and page dimensions. Joining word elements with one space and adding markers changes text representation; this is correctly documented. Coordinates do not restore table-cell relationships, reading order, checkboxes, figures or OCR content. The method report appropriately avoids a semantic-fidelity or full-document visual-QA claim. This review did not repeat the previous 24-page visual extraction QA or certify the remaining source pages visually.

The 24,000-unit value is an engineering budget, not a token or provider-context guarantee. Prompt, rubric, output allowance and provider overhead still require actual backend checks. Whole-page chunks can split a multi-page table; oversized pages remain intact and explicitly flagged. Page/line markers also consume native parser space and can change which original text survives its prefix cap. Before choosing this representation for any condition, record whether those markers are model-visible and rerun the relevant input/prompt preflight on the exact chosen bytes.

Minor future hardening, not a current blocker: `sources()` checks twelve unique PDF paths but does not explicitly reject two entries that resolve to the same `(grant, record)` output directory. All twelve current output directories are distinct. A later manifest allowing multiple files from one record should validate destination uniqueness before a build, to avoid overwriting one document's packet assets.

## Terms and intervention boundaries

`git check-ignore` confirms that packet XML/text/JSON assets and original PDFs are ignored by the corpus-local rule. The visible corpus `.gitignore` and README do not imply that raw source content is being tracked. The packet manifest pins the proposal hash, where source-specific licence evidence remains recorded; it does not assign a new licence to third-party documents. AGRICORE's unknown blanket reuse terms remain explicit. Local preparation is not permission for external submission or redistribution.

The packet report and experiment draft correctly treat chunking, parser bypass, changed rubric text, phase corrections and new score aggregation as declared configurations/interventions. A native run retains its actual parser prefix, quote substitution, effective rubric/phase behavior and native aggregates. The 79 chunks are preparation artifacts: they are neither automatically 79 requests nor 79 independent observations, and no averaging/max/voting rule follows from generating them.

## Experimental design review

The machine matrix matches the six project/grant pairs in the proposal. It correctly treats six projects as six analysis clusters, with two documents and criterion/repeat observations nested within each. It avoids discipline rankings, criterion-row independence and causal claims about early/late improvement.

N0 is an operational native diagnostic. F0/F1 are separately configured comparisons with complete inputs, explicit criteria and a proposed calibrated ordinal output. Native-versus-configured differences change input exposure, rubric, phase handling and scale jointly; they cannot identify one repair or model effect. Within F0/F1 the design holds model, source content, full rubric context and output semantics constant while changing target scope and request structure. The later model comparison holds F0 fixed. Full-app/provider behavior and implementation of those configured paths remain to be demonstrated.

The approved 0/1/2 scale is identified as calibration-only. Benchmark anchors and phase/crosswalk choices remain pending, with no invented conversion from native 0–100 scores. Native missing criteria, undefined instrument cells, inapplicability, uncertainty and failed outputs remain separate. The draft also preserves a full-human versus native-prefix information confound and requires failure/coverage denominators alongside conditional numerical agreement.

The proposed primary calculation is project-balanced: criterion disagreement within document, two document means within project, then equal weighting across six project contrasts. This is descriptive pilot evidence. Conditioning on both conditions producing numeric applicable judgments can select an easier subset, so the mandated fixed-denominator coverage/applicability/failure reporting is necessary; the conditional result must not be presented alone as unconditional accuracy.

One inconsistency was identified and resolved during review: the opening estimand sentence initially said “agreement,” while its calculation, sign and JSON specified **disagreement**. The coordinator changed it to project-balanced exact disagreement rate. The final paragraph and matrix now agree that negative F1-minus-F0 favors F1.

Request arithmetic was independently checked: at most 216 first-stage logical requests; 228 including the proposed second-model F0 extension; 648 for three main repeats; 684 including its model extension. The six outside-cohort smoke requests and transport retries are explicitly separate. Twenty-four human document assessments can yield up to 384 criterion rows, which do not increase the number of independent projects. These are proposed counts, not approved spending or executed work. One repeat cannot measure stochastic stability.

Before execution, the stated freeze gates still matter: complete input QA and context feasibility; exact prompt/configuration/model pins and actual settings; phase/crosswalk/anchor decisions; reference independence and masking; missingness/retry rules; and intended submission terms. Any chunk-based alternative needs its own evidence-linkage, omission, deduplication and final-judgment policy. Technical preparation can continue while the human pilot is deferred.

## Reviewed identities

SHA-256 values at this review:

| Artifact | SHA-256 |
| --- | --- |
| `input-packets.py` | `c2e7fd531792d2123d92911c715d408a5112ee53e3811843d0dad26ea4191540` |
| `input-packets-selfcheck.py` | `5a55c307b22122c4b88dc25834eef4d8830cb318f7c4417c7a68a010cb0f5ebd` |
| `input-packets.json` | `015e20eb08597303b2f2487612e2469f23bab73499f3b2599203d3e5ae333bbd` |
| `input-packets.md` | `319b24537533d0895f8b6ba756dcc6551383bd7e0579a04d220f98f0a2d3651c` |
| Final corrected `experiment-protocol-draft.md` | `3d2ea9c7d69b470d2b7512119513fbe19022de0eef8a3904c431822f96b744a6` |
| `experiment-matrix.json` | `5ad513c11400704dc3e8abf627d583d2340ca613a01c411a9e4024fffbf54f10` |
| `cohort-proposal.json` | `edf1d3eab475302156d0366f262516e61d674a553fe67366a7181aff35a735fd` |

Later edits require checking the affected claims rather than treating this review as approval of arbitrary subsequent versions.
