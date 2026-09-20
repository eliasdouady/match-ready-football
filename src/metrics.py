from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# PATHS & CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

BASELINE_WEEKS = [1, 2, 3]

MONITORING_START_WEEK = 4

TRAINING_MD_CODES = [
    "MD-4",
    "MD-3",
    "MD-2",
    "MD-1",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    sessions = pd.read_csv(
        RAW_DIR / "sessions.csv",
        parse_dates=["date"]
    )

    players = pd.read_csv(
        RAW_DIR / "player_profiles.csv"
    )

    benchmarks = pd.read_csv(
        RAW_DIR / "position_benchmarks.csv"
    )

    sessions = sessions.sort_values(
        ["player_id", "date"]
    ).reset_index(drop=True)

    return sessions, players, benchmarks


# ============================================================
# DAILY ROLLING METRICS
# ============================================================

def add_rolling_metrics(df):

    df = df.copy()

    rolling_variables = [
        "session_load_au",
        "total_distance_m",
        "hsr_m",
        "sprint_distance_m",
    ]

    for variable in rolling_variables:

        df[f"{variable}_7d"] = (
            df
            .groupby("player_id")[variable]
            .transform(
                lambda x:
                x.rolling(
                    window=7,
                    min_periods=1
                ).sum()
            )
        )

        df[f"{variable}_28d"] = (
            df
            .groupby("player_id")[variable]
            .transform(
                lambda x:
                x.rolling(
                    window=28,
                    min_periods=1
                ).sum()
            )
        )

    # --------------------------------------------------------
    # CONTEXTUAL 7:28 LOAD RATIO
    #
    # Included only as descriptive context.
    # It will NOT drive the monitoring classification.
    # --------------------------------------------------------

    df["chronic_load_weekly_equivalent"] = (
        df["session_load_au_28d"] / 4
    )

    df["observation_days"] = (
        df
        .groupby("player_id")
        .cumcount()
        + 1
    )

    denominator = (
        df["chronic_load_weekly_equivalent"]
        .replace(0, np.nan)
    )

    df["load_ratio_7_28_context"] = (
        df["session_load_au_7d"]
        / denominator
    )

    # Do not display the ratio before enough
    # historical information exists.
    df.loc[
        df["observation_days"] < 28,
        "load_ratio_7_28_context"
    ] = np.nan

    return df


# ============================================================
# DAYS SINCE SPEED EXPOSURE
# ============================================================

def add_speed_exposure_recency(df):

    df = df.copy()

    thresholds = [85, 90, 95]

    for threshold in thresholds:

        output = pd.Series(
            index=df.index,
            dtype=float
        )

        for _, group in df.groupby(
            "player_id",
            sort=False
        ):

            last_exposure_date = None

            for idx, row in group.iterrows():

                if (
                    row["percent_vmax"]
                    >= threshold
                ):
                    last_exposure_date = row["date"]

                if last_exposure_date is None:

                    days_since = np.nan

                else:

                    days_since = (
                        row["date"]
                        - last_exposure_date
                    ).days

                output.loc[idx] = days_since

        df[
            f"days_since_{threshold}_pct_vmax"
        ] = output

    return df


# ============================================================
# WEEKLY TRAINING MICRO-CYCLE
# ============================================================

def build_weekly_training_metrics(df):

    training = df[
        df["md_code"].isin(
            TRAINING_MD_CODES
        )
    ].copy()

    weekly = (
        training
        .groupby(
            [
                "player_id",
                "player_name",
                "position",
                "week",
            ],
            as_index=False
        )
        .agg(
            training_distance_m=(
                "total_distance_m",
                "sum"
            ),

            training_hsr_m=(
                "hsr_m",
                "sum"
            ),

            training_sprint_m=(
                "sprint_distance_m",
                "sum"
            ),

            training_load_au=(
                "session_load_au",
                "sum"
            ),

            training_accelerations=(
                "accelerations",
                "sum"
            ),

            training_decelerations=(
                "decelerations",
                "sum"
            ),

            peak_training_speed_kmh=(
                "max_speed_kmh",
                "max"
            ),

            peak_training_pct_vmax=(
                "percent_vmax",
                "max"
            ),
        )
    )

    return weekly


# ============================================================
# MD-1 SNAPSHOT INFORMATION
# ============================================================

def build_md1_context(df):

    md1 = df[
        df["md_code"] == "MD-1"
    ].copy()

    columns = [
        "player_id",
        "week",
        "date",
        "wellness_score",
        "session_load_au_7d",
        "session_load_au_28d",
        "total_distance_m_7d",
        "hsr_m_7d",
        "sprint_distance_m_7d",
        "load_ratio_7_28_context",
        "days_since_85_pct_vmax",
        "days_since_90_pct_vmax",
        "days_since_95_pct_vmax",
    ]

    md1 = md1[columns]

    md1 = md1.rename(
        columns={
            "date":
                "snapshot_date",

            "wellness_score":
                "md1_wellness",

            "session_load_au_7d":
                "load_7d_au",

            "session_load_au_28d":
                "load_28d_au",

            "total_distance_m_7d":
                "distance_7d_m",

            "hsr_m_7d":
                "hsr_7d_m",

            "sprint_distance_m_7d":
                "sprint_7d_m",
        }
    )

    return md1


# ============================================================
# INDIVIDUAL BASELINE
# ============================================================

def build_individual_baseline(weekly):

    baseline_data = weekly[
        weekly["week"].isin(
            BASELINE_WEEKS
        )
    ].copy()

    baseline = (
        baseline_data
        .groupby(
            "player_id",
            as_index=False
        )
        .agg(
            baseline_training_distance_m=(
                "training_distance_m",
                "median"
            ),

            baseline_training_hsr_m=(
                "training_hsr_m",
                "median"
            ),

            baseline_training_sprint_m=(
                "training_sprint_m",
                "median"
            ),

            baseline_training_load_au=(
                "training_load_au",
                "median"
            ),

            baseline_peak_pct_vmax=(
                "peak_training_pct_vmax",
                "median"
            ),

            baseline_accelerations=(
                "training_accelerations",
                "median"
            ),

            baseline_decelerations=(
                "training_decelerations",
                "median"
            ),
        )
    )

    return baseline


# ============================================================
# MD-1 WELLNESS BASELINE
# ============================================================

def build_wellness_baseline(md1):

    baseline = md1[
        md1["week"].isin(
            BASELINE_WEEKS
        )
    ]

    wellness_baseline = (
        baseline
        .groupby(
            "player_id",
            as_index=False
        )
        .agg(
            baseline_md1_wellness=(
                "md1_wellness",
                "median"
            )
        )
    )

    return wellness_baseline


# ============================================================
# SAFE RATIO
# ============================================================

def safe_ratio(numerator, denominator):

    denominator = denominator.replace(
        0,
        np.nan
    )

    return numerator / denominator


# ============================================================
# EXPOSURE INDEX
# ============================================================

def calculate_preparation_alignment(df):
    """
    Transparent portfolio heuristic (0-100).

    The index describes how closely the current training exposure
    resembles the player's own preparation baseline. It is intentionally
    NOT a medical score and NOT an injury-probability model.

    Unlike the previous version, values above baseline do not simply
    saturate at 100. This makes the index more informative visually:
    large deviations below OR above the player's usual preparation
    reduce alignment, while near-baseline exposure scores highest.
    """

    sprint_alignment = np.clip(
        1 - np.abs(df["sprint_vs_baseline"] - 1.0),
        0,
        1,
    )

    hsr_alignment = np.clip(
        1 - np.abs(df["hsr_vs_baseline"] - 1.0),
        0,
        1,
    )

    speed_component = np.clip(
        df["peak_training_pct_vmax"] / 90,
        0,
        1,
    )

    alignment = (
        0.50 * sprint_alignment
        + 0.25 * hsr_alignment
        + 0.25 * speed_component
    ) * 100

    return alignment.round(0)


# ============================================================
# MONITORING CLASSIFICATION
# ============================================================

def classify_player(row):
    """
    Demonstration monitoring logic.

    The thresholds below are deliberately transparent portfolio rules.
    They are not clinical thresholds and must not be interpreted as an
    injury prediction model.
    """

    if row["week"] < MONITORING_START_WEEK:
        return pd.Series({
            "monitoring_status": "Baseline",
            "monitoring_reasons": "Baseline acquisition period",
        })

    hard_underexposure = []
    monitoring_flags = []

    # Strong underexposure signals
    if row["sprint_vs_baseline"] < 0.60:
        hard_underexposure.append("Very low sprint exposure")

    if row["hsr_vs_baseline"] < 0.60:
        hard_underexposure.append("Very low HSR exposure")

    if row["peak_training_pct_vmax"] < 85:
        hard_underexposure.append("No recent high-speed exposure")

    # Moderate exposure signals
    if 0.60 <= row["sprint_vs_baseline"] < 0.85:
        monitoring_flags.append("Reduced sprint exposure")

    if 0.60 <= row["hsr_vs_baseline"] < 0.80:
        monitoring_flags.append("Reduced HSR exposure")

    # A single week below 90% Vmax is not automatically treated as a
    # monitoring issue if the player was exposed recently. This avoids
    # over-flagging normal microcycle variation.
    days_since_90 = row.get("days_since_90_pct_vmax", np.nan)

    if (
        85 <= row["peak_training_pct_vmax"] < 90
        and (pd.isna(days_since_90) or days_since_90 >= 10)
    ):
        monitoring_flags.append("Limited recent >90% Vmax exposure")

    # Load context
    if row["load_vs_baseline"] > 1.20:
        monitoring_flags.append("Elevated training load")

    if row["load_vs_baseline"] < 0.75:
        monitoring_flags.append("Reduced overall training load")

    # Wellness context
    if row["wellness_delta"] <= -8:
        monitoring_flags.append("Wellness below individual baseline")

    if hard_underexposure:
        status = "Underexposed"
        reasons = hard_underexposure + monitoring_flags
    elif monitoring_flags:
        status = "Monitor"
        reasons = monitoring_flags
    else:
        status = "Ready"
        reasons = ["Exposure aligned with individual baseline"]

    return pd.Series({
        "monitoring_status": status,
        "monitoring_reasons": "; ".join(reasons),
    })


# ============================================================
# BUILD PLAYER WEEKLY SNAPSHOTS
# ============================================================

def build_player_snapshots(
    df,
    players
):

    weekly = build_weekly_training_metrics(
        df
    )

    md1 = build_md1_context(
        df
    )

    baseline = build_individual_baseline(
        weekly
    )

    wellness_baseline = (
        build_wellness_baseline(
            md1
        )
    )

    # --------------------------------------------------------
    # MERGE ALL CONTEXT
    # --------------------------------------------------------

    snapshot = weekly.merge(
        md1,
        on=[
            "player_id",
            "week"
        ],
        how="left"
    )

    snapshot = snapshot.merge(
        baseline,
        on="player_id",
        how="left"
    )

    snapshot = snapshot.merge(
        wellness_baseline,
        on="player_id",
        how="left"
    )

    player_reference_columns = [
        "player_id",
        "vmax_kmh",
        "match_total_distance_m",
        "match_hsr_m",
        "match_sprint_distance_m",
        "match_accelerations",
        "match_decelerations",
    ]

    snapshot = snapshot.merge(
        players[
            player_reference_columns
        ],
        on="player_id",
        how="left"
    )

    # --------------------------------------------------------
    # CURRENT VS INDIVIDUAL BASELINE
    # --------------------------------------------------------

    snapshot["distance_vs_baseline"] = (
        safe_ratio(
            snapshot["training_distance_m"],
            snapshot[
                "baseline_training_distance_m"
            ]
        )
    )

    snapshot["hsr_vs_baseline"] = (
        safe_ratio(
            snapshot["training_hsr_m"],
            snapshot[
                "baseline_training_hsr_m"
            ]
        )
    )

    snapshot["sprint_vs_baseline"] = (
        safe_ratio(
            snapshot["training_sprint_m"],
            snapshot[
                "baseline_training_sprint_m"
            ]
        )
    )

    snapshot["load_vs_baseline"] = (
        safe_ratio(
            snapshot["training_load_au"],
            snapshot[
                "baseline_training_load_au"
            ]
        )
    )

    # --------------------------------------------------------
    # TRAINING VS MATCH DEMANDS
    # --------------------------------------------------------

    snapshot[
        "training_to_match_hsr"
    ] = safe_ratio(
        snapshot["training_hsr_m"],
        snapshot["match_hsr_m"]
    )

    snapshot[
        "training_to_match_sprint"
    ] = safe_ratio(
        snapshot["training_sprint_m"],
        snapshot[
            "match_sprint_distance_m"
        ]
    )

    snapshot[
        "peak_speed_vs_player_vmax"
    ] = safe_ratio(
        snapshot["peak_training_speed_kmh"],
        snapshot["vmax_kmh"]
    )

    # --------------------------------------------------------
    # WELLNESS
    # --------------------------------------------------------

    snapshot["wellness_delta"] = (
        snapshot["md1_wellness"]
        - snapshot[
            "baseline_md1_wellness"
        ]
    )

    # --------------------------------------------------------
    # SIMPLE LOAD CONTEXT
    # --------------------------------------------------------

    conditions = [
        snapshot["load_vs_baseline"] < 0.75,

        snapshot["load_vs_baseline"] > 1.20,
    ]

    choices = [
        "Low",
        "High",
    ]

    snapshot["load_context"] = np.select(
        conditions,
        choices,
        default="Typical"
    )

    # --------------------------------------------------------
    # TRAINING CONTEXT / AVAILABILITY
    # --------------------------------------------------------

    snapshot["training_context"] = "Full training"
    snapshot["context_note"] = "Normal squad training plan"
    snapshot["planned_reduction"] = False

    # Synthetic return-to-performance storyline for P22.
    mask = (
        (snapshot["player_id"] == "P22")
        & (snapshot["week"] == 4)
    )
    snapshot.loc[mask, "training_context"] = "Modified / unavailable"
    snapshot.loc[mask, "context_note"] = (
        "Reduced exposure is planned within the synthetic return-to-performance scenario"
    )
    snapshot.loc[mask, "planned_reduction"] = True

    mask = (
        (snapshot["player_id"] == "P22")
        & (snapshot["week"] == 5)
    )
    snapshot.loc[mask, "training_context"] = "Reintegration"
    snapshot.loc[mask, "context_note"] = (
        "Progressive reintegration: reduced external load is expected rather than unexpected"
    )
    snapshot.loc[mask, "planned_reduction"] = True

    mask = (
        (snapshot["player_id"] == "P22")
        & (snapshot["week"] == 6)
    )
    snapshot.loc[mask, "training_context"] = "Return to full training"
    snapshot.loc[mask, "context_note"] = (
        "Exposure has returned towards the player's usual preparation profile"
    )

    # --------------------------------------------------------
    # PREPARATION ALIGNMENT
    # --------------------------------------------------------

    snapshot["preparation_alignment"] = (
        calculate_preparation_alignment(snapshot)
    )

    # Backward-compatible alias used by the first visual-export script.
    snapshot["exposure_index"] = snapshot["preparation_alignment"]

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    classification = snapshot.apply(
        classify_player,
        axis=1
    )

    snapshot = pd.concat(
        [
            snapshot,
            classification
        ],
        axis=1
    )

    # --------------------------------------------------------
    # ROUND RATIOS FOR EXPORT
    # --------------------------------------------------------

    ratio_columns = [
        "distance_vs_baseline",
        "hsr_vs_baseline",
        "sprint_vs_baseline",
        "load_vs_baseline",
        "training_to_match_hsr",
        "training_to_match_sprint",
        "peak_speed_vs_player_vmax",
        "load_ratio_7_28_context",
    ]

    for column in ratio_columns:

        snapshot[column] = (
            snapshot[column]
            .round(2)
        )

    return snapshot


# ============================================================
# TEAM WEEKLY SUMMARY
# ============================================================

def build_team_summary(snapshot):

    monitoring = snapshot[
        snapshot["week"]
        >= MONITORING_START_WEEK
    ].copy()

    counts = (
        monitoring
        .groupby(
            [
                "week",
                "snapshot_date",
                "monitoring_status"
            ]
        )
        .size()
        .unstack(
            fill_value=0
        )
        .reset_index()
    )

    expected_statuses = [
        "Ready",
        "Monitor",
        "Underexposed",
    ]

    for status in expected_statuses:

        if status not in counts.columns:
            counts[status] = 0

    counts["total_players"] = (
        counts[
            expected_statuses
        ].sum(axis=1)
    )

    counts["ready_pct"] = (
        counts["Ready"]
        / counts["total_players"]
        * 100
    ).round(1)

    counts["monitor_pct"] = (
        counts["Monitor"]
        / counts["total_players"]
        * 100
    ).round(1)

    counts["underexposed_pct"] = (
        counts["Underexposed"]
        / counts["total_players"]
        * 100
    ).round(1)

    return counts


# ============================================================
# QA / STORY CHECKS
# ============================================================

def print_story_checks(snapshot):

    print("")
    print("=" * 70)
    print("STORYLINE QUALITY CHECK")
    print("=" * 70)

    cases = [
        ("P18", [5, 6]),
        ("P07", [7]),
        ("P22", [4, 5, 6]),
    ]

    columns = [
        "week",
        "player_id",
        "position",
        "sprint_vs_baseline",
        "hsr_vs_baseline",
        "peak_training_pct_vmax",
        "load_vs_baseline",
        "md1_wellness",
        "wellness_delta",
        "preparation_alignment",
        "training_context",
        "monitoring_status",
        "monitoring_reasons",
    ]

    for player_id, weeks in cases:

        print("")
        print(
            f"--- {player_id} ---"
        )

        check = snapshot[
            (
                snapshot["player_id"]
                == player_id
            )
            & (
                snapshot["week"]
                .isin(weeks)
            )
        ][columns]

        print(
            check.to_string(
                index=False
            )
        )

    print("")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print("")
    print("=" * 70)
    print("MATCH READY — PERFORMANCE ENGINE")
    print("=" * 70)

    sessions, players, benchmarks = (
        load_data()
    )

    # --------------------------------------------------------
    # Daily calculations
    # --------------------------------------------------------

    daily = add_rolling_metrics(
        sessions
    )

    daily = add_speed_exposure_recency(
        daily
    )

    # --------------------------------------------------------
    # Weekly MD-1 snapshots
    # --------------------------------------------------------

    snapshots = (
        build_player_snapshots(
            daily,
            players
        )
    )

    # --------------------------------------------------------
    # Team summary
    # --------------------------------------------------------

    team_summary = (
        build_team_summary(
            snapshots
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    daily.to_csv(
        PROCESSED_DIR
        / "daily_metrics.csv",
        index=False
    )

    snapshots.to_csv(
        PROCESSED_DIR
        / "player_weekly_snapshots.csv",
        index=False
    )

    team_summary.to_csv(
        PROCESSED_DIR
        / "team_weekly_summary.csv",
        index=False
    )

    print("")
    print(
        f"Daily rows: {len(daily)}"
    )

    print(
        f"Weekly snapshots: {len(snapshots)}"
    )

    print(
        f"Saved to: {PROCESSED_DIR}"
    )

    print_story_checks(
        snapshots
    )

    print("")
    print("FILES CREATED")
    print(
        " - daily_metrics.csv"
    )
    print(
        " - player_weekly_snapshots.csv"
    )
    print(
        " - team_weekly_summary.csv"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()