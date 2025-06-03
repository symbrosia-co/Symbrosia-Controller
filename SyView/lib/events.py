#------------------------------------------------------------------------------
#  SyView events
#
#  - Handle the events tab
#
#  1Jul2022 A. Cooper
#  - initial version
#  29May2025 v2.0 A. Cooper
#  - replace SymCtrlModbus with SymbCtrlScan, a subprocess based comm handler
#  - alterations all through code to support new controller handler
#
#-- includes ------------------------------------------------------------------
import tkinter as tk
import datetime as dt
from tkinter import ttk, messagebox

# -- constants ----------------------------------------------------------------
colBack= '#BBBBBB'

#------------------------------------------------------------------------------
#  Events Tab
#
#  - handle the events tab
#
#------------------------------------------------------------------------------
class Events(tk.Frame):
  eventLast= dt.datetime.min
  delegates= []

  def __init__(self, parent):
    tk.Frame.__init__(self, master=parent)
    self.grid()
    self.createWidgets()

  def createWidgets(self):
    self.eventLog=         tk.Text(self,width=85,height=18,bg=colBack)
    self.eventLog.grid     (column=1,row=0,padx=0,pady=8,sticky=tk.E+tk.W)
    self.scrollbar=        tk.Scrollbar(self)
    self.scrollbar.config  (command=self.eventLog.yview)
    self.eventLog.config   (yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid    (column=2,row=0,padx=0,pady=8,sticky=tk.N+tk.S+tk.W)
    # spacers
    self.spacer1= tk.Label(self,text=' ')
    self.spacer1.grid (column=0,row=0)

  #external methods
  def setDelegates(self,funcs):
    self.delegates= funcs  

  def update(self,event):
    pass

  def log(self,event,incDate):
    if (dt.datetime.now()-self.eventLast)>dt.timedelta(seconds=2):
      self.eventLog.insert(tk.END,'{:%Y%b%d %H:%M:%S} '.format(dt.datetime.now()))
    else:
      self.eventLog.insert(tk.END,'                   ')
    self.eventLog.insert(tk.END,event+'\n')
    self.eventLog.see(tk.END)
    self.eventLast= dt.datetime.now()

  def save(self,event):
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

#-- End events.py -------------------------------------------------------------
