#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  __  __ ____ _  __ ____ ___ __  __
#  \ \/ // __// |/ //  _// _ |\ \/ /
#   \  // _/ /    /_/ / / __ | \  / 
#   /_//___//_/|_//___//_/ |_| /_/  
# 
#   2024 Yeniay Uav Flight Control Systems
#   Research and Development Team

import math


def p2d(v):return [v[0],v[1]]

def p3d(v):return [v[0],v[1],0]

def pl2d(pv):
    npv=[]
    for p in pv:
        npv.append(p2d(p))
    return npv

def pl3d(pv):
    npv=[]
    for p in pv:
        npv.append(p3d(p))
    return npv

def vadd(v1,v2):
    return [v1[0]+v2[0],v1[1]+v2[1],v1[2]+v2[2]]

def vsub(v1,v2):
    return vadd(v1,vneg(v2))

def vneg(v):
    return [-v[0],-v[1],-v[2]]

def vdist(v1,v2):
    return(vmag(vsub(v1,v2)))

def vmag(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def vort(pcl):
    pcls = pcl.copy()
    pcladd = [0,0,0]
    for p in pcls:
        pcladd = vadd(pcladd,p)
    return vdiv(pcladd,pcls.__len__())

def vdiv(v,s):
    d=[0,0,0]
    if s==0:return d
    if v[0]!=0: d[0] =v[0]/s
    if v[1]!=0: d[1] =v[1]/s
    if v[2]!=0: d[2] =v[2]/s
    return d

def vmult(v,m):
    return [v[0]*m , v[1]*m ,v[2]*m]

def vdot(v):
    return vdiv(v,vmag(v))

def vmax(v,m):
    if vmag(v)>m: return vmult(vdot(v),m)
    return v

def vlerp(v1,v2,i):
    return vadd(vmult(v1,1-i),vmult(v2,i))

def vround(v,n):
    return [round(v[0],n),round(v[1],n),round(v[2],n)]

def vnearest(v,pcl,d=20000,z0=False):
    ps = pcl.copy()
    vs = v.copy()
    ds = d
    nearest=[]
    if z0:
        ps=pl3d(ps)
        vs=p3d(vs)
    for p in ps:
        dis = vdist(vs,p)
        if dis<ds:
            ds = dis
            nearest=p
    if z0:return p2d(nearest)
    return nearest


def origin_set(pcloud=[], new_origin=[], z0=False):
    newpc =[]
    for p in pcloud:
        if z0: 
            p = p3d(p)
            new_origin =p3d(new_origin)

        newp = vsub(p,new_origin)
        if z0: newp = p2d(newp)
        newpc.append(newp)
    return newpc

def scale_set(pcloud=[],origin=[0,0],scale=1,z0=False):
    if z0: exorigin = vneg([origin[0],origin[1],0])
    else: exorigin = vneg(origin)
    pcl_set = origin_set(pcloud,origin,z0)

    newpc =[]
    for p in pcl_set:
        if z0: p = p3d(p)
        newp = vmult(p,scale)
        if z0: newp = p2d(newp)
        newpc.append(newp)
    
    newpc = origin_set(newpc,exorigin,z0)
    
    return newpc

def plinelen(pline=[],z0=False):
    l=0
    pex=None
    for p in pline:
        if z0: p = p3d(p)
        if pex == None:
            pex = p
            continue
        l = l+vdist(pex,p)
        pex = p
    return l

def peucker2d(pline=[],divider=1):
    if pline.__len__()<= divider: return pline
    pckr=[]
    if divider <=0: return pckr
    pllen = plinelen(pline,z0=True)/divider
    plx0=0
    plx1=0
    for i in range(divider):
        d=0
        while d<pllen:
            if plx1>= pline.__len__()-1:break
            plx0 = plx1
            plx1 = plx1+1
            p1 = pline[plx0]
            p2 = pline[plx1]
            d_now = vdist([p1[0],p1[1],0],[p2[0],p2[1],0])
            d = d+d_now
        pckr.append(pline[plx1])
    
    return pckr

def vposer(pcloud,pos):
        pcl = pcloud.copy()
        ps = pos.copy()
        for p in pcl:
            p[0]=round(ps[0]+p[0],5)
            p[1]=round(ps[1]+p[1],5)
            p[2]=round(ps[2]+p[2],5)
        return pcl

# # --------------------------------------------------
# # xy

# ncstacles=[[0,0.5,0],[0,-0.2,0]]
# obstacles= [[0,3,31],[0,0.2,0]]
# est_x = 0
# est_y = 0
# est_pos=[0,0,0]
# est_p = [est_x,est_y,0]

# react_f =[0,0,0]

# if obstacles.__len__()>0:
#     obs = vnearest(est_p,obstacles,z0=True)
#     obs = p3d(obs)
#     obs_dist = vdist(obs,est_p)-0.05
    
#     if obs_dist<=0:obs_dist=0.01
    
#     if obs_dist < 0.25:
#         kd = 0.05/(obs_dist**2)
#         obs_f = vmult(vsub(est_p.copy(),obs),kd)
#         react_f = vadd(react_f,obs_f)
# # --------------------------------------------------
# # xyz collision avoidance

# if ncstacles.__len__()>0:
#     ncf = vnearest(est_pos,ncstacles)
#     ncf_dist = vdist(est_pos,ncf)-0.05
#     if ncf_dist<=0:ncf_dist=0.01
#     if ncf_dist < 0.25:
#         kd = 0.08/(ncf_dist**2)
#         ncf_f = vmult(vsub(est_pos,ncf),kd)
#         react_f = vadd(react_f.copy(),ncf_f)

# print(vmax(react_f,1.25))

# # ------------------ ALL FORCE --------------------

# tf_form = [[-5,-5,-5],[-10,-10,-10],[-15,-15,-15]]
# tff = []
# for p in tf_form:
#     tff.append([p[0],p[1],p[2]])
# tf_center = vort(tf_form)
# print(tf_form)

# print('EEEE')
# print(vposer(tff,tf_center))
# print(vposer(tff,tf_center))

# print(tf_form)