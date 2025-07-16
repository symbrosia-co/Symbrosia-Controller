# CO<sub>2</sub> Monitor

This example uses a simple pressure monitor to provide an alarm before a CO<sub>2</sub> cylinder is exhausted.

There is a complication in using a simple pressure sensor to monitor a CO<sub>2</sub> cylinder.  As CO<sub>2</sub> is stored as a liquid under pressure in the cylinder, the pressure in the tank is not determined by the amount of gas remaining, but rather by the boiling point of CO<sub>2</sub>.  Thus the amount of remaining gas cannot be measured by monitoring the pressure as it could be with air as done in scuba tanks.

The working pressure of the tank will remain at 50 to 70 Bar (700-1000 PSI), depending on ambient temperture, until the last liquid boils off.  Only once the liquid is gone will the pressure begin to drop as the last gas from the tank is used.  Setting an alarm threshhold of around 35 Bar (500 PSI) will allow a bit of warning before the available supply of gas is totally expended.

If proper determination of the amount of remaining CO<sub>2</sub> is desired the most practical method is to place the cylinder on a scale to directly measure the weight of the remaining gas.  As some scales do offer an analog output this output could be connected to a Symbrosia controller to provide remote monitoring and alarms.

<p align="center"><img width="50" height="50" src="/res/SymbrosiaLogo.png"></p>
