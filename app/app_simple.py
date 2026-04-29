"""
Dash app for exploring DC school test scores.

Reads from the pre-cleaned combined_all_years.csv and cohort growth outputs.
Provides:
  - Time series & bar charts of school performance
  - Cohort growth analysis (Grade N → Grade N+1)
  - Map view (when school_locations.csv is available)
"""
import os
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

cohort_detail = pd.DataFrame()
cohort_summary = pd.DataFrame()
equity_summary = pd.DataFrame()
proficiency_trends = pd.DataFrame()
geo_equity = pd.DataFrame()
yoy_detail = pd.DataFrame()
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
        html.Small(
            "Run python src/yoy_growth_analysis.py to generate this data.",
            className="text-muted",
            id='yoy-note',
        ),
        html.Div(className="mt-1", children=[
            dcc.Graph(id='yoy-growth')
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
                import re as _re
                m = _re.search(r'\d+', str(g))
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
                import re as _re_yoy

                def _grade_key_yoy(g):
                    m = _re_yoy.search(r'\d+', str(g))
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

    return (
        fig_ts, fig_bars, fig_cohort_bars, fig_cohort_detail,
        fig_map, fig_equity_gaps, fig_equity_gap_change, fig_heatmap,
        fig_scatter, fig_geo, fig_yoy,
    )


if __name__ == '__main__':
    if multi_year.empty:
        print("\nERROR: No data loaded!")
        print("Please run: python src/load_clean_data.py")
    else:
        print("\nStarting Dash app...")
        print("Open your browser to: http://127.0.0.1:8050/")
        app.run(debug=True)
