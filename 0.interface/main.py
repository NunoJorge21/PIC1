import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback_context
import numpy

HALF_SAMP_FREQ = 20000  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hz

location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}

# Ensure that this is always true!
freq_axis = numpy.linspace(0, HALF_SAMP_FREQ, num=int(HALF_SAMP_FREQ / SPECTRAL_RESOLUTION) + 1, endpoint=True).tolist()
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

df = getDataFromArduino()

# Custom colorscale
custom_colorscale = [
    [0, 'green'],        # 0% corresponds to green
    [0.25, 'limegreen'], # 25% - lighter green
    [0.5, 'yellow'],     # 50% - yellow
    [0.75, 'orange'],    # 75% - orange
    [1, 'red']           # 100% corresponds to red
]

# Create a scattermapbox trace
trace = go.Scattermapbox(
    lat=df['Latitude'],
    lon=df['Longitude'],
    mode='markers',
    marker=dict(
        size=20,
        color=df['Intensity_dB'],
        opacity=0.8,
        colorscale=custom_colorscale,
        showscale=True,  # Show the colorbar
        colorbar=dict(
            title='Intensity (dB)',
            titleside='right',
            ticks='outside',
        )
    ),
    text=[f'Button {i+1}' for i in range(len(df))],
    customdata=[i for i in range(len(df))]  # Custom data to identify points
)

# Create a layout for the figure
layout = go.Layout(
    title='Sound Monitoring Scatter Map',
    mapbox=dict(
        center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
        zoom=18,
        style='carto-positron'
    ),
    margin=dict(r=0, t=50, l=0, b=10)
)

# Create the figure
fig = go.Figure(data=[trace], layout=layout)

# Initialize the Dash app with suppress_callback_exceptions=True
app = Dash(__name__, suppress_callback_exceptions=True, title='Smart Sound Monitoring')

    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        create_navbar(),
        html.Div(id='page-content', style={'padding': '20px', 'marginTop': '56px'}),  # Add marginTop to account for fixed navbar
        dcc.Interval(id='interval-component', interval=5000, n_intervals=0)  # Trigger updates every 5 seconds
    ])

# Callback to update the URL based on map click
@app.callback(
    Output('url', 'pathname'),
    Input('main-graph', 'clickData')
)


def update_url(clickData):
    if clickData is None:
        return '/'
    else:
        point_index = clickData['points'][0]['pointIndex']
        return f'/plot/button_{point_index + 1}'

# Callback to display content based on URL
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
            ),
            html.Button("Back to Main Map", id="back-button", n_clicks=0)
        ])
    return "404 Page Not Found"

# Callback to handle the back button
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('back-button', 'n_clicks'),
    prevent_initial_call=True
)

def go_back(n_clicks):
    return '/'

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False, port=8053)