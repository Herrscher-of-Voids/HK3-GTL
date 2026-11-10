# -*- coding: utf-8 -*-
"""以游戏原帧校准腿爪和叠甲，玩家写实三维仅辅助体积判断。"""
import json
import numpy as np
import w04_kurikara_d1_20261110 as prior
from w04_kurikara_d1_parts_20261110 import *
from w04_kurikara_d1_body_20261110 import torso_neck as old_torso
from w04_kurikara_d1_head_wings_20261110 import wing_arm as old_wing

PRIOR=OUT
OUT=ROOT/'deliveries/W04_俱利伽罗_腿爪与叠甲细化_D2_20261110'
LOG=ROOT/'logs/w04-kurikara-d2-20261110'
SWORD=prior.SWORD


def inherit(source,recolor=None):
    p=Part(source.name)
    for value in np.unique(source.states):
        state=STATES[int(value)-1]
        p.points(source.p[source.states==value],(recolor or {}).get(state,state))
    return p


def hindleg(side):
    p=Part(f'06_{side:+d}_粗壮折腿宽掌与钩爪')
    q=lambda x,y,z:np.array([side*x,y,z],float)
    hip,knee,hock,ankle,palm=[q(*v) for v in [(26,137,-52),(53,106,-16),(43,67,2),(49,39,28),(49,28,46)]]
    taper(p,[hip,q(43,125,-37),knee,hock,ankle,palm],[21,25,22,15,14,18],BLACK,.88)
    taper(p,[hip,q(46,122,-33),knee],[20,24,20],RED,.85)
    # 大腿红甲逐片叠压，内缘是骨白的锯齿状甲列。
    for t,width in zip([.12,.31,.50,.69,.86],[19,21,20,18,15]):
        c=hip*(1-t)+knee*t+np.array([0,0,16])
        points=[c+q(-width,9,-2),c+q(-width*.8,-2,6),c+q(0,-14,10),
            c+q(width*.8,-2,6),c+q(width,9,-2),c+q(0,14,0)]
        facet(p,points,[0,.25,1],4,BLACK,3)
        facet(p,[c+q(-width+2,8,2),c+q(-width*.65,-2,9),c+q(0,-11,14),
            c+q(width*.65,-2,9),c+q(width-2,8,2),c+q(0,10,6)],[0,.3,1],3,RED,3)
        c=c+q(-8,-2,9);w=8 if t<.6 else 6
        facet(p,[c+q(-w,7,0),c+q(-w,0,2),c+q(0,-9,6),c+q(w,0,2),c+q(w,7,0)],
            [0,.2,1],2.5,IVORY,2)
        traced(p,[c+q(-w,0,4),c+q(0,-9,8),c+q(w,0,4)],1.1,BLACK)
    # 膝甲与反折跗关节保留体积，避免整根细杆只贴一片平板。
    for c,width in [(knee,19),(hock,14),(ankle,16)]:
        facet(p,[c+q(-width,9,7),c+q(-width,-4,11),c+q(0,-13,19),
            c+q(width,-4,11),c+q(width,9,7),c+q(0,14,12)],[0,.15,1],7,BLACK,4)
        facet(p,[c+q(-width+3,7,12),c+q(0,-9,23),c+q(width-3,7,12),c+q(0,12,17)],
            [0,.1,1],3,DARK,2)
    for t in [.23,.48,.73]:
        c=knee*(1-t)+hock*t+q(0,0,13);w=14-t*3
        facet(p,[c+q(-w,7,0),c+q(-w,-3,2),c+q(0,-12,8),c+q(w,-3,2),c+q(w,7,0)],
            [0,0,1],4,DARK,3)
        traced(p,[c+q(-w,-3,5),c+q(0,-12,11),c+q(w,-3,5)],1.6,IVORY)
    # 宽爪掌与三根分开的指节，爪尖向下内钩，不再做向上翘的平底饰片。
    taper(p,[ankle,palm,q(49,26,60)],[14,23,21],BLACK,.66)
    facet(p,[q(27,37,39),q(49,43,42),q(71,37,39),q(74,27,60),q(49,22,70),q(24,27,60)],
        [0,.9,.2],5,DARK,3)
    for j,dx in enumerate([-17,0,17]):
        length=12 if j==1 else 0
        a=q(49+dx,29,54);b=q(49+dx*1.15,24,72+length)
        c=q(49+dx*1.3,16,87+length)
        taper(p,[a,b,c],[8.3,8,5.5],BLACK,.80)
        for t in [.18,.52]:
            at=a*(1-t)+b*t
            facet(p,[at+q(-7,3,-4),at+q(0,7,0),at+q(7,3,-4),at+q(6,0,8),at+q(-6,0,8)],
                [0,1,.1],2.5,DARK,1.5)
        claw=[b+q(0,4,1),c+q(0,5,0),q(49+dx*1.36,9,96+length),q(49+dx*1.32,3,110+length)]
        # 爪尖两个横向尺寸同时收束，避免固定厚度棱柱留下方头。
        sections=[];normal=np.array([1.,0,0])
        for k,(center,width,depth) in enumerate(zip(claw,[5,7,4,.15],[6,6,3.5,.15])):
            axis=claw[min(k+1,3)]-claw[max(k-1,0)];u=np.cross(normal,axis);u/=np.linalg.norm(u)
            sections.append(np.array([center-u*width,center+normal*depth,center+u*width,center-normal*depth]))
        loft(p,sections,RED)
        blade(p,[claw[0]+q(0,1,0),claw[1]+q(0,1,0),claw[2]+q(0,1,0)],
            [1.4,2,.2],.8,TRIM,normal=(1,0,0))
        traced(p,[b+q(-5,4,1),c+q(-4,4,0)],1.1,BLACK)
    return p.finish()


def torso_neck():
    p=inherit(old_torso(),{SILVER:DARK})
    # 连续重叠的胸腹甲取代横向栏杆观感；细边沿甲面贴合。
    for y,z,w in [(202,35,30),(185,35,35),(168,25,32),(151,7,27),(136,-10,21)]:
        c=np.array([0.,y,z])
        outer=[c+[-w,9,0],c+[-w*.82,-3,3],c+[0,-16,12],c+[w*.82,-3,3],c+[w,9,0],c+[0,4,6]]
        facet(p,outer,[0,.2,1],5,BLACK,3)
        inner=[c+[-w+3,6,3],c+[-w*.68,-3,7],c+[0,-12,15],c+[w*.68,-3,7],c+[w-3,6,3],c+[0,5,10]]
        facet(p,inner,[0,.2,1],2.5,DARK,3)
        traced(p,[c+[-w*.76,-2,9],c+[0,-13,17],c+[w*.76,-2,9]],1.4,SILVER)
    path=np.array([[0,211,44],[0,226,69],[0,242,95],[0,258,121]],float)
    for i,t in enumerate(np.linspace(0,1,10)):
        f=t*3;k=min(int(f),2);c=path[k]*(1-(f-k))+path[k+1]*(f-k)
        w=19-4*t;c=c+[0,-8,14]
        facet(p,[c+[-w,7,0],c+[-w*.9,-2,4],c+[0,-12,12],c+[w*.9,-2,4],c+[w,7,0]],
            [0,-.3,1],3,BLACK,2)
        facet(p,[c+[-w+2,6,3],c+[0,-9,15],c+[w-2,6,3],c+[0,9,5]],
            [0,-.3,1],2.5,DARK,2)
    return p.finish()


def wing_arm(side):
    p=inherit(old_wing(side));q=lambda x,y,z:np.array([side*x,y,z],float)
    for x,y,z,w in [(78,199,19,11),(97,204,31,12),(116,213,44,11),(135,221,58,12)]:
        c=q(x,y,z)
        facet(p,[c+q(-12,0,0),c+q(-3,9,1),c+q(13,7,3),c+q(14,-3,6),c+q(0,-9,9)],
            [0,.3,1],4,BLACK,2)
        facet(p,[c+q(-8,0,4),c+q(-1,6,5),c+q(11,5,6),c+q(11,-2,9),c+q(0,-6,12)],
            [0,.3,1],2.2,DARK,2)
    return p.finish()


def build():
    saved=(prior.hindleg,prior.torso_neck,prior.wing_arm,prior.LOG)
    prior.hindleg,prior.torso_neck,prior.wing_arm,prior.LOG=hindleg,torso_neck,wing_arm,LOG
    try:cube,data,parts=prior.build()
    finally:prior.hindleg,prior.torso_neck,prior.wing_arm,prior.LOG=saved
    refs=json.loads((OUT/'参考图清单.json').read_text('utf8'))
    data.update(name='hk3gtl-w04-kurikara-independent-d2-20261110',title='俱利伽罗 · 腿爪与叠甲细化 D2',
        reference_count=refs['count'],fan_model_images=13,
        summary='重做粗壮后腿、反折关节、宽爪掌、三根长钩爪和骨白腿甲；胸腹与颈部改叠压甲片，翼腕追加分段护甲。',
        official_model_found=False,source_mesh_used=False,fan_model_url='https://www.artstation.com/artwork/n0bPo1',
        source_limits=['未确认官方龙体模型公开下载；已核对的官方雷律人物包不能当成龙模型。',
            '玩家三维作品是写实改编，仅辅助体积；未下载或使用源网格，细节以官方教学和游戏原帧为主。',
            '背部骑乘座下方、部分翼膜背纹及精确三视比例仍待核对。'],
        detail_changes=['双后腿与爪掌完整重做','胸腹及颈甲叠片细化','左右翼腕分段护甲'],
        unchanged_components=['01_长角V形面甲与龙首','03_红脊白刺与细长弯尾','05_-1_四片分体红色翼爪','05_+1_四片分体红色翼爪'])
    data['detail_views']['feet']=dict(center=[0,86,26],half=[85,78,112])
    data['detail_views']['feetfront']=data['detail_views']['feet']
    data['detail_views']['feetside']=dict(center=[49,87,20],half=[44,81,113])
    return cube,data,parts


if __name__=='__main__':
    c,d,p=build();print(json.dumps(dict(size=d['size'],blocks=d['blocks'],connectivity=d['connectivity']),ensure_ascii=False))
