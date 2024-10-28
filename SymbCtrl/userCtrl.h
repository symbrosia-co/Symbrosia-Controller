/*------------------------------------------------------------------------------
  User Interface Control - Symbrosia Controller
  - handle an input encoder and an LCD display

  - Written for the ESP32

  01Jan2022 A. Cooper
  - initial version
  20Mar2024 v2.4 A. Cooper
  - added screen for internal temp and supply voltage
  08Oct2024 v2.7 A. Cooper
  - major re-write to clean up the methods for handling user input
  such as calibration and WiFi credential input, a number of private
  variables were added and deleted

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
#ifndef uiCtrl
#define uiCtrl

//- Library includes -----------------------------------------------------------
#include <Arduino.h>

//- constants ------------------------------------------------------------------
#define scrSplash     0
#define scrFirst      1
#define scrStatus     1
#define scrWQSensor   2
#define scrTemps      3
#define scrAnalog     4
#define scrProc       5
#define scrControl1a  6
#define scrControl1b  7
#define scrControl1c  8
#define scrControl2a  9
#define scrControl2b 10
#define scrControl2c 11
#define scrControl3a 12
#define scrControl3b 13
#define scrControl3c 14
#define scrControl4a 15
#define scrControl4b 16
#define scrControl4c 17
#define scrLogic     18
#define scrOutputs   19
#define scrToD       20
#define scrToD2      21
#define scrCounter   22
#define scrTimer     23
#define scrModbus    24
#define scrTime      25
#define scrWiFi      26
#define scrWiFi2     27
#define scrIntData   28
#define scrUnit      29
#define scrLast      29
#define scrWiFiStart 90
#define scrWiFiDone  91

//- a little class -------------------------------------------------------------
class UserCtrl{
  public:
    UserCtrl();
    void init();
    void service();
    void setScreen(int scr);
    void left();
    void right();
    void click();
    void press();
    void dClick();
  private:
    int screen= 0;
    bool newScr= true;
    unsigned long lastUpdate;
    unsigned long screenTime;
    int userSetReq;
    bool userSetNext;
    bool userSetAcpt;
    unsigned long userSetTime;
    int userSelect;   
    int userSelLimit;
    int userSelScroll;
    int userSelPos;
    char wifiPass[16];
    unsigned long wifiStart;

    void printChan(int chan);
    void printState(int chan);
    void printRead(float read,int space,int decs,int unit,bool valid);
    void printLeadZero(int num);
    void printLeftInt(int num,int space);
    void printDate();
    void printTime();
    void printOnOff(bool state);
    void drawScreen();
    void drawSplash();
    void drawStatus();
    void drawWQSensor();
    void drawTemps();
    void drawAnalog();
    void drawProc();
    void drawControlA(int loop);
    void drawControlB(int loop);
    void drawControlC(int loop);
    void drawLogic();
    void drawToD();
    void drawToD2();
    void drawOutputs();
    void drawCounter();
    void drawTimer();
    void drawLogging();
    void drawModbus();
    void drawTime();
    void drawWiFi();
    void drawWiFi2();
    void drawIntData();
    void drawUnit();
    void drawWiFiStart();
    void drawWiFiDone();
};

#endif
//- End userCtrl.h -------------------------------------------------------------
