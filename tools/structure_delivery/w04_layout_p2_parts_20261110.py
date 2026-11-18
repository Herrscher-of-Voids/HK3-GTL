# -*- coding: utf-8 -*-
"""P2三巴纹磁环、鬼角电容塔、锁链与导流母线；独立体素构件。"""
import math
import numpy as np
from w04_gemini_dragon_b1_20261110 import Part,STATES,ROLES,BLACK,DARK,RED,GOLD,LIGHT,GLASS,SILVER,annulus
from w04_kurikara_d1_parts_20261110 import hull,loft

CENTER=np.array([0.,180.,235.])
RINGS=[(110,18),(145,-22),(175,35)]


def frame(degrees):
    a=math.radians(degrees)
    return np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])


def ring(index,radius,degrees):
    p=Part(f'P2_01_{index}_三巴纹双轨雷鼓磁环');matrix=frame(degrees);axis=matrix[:,2]
    world=lambda v:CENTER+np.asarray(v)@matrix.T
    for z in [-7,7]:
        center=world([0,0,z])
        annulus(p,center,axis,radius+5,radius-5,5,BLACK)
        annulus(p,center+axis*3,axis,radius+4,radius+2,2,GOLD)
        annulus(p,center+axis*3,axis,radius-2,radius-4,2,GOLD)
        annulus(p,center+axis*3,axis,radius+1,radius-1,2,RED)
    for a in np.linspace(0,2*math.pi,24,endpoint=False):
        for sign in [-1,1]:
            start=world([(radius+sign*2)*math.cos(a-.025),(radius+sign*2)*math.sin(a-.025),-7])
            end=world([(radius-sign*2)*math.cos(a+.025),(radius-sign*2)*math.sin(a+.025),7])
            p.beam(start,end,1.8,GOLD)
    # 三枚勾玉用圆头和收细曲尾组成，沿环内缘分布，中央保持贯通。
    for a in [math.pi/2,math.pi/2+2*math.pi/3,math.pi/2+4*math.pi/3]:
        center=world([(radius-12)*math.cos(a),(radius-12)*math.sin(a),11])
        annulus(p,center,axis,10,0,6,GOLD)
        annulus(p,center+axis*4,axis,6,0,2,RED)
        stations=np.linspace(0,1,12);sections=[]
        for t in stations:
            angle=a+.36*t;r=radius-12-20*t
            c=np.array([r*math.cos(angle),r*math.sin(angle),11]);w=8*(1-t)+.5
            tangent=np.array([math.cos(angle),math.sin(angle),0])*w
            sections.append(np.array([world(c-tangent-[0,0,3]),world(c+tangent-[0,0,3]),
                world(c+tangent+[0,0,3]),world(c-tangent+[0,0,3])]))
        loft(p,sections,GOLD)
    for a in np.linspace(0,2*math.pi,12,endpoint=False):
        radial=np.array([math.cos(a),math.sin(a),0]);tangent=np.array([-math.sin(a),math.cos(a),0])
        for sign in [-1,1]:
            root=radial*(radius+3)+tangent*sign*4
            shoulder=radial*(radius+13)+tangent*sign*8
            tip=radial*(radius+24)+tangent*sign*5
            hull(p,[world(root+tangent*sign*2+[0,0,z]) for z in [-4,4]]+
                [world(shoulder+tangent*s+[0,0,z]) for s in [-3,3] for z in [-3,3]]+[world(tip)],BLACK)
            p.beam(world(shoulder),world(tip),1.3,RED)
    return p.finish()


def tower(side):
    p=Part(f'P2_02_{side:+d}_鬼角电容扼流塔')
    q=lambda x,y,z:np.array([side*x,y,z],float)
    def box(a,b,state):p.box(np.minimum(a,b),np.maximum(a,b),state)
    box(q(288,25,230),q(372,41,320),BLACK)
    stations=[]
    for y,cx,rx,rz in [(41,330,31,35),(88,330,29,31),(180,336,23,26),(236,340,18,22)]:
        stations.append(np.array([q(cx+x,y,275+z) for x,z in [(-rx,-rz),(rx,-rz),(rx,rz),(-rx,rz)]]))
    loft(p,stations,BLACK)
    # 前面露出分段红绕组与金属散热片，侧面保留深色立柱。
    for y in range(55,227,20):
        center_x=330+max(0,y-88)*10/148
        box(q(center_x-15,y,243),q(center_x+15,y+9,249),RED)
        box(q(center_x-20,y+11,243),q(center_x+20,y+14,251),GOLD)
    for z in [251,299]:
        p.beam(q(310,42,z),q(323,218,z),3,DARK)
        p.beam(q(350,42,z),q(354,218,z),3,DARK)
    for y,r in [(64,36),(128,33),(192,29)]:
        annulus(p,q(333,y,275),[0,1,0],r,r-7,9,RED)
    # 双角是工业电极造型，并非无参考复刻雷律机械手。
    for shift in [-1,1]:
        root=q(340+shift*12,223,275);middle=q(340+shift*25,266,273)
        tip=q(340+shift*43,303,264)
        hull(p,[root+[x,0,z] for x in [-9,9] for z in [-12,12]]+
            [middle+[x,0,z] for x in [-5,5] for z in [-7,7]]+[tip],BLACK)
        p.beam(root+[0,0,-13],middle+[0,0,-8],2,RED)
        p.beam(middle+[0,0,-8],tip,1.6,GOLD)
    return p.finish()


def chain(side):
    p=Part(f'P2_03_{side:+d}_赤金交替链环')
    start=np.array([side*320,217,269.]);end=np.array([side*176,180,235.])
    axis=end-start;axis/=np.linalg.norm(axis)
    u=np.cross(axis,[0,0,1]);u/=np.linalg.norm(u);v=np.cross(axis,u)
    for i,t in enumerate(np.linspace(0,1,14)):
        center=start*(1-t)+end*t;normal=u if i%2 else v
        annulus(p,center,normal,9,5,3,GOLD)
    p.sphere(start,12,BLACK);p.sphere(start+[0,0,9],7,RED)
    p.sphere(end,9,BLACK);p.sphere(end+[0,0,7],4,RED)
    return p.finish()


def bus(side):
    p=Part(f'P2_04_{side:+d}_绯红母线廊桥')
    path=np.array([[side*260,37,-320],[side*170,45,-210],[side*100,72,-130],[side*58,162,-85]],float)
    for start,end in zip(path[:-1],path[1:]):
        p.beam(start,end,10,BLACK);p.beam(start+[0,7,0],end+[0,7,0],5,RED)
        for sign in [-1,1]:p.beam(start+[sign*7,11,0],end+[sign*7,11,0],1.6,GOLD)
    for a,b in zip(path[:-1],path[1:]):
        for t in np.linspace(0,1,7):
            c=a*(1-t)+b*t
            p.beam(c+[-9,6,0],c+[-9,14,0],1.4,SILVER)
            p.beam(c+[9,6,0],c+[9,14,0],1.4,SILVER)
    return p.finish()


def spiral(p,start,end,radius,turns):
    start,end=np.asarray(start,float),np.asarray(end,float);axis=end-start;axis/=np.linalg.norm(axis)
    u=np.cross(axis,[1,0,0]);u/=np.linalg.norm(u);v=np.cross(axis,u)
    for phase in [0,2*math.pi/3,4*math.pi/3]:
        path=[]
        for t in np.linspace(0,1,85):
            r=radius*math.sin(math.pi*t);a=phase+t*turns*2*math.pi
            path.append(start*(1-t)+end*t+r*(u*math.cos(a)+v*math.sin(a)))
        for a,b in zip(path[:-1],path[1:]):p.beam(a,b,2.6,GLASS)
        for a,b in zip(path[:-1],path[1:]):p.beam(a,b,1.1,LIGHT)


def energy():
    p=Part('P2_05_龙口与刀尖螺旋电弧束')
    spiral(p,[0,330,151],[0,75,235],8,3.5)
    spiral(p,[0,94,235],[0,75,235],4,1.2)
    return p.finish()


def build():
    parts=[ring(i+1,r,a) for i,(r,a) in enumerate(RINGS)]
    for builder in [tower,chain,bus]:parts.extend(builder(s) for s in [-1,1])
    parts.append(energy())
    return parts
