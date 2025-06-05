#------------------------------------------------------------------------------
#  SyView control
#
#  - Handle the control tabs
#
#  01Jul2022 A. Cooper
#  - initial version
#  31Oct2024 v1.2 A. Cooper
#  - Fix analog channels numbers for time
#  29May2025 v2.0 A. Cooper
#  - replace SymCtrlModbus with SymbCtrlScan, a subprocess based comm handler
#  - alterations all through code to support new controller handler
#
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
ctrlOffset=         16
padY=               0
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
anlgChan=  {'None':0,'WQ Amplifier':1,'Temperature 1':2,'Temperature 2':3,'Analog 1':4,'Analog 2':5,'Internal Temp':6,'Supply Voltage':7,'Processed':8,'Days':35,'Hours':36,'Minutes':37,'Seconds':38}
anlgName=  {0:None,1:'WQSensor',2:'Temperature1',3:'Temperature2',4:'Analog1',5:'Analog2',6:'InternalTemp',7:'SupplyVoltage',8:'Processed',35:'Day',36:'Hour',37:'Minute',38:'Second'}
anlgUnit=  {0:None,1:'WQSensorUnits',2:'Temp1Units',3:'Temp2Units',4:'Analog1Units',5:'Analog2Units',6:'IntTempUnits',7:'SupVoltUnits',8:'ProcUnits',36:'day',37:'hour',38:'min',39:'sec'}
outChan=   {'None':0,'Relay 1':11,'Relay 2':12,'Output 1':13,'Output 2':14,'Virtual 1':15,'Virtual 2':16}
digChan=   {'None':0,'Input 1':9,'Input 2':10,'Relay 1':11,'Relay 2':12,'Output 1':13,'Output 2':14,'Virtual 1':15,'Virtual 2':16,'TofD':39}

#------------------------------------------------------------------------------
#  Control Tab
#
#  - handle the control tab
#
#------------------------------------------------------------------------------
class Control(tk.Frame):

  def __init__(self,parent,controller,ctrlChan):
    self.widgets= [# column 1
      {'reg':'Control1Name',    'form':'label', 'col':1, 'row':1, 'span':2,'width':16,'font':3,'just':'l','value':'--'                   },
      {'reg':'Control1Name',    'form':'entry', 'col':1, 'row':2, 'span':2,'width':16,'font':1,'just':'w','value':None                   },
      {'reg':'Control1Name',    'form':'send',  'col':3, 'row':2, 'span':1,'width':20,'font':1,'just':'l','value':None                   },
      {'reg':None,              'form':'label', 'col':1, 'row':4, 'span':2,'width':16,'font':1,'just':'l','value':'Control Input'        },
      {'reg':'Ctrl1Input',      'form':'achan', 'col':1, 'row':5, 'span':2,'width':32,'font':1,'just':'l','value':None                   },
      {'reg':None,              'form':'input', 'col':1, 'row':6, 'span':1,'width':8, 'font':2,'just':'r','value':0.0                    },
      {'reg':None,              'form':'unitin','col':2, 'row':6, 'span':1,'width':8, 'font':1,'just':'l','value':''                     },
      {'reg':None,              'form':'label', 'col':1, 'row':7, 'span':1,'width':10,'font':1,'just':'r','value':'Valid'                },
      {'reg':'Temp1Valid',      'form':'indtf', 'col':2, 'row':7, 'span':1,'width':48,'font':0,'just':'l','value':False                  },
      {'reg':None,              'form':'label', 'col':1, 'row':9, 'span':1,'width':12,'font':1,'just':'r','value':'Enable Control'       },
      {'reg':'Ctrl1Enable',     'form':'switch','col':2, 'row':9, 'span':1,'width':48,'font':0,'just':'l','value':None                   },
      {'reg':None,              'form':'label', 'col':1, 'row':10,'span':1,'width':12,'font':1,'just':'r','value':'Control High'         },
      {'reg':'Ctrl1High',       'form':'switch','col':2, 'row':10,'span':1,'width':48,'font':0,'just':'l','value':None                   },
      {'reg':None,              'form':'label', 'col':1, 'row':11,'span':1,'width':12,'font':1,'just':'r','value':'One-Shot'             },
      {'reg':'statCtrl1OneShot','form':'switch','col':2, 'row':11,'span':1,'width':48,'font':0,'just':'l','value':None                   },
      {'reg':None,              'form':'label', 'col':1, 'row':12,'span':2,'width':16,'font':1,'just':'l','value':'External Enable Input'},
      {'reg':'Ctrl1EnbSource',  'form':'dchan', 'col':1, 'row':13,'span':2,'width':32,'font':1,'just':'l','value':None                   },
      {'reg':None,              'form':'space', 'col':1, 'row':3, 'span':1,'width':1, 'font':1,'just':'l','value':None                   },
      # column 2                
      {'reg':None,              'form':'label', 'col':4, 'row':5, 'span':1,'width':10,'font':1,'just':'r','value':'Alarm High'           },
      {'reg':None,              'form':'label', 'col':4, 'row':6, 'span':1,'width':10,'font':1,'just':'r','value':'Setpoint High'        },
      {'reg':None,              'form':'label', 'col':4, 'row':7, 'span':1,'width':10,'font':1,'just':'r','value':'Setpoint'             },
      {'reg':None,              'form':'label', 'col':4, 'row':8, 'span':1,'width':10,'font':1,'just':'r','value':'Hysteresis'           },
      {'reg':None,              'form':'label', 'col':4, 'row':9, 'span':1,'width':10,'font':1,'just':'r','value':'Setpoint Low'         },
      {'reg':None,              'form':'label', 'col':4, 'row':10,'span':1,'width':10,'font':1,'just':'r','value':'Alarm Low'            },
      {'reg':None,              'form':'label', 'col':4, 'row':11,'span':1,'width':12,'font':1,'just':'r','value':'Min On/Off'           },
      {'reg':None,              'form':'label', 'col':4, 'row':12,'span':1,'width':10,'font':1,'just':'r','value':'Minimum'              },
      {'reg':None,              'form':'label', 'col':4, 'row':13,'span':1,'width':10,'font':1,'just':'r','value':'Maximum'              },
      {'reg':None,              'form':'label', 'col':6, 'row':12,'span':1,'width':6, 'font':1,'just':'r','value':'Reset'                },
      {'reg':'Ctrl1AlarmPtHigh','form':'float', 'col':5, 'row':5, 'span':1,'width':6, 'font':2,'just':'r','value':0.0                    },
      {'reg':'Ctrl1Setpoint',   'form':'sethi', 'col':5, 'row':6, 'span':1,'width':6, 'font':2,'just':'r','value':0.0                    },
      {'reg':'Ctrl1Setpoint',   'form':'float', 'col':5, 'row':7, 'span':1,'width':6, 'font':2,'just':'r','value':0.0                    },
      {'reg':'Ctrl1Hysteresis', 'form':'float', 'col':5, 'row':8, 'span':1,'width':6, 'font':2,'just':'r','value':0.0                    },
      {'reg':'Ctrl1Setpoint',   'form':'setlo', 'col':5, 'row':9, 'span':1,'width':6, 'font':2,'just':'r','value':0.0                    },
      {'reg':'Ctrl1AlarmPtLow', 'form':'float', 'col':5, 'row':10,'span':1,'width':6, 'font':2,'just':'r','value':0.0                    },
      {'reg':'Ctrl1MinOnTime',  'form':'int',   'col':5, 'row':11,'span':1,'width':6, 'font':2,'just':'r','value':0                      },
      {'reg':'Ctrl1Minimum',    'form':'float', 'col':5, 'row':12,'span':1,'width':6, 'font':2,'just':'r','value':0.0                    },
      {'reg':'Ctrl1Maximum',    'form':'float', 'col':5, 'row':13,'span':1,'width':6, 'font':2,'just':'r','value':0.0                    },
      {'reg':'RstCtrl1Max',     'form':'button','col':6, 'row':13,'span':1,'width':48,'font':0,'just':'r','value':None                   },
      {'reg':'Ctrl1AlarmPtHigh','form':'entry', 'col':6, 'row':5, 'span':1,'width':8, 'font':1,'just':'w','value':None                   },
      {'reg':'Ctrl1Setpoint',   'form':'entry', 'col':6, 'row':7, 'span':1,'width':8, 'font':1,'just':'w','value':None                   },
      {'reg':'Ctrl1Hysteresis', 'form':'entry', 'col':6, 'row':8, 'span':1,'width':8, 'font':1,'just':'w','value':None                   },
      {'reg':'Ctrl1AlarmPtLow', 'form':'entry', 'col':6, 'row':10,'span':1,'width':8, 'font':1,'just':'w','value':None                   },
      {'reg':'Ctrl1MinOnTime',  'form':'entry', 'col':6, 'row':11,'span':1,'width':8, 'font':1,'just':'w','value':None                   },
      {'reg':'Ctrl1AlarmPtHigh','form':'send',  'col':7, 'row':5, 'span':1,'width':20,'font':1,'just':'l','value':None                   },
      {'reg':'Ctrl1Setpoint',   'form':'send',  'col':7, 'row':7, 'span':1,'width':20,'font':1,'just':'l','value':None                   },
      {'reg':'Ctrl1Hysteresis', 'form':'send',  'col':7, 'row':8, 'span':1,'width':20,'font':1,'just':'l','value':None                   },
      {'reg':'Ctrl1AlarmPtLow', 'form':'send',  'col':7, 'row':10,'span':1,'width':20,'font':1,'just':'l','value':None                   },
      {'reg':'Ctrl1MinOnTime',  'form':'send',  'col':7, 'row':11,'span':1,'width':20,'font':1,'just':'l','value':None                   },
      {'reg':None,              'form':'space', 'col':8, 'row':4, 'span':1,'width':1, 'font':1,'just':'l','value':None                   },
      #column 3
      {'reg':None,              'form':'label', 'col':9, 'row':4, 'span':1,'width':12,'font':1,'just':'l','value':'Control Output'       },
      {'reg':'Ctrl1Output',     'form':'ochan', 'col':9, 'row':5, 'span':2,'width':10,'font':1,'just':'l','value':None                   },
      {'reg':None,              'form':'label', 'col':9, 'row':6, 'span':1,'width':10,'font':1,'just':'r','value':'Control Active'       },
      {'reg':None,              'form':'label', 'col':9, 'row':8, 'span':1,'width':10,'font':1,'just':'r','value':'Control Alarm'        },
      {'reg':None,              'form':'label', 'col':9, 'row':9, 'span':1,'width':10,'font':1,'just':'r','value':'Control 1 Alarm'      },
      {'reg':None,              'form':'label', 'col':9, 'row':10,'span':1,'width':10,'font':1,'just':'r','value':'Ctrl 1 Alarm High'    },
      {'reg':None,              'form':'label', 'col':9, 'row':11,'span':1,'width':10,'font':1,'just':'r','value':'Ctrl 1 Alarm Low'     },
      {'reg':'Ctrl1Active',     'form':'indtf', 'col':10,'row':6, 'span':1,'width':48,'font':0,'just':'l','value':False                  },
      {'reg':'CtrlAlarm',       'form':'indtf', 'col':10,'row':8, 'span':1,'width':48,'font':0,'just':'l','value':False                  },
      {'reg':'Ctrl1Alarm',      'form':'indtf', 'col':10,'row':9, 'span':1,'width':48,'font':0,'just':'l','value':False                  },
      {'reg':'Ctrl1AlarmHigh',  'form':'indtf', 'col':10,'row':10,'span':1,'width':48,'font':0,'just':'l','value':False                  },
      {'reg':'Ctrl1AlarmLow',   'form':'indtf', 'col':10,'row':11,'span':1,'width':48,'font':0,'just':'l','value':False                  },
      ]
    if ctrlChan==2:
      for wid in self.widgets:
        if wid['reg']!=None: wid['reg']= wid['reg'].replace('1','2')
    if ctrlChan==3:
      for wid in self.widgets:
        if wid['reg']!=None: wid['reg']= wid['reg'].replace('1','3')
    if ctrlChan==4:
      for wid in self.widgets:
        if wid['reg']!=None: wid['reg']= wid['reg'].replace('1','4')
    self.hysteresis= 0
    tk.Frame.__init__(self,master=parent)
    self.controller= controller
    self.ctrlChan= ctrlChan
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
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='space':
        newWid= tk.Label(self,text=' ',width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY)
      if wid['form'] in ['int','float','input','unitin','unitd','sethi','setlo']:
        newWid= tk.Label(self,text=wid['value'],width=wid['width'],state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='indoo':
        newWid= tk.Button(self,image=self.offIndicator,height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='indtf':
        newWid= tk.Button(self,image=self.falseIndicator,height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='switch':
        newWid= tk.Button(self,image=self.offSwitch,command=partial(self.set,wid['reg']),height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='button':
        newWid= tk.Button(self,image=self.setButton,command=partial(self.set,wid['reg']),height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='entry':
        newWid= tk.Entry(self,width=wid['width'],state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='send':
        newWid= tk.Button(self,command=partial(self.set,wid['reg']),image=self.sendArrow,height=16,width=wid['width'],relief=tk.FLAT,state=tk.DISABLED)
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='achan':
        newStr= tk.StringVar()
        newStr.set(list(anlgChan.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*anlgChan,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=padX,row=wid['row'],pady=padY,sticky=tk.W+tk.E)
        wid['entry']= newStr
      if wid['form']=='ochan':
        newStr= tk.StringVar()
        newStr.set(list(anlgChan.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*outChan,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=padX,row=wid['row'],pady=padY,sticky=tk.W+tk.E)
        wid['entry']= newStr
      if wid['form']=='dchan':
        newStr= tk.StringVar()
        newStr.set(list(digChan.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*digChan,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=padX,row=wid['row'],pady=padY,sticky=tk.W+tk.E)
        wid['entry']= newStr
      if newWid!= None:
        if wid['font']==1:   newWid.configure(font=('Helvetica','10'))
        if wid['font']==2:   newWid.configure(font=('Helvetica','10','bold'))
        if wid['font']==3:   newWid.configure(font=('Helvetica','12','bold'))
        if wid['just']=='r': newWid.configure(anchor=tk.E,justify=tk.RIGHT)
        if wid['just']=='f': newWid.configure(justify=tk.RIGHT,sticky=tk.E)
        if wid['just']=='l': newWid.configure(anchor=tk.W,justify=tk.LEFT)
        if wid['just']=='w': newWid.configure(justify=tk.LEFT)
        wid['widget']= newWid
    # top corner spacer
    spacer= tk.Label(self,image=self.spacerButton,width=20)
    spacer.grid (column=0,row=0)

  def set(self,reg):
    if self.controller.valid():
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
            if self.controller.write(reg,True):
              self.delegates['EventLog']('{} requested'.format(reg),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message),True)
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
                  value= w['widget'].get()[:16]
                  valid= True
            if valid:
              wid['value']= value
              if self.controller.write(reg,wid['value']):
                self.delegates['EventLog']('{} set to {}'.format(reg,wid['value']),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message),True)

  def setMenu(self,reg,selection):
    if self.controller.valid():
      for wid in self.widgets:
        if wid['reg']==reg:
          if wid['form']=='achan':
            if self.controller.write(reg,anlgChan[selection]):
              self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message),True)
            for w in self.widgets:
              if w['form']=='input':
                w['reg']= anlgName[anlgChan[selection]]
              if w['form']=='unitin':
                w['reg']= anlgUnit[anlgChan[selection]]
          if wid['form']=='ochan':
            if self.controller.write(reg,outChan[selection]):
              self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message),True)
          if wid['form']=='dchan':
            if self.controller.write(reg,digChan[selection]):
              self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message),True)

  #-- external methods --------------------------------------------------------

  def setDelegates(self,funcList):
    self.delegates= funcList

  def update(self):
    for wid in self.widgets:
      if wid['form']=='int':
        if not self.controller.valid():
          wid['widget'].configure(text='--',state=tk.DISABLED)
          wid['value']= None
        elif wid['reg']== None:
          wid['widget'].configure(text='--',state=tk.NORMAL)
          wid['value']= None
        else:
          wid['value']= self.controller.read(wid['reg'])
          if isinstance(wid['value'],int):
            wid['widget'].configure(text='{:d}'.format(wid['value']),state=tk.NORMAL)
      if wid['form']=='float' or wid['form']=='input':
        if not self.controller.valid():
          wid['widget'].configure(text='-.--',state=tk.DISABLED)
          wid['value']= None
        elif wid['reg']== None:
          wid['widget'].configure(text='-.--',state=tk.NORMAL)
          wid['value']= None
        else:
          wid['value']= self.controller.read(wid['reg'])
          if isinstance(wid['value'],float):
            wid['widget'].configure(text='{:.2f}'.format(wid['value']),state=tk.NORMAL)
            if 'Hysteresis' in wid['reg']: self.hysteresis= wid['value']
      if wid['form']=='sethi':
        if self.controller.valid():
          wid['value']= self.controller.read(wid['reg'])
          if isinstance(wid['value'],float):
            wid['widget'].configure(text='{:.2f}'.format(wid['value']+self.hysteresis/2),state=tk.NORMAL)
        else:
          wid['widget'].configure(text='-.--',state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='setlo':
        if self.controller.valid():
          wid['value']= self.controller.read(wid['reg'])
          if isinstance(wid['value'],float):
            wid['widget'].configure(text='{:.2f}'.format(wid['value']-self.hysteresis/2),state=tk.NORMAL)
        else:
          wid['widget'].configure(text='-.--',state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='switch':
        if self.controller.valid():
          wid['value']= self.controller.read(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.onSwitch,state=tk.NORMAL)
          else:
            wid['widget'].configure(image=self.offSwitch,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='button':
        if self.controller.valid():
            wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='indoo':
        if self.controller.valid():
          wid['value']= self.controller.read(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.onIndicator,state=tk.NORMAL)
          else:
            wid['widget'].configure(image=self.offIndicator,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='indtf':
        if self.controller.valid():
          wid['value']= self.controller.read(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.trueIndicator,state=tk.NORMAL)
          else:
            wid['widget'].configure(image=self.falseIndicator,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='unitd' or wid['form']=='unitin':
        if not self.controller.valid():
          wid['widget'].configure(state=tk.DISABLED)
        elif wid['reg']== None:
          wid['value']= None
          wid['widget'].configure(text='',state=tk.NORMAL)
        else:
          value= self.controller.read(wid['reg'])
          if isinstance(value,int):
            wid['widget'].configure(text=self.controller.unit(value),state=tk.NORMAL)
          else:
            wid['widget'].configure(text='',state=tk.NORMAL)
      if wid['form']=='label':
        if wid['reg']!=None:
          if self.controller.valid():
            value= self.controller.read(wid['reg'])
            if isinstance(value,str):
              if value=='':
                wid['widget'].configure(text='--',state=tk.NORMAL)
              else:
                wid['widget'].configure(text=value,state=tk.NORMAL)
          else:
            wid['widget'].configure(text='--',state=tk.DISABLED)
            wid['value']= None
      if wid['form']=='entry':
        if self.controller.valid():
          wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='send':
        if self.controller.valid():
          wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='achan':
        if self.controller.valid():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in anlgChan.keys():
            if anlgChan[entry]==self.controller.read(wid['reg']):
              wid['entry'].set(entry)
              for w in self.widgets:
                if w['form']=='input':
                  w['reg']= anlgName[anlgChan[entry]]
                if w['form']=='unitin':
                  w['reg']= anlgUnit[anlgChan[entry]]
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='ochan':
        if self.controller.valid():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in outChan.keys():
            if outChan[entry]==self.controller.read(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='dchan':
        if self.controller.valid():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in digChan.keys():
            if digChan[entry]==self.controller.read(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)

#-- End control.py ----------------------------------------------------------
