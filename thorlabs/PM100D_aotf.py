#!/usr/bin/python
#
# @file
#
# Communicates with a Thorlabs PM-100D power
# meter via USB.
#
# Gayatri 2/19
#


import visa
from ThorlabsPM100 import ThorlabsPM100
from time import sleep
import numpy
from numpy import array
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import nationalInstruments.nicontrol as ni
import numbers
import pandas as pd
import crystalTechnologies.AOTF as aotf
#import signal

def ctrlCHandler(sig, frame):
    print("CTRL-C Handler:")
    print("Shutting down aotf !")
    my_aotf.shutDown()
    
if (__name__ == "__main__"):

    #Establish connection with power meter and obtain a handle
    rm = visa.ResourceManager()
    inst = rm.open_resource('USB0::0x1313::0x8078::PM002212::INSTR')
    power_meter = ThorlabsPM100(inst=inst)
    power_meter.system.beeper.immediate()

    #Print current wavelength setting
    print("Wavelength       :", power_meter.sense.correction.wavelength)

    #Incase you need to change wavelength
    w = input("Change wavelength? (y or n) : ")
    if w=="y":
        wavelength = input("New wavelength setting : ")
        power_meter.sense.correction.wavelength = float(wavelength)
        print("New wavelength       :", power_meter.sense.correction.wavelength)

    #To set range as AUTO if not already set.
    print("Set range auto and wait 500ms    ...")
    power_meter.sense.power.dc.range.auto = "ON"
    sleep(.5)
    #Set required average count
    #print("Average per measure :", power_meter.sense.average.count)
    #print("Set average to 1 ...")
    power_meter.sense.average.count = 150


    #Send a constant 1V to the laser's channel (eg: ao8 for 488) so that FSK# remains high
    ao0 = ni.AnalogOutput(source="Dev1/ao0", min_val=0.0, max_val=1.2)
    ao0.output(1)

    # Generate the modulation voltage. This is what we will vary, to check its effect on power output
    # at constant gain
    ao20 = ni.AnalogOutput(source="Dev1/ao20", min_val=0.0, max_val=1.6)
    ao20.output(0.953)

    #Initialize AOTF control
    my_aotf = aotf.AOTF64Bit(python32_exe = "C:/Users/Storm1/AppData/Local/Programs/Python/Python36-32/python")
    if not my_aotf.getStatus():
        exit()
    print(my_aotf._sendCmd("BoardID ID"))
    my_aotf._sendCmd("dau en")
    my_aotf._sendCmd("dau gain * 255")
    my_aotf._sendCmd("dau dis")
    my_aotf._sendCmd("dds fsk 0 1")
    my_aotf._sendCmd("dds f 0 20.0 89.66 20.0 20.0")
    my_aotf._sendCmd("dds fsk 1 1")
    my_aotf._sendCmd("dds f 1 20.0 107.03 20.0 20.0")
    my_aotf._sendCmd("dds fsk 2 1")
    my_aotf._sendCmd("dds f 2 20.0 130.20 20.0 20.0")
    my_aotf._sendCmd("dds fsk 3 1")
    my_aotf._sendCmd("dds f 3 20.0 141.03 20.0 20.0")
    my_aotf._sendCmd("dds a 0 8193")
    my_aotf._sendCmd("dds a 1 7023")
    my_aotf._sendCmd("dds a 2 12873")
    my_aotf._sendCmd("dds a 3 6633")
    #Wait here for a random input, just to give time to verify connections
    kapish = input("Shall we start ? (y or n) : ")
    if kapish=='n':
        my_aotf.shutDown()
        exit()
    wl = int(power_meter.sense.correction.wavelength)

    # Configure ctrl-c handling.
    # signal.signal(signal.SIGINT, ctrlCHandler)

    mappings = [[647, 0, 8193], [561, 1, 7023] , [488, 2, 12873] , [460, 3, 6633]]
    search = wl
    for (wav, ch, amp) in mappings:
        if wav == wl:
            channel = ch
            rfmax = amp
        else :
            pass

    data = []
    amplitude = []

    #Generate a range of voltages and store power_meter readings for each
    for i in range(0,101):
        a = round(float(rfmax*i/100),0)
        cmd = "dds a " + str(channel) + " " + str(a)
        my_aotf._sendCmd(cmd)
        sleep(0.01)
        data.append(power_meter.read)
        amplitude.append(a)    
        sleep(0.02)

    #Restore zero voltage output at channels
    print("Finished voltage waveform!")
    ao20.output(0)
    ao0.output(0)

    #Store wavelength value as string

    wl = str(wl)

    #Save data to .csv file
    file_name1 = wl + "-aotf.csv"
    data1 = [1000*x for x in data]
    data1 = numpy.around(data1, decimals = 2)

    df = pd.DataFrame({"RF amplitude" : amplitude, "Power meter readings (mW)" : data1})
    df.to_csv(file_name1, index=False)

    #Save other details like peak intensity, etc...to a text file
    peak_index = numpy.where(data1 == numpy.amax(data1))
    file_name2 = "info-" + wl + "-aotf.txt"
    f = open(file_name2,'w')
    #Sometimes line 141 throws an error for 647... Perhaps it catches two close peak_indices ?
    a = float(amplitude[int(peak_index[0])])
    b = float(data1[int(peak_index[0])])
    wave_text = 'Wavelength = '+ wl + 'nm'
    f.write(wave_text)
    f.write('\n')
    f.write('Peak intensity :'+ str(b) + 'mW\n')
    f.write('At amplitude :'+ str(a) + '\n')
    f.write('Gain = 255')
    f.close()

    #Shutdown AOTF
    kapish = input("Shutdown aotf? : ")
    my_aotf.shutDown()

    #Plot and save graph
    plt.style.use('classic')
    title = "AOTF RF amplitude vs optical pwr relation for " + wl + "nm"
    plt.title(title)
    plt.ylabel('Optical power (mW)')
    plt.xlabel('RF amplitude')
    plt.plot(amplitude,data1, 'r--')
    fig_name = wl + '-aotf.png'
    plt.savefig(fig_name)
    plt.show()
    inst.close()



#
# The MIT License
#
# Copyright (c) 2013 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#