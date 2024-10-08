#------------------------------------------------------------------------------
#  Config
#
#  - Read configuration files
#  - written for Python v3.4
#
#  Symbrosia
#  Copyright 2021, all rights reserved
#
# 30Jan2022 A. Cooper v0.1
#  - Initial version
#
#------------------------------------------------------------------------------

#-- library -------------------------------------------------------------------
import sys
import os
import xml.etree.ElementTree as xml
from tkinter import messagebox

#----------------------------------------------------------------------------
#  Load general configuration
#  - return config else None
#  - Four sensors are currently supported
#
def loadConfig(configPath,configFile):
  #try:
  tree = xml.parse(os.path.join(configPath,configFile))
  #except:
  #  messagebox.showerror(title='Startup error...',message='Unable to load configuration file {}\{}'.format(configPath,configFile))
  #  return None
  #process top level
  config= {}
  config['devices']= []
  root= tree.getroot()
  for item in root:
    if item.tag=='device':
      device= {'data':[]}
      for dev in item:
        if dev.tag=='datum':
          datum= {}
          for dat in dev:
            datum[dat.tag]= dat.text
          device['data'].append(datum)
        else:
          device[dev.tag]= dev.text
      config['devices'].append(device)
    else:
      config[item.tag]= item.text
  return config

#-- End Config ----------------------------------------------------------------