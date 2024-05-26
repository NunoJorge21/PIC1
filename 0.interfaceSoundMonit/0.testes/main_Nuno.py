import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback_context
import numpy


HALF_SAMP_FREQ = 20000 # 20 kHz
SPECTRAL_RESOLUTION = 10 # Hz

global location_intensity
global freq_axis
global frequency_responses

location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}

###########################
# !!!!!!!!!!!!!!!!!!!!!!!!!
# Temos de ter a certeza de que isto é sempre verdade!
freq_axis = numpy.linspace(0, HALF_SAMP_FREQ, num=int(HALF_SAMP_FREQ/SPECTRAL_RESOLUTION)+1, endpoint=True).tolist()
frequency_responses = []


def getDataFromArduino():
    latitude = 38.736667
    longitude = -9.13722
    freq_data = [-170]*2001
    freq_data[100] = 20

    frequency_responses.append(freq_data)

    location_intensity['Latitude'].append(latitude)
    location_intensity['Longitude'].append(longitude)
    location_intensity['Intensity_dB'].append(max(freq_data)) # consider maximum intensity
    
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
    customdata=[i for i in range(len(df))]  # Custom data to identify buttons
)

# Create a layout for the figure
layout = go.Layout(
    title='Sound Monitoring Scatter Map',
    mapbox=dict(
        center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
        zoom=18,
        #style='open-street-map'
        style='carto-positron'
    ),
    margin=dict(r=0, t=50, l=0, b=10)
)

# Create the figure
fig = go.Figure(data=[trace], layout=layout)

# Initialize the Dash app with suppress_callback_exceptions=True
app = Dash(__name__, suppress_callback_exceptions=True)

# Define the app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to update the URL based on button click
@app.callback(
    Output('url', 'pathname'),
    [Input(f'Button_{i+1}', 'n_clicks') for i in range(len(df))]
)
def update_url(*args):
    ctx = callback_context
    if not ctx.triggered:
        return '/'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return f'/plot/{button_id}'

# Callback to display content based on URL
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/':
        return html.Div([
            dcc.Graph(id='main-graph', figure=fig),
            html.Div(id='Button_container', children=[
                html.Button(f'Button {i+1}', id=f'Button_{i+1}', n_clicks=0) for i in range(len(df))
            ])
        ])
    elif pathname and pathname.startswith('/plot/'):
        button_id = pathname.split('/')[-1]
        button_index = button_id.split('_')[-1]
        return html.Div([
            html.H3(f'Displaying plot for {button_id}'),
            dcc.Graph(
                figure=go.Figure(
                    data=[
                        go.Scatter(
                            x=freq_axis,
                            y=frequency_responses[int(button_index)-1]
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
    app.run_server(debug=True, use_reloader=False)