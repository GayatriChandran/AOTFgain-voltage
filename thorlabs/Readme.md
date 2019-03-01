Procedure (For getting voltage-intensity relation):

1. Decide which wavelength to test.
2. Switch on the laser.
3. Open a terminal with stormenv and navigate to crystalTechnologies folder.
4. Edit the main() part of AOTF.py such that it is specific to the desired channel.
5. Make sure amplitude, frequency values are correct.
6. Run AOTF.py (inside storm-control and stormenv). The string "Shutdown ? : " will be displayed. Minimise this terminal and open another one.
7. Navigate to pm100d folder and activate pm100d environment.
8. Make sure the first ao channel is correct (eg; ao8 for 488nm). The power meter should be ON.
9. Run PM100D.py
9. Enter required wavelength.
10. A prompt will appear, asking "Shall we start? ". 
11. Before sending varying mod voltage to the AOTF, the mod input of that channel should be connected to ao20.
12. When ready, start.
13. A plot is displayed. Save it.

To summarise :

Start AOTF
Start PM100D
Make sure correct channel is connected to ao20
Plot!

Update : By default, the AOTF.py code sends all commands now. No need to change anything. 

Procedure (for getting RF amplitude - optical intensity relation at constant voltage, gain):

Make sure ao channel is correct
Check the optimal voltage is sent as modulation (from ao20)