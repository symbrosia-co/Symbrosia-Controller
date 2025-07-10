/*------------------------------------------------------------------------------
  Proccess Data - Symbrosia Controller
  - merge the results of two channels
  - Written for the ESP32

  3Apr2022 A. Cooper
  - initial version
  15 Apri2022 A. Cooper
  - functional and tested
  31Jul2024 v2.6 A. Cooper
  - major rewrite
  - handling bad values differently, all methods now operate like priority
  with the good value passed through, alarms will still be thrown as alarms 
  just looks for invalid channel in use, but some value will be passed through
  to allow the control loop to limp along
  - priority remains as a method as there is no modification to the value
  01Nov2024 v2.7 A. Cooper
  - do not use priority for sum or difference, lose any reading => invalid

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
#include "procCtrl.h"
#include "Memory.h"
extern Memory memory;
extern bool isAnalog(int chan);
extern float getAChan(int chan);

//- local variables ------------------------------------------------------------
unsigned long procLastTime= 0;

//- functions ------------------------------------------------------------------
ProcCtrl::ProcCtrl(){
}

void ProcCtrl::init(){
  memory.setFloat(datProcessedData,0);
  memory.setBool(statProcReadValid,false);
  procLastTime= millis();
} // init

void ProcCtrl::service(){
  if (millis()<procLastTime) procLastTime= 0; // handle millis rollover
  if (millis()-procLastTime<1000) return;
  procLastTime= millis();  
  float a= 0;
  float b= 0;
  // get and check values
  int chanA= memory.getInt(datProcessChanA);
  if (isAnalog(chanA)) a= getAChan(chanA);
  else{
    memory.setFloat(datProcessedData,0);
    memory.setBool(statProcReadValid,false);
    return;
  }
  int chanB= memory.getInt(datProcessChanB); 
  if (isAnalog(chanB)) b= getAChan(chanB);
  else{
    memory.setFloat(datProcessedData,0);
    memory.setBool(statProcReadValid,false);
    return;
  } 
  // handle priority processing by validity
  bool valid=  true;
  bool validA= memory.getBool(statWQSensorValid+chanA-ioWQAmp);
  bool validB= memory.getBool(statWQSensorValid+chanB-ioWQAmp);
  float result= 0;
  int units;
  if (!validA && !validB){
    valid= false;
    units= unitsNone;
  }
  if ((memory.getInt(datProcessID)==procSum || memory.getInt(datProcessID)==procDiff) && !(validA && validB)){
    valid= false;
    units= unitsNone;
  }
  else{
    if (validA && !validB){
      result= a;
      units= memory.getInt(datWQSensorUnits+chanA-1);
    }
    if (!validA && validB){
      result= b;
      units= memory.getInt(datWQSensorUnits+chanB-1);
    }
  }
  if (validA && validB){
    units= memory.getInt(datWQSensorUnits+chanA-1);
    switch(memory.getInt(datProcessID)){
      case(procValid):
        result= a;
        break;
      case(procAvg):
        result= (a+b)/2;
        break;
      case(procMin):
        if (a<b) result= a;
        else result= b;
        break;
      case(procMax):
        if (a>b) result= a;
        else result= b;
        break;
      case(procSum):
        result= a+b;
        break;
      case(procDiff):
        result= a-b;
        break;
    }
  }
  memory.setFloat(datProcessedData,result);
  memory.setBool(statProcReadValid,valid);
  memory.setInt(datProcUnits,units);
} // service

//- End procCtrl ---------------------------------------------------------------
