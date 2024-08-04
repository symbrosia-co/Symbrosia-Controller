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
#ifndef logCtrl
#define logCtrl

//- Library includes -----------------------------------------------------------
#include <Arduino.h>

//- a little class -------------------------------------------------------------
class LogicCtrl{
  public:
    LogicCtrl();
    void init();
    void service();
};

#endif
//- End logicCtrl.h -------------------------------------------------------------