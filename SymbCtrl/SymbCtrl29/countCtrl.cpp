/*------------------------------------------------------------------------------
  Counter and Timer - Symbrosia Controller
  - event counting and timing

  - Written for the ESP32

  14Jan2022 A. Cooper
  - initial version
  - tested and operational
  15Jan2022 A. Cooper
  - added reset
  20Mar2024 v2.4 A. Cooper
  - finished timer and counter resets hourly and daily
  - added monthly reset
  - added frequency counter to counter function

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
#include "countCtrl.h"
#include "Memory.h"
extern Memory memory;

//- class variables ------------------------------------------------------------
bool lastEventState= 0;
unsigned long lastCountTime= 0;

//- functions ------------------------------------------------------------------
CountCtrl::CountCtrl(){
}

void CountCtrl::init(){
  bool lastEventState= false;
  unsigned long lastCountTime= 0;
  freqTime= 0;
  freqCounter= 0;
} // init

void CountCtrl::service(){
  int chan;  
  bool state;
  // check event counter
  chan= memory.getInt(datCountSource);
  if (chan==0) memory.setLong(datCounter,0);
  else if (chan>=ioDigIn1 && chan<=ioFlash){
    state= memory.getBool(ioAddr[chan]);
    if (state!=lastEventState){
      lastEventState= state;
      if (state){
        memory.setLong(datCounter,memory.getLong(datCounter)+1);
        freqCounter++;
      }
    }
  }
  // measure frequency on counter input
  if (millis()<freqTime){ // handle millis rollover
    freqTime= millis();
    freqCounter= 0;
  }
  if (millis()-freqTime>999){ //readout each second
    freqTime= millis();
    memory.setUInt(datFrequency,constrain(freqCounter,0,1000));
    freqCounter= 0;
  }
  // check event timer
  chan= memory.getInt(datTimerSource);
  if (chan==0) memory.setLong(datTimer,0);
  else if (chan>=ioDigIn1 && chan<=ioFlash){
    state= memory.getBool(ioAddr[chan]);
    if (state){     
      if (millis()<lastCountTime) lastCountTime= 0; // handle millis rollover
      if (millis()-lastCountTime>999){
        lastCountTime= millis();
        memory.setLong(datTimer,memory.getLong(datTimer)+1);
      }      
    } 
    else lastCountTime= millis();
  }
  // check for resets
  if (memory.getBool(statResetCounter)){
    memory.setBool(statResetCounter,false);
    memory.setLong(datCounter,0);
  }
  if (memory.getBool(statResetTimer)){
    memory.setBool(statResetTimer,false);
    memory.setLong(datTimer,0);
  }
  // check for timed resets
  if (memory.getUInt(datDay)==0 && memory.getUInt(datHour)==0 && memory.getUInt(datMinute)==0 && memory.getUInt(datSecond)==0){
    if (memory.getUInt(datCountRstIntv)==resetMonthly)
      memory.setLong(datCounter,0);
    if (memory.getUInt(datTimerRstIntv)==resetMonthly)
      memory.setLong(datTimer,0);
  }
  if (memory.getUInt(datHour)==0 && memory.getUInt(datMinute)==0 && memory.getUInt(datSecond)==0){
    if (memory.getUInt(datCountRstIntv)==resetDaily)
      memory.setLong(datCounter,0);
    if (memory.getUInt(datTimerRstIntv)==resetDaily)
      memory.setLong(datTimer,0);
  }
  if (memory.getUInt(datMinute)==0 && memory.getUInt(datSecond)==0){
    if (memory.getUInt(datCountRstIntv)==resetHourly)
      memory.setLong(datCounter,0);
    if (memory.getUInt(datTimerRstIntv)==resetHourly)
      memory.setLong(datTimer,0);
  }
} // service

//- End countCtrl ---------------------------------------------------------------
