"""
Analyze DC school test score growth from the cleaned combined dataset.

This script reads the pre-cleaned combined_all_years.csv and computes:
- Year-over-year growth by school, subject, and subgroup
- Summary statistics and comparisons
"""
import os
import pandas as pd
import numpy as np
from typing import List

# Paths
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.abspath(f"{CURRENT_PATH}/../output_data")
COMBINED_DATA_FILE = os.path.join(OUTPUT_PATH, 'combined_all_years.csv')


def parse_percent(series: pd.Series) -> pd.Series:
    """
    Convert percent values to numeric, handling suppressed data.
    
    Returns NaN for: DS, n<10, <5%, etc.
    """
    def _parse_value(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().upper()
        # Suppressed values
        if s in ['DS', 'N<10', '<5%', '<=10%', 'N/A', 'NA', '']:
            return np.nan
        # Inequality markers
        if any(s.startswith(marker) for marker in ['<', '<=', '>', '>=']):
            return np.nan
        # Remove % sign and convert
        s = s.replace('%', '').strip()
        try:
            return float(s)
        except:
            return np.nan
    
    return series.apply(_parse_value)


def parse_count(series: pd.Series) -> pd.Series:
    """Convert count values to numeric, handling suppressed data."""
    def _parse_value(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().upper()
        if s in ['DS', 'N<10', '<5', '<=10', 'N/A', 'NA', '']:
            return np.nan
        try:
            return float(s)
        except:
            return np.nan
    
    return series.apply(_parse_value)


def load_and_prepare_data() -> pd.DataFrame:
    """Load the combined data and prepare it for analysis."""
    print("=" * 70)
    print("LOADING COMBINED DATA")
    print("=" * 70)
    
    if not os.path.exists(COMBINED_DATA_FILE):
        print(f"\nERROR: {COMBINED_DATA_FILE} not found!")
        print("Please run load_clean_data.py first to create the combined dataset.")
        return pd.DataFrame()
    
    print(f"\nReading: {COMBINED_DATA_FILE}")
    df = pd.read_csv(COMBINED_DATA_FILE, dtype=str)
    print(f"Loaded: {len(df):,} rows")
    
    # Parse numeric columns
    print("\nParsing numeric values...")
    df['percent_value'] = parse_percent(df['Percent'])
    df['count_value'] = parse_count(df['Count'])
    df['total_count_value'] = parse_count(df['Total Count'])
    df['year'] = pd.to_numeric(df['Year'], errors='coerce')
    
    # Rename columns for consistency with old code
    df = df.rename(columns={
        'Student Group Value': 'subgroup_value_std'
    })
    
    # Filter to school level only
    df = df[df['Aggregation Level'].str.upper() == 'SCHOOL']
    
    print(f"After filtering: {len(df):,} rows")
    print(f"Years: {sorted(df['year'].dropna().unique())}")
    print(f"Schools: {df['School Name'].nunique()}")
    print(f"Subjects: {sorted(df['Subject'].dropna().unique())}")
    
    return df


def compute_growth_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute year-over-year growth metrics.
    
    Creates a pivot table with years as columns and growth calculations.
    """
    print("\n" + "=" * 70)
    print("COMPUTING GROWTH METRICS")
    print("=" * 70)
    
    # Define the grain for analysis
    index_cols = [
        'LEA Code', 'LEA Name', 'School Code', 'School Name',
        'Assessment Name', 'Subject', 'Student Group', 'subgroup_value_std',
        'Tested Grade/Subject', 'Grade of Enrollment'
    ]
    
    # Create pivot tables for each metric
    print("\nPivoting data by year...")
    
    # Percent pivot
    percent_pivot = df.pivot_table(
        index=index_cols,
        columns='year',
        values='percent_value',
        aggfunc='mean'
    )
    
    # Rename columns
    percent_pivot.columns = [f'percent_{int(c)}' for c in percent_pivot.columns]
    
    # Count pivot
    count_pivot = df.pivot_table(
        index=index_cols,
        columns='year',
        values='count_value',
        aggfunc='sum'
    )
    count_pivot.columns = [f'count_{int(c)}' for c in count_pivot.columns]
    
    # Total count pivot
    total_pivot = df.pivot_table(
        index=index_cols,
        columns='year',
        values='total_count_value',
        aggfunc='sum'
    )
    total_pivot.columns = [f'total_count_{int(c)}' for c in total_pivot.columns]
    
    # Combine all pivots
    growth_df = percent_pivot.join([count_pivot, total_pivot], how='outer')
    
    # Calculate growth metrics
    print("Calculating growth metrics...")
    
    # Get year columns
    percent_cols = sorted([c for c in growth_df.columns if c.startswith('percent_')])
    
    if len(percent_cols) >= 2:
        first_col = percent_cols[0]
        last_col = percent_cols[-1]
        prev_col = percent_cols[-2]
        
        # First to last growth
        growth_df['percent_growth_first_to_last'] = growth_df[last_col] - growth_df[first_col]
        
        # Last vs previous year growth
        growth_df['percent_growth_last_vs_prev'] = growth_df[last_col] - growth_df[prev_col]
        
        print(f"  Growth from {first_col} to {last_col}")
        print(f"  Year-over-year: {prev_col} to {last_col}")
    
    growth_df = growth_df.reset_index()
    print(f"\nGrowth data: {len(growth_df):,} rows")
    
    return growth_df


def create_school_subject_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a summary table by School x Subject x Subgroup.
    
    Aggregates across grades to show school-level performance.
    """
    print("\n" + "=" * 70)
    print("CREATING SCHOOL-LEVEL SUMMARY")
    print("=" * 70)
    
    # Aggregate by school, subject, subgroup, and year
    summary = (
        df.groupby(['School Name', 'Subject', 'subgroup_value_std', 'year'], as_index=False)
        .agg(
            percent_mean=('percent_value', 'mean'),
            count_sum=('count_value', 'sum'),
            total_count_sum=('total_count_value', 'sum')
        )
    )
    
    # Pivot by year
    summary_pivot = summary.pivot_table(
        index=['School Name', 'Subject', 'subgroup_value_std'],
        columns='year',
        values='percent_mean'
    )
    
    # Add growth columns
    years = sorted([c for c in summary_pivot.columns])
    if len(years) >= 2:
        first_year, last_year = years[0], years[-1]
        summary_pivot['growth_first_to_last'] = summary_pivot[last_year] - summary_pivot[first_year]
        
        if len(years) >= 2:
            prev_year = years[-2]
            summary_pivot['growth_last_vs_prev'] = summary_pivot[last_year] - summary_pivot[prev_year]
    
    summary_pivot = summary_pivot.reset_index()
    print(f"Summary: {len(summary_pivot):,} rows")
    
    return summary_pivot


def save_outputs(growth_df: pd.DataFrame, summary_df: pd.DataFrame):
    """Save analysis outputs to CSV files."""
    print("\n" + "=" * 70)
    print("SAVING OUTPUTS")
    print("=" * 70)
    
    # Full growth data
    growth_file = os.path.join(OUTPUT_PATH, 'school_growth_full.csv')
    growth_df.to_csv(growth_file, index=False)
    print(f"✓ Saved: {growth_file}")
    print(f"  {len(growth_df):,} rows")
    
    # School-level summary
    summary_file = os.path.join(OUTPUT_PATH, 'school_growth_by_school_subject.csv')
    summary_df.to_csv(summary_file, index=False)
    print(f"✓ Saved: {summary_file}")
    print(f"  {len(summary_df):,} rows")
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)


def main():
    """Main analysis workflow."""
    # Load data
    df = load_and_prepare_data()
    
    if df.empty:
        return
    
    # Compute growth metrics
    growth_df = compute_growth_metrics(df)
    
    # Create school-level summary
    summary_df = create_school_subject_summary(df)
    
    # Save outputs
    save_outputs(growth_df, summary_df)
    
    # Print some interesting findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    
    # Top schools by recent growth
    if 'percent_growth_last_vs_prev' in summary_df.columns:
        print("\nTop 10 Schools by Recent Growth (last year vs previous):")
        top_growth = (
            summary_df[summary_df['subgroup_value_std'] == 'All Students']
            .nlargest(10, 'percent_growth_last_vs_prev')[['School Name', 'Subject', 'percent_growth_last_vs_prev']]
        )
        for idx, row in top_growth.iterrows():
            print(f"  {row['School Name']} ({row['Subject']}): +{row['percent_growth_last_vs_prev']:.1f}%")


if __name__ == '__main__':
    main()
