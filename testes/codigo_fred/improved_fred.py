import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import re

NSAMP = 1024
FS = 25000  # Frequência de amostragem

def sscanf(string, format_string):
    pattern = format_string.replace('%d', r'(-?\d+)').replace('%f', r'(-?\d+\.\d+)').replace('%s', r'(\S+)')
    match = re.match(pattern, string)
    if match:
        return match.groups()

def read_line(string):
    data = sscanf(string, "%s %d %d %d %d")
    if data is not None and data[0] == "S:":
        return [int(data[i]) for i in range(1, 5)]
    return None

def read_stuff(ser):
    X, T = [], []
    lat_lng_data = []
    t_sample = 1 / FS
    i = 0

    while True:
        line = ser.readline().strip().decode()

        pattern = r"position:Lat: (-?\d+\.\d+), Lng: (-?\d+\.\d+)"
        match = re.match(pattern, line)
        if match:
            lat = float(match.group(1))
            lng = float(match.group(2))
            lat_lng_data.append((lat, lng))
            print(f"Latitude: {lat}, Longitude: {lng}")
            continue

        if line == "finish":
            print("Finished reading")
            break

        samples = read_line(line)
        if samples:
            X.extend(samples)
            T.extend([t_sample * (i + j) for j in range(4)])
            i += 4

    return np.array(X), np.array(T), lat_lng_data

def calculate_fft(X, t_sample):
    Y = np.fft.fft(X)
    F1 = np.fft.fftfreq(len(X), t_sample)
    F, S = [], []

    for i in range(len(F1)):
        if F1[i] < 0:
            break
        F.append(F1[i])
        S.append(2 * pow(abs(Y[i]) / len(X), 2) if i != 0 else pow(abs(Y[i]) / len(X), 2))
    
    S[-1] /= 2
    S_dB = 10 * np.log10(S)
    return np.array(F), np.array(S_dB)

def integrate_fft_in_db(X, fs):
    t_sample = 1 / fs
    F, S_dB = calculate_fft(X, t_sample)
    power_total = np.sum(10**(S_dB / 10))
    power_total_dB = 10 * np.log10(power_total)
    return power_total_dB

def plot_data(T, X, F, S_dB):
    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)
    plt.plot(T, X)
    plt.title('Signal Recorded')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [V]')
    plt.grid()
    plt.xlim(0, T[-1])

    plt.subplot(2, 1, 2)
    plt.plot(F, S_dB)
    plt.title('Power Spectrum')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Power [dBW]')
    plt.grid()
    plt.xlim(0, F[-1])

    plt.tight_layout()
    plt.show()

def main():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=100)
        time.sleep(2)

        while True:
            line = ser.readline().strip().decode()
            if line == "start":
                print("Start reading\n")
                X, T, lat_lng_data = read_stuff(ser)
                if len(X) == NSAMP:
                    F, S_dB = calculate_fft(X, 1/FS)
                    power_dB = integrate_fft_in_db(X, FS)
                    plot_data(T, X, F, S_dB)
                    print(f"Potência total do sinal em dB: {power_dB:.2f} dB")
                else:
                    print("Not enough samples received.")

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
