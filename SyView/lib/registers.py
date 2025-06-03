#------------------------------------------------------------------------------
#  SyView registers
#
#  - Handle the registers tab
#
#  1Jul2022 A. Cooper
#  - initial version
#  29May2025 v2.0 A. Cooper
#  - replace SymCtrlModbus with SymbCtrlScan, a subprocess based comm handler
#  - alterations all through code to support new controller handler
#
#-- includes ------------------------------------------------------------------
import tkinter as tk
import os
from datetime import datetime
from tkinter import ttk, messagebox
from functools import partial

#-- globals -------------------------------------------------------------------
localDir= os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
imgPath=  os.path.join(localDir,'img')

# -- constants ----------------------------------------------------------------
subSizeX=         735
subSizeY=         390
sendArrowFile=    'sendArrow.png'
onSwitchFile=     'switchOn.png'
offSwitchFile=    'switchOff.png'
onIndicatorFile=  'indicatorOn.png'
offIndicatorFile= 'indicatorOff.png'
setButtonFile=    'setButton.png'
colGood=          '#000000'
colBad=           '#FFADAD'

#------------------------------------------------------------------------------
#  Registers Tab
#
#  - handle the registers tab
#
#------------------------------------------------------------------------------
class Registers(tk.Frame):
  globalMethods= []
  regs= {}

  def __init__(self, parent,controller):
    tk.Frame.__init__(self, master=parent)
    self.controller= controller
    for reg in self.controller.registers():
      self.regs[reg]= {'type':self.controller.type(reg),
                       'mode':self.controller.mode(reg)}
    self.grid()
    self.createWidgets()

  def createWidgets(self):
    padX= 4
    # images for the buttons
    self.sendArrow=    tk.PhotoImage(file=os.path.join(localDir,'img',sendArrowFile))
    self.onSwitch=     tk.PhotoImage(file=os.path.join(localDir,'img',onSwitchFile))
    self.offSwitch=    tk.PhotoImage(file=os.path.join(localDir,'img',offSwitchFile))
    self.onIndicator=  tk.PhotoImage(file=os.path.join(localDir,'img',onIndicatorFile))
    self.offIndicator= tk.PhotoImage(file=os.path.join(localDir,'img',offIndicatorFile))
    self.setButton=    tk.PhotoImage(file=os.path.join(localDir,'img',setButtonFile))
    # structural elements
    self.canvas=         tk.Canvas(self,width=subSizeX,height=subSizeY,bd=0,relief=tk.FLAT)
    self.canvas.grid     (column=0,row=0,padx=0,pady=0,sticky=tk.E+tk.W)
    self.scrollbar=      tk.Scrollbar(self,orient="vertical",command=self.canvas.yview)
    self.canvas.config   (yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid  (column=1,row=0,padx=0,pady=0,sticky=tk.N+tk.S+tk.W)
    self.subFrame=       tk.Frame(self.canvas,width=subSizeX-10,height=subSizeY-10)
    self.subFrame.bind   ('<Configure>',lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
    self.canvas.create_window((0,0),window=self.subFrame,anchor="nw")
    self.subFrame.bind   ('<Enter>', self.setMouseWheel)
    self.subFrame.bind   ('<Leave>', self.unsetMouseWheel)
    # data display fields
    for row,reg in enumerate(self.regs.keys()):
      label= tk.Label(self.subFrame,text=reg,width=20,anchor=tk.E,justify=tk.RIGHT)
      label.grid(column=1,row=row,padx=padX)
      label= tk.Label(self.subFrame,text=self.regs[reg]['type'])
      label.grid(column=3,row=row,padx=padX)
      label= tk.Label(self.subFrame,text=self.regs[reg]['mode'])
      label.grid(column=4,row=row,padx=padX)
      if self.regs[reg]['type']=='bool':
        if self.regs[reg]['mode']=='r':
          button= tk.Button(self.subFrame,image=self.offIndicator,height=16,width=48,relief=tk.FLAT)
          self.regs[reg]['entry']= False
        elif self.regs[reg]['mode']=='rw':
          button= tk.Button(self.subFrame,image=self.offSwitch,command=partial(self.toggle,reg),height=16,width=48,relief=tk.FLAT)
          self.regs[reg]['entry']= False
        else:
          button= tk.Button(self.subFrame,image=self.setButton,command=partial(self.set,reg),height=16,width=48,relief=tk.FLAT)
        button.grid(column=2,row=row,padx=padX)
        self.regs[reg]['button']= button
      else:
        if self.regs[reg]['mode']!='w':
          value= tk.Label(self.subFrame,text='123.45',width=16,font=('Helvetica','12','bold'))
          value.grid(column=2,row=row,padx=padX)
          self.regs[reg]['value']= value
        if self.regs[reg]['mode']!='r':
          entry= tk.StringVar()
          self.regs[reg]['entry']= entry
          eBox=  tk.Entry(self.subFrame,textvariable=entry,width=16)
          eBox.grid(column=5,row=row,padx=padX)
          send= tk.Button(self.subFrame,command=partial(self.send,reg),image=self.sendArrow,height=16,width=24,relief=tk.FLAT)
          send.grid(column=6,row=row,padx=padX)

  def setMouseWheel(self, event):
    self.subFrame.bind_all("<MouseWheel>", self.onMouseWheel)

  def unsetMouseWheel(self, event):
    self.subFrame.unbind_all("<MouseWheel>")

  def onMouseWheel(self, event):
    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

  def toggle(self,reg):
    if self.regs[reg]['entry']==False:
      self.regs[reg]['entry']= True
      self.regs[reg]['button'].config(image=self.onSwitch)
      self.controller.write(reg,True)
    else:
      self.regs[reg]['entry']= False
      self.regs[reg]['button'].config(image=self.offSwitch)
      self.controller.write(reg,False)
        
  def set(self,reg):
    if not self.controller.valid(): return
    if reg=='SaveSettings':
      if not messagebox.askyesno(title='Check that...',message='Save settings to EEPROM?'):
        return
    if reg=='ClearSettings':
      if not messagebox.askyesno(title='Check that...',message='Clear all controller settings?'):
        return
      if not messagebox.askyesno(title='Check that...',message='Confirm...  Clear all controller settings?'):
        return
    if reg=='ResetLogging':
      if not messagebox.askyesno(title='Check that...',message='Clear all logged data?'):
        return
    self.controller.write(reg,True)

  def send(self,reg):
    if not self.controller.valid(): return
    if self.regs[reg]['type']=='int':
      try: val= int(self.regs[reg]['entry'].get())
      except:
        messagebox.showwarning(title='Entry error...', message='Entry not an integer value!!')
        return
      if val<-32768 or val>32767:
        messagebox.showwarning(title='Entry error...', message='Integer must be between -32768 and 32767!!')
        return
      self.controller.write(reg,val)
      if self.controller.error:
        messagebox.showwarning(title='Write error...', message=self.controller.message())
    if self.regs[reg]['type']=='uint':
      try: val= int(self.regs[reg]['entry'].get())
      except:
        messagebox.showwarning(title='Entry error...', message='Entry not an integer value!!')
        return
      if val<0 or val>65535:
        messagebox.showwarning(title='Entry error...', message='Unsigned integer must be between 0 and 65535!!')
        return
      self.controller.write(reg,val)
      if self.controller.error:
        messagebox.showwarning(title='Write error...', message=self.controller.message())
    if self.regs[reg]['type']=='dint':
      try: val= int(self.regs[reg]['entry'].get())
      except:
        messagebox.showwarning(title='Entry error...', message='Entry not an integer value!!')
        return
      if val<0 or val>4294967295:
        messagebox.showwarning(title='Entry error...', message='Unsigned integer must be between 0 and 4294967295!!')
        return
      self.controller.write(reg,val)
      if self.controller.error:
        messagebox.showwarning(title='Write error...', message=self.controller.message())
    if self.regs[reg]['type']=='float':
      try: val= float(self.regs[reg]['entry'].get())
      except:
        messagebox.showwarning(title='Entry error...', message='Entry not a floating point number!!')
        return
      self.controller.write(reg,val)
      if self.controller.error:
        messagebox.showwarning(title='Write error...', message=self.controller.message())
    if self.regs[reg]['type']=='str':
      val= self.regs[reg]['entry'].get()
      if len(val)>16:
        messagebox.showwarning(title='Entry error...', message='Only first 16 characters will be used!')
        self.controller.write(reg,val)
        val= val[0:15]
      self.controller.write(reg,val)
      if self.controller.error:
        messagebox.showwarning(title='Write error...', message=self.controller.message())

  #-- external methods --------------------------------------------------------
  def setDelegates(self,methodList):
    self.globalMethods= methodList

  def update(self):
    if self.controller.valid():
      for reg in self.regs.keys():
        type= self.controller.type(reg)
        val=  self.controller.read(reg)
        if type=='bool':
          if self.regs[reg]['mode']!='w':
            if val==None:
              self.regs[reg]['button'].config(state=tk.DISABLED)
            elif self.regs[reg]['mode']=='r':
              if val:
                self.regs[reg]['entry']= True
                self.regs[reg]['button'].config(image=self.onIndicator,state=tk.NORMAL)
              else:
                self.regs[reg]['entry']= False
                self.regs[reg]['button'].config(image=self.offIndicator,state=tk.NORMAL)
            elif self.regs[reg]['mode']=='rw':
              if val:
                self.regs[reg]['entry']= True
                self.regs[reg]['button'].config(image=self.onSwitch,state=tk.NORMAL)
              else:
                self.regs[reg]['entry']= False
                self.regs[reg]['button'].config(image=self.offSwitch,state=tk.NORMAL)
            else:
              self.regs[reg]['button'].config(state=tk.NORMAL)
        elif self.regs[reg]['mode']!='w':
          if val==None:
            self.regs[reg]['value'].config(fg=colBad)
          else:
            if type=='int':
              self.regs[reg]['value'].config(text='{:d}'.format(val),fg=colGood)
            if type=='dint':
              self.regs[reg]['value'].config(text='{:d}'.format(val),fg=colGood)
            if type=='uint':
              self.regs[reg]['value'].config(text='{:d}'.format(val),fg=colGood)
            if type=='float':
              self.regs[reg]['value'].config(text='{:.2f}'.format(val),fg=colGood)
            if type=='str':
              self.regs[reg]['value'].config(text=val,fg=colGood)
    else:
      for reg in self.regs.keys():
        if self.controller.type(reg)=='bool':
          self.regs[reg]['button'].config(state=tk.DISABLED)
        else:
          self.regs[reg]['value'].config(fg=colBad)


#-- End registers.py ----------------------------------------------------------
