#------------------------------------------------------------------------------
#  SyCheck
#
#  - Ensure correct configuration of controllers on the network
#  - written for Python v3.9
#
#  Symbrosia
#  Copyright 2024, all rights reserved
#
# 23Oct2024 A. Cooper v0.1
# - initial version
# 23Oct2024 A. Cooper v0.2
# - test version released to cultivation
#
#------------------------------------------------------------------------------
verStr= 'SyCheck v0.2'

#-- constants -----------------------------------------------------------------
cfgFileName= 'configuration.xml'
cfgFilePath= 'cfg'
rptFilePath= 'reports'
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
sys.path.append(libPath)

#-- local libraries -----------------------------------------------------------
import symbCtrlModbus

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
  report=[]
  lastLog=  dt.datetime.now()
  eventNow= dt.datetime.min

  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.grid()
    self.createWidgets()
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW",self.done)
    self.controller= symbCtrlModbus.SymbCtrl()
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
    self.saveButton=       tk.Button(self,text="Save",width=10,command=self.saveReport,font=("Helvetica", "12"))
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
    try:
      tree = xml.parse(os.path.join(configPath,configFile))
    except:
      messagebox.showerror(title='Startup error...',message='Unable to load configuration file {}\{}'.format(cfgFilePath,configFile))
      return False
    # process top level
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
          messagebox.showerror(title='Startup error...',message='Unable to load reference file {}\{}'.format(cfgFilePath,unit['ref']))
          return False
        #process top level
        new= []
        root= tree.getroot()
        for reg in root:
          if reg.tag=='register':
            new.append({'reg':reg.attrib['name'],'value':reg.text,'type':self.controller.type(reg.attrib['name'])})
        self.refs[unit['ref']]= new
        self.logEvent('Reference file {} loaded'.format(unit['ref']),True)
    return True

  #- GUI event handling -------------------------------------------------------

  def scan(self):
    self.report= []
    self.report.append('SyCheck Report')
    self.report.append('  {:%Y-%m-%d %H:%M:%S}'.format(dt.datetime.now()))
    self.report.append('  ')
    for unit in self.units:
      if unit['name']==self.ctrlStr.get():
        self.scanUnit(unit)
    self.logEvent('Scan {} complete'.format(self.ctrlStr.get()),True)
      
  def scanAll(self):
    self.report= []
    self.report.append('SyCheck Report')
    self.report.append('  {:%Y-%m-%d %H:%M:%S}'.format(dt.datetime.now()))
    self.report.append('')
    for unit in self.units:
      self.scanUnit(unit)
    self.logEvent('Scan all complete',True)

  def scanUnit(self,unit):
      header= '  Register               Controller   Reference        Description'
      headline= '  -------------------------------------------------------------------------------------------'
      self.logEvent('Check config for {} against {}...'.format(unit['name'],unit['ref']),True)
      self.report.append('Check config for {} against {}...'.format(unit['name'],unit['ref']))
      diffs= 0
      if self.controller.start(unit['address'],502):
        self.controller.service()
        if self.controller.error():
          self.logEvent('  Communications error with {}'.format(unit['name']),True)
          self.report.append('  Communications error with {}'.format(unit['name']))
        else:
          self.logEvent('  {} configuration read'.format(unit['name']),True)
          firstErr= True
          for reg in self.refs[unit['ref']]:
            regValue= self.controller.value(reg['reg'])
            refValue= self.controller.convert(reg['reg'],reg['value'])
            if reg['type']=='str':
              if regValue!=refValue:
                if firstErr:
                  self.report.append(header)
                  self.report.append(headline)
                  firstErr= False
                self.logEvent('  {}:\'{}\' ≠ \'{}\' in reference'.format(reg['reg'],regValue,refValue),True)
                self.report.append('  {:<16} {:>16} ≠ {:<16} {}'.format(reg['reg'],regValue,refValue,self.controller.description(reg['reg'])))
                diffs+=1
            if reg['type']=='int' or reg['reg']=='uint':
              if regValue!=refValue:
                if firstErr:
                  self.report.append(header)
                  self.report.append(headline)
                  firstErr= False
                self.logEvent('  {}:{:d} ≠ {:d} in reference'.format(reg['reg'],regValue,refValue),True)
                self.report.append('  {:<16} {:>16d} ≠ {:<16d} {}'.format(reg['reg'],regValue,refValue,self.controller.description(reg['reg'])))
                diffs+=1
            if reg['type']=='float':
              if round(regValue,4)!=round(refValue,4):
                if firstErr:
                  self.report.append(header)
                  self.report.append(headline)
                  firstErr= False
                self.logEvent('  {}:{:.2f} ≠ {:.2f} in reference'.format(reg['reg'],regValue,refValue),True)
                self.report.append('  {:<16} {:>16.2f} ≠ {:<16.2f} {}'.format(reg['reg'],regValue,refValue,self.controller.description(reg['reg'])))
                diffs+=1
            if reg['type']=='bool':
              if regValue!=refValue:
                if firstErr:
                  self.report.append(header)
                  self.report.append(headline)
                  firstErr= False
                self.logEvent('  {}:{} ≠ {} in reference'.format(reg['reg'],regValue,refValue),True)
                if regValue: regValue='On'
                else: regValue= 'Off'
                if refValue: refValue='On'
                else: refValue= 'Off'
                self.report.append('  {:<16} {:>16} ≠ {:<16} {}'.format(reg['reg'],regValue,refValue,self.controller.description(reg['reg'])))
                diffs+=1
          if diffs==0:
            self.logEvent('  No differences found'.format(diffs),True)
            self.report.append('  No differences found'.format(diffs))
          elif diffs==1:
            self.logEvent('  {:d} difference found'.format(diffs),True)
            self.report.append('  {:d} difference found'.format(diffs))
          else:
            self.logEvent('  {:d} differences found'.format(diffs),True)
            self.report.append('  {:d} differences found'.format(diffs))
          self.report.append('')
      else:
        self.logEvent('  Error!! Unable to open {}'.format(unit['name']),True)
        self.report.append('  Error!! Unable to open {}'.format(unit['name']))    

  def saveReport(self):
      type= [('Text', '*.txt')]
      name= 'SyCheck{:%Y%m%d}'.format(dt.datetime.now())
      file= filedialog.asksaveasfilename(title='Save report...',initialfile=name,filetypes=type,defaultextension=type,initialdir=rptPath)
      if file=='': return
      if file==None: return
      try:
        reportFile= open(file,'w',encoding="utf-8")
      except:
        messagebox.showwarning(title='File error...', message='Unable to open file {}'.format(file))
        return
      for line in self.report:
        reportFile.write(line)
        reportFile.write('\n')
      reportFile.close()
      self.logEvent('Report {} saved'.format(os.path.basename(file)),True)  

  # handle the quit button
  def done(self):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
      self.quit()

  #- Event reporting ----------------------------------------------------------

  # log event
  def logEvent(self,event,incDate):
    self.eventLast= self.eventNow
    self.eventNow= dt.datetime.now()
    if (self.eventNow-self.eventLast)<dt.timedelta(seconds=3):
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