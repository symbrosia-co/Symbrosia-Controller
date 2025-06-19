#------------------------------------------------------------------------------
#  SymbCtrl Scanner
#
#  - Handle the modbus functions of a Symbrosia Controller
#  - Use multiprocess to spawn a subprocesses to get data asychronously
#
#  External notes...
#  - SyScan.start(ip)           start subprocess and initiate scanning
#  - SyScan.connected()         return True if scanning a controller
#  - SyScan.scanInt(interval)   set the controller scan interval, default is 2s
#  - SyScan.read(regName)       retrieve a specific datum by name
#                               will return None if an error occurs
#  - SyScan.write(regName,value) write a specific datum to the controller
#  - SyScan.status()            connection status, true= good
#  - SyScan.error()             get the result of the last operation
#                               true= error occurred
#  - SyScan.message()           get error message in text form
#  - SyScan.close()             kill the subprocesses and end scanning
#  - SyScan.registers()         return all register names as a list
#  - SyScan.type(regName)       return the register type by name
#                                 int:    signed 16bit integer
#                                 uint:   unsigned 16bit integer
#                                 float:  IEEE-754 32bit floating point
#                                 bool:   boolean
#                                 string: char string up to 16 characters
#  - SyScan.mode(regName)       the register mode
#                                 r:      read only
#                                 w:      write only
#                                 +:      read and write
#
#  Internal notes...
#  - communication with the subprocess takes place through an array of integers
#        0:  data valid
#        1:  command to subprocess
#              0:none
#             -1:kill
#              1:write coil
#              2:write hold
#              3:scan time
#        2:  subprocess error
#              0:none
#              1:com error
#              2:read error
#              3:write error
#              4:write buffer full
#        3:  IP address byte 1
#        4:  IP address byte 2
#        5:  IP address byte 3
#        6:  IP address byte 4
#        7:  write address
#        8:  write count
#        9 to 16:   write data
#        17 to 86:  coil register data
#        87 to 306: holding register data
#
#  Symbrosia
#  Copyright 2021-2025, all rights reserved
#
# 23Mar2025 A. Cooper
#  - initial version
# 29Mar2025 A. Cooper
#  - first version functionally complete
#  - added a buffer in subprocess for write commands
#  - reverted convert module, it really was needed;)
#  - fixed read only mode on logic gate output -> rw
#
#------------------------------------------------------------------------------

#-- library -------------------------------------------------------------------
import os
import datetime as dt
import time
import ipaddress
from enum import IntEnum
from multiprocessing import Process, Array
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

#-- constants -----------------------------------------------------------------
debugScan= False
debugSub=  False

#------------------------------------------------------------------------------
#  SyScan Class
#
#  - class for access to the SymbCtrl
#
#------------------------------------------------------------------------------
class SymbCtrl():
  ctrl=     None   # controller subprocess
  shared=   None   # controller subprocess shared array
  ipAddr=   ''     # controller IP address
  name=     None   # controller name read from controller
  error=    False  # error status of last call
  message=  ''     # text description of last call result
  ctrlRegs= {          # mapping of all implemented Modbus registers in the SymbCtrl mk2
    'ModelName':       {'addr':170,'mode':'r', 'type':'str',  'unit':None,            'valid':None,            'desc':'Controller model name'},
    'ControlName':     {'addr':178,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'User assigned controller name'},
    'WQName':          {'addr':186,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Water quality sensor description'},
    'Temp1Name':       {'addr':194,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Temperature sensor 1 description'},
    'Temp2Name':       {'addr':202,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Temperature sensor 2 description'},
    'Input1Name':      {'addr':210,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Input 1 description'},
    'Input2Name':      {'addr':218,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Input 2 description'},
    'Relay1Name':      {'addr':226,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Relay 1 description'},
    'Relay2Name':      {'addr':234,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Relay 2 description'},
    'Output1Name':     {'addr':242,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Digital output 1 description'},
    'Output2Name':     {'addr':250,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Digital output 2 description'},
    'Control1Name':    {'addr':258,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Decription of control loop 1'},
    'Control2Name':    {'addr':266,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Decription of control loop 2'},
    'Control3Name':    {'addr':274,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Decription of control loop 3'},
    'Control4Name':    {'addr':282,'mode':'rw','type':'str',  'unit':None,            'valid':None,            'desc':'Decription of control loop 4'},
    'StatusCode':      {'addr':  0,'mode':'r', 'type':'uint', 'unit':None,            'valid':None,            'desc':'Current controller status code, 0=good'},
    'ModelNumber':     {'addr':  1,'mode':'r', 'type':'uint', 'unit':None,            'valid':None,            'desc':'Model number of the Symbrosia Controller'},
    'SerialNumber':    {'addr':  2,'mode':'r', 'type':'uint', 'unit':None,            'valid':None,            'desc':'Serial number of the Symbrosia controller'},
    'FirmwareRev':     {'addr':  3,'mode':'r', 'type':'uint', 'unit':None,            'valid':None,            'desc':'Firmware version, major in upper byte, minor in lower byte'},
    'HeartbeatIn':     {'addr':  4,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Heartbeat, value written will be echoed in HeartbeatOut'},
    'HeartbeatOut':    {'addr':  5,'mode':'r', 'type':'uint', 'unit':None,            'valid':None,            'desc':'Heartbeat echo of value written to HeartbeatIn'},
    'StatusDisp1':     {'addr':  8,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Value to be shown on status screen position 1'},
    'StatusDisp2':     {'addr':  9,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Value to be shown on status screen position 2'},
    'TimeZone':        {'addr': 10,'mode':'rw','type':'int',  'unit':'h',             'valid':None,            'desc':'Controller timezone'},
    'Date':            {'addr': 11,'mode':'r', 'type':'date', 'unit':None,            'valid':None,            'desc':'Current controller date fromt NTP time'},
    'Time':            {'addr': 14,'mode':'r', 'type':'time', 'unit':None,            'valid':None,            'desc':'Current controller time from NTP time'},
    'DateTime':        {'addr': 11,'mode':'r', 'type':'dattm','unit':None,            'valid':None,            'desc':'Current controller date and time from NTP time'},
    'Year':            {'addr': 11,'mode':'r', 'type':'uint', 'unit':None,            'valid':None,            'desc':'Current Full year from NTP time'},
    'Month':           {'addr': 12,'mode':'r', 'type':'uint', 'unit':None,            'valid':None,            'desc':'Current month from NTP time, 0=January'},
    'Day':             {'addr': 13,'mode':'r', 'type':'uint', 'unit':None,            'valid':None,            'desc':'Current day from NTP time'},
    'Hour':            {'addr': 14,'mode':'r', 'type':'uint', 'unit':'h',             'valid':None,            'desc':'Current hour from NTP time'},
    'Minute':          {'addr': 15,'mode':'r', 'type':'uint', 'unit':'m',             'valid':None,            'desc':'Current minute from NTP time'},
    'Second':          {'addr': 16,'mode':'r', 'type':'uint', 'unit':'s',             'valid':None,            'desc':'Current second from NTP time'},
    'WQSensor':        {'addr': 20,'mode':'r', 'type':'float','unit':'WQSensorUnits', 'valid':'WQSensorValid', 'desc':'Calibrated reading of the water quality sensor'},
    'Temperature1':    {'addr': 22,'mode':'r', 'type':'float','unit':'Temp1Units',    'valid':'Temp1Valid',    'desc':'Calibrated reading from temperature sensor 1'},
    'Temperature2':    {'addr': 24,'mode':'r', 'type':'float','unit':'Temp2Units',    'valid':'Temp2Valid',    'desc':'Calibrated reading from temperature sensor 2'},
    'Analog1':         {'addr': 26,'mode':'r', 'type':'float','unit':'Analog1Units',  'valid':'Analog1Valid',  'desc':'Calibrated reading from analog input 1'},
    'Analog2':         {'addr': 28,'mode':'r', 'type':'float','unit':'Analog2Units',  'valid':'Analog2Valid',  'desc':'Calibrated reading from analog input 2'},
    'InternalTemp':    {'addr': 30,'mode':'r', 'type':'float','unit':'IntTempUnits',  'valid':'LocalTempValid','desc':'Controller internal temperature'},
    'SupplyVoltage':   {'addr': 32,'mode':'r', 'type':'float','unit':'SupVoltUnits',  'valid':'SupVoltValid',  'desc':'Controller supply voltage'},
    'ProcessedData':   {'addr': 34,'mode':'r', 'type':'float','unit':'ProcessedUnits','valid':'ProcReadValid', 'desc':'Result of data processing'},
    'WQSensorUnits':   {'addr': 36,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Units for the water quality sensor, 3=pH, 4=mV'},
    'Temp1Units':      {'addr': 37,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Units for temperature sensor 1, 1=°C or 2=°F'},
    'Temp2Units':      {'addr': 38,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Units for temperature sensor 2, 1=°C or 2=°F'},
    'Analog1Units':    {'addr': 39,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Units for analog input 1'},
    'Analog2Units':    {'addr': 40,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Units for analog input 2'},
    'IntTempUnits':    {'addr': 41,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Controller internal temperature units, 1=°C or 2=°F'},
    'SupVoltUnits':    {'addr': 42,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Controller supply voltage unit is volts'},
    'ProcessedUnits':  {'addr': 43,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Controller supply voltage unit is volts'},
    'pHTempComp':      {'addr': 44,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'pH temperature calibration source'},
    'WQOffset':        {'addr': 50,'mode':'rw','type':'float','unit':'WQSensorUnits', 'valid':None,            'desc':'Calibration offset for the WQ sensor amplifier'},
    'Temp1Offset':     {'addr': 52,'mode':'rw','type':'float','unit':'Temp1Units',    'valid':None,            'desc':'Calibration offset for temperature sensor 1'},
    'Temp2Offset':     {'addr': 54,'mode':'rw','type':'float','unit':'Temp2Units',    'valid':None,            'desc':'Calibration offset for temperature sensor 1'},
    'Analog1Offset':   {'addr': 56,'mode':'rw','type':'float','unit':'Analog1Units',  'valid':None,            'desc':'Calibration offset for analog input 1'},
    'Analog2Offset':   {'addr': 58,'mode':'rw','type':'float','unit':'Analog2Units',  'valid':None,            'desc':'Calibration offset for analog input 2'},
    'WQGain':          {'addr': 60,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Calibration gain for the WQ sensor amplifier'},
    'Temp1Gain':       {'addr': 62,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Calibration gain for temperature sensor 1'},
    'Temp2Gain':       {'addr': 64,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Calibration gain for temperature sensor 1'},
    'Analog1Gain':     {'addr': 66,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Calibration gain for analog input 1'},
    'Analog2Gain':     {'addr': 68,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Calibration gain for analog input 2'},
    'Ctrl1Input':      {'addr': 70,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 1 input source'},
    'Ctrl1Output':     {'addr': 71,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 1 output'},
    'Ctrl1Setpoint':   {'addr': 72,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 1 setpoint'},
    'Ctrl1Hysteresis': {'addr': 74,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 1 hysteresis'},
    'Ctrl1AlarmPtLow': {'addr': 76,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 1 alarm point low'},
    'Ctrl1AlarmPtHigh':{'addr': 78,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 1 alarm point high'},
    'Ctrl1EnbSource':  {'addr': 80,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 1 exernal enable source'},
    'Ctrl1MinOnTime':  {'addr': 81,'mode':'rw','type':'uint', 'unit':'s',             'valid':None,            'desc':'Control loop 1 minimum on time in seconds'},
    'Ctrl1Minimum':    {'addr': 82,'mode':'r', 'type':'float','unit':None,            'valid':None,            'desc':'Control loop 1 minimum value measured'},
    'Ctrl1Maximum':    {'addr': 84,'mode':'r', 'type':'float','unit':None,            'valid':None,            'desc':'Control loop 1 maximum value measured'},
    'Ctrl2Input':      {'addr': 86,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 2 input source'},
    'Ctrl2Output':     {'addr': 87,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 2 output'},
    'Ctrl2Setpoint':   {'addr': 88,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 2 setpoint'},
    'Ctrl2Hysteresis': {'addr': 90,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 2 hysteresis'},
    'Ctrl2AlarmPtLow': {'addr': 92,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 2 alarm point low'},
    'Ctrl2AlarmPtHigh':{'addr': 94,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 2 alarm point high'},
    'Ctrl2EnbSource':  {'addr': 96,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 2 exernal enable source'},
    'Ctrl2MinOnTime':  {'addr': 97,'mode':'rw','type':'uint', 'unit':'s',             'valid':None,            'desc':'Control loop 2 minimum on time in seconds'},
    'Ctrl2Minimum':    {'addr': 98,'mode':'r', 'type':'float','unit':None,            'valid':None,            'desc':'Control loop 2 minimum value measured'},
    'Ctrl2Maximum':    {'addr':100,'mode':'r', 'type':'float','unit':None,            'valid':None,            'desc':'Control loop 2 maximum value measured'},
    'Ctrl3Input':      {'addr':102,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 3 input source'},
    'Ctrl3Output':     {'addr':103,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 3 output'},
    'Ctrl3Setpoint':   {'addr':104,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 3 setpoint'},
    'Ctrl3Hysteresis': {'addr':106,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 3 hysteresis'},
    'Ctrl3AlarmPtLow': {'addr':108,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 3 alarm point low'},
    'Ctrl3AlarmPtHigh':{'addr':110,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 3 alarm point high'},
    'Ctrl3EnbSource':  {'addr':112,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 3 exernal enable source'},
    'Ctrl3MinOnTime':  {'addr':113,'mode':'rw','type':'uint', 'unit':'s',             'valid':None,            'desc':'Control loop 3 minimum on time in seconds'},
    'Ctrl3Minimum':    {'addr':114,'mode':'r', 'type':'float','unit':None,            'valid':None,            'desc':'Control loop 3 minimum value measured'},
    'Ctrl3Maximum':    {'addr':116,'mode':'r', 'type':'float','unit':None,            'valid':None,            'desc':'Control loop 3 maximum value measured'},
    'Ctrl4Input':      {'addr':118,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 4 input source'},
    'Ctrl4Output':     {'addr':119,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 4 output'},
    'Ctrl4Setpoint':   {'addr':120,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 4 setpoint'},
    'Ctrl4Hysteresis': {'addr':122,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 4 hysteresis'},
    'Ctrl4AlarmPtLow': {'addr':124,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 4 alarm point low'},
    'Ctrl4AlarmPtHigh':{'addr':126,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':'Control loop 4 alarm point high'},
    'Ctrl4EnbSource':  {'addr':128,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Control loop 4 exernal enable source'},
    'Ctrl4MinOnTime':  {'addr':129,'mode':'rw','type':'uint', 'unit':'s',             'valid':None,            'desc':'Control loop 4 minimum on time in seconds'},
    'Ctrl4Minimum':    {'addr':130,'mode':'r', 'type':'float','unit':None,            'valid':None,            'desc':'Control loop 4 minimum value measured'},
    'Ctrl4Maximum':    {'addr':132,'mode':'r', 'type':'float','unit':None,            'valid':None,            'desc':'Control loop 4 maximum value measured'},
    'LogicInA':        {'addr':136,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'LogicInB':        {'addr':137,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'LogicFunction':   {'addr':138,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'LogicOut':        {'addr':139,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'ToDStart':        {'addr':140,'mode':'r', 'type':'hour', 'unit':None,            'valid':None,            'desc':'Formatted ToD start time string'},
    'ToDStartHour':    {'addr':140,'mode':'rw','type':'uint', 'unit':'h',             'valid':None,            'desc':''},
    'ToDStartMin':     {'addr':141,'mode':'rw','type':'uint', 'unit':'m',             'valid':None,            'desc':''},
    'ToDStop':         {'addr':142,'mode':'r' ,'type':'hour', 'unit':None,            'valid':None,            'desc':'Formatted ToD stop time string'},
    'ToDStopHour':     {'addr':142,'mode':'rw','type':'uint', 'unit':'h',             'valid':None,            'desc':''},
    'ToDStopMin':      {'addr':143,'mode':'rw','type':'uint', 'unit':'m',             'valid':None,            'desc':''},
    'ToDOutput1':      {'addr':144,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Time of day output channel 1'},
    'ToDOutput2':      {'addr':145,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Time of day output channel 2'},
    'ToDOutput3':      {'addr':146,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Time of day output channel 3'},
    'ToDOutput4':      {'addr':147,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Time of day output channel 4'},
    'TimeLimCmdTime':  {'addr':148,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Time limited command duration'},
    'TimeLimCmdOut':   {'addr':149,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Time limited command output channel'},
    'CountSource':     {'addr':150,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Counter source channel'},
    'Counter':         {'addr':151,'mode':'r', 'type':'dint', 'unit':None,            'valid':None,            'desc':'Event counter'},
    'CountRstIntv':    {'addr':153,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Counter reset interval'},
    'TimerSource':     {'addr':154,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Timer source channel'},
    'Timer':           {'addr':155,'mode':'r', 'type':'dint', 'unit':'s',             'valid':None,            'desc':'Event counter in seconds'},
    'TimerRstIntv':    {'addr':157,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Timer reset interval'},
    'LogInterval':     {'addr':160,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'LogRecords':      {'addr':161,'mode':'r', 'type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'LogNumber':       {'addr':162,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'LogItem':         {'addr':163,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'LogData':         {'addr':164,'mode':'rw','type':'float','unit':None,            'valid':None,            'desc':''},
    'ProcessChanA':    {'addr':166,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'ProcessChanB':    {'addr':167,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':''},
    'ProcessID':       {'addr':168,'mode':'rw','type':'uint', 'unit':None,            'valid':None,            'desc':'Operation to perform on processed inputs'},
    'Status':          {'addr':  0,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Current controller status, True=good'},
    'NTPTimeValid':    {'addr':  1,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Status of last attempted NTP time synchonization'},
    'Startup':         {'addr':  2,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'True during controller startup, no controls active'},
    'SaveSettings':    {'addr':  3,'mode':'w', 'type':'bool', 'unit':None,            'valid':None,            'desc':'save settings to EEPROM'},
    'ClearSettings':   {'addr':  4,'mode':'w', 'type':'bool', 'unit':None,            'valid':None,            'desc':'set all settings to defaults'},
    'MidnightSave':    {'addr':  5,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Save settings each midnight'},
    'MidnightReset':   {'addr':  6,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Reset controller each midnight'},
    'SilenceAlarms':   {'addr':  7,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Silence alarms'},
    'DigitalIn1':      {'addr':  8,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'DigitalIn2':      {'addr':  9,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Relay1Status':    {'addr': 10,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Relay2Status':    {'addr': 11,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'DigitalOut1':     {'addr': 12,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'DigitalOut2':     {'addr': 13,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Relay1Request':   {'addr': 14,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Relay2Request':   {'addr': 15,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Dout1Request':    {'addr': 16,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Dout2Request':    {'addr': 17,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'VirtualIO1':      {'addr': 18,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'VirtualIO2':      {'addr': 19,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'WQSensorValid':   {'addr': 20,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Temp1Valid':      {'addr': 21,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Temp2Valid':      {'addr': 22,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Analog1Valid':    {'addr': 23,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Analog2Valid':    {'addr': 24,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'LocalTempValid':  {'addr': 25,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'SupVoltValid':    {'addr': 26,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'ProcReadValid':   {'addr': 27,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'LogicGateResult': {'addr': 28,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Flash':           {'addr': 29,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl1Enable':     {'addr': 30,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl2Enable':     {'addr': 31,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl3Enable':     {'addr': 32,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl4Enable':     {'addr': 33,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl1High':       {'addr': 34,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl2High':       {'addr': 35,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl3High':       {'addr': 36,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl4High':       {'addr': 37,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl1Active':     {'addr': 38,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl2Active':     {'addr': 39,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl3Active':     {'addr': 40,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'Ctrl4Active':     {'addr': 41,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'CtrlAlarm':       {'addr': 42,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop alarm'},
    'Ctrl1Alarm':      {'addr': 43,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 1 alarm'},
    'Ctrl2Alarm':      {'addr': 44,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 2 alarm'},
    'Ctrl3Alarm':      {'addr': 45,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 3 alarm'},
    'Ctrl4Alarm':      {'addr': 46,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 4 alarm'},
    'Ctrl1AlarmLow':   {'addr': 47,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 1 alarm low'},
    'Ctrl2AlarmLow':   {'addr': 48,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 2 alarm low'},
    'Ctrl3AlarmLow':   {'addr': 49,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 3 alarm low'},
    'Ctrl4AlarmLow':   {'addr': 50,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 4 alarm low'},
    'Ctrl1AlarmHigh':  {'addr': 51,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 1 alarm high'},
    'Ctrl2AlarmHigh':  {'addr': 52,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 2 alarm high'},
    'Ctrl3AlarmHigh':  {'addr': 53,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 3 alarm high'},
    'Ctrl4AlarmHigh':  {'addr': 54,'mode':'r', 'type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 4 alarm high'},
    'RstCtrl1Max':     {'addr': 55,'mode':'w', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'RstCtrl2Max':     {'addr': 56,'mode':'w', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'RstCtrl3Max':     {'addr': 57,'mode':'w', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'RstCtrl4Max':     {'addr': 58,'mode':'w', 'type':'bool', 'unit':None,            'valid':None,            'desc':''},
    'CounterEnable':   {'addr': 59,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Enable event counter'},
    'TimerEnable':     {'addr': 60,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Enable event timer'},
    'ToDEnable':       {'addr': 61,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Enable time of day function'},
    'ToDActive':       {'addr': 62,'mode':'r' ,'type':'bool', 'unit':None,            'valid':None,            'desc':'Time of day is active'},
    'ResetCounter':    {'addr': 63,'mode':'w' ,'type':'bool', 'unit':None,            'valid':None,            'desc':'Write True to reset event counter'},
    'ResetTimer':      {'addr': 64,'mode':'w' ,'type':'bool', 'unit':None,            'valid':None,            'desc':'Write True to reset event timer'},
    'ResetLogging':    {'addr': 65,'mode':'w' ,'type':'bool', 'unit':None,            'valid':None,            'desc':'Write True to reset internal logging'},
    'statCtrl1OneShot':{'addr': 66,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 1 one-shot mode'},
    'statCtrl2OneShot':{'addr': 67,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 2 one-shot mode'},
    'statCtrl3OneShot':{'addr': 68,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 3 one-shot mode'},
    'statCtrl4OneShot':{'addr': 69,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Control loop 4 one-shot mode'},
    'TimeLimitedCmd'  :{'addr': 70,'mode':'rw','type':'bool', 'unit':None,            'valid':None,            'desc':'Time limited command input'}}
  units= ['None','°C','°F','pH','mV','V','mA','A','mm','m','ml','l','g','kg','lbs','kPa','PSI','Hz','%','ppm','Ω','day','hr','min','sec','mol','mph','m/s','°','mmHg','mBar','kW','kVA']
  processes= ['Average','Minimum','Maximum','Sum','Difference','Priority']
  channels=   ['None','WQSensor','Temperature1','Temperature2','Analog1','Analog2',
               'InternalTemp','SupplyVoltage','ProcessedData',
               'DigitalIn1','DigitalIn2','Relay1Status','Relay2Status','DigitalOut1','DigitalOut2','VirtualIO1','VirtualIO2',
               'Ctrl1Active','Ctrl2Active','Ctrl3Active','Ctrl4Active',
               'CtrlAlarm','Ctrl1Alarm','Ctrl2Alarm','Ctrl3Alarm','Ctrl4Alarm',
               'Ctrl1AlarmLow','Ctrl2AlarmLow','Ctrl3AlarmLow','Ctrl4AlarmLow',
               'Ctrl1AlarmHigh','Ctrl2AlarmHigh','Ctrl3AlarmHigh','Ctrl4AlarmHigh',
               'Flasher','Day','Hour','Minute','Second','TofD']
  channelNames= ['None','WQ Amplifier','Temperature 1','Temperature 2','Analog 1','Analog 2',
               'Internal Temp','Supply Voltage','Processed',
               'Digital In 1','Digitial In 2','Relay 1','Relay 2','Digital Out 1','Digitial Out 2','Virtual IO 1','Virtual IO 2',
               'Control 1 Out','Control 2 Out','Control 3 Out','Control 4 Out',
               'Control Alarm','Control 1 Alarm','Control 2 Alarm','Control 3 Alarm','Control 4 Alarm',
               'Control 1 Alarm Low','Control 2 Alarm Low','Control 3 Alarm Low','Control 4 Alarm Low',
               'Control 1 Alarm High','Control 2 Alarm High','Control 3 Alarm High','Control 4 Alarm High',
               'Flasher','Days','Hours','Minutes','Seconds','Time of Day']
               
  #-- constants -----------------------------------------------------------------

  # symbrosia controller
  PORT      = 502 # SymbCtrl uses default modbusTCP port
  COIL_SIZE = 80  # number of SymbCtrl coil registers
  HOLD_SIZE = 300 # number of SymbCtrl holding regs
  DATA_EXP=   10  # expiration time for valid data in seconds

  # data valid codes
  DAT_VALID  = 1  # current data is valid
  DAT_INVALID= 0  # current data is expired

  # error codes
  ERR_NONE   = 0  # no current error
  ERR_COM    = 1  # unable to open controller session
  ERR_READ   = 2  # unable to read a register
  ERR_WRITE  = 3  # unable to write a register
  ERR_FULL   = 4  # write buffer full

  # command codes
  CMD_KILL   =-1  # terminate subprocess
  CMD_NONE   = 0  # no command pending
  CMD_COIL   = 1  # write coil registers
  CMD_HOLD   = 2  # write holding registers
  CMD_SCAN   = 3  # update scan time

  # shared array indices (see header comments)
  SHR_VALID  = 0  # valid data?  See code above
  SHR_CMD    = 1  # command to subprocess
  SHR_ERROR  = 2  # current error code, see code above
  SHR_IP1    = 3  # IP address of client device
  SHR_IP2    = 4
  SHR_IP3    = 5
  SHR_IP4    = 6
  SHR_ADDR   = 7  # register address for write
  SHR_COUNT  = 8  # number of bytes to write
  SHR_DATA   = 9  # register contents to write (up to eight bytes)
  SHR_COIL   = 17 # current coil register contents
  SHR_HOLD   = 17+COIL_SIZE  # current holding register contents
  SHR_SIZE   = 17+COIL_SIZE+HOLD_SIZE  # number of bytes in shared memory

  def __init__(self, master=None):
    self.ctrl=     None
    self.ipAddr=   ''
    self.name=     None
    self.error=    False
    self.message=  ''

  def start(self,ipAddr):
    # parse ip address
    try:
      ipaddress.ip_address(ipAddr)
    except ValueError:
      self.error= True
      self.message= 'Illegal IP address'
      self.ctrl= None
      self.name=  ''
      return False
    ipArr= ipAddr.split(".")
    # check for open controller
    if (self.ctrl!=None):
      self.error= True
      self.message= 'Controller already open'
      self.ctrl= None
      self.name=  ''
      return False
    # make and load shared array
    self.shared= Array('i',self.SHR_SIZE)
    self.shared[self.SHR_CMD]=   0
    self.shared[self.SHR_ERROR]= 0
    for i in range(4):
      self.shared[i+self.SHR_IP1]= int(ipArr[i])
    # spawn the process
    print('  Starting subprocess for {}'.format(ipAddr))
    self.ctrl= Process(target=self.scanSub,args=(self.shared,))
    self.ctrl.start()
    # start status
    self.error= False
    self.message= 'No error'
    return True

  def scanInterval(time):
    if self.ctrl==None:
      self.error= True
      self.message= 'Controller is not open'
      return False
    if not isinstance(value,int):
      self.error= True
      self.message= 'Illegal parameter type for scan time'
      return False
    if time<1 or time>60:
      self.error= True
      self.message= 'Illegal value for scan time'
      return False
    self.shared[self.SHR_DATA]= time
    self.shared[self.SHR_CMD]=  self.CMD_SCAN
    self.error= False
    self.message= 'No error'
    return True

  def valid(self):
    if self.ctrl!=None:
      return self.shared[self.SHR_VALID]==self.DAT_VALID;
    return False
    
  def close(self):
    print('  Terminating controller subprocess..')
    if self.ctrl!=None:
      self.shared[self.SHR_CMD]= self.CMD_KILL
      self.ctrl.join()
      self.error= False
      self.message= 'No Error'
      self.ctrl= None
      self.name=  ''
      print('  Subprocesses terminated!')
      return True
    else:
      self.error= True
      self.message= 'No open controller'
      self.name=  ''
      return False
      
  def scanSub(self,shared):
    ipAddr= '{}.{}.{}.{}'.format(shared[self.SHR_IP1],shared[self.SHR_IP2],shared[self.SHR_IP3],shared[self.SHR_IP4])
    writeBuffer= []
    # create a Modbus client object
    device= ModbusClient(debug=False,timeout=5)
    device.host(ipAddr)
    device.port(self.PORT)
    # initialize vars
    scanTime= 1
    shared[self.SHR_VALID]= self.DAT_INVALID
    shared[self.SHR_ERROR]= self.ERR_COM
    scan= dt.datetime.now()-dt.timedelta(seconds=scanTime+1)
    last= dt.datetime.now()-dt.timedelta(seconds=self.DATA_EXP+1)
    idle= dt.datetime.now()
    # scanning loop
    while True:
      now= dt.datetime.now()
      # swallow poison pill and die
      if shared[self.SHR_CMD]==self.CMD_KILL: 
        print('    Scanner for {:15s} terminated!'.format(ipAddr))
        break
      # check for write command and move to queue
      if shared[self.SHR_CMD]==self.CMD_COIL or shared[self.SHR_CMD]==self.CMD_HOLD:
        if len(writeBuffer)>100: shared[self.SHR_ERROR]= self.ERR_FULL
        else:
          wCmd= {'cmd':shared[self.SHR_CMD],'addr':shared[self.SHR_ADDR],'size':shared[self.SHR_COUNT],'data':[]}
          for i in range(shared[self.SHR_COUNT]): wCmd['data'].append(shared[self.SHR_DATA+i])
          shared[self.SHR_CMD]= self.CMD_NONE
          writeBuffer.append(wCmd)
          continue
      # process write buffer
      if len(writeBuffer)>0:
        if debugSub: print('    Buffered commands {}'.format(len(writeBuffer)))
        wCmd= writeBuffer[0]
        # check for write coil command
        if wCmd['cmd']==self.CMD_COIL:
          if debugSub: print('  Write coil...')
          if device.open():
            val= wCmd['data'][0]==1
            if device.write_single_coil(wCmd['addr'],val):
              writeBuffer.remove(wCmd)
            else:
              shared[self.SHR_ERROR]= self.ERR_WRITE
              if debugSub: print('    Write error!')
            device.close()
            if debugSub: print('    Coil {:d} written with {}'.format(wCmd['addr'],val))
          else:
            shared[self.SHR_ERROR]= self.ERR_WRITE
            if debugSub: print('    Write error!')
        # check for write hold command
        if wCmd['cmd']==self.CMD_HOLD:
          if debugSub: print('  Write holding reg...')
          if device.open():
            if device.write_multiple_registers(wCmd['addr'],wCmd['data']):
              writeBuffer.remove(wCmd)
            else:
              shared[self.SHR_ERROR]= self.ERR_WRITE
              if debugSub: print('    Write error!')
            device.close()
            if debugSub: print('    {} holding regs written at {:d}'.format(wCmd['size'],wCmd['addr']))
          else:
            shared[self.SHR_ERROR]= self.ERR_WRITE
            if debugSub: print('    Write error!')
        idle= now
        continue
      # set scantime
      if shared[self.SHR_CMD]==self.CMD_SCAN: 
        shared[self.SHR_CMD]= self.CMD_NONE
        if debugSub: print('  Set scan time to {:d}'.format(shared[self.SHR_DATA]))
        if shared[self.SHR_DATA]>=1 and shared[self.SHR_DATA]<=60:
          scanTime= shared[self.SHR_DATA]
        else:
          shared[self.SHR_ERROR]= self.ERR_WRITE
          if debugSub: print('    Bad value for scan time!')
        idle= now
      # low power idle if no activity besides regular scan
      if now-idle>dt.timedelta(seconds=1):
        time.sleep(0.01)
      # check last valid data
      if (now-last)<dt.timedelta(seconds=self.DATA_EXP):
        shared[self.SHR_VALID]= self.DAT_VALID
      else:
        shared[self.SHR_VALID]= self.DAT_INVALID
      # scan if time elapsed
      if (now-scan)>dt.timedelta(seconds=scanTime):
        scan= now
        error= self.ERR_NONE
        if debugSub: print('Scanning controller {}...'.format(ipAddr))
        # get new data from controller
        if device.open():
          # coils
          if debugSub: print('  Read coils')
          values= device.read_coils(0,self.COIL_SIZE)
          if values!=None: # place data in shared
            for i,val in enumerate(values):
              if val:
                shared[self.SHR_COIL+i]= 1
              else:
                shared[self.SHR_COIL+i]= 0
          else:
            if debugSub: print('    Read error!')
            error= self.ERR_READ #set read failed error flag
          # holding registers
          if debugSub: print('  Read holding regs')
          values= []
          for pos in range(0,self.HOLD_SIZE,100): # get data in blocks of 100
            if pos+100>self.HOLD_SIZE:
              count= self.HOLD_SIZE-pos+1
            else:
              count= 100
            if debugSub: print('    Read holding regs {:3d} to {:3d}'.format(pos,pos+count-1))
            val= device.read_holding_registers(pos,count)
            if val==None:
              values= None
              break
            values= values+val
          # place in shared array
          if values!=None:
            for i,val in enumerate(values):
              shared[self.SHR_HOLD+i]= val
          else:
            goodData= False
            if debugScan: print('    Read error!')
            error= self.ERR_READ #set read failed error flag
          device.close()
        else:
          if debugScan: print('  Com error!')
          error= self.ERR_COM #set com error flag
        # handle errors
        shared[self.SHR_ERROR]= error
        if error==self.ERR_NONE: # keep data valid flag set if com good
          shared[self.SHR_VALID]= self.DAT_VALID
          last= now
          if debugSub: print('  Good scan!')

#-- controller information ----------------------------------------------------
  def name(self):
    if self.ctrl!=None:
      name= self.read('ControlName')
      if name!=None: return name
    else: return ''

  def connected(self):
    if self.ctrl!=None: 
      if self.shared[self.SHR_ERROR]==self.ERR_NONE: return True
    return False

  def status(self):
    if self.ctrl!=None: 
      stat= self.read('Status')
      if self.shared[self.SHR_ERROR]==self.ERR_NONE:
        if stat: return True
    return False

  def registers(self):
    return self.ctrlRegs.keys()

  def address(self,reg):
    if reg in self.ctrlRegs:
      self.error= False
      self.message= 'No error'
      return self.ctrlRegs[reg]['addr']
    self.error= True
    self.message= 'Bad register name {}'.format(reg)
    return None

  def type(self,reg):
    if reg in self.ctrlRegs:
      self.error= False
      self.message= 'No error'
      return self.ctrlRegs[reg]['type']
    self.error= True
    self.message= 'Bad register name {}'.format(reg)
    return None
    
  def mode(self,reg):
    if reg in self.ctrlRegs:
      self.error= False
      self.message= 'No error'
      return self.ctrlRegs[reg]['mode']
    self.error= True
    self.message= 'Bad register name{}'.format(reg)
    return None

  def description(self,reg):
    if reg in self.ctrlRegs:
      self.error= False
      self.message= 'No error'
      return self.ctrlRegs[reg]['desc']
    self.error= True
    self.message= 'Bad register name.'.format(reg)
    return None

  def unit(self,unitID):
    if unitID==0 : return ''
    if unitID in range(len(self.units)):
      return self.units[unitID]
    return None

  def unitList(self):
    return self.units

  def channelUnit(self,chan):
    if chan in self.ctrlRegs:
      if self.ctrlRegs[chan]['unit']!=None:
        if self.ctrlRegs[chan]['unit'] not in self.ctrlRegs: return self.ctrlRegs[chan]['unit']
        unit= self.read(self.ctrlRegs[chan]['unit'])
        if not self.error:
          if unit in range(len(self.units)):
            if self.units[unit]!='None': return self.units[unit]
    return ''

  def channelList(self):
    return self.channels

  def channel(self,chan):
    if chan in range(len(self.channels)):
      return self.channels[chan]
    return None

#-- read and write controller data --------------------------------------------
  def read(self,reg):
    if self.ctrl==None:
      self.error= True
      self.message= 'Controller is not open'
      return None
    if reg not in self.ctrlRegs:
      self.error= True
      self.message= 'Bad register name {}'.format(reg)
      return None
    if self.ctrlRegs[reg]['mode']=='w':
      self.error= True
      self.message= 'Register {} not readable'.format(reg)
      return None
    if not self.shared[self.SHR_VALID]==self.DAT_VALID:
      self.error= True
      self.message= 'No recent data from controller'
      return None
    addr= self.ctrlRegs[reg]['addr']
    typ=  self.ctrlRegs[reg]['type']
    self.error= False
    self.message= 'No error'
    if typ=='float':
      val= [self.shared[self.SHR_HOLD+addr],self.shared[self.SHR_HOLD+addr+1]]
      val= utils.word_list_to_long(val,big_endian=False)
      val= utils.decode_ieee(val[0])
      return val
    if typ=='uint':
      return self.shared[self.SHR_HOLD+addr]
    if typ=='int':
      val= self.shared[self.SHR_HOLD+addr]
      if (val>>15) & 1: val= val-65536
      return val
    if typ=='dint':
      return self.shared[self.SHR_HOLD+addr]+self.shared[self.SHR_HOLD+addr+1]*65536
    if typ=='bool':
      return self.shared[self.SHR_COIL+addr]==1
    if typ=='str':
      st= ''
      for c in range(8):
        chs= self.shared[self.SHR_HOLD+addr+c]
        ch= chs>>8
        if ch==0: return st
        st= st+chr(ch)
        ch= chs&0xFF
        if ch==0: return st
        st= st+chr(ch)
      return st
    if typ=='dattm':
      m= self.shared[self.SHR_HOLD+addr+1]
      if m<0 or m>11: m= 0
      month= ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m]
      return '{:02d}{}{:02d} {:02d}:{:02d}:{:02d}'.format(self.shared[self.SHR_HOLD+addr+2],month,self.shared[self.SHR_HOLD+addr],self.shared[self.SHR_HOLD+addr+3],self.shared[self.SHR_HOLD+addr+4],self.shared[self.SHR_HOLD+addr+5])
    if typ=='date':
      m= self.shared[self.SHR_HOLD+addr+1]
      if m<0 or m>11: m= 0
      month= ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m]
      return '{:02d}{}{:02d}'.format(self.shared[self.SHR_HOLD+addr+2],month,self.shared[self.SHR_HOLD+addr])
    if typ=='time':
      return '{:02d}:{:02d}:{:02d}'.format(self.shared[self.SHR_HOLD+addr],self.shared[self.SHR_HOLD+addr+1],self.shared[self.SHR_HOLD+addr+2])
    if typ=='hour':
      return '{:02d}:{:02d}'.format(self.shared[self.SHR_HOLD+addr],self.shared[self.SHR_HOLD+addr+1])
    # if no implemented type
    self.error= True
    self.message= 'No such type {}'.format(typ)
    return None

  def write(self,reg,value):
    if not reg in self.ctrlRegs:
      self.error= True
      self.message= 'Bad register name {}'.format(reg)
      return False
    if self.ctrlRegs[reg]['mode']=='r':
      self.error= True
      self.message= 'Register {} not writable'.format(reg)
      return False
    for w in range(50):
      if self.shared[self.SHR_CMD]!=self.CMD_NONE: time.sleep(0.01)
    if self.shared[self.SHR_CMD]!=self.CMD_NONE:
      self.error= True
      self.message= 'Controller write queue busy'
      return False
    typ=  self.ctrlRegs[reg]['type']
    addr= self.ctrlRegs[reg]['addr']
    if typ=='bool':
      if not isinstance(value,bool):
        self.error= True
        self.message= 'Value not boolean for {}'.format(reg)
        return False
      self.shared[self.SHR_ADDR]=  addr
      self.shared[self.SHR_COUNT]= 1
      if value: self.shared[self.SHR_DATA]=  1
      else:     self.shared[self.SHR_DATA]=  0
      self.shared[self.SHR_CMD]= self.CMD_COIL
      # write into shared data to show immediate change
      if value: self.shared[self.SHR_COIL+addr]=  1
      else:     self.shared[self.SHR_COIL+addr]=  0
      self.error= False
      self.message= 'No error'
      return True
    if typ=='int':
      if not isinstance(value,int):
        self.error= True
        self.message= 'Value not integer for {}'.format(reg)
        return False
      if value<-32768 or value>32767:
        self.error= True
        self.message= 'Value {:d} out of range for 16bit integer'.format(value)
        return False
      if (value & (1<<15))!=0: value= (value-(1<<16)) & 65535 #convert to two's complement
      self.shared[self.SHR_ADDR]=  addr
      self.shared[self.SHR_COUNT]= 1
      self.shared[self.SHR_DATA]=  value
      self.shared[self.SHR_CMD]=   self.CMD_HOLD
      self.error= False
      self.message= 'No error'
      return True
    if typ=='uint':
      if not isinstance(value,int):
        self.error= True
        self.message= 'Value not integer for {}'.format(reg)
        return False
      if value<0 or value>65535:
        self.error= True
        self.message= 'Value {:d} out of range for unsigned integer'.format(value)
        return False
      self.shared[self.SHR_ADDR]=  addr
      self.shared[self.SHR_COUNT]= 1
      self.shared[self.SHR_DATA]=  value
      self.shared[self.SHR_CMD]=   self.CMD_HOLD
      self.error= False
      self.message= 'No error'
      return True
    if typ=='dint':
      if not isinstance(value,int):
        self.error= True
        self.message= 'Value not integer for {}'.format(reg)
        return False
      if value<0 or value>4294967295:
        self.error= True
        self.message= 'Value {:d} out of range for 32bit integer'.format(value)
        return False
      self.shared[self.SHR_ADDR]=   addr
      self.shared[self.SHR_COUNT]=  2
      self.shared[self.SHR_DATA]=  (value>>16)&0xffff
      self.shared[self.SHR_DATA+1]= value&0xffff
      self.shared[self.SHR_CMD]=    self.CMD_HOLD
      self.error= False
      self.message= 'No error'
      return True
    if typ=='float':
      if not (isinstance(value,(float,int))):
        self.error= True
        self.message= 'Value not float for {}'.format(reg)
        return False
      vals= utils.long_list_to_word([utils.encode_ieee(value)],big_endian=False)
      self.shared[self.SHR_ADDR]=    addr
      self.shared[self.SHR_COUNT]=   2
      self.shared[self.SHR_DATA]=    vals[0]
      self.shared[self.SHR_DATA+1]=  vals[1]
      self.shared[self.SHR_CMD]=     self.CMD_HOLD
      self.error= False
      self.message= 'No error'
      return True
    if typ=='str':
      if not isinstance(value,str):
        self.error= True
        self.message= 'Value not str for {}'.format(reg)
        return False
      self.shared[self.SHR_ADDR]=  addr
      self.shared[self.SHR_COUNT]= 8
      for pos in range(8):
        word= 0
        if pos*2<len(value):   word= ord(value[pos*2])*256
        if pos*2+1<len(value): word= word+ord(value[pos*2+1])
        self.shared[self.SHR_DATA+pos]= word
      self.shared[self.SHR_CMD]= self.CMD_HOLD
      self.error= False
      self.message= 'No error'
      return True
    self.error= True
    self.message= 'Unknown type for writing'
    return False

  def textValue(self,chan,size,unit):
    if size<8: size= 8
    if unit: width= size-4
    else:    width= size
    vStr= '{val:{width}s}'.format(width=width,val='Chan!')
    # get value
    if chan in self.ctrlRegs:
      value= self.read(chan)
      if self.error:
        vStr= '{val:>{width}s}'.format(width=width,val='Err!')
      else:
        if self.ctrlRegs[chan]['type']=='float':
          vStr= '{val:>{width}.2f}'.format(width=width,val=value)
        if self.ctrlRegs[chan]['type']=='int':
          vStr= '{val:>{width}d}'.format(width=width,val=value)
        if self.ctrlRegs[chan]['type']=='uint':
          vStr= '{val:>{width}d}'.format(width=width,val=value)
        if self.ctrlRegs[chan]['type']=='dint':
          vStr= '{val:>{width}d}'.format(width=width,val=value)
        if self.ctrlRegs[chan]['type']=='bool':
          if 'Alarm' in chan:
            if value: vStr= '{val:>{width}s}'.format(width=width,val='Alarm')
            else:     vStr= '{val:>{width}s}'.format(width=width,val='No Alarm')
          else:
            if value: vStr= '{val:>{width}s}'.format(width=width,val='On')
            else:     vStr= '{val:>{width}s}'.format(width=width,val='Off')
        if self.ctrlRegs[chan]['type'] in ['str','dattm','date','time','hour']:
          vStr= '{val:{width}s}'.format(width=width,val=value)
      # return result
      if unit: return '{}{:<4s}'.format(vStr,self.channelUnit(chan))
    return vStr

  def convert(self,reg,value):
    if reg in self.ctrlRegs:
      type= self.ctrlRegs[reg]['type']
      if type=='str':
        if value==None: return ''
        return str(value)
      if type=='int':
        try: cval= int(value)
        except: return None
        return cval
      if type=='uint':
        try: cval= int(value)
        except: return None
        return cval
      if type=='dint':
        try: cval= int(value)
        except: return None
        return cval
      if type=='float':
        try: cval= float(value)
        except: return None
        return cval
      if type=='bool':
        if isinstance(value,bool):
          return value
        if value=='True':
          return True
        else:
          return False
    return None
    
#-- end SymbCtrlScan ----------------------------------------------------------
