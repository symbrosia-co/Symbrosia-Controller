#------------------------------------------------------------------------------
#  Linked Control
#
#  - Perform control with several controllers
#
#  Symbrosia
#  Copyright 2021-2025, all rights reserved
#
# 12May2025 A. Cooper v0.1
#  - initial version
#
#------------------------------------------------------------------------------
verStr= 'LinkedCtrl v0.1'

#-- constants -----------------------------------------------------------------
logFileName= 'Control'
logFilePath= 'log'
libFilePath= 'lib'
cfgFilePath= 'setup'
colBack=     '#BBBBBB'
colDev=      '#999999'
colOn=       '#ADFF8C'
colOff=      '#FFADAD'
colErr=      '#AAAAAA'
verbose=     True;
scanInterval= 1 #time between network scans
logInterval= 60 #time between log file entries
minTime=     10 #minimum time between valve state changes
minPH=      7.5 #minimum allowed pH in any tank

#-- library -------------------------------------------------------------------
import string
import sys
import os
import time
from pathlib import Path
import urllib.request
import datetime as     dt
import tkinter  as     tk
from   tkinter  import ttk, messagebox, filedialog
import xml.etree.ElementTree as xml
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

#-- globals -------------------------------------------------------------------
localDir= os.path.dirname(os.path.realpath(__file__))
logPath=  os.path.join(localDir,logFilePath)
libPath=  os.path.join(localDir,libFilePath)
cfgPath=  os.path.join(localDir,cfgFilePath)

#-- modbus handling ---------------------------------------------------------
def mbStart(ipAddr,port):
  return ModbusClient(host=ipAddr,port=port,unit_id=1,timeout=20,auto_open=False,auto_close=False)

def mbOpen(client):
  if client.is_open()==True:
    client.close()
  return client.open()

def mbClose(client):
  if client.is_open():
    client.close()

def mbRead(client,addr,typ):
  if typ=='int' or typ=='hold':
    val= client.read_holding_registers(addr,1)
    if val!= None: return utils.get_list_2comp(val,16)[0]
    return val
  if typ=='uint':
    val= client.read_holding_registers(addr,1)
    if val!=None: return val[0]
    return None
  if typ=='dint' or typ=='long':
    val= client.read_holding_registers(addr,2)
    if val!=None: return utils.word_list_to_long(val,big_endian=False)[0]
    return val
  if typ=='float':
    val= client.read_holding_registers(addr,2)
    if val!=None: return utils.decode_ieee(utils.word_list_to_long(val,big_endian=False)[0])
    return None
  if typ=='str':
    st= ''
    arry= client.read_holding_registers(addr,8)
    if arry==None: return None
    for chs in arry:
      ch= chs>>8
      if ch==0: return st
      st= st+chr(ch)
      ch= chs&0xFF
      if ch==0: return st
      st= st+chr(ch)
    return st
  if typ=='coil' or typ=='bool':
    val= client.read_coils(addr,1)
    if val!=None: return val[0]
    return None
  return None

def mbWrite(client,addr,data,typ):
  if typ=='int' or typ=='hold':
    if not isinstance(data,int): return False
    if (data & (1<<15))!= 0: data= data-(1<<16)
    if client.write_single_register(addr,data&65535):
      return True
  if typ=='uint':
    if not isinstance(data,int): return False
    if client.write_single_register(addr,data):
      return True
  if typ=='dint' or typ=='long':
    if not isinstance(data,int): return False
    if client.write_multiple_registers(addr,[(data>>16)&0xffff,data&0xffff]):
      return True
  if typ=='float':
    if not isinstance(data,float): return False
    if client.write_multiple_registers(addr,utils.long_list_to_word([utils.encode_ieee(data)],big_endian=False)):
      return True
  if typ=='str':
    if not isinstance(data,str): return False
    arry= []
    for pos in range(8):
      word= 0
      if pos*2<len(data):
        word= ord(data[pos*2])*256
      if pos*2+1<len(data):
        word= word+ord(data[pos*2+1])
      arry.append(word)
    if client.write_multiple_registers(addr,arry):
      return True
  if typ=='bool':
    if not isinstance(data,bool): return False
    if client.write_single_coil(addr,data):
      return True
  return False

#------------------------------------------------------------------------------
#  LinkedCtrl GUI
#
#  - setup the GUI
#
#  12May2025 A. Cooper
#  - initial version
#
#------------------------------------------------------------------------------
class Application(tk.Frame):
  device=       {}
  data=         []
  dataFields=   0
  logFile=      None
  lastLog=      dt.datetime.now()
  eventNow=     dt.datetime.min
  lastChange=   dt.datetime.now()
  control=      False
  mbEvent=      None
  mbActive=     False
  logging=      False
  tankCount=    4
  device= {'carbofox':{'name':'Carbofox','ipAddr':'192.168.0.212','pH':0.0,'Valve':False,'timer':0},
              'tank1':{'name':'X01','ipAddr':'192.168.0.254',     'pH':0.0,'temp':0.0,'co2Valve':False,'tempValve':False},
              'tank2':{'name':'X02','ipAddr':'192.168.0.244',     'pH':0.0,'temp':0.0,'co2Valve':False,'tempValve':False},
              'tank3':{'name':'X03','ipAddr':'192.168.0.3',       'pH':0.0,'temp':0.0,'co2Valve':False,'tempValve':False},
              'tank4':{'name':'X04','ipAddr':'192.168.0.251',     'pH':0.0,'temp':0.0,'co2Valve':False,'tempValve':False}}

  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.grid()
    self.createWidgets()
    for dev in self.device.values():
      dev['ctrl']= mbStart(dev['ipAddr'],502)
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW",self.done)
    self.logEvent('{} started'.format(verStr),True)
    print('{} running...'.format(verStr))
    
  def createWidgets(self):
    spaceX= 5
    spaceY= 5
    # carbofox
    label= tk.Label(self,text=self.device['carbofox']['name'],width=36,anchor=tk.W,font=("Helvetica","12"),bg=colDev)
    label.grid(column=1,row=1,columnspan=3,sticky=tk.E+tk.W)
    label= tk.Label(self,text=self.device['carbofox']['ipAddr'],width=36,anchor=tk.E,font=("Helvetica","12"),bg=colDev)
    label.grid(column=4,row=1,columnspan=3)
    label= tk.Label(self,text='pH',width=12,anchor=tk.E,font=("Helvetica","12"))
    label.grid(column=1,row=2,sticky=tk.W)
    self.device['carbofox']['phDisp']= tk.Label(self,text='-.-',width=10,anchor=tk.W,font=("Helvetica","12"))
    self.device['carbofox']['phDisp'].grid(column=2,row=2)
    label= tk.Label(self,text='  ',width=8,anchor=tk.W,justify=tk.LEFT,font=("Helvetica","12"))
    label.grid(column=3,row=2,sticky=tk.W)
    label= tk.Label(self,text='Timer',width=12,anchor=tk.E,font=("Helvetica","12"))
    label.grid(column=4,row=2,sticky=tk.W)
    self.device['carbofox']['timeDisp']= tk.Label(self,text='--',width=10,anchor=tk.W,font=("Helvetica","12"))
    self.device['carbofox']['timeDisp'].grid(column=5,row=2)
    label= tk.Label(self,text='s',width=8,anchor=tk.W,justify=tk.LEFT,font=("Helvetica","12"))
    label.grid(column=6,row=2,sticky=tk.W)
    # tanks
    row= 3
    for tank in range(1,self.tankCount+1):
      key= 'tank{:d}'.format(tank)
      label= tk.Label(self,text=self.device[key]['name'],width=36,anchor=tk.W,font=("Helvetica","12"),bg=colDev)
      label.grid(column=1,row=row,columnspan=3,sticky=tk.E+tk.W)
      label= tk.Label(self,text=self.device[key]['ipAddr'],width=36,anchor=tk.E,font=("Helvetica","12"),bg=colDev)
      label.grid(column=4,row=row,columnspan=3)
      label= tk.Label(self,text='pH',width=12,anchor=tk.E,font=("Helvetica","12"))
      row+= row
      label.grid(column=1,row=row,sticky=tk.W)
      self.device[key]['phDisp']= tk.Label(self,text='-.-',width=10,anchor=tk.W,font=("Helvetica","12"))
      self.device[key]['phDisp'].grid(column=2,row=row)
      label= tk.Label(self,text='  ',width=8,anchor=tk.W,justify=tk.LEFT,font=("Helvetica","12"))
      label.grid(column=3,row=row,sticky=tk.W)
      label= tk.Label(self,text='Temp',width=12,anchor=tk.E,font=("Helvetica","12"))
      label.grid(column=4,row=row,sticky=tk.W)
      self.device[key]['tempDisp']= tk.Label(self,text='-.-',width=10,anchor=tk.W,font=("Helvetica","12"))
      self.device[key]['tempDisp'].grid(column=5,row=row)
      label= tk.Label(self,text='°C',width=8,anchor=tk.W,justify=tk.LEFT,font=("Helvetica","12"))
      label.grid(column=6,row=row,sticky=tk.W)
      row+= 1
    # log window
    self.eventLog=         tk.Text(self,width=58,height=5,bg=colBack)
    self.eventLog.grid     (column=1,row=row,padx=0,pady=spaceY,columnspan=6,sticky=tk.E+tk.W)
    self.scrollbar=        tk.Scrollbar(self)
    self.scrollbar.config  (command=self.eventLog.yview)
    self.eventLog.config   (yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid    (column=7,row=row,padx=0,pady=spaceY,sticky=tk.N+tk.S+tk.W)
    #buttons
    row+= 1
    self.startButton=      tk.Button(self,text="Stopped",width=10,command=self.startStop,font=("Helvetica", "12"),bg=colOff)
    self.startButton.grid  (column=1,row=row,padx=spaceX,pady=spaceY)
    self.ctrlButton=       tk.Button(self,text="Ctrl Off",width=10,command=self.startControl,font=("Helvetica", "12"),bg=colOff)
    self.ctrlButton.grid   (column=2,row=row,padx=spaceX,pady=spaceY)
    self.logButton=        tk.Button(self,text="No Log",width=10,command=self.startLog,font=("Helvetica", "12"),bg=colOff)
    self.logButton.grid    (column=3,row=row,padx=spaceX,pady=spaceY)
    self.quitButton=       tk.Button(self,text="Quit",width=10,command=self.done,font=("Helvetica", "12"))
    self.quitButton.grid   (column=6,row=row,padx=spaceX,pady=spaceY)
    #spacers
    self.spacer1=          tk.Label(self,text=' ')
    self.spacer1.grid      (column=0,row=1,padx=spaceX,pady=spaceY)
    self.spacer2=          tk.Label(self,text=' ')
    self.spacer2.grid      (column=7,row=row,padx=spaceX,pady=spaceY)

  #- GUI event handling -------------------------------------------------------

  def startStop(self):
    if self.mbActive:
      self.mbActive= False
      root.after_cancel(self.mbEvent)
      self.startButton.config(text="Stopped",bg=colOff)
      self.logButton.config(text="No Log",bg=colOff)
      self.logEvent('Scanning stopped',True)
      self.control= False
      self.ctrlButton.config(text="Ctrl Off",bg=colOff)
      self.logEvent('Control stopped',True)
      self.logging= False
      self.logButton.config(text="No Log",bg=colOff)
      self.logEvent('Logging stopped',True)
    else:
      self.mbActive= True
      self.update();
      self.startButton.config(text="Running",bg=colOn)
      self.logEvent('Scanning started',True)

  def startControl(self):
    if self.control:
      self.control= False
      self.ctrlButton.config(text="Ctrl Off",bg=colOff)
      self.logEvent('Control stopped',True)
    else:
      if self.mbActive:
        self.control= True
        self.ctrlButton.config(text="Ctrl On",bg=colOn)
        self.logEvent('Control started',True)

  def startLog(self):
    if self.logging:
      self.logging= False
      self.logButton.config(text="No Log",bg=colOff)
      self.logEvent('Logging stopped',True)
    else:
      if self.mbActive:
        self.logging= True
        self.logButton.config(text="Logging",bg=colOn)
        self.logEvent('Logging started',True)

  # handle the quit button
  def done(self):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
      if self.mbActive:
        root.after_cancel(self.mbEvent)
      self.quit()

  def update(self):
    self.updateData()
    self.execCtrl()
    self.logTimer()
    if self.mbActive:
      self.mbEvent= root.after(scanInterval*1000,self.update)
      
  #- Control ------------------------------------------------------------------
  
  def execCtrl(self):
    co2On= False
    # control enabled?
    if self.control:
      #ensure good data
      if self.device['tank1']['tempValve']!=None and self.device['tank2']['tempValve']!=None and self.device['tank1']['pH']!=None and self.device['tank2']['pH']!=None:
        # ensure DSW is flowing
        if self.device['tank1']['tempValve'] or self.device['tank2']['tempValve']:
          co2On= True
        # turn off CO2 if any tank is below 7 and its DSW valve is open
        if (self.device['tank1']['pH']<minPH and self.device['tank1']['tempValve']):
          co2On= False
        if (self.device['tank2']['pH']<minPH and self.device['tank2']['tempValve']):
          co2On= False
      else:
        self.logEvent('Missing data! CO2 off',True)
    # check and act on result every minTime second
    now= dt.datetime.now()
    if now-self.lastChange>dt.timedelta(seconds=minTime):
      self.lastChange= now
      mbWrite(self.device['carbofox']['ctrl'],16,co2On,'bool')
    
  def updateData(self):
    # carbofox
    dev= self.device['carbofox']
    if not mbOpen(dev['ctrl']):
      self.logEvent('Cannot open Carbfox',True)
      dev['phDisp'].configure(bg=colErr)
      dev['phDisp'].configure(text='-.--')
      dev['timeDisp'].configure(text='--')
      return
    val= mbRead(dev['ctrl'],12,'bool')
    dev['co2Valve']= val
    if val==True:  dev['phDisp'].configure(bg=colOn)
    elif val==False: dev['phDisp'].configure(bg=colOff)
    else: dev['phDisp'].configure(bg=colErr)
    val= mbRead(dev['ctrl'],20,'float')
    dev['pH']= val
    if val!=None: dev['phDisp'].configure(text='{:.2f}'.format(val))
    else: dev['phDisp'].configure(text='-.--')
    val= mbRead(dev['ctrl'],155,'long')
    dev['timer']= val
    if val!=None: dev['timeDisp'].configure(text='{:d}'.format(val))
    else: dev['timeDisp'].configure(text='--')
    # tank data
    for tank in range(1,self.tankCount+1):
      dev= self.device['tank{:d}'.format(tank)]
      if not mbOpen(dev['ctrl']):
        self.logEvent('Cannot open Tank 1',True)
        dev['phDisp'].configure(text='-.--')
        dev['tempDisp'].configure(text='-.--')
        dev['phDisp'].configure(bg=colErr)
        dev['tempDisp'].configure(bg=colErr)
        return
      val= mbRead(dev['ctrl'],20,'float')
      dev['pH']= val
      if val!=None: dev['phDisp'].configure(text='{:.2f}'.format(val))
      else: dev['phDisp'].configure(text='-.--')
      val= mbRead(dev['ctrl'],22,'float')
      dev['temp']= val
      if val!=None: dev['tempDisp'].configure(text='{:.2f}'.format(val))
      else: dev['tempDisp'].configure(text='-.--')
      val= mbRead(dev['ctrl'],12,'bool')
      dev['co2Valve']= val
      if val==True:  dev['phDisp'].configure(bg=colOn)
      elif val==False: dev['phDisp'].configure(bg=colOff)
      else: dev['phDisp'].configure(bg=colErr)
      val= mbRead(dev['ctrl'],10,'bool')
      dev['tempValve']= val
      if val==True:  dev['tempDisp'].configure(bg=colOn)
      elif val==False: dev['tempDisp'].configure(bg=colOff)
      else: dev['tempDisp'].configure(bg=colErr)

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

  def logTimer(self):
    # check interval
    now= dt.datetime.now()
    if (now-self.lastLog)<dt.timedelta(seconds=logInterval):
      return
    # sync interval to round time units 
    if logInterval%600==0 and now.second!=0 and now.minute!=0:
      return
    if logInterval%60==0 and now.second!=0:
      return
    # if time -> log!
    self.logWrite()
    self.lastLog= now
  
  def logWrite(self):
    now= dt.datetime.now()
    # write log file
    logName= '{}{}.csv'.format(logFileName,now.strftime('%Y%m%d'))
    filePath= os.path.join(logPath,logName)
    # create directory if needed
    Path(logPath).mkdir(parents=True,exist_ok=True)
    # if needed setup new file
    if not os.path.exists(filePath):
      outFile= open(filePath,'w')
      outFile.write('Date, Time, CO2 On, Supply pH, CO2 Timer')
      for tank in range(1,self.tankCount+1):
        key= 'tank{:d}'.format(tank)
        outFile.write(', Tank {0:d} pH, Tank {0:d} Temp, Tank {0:d} Cooling'.format(tank))
      outFile.write('\n')
      self.logEvent('New log file {} created'.format(logName),True)
    else:
      outFile= open(filePath,'a')
    # write data line
    outFile.write('{}, {}'.format(dt.datetime.now().strftime('%Y-%b-%d'),dt.datetime.now().strftime('%H:%M:%S')))
    if self.device['carbofox']['co2Valve']!= None:
      if self.device['carbofox']['co2Valve']:
        outFile.write(',     True')
      else:
        outFile.write(',    False')
    else: outFile.write(',         ')
    if self.device['carbofox']['pH']!= None:
      outFile.write(',{:9.2f}'.format(self.device['carbofox']['pH']))
    else: outFile.write(',         ')
    if self.device['carbofox']['timer']!=None:
      outFile.write(',{:9d}'.format(self.device['carbofox']['timer']))
    else: outFile.write(',         ')
    for tank in range(1,self.tankCount+1):
      key= 'tank{:d}'.format(tank)
      if self.device[key]['pH']!= None:
        outFile.write(',{:9.2f}'.format(self.device[key]['pH']))
      else: outFile.write(',         ')
      if self.device[key]['temp']!=None:
        outFile.write(',{:9.2f}'.format(self.device[key]['temp']))
      else: outFile.write(',         ')
      if self.device[key]['tempValve']!=None:
        if self.device[key]['tempValve']:
          outFile.write(',     True')
        else:
          outFile.write(',    False')
      else: outFile.write(',         ')
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

#-- End MBMon -----------------------------------------------------------------