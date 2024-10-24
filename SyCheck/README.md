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

...
<!--
  SyView Configuration File
  - Installation specific information in XML format
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
...

You may have multiple reference files so that each controller may use one of several different configurations

## Reference File
The reference file uses the same file format used by SyView to upload and download controller configurations.  Simply using SyView to save the setup of a known good controller can be used here.

<!--

  Tank configuration file
  2024Jun22 08:45:25

-->
<configuration>
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
</configuration>

Some editing of this file is suggested.  Only the fields present in the file will be checked, fields not requiring checks can be deleted.  Fields such as unit name will always fail (unless you name all of your controllers the same, probably not good practice;)
---
