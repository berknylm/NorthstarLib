#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  __  __ ____ _  __ ____ ___ __  __
#  \ \/ // __// |/ //  _// _ |\ \/ /
#   \  // _/ /    /_/ / / __ | \  / 
#   /_//___//_/|_//___//_/ |_| /_/  
# 
#   2024 Yeniay Uav Flight Control Systems
#   Research and Development Team

import time
import math
# Local vector math helpers
from northuav.math3d import *

Blank = [0.0, 0.0, 0.0]

Triangle = [
    [-1.6, -0.8, 0],
    [   0,    2, 0],
    [ 1.6, -0.8, 0]
]

Safe = [
    [-1.6, -0.8,  3],
    [   0,    2,  0],
    [ 1.6, -0.8, -3]
]

Trimap = [
    [-15,  0,  3],
    [-13,  0,  0],
    [-11,  0, -3]
]

class Shape:

    def __init__(self, pos=Blank, rot=Blank, scale=1.0, pCloud=[]):
        self.pos   = pos
        self.rot   = rot
        self.scale = scale
        self.abstract = pCloud

    def rotater(self, pcloud, rot):
        pcl = []
        x = math.radians(rot[0])
        y = math.radians(rot[1])
        z = math.radians(rot[2])
        
        for p in pcloud:

            p = [p[0],(p[1]*math.cos(x))-(p[2]*math.sin(x)),(p[1]*math.sin(x))+(p[2]*math.cos(x))]
            p = [(p[0]*math.cos(y))+(p[2]*math.sin(y)),p[1],(p[2]*math.cos(y))-(p[0]*math.sin(y))]
            p = [(p[0]*math.cos(z))-(p[1]*math.sin(z)),(p[0]*math.sin(z))+(p[1]*math.cos(z)),p[2]]

            p[0]= round(p[0], 5)
            p[1]= round(p[1], 5)
            p[2]= round(p[2], 5)

            pcl.append(p)
        
        return pcl

    def scaler(self, pcloud, scl):
        pcl = []
        for p in pcloud:
            p = [p[0]*scl,p[1]*scl,p[2]*scl]
            p[0]= round(p[0],5)
            p[1]= round(p[1],5)
            p[2]= round(p[2],5)
            pcl.append(p)
        return pcl
    
    def poser(self, pcloud, pos):
        pcl = pcloud
        for p in pcl:
            p[0]=round(pos[0]+p[0],5)
            p[1]=round(pos[1]+p[1],5)
            p[2]=round(pos[2]+p[2],5)
        return pcl

    def getPoints(self):
        """ Point pipeline should not change """
        pcl = self.abstract
        pcl = self.rotater(pcl,self.rot)
        pcl = self.scaler(pcl,self.scale)
        pcl = self.poser(pcl,self.pos)
        return pcl
    

def shapeLerp(shp1 = Shape(), shp2 = Shape(), alpha = float):
    pos = vlerp(shp1.pos, shp2.pos, alpha)
    rot = vlerp(shp1.rot, shp2.rot, alpha)
    scl = (shp1.scale * (1 - alpha)) + (shp2.scale * (alpha))
    return Shape(pos, rot, scl, shp1.abstract)
