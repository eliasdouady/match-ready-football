# Match-to-match tracking variability

This layer is derived from the open SkillCorner broadcast-tracking sample.

## Why it exists

The season-level SkillCorner aggregate file is useful for a stable positional reference,
but a season average hides how much physical demand changes from one match to another.

The tracking layer therefore creates one observation per eligible player-match and then
summarises the distribution by position.

## Processing choices

- source: SkillCorner Open Data broadcast tracking, sampled at 10 Hz
- outfield position groups only: CB, FB, CM, W, ST
- player must have played at least 60 minutes
- speed is estimated from an approximately 1-second displacement window to reduce
  frame-to-frame tracking noise
- obvious speed jumps above 41.4 km/h are discarded
- HSR: 20 to <25 km/h
- sprint: >=25 km/h
- HSR and sprint are normalised to metres per 90 minutes
- speed P99 is reported as a robust peak-speed descriptor

## Important limitation

These values are **derived in this portfolio from SkillCorner tracking coordinates**.
They are not the same as SkillCorner's proprietary physical-metrics pipeline and should
not be presented as official SkillCorner physical outputs.

The sample is also much smaller than the full-season aggregate dataset. Its purpose is
to make match-to-match variability visible, not to replace the season-level reference.

For players appearing in at least two open matches, the project also calculates a
within-player coefficient of variation (CV) for HSR and sprint. This provides a direct
measure of how much the same player's physical output varies across matches in the open sample.
