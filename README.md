# Match Ready?

**Sprint Exposure & Physical Readiness in Football**

Match Ready? is a portfolio project that simulates a football performance-monitoring workflow around a practical staff question:

> Is the player's recent training exposure consistent with the physical demands we expect from them?

The project combines synthetic training/load data, individual baselines, transparent monitoring rules, interactive visualisation and a staff-oriented Streamlit interface. The match-demand context is now grounded in real SkillCorner Open Data from the Australian A-League 2024/25.

![Featured cover](assets/exports/05_featured_cover.png)

## Live demo

**Interactive dashboard:** https://match-ready-football.streamlit.app/

Recommended first view:
- **Monitoring week:** Week 5
- **Player:** Player 18 · Winger

This view highlights the main project storyline: overall training volume remains present while sprint-specific exposure is substantially reduced.


## Why this project

Football performance data is easy to turn into dashboards and much harder to turn into interpretable decisions. Match Ready? was designed around three questions:

- **Who needs attention?**
- **Why have they been flagged?**
- **Is the flag unexpected, or explained by the training plan?**

The app therefore avoids an artificial "injury probability" and focuses on exposure, preparation and context.

## Data design

Training and wellness data are synthetic so the workflow remains reproducible and does not pretend to contain private club GPS data.

The external match-demand reference is real and is derived from SkillCorner Open Data.

- 24 outfield players
- 5 position groups: CB, FB, CM, W, ST
- 8 weekly microcycles
- Weeks 1–3: individual baseline acquisition
- Weeks 4–8: monitoring period
- Daily training / match observations
- Total distance, HSR, sprint distance, accelerations, decelerations, peak speed, session RPE, load and wellness

Goalkeepers are intentionally excluded because their physical demands require a different framework.

### Real match-demand reference

The project uses season-level SkillCorner physical aggregates for the Australian A-League 2024/25. For each position group, Match Ready? stores P25, P50, P75 and P90 for total distance, HSR, sprint distance and PSV-99.

This portfolio processing step keeps player-position samples with at least five matches and no failed physical quality checks.

See [DATA_SOURCES.md](DATA_SOURCES.md) for provenance, processing choices and limitations.

## Designed scenarios

Three specific storylines make the dataset useful to explore.

### P18 — Winger: unexpected speed underexposure

Training volume remains broadly present, while sprint distance and near-max-speed exposure fall substantially.

![Player exposure profile](assets/exports/02_player_exposure_profile.png)

### P07 — Full Back: accumulated-load context

Week 7 contains a deliberate load increase without the same speed-underexposure pattern.

### P22 — Striker: planned reintegration

Reduced exposure in weeks 4–5 is intentional within a return-to-performance scenario. The numerical flag remains visible, but the interface explicitly shows that the reduction is planned.

This is an important design principle of the project: **monitoring data should support staff judgement, not replace it.**

## Monitoring logic

Current preparation is primarily compared with the player's own baseline.

The monitoring interface uses:

- sprint exposure vs individual baseline
- HSR exposure vs individual baseline
- peak speed as % individual Vmax
- recency of >90% and >95% Vmax exposure
- overall training load vs individual baseline
- wellness context
- pre-match training exposure vs real positional match-demand distributions

### Preparation Alignment

A custom 0–100 visual index combines:

- 50% sprint alignment
- 25% HSR alignment
- 25% peak-speed exposure

The index is an interface aid for this synthetic portfolio project. It is **not** a validated injury-risk score or a medical metric.

## Real match-demand lens

The Player Analysis workspace compares the synthetic pre-match training week with real positional distributions from SkillCorner Open Data.

The dashboard shows the positional P25–P90 range and the P50 reference for HSR and sprint distance. These are contextual benchmarks, not prescribed training targets. A full training week and a single match are different exposure windows; the comparison is used to inspect the stimulus mix across dimensions.

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
│   ├── processed/
│   └── real/
├── src/
│   ├── data_generation.py
│   ├── metrics.py
│   ├── skillcorner_reference.py
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

Training and wellness data are synthetic; the external match-demand reference is real SkillCorner Open Data. The current real-data layer uses season-level player-position aggregates, so it captures positional variation across players but not the complete fixture-to-fixture distribution of one player.

Monitoring thresholds are transparent portfolio heuristics created to demonstrate a workflow and interface. The project does not provide medical diagnosis, injury prediction or return-to-play clearance.
