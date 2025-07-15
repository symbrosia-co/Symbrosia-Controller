# SyView
SyView is the Python configuration utility for the Symbrosia Controller. With SyView a user can configure and test a controller, as well as save and load configurations to and from the controller.

<p align="center"><img src="/res/SyView.png"></p>

SyView is a Python 3.x application that should run on any modern operating system.

## Installation
SyView is installed by simply copying the SyView directory to your desired location on a local hard drive.

There are three subdirectories in the folder for SyView...
+ **lib** should contain the various required files for SyView
+ **configuration** will likewise hold the configuration file configuration.xml (see below)

## Dependencies
SyView requires Python 3.x be installed on the local computer.  Along with Python there is one additional library, pyModbusTCP required.  The latest version of Python should be downloaded and installed from the Python.org website.  The library for pyModbusTCP may be installed directly using PIP (recommended) or from the Github archive.

+ [Python.org](https://www.python.org/) Follow the install links of the main page for your operating system

To install pyModbusTCP using PIP use the following at a command line...

+ Unix/Linix systems  **sudo pip3 install pyModbusTCP**
+ Windows **pip install pyModbusTCP**

pyModbusTCP support...

+ [pyModbusTCP at Github](https://github.com/sourceperl/pyModbusTCP)
+ [pyModbusTCP documentation at Read the Docs](https://pymodbustcp.readthedocs.io/en/stable/index.html)


## Configuration file
SyView is configured using an XML file that stores the IP address and register addresses of the desired data.  This file should be named configuration.xml and be placed the the **cfg** subdirectory.  An example configuration file is provided in the Github repository.

```xml
<!-- SyView Configuration File -->

<configuration>
  <ctrl name='Tank X01'>
    <model>SyCtrl Mk2</model>
    <description>Tank Controller</description>
    <address>192.168.0.24</address>
  </ctrl>
  <ctrl name='Tank X02'>
    <model>SyCtrl Mk2</model>
    <description>Tank Controller</description>
    <address>192.168.0.245</address>
  </ctrl>
</configuration>
```

A description of each XML field is below.

+ **configuration** This tag encompasses the entire configuration file
+ **model** The specific controller model, currently only Mark 2's are supported
+ **description** A quick description identifying the controller
+ **address** The IP address of the target Symbrosia controller

<p align="center"><img width="50" height="50" src="/res/SymbrosiaLogo.png"></p>

---
