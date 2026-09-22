from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Match Ready?",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REAL_DIR = PROJECT_ROOT / "data" / "real"


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
WHITE = "#FFFFFF"
PURPLE = "#B794F4"

STATUS_COLORS = {
    "Ready": READY,
    "Monitor": MONITOR,
    "Underexposed": UNDER,
    "Baseline": "#718096",
}

POSITION_LABELS = {
    "CB": "Centre Back",
    "FB": "Full Back",
    "CM": "Central Midfielder",
    "W": "Winger",
    "ST": "Striker",
}

STORY_WEEK = 5
STORY_PLAYER = "P18"


# ============================================================
# HTML RENDERER
# ============================================================

def render_html(content):
    """Render custom HTML without Markdown turning it into code."""
    html = dedent(content).strip()

    if hasattr(st, "html"):
        st.html(html)
    else:
        # Older Streamlit fallback: strip blank lines / indentation so
        # Markdown cannot reinterpret nested HTML as code blocks.
        compact = "\n".join(
            line.strip()
            for line in html.splitlines()
            if line.strip()
        )
        st.markdown(compact, unsafe_allow_html=True)


# ============================================================
# CSS
# ============================================================

render_html(
    f"""
    <style>
    .stApp {{ background:{BG}; color:{TEXT}; }}
    .block-container {{ padding-top:1.6rem; padding-bottom:4rem; max-width:1480px; }}

    section[data-testid="stSidebar"] {{
        background:#090D12;
        border-right:1px solid {GRID};
    }}

    h1, h2, h3 {{ color:{TEXT}; font-family:Arial, sans-serif; }}

    .mr-hero {{ padding:8px 0 16px 0; }}
    .mr-eyebrow {{
        color:{ACCENT}; font-size:11px; letter-spacing:.14em;
        font-weight:800; margin-bottom:8px;
    }}
    .mr-title {{
        color:{TEXT}; font-size:44px; line-height:1.0; font-weight:850;
        margin-bottom:10px;
    }}
    .mr-subtitle {{
        color:{MUTED}; font-size:15px; max-width:870px; line-height:1.55;
    }}

    .mr-panel {{
        background:{PANEL}; border:1px solid {GRID}; border-radius:15px;
        padding:18px 20px; margin-bottom:14px;
    }}

    .mr-soft-panel {{
        background:{PANEL_ALT}; border:1px solid {GRID}; border-radius:15px;
        padding:18px 20px; margin-bottom:14px;
    }}

    .mr-kpi {{
        background:{PANEL}; border:1px solid {GRID}; border-radius:14px;
        padding:17px 19px; min-height:118px;
    }}
    .mr-kpi-label {{
        color:{MUTED}; font-size:10px; letter-spacing:.09em;
        font-weight:800; margin-bottom:9px;
    }}
    .mr-kpi-value {{ color:{TEXT}; font-size:33px; line-height:1; font-weight:800; }}
    .mr-kpi-sub {{ color:{MUTED}; font-size:11px; margin-top:10px; line-height:1.35; }}

    .mr-section-title {{
        color:{TEXT}; font-size:20px; font-weight:750; margin-top:16px; margin-bottom:3px;
    }}
    .mr-section-subtitle {{ color:{MUTED}; font-size:12px; margin-bottom:13px; }}

    .mr-badge {{
        display:inline-block; padding:5px 10px; border-radius:999px;
        font-size:10px; font-weight:800; letter-spacing:.06em;
        vertical-align:middle;
    }}

    .mr-context-badge {{
        display:inline-block; padding:5px 9px; border-radius:999px;
        font-size:10px; font-weight:700; color:{TEXT};
        background:{PURPLE}1A; border:1px solid {PURPLE}55;
        vertical-align:middle;
    }}

    .mr-priority {{
        background:{PANEL}; border:1px solid {GRID}; border-radius:14px;
        padding:15px 17px; min-height:145px;
    }}
    .mr-priority-label {{ color:{MUTED}; font-size:10px; font-weight:800; letter-spacing:.08em; }}
    .mr-priority-name {{ color:{TEXT}; font-size:17px; font-weight:750; margin:7px 0 6px 0; }}
    .mr-priority-reason {{ color:{MUTED}; font-size:11px; line-height:1.45; margin-top:10px; }}

    .mr-player-card {{
        background:linear-gradient(145deg, {PANEL_ALT}, {PANEL});
        border:1px solid {GRID}; border-radius:17px; padding:22px;
        min-height:235px;
    }}
    .mr-player-id {{ color:{MUTED}; font-size:10px; letter-spacing:.10em; font-weight:800; }}
    .mr-player-name {{ color:{TEXT}; font-size:29px; font-weight:850; margin:6px 0 2px 0; }}
    .mr-player-pos {{ color:{MUTED}; font-size:13px; margin-bottom:17px; }}
    .mr-reference-grid {{
        display:grid; grid-template-columns:repeat(2, 1fr); gap:10px; margin-top:16px;
    }}
    .mr-reference-item {{
        background:{BG}; border:1px solid {GRID}; border-radius:11px; padding:11px 12px;
    }}
    .mr-ref-label {{ color:{MUTED}; font-size:9px; letter-spacing:.06em; font-weight:750; }}
    .mr-ref-value {{ color:{TEXT}; font-size:17px; font-weight:750; margin-top:4px; }}

    .mr-insight {{
        background:{PANEL_ALT}; border-left:3px solid {ACCENT}; border-radius:11px;
        padding:16px 18px; color:{TEXT}; margin-bottom:15px; line-height:1.5;
    }}
    .mr-insight-title {{
        color:{MUTED}; font-size:10px; font-weight:800;
        letter-spacing:.09em; margin-bottom:7px;
    }}

    .mr-small-stat {{
        background:{PANEL}; border:1px solid {GRID}; border-radius:12px;
        padding:13px 15px; min-height:88px;
    }}
    .mr-small-stat-label {{ color:{MUTED}; font-size:9px; font-weight:800; letter-spacing:.07em; }}
    .mr-small-stat-value {{ color:{TEXT}; font-size:22px; font-weight:800; margin-top:5px; }}
    .mr-small-stat-sub {{ color:{MUTED}; font-size:10px; margin-top:4px; }}

    .mr-rule {{
        background:{PANEL}; border:1px solid {GRID}; border-radius:12px;
        padding:15px 17px; margin-bottom:10px; color:{MUTED}; font-size:12px; line-height:1.55;
    }}
    .mr-rule b {{ color:{TEXT}; }}

    .mr-disclaimer {{
        color:{MUTED}; font-size:10.5px; line-height:1.5;
        border-top:1px solid {GRID}; padding-top:15px; margin-top:28px;
    }}

    div[data-testid="stDataFrame"] {{
        border:1px solid {GRID}; border-radius:12px; overflow:hidden;
    }}
    hr {{ border-color:{GRID}; }}
    </style>
    """
)


# ============================================================
# DATA
# ============================================================

@st.cache_data
def load_data():
    sessions = pd.read_csv(RAW_DIR / "sessions.csv", parse_dates=["date"])
    players = pd.read_csv(RAW_DIR / "player_profiles.csv")
    snapshots = pd.read_csv(
        PROCESSED_DIR / "player_weekly_snapshots.csv",
        parse_dates=["snapshot_date"],
    )
    daily = pd.read_csv(PROCESSED_DIR / "daily_metrics.csv", parse_dates=["date"])
    team = pd.read_csv(
        PROCESSED_DIR / "team_weekly_summary.csv",
        parse_dates=["snapshot_date"],
    )
    real_benchmarks = pd.read_csv(
        REAL_DIR / "skillcorner_position_benchmarks.csv"
    )
    return sessions, players, snapshots, daily, team, real_benchmarks


try:
    sessions, players, snapshots, daily, team, real_benchmarks = load_data()
except FileNotFoundError:
    st.error(
        "Processed data not found. Run `python src/data_generation.py` and "
        "`python src/metrics.py` first."
    )
    st.stop()


# ============================================================
# HELPERS
# ============================================================

def apply_plot_style(fig, height=None):
    fig.update_layout(
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT, family="Arial"),
        margin=dict(l=40, r=30, t=60, b=42),
        hoverlabel=dict(bgcolor=PANEL_ALT, font_color=TEXT, bordercolor=GRID),
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig


def status_badge(status):
    color = STATUS_COLORS.get(status, MUTED)
    return (
        f'<span class="mr-badge" style="background:{color}18;color:{color};'
        f'border:1px solid {color}55;">{str(status).upper()}</span>'
    )


def context_badge(context):
    return f'<span class="mr-context-badge">{context}</span>'


def kpi_card(label, value, subtitle="", color=None):
    border = color or GRID
    render_html(
        f"""
        <div class="mr-kpi" style="border-top:3px solid {border};">
            <div class="mr-kpi-label">{label}</div>
            <div class="mr-kpi-value">{value}</div>
            <div class="mr-kpi-sub">{subtitle}</div>
        </div>
        """
    )


def small_stat(label, value, subtitle=""):
    render_html(
        f"""
        <div class="mr-small-stat">
            <div class="mr-small-stat-label">{label}</div>
            <div class="mr-small-stat-value">{value}</div>
            <div class="mr-small-stat-sub">{subtitle}</div>
        </div>
        """
    )


def section_header(title, subtitle=None):
    html = f'<div class="mr-section-title">{title}</div>'
    if subtitle:
        html += f'<div class="mr-section-subtitle">{subtitle}</div>'
    render_html(html)


def format_days(value):
    if pd.isna(value):
        return "Not observed"
    value = int(value)
    return "Today" if value == 0 else f"{value} d"


def player_interpretation(row):
    """Deterministic, transparent summary for the portfolio UI."""
    sprint = row["sprint_vs_baseline"] * 100
    hsr = row["hsr_vs_baseline"] * 100
    load = row["load_vs_baseline"] * 100
    peak = row["peak_training_pct_vmax"]

    if bool(row.get("planned_reduction", False)):
        return (
            f"Reduced exposure is expected in this {row['training_context'].lower()} scenario. "
            f"Sprint exposure is {sprint:.0f}% and HSR exposure is {hsr:.0f}% of the player's "
            "usual preparation baseline; the flag therefore needs staff context rather than an "
            "automatic intervention."
        )

    if row["monitoring_status"] == "Underexposed":
        return (
            f"Overall training load is {load:.0f}% of baseline, but sprint exposure is only "
            f"{sprint:.0f}% and peak speed reached {peak:.0f}% of Vmax. The mismatch suggests "
            "that general volume is present while the high-speed stimulus is comparatively limited."
        )

    if row["monitoring_status"] == "Monitor":
        if row["load_vs_baseline"] > 1.20:
            return (
                f"Training exposure is broadly maintained, while total session load has risen to "
                f"{load:.0f}% of the individual baseline. This is a context flag for staff review, "
                "not an injury prediction."
            )
        if row["wellness_delta"] <= -8:
            return (
                f"Physical exposure remains broadly aligned, but MD-1 wellness is "
                f"{abs(row['wellness_delta']):.0f} points below the player's baseline. "
                "The useful signal here is the disagreement between external and internal context."
            )
        return (
            f"The player is close to their normal preparation profile, but one exposure dimension "
            f"is outside the chosen monitoring range. Peak speed reached {peak:.0f}% of Vmax."
        )

    return (
        f"Sprint ({sprint:.0f}%), HSR ({hsr:.0f}%) and overall load ({load:.0f}%) are broadly "
        "consistent with the player's individual preparation profile."
    )


def priority_rank(df):
    ranked = df.copy()
    status_rank = {"Underexposed": 0, "Monitor": 1, "Ready": 3}
    ranked["_status_rank"] = ranked["monitoring_status"].map(status_rank).fillna(4)
    ranked["_planned_rank"] = ranked["planned_reduction"].astype(bool).astype(int)
    return ranked.sort_values(
        ["_planned_rank", "_status_rank", "preparation_alignment"],
        ascending=[True, True, True],
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("### MATCH READY?\n**Football Performance Monitoring**")
st.sidebar.caption("Sprint exposure · HSR · Training load · Match preparation")
st.sidebar.divider()

page = st.sidebar.radio(
    "Workspace",
    ["Squad Overview", "Player Analysis", "Real Match Demands", "Exposure Map", "Methodology"],
)

monitoring_weeks = sorted(
    snapshots.loc[snapshots["week"] >= 4, "week"].unique().tolist()
)

default_week_index = (
    monitoring_weeks.index(STORY_WEEK)
    if STORY_WEEK in monitoring_weeks
    else len(monitoring_weeks) - 1
)

selected_week = st.sidebar.selectbox(
    "Monitoring week",
    monitoring_weeks,
    index=default_week_index,
    format_func=lambda x: f"Week {x}",
)

player_options = players[["player_id", "player_name", "position"]].copy()
player_options["label"] = player_options["player_name"] + " · " + player_options["position"]
player_ids = player_options["player_id"].tolist()
default_player_index = player_ids.index(STORY_PLAYER) if STORY_PLAYER in player_ids else 0

selected_player = st.sidebar.selectbox(
    "Player",
    player_ids,
    index=default_player_index,
    format_func=lambda pid: player_options.loc[
        player_options["player_id"] == pid, "label"
    ].iloc[0],
)

st.sidebar.divider()
st.sidebar.caption("Synthetic training dataset · 24 outfield players · 8-week monitoring period")
st.sidebar.caption("Real match-demand reference · SkillCorner A-League 2024/25")
st.sidebar.caption("Weeks 1–3 = baseline acquisition · Weeks 4–8 = monitoring")
st.sidebar.caption("Portfolio project · Not a medical diagnostic tool")


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="mr-hero">
        <div class="mr-eyebrow">FOOTBALL PERFORMANCE · DATA SCIENCE</div>
        <div class="mr-title">Match Ready?</div>
        <div class="mr-subtitle">
            An interpretable football performance monitoring environment built around one practical
            question: is the player's recent exposure consistent with the physical demands we expect?
        </div>
    </div>
    """
)

week_df = snapshots[snapshots["week"] == selected_week].copy()


# ============================================================
# SQUAD OVERVIEW
# ============================================================

if page == "Squad Overview":
    section_header(
        "Squad Readiness",
        f"MD-1 monitoring snapshot · Week {selected_week} · individual baselines, not population averages",
    )

    counts = week_df["monitoring_status"].value_counts()
    ready = int(counts.get("Ready", 0))
    monitor = int(counts.get("Monitor", 0))
    under = int(counts.get("Underexposed", 0))
    actionable = int(
        ((week_df["monitoring_status"] != "Ready") & (~week_df["planned_reduction"].astype(bool))).sum()
    )
    total = len(week_df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("READY", ready, f"{ready / total * 100:.0f}% of squad", READY)
    with c2:
        kpi_card("MONITOR", monitor, "Context flag · requires interpretation", MONITOR)
    with c3:
        kpi_card("UNDEREXPOSED", under, "Exposure profile materially reduced", UNDER)
    with c4:
        kpi_card("ACTIONABLE FLAGS", actionable, "Excludes planned reduced exposure", ACCENT)

    section_header(
        "Staff Priority Queue",
        "Unexpected flags first; planned rehabilitation / reintegration is kept visible but contextualised",
    )

    flagged = week_df[week_df["monitoring_status"] != "Ready"].copy()
    ranked = priority_rank(flagged)

    if ranked.empty:
        st.success("No monitoring flags in the selected week.")
    else:
        top = ranked.head(4)
        cols = st.columns(len(top))
        for col, (_, row) in zip(cols, top.iterrows()):
            with col:
                color = STATUS_COLORS.get(row["monitoring_status"], MUTED)
                context = (
                    "PLANNED CONTEXT"
                    if bool(row["planned_reduction"])
                    else "STAFF ATTENTION"
                )
                render_html(
                    f"""
                    <div class="mr-priority" style="border-top:3px solid {color};">
                        <div class="mr-priority-label">{context}</div>
                        <div class="mr-priority-name">{row['player_name']} · {row['position']}</div>
                        {status_badge(row['monitoring_status'])}
                        <div class="mr-priority-reason">{row['monitoring_reasons']}</div>
                    </div>
                    """
                )

    planned = week_df[
        (week_df["planned_reduction"].astype(bool))
        & (week_df["monitoring_status"] != "Ready")
    ]
    if not planned.empty:
        row = planned.iloc[0]
        render_html(
            f"""
            <div class="mr-insight" style="border-left-color:{PURPLE};">
                <div class="mr-insight-title">WHY CONTEXT MATTERS</div>
                <b>{row['player_name']} · {row['position']}</b> &nbsp; {context_badge(row['training_context'])}
                <br><br>{row['context_note']}
            </div>
            """
        )

    left, right = st.columns([1.75, 1])

    with left:
        section_header(
            "Squad Monitoring Board",
            "Current week compared with each player's own baseline",
        )

        table = week_df[
            [
                "player_name",
                "position",
                "training_context",
                "hsr_vs_baseline",
                "sprint_vs_baseline",
                "peak_training_pct_vmax",
                "load_vs_baseline",
                "preparation_alignment",
                "monitoring_status",
            ]
        ].copy()

        table["HSR %"] = (table["hsr_vs_baseline"] * 100).round(0)
        table["Sprint %"] = (table["sprint_vs_baseline"] * 100).round(0)
        table["Load %"] = (table["load_vs_baseline"] * 100).round(0)
        table = table.rename(
            columns={
                "player_name": "Player",
                "position": "Pos",
                "training_context": "Context",
                "peak_training_pct_vmax": "% Vmax",
                "preparation_alignment": "Alignment",
                "monitoring_status": "Status",
            }
        )
        table = table[
            ["Player", "Pos", "Context", "HSR %", "Sprint %", "% Vmax", "Load %", "Alignment", "Status"]
        ]

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
            height=575,
            column_config={
                "HSR %": st.column_config.ProgressColumn("HSR %", min_value=0, max_value=140, format="%.0f%%"),
                "Sprint %": st.column_config.ProgressColumn("Sprint %", min_value=0, max_value=140, format="%.0f%%"),
                "Load %": st.column_config.ProgressColumn("Load %", min_value=0, max_value=140, format="%.0f%%"),
                "% Vmax": st.column_config.NumberColumn("% Vmax", format="%.0f%%"),
                "Alignment": st.column_config.NumberColumn("Alignment", format="%.0f"),
            },
        )

    with right:
        section_header("Status Distribution", "Current monitoring classification")
        status_counts = week_df["monitoring_status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Players"]

        fig = go.Figure(
            go.Pie(
                labels=status_counts["Status"],
                values=status_counts["Players"],
                hole=0.72,
                marker=dict(
                    colors=[STATUS_COLORS.get(x, MUTED) for x in status_counts["Status"]]
                ),
                textinfo="none",
                hovertemplate="%{label}<br>%{value} players<extra></extra>",
            )
        )
        fig.add_annotation(
            text=f"<b>{total}</b><br><span style='font-size:10px'>PLAYERS</span>",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(color=TEXT, size=20),
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
        )
        apply_plot_style(fig, 315)
        st.plotly_chart(fig, use_container_width=True)

        section_header("Squad Speed Context", "Median values at MD-1")
        s1, s2 = st.columns(2)
        with s1:
            small_stat(
                "PEAK SPEED",
                f"{week_df['peak_training_pct_vmax'].median():.0f}%",
                "Median % individual Vmax",
            )
        with s2:
            small_stat(
                "ALIGNMENT",
                f"{week_df['preparation_alignment'].median():.0f}/100",
                "Median preparation alignment",
            )

        s3, s4 = st.columns(2)
        with s3:
            days90 = week_df["days_since_90_pct_vmax"].dropna().median()
            small_stat("LAST >90% VMAX", format_days(days90), "Squad median recency")
        with s4:
            small_stat(
                "SPRINT EXPOSURE",
                f"{week_df['sprint_vs_baseline'].median() * 100:.0f}%",
                "Median vs individual baseline",
            )

    section_header(
        "Squad Trend",
        "Status counts across monitoring weeks; weeks 1–3 are intentionally excluded as baseline acquisition",
    )
    trend = (
        snapshots[snapshots["week"] >= 4]
        .groupby(["week", "monitoring_status"])
        .size()
        .reset_index(name="Players")
    )
    fig = px.line(
        trend,
        x="week",
        y="Players",
        color="monitoring_status",
        markers=True,
        color_discrete_map=STATUS_COLORS,
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(legend_title_text="", xaxis_title="Week", yaxis_title="Players")
    apply_plot_style(fig, 370)
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PLAYER ANALYSIS
# ============================================================

elif page == "Player Analysis":
    player_history = snapshots[snapshots["player_id"] == selected_player].copy()
    player_week = player_history[player_history["week"] == selected_week]

    if player_week.empty:
        st.warning("No snapshot available for this player/week.")
        st.stop()

    row = player_week.iloc[0]
    position_full = POSITION_LABELS.get(row["position"], row["position"])

    real_ref = real_benchmarks[
        real_benchmarks["position"] == row["position"]
    ]
    if real_ref.empty:
        st.error("No real match-demand reference is available for this position.")
        st.stop()
    real_ref = real_ref.iloc[0]

    real_match_distance = real_ref["total_distance_p50_m"]
    real_match_hsr = real_ref["hsr_p50_m"]
    real_match_sprint = real_ref["sprint_p50_m"]
    real_psv99 = real_ref["psv99_p50_kmh"]
    training_to_real_hsr = row["training_hsr_m"] / real_match_hsr
    training_to_real_sprint = row["training_sprint_m"] / real_match_sprint

    left_card, right_card = st.columns([0.78, 1.45])

    with left_card:
        render_html(
            f"""
            <div class="mr-player-card">
                <div class="mr-player-id">{row['player_id']} · WEEK {selected_week}</div>
                <div class="mr-player-name">{row['player_name']}</div>
                <div class="mr-player-pos">{position_full}</div>
                {status_badge(row['monitoring_status'])} &nbsp; {context_badge(row['training_context'])}

                <div class="mr-reference-grid">
                    <div class="mr-reference-item">
                        <div class="mr-ref-label">INDIVIDUAL VMAX</div>
                        <div class="mr-ref-value">{row['vmax_kmh']:.1f} km/h</div>
                    </div>
                    <div class="mr-reference-item">
                        <div class="mr-ref-label">REAL MATCH P50 · DISTANCE</div>
                        <div class="mr-ref-value">{real_match_distance/1000:.1f} km</div>
                    </div>
                    <div class="mr-reference-item">
                        <div class="mr-ref-label">REAL MATCH P50 · HSR</div>
                        <div class="mr-ref-value">{real_match_hsr:.0f} m</div>
                    </div>
                    <div class="mr-reference-item">
                        <div class="mr-ref-label">REAL MATCH P50 · SPRINT</div>
                        <div class="mr-ref-value">{real_match_sprint:.0f} m</div>
                    </div>
                </div>
            </div>
            """
        )

    with right_card:
        section_header(
            "Decision-Support Summary",
            "A transparent interpretation generated from the same metrics shown below",
        )
        render_html(
            f"""
            <div class="mr-insight" style="border-left-color:{STATUS_COLORS.get(row['monitoring_status'], ACCENT)};">
                <div class="mr-insight-title">WHAT CHANGED?</div>
                {player_interpretation(row)}
            </div>
            """
        )
        render_html(
            f"""
            <div class="mr-soft-panel">
                <b style="color:{TEXT};">Context note</b><br><br>
                <span style="color:{MUTED};font-size:12px;line-height:1.5;">{row['context_note']}</span>
            </div>
            """
        )

    section_header("Current Preparation", "Five dimensions to read together, not in isolation")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card(
            "SPRINT EXPOSURE",
            f"{row['sprint_vs_baseline'] * 100:.0f}%",
            "vs individual baseline",
            READY if row["sprint_vs_baseline"] >= 0.85 else MONITOR if row["sprint_vs_baseline"] >= 0.60 else UNDER,
        )
    with c2:
        kpi_card(
            "HSR EXPOSURE",
            f"{row['hsr_vs_baseline'] * 100:.0f}%",
            "vs individual baseline",
            READY if row["hsr_vs_baseline"] >= 0.80 else MONITOR if row["hsr_vs_baseline"] >= 0.60 else UNDER,
        )
    with c3:
        kpi_card(
            "PEAK SPEED",
            f"{row['peak_training_pct_vmax']:.0f}%",
            "of individual Vmax",
            READY if row["peak_training_pct_vmax"] >= 90 else MONITOR if row["peak_training_pct_vmax"] >= 85 else UNDER,
        )
    with c4:
        kpi_card("TRAINING LOAD", f"{row['load_vs_baseline'] * 100:.0f}%", "vs individual baseline", ACCENT)
    with c5:
        kpi_card("ALIGNMENT", f"{row['preparation_alignment']:.0f}", "preparation alignment · 0–100", PURPLE)

    section_header(
        "Training-to-Real-Match Reference",
        "Synthetic pre-match training exposure compared with the real SkillCorner positional P50",
    )

    dm1, dm2, dm3, dm4 = st.columns(4)
    with dm1:
        small_stat(
            "WEEKLY HSR / REAL P50",
            f"{training_to_real_hsr:.2f}×",
            f"{row['training_hsr_m']:.0f} m training · {real_match_hsr:.0f} m real positional P50",
        )
    with dm2:
        small_stat(
            "WEEKLY SPRINT / REAL P50",
            f"{training_to_real_sprint:.2f}×",
            f"{row['training_sprint_m']:.0f} m training · {real_match_sprint:.0f} m real positional P50",
        )
    with dm3:
        small_stat(
            "LAST >90% VMAX",
            format_days(row["days_since_90_pct_vmax"]),
            "Recency at MD-1 snapshot",
        )
    with dm4:
        small_stat(
            "LAST >95% VMAX",
            format_days(row["days_since_95_pct_vmax"]),
            "Recency at MD-1 snapshot",
        )

    st.caption(
        "Real reference: SkillCorner Open Data, Australian A-League 2024/25. "
        "The P50 is the median across eligible season-level player-position averages "
        "(minimum 5 matches in this portfolio processing step). Ratios are descriptive, not prescribed targets."
    )

    left, right = st.columns([1, 1.15])

    with left:
        section_header("Preparation Profile", "Current microcycle vs individual baseline")
        profile = pd.DataFrame(
            {
                "Metric": ["Sprint", "HSR", "Training Load", "Distance"],
                "Current": [
                    row["sprint_vs_baseline"] * 100,
                    row["hsr_vs_baseline"] * 100,
                    row["load_vs_baseline"] * 100,
                    row["distance_vs_baseline"] * 100,
                ],
            }
        )
        fig = go.Figure(
            go.Bar(
                x=profile["Current"],
                y=profile["Metric"],
                orientation="h",
                marker=dict(
                    color=[
                        READY if value >= 85 else MONITOR if value >= 60 else UNDER
                        for value in profile["Current"]
                    ]
                ),
                text=[f"{v:.0f}%" for v in profile["Current"]],
                textposition="outside",
                hovertemplate="%{y}: %{x:.0f}%<extra></extra>",
            )
        )
        fig.add_vline(x=100, line_dash="dash", line_color=WHITE, opacity=0.55)
        fig.update_xaxes(
            range=[0, max(135, profile["Current"].max() + 15)],
            title="Individual baseline (%)",
        )
        fig.update_layout(showlegend=False)
        apply_plot_style(fig, 390)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        section_header("Peak-Speed Exposure", "Weekly maximum training speed as % individual Vmax")
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=player_history["week"],
                y=player_history["peak_training_pct_vmax"],
                mode="lines+markers",
                line=dict(color=ACCENT, width=3),
                marker=dict(size=8, color=ACCENT),
                hovertemplate="Week %{x}<br>% Vmax: %{y:.1f}%<extra></extra>",
            )
        )
        fig.add_hrect(y0=90, y1=102, fillcolor=READY, opacity=0.04, line_width=0)
        fig.add_hrect(y0=85, y1=90, fillcolor=MONITOR, opacity=0.06, line_width=0)
        fig.add_hrect(y0=0, y1=85, fillcolor=UNDER, opacity=0.035, line_width=0)
        fig.add_hline(y=90, line_dash="dash", line_color=READY, opacity=0.55)
        fig.add_hline(y=85, line_dash="dash", line_color=MONITOR, opacity=0.55)
        fig.add_trace(
            go.Scatter(
                x=[selected_week],
                y=[row["peak_training_pct_vmax"]],
                mode="markers",
                marker=dict(
                    size=17,
                    color=STATUS_COLORS.get(row["monitoring_status"], ACCENT),
                    line=dict(color=BG, width=3),
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.update_yaxes(range=[65, 102], title="% individual Vmax")
        fig.update_xaxes(title="Week", dtick=1)
        fig.update_layout(showlegend=False)
        apply_plot_style(fig, 390)
        st.plotly_chart(fig, use_container_width=True)

    section_header("Microcycle Breakdown", "Where did high-speed exposure occur inside the week?")
    training_codes = ["MD-4", "MD-3", "MD-2", "MD-1"]
    current_daily = daily[
        (daily["player_id"] == selected_player)
        & (daily["week"] == selected_week)
        & (daily["md_code"].isin(training_codes))
    ].copy()
    current_daily["md_code"] = pd.Categorical(
        current_daily["md_code"], categories=training_codes, ordered=True
    )
    current_daily = current_daily.sort_values("md_code")

    baseline_daily = (
        daily[
            (daily["player_id"] == selected_player)
            & (daily["week"].isin([1, 2, 3]))
            & (daily["md_code"].isin(training_codes))
        ]
        .groupby("md_code", as_index=False, observed=False)
        .agg(
            baseline_sprint=("sprint_distance_m", "median"),
            baseline_hsr=("hsr_m", "median"),
            baseline_speed=("percent_vmax", "median"),
        )
    )
    micro = current_daily.merge(baseline_daily, on="md_code", how="left")

    m1, m2 = st.columns(2)
    with m1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=micro["md_code"], y=micro["baseline_sprint"], name="Baseline", marker_color=GRID))
        fig.add_trace(go.Bar(x=micro["md_code"], y=micro["sprint_distance_m"], name=f"Week {selected_week}", marker_color=ACCENT))
        fig.update_layout(title="Sprint distance", barmode="group", legend=dict(orientation="h", y=1.12))
        fig.update_yaxes(title="Metres")
        apply_plot_style(fig, 350)
        st.plotly_chart(fig, use_container_width=True)

    with m2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=micro["md_code"], y=micro["baseline_hsr"], name="Baseline", marker_color=GRID))
        fig.add_trace(go.Bar(x=micro["md_code"], y=micro["hsr_m"], name=f"Week {selected_week}", marker_color=ACCENT))
        fig.update_layout(title="High-speed running", barmode="group", legend=dict(orientation="h", y=1.12))
        fig.update_yaxes(title="Metres")
        apply_plot_style(fig, 350)
        st.plotly_chart(fig, use_container_width=True)

    section_header("Load & Wellness Context", "External exposure should not be interpreted from a single signal")
    c1, c2 = st.columns(2)

    with c1:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=player_history["week"],
                y=player_history["md1_wellness"],
                mode="lines+markers",
                name="MD-1 Wellness",
                line=dict(color=READY, width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=player_history["week"],
                y=player_history["baseline_md1_wellness"],
                mode="lines",
                name="Baseline",
                line=dict(color=MUTED, dash="dash"),
            )
        )
        fig.update_layout(title="Wellness trend", legend=dict(orientation="h", y=1.12))
        fig.update_yaxes(title="Wellness score")
        apply_plot_style(fig, 335)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=player_history["week"],
                y=player_history["load_vs_baseline"] * 100,
                marker_color=ACCENT,
                hovertemplate="Week %{x}<br>Load: %{y:.0f}%<extra></extra>",
            )
        )
        fig.add_hline(y=100, line_dash="dash", line_color=WHITE, opacity=0.5)
        fig.add_hline(y=120, line_dash="dot", line_color=MONITOR, opacity=0.55)
        fig.update_layout(title="Training load vs individual baseline", showlegend=False)
        fig.update_yaxes(title="Baseline (%)")
        apply_plot_style(fig, 335)
        st.plotly_chart(fig, use_container_width=True)



# ============================================================
# REAL MATCH DEMANDS
# ============================================================

elif page == "Real Match Demands":
    section_header(
        "Real Match-Demand Reference",
        "SkillCorner Open Data · Australian A-League 2024/25 · season-level player-position physical aggregates",
    )

    render_html(
        f"""
        <div class="mr-insight" style="border-left-color:{READY};">
            <div class="mr-insight-title">WHAT CHANGED IN V3?</div>
            Training exposure remains synthetic and reproducible, but the external match-demand
            reference is now built from real SkillCorner physical data rather than hand-set positional values.
        </div>
        """
    )

    source_left, source_right = st.columns([2.2, 0.8])
    with source_left:
        st.caption(
            "Benchmark construction keeps player-position samples with at least five matches and "
            "no failed physical quality checks. The upstream aggregate dataset is filtered by SkillCorner "
            "to performances above 60 minutes."
        )
    with source_right:
        st.link_button(
            "Open SkillCorner source ↗",
            "https://github.com/SkillCorner/opendata",
            use_container_width=True,
        )

    role = st.selectbox(
        "Position reference",
        ["CB", "FB", "CM", "W", "ST"],
        index=3,
        format_func=lambda x: f"{x} · {POSITION_LABELS.get(x, x)}",
    )
    ref = real_benchmarks[real_benchmarks["position"] == role].iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card(
            "REAL MATCH DISTANCE · P50",
            f"{ref['total_distance_p50_m']/1000:.1f} km",
            f"P25 {ref['total_distance_p25_m']/1000:.1f} · P90 {ref['total_distance_p90_m']/1000:.1f} km",
            ACCENT,
        )
    with k2:
        kpi_card(
            "REAL HSR · P50",
            f"{ref['hsr_p50_m']:.0f} m",
            f"P25 {ref['hsr_p25_m']:.0f} · P90 {ref['hsr_p90_m']:.0f} m",
            READY,
        )
    with k3:
        kpi_card(
            "REAL SPRINT · P50",
            f"{ref['sprint_p50_m']:.0f} m",
            f"P25 {ref['sprint_p25_m']:.0f} · P90 {ref['sprint_p90_m']:.0f} m",
            MONITOR,
        )
    with k4:
        kpi_card(
            "PSV-99 · P50",
            f"{ref['psv99_p50_kmh']:.1f} km/h",
            f"{int(ref['n_players'])} players · {int(ref['total_matches'])} matches",
            PURPLE,
        )

    section_header(
        "Where does the positional median sit?",
        "Real season-level player-position distributions; bars show P25–P90 and the dot shows P50",
    )
    d1, d2 = st.columns(2)

    with d1:
        fig = go.Figure()
        for _, r in real_benchmarks.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=[r["hsr_p25_m"], r["hsr_p90_m"]],
                    y=[r["position"], r["position"]],
                    mode="lines",
                    line=dict(color=GRID, width=9),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=[r["hsr_p50_m"]],
                    y=[r["position"]],
                    mode="markers",
                    marker=dict(
                        size=12,
                        color=ACCENT if r["position"] == role else READY,
                        line=dict(color=BG, width=2),
                    ),
                    hovertemplate=(
                        f"{r['position']}<br>P25 {r['hsr_p25_m']:.0f} m"
                        f"<br>P50 {r['hsr_p50_m']:.0f} m"
                        f"<br>P90 {r['hsr_p90_m']:.0f} m<extra></extra>"
                    ),
                    showlegend=False,
                )
            )
        fig.update_layout(title="High-speed running")
        fig.update_xaxes(title="Metres per eligible match performance")
        fig.update_yaxes(title="")
        apply_plot_style(fig, 390)
        st.plotly_chart(fig, use_container_width=True)

    with d2:
        fig = go.Figure()
        for _, r in real_benchmarks.iterrows():
            fig.add_trace(
                go.Scatter(
                    x=[r["sprint_p25_m"], r["sprint_p90_m"]],
                    y=[r["position"], r["position"]],
                    mode="lines",
                    line=dict(color=GRID, width=9),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=[r["sprint_p50_m"]],
                    y=[r["position"]],
                    mode="markers",
                    marker=dict(
                        size=12,
                        color=ACCENT if r["position"] == role else MONITOR,
                        line=dict(color=BG, width=2),
                    ),
                    hovertemplate=(
                        f"{r['position']}<br>P25 {r['sprint_p25_m']:.0f} m"
                        f"<br>P50 {r['sprint_p50_m']:.0f} m"
                        f"<br>P90 {r['sprint_p90_m']:.0f} m<extra></extra>"
                    ),
                    showlegend=False,
                )
            )
        fig.update_layout(title="Sprint distance")
        fig.update_xaxes(title="Metres per eligible match performance")
        fig.update_yaxes(title="")
        apply_plot_style(fig, 390)
        st.plotly_chart(fig, use_container_width=True)

    section_header(
        "How to read this layer",
        "A real external reference adds context without turning a positional average into a universal target",
    )
    render_html(
        f"""
        <div class="mr-panel">
            <b>{role} · {POSITION_LABELS.get(role, role)}</b><br><br>
            The positional P50 is a reference point, not a prescription. P25–P90 is displayed to make
            variation visible instead of hiding it behind one average. This version captures
            between-player positional variation from season aggregates. Fixture-to-fixture variability
            from raw tracking is the next analytical layer.
        </div>
        """
    )


# ============================================================
# EXPOSURE MAP
# ============================================================

elif page == "Exposure Map":
    section_header(
        "Squad Exposure Map",
        "Sprint and HSR exposure relative to each player's individual preparation baseline",
    )

    f1, f2 = st.columns(2)
    with f1:
        positions = st.multiselect(
            "Position",
            options=sorted(week_df["position"].unique()),
            default=sorted(week_df["position"].unique()),
        )
    with f2:
        statuses = st.multiselect(
            "Monitoring status",
            options=["Ready", "Monitor", "Underexposed"],
            default=["Ready", "Monitor", "Underexposed"],
        )

    map_df = week_df[
        week_df["position"].isin(positions)
        & week_df["monitoring_status"].isin(statuses)
    ].copy()

    if map_df.empty:
        st.info("No players match the selected filters.")
        st.stop()

    map_df["Sprint Exposure (%)"] = map_df["sprint_vs_baseline"] * 100
    map_df["HSR Exposure (%)"] = map_df["hsr_vs_baseline"] * 100

    fig = px.scatter(
        map_df,
        x="Sprint Exposure (%)",
        y="HSR Exposure (%)",
        color="monitoring_status",
        symbol="position",
        size="preparation_alignment",
        size_max=18,
        hover_name="player_name",
        hover_data={
            "position": True,
            "monitoring_status": True,
            "training_context": True,
            "peak_training_pct_vmax": ":.1f",
            "preparation_alignment": ":.0f",
            "Sprint Exposure (%)": ":.0f",
            "HSR Exposure (%)": ":.0f",
        },
        color_discrete_map=STATUS_COLORS,
    )
    fig.update_traces(marker=dict(line=dict(color=BG, width=1.4), opacity=0.95))
    fig.add_vrect(x0=0, x1=60, fillcolor=UNDER, opacity=0.045, line_width=0, layer="below")
    fig.add_hrect(y0=0, y1=60, fillcolor=UNDER, opacity=0.045, line_width=0, layer="below")
    fig.add_vline(x=100, line_dash="dash", line_color=WHITE, opacity=0.38)
    fig.add_hline(y=100, line_dash="dash", line_color=WHITE, opacity=0.38)

    labels = map_df[map_df["monitoring_status"] != "Ready"]
    for _, p in labels.iterrows():
        fig.add_annotation(
            x=p["Sprint Exposure (%)"],
            y=p["HSR Exposure (%)"],
            text=p["player_id"],
            showarrow=False,
            xshift=8,
            yshift=9,
            font=dict(color=TEXT, size=10),
        )

    fig.update_xaxes(
        range=[
            max(20, map_df["Sprint Exposure (%)"].min() - 15),
            max(130, map_df["Sprint Exposure (%)"].max() + 15),
        ]
    )
    fig.update_yaxes(
        range=[
            max(20, map_df["HSR Exposure (%)"].min() - 15),
            max(130, map_df["HSR Exposure (%)"].max() + 15),
        ]
    )
    fig.update_layout(legend_title_text="")
    apply_plot_style(fig, 650)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "100% = player's individual baseline. The shaded area is a visual monitoring context only, "
        "not a medical-risk zone. Bubble size reflects the preparation-alignment index."
    )

    section_header("Flag Context", "The same numerical flag can mean different things depending on the training plan")
    attention = priority_rank(map_df[map_df["monitoring_status"] != "Ready"])

    if attention.empty:
        st.success("No players require additional monitoring context in this view.")
    else:
        for _, p in attention.iterrows():
            color = STATUS_COLORS.get(p["monitoring_status"], MUTED)
            plan_label = "PLANNED REDUCTION" if bool(p["planned_reduction"]) else "UNEXPECTED / REVIEW"
            render_html(
                f"""
                <div class="mr-panel" style="border-left:3px solid {color};">
                    <b>{p['player_name']} · {p['position']}</b>
                    &nbsp; {status_badge(p['monitoring_status'])}
                    &nbsp; {context_badge(plan_label)}
                    <br><br>
                    <span style="color:{MUTED};font-size:11px;">
                        Sprint {p['sprint_vs_baseline']*100:.0f}% · HSR {p['hsr_vs_baseline']*100:.0f}% ·
                        Peak {p['peak_training_pct_vmax']:.0f}% Vmax · Alignment {p['preparation_alignment']:.0f}/100
                    </span>
                    <br><br>{p['monitoring_reasons']}
                </div>
                """
            )


# ============================================================
# METHODOLOGY
# ============================================================

elif page == "Methodology":
    section_header(
        "Methodology",
        "Transparent assumptions, hybrid synthetic/real data design and limits of interpretation",
    )

    a, b = st.columns(2)
    with a:
        render_html(
            """
            <div class="mr-panel">
                <b>1 · Hybrid data design</b><br><br>
                Training exposure is simulated for 24 outfield players across eight competitive microcycles.
                The external match-demand reference is derived from real SkillCorner A-League 2024/25
                season-level physical aggregates. Goalkeepers remain excluded because their demands
                require a different monitoring framework.
            </div>
            """
        )
        render_html(
            """
            <div class="mr-panel">
                <b>2 · Individual baselines</b><br><br>
                Weeks 1–3 establish each player's normal preparation profile. Weeks 4–8 are the
                monitoring period. Current exposure is therefore interpreted primarily against the
                player's own recent history rather than a single universal value.
            </div>
            """
        )
        render_html(
            """
            <div class="mr-panel">
                <b>3 · Real match-demand lens</b><br><br>
                Weekly synthetic training HSR and sprint distance are expressed relative to the real
                positional P50 from SkillCorner Open Data. The dashboard also exposes P25–P90 to avoid
                presenting one positional average as a universal target. These ratios are descriptive.
            </div>
            """
        )

    with b:
        render_html(
            """
            <div class="mr-panel">
                <b>4 · Preparation alignment</b><br><br>
                A 0–100 visual index combines sprint alignment (50%), HSR alignment (25%) and
                peak-speed exposure (25%). Near-baseline exposure scores highest; large deviations
                above or below baseline reduce alignment. It is an interface aid, not a validated score.
            </div>
            """
        )
        render_html(
            """
            <div class="mr-panel">
                <b>5 · Human context is explicit</b><br><br>
                P22 demonstrates a planned return-to-performance scenario. The system may still flag
                low exposure numerically, but the interface shows that the reduction is expected.
                This illustrates why monitoring data should support — not replace — staff judgement.
            </div>
            """
        )
        render_html(
            """
            <div class="mr-panel">
                <b>6 · No injury probability</b><br><br>
                Match Ready? deliberately avoids converting workload variables into a percentage
                probability of injury. It describes preparation, exposure and context rather than
                claiming a medical prediction.
            </div>
            """
        )

    section_header("Monitoring Rules", "Portfolio heuristics chosen for interpretability, not clinical cut-offs")
    render_html(
        f"""
        <div class="mr-rule"><b style="color:{UNDER};">UNDEREXPOSED</b> · sprint &lt;60% baseline, HSR &lt;60% baseline, or weekly peak speed &lt;85% Vmax.</div>
        <div class="mr-rule"><b style="color:{MONITOR};">MONITOR</b> · moderate sprint / HSR reduction, elevated or reduced overall load, materially lower wellness, or limited recent &gt;90% Vmax exposure.</div>
        <div class="mr-rule"><b style="color:{READY};">READY</b> · no current rule is triggered. This means exposure is broadly aligned with the synthetic individual baseline; it is not a medical clearance.</div>
        """
    )

    section_header("Designed Storylines", "Three deliberately different cases make the dashboard useful to explore")
    s1, s2, s3 = st.columns(3)
    with s1:
        render_html(
            f"""
            <div class="mr-priority" style="border-top:3px solid {UNDER};">
                <div class="mr-priority-label">P18 · WINGER</div>
                <div class="mr-priority-name">Unexpected speed underexposure</div>
                <div class="mr-priority-reason">General training volume remains present while sprint and near-max-speed exposure fall sharply.</div>
            </div>
            """
        )
    with s2:
        render_html(
            f"""
            <div class="mr-priority" style="border-top:3px solid {MONITOR};">
                <div class="mr-priority-label">P07 · FULL BACK</div>
                <div class="mr-priority-name">Accumulated load context</div>
                <div class="mr-priority-reason">Week 7 contains a deliberate load increase without the same underexposure pattern.</div>
            </div>
            """
        )
    with s3:
        render_html(
            f"""
            <div class="mr-priority" style="border-top:3px solid {PURPLE};">
                <div class="mr-priority-label">P22 · STRIKER</div>
                <div class="mr-priority-name">Planned reintegration</div>
                <div class="mr-priority-reason">Reduced week 4–5 exposure is intentionally contextualised as a return-to-performance scenario.</div>
            </div>
            """
        )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="mr-disclaimer">
        <b>Match Ready?</b> · Synthetic training data + SkillCorner open match-demand reference · Portfolio project.<br>
        Monitoring classifications and the preparation-alignment index are illustrative decision-support constructs.
        They are not medical diagnoses, validated injury-risk predictions or return-to-play clearances.
    </div>
    """
)
