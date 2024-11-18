/*------------------------------------------------------------------------------
  Memory - Symbrosia Controller
  - maintain primary data structure, echoed to modbus registers
  - keep configuration in flash memory

  02Jan2022 A. Cooper
  - initial version
  15Apr2022 A. Cooper
  - added getLong/setLong
  23Mar2024 v2.4 A. Cooper
  - added limiting to some values upon modbus holding register write
  31Jul2024 v2.6 A. Cooper
  - added value restriction for internal temperature units
  - added value restriction for control enable source
  31Jul2024 v2.7 A. Cooper
  - add saveFloat to allow storing of calibration values without global save
  - add saveWiFi to allow storing credentials without global save
  - changed serial messages during EEPROM load
  02Nov2024 v2.8 A. Cooper
  - reserve 16 bytes at start of flash for fixed information including
  serial number and hardware information
  - add setSerial, setHdwr, and getProcessor methods
  - add getSerial, getHdwr, and getProcessor methods
  - add readOne and saveOne methods for use on fixed memory
  - add readFixed to read and buffer fixed memory in fixed[]

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
#include <EEPROM.h>

//- Local includes -------------------------------------------------------------
#include "globals.h"
#include "memory.h"
extern bool isIO(int chan);
extern bool isDigital(int chan);
extern bool isOutput(int chan);
extern bool isAnalog(int chan);

//- functions ------------------------------------------------------------------
Memory::Memory(){
  stat[0]= false;
  checkLimits= false;
}

int16_t Memory::getInt(uint16_t addr){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal read address in getInt!!");
    return 0;
  }
  return data[addr];
}

void Memory::setInt(uint16_t addr,int16_t val){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal write address in setInt!!");
    return;
  }
  data[addr]= int(val);
}

uint16_t Memory::getUInt(uint16_t addr){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal read address in getUInt!!");
    return 0;  
  }
  return data[addr];
}

void Memory::setUInt(uint16_t addr,uint16_t val){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal write address in setUInt!!");
    return;
  }
  data[addr]= val;
}

unsigned long Memory::getLong(uint16_t addr){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal read address in getLong!!");
    return 0;
  }
  return *((unsigned long *)(data+addr));
}

void Memory::setLong(uint16_t addr,unsigned long val){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal write address in setLong!!");
    return;
  }
  *((unsigned long *)(data+addr))= val;
}

float Memory::getFloat(uint16_t addr){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal read address in getFloat!!");
    return 0;
  }
  return *((float *)(data+addr));
}

void Memory::setFloat(uint16_t addr,float val){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal write address in setFloat!!");
    return;
  }
  *((float *)(data+addr))= val;
}

char Memory::getChar(uint16_t addr){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal read address in getChar!!");
    return 0;
  }
  return data[addr];
}

void Memory::setChar(uint16_t addr,char val){
  if (addr<0 || addr>dataSize){
    Serial.println("Illegal write address in setChar!!");
    return;
  }
  data[addr]= char(val);
}

// retrieve a string from register memory, max length of 16 chars
// the string will be unpacked from the two chars per 16bit register format
// the array of chars result must be declared at least 17 chars long to
//   accomodate a terminating null
void Memory::getStr(uint16_t addr,char* st){
  if (addr<0 || addr>dataSize-8){
    Serial.println("Illegal read address in getStr!!");
    return;
  }
  for (int i=0;i<8;i++){
    st[2*i]= char(highByte(data[addr+i]));
    if (st[2*i]==0) break;
    st[2*i+1]= char(lowByte(data[addr+i]));
    if (st[2*i+1]==0) break;
  }
  st[16]= 0;
}

// place a packed string into register memory, two chars per 16bit register
// maximum of a 16 character string (arbitrary limit), null terminated
void Memory::setStr(uint16_t addr,const char* str){
  if (addr<0 || addr>dataSize-8){
    Serial.println("Illegal write address in setStr!!");
    return;
  }
  int val=0;
  for (int i=0;i<8;i++){
    if (str[i*2]==0){
      data[addr+i]= 0;
      break;
    }      
    val= str[i*2];
    val= val*256+str[(i*2)+1];   
    data[addr+i]= val;
    if (str[(i*2)+1]==0)
      break;
  }
}

bool Memory::getBool(uint16_t addr){
  if (addr<0 || addr>statSize){
    Serial.println("Illegal read address in getBool!!");
    return false;
  }
  return stat[addr];
}

void Memory::setBool(uint16_t addr,bool val){
  if (addr<0 || addr>statSize){
    Serial.print("Illegal write address in setBool!!  ");
    Serial.println(addr);
    return;
  }
  stat[addr]= val;
}

// set default values for most memory locations
void Memory::defaults(){
  // zero buffer contents
  for (int i=0;i<datSizeClear;i++) data[i]=0; //do not clear wifi credentials
  for (int i=0;i<statSize;i++) stat[i]=false;
  // set specific items
  setInt  (datModelNumber,fixed[addrHardware]);
  setInt  (datSerialNumber,fixed[addrSerial]);
  setStr  (datModelName,modelNameStr);
  setStr  (datWifiAPName,defWiFi);
  setStr  (datWifiPassword,defPass);
  setInt  (datFirmwareRev,firmMajor*256+firmMinor);
  setBool (statMidnightSave,    false);
  setBool (statMidnightReset,   false);
  setInt  (datStatusDisp1,      ioWQAmp);
  setInt  (datStatusDisp2,      ioTemp1);
  setInt  (datTimezone,         timeZone);
  setInt  (datWQSensorUnits,    unitspH);
  setInt  (datTemp1Units,       unitsDegC);
  setInt  (datTemp2Units,       unitsDegC);
  setInt  (datAnalog1Units,     unitsV);
  setInt  (datAnalog2Units,     unitsV);
  setInt  (datIntTempUnits,     unitsDegC);
  setInt  (datSupVoltUnits,     unitsV);
  setInt  (datProcUnits,        ioNone);
  setFloat(datWQGain,           1);
  setFloat(datTemp1Gain,        1);
  setFloat(datTemp2Gain,        1);
  setFloat(datAnalog1Gain,      1);
  setFloat(datAnalog2Gain,      1);
  setFloat(datAnalog2Gain,      1);
  setInt  (datCtrl1Input,       ioNone);
  setFloat(datCtrl1Setpoint,    1);
  setFloat(datCtrl1Hysteresis,  1);
  setFloat(datCtrl1AlarmLow,    0);
  setFloat(datCtrl1AlarmHigh,   2);
  setBool (statCtrl1High,       true);
  setInt  (datCtrl2Input,       ioNone);
  setFloat(datCtrl2Setpoint,    1);
  setFloat(datCtrl2Hysteresis,  1);
  setFloat(datCtrl2AlarmLow,    0);
  setFloat(datCtrl2AlarmHigh,   2);
  setBool (statCtrl2High,       true);
  setInt  (datCtrl3Input,       ioNone);
  setFloat(datCtrl3Setpoint,    1);
  setFloat(datCtrl3Hysteresis,  1);
  setFloat(datCtrl3AlarmLow,    0);
  setFloat(datCtrl3AlarmHigh,   2);
  setBool (statCtrl3High,       true);
  setInt  (datCtrl4Input,       ioNone);
  setFloat(datCtrl4Setpoint,    1);
  setFloat(datCtrl4Hysteresis,  1); 
  setFloat(datCtrl4AlarmLow,    0);
  setFloat(datCtrl4AlarmHigh,   2);
  setBool (statCtrl4High,       true);
  setInt  (datToDStartHour,     6);
  setInt  (datToDStopHour,      18);
  setInt  (datLogInterval,      10);
} // defaults

// limit some memory locations to specified ranges
void Memory::limit(){
  if (!isIO(getUInt(datStatusDisp1)))      setUInt(datStatusDisp1,ioNone);
  if (!isIO(getUInt(datStatusDisp2)))      setUInt(datStatusDisp2,ioNone);
  if (getInt(datTimezone)<minTimezone)     setInt(datTimezone,minTimezone);
  if (getInt(datTimezone)>maxTimezone)     setInt(datTimezone,maxTimezone);
  if (getUInt(datWQSensorUnits)<minUnits)  setUInt(datWQSensorUnits,minUnits);
  if (getUInt(datWQSensorUnits)>maxUnits)  setUInt(datWQSensorUnits,maxUnits);
  if (getUInt(datTemp1Units)<minTempUnits) setUInt(datTemp1Units,unitsDegC);
  if (getUInt(datTemp1Units)>maxTempUnits) setUInt(datTemp1Units,unitsDegC);
  if (getUInt(datTemp2Units)<minTempUnits) setUInt(datTemp2Units,unitsDegC);
  if (getUInt(datTemp2Units)>maxTempUnits) setUInt(datTemp2Units,unitsDegC);
  if (getUInt(datAnalog1Units)<minUnits)   setUInt(datAnalog1Units,minUnits);
  if (getUInt(datAnalog1Units)>maxUnits)   setUInt(datAnalog1Units,maxUnits);
  if (getUInt(datAnalog2Units)<minUnits)   setUInt(datAnalog2Units,minUnits);
  if (getUInt(datAnalog2Units)>maxUnits)   setUInt(datAnalog2Units,maxUnits);
  if (getUInt(datIntTempUnits)<minTempUnits) setUInt(datIntTempUnits,unitsDegC);
  if (getUInt(datIntTempUnits)>maxTempUnits) setUInt(datIntTempUnits,unitsDegC);
  // control 1
  if (!isAnalog(getUInt(datCtrl1Input)))  setUInt(datCtrl1Input,ioNone);
  if (!isOutput(getUInt(datCtrl1Output))) setUInt(datCtrl1Output,ioNone);
  if (getUInt(datCtrl1MinOnTime)<minOnOffTime) setUInt(datCtrl1MinOnTime,minOnOffTime);
  if (getUInt(datCtrl1MinOnTime)>maxOnOffTime) setUInt(datCtrl1MinOnTime,maxOnOffTime);
  if (!isDigital(getUInt(datCtrl1EnbSource))) setUInt(datCtrl1EnbSource,ioNone);
  if (getUInt(datCtrl1EnbSource)==getUInt(datCtrl1Output)) setUInt(datCtrl1EnbSource,ioNone);
  // control 2
  if (!isAnalog(getUInt(datCtrl2Input)))  setUInt(datCtrl2Input,ioNone);
  if (!isOutput(getUInt(datCtrl2Output))) setUInt(datCtrl2Output,ioNone);
  if (getUInt(datCtrl2MinOnTime)<minOnOffTime) setUInt(datCtrl2MinOnTime,minOnOffTime);
  if (getUInt(datCtrl2MinOnTime)>maxOnOffTime) setUInt(datCtrl2MinOnTime,maxOnOffTime);
  if (!isDigital(getUInt(datCtrl2EnbSource))) setUInt(datCtrl2EnbSource,ioNone);
  if (getUInt(datCtrl2EnbSource)==getUInt(datCtrl2Output)) setUInt(datCtrl2EnbSource,ioNone);
  // control 3
  if (!isAnalog(getUInt(datCtrl3Input)))  setUInt(datCtrl3Input,ioNone);
  if (!isOutput(getUInt(datCtrl3Output))) setUInt(datCtrl3Output,ioNone);
  if (getUInt(datCtrl3MinOnTime)<minOnOffTime) setUInt(datCtrl3MinOnTime,minOnOffTime);
  if (getUInt(datCtrl3MinOnTime)>maxOnOffTime) setUInt(datCtrl3MinOnTime,maxOnOffTime);
  if (!isDigital(getUInt(datCtrl3EnbSource))) setUInt(datCtrl3EnbSource,ioNone);
  if (getUInt(datCtrl3EnbSource)==getUInt(datCtrl3Output)) setUInt(datCtrl3EnbSource,ioNone);
  // control 4
  if (!isAnalog(getUInt(datCtrl4Input)))  setUInt(datCtrl4Input,ioNone);
  if (!isOutput(getUInt(datCtrl4Output))) setUInt(datCtrl4Output,ioNone);
  if (getUInt(datCtrl4MinOnTime)<minOnOffTime) setUInt(datCtrl4MinOnTime,minOnOffTime);
  if (getUInt(datCtrl4MinOnTime)>maxOnOffTime) setUInt(datCtrl4MinOnTime,maxOnOffTime);
  if (!isDigital(getUInt(datCtrl4EnbSource))) setUInt(datCtrl4EnbSource,ioNone);
  if (getUInt(datCtrl4EnbSource)==getUInt(datCtrl4Output)) setUInt(datCtrl4EnbSource,ioNone);
  // logic gate
  if (!isDigital(getUInt(datLogicInA)))  setUInt(datLogicInA,ioNone);
  if (!isDigital(getUInt(datLogicInB)))  setUInt(datLogicInB,ioNone);
  if (getUInt(datLogicFunction)<minLogicFunc)  setUInt(datLogicFunction,minLogicFunc);
  if (getUInt(datLogicFunction)>maxLogicFunc)  setUInt(datLogicFunction,maxLogicFunc);
  if (!isOutput(getUInt(datLogicOut)))  setUInt(datLogicOut,ioNone);
  // ensure no loops in logic gate
  if (getUInt(datLogicOut)==getUInt(datLogicInA)) setUInt(datLogicOut,ioNone);
  if (getUInt(datLogicOut)==getUInt(datLogicInB)) setUInt(datLogicOut,ioNone);
  // TofD
  if (getUInt(datToDStartHour)<minHour)  setUInt(datToDStartHour,minHour);
  if (getUInt(datToDStartHour)>maxHour)  setUInt(datToDStartHour,maxHour);
  if (getUInt(datToDStopHour)<minHour)   setUInt(datToDStopHour,minHour);
  if (getUInt(datToDStopHour)>maxHour)   setUInt(datToDStopHour,maxHour);
  if (getUInt(datToDStartMin)<minMinute) setUInt(datToDStartMin,minMinute);
  if (getUInt(datToDStartMin)>maxMinute) setUInt(datToDStartMin,maxMinute);
  if (getUInt(datToDStopMin)<minMinute)  setUInt(datToDStopMin,minMinute);
  if (getUInt(datToDStopMin)>maxMinute)  setUInt(datToDStopMin,maxMinute);
  if (!isOutput(getUInt(datToDOutput1))) setUInt(datToDOutput1,ioNone);
  if (!isOutput(getUInt(datToDOutput2))) setUInt(datToDOutput2,ioNone);
  if (!isOutput(getUInt(datToDOutput3))) setUInt(datToDOutput3,ioNone);
  if (!isOutput(getUInt(datToDOutput4))) setUInt(datToDOutput4,ioNone);
  // counter and timer
  if (!isDigital(getUInt(datCountSource)))   setUInt(datCountSource,ioNone);
  if (!isDigital(getUInt(datTimerSource)))   setUInt(datTimerSource,ioNone);
  if (getUInt(datCountRstIntv)<minResetIntv) setUInt(datCountRstIntv,minResetIntv);
  if (getUInt(datCountRstIntv)>maxResetIntv) setUInt(datCountRstIntv,maxResetIntv);
  if (getUInt(datTimerRstIntv)<minResetIntv) setUInt(datTimerRstIntv,minResetIntv);
  if (getUInt(datTimerRstIntv)>maxResetIntv) setUInt(datTimerRstIntv,maxResetIntv);
  // processed inputs
  if (!isAnalog(getUInt(datProcessChanA)))  setUInt(datProcessChanA,ioNone);
  if (!isAnalog(getUInt(datProcessChanB)))  setUInt(datProcessChanB,ioNone);
  if (getUInt(datProcessID)<minProcess)     setUInt(datProcessID,minProcess);
  if (getUInt(datProcessID)>maxProcess)     setUInt(datProcessID,maxProcess);
  // other
  if (getUInt(datLogInterval)<minLogInterval)   setUInt(datLogInterval,minLogInterval);
  if (getUInt(datLogInterval)>maxLogInterval)   setUInt(datLogInterval,maxLogInterval);
}

// set a flag to check limits next memory service
void Memory::limitCheck(){
  checkLimits= true;
}

void Memory::readFixed(){
  EEPROM.begin((dataSize*2)+statSize+fixedSize);
  for (int addr=0;addr<fixedSize/2;addr++) fixed[addr]= EEPROM.read(addr*2)+EEPROM.read(addr*2+1)*256;
  EEPROM.end();
} // readFixed

void Memory::load(){
  // check for initialized EEPROM memory, model and serial must match
  EEPROM.begin((dataSize*2)+statSize+fixedSize);
  Serial.println("  Retrieve parameters...");
  // read EEPROM
  for (int addr=0;addr<dataSize*2;addr++) ((byte *)data)[addr]= EEPROM.read(addr+fixedSize);
  for (int addr=0;addr<statSize;addr++) stat[addr]= EEPROM.read(addr+(dataSize*2)+fixedSize)==1;
  Serial.println("    Loaded parameters from flash");
  EEPROM.end();
} // load

void Memory::save(){
  limit();
  EEPROM.begin((dataSize*2)+statSize+fixedSize);
  for (int addr=0;addr<dataSize*2;addr++) EEPROM.write(addr+fixedSize,((byte *)data)[addr]);
  for (int addr=0;addr<statSize;addr++) EEPROM.write(addr+(dataSize*2)+fixedSize,int(stat[addr]));
  EEPROM.commit();
  EEPROM.end();
  Serial.println("    Parameters saved in flash");
} // save

void Memory::saveFloat(uint16_t addr){
  if (addr>=0 || addr<dataSize){
    EEPROM.begin((dataSize*2)+statSize+fixedSize);
    for (int off=0;off<4;off++) EEPROM.write(addr*2+off+fixedSize,((byte *)data)[addr*2+off]);
    EEPROM.commit();
    EEPROM.end();
    Serial.println("    Value saved in flash");
  }
  return;
} // saveFloat

void Memory::saveWiFi(){
  EEPROM.begin((dataSize*2)+statSize+fixedSize);
  for (int off=0;off<32;off++)
    EEPROM.write(datWifiAPName*2+off+fixedSize,((byte *)data)[datWifiAPName*2+off]);
  EEPROM.commit();
  EEPROM.end();
  Serial.println("    WiFi credentials saved in flash");
} // saveWiFi

uint16_t Memory::getSerial(){
  return fixed[addrSerial];
}

uint16_t Memory::getHardware(){
  return fixed[addrHardware];
}

uint16_t Memory::getProcessor(){
  return fixed[addrProcessor];
}

bool Memory::getWQInstalled(){
  return fixed[addrWQInstalled]==1;
}

void Memory::setSerial(uint16_t serial){
  for (int addr=0;addr<8;addr++)
    if (addr==addrSerial) saveOne(addr,serial);
    else saveOne(addr,0); // clear the rest of fixed memory
  fixed[addrSerial]= serial;
}

void Memory::setHardware(uint16_t hdwr){
  saveOne(addrHardware,hdwr);
  fixed[addrHardware]= hdwr;
}

void Memory::setProcessor(uint16_t proc){
  saveOne(addrProcessor,proc);
  fixed[addrProcessor]= proc;
}

void Memory::setWQInstalled(bool WQInst){
  saveOne(addrWQInstalled,WQInst);
  fixed[addrWQInstalled]= WQInst;
}

uint16_t Memory::readOne(uint16_t addr){
  EEPROM.begin((dataSize*2)+statSize+fixedSize);
  uint16_t result= EEPROM.read(addr*2)+EEPROM.read(addr*2+1)*256;
  EEPROM.end();
  return result;
} // readOne

void Memory::saveOne(uint16_t addr,uint16_t data){
  EEPROM.begin((dataSize*2)+statSize+fixedSize);
  EEPROM.write(addr*2,lowByte(data));
  EEPROM.write(addr*2+1,highByte(data));
  EEPROM.commit();
  EEPROM.end();
} // saveOne

void Memory::service(){
  // check for save settings bit
  if (getBool(statSaveSettings)){
    save();
    setBool(statSaveSettings,false);
  }
  // check for clear settings bit
  if (getBool(statClearSettings)){
    defaults();
    save(); 
    setBool(statClearSettings,false);       
  }
  // check limits
  if (checkLimits){
    limit();
    checkLimits= false;
  }
} // service

//- End memory -----------------------------------------------------------------
