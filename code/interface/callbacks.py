# callbacks.py
from dash import Input, Output, State, html, dcc
import plotly.graph_objects as go
import dash_leaflet as dl
from data_processing import get_data_from_arduino
from layout import create_scattermapbox_trace, create_layout
import global_vars as gv


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
                                    x=gv.freq_axis[button_index],
                                    y=gv.frequency_responses[button_index]
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
        Input('data-update-trigger', 'data')
    )
    def update_graph_live(data):
        if gv.new_data_available:
            get_data_from_arduino()
            gv.new_data_available = False  # Reset the flag after reading data
            print(gv.df)  # Debug print to verify data frame content
        trace = create_scattermapbox_trace(gv.df, gv.custom_colorscale)
        layout = create_layout(gv.df)
        return go.Figure(data=[trace], layout=layout)
