from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

OUTPUT_DIR = PROJECT_ROOT / "assets" / "exports"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# STORY CONFIGURATION
# ============================================================

STORY_WEEK = 5

STORY_PLAYER = "P18"


# ============================================================
# VISUAL IDENTITY
# ============================================================

BG = "#0B0F14"

PANEL = "#121821"

PANEL_ALT = "#171E28"

TEXT = "#F3F6F8"

MUTED = "#8E99A8"

GRID = "#29313D"

ACCENT = "#6EA8FE"

READY = "#49D6A0"

MONITOR = "#F4C95D"

UNDER = "#FF6B6B"

BASELINE = "#718096"

WHITE = "#FFFFFF"


POSITION_MARKERS = {

    "CB": "s",

    "FB": "D",

    "CM": "o",

    "W": "^",

    "ST": "P",

}


STATUS_COLORS = {

    "Ready": READY,

    "Monitor": MONITOR,

    "Underexposed": UNDER,

    "Baseline": BASELINE,

}


plt.rcParams.update({

    "figure.facecolor": BG,

    "axes.facecolor": BG,

    "savefig.facecolor": BG,

    "font.family": "DejaVu Sans",

    "text.color": TEXT,

    "axes.labelcolor": TEXT,

    "xtick.color": MUTED,

    "ytick.color": MUTED,

    "axes.edgecolor": GRID,

    "axes.titleweight": "bold",

})


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    snapshots = pd.read_csv(
        PROCESSED_DIR
        / "player_weekly_snapshots.csv",
        parse_dates=["snapshot_date"]
    )

    daily = pd.read_csv(
        PROCESSED_DIR
        / "daily_metrics.csv",
        parse_dates=["date"]
    )

    team = pd.read_csv(
        PROCESSED_DIR
        / "team_weekly_summary.csv",
        parse_dates=["snapshot_date"]
    )

    players = pd.read_csv(
        RAW_DIR
        / "player_profiles.csv"
    )

    return (
        snapshots,
        daily,
        team,
        players
    )


# ============================================================
# HELPERS
# ============================================================

def add_panel(
    ax,
    radius=0.02,
    facecolor=PANEL
):

    patch = FancyBboxPatch(

        (0, 0),

        1,

        1,

        transform=ax.transAxes,

        boxstyle=(
            f"round,pad=0.012,"
            f"rounding_size={radius}"
        ),

        linewidth=1,

        edgecolor=GRID,

        facecolor=facecolor,

        zorder=-10,

        clip_on=False,
    )

    ax.add_patch(patch)


def remove_axes(ax):

    ax.set_xticks([])

    ax.set_yticks([])

    for spine in ax.spines.values():

        spine.set_visible(False)


def save_figure(
    fig,
    filename,
    dpi=190
):

    path = (
        OUTPUT_DIR
        / filename
    )

    fig.savefig(

        path,

        dpi=dpi,

        bbox_inches="tight",

        pad_inches=0.18,

        facecolor=BG
    )

    plt.close(fig)

    print(
        f"Saved: {path}"
    )


def pct(
    value,
    decimals=0
):

    if pd.isna(value):

        return "—"

    return (
        f"{value * 100:.{decimals}f}%"
    )


def status_color(status):

    return STATUS_COLORS.get(
        status,
        MUTED
    )


def latest_monitoring_week(
    snapshots
):

    monitoring = snapshots[
        snapshots[
            "monitoring_status"
        ] != "Baseline"
    ]

    return int(
        monitoring[
            "week"
        ].max()
    )


def resolve_story_week(
    snapshots
):

    available_weeks = (
        snapshots[
            "week"
        ]
        .unique()
    )

    if STORY_WEEK in available_weeks:

        return STORY_WEEK

    return latest_monitoring_week(
        snapshots
    )


# ============================================================
# 1. TEAM OVERVIEW
# ============================================================

def plot_team_overview(
    snapshots,
    week=None
):

    if week is None:

        week = resolve_story_week(
            snapshots
        )

    week_df = (
        snapshots[
            snapshots["week"]
            == week
        ]
        .copy()
    )

    week_df[
        "status_rank"
    ] = (
        week_df[
            "monitoring_status"
        ]
        .map({

            "Underexposed": 0,

            "Monitor": 1,

            "Ready": 2,

        })
        .fillna(3)
    )

    week_df = (
        week_df
        .sort_values(

            [
                "status_rank",
                "exposure_index",
                "player_id",
            ]
        )
    )

    counts = (
        week_df[
            "monitoring_status"
        ]
        .value_counts()
    )


    fig = plt.figure(
        figsize=(15, 10)
    )


    fig.text(

        0.055,

        0.955,

        "MATCH READY?",

        fontsize=28,

        fontweight="bold",

        color=TEXT,

        va="top"
    )


    fig.text(

        0.055,

        0.912,

        (
            "Squad physical preparation overview"
            f"  ·  MD-1  ·  Week {week}"
        ),

        fontsize=12,

        color=MUTED,

        va="top"
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    card_y = 0.79

    card_h = 0.095

    card_w = 0.205


    cards = [

        (
            "READY",
            "Ready",
            READY
        ),

        (
            "MONITOR",
            "Monitor",
            MONITOR
        ),

        (
            "UNDEREXPOSED",
            "Underexposed",
            UNDER
        ),

    ]


    for i, (
        label,
        key,
        color
    ) in enumerate(cards):

        left = (
            0.055
            + i * 0.235
        )

        ax = fig.add_axes(

            [
                left,
                card_y,
                card_w,
                card_h
            ]
        )

        add_panel(ax)

        remove_axes(ax)

        value = int(
            counts.get(
                key,
                0
            )
        )

        ax.text(

            0.07,

            0.70,

            label,

            fontsize=9,

            color=MUTED,

            transform=ax.transAxes,

            fontweight="bold"
        )

        ax.text(

            0.07,

            0.17,

            str(value),

            fontsize=27,

            color=TEXT,

            transform=ax.transAxes,

            fontweight="bold"
        )

        ax.add_patch(

            Rectangle(

                (
                    0.91,
                    0.17
                ),

                0.025,

                0.62,

                transform=ax.transAxes,

                color=color,

                lw=0
            )
        )


    # ========================================================
    # PLAYER MATRIX
    # ========================================================

    ax = fig.add_axes(

        [
            0.055,
            0.08,
            0.89,
            0.66
        ]
    )

    add_panel(ax)

    remove_axes(ax)


    headers = [

        (
            "PLAYER",
            0.04
        ),

        (
            "POS",
            0.25
        ),

        (
            "HSR",
            0.35
        ),

        (
            "SPRINT",
            0.48
        ),

        (
            "% VMAX",
            0.62
        ),

        (
            "ALIGN.",
            0.75
        ),

        (
            "STATUS",
            0.86
        ),

    ]


    for label, x in headers:

        ax.text(

            x,

            0.955,

            label,

            transform=ax.transAxes,

            fontsize=8,

            color=MUTED,

            fontweight="bold",

            va="center"
        )


    n = len(
        week_df
    )

    top = 0.91

    bottom = 0.05

    row_h = (
        top - bottom
    ) / max(
        n,
        1
    )


    for row_num, (
        _,
        row
    ) in enumerate(
        week_df.iterrows()
    ):

        y_top = (
            top
            - row_num * row_h
        )

        y_mid = (
            y_top
            - row_h / 2
        )


        if row_num % 2 == 0:

            ax.add_patch(

                Rectangle(

                    (
                        0.018,
                        y_top - row_h
                    ),

                    0.964,

                    row_h,

                    transform=ax.transAxes,

                    facecolor=PANEL_ALT,

                    edgecolor="none",

                    alpha=0.42
                )
            )


        color = status_color(
            row[
                "monitoring_status"
            ]
        )


        ax.text(

            0.04,

            y_mid,

            row[
                "player_name"
            ],

            transform=ax.transAxes,

            fontsize=8.6,

            color=TEXT,

            va="center",

            fontweight="bold"
        )


        ax.text(

            0.25,

            y_mid,

            row[
                "position"
            ],

            transform=ax.transAxes,

            fontsize=8,

            color=MUTED,

            va="center"
        )


        hsr = row[
            "hsr_vs_baseline"
        ]

        sprint = row[
            "sprint_vs_baseline"
        ]

        speed = row[
            "peak_training_pct_vmax"
        ]

        index = row[
            "exposure_index"
        ]


        ax.text(

            0.35,

            y_mid,

            pct(hsr),

            transform=ax.transAxes,

            fontsize=8.4,

            color=TEXT,

            va="center"
        )


        ax.text(

            0.48,

            y_mid,

            pct(sprint),

            transform=ax.transAxes,

            fontsize=8.4,

            color=TEXT,

            va="center"
        )


        ax.text(

            0.62,

            y_mid,

            f"{speed:.0f}%",

            transform=ax.transAxes,

            fontsize=8.4,

            color=TEXT,

            va="center"
        )


        ax.text(

            0.75,

            y_mid,

            f"{index:.0f}",

            transform=ax.transAxes,

            fontsize=8.4,

            color=TEXT,

            va="center"
        )


        ax.scatter(

            [0.86],

            [y_mid],

            s=26,

            color=color,

            transform=ax.transAxes,

            clip_on=False
        )


        ax.text(

            0.88,

            y_mid,

            row[
                "monitoring_status"
            ],

            transform=ax.transAxes,

            fontsize=8.1,

            color=color,

            va="center",

            fontweight="bold"
        )


    fig.text(

        0.055,

        0.025,

        (
            "Synthetic football performance data"
            "  ·  Status reflects preparation/exposure,"
            " not injury probability."
        ),

        fontsize=8,

        color=MUTED
    )


    save_figure(

        fig,

        "01_team_overview.png"
    )


# ============================================================
# 2. INDIVIDUAL PLAYER PROFILE
# ============================================================

def plot_player_profile(
    snapshots,
    player_id=STORY_PLAYER,
    week=STORY_WEEK
):

    player_all = snapshots[
        snapshots[
            "player_id"
        ] == player_id
    ].copy()


    current = player_all[
        player_all[
            "week"
        ] == week
    ]


    if current.empty:

        raise ValueError(

            (
                f"No snapshot for "
                f"{player_id}, week {week}"
            )
        )


    row = current.iloc[0]


    fig = plt.figure(
        figsize=(15, 8.5)
    )


    fig.text(

        0.055,

        0.95,

        (
            f'{row["player_name"].upper()}'
            f'  ·  {row["position"]}'
        ),

        fontsize=25,

        fontweight="bold",

        color=TEXT,

        va="top"
    )


    fig.text(

        0.055,

        0.91,

        "Individual physical exposure profile",

        fontsize=11.5,

        color=MUTED,

        va="top"
    )


    # ========================================================
    # STATUS BADGE
    # ========================================================

    badge_ax = fig.add_axes(

        [
            0.755,
            0.885,
            0.19,
            0.075
        ]
    )

    add_panel(
        badge_ax
    )

    remove_axes(
        badge_ax
    )


    color = status_color(
        row[
            "monitoring_status"
        ]
    )


    badge_ax.scatter(

        [0.12],

        [0.5],

        s=58,

        color=color,

        transform=badge_ax.transAxes
    )


    badge_ax.text(

        0.22,

        0.5,

        row[
            "monitoring_status"
        ].upper(),

        fontsize=11,

        color=color,

        fontweight="bold",

        transform=badge_ax.transAxes,

        va="center"
    )


    # ========================================================
    # METRIC PANEL
    # ========================================================

    ax_metrics = fig.add_axes(

        [
            0.055,
            0.16,
            0.39,
            0.64
        ]
    )


    add_panel(
        ax_metrics
    )


    remove_axes(
        ax_metrics
    )


    ax_metrics.text(

        0.07,

        0.92,

        "CURRENT vs INDIVIDUAL BASELINE",

        transform=ax_metrics.transAxes,

        fontsize=9,

        color=MUTED,

        fontweight="bold"
    )


    metrics = [

        (
            "SPRINT EXPOSURE",
            row[
                "sprint_vs_baseline"
            ]
        ),

        (
            "HSR EXPOSURE",
            row[
                "hsr_vs_baseline"
            ]
        ),

        (
            "TRAINING LOAD",
            row[
                "load_vs_baseline"
            ]
        ),

    ]


    y_positions = [

        0.72,

        0.50,

        0.28,

    ]


    for (
        label,
        value
    ), y in zip(
        metrics,
        y_positions
    ):

        ax_metrics.text(

            0.07,

            y + 0.09,

            label,

            transform=ax_metrics.transAxes,

            fontsize=8.5,

            color=TEXT,

            fontweight="bold"
        )


        ax_metrics.text(

            0.91,

            y + 0.09,

            pct(value),

            transform=ax_metrics.transAxes,

            fontsize=13,

            color=TEXT,

            fontweight="bold",

            ha="right"
        )


        # Background
        ax_metrics.add_patch(

            FancyBboxPatch(

                (
                    0.07,
                    y
                ),

                0.84,

                0.055,

                transform=ax_metrics.transAxes,

                boxstyle=(
                    "round,pad=0.005,"
                    "rounding_size=0.02"
                ),

                facecolor=GRID,

                edgecolor="none"
            )
        )


        fill_value = min(
            max(
                value,
                0
            ),
            1.25
        ) / 1.25


        if value < 0.60:

            bar_color = UNDER

        elif value < 0.85:

            bar_color = MONITOR

        else:

            bar_color = READY


        ax_metrics.add_patch(

            FancyBboxPatch(

                (
                    0.07,
                    y
                ),

                0.84
                * fill_value,

                0.055,

                transform=ax_metrics.transAxes,

                boxstyle=(
                    "round,pad=0.005,"
                    "rounding_size=0.02"
                ),

                facecolor=bar_color,

                edgecolor="none"
            )
        )


        # Individual baseline = 100%
        baseline_x = (

            0.07

            + 0.84
            * (
                1 / 1.25
            )
        )


        ax_metrics.plot(

            [
                baseline_x,
                baseline_x
            ],

            [
                y - 0.012,
                y + 0.068
            ],

            color=WHITE,

            lw=1.4,

            transform=ax_metrics.transAxes
        )


    ax_metrics.text(

        0.07,

        0.08,

        "White marker = individual baseline",

        transform=ax_metrics.transAxes,

        fontsize=7.8,

        color=MUTED
    )


    # ========================================================
    # SPEED EXPOSURE HISTORY
    # ========================================================

    ax_speed = fig.add_axes(

        [
            0.49,
            0.43,
            0.455,
            0.37
        ]
    )


    add_panel(
        ax_speed
    )


    ax_speed.set_title(

        "WEEKLY PEAK SPEED EXPOSURE",

        loc="left",

        fontsize=9,

        color=MUTED,

        pad=15
    )


    ax_speed.plot(

        player_all[
            "week"
        ],

        player_all[
            "peak_training_pct_vmax"
        ],

        marker="o",

        lw=2.4,

        color=ACCENT
    )


    ax_speed.axhline(

        90,

        color=READY,

        lw=1,

        alpha=0.55,

        ls="--"
    )


    ax_speed.axhline(

        85,

        color=MONITOR,

        lw=1,

        alpha=0.55,

        ls="--"
    )


    ax_speed.scatter(

        [week],

        [
            row[
                "peak_training_pct_vmax"
            ]
        ],

        s=100,

        color=color,

        edgecolor=BG,

        linewidth=2,

        zorder=5
    )


    ax_speed.set_ylim(
        70,
        101
    )


    ax_speed.set_xlim(

        player_all[
            "week"
        ].min() - 0.3,

        player_all[
            "week"
        ].max() + 0.3
    )


    ax_speed.set_ylabel(

        "% individual Vmax",

        fontsize=8.5,

        color=MUTED
    )


    ax_speed.set_xlabel(

        "Week",

        fontsize=8.5,

        color=MUTED
    )


    ax_speed.grid(

        axis="y",

        color=GRID,

        alpha=0.65,

        linewidth=0.7
    )


    ax_speed.spines[
        [
            "top",
            "right"
        ]
    ].set_visible(False)


    # ========================================================
    # WHY FLAGGED?
    # ========================================================

    ax_reason = fig.add_axes(

        [
            0.49,
            0.16,
            0.455,
            0.21
        ]
    )


    add_panel(

        ax_reason,

        facecolor=PANEL_ALT
    )


    remove_axes(
        ax_reason
    )


    ax_reason.text(

        0.05,

        0.78,

        "WHY IS THIS PLAYER FLAGGED?",

        transform=ax_reason.transAxes,

        fontsize=8.5,

        color=MUTED,

        fontweight="bold"
    )


    reasons = str(
        row[
            "monitoring_reasons"
        ]
    ).split(
        "; "
    )


    wrapped = "\n".join(

        f"• {reason}"

        for reason
        in reasons[:4]
    )


    ax_reason.text(

        0.05,

        0.56,

        wrapped,

        transform=ax_reason.transAxes,

        fontsize=10,

        color=TEXT,

        va="top",

        linespacing=1.55
    )


    fig.text(

        0.055,

        0.075,

        (
            f'Week {week}'
            f' · Preparation alignment '
            f'{row["exposure_index"]:.0f}/100'
            ' · Synthetic data'
        ),

        fontsize=8.5,

        color=MUTED
    )


    save_figure(

        fig,

        "02_player_exposure_profile.png"
    )


# ============================================================
# 3. SQUAD EXPOSURE MAP
# ============================================================

def plot_squad_exposure_map(
    snapshots,
    week=None
):

    if week is None:

        week = resolve_story_week(
            snapshots
        )


    data = snapshots[
        snapshots[
            "week"
        ] == week
    ].copy()


    data[
        "sprint_pct"
    ] = (
        data[
            "sprint_vs_baseline"
        ]
        * 100
    )


    data[
        "hsr_pct"
    ] = (
        data[
            "hsr_vs_baseline"
        ]
        * 100
    )


    fig, ax = plt.subplots(

        figsize=(
            13.5,
            8.5
        )
    )


    fig.subplots_adjust(

        left=0.10,

        right=0.80,

        top=0.84,

        bottom=0.14
    )


    fig.text(

        0.08,

        0.94,

        "SQUAD EXPOSURE MAP",

        fontsize=25,

        fontweight="bold",

        color=TEXT
    )


    fig.text(

        0.08,

        0.895,

        (
            "Current microcycle vs each player's "
            f"individual baseline  ·  Week {week}"
        ),

        fontsize=11,

        color=MUTED
    )


    # ========================================================
    # CONTEXT ZONES
    # ========================================================

    ax.axvspan(

        0,

        60,

        color=UNDER,

        alpha=0.07
    )


    ax.axhspan(

        0,

        60,

        color=UNDER,

        alpha=0.07
    )


    ax.axvspan(

        60,

        85,

        color=MONITOR,

        alpha=0.035
    )


    ax.axhspan(

        60,

        80,

        color=MONITOR,

        alpha=0.035
    )


    ax.axvline(

        100,

        color=WHITE,

        alpha=0.32,

        lw=1,

        ls="--"
    )


    ax.axhline(

        100,

        color=WHITE,

        alpha=0.32,

        lw=1,

        ls="--"
    )


    # ========================================================
    # PLAYERS
    # ========================================================

    for position in POSITION_MARKERS:

        subset = data[
            data[
                "position"
            ] == position
        ]


        for status in [

            "Ready",

            "Monitor",

            "Underexposed"

        ]:

            current = subset[
                subset[
                    "monitoring_status"
                ] == status
            ]


            if current.empty:

                continue


            ax.scatter(

                current[
                    "sprint_pct"
                ],

                current[
                    "hsr_pct"
                ],

                s=95,

                marker=POSITION_MARKERS[
                    position
                ],

                color=status_color(
                    status
                ),

                edgecolor=BG,

                linewidth=1.3,

                alpha=0.93,

                zorder=3
            )


    # Label only players that need attention
    labels = data[
        data[
            "monitoring_status"
        ].isin(
            [
                "Monitor",
                "Underexposed"
            ]
        )
    ]


    for _, row in labels.iterrows():

        ax.annotate(

            row[
                "player_id"
            ],

            (
                row[
                    "sprint_pct"
                ],

                row[
                    "hsr_pct"
                ]
            ),

            xytext=(6, 6),

            textcoords="offset points",

            fontsize=7.5,

            color=TEXT,

            fontweight="bold"
        )


    ax.set_xlim(

        max(

            25,

            data[
                "sprint_pct"
            ].min() - 12
        ),

        max(

            125,

            data[
                "sprint_pct"
            ].max() + 12
        )
    )


    ax.set_ylim(

        max(

            25,

            data[
                "hsr_pct"
            ].min() - 12
        ),

        max(

            125,

            data[
                "hsr_pct"
            ].max() + 12
        )
    )


    ax.set_xlabel(

        "Sprint exposure vs baseline (%)",

        fontsize=10,

        color=MUTED,

        labelpad=12
    )


    ax.set_ylabel(

        "HSR exposure vs baseline (%)",

        fontsize=10,

        color=MUTED,

        labelpad=12
    )


    ax.grid(

        color=GRID,

        alpha=0.55,

        linewidth=0.7
    )


    ax.spines[
        [
            "top",
            "right"
        ]
    ].set_visible(False)


    # ========================================================
    # POSITION LEGEND
    # ========================================================

    position_handles = [

        Line2D(

            [0],

            [0],

            marker=marker,

            color="none",

            markerfacecolor=MUTED,

            markeredgecolor=MUTED,

            markersize=8,

            label=position
        )

        for position, marker
        in POSITION_MARKERS.items()
    ]


    legend1 = ax.legend(

        handles=position_handles,

        title="POSITION",

        bbox_to_anchor=(
            1.03,
            1.0
        ),

        loc="upper left",

        frameon=False,

        labelcolor=TEXT,

        title_fontsize=8,

        fontsize=8
    )


    ax.add_artist(
        legend1
    )


    status_handles = [

        Line2D(

            [0],

            [0],

            marker="o",

            color="none",

            markerfacecolor=color,

            markersize=8,

            label=status
        )

        for status, color
        in [

            (
                "Ready",
                READY
            ),

            (
                "Monitor",
                MONITOR
            ),

            (
                "Underexposed",
                UNDER
            ),

        ]
    ]


    ax.legend(

        handles=status_handles,

        title="STATUS",

        bbox_to_anchor=(
            1.03,
            0.62
        ),

        loc="upper left",

        frameon=False,

        labelcolor=TEXT,

        title_fontsize=8,

        fontsize=8
    )


    fig.text(

        0.08,

        0.055,

        (
            "100% = player's individual baseline. "
            "Shaded areas are monitoring context, "
            "not medical risk zones."
        ),

        fontsize=8,

        color=MUTED
    )


    save_figure(

        fig,

        "03_squad_exposure_map.png"
    )


# ============================================================
# 4. MICRO-CYCLE COMPARISON
# ============================================================

def plot_microcycle_comparison(
    daily,
    player_id=STORY_PLAYER,
    week=STORY_WEEK
):

    player = daily[
        daily[
            "player_id"
        ] == player_id
    ].copy()


    training_codes = [

        "MD-4",

        "MD-3",

        "MD-2",

        "MD-1",

    ]


    baseline = (

        player[

            (
                player[
                    "week"
                ].isin(
                    [1, 2, 3]
                )
            )

            &

            (
                player[
                    "md_code"
                ].isin(
                    training_codes
                )
            )
        ]

        .groupby(
            "md_code",
            as_index=False
        )

        .agg(

            baseline_sprint=(
                "sprint_distance_m",
                "median"
            ),

            baseline_hsr=(
                "hsr_m",
                "median"
            ),

            baseline_pct_vmax=(
                "percent_vmax",
                "median"
            ),
        )
    )


    current = (

        player[

            (
                player[
                    "week"
                ] == week
            )

            &

            (
                player[
                    "md_code"
                ].isin(
                    training_codes
                )
            )
        ][

            [
                "md_code",
                "sprint_distance_m",
                "hsr_m",
                "percent_vmax",
            ]
        ]

        .copy()
    )


    merged = baseline.merge(

        current,

        on="md_code",

        how="inner"
    )


    order = {

        code: i

        for i, code
        in enumerate(
            training_codes
        )
    }


    merged[
        "order"
    ] = (
        merged[
            "md_code"
        ]
        .map(
            order
        )
    )


    merged = merged.sort_values(
        "order"
    )


    fig = plt.figure(
        figsize=(14, 8.2)
    )


    fig.text(

        0.06,

        0.94,

        "MICROCYCLE EXPOSURE",

        fontsize=25,

        fontweight="bold",

        color=TEXT
    )


    player_name = (
        player[
            "player_name"
        ]
        .iloc[0]
    )


    position = (
        player[
            "position"
        ]
        .iloc[0]
    )


    fig.text(

        0.06,

        0.897,

        (
            f"{player_name} · {position}"
            f" · Week {week}"
            " vs baseline weeks 1–3"
        ),

        fontsize=11,

        color=MUTED
    )


    x = np.arange(
        len(
            merged
        )
    )


    width = 0.33


    # ========================================================
    # SPRINT DISTANCE
    # ========================================================

    ax1 = fig.add_axes(

        [
            0.07,
            0.49,
            0.86,
            0.31
        ]
    )


    ax1.bar(

        x - width / 2,

        merged[
            "baseline_sprint"
        ],

        width,

        label="Baseline",

        color=GRID
    )


    ax1.bar(

        x + width / 2,

        merged[
            "sprint_distance_m"
        ],

        width,

        label=f"Week {week}",

        color=ACCENT
    )


    ax1.set_title(

        "SPRINT DISTANCE BY TRAINING DAY",

        loc="left",

        fontsize=9,

        color=MUTED,

        pad=12
    )


    ax1.set_ylabel(

        "metres",

        fontsize=8.5,

        color=MUTED
    )


    ax1.set_xticks(

        x,

        merged[
            "md_code"
        ]
    )


    ax1.grid(

        axis="y",

        color=GRID,

        alpha=0.55,

        linewidth=0.7
    )


    ax1.legend(

        frameon=False,

        fontsize=8,

        labelcolor=TEXT,

        loc="upper right"
    )


    ax1.spines[
        [
            "top",
            "right"
        ]
    ].set_visible(False)


    # ========================================================
    # PEAK SPEED
    # ========================================================

    ax2 = fig.add_axes(

        [
            0.07,
            0.12,
            0.86,
            0.25
        ]
    )


    ax2.plot(

        x,

        merged[
            "baseline_pct_vmax"
        ],

        marker="o",

        lw=2.2,

        color=GRID,

        label="Baseline"
    )


    ax2.plot(

        x,

        merged[
            "percent_vmax"
        ],

        marker="o",

        lw=2.5,

        color=ACCENT,

        label=f"Week {week}"
    )


    ax2.axhline(

        90,

        color=READY,

        ls="--",

        lw=1,

        alpha=0.55
    )


    ax2.axhline(

        85,

        color=MONITOR,

        ls="--",

        lw=1,

        alpha=0.55
    )


    ax2.set_title(

        "PEAK SPEED EXPOSURE",

        loc="left",

        fontsize=9,

        color=MUTED,

        pad=12
    )


    ax2.set_ylabel(

        "% Vmax",

        fontsize=8.5,

        color=MUTED
    )


    ax2.set_xticks(

        x,

        merged[
            "md_code"
        ]
    )


    ax2.set_ylim(
        55,
        100
    )


    ax2.grid(

        axis="y",

        color=GRID,

        alpha=0.55,

        linewidth=0.7
    )


    ax2.spines[
        [
            "top",
            "right"
        ]
    ].set_visible(False)


    fig.text(

        0.07,

        0.045,

        (
            "This view isolates where exposure changed "
            "within the training week rather than relying "
            "on weekly totals alone."
        ),

        fontsize=8,

        color=MUTED
    )


    save_figure(

        fig,

        "04_microcycle_exposure.png"
    )


# ============================================================
# 5. LINKEDIN FEATURED COVER
# ============================================================

def plot_featured_cover(
    snapshots,
    week=None
):

    if week is None:

        week = resolve_story_week(
            snapshots
        )


    data = snapshots[
        snapshots[
            "week"
        ] == week
    ]


    counts = (
        data[
            "monitoring_status"
        ]
        .value_counts()
    )


    # Exact LinkedIn-style landscape ratio
    fig = plt.figure(

        figsize=(
            12,
            6.27
        ),

        dpi=100
    )


    ax_bg = fig.add_axes(
        [
            0,
            0,
            1,
            1
        ]
    )


    remove_axes(
        ax_bg
    )


    ax_bg.add_patch(

        Rectangle(

            (
                0.72,
                0
            ),

            0.28,

            1,

            transform=ax_bg.transAxes,

            color=PANEL
        )
    )


    ax_bg.add_patch(

        Rectangle(

            (
                0.72,
                0
            ),

            0.006,

            1,

            transform=ax_bg.transAxes,

            color=ACCENT
        )
    )


    fig.text(

        0.07,

        0.78,

        "MATCH READY?",

        fontsize=31,

        fontweight="bold",

        color=TEXT
    )


    fig.text(

        0.07,

        0.68,

        "Sprint Exposure & Physical Readiness",

        fontsize=16,

        fontweight="bold",

        color=TEXT
    )


    fig.text(

        0.07,

        0.61,

        "Football performance monitoring project",

        fontsize=10.5,

        color=MUTED
    )


    fig.text(

        0.07,

        0.43,

        "TRAINING",

        fontsize=9,

        color=MUTED,

        fontweight="bold"
    )


    fig.text(

        0.07,

        0.37,

        "→",

        fontsize=20,

        color=ACCENT,

        fontweight="bold"
    )


    fig.text(

        0.12,

        0.37,

        "EXPOSURE",

        fontsize=13,

        color=TEXT,

        fontweight="bold"
    )


    fig.text(

        0.28,

        0.37,

        "→",

        fontsize=20,

        color=ACCENT,

        fontweight="bold"
    )


    fig.text(

        0.33,

        0.37,

        "MATCH DEMANDS",

        fontsize=13,

        color=TEXT,

        fontweight="bold"
    )


    fig.text(

        0.07,

        0.17,

        (
            "Python  ·  Sport Science"
            "  ·  Data Visualisation"
        ),

        fontsize=9.5,

        color=MUTED
    )


    # ========================================================
    # RIGHT KPI COLUMN
    # ========================================================

    y = 0.74


    for (
        label,
        status,
        color
    ) in [

        (
            "READY",
            "Ready",
            READY
        ),

        (
            "MONITOR",
            "Monitor",
            MONITOR
        ),

        (
            "UNDEREXPOSED",
            "Underexposed",
            UNDER
        ),

    ]:

        fig.text(

            0.79,

            y,

            (
                f"{int(counts.get(status, 0)):02d}"
            ),

            fontsize=24,

            fontweight="bold",

            color=TEXT
        )


        fig.text(

            0.79,

            y - 0.055,

            label,

            fontsize=8,

            color=color,

            fontweight="bold"
        )


        y -= 0.22


    cover_path = (

        OUTPUT_DIR
        / "05_featured_cover.png"
    )


    fig.savefig(

        cover_path,

        dpi=100,

        facecolor=BG
    )


    plt.close(
        fig
    )


    print(
        f"Saved: {cover_path}"
    )


# ============================================================
# 6. TRAINING-TO-MATCH DEMAND STORY VISUAL
# ============================================================

def plot_match_demand_lens(
    snapshots,
    player_id=STORY_PLAYER,
    week=STORY_WEEK,
):

    current = snapshots[
        (snapshots["player_id"] == player_id)
        & (snapshots["week"] == week)
    ]

    if current.empty:
        raise ValueError(
            f"No snapshot for {player_id}, week {week}"
        )

    row = current.iloc[0]

    fig = plt.figure(
        figsize=(14, 8.2)
    )

    fig.text(
        0.06,
        0.94,
        "TRAINING → MATCH DEMAND",
        fontsize=25,
        fontweight="bold",
        color=TEXT,
    )

    fig.text(
        0.06,
        0.895,
        (
            f'{row["player_name"]} · {row["position"]}'
            f' · Week {week} · pre-match training exposure'
        ),
        fontsize=11,
        color=MUTED,
    )

    # --------------------------------------------------------
    # Main ratio chart
    # --------------------------------------------------------

    ax = fig.add_axes([
        0.07,
        0.29,
        0.58,
        0.48,
    ])

    ratios = [
        row["training_to_match_hsr"],
        row["training_to_match_sprint"],
    ]

    labels = [
        "HSR",
        "SPRINT",
    ]

    y = np.arange(len(labels))

    ax.barh(
        y,
        ratios,
        height=0.42,
        color=[ACCENT, UNDER],
    )

    ax.axvline(
        1.0,
        color=WHITE,
        lw=1.4,
        ls="--",
        alpha=0.70,
    )

    ax.text(
        1.0,
        1.42,
        "1.00× typical match demand",
        fontsize=8,
        color=MUTED,
        ha="center",
    )

    for i, value in enumerate(ratios):
        ax.text(
            value + 0.035,
            i,
            f"{value:.2f}×",
            va="center",
            fontsize=14,
            color=TEXT,
            fontweight="bold",
        )

    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(1.65, max(ratios) + 0.25))
    ax.set_xlabel(
        "Weekly training exposure / individual one-match demand",
        fontsize=9,
        color=MUTED,
        labelpad=12,
    )
    ax.grid(
        axis="x",
        color=GRID,
        alpha=0.55,
        linewidth=0.7,
    )
    ax.spines[["top", "right", "left"]].set_visible(False)

    # --------------------------------------------------------
    # Right insight panel
    # --------------------------------------------------------

    ax2 = fig.add_axes([
        0.70,
        0.29,
        0.24,
        0.48,
    ])

    add_panel(
        ax2,
        facecolor=PANEL_ALT,
    )
    remove_axes(ax2)

    ax2.text(
        0.08,
        0.88,
        "KEY INTERPRETATION",
        transform=ax2.transAxes,
        fontsize=8.5,
        color=MUTED,
        fontweight="bold",
    )

    ax2.text(
        0.08,
        0.72,
        "HSR VOLUME IS PRESENT.",
        transform=ax2.transAxes,
        fontsize=14,
        color=TEXT,
        fontweight="bold",
    )

    ax2.text(
        0.08,
        0.61,
        "SPRINT EXPOSURE\nIS NOT.",
        transform=ax2.transAxes,
        fontsize=14,
        color=UNDER,
        fontweight="bold",
        linespacing=1.3,
    )

    ax2.text(
        0.08,
        0.39,
        (
            f'Peak speed: {row["peak_training_pct_vmax"]:.0f}% Vmax\n'
            f'Sprint vs baseline: {row["sprint_vs_baseline"]*100:.0f}%\n'
            f'HSR vs baseline: {row["hsr_vs_baseline"]*100:.0f}%'
        ),
        transform=ax2.transAxes,
        fontsize=10,
        color=MUTED,
        linespacing=1.65,
    )

    ax2.text(
        0.08,
        0.12,
        row["monitoring_status"].upper(),
        transform=ax2.transAxes,
        fontsize=12,
        color=status_color(row["monitoring_status"]),
        fontweight="bold",
    )

    fig.text(
        0.07,
        0.13,
        (
            "The ratios are descriptive comparisons, not prescribed targets. "
            "Synthetic football performance data."
        ),
        fontsize=8,
        color=MUTED,
    )

    save_figure(
        fig,
        "06_training_to_match_demand.png",
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("")

    print(
        "=" * 65
    )

    print(
        "MATCH READY — VISUAL EXPORT"
    )

    print(
        "=" * 65
    )


    (
        snapshots,
        daily,
        team,
        players

    ) = load_data()


    plot_team_overview(

        snapshots,

        week=STORY_WEEK
    )


    plot_player_profile(

        snapshots,

        player_id=STORY_PLAYER,

        week=STORY_WEEK
    )


    plot_squad_exposure_map(

        snapshots,

        week=STORY_WEEK
    )


    plot_microcycle_comparison(

        daily,

        player_id=STORY_PLAYER,

        week=STORY_WEEK
    )


    plot_featured_cover(

        snapshots,

        week=STORY_WEEK
    )


    plot_match_demand_lens(

        snapshots,

        player_id=STORY_PLAYER,

        week=STORY_WEEK
    )


    print("")

    print(

        "All visuals exported to: "
        f"{OUTPUT_DIR}"
    )

    print(
        "=" * 65
    )


if __name__ == "__main__":

    main()