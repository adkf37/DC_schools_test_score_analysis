"""
Subgroup Proficiency Trend Analysis for DC Schools.

This script computes proficiency levels over time for each student demographic
subgroup (All Students, Male, Female, Black or African American, Hispanic/Latino,
Economically Disadvantaged, EL Active, Students with Disabilities, White) for
both ELA and Math.

Unlike equity_gap_analysis.py — which measures how much each subgroup's cohort
growth *changed relative to "All Students"* — this analysis asks:

    "Across all DC schools, how do absolute proficiency levels compare across
     student demographic groups, and how has each group's proficiency changed
     over time?"

Key metrics computed:

  Per subgroup × subject × year (subgroup_proficiency.csv):
    n_schools              — number of schools with valid data for this cell
    avg_proficiency_pct    — mean proficiency across schools
    median_proficiency_pct — median proficiency across schools

  Per subgroup × subject (subgroup_summary.csv):
    n_schools           — distinct schools with any valid data
    avg_proficiency_pct — grand average across all years
    covid_impact_pp     — avg COVID impact 2019→2022 (where both years exist)
    recovery_pp         — avg recovery 2022→2024 (where both years exist)
    net_vs_precovid_pp  — avg net change 2024 vs 2019
    avg_yoy_growth_pp   — mean of year-over-year changes across valid consecutive
                          transitions (2016→17, 17→18, 18→19, 22→23, 23→24)

Inputs:
    output_data/combined_all_years.csv   — produced by load_wide_format_data.py

Outputs:
    output_data/subgroup_proficiency.csv — avg/median proficiency per
                                           subgroup × subject × year
    output_data/subgroup_summary.csv     — per subgroup × subject aggregate
                                           with COVID recovery and YoY metrics

Usage:
    python src/subgroup_trend_analysis.py

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
OUT_PROFICIENCY = os.path.join(OUTPUT_PATH, "subgroup_proficiency.csv")
OUT_SUMMARY = os.path.join(OUTPUT_PATH, "subgroup_summary.csv")

# ── Constants ─────────────────────────────────────────────────────────────────
# Consecutive year pairs for YoY growth (exclude COVID gap 2019→2022)
VALID_YOY_TRANSITIONS = {
    (2016, 2017),
    (2017, 2018),
    (2018, 2019),
    (2022, 2023),
    (2023, 2024),
}

# Display order for subgroups (All Students first, then alphabetical).
# NOTE: These strings must exactly match the values in the `Student Group Value`
# column of combined_all_years.csv as produced by load_wide_format_data.py.
# "Econ Dis" and "EL Active" are the abbreviated labels used by OSSE in the
# source workbooks.
SUBGROUP_ORDER = [
    "All Students",
    "Male",
    "Female",
    "Black or African American",
    "Hispanic/Latino of any race",
    "White",
    "Asian",
    "Two or more races",
    "Econ Dis",
    "EL Active",
    "Students with Disabilities",
]

# Minimum schools with valid data required to include a cell
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
    """Filter to school-level rows, parse numerics, keep recognised subgroups."""
    # School-level only
    df = df[df["Aggregation Level"].str.upper() == "SCHOOL"].copy()

    # Parse numeric columns
    df["proficiency_pct"] = _parse_percent(df["Percent"])
    df["year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Standardise subgroup label
    df["subgroup"] = df["Student Group Value"].str.strip()

    # Keep only subgroups that appear in our ordered list
    df = df[df["subgroup"].isin(SUBGROUP_ORDER)]

    # Drop rows with missing key fields
    df = df.dropna(subset=["School Name", "Subject", "subgroup",
                            "year", "proficiency_pct"])

    # Use "All Grades" rows where available (Tested Grade/Subject == "All") to
    # avoid double-counting individual-grade rows within the same school-year-subgroup.
    # If no "All" row exists, fall back to averaging across grade rows.
    all_mask = df["Tested Grade/Subject"].str.upper().isin({"ALL", "ALL GRADES"})
    df_all = df[all_mask].copy()
    df_other = df[~all_mask].copy()

    # Identify (school, subject, subgroup, year) keys already covered by an All row
    all_keys = set(zip(df_all["School Name"], df_all["Subject"],
                       df_all["subgroup"], df_all["year"]))
    other_not_covered = df_other[
        ~df_other.apply(
            lambda r: (r["School Name"], r["Subject"], r["subgroup"], r["year"])
            in all_keys,
            axis=1,
        )
    ]

    # Average across grade-level rows for those not covered
    if not other_not_covered.empty:
        other_agg = (
            other_not_covered
            .groupby(["School Name", "Subject", "subgroup", "year"], as_index=False)
            .agg(proficiency_pct=("proficiency_pct", "mean"))
        )
        df_combined = pd.concat([df_all, other_agg], ignore_index=True)
    else:
        df_combined = df_all.copy()

    # Final dedup: one row per school × subject × subgroup × year
    df_combined = (
        df_combined
        .groupby(["School Name", "Subject", "subgroup", "year"], as_index=False)
        .agg(proficiency_pct=("proficiency_pct", "mean"))
    )

    print(f"Prepared {len(df_combined):,} school × subject × subgroup × year rows with valid proficiency")
    print(f"Subgroups present: {sorted(df_combined['subgroup'].unique())}")
    return df_combined


def compute_subgroup_proficiency(df: pd.DataFrame) -> pd.DataFrame:
    """Avg / median proficiency per subgroup × subject × year."""
    agg = (
        df.groupby(["subgroup", "Subject", "year"], as_index=False)
        .agg(
            n_schools=("School Name", "nunique"),
            avg_proficiency_pct=("proficiency_pct", "mean"),
            median_proficiency_pct=("proficiency_pct", "median"),
        )
    )
    agg["avg_proficiency_pct"] = agg["avg_proficiency_pct"].round(2)
    agg["median_proficiency_pct"] = agg["median_proficiency_pct"].round(2)

    # Apply subgroup display order
    valid_subgroups = [s for s in SUBGROUP_ORDER if s in agg["subgroup"].values]
    agg = agg[agg["subgroup"].isin(valid_subgroups)]
    agg["subgroup"] = pd.Categorical(agg["subgroup"], categories=valid_subgroups, ordered=True)
    agg = agg.sort_values(["subgroup", "Subject", "year"])

    # Keep only cells with enough schools
    agg = agg[agg["n_schools"] >= MIN_SCHOOLS]

    print(f"Subgroup proficiency: {len(agg):,} rows "
          f"({agg['subgroup'].nunique()} subgroups × {agg['Subject'].nunique()} subjects "
          f"× up to {agg['year'].nunique()} years)")
    return agg.reset_index(drop=True)


def compute_subgroup_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per subgroup × subject aggregate with COVID impact, recovery, YoY growth."""
    records = []

    for (subgroup, subject), grp in df.groupby(["subgroup", "Subject"]):
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
            "subgroup": subgroup,
            "Subject": subject,
            "n_schools": n_schools,
            "avg_proficiency_pct": round(avg_prof, 2),
            "covid_impact_pp": round(covid_impact_pp, 2) if not np.isnan(covid_impact_pp) else np.nan,
            "recovery_pp": round(recovery_pp, 2) if not np.isnan(recovery_pp) else np.nan,
            "net_vs_precovid_pp": round(net_vs_precovid_pp, 2) if not np.isnan(net_vs_precovid_pp) else np.nan,
            "avg_yoy_growth_pp": round(avg_yoy_growth_pp, 2) if not np.isnan(avg_yoy_growth_pp) else np.nan,
        })

    summary = pd.DataFrame(records)

    # Apply subgroup display order
    valid_subgroups = [s for s in SUBGROUP_ORDER if s in summary["subgroup"].values]
    summary["subgroup"] = pd.Categorical(summary["subgroup"], categories=valid_subgroups, ordered=True)
    summary = summary.sort_values(["Subject", "subgroup"]).reset_index(drop=True)

    print(f"Subgroup summary: {len(summary):,} rows "
          f"({summary['subgroup'].nunique()} subgroups × {summary['Subject'].nunique()} subjects)")
    return summary


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print("=" * 70)
    print("Subgroup Proficiency Trend Analysis")
    print("=" * 70)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    raw = load_combined()
    df = prepare_data(raw)

    proficiency = compute_subgroup_proficiency(df)
    summary = compute_subgroup_summary(df)

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
        print(f"  Highest avg proficiency: {top['subgroup']} "
              f"({top['avg_proficiency_pct']:.1f}%)")
        print(f"  Lowest  avg proficiency: {bot['subgroup']} "
              f"({bot['avg_proficiency_pct']:.1f}%)")
        covid_row = sub.dropna(subset=["covid_impact_pp"]).sort_values("covid_impact_pp")
        if not covid_row.empty:
            worst = covid_row.iloc[0]
            print(f"  Largest COVID impact: {worst['subgroup']} "
                  f"({worst['covid_impact_pp']:+.2f} pp)")
        rec_row = sub.dropna(subset=["recovery_pp"]).sort_values("recovery_pp", ascending=False)
        if not rec_row.empty:
            best = rec_row.iloc[0]
            print(f"  Strongest recovery:   {best['subgroup']} "
                  f"({best['recovery_pp']:+.2f} pp)")

    # Show the proficiency gap between highest and lowest subgroup
    print("\n── Proficiency gap (citywide avg, all years) ─────────────────────")
    for subject in ["ELA", "Math"]:
        sub = summary[(summary["Subject"] == subject) &
                      (summary["subgroup"] != "All Students")].copy()
        if sub.empty:
            continue
        sub_all = summary[(summary["Subject"] == subject) &
                          (summary["subgroup"] == "All Students")]
        all_avg = sub_all["avg_proficiency_pct"].iloc[0] if not sub_all.empty else np.nan
        top = sub.sort_values("avg_proficiency_pct", ascending=False).iloc[0]
        bot = sub.sort_values("avg_proficiency_pct").iloc[0]
        gap = top["avg_proficiency_pct"] - bot["avg_proficiency_pct"]
        print(f"\n{subject}  (All Students avg: {all_avg:.1f}%)")
        print(f"  Highest subgroup: {top['subgroup']} ({top['avg_proficiency_pct']:.1f}%)")
        print(f"  Lowest  subgroup: {bot['subgroup']} ({bot['avg_proficiency_pct']:.1f}%)")
        print(f"  Gap: {gap:.1f} pp")

    print("\n" + "=" * 70)
    print("COMPLETE — subgroup_trend_analysis.py done")
    print("=" * 70)


if __name__ == "__main__":
    main()
