"""
School Rankings by Cohort Growth — DC Schools Test Score Analysis.

Reads the cohort growth summary and equity gap summary to produce two
ranked tables that support policy analysis:

  1. school_rankings.csv — Schools ranked by avg cohort growth (pp)
     for each subject (ELA and Math), filtered to the "All Students"
     subgroup so that rankings reflect the full student body.

  2. school_equity_rankings.csv — Schools ranked by average gap-change
     for disadvantaged subgroups, identifying which schools are most
     (and least) effective at narrowing equity gaps.

Usage:
    python src/generate_school_rankings.py

Dependencies:
    - output_data/cohort_growth_summary.csv (produced by analyze_cohort_growth.py)
    - output_data/equity_gap_summary.csv    (produced by equity_gap_analysis.py)
"""
import os
import sys
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, '..', 'output_data'))

COHORT_SUMMARY_FILE = os.path.join(OUTPUT_PATH, 'cohort_growth_summary.csv')
EQUITY_SUMMARY_FILE = os.path.join(OUTPUT_PATH, 'equity_gap_summary.csv')
RANKINGS_FILE = os.path.join(OUTPUT_PATH, 'school_rankings.csv')
EQUITY_RANKINGS_FILE = os.path.join(OUTPUT_PATH, 'school_equity_rankings.csv')

ALL_STUDENTS_LABELS = {'All Students', 'All', 'Total'}
DISADVANTAGED_SUBGROUPS = {
    'Black or African American',
    'Hispanic/Latino of any race',
    'EL Active',
    'Econ Dis',
    'Students with Disabilities',
}


# ═════════════════════════════════════════════════════════════════════════
# Data loading
# ═════════════════════════════════════════════════════════════════════════

def load_cohort_summary() -> pd.DataFrame:
    if not os.path.isfile(COHORT_SUMMARY_FILE):
        print(f'ERROR: {COHORT_SUMMARY_FILE} not found.')
        print('Run python src/analyze_cohort_growth.py first.')
        sys.exit(1)
    df = pd.read_csv(COHORT_SUMMARY_FILE)
    print(f'Loaded cohort summary: {len(df):,} rows')
    return df


def load_equity_summary() -> pd.DataFrame:
    if not os.path.isfile(EQUITY_SUMMARY_FILE):
        print(f'ERROR: {EQUITY_SUMMARY_FILE} not found.')
        print('Run python src/equity_gap_analysis.py first.')
        sys.exit(1)
    df = pd.read_csv(EQUITY_SUMMARY_FILE)
    print(f'Loaded equity gap summary: {len(df):,} rows')
    return df


# ═════════════════════════════════════════════════════════════════════════
# Rankings computation
# ═════════════════════════════════════════════════════════════════════════

def compute_overall_rankings(cohort_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Rank schools by average cohort growth for the 'All Students' subgroup.

    Returns one row per school × subject with:
      - avg_pp_growth           : mean percentage-point cohort growth
      - n_transitions           : number of cohort transitions included
      - pct_positive_growth     : % of transitions with positive growth
      - pct_significant_transitions : % of transitions with p < 0.05
      - rank                    : rank within subject (1 = highest growth)
    """
    # Filter to All Students rows only
    mask = cohort_summary['Student Group Value'].isin(ALL_STUDENTS_LABELS)
    df = cohort_summary[mask].copy()

    if df.empty:
        print('WARNING: no All Students rows found in cohort summary.')
        return pd.DataFrame()

    # Compute extra metrics if available
    out_cols = ['School Name', 'Subject', 'avg_pp_growth', 'n_transitions']
    if 'pct_significant_transitions' in df.columns:
        out_cols.append('pct_significant_transitions')

    rankings = df[out_cols].copy()

    # Compute pct positive growth from detail if not present
    # (Cohort summary does not always carry this; derive from avg direction)
    rankings['avg_pp_growth'] = pd.to_numeric(rankings['avg_pp_growth'], errors='coerce')

    # Add rank within each subject
    rankings['rank'] = (
        rankings
        .groupby('Subject')['avg_pp_growth']
        .rank(method='min', ascending=False)
        .astype('Int64')
    )

    rankings = rankings.sort_values(['Subject', 'rank'])
    rankings = rankings.reset_index(drop=True)

    print(f'Overall rankings: {len(rankings)} rows across {rankings["Subject"].nunique()} subjects')
    return rankings


def compute_equity_rankings(equity_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Rank schools by how effectively they narrow equity gaps for
    disadvantaged student subgroups.

    Metric used: avg_gap_change (positive = gap narrowing).

    Returns one row per school × subject with:
      - avg_gap_change          : mean gap-change across disadvantaged subgroups
                                  (positive = gap narrowed on average)
      - avg_growth_gap          : mean growth-gap (subgroup grew faster than All Students)
      - n_subgroups             : number of disadvantaged subgroups with data
      - pct_narrowing           : % of subgroup/transitions where gap narrowed
      - equity_rank             : rank within subject (1 = most gap-narrowing)
    """
    # Filter to disadvantaged subgroups only
    mask = equity_summary['Student Group Value'].isin(DISADVANTAGED_SUBGROUPS)
    df = equity_summary[mask].copy()

    if df.empty:
        print('WARNING: no disadvantaged subgroup rows found in equity summary.')
        return pd.DataFrame()

    numeric_cols = ['avg_gap_change', 'avg_growth_gap', 'n_transitions', 'pct_narrowing']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Aggregate across disadvantaged subgroups per school × subject
    agg_dict = {}
    if 'avg_gap_change' in df.columns:
        agg_dict['avg_gap_change'] = ('avg_gap_change', 'mean')
    if 'avg_growth_gap' in df.columns:
        agg_dict['avg_growth_gap'] = ('avg_growth_gap', 'mean')
    if 'pct_narrowing' in df.columns:
        agg_dict['pct_narrowing'] = ('pct_narrowing', 'mean')

    agg_dict['n_subgroups'] = ('Student Group Value', 'count')

    equity_rankings = (
        df.groupby(['School Name', 'Subject'])
          .agg(**agg_dict)
          .reset_index()
    )

    # Add rank within each subject by avg_gap_change (higher = more gap-narrowing)
    if 'avg_gap_change' in equity_rankings.columns:
        equity_rankings['equity_rank'] = (
            equity_rankings
            .groupby('Subject')['avg_gap_change']
            .rank(method='min', ascending=False)
            .astype('Int64')
        )
        equity_rankings = equity_rankings.sort_values(['Subject', 'equity_rank'])

    equity_rankings = equity_rankings.reset_index(drop=True)

    print(f'Equity rankings: {len(equity_rankings)} rows across {equity_rankings["Subject"].nunique()} subjects')
    return equity_rankings


# ═════════════════════════════════════════════════════════════════════════
# Reporting
# ═════════════════════════════════════════════════════════════════════════

def print_top_bottom(rankings: pd.DataFrame, rank_col: str, label_col: str,
                     metric_col: str, n: int = 10) -> None:
    """Print top-n and bottom-n schools for each subject."""
    for subject in sorted(rankings['Subject'].unique()):
        sub = rankings[rankings['Subject'] == subject].copy()
        sub = sub.dropna(subset=[metric_col]).sort_values(metric_col, ascending=False)

        print(f'\n  ── {subject} ──')
        print(f'  Top {min(n, len(sub))} schools:')
        for _, row in sub.head(n).iterrows():
            val = row[metric_col]
            print(f'    #{int(row[rank_col]):3d}  {row[label_col][:45]:<45}  {val:+.1f}')

        if len(sub) > n:
            print(f'  Bottom {min(n, len(sub))} schools:')
            for _, row in sub.tail(n).iterrows():
                val = row[metric_col]
                print(f'    #{int(row[rank_col]):3d}  {row[label_col][:45]:<45}  {val:+.1f}')


# ═════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════

def main() -> None:
    print('=' * 70)
    print('SCHOOL RANKINGS — DC Schools Test Score Analysis')
    print('=' * 70)

    cohort_summary = load_cohort_summary()
    equity_summary = load_equity_summary()

    # ── Overall rankings ────────────────────────────────────────────────
    print('\n── Overall Growth Rankings (All Students subgroup) ──')
    rankings = compute_overall_rankings(cohort_summary)
    if not rankings.empty:
        rankings.to_csv(RANKINGS_FILE, index=False)
        print(f'✓ Saved: {RANKINGS_FILE}')
        print(f'  {len(rankings):,} rows')
        print_top_bottom(rankings, 'rank', 'School Name', 'avg_pp_growth', n=10)

    # ── Equity rankings ─────────────────────────────────────────────────
    print('\n\n── Equity Gap Rankings (Disadvantaged Subgroups) ──')
    equity_rankings = compute_equity_rankings(equity_summary)
    if not equity_rankings.empty:
        equity_rankings.to_csv(EQUITY_RANKINGS_FILE, index=False)
        print(f'✓ Saved: {EQUITY_RANKINGS_FILE}')
        print(f'  {len(equity_rankings):,} rows')
        if 'equity_rank' in equity_rankings.columns:
            print_top_bottom(equity_rankings, 'equity_rank', 'School Name',
                             'avg_gap_change', n=10)

    print('\n' + '=' * 70)
    print('RANKINGS COMPLETE!')
    print('=' * 70)


if __name__ == '__main__':
    main()
