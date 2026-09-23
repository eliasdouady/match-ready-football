# Build trigger: generate open-tracking variability summaries
from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
import pandas as pd

POSITION_MAP = {
    "Central Defender": "CB",
    "Full Back": "FB",
    "Midfield": "CM",
    "Wide Attacker": "W",
    "Center Forward": "ST",
}

FPS = 10.0
WINDOW_FRAMES = 10
MIN_MINUTES = 60.0
MAX_REASONABLE_SPEED_MPS = 11.5  # ~41.4 km/h; removes obvious tracking jumps


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def match_metadata(match_path: Path):
    data = load_json(match_path)
    players = {}

    for p in data.get("players", []):
        role = p.get("player_role") or {}
        position_group = role.get("position_group")
        mapped = POSITION_MAP.get(position_group)
        playing = (p.get("playing_time") or {}).get("total") or {}
        minutes = playing.get("minutes_played")

        if not mapped or minutes is None:
            continue

        # The current open tracking schema exposes SkillCorner player_id
        # directly in each frame, so key the lookup by the player entity id.
        players[int(p["id"])] = {
            "player_id": int(p["id"]),
            "player_name": p.get("short_name") or f"{p.get('first_name', '')} {p.get('last_name', '')}".strip(),
            "team_id": int(p["team_id"]),
            "position": mapped,
            "skillcorner_position": position_group,
            "minutes": float(minutes),
        }

    return data, players


def process_tracking(tracking_path: Path, players: dict[int, dict]):
    history = defaultdict(lambda: deque(maxlen=WINDOW_FRAMES + 3))
    speeds = defaultdict(list)
    hsr_m = defaultdict(float)
    sprint_m = defaultdict(float)
    tracked_seconds = defaultdict(float)

    with tracking_path.open("r", encoding="utf-8") as f:
        first = f.readline()
        if first.startswith("version https://git-lfs.github.com/spec"):
            raise RuntimeError(
                f"{tracking_path} is still a Git LFS pointer. Pull the LFS object before processing."
            )

        for raw in [first, *f]:
            raw = raw.strip()
            if not raw:
                continue
            frame = json.loads(raw)
            frame_id = int(frame["frame"])

            for obj in frame.get("player_data") or []:
                trackable = obj.get("player_id")
                if trackable is None:
                    continue
                trackable = int(trackable)
                if trackable not in players:
                    continue

                x = obj.get("x")
                y = obj.get("y")
                if x is None or y is None:
                    continue

                x = float(x)
                y = float(y)
                dq = history[trackable]
                dq.append((frame_id, x, y))

                # Use an approximately 1-second displacement to make speed
                # estimation less sensitive to frame-to-frame tracking noise.
                reference = None
                target_frame = frame_id - WINDOW_FRAMES
                for candidate in dq:
                    if candidate[0] <= target_frame:
                        reference = candidate
                    else:
                        break

                if reference is None:
                    continue

                old_frame, old_x, old_y = reference
                dt = (frame_id - old_frame) / FPS
                if dt < 0.7 or dt > 1.3:
                    continue

                speed_mps = float(np.hypot(x - old_x, y - old_y) / dt)
                if speed_mps < 0 or speed_mps > MAX_REASONABLE_SPEED_MPS:
                    continue

                # One frame contributes 0.1 s at 10 Hz. Distance accumulated
                # here is based on the smoothed speed estimate.
                step_distance = speed_mps / FPS
                tracked_seconds[trackable] += 1.0 / FPS
                speeds[trackable].append(speed_mps)

                speed_kmh = speed_mps * 3.6
                if 20.0 <= speed_kmh < 25.0:
                    hsr_m[trackable] += step_distance
                elif speed_kmh >= 25.0:
                    sprint_m[trackable] += step_distance

    return speeds, hsr_m, sprint_m, tracked_seconds


def build_outputs(source_root: Path):
    matches_path = source_root / "data" / "matches.json"
    matches_index = {int(m["id"]): m for m in load_json(matches_path)}

    rows = []
    tracking_files = sorted(
        (source_root / "data" / "matches").glob("*/*_tracking_extrapolated.jsonl")
    )

    for tracking_path in tracking_files:
        match_id = int(tracking_path.parent.name)
        match_path = tracking_path.parent / f"{match_id}_match.json"
        if not match_path.exists():
            continue

        match, players = match_metadata(match_path)
        if not players:
            continue

        try:
            speeds, hsr_m, sprint_m, tracked_seconds = process_tracking(
                tracking_path, players
            )
        except RuntimeError as exc:
            print(f"SKIP {match_id}: {exc}")
            continue

        index = matches_index.get(match_id, {})
        home_team = (index.get("home_team") or match.get("home_team") or {}).get(
            "short_name", "Home"
        )
        away_team = (index.get("away_team") or match.get("away_team") or {}).get(
            "short_name", "Away"
        )
        home_id = int((match.get("home_team") or {}).get("id", -1))
        away_id = int((match.get("away_team") or {}).get("id", -1))

        for trackable, meta in players.items():
            minutes = meta["minutes"]
            if minutes < MIN_MINUTES or len(speeds[trackable]) < 100:
                continue

            team_id = meta["team_id"]
            if team_id == home_id:
                team, opponent = home_team, away_team
            elif team_id == away_id:
                team, opponent = away_team, home_team
            else:
                team, opponent = str(team_id), "Unknown"

            scale = 90.0 / minutes
            speed_values = np.asarray(speeds[trackable], dtype=float) * 3.6

            rows.append(
                {
                    "match_id": match_id,
                    "date_time": index.get("date_time", match.get("date_time")),
                    "team": team,
                    "opponent": opponent,
                    "player_id": meta["player_id"],
                    "player_name": meta["player_name"],
                    "position": meta["position"],
                    "skillcorner_position": meta["skillcorner_position"],
                    "minutes": round(minutes, 2),
                    "tracked_minutes": round(tracked_seconds[trackable] / 60.0, 2),
                    "hsr_m": round(hsr_m[trackable], 1),
                    "sprint_m": round(sprint_m[trackable], 1),
                    "hsr_m_per90": round(hsr_m[trackable] * scale, 1),
                    "sprint_m_per90": round(sprint_m[trackable] * scale, 1),
                    "speed_p99_kmh": round(float(np.percentile(speed_values, 99)), 2),
                    "speed_max_kmh": round(float(np.max(speed_values)), 2),
                }
            )

        print(f"Processed match {match_id}: {home_team} vs {away_team}")

    observations = pd.DataFrame(rows)
    if observations.empty:
        raise RuntimeError("No eligible player-match observations were produced.")

    observations = observations.sort_values(
        ["date_time", "match_id", "position", "player_name"]
    ).reset_index(drop=True)

    summary_rows = []
    for position, group in observations.groupby("position"):
        repeated = group.groupby("player_id").filter(lambda g: len(g) >= 2)
        repeated_player_count = repeated["player_id"].nunique()

        within_player_hsr_cv = []
        within_player_sprint_cv = []
        for _, pg in repeated.groupby("player_id"):
            for col, target in [
                ("hsr_m_per90", within_player_hsr_cv),
                ("sprint_m_per90", within_player_sprint_cv),
            ]:
                mean = pg[col].mean()
                if mean > 0 and len(pg) >= 2:
                    target.append(float(pg[col].std(ddof=1) / mean * 100))

        row = {
            "position": position,
            "n_player_matches": int(len(group)),
            "n_players": int(group["player_id"].nunique()),
            "n_repeated_players": int(repeated_player_count),
            "n_matches": int(group["match_id"].nunique()),
        }

        for col, prefix in [
            ("hsr_m_per90", "hsr"),
            ("sprint_m_per90", "sprint"),
            ("speed_p99_kmh", "speed_p99"),
        ]:
            for label, q in [("p10", .10), ("p25", .25), ("p50", .50), ("p75", .75), ("p90", .90)]:
                row[f"{prefix}_{label}"] = round(float(group[col].quantile(q)), 2)

        row["hsr_within_player_cv_median_pct"] = (
            round(float(np.median(within_player_hsr_cv)), 2)
            if within_player_hsr_cv
            else np.nan
        )
        row["sprint_within_player_cv_median_pct"] = (
            round(float(np.median(within_player_sprint_cv)), 2)
            if within_player_sprint_cv
            else np.nan
        )
        summary_rows.append(row)

    variability = pd.DataFrame(summary_rows).sort_values("position").reset_index(drop=True)
    return observations, variability


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        type=Path,
        required=True,
        help="Path to a checked-out SkillCorner/opendata repository with LFS tracking files pulled.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "real",
    )
    args = parser.parse_args()

    observations, variability = build_outputs(args.source_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    obs_path = args.output_dir / "skillcorner_tracking_player_matches.csv"
    var_path = args.output_dir / "skillcorner_tracking_variability.csv"

    observations.to_csv(obs_path, index=False)
    variability.to_csv(var_path, index=False)

    print(f"Saved {obs_path} ({len(observations)} rows)")
    print(f"Saved {var_path} ({len(variability)} positions)")
    print(variability.to_string(index=False))


if __name__ == "__main__":
    main()
