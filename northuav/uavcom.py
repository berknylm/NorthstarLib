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
from   northuav.math3d import *
import struct
import threading

class UavEXE():
    UAVEXE_PACKET_ID       = 42

    UAVEXE_CMD_PARSE       = 0
    UAVEXE_CMD_SET         = 1
    UAVEXE_CMD_LAUNCH      = 2
    
    UAVEXE_FID_DELAY       = 0
    UAVEXE_FID_UAVCMD      = 1
    UAVEXE_FID_PRINT       = 2

    def uavexeCMD_PARSE(self, fid, arg):
        cmd = [self.UAVEXE_CMD_PARSE, fid]
        cmd.extend(arg)
        return cmd
    
    def uavexeCMD_SET(self, fid, arg):
        cmd = [self.UAVEXE_CMD_SET, fid]
        cmd.extend(arg)
        return cmd
    
    def uavexeCMD_LAUNCH(self):
        return [self.UAVEXE_CMD_LAUNCH]
    
    def exe_DELAY(self, seconds, setcmd=False):
        arg = list(struct.pack('<I', int(seconds * 1000))) #Milliseconds as bytes uint32
        if setcmd: 
            cmd = self.uavexeCMD_SET(self.UAVEXE_FID_DELAY, arg)
            self.txCMD(dataID=self.UAVEXE_PACKET_ID, channels=bytearray(cmd))
        else:      
            cmd = self.uavexeCMD_PARSE(self.UAVEXE_FID_DELAY, arg)
            self.txCMD(dataID=self.UAVEXE_PACKET_ID, channels=bytearray(cmd))
    
    def exe_UAVCMD(self, arg, setcmd=False):
        if setcmd: 
            cmd = self.uavexeCMD_SET(self.UAVEXE_FID_UAVCMD, arg)
            self.txCMD(dataID=self.UAVEXE_PACKET_ID, channels=bytearray(cmd))
        else:      
            cmd = self.uavexeCMD_PARSE(self.UAVEXE_FID_UAVCMD, arg)
            self.txCMD(dataID=self.UAVEXE_PACKET_ID, channels=bytearray(cmd))
    
    def exe_PRINT(self, string:str, setcmd=False):
        arg = list(bytes(string, 'utf-8'))
        if setcmd: 
            cmd = self.uavexeCMD_SET(self.UAVEXE_FID_PRINT, arg)
            self.txCMD(dataID=self.UAVEXE_PACKET_ID, channels=bytearray(cmd))
        else:      
            cmd = self.uavexeCMD_PARSE(self.UAVEXE_FID_PRINT, arg)
            self.txCMD(dataID=self.UAVEXE_PACKET_ID, channels=bytearray(cmd))
    
    def launch(self):
        """Execute all queued commands"""
        cmd = self.uavexeCMD_LAUNCH()
        self.txCMD(dataID=self.UAVEXE_PACKET_ID, channels=bytearray(cmd))

class UavCOM(NorthCOM, UavEXE):
    
    UAVCOM_STATE_IDLE      = 0
    UAVCOM_STATE_READY     = 1
    UAVCOM_STATE_AUTO      = 2
    UAVCOM_STATE_MOVING    = 3
    UAVCOM_STATE_TAKEOFF   = 4
    UAVCOM_STATE_LAND      = 5

    UAV_CMD_ARM            = 1
    UAV_CMD_DISARM         = 2
    UAV_CMD_TAKEOFF        = 3
    UAV_CMD_LAND           = 4
    UAV_CMD_MOVE           = 5
    UAV_CMD_YAW            = 6
    UAV_CMD_HOME           = 7
    UAV_CMD_KILL           = 8
    UAV_CMD_ORIGIN         = 9
    UAV_CMD_ORIGIN         = 9

    UAVCOM_PACKET_ID       = 40
    
    def __init__(self, uri="radio:/0/72/2/E7E7E7E301"):
        super().__init__(uri)

        self.mode      = self.UAVCOM_STATE_IDLE
        self.modeFunc  = self._uavIdle
        self.uavThread = threading.Thread(target=self._uavTask, daemon=False)
        self.uavAlive  = False

        self.position = [0.0, 0.0, 0.0] # Position Self Frame
        self.posBias  = [0.0, 0.0, 0.0] # Start Position
        self.heading  =  0.0            # Rotation Self Frame
        self.target   = [0.0, 0.0, 0.0] # Target position for auto mode

    def start(self):
        #self.connect() # Wait Connection Sync
        self.connection = True # 1 Way Connection, Not ideal 
        if self.connection is not True: return
        self.uavAlive = True
        self.uavThread.start()

    def uavCMD(self, arg, setcmd=False):
        """ ARM      : [1]
            DISARM   : [2]
            TAKEOFF  : [3, posz]
            LAND	 : [4]
            MOVE     : [5, posx, posy, posz]
            YAW		 : [6, rotz]
            HOME	 : [7]
            KILL     : [8]
        """
        if setcmd:
            self.exe_UAVCMD(arg, setcmd=True)
        else:
            self.txCMD(dataID = self.UAVCOM_PACKET_ID, channels = bytearray(arg))

    def arm(self, setcmd=False):
        self.uavCMD([self.UAV_CMD_ARM], setcmd)
            
    def disarm(self, setcmd=False):
        self.uavCMD([self.UAV_CMD_DISARM], setcmd)
        
    def takeoff(self, posz:float = 3, setcmd=False):
        arg = [self.UAV_CMD_TAKEOFF]
        arg.extend(struct.pack('<f', float(posz)))
        self.uavCMD(arg, setcmd)

    def land(self, setcmd=False):
        self.uavCMD([self.UAV_CMD_LAND], setcmd)
    
    def move(self, pos=[0,0,0], setcmd=False): 
        arg = [self.UAV_CMD_MOVE]
        arg.extend(struct.pack('<f', float(pos[0])))
        arg.extend(struct.pack('<f', float(pos[1])))
        arg.extend(struct.pack('<f', float(pos[2])))
        self.uavCMD(arg, setcmd)

    def yaw(self, rotz:float, setcmd=False):
        arg = [self.UAV_CMD_YAW]
        arg.extend(struct.pack('<f', float(rotz)))
        self.uavCMD(arg, setcmd)
    
    def home(self, setcmd=False):
        self.uavCMD([self.UAV_CMD_HOME], setcmd)

    def kill(self):
        self.uavCMD([self.UAV_CMD_KILL])

    def origin(self, lat:float, lon:float):
        arg = [self.UAV_CMD_ORIGIN]
        arg.extend(struct.pack('<d', float(lat)))
        arg.extend(struct.pack('<d', float(lon)))
        self.uavCMD(arg)

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
