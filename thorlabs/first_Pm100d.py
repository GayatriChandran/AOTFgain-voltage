#!/usr/bin/python
#
# @file
#
# Communicates with a Thorlabs PM-100D power
# meter via USB.
#
# Gayatri 2/19
#

#import traceback
import visa
from ThorlabsPM100 import ThorlabsPM100
from time import sleep
import numpy
from numpy import array
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import nationalInstruments.nicontrol as ni
import numbers

rm = visa.ResourceManager()
# print(rm.list_resources())
inst = rm.open_resource('USB0::0x1313::0x8078::PM002212::INSTR')
power_meter = ThorlabsPM100(inst=inst)
# print (power_meter.read) # Read-only property

power_meter.system.beeper.immediate()

print("Measurement type :", power_meter.getconfigure)
print("Current value    :", power_meter.read)
print("Wavelength       :", power_meter.sense.correction.wavelength)
print("Power range limit:", power_meter.sense.power.dc.range.upper)

# wavelength = input("New wavelength setting : ")
# power_meter.sense.correction.wavelength = float(wavelength)
# print("New wavelength       :", power_meter.sense.correction.wavelength)
print("Set range auto and wait 500ms    ...")
sleep(.5)
power_meter.sense.power.dc.range.auto = "ON"
print("Average per measure :", power_meter.sense.average.count)
print("Set average to 1 ...")
power_meter.sense.average.count = 1

print("Perform 100 measurements ...")
mes = array([power_meter.read for _ in range(100)])

#Send a constant 1V to the laser's channel (eg: ao8 for 488) so that FSK# remains high
ao4 = ni.AnalogOutput(source="Dev1/ao4", min_val=0.0, max_val=1.2)
ao4.output(1)

# Generate the modulation voltage. This is what we will vary, to check its effect on power output
# at constant gain
ao20 = ni.AnalogOutput(source="Dev1/ao20", min_val=0.0, max_val=1.6)
ao20.output(1)
#Wait here for a random input, just to give me time to verify connections
kapish = input("Shall we start ? : ")
data = []
voltage = []
for i in range(0, 150):
    v = i/150
    ao20.output(v)
    sleep(0.01)
    data.append(power_meter.read)
    voltage.append(v)    
    sleep(0.05)

print("Finished voltage waveform!")
ao20.output(0)
ao4.output(0)
plt.style.use('classic')
# t = numpy.linspace(0, 10, 100)
plt.plot(voltage,data)
plt.show()
