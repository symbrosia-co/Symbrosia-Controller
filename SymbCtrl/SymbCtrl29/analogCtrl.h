/*------------------------------------------------------------------------------
  Analog to Digital Control - Symbrosia Controller
  - handle the AtoD converter
  - perform filtering on all channels if set
  - perform calibration
  - Written for the ESP32

  01Jan2022 A. Cooper
  - initial version
  29Jul2024 v2.6 A. Cooper
  - remove average table variables from class 
  - removed single channel read function, never implemented or used
  - added CtoF

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
#ifndef adCtrl
#define adCtrl

//- Library includes -----------------------------------------------------------
#include <Arduino.h>
#include <Wire.h>
#include <MCP_ADC.h>
#include <MCP3X21.h>
#include "globals.h"
#include "Memory.h"
extern Memory memory;

//- a little class -------------------------------------------------------------
class AnalogCtrl{
  public:
    AnalogCtrl();
    void init();
    float CtoF(float degC);
    void readAll();
  private:
    const int adChans[7]= {hdwrWQ,hdwrTemp1,hdwrTemp2,hdwrAnalog2,hdwrAnalog1,hdwrSupplyVolt,hdwrTempInt};
    int adCurrent;
    unsigned long adLastTime;
    uint8_t pHADAddr;
    float adAverage[7];
    uint8_t pHAtoDFind();
    int pHAtoDRead(uint8_t pHAddr);
};

#endif
//- End analogCtrl.h -----------------------------------------------------------
