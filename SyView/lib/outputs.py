#------------------------------------------------------------------------------
#  SyView outputs
#
#  - Handle the outputs tab
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
trueIndicatorFile=  'indicatorTrue.png'
falseIndicatorFile= 'indicatorFalse.png'
setButtonFile=      'setButton.png'
spacerFile=         'spacer.png'
colGood=            '#000000'
colBad=             '#FFADAD'
outChan=   {'Relay 1':11,'Relay 2':12,'Output 1':13,'Output 2':14,'Virtual 1':15,'Virtual 2':16}


#------------------------------------------------------------------------------
#  Outputs Tab
#
#  - handle the outputs tab
#
#------------------------------------------------------------------------------
class Outputs(tk.Frame):
  widgets= [# Relay 1
    {'reg':None,            'form':'title', 'conf':False,'col':1,'row':1, 'padx':5, 'span':1,'width':8, 'font':3,'just':'l','value':'Relay 1'          },
    {'reg':'Relay1Name',    'form':'text',  'conf':False,'col':2,'row':1, 'padx':5, 'span':1,'width':16,'font':1,'just':'l','value':'--'               },
    {'reg':'Relay1Name',    'form':'entry', 'conf':False,'col':2,'row':2, 'padx':5, 'span':1,'width':16,'font':1,'just':'f','value':''                 },
    {'reg':'Relay1Name',    'form':'send',  'conf':False,'col':3,'row':2, 'padx':0, 'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':4,'row':1, 'padx':5, 'span':1,'width':6, 'font':1,'just':'r','value':'Status'           },
    {'reg':'Relay1Status',  'form':'indtf', 'conf':False,'col':5,'row':1, 'padx':5, 'span':1,'width':6, 'font':0,'just':'c','value':False              },
    {'reg':None,            'form':'label', 'conf':False,'col':4,'row':2, 'padx':5, 'span':1,'width':10,'font':1,'just':'r','value':'Request On'       },
    {'reg':'Relay1Request', 'form':'switch','conf':True ,'col':5,'row':2, 'padx':5, 'span':1,'width':6, 'font':0,'just':'c','value':False              },
    # Relay 2
    {'reg':None,            'form':'label', 'conf':False,'col':0,'row':3, 'padx':5, 'span':1,'width':6, 'font':1,'just':'l','value':''                 },
    {'reg':None,            'form':'title', 'conf':False,'col':1,'row':4, 'padx':5, 'span':1,'width':8, 'font':3,'just':'l','value':'Relay 2'          },
    {'reg':'Relay2Name',    'form':'text',  'conf':False,'col':2,'row':4, 'padx':5, 'span':1,'width':16,'font':1,'just':'l','value':'--'               },
    {'reg':'Relay2Name',    'form':'entry', 'conf':False,'col':2,'row':5, 'padx':5, 'span':1,'width':16,'font':1,'just':'f','value':''                 },
    {'reg':'Relay2Name',    'form':'send',  'conf':False,'col':3,'row':5, 'padx':0, 'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':4,'row':4, 'padx':5, 'span':1,'width':6, 'font':1,'just':'r','value':'Status'           },
    {'reg':'Relay2Status',  'form':'indtf', 'conf':False,'col':5,'row':4, 'padx':5, 'span':1,'width':6, 'font':0,'just':'c','value':False              },
    {'reg':None,            'form':'label', 'conf':False,'col':4,'row':5, 'padx':5, 'span':1,'width':10,'font':1,'just':'r','value':'Request On'       },
    {'reg':'Relay2Request', 'form':'switch','conf':False,'col':5,'row':5, 'padx':5, 'span':1,'width':6, 'font':0,'just':'c','value':False              },
    # Output 1
    {'reg':None,            'form':'label', 'conf':False,'col':0,'row':6, 'padx':5, 'span':1,'width':6, 'font':1,'just':'l','value':''                 },
    {'reg':None,            'form':'title', 'conf':False,'col':1,'row':8, 'padx':5, 'span':1,'width':8, 'font':3,'just':'l','value':'Output 1'         },
    {'reg':'Output1Name',   'form':'text',  'conf':False,'col':2,'row':8, 'padx':5, 'span':1,'width':16,'font':1,'just':'l','value':'--'               },
    {'reg':'Output1Name',   'form':'entry', 'conf':False,'col':2,'row':9, 'padx':5, 'span':1,'width':16,'font':1,'just':'f','value':''                 },
    {'reg':'Output1Name',   'form':'send',  'conf':False,'col':3,'row':9, 'padx':0, 'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':4,'row':8, 'padx':5, 'span':1,'width':6, 'font':1,'just':'r','value':'Status'           },
    {'reg':'DigitalOut1',   'form':'indtf', 'conf':False,'col':5,'row':8, 'padx':5, 'span':1,'width':6, 'font':0,'just':'c','value':False              },
    {'reg':None,            'form':'label', 'conf':False,'col':4,'row':9, 'padx':5, 'span':1,'width':10,'font':1,'just':'r','value':'Request On'       },
    {'reg':'Dout1Request',  'form':'switch','conf':False,'col':5,'row':9, 'padx':5, 'span':1,'width':6, 'font':0,'just':'c','value':False              },
    # Output 2
    {'reg':None,            'form':'label', 'conf':False,'col':0,'row':10,'padx':5, 'span':1,'width':6, 'font':1,'just':'l','value':''                 },
    {'reg':None,            'form':'title', 'conf':False,'col':1,'row':11,'padx':5, 'span':1,'width':8, 'font':3,'just':'l','value':'Output 2'         },
    {'reg':'Output2Name',   'form':'text',  'conf':False,'col':2,'row':11,'padx':5, 'span':1,'width':16,'font':1,'just':'l','value':'--'               },
    {'reg':'Output2Name',   'form':'entry', 'conf':False,'col':2,'row':12,'padx':5, 'span':1,'width':16,'font':1,'just':'f','value':''                 },
    {'reg':'Output2Name',   'form':'send',  'conf':False,'col':3,'row':12,'padx':0, 'span':1,'width':6, 'font':1,'just':'l','value':None               },
    {'reg':None,            'form':'label', 'conf':False,'col':4,'row':11,'padx':5, 'span':1,'width':6, 'font':1,'just':'r','value':'Status'           },
    {'reg':'DigitalOut2',   'form':'indtf', 'conf':False,'col':5,'row':11,'padx':5, 'span':1,'width':6, 'font':0,'just':'c','value':False              },
    {'reg':None,            'form':'label', 'conf':False,'col':4,'row':12,'padx':5, 'span':1,'width':10,'font':1,'just':'r','value':'Request On'       },
    {'reg':'Dout2Request',  'form':'switch','conf':False,'col':5,'row':12,'padx':5, 'span':1,'width':6, 'font':0,'just':'c','value':False              }]

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
    self.trueIndicator=  tk.PhotoImage(file=os.path.join(localDir,'img',trueIndicatorFile))
    self.falseIndicator= tk.PhotoImage(file=os.path.join(localDir,'img',falseIndicatorFile))
    self.setButton=      tk.PhotoImage(file=os.path.join(localDir,'img',setButtonFile))
    self.spacerImage=    tk.PhotoImage(file=os.path.join(localDir,'img',spacerFile))
    #place widgets
    for wid in self.widgets:
      newWid= None
      if wid['form']=='title':
        newWid= tk.Label(self,text=wid['value'],width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=wid['padx'],pady=padY)
      if wid['form']=='label':
        newWid= tk.Label(self,text=wid['value'],width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=wid['padx'],pady=padY)
      if wid['form']=='text':
        newWid= tk.Label(self,text=wid['value'],width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=wid['padx'],pady=padY)
      if wid['form']=='indtf':
        newWid= tk.Button(self,image=self.falseIndicator,height=16,width=48,relief=tk.FLAT)
        newWid.grid (column=wid['col'],row=wid['row'],padx=wid['padx'],pady=padY)
      if wid['form']=='switch':
        newWid= tk.Button(self,command=partial(self.set,wid['reg']),image=self.offSwitch,height=16,width=48,relief=tk.FLAT)
        newWid.grid (column=wid['col'],row=wid['row'],padx=wid['padx'],pady=padY)
      if wid['form']=='entry':
        newStr= tk.StringVar()
        newWid= tk.Entry(self,textvariable=newStr,width=wid['width'])
        newWid.grid (column=wid['col'],columnspan=wid['span'],row=wid['row'],padx=wid['padx'],pady=padY)
        wid['entry']= newStr
      if wid['form']=='send':
        newWid= tk.Button(self,command=partial(self.set,wid['reg']),image=self.sendArrow,height=16,width=24,relief=tk.FLAT)
        newWid.grid (column=wid['col'],row=wid['row'],padx=wid['padx'],pady=padY)
      if newWid!= None:
        if wid['font']==1:   newWid.configure(font=('Helvetica','10'))
        if wid['font']==2:   newWid.configure(font=('Helvetica','10','bold'))
        if wid['font']==3:   newWid.configure(font=('Helvetica','12','bold'))
        if wid['just']=='r': newWid.configure(anchor=tk.E,justify=tk.RIGHT)
        if wid['just']=='f': newWid.configure(justify=tk.RIGHT)
        if wid['just']=='l': newWid.configure(anchor=tk.W,justify=tk.LEFT)
        wid['widget']= newWid
    # top corner spacer
    spacer= tk.Label(self,image=self.spacerImage,width=10)
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
          if wid['form']=='send':
            for w in self.widgets:
              if w['reg']==reg and w['form']=='entry':
                wid['value']= w['entry'].get()
            self.controller.write(reg,wid['value'])
            self.delegates['EventLog']('{} set {}'.format(reg,wid['value']),True)

  #-- external methods --------------------------------------------------------

  def setDelegates(self,funcList):
    self.delegates= funcList

  def update(self):
    if self.controller.connected():
      for wid in self.widgets:
        if wid['form'] in ('indtf','switch','text','entry','send'):
          wid['widget'].configure(state=tk.NORMAL)
        if wid['form']=='indtf':
          wid['value']= self.controller.read(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.trueIndicator)
          else:
            wid['widget'].configure(image=self.falseIndicator)
        if wid['form']=='switch':
          wid['value']= self.controller.read(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.onSwitch)
          else:
            wid['widget'].configure(image=self.offSwitch)
        if wid['form']=='text':
          wid['value']= self.controller.read(wid['reg'])
          if isinstance(wid['value'],str):
            if wid['value']=='':
              wid['widget'].configure(text='--')
            else:
              wid['widget'].configure(text=wid['value'])
    else:
      for wid in self.widgets:
        if wid['form'] in ('indtf','switch','text','entry','send'):
          wid['widget'].configure(state=tk.DISABLED)

#-- End outputs.py ----------------------------------------------------------
