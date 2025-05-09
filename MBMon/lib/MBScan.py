#------------------------------------------------------------------------------
#  ModbusTCP Scanner
#
#  - Maintain a data structure from a set of Modbus devices
#  - Use a multiprocess to spawn a subprocesses to get data
#  - data is stored in a list of dicts with a list of IP addresses and registers
#
#    [{'ipAddr':<IP Address>,
#      'port':<port number>,
#      'name':<data name>,
#      'register':<register number>,
#      'type':<data type>,
#      'value':<current value>,
#      'valid':<data valid?>,
#      'error':<error code>}]
#
#  - the data list will be compiled into a device and register list that
#  uses one or two transactions per modbus device, one for holding and one
#  for coil registers
#  - start should be called once to initiate scanning
#  - scan should be called regularly to keep data fresh
#  - close will kill all subprocesses
#  - communication with the subprocess takes place through an array on integers
#
#    0:  message to subprocess, 0:none, -1:kill
#    1:  message from subprocess, 0:none, 1:com error
#    2:  IP address byte 1
#    3:  IP address byte 2
#    4:  IP address byte 3
#    5:  IP address byte 4
#    6:  port
#    7:  start hold address
#    8:  end hold address
#    9:  start coil address
#    10: end coild address
#    11: scan time in seconds
#    12 to n: holding reg data
#    n+1 to m: coil reg data
#
#  Symbrosia
#  Copyright 2021-2025, all rights reserved
#
# 30Apr2025 A. Cooper
#  - initial version
#
# Remaining to do:
# - add input qualification
#
#------------------------------------------------------------------------------

#-- library -------------------------------------------------------------------
import os
import datetime as dt
import time
import ipaddress
from multiprocessing import Process, Array
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

#-- scanner class -------------------------------------------------------------
class mbScanner():
  devList= {}
  datList= {}
  scanInt= 60
  lastScan= dt.datetime.now();
  stat= True
  errTxt= 'No error'

  def start(self,data,scanInt):
    self.devList= {}
    self.datList= {}
    self.scanInt= scanInt
    if scanInt<1:   scanInt= 1
    if scanInt>600: scanInt= 600
    for datum in data:
      found= False
      for ipAddr,device in self.devList.items():
        if datum['ipAddr']==ipAddr:
          found= True
          if datum['type']=='int' or datum['type']=='uint':
            if device['holdStart']==None:
              newDev['holdStart']= datum['register']
              newDev['holdStop']= datum['register']
            else:
              if datum['register']<device['holdStart']:
                device['holdStart']= datum['register']
              if datum['register']>device['holdStop']:
                device['holdSop']= datum['register']
          if datum['type']=='long' or datum['type']=='float':
            if device['holdStart']==None:
              newDev['holdStart']= datum['register']
              newDev['holdStop']= datum['register']+1
            else:
              if datum['register']<device['holdStart']:
                device['holdStart']= datum['register']
              if datum['register']>device['holdStop']:
                device['holdStop']= datum['register']+1
          if datum['type']=='string':
            if device['holdStart']==None:
              device['holdStart']= datum['register']
              device['holdStop']= datum['register']+datum['length']
            else:
              if datum['register']<device['holdStart']:
                device['holdStart']= datum['register']
              if datum['register']+datum['length']>device['holdStop']:
                device['holdStop']= datum['register']+datum['length']
          if datum['type']=='coil':
            if device['coilStart']==None:
              newDev['coilStart']= datum['register']
              newDev['holdStop']= datum['register']
            else:
              if datum['register']<device['coilStart']:
                device['coilStart']= datum['register']
              if datum['register']>device['coilStop']:
                device['holdStop']= datum['register']
      if not found:
        newDev= {'port':datum['port'],'holdStart':None,'holdStop':None,'coilStart':None,'coilStop':None,'proc':None}
        if datum['type']=='int' or datum['type']=='uint':
          newDev['holdStart']= datum['register']
          newDev['holdStop']= datum['register']
        if datum['type']=='long' or datum['type']=='float':
          newDev['holdStart']= datum['register']
          newDev['holdStop']= datum['register']+1
        if datum['type']=='string':
          device['holdStart']= datum['register']
          device['holdStop']= datum['register']+datum['length']
        if datum['type']=='coil':
          newDev['coilStart']= datum['register']
          newDev['holdStop']= datum['register']
        self.devList[datum['ipAddr']]= newDev
      # generate internal data list
      self.datList['{}{}'.format(datum['ipAddr'],datum['name'])]= {'register':datum['register'],'type':datum['type']}
    # generate subprocesses
    for ipAddr,dev in self.devList.items():
      arrLen= 0
      # parse ip address
      try:
        ipaddress.ip_address(ipAddr)
      except ValueError:
        dev['error']= 1
        continue
      ipArr= ipAddr.split(".")
      # build mailbox array
      if dev['holdStop']!=None:
        arrLen= 1+dev['holdStop']-dev['holdStart']
      if dev['coilStop']!=None:
        arrLen= arrLen+1+dev['coilStop']-dev['coilStart']
      dev['data']= Array('i',arrLen+12)
      #load the array with needed values
      dev['data'][0]= 0
      dev['data'][1]= 0
      for i in range(4):
        dev['data'][i+2]= int(ipArr[i])
      dev['data'][6]=  int(dev['port'])
      if dev['holdStart']!=None:
        dev['data'][7]=  dev['holdStart']
      else:
        dev['data'][7]= -1
      if dev['holdStop']!=None:
        dev['data'][8]=  dev['holdStop']
      else:
        dev['data'][8]= -1
      if dev['coilStart']!=None:
        dev['data'][9]= dev['coilStart']
      else:
        dev['data'][9]= -1
      if dev['coilStop']!=None:
        dev['data'][10]= dev['coilStop']
      else:
        dev['data'][10]= -1
      dev['data'][11]= scanInt
      #span the process
      dev['proc']= Process(target=self.scanSub,args=(dev['data'],))
      dev['proc'].start()
      print(dev['proc'])
      
  def scanSub(self,shared):
    comGood= False
    ipAddr= '{}.{}.{}.{}'.format(shared[2],shared[3],shared[4],shared[5])
    port= '{}'.format(shared[6])
    device= ModbusClient(debug=False)
    device.host(ipAddr)
    device.port(port)
    holdStart= shared[7]
    holdStop=  shared[8]
    coilStart= shared[9]
    coilStop=  shared[10]
    scan=      shared[11]
    last= dt.datetime.now()
    while True:
      #recieve poison pill
      if shared[1]==-1: 
        print('Subprocess {} terminating'.format(ipAddr))
        break
      now= dt.datetime.now()
      if (now-last)>dt.timedelta(seconds=scan):
        last= now
        if device.open():
          shared[1]= 0 #no error
          # holding registers
          if holdStart!=-1:
            print('Read holding regs for {}'.format(ipAddr))
            values= device.read_holding_registers(holdStart,holdStop-holdStart+1)
            print(values)
            if values!=None: # place data in shared
              for i,val in enumerate(values):
                shared[12+i]= val
            else:
              shared[1]= 2 #set com error flag
          # coils
          if coilStart!=-1:
            print('Read coils for {}'.format(ipAddr))
            values= device.read_coils(coilStart,coilStop-coilStart+1)
            print(values)
            if values!=None: # place data in shared
              for i,val in enumerate(values):
                shared[13+(holdStop-holdStart)+i]= val
            else:
              shared[1]= 2 #set com error flag
          device.close()
        else:
          shared[1]= 1 #set com error flag

  # get the latest value of a particular datum
  def get(self,ipAddr,name):
    self.stat= True
    self.errTxt= 'No error'
    print('Get value...')
    print(self.datList)
    print(self.devList)
    dev= '{}{}'.format(ipAddr,name)
    if dev in self.datList:
      reg= self.datList[dev]['register']
      typ= self.datList[dev]['type']
      print(self.datList[dev])
      if '{}{}'.format(ipAddr,name) in self.devList:
        
        if typ=='float':
          val= [[0],[0]]
          val= utils.word_list_to_long(val,big_endian=False)
          val= utils.decode_ieee(val[0])
          print(val)
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
      else:
        self.stat= False
        self.errTxt= ''
        return None
    else:
      self.stat= False
      self.errTxt= ''
      return None

  def close(self):
    for ip,dev in self.devList.items():
      dev['data'][1]= -1 #send poison pill
      dev['proc'].join()

  # decode error codes into human readable string
  def error(errorCode):
    if errorCode==0: return 'No error'
    if errorCode==1: return 'Unable to open connection'
    if errorCode==2: return 'Connection timeout'
    if errorCode==3: return 'Stale value'
    if errorCode==4: return 'Illegal value'

#- test -----------------------------------------------------------------------
testList1= []
testList2= [{'ipAddr':'192.168.200.60',
             'port':'502',
             'name':'Temperature',
             'register':20,
             'type':'float',
             'length': 2,
             'value':0.0,
             'valid':True,
             'error':0},
             {'ipAddr':'192.168.200.60',
             'port':'502',
             'name':'Ambient',
             'register':22,
             'type':'float',
             'length': 2,
             'value':0.0,
             'valid':True,
             'error':0}]

if __name__=='__main__':
  mb= mbScanner();
  mb.start(testList2,2)
  count= 0
  while count<6:
    time.sleep(5)
    val= mb.get('192.168.200.60','Temperature')
    if val!=None:
      print(val)
    else:
      print('Read error!')
    count+=1
  mb.close()

#-- end MBScanner -------------------------------------------------------------


