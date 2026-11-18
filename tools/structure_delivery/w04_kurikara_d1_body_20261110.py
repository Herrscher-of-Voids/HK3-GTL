# -*- coding: utf-8 -*-
"""独立悬停龙躯：弯颈叠甲、短躯、双后足与细长尾，保留参考的翼龙体态。"""
import math
import numpy as np
from scipy.interpolate import CubicSpline
from w04_kurikara_d1_parts_20261110 import *


def armored_curve(p,path,radii,steps,neck=False):
    curve=CubicSpline(np.linspace(0,1,len(path)),np.asarray(path,float),axis=0)
    stations=np.linspace(0,1,steps+1)
    def radius(t):return np.interp(t,np.linspace(0,1,len(radii)),radii)
    def ring(t,scale=1):
        _,u,v=body_frame(curve,t);r=radius(t)
        return np.array([curve(t)+u*math.cos(a)*r*scale+v*math.sin(a)*r*.8*scale for a in np.linspace(0,2*math.pi,10,endpoint=False)])
    loft(p,[ring(t,.90) for t in np.linspace(0,1,steps*2)],BLACK)
    for a,c in zip(stations[:-1],stations[1:]):
        t=(a+c)/2;axis,u,v=body_frame(curve,t);r=radius(t)
        for angles,state in [(np.linspace(.15,math.pi-.15,6),RED),(np.linspace(math.pi+.08,2*math.pi-.08,6),DARK)]:
            rows=[]
            for s,scale in [(a+(c-a)*.06,.97),(t,1.06),(c-(c-a)*.09,.94)]:
                _,uu,vv=body_frame(curve,s);rr=radius(s)
                rows.append(np.array([curve(s)+uu*math.cos(ang)*rr*scale+vv*math.sin(ang)*rr*.8*scale for ang in angles]))
            hull(p,np.vstack(rows),state)
        center=curve(t);surface=center-v*r*.82
        points=[surface-u*r*.7+axis*4,surface-u*r*.55-axis*1,
            surface-axis*8-v*2,surface+u*r*.55-axis*1,surface+u*r*.7+axis*4,surface+axis*6+v]
        facet(p,points,-v,2.5,IVORY if not neck and t<.20 else DARK,2)
        if neck:
            traced(p,[points[1]-v*2,points[2]-v*2,points[3]-v*2],.7,SILVER)
            for sign in [-1,1]:
                flank=center+u*sign*r*.78+v*r*.3
                blade(p,[flank-axis*3,flank+v*5+axis*3,flank-axis*7+v*6],[3,3,.2],1.7,RED,normal=u)
    return curve


def torso_neck():
    p=Part('02_短躯弯颈与分节胸腹甲')
    armored_curve(p,[[0,116,-69],[0,148,-50],[0,179,-20],[0,201,13]],[20,35,38,26],12)
    armored_curve(p,[[0,198,6],[0,216,48],[0,242,91],[0,261,129]],[23,19,16,18],13,True)
    # 面向前方的胸甲呈层叠V形，不增加人形腰身。
    for y,z,width in [(183,18,33),(169,7,34),(154,-3,28)]:
        points=[[-width,y+9,z],[-width*.72,y-1,z+9],[0,y-14,z+20],
            [width*.72,y-1,z+9],[width,y+9,z],[0,y-4,z+15]]
        facet(p,points,[0,.2,1],4,BLACK,3)
        traced(p,[[-width*.8,y+2,z+9],[0,y-10,z+22],[width*.8,y+2,z+9]],1.6,SILVER)
    for side in [-1,1]:
        q=lambda x,y,z:np.array([side*x,y,z],float)
        facet(p,[q(19,206,0),q(44,210,-13),q(60,194,-6),q(42,183,15),q(28,190,20)],
            [0,.6,1],6,RED,5)
        blade(p,[q(29,198,-17),q(43,217,-23),q(52,225,-33)],[8,7,.2],4,RED)
        blade(p,[q(29,180,25),q(37,194,20),q(47,188,10)],[3,4,.3],1.6,WHITE)
        traced(p,[q(28,179,27),q(35,190,24)],1.4,LIGHT)
    # 背甲中线有细鳍与错层装甲，骑乘座下遮挡连接仅做简化。
    for y,z,w in [(190,-20,18),(172,-43,22),(151,-65,18),(132,-76,12)]:
        facet(p,[[-w,y,z],[0,y+8,z-8],[w,y,z],[0,y-6,z+4]],[0,1,-.3],4,RED,3)
        blade(p,[[0,y+3,z-4],[0,y+17,z-14],[0,y+5,z-27]],[4,4,.2],3,BLACK,normal=(1,0,0))
    return p.finish()


def hindleg(side):
    p=Part(f'06_{side:+d}_收拢后足与红色三爪');q=lambda x,y,z:np.array([side*x,y,z],float)
    path=[q(25,134,-52),q(41,106,-24),q(34,78,0),q(37,48,17),q(37,39,39)]
    taper(p,path,[13,15,9,7,9],DARK,.8)
    for i,(a,c) in enumerate(zip(path[:-1],path[1:])):
        direction=c-a;front=np.array([0.,0.,1.]);mid=(a+c)/2+front*(10 if i<2 else 7)
        blade(p,[a+front*6,mid,c+front*5],[9 if i<2 else 6,12 if i<2 else 7,4],3,BLACK)
        if i<2:
            blade(p,[a+q(5,1,7),mid+q(5,0,3),c+q(4,0,5)],[5,6,.2],2,RED)
        else:
            blade(p,[a+front*9,mid+front*4,c+front*8],[4,5,.3],1.7,NAVY)
        traced(p,[a+q(-5,0,5),mid+q(-6,0,1),c+q(-4,0,5)],1.4,IVORY)
    for dx in [-8,0,8]:
        toe=[q(37+dx,40,35),q(37+dx*1.2,32,49),q(37+dx*1.3,30,62),q(37+dx*1.2,38,71)]
        taper(p,toe[:3],[4.5,4,3],BLACK,.7)
        blade(p,[toe[1]+[0,2,0],toe[2]+[0,1,0],toe[3]],[4,3,.25],2,RED)
    return p.finish()


def tail():
    p=Part('03_红脊白刺与细长弯尾')
    path=[[0,121,-69],[0,94,-108],[10,76,-151],[34,72,-198],[61,86,-246],
        [68,108,-283],[49,126,-319],[19,138,-349],[-9,137,-371]]
    curve=CubicSpline(np.linspace(0,1,len(path)),np.asarray(path,float),axis=0)
    radii=[16,14,11,9,7,5,3.7,2,.5]
    def r(t):return float(np.interp(t,np.linspace(0,1,len(radii)),radii))
    sections=[]
    for t in np.linspace(0,1,88):
        _,u,v=body_frame(curve,t);rr=r(t)
        sections.append(np.array([curve(t)+u*math.cos(a)*rr+v*math.sin(a)*rr*.72 for a in np.linspace(0,2*math.pi,8,endpoint=False)]))
    loft(p,sections,DARK)
    for a,c in zip(np.linspace(.02,.92,22)[:-1],np.linspace(.02,.92,22)[1:]):
        t=(a+c)/2;axis,u,v=body_frame(curve,t);rr=r(t);center=curve(t)+v*rr*.65
        facet(p,[center-u*rr*.8-axis*3,center-u*rr*.75+axis*4,center+axis*9+v*3,
            center+u*rr*.75+axis*4,center+u*rr*.8-axis*3],v,3,RED,2)
        if .15<t<.8:
            blade(p,[center-axis*2,center+v*(rr*.8+6)-axis*7,center-axis*14],
                [max(2,rr*.3),max(1,rr*.2),.2],2,IVORY,normal=u)
        if t<.75:
            for sign in [-1,1]:
                traced(p,[center+u*sign*rr*.68-axis*3,center+u*sign*rr*.76+axis*3,center+axis*8],.9,WHITE)
    return p.finish(),float(np.linalg.norm(np.diff(curve(np.linspace(0,1,1001)),axis=0),axis=1).sum())
