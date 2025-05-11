#------------------------------------------------------------------------------
#  ModbusTCP Monitor 2
#
#  - Monitor a set of Modbus addresses
#
#  Symbrosia
#  Copyright 2021-2025, all rights reserved
#
# 29Nov2021 A. Cooper v0.1
#  - initial version
# 29Mar2025 A. Cooper v0.2
#  - make data frame scrollable
# 30Apr2025 A. Cooper v0.3
#  - add snapshot button
#  - clean up formatting of data window
#  - autoscale size of data window
# 05May2025 A. Cooper v2.0
#  - create MBMon2 as a major upgrade
#  - use MBScan library to perform subprocess reads of Modbus devices,
#    the decouples the GUI from reading and avoids laggy operation on com
#    errors
#  - better handling of com errors
#  - change color of device bar to indicate com status
#  - remove scan and log buttons, now always on
#  - allow aliases for hold/int and coil/bool
#  - rename subdirectories to match SyView, logs to log, libs to lib
#  - correct some CSV formatting for blank fields
#  - split date and time in CSV file for better compatibility with CSV readers
#  - improved error reporting using messages from MBScan
#  - only report sustained errors every 10 minutes
#  - The configuration tag <precision> can now be <dispPrec> and <logPrec> to
#    specify the number of decimal places used in the display and in the log,
#    <precision> still works if no log or display precision is specified, if
#    none specified two decimal places used
#
#------------------------------------------------------------------------------
verStr= 'MBMon2 v2.0'

#-- constants -----------------------------------------------------------------
cfgFileName=  'MBMon.xml'
logFileName=  'MBMon'
logFilePath=  'log'
libFilePath=  'lib'
cfgFilePath=  'setup'
colBack=      '#BBBBBB'
colDev=       '#999999'
colOn=        '#ADFF8C'
colOff=       '#FFADAD'
verbose=      False;
scanInterval= 2   #subprocess scanning interval in seconds
errorInterval=600 #error message suppression duration in seconds

#-- library -------------------------------------------------------------------
import string
import sys
import os
from pathlib import Path
import time
import urllib.request
import datetime as     dt
import tkinter  as     tk
from   tkinter  import ttk, messagebox, filedialog
import xml.etree.ElementTree as xml

#-- globals -------------------------------------------------------------------
localDir= os.path.dirname(os.path.realpath(__file__))
logPath=  os.path.join(localDir,logFilePath)
libPath=  os.path.join(localDir,libFilePath)
cfgPath=  os.path.join(localDir,cfgFilePath)
sys.path.append(libPath)
from MBScan import MBScanner

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
  dataFields=   0
  logFile=      None
  lastLog=      dt.datetime.now()
  eventNow=     dt.datetime.min

  def __init__(self, master=None):
    print('{} starting...'.format(verStr))
    # get configuration
    if not self.loadConfig(cfgPath,cfgFileName):
      sys.exit()
    #print(self.config)
    # create GUI
    tk.Frame.__init__(self, master)
    self.grid()
    self.createWidgets()
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW",self.done)
    self.logEvent('{} started'.format(verStr),True)
    # spawn subprocesses
    self.devices= MBScanner()
    regs= []
    for device in self.config['devices']:
      for datum in device['data']:
        reg= {'ipAddr':device['ipAddr'],'port':device['port'],'name':datum['name'],'register':int(datum['addr']),'type':datum['type']}
        regs.append(reg)
    self.devices.start(regs,scanInterval)
    #setup complete
    self.mbEvent= root.after(int(self.config['scanInterval'])*500,self.update)
    print('  MBMon2 running...')
 
  def createWidgets(self):
    spaceX= 5
    spaceY= 5
    # scrollable frame for data
    datWinSize= self.dataFields*26
    if datWinSize<100: datWinSize= 100
    if datWinSize>800: datWinSize= 500
    canvas= tk.Canvas(self,width=580,height=datWinSize)
    canvas.grid(column=1,row=1,pady=spaceY,columnspan=4)
    scrollbar= ttk.Scrollbar(self,orient=tk.VERTICAL,command=canvas.yview)
    scrollbar.grid(column=5,row=1,sticky=tk.N+tk.S)
    canvas.configure(yscrollcommand=scrollbar.set)
    frame= ttk.Frame(canvas)
    canvas.create_window((0,0),window=frame,anchor=tk.NW)
    def onMousewheel(event):
      canvas.yview_scroll(int(-1*(event.delta/120)),"units")
    def boundToMousewheel(event):
      canvas.bind_all("<MouseWheel>",onMousewheel)
    def unboundToMousewheel(event):
      canvas.unbind_all("<MouseWheel>")
    def configureScrollRegion(event):
      canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind('<Enter>',boundToMousewheel)
    frame.bind('<Leave>',unboundToMousewheel)
    frame.bind("<Configure>",configureScrollRegion)
    # data fields
    row= 0
    for device in self.config['devices']:
      nameLabel= tk.Label(frame,text=device['name'],width=40,anchor=tk.W,font=("Helvetica","12"),bg=colDev)
      nameLabel.grid(column=0,row=row,columnspan=3,sticky=tk.W)
      ipLabel= tk.Label(frame,text=device['ipAddr'],width=32,justify=tk.RIGHT,font=("Helvetica","12"),bg=colDev)
      ipLabel.grid(column=3,row=row)
      row+= 1
      for dat in device['data']:
        label= tk.Label(frame,text=' ',width=4,font=("Helvetica","10"))
        label.grid(column=0,row=row,pady=2)
        datum= {}
        label= tk.Label(frame,text=dat['name'],width=24,font=("Helvetica","10"))
        label.grid    (column=1,row=row,pady=2,sticky=tk.W)
        datum['ipAddr']=  device['ipAddr']
        datum['port']=    device['port']
        datum['devName']= device['name']
        datum['name']=    dat['name']
        datum['addr']=    dat['addr']
        datum['type']=    dat['type']
        datum['ipLab']=   ipLabel
        datum['nameLab']= nameLabel
        datum['lastErr']= dt.datetime.now()-dt.timedelta(seconds=errorInterval)
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
        label.grid(column=2,row=row,sticky=tk.E)
        datum['valueDisp']= label
        if 'unit' in dat:
          label= tk.Label(frame,text=dat['unit'],width=10,anchor=tk.W,font=("Helvetica","10"))
          label.grid(column=3,row=row,sticky=tk.W)
        row+= 1
        self.data.append(datum)
    # log window
    self.eventLog=         tk.Text(self,width=72,height=5,bg=colBack)
    self.eventLog.grid     (column=1,row=2,padx=0,pady=spaceY,columnspan=4,sticky=tk.E+tk.W)
    self.scrollbar=        tk.Scrollbar(self)
    self.scrollbar.config  (command=self.eventLog.yview)
    self.eventLog.config   (yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid    (column=5,row=2,padx=0,pady=spaceY,sticky=tk.N+tk.S+tk.W)
    #buttons
    self.quitButton=       tk.Button(self,text="Quit",width=10,command=self.done,font=("Helvetica", "12"))
    self.quitButton.grid   (column=4,row=3,padx=spaceX,pady=spaceY)
    #spacers
    self.spacer1=          tk.Label(self,text=' ')
    self.spacer1.grid      (column=0,row=1,padx=spaceX,pady=spaceY)
    self.spacer2=          tk.Label(self,text=' ')
    self.spacer2.grid      (column=6,row=3,padx=spaceX,pady=spaceY)

  def loadConfig(self,configPath,configFile):
    try:
      tree = xml.parse(os.path.join(configPath,configFile))
    except:
      messagebox.showerror(title='Startup error...',message='Unable to load configuration file {}\{}'.format(configPath,configFile))
      return False
    #process XML
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
            self.dataFields+= 1
          else:
            device[dev.tag]= dev.text
        self.config['devices'].append(device)
        self.dataFields+= 1
      else:
        self.config[item.tag]= item.text
    return True

  #- GUI event handling -------------------------------------------------------

  # handle the quit button
  def done(self):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
      self.logEvent('Shutting down...',True)
      self.update_idletasks()
      root.after_cancel(self.mbEvent)
      self.devices.close()
      self.quit()

  def update(self):
    self.scanData();
    self.logTimer();
    self.mbEvent= root.after(int(self.config['scanInterval'])*500,self.update)
    
  #- Data Handing -------------------------------------------------------------

  def scanData(self):
    for datum in self.data:
      val= self.devices.get(datum['ipAddr'],datum['name'])
      if not self.devices.error:
        datum['value']= val
        if datum['type']=='float':
          prec= 2
          if 'precision' in datum: prec= datum['precision']
          if 'dispPrec' in datum: prec= datum['dispPrec']
          datum['valueDisp'].config(text='{0:.{1}f}'.format(val,prec))
        if datum['type']=='hold' or datum['type']=='long' or datum['type']=='int' or datum['type']=='uint':
          datum['valueDisp'].config(text='{:d}'.format(val))
        if datum['type']=='coil' or datum['type']=='bool':
          if val:
            datum['valueDisp'].config(text='On')
          else:
            datum['valueDisp'].config(text='Off')
        datum['ipLab'].config(bg=colOn)
        datum['nameLab'].config(bg=colOn)
      else:
        if dt.datetime.now()-datum['lastErr']>dt.timedelta(seconds=errorInterval):
          datum['lastErr']= dt.datetime.now()
          self.logEvent('Error! {}'.format(self.devices.errText),True)
        datum['value']= None
        datum['valueDisp'].config(text='---')
        datum['ipLab'].config(bg=colOff)
        datum['nameLab'].config(bg=colOff)

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
    self.eventLog.insert(tk.END,event[:52]+'\n')
    self.eventLog.see(tk.END)

  def clearEvents(self):
    self.eventLog.delete('1.0',tk.END)

  #- Log File -----------------------------------------------------------------

  def logTimer(self):
    # constrain interval
    interval= int(self.config['logInterval'])
    if interval<10: interval=10
    if interval>3600: interval= 3600
    # check interval
    now= dt.datetime.now()
    if (now-self.lastLog)<dt.timedelta(seconds=interval):
      return
    # sync interval to round time units 
    if interval%600==0 and now.second!=0 and now.minute!=0:
      return
    if interval%60==0 and now.second!=0:
      return
    # if time -> log!
    self.logWrite()
    self.lastLog= now
  
  def logWrite(self):
    now= dt.datetime.now()
    # check for directory
    Path(logPath).mkdir(parents=True,exist_ok=True)
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
      outFile.write('Date, Time')
      for datum in self.data:
        if datum['log']:
          outFile.write(', {} {}'.format(datum['devName'],datum['name']))
      outFile.write('\n')
      self.logEvent('New log file {} created'.format(logName),True)
    else:
      outFile= open(filePath,'a')
    # write data line
    outFile.write('{}'.format(dt.datetime.now().strftime('%Y-%b-%d, %H:%M:%S')))
    for datum in self.data:
      if verbose: print(datum['name'],datum['value'])
      if datum['log']:
        if datum['value']==None:
          outFile.write(',         ')
        else:
          if datum['type']=='float':
            prec= 2
            if 'precision' in datum: prec= datum['precision']
            if 'logPrec' in datum: prec= datum['logPrec']
            outFile.write(',{0:10.{1}f}'.format(datum['value'],prec))
          if datum['type']=='hold' or datum['type']=='int' or datum['type']=='uint' or datum['type']=='long':
            outFile.write(',{:10d}'.format(int(datum['value'])))
          if datum['type']=='coil' or datum['type']=='bool':
            if datum['value']:
              outFile.write(',      True')
            else:
              outFile.write(',     False')
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
if __name__=='__main__':
  root= tk.Tk()
  app= Application(master=root)
  app.master.title(verStr)
  root.protocol("WM_DELETE_WINDOW",app.done)
  app.mainloop()
  root.destroy()

#-- End MBMon -----------------------------------------------------------------