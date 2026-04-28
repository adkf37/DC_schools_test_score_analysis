"""
Proficiency Trend Analysis for DC school test scores.

Reads combined_all_years.csv and produces a tidy grade × year proficiency
grid that is used by the dashboard heatmap and can support standalone policy
analysis.

For each school / year / subject / grade / student-subgroup combination the
script reports:
  - proficiency_pct   : mean percentage meeting/exceeding standard
  - n_test_takers     : total number of students tested
  - n_proficient      : estimated number of proficient students

Output:
    output_data/proficiency_trends.csv

Usage:
    python src/proficiency_trend_analysis.py

Dependencies:
    - output_data/combined_all_years.csv  (produced by load_wide_format_data.py)
"""
import os
import re
import sys
import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, ".."))
OUTPUT_PATH = os.path.join(REPO_ROOT, "output_data")

COMBINED_FILE = os.path.join(OUTPUT_PATH, "combined_all_years.csv")
TRENDS_FILE = os.path.join(OUTPUT_PATH, "proficiency_trends.csv")

# Skip school-wide aggregate rows – these are summary rows across all grades
SKIP_GRADES = {"ALL", "ALL GRADES", "HS"}

# Canonical grade sort order (Grade 3 … Grade 12)
GRADE_ORDER = [f"Grade {n}" for n in range(3, 13)]


# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════

def _coerce_numeric(series: pd.Series) -> pd.Series:
    """Convert a Series to float, mapping OSSE suppression codes to NaN."""
    def _parse(val):
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return np.nan
        s = str(val).strip().upper()
        if s in ("", "DS", "N/A", "NA", "."):
            return np.nan
        # Match OSSE suppression patterns:
        #   N\s*<  → "N < 10", "N<10"
        #   <[^-]  → "<5%" but not "<-" (negative numbers are valid data values)
        #   >      → ">95%"
        if re.match(r"^(N\s*<|<[^-]|>)", s):
            return np.nan
        s = s.replace("%", "").replace(",", "").strip()
        try:
            return float(s)
        except (ValueError, TypeError):
            return np.nan

    return series.apply(_parse)


def _grade_sort_key(grade_str: str) -> int:
    """Return a numeric sort key for a single grade string (e.g. 'Grade 6' → 6)."""
    m = re.search(r"\d+", str(grade_str))
    return int(m.group()) if m else 99


def _sort_grade(grade_series: pd.Series) -> pd.Series:
    """Return a numeric sort-key Series for a Series of grade strings."""
    return grade_series.apply(_grade_sort_key)


# ═════════════════════════════════════════════════════════════════════════════
# Core
# ═════════════════════════════════════════════════════════════════════════════

def load_data() -> pd.DataFrame:
    """Load and lightly clean the combined dataset."""
    if not os.path.isfile(COMBINED_FILE):
        print(f"ERROR: {COMBINED_FILE} not found.")
        print("Run python src/load_wide_format_data.py first.")
        sys.exit(1)

    print("=" * 70)
    print("PROFICIENCY TREND ANALYSIS")
    print("=" * 70)
    print(f"\nLoading: {COMBINED_FILE}")

    df = pd.read_csv(COMBINED_FILE, dtype=str)
    print(f"  Loaded {len(df):,} rows")

    # Numeric conversion
    df["pct"] = _coerce_numeric(df["Percent"])
    df["total_n"] = _coerce_numeric(df["Total Count"])
    df["prof_n"] = _coerce_numeric(df["Count"])
    df["year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Keep school-level rows only
    df = df[df["Aggregation Level"].str.upper() == "SCHOOL"].copy()

    # Normalise grade column (strip trailing -All, leading HS-)
    def _norm_grade(val):
        if pd.isna(val):
            return val
        s = str(val).strip()
        s = re.sub(r"-All$", "", s)
        s = re.sub(r"^HS-", "", s)
        m = re.match(r"^(\d{1,2})$", s)
        if m:
            s = f"Grade {int(m.group(1))}"
        return s

    df["grade"] = df["Grade of Enrollment"].apply(_norm_grade)

    # Remove school-wide aggregate grade rows
    df = df[~df["grade"].str.upper().isin(SKIP_GRADES)]

    # Deduplicate: when the same school/grade/subgroup/year has multiple rows
    # (e.g. PARCC + MSAA), prefer the row with the larger total_n.
    dedup_keys = [
        "School Code", "School Name", "Subject",
        "grade", "Student Group Value", "year",
    ]
    df = (
        df.sort_values("total_n", ascending=False, na_position="last")
          .drop_duplicates(subset=dedup_keys, keep="first")
    )

    print(f"  After school-level filter + dedup: {len(df):,} rows")
    print(f"  Years:    {sorted(df['year'].dropna().unique().tolist())}")
    print(f"  Schools:  {df['School Name'].nunique()}")
    print(f"  Subjects: {sorted(df['Subject'].dropna().unique().tolist())}")

    return df


def compute_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate to one row per School / Year / Subject / Grade / Subgroup.

    Returns a long-format DataFrame suitable for heatmap rendering.
    """
    group_keys = [
        "School Name", "year", "Subject", "grade",
        "Student Group Value",
    ]

    trends = (
        df.groupby(group_keys, as_index=False)
          .agg(
              proficiency_pct=("pct", "mean"),
              n_test_takers=("total_n", "sum"),
              n_proficient=("prof_n", "sum"),
          )
    )

    # Round for cleaner output
    trends["proficiency_pct"] = trends["proficiency_pct"].round(2)
    trends["n_test_takers"] = trends["n_test_takers"].fillna(0).astype(int)
    trends["n_proficient"] = trends["n_proficient"].fillna(0).astype(int)

    # Add a numeric sort key for grades
    trends["grade_sort"] = _sort_grade(trends["grade"])

    # Sort for readability
    trends = trends.sort_values(
        ["School Name", "year", "Subject", "grade_sort", "Student Group Value"]
    ).drop(columns=["grade_sort"])
    trends = trends.reset_index(drop=True)

    return trends


def print_summary(trends: pd.DataFrame) -> None:
    """Print descriptive statistics."""
    print("\n── Summary ──────────────────────────────────────────────────────────")
    print(f"  Total rows:   {len(trends):,}")
    print(f"  Schools:      {trends['School Name'].nunique()}")
    print(f"  Years:        {sorted(trends['year'].dropna().unique().tolist())}")
    print(f"  Grades:       {sorted(trends['grade'].dropna().unique().tolist(), key=_grade_sort_key)}")
    print(f"  Subgroups:    {trends['Student Group Value'].nunique()}")

    # Citywide All-Students proficiency by year and subject
    all_stu = trends[trends["Student Group Value"] == "All Students"]
    if not all_stu.empty:
        print("\n  Citywide avg proficiency (All Students, per year × subject):")
        pivot = (
            all_stu.groupby(["year", "Subject"])["proficiency_pct"]
                   .mean()
                   .round(1)
                   .unstack("Subject")
        )
        for row in pivot.to_string().split("\n"):
            print(f"    {row}")


def main() -> None:
    df = load_data()

    print("\n── Computing proficiency trends … ──────────────────────────────────")
    trends = compute_trends(df)

    print_summary(trends)

    trends.to_csv(TRENDS_FILE, index=False)
    print(f"\n✓ Saved: {TRENDS_FILE}")
    print(f"  {len(trends):,} rows")

    print("\n" + "=" * 70)
    print("PROFICIENCY TREND ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
