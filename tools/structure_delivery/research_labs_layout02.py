# -*- coding: utf-8 -*-
"""研究所候选02几何：按69座总表逐轴扩建，保留候选01记录。
变更#1 2026-09-28 02:50:25：新增匹配总表的实验翼、资料穹顶及研究环廊；不改生产代码。
"""
import math

def designs(Build):
    a=Build('s02',[35,25,33],'S02 研究所·第二阶（名称待定）');c=a.cx
    for x in (2,24):
        a.pod((x,1,8),(x+8,10,27))
        a.box((x+2,2,6),(x+6,4,6),'filter');a.line((x+4,4,6),(x+4,4,8),'pipe')
    a.pod((c-5,7,12),(c+5,19,28),'molecular')
    for x in (c-5,c+5):
        for z in (12,28):a.box((x,1,z),(x,7,z),'power')
    for x in (4,30):
        a.pod((x-1,1,29),(x+1,24,31),'cooler')
        a.line((x,14,29),(c-5 if x<c else c+5,14,27),'pipe')
    for x in (c-7,c+7):
        a.box((x,1,6),(x,4,28),'panel');a.box((x,5,9),(x,5,27),'connector')
    yield a.finish('左右制备与冷却翼延展至后场，中央检测腔与24格高散热柱连接；统一白色地板、中轴净空和白框全接口面板。')

    a=Build('s03',[45,39,49],'S03 研究所·第三阶（名称待定）');c=a.cx;z=26
    for x in (5,39):
        for zz in (10,40):
            a.pod((x-2,1,zz-4),(x+2,11,zz+4),'panel')
            a.line((x,11,zz),(c+(12 if x>c else -12),18,z+(12 if zz>z else -12)),'power')
    a.ring((c,22,z),16,'xy','frame',2);a.ring((c,22,z),16,'yz','frame',2)
    a.ring((c,22,z),14,'xy','coil');a.ring((c,22,z),14,'yz','qft');a.ring((c,18,z),17,'xz','molecular')
    for x in (c-17,c+17):a.box((x,1,z),(x,21,z),'power')
    a.pod((c-4,17,z-4),(c+4,25,z+4),'fusion');a.box((c-1,18,z-1),(c+1,24,z+1),'qft')
    a.line((c-17,21,z),(c+17,21,z),'compute');a.line((c,21,z-17),(c,21,z+17),'compute')
    yield a.finish('双交叉量子环保留，前后独立仪器翼加长，中央共享观测腔与计算干线连接；实际占地45×49，高39。')

    a=Build('s04',[65,55,65],'S04 研究所·第四阶（名称待定）');c=a.cx;z=34
    for x in (3,51):
        a.pod((x,1,10),(x+10,17,52),'field');a.box((x+2,18,14),(x+8,19,48),'cooler')
        for zz in (17,34,49):a.line((x+5,19,zz),(c-5 if x<c else c+5,19,zz),'pipe')
    for x in (c-5,c+5):
        for zz in (z-5,z+5):a.box((x,1,zz),(x,54,zz),'field')
    a.pod((c-4,8,z-4),(c+4,54,z+4),'fusion');a.box((c-1,9,z-1),(c+1,53,z+1),'qft')
    for yy,rr in ((13,22),(29,26),(47,19)):
        a.ring((c,yy,z),rr,'xz','frame',2);a.ring((c,yy+1,z),rr-2,'xz','coil')
        for xx in (c-rr,c+rr):a.line((xx,yy,z),(c-5 if xx<c else c+5,yy,z),'power')
    for phase in (0,math.pi):
        points=[(c+14*math.cos(phase+i*math.tau/72),8+i*46/72,z+14*math.sin(phase+i*math.tau/72)) for i in range(73)]
        for p,q in zip(points,points[1:]):a.line(p,q,'molecular')
        a.line(points[0],(c+5 if points[0][0]>c else c-5,8,z),'connector')
    for x in (c-26,c+26):a.line((x,17,z),(x,29,z),'pipe')
    for x in (15,40):
        a.pod((x,1,55),(x+9,12,61),'panel');a.line((x+4,12,55),(c-5 if x<c else c+5,13,z+5),'connector')
    yield a.finish('65×65基座上分开展开实验翼、后侧样本区与供能系统；三层宽约束环、双螺旋和55格高锚定柱构成主体，保留中轴检修净空。')

    a=Build('s05',[129,97,129],'S05 文明认知穹顶');c=a.cx;z=66
    # 两侧资料研究翼有独立计算层，后方档案厅跨中轴架空，通道不切主体。
    for x in (4,104):
        a.pod((x,1,19),(x+20,22,107),'panel')
        for zz in (28,52,76,100):
            a.pod((x+3,23,zz-5),(x+17,31,zz+5),'compute')
            a.box((x+5,32,zz-4),(x+15,33,zz+4),'cooler')
    a.pod((30,7,112),(98,30,123),'molecular')
    for xx in (30,47,81,98):a.box((xx,1,112),(xx,7,123),'power')
    # 下层研究环廊与高位穹顶分开；环廊上各站接入立柱与穹顶。
    a.ring((c,7,z),59,'xz','frame',3);a.ring((c,8,z),57,'xz','grating',2)
    a.ring((c,42,z),54,'xz','frame',3);a.ring((c,43,z),51,'xz','compute',2)
    for i in range(12):
        theta=i*math.tau/12
        xx=round(c+54*math.cos(theta));zz=round(z+54*math.sin(theta))
        if abs(xx-c)<=1:
            for sx in (c-4,c+4):a.box((sx,1,zz),(sx,7,zz),'field')
            a.line((c-4,7,zz),(c+4,7,zz),'power');a.box((xx,7,zz),(xx,42,zz),'field')
        else:
            a.box((xx,1,zz),(xx,42,zz),'field')
            a.pod((xx-2,9,zz-2),(xx+2,17,zz+2),'compute')
        a.line((xx,7,zz),(c+59*math.cos(theta),7,z+59*math.sin(theta)),'connector')
        points=[(c+54*math.cos(t)*math.cos(theta),42+54*math.sin(t),z+54*math.cos(t)*math.sin(theta)) for t in [j*math.pi/2/90 for j in range(91)]]
        for p,q in zip(points,points[1:]):a.line(p,q,'frame')
    for yy in (54,67,79,89):
        rr=round(math.sqrt(54**2-(yy-42)**2))
        a.ring((c,yy,z),rr,'xz','fusion');a.ring((c,yy-1,z),rr,'xz','molecular')
    a.pod((c-10,12,z-10),(c+10,41,z+10),'fusion')
    a.box((c-4,13,z-4),(c+4,40,z+4),'compute')
    for xx in (c-10,c+10):
        for zz in (z-10,z+10):a.box((xx,1,zz),(xx,12,zz),'power')
    for xx in (c-54,c+54):a.line((xx,22,z),(c-10 if xx<c else c+10,22,z),'connector')
    a.line((c,30,112),(c,42,120),'connector')
    yield a.finish('按总表129×129×97重新展开：十二肋资料穹顶、低位环形研究廊、双侧分段计算翼、后方架空档案厅和中央认知腔；实际穹顶最高96层，不用空白地板或空气凑高度。')

# 变更#2 2026-09-28 02:56:31：撤回未批准命名，S02至S04用阶级占位；S01不命名，S05沿用既定称呼。
