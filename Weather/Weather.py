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
colTemp=     '#A00000'
colHumid=    '#0070A0'
colRain=     '#0000A0'
colPAR=      '#00A000'
dataSize=     14
unitSize=     10
dataFont=     'Arial'
graphX=       250
graphY=       100

verbose=     True

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
  scanActive=   False
  logging=      False

  def __init__(self, master=None):
    self.config= loadConfig(cfgPath,cfgFileName)
    if self.config==None:
      sys.exit()
    # create GUI
    tk.Frame.__init__(self, master)
    self.grid()
    self.createWidgets()
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW",self.done)
    # setup modbus
    self.controller= symbCtrlModbus.SymbCtrl()
    # running
    self.logEvent('{} started'.format(verStr),True)
    self.device= ModbusClient(debug=verbose)
    print('{} running...'.format(verStr))

  def createWidgets(self):
    spaceX= 5
    spaceY= 1
    # temperature
    self.label=            tk.Label(self,text='Temp',font=(dataFont,unitSize),fg=colTemp)
    self.label.grid        (column=1,row=1,sticky=tk.E)
    self.label=            tk.Label(self,text='Tmax',font=(dataFont,unitSize),fg=colTemp)
    self.label.grid        (column=1,row=2,sticky=tk.E)
    self.label=            tk.Label(self,text='Tmin',font=(dataFont,unitSize),fg=colTemp)
    self.label.grid        (column=1,row=3,sticky=tk.E)
    self.rainData=         tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colTemp)
    self.rainData.grid     (column=2,row=1)
    self.rainDataMax=      tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colTemp)
    self.rainDataMax.grid  (column=2,row=2)
    self.rainDataMin=      tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colTemp)
    self.rainDataMin.grid  (column=2,row=3)
    self.label=            tk.Label(self,text='°C',font=(dataFont,unitSize),fg=colTemp)
    self.label.grid        (column=3,row=1,sticky=tk.W)
    self.label=            tk.Label(self,text='°C',font=(dataFont,unitSize),fg=colTemp)
    self.label.grid        (column=3,row=2,sticky=tk.W)
    self.label=            tk.Label(self,text='°C',font=(dataFont,unitSize),fg=colTemp)
    self.label.grid        (column=3,row=3,sticky=tk.W)
    self.tempGraph=        tk.Canvas(self,width=graphX,height=graphY,bg=colBack)
    self.tempGraph.grid    (column=4,row=1,padx=spaceX,pady=spaceY,rowspan=3)
    # humidity
    self.label=            tk.Label(self,text='Humidity',font=(dataFont,unitSize),fg=colHumid)
    self.label.grid        (column=6,row=1,sticky=tk.E)
    self.label=            tk.Label(self,text='RHmax',font=(dataFont,unitSize),fg=colHumid)
    self.label.grid        (column=6,row=2,sticky=tk.E)
    self.label=            tk.Label(self,text='RHmin',font=(dataFont,unitSize),fg=colHumid)
    self.label.grid        (column=6,row=3,sticky=tk.E)
    self.humidData=        tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colHumid)
    self.humidData.grid    (column=7,row=1)
    self.humidDataMax=     tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colHumid)
    self.humidDataMax.grid (column=7,row=2)
    self.humidDataMin=     tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colHumid)
    self.humidDataMin.grid (column=7,row=3)
    self.label=            tk.Label(self,text='%RH',font=(dataFont,unitSize),fg=colHumid)
    self.label.grid        (column=8,row=1,sticky=tk.W)
    self.label=            tk.Label(self,text='%RH',font=(dataFont,unitSize),fg=colHumid)
    self.label.grid        (column=8,row=2,sticky=tk.W)
    self.label=            tk.Label(self,text='%RH',font=(dataFont,unitSize),fg=colHumid)
    self.label.grid        (column=8,row=3,sticky=tk.W)
    self.tempGraph=        tk.Canvas(self,width=graphX,height=graphY,bg=colBack)
    self.tempGraph.grid    (column=9,row=1,padx=spaceX,pady=spaceY,rowspan=3)
    # precipitation
    self.label=            tk.Label(self,text='Precipitation',font=(dataFont,unitSize),fg=colRain)
    self.label.grid        (column=1,row=5,sticky=tk.E)
    self.label=            tk.Label(self,text='Rate',font=(dataFont,unitSize),fg=colRain)
    self.label.grid        (column=1,row=6,sticky=tk.E)
    self.rainData=         tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colRain)
    self.rainData.grid     (column=2,row=5)
    self.rainDataRate=      tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colRain)
    self.rainDataRate.grid  (column=2,row=6)
    self.label=            tk.Label(self,text='mm',font=(dataFont,unitSize),fg=colRain)
    self.label.grid        (column=3,row=5,sticky=tk.W)
    self.label=            tk.Label(self,text='mm/h',font=(dataFont,unitSize),fg=colRain)
    self.label.grid        (column=3,row=6,sticky=tk.W)
    self.spacer=           tk.Label(self,text=' ',font=(dataFont,unitSize))
    self.spacer.grid       (column=3,row=7)
    self.rainGraph=        tk.Canvas(self,width=graphX,height=graphY,bg=colBack)
    self.rainGraph.grid    (column=4,row=5,padx=spaceX,pady=spaceY,rowspan=3)
    # PAR
    self.label=            tk.Label(self,text='PAR',font=(dataFont,unitSize),fg=colPAR)
    self.label.grid        (column=6,row=5,sticky=tk.E)
    self.label=            tk.Label(self,text='Tmax',font=(dataFont,unitSize),fg=colPAR)
    self.label.grid        (column=6,row=6,sticky=tk.E)
    self.parData=          tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colPAR)
    self.parData.grid      (column=7,row=5)
    self.parDataMax=       tk.Label(self,text='0.0',font=(dataFont,dataSize),fg=colPAR)
    self.parDataMax.grid   (column=7,row=6)
    self.label=            tk.Label(self,text='µMol/m²/s',font=(dataFont,unitSize),fg=colPAR)
    self.label.grid        (column=8,row=5,sticky=tk.W)
    self.label=            tk.Label(self,text='µMol/m²/s',font=(dataFont,unitSize),fg=colPAR)
    self.label.grid        (column=8,row=6,sticky=tk.W)
    self.spacer=           tk.Label(self,text=' ')
    self.spacer.grid       (column=8,row=7)
    self.parGraph=         tk.Canvas(self,width=graphX,height=graphY,bg=colBack)
    self.parGraph.grid     (column=9,row=5,padx=spaceX,pady=spaceY,rowspan=3)
    #log window
    self.eventLog=         tk.Text(self,width=60,height=5,bg=colBack)
    self.eventLog.grid     (column=1,row=9,padx=spaceX,pady=spaceY,columnspan=6,rowspan=2)
    self.scrollbar=        tk.Scrollbar(self)
    self.scrollbar.config  (command=self.eventLog.yview)
    self.eventLog.config   (yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid    (column=7,row=9,padx=0,pady=spaceY,sticky=tk.N+tk.S+tk.W)
    #buttons
    self.startButton=      tk.Button(self,text="Stopped",width=10,command=self.startStop,font=("Helvetica", "12"),bg=colOff)
    self.startButton.grid  (column=9,row=9,padx=spaceX,pady=spaceY,sticky=tk.E)
    self.quitButton=       tk.Button(self,text="Quit",width=10,command=self.done,font=("Helvetica", "12"))
    self.quitButton.grid   (column=9,row=10,padx=spaceX,pady=spaceY,sticky=tk.E)
    #spacers
    self.spacer=          tk.Label(self,text=' ')
    self.spacer.grid      (column=0,row=0)
    self.spacer=          tk.Label(self,text=' ')
    self.spacer.grid      (column=0,row=4)
    self.spacer=          tk.Label(self,text=' ')
    self.spacer.grid      (column=0,row=8)
    self.spacer=          tk.Label(self,text=' ')
    self.spacer.grid      (column=10,row=11)

  #- GUI event handling -------------------------------------------------------
    
  def startStop(self):
    if self.scanActive:
      self.scanActive= False
      root.after_cancel(self.scanEvent)
    else:
      self.scanActive= True
      self.update();

  # handle the quit button
  def done(self):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
      if self.scanActive:
        root.after_cancel(self.scanEvent)
      #self.closeLogFile()
      self.quit()

  def update(self):
    # self.scanModbus();
    # self.logWrite();
    if self.scanActive:
      self.startButton.config(text="Running",bg=colOn)
      self.scanEvent= root.after(int(self.config['scanInterval'])*1000,self.update)
    else:
      self.startButton.config(text="Stopped",bg=colOff)

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