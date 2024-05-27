import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback_context

HALF_SAMP_FREQ = 20000  # 20 kHz
SPECTRAL_RESOLUTION = 10  # Hz

# Função para simular dados do Arduino
def getDataFromArduino():
    latitude = 38.736667
    longitude = -9.13722
    freq_data = [-170] * 2001
    freq_data[100] = 20
    return pd.DataFrame({'Latitude': [latitude], 'Longitude': [longitude], 'Intensity_dB': [max(freq_data)]})

# Inicializar dados
df = getDataFromArduino()

# Layout principal
app = Dash(__name__, suppress_callback_exceptions=True, title='Smart Sound Monitoring')
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
    app.run_server(debug=True, use_reloader=False, port=8055)
