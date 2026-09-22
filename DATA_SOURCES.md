# Real-data reference

Match Ready? V3 adds a real external match-demand reference derived from the
[SkillCorner Open Data](https://github.com/SkillCorner/opendata) project.

## Source

- Competition: Australian A-League
- Season: 2024/2025
- Source file: `aus1league_physicalaggregates_20242025.csv`
- Provider: SkillCorner
- License: MIT (see the upstream repository)
- Upstream data include season-level player-position physical aggregates.

SkillCorner states that its aggregate datasets are filtered to performances
above 60 minutes. For this project, the benchmark-building script additionally
keeps player-position samples with at least 5 matches and no failed physical
quality checks.

## Metrics used

The external reference uses:

- total distance
- high-speed-running distance
- sprint distance
- PSV-99 (99th-percentile peak sprint velocity proxy)

For male players, SkillCorner defines HSR as 20–25 km/h and sprinting as
above 25 km/h in its Physical Data Glossary.

## How Match Ready? uses the data

The real data do **not** replace the synthetic training dataset.

Instead:

```
synthetic training exposure
          ↓
individual training baseline
          ↓
real positional match-demand reference
          ↓
staff-facing interpretation
```

This keeps the portfolio scenario reproducible while replacing the previous
synthetic match-demand benchmark with a real external reference.

## Important limitation

The checked-in benchmark file contains distributions across season-level
player-position averages. It therefore captures between-player positional
variation, but not the full fixture-to-fixture distribution for an individual
player. Match-level variability from the 10 open tracking matches is a logical
next layer rather than something this file claims to contain.

## Rebuild

```bash
python src/skillcorner_reference.py
```

This downloads the upstream aggregate CSV and recreates
`data/real/skillcorner_position_benchmarks.csv`.
