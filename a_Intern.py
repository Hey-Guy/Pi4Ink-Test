from numpy.random import randint
import basics

def fuellstand(sensorVL_Voll, sensorVL_Leer,sensorRL_Voll, sensorRL_Leer):
    fuellVL = float(basics.iniLesen('all_Ist.ini','fuellstandVL'))
    fuellRL = float(basics.iniLesen('all_Ist.ini','fuellstandRL'))
    return fuellVL, fuellRL

def fuellstandGradient(tank):
    fuellstand = randint(11000, 11001)
    #print('fuellstandGradient Fuellstand ',fuellstand)
    return fuellstand

def setupRelais(GIPOs):
    #print('setupRelais')
    return

def schalter(GIPOs, channel, wert):
    #print('Schalter :\t', channel, '\t', not (wert))
    return

def regler(channel, wert):
    DAC = {'reglerVL': 0b00010000,  # sollVL
           'reglerRL': 0b00010001,  # soolRL
           'reglerPumpe': 0b00010010,  # sollPumpe
           'reglerVakuum': 0b00010011,  # sollDruck
           'reglerPurgen': 0b00010100}  #Druck beim Purgen
    #print('Regler :\t', DAC[channel], '\t', wert)


def setupRegler():
    #print('SetupRegler')
    return

def arduino():
    istVL = round(float(basics.iniLesen('all_Ist.ini', 'istVL')), 1)
    istRL = round(float(basics.iniLesen('all_Ist.ini', 'istRL')), 1)
    istPumpe = round(float(basics.iniLesen('all_Ist.ini', 'istPumpe')), 1)
    istVakuum = round(float(basics.iniLesen('all_Ist.ini', 'istVakuum')), 1)
    istDruck = round(float(basics.iniLesen('all_Ist.ini', 'istDruck')), 1)
    vorVakuum = round(float(basics.iniLesen('all_Ist.ini', 'vorVakuum')), 1)
    return istVL, istRL, istPumpe, istVakuum, istDruck, vorVakuum


def adc1015Wert(channel):
    spannung = 24
    #print(channel, '\t Spannung ', spannung)
    return spannung
