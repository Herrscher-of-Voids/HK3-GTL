# -*- coding: utf-8 -*-
"""W04首版：鬼角双极围合悬刃工位，绯雷红与黑紫机械甲。"""
from pathlib import Path
import math
import numpy as np
from w02_19c_geometry_v4_20261110 import SolidPart,hull,tube,solid_annulus as annulus,bezier,basis

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W04_鸣霆超导电磁天枢_鬼角悬刃_A1_20261110'
LOG=ROOT/'logs/w04-thunder-canyon-a1-20261110'
BLACK='minecraft:deepslate_tiles'
RED='hk3gtl:voltage_machine_casing_hrv'
SILVER='minecraft:light_gray_concrete'
WHITE='minecraft:white_concrete'
DARK='minecraft:black_concrete'
PURPLE='minecraft:amethyst_block'
GLASS='minecraft:purple_stained_glass'
LIGHT='minecraft:sea_lantern'
STATES=[BLACK,RED,SILVER,WHITE,DARK,PURPLE,GLASS,LIGHT]
IDS={state:i+1 for i,state in enumerate(STATES)}
ROLES=dict(zip(STATES,['黑色机械装甲','雷之律者绯雷红#C93F63','银色磁轭与刃口','小面积白色骨瓷绝缘件','深黑内衬','紫色晶格线圈','静态雷场玻璃','少量冷白放电尖端']))


class Part(SolidPart):
    def points(self,points,state):
        a=np.rint(points).astype(np.int32).reshape(-1,3)
        if len(a):
            assert np.all(abs(a)<2048),'完整生成，不能裁切构件'
            self.chunks.append(a);self.values.append(np.full(len(a),IDS[state],np.uint8))


def slab(p,outline,y0,y1,state):hull(p,[(x,y,z) for y in [y0,y1] for x,z in outline],state)


def deck():
    p=Part('01_双岸机械基座与中央峡谷')
    for s in [-1,1]:
        outline=[(s*x,z) for x,z in [(126,-210),(290,-250),(348,-192),(348,202),(285,250),(126,209)]]
        slab(p,outline,0,6,BLACK);slab(p,outline,28,35,BLACK)
        for z in [-200,-120,-40,40,120,200]:
            p.box([s*240-10,6,z-12],[s*240+10,28,z+12],DARK)
            p.box([s*240-12,16,z-10],[s*240+12,19,z+10],RED)
        for x in [s*137,s*320]:
            p.box([x-3,36,-190],[x+3,38,191],SILVER)
            p.box([x-1,39,-190],[x+1,39,191],RED)
        for z in range(-180,201,30):p.beam([s*155,36,z],[s*300,36,z],1.5,RED)
    slab(p,[(-155,-226),(-100,-282),(100,-282),(155,-226),(132,-195),(-132,-195)],0,26,BLACK)
    for z in [-258,-225]:p.beam([-95,28,z],[95,28,z],3,RED)
    return p.finish()


def horn(side):
    p=Part(f'02_{side:+d}_鬼角电极主脊')
    path=np.array([[side*245,35,-72],[side*291,184,-48],[side*216,315,-5],[side*72,339,5]],float)
    def cross(t,rx,rz):
        c=bezier(path,t);axis=bezier(path,min(1,t+.001))-bezier(path,max(0,t-.001));axis,u,w=basis(axis)
        return c+np.array([[x*rx,0,z*rz] for x,z in [(-1,0),(-.65,.7),(0,1),(.65,.7),(1,0),(.65,-.7),(0,-1),(-.65,-.7)]])[:,[0,1,2]]@np.array([u,axis,w])
    ts=np.linspace(0,1,35)
    for a,b in zip(ts[:-1],ts[1:]):
        ra=28*(1-a)**.6+1;rb=28*(1-b)**.6+1
        hull(p,np.vstack([cross(a,ra,ra*.74),cross(b,rb,rb*.74)]),BLACK)
    for flank in [-1,1]:
        route=[]
        for t in ts:
            c=bezier(path,t);axis,u,w=basis(bezier(path,min(1,t+.001))-bezier(path,max(0,t-.001)))
            radius=28*(1-t)**.6+1;route.append(c+w*flank*radius*.74)
        tube(p,route,2.5,RED)
    for i,t in enumerate(np.linspace(.04,.91,16)):
        c=bezier(path,t);axis,u,w=basis(bezier(path,t+.002)-bezier(path,t-.002));r=28*(1-t)**.6+3
        annulus(p,c,axis,r,r-3,5,RED if i%3 else SILVER)
        annulus(p,c+axis*4,axis,r-1,r-3,2,PURPLE)
    return p.finish()


def generators(side,z):
    p=Part(f'03_{side:+d}_{z:+d}_超导脉冲堆')
    c=np.array([side*253,43,z]);annulus(p,c,[0,1,0],42,0,8,BLACK)
    for y,r in [(53,35),(68,32),(86,27),(102,22)]:
        annulus(p,[c[0],y,z],[0,1,0],r,r-7,7,RED)
        annulus(p,[c[0],y+5,z],[0,1,0],r-3,r-6,3,PURPLE)
    for a in np.linspace(0,2*math.pi,8,endpoint=False):
        p.beam(c+[37*math.cos(a),0,37*math.sin(a)],c+[19*math.cos(a),66,19*math.sin(a)],3,SILVER)
    annulus(p,[c[0],109,z],[0,1,0],18,11,4,WHITE)
    tube(p,[[c[0],50,z],[side*157,50,z],[side*157,50,-70],[side*217,50,-70]],5,BLACK)
    tube(p,[[c[0],55,z],[side*157,55,z],[side*157,55,-70],[side*217,55,-70]],1.5,RED)
    return p.finish()


def sword():
    p=Part('04_中央悬浮电磁太刀')
    stations=[(-103,91,1),(-66,137,10),(-26,199,14),(5,263,16)]
    for (x,y,w),(x1,y1,w1) in zip(stations[:-1],stations[1:]):
        hull(p,[(x+dx,y,z) for dx in [-w,w] for z in [2,12]]+[(x1+dx,y1,z) for dx in [-w1,w1] for z in [2,12]],SILVER)
        hull(p,[(x+dx,y,z) for dx in [-w*.57,w*.6] for z in [1,13]]+[(x1+dx,y1,z) for dx in [-w1*.57,w1*.6] for z in [1,13]],DARK)
        p.beam([x+w*.7,y,13],[x1+w1*.7,y1,13],1.5,RED)
    p.beam([-26,257,7],[41,279,7],5,RED)
    p.beam([7,274,7],[29,326,7],8,BLACK)
    for t in np.linspace(0,1,7):
        c=np.array([7,274,7])+np.array([22,52,0])*t;annulus(p,c,[22,52,0],9,6,3,RED)
    p.beam([29,326,7],[31,333,7],9,SILVER)
    return p.finish()


def field_core():
    p=Part('05_中央极化工位与静态放电')
    c=np.array([0,163,-12]);p.sphere(c,22,DARK)
    for axis in [[0,0,1],[0,1,0],[1,0,0]]:
        annulus(p,c,axis,31,27,4,PURPLE);annulus(p,c,axis,33,31,1,RED)
    for s in [-1,1]:
        tube(p,[[s*162,127,-12],[s*144,166,-12],[s*103,190,-12],[s*82,170,-12],[s*36,166,-12]],1.4,GLASS)
    annulus(p,[0,63,-12],[0,1,0],65,61,7,BLACK)
    annulus(p,[0,67,-12],[0,1,0],62,59,3,RED)
    for a in np.linspace(0,2*math.pi,8,endpoint=False):
        c=np.array([57*math.cos(a),68,-12+57*math.sin(a)]);p.beam(c,c+[0,28,0],3,BLACK)
        p.beam(c+[0,28,0],c*.72+[0,53,-3],1,GLASS)
    return p.finish()


def electrodes(side):
    p=Part(f'06_{side:+d}_峡谷内侧分层放电齿')
    for i,y in enumerate([105,157,210]):
        x=side*(205-i*8);z=-25+i*14
        hull(p,[(x+side*a,y+b,z+c) for a,b,c in [(25,-12,-17),(25,12,-17),(25,-12,17),(25,12,17),(-25,2,-8),(-25,2,8)]],BLACK)
        p.beam([x+side*23,y+10,z],[x-side*17,y+4,z],2,RED)
        annulus(p,[x-side*24,y+2,z],[side,0,0],8,4,3,WHITE)
        p.sphere([x-side*27,y+2,z],3,LIGHT)
    return p.finish()


def control_bridge():
    p=Part('07_前方御雷舰桥与观察步道')
    slab(p,[(-90,213),(-50,195),(50,195),(90,213),(65,282),(-65,282)],0,10,BLACK)
    for x in [-58,58]:
        hull(p,[(x+dx,y,z+dz) for dx,y,z in [(-7,10,247),(7,10,247),(5,51,229),(-5,51,229)] for dz in [-4,4]],RED)
        p.beam([x,13,253],[x,44,237],1.5,SILVER)
    for z in range(75,248):
        y=17+max(0,(247-z)//6);p.box([-18,y-3,z],[18,y,z],BLACK)
        for x in [-19,19]:p.box([x,y,z],[x,y+1,z],RED)
    p.box([-15,11,261],[15,32,268],DARK);p.box([-10,16,269],[10,28,269],PURPLE)
    p.box([-2,20,270],[2,24,270],LIGHT)
    for x in [-38,-28,28,38]:p.box([x-3,14,262],[x+3,22,268],SILVER)
    return p.finish()


def build():
    parts=[deck(),horn(-1),horn(1)]+[generators(s,z) for s in [-1,1] for z in [-158,126]]
    parts += [sword(),field_core(),electrodes(-1),electrodes(1),control_bridge()]
    points=np.concatenate([p.p for p in parts]);lo,hi=points.min(0),points.max(0);size=hi-lo+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    for p in parts:
        at=p.p-lo;cube[at[:,1],at[:,2],at[:,0]]=p.states
    return cube,dict(name='hk3gtl-w04-thunder-canyon-a1-20261110',title='雷之律者 · 鸣霆·超导电磁天枢 · 鬼角悬刃A1',
        size=size.tolist(),blocks=int(np.count_nonzero(cube)),blueprint_bounds=dict(min=lo.tolist(),max=hi.tolist()),
        blueprint_to_export_offset_xyz=(-lo).tolist(),center_blueprint=[0,170,7],controller=None,ports=[],
        display_version='A1',animation_enabled=False,approved=False,installed=False,game_verified=False,
        palette_identity=dict(name='绯雷红',color='#C93F63',tier='HRV',runtime_voltage='WSV'),
        nominal_reference_xzy=[697,565,339],no_nominal_clipping=True,design_original=True,
        summary='双岸机械基座围出放电峡谷，两条向内弯折的鬼角电极夹住悬浮太刀；四座超导脉冲堆沿外侧回流，中心极化工位及前控观察桥保持清楚视线。',
        source_conflicts=['本项目首版原创组合，借用雷之律者黑红甲、角形与刀的视觉语言，不宣称官方机械复刻。','未使用始源之律者造型；HRV绯雷红为身份基准，紫色只用于电磁晶格。','完整几何先生成再求边界，未进行游戏实装或功能验收。']),parts


if __name__=='__main__':
    _,m,_=build();print(m['size'],m['blocks'])
