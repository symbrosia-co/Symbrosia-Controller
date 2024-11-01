# SyCheck
SyCheck performs configuration checks on any number of deployed controllers.

Assuring that each controller in an installation is configured correctly can be a time consuming task.  SyCheck will retrieve the configuration for each controller on the network and compare the configuration against a reference file, producing a report of any differences found.

A set of configuration files are required.  The first file is an XML file contianing the IP addresses of any deployed controllers and the name of the reference file that controller should be configured with.  Also required are one or more reference files to compare against the controllers in the installation.

SyCheck is a Python 3.x application that should run on any operating system.

One library is required beyond the standard Python install, the [pyModbusTCP library by Loic Lefebvre](https://pypi.org/project/pyModbusTCP/).  This can be installed by through pip...

* sudo pip install pyModbusTCP (for Linix/Unix)
* pip install pyModbusTCP (for Windows)

## Configuration file
The configuration file is an XML file that contains a record for each controller on the network you wish to check.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
  SyCheck Configuration File
  - Installation specific information
-->
<configuration>
  <ctrl name='Tank 1'>
    <address>192.168.1.20</address>
    <ref>TankSetup.xml</ref>
  </ctrl>
  <ctrl name='Tank 2'>
    <address>192.168.1.21</address>
    <ref>TankSetup.xml</ref>
  </ctrl>
</configuration>
```

You may have multiple reference files so that each controller may use one of several different configurations

## Reference File
The reference file uses the same file format used by SyView to upload and download controller configurations.  Simply using SyView to save the setup of a known good controller can be used as a starting point.

Some editing of this file is suggested.  Only the fields present in the file will be checked, fields not requiring checks can be deleted.  Fields such as unit name will always fail (unless you name all of your controllers the same, probably not good practice;)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
  Tank configuration file
  2024Jun22 08:45:25
-->
<configuration>
  <register name="WQName">pH</register>
  <register name="Temp1Name">Tank Temp</register>
  <register name="Temp2Name"></register>
  <register name="Input1Name"></register>
  <register name="Input2Name"></register>
  <register name="Relay1Name">Cooling Valve</register>
  <register name="Relay2Name"></register>
  <register name="Output1Name">CO2 Valve</register>
  <register name="Output2Name"></register>
  <register name="Control1Name">pH</register>
  <register name="Control2Name">Cooling</register>
  <register name="Control3Name">Lights</register>
  <register name="Control4Name"></register>
  <register name="StatusDisp1">1</register>
  <register name="StatusDisp2">2</register>
  <register name="TimeZone">-10</register>
  <register name="WQSensorUnits">3</register>
  <register name="Temp1Units">1</register>
  <register name="Temp2Units">1</register>
  <register name="Analog1Units">5</register>
  <register name="Analog2Units">5</register>
  <register name="IntTempUnits">1</register>
  <register name="SupVoltUnits">5</register>
  <register name="WQOffset">-0.20</register>
  <register name="Temp1Offset">0.10</register>
  <register name="Temp2Offset">0.00</register>
  <register name="Analog1Offset">0.00</register>
  <register name="Analog2Offset">0.00</register>
  <register name="WQGain">1.08</register>
  <register name="Temp1Gain">1.00</register>
  <register name="Temp2Gain">1.00</register>
  <register name="Analog1Gain">1.00</register>
  <register name="Analog2Gain">1.00</register>
  <register name="Ctrl1Input">1</register>
  <register name="Ctrl1Output">13</register>
  <register name="Ctrl1Setpoint">7.50</register>
  <register name="Ctrl1Hysteresis">0.20</register>
  <register name="Ctrl1AlarmPtLow">7.00</register>
  <register name="Ctrl1AlarmPtHigh">8.00</register>
  <register name="Ctrl1OffTime">0</register>
  <register name="Ctrl1OnTime">0</register>
  <register name="Ctrl2Input">2</register>
  <register name="Ctrl2Output">11</register>
  <register name="Ctrl2Setpoint">23.50</register>
  <register name="Ctrl2Hysteresis">1.00</register>
  <register name="Ctrl2AlarmPtLow">20.00</register>
  <register name="Ctrl2AlarmPtHigh">28.00</register>
  <register name="Ctrl2OffTime">0</register>
  <register name="Ctrl2OnTime">0</register>
  <register name="Ctrl3Input">0</register>
  <register name="Ctrl3Output">0</register>
  <register name="Ctrl3Setpoint">6.00</register>
  <register name="Ctrl3Hysteresis">12.00</register>
  <register name="Ctrl3AlarmPtLow">0.00</register>
  <register name="Ctrl3AlarmPtHigh">30.00</register>
  <register name="Ctrl3OffTime">0</register>
  <register name="Ctrl3OnTime">0</register>
  <register name="Ctrl4Input">0</register>
  <register name="Ctrl4Output">0</register>
  <register name="Ctrl4Setpoint">1.50</register>
  <register name="Ctrl4Hysteresis">0.50</register>
  <register name="Ctrl4AlarmPtLow">0.00</register>
  <register name="Ctrl4AlarmPtHigh">2.00</register>
  <register name="Ctrl4OffTime">0</register>
  <register name="Ctrl4OnTime">0</register>
  <register name="LogicInA">0</register>
  <register name="LogicInB">0</register>
  <register name="LogicFunction">0</register>
  <register name="ToDStartHour">6</register>
  <register name="ToDStartMin">0</register>
  <register name="ToDStopHour">18</register>
  <register name="ToDStopMin">0</register>
  <register name="ToDOutput1">13</register>
  <register name="ToDOutput2">0</register>
  <register name="ToDOutput3">0</register>
  <register name="ToDOutput4">0</register>
  <register name="CountSource">13</register>
  <register name="CountRstIntv">2</register>
  <register name="TimerSource">13</register>
  <register name="TimerRstIntv">2</register>
  <register name="LogInterval">10</register>
  <register name="LogNumber">0</register>
  <register name="LogItem">0</register>
  <register name="LogData">0.00</register>
  <register name="ProcessChanA">0</register>
  <register name="ProcessChanB">0</register>
  <register name="ProcessID">0</register>
  <register name="MidnightSave">False</register>
  <register name="MidnightReset">False</register>
  <register name="SilenceAlarms">False</register>
  <register name="Relay1Request">False</register>
  <register name="Relay2Request">False</register>
  <register name="Dout1Request">False</register>
  <register name="Dout2Request">False</register>
  <register name="VState1">False</register>
  <register name="VState2">False</register>
  <register name="Ctrl1Enable">True</register>
  <register name="Ctrl2Enable">True</register>
  <register name="Ctrl3Enable">False</register>
  <register name="Ctrl4Enable">False</register>
  <register name="Ctrl1High">True</register>
  <register name="Ctrl2High">True</register>
  <register name="Ctrl3High">False</register>
  <register name="Ctrl4High">False</register>
  <register name="CounterEnable">False</register>
  <register name="TimerEnable">False</register>
  <register name="ToDEnable">True</register>
</configuration>
```
