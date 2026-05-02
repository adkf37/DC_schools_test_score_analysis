"""
Multi-Metric School Performance Index — DC Schools Test Score Analysis.

This script synthesises the four major analytical dimensions already computed
by the pipeline into a single composite score for each school × subject
(All Students):

    1. Proficiency Score   — percentile rank of average proficiency level
                             (source: school_consistency.csv, avg_proficiency_pct)
    2. Growth Score        — percentile rank of average cohort-growth pp
                             (source: school_rankings.csv, avg_pp_growth)
    3. Recovery Score      — percentile rank of COVID recovery pp (2022→2024)
                             (source: covid_recovery_summary.csv, recovery_pp)
    4. Trajectory Score    — percentile rank of long-run OLS trend slope (pp/yr)
                             (source: school_trajectory_classification.csv,
                              trend_slope_pp_yr; Insufficient Data excluded)

Each component is rescaled to a 0–100 percentile rank within its subject.
The composite is the simple mean of the available component scores.
Schools with fewer than 2 valid components receive an "Insufficient Data"
composite class.

Composite quintile labels (based on composite_score):
    Q5 – Top Performers         ≥ 80th percentile
    Q4 – Above Average          60–80th percentile
    Q3 – Middle                 40–60th percentile
    Q2 – Below Average          20–40th percentile
    Q1 – Bottom Performers      < 20th percentile
    Insufficient Data           fewer than 2 valid component scores

Key outputs:
    school_performance_index.csv  — one row per school × subject; includes
                                    all component scores, composite score,
                                    composite quintile, and source metrics
    performance_index_summary.csv — per quintile × subject: n_schools,
                                    mean composite, mean proficiency, mean
                                    cohort growth, mean recovery pp

Inputs (all optional — missing components are silently omitted from the
composite for the affected schools):
    output_data/school_consistency.csv
    output_data/school_rankings.csv
    output_data/covid_recovery_summary.csv
    output_data/school_trajectory_classification.csv

Usage:
    python src/school_performance_index.py

Dependencies:
    Run after school_consistency_analysis.py (ideally after the full pipeline).
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import percentileofscore

# ── Paths ─────────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, ".."))
OUTPUT_PATH = os.path.join(REPO_ROOT, "output_data")

CONSISTENCY_FILE = os.path.join(OUTPUT_PATH, "school_consistency.csv")
RANKINGS_FILE = os.path.join(OUTPUT_PATH, "school_rankings.csv")
COVID_RECOVERY_FILE = os.path.join(OUTPUT_PATH, "covid_recovery_summary.csv")
TRAJECTORY_FILE = os.path.join(OUTPUT_PATH, "school_trajectory_classification.csv")

OUT_INDEX = os.path.join(OUTPUT_PATH, "school_performance_index.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "performance_index_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
MIN_COMPONENTS = 2   # minimum valid component scores for a composite rating

QUINTILE_LABELS = [
    "Q5 – Top Performers",
    "Q4 – Above Average",
    "Q3 – Middle",
    "Q2 – Below Average",
    "Q1 – Bottom Performers",
]
QUINTILE_ORDER = QUINTILE_LABELS + ["Insufficient Data"]

# All-Students labels in the source files
ALL_STUDENTS_LABELS = {"All Students", "All", "Total"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _pct_rank_series(series: pd.Series) -> pd.Series:
    """
    Compute 0–100 percentile rank for each value in the series, ignoring NaN.
    Uses scipy percentileofscore with kind='mean' for fair tied-rank treatment.
    """
    valid = series.dropna().values
    if len(valid) == 0:
        return pd.Series(np.nan, index=series.index)

    def _rank(v):
        if pd.isna(v):
            return np.nan
        return float(percentileofscore(valid, v, kind="mean"))

    return series.apply(_rank)


def _assign_quintile(score: float, thresholds: dict) -> str:
    """Return the quintile label for a composite score given per-subject thresholds."""
    if np.isnan(score):
        return "Insufficient Data"
    if score >= thresholds["q4"]:
        return "Q5 – Top Performers"
    if score >= thresholds["q3"]:
        return "Q4 – Above Average"
    if score >= thresholds["q2"]:
        return "Q3 – Middle"
    if score >= thresholds["q1"]:
        return "Q2 – Below Average"
    return "Q1 – Bottom Performers"


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("MULTI-METRIC SCHOOL PERFORMANCE INDEX")
    print("=" * 70)

    # ── Load source files ─────────────────────────────────────────────────────

    # 1. Proficiency (avg_proficiency_pct per school × subject)
    proficiency_df = pd.DataFrame()
    if os.path.isfile(CONSISTENCY_FILE):
        raw = pd.read_csv(CONSISTENCY_FILE)
        # Keep All-Students proxy (consistency already filtered to All Students)
        proficiency_df = raw[["School Name", "Subject", "avg_proficiency_pct"]].copy()
        print(f"\n  Loaded school_consistency.csv: {len(proficiency_df):,} rows "
              f"({proficiency_df['School Name'].nunique()} schools)")
    else:
        print(f"\n  NOTE: school_consistency.csv not found — proficiency component skipped.")

    # 2. Cohort growth (avg_pp_growth per school × subject)
    growth_df = pd.DataFrame()
    if os.path.isfile(RANKINGS_FILE):
        raw = pd.read_csv(RANKINGS_FILE)
        # Keep All Students rows if the column is present; otherwise use all rows
        if "Student Group Value" in raw.columns:
            raw = raw[raw["Student Group Value"].isin(ALL_STUDENTS_LABELS)]
        growth_df = raw[["School Name", "Subject", "avg_pp_growth"]].copy()
        print(f"  Loaded school_rankings.csv: {len(growth_df):,} rows "
              f"({growth_df['School Name'].nunique()} schools)")
    else:
        print(f"  NOTE: school_rankings.csv not found — growth component skipped.")

    # 3. COVID recovery (recovery_pp per school × subject)
    recovery_df = pd.DataFrame()
    if os.path.isfile(COVID_RECOVERY_FILE):
        raw = pd.read_csv(COVID_RECOVERY_FILE)
        if "Student Group Value" in raw.columns:
            raw = raw[raw["Student Group Value"].isin(ALL_STUDENTS_LABELS)]
        recovery_df = raw[["School Name", "Subject", "recovery_pp"]].copy()
        print(f"  Loaded covid_recovery_summary.csv: {len(recovery_df):,} rows "
              f"({recovery_df['School Name'].nunique()} schools)")
    else:
        print(f"  NOTE: covid_recovery_summary.csv not found — recovery component skipped.")

    # 4. Trajectory slope (trend_slope_pp_yr per school × subject)
    trajectory_df = pd.DataFrame()
    if os.path.isfile(TRAJECTORY_FILE):
        raw = pd.read_csv(TRAJECTORY_FILE)
        # Exclude rows with no valid slope (Insufficient Data)
        raw = raw.dropna(subset=["trend_slope_pp_yr"])
        trajectory_df = raw[["School Name", "Subject", "trend_slope_pp_yr"]].copy()
        print(f"  Loaded school_trajectory_classification.csv: "
              f"{len(trajectory_df):,} rows with valid slope "
              f"({trajectory_df['School Name'].nunique()} schools)")
    else:
        print(f"  NOTE: school_trajectory_classification.csv not found "
              f"— trajectory component skipped.")

    # Guard: need at least one component
    if all(df.empty for df in [proficiency_df, growth_df, recovery_df, trajectory_df]):
        print("\nERROR: No source files found. Run the pipeline first:")
        print("  python src/school_consistency_analysis.py")
        print("  python src/generate_school_rankings.py")
        print("  python src/covid_recovery_analysis.py")
        print("  python src/school_trajectory_analysis.py")
        sys.exit(1)

    # ── Build a school × subject universe ────────────────────────────────────
    # Start from proficiency (largest coverage); augment with other subjects/schools
    universe_dfs = [df[["School Name", "Subject"]].drop_duplicates()
                    for df in [proficiency_df, growth_df, recovery_df, trajectory_df]
                    if not df.empty]
    universe = pd.concat(universe_dfs).drop_duplicates().reset_index(drop=True)
    print(f"\n  Universe: {len(universe):,} school × subject rows "
          f"({universe['School Name'].nunique()} schools)")

    # Merge in each component
    result = universe.copy()
    if not proficiency_df.empty:
        result = result.merge(
            proficiency_df.rename(columns={"avg_proficiency_pct": "proficiency_pct"}),
            on=["School Name", "Subject"], how="left",
        )
    else:
        result["proficiency_pct"] = np.nan

    if not growth_df.empty:
        result = result.merge(
            growth_df.rename(columns={"avg_pp_growth": "cohort_growth_pp"}),
            on=["School Name", "Subject"], how="left",
        )
    else:
        result["cohort_growth_pp"] = np.nan

    if not recovery_df.empty:
        result = result.merge(
            recovery_df.rename(columns={"recovery_pp": "covid_recovery_pp"}),
            on=["School Name", "Subject"], how="left",
        )
    else:
        result["covid_recovery_pp"] = np.nan

    if not trajectory_df.empty:
        result = result.merge(
            trajectory_df.rename(columns={"trend_slope_pp_yr": "trajectory_slope_pp_yr"}),
            on=["School Name", "Subject"], how="left",
        )
    else:
        result["trajectory_slope_pp_yr"] = np.nan

    # ── Compute percentile ranks within each subject ───────────────────────
    print("\n  Computing percentile ranks within each subject…")
    for subj in sorted(result["Subject"].unique()):
        mask = result["Subject"] == subj
        result.loc[mask, "proficiency_score"] = _pct_rank_series(
            result.loc[mask, "proficiency_pct"]
        ).values
        result.loc[mask, "growth_score"] = _pct_rank_series(
            result.loc[mask, "cohort_growth_pp"]
        ).values
        result.loc[mask, "recovery_score"] = _pct_rank_series(
            result.loc[mask, "covid_recovery_pp"]
        ).values
        result.loc[mask, "trajectory_score"] = _pct_rank_series(
            result.loc[mask, "trajectory_slope_pp_yr"]
        ).values

    # ── Composite score = mean of available component scores ─────────────
    component_cols = ["proficiency_score", "growth_score", "recovery_score", "trajectory_score"]
    result["n_components"] = result[component_cols].notna().sum(axis=1)
    result["composite_score"] = result.apply(
        lambda row: (
            float(np.nanmean([row[c] for c in component_cols
                               if not np.isnan(row[c])]))
            if row["n_components"] >= MIN_COMPONENTS
            else np.nan
        ),
        axis=1,
    )

    # ── Assign quintile labels ─────────────────────────────────────────────
    print("  Assigning quintile labels…")
    result["composite_quintile"] = "Insufficient Data"
    for subj in sorted(result["Subject"].unique()):
        mask = result["Subject"] == subj
        valid_scores = result.loc[mask & result["composite_score"].notna(), "composite_score"]
        if valid_scores.empty:
            continue
        thresholds = {
            "q1": float(np.percentile(valid_scores, 20)),
            "q2": float(np.percentile(valid_scores, 40)),
            "q3": float(np.percentile(valid_scores, 60)),
            "q4": float(np.percentile(valid_scores, 80)),
        }
        result.loc[mask, "composite_quintile"] = result.loc[mask, "composite_score"].apply(
            lambda s: _assign_quintile(s, thresholds)
        )

    # Round numeric columns
    for col in ("proficiency_pct", "cohort_growth_pp", "covid_recovery_pp",
                "trajectory_slope_pp_yr", "proficiency_score", "growth_score",
                "recovery_score", "trajectory_score", "composite_score"):
        if col in result.columns:
            result[col] = result[col].round(2)

    # Sort by subject then composite score descending
    quintile_sort = {q: i for i, q in enumerate(QUINTILE_ORDER)}
    result["_q_sort"] = result["composite_quintile"].map(quintile_sort).fillna(99)
    result = (
        result
        .sort_values(["Subject", "_q_sort", "composite_score"],
                     ascending=[True, True, False])
        .drop(columns=["_q_sort"])
        .reset_index(drop=True)
    )

    # Column order
    col_order = [
        "School Name", "Subject",
        "composite_score", "composite_quintile", "n_components",
        "proficiency_score", "growth_score", "recovery_score", "trajectory_score",
        "proficiency_pct", "cohort_growth_pp", "covid_recovery_pp", "trajectory_slope_pp_yr",
    ]
    col_order = [c for c in col_order if c in result.columns]
    result = result[col_order]

    # ── Print headline findings ───────────────────────────────────────────
    print("\n" + "─" * 70)
    print("COMPOSITE PERFORMANCE INDEX — QUINTILE DISTRIBUTION")
    print("─" * 70)
    for subj in sorted(result["Subject"].unique()):
        sub = result[result["Subject"] == subj]
        classified = sub[sub["composite_quintile"] != "Insufficient Data"]
        print(f"\n  {subj}  ({len(sub)} schools; {len(classified)} with composite score)")
        dist = sub["composite_quintile"].value_counts()
        for q in QUINTILE_ORDER:
            n = dist.get(q, 0)
            pct = 100.0 * n / len(sub) if len(sub) > 0 else 0
            print(f"    {q:35s}  {n:3d} schools ({pct:.0f}%)")

    print("\n  Top 5 Composite Performers (ELA):")
    top5_ela = result[(result["Subject"] == "ELA")
                      & result["composite_score"].notna()].head(5)
    for _, row in top5_ela.iterrows():
        print(
            f"    {row['School Name']:45s}"
            f"  composite={row['composite_score']:.1f}"
            f"  ({row['composite_quintile']})"
        )

    print("\n  Top 5 Composite Performers (Math):")
    top5_math = result[(result["Subject"] == "Math")
                       & result["composite_score"].notna()].head(5)
    for _, row in top5_math.iterrows():
        print(
            f"    {row['School Name']:45s}"
            f"  composite={row['composite_score']:.1f}"
            f"  ({row['composite_quintile']})"
        )

    # ── Summary by quintile ───────────────────────────────────────────────
    summary_records = []
    for (quintile, subj), grp in result.groupby(["composite_quintile", "Subject"]):
        valid = grp.dropna(subset=["composite_score"])
        summary_records.append({
            "composite_quintile": quintile,
            "Subject": subj,
            "n_schools": len(grp),
            "avg_composite_score": round(valid["composite_score"].mean(), 2)
            if not valid.empty else np.nan,
            "avg_proficiency_pct": round(grp["proficiency_pct"].dropna().mean(), 2)
            if grp["proficiency_pct"].notna().any() else np.nan,
            "avg_cohort_growth_pp": round(grp["cohort_growth_pp"].dropna().mean(), 2)
            if grp["cohort_growth_pp"].notna().any() else np.nan,
            "avg_covid_recovery_pp": round(grp["covid_recovery_pp"].dropna().mean(), 2)
            if grp["covid_recovery_pp"].notna().any() else np.nan,
            "avg_trajectory_slope_pp_yr": round(
                grp["trajectory_slope_pp_yr"].dropna().mean(), 2
            ) if grp["trajectory_slope_pp_yr"].notna().any() else np.nan,
        })

    summary = pd.DataFrame(summary_records)
    q_sort = {q: i for i, q in enumerate(QUINTILE_ORDER)}
    summary["_q_sort"] = summary["composite_quintile"].map(q_sort).fillna(99)
    summary = (
        summary
        .sort_values(["Subject", "_q_sort"])
        .drop(columns=["_q_sort"])
        .reset_index(drop=True)
    )

    print("\n" + "─" * 70)
    print("SUMMARY BY QUINTILE")
    print("─" * 70)
    for subj in sorted(summary["Subject"].unique()):
        sub = summary[summary["Subject"] == subj]
        print(f"\n  {subj}")
        for _, row in sub.iterrows():
            print(
                f"    {row['composite_quintile']:35s}"
                f"  n={row['n_schools']:3d}"
                f"  avg_composite={row['avg_composite_score'] if pd.notna(row['avg_composite_score']) else 'n/a':>6}"
                f"  avg_prof={row['avg_proficiency_pct'] if pd.notna(row['avg_proficiency_pct']) else 'n/a':>6}"
            )

    # ── Save outputs ──────────────────────────────────────────────────────
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    result.to_csv(OUT_INDEX, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"\n✓ Saved {len(result):,} rows → {OUT_INDEX}")
    print(f"✓ Saved {len(summary):,} rows → {OUT_SUMMARY}")
    print()
    print("=" * 70)
    print("SCHOOL PERFORMANCE INDEX COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    run()
