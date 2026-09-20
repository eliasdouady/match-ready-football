from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42
rng = np.random.default_rng(SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = pd.Timestamp("2026-07-20")   # Monday
N_WEEKS = 8


# ============================================================
# POSITION PROFILES
# Approximate synthetic match demands
# ============================================================

POSITION_PROFILES = {
    "CB": {
        "count": 5,
        "vmax_mean": 32.0,
        "vmax_sd": 0.8,
        "total_distance": 9800,
        "hsr": 430,
        "sprint": 90,
        "accelerations": 34,
        "decelerations": 32,
    },
    "FB": {
        "count": 5,
        "vmax_mean": 34.0,
        "vmax_sd": 0.9,
        "total_distance": 10800,
        "hsr": 820,
        "sprint": 250,
        "accelerations": 45,
        "decelerations": 44,
    },
    "CM": {
        "count": 5,
        "vmax_mean": 32.5,
        "vmax_sd": 0.8,
        "total_distance": 11200,
        "hsr": 650,
        "sprint": 140,
        "accelerations": 47,
        "decelerations": 46,
    },
    "W": {
        "count": 5,
        "vmax_mean": 35.0,
        "vmax_sd": 0.9,
        "total_distance": 10400,
        "hsr": 920,
        "sprint": 330,
        "accelerations": 48,
        "decelerations": 46,
    },
    "ST": {
        "count": 4,
        "vmax_mean": 34.4,
        "vmax_sd": 0.8,
        "total_distance": 9900,
        "hsr": 750,
        "sprint": 280,
        "accelerations": 43,
        "decelerations": 40,
    },
}


# ============================================================
# TRAINING MICRO-CYCLE
# Values are expressed relative to individual match demands.
# ============================================================

MICROCYCLE = {
    0: {
        "md_code": "OFF",
        "focus": "Off",
        "session_type": "Off",
    },
    1: {
        "md_code": "MD-4",
        "focus": "Volume",
        "session_type": "Training",
    },
    2: {
        "md_code": "MD-3",
        "focus": "Speed / HSR",
        "session_type": "Training",
    },
    3: {
        "md_code": "MD-2",
        "focus": "Tactical",
        "session_type": "Training",
    },
    4: {
        "md_code": "MD-1",
        "focus": "Activation",
        "session_type": "Training",
    },
    5: {
        "md_code": "MD",
        "focus": "Match",
        "session_type": "Match",
    },
    6: {
        "md_code": "MD+1",
        "focus": "Recovery",
        "session_type": "Recovery",
    },
}


TRAINING_CONFIG = {
    "OFF": {
        "duration": 0,
        "distance": 0,
        "hsr": 0,
        "sprint": 0,
        "accel": 0,
        "decel": 0,
        "vmax_ratio": 0,
        "rpe": 0,
    },

    "MD-4": {
        "duration": 78,
        "distance": 0.64,
        "hsr": 0.52,
        "sprint": 0.32,
        "accel": 0.72,
        "decel": 0.72,
        "vmax_ratio": 0.80,
        "rpe": 5.2,
    },

    "MD-3": {
        "duration": 88,
        "distance": 0.78,
        "hsr": 0.86,
        "sprint": 0.82,
        "accel": 0.88,
        "decel": 0.88,
        "vmax_ratio": 0.92,
        "rpe": 6.4,
    },

    "MD-2": {
        "duration": 70,
        "distance": 0.54,
        "hsr": 0.42,
        "sprint": 0.27,
        "accel": 0.62,
        "decel": 0.62,
        "vmax_ratio": 0.79,
        "rpe": 4.4,
    },

    "MD-1": {
        "duration": 44,
        "distance": 0.30,
        "hsr": 0.14,
        "sprint": 0.08,
        "accel": 0.34,
        "decel": 0.34,
        "vmax_ratio": 0.70,
        "rpe": 2.6,
    },

    "MD+1": {
        "duration": 34,
        "distance": 0.22,
        "hsr": 0.04,
        "sprint": 0.01,
        "accel": 0.18,
        "decel": 0.18,
        "vmax_ratio": 0.55,
        "rpe": 1.8,
    },

    "TOP_UP": {
        "duration": 52,
        "distance": 0.46,
        "hsr": 0.40,
        "sprint": 0.25,
        "accel": 0.55,
        "decel": 0.55,
        "vmax_ratio": 0.82,
        "rpe": 4.7,
    },
}


STARTERS_BY_POSITION = {
    "CB": 2,
    "FB": 2,
    "CM": 3,
    "W": 2,
    "ST": 1,
}


# ============================================================
# HELPERS
# ============================================================

def positive(value):
    return max(0, value)


def noisy(value, sd=0.08):
    """
    Add proportional noise.
    """
    return value * rng.normal(1.0, sd)


# ============================================================
# PLAYER GENERATION
# ============================================================

def create_players():
    players = []

    player_number = 1

    for position, profile in POSITION_PROFILES.items():

        for _ in range(profile["count"]):

            player_id = f"P{player_number:02d}"

            vmax = rng.normal(
                profile["vmax_mean"],
                profile["vmax_sd"]
            )

            player = {
                "player_id": player_id,
                "player_name": f"Player {player_number:02d}",
                "position": position,

                "vmax_kmh": round(vmax, 2),

                "match_total_distance_m":
                    round(noisy(profile["total_distance"], 0.05), 0),

                "match_hsr_m":
                    round(noisy(profile["hsr"], 0.08), 0),

                "match_sprint_distance_m":
                    round(noisy(profile["sprint"], 0.10), 0),

                "match_accelerations":
                    round(noisy(profile["accelerations"], 0.07), 0),

                "match_decelerations":
                    round(noisy(profile["decelerations"], 0.07), 0),
            }

            players.append(player)

            player_number += 1

    return pd.DataFrame(players)


# ============================================================
# MATCH SELECTION
# ============================================================

def create_match_roles(players):
    """
    Creates realistic weekly match involvement:
    - 10 outfield starters
    - 4 substitutes used
    - remaining players unused

    Special scenario:
    - P22 is unavailable in week 4
    - P22 returns as a substitute in week 5
    """

    roles = {}

    for week in range(1, N_WEEKS + 1):

        week_roles = {
            player_id: "Unused"
            for player_id in players["player_id"]
        }

        starters = []

        for position, n_starters in STARTERS_BY_POSITION.items():

            candidates = players[
                players["position"] == position
            ]["player_id"].tolist()

            # P22 is not available to start during weeks 4-5
            if (
                position == "ST"
                and week in [4, 5]
                and "P22" in candidates
            ):
                candidates.remove("P22")

            selected = rng.choice(
                candidates,
                size=n_starters,
                replace=False
            )

            starters.extend(selected.tolist())

        for player_id in starters:
            week_roles[player_id] = "Starter"

        remaining = [
            p for p in players["player_id"]
            if p not in starters
        ]

        # Week 4: P22 unavailable
        if week == 4:

            available_for_subs = [
                p for p in remaining
                if p != "P22"
            ]

            subs = rng.choice(
                available_for_subs,
                size=4,
                replace=False
            ).tolist()

        # Week 5: P22 returns from the bench
        elif week == 5:

            available_for_subs = [
                p for p in remaining
                if p != "P22"
            ]

            other_subs = rng.choice(
                available_for_subs,
                size=3,
                replace=False
            ).tolist()

            subs = ["P22"] + other_subs

        else:

            subs = rng.choice(
                remaining,
                size=4,
                replace=False
            ).tolist()

        for player_id in subs:
            week_roles[player_id] = "Sub"

        roles[week] = week_roles

    return roles


# ============================================================
# NORMAL TRAINING SESSION
# ============================================================

def generate_training_session(player, md_code):

    config = TRAINING_CONFIG[md_code]

    if md_code == "OFF":

        return {
            "duration_min": 0,
            "total_distance_m": 0,
            "hsr_m": 0,
            "sprint_distance_m": 0,
            "accelerations": 0,
            "decelerations": 0,
            "max_speed_kmh": 0,
            "percent_vmax": 0,
            "session_rpe": 0,
        }

    duration = positive(
        rng.normal(config["duration"], 4)
    )

    total_distance = positive(
        noisy(
            player["match_total_distance_m"]
            * config["distance"],
            0.07
        )
    )

    hsr = positive(
        noisy(
            player["match_hsr_m"]
            * config["hsr"],
            0.12
        )
    )

    sprint = positive(
        noisy(
            player["match_sprint_distance_m"]
            * config["sprint"],
            0.15
        )
    )

    accelerations = positive(
        noisy(
            player["match_accelerations"]
            * config["accel"],
            0.10
        )
    )

    decelerations = positive(
        noisy(
            player["match_decelerations"]
            * config["decel"],
            0.10
        )
    )

    vmax_ratio = np.clip(
        rng.normal(
            config["vmax_ratio"],
            0.035
        ),
        0,
        1.02
    )

    max_speed = player["vmax_kmh"] * vmax_ratio

    rpe = np.clip(
        rng.normal(config["rpe"], 0.6),
        0,
        10
    )

    return {
        "duration_min": round(duration, 0),
        "total_distance_m": round(total_distance, 0),
        "hsr_m": round(hsr, 0),
        "sprint_distance_m": round(sprint, 0),
        "accelerations": round(accelerations, 0),
        "decelerations": round(decelerations, 0),
        "max_speed_kmh": round(max_speed, 2),
        "percent_vmax": round(vmax_ratio * 100, 1),
        "session_rpe": round(rpe, 1),
    }


# ============================================================
# MATCH / TOP-UP SESSION
# ============================================================

def generate_match_session(player, role):

    if role == "Starter":

        minutes = np.clip(
            rng.normal(87, 7),
            65,
            96
        )

        minute_factor = minutes / 90

        total_distance = noisy(
            player["match_total_distance_m"]
            * minute_factor,
            0.07
        )

        hsr = noisy(
            player["match_hsr_m"]
            * minute_factor,
            0.14
        )

        sprint = noisy(
            player["match_sprint_distance_m"]
            * minute_factor,
            0.18
        )

        accels = noisy(
            player["match_accelerations"]
            * minute_factor,
            0.10
        )

        decels = noisy(
            player["match_decelerations"]
            * minute_factor,
            0.10
        )

        vmax_ratio = np.clip(
            rng.normal(0.95, 0.035),
            0.83,
            1.02
        )

        rpe = np.clip(
            rng.normal(8.4, 0.7),
            6,
            10
        )

        session_type = "Match"

    elif role == "Sub":

        minutes = np.clip(
            rng.normal(26, 9),
            8,
            45
        )

        # substitutes generally operate at slightly
        # higher intensity per minute
        minute_factor = (minutes / 90) * 1.08

        total_distance = noisy(
            player["match_total_distance_m"]
            * minute_factor,
            0.10
        )

        hsr = noisy(
            player["match_hsr_m"]
            * minute_factor,
            0.20
        )

        sprint = noisy(
            player["match_sprint_distance_m"]
            * minute_factor,
            0.24
        )

        accels = noisy(
            player["match_accelerations"]
            * minute_factor,
            0.13
        )

        decels = noisy(
            player["match_decelerations"]
            * minute_factor,
            0.13
        )

        vmax_ratio = np.clip(
            rng.normal(0.88, 0.06),
            0.70,
            1.00
        )

        rpe = np.clip(
            rng.normal(7.2, 0.8),
            5,
            10
        )

        session_type = "Match"

    else:

        session = generate_training_session(
            player,
            "TOP_UP"
        )

        session["session_type"] = "Top-up"

        return session

    max_speed = (
        player["vmax_kmh"]
        * vmax_ratio
    )

    return {
        "duration_min": round(minutes, 0),
        "total_distance_m": round(positive(total_distance), 0),
        "hsr_m": round(positive(hsr), 0),
        "sprint_distance_m": round(positive(sprint), 0),
        "accelerations": round(positive(accels), 0),
        "decelerations": round(positive(decels), 0),
        "max_speed_kmh": round(max_speed, 2),
        "percent_vmax": round(vmax_ratio * 100, 1),
        "session_rpe": round(rpe, 1),
        "session_type": session_type,
    }


# ============================================================
# STORYTELLING SCENARIOS
# ============================================================

def apply_special_scenarios(row):
    """
    Intentionally creates realistic situations that the
    future monitoring system should detect.
    """

    # --------------------------------------------------------
    # PLAYER 18 - WINGER
    # Hidden sprint underexposure
    # Normal total running volume but insufficient speed exposure.
    # --------------------------------------------------------

    if (
        row["player_id"] == "P18"
        and row["week"] in [5, 6]
        and row["md_code"] in ["MD-4", "MD-3", "MD-2", "MD-1"]
    ):

        row["hsr_m"] *= 0.72
        row["sprint_distance_m"] *= 0.42

        row["max_speed_kmh"] = min(
            row["max_speed_kmh"],
            row["player_vmax_kmh"] * 0.84
        )

        row["percent_vmax"] = (
            row["max_speed_kmh"]
            / row["player_vmax_kmh"]
            * 100
        )

    # --------------------------------------------------------
    # PLAYER 07 - FULL BACK
    # High accumulated training load during week 7.
    # --------------------------------------------------------

    if (
        row["player_id"] == "P07"
        and row["week"] == 7
        and row["md_code"] in ["MD-4", "MD-3", "MD-2"]
    ):

        row["total_distance_m"] *= 1.18
        row["accelerations"] *= 1.15
        row["decelerations"] *= 1.15
        row["session_rpe"] = min(
            row["session_rpe"] + 1.3,
            10
        )

    # --------------------------------------------------------
    # PLAYER 22 - STRIKER
    # Reduced training exposure in week 4
    # followed by progressive reintegration.
    # --------------------------------------------------------

    if row["player_id"] == "P22":

        if row["week"] == 4:

            row["total_distance_m"] *= 0.55
            row["hsr_m"] *= 0.45
            row["sprint_distance_m"] *= 0.35

        elif row["week"] == 5:

            row["total_distance_m"] *= 0.78
            row["hsr_m"] *= 0.70
            row["sprint_distance_m"] *= 0.65

    return row


# ============================================================
# FULL DATASET GENERATION
# ============================================================

def generate_dataset():

    players = create_players()
    match_roles = create_match_roles(players)

    dates = pd.date_range(
        START_DATE,
        periods=N_WEEKS * 7,
        freq="D"
    )

    rows = []

    for date in dates:

        week = (
            (date - START_DATE).days // 7
        ) + 1

        weekday = date.weekday()

        day_plan = MICROCYCLE[weekday]

        for _, player in players.iterrows():

            role = match_roles[week][
                player["player_id"]
            ]

            if day_plan["md_code"] == "MD":

                session = generate_match_session(
                    player,
                    role
                )

                session_type = session.get(
                    "session_type",
                    "Match"
                )

            else:

                session = generate_training_session(
                    player,
                    day_plan["md_code"]
                )

                session_type = day_plan[
                    "session_type"
                ]

            row = {
                "date": date,
                "week": week,

                "player_id":
                    player["player_id"],

                "player_name":
                    player["player_name"],

                "position":
                    player["position"],

                "player_vmax_kmh":
                    player["vmax_kmh"],

                "md_code":
                    day_plan["md_code"],

                "session_focus":
                    day_plan["focus"],

                "session_type":
                    session_type,

                "match_role":
                    role if day_plan["md_code"] == "MD"
                    else "N/A",

                **{
                    key: value
                    for key, value in session.items()
                    if key != "session_type"
                }
            }

            rows.append(row)

    df = pd.DataFrame(rows)

    # --------------------------------------------------------
    # Apply synthetic storyline scenarios
    # --------------------------------------------------------

    df = df.apply(
        apply_special_scenarios,
        axis=1
    )

    # --------------------------------------------------------
    # Session load = duration x session RPE
    # --------------------------------------------------------

    df["session_load_au"] = (
        df["duration_min"]
        * df["session_rpe"]
    ).round(0)

    # --------------------------------------------------------
    # PRE-SESSION WELLNESS
    # Estimated from previous 3 days training load.
    # --------------------------------------------------------

    df = df.sort_values(
        ["player_id", "date"]
    ).reset_index(drop=True)

    df["previous_3d_load"] = (
        df
        .groupby("player_id")["session_load_au"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=3,
                min_periods=1
            )
            .sum()
        )
    )

    df["previous_3d_load"] = (
        df["previous_3d_load"]
        .fillna(0)
    )

    wellness_noise = rng.normal(
        0,
        3.2,
        len(df)
    )

    df["wellness_score"] = (
        88
        - 0.008
        * df["previous_3d_load"]
        + wellness_noise
    )

    # Extra fatigue scenario for Player 07
    mask_p07 = (
        (df["player_id"] == "P07")
        & (df["week"] == 7)
    )

    df.loc[
        mask_p07,
        "wellness_score"
    ] -= 10

    df["wellness_score"] = (
        df["wellness_score"]
        .clip(50, 96)
        .round(0)
    )

    # --------------------------------------------------------
    # Clean numeric values
    # --------------------------------------------------------

    numeric_cols = [
        "total_distance_m",
        "hsr_m",
        "sprint_distance_m",
        "accelerations",
        "decelerations",
        "session_load_au",
    ]

    for col in numeric_cols:

        df[col] = (
            df[col]
            .clip(lower=0)
            .round(0)
        )

    df["max_speed_kmh"] = (
        df["max_speed_kmh"]
        .clip(lower=0)
        .round(2)
    )

    df["percent_vmax"] = (
        df["percent_vmax"]
        .clip(lower=0, upper=102)
        .round(1)
    )

    # --------------------------------------------------------
    # Position benchmark dataframe
    # --------------------------------------------------------

    benchmark_rows = []

    for position, values in POSITION_PROFILES.items():

        benchmark_rows.append({
            "position": position,
            "typical_match_total_distance_m":
                values["total_distance"],

            "typical_match_hsr_m":
                values["hsr"],

            "typical_match_sprint_distance_m":
                values["sprint"],

            "typical_match_accelerations":
                values["accelerations"],

            "typical_match_decelerations":
                values["decelerations"],

            "typical_vmax_kmh":
                values["vmax_mean"],
        })

    benchmarks = pd.DataFrame(
        benchmark_rows
    )

    # --------------------------------------------------------
    # SAVE FILES
    # --------------------------------------------------------

    players.to_csv(
        RAW_DIR / "player_profiles.csv",
        index=False
    )

    df.to_csv(
        RAW_DIR / "sessions.csv",
        index=False
    )

    benchmarks.to_csv(
        RAW_DIR / "position_benchmarks.csv",
        index=False
    )

    print("")
    print("=" * 60)
    print("MATCH READY DATASET GENERATED")
    print("=" * 60)

    print(
        f"Players: {players.shape[0]}"
    )

    print(
        f"Sessions: {df.shape[0]}"
    )

    print(
        f"Weeks: {N_WEEKS}"
    )

    print("")

    print(
        f"Saved to: {RAW_DIR}"
    )

    print("")
    print("Files:")
    print(" - player_profiles.csv")
    print(" - sessions.csv")
    print(" - position_benchmarks.csv")

    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    generate_dataset()