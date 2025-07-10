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
  02Nov2024 v2.8 A. Cooper
  - move LCD screen constants to globals.h
  - add getScreen

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

//- a little class -------------------------------------------------------------
class UserCtrl{
  public:
    UserCtrl();
    void init();
    void service();
    void setScreen(int scr);
    int  getScreen();
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
    void drawSerial();
    void drawHardware();
    void drawProcessor();
    void drawFirmware();
};

#endif
//- End userCtrl.h -------------------------------------------------------------
