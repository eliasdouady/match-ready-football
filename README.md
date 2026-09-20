# Match Ready?

**Sprint Exposure & Physical Readiness in Football**

Match Ready? is a portfolio project that simulates a football performance-monitoring workflow around a practical staff question:

> Is the player's recent training exposure consistent with the physical demands we expect from them?

The project combines synthetic GPS/load data, individual baselines, transparent monitoring rules, interactive visualisation and a staff-oriented Streamlit interface.

![Featured cover](assets/exports/05_featured_cover.png)

## Why this project

Football performance data is easy to turn into dashboards and much harder to turn into interpretable decisions. Match Ready? was designed around three questions:

- **Who needs attention?**
- **Why have they been flagged?**
- **Is the flag unexpected, or explained by the training plan?**

The app therefore avoids an artificial "injury probability" and focuses on exposure, preparation and context.

## Dataset

The dataset is fully synthetic and designed to reproduce plausible performance-monitoring situations.

- 24 outfield players
- 5 position groups: CB, FB, CM, W, ST
- 8 weekly microcycles
- Weeks 1–3: individual baseline acquisition
- Weeks 4–8: monitoring period
- Daily training / match observations
- Total distance, HSR, sprint distance, accelerations, decelerations, peak speed, session RPE, load and wellness

Goalkeepers are intentionally excluded because their physical demands require a different framework.

## Designed scenarios

### P18 — Winger: unexpected speed underexposure

Training volume remains broadly present, while sprint distance and near-max-speed exposure fall substantially.

![Player exposure profile](assets/exports/02_player_exposure_profile.png)

### P07 — Full Back: accumulated-load context

Week 7 contains a deliberate load increase without the same speed-underexposure pattern.

### P22 — Striker: planned reintegration

Reduced exposure in weeks 4–5 is intentional within a return-to-performance scenario. The numerical flag remains visible, but the interface explicitly shows that the reduction is planned.

**Monitoring data should support staff judgement, not replace it.**

## Monitoring logic

Current preparation is primarily compared with the player's own baseline.

The monitoring interface uses:

- sprint exposure vs individual baseline
- HSR exposure vs individual baseline
- peak speed as % individual Vmax
- recency of >90% and >95% Vmax exposure
- overall training load vs individual baseline
- wellness context
- pre-match training exposure vs individual match demand

### Preparation Alignment

A custom 0–100 visual index combines:

- 50% sprint alignment
- 25% HSR alignment
- 25% peak-speed exposure

The index is an interface aid for this synthetic portfolio project. It is **not** a validated injury-risk score or a medical metric.

## Training-to-match lens

The app also expresses the pre-match training week relative to each player's synthetic typical one-match demand.

![Training to match demand](assets/exports/06_training_to_match_demand.png)

These ratios are descriptive comparisons. `1.00x` means that the total pre-match training-week exposure equals the player's synthetic typical 90-minute match demand; it is not presented as a prescribed target.

## Dashboard

The Streamlit app contains four workspaces:

1. **Squad Overview** — status distribution, priority queue and squad monitoring board
2. **Player Analysis** — player card, exposure profile, match-demand lens, microcycle and wellness/load context
3. **Exposure Map** — interactive squad-level sprint/HSR positioning
4. **Methodology** — assumptions, monitoring rules and designed scenarios

## Project structure

```text
match-ready-football/
├── assets/
│   └── exports/
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── data_generation.py
│   ├── metrics.py
│   └── visuals.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
└── README.md
```

## Run locally

```bash
pip install -r requirements.txt
python src/data_generation.py
python src/metrics.py
python src/visuals.py
streamlit run dashboard/app.py
```

If the data and visuals are already present, only the last command is required.

## Tech stack

- Python
- pandas
- NumPy
- Plotly
- Matplotlib
- Streamlit

## Important limitation

All player data is synthetic. Monitoring thresholds are transparent portfolio heuristics created to demonstrate a workflow and interface. The project does not provide medical diagnosis, injury prediction or return-to-play clearance.
