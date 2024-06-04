# global_vars.py
import pandas as pd

custom_colorscale = [
    [0, 'green'],
    [0.25, 'limegreen'],
    [0.5, 'yellow'],
    [0.75, 'orange'],
    [1, 'red']
]

# Data vectors
X, T, F, S, S_dB = [], [], [], [], []

# Serial port (adjust as needed)
ser = None
lat, lng = 0.0, 0.0

# Global variables for data storage
location_intensity = {'Latitude': [], 'Longitude': [], 'Intensity_dB': []}
freq_axis, frequency_responses = [], []
new_data_available = False  # Flag for new data availability
data_buffer = []  # Buffer to store data between "start" and "finish"

# DataFrame
df = pd.DataFrame(location_intensity)

# Constants
NSAMP = 1024  # Number of samples
HALF_SAMP_FREQ = 12500  # Half of the sampling frequency
SPECTRAL_RESOLUTION = 10  # Hz
NF = 512  # Number of frequencies
