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
from   northlib.ntrp.northpipe import NorthPipe,NorthNRF
import northlib.ntrp.ntrp as ntrp
from   northlib.ncmd.northcom import NorthCOM
from   northswarm.math3d import *
import struct
import threading

class UavCOM(NorthCOM):
    
    UAVCOM_STATE_IDLE      = 0
    UAVCOM_STATE_READY     = 1
    UAVCOM_STATE_AUTO      = 2
    UAVCOM_STATE_MOVING    = 3
    UAVCOM_STATE_TAKEOFF   = 4
    UAVCOM_STATE_LAND      = 5

    UAV_CMD_ARM     = 1
    UAV_CMD_DISARM  = 2
    UAV_CMD_TAKEOFF = 3
    UAV_CMD_LAND    = 4
    UAV_CMD_MOVE    = 5
    UAV_CMD_YAW     = 6
    UAV_CMD_HOME    = 7
    UAV_CMD_KILL    = 8

    CMD_ID_UAV_CONTROLLER = 40

    def __init__(self, uri="radio:/0/76/2/E7E7E7E301"):
        super().__init__(uri)

        self.mode      = self.UAVCOM_STATE_IDLE
        self.modeFunc  = self._uavIdle
        self.uavThread = threading.Thread(target=self._uavTask, daemon=False)
        self.uavAlive  = False

    def start(self):
        #self.connect() # Wait Connection Sync
        self.connection = True # 1 Way Connection, Not ideal 
        if self.connection is not True: return
        self.uavAlive = True
        self.uavThread.start()

    def uavCMD(self, arg):
        """ ARM      : [1]
            DISARM   : [2]
            TAKEOFF  : [3, posz]
            LAND	 : [4]
            MOVE     : [5, posx, posy, posz]
            YAW		 : [6, rotz]
            HOME	 : [7]
            KILL     : [8]
        """
        self.txCMD(dataID = self.CMD_ID_UAV_CONTROLLER, channels = bytearray(arg))

    def setMode(self, mode=int):
        modeDict = {
            self.UAVCOM_STATE_IDLE    : self._uavIdle,
            self.UAVCOM_STATE_READY   : self._uavReady,
            self.UAVCOM_STATE_AUTO    : self._uavAuto,
            self.UAVCOM_STATE_TAKEOFF : self._uavTakeOff,
            self.UAVCOM_STATE_LAND    : self._uavLand,
        }
        self.mode     = mode
        self.modeFunc = modeDict[mode]
        
    def _uavTask(self):
        while self.uavAlive:
            self.modeFunc()
            time.sleep(0.03)

    def arm(self):
        self.uavCMD([self.UAV_CMD_ARM])
            
    def disarm(self):
        self.uavCMD([self.UAV_CMD_DISARM])
        
    def takeoff(self, posz:float = 3):
        arg = [self.UAV_CMD_TAKEOFF]
        arg.extend(struct.pack('<f', float(posz)))
        self.uavCMD(arg)

    def land(self):
        self.uavCMD([self.UAV_CMD_LAND])
    
    def move(self, pos=[0,0,0]): 
        arg = [self.UAV_CMD_MOVE]
        arg.extend(struct.pack('<f', float(pos[0])))
        arg.extend(struct.pack('<f', float(pos[1])))
        arg.extend(struct.pack('<f', float(pos[2])))
        self.uavCMD(arg)

    def yaw(self, rotz:float):
        arg = [self.UAV_CMD_YAW]
        arg.extend(struct.pack('<f', float(rotz)))
        self.uavCMD(arg)
    
    def home(self):
        self.uavCMD([self.UAV_CMD_HOME])

    def kill(self):
        self.uavCMD([self.UAV_CMD_KILL])

    def _uavIdle(self):
        self.disarm()
    
    def _uavReady(self):
        self.arm()

    def _uavAuto(self):
        self.move(pos = self.target)
    
    def _uavTakeOff(self):
        self.uavCMD([self.UAV_CMD_TAKEOFF])

    def _uavLand(self):
        self.land()

    def destroy(self):
        ts = 0
        while(ts < 1000):   
            self.kill()
            ts += 1

        self.setMode(self.UAVCOM_STATE_IDLE)
        self.uavAlive = False
        return super().destroy()
