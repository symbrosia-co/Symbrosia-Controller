/*------------------------------------------------------------------------------

  SymbCtrl - The Symbrosia Aquaculture Controller
  Copyright © 2021 Symbrosia Inc.

  This program is free software: you can redistribute it and/or modify it under 
  the terms of the GNU General Public License as published bythe Free Software
  foundation, either version 3 of the License, or (at your option) any later
  version.

  This program is distributed in the hope that it will be useful, but WITHOUT
  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along with
  this program.  If not, see <https://www.gnu.org/licenses/>.
  
-- required libraries ---------------------------------------------------------

  Library list...   (the following are required for the project)
  - Arduino
  - WiFi, v1.2.7
  - Wire, v2.0.0
  - SPI, v2.0.0
  - EEPROM, v2.0.0
  - LiquidCrystal, v1.0.7
  - ESP32Time, ESP32 RTC time support by Felix Biego v2.0.6
  - ModbusTCP, Modbus TCP support by Alexander Emelianov v4.1.0
  - ESP Rotary, rotary encoder support by Lennart Hennigs v2.1.1
  - Button2, pushbutton support by Lennart Hennigs v2.3.3
  - Adafruit Neopixel, support for the ESP32 RGB neopixel LED v1.12.3
  - MCP_ADC, handling for the MCP3208 AtoD by Rob Tillaart v0.5.1
  - MCP3X21, handling for the MCP3021 AtoD by Pavel Slama v1.0.1
  - esp32FOTA, support for over-the-air firmware update by Chris Joyce v0.2.9
  - ArduinoJSON, JSON file used in firmware update by Benoit Blanchon v7.2.1

-- revision record ------------------------------------------------------------

  24Dec2021 v0.1 A. Cooper
  - initial version, based on Genesis controller
  17Jan2022 A. Cooper
  - converted dedicated control loops to three generic control loops
  - added 30 second startup delay
  10Feb2022 A. Cooper v0.9
  - revised to match new PCB layout
  - removed relay 3
  - added additional control loop, now four outputs and four control loops
  - added supply voltage monitor
  - added processed output
  - reconciled memory maps in memory.h, modbusCtrl.cpp, and documentation
  15Apr2022 A. Cooper
  - all PCB hardware tested and operational, hardware design frozen
  - most basic features now implemented and tested
  - logging will be postponed for first release
  - implemented midnight reset and autosave of parameters
  - added a number of front panel controls to enable/disable/reset
  - added pH calibration from front panel
  - revised memory maps for final release and cleanup from development
  - added status display with Saola RGB neopixel
  - added a clear settings bit to restore defaults in EEPROM
  - fixed memory.setStr bug  
  16Apr2022 A. Cooper
  - added the logic gate controller to handle digitial control
  - added a 1Hz flash register for the logic controller  
  - logic gate function added for multiple inputs including alarms
  - flasher added at 1Hz
  - added two virtual IO registers for the logic gate function
  - added status detection for alarms, low voltage, high temp
  17Apr2022 A. Cooper v1.0
  - first release candidate, deployed on two units
  23Apr2022 A. Cooper v1.1
  - allowed decimal time as control input value to enable time based control
  - added global silence for alarms
  - added unit data screen
  - modified status screen to allow selection of displayed values
  12May2022 A. Cooper v1.2
  - use controller name as WiFi host name, else SymbCtrl if no name set
  - fixed type bug in time based control, fractional hours and minutes not working
  - fixed output change bug, output stayed active when loop output changed
  - added temperature compensation to pH readings
  - display pH temp comp source on WQ screen
  - improved network recovery on outage
  - better handling of invalid NTP time, ToD and time based control inactive
  7July2022 A. Cooper v1.3
  - fixed calibration bug in WQ sensor
  - added dummy read to switch channels and stabilize readings
  - added WiFi network selection and SSID entry to WiFi screen
  - added second WiFi screen to user interface with nework info
  - added unit reset to unit info screen
  - increased analog averaging table to 40 samples
  31July2023 A. Cooper v1.4
  - added asterisk to the allowable WiFi password characters
  - added daily reset to counter and timer
  16Dec2023 v2.0 A. Cooper
  - modify for Mark 2 PCB's
  - use ESP32-S3 in the Wemos S3 Mini form factor
  - LCD interface to 8 bit bus
  - pH is handled by a galvanically isolated MCP3021 single input 10-bit
  AtoD converter using an I2C interface
  - all other AtoD uses 8 channels with an MCP3208 12-bit SAR
  AtoD with an SPI interface
  - rescale all conversion constants for new hardware
  18Jan2024 v2.1 A. Cooper
  - increased A/D averaging substantially
  20Mar2024 v2.1 A. Cooper
  - fixed temperature 2 units bug, using temperature 1 units to flag conversion
  20Mar2024 v2.4 A. Cooper
  - Added and tested support for Wemos ESP32-S2 Mini
  - removed support for ESP32 Saola and older rev PCB's, Rev A and later are supported
  - added limiting to some values upon modbus holding register write
  - finished timer and counter resets hourly and daily
  - better handling of WiFi connection, retries and detection of bad connection, loss of NTP time
  - added screen for internal temp and supply voltage
  - added combined alarm states for each control loop and overall
  - major update/rewrite to timeCtrl toproperly use ESP32 RTC in place of generic Arduino timekeeping library
  - added frequency counter to counter function
  - fixed temperature 2 units bug, using temperature 1 units to flag conversion
  - breaking changes to MCP_ADC library incorporated, now using 0.5.0
  - added offsetHdwr to compensate for average hardware temperature offset
  - added local control loop setpoint adjust
  - added local temperature calibration
  23Apr2024 v2.5 A. Cooper
  - changed temp out-of-range to -30 to 140 (before cal offsets)
  - fixed left scroll out of ScrWiFiDone bug
  - fixed incorrect pin on Digital Output 1 33 to 40 for ESP-S2 mini
  - expanded the alarm bits to add control alarms
  17Jul2024 v2.6 A. Cooper
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
  08Oct2024 v2.7 A. Cooper
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
  02Nov2024 v2.8 A. Cooper
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
  
  Known bugs...
  - none

------------------------------------------------------------------------------*/

//- Library includes -----------------------------------------------------------
#include <Arduino.h>
#include <WiFi.h>
#include <ModbusTCP.h>
#include <Wire.h>
#include <SPI.h>
#include <ESPRotary.h>
#include <Button2.h>
#include <esp32-hal-log.h>
#include <Adafruit_NeoPixel.h>

//- Local includes -------------------------------------------------------------
#include "globals.h"
#include "memory.h"
#include "control.h"
#include "analogCtrl.h"
#include "procCtrl.h"
#include "modbusCtrl.h"
#include "timeCtrl.h"
#include "userCtrl.h"
#include "logicCtrl.h"
#include "todCtrl.h"
#include "countCtrl.h"
#include "fotaCtrl.h"

//- Instantiate Local Libraries ------------------------------------------------
Memory     memory;
TimeCtrl   timeCtrl;
UserCtrl   userCtrl;
AnalogCtrl analogCtrl;
ProcCtrl   procCtrl;
Control    control;
LogicCtrl  logic;
ToDCtrl    todCtrl;
CountCtrl  countCtrl;
FOtACtrl   fotaCtrl;

//- Instantiate IO Libraries ---------------------------------------------------
ESPRotary  encodeRot;
Button2    encodeButton;
#ifdef hardwareS3Mini  // only the S3 has an RGB LED
Adafruit_NeoPixel pixel(1, hdwrRGBLED, NEO_GRB + NEO_KHZ800);
#endif

//- Global variables -----------------------------------------------------------
boolean wifiStat= false;
IPAddress wifiIPAddr;
unsigned long pixelTime= 0;
unsigned long wifiTime= 0;
const bool wifiOn= true;

//- output control -------------------------------------------------------------
bool ctrlMatrix[ctrlOuts][ctrlSrcs];
  
//- low level hardware --------------------------------------------------------- 
void setOutputs(){
  // move manual requests to control matrix
  for (int i=0;i<ctrlOuts;i++)
    ctrlMatrix[i][ctrlExtReq]= memory.getBool(statRelay1Request+i);
  if (!memory.getBool(statStartup))
    // set outputs based on control matrix
    // the matrix collects the various control sources and OR's the result
    // to activate relays, ToD overlays the result
    for (int out= 0;out<ctrlOuts;out++){
      bool result= ((ctrlMatrix[out][ctrlCtrl1]  || ctrlMatrix[out][ctrlCtrl2] ||
                     ctrlMatrix[out][ctrlCtrl3]  || ctrlMatrix[out][ctrlCtrl4] ||
                     ctrlMatrix[out][ctrlLogic]) && ctrlMatrix[out][ctrlToD])  ||
                     ctrlMatrix[out][ctrlExtReq];
      // handle ToD direct control
      if (!control.controlled(out+ioRelay1)
          && todCtrl.controlled(out+ioRelay1)
          && out+ioRelay1!=memory.getInt(datLogicOut))
        result= memory.getBool(statToDActive);
      // set output!
      memory.setBool(statRelay1Status+out,result);
      int state= LOW;
      if (result) state= HIGH;
      switch (out){
        case 0:
         digitalWrite(hdwrRelay1,state);
         break;         
        case 1:
         digitalWrite(hdwrRelay2,state);
         break;         
        case 2:
         digitalWrite(hdwrOutput1,state);
         break;         
        case 3:
         digitalWrite(hdwrOutput2,state);
         break;         
      }
    }
} //setOutputs

void checkStatus(){  
  uint16_t stat= 0;
  // startup
  if (memory.getBool(statStartup)) stat= stat | 1;
  // supply voltage
  if (memory.getFloat(datSupplyVoltage)<alarmVSupLow)  stat= stat | 2;
  if (memory.getFloat(datSupplyVoltage)>alarmVSupHigh) stat= stat | 4;
  // controller temperature
  if (memory.getUInt(datIntTempUnits)==unitsDegC
      && memory.getFloat(datIntTemp)>alarmIntTHigh) stat= stat | 8;
  if (memory.getUInt(datIntTempUnits)==unitsDegF
      && memory.getFloat(datIntTemp)>analogCtrl.CtoF(alarmIntTHigh)) stat= stat | 8;
  // WiFi
  if (!wifiStat) stat= stat | 16;
  // time
  if (!memory.getBool(statNTPTimeValid)) stat= stat | 32;
  // input channels valid, only if channel is in use
  if (control.controlled(ioWQAmp)   && !memory.getBool(statWQSensorValid)) stat= stat | 64;
  if (control.controlled(ioTemp1)   && !memory.getBool(statTemp1Valid))    stat= stat | 128;
  if (control.controlled(ioTemp2)   && !memory.getBool(statTemp2Valid))    stat= stat | 256;
  if (control.controlled(ioAnalog1) && !memory.getBool(statAnalog1Valid))  stat= stat | 512;
  if (control.controlled(ioAnalog2) && !memory.getBool(statAnalog2Valid))  stat= stat | 1024;
  // check control alarms
  if (memory.getBool(statCtrl1Alarm)) stat= stat | 2048;
  if (memory.getBool(statCtrl2Alarm)) stat= stat | 4096;
  if (memory.getBool(statCtrl3Alarm)) stat= stat | 8192;
  if (memory.getBool(statCtrl4Alarm)) stat= stat | 16384;
  if (memory.getBool(statCtrlAlarm))  stat= stat | 32768;
  // write results
  memory.setInt(datStatusCode,stat);
  if (memory.getBool(statStartup)) memory.setBool(statStatus,0);
  else memory.setBool(statStatus,stat==0); 
} // checkStatus

// handle encoder events
void encoderRight(ESPRotary& encodeRot){
  userCtrl.right();
}
void encoderLeft(ESPRotary& encodeRot){
  userCtrl.left();
}
void encoderClick(Button2& click){
  switch (click.getType()) {
    case single_click:
      userCtrl.click();
      break;
    case double_click:  
      userCtrl.dClick();
      break;
    case triple_click:
      userCtrl.dClick();
      break;  
    case long_click:
      userCtrl.press();
      break;
    }
} // encoderClick

// handle midnight reset and save parameter events
void checkMidnight(){
  if (timeCtrl.midnight()){  // wait for midnight
    if (memory.getBool(statMidnightSave)){
      Serial.print("Midnight save of EEPROM... ");
      memory.save();
    }
    if (memory.getBool(statMidnightReset)){
      Serial.print("Resetting processor... ");
      ESP.restart();
    }
  }
} // checkMidnight

void statLED(){
#ifdef hardwareS3Mini  // only the S3 has an RGB LED
  // send every quarter second
  if (millis()<pixelTime) pixelTime= 0;
  if (millis()-pixelTime<250) return;
  pixelTime= millis();
  if (memory.getBool(statStartup)) pixel.setPixelColor(0,180,255,0);
  else if (memory.getBool(statStatus)) pixel.setPixelColor(0,255,0,0);
  else{
    if (memory.getBool(statFlash)) pixel.setPixelColor(0,0,255,0);
    else pixel.setPixelColor(0,0,0,0);
  }
  // send it
  pixel.show();
#endif
  return;
} // statLED

//- Utility --------------------------------------------------------------------

// check for valid I/O channels
bool isIO(int chan){
  if (chan>=ioNone && chan<=ioTofD) return true;
  return false;
}
bool isDigital(int chan){
  if (chan==ioNone) return true;
  if (chan>=ioDigIn1 && chan<=ioFlash) return true;
  if (chan==ioTofD) return true;
  return false;
}
bool isOutput(int chan){
  if (chan==ioNone) return true;
  if (chan>=ioRelay1 && chan<=ioVState2) return true;
  return false;
}
bool isAnalog(int chan){
  if (chan==ioNone) return true;
  if (chan>=ioWQAmp && chan<=ioProcRead) return true;
  if (chan>=ioDays  && chan<=ioSeconds)  return true;
  return false;
}

// get the state of a digital channel
bool getChan(int chan){
  bool result= false;
  if (chan>=ioDigIn1 && chan<=ioFlash) result= memory.getBool(ioAddr[chan]);
  if (chan==ioTofD) result= memory.getBool(ioAddr[chan]);
  return result;
}

// get the value of an analog channel
float getAChan(int chan){
  float result= 0;
  if (chan>=ioWQAmp && chan<=ioProcRead) result= memory.getFloat(ioAddr[chan]);
  if (chan>=ioDays  && chan<=ioSeconds) result= memory.getInt(ioAddr[chan]);
  return result;
}

//- WiFI -----------------------------------------------------------------------
void wifiCheck(){
  if (wifiTime>millis()) wifiTime= 0; // handle millis rollover
  if (millis()-wifiTime>600000){ // check and retry every 10 minutes
    wifiTime= millis();
    if (!wifiStat) wifiConnect();
    if (wifiStat && !ModbusAvailable()) ModbusInit();       
  }
} // wifiCheck

void wifiConnect(){
  userCtrl.setScreen(scrWiFiStart);
  char ssid[18];
  char pass[18];
  char name[18];
  char hostName[28];
  char serNum[8];
  memory.getStr(datWifiAPName,ssid);
  memory.getStr(datWifiPassword,pass);
  memory.getStr(datControlName,name);
  Serial.println("  Initializing WiFi...");
  Serial.print("    SSID:");Serial.println(ssid);
  Serial.print("    Pass:");Serial.println(pass);
  strcpy(hostName,"SymbCtrl");
  for (int i=0;i<strlen(name);i++) if (!isAlphaNumeric(name[i])) name[i]= char(45);
  if (strlen(name)>1) {strcat(hostName,"-");strcat(hostName,name);} 
  else  {strcat(hostName,"-");ultoa(memory.getSerial(),serNum,10);strcat(hostName,serNum);}
  Serial.print("    Name:");Serial.println(hostName);
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(hostName);  
  WiFi.begin(ssid,pass);
  unsigned long timeOut= millis();
  Serial.print("    Connecting ");
  while ((WiFi.status()!= WL_CONNECTED) && ((millis()-timeOut)<20000)){
    delay(500);
    Serial.print("-");
    userCtrl.service();
    }
  if (WiFi.status()==WL_CONNECTED){
    wifiStat= true;
    Serial.println("");
    Serial.println("    WiFi connected");
    Serial.print("    IP address: ");
    Serial.println(WiFi.localIP());
    wifiIPAddr= WiFi.localIP();
    timeCtrl.setTime(); 
    }
  else{
    wifiStat= false;
    Serial.println("");
    Serial.print("    WiFi connection failed to ");
    Serial.println(ssid);
    WiFi.disconnect(true);
    }
  wifiTime= millis();
  userCtrl.setScreen(scrWiFiDone);
} //wifiConnect

//- Setup ----------------------------------------------------------------------
void setup() {
  // IO pin setup
  pinMode(hdwrRelay1,OUTPUT);
  pinMode(hdwrRelay2,OUTPUT);
  pinMode(hdwrOutput1,OUTPUT);
  pinMode(hdwrOutput2,OUTPUT);
  digitalWrite(hdwrRelay1,LOW);
  digitalWrite(hdwrRelay2,LOW);
  digitalWrite(hdwrOutput1,LOW);
  digitalWrite(hdwrOutput2,LOW);
  // get fixed data (serial number, hardware, etc)
  memory.readFixed();
  // control setup
  for (int i=0;i<ctrlOuts;i++)
    for (int j=0;j<ctrlSrcs;j++)
      ctrlMatrix[i][j]= false;
  //start display
  userCtrl.init();
  userCtrl.setScreen(scrSplash);
  userCtrl.service();  
  delay(1000);
  //start user IO hardware
  encodeRot.begin(hdwrEncB,hdwrEncA,4);
  encodeRot.setLeftRotationHandler(encoderLeft);
  encodeRot.setRightRotationHandler(encoderRight);
  encodeButton.begin(hdwrEncoderPB);
  encodeButton.setLongClickTime(1000);
  encodeButton.setClickHandler(encoderClick);
  encodeButton.setLongClickHandler(encoderClick);
  encodeButton.setDoubleClickHandler(encoderClick);
  encodeButton.setTripleClickHandler(encoderClick);
  //serial port init
  Serial.begin(115200);
  delay(500);
  Serial.println("");
  Serial.println("");
  Serial.println("--------------------------------------------");
  Serial.print("Symbrosia Controller                 sn: ");
  Serial.println(memory.getSerial());
  Serial.print(modelNameStr);
  Serial.print("                  Firmware: v");
  Serial.print(firmMajor); Serial.print("."); Serial.println(firmMinor);
  Serial.println("--------------------------------------------");
  Serial.println("Controller startup...");
  Serial.print("  CPU Speed:     ");
  Serial.print(ESP.getCpuFreqMHz());
  Serial.println("MHz");
  Serial.print("  Flash size:    ");
  Serial.println(ESP.getFlashChipSize());
  Serial.print("  Program Size:  ");
  Serial.println(ESP.getSketchSize());
  Serial.print("  Program Space: ");
  Serial.println(ESP.getFreeSketchSpace());
  // RGB pixel setup
#ifdef hardwareS3Mini  // the S3 has an RGB LED
  Serial.println("  Using RGB LED");
  pixel.begin();
  pixel.setBrightness(10);
  pixel.setPixelColor(0,0,0,255);
  pixel.show();
  pixelTime= 0;
#endif
  // first time run? if so, enter fixed data
  bool loadDef= false;
  Serial.println("  Check flash memory...");
  if (memory.getSerial()<serialNumMin || memory.getSerial()>serialNumMax || forceSerial){
    userCtrl.setScreen(scrSerial);
    while(userCtrl.getScreen()!=scrStatus){
      userCtrl.service();
      encodeRot.loop();
      encodeButton.loop();
    }
    Serial.println("    Flash uninitialized!! Fixed data entered");
    loadDef= true;
  }
  // force load of defaults
  if (forceDefaults) Serial.println("    Force load defaults!! (see globals.h)");
  if (loadDef || forceDefaults){
    memory.defaults();
    Serial.println("    Flash defaults loaded");
    memory.save();
  }
  memory.load();
  // set defaults on some memory locations
  memory.setInt(datSerialNumber,memory.getSerial());
  memory.setInt(datModelNumber,memory.getHardware());
  memory.setStr(datModelName,modelNameStr);
  memory.setInt(datFirmwareRev,firmMajor*256+firmMinor);
  memory.setBool(statStatus,true);
  memory.setInt(datStatusCode,0);
  memory.setBool(statSaveSettings,false);
  memory.setBool(statClearSettings,false);
  memory.setBool(statRelay1Request,false);
  memory.setBool(statRelay2Request,false);  
  memory.setBool(statDout1Request,false);
  memory.setBool(statDout2Request,false);
  memory.setBool(statStartup,true);
  // init various modules
  analogCtrl.init();
  control.init();
  logic.init();
  todCtrl.init();
  countCtrl.init();
  procCtrl.init();
  timeCtrl.init();
  // establish WiFi connection
  wifiConnect();
  // setup network services if wifi connected...
  if (wifiStat) ModbusInit();
  Serial.println("  Setup complete, running!");
} // setup

//- Main Loop ------------------------------------------------------------------
void loop() {
  wifiCheck();  
  if (wifiStat){
    ModbusService();
    ModbusHeartbeat();
  }
  timeCtrl.service();  
  userCtrl.service();  
  encodeRot.loop();
  encodeButton.loop();
  analogCtrl.readAll();
  procCtrl.service();
  control.service();
  logic.service();
  todCtrl.service();
  countCtrl.service();
  memory.service();
  checkStatus();
  setOutputs();
  checkMidnight();
  statLED();
} // loop

//- End Symbrosia Controller ---------------------------------------------------
