from pathlib import Path
import pandas as pd

SOURCE_URL = (
    "https://raw.githubusercontent.com/SkillCorner/opendata/master/"
    "data/aggregates/aus1league_physicalaggregates_20242025.csv"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "real"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "skillcorner_position_benchmarks.csv"

POSITION_MAP = {
    "Central Defender": "CB",
    "Full Back": "FB",
    "Midfield": "CM",
    "Wide Attacker": "W",
    "Center Forward": "ST",
}

METRICS = {
    "total_distance_full_all": "total_distance",
    "hsr_distance_full_all": "hsr",
    "sprint_distance_full_all": "sprint",
    "psv99": "psv99",
}

QUANTILES = {
    "p25": 0.25,
    "p50": 0.50,
    "p75": 0.75,
    "p90": 0.90,
}


def main():
    df = pd.read_csv(SOURCE_URL)

    # Keep role samples with enough season exposure to make the positional
    # reference less sensitive to one-off appearances.
    df = df[
        df["position_group"].isin(POSITION_MAP)
        & (df["count_match"] >= 5)
        & (df["count_match_failed"] == 0)
    ].copy()

    rows = []
    for skillcorner_position, position in POSITION_MAP.items():
        group = df[df["position_group"] == skillcorner_position]

        row = {
            "position": position,
            "skillcorner_position": skillcorner_position,
            "n_players": len(group),
            "total_matches": int(group["count_match"].sum()),
        }

        for source_col, short_name in METRICS.items():
            for quantile_name, quantile in QUANTILES.items():
                suffix = "_kmh" if short_name == "psv99" else "_m"
                row[f"{short_name}_{quantile_name}{suffix}"] = (
                    group[source_col].quantile(quantile)
                )

        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {OUTPUT_FILE}")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
