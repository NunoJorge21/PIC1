#################################
# Versão final da interface!

    # A fazer:
        # inicialização
        # botão para recentrar
#################################

import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import numpy as np
import dash_leaflet as dl
import serial
import time
import re
import threading
import MEMS_calibration

# Constants
HALF_SAMP_FREQ = 12500  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hz
NSAMP = 1024
NF = 512

# Globals
global custom_colorscale, X, T, F, S, S_dB, ser, lat, lng, location_intensity, freq_axis, frequency_responses, df, new_data_available
global data_buffer, collecting_data

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
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=100)
time.sleep(2)

# Global variables for data storage
location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}
freq_axis, frequency_responses = [], []
lat, lng = 0.0, 0.0
new_data_available = False  # Flag for new data availability
data_buffer = []  # Buffer to store data between "start" and "finish"
collecting_data = False  # Flag to indicate data collection state

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
        match = re.match(r"position:L:(-?\d+\.\d+),(-?\d+\.\d+)", line)
        if match:
            lat, lng = float(match.group(1)), float(match.group(2))
            continue
        ReadLine(line)
        for j in range(4):
            T.append(tSample * (i + j))
        i += 4


    if not X:
        print("Warning: X array is empty. Skipping FFT computation.")
        return

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
    #S_dB = (10 * np.log10(S)).tolist()
    S_dB = MEMS_calibration.S_to_dbSPL(S)

def get_data_from_arduino():
    global lat, lng, df, data_buffer, S_dB, freq_axis, frequency_responses
    ReadStuff()  # Process the data buffer
    data_buffer = []  # Clear the buffer after processing

    if not S_dB:
        print("Warning: S_dB array is empty. Skipping data update.")
        return

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
            cmin=-30,
            cmax=130,
            showscale=True,
            colorbar=dict(
                title='Intensity (dB)',
                titleside='right',
                ticks='outside'
            )
        ),
        text=[f'Button {i + 1}' for i in range(len(df))],
        #text=[f'Intensity: {round(df['Intensity_dB'][i], 1)} dB; Button {i + 1}' for i in range(len(df))],
        customdata=[i for i in range(len(df))]
    )

def create_layout(df, zoom=12, center_lat=None, center_lon=None):
    if center_lat is None or center_lon is None:
        center_lat = df['Latitude'].mean()  # Default center latitude
        center_lon = df['Longitude'].mean()  # Default center longitude
    return go.Layout(
        mapbox=dict(
            center=dict(lat=center_lat, lon=center_lon),
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
                dbc.NavbarBrand("Smart Sound Monitoring", href="/", className="ms-2"),
                dbc.Nav(
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
        dcc.Interval(id='interval-component', interval=1 * 1000, n_intervals=0),
        dcc.Graph(id='main-graph', figure=fig)  # Add the graph directly to the layout
    ])
    return app

def register_callbacks(app, fig):
    global new_data_available
    
    @app.callback(
        Output('main-graph', 'figure'),
        Input('interval-component', 'n_intervals'),
        Input('main-graph', 'relayoutData')  # Listen to changes in the layout data
    )
    def update_graph_live(n_intervals, relayout_data):
        global new_data_available

        # Check if relayoutData is not None and contains zoom or center information
        if relayout_data is not None and ('mapbox.zoom' in relayout_data or 'mapbox.center' in relayout_data):
            # Extract zoom level and center coordinates from relayoutData
            zoom = relayout_data.get('mapbox.zoom', 12)  # Default zoom level
            center = relayout_data.get('mapbox.center', None)
            if center is not None:
                center_lat = center['lat']
                center_lon = center['lon']
            else:
                center_lat = None
                center_lon = None
        else:
            # Use default values if relayoutData is None or does not contain relevant information
            zoom = 12  # Default zoom level
            center_lat = None  # Default center latitude
            center_lon = None

        # Check if the interval component triggered the callback
        ctx = callback_context
        if not ctx.triggered:
            trigger_id = None
        else:
            trigger_id = ctx.triggered[0]['prop_id']

        # Update map layout with new zoom level and center
        layout = create_layout(df, zoom=zoom, center_lat=center_lat, center_lon=center_lon)

        # Update map figure
        trace = create_scattermapbox_trace(df, custom_colorscale)
        fig = go.Figure(data=[trace], layout=layout)

        # If the interval component triggered the callback, update the data from Arduino
        if trigger_id == 'interval-component.n_intervals':
            global new_data_available
            if new_data_available:
                get_data_from_arduino()
                new_data_available = False  # Reset the flag after reading data

        return fig

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
        Output('link-home', 'active'),
        Input('url', 'pathname')
    )
    def update_active_links(pathname):
        if pathname == '/':
            return True
        return False

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
        return html.Div("404 Page Not Found")


def serial_read_thread():
    global new_data_available, data_buffer, lat, lng, collecting_data  # Ensure global variables are accessible

    def read_from_serial():
        global new_data_available, data_buffer, lat, lng, collecting_data  # Ensure global variables are accessible

        while True:
            line = ser.readline()
            if line:
                line = line.strip().decode()
                if line == "start":
                    print("Start reading")
                    data_buffer.clear()  # Clear the buffer at the start of new data
                    collecting_data = True
                elif line == "finish":
                    print("Finish reading")
                    collecting_data = False
                    new_data_available = True  # Set the flag when new data is available
                elif collecting_data:
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
        app.run_server(debug=True, use_reloader=False, port=8055)

main()