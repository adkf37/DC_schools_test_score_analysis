"""
Improved data loading utilities for DC school test score analysis.
"""
import os
import re
from typing import List, Optional, Dict, Tuple
import pandas as pd

from config import (
    COLUMN_MAPPINGS, SUBGROUP_STANDARDIZATION, EXPECTED_COLS,
    METRIC_FILTER, SKIP_SHEET_PATTERNS, REQUIRED_SHEET_COLUMNS,
    SUPPRESSED_VALUES
)
from data_utils import logger, validate_dataframe, DataLoadStats


def parse_percent(value):
    """
    Parse percent values, handling suppressed data markers.
    
    Returns pd.NA for suppressed or invalid values.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return pd.NA
    
    s = str(value).strip().upper()
    
    # Check for empty or suppressed values
    if s == '':
        return pd.NA
    
    for suppressed in SUPPRESSED_VALUES:
        if suppressed.upper() in s:
            return pd.NA
    
    # Handle inequality markers (< > <= >=)
    if any(s.startswith(marker) for marker in ['<', '<=', '>', '>=']):
        return pd.NA
    
    # Remove percent sign and parse
    s = s.replace('%', '').strip()
    try:
        return float(s)
    except (ValueError, TypeError):
        return pd.NA


def standardize_subgroup_value(val):
    """
    Standardize subgroup value names for consistency.
    
    Uses mapping from config.SUBGROUP_STANDARDIZATION.
    """
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return val
    
    s = str(val).strip()
    lower = s.lower()
    
    return SUBGROUP_STANDARDIZATION.get(lower, s)


def extract_year_from_filename(name: str) -> Optional[int]:
    """
    Extract the ending year from a filename.
    
    Supports patterns like:
    - 2023-2024 or 2024-25 or 2015-16 → returns ending year
    - 21_22 or 22-23 (shortened format) → returns 20xx
    - Single years like 2019 or 2022
    - "School Year 2016-17" format
    
    Returns None if no year pattern is found.
    """
    base = os.path.basename(name)
    
    # Pattern 1: Full range like 2023-2024 or 2024-25 or 2015-16
    m = re.search(r'(20\d{2})\s*[\-–_]\s*(\d{2,4})', base)
    if m:
        start = int(m.group(1))
        end_raw = m.group(2)
        # Handle 2-digit year (e.g., "25" in "2024-25")
        end = int(end_raw) if len(end_raw) == 4 else (2000 + int(end_raw))
        return end
    
    # Pattern 2: Shortened range like 21_22 or 22-23 (assume 20xx)
    m2 = re.search(r'\b(\d{2})[\-–_](\d{2})\b', base)
    if m2:
        year1 = int(m2.group(1))
        year2 = int(m2.group(2))
        # Assume 21st century
        # The second year is the ending year
        return 2000 + year2
    
    # Pattern 3: Single year like 2019, 2022, 2023-2024
    years = re.findall(r'(20\d{2})', base)
    if years:
        # Return the last year found (often the end year)
        return int(years[-1])
    
    return None


def find_percent_column(cols: List[str]) -> Optional[str]:
    """Find the column containing percent data."""
    # Exact match first
    if 'Percent' in cols:
        return 'Percent'
    
    # Case-insensitive search
    for c in cols:
        if 'percent' in c.lower():
            return c
    
    return None


def find_count_columns(cols: List[str]) -> Dict:
    """
    Find columns containing count data.
    
    Returns dict with 'count' and 'total' keys.
    """
    result: Dict[str, Optional[str]] = {'count': None, 'total': None}
    
    # Exact matches first
    if 'Count' in cols:
        result['count'] = 'Count'
    if 'Total Count' in cols:
        result['total'] = 'Total Count'
    
    # Soft search if exact match not found
    if result['count'] is None:
        for c in cols:
            cl = c.lower()
            if 'count' in cl and 'total' not in cl:
                result['count'] = c
                break
    
    if result['total'] is None:
        for c in cols:
            cl = c.lower()
            if 'total' in cl and 'count' in cl:
                result['total'] = c
                break
    
    return result


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names using the standard mapping.
    
    Applies column renames from config.COLUMN_MAPPINGS.
    """
    # Apply column mappings
    df = df.rename(columns=COLUMN_MAPPINGS)
    
    # Ensure essential columns exist
    for col in ['lea_name', 'Student group', 'Subgroup Value']:
        if col not in df.columns:
            df[col] = pd.NA
    
    return df


def filter_aggregation_level(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out District-level aggregation, keep School-level."""
    if 'Aggregation Level' in df.columns:
        before_count = len(df)
        df = df[df['Aggregation Level'].fillna('').str.upper() != 'DISTRICT']
        after_count = len(df)
        
        if before_count > after_count:
            logger.debug(f"Filtered out {before_count - after_count} district-level rows")
    
    return df


def filter_metric(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to keep only the specified metric (e.g., 'Meeting or Exceeding')."""
    if 'Metric' in df.columns:
        before_count = len(df)
        df = df[df['Metric'].astype(str).str.contains(METRIC_FILTER, case=False, na=False)]
        after_count = len(df)
        
        if before_count > after_count:
            logger.debug(f"Filtered to '{METRIC_FILTER}' metric: {after_count} rows (removed {before_count - after_count})")
    
    return df


def to_common_schema(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Convert a raw DataFrame to the common schema.
    
    Args:
        df: Raw DataFrame from input file
        year: School year (ending year)
    
    Returns:
        Normalized DataFrame with standard columns
    """
    # Normalize columns
    df = normalize_columns(df)
    
    # Filter to school level and desired metric
    df = filter_aggregation_level(df)
    df = filter_metric(df)
    
    # Add year
    df['year'] = int(year)
    
    # Parse percent, count, and total count columns
    cols = list(df.columns)
    
    pct_col = find_percent_column(cols)
    if pct_col is not None:
        df['percent_value'] = df[pct_col].apply(parse_percent)
    else:
        df['percent_value'] = pd.NA
        logger.warning(f"No percent column found in data for year {year}")
    
    cnt_cols = find_count_columns(cols)
    if cnt_cols['count'] is not None:
        df['count_value'] = pd.to_numeric(df[cnt_cols['count']], errors='coerce')
    else:
        df['count_value'] = pd.NA
    
    if cnt_cols['total'] is not None:
        df['total_count_value'] = pd.to_numeric(df[cnt_cols['total']], errors='coerce')
    else:
        df['total_count_value'] = pd.NA
    
    # Standardize subgroup values
    df['subgroup_value_std'] = df['Subgroup Value'].apply(standardize_subgroup_value)
    
    # Ensure all expected columns exist (at least as placeholders)
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    
    return df


def should_skip_sheet(sheet_name: str) -> bool:
    """Determine if an Excel sheet should be skipped based on its name."""
    sheet_lower = sheet_name.lower()
    
    for pattern in SKIP_SHEET_PATTERNS:
        if pattern in sheet_lower:
            return True
    
    return False


def read_csv_file(file_path: str, stats: DataLoadStats) -> Optional[pd.DataFrame]:
    """
    Read and process a CSV file.
    
    Args:
        file_path: Path to CSV file
        stats: DataLoadStats object to track loading
    
    Returns:
        Processed DataFrame or None if failed
    """
    filename = os.path.basename(file_path)
    
    # Extract year from filename
    year = extract_year_from_filename(file_path)
    if year is None:
        stats.add_file_skip(filename, "Could not extract year from filename")
        return None
    
    # Try to read CSV
    try:
        df = pd.read_csv(file_path, dtype=str)
    except Exception as e:
        stats.add_file_error(filename, f"Failed to read CSV: {str(e)}")
        return None
    
    # Validate
    is_valid, error = validate_dataframe(df, filename, REQUIRED_SHEET_COLUMNS)
    if not is_valid:
        stats.add_file_skip(filename, error or "Validation failed")
        return None
    
    # Process to common schema
    try:
        df_processed = to_common_schema(df, year)
        if df_processed.empty:
            stats.add_file_skip(filename, "No data after filtering")
            return None
        
        stats.add_file_success(filename, year, len(df_processed))
        return df_processed
    
    except Exception as e:
        stats.add_file_error(filename, f"Failed to process: {str(e)}")
        return None


def read_excel_file(file_path: str, stats: DataLoadStats) -> Optional[pd.DataFrame]:
    """
    Read and process an Excel file (possibly with multiple sheets).
    
    Args:
        file_path: Path to Excel file
        stats: DataLoadStats object to track loading
    
    Returns:
        Processed DataFrame (combined from all valid sheets) or None if failed
    """
    filename = os.path.basename(file_path)
    
    # Extract year from filename
    year = extract_year_from_filename(file_path)
    if year is None:
        stats.add_file_skip(filename, "Could not extract year from filename")
        return None
    
    # Try to read all sheets
    try:
        sheets = pd.read_excel(file_path, sheet_name=None, dtype=str)
    except Exception as e:
        stats.add_file_error(filename, f"Failed to read Excel: {str(e)}")
        return None
    
    # Process each sheet
    valid_dfs = []
    sheet_count = 0
    
    for sheet_name, sdf in sheets.items():
        # Skip documentation/metadata sheets
        if should_skip_sheet(sheet_name):
            logger.debug(f"  Skipping sheet '{sheet_name}' (documentation/metadata)")
            continue
        
        # Validate sheet has required columns
        cols = list(sdf.columns)
        if not any(c in cols for c in REQUIRED_SHEET_COLUMNS):
            logger.debug(f"  Skipping sheet '{sheet_name}' (missing required columns)")
            continue
        
        # Process sheet
        try:
            sdf_processed = to_common_schema(sdf, year)
            if not sdf_processed.empty:
                valid_dfs.append(sdf_processed)
                sheet_count += 1
                logger.debug(f"  Loaded sheet '{sheet_name}': {len(sdf_processed)} rows")
        except Exception as e:
            logger.warning(f"  Error processing sheet '{sheet_name}': {str(e)}")
            continue
    
    # Combine all valid sheets
    if not valid_dfs:
        stats.add_file_skip(filename, "No valid sheets found")
        return None
    
    df_combined = pd.concat(valid_dfs, ignore_index=True, sort=False)
    stats.add_file_success(filename, year, len(df_combined), sheets=sheet_count)
    
    return df_combined


def load_all_input_files(input_path: str, selected_schools: Optional[List[str]] = None) -> Tuple[pd.DataFrame, DataLoadStats]:
    """
    Load and process all input files from the input directory.
    
    Args:
        input_path: Path to input data directory
        selected_schools: Optional list of school names to filter to
    
    Returns:
        Tuple of (combined DataFrame, DataLoadStats object)
    """
    stats = DataLoadStats()
    frames: List[pd.DataFrame] = []
    
    logger.info(f"Loading data from: {input_path}")
    logger.info("=" * 60)
    
    # Get all files
    try:
        files = sorted(os.listdir(input_path))
    except Exception as e:
        logger.error(f"Could not read input directory: {e}")
        return pd.DataFrame(), stats
    
    # Process each file
    for name in files:
        fp = os.path.join(input_path, name)
        
        # Skip directories
        if not os.path.isfile(fp):
            continue
        
        # Skip temp files
        if name.startswith('~$'):
            continue
        
        # Process based on file type
        lower = name.lower()
        df = None
        
        if lower.endswith('.csv'):
            df = read_csv_file(fp, stats)
        elif lower.endswith('.xlsx') or lower.endswith('.xls'):
            df = read_excel_file(fp, stats)
        else:
            stats.add_file_skip(name, "Unsupported file type")
            continue
        
        # Add to frames if successful
        if df is not None and not df.empty:
            frames.append(df)
    
    # Combine all frames
    if not frames:
        logger.warning("No data loaded from any files!")
        return pd.DataFrame(), stats
    
    all_df = pd.concat(frames, ignore_index=True, sort=False)
    logger.info(f"\nCombined data: {len(all_df):,} total rows")
    
    # Optional: filter to selected schools
    if selected_schools:
        before_count = len(all_df)
        all_df = all_df[all_df['School Name'].isin(selected_schools)]
        logger.info(f"Filtered to {len(selected_schools)} selected schools: {len(all_df):,} rows (removed {before_count - len(all_df):,})")
    
    return all_df, stats
