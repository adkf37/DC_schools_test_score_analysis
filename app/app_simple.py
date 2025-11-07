"""
Dash app for exploring DC school test scores.

Reads from the pre-cleaned combined_all_years.csv file.
"""
import os
import pandas as pd
import numpy as np
import plotly.express as px
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
        
        html.Div(className="row g-3 mt-3", children=[
            html.Div(className="col-lg-6", children=[
                dcc.Graph(id='timeseries')
            ]),
            html.Div(className="col-lg-6", children=[
                dcc.Graph(id='bars')
            ]),
        ]),
        
        html.Hr(),
        
        html.Div(children=[
            html.H5("School Locations Map (latest year)"),
            html.Small("Add input_data/school_locations.csv with columns: School Name, Latitude, Longitude to enable mapping.", className="text-muted"),
            dcc.Graph(id='map')
        ])
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
    Output('map', 'figure'),
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
        
        fig_map = px.scatter_mapbox(
            map_df,
            lat='Latitude', lon='Longitude',
            color='percent', size='percent',
            hover_name='School Name',
            hover_data={'Latitude': False, 'Longitude': False, 'percent': ':.1f'},
            color_continuous_scale='Viridis',
            size_max=20, zoom=10,
            title=f'{subject} - {latest_year}: School Performance Map'
        )
        fig_map.update_layout(mapbox_style='open-street-map')
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    else:
        # Empty map placeholder
        fig_map = px.scatter_mapbox(pd.DataFrame({'lat': [], 'lon': []}), lat='lat', lon='lon')
        fig_map.update_layout(
            mapbox_style='open-street-map',
            title='Add school_locations.csv to enable mapping',
            margin=dict(l=0, r=0, t=40, b=0)
        )
    
    return fig_ts, fig_bars, fig_map


if __name__ == '__main__':
    if multi_year.empty:
        print("\nERROR: No data loaded!")
        print("Please run: python src/load_clean_data.py")
    else:
        print("\nStarting Dash app...")
        print("Open your browser to: http://127.0.0.1:8050/")
        app.run_server(debug=True)
