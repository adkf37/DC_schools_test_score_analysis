"""
School Performance Trajectory Classification for DC Schools.

This script classifies each school's long-run proficiency trajectory by fitting
a linear trend to the school's annual All Students proficiency data across all
available years (2016–2024).  Unlike the same-grade YoY growth script (which
looks at consecutive-year changes) or the COVID recovery script (which focuses
on the 2019→2022→2024 window), this analysis takes the broadest possible view:
"Has this school been consistently improving, stable, or declining over the full
multi-year period available in the dataset?"

A minimum of 3 distinct years with valid data are required before a slope is
estimated; schools with fewer years are flagged as "Insufficient Data".

Key metrics computed for every school × subject combination (All Students):

  n_years_with_data   — number of distinct school years with valid proficiency data
  first_year          — earliest school year in the school's data window
  last_year           — latest school year in the school's data window
  avg_proficiency_pct — simple mean of annual proficiency values across all years
  first_proficiency   — proficiency in the first observed year
  last_proficiency    — proficiency in the last observed year
  total_change_pp     — last_proficiency − first_proficiency
  trend_slope_pp_yr   — OLS slope (pp per calendar year) from linear regression
                         on year → proficiency
  r_squared           — R² of the linear fit (goodness of fit; 0–1)
  trajectory_class    — one of:
                         "Strongly Improving"   (slope >  2.0 pp/yr)
                         "Improving"            (slope ≥  0.5 pp/yr)
                         "Stable"               (|slope| <  0.5 pp/yr)
                         "Declining"            (slope ≤ −0.5 pp/yr)
                         "Strongly Declining"   (slope < −2.0 pp/yr)
                         "Insufficient Data"    (fewer than 3 years with data)

Inputs:
    output_data/proficiency_trends.csv   – produced by proficiency_trend_analysis.py

Outputs:
    output_data/school_trajectory_classification.csv  — one row per school ×
        subject (All Students) with trend metrics and trajectory class

Usage:
    python src/school_trajectory_analysis.py
"""
import os
import sys
import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, ".."))
OUTPUT_PATH = os.path.join(REPO_ROOT, "output_data")

TRENDS_FILE = os.path.join(OUTPUT_PATH, "proficiency_trends.csv")
OUT_FILE = os.path.join(OUTPUT_PATH, "school_trajectory_classification.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
# Minimum number of distinct years with valid data to fit a trend
MIN_YEARS = 3

# All-Students labels used in proficiency_trends.csv
ALL_STUDENTS_LABELS = {"All Students", "All", "Total"}

# Trajectory classification thresholds (pp per year)
STRONGLY_IMPROVING_THRESHOLD = 2.0
IMPROVING_THRESHOLD = 0.5
DECLINING_THRESHOLD = -0.5
STRONGLY_DECLINING_THRESHOLD = -2.0


# ── Helper ────────────────────────────────────────────────────────────────────

def _classify_trajectory(slope: float) -> str:
    """Return a trajectory-class label from a linear slope (pp/yr)."""
    if slope > STRONGLY_IMPROVING_THRESHOLD:
        return "Strongly Improving"
    if slope >= IMPROVING_THRESHOLD:
        return "Improving"
    if slope > DECLINING_THRESHOLD:
        return "Stable"
    if slope >= STRONGLY_DECLINING_THRESHOLD:
        return "Declining"
    return "Strongly Declining"


def _compute_trajectory(years: np.ndarray, pcts: np.ndarray):
    """
    Fit an OLS line to (year, proficiency_pct) pairs.
    Returns (slope, r_squared).  If fewer than MIN_YEARS points, returns (NaN, NaN).
    """
    if len(years) < MIN_YEARS:
        return np.nan, np.nan

    # polyfit returns [slope, intercept]
    coeffs = np.polyfit(years, pcts, 1)
    slope = coeffs[0]

    # R²
    predicted = np.polyval(coeffs, years)
    ss_res = np.sum((pcts - predicted) ** 2)
    ss_tot = np.sum((pcts - pcts.mean()) ** 2)
    r_sq = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return slope, r_sq


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("SCHOOL PERFORMANCE TRAJECTORY CLASSIFICATION")
    print("=" * 70)

    # ── Load data ─────────────────────────────────────────────────────────────
    if not os.path.isfile(TRENDS_FILE):
        print(f"ERROR: {TRENDS_FILE} not found.")
        print("       Run src/proficiency_trend_analysis.py first.")
        sys.exit(1)

    trends = pd.read_csv(TRENDS_FILE)
    print(f"\n  Loaded {len(trends):,} rows from proficiency_trends.csv")

    # Keep All Students only
    all_stu = trends[trends["Student Group Value"].isin(ALL_STUDENTS_LABELS)].copy()

    # Ensure proficiency_pct is numeric
    all_stu["proficiency_pct"] = pd.to_numeric(all_stu["proficiency_pct"], errors="coerce")
    all_stu["year"] = pd.to_numeric(all_stu["year"], errors="coerce")
    all_stu = all_stu.dropna(subset=["proficiency_pct", "year"])

    print(f"  After All Students filter: {len(all_stu):,} rows")
    print(f"  Years available: {sorted(all_stu['year'].unique())}")
    print(f"  Schools        : {all_stu['School Name'].nunique()}")

    # ── Aggregate to school × subject × year ─────────────────────────────────
    # Average across grades within a school × subject × year
    school_year = (
        all_stu.groupby(["School Name", "Subject", "year"], as_index=False)
        .agg(proficiency_pct=("proficiency_pct", "mean"))
    )

    # ── Compute trajectory per school × subject ───────────────────────────────
    records = []
    for (school_name, subject), grp in school_year.groupby(["School Name", "Subject"]):
        grp = grp.sort_values("year")
        valid = grp.dropna(subset=["proficiency_pct"])

        n_years = len(valid)
        if n_years == 0:
            continue

        years_arr = valid["year"].values.astype(float)
        pcts_arr = valid["proficiency_pct"].values

        first_year = int(valid["year"].iloc[0])
        last_year = int(valid["year"].iloc[-1])
        first_pct = round(pcts_arr[0], 2)
        last_pct = round(pcts_arr[-1], 2)
        avg_pct = round(pcts_arr.mean(), 2)
        total_change = round(last_pct - first_pct, 2)

        slope, r_sq = _compute_trajectory(years_arr, pcts_arr)

        if np.isnan(slope):
            traj_class = "Insufficient Data"
        else:
            traj_class = _classify_trajectory(slope)

        records.append({
            "School Name": school_name,
            "Subject": subject,
            "n_years_with_data": n_years,
            "first_year": first_year,
            "last_year": last_year,
            "avg_proficiency_pct": avg_pct,
            "first_proficiency_pct": first_pct,
            "last_proficiency_pct": last_pct,
            "total_change_pp": total_change,
            "trend_slope_pp_yr": round(slope, 3) if not np.isnan(slope) else np.nan,
            "r_squared": round(r_sq, 3) if not np.isnan(r_sq) else np.nan,
            "trajectory_class": traj_class,
        })

    result = pd.DataFrame(records)
    result = result.sort_values(
        ["Subject", "trend_slope_pp_yr"], ascending=[True, False]
    ).reset_index(drop=True)

    print(f"\n  School trajectory rows: {len(result):,}")

    # ── Print headline findings ───────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("TRAJECTORY DISTRIBUTION — All Students (school-level averages)")
    print("─" * 70)

    for subj in sorted(result["Subject"].unique()):
        sub = result[result["Subject"] == subj]
        print(f"\n  {subj}  ({len(sub)} schools)")
        dist = sub["trajectory_class"].value_counts()
        for cls, n in dist.items():
            pct = 100.0 * n / len(sub) if len(sub) > 0 else 0.0
            print(f"    {cls:25s}  {n:3d} schools ({pct:.0f}%)")

        valid_slope = sub.dropna(subset=["trend_slope_pp_yr"])
        if not valid_slope.empty:
            avg_slope = valid_slope["trend_slope_pp_yr"].mean()
            print(f"    Avg trend slope: {avg_slope:+.3f} pp/yr")

    print("\n  Top 5 Improving Schools (ELA, All Students):")
    top_ela = result[
        (result["Subject"] == "ELA") & result["trend_slope_pp_yr"].notna()
    ].sort_values("trend_slope_pp_yr", ascending=False).head(5)
    for _, row in top_ela.iterrows():
        print(
            f"    {row['School Name']:45s}  slope={row['trend_slope_pp_yr']:+.3f} pp/yr"
            f"  ({row['first_proficiency_pct']:.1f}% → {row['last_proficiency_pct']:.1f}%)"
        )

    print("\n  Top 5 Improving Schools (Math, All Students):")
    top_math = result[
        (result["Subject"] == "Math") & result["trend_slope_pp_yr"].notna()
    ].sort_values("trend_slope_pp_yr", ascending=False).head(5)
    for _, row in top_math.iterrows():
        print(
            f"    {row['School Name']:45s}  slope={row['trend_slope_pp_yr']:+.3f} pp/yr"
            f"  ({row['first_proficiency_pct']:.1f}% → {row['last_proficiency_pct']:.1f}%)"
        )

    # ── Save output ───────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    result.to_csv(OUT_FILE, index=False)
    print(f"\n✓ Saved {len(result):,} rows → {OUT_FILE}")
    print()
    print("=" * 70)
    print("SCHOOL TRAJECTORY CLASSIFICATION COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    run()
