# Match-to-match variability layer

This layer uses the **10-match broadcast-tracking sample** from SkillCorner Open Data
to move beyond a single season-level positional benchmark.

## Why this exists

A positional median is useful, but it can hide the fact that the same role can face
very different physical demands from one fixture to another.

The project therefore derives one physical profile per eligible player-match and
summarises the spread of match demands by position.

## Source

- SkillCorner Open Data
- Australian A-League 2024/25
- 10 broadcast-tracking matches from the reproducible original open-data sample
- 10 Hz tracking
- male outfield players only

Match IDs:

`1886347, 1899585, 1925299, 1953632, 1996435, 2006229, 2011166, 2013725, 2015213, 2017461`

## Eligibility

- outfield position group: Central Defender, Full Back, Midfield, Wide Attacker, Center Forward
- at least 60 minutes played in the match

## Processing choices

The raw tracking is converted into a speed signal using:

- no differentiation across period boundaries
- no bridging of tracking gaps greater than 0.5 s
- rejection of implausible samples above 40 km/h
- trailing 1-second mean of speed at 10 Hz
- HSR: 20–25 km/h
- Sprint: >=25 km/h

Volume metrics are additionally normalised to 90 minutes to reduce substitution-time
effects when comparing match performances.

The derived `speed_p99_kmh` field is a frame-level 99th percentile of the smoothed
speed signal. It is intentionally **not** labelled SkillCorner PSV-99 because the
provider's published PSV-99 definition is activity-based.

## Outputs

### `skillcorner_player_match_metrics.csv`

One row per eligible real player-match:

- total distance
- HSR distance
- sprint distance
- 90-minute-normalised versions
- speed P99
- player, team, opponent, role and minutes

### `skillcorner_match_variability.csv`

Position-level P10/P25/P50/P75/P90 distributions across real match performances.

### `skillcorner_repeated_player_variability.csv`

Within-player variability for real players appearing in at least two eligible matches
in the sample.

## Interpretation

These data are used as **external context**, not as prescribed training targets.

The main question is no longer only:

> What does a typical winger match look like?

It becomes:

> How much can winger match demands vary across fixtures, and is the player's recent
> preparation exposing them to that range of demands?

This remains a portfolio analysis and does not make injury-risk or medical claims.
