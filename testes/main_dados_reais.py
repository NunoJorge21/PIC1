import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import numpy as np
import dash_leaflet as dl
import dash_leaflet.express as dlx
import serial
import time
import matplotlib.pyplot as p
import re
import threading

HALF_SAMP_FREQ = 12500  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hz
NSAMP = 1024
NF = 512

global X
global T
global F
global S
global ser
global lat
global lng
global location_intensity
global freq_axis
global frequency_responses
global df
global app  # Define app globally


# Data Vector
X = []  # Signal from Arduino
T = []  # Time Vector of the samples
F = []  # Frequency vector
S = []  # Power Spectrum

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=100)
time.sleep(2)

lat = 0.0
lng = 0.0

# Global variables
location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}
freq_axis = []
frequency_responses = []

df = pd.DataFrame(location_intensity)


def sscanf(string, format_string):
    pattern = format_string.replace('%d', r'(-?\d+)').replace('%f', r'(-?\d+\.\d+)').replace('%s', r'(\S+)')
    match = re.match(pattern, string)
    if match:
        return match.groups()


def ReadLine(string):
    i = 1
    data = sscanf(string, "%s %d %d %d %d")
    if data is not None and data[0] == "S:":
        for i in range(1, 5):
            X.append(int(data[i]))


def ReadStuff():
    X.clear()
    T.clear()
    F.clear()
    S.clear()
    fs = 25000  # sampling freq same as arduino
    tSample = 1 / fs
    i = 0
    # Read the points from arduino
    while 1:
        line = ser.readline()
        line = line.strip()
        line = line.decode()
        # Regular expression pattern to match the line and capture the latitude and longitude
        pattern = r"position:Lat: (-?\d+\.\d+), Lng: (-?\d+\.\d+)"

        # Use re.match to check if the line matches the pattern
        match = re.match(pattern, line)

        if match:
            # Extract latitude and longitude from the match groups
            lat = float(match.group(1))
            lng = float(match.group(2))
            print(f"Latitude: {lat}, Longitude: {lng}")
            continue

        if line == "finish":
            print("finished reading")
            break

        ReadLine(line)
        T.append(tSample * i)
        T.append(tSample * (i + 1))
        T.append(tSample * (i + 2))
        T.append(tSample * (i + 3))
        i = i + 4

    # Bilateral Fourier Transform
    Y = np.fft.fft(X)
    F1 = np.fft.fftfreq(NSAMP, tSample)

    # Conversion to unilateral
    i = 0
    while F1[i] >= 0:
        F.append(F1[i])
        if i == 0:
            S.append(pow(abs(Y[i]) / NSAMP, 2))
        else:
            S.append(2 * pow(abs(Y[i]) / NSAMP, 2))
        i = i + 1
    N_points = i
    S[N_points - 1] = S[N_points - 1] / 2
    del F1

    # Unilateral power spectrum
    S_dB = 10 * np.log10(S)

    # Plots
    p.figure(1, figsize=(10, 6))  # Tamanho customizável

    # Plot of the Audio
    p.subplot(2, 1, 1)
    p.plot(T, X)

    # Plot Information
    p.title('Signal Recorded')
    p.xlabel('Time [s]')
    p.ylabel('Amplitude [V]')  # Mudar para as devidas unidades
    p.grid()
    ax = p.gca()
    ax.set_xlim(0, T[NSAMP - 1])

    # Plot of the Density Power Spectrum
    p.subplot(2, 1, 2)

    # Plot options
    # p.plot(F, S) #Unidades lineares
    # p.semilogx(F,S) #Por década, Unidades lineares
    p.plot(F, S_dB)  # Unidades logarítmicas
    # p.semilogx(F,S_dB) #Por década, logarítmicas

    # Plot Information
    p.title('Power Spectrum')
    p.xlabel('Frequency [Hz]')
    p.ylabel('Power [dBW]')  # Unidades Lineares
    # p.ylabel('Power [dBW]') #Unidades logarítmicas
    p.grid()
    ax = p.gca()
    ax.set_xlim(0, F[N_points - 1])  # Linear
    # ax.set_xlim(0.1,F[N_points - 1]) #Décadas

    p.tight_layout()
    p.show()


def get_data_from_arduino():
    freq_axis.append(F)
    frequency_responses.append(S)

    print("Latitude:", lat)
    print("Longitude:", lng)

    location_intensity['Latitude'].append(lat)
    location_intensity['Longitude'].append(lng)
    location_intensity['Intensity_dB'].append(max(S))  # consider maximum intensity

    #return pd.DataFrame(location_intensity)
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
                ticks='outside',
            )
        ),
        text=[f'Button {i + 1}' for i in range(len(df))],
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
    global app  # Declare app as global to modify the global app object
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
               title='Smart Sound Monitoring')

    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        create_navbar(),
        html.Div(id='page-content', style={'padding': '20px', 'marginTop': '56px'}),  # Add marginTop to account for fixed navbar
        dcc.Store(id='store-trigger', data=0)  # Store component to trigger updates
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

    @app.callback(
        Output('main-graph', 'figure'),
        Input('store-trigger', 'data')
    )
    def update_graph_live(trigger):
        #df = get_data_from_arduino()
        get_data_from_arduino()
        trace = create_scattermapbox_trace(df, custom_colorscale)
        layout = create_layout(df)
        return go.Figure(data=[trace], layout=layout)


def serial_read_thread():
    global app  # Ensure app is recognized as a global variable
    update_signal = 0

    def read_from_serial():
        nonlocal update_signal
        while True:
            line = ser.readline()
            if line:
                line = line.strip()
                line = line.decode()
                if line == "start":
                    print("start reading\n")
                    update_signal += 1
                    app.server.call_action_callback(callback_id="store-trigger", prop_id="data", value=update_signal)

    thread = threading.Thread(target=read_from_serial)
    thread.daemon = True
    thread.start()


def main():
    global custom_colorscale

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
    serial_read_thread()

    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader=False, port=8055)


main()
