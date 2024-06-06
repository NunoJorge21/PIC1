import serial
import time
import numpy as np
import re
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import threading
from flask import Flask
from flask_socketio import SocketIO, emit
from datetime import datetime

NSAMP = 1024
FS = 25000  # Sampling frequency
HALF_SAMP_FREQ = 20000  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hz
location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': [], 'Timestamp': []}
freq_axis = np.linspace(0, HALF_SAMP_FREQ, num=int(HALF_SAMP_FREQ / SPECTRAL_RESOLUTION) + 1, endpoint=True).tolist()
frequency_responses = []

# Create Flask server and SocketIO
server = Flask(__name__)
socketio = SocketIO(server)

# Create Dash app
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, title='Smart Sound Monitoring')

def sscanf(string, format_string):
    pattern = format_string.replace('%d', r'(-?\d+)').replace('%f', r'(-?\d+\.\d+)').replace('%s', r'(\S+)')
    match = re.match(pattern, string)
    if match:
        return match.groups()

def read_line(string):
    data = sscanf(string, "%s %d %d %d %d")
    if data is not None and data[0] == "S:":
        return [int(data[i]) for i in range(1, 5)]
    return None

def read_stuff(ser):
    X, T = [], []
    lat_lng_data = []
    t_sample = 1 / FS
    i = 0

    while True:
        try:
            line = ser.readline().strip().decode()
        except serial.SerialException as e:
            print(f"Serial read error: {e}")
            break

        pattern = r"position:Lat: (-?\d+\.\d+), Lng: (-?\d+\.\d+)"
        match = re.match(pattern, line)
        if match:
            lat = float(match.group(1))
            lng = float(match.group(2))
            lat_lng_data.append((lat, lng))
            continue

        if line == "finish":
            break

        samples = read_line(line)
        if samples:
            X.extend(samples)
            T.extend([t_sample * (i + j) for j in range(4)])
            i += 4

    return np.array(X), np.array(T), lat_lng_data

def calculate_fft(X, t_sample):
    Y = np.fft.fft(X)
    F1 = np.fft.fftfreq(len(X), t_sample)
    F, S = [], []

    for i in range(len(F1)):
        if F1[i] < 0:
            break
        F.append(F1[i])
        S.append(2 * pow(abs(Y[i]) / len(X), 2) if i != 0 else pow(abs(Y[i]) / len(X), 2))
    
    S[-1] /= 2
    S_dB = 10 * np.log10(S)
    return np.array(F), np.array(S_dB)

def integrate_fft_in_db(X, fs):
    t_sample = 1 / fs
    F, S_dB = calculate_fft(X, t_sample)
    power_total = np.sum(10**(S_dB / 10))
    power_total_dB = 10 * np.log10(power_total)
    return power_total_dB

def get_data_from_arduino(ser):
    X, T, lat_lng_data = read_stuff(ser)
    if len(X) == NSAMP:
        F, S_dB = calculate_fft(X, 1/FS)
        power_dB = integrate_fft_in_db(X, FS)
        latitude, longitude = lat_lng_data[-1]  # Last position read
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        frequency_responses.append(S_dB.tolist())

        location_intensity['Latitude'].append(latitude)
        location_intensity['Longitude'].append(longitude)
        location_intensity['Intensity_dB'].append(power_dB)
        location_intensity['Timestamp'].append(timestamp)  # Add timestamp

        return pd.DataFrame(location_intensity)
    else:
        print(f"Received data length {len(X)} does not match NSAMP {NSAMP}")
        return pd.DataFrame(location_intensity)

def create_scattermapbox_trace(df, custom_colorscale):
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        print("Latitude and Longitude columns found")
        return go.Scattermapbox(
            lat=df['Latitude'],
            lon=df['Longitude'],
            mode='markers',
            marker=dict(
                size=20,
                color=df['Intensity_dB'],
                opacity=0.8,
                colorscale=custom_colorscale,
                cmin=0,  # Minimum dB level
                cmax=120,  # Maximum dB level
                showscale=True,
                colorbar=dict(
                    title='Intensity (dB)',
                    titleside='right',
                    ticks='outside',
                )
            ),
            text=[f'Time: {df["Timestamp"][i]}' for i in range(len(df))],  # Display timestamp
            customdata=[i for i in range(len(df))]
        )
    else:
        print("Latitude and Longitude columns not found")


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

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    create_navbar(),
    html.Div(id='page-content', style={'padding': '20px', 'marginTop': '56px'}),  # Add marginTop to account for fixed navbar
    dcc.Store(id='graph-data-store'),  # Store for the graph data
    # dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)  # Update every 10 seconds
])

def register_callbacks(app):
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
        [Output('link-home', 'active')],
        Input('url', 'pathname')
    )
    def update_active_links(pathname):
        if pathname == '/':
            return [True]
        return [False]

    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname'), Input('graph-data-store', 'data')]
    )
    def display_page(pathname, data):
        if data is None:
            df = pd.DataFrame(location_intensity)
        else:
            df = pd.DataFrame(data)
        
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
        return html.Div("404 Page Not Found")

def update_map(ser):
    while True:
        new_data = get_data_from_arduino(ser)
        if not new_data.empty and not new_data.equals(pd.DataFrame(location_intensity)):  # Check if new data is different
            socketio.emit('update-map', new_data.to_dict('records'))

@socketio.on('update-map')
def handle_update_map(data):
    socketio.emit('update-graph', {'data': data})

@app.callback(
    Output('graph-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('graph-data-store', 'data')
)
def update_graph_store(n_intervals, current_data):
    new_data = pd.DataFrame(location_intensity)
    current_df = pd.DataFrame(current_data) if current_data else pd.DataFrame()
    
    if not new_data.equals(current_df):  # Update only if new data is different
        return new_data.to_dict('records')
    
    return current_data

@app.callback(
    Output('main-graph', 'figure'),
    Input('graph-data-store', 'data')
)
def update_graph_live(data):
    df = pd.DataFrame(data)
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
    return fig

def main():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=100)
        time.sleep(2)
        
        register_callbacks(app)
        
        thread = threading.Thread(target=update_map, args=(ser,))
        thread.start()

        if __name__ == '__main__':
            socketio.run(server, debug=True, use_reloader=False, port=12056)

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

main()


