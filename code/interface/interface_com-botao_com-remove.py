#################################
# Versão final da interface!

    # Botão para acrescentar os pontos
    # para evitar atualizações peiódicas da página 
        # (não dá para mostrar mensagens que indicam início e fim da leitura)
    # Cada ponto tem um botã de remove associado


    # A FAZER:
        # na janela de plot, substituir botões atuais por "Back" (volta à janela do mapa)
        # atualização automática com novos pontos

# 27/07/2024
#################################

import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
import numpy as np
import threading
import serial
import re
import time
import MEMS_calibration

# Constants
HALF_SAMP_FREQ = 12500  # 25 kHz
SPECTRAL_RESOLUTION = 10  # Hz
NSAMP = 1024
NF = 512

# Globals
custom_colorscale = [
    [0, 'green'],
    [0.25, 'limegreen'],
    [0.5, 'yellow'],
    [0.75, 'orange'],
    [1, 'red']
]

X, T, F, S, S_dB = [], [], [], [], []
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=100)
time.sleep(2)

location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}
freq_axis, frequency_responses = [], []
lat, lng = 0.0, 0.0
new_data_available = False
data_buffer = []
collecting_data = False

df = pd.DataFrame(location_intensity)


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

    Y = np.fft.fft(X)
    F1 = np.fft.fftfreq(NSAMP, tSample)
    i = 0
    while F1[i] >= 0:
        F.append(F1[i])
        S.append(2 * pow(abs(Y[i]) / NSAMP, 2) if i else pow(abs(Y[i]) / NSAMP, 2))
        if S[i] == 0:
            S[i] = 0.00001
        i += 1
    S[i - 1] = S[i - 1] / 2
    S_dB = MEMS_calibration.S_to_dbSPL(S)


def get_data_from_arduino():
    global lat, lng, df, data_buffer, S_dB, freq_axis, frequency_responses, new_data_available
    ReadStuff()
    data_buffer = []

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

    new_data_available = False


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
        text=[f'Intensity: {intensity:.2f} dB, Button {i + 1}' for i, intensity in enumerate(df['Intensity_dB'])],
        customdata=[i for i in range(len(df))]
    )


def create_layout(df, zoom=12, center_lat=None, center_lon=None):
    if center_lat is None or center_lon is None:
        center_lat = 38.75
        center_lon = -9.15
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
                    [
                        dbc.NavItem(dbc.Button("Recenter", id='recenter-button', color="primary", className="me-1")),
                        dbc.NavItem(dbc.Button("Start Data Collection", id='start-data-button', color="primary", className="me-1")),
                    ],
                    className="ms-auto",
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


def initialize_dash_app():
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
               title='Smart Sound Monitoring')
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        create_navbar(),
        html.Div(id='page-content', style={'padding': '20px', 'marginTop': '56px'}),
    ])
    return app


def register_callbacks(app):
    @app.callback(
        Output('main-graph', 'figure'),
        Input('recenter-button', 'n_clicks'),
        Input('start-data-button', 'n_clicks'),
        Input('main-graph', 'relayoutData'),
        Input({'type': 'remove-button', 'index': ALL}, 'n_clicks')
    )
    def update_graph_live(recenter_clicks, start_data_clicks, relayout_data, remove_button_clicks):
        global new_data_available, df, freq_axis, frequency_responses, location_intensity

        ctx = callback_context
        if not ctx.triggered:
            trigger_id = None
        else:
            trigger_id = ctx.triggered[0]['prop_id']

        zoom = 12
        center_lat = None
        center_lon = None

        # Handle map relayout data
        if relayout_data is not None and ('mapbox.zoom' in relayout_data or 'mapbox.center' in relayout_data):
            zoom = relayout_data.get('mapbox.zoom', 12)
            center = relayout_data.get('mapbox.center', None)
            if center is not None:
                center_lat = center['lat']
                center_lon = center['lon']

        # Handle start data button click
        if trigger_id == 'start-data-button.n_clicks':
            if start_data_clicks and new_data_available:
                get_data_from_arduino()

        # Handle recenter button click
        if trigger_id == 'recenter-button.n_clicks' or trigger_id is None:
            zoom = 11
            center_lat = 38.75
            center_lon = -9.15

        # Handle remove button click
        if remove_button_clicks:
            indices_to_remove = [index for index, clicks in enumerate(remove_button_clicks) if clicks]
            indices_to_remove.sort(reverse=True)  # Remove in reverse order to avoid index errors
            for index in indices_to_remove:
                if index < len(df):
                    freq_axis.pop(index)
                    frequency_responses.pop(index)

                    location_intensity['Latitude'].pop(index)
                    location_intensity['Longitude'].pop(index)
                    location_intensity['Intensity_dB'].pop(index)

            df = pd.DataFrame(location_intensity)

        layout = create_layout(df, zoom=zoom, center_lat=center_lat, center_lon=center_lon)
        trace = create_scattermapbox_trace(df, custom_colorscale)
        fig = go.Figure(data=[trace], layout=layout)

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
                dcc.Graph(id='main-graph'),
                html.H3("Remove buttons:"),
                html.Div(id='button-container')
            ])
        elif pathname and pathname.startswith('/plot/'):
            try:
                button_id = pathname.split('/')[-1]
                button_index = int(button_id.split('_')[-1]) - 1
                return html.Div([
                    html.H3(f'Frequency response for {button_id}'),
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

    @app.callback(
        Output('button-container', 'children'),
        Input('main-graph', 'figure')
    )
    def update_buttons(figure):
        buttons = []
        for i in range(len(df)):
            buttons.append(dbc.Button(f"Remove Button {i+1}", id={'type': 'remove-button', 'index': i}, color="danger", className="me-1"))
        return buttons
    

def serial_read_thread():
    global new_data_available, data_buffer, lat, lng, collecting_data

    def read_from_serial():
        global new_data_available, data_buffer, lat, lng, collecting_data

        while True:
            line = ser.readline()
            if line:
                line = line.strip().decode()
                
                if line == "start":
                    print("Start reading")
                    data_buffer.clear()
                    collecting_data = True
                elif line == "finish":
                    print("Finish reading")
                    collecting_data = False
                    new_data_available = True
                elif collecting_data:
                    data_buffer.append(line)

    thread = threading.Thread(target=read_from_serial)
    thread.daemon = True
    thread.start()


def main():
    app = initialize_dash_app()
    register_callbacks(app)
    serial_read_thread()

    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader=False, port=8055)

main()
