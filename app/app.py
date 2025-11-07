import os
import sys
from typing import List, Optional

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Resolve paths
APP_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, '..'))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
INPUT_DIR = os.path.join(PROJECT_ROOT, 'input_data')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output_data')

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# Try to import the data loader from the processing script
try:
    import test_score_growth as tsg
except Exception:
    tsg = None


def load_multi_year() -> pd.DataFrame:
    if tsg is not None and hasattr(tsg, '_load_all_input'):
        try:
            df = tsg._load_all_input()  # type: ignore[attr-defined]
            if df is not None and not df.empty:
                return df
        except Exception:
            pass
    # Fallback: if the processing script didn't import, attempt to read the summary outputs
    # Note: This fallback has less granularity than the full multi_year dataset
    try:
        df = pd.read_csv(os.path.join(OUTPUT_DIR, 'school_growth_full.csv'))
        # Attempt to backfill essential fields
        if 'subgroup_value_std' not in df.columns and 'Subgroup Value' in df.columns:
            df['subgroup_value_std'] = df['Subgroup Value']
        if 'percent_value' not in df.columns and 'percent_2023' in df.columns:
            df['percent_value'] = df['percent_2023']
        if 'year' not in df.columns:
            # Not ideal; create a pseudo year column for latest
            df['year'] = pd.NA
        return df
    except Exception:
        return pd.DataFrame()


def try_load_school_locations() -> Optional[pd.DataFrame]:
    # Accept common filenames
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
                # Expect at least columns: School Name, Latitude, Longitude
                if all(c in df.columns for c in ['School Name', 'Latitude', 'Longitude']):
                    return df
            except Exception:
                continue
    return None


multi_year = load_multi_year()
locations_df = try_load_school_locations()

# Prepare filter options
YEARS: List[int] = sorted([int(y) for y in pd.to_numeric(multi_year['year'], errors='coerce').dropna().unique()]) if not multi_year.empty else []
SUBJECTS: List[str] = sorted([s for s in multi_year['Subject'].dropna().astype(str).unique()]) if 'Subject' in multi_year.columns else []
SUBGROUPS: List[str] = sorted([s for s in multi_year['subgroup_value_std'].dropna().astype(str).unique()]) if 'subgroup_value_std' in multi_year.columns else []
SCHOOLS: List[str] = sorted([s for s in multi_year['School Name'].dropna().astype(str).unique()]) if 'School Name' in multi_year.columns else []

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
    default_year_range = [max(min(YEARS), YEARS[-1] - 3), YEARS[-1]] if len(YEARS) >= 2 else [YEARS[0], YEARS[0]]
else:
    default_year_range = [0, 0]

app.layout = html.Div(
    className="container py-3",
    children=[
        html.H2("DC School Test Score Explorer"),
        html.Div(
            className="row g-3",
            children=[
                html.Div(className="col-md-3", children=[
                    html.Label("Subject"),
                    dcc.Dropdown(id='subject-dd', options=[{"label": s, "value": s} for s in SUBJECTS], value=default_subject, clearable=False)
                ]),
                html.Div(className="col-md-3", children=[
                    html.Label("Subgroup"),
                    dcc.Dropdown(id='subgroup-dd', options=[{"label": s, "value": s} for s in SUBGROUPS], value=default_subgroup, clearable=False)
                ]),
                html.Div(className="col-md-6", children=[
                    html.Label("Schools (optional)"),
                    dcc.Dropdown(id='schools-dd', options=[{"label": s, "value": s} for s in SCHOOLS], value=None, multi=True, placeholder="Select one or more schools or leave blank for all")
                ]),
            ]
        ),
        html.Div(className="mt-3", children=[
            html.Label("Years"),
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
            html.Div(className="col-lg-6", children=[dcc.Graph(id='timeseries')]),
            html.Div(className="col-lg-6", children=[dcc.Graph(id='bars')]),
        ]),
        html.Hr(),
        html.Div(children=[
            html.H5("Map (latest selected year)"),
            html.Small("Provide input_data/school_locations.csv with columns: School Name, Latitude, Longitude to enable mapping."),
            dcc.Graph(id='map')
        ])
    ]
)


def filter_data(subject: Optional[str], subgroup: Optional[str], schools: Optional[List[str]], year_range: List[int]) -> pd.DataFrame:
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
def update_figs(subject, subgroup, schools, year_range):
    schools = schools or []
    df = filter_data(subject, subgroup, schools, year_range)

    # Timeseries: average percent_value per school per year
    ts = (
        df.groupby(['School Name', 'year'], as_index=False)
          .agg(percent=('percent_value', 'mean'))
    )
    if schools:
        ts = ts[ts['School Name'].isin(schools)]
    fig_ts = px.line(ts, x='year', y='percent', color='School Name', markers=True,
                     title='Percent Meeting/Exceeding by Year')
    fig_ts.update_layout(yaxis_title='Percent', xaxis_title='Year')

    # Bars: latest year in range
    latest_year = year_range[1]
    bars = (df[df['year'] == latest_year]
            .groupby(['School Name'], as_index=False)
            .agg(percent=('percent_value', 'mean'))
           )
    bars = bars.sort_values('percent', ascending=False)
    if schools:
        bars = bars[bars['School Name'].isin(schools)]
    fig_bars = px.bar(bars, x='percent', y='School Name', orientation='h',
                      title=f'Latest Year {latest_year}: Percent Meeting/Exceeding')
    fig_bars.update_layout(xaxis_title='Percent', yaxis_title='School')

    # Map: join locations if available
    if locations_df is not None and not locations_df.empty:
        map_df = (df[df['year'] == latest_year]
                  .groupby(['School Name'], as_index=False)
                  .agg(percent=('percent_value', 'mean')))
        map_df = map_df.merge(locations_df[['School Name', 'Latitude', 'Longitude']], on='School Name', how='inner')
        # Drop rows without coordinates
        map_df = map_df.dropna(subset=['Latitude', 'Longitude'])
        # Ensure numeric
        map_df['Latitude'] = pd.to_numeric(map_df['Latitude'], errors='coerce')
        map_df['Longitude'] = pd.to_numeric(map_df['Longitude'], errors='coerce')
        map_df = map_df.dropna(subset=['Latitude', 'Longitude'])
        fig_map = px.scatter_mapbox(
            map_df,
            lat='Latitude', lon='Longitude', color='percent', size='percent',
            hover_name='School Name',
            color_continuous_scale='Viridis',
            size_max=20, zoom=10,
            title=f'Map {latest_year}: Percent Meeting/Exceeding'
        )
        fig_map.update_layout(mapbox_style='open-street-map')
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    else:
        # Empty map placeholder
        fig_map = px.scatter_mapbox(pd.DataFrame({'lat': [], 'lon': []}), lat='lat', lon='lon')
        fig_map.update_layout(mapbox_style='open-street-map',
                              title='Provide school_locations.csv to enable mapping',
                              margin=dict(l=0, r=0, t=40, b=0))

    return fig_ts, fig_bars, fig_map


if __name__ == '__main__':
    # Run app
    app.run_server(debug=True)
