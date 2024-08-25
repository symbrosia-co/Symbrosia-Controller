#------------------------------------------------------------------------------
#  SyView status
#
#  - Handle the status tab
#
#  1Jul2022 A. Cooper
#  - initial version

#-- includes ------------------------------------------------------------------
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from functools import partial

#-- globals -------------------------------------------------------------------
localDir= os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
imgPath=  os.path.join(localDir,'img')

# -- constants ----------------------------------------------------------------
sendArrowFile=      'sendArrow.png'
onSwitchFile=       'switchOn.png'
offSwitchFile=      'switchOff.png'
onIndicatorFile=    'indicatorOn.png'
offIndicatorFile=   'indicatorOff.png'
trueIndicatorFile=  'indicatorTrue.png'
falseIndicatorFile= 'indicatorFalse.png'
setButtonFile=      'setButton.png'
spacerFile=         'spacer.png'
colGood=            '#000000'
colBad=             '#FFADAD'

#------------------------------------------------------------------------------
#  Status Tab
#
#  - handle the status tab
#
#------------------------------------------------------------------------------
class Status(tk.Frame):
  widgets= [{'reg':'ControlName',   'form':'label', 'conf':False,'col':1,'row':1, 'span':2,'width':16,'font':3,'just':'l','conf':False,'value':'Controller'     },
            {'reg':'ControlName',   'form':'entry', 'conf':False,'col':1,'row':2, 'span':1,'width':16,'font':1,'just':'w','conf':False,'value':None             },
            {'reg':'ControlName',   'form':'send',  'conf':False,'col':2,'row':2, 'span':1,'width':24,'font':1,'just':'l','conf':False,'value':None             },
            {'reg':'ModelName',     'form':'label', 'conf':False,'col':1,'row':3, 'span':1,'width':13,'font':1,'just':'l','conf':False,'value':None             },
            {'reg':'ControlName',   'form':'name',  'conf':False,'col':4,'row':1, 'span':2,'width':16,'font':3,'just':'l','conf':False,'value':'Stat'           },
            {'reg':'Time',          'form':'time',  'conf':False,'col':5,'row':1, 'span':1,'width':8, 'font':3,'just':'c','conf':False,'value':'00:00:00'       },
            {'reg':'StatusDisp1',   'form':'read',  'conf':False,'col':4,'row':2, 'span':1,'width':8, 'font':3,'just':'c','conf':False,'value':'--'            },
            {'reg':'StatusDisp2',   'form':'read',  'conf':False,'col':5,'row':2, 'span':1,'width':8, 'font':3,'just':'c','conf':False,'value':'--'            },
            {'reg':None,            'form':'label', 'conf':False,'col':4,'row':5, 'span':1,'width':13,'font':1,'just':'l','conf':False,'value':'Time Zone'      },
            {'reg':'TimeZone',      'form':'int',   'conf':False,'col':5,'row':3, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'TimeZone',      'form':'entry', 'conf':False,'col':4,'row':4, 'span':1,'width':6, 'font':1,'just':'w','conf':False,'value':None             },
            {'reg':'TimeZone',      'form':'send',  'conf':False,'col':5,'row':4, 'span':1,'width':24,'font':1,'just':'l','conf':False,'value':None             },
            # column 1
            {'reg':None,            'form':'label', 'conf':False,'col':1,'row':4, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Serial'         },
            {'reg':None,            'form':'label', 'conf':False,'col':1,'row':5, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Firmware'       },
            {'reg':None,            'form':'label', 'conf':False,'col':1,'row':6, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Status'         },
            {'reg':None,            'form':'label', 'conf':False,'col':1,'row':7, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Status Code'    },
            {'reg':None,            'form':'label', 'conf':False,'col':1,'row':8, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'NTP Valid'      },
            {'reg':None,            'form':'label', 'conf':False,'col':1,'row':9, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Startup'        },
            {'reg':None,            'form':'label', 'conf':False,'col':1,'row':11,'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Heartbeat In'   },
            {'reg':None,            'form':'label', 'conf':False,'col':1,'row':12,'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Heartbeat Out'  },
            # column 2
            {'reg':'SerialNumber',  'form':'int',   'conf':False,'col':2,'row':4, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'FirmwareRev',   'form':'rev',   'conf':False,'col':2,'row':5, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'Status',        'form':'indtf', 'conf':False,'col':2,'row':6, 'span':1,'width':48,'font':0,'just':'c','conf':False,'value':None             },
            {'reg':'StatusCode',    'form':'int',   'conf':False,'col':2,'row':7, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'NTPTimeValid',  'form':'indtf', 'conf':False,'col':2,'row':8, 'span':1,'width':48,'font':0,'just':'c','conf':False,'value':None             },
            {'reg':'Startup',       'form':'indoo', 'conf':False,'col':2,'row':9, 'span':1,'width':48,'font':0,'just':'c','conf':False,'value':None             },
            {'reg':'HeartbeatIn',   'form':'int',   'conf':False,'col':2,'row':11,'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'HeartbeatOut',  'form':'int',   'conf':False,'col':2,'row':12,'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            # column 3
            # column 4
            {'reg':None,            'form':'label', 'conf':False,'col':4,'row':6, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Silence Alarms' },
            {'reg':None,            'form':'label', 'conf':False,'col':4,'row':7, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Midnight Save'  },
            {'reg':None,            'form':'label', 'conf':False,'col':4,'row':8, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Midnight Reboot'},
            {'reg':None,            'form':'label', 'conf':False,'col':4,'row':10,'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Save Settings'  },
            {'reg':None,            'form':'label', 'conf':False,'col':4,'row':11,'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Clear Settings' },
            {'reg':None,            'form':'label', 'conf':False,'col':4,'row':12,'span':1,'width':13,'font':1,'just':'l','conf':False,'value':'Display'        },
            {'reg':'StatusDisp1',   'form':'achan', 'conf':False,'col':4,'row':13,'span':2,'width':32,'font':1,'just':'l','value':None                          },
            {'reg':'StatusDisp2',   'form':'achan', 'conf':False,'col':4,'row':14,'span':2,'width':32,'font':1,'just':'l','value':None                          },
            # column 5
            {'reg':'SilenceAlarms', 'form':'switch','conf':True ,'col':5,'row':6, 'span':1,'width':48,'font':0,'just':'r','conf':False,'value':None             },
            {'reg':'MidnightSave',  'form':'switch','conf':True ,'col':5,'row':7, 'span':1,'width':48,'font':0,'just':'r','conf':False,'value':None             },
            {'reg':'MidnightReset', 'form':'switch','conf':True ,'col':5,'row':8, 'span':1,'width':48,'font':0,'just':'r','conf':False,'value':None             },
            {'reg':'SaveSettings',  'form':'button','conf':True ,'col':5,'row':10,'span':1,'width':48,'font':0,'just':'r','conf':True, 'value':None             },
            {'reg':'ClearSettings', 'form':'button','conf':True ,'col':5,'row':11,'span':1,'width':48,'font':0,'just':'r','conf':True, 'value':None             },
            # column 6
            # column 7
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':3, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Water Quality'  },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':4, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Temperature 1'  },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':5, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Temperature 2'  },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':6, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Analog 1'       },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':7, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Analog 2'       },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':8, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Internal Temp'  },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':9, 'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Supply'         },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':10,'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Processed'      },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':11,'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Relay 1'        },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':12,'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Relay 2'        },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':13,'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Digital Out 1'  },
            {'reg':None,            'form':'label', 'conf':False,'col':7,'row':14,'span':1,'width':13,'font':1,'just':'r','conf':False,'value':'Digital Out 2'  },
            # column 8
            {'reg':'WQSensor',      'form':'float', 'conf':False,'col':8,'row':3, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'Temperature1',  'form':'float', 'conf':False,'col':8,'row':4, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'Temperature2',  'form':'float', 'conf':False,'col':8,'row':5, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'Analog1',       'form':'float', 'conf':False,'col':8,'row':6, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'Analog2',       'form':'float', 'conf':False,'col':8,'row':7, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'InternalTemp',  'form':'float', 'conf':False,'col':8,'row':8, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'SupplyVoltage', 'form':'float', 'conf':False,'col':8,'row':9, 'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'ProcessedData', 'form':'float', 'conf':False,'col':8,'row':10,'span':1,'width':10,'font':2,'just':'c','conf':False,'value':None             },
            {'reg':'Relay1Status',  'form':'indoo', 'conf':False,'col':8,'row':11,'span':1,'width':48,'font':0,'just':'c','conf':False,'value':None             },
            {'reg':'Relay2Status',  'form':'indoo', 'conf':False,'col':8,'row':12,'span':1,'width':48,'font':0,'just':'c','conf':False,'value':None             },
            {'reg':'DigitalOut1',   'form':'indoo', 'conf':False,'col':8,'row':13,'span':1,'width':48,'font':0,'just':'c','conf':False,'value':None             },
            {'reg':'DigitalOut2',   'form':'indoo', 'conf':False,'col':8,'row':14,'span':1,'width':48,'font':0,'just':'c','conf':False,'value':None             },
            # column 9
            {'reg':'WQSensorUnits', 'form':'unitd', 'conf':False,'col':9,'row':3, 'span':1,'width':10,'font':1,'just':'l','conf':False,'value':None             },
            {'reg':'Temp1Units',    'form':'unitd', 'conf':False,'col':9,'row':4, 'span':1,'width':10,'font':1,'just':'l','conf':False,'value':None             },
            {'reg':'Temp2Units',    'form':'unitd', 'conf':False,'col':9,'row':5, 'span':1,'width':10,'font':1,'just':'l','conf':False,'value':None             },
            {'reg':'Analog1Units',  'form':'unitd', 'conf':False,'col':9,'row':6, 'span':1,'width':10,'font':1,'just':'l','conf':False,'value':None             },
            {'reg':'Analog1Units',  'form':'unitd', 'conf':False,'col':9,'row':7, 'span':1,'width':10,'font':1,'just':'l','conf':False,'value':None             },
            {'reg':'LocalTempUnits','form':'unitd', 'conf':False,'col':9,'row':8, 'span':1,'width':10,'font':1,'just':'l','conf':False,'value':None             },
            {'reg':'SupVoltUnits',  'form':'unitd', 'conf':False,'col':9,'row':9, 'span':1,'width':10,'font':1,'just':'l','conf':False,'value':None             },
            {'reg':'ProcUnits',     'form':'unitd', 'conf':False,'col':9,'row':10,'span':1,'width':10,'font':1,'just':'l','conf':False,'value':None             }]
  anlgChan= {'None':0,'WQ Amplifier':1,'Temperature 1':2,'Temperature 2':3,'Analog 1':4,'Analog 2':5,'Internal Temp':6,'Supply Voltage':7,'Processed':8}
  anlgName= {0:None,1:'WQSensor',2:'Temperature1',3:'Temperature2',4:'Analog1',5:'Analog2',6:'InternalTemp',7:'SupplyVoltage',8:'Processed'}
  anlgUnit= {0:None,1:'WQSensorUnits',2:'Temp1Units',3:'Temp2Units',4:'Analog1Units',5:'Analog2Units',6:'IntTempUnits',7:'SupVoltUnits',8:'ProcUnits'}


  def __init__(self,parent,controller):
    tk.Frame.__init__(self,master=parent)
    self.controller= controller
    self.grid()  
    self.createWidgets()

  def createWidgets(self):
    padX= 4
    padY= 2
    # images for the buttons
    self.sendArrow=      tk.PhotoImage(file=os.path.join(localDir,'img',sendArrowFile))
    self.onSwitch=       tk.PhotoImage(file=os.path.join(localDir,'img',onSwitchFile))
    self.offSwitch=      tk.PhotoImage(file=os.path.join(localDir,'img',offSwitchFile))
    self.onIndicator=    tk.PhotoImage(file=os.path.join(localDir,'img',onIndicatorFile))
    self.offIndicator=   tk.PhotoImage(file=os.path.join(localDir,'img',offIndicatorFile))
    self.trueIndicator=  tk.PhotoImage(file=os.path.join(localDir,'img',trueIndicatorFile))
    self.falseIndicator= tk.PhotoImage(file=os.path.join(localDir,'img',falseIndicatorFile))
    self.setButton=      tk.PhotoImage(file=os.path.join(localDir,'img',setButtonFile))
    self.spacerButton=   tk.PhotoImage(file=os.path.join(localDir,'img',spacerFile))
    #place widgets
    for wid in self.widgets:
      newWid= None
      if wid['form']=='label':
        newWid= tk.Label(self,text=wid['value'],width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY)
      if wid['form']=='name' or wid['form']=='time' or wid['form']=='read':
        newWid= tk.Label(self,text=wid['value'],width=wid['width'],bg='#3050A0', fg='#FFFFFF')
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=0,pady=0,sticky=tk.NSEW)
      if wid['form'] in ['int','float','rev','unitd']:
        newWid= tk.Label(self,text=wid['value'],width=wid['width'],state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY)
      if wid['form']=='indoo':
        newWid= tk.Button(self,image=self.offIndicator,height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],padx=padX,pady=padY)
      if wid['form']=='indtf':
        newWid= tk.Button(self,image=self.falseIndicator,height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],padx=padX,pady=padY)
      if wid['form']=='switch':
        newWid= tk.Button(self,image=self.offSwitch,command=partial(self.set,wid['reg']),height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],padx=padX,pady=padY)
      if wid['form']=='button':
        newWid= tk.Button(self,image=self.setButton,command=partial(self.set,wid['reg']),height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],padx=padX,pady=padY)
      if wid['form']=='entry':
        newStr= tk.StringVar()
        newWid= tk.Entry(self,textvariable=newStr,width=wid['width'],state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],padx=padX,pady=padY)
        wid['entry']= newStr
      if wid['form']=='send':
        newWid= tk.Button(self,command=partial(self.set,wid['reg']),image=self.sendArrow,height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],padx=padX,pady=padY)
      if wid['form']=='achan':
        newStr= tk.StringVar()
        newStr.set(list(self.anlgChan.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*self.anlgChan,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=padX,row=wid['row'],pady=padY,sticky=tk.W+tk.E)
        wid['entry']= newStr
      if newWid!= None:
        if wid['font']==1:   newWid.configure(font=('Helvetica','10'))
        if wid['font']==2:   newWid.configure(font=('Helvetica','10','bold'))
        if wid['font']==3:   newWid.configure(font=('Helvetica','12','bold'))
        if wid['just']=='r': newWid.configure(anchor=tk.E,justify=tk.RIGHT)
        if wid['just']=='f': newWid.configure(justify=tk.RIGHT)
        if wid['just']=='l': newWid.configure(anchor=tk.W,justify=tk.LEFT)
        if wid['just']=='w': newWid.configure(justify=tk.LEFT)
        wid['widget']= newWid
    # top corner spacer
    spacer= tk.Label(self,image=self.spacerButton,width=20)
    spacer.grid (column=0,row=0)
    
  def set(self,reg):
    if self.controller.connected():
      for wid in self.widgets:
        if wid['reg']==reg:
          if wid['form']=='switch':
            if wid['value']:
              wid['value']= False
              wid['widget'].configure(image=self.offSwitch)
            else:
              wid['value']= True
              wid['widget'].configure(image=self.onSwitch)
            self.controller.write(reg,wid['value'])
            self.delegates['EventLog']('{} set {}'.format(reg,wid['value']),True)
          if wid['form']=='button':
            if messagebox.askyesno(title='Are you sure?', message='Are you sure you wish to '+self.controller.description(wid['reg']),default='no'):
              if self.controller.write(reg,True):
                self.delegates['EventLog']('{} requested'.format(reg),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
          if wid['form']=='send':
            valid= False
            for w in self.widgets:
              if w['reg']==reg and w['form']=='entry':
                if self.controller.type(reg)=='float':
                  try: value= float(w['widget'].get())
                  except:
                    self.delegates['EventLog']('Write error to {}! Improper value'.format(reg),True)
                  else:
                    valid= True
                if self.controller.type(reg)=='int':
                  try: value= int(w['widget'].get())
                  except:
                    self.delegates['EventLog']('Write error to {}! Improper value'.format(reg),True)
                  else:
                    valid= True
                if self.controller.type(reg)=='uint':
                  try: value= int(w['widget'].get())
                  except:
                    self.delegates['EventLog']('Write error to {}! Improper value'.format(reg),True)
                  else:
                    if value>=0:
                      valid= True
                    else:
                      self.delegates['EventLog']('Write error to {}! Improper value'.format(reg),True)
                if self.controller.type(reg)=='str':
                  value= w['widget'].get()[:16].strip()
                  valid= True
            if valid:
              wid['value']= value
              if self.controller.write(reg,wid['value']):
                self.delegates['EventLog']('{} set to {}'.format(reg,wid['value']),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)

  def setMenu(self,reg,selection):
    if self.controller.connected():
      for wid in self.widgets:
        if wid['reg']==reg:
          if wid['form']=='achan':
            if self.controller.write(reg,self.anlgChan[selection]):
              self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
            for w in self.widgets:
              if w['form']=='input':
                w['reg']= self.anlgName[self.anlgChan[selection]]
              if w['form']=='unitin':
                w['reg']= self.anlgUnit[self.anlgChan[selection]]

  #-- external methods --------------------------------------------------------
  def setDelegates(self,funcList):
    self.delegates= funcList
  def update(self):
    for wid in self.widgets:
      if wid['form']=='int':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if isinstance(wid['value'],int):
            wid['widget'].configure(text='{:d}'.format(wid['value']),state=tk.NORMAL)
        else:
          wid['widget'].configure(text='--',state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='rev':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if isinstance(wid['value'],int):
            wid['widget'].configure(text='{:d}.{:d}'.format(wid['value'] >> 8,wid['value'] & 0xFF),state=tk.NORMAL)
        else:
          wid['widget'].configure(text='-.-',state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='float':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if isinstance(wid['value'],float):
            wid['widget'].configure(text='{:.2f}'.format(wid['value']),state=tk.NORMAL)
        else:
          wid['widget'].configure(text='-.--',state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='read':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if isinstance(wid['value'],float):
            wid['widget'].configure(text='{:.2f}'.format(wid['value']),state=tk.NORMAL)
        else:
          wid['widget'].configure(text='-.--',state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='switch':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.onSwitch,state=tk.NORMAL)
          else:
            wid['widget'].configure(image=self.offSwitch,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='button':
        if self.controller.connected():
            wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='indoo':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.onIndicator,state=tk.NORMAL)
          else:
            wid['widget'].configure(image=self.offIndicator,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='indtf':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.trueIndicator,state=tk.NORMAL)
          else:
            wid['widget'].configure(image=self.falseIndicator,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='unitd':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if isinstance(wid['value'],int):
            wid['widget'].configure(text=self.controller.unit(wid['value']),state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='label':
        if wid['reg']!=None:
          if self.controller.connected():
            value= self.controller.value(wid['reg'])
            if isinstance(value,str):
              if value=='':
                wid['widget'].configure(text='--',state=tk.NORMAL)
              else:
                wid['widget'].configure(text=value,state=tk.NORMAL)
          else:
            wid['widget'].configure(text='--',state=tk.DISABLED)
            wid['value']= None
      if wid['form']=='name':
        if wid['reg']!=None:
          if self.controller.connected():
            value= self.controller.value(wid['reg'])
            if isinstance(value,str):
              if value=='':
                wid['widget'].configure(text='Stat',state=tk.NORMAL)
              else:
                wid['widget'].configure(text=value,state=tk.NORMAL)
          else:
            wid['widget'].configure(text='Stat',state=tk.DISABLED)
            wid['value']= None
      if wid['form']=='time':
        if wid['reg']!=None:
          if self.controller.connected():
            value= self.controller.value(wid['reg'])
            if isinstance(value,str):
              if value=='':
                wid['widget'].configure(text='00:00:00',state=tk.NORMAL)
              else:
                wid['widget'].configure(text=value,state=tk.NORMAL)
          else:
            wid['widget'].configure(text='00:00:00',state=tk.DISABLED)
            wid['value']= None
      if wid['form']=='achan':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in self.anlgChan.keys():
            if self.anlgChan[entry]==self.controller.value(wid['reg']):
              wid['entry'].set(entry)
              for w in self.widgets:
                if w['form']=='input':
                  w['reg']= self.anlgName[self.anlgChan[entry]]
                if w['form']=='unitin':
                  w['reg']= self.anlgUnit[self.anlgChan[entry]]
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='entry':
        if self.controller.connected():
          wid['widget'].configure(text=value,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='send':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='read':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          chan= self.controller.channel(self.controller.value(wid['reg'])) 
          wid['widget'].configure(text=self.controller.textValue(chan),state=tk.NORMAL)
        else:
          wid['widget'].configure(text='--',state=tk.DISABLED)

#-- End status.py ----------------------------------------------------------
