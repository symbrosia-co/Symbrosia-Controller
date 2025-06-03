#-- SymbCtrlScan Test Code ----------------------------------------------------
import os
import sys
import time
localDir= os.path.dirname(os.path.realpath(__file__))
sys.path.append(localDir)

import SymbCtrlScan as SyScan

def boolStr(val):
  if val!=None: 
    if val: return 'True '
    else:   return 'False'
  return 'None '
if __name__=='__main__':
  print('Startup scanner...')
  ctrl= SyScan.SymbCtrl()
  check= ctrl.start('192.168.200.41')
  print('    Start:    {:<8s}  Err: {:s}  Msg: {}'.format(boolStr(check),boolStr(ctrl.error),ctrl.message))
  for i in range(7):
    print('  Get test data {:d}...'.format(i))
    if ctrl!=None:
      for reg in ctrl.registers():
        print('    {:<16s}: {} Err: {:s}  Msg: {}'.format(reg,ctrl.textValue(reg,16,True),boolStr(ctrl.error),ctrl.message))
      if i==2:
        print('  Write...')
        ctrl.write('Ctrl1Enable',True)
        print('    Ctrl1Enb:   True     Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
        ctrl.write('Ctrl1Setpoint',8)
        print('    Ctrl1Set:   8.00     Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
        ctrl.write('Ctrl1Hysteresis',2)
        print('    Ctrl1Hyst:  2.00     Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
        ctrl.write('Relay1Request',True)
        print('    Relay1Req:  True     Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
        ctrl.write('ControlName','Test 1')
        print('    CtrlName: Test 1     Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
        ctrl.write('WQSensor',7)
        print('    WQSensor:   7.00     Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
      if i==4:
        print('  Write...')
        ctrl.write('Ctrl1Enable',False)
        print('    Ctrl1Enb:  False     Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
        ctrl.write('Ctrl1Setpoint',5)
        print('    Ctrl1Set:    5.00    Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
        ctrl.write('Ctrl1Hysteresis',1)
        print('    Ctrl1Hyst:   1.00    Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
        ctrl.write('Relay1Request',False)
        print('    Relay1Req: False     Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
        ctrl.write('ControlName','Test 2')
        print('    CtrlName: Test 1     Err: {:s}  Msg: {}'.format(boolStr(ctrl.error),ctrl.message))
    else:
      print('    Scanner not running')
    time.sleep(2)
  print('Close scanner...')
  if ctrl!=None:
    check= ctrl.close()
    print('    Close:    {:<8s}  Err: {:s}  Msg: {}'.format(boolStr(check),boolStr(ctrl.error),ctrl.message))
  else:
    print('Scanner not running')

#-- End Test Code -------------------------------------------------------------