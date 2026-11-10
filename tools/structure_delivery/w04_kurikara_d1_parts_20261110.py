# -*- coding: utf-8 -*-
"""俱利伽罗静态转译的材质与分面薄甲工具；不引用旧盘环姿态。"""
from pathlib import Path
import math
import numpy as np
from w02_19c_geometry_v4_20261110 import SolidPart,solid_annulus
from scipy.spatial import ConvexHull
from w02_bunny_dock_geometry_v3_20261108 import encode

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W04_俱利伽罗_独立静态小样_D1_20261110'
LOG=ROOT/'logs/w04-kurikara-d1-20261110'
BLACK,DARK,NAVY,RED,TRIM,IVORY,WHITE,SILVER,LIGHT,PINK=[
    'minecraft:'+s for s in ['black_concrete','gray_concrete','cyan_terracotta','red_concrete','pink_terracotta',
    'white_terracotta','white_concrete','light_gray_concrete','sea_lantern','magenta_concrete']]
STATES=[BLACK,DARK,NAVY,RED,TRIM,IVORY,WHITE,SILVER,LIGHT,PINK]
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES=dict(zip(STATES,['甲缝和深色内衬','暗灰颈腹、翼膜和后足','冷灰翼膜、额甲与角内侧',
    '红色骨甲、面甲与翼爪主刃','小面积红甲受光分面','骨白长角、颊环、尾刺与爪缘',
    '翼刃白色嵌片与窄亮纹','颈腹甲的银灰边缘','嵌入式静态白光芯','眼部细窄紫红内层']))


class Part(SolidPart):
    def points(self,points,state):
        a=np.rint(points).astype(np.int32).reshape(-1,3)
        if len(a):
            assert np.all(abs(a)<2048),'几何越界只报错，不裁切'
            self.chunks.append(a);self.values.append(np.full(len(a),IDS[state],np.uint8))


def hull(p,vertices,state):
    """保留与薄甲几何相交的体素，避免斜薄片退化成互不连接的点列。"""
    vertices=np.asarray(vertices,float);equations=ConvexHull(vertices).equations
    tolerance=.5*np.abs(equations[:,:3]).sum(1)
    low=np.floor(vertices.min(0)-.5).astype(int);high=np.ceil(vertices.max(0)+.5).astype(int)
    zz,xx=np.mgrid[low[2]:high[2]+1,low[0]:high[0]+1]
    for y in range(low[1],high[1]+1):
        at=np.c_[xx.ravel(),np.full(xx.size,y),zz.ravel()]
        keep=np.all(at@equations[:,:3].T+equations[:,3]<=tolerance+.001,axis=1)
        p.points(at[keep],state)


def loft(p,sections,state):
    for a,c in zip(sections[:-1],sections[1:]):hull(p,np.vstack([a,c]),state)


def blade(p,path,widths,depth,state,normal=(0,0,1)):
    path=np.asarray(path,float);normal=np.asarray(normal,float);normal/=np.linalg.norm(normal);sections=[]
    for i,(center,width) in enumerate(zip(path,widths)):
        tangent=path[min(i+1,len(path)-1)]-path[max(0,i-1)]
        u=np.cross(normal,tangent);u/=np.linalg.norm(u)
        sections.append(np.array([center-u*width,center+normal*depth,center+u*width,center-normal*depth]))
    loft(p,sections,state)


def taper(p,path,widths,state,flat=1):
    path=np.asarray(path,float);sections=[]
    for i,(center,width) in enumerate(zip(path,widths)):
        axis=path[min(i+1,len(path)-1)]-path[max(0,i-1)];axis/=np.linalg.norm(axis)
        ref=np.array([0.,1.,0.]) if abs(axis[1])<.85 else np.array([0.,0.,1.])
        u=np.cross(axis,ref);u/=np.linalg.norm(u);v=np.cross(axis,u)
        sections.append(np.array([center+u*math.cos(a)*width+v*math.sin(a)*width*flat for a in np.linspace(0,2*math.pi,8,endpoint=False)]))
    loft(p,sections,state)


def facet(p,points,normal,depth,state,peak=0):
    points=np.asarray(points,float);reference=np.asarray(normal,float)
    _,_,axes=np.linalg.svd(points-points.mean(0));normal=axes[-1]
    if normal@reference<0:normal=-normal
    vertices=np.vstack([points-normal*depth/2,points+normal*depth/2])
    if peak:vertices=np.vstack([vertices,points.mean(0)+normal*(depth/2+peak)])
    hull(p,vertices,state)


def traced(p,path,r,state):
    for a,c in zip(path[:-1],path[1:]):p.beam(a,c,max(1.05,r),state)


def collar(p,center,axis,r,inner,depth,state):
    solid_annulus(p,center,axis,r,inner,depth,state)


def body_frame(curve,t):
    axis=curve(t,1);axis/=np.linalg.norm(axis);u=np.array([1.,0,0])
    u-=axis*np.dot(u,axis);u/=np.linalg.norm(u);v=np.cross(axis,u)
    if v[1]<0:u=-u;v=-v
    return axis,u,v
