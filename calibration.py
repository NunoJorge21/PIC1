# Python 3.9.9

import T_Display
import time
import math
import gc

# Global variables
global N_SAMPLES # number of samples
global tSample # sampling duration
global sampleDurations
global verticalScale
global horizontalScale 
global currentVscale # Vertical scale to be displayed
global currentHscaleTime # Horizontal scale to be displayed in time
global currentHscaleFreq # Horizontal scale to be displayed in frequency
global factor # Voltage divider factor
global adcReadings # will conatin ADC readings
global systemVoltage # will contain input voltage levels converted from ADC readings
global adcDFT #wil contain DFT
global slope # slope used in digital value to voltage conversion
global yIntersection # y-intersection used in digital value to voltage conversion
global tft # intantiates a TFT object
global V_max # signal's maximum value
global V_min # signal's minimum value
global V_av # signal's average value
global V_ef # signal's rms value

N_SAMPLES = 240 # number of samples
tSample = 200 # sampling duration in ms
sampleDurations = [50, 100, 200, 500] # vaious sampling durations in ms
verticalScale = [1, 2, 5, 10]
horizontalScale = [5, 10, 20, 50] 
currentVscale = 10 # Vertical scale to be displayed
currentHscaleTime = 20 # Horizontal scale to be displayed in time
currentHscaleFreq = 60 # Horizontal scale to be displayed in frequency
factor = 1/29.3 # Voltage divider factor
adcReadings = [0.0]*N_SAMPLES # will conatin ADC readings
systemVoltage = [0.0]*N_SAMPLES # will contain voltage levels converted from ADC readings
adcDFT = [0.0]*N_SAMPLES # will contain voltage levels converted from ADC readings
slope = 0.00044028 # slope used in digital value to voltage conversion
yIntersection = 0.091455 # y-intersection used in digital value to voltage conversion
tft = T_Display.TFT() # intantiates a TFT object
V_max = 0.0 # signal's maximum value
V_min = 0.0 # signal's minimum value
V_av = 0.0 # signal's average value
V_ef = 0.0 # signal's rms value


# Functions
'''
Function - setDisplay(gridFlag)

Arguments: 
    gridFlag - fetermines which grid to display 
        (if 1, grid in time mode; if 2, grid in frequency mode; else, no grid)

Description:
    This function clears the display and sets the grid,
the scales and the Wi-Fi icon.
'''
def setDisplay(gridFlag):
    tft.display_set(tft.BLACK, 0, 0, 240, 135) # clear display
    
    if gridFlag == 1:
        # trace time grid on display
        tft.display_write_grid(0,16,240,135-16,10,6,True, tft.GREY1,tft.GREY2)
        tft.display_write_str(tft.Arial16, "{vscale}V/".format(vscale = currentVscale), 0, 0)
        tft.display_write_str(tft.Arial16, "{hscale}ms/".format(hscale = currentHscaleTime), 105, 0)
    elif gridFlag == 2:
        currentHscaleFreq = (N_SAMPLES/(2*tSample*10**-3))//10 # this operation corresponds to (half of sampling frequency)//10

        # trace frequency grid on display
        tft.display_write_grid(0,16,240,135-16,10,6,False, tft.GREY1,tft.GREY2)
        tft.display_write_str(tft.Arial16, "{vscale}V/".format(vscale = currentVscale/2), 0, 0)
        tft.display_write_str(tft.Arial16, "{hscale}Hz/".format(hscale = currentHscaleFreq), 105, 0)        

    tft.set_wifi_icon(224, 0)

    gc.collect()



'''
Function - calibrate(tft)

Arguments:
    tft - TFT object

Description:
    This function performs the calibration of the ADC reading to 
        voltage value conversion, for the ADC that is being used.
'''
def calibrate(tft):
    global slope
    global yIntersection

    n_inputs = 0
    adc_values = [0.0]*5
    input_values = [-10, -5, 0, 5, 10]
    SLOPES = [0.0]*4
    Y_INTERSECTIONS = [0.0]*4

    setDisplay(0)

    tft.display_write_str(tft.Arial16, "Input DC voltages for calibration:", 0, 135-16)
    tft.display_write_str(tft.Arial16, "-10V, -5V, 0V, +5V and +10V", 16, 135-40)
    tft.display_write_str(tft.Arial16, "{n_inputs}/5 input voltages read".format(n_inputs = n_inputs), 16, 135-70)
    tft.display_write_str(tft.Arial16, "Next input voltage: {input}V".format(input = -10), 0, 35)
    tft.display_write_str(tft.Arial16, "(Press button 11 when input is set)", 0, 16)

    while 1:
        if tft.readButton() == 11:
            # Perform 100 samples of 100 points each
            for i in range(100): 
                aux_ADCreadings = tft.read_adc(100, 50)
                adc_values[n_inputs] += sum(aux_ADCreadings[:100])

            adc_values[n_inputs] /= 10000
            # adc_values[n_inputs] now stores the average of the 10000 points

            n_inputs += 1
            tft.display_write_str(tft.Arial16, "{n_inputs}/5 input voltages read".format(n_inputs = n_inputs), 16, 135-70)
            tft.display_set(tft.BLACK, 0, 35, 240, 16) # clear the line before writing
            if n_inputs < 5:
                tft.display_write_str(tft.Arial16, "Next input voltage: {input}V".format(input = input_values[n_inputs]), 0, 35)
            else:
                tft.display_write_str(tft.Arial16, "Next input voltage: None", 0, 35)
                break
        else:
            continue

    # Let's perform a linear regression of the measured points, considering the minimum squares method
    A_mat = 0
    B_mat = 0
    C_mat = 0
    D_mat = 0
    E_mat = 0
    for i in range(4):
        A_mat += (adc_values[i])*(adc_values[i])
        B_mat += adc_values[i]
        C_mat += 1
        D_mat += adc_values[i]*input_values[i]
        E_mat += input_values[i]

    slope = (C_mat*D_mat-B_mat*E_mat)/(A_mat*C_mat-B_mat*B_mat)
    yIntersection = (A_mat*E_mat-B_mat*D_mat)/(A_mat*C_mat-B_mat*B_mat)

    # The equation of the obtained line is of the form:
        # V_I = slope*D + yIntersection;
        # V_I is the system input voltage (input_values) and D is the digital value read by the ADC
    
    # We need to convert this to something of the form:
        # V_ADC = slope*D + yIntersection
        # V_ADC = factor*V_I + 1 = factor*(slope*D + yIntersection) + 1

    slope = slope*factor
    yIntersection = (yIntersection*factor)+1

    time.sleep(2)

    del n_inputs
    del aux_ADCreadings
    del adc_values
    del input_values
    del SLOPES
    del Y_INTERSECTIONS
    del A_mat
    del B_mat
    del C_mat
    del D_mat
    del E_mat
    gc.collect()




### Main ###
gc.collect()    

domainFlag = 0 # indicates if we are on time (0) or frequency (1) domain

tft.display_write_str(tft.Arial16, "Embedded system oscilloscpe", 16, 135-40)


calibrate(tft)
setDisplay(0)
tft.display_write_str(tft.Arial16, "slope= {slope}".format(slope=slope), 0, 135-70)
tft.display_write_str(tft.Arial16, "yIntersection={yIntersection}".format(yIntersection=yIntersection), 0, 16)

time.sleep(10000)

