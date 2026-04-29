"""
COVID Recovery Analysis for DC Schools.

This script quantifies the pandemic's effect on DC school test performance and
measures how well each school has recovered by using the 2019 school year as a
pre-COVID benchmark and the 2022, 2023, and 2024 data as the post-COVID years.

Key metrics computed for every school × subject × student-subgroup combination:

  covid_impact_pp   — proficiency change from 2019 → 2022 (drop is negative)
  recovery_pp       — proficiency change from 2022 → 2024 (gain is positive)
  net_vs_precovid   — 2024 proficiency minus 2019 proficiency
  recovery_status   — one of:
                        "Exceeded Pre-COVID"    (net_vs_precovid >  +1 pp)
                        "Fully Recovered"       (net_vs_precovid ≥  −1 pp)
                        "Partially Recovered"   (recovered > 0 but still below)
                        "Still Below Pre-COVID" (recovery_pp ≤ 0 and still below)

Only rows where the school has data in 2019 AND at least one post-COVID year
(2022 or 2024) are included.  Minimum N = 10 filter applies throughout.

Inputs:
    output_data/combined_all_years.csv   – produced by load_wide_format_data.py

Outputs:
    output_data/covid_recovery_detail.csv  – one row per school × subject ×
                                             subgroup with 2019, 2022, 2024
                                             proficiency and derived metrics
    output_data/covid_recovery_summary.csv – school × subject aggregate
                                             (All Students only) with status
                                             distribution and city-rank columns

Usage:
    python src/covid_recovery_analysis.py
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
OUT_DETAIL = os.path.join(OUTPUT_PATH, "covid_recovery_detail.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "covid_recovery_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
PRE_COVID_YEAR = 2019
COVID_YEAR = 2022          # first post-COVID data year in the repo
LATEST_YEAR = 2024         # last available year

MIN_N = 10                 # minimum student count to include a data point

# Skip "all grades" pseudo-grade rows
SKIP_GRADES = {"ALL", "ALL GRADES"}

# Recovery classification thresholds (pp, relative to 2019 baseline)
EXCEEDED_THRESHOLD = 1.0    # net_vs_precovid > +1 pp → Exceeded Pre-COVID
RECOVERED_THRESHOLD = -1.0  # net_vs_precovid ≥ -1 pp → Fully Recovered


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def _classify_recovery(net: float, recovery: float) -> str:
    """Assign a recovery status label given net vs. pre-COVID and recovery pp."""
    if pd.isna(net):
        return "Unknown"
    if net > EXCEEDED_THRESHOLD:
        return "Exceeded Pre-COVID"
    if net >= RECOVERED_THRESHOLD:
        return "Fully Recovered"
    if recovery > 0:
        return "Partially Recovered"
    return "Still Below Pre-COVID"


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("COVID RECOVERY ANALYSIS")
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

    # Filter to school-level rows only
    df = df[df["Aggregation Level"].str.upper() == "SCHOOL"].copy()

    # Drop rows without a usable percent value or year
    df = df.dropna(subset=["percent_value", "year"])

    # Drop pseudo-grade rows (e.g., "All Grades")
    grade_col = "Grade of Enrollment"
    df = df[~df[grade_col].str.upper().str.strip().isin(SKIP_GRADES)]

    # Keep only years relevant to COVID analysis
    relevant_years = {PRE_COVID_YEAR, COVID_YEAR, LATEST_YEAR}
    df = df[df["year"].isin(relevant_years)]

    # Apply minimum-N filter
    df = df[df["total_count"].fillna(0) >= MIN_N]

    print(f"  After filtering: {len(df):,} rows")
    print(f"  Years available: {sorted(df['year'].dropna().unique())}")
    print(f"  Schools        : {df['School Name'].nunique()}")

    if PRE_COVID_YEAR not in df["year"].values:
        print(f"\nWARNING: No data found for pre-COVID year ({PRE_COVID_YEAR}).")
        print("         COVID recovery analysis requires 2019 data.")
        print("         Ensure load_wide_format_data.py has loaded the 2018-19 workbook.")
        sys.exit(1)

    # ── Aggregate to school × subject × subgroup × year ───────────────────────
    group_keys = ["School Name", "Subject", "Student Group Value"]

    agg = (
        df.groupby(group_keys + ["year"], as_index=False)
        .agg(
            pct=("percent_value", "mean"),
            n_students=("total_count", "mean"),
        )
    )

    # ── Pivot to one row per school × subject × subgroup ──────────────────────
    def _pivot_year(year_val: int, suffix: str, df_agg: pd.DataFrame) -> pd.DataFrame:
        """Extract data for a specific year and rename columns with suffix."""
        sub = df_agg[df_agg["year"] == year_val][group_keys + ["pct", "n_students"]].copy()
        sub = sub.rename(columns={"pct": f"pct_{suffix}", "n_students": f"n_{suffix}"})
        return sub

    pre = _pivot_year(PRE_COVID_YEAR, "2019", agg)
    covid = _pivot_year(COVID_YEAR, "2022", agg)
    latest = _pivot_year(LATEST_YEAR, "2024", agg)

    # Merge: require 2019 data; 2022 and 2024 are optional but at least one needed
    detail = pre.merge(covid, on=group_keys, how="left")
    detail = detail.merge(latest, on=group_keys, how="left")

    # Keep only rows where we can compute at least one post-COVID comparison
    has_2022 = detail["pct_2022"].notna()
    has_2024 = detail["pct_2024"].notna()
    detail = detail[has_2022 | has_2024].copy()

    print(f"\n  Matched school × subject × subgroup rows: {len(detail):,}")

    # ── Compute derived metrics ────────────────────────────────────────────────
    # COVID impact: 2019 → 2022 change
    detail["covid_impact_pp"] = (detail["pct_2022"] - detail["pct_2019"]).round(2)

    # Recovery progress: 2022 → 2024 change
    detail["recovery_pp"] = (detail["pct_2024"] - detail["pct_2022"]).round(2)

    # Net change relative to pre-COVID: 2024 vs. 2019
    detail["net_vs_precovid_pp"] = (detail["pct_2024"] - detail["pct_2019"]).round(2)

    # Recovery status classification (requires 2024 data)
    detail["recovery_status"] = detail.apply(
        lambda r: _classify_recovery(r["net_vs_precovid_pp"], r["recovery_pp"])
        if pd.notna(r["pct_2024"])
        else "No 2024 Data",
        axis=1,
    )

    # Round proficiency columns
    for col in ["pct_2019", "pct_2022", "pct_2024"]:
        detail[col] = detail[col].round(2)

    detail = detail.sort_values(
        ["School Name", "Subject", "Student Group Value"]
    ).reset_index(drop=True)

    # Reorder columns for readability
    col_order = [
        "School Name", "Subject", "Student Group Value",
        "pct_2019", "n_2019",
        "pct_2022", "n_2022",
        "pct_2024", "n_2024",
        "covid_impact_pp", "recovery_pp", "net_vs_precovid_pp",
        "recovery_status",
    ]
    detail = detail[[c for c in col_order if c in detail.columns]]

    print(f"  COVID recovery detail rows: {len(detail):,}")

    # ── Build All-Students summary ─────────────────────────────────────────────
    all_stu = detail[detail["Student Group Value"] == "All Students"].copy()

    # Status counts per school × subject
    status_counts = (
        all_stu.groupby(["School Name", "Subject", "recovery_status"], as_index=False)
        .size()
        .rename(columns={"size": "n_rows"})
    )

    # Pivot to one row per school × subject with status breakdown
    summary = (
        all_stu.groupby(["School Name", "Subject"], as_index=False)
        .agg(
            pct_2019=("pct_2019", "mean"),
            pct_2022=("pct_2022", "mean"),
            pct_2024=("pct_2024", "mean"),
            covid_impact_pp=("covid_impact_pp", "mean"),
            recovery_pp=("recovery_pp", "mean"),
            net_vs_precovid_pp=("net_vs_precovid_pp", "mean"),
        )
        .round(2)
    )

    # Classify at the summary level using averaged metrics
    summary["recovery_status"] = summary.apply(
        lambda r: _classify_recovery(r["net_vs_precovid_pp"], r["recovery_pp"])
        if pd.notna(r["pct_2024"])
        else "No 2024 Data",
        axis=1,
    )

    summary = summary.sort_values(
        ["Subject", "net_vs_precovid_pp"], ascending=[True, False]
    ).reset_index(drop=True)

    print(f"  COVID recovery summary rows (All Students): {len(summary):,}")

    # ── Print headline findings ───────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("CITYWIDE SUMMARY — All Students (school averages)")
    print("─" * 70)

    for subj in sorted(all_stu["Subject"].unique()):
        sub = all_stu[all_stu["Subject"] == subj]
        avg_impact = sub["covid_impact_pp"].mean()
        avg_recovery = sub["recovery_pp"].mean()
        avg_net = sub["net_vs_precovid_pp"].mean()
        n_schools = sub["School Name"].nunique()
        print(f"\n  {subj}  ({n_schools} schools with 2019 data)")
        print(f"    Avg COVID impact (2019→2022)    : {avg_impact:+.2f} pp")
        print(f"    Avg recovery (2022→2024)        : {avg_recovery:+.2f} pp")
        print(f"    Avg net vs. pre-COVID (2024−2019): {avg_net:+.2f} pp")

    # Status distribution
    print("\n  Recovery Status Distribution (All Students, school-level):")
    status_counts_summary = summary["recovery_status"].value_counts()
    for status_label, n_schools in status_counts_summary.items():
        pct_share = 100.0 * n_schools / len(summary) if len(summary) > 0 else 0.0
        print(f"    {status_label:30s}  {n_schools:3d} schools ({pct_share:.0f}%)")

    # ── Save outputs ──────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    detail.to_csv(OUT_DETAIL, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"\n✓ Saved {len(detail):,} rows → {OUT_DETAIL}")
    print(f"✓ Saved {len(summary):,} rows → {OUT_SUMMARY}")
    print()
    print("=" * 70)
    print("COVID RECOVERY ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    run()
