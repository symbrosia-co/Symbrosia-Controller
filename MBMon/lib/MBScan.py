#------------------------------------------------------------------------------
#  ModbusTCP Scanner
#
#  - Maintain a data structure from a set of Modbus devices
#  - Use multiprocess to spawn a subprocesses to get data asychronously
#
#  External notes...
#  - mbScanner.start(map) should be called once to initiate scanning
#  - mbScanner.close()    will kill all subprocesses
#  - mbScanner.error      indicates the error status, 0=good, 1=com error, 2=read error
#  - mbScanner.errText    give the error reason in human readable text
#  - the register map is sent as a list of required devices and registers
#        [{'ipAddr':   <device IP address>,
#          'port':     <Modbus port>,
#          'name':     <register name>,
#          'register': <Modbus register number>,
#          'type':     <register type>}]
#  - type may be one of the following
#        hold:  one holding register as an unsigned integer
#        uint:  same as hold
#        int:   one holding resiter as signed integer
#        float: floating point using two holding registers as 32bit IEEE-754
#        coil:  one coil register as boolean
#        bool:  same as coil
#  
#  Internal notes...
#  - the data list will be compiled into a device and register list that
#    uses one or two transactions per modbus device, one for holding and one
#    for coil registers
#  - the register map is stored in a dict of dicts with a list of IP addresses and registers
#        mbScanner.datList= {<ipAddr>:
#            {'port':    <Modbus port>,
#             'name':    <data name>,
#             'register':<register number>,
#             'type':    <data type>}}
#  - the list of unique devices is compiled and stored in a dict of dicts
#        mbScanner.devList= {<ipAddr>+<reg name>:
#            {'port':<Modbus port>,
#             'holdStart':<first Modbus holding register>,
#             'holdStop': <last Modbus holding register>,
#             'coilStart':<first Modbus coil register>,
#             'coilStop': <last Modbus coil register>,
#             'proc':     <subprocess object>,
#             'data':     <subprocess shared array>}
#  - communication with the subprocess takes place through an array of integers
#        0:  message to subprocess, 0:none, -1:kill
#        1:  subprocess error, 0:none, 1:com error, 2:read error
#        2:  IP address byte 1
#        3:  IP address byte 2
#        4:  IP address byte 3
#        5:  IP address byte 4
#        6:  port
#        7:  start hold address
#        8:  end hold address
#        9:  first hold address
#        10: number of holding registers
#        11: start coil address
#        12: end coil address
#        13: first coil address
#        14: number of coil registers
#        15: scan time in seconds
#        16 to n: holding reg data
#        n+1 to m: coil reg data
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
from enum import IntEnum
from multiprocessing import Process, Array
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

class Share(IntEnum):
    SUBMSG   = 0
    ERROR    = 1
    IP1      = 2
    IP2      = 3
    IP3      = 4
    IP4      = 5
    PORT     = 6
    HOLDSTART= 7
    HOLDSTOP = 8
    HOLDFIRST= 9
    HOLDCOUNT= 10
    COILSTART= 11
    COILSTOP = 12
    COILFIRST= 13
    COILCOUNT= 14
    SCANTIME=  15
    FIRSTDATA= 16

#-- scanner class -------------------------------------------------------------

def scanSub(shared):
  debug= False
  comGood= False
  ipAddr= '{}.{}.{}.{}'.format(shared[Share.IP1],shared[Share.IP2],shared[Share.IP3],shared[Share.IP4])
  port= '{}'.format(shared[Share.PORT])
  # create a Modbus client object
  device= ModbusClient(debug=False)
  device.host(ipAddr)
  device.port(port)
  # freeze array indexes
  holdStart= shared[Share.HOLDSTART]
  holdStop=  shared[Share.HOLDSTOP]
  holdFirst= shared[Share.HOLDFIRST]
  holdCount= shared[Share.HOLDCOUNT]
  coilStart= shared[Share.COILSTART]
  coilStop=  shared[Share.COILSTOP]
  coilFirst= shared[Share.COILFIRST]
  coilCount= shared[Share.COILCOUNT]
  # scanning loop
  last= dt.datetime.now()-dt.timedelta(seconds=shared[Share.SCANTIME]+1)
  while True:
    # swallow poison pill and die
    if shared[Share.SUBMSG]==-1: 
      print('Scanner for {} terminating'.format(ipAddr))
      break
    # scan if time elapsed
    time.sleep(0.1)
    now= dt.datetime.now()
    if (now-last)>dt.timedelta(seconds=shared[Share.SCANTIME]):
      last= now
      if device.open():
        # holding registers
        if holdCount>0:
          if debug: print('Read holding regs for {}'.format(ipAddr))
          values= device.read_holding_registers(holdStart,holdCount)
          if values!=None: # place data in shared
            for i,val in enumerate(values):
              shared[holdFirst+i]= val
            shared[Share.ERROR]= 0 #no error
          else:
            if debug: print('  Read error!')
            shared[Share.ERROR]= 2 #set read failed error flag
        # coils
        if coilCount>0:
          if debug: print('Read coils for {}'.format(ipAddr))
          values= device.read_coils(coilStart,coilCount)
          if values!=None: # place data in shared
            for i,val in enumerate(values):
              if val:
                shared[coilFirst+i]= 1
              else:
                shared[coilFirst+i]= 0
            shared[Share.ERROR]= 0 #no error
          else:
            if debug: print('  Read error!')
            shared[Share.ERROR]= 2 #set read failed error flag
        device.close()
      else:
        if debug: print('  Com error!')
        shared[Share.ERROR]= 1 #set com error flag


class MBScanner():
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
                device['holdStop']= datum['register']
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
              newDev['coilStop']= datum['register']
            else:
              if datum['register']<device['coilStart']:
                device['coilStart']= datum['register']
              if datum['register']>device['coilStop']:
                device['coilStop']= datum['register']
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
          newDev['coilStop']= datum['register']
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
      # build shared array
      if dev['holdStop']!=None:
        arrLen= 1+dev['holdStop']-dev['holdStart']
      if dev['coilStop']!=None:
        arrLen= arrLen+1+dev['coilStop']-dev['coilStart']
      data= Array('i',arrLen+Share.FIRSTDATA)
      dev['data']= data
      # load the array with needed values
      data[Share.SUBMSG]= 0
      data[Share.ERROR]=  0
      for i in range(4):
        data[i+Share.IP1]= int(ipArr[i])
      data[Share.PORT]=  int(dev['port'])
      if dev['holdStart']!=None:
        data[Share.HOLDSTART]= dev['holdStart']
        data[Share.HOLDSTOP]=  dev['holdStop']
        data[Share.HOLDFIRST]= Share.FIRSTDATA
        data[Share.HOLDCOUNT]= dev['holdStop']-dev['holdStart']+1
      else:
        data[Share.HOLDSTART]= -1
        data[Share.HOLDSTOP]=  -1
        data[Share.HOLDFIRST]= -1
        data[Share.HOLDCOUNT]= 0
      if dev['coilStart']!=None:
        data[Share.COILSTART]= dev['coilStart']
        data[Share.COILSTOP]=  dev['coilStop']
        if dev['holdStart']!=None:
          data[Share.COILFIRST]= Share.FIRSTDATA+(dev['holdStop']-dev['holdStart'])+1
        else:
          data[Share.COILFIRST]= Share.FIRSTDATA
        data[Share.COILCOUNT]= dev['coilStop']-dev['coilStart']+1
      else:
        data[Share.COILSTART]= -1
        data[Share.COILSTOP]=  -1
        data[Share.COILFIRST]= -1
        data[Share.COILCOUNT]=  0
      data[Share.SCANTIME]= int(scanInt)
      # spawn the process
      print('Starting subprocess for {}'.format(ipAddr))
      dev['proc']= Process(target=scanSub,args=(data,))
      dev['proc'].start()

  # get the latest value of a particular datum
  def get(self,ipAddr,name):
    debug= False
    self.error= False
    self.errTxt= 'No error'
    if debug: print('Get {}...'.format(name))
    dat= '{}{}'.format(ipAddr,name)
    if dat in self.datList:
      reg= self.datList[dat]['register']
      typ= self.datList[dat]['type']
      if ipAddr in self.devList:
        shared= self.devList[ipAddr]['data']
        #self.printShared(shared)
        if shared[Share.ERROR]==1:
          if debug: print ('  Error! Unable to open {} for Modbus'.format(ipAddr))
          self.error= True
          self.errTxt= 'Unable to open {} for Modbus'.format(ipAddr)
          return None
        if shared[Share.ERROR]==2:
          if debug: print ('  Error! Unable read {} from {}'.format(name,ipAddr))
          self.error= True
          self.errTxt= 'Unable read {} from {}'.format(name,ipAddr)
          return None
        if shared[Share.ERROR]!=0:
          if debug: print ('  Error! Unknown error from {}'.format(ipAddr))
          self.error= True
          self.errTxt= 'Unknown error from {}'.format(ipAddr)
          return None
        if typ=='float':
          sharePos= reg+shared[Share.HOLDFIRST]-shared[Share.HOLDSTART]
          val= [shared[sharePos],shared[sharePos+1]]
          val= utils.word_list_to_long(val,big_endian=False)
          val= utils.decode_ieee(val[0])
          if debug: print('  Float {:0.4f} at reg {:d} shared {:d} [{:d},{:d}]'.format(val,reg,sharePos,shared[sharePos],shared[sharePos+1]))
          return val
        if typ=='hold' or typ=='uint':
          sharePos= reg+shared[Share.HOLDFIRST]-shared[Share.HOLDSTART]
          val= shared[sharePos]
          if debug: print('  Hold {:d} at reg {:d} shared {:d} [{:d}]'.format(val,reg,sharePos,shared[sharePos]))
          return val
        if typ=='int':
          sharePos= reg+shared[Share.HOLDFIRST]-shared[Share.HOLDSTART]
          val= shared[sharePos]
          if (val>>15) & 1:
            val= val-65536
          if debug: print('  Hold {:d} at reg {:d} shared {:d} [{:d}]'.format(val,reg,sharePos,shared[sharePos]))
          return val
        if typ=='long':
          sharePos= reg+shared[Share.HOLDFIRST]-shared[Share.HOLDSTART]
          valL= shared[sharePos]
          valH= shared[sharePos+1]
          val= valL+valH*65536
          if debug: print('  Long {:d} at reg {:d} shared {:d} [{:d},{:d}]'.format(val,reg,sharePos,shared[sharePos],shared[sharePos+1]))
          return val
        if typ=='coil' or typ=='bool':
          sharePos= reg+shared[Share.COILFIRST]-shared[Share.COILSTART]
          if shared[sharePos]: val= True
          else: val= False
          if debug: print('  Coil {} at reg {:d} shared {:d} [{}]'.format(val,reg,sharePos,shared[sharePos]))
          return val
        else:
          self.error= True
          self.errTxt= 'No such type {}'.format(typ)
          if debug: print ('  Error! No such type {}'.format(typ))
          return None
      else:
        self.error= True
        self.errTxt= 'No such device {}'.format(ipAddr)
        if debug: print ('  Error! No such device {}'.format(ipAddr))
        return None
    else:
      self.error= True
      self.errTxt= 'No such datum {}'.format(dat)
      if debug: print ('  Error! No such datum {}'.format(dat))
      return None
      
  # print shared memory report
  def printShared(self,shared):
    print('  IP Addr: {:d}.{:d}.{:d}.{:d}'.format(shared[Share.IP1],shared[Share.IP2],shared[Share.IP3],shared[Share.IP4]))
    print('  Port:    {:d}'.format(shared[Share.PORT]))
    print('  Scan:    {:d}s'.format(shared[Share.SCANTIME]))
    print('  Message: {:d}'.format(shared[Share.SUBMSG]))
    print('  Error:   {:d}'.format(shared[Share.ERROR]))
    if shared[Share.HOLDCOUNT]>0:
      print('  Hold:    {:d} registers {:d} to {:d} starting at shared {:d}'.format(shared[Share.HOLDCOUNT],shared[Share.HOLDSTART],shared[Share.HOLDSTOP],shared[Share.HOLDFIRST]))
      for i in range(shared[Share.HOLDCOUNT]):
        print('    {:2d}[{:02d}]: {:5d}'.format(i+shared[Share.HOLDSTART],i+shared[Share.HOLDFIRST],shared[i+shared[Share.HOLDFIRST]]))
    else:
      print('  No holding regs')
    if shared[Share.COILCOUNT]>0:
      print('  Coil:    {:d} coils {:d} to {:d} starting at shared {:d}'.format(shared[Share.COILCOUNT],shared[Share.COILSTART],shared[Share.COILSTOP],shared[Share.COILFIRST]))
      for i in range(shared[Share.COILCOUNT]):
        print('    {:2d}[{:02d}]: {}'.format(i+shared[Share.COILSTART],i+shared[Share.COILFIRST],shared[i+shared[Share.COILFIRST]]))
    else:
      print('  No coils')

  # close all subprocesses
  def close(self):
    for ip,dev in self.devList.items():
      dev['data'][Share.SUBMSG]= -1 #send poison pill
      dev['proc'].join()

#- test -----------------------------------------------------------------------

testList1= [{'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Din2',
             'register':9,
             'type':'coil'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Flash',
             'register':29,
             'type':'coil'}]
             
testList2= [{'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'pH',
             'register':20,
             'type':'float'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Internal',
             'register':30,
             'type':'float'}]
                      
testList3= [{'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'pH',
             'register':20,
             'type':'float'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Internal',
             'register':30,
             'type':'float'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Din2',
             'register':9,
             'type':'coil'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Flash',
             'register':29,
             'type':'coil'}]

testList4= [{'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'pH',
             'register':20,
             'type':'float'},
             {'ipAddr':'192.168.9.202',
             'port':'502',
             'name':'Internal',
             'register':30,
             'type':'float'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Din2',
             'register':9,
             'type':'coil'},
             {'ipAddr':'192.168.9.202',
             'port':'502',
             'name':'Flash',
             'register':29,
             'type':'coil'}]
             
testList5= [{'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Status',
             'register':0,
             'type':'uint'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Seconds',
             'register':16,
             'type':'int'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Time Zone',
             'register':10,
             'type':'int'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'pH',
             'register':20,
             'type':'float'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Internal',
             'register':30,
             'type':'float'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Supply Voltage',
             'register':32,
             'type':'float'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Timer',
             'register':155,
             'type':'long'},             
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Status',
             'register':0,
             'type':'coil'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Toggle',
             'register':9,
             'type':'coil'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Flash',
             'register':29,
             'type':'coil'},
             {'ipAddr':'192.168.9.66',
             'port':'502',
             'name':'Ctrl4 OneShot',
             'register':69,
             'type':'coil'}]

if __name__=='__main__':
  list= testList5
  mb= MBScanner();
  mb.start(list,2)
  count= 0
  while count<5:
    for data in list:
      val= mb.get(data['ipAddr'],data['name'])
      if (mb.error)!=0:
        print('Error! {}'.format(mb.errTxt))
      else:
        if data['type']=='float':
          print('  {}: {:.2f}'.format(data['name'],val))
        if data['type']=='coil':  
          print('  {}: {}'.format(data['name'],val))
    print(' ')
    print(' ')
    time.sleep(5)
    count+=1
  mb.close()

#-- end MBScanner -------------------------------------------------------------


