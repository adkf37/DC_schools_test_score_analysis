"""
Dash app for exploring DC school test scores.

Reads from the pre-cleaned combined_all_years.csv and cohort growth outputs.
Provides:
  - Time series & bar charts of school performance
  - Cohort growth analysis (Grade N → Grade N+1)
  - Map view (when school_locations.csv is available)
"""
import os
import re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from typing import List, Optional

# Paths
APP_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, '..'))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output_data')
INPUT_DIR = os.path.join(PROJECT_ROOT, 'input_data')
COMBINED_DATA_FILE = os.path.join(OUTPUT_DIR, 'combined_all_years.csv')


def parse_percent(series: pd.Series) -> pd.Series:
    """Convert percent values to numeric, handling suppressed data."""
    def _parse_value(val):
        if pd.isna(val):
            return np.nan
        s = str(val).strip().upper()
        if s in ['DS', 'N<10', '<5%', '<=10%', 'N/A', 'NA', '']:
            return np.nan
        if any(s.startswith(m) for m in ['<', '<=', '>', '>=']):
            return np.nan
        s = s.replace('%', '').strip()
        try:
            return float(s)
        except:
            return np.nan
    return series.apply(_parse_value)


def load_data() -> pd.DataFrame:
    """Load and prepare the combined dataset."""
    if not os.path.exists(COMBINED_DATA_FILE):
        print(f"ERROR: {COMBINED_DATA_FILE} not found!")
        print("Run load_clean_data.py first to create the combined dataset.")
        return pd.DataFrame()
    
    print(f"Loading data from: {COMBINED_DATA_FILE}")
    df = pd.read_csv(COMBINED_DATA_FILE, dtype=str)
    
    # Parse numeric columns
    df['percent_value'] = parse_percent(df['Percent'])
    df['year'] = pd.to_numeric(df['Year'], errors='coerce')
    
    # Rename for consistency
    df = df.rename(columns={'Student Group Value': 'subgroup_value_std'})
    
    # Filter to school level
    df = df[df['Aggregation Level'].str.upper() == 'SCHOOL']
    
    print(f"Loaded {len(df):,} rows")
    print(f"Years: {sorted(df['year'].dropna().unique())}")
    print(f"Schools: {df['School Name'].nunique()}")
    
    return df


def try_load_school_locations() -> Optional[pd.DataFrame]:
    """Try to load school location data for mapping."""
    candidates = [
        'school_locations.csv',
        'schools_geocoded.csv',
        'dc_school_locations.csv',
    ]
    for name in candidates:
        fp = os.path.join(INPUT_DIR, name)
        if os.path.isfile(fp):
            try:
                df = pd.read_csv(fp)
                if all(c in df.columns for c in ['School Name', 'Latitude', 'Longitude']):
                    return df
            except Exception:
                continue
    return None


# Load data
multi_year = load_data()
locations_df = try_load_school_locations()

# Load cohort growth data if available
COHORT_DETAIL_FILE = os.path.join(OUTPUT_DIR, 'cohort_growth_detail.csv')
COHORT_SUMMARY_FILE = os.path.join(OUTPUT_DIR, 'cohort_growth_summary.csv')
EQUITY_SUMMARY_FILE = os.path.join(OUTPUT_DIR, 'equity_gap_summary.csv')
PROFICIENCY_TRENDS_FILE = os.path.join(OUTPUT_DIR, 'proficiency_trends.csv')
GEO_EQUITY_FILE = os.path.join(OUTPUT_DIR, 'geographic_equity_by_quadrant.csv')
YOY_DETAIL_FILE = os.path.join(OUTPUT_DIR, 'yoy_growth_detail.csv')
COVID_RECOVERY_FILE = os.path.join(OUTPUT_DIR, 'covid_recovery_summary.csv')
TRAJECTORY_FILE = os.path.join(OUTPUT_DIR, 'school_trajectory_classification.csv')
SCHOOL_TYPE_PROFICIENCY_FILE = os.path.join(OUTPUT_DIR, 'school_type_proficiency.csv')
SCHOOL_TYPE_BY_SCHOOL_FILE = os.path.join(OUTPUT_DIR, 'school_type_by_school.csv')
GRADE_LEVEL_PROFICIENCY_FILE = os.path.join(OUTPUT_DIR, 'grade_level_proficiency.csv')
SUBGROUP_PROFICIENCY_FILE = os.path.join(OUTPUT_DIR, 'subgroup_proficiency.csv')
SCHOOL_CONSISTENCY_FILE = os.path.join(OUTPUT_DIR, 'school_consistency.csv')
PERFORMANCE_INDEX_FILE = os.path.join(OUTPUT_DIR, 'school_performance_index.csv')
SCHOOL_SECTOR_PROFICIENCY_FILE = os.path.join(OUTPUT_DIR, 'school_sector_proficiency.csv')
SCHOOL_SECTOR_BY_SCHOOL_FILE = os.path.join(OUTPUT_DIR, 'school_sector_by_school.csv')
SCHOOL_NEEDS_INDEX_FILE = os.path.join(OUTPUT_DIR, 'school_needs_index.csv')
WARD_SUMMARY_FILE = os.path.join(OUTPUT_DIR, 'ward_summary.csv')
WARD_PROFICIENCY_FILE = os.path.join(OUTPUT_DIR, 'ward_proficiency.csv')
EQUITY_PROGRESS_CITYWIDE_FILE = os.path.join(OUTPUT_DIR, 'equity_progress_citywide.csv')
EQUITY_PROGRESS_SUMMARY_FILE = os.path.join(OUTPUT_DIR, 'equity_progress_summary.csv')

cohort_detail = pd.DataFrame()
cohort_summary = pd.DataFrame()
equity_summary = pd.DataFrame()
proficiency_trends = pd.DataFrame()
geo_equity = pd.DataFrame()
yoy_detail = pd.DataFrame()
covid_recovery = pd.DataFrame()
school_trajectories = pd.DataFrame()
school_type_proficiency = pd.DataFrame()
school_type_by_school = pd.DataFrame()
grade_level_proficiency = pd.DataFrame()
subgroup_proficiency = pd.DataFrame()
school_consistency = pd.DataFrame()
performance_index = pd.DataFrame()
school_sector_proficiency = pd.DataFrame()
school_sector_by_school = pd.DataFrame()
school_needs_index = pd.DataFrame()
ward_summary = pd.DataFrame()
ward_proficiency = pd.DataFrame()
equity_progress_citywide = pd.DataFrame()
equity_progress_summary_df = pd.DataFrame()
if os.path.isfile(COHORT_DETAIL_FILE):
    cohort_detail = pd.read_csv(COHORT_DETAIL_FILE)
    print(f"Loaded cohort detail: {len(cohort_detail):,} rows")
if os.path.isfile(COHORT_SUMMARY_FILE):
    cohort_summary = pd.read_csv(COHORT_SUMMARY_FILE)
    print(f"Loaded cohort summary: {len(cohort_summary):,} rows")
if os.path.isfile(EQUITY_SUMMARY_FILE):
    equity_summary = pd.read_csv(EQUITY_SUMMARY_FILE)
    print(f"Loaded equity gap summary: {len(equity_summary):,} rows")
if os.path.isfile(PROFICIENCY_TRENDS_FILE):
    proficiency_trends = pd.read_csv(PROFICIENCY_TRENDS_FILE)
    print(f"Loaded proficiency trends: {len(proficiency_trends):,} rows")
if os.path.isfile(GEO_EQUITY_FILE):
    geo_equity = pd.read_csv(GEO_EQUITY_FILE)
    print(f"Loaded geographic equity: {len(geo_equity):,} rows")
if os.path.isfile(YOY_DETAIL_FILE):
    yoy_detail = pd.read_csv(YOY_DETAIL_FILE)
    print(f"Loaded YoY growth detail: {len(yoy_detail):,} rows")
if os.path.isfile(COVID_RECOVERY_FILE):
    covid_recovery = pd.read_csv(COVID_RECOVERY_FILE)
    print(f"Loaded COVID recovery summary: {len(covid_recovery):,} rows")
if os.path.isfile(TRAJECTORY_FILE):
    school_trajectories = pd.read_csv(TRAJECTORY_FILE)
    print(f"Loaded school trajectory classification: {len(school_trajectories):,} rows")
if os.path.isfile(SCHOOL_TYPE_PROFICIENCY_FILE):
    school_type_proficiency = pd.read_csv(SCHOOL_TYPE_PROFICIENCY_FILE)
    print(f"Loaded school type proficiency: {len(school_type_proficiency):,} rows")
if os.path.isfile(SCHOOL_TYPE_BY_SCHOOL_FILE):
    school_type_by_school = pd.read_csv(SCHOOL_TYPE_BY_SCHOOL_FILE)
    print(f"Loaded school type classifications: {len(school_type_by_school):,} rows")
if os.path.isfile(GRADE_LEVEL_PROFICIENCY_FILE):
    grade_level_proficiency = pd.read_csv(GRADE_LEVEL_PROFICIENCY_FILE)
    print(f"Loaded grade-level proficiency: {len(grade_level_proficiency):,} rows")
if os.path.isfile(SUBGROUP_PROFICIENCY_FILE):
    subgroup_proficiency = pd.read_csv(SUBGROUP_PROFICIENCY_FILE)
    print(f"Loaded subgroup proficiency: {len(subgroup_proficiency):,} rows")
if os.path.isfile(SCHOOL_CONSISTENCY_FILE):
    school_consistency = pd.read_csv(SCHOOL_CONSISTENCY_FILE)
    print(f"Loaded school consistency: {len(school_consistency):,} rows")
if os.path.isfile(PERFORMANCE_INDEX_FILE):
    performance_index = pd.read_csv(PERFORMANCE_INDEX_FILE)
    print(f"Loaded school performance index: {len(performance_index):,} rows")
if os.path.isfile(SCHOOL_SECTOR_PROFICIENCY_FILE):
    school_sector_proficiency = pd.read_csv(SCHOOL_SECTOR_PROFICIENCY_FILE)
    print(f"Loaded school sector proficiency: {len(school_sector_proficiency):,} rows")
if os.path.isfile(SCHOOL_SECTOR_BY_SCHOOL_FILE):
    school_sector_by_school = pd.read_csv(SCHOOL_SECTOR_BY_SCHOOL_FILE)
    print(f"Loaded school sector classifications: {len(school_sector_by_school):,} rows")
if os.path.isfile(SCHOOL_NEEDS_INDEX_FILE):
    school_needs_index = pd.read_csv(SCHOOL_NEEDS_INDEX_FILE)
    print(f"Loaded school needs index: {len(school_needs_index):,} rows")
if os.path.isfile(WARD_SUMMARY_FILE):
    ward_summary = pd.read_csv(WARD_SUMMARY_FILE)
    print(f"Loaded ward summary: {len(ward_summary):,} rows")
if os.path.isfile(WARD_PROFICIENCY_FILE):
    ward_proficiency = pd.read_csv(WARD_PROFICIENCY_FILE)
    print(f"Loaded ward proficiency: {len(ward_proficiency):,} rows")
if os.path.isfile(EQUITY_PROGRESS_CITYWIDE_FILE):
    equity_progress_citywide = pd.read_csv(EQUITY_PROGRESS_CITYWIDE_FILE)
    print(f"Loaded equity progress citywide: {len(equity_progress_citywide):,} rows")
if os.path.isfile(EQUITY_PROGRESS_SUMMARY_FILE):
    equity_progress_summary_df = pd.read_csv(EQUITY_PROGRESS_SUMMARY_FILE)
    print(f"Loaded equity progress summary: {len(equity_progress_summary_df):,} rows")

# Prepare filter options
YEARS: List[int] = sorted([int(y) for y in multi_year['year'].dropna().unique()]) if not multi_year.empty else []
SUBJECTS: List[str] = sorted([s for s in multi_year['Subject'].dropna().unique()]) if not multi_year.empty else []
SUBGROUPS: List[str] = sorted([s for s in multi_year['subgroup_value_std'].dropna().unique()]) if not multi_year.empty else []
SCHOOLS: List[str] = sorted([s for s in multi_year['School Name'].dropna().unique()]) if not multi_year.empty else []

print(f"\nAvailable filters:")
print(f"  Years: {YEARS}")
print(f"  Subjects: {SUBJECTS}")
print(f"  Subgroups: {len(SUBGROUPS)} subgroups")
print(f"  Schools: {len(SCHOOLS)} schools")

# Module-level colour constants for chart components
WARD_COLORS = {
    1: '#1565c0', 2: '#1976d2', 3: '#1e88e5', 4: '#42a5f5',
    5: '#e65100', 6: '#ef6c00', 7: '#f57c00', 8: '#fb8c00',
}

# Build app
external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'DC School Test Score Explorer'

# Defaults
default_subject = SUBJECTS[0] if SUBJECTS else None
default_subgroup = 'All Students' if 'All Students' in SUBGROUPS else (SUBGROUPS[0] if SUBGROUPS else None)
if YEARS:
    default_year_range = [max(min(YEARS), YEARS[-1] - 2), YEARS[-1]] if len(YEARS) >= 2 else [YEARS[0], YEARS[0]]
else:
    default_year_range = [0, 0]

app.layout = html.Div(
    className="container py-3",
    children=[
        html.H2("DC School Test Score Explorer"),
        html.P(f"Data from {len(multi_year):,} school records across {len(YEARS)} years", className="text-muted"),
        
        html.Div(
            className="row g-3",
            children=[
                html.Div(className="col-md-3", children=[
                    html.Label("Subject"),
                    dcc.Dropdown(
                        id='subject-dd',
                        options=[{"label": s, "value": s} for s in SUBJECTS],
                        value=default_subject,
                        clearable=False
                    )
                ]),
                html.Div(className="col-md-3", children=[
                    html.Label("Student Group"),
                    dcc.Dropdown(
                        id='subgroup-dd',
                        options=[{"label": s, "value": s} for s in SUBGROUPS],
                        value=default_subgroup,
                        clearable=False
                    )
                ]),
                html.Div(className="col-md-6", children=[
                    html.Label("Schools (optional - leave blank for all)"),
                    dcc.Dropdown(
                        id='schools-dd',
                        options=[{"label": s, "value": s} for s in SCHOOLS],
                        value=None,
                        multi=True,
                        placeholder="Select schools to compare or leave blank for all"
                    )
                ]),
            ]
        ),
        
        html.Div(className="mt-3", children=[
            html.Label("Year Range"),
            dcc.RangeSlider(
                id='year-range',
                min=YEARS[0] if YEARS else 0,
                max=YEARS[-1] if YEARS else 0,
                value=default_year_range,
                marks={y: str(y) for y in YEARS},
                step=None
            ),
        ]),
        
        # ── Same-grade time series & bar charts ──────────────────────────
        html.H4("Same-Grade Performance Over Time", className="mt-4"),
        html.P("How does each grade's proficiency change year over year?", className="text-muted small"),
        html.Div(className="row g-3 mt-1", children=[
            html.Div(className="col-lg-6", children=[
                dcc.Graph(id='timeseries')
            ]),
            html.Div(className="col-lg-6", children=[
                dcc.Graph(id='bars')
            ]),
        ]),
        
        html.Hr(),
        
        # ── Cohort growth section ────────────────────────────────────────
        html.H4("Cohort Growth (Grade N → Grade N+1)", className="mt-3"),
        html.P("Tracks the same group of students as they advance one grade. "
               "Positive values mean students gained proficiency over the year.",
               className="text-muted small"),
        html.Div(className="row g-3 mt-1", children=[
            html.Div(className="col-lg-6", children=[
                dcc.Graph(id='cohort-bars')
            ]),
            html.Div(className="col-lg-6", children=[
                dcc.Graph(id='cohort-detail')
            ]),
        ]),
        
        html.Hr(),
        
        html.Div(children=[
            html.H5("School Locations Map (latest year)"),
            html.Small("Add input_data/school_locations.csv with columns: School Name, Latitude, Longitude to enable mapping.", className="text-muted"),
            dcc.Graph(id='map')
        ]),

        html.Hr(),

        # ── Equity gap section ───────────────────────────────────────────
        html.H4("Equity Gap Analysis", className="mt-3"),
        html.P(
            "Difference between each student subgroup and the 'All Students' average. "
            "Proficiency Gap = subgroup − All Students at baseline. "
            "Gap Change = how much the gap narrowed (positive) or widened (negative) "
            "over the cohort transition.",
            className="text-muted small",
        ),
        html.Small(
            "Run python src/equity_gap_analysis.py to generate this data.",
            className="text-muted",
            id='equity-note',
        ),
        html.Div(className="row g-3 mt-1", children=[
            html.Div(className="col-lg-6", children=[
                dcc.Graph(id='equity-gaps')
            ]),
            html.Div(className="col-lg-6", children=[
                dcc.Graph(id='equity-gap-change')
            ]),
        ]),

        html.Hr(),

        # ── Proficiency heatmap section ──────────────────────────────────
        html.H4("Proficiency Heatmap: Grade × Year", className="mt-3"),
        html.P(
            "How does each grade level's proficiency change across years? "
            "Select a school to see its grade-by-year heatmap, or leave blank "
            "for the citywide average.",
            className="text-muted small",
        ),
        html.Small(
            "Run python src/proficiency_trend_analysis.py to generate this data.",
            className="text-muted",
            id='heatmap-note',
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='heatmap')
        ]),

        html.Hr(),

        # ── Scatter plot section ─────────────────────────────────────────
        html.H4("Baseline Proficiency vs. Cohort Growth", className="mt-3"),
        html.P(
            "Each point is a school (filtered by subject and student group). "
            "X-axis: average baseline proficiency %. "
            "Y-axis: average cohort growth (percentage points). "
            "Schools in the upper-left quadrant — low baseline but positive growth — "
            "are 'beating the odds'. Point size reflects the number of cohort transitions.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='scatter')
        ]),

        html.Hr(),

        # ── Geographic equity section ────────────────────────────────────
        html.H4("Geographic Equity: Performance by DC Quadrant", className="mt-3"),
        html.P(
            "Average proficiency and cohort growth by DC geographic quadrant "
            "(NE / NW / SE / SW). Reveals persistent geographic disparities across "
            "the city. Run python src/geographic_equity_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Small(
            "Run python src/geographic_equity_analysis.py to generate this data.",
            className="text-muted",
            id='geo-equity-note',
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='geo-equity')
        ]),

        html.Hr(),

        # ── Same-grade YoY growth section ────────────────────────────────
        html.H4("Same-Grade Year-over-Year Growth", className="mt-3"),
        html.P(
            "How is each grade level improving at the same school year after year? "
            "Unlike cohort growth (which tracks the same students moving up a grade), "
            "same-grade YoY growth shows whether instruction at a given grade is "
            "improving over time. "
            "Run python src/yoy_growth_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='yoy-growth')
        ]),

        html.Hr(),

        # ── COVID Recovery section ───────────────────────────────────────
        html.H4("COVID Recovery Analysis (2019 → 2022 → 2024)", className="mt-3"),
        html.P(
            "How did each school's proficiency change from the pre-COVID 2019 baseline "
            "to the COVID-impacted 2022 year, and how much has it recovered by 2024? "
            "Schools are classified as: Exceeded Pre-COVID, Fully Recovered, "
            "Partially Recovered, or Still Below Pre-COVID. "
            "Run python src/covid_recovery_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='covid-recovery')
        ]),

        html.Hr(),

        # ── School Performance Trajectory section ─────────────────────────
        html.H4("School Performance Trajectory (2016–2024)", className="mt-3"),
        html.P(
            "Long-run proficiency trend for each school, estimated from a linear "
            "regression across all available years (2016–2024). "
            "Slope (pp/yr) classifies schools as: "
            "Strongly Improving (>2 pp/yr), Improving (0.5–2), Stable (±0.5), "
            "Declining (−0.5 to −2), or Strongly Declining (<−2). "
            "Run python src/school_trajectory_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='trajectory')
        ]),

        html.Hr(),

        # ── School Type Proficiency section ──────────────────────────────
        html.H4("Proficiency by School Type", className="mt-3"),
        html.P(
            "How does proficiency compare across school types (Elementary, Middle School, "
            "High School, Elementary-Middle, Middle-High)? "
            "Each line shows the average proficiency for all schools of that type by year. "
            "In school-selection mode, shows the selected schools colour-coded by type. "
            "Run python src/school_type_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='school-type')
        ]),

        html.Hr(),

        # ── Grade-Level Proficiency section ──────────────────────────────
        html.H4("Proficiency by Grade Level", className="mt-3"),
        html.P(
            "How does proficiency compare across grade levels (Grade 3–8 and High School)? "
            "Each line shows the average proficiency for all DC schools at that grade, "
            "by year and subject. In school-selection mode, shows the selected school's "
            "per-grade proficiency over time. "
            "Run python src/grade_level_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='grade-level')
        ]),

        html.Hr(),

        # ── Subgroup Proficiency Trend section ────────────────────────────
        html.H4("Proficiency Trends by Student Subgroup", className="mt-3"),
        html.P(
            "How do absolute proficiency levels compare across student demographic "
            "groups (All Students, Male, Female, Black or African American, "
            "Hispanic/Latino, White, Asian, Economically Disadvantaged, EL Active, "
            "Students with Disabilities) over time? "
            "Run python src/subgroup_trend_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='subgroup-trend')
        ]),

        html.Hr(),

        # ── Performance Consistency section ───────────────────────────────
        html.H4("School Performance Consistency", className="mt-3"),
        html.P(
            "How stable is each school's proficiency from year to year? "
            "Each point is a school (All Students, selected subject). "
            "X-axis: average proficiency. Y-axis: Coefficient of Variation (CV = std/avg × 100%) — "
            "higher CV means more year-to-year fluctuation. "
            "Schools are classified into four quadrants: "
            "High-Consistent (steady high performers), High-Volatile (high but fluctuating), "
            "Low-Consistent (steady but low), and Low-Volatile (low and fluctuating). "
            "Run python src/school_consistency_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='consistency')
        ]),

        html.Hr(),

        # ── Multi-Metric Performance Index section ────────────────────────
        html.H4("Multi-Metric School Performance Index", className="mt-3"),
        html.P(
            "A composite school performance score (0–100) that synthesises four "
            "analytical dimensions: (1) Proficiency — average All Students proficiency "
            "level; (2) Growth — average cohort-growth (Grade N → N+1); "
            "(3) Recovery — COVID recovery pp (2022→2024); and "
            "(4) Trajectory — long-run OLS trend slope (pp/yr). "
            "Each component is percentile-ranked within the subject; the composite is "
            "the mean of available component scores. Schools are grouped into five "
            "quintiles (Q5 = Top Performers … Q1 = Bottom Performers). "
            "Run python src/school_performance_index.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='performance-index')
        ]),

        html.Hr(),

        # ── School Program Sector Comparison section ──────────────────────
        html.H4("School Program Sector Comparison", className="mt-3"),
        html.P(
            "How do different school program sectors compare in proficiency and growth trends? "
            "Schools are classified as: Charter (4-digit OSSE codes), "
            "DCPS Specialized (selective/themed magnets: Banneker HS, McKinley Tech HS, "
            "Duke Ellington, School Without Walls), "
            "DCPS Alternative (STAY programs, alternative HS), and "
            "DCPS Traditional (neighborhood schools). "
            "Run python src/charter_dcps_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='sector-comparison')
        ]),

        html.Hr(),

        # ── School Needs Index section ────────────────────────────────────
        html.H4("School Needs Index", className="mt-3"),
        html.P(
            "Which schools most need intervention support? "
            "The Needs Index is the policy-targeted complement to the Performance Index. "
            "It combines four inverted dimensions: (1) Low Proficiency; (2) Low Cohort Growth; "
            "(3) COVID Recovery Deficit (net change vs. pre-COVID); and "
            "(4) Equity Gap Severity (mean absolute gap across disadvantaged groups). "
            "Each component is percentile-ranked within the subject; the composite is "
            "the mean of available components. Schools are grouped into four tiers: "
            "Critical (top-quartile need), High, Moderate, and Low. "
            "Run python src/school_needs_index.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='needs-index')
        ]),

        html.Hr(),

        # ── Ward-Level Performance Analysis section ───────────────────────
        html.H4("Ward-Level Performance Analysis", className="mt-3"),
        html.P(
            "How do DC's eight political wards compare in proficiency and cohort growth? "
            "DC wards (1–8) are the primary political and planning units used by the DC "
            "Council and DCPS.  Each school is assigned to a ward based on its neighbourhood "
            "(from school_locations.csv).  The chart shows average proficiency (left axis, "
            "bars) and average cohort growth (right axis, line) per ward × subject.  "
            "Ward 3 (NW: Tenleytown, Cleveland Park, Chevy Chase) is used as the reference "
            "because it historically has the highest DCPS proficiency; the gap_vs_ward3_pp "
            "metric shows how far each ward's average proficiency is below that benchmark. "
            "Run python src/ward_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='ward-analysis')
        ]),

        html.Hr(),

        # ── Equity Progress (Gap Closure) section ─────────────────────────
        html.H4("Equity Progress: Are Achievement Gaps Closing?", className="mt-3"),
        html.P(
            "Has DC made progress on closing achievement gaps between student "
            "demographic groups?  For six key subgroup pairs (White − Black, "
            "White − Hispanic, White − Econ Dis, All − Econ Dis, All − EL Active, "
            "All − Students with Disabilities) this chart shows whether the "
            "average proficiency gap across DC schools is Narrowing, Stable, or "
            "Widening from the earliest available year to the most recent year.  "
            "Bars to the left (negative gap change) indicate equity improvement; "
            "bars to the right (positive gap change) indicate the gap has grown. "
            "Run python src/equity_progress_analysis.py to generate this data.",
            className="text-muted small",
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='equity-progress')
        ]),
    ]
)


def filter_data(subject: Optional[str], subgroup: Optional[str], schools: Optional[List[str]], year_range: List[int]) -> pd.DataFrame:
    """Filter the dataset based on user selections."""
    if multi_year.empty:
        return multi_year
    
    df = multi_year.copy()
    
    if subject:
        df = df[df['Subject'] == subject]
    
    if subgroup:
        df = df[df['subgroup_value_std'] == subgroup]
    
    if schools:
        df = df[df['School Name'].isin(schools)]
    
    df = df[df['year'].between(year_range[0], year_range[1])]
    
    return df


@app.callback(
    Output('timeseries', 'figure'),
    Output('bars', 'figure'),
    Output('cohort-bars', 'figure'),
    Output('cohort-detail', 'figure'),
    Output('map', 'figure'),
    Output('equity-gaps', 'figure'),
    Output('equity-gap-change', 'figure'),
    Output('heatmap', 'figure'),
    Output('scatter', 'figure'),
    Output('geo-equity', 'figure'),
    Output('yoy-growth', 'figure'),
    Output('covid-recovery', 'figure'),
    Output('trajectory', 'figure'),
    Output('school-type', 'figure'),
    Output('grade-level', 'figure'),
    Output('subgroup-trend', 'figure'),
    Output('consistency', 'figure'),
    Output('performance-index', 'figure'),
    Output('sector-comparison', 'figure'),
    Output('needs-index', 'figure'),
    Output('ward-analysis', 'figure'),
    Output('equity-progress', 'figure'),
    Input('subject-dd', 'value'),
    Input('subgroup-dd', 'value'),
    Input('schools-dd', 'value'),
    Input('year-range', 'value')
)
def update_figures(subject, subgroup, schools, year_range):
    """Update all visualizations based on user selections."""
    schools = schools or []
    df = filter_data(subject, subgroup, schools, year_range)
    
    # Timeseries: average percent by school and year
    ts = (
        df.groupby(['School Name', 'year'], as_index=False)
          .agg(percent=('percent_value', 'mean'))
    )
    
    # Limit to selected schools if any
    if schools:
        ts = ts[ts['School Name'].isin(schools)]
    else:
        # Show top 10 schools by latest year performance
        latest_year = year_range[1]
        top_schools = (
            df[df['year'] == latest_year]
            .groupby('School Name', as_index=False)
            .agg(percent=('percent_value', 'mean'))
            .nlargest(10, 'percent')['School Name'].tolist()
        )
        ts = ts[ts['School Name'].isin(top_schools)]
    
    fig_ts = px.line(
        ts, x='year', y='percent', color='School Name',
        markers=True,
        title=f'{subject} - Percent Meeting/Exceeding Over Time',
        labels={'percent': 'Percent', 'year': 'Year'}
    )
    fig_ts.update_layout(yaxis_title='Percent Meeting/Exceeding', xaxis_title='Year')
    
    # Bar chart: latest year
    latest_year = year_range[1]
    bars = (
        df[df['year'] == latest_year]
        .groupby('School Name', as_index=False)
        .agg(percent=('percent_value', 'mean'))
        .sort_values('percent', ascending=False)
    )
    
    # Limit to top schools if not filtered
    if not schools:
        bars = bars.head(20)
    
    fig_bars = px.bar(
        bars, x='percent', y='School Name', orientation='h',
        title=f'{subject} - Year {latest_year}: Top Schools',
        labels={'percent': 'Percent Meeting/Exceeding', 'School Name': 'School'}
    )
    fig_bars.update_layout(xaxis_title='Percent', yaxis_title='School')
    
    # Map: join with locations if available
    if locations_df is not None and not locations_df.empty:
        map_df = (
            df[df['year'] == latest_year]
            .groupby('School Name', as_index=False)
            .agg(percent=('percent_value', 'mean'))
        )
        map_df = map_df.merge(
            locations_df[['School Name', 'Latitude', 'Longitude']],
            on='School Name',
            how='inner'
        )
        map_df = map_df.dropna(subset=['Latitude', 'Longitude'])
        map_df['Latitude'] = pd.to_numeric(map_df['Latitude'], errors='coerce')
        map_df['Longitude'] = pd.to_numeric(map_df['Longitude'], errors='coerce')
        map_df = map_df.dropna(subset=['Latitude', 'Longitude'])

        fig_map = px.scatter_map(
            map_df,
            lat='Latitude', lon='Longitude',
            color='percent', size='percent',
            hover_name='School Name',
            hover_data={'Latitude': False, 'Longitude': False, 'percent': ':.1f'},
            color_continuous_scale='Viridis',
            size_max=20, zoom=10,
            title=f'{subject} - {latest_year}: School Performance Map',
            map_style='open-street-map',
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    else:
        # Empty map placeholder
        fig_map = px.scatter_map(
            pd.DataFrame({'lat': [], 'lon': []}), lat='lat', lon='lon',
            map_style='open-street-map',
            title='Add school_locations.csv to enable mapping',
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    
    # ── Cohort growth charts ─────────────────────────────────────────────
    fig_cohort_bars = go.Figure()
    fig_cohort_detail = go.Figure()

    if not cohort_summary.empty:
        cs = cohort_summary.copy()
        # Filter by subject
        if subject:
            cs = cs[cs['Subject'] == subject]
        # Filter by subgroup
        if subgroup:
            cs = cs[cs['Student Group Value'] == subgroup]
        # Filter by schools
        if schools:
            cs = cs[cs['School Name'].isin(schools)]

        if not cs.empty:
            # Bar chart: top/bottom schools by avg cohort growth
            cs_sorted = cs.sort_values('avg_pp_growth', ascending=True)
            if not schools:
                # Show top 15 and bottom 5
                top15 = cs_sorted.tail(15)
                bot5 = cs_sorted.head(5)
                chart_data = pd.concat([bot5, top15]).drop_duplicates()
            else:
                chart_data = cs_sorted

            colors = ['#d32f2f' if v < 0 else '#388e3c' for v in chart_data['avg_pp_growth']]
            fig_cohort_bars = go.Figure(go.Bar(
                x=chart_data['avg_pp_growth'],
                y=chart_data['School Name'],
                orientation='h',
                marker_color=colors,
                text=chart_data['avg_pp_growth'].apply(lambda x: f'{x:+.1f}'),
                textposition='auto',
            ))
            fig_cohort_bars.update_layout(
                title=f'{subject} – Avg Cohort Growth (pp)',
                xaxis_title='Percentage Point Growth',
                yaxis_title='',
                yaxis=dict(autorange='reversed') if not schools else {},
                height=max(400, len(chart_data) * 25),
            )

    if not cohort_detail.empty:
        cd = cohort_detail.copy()
        if subject:
            cd = cd[cd['Subject'] == subject]
        if subgroup:
            cd = cd[cd['Student Group Value'] == subgroup]
        if schools:
            cd = cd[cd['School Name'].isin(schools)]

        if not cd.empty:
            # Grouped bar: show each transition for selected schools
            if schools:
                fig_cohort_detail = px.bar(
                    cd,
                    x='transition_label',
                    y='pp_growth',
                    color='School Name',
                    barmode='group',
                    title=f'{subject} – Cohort Growth by Transition',
                    labels={'pp_growth': 'PP Growth', 'transition_label': 'Transition'},
                )
            else:
                # Distribution of growth across all schools per transition
                fig_cohort_detail = px.box(
                    cd,
                    x='transition_label',
                    y='pp_growth',
                    title=f'{subject} – Cohort Growth Distribution by Transition',
                    labels={'pp_growth': 'PP Growth', 'transition_label': 'Transition'},
                )
    
    if fig_cohort_bars.data == ():
        fig_cohort_bars.update_layout(title='No cohort data – run analyze_cohort_growth.py')
    if fig_cohort_detail.data == ():
        fig_cohort_detail.update_layout(title='No cohort data – run analyze_cohort_growth.py')

    # ── Equity gap charts ────────────────────────────────────────────────
    fig_equity_gaps = go.Figure()
    fig_equity_gap_change = go.Figure()

    if not equity_summary.empty:
        eq = equity_summary.copy()
        if subject:
            eq = eq[eq['Subject'] == subject]
        if schools:
            eq = eq[eq['School Name'].isin(schools)]

        if not eq.empty:
            # Citywide view: average proficiency gap by subgroup
            if not schools:
                citywide_eq = (
                    eq
                    .groupby('Student Group Value', as_index=False)
                    .agg(
                        avg_proficiency_gap=('avg_proficiency_gap', 'mean'),
                        avg_gap_change=('avg_gap_change', 'mean'),
                        is_disadvantaged=('is_disadvantaged', 'first'),
                    )
                    .sort_values('avg_proficiency_gap')
                )
                colors_gap = [
                    '#d32f2f' if row['is_disadvantaged'] else '#1565c0'
                    for _, row in citywide_eq.iterrows()
                ]
                fig_equity_gaps = go.Figure(go.Bar(
                    x=citywide_eq['avg_proficiency_gap'],
                    y=citywide_eq['Student Group Value'],
                    orientation='h',
                    marker_color=colors_gap,
                    text=citywide_eq['avg_proficiency_gap'].apply(lambda x: f'{x:+.1f}'),
                    textposition='auto',
                ))
                fig_equity_gaps.update_layout(
                    title=f'{subject} – Citywide Avg Proficiency Gap vs All Students',
                    xaxis_title='Proficiency Gap (pp)',
                    yaxis_title='',
                    xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black'),
                )

                colors_change = [
                    '#388e3c' if v > 0 else '#d32f2f'
                    for v in citywide_eq['avg_gap_change']
                ]
                fig_equity_gap_change = go.Figure(go.Bar(
                    x=citywide_eq['avg_gap_change'],
                    y=citywide_eq['Student Group Value'],
                    orientation='h',
                    marker_color=colors_change,
                    text=citywide_eq['avg_gap_change'].apply(lambda x: f'{x:+.1f}'),
                    textposition='auto',
                ))
                fig_equity_gap_change.update_layout(
                    title=f'{subject} – Citywide Avg Gap Change (+ = narrowing)',
                    xaxis_title='Gap Change (pp)',
                    yaxis_title='',
                    xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black'),
                )
            else:
                # School-level view: proficiency gap per school for selected subgroup
                eq_sub = eq.copy()
                if subgroup and subgroup != 'All Students':
                    eq_sub = eq_sub[eq_sub['Student Group Value'] == subgroup]
                if not eq_sub.empty:
                    eq_sub_sorted = eq_sub.sort_values('avg_proficiency_gap')
                    colors_gap = [
                        '#d32f2f' if v < 0 else '#1565c0'
                        for v in eq_sub_sorted['avg_proficiency_gap']
                    ]
                    fig_equity_gaps = go.Figure(go.Bar(
                        x=eq_sub_sorted['avg_proficiency_gap'],
                        y=eq_sub_sorted['School Name'],
                        orientation='h',
                        marker_color=colors_gap,
                        text=eq_sub_sorted['avg_proficiency_gap'].apply(lambda x: f'{x:+.1f}'),
                        textposition='auto',
                    ))
                    fig_equity_gaps.update_layout(
                        title=f'{subject} – Proficiency Gap vs All Students',
                        xaxis_title='Proficiency Gap (pp)',
                        yaxis_title='',
                        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black'),
                        height=max(400, len(eq_sub_sorted) * 30),
                    )

                    colors_change = [
                        '#388e3c' if v > 0 else '#d32f2f'
                        for v in eq_sub_sorted['avg_gap_change']
                    ]
                    fig_equity_gap_change = go.Figure(go.Bar(
                        x=eq_sub_sorted['avg_gap_change'],
                        y=eq_sub_sorted['School Name'],
                        orientation='h',
                        marker_color=colors_change,
                        text=eq_sub_sorted['avg_gap_change'].apply(lambda x: f'{x:+.1f}'),
                        textposition='auto',
                    ))
                    fig_equity_gap_change.update_layout(
                        title=f'{subject} – Gap Change (+ = narrowing)',
                        xaxis_title='Gap Change (pp)',
                        yaxis_title='',
                        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black'),
                        height=max(400, len(eq_sub_sorted) * 30),
                    )

    if fig_equity_gaps.data == ():
        fig_equity_gaps.update_layout(
            title='No equity data – run src/equity_gap_analysis.py'
        )
    if fig_equity_gap_change.data == ():
        fig_equity_gap_change.update_layout(
            title='No equity data – run src/equity_gap_analysis.py'
        )

    # ── Proficiency heatmap ──────────────────────────────────────────────
    fig_heatmap = go.Figure()

    if not proficiency_trends.empty:
        pt = proficiency_trends.copy()
        if subject:
            pt = pt[pt['Subject'] == subject]
        if subgroup:
            pt = pt[pt['Student Group Value'] == subgroup]
        pt = pt[pt['year'].between(year_range[0], year_range[1])]

        # Choose data scope: single school or citywide average
        if schools:
            focus_school = schools[0]
            pt = pt[pt['School Name'] == focus_school]
            heatmap_title = f'{subject} – {focus_school}: Grade × Year Proficiency (%)'
        else:
            # Citywide average across all schools
            pt = (
                pt.groupby(['year', 'grade'], as_index=False)
                  .agg(proficiency_pct=('proficiency_pct', 'mean'))
            )
            heatmap_title = f'{subject} – Citywide Average: Grade × Year Proficiency (%)'

        if not pt.empty:
            # Pivot to grade × year matrix
            heatmap_pivot = pt.pivot_table(
                index='grade',
                columns='year',
                values='proficiency_pct',
                aggfunc='mean',
            )

            # Sort grades numerically (e.g. 'Grade 6' → 6, 'Grade 10' → 10)
            def _grade_key(g):
                m = re.search(r'\d+', str(g))
                return int(m.group()) if m else 99

            sorted_grades = sorted(heatmap_pivot.index.tolist(), key=_grade_key)
            heatmap_pivot = heatmap_pivot.reindex(sorted_grades)
            sorted_years = sorted(heatmap_pivot.columns.tolist())
            heatmap_pivot = heatmap_pivot[sorted_years]

            z = heatmap_pivot.values.tolist()
            x_labels = [str(int(y)) for y in sorted_years]
            y_labels = sorted_grades

            # Build text annotations (show value or dash for suppressed/missing cells)
            text_vals = [
                [f'{v:.1f}%' if not np.isnan(v) else '—' for v in row]
                for row in heatmap_pivot.values.tolist()
            ]

            fig_heatmap = go.Figure(go.Heatmap(
                z=z,
                x=x_labels,
                y=y_labels,
                text=text_vals,
                texttemplate='%{text}',
                colorscale='RdYlGn',
                zmid=50,
                colorbar=dict(title='% Proficient'),
                hoverongaps=False,
            ))
            fig_heatmap.update_layout(
                title=heatmap_title,
                xaxis_title='Year',
                yaxis_title='Grade',
                # 55 pixels per grade row + 120 px for title/axes, minimum 300 px
                height=max(300, len(y_labels) * 55 + 120),
            )

    if fig_heatmap.data == ():
        fig_heatmap.update_layout(
            title='No trend data – run src/proficiency_trend_analysis.py'
        )

    # ── Scatter: baseline proficiency vs. cohort growth ──────────────────
    fig_scatter = go.Figure()

    if not cohort_summary.empty:
        sc = cohort_summary.copy()
        if subject:
            sc = sc[sc['Subject'] == subject]
        if subgroup:
            sc = sc[sc['Student Group Value'] == subgroup]
        if schools:
            sc = sc[sc['School Name'].isin(schools)]

        sc = sc.dropna(subset=['avg_baseline_pct', 'avg_pp_growth'])

        if not sc.empty:
            # Quadrant reference lines and annotation
            x_mid = 50.0  # reference line at 50% proficiency
            y_mid = 0.0   # reference line at 0 growth

            fig_scatter = px.scatter(
                sc,
                x='avg_baseline_pct',
                y='avg_pp_growth',
                size='n_transitions',
                color='pct_significant_transitions',
                hover_name='School Name',
                hover_data={
                    'avg_baseline_pct': ':.1f',
                    'avg_pp_growth': ':.2f',
                    'n_transitions': True,
                    'pct_significant_transitions': ':.1f',
                },
                color_continuous_scale='Blues',
                size_max=20,
                title=(
                    f'{subject} – Baseline Proficiency vs. Cohort Growth'
                    + (f' ({subgroup})' if subgroup else '')
                ),
                labels={
                    'avg_baseline_pct': 'Avg Baseline Proficiency (%)',
                    'avg_pp_growth': 'Avg Cohort Growth (pp)',
                    'n_transitions': '# Transitions',
                    'pct_significant_transitions': '% Significant',
                },
            )
            # Add quadrant reference lines
            fig_scatter.add_hline(
                y=y_mid, line_dash='dash', line_color='grey', line_width=1,
            )
            fig_scatter.add_vline(
                x=x_mid, line_dash='dash', line_color='grey', line_width=1,
            )
            # Quadrant labels — positions as 5% / 95% of data range for robustness
            x_pad = (sc['avg_baseline_pct'].max() - sc['avg_baseline_pct'].min()) * 0.1 or 1.0
            y_pad = (sc['avg_pp_growth'].max() - sc['avg_pp_growth'].min()) * 0.1 or 1.0
            x_range = [sc['avg_baseline_pct'].min() - x_pad, sc['avg_baseline_pct'].max() + x_pad]
            y_range = [sc['avg_pp_growth'].min() - y_pad, sc['avg_pp_growth'].max() + y_pad]
            x_inner_pad = (x_range[1] - x_range[0]) * 0.05
            y_inner_pad = (y_range[1] - y_range[0]) * 0.05
            for annotation in [
                dict(x=x_range[0] + x_inner_pad, y=y_range[1] - y_inner_pad,
                     text='Beating the odds', showarrow=False,
                     font=dict(size=10, color='#388e3c')),
                dict(x=x_range[1] - x_inner_pad, y=y_range[1] - y_inner_pad,
                     text='High & growing', showarrow=False,
                     font=dict(size=10, color='#1565c0')),
                dict(x=x_range[0] + x_inner_pad, y=y_range[0] + y_inner_pad,
                     text='Struggling', showarrow=False,
                     font=dict(size=10, color='#d32f2f')),
                dict(x=x_range[1] - x_inner_pad, y=y_range[0] + y_inner_pad,
                     text='High but declining', showarrow=False,
                     font=dict(size=10, color='#e65100')),
            ]:
                fig_scatter.add_annotation(**annotation)
            fig_scatter.update_layout(height=500)

    if fig_scatter.data == ():
        fig_scatter.update_layout(
            title='No cohort data – run src/analyze_cohort_growth.py'
        )

    # ── Geographic equity bar chart ───────────────────────────────────────
    fig_geo = go.Figure()
    if not geo_equity.empty:
        gq = geo_equity.copy()
        if subject:
            gq = gq[gq['Subject'] == subject]
        if not gq.empty:
            quadrant_order = ['NE', 'NW', 'SE', 'SW']
            gq['Quadrant'] = pd.Categorical(gq['Quadrant'], categories=quadrant_order, ordered=True)
            gq = gq.sort_values('Quadrant')

            fig_geo.add_trace(go.Bar(
                name='Avg Proficiency (%)',
                x=gq['Quadrant'],
                y=gq['avg_mean_proficiency'],
                marker_color='#1976d2',
                text=gq['avg_mean_proficiency'].round(1).astype(str) + '%',
                textposition='outside',
                yaxis='y',
            ))
            fig_geo.add_trace(go.Scatter(
                name='Avg Cohort Growth (pp)',
                x=gq['Quadrant'],
                y=gq['avg_pp_growth'],
                mode='markers+lines',
                marker=dict(size=10, color='#e65100'),
                line=dict(color='#e65100', width=2),
                yaxis='y2',
            ))
            fig_geo.update_layout(
                title=f'{subject} – Average Proficiency & Cohort Growth by DC Quadrant' if subject else 'Average Proficiency & Cohort Growth by DC Quadrant',
                xaxis_title='DC Quadrant',
                yaxis=dict(title='Avg Proficiency (%)', side='left'),
                yaxis2=dict(title='Avg Cohort Growth (pp)', overlaying='y', side='right', zeroline=True),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=400,
                barmode='group',
            )
    if not fig_geo.data:
        fig_geo.update_layout(
            title='No geographic equity data – run src/geographic_equity_analysis.py'
        )

    # ── Same-grade YoY growth line chart ─────────────────────────────────
    fig_yoy = go.Figure()

    if not yoy_detail.empty:
        yd = yoy_detail.copy()
        if subject:
            yd = yd[yd['Subject'] == subject]
        if subgroup:
            yd = yd[yd['Student Group Value'] == subgroup]
        if schools:
            yd = yd[yd['School Name'].isin(schools)]

        if not yd.empty:
            if schools:
                # School view: one line per selected school, avg over grades per transition
                yd_agg = (
                    yd.groupby(['School Name', 'transition_label'], as_index=False)
                    .agg(avg_pp_change=('pp_change', 'mean'))
                    .sort_values('transition_label')
                )
                for school_name in yd_agg['School Name'].unique():
                    school_data = yd_agg[yd_agg['School Name'] == school_name]
                    fig_yoy.add_trace(go.Scatter(
                        x=school_data['transition_label'],
                        y=school_data['avg_pp_change'],
                        mode='lines+markers',
                        name=school_name,
                    ))
                fig_yoy.update_layout(
                    title=f'{subject} – Same-Grade YoY Growth by Transition',
                    xaxis_title='Transition Period',
                    yaxis_title='Avg pp Change (same grade, year over year)',
                )
            else:
                # Citywide view: one line per grade level (All Students subgroup only)
                yd_all = yd[yd['Student Group Value'] == 'All Students'] if 'All Students' in yd['Student Group Value'].values else yd
                yd_agg = (
                    yd_all.groupby(['grade', 'transition_label'], as_index=False)
                    .agg(avg_pp_change=('pp_change', 'mean'))
                    .sort_values('transition_label')
                )

                # Sort grades numerically for legend order
                def _grade_key_yoy(g):
                    m = re.search(r'\d+', str(g))
                    return int(m.group()) if m else 99

                sorted_grades_yoy = sorted(yd_agg['grade'].unique(), key=_grade_key_yoy)

                for grade_name in sorted_grades_yoy:
                    gdata = yd_agg[yd_agg['grade'] == grade_name].sort_values('transition_label')
                    fig_yoy.add_trace(go.Scatter(
                        x=gdata['transition_label'],
                        y=gdata['avg_pp_change'],
                        mode='lines+markers',
                        name=grade_name,
                    ))
                fig_yoy.add_hline(
                    y=0, line_dash='dash', line_color='grey', line_width=1,
                )
                fig_yoy.update_layout(
                    title=f'{subject} – Citywide Same-Grade YoY Growth by Grade Level',
                    xaxis_title='Transition Period',
                    yaxis_title='Avg pp Change (same grade, year over year)',
                    legend_title='Grade',
                    height=450,
                )

    if not fig_yoy.data:
        fig_yoy.update_layout(
            title='No YoY data – run src/yoy_growth_analysis.py'
        )

    # ── COVID Recovery grouped bar chart ─────────────────────────────────
    fig_covid = go.Figure()

    if not covid_recovery.empty:
        cr = covid_recovery.copy()
        if subject:
            cr = cr[cr['Subject'] == subject]
        if schools:
            cr = cr[cr['School Name'].isin(schools)]

        if not cr.empty:
            if schools:
                # School view: grouped bar showing 2019/2022/2024 proficiency
                cr_sel = cr.dropna(subset=['pct_2019'])
                cr_sel = cr_sel.sort_values('net_vs_precovid_pp', ascending=True)
                fig_covid.add_trace(go.Bar(
                    name='2019 (Pre-COVID)',
                    x=cr_sel['School Name'],
                    y=cr_sel['pct_2019'],
                    marker_color='#1565c0',
                ))
                fig_covid.add_trace(go.Bar(
                    name='2022 (COVID Impact)',
                    x=cr_sel['School Name'],
                    y=cr_sel['pct_2022'],
                    marker_color='#d32f2f',
                ))
                fig_covid.add_trace(go.Bar(
                    name='2024 (Recovery)',
                    x=cr_sel['School Name'],
                    y=cr_sel['pct_2024'],
                    marker_color='#388e3c',
                ))
                fig_covid.update_layout(
                    title=f'{subject} – Proficiency: 2019 vs 2022 vs 2024',
                    xaxis_title='School',
                    yaxis_title='Proficiency (%)',
                    barmode='group',
                    height=max(400, len(cr_sel) * 30),
                )
            else:
                # Citywide view: scatter of COVID impact vs. recovery
                cr_plot = cr.dropna(subset=['covid_impact_pp', 'recovery_pp'])
                status_colors = {
                    'Exceeded Pre-COVID': '#1a9641',
                    'Fully Recovered': '#a6d96a',
                    'Partially Recovered': '#fdae61',
                    'Still Below Pre-COVID': '#d7191c',
                    'No 2024 Data': '#bdbdbd',
                    'Unknown': '#969696',
                }
                for status_val, color in status_colors.items():
                    sub_cr = cr_plot[cr_plot['recovery_status'] == status_val]
                    if sub_cr.empty:
                        continue
                    fig_covid.add_trace(go.Scatter(
                        x=sub_cr['covid_impact_pp'],
                        y=sub_cr['recovery_pp'],
                        mode='markers',
                        name=status_val,
                        marker=dict(color=color, size=8, opacity=0.8),
                        text=sub_cr['School Name'],
                        hovertemplate=(
                            '<b>%{text}</b><br>'
                            'COVID impact: %{x:+.1f} pp<br>'
                            'Recovery: %{y:+.1f} pp<br>'
                            '<extra></extra>'
                        ),
                    ))
                fig_covid.add_hline(
                    y=0, line_dash='dash', line_color='grey', line_width=1,
                )
                fig_covid.add_vline(
                    x=0, line_dash='dash', line_color='grey', line_width=1,
                )
                fig_covid.update_layout(
                    title=f'{subject} – COVID Impact (2019→2022) vs Recovery (2022→2024)',
                    xaxis_title='COVID Impact (pp, negative = decline)',
                    yaxis_title='Recovery 2022→2024 (pp)',
                    legend_title='Recovery Status',
                    height=500,
                )

    if not fig_covid.data:
        fig_covid.update_layout(
            title='No COVID recovery data – run src/covid_recovery_analysis.py'
        )

    # ── School performance trajectory scatter ─────────────────────────────
    fig_trajectory = go.Figure()

    if not school_trajectories.empty:
        tr = school_trajectories.copy()
        if subject:
            tr = tr[tr['Subject'] == subject]
        if schools:
            tr = tr[tr['School Name'].isin(schools)]

        # Exclude Insufficient Data rows when both axes are NaN
        tr_plot = tr.dropna(subset=['trend_slope_pp_yr', 'avg_proficiency_pct'])

        if not tr_plot.empty:
            trajectory_colors = {
                'Strongly Improving': '#1a9641',
                'Improving': '#a6d96a',
                'Stable': '#ffffbf',
                'Declining': '#fdae61',
                'Strongly Declining': '#d7191c',
                'Insufficient Data': '#bdbdbd',
            }
            for tclass, color in trajectory_colors.items():
                sub_tr = tr_plot[tr_plot['trajectory_class'] == tclass]
                if sub_tr.empty:
                    continue
                fig_trajectory.add_trace(go.Scatter(
                    x=sub_tr['trend_slope_pp_yr'],
                    y=sub_tr['avg_proficiency_pct'],
                    mode='markers',
                    name=tclass,
                    marker=dict(color=color, size=9, opacity=0.85,
                                line=dict(width=0.5, color='#555')),
                    text=sub_tr['School Name'],
                    customdata=sub_tr[['first_proficiency_pct', 'last_proficiency_pct',
                                       'n_years_with_data']].values,
                    hovertemplate=(
                        '<b>%{text}</b><br>'
                        'Slope: %{x:+.3f} pp/yr<br>'
                        'Avg proficiency: %{y:.1f}%<br>'
                        'First → Last: %{customdata[0]:.1f}% → %{customdata[1]:.1f}%<br>'
                        'Years with data: %{customdata[2]}<br>'
                        '<extra></extra>'
                    ),
                ))
            fig_trajectory.add_vline(
                x=0, line_dash='dash', line_color='grey', line_width=1,
            )
            fig_trajectory.update_layout(
                title=(
                    f'{subject} – School Proficiency Trajectory (2016–2024)'
                    if subject else 'School Proficiency Trajectory (2016–2024)'
                ),
                xaxis_title='Trend Slope (pp/yr, positive = improving)',
                yaxis_title='Avg Proficiency, All Students (%)',
                legend_title='Trajectory',
                height=500,
            )

    if not fig_trajectory.data:
        fig_trajectory.update_layout(
            title='No trajectory data – run src/school_trajectory_analysis.py'
        )

    # ── School type proficiency line chart ────────────────────────────────
    fig_school_type = go.Figure()

    if not school_type_proficiency.empty:
        stp = school_type_proficiency.copy()
        if subject:
            stp = stp[stp['Subject'] == subject]
        stp = stp[stp['year'].between(year_range[0], year_range[1])]

        if schools and not school_type_by_school.empty:
            # School-selection mode: show selected schools coloured by type,
            # as scatter points overlaid on faint type-average lines
            sbs = school_type_by_school[
                school_type_by_school['School Name'].isin(schools)
            ][['School Name', 'School Type']].drop_duplicates()

            # Citywide type averages (faint lines for context)
            type_order_visible = stp['School Type'].unique()
            for stype in type_order_visible:
                tdata = stp[stp['School Type'] == stype].sort_values('year')
                fig_school_type.add_trace(go.Scatter(
                    x=tdata['year'],
                    y=tdata['avg_proficiency_pct'],
                    mode='lines',
                    name=f'{stype} (citywide avg)',
                    line=dict(dash='dot', width=1),
                    opacity=0.4,
                    showlegend=True,
                ))

            # Individual school proficiency series
            if not multi_year.empty:
                sel_df = multi_year[multi_year['School Name'].isin(schools)].copy()
                if subject:
                    sel_df = sel_df[sel_df['Subject'] == subject]
                sel_df = sel_df[sel_df['year'].between(year_range[0], year_range[1])]
                sel_df = sel_df.merge(sbs, on='School Name', how='left')
                school_avg = (
                    sel_df.groupby(['School Name', 'School Type', 'year'], as_index=False)
                    .agg(avg_pct=('percent_value', 'mean'))
                )
                for school_name in school_avg['School Name'].unique():
                    sd = school_avg[school_avg['School Name'] == school_name].sort_values('year')
                    stype = sd['School Type'].iloc[0] if not sd.empty else ''
                    fig_school_type.add_trace(go.Scatter(
                        x=sd['year'],
                        y=sd['avg_pct'],
                        mode='lines+markers',
                        name=f'{school_name} ({stype})',
                        marker=dict(size=8),
                    ))
            fig_school_type.update_layout(
                title=f'{subject} – Selected Schools Proficiency by School Type',
                xaxis_title='Year',
                yaxis_title='Avg Proficiency (%)',
                legend_title='School',
                height=500,
            )
        else:
            # Citywide mode: one line per school type
            school_type_order = [
                "Elementary", "Middle School", "High School",
                "Elementary-Middle", "Middle-High",
            ]
            for stype in school_type_order:
                tdata = stp[stp['School Type'] == stype].sort_values('year')
                if tdata.empty:
                    continue
                fig_school_type.add_trace(go.Scatter(
                    x=tdata['year'],
                    y=tdata['avg_proficiency_pct'],
                    mode='lines+markers',
                    name=stype,
                    customdata=tdata[['n_schools', 'median_proficiency_pct']].values,
                    hovertemplate=(
                        f'<b>{stype}</b><br>'
                        'Year: %{x}<br>'
                        'Avg proficiency: %{y:.1f}%<br>'
                        'Median: %{customdata[1]:.1f}%<br>'
                        'Schools: %{customdata[0]}<br>'
                        '<extra></extra>'
                    ),
                ))
            fig_school_type.update_layout(
                title=f'{subject} – Citywide Avg Proficiency by School Type',
                xaxis_title='Year',
                yaxis_title='Avg Proficiency (%)',
                legend_title='School Type',
                height=450,
            )

    if not fig_school_type.data:
        fig_school_type.update_layout(
            title='No school type data – run src/school_type_analysis.py'
        )

    # ── Grade-level proficiency line chart ────────────────────────────────
    GRADE_ORDER_DISPLAY = [
        "Grade 3", "Grade 4", "Grade 5",
        "Grade 6", "Grade 7", "Grade 8", "HS",
    ]
    fig_grade_level = go.Figure()

    if not grade_level_proficiency.empty:
        glp = grade_level_proficiency.copy()
        if subject:
            glp = glp[glp['Subject'] == subject]
        glp = glp[glp['year'].between(year_range[0], year_range[1])]

        if schools and not multi_year.empty:
            # School-selection mode: show selected school's per-grade proficiency
            sel_df = multi_year[multi_year['School Name'].isin(schools)].copy()
            if subject:
                sel_df = sel_df[sel_df['Subject'] == subject]
            sel_df = sel_df[sel_df['year'].between(year_range[0], year_range[1])]
            # Keep All Students rows for comparability
            sel_df = sel_df[sel_df['subgroup_value_std'].isin(
                {'All Students', 'All', 'Total'}
            )]
            sel_df = sel_df.dropna(subset=['Grade of Enrollment', 'percent_value'])
            sel_df['grade'] = sel_df['Grade of Enrollment'].str.strip()

            # Citywide grade averages as faint reference lines
            for grade in GRADE_ORDER_DISPLAY:
                gdata = glp[glp['grade'] == grade].sort_values('year')
                if gdata.empty:
                    continue
                fig_grade_level.add_trace(go.Scatter(
                    x=gdata['year'],
                    y=gdata['avg_proficiency_pct'],
                    mode='lines',
                    name=f'{grade} (citywide avg)',
                    line=dict(dash='dot', width=1),
                    opacity=0.4,
                    showlegend=True,
                ))

            # Selected school(s) lines per grade
            school_grade_avg = (
                sel_df.groupby(['School Name', 'grade', 'year'], as_index=False)
                .agg(avg_pct=('percent_value', 'mean'))
            )
            for school_name in school_grade_avg['School Name'].unique():
                for grade in GRADE_ORDER_DISPLAY:
                    sd = school_grade_avg[
                        (school_grade_avg['School Name'] == school_name) &
                        (school_grade_avg['grade'] == grade)
                    ].sort_values('year')
                    if sd.empty:
                        continue
                    fig_grade_level.add_trace(go.Scatter(
                        x=sd['year'],
                        y=sd['avg_pct'],
                        mode='lines+markers',
                        name=f'{school_name} – {grade}',
                        marker=dict(size=7),
                    ))
            fig_grade_level.update_layout(
                title=f'{subject} – Selected Schools Proficiency by Grade Level',
                xaxis_title='Year',
                yaxis_title='Avg Proficiency (%)',
                legend_title='School / Grade',
                height=500,
            )
        else:
            # Citywide mode: one line per grade level
            for grade in GRADE_ORDER_DISPLAY:
                gdata = glp[glp['grade'] == grade].sort_values('year')
                if gdata.empty:
                    continue
                fig_grade_level.add_trace(go.Scatter(
                    x=gdata['year'],
                    y=gdata['avg_proficiency_pct'],
                    mode='lines+markers',
                    name=grade,
                    customdata=gdata[['n_schools', 'median_proficiency_pct']].values,
                    hovertemplate=(
                        f'<b>{grade}</b><br>'
                        'Year: %{x}<br>'
                        'Avg proficiency: %{y:.1f}%<br>'
                        'Median: %{customdata[1]:.1f}%<br>'
                        'Schools: %{customdata[0]}<br>'
                        '<extra></extra>'
                    ),
                ))
            fig_grade_level.update_layout(
                title=f'{subject} – Citywide Avg Proficiency by Grade Level',
                xaxis_title='Year',
                yaxis_title='Avg Proficiency (%)',
                legend_title='Grade',
                height=450,
            )

    if not fig_grade_level.data:
        fig_grade_level.update_layout(
            title='No grade-level data – run src/grade_level_analysis.py'
        )

    # ── Subgroup proficiency trend line chart ─────────────────────────────
    SUBGROUP_ORDER_DISPLAY = [
        "All Students", "Male", "Female",
        "Black or African American", "Hispanic/Latino of any race",
        "White", "Asian", "Two or more races",
        # "Econ Dis" and "EL Active" are the OSSE source labels used in the data;
        # they appear as-is in combined_all_years.csv and subgroup_proficiency.csv.
        "Econ Dis", "EL Active", "Students with Disabilities",
    ]
    fig_subgroup = go.Figure()

    if not subgroup_proficiency.empty:
        sgp = subgroup_proficiency.copy()
        if subject:
            sgp = sgp[sgp['Subject'] == subject]
        sgp = sgp[sgp['year'].between(year_range[0], year_range[1])]

        if schools and not multi_year.empty:
            # School-selection mode: show selected school(s) proficiency for the
            # selected subgroup overlaid on faint citywide subgroup averages
            sel_df = multi_year[multi_year['School Name'].isin(schools)].copy()
            if subject:
                sel_df = sel_df[sel_df['Subject'] == subject]
            sel_df = sel_df[sel_df['year'].between(year_range[0], year_range[1])]
            sel_df = sel_df.rename(columns={'subgroup_value_std': 'subgroup'})
            sel_df = sel_df[sel_df['subgroup'].isin(SUBGROUP_ORDER_DISPLAY)]
            sel_df = sel_df.dropna(subset=['subgroup', 'percent_value'])

            # Faint citywide subgroup averages
            for sg in SUBGROUP_ORDER_DISPLAY:
                sgdata = sgp[sgp['subgroup'] == sg].sort_values('year')
                if sgdata.empty:
                    continue
                fig_subgroup.add_trace(go.Scatter(
                    x=sgdata['year'],
                    y=sgdata['avg_proficiency_pct'],
                    mode='lines',
                    name=f'{sg} (citywide)',
                    line=dict(dash='dot', width=1),
                    opacity=0.35,
                    showlegend=True,
                ))

            # Selected school(s) per subgroup
            school_sg_avg = (
                sel_df.groupby(['School Name', 'subgroup', 'year'], as_index=False)
                .agg(avg_pct=('percent_value', 'mean'))
            )
            for school_name in school_sg_avg['School Name'].unique():
                if subgroup and subgroup in SUBGROUP_ORDER_DISPLAY:
                    sg_list = [subgroup]
                else:
                    sg_list = [s for s in SUBGROUP_ORDER_DISPLAY
                               if s in school_sg_avg['subgroup'].values]
                for sg in sg_list:
                    sd = school_sg_avg[
                        (school_sg_avg['School Name'] == school_name) &
                        (school_sg_avg['subgroup'] == sg)
                    ].sort_values('year')
                    if sd.empty:
                        continue
                    fig_subgroup.add_trace(go.Scatter(
                        x=sd['year'],
                        y=sd['avg_pct'],
                        mode='lines+markers',
                        name=f'{school_name} – {sg}',
                        marker=dict(size=7),
                    ))
            fig_subgroup.update_layout(
                title=f'{subject} – Selected Schools Proficiency by Student Subgroup',
                xaxis_title='Year',
                yaxis_title='Avg Proficiency (%)',
                legend_title='School / Subgroup',
                height=500,
            )
        else:
            # Citywide mode: one line per subgroup
            for sg in SUBGROUP_ORDER_DISPLAY:
                sgdata = sgp[sgp['subgroup'] == sg].sort_values('year')
                if sgdata.empty:
                    continue
                fig_subgroup.add_trace(go.Scatter(
                    x=sgdata['year'],
                    y=sgdata['avg_proficiency_pct'],
                    mode='lines+markers',
                    name=sg,
                    customdata=sgdata[['n_schools', 'median_proficiency_pct']].values,
                    hovertemplate=(
                        f'<b>{sg}</b><br>'
                        'Year: %{x}<br>'
                        'Avg proficiency: %{y:.1f}%<br>'
                        'Median: %{customdata[1]:.1f}%<br>'
                        'Schools: %{customdata[0]}<br>'
                        '<extra></extra>'
                    ),
                ))
            fig_subgroup.update_layout(
                title=f'{subject} – Citywide Avg Proficiency by Student Subgroup',
                xaxis_title='Year',
                yaxis_title='Avg Proficiency (%)',
                legend_title='Student Subgroup',
                height=500,
            )

    if not fig_subgroup.data:
        fig_subgroup.update_layout(
            title='No subgroup data – run src/subgroup_trend_analysis.py'
        )

    # ── School performance consistency scatter ────────────────────────────
    CONSISTENCY_COLORS = {
        'High-Consistent': '#1a9641',
        'High-Volatile': '#a6d96a',
        'Low-Consistent': '#fdae61',
        'Low-Volatile': '#d7191c',
        'Insufficient Data': '#bdbdbd',
    }
    fig_consistency = go.Figure()

    if not school_consistency.empty:
        sc_df = school_consistency.copy()
        if subject:
            sc_df = sc_df[sc_df['Subject'] == subject]
        if schools:
            sc_df = sc_df[sc_df['School Name'].isin(schools)]

        sc_plot = sc_df.dropna(subset=['avg_proficiency_pct', 'cv_proficiency_pct'])

        if not sc_plot.empty:
            for cls, color in CONSISTENCY_COLORS.items():
                sub_cls = sc_plot[sc_plot['consistency_class'] == cls]
                if sub_cls.empty:
                    continue
                fig_consistency.add_trace(go.Scatter(
                    x=sub_cls['avg_proficiency_pct'],
                    y=sub_cls['cv_proficiency_pct'],
                    mode='markers',
                    name=cls,
                    marker=dict(
                        color=color, size=9, opacity=0.85,
                        line=dict(width=0.5, color='#555'),
                    ),
                    text=sub_cls['School Name'],
                    customdata=sub_cls[['n_years_with_data', 'std_proficiency_pct',
                                        'range_proficiency_pp']].values,
                    hovertemplate=(
                        '<b>%{text}</b><br>'
                        'Avg proficiency: %{x:.1f}%<br>'
                        'CV: %{y:.1f}%<br>'
                        'Std dev: %{customdata[1]:.1f} pp<br>'
                        'Range (max−min): %{customdata[2]:.1f} pp<br>'
                        'Years with data: %{customdata[0]}<br>'
                        '<extra></extra>'
                    ),
                ))

            # Median cut-point reference lines
            classifiable = sc_plot[sc_plot['consistency_class'] != 'Insufficient Data']
            if not classifiable.empty:
                med_avg = classifiable['avg_proficiency_pct'].median()
                med_cv = classifiable['cv_proficiency_pct'].median()
                fig_consistency.add_vline(
                    x=med_avg, line_dash='dash', line_color='grey', line_width=1,
                )
                fig_consistency.add_hline(
                    y=med_cv, line_dash='dash', line_color='grey', line_width=1,
                )
                x_rng = sc_plot['avg_proficiency_pct']
                y_rng = sc_plot['cv_proficiency_pct']
                x_pad = (x_rng.max() - x_rng.min()) * 0.05 or 1.0
                y_pad = (y_rng.max() - y_rng.min()) * 0.05 or 1.0
                for annotation in [
                    dict(x=x_rng.max() + x_pad, y=y_rng.min() - y_pad,
                         text='High-Consistent', showarrow=False,
                         font=dict(size=9, color='#1a9641'), xanchor='right'),
                    dict(x=x_rng.max() + x_pad, y=y_rng.max() + y_pad,
                         text='High-Volatile', showarrow=False,
                         font=dict(size=9, color='#7a9e3b'), xanchor='right'),
                    dict(x=x_rng.min() - x_pad, y=y_rng.min() - y_pad,
                         text='Low-Consistent', showarrow=False,
                         font=dict(size=9, color='#e09020'), xanchor='left'),
                    dict(x=x_rng.min() - x_pad, y=y_rng.max() + y_pad,
                         text='Low-Volatile', showarrow=False,
                         font=dict(size=9, color='#d7191c'), xanchor='left'),
                ]:
                    fig_consistency.add_annotation(**annotation)

            fig_consistency.update_layout(
                title=(
                    f'{subject} – School Performance Consistency'
                    if subject else 'School Performance Consistency'
                ),
                xaxis_title='Avg Proficiency, All Students (%)',
                yaxis_title='CV (Coefficient of Variation, %)',
                legend_title='Consistency Class',
                height=520,
            )

    if not fig_consistency.data:
        fig_consistency.update_layout(
            title='No consistency data – run src/school_consistency_analysis.py'
        )

    # ── Multi-Metric Performance Index scatter ────────────────────────────
    QUINTILE_COLORS = {
        'Q5 – Top Performers': '#1a9641',
        'Q4 – Above Average': '#a6d96a',
        'Q3 – Middle': '#ffffbf',
        'Q2 – Below Average': '#fdae61',
        'Q1 – Bottom Performers': '#d7191c',
        'Insufficient Data': '#bdbdbd',
    }
    fig_perf_index = go.Figure()

    if not performance_index.empty:
        pi = performance_index.copy()
        if subject:
            pi = pi[pi['Subject'] == subject]
        if schools:
            pi = pi[pi['School Name'].isin(schools)]

        pi_plot = pi.dropna(subset=['composite_score'])

        if not pi_plot.empty:
            quintile_order = [
                'Q5 – Top Performers', 'Q4 – Above Average', 'Q3 – Middle',
                'Q2 – Below Average', 'Q1 – Bottom Performers', 'Insufficient Data',
            ]
            component_labels = {
                'proficiency_score': 'Proficiency',
                'growth_score': 'Growth',
                'recovery_score': 'Recovery',
                'trajectory_score': 'Trajectory',
            }
            for quintile in quintile_order:
                sub_pi = pi_plot[pi_plot['composite_quintile'] == quintile]
                if sub_pi.empty:
                    continue

                # Build customdata for hover: n_components + component scores
                custom_cols = ['n_components', 'proficiency_score', 'growth_score',
                               'recovery_score', 'trajectory_score',
                               'cohort_growth_pp', 'covid_recovery_pp',
                               'trajectory_slope_pp_yr']
                # Use only columns that exist in the dataframe
                available_custom = [c for c in custom_cols if c in sub_pi.columns]
                customdata = sub_pi[available_custom].values

                fig_perf_index.add_trace(go.Scatter(
                    x=sub_pi['composite_score'],
                    y=sub_pi['proficiency_pct'],
                    mode='markers',
                    name=quintile,
                    marker=dict(
                        color=QUINTILE_COLORS.get(quintile, '#999'),
                        size=9, opacity=0.85,
                        line=dict(width=0.5, color='#555'),
                    ),
                    text=sub_pi['School Name'],
                    customdata=customdata,
                    hovertemplate=(
                        '<b>%{text}</b><br>'
                        'Composite: %{x:.1f}<br>'
                        'Avg proficiency: %{y:.1f}%<br>'
                        'Components used: %{customdata[0]}<br>'
                        'Proficiency score: %{customdata[1]:.1f}<br>'
                        'Growth score: %{customdata[2]:.1f}<br>'
                        'Recovery score: %{customdata[3]:.1f}<br>'
                        'Trajectory score: %{customdata[4]:.1f}<br>'
                        '<extra></extra>'
                    ),
                ))

            # Reference lines at original quintile boundaries derived from the
            # full subject population (before any school filter) so they stay
            # consistent with the pre-computed composite_quintile labels.
            pi_subject_full = performance_index.copy()
            if subject:
                pi_subject_full = pi_subject_full[pi_subject_full['Subject'] == subject]
            full_composites = pi_subject_full['composite_score'].dropna()
            for pct_val in [20, 40, 60, 80]:
                threshold = float(np.percentile(full_composites, pct_val))
                fig_perf_index.add_vline(
                    x=threshold, line_dash='dot', line_color='#aaa', line_width=1,
                )

            fig_perf_index.update_layout(
                title=(
                    f'{subject} – Multi-Metric School Performance Index'
                    if subject else 'Multi-Metric School Performance Index'
                ),
                xaxis_title='Composite Score (0–100)',
                yaxis_title='Avg Proficiency, All Students (%)',
                legend_title='Quintile',
                height=520,
            )

    if not fig_perf_index.data:
        fig_perf_index.update_layout(
            title='No index data – run src/school_performance_index.py'
        )

    # ── School program sector comparison bar chart ────────────────────────
    SECTOR_ORDER_DISPLAY = [
        "Charter",
        "DCPS Specialized",
        "DCPS Alternative",
        "DCPS Traditional",
    ]
    SECTOR_COLORS = {
        "Charter": "#9c27b0",
        "DCPS Specialized": "#1565c0",
        "DCPS Alternative": "#e65100",
        "DCPS Traditional": "#388e3c",
    }
    fig_sector = go.Figure()

    if not school_sector_proficiency.empty:
        sp = school_sector_proficiency.copy()
        if subject:
            sp = sp[sp['Subject'] == subject]
        sp = sp[sp['year'].between(year_range[0], year_range[1])]

        if schools and not school_sector_by_school.empty:
            # School-selection mode: show selected schools coloured by sector,
            # overlaid on faint sector-average lines
            sbs = school_sector_by_school[
                school_sector_by_school['School Name'].isin(schools)
            ][['School Name', 'School Sector']].drop_duplicates()

            # Faint sector average lines for context
            for sect in SECTOR_ORDER_DISPLAY:
                sdata = sp[sp['School Sector'] == sect].sort_values('year')
                if sdata.empty:
                    continue
                fig_sector.add_trace(go.Scatter(
                    x=sdata['year'],
                    y=sdata['avg_proficiency_pct'],
                    mode='lines',
                    name=f'{sect} (sector avg)',
                    line=dict(dash='dot', width=1,
                              color=SECTOR_COLORS.get(sect, '#999')),
                    opacity=0.4,
                    showlegend=True,
                ))

            # Individual school proficiency series
            if not multi_year.empty:
                sel_df = multi_year[multi_year['School Name'].isin(schools)].copy()
                if subject:
                    sel_df = sel_df[sel_df['Subject'] == subject]
                sel_df = sel_df[sel_df['year'].between(year_range[0], year_range[1])]
                sel_df = sel_df.merge(sbs, on='School Name', how='left')
                school_avg_df = (
                    sel_df.groupby(
                        ['School Name', 'School Sector', 'year'], as_index=False
                    ).agg(avg_pct=('percent_value', 'mean'))
                )
                for school_name in school_avg_df['School Name'].unique():
                    sd = school_avg_df[
                        school_avg_df['School Name'] == school_name
                    ].sort_values('year')
                    sect = sd['School Sector'].iloc[0] if not sd.empty else ''
                    fig_sector.add_trace(go.Scatter(
                        x=sd['year'],
                        y=sd['avg_pct'],
                        mode='lines+markers',
                        name=f'{school_name} ({sect})',
                        marker=dict(
                            size=8, color=SECTOR_COLORS.get(sect, '#999')
                        ),
                    ))
            fig_sector.update_layout(
                title=f'{subject} – Selected Schools Proficiency by Sector',
                xaxis_title='Year',
                yaxis_title='Avg Proficiency (%)',
                legend_title='School',
                height=500,
            )
        else:
            # Citywide mode: one line per sector
            for sect in SECTOR_ORDER_DISPLAY:
                sdata = sp[sp['School Sector'] == sect].sort_values('year')
                if sdata.empty:
                    continue
                fig_sector.add_trace(go.Scatter(
                    x=sdata['year'],
                    y=sdata['avg_proficiency_pct'],
                    mode='lines+markers',
                    name=sect,
                    marker=dict(size=8, color=SECTOR_COLORS.get(sect, '#999')),
                    line=dict(color=SECTOR_COLORS.get(sect, '#999'), width=2),
                    customdata=sdata[['n_schools', 'median_proficiency_pct']].values,
                    hovertemplate=(
                        f'<b>{sect}</b><br>'
                        'Year: %{x}<br>'
                        'Avg proficiency: %{y:.1f}%<br>'
                        'Median: %{customdata[1]:.1f}%<br>'
                        'Schools: %{customdata[0]}<br>'
                        '<extra></extra>'
                    ),
                ))
            fig_sector.update_layout(
                title=(
                    f'{subject} – Avg Proficiency by School Program Sector'
                    if subject else 'Avg Proficiency by School Program Sector'
                ),
                xaxis_title='Year',
                yaxis_title='Avg Proficiency (%)',
                legend_title='Sector',
                height=450,
            )

    if not fig_sector.data:
        fig_sector.update_layout(
            title='No sector data – run src/charter_dcps_analysis.py'
        )

    # ── School Needs Index scatter plot ───────────────────────────────────
    NEEDS_TIER_ORDER = ["Critical", "High", "Moderate", "Low", "Insufficient Data"]
    NEEDS_TIER_COLORS = {
        "Critical": "#d32f2f",
        "High": "#f57c00",
        "Moderate": "#fbc02d",
        "Low": "#388e3c",
        "Insufficient Data": "#9e9e9e",
    }
    NEEDS_CUSTOM_COLS = [
        'n_components', 'proficiency_need_score',
        'growth_need_score', 'recovery_need_score',
        'equity_need_score',
    ]
    fig_needs = go.Figure()

    if not school_needs_index.empty:
        ni = school_needs_index.copy()
        if subject:
            ni = ni[ni['Subject'] == subject]

        # School-selection mode: highlight selected schools; grey out others
        if schools:
            ni_highlight = ni[ni['School Name'].isin(schools)]
            ni_rest = ni[~ni['School Name'].isin(schools)]
            # Background points (faint)
            for tier in NEEDS_TIER_ORDER:
                sub_rest = ni_rest[ni_rest['needs_tier'] == tier]
                if sub_rest.empty:
                    continue
                fig_needs.add_trace(go.Scatter(
                    x=sub_rest['composite_needs_score'],
                    y=sub_rest['avg_proficiency_pct'],
                    mode='markers',
                    name=f'{tier} (other)',
                    marker=dict(color='#cccccc', size=6, opacity=0.3),
                    text=sub_rest['School Name'],
                    hovertemplate=(
                        '<b>%{text}</b><br>'
                        'Needs score: %{x:.1f}<br>'
                        'Avg proficiency: %{y:.1f}%<br>'
                        '<extra></extra>'
                    ),
                    showlegend=False,
                ))
            # Highlighted selected schools
            for tier in NEEDS_TIER_ORDER:
                sub_sel = ni_highlight[ni_highlight['needs_tier'] == tier]
                if sub_sel.empty:
                    continue
                avail = [c for c in NEEDS_CUSTOM_COLS if c in sub_sel.columns]
                customdata = sub_sel[avail].values if avail else None
                fig_needs.add_trace(go.Scatter(
                    x=sub_sel['composite_needs_score'],
                    y=sub_sel['avg_proficiency_pct'],
                    mode='markers+text',
                    name=tier,
                    marker=dict(
                        color=NEEDS_TIER_COLORS.get(tier, '#999'),
                        size=12, opacity=0.9,
                        line=dict(width=1, color='#333'),
                    ),
                    text=sub_sel['School Name'],
                    textposition='top center',
                    customdata=customdata,
                    hovertemplate=(
                        '<b>%{text}</b><br>'
                        'Needs score: %{x:.1f}<br>'
                        'Avg proficiency: %{y:.1f}%<br>'
                        '<extra></extra>'
                    ),
                ))
        else:
            # Citywide mode: all schools coloured by tier
            for tier in NEEDS_TIER_ORDER:
                sub_ni = ni[ni['needs_tier'] == tier]
                if sub_ni.empty:
                    continue
                avail = [c for c in NEEDS_CUSTOM_COLS if c in sub_ni.columns]
                customdata = sub_ni[avail].values if avail else None
                htmpl = (
                    '<b>%{text}</b><br>'
                    'Needs score: %{x:.1f}<br>'
                    'Avg proficiency: %{y:.1f}%<br>'
                )
                if customdata is not None and len(avail) >= 4:
                    htmpl += (
                        'Components used: %{customdata[0]}<br>'
                        'Proficiency need: %{customdata[1]:.1f}<br>'
                        'Growth need: %{customdata[2]:.1f}<br>'
                        'Recovery need: %{customdata[3]:.1f}<br>'
                    )
                    if len(avail) >= 5:
                        htmpl += 'Equity need: %{customdata[4]:.1f}<br>'
                htmpl += '<extra></extra>'
                fig_needs.add_trace(go.Scatter(
                    x=sub_ni['composite_needs_score'],
                    y=sub_ni['avg_proficiency_pct'],
                    mode='markers',
                    name=tier,
                    marker=dict(
                        color=NEEDS_TIER_COLORS.get(tier, '#999'),
                        size=8, opacity=0.8,
                        line=dict(width=0.5, color='#555'),
                    ),
                    text=sub_ni['School Name'],
                    customdata=customdata,
                    hovertemplate=htmpl,
                ))

        # Reference line: median needs score
        ni_valid = ni[ni['composite_needs_score'].notna()]
        if not ni_valid.empty:
            median_needs = float(ni_valid['composite_needs_score'].median())
            fig_needs.add_vline(
                x=median_needs, line_dash='dot', line_color='#aaa', line_width=1,
                annotation_text='Median',
                annotation_position='top right',
            )

        fig_needs.update_layout(
            title=(
                f'{subject} – School Needs Index (Composite vs. Avg Proficiency)'
                if subject else 'School Needs Index (Composite vs. Avg Proficiency)'
            ),
            xaxis_title='Composite Needs Score (0–100, higher = greater need)',
            yaxis_title='Avg Proficiency, All Students (%)',
            legend_title='Needs Tier',
            height=520,
        )

    if not fig_needs.data:
        fig_needs.update_layout(
            title='No needs index data – run src/school_needs_index.py'
        )

    # ── Ward-level performance bar+line chart ─────────────────────────────
    fig_ward = go.Figure()

    if not ward_summary.empty:
        ws = ward_summary.copy()
        if subject:
            ws = ws[ws['Subject'] == subject]

        if not ws.empty:
            ws = ws.sort_values('Ward')
            ward_labels = ws['Ward Label'] if 'Ward Label' in ws.columns else (
                'Ward ' + ws['Ward'].astype(str)
            )

            fig_ward.add_trace(go.Bar(
                name='Avg Proficiency (%)',
                x=ward_labels,
                y=ws['avg_proficiency_pct'],
                marker_color=[WARD_COLORS.get(int(w), '#42a5f5') for w in ws['Ward']],
                text=ws['avg_proficiency_pct'].round(1).astype(str) + '%',
                textposition='outside',
                yaxis='y',
            ))

            if 'avg_pp_growth' in ws.columns:
                fig_ward.add_trace(go.Scatter(
                    name='Avg Cohort Growth (pp)',
                    x=ward_labels,
                    y=ws['avg_pp_growth'],
                    mode='markers+lines',
                    marker=dict(size=10, color='#d32f2f'),
                    line=dict(color='#d32f2f', width=2),
                    yaxis='y2',
                ))

            fig_ward.update_layout(
                title=(
                    f'{subject} – Average Proficiency & Cohort Growth by DC Ward'
                    if subject else 'Average Proficiency & Cohort Growth by DC Ward'
                ),
                xaxis_title='DC Ward',
                yaxis=dict(title='Avg Proficiency (%)', side='left'),
                yaxis2=dict(
                    title='Avg Cohort Growth (pp)',
                    overlaying='y', side='right', zeroline=True,
                ),
                legend=dict(orientation='h', yanchor='bottom', y=1.02,
                            xanchor='right', x=1),
                height=420,
                barmode='group',
            )

    if not fig_ward.data:
        fig_ward.update_layout(
            title='No ward data – run src/ward_analysis.py'
        )

    # ── Equity Progress gap-change horizontal bar chart ───────────────────
    PROGRESS_COLORS = {
        'Narrowing': '#1a9641',
        'Stable': '#bdbdbd',
        'Widening': '#d7191c',
    }
    fig_equity_progress = go.Figure()

    if not equity_progress_summary_df.empty:
        ep = equity_progress_summary_df.copy()
        if subject:
            ep = ep[ep['Subject'] == subject]

        if not ep.empty:
            ep = ep.sort_values('gap_change_pp')

            colors = [
                PROGRESS_COLORS.get(d, '#bdbdbd')
                for d in ep['direction']
            ]

            first_yr = int(ep['first_year'].min()) if 'first_year' in ep.columns else ''
            last_yr = int(ep['last_year'].max()) if 'last_year' in ep.columns else ''

            fig_equity_progress.add_trace(go.Bar(
                x=ep['gap_change_pp'],
                y=ep['pair_label'],
                orientation='h',
                marker_color=colors,
                text=[
                    f"{v:+.1f} pp ({d})"
                    for v, d in zip(ep['gap_change_pp'], ep['direction'])
                ],
                textposition='outside',
                customdata=ep[['gap_first_pp', 'gap_last_pp',
                               'first_year', 'last_year',
                               'n_schools_first', 'n_schools_last']].values,
                hovertemplate=(
                    '<b>%{y}</b><br>'
                    f'Gap in %{{customdata[2]}}: %{{customdata[0]:+.1f}} pp<br>'
                    f'Gap in %{{customdata[3]}}: %{{customdata[1]:+.1f}} pp<br>'
                    'Change: %{x:+.2f} pp<br>'
                    'Schools (first year): %{customdata[4]}<br>'
                    'Schools (last year): %{customdata[5]}<br>'
                    '<extra></extra>'
                ),
            ))

            fig_equity_progress.add_vline(
                x=0, line_dash='solid', line_color='#555', line_width=1,
            )

            fig_equity_progress.update_layout(
                title=(
                    f'{subject} – Equity Gap Change: {first_yr}→{last_yr} '
                    f'(negative = gap narrowed)'
                    if subject else
                    f'Equity Gap Change: {first_yr}→{last_yr} (negative = gap narrowed)'
                ),
                xaxis_title='Gap Change (pp) — negative means equity improved',
                yaxis_title='Subgroup Pair (reference − comparison)',
                height=420,
            )

    if not fig_equity_progress.data:
        fig_equity_progress.update_layout(
            title='No equity progress data – run src/equity_progress_analysis.py'
        )

    return (
        fig_ts, fig_bars, fig_cohort_bars, fig_cohort_detail,
        fig_map, fig_equity_gaps, fig_equity_gap_change, fig_heatmap,
        fig_scatter, fig_geo, fig_yoy, fig_covid, fig_trajectory,
        fig_school_type, fig_grade_level, fig_subgroup, fig_consistency,
        fig_perf_index, fig_sector, fig_needs, fig_ward, fig_equity_progress,
    )


if __name__ == '__main__':
    if multi_year.empty:
        print("\nERROR: No data loaded!")
        print("Please run: python src/load_clean_data.py")
    else:
        print("\nStarting Dash app...")
        print("Open your browser to: http://127.0.0.1:8050/")
        app.run(debug=True)
