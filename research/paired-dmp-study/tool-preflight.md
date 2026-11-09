# DMP-EVA browser preflight without model calls

Checked 2026-11-04. **All 44 assertions passed** in Google Chrome 156.0.8078.79 against pinned DMP-EVA commit [`b80b43de820d46440d982eb99b2b3da8f4c2f818`](https://github.com/usadellab/dmp-eva/tree/b80b43de820d46440d982eb99b2b3da8f4c2f818). The assertions confirm the specified observed behavior, including anomalies; they do not mean those behaviors are desirable. This ran the actual exported functions in an isolated temporary browser page, using exact hash-verified source bytes. No model or provider request was made.

## Five bounded behavior checks

| Behavior | Actual browser result | Interpretation for a campaign |
| --- | --- | --- |
| Default prompt content | Default extraction yields 14 IDs, excluding 3c and 5d. The assembled prompt contains those IDs but none of the 14 complete criterion names or descriptions. Distinctive synthetic name, description and `criteriaContext` markers are absent too. Input double quotes become single quotes. | Preserve and inspect the final model-visible prompt; loading a rubric file does not establish that its wording reaches the model. |
| Phase mapping | Short keys select the appropriate rubric stage but all three get early-stage prompt guidance. Long keys select the intended prompt guidance but all three get early-stage rubric wording. | Phase intent requires an explicit campaign decision. This exercised extractor/prompt functions with the keys recorded in the source review, rather than running single/batch UI orchestration. |
| Zero-score aggregation | Synthetic category scores **90, 0, 0** yield native overall **90** and separate summary average **30**. One zero is explicit evidence, one has no assigned unit. All-zero inputs yield overall 0. | Native overall omits both sorts of zero. Coverage, criterion scores and any separately computed aggregate need distinct reporting. These scores are test inputs, not human judgments. |
| Parsing | All three synthetic text cases return the exact first **30,720 UTF-16 code units**. An emoji case returns 61,440 UTF-8 bytes; a boundary case ends in a lone high surrogate. A synthetic PDF is rejected as unsupported. | The limit is neither bytes nor tokens. Native PDF support remains absent; reviewed extraction is required. Actual candidate text results are below. |
| Request configuration | Given temperature 0.17, synthetic seed 12345, maxTokens 321, JSON mode and disabled thinking, the constructed body contains `max_tokens:321`, `response_format`, `enable_thinking:false`, model and messages. It contains neither temperature nor seed. | Output-cap propagation works at request construction. Temperature omission persists; seed was an injected probe field, not evidence of a supported seed UI. The request was constructed only and never sent. |

| Input phase key | Loaded rubric stage | Prompt guidance |
| --- | --- | --- |
| `proposal` | `proposal_early_stage` | early |
| `mid` | `mid_project` | early |
| `end` | `end_project` | early |
| `proposal_early_stage` | `proposal_early_stage` | early |
| `mid_project` | `proposal_early_stage` | mid |
| `end_project` | `proposal_early_stage` | end |

## Native parser results for proposed documents

The same browser called `FileParser.parseFile` on all **24 hash-verified local TXT files**: twelve `pdftotext -layout` extractions and twelve default reading-order alternatives from [text-extraction.json](text-extraction.json). **All twelve layout extractions and eleven of twelve reading-order alternatives are truncated.** RECHARGE early, reading-order representation, is the sole full-length result. Each output equals the input's exact first 30,720 UTF-16 units, or the entire input if shorter. Thus the exposure is not explained solely by layout padding.

These are draft extractions, with full-document table and reading-order QA pending. Parser retention measures text units, including whitespace; it does not measure retained scientific meaning, completeness of the original DMP, or DMP quality. It must not drive quality-based candidate selection. No prompts or scores were generated from these candidate texts.

| Project / version | Layout input units | Layout retained | Reading-order input units | Reading-order retained |
| --- | ---: | ---: | ---: | ---: |
| iMagine / early | 126,953 | 24.2% | 86,961 | 35.3% |
| iMagine / late | 182,821 | 16.8% | 124,824 | 24.6% |
| EGI-ACE / early | 121,378 | 25.3% | 85,163 | 36.1% |
| EGI-ACE / late | 141,995 | 21.6% | 101,087 | 30.4% |
| NANOFACTS / early | 66,819 | 46.0% | 60,181 | 51.0% |
| NANOFACTS / late | 68,254 | 45.0% | 61,131 | 50.3% |
| AGRICORE / early | 44,956 | 68.3% | 34,365 | 89.4% |
| AGRICORE / late | 99,609 | 30.8% | 78,591 | 39.1% |
| SUSTRACK / early | 181,498 | 16.9% | 148,942 | 20.6% |
| SUSTRACK / late | 199,662 | 15.4% | 155,921 | 19.7% |
| RECHARGE / early | 35,617 | 86.3% | 27,503 | 100.0% (full) |
| RECHARGE / late | 48,235 | 63.7% | 39,439 | 77.9% |

A default full-document evaluation of these extractions would therefore require a declared input-handling condition. Keeping the native cap measures behavior on a prefix and cannot support full-document claims. A patch, chunking approach or different extraction is a separately documented condition; this check applied none of those changes to DMP-EVA.

## Reproduction and boundaries

Run from the repository root:

```bash
python3 research/paired-dmp-study/tool-preflight.py \
  --source-dir data/paired-dmp-corpus/upstream/dmp-eva-b80b43de820d46440d982eb99b2b3da8f4c2f818 \
  --text-manifest research/paired-dmp-study/text-extraction.json \
  --output /tmp/tool-preflight-new-run.json
```

Omit `--text-manifest` for the 20 synthetic assertions alone. The script requires Google Chrome and the exact pinned cached sources under `/tmp/dmp-eva-evolution/` (override with `--source-dir`). A durable local copy of the six tested files and upstream MIT licence is now preserved in the ignored corpus directory shown above; the original temporary cache is optional. It verifies hard-coded source hashes and candidate text hashes before execution. If the source cache is absent, download the immutable URLs listed in [tool-preflight.json](tool-preflight.json) into the indicated cache filenames; the script itself makes no downloads. `--output` can preserve a previous result when re-running. No Node or added Python dependency is required.

Network controls are a CSP denying connections/resources, throwing stubs for fetch/XHR/WebSocket/EventSource/sendBeacon/WebRTC, Chrome background-network flags, a proxy to loopback port 9 and external DNS rejection. **Zero network-stub invocations were recorded.** The page embeds source and test data; it uses a fresh temporary Chrome profile and deletes that profile afterwards. Chrome required execution outside the container sandbox after its socket setup was denied; those network controls remained in force. This is not a packet-capture audit.

The full app, provider compatibility, streaming/retry paths, DOC/DOCX/HTML dependencies, model behavior, native export UI and empirical agreement were outside this preflight. No dashboard selftest, legacy selection endpoint or benchmark was run. The source files were neither patched nor reimplemented. Earlier extended-harness attempts returned before asynchronous local reads completed; the final harness starts the candidate reads concurrently and completes all 44 assertions. This was a harness completion issue, not an observed DMP-EVA error.

The JSON stores exact synthetic inputs and function outputs, source URLs/hashes, browser/version, network controls, candidate input hashes, parser measurements and the SHA-256 of each expected parsed prefix (independently calculated by Python after browser equality verification). Its timestamp is the execution time; this check does not refresh the live upstream HEAD. [tool-evolution.md](tool-evolution.md) remains the latest-source discovery/provenance report. Human reference labels and the campaign's frozen input/prompt/phase/aggregation decisions remain separate work.
