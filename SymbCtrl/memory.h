/*------------------------------------------------------------------------------
  Memory - Symbrosia Controller
  - load defaults and store in EEPROM
  - Written for the ESP32

  02Jan2022 A. Cooper
  - initial version
  21Jan2022 A. Cooper
  - revised register map for new arrangement
  - added setStr for packed string handling
  15Apr2022 A. Cooper
  - revised memory map for first release
  20Mar2024 v2.4 A. Cooper
  - added combined alarm states for each control loop and overall control
  23Oct2024 v2.7 A. Cooper
  - add saveFloat to allow storing of calibration values without global save
  - add saveWiFi to allow storing credentials without global save
  02Nov2024 v2.8 A. Cooper
  - reserve 16 bytes at start of flash for fixed information including
  serial number and hardware information
  - add fixed array to buffer the fixed memory data
  - add setSerial, setHardware, and setProcessor methods
  - add getSerial, getHardware, and getProcessor methods
  - add getWQInstalled and setWQInstalled method

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
#ifndef memCtrl
#define memCtrl

//- Library includes -----------------------------------------------------------
#include <Arduino.h>

//- memory ---------------------------------------------------------------------
#define dataSize        320  // size of data memory
#define datSizeClear    300  // section of data to be cleared on defaults load
#define statSize         70  // size of status memory
#define fixedSize        16  // size of fixed data at start of flash memory
#define addrSerial        0  // address of serial number
#define addrHardware      1  // address of hardware ID
#define addrProcessor     2  // address of processor ID
#define addrWQInstalled   3  // address of water quality sensor installed flag

//- limits ---------------------------------------------------------------------
#define minUnits          0
#define maxUnits         33
#define minTimeUnits     35
#define maxTimeUnits     38
#define minTempUnits      1
#define maxTempUnits      2
#define minChan           0
#define maxChan          38
#define minAnalogChan     0
#define maxAnalogChan     8
#define minLogicChan      9
#define maxLogicChan     34
#define minOutputChan    11
#define maxOutputChan    16
#define minProcess        0
#define maxProcess        5
#define minLogicFunc      0
#define maxLogicFunc      7
#define minResetIntv      0
#define maxResetIntv      3
#define minTemp         -40
#define maxTemp         140
#define minTimezone     -12
#define maxTimezone      14
#define minHour           0
#define maxHour          23
#define minMinute         0
#define maxMinute        59
#define minOnOffTime      0
#define maxOnOffTime   3600
#define minLogInterval    1
#define maxLogInterval 1440

//- a little class -------------------------------------------------------------
class Memory{
  public:
    Memory();
    int16_t  getInt(uint16_t addr);
    void     setInt(uint16_t addr,int16_t val);
    uint16_t getUInt(uint16_t addr);
    void     setUInt(uint16_t addr,uint16_t val);
    unsigned long getLong(uint16_t addr);
    void     setLong(uint16_t addr,unsigned long val);
    float    getFloat(uint16_t addr);
    void     setFloat(uint16_t addr,float val);
    char     getChar(uint16_t addr);
    void     setChar(uint16_t addr,char val);
    void     getStr(uint16_t addr,char* st);
    void     setStr(uint16_t addr,const char* str);
    bool     getBool(uint16_t addr);
    void     setBool(uint16_t addr,bool val);
    void     defaults();
    void     limit();
    void     limitCheck();
    void     readFixed();
    void     load();
    void     save();
    void     saveFloat(uint16_t addr);
    void     saveWiFi();
    uint16_t getSerial();
    uint16_t getHardware();
    uint16_t getProcessor();
    bool     getWQInstalled();
    void     setSerial(uint16_t serial);
    void     setHardware(uint16_t hdwr);
    void     setProcessor(uint16_t proc);
    void     setWQInstalled(bool WQInst);
    void     service();
  private:
    uint16_t fixed[fixedSize/2];
    uint16_t data[dataSize];
    boolean  stat[statSize];
    boolean  checkLimits;
    uint16_t readOne(uint16_t addr);
    void     saveOne(uint16_t addr,uint16_t data);
};

#endif
//- End memory.h ---------------------------------------------------------------
