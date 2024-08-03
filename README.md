# The Symbrosia Controller
The Symbrosia Controller is a low cost, robust, controller designed for aquaculture.  Initially developed to support on-shore seaweed farming operations in Kailua Kona, Hawai'i, the Symbrosia Controller features a customized, low-cost sensor suite and integrated control functions tailored to meet the unique demands of these environments. 

In addition to commercial use we envision the Symbrosia Controller as a powerful educational tool. By promoting literacy in electronics, programming, and agricultural management, we hope to empower individuals and communities to innovate and thrive in the agricultural sector. Our goal is to create a community where knowledge and technology are shared to drive sustainable agricultural practices and food security worldwide.

![A SymbCtrl in the DIN mount case](/res/CL46-47-24138-DC.jpg)

## Background
The Symbrosia controller was developed for in-house use as a lower cost alternative to the PLC based and commercial off-the-shelf systems we use for algae tank and bioreactor control.  In addition to controlling the tanks there were a few other needs, places where a little remote control and monitoring is useful.  With the availability of WiFi processors like the ESP32 automating these functions was a practical option.

Thus the Symbrosia Controller was born…  An ESP32 wedded to a circuit board that contains the most commonly needed interfaces. A water quality sensor amplifier, some temperature inputs, a couple analog inputs, along with some relays and transistor outputs for controlling external devices like valves and pumps. 

While there are commercial solutions available, we have had mixed experience with them... The available commercial controllers are expensive and tend to provide “closed garden” systems where it becomes difficult to retrieve data outside of dedicated application software.  There is also limited support for integrating this equipment into a wider system.  While a number of small-scale, open source solutions do exist, none of the devices we have reviewed are fully developed into robust, industrial solutions.  As a result of our experience the Symbrosia controller offers a number of key advantages…

+ Designed from the ground up as a network appliance with full WiFi access.
+ A standard industrial ModbusTCP interface, a well established interface supported by a vast array of software and solutions available in the market.
+ A simple and effective user interface allowing access to key settings.
+ A well thought out and flexible control arrangement allowing automated control of pH, temperature, or other parameters.
+ A range of inputs that address the usual aquaculture needs...
  + One fully isolated water quality amplifier (for pH, ORP, etc.)
  + Two Pt100 temperature inputs
  + Two general purpose analog inputs that can be used with 0-5V, 0-10V, or 4-20mA signals, these can also be used as simple digital inputs.
  + Two relay outputs
  + Two open collector digital outputs
+ Good calibration solutions in place for the analog inputs
+ Semi-automated pH calibration built into the software for use with 7ph, and 4pH or 10pH reference solutions.
+ A complete solution ready for deployment in real applications.  Use it as designed and published, or change the hardware or code to suit your own needs.

Communication is via 2.4GHz WiFi, thus no cabling beyond power, or perhaps your sensors is required, a very real concern when salt water is involved and locations are scattered across a large facility. 2.4GHz offers much increased range for applications that do not require the high bandwidth of higher frequencies.

For remote monitoring a ModbusTCP interface is implemented.  This allows easy integration with custom software or standard industrial SCADA infrastructure.  All SCADA software can interface with Modbus devices.  While most programming languages like Python have ModbusTCP libraries available to allow connections with a few lines of code.

There are many options for designing and building a device like this.  The philosophy used in the design was carefully considered...

+ The controller is designed to be constructed and maintained by anyone with modest electronics knowledge and skills. Unless changing features is desired, no programming is required to set up and use the controller.
+ Complex solutions or specialized parts were avoided.  Rather parts that are commonly available, inexpensive, and likely to remain available for some time to come were chosen for the design.
+ An open source programming platform is used so that development tools are available at no cost, specifically the Arduino platform.
+ An open source schematic capture PCB CAD package was used, specifically KiCad. The CAD files may be used or edited at no cost beyond learning to use the software.

An example of the commonly available part philosophy can be found in the display.  There was great temptation to use a newer OLED color graphical display that would be both fun and attractive.  Rather a mundane 16x2 LCD character display was chosen.  The LDC display is very standard, inexpensive, robust in outdoor settings, available from multiple vendors, and is likely to remain available for a decade or two.  Still, a version based on an OLED display may exist someday just for the fun of it.

Another good example of this is in using a development module for the ESP32 rather than laying out the ESP32 and support electronics directly onto the main PCB.  While much of the design is surface mount, larger packages were used, this allows the entire PCB to be assembled by hand with no more specialized equipment than a decent soldering iron.

Likewise using the Arduino programming platform provides an approachable simplicity that is easily learned.  A huge array of support exists on the web with a robust development community.  Libraries to support Arduino are available from many sources that allow the use of a wide array of sensors, chips, or ready to use modules.

With the controller proving its usefulness across our algae production facility a further decision was made…  To release the controller to the community as an open source device.  Symbrosia is publishing the complete plans…  Schematic, BOM, PCB, 3D models, code, and user manual.

There is nothing exotic or particularly special here.  The Symbrosia Controller is the result of taking a number of parts and solutions that are available in the community and weaving them into a well thought out and robust solution.  The controller has been a good solution for us, maybe you can use it as well.

The Symbrosia Team

## Hardware
The 

## Software

### Firmware

### SyView

### MbMon
MbMon is a ModbusTCP data logger.  This script is often used to do simple datalogging for testing and short experiments.  An XML configuration file is used to designate a few Modbus devices on a local network.  The specified registers are monitored and if needed logged to a CSV file that can be used for data analysis.

MbMon will work with any ModbusTCP device including SymbCtrl, and serve as example code for writing your own logging application.

## Examples
Currently three sample systems are documented here, use these setups as is, or modify them to your own needs...

* [Tank or PBR controller](/samples/PBRCont/)
* [CO<sub>2</sub> Tapping Point Monitor](/samples/CO2Tap/)
* Weather Station(/samples/Weather/)
  
Each of these designs are provided with schematics, 3D models, and setup files for the Symbrosia Controller.



