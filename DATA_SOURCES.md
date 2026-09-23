# Real match-demand data

Match Ready? uses a real external reference from the
[SkillCorner Open Data](https://github.com/SkillCorner/opendata) repository.

## Source

- Competition: Australian A-League
- Season: 2024/2025
- Provider: SkillCorner
- Season aggregate: `data/aggregates/aus1league_physicalaggregates_20242025.csv`
- Match variability: 10-match open broadcast-tracking sample at 10 Hz

SkillCorner describes the aggregate files as season-level player aggregates and
states that aggregate datasets are filtered to performances above 60 minutes.
The tracking layer is processed separately into player-match physical metrics.

## Match Ready? processing

The portfolio benchmark keeps player-position samples with:

- at least 5 matches
- no failed physical quality checks

For each position group, the project stores P25, P50, P75 and P90 for:

- total distance
- high-speed-running distance
- sprint distance
- PSV-99

The position mapping is:

- Central Defender → CB
- Full Back → FB
- Midfield → CM
- Wide Attacker → W
- Center Forward → ST

## Important distinction

The training and wellness environment in Match Ready? remains synthetic so the
project is reproducible and does not pretend to contain private club GPS data.

The external match-demand reference is real.

The positional distributions are contextual references, not training targets,
medical thresholds or injury-risk estimates.

The season-level aggregate layer captures broad between-player positional
variation. A second layer now derives HSR and sprint distributions directly
from the 10-match open tracking sample, including repeated-player examples when
the same player has multiple eligible performances.

That tracking sample demonstrates match-to-match variability, but it is still a
small sample and should not be interpreted as the full A-League distribution.
See `MATCH_VARIABILITY.md` for the speed thresholds, smoothing, eligibility and
normalisation choices used to create the derived match tables.
