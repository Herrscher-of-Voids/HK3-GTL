# -*- coding: utf-8 -*-
"""完整P3的整数格部件；不使用纯色几何草模或运行时缩放模型。"""
import math
import numpy as np
from scipy.ndimage import map_coordinates,distance_transform_edt
from w02_19c_geometry_v4_20261110 import SolidPart
from w04_kurikara_d1_parts_20261110 import hull,loft
import w04_layout_p2_parts_20261110 as old
import w04_kurikara_d4_20261110 as dragon
import w04_narukami_s1_20261110 as sword

BLACK='minecraft:polished_blackstone_bricks';DARK='minecraft:deepslate_tiles'
RED='hk3gtl:voltage_machine_casing_hrv';GOLD='minecraft:gold_block';IRON='minecraft:iron_block'
LIGHT='minecraft:sea_lantern';GLASS='minecraft:red_stained_glass';QUARTZ='minecraft:quartz_block'
INTERFACE='hk3gtl:wonder_thunder_interface';CONTROLLER='minecraft:redstone_block'
DRAGON_MAP={'minecraft:black_concrete':BLACK,'minecraft:gray_concrete':'minecraft:polished_deepslate',
    'minecraft:cyan_terracotta':DARK,'minecraft:red_concrete':RED,'minecraft:pink_terracotta':'hk3gtl:wonder_thunder_casing',
    'minecraft:white_terracotta':QUARTZ,'minecraft:white_concrete':QUARTZ,'minecraft:light_gray_concrete':IRON}
SWORD_MAP={'minecraft:black_concrete':BLACK,'minecraft:gray_concrete':DARK,
    'minecraft:white_concrete':QUARTZ,'minecraft:light_gray_concrete':IRON}
STATES=list(dict.fromkeys([*map(lambda s:DRAGON_MAP.get(s,s),dragon.STATES),
    *map(lambda s:SWORD_MAP.get(s,s),sword.STATES),*old.STATES,BLACK,DARK,RED,GOLD,IRON,LIGHT,GLASS,QUARTZ,INTERFACE,CONTROLLER]))
IDS={s:i+1 for i,s in enumerate(STATES)}
DRAGON_SHIFT=np.array([0,185,-40]);RINGS=[(105,18),(142,-22),(190,35)]
ANGLE=22;SWORD_SCALE=.64
ax=math.radians(ANGLE);RX=np.array([[1,0,0],[0,math.cos(ax),-math.sin(ax)],[0,math.sin(ax),math.cos(ax)]])
SWORD_MATRIX=RX@np.array([[0,-1,0],[1,0,0],[0,0,1]])*SWORD_SCALE
SWORD_ANCHOR=np.array([5.,53.,0.]);SWORD_TARGET=np.array([0.,95.,235.])


class Part(SolidPart):
    def points(self,points,state):
        at=np.rint(points).astype(np.int32).reshape(-1,3)
        if len(at):
            assert np.all(abs(at)<2048),'完整几何越过编码范围，只报错、不裁切'
            self.chunks.append(at);self.values.append(np.full(len(at),IDS[state],np.uint8))


def imported(npz,states,prefix,shift,mapping):
    for name in npz.files:
        if not name.endswith('__p'):continue
        base=name[:-3];p=Part(prefix+'_'+base)
        points=npz[name]+shift;values=npz[base+'__states']
        for i,state in enumerate(states,1):p.points(points[values==i],mapping.get(state,state))
        yield p.finish()


def sword_parts(npz):
    for name in npz.files:
        if not name.endswith('__p'):continue
        base=name[:-3];points=npz[name];values=npz[base+'__states'];low=points.min(0)-2;high=points.max(0)+2
        size=high-low+1;dense=np.zeros(tuple(size),np.uint8);dense[tuple((points-low).T)]=values
        occupied=(dense>0).astype(np.float32)
        nearest=distance_transform_edt(dense==0,return_distances=False,return_indices=True);nearest_values=dense[tuple(nearest)]
        corners=np.array([[x,y,z] for x in [low[0],high[0]+1] for y in [low[1],high[1]+1] for z in [low[2],high[2]+1]])
        transformed=(corners-SWORD_ANCHOR)@SWORD_MATRIX.T+SWORD_TARGET
        lo=np.floor(transformed.min(0)-1).astype(int);hi=np.ceil(transformed.max(0)+1).astype(int)
        zz,xx=np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1];inverse=np.linalg.inv(SWORD_MATRIX)
        p=Part('sword_'+base)
        for y in range(lo[1],hi[1]+1):
            at=np.c_[xx.ravel(),np.full(xx.size,y),zz.ravel()]
            source=(at+.5-SWORD_TARGET)@inverse.T+SWORD_ANCHOR-low-.5
            keep=map_coordinates(occupied,source.T,order=1,mode='constant',cval=0,prefilter=False)>.22
            ids=map_coordinates(nearest_values,source[keep].T,order=0,mode='nearest',prefilter=False)
            for i in np.unique(ids):p.points(at[keep][ids==i],SWORD_MAP.get(sword.STATES[i-1],sword.STATES[i-1]))
        # 全部源方块中心参与量化，保留薄刃与端点；缩放合并不是边界裁切。
        mapped=np.floor((points+.5-SWORD_ANCHOR)@SWORD_MATRIX.T+SWORD_TARGET).astype(int)
        for i,state in enumerate(sword.STATES,1):p.points(mapped[values==i],SWORD_MAP.get(state,state))
        yield p.finish()


def field_parts():
    saved=old.Part;old.Part=Part
    try:
        for i,(r,a) in enumerate(RINGS,1):
            p=old.ring(i,r,a);p.name=f'field_01_{i}_三巴纹双轨雷鼓磁环';yield p
        for side in [-1,1]:
            p=old.tower(side);p.name=f'field_02_{side:+d}_鬼角电容塔';yield p
            p=Part(f'field_03_{side:+d}_外缘赤金链环')
            start=np.array([side*320,217,269.]);end=np.array([side*198,180,235.]);axis=end-start;axis/=np.linalg.norm(axis)
            u=np.cross(axis,[0,0,1]);u/=np.linalg.norm(u);v=np.cross(axis,u)
            for i,t in enumerate(np.linspace(0,1,13)):old.annulus(p,start*(1-t)+end*t,u if i%2 else v,9,5,3,GOLD)
            p.sphere(start,12,BLACK);p.sphere(end,9,BLACK);yield p.finish()
    finally:old.Part=saved
    for side in [-1,1]:
        p=Part(f'field_04_{side:+d}_绯红超导母线廊桥')
        path=np.array([[side*260,37,-320],[side*170,45,-210],[side*100,106,-110],[side*58,247,-55]],float)
        for a,b in zip(path[:-1],path[1:]):
            p.beam(a,b,10,BLACK);p.beam(a+[0,7,0],b+[0,7,0],5,RED)
            for sign in [-1,1]:p.beam(a+[sign*7,11,0],b+[sign*7,11,0],1.7,GOLD)
        yield p.finish()
    p=Part('field_05_龙口与刀尖螺旋电弧')
    old.spiral(p,[0,415,181],[0,75,235],8,3.5);old.spiral(p,[0,94,235],[0,75,235],4,1.2)
    yield p.finish()


def deck():
    p=Part('base_01_下沉八角船坞与检修格栅')
    zz,xx=np.mgrid[-470:586,-470:471];cut=65
    octagon=(abs(xx)<=470)&(zz>=-470)&(zz<=585)&(abs(xx)+np.maximum(-zz-405,zz-520)<=470)
    radial=np.hypot(xx,zz-235);hole=radial<185
    for y in range(-10,25):
        edge=(abs(xx)>460)|(zz<-460)|(zz>575)|(abs(xx)+np.maximum(-zz-405,zz-520)>458)
        shell=(y< -7)|(y>=22)|edge
        # 保留原Y=18主控位置，前庭下沉通道不能被新甲板表皮封住。
        access=(abs(xx)<=24)&(zz>=419)&(y>=13)
        keep=octagon&~hole&shell&~access
        if y>=22:
            # 大平面留机械分块缝，框架与表皮均为实际方块。
            ribs=(abs(xx)%36<=2)|(abs(zz)%36<=2)
            for state,mask in [(BLACK,keep&~ribs),(DARK,keep&ribs)]:p.points(np.c_[xx[mask],np.full(np.count_nonzero(mask),y),zz[mask]],state)
        else:p.points(np.c_[xx[keep],np.full(np.count_nonzero(keep),y),zz[keep]],BLACK)
    for x in range(-432,433,72):
        if abs(x)<190:continue
        for z in [-408,-264,-120,24,168,312,456]:p.box([x-3,-7,z-3],[x+3,21,z+3],DARK)
    for side in [-1,1]:
        x=side*450;p.box([min(x-3,x+3),24,-398],[max(x-3,x+3),27,514],RED)
    p.box([-24,10,419],[24,12,554],BLACK)
    for step in range(12):p.box([-24,10,555+step*2],[24,13+step,556+step*2],DARK)
    return p.finish()


def reactor():
    p=Part('base_02_八角下沉托卡马克雷池')
    for outer,inner,y0,y1,state in [(182,0,-37,-34,BLACK),(181,170,-33,17,BLACK),(183,177,18,25,IRON),
        (166,158,-30,-24,RED),(139,133,-30,-27,GOLD),(110,106,-30,-27,LIGHT),(76,72,-30,-27,RED)]:
        old.annulus(p,[0,(y0+y1)/2,235],[0,1,0],outer,inner,y1-y0+1,state)
    for i in range(16):
        a=i*math.pi/8;radial=np.array([math.sin(a),0,math.cos(a)]);tangent=np.array([math.cos(a),0,-math.sin(a)])
        center=np.array([0,28,235])+radial*176
        for width,height,depth,dy,state in [(7,22,14,0,BLACK),(8,6,11,5,RED),(5,2,14,17,GOLD)]:
            hull(p,[center+tangent*x+radial*z+[0,y+dy,0] for x in [-width,width] for y in [-height,height] for z in [-depth,depth]],state)
    old.annulus(p,[0,22,235],[0,1,0],17,0,102,RED);old.annulus(p,[0,75,235],[0,1,0],9,0,6,LIGHT)
    p.finish()
    # 正前磁轭和池沿预留主控检修门洞，避免遮住固定坐标的3×3接口墙。
    doorway=(abs(p.p[:,0])<=24)&(p.p[:,2]>=409)&(p.p[:,1]>=13)&(p.p[:,1]<=40)
    p.p=p.p[~doorway];p.states=p.states[~doorway]
    return p


def storage(side):
    p=Part(f'base_03_{side:+d}_五联真实超导储能列')
    for i in range(5):
        x=side*260;z=-340+i*92
        p.box([x-35,25,z-33],[x+35,50,z+33],BLACK)
        p.box([x-24,51,z-24],[x+24,102,z+24],DARK)
        for y in [57,73,89]:
            old.annulus(p,[x,y,z],[0,1,0],30,25,8,RED)
            old.annulus(p,[x,y+5,z],[0,1,0],31,28,2,IRON)
        p.box([x-28,103,z-27],[x+28,110,z+27],IRON)
        p.box([x-3,112,z-12],[x+3,115,z+12],GOLD)
    return p.finish()


def torii():
    p=Part('base_04_三进黑金超导鸟居与检修前庭')
    for z,width,height in [(390,156,94),(465,194,115),(540,232,137)]:
        for side in [-1,1]:
            x=side*(width/2-22)
            p.box([x-6,25,z-8],[x+6,height-10,z+8],BLACK)
            p.box([x-2,34,z+9],[x+2,height-17,z+11],RED)
            old.annulus(p,[x,50,z],[0,1,0],11,6,6,IRON)
            old.annulus(p,[x,72,z],[0,1,0],10,6,6,RED)
        p.box([-width//2,height-14,z-9],[width//2,height-7,z+9],RED)
        hull(p,[[-width/2-10,height+4,z-10],[-width/2-7,height+11,z-10],[-width/4,height+5,z-10],
            [0,height+1,z-10],[width/4,height+5,z-10],[width/2+7,height+11,z-10],[width/2+10,height+4,z-10],
            *[[x,y,z+10] for x,y in [(-width/2-10,height+4),(-width/2-7,height+11),(-width/4,height+5),(0,height+1),(width/4,height+5),(width/2+7,height+11),(width/2+10,height+4)]]],BLACK)
        p.box([-width//2+12,height+2,z+11],[width//2-12,height+4,z+13],GOLD)
    # 3×3实体位置保留；红石块是未注册W04主控的明确占位标记。
    p.box([-75,-8,385],[75,12,433],BLACK);p.box([-22,13,409],[22,37,418],RED)
    for x in [-1,0,1]:
        for dy in [-1,0,1]:p.box([x,18+dy,419],[x,18+dy,419],CONTROLLER if x==0 and dy==0 else INTERFACE)
    for z in range(435,579,12):
        p.box([-52,25,z],[-25,26,z+2],IRON);p.box([25,25,z],[52,26,z+2],IRON)
    return p.finish()


def build():
    parts=list(imported(np.load(dragon.LOG/'components.npz'),dragon.STATES,'dragon',DRAGON_SHIFT,DRAGON_MAP))
    parts+=list(sword_parts(np.load(dragon.ROOT/'logs/w04-narukami-study-20261110/s1-components.npz')))
    parts+=list(field_parts());parts+=[deck(),reactor(),storage(-1),storage(1),torii()]
    return parts
