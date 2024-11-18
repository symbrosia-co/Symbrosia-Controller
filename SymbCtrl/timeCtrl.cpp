/*------------------------------------------------------------------------------
  Time Control - Symbrosia Controller
  - handle the network time

  - Written for the ESP32

  01Jan2022 A. Cooper
  - initial version
  15Apr2022 A. Cooper
  - changed setTime to on the half hour
  - run setTime uses a two step process to avoid rerun with slight backwards
  change in time at 20 and 30 minutes into the hour
  31Mar2024 v2.4 A. Cooper
  - Major update/rewrite to properly use ESP32 RTC in place of generic
  Arduino timekeeping library
  - better handling of WiFi connection, retries and detection of bad connection,
   loss of NTP time

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
#include <ESP32Time.h>

//- Local includes -------------------------------------------------------------
#include "globals.h"
#include "timeCtrl.h"
#include "Memory.h"
extern Memory memory;

//- instantiate libaries -------------------------------------------------------
ESP32Time rtc(timeZone*3600);

//- functions ------------------------------------------------------------------

TimeCtrl::TimeCtrl(){
}

void TimeCtrl::init(){
  rtc.setTime(memory.getInt(datSecond),
              memory.getInt(datMinute),
              memory.getInt(datHour),
              memory.getInt(datDay),
              memory.getInt(datMonth),
              memory.getInt(datYear));
  timeZero= millis();
  timeBoot= rtc.getLocalEpoch();
  timeLast= 0;
  timeDay=  0;
  timeSet=  false;
  timeValid= false;
  memory.setBool(statNTPTimeValid,false);
  memory.setBool(statStartup,true);
} // init

bool TimeCtrl::setTime(){
  if (wifiStat){
    Serial.println("  Fetch network time...");
    configTime(0,0,ntpServer1,ntpServer2);
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)){
      timeValid= true;
      rtc.setTimeStruct(timeinfo);
      timeLast= rtc.getLocalEpoch();
      Serial.println("    NTP fetch successful");
      // move RTC time to modBus registers   
      memory.setUInt(datSecond,rtc.getSecond());
      memory.setUInt(datMinute,rtc.getMinute());
      memory.setUInt(datHour,  rtc.getHour(true));
      memory.setUInt(datDay,   rtc.getDay());
      memory.setUInt(datMonth, rtc.getMonth());
      memory.setUInt(datYear,  rtc.getYear());
      Serial.print("    ");printTime();Serial.println(" ");
      return true;
    }
    else Serial.println("    Failed to obtain time");
  }
  return false;
}

bool TimeCtrl::NTPValid(){
  return timeValid;
}

void TimeCtrl::service(){
  if (memory.getBool(statStartup)){
    // clear startup after the specified number of seconds, ideally about 40s
    if (((millis()-timeZero)/1000)>startupDelay){
      memory.setBool(statStartup,false);
      if (wifiStat && timeValid){
        timeBoot= rtc.getLocalEpoch()-startupDelay;
        timeLast= rtc.getLocalEpoch()-startupDelay;
        timeDay=  rtc.getDay();
      }
      printTime();
      Serial.println("Startup delay expired");
    }
  }
  else{
    // get NTP time every hour on the half hour
    if (memory.getUInt(datMinute)==20) timeSet= true;
    if (timeSet && memory.getUInt(datMinute)==30){
      timeSet= false;
      setTime();
    }
    // check for timeouts
    if ((rtc.getLocalEpoch()-timeLast)/3600>timeNoNetMax) wifiStat= false;
    if ((rtc.getLocalEpoch()-timeLast)/3600>timeNoNTPMax) timeValid=false;
  }
  // move RTC time to modBus registers   
  memory.setUInt(datSecond,rtc.getSecond());
  memory.setUInt(datMinute,rtc.getMinute());
  memory.setUInt(datHour,  rtc.getHour(true));
  memory.setUInt(datDay,   rtc.getDay());
  memory.setUInt(datMonth, rtc.getMonth());
  memory.setUInt(datYear,  rtc.getYear());
  // flash
  memory.setBool(statFlash,rtc.getMillis()<500);
  // check timeouts for time and network
  memory.setBool(statNTPTimeValid,timeValid);
} // service

unsigned long TimeCtrl::timeSinceBoot(){
  return rtc.getLocalEpoch()-timeBoot;
}

// true if midnight, only works once per day
bool TimeCtrl::midnight(){
  if (!memory.getBool(statStartup) && timeValid)
    if (timeDay!=rtc.getDay()){
      timeDay= rtc.getDay();
      Serial.println("Midnight!");
      return true;
    }
  return false;
}

void TimeCtrl::printTime(){
  if (timeValid){
    Serial.print(memory.getInt(datYear));
    Serial.print("-");
    if (memory.getInt(datMonth)+1<10) Serial.print("0");
    Serial.print(memory.getInt(datMonth)+1);
    Serial.print("-");
    if (memory.getInt(datDay)<10) Serial.print("0");
    Serial.print(memory.getInt(datDay));
    Serial.print(" ");
    if (memory.getInt(datHour)<10) Serial.print("0");
    Serial.print(memory.getInt(datHour));
    Serial.print(":");
    if (memory.getInt(datMinute)<10) Serial.print("0");
    Serial.print(memory.getInt(datMinute));
    Serial.print(":");
    if (memory.getInt(datSecond)<10) Serial.print("0");
    Serial.print(memory.getInt(datSecond));
    Serial.print(" ");
  }
}

//- End timeCtrl ---------------------------------------------------------------
