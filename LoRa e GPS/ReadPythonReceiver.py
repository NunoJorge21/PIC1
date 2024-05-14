import serial
import time
import numpy as np
import matplotlib.pyplot as p
import re

NSAMP = 2048
NF = 1024

def sscanf(string, format_string):
    pattern = format_string.replace('%d', r'(\d+)').replace('%f', r'(\d+\.\d+)').replace('%s', r'(\S+)')
    match = re.match(pattern, string)
    if match:
        return match.groups()



def ReadLine(string):
    i = 1
    data = sscanf(string, "%s %d %d %d %d")
    if data is not None and data[0] == "sent:":
        for i in range(1,5):
            S.append(int(data[i]))
    
    
def ReadStuff():
    lat = 0
    lng = 0
    F.clear()
    S.clear()
    fs = 25000  #sampling freq same as arduino
    res = fs/NSAMP
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
        F.append(res*i)
        F.append(res*(i+1))
        F.append(res*(i+2))
        F.append(res*(i+3))
        i = i + 4

    #lat = S.pop(NF)
    #lng = S.pop(NF+1)
    #F.pop(NF)
    #F.pop(NF+1)

    # Unilateral power spectrum
    S_dB = 10*np.log10(S)

    #Plots
    p.figure(1, figsize=(10, 6)) #Tamanho customizável


    #Plot options
    p.plot(F, S) #Unidades lineares
    #p.semilogx(F,S) #Por década, Unidades lineares
    #p.plot(F, S_dB) #Unidades logarítmicas
    #p.semilogx(F,S_dB) #Por década, logarítmicas

    #Plot Information
    p.title('Power Spectrum')
    #p.suptitle(f'Latitude : {lat:.7f} Longitude: {lng:.7f}')
    p.xlabel('Frequency [Hz]')
    p.ylabel('Power [W]') #Unidades Lineares
    #p.ylabel('Power [dBW]') #Unidades logarítmicas
    p.grid()
    ax = p.gca()
    ax.set_xlim(0,F[NF - 1]) #Linear
    #ax.set_xlim(0.1,F[N_points - 1]) #Décadas

    p.tight_layout()
    p.show()

#Data Vector
F = [] #Frequency vector
S = [] #Power Spectrum

# ser = serial.Serial('COM3',9600,timeout=100)
ser = serial.Serial('/dev/ttyUSB0',9600,timeout=100)
time.sleep(2)

while(1):
    line = ser.readline()
    if line != 0:
        line = line.strip()
        line = line.decode()
        if line == "start":
            print("start reading\n")
            ReadStuff()


del S, F, ser
exit()