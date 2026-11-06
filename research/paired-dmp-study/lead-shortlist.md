# Reserve shortlist from Zenodo version chains

Generated 2026-11-06 by `lead-triage.py`. **A screen, not a selection.** No issue date, scope or lineage has been read, nothing is registered in the dashboard, and the six proposal pairs are unaffected.

## Method

`scripts/06_discover_versions.py versions` fetched the Zenodo version chain of every plan with a grant number (1,503 records, 0 failures). 226 concepts have earlier versions missing from the saved harvest. Of these, 99 belong to projects without a CORDIS discipline or project dates (D08 needs one) and 109 have no version deposited after the project end. A document deposited before the end cannot have been issued after it, so those can never supply a late document. **18 concepts remain**:

| tier | meaning | concepts |
|---|---|---|
| A | early by deposit date; late issue date must be checked | 6 |
| B | deposit between 50% and 100%, plus a post-end deposit; both issue dates must be checked | 6 |
| D | only post-end deposits; both issue dates must be checked | 6 |

Publication positions use the local CORDIS dates (extensions not checked, D09). Same concept means the depositor uploaded it as a new version of the same Zenodo record, which is a stronger lineage lead than a shared grant. It still needs a person to confirm that the later document revises the earlier one and has the same scope.

## Reserve coverage by discipline (projects outside the proposal)

- **natural sciences**: e-DIPLOMA, MultiMiner, ExPaNDS, PathOS, MarinePlan, EUbOPEN, PAPILLONS, RitualModes, ADOPT BBMRI-ERIC, COMETE, GOLDEN-ROM
- **engineering and technology**: MultiMiner, TWEET-IE, SteamBioAfrica
- **medical and health sciences**: D1-Glia, EUbOPEN, ADOPT BBMRI-ERIC
- **agricultural sciences**: PAPILLONS
- **social sciences**: e-DIPLOMA, SteamBioAfrica, ExPaNDS, IANUS, MarinePlan, RitualModes, ADOPT BBMRI-ERIC, FAIRsFAIR
- **humanities**: RitualModes, GOLDEN-ROM

## Shortlist

### Tier A · e-DIPLOMA (grant 101061424, Horizon Europe)

CORDIS branches: natural sciences, social sciences (dominant: natural sciences). Project 2022-09-01 → 2025-10-31 (local CORDIS). Zenodo concept 10390669.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [10390670](https://zenodo.org/records/10390670) | 2023-11-27 | 39.10% | early-by-deposit | no | e-DIPLOMA - Deliverable 1.3: Data Management Plan |
| [21102983](https://zenodo.org/records/21102983) | 2026-03-26 | 112.63% | post-end | yes | e-DIPLOMA - Deliverable 1.3: Data Management Plan v2 |

### Tier A · MultiMiner (grant 101091374, Horizon Europe)

CORDIS branches: engineering and technology, natural sciences (dominant: engineering and technology). Project 2023-01-01 → 2026-06-30 (local CORDIS). Zenodo concept 8063405.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [8063406](https://zenodo.org/records/8063406) | 2023-06-21 | 13.40% | early-by-deposit | no | MultiMiner Project Deliverable No 5.4 - Data Management Plan V1.3 |
| [10653171](https://zenodo.org/records/10653171) | 2024-02-13 | 31.97% | early-by-deposit | no | MultiMiner Project Deliverable No 5.4 - Data Management Plan V1.4 |
| [14016960](https://zenodo.org/records/14016960) | 2024-10-31 | 52.43% | mid | no | MultiMiner Project Deliverable No 5.4 - Data Management Plan V1.5 |
| [14878400](https://zenodo.org/records/14878400) | 2025-02-16 | 60.89% | mid | no | MultiMiner Project Deliverable No 5.4 - Data Management Plan V1.6 |
| [17052131](https://zenodo.org/records/17052131) | 2025-09-04 | 76.57% | mid | no | MultiMiner Project Deliverable No 5.4 - Data Management Plan V1.7 |
| [20429095](https://zenodo.org/records/20429095) | 2026-05-28 | 97.41% | mid | yes | MultiMiner Project Deliverable No 5.4 - Data Management Plan V1.8 |
| [22706196](https://zenodo.org/records/22706196) | 2026-09-11 | 105.72% | post-end | no | MultiMiner Project Deliverable No 5.4 - Data Management Plan V1.9 |

### Tier A · TWEET-IE (grant 101079125, Horizon Europe)

CORDIS branches: engineering and technology (dominant: engineering and technology). Project 2022-11-01 → 2025-10-31 (local CORDIS). Zenodo concept 10061048.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [10061049](https://zenodo.org/records/10061049) | 2023-11-01 | 33.33% | early-by-deposit | no | TWEET-IE Deliverable 6.3: Data Management Plan |
| [14022681](https://zenodo.org/records/14022681) | 2024-03-31 | 47.12% | early-by-deposit | no | TWEET-IE Deliverable 6.3: Data Management Plan |
| [14023125](https://zenodo.org/records/14023125) | 2024-06-20 | 54.52% | mid | no | TWEET-IE Deliverable 6.3: Data Management Plan |
| [14024376](https://zenodo.org/records/14024376) | 2024-11-01 | 66.76% | mid | no | TWEET-IE Deliverable 6.3: Data Management Plan |
| [17361082](https://zenodo.org/records/17361082) | 2025-12-31 | 105.57% | post-end | yes | TWEET-IE Deliverable 6.4: Data Management Plan - Final assessment |

### Tier A · D1-Glia (grant 101090280, Horizon Europe)

CORDIS branches: medical and health sciences (dominant: medical and health sciences). Project 2023-04-01 → 2025-03-31 (local CORDIS). Zenodo concept 10844551.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [11091859](https://zenodo.org/records/11091859) | 2024-03-19 | 48.36% | early-by-deposit | no | Data Management Plan |
| [10844552](https://zenodo.org/records/10844552) | 2024-03-20 | 48.49% | early-by-deposit | no | Data Management Plan |
| [15392557](https://zenodo.org/records/15392557) | 2025-05-12 | 105.75% | post-end | yes | Data Management Plan |

### Tier A · SteamBioAfrica (grant 101036401, Horizon 2020)

CORDIS branches: engineering and technology, social sciences (dominant: engineering and technology). Project 2021-09-01 → 2024-08-31 (local CORDIS). Zenodo concept 13871825.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [13871826](https://zenodo.org/records/13871826) | 2022-03-31 | 19.27% | early-by-deposit | no | D12.1 Data Management Plan |
| [13879550](https://zenodo.org/records/13879550) | 2022-06-06 | 25.39% | early-by-deposit | no | D12.1 Data Management Plan |
| [13879557](https://zenodo.org/records/13879557) | 2023-04-17 | 54.16% | mid | no | D12.1 Data Management Plan |
| [13879565](https://zenodo.org/records/13879565) | 2024-09-17 | 101.55% | post-end | yes | D12.1 Data Management Plan |

### Tier A · ExPaNDS (grant 857641, Horizon 2020)

CORDIS branches: natural sciences, social sciences (dominant: natural sciences). Project 2019-09-01 → 2023-02-28 (local CORDIS). Zenodo concept 3672925.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [3672926](https://zenodo.org/records/3672926) | 2020-02-14 | 13.01% | early-by-deposit | no | D1.10 ExPaNDS Data Management Plan |
| [7646655](https://zenodo.org/records/7646655) | 2023-03-15 | 101.18% | post-end | yes | ExPaNDS Data Management Plan |

### Tier B · PathOS (grant 101058728, Horizon Europe)

CORDIS branches: natural sciences (dominant: natural sciences). Project 2022-09-01 → 2025-08-31 (local CORDIS). Zenodo concept 11049556.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [11049557](https://zenodo.org/records/11049557) | 2024-04-11 | 53.70% | mid | no | PathOS - D3.5 Data Management Plan |
| [17578116](https://zenodo.org/records/17578116) | 2025-11-10 | 106.48% | post-end | yes | PathOS - D3.5 Data Management Plan (update) |

### Tier B · IANUS (grant 101058158, Horizon Europe)

CORDIS branches: social sciences (dominant: social sciences). Project 2022-06-01 → 2025-05-31 (local CORDIS). Zenodo concept 15527690.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [15527691](https://zenodo.org/records/15527691) | 2025-05-27 | 99.63% | mid | no | IANUS - Data Management Plan (M6) |
| [15527866](https://zenodo.org/records/15527866) | 2025-05-27 | 99.63% | mid | no | IANUS - Data Management Plan (mid-term update) |
| [17779555](https://zenodo.org/records/17779555) | 2025-12-01 | 116.80% | post-end | yes | IANUS - Data Management Plan (final update) |

### Tier B · MarinePlan (grant 101059407, Horizon Europe)

CORDIS branches: natural sciences, social sciences (dominant: natural sciences). Project 2022-10-01 → 2025-09-30 (local CORDIS). Zenodo concept 15785969.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [15785970](https://zenodo.org/records/15785970) | 2025-07-01 | 91.69% | mid | no | D6.5 - Final Data Management Plan |
| [17132524](https://zenodo.org/records/17132524) | 2025-09-16 | 98.72% | mid | no | D6.5 - Final Data Management Plan |
| [17641382](https://zenodo.org/records/17641382) | 2025-09-19 | 99.00% | mid | yes | D6.5 - Final Data Management Plan |
| [17132397](https://zenodo.org/records/17132397) | 2025-11-16 | 104.29% | post-end | no | D6.5 - Final Data Management Plan |

### Tier B · EUbOPEN (grant 875510, Horizon 2020)

CORDIS branches: natural sciences, medical and health sciences (dominant: natural sciences). Project 2020-05-01 → 2025-10-31 (local CORDIS). Zenodo concept 8278990.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [8278991](https://zenodo.org/records/8278991) | 2023-04-30 | 54.45% | mid | no | EUbOPEN Data Management Plan |
| [21646962](https://zenodo.org/records/21646962) | 2026-07-28 | 113.44% | post-end | yes | EUbOPEN Data Management Plan |

### Tier B · PAPILLONS (grant 101000210, Horizon 2020)

CORDIS branches: natural sciences, agricultural sciences (dominant: natural sciences). Project 2021-06-01 → 2025-05-31 (local CORDIS). Zenodo concept 17245510.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [17640869](https://zenodo.org/records/17640869) | 2024-06-21 | 76.44% | mid | yes | PAPILLONS Data Management Plan |
| [17245511](https://zenodo.org/records/17245511) | 2025-10-01 | 108.42% | post-end | no | PAPILLONS Data Management Plan |

### Tier B · EGI-ACE (grant 101017567, Horizon 2020) — already the proposal's engineering and technology pair

CORDIS branches: natural sciences, engineering and technology (dominant: natural sciences). Project 2021-01-01 → 2023-06-30 (local CORDIS). Zenodo concept 7262255.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [7262256](https://zenodo.org/records/7262256) | 2022-10-26 | 72.86% | mid | no | EGI-ACE D1.5 Data Management Plan |
| [10149915](https://zenodo.org/records/10149915) | 2023-11-17 | 115.38% | post-end | no | EGI-ACE D1.5 Data Management Plan |
| [19402005](https://zenodo.org/records/19402005) | 2023-11-17 | 115.38% | post-end | yes | EGI-ACE D1.5 Data Management Plan |

### Tier D · RECHARGE (grant 101061233, Horizon Europe) — already the proposal's humanities pair

CORDIS branches: medical and health sciences, humanities (dominant: medical and health sciences). Project 2022-10-01 → 2025-09-30 (local CORDIS). Zenodo concept 17733865.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [17733866](https://zenodo.org/records/17733866) | 2025-11-27 | 105.30% | post-end | no | RECHARGE: Data Management Plan |
| [17801415](https://zenodo.org/records/17801415) | 2025-12-03 | 105.84% | post-end | no | RECHARGE: Data Management Plan (mid-term update) |
| [18403735](https://zenodo.org/records/18403735) | 2026-01-28 | 110.96% | post-end | yes | RECHARGE: Data Management Plan (final update) |

### Tier D · RitualModes (grant 694986, Horizon 2020)

CORDIS branches: natural sciences, humanities, social sciences (dominant: natural sciences). Project 2016-10-01 → 2023-09-30 (local CORDIS). Zenodo concept 8403008.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [8403009](https://zenodo.org/records/8403009) | 2023-10-03 | 100.12% | post-end | no | Data, code and documentation for the paper The Tragedies that Bind Us: Shared memories, id |
| [17585539](https://zenodo.org/records/17585539) | 2025-03-30 | 121.41% | post-end | yes | Data, code and documentation for the paper The Tragedies that Bind Us: Shared memories, id |

### Tier D · ADOPT BBMRI-ERIC (grant 676550, Horizon 2020)

CORDIS branches: medical and health sciences, social sciences, natural sciences (dominant: medical and health sciences). Project 2015-10-01 → 2019-03-31 (local CORDIS). Zenodo concept 7513755.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [7513756](https://zenodo.org/records/7513756) | 2023-01-08 | 207.99% | post-end | no | BBMRI-ERIC Colorectal Cancer Cohort (CRC-Cohort): Data Protection Policy |
| [7930536](https://zenodo.org/records/7930536) | 2023-05-12 | 217.70% | post-end | yes | BBMRI-ERIC Colorectal Cancer Cohort (CRC-Cohort): Data Protection Policy |

### Tier D · COMETE (grant 813948, Horizon 2020)

CORDIS branches: natural sciences (dominant: natural sciences). Project 2018-11-01 → 2023-04-30 (local CORDIS). Zenodo concept 8063546.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [8063547](https://zenodo.org/records/8063547) | 2023-06-21 | 103.17% | post-end | no | Next-Generation Computational Methods for Enhanced Multiphase Flow Processes - WP2 |
| [8378578](https://zenodo.org/records/8378578) | 2023-06-21 | 103.17% | post-end | yes | Next-Generation Computational Methods for Enhanced Multiphase Flow Processes - WP2 |

### Tier D · GOLDEN-ROM (grant 101029346, Horizon 2020)

CORDIS branches: humanities, natural sciences (dominant: humanities). Project 2021-06-01 → 2023-05-31 (local CORDIS). Zenodo concept 8242973.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [8242974](https://zenodo.org/records/8242974) | 2023-08-13 | 110.15% | post-end | no | Data Management Plan |
| [8242975](https://zenodo.org/records/8242975) | 2023-08-13 | 110.15% | post-end | yes | Data Management Plan |

### Tier D · FAIRsFAIR (grant 831558, Horizon 2020)

CORDIS branches: social sciences (dominant: social sciences). Project 2019-03-01 → 2022-02-28 (local CORDIS). Zenodo concept 6334610.

| record | published | position | screen | in dataset | title |
|---|---|---|---|---|---|
| [6334611](https://zenodo.org/records/6334611) | 2022-03-07 | 100.64% | post-end | no | D1.2 Data Management Plan |
| [6656144](https://zenodo.org/records/6656144) | 2022-03-07 | 100.64% | post-end | yes | D1.2 Data Management Plan |

## To turn a lead into a candidate

Read both issue dates. Register a missing version with `python scripts/06_discover_versions.py register --doc-id zenodo:<id> --record-id <id> ...` so it appears in the dashboard, then assign it and record the evidence there. Registering is a selection decision and has not been done for any lead.
