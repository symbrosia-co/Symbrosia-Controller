#------------------------------------------------------------------------------
#  SyCheck
#
#  - Ensure correct configuration of controllers on the network
#  - written for Python v3.9
#
#  Symbrosia
#  Copyright 2021, all rights reserved
#
# 23Oct2024 A. Cooper v0.1
# - initial version
#
#------------------------------------------------------------------------------
verStr= 'SyCheck v0.1'

#-- constants -----------------------------------------------------------------
cfgFileName= 'configuration.xml'
cfgFilePath= 'cfg'
rptFilePath= 'rpt'
refFilePath= 'ref'
libFilePath= 'lib'
colBack=     '#BBBBBB'
colDev=      '#999999'
colOn=       '#ADFF8C'
colOff=      '#FFADAD'

verbose=     False;

#-- library -------------------------------------------------------------------
import string
import sys
import os
import time
import urllib.request
import datetime as     dt
import tkinter  as     tk
from   tkinter  import ttk, messagebox, filedialog
from   pyModbusTCP.client import ModbusClient
from   pyModbusTCP import utils
import xml.etree.ElementTree as xml

#-- globals -------------------------------------------------------------------
localDir= os.path.dirname(os.path.realpath(__file__))
rptPath=  os.path.join(localDir,rptFilePath)
cfgPath=  os.path.join(localDir,cfgFilePath)
refPath=  os.path.join(localDir,refFilePath)
libPath=  os.path.join(localDir,libFilePath)
print(libPath)
sys.path.append(libPath)

#-- local libraries -----------------------------------------------------------
import symbCtrlModbus.py

#------------------------------------------------------------------------------
#  SyCheck GUI
#
#  - setup the GUI
#
#  23Oct2024 A. Cooper
#  - initial version
#
#------------------------------------------------------------------------------
class Application(tk.Frame):
  units= {}
  refs=  {}
  lastLog=  dt.datetime.now()
  eventNow= dt.datetime.min
  controller= SymbCtrl();

  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.grid()
    self.createWidgets()
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW",self.done)
    # load units and refs
    if not self.loadConfig(cfgPath,cfgFileName):
      sys.exit()
    if not self.loadRefs(refPath):
      sys.exit()
    self.createUnitMenu();
    #finish
    self.logEvent('{} started'.format(verStr),True)
    self.device= ModbusClient(debug=verbose)
    print('{} running...'.format(verStr))

  def createWidgets(self):
    spaceX= 5
    spaceY= 1
    #buttons
    self.scanButton=       tk.Button(self,text="Scan",width=10,command=self.scan,font=("Helvetica", "12"))
    self.scanButton.grid   (column=1,row=2,padx=spaceX,pady=spaceY)
    self.scanAllButton=    tk.Button(self,text="Scan All",width=10,command=self.scanAll,font=("Helvetica", "12"))
    self.scanAllButton.grid(column=1,row=3,padx=spaceX,pady=spaceY)
    self.saveButton=       tk.Button(self,text="Save",width=10,command=self.save,font=("Helvetica", "12"))
    self.saveButton.grid   (column=1,row=4,padx=spaceX,pady=spaceY)
    self.quitButton=       tk.Button(self,text="Quit",width=10,command=self.done,font=("Helvetica", "12"))
    self.quitButton.grid   (column=1,row=5,padx=spaceX,pady=spaceY)
    #log window
    self.eventLog=         tk.Text(self,width=80,height=16,bg=colBack)
    self.eventLog.grid     (column=3,row=1,rowspan=5,padx=0,pady=spaceY,sticky=tk.E+tk.W)
    self.scrollbar=        tk.Scrollbar(self)
    self.scrollbar.config  (command=self.eventLog.yview)
    self.eventLog.config   (yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid    (column=4,row=1,rowspan=5,padx=0,pady=spaceY,sticky=tk.N+tk.S+tk.W)
    #spacers
    self.spacer1=          tk.Label(self,text=' ')
    self.spacer1.grid      (column=0,row=0)
    self.spacer2=          tk.Label(self,text=' ')
    self.spacer2.grid      (column=5,row=6)
    
  def createUnitMenu(self):
    spaceX= 5
    spaceY= 1
    self.ctrlList= []
    for ctrl in self.units:
      self.ctrlList.append(ctrl['name'])
    self.ctrlStr= tk.StringVar()
    self.ctrlStr.set(self.ctrlList[0])
    self.ctrlMenu= tk.OptionMenu(self,self.ctrlStr,*self.ctrlList)
    self.ctrlMenu.config (width=14,font=('Helvetica','10'))
    self.ctrlMenu.grid(column=1,row=1,padx=spaceX,pady=spaceY,sticky=tk.W)

  def loadConfig(self,configPath,configFile):
    #try:
    tree = xml.parse(os.path.join(configPath,configFile))
    #except:
    #  messagebox.showerror(title='Startup error...',message='Unable to load configuration file {}\{}'.format(configPath,configFile))
    #  return False
    #process top level
    self.units= []
    root= tree.getroot()
    for ctrl in root:
      if ctrl.tag=='ctrl':
        new= {'name':ctrl.attrib['name']}
        for item in ctrl:
          new[item.tag]= item.text
        self.units.append(new)
    self.logEvent('Controllers loaded',True)
    return True

  def loadRefs(self,refPath):
    self.refs= {}
    for unit in self.units:
      if unit['ref'] not in self.refs:
        try:
          tree = xml.parse(os.path.join(refPath,unit['ref']))
        except:
          messagebox.showerror(title='Startup error...',message='Unable to load refernce file {}\{}'.format(configPath,unit['ref']))
          return False
        #process top level
        new= {}
        root= tree.getroot()
        for reg in root:
          if reg.tag=='register':
            new[reg.attrib['name']]= reg.text
        self.refs[unit['ref']]= new
        self.logEvent('Reference file {} loaded'.format(unit['ref']),True)
    return True

  #- GUI event handling -------------------------------------------------------

  def scan(self):
    pass
      
  def scanAll(self):
    for unit in self.units:
      self.logEvent('Check config for {}...'.format(unit['name']),True)
      if self.controller.start(unit['address'],502):
        self.controller.service()
        regs= self.controller.getRegs()
        for reg in regs:
          print(reg)
      else:
        self.logEvent('  Error!! Unable to open {}'.format(unit['name']),True)
        
    
  def save(self):
    pass

  # handle the quit button
  def done(self):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
      if self.mbActive:
        root.after_cancel(self.mbEvent)
      #self.closeLogFile()
      self.quit()

  #- Event reporting ----------------------------------------------------------

  # log event
  def logEvent(self,event,incDate):
    self.eventLast= self.eventNow
    self.eventNow= dt.datetime.now()
    if (self.eventNow-self.eventLast)<dt.timedelta(seconds=2):
      incDate= False
    if incDate:
      self.eventLog.insert(tk.END,'{:%Y-%m-%d %H:%M:%S} '.format(self.eventNow))
    else:
      self.eventLog.insert(tk.END,'                    ')
    self.eventLog.insert(tk.END,event+'\n')
    self.eventLog.see(tk.END)

  def clearEvents(self):
    self.eventLog.delete('1.0',tk.END)

  #- Report -------------------------------------------------------------------

  def report(self):
    pass

  #- Modbus -------------------------------------------------------------------
  
  def getController(self):
    pass

#------------------------------------------------------------------------------
#  GUI Main
#
#  - run the GIU
#
#  08Feb2010 A. Cooper
#  - initial version
#
#------------------------------------------------------------------------------
root= tk.Tk()
app= Application(master=root)
app.master.title(verStr)
root.protocol("WM_DELETE_WINDOW",app.done)
app.mainloop()
root.destroy()

#-- End MBMon -----------------------------------------------------------------