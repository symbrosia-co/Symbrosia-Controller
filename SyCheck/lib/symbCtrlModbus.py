#------------------------------------------------------------------------------
#  SymbCtrl ModBus
#
#  - A utility wrapper for acces to the SymbCtrl using pyModBusTCP
#  - written for Python v3.9
#  - uses the ModbusTCP library pyModbusTCP version 0.1.10 or later maintained
#  by user sourceperl under an MIT open source license, documentation at
#  https://github.com/sourceperl/pyModbusTCP
#  - pyModbusTCP must be installed prior to use, use 'pip install pyModbusTCP'
#
#
#  Notes:
#  - Modbus operations are handled by opening the connection, performing the
#  requested operation, then immediately closing the connection, connections
#  are not left open
#  - The error result and message may be queried through calls after completion
#  of the operation to determine success or failure
#
# 12May2022 v0.1 A. Cooper
#  - initial version
# 20Mar2024 v1.0 A. Cooper
# - expanded channels to add alarm states for each control loop and overall
# 30Jul2024 v1.1 A. Cooper
#  - modified to support new features in SymbCtrl 2.6
#  - implemented external enable
#  - implemented minimum time on/off
#  - added one-shot registers
#  - added TofD to channel list
# 24Oct2024 v1.2 A. Cooper
#  - added getRegs to return a full register/value dictionary
# 24Oct2024 v1.3 A. Cooper
#  - Edited register table to complete a lot of descriptions
#  - Added getRegs to provide the whole register table in array form
#
#------------------------------------------------------------------------------
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import datetime as dt

#------------------------------------------------------------------------------
#  SymbCtrl Class
#
#  - class for access to the SymbCtrl
#
#------------------------------------------------------------------------------
class SymbCtrl():
  ctrl=       None     # controller Modbus client object
  ctrlName=   None     # controller name read from controller
  open=       False    # controller communication established
  valid=      False    # fresh data in buffer
  dataTime=   None     # time of last data service
  comTime=    None     # time of last communication with controller
  lastError=  False    # error status of last call
  lastMessage=''       # text description of last call result
  ipAddr=     ''       # ModbusTCP IP address
  port=       502      # Modbus port, SymbCtrl uses the default 508
  holdBase=   0        # first Modbus holding register address
  holdSize=   300      # number of holding registers implemented in SymbCtrl
  coilBase=   0        # first Modbus coil register address
  coilSize=   70       # number of coil registers implemented in SymbCtrl
  timeout=    5        # Modbus timeout in seconds
  validTime=  60       # maximum age for valid data in buffer
  ctrlRegs= {          # mapping of all implemented Modbus registers in the SymbCtrl
    'ModelName':       {'addr':170,'mode':'r', 'type':'str',  'value':''   ,'desc':'Controller model name'},
    'ControlName':     {'addr':178,'mode':'rw','type':'str',  'value':''   ,'desc':'User assigned controller name'},
    'WQName':          {'addr':186,'mode':'rw','type':'str',  'value':''   ,'desc':'Water quality sensor description'},
    'Temp1Name':       {'addr':194,'mode':'rw','type':'str',  'value':''   ,'desc':'Temperature sensor 1 description'},
    'Temp2Name':       {'addr':202,'mode':'rw','type':'str',  'value':''   ,'desc':'Temperature sensor 2 description'},
    'Input1Name':      {'addr':210,'mode':'rw','type':'str',  'value':''   ,'desc':'Input 1 description'},
    'Input2Name':      {'addr':218,'mode':'rw','type':'str',  'value':''   ,'desc':'Input 2 description'},
    'Relay1Name':      {'addr':226,'mode':'rw','type':'str',  'value':''   ,'desc':'Relay 1 description'},
    'Relay2Name':      {'addr':234,'mode':'rw','type':'str',  'value':''   ,'desc':'Relay 2 description'},
    'Output1Name':     {'addr':242,'mode':'rw','type':'str',  'value':''   ,'desc':'Digital output 1 description'},
    'Output2Name':     {'addr':250,'mode':'rw','type':'str',  'value':''   ,'desc':'Digital output 2 description'},
    'Control1Name':    {'addr':258,'mode':'rw','type':'str',  'value':''   ,'desc':'Description of control loop 1'},
    'Control2Name':    {'addr':266,'mode':'rw','type':'str',  'value':''   ,'desc':'Description of control loop 2'},
    'Control3Name':    {'addr':274,'mode':'rw','type':'str',  'value':''   ,'desc':'Description of control loop 3'},
    'Control4Name':    {'addr':282,'mode':'rw','type':'str',  'value':''   ,'desc':'Description of control loop 4'},
    'StatusCode':      {'addr':  0,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Current controller status code, 0=good'},
    'ModelNumber':     {'addr':  1,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Model number of the Symbrosia Controller'},
    'SerialNumber':    {'addr':  2,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Serial number of the Symbrosia controller'},
    'FirmwareRev':     {'addr':  3,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Firmware version, major in upper byte, minor in lower byte'},
    'HeartbeatIn':     {'addr':  4,'mode':'rw','type':'uint', 'value':0    ,'desc':'Heartbeat, value written will be echoed in HeartbeatOut'},
    'HeartbeatOut':    {'addr':  5,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Heartbeat echo of value written to HeartbeatIn'},
    'StatusDisp1':     {'addr':  8,'mode':'rw','type':'uint', 'value':0    ,'desc':'Value to be shown on status screen position 1'},
    'StatusDisp2':     {'addr':  9,'mode':'rw','type':'uint', 'value':0    ,'desc':'Value to be shown on status screen position 2'},
    'TimeZone':        {'addr': 10,'mode':'rw','type':'int',  'value':0    ,'desc':'Controller timezone'},
    'Year':            {'addr': 11,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Current Full year from NTP time'},
    'Month':           {'addr': 12,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Current month from NTP time, 0=January'},
    'Day':             {'addr': 13,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Current day from NTP time'},
    'Hour':            {'addr': 14,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Current hour from NTP time'},
    'Minute':          {'addr': 15,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Current minute from NTP time'},
    'Second':          {'addr': 16,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Current second from NTP time'},
    'Time':            {'addr': 14,'mode':'r', 'type':'time', 'value':0    ,'desc':'Formatted time string'},
    'WQSensor':        {'addr': 20,'mode':'r', 'type':'float','value':0    ,'desc':'Calibrated reading of the water quality sensor'},
    'Temperature1':    {'addr': 22,'mode':'r', 'type':'float','value':0    ,'desc':'Calibrated reading from temperature sensor 1'},
    'Temperature2':    {'addr': 24,'mode':'r', 'type':'float','value':0    ,'desc':'Calibrated reading from temperature sensor 2'},
    'Analog1':         {'addr': 26,'mode':'r', 'type':'float','value':0    ,'desc':'Calibrated reading from analog input 1'},
    'Analog2':         {'addr': 28,'mode':'r', 'type':'float','value':0    ,'desc':'Calibrated reading from analog input 2'},
    'InternalTemp':    {'addr': 30,'mode':'r', 'type':'float','value':0    ,'desc':'Controller internal temperature'},
    'SupplyVoltage':   {'addr': 32,'mode':'r', 'type':'float','value':0    ,'desc':'Controller supply voltage'},
    'ProcessedData':   {'addr': 34,'mode':'r', 'type':'float','value':0    ,'desc':'Result of data processing'},
    'WQSensorUnits':   {'addr': 36,'mode':'rw','type':'uint', 'value':0    ,'desc':'Units for the water quality sensor, 3=pH, 4=mV'},
    'Temp1Units':      {'addr': 37,'mode':'rw','type':'uint', 'value':0    ,'desc':'Units for temperature sensor 1, 1=°C or 2=°F'},
    'Temp2Units':      {'addr': 38,'mode':'rw','type':'uint', 'value':0    ,'desc':'Units for temperature sensor 2, 1=°C or 2=°F'},
    'Analog1Units':    {'addr': 39,'mode':'rw','type':'uint', 'value':0    ,'desc':'Units for analog input 1'},
    'Analog2Units':    {'addr': 40,'mode':'rw','type':'uint', 'value':0    ,'desc':'Units for analog input 2'},
    'IntTempUnits':    {'addr': 41,'mode':'rw','type':'uint', 'value':0    ,'desc':'Controller internal temperature units, 1=°C or 2=°F'},
    'SupVoltUnits':    {'addr': 42,'mode':'rw','type':'uint', 'value':0    ,'desc':'Controller supply voltage unit is volts'},
    'pHTempComp':      {'addr': 44,'mode':'rw','type':'uint', 'value':0    ,'desc':'pH temperature calibration source'},
    'WQOffset':        {'addr': 50,'mode':'rw','type':'float','value':0    ,'desc':'Calibration offset for the WQ sensor amplifier'},
    'Temp1Offset':     {'addr': 52,'mode':'rw','type':'float','value':0    ,'desc':'Calibration offset for temperature sensor 1'},
    'Temp2Offset':     {'addr': 54,'mode':'rw','type':'float','value':0    ,'desc':'Calibration offset for temperature sensor 1'},
    'Analog1Offset':   {'addr': 56,'mode':'rw','type':'float','value':0    ,'desc':'Calibration offset for analog input 1'},
    'Analog2Offset':   {'addr': 58,'mode':'rw','type':'float','value':0    ,'desc':'Calibration offset for analog input 2'},
    'WQGain':          {'addr': 60,'mode':'rw','type':'float','value':0    ,'desc':'Calibration gain for the WQ sensor amplifier'},
    'Temp1Gain':       {'addr': 62,'mode':'rw','type':'float','value':0    ,'desc':'Calibration gain for temperature sensor 1'},
    'Temp2Gain':       {'addr': 64,'mode':'rw','type':'float','value':0    ,'desc':'Calibration gain for temperature sensor 1'},
    'Analog1Gain':     {'addr': 66,'mode':'rw','type':'float','value':0    ,'desc':'Calibration gain for analog input 1'},
    'Analog2Gain':     {'addr': 68,'mode':'rw','type':'float','value':0    ,'desc':'Calibration gain for analog input 2'},
    'Ctrl1Input':      {'addr': 70,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 1 input source'},
    'Ctrl1Output':     {'addr': 71,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 1 output'},
    'Ctrl1Setpoint':   {'addr': 72,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 1 setpoint'},
    'Ctrl1Hysteresis': {'addr': 74,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 1 hysteresis'},
    'Ctrl1AlarmPtLow': {'addr': 76,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 1 alarm point low'},
    'Ctrl1AlarmPtHigh':{'addr': 78,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 1 alarm point high'},
    'Ctrl1EnbSource':  {'addr': 80,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 1 exernal enable source'},
    'Ctrl1MinOnTime':  {'addr': 81,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 1 minimum on time in seconds'},
    'Ctrl1Minimum':    {'addr': 82,'mode':'r', 'type':'float','value':0    ,'desc':'Control loop 1 minimum value measured'},
    'Ctrl1Maximum':    {'addr': 84,'mode':'r', 'type':'float','value':0    ,'desc':'Control loop 1 maximum value measured'},
    'Ctrl2Input':      {'addr': 86,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 2 input source'},
    'Ctrl2Output':     {'addr': 87,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 2 output'},
    'Ctrl2Setpoint':   {'addr': 88,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 2 setpoint'},
    'Ctrl2Hysteresis': {'addr': 90,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 2 hysteresis'},
    'Ctrl2AlarmPtLow': {'addr': 92,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 2 alarm point low'},
    'Ctrl2AlarmPtHigh':{'addr': 94,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 2 alarm point high'},
    'Ctrl2EnbSource':  {'addr': 96,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 2 exernal enable source'},
    'Ctrl2MinOnTime':  {'addr': 97,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 2 minimum on time in seconds'},
    'Ctrl2Minimum':    {'addr': 98,'mode':'r', 'type':'float','value':0    ,'desc':'Control loop 2 minimum value measured'},
    'Ctrl2Maximum':    {'addr':100,'mode':'r', 'type':'float','value':0    ,'desc':'Control loop 2 maximum value measured'},
    'Ctrl3Input':      {'addr':102,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 3 input source'},
    'Ctrl3Output':     {'addr':103,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 3 output'},
    'Ctrl3Setpoint':   {'addr':104,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 3 setpoint'},
    'Ctrl3Hysteresis': {'addr':106,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 3 hysteresis'},
    'Ctrl3AlarmPtLow': {'addr':108,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 3 alarm point low'},
    'Ctrl3AlarmPtHigh':{'addr':110,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 3 alarm point high'},
    'Ctrl3EnbSource':  {'addr':112,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 3 exernal enable source'},
    'Ctrl3MinOnTime':  {'addr':113,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 3 minimum on time in seconds'},
    'Ctrl3Minimum':    {'addr':114,'mode':'r', 'type':'float','value':0    ,'desc':'Control loop 3 minimum value measured'},
    'Ctrl3Maximum':    {'addr':116,'mode':'r', 'type':'float','value':0    ,'desc':'Control loop 3 maximum value measured'},
    'Ctrl4Input':      {'addr':118,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 4 input source'},
    'Ctrl4Output':     {'addr':119,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 4 output'},
    'Ctrl4Setpoint':   {'addr':120,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 4 setpoint'},
    'Ctrl4Hysteresis': {'addr':122,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 4 hysteresis'},
    'Ctrl4AlarmPtLow': {'addr':124,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 4 alarm point low'},
    'Ctrl4AlarmPtHigh':{'addr':126,'mode':'rw','type':'float','value':0    ,'desc':'Control loop 4 alarm point high'},
    'Ctrl4EnbSource':  {'addr':128,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 4 exernal enable source'},
    'Ctrl4MinOnTime':  {'addr':129,'mode':'rw','type':'uint', 'value':0    ,'desc':'Control loop 4 minimum on time in seconds'},
    'Ctrl4Minimum':    {'addr':130,'mode':'r', 'type':'float','value':0    ,'desc':'Control loop 4 minimum value measured'},
    'Ctrl4Maximum':    {'addr':132,'mode':'r', 'type':'float','value':0    ,'desc':'Control loop 4 maximum value measured'},
    'LogicInA':        {'addr':136,'mode':'rw','type':'uint', 'value':0    ,'desc':'Logic function input A'},
    'LogicInB':        {'addr':137,'mode':'rw','type':'uint', 'value':0    ,'desc':'Logic function input B'},
    'LogicFunction':   {'addr':138,'mode':'rw','type':'uint', 'value':0    ,'desc':'Logic function to be applied'},
    'LogicOut':        {'addr':139,'mode':'r', 'type':'uint', 'value':0    ,'desc':'Logic function result output'},
    'ToDStart':        {'addr':140,'mode':'r', 'type':'hour', 'value':0    ,'desc':'Formatted ToD start time string'},
    'ToDStartHour':    {'addr':140,'mode':'rw','type':'uint', 'value':0    ,'desc':'Hour to start Time if Day operation'},
    'ToDStartMin':     {'addr':141,'mode':'rw','type':'uint', 'value':0    ,'desc':'Minute to start Time if Day operation'},
    'ToDStop':         {'addr':142,'mode':'r' ,'type':'hour', 'value':0    ,'desc':'Formatted ToD stop time string'},
    'ToDStopHour':     {'addr':142,'mode':'rw','type':'uint', 'value':0    ,'desc':'Hour to stop Time if Day operation'},
    'ToDStopMin':      {'addr':143,'mode':'rw','type':'uint', 'value':0    ,'desc':'Minute to stop Time if Day operation'},
    'ToDOutput1':      {'addr':144,'mode':'rw','type':'uint', 'value':0    ,'desc':'Time of day controlled output 1'},
    'ToDOutput2':      {'addr':145,'mode':'rw','type':'uint', 'value':0    ,'desc':'Time of day controlled output 2'},
    'ToDOutput3':      {'addr':146,'mode':'rw','type':'uint', 'value':0    ,'desc':'Time of day controlled output 3'},
    'ToDOutput4':      {'addr':147,'mode':'rw','type':'uint', 'value':0    ,'desc':'Time of day controlled output 4'},
    'CountSource':     {'addr':150,'mode':'rw','type':'uint', 'value':0    ,'desc':'Counter source'},
    'Counter':         {'addr':151,'mode':'r', 'type':'dint', 'value':0    ,'desc':'Event counter'},
    'CountRstIntv':    {'addr':153,'mode':'rw','type':'uint', 'value':0    ,'desc':'Counter reset interval'},
    'TimerSource':     {'addr':154,'mode':'rw','type':'uint', 'value':0    ,'desc':'Timer source'},
    'Timer':           {'addr':155,'mode':'r', 'type':'dint', 'value':0    ,'desc':'Event counter in seconds'},
    'TimerRstIntv':    {'addr':157,'mode':'rw','type':'uint', 'value':0    ,'desc':'Timer reset interval'},
    'LogInterval':     {'addr':160,'mode':'rw','type':'uint', 'value':0    ,'desc':''},
    'LogRecords':      {'addr':161,'mode':'r', 'type':'uint', 'value':0    ,'desc':''},
    'LogNumber':       {'addr':162,'mode':'rw','type':'uint', 'value':0    ,'desc':''},
    'LogItem':         {'addr':163,'mode':'rw','type':'uint', 'value':0    ,'desc':''},
    'LogData':         {'addr':164,'mode':'rw','type':'float','value':0    ,'desc':''},
    'ProcessChanA':    {'addr':166,'mode':'rw','type':'uint', 'value':0    ,'desc':''},
    'ProcessChanB':    {'addr':167,'mode':'rw','type':'uint', 'value':0    ,'desc':''},
    'ProcessID':       {'addr':168,'mode':'rw','type':'uint', 'value':0    ,'desc':'Operation to perform on processed inputs'},
    'Status':          {'addr':  0,'mode':'r', 'type':'bool', 'value':False,'desc':'Current controller status, True=good'},
    'NTPTimeValid':    {'addr':  1,'mode':'r', 'type':'bool', 'value':False,'desc':'Status of last attempted NTP time synchonization'},
    'Startup':         {'addr':  2,'mode':'r', 'type':'bool', 'value':False,'desc':'True during controller startup, no controls active'},
    'SaveSettings':    {'addr':  3,'mode':'w', 'type':'bool', 'value':False,'desc':'save settings to EEPROM'},
    'ClearSettings':   {'addr':  4,'mode':'w', 'type':'bool', 'value':False,'desc':'set all settings to defaults'},
    'MidnightSave':    {'addr':  5,'mode':'rw','type':'bool', 'value':False,'desc':'Save settings each midnight'},
    'MidnightReset':   {'addr':  6,'mode':'rw','type':'bool', 'value':False,'desc':'Reset controller each midnight'},
    'SilenceAlarms':   {'addr':  7,'mode':'rw','type':'bool', 'value':False,'desc':'Silence alarms'},
    'DigitalIn1':      {'addr':  8,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'DigitalIn2':      {'addr':  9,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'Relay1Status':    {'addr': 10,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'Relay2Status':    {'addr': 11,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'DigitalOut1':     {'addr': 12,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'DigitalOut2':     {'addr': 13,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'Relay1Request':   {'addr': 14,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Relay2Request':   {'addr': 15,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Dout1Request':    {'addr': 16,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Dout2Request':    {'addr': 17,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'VirtualIO1':      {'addr': 18,'mode':'rw','type':'bool', 'value':False,'desc':'Virtual output register 1'},
    'VirtualIO2':      {'addr': 19,'mode':'rw','type':'bool', 'value':False,'desc':'Virtual output register 2'},
    'WQSensorValid':   {'addr': 20,'mode':'r', 'type':'bool', 'value':False,'desc':'Status of WQ sensor'},
    'Temp1Valid':      {'addr': 21,'mode':'r', 'type':'bool', 'value':False,'desc':'Status of Temperature 1 sensor'},
    'Temp2Valid':      {'addr': 22,'mode':'r', 'type':'bool', 'value':False,'desc':'Status of Temperature 2 sensor'},
    'Analog1Valid':    {'addr': 23,'mode':'r', 'type':'bool', 'value':False,'desc':'Status of Analog 1 input'},
    'Analog2Valid':    {'addr': 24,'mode':'r', 'type':'bool', 'value':False,'desc':'Status of Analog 2 input'},
    'LocalTempValid':  {'addr': 25,'mode':'r', 'type':'bool', 'value':False,'desc':'Status of Local Temperature reading'},
    'SupVoltValid':    {'addr': 26,'mode':'r', 'type':'bool', 'value':False,'desc':'Status of Supply Voltage reading'},
    'ProcReadValid':   {'addr': 27,'mode':'r', 'type':'bool', 'value':False,'desc':'Status of Processed Reading'},
    'LogicGateResult': {'addr': 28,'mode':'r', 'type':'bool', 'value':False,'desc':'Result of the Logic Gate function'},
    'Flash':           {'addr': 29,'mode':'r', 'type':'bool', 'value':False,'desc':'A 1Hz on/off signal'},
    'Ctrl1Enable':     {'addr': 30,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Ctrl2Enable':     {'addr': 31,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Ctrl3Enable':     {'addr': 32,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Ctrl4Enable':     {'addr': 33,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Ctrl1High':       {'addr': 34,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Ctrl2High':       {'addr': 35,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Ctrl3High':       {'addr': 36,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Ctrl4High':       {'addr': 37,'mode':'rw','type':'bool', 'value':False,'desc':''},
    'Ctrl1Active':     {'addr': 38,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'Ctrl2Active':     {'addr': 39,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'Ctrl3Active':     {'addr': 40,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'Ctrl4Active':     {'addr': 41,'mode':'r', 'type':'bool', 'value':False,'desc':''},
    'CtrlAlarm':       {'addr': 42,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop alarm'},
    'Ctrl1Alarm':      {'addr': 43,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 1 alarm'},
    'Ctrl2Alarm':      {'addr': 44,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 2 alarm'},
    'Ctrl3Alarm':      {'addr': 45,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 3 alarm'},
    'Ctrl4Alarm':      {'addr': 46,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 4 alarm'},
    'Ctrl1AlarmLow':   {'addr': 47,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 1 alarm low'},
    'Ctrl2AlarmLow':   {'addr': 48,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 2 alarm low'},
    'Ctrl3AlarmLow':   {'addr': 49,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 3 alarm low'},
    'Ctrl4AlarmLow':   {'addr': 50,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 4 alarm low'},
    'Ctrl1AlarmHigh':  {'addr': 51,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 1 alarm high'},
    'Ctrl2AlarmHigh':  {'addr': 52,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 2 alarm high'},
    'Ctrl3AlarmHigh':  {'addr': 53,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 3 alarm high'},
    'Ctrl4AlarmHigh':  {'addr': 54,'mode':'r', 'type':'bool', 'value':False,'desc':'Control loop 4 alarm high'},
    'RstCtrl1Max':     {'addr': 55,'mode':'w', 'type':'bool', 'value':False,'desc':''},
    'RstCtrl2Max':     {'addr': 56,'mode':'w', 'type':'bool', 'value':False,'desc':''},
    'RstCtrl3Max':     {'addr': 57,'mode':'w', 'type':'bool', 'value':False,'desc':''},
    'RstCtrl4Max':     {'addr': 58,'mode':'w', 'type':'bool', 'value':False,'desc':''},
    'ToDEnable':       {'addr': 61,'mode':'rw','type':'bool', 'value':False,'desc':'Enable time of day function'},
    'ToDActive':       {'addr': 62,'mode':'r' ,'type':'bool', 'value':False,'desc':'Time of day is active'},
    'ResetCounter':    {'addr': 63,'mode':'w' ,'type':'bool', 'value':False,'desc':'Write True to reset event counter'},
    'ResetTimer':      {'addr': 64,'mode':'w' ,'type':'bool', 'value':False,'desc':'Write True to reset event timer'},
    'ResetLogging':    {'addr': 65,'mode':'w' ,'type':'bool', 'value':False,'desc':'Write True to reset internal logging'},
    'statCtrl1OneShot':{'addr': 66,'mode':'rw','type':'bool', 'value':False,'desc':'Control loop 1 one-shot mode'},
    'statCtrl2OneShot':{'addr': 67,'mode':'rw','type':'bool', 'value':False,'desc':'Control loop 2 one-shot mode'},
    'statCtrl3OneShot':{'addr': 68,'mode':'rw','type':'bool', 'value':False,'desc':'Control loop 3 one-shot mode'},
    'statCtrl4OneShot':{'addr': 69,'mode':'rw','type':'bool', 'value':False,'desc':'Control loop 4 one-shot mode'}}
  units= ['None','°C','°F','pH','mV','V','mA','A','mm','m','ml','l','g','kg','lbs','kPa','PSI','Hz','%','ppm','Ω','day','hr','min','sec']
  processes= ['Average','Minimum','Maximum','Sum','Difference','Priority']
  channels= ['None','WQSensor','Temperature1','Temperature2','Analog1','Analog2',
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
  channelUnits= {'WQSensor':'WQSensorUnits',
                 'Temperature1':'Temp1Units',
                 'Temperature2':'Temp2Units',
                 'Analog1':'Analog1Units',
                 'Analog2':'Analog2Units',
                 'InternalTemp':'IntTempUnits',
                 'SupplyVoltage':'SupVoltUnits',
                 'ProcessedData':'ProcUnits'}
  channelValid= {'WQSensor':'WQSensorValid',
                 'Temperature1':'Temp1Valid',
                 'Temperature2':'Temp2Valid',
                 'Analog1':'Analog1Valid',
                 'Analog2':'Analog2Valid',
                 'InternalTemp':'LocalTempValid',
                 'SupplyVoltage':'SupVoltValid',
                 'ProcessedData':'ProcReadValid'}
               

  def __init__(self, master=None):
    self.ctrl=       None
    self.ctrlName=   None
    self.open=       False
    self.valid=      False
    self.dataTime=   dt.datetime.min
    self.comTime=    dt.datetime.min
    self.lastError=  False
    self.lastMessage=''
    self.ipAddr=     ''

  def start(self,ipAddr,port):
    if self.__mbStart(ipAddr,port):
      self.ipAddr= ipAddr
      self.port= port
      self.ctrlName= self.__mbRead('ControlName')
      if self.ctrlName=='' or self.ctrlName==None:
        self.ctrlName= 'SymbCtrl'
      if self.ctrlName!=None:
        self.lastError= False
        self.lastMessage= 'Controller {}@{} communication successful'.format(self.ctrlName,ipAddr)
        self.__mbClose()
        self.open= True
        self.comTime= dt.datetime.now()
        return True
    self.ctrl=       None
    self.ctrlName=   None
    self.open=       False
    self.valid=      False
    self.dataTime=   dt.datetime.min
    self.comTime=    dt.datetime.min
    self.lastError=  True
    self.lastMessage= 'Unable to open controller {}:{}'.format(ipAddr,port)
    return False
    
  def error(self):
    return self.lastError

  def message(self):
    return self.lastMessage

#-- controller register information -------------------------------------------
  def regList(self):
    return self.ctrlRegs.keys()

  def address(self,reg):
    if reg in self.ctrlRegs:
      self.lastError= False
      self.lastMessage= 'Success'
      return self.ctrlRegs[reg]['addr']
    self.lastError= True
    self.lastMessage= 'Bad register name'
    return None

  def valid(self):
    return self.valid

  def value(self,reg):
    if dt.datetime.now()-self.dataTime>dt.timedelta(seconds=self.validTime):
      self.lastError= True
      self.lastMessage= 'Data in buffer is over {:d}s old'.format(self.validTime)
      self.valid= False
      return None
    if reg in self.ctrlRegs:
      if (self.ctrlRegs[reg]['mode']=='r' or self.ctrlRegs[reg]['mode']=='rw'):
        self.lastError= False
        self.lastMessage= 'Success'
        return self.ctrlRegs[reg]['value']
      else:
        self.lastMessage= '{} is write only'.format(reg)
    else:
      self.lastMessage= 'Bad register name'
    self.lastError= True
    return None

  def getRegs(self):
    result= []
    for reg in self.ctrlRegs:
      result.append({'reg':reg,'value':self.ctrlRegs[reg]['value'],'type':self.ctrlRegs[reg]['type']})
    return result;

  def putValue(self,reg,value):
    self.lastError= True
    if not reg in self.ctrlRegs:
      self.lastMessage= 'Bad register name'
      return False
    type= self.ctrlRegs[reg]['type']
    if type=='int':
      if not isinstance(value,int):
        self.lastMessage= 'Value not integer for {}'.format(reg)
        return False
      if value<-32768 or value>32767:
        self.lastMessage= 'Value {:d} out of range for 16bit integer'.format(value)
        return False
    if type=='uint':
      if not isinstance(value,int):
        self.lastMessage= 'Value not integer for {}'.format(reg)
        return False
      if value<0 or value>65535:
        self.lastError= True
        self.lastMessage= 'Value {:d} out of range for unsigned integer'.format(value)
        return False
    if type=='dint':
      if not isinstance(value,int):
        self.lastMessage= 'Value not integer for {}'.format(reg)
        return False
      if value<0 or value>4294967295:
        self.lastMessage= 'Value {:d} out of range for 32bit integer'.format(value)
        return False
    if type=='float':
      if not (isinstance(value,(float,int))):
        self.lastMessage= 'Value not float for {}'.format(reg)
        return False
    if type=='str':
      if not isinstance(value,str):
        self.lastMessage= 'Value not str for {}'.format(reg)
        return False
    self.ctrlRegs[reg]['value']= value
    self.lastError= False
    self.lastMessage= 'Success'
    return True

  def type(self,reg):
    if reg in self.ctrlRegs:
      self.lastError= False
      self.lastMessage= 'Success'
      return self.ctrlRegs[reg]['type']
    self.lastError= True
    self.lastMessage= 'Bad register name'
    return None

  def mode(self,reg):
    if reg in self.ctrlRegs:
      self.lastError= False
      self.lastMessage= 'Success'
      return self.ctrlRegs[reg]['mode']
    self.lastError= True
    self.lastMessage= 'Bad register name'
    return None

  def description(self,reg):
    if reg in self.ctrlRegs:
      self.lastError= False
      self.lastMessage= 'Success'
      return self.ctrlRegs[reg]['desc']
    self.lastError= True
    self.lastMessage= 'Bad register name'
    return None

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
  
  # return a formatted string of the specified channel
  # units and valid status are used
  def textValue(self,chan):
    value= self.value(chan)
    if self.lastError: return '###'
    value= self.convert(chan,value)
    if self.ctrlRegs[chan]['type']== 'float':
      text= '{:.1f}'.format(value)
    elif self.ctrlRegs[chan]['type'] in ('unit','dint','int'):
      text= '{:d}'.format(value)
    elif self.ctrlRegs[chan]['type']=='bool':
      if 'Alarm' in chan:
        if value: text='Alarm'
        else: text= 'No Alarm'
      else:
        if value: text='On'
        else: text= 'Off'
    else:
      text= str(value)
    if chan in self.channelValid:
      if not self.ctrlRegs[self.channelValid[chan]]['value']:
        if self.ctrlRegs[chan]['type']=='float':
          text= '-.-'
        else:
          text= '--'
    if chan in self.channelUnits:
      units= self.channelUnit(chan)
      if units!=None: text= text+units
    return text
    
  def unit(self,unitID):
    if unitID==0 : return ''
    if unitID in range(len(self.units)):
      return self.units[unitID]
    return None
    
  def unitList(self):
    return self.units
    
  def channelUnit(self,chan):
    if chan in self.channelUnits:
      try:  return self.unit(self.ctrlRegs[self.channelUnits[chan]]['value'])
      except: return None
    return None
  
  def channelList(self):
    return self.channels
    
  def channel(self,chan):
    if chan in range(len(self.channels)):
      return self.channels[chan]
    return None

  def processList(self):
    return self.processes

#-- controller queries --------------------------------------------------------

  def name(self):
    return self.ctrlName

  def connected(self):
    return self.open

  def status(self):
    if not self.__mbOpen():
      self.lastError= True
      self.lastMessage= 'Unable to connect to {}'.format(self.ctrlName)
      self.open= False
      return None
    stat= self.__mbRead('Status')
    if stat==None:
      self.lastError= True
      self.lastMessage= 'Unable to query {} status '.format(self.ctrlName)
      self.__mbClose()
      return None
    self.lastError= False
    self.lastMessage= 'Success'
    self.__mbClose()
    self.comTime= dt.datetime.now()
    return stat

  def read(self,reg):
    if not self.__mbOpen():
      self.lastError= True
      self.lastMessage= 'Unable to connect to {}'.format(self.ctrlName)
      self.open= False
      return None
    val= self.__mbRead(reg)
    if val!=None:
      self.lastError= False
      self.lastMessage= 'Success'
      self.comTime= dt.datetime.now()
    else:
      self.lastError= True
      self.lastMessage= 'Unable to read {} from {}'.format(reg,self.ctrlName)
    self.__mbClose()
    return val

  def write(self,reg,value):
    if not self.__mbOpen():
      self.lastError= True
      self.lastMessage= 'Unable to connect to {}'.format(self.ctrlName)
      self.open= False
      return False
    if self.__mbWrite(reg,value):
      self.lastError= False
      self.lastMessage= 'Success'
      self.__mbClose()
      self.comTime= dt.datetime.now()
      return True
    self.lastError= True
    self.lastMessage= 'Unable to write {} to {}'.format(reg,self.ctrlName)
    self.__mbClose()
    return False

  def writeAll(self):
    for reg in self.ctrlRegs:
      if self.ctrlRegs[reg]['mode']=='rw':
        if not self.write(reg,self.ctrlRegs[reg]['value']):
          return False
    self.lastError= False
    self.lastMessage= 'Success'
    self.comTime= dt.datetime.now()
    return True

  def service(self):
    if not self.__mbOpen():
      self.lastError= True
      self.lastMessage= 'Unable to connect to {}'.format(self.ctrlName)
      self.open= False
      return False
    hold= self.__mbBlockHold(self.holdBase,self.holdSize)
    if hold==None:
      self.lastError= True
      self.lastMessage= 'Could not read data from {}'.format(self.ctrlName)
      self.__mbClose()
      return False
    coil= self.__mbBlockCoil(self.coilBase,self.coilSize)
    if coil==None:
      self.lastError= True
      self.lastMessage= 'Could not read data from {}'.format(self.ctrlName)
      self.__mbClose()
      return False
    for reg in self.ctrlRegs.keys():
      if self.ctrlRegs[reg]['mode']=='w': continue
      if self.ctrlRegs[reg]['type']=='bool':
        self.ctrlRegs[reg]['value']= coil[self.ctrlRegs[reg]['addr']]
      if self.ctrlRegs[reg]['type']=='int':
        self.ctrlRegs[reg]['value']= utils.get_list_2comp([hold[self.ctrlRegs[reg]['addr']]],16)[0]
      if self.ctrlRegs[reg]['type']=='uint':
        self.ctrlRegs[reg]['value']= hold[self.ctrlRegs[reg]['addr']]
      if self.ctrlRegs[reg]['type']=='dint':
        self.ctrlRegs[reg]['value']= hold[self.ctrlRegs[reg]['addr']]+(hold[self.ctrlRegs[reg]['addr']+1]*65536)
      if self.ctrlRegs[reg]['type']=='float':
        self.ctrlRegs[reg]['value']= utils.decode_ieee(utils.word_list_to_long([hold[self.ctrlRegs[reg]['addr']],hold[self.ctrlRegs[reg]['addr']+1]],big_endian=False)[0])
      if self.ctrlRegs[reg]['type']=='str':
        st= ''
        addr= self.ctrlRegs[reg]['addr']
        for pos in range(8):
          ch= hold[addr+pos]>>8
          if ch==0: break
          st= st+chr(ch)
          ch= hold[addr+pos]&0xFF
          if ch==0: break
          st= st+chr(ch)
        self.ctrlRegs[reg]['value']= st
      if self.ctrlRegs[reg]['type']=='time':
        self.ctrlRegs[reg]['value']= '{:02d}:{:02d}:{:02d}'.format(hold[self.ctrlRegs[reg]['addr']],hold[self.ctrlRegs[reg]['addr']+1],hold[self.ctrlRegs[reg]['addr']+2])
      if self.ctrlRegs[reg]['type']=='hour':
        self.ctrlRegs[reg]['value']= '{:02d}:{:02d}'.format(hold[self.ctrlRegs[reg]['addr']],hold[self.ctrlRegs[reg]['addr']+1])
    self.__mbClose()
    self.comTime=  dt.datetime.now()
    self.dataTime= dt.datetime.now()
    self.valid= True
    return True

  #-- modbus handling ---------------------------------------------------------
  def __mbStart(self,ipAddr,port):
    self.ctrl= ModbusClient(host=ipAddr,port=port,unit_id=1,timeout=self.timeout,auto_open=False,auto_close=False)
    return self.ctrl.open()

  def __mbOpen(self):
    if self.ctrl.is_open()==True:
      self.ctrl.close()
    return self.ctrl.open()

  def __mbClose(self):
    if self.ctrl.is_open():
      self.ctrl.close()
    return True

  def __mbRead(self,reg):
    if reg not in self.ctrlRegs:
      return None
    addr= self.ctrlRegs[reg]['addr']
    type= self.ctrlRegs[reg]['type']
    if type=='int':
      return utils.get_list_2comp(self.ctrl.read_holding_registers(addr,1),16)[0]
    if type=='uint':
      return self.ctrl.read_holding_registers(addr,1)[0]
    if type=='dint':
      return utils.word_list_to_long(self.ctrl.read_holding_registers(addr,2))
    if type=='float':
      while True:
        result= self.ctrl.read_holding_registers(addr,2)
        if result==None:
          return None
        else:
          return utils.decode_ieee(utils.word_list_to_long(result,big_endian=False)[0])
    if type=='str':
      st= ''
      arry= self.ctrl.read_holding_registers(addr,8)
      if arry==None: return None
      for chs in arry:
        ch= chs>>8
        if ch==0: return st
        st= st+chr(ch)
        ch= chs&0xFF
        if ch==0: return st
        st= st+chr(ch)
      return st
    if type=='bool':
      while True:
        result= self.ctrl.read_coils(addr,1)
        if result==None:
          return None
        else:
          return result[0]
    return None

  def __mbWrite(self,reg,data):
    if reg not in self.ctrlRegs:
      return False
    addr= self.ctrlRegs[reg]['addr']
    type= self.ctrlRegs[reg]['type']
    if type=='int':
      if not isinstance(data,int): return False
      if (data & (1<<15))!= 0: data= data-(1<<16)
      if self.ctrl.write_single_register(addr,data&65535):
        return True
      print('Here!!')
    if type=='uint':
      if not isinstance(data,int): return False
      if self.ctrl.write_single_register(addr,data):
        return True
    if type=='dint':
      if not isinstance(data,int): return False
      if self.ctrl.write_multiple_registers(addr,[(data>>16)&0xffff,data&0xffff]):
        return True
    if type=='float':
      if not isinstance(data,float): return False
      if self.ctrl.write_multiple_registers(addr,utils.long_list_to_word([utils.encode_ieee(data)],big_endian=False)):
        return True
    if type=='str':
      if not isinstance(data,str): return False
      arry= []
      for pos in range(8):
        word= 0
        if pos*2<len(data):
          word= ord(data[pos*2])*256
        if pos*2+1<len(data):
          word= word+ord(data[pos*2+1])
        arry.append(word)
      if self.ctrl.write_multiple_registers(addr,arry):
        return True
    if type=='bool':
      if not isinstance(data,bool): return False
      if self.ctrl.write_single_coil(addr,data):
        return True
    return False

  def __mbBlockHold(self,addr,size):
    block= []
    for start in range(addr,size,100):
      end= start+99;
      if end>size-1: end= size-1
      part= self.ctrl.read_holding_registers(start,end-start+1)
      if part!=None:
        for reg in part:
          block.append(reg)
      else:
        return None
    return block

  def __mbBlockCoil(self,addr,size):
    block= []
    for start in range(addr,size,100):
      end= start+99;
      if end>size-1: end= size-1
      part= self.ctrl.read_coils(start,end-start+1)
      if part!=None:
        for reg in part:
          block.append(reg)
      else:
        return None
    return block

#-- test code -----------------------------------------------------------------
# import random
# import time

#controller= SymbCtrl()
#print('Start...')
#res= controller.start('192.168.1.4',502)
#print('  Error:     {}'.format(str(controller.error())))
#print('  Message:   {}'.format(controller.message()))
#print('')

#controller.testBlock(0,300)

# print('Single queries...')
# print('  Status:    {}'.format(str(controller.status())))
# print('    Error:   {}'.format(str(controller.error())))
# print('    Message: {}'.format(controller.message()))
# print('  Time:      {:02d}:{:02d}:{:02d}'.format(controller.read('Hour'),controller.read('Minute'),controller.read('Second')))
# print('    Error:   {}'.format(str(controller.error())))
# print('    Message: {}'.format(controller.message()))
# print('  Time Zone: {:d}'.format(controller.read('Timezone')))
# print('    Error:   {}'.format(str(controller.error())))
# print('    Message: {}'.format(controller.message()))
# print('  Int Temp:  {:.2f}'.format(controller.read('LocalTemp')))
# print('    Error:   {}'.format(str(controller.error())))
# print('    Message: {}'.format(controller.message()))
# print('')
# print('Heartbeat...')
# for count in range(5):
  # num= random.randint(0,65535)
  # print('  Write:     {:d}'.format(num))
  # controller.write('HeartbeatIn',num)
  # print('  Read:      {:d}'.format(controller.read('HeartbeatOut')))
# print('Toggle outputs...')
# controller.write('Relay1Request',True)
# time.sleep(1)
# controller.write('Relay1Request',False)
# controller.write('Relay2Request',True)
# time.sleep(1)
# controller.write('Relay2Request',False)
# controller.write('Dout1Request',True)
# time.sleep(1)
# controller.write('Dout1Request',False)
# controller.write('Dout2Request',True)
# time.sleep(1)
# controller.write('Dout2Request',False)
# print('Service...')
# res= controller.service()
# print('  Error:     {}'.format(str(controller.error())))
# print('  Message:   {}'.format(controller.message()))

#-- end SymbCtrl --------------------------------------------------------------