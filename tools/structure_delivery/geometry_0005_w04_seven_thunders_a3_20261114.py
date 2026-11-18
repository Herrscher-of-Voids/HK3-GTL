# -*- coding: utf-8 -*-
"""七雷悬浮供能，开口取能环与汇流母线组成天枢主景。"""
from pathlib import Path
import json
import math
import numpy as np
from w02_19c_geometry_v4_20261110 import solid_annulus
import geometry_0005_w04_em_skyhub_a1_20261114 as base

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w04-seven-thunders-a3-20261114'
Part, STATES = base.Part, base.STATES
BLACK, DARK, RED, IRON, GOLD, LIGHT = base.BLACK, base.DARK, base.RED, base.IRON, base.GOLD, base.LIGHT
PURPLE, GLASS = 'minecraft:magenta_concrete', 'minecraft:magenta_stained_glass'
TIP = np.array([-45., 144., 110.])
SCALE, LEAN = .62, math.radians(12)
MATRIX = SCALE * np.array([[math.sin(LEAN), -math.cos(LEAN), 0],
    [math.cos(LEAN), math.sin(LEAN), 0], [0, 0, 1]])
SHIFT = TIP - MATRIX @ np.array([5, 53, 0])
LEVELS = [(205, 90), (295, 110), (415, 128)]


def axis_x(y):
    return TIP[0] + (y - TIP[1]) * math.tan(LEAN)


def path(p, points, radius, state):
    for a, b in zip(points[:-1], points[1:]):
        p.beam(a, b, radius, state)


def frame():
    p = Part('field_04_后置双脊高拱约束架')
    for side in [-1, 1]:
        x = side * 235
        p.box([x-28,25,-111], [x+28,37,-45], BLACK)
        p.beam([x,37,-78], [x,342,-78], 12, BLACK)
        p.beam([x,40,-66], [x,342,-66], 4, RED)
        p.beam([x,42,-63], [x,342,-63], 1.8, GOLD)
        for y in range(64,335,36):
            p.box([x-16,y-3,-94], [x+16,y+3,-62], IRON)
    points = [[235*math.cos(a),342+240*math.sin(a),-78] for a in np.linspace(0,math.pi,101)]
    path(p, points, 11, BLACK)
    path(p, [np.array(q)+[0,0,8] for q in points], 5.5, RED)
    path(p, [np.array(q)+[0,0,14] for q in points], 1.8, GOLD)
    for a in np.linspace(.12,math.pi-.12,15):
        p.sphere([235*math.cos(a),342+240*math.sin(a),-61], 3.2, LIGHT)
    return p.finish()


def collector(index, y, radius):
    p = Part(f'field_03_{index}_前开口感应取能环与双侧接收器')
    cx = axis_x(y)
    zz, xx = np.mgrid[110-radius-11:110+radius+12, math.floor(cx-radius-12):math.ceil(cx+radius+13)]
    radial = np.hypot(xx-cx,zz-110)
    angle = np.arctan2(zz-110,xx-cx)
    opening = (angle > math.pi/4) & (angle < 3*math.pi/4)
    for dy in range(-8,10):
        keep = (radial >= radius-8) & (radial <= radius+8) & ~opening
        middle = (radial >= radius-5) & (radial <= radius+5)
        for state, mask in [(BLACK,keep & ~middle),(RED,keep & middle)]:
            p.points(np.c_[xx[mask],np.full(mask.sum(),y+dy),zz[mask]],state)
    for offset,state in [(10,IRON),(12,LIGHT)]:
        keep=(abs(radial-(radius-6))<1.4)&~opening
        p.points(np.c_[xx[keep],np.full(keep.sum(),y+offset),zz[keep]],state)
    for side in [-1,1]:
        jaw = np.array([cx+side*(radius-23),y,110.])
        p.beam([cx+side*radius,y,110],jaw,6,IRON)
        solid_annulus(p,jaw,[1,0,0],17,9,9,BLACK)
        solid_annulus(p,jaw+[side*5,0,0],[1,0,0],16,11,3,RED)
        solid_annulus(p,jaw-[side*5,0,0],[1,0,0],12,9,2,LIGHT)
        for dy in [-14,14]:
            p.beam(jaw+[side*3,dy,0],jaw+[-side*7,dy*.8,0],2.4,IRON)
        start=[cx+side*radius/math.sqrt(2),y,110-radius/math.sqrt(2)]
        route=[start,[side*180,y,-46],[side*235,y,-46]]
        path(p,route,6,BLACK)
        path(p,[np.array(q)+[0,5,0] for q in route],2.8,GOLD)
    return p.finish()


def energy(index, y, radius, sword):
    p = Part(f'energy_01_{index}_刃面向外导能弧与方向光节')
    cx = axis_x(y)
    near=sword[abs(sword[:,1]-y)<=2]
    for side in [-1,1]:
        edge=near[near[:,0].argmin() if side<0 else near[:,0].argmax()]
        end=np.array([cx+side*(radius-30),y,110.])
        start=edge.astype(float)+[side*2,0,0]
        route=[start,start*.7+end*.3+[0,8,3],start*.5+end*.5+[0,-6,-3],
            start*.25+end*.75+[0,5,2],end]
        path(p,route,2.6,PURPLE)
        path(p,route,1.1,LIGHT)
        for t in [.45,.72]:
            c=start*(1-t)+end*t
            path(p,[c+[-side*5,5,0],c+[side*2,0,0],c+[-side*5,-5,0]],1.3,LIGHT)
        branch=[start+[0,side*7,0],start*.6+end*.4+[0,side*12,-2],route[2]]
        path(p,branch,1.4,GLASS)
    return p.finish()


def discharge():
    p=Part('field_05_双侧降压汇流脊与落地超导母线')
    for side in [-1,1]:
        route=[[side*235,415,-46],[side*235,54,-46],[side*302,54,15],[side*302,54,108]]
        path(p,route,9,BLACK)
        path(p,[np.array(q)+[0,0,7] for q in route],3.2,GOLD)
        for y in range(80,410,28):
            p.box([side*235-14,y-4,-55],[side*235+14,y+4,-37],RED)
            p.box([side*235-10,y+5,-38],[side*235+10,y+6,-37],IRON)
        path(p,[[side*302,56,144],[side*210,56,144],[side*158,40,144]],3,LIGHT)
    return p.finish()


def main():
    LOG.mkdir(parents=True,exist_ok=True)
    parts=[base.deck(),base.basin()]
    parts += [base.magnet(i,r,y) for i,(r,y) in enumerate([(199,44),(163,78),(127,112)],1)]
    parts += [base.tower(s) for s in [-1,1]]+[base.cooling(s) for s in [-1,1]]+[base.control()]
    sword=list(base.imported(ROOT/'logs/w04-narukami-study-20261110/s1-components.npz',
        base.sword.STATES,'sword',MATRIX,SHIFT,base.SWORD_MAP))
    joined=np.concatenate([p.p for p in sword])
    parts += [frame(),discharge()]
    parts += [collector(i,y,r) for i,(y,r) in enumerate(LEVELS,1)]
    parts += sword+[energy(i,y,r,joined) for i,(y,r) in enumerate(LEVELS,1)]
    np.savez_compressed(LOG/'components.npz',**{k:v for p in parts for k,v in
        [(p.name+'__p',p.p),(p.name+'__states',p.states)]})
    low=np.min([p.p.min(0) for p in parts],0);high=np.max([p.p.max(0) for p in parts],0)
    sl=joined.min(0);sh=joined.max(0)
    views=dict(sword=dict(center=((sl+sh)/2).tolist(),half=((sh-sl)/2+10).tolist()),
        blade=dict(center=[-8,306,110],half=[112,140,85]),
        reactor=dict(center=[0,170,110],half=[220,155,225]),
        field=dict(center=[0,310,60],half=[260,300,200]),
        casing=dict(center=[302,120,175],half=[14,15,12]),
        torii=dict(center=[0,25,329],half=[60,38,47]),
        magnet=dict(center=[0,72,110],half=[225,80,225]),
        controller=dict(center=[0,18,329],half=[45,20,38]))
    scene=dict(states=STATES,parts=[dict(id=p.name,asset=p.name.split('_')[0]) for p in parts],
        controller_world=[0,18,329],detail_views=views,sword_bounds=dict(min=sl.tolist(),max=sh.tolist()),
        bounds_world=dict(min=low.tolist(),max=high.tolist()),
        transforms=dict(dragon_included=False,sword=dict(scale=SCALE,rotation_z=78,
            anchor=[5,53,0],target=TIP.tolist(),matrix=MATRIX.tolist(),translation=SHIFT.tolist())),
        summary='只保留七雷为主景：刀尖悬在雷池上方，刀身微倾12度；三层正面开口取能环经紫色导能弧从刃面取能，向两侧接收器、后部母线与储能塔汇流。后拱架约束悬浮场，前方保留完整刀面视线。',
        source_models=['logs/w04-narukami-study-20261110/s1-components.npz',
            'tools/structure_delivery/geometry_0005_w04_seven_thunders_a3_20261114.py'],
        source_quantization='复用S1五构件，完整源方块中心按0.62倍、绕Z78度变换后整数格量化；没有裁切源轮廓或运行时缩放。取能环正面90度开口为本次主动设计。',
        energy_design=dict(levels_y=[y for y,r in LEVELS],source='七雷刃面与刃根',
            receivers='三层双侧接收器',route='刃面→紫色导能弧→接收器→开口磁环→双侧母线→储能塔→雷池',
            sword_min_y=int(sl[1]),pool_luminous_top_y=27,tip_clearance_blocks=int(sl[1])-28,
            lower_magnet_top_y=125,tip_clearance_to_magnet_blocks=int(sl[1])-126,
            visual_only=True))
    (LOG/'scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2),'utf8')
    print(json.dumps(dict(parts=len(parts),size_xyz=(high-low+1).tolist(),
        sword_bounds=scene['sword_bounds'],source_component_blocks=sum(len(p.p) for p in parts)),ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
