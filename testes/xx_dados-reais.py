#######################################################################
# Está funcional!!!
# A corrigir:
#   segunda janela (desenhos ou heatmap)
#   inicializar melhor a janela (tipo menor zoom e centrar em Portugal)
#   usar código improved_fred.py
#######################################################################

import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import numpy as np
import dash_leaflet as dl
import dash_leaflet.express as dlx
import serial
import time
import re
import threading

# Constants
HALF_SAMP_FREQ = 12500  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hz
NSAMP = 1024
NF = 512

# Globals
global custom_colorscale, X, T, F, S, S_dB, ser, lat, lng, location_intensity, freq_axis, frequency_responses, df, new_data_available
global data_buffer

# Initializing global variables
custom_colorscale = [
    [0, 'green'],
    [0.25, 'limegreen'],
    [0.5, 'yellow'],
    [0.75, 'orange'],
    [1, 'red']
]

# Data vectors
X, T, F, S, S_dB = [], [], [], [], []
ser = serial.Serial('/dev/ttyUSB2', 9600, timeout=100)
time.sleep(2)

# Global variables for data storage
location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}
freq_axis, frequency_responses = [], []
lat, lng = 0.0, 0.0
new_data_available = False  # Flag for new data availability
data_buffer = []  # Buffer to store data between "start" and "finish"

# DataFrame
df = pd.DataFrame(location_intensity)

# Helper functions for reading data
def sscanf(string, format_string):
    pattern = format_string.replace('%d', r'(-?\d+)').replace('%f', r'(-?\d+\.\d+)').replace('%s', r'(\S+)')
    match = re.match(pattern, string)
    if match:
        return match.groups()

def ReadLine(string):
    data = sscanf(string, "%s %d %d %d %d")
    if data and data[0] == "S:":
        for i in range(1, 5):
            X.append(int(data[i]))

def ReadStuff():
    global lat, lng, data_buffer, S_dB
    X.clear()
    T.clear()
    F.clear()
    S.clear()
    S_dB.clear()
    fs = 25000  # Sampling frequency
    tSample = 1 / fs
    i = 0
    for line in data_buffer:
        match = re.match(r"position:Lat: (-?\d+\.\d+), Lng: (-?\d+\.\d+)", line)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            continue
        ReadLine(line)
        for j in range(4):
            T.append(tSample * (i + j))
        i += 4

    # Bilateral Fourier Transform
    Y = np.fft.fft(X)
    F1 = np.fft.fftfreq(NSAMP, tSample)
    i = 0
    while F1[i] >= 0:
        F.append(F1[i])
        S.append(2 * pow(abs(Y[i]) / NSAMP, 2) if i else pow(abs(Y[i]) / NSAMP, 2))
        if S[i] == 0: S[i] = 0.00001
        i += 1
    S[i - 1] = S[i - 1]/2
    S_dB = (10 * np.log10(S)).tolist()


def get_data_from_arduino():
    global lat, lng, df, data_buffer, S_dB, freq_axis, frequency_responses
    ReadStuff()  # Process the data buffer
    data_buffer = []  # Clear the buffer after processing

    F_copy = F.copy()
    S_dB_copy = S_dB.copy()
    freq_axis.append(F_copy)
    frequency_responses.append(S_dB_copy)

    location_intensity['Latitude'].append(lat)
    location_intensity['Longitude'].append(lng)
    location_intensity['Intensity_dB'].append(max(S_dB))
    df = pd.DataFrame(location_intensity)

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
                ticks='outside'
            )
        ),
        text=[f'Button {i + 1}' for i in range(len(df))],
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
    global app, freq_axis, frequency_responses
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, title='Smart Sound Monitoring')
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        create_navbar(),
        html.Div(id='page-content', style={'padding': '20px', 'marginTop': '56px'}),
        dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0)
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
                                    x=freq_axis[button_index],
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
                return html.Div([
                    html.H3('Invalid button ID')
                ])
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

    @app.callback(
        Output('main-graph', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_graph_live(n_intervals):
        global new_data_available
        if new_data_available:
            get_data_from_arduino()
            new_data_available = False  # Reset the flag after reading data
        trace = create_scattermapbox_trace(df, custom_colorscale)
        layout = create_layout(df)
        return go.Figure(data=[trace], layout=layout)

def serial_read_thread():
    global new_data_available, data_buffer, lat, lng  # Ensure global variables are accessible

    def read_from_serial():
        while True:
            line = ser.readline()
            if line:
                line = line.strip().decode()
                if line == "start":
                    print("start reading\n")
                    data_buffer.clear()  # Clear the buffer at the start of new data
                elif line == "finish":
                    print("finish reading\n")
                    new_data_available = True  # Set the flag when new data is available
                    get_data_from_arduino()  # Call the function to process the received data
                else:
                    data_buffer.append(line)  # Buffer each line of data

    thread = threading.Thread(target=read_from_serial)
    thread.daemon = True  # Set the thread as a daemon so it terminates when the main program exits
    thread.start()  # Start the thread



def main():
    trace = create_scattermapbox_trace(df, custom_colorscale)
    layout = create_layout(df)
    fig = go.Figure(data=[trace], layout=layout)

    app = initialize_dash_app(fig)
    register_callbacks(app, fig)
    serial_read_thread()  # Call the serial_read_thread function to start the serial thread

    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader=False, port=1056)

main()