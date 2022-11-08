import sys
import time

import basics

if '/usr/bin' in sys.executable:  # Auswhal, ob python am Pi oder am LapTop
    import a_Extern as ziel
else:
    import a_Intern as ziel
# print('Ziel = a_Extern', )

GIPOs = {'ventilVL': 6,  # pin29 - Flüssigkeit
         'ventilRL': 13,  # pin31 - Flüssigkeit
         'pumpeInk': 16,  # pin33
         'Licht': 5,  # pin36
         'druckPurgen': 19,  # pin35
         'vorVentile': 20,  # pin38 - 2 mal für Vakuum und 1 für Druck
         'purgenVL': 26,  # pin40 Umschaltventil zwischen Vakuum und Purgedruck
         'purgenRL': 21}  # pin37 Umschaltventil zwischen Vakuum und Purgedruck

ADCs = {'vakuum': 'in2/ref',
        'pumpe': 'in0/ref'}


def purgen(name, sollPumpe) -> object:  # name: spuelen oder intensiv
    def rampe(zeit, startDruck, stopDruck):
        startZeit = time.time()  # in sekunden
        stufenZeit = 0.2  # TODO: Anzahl der Schaltungen pro Sekunde messen
        stufen = int(zeit / stufenZeit)
        deltaDruck = (stopDruck - startDruck) / stufen
        druck = startDruck
        stufDurchlauf = 0
        for i in range(stufen):
            deltaZeit = time.time() - startZeit
            while (deltaZeit < i * stufenZeit):
                time.sleep(0.01)
                deltaZeit = time.time() - startZeit
            druck = round(druck + deltaDruck, 3)  # round damit keine negativen Werte
            ziel.regler('reglerPurgen', druck)
            print('a_Interface purgen: Zeit ', round(deltaZeit, 3), '\tDruck ', druck)
            stufDurchlauf += 1

    vorlauf = float(basics.iniLesen('allVorgaben.ini', 'vorlauf ' + name))  # name = {normal, intensiv, maxVL, maxRL)
    dauer = float(basics.iniLesen('allVorgaben.ini', 'dauer ' + name))
    nachlauf = float(basics.iniLesen('allVorgaben.ini', 'nachlauf ' + name))
    staerke = float(basics.iniLesen('allVorgaben.ini', 'staerke ' + name))

    ziel.regler('reglerPumpe', 0)
    ziel.regler('reglerPurgen', 0)
    ziel.schalter(GIPOs, 'purgenVL', True)
    ziel.schalter(GIPOs, 'purgenRL', True)
    if 'VL' in name:
        ziel.schalter(GIPOs, 'purgenRL', False)
    if 'RL' in name:
        ziel.schalter(GIPOs, 'purgenVL', False)
    ziel.schalter(GIPOs, 'druckPurgen', True)
    rampe(vorlauf, 0, staerke)
    rampe(dauer, staerke, staerke)
    rampe(nachlauf, staerke, 0)
    ziel.regler('reglerPurgen', 0)
    ziel.schalter(GIPOs, 'purgenVL', False)
    ziel.schalter(GIPOs, 'purgenRL', False)
    ziel.regler('reglerPumpe', sollPumpe)


def fuellstandNormierungParabel(fuellsensor, tank):
    koef = [float(basics.iniLesen('allVorgaben.ini', tank + '_a')),
            float(basics.iniLesen('allVorgaben.ini', tank + '_b')),
            float(basics.iniLesen('allVorgaben.ini', tank + '_c'))]
    fuellProzent = round(koef[0] * fuellsensor * fuellsensor + koef[1] * fuellsensor + koef[2], 3)
    print('a_Interface Koef', koef)
    return fuellProzent


def fuellstandNormierungStufen(fuellsensor, tank):  # Linear zwischen 0 und 20% und 20% bis 100% -2 Geraden
    stufen = [0, 10, 20, 30, 40, 50, 99]  # zweimal 99, wegen Überlauf variable
    fuellEichung = []
    for i in stufen:
        titel = tank + str(i)
        fuellEichung.append(float(basics.iniLesen('allVorgaben.ini', titel)))
    schritteLen = len(stufen)-1
    if fuellsensor >= fuellEichung[schritteLen]:
        m = (stufen[schritteLen] - stufen[schritteLen-1]) / (fuellEichung[schritteLen] - fuellEichung[schritteLen-1])
        t = stufen[schritteLen] - m * fuellEichung[schritteLen]
    else:
        for i in range(0,schritteLen):
            if fuellsensor < fuellEichung[i + 1]:
                m = (stufen[i + 1] - stufen[i]) / (fuellEichung[i + 1] - fuellEichung[i])
                t = stufen[i] - m * fuellEichung[i]
                break
    fuellProzent = m * fuellsensor + t
    if fuellProzent < 0:
        fuellProzent=0
    #print('a_Interface m ', m, '\t t', t, '\tfuellProzent', fuellProzent ,'fuellEichung', fuellEichung)
    return fuellProzent

'''def fuellstandNormierung20(fuellsensor, tank):  # Linear zwischen 0 und 20% und 20% bis 100% -2 Geraden
    fuellEichung = [float(basics.iniLesen('allVorgaben.ini', tank + '0')),
                    float(basics.iniLesen('allVorgaben.ini', tank + '20')),
                    float(basics.iniLesen('allVorgaben.ini', tank + '100'))]
    if fuellsensor < fuellEichung[1]:
        m = (20 - 0) / (fuellEichung[1] - fuellEichung[0])
        t = 0 - m * fuellEichung[0]
    else:
        m = (100 - 20) / (fuellEichung[2] - fuellEichung[1])
        t = 20 - m * fuellEichung[1]

    fuellProzent = m * fuellsensor + t
    # print('a_Interface fuellEichung \t', fuellEichung, '\m ', m, '\t t', t,'\tfuellProzent',fuellProzent)
    return fuellProzent
'''

def fuellstandMessen(sollPumpe, statusPumpe, fuellVLalt, fuellRLalt):
    empfindlichkeit = 0.005
    empfindlichkeitDelta = 0.001

    deltaAlt = fuellRLalt - fuellVLalt
    fuellVLsensor = ziel.fuellstandGradient('VL')
    fuellVL = fuellstandNormierungStufen(fuellVLsensor, 'VL')
    fuellRLsensor = ziel.fuellstandGradient('RL')
    fuellRL = fuellstandNormierungStufen(fuellRLsensor, 'RL')

    delta = fuellRL - fuellVL
    regelfaktor = delta
    if statusPumpe == 'auto':
        if abs(delta) > abs(deltaAlt):  # falls Unerschied der Füllhöhen sinkt, Pumpleistung bleibt gleich
            regelfaktor = delta
            # print('Fall 1', abs(delta) - abs(deltaAlt))
        elif delta == 0:
            regelfaktor = 0
        else:
            regelfaktor = -deltaAlt / delta * delta / abs(delta) * empfindlichkeitDelta
            # print('Fall 2', regelfaktor)

    if sollPumpe > 99:
        sollPumpe = 99
    if sollPumpe < 0:
        sollPumpe = 0

    sollPumpe += regelfaktor * empfindlichkeit
    regler('reglerPumpe', sollPumpe)

    fuellVL = round(fuellVL, 3)
    fuellRL = round(fuellRL, 3)

    # print('fuellVl: ', fuellVL, '\tfuellRl: ', fuellRL, '  delta: ', delta, deltaAlt)
    # print('SollPumpe in fuelstand:', sollPumpe, '\tStatus: ',statusPumpe)
    # print('FüllstandVL = ' + str(fuellVL) + ' FüllstandRL = ' + str(fuellRL) + ' Pumpe = ' + str(sollPumpe))
    return sollPumpe, fuellVL, fuellRL


def setup(sollVL, sollRL):
    ziel.setupRelais(GIPOs)  # alle Relais auf False
    ziel.setupRegler()
    ziel.schalter(GIPOs, 'Licht', True)
    ziel.schalter(GIPOs, 'vorVentile', True)
    ziel.regler('reglerVL', sollVL)
    ziel.regler('reglerRL', sollRL)
    startVakuum = int(basics.iniLesen('allVorgaben.ini', 'startVakuum'))
    ziel.regler('reglerVakuum', startVakuum)
    ziel.schalter(GIPOs, 'Licht', True)  # Vakuumpumpe ein
    ziel.regler('reglerPurgen', 0)


def start():
    ziel.schalter(GIPOs, 'ventilVL', True)
    ziel.schalter(GIPOs, 'ventilRL', True)
    ziel.schalter(GIPOs, 'pumpeInk', True)
    ziel.schalter(GIPOs, 'Licht', True)
    sollPumpeVakuum = int(basics.iniLesen('allVorgaben.ini', 'hochVakuum'))
    ziel.regler('reglerVakuum', sollPumpeVakuum)
    ziel.schalter(GIPOs, 'vorVentile', True)  # Vakuumpumpe ein


def stop() -> object:
    pause = 0.1
    ziel.schalter(GIPOs, 'ventilVL', False)
    time.sleep(pause)
    ziel.schalter(GIPOs, 'ventilRL', False)
    time.sleep(pause)
    ziel.regler('reglerPumpe', 0)
    ziel.schalter(GIPOs, 'pumpeInk', False)
    time.sleep(pause)
    ziel.schalter(GIPOs, 'Licht', False)
    time.sleep(pause)
    ziel.regler("reglerVakuum", 10)
    time.sleep(pause)
    ziel.regler('reglerPurgen', 0)
    ziel.schalter(GIPOs, 'druckPurgen', False)
    time.sleep(pause)
    ziel.schalter(GIPOs, 'vorVentile', False)
    time.sleep(pause)
    ziel.schalter(GIPOs, 'purgenVL', False)
    time.sleep(pause)
    ziel.schalter(GIPOs, 'purgenRL', False)
    time.sleep(pause)


def adcMessung(channel):
    eingang = ziel.adc1015Wert(ADCs[channel])
    return eingang


def schalter(channel, wert):
    ziel.schalter(GIPOs, channel, wert)


def regler(channel, wert):
    ziel.regler(channel, wert)
