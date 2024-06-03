# serial_reader.py
# serial_reader.py
import threading
import serial
import time
import re
from data_processing import get_data_from_arduino
import global_vars as gv
from dash import callback_context, no_update
from dash.dependencies import Output, State

def serial_read_thread(app):
    def read_from_serial():
        while True:
            line = gv.ser.readline()
            if line:
                line = line.strip().decode()
                if line == "start":
                    print("Start reading")
                    gv.data_buffer.clear()  # Clear the buffer at the start of new data
                elif line == "finish":
                    print("Finish reading")
                    gv.new_data_available = True  # Set the flag when new data is available
                    get_data_from_arduino()  # Process the received data
                    app.server.app_context().push()
                    store_data = app.layout['data-update-trigger'].data
                    app.layout['data-update-trigger'].data = store_data + 1
                else:
                    gv.data_buffer.append(line)  # Buffer each line of data
                    print(f"Buffered line: {line}")

    thread = threading.Thread(target=read_from_serial)
    thread.daemon = True  # Set the thread as a daemon so it terminates when the main program exits
    thread.start()  # Start the thread
