/*------------------------------------------------------------------------------
  Modbus Control - Symbrosia Controller
  - handle the modbus Modbus service
  - move data betwixt the primary data buffer and the modbus registers

  - Written for the ESP32
  - Uses the Arduino Modbus library by Andre Sarmento Barbosa
  info and docs at https://github.com/emelianov/modbus-esp8266
  - This is NOT a class as C does not support using class methods for the
  callback functions

  24Dec2021 v0.1 A. Cooper
  - initial version
  21Jan2022 A. Cooper
  - removed register types

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
#ifndef mbCtrl
#define mbCtrl

//- Library includes -----------------------------------------------------------
#include <Arduino.h>
#include <ModbusTCP.h>

// modbus register sizes
#define mbBaseCoil         0
#define mbBaseHold         0

//- functions ------------------------------------------------------------------
void ModbusInit();

// service routine, call in main loop
void ModbusService();

// maintain heartbeat
void ModbusHeartbeat();

// true if modbus setup and running
bool ModbusAvailable();

// true if recent modbus comm activity
bool ModbusActive();

// get info on registers
char ModbusGetHoldMode(int addr);
char ModbusSetCoilMode(int addr);
int  ModbusSetHoldSize();
int  ModbusGetCoilSize();

uint16_t ModbusOnReadHold(TRegister* reg, uint16_t val);
uint16_t ModbusOnWriteHold(TRegister* reg, uint16_t val);
uint16_t ModbusOnWriteCoil(TRegister* reg, uint16_t val);
uint16_t ModbusOnReadCoil(TRegister* reg, uint16_t val);

#endif
//- End modbus.h ---------------------------------------------------------------
