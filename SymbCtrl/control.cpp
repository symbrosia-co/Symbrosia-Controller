 /*------------------------------------------------------------------------------
  Control - Symbrosia Controller
  - handle the control loops
  - simple bang-bang control with a setpoint and hysteresis

  - Written for the ESP32

  01Jan2022 A. Cooper
  - initial version
  17Jan2022 A. Cooper
  - converted to handle four generic control loops
  12Apr2022 A. Cooper
  - added detection/handling for out of range values
  - added method to confirm control of channel
  - added time based control
  21May2022 A. Cooper
  - fixed type bug in time based control, fractional hours and minutes not working
  - fixed output change bug, output stayed active when loop output changed
  - expanded the alarm bits to add control alarms
  25Jul2024 v 2.6 A. Cooper
  - implemented external control enable
  - implemented minimum on/off time
  - implemented one-shot enable
  - revised much of the service function to make these changes
  08Oct2024 v2.7 A. Cooper
  - remove enable or disabled status from controlled logic, will show
  controlled as long as any controller is set to use as output
  
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
#include "control.h"
#include "Memory.h"
#include "todCtrl.h"
extern Memory  memory;
extern ToDCtrl todCtrl;
extern bool ctrlMatrix[ctrlOuts][ctrlSrcs];
extern bool isDigital(int chan);
extern bool getChan(int chan);

//- constants ------------------------------------------------------------------
#define offset  16   //spacing of channel data in setup registers

//- functions ------------------------------------------------------------------
Control::Control(){
}

void Control::init(){  
  proc= 0;
  timeLast= millis();
  for (int i=0;i<4;i++){
    memory.setBool(statCtrl1Active+i,false);
    memory.setBool(statCtrl1AlarmLow+i,false);
    memory.setBool(statCtrl1AlarmHigh+i,false);
    memory.setBool(statRstCtrl1Max+i,true);
    switchTime[i]= millis();
    stateLast[i]=  false;
    oneShot[i]=    false;
  }
} // init

// make control decisions based on control variables...
//  datCtrlXInput:      input channel to use for control
//  datCtrlXInput:      output channel to use for control
//  datCtrlXOutput:     state of control output
//  datCtrlXSetpoint:   desired average value
//  datCtrlXHysteresis: hysteresis about setpoint, control at setpoint +/-(hysteresis/2)
//  datCtrlXAlarmLow:   low alarm point
//  datCtrlXAlarmHigh:  high alarm point
//  datCtrlXOffTime:    minimum time for control in inactive state in seconds
//  datCtrlXOnTime:     minimum time for control in active state in seconds
//  datCtrlXMimimum:    minimum value encountered
//  datCtrlXMaximum:    maximum value encountered
//  statCtrlXEnable:    true if control enabled
//  statCtrlXHigh:      true if control on when value is high, else on when low
//  statCtrlXActive:    output state of control channel
//  statCtrlXAlarmLow:  low alarm exists
//  statCtrlXAlarmHigh: high alarm exists
//
void Control::service(){
  // do a pass every 250ms, thus each proc will be processed at 1Hz
  if (millis()<timeLast) timeLast= 0; // handle millis rollover    
  if (millis()-timeLast<249) return;
  timeLast= millis();
  // cycle through the control processes, process one each pass
  if (++proc>3) proc=0;
  // get the process input
  float read=0;
  int inChan= memory.getInt(datCtrl1Input+(proc*offset));
  bool timeCtrl= inChan>=ioDays and inChan<=ioSeconds;
  bool valid= false;
  if (inChan>=ioWQAmp && inChan<=ioProcRead){
    valid= memory.getBool(statWQSensorValid+inChan-ioWQAmp);
    read=  memory.getFloat(datWQ+((inChan-1)*2));
  }
  else if (timeCtrl){
    valid= memory.getBool(statNTPTimeValid);
    switch(inChan){
      case ioDays:
        read= float(memory.getInt(datDay))+float(memory.getInt(datHour))/24+float(memory.getInt(datMinute))/1440;
        break;
      case ioHours:
        read= float(memory.getInt(datHour))+float(memory.getInt(datMinute))/60+float(memory.getInt(datSecond))/3600;
        break;
      case ioMinutes:
        read= float(memory.getInt(datMinute))+float(memory.getInt(datSecond))/60;
        break;
      case ioSeconds:
        read=  memory.getInt(datSecond);
        break;
    }
  }
  // compare reading to thresholds
  bool active= memory.getBool(statCtrl1Active+proc);
  float setp= memory.getFloat(datCtrl1Setpoint+(proc*offset));
  float hyst= memory.getFloat(datCtrl1Hysteresis+(proc*offset));
  if (valid){
    if (timeCtrl){ // use in-the-zone for time based control
      if (memory.getBool(statNTPTimeValid))
        active= (read>=setp) && (read<setp+hyst);}
    else{
      if (read<setp-(hyst/2.0))
        active= !memory.getBool(statCtrl1High+proc);
      if (read>setp+(hyst/2.0))
        active= memory.getBool(statCtrl1High+proc);
    }
  }
  else active= false;
  // enable logic
  bool enable= false;
  bool extEnable= ioNone;
  int  extChan= memory.getInt(datCtrl1EnbSource+(proc*offset));
  if (isDigital(extEnable)) extEnable= getChan(extChan);
  if (memory.getBool(statCtrl1Enable+proc)) enable= true;
  else if (extChan!=ioNone)
    if (memory.getBool(statCtrl1OneShot+proc)){  // one shot logic
      if (!oneShot[proc] && active && extEnable){ // start shot
        oneShot[proc]= true;
        enable= true;
      }
      if (oneShot[proc] && active && memory.getBool(statCtrl1Active+proc)) // continue shot
        enable= true;
      if (oneShot[proc] && !memory.getBool(statCtrl1Active+proc) && !extEnable) // reset shot
        oneShot[proc]= false;
    }
    else enable= extEnable;
  // set control output based on all the above
  int outChan= memory.getInt(datCtrl1Output+(proc*offset))-ioRelay1;
  bool result= enable && valid && active;
  if (!stateHold[proc]){
    memory.setBool(statCtrl1Active+proc,result);
    for (int out=0;out<ctrlOuts;out++)
      if (outChan==out) ctrlMatrix[out][proc]= result;
      else ctrlMatrix[out][proc]= false;
  }
  // timeout status
  int delay= memory.getInt(datCtrl1MinOnTime+(proc*offset));
  if (delay==0){  // no hold requested
    stateHold[proc]=  false;
    switchTime[proc]= millis();
    stateLast[proc]=  memory.getBool(statCtrl1Active+proc);
  }
  else if (stateHold[proc]){
    if (millis()-switchTime[proc]>delay*1000){  // end of hold?
      stateHold[proc]=  false;
      switchTime[proc]= millis();
    }
  }
  else if (stateLast[proc]!=memory.getBool(statCtrl1Active+proc)){ // start hold?
    switchTime[proc]= millis();
    stateHold[proc]=  true;
    stateLast[proc]=  memory.getBool(statCtrl1Active+proc);
  }
  else switchTime[proc]= millis();  // no hold in progress
  if (millis()<switchTime[proc]) switchTime[proc]=millis(); // handle millis rollover
  // a litle debug output...
  // if (proc==0){
  //   Serial.print("  Enb:");Serial.print(enable?"T":"F");
  //   Serial.print("  Ext:");Serial.print(extEnable?"T":"F");
  //   Serial.print("  ExtCh:");Serial.print(extChan);
  //   Serial.print("  One:");Serial.print(oneShot[proc]?"T":"F");
  //   Serial.print("  Last:");Serial.print(stateLast[proc]?"T":"F");
  //   Serial.print("  Hold:");Serial.print(stateHold[proc]?"T":"F");
  //   Serial.print("/");Serial.print((millis()-switchTime[proc])/1000);
  //   Serial.print("  Act:");Serial.print(active?"T":"F");
  //   Serial.print("  Valid:");Serial.print(valid?"T":"F");
  //   Serial.print("  Read:");Serial.print(read,2);
  //   Serial.print("  Set:");Serial.print(setp,2);
  //   Serial.print("  Hyst:");Serial.println(hyst,2);
  // }
  // alarms
  if (enable && !memory.getBool(statStartup) && !memory.getBool(statSilenceAlarms) && !timeCtrl){
    if (valid){
      memory.setBool(statCtrl1AlarmLow+proc,read<memory.getFloat(datCtrl1AlarmLow+(proc*offset)));
      memory.setBool(statCtrl1AlarmHigh+proc,read>memory.getFloat(datCtrl1AlarmHigh+(proc*offset)));
    }
    else{
      memory.setBool(statCtrl1AlarmLow+proc,true);
      memory.setBool(statCtrl1AlarmHigh+proc,true);
    }
  }
  else if (timeCtrl && !memory.getBool(statNTPTimeValid)){
    memory.setBool(statCtrl1AlarmLow+proc,true);
    memory.setBool(statCtrl1AlarmHigh+proc,true);
  }
  else{
    memory.setBool(statCtrl1AlarmLow+proc,false);
    memory.setBool(statCtrl1AlarmHigh+proc,false);
  }
  memory.setBool(statCtrl1Alarm+proc,memory.getBool(statCtrl1AlarmLow+proc) || memory.getBool(statCtrl1AlarmHigh+proc));
  memory.setBool(statCtrlAlarm,memory.getBool(statCtrl1Alarm) || memory.getBool(statCtrl2Alarm) || memory.getBool(statCtrl3Alarm) || memory.getBool(statCtrl4Alarm));
  // min and max
  if (valid){
    if (read<memory.getFloat(datCtrl1Minimum+(proc*offset))) memory.setFloat(datCtrl1Minimum+(proc*offset),read);
    if (read>memory.getFloat(datCtrl1Maximum+(proc*offset))) memory.setFloat(datCtrl1Maximum+(proc*offset),read);
  }
  if (memory.getBool(statRstCtrl1Max+proc) || memory.getBool(statStartup)){
    memory.setFloat(datCtrl1Minimum+(proc*offset),read);
    memory.setFloat(datCtrl1Maximum+(proc*offset),read);
    memory.setBool(statRstCtrl1Max+proc,false);
  }
} // service

// return true if channel under loop control
bool Control::controlled(int chan){
  if (chan==0) return false;
  if (chan==memory.getInt(datCtrl1Output)) return true;
  if (chan==memory.getInt(datCtrl2Output)) return true;
  if (chan==memory.getInt(datCtrl3Output)) return true;
  if (chan==memory.getInt(datCtrl4Output)) return true;
  if (chan==memory.getInt(datProcessChanA) || chan==memory.getInt(datProcessChanB)) return true;
  return false;
}  // controlled

//- End control ----------------------------------------------------------------
