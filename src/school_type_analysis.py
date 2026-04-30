"""
School Type Performance Analysis for DC Schools.

This script classifies each school into a grade-band type (Elementary, Middle
School, High School, Elementary-Middle, or Middle-High) based on the grades it
served across all available years.  It then computes proficiency trends,
COVID recovery metrics, and cohort growth averages by school type, allowing
policy researchers to compare performance patterns across fundamentally
different school configurations.

School type classification is based on the Grade of Enrollment column:
  - Elementary          — serves only Grades 3-5
  - Middle School       — serves only Grades 6-8
  - High School         — serves only HS (high school)
  - Elementary-Middle   — serves Grades 3-8 (K-8 or similar)
  - Middle-High         — serves Grades 6-12 (combines middle and high school)

Key metrics computed:

  Per school (school_type_by_school.csv):
    school_type             — one of the five labels above
    grades_served           — comma-separated list of distinct grade labels
    n_years_present         — number of distinct years the school appears in data
    first_year              — earliest year in the school's data
    last_year               — latest year in the school's data

  Per school type × subject × year (school_type_proficiency.csv):
    avg_proficiency_pct     — mean proficiency across schools of this type
    n_schools               — number of schools with valid data for this type/year
    median_proficiency_pct  — median proficiency

  Per school type × subject (school_type_summary.csv):
    n_schools               — distinct schools of this type with any proficiency data
    avg_proficiency_pct     — grand average across all years
    covid_impact_pp         — avg COVID impact 2019→2022 (All Students)
    recovery_pp             — avg recovery 2022→2024 (All Students)
    net_vs_precovid_pp      — avg net change 2024 vs 2019 (All Students)
    avg_cohort_growth_pp    — avg cohort growth (All Students, from cohort summary)

Inputs:
    output_data/combined_all_years.csv        – produced by load_wide_format_data.py
    output_data/cohort_growth_summary.csv     – produced by analyze_cohort_growth.py (optional)
    output_data/covid_recovery_summary.csv    – produced by covid_recovery_analysis.py (optional)

Outputs:
    output_data/school_type_by_school.csv     – one row per school with type classification
    output_data/school_type_proficiency.csv   – avg proficiency by school type × subject × year
    output_data/school_type_summary.csv       – per school-type × subject aggregate with COVID
                                               recovery and cohort growth metrics

Usage:
    python src/school_type_analysis.py
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
COHORT_SUMMARY_FILE = os.path.join(OUTPUT_PATH, "cohort_growth_summary.csv")
COVID_RECOVERY_FILE = os.path.join(OUTPUT_PATH, "covid_recovery_summary.csv")

OUT_BY_SCHOOL = os.path.join(OUTPUT_PATH, "school_type_by_school.csv")
OUT_PROFICIENCY = os.path.join(OUTPUT_PATH, "school_type_proficiency.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "school_type_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
MIN_N = 10   # minimum student count to include a data point

# Grade membership sets for classification
ELEM_GRADES = {"Grade 3", "Grade 4", "Grade 5"}
MID_GRADES = {"Grade 6", "Grade 7", "Grade 8"}
HS_GRADES = {"HS"}

# COVID analysis reference years
PRE_COVID_YEAR = 2019
COVID_YEAR = 2022
LATEST_YEAR = 2024

ALL_STUDENTS_LABELS = {"All Students", "All", "Total"}

# Ordered school type labels for consistent display
SCHOOL_TYPE_ORDER = [
    "Elementary",
    "Middle School",
    "High School",
    "Elementary-Middle",
    "Middle-High",
]


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


def _classify_school_type(grades: set) -> str:
    """
    Assign a school-type label from the set of grade labels a school serves.

    Classification priority (most specific first):
      Elementary-Middle — serves both Grades 3-5 and Grades 6-8
      Middle-High       — serves Grades 6-8 and HS
      Elementary        — serves only Grades 3-5 (may also serve K-2)
      Middle School     — serves only Grades 6-8
      High School       — serves only HS
    """
    has_elem = bool(ELEM_GRADES & grades)
    has_mid = bool(MID_GRADES & grades)
    has_hs = bool(HS_GRADES & grades)

    if has_elem and has_mid and not has_hs:
        return "Elementary-Middle"
    if has_mid and has_hs and not has_elem:
        return "Middle-High"
    if has_elem and not has_mid and not has_hs:
        return "Elementary"
    if has_mid and not has_elem and not has_hs:
        return "Middle School"
    if has_hs and not has_elem and not has_mid:
        return "High School"
    # Fallback: use dominant grades
    if has_elem:
        return "Elementary"
    if has_mid:
        return "Middle School"
    return "High School"


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("SCHOOL TYPE PERFORMANCE ANALYSIS")
    print("=" * 70)

    # ── Load combined data ─────────────────────────────────────────────────
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

    # Apply minimum-N filter
    df = df[df["total_count"].fillna(0) >= MIN_N]

    # Drop rows without a usable percent value or year
    df = df.dropna(subset=["percent_value", "year"])

    print(f"  After filtering: {len(df):,} rows")
    print(f"  Years available: {sorted(df['year'].dropna().unique())}")
    print(f"  Schools        : {df['School Name'].nunique()}")

    # ── Build school type map ──────────────────────────────────────────────
    grade_col = "Grade of Enrollment"

    # Collect all grades each school has ever served
    school_grades_all = (
        df.groupby("School Name")[grade_col]
        .apply(set)
    )

    school_type_map = school_grades_all.apply(_classify_school_type)

    # Build by-school classification table
    school_meta = []
    for school_name, grades in school_grades_all.items():
        school_years = df[df["School Name"] == school_name]["year"].dropna()
        school_meta.append({
            "School Name": school_name,
            "School Type": school_type_map[school_name],
            "Grades Served": ", ".join(sorted(grades)),
            "n_years_present": school_years.nunique(),
            "first_year": int(school_years.min()),
            "last_year": int(school_years.max()),
        })

    by_school = pd.DataFrame(school_meta).sort_values(
        ["School Type", "School Name"]
    ).reset_index(drop=True)

    print(f"\n  School type distribution:")
    for stype in SCHOOL_TYPE_ORDER:
        n = (by_school["School Type"] == stype).sum()
        print(f"    {stype:22s}  {n:3d} schools")

    # ── Merge school type into main data ──────────────────────────────────
    df["School Type"] = df["School Name"].map(school_type_map)

    # ── Proficiency by school type × subject × year ───────────────────────
    all_stu = df[df["Student Group Value"].isin(ALL_STUDENTS_LABELS)].copy()

    proficiency_by_type = (
        all_stu.groupby(["School Type", "Subject", "year"], as_index=False)
        .agg(
            avg_proficiency_pct=("percent_value", "mean"),
            median_proficiency_pct=("percent_value", "median"),
            n_schools=("School Name", "nunique"),
        )
        .round({"avg_proficiency_pct": 2, "median_proficiency_pct": 2})
    )
    proficiency_by_type["year"] = proficiency_by_type["year"].astype(int)
    proficiency_by_type = proficiency_by_type.sort_values(
        ["Subject", "School Type", "year"]
    ).reset_index(drop=True)

    # ── Summary: grand average proficiency per school type × subject ───────
    type_avg = (
        all_stu.groupby(["School Type", "Subject"], as_index=False)
        .agg(
            n_schools=("School Name", "nunique"),
            avg_proficiency_pct=("percent_value", "mean"),
        )
        .round({"avg_proficiency_pct": 2})
    )

    # ── COVID recovery metrics by school type × subject ────────────────────
    covid_df = pd.DataFrame()
    if os.path.isfile(COVID_RECOVERY_FILE):
        covid_raw = pd.read_csv(COVID_RECOVERY_FILE)
        # Merge school type
        covid_raw = covid_raw.merge(
            by_school[["School Name", "School Type"]],
            on="School Name", how="left",
        )
        covid_all = covid_raw[covid_raw["School Name"].notna()].copy()
        covid_grp = (
            covid_all.groupby(["School Type", "Subject"], as_index=False)
            .agg(
                covid_impact_pp=("covid_impact_pp", "mean"),
                recovery_pp=("recovery_pp", "mean"),
                net_vs_precovid_pp=("net_vs_precovid_pp", "mean"),
            )
            .round(2)
        )
        covid_df = covid_grp
        print(f"\n  Loaded COVID recovery data: {len(covid_raw):,} rows")

    # ── Cohort growth metrics by school type × subject ─────────────────────
    cohort_df = pd.DataFrame()
    if os.path.isfile(COHORT_SUMMARY_FILE):
        cohort_raw = pd.read_csv(COHORT_SUMMARY_FILE)
        cohort_raw = cohort_raw.merge(
            by_school[["School Name", "School Type"]],
            on="School Name", how="left",
        )
        cohort_all = cohort_raw[
            cohort_raw["Student Group Value"].isin(ALL_STUDENTS_LABELS)
            & cohort_raw["School Type"].notna()
        ].copy()
        cohort_grp = (
            cohort_all.groupby(["School Type", "Subject"], as_index=False)
            .agg(avg_cohort_growth_pp=("avg_pp_growth", "mean"))
            .round(2)
        )
        cohort_df = cohort_grp
        print(f"  Loaded cohort growth summary: {len(cohort_raw):,} rows")

    # ── Merge summary metrics ──────────────────────────────────────────────
    summary = type_avg.copy()
    if not covid_df.empty:
        summary = summary.merge(covid_df, on=["School Type", "Subject"], how="left")
    if not cohort_df.empty:
        summary = summary.merge(cohort_df, on=["School Type", "Subject"], how="left")

    # Ensure school type ordering
    type_order = {t: i for i, t in enumerate(SCHOOL_TYPE_ORDER)}
    summary["_type_order"] = summary["School Type"].map(type_order).fillna(99)
    summary = summary.sort_values(["_type_order", "Subject"]).drop(
        columns=["_type_order"]
    ).reset_index(drop=True)

    # ── Print headline findings ───────────────────────────────────────────
    print("\n" + "─" * 70)
    print("PROFICIENCY BY SCHOOL TYPE — All Students (2016–2024 average)")
    print("─" * 70)

    for subj in ("ELA", "Math"):
        sub = summary[summary["Subject"] == subj]
        print(f"\n  {subj}:")
        for _, row in sub.iterrows():
            covid_str = ""
            if "covid_impact_pp" in row and pd.notna(row.get("covid_impact_pp")):
                covid_str = (
                    f"  COVID impact {row['covid_impact_pp']:+.1f} pp,"
                    f" recovery {row.get('recovery_pp', np.nan):+.1f} pp"
                )
            growth_str = ""
            if "avg_cohort_growth_pp" in row and pd.notna(row.get("avg_cohort_growth_pp")):
                growth_str = f"  cohort growth {row['avg_cohort_growth_pp']:+.1f} pp/yr"
            print(
                f"    {row['School Type']:22s}"
                f"  avg proficiency {row['avg_proficiency_pct']:.1f}%"
                f"  ({int(row['n_schools'])} schools){covid_str}{growth_str}"
            )

    # ── Save outputs ──────────────────────────────────────────────────────
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    by_school.to_csv(OUT_BY_SCHOOL, index=False)
    proficiency_by_type.to_csv(OUT_PROFICIENCY, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"\n✓ Saved {len(by_school):,} rows  → {OUT_BY_SCHOOL}")
    print(f"✓ Saved {len(proficiency_by_type):,} rows  → {OUT_PROFICIENCY}")
    print(f"✓ Saved {len(summary):,} rows  → {OUT_SUMMARY}")
    print()
    print("=" * 70)
    print("SCHOOL TYPE PERFORMANCE ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    run()
