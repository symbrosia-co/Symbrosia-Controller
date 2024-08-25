#------------------------------------------------------------------------------
#  Weather
#
#  - A simple weather display GUI
#  - written for Python v3.9
#
#  Symbrosia
#  Copyright 2024, all rights reserved
#
# 25Aug2024 A. Cooper v0.1
#  - initial version
#
#------------------------------------------------------------------------------
verStr= 'Weather v0.1'

#-- constants -----------------------------------------------------------------
cfgFileName= 'config.xml'
logFileName= 'Weather'
logFilePath= 'log'
cfgFilePath= 'cfg'
libFilePath= 'lib'
colBack=     '#BBBBBB'
colDev=      '#999999'
colOn=       '#ADFF8C'
colOff=      '#FFADAD'

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
logPath=  os.path.join(localDir,logFilePath)
cfgPath=  os.path.join(localDir,cfgFilePath)
libPath=  os.path.join(localDir,libFilePath)
sys.path.append(libPath)

#-- includes ------------------------------------------------------------------
from config import loadConfig
import symbCtrlModbus

#------------------------------------------------------------------------------
#  Weather GUI
#
#  - setup the GUI
#
#------------------------------------------------------------------------------
class Application(tk.Frame):
  config=       {}
  data=         []
  logFile=      None
  lastLog=      dt.datetime.now()
  eventNow=     dt.datetime.min
  mbActive=     False
  logging=      False

  def __init__(self, master=None):
    self.config= loadConfig(cfgPath,cfgFileName)
    if self.config==None:
      sys.exit()
    print(self.config)
    sys.exit()
    tk.Frame.__init__(self, master)
    self.grid()
    self.createWidgets()
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW",self.done)
    self.logEvent('{} started'.format(verStr),True)
    self.device= ModbusClient(debug=verbose)
    print('{} running...'.format(verStr))

  def createWidgets(self):
    spaceX= 5
    spaceY= 1
    #data fields
    row= 1
    for device in self.config['devices']:
      label= tk.Label(self,text=device['name'],width=50,anchor=tk.W,font=("Helvetica","12"),bg=colDev)
      label.grid(column=1,row=row,columnspan=4,sticky=tk.W)
      label= tk.Label(self,text=device['ipAddr'],width=40,anchor=tk.E,font=("Helvetica","12"),bg=colDev)
      label.grid(column=4,row=row,columnspan=3,sticky=tk.W)
      row+= 1
      for dat in device['data']:
        datum= {}
        label= tk.Label(self,text=dat['name'],font=("Helvetica","10"))
        label.grid    (column=1,row=row,pady=spaceY,sticky=tk.E)
        datum['ipAddr']=  device['ipAddr']
        datum['port']=    device['port']
        datum['devName']= device['name']
        datum['name']=    dat['name']
        datum['addr']=    dat['addr']
        datum['type']=    dat['type']
        if 'log' in dat:
          datum['log']=   dat['log']
        else:
          datum['log']=   False
        if 'precision' in dat:
          datum['prec']=  dat['precision']
        datum['write']=   False
        datum['value']=   None
        if 'log' in dat:
          if dat['log']== 'True': datum['log']= True
          else: datum['log']= False
        else: datum['log']= False
        label= tk.Label(self,text='---',font=("Helvetica","12"))
        label.grid     (column=2,row=row,sticky=tk.E)
        datum['valueDisp']= label
        if 'unit' in dat:
          label= tk.Label(self,text=dat['unit'],anchor=tk.W,font=("Helvetica","10"))
          label.grid     (column=3,row=row,sticky=tk.W)
        if 'write' in dat:
          button=  tk.Button(self,text='Write',width=10,command=self.write,font=("Helvetica", "12"))
          button.grid     (column=5,row=row)
          datum['button']=  button
          datum['write']=   True
        row+= 1
        self.data.append(datum)
    #log window
    self.eventLog=         tk.Text(self,width=80,height=8,bg=colBack)
    self.eventLog.grid     (column=1,row=row,padx=0,pady=spaceY,columnspan=5,sticky=tk.E+tk.W)
    self.scrollbar=        tk.Scrollbar(self)
    self.scrollbar.config  (command=self.eventLog.yview)
    self.eventLog.config   (yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid    (column=6,row=row,padx=0,pady=8,sticky=tk.N+tk.S+tk.W)
    #buttons
    self.startButton=      tk.Button(self,text="Stopped",width=10,command=self.startStop,font=("Helvetica", "12"),bg=colOff)
    self.startButton.grid  (column=1,row=row+1,padx=spaceX,pady=spaceY)
    self.logButton=        tk.Button(self,text="No Log",width=10,command=self.startLog,font=("Helvetica", "12"),bg=colOff)
    self.logButton.grid    (column=2,row=row+1,padx=spaceX,pady=spaceY)
    self.quitButton=       tk.Button(self,text="Quit",width=10,command=self.done,font=("Helvetica", "12"))
    self.quitButton.grid   (column=5,row=row+1,padx=spaceX,pady=spaceY)
    #spacers
    self.spacer1=          tk.Label(self,text=' ')
    self.spacer1.grid      (column=0,row=0)
    self.spacer2=          tk.Label(self,text=' ')
    self.spacer2.grid      (column=7,row=row+2)

  #- GUI event handling -------------------------------------------------------

  def write(self):
    pass
    
  def startStop(self):
    if self.mbActive:
      self.mbActive= False
      self.logging= False
      root.after_cancel(self.mbEvent)
      self.startButton.config(text="Stopped",bg=colOff)
    else:
      self.mbActive= True
      self.update();
      self.startButton.config(text="Running",bg=colOn)
      
  def startLog(self):
    if self.logging:
      self.logging= False
      self.logButton.config(text="No Log",bg=colOff)
    else:
      if self.mbActive:
        self.logging= True
        self.logButton.config(text="Logging",bg=colOn)

  # handle the quit button
  def done(self):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
      if self.mbActive:
        root.after_cancel(self.mbEvent)
      #self.closeLogFile()
      self.quit()

  def update(self):
    self.scanModbus();
    self.logWrite();
    if self.mbActive:
      self.mbEvent= root.after(int(self.config['scanInterval'])*1000,self.update)

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

  #- Log File -----------------------------------------------------------------

  def logWrite(self):
    if not self.logging:
      self.logButton.config(text="No Log",bg=colOff)
      return
    self.logButton.config(text="Logging",bg=colOn)
    now= dt.datetime.now()
    interval= int(self.config['logInterval'])
    if interval<10: interval=10
    if (now-self.lastLog)<dt.timedelta(seconds=(interval-5)):
      return
    if interval%60==0:
      if now.second!=0:
        return
    elif interval%10==0:
      if now.second%10!=0:
        return
    else:
      if now-self.lastLog<dt.timedelta(seconds=interval):
        return
    self.lastLog= now
    # write log file
    if 'logName' in self.config:
      logName= '{}{}.csv'.format(self.config['logName'],now.strftime('%Y%m%d'))
    else:
      logName= '{}{}.csv'.format(logFileName,now.strftime('%Y%m%d'))
    filePath= os.path.join(logPath,logName)
    new= not os.path.exists(filePath)
    # write header if new file
    if new:
      outFile= open(filePath,'w')
      outFile.write('Date and Time')
      for item in self.data:
        if item['log']:
          outFile.write(', {}'.format(item['name']))
      outFile.write('\n')
      self.logEvent('New log file {} created'.format(logName),True)
    else:
      outFile= open(filePath,'a')
    # write data line
    outFile.write('{}'.format(dt.datetime.now().strftime('%Y%b%d %H:%M:%S')))
    for item in self.data:
      if verbose: print(item['name'],item['value'])
      if item['log']:
        if item['value']==None:
          outFile.write(',')
        else:
          if item['type']=='float':
            outFile.write(', {:8.2f}'.format(item['value']))
          if item['type']=='hold':
            outFile.write(', {:8d}'.format(int(item['value'])))
          if item['type']=='long':
            outFile.write(', {:8d}'.format(int(item['value'])))
          if item['type']=='coil':
            if item['value']:
              outFile.write(',  True')
            else:
              outFile.write(', False')
    outFile.write('\n')
    outFile.close()
    self.logEvent('Log file {} appended'.format(logName),True)

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

#-- End Weather ---------------------------------------------------------------