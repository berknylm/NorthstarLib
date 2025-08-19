#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  __  __ ____ _  __ ____ ___ __  __
#  \ \/ // __// |/ //  _// _ |\ \/ /
#   \  // _/ /    /_/ / / __ | \  / 
#   /_//___//_/|_//___//_/ |_| /_/  
# 
#   2024 Yeniay Uav Flight Control Systems
#   Research and Development Team

import sys
sys.path.append('./')

import time
import northlib.ntrp as radioManager
from   northlib.ntrp.northpipe import NorthNRF
import northlib.ncmd.controller as ncmd

RCCOM_STATE_HEIGHT = 2
RCCOM_STATE_NAV    = 3

# PID : 0.9 ... 21 : FAIL

# PID : 0.9 ... 30 : FAIL

# PID : 0.9 ... 12 : OK

if __name__ == '__main__':

    print("RCCOM Application")

    radioManager.radioSearch()
    if len(radioManager.availableRadios) == 0:  sys.exit()
    
    uavcom = NorthNRF(ch=84)
 
    ctrl = ncmd.Controller(True)
    
    if ctrl.findController():
        ctrl.start_polling()
        try:
            while uavcom.radio.isRadioAlive():
                ctrl.update()
                time.sleep(ctrl.THREAD_SLEEP)
                cmd = ctrl.getAxis()
                if cmd[4] != 0: cmd[4] = RCCOM_STATE_HEIGHT
                uavcom.txCMD(channels=cmd, force=True)
        except KeyboardInterrupt:
            print("Keyboard Interrupt")

    ctrl.destroy()
    uavcom.destroy()
    radioManager.closeAvailableRadios()
    
    print("RCCOM Exit")
    sys.exit()