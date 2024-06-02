import numpy as np
import pandas as pd
import re
import global_vars as gv

def sscanf(string, format_string):
    pattern = format_string.replace('%d', r'(-?\d+)').replace('%f', r'(-?\d+\.\d+)').replace('%s', r'(\S+)')
    match = re.match(pattern, string)
    if match:
        return match.groups()

def ReadLine(string):
    data = sscanf(string, "%s %d %d %d %d")
    if data and data[0] == "S:":
        print(f"Parsed data: {data}")  # Debug logging
        for i in range(1, 5):
            gv.X.append(int(data[i]))
        print(f"Updated gv.X: {gv.X[-4:]}")  # Debug logging

def ReadStuff():
    gv.X.clear()
    gv.T.clear()
    gv.F.clear()
    gv.S.clear()
    gv.S_dB.clear()
    fs = 25000  # Sampling frequency
    tSample = 1 / fs
    i = 0
    for line in gv.data_buffer:
        match = re.match(r"position:Lat: (-?\d+\.\d+), Lng: (-?\d+\.\d+)", line)
        if match:
            gv.lat, gv.lng = float(match.group(1)), float(match.group(2))
            print(f"Updated position: lat={gv.lat}, lng={gv.lng}")  # Debug logging
            continue
        ReadLine(line)
        for j in range(4):
            gv.T.append(tSample * (i + j))
        i += 4

    if not gv.X:
        print("Warning: No data in gv.X")
        return

    # Bilateral Fourier Transform
    Y = np.fft.fft(gv.X)
    F1 = np.fft.fftfreq(gv.NSAMP, tSample)
    i = 0
    while F1[i] >= 0:
        gv.F.append(F1[i])
        gv.S.append(2 * pow(abs(Y[i]) / gv.NSAMP, 2) if i else pow(abs(Y[i]) / gv.NSAMP, 2))
        if gv.S[i] == 0: gv.S[i] = 0.00001
        i += 1
    gv.S[i - 1] = gv.S[i - 1] / 2
    gv.S_dB = (10 * np.log10(gv.S)).tolist()

def get_data_from_arduino():
    ReadStuff()  # Process the data buffer
    gv.data_buffer = []  # Clear the buffer after processing

    if not gv.F:
        print("Warning: No frequency data (gv.F) computed")
        return
    if not gv.S_dB:
        print("Warning: No spectral data (gv.S_dB) computed")
        return

    F_copy = gv.F.copy()
    S_dB_copy = gv.S_dB.copy()
    gv.freq_axis.append(F_copy)
    gv.frequency_responses.append(S_dB_copy)

    gv.location_intensity['Latitude'].append(gv.lat)
    gv.location_intensity['Longitude'].append(gv.lng)
    gv.location_intensity['Intensity_dB'].append(max(gv.S_dB))
    gv.df = pd.DataFrame(gv.location_intensity)
