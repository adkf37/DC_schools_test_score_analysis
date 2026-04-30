"""
Grade-Level Performance Analysis for DC Schools.

This script computes proficiency metrics broken down by specific grade of
enrollment (Grade 3 through Grade 8 and High School) for every subject and
year.  Unlike the school-type analysis (which aggregates by grade-band) or
the YoY analysis (which focuses on consecutive-year changes at one school),
this analysis asks:

    "Across all DC schools, which grades show the highest and lowest
     proficiency, and how has grade-level performance changed over time?"

Key metrics computed:

  Per grade × subject × year (grade_level_proficiency.csv):
    n_schools           — number of schools with valid data for this cell
    avg_proficiency_pct — mean proficiency across schools
    median_proficiency_pct — median proficiency across schools

  Per grade × subject (grade_level_summary.csv):
    n_schools           — distinct schools with any data
    avg_proficiency_pct — grand average across all years
    covid_impact_pp     — avg COVID impact 2019→2022 (where both years exist)
    recovery_pp         — avg recovery 2022→2024 (where both years exist)
    net_vs_precovid_pp  — avg net change 2024 vs 2019
    avg_yoy_growth_pp   — mean of year-over-year changes across all valid
                          consecutive transitions (2016→17, 17→18, 18→19,
                          22→23, 23→24)

Inputs:
    output_data/combined_all_years.csv   – produced by load_wide_format_data.py

Outputs:
    output_data/grade_level_proficiency.csv  – avg/median proficiency per
                                               grade × subject × year
    output_data/grade_level_summary.csv      – per grade × subject aggregate
                                               with COVID recovery and YoY metrics

Usage:
    python src/grade_level_analysis.py

Dependencies:
    - output_data/combined_all_years.csv (produced by load_wide_format_data.py)
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
OUT_PROFICIENCY = os.path.join(OUTPUT_PATH, "grade_level_proficiency.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "grade_level_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
# Consecutive year pairs for YoY growth (exclude COVID gap 2019→2022)
VALID_YOY_TRANSITIONS = {
    (2016, 2017),
    (2017, 2018),
    (2018, 2019),
    (2022, 2023),
    (2023, 2024),
}

# Grade display order
GRADE_ORDER = ["Grade 3", "Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8", "HS"]

# Minimum schools for a valid cell
MIN_SCHOOLS = 3


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


# ═════════════════════════════════════════════════════════════════════════════
# Core computation
# ═════════════════════════════════════════════════════════════════════════════

def load_combined() -> pd.DataFrame:
    """Load the combined wide-format data."""
    if not os.path.isfile(COMBINED_FILE):
        print(f"ERROR: {COMBINED_FILE} not found.")
        print("Run python src/load_wide_format_data.py first.")
        sys.exit(1)
    df = pd.read_csv(COMBINED_FILE, dtype=str)
    print(f"Loaded combined data: {len(df):,} rows")
    return df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to school-level All Students rows and parse numerics."""
    # School-level only
    df = df[df["Aggregation Level"].str.upper() == "SCHOOL"].copy()

    # All Students only
    df = df[df["Student Group Value"].isin({"All Students", "All", "Total"})]

    # Parse numeric columns
    df["proficiency_pct"] = _parse_percent(df["Percent"])
    df["year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Drop rows with missing key fields
    df = df.dropna(subset=["School Name", "Subject", "Grade of Enrollment",
                            "year", "proficiency_pct"])

    # Standardise grade labels
    df["grade"] = df["Grade of Enrollment"].str.strip()

    print(f"Prepared {len(df):,} All Students school-level rows with valid proficiency")
    return df


def compute_grade_level_proficiency(df: pd.DataFrame) -> pd.DataFrame:
    """Avg / median proficiency per grade × subject × year."""
    agg = (
        df.groupby(["grade", "Subject", "year"], as_index=False)
        .agg(
            n_schools=("School Name", "nunique"),
            avg_proficiency_pct=("proficiency_pct", "mean"),
            median_proficiency_pct=("proficiency_pct", "median"),
        )
    )
    agg["avg_proficiency_pct"] = agg["avg_proficiency_pct"].round(2)
    agg["median_proficiency_pct"] = agg["median_proficiency_pct"].round(2)

    # Apply grade order
    grade_cat = pd.CategoricalDtype(categories=GRADE_ORDER, ordered=True)
    agg["grade"] = agg["grade"].astype(str)
    valid_grades = [g for g in GRADE_ORDER if g in agg["grade"].values]
    agg = agg[agg["grade"].isin(valid_grades)]
    agg["grade"] = pd.Categorical(agg["grade"], categories=valid_grades, ordered=True)
    agg = agg.sort_values(["grade", "Subject", "year"])

    # Keep only cells with enough schools
    agg = agg[agg["n_schools"] >= MIN_SCHOOLS]

    print(f"Grade-level proficiency: {len(agg):,} rows "
          f"({agg['grade'].nunique()} grades × {agg['Subject'].nunique()} subjects "
          f"× up to {agg['year'].nunique()} years)")
    return agg.reset_index(drop=True)


def compute_grade_level_summary(df: pd.DataFrame,
                                 proficiency: pd.DataFrame) -> pd.DataFrame:
    """Per grade × subject aggregate with COVID impact, recovery, YoY growth."""
    records = []

    for (grade, subject), grp in df.groupby(["grade", "Subject"]):
        n_schools = grp["School Name"].nunique()

        # Grand average across all years
        avg_prof = grp["proficiency_pct"].mean()

        # School-level year pivot to compute per-school metrics
        school_year = (
            grp.groupby(["School Name", "year"])["proficiency_pct"]
            .mean()
            .reset_index()
        )
        pivot = school_year.pivot(index="School Name", columns="year",
                                   values="proficiency_pct")

        # COVID impact: 2019→2022
        covid_impacts = []
        recoveries = []
        net_changes = []
        if 2019 in pivot.columns and 2022 in pivot.columns:
            valid = pivot[[2019, 2022]].dropna()
            covid_impacts = (valid[2022] - valid[2019]).tolist()
        if 2022 in pivot.columns and 2024 in pivot.columns:
            valid = pivot[[2022, 2024]].dropna()
            recoveries = (valid[2024] - valid[2022]).tolist()
        if 2019 in pivot.columns and 2024 in pivot.columns:
            valid = pivot[[2019, 2024]].dropna()
            net_changes = (valid[2024] - valid[2019]).tolist()

        covid_impact_pp = float(np.mean(covid_impacts)) if covid_impacts else np.nan
        recovery_pp = float(np.mean(recoveries)) if recoveries else np.nan
        net_vs_precovid_pp = float(np.mean(net_changes)) if net_changes else np.nan

        # Average YoY growth across valid consecutive transitions
        yoy_values = []
        for (yr_from, yr_to) in VALID_YOY_TRANSITIONS:
            if yr_from in pivot.columns and yr_to in pivot.columns:
                valid = pivot[[yr_from, yr_to]].dropna()
                if len(valid) >= MIN_SCHOOLS:
                    yoy_values.extend((valid[yr_to] - valid[yr_from]).tolist())
        avg_yoy_growth_pp = float(np.mean(yoy_values)) if yoy_values else np.nan

        records.append({
            "grade": grade,
            "Subject": subject,
            "n_schools": n_schools,
            "avg_proficiency_pct": round(avg_prof, 2),
            "covid_impact_pp": round(covid_impact_pp, 2) if not np.isnan(covid_impact_pp) else np.nan,
            "recovery_pp": round(recovery_pp, 2) if not np.isnan(recovery_pp) else np.nan,
            "net_vs_precovid_pp": round(net_vs_precovid_pp, 2) if not np.isnan(net_vs_precovid_pp) else np.nan,
            "avg_yoy_growth_pp": round(avg_yoy_growth_pp, 2) if not np.isnan(avg_yoy_growth_pp) else np.nan,
        })

    summary = pd.DataFrame(records)

    # Apply grade order
    valid_grades = [g for g in GRADE_ORDER if g in summary["grade"].values]
    summary["grade"] = pd.Categorical(summary["grade"], categories=valid_grades, ordered=True)
    summary = summary.sort_values(["grade", "Subject"]).reset_index(drop=True)

    print(f"Grade-level summary: {len(summary):,} rows "
          f"({summary['grade'].nunique()} grades × {summary['Subject'].nunique()} subjects)")
    return summary


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print("=" * 70)
    print("Grade-Level Performance Analysis")
    print("=" * 70)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    raw = load_combined()
    df = prepare_data(raw)

    proficiency = compute_grade_level_proficiency(df)
    summary = compute_grade_level_summary(df, proficiency)

    proficiency.to_csv(OUT_PROFICIENCY, index=False)
    print(f"✓ {OUT_PROFICIENCY}  ({len(proficiency):,} rows)")

    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"✓ {OUT_SUMMARY}  ({len(summary):,} rows)")

    # ── Print key findings ─────────────────────────────────────────────────
    print("\n── Key findings ──────────────────────────────────────────────────")
    for subject in ["ELA", "Math"]:
        sub = summary[summary["Subject"] == subject].copy()
        if sub.empty:
            continue
        top = sub.sort_values("avg_proficiency_pct", ascending=False).iloc[0]
        bot = sub.sort_values("avg_proficiency_pct").iloc[0]
        print(f"\n{subject}:")
        print(f"  Highest avg proficiency: {top['grade']} "
              f"({top['avg_proficiency_pct']:.1f}%)")
        print(f"  Lowest  avg proficiency: {bot['grade']} "
              f"({bot['avg_proficiency_pct']:.1f}%)")
        covid_row = sub.dropna(subset=["covid_impact_pp"]).sort_values("covid_impact_pp")
        if not covid_row.empty:
            worst = covid_row.iloc[0]
            print(f"  Largest COVID impact: {worst['grade']} "
                  f"({worst['covid_impact_pp']:+.2f} pp)")
        rec_row = sub.dropna(subset=["recovery_pp"]).sort_values("recovery_pp", ascending=False)
        if not rec_row.empty:
            best = rec_row.iloc[0]
            print(f"  Strongest recovery:   {best['grade']} "
                  f"({best['recovery_pp']:+.2f} pp)")

    print("\n" + "=" * 70)
    print("COMPLETE — grade_level_analysis.py done")
    print("=" * 70)


if __name__ == "__main__":
    main()
