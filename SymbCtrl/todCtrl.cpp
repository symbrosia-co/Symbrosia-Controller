/*------------------------------------------------------------------------------
  Time of Day Control - Symbrosia Controller
  - time of day enable
  - Written for the ESP32

  22Jan2022 A. Cooper
  - initial version
  27Jun2024 v2.6 A. Cooper
  - revised ToD logic to change behavior, ToD active will reflect ToD enable
  - cleaned up code in TofDay
  08Oct2024 v2.7 A. Cooper
  - change logic to ensure ToD does not enable a channel if any controller is'
  using it, whether the controller is enabled or not

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

//- Local includes -------------------------------------------------------------
#include "globals.h"
#include "todCtrl.h"
#include "memory.h"
#include "control.h"
extern Memory memory;
extern Control control;
extern bool ctrlMatrix[ctrlOuts][ctrlSrcs];

//- functions ------------------------------------------------------------------
ToDCtrl::ToDCtrl(){
}

void ToDCtrl::init(){
  memory.setBool(statToDActive,false);
} // init

void ToDCtrl::service(){  
  bool todActive;
  if (memory.getBool(statStartup)) todActive= false;
  else if (!memory.getBool(statToDEnable)) todActive= false;
  else if (!memory.getBool(statNTPTimeValid)) todActive= false;
  else{
    int start= 60*memory.getInt(datToDStartHour)+memory.getInt(datToDStartMin);
    int stop=  60*memory.getInt(datToDStopHour)+memory.getInt(datToDStopMin);
    int tod=   60*memory.getInt(datHour)+memory.getInt(datMinute);
    // check for time crossing midnight
    if (start>stop) todActive= tod<stop || tod>=start;
    else todActive= tod>=start && tod<stop;
  }
  memory.setBool(statToDActive,todActive);
  // place results in control matrix
  bool found;
  for (int out=0;out<ctrlOuts;out++){
    if (!memory.getBool(statToDEnable)) ctrlMatrix[out][ctrlToD]= true;
    else{
      found= false;
      for (int i=0;i<4;i++)
        if ((memory.getInt(datToDOutput1+i)-ioRelay1)==out) found= true;
      if (found)
        ctrlMatrix[out][ctrlToD]= todActive;
      else
        ctrlMatrix[out][ctrlToD]= true;
    }
  }
} // service

bool ToDCtrl::controlled(int chan){
  if (chan==0) return false;
  if (memory.getBool(statToDEnable))
    for (int i=0;i<4;i++)
      if (chan==memory.getInt(datToDOutput1+i))
        return true;
  return false;
} // controlled

//- End todCtrl ----------------------------------------------------------------
