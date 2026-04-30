"""
School Performance Consistency Analysis for DC Schools.

This script measures how consistently each school's proficiency rates hold up
year to year by computing the standard deviation and coefficient of variation
(CV) of All Students proficiency across all available school years.  Unlike the
trajectory analysis (which asks "is this school improving or declining?"), this
analysis asks:

    "How stable or volatile is this school's performance year to year?"

A school can be a high-consistent performer (steady high proficiency), a
low-consistent performer (steady but low proficiency), or volatile (swings that
may reflect genuine instability, cohort-composition changes, or COVID
disruption).

Classification (applied only to schools with ≥ 3 years of valid data):

    - High-Consistent   — avg proficiency ≥ citywide median AND CV ≤ citywide
                          median CV  (stable above-average performance)
    - High-Volatile     — avg proficiency ≥ citywide median AND CV > citywide
                          median CV  (high but fluctuating)
    - Low-Consistent    — avg proficiency < citywide median AND CV ≤ citywide
                          median CV  (stable below-average performance)
    - Low-Volatile      — avg proficiency < citywide median AND CV > citywide
                          median CV  (low and fluctuating — possible intervention
                          target)
    - Insufficient Data — fewer than 3 years of valid data

Key metrics computed for every school × subject (All Students):

    n_years_with_data       — number of distinct years with valid proficiency data
    first_year / last_year  — observation window
    avg_proficiency_pct     — simple mean across all years
    std_proficiency_pct     — sample standard deviation across years (NaN if < 2 years)
    cv_proficiency_pct      — coefficient of variation = std/avg × 100 (%)
    min_proficiency_pct     — lowest annual value observed
    max_proficiency_pct     — highest annual value observed
    range_proficiency_pp    — max − min (total observed swing)
    consistency_class       — one of the five classes above

Citywide summary (consistency_class_summary.csv) reports, per class × subject:
    n_schools               — number of schools in the class
    avg_proficiency_pct     — mean of school-level averages
    avg_cv_pct              — mean CV
    avg_range_pp            — mean range (max − min)

Inputs:
    output_data/proficiency_trends.csv   – produced by proficiency_trend_analysis.py

Outputs:
    output_data/school_consistency.csv         — one row per school × subject
    output_data/consistency_class_summary.csv  — per consistency class × subject

Usage:
    python src/school_consistency_analysis.py

Dependencies:
    - output_data/proficiency_trends.csv (produced by proficiency_trend_analysis.py)
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
OUT_CONSISTENCY = os.path.join(OUTPUT_PATH, "school_consistency.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "consistency_class_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
MIN_YEARS = 3   # minimum years required for consistency classification

# All-Students labels used in proficiency_trends.csv
ALL_STUDENTS_LABELS = {"All Students", "All", "Total"}

# Ordered display list for consistency classes
CONSISTENCY_CLASS_ORDER = [
    "High-Consistent",
    "High-Volatile",
    "Low-Consistent",
    "Low-Volatile",
    "Insufficient Data",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _classify(avg_pct: float, cv: float, med_avg: float, med_cv: float) -> str:
    """Return a consistency-class label from avg proficiency and CV."""
    high = avg_pct >= med_avg
    stable = cv <= med_cv
    if high and stable:
        return "High-Consistent"
    if high and not stable:
        return "High-Volatile"
    if not high and stable:
        return "Low-Consistent"
    return "Low-Volatile"


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("SCHOOL PERFORMANCE CONSISTENCY ANALYSIS")
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
    all_stu["proficiency_pct"] = pd.to_numeric(all_stu["proficiency_pct"], errors="coerce")
    all_stu["year"] = pd.to_numeric(all_stu["year"], errors="coerce")
    all_stu = all_stu.dropna(subset=["proficiency_pct", "year"])

    print(f"  After All Students filter: {len(all_stu):,} rows")
    print(f"  Years: {sorted(all_stu['year'].unique())}")
    print(f"  Schools: {all_stu['School Name'].nunique()}")

    # ── Aggregate to school × subject × year ─────────────────────────────────
    # Average proficiency across grades within each school × subject × year
    school_year = (
        all_stu
        .groupby(["School Name", "Subject", "year"], as_index=False)
        .agg(proficiency_pct=("proficiency_pct", "mean"))
    )

    # ── Compute per-school consistency metrics ────────────────────────────────
    records = []
    for (school_name, subject), grp in school_year.groupby(["School Name", "Subject"]):
        valid = grp.dropna(subset=["proficiency_pct"]).sort_values("year")
        n_years = len(valid)
        if n_years == 0:
            continue

        pcts = valid["proficiency_pct"].values
        years = valid["year"].values

        avg_pct = float(np.mean(pcts))
        std_pct = float(np.std(pcts, ddof=1)) if n_years >= 2 else np.nan
        cv_pct = float(std_pct / avg_pct * 100) if (not np.isnan(std_pct) and avg_pct > 0) else np.nan
        min_pct = float(np.min(pcts))
        max_pct = float(np.max(pcts))
        range_pp = float(max_pct - min_pct)

        records.append({
            "School Name": school_name,
            "Subject": subject,
            "n_years_with_data": n_years,
            "first_year": int(years[0]),
            "last_year": int(years[-1]),
            "avg_proficiency_pct": round(avg_pct, 2),
            "std_proficiency_pct": round(std_pct, 2) if not np.isnan(std_pct) else np.nan,
            "cv_proficiency_pct": round(cv_pct, 2) if not np.isnan(cv_pct) else np.nan,
            "min_proficiency_pct": round(min_pct, 2),
            "max_proficiency_pct": round(max_pct, 2),
            "range_proficiency_pp": round(range_pp, 2),
            # Classification filled in after computing citywide medians
            "consistency_class": "Insufficient Data",
        })

    result = pd.DataFrame(records)
    print(f"\n  School × subject rows: {len(result):,}")

    # ── Classify using citywide median cut-points ─────────────────────────────
    # Only schools with ≥ MIN_YEARS are eligible for a full class
    classifiable = result[result["n_years_with_data"] >= MIN_YEARS].copy()

    for subject in sorted(result["Subject"].unique()):
        sub_cls = classifiable[classifiable["Subject"] == subject]
        if sub_cls.empty:
            continue
        valid_cv = sub_cls["cv_proficiency_pct"].dropna()
        valid_avg = sub_cls["avg_proficiency_pct"].dropna()
        if valid_cv.empty or valid_avg.empty:
            continue

        med_avg = float(valid_avg.median())
        med_cv = float(valid_cv.median())

        # Apply classification
        mask = (
            (result["Subject"] == subject)
            & (result["n_years_with_data"] >= MIN_YEARS)
            & result["cv_proficiency_pct"].notna()
        )
        result.loc[mask, "consistency_class"] = result.loc[mask].apply(
            lambda row: _classify(
                row["avg_proficiency_pct"], row["cv_proficiency_pct"],
                med_avg, med_cv,
            ),
            axis=1,
        )

        print(
            f"\n  {subject}: median avg proficiency = {med_avg:.2f}%,"
            f" median CV = {med_cv:.2f}%"
        )

    # Sort by subject then consistency class
    class_order_map = {c: i for i, c in enumerate(CONSISTENCY_CLASS_ORDER)}
    result["_class_sort"] = result["consistency_class"].map(
        lambda c: class_order_map.get(c, 99)
    )
    result = result.sort_values(
        ["Subject", "_class_sort", "avg_proficiency_pct"],
        ascending=[True, True, False],
    ).drop(columns=["_class_sort"]).reset_index(drop=True)

    # ── Print headline findings ───────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("CONSISTENCY DISTRIBUTION — All Students (school-level, ≥ 3 years)")
    print("─" * 70)

    for subj in sorted(result["Subject"].unique()):
        sub = result[result["Subject"] == subj]
        print(f"\n  {subj}  ({len(sub)} schools total)")
        dist = sub["consistency_class"].value_counts()
        for cls in CONSISTENCY_CLASS_ORDER:
            n = dist.get(cls, 0)
            pct_share = 100.0 * n / len(sub) if len(sub) > 0 else 0.0
            print(f"    {cls:25s}  {n:3d} schools ({pct_share:.0f}%)")

    print("\n  Top 5 High-Consistent Schools (ELA, All Students — highest avg):")
    top_hc_ela = result[
        (result["Subject"] == "ELA") & (result["consistency_class"] == "High-Consistent")
    ].head(5)
    for _, row in top_hc_ela.iterrows():
        print(
            f"    {row['School Name']:45s}"
            f"  avg={row['avg_proficiency_pct']:.1f}%  CV={row['cv_proficiency_pct']:.1f}%"
        )

    print("\n  Top 5 Low-Volatile Schools (ELA — highest CV among below-median avg):")
    low_vol_ela = result[
        (result["Subject"] == "ELA") & (result["consistency_class"] == "Low-Volatile")
    ].sort_values("cv_proficiency_pct", ascending=False).head(5)
    for _, row in low_vol_ela.iterrows():
        print(
            f"    {row['School Name']:45s}"
            f"  avg={row['avg_proficiency_pct']:.1f}%  CV={row['cv_proficiency_pct']:.1f}%"
        )

    # ── Summary by consistency class ─────────────────────────────────────────
    summary_records = []
    for (cls, subj), grp in result.groupby(["consistency_class", "Subject"]):
        valid = grp.dropna(subset=["avg_proficiency_pct"])
        summary_records.append({
            "consistency_class": cls,
            "Subject": subj,
            "n_schools": len(valid),
            "avg_proficiency_pct": round(valid["avg_proficiency_pct"].mean(), 2) if not valid.empty else np.nan,
            "avg_cv_pct": round(valid["cv_proficiency_pct"].dropna().mean(), 2) if not valid["cv_proficiency_pct"].dropna().empty else np.nan,
            "avg_range_pp": round(valid["range_proficiency_pp"].dropna().mean(), 2) if not valid["range_proficiency_pp"].dropna().empty else np.nan,
        })

    summary = pd.DataFrame(summary_records)
    summary["_class_sort"] = summary["consistency_class"].map(
        lambda c: class_order_map.get(c, 99)
    )
    summary = summary.sort_values(["Subject", "_class_sort"]).drop(columns=["_class_sort"]).reset_index(drop=True)

    print("\n" + "─" * 70)
    print("SUMMARY BY CONSISTENCY CLASS")
    print("─" * 70)
    for subj in sorted(summary["Subject"].unique()):
        sub = summary[summary["Subject"] == subj]
        print(f"\n  {subj}")
        for _, row in sub.iterrows():
            print(
                f"    {row['consistency_class']:25s}"
                f"  n={row['n_schools']:3d}"
                f"  avg={row['avg_proficiency_pct']:5.1f}%"
                f"  avg_CV={row['avg_cv_pct']:5.1f}%"
                f"  avg_range={row['avg_range_pp']:5.1f} pp"
            )

    # ── Save outputs ──────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    result.to_csv(OUT_CONSISTENCY, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"\n✓ Saved {len(result):,} rows → {OUT_CONSISTENCY}")
    print(f"✓ Saved {len(summary):,} rows → {OUT_SUMMARY}")
    print()
    print("=" * 70)
    print("SCHOOL CONSISTENCY ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    run()
