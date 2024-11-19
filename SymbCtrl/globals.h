/*------------------------------------------------------------------------------
  Globals - Symbrosia Controller
  Copyright © 2021 Symbrosia Inc.

  This program is free software: you can redistribute it and/or modify it under 
  the terms of the GNU General Public License as published bythe Free Software
  foundation, either version 3 of the License, or (at your option) any later
  version.

  This program is distributed in the hope that it will be useful, but WITHOUT
  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along with
  this program.  If not, see <https://www.gnu.org/licenses/>.

--- revision record ------------------------------------------------------------

  26Dec2021 v0.1 A. Cooper
  - initial version
  16Apr2022 v1.0 A. Cooper
  - first release candidate
  16Dec2023 v2.0 A. Cooper
  - modify for Mark 2 PCB's
  20Mar2024 v2.4 A. Cooper
  - Added and tested support for Wemos ESP32-S2 Mini, S2 mini and S3 mini are
  the current processor module choices
  - removed support for ESP32 Saola and older rev PCB's
  - added monthly reset
  - added combined control alarms
  - added a few new units: ppm, day, hour, min, sec
  - added datFrequency to support frequency counter
  25Mar2024 v2.6 A. Cooper
  - added control enable source
  - added control one-shot flag
  - added TofD to IO channel list
  - added a few new units
  02Nov2024 v2.8 A. Cooper
  - move LCD screen constants here from userCtrl.h
  - add screen ID's for fixed data entry (92 to 94)
  - add screen ID's for firmware update (95)
  - add fixed data definitions (serial,hardware, processor)

------------------------------------------------------------------------------*/
#pragma once

#define hardwareS2Mini 2
//#define hardwareS3Mini 3

#ifdef hardwareS2Mini
#include "hardwareSymbCtrlS2Mini.h"
#endif

#ifdef hardwareS3Mini
#include "hardwareSymbCtrlS3Mini.h"
#endif

// unit ID 
#define firmMajor     2
#define firmMinor     8
#define modelNameStr  "SymbCtrl Mk2"

// default time zone
#define timeZone      -10

// alarm points
#define alarmVSupLow  8  // low supply voltage alarm point
#define alarmVSupHigh 16 // high supply voltage alarm point
#define alarmIntTHigh 55 // high internal temperature alarm point in C

// network loss time limits
#define timeNoNetMax   2 // time to indicate net loss in hours
#define timeNoNTPMax  48 // time to indicate NTP time invalid in hours

// startup lockout
#define startupDelay  30 // startup lockout in seconds\p\order\detail.html

// misc
#define forceSerial   false // force load of fixed data (serial, hardware, etc)
#define forceDefaults false // force load of defaults on boot

//- WiFi credentials -----------------------------------------------------------
#define defWiFi "SSID"
#define defPass "Pass"

//- ntp server -----------------------------------------------------------------
#define ntpServer1 "pool.ntp.org"
#define ntpServer2 "time.nist.gov"

// global variables and functions ----------------------------------------------
extern bool      wifiStat;
extern IPAddress wifiIPAddr;

// serial number
#define serialNumMin       100
#define serialNumStart     250
#define serialNumMax       999

// hardware ID codes...
#define hdwrIDmk1            1
#define hdwrIDmk2revA        2
#define hdwrIDmk2revB        3
#define hdwrIDMin            1
#define hdwrIDMax            3

// processor ID codes...
#define procIDS2Saola        1
#define procIDS2Mini         2
#define procIDS3Mini         3
#define procIDMin            1
#define procIDMax            3

// Output control...
#define ctrlOuts             4
#define ctrlRelay1           0
#define ctrlRelay2           1
#define ctrlOutput1          2
#define ctrlOutput2          3
#define ctrlSrcs             7
#define ctrlCtrl1            0
#define ctrlCtrl2            1
#define ctrlCtrl3            2
#define ctrlCtrl4            3
#define ctrlToD              4
#define ctrlLogic            5
#define ctrlExtReq           6

// I/O channels...
#define ioNone               0 // no I/O channel (no action)
#define ioWQAmp              1 // WQ sensor amplifier
#define ioTemp1              2 // temperature amplifier 1
#define ioTemp2              3 // temperature amplifier 2
#define ioAnalog1            4 // analog input 1
#define ioAnalog2            5 // analog input 2
#define ioIntTemp            6 // internal temperature
#define ioSupplyV            7 // supply voltage
#define ioProcRead           8 // processed reading
#define ioDigIn1             9 // digital input 1
#define ioDigIn2            10 // digital input 2
#define ioRelay1            11 // output relay 1
#define ioRelay2            12 // output relay 2
#define ioDigOut1           13 // digital output 1
#define ioDigOut2           14 // digital output 2
#define ioVState1           15 // virtual IO
#define ioVState2           16
#define ioCtrl1             17 // control outputs
#define ioCtrl2             18
#define ioCtrl3             19
#define ioCtrl4             20
#define ioCAlm              21 // Control loop alarms
#define ioC1Alm             22
#define ioC2Alm             23
#define ioC3Alm             24
#define ioC4Alm             25
#define ioC1AlmLo           26
#define ioC2AlmLo           27
#define ioC3AlmLo           28
#define ioC4AlmLo           29
#define ioC1AlmHi           30
#define ioC2AlmHi           31
#define ioC3AlmHi           32
#define ioC4AlmHi           33
#define ioFlash             34 // a flasher on/off 1Hz
#define ioDays              35 // day of month in decimal days 0.0 to 31.99d
#define ioHours             36 // time of day in decimal hours 0.0 to 23.99h
#define ioMinutes           37 // minutes and seconds in decimal 0.00 to 59.99m
#define ioSeconds           38 // seconds in decimal 0 to 59s
#define ioTofD              39 // time of day function result

// modbud address enumeration
// status
#define datStatusCode        0
#define datModelNumber       1
#define datSerialNumber      2
#define datFirmwareRev       3
#define datHeartbeatIn       4
#define datHeartbeatOut      5
#define datStatusDisp1       8
#define datStatusDisp2       9
// time
#define datTimezone         10
#define datYear             11
#define datMonth            12
#define datDay              13
#define datHour             14
#define datMinute           15
#define datSecond           16
// analog inputs
#define datWQ               20
#define datTemperature1     22
#define datTemperature2     24
#define datAnalog1          26
#define datAnalog2          28
#define datIntTemp          30
#define datSupplyVoltage    32
#define datProcessedData    34
#define datWQSensorUnits    36
#define datTemp1Units       37
#define datTemp2Units       38
#define datAnalog1Units     39
#define datAnalog2Units     40
#define datIntTempUnits     41
#define datSupVoltUnits     42
#define datProcUnits        43
#define datPHTempComp       44
// calibration
#define datWQOffset         50
#define datTemp1Offset      52
#define datTemp2Offset      54
#define datAnalog1Offset    56
#define datAnalog2Offset    58
#define datWQGain           60
#define datTemp1Gain        62
#define datTemp2Gain        64
#define datAnalog1Gain      66
#define datAnalog2Gain      68
// control
#define datCtrl1Input       70
#define datCtrl1Output      71
#define datCtrl1Setpoint    72
#define datCtrl1Hysteresis  74
#define datCtrl1AlarmLow    76
#define datCtrl1AlarmHigh   78
#define datCtrl1EnbSource   80
#define datCtrl1MinOnTime   81
#define datCtrl1Minimum     82
#define datCtrl1Maximum     84
#define datCtrl2Input       86
#define datCtrl2Output      87
#define datCtrl2Setpoint    88
#define datCtrl2Hysteresis  90
#define datCtrl2AlarmLow    92
#define datCtrl2AlarmHigh   94
#define datCtrl2EnbSource   96
#define datCtrl2MinOnTime   97
#define datCtrl2Minimum     98
#define datCtrl2Maximum    100
#define datCtrl3Input      102
#define datCtrl3Output     103
#define datCtrl3Setpoint   104
#define datCtrl3Hysteresis 106
#define datCtrl3AlarmLow   108
#define datCtrl3AlarmHigh  110
#define datCtrl3EnbSource  112
#define datCtrl3MinOnTime  113
#define datCtrl3Minimum    114
#define datCtrl3Maximum    116
#define datCtrl4Input      118
#define datCtrl4Output     119
#define datCtrl4Setpoint   120
#define datCtrl4Hysteresis 122
#define datCtrl4AlarmLow   124
#define datCtrl4AlarmHigh  126
#define datCtrl4EnbSource  128
#define datCtrl4MinOnTime  129
#define datCtrl4Minimum    130
#define datCtrl4Maximum    132

// logic gate
#define datLogicInA        136
#define datLogicInB        137
#define datLogicFunction   138
#define datLogicOut        139
// ToD Control
#define datToDStartHour    140
#define datToDStartMin     141
#define datToDStopHour     142
#define datToDStopMin      143
#define datToDOutput1      144
#define datToDOutput2      145
#define datToDOutput3      146
#define datToDOutput4      147
// counter and timer
#define datCountSource     150
#define datCounter         151
#define datCountRstIntv    153
#define datTimerSource     154
#define datTimer           155
#define datTimerRstIntv    157
#define datFrequency       158
// logging
#define datLogInterval     160
#define datLogRecords      161
#define datLogNumber       162
#define datLogItem         163
#define datLogData         164
// processed reading
#define datProcessChanA    166
#define datProcessChanB    167
#define datProcessID       168
// text fields
#define datModelName       170
#define datControlName     178
#define datWQName          186
#define datTemp1Name       194
#define datTemp2Name       202
#define datInput1Name      210
#define datInput2Name      218
#define datRelay1Name      226
#define datRelay2Name      234
#define datOutput1Name     242
#define datOutput2Name     250
#define datControl1Name    258
#define datControl2Name    266
#define datControl3Name    274
#define datControl4Name    282
#define datWifiAPName      300
#define datWifiPassword    308    
// state registers
#define statStatus           0
#define statNTPTimeValid     1
#define statStartup          2
#define statSaveSettings     3
#define statClearSettings    4
#define statMidnightSave     5
#define statMidnightReset    6
#define statSilenceAlarms    7
#define statDigitalIn1       8
#define statDigitalIn2       9
#define statRelay1Status    10
#define statRelay2Status    11
#define statDigitalOut1     12
#define statDigitalOut2     13
#define statRelay1Request   14
#define statRelay2Request   15
#define statDout1Request    16
#define statDout2Request    17
#define statVState1         18
#define statVState2         19
#define statWQSensorValid   20
#define statTemp1Valid      21
#define statTemp2Valid      22
#define statAnalog1Valid    23
#define statAnalog2Valid    24
#define statIntTempValid    25
#define statSupVoltValid    26
#define statProcReadValid   27
#define statLogicGateResult 28
#define statFlash           29
// process control
#define statCtrl1Enable     30
#define statCtrl2Enable     31
#define statCtrl3Enable     32
#define statCtrl4Enable     33
#define statCtrl1High       34
#define statCtrl2High       35
#define statCtrl3High       36
#define statCtrl4High       37
#define statCtrl1Active     38
#define statCtrl2Active     39
#define statCtrl3Active     40
#define statCtrl4Active     41
#define statCtrlAlarm       42
#define statCtrl1Alarm      43
#define statCtrl2Alarm      44
#define statCtrl3Alarm      45
#define statCtrl4Alarm      46
#define statCtrl1AlarmLow   47
#define statCtrl2AlarmLow   48
#define statCtrl3AlarmLow   49
#define statCtrl4AlarmLow   50
#define statCtrl1AlarmHigh  51
#define statCtrl2AlarmHigh  52
#define statCtrl3AlarmHigh  53
#define statCtrl4AlarmHigh  54
#define statRstCtrl1Max     55
#define statRstCtrl2Max     56
#define statRstCtrl3Max     57
#define statRstCtrl4Max     58
#define statCounterEnable   59
#define statTimerEnable     60
#define statToDEnable       61
#define statToDActive       62
#define statResetCounter    63
#define statResetTimer      64
#define statResetLogging    65
#define statCtrl1OneShot    66
#define statCtrl2OneShot    67
#define statCtrl3OneShot    68
#define statCtrl4OneShot    69

// lookup array to convert IO channel to modbus address
const int ioAddr[]={
  0,                 // ioNone     0
  datWQ,             // ioWQAmp    1
  datTemperature1,   // ioTemp1    2
  datTemperature2,   // ioTemp2    3
  datAnalog1,        // ioAnalog1  4
  datAnalog2,        // ioAnalog2  5
  datIntTemp,        // ioIntTemp  6
  datSupplyVoltage,  // ioSupplyV  7
  datProcessedData,  // ioProcRead 8
  statDigitalIn1,    // ioDigIn1   9
  statDigitalIn2,    // ioDigIn2  10
  statRelay1Status,  // ioRelay1  11
  statRelay2Status,  // ioRelay2  12
  statDigitalOut1,   // ioDigOut1 13
  statDigitalOut2,   // ioDigOut2 14
  statVState1,       // ioVState1 15
  statVState2,       // ioVState2 16
  statCtrl1Active,   // ioCtrl1   17
  statCtrl2Active,   // ioCtrl2   18
  statCtrl3Active,   // ioCtrl3   19
  statCtrl4Active,   // ioCtrl4   20
  statCtrlAlarm,     // ioCAlm    21
  statCtrl1Alarm,    // ioC1Alm   22
  statCtrl2Alarm,    // ioC2Alm   23
  statCtrl3Alarm,    // ioC3Alm   24
  statCtrl4Alarm,    // ioC4Alm   25
  statCtrl1AlarmLow, // ioC1AlmLo 26
  statCtrl2AlarmLow, // ioC2AlmLo 27
  statCtrl3AlarmLow, // ioC3AlmLo 28
  statCtrl4AlarmLow, // ioC4AlmLo 29
  statCtrl1AlarmHigh,// ioC1AlmHi 30
  statCtrl2AlarmHigh,// ioC2AlmHi 31
  statCtrl3AlarmHigh,// ioC3AlmHi 32
  statCtrl4AlarmHigh,// ioC4AlmHi 33
  statFlash,         // ioFlash   34
  datDay,            // ioDays    35
  datHour,           // ioHours   36
  datMinute,         // ioMinutes 37
  datSecond,         // ioSeconds 38
  statToDActive      // ioToD     39
};

// ADC channel enumeration
#define hdwrWQ         0
#define hdwrTemp1      1
#define hdwrTemp2      2
#define hdwrAnalog2    3
#define hdwrAnalog1    4
#define hdwrSupplyVolt 5
#define hdwrTempInt    6
#define hdwrAnalog3    7
#define hdwrAnalog4    8

// units
#define unitsNone   0	// No units
#define unitsDegC   1	// °C
#define unitsDegF   2	// °F
#define unitspH     3	// pH
#define unitsmV     4	// mV
#define unitsV      5	// V
#define unitsmA     6	// mA
#define unitsA      7	// A
#define unitsmm     8	// mm
#define unitsm      9	// m
#define unitsml    10	// ml
#define unitsl     11	// l
#define unitsg     12	// g
#define unitskg    13	// kg
#define unitslbs   14	// lbs
#define unitskPa   15	// kPa
#define unitsPSI   16	// PSI
#define unitsHz    17	// Hz
#define unitsPct   18	// %
#define unitsPPM   19	// %
#define unitsOhm   20	// Ω
#define unitsDay   21  // day
#define unitsHour  22  // hour
#define unitsMin   23  // min
#define unitsSec   24  // s
#define unitsMol   25  // mol
#define unitsMPH   26  // mph
#define unitsMPS   27  // m/s
#define unitsDeg   28  // degrees
#define unitsmmH   29  // mmHg
#define unitsmBar  30  // mBar
#define unitsWatt  31  // watts
#define unitskWatt 32  // kilowatts
#define unitskVA   33  // kVA

// data processing
#define procAvg    0  // average
#define procMin    1  // choose minimum
#define procMax    2  // choose maximum
#define procSum    3  // sum the values
#define procDiff   4  // find the difference A-B
#define procValid  5  // keep a valid read with priority for A over B

// logic gate function
#define logicNot   0  // not of input A
#define logicAnd   1
#define logicNand  2
#define logicOr    3
#define logicNor   4
#define logicXor   5
#define logicNxor  6
#define logicEcho  7

// counter and timer reset intervals
#define resetNever   0
#define resetHourly  1
#define resetDaily   2
#define resetMonthly 3

// LCD screens
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
#define scrSerial    92
#define scrHardware  93
#define scrProcessor 94
#define scrFirmware  95

//- End globals.h --------------------------------------------------------------
