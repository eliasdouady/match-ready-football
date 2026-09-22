from pathlib import Path
import pandas as pd

SOURCE_URL = (
    "https://raw.githubusercontent.com/SkillCorner/opendata/master/"
    "data/aggregates/aus1league_physicalaggregates_20242025.csv"
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "real" / "skillcorner_position_benchmarks.csv"

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

QUANTILES = {"p25": .25, "p50": .50, "p75": .75, "p90": .90}


def main():
    df = pd.read_csv(SOURCE_URL)
    df = df[
        df["position_group"].isin(POSITION_MAP)
        & (df["count_match"] >= 5)
        & (df["count_match_failed"] == 0)
    ].copy()

    rows = []
    for source_position, position in POSITION_MAP.items():
        g = df[df["position_group"] == source_position]
        row = {
            "position": position,
            "skillcorner_position": source_position,
            "n_players": len(g),
            "total_matches": int(g["count_match"].sum()),
        }
        for source_col, short in METRICS.items():
            for q_name, q_value in QUANTILES.items():
                unit = "_kmh" if short == "psv99" else "_m"
                row[f"{short}_{q_name}{unit}"] = g[source_col].quantile(q_value)
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
