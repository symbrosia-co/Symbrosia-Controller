  /*----------------------------------------------------------------------------
  Modbus Control - Symbrosia Controller
  - handle the modbus Modbus service
  - move data betwixt the primary data buffer and the modbus registers

  - Written for the ESP32
  - Uses the Arduino Modbus library by Andre Sarmento Barbosa
  info and docs at https://github.com/emelianov/modbus-esp8266
  - This is NOT a class as this version of C does not support using class
  methods for the callback functions
  
  25Dec2021 A. Cooper
  - initial version
  01Jan2022 A. Cooper
  - abandoned buf/reg updates and moved all the action to the callbacks
  - tested and operational
  21Jan2022 A. Cooper
  - removed register types
  - revised memory map for new arrangement
  15Apr2022 A. Cooper
  - revised memory map for first release
  23Mar2024 v2.4 A. Cooper
  - add call to limit on modbus holding register write

--------------------------------------------------------------------------------

    SymbCtrl - The Symbrosia Aquaculture Controller
    Copyright © 2021 Symbrosia Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

------------------------------------------------------------------------------*/

//- library includes -----------------------------------------------------------
#include <Arduino.h>
#include <ModbusTCP.h>

//- Local includes -------------------------------------------------------------
#include "modbusCtrl.h"
#include "globals.h"
#include "Memory.h"
extern Memory memory;

//- instantiate ----------------------------------------------------------------
ModbusTCP mb;  //ModbusTCP object

//- handling and restriction maps ----------------------------------------------

// handling code for each holding register
//  - 'r' read only
//  - 'w' write only
//  - '+' read and write
#define mbRWModeSize 177
const char mbHoldRWMode[dataSize]= {
  'r', //   0 datStatusCode
  'r', //   1 datModelNumber
  'r', //   2 datSerialNumber
  '+', //   3 datSoftwareRev
  '+', //   4 datHeartbeatIn
  'r', //   5 datHeartbeatOut
  '+', //   6 nc
  '+', //   7 nc
  '+', //   8 datStatusDisp1
  '+', //   9 datStatusDisp2
  '+', //  10 datTimezone
  'r', //  11 datYear
  'r', //  12 datMonth
  'r', //  13 datDay
  'r', //  14 datHour
  'r', //  15 datMinute
  'r', //  16 datSecond
  '+', //  17 nc
  '+', //  18 nc
  '+', //  19 nc
  'r', //  20 datWQ
  'r', //  21
  'r', //  22 datTemperature1
  'r', //  23
  'r', //  24 datTemperature2
  'r', //  25
  'r', //  26 datAnalog1
  'r', //  27
  'r', //  28 datAnalog2
  'r', //  29
  'r', //  30 datIntTemp
  'r', //  31
  'r', //  32 datSupplyVoltage
  'r', //  33
  'r', //  34 datProcessedRead
  'r', //  35
  '+', //  36 datWQSensorUnits
  '+', //  37 datTemp1Units
  '+', //  38 datTemp2Units
  '+', //  39 datAnalog1Units
  '+', //  40 datAnalog2Units
  '+', //  41 datIntTempUnits
  '+', //  42 datSupVoltUnits
  'r', //  43 datProcReadUnits
  '+', //  44 datPHTempComp
  '+', //  45 nc
  '+', //  46 nc
  '+', //  47 nc
  '+', //  48 nc
  '+', //  49 nc
  '+', //  50 datWQOffset
  '+', //  51
  '+', //  52 datTemp1Offset
  '+', //  53
  '+', //  54 datTemp2Offset
  '+', //  55
  '+', //  56 datAnalog1Offset
  '+', //  57
  '+', //  58 datAnalog2Offset
  '+', //  59
  '+', //  60 datWQGain
  '+', //  61
  '+', //  62 datTemp1Gain
  '+', //  63
  '+', //  64 datTemp2Gain
  '+', //  65
  '+', //  66 datAnalog1Gain
  '+', //  67
  '+', //  68 datAnalog2Gain
  '+', //  69
  '+', //  70 datCtrl1Input
  '+', //  71 datCtrl1Output
  '+', //  72 datCtrl1Setpoint
  '+', //  73
  '+', //  74 datCtrl1Hysteresis
  '+', //  75
  '+', //  76 datCtrl1AlarmLow
  '+', //  77
  '+', //  78 datCtrl1AlarmHigh
  '+', //  79
  '+', //  80 datCtrl1EnbSource
  '+', //  81 datCtrl1MinOnTime
  'r', //  82 datCtrl1Minimum
  'r', //  83
  'r', //  84 datCtrl1Maximum
  'r', //  85
  '+', //  86 datCtrl2Input
  '+', //  87 datCtrl2Output
  '+', //  88 datCtrl2Setpoint
  '+', //  89
  '+', //  90 datCtrl2Hysteresis
  '+', //  91
  '+', //  92 datCtrl2AlarmLow
  '+', //  93
  '+', //  94 datCtrl2AlarmHigh
  '+', //  95
  '+', //  96 datCtrl2EnbSource
  '+', //  97 datCtrl2MinOnTime
  'r', //  98 datCtrl2Minimum
  'r', //  99
  'r', // 100 datCtrl2Maximum
  'r', // 101
  '+', // 102 datCtrl3Input
  '+', // 103 datCtrl3Output
  '+', // 104 datCtrl3Setpoint
  '+', // 105
  '+', // 106 datCtrl3Hysteresis
  '+', // 107
  '+', // 108 datCtrl3AlarmLow
  '+', // 109
  '+', // 110 datCtrl3AlarmHigh
  '+', // 111
  '+', // 112 datCtrl3EnbSource
  '+', // 113 datCtrl3MinOnTime
  'r', // 114 datCtrl3Minimum
  'r', // 115
  'r', // 116 datCtrl3Maximum
  'r', // 117
  '+', // 118 datCtrl4Input
  '+', // 119 datCtrl4Output
  '+', // 120 datCtrl4Setpoint
  '+', // 121
  '+', // 122 datCtrl4Hysteresis
  '+', // 123
  '+', // 124 datCtrl4AlarmLow
  '+', // 125
  '+', // 126 datCtrl4AlarmHigh
  '+', // 127
  '+', // 128 datCtrl4EnbSource
  '+', // 129 datCtrl4MinOnTime
  'r', // 130 datCtrl3Minimum
  'r', // 131
  'r', // 132 datCtrl3Maximum
  'r', // 133
  '+', // 134 nc
  '+', // 135 nc
  '+', // 136 datLogicInA
  '+', // 137 datLogicInB
  '+', // 138 datLogicFunction
  '+', // 139 datLogicOutput
  '+', // 140 datToDStartHour
  '+', // 141 datToDStartMin
  '+', // 142 datToDStopHour
  '+', // 143 datToDStopMin
  '+', // 144 datToDOutput1
  '+', // 145 datToDOutput2
  '+', // 146 datToDOutput3
  '+', // 147 datToDOutput4
  '+', // 148 nc
  '+', // 149 nc
  '+', // 150 datCountSource
  'r', // 151 datCounter
  'r', // 152
  '+', // 153 datCountRstIntv
  '+', // 154 datTimerSource
  'r', // 155 datTimer
  'r', // 156
  '+', // 157 datTimerRstIntv
  '+', // 158 nc
  '+', // 159 nc
  '+', // 160 datLogInterval
  'r', // 161 datLogRecords
  'w', // 162 datLogNumber
  'w', // 163 datLogItem
  'r', // 164 datLogData
  'r', // 165
  '+', // 166 datProcessChanA
  '+', // 167 datProcessChanB
  '+', // 168 datProcessID
  '+', // 169 nc
  'r', // 170 Model Name
  'r', // 171
  'r', // 172
  'r', // 173
  'r', // 174
  'r', // 175
  'r', // 176
  'r'};// 177

// handling code for each coil register
//  - 'r' read only
//  - 'w' write only
//  - '+' read and write
const char mbCoilRWMode[statSize]= {
  'r', //   0 statStatus
  'r', //   1 statNTPTimeValid
  'r', //   2 statStartup
  'w', //   3 statSaveSettings
  'w', //   4 statClearSettings  
  '+', //   5 statMidnightSave
  '+', //   6 statMidnightReset
  '+', //   7 statSilenceAlarms
  'r', //   8 statDigitalIn1
  'r', //   9 statDigitalIn2
  'r', //  10 statRelay1Status
  'r', //  11 statRelay2Status
  'r', //  12 statDigitalOut1
  'r', //  13 statDigitalOut2
  '+', //  14 Relay 1 Request
  '+', //  15 Relay 2 Request
  '+', //  16 DOut 1 Request
  '+', //  17 DOut 2 Request
  '+', //  18 virtual state A
  '+', //  19 virtual state B
  'r', //  20 statWQSensorValid
  'r', //  21 statTemp1Valid
  'r', //  22 statTemp2Valid
  'r', //  23 statAnalog1Valid
  'r', //  24 statAnalog2Valid
  'r', //  25 statIntTempValid
  'r', //  26 statSupVoltValid
  'r', //  27 statProcReadValid
  'r', //  28 statLogicGateResult
  'r', //  29 statFlash
  '+', //  30 statCtrl1Enable
  '+', //  31 statCtrl2Enable
  '+', //  32 statCtrl3Enable
  '+', //  33 statCtrl4Enable
  '+', //  34 statCtrl1High
  '+', //  35 statCtrl2High
  '+', //  36 statCtrl3High
  '+', //  37 statCtrl4High
  'r', //  38 statCtrl1Active
  'r', //  39 statCtrl2Active
  'r', //  40 statCtrl3Active
  'r', //  41 statCtrl4Active
  'r', //  42 statCtrlAlarm
  'r', //  43 statCtrl1Alarm
  'r', //  44 statCtrl2Alarm
  'r', //  45 statCtrl3Alarm
  'r', //  46 statCtrl4Alarm
  'r', //  47 statCtrl1AlarmLow
  'r', //  48 statCtrl2AlarmLow
  'r', //  49 statCtrl3AlarmLow
  'r', //  50 statCtrl4AlarmLow
  'r', //  51 statCtrl1AlarmHigh
  'r', //  52 statCtrl2AlarmHigh
  'r', //  53 statCtrl3AlarmHigh
  'r', //  54 statCtrl4AlarmHigh
  'w', //  55 statRstCtrl1Max
  'w', //  56 statRstCtrl2Max
  'w', //  57 statRstCtrl3Max
  'w', //  58 statRstCtrl4Max
  '+', //  59 statCounterEnable
  '+', //  60 statTimerEnable
  '+', //  61 statToDEnable
  'r', //  62 statToDActive
  'w', //  63 statResetCounter
  'w', //  64 statResetTimer
  'w', //  65 statResetLogging
  '+', //  66 statCtrl1OneShot
  '+', //  67 statCtrl2OneShot
  '+', //  68 statCtrl3OneShot
  '+'};//  69 statCtrl4OneShot

  bool mbActive;
  bool mbAvailable;
  unsigned long mbTime;

//- functions ------------------------------------------------------------------

void ModbusInit(){
  Serial.println("  Initialize Modbus server...");
  mb.server();
  mbAvailable=  true;
  mbActive=     false;
  mbTime= 0;
  //setup needed registers
  mb.addCoil(0+mbBaseCoil,0,statSize);
  mb.addHreg(0+mbBaseHold,0,dataSize);
  mb.onGetCoil(0+mbBaseCoil,ModbusOnReadCoil,statSize);
  mb.onSetCoil(0+mbBaseCoil,ModbusOnWriteCoil,statSize);
  mb.onGetHreg(0+mbBaseHold,ModbusOnReadHold,dataSize);
  mb.onSetHreg(0+mbBaseHold,ModbusOnWriteHold,dataSize);
  Serial.println("    Modbus registers defined");
  Serial.println("    Modbus server running");
  return;
} // ModbusInit

void ModbusService(){
  if (!mbAvailable) return;
  //  allow modbus to service requests
  mb.task();
  // keep active flag for 10 sec after external read or write
  if ((millis()-mbTime)<10000) mbActive= true;
  else mbActive= false;
  // Serial.print(millis());
  // Serial.print("  ");
  // Serial.print(mbTime);
  // Serial.print("  ");
  // Serial.println(mbActive);
} // ModbusService

void ModbusHeartbeat(){
  memory.setInt(datHeartbeatOut,memory.getInt(datHeartbeatIn));
} // ModbusHeartbeat

bool ModbusActive(){
  if (!wifiStat) return false;
  if (!mbAvailable) return false;
  return mbActive;
} // ModbusActive

bool ModbusAvailable(){
  if (!wifiStat) return false;
  return mbAvailable;
} // ModbusAvailable

char ModbusGetHoldMode(int addr){
  if (addr>=0 && addr<dataSize) return mbHoldRWMode[addr];
  return 0;
} // ModbusGetHoldMode

char ModbusGetCoilMode(int addr){
  if (addr>=0 && addr<statSize) return mbCoilRWMode[addr];
  return 0;
} // ModbusGetHoldType

int ModbusGetHoldSize(){
  return dataSize;
} // ModbusGetHoldSize

int ModbusGetCoilSize(){
  return statSize;
} // ModbusGetCoilSize

//- Callbacks ------------------------------------------------------------------

uint16_t ModbusOnReadHold(TRegister* reg, uint16_t val){
  // Serial.println("Read Hold!");
  // Serial.print("      Address: ");
  // Serial.println(reg->address.address);  
  // Serial.print("      Value:   ");
  // Serial.println(memory.getInt((reg->address.address)-mbBaseHold));
  mbTime= millis();
  int addr= reg->address.address-mbBaseHold;
  if (addr>mbRWModeSize && addr<dataSize) // mbRWModeSize is the end of the r/w reference array
    return memory.getInt(addr);
  if (mbHoldRWMode[addr]=='r' || mbHoldRWMode[addr]=='+') 
    return memory.getInt(addr);
  return 0;
} // ModbusOnReadHold

uint16_t ModbusOnWriteHold(TRegister* reg, uint16_t val){
  // Serial.println("    Write Hold!");
  // Serial.print("      Address: ");
  // Serial.println(reg->address.address);
  // Serial.print("      Value:   ");
  // Serial.println(val);
  mbTime= millis();
  int addr= reg->address.address-mbBaseHold;
  if (addr>mbRWModeSize && addr<dataSize){ // mbRWModeSize is the end of the r/w reference array
    memory.setUInt(addr,val);
    return val;
  }
  if (mbHoldRWMode[addr]=='w' || mbHoldRWMode[addr]=='+'){
    if (addr==datTimezone) memory.setInt(addr,val);//Timezone is the only signed integer
    else memory.setUInt(addr,val);
    memory.limitCheck();
    return val;
  }
  return 0;
} // ModbusOnWriteHold

uint16_t ModbusOnReadCoil(TRegister* reg, uint16_t val){
  // Serial.println("Read Coil!");
  // Serial.print("      Address: ");
  // Serial.println(reg->address.address);
  // Serial.print("      Value:   ");
  // Serial.println(memory.getBool((reg->address.address)-mbBaseCoil));
  mbTime= millis();
  if (memory.getBool((reg->address.address)-mbBaseCoil)) return 65280;
  else return 0;
} // ModbusOnReadCoil

uint16_t ModbusOnWriteCoil(TRegister* reg, uint16_t val){
  // Serial.println("Write Coil!");
  // Serial.print("      Address: ");
  // Serial.println(reg->address.address);
  // Serial.print("      Value:   ");
  // Serial.println(val);
  mbTime= millis();
  int addr= reg->address.address-mbBaseCoil;
  if (mbCoilRWMode[addr]=='w' || mbCoilRWMode[addr]=='+'){
      if (val==65280) memory.setBool(addr,true);
      else memory.setBool(addr,false);
      return val;
    }
  if (memory.getBool(addr)) return 65280; // 65280 is a magic number for true in modbus
  return 0;
} // ModbusOnWriteCoil

//- End modbusCtrl -------------------------------------------------------------
