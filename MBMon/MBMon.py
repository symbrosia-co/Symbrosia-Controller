#------------------------------------------------------------------------------
#  ModbusTCP Monitor
#
#  - Monitor a set of Modbus addresses
#
#  Symbrosia
#  Copyright 2021-2025, all rights reserved
#
# 29Nov2021 A. Cooper v0.1
#  - initial version
# 29Nov2025 A. Cooper v0.2
#  - make data frame scrollable
#
#------------------------------------------------------------------------------
verStr= 'MBMon v0.2'

#-- constants -----------------------------------------------------------------
cfgFileName= 'MBMon.xml'
logFileName= 'MBMon'
logFilePath= 'logs'
cfgFilePath= 'setup'
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
logPath=  os.path.join(localDir,logFilePath)
cfgPath=  os.path.join(localDir,cfgFilePath)

#------------------------------------------------------------------------------
#  MBMon GUI
#
#  - setup the GUI
#
#  29Nov2021 A. Cooper
#  - initial version
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
    if not self.loadConfig(cfgPath,cfgFileName):
      sys.exit()
    # print(self.config)
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
    # scrollable frame for data
    canvas= tk.Canvas(self,width=600,height=400)
    canvas.grid(column=1,row=1,columnspan=5)
    scrollbar= ttk.Scrollbar(self,orient=tk.VERTICAL,command=canvas.yview)
    scrollbar.grid(column=6,row=1,sticky=tk.N+tk.S)
    canvas.configure(yscrollcommand=scrollbar.set)
    frame= ttk.Frame(canvas)
    canvas.create_window((0,0),window=frame,anchor=tk.NW)
    def configure_scroll_region(event):
      canvas.configure(scrollregion=canvas.bbox("all"))
    def on_mousewheel(event):
      canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    frame.bind("<Configure>",configure_scroll_region)
    canvas.bind_all("<MouseWheel>",on_mousewheel)
    # data fields
    row= 0
    for device in self.config['devices']:
      label= tk.Label(frame,text=device['name'],width=46,anchor=tk.W,font=("Helvetica","12"),bg=colDev)
      label.grid(column=0,row=row,columnspan=3,sticky=tk.W)
      label= tk.Label(frame,text=device['ipAddr'],width=20,anchor=tk.E,font=("Helvetica","12"),bg=colDev)
      label.grid(column=3,row=row,columnspan=2,sticky=tk.W)
      row+= 1
      for dat in device['data']:
        label= tk.Label(frame,text=' ',width=4,font=("Helvetica","10"))
        label.grid    (column=0,row=row,pady=spaceY,sticky=tk.E)
        datum= {}
        label= tk.Label(frame,text=dat['name'],width=32,font=("Helvetica","10"))
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
        label= tk.Label(frame,text='---',width=10,font=("Helvetica","12"))
        label.grid(column=1,row=row,sticky=tk.E)
        datum['valueDisp']= label
        if 'unit' in dat:
          label= tk.Label(frame,text=dat['unit'],width=10,anchor=tk.W,font=("Helvetica","10"))
          label.grid(column=2,row=row,sticky=tk.W)
        if 'write' in dat:
          button=  tk.Button(frame,text='Write',width=10,command=self.write,font=("Helvetica", "12"))
          button.grid(column=4,row=row)
          datum['button']=  button
          datum['write']=   True
        row+= 1
        self.data.append(datum)
    # log window
    self.eventLog=         tk.Text(self,width=80,height=5,bg=colBack)
    self.eventLog.grid     (column=1,row=2,padx=0,pady=spaceY,columnspan=5,sticky=tk.E+tk.W)
    self.scrollbar=        tk.Scrollbar(self)
    self.scrollbar.config  (command=self.eventLog.yview)
    self.eventLog.config   (yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid    (column=6,row=2,padx=0,pady=8,sticky=tk.N+tk.S+tk.W)
    #buttons
    self.startButton=      tk.Button(self,text="Stopped",width=10,command=self.startStop,font=("Helvetica", "12"),bg=colOff)
    self.startButton.grid  (column=1,row=3,padx=spaceX,pady=spaceY)
    self.logButton=        tk.Button(self,text="No Log",width=10,command=self.startLog,font=("Helvetica", "12"),bg=colOff)
    self.logButton.grid    (column=2,row=3,padx=spaceX,pady=spaceY)
    self.quitButton=       tk.Button(self,text="Quit",width=10,command=self.done,font=("Helvetica", "12"))
    self.quitButton.grid   (column=5,row=3,padx=spaceX,pady=spaceY)
    #spacers
    self.spacer1=          tk.Label(self,text=' ')
    self.spacer1.grid      (column=0,row=0)
    self.spacer2=          tk.Label(self,text=' ')
    self.spacer2.grid      (column=3,row=4)

  def loadConfig(self,configPath,configFile):
    #try:
    tree = xml.parse(os.path.join(configPath,configFile))
    #except:
    #  messagebox.showerror(title='Startup error...',message='Unable to load configuration file {}\{}'.format(configPath,configFile))
    #  return False
    #process top level
    self.config['devices']= []
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
        self.config['devices'].append(device)
      else:
        self.config[item.tag]= item.text
    return True

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

  #- Modbus -------------------------------------------------------------------

  def mbOpen(self,device,ipAddr,port):
    if self.device.is_open():
      self.device.close()
    self.device.timeout(timeout=5)
    if not self.device.host(ipAddr):
      self.logEvent('Unable to set IP address {}@{}'.format(device,ipAddr),True)
      return False
    if not self.device.port(port):
      self.logEvent('Unable to set IP port {}@{}:{}'.format(device@ipAddr,port),True)
      return False
    if not self.device.open():
      self.logEvent('Unable to open device {}@{}:{}'.format(device,ipAddr,port),True)
      return False
    return True
    
  def mbClose(self):
    if self.device.is_open():
      self.device.close()
    
  def mbRead(self,device,name,mbAddr,varType):
    if not self.device.is_open():
      self.logEvent('Modbus device {} not open for reading!!'.format(device),True)
      return None
    try:
      mbAddr= int(mbAddr)
    except:
      return None
    if verbose: print ('Attempt read of {}:{}:{:d} as {}...'.format(device,name,mbAddr,varType))
    if varType=='float':
      val= self.device.read_holding_registers(mbAddr,2)
      if val==None:
        if verbose: print ('  No data returned')
        self.logEvent('No data returned from {}:{:d} - {}!!'.format(device,mbAddr,name),True)
        return None
      else:
        val= utils.word_list_to_long(val,big_endian=False)
        val= utils.decode_ieee(val[0])
        return val
    if varType=='hold':
      val= self.device.read_holding_registers(mbAddr,1)
      if val==None:
        if verbose: print ('  No data returned')
        self.logEvent('No data returned from {}:{:d} - {}!!'.format(device,mbAddr,name),True)
        return None
      else:
        return val[0]
    if varType=='long':
      valL= self.device.read_holding_registers(mbAddr,1)
      valH= self.device.read_holding_registers(mbAddr+1,1)
      if valL!=None and valH!= None:
        val= valL[0]+valH[0]*65536
        return val
      else:
        if verbose: print ('  No data returned')
        self.logEvent('No data returned from {}:{:d} - {}!!'.format(device,mbAddr,name),True)
        return None
      return val
    if varType=='coil':
      val= self.device.read_coils(mbAddr,1)
      if val==None:
        if verbose: print ('  No data returned')
        self.logEvent('No data returned from {}:{:d} - {}!!'.format(device,mbAddr,name),True)
        return None
      else:
        if val[0]==1:
          return True
        else:
          return False
    if varType=='discrete':
      # if mbAddr<10000 or mbAddr>19999:
        # self.logEvent('Bad modbus address {}:{:d} for discrete!!'.format(name,mbAddr),True)
        # return False
      val= self.device.read_discrete_inputs(mbAddr,1)
      if val==None:
        if verbose: print ('  No data returned')
        self.logEvent('No data returned from {}:{:d} - {}!!'.format(device,mbAddr,name),True)
        return None
      else:
        if val[0]==1:
          return True
        else:
          return False
    if varType=='input':
      # if mbAddr<30000 or mbAddr>39999:
        # self.logEvent('Bad modbus address {}:{:d} for input!!'.format(name,mbAddr),True)
        # return False
      val= self.device.read_input_registers(mbAddr,1)
      if val==None:
        if verbose: print ('  No data returned')
        self.logEvent('No data returned from {}:{:d} - {}!!'.format(device,mbAddr,name),True)
        return None
      else:
        return val[0]

  def scanModbus(self):
    ip= None
    for datum in self.data:
      if ip==None or ip!=datum['ipAddr']:
        ip= datum['ipAddr']
        if not self.mbOpen(datum['name'],ip,datum['port']):
          ip= None
          continue
      if ip!=datum['ipAddr']:
        self.mbClose()
        if not self.mbOpen(datum['name'],ip,datum['port']):
          ip= None
          continue
        ip=datum['ipAddr']
      result= self.mbRead(datum['devName'],datum['name'],datum['addr'],datum['type'])
      if result==None:
        datum['value']= None
        datum['valueDisp'].config(text='---')
      else:
        if datum['type']=='float':
          val= float(result)
          datum['valueDisp'].config(text='{0:.{1}f}'.format(val,datum['prec']))
          datum['value']= val
        if datum['type']=='hold' or datum['type']=='long':
          val= int(result)
          datum['valueDisp'].config(text='{:d}'.format(val))
          datum['value']= val
        if datum['type']=='coil':
          if result:
            datum['valueDisp'].config(text='On')
          else:
            datum['valueDisp'].config(text='Off')
          datum['value']= result
    self.mbClose()

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