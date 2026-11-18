# -*- coding: utf-8 -*-
"""按官方多角度原帧重做俱利伽罗，单主景构图保留工业基座。"""
from pathlib import Path
import json
import math
import numpy as np
from scipy.interpolate import CubicSpline
from w02_19c_geometry_v4_20261110 import SolidPart
from w04_kurikara_d1_parts_20261110 import hull, loft, blade, taper, facet, traced, body_frame
import geometry_0005_w04_em_skyhub_a1_20261114 as base
import kurikara_original_head_0005_a2_20261114 as head

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w04-kurikara-a2-20261114'
PALETTE = dict(black='minecraft:black_concrete', dark='minecraft:gray_concrete',
    red='minecraft:red_concrete', light='minecraft:white_concrete',
    ivory='minecraft:white_terracotta', metal='minecraft:iron_block', glow='minecraft:magenta_concrete')
STATES = list(dict.fromkeys(base.STATES + list(PALETTE.values())))
IDS = {state: i + 1 for i, state in enumerate(STATES)}
BLACK, DARK, RED, WHITE, IVORY = [PALETTE[k] for k in ['black', 'dark', 'red', 'light', 'ivory']]
SHIFT = np.array([0, 25, -75])


class Part(SolidPart):
    def points(self, points, state):
        points = np.rint(points).astype(np.int32).reshape(-1, 3)
        self.chunks.append(points)
        self.values.append(np.full(len(points), IDS[state], np.uint8))


def torso():
    p = Part('dragon_02_前伸弯颈与暗色V形胸腹甲')
    path = np.array([[0,146,-110],[0,164,-67],[0,182,-22],[0,211,20],[0,239,58],[0,260,105]])
    curve = CubicSpline(np.linspace(0, 1, len(path)), path, axis=0)
    radii = [34, 44, 41, 29, 21, 18]
    radius = lambda t: np.interp(t, np.linspace(0,1,len(radii)), radii)
    sections = []
    for t in np.linspace(0, 1, 74):
        _, u, v = body_frame(curve, t)
        c, r = curve(t), radius(t)
        sections.append([c + r * (u * math.cos(a) + v * math.sin(a) * .8)
                         for a in np.linspace(0, 2*math.pi, 10, endpoint=False)])
    loft(p, sections, BLACK)
    for t in [.05, .15, .27, .39, .51, .63, .75, .87]:
        axis, u, v = body_frame(curve, t)
        c, r = curve(t), radius(t)
        front = c - v * r * .73
        facet(p, [front-u*r*.78+axis*5, front-u*r*.72-axis*6,
            front-axis*15-v*6, front+u*r*.72-axis*6, front+u*r*.78+axis*5], -v, 5, DARK, 4)
        back = c + v * r * .75
        facet(p, [back-u*r*.85-axis*5, back-u*r*.75+axis*7,
            back+axis*12+v*5, back+u*r*.75+axis*7, back+u*r*.85-axis*5], v, 5, RED, 5)
        if .11 < t < .8:
            blade(p, [back-axis*4, back+v*12-axis*8, back-axis*17], [6,5,.3], 3, RED, normal=u)
    for side in [-1,1]:
        q = lambda x,y,z: np.array([side*x,y,z], float)
        blade(p, [q(21,220,39),q(39,199,19),q(49,185,-8),q(24,174,-12)],
              [6,11,12,.4], 5, RED, normal=(0,.35,1))
        blade(p, [q(28,218,20),q(51,231,0),q(72,216,-25)],
              [12,13,.3], 5, RED, normal=(0,.25,1))
        for y,z in [(224,45),(238,68)]:
            blade(p,[q(18,y,z),q(31,y+6,z-7),q(38,y+11,z-19)],
                  [5,5,.2],2,IVORY,normal=(0,0,1))
    return p.finish()


def tail():
    p = Part('dragon_03_渐细弧尾与分节背脊')
    path = np.array([[0,146,-110],[0,128,-160],[4,99,-216],[22,78,-267],
        [38,83,-312],[35,104,-344],[0,113,-358],[-30,109,-345]])
    curve = CubicSpline(np.linspace(0,1,len(path)), path, axis=0)
    radii = [28,23,18,12,8,5,2.5,.5]
    sections = []
    for t in np.linspace(0,1,85):
        _,u,v = body_frame(curve,t)
        r = np.interp(t,np.linspace(0,1,len(radii)),radii)
        sections.append([curve(t)+r*(u*math.cos(a)+v*math.sin(a)*.82)
                         for a in np.linspace(0,2*math.pi,8,endpoint=False)])
    loft(p,sections,DARK)
    for t in [.08,.18,.28,.38,.48,.58,.68]:
        axis,u,v = body_frame(curve,t)
        r = np.interp(t,np.linspace(0,1,len(radii)),radii)
        c = curve(t)+v*r*.7
        facet(p,[c-u*r*.86-axis*3,c-u*r*.72+axis*7,c+axis*12+v*3,
                 c+u*r*.72+axis*7,c+u*r*.86-axis*3],v,3,RED,3)
        if .05 < t < .68:
            blade(p,[c-axis*2,c+v*(r*.24+5)-axis*8,c-axis*16],
                  [max(2,r*.18),max(1,r*.12),.2],1.5,IVORY,normal=u)
    return p.finish()


def wing(side):
    p = Part(f'dragon_04_{side:+d}_前折翼腕与后掠宽翼膜')
    q = lambda x,y,z: np.array([side*x,y,z],float)
    root, elbow, wrist = q(29,195,-9),q(91,211,29),q(172,222,48)
    taper(p,[root,q(61,201,6),elbow,q(128,216,42),wrist],[16,16,14,12,15],BLACK,.8)
    for x,y,z in [(57,202,6),(85,211,26),(114,216,36),(144,221,44)]:
        c=q(x,y,z)
        facet(p,[c+q(-15,-5,-4),c+q(-6,11,-5),c+q(14,10,4),
            c+q(18,-3,8),c+q(0,-10,10)],[0,.4,1],4,DARK,3)
    blade(p,[root+[0,8,4],q(67,219,-2),q(97,218,20)],[10,14,.3],5,RED)
    tips=[q(392,286,-137),q(397,227,-204),q(326,166,-251),q(220,140,-224)]
    starts=[wrist+q(i*2,-i*3,-i*5) for i in range(4)]
    rear=[q(35,171,-49),q(62,148,-111),q(101,127,-158),q(146,126,-185)]
    for i in range(3):
        a=tips[i]*.78+wrist*.22
        b=tips[i+1]*.77+wrist*.23
        notch=(a+b)*.5+q(-17,13,25)
        anchor=rear[min(i+1,3)]
        for triangle in [[wrist,anchor,a],[anchor,notch,a],[anchor,b,notch]]:
            facet(p,triangle,[0,.7,1],3,DARK)
        traced(p,[anchor,notch,b],2,BLACK)
        taper(p,[wrist,anchor],[5,2],BLACK,.65)
    for i,(start,tip,width) in enumerate(zip(starts,tips,[19,21,20,15])):
        mid=start*.46+tip*.54+q(-3,18,6)
        knee=mid*.48+tip*.52+q(0,4,-3)
        normal=np.array([0,.5,1.]);normal/=np.linalg.norm(normal)
        blade(p,[start-normal*2,mid-normal*2,knee,tip],[10,width,width*.52,.3],6,BLACK,normal)
        blade(p,[start,mid,knee,tip],[8,width*.86,width*.42,.2],6,RED,normal)
        inset=[start*.3+mid*.7+normal*6,mid*.4+knee*.6+normal*5,tip*.72+knee*.28]
        blade(p,inset,[3,4,.2],1.6,IVORY,normal)
        if i < 2:
            traced(p,[start*.65+mid*.35+normal*7,start*.3+mid*.7+normal*7],1.5,WHITE)
    blade(p,[wrist,q(157,200,76),q(138,190,70)],[9,8,.2],4,RED)
    facet(p,[wrist+q(-17,10,4),wrist+q(1,22,4),wrist+q(24,9,8),wrist+q(3,-10,13)],
          [0,.4,1],5,RED,5)
    return p.finish()


def hindleg(side):
    p=Part(f'dragon_05_{side:+d}_腹下反折后足与三趾钩爪')
    q=lambda x,y,z:np.array([side*x,y,z],float)
    route=[q(33,157,-66),q(56,133,-36),q(48,105,1),q(54,111,45)]
    taper(p,route,[18,17,10,8],BLACK,.8)
    blade(p,[route[0]+[0,5,6],route[1]+[0,5,9],route[2]+[0,3,5]],
          [14,13,6],4,RED)
    for x,y,z in [(52,128,-26),(50,114,-7),(50,108,10)]:
        c=q(x,y,z)
        facet(p,[c+q(-9,7,-5),c+q(9,7,-5),c+q(8,-5,7),c+q(0,-8,11),c+q(-8,-5,7)],
              [0,.1,1],4,DARK,3)
    for dx in [-8,0,8]:
        toe=[route[-1]+[dx,0,-3],route[-1]+[dx,1,13],route[-1]+[dx,-8,24]]
        taper(p,toe,[4.5,4,.2],RED,.7)
        taper(p,[toe[1]+[0,0,2],toe[2]],[2.3,.2],IVORY,.65)
    return p.finish()


def industrial():
    old=[base.deck(),base.basin()]
    old += [base.magnet(i,r,y) for i,(r,y) in enumerate([(199,44),(163,78),(127,112)],1)]
    old += [base.tower(s) for s in [-1,1]]+[base.cooling(s) for s in [-1,1]]+[base.control()]
    remap=np.array([0]+[IDS[s] for s in base.STATES],np.uint8)
    for p in old:
        p.states=remap[p.states]
    return old


def mounts():
    p=Part('base_04_后部龙躯磁悬托架')
    for side in [-1,1]:
        p.box([side*70-18,25,-208],[side*70+18,32,-164],base.BLACK)
        p.beam([side*70,31,-186],[side*27,123,-169],6,base.BLACK)
        p.beam([side*70,37,-186],[side*27,129,-169],2,base.RED)
    return p.finish()


def main():
    LOG.mkdir(parents=True,exist_ok=True)
    dragon=[tail(),torso(),wing(-1),wing(1),hindleg(-1),hindleg(1),head.build(Part,PALETTE)]
    for p in dragon:
        p.p += SHIFT
        print(p.name,len(p.p),flush=True)
    parts=industrial()+[mounts()]+dragon
    np.savez_compressed(LOG/'components.npz',**{k:v for p in parts for k,v in
        [(p.name+'__p',p.p),(p.name+'__states',p.states)]})
    low=np.min([p.p.min(0) for p in parts],0);high=np.max([p.p.max(0) for p in parts],0)
    dl=np.min([p.p.min(0) for p in dragon],0);dh=np.max([p.p.max(0) for p in dragon],0)
    details=dict(reactor=dict(center=[0,72,110],half=[225,80,225]),
        dragon=dict(center=((dl+dh)/2).tolist(),half=((dh-dl)/2+6).tolist()),
        field=dict(center=[0,125,120],half=[350,112,240]),
        head=dict(center=[0,324,55],half=[65,102,99]),
        casing=dict(center=[302,120,175],half=[14,15,12]),
        torii=dict(center=[0,25,329],half=[60,38,47]),
        magnet=dict(center=[0,72,110],half=[225,80,225]),
        controller=dict(center=[0,18,329],half=[45,20,38]))
    scene=dict(states=STATES,parts=[dict(id=p.name,asset=p.name.split('_')[0]) for p in parts],
        controller_world=[0,18,329],detail_views=details,
        transforms=dict(dragon=dict(scale=1,translation=SHIFT.tolist(),reconstructed=True),sword_included=False),
        summary='只保留俱利伽罗为角色主景；按官方原帧重做尖楔红面甲、后掠长角、前伸弯颈、暗色V腹甲及宽翼膜，移除七雷与剑托。工业基座、三层磁环与双塔保留。',
        bounds_world=dict(min=low.tolist(),max=high.tolist()),dragon_bounds=dict(min=dl.tolist(),max=dh.tolist()),
        source_models=['tools/structure_delivery/geometry_0005_w04_kurikara_a2_20261114.py',
            'tools/structure_delivery/kurikara_original_head_0005_a2_20261114.py'],
        reference_manifest='logs/0005-w04-kurikara-reference-a2-20261114/official/reference-manifest.json',
        source_quantization='官方多角度原帧人工分面几何转译，直接生成整数格；未使用下载模型或旧D4龙体，未按名义尺寸裁切。')
    (LOG/'scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2),'utf8')
    print(json.dumps(dict(parts=len(parts),size_xyz=(high-low+1).tolist(),
        source_component_blocks=sum(len(p.p) for p in parts)),ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
