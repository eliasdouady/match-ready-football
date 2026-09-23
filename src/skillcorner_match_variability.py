from __future__ import annotations

import json
import math
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


# Reproducible 10-match sample used in the original SkillCorner Open Data release.
# These IDs match the open-data tracking sample documented by SkillCorner.
MATCH_IDS = [
    1886347,
    1899585,
    1925299,
    1953632,
    1996435,
    2006229,
    2011166,
    2013725,
    2015213,
    2017461,
]

RAW_BASE = "https://raw.githubusercontent.com/SkillCorner/opendata/master/data/matches"
LFS_BASE = "https://media.githubusercontent.com/media/SkillCorner/opendata/master/data/matches"

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "real"

FPS = 10.0
MAX_GAP_SECONDS = 0.5
MAX_SPEED_KMH = 40.0
HSR_MIN_KMH = 20.0
SPRINT_MIN_KMH = 25.0
MIN_PLAYED_MINUTES = 60.0
ROLLING_WINDOW_SAMPLES = 10  # trailing 1-second mean at 10 Hz

POSITION_MAP = {
    "Central Defender": "CB",
    "Full Back": "FB",
    "Midfield": "CM",
    "Wide Attacker": "W",
    "Center Forward": "ST",
}

VALID_GROUPS = set(POSITION_MAP)


def _url_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "match-ready-football/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)


def _player_registry(meta: dict) -> tuple[dict[str, dict], dict[str, dict]]:
    """
    Return:
      registry: canonical player_id -> player metadata
      raw_id_map: any provider player identifier -> canonical player_id

    SkillCorner match metadata exposes several identifiers. Mapping all of them
    makes the parser robust to whichever identifier the tracking JSONL uses.
    """
    registry: dict[str, dict] = {}
    raw_id_map: dict[str, dict] = {}

    for player in meta.get("players", []):
        playing = ((player.get("playing_time") or {}).get("total") or {})
        minutes = playing.get("minutes_played")
        role = player.get("player_role") or {}
        group = role.get("position_group")

        if minutes is None or float(minutes) < MIN_PLAYED_MINUTES:
            continue
        if group not in VALID_GROUPS:
            continue

        canonical_id = str(player.get("id"))
        team_id = player.get("team_id")
        team_name = None
        if team_id == (meta.get("home_team") or {}).get("id"):
            team_name = (meta.get("home_team") or {}).get("short_name")
        elif team_id == (meta.get("away_team") or {}).get("id"):
            team_name = (meta.get("away_team") or {}).get("short_name")

        rec = {
            "player_id": canonical_id,
            "player_name": player.get("short_name") or (
                f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
            ),
            "team_id": team_id,
            "team_name": team_name,
            "position_group": group,
            "position": POSITION_MAP[group],
            "role": role.get("name"),
            "minutes_played": float(minutes),
            "start_frame": playing.get("start_frame"),
            "end_frame": playing.get("end_frame"),
        }
        registry[canonical_id] = rec

        for candidate in (
            player.get("id"),
            player.get("trackable_object"),
            player.get("team_player_id"),
        ):
            if candidate is not None:
                raw_id_map[str(candidate)] = rec

    return registry, raw_id_map


def _valid_xy(x: object, y: object, pitch_length: float, pitch_width: float) -> bool:
    try:
        x = float(x)
        y = float(y)
    except (TypeError, ValueError):
        return False
    if not (math.isfinite(x) and math.isfinite(y)):
        return False

    # Extrapolated broadcast tracking can occasionally park an undetected player
    # well outside the pitch. Keep a small tolerance but reject impossible points.
    return (
        abs(x) <= pitch_length / 2 + 5.0
        and abs(y) <= pitch_width / 2 + 5.0
    )


def _segment_metrics(frame: np.ndarray, x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Compute robust physical volumes from one continuous period/segment."""
    if len(frame) < 4:
        return {
            "total_distance_m": 0.0,
            "hsr_distance_m": 0.0,
            "sprint_distance_m": 0.0,
            "speed_samples_kmh": np.array([], dtype=float),
        }

    dt = np.diff(frame) / FPS
    dx = np.diff(x)
    dy = np.diff(y)
    step = np.hypot(dx, dy)

    raw_speed_mps = np.divide(
        step,
        dt,
        out=np.full_like(step, np.nan, dtype=float),
        where=(dt > 0),
    )
    raw_speed_kmh = raw_speed_mps * 3.6

    valid = (
        (dt > 0)
        & (dt <= MAX_GAP_SECONDS)
        & np.isfinite(raw_speed_kmh)
        & (raw_speed_kmh <= MAX_SPEED_KMH)
    )

    speed = pd.Series(np.where(valid, raw_speed_mps, np.nan))
    # SkillCorner notes that smoothing/control should be applied to raw tracking.
    # A trailing 1-second mean is transparent and mirrors the legacy physical
    # workflow commonly used with this open sample.
    speed = speed.rolling(
        ROLLING_WINDOW_SAMPLES,
        min_periods=3,
    ).mean().to_numpy()

    usable = valid & np.isfinite(speed)
    distance = np.where(usable, speed * dt, 0.0)
    speed_kmh = speed * 3.6

    hsr_mask = usable & (speed_kmh >= HSR_MIN_KMH) & (speed_kmh < SPRINT_MIN_KMH)
    sprint_mask = usable & (speed_kmh >= SPRINT_MIN_KMH)

    return {
        "total_distance_m": float(distance.sum()),
        "hsr_distance_m": float(distance[hsr_mask].sum()),
        "sprint_distance_m": float(distance[sprint_mask].sum()),
        "speed_samples_kmh": speed_kmh[usable],
    }


def _player_metrics(observations: list[tuple[int, int, float, float]]) -> dict[str, float]:
    """
    observations: (period, frame, x, y)

    Periods and tracking gaps are never bridged when estimating speed.
    """
    if not observations:
        return {
            "total_distance_m": np.nan,
            "hsr_distance_m": np.nan,
            "sprint_distance_m": np.nan,
            "speed_p99_kmh": np.nan,
        }

    obs = pd.DataFrame(observations, columns=["period", "frame", "x", "y"])
    obs = obs.drop_duplicates(["period", "frame"]).sort_values(["period", "frame"])

    totals = defaultdict(float)
    speed_samples: list[np.ndarray] = []

    for _, period_df in obs.groupby("period", sort=True):
        period_df = period_df.sort_values("frame")
        frame = period_df["frame"].to_numpy(dtype=float)
        x = period_df["x"].to_numpy(dtype=float)
        y = period_df["y"].to_numpy(dtype=float)

        # Split again when the tracking stream has a gap > 0.5 s.
        gap = np.diff(frame, prepend=frame[0]) / FPS
        segment_id = np.cumsum(gap > MAX_GAP_SECONDS)

        for _, seg in period_df.assign(_segment=segment_id).groupby("_segment"):
            out = _segment_metrics(
                seg["frame"].to_numpy(dtype=float),
                seg["x"].to_numpy(dtype=float),
                seg["y"].to_numpy(dtype=float),
            )
            totals["total_distance_m"] += out["total_distance_m"]
            totals["hsr_distance_m"] += out["hsr_distance_m"]
            totals["sprint_distance_m"] += out["sprint_distance_m"]
            if len(out["speed_samples_kmh"]):
                speed_samples.append(out["speed_samples_kmh"])

    if speed_samples:
        speeds = np.concatenate(speed_samples)
        p99 = float(np.nanpercentile(speeds, 99))
    else:
        p99 = np.nan

    return {
        "total_distance_m": totals["total_distance_m"],
        "hsr_distance_m": totals["hsr_distance_m"],
        "sprint_distance_m": totals["sprint_distance_m"],
        "speed_p99_kmh": p99,
    }


def process_match(match_id: int) -> list[dict]:
    match_url = f"{RAW_BASE}/{match_id}/{match_id}_match.json"
    tracking_url = f"{LFS_BASE}/{match_id}/{match_id}_tracking_extrapolated.jsonl"

    meta = _url_json(match_url)
    registry, raw_id_map = _player_registry(meta)
    if not registry:
        return []

    pitch_length = float(meta.get("pitch_length") or 105.0)
    pitch_width = float(meta.get("pitch_width") or 68.0)

    observations: dict[str, list[tuple[int, int, float, float]]] = defaultdict(list)

    req = urllib.request.Request(
        tracking_url,
        headers={"User-Agent": "match-ready-football/1.0"},
    )
    with urllib.request.urlopen(req, timeout=600) as response:
        for binary_line in response:
            if not binary_line.strip():
                continue
            frame_data = json.loads(binary_line)
            frame = frame_data.get("frame")
            period = frame_data.get("period")
            if frame is None or period is None:
                continue

            for p in frame_data.get("player_data") or []:
                raw_id = p.get("player_id")
                rec = raw_id_map.get(str(raw_id))
                if rec is None:
                    continue

                start = rec.get("start_frame")
                end = rec.get("end_frame")
                if start is not None and frame < start:
                    continue
                if end is not None and frame > end:
                    continue

                x, y = p.get("x"), p.get("y")
                if not _valid_xy(x, y, pitch_length, pitch_width):
                    continue

                observations[rec["player_id"]].append(
                    (int(period), int(frame), float(x), float(y))
                )

    date = str(meta.get("date_time") or "")[:10]
    home = (meta.get("home_team") or {}).get("short_name")
    away = (meta.get("away_team") or {}).get("short_name")

    rows: list[dict] = []
    for player_id, rec in registry.items():
        metrics = _player_metrics(observations.get(player_id, []))
        minutes = rec["minutes_played"]
        scale = 90.0 / minutes if minutes > 0 else np.nan

        opponent = away if rec["team_name"] == home else home

        row = {
            "match_id": match_id,
            "date": date,
            "home_team": home,
            "away_team": away,
            "player_id": player_id,
            "player_name": rec["player_name"],
            "team": rec["team_name"],
            "opponent": opponent,
            "position": rec["position"],
            "position_group": rec["position_group"],
            "role": rec["role"],
            "minutes_played": minutes,
            **metrics,
        }
        for metric in ("total_distance_m", "hsr_distance_m", "sprint_distance_m"):
            row[f"{metric}_p90"] = metrics[metric] * scale
        rows.append(row)

    return rows


def _cv(series: pd.Series) -> float:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 2 or float(s.mean()) == 0:
        return np.nan
    return float(s.std(ddof=1) / s.mean())


def build_outputs(player_matches: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    quantiles = {"p10": .10, "p25": .25, "p50": .50, "p75": .75, "p90": .90}
    rows = []

    for position, g in player_matches.groupby("position"):
        rec = {
            "position": position,
            "n_performances": int(len(g)),
            "n_players": int(g["player_id"].nunique()),
            "n_matches": int(g["match_id"].nunique()),
        }

        for metric, prefix in (
            ("total_distance_m_p90", "total_distance"),
            ("hsr_distance_m_p90", "hsr"),
            ("sprint_distance_m_p90", "sprint"),
            ("speed_p99_kmh", "speed_p99"),
        ):
            values = pd.to_numeric(g[metric], errors="coerce").dropna()
            for label, q in quantiles.items():
                rec[f"{prefix}_{label}"] = float(values.quantile(q))
            rec[f"{prefix}_cv"] = _cv(values)

        rows.append(rec)

    position_variability = pd.DataFrame(rows).sort_values("position")

    repeated_rows = []
    for (player_id, position), g in player_matches.groupby(["player_id", "position"]):
        if len(g) < 2:
            continue
        repeated_rows.append(
            {
                "player_id": player_id,
                "player_name": g["player_name"].iloc[0],
                "position": position,
                "n_matches": int(len(g)),
                "hsr_p90_mean": float(g["hsr_distance_m_p90"].mean()),
                "hsr_p90_min": float(g["hsr_distance_m_p90"].min()),
                "hsr_p90_max": float(g["hsr_distance_m_p90"].max()),
                "hsr_p90_cv": _cv(g["hsr_distance_m_p90"]),
                "sprint_p90_mean": float(g["sprint_distance_m_p90"].mean()),
                "sprint_p90_min": float(g["sprint_distance_m_p90"].min()),
                "sprint_p90_max": float(g["sprint_distance_m_p90"].max()),
                "sprint_p90_cv": _cv(g["sprint_distance_m_p90"]),
            }
        )

    repeated = pd.DataFrame(repeated_rows)
    if not repeated.empty:
        repeated = repeated.sort_values(["position", "n_matches", "player_name"], ascending=[True, False, True])

    return position_variability, repeated


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for i, match_id in enumerate(MATCH_IDS, start=1):
        print(f"[{i}/{len(MATCH_IDS)}] Processing match {match_id}", flush=True)
        match_rows = process_match(match_id)
        rows.extend(match_rows)
        print(f"  -> {len(match_rows)} eligible outfield performances", flush=True)

    player_matches = pd.DataFrame(rows)
    if player_matches.empty:
        raise RuntimeError("No player-match rows were produced.")

    position_variability, repeated = build_outputs(player_matches)

    player_path = OUT_DIR / "skillcorner_player_match_metrics.csv"
    position_path = OUT_DIR / "skillcorner_match_variability.csv"
    repeated_path = OUT_DIR / "skillcorner_repeated_player_variability.csv"

    player_matches.to_csv(player_path, index=False)
    position_variability.to_csv(position_path, index=False)
    repeated.to_csv(repeated_path, index=False)

    print("\nSaved:")
    print(f"  {player_path}")
    print(f"  {position_path}")
    print(f"  {repeated_path}")
    print("\nPosition summary:")
    print(position_variability.to_string(index=False))


if __name__ == "__main__":
    main()
