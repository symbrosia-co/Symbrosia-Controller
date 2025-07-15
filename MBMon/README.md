# MbMon
MbMon is a simple Modbus logging utility, it can monitor any ModbusTCP device and store data into a CSV file.  The application is a Python GUI that may be used as is, or examined as an example of how to write you own Modbus scripts.

<p align="center"><img src="/res/MBMon.png"></p>

The program reads a configuration file and simply runs, reading from the specified Modbus devices and registers and logging the data to the specified CSV file.

Each device is shown in a section with the device name and IP address displayed.  Beneath a header each datum is displayed in table format.  The background color to the header indicates connection status to the device, green or red.  Occasional red may be displayed if network connectivity is poor or temporarily interrupted, the data request will be re-attempted.  A prolonged connection error will result in the data values being dashed out indicating stale and invalid data.

Below the data table is a log window that records a record of logging events and communications errors.

## Installation
MBMon is installed by simply copying the MBMon directory to your desired location on a local hard drive.

There are three subdirectories in the folder for MBMon...
+ **lib** should contain the required file MBScan.py
+ **setup** will likewise hold the configuration file MBMon.xml (see below)
+ **log** which will hold the resulting CSV files.  If **log** does not exist the directory will be created when MBMon is run the first time.

## Dependencies
MBMon requires Python 3.x be installed on the local computer.  Along with Python there is one additional library, pyModbusTCP required.  The latest version of Python should be downloaded and installed from the Python.org website.  The library for pyModbusTCP may be installed directly using PIP (recommended) or from the Github archive.

+ [Python.org](https://www.python.org/) Follow the install links of the main page for your operating system

To install pyModbusTCP using PIP use the following at a command line...

+ Unix/Linix systems  **sudo pip3 install pyModbusTCP**
+ Windows **pip install pyModbusTCP**

pyModbusTCP support...

+ [pyModbusTCP at Github](https://github.com/sourceperl/pyModbusTCP)
+ [pyModbusTCP documentation at Read the Docs](https://pymodbustcp.readthedocs.io/en/stable/index.html)

## Configuration file
MbMon is configured using an XML file that stores the IP address and register addresses of the desired data.  This file should be named MBMon.xml and be placed the the **setup** subdirectory.  A couple example configuration files are provided in the Github repository.

```xml
<!-- Modbus Monitor Configuration File -->
<configuration>
  <scanInterval>1</scanInterval>
  <logInterval>120</logInterval>
  <logName>TankCtrl</logName>
  <device>
    <name>Tank X01</name>
    <ipAddr>192.168.0.111</ipAddr>
    <port>502</port>
    <datum>
      <name>Tank Temp</name>
      <addr>22</addr>
      <type>float</type>
      <unit>°C</unit>
      <dispPrec>2</dispPrec>
      <logPrec>2</logPrec>
      <log>True</log>
    </datum>
    <datum>
      <name>Tank pH</name>
      <addr>20</addr>
      <type>float</type>
      <unit>pH</unit>
      <dispPrec>1</dispPrec>
      <logPrec>2</logPrec>
      <log>True</log>
    </datum>
    <datum>
      <name>CO2 Valve</name>
      <addr>12</addr>
      <type>coil</type>
      <log>True</log>
    </datum>
  </device>
</configuration>
```

A description of each XML field is below.

+ **configuration** This tag encompasses the entire MBMon configuration file
+ **scanInterval** Specified the rate at which the device should be queried for data over the network in seconds.  Can be set to longer intervals for equipment that cannot support high data rates.
+ **logInterval** Specifies the interval for writing to the log file in seconds.
+ **logname** Base filename for the resulting data file, the name will have the date and the filename extension **.xml** appended to the supplied name.  Files will be created when needed, if the file already exists data will be appended each logging interval.
+ **name** A decriptive name for the device, this will be used to organize the data for display during logging and will be appended to the column header in the CSV file.
+ **ipAddr** The local IP address for the ModbusTCP device.
+ **port** The port for ModbusTCP access, usually the default ModbusTCP port 502.
+ **datum** Used to specify a specific item of data.
+ **name** A descriptive name for the item of data, this will be used to format the data for display when logging and as the column header in the CSV file.
+ **addr** The ModbusTCP register address, addressing starting at zero is used. It is important to specify a type to read the cirrect address in the device, coil registers are used for coil or boolean values, else holding registers are read.
+ **type** The type of data expected, the following values are permissable
+ **unit** The units (if any), this is used for data display during logging, this field is not required and is not used for coil or boolean types
+ **dispPrec** The number of decimal points to be displayed during logging, this field is not required or used for non-floating point values
+ **logPrec** The number of decimal points to be recorded in the log file, this field is not required or used for non-floating point values
+ **log** If **true** the value is logged to the CSV file, if **false** the value is displayed only.

<p align="center"><img width="50" height="50" src="/res/SymbrosiaLogo.png"></p>