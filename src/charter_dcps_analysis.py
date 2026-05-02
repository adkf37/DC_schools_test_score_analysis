"""
School Program Sector Analysis — DC Schools Test Score Analysis.

This script implements the charter vs. traditional public school comparison
described in backlog/phases.md (Phase 3 Build).

The OSSE "School and Demographic Group Aggregation" workbooks include all DC
public schools.  DCPS (DC Public Schools) assigns 3-digit school codes to its
traditional and alternative programs; schools that were added outside the
original DCPS numbering scheme carry 4-digit codes and are treated here as
the Charter sector.  Within DCPS the script further distinguishes:

  Sector classification (school_sector_by_school.csv → ``sector`` column):

    Charter              — school code is numeric and > 999
    DCPS Specialized     — selective-admissions or themed magnet programs
                           (Banneker HS, McKinley Tech HS, Duke Ellington,
                            School Without Walls HS, etc.)
    DCPS Alternative     — alternative and STAY programs for at-risk youth
                           (Ballou STAY, Roosevelt STAY, Washington
                            Metropolitan HS, Luke Moore HS, Phelps ACE HS,
                            Excel Academy, Ron Brown College Prep)
    DCPS Traditional     — all remaining neighborhood schools

Key metrics computed:

  Per school (school_sector_by_school.csv):
    sector                  — one of the four labels above
    school_code             — OSSE school code
    n_years_present         — number of distinct years the school appears

  Per sector × subject × year (school_sector_proficiency.csv):
    avg_proficiency_pct     — mean All-Students proficiency across schools
    n_schools               — number of schools with valid data

  Per sector × subject (school_sector_summary.csv):
    n_schools               — distinct schools with any proficiency data
    avg_proficiency_pct     — grand average across all years
    covid_impact_pp         — avg COVID impact 2019→2022 (All Students)
    recovery_pp             — avg recovery 2022→2024 (All Students)
    net_vs_precovid_pp      — avg net change 2024 vs 2019 (All Students)
    avg_cohort_growth_pp    — avg cohort growth (All Students)

Inputs:
    output_data/combined_all_years.csv        – produced by load_wide_format_data.py
    output_data/cohort_growth_summary.csv     – produced by analyze_cohort_growth.py (optional)
    output_data/covid_recovery_summary.csv    – produced by covid_recovery_analysis.py (optional)

Outputs:
    output_data/school_sector_by_school.csv   – one row per school with sector classification
    output_data/school_sector_proficiency.csv – avg proficiency by sector × subject × year
    output_data/school_sector_summary.csv     – per sector × subject aggregate with COVID
                                               recovery and cohort growth metrics

Usage:
    python src/charter_dcps_analysis.py
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

OUT_BY_SCHOOL = os.path.join(OUTPUT_PATH, "school_sector_by_school.csv")
OUT_PROFICIENCY = os.path.join(OUTPUT_PATH, "school_sector_proficiency.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "school_sector_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
MIN_N = 10   # minimum student count to include a data point

# COVID analysis reference years
PRE_COVID_YEAR = 2019
COVID_YEAR = 2022
LATEST_YEAR = 2024

ALL_STUDENTS_LABELS = {"All Students", "All", "Total"}

# Ordered sector labels for consistent display
SECTOR_ORDER = [
    "Charter",
    "DCPS Specialized",
    "DCPS Alternative",
    "DCPS Traditional",
]

# Schools identified as DCPS Specialized (selective or themed magnet programs).
# Matched by substring (case-insensitive) against the canonical School Name.
SPECIALIZED_SUBSTRINGS = [
    "banneker",
    "mckinley technology",
    "ellington",
    "school without walls",
    "bard high school",      # Bard DC also has a 4-digit code → Charter takes precedence
    "macfarland",            # MacFarland serves as the host for SWW @ Francis Stevens
]

# Schools identified as DCPS Alternative (alternative programs and STAY schools).
# Matched by substring (case-insensitive).
ALTERNATIVE_SUBSTRINGS = [
    "stay",
    "washington metropolitan",
    "luke moore",
    "phelps",
    "excel academy",
    "ron brown college",
    "ballou stay",
    "roosevelt stay",
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


def _classify_sector(school_name: str, school_code) -> str:
    """
    Classify a school into one of four program sectors.

    Priority order:
      1. Charter      — numeric 4-digit school code
      2. DCPS Specialized — name matches a known specialized/magnet program
      3. DCPS Alternative — name matches a known alternative/STAY program
      4. DCPS Traditional — all other schools
    """
    name_lower = str(school_name).lower()

    # Charter: 4-digit numeric school code
    try:
        code_int = int(str(school_code).strip())
        if code_int > 999:
            return "Charter"
    except (ValueError, TypeError):
        pass

    # DCPS Specialized
    for substr in SPECIALIZED_SUBSTRINGS:
        if substr in name_lower:
            return "DCPS Specialized"

    # DCPS Alternative
    for substr in ALTERNATIVE_SUBSTRINGS:
        if substr in name_lower:
            return "DCPS Alternative"

    return "DCPS Traditional"


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 70)
    print("SCHOOL PROGRAM SECTOR ANALYSIS (Charter vs. DCPS)")
    print("=" * 70)

    # ── Load combined data ─────────────────────────────────────────────────
    if not os.path.isfile(COMBINED_FILE):
        print(f"ERROR: {COMBINED_FILE} not found.")
        print("       Run src/load_wide_format_data.py first.")
        sys.exit(1)

    df = pd.read_csv(COMBINED_FILE)
    print(f"\nLoaded combined data: {len(df):,} rows")

    # Keep school-level rows only
    df = df[df["Aggregation Level"].str.upper() == "SCHOOL"].copy()

    # Parse numeric fields
    df["pct"] = _parse_percent(df["Percent"])
    df["count"] = _parse_count(df["Count"])
    df["total_count"] = _parse_count(df["Total Count"])
    df["year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Drop rows without a school name or year
    df = df.dropna(subset=["School Name", "year"])
    df["year"] = df["year"].astype(int)

    # ── Classify sectors ───────────────────────────────────────────────────
    # Use the most common school code per school name
    code_map = (
        df.groupby("School Name")["School Code"]
        .agg(lambda s: s.mode().iloc[0] if not s.mode().empty else "0")
    )

    sectors = {
        name: _classify_sector(name, code)
        for name, code in code_map.items()
    }
    df["sector"] = df["School Name"].map(sectors)

    # ── Build school-level classification table ────────────────────────────
    by_school = (
        df.groupby("School Name")
        .agg(
            sector=("sector", "first"),
            school_code=("School Code", lambda s: s.mode().iloc[0] if not s.mode().empty else ""),
            n_years_present=("year", "nunique"),
            first_year=("year", "min"),
            last_year=("year", "max"),
        )
        .reset_index()
        .sort_values(["sector", "School Name"])
    )

    print(f"\nSector breakdown:")
    counts = by_school["sector"].value_counts()
    for sector in SECTOR_ORDER:
        print(f"  {sector}: {counts.get(sector, 0)} schools")

    # ── Proficiency by sector × subject × year ────────────────────────────
    # Filter to All Students rows, valid proficiency
    all_std = df[df["Student Group Value"].isin(ALL_STUDENTS_LABELS)].copy()
    all_std = all_std.dropna(subset=["pct"])
    all_std = all_std[all_std["total_count"] >= MIN_N]

    sector_prof = (
        all_std.groupby(["sector", "Subject", "year"], as_index=False)
        .agg(
            avg_proficiency_pct=("pct", "mean"),
            n_schools=("School Name", "nunique"),
            median_proficiency_pct=("pct", "median"),
        )
    )
    sector_prof["avg_proficiency_pct"] = sector_prof["avg_proficiency_pct"].round(2)
    sector_prof["median_proficiency_pct"] = sector_prof["median_proficiency_pct"].round(2)
    # Add sector ordering
    sector_sort = {s: i for i, s in enumerate(SECTOR_ORDER)}
    sector_prof["_sect_ord"] = sector_prof["sector"].map(sector_sort).fillna(99)
    sector_prof = sector_prof.sort_values(
        ["Subject", "_sect_ord", "year"]
    ).drop(columns=["_sect_ord"]).reset_index(drop=True)
    sector_prof.rename(columns={"sector": "School Sector"}, inplace=True)

    # ── COVID recovery metrics per sector ─────────────────────────────────
    covid_rows = []

    for sector in SECTOR_ORDER:
        sector_names = set(by_school.loc[by_school["sector"] == sector, "School Name"])
        for subj in all_std["Subject"].unique():
            sub = all_std[
                (all_std["sector"] == sector) & (all_std["Subject"] == subj)
            ]
            pre = sub[sub["year"] == PRE_COVID_YEAR].groupby("School Name")["pct"].mean()
            post = sub[sub["year"] == COVID_YEAR].groupby("School Name")["pct"].mean()
            late = sub[sub["year"] == LATEST_YEAR].groupby("School Name")["pct"].mean()

            schools_with_both = pre.index.intersection(post.index)
            if len(schools_with_both) > 0:
                impact = (post[schools_with_both] - pre[schools_with_both]).mean()
            else:
                impact = np.nan

            schools_rec = post.index.intersection(late.index)
            if len(schools_rec) > 0:
                recovery = (late[schools_rec] - post[schools_rec]).mean()
                net = (late[schools_rec] - pre.reindex(schools_rec)).mean()
            else:
                recovery = np.nan
                net = np.nan

            covid_rows.append(
                dict(
                    sector=sector,
                    Subject=subj,
                    covid_impact_pp=round(impact, 2) if not np.isnan(impact) else np.nan,
                    recovery_pp=round(recovery, 2) if not np.isnan(recovery) else np.nan,
                    net_vs_precovid_pp=round(net, 2) if not np.isnan(net) else np.nan,
                )
            )

    covid_df = pd.DataFrame(covid_rows)

    # ── Optional: load cohort growth per sector ────────────────────────────
    cohort_sector = pd.DataFrame()
    if os.path.isfile(COHORT_SUMMARY_FILE):
        cg = pd.read_csv(COHORT_SUMMARY_FILE)
        cg = cg[cg["Student Group Value"].isin(ALL_STUDENTS_LABELS)].copy()
        cg["sector"] = cg["School Name"].map(sectors)
        cohort_sector = (
            cg.groupby(["sector", "Subject"], as_index=False)
            .agg(avg_cohort_growth_pp=("avg_pp_growth", "mean"))
        )
        cohort_sector["avg_cohort_growth_pp"] = cohort_sector["avg_cohort_growth_pp"].round(2)

    # ── Build sector summary table ─────────────────────────────────────────
    n_schools_df = (
        all_std.groupby(["sector", "Subject"])["School Name"]
        .nunique()
        .reset_index()
        .rename(columns={"School Name": "n_schools"})
    )
    avg_prof_df = (
        all_std.groupby(["sector", "Subject"], as_index=False)
        .agg(avg_proficiency_pct=("pct", "mean"))
    )
    avg_prof_df["avg_proficiency_pct"] = avg_prof_df["avg_proficiency_pct"].round(2)

    summary = n_schools_df.merge(avg_prof_df, on=["sector", "Subject"], how="outer")
    if not covid_df.empty:
        summary = summary.merge(covid_df, on=["sector", "Subject"], how="left")
    if not cohort_sector.empty:
        summary = summary.merge(cohort_sector, on=["sector", "Subject"], how="left")

    # Enforce sector order
    summary["_sect_ord"] = summary["sector"].map(sector_sort).fillna(99)
    summary = summary.sort_values(
        ["Subject", "_sect_ord"]
    ).drop(columns=["_sect_ord"]).reset_index(drop=True)
    summary.rename(columns={"sector": "School Sector"}, inplace=True)

    # ── Save outputs ───────────────────────────────────────────────────────
    by_school.rename(columns={"sector": "School Sector", "school_code": "School Code"}, inplace=True)
    by_school.to_csv(OUT_BY_SCHOOL, index=False)
    sector_prof.to_csv(OUT_PROFICIENCY, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"\n✓ Saved {len(by_school)} rows → {OUT_BY_SCHOOL}")
    print(f"✓ Saved {len(sector_prof)} rows → {OUT_PROFICIENCY}")
    print(f"✓ Saved {len(summary)} rows → {OUT_SUMMARY}")

    # ── Print key findings ─────────────────────────────────────────────────
    print("\n── Key Findings ──")
    if not summary.empty:
        for subj in sorted(summary["Subject"].unique()):
            sub_s = summary[summary["Subject"] == subj]
            print(f"\n  {subj}:")
            for _, row in sub_s.iterrows():
                sector_label = row["School Sector"]
                n = int(row.get("n_schools", 0)) if not pd.isna(row.get("n_schools", np.nan)) else 0
                avg_p = row.get("avg_proficiency_pct", np.nan)
                covid_i = row.get("covid_impact_pp", np.nan)
                rec = row.get("recovery_pp", np.nan)
                growth = row.get("avg_cohort_growth_pp", np.nan)
                parts = [f"    {sector_label}: n={n}, avg proficiency {avg_p:.1f}%"]
                if not pd.isna(covid_i):
                    parts.append(f"COVID impact {covid_i:+.1f} pp")
                if not pd.isna(rec):
                    parts.append(f"recovery {rec:+.1f} pp")
                if not pd.isna(growth):
                    parts.append(f"avg cohort growth {growth:+.1f} pp")
                print(", ".join(parts))

    print()
    print("=" * 70)
    print("SCHOOL PROGRAM SECTOR ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run()
