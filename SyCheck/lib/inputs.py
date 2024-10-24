#------------------------------------------------------------------------------
#  SyView inputs
#
#  - Handle the inputs tab
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
unitsAll=  {'None':0,'°C':1,'°F':2,'pH':3,'mV':4,'V':5,'mA':6,'A':7,'mm':8,'m':9,'ml':10,'l':11,'g':12,'kg':13,'lbs':14,'kPa':15,'PSI':16,'Hz':17,'%':18,'ppm':19,'Ω':20}
unitsTemp= {'°C':1,'°F':2}
unitsWQ=   {'pH':3,'mV':4,'V':5}
anlgChan=  {'None':0,'WQ Amplifier':1,'Temperature 1':2,'Temperature 2':3,'Analog 1':4,'Analog 2':5,'Internal Temp':6,'Supply Voltage':7}
procSel=   {'Average':0,'Minimum':1,'Maximum':2,'Sum':3,'Difference':4,'Priority':5}

#------------------------------------------------------------------------------
#  Inputs Tab
#
#  - handle the inputs tab
#
#------------------------------------------------------------------------------
class Inputs(tk.Frame):
  widgets= [# WQ Input
    {'reg':None,            'form':'title', 'conf':False,'col':1, 'row':1, 'padx':5,'span':2,'width':14,'font':3,'just':'l','value':'WQ Input'         },
    {'reg':'WQSensor',      'form':'float', 'conf':False,'col':1, 'row':2, 'padx':5,'span':1,'width':6, 'font':1,'just':'r','value':0.0                },
    {'reg':'WQSensorUnits', 'form':'unitd', 'conf':False,'col':2, 'row':2, 'padx':0,'span':1,'width':3, 'font':1,'just':'l','value':'-'                },
    {'reg':'WQName',        'form':'label', 'conf':False,'col':3, 'row':1, 'padx':5,'span':1,'width':16,'font':1,'just':'f','value':'--'               },
    {'reg':'WQName',        'form':'entry', 'conf':False,'col':3, 'row':2, 'padx':5,'span':1,'width':16,'font':1,'just':'f','value':''                 },
    {'reg':'WQName',        'form':'send',  'conf':False,'col':4, 'row':2, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':1, 'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Gain'             },
    {'reg':'WQGain',        'form':'float', 'conf':False,'col':6, 'row':1, 'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'WQGain',        'form':'entry', 'conf':False,'col':7, 'row':1, 'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'WQGain',        'form':'send',  'conf':False,'col':8, 'row':1, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':2, 'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Offset'           },
    {'reg':'WQOffset',      'form':'float', 'conf':False,'col':6, 'row':2, 'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'WQOffset',      'form':'entry', 'conf':False,'col':7, 'row':2, 'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'WQOffset',      'form':'send',  'conf':False,'col':8, 'row':2, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':'WQSensorUnits', 'form':'unitwq','conf':False,'col':9, 'row':1, 'padx':9,'span':1,'width':4, 'font':1,'just':'l','value':0                  },
    {'reg':None,            'form':'label', 'conf':False,'col':10,'row':1, 'padx':5,'span':1,'width':6, 'font':1,'just':'c','value':'Valid'            },
    {'reg':'WQSensorValid', 'form':'indtf', 'conf':False,'col':10,'row':2, 'padx':5,'span':1,'width':6, 'font':0,'just':'c','value':False              },
    # Temperature 1
    {'reg':None,            'form':'title', 'conf':False,'col':1, 'row':3, 'padx':5,'span':2,'width':14,'font':3,'just':'l','value':'Temperature 1'    },
    {'reg':'Temperature1',  'form':'float', 'conf':False,'col':1, 'row':4, 'padx':5,'span':1,'width':6, 'font':1,'just':'r','value':0.0                },
    {'reg':'Temp1Units',    'form':'unitd', 'conf':False,'col':2, 'row':4, 'padx':0,'span':1,'width':3, 'font':1,'just':'l','value':'-'                },
    {'reg':'Temp1Name',     'form':'label', 'conf':False,'col':3, 'row':3, 'padx':5,'span':1,'width':16,'font':1,'just':'f','value':'--'               },
    {'reg':'Temp1Name',     'form':'entry', 'conf':False,'col':3, 'row':4, 'padx':5,'span':1,'width':16,'font':1,'just':'f','value':''                 },
    {'reg':'Temp1Name',     'form':'send',  'conf':False,'col':4, 'row':4, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':3, 'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Gain'             },
    {'reg':'Temp1Gain',     'form':'float', 'conf':False,'col':6, 'row':3, 'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'Temp1Gain',     'form':'entry', 'conf':False,'col':7, 'row':3, 'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'Temp1Gain',     'form':'send',  'conf':False,'col':8, 'row':3, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':4, 'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Offset'           },
    {'reg':'Temp1Offset',   'form':'float', 'conf':False,'col':6, 'row':4, 'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'Temp1Offset',   'form':'entry', 'conf':False,'col':7, 'row':4, 'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'Temp1Offset',   'form':'send',  'conf':False,'col':8, 'row':4, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':''                 },
    {'reg':'Temp1Units',    'form':'unitt', 'conf':False,'col':9, 'row':3, 'padx':9,'span':1,'width':4, 'font':1,'just':'r','value':0                  },
    {'reg':None,            'form':'label', 'conf':False,'col':10,'row':3, 'padx':5,'span':1,'width':6, 'font':1,'just':'c','value':'Valid'            },
    {'reg':'Temp1Valid',    'form':'indtf', 'conf':False,'col':10,'row':4, 'padx':5,'span':1,'width':6, 'font':0,'just':'c','value':False              },
    # Temperature 2
    {'reg':None,            'form':'title', 'conf':False,'col':1, 'row':5, 'padx':5,'span':2,'width':14,'font':3,'just':'l','value':'Temperature 2'    },
    {'reg':'Temperature2',  'form':'float', 'conf':False,'col':1, 'row':6, 'padx':5,'span':1,'width':6, 'font':1,'just':'r','value':0.0                },
    {'reg':'Temp2Units',    'form':'unitd', 'conf':False,'col':2, 'row':6, 'padx':0,'span':1,'width':3, 'font':1,'just':'l','value':'-'                },
    {'reg':'Temp2Name',     'form':'label', 'conf':False,'col':3, 'row':5, 'padx':5,'span':1,'width':16,'font':1,'just':'f','value':'--'               },
    {'reg':'Temp2Name',     'form':'entry', 'conf':False,'col':3, 'row':6, 'padx':5,'span':1,'width':16,'font':1,'just':'f','value':''                 },
    {'reg':'Temp2Name',     'form':'send',  'conf':False,'col':4, 'row':6, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':5, 'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Gain'             },
    {'reg':'Temp2Gain',     'form':'float', 'conf':False,'col':6, 'row':5, 'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'Temp2Gain',     'form':'entry', 'conf':False,'col':7, 'row':5, 'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'Temp2Gain',     'form':'send',  'conf':False,'col':8, 'row':5, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':6, 'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Offset'           },
    {'reg':'Temp2Offset',   'form':'float', 'conf':False,'col':6, 'row':6, 'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'Temp2Offset',   'form':'entry', 'conf':False,'col':7, 'row':6, 'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'Temp2Offset',   'form':'send',  'conf':False,'col':8, 'row':6, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':''                 },
    {'reg':'Temp2Units',    'form':'unitt', 'conf':False,'col':9, 'row':5, 'padx':9,'span':1,'width':4, 'font':1,'just':'r','value':0                  },
    {'reg':None,            'form':'label', 'conf':False,'col':10,'row':5, 'padx':5,'span':1,'width':6, 'font':1,'just':'c','value':'Valid'            },
    {'reg':'Temp2Valid',    'form':'indtf', 'conf':False,'col':10,'row':6, 'padx':5,'span':1,'width':6, 'font':0,'just':'c','value':False              },
    # Input 1
    {'reg':None,            'form':'title', 'conf':False,'col':1, 'row':7, 'padx':5,'span':2,'width':14,'font':3,'just':'l','value':'Input 1'          },
    {'reg':'Analog1',       'form':'float', 'conf':False,'col':1, 'row':8, 'padx':5,'span':1,'width':6, 'font':1,'just':'r','value':0.0                },
    {'reg':'Analog1Units',  'form':'unitd', 'conf':False,'col':2, 'row':8, 'padx':0,'span':1,'width':3, 'font':1,'just':'l','value':'-'                },
    {'reg':'DigitalIn1',    'form':'indoo', 'conf':False,'col':2, 'row':7, 'padx':0,'span':1,'width':3, 'font':0,'just':'c','value':False              },
    {'reg':'Input1Name',    'form':'label', 'conf':False,'col':3, 'row':7, 'padx':5,'span':1,'width':16,'font':1,'just':'f','value':'--'               },
    {'reg':'Input1Name',    'form':'entry', 'conf':False,'col':3, 'row':8, 'padx':5,'span':1,'width':16,'font':1,'just':'f','value':''                 },
    {'reg':'Input1Name',    'form':'send',  'conf':False,'col':4, 'row':8, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':7, 'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Gain'             },
    {'reg':'Analog1Gain',   'form':'float', 'conf':False,'col':6, 'row':7, 'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'Analog1Gain',   'form':'entry', 'conf':False,'col':7, 'row':7, 'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'Analog1Gain',   'form':'send',  'conf':False,'col':8, 'row':7, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':8, 'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Offset'           },
    {'reg':'Analog1Offset', 'form':'float', 'conf':False,'col':6, 'row':8, 'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'Analog1Offset', 'form':'entry', 'conf':False,'col':7, 'row':8, 'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'Analog1Offset', 'form':'send',  'conf':False,'col':8, 'row':8, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':'Analog1Units',  'form':'units', 'conf':False,'col':9, 'row':7, 'padx':9,'span':1,'width':4, 'font':1,'just':'r','value':0                  },
    {'reg':None,            'form':'label', 'conf':False,'col':10,'row':7, 'padx':5,'span':1,'width':6, 'font':1,'just':'c','value':'Valid'            },
    {'reg':'Analog1Valid',  'form':'indtf', 'conf':False,'col':10,'row':8, 'padx':5,'span':1,'width':6, 'font':0,'just':'c','value':False              },
    # Input 2
    {'reg':None,            'form':'title', 'conf':False,'col':1, 'row':9, 'padx':5,'span':2,'width':14,'font':3,'just':'l','value':'Input 2'          },
    {'reg':'Analog2',       'form':'float', 'conf':False,'col':1, 'row':10,'padx':5,'span':1,'width':6, 'font':1,'just':'r','value':0.0                },
    {'reg':'Analog2Units',  'form':'unitd', 'conf':False,'col':2, 'row':10,'padx':0,'span':1,'width':3, 'font':1,'just':'l','value':'-'                },
    {'reg':'DigitalIn2',    'form':'indoo', 'conf':False,'col':2, 'row':9, 'padx':0,'span':1,'width':3, 'font':0,'just':'c','value':False              },
    {'reg':'Input2Name',    'form':'label', 'conf':False,'col':3, 'row':9, 'padx':5,'span':1,'width':16,'font':1,'just':'f','value':'--'               },
    {'reg':'Input2Name',    'form':'entry', 'conf':False,'col':3, 'row':10,'padx':5,'span':1,'width':16,'font':1,'just':'f','value':''                 },
    {'reg':'Input2Name',    'form':'send',  'conf':False,'col':4, 'row':10,'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':9, 'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Gain'             },
    {'reg':'Analog2Gain',   'form':'float', 'conf':False,'col':6, 'row':9, 'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'Analog2Gain',   'form':'entry', 'conf':False,'col':7, 'row':9, 'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'Analog2Gain',   'form':'send',  'conf':False,'col':8, 'row':9, 'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':5, 'row':10,'padx':2,'span':1,'width':6, 'font':1,'just':'r','value':'Offset'           },
    {'reg':'Analog2Offset', 'form':'float', 'conf':False,'col':6, 'row':10,'padx':5,'span':1,'width':6, 'font':1,'just':'f','value':0.0                },
    {'reg':'Analog2Offset', 'form':'entry', 'conf':False,'col':7, 'row':10,'padx':5,'span':1,'width':10,'font':1,'just':'f','value':''                 },
    {'reg':'Analog2Offset', 'form':'send',  'conf':False,'col':8, 'row':10,'padx':0,'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':'Analog2Units',  'form':'units', 'conf':False,'col':9, 'row':9, 'padx':9,'span':1,'width':4, 'font':1,'just':'r','value':0                  },
    {'reg':None,            'form':'label', 'conf':False,'col':10,'row':9, 'padx':5,'span':1,'width':6, 'font':1,'just':'c','value':'Valid'            },
    {'reg':'Analog2Valid',  'form':'indtf', 'conf':False,'col':10,'row':10,'padx':5,'span':1,'width':6, 'font':0,'just':'c','value':False              },
    # supply and int temp
    {'reg':None,            'form':'title', 'conf':False,'col':1 ,'row':11,'padx':5,'span':2,'width':14,'font':3,'just':'l','value':'Int Temp'         },
    {'reg':'InternalTemp',  'form':'float', 'conf':False,'col':1 ,'row':12,'padx':5,'span':1,'width':6, 'font':1,'just':'r','value':0.0                },
    {'reg':'IntTempUnits',  'form':'unitd', 'conf':False,'col':2 ,'row':12,'padx':0,'span':1,'width':3, 'font':1,'just':'l','value':'-'                },
    {'reg':None,            'form':'title', 'conf':False,'col':3 ,'row':11,'padx':5,'span':2,'width':16,'font':3,'just':'l','value':'Supply Voltage'   },
    {'reg':'SupplyVoltage', 'form':'float', 'conf':False,'col':3 ,'row':12,'padx':5,'span':1,'width':6, 'font':1,'just':'r','value':0.0                },
    {'reg':'SupVoltUnits',  'form':'unitd', 'conf':False,'col':4 ,'row':12,'padx':0,'span':1,'width':3, 'font':1,'just':'l','value':'-'                },
    # Processed
    {'reg':None,            'form':'title', 'conf':False,'col':1, 'row':13,'padx':5,'span':2,'width':14,'font':3,'just':'l','value':'Processed Read'},
    {'reg':'ProcessChanA',  'form':'achan', 'conf':False,'col':3, 'row':13,'padx':0,'span':1,'width':10,'font':1,'just':'c','value':''                 },
    {'reg':'ProcessChanB',  'form':'achan', 'conf':False,'col':3, 'row':14,'padx':0,'span':1,'width':10,'font':1,'just':'c','value':''                 },
    {'reg':'ProcessID',     'form':'proc',  'conf':False,'col':4, 'row':13,'padx':0,'span':3,'width':8, 'font':1,'just':'l','value':0                  },
    {'reg':'ProcessedData', 'form':'float', 'conf':False,'col':4, 'row':14,'padx':0,'span':2,'width':6, 'font':1,'just':'r','value':0.0                },
    {'reg':'ProcUnits',     'form':'unitd', 'conf':False,'col':6, 'row':14,'padx':0,'span':1,'width':3, 'font':1,'just':'l','value':'-'                },
    {'reg':None,            'form':'label', 'conf':False,'col':10,'row':13,'padx':5,'span':1,'width':6, 'font':1,'just':'c','value':'Valid'            },
    {'reg':'ProcReadValid', 'form':'indtf', 'conf':False,'col':10,'row':14,'padx':5,'span':1,'width':6, 'font':0,'just':'c','value':None               }]

  def __init__(self,parent,controller):    
    tk.Frame.__init__(self,master=parent)
    self.controller= controller
    self.grid()  
    self.createWidgets()

  def createWidgets(self):
    # images for the buttons
    self.sendArrow=      tk.PhotoImage(file=os.path.join(localDir,'img',sendArrowFile))
    self.onSwitch=       tk.PhotoImage(file=os.path.join(localDir,'img',onSwitchFile))
    self.offSwitch=      tk.PhotoImage(file=os.path.join(localDir,'img',offSwitchFile))
    self.onIndicator=    tk.PhotoImage(file=os.path.join(localDir,'img',onIndicatorFile))
    self.offIndicator=   tk.PhotoImage(file=os.path.join(localDir,'img',offIndicatorFile))
    self.trueIndicator=  tk.PhotoImage(file=os.path.join(localDir,'img',trueIndicatorFile))
    self.falseIndicator= tk.PhotoImage(file=os.path.join(localDir,'img',falseIndicatorFile))
    self.setButton=      tk.PhotoImage(file=os.path.join(localDir,'img',setButtonFile))
    self.spacerImg=      tk.PhotoImage(file=os.path.join(localDir,'img',spacerFile))
    #place widgets
    for wid in self.widgets:
      newWid= None
      if wid['form']=='title':
        newWid= tk.Label(self,text=wid['value'],width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=wid['padx'],pady=padY)
      if wid['form']=='label':
        newWid= tk.Label(self,text=wid['value'],width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=wid['padx'],pady=padY)
      if wid['form']=='int':
        newWid= tk.Label(self,text="{:d}".format(wid['value']),width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=wid['padx'],pady=padY)
      if wid['form']=='float':
        newWid= tk.Label(self,text="{:.2f}".format(wid['value']),width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=wid['padx'],pady=padY)
      if wid['form']=='rev':
        newWid= tk.Label(self,text="{:3.1f}".format(wid['value']),width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=wid['padx'],pady=padY)
      if wid['form']=='indtf':
        newWid= tk.Button(self,image=self.falseIndicator,height=16,width=48,relief=tk.FLAT)
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
      if wid['form']=='indoo':
        newWid= tk.Button(self,image=self.offIndicator,height=16,width=48,relief=tk.FLAT)
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
      if wid['form']=='switch':
        newWid= tk.Button(self,image=self.offSwitch,height=16,width=48,relief=tk.FLAT)
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
      if wid['form']=='button':
        newWid= tk.Button(self,image=self.setButton,height=16,width=48,relief=tk.FLAT)
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
      if wid['form']=='entry':
        newStr= tk.StringVar()
        newWid= tk.Entry(self,textvariable=newStr,width=wid['width'])
        newWid.grid (column=wid['col'],columnspan=wid['span'],row=wid['row'],padx=wid['padx'],pady=padY)
        wid['entry']= newStr
      if wid['form']=='send':
        newWid= tk.Button(self,command=partial(self.set,wid['reg']),image=self.sendArrow,height=16,width=24,relief=tk.FLAT)
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
      if wid['form']=='unitd':
        newWid= tk.Label(self,text=wid['value'],width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=wid['padx'],pady=padY)
      if wid['form']=='unitwq':
        newStr= tk.StringVar()
        newStr.set(list(unitsWQ.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*unitsWQ,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
        newWid.configure(width=wid['width'])
        wid['entry']= newStr
      if wid['form']=='unitt':
        newStr= tk.StringVar()
        newStr.set(list(unitsTemp.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*unitsTemp,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
        newWid.configure(width=wid['width'])
        wid['entry']= newStr
      if wid['form']=='units':
        newStr= tk.StringVar()
        newStr.set(list(unitsAll.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*unitsAll,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
        newWid.configure(width=wid['width'])
        wid['entry']= newStr
      if wid['form']=='achan':
        newStr= tk.StringVar()
        newStr.set(list(anlgChan.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*anlgChan,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
        newWid.configure(width=wid['width'])
        wid['entry']= newStr
      if wid['form']=='proc':
        newStr= tk.StringVar()
        newStr.set(list(procSel.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*procSel,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=wid['padx'],row=wid['row'],pady=padY)
        newWid.configure(width=wid['width'])
        wid['entry']= newStr
      if newWid!= None:
        if wid['font']==1:   newWid.configure(font=('Helvetica','10'))
        if wid['font']==2:   newWid.configure(font=('Helvetica','10','bold'))
        if wid['font']==3:   newWid.configure(font=('Helvetica','12','bold'))
        if wid['just']=='r': newWid.configure(anchor=tk.E,justify=tk.RIGHT)
        if wid['just']=='f': newWid.configure(justify=tk.RIGHT)
        if wid['just']=='l': newWid.configure(anchor=tk.W,justify=tk.LEFT)
        wid['widget']= newWid
    # top corner spacer
    spacer= tk.Label(self,image=self.spacerImg,width=10)
    spacer.grid (column=0,row=0)
    
  def setMenu(self,reg,selection):
    if self.controller.connected():
      for wid in self.widgets:
        if wid['reg']==reg:
          if wid['form']=='units':
              if self.controller.write(reg,unitsAll[selection]):
                self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
          if wid['form']=='unitwq':
              if self.controller.write(reg,unitsWQ[selection]):
                self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
          if wid['form']=='unitt':
              if self.controller.write(reg,unitsTemp[selection]):
                self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
          if wid['form']=='achan':
              if self.controller.write(reg,anlgChan[selection]):
                self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
          if wid['form']=='proc':
              if self.controller.write(reg,procSel[selection]):
                self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)

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
            if self.controller.write(reg,True):
              self.delegates['EventLog']('{} set to {}'.format(reg,wid['value']),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
          if wid['form']=='send':
            valid= False
            for w in self.widgets:
              if w['reg']==reg and w['form']=='entry':
                if self.controller.type(reg)=='float':
                  try: value= float(w['entry'].get())
                  except:
                    self.delegates['EventLog']('Write error to {}! Improper value'.format(reg),True)
                  else:
                    valid= True
                if self.controller.type(reg)=='int':
                  try: value= int(w['entry'].get())
                  except:
                    self.delegates['EventLog']('Write error to {}! Improper value'.format(reg),True)
                  else:
                    valid= True
                if self.controller.type(reg)=='uint':
                  try: value= int(w['entry'].get())
                  except:
                    self.delegates['EventLog']('Write error to {}! Improper value'.format(reg),True)
                  else:
                    if value>=0:
                      valid= True
                    else:
                      self.delegates['EventLog']('Write error to {}! Improper value'.format(reg),True)
                if self.controller.type(reg)=='str':
                  value= w['entry'].get()[:16]
                  valid= True
            if valid:
              wid['value']= value
              if self.controller.write(reg,wid['value']):
                self.delegates['EventLog']('{} set to {}'.format(reg,wid['value']),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)

  #-- external methods --------------------------------------------------------
  
  def setDelegates(self,funcList):
    self.delegates= funcList

  def update(self):
    for wid in self.widgets:
      if wid['form']=='int':
        if not self.controller.connected():
          wid['widget'].configure(text='--',state=tk.DISABLED)
          wid['value']= None
        elif wid['reg']== None:
          wid['widget'].configure(text='--',state=tk.NORMAL)
          wid['value']= None
        else:
          wid['value']= self.controller.value(wid['reg'])
          if isinstance(wid['value'],int):
            wid['widget'].configure(text='{:d}'.format(wid['value']),state=tk.NORMAL)
      if wid['form']=='float' or wid['form']=='input':
        if not self.controller.connected():
          wid['widget'].configure(text='-.--',state=tk.DISABLED)
          wid['value']= None
        elif wid['reg']== None:
          wid['widget'].configure(text='-.--',state=tk.NORMAL)
          wid['value']= None
        else:
          wid['value']= self.controller.value(wid['reg'])
          if isinstance(wid['value'],float):
            wid['widget'].configure(text='{:.2f}'.format(wid['value']),state=tk.NORMAL)
            if 'Hysteresis' in wid['reg']: self.hysteresis= wid['value']
      if wid['form']=='sethi':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if isinstance(wid['value'],float):
            wid['widget'].configure(text='{:.2f}'.format(wid['value']+self.hysteresis/2),state=tk.NORMAL)
        else:
          wid['widget'].configure(text='-.--',state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='setlo':
        if self.controller.connected():
          wid['value']= self.controller.value(wid['reg'])
          if isinstance(wid['value'],float):
            wid['widget'].configure(text='{:.2f}'.format(wid['value']-self.hysteresis/2),state=tk.NORMAL)
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
      if wid['form']=='unitd' or wid['form']=='unitin':
        if not self.controller.connected():
          wid['widget'].configure(state=tk.DISABLED)
        elif wid['reg']== None:
          wid['value']= None
          wid['widget'].configure(text='',state=tk.NORMAL)
        else:
          value= self.controller.value(wid['reg'])
          if isinstance(value,int):
            wid['widget'].configure(text=self.controller.unit(value),state=tk.NORMAL)
          else:
            wid['widget'].configure(text='',state=tk.NORMAL)
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
      if wid['form']=='entry':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='send':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='achan':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in anlgChan.keys():
            if anlgChan[entry]==self.controller.value(wid['reg']):
              wid['entry'].set(entry)
              for w in self.widgets:
                if w['form']=='input':
                  w['reg']= anlgName[anlgChan[entry]]
                if w['form']=='unitin':
                  w['reg']= anlgUnit[anlgChan[entry]]
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='proc':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in procSel.keys():
            if procSel[entry]==self.controller.value(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='units':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in unitsAll.keys():
            if unitsAll[entry]==self.controller.value(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='unitt':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in unitsTemp.keys():
            if unitsTemp[entry]==self.controller.value(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='unitwq':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in unitsWQ.keys():
            if unitsWQ[entry]==self.controller.value(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)

#-- End inputs.py ----------------------------------------------------------
