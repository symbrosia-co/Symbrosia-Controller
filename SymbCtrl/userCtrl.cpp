 /*------------------------------------------------------------------------------
  User Interface Control - Symbrosia Controller
  - handle an input encoder and an LCD display

  - Written for the ESP32 S3

  01Jan2022 A. Cooper
  - initial version
  15Apr2022 A. Cooper
  - all screens complete
  - added pH calibrate function
  - added timeout to pH calibrate
  - added processed reading screen
  - added timeout return to status screen
  - modified splash for firmware version display
  21May2022 A. Cooper
  - removed logging screen until this is implemented
  16Dec2023 A. Cooper
  - use 8-bit interface for the LCD on mk2 PCB
  20Mar2024 v2.4 A. Cooper
  - added screen for internal temp and supply voltage
  - added patch to allow scrolling back over WiFi2 when no network
  - added control loop setpoint adjust
  23Apr2024 v2.5 A. Cooper
  - fixed left scroll out of ScrWiFiDone bug
  27Jul2024 v2.6 A. Cooper
  - removed a decimal point from status screen value display
  - added a number of new units
  08Oct2024 v2.7 A. Cooper
  - convert WiFi scanNetworks to non-blocking
  - add a timeout to scanNetworks
  - change memory.save to memory.saveFloat in calibration routines
  - change momory.save to memory.saveWiFi in credential entry routine

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
#include <LiquidCrystal.h>

//- Local includes -------------------------------------------------------------
#include "globals.h"
#include "userCtrl.h"
#include "Memory.h"
#include "timeCtrl.h"
#include "modbusCtrl.h"
extern TimeCtrl timeCtrl;
extern Memory memory;

//- instantiate ----------------------------------------------------------------
LiquidCrystal lcd(hdwrLCDRS,hdwrLCDRW,hdwrLCDE,hdwrLCDD0,hdwrLCDD1,hdwrLCDD2,hdwrLCDD3,hdwrLCDD4,hdwrLCDD5,hdwrLCDD6,hdwrLCDD7);

//- class variables ------------------------------------------------------------
int screen= 0;
bool newScr= true;
unsigned long lastUpdate= 0;
bool userSetReq=  false;
bool userSetNext= false;
bool userSetAcpt= false;
bool userSetEnd=  false;
unsigned long userSetTime;
unsigned long wifiStart;
unsigned long wifiScanTime;
int userSelect= 0;
int userSelLimit= 0;
int userSelPos= 0;
const char pwChars[]= "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$@^`,|%;.()/{}:?[]=-+_#!*";
char wifiPass[16]; 

//- constants ------------------------------------------------------------------
#define lcdUpdate  250
#define chanOffset  16   //spacing of channel data in setup registers
#define screenStatDelay 600
#define wifiTimeout 60000  // timeout for WiFi scanNetworks

//- functions ------------------------------------------------------------------

UserCtrl::UserCtrl(){
}

void UserCtrl::init(){
  lcd.begin(16,2);
  lcd.clear();
  screen= 0;
  newScr= true;
  drawScreen();
  lastUpdate= millis();
  userSetReq=  false;
  userSetNext= false;
  userSetAcpt= false;
  userSetEnd=  false;
  userSetTime= millis();
} // init

void UserCtrl::service(){
  // update the screen delay
  if (millis()<lastUpdate) lastUpdate= 0; // handle millis rollover  
  if (millis()-lastUpdate<lcdUpdate) return;
  lastUpdate= millis();
  // timeout return to status screen
  if (!userSetReq){
    if (millis()<screenTime) screenTime= 0;
    if (millis()-screenTime>screenStatDelay*1000) setScreen(scrStatus); 
    userSetNext= false;
    userSetAcpt= false;
  }
  // timeout of setting request
  else{
    if (millis()<userSetTime) userSetTime= 0;
    if (millis()-userSetTime>120000){
      userSetReq= false;
      newScr= true;
    }
  }
  // refresh the screen
  drawScreen();
} // service

void UserCtrl::setScreen(int scr){
  if (scr>=scrSplash && scr<=scrLast) screen= scr;
  if (scr==scrWiFiStart) screen= scr;
  if (scr==scrWiFiDone) screen= scr;
  newScr= true;
  userSetReq= false;
  drawScreen();
} // setScreen

void UserCtrl::right(){
  if (userSetReq) userSelScroll++;
  else{
    if (++screen>scrLast) screen= scrFirst;
    setScreen(screen);
  }
}

void UserCtrl::left(){  
  if (userSetReq) userSelScroll--;
  else{
    if (screen==scrWiFiDone) screen= scrFirst;
    if (--screen<scrFirst) screen= scrLast;
    if (screen==scrWiFi2 && !wifiStat) screen= scrWiFi; // patch to allow scrolling back over WiFi2
    setScreen(screen);
  }
}

void UserCtrl::click(){
  if (userSetReq) userSetAcpt= true;
  else{
    if (++screen>scrLast) screen= 1;
    setScreen(screen);
  }
}

void UserCtrl::press(){
  switch (screen){
    // WQ calibrate
    case scrWQSensor:
      userSetTime= millis();    
      if (!userSetReq) userSetReq= true;
      else
        if (!userSetNext) userSetNext= true;
        else userSetAcpt= true;
      break;
    // temperature calibrate
    case scrTemps:
      userSetTime= millis();    
      if (!userSetReq) userSetReq= true;
      else userSetAcpt= true;
      break;
    // control loop activate
    case scrControl1a:
      memory.setBool(statCtrl1Enable,!memory.getBool(statCtrl1Enable));
      break;
    case scrControl2a:
      memory.setBool(statCtrl2Enable,!memory.getBool(statCtrl2Enable));
      break;
    case scrControl3a:
      memory.setBool(statCtrl3Enable,!memory.getBool(statCtrl3Enable));
      break;
    case scrControl4a:
      memory.setBool(statCtrl4Enable,!memory.getBool(statCtrl4Enable));
      break;
    // setpoint adjust
    case scrControl1c:
    case scrControl2c:
    case scrControl3c:
    case scrControl4c:
      if (!userSetReq) userSetReq= true;
      else userSetAcpt= true;
      userSetTime= millis();
      break;
    // ToD Enable
    case scrToD:
      memory.setBool(statToDEnable,!memory.getBool(statToDEnable));
      break;
    // reset counter and timer
    case scrCounter:
      memory.setLong(datCounter,0);
      break;
    case scrTimer:
      memory.setLong(datTimer,0);
      break;
    case scrTime:
      timeCtrl.setTime();
      break;
    case scrWiFi:
      if (!userSetReq){
        userSetReq= true;
        WiFi.disconnect();
        lcd.setCursor(5,0);
        lcd.print("Scanning...");
        lcd.setCursor(0,1);
        lcd.print("                ");
        wifiScanTime= millis();
        Serial.println("Scanning networks...");
      }
      else userSetEnd= true;
      break;
    case scrUnit:
      ESP.restart();
      break;
  }
}

void UserCtrl::dClick(){
   setScreen(scrStatus);
}

//- formatting -----------------------------------------------------------------

void UserCtrl::printChan(int chan){
  switch(chan){
    case ioNone:     lcd.print("None "); break;
    case ioWQAmp:    lcd.print("WQAmp"); break;
    case ioTemp1:    lcd.print("Temp1"); break;
    case ioTemp2:    lcd.print("Temp2"); break;
    case ioAnalog1:  lcd.print("Anlg1"); break;
    case ioAnalog2:  lcd.print("Anlg2"); break;
    case ioIntTemp:  lcd.print("IntT "); break;
    case ioSupplyV:  lcd.print("SupV "); break;
    case ioProcRead: lcd.print("Proc "); break;
    case ioDigIn1:   lcd.print("Din1 "); break;
    case ioDigIn2:   lcd.print("Din2 "); break;
    case ioRelay1:   lcd.print("Rly1 "); break;
    case ioRelay2:   lcd.print("Rly2 "); break;
    case ioDigOut1:  lcd.print("Dout1"); break;
    case ioDigOut2:  lcd.print("Dout2"); break;
    case ioVState1:  lcd.print("Virt1"); break;
    case ioVState2:  lcd.print("Virt2"); break;
    case ioCtrl1:    lcd.print("Ctrl1"); break;
    case ioCtrl2:    lcd.print("Ctrl2"); break;
    case ioCtrl3:    lcd.print("Ctrl3"); break;
    case ioCtrl4:    lcd.print("Ctrl4"); break;
    case ioC1AlmHi:  lcd.print("Al1Hi"); break;
    case ioC1AlmLo:  lcd.print("Al1Lo"); break;
    case ioC2AlmHi:  lcd.print("Al2Hi"); break;
    case ioC2AlmLo:  lcd.print("Al2Lo"); break;
    case ioC3AlmHi:  lcd.print("Al3Hi"); break;
    case ioC3AlmLo:  lcd.print("Al3Lo"); break;
    case ioC4AlmHi:  lcd.print("Al4Hi"); break;
    case ioC4AlmLo:  lcd.print("Al4Lo"); break;
    case ioFlash:    lcd.print("Flash"); break;
    case ioDays:     lcd.print("Days "); break;
    case ioHours:    lcd.print("Hours"); break;
    case ioMinutes:  lcd.print("Min  "); break;
    case ioSeconds:  lcd.print("Sec  "); break;
    case ioTofD:     lcd.print("TofD "); break;
  }
}

void UserCtrl::printState(int chan){
  float read;
  switch (chan){
    case ioNone:
      lcd.print("  None  ");
      break;
    case ioWQAmp:
    case ioTemp1:
    case ioTemp2:
    case ioAnalog1:
    case ioAnalog2:
    case ioIntTemp:
    case ioSupplyV:
    case ioProcRead:
      printRead(memory.getFloat(datWQ+((chan-ioWQAmp)*2)),7,1,
                memory.getInt  (datWQSensorUnits+chan-ioWQAmp),
                memory.getBool (statWQSensorValid+chan-ioWQAmp));
      break;
    case ioDigIn1:
    case ioDigIn2:
      if (memory.getBool(statDigitalIn1+chan-ioDigIn1)) lcd.print("  High  ");
      else lcd.print("  Low   ");
      break;
    case ioRelay1:
    case ioRelay2:
    case ioDigOut1:
    case ioDigOut2:
    case ioTofD:
      if (memory.getBool(statRelay1Status+chan-ioRelay1)) lcd.print("  On    ");
      else lcd.print("  Off   ");
      break;
    case ioVState1:
    case ioVState2:
      if (memory.getBool(statVState1+chan-ioVState1)) lcd.print("  True  ");
      else lcd.print("  False ");
      break;
    case ioCtrl1:
    case ioCtrl2:
    case ioCtrl3:
    case ioCtrl4:
      if (memory.getBool(statCtrl1Active+chan-ioCtrl1)) lcd.print("  On    ");
      else lcd.print("  Off   ");
      break;
    case ioCAlm:
    case ioC1Alm:
    case ioC2Alm:
    case ioC3Alm:
    case ioC4Alm:
    case ioC1AlmLo:
    case ioC2AlmLo:
    case ioC3AlmLo:
    case ioC4AlmLo:
    case ioC1AlmHi:
    case ioC2AlmHi:
    case ioC3AlmHi:
    case ioC4AlmHi:
      if (memory.getBool(statCtrlAlarm+chan-ioCAlm)) lcd.print(" Alarm  ");
      else lcd.print("No Alarm");
      break;
    case ioFlash:
      if (memory.getBool(statFlash)) lcd.print("  True  ");
      else lcd.print("  False ");
      break;
    case ioDays:
      read= memory.getInt(datDay)+(memory.getInt(datHour)+(memory.getInt(datMinute)+memory.getInt(datSecond)/60)/60)/24;
      printRead(read,8,0,unitsDay,memory.getBool(statNTPTimeValid));
      break;
    case ioHours:
      read= memory.getInt(datHour)+memory.getInt(datMinute)/60+memory.getInt(datSecond)/3600;
      printRead(read,8,0,unitsHour,memory.getBool(statNTPTimeValid));
      break;
    case ioMinutes:
      read= memory.getInt(datMinute)+memory.getInt(datSecond)/60;
      printRead(read,8,0,unitsMin,memory.getBool(statNTPTimeValid));
      break;
    case ioSeconds:
      read= memory.getInt(datSecond);
      printRead(read,8,0,unitsSec,memory.getBool(statNTPTimeValid));
      break;
    default:
      lcd.print("        ");
  }
}

void UserCtrl::printRead(float read,int space,int decs,int unit,bool valid){
  space= space-3;
  int i;
  if (valid){
    space= space-decs-2;
    if (read<0) space= space=1;
    for (i=0;i<space;i++)
      if (read<pow(10,i+1)) lcd.print(" ");
    if (read<0) lcd.print("-");
    lcd.print(abs(read),decs);
  }
  else{
    if (decs>0){
      lcd.print(" ");
      for (i=0;i<space-decs-2;i++) lcd.print("-");
      lcd.print(".");
      for (i=0;i<decs;i++) lcd.print("-");
    }
    else{
      lcd.print(" ");
      for (i=0;i<space-1;i++) lcd.print("-");
    }
  }
  switch(unit){
    case unitsNone: lcd.print("   "); break;
    case unitsDegC: lcd.print(char(223)); lcd.print("C "); break;
    case unitsDegF: lcd.print(char(223)); lcd.print("F "); break;
    case unitspH:   lcd.print("pH "); break;
    case unitsmV:   lcd.print("mV "); break;
    case unitsV:    lcd.print("V  "); break;
    case unitsmA:   lcd.print("mA "); break;
    case unitsA:    lcd.print("A  "); break;
    case unitsmm:   lcd.print("mm "); break;
    case unitsm:    lcd.print("m  "); break;
    case unitsml:   lcd.print("ml "); break;
    case unitsl:    lcd.print("l  "); break;
    case unitsg:    lcd.print("g  "); break;
    case unitskg:   lcd.print("kg "); break;
    case unitslbs:  lcd.print("lb "); break;
    case unitskPa:  lcd.print("kPa"); break;
    case unitsPSI:  lcd.print("PSI"); break;
    case unitsHz:   lcd.print("Hz "); break;
    case unitsPct:  lcd.print("%  "); break;
    case unitsOhm:  lcd.print(char(244)); lcd.print("  "); break;
    case unitsDay:  lcd.print("day"); break;
    case unitsHour: lcd.print("hrs"); break;
    case unitsMin:  lcd.print("min"); break;
    case unitsSec:  lcd.print("s  "); break;
    case unitsMol:  lcd.print("mol"); break;
    case unitsMPH:  lcd.print("mph"); break;
    case unitsMPS:  lcd.print("m/s"); break;
    case unitsDeg:  lcd.print(char(223)); lcd.print("  "); break;
    case unitsmmH:  lcd.print("mmH"); break;
    case unitsmBar: lcd.print("mBr"); break;
    case unitsWatt: lcd.print("W  "); break;
    case unitskWatt:lcd.print("kW "); break;
    case unitskVA:  lcd.print("kVA"); break;
  }
}

void UserCtrl::printLeadZero(int num){
  if (num<10) lcd.print("0");
  lcd.print(num);
}

void UserCtrl::printLeftInt(int num,int space){
  if (space>10) space=10;
  for (int i=1;i<space;i++)
    if (num<pow(10,i)) lcd.print(" ");
  lcd.print(num);
}

void UserCtrl::printDate(){
  if (memory.getBool(statNTPTimeValid)){
    printLeadZero(memory.getInt(datDay));
    switch (memory.getInt(datMonth)+1){
      case 1:  lcd.print("Jan"); break;
      case 2:  lcd.print("Feb"); break;
      case 3:  lcd.print("Mar"); break;
      case 4:  lcd.print("Apr"); break;
      case 5:  lcd.print("May"); break;
      case 6:  lcd.print("Jun"); break;
      case 7:  lcd.print("Jul"); break;
      case 8:  lcd.print("Aug"); break;
      case 9:  lcd.print("Sep"); break;
      case 10: lcd.print("Oct"); break;
      case 11: lcd.print("Nov"); break;
      case 12: lcd.print("Dec"); break;
    }
    printLeadZero(memory.getInt(datYear)-2000);
  }
  else lcd.print("No NTP!");
}

void UserCtrl::printTime(){
  printLeadZero(memory.getInt(datHour));
  lcd.print(":");
  printLeadZero(memory.getInt(datMinute));
  lcd.print(":");
  printLeadZero(memory.getInt(datSecond));;
}

void UserCtrl::printOnOff(bool state){
  if (state) lcd.print("On ");
  else lcd.print("Off");
}

//- screen functions -----------------------------------------------------------

void UserCtrl::drawScreen(){
  if (newScr){
    lcd.clear();
    lcd.noCursor();
    userSetReq= false;
    userSetNext= false;
    userSetAcpt= false;
    userSetTime= millis();
    screenTime= millis();
  }
  // draw active screen
  switch (screen){
    case scrSplash:
      drawSplash();
      break;
    case scrStatus:
      drawStatus();
      break;
    case scrWQSensor:
      drawWQSensor();
      break;
    case scrTemps:
      drawTemps();
      break;
    case scrAnalog:
      drawAnalog();
      break;
    case scrProc:
      drawProc();
      break;
    case scrControl1a:
    case scrControl2a:
    case scrControl3a:
    case scrControl4a:
      drawControlA(int((screen-scrControl1a)/3));
      break;
    case scrControl1b:
    case scrControl2b:
    case scrControl3b:
    case scrControl4b:
      drawControlB(int((screen-scrControl1b)/3));
      break;
    case scrControl1c:
    case scrControl2c:
    case scrControl3c:
    case scrControl4c:
      drawControlC(int((screen-scrControl1c)/3));
      break;
    case scrLogic:
      drawLogic();
      break;
    case scrToD:
      drawToD();
      break;
    case scrToD2:
      drawToD2();
      break;
    case scrOutputs:
      drawOutputs();
      break;
    case scrCounter:
      drawCounter();
      break;
    case scrTimer:
      drawTimer();
      break;
    case scrModbus:
      drawModbus();
      break;
    case scrTime:
      drawTime();
      break;
    case scrWiFi:
      drawWiFi();
      break;
    case scrWiFi2:
      drawWiFi2();
      break;
    case scrIntData:
      drawIntData();
      break;
    case scrUnit:
      drawUnit();
      break;
    case scrWiFiStart:
      drawWiFiStart();
      break;
    case scrWiFiDone:
      drawWiFiDone();
      break;
  }
  newScr= false;
} // drawScreen

void UserCtrl::drawSplash(){
  if (newScr){
    lcd.print("Symbrosia");
    lcd.setCursor(2,1);
    lcd.print("Control ");
    lcd.print("v");
    lcd.print(firmMajor);
    lcd.print(".");
    lcd.print(firmMinor);
    }
} // drawSplash

void UserCtrl::drawStatus(){
  if (newScr){
    char name[18];
    memory.getStr(datControlName,name);
    if (name[0]!=0) lcd.print(name);
    else lcd.print("Stat");
    lcd.setCursor(7,0);
    lcd.print(" ");    
  }
  lcd.setCursor(8,0);
  printTime();
  lcd.setCursor(0,1);
  printState(memory.getInt(datStatusDisp1));
  lcd.setCursor(8,1);
  printState(memory.getInt(datStatusDisp2));
} // drawStatus

void UserCtrl::drawWQSensor(){
  if (newScr){
    lcd.print("WQ");
    lcd.setCursor(8,1);
    lcd.print("Tc:");
    }
  // get reading with gain and offset removed
  float read= ((memory.getFloat(datWQ)-7)/memory.getFloat(datWQGain))+7-memory.getFloat(datWQOffset);
  // handle calibration
  lcd.setCursor(3,0);
  if (userSetReq){
    if (!memory.getBool(statWQSensorValid) || !(memory.getInt(datWQSensorUnits)==unitspH)){
      userSetReq= false;
      return;
    }  
    if (!userSetNext) lcd.print("   Confirm?  ");      
    else{
      if (!userSetAcpt) lcd.print("  Calibrate! ");
      else{
        if (read>3 && read<5){
          memory.setFloat(datWQGain,-3/(read-7.0+memory.getFloat(datWQOffset)));
          memory.saveFloat(datWQGain);
          lcd.print(" Cal'd @ 4pH ");
        }
        else if (read>6 && read<8){
          memory.setFloat(datWQOffset,7.0-read);
          memory.saveFloat(datWQOffset);
          lcd.print(" Cal'd @ 7pH ");
        }
        else if (read>9 && read<11){
          memory.setFloat(datWQGain,3/(read-7.0+memory.getFloat(datWQOffset)));
          memory.saveFloat(datWQGain);
          lcd.print(" Cal'd @ 10pH");
        }
        else lcd.print("Out of Range!");
        userSetReq=  false;
        userSetNext= false;
        userSetAcpt= false;
      }
    }
  }
  // display reading    
  lcd.setCursor(0,1);
  printRead(memory.getFloat(datWQ),8,2,memory.getInt(datWQSensorUnits),memory.getBool(statWQSensorValid));
  lcd.setCursor(11,1);
  printChan(memory.getInt(datPHTempComp)); 
} // drawWQSensor

void UserCtrl::drawTemps(){
  if (newScr){
    lcd.print("Temp");
    lcd.setCursor(5,0);
    lcd.print("T1:");
    lcd.setCursor(5,1);
    lcd.print("T2:");
    }
  if (userSetReq){
    if (!userSetNext){
      lcd.setCursor(5,0);
      if (memory.getBool(statFlash)) lcd.print("T1:");
      else lcd.print("   ");
      memory.setFloat(datTemp1Offset,memory.getFloat(datTemp1Offset)+float(userSelScroll)*0.1);
      userSelScroll= 0;
    }
    else{
      lcd.setCursor(5,1);
      if (memory.getBool(statFlash)) lcd.print("T2:");
      else lcd.print("   ");
      memory.setFloat(datTemp2Offset,memory.getFloat(datTemp2Offset)+float(userSelScroll)*0.1);
      userSelScroll= 0;
    }
    if (userSetAcpt){
      lcd.setCursor(5,0);
      lcd.print("T1:");
      lcd.setCursor(5,1);
      lcd.print("T2:");
      if (!userSetNext) userSetNext=true;
      else{
        memory.saveFloat(datTemp1Offset);
        memory.saveFloat(datTemp2Offset);
        userSetReq= false;
      }
      userSetAcpt= false;
    }
  }
  lcd.setCursor(8,0);
  printRead(memory.getFloat(datTemperature1),8,2,memory.getInt(datTemp1Units),memory.getBool(statTemp1Valid));
  lcd.setCursor(8,1);
  printRead(memory.getFloat(datTemperature2),8,2,memory.getInt(datTemp2Units),memory.getBool(statTemp2Valid));
} // drawTemps

void UserCtrl::drawAnalog(){
  if (newScr){
    lcd.print("Ain");
    lcd.setCursor(4,0);
    lcd.print("A1:");
    lcd.setCursor(4,1);
    lcd.print("A2:");
    }
    lcd.setCursor(8,0);
    printRead(memory.getFloat(datAnalog1),8,2,memory.getInt(datAnalog1Units),memory.getBool(statAnalog1Valid));
    lcd.setCursor(8,1);
    printRead(memory.getFloat(datAnalog2),8,2,memory.getInt(datAnalog2Units),memory.getBool(statAnalog2Valid));
} // drawAnalog

void UserCtrl::drawProc(){
  if (newScr){
    lcd.print("Proc");
    lcd.setCursor(0,1);
    lcd.print("A:");
    lcd.setCursor(8,1);
    lcd.print("B:");
    }
  lcd.setCursor(8,0);
  printRead(memory.getFloat(datProcessedData),8,2,memory.getInt(datProcUnits),memory.getBool(statProcReadValid));
  lcd.setCursor(2,1);
  printChan(memory.getInt(datProcessChanA));
  lcd.setCursor(10,1);
  printChan(memory.getInt(datProcessChanB));
} // drawProc

void UserCtrl::drawControlA(int loop){
  char name[18];
  if (newScr){
    lcd.print("Ctrl");
    lcd.print(loop+1);
    }
  int chan= memory.getInt(datCtrl1Input+(loop*chanOffset));
  lcd.setCursor(6,0);
  memory.getStr(datControl1Name+loop*8,name);
  lcd.print(name);
  lcd.setCursor(0,1);
  if (chan>=ioWQAmp && chan<=ioProcRead)
    printRead(memory.getFloat(datWQ+(2*(chan-1))),8,1,memory.getInt(datWQSensorUnits+chan-1),memory.getBool(statWQSensorValid+chan-1));
  else lcd.print("  ----  ");
  lcd.setCursor(8,1);
  if (memory.getBool(statCtrl1Active+loop) && memory.getBool(statCtrl1OneShot+loop)) lcd.print("One-Shot");
  else if (memory.getBool(statCtrl1Active+loop) && !memory.getBool(statCtrl1Enable+loop)) lcd.print("External");
  else if (!memory.getBool(statCtrl1Active+loop) && memory.getBool(statCtrl1Enable+loop)) lcd.print("Inactive");
  else if (memory.getBool(statCtrl1Active+loop)) lcd.print(" Active ");
  else lcd.print("Disabled");
} // drawControlA

void UserCtrl::drawControlB(int loop){
  if (newScr){
    lcd.print("Ctrl");
    lcd.print(loop+1);
    lcd.setCursor(6,0);
    lcd.print(" In:");
    lcd.setCursor(6,1);
    lcd.print("Out:");
    }
  lcd.setCursor(10,0);
  printChan(memory.getInt(datCtrl1Input+(loop*chanOffset)));
  lcd.setCursor(10,1);
  printChan(memory.getInt(datCtrl1Output+(loop*chanOffset)));
} // drawControlB

void UserCtrl::drawControlC(int loop){
  if (newScr){
    lcd.print("Ctrl");
    lcd.print(loop+1);
    lcd.setCursor(6,0);
    lcd.print("S:");
    lcd.setCursor(6,1);
    lcd.print("H:");
    userSelScroll= 0;
  }
  if (userSetReq){
    lcd.setCursor(6,0);
    if (memory.getBool(statFlash)) lcd.print("S:");
    else lcd.print("  ");
    memory.setFloat(datCtrl1Setpoint+(loop*chanOffset),memory.getFloat(datCtrl1Setpoint+(loop*chanOffset))+(float(userSelScroll)*0.1));
    userSelScroll= 0;
    if (userSetAcpt || millis()-userSetTime>30000){
      memory.saveFloat(datCtrl1Setpoint+(loop*chanOffset));
      userSetReq=  false;
      lcd.setCursor(6,0);
      lcd.print("S:");
    }
  }
  lcd.setCursor(8,0);
  int chan= memory.getInt(datCtrl1Input+(loop*chanOffset));
  printRead(memory.getFloat(datCtrl1Setpoint+(loop*chanOffset)),8,1,memory.getInt(datWQSensorUnits+chan-1),true);
  lcd.setCursor(8,1);
  printRead(memory.getFloat(datCtrl1Hysteresis+(loop*chanOffset)),8,1,memory.getInt(datWQSensorUnits+chan-1),true);
} // drawControlC

void UserCtrl::drawLogic(){
  if (newScr){    
    lcd.print("Logic");
    lcd.setCursor(0,1);
    lcd.print("A:");
    lcd.setCursor(8,1);
    lcd.print("B:");
    }
  lcd.setCursor(6,0);
  switch(memory.getInt(datLogicFunction)){
    case logicNot:  lcd.print("NOT A");break;
    case logicAnd:  lcd.print("AND  ");break;
    case logicNand: lcd.print("NAND ");break;
    case logicOr:   lcd.print("OR   ");break;
    case logicNor:  lcd.print("NOR  ");break;
    case logicXor:  lcd.print("XOR  ");break;
    case logicNxor: lcd.print("NXOR ");break;
    default:        lcd.print("     ");break;
  }
  lcd.setCursor(12,0);
  if(memory.getBool(statLogicGateResult)) lcd.print("High");
  else lcd.print("Low ");
  lcd.setCursor(2,1);
  printChan(memory.getInt(datLogicInA));
  lcd.setCursor(10,1);
  printChan(memory.getInt(datLogicInB));
} // drawToD

void UserCtrl::drawToD(){
  if (newScr){    
    lcd.print("TofD");
    }
  lcd.setCursor(5,0);
  printLeadZero(memory.getInt(datToDStartHour));
  lcd.print(":");
  printLeadZero(memory.getInt(datToDStartMin));
  lcd.print("-");
  printLeadZero(memory.getInt(datToDStopHour));
  lcd.print(":");
  printLeadZero(memory.getInt(datToDStopMin));
  lcd.setCursor(0,1);
  printTime();
  lcd.setCursor(8,1);
  if (memory.getBool(statToDEnable))
    if (memory.getBool(statNTPTimeValid))
      if (memory.getBool(statToDActive)) lcd.print(" Active ");
      else lcd.print("  Off   ");
    else lcd.print(" No NTP!");
  else lcd.print("Disabled");
} // drawToD

void UserCtrl::drawToD2(){
  if (newScr){    
    lcd.print("TofD");
    }
  lcd.setCursor(5,0);
  printChan(memory.getInt(datToDOutput1));
  lcd.setCursor(11,0);
  printChan(memory.getInt(datToDOutput2));
  lcd.setCursor(5,1);
  printChan(memory.getInt(datToDOutput3));
  lcd.setCursor(11,1);
  printChan(memory.getInt(datToDOutput4));  
} // drawToD2

void UserCtrl::drawOutputs(){
  if (newScr){
    lcd.print("Out");
    lcd.setCursor(4,0);
    lcd.print("1:    D1:");
    lcd.setCursor(1,1);
    lcd.print("Rly2:    D2:");
    }
  lcd.setCursor(6,0);
  printOnOff(memory.getBool(statRelay1Status));
  lcd.setCursor(13,0);
  printOnOff(memory.getBool(statDigitalOut1));
  lcd.setCursor(6,1);
  printOnOff(memory.getBool(statRelay2Status));
  lcd.setCursor(13,1);
  printOnOff(memory.getBool(statDigitalOut2));
} // drawRelay

void UserCtrl::drawCounter(){
  if (newScr){
    lcd.print("Counter");
    lcd.setCursor(4,1);
    lcd.print("Hz");
  }
  lcd.setCursor(10,0);
  printChan(memory.getInt(datCountSource));
  lcd.setCursor(0,1);
  printLeftInt(memory.getInt(datFrequency),4);
  lcd.setCursor(6,1);
  printLeftInt(memory.getLong(datCounter),10);
} // drawCounter

void UserCtrl::drawTimer(){
  if (newScr){
    lcd.print("Timer");
  }
  lcd.setCursor(10,0);
  printChan(memory.getInt(datTimerSource));
  lcd.setCursor(2,1);
  printLeftInt(memory.getLong(datTimer),10);
  lcd.print("s");
} // drawTimer

void UserCtrl::drawModbus(){
  if (newScr){
    lcd.print("ModB");
    }
  lcd.setCursor(8,0);
  if (ModbusActive()) lcd.print(" Active ");
  else lcd.print("Inactive");
  lcd.setCursor(1,1);
  if (ModbusAvailable()) lcd.print("  Available  ");
  else lcd.print("Not Available");
} // drawModbus

void UserCtrl::drawTime(){
  if (newScr){
    lcd.print("Time");
    }
  lcd.setCursor(7,0);
  if (timeCtrl.NTPValid()) lcd.print("NTP Valid");
  else lcd.print("NTP Fail");
  lcd.setCursor(0,1);
  printDate();
  lcd.print(" ");
  printTime();
} // drawTime

void UserCtrl::drawWiFi(){
  if (newScr){
    lcd.print("WiFi");
    userSelScroll= 0;
  }
  if (userSetReq){
    userSelect= userSelect+userSelScroll;
    userSelScroll= 0;
    if (userSelect<0) userSelect= userSelLimit;
    if (userSelect>userSelLimit) userSelect= 0;
    if (!userSetNext){  // choose network access point name
      if (userSetEnd){
        userSetEnd= false;
        userSetReq= false;
        setScreen(scrUnit);
        return;        
      }
      if (userSetAcpt){
        if (WiFi.SSID(userSelect).length()>0) memory.setStr(datWifiAPName,WiFi.SSID(userSelect).c_str());
        else memory.setStr(datWifiAPName,"Unknown");
        userSetAcpt= false;
        userSetNext= true;
        userSelect= 0;
        userSelPos= 0;
        userSelLimit= sizeof(pwChars)-1;
        lcd.cursor();
        //lcd.blink();
        wifiPass[0]= 0;
        lcd.setCursor(5,0);
        lcd.print("Password:");
        lcd.setCursor(0,1);
        lcd.print("                ");
      }
      else{
        userSelLimit= WiFi.scanComplete();
        if (wifiScanTime>millis()) wifiScanTime= millis(); // handle millis rollover
        if (userSelLimit==-2 && millis()-wifiScanTime>2000){
          WiFi.scanNetworks(true,false);
          Serial.println("  Network scan start");
        }
        if (millis()-wifiScanTime>wifiTimeout){
          userSelLimit= 0;
          WiFi.disconnect();
          Serial.println("  Network scan timeout");
        }
        if (userSelLimit>=0){
          Serial.print("Network scan complete, ");
          Serial.print(userSelLimit);
          Serial.println(" found");
          lcd.setCursor(5,0);
          lcd.print("Select...");
          lcd.setCursor(0,1);
          if (userSelLimit<1)  lcd.print(" No WiFi found! ");
          else{
            if (WiFi.SSID(userSelect).length()<1) lcd.print("Unknown      ");
            else lcd.print(WiFi.SSID(userSelect).substring(0,12));
            lcd.print("             ");
            lcd.setCursor(13,1);
            lcd.print(WiFi.RSSI(userSelect));
          }
        }
      }
    }
    else{  // enter password
      if (userSetEnd || userSelPos>15){
        userSetEnd= false;
        userSetReq= false;
        if (userSelPos<15 && userSelect<userSelLimit){
          wifiPass[userSelPos++]= pwChars[userSelect];
          wifiPass[userSelPos]= 0;
        }
        memory.setStr(datWifiPassword,wifiPass);
        memory.saveWiFi();
        setScreen(scrUnit);
        return;
      }
      if (userSetAcpt){  // accept and goto next char
        userSetAcpt= false;
        if (userSelect==userSelLimit){  // delete
          if (userSelPos>0) userSelPos--;
        }
        else wifiPass[userSelPos++]= pwChars[userSelect];
        if (userSelPos<15){
          wifiPass[userSelPos]= 0;
        }
      }
      else{
        lcd.setCursor(0,1);
        lcd.print(wifiPass);
        if (userSelect==userSelLimit) lcd.print((char)127);
        else lcd.print(pwChars[userSelect]);
        lcd.print(" ");
        lcd.setCursor(userSelPos,1);
      }
    }
  }
  else{  // normal display
    if (wifiStat){
      lcd.setCursor(5,0);
      lcd.print(WiFi.SSID());
      lcd.setCursor(0,1);
      lcd.print(wifiIPAddr);
    }
    else{
      lcd.setCursor(2,1);
      lcd.print("No network!");
    }
  }
} // drawWiFi

void UserCtrl::drawWiFi2(){
  if (newScr) lcd.print("WiFi");
  if (wifiStat){
      lcd.setCursor(5,0);
      lcd.print(WiFi.SSID());
      int sigStr= WiFi.RSSI();
      lcd.setCursor(0,1);
      if (sigStr<-80)      lcd.print("Unstable  ");
      else if (sigStr<-70) lcd.print("Weak      ");
      else if (sigStr<-60) lcd.print("Moderate  ");
      else if (sigStr<-50) lcd.print("Strong    ");
      else                 lcd.print("Excellent ");
      lcd.print(sigStr);
      lcd.print("dBm");
  }
  else{
    setScreen(screen+1);
    return;
  }
} // drawWiFi2

void UserCtrl::drawIntData(){
  if (newScr){
    lcd.print("Int Temp");
    lcd.setCursor(0,1);
    lcd.print("   Sup V");
    }
  lcd.setCursor(9,0);
  printRead(memory.getFloat(datIntTemp),7,1,memory.getInt(datIntTempUnits),memory.getBool(statIntTempValid));
  lcd.setCursor(9,1);
  printRead(memory.getFloat(datSupplyVoltage),7,2,memory.getInt(datSupVoltUnits),memory.getBool(statSupVoltValid));
} // drawIntData

void UserCtrl::drawUnit(){
  if (newScr){
    char unit[18];
    memory.getStr(datModelName,unit);
    if (unit[0]!=0) lcd.print(unit);
    else lcd.print("Unit");
    lcd.setCursor(0,1);
    lcd.print("SN ");
    lcd.print(memory.getInt(datSerialNumber));
    lcd.setCursor(8,1);
    lcd.print("FW ");
    lcd.print("v");
    lcd.print(firmMajor);
    lcd.print(".");
    lcd.print(firmMinor);
  }
} // drawUnit

void UserCtrl::drawWiFiStart(){
  if (newScr){
    lcd.print("WiFi  Connect");
    wifiStart= millis();
  }
  int pos= (millis()-wifiStart)/1000;
  if (pos>15) pos=15;
  lcd.setCursor(pos,1);
  lcd.print(char(255));
} // drawWiFiStart

void UserCtrl::drawWiFiDone(){
  if (newScr){
    lcd.print("WiFi ");
    if (wifiStat) lcd.print("Connected");
    else lcd.print("Failed");
    lcd.setCursor(0,1);
    if (wifiStat) lcd.print(wifiIPAddr);
  }
  // go to status screen after startup delay
  if (!memory.getBool(statStartup)) setScreen(1);
} // drawWiFiStart

//- End userCtrl ---------------------------------------------------------------
