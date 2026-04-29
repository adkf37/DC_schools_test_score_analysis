"""
Same-Grade Year-over-Year (YoY) Growth Analysis for DC Schools.

This script computes same-grade year-over-year growth for every school,
grade, subject, and student subgroup.  Unlike cohort growth (which tracks
the SAME students as they advance to the next grade), YoY growth answers:

    "Is Grade 6 ELA at this school improving year after year?"

Only consecutive school-year pairs are compared (2016→2017, 2017→2018,
2018→2019, 2022→2023, 2023→2024).  The 2019→2022 COVID gap is excluded
because it spans three years and would mix pandemic-era disruption with
genuine instructional improvement.

Inputs:
    output_data/combined_all_years.csv   – produced by load_wide_format_data.py

Outputs:
    output_data/yoy_growth_detail.csv    – one row per school × grade × subject ×
                                           subgroup × transition pair
    output_data/yoy_growth_summary.csv   – school × subject × subgroup summary
                                           aggregated over all transitions

Usage:
    python src/yoy_growth_analysis.py
"""
import os
import sys
import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, ".."))
OUTPUT_PATH = os.path.join(REPO_ROOT, "output_data")

COMBINED_FILE = os.path.join(OUTPUT_PATH, "combined_all_years.csv")
OUT_DETAIL = os.path.join(OUTPUT_PATH, "yoy_growth_detail.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "yoy_growth_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
# Consecutive year pairs to include (excludes the 2019→2022 COVID gap)
VALID_TRANSITIONS = {
    (2016, 2017),
    (2017, 2018),
    (2018, 2019),
    (2022, 2023),
    (2023, 2024),
}

# Minimum student count for a valid data point
MIN_N = 10

# Skip these "all grades" pseudo-grades
SKIP_GRADES = {"ALL", "ALL GRADES"}


# ── Helper ────────────────────────────────────────────────────────────────────

def _parse_percent(series: pd.Series) -> pd.Series:
    """Convert percent strings to float; return NaN for suppressed values."""
    suppress = {"DS", "N<10", "<5%", "<=10%", "N/A", "NA", ""}

    def _parse(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().upper()
        if s in suppress:
            return np.nan
        if any(s.startswith(m) for m in ("<", "<=", ">", ">=")):
            return np.nan
        try:
            return float(s.replace("%", "").strip())
        except ValueError:
            return np.nan

    return series.apply(_parse)


def _parse_count(series: pd.Series) -> pd.Series:
    """Convert count strings to float; return NaN for suppressed values."""
    suppress = {"DS", "N<10", "<5", "<=10", "N/A", "NA", ""}

    def _parse(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().upper()
        if s in suppress:
            return np.nan
        try:
            return float(s)
        except ValueError:
            return np.nan

    return series.apply(_parse)


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("SAME-GRADE YEAR-OVER-YEAR GROWTH ANALYSIS")
    print("=" * 70)

    # ── Load data ─────────────────────────────────────────────────────────────
    if not os.path.isfile(COMBINED_FILE):
        print(f"ERROR: {COMBINED_FILE} not found.")
        print("       Run src/load_wide_format_data.py first.")
        sys.exit(1)

    df = pd.read_csv(COMBINED_FILE, dtype=str)
    print(f"\n  Loaded {len(df):,} rows from combined_all_years.csv")

    # Parse numeric columns
    df["percent_value"] = _parse_percent(df["Percent"])
    df["total_count"] = _parse_count(df["Total Count"])
    df["year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

    # Filter to school level
    df = df[df["Aggregation Level"].str.upper() == "SCHOOL"].copy()

    # Drop rows with no usable percent or year
    df = df.dropna(subset=["percent_value", "year"])

    # Drop pseudo-grade rows (e.g., "All Grades")
    grade_col = "Grade of Enrollment"
    df = df[~df[grade_col].str.upper().str.strip().isin(SKIP_GRADES)]

    # Normalise grade strings  (e.g., "Grade 06" → "Grade 6")
    df[grade_col] = df[grade_col].str.strip()

    print(f"  After filtering: {len(df):,} rows")
    print(f"  Years available: {sorted(df['year'].dropna().unique())}")
    print(f"  Schools        : {df['School Name'].nunique()}")

    # ── Build transitions ─────────────────────────────────────────────────────
    # Keys that uniquely identify a data point (same as cohort engine logic)
    group_keys = [
        "School Name",
        "Subject",
        "Student Group Value",
        grade_col,
    ]

    # Average percent and sum total count per key × year
    agg = (
        df.groupby(group_keys + ["year"], as_index=False)
        .agg(
            pct=("percent_value", "mean"),
            n_students=("total_count", "mean"),
        )
    )

    # Self-join on (school, subject, subgroup, grade) where followup_year = baseline_year + 1
    base = agg.rename(columns={"year": "baseline_year", "pct": "baseline_pct", "n_students": "baseline_n"})
    follow = agg.rename(columns={"year": "followup_year", "pct": "followup_pct", "n_students": "followup_n"})

    joined = base.merge(follow, on=group_keys)
    joined = joined[
        joined.apply(
            lambda r: (int(r["baseline_year"]), int(r["followup_year"])) in VALID_TRANSITIONS,
            axis=1,
        )
    ]

    # Apply minimum-N filter on both ends
    joined = joined[
        (joined["baseline_n"].fillna(0) >= MIN_N)
        & (joined["followup_n"].fillna(0) >= MIN_N)
    ]

    # Compute percentage-point change
    joined["pp_change"] = (joined["followup_pct"] - joined["baseline_pct"]).round(2)
    joined["transition_label"] = (
        joined["baseline_year"].astype(str) + "→" + joined["followup_year"].astype(str)
    )
    joined = joined.rename(columns={grade_col: "grade", "Student Group Value": "Student Group Value"})

    detail = joined[
        [
            "School Name",
            "Subject",
            "Student Group Value",
            "grade",
            "baseline_year",
            "baseline_pct",
            "followup_year",
            "followup_pct",
            "pp_change",
            "transition_label",
            "baseline_n",
            "followup_n",
        ]
    ].copy()

    detail["baseline_pct"] = detail["baseline_pct"].round(2)
    detail["followup_pct"] = detail["followup_pct"].round(2)
    detail = detail.sort_values(
        ["School Name", "Subject", "Student Group Value", "grade", "baseline_year"]
    ).reset_index(drop=True)

    print(f"\n  YoY detail rows: {len(detail):,}")
    print(f"  Transitions    : {sorted(detail['transition_label'].unique())}")

    # ── Summary by school × subject × subgroup ────────────────────────────────
    summary = (
        detail.groupby(["School Name", "Subject", "Student Group Value"], as_index=False)
        .agg(
            n_transitions=("pp_change", "count"),
            avg_pp_change=("pp_change", "mean"),
            median_pp_change=("pp_change", "median"),
            pct_improving=("pp_change", lambda x: round(100 * (x > 0).sum() / len(x), 1)),
            max_pp_change=("pp_change", "max"),
            min_pp_change=("pp_change", "min"),
        )
    )
    summary["avg_pp_change"] = summary["avg_pp_change"].round(2)
    summary["median_pp_change"] = summary["median_pp_change"].round(2)
    summary["max_pp_change"] = summary["max_pp_change"].round(2)
    summary["min_pp_change"] = summary["min_pp_change"].round(2)
    summary = summary.sort_values(["School Name", "Subject", "Student Group Value"]).reset_index(drop=True)

    print(f"  YoY summary rows: {len(summary):,}")

    # ── Print headline findings ───────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("CITYWIDE AVERAGE — All Students")
    print("─" * 70)
    citywide = detail[detail["Student Group Value"] == "All Students"]
    for subj in sorted(citywide["Subject"].unique()):
        sub = citywide[citywide["Subject"] == subj]
        trans_avg = sub.groupby("transition_label")["pp_change"].mean().sort_index()
        print(f"\n  {subj}")
        for trans, avg in trans_avg.items():
            print(f"    {trans}: avg {avg:+.2f} pp")

    # ── Save outputs ──────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    detail.to_csv(OUT_DETAIL, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"\n✓ Saved {len(detail):,} rows → {OUT_DETAIL}")
    print(f"✓ Saved {len(summary):,} rows → {OUT_SUMMARY}")
    print()
    print("=" * 70)
    print("YOY GROWTH ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    run()
