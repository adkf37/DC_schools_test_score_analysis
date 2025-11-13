"""
Configuration constants for DC school test score analysis.
"""
from typing import List

# Directory paths (these will be set at runtime)
CURRENT_PATH = None
INPUT_PATH = None
OUTPUT_PATH = None

# School filtering
# Leave empty to process all schools, or add specific school names to filter
SELECTED_SCHOOLS: List[str] = []
# Example: ['Stuart-Hobson Middle School (Capitol Hill Cluster)', 'BASIS DC PCS']

# Subgroup filtering for the filtered_data.csv export
SUBGROUP_VALUES_FOR_FILTER: List[str] = ['White', 'White/Caucasian']

# Expected column names in standardized format
EXPECTED_COLS = [
    'Aggregation Level', 'LEA Code', 'lea_name', 'School Code', 'School Name',
    'Assessment Name', 'Subject', 'Student group', 'Subgroup Value',
    'Tested Grade/Subject', 'Grade of Enrollment', 'Count', 'Total Count', 'Percent'
]

# Column name mappings for normalization
# (kept for backwards compatibility with older sheets)
COLUMN_MAPPINGS = {
    'LEA Name': 'lea_name',
    'lea Name': 'lea_name',
    'Student Group': 'Student group',
    'Student group': 'Student group',
    'Student Group Value': 'Subgroup Value',
    'Student group Value': 'Subgroup Value',
}

# Additional aliases used to align changing column headers across releases
COLUMN_ALIASES = {
    'lea_name': ['LEA Name', 'lea_name', 'Lea Name'],
    'Student group': ['Student group', 'Student Group', 'student group'],
    'Subgroup Value': [
        'Subgroup Value',
        'Subgroup value',
        'Student Group Value',
        'Student group value',
        'Student Group Value ',
    ],
    'Tested Grade/Subject': [
        'Tested Grade/Subject',
        'Tested Grade Subject',
        'Tested Grade / Subject',
        'Tested Grade or Subject',
    ],
    'Grade of Enrollment': [
        'Grade of Enrollment',
        'Grade Of Enrollment',
    ],
    'Aggregation Level': ['Aggregation Level'],
    'LEA Code': ['LEA Code'],
    'School Code': ['School Code'],
    'School Name': ['School Name'],
    'Assessment Name': ['Assessment Name'],
    'Subject': ['Subject'],
    'Count': ['Count'],
    'Total Count': ['Total Count'],
    'Percent': ['Percent'],
    'Metric': ['Metric'],
    'Enrolled Grade or Course': ['Enrolled Grade or Course', 'Enrolled Grade/Course'],
}

# Subgroup value standardization mapping
SUBGROUP_STANDARDIZATION = {
    'white/caucasian': 'White',
    'white': 'White',
    'black/african american': 'Black/African American',
    'hispanic/latino of any race': 'Hispanic/Latino',
    'hispanic/latino': 'Hispanic/Latino',
    'two or more races': 'Two or More Races',
    'american indian/alaska native': 'American Indian/Alaska Native',
    'native hawaiian/other pacific islander': 'Native Hawaiian/Pacific Islander',
    'asian': 'Asian',
    'all students': 'All Students',
    'economically disadvantaged': 'Economically Disadvantaged',
    'students with disabilities': 'Students with Disabilities',
    'english learners': 'English Learners',
}

# Metric filter - only keep rows with this metric if a Metric column exists
METRIC_FILTER = 'Meeting or Exceeding'

# Excel sheet names to skip (documentation/metadata sheets)
SKIP_SHEET_PATTERNS = [
    'data notes',
    'business rules',
    'data dictionary',
    'metadata',
    'readme',
    'instructions',
]

# Columns that must be present to consider a sheet valid
REQUIRED_SHEET_COLUMNS = ['School Name', 'School Code', 'Aggregation Level']

# Values that indicate suppressed/missing data
SUPPRESSED_VALUES = ['DS', 'N<10', '<5%', '<=10%', 'N/A', 'NA']

# Index columns for growth calculations
GROWTH_INDEX_COLS = [
    'LEA Code', 'lea_name', 'School Code', 'School Name',
    'Assessment Name', 'Subject', 'Student group', 'subgroup_value_std',
    'Tested Grade/Subject', 'Grade of Enrollment',
]
