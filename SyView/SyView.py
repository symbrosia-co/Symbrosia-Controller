#------------------------------------------------------------------------------
#  SyView
#
#  - Symbrosia controller interface
#  - written for Python v3.4
#  
#  Symbrosia
#  Copyright 2022-2024, all rights reserved
#
#  28Jan2022 v0.1 A. Cooper
#  - initial version
#  15Mar2024 v1.0 A. Cooper
#  - completed outputs tab
#  28Jul2024 v1.1 A. Cooper
#  - Added support for the new features of v2.6
#    - min on/off time
#    - one-shot
#    - external enable
#  - Added simulated LCD to status display
#  - Added status display value selection to status stab
#  31Oct2024 v1.2 A. Cooper
#  - Fix analog channels numbers for time
#  31Nov2024 v1.3 A. Cooper
#  - add manual IP address selection
#
# Known issues:
# - missing units for internal temp on status screen
# - current reading not displayed for some inputs on control tab
#
#------------------------------------------------------------------------------
verStr= 'SyView v1.3'

#-- constants -----------------------------------------------------------------
configFile= 'configuration.xml'
colOn=      '#ADFF8C'
colOff=     '#FFADAD'
colHigh=    '#E0FFE0'
colLow=     '#FFE0E0'
colBack=    '#BBBBBB'
colTab=     '#CCCCCC'
tabSizeX=   750
tabSizeY=   400

#-- library -------------------------------------------------------------------
import string
import sys
import os
import time
import ipaddress
import datetime as dt
import tkinter as tk
from   tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as xml

#-- globals -------------------------------------------------------------------
localDir=    os.path.dirname(os.path.realpath(__file__))
libPath=     os.path.join(localDir,'lib')
configPath=  os.path.join(localDir,'cfg')
logPath=     os.path.join(localDir,'log')
unitPath=    os.path.join(localDir,'units')
sys.path.append(libPath)

#-- includes ------------------------------------------------------------------
from config import loadConfig
import symbCtrlModbus
import status,inputs,outputs,control,misc,registers,events

# -- constants ----------------------------------------------------------------
logoImageFile= 'logo.png'

#------------------------------------------------------------------------------
#  SyView GUI
#
#  - setup the GUI
#
#  28Jan2022 A. Cooper
#  - initial version
#
#------------------------------------------------------------------------------
class Application(tk.Frame):
  tabs=      []
  config=    {}
  ctrlList=  []
  online=    False
  scanning=  False
  heartbeat= 0
  unitCfg=   {}

  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.grid()
    self.config= loadConfig(configPath,configFile)
    #print(self.config)
    self.controller= symbCtrlModbus.SymbCtrl()
    self.createWidgets()
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW",self.done)
    self.eventNow= dt.datetime(2021,6,2)
    self.update()
    self.eventsTab.log('{} started'.format(verStr),True)
    print('{} running...'.format(verStr))
    # attempt to open first controller in the config
    #self.openControl()
    #if self.online: self.scanning= True

  def createWidgets(self):
    spaceX= 8
    spaceY= 5
    self.logoImage=      tk.PhotoImage(file=os.path.join(localDir,'img',logoImageFile))
    # side frame
    self.scanButton=     tk.Button(self,text="Scanning",bg=colOff,width=10,command=self.scanToggle,font=('Helvetica','12'))
    self.scanButton.grid (column=1,row=2,padx=spaceX,pady=spaceY)
    self.loadButton=     tk.Button(self,text="Load Cfg",width=10,command=self.loadCfgFile,font=('Helvetica','12'))
    self.loadButton.grid (column=1,row=3,padx=spaceX,pady=spaceY)
    self.sendButton=     tk.Button(self,text="Send Cfg",width=10,command=self.sendCfg,font=('Helvetica','12'))
    self.sendButton.grid (column=1,row=4,padx=spaceX,pady=spaceY)
    self.saveButton=     tk.Button(self,text="Save Cfg",width=10,command=self.saveCfgFile,font=('Helvetica','12'))
    self.saveButton.grid (column=1,row=5,padx=spaceX,pady=spaceY)
    self.quitButton=     tk.Button(self,text="Quit",width=10,command=self.done,font=('Helvetica','12'))
    self.quitButton.grid (column=1,row=7,padx=spaceX,pady=spaceY)
    self.logoButton=     tk.Button(self,image=self.logoImage,width=104,height=104,relief=tk.FLAT)
    self.logoButton.grid (column=1,row=8,rowspan=2,padx=spaceX,pady=spaceY)
    # controller menu
    self.ctrlList= ['Manual']
    for ctrl in self.config['ctrlList']:
      self.ctrlList.append(ctrl['name'])
    self.ctrlStr= tk.StringVar()
    self.ctrlStr.set(self.ctrlList[0])
    self.ctrlMenu= tk.OptionMenu(self,self.ctrlStr,*self.ctrlList,command=self.changeControl)
    self.ctrlMenu.config (width=14,font=('Helvetica','10'))
    self.ctrlMenu.grid(column=0,row=0,columnspan=3,padx=spaceX,pady=spaceY,sticky=tk.W)
    # IP entry box
    self.IPaddr=        tk.Entry(self,width=14,justify="center",font=('Helvetica','12'))
    self.IPaddr.grid    (column=1,row=1,padx=spaceX,pady=spaceY)
    self.IPaddr.delete  (0,tk.END)
    self.IPaddr.insert  (0,"192.168.0.xxx")
    # tabbing system
    self.allTabs=        ttk.Notebook(self,height=tabSizeY,width=tabSizeX)
    self.allTabs.tk.call ('font', 'configure', 'TkDefaultFont', '-size', '12')
    self.statusTab=      status.Status(self.allTabs,self.controller)
    self.allTabs.add     (self.statusTab, text='   Status  ')
    self.inputsTab=      inputs.Inputs(self.allTabs,self.controller)
    self.allTabs.add     (self.inputsTab, text=' Inputs  ')
    self.outputsTab=     outputs.Outputs(self.allTabs,self.controller)
    self.allTabs.add     (self.outputsTab, text=' Outputs  ')
    self.control1Tab=    control.Control(self.allTabs,self.controller,1)
    self.allTabs.add     (self.control1Tab, text=' Control 1  ')
    self.control2Tab=    control.Control(self.allTabs,self.controller,2)
    self.allTabs.add     (self.control2Tab, text=' Control 2  ')
    self.control3Tab=    control.Control(self.allTabs,self.controller,3)
    self.allTabs.add     (self.control3Tab, text=' Control 3  ')
    self.control4Tab=    control.Control(self.allTabs,self.controller,4)
    self.allTabs.add     (self.control4Tab, text=' Control 4  ')
    self.miscTab=        misc.Misc(self.allTabs,self.controller)
    self.allTabs.add     (self.miscTab, text=' Misc  ')
    self.registersTab=   registers.Registers(self.allTabs,self.controller)
    self.allTabs.add     (self.registersTab, text=' Registers  ')
    self.eventsTab=      events.Events(self.allTabs)
    self.allTabs.add     (self.eventsTab, text=' Events  ')
    self.allTabs.grid(column=3,row=1,columnspan=9,rowspan=9)
    # status labels
    self.commLabel= tk.Label(self,text='Communication',font=('Helvetica','9'),bg=colOff,relief=tk.GROOVE)
    self.commLabel.grid (column=3,row=0,pady=spaceY,sticky=tk.E+tk.W)
    self.statLabel= tk.Label(self,text='Controller',font=('Helvetica','9'),bg=colOff,relief=tk.GROOVE)
    self.statLabel.grid (column=4,row=0,pady=spaceY,sticky=tk.E+tk.W)
    #self.logLabel= tk.Label(self,text='Logging off',font=('Helvetica','9'),bg=colOff,relief=tk.GROOVE)
    #self.logLabel.grid (column=5,row=0,pady=spaceY,sticky=tk.E+tk.W)
    self.ipLabel= tk.Label(self,text='xxx.xxx.xxx.xxx',font=('Helvetica','9'))
    self.ipLabel.grid (column=10,row=0,columnspan=2,pady=spaceY,sticky=tk.W)
    # spacers
    self.spacer1= tk.Label(self,text=' ')
    self.spacer1.grid (column=9,row=0)
    # set method delegates to allow universal access
    self.delegates= {'CtrlRegList': self.controller.regList,
                     'CtrlValue':   self.controller.value, 
                     'CtrlService': self.controller.service,
                     'CtrlRead':    self.controller.read,
                     'CtrlWrite':   self.controller.write,
                     'CtrlType':    self.controller.type,
                     'CtrlMode':    self.controller.mode,
                     'CtrlStatus':  self.controller.status,
                     'EventLog':    self.eventsTab.log,
                     'EventSave':   self.eventsTab.save}
    self.statusTab.setDelegates(self.delegates)
    self.inputsTab.setDelegates(self.delegates)
    self.outputsTab.setDelegates(self.delegates)
    self.control1Tab.setDelegates(self.delegates)
    self.control2Tab.setDelegates(self.delegates)
    self.control3Tab.setDelegates(self.delegates)
    self.control4Tab.setDelegates(self.delegates)
    self.miscTab.setDelegates(self.delegates)
    self.eventsTab.setDelegates(self.delegates)
    self.registersTab.setDelegates(self.delegates)

  #- Event reporting ----------------------------------------------------------

  # log event
  def logEvent(self,event,incDate):
    self.writeLogWin(event,incDate)
    self.writeLogFile(event)

  def writeLogWin(self,event,incDate):
    self.eventLast= self.eventNow
    self.eventNow= dt.datetime.now()
    if (self.eventNow-self.eventLast)<dt.timedelta(seconds=2):
      incDate= False
    if incDate:
      self.eventLog.insert(tk.END,'{:%Y%b%d %H:%M:%S} '.format(self.eventNow))
    else:
      self.eventLog.insert(tk.END,'                   ')
    self.eventLog.insert(tk.END,event+'\n')
    self.eventLog.see(tk.END)

  def writeLogFile(self,event):
    today= dt.date.today()
    fileName= '{}{:%Y%m%d}.log'.format(logFileName,today)
    if today!=self.logFileDate:
      if self.logFile!=None:
        self.logFile.write('{:%Y%b%d %H:%M:%S} Closed log file\n'.format(dt.datetime.now()))
        self.logFile.close()
        self.logFile== None
        self.writeLogWin('Close previous log file',True)
    if self.logFile!=None and self.logFile.closed:
      self.logFile= None
    if self.logFile==None:
      try:
        self.logFile= open(os.path.join(logPath,'PondView',fileName),'a',buffering=1)
        self.logFile.write('{:%Y%b%d %H:%M:%S} Opened log file\n'.format(dt.datetime.now()))
      except:
        self.logFile= None
        self.writeLogWin('Unable to open log {}'.format(fileName),True)
        return  
      self.writeLogWin('Opened log {}'.format(fileName),True)
      self.logFileDate= today
    if self.logFile!=None:
      self.logFile.write('{:%Y%b%d %H:%M:%S} {}\n'.format(dt.datetime.now(),event))

  def closeLogFile(self):
    if self.logFile!=None and not self.logFile.closed:
      self.logFile.write('{:%Y%b%d %H:%M:%S} Closed log file\n'.format(dt.datetime.now()))
      self.logFile.close()

  #- GUI event handling -------------------------------------------------------

  # handle the quit button
  def done(self):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
      root.after_cancel(self.dispUpdate)
      #self.closeLogFile()
      self.quit()

  def scanToggle(self):
    if self.scanning:
      self.scanning= False
      self.scanButton.config(text="Scan Off",bg=colOff)
      self.eventsTab.log("Scanning turned off",True)
    else:
      self.scanning= True
      self.scanButton.config(text="Scanning",bg=colOn)
      self.eventsTab.log("Scanning turned on",True)
      if not self.controller.connected(): self.openControl()
  
  def scanSet(self,set):
    if set:
      self.scanning= True
      self.scanButton.config(text="Scanning",bg=colOn)
      self.eventsTab.log("Scanning turned on",True)
    else:
      self.scanning= False
      self.scanButton.config(text="Scan Off",bg=colOff)
      self.eventsTab.log("Scanning turned off",True)

  #- controller and display update --------------------------------------------

  def openControl(self):
    if len(self.config['ctrlList'])<1:
      self.eventsTab.log('No controllers in config!',True)
      return
    if self.ctrlStr.get()=='Manual':
      try:
        ipaddress.ip_address(self.IPaddr.get())
      except ValueError:
        messagebox.showerror(title='Error...', message='Invalid IP address!!')
        self.scanning= False
        self.scanButton.config(text='Scan Off',bg=colOff)
        return
      self.config['ctrlList'][0]['address']= self.IPaddr.get()
      self.currCtrl= self.config['ctrlList'][0]
    else:
      for ctrl in self.config['ctrlList']:
        if ctrl['name']==self.ctrlStr.get():
          self.currCtrl= ctrl
          self.IPaddr.delete (0,tk.END)
          self.IPaddr.insert (0,self.currCtrl['address'])
    self.ipLabel.config(text=self.currCtrl['address'])
    self.controller.start(self.currCtrl['address'],502)
    if self.controller.error():
      self.eventsTab.log('Controller error: {}'.format(self.controller.message()),True)
      self.online= False
      self.currCtrl== {}
    else:
      self.eventsTab.log(self.controller.message(),True)
      self.online= True
  
  def changeControl(self,param):
    self.openControl()  
  
  def update(self):
    # read all values from the controller
    if not self.controller.connected():
      self.scanning= False
      self.scanButton.config(text="Scan Off",bg=colOff)
    if self.scanning:
      if self.controller.connected():
        self.onLine= True
        self.controller.service()  
        self.commLabel.config(bg=colOn)
        if self.controller.value('Status'):
          self.statLabel.config(bg=colOn)
        else:
          self.statLabel.config(bg=colOff)
      else:
        if self.online==True:
          self.online= False
          self.commLabel.config(bg=colOff)
          self.eventsTab.log('Communication with {} lost!'.format(self.currCtrl['name']),True)
    else:
      self.commLabel.config(bg=colOff)
      self.statLabel.config(bg=colOff)
    # update the various tabs
    tab= self.allTabs.index(self.allTabs.select())
    if tab==0: self.statusTab.update()
    if tab==1: self.inputsTab.update()
    if tab==2: self.outputsTab.update()
    if tab==3: self.control1Tab.update()
    if tab==4: self.control2Tab.update()
    if tab==5: self.control3Tab.update()
    if tab==6: self.control4Tab.update()
    if tab==7: self.miscTab.update()
    if tab==8: self.registersTab.update()
    # heartbeat
    if self.online:
      self.heartbeat+=1
      if self.heartbeat>65535: self.heartbeat= 0
      self.controller.write('HeartbeatIn',self.heartbeat)
    # update again in 0.5s
    self.dispUpdate= root.after(500,self.update)
    
  #- load and save controller configuration files -----------------------------
  def loadCfgFile(self):
    # load and parse the specified file
    type= [('XML', '*.xml')]
    file= filedialog.askopenfilename(filetypes=type,defaultextension=type,initialdir=unitPath)
    if file==None: return
    try:
      tree= xml.parse(file)
    except:
      messagebox.showerror(title='File error...',message='Unable to load controller configuration file {}'.format(file))
      return
    #clear any existing configuration
    self.unitCfg= {}
    #process config
    root= tree.getroot()
    for item in root:
      if item.tag=='register':
        reg= item.get('name')
        val= self.controller.convert(reg,item.text)
        if val!=None:
          self.unitCfg[reg]= val
    self.eventsTab.log('{} loaded'.format(file),True)
    
  def sendCfg(self):
    prob= False
    if len(self.unitCfg)<1:
      messagebox.showwarning(title='Send error...', message='No configuration data to send!')
    else:
      for reg in self.unitCfg.keys():
        self.controller.write(reg,self.unitCfg[reg])
        if self.controller.error():
          self.eventsTab.log('Send error for register {}!'.format(reg),True)
          prob= True
    if prob:
      messagebox.showwarning(title='Send error...', message='Errors during send! See log')
      self.eventsTab.log('Problems sending unit configuration!',True)
    else:
      messagebox.showwarning(title='Send configuration...', message='Parameters sent to SN:{} successfully!'.format(self.controller.read('SerialNumber')))
      self.eventsTab.log('Unit configuration sent!',True)

  def saveCfgFile(self):
    if self.online:
      type= [('XML', '*.xml')]
      file= filedialog.asksaveasfilename(filetypes=type,defaultextension=type,initialdir=unitPath)
      if file==None: return
      try:
        cfgFile= open(file,'w',encoding="utf-8")
      except:
        messagebox.showwarning(title='File error...', message='Unable to open file {}'.format(file))
        return
      cfgFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
      cfgFile.write('<!--\n\n')
      cfgFile.write('  {} configuration file\n'.format(self.currCtrl['name']))
      cfgFile.write('  {:%Y%b%d %H:%M:%S}\n\n'.format(dt.datetime.now()))
      cfgFile.write('-->\n\n')
      cfgFile.write('<configuration>\n')
      for reg in self.controller.regList():
        if self.controller.mode(reg)=='rw':
          if self.controller.type(reg)=='float':
            cfgFile.write('  <register name="{}">{:.2f}</register>\n'.format(reg,self.controller.value(reg)))
          else:
            cfgFile.write('  <register name="{}">{}</register>\n'.format(reg,str(self.controller.value(reg))))
      cfgFile.write('</configuration>\n')
      cfgFile.close()
      self.eventsTab.log('Configuration {} saved'.format(file),True)

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

#-- End SyView ----------------------------------------------------------------