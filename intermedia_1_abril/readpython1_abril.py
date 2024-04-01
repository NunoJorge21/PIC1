import serial
import time
import numpy as np
import matplotlib.pyplot as p

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
    #while i < 10000:
        line = ser.readline()
        line = line.strip()
        line = line.decode()
        #if i == 0: 
         #   fs = float(line)
          #  tSample = 1/fs
        #else : 
        if line == "finish": 
            print("finished reading")
            break

        X.append(float(line))
        T.append(tSample*i)
        i = i + 1
        
    #del line
    N = i

    #Bilateral Fourier Transform
    Y = np.fft.fft(X)
    F1 = np.fft.fftfreq(N, tSample)

    # Conversion to unilateral
    i = 0
    while(F1[i] >= 0): #Curiosamente, a função fft.fftfreq ordena o vetor F1 com as frequência positivas primeiro, seguidas das negativas. Além disso, estão ordenadas de forma crescente (as positivas) 
        F.append(F1[i])
        if i == 0: S.append(pow(abs(Y[i])/N, 2))
        else: S.append(2*pow(abs(Y[i])/N,2))
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
    ax.set_xlim(0,T[N-1])

    #Plot of the Density Power Spectrum 
    p.subplot(2, 1, 2)

    #Plot options
    p.plot(F, S) #Unidades lineares
    #p.semilogx(F,S) #Por década, Unidades lineares
    #p.plot(F, S_dB) #Unidades logarítmicas
    #p.semilogx(F,S_dB) #Por década, logarítmicas

    #Plot Information
    p.title('Power Spectrum')
    p.xlabel('Frequency [Hz]')
    p.ylabel('Power [W]') #Unidades Lineares
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

ser = serial.Serial("/dev/ttyACM0",9600,timeout=100)
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