"""
Cohort-based growth analysis for DC school test scores.

This replicates – citywide and for every school – the manual growth
calculation shown in the Stuart-Hobson example spreadsheet:

    Grade N in Year Y  →  Grade N+1 in Year Y+1
    (same cohort of students advancing one grade)

Outputs:
    cohort_growth_detail.csv   – one row per school / subject / subgroup /
                                  cohort transition (e.g. Gr6→Gr7 2022→2023)
    cohort_growth_summary.csv  – school-level summary across all transitions
    cohort_growth_pivot.xlsx   – Excel workbook with pivot-friendly layout

Usage:
    python src/analyze_cohort_growth.py
"""
import os
import re
import sys
import numpy as np
import pandas as pd
from typing import List, Optional, Tuple

# ── Paths ────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, '..', 'output_data'))
COMBINED_DATA_FILE = os.path.join(OUTPUT_PATH, 'combined_all_years.csv')

# ── Configuration ────────────────────────────────────────────────────────
# Assessment types to use for the main analysis.
# PARCC was used through 22-23; DCCAPE replaced it in 23-24; 24-25 only has "All".
# We prefer the specific assessment name over "All" when both exist.
MAIN_ASSESSMENTS = ['PARCC', 'DCCAPE']

# Minimum total test-taker count to include a row (avoids noisy small-N data)
MIN_TOTAL_COUNT = 10


# ═════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════

def parse_numeric(series: pd.Series) -> pd.Series:
    """Parse string values to numeric, returning NaN for suppressed data."""
    def _parse(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().upper()
        if s in ('', 'DS', 'N<10', '<5%', '<=10%', 'N/A', 'NA', 'NONE', '.'):
            return np.nan
        if s.startswith(('<', '>', 'N<', 'N ')) or s == 'N < 10':
            return np.nan
        s = s.replace('%', '').replace(',', '').strip()
        try:
            return float(s)
        except (ValueError, TypeError):
            return np.nan
    return series.apply(_parse)


def extract_grade_number(grade_str) -> int:
    """Extract numeric grade from strings like 'Grade 6'. Returns -1 if N/A."""
    if pd.isna(grade_str):
        return -1
    m = re.match(r'Grade\s*(\d+)', str(grade_str).strip())
    return int(m.group(1)) if m else -1


def normalize_grade(val) -> str:
    """Normalize grade labels: 'Grade 6-All' → 'Grade 6', '06' → 'Grade 6'."""
    if pd.isna(val):
        return val
    s = str(val).strip()
    s = re.sub(r'-All$', '', s)
    s = re.sub(r'^HS-', '', s)
    m = re.match(r'^(\d{1,2})$', s)
    if m:
        s = f'Grade {int(m.group(1))}'
    return s


# ═════════════════════════════════════════════════════════════════════════
# Data loading
# ═════════════════════════════════════════════════════════════════════════

def load_and_prepare() -> pd.DataFrame:
    """Load combined data, parse numerics, filter to school-level grade rows."""
    print("=" * 70)
    print("COHORT GROWTH ANALYSIS")
    print("=" * 70)

    if not os.path.exists(COMBINED_DATA_FILE):
        print(f"\nERROR: {COMBINED_DATA_FILE} not found!")
        print("Run  python src/load_clean_data.py  first.")
        sys.exit(1)

    print(f"\nReading {COMBINED_DATA_FILE} ...")
    df = pd.read_csv(COMBINED_DATA_FILE, dtype=str)
    print(f"  Loaded {len(df):,} rows")

    # Parse numerics
    df['percent_value'] = parse_numeric(df['Percent'])
    df['count_value'] = parse_numeric(df['Count'])
    df['total_count_value'] = parse_numeric(df['Total Count'])
    df['year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

    # Filter to school level only
    df = df[df['Aggregation Level'].str.upper() == 'SCHOOL'].copy()

    # Normalize grades in both columns
    df['Tested Grade/Subject'] = df['Tested Grade/Subject'].apply(normalize_grade)
    df['Grade of Enrollment'] = df['Grade of Enrollment'].apply(normalize_grade)

    # Extract grade numbers from BOTH columns
    df['tested_grade_num'] = df['Tested Grade/Subject'].apply(extract_grade_number)
    df['enrolled_grade_num'] = df['Grade of Enrollment'].apply(extract_grade_number)

    # ── Determine the "cohort grade" ────────────────────────────────────
    # For cohort tracking we want the grade the students are ENROLLED in,
    # not the test level they took.  E.g. a Grade-8 student taking Algebra I
    # should count as Grade 8 for cohort purposes.
    #
    # Priority:
    #   1. If Grade of Enrollment has a specific grade → use it
    #   2. Else fall back to Tested Grade/Subject
    df['cohort_grade'] = df.apply(
        lambda row: row['enrolled_grade_num']
                    if row['enrolled_grade_num'] >= 0
                    else row['tested_grade_num'],
        axis=1,
    )

    # Keep only rows with a valid cohort grade (≥3)
    df = df[df['cohort_grade'] >= 3].copy()

    # ── Filter: only keep rows that represent the FULL enrolled cohort ───
    # Rows where Tested Grade/Subject is a specific test name like
    # "Algebra I" or "Geometry" only cover a SUBSET of enrolled students.
    # We only want rows where:
    #   a) Tested Grade/Subject = "All" (combined rate for the enrolled grade), OR
    #   b) Tested Grade/Subject matches the cohort grade (e.g. "Grade 8" for cohort_grade=8)
    # This prevents e.g. an Algebra I row (69.8%) from being used as the
    # full Grade 8 cohort proficiency rate.
    tgs_is_combined = df['Tested Grade/Subject'] == 'All'
    tgs_matches_cohort = df['tested_grade_num'] == df['cohort_grade']
    df = df[tgs_is_combined | tgs_matches_cohort].copy()

    # ── "Tested Grade/Subject" preference ────────────────────────────────
    # Within a cohort grade, rows where Tested Grade/Subject = "All" combine
    # ALL assessment levels (e.g. Grade-8 Math + Algebra I) and therefore
    # represent the true enrolled-cohort proficiency rate.
    # Rows where Tested Grade/Subject = a specific test level (Grade 8, Algebra I)
    # only cover a subset of students.
    #
    # We prefer "Tested Grade/Subject = All" (combined) when it exists,
    # falling back to the specific test-level row otherwise.
    df['_tgs_sort'] = df['Tested Grade/Subject'].apply(
        lambda x: 0 if str(x).strip() == 'All' else 1   # "All" first
    )

    # ── Assessment name preference ───────────────────────────────────────
    # For years with both a specific assessment (PARCC/DCCAPE) and "All",
    # prefer the specific one. For 2025 where only "All" exists, keep "All".
    df['assess_type'] = df['Assessment Name'].apply(
        lambda x: 'main' if str(x).strip() in MAIN_ASSESSMENTS
        else ('all' if str(x).strip() == 'All' else 'other')
    )

    # Combined sort: prefer TGS="All" first, then main assessment, then "All" assessment
    df['_assess_sort'] = df['assess_type'].map({'main': 0, 'all': 1, 'other': 2})

    # Dedup key: school / year / cohort_grade / subject / subgroup
    key_cols = ['year', 'School Code', 'Subject', 'cohort_grade',
                'Student Group', 'Student Group Value']

    # Sort: prefer TGS="All" first, then within that prefer specific assessment
    df = df.sort_values(key_cols + ['_tgs_sort', '_assess_sort'])

    # Separate MSAA (different tested population) from main/all
    df_main = df[df['assess_type'].isin(['main', 'all'])].copy()
    df_main = df_main.drop_duplicates(subset=key_cols, keep='first')
    df_msaa = df[df['assess_type'] == 'other'].copy()

    df = pd.concat([df_main, df_msaa], ignore_index=True)
    df = df.drop(columns=['_tgs_sort', '_assess_sort'])

    # Filter out rows with missing percent or very small N
    df = df.dropna(subset=['percent_value'])
    df = df[df['total_count_value'].fillna(0) >= MIN_TOTAL_COUNT]

    # ── Harmonize student group labels across years ──────────────────────
    # 2022 uses Student Group="All" / Value="All"
    # 2023+ uses Student Group="All Students" / Value="All Students"
    df['Student Group'] = df['Student Group'].replace({'All': 'All Students'})
    df['Student Group Value'] = df['Student Group Value'].replace({'All': 'All Students'})

    # Standardize common subgroup label variations across years
    subgroup_map = {
        'White/Caucasian': 'White',
        'Hispanic/Latino': 'Hispanic/Latino of any race',
        'Two or More Races': 'Two or more races',
        'Active or Monitored English Learner': 'EL Active or Monitored 1-2 yr',
        'Not Active or Monitored English Learner': 'Not EL Active or Monitored 1-2 yr',
        'English Learner': 'EL Active',
        'At-Risk': 'Econ Dis',       # close proxy, not exact
        'Economically Disadvantaged': 'Econ Dis',
    }
    df['Student Group Value'] = df['Student Group Value'].replace(subgroup_map)

    print(f"  After filtering: {len(df):,} rows")
    print(f"  Years: {sorted(df['year'].dropna().unique())}")
    print(f"  Cohort grades: {sorted(df['cohort_grade'].unique())}")
    print(f"  Schools: {df['School Name'].nunique()}")

    return df


# ═════════════════════════════════════════════════════════════════════════
# Cohort Growth Computation
# ═════════════════════════════════════════════════════════════════════════

def compute_cohort_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each school/subject/subgroup, match Grade N in Year Y to Grade N+1
    in Year Y+1, computing the percentage-point change.

    Returns a DataFrame with one row per cohort transition.
    """
    print("\n" + "=" * 70)
    print("COMPUTING COHORT GROWTH")
    print("=" * 70)

    # We join the data to itself: left side = baseline year, right side = next year
    # Join condition: same school, subject, subgroup AND cohort_grade+1, year+1
    merge_cols = ['School Code', 'School Name', 'LEA Code', 'LEA Name',
                  'Subject', 'Student Group', 'Student Group Value']

    # Prepare baseline (left) and follow-up (right) frames
    base = df.copy()
    base['next_grade'] = base['cohort_grade'] + 1
    base['next_year'] = base['year'] + 1

    follow = df[['School Code', 'Subject', 'Student Group', 'Student Group Value',
                 'cohort_grade', 'year',
                 'percent_value', 'count_value', 'total_count_value',
                 'Assessment Name', 'Tested Grade/Subject']].copy()
    follow = follow.rename(columns={
        'cohort_grade': 'follow_grade',
        'year': 'follow_year',
        'percent_value': 'percent_follow',
        'count_value': 'count_follow',
        'total_count_value': 'total_count_follow',
        'Assessment Name': 'assessment_follow',
        'Tested Grade/Subject': 'follow_tested_grade',
    })

    # Merge
    merged = base.merge(
        follow,
        left_on=['School Code', 'Subject', 'Student Group', 'Student Group Value',
                 'next_grade', 'next_year'],
        right_on=['School Code', 'Subject', 'Student Group', 'Student Group Value',
                  'follow_grade', 'follow_year'],
        how='inner'
    )

    if merged.empty:
        print("  WARNING: No cohort matches found. Check grade/year data.")
        return pd.DataFrame()

    # Calculate growth
    merged['pp_growth'] = merged['percent_follow'] - merged['percent_value']

    # Build clean output
    result = merged[[
        'LEA Code', 'LEA Name', 'School Code', 'School Name',
        'Subject', 'Student Group', 'Student Group Value',
        'cohort_grade', 'Tested Grade/Subject',
        'year', 'percent_value', 'count_value', 'total_count_value',
        'Assessment Name',
        'next_grade', 'next_year',
        'percent_follow', 'count_follow', 'total_count_follow',
        'assessment_follow', 'follow_tested_grade',
        'pp_growth',
    ]].copy()

    result = result.rename(columns={
        'cohort_grade': 'baseline_grade',
        'Tested Grade/Subject': 'baseline_tested_grade',
        'year': 'baseline_year',
        'percent_value': 'baseline_pct',
        'count_value': 'baseline_count',
        'total_count_value': 'baseline_total',
        'Assessment Name': 'baseline_assessment',
        'next_grade': 'followup_grade',
        'next_year': 'followup_year',
        'percent_follow': 'followup_pct',
        'count_follow': 'followup_count',
        'total_count_follow': 'followup_total',
        'assessment_follow': 'followup_assessment',
        'follow_tested_grade': 'followup_tested_grade',
    })

    result['baseline_grade_label'] = result['baseline_grade'].apply(lambda g: f'Grade {g}')

    result['followup_grade_label'] = result['followup_grade'].apply(lambda g: f'Grade {g}')
    result['transition_label'] = (
        'Gr' + result['baseline_grade'].astype(str) + '→Gr' + result['followup_grade'].astype(str)
        + ' (' + result['baseline_year'].astype(str) + '→' + result['followup_year'].astype(str) + ')'
    )

    result = result.sort_values(
        ['School Name', 'Subject', 'Student Group Value', 'baseline_year', 'baseline_grade']
    ).reset_index(drop=True)

    print(f"  Cohort transitions found: {len(result):,}")
    print(f"  Year pairs: {sorted(result[['baseline_year','followup_year']].drop_duplicates().apply(tuple, axis=1).tolist())}")
    print(f"  Schools with transitions: {result['School Name'].nunique()}")

    return result


def create_cohort_summary(detail: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate cohort growth to the school / subject / subgroup level.

    For each school–subject–subgroup combination, compute:
    - avg_pp_growth: mean pp growth across all cohort transitions
    - median_pp_growth: median
    - n_transitions: how many grade-pairs contributed
    - transitions: which grade transitions (e.g., "Gr3→4, Gr4→5")
    - latest_transition_growth: growth from the most recent transition
    """
    print("\n" + "=" * 70)
    print("CREATING COHORT GROWTH SUMMARY")
    print("=" * 70)

    group_cols = ['LEA Code', 'LEA Name', 'School Code', 'School Name',
                  'Subject', 'Student Group', 'Student Group Value']

    summary = (
        detail
        .groupby(group_cols, as_index=False)
        .agg(
            avg_pp_growth=('pp_growth', 'mean'),
            median_pp_growth=('pp_growth', 'median'),
            min_pp_growth=('pp_growth', 'min'),
            max_pp_growth=('pp_growth', 'max'),
            n_transitions=('pp_growth', 'count'),
            avg_baseline_pct=('baseline_pct', 'mean'),
            avg_followup_pct=('followup_pct', 'mean'),
        )
    )

    # Add the latest transition's growth
    latest = (
        detail
        .sort_values('baseline_year')
        .groupby(group_cols, as_index=False)
        .last()
        [group_cols + ['pp_growth', 'baseline_year', 'followup_year',
                       'baseline_grade', 'followup_grade']]
        .rename(columns={
            'pp_growth': 'latest_pp_growth',
            'baseline_year': 'latest_baseline_year',
            'followup_year': 'latest_followup_year',
        })
    )
    summary = summary.merge(latest, on=group_cols, how='left')

    # Round for readability
    for col in ['avg_pp_growth', 'median_pp_growth', 'min_pp_growth', 'max_pp_growth',
                'avg_baseline_pct', 'avg_followup_pct', 'latest_pp_growth']:
        if col in summary.columns:
            summary[col] = summary[col].round(2)

    summary = summary.sort_values(
        ['School Name', 'Subject', 'Student Group Value']
    ).reset_index(drop=True)

    print(f"  Summary rows: {len(summary):,}")
    return summary


def create_pivot_workbook(detail: pd.DataFrame, summary: pd.DataFrame, output_path: str):
    """
    Create an Excel workbook with multiple sheets for easy exploration.
    """
    pivot_file = os.path.join(output_path, 'cohort_growth_pivot.xlsx')
    print(f"\n  Creating Excel workbook: {pivot_file}")

    try:
        with pd.ExcelWriter(pivot_file, engine='openpyxl') as writer:
            # Sheet 1: Summary – all students, sorted by growth
            all_students_summary = summary[
                summary['Student Group Value'] == 'All Students'
            ].sort_values('avg_pp_growth', ascending=False)
            all_students_summary.to_excel(writer, sheet_name='All Students Summary', index=False)

            # Sheet 2: Full summary
            summary.to_excel(writer, sheet_name='Full Summary', index=False)

            # Sheet 3: Detail for "All Students"
            all_detail = detail[
                detail['Student Group Value'] == 'All Students'
            ]
            all_detail.to_excel(writer, sheet_name='All Students Detail', index=False)

            # Sheet 4: ELA cohort pivot (schools × transition)
            ela_detail = all_detail[all_detail['Subject'] == 'ELA']
            if not ela_detail.empty:
                ela_pivot = ela_detail.pivot_table(
                    index=['School Name'],
                    columns='transition_label',
                    values='pp_growth',
                    aggfunc='mean'
                ).round(2)
                ela_pivot.to_excel(writer, sheet_name='ELA Cohort Pivot')

            # Sheet 5: Math cohort pivot
            math_detail = all_detail[all_detail['Subject'] == 'Math']
            if not math_detail.empty:
                math_pivot = math_detail.pivot_table(
                    index=['School Name'],
                    columns='transition_label',
                    values='pp_growth',
                    aggfunc='mean'
                ).round(2)
                math_pivot.to_excel(writer, sheet_name='Math Cohort Pivot')

            # Sheet 6: Full detail
            detail.to_excel(writer, sheet_name='Full Detail', index=False)

        print(f"  ✓ Saved workbook with {6} sheets")
    except Exception as e:
        print(f"  WARNING: Could not create Excel workbook: {e}")
        print(f"  (CSV outputs are still available)")


# ═════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════

def main():
    """Run the full cohort growth analysis pipeline."""
    # Load
    df = load_and_prepare()

    # Compute cohort growth
    detail = compute_cohort_growth(df)
    if detail.empty:
        print("\nNo cohort growth data could be computed. Exiting.")
        return

    # Create summary
    summary = create_cohort_summary(detail)

    # ── Save outputs ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SAVING OUTPUTS")
    print("=" * 70)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    detail_file = os.path.join(OUTPUT_PATH, 'cohort_growth_detail.csv')
    detail.to_csv(detail_file, index=False)
    print(f"  ✓ {detail_file} ({len(detail):,} rows)")

    summary_file = os.path.join(OUTPUT_PATH, 'cohort_growth_summary.csv')
    summary.to_csv(summary_file, index=False)
    print(f"  ✓ {summary_file} ({len(summary):,} rows)")

    create_pivot_workbook(detail, summary, OUTPUT_PATH)

    # ── Print highlights ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    all_stu = summary[summary['Student Group Value'] == 'All Students']

    for subject in ['ELA', 'Math']:
        subj_data = all_stu[all_stu['Subject'] == subject].copy()
        if subj_data.empty:
            continue

        print(f"\n── {subject} Cohort Growth (All Students) ──")
        print(f"  Schools with data: {len(subj_data)}")
        print(f"  Average growth: {subj_data['avg_pp_growth'].mean():.2f} pp")
        print(f"  Median growth:  {subj_data['median_pp_growth'].median():.2f} pp")

        print(f"\n  Top 10 schools by avg cohort growth:")
        top = subj_data.nlargest(10, 'avg_pp_growth')
        for _, row in top.iterrows():
            print(f"    {row['School Name']}: +{row['avg_pp_growth']:.1f} pp "
                  f"(n={int(row['n_transitions'])} transitions)")

        print(f"\n  Bottom 5 schools by avg cohort growth:")
        bottom = subj_data.nsmallest(5, 'avg_pp_growth')
        for _, row in bottom.iterrows():
            sign = '+' if row['avg_pp_growth'] >= 0 else ''
            print(f"    {row['School Name']}: {sign}{row['avg_pp_growth']:.1f} pp")

    # ── Validate against Stuart-Hobson manual example ────────────────────
    print("\n" + "=" * 70)
    print("VALIDATION: Stuart-Hobson Manual Example")
    print("=" * 70)

    sh = detail[detail['School Name'].str.contains('Stuart', case=False, na=False)]
    if not sh.empty:
        sh_all = sh[sh['Student Group Value'].isin(['All Students'])]
        print(f"\n  Stuart-Hobson 'All Students' transitions: {len(sh_all)}")
        for _, row in sh_all.sort_values(['Subject', 'baseline_year', 'baseline_grade']).iterrows():
            print(f"    {row['Subject']} {row['transition_label']}: "
                  f"{row['baseline_pct']:.1f}% → {row['followup_pct']:.1f}% "
                  f"({'+' if row['pp_growth'] >= 0 else ''}{row['pp_growth']:.1f} pp)")
        
        print(f"\n  All Stuart-Hobson transitions (all subgroups): {len(sh)}")
        for _, row in sh.sort_values(['Subject', 'Student Group Value', 'baseline_year', 'baseline_grade']).iterrows():
            print(f"    {row['Subject']} | {row['Student Group Value']:30s} | {row['transition_label']}: "
                  f"{row['baseline_pct']:.1f}% → {row['followup_pct']:.1f}% "
                  f"({'+' if row['pp_growth'] >= 0 else ''}{row['pp_growth']:.1f} pp)")
        print("\n  Compare with manual spreadsheet:")
        print("    ELA Gr6→Gr7 (2022→2023): 33.5% → 40.5% (+7.0 pp)")
        print("    ELA Gr7→Gr8 (2022→2023): 36.3% → 46.6% (+10.3 pp)")
        print("    Math Gr6→Gr7 (2022→2023): 11.0% → 14.7% (+3.6 pp)")
        print("    Math Gr7→Gr8 (2022→2023): 13.7% → 19.6% (+5.9 pp)")
    else:
        print("  Stuart-Hobson not found in data (may be filtered out)")

    print("\n" + "=" * 70)
    print("COHORT GROWTH ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
