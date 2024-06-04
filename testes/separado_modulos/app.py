# app.py
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from layout import create_layout, create_navbar, create_scattermapbox_trace, initialize_dash_app
from callbacks import register_callbacks
from serial_reader import serial_read_thread
import global_vars as gv
import serial
import time

from layout import create_layout, create_navbar, create_scattermapbox_trace, initialize_dash_app
from callbacks import register_callbacks
from serial_reader import serial_read_thread
from data_processing import get_data_from_arduino
import global_vars as gv

def main():
    # Initialize serial port
    gv.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=100)
    time.sleep(2)  # Wait for the serial connection to establish

    trace = create_scattermapbox_trace(gv.df, gv.custom_colorscale)
    layout = create_layout(gv.df)
    fig = go.Figure(data=[trace], layout=layout)

    app = initialize_dash_app(fig)
    register_callbacks(app, fig)
    serial_read_thread(app)  # Call the serial_read_thread function with the app instance

    if __name__ == '__main__':
        app.run_server(debug=True, use_reloader=False, port=8067)

main()



