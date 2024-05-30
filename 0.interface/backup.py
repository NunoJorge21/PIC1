import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback_context
import numpy as np
from scipy.ndimage import gaussian_filter
import plotly.colors


HALF_SAMP_FREQ = 20000  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hz

# Global variables
global location_intensity
global freq_axis
global frequency_responses

location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}

# Ensure that this is always true!
freq_axis = np.linspace(0, HALF_SAMP_FREQ, num=int(HALF_SAMP_FREQ / SPECTRAL_RESOLUTION) + 1, endpoint=True).tolist()
frequency_responses = []

def getDataFromArduino(lat, lon, dB):
    latitude = lat
    longitude = lon
    freq_data = [-170] * 2001
    freq_data[100] = dB

    frequency_responses.append(freq_data)

    location_intensity['Latitude'].append(latitude)
    location_intensity['Longitude'].append(longitude)
    location_intensity['Intensity_dB'].append(max(freq_data))  # consider maximum intensity

    return pd.DataFrame(location_intensity)

# Add multiple data points
df = getDataFromArduino(38.736667, -9.13722, 20)
df = getDataFromArduino(38.7367, -9.1372, -40)
df = getDataFromArduino(38.7368, -9.1373, 10)
df = getDataFromArduino(38.7369, -9.1374, 30)

# Normalize Intensity_dB for marker sizes
min_size = 10
max_size = 30
df['Normalized_Size'] = np.interp(df['Intensity_dB'], (df['Intensity_dB'].min(), df['Intensity_dB'].max()), (min_size, max_size))

# Custom colorscale
custom_colorscale = [
    [0, 'green'],        # 0% corresponds to green
    [0.25, 'limegreen'], # 25% - lighter green
    [0.5, 'yellow'],     # 50% - yellow
    [0.75, 'orange'],    # 75% - orange
    [1, 'red']           # 100% corresponds to red
]

# Function to map intensity values to colors
def map_intensity_to_color(intensity, colorscale):
    scale_values, scale_colors = zip(*colorscale)
    # Find the index of the nearest intensity value in the scale
    idx = np.abs(np.array(scale_values) - intensity).argmin()
    # Return the corresponding color
    return scale_colors[idx]


# Function to create Gaussian blobs for each point
def create_gaussian_blobs(df, lat_range, lon_range, grid_size=(200, 200), sigma=5, threshold=0.05):
    blobs = []
    for _, row in df.iterrows():
        lat_idx = np.searchsorted(lat_range, row['Latitude'])
        lon_idx = np.searchsorted(lon_range, row['Longitude'])
        grid = np.zeros(grid_size)
        grid[lat_idx, lon_idx] = row['Intensity_dB']
        blob = gaussian_filter(grid, sigma=sigma)
        blob[blob < threshold] = 0  # Apply the threshold
        blobs.append(blob)
    return blobs

# Adjust the range to a smaller area around the data points
lat_range = np.linspace(df['Latitude'].min() - 0.001, df['Latitude'].max() + 0.001, 200)
lon_range = np.linspace(df['Longitude'].min() - 0.001, df['Longitude'].max() + 0.001, 200)
blobs = create_gaussian_blobs(df, lat_range, lon_range)

# Create a scattermapbox trace for the main graph
scatter_trace = go.Scattermapbox(
    lat=df['Latitude'],
    lon=df['Longitude'],
    mode='markers',
    marker=dict(
        size=df['Normalized_Size'],
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
    text=[f'Intensity: {intensity} dB' for intensity in df['Intensity_dB']],
    hoverinfo='text'
)

# Create the layout for the scatter map
scatter_layout = go.Layout(
    title='Sound Monitoring Scatter Map',
    mapbox=dict(
        center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
        zoom=18,
        style='carto-positron'
    ),
    margin=dict(r=0, t=50, l=0, b=10)
)

# Create the scatter map figure
scatter_fig = go.Figure(data=[scatter_trace], layout=scatter_layout)


# Create scatter traces for each Gaussian blob
heatmap_traces = []
for i, blob in enumerate(blobs):
    lat_idx, lon_idx = np.where(blob > 0)
    lat_values = lat_range[lat_idx]
    lon_values = lon_range[lon_idx]
    intensity_values = blob[lat_idx, lon_idx]
    
    # Determine the color of each point based on intensity
    color_values = [map_intensity_to_color(val, custom_colorscale) for val in intensity_values]

    heatmap_traces.append(go.Scattermapbox(
        lat=lat_values,
        lon=lon_values,
        mode='markers',
        marker=dict(
            size=10,
            color=color_values,
            opacity=0.3,  # Decreased opacity
            colorscale=custom_colorscale,
            showscale=False  # Hide individual colorbars
        ),
        hoverinfo='none'
    ))

# Create the layout for the heatmap
heatmap_layout = go.Layout(
    title='Sound Monitoring Heatmap',
    mapbox=dict(
        center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
        zoom=18,
        style='carto-positron'
    ),
    margin=dict(r=0, t=50, l=0, b=10)
)

# Create the heatmap figure
heatmap_fig = go.Figure(data=heatmap_traces, layout=heatmap_layout)

# Initialize the Dash app with suppress_callback_exceptions=True
app = Dash(__name__, suppress_callback_exceptions=True, title='Smart Sound Monitoring')

# Define the app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to update the URL based on map click
@app.callback(
    Output('url', 'pathname'),
    Input('main-graph', 'clickData'),
    Input('switch-button', 'n_clicks')
)
def update_url(clickData, n_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return '/'
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'main-graph' and clickData is not None:
        point_index = clickData['points'][0]['pointIndex']
        return f'/plot/button_{point_index + 1}'
    elif trigger_id == 'switch-button':
        return '/heatmap'
    return '/'

# Callback to display content based on URL
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/':
        return html.Div([
            dcc.Graph(id='main-graph', figure=scatter_fig),
            html.Button("Switch to Heatmap View", id="switch-button", n_clicks=0)
        ])
    elif pathname == '/heatmap':
        return html.Div([
            dcc.Graph(id='heatmap-graph', figure=heatmap_fig),
            html.Button("Back to Main Map", id="back-button", n_clicks=0)
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
    app.run_server(debug=True, use_reloader=False, port=8051)