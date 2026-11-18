# -*- coding: utf-8 -*-
"""鸣雷见独立静态小样：参考侧廓校准，刃厚、刀镡和握柄分别构造。"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, label, generate_binary_structure
from w02_19c_geometry_v4_20261110 import SolidPart
from w02_19c_study_20261110 import hull

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W04_涤罪七雷鸣雷见_独立小样_S1_20261110'
LOG=ROOT/'logs/w04-narukami-study-20261110'
PRIOR=ROOT/'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110'
SCALE=1.25
BLACK,GRAY,PURPLE,MAGENTA,PINK,WHITE,SILVER,RED,GLASS,LIGHT=[
    'minecraft:'+s for s in ['black_concrete','gray_concrete','purple_concrete','magenta_concrete',
    'pink_concrete','white_concrete','light_gray_concrete','red_concrete','magenta_stained_glass','sea_lantern']]
STATES=[BLACK,GRAY,PURPLE,MAGENTA,PINK,WHITE,SILVER,RED,GLASS,LIGHT]
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES=dict(zip(STATES,['刀背、根部镂空内衬和黑色握柄','深色金属切面','紫色实体刃面与刀镡',
    '紫红刃口','窄亮刃与晶体表层','骨白镶片与白色缠带','银灰纹样','上刃根红色分片与柄侧饰条',
    '柄尾与刃根紫晶外壳','紫晶内的少量静态光芯']))
PROTOTYPES=np.array([[36,23,43],[99,79,103],[101,34,143],[183,47,202],
    [240,140,236],[235,225,227],[175,153,170],[155,29,63]],float)


class Part(SolidPart):
    def points(self,points,state):
        a=np.rint(points).astype(np.int32).reshape(-1,3)
        if len(a):
            assert np.all(abs(a)<2048),'只报错，不裁切'
            self.chunks.append(a);self.values.append(np.full(len(a),IDS[state],np.uint8))


def world(x,y,z=0):
    return np.array([x*SCALE,(86-y)*SCALE,z],float)


def image_data():
    source=np.asarray(Image.open(OUT/'轮廓取样源.png').convert('RGBA'))
    mask=source[:,:,3]>=240
    components,n=label(mask);counts=np.bincount(components.ravel());counts[0]=0
    main=components==np.argmax(counts)
    removed=int(np.count_nonzero(mask & ~main))
    rgb=source[:,:,:3].astype(float)
    colors=np.argmin(((rgb[:,:,None,:]-PROTOTYPES)**2).sum(3),2).astype(np.uint8)+1
    return source,main,colors,removed


def profiled_part(name,zone,mask,colors,max_thickness):
    p=Part(name);distance=distance_transform_edt(mask)
    yy,xx=np.mgrid[0:round(86*SCALE),0:round(mask.shape[1]*SCALE)]
    sx=np.minimum(np.floor(xx/SCALE).astype(int),mask.shape[1]-1)
    sy=np.minimum(np.floor(yy/SCALE).astype(int),mask.shape[0]-1)
    valid=mask[sy,sx] & zone(sx,sy)
    x,y=xx[valid],yy[valid];ix,iy=sx[valid],sy[valid]
    mid=colors[iy,ix].copy()
    half=(.65+np.minimum(max_thickness,distance[iy,ix]*.68))*SCALE
    half+=np.where(np.isin(mid,[IDS[WHITE],IDS[SILVER]])&(ix<280),1.5,0)
    half=np.maximum(1,np.rint(half)).astype(int)
    # 无强光展示图中的红色上叉与转台中的紫色光层分开处理。
    upper=(ix>300)&(ix<394)&(iy<40-.025*(ix-300))
    mid[upper & np.isin(mid,[3,4,5,6,7])]=IDS[RED]
    for z in range(-int(half.max()),int(half.max())+1):
        keep=abs(z)<=half
        surface=(half-abs(z)<=1)
        ids=np.where(surface,mid,IDS[BLACK])
        # 刃背与刃口都收薄，白色镶片仅位于双侧装甲表面。
        for value in np.unique(ids[keep]):
            m=keep & (ids==value)
            p.points(np.c_[x[m],round(86*SCALE)-1-y[m],np.full(m.sum(),z)],STATES[int(value)-1])
    return p.finish()


def guard():
    p=Part('03_小型环状刀镡与颈座')
    c=np.rint(world(419,44));rx,ry,rz=4.5,22,19
    xx,yy,zz=np.mgrid[-5:6,-23:24,-20:21]
    radius=(yy/ry)**2+(zz/rz)**2
    keep=(abs(xx)<=rx)&(radius<=1)&((radius>=.49)|(abs(zz)<=2)|(abs(yy)<=2))
    edge=(radius>.83)|(abs(xx)>=3)
    for m,state in [(keep&~edge,PURPLE),(keep&edge,MAGENTA)]:
        p.points(np.c_[xx[m]+c[0],yy[m]+c[1],zz[m]],state)
    p.beam(world(410,46),world(433,43),6,BLACK)
    for sign in [-1,1]:
        p.beam(c+[3,-14,sign*10],c+[3,14,sign*10],1,SILVER)
    return p.finish()


def grip(source,colors):
    p=Part('04_黑色握柄与绕柄白缠带')
    for x in range(round(426*SCALE),round(538*SCALE)+1):
        sx=x/SCALE;cy=float(np.interp(sx,[426,470,504,538],[43,40,34,28]))
        radius=6.3 if sx<490 else 5.6
        yy,zz=np.mgrid[-9:10,-8:9];ellipse=(yy/(radius*SCALE))**2+(zz/(radius*.82*SCALE))**2
        keep=ellipse<=1;inner=ellipse<.6
        ids=np.full(keep.shape,IDS[BLACK],np.uint8)
        angle=np.arctan2(yy,zz)
        if 491<sx<526:
            phase=(sx-491)/8.6+angle/(2*np.pi)
            ids[((phase%1)<.33)&~inner]=IDS[WHITE]
        if 435<sx<473:
            # 参考中的银白斑纹和柄下红弧，沿曲面包覆；背侧细纹仍为转译。
            sy=np.clip(np.rint(cy-yy/SCALE).astype(int),0,85)
            ix=min(round(sx),source.shape[1]-1)
            marks=np.isin(colors[sy,ix],[IDS[WHITE],IDS[SILVER]])
            ids[marks&~inner]=IDS[SILVER]
            red_edge=-radius*SCALE*(.38+.21*np.sin((sx-435)/38*np.pi))
            ids[(yy<red_edge)&~inner]=IDS[RED]
        if sx<435 or sx>530:ids[~inner]=IDS[GRAY]
        for value in np.unique(ids[keep]):
            m=keep&(ids==value);p.points(np.c_[np.full(m.sum(),x),yy[m]+world(0,cy)[1],zz[m]],STATES[int(value)-1])
    return p.finish()


def crystal(p,center,length,height,depth):
    c=np.array(center,float)
    points=[c+[length,0,0],c+[-length,0,0],c+[0,height,0],c+[0,-height,0],c+[0,0,depth],c+[0,0,-depth]]
    hull(p,points,GLASS)
    hull(p,[c+[length*.43,0,0],c+[-length*.43,0,0],c+[0,height*.45,0],c+[0,-height*.45,0],
        c+[0,0,depth*.48],c+[0,0,-depth*.48]],LIGHT)


def build():
    source,mask,colors,removed=image_data()
    parts=[profiled_part('01_弧形主刃与骨白镶片',lambda x,y:x<300,mask,colors,5.3),
        profiled_part('02_不对称镂空刃根',lambda x,y:(x>=300)&((x<413)|(y>=60))&(x<446),mask,colors,7.5),
        guard(),grip(source,colors)]
    tail=profiled_part('05_尖叶柄尾与紫晶',lambda x,y:x>=534,mask,colors,4.8)
    q=Part(tail.name)
    for value in np.unique(tail.states):q.points(tail.p[tail.states==value],STATES[int(value)-1])
    crystal(q,world(551,27),10,5,7)
    parts.append(q.finish())
    # 刃根能量结单列为光学嵌件，不填平周边透空孔。
    root=parts[1];q=Part(root.name)
    for value in np.unique(root.states):q.points(root.p[root.states==value],STATES[int(value)-1])
    crystal(q,world(375,45),13,6,16)
    parts[1]=q.finish()
    low=np.min([p.p.min(0) for p in parts],axis=0);high=np.max([p.p.max(0) for p in parts],axis=0)
    size=high-low+1;cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    for p in parts:
        a=p.p-low;cube[a[:,1],a[:,2],a[:,0]]=p.states
    counts=np.bincount(cube.ravel(),minlength=len(STATES)+1);assert np.all(counts[1:]>0)
    joined,n=label(cube>0,generate_binary_structure(3,1));sizes=np.bincount(joined.ravel())[1:]
    # 对主刃与刃根的连续轮廓逐个采样；接合处刀镡可超出原侧廓。
    holes=[]
    for x,y in [(339,38),(352,52),(387,51),(382,56)]:
        point=np.rint(world(x,y)).astype(int)-low
        assert cube[point[1],:,point[0]].sum()==0,(x,y,'参考中的刃根开孔被填平')
        holes.append([x,y])
    data=dict(name='hk3gtl-w04-narukami-independent-s1-20261110',title='涤罪七雷·鸣雷见 · 独立静态小样 S1',
        size=size.tolist(),blocks=int(counts[1:].sum()),blueprint_to_export_offset_xyz=(-low).tolist(),
        bounds_blueprint=dict(min=low.tolist(),max=high.tolist()),scale=SCALE,reference_count=48,ports=[],
        summary='48张分源参考校准；仅制作超限鸣雷见。侧廓来自透明展示图，双侧刃面有楔形厚度，环形刀镡与圆截面握柄独立构造。',
        center_blueprint=world(295,43).tolist(),
        detail_views={name:dict(center=world(x,y).tolist(),half=half) for name,x,y,half in [
            ('root',365,48,[104,53,35]),('guard',420,43,[50,40,35]),('guardend',419,44,[28,28,28]),('grip',496,33,[110,39,30]),
            ('tip',100,27,[134,49,28]),('pommel',558,27,[47,28,27])]},
        source_limits=['没有官方三视尺寸图；精确厚度与遮挡背纹属于转台约束下的转译。',
            '背面细纹复用了已见侧面的母纹，未宣称逐处复刻。','独立细节比例；尚未安放到W04，不等于整机候选获批准。'],
        construction=dict(profile_source='轮廓取样源.png',source_resolution=[545,320],aligned_resolution=[590,86],
            image_opaque_threshold=240,removed_antialias_islands=removed,variable_blade_thickness=True,
            ring_guard_3d=True,elliptical_grip=True,wrapped_grip_bands=True,root_openings=holes),
        connectivity=dict(six_neighbor_components=int(n),component_sizes=sorted(sizes.tolist(),reverse=True)),
        static=True,animation_enabled=False,approved=False,game_verified=False)
    return cube,data,parts


if __name__=='__main__':
    cube,data,parts=build();print(json.dumps({k:data[k] for k in ['size','blocks','connectivity']},ensure_ascii=False))
