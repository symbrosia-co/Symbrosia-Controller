/*------------------------------------------------------------------------------
  Proccess Data - Symbrosia Controller
  - merge the results of two channels
  - Written for the ESP32

  3Apr2022 A. Cooper
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
#ifndef prCtrl
#define prCtrl

//- Library includes -----------------------------------------------------------
#include <Arduino.h>

//- a little class -------------------------------------------------------------
class ProcCtrl{
  public:
    ProcCtrl();
    void init();
    void service();
  private:
    unsigned long procLastTime;      
};

#endif
//- End procCtrl.h -------------------------------------------------------------
