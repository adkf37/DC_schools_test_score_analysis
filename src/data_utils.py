"""
Data validation and logging utilities for DC school test score analysis.
"""
import logging
from typing import Dict, List, Optional
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class DataLoadStats:
    """Track statistics about data loading process."""
    
    def __init__(self):
        self.files_attempted = 0
        self.files_loaded = 0
        self.files_skipped = 0
        self.total_rows = 0
        self.rows_by_year: Dict[int, int] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.files_details: List[Dict] = []
    
    def add_file_success(self, filename: str, year: int, rows: int, sheets: Optional[int] = None):
        """Record a successfully loaded file."""
        self.files_attempted += 1
        self.files_loaded += 1
        self.total_rows += rows
        self.rows_by_year[year] = self.rows_by_year.get(year, 0) + rows
        
        detail = {
            'filename': filename,
            'status': 'success',
            'year': year,
            'rows': rows,
        }
        if sheets is not None:
            detail['sheets'] = sheets
        self.files_details.append(detail)
        
        logger.info(f"✓ Loaded {filename} (Year: {year}, Rows: {rows})")
    
    def add_file_skip(self, filename: str, reason: str):
        """Record a skipped file."""
        self.files_attempted += 1
        self.files_skipped += 1
        self.warnings.append(f"{filename}: {reason}")
        self.files_details.append({
            'filename': filename,
            'status': 'skipped',
            'reason': reason,
        })
        logger.warning(f"⊘ Skipped {filename} - {reason}")
    
    def add_file_error(self, filename: str, error: str):
        """Record a file that failed to load."""
        self.files_attempted += 1
        self.files_skipped += 1
        self.errors.append(f"{filename}: {error}")
        self.files_details.append({
            'filename': filename,
            'status': 'error',
            'error': error,
        })
        logger.error(f"✗ Error loading {filename} - {error}")
    
    def add_warning(self, message: str):
        """Add a general warning."""
        self.warnings.append(message)
        logger.warning(message)
    
    def print_summary(self):
        """Print a summary of the data loading process."""
        logger.info("=" * 60)
        logger.info("DATA LOADING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Files attempted: {self.files_attempted}")
        logger.info(f"Files loaded: {self.files_loaded}")
        logger.info(f"Files skipped/failed: {self.files_skipped}")
        logger.info(f"Total rows loaded: {self.total_rows}")
        
        if self.rows_by_year:
            logger.info("\nRows by year:")
            for year in sorted(self.rows_by_year.keys()):
                logger.info(f"  {year}: {self.rows_by_year[year]:,} rows")
        
        if self.errors:
            logger.info(f"\n{len(self.errors)} errors occurred:")
            for error in self.errors[:5]:  # Show first 5
                logger.info(f"  - {error}")
            if len(self.errors) > 5:
                logger.info(f"  ... and {len(self.errors) - 5} more")
        
        if self.warnings:
            logger.info(f"\n{len(self.warnings)} warnings:")
            for warning in self.warnings[:5]:  # Show first 5
                logger.info(f"  - {warning}")
            if len(self.warnings) > 5:
                logger.info(f"  ... and {len(self.warnings) - 5} more")
        
        logger.info("=" * 60)


def validate_dataframe(df: pd.DataFrame, filename: str, required_cols: List[str]) -> tuple[bool, Optional[str]]:
    """
    Validate that a DataFrame has the minimum required structure.
    
    Returns:
        (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty"
    
    # Check for at least one required column
    has_required = any(col in df.columns for col in required_cols)
    if not has_required:
        return False, f"Missing required columns. Expected one of: {required_cols}"
    
    return True, None


def check_data_quality(df: pd.DataFrame) -> Dict:
    """
    Analyze data quality of a DataFrame.
    
    Returns dictionary with quality metrics.
    """
    if df.empty:
        return {'total_rows': 0, 'issues': ['DataFrame is empty']}
    
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_by_column': {},
        'issues': [],
    }
    
    # Check for missing data
    for col in df.columns:
        missing = df[col].isna().sum()
        if missing > 0:
            pct = (missing / len(df)) * 100
            stats['missing_by_column'][col] = {
                'count': int(missing),
                'percent': round(pct, 2)
            }
    
    # Check for key columns
    key_cols = ['School Name', 'Subject', 'year']
    for col in key_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            if missing > len(df) * 0.5:  # More than 50% missing
                stats['issues'].append(f"Column '{col}' has {missing} missing values ({missing/len(df)*100:.1f}%)")
    
    # Check if percent_value is mostly missing
    if 'percent_value' in df.columns:
        missing = df['percent_value'].isna().sum()
        if missing > len(df) * 0.8:
            stats['issues'].append(f"Most percent values are missing ({missing/len(df)*100:.1f}%)")
    
    return stats


def log_processing_step(step_name: str, details: str = ""):
    """Log a processing step."""
    if details:
        logger.info(f"→ {step_name}: {details}")
    else:
        logger.info(f"→ {step_name}")


def create_processing_report(df: pd.DataFrame, stats: DataLoadStats, output_path: str):
    """
    Create a detailed processing report.
    
    Args:
        df: The processed DataFrame
        stats: DataLoadStats object with loading statistics
        output_path: Path to save the report
    """
    report_lines = []
    report_lines.append("DC SCHOOL TEST SCORE ANALYSIS - PROCESSING REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"\nGenerated: {pd.Timestamp.now()}")
    report_lines.append(f"\n{'FILES PROCESSED':-^70}")
    report_lines.append(f"Total files attempted: {stats.files_attempted}")
    report_lines.append(f"Successfully loaded: {stats.files_loaded}")
    report_lines.append(f"Skipped/Failed: {stats.files_skipped}")
    
    report_lines.append(f"\n{'FILE DETAILS':-^70}")
    for detail in stats.files_details:
        if detail['status'] == 'success':
            report_lines.append(f"✓ {detail['filename']} → Year {detail['year']}, {detail['rows']:,} rows")
        elif detail['status'] == 'skipped':
            report_lines.append(f"⊘ {detail['filename']} → {detail.get('reason', 'Unknown')}")
        else:
            report_lines.append(f"✗ {detail['filename']} → {detail.get('error', 'Unknown error')}")
    
    if not df.empty:
        report_lines.append(f"\n{'PROCESSED DATA SUMMARY':-^70}")
        report_lines.append(f"Total rows: {len(df):,}")
        report_lines.append(f"Total columns: {len(df.columns)}")
        
        if 'year' in df.columns:
            years = sorted([y for y in df['year'].dropna().unique()])
            report_lines.append(f"Years covered: {min(years) if years else 'N/A'} - {max(years) if years else 'N/A'}")
            report_lines.append(f"Year breakdown:")
            for year in years:
                count = (df['year'] == year).sum()
                report_lines.append(f"  {year}: {count:,} rows")
        
        if 'School Name' in df.columns:
            unique_schools = df['School Name'].nunique()
            report_lines.append(f"\nUnique schools: {unique_schools}")
        
        if 'Subject' in df.columns:
            subjects = sorted(df['Subject'].dropna().unique())
            report_lines.append(f"Subjects: {', '.join(str(s) for s in subjects[:10])}")
            if len(subjects) > 10:
                report_lines.append(f"  ... and {len(subjects) - 10} more")
        
        if 'subgroup_value_std' in df.columns:
            subgroups = sorted(df['subgroup_value_std'].dropna().unique())
            report_lines.append(f"Subgroups: {', '.join(str(s) for s in subgroups)}")
    
    if stats.errors:
        report_lines.append(f"\n{'ERRORS':-^70}")
        for error in stats.errors:
            report_lines.append(f"  - {error}")
    
    if stats.warnings:
        report_lines.append(f"\n{'WARNINGS':-^70}")
        for warning in stats.warnings:
            report_lines.append(f"  - {warning}")
    
    report_lines.append("\n" + "=" * 70)
    
    # Save report
    report_path = f"{output_path}/processing_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    logger.info(f"Processing report saved to: {report_path}")
