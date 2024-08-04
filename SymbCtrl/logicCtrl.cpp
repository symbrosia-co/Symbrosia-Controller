/*------------------------------------------------------------------------------
  Logic Gate - Symbrosia Controller
  - output control based on other digital inputs

  - Written for the ESP32

  17Apr2022 A. Cooper
  - initial version

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
#include "logicCtrl.h"
#include "Memory.h"
extern Memory memory;
extern bool ctrlMatrix[ctrlOuts][ctrlSrcs];
extern bool getChan(int chan);

//- class variables ------------------------------------------------------------
unsigned long logicTime= 0;

//- functions ------------------------------------------------------------------
LogicCtrl::LogicCtrl(){
}

void LogicCtrl::init(){
  logicTime= millis();
} // init

void LogicCtrl::service(){
  // get inputs
  bool inA= false;
  bool inB= false;
  bool result= false;
  inA= getChan(memory.getInt(datLogicInA));
  inB= getChan(memory.getInt(datLogicInB));
  // apply function
  switch(memory.getInt(datLogicFunction)){
    case logicNot:
      result= !inA;
      break;
    case logicAnd:
      result= inA && inB;
      break;
    case logicNand:
      result= !(inA && inB);
      break;
    case logicOr:
      result= inA || inB;
      break;
    case logicNor:
      result= !(inA || inB);
      break;
    case logicXor:
      result= inA != inB;
      break;
    case logicNxor:
      result= inA == inB;
      break;
    case logicEcho:
      result= inA;
      break;
  }
  // set the result
  memory.setBool(statLogicGateResult,result);
  // set the requested output
  int out= memory.getInt(datLogicOut);
  if (out==0)
    for (int i=0;i<ctrlOuts;i++) ctrlMatrix[i][ctrlLogic]= false;
  if (out>=ioRelay1 && out<=ioDigOut2)
    for (int i=0;i<ctrlOuts;i++)
      if (i==(out-ioRelay1)) ctrlMatrix[i][ctrlLogic]= result;
      else ctrlMatrix[i][ctrlLogic]= false;
  if (out>=ioVState1 && out<=ioVState2){
    memory.setBool(statVState1+(out-ioVState1),result);
    for (int i=0;i<ctrlOuts;i++) ctrlMatrix[i][ctrlLogic]= false;
  }
} // service

//- End countCtrl ---------------------------------------------------------------
