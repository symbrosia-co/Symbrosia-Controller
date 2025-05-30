#------------------------------------------------------------------------------
#  SyView misc
#
#  - Handle the misc tab
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
outChan=   {'None':0,'Relay 1':11,'Relay 2':12,'Output 1':13,'Output 2':14,'Virtual 1':15,'Virtual 2':16}
digChan=   {'None':0,'Input 1':9,'Input 2':10,'Relay 1':11,'Relay 2':12,'Output 1':13,'Output 2':14,'Virtual 1':15,'Virtual 2':16,
            'Control 1 Out':17,'Control 2 Out':18,'Control 3 Out':19,'Control 4 Out':20,
            'Control Alarm':21,'Control 1 Alarm':22,'Control 2 Alarm':23,'Control 3 Alarm':24,'Control 4 Alarm':25,
            'Control 1 Alarm Low':26,'Control 2 Alarm Low':27,'Control 3 Alarm Low':28,'Control 4 Alarm Low':29,
            'Control 1 Alarm High':30,'Control 2 Alarm High':31,'Control 3 Alarm High':32,'Control 4 Alarm High':33,'Flasher':34}
logicFunc= {'NOT':0,'AND':1,'NAND':2,'OR':3,'NOR':4,'XOR':5,'NXOR':6}
resetIntv= {'No Reset':0,'Reset Hourly':1,'Reset Daily':2,'Reset Monthly':3}

#------------------------------------------------------------------------------
#  Misc Tab
#
#  - handle the misc tab
#
#------------------------------------------------------------------------------
class Misc(tk.Frame):

  def __init__(self, parent, controller):
    self.widgets= [
      # time of day
      {'reg':None,              'form':'label', 'col':1, 'row':1, 'span':2, 'width':16,'font':3,'just':'l','value':'Time of Day'      },
      {'reg':None,              'form':'label', 'col':1, 'row':2, 'span':1, 'width':5, 'font':1,'just':'r','value':'Start'            },
      {'reg':'ToDStart',        'form':'time',  'col':2, 'row':2, 'span':1, 'width':6, 'font':2,'just':'l','value':'--:--'            },
      {'reg':'ToDStartHour',    'form':'entry', 'col':3, 'row':2, 'span':1, 'width':5, 'font':1,'just':'w','value':None               },
      {'reg':None,              'form':'label', 'col':4, 'row':2, 'span':1, 'width':1, 'font':3,'just':'l','value':':'                },
      {'reg':'ToDStartMin',     'form':'entry', 'col':5, 'row':2, 'span':1, 'width':5, 'font':1,'just':'w','value':None               },
      {'reg':'ToDStart',        'form':'send',  'col':6, 'row':2, 'span':1, 'width':20,'font':1,'just':'l','value':None               },
      {'reg':None,              'form':'label', 'col':1, 'row':3, 'span':1, 'width':5, 'font':1,'just':'r','value':'Stop'             },
      {'reg':'ToDStop',         'form':'time',  'col':2, 'row':3, 'span':1, 'width':6, 'font':2,'just':'l','value':'--:--'            },
      {'reg':'ToDStopHour',     'form':'entry', 'col':3, 'row':3, 'span':1, 'width':5, 'font':1,'just':'w','value':None               },
      {'reg':None,              'form':'label', 'col':4, 'row':3, 'span':1, 'width':1, 'font':3,'just':'l','value':':'                },
      {'reg':'ToDStopMin',      'form':'entry', 'col':5, 'row':3, 'span':1, 'width':5, 'font':1,'just':'w','value':None               },
      {'reg':'ToDStop',         'form':'send',  'col':6, 'row':3, 'span':1, 'width':20,'font':1,'just':'l','value':None               },
      {'reg':None,              'form':'label', 'col':8, 'row':1, 'span':1, 'width':1, 'font':1,'just':'r','value':'Enable'           },
      {'reg':'ToDEnable',       'form':'switch','col':9, 'row':1, 'span':1, 'width':48,'font':0,'just':'l','value':None               },
      {'reg':'ToDOutput1',      'form':'ochan', 'col':8, 'row':2, 'span':1, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'ToDOutput2',      'form':'ochan', 'col':8, 'row':3, 'span':1, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'ToDOutput3',      'form':'ochan', 'col':9, 'row':2, 'span':1, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'ToDOutput4',      'form':'ochan', 'col':9, 'row':3, 'span':1, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':None,              'form':'label', 'col':10,'row':2, 'span':1, 'width':1, 'font':1,'just':'l','value':'Active'           },
      {'reg':'ToDActive',       'form':'indtf', 'col':10,'row':3, 'span':1, 'width':48,'font':0,'just':'l','value':False              },
      {'reg':None,              'form':'space', 'col':8, 'row':4, 'span':1, 'width':12,'font':1,'just':'l','value':None               },
      {'reg':None,              'form':'space', 'col':9, 'row':4, 'span':1, 'width':12,'font':1,'just':'l','value':None               },
      {'reg':None,              'form':'sephz', 'col':1, 'row':5, 'span':10,'width':0, 'font':0,'just':'n','value':None               },
      # counter and timer
      {'reg':None,              'form':'label', 'col':1, 'row':6, 'span':2, 'width':16,'font':3,'just':'l','value':'Counter'          },
      {'reg':'CountSource',     'form':'dchan', 'col':1, 'row':7, 'span':2, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'CountRstIntv',    'form':'rintv', 'col':1, 'row':8, 'span':2, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'Counter',         'form':'dint',  'col':3, 'row':7, 'span':2, 'width':8, 'font':1,'just':'r','value':None               },
      {'reg':'ResetCounter',    'form':'button','col':3, 'row':8, 'span':2, 'width':48,'font':0,'just':'r','value':None               },
      {'reg':None,              'form':'label', 'col':7, 'row':6, 'span':2, 'width':16,'font':3,'just':'l','value':'Timer'            },
      {'reg':'TimerSource',     'form':'dchan', 'col':7, 'row':7, 'span':2, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'TimerRstIntv',    'form':'rintv', 'col':7, 'row':8, 'span':2, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'Timer',           'form':'dint',  'col':9, 'row':7, 'span':1, 'width':8, 'font':1,'just':'r','value':None               },
      {'reg':'ResetTimer',      'form':'button','col':9, 'row':8, 'span':1, 'width':48,'font':0,'just':'r','value':None               },
      {'reg':None,              'form':'space', 'col':7, 'row':9, 'span':1, 'width':4, 'font':1,'just':'l','value':None               },
      {'reg':None,              'form':'sephz', 'col':1, 'row':10,'span':10,'width':0, 'font':0,'just':'n','value':None               },
      # logic gate
      {'reg':None,              'form':'label', 'col':1, 'row':11,'span':2, 'width':16,'font':3,'just':'l','value':'Logic Gate'       },
      {'reg':'LogicInA',        'form':'dchan', 'col':1, 'row':12,'span':2, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'LogicInB',        'form':'dchan', 'col':1, 'row':13,'span':2, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'LogicFunction',   'form':'lfunc', 'col':3, 'row':12,'span':3, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'LogicOut',        'form':'ochan', 'col':3, 'row':13,'span':3, 'width':0, 'font':1,'just':'l','value':None               },
      {'reg':'LogicGateResult', 'form':'indtf', 'col':6, 'row':12,'span':2, 'width':48,'font':0,'just':'l','value':False              },]
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
      if wid['form']=='label' or wid['form']=='time':
        newWid= tk.Label(self,text=wid['value'],width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='sephz':
        newWid= ttk.Separator(self, orient='horizontal')
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY,sticky=tk.W+tk.E)
      if wid['form']=='space':
        newWid= tk.Label(self,text=' ',width=wid['width'])
        newWid.grid (column=wid['col'],row=wid['row'],columnspan=wid['span'],padx=padX,pady=padY)
      if wid['form'] in ['int','dint','float','input','unitin','unitd','sethi','setlo']:
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
      if wid['form']=='dchan':
        newStr= tk.StringVar()
        newStr.set(list(digChan.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*digChan,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=padX,row=wid['row'],pady=padY,sticky=tk.W+tk.E)
        wid['entry']= newStr
      if wid['form']=='ochan':
        newStr= tk.StringVar()
        newStr.set(list(outChan.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*outChan,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=padX,row=wid['row'],pady=padY,sticky=tk.W+tk.E)
        wid['entry']= newStr
      if wid['form']=='lfunc':
        newStr= tk.StringVar()
        newStr.set(list(logicFunc.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*logicFunc,command=partial(self.setMenu,wid['reg']))
        newWid.grid (column=wid['col'],columnspan=wid['span'],padx=padX,row=wid['row'],pady=padY,sticky=tk.W+tk.E)
        wid['entry']= newStr
      if wid['form']=='rintv':
        newStr= tk.StringVar()
        newStr.set(list(resetIntv.keys())[0])
        newWid= tk.OptionMenu(self,newStr,*resetIntv,command=partial(self.setMenu,wid['reg']))
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
                  value= w['widget'].get()[:16]
                  valid= True
            if valid:
              wid['value']= value
              if self.controller.write(reg,wid['value']):
                self.delegates['EventLog']('{} set to {}'.format(reg,wid['value']),True)
              else:
                self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
            if self.controller.type(reg)=='hour':
              for w in self.widgets:
                if w['reg']!=None:
                  if reg in w['reg']:
                    try: value= int(w['widget'].get())
                    except:
                      self.delegates['EventLog']('Write error to {}! Improper value'.format(reg),True)
                    else:
                      w['value']= value
                      if self.controller.write(w['reg'],value):
                        self.delegates['EventLog']('{} set to {}'.format(reg,w['value']),True)
                      else:
                        self.delegates['EventLog']('Write error to {}! {}'.format(w['reg'],self.controller.message()),True)

  def setMenu(self,reg,selection):
    if self.controller.connected():
      for wid in self.widgets:
        if wid['reg']==reg:
          if wid['form']=='dchan':
            if self.controller.write(reg,digChan[selection]):
              self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
          if wid['form']=='ochan':
            if self.controller.write(reg,outChan[selection]):
              self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
          if wid['form']=='lfunc':
            if self.controller.write(reg,logicFunc[selection]):
              self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)
          if wid['form']=='rintv':
            if self.controller.write(reg,resetIntv[selection]):
              self.delegates['EventLog']('{} set to {}'.format(reg,selection),True)
            else:
              self.delegates['EventLog']('Write error to {}! {}'.format(reg,self.controller.message()),True)

  #-- external methods --------------------------------------------------------

  def setDelegates(self,funcList):
    self.delegates= funcList

  def update(self):
    for wid in self.widgets:
      if wid['form']=='int' or wid['form']=='dint':
        if not self.controller.connected():
          wid['widget'].configure(text='--',state=tk.DISABLED)
          wid['value']= None
        elif wid['reg']== None:
          wid['widget'].configure(text='--',state=tk.NORMAL)
          wid['value']= None
        else:
          wid['value']= self.controller.read(wid['reg'])
          if isinstance(wid['value'],int):
            wid['widget'].configure(text='{:d}'.format(wid['value']),state=tk.NORMAL)
      if wid['form']=='time':
        if not self.controller.connected():
          wid['widget'].configure(text='--:--',state=tk.DISABLED)
          wid['value']= None
        elif wid['reg']== None:
          wid['widget'].configure(text='--',state=tk.NORMAL)
          wid['value']= None
        else:
          wid['value']= self.controller.read(wid['reg'])  
          if isinstance(wid['value'],str):
            wid['widget'].configure(text='{}'.format(wid['value']),state=tk.NORMAL)
      if wid['form']=='float':
        if not self.controller.connected():
          wid['widget'].configure(text='-.--',state=tk.DISABLED)
          wid['value']= None
        elif wid['reg']== None:
          wid['widget'].configure(text='-.--',state=tk.NORMAL)
          wid['value']= None
        else:
          wid['value']= self.controller.read(wid['reg'])
          if isinstance(wid['value'],float):
            wid['widget'].configure(text='{:.2f}'.format(wid['value']),state=tk.NORMAL)
      if wid['form']=='button':
        if self.controller.connected():
            wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='switch':
        if self.controller.connected():
          wid['value']= self.controller.read(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.onSwitch,state=tk.NORMAL)
          else:
            wid['widget'].configure(image=self.offSwitch,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None 
      if wid['form']=='indoo':
        if self.controller.connected():
          wid['value']= self.controller.read(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.onIndicator,state=tk.NORMAL)
          else:
            wid['widget'].configure(image=self.offIndicator,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='indtf':
        if self.controller.connected():
          wid['value']= self.controller.read(wid['reg'])
          if wid['value']:
            wid['widget'].configure(image=self.trueIndicator,state=tk.NORMAL)
          else:
            wid['widget'].configure(image=self.falseIndicator,state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
          wid['value']= None
      if wid['form']=='label':
        if wid['reg']!=None:
          if self.controller.connected():
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
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='send':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='ochan':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in outChan.keys():
            if outChan[entry]==self.controller.read(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='dchan':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in digChan.keys():
            if digChan[entry]==self.controller.read(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='rintv':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in resetIntv.keys():
            if resetIntv[entry]==self.controller.read(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)
      if wid['form']=='lfunc':
        if self.controller.connected():
          wid['widget'].configure(state=tk.NORMAL)
          for entry in logicFunc.keys():
            if logicFunc[entry]==self.controller.read(wid['reg']):
              wid['entry'].set(entry)
        else:
          wid['widget'].configure(state=tk.DISABLED)

#-- End misc.py ---------------------------------------------------------------
