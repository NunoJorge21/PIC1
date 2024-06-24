import math

def raw_to_dBSPL( MEMS_value) :
    kS = 25.8007913316472
    CC = -0.192071444248343

    Son = math.log10(MEMS_value)
    Son = Son - CC
    Son = kS * Son
    return Son

def Y_to_dbSPL( Y ) :
    YdB = []

    for element in Y:
        YdB.append(raw_to_dBSPL(element))

    return YdB

def S_to_dbSPL( S ) :
    SdB = []

    for element in S:
        aux = math.sqrt(element)
        SdB.append(raw_to_dBSPL(aux))

    return SdB

#values = [ 134.23 ,84.98,55.94,33.82, 26.05, 24.23,23.17,184.19,300.1,796.57,2719.21]

#for element in values:
#    print(raw_to_dbSPL(element))
