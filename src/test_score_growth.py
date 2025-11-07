import os
import os.path
from typing import List

import pandas as pd

# Import new modular components
import config
from data_loader import load_all_input_files, standardize_subgroup_value
from data_utils import logger, create_processing_report

# Set up paths
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
INPUT_PATH = os.path.abspath(f"{CURRENT_PATH}/../input_data")
OUTPUT_PATH = os.path.abspath(f"{CURRENT_PATH}/../output_data")

# Update config with paths
config.CURRENT_PATH = CURRENT_PATH
config.INPUT_PATH = INPUT_PATH
config.OUTPUT_PATH = OUTPUT_PATH

# Optional: customize these to narrow comparisons
SELECTED_SCHOOLS: List[str] = config.SELECTED_SCHOOLS
SUBGROUP_VALUES_FOR_FILTER: List[str] = config.SUBGROUP_VALUES_FOR_FILTER


def _ensure_output_dir():
    os.makedirs(OUTPUT_PATH, exist_ok=True)


def _pivot_all_years(df: pd.DataFrame, value_col: str, index_cols: List[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    piv = df.pivot_table(index=index_cols, columns='year', values=value_col, aggfunc='mean')
    # Rename columns to include the value name for clarity
    rename_map = {}
    for yr in piv.columns:
        base = value_col.replace('_value', '')
        rename_map[yr] = f"{base}_{yr}"
    piv = piv.rename(columns=rename_map)
    return piv


def _add_growth_columns(piv: pd.DataFrame, base_name: str) -> pd.DataFrame:
    if piv.empty:
        return piv
    # Identify year columns
    year_cols = sorted([c for c in piv.columns if c.startswith(base_name + '_')], key=lambda x: int(x.split('_')[-1]))
    if len(year_cols) >= 2:
        first_col = year_cols[0]
        last_col = year_cols[-1]
        piv[f'{base_name}_growth_first_to_last'] = piv[last_col] - piv[first_col]
        prev_col = year_cols[-2]
        piv[f'{base_name}_growth_last_vs_prev'] = piv[last_col] - piv[prev_col]
    return piv


def main():
    _ensure_output_dir()

    # Load all input data using the new modular loader
    logger.info("Starting DC school test score analysis")
    multi_year, stats = load_all_input_files(INPUT_PATH, SELECTED_SCHOOLS)

    if multi_year.empty:
        logger.error('No input data found in ' + INPUT_PATH)
        stats.print_summary()
        return

    stats.print_summary()

    # Keep a familiar filtered export for configured subgroups (across all years)
    filtered = multi_year[multi_year['subgroup_value_std'].isin([standardize_subgroup_value(v) for v in SUBGROUP_VALUES_FOR_FILTER])]
    filtered.to_csv(os.path.join(OUTPUT_PATH, 'filtered_data.csv'), index=False)
    logger.info(f"Saved filtered data ({len(filtered):,} rows) to filtered_data.csv")

    # Compute growth at a stable grain (match exact combinations across years)
    index_cols = config.GROWTH_INDEX_COLS

    percent_p = _pivot_all_years(multi_year, 'percent_value', index_cols)
    count_p = _pivot_all_years(multi_year, 'count_value', index_cols)
    totcount_p = _pivot_all_years(multi_year, 'total_count_value', index_cols)

    # Merge pivots
    growth = percent_p
    for p in [count_p, totcount_p]:
        if not p.empty:
            growth = growth.join(p, how='outer')

    # Derive growth metrics (first-to-last, and last-vs-prev)
    growth = _add_growth_columns(growth, 'percent')
    growth = _add_growth_columns(growth, 'count')
    growth = _add_growth_columns(growth, 'total_count')

    growth = growth.reset_index()
    growth.to_csv(os.path.join(OUTPUT_PATH, 'school_growth_full.csv'), index=False)
    logger.info(f"Saved full growth data ({len(growth):,} rows) to school_growth_full.csv")

    # Summary by School x Subject x Subgroup across all years
    summary = (
        multi_year
        .groupby(['School Name', 'Subject', 'subgroup_value_std', 'year'], as_index=False)
        .agg(percent_mean=('percent_value', 'mean'))
    )
    summary_p = summary.pivot_table(index=['School Name', 'Subject', 'subgroup_value_std'], columns='year', values='percent_mean')
    # Add growth summaries
    # Build a DataFrame to work on
    summary_p = summary_p.copy()
    if not summary_p.empty:
        years = sorted([c for c in summary_p.columns if isinstance(c, (int, float))])
        if len(years) >= 2:
            first, last = years[0], years[-1]
            summary_p['growth_first_to_last'] = summary_p[last] - summary_p[first]
            prev = years[-2]
            summary_p['growth_last_vs_prev'] = summary_p[last] - summary_p[prev]
    summary_p = summary_p.reset_index()
    summary_p.to_csv(os.path.join(OUTPUT_PATH, 'school_growth_by_school_subject.csv'), index=False)
    logger.info(f"Saved summary growth data ({len(summary_p):,} rows) to school_growth_by_school_subject.csv")

    # Optional Excel export with both views
    # Temporarily disabled - uncomment to enable
    # try:
    #     logger.info("Creating Excel workbook (this may take a moment for large datasets)...")
    #     with pd.ExcelWriter(os.path.join(OUTPUT_PATH, 'school_growth_pivot.xlsx'), engine='openpyxl') as writer:
    #         growth.to_excel(writer, sheet_name='full_grain_growth', index=False)
    #         summary_p.to_excel(writer, sheet_name='by_school_subject', index=False)
    #     logger.info("Saved Excel workbook to school_growth_pivot.xlsx")
    # except Exception as e:
    #     # If openpyxl isn't installed, skip Excel export gracefully
    #     logger.warning(f"Could not create Excel export: {e}")
    
    logger.info("Skipping Excel export (can be slow for large datasets)")
    
    # Create processing report
    create_processing_report(multi_year, stats, OUTPUT_PATH)
    
    logger.info("Analysis complete!")


# Expose this function for use by the app
def _load_all_input() -> pd.DataFrame:
    """Legacy function for backwards compatibility with app.py"""
    multi_year, _ = load_all_input_files(INPUT_PATH, SELECTED_SCHOOLS)
    return multi_year


if __name__ == '__main__':
    main()
