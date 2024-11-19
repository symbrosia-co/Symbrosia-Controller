# SymbCtrl
SymbCtrl is the operational firmware for the Symbrosia Controller.

Two processor modules are supported, the Lolin ESP32 S2 Mini and the ESP32 S3 Mini.  The current version of the controler was designed for the latest S3 processor.  This processor has occasionally been scarce, thus the code was modified to support the much more common S2 version.  Both versions can be accomodated easily.

While the initial programming of a new processor module must be done with a direct cabled download, subsequent firmware upgrades can be handled easily using an over-the-air firmware update.  The updated firmware binary files are hosted here on Github.

![SymbCtrl PCB assembly top](/res/SymbCtrlPCB.png)

## Aurduino IDE 2.x setup

SymbCtrl is to be compiled and downloaded to the controller using the Arduino IDE. If you do not already have it, download and install the latest Arduino IDE 2.x at [Arduino Software](https://www.arduino.cc/en/software)

The following libraries are used and are part of the basic Arduino install, these should be avaialble without additional steps to install.
  - Arduino
  - WiFi, v1.2.7
  - Wire, v2.0.0
  - SPI, v2.0.0
  - EEPROM, v2.0.0
  - LiquidCrystal, v1.0.7

The following libraries need to be installed to compile SymbCtrl.  Use the library tab in the sidebar to search for each library by name, then use the install button to make the library available.  Some Arduino libraries share similar names, double check that the library matches the information shown below.  

The versions shown are the currently used versions, mostl likely that or any later version should work.  If errors appear use the Arduino library tab to roll the version back to the known good version shown below. 

  - ESP32Time, ESP32 RTC time support by Felix Biego v2.0.6
  - ModbusTCP, Modbus TCP support by Alexander Emelianov v4.0.0
  - ESP Rotary, rotary encoder support by Lennart Hennigs v1.4.2
  - Button2, pushbutton support by Lennart Hennigs v1.6.5
  - Adafruit Neopixel, support for the ESP32 RGB neopixel LED v1.10.4
  - MCP3208 AtoD handled by MCP_ADC by Rob Tillaart v0.5.0
  - esp32FOTA, support for over-the-air firmware update by Chris Joyce v0.2.9
  - ArduinoJSON, JSON file used in firmware update by Benoit Blanchon v7.2.1

Simply open the SymbCtrl.ino file with the IDE to begin work.

# Revision Record

## v2.6 17Jul2024
  - Added alarm bits to the status register
  - revised ToD logic to change behavior, ToD active will reflect ToD enable
  - cleaned up code in TofDay
  - major modifications to control:service
    - added control enable with external sources
    - added one-shot enable
    - added minimim on/off time
  - removed a decimal point from status screen analog values
  - allow any IO channel on status display
  - changed from boxcar average to a tracking average in analogCtrl
  - added TofD to IO channel list
  - corrected bug: alarm if internal temp was in Deg F
  - major re-write of the processed reading, all methods now operate
  like priority in passing a value through
  - added CtoF to analogCtrl
  - some corrections to pH temperature calibration, tested successfully
  - apply gain and offset to analog inputs last using selected units
  - removed MCP3021 library, use direct calls to Wire
  - added auto I2C address search for MCP3021
  - a successful functional test performed
  - concat SymbCtrl to unit name to make network name

##  v2.7 08Oct2024
  - major re-write of userCtrl to clean up the methods for handling user
    input such as calibration and WiFi credential input, it needed it
  - solved WiFi.scanNetworks bug, would not initiate a scan when the
    previous network connection or connection attempt was not fully
    terminated, use WiFi.disconnect with a wifioff=true to fully
    disconnect and shutdown the conection before an SSID scan
  - change memory.save to memory.saveFloat in calibration routines
  - change memory.save to memory.saveWiFi in credential entry routine
  - restart userSetTime timeout on all encoder or button input
  - add manual offset adjustment to analog inputs
  - add indication of manual NTP fetch
  - re-write pH calibration process to reduce putton pushing
  - add simple offset adjustment to WQ input when not used for pH
  - change ToD logic to not use direct mode as long as any controller
    has the channel whether the controller is enabled or disabled
  - changed serial messages during EEPROM load
  - show sensor name on WQ screen
  - do not use priority for sum or difference in processed reading, lose
    any reading => invalid
    
##  v2.8 02Nov2024
  - Set up code for fota using esp32FOTA by Chris Joyce
  - new serial number assignment method at first boot on new unit
  - reserve bytes at start of flash for fixed information including
  serial number and hardware information
  - add setSerial, setHardware, and setProcessor methods to memory
  - add getSerial, getHardware, and getProcessor methods to memory
  - add getWQInstalled and setWQInstalled methods to memory
  - modify setup to handle fixed memory entry if needed on startup,
  setup will block while looping userCtrl.service, encoder, and button
  - in userCtrl add screens for fixed data entry
  - in userCtrl add screen for firmware update
  - in userCtrl move reset function to status screen
  - in userCtrl add firmware update to unit info screen

  ---
