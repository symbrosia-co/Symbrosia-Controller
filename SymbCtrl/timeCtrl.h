/*------------------------------------------------------------------------------
  Time Control - Symbrosia Controller
  - handle the network time

  - Written for the ESP32

  01Jan2022 A. Cooper
  - initial version
  31Mar2021 v2.4 A. Cooper
  - Major update/rewrite to properly use ESP32 RTC in place of generic
  Arduino timekeeping library

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
#ifndef tmCtrl
#define tmCtrl

//- library includes -----------------------------------------------------------
#include <Arduino.h>

//- a little class -------------------------------------------------------------
class TimeCtrl{
  public:
    TimeCtrl();
    void init();
    bool setTime();
    bool NTPValid();
    void service();
    unsigned long timeSinceBoot();
    bool midnight();
    void printTime();
  private:
    bool timeValid;         // successful recent NTP fetch
    unsigned long timeZero; // millis() at code start
    unsigned long timeBoot; // time of controller boot
    unsigned long timeLast; // time of last successful NTP fetch
    bool timeSet;           // flag used for setting time on the half hour
    int  timeDay;           // current day (used for midnight detection)
};

#endif
//- End timeCtrl.h ---------------------------------------------------------------
