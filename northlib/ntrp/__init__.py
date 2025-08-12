#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  __  __ ____ _  __ ____ ___ __  __
#  \ \/ // __// |/ //  _// _ |\ \/ /
#   \  // _/ /    /_/ / / __ | \  / 
#   /_//___//_/|_//___//_/ |_| /_/  
# 
#   2024 Yeniay Uav Flight Control Systems
#   Research and Development Team

import northlib.ntrp.ntrp as ntrp
from northlib.ntrp.ntrpbuffer import NTRPBuffer
from northlib.ntrp.northport import NorthPort
from northlib.ntrp.northradio import NorthRadio
from northlib.ntrp import*

__author__ = 'Yeniay RD'
__all__ = []

import serial
import serial.tools.list_ports
import time

"""
    NRTP Protocol and NRTP Library created for 
    communication between computer and embedded systems.

    NRTP Protocol supports node based communication.
    Routers are wireless communication dongles that can
    both transmits and receives the data from other nodes.

    USAGE 1 Dongle(Router) : 
    [PC] <--- USB ---> [DONGLE] <--- SPI ---> [RF] <   RF   > [NODE1, NODE2...]

    USAGE 2 LORA: 
    [PC] <--- USB ---> [USB TO UART CONVERTER] <--- UART ---> [LORA] <  LORA  > [NODE1, NODE2...]

"""

availableRadios = list[NorthRadio]([])

def radioSearch(baud=2000000):
    """
    Search available ntrp radios connected to PC
    Radio objects stored  @availableRadios[] 
    """

    #Radio Search closes all radios in the list
    closeAvailableRadios()
    coms = NorthPort.getAvailablePorts()
    print("RadioManager:/COM LIST> ", coms)

    for com in coms:
        nr = None
        try:
            nr = NorthRadio(com,baud)
            if nr.syncRadio(2):
                print('RadioManager:/> NTRP Radio found : '+ com + " " + str(baud))
                nr.beginRadio()
                availableRadios.append(nr)
                
            else:
                print("RadioManager:/> Can't connect to : " + com) 
                nr.destroy()
        except: serial.SerialException
        
def closeAvailableRadios(): 
    for radio in availableRadios:
        radio.destroy()
    availableRadios.clear()
    print("RadioManager:/> All radios closed.")

def getRadio(index=int)->NorthRadio:
    if index >= len(availableRadios) or index < 0:
        print("RadioManager:/> Radio "+ str(index) +" not initalized.")
        return None
    return availableRadios[index]

def getAvailableRadios():
    return availableRadios


