# Real match-demand data

Match Ready? uses a real external reference from the
[SkillCorner Open Data](https://github.com/SkillCorner/opendata) repository.

## Source

- Competition: Australian A-League
- Season: 2024/2025
- Provider: SkillCorner
- Upstream file: `data/aggregates/aus1league_physicalaggregates_20242025.csv`

SkillCorner describes these files as season-level player aggregates and states
that aggregate datasets are filtered to performances above 60 minutes.

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

Because these are season-level player-position aggregates, they capture
between-player positional variation but not the complete fixture-to-fixture
distribution of a single player. The open tracking matches are the next layer
for future work.
