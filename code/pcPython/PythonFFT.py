import serial
import time
import numpy as np
import matplotlib.pyplot as p
import re

NSAMP = 1024
NF = 512

def sscanf(string, format_string):
    pattern = format_string.replace('%d', r'(-?\d+)').replace('%f', r'(-?\d+\.\d+)').replace('%s', r'(\S+)')
    match = re.match(pattern, string)
    if match:
        return match.groups()



def ReadLine(string):
    i = 1
    data = sscanf(string, "%s %d %d %d %d")
    print(data)
    if data is not None and data[0] == "S:":
        for i in range(1,5):
            X.append(int(data[i]))

def ReadStuff():
    X.clear()
    T.clear()
    F.clear()
    S.clear()
    fs = 25000  #sampling freq same as arduino
    tSample = 1/fs
    i = 0
    # Read the points from arduino
    while 1:
        line = ser.readline()
        line = line.strip()
        line = line.decode()
        if line == "finish": 
            print("finished reading")
            break
        
        ReadLine(line)
        T.append(tSample*i)
        T.append(tSample*(i+1))
        T.append(tSample*(i+2))
        T.append(tSample*(i+3))
        i = i + 4
    print(len(X))
    print(len(T))

    #Bilateral Fourier Transform
    Y = np.fft.fft(X)
    F1 = np.fft.fftfreq(NSAMP, tSample)

    # Conversion to unilateral
    i = 0
    while(F1[i] >= 0): #Curiosamente, a função fft.fftfreq ordena o vetor F1 com as frequência positivas primeiro, seguidas das negativas. Além disso, estão ordenadas de forma crescente (as positivas) 
        F.append(F1[i])
        if i == 0: S.append(pow(abs(Y[i])/NSAMP, 2))
        else: S.append(2*pow(abs(Y[i])/NSAMP,2))
        i = i + 1
    N_points = i
    S[N_points - 1] = S[N_points - 1]/2
    del F1

    # Unilateral power spectrum
    S_dB = 10*np.log10(S)

    #Plots
    p.figure(1, figsize=(10, 6)) #Tamanho customizável

    #Plot of the Audio
    p.subplot(2, 1, 1)
    p.plot(T, X)

    #Plot Information
    p.title('Signal Recorded')
    p.xlabel('Time [s]')
    p.ylabel('Amplitude [V]') #Mudar para as devidas unidades
    p.grid()
    ax = p.gca()
    ax.set_xlim(0,T[NSAMP-1])

    #Plot of the Density Power Spectrum 
    p.subplot(2, 1, 2)

    #Plot options
    #p.plot(F, S) #Unidades lineares
    #p.semilogx(F,S) #Por década, Unidades lineares
    p.plot(F, S_dB) #Unidades logarítmicas
    #p.semilogx(F,S_dB) #Por década, logarítmicas

    #Plot Information
    p.title('Power Spectrum')
    p.xlabel('Frequency [Hz]')
    p.ylabel('Power [dBW]') #Unidades Lineares
    #p.ylabel('Power [dBW]') #Unidades logarítmicas
    p.grid()
    ax = p.gca()
    ax.set_xlim(0,F[N_points - 1]) #Linear
    #ax.set_xlim(0.1,F[N_points - 1]) #Décadas

    p.tight_layout()
    p.show()

#Data Vector
X = [] #Signal from Arduino
T = [] #Time Vector of the samples
F = [] #Frequency vector
S = [] #Power Spectrum

ser = serial.Serial('COM8',9600,timeout=100)
time.sleep(2)

while(1):
    line = ser.readline()
    if line != 0:
        line = line.strip()
        line = line.decode()
        if line == "start":
            print("start reading\n")
            ReadStuff()


del S, F, X, T, ser
exit()