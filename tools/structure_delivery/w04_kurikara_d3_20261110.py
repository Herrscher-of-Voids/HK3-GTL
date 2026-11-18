# -*- coding: utf-8 -*-
"""扩展翼骨、翼膜和翼刃，按原路径加厚尾体，保留D2头身腿爪。"""
import json,math
import numpy as np
from scipy.interpolate import CubicSpline
import w04_kurikara_d1_20261110 as base
import w04_kurikara_d2_20261110 as d2
from w04_kurikara_d1_parts_20261110 import *

PRIOR=d2.OUT
OUT=ROOT/'deliveries/W04_俱利伽罗_展翼与厚尾_D3_20261110'
LOG=ROOT/'logs/w04-kurikara-d3-20261110'
SWORD=d2.SWORD
TAIL_PATH=[[0,121,-69],[0,94,-108],[10,76,-151],[34,72,-198],[61,86,-246],
    [68,108,-283],[49,126,-319],[19,138,-349],[-9,137,-371]]
TAIL_RADII=[29,26,22,18,14,10,7.4,4,.7]


def wing_arm(side):
    p=Part(f'04_{side:+d}_展开翼骨与宽幅凹缘翼膜');q=lambda x,y,z:np.array([side*x,y,z],float)
    root=q(31,192,-9);elbow=q(119,196,23);wrist=q(201,225,65)
    taper(p,[root,q(75,191,7),elbow,q(160,211,46),wrist],[18,18,15,15,18],DARK,.80)
    blade(p,[root+[0,12,7],q(86,212,5),q(123,207,27)],[16,21,9],6,RED)
    blade(p,[q(114,199,27),q(160,220,49),wrist+[0,8,4]],[12,14,13],5,BLACK)
    anchors=[q(34,167,-40),q(78,135,-80),q(155,145,-138),q(227,180,-180),q(275,225,-155)]
    leading=[root,elbow,wrist,q(260,274,4),q(340,305,-26)]
    for i in range(4):
        a,c=anchors[i:i+2];b=leading[i+1];notch=(a+c)/2+q(-6,16,22)
        for tri in [[leading[i],a,notch],[leading[i],notch,b],[b,notch,c]]:
            facet(p,tri,[0,.12,1],2.8,NAVY if i%2 else DARK)
        traced(p,[a,notch,c],1.8,BLACK)
        traced(p,[leading[i],a],3,DARK)
    # 腕甲随翼骨一起外展，保留分片覆甲及内侧回钩拇爪。
    for x,y,z in [(104,200,19),(133,205,31),(162,215,44),(190,226,58)]:
        c=q(x,y,z)
        facet(p,[c+q(-16,0,0),c+q(-4,12,1),c+q(17,9,3),c+q(19,-4,8),c+q(0,-12,12)],
            [0,.3,1],5,BLACK,3)
        facet(p,[c+q(-12,0,5),c+q(-1,8,6),c+q(14,6,8),c+q(14,-2,11),c+q(0,-8,15)],
            [0,.3,1],3,DARK,2)
    blade(p,[wrist,q(184,196,85),q(161,174,101)],[10,9,.25],4,RED)
    return p.finish()


def wing_blades(side):
    p=Part(f'05_{side:+d}_加长加宽四片翼刃');q=lambda x,y,z:np.array([side*x,y,z],float)
    wrist=q(201,225,65);normal=np.array([0,.12,1.]);normal/=np.linalg.norm(normal)
    tips=[q(227,376,82),q(327,394,20),q(414,337,-44),q(452,254,-104)]
    for i,(tip,width) in enumerate(zip(tips,[22,29,32,28])):
        start=wrist+q(i*5,-i*3,-i*5)
        mid=start*.48+tip*.52+q(-5,12,10)
        shoulder=start*.76+tip*.24+q(3,2,8)
        knee=mid*.48+tip*.52+q(0,3,1)
        path=[start,shoulder,mid,knee,tip]
        blade(p,[v-normal*2 for v in path],[10,width*.8,width,width*.46,.3],7,BLACK,normal)
        blade(p,path,[10,width*.75,width*.9,width*.4,.2],8.5,RED,normal)
        tangent=tip-start;u=np.cross(normal,tangent);u/=np.linalg.norm(u)
        blade(p,[shoulder+normal*8+u*5,mid+normal*9+u*8,knee+normal*6+u*4,tip],
            [2,5,2.5,.15],1.2,TRIM,normal)
        white=[shoulder*.72+mid*.28+normal*9,mid+normal*10-u*4,
            knee*.70+mid*.30+normal*9,tip*.74+mid*.26+normal*4]
        blade(p,white,[1,6,3.5,.2],1.5,WHITE,normal)
        traced(p,[shoulder-u*(width*.62)-normal,mid-u*(width*.77)-normal,knee-u*(width*.35),tip],1.8,IVORY)
        blade(p,[shoulder-normal*7,mid-normal*8,knee-normal*5],[1,3,.2],1,IVORY,normal)
    collar(p,wrist,[0,.1,1],21,13,11,RED)
    collar(p,wrist+[0,0,6],[0,.1,1],13,0,3,BLACK)
    facet(p,[wrist+q(-16,10,9),wrist+q(0,17,12),wrist+q(20,6,9),wrist+q(0,-7,14)],
        [0,.1,1],5,RED,3)
    return p.finish()


def tail():
    p=Part('03_厚尾根渐细尾体与分节骨甲')
    curve=CubicSpline(np.linspace(0,1,len(TAIL_PATH)),np.asarray(TAIL_PATH,float),axis=0)
    r=lambda t:float(np.interp(t,np.linspace(0,1,len(TAIL_RADII)),TAIL_RADII))
    sections=[]
    for t in np.linspace(0,1,100):
        _,u,v=body_frame(curve,t);rr=r(t)
        sections.append(np.array([curve(t)+u*math.cos(a)*rr+v*math.sin(a)*rr*.82
            for a in np.linspace(0,2*math.pi,10,endpoint=False)]))
    loft(p,sections,DARK)
    stations=np.linspace(.015,.96,28)
    for a,c in zip(stations[:-1],stations[1:]):
        t=(a+c)/2;axis,u,v=body_frame(curve,t);rr=r(t);center=curve(t)+v*rr*.72
        facet(p,[center-u*rr*.88-axis*4,center-u*rr*.82+axis*6,center+axis*12+v*4,
            center+u*rr*.82+axis*6,center+u*rr*.88-axis*4],v,4,BLACK,2)
        facet(p,[center-u*rr*.78-axis*2,center-u*rr*.72+axis*6,center+axis*10+v*5,
            center+u*rr*.72+axis*6,center+u*rr*.78-axis*2],v,4,RED,2)
        if .12<t<.86:
            blade(p,[center-axis*3,center+v*(rr*.72+7)-axis*9,center-axis*19],
                [max(3,rr*.32),max(2,rr*.24),.2],max(2,rr*.16),IVORY,normal=u)
        if t<.78:
            for sign in [-1,1]:
                traced(p,[center+u*sign*rr*.64-axis*3,center+u*sign*rr*.73+axis*4,center+axis*10],1.1,WHITE)
    length=float(np.linalg.norm(np.diff(curve(np.linspace(0,1,1001)),axis=0),axis=1).sum())
    return p.finish(),length


def build():
    overrides=dict(hindleg=d2.hindleg,torso_neck=d2.torso_neck,wing_arm=wing_arm,wing_blades=wing_blades,tail=tail,LOG=LOG)
    saved={key:getattr(base,key) for key in overrides}
    for key,value in overrides.items():setattr(base,key,value)
    try:cube,data,parts=base.build()
    finally:
        for key,value in saved.items():setattr(base,key,value)
    old=json.loads((PRIOR/'manifest.json').read_text('utf8'))
    for key in ['reference_count','fan_model_images','official_model_found','source_mesh_used','fan_model_url','source_limits']:
        data[key]=old[key]
    data.update(name='hk3gtl-w04-kurikara-independent-d3-20261110',title='俱利伽罗 · 展翼与厚尾 D3',
        summary='翼骨加长、翼膜向后展宽、四片翼刃同步扩大；原尾部路径保持，尾根与中段加厚并逐节收细。保留D2头身腿爪。',
        detail_changes=['双翼翼骨、翼膜及四片翼刃整体重做','尾根与中段加厚，保持原尾部中心线'],
        unchanged_components=['01_长角V形面甲与龙首','02_短躯弯颈与分节胸腹甲',
            '06_-1_粗壮折腿宽掌与钩爪','06_+1_粗壮折腿宽掌与钩爪'],
        proportion_revision=dict(official_exact_dimensions=False,tail_centerline_unchanged=True,
            old_tail_radii=[16,14,11,9,7,5,3.7,2,.5],new_tail_radii=TAIL_RADII,
            calibration_images=['guide-132.0.jpg','guide-144.0.jpg','guide-148.0.jpg','guide-150.0.jpg','guide-166.0.jpg']))
    data['detail_views'].update(old['detail_views'])
    data['detail_views']['wing']=dict(center=[289,268,-10],half=[177,143,170])
    data['detail_views']['wingback']=dict(center=[-289,268,-10],half=[177,143,170])
    data['detail_views']['tail']=dict(center=[20,108,-218],half=[96,78,178])
    return cube,data,parts


if __name__=='__main__':
    c,d,p=build();print(json.dumps(dict(size=d['size'],blocks=d['blocks'],connected=d['connectivity']['six_neighbor_components'])))
