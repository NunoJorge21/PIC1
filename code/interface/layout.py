# layout.py
from dash import Dash, dcc, html
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

def create_scattermapbox_trace(df, custom_colorscale):
    if df.empty:
        return go.Scattermapbox()
    max_intensity = df['Intensity_dB'].max()
    min_intensity = df['Intensity_dB'].min()
    
    return go.Scattermapbox(
        lat=df['Latitude'],
        lon=df['Longitude'],
        mode='markers',
        marker=dict(
            size=15,  # Increased marker size for better visibility
            color=df['Intensity_dB'],
            opacity=0.9,
            colorscale=custom_colorscale,
            showscale=True,
            colorbar=dict(
                title='Intensity (dB)',
                titleside='right',
                ticks='outside'
            ),
            cmin=min_intensity,  # Set color scale min value
            cmax=max_intensity  # Set color scale max value
        ),
        text=[f'Button {i + 1}: {intensity} dB' for i, intensity in enumerate(df['Intensity_dB'])],
        customdata=[i for i in range(len(df))]
    )

def create_layout(df, zoom=18):
    return go.Layout(
        title='Sound Monitoring Scatter Map',
        mapbox=dict(
            center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
            zoom=zoom,
            style='carto-positron'
        ),
        margin=dict(r=0, t=0, l=0, b=0),
        height=800
    )

def create_navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand("Sound Monitoring", href="/", className="ms-2"),
                dbc.Nav(
                    [
                        dbc.NavLink("Sound Monitoring Scatter Map", href="/", id="link-home", className="me-2"),
                        dbc.NavLink("Layout Edit", href="/layout-edit", id="link-layout-edit", className="me-2"),
                    ],
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="lightblue",
        dark=False,
        className="mb-4",
        fixed="top",
    )

def initialize_dash_app(fig):
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, title='Smart Sound Monitoring')
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        create_navbar(),
        html.Div(id='page-content', style={'padding': '20px', 'marginTop': '56px'}),
        dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0)  # Update every second
    ])
    return app

