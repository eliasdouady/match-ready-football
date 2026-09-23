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

STATUS_LABELS = {
    "Ready": "Aligned",
    "Monitor": "Review",
    "Underexposed": "Low speed exposure",
    "Baseline": "Baseline",
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

    .mr-report-kpi {{
        background:{PANEL}; border:1px solid {GRID}; border-radius:13px;
        padding:13px 16px; min-height:92px;
    }}
    .mr-report-kpi-label {{
        color:{MUTED}; font-size:9px; letter-spacing:.09em;
        font-weight:800; margin-bottom:7px;
    }}
    .mr-report-kpi-value {{
        color:{TEXT}; font-size:29px; line-height:1; font-weight:800;
    }}
    .mr-report-kpi-sub {{
        color:{MUTED}; font-size:10px; margin-top:8px; line-height:1.3;
    }}
    .mr-report-title {{
        color:{TEXT}; font-size:34px; line-height:1; font-weight:850;
    }}
    .mr-report-meta {{
        color:{MUTED}; font-size:11px; margin-top:7px;
    }}
    .mr-report-section-title {{
        color:{TEXT}; font-size:18px; font-weight:760; margin-top:13px; margin-bottom:2px;
    }}
    .mr-report-section-subtitle {{
        color:{MUTED}; font-size:10.5px; margin-bottom:10px;
    }}
    .mr-report-insight {{
        background:{PANEL_ALT}; border-left:3px solid {ACCENT}; border-radius:10px;
        padding:13px 16px; color:{TEXT}; margin:12px 0 13px 0; line-height:1.45;
    }}
    .mr-report-note {{
        color:{MUTED}; font-size:9.5px; line-height:1.45;
        margin-top:8px; padding-top:9px; border-top:1px solid {GRID};
    }}
    .mr-context-strip {{
        display:grid; grid-template-columns:repeat(3, 1fr); gap:8px;
        margin:8px 0 10px 0;
    }}
    .mr-context-chip {{
        background:{PANEL}; border:1px solid {GRID}; border-radius:9px;
        padding:8px 10px;
    }}
    .mr-context-chip-label {{
        color:{MUTED}; font-size:8px; font-weight:800; letter-spacing:.08em;
        margin-bottom:3px;
    }}
    .mr-context-chip-value {{
        color:{TEXT}; font-size:11px; font-weight:700; line-height:1.25;
    }}
    .mr-staff-check {{
        color:{MUTED}; font-size:10.5px; line-height:1.45;
        margin:-2px 0 12px 0;
    }}
    .mr-staff-check b {{ color:{TEXT}; }}

    .mr-role-card {{
        background:linear-gradient(145deg, {PANEL_ALT}, {PANEL});
        border:1px solid {GRID}; border-radius:13px;
        padding:11px 13px; min-height:118px;
        display:flex; gap:13px; align-items:center;
    }}
    .mr-role-copy {{ min-width:126px; }}
    .mr-role-eyebrow {{
        color:{MUTED}; font-size:8.5px; letter-spacing:.11em;
        font-weight:800; margin-bottom:5px;
    }}
    .mr-role-name {{
        color:{TEXT}; font-size:16px; font-weight:800; line-height:1.1;
    }}
    .mr-role-sub {{
        color:{MUTED}; font-size:9.5px; line-height:1.35; margin-top:6px;
    }}
    .mr-pitch {{
        position:relative; width:145px; height:82px; flex:0 0 145px;
        border:1px solid rgba(243,246,248,.44); border-radius:4px;
        background:linear-gradient(90deg, rgba(73,214,160,.035), rgba(110,168,254,.055));
        overflow:hidden;
    }}
    .mr-pitch:before {{
        content:""; position:absolute; left:50%; top:0; bottom:0;
        width:1px; background:rgba(243,246,248,.38);
    }}
    .mr-pitch:after {{
        content:""; position:absolute; width:28px; height:28px;
        border:1px solid rgba(243,246,248,.38); border-radius:50%;
        left:50%; top:50%; transform:translate(-50%,-50%);
    }}
    .mr-box-left, .mr-box-right {{
        position:absolute; width:24px; height:44px; top:18px;
        border:1px solid rgba(243,246,248,.30);
    }}
    .mr-box-left {{ left:-1px; border-left:none; }}
    .mr-box-right {{ right:-1px; border-right:none; }}
    .mr-role-zone {{
        position:absolute; border:1px solid rgba(110,168,254,.34);
        background:rgba(110,168,254,.13); border-radius:3px;
    }}
    .mr-role-dot {{
        position:absolute; width:10px; height:10px; border-radius:50%;
        background:{ACCENT}; border:2px solid {BG};
        box-shadow:0 0 0 1px {ACCENT}88;
        transform:translate(-50%,-50%);
    }}
    .mr-pitch-direction {{
        position:absolute; right:5px; bottom:3px; color:rgba(243,246,248,.48);
        font-size:7px; font-weight:800; letter-spacing:.08em;
    }}
    .mr-role-tag {{
        display:inline-block; margin-top:7px; padding:3px 7px; border-radius:999px;
        color:{ACCENT}; background:{ACCENT}14; border:1px solid {ACCENT}44;
        font-size:8px; font-weight:800; letter-spacing:.07em;
    }}

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
    match_variability = pd.read_csv(
        REAL_DIR / "skillcorner_match_variability.csv"
    )
    repeated_variability = pd.read_csv(
        REAL_DIR / "skillcorner_repeated_player_variability.csv"
    )
    return (
        sessions,
        players,
        snapshots,
        daily,
        team,
        real_benchmarks,
        match_variability,
        repeated_variability,
    )


try:
    (
        sessions,
        players,
        snapshots,
        daily,
        team,
        real_benchmarks,
        match_variability,
        repeated_variability,
    ) = load_data()
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
    label = STATUS_LABELS.get(status, str(status))
    return (
        f'<span class="mr-badge" style="background:{color}18;color:{color};'
        f'border:1px solid {color}55;">{label.upper()}</span>'
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


def report_kpi_card(label, value, subtitle="", color=None):
    border = color or GRID
    render_html(
        f"""
        <div class="mr-report-kpi" style="border-top:2px solid {border};">
            <div class="mr-report-kpi-label">{label}</div>
            <div class="mr-report-kpi-value">{value}</div>
            <div class="mr-report-kpi-sub">{subtitle}</div>
        </div>
        """
    )


def report_section_header(title, subtitle=None):
    html = f'<div class="mr-report-section-title">{title}</div>'
    if subtitle:
        html += f'<div class="mr-report-section-subtitle">{subtitle}</div>'
    render_html(html)


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


def plain_language_takeaway(row):
    """Return a short, non-technical explanation for the selected player/week."""
    sprint = row["sprint_vs_baseline"] * 100
    hsr = row["hsr_vs_baseline"] * 100
    load = row["load_vs_baseline"] * 100
    peak = row["peak_training_pct_vmax"]

    if bool(row.get("planned_reduction", False)):
        return (
            "Lower exposure is expected here because the player is in a planned reduced-training "
            "or reintegration scenario. The numbers still matter, but they should be read in context."
        )

    if row["monitoring_status"] == "Underexposed":
        return (
            f"Overall work was normal-to-high ({load:.0f}% of usual), but the high-speed stimulus was much lower: "
            f"{sprint:.0f}% of usual sprint exposure, {hsr:.0f}% of usual high-speed running and "
            f"{peak:.0f}% of Vmax. Key point: enough total work, but much less speed-specific work."
        )

    if row["monitoring_status"] == "Monitor":
        if row["load_vs_baseline"] > 1.20:
            return (
                f"High-speed exposure is broadly present, but total training load is {load:.0f}% "
                "of the player's usual level. This is mainly a load-management review rather than a speed-exposure problem."
            )
        if row["wellness_delta"] <= -8:
            return (
                "External training exposure looks broadly acceptable, but the player's wellness is lower than usual. "
                "That disagreement is the main reason to review the week."
            )
        return (
            "Most exposure markers are close to the player's usual preparation, but one signal is outside "
            "the normal range. This is a review flag, not a medical diagnosis."
        )

    return (
        "The main preparation markers are broadly consistent with the player's usual pre-match training profile."
    )


def match_variability_band(value, ref, prefix):
    """Describe where a value sits inside an empirical match distribution."""
    p10 = float(ref[f"{prefix}_p10"])
    p25 = float(ref[f"{prefix}_p25"])
    p50 = float(ref[f"{prefix}_p50"])
    p75 = float(ref[f"{prefix}_p75"])
    p90 = float(ref[f"{prefix}_p90"])

    if value < p10:
        return "below P10"
    if value < p25:
        return "between P10 and P25"
    if value < p50:
        return "between P25 and P50"
    if value < p75:
        return "between P50 and P75"
    if value < p90:
        return "between P75 and P90"
    return "above P90"


def position_report_profile(position):
    """Football-facing role context for the compact performance report."""
    profiles = {
        "CB": {
            "name": "Centre Back",
            "focus": "Defensive coverage · build-up support · repeated accelerations",
            "tag": "DEFENSIVE LOAD PROFILE",
            "zone": "left:8%;top:24%;width:28%;height:52%;",
            "dot": "left:24%;top:50%;",
        },
        "FB": {
            "name": "Full Back",
            "focus": "Wide transitions · repeated high-speed runs · recovery actions",
            "tag": "REPEATED SPEED PROFILE",
            "zone": "left:18%;top:4%;width:40%;height:24%;",
            "dot": "left:40%;top:16%;",
        },
        "CM": {
            "name": "Central Midfielder",
            "focus": "High running volume · support actions · repeated transitions",
            "tag": "VOLUME + HSR PROFILE",
            "zone": "left:34%;top:24%;width:32%;height:52%;",
            "dot": "left:50%;top:50%;",
        },
        "W": {
            "name": "Winger",
            "focus": "Wide high-speed actions · sprint exposure · depth runs",
            "tag": "SPEED EXPOSURE PROFILE",
            "zone": "left:58%;top:4%;width:38%;height:24%;",
            "dot": "left:78%;top:16%;",
        },
        "ST": {
            "name": "Striker",
            "focus": "Explosive depth runs · high-speed efforts · sprint exposure",
            "tag": "EXPLOSIVE RUN PROFILE",
            "zone": "left:70%;top:24%;width:26%;height:52%;",
            "dot": "left:84%;top:50%;",
        },
    }
    return profiles.get(
        position,
        {
            "name": POSITION_LABELS.get(position, position),
            "focus": "Individual physical preparation profile",
            "tag": "PLAYER LOAD PROFILE",
            "zone": "left:40%;top:25%;width:20%;height:50%;",
            "dot": "left:50%;top:50%;",
        },
    )


def report_context(row):
    """Return compact, staff-facing context for the selected week."""
    wellness_delta = float(row.get("wellness_delta", 0))
    if wellness_delta <= -1:
        wellness = f"{abs(wellness_delta):.0f} pts below usual"
    elif wellness_delta >= 1:
        wellness = f"{wellness_delta:.0f} pts above usual"
    else:
        wellness = "close to usual"

    if bool(row.get("planned_reduction", False)):
        staff_check = (
            "Planned reduction: confirm the exposure progression remains consistent "
            "with the return-to-performance plan."
        )
    elif row["monitoring_status"] == "Underexposed":
        staff_check = (
            "Was the lower speed exposure planned? If not, review where sprint / near-max-speed "
            "work was missed across the pre-match microcycle."
        )
    elif row["monitoring_status"] == "Monitor" and row["load_vs_baseline"] > 1.20:
        staff_check = "Review cumulative load together with recovery and session-content context."
    elif row["monitoring_status"] == "Monitor" and wellness_delta <= -8:
        staff_check = "Compare the external load with wellness and recovery context before interpreting the flag."
    elif row["monitoring_status"] == "Monitor":
        staff_check = "Review the flagged metric alongside the session plan and upcoming match demands."
    else:
        staff_check = "No current flag; keep the preparation profile in context with the session and match plan."

    return {
        "training_plan": str(row.get("training_context", "Training")),
        "speed_recency": format_days(row.get("days_since_90_pct_vmax")),
        "wellness": wellness,
        "staff_check": staff_check,
    }


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
st.sidebar.caption("See who needs attention, understand why, and compare training exposure with match demands.")
st.sidebar.divider()

PAGE_LABELS = {
    "Performance Report": "Performance report",
    "Squad Overview": "Team overview",
    "Player Analysis": "Player view",
    "Exposure Map": "Team exposure map",
    "Methodology": "How it works",
}

page = st.sidebar.radio(
    "Workspace",
    ["Performance Report", "Squad Overview", "Player Analysis", "Exposure Map", "Methodology"],
    format_func=lambda x: PAGE_LABELS[x],
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
player_options["position_label"] = player_options["position"].map(POSITION_LABELS).fillna(player_options["position"])
player_options["label"] = player_options["player_name"] + " · " + player_options["position_label"]
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
st.sidebar.caption("Synthetic training data · 24 outfield players · 8-week monitoring period")
st.sidebar.caption("Real match-demand reference · SkillCorner A-League 2024/25")
st.sidebar.caption("Weeks 1–3 = baseline acquisition · Weeks 4–8 = monitoring")
st.sidebar.caption("Portfolio project · Not a medical diagnostic tool")


# ============================================================
# HERO
# ============================================================

if page != "Performance Report":
    render_html(
        """
        <div class="mr-hero">
            <div class="mr-eyebrow">FOOTBALL PERFORMANCE · DATA SCIENCE</div>
            <div class="mr-title">Match Ready?</div>
            <div class="mr-subtitle">
                A simple decision-support view: what changed this week, why it matters,
                and how the player's preparation compares with real match-demand context.
            </div>
        </div>
        """
    )

week_df = snapshots[snapshots["week"] == selected_week].copy()


# ============================================================
# PERFORMANCE REPORT
# ============================================================

if page == "Performance Report":
    player_history = snapshots[snapshots["player_id"] == selected_player].copy()
    player_week = player_history[player_history["week"] == selected_week]

    if player_week.empty:
        st.warning("No snapshot available for this player/week.")
        st.stop()

    row = player_week.iloc[0]
    position_full = POSITION_LABELS.get(row["position"], row["position"])
    status_color = STATUS_COLORS.get(row["monitoring_status"], ACCENT)
    role_profile = position_report_profile(row["position"])
    report_ctx = report_context(row)

    real_ref = real_benchmarks[real_benchmarks["position"] == row["position"]]
    if real_ref.empty:
        st.error("No real match-demand reference is available for this position.")
        st.stop()
    real_ref = real_ref.iloc[0]

    real_hsr_p25 = real_ref["hsr_p25_m"]
    real_hsr_p50 = real_ref["hsr_p50_m"]
    real_hsr_p90 = real_ref["hsr_p90_m"]
    real_sprint_p25 = real_ref["sprint_p25_m"]
    real_sprint_p50 = real_ref["sprint_p50_m"]
    real_sprint_p90 = real_ref["sprint_p90_m"]

    match_ref = match_variability[match_variability["position"] == row["position"]]
    if match_ref.empty:
        st.error("No match-to-match reference is available for this position.")
        st.stop()
    match_ref = match_ref.iloc[0]

    repeated_examples = repeated_variability[
        repeated_variability["position"] == row["position"]
    ].sort_values(["n_matches", "player_name"], ascending=[False, True])
    repeated_example = repeated_examples.iloc[0] if not repeated_examples.empty else None

    header_left, header_right = st.columns([1.55, 0.65], gap="medium")

    with header_left:
        render_html(
            f"""
            <div style="padding:48px 0 9px 0;">
                <div style="color:{MUTED};font-size:9px;font-weight:800;letter-spacing:.14em;">
                    MATCH READY? · PERFORMANCE REPORT
                </div>
                <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-top:5px;">
                    <div>
                        <div class="mr-report-title">{row['player_name']} · {position_full}</div>
                        <div class="mr-report-meta">Week {selected_week} · pre-match preparation</div>
                    </div>
                    <div>{status_badge(row['monitoring_status'])}</div>
                </div>
            </div>
            """
        )

    with header_right:
        render_html(
            f"""
            <div style="padding-top:48px;">
                <div class="mr-role-card">
                    <div class="mr-role-copy">
                        <div class="mr-role-eyebrow">POSITION PROFILE</div>
                        <div class="mr-role-name">{role_profile['name']}</div>
                        <div class="mr-role-sub">{role_profile['focus']}</div>
                        <div class="mr-role-tag">{role_profile['tag']}</div>
                    </div>
                    <div class="mr-pitch" aria-label="Football pitch showing representative {role_profile['name']} zone">
                        <div class="mr-box-left"></div>
                        <div class="mr-box-right"></div>
                        <div class="mr-role-zone" style="{role_profile['zone']}"></div>
                        <div class="mr-role-dot" style="{role_profile['dot']}"></div>
                        <div class="mr-pitch-direction">ATTACK →</div>
                    </div>
                </div>
            </div>
            """
        )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        report_kpi_card(
            "TRAINING LOAD",
            f"{row['load_vs_baseline'] * 100:.0f}%",
            "of usual weekly load",
            ACCENT,
        )
    with k2:
        report_kpi_card(
            "SPRINT EXPOSURE",
            f"{row['sprint_vs_baseline'] * 100:.0f}%",
            "of usual sprint exposure",
            UNDER if row["sprint_vs_baseline"] < 0.60 else MONITOR if row["sprint_vs_baseline"] < 0.85 else READY,
        )
    with k3:
        report_kpi_card(
            "HIGH-SPEED RUNNING",
            f"{row['hsr_vs_baseline'] * 100:.0f}%",
            "of usual high-speed running",
            UNDER if row["hsr_vs_baseline"] < 0.60 else MONITOR if row["hsr_vs_baseline"] < 0.80 else READY,
        )
    with k4:
        report_kpi_card(
            "PEAK SPEED",
            f"{row['peak_training_pct_vmax']:.0f}% Vmax",
            "fastest speed reached this week",
            UNDER if row["peak_training_pct_vmax"] < 85 else MONITOR if row["peak_training_pct_vmax"] < 90 else READY,
        )

    if row["monitoring_status"] == "Underexposed" and not bool(row["planned_reduction"]):
        headline = "SAME LOAD. DIFFERENT STIMULUS."
        summary = (
            f"The player did enough work overall ({row['load_vs_baseline'] * 100:.0f}% of usual), "
            f"but much less of it was speed-specific: sprint exposure fell to "
            f"{row['sprint_vs_baseline'] * 100:.0f}% and high-speed running to "
            f"{row['hsr_vs_baseline'] * 100:.0f}% of usual."
        )
    elif bool(row["planned_reduction"]):
        headline = "LOWER EXPOSURE, BUT PLANNED."
        summary = (
            "The reduced exposure is intentional in the current training context, so the numerical flag "
            "should not be treated as an unexpected preparation issue."
        )
    elif row["monitoring_status"] == "Monitor":
        headline = "REVIEW THE CONTEXT."
        summary = plain_language_takeaway(row)
    else:
        headline = "PREPARATION BROADLY ALIGNED."
        summary = plain_language_takeaway(row)

    render_html(
        f"""
        <div class="mr-report-insight" style="border-left-color:{status_color};">
            <div class="mr-insight-title">{headline}</div>
            <div style="font-size:14.5px;line-height:1.45;">{summary}</div>
        </div>
        <div class="mr-context-strip">
            <div class="mr-context-chip">
                <div class="mr-context-chip-label">TRAINING PLAN</div>
                <div class="mr-context-chip-value">{report_ctx['training_plan']}</div>
            </div>
            <div class="mr-context-chip">
                <div class="mr-context-chip-label">LAST &gt;90% VMAX</div>
                <div class="mr-context-chip-value">{report_ctx['speed_recency']}</div>
            </div>
            <div class="mr-context-chip">
                <div class="mr-context-chip-label">WELLNESS</div>
                <div class="mr-context-chip-value">{report_ctx['wellness']}</div>
            </div>
        </div>
        <div class="mr-staff-check"><b>Staff check:</b> {report_ctx['staff_check']}</div>
        """
    )

    report_section_header(
        "Preparation profile",
        "Training week vs personal baseline · 100% = the player's usual pre-match exposure",
    )

    report_profile = pd.DataFrame(
        {
            "Metric": ["Training load", "Total distance", "High-speed running", "Sprint"],
            "Current": [
                row["load_vs_baseline"] * 100,
                row["distance_vs_baseline"] * 100,
                row["hsr_vs_baseline"] * 100,
                row["sprint_vs_baseline"] * 100,
            ],
        }
    )

    bar_colors = []
    for metric, value in zip(report_profile["Metric"], report_profile["Current"]):
        if metric in ["Training load", "Total distance"]:
            bar_colors.append(ACCENT if value >= 85 else MONITOR)
        elif metric == "High-speed running":
            bar_colors.append(READY if value >= 80 else MONITOR if value >= 60 else UNDER)
        else:
            bar_colors.append(READY if value >= 85 else MONITOR if value >= 60 else UNDER)

    fig = go.Figure(
        go.Bar(
            x=report_profile["Current"],
            y=report_profile["Metric"],
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.0f}%" for v in report_profile["Current"]],
            textposition="outside",
            hovertemplate="%{y}: %{x:.0f}% of baseline<extra></extra>",
        )
    )
    fig.add_vline(
        x=100,
        line_dash="dash",
        line_color=WHITE,
        opacity=0.55,
        annotation_text="Usual",
        annotation_position="top",
    )
    fig.update_xaxes(
        range=[0, max(130, float(report_profile["Current"].max()) + 12)],
        title="Individual baseline (%)",
    )
    fig.update_yaxes(title="")
    fig.update_layout(showlegend=False, bargap=0.28)
    apply_plot_style(fig, 335)
    st.plotly_chart(fig, use_container_width=True)

    report_section_header(
        "Real match variability",
        f"{position_full} · SkillCorner Open Data · 10 A-League tracking matches · volumes normalised to 90 min",
    )

    mv_hsr_p10 = float(match_ref["hsr_p10"])
    mv_hsr_p25 = float(match_ref["hsr_p25"])
    mv_hsr_p50 = float(match_ref["hsr_p50"])
    mv_hsr_p75 = float(match_ref["hsr_p75"])
    mv_hsr_p90 = float(match_ref["hsr_p90"])

    mv_sprint_p10 = float(match_ref["sprint_p10"])
    mv_sprint_p25 = float(match_ref["sprint_p25"])
    mv_sprint_p50 = float(match_ref["sprint_p50"])
    mv_sprint_p75 = float(match_ref["sprint_p75"])
    mv_sprint_p90 = float(match_ref["sprint_p90"])

    hsr_match_ratio = row["training_hsr_m"] / mv_hsr_p50
    sprint_match_ratio = row["training_sprint_m"] / mv_sprint_p50

    mv1, mv2 = st.columns(2)
    with mv1:
        report_kpi_card(
            "REAL MATCH HSR · MEDIAN",
            f"{mv_hsr_p50:.0f} m / 90",
            f"middle 50%: {mv_hsr_p25:.0f}–{mv_hsr_p75:.0f} m · training week: {row['training_hsr_m']:.0f} m",
            ACCENT,
        )
    with mv2:
        report_kpi_card(
            "REAL MATCH SPRINT · MEDIAN",
            f"{mv_sprint_p50:.0f} m / 90",
            f"middle 50%: {mv_sprint_p25:.0f}–{mv_sprint_p75:.0f} m · training week: {row['training_sprint_m']:.0f} m",
            ACCENT,
        )

    match_context = pd.DataFrame(
        {
            "Metric": ["High-speed running", "Sprint"],
            "Training_pct": [hsr_match_ratio * 100, sprint_match_ratio * 100],
            "P10_pct": [mv_hsr_p10 / mv_hsr_p50 * 100, mv_sprint_p10 / mv_sprint_p50 * 100],
            "P25_pct": [mv_hsr_p25 / mv_hsr_p50 * 100, mv_sprint_p25 / mv_sprint_p50 * 100],
            "P75_pct": [mv_hsr_p75 / mv_hsr_p50 * 100, mv_sprint_p75 / mv_sprint_p50 * 100],
            "P90_pct": [mv_hsr_p90 / mv_hsr_p50 * 100, mv_sprint_p90 / mv_sprint_p50 * 100],
        }
    )

    fig = go.Figure()
    for _, metric_row in match_context.iterrows():
        # Outer band = P10–P90 across real player-match performances.
        fig.add_trace(
            go.Scatter(
                x=[metric_row["P10_pct"], metric_row["P90_pct"]],
                y=[metric_row["Metric"], metric_row["Metric"]],
                mode="lines",
                line=dict(color=GRID, width=18),
                hovertemplate=(
                    "Real match P10–P90: "
                    + f"{metric_row['P10_pct']:.0f}%–{metric_row['P90_pct']:.0f}% of median"
                    + "<extra></extra>"
                ),
                showlegend=False,
            )
        )
        # Inner band = middle 50%.
        fig.add_trace(
            go.Scatter(
                x=[metric_row["P25_pct"], metric_row["P75_pct"]],
                y=[metric_row["Metric"], metric_row["Metric"]],
                mode="lines",
                line=dict(color="#526171", width=9),
                hovertemplate=(
                    "Real match P25–P75: "
                    + f"{metric_row['P25_pct']:.0f}%–{metric_row['P75_pct']:.0f}% of median"
                    + "<extra></extra>"
                ),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[100],
                y=[metric_row["Metric"]],
                mode="markers",
                marker=dict(size=11, color=READY, line=dict(color=BG, width=2)),
                hovertemplate="Real match median (P50)<extra></extra>",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[metric_row["Training_pct"]],
                y=[metric_row["Metric"]],
                mode="markers+text",
                text=[f"{metric_row['Training_pct']:.0f}%"],
                textposition="middle right",
                textfont=dict(color=TEXT, size=11),
                marker=dict(size=16, color=ACCENT, symbol="diamond", line=dict(color=BG, width=2)),
                hovertemplate="Training week: %{x:.0f}% of real match median<extra></extra>",
                showlegend=False,
            )
        )

    x_min = max(35, float(match_context[["P10_pct", "Training_pct"]].min().min()) - 12)
    x_max = max(180, float(match_context[["P90_pct", "Training_pct"]].max().max()) + 12)

    fig.add_vline(
        x=100,
        line_dash="dash",
        line_color=READY,
        opacity=0.42,
        annotation_text="Real match median",
        annotation_position="top",
    )
    fig.update_layout(
        title="Training week vs the real match-to-match range",
        showlegend=False,
    )
    fig.update_xaxes(
        title="Real match median = 100%",
        range=[x_min, x_max],
        ticksuffix="%",
    )
    fig.update_yaxes(title="")
    apply_plot_style(fig, 255)
    st.plotly_chart(fig, use_container_width=True)

    hsr_band = match_variability_band(row["training_hsr_m"], match_ref, "hsr")
    sprint_band = match_variability_band(row["training_sprint_m"], match_ref, "sprint")

    example_html = ""
    if repeated_example is not None:
        example_html = f"""
        <div class="mr-report-note">
            <b style="color:{TEXT};">REAL SAME-PLAYER EXAMPLE</b> ·
            {repeated_example['player_name']} · {int(repeated_example['n_matches'])} eligible matches ·
            HSR {repeated_example['hsr_p90_min']:.0f}–{repeated_example['hsr_p90_max']:.0f} m/90 ·
            Sprint {repeated_example['sprint_p90_min']:.0f}–{repeated_example['sprint_p90_max']:.0f} m/90.
            This illustrates how the same player's physical demand can change from fixture to fixture.
        </div>
        """

    render_html(
        f"""
        <div class="mr-report-insight" style="border-left-color:{ACCENT};">
            <div class="mr-insight-title">WHAT THE VARIABILITY ADDS</div>
            This training week sits <b>{hsr_band}</b> for HSR and <b>{sprint_band}</b> for sprint
            when compared with real {position_full.lower()} match performances.
            A single positional average would hide this spread.
        </div>
        {example_html}
        <div class="mr-report-note">
            Real sample: {int(match_ref['n_performances'])} eligible {position_full.lower()} performances ·
            {int(match_ref['n_players'])} players · {int(match_ref['n_matches'])} matches.
            SkillCorner Open Data · A-League 2024/25. Match volumes are normalised to 90 minutes.
            Synthetic training/wellness data remain separate. The 10-match sample is contextual, not a league-wide target.
        </div>
        """
    )


# ============================================================
# SQUAD OVERVIEW
# ============================================================

elif page == "Squad Overview":
    section_header(
        "Team overview",
        f"Week {selected_week} · start with the priority queue, then use the table for detail",
    )
    st.caption(
        "Aligned = no current flag · Review = context needed · Low speed exposure = sprint, HSR or peak-speed work is clearly lower than usual."
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
        kpi_card("ALIGNED", ready, f"{ready / total * 100:.0f}% of squad", READY)
    with c2:
        kpi_card("REVIEW", monitor, "Needs staff context", MONITOR)
    with c3:
        kpi_card("LOW SPEED EXPOSURE", under, "Speed stimulus clearly reduced", UNDER)
    with c4:
        kpi_card("NEEDS REVIEW", actionable, "Unexpected flags only", ACCENT)

    section_header(
        "Who needs attention?",
        "Unexpected flags first. Planned rehabilitation or reintegration remains visible, but is not treated as urgent.",
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
                    "PLANNED REDUCTION"
                    if bool(row["planned_reduction"])
                    else "REVIEW FIRST"
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
        table["Status"] = table["Status"].map(STATUS_LABELS).fillna(table["Status"])
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
        status_counts["Display"] = status_counts["Status"].map(STATUS_LABELS).fillna(status_counts["Status"])

        fig = go.Figure(
            go.Pie(
                labels=status_counts["Display"],
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

    real_ref = real_benchmarks[real_benchmarks["position"] == row["position"]]
    if real_ref.empty:
        st.error("No real match-demand reference is available for this position.")
        st.stop()
    real_ref = real_ref.iloc[0]

    real_distance_p50 = real_ref["total_distance_p50_m"]
    real_hsr_p50 = real_ref["hsr_p50_m"]
    real_sprint_p50 = real_ref["sprint_p50_m"]
    hsr_vs_real_p50 = row["training_hsr_m"] / real_hsr_p50
    sprint_vs_real_p50 = row["training_sprint_m"] / real_sprint_p50

    hsr_real_delta = (hsr_vs_real_p50 - 1) * 100
    sprint_real_delta = (sprint_vs_real_p50 - 1) * 100

    section_header(
        "Player snapshot",
        "Start here: what changed, why it matters, then open the technical detail only if you need it.",
    )

    identity_col, takeaway_col = st.columns([0.78, 1.45])

    with identity_col:
        render_html(
            f"""
            <div class="mr-player-card">
                <div class="mr-player-id">{row['player_id']} · WEEK {selected_week}</div>
                <div class="mr-player-name">{row['player_name']}</div>
                <div class="mr-player-pos">{position_full}</div>
                {status_badge(row['monitoring_status'])} &nbsp; {context_badge(row['training_context'])}
                <div style="margin-top:18px;color:{MUTED};font-size:11px;line-height:1.55;">
                    <b style="color:{TEXT};">Status meaning</b><br>
                    Aligned = no current flag · Review = context needed · Low speed exposure = one or more
                    speed-related exposures are clearly lower than usual.
                </div>
            </div>
            """
        )

    with takeaway_col:
        render_html(
            f"""
            <div class="mr-insight" style="border-left-color:{STATUS_COLORS.get(row['monitoring_status'], ACCENT)};">
                <div class="mr-insight-title">QUICK TAKEAWAY</div>
                <div style="font-size:18px;line-height:1.5;font-weight:650;">
                    {plain_language_takeaway(row)}
                </div>
                <div style="margin-top:14px;padding-top:12px;border-top:1px solid {GRID};color:{MUTED};font-size:11px;">
                    <b style="color:{TEXT};">Context:</b> {row['context_note']}
                </div>
            </div>
            """
        )

    section_header(
        "1 · What changed this week?",
        "100% means the player's usual pre-match training week, based on the individual baseline.",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card(
            "OVERALL TRAINING LOAD",
            f"{row['load_vs_baseline'] * 100:.0f}%",
            f"{abs(row['load_vs_baseline'] * 100 - 100):.0f}% {'above' if row['load_vs_baseline'] >= 1 else 'below'} usual",
            ACCENT,
        )
    with c2:
        kpi_card(
            "SPRINT EXPOSURE",
            f"{row['sprint_vs_baseline'] * 100:.0f}%",
            f"{abs(row['sprint_vs_baseline'] * 100 - 100):.0f}% {'above' if row['sprint_vs_baseline'] >= 1 else 'below'} usual",
            READY if row["sprint_vs_baseline"] >= 0.85 else MONITOR if row["sprint_vs_baseline"] >= 0.60 else UNDER,
        )
    with c3:
        kpi_card(
            "HIGH-SPEED RUNNING",
            f"{row['hsr_vs_baseline'] * 100:.0f}%",
            f"{abs(row['hsr_vs_baseline'] * 100 - 100):.0f}% {'above' if row['hsr_vs_baseline'] >= 1 else 'below'} usual",
            READY if row["hsr_vs_baseline"] >= 0.80 else MONITOR if row["hsr_vs_baseline"] >= 0.60 else UNDER,
        )
    with c4:
        kpi_card(
            "FASTEST SPEED REACHED",
            f"{row['peak_training_pct_vmax']:.0f}% Vmax",
            "share of the player's known individual maximum speed",
            READY if row["peak_training_pct_vmax"] >= 90 else MONITOR if row["peak_training_pct_vmax"] >= 85 else UNDER,
        )

    section_header(
        "2 · Why does this matter?",
        "A similar total workload can contain a very different physical stimulus.",
    )

    if row["monitoring_status"] == "Underexposed" and not bool(row["planned_reduction"]):
        insight_title = "SAME LOAD. DIFFERENT STIMULUS."
        insight_text = (
            f"Overall load is {row['load_vs_baseline'] * 100:.0f}% of usual, while sprint exposure is "
            f"{row['sprint_vs_baseline'] * 100:.0f}% and HSR is {row['hsr_vs_baseline'] * 100:.0f}%. "
            "The player has done plenty of work, but the week contains much less high-speed work than their normal preparation."
        )
        insight_color = UNDER
    elif bool(row["planned_reduction"]):
        insight_title = "LOWER EXPOSURE, BUT PLANNED."
        insight_text = (
            "The numerical reduction is visible, but the training context says it is intentional. "
            "This is why the dashboard keeps staff context next to the numbers."
        )
        insight_color = PURPLE
    elif row["monitoring_status"] == "Monitor":
        insight_title = "REVIEW THE CONTEXT."
        insight_text = plain_language_takeaway(row)
        insight_color = MONITOR
    else:
        insight_title = "PREPARATION IS BROADLY ALIGNED."
        insight_text = plain_language_takeaway(row)
        insight_color = READY

    render_html(
        f"""
        <div class="mr-insight" style="border-left-color:{insight_color};">
            <div class="mr-insight-title">{insight_title}</div>
            {insight_text}
        </div>
        """
    )

    section_header(
        "3 · What does real match data add?",
        "SkillCorner A-League 2024/25 gives an external positional reference. It adds context; it does not define a training target.",
    )

    real1, real2 = st.columns(2)
    with real1:
        direction = "above" if hsr_real_delta >= 0 else "below"
        kpi_card(
            "HIGH-SPEED RUNNING",
            f"{hsr_vs_real_p50 * 100:.0f}% of match P50",
            f"{row['training_hsr_m']:.0f} m this week · real {position_full} P50: {real_hsr_p50:.0f} m",
            ACCENT,
        )
    with real2:
        direction = "above" if sprint_real_delta >= 0 else "below"
        kpi_card(
            "SPRINT DISTANCE",
            f"{sprint_vs_real_p50 * 100:.0f}% of match P50",
            f"{row['training_sprint_m']:.0f} m this week · real {position_full} P50: {real_sprint_p50:.0f} m",
            ACCENT,
        )

    context = pd.DataFrame(
        {
            "Metric": ["HSR", "Sprint"],
            "Training": [row["training_hsr_m"], row["training_sprint_m"]],
            "P25": [real_ref["hsr_p25_m"], real_ref["sprint_p25_m"]],
            "P50": [real_ref["hsr_p50_m"], real_ref["sprint_p50_m"]],
            "P90": [real_ref["hsr_p90_m"], real_ref["sprint_p90_m"]],
        }
    )

    fig = go.Figure()
    for _, metric_row in context.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[metric_row["P25"], metric_row["P90"]],
                y=[metric_row["Metric"], metric_row["Metric"]],
                mode="lines",
                line=dict(color=GRID, width=18),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[metric_row["P50"]],
                y=[metric_row["Metric"]],
                mode="markers",
                marker=dict(size=12, color=READY, line=dict(color=BG, width=2)),
                hovertemplate="Real positional median: %{x:.0f} m<extra></extra>",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[metric_row["Training"]],
                y=[metric_row["Metric"]],
                mode="markers+text",
                text=["Training week"],
                textposition="middle right",
                textfont=dict(color=TEXT, size=11),
                marker=dict(size=16, color=ACCENT, symbol="diamond", line=dict(color=BG, width=2)),
                hovertemplate="Training week: %{x:.0f} m<extra></extra>",
                showlegend=False,
            )
        )

    fig.update_layout(
        title="This training week vs real positional match reference",
        showlegend=False,
    )
    fig.update_xaxes(title="Metres")
    fig.update_yaxes(title="")
    apply_plot_style(fig, 300)
    st.plotly_chart(fig, use_container_width=True)

    render_html(
        f"""
        <div class="mr-insight" style="border-left-color:{ACCENT};">
            <div class="mr-insight-title">WHAT THE REAL DATA ADDS</div>
            The week accumulated <b>{hsr_vs_real_p50 * 100:.0f}%</b> of the real {position_full.lower()} match P50 for HSR,
            but only <b>{sprint_vs_real_p50 * 100:.0f}%</b> for sprint distance.
            The mix is therefore uneven: plenty of high-speed running, but comparatively less sprinting.
            Combined with the player's own sprint baseline ({row['sprint_vs_baseline'] * 100:.0f}%),
            this supports the same conclusion from a second angle: the issue is the <b>type of speed stimulus</b>, not total work.
        </div>
        """
    )

    st.caption(
        f"SkillCorner reference: {int(real_ref['n_players'])} eligible {position_full.lower()} player-position samples, "
        f"{int(real_ref['total_matches'])} matches represented. A full training week and one match are different exposure windows; "
        "the comparison is descriptive and should not be read as a prescribed target."
    )

    with st.expander("What do these terms mean?"):
        st.markdown(
            """
            **Baseline** — the player's own usual pre-match training profile, built from the first three weeks.  
            **HSR (high-speed running)** — running at high speed below the sprint threshold.  
            **Sprint exposure** — distance covered at sprint speed.  
            **Vmax** — the player's individual maximum speed.  
            **P50** — the median value in the real positional reference; half the player-position averages are below it and half above it.  
            **P25–P90** — a wider reference range showing variation across real player-position averages.
            """
        )

    with st.expander("4 · Technical detail — weekly trends, microcycle and wellness", expanded=False):
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
            format_func=lambda x: STATUS_LABELS.get(x, x),
        )

    map_df = week_df[
        week_df["position"].isin(positions)
        & week_df["monitoring_status"].isin(statuses)
    ].copy()

    if map_df.empty:
        st.info("No players match the selected filters.")
        st.stop()

    map_df["Sprint exposure vs usual (%)"] = map_df["sprint_vs_baseline"] * 100
    map_df["High-speed running vs usual (%)"] = map_df["hsr_vs_baseline"] * 100
    map_df["Status"] = map_df["monitoring_status"].map(STATUS_LABELS).fillna(map_df["monitoring_status"])
    map_df["Position"] = map_df["position"].map(POSITION_LABELS).fillna(map_df["position"])

    display_status_colors = {
        STATUS_LABELS["Ready"]: READY,
        STATUS_LABELS["Monitor"]: MONITOR,
        STATUS_LABELS["Underexposed"]: UNDER,
    }

    fig = px.scatter(
        map_df,
        x="Sprint exposure vs usual (%)",
        y="High-speed running vs usual (%)",
        color="Status",
        hover_name="player_name",
        hover_data={
            "Position": True,
            "training_context": True,
            "peak_training_pct_vmax": ":.1f",
            "Sprint exposure vs usual (%)": ":.0f",
            "High-speed running vs usual (%)": ":.0f",
            "monitoring_status": False,
            "position": False,
        },
        color_discrete_map=display_status_colors,
    )
    fig.update_traces(marker=dict(size=12, line=dict(color=BG, width=1.4), opacity=0.95))
    fig.add_vrect(x0=0, x1=60, fillcolor=UNDER, opacity=0.045, line_width=0, layer="below")
    fig.add_hrect(y0=0, y1=60, fillcolor=UNDER, opacity=0.045, line_width=0, layer="below")
    fig.add_vline(x=100, line_dash="dash", line_color=WHITE, opacity=0.38)
    fig.add_hline(y=100, line_dash="dash", line_color=WHITE, opacity=0.38)

    labels = map_df[map_df["monitoring_status"] != "Ready"]
    for _, p in labels.iterrows():
        fig.add_annotation(
            x=p["Sprint exposure vs usual (%)"],
            y=p["High-speed running vs usual (%)"],
            text=p["player_id"],
            showarrow=False,
            xshift=8,
            yshift=9,
            font=dict(color=TEXT, size=10),
        )

    fig.update_xaxes(
        range=[
            max(20, map_df["Sprint exposure vs usual (%)"].min() - 15),
            max(130, map_df["Sprint exposure vs usual (%)"].max() + 15),
        ]
    )
    fig.update_yaxes(
        range=[
            max(20, map_df["High-speed running vs usual (%)"].min() - 15),
            max(130, map_df["High-speed running vs usual (%)"].max() + 15),
        ]
    )
    fig.update_layout(legend_title_text="")
    apply_plot_style(fig, 650)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "100% = the player's usual preparation level. Colour shows monitoring status; position and training context are available on hover. "
        "The shaded area is a visual monitoring aid, not a medical-risk zone."
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
                    <b>{p['player_name']} · {POSITION_LABELS.get(p['position'], p['position'])}</b>
                    &nbsp; {status_badge(p['monitoring_status'])}
                    &nbsp; {context_badge(plan_label)}
                    <br><br>
                    <span style="color:{MUTED};font-size:11px;">
                        Sprint {p['sprint_vs_baseline']*100:.0f}% of usual · High-speed running {p['hsr_vs_baseline']*100:.0f}% of usual ·
                        Peak speed {p['peak_training_pct_vmax']:.0f}% Vmax
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
        "How it works",
        "The data, the comparison logic and the limits — explained transparently.",
    )

    a, b = st.columns(2)
    with a:
        render_html(
            """
            <div class="mr-panel">
                <b>1 · Hybrid data design</b><br><br>
                Training and wellness data are simulated for 24 outfield players across eight competitive
                microcycles. Match-demand context comes from real SkillCorner A-League 2024/25 physical
                aggregates. Goalkeepers are excluded because their demands require a different framework.
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
                Weekly synthetic training HSR and sprint distance are compared with real positional
                P25–P90 distributions from SkillCorner Open Data. The comparison adds external context
                without turning a positional benchmark into a prescribed training target.
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
        <div class="mr-rule"><b style="color:{UNDER};">LOW SPEED EXPOSURE</b> · sprint &lt;60% baseline, high-speed running &lt;60% baseline, or weekly peak speed &lt;85% Vmax.</div>
        <div class="mr-rule"><b style="color:{MONITOR};">REVIEW</b> · moderate speed-exposure reduction, elevated or reduced overall load, materially lower wellness, or limited recent &gt;90% Vmax exposure.</div>
        <div class="mr-rule"><b style="color:{READY};">ALIGNED</b> · no current rule is triggered. Exposure is broadly aligned with the synthetic individual baseline; this is not a medical clearance.</div>
        """
    )

    section_header("Designed Storylines", "Three deliberately different cases make the dashboard useful to explore")
    s1, s2, s3 = st.columns(3)
    with s1:
        render_html(
            f"""
            <div class="mr-priority" style="border-top:3px solid {UNDER};">
                <div class="mr-priority-label">P18 · WINGER</div>
                <div class="mr-priority-name">Unexpected speed-exposure drop</div>
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
        <b>Match Ready?</b> · Synthetic training data + real SkillCorner match-demand reference · Portfolio project.<br>
        Monitoring classifications and the preparation-alignment index are illustrative decision-support constructs.
        They are not medical diagnoses, validated injury-risk predictions or return-to-play clearances.
    </div>
    """
)
