# -*- coding: utf-8 -*-
"""按官方龙首正面、侧颊和翼刃局部重做头部与翼前肢。"""
import math
import numpy as np
from w04_kurikara_d1_parts_20261110 import *


def head():
    p=Part('01_长角V形面甲与龙首')
    sections=[]
    for z,rx,low,high in [(126,19,246,285),(145,28,245,310),(163,27,242,304),
        (182,20,237,286),(202,11,231,260),(219,2,232,239)]:
        sections.append(np.array([[0,high,z],[-rx,high-9,z],[-rx,low+6,z],[0,low,z],
            [rx,low+6,z],[rx,high-9,z]]))
    loft(p,sections,BLACK)
    hull(p,[[-16,297,155],[16,297,155],[0,314,163],[-12,291,184],[12,291,184],[0,278,195]],BLACK)
    p.beam([0,301,153],[0,310,165],6,BLACK)
    # 中央灰色额冠夹在红色V甲和两根长白角之间。
    for points in [[[-16,329,153],[-5,315,169],[0,312,177],[0,293,191],[-13,305,178]],
        [[16,329,153],[5,315,169],[0,312,177],[0,293,191],[13,305,178]]]:
        facet(p,points,[0,.35,1],3,NAVY,2)
    facet(p,[[0,311,179],[-8,319,165],[-5,303,184],[0,298,190],[5,303,184],[8,319,165]],
        [0,.35,1],1.5,NAVY)
    traced(p,[[-13,312,179],[0,291,193],[13,312,179]],1.1,BLACK)
    for side in [-1,1]:
        q=lambda x,y,z:np.array([side*x,y,z],float)
        facet(p,[q(6,307,188),q(9,313,181),q(12,310,181),q(10,302,189)],
            [0,.3,1],1,IVORY)
        # 不用横向十字条：两片向中央尖喙收束的折线面甲。
        main=[q(0,246,211),q(6,274,201),q(25,306,175),q(39,324,151),
            q(31,302,166),q(20,278,192),q(11,255,211)]
        facet(p,main,[0,.24,1],5,RED,2)
        facet(p,[q(2,251,215),q(10,278,203),q(22,300,182),q(18,278,200)],
            [0,.2,1],1.5,TRIM)
        facet(p,[q(5,247,214),q(14,267,205),q(21,288,191),q(16,281,197)],
            [0,.15,1],1,BLACK)
        # 颊环贴在颅侧，留黑色中央，再由红甲覆盖上半圆。
        center=q(26,267,153);axis=np.array([side,0,.1])
        collar(p,center,axis,17,12,3,IVORY)
        collar(p,center+q(1,0,0),axis,11.4,0,2,BLACK)
        facet(p,[q(29,278,138),q(32,288,151),q(30,276,171),q(26,265,174),q(24,272,155)],
            [side,0,0],4,RED,2)
        facet(p,[q(29,269,163),q(27,267,177),q(22,261,187),q(24,266,176)],
            [side,0,.2],2,IVORY)
        facet(p,[q(30,270,167),q(29,269,177),q(25,265,183)],
            [side,0,.3],1,WHITE)
        # 主角有弯折与收束，角腹暗、外侧骨白；不做圆锥柱。
        horn=[q(18,307,151),q(26,338,139),q(40,367,119),q(48,388,99),q(49,399,89)]
        taper(p,[q(17,294,145),horn[0],q(23,321,146)],[8,8,6],RED,.8)
        blade(p,horn,[7,9,6,2.5,.25],4,IVORY,normal=(0,.12,1))
        blade(p,[h+q(-1,-1,-4) for h in horn],[4.5,5,3,1,.2],1.2,NAVY,normal=(0,.12,1))
        blade(p,[horn[0]+q(2,1,3),horn[1]+q(3,0,2),horn[2]+q(2,0,1),horn[3]],[2,2.5,1,.2],.8,WHITE)
        blade(p,[q(22,299,141),q(40,316,120),q(48,335,101)],[5.5,4.5,.3],3,RED)
        for x,y,z in [(26,255,137),(24,245,141)]:
            blade(p,[q(x,y,z),q(x+10,y+3,z-15),q(x+15,y+10,z-29)],[5.5,5,.25],3,RED)
        # 紫色只留在眼后细缝，常态眼线按官方的浅色狭缝表达。
        traced(p,[q(29,269,165),q(24,265,181)],1.1,PINK)
        traced(p,[q(30,271,164),q(25,267,179)],.8,WHITE)
    # 紧闭下颚，保留窄口缝；不加缺乏依据的大口獠牙阵列。
    jaw=[]
    for z,rx,y in [(141,19,242),(168,18,232),(193,10,227),(219,1,230)]:
        jaw.append(np.array([[-rx,y,z],[0,y-5,z],[rx,y,z],[0,y+2,z]]))
    loft(p,jaw,DARK)
    blade(p,[[0,241,191],[0,236,207],[0,230,220]],[6,4,.3],1.6,RED)
    return p.finish()


def wing_arm(side):
    p=Part(f'04_{side:+d}_翼臂与暗色翼膜');q=lambda x,y,z:np.array([side*x,y,z],float)
    root=q(31,192,-9);elbow=q(91,196,23);wrist=q(151,221,65)
    taper(p,[root,q(58,191,7),elbow,q(121,209,46),wrist],[14,13,10,10,12],DARK,.75)
    blade(p,[root+[0,9,6],q(67,208,5),q(96,204,27)],[12,15,5],4,RED)
    blade(p,[q(88,199,27),q(122,218,49),wrist+[0,5,4]],[7,9,8],3,BLACK)
    blade(p,[q(93,200,29),q(121,217,50),wrist+[0,5,6]],[3.5,3.8,3],1.6,NAVY)
    # 膜位于腕后和躯干之间；凹边由独立三角片保留，不能填成整块矩形。
    anchors=[q(34,167,-30),q(58,151,-55),q(105,165,-81),q(144,189,-100),q(162,218,-89)]
    leading=[root,elbow,wrist,q(184,247,4),q(233,276,-26)]
    for i in range(4):
        a=anchors[i];c=anchors[i+1];b=leading[min(i+1,len(leading)-1)]
        notch=(a+c)/2+q(-4,13,18)
        for tri in [[leading[i],a,notch],[leading[i],notch,b],[b,notch,c]]:
            facet(p,tri,[0,.12,1],2.2,NAVY if i%2 else DARK)
        traced(p,[a,notch,c],1.2,BLACK)
        traced(p,[leading[i],a],2.2,DARK)
    # 腕内侧一枚回钩短爪。
    blade(p,[wrist,q(137,199,80),q(120,183,91)],[7,6,.25],3,RED)
    return p.finish()


def wing_blades(side):
    p=Part(f'05_{side:+d}_四片分体红色翼爪');q=lambda x,y,z:np.array([side*x,y,z],float)
    wrist=q(151,221,65);normal=np.array([0,.12,1.]);normal/=np.linalg.norm(normal)
    tips=[q(171,336,77),q(237,349,28),q(298,306,-22),q(324,248,-82)]
    widths=[15,20,23,20]
    for i,(tip,width) in enumerate(zip(tips,widths)):
        start=wrist+q(i*4,-i*2,-i*4)
        mid=start*.48+tip*.52+q(-4,9,8)
        shoulder=start*.76+tip*.24+q(2,1,6)
        knee=mid*.48+tip*.52+q(0,2,1)
        path=[start,shoulder,mid,knee,tip]
        blade(p,[v-normal*2 for v in path],[7,width*.8,width,width*.46,.3],6,BLACK,normal)
        blade(p,path,[7,width*.75,width*.9,width*.4,.2],7,RED,normal)
        # 窄受光分面、骨白外刃和中部白色火舌均为实体嵌片。
        tangent=tip-start;u=np.cross(normal,tangent);u/=np.linalg.norm(u)
        blade(p,[shoulder+normal*6+u*4,mid+normal*7+u*6,knee+normal*4+u*3,tip],
            [1.5,3.7,1.8,.15],1,TRIM,normal)
        white=[shoulder*.72+mid*.28+normal*7,mid+normal*8-u*3,knee*.70+mid*.30+normal*7,tip*.74+mid*.26+normal*3]
        blade(p,white,[.8,4.3,2.4,.2],1.2,WHITE,normal)
        traced(p,[shoulder-u*(width*.62)-normal*1,mid-u*(width*.77)-normal*1,knee-u*(width*.35),tip],1.4,IVORY)
        # 翼背的浅色嵌片比正面更窄，不复制成整面白色。
        blade(p,[shoulder-normal*6,mid-normal*7,knee-normal*4],[.7,2,.2],.9,IVORY,normal)
    collar(p,wrist,[0,.1,1],15,9,8,RED)
    collar(p,wrist+[0,0,5],[0,.1,1],9,0,2,BLACK)
    facet(p,[wrist+q(-11,7,7),wrist+q(0,12,9),wrist+q(14,4,6),wrist+q(0,-5,10)],
        [0,.1,1],3,RED,2)
    return p.finish()
