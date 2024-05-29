##########
# FALTA:
#   -> estabelecimento de comunicações com gateway;
#       --> gerir ativação do programa de acordo com as comunicações
#   -> while loop para garantir continuidade nas atualizações da informação;
#       --> só acaba quando comunicações fecharem por completo ou utilizador fechar a janela 

import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback_context

HALF_SAMP_FREQ = 20000  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hz

<<<<<<< HEAD:0.interface/v4_main.py
# Função para simular dados do Arduino
=======
# Global variables
global location_intensity
global freq_axis
global frequency_responses

location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}

# Ensure that this is always true!
freq_axis = numpy.linspace(0, HALF_SAMP_FREQ, num=int(HALF_SAMP_FREQ / SPECTRAL_RESOLUTION) + 1, endpoint=True).tolist()
frequency_responses = []

>>>>>>> dece5d6 (Heatmap):0.interface/backup_main.py
def getDataFromArduino():
    latitude = 38.736667
    longitude = -9.13722
    freq_data = [-170] * 2001
    freq_data[100] = 20
<<<<<<< HEAD:0.interface/v4_main.py
    return pd.DataFrame({'Latitude': [latitude], 'Longitude': [longitude], 'Intensity_dB': [max(freq_data)]})

# Inicializar dados
df = getDataFromArduino()

# Layout principal
app = Dash(__name__, suppress_callback_exceptions=True, title='Smart Sound Monitoring')
=======

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

# Define the app layout
>>>>>>> dece5d6 (Heatmap):0.interface/backup_main.py
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    # Barra de navegação
    html.Div([
        html.Button("Sound Monitoring Scatter Map", id="scatter-button", style={'margin': '0 10px'}),
        html.Button("Layout Edit", id="layout-button", style={'margin': '0 10px'})
    ]),
    # Conteúdo das seções
    html.Div(id='page-content')
])

<<<<<<< HEAD:0.interface/v4_main.py
# Página do mapa de dispersão de monitoramento de som
scatter_map_page = html.Div([
    dcc.Graph(id='main-graph', figure={}, style={'height': '80vh'})  # Mapa de dispersão
])

# Página de edição de layout
layout_edit_page = html.Div([
    html.H3('Layout Edit'),
    # Conteúdo da edição de layout aqui
])

# Callback para atualizar a URL com base no clique nos botões de navegação
@app.callback(
    Output('url', 'pathname'),
    [Input('scatter-button', 'n_clicks'), Input('layout-button', 'n_clicks')]
)
def update_url(scatter_clicks, layout_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return '/'
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'scatter-button':
        return '/scatter-map'
    elif button_id == 'layout-button':
        return '/layout-edit'
=======
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
>>>>>>> dece5d6 (Heatmap):0.interface/backup_main.py
    return '/'

# Callback para exibir o conteúdo com base na URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_content(pathname):
    if pathname == '/scatter-map':
        return scatter_map_page
    elif pathname == '/layout-edit':
        return layout_edit_page
    else:
        return scatter_map_page  # Página padrão

# Callback para destacar o botão de navegação da seção atual
@app.callback(
    Output('scatter-button', 'style'),
    [Input('url', 'pathname')]
)
def highlight_button(pathname):
    if pathname == '/scatter-map':
        return {'margin': '0 10px', 'background-color': 'lightblue'}
    return {'margin': '0 10px'}

if __name__ == '__main__':
<<<<<<< HEAD:0.interface/v4_main.py
    app.run_server(debug=True, use_reloader=False, port=8055)
=======
    app.run_server(debug=True, use_reloader=False, port=8053)
>>>>>>> dece5d6 (Heatmap):0.interface/backup_main.py
