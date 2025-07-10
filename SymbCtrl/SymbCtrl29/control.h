/*------------------------------------------------------------------------------
  Control - Symbrosia Controller
  - handle the control loops

  - Written for the ESP32

  01Jan2022 A. Cooper
  - initial version
  25Jul2024 v 2.6 A. Cooper
  - added class variables to implement hold time and one-shot

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
#ifndef ctrlCtrl
#define ctrlCtrl

//- Library includes -----------------------------------------------------------
#include <Arduino.h>

//- a little class -------------------------------------------------------------
class Control{
  public:
    Control();
    void init();
    void service();
    bool controlled(int chan);
  private:
    unsigned long timeLast;
    int proc;
    unsigned long switchTime[4];
    bool stateHold[4], stateLast[4], oneShot[4];
};

#endif
//- End control.h --------------------------------------------------------------
