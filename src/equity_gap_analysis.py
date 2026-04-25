"""
Equity Gap Analysis for DC school test scores.

For every school, subject, and cohort transition, computes the difference
between each student subgroup and the "All Students" reference:

    proficiency_gap  = subgroup baseline_pct  − All Students baseline_pct
    followup_gap     = subgroup followup_pct   − All Students followup_pct
    gap_change       = followup_gap − proficiency_gap
                       (positive → gap narrowed; negative → gap widened)
    growth_gap       = subgroup pp_growth − All Students pp_growth
                       (positive → subgroup grew faster than average)

Outputs:
    equity_gap_detail.csv   – one row per school / subgroup / transition
    equity_gap_summary.csv  – school × subject × subgroup aggregates

Usage:
    python src/equity_gap_analysis.py

Dependencies:
    - output_data/cohort_growth_detail.csv (produced by analyze_cohort_growth.py)
"""
import os
import sys
import numpy as np
import pandas as pd
from typing import List

# ── Paths ────────────────────────────────────────────────────────────────
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, '..', 'output_data'))
DETAIL_FILE = os.path.join(OUTPUT_PATH, 'cohort_growth_detail.csv')

# Subgroups typically representing disadvantaged populations
DISADVANTAGED_SUBGROUPS = {
    'Black or African American',
    'Hispanic/Latino of any race',
    'EL Active',
    'Econ Dis',
    'Students with Disabilities',
}


# ═════════════════════════════════════════════════════════════════════════
# Core computation
# ═════════════════════════════════════════════════════════════════════════

def load_cohort_detail() -> pd.DataFrame:
    """Load cohort growth detail CSV."""
    if not os.path.isfile(DETAIL_FILE):
        print(f"ERROR: {DETAIL_FILE} not found.")
        print("Run python src/analyze_cohort_growth.py first.")
        sys.exit(1)
    df = pd.read_csv(DETAIL_FILE)
    print(f"Loaded cohort growth detail: {len(df):,} rows")
    return df


def compute_equity_gaps(detail: pd.DataFrame) -> pd.DataFrame:
    """
    Merge each subgroup's transitions with the 'All Students' reference for the
    same school / subject / transition_label and compute gap metrics.

    Returns a DataFrame with one row per school / subgroup / transition
    (excluding 'All Students' rows, which are the reference).
    """
    print("\n" + "=" * 70)
    print("COMPUTING EQUITY GAPS")
    print("=" * 70)

    # Build All-Students reference
    ref_cols = [
        'School Name', 'School Code', 'LEA Code', 'LEA Name',
        'Subject', 'transition_label',
        'baseline_year', 'followup_year',
        'baseline_grade', 'followup_grade',
    ]
    all_stu = detail[detail['Student Group Value'] == 'All Students'].copy()
    subgroups = detail[detail['Student Group Value'] != 'All Students'].copy()

    print(f"  All Students rows (reference): {len(all_stu):,}")
    print(f"  Subgroup rows: {len(subgroups):,}")

    if all_stu.empty:
        print("  WARNING: No 'All Students' rows found — cannot compute equity gaps.")
        return pd.DataFrame()

    # Rename All-Students columns for merge disambiguation
    ref = all_stu[ref_cols + ['baseline_pct', 'followup_pct', 'pp_growth']].rename(columns={
        'baseline_pct': 'all_baseline_pct',
        'followup_pct': 'all_followup_pct',
        'pp_growth':    'all_pp_growth',
    })

    # Merge on school + subject + transition
    merge_keys = ['School Name', 'School Code', 'LEA Code', 'LEA Name',
                  'Subject', 'transition_label',
                  'baseline_year', 'followup_year',
                  'baseline_grade', 'followup_grade']
    merged = subgroups.merge(ref[merge_keys + ['all_baseline_pct', 'all_followup_pct', 'all_pp_growth']],
                             on=merge_keys, how='inner')

    if merged.empty:
        print("  WARNING: No matching All Students reference rows found after merge.")
        return pd.DataFrame()

    # ── Gap metrics ──────────────────────────────────────────────────────
    # Proficiency gap at baseline (negative = below average)
    merged['proficiency_gap'] = (merged['baseline_pct'] - merged['all_baseline_pct']).round(2)

    # Proficiency gap at follow-up
    merged['followup_gap'] = (merged['followup_pct'] - merged['all_followup_pct']).round(2)

    # Gap change: positive = gap narrowed (subgroup catching up), negative = widened
    merged['gap_change'] = (merged['followup_gap'] - merged['proficiency_gap']).round(2)

    # Growth gap: subgroup grew faster (+) or slower (-) than All Students
    merged['growth_gap'] = (merged['pp_growth'] - merged['all_pp_growth']).round(2)

    # Flag disadvantaged subgroups
    merged['is_disadvantaged'] = merged['Student Group Value'].isin(DISADVANTAGED_SUBGROUPS)

    print(f"  Equity gap rows computed: {len(merged):,}")
    print(f"  Schools with data: {merged['School Name'].nunique()}")
    return merged


def create_equity_summary(equity: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate equity gap detail to school / subject / subgroup level.

    For each combination compute:
    - avg_proficiency_gap: mean baseline gap across transitions
    - avg_growth_gap:      mean growth-gap (positive = growing faster than avg)
    - avg_gap_change:      mean gap change (positive = gap narrowing on average)
    - pct_narrowing:       % of transitions where the gap narrowed (gap_change > 0)
    - n_transitions:       count of transitions with data
    """
    print("\n" + "=" * 70)
    print("CREATING EQUITY GAP SUMMARY")
    print("=" * 70)

    group_cols = [
        'LEA Code', 'LEA Name', 'School Code', 'School Name',
        'Subject', 'Student Group', 'Student Group Value', 'is_disadvantaged',
    ]

    def _pct_narrowing(x: pd.Series) -> float:
        return round(100.0 * (x > 0).sum() / len(x), 1) if len(x) > 0 else np.nan

    summary = (
        equity
        .groupby(group_cols, as_index=False)
        .agg(
            avg_proficiency_gap=('proficiency_gap', 'mean'),
            avg_followup_gap=('followup_gap', 'mean'),
            avg_gap_change=('gap_change', 'mean'),
            avg_growth_gap=('growth_gap', 'mean'),
            n_transitions=('gap_change', 'count'),
        )
    )

    # pct_narrowing separately (needs lambda)
    narrowing = (
        equity
        .groupby(group_cols, as_index=False)['gap_change']
        .agg(pct_narrowing=_pct_narrowing)
    )
    summary = summary.merge(narrowing, on=group_cols, how='left')

    # Round numeric columns
    for col in ['avg_proficiency_gap', 'avg_followup_gap', 'avg_gap_change',
                'avg_growth_gap']:
        if col in summary.columns:
            summary[col] = summary[col].round(2)

    summary = summary.sort_values(
        ['Student Group Value', 'Subject', 'avg_proficiency_gap']
    ).reset_index(drop=True)

    print(f"  Equity summary rows: {len(summary):,}")
    return summary


# ═════════════════════════════════════════════════════════════════════════
# Reporting helpers
# ═════════════════════════════════════════════════════════════════════════

def print_citywide_equity_summary(equity: pd.DataFrame) -> None:
    """Print a compact citywide equity summary to stdout."""
    print("\n" + "=" * 70)
    print("CITYWIDE EQUITY SUMMARY (all schools aggregated)")
    print("=" * 70)

    citywide = (
        equity
        .groupby(['Student Group Value', 'Subject'], as_index=False)
        .agg(
            avg_proficiency_gap=('proficiency_gap', 'mean'),
            avg_growth_gap=('growth_gap', 'mean'),
            avg_gap_change=('gap_change', 'mean'),
            n_transitions=('gap_change', 'count'),
        )
        .round(2)
    )

    for subject in ['ELA', 'Math']:
        subj = citywide[citywide['Subject'] == subject].sort_values('avg_proficiency_gap')
        if subj.empty:
            continue
        print(f"\n── {subject} ──")
        print(f"  {'Subgroup':<40} {'Proficiency Gap':>16} {'Growth Gap':>12} {'Gap Change':>12} {'N':>6}")
        print(f"  {'-'*40} {'-'*16} {'-'*12} {'-'*12} {'-'*6}")
        for _, row in subj.iterrows():
            pg = f"{row['avg_proficiency_gap']:+.1f} pp"
            gg = f"{row['avg_growth_gap']:+.1f} pp"
            gc = f"{row['avg_gap_change']:+.1f} pp"
            print(f"  {row['Student Group Value']:<40} {pg:>16} {gg:>12} {gc:>12} {int(row['n_transitions']):>6}")

    print()
    print("  Notes:")
    print("  - Proficiency Gap: subgroup baseline proficiency minus All Students baseline.")
    print("    Negative means the subgroup starts below average.")
    print("  - Growth Gap: subgroup cohort growth minus All Students growth.")
    print("    Positive means the subgroup grew faster than the city average.")
    print("  - Gap Change: followup gap minus baseline gap.")
    print("    Positive means the achievement gap narrowed over the transition.")


def print_school_equity_highlights(equity_summary: pd.DataFrame) -> None:
    """Print schools with notable equity outcomes."""
    print("\n" + "=" * 70)
    print("SCHOOL-LEVEL EQUITY HIGHLIGHTS")
    print("=" * 70)

    disadv_summary = equity_summary[equity_summary['is_disadvantaged']].copy()
    if disadv_summary.empty:
        print("  No disadvantaged-subgroup data available.")
        return

    for subject in ['ELA', 'Math']:
        subj = disadv_summary[disadv_summary['Subject'] == subject]
        if subj.empty:
            continue

        best_narrowing = subj.nlargest(5, 'avg_gap_change')
        print(f"\n── {subject}: Top 5 schools for gap narrowing (disadvantaged subgroups) ──")
        for _, row in best_narrowing.iterrows():
            print(f"  {row['School Name']} | {row['Student Group Value']}: "
                  f"gap change = {row['avg_gap_change']:+.1f} pp over {int(row['n_transitions'])} transition(s)")

        most_negative = subj.nsmallest(5, 'avg_proficiency_gap')
        print(f"\n── {subject}: Subgroup-school combinations with largest baseline gaps ──")
        for _, row in most_negative.iterrows():
            print(f"  {row['School Name']} | {row['Student Group Value']}: "
                  f"proficiency gap = {row['avg_proficiency_gap']:+.1f} pp")


# ═════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════

def main():
    """Run the equity gap analysis pipeline."""
    detail = load_cohort_detail()

    equity = compute_equity_gaps(detail)
    if equity.empty:
        print("\nCould not compute equity gaps. Exiting.")
        sys.exit(1)

    equity_summary = create_equity_summary(equity)

    # ── Save outputs ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SAVING OUTPUTS")
    print("=" * 70)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    detail_out = os.path.join(OUTPUT_PATH, 'equity_gap_detail.csv')
    equity.to_csv(detail_out, index=False)
    print(f"  ✓ {detail_out} ({len(equity):,} rows)")

    summary_out = os.path.join(OUTPUT_PATH, 'equity_gap_summary.csv')
    equity_summary.to_csv(summary_out, index=False)
    print(f"  ✓ {summary_out} ({len(equity_summary):,} rows)")

    # ── Print highlights ─────────────────────────────────────────────────
    print_citywide_equity_summary(equity)
    print_school_equity_highlights(equity_summary)

    print("\n" + "=" * 70)
    print("EQUITY GAP ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
