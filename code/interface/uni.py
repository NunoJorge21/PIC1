import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

# Constants
NUM_SAMPLES = 1024
FS = 25000  # Sampling frequency same as Arduino
HALF_SAMP_FREQ = 20000  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hz

location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}
freq_axis = np.linspace(0, HALF_SAMP_FREQ, num=int(HALF_SAMP_FREQ / SPECTRAL_RESOLUTION) + 1, endpoint=True).tolist()
frequency_responses = []

# Serial data processing functions
def sscanf(string, format_string):
    pattern = format_string.replace('%d', r'(-?\d+)').replace('%f', r'(-?\d+\.\d+)').replace('%s', r'(\S+)')
    match = re.match(pattern, string)
    if match:
        return match.groups()
    return None

def read_line(string, sensor_data):
    data = sscanf(string, "%s %d %d %d %d")
    if data is not None and data[0] == "S:":
        for i in range(1, 5):
            sensor_data.append(int(data[i]))

def read_data_from_serial(ser):
    sensor_data = []
    time_stamps = []
    gps_pattern = r"position:Lat: (-?\d+\.\d+), Lng: (-?\d+\.\d+)"
    sample_interval = 1 / FS
    sample_index = 0

    while True:
        try:
            line = ser.readline().strip().decode()
        except Exception as e:
            print(f"Error reading line: {e}")
            continue

        if re.match(gps_pattern, line):
            lat, lng = map(float, re.findall(gps_pattern, line)[0])
            print(f"Latitude: {lat}, Longitude: {lng}")
            location_intensity['Latitude'].append(lat)
            location_intensity['Longitude'].append(lng)
            continue

        if line == "finish":
            print("finished reading")
            break

        read_line(line, sensor_data)
        for j in range(4):
            time_stamps.append(sample_interval * (sample_index + j))
        sample_index += 4

    return np.array(time_stamps), np.array(sensor_data)

def compute_fft(sensor_data, sample_interval):
    Y = np.fft.fft(sensor_data)
    F1 = np.fft.fftfreq(NUM_SAMPLES, sample_interval)

    F = F1[:NUM_SAMPLES//2]
    power_spectrum = (2.0 / NUM_SAMPLES) * np.abs(Y[:NUM_SAMPLES//2])**2
    power_spectrum_dB = 10 * np.log10(power_spectrum)
    
    return F, power_spectrum_dB

def compute_sound_level_dB(signal_data):
    rms_value = np.sqrt(np.mean(np.square(signal_data)))
    dB_value = 20 * np.log10(rms_value)
    return dB_value

def plot_data(time_stamps, sensor_data, F, power_spectrum_dB, sound_level_dB):
    plt.figure(1, figsize=(10, 6))

    # Plot of the Audio
    plt.subplot(2, 1, 1)
    plt.plot(time_stamps, sensor_data)
    plt.title(f'Signal Recorded - Sound Level: {sound_level_dB:.2f} dB')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [V]')
    plt.grid(True)

    # Plot of the Density Power Spectrum
    plt.subplot(2, 1, 2)
    plt.plot(F, power_spectrum_dB)
    plt.title('Power Spectrum')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Power [dBW]')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# Dash app functions
def get_data_from_arduino(update=False):
    if not update:
        for _ in range(10):  # Initial data points
            latitude = np.random.uniform(38.736, 38.737)
            longitude = np.random.uniform(-9.138, -9.137)
            freq_data = np.random.uniform(-170, -100, size=len(freq_axis)).tolist()
            freq_data[100] = 20 + np.random.randint(-5, 5)  # Simulate some peak

            frequency_responses.append(freq_data)

            location_intensity['Latitude'].append(latitude)
            location_intensity['Longitude'].append(longitude)
            location_intensity['Intensity_dB'].append(max(freq_data))  # consider maximum intensity
    else:
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
            return f'/fourier_transform/button_{point_index + 1}'

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
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/':
            return html.Div([
                dcc.Graph(id='main-graph', figure=fig)
            ])
        elif pathname and pathname.startswith('/fourier_transform/'):
            try:
                button_id = pathname.split('/')[-1]
                button_index = int(button_id.split('_')[-1]) - 1
                return html.Div([
                    html.H3(f'Fourier Transform for {button_id}'),
                    dcc.Graph(
                        figure=go.Figure(
                            data=[
                                go.Scatter(
                                    x=freq_axis,
                                    y=frequency_responses[button_index]
                                )
                            ],
                            layout=go.Layout(
                                title=f'Fourier Transform for {button_id}',
                                xaxis=dict(title='Frequency [Hz]'),
                                yaxis=dict(title='Intensity [dB]')
                            )
                        )
                    )
                ])
            except IndexError:
                return html.Div("Invalid button index")
        return html.Div("404 Page Not Found")

    @app.callback(
        Output('main-graph', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_graph_live(n):
        df = get_data_from_arduino(update=True)
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

# Main function to run the app
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
