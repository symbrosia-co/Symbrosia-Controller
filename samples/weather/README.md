# SymbCtrl Weather Station

The weather station is configured to support the sesnors that provide the most useful values to an outdoor aquaculture.

While a dedicated weather station may be desired, there is an option...  In a modest to large outdoor installation is likely that there are unused input channels on the various controllers scattered across a cultivation yard.  Adding weather instruments to these otherwise unused channels would allow excellent weather monitoring without a dedicated weather station.  The method of connection would be the same as detailed here.

* An air temperature sensor
* PAR sensor
* Rain gauge

## Sensors

### Air Temperature Sensor
A Pt100 temperature sensor is used for ambient temperature, simply connected to one of the temperature inputs on the controller.  To ensure accurate readings the sensor needs to be located in free air away from other objects, ideally at a height above the ground.  

The temperature sensor also needs to be shaded from sunlight. this is done with a small louvered enclosure.  A 3D model for a small solar radiation enclosure is provided here in the repository.  This should be printed using a sunlight resistant plastic such as ABS or ASA.   

### PAR Sensor
A commercial PAR (Photosynthetically Active Radiation) sensor is connected to one of the general purpose analog inputs.  This provides a calibrated measurement of the avalable solar radiation avalable for algae growth.

A good example of such a sesnor would be the [Apogee SQ-515-SS or SQ-514-SS sensors](https://www.apogeeinstruments.com/full-spectrum-quantum-par-meters-and-sensors).  These provide a 0 to 5V or 4-20mA signal that can be directly connected to the analog inputs on a Symbrosia Controller.

### Rain Gauge
A standard tipping bucket rain gauge is connected to one of the digital inputs.

Using the software counter provides a direct measurement of rainfall on your facility.  Configuring the counter with a daily reset then gives a daily precipitation count that can be easily logged.

## Hardware

### SymbCtrl PCB

### Housing

### 3D Prints

### Wiring

## Software

### Firmware
The standard SymbCtrl firmware should be loaded

## SyWx
A simple weather station GUI is provided that displays and logs the weather station data.  This is a Python and TCl GUI that should run on any operating system.
