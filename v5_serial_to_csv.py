import serial
import time
import csv
import os

startTime = time.time()

N = 20000 #number of points TEST FOR ARDUINO CODE COMPABILITY

ser = serial.Serial("/dev/ttyACM0",9600,timeout=100)
time.sleep(2)

# File path to save the CSV
file_path = "rp2040_data_20240329.csv"
help_file = "help_file"

# Open the CSV file in write mode
with open(help_file, "w") as h:
    for i in range(N):
        line = ser.readline()
        line = line.strip()
        line = line.decode()
        print(line)
        h.write(line+'\n')

measureTime = time.time()-startTime
tSample = measureTime/N

with open(help_file, "r") as h:
    with open(file_path, "w") as f:
        i = 0
        for line in h:
            f.write(str(i*tSample)+','+line)
            i = i +1
os.remove(help_file)
    
    
         
ser.close()


    
 
