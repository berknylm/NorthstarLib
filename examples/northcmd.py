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
import northlib.ncmd.controller as ncmd
from   northlib.ncmd.northcom import NorthCOM
from   northlib.ncmd.nrxtable import NrxTableLog
from   northswarm.uavcom import UavCOM

"""
String to NRX Commands translator
Controller task auto start
str = [GET / SET][NRX NAME][VALUE]
"""
class NorthCMD(UavCOM):
	def __init__(self, uri) -> None:
		super().__init__(uri)
		self.ctrl = ncmd.Controller(True) # Joystick controller
		self.ctrl.callBack = lambda x : self.setRC(channels = x)
		self.start()

	def commandParser(self, string = str):
		parsed = string.split(' ')
		if(parsed[0] == "GET"):
			print(self.GET(parsed[1]))
		if(parsed[0] == "SET"):
			if(len(parsed) > 3)   : self.SET(parsed[1], parsed[2:])
			elif(len(parsed) == 3): self.SET(parsed[1], parsed[2])
		if(parsed[0] == "POS")    : self.position = [float(x) for x in parsed[1:]]
		if(parsed[0] == "IDLE")   : self.setMode(self.UAV_IDLE)
		if(parsed[0] == "MANUAL") : self.setMode(self.UAV_MANUAL)
		if(parsed[0] == "HEIGHT") : self.setMode(self.UAV_HEIGHT)
		if(parsed[0] == "AUTO")   : self.setMode(self.UAV_AUTO)
		if(parsed[0] == "TAKEOFF"): self.setMode(self.UAV_TAKEOFF)
		if(parsed[0] == "LAND")   : self.setMode(self.UAV_LAND)


uri = "radio:/0/76/2/E7E7E7E305"

if __name__ == '__main__':
	
	radioManager.radioSearch (baud=2000000)
	if not len(radioManager.availableRadios) > 0: sys.exit()

	uav = NorthCMD(uri)
	uav.commandParser(input())

	while (uav.radio.isRadioAlive()):
		uav.commandParser(input())