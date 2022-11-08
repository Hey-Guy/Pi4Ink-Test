import smbus
import a_Extern as ziel
print('Skript DAC_AD5593.py 4 - 20 mA')
'''
V   mA
1   4,12
2   7,74
3   11,32
4   14,93
'''
i2cKanal = smbus.SMBus(1)
i2cPort = 0x10
i2cKanal.write_i2c_block_data(i2cPort, 0b00000101, [0b00000000, 0b00001111])  # pin 0 - 3 als DACs

DAC = {'reglerVL': 0b00010000,  # sollVL
       'reglerRL': 0b00010001,  # soolRL
       'reglerPumpe': 0b00010010,  # sollPumpe
       'reglerVakuum': 0b00010011}  # sollDruck

def in_MSB_LSB(wert):
    msb = int(wert / 0xFF)
    lsb = int(wert - (msb * 0xFF))
    return msb, lsb


def dac(chanel, mA):  # wert 0 - 10 V
    DAC = {0: 0b00010000,  # sollVL
           1: 0b00010001,  # soolRL
           2: 0b00010010,  # sollPumpe
           3: 0b00010011,  # sollDruck
           4: 0b00010100,  # istVL
           5: 0b00010101,  # istRl
           6: 0b00010110,  # istPumpe
           7: 0b00010111}  # istDruck
    signal = (mA - 1.146)/0.0043
    msb, lsb = in_MSB_LSB(signal)
    i2cKanal.write_i2c_block_data(i2cPort, DAC[chanel], [msb, lsb])
    return

def regler(channel, wert):
    ziel.regler(channel, wert)


regler('reglerVL',1)
regler('reglerRL',10)
regler('reglerPumpe',100)
regler('reglerVakuum',0)





#Wert in mA (zwischen 4 und 20 --> 0,0005 bis - 0,1 bar)