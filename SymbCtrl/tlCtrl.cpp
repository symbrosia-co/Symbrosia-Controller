/*-----------------------------------------------------------------------------
  Time Limited Control - Symbrosia Controller
  - a time limted control input

  - Written for the ESP32

  4Jun2022 A. Cooper
  - initial version

-------------------------------------------------------------------------------

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

-----------------------------------------------------------------------------*/

//- library includes ----------------------------------------------------------
#include <Arduino.h>

//- Local includes ------------------------------------------------------------
#include "globals.h"
#include "tlCtrl.h"
#include "Memory.h"
extern Memory memory;
extern bool ctrlMatrix[ctrlOuts][ctrlSrcs];
extern bool getChan(int chan);

//- class variables -----------------------------------------------------------
unsigned long tlcTime= 0;

//- functions -----------------------------------------------------------------
TLCtrl::TLCCtrl(){
}

void TLCtrl::init(){
  tlcTime= millis();
} // init

void TLCtrl::service(){
  // check flag
  if memory.getBool(statTimeLimFlag){
    memory.setBool(statTimeLimFlag,false);
    tlcTime= millis();
  }
  // reset command state on timer
  if (tlcTime>millis()) tlcTime= millis(); // handle millis rollover
  if (millis()-tlcTime>memory.getUInt(datTLCDuration)*1000){
    memory.setBool(statTimeLimCmd,false)
    tlcTime= millis();
  }
    // set the requested output
  int out= memory.getInt(datTLCOutput);
  if (out==0)
    for (int i=0;i<ctrlOuts;i++) ctrlMatrix[i][ctrlTLCmd]= false;
  if (out>=ioRelay1 && out<=ioDigOut2)
    for (int i=0;i<ctrlOuts;i++)
      if (i==(out-ioRelay1)) ctrlMatrix[i][ctrlTLCmd]= memory.getBool(statTimeLimCmd);
      else ctrlMatrix[i][ctrlTLCmd]= false;
  if (out==ioVState1) memory.setBool(statVState1,memory.getBool(statTimeLimCmd);
  if (out==ioVState2) memory.setBool(statVState2,memory.getBool(statTimeLimCmd);
} // service

//- End TLCtrl ----------------------------------------------------------------
