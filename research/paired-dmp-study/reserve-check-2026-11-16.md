# Reserve check, 2026-11-16

Question: could three reserve projects from `lead-shortlist.md` replace AGRICORE (no reuse licence)
and EGI-ACE / NANOFACTS (secondary discipline)? Each reserve's PDFs were downloaded from Zenodo to
the git-ignored `data/paired-dmp-corpus/reserve-check/`, and the issue dates were read from the
documents by Claude. Not verified by a person.

**Result at that point: none of the three qualified under the then-approved rule (early ≤ 50%, late
> 100% by issue date).** Later the same day the user changed the late rule (D23) and three pairs
were swapped (D24); see the follow-up section at the end, which supersedes the "Consequences" below.

| Reserve | Would replace | Early document | Late document | Verdict |
|---|---|---|---|---|
| TWEET-IE (101079125), engineering only | EGI-ACE | D6.3 v2.0, dated 2023-10-31 (33%), record 10061049: passes | D6.4 final, dated 2025-10-31 in cover and change history, record 17361082. The project ends 2025-10-31, so this is exactly 100%, not after the end. Deposited 2025-12-31. | **Fails late** by the strict rule. Would pass only if "late" meant ≥ 100%. Licence on Zenodo: `apl1.0` (unusual). |
| D1-Glia (101090280), medical only | NANOFACTS | v1 2023-06-29 and v2 2024-03-19 exist, but their Zenodo records (10844552, 11091859) are access-restricted | v3 issued 2025-03-09, record 15392557. The project ends 2025-03-31, so about 97%. | **Fails late**, and the early file is not openly downloadable. |
| PAPILLONS (101000210), agricultural + natural | AGRICORE | Earliest version on Zenodo is D5.4 v1, delivered 2024-06-21 (due 2024-05-31), record 17640869: about 76% | Record 17245511, dated 2025-10-01 (108%): passes | **Fails early.** No earlier DMP on Zenodo. CC BY 4.0. |

Consequences:
- AGRICORE remains the only checked option for agricultural sciences; its licence question stays open.
- The secondary-discipline limitation for EGI-ACE and NANOFACTS stays.
- TWEET-IE is the nearest miss. If the group relaxed "late" to "at or after the project end", it
  would qualify and give a single-discipline engineering pair. That is a protocol change (D01), not
  something to apply silently.
- Tier B and D leads not checked here: PathOS, IANUS, MarinePlan, EUbOPEN, RitualModes, ADOPT
  BBMRI-ERIC, COMETE, GOLDEN-ROM, FAIRsFAIR.

## Follow-up the same day: wider search, rule change and swaps

The user asked to replace the weak pairs. A wider search (every project with 2+ DMP documents and a
post-end deposit, combining dataset rows and cached version chains, plus a Zenodo title search for
BY-COVID) gave eleven more candidates. Issue dates read from the PDFs:

| Project | Discipline(s) | Early | Final | Outcome |
|---|---|---|---|---|
| ColdSpark (101069931) | engineering only | 2022-11-30, 14.2% | 2025-11-29, 99.9% | **chosen for engineering** under D23 |
| EM-TECH (101096083) | engineering only | 2023-06-30, 16.4% | 2025-12-19, 98.9% | qualifies under D23; reserve |
| ERIES (101058684) | engineering + natural | 2022-12-20, 13.8% | 2026-07-13, 102.9% | qualifies even under the strict rule; Argos exports; reserve |
| CURE (870337) | engineering + natural | 2020-03-31, 7.4% | 2023-04-19, 98.9% | qualifies under D23; reserve |
| PIXEL (769355) | engineering + natural | v2 2019-10-30, 44% | 2021-09-30, 100.0% | qualifies under D23; reserve |
| MultiMiner (101091374) | engineering + natural | 2023-05-31, 11.8% | 2026-06-30 / 2026-09-11 | unclear version dating; not used |
| SteamBioAfrica (101036401) | engineering + social | | | access-restricted files |
| BY-COVID (101046203) | medical only | 2022-03-30, 16.4% | 2024-07-31, 94.4% | **chosen for medical** under D23 |
| ASTEP (884411) | agricultural + engineering | 2020-10-31, 9.7% | 2025-07-24, 101.3% (last revision 2025-06-26, 99.8%) | **chosen for agricultural** |
| VIRTIGATION (101000570) | agricultural + natural | | | only 2-page public summaries |
| REFOREST (101060635) | agricultural + social | | "update" dated 2024-06-13, mid-project | no final DMP; CC BY-NC |
| EURAKNOS (817863) | agricultural only | | | access-restricted files |
| DIANA (730109) | engineering first, agricultural secondary | M3 2017 | M36 = Dec 2019 | old (2017-2019); not used |

Decisions D23 (late = final DMP at 90% or later) and D24 (the three swaps) followed. Humanities has no
better candidate than RECHARGE. Downloads are in the git-ignored
`data/paired-dmp-corpus/reserve-check/`.
