"""
Load and clean DC school test score data from 4 specific XLSX files.
Each file has a different schema that needs to be normalized.

Key normalizations:
- Column names standardized across schema versions
- Grade names normalized (e.g., "Grade 6-All" → "Grade 6", "06" → "Grade 6")
- Duplicate rows removed
- Assessment name standardized (PARCC / DCCAPE → main assessment)
"""
import os
import re
import pandas as pd
from typing import Dict, List

# Define paths
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
INPUT_PATH = os.path.abspath(f"{CURRENT_PATH}/../input_data")
OUTPUT_PATH = os.path.abspath(f"{CURRENT_PATH}/../output_data")

# File configurations: (filename, sheet_name, year)
FILE_CONFIGS = [
    {
        'filename': '2021-22 School Level PARCC and MSAA Data.xlsx',
        'sheet': 'prof',
        'year': 2022,
        'schema_version': '21-22'
    },
    {
        'filename': '2022-23 School Level PARCC and MSAA Data_9_5.xlsx',
        'sheet': 'Meeting, Exceeding',
        'year': 2023,
        'schema_version': '22-23'
    },
    {
        'filename': '2023-24 School Level DCCAPE and MSAA Data 1.15.2025.xlsx',
        'sheet': 'Meeting, Exceeding',
        'year': 2024,
        'schema_version': '23-24'
    },
    {
        'filename': '2024-25 Public File School Level DCCAPE and MSAA Data 1.xlsx',
        'sheet': 'Meeting, Exceeding',
        'year': 2025,
        'schema_version': '24-25'
    }
]

# Column mappings for each schema version to standard names
COLUMN_MAPPINGS = {
    '21-22': {
        'Aggregation Level': 'Aggregation Level',
        'LEA Code': 'LEA Code',
        'lea_name': 'LEA Name',
        'School Code': 'School Code',
        'School Name': 'School Name',
        'Assessment Name': 'Assessment Name',
        'Subject': 'Subject',
        'Student group': 'Student Group',
        'Subgroup Value': 'Student Group Value',
        'Tested Grade/Subject': 'Tested Grade/Subject',
        'Grade of Enrollment': 'Grade of Enrollment',
        'Count': 'Count',
        'Total Count': 'Total Count',
        'Percent': 'Percent'
    },
    '22-23': {
        'Aggregation Level': 'Aggregation Level',
        'LEA Code': 'LEA Code',
        'LEA Name': 'LEA Name',
        'School Code': 'School Code',
        'School Name': 'School Name',
        'Assessment Name': 'Assessment Name',
        'Subject': 'Subject',
        'Student Group': 'Student Group',
        'Student Group Value': 'Student Group Value',
        'Tested Grade/Subject': 'Tested Grade/Subject',
        'Grade of Enrollment': 'Grade of Enrollment',
        'Count': 'Count',
        'Total Count': 'Total Count',
        'Percent': 'Percent'
        # Drop: Metric, School Framework
    },
    '23-24': {
        'Aggregation Level': 'Aggregation Level',
        'LEA Code': 'LEA Code',
        'LEA Name': 'LEA Name',
        'School Code': 'School Code',
        'School Name': 'School Name',
        'Assessment Name': 'Assessment Name',
        'Subject': 'Subject',
        'Student Group': 'Student Group',
        'Student Group Value': 'Student Group Value',
        'Tested Grade/Subject': 'Tested Grade/Subject',
        'Grade of Enrollment': 'Grade of Enrollment',
        'Count': 'Count',
        'Total Count': 'Total Count',
        'Percent': 'Percent'
        # Drop: Metric, School Framework
    },
    '24-25': {
        'Aggregation Level': 'Aggregation Level',
        'LEA Code': 'LEA Code',
        'lea_name': 'LEA Name',
        'School Code': 'School Code',
        'School Name': 'School Name',
        'Assessment Name': 'Assessment Name',
        'Subject': 'Subject',
        'Student Group': 'Student Group',
        'Student Group Value': 'Student Group Value',
        'Enrolled Grade or Course': 'Enrolled Grade or Course',  # Special case
        'Count': 'Count',
        'Total Count': 'Total Count',
        'Percent': 'Percent'
        # Drop: Metric
    }
}


def load_file(config: Dict) -> pd.DataFrame:
    """
    Load a single file and normalize its schema.
    
    Args:
        config: Dictionary with filename, sheet, year, and schema_version
    
    Returns:
        Normalized DataFrame
    """
    filepath = os.path.join(INPUT_PATH, config['filename'])
    sheet = config['sheet']
    year = config['year']
    schema_version = config['schema_version']
    
    print(f"\nLoading {config['filename']}...")
    print(f"  Sheet: {sheet}")
    print(f"  Year: {year}")
    
    # Read the specific sheet (this may take a moment for large files)
    print(f"  Reading sheet... (large files may take 1-2 minutes)")
    try:
        # Use pyarrow engine if available, otherwise openpyxl
        import openpyxl
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        ws = wb[sheet]
        
        # Convert to list of lists
        data = []
        for row in ws.iter_rows(values_only=True):
            data.append(row)
        
        wb.close()
        
        # Create DataFrame
        if data:
            df = pd.DataFrame(data[1:], columns=data[0])  # First row is headers
            # Convert all to strings
            df = df.astype(str)
            print(f"  ✓ Loaded {len(df):,} rows")
        else:
            print(f"  ERROR: Sheet is empty")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"  ERROR: Could not read file - {e}")
        return pd.DataFrame()
    
    # Get the column mapping for this schema
    mapping = COLUMN_MAPPINGS[schema_version]
    
    # Keep only the columns we want and rename them
    cols_to_keep = {old: new for old, new in mapping.items() if old in df.columns}
    df = df[list(cols_to_keep.keys())].copy()
    df = df.rename(columns=cols_to_keep)
    
    # Special handling for 24-25 data
    if schema_version == '24-25':
        # Copy 'Enrolled Grade or Course' into both the grade and subject fields
        if 'Enrolled Grade or Course' in df.columns:
            df['Tested Grade/Subject'] = df['Enrolled Grade or Course']
            df['Grade of Enrollment'] = df['Enrolled Grade or Course']
            print(f"  Copied 'Enrolled Grade or Course' to grade/subject fields")
    
    # Add year column
    df['Year'] = year
    
    # Ensure all standard columns exist
    standard_cols = [
        'Aggregation Level', 'LEA Code', 'LEA Name', 'School Code', 'School Name',
        'Assessment Name', 'Subject', 'Student Group', 'Student Group Value',
        'Tested Grade/Subject', 'Grade of Enrollment', 'Count', 'Total Count', 'Percent'
    ]
    
    for col in standard_cols:
        if col not in df.columns:
            df[col] = None
    
    # Reorder columns
    df = df[standard_cols + ['Year']]
    
    print(f"  Normalized rows: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    
    return df


def normalize_grade(val: str) -> str:
    """
    Normalize grade values to a consistent format.
    
    Examples:
        'Grade 6-All' → 'Grade 6'
        'Grade 7-All' → 'Grade 7'
        '06' → 'Grade 6'
        'Grade 8' → 'Grade 8'
        'HS-Algebra I' → 'Algebra I'
        'All' → 'All'
    """
    if pd.isna(val) or str(val).strip() == '':
        return val
    s = str(val).strip()
    
    # Remove '-All' suffix (appears in 2025 data)
    s = re.sub(r'-All$', '', s)
    
    # Remove 'HS-' prefix (appears in 2025 data) 
    s = re.sub(r'^HS-', '', s)
    
    # Convert bare 2-digit grade numbers to 'Grade N' format
    m = re.match(r'^(\d{1,2})$', s)
    if m:
        grade_num = int(m.group(1))
        s = f'Grade {grade_num}'
    
    return s


def extract_grade_number(grade_str: str) -> int:
    """
    Extract a numeric grade level from a grade string.
    
    Returns -1 if not a numeric grade (e.g., 'All', 'Algebra I').
    
    Examples:
        'Grade 6' → 6
        'Grade 8' → 8
        'Grade 11' → 11
        'All' → -1
        'Algebra I' → -1
    """
    if pd.isna(grade_str):
        return -1
    m = re.match(r'Grade\s+(\d+)', str(grade_str).strip())
    if m:
        return int(m.group(1))
    return -1


def main():
    """Load all 4 files and combine into a single dataset."""
    
    print("=" * 70)
    print("DC SCHOOLS TEST SCORE DATA LOADER")
    print("=" * 70)
    
    # Create output directory if needed
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    # Load each file
    all_dfs = []
    for config in FILE_CONFIGS:
        df = load_file(config)
        if not df.empty:
            all_dfs.append(df)
    
    # Combine all dataframes
    if not all_dfs:
        print("\nERROR: No data loaded from any files!")
        print("\nTIP: If the above files are not available, use the alternative loader:")
        print("     python src/load_wide_format_data.py")
        print("  This loader reads the wide-format OSSE files from:")
        print("  input_data/School and Demographic Group Aggregation/")
        return
    
    print("\n" + "=" * 70)
    print("COMBINING DATA")
    print("=" * 70)
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    print(f"\nCombined dataset (before cleanup):")
    print(f"  Total rows: {len(combined_df):,}")
    
    # ── Grade normalization ──────────────────────────────────────────────
    print("\nNormalizing grade names...")
    combined_df['Tested Grade/Subject'] = combined_df['Tested Grade/Subject'].apply(normalize_grade)
    combined_df['Grade of Enrollment'] = combined_df['Grade of Enrollment'].apply(normalize_grade)
    
    # Add numeric grade column for cohort tracking
    combined_df['Grade Number'] = combined_df['Tested Grade/Subject'].apply(extract_grade_number)
    
    # ── Deduplicate rows ─────────────────────────────────────────────────
    # Some year/school/grade/subject/group combos appear with both a specific
    # assessment (PARCC, DCCAPE) AND an aggregated "All" assessment row that
    # has identical values. Keep only the specific assessment rows when duplicates
    # exist; fall back to "All" when there is no specific assessment row.
    dedup_keys = [
        'Year', 'School Code', 'School Name', 'Subject',
        'Tested Grade/Subject', 'Grade of Enrollment',
        'Student Group', 'Student Group Value'
    ]
    
    before_dedup = len(combined_df)
    # Sort so specific assessments come before "All"
    combined_df['_assess_sort'] = combined_df['Assessment Name'].apply(
        lambda x: 1 if str(x).strip() == 'All' else 0
    )
    combined_df = combined_df.sort_values(dedup_keys + ['_assess_sort'])
    combined_df = combined_df.drop_duplicates(subset=dedup_keys, keep='first')
    combined_df = combined_df.drop(columns=['_assess_sort'])
    after_dedup = len(combined_df)
    print(f"  Deduplicated: {before_dedup:,} → {after_dedup:,} rows (removed {before_dedup - after_dedup:,} duplicates)")
    
    print(f"\nCombined dataset:")
    print(f"  Total rows: {len(combined_df):,}")
    print(f"  Total columns: {len(combined_df.columns)}")
    print(f"  Years: {sorted(combined_df['Year'].unique())}")
    
    # Show breakdown by year
    print(f"\nRows by year:")
    year_counts = combined_df['Year'].value_counts().sort_index()
    for year, count in year_counts.items():
        print(f"  {year}: {count:,} rows")
    
    # Show unique schools
    unique_schools = combined_df['School Name'].nunique()
    print(f"\nUnique schools: {unique_schools}")
    
    # Show unique subjects
    unique_subjects = combined_df['Subject'].dropna().unique()
    print(f"Unique subjects: {sorted(unique_subjects)}")
    
    # Show grade breakdown
    grade_nums = combined_df[combined_df['Grade Number'] >= 0]['Grade Number'].unique()
    print(f"Numeric grades: {sorted(grade_nums)}")
    print(f"Non-numeric grade values: {sorted(combined_df[combined_df['Grade Number'] < 0]['Tested Grade/Subject'].dropna().unique())}")
    
    # Show sample of data
    print(f"\nSample of first few rows:")
    print(combined_df.head())
    
    # Save to CSV
    output_file = os.path.join(OUTPUT_PATH, 'combined_all_years.csv')
    combined_df.to_csv(output_file, index=False)
    print(f"\n✓ Saved combined data to: {output_file}")
    
    # Also show some data quality info
    print(f"\n" + "=" * 70)
    print("DATA QUALITY SUMMARY")
    print("=" * 70)
    
    for col in ['School Name', 'Subject', 'Student Group Value', 'Percent']:
        missing = combined_df[col].isna().sum()
        pct = (missing / len(combined_df)) * 100
        print(f"{col:30s}: {missing:,} missing ({pct:.1f}%)")
    
    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
