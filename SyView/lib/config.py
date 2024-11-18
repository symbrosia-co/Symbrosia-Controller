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
# - initial version
# 13Nov2024 A. Cooper v1.3
# - add manual controller entry
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
#
def loadConfig(configPath,configFile):
  try:
    tree= xml.parse(os.path.join(configPath,configFile))
  except:
    messagebox.showerror(title='Startup error...',message='Unable to load configuration file {}\{}'.format(configPath,configFile))
    return None
  #process config
  root= tree.getroot()
  config= {'ctrlList':[{'name':'Manual','model':'SyCtrl Mk2','address':'192.168.0.0'}]}
  for section in root:
    if section.tag=='ctrl':
      ctrl= {'name':section.get('name')}
      for item in section:
        ctrl[item.tag]= item.text
      config['ctrlList'].append(ctrl)
    else:
      config[section.tag]= section.text
  return config

#-- End Config ----------------------------------------------------------------