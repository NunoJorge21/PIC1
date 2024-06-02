import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np
import dash_leaflet as dl
import dash_leaflet.express as dlx

HALF_SAMP_FREQ = 20000  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hzpy

location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}
freq_axis = np.linspace(0, HALF_SAMP_FREQ, num=int(HALF_SAMP_FREQ / SPECTRAL_RESOLUTION) + 1, endpoint=True).tolist()
frequency_responses = []

def get_data_from_arduino():
    latitude = np.random.uniform(38.736, 38.737)
    longitude = np.random.uniform(-9.138, -9.137)
    freq_data = np.random.uniform(-170, -100, size=len(freq_axis)).tolist()
    freq_data[100] = 20 + np.random.randint(-5, 5)  # Simulate some peak

    frequency_responses.append(freq_data)

    location_intensity['Latitude'].append(latitude)
    location_intensity['Longitude'].append(longitude)
    location_intensity['Intensity_dB'].append(max(freq_data))  # consider maximum intensity

    return pd.DataFrame(location_intensity)

def create_scattermapbox_trace(df, custom_colorscale):
    return go.Scattermapbox(
        lat=df['Latitude'],
        lon=df['Longitude'],
        mode='markers',
        marker=dict(
            size=20,
            color=df['Intensity_dB'],
            opacity=0.8,
            colorscale=custom_colorscale,
            showscale=True,
            colorbar=dict(
                title='Intensity (dB)',
                titleside='right',
                ticks='outside',
            )
        ),
        text=[f'Button {i+1}' for i in range(len(df))],
        customdata=[i for i in range(len(df))]
    )

def create_layout(df):
    return go.Layout(
        title='Sound Monitoring Scatter Map',
        mapbox=dict(
            center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
            zoom=18,
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
        html.Div(id='page-content', style={'padding': '20px', 'marginTop': '56px'}),  # Add marginTop to account for fixed navbar
        dcc.Interval(id='interval-component', interval=5000, n_intervals=0)  # Trigger updates every 5 seconds
    ])

    return app

def register_callbacks(app, fig):
    @app.callback(
        Output('url', 'pathname'),
        Input('main-graph', 'clickData')
    )
    def update_url(clickData):
        if clickData is None:
            return '/'
        else:
            point_index = clickData['points'][0]['customdata']
            return f'/plot/button_{point_index + 1}'

    @app.callback(
        [Output('link-home', 'active'),
         Output('link-layout-edit', 'active')],
        Input('url', 'pathname')
    )
    def update_active_links(pathname):
        if pathname == '/':
            return True, False
        elif pathname == '/layout-edit':
            return False, True
        return False, False

    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/':
            return html.Div([
                dcc.Graph(id='main-graph', figure=fig)
            ])
        elif pathname and pathname.startswith('/plot/'):
            try:
                button_id = pathname.split('/')[-1]
                button_index = int(button_id.split('_')[-1]) - 1
                return html.Div([
                    html.H3(f'Displaying plot for {button_id}'),
                    dcc.Graph(
                        figure=go.Figure(
                            data=[
                                go.Scatter(
                                    x=freq_axis,
                                    y=frequency_responses[button_index]
                                )
                            ],
                            layout=go.Layout(
                                title=f'Plot for {button_id}',
                                xaxis=dict(title='Frequency [Hz]'),
                                yaxis=dict(title='Intensity [dB]')
                            )
                        )
                    )
                ])
            except IndexError:
                return html.Div("Invalid button index")
        elif pathname == '/layout-edit':
            return html.Div([
                html.H3('This is the Layout Edit page.'),
                html.Button('Draw New Sound Source', id='draw-button', n_clicks=0),
                dl.Map(center=[38.736667, -9.13722], zoom=18, children=[
                    dl.TileLayer(),
                    dl.FeatureGroup(id="feature-group", children=[
                        dl.EditControl(
                            id='edit-control',
                            draw={
                                "polyline": False,
                                "polygon": False,
                                "circle": False,
                                "marker": False,
                                "circlemarker": False,
                                "rectangle": True
                            },
                            edit={"remove": True}
                        )
                    ])
                ], style={'height': '600px'}),
                html.Div(id='draw-data')
            ])
        return html.Div("404 Page Not Found")

    @app.callback(
        Output('feature-group', 'children'),
        Input('draw-button', 'n_clicks'),
        State('feature-group', 'children')
    )
    def activate_draw_mode(n_clicks, children):
        if n_clicks > 0:
            return [
                dl.EditControl(
                    id='edit-control',
                    draw={
                        "polyline": False,
                        "polygon": False,
                        "circle": False,
                        "marker": False,
                        "circlemarker": False,
                        "rectangle": True
                    },
                    edit={"remove": True}
                )
            ]
        return children

    @app.callback(
        Output('draw-data', 'children'),
        Input('edit-control', 'geojson')
    )
    def show_draw_data(data):
        if data:
            return html.Pre(str(data))
        return "No drawings yet"

def main():
    df = get_data_from_arduino()  # Initial data points
    custom_colorscale = [
        [0, 'green'],
        [0.25, 'limegreen'],
        [0.5, 'yellow'],
        [0.75, 'orange'],
        [1, 'red']
    ]
    trace = create_scattermapbox_trace(df, custom_colorscale)
    layout = create_layout(df)
    fig = go.Figure(data=[trace], layout=layout)

    app = initialize_dash_app(fig)
    register_callbacks(app, fig)

    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader=False, port=8055)

main()