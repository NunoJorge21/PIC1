import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import re

NUM_SAMPLES = 1024
NF = 512
FS = 25000  # Sampling frequency same as Arduino

def sscanf(string, format_string):
    pattern = format_string.replace('%d', r'(-?\d+)').replace('%f', r'(-?\d+\.\d+)').replace('%s', r'(\S+)')
    match = re.match(pattern, string)
    if match:
        return match.groups()
    return None

def read_line(string, sensor_data):
    data = sscanf(string, "%s %d %d %d %d")
    if data is not None and data[0] == "S:":
        for i in range(1, 5):
            sensor_data.append(int(data[i]))

def read_data_from_serial(ser):
    sensor_data = []
    time_stamps = []
    gps_pattern = r"position:Lat: (-?\d+\.\d+), Lng: (-?\d+\.\d+)"
    sample_interval = 1 / FS
    sample_index = 0

    while True:
        try:
            line = ser.readline().strip().decode()
        except Exception as e:
            print(f"Error reading line: {e}")
            continue

        if re.match(gps_pattern, line):
            lat, lng = map(float, re.findall(gps_pattern, line)[0])
            print(f"Latitude: {lat}, Longitude: {lng}")
            continue

        if line == "finish":
            print("finished reading")
            break

        read_line(line, sensor_data)
        for j in range(4):
            time_stamps.append(sample_interval * (sample_index + j))
        sample_index += 4

    return np.array(time_stamps), np.array(sensor_data)

def compute_fft(sensor_data, sample_interval):
    Y = np.fft.fft(sensor_data)
    F1 = np.fft.fftfreq(NUM_SAMPLES, sample_interval)

    F = F1[:NUM_SAMPLES//2]
    power_spectrum = (2.0 / NUM_SAMPLES) * np.abs(Y[:NUM_SAMPLES//2])**2
    power_spectrum_dB = 10 * np.log10(power_spectrum)
    
    return F, power_spectrum_dB

def compute_sound_level_dB(signal_data):
    rms_value = np.sqrt(np.mean(np.square(signal_data)))
    dB_value = 20 * np.log10(rms_value)
    return dB_value

def plot_data(time_stamps, sensor_data, F, power_spectrum_dB, sound_level_dB):
    plt.figure(1, figsize=(10, 6))

    # Plot of the Audio
    plt.subplot(2, 1, 1)
    plt.plot(time_stamps, sensor_data)
    plt.title(f'Signal Recorded - Sound Level: {sound_level_dB:.2f} dB')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [V]')
    plt.grid(True)

    # Plot of the Density Power Spectrum
    plt.subplot(2, 1, 2)
    plt.plot(F, power_spectrum_dB)
    plt.title('Power Spectrum')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Power [dBW]')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def main():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=100)
        time.sleep(2)
    except Exception as e:
        print(f"Error opening serial port: {e}")
        return

    while True:
        line = ser.readline().strip().decode()
        if line == "start":
            print("start reading")
            time_stamps, sensor_data = read_data_from_serial(ser)
            sample_interval = 1 / FS
            F, power_spectrum_dB = compute_fft(sensor_data, sample_interval)
            sound_level_dB = compute_sound_level_dB(sensor_data)
            print(f"Sound Level: {sound_level_dB:.2f} dB")
            plot_data(time_stamps, sensor_data, F, power_spectrum_dB, sound_level_dB)
            break

    ser.close()

if __name__ == "__main__":
    main()
