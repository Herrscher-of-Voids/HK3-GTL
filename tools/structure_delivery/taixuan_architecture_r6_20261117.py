import numpy as np

import taixuan_architecture_r2_20261116 as original
from taixuan_common_20261116 import Part, model, WOOD, FRAME, ROOF, TILE, WHITE, PAVING, BROWN


def _gallery():
    p=Part('gallery','西侧曲檐回廊',inference='按负责人标注将西后折廊重建为四分之一圆弧；廊宽、格窗与材质沿用既有木构长廊。')
    original._gallery_span(p,(-108,-16),100,2)
    for i,(points,states) in enumerate(zip(p.chunks,p.values)):
        keep=~((points[:,2]<-49)&(points[:,1]>=182)&((states==ROOF)|(states==FRAME)))
        p.chunks[i],p.values[i]=points[keep],states[keep]

    cx,cz,radius=-66,-66,42
    z,x=np.mgrid[-125:-65,-125:-65]
    distance=np.hypot(x-cx,z-cz)
    angle=np.mod(np.arctan2(z-cz,x-cx),2*np.pi)
    floor=(distance>=radius-14)&(distance<=radius+14)
    for y in range(160,168):
        p.points(np.c_[x[floor],np.full(floor.sum(),y),z[floor]],TILE if y<166 else PAVING)
    outer=abs(distance-(radius+12))<=.8
    frieze=abs(distance-(radius+12))<=1.5
    for y in range(168,175):
        p.points(np.c_[x[outer],np.full(outer.sum(),y),z[outer]],WHITE)
    for y in (175,176):
        p.points(np.c_[x[frieze],np.full(frieze.sum(),y),z[frieze]],FRAME)

    roof=abs(distance-radius)<=17
    height=np.rint(184+11*np.maximum(0,1-abs(distance-radius)/17)**1.5).astype(int)
    for depth in (0,-1):
        p.points(np.c_[x[roof],height[roof]+depth,z[roof]],ROOF)
    ribs=roof&(np.rint((angle-np.pi)*radius).astype(int)%10==0)
    p.points(np.c_[x[ribs],height[ribs]+1,z[ribs]],ROOF)
    rim=roof&(abs(abs(distance-radius)-17)<1)
    p.points(np.c_[x[rim],np.full(rim.sum(),182),z[rim]],FRAME)

    z,x=np.mgrid[-66:-48,-125:-90]
    height=np.rint(184+11*np.maximum(0,1-abs(x+108)/17)**1.5).astype(int)
    for depth in (0,-1):
        p.points(np.c_[x.ravel(),(height+depth).ravel(),z.ravel()],ROOF)
    ribs=z%10==0
    p.points(np.c_[x[ribs],height[ribs]+1,z[ribs]],ROOF)
    rim=abs(x+108)>=16
    p.points(np.c_[x[rim],np.full(rim.sum(),182),z[rim]],FRAME)

    for theta in np.linspace(np.pi,np.pi*1.5,7)[:-1]:
        for offset in (-11,11):
            xx,zz=np.rint([cx+(radius+offset)*np.cos(theta),cz+(radius+offset)*np.sin(theta)]).astype(int)
            p.box((xx-1,168,zz-1),(xx+1,184,zz+1),BROWN)
            p.box((xx-3,181,zz-3),(xx+3,183,zz+3),WOOD)
    for theta in np.linspace(np.pi,np.pi*1.5,7)[:-1]+np.pi/24:
        window=Part('window','曲廊格窗')
        original._window(window,(0,0),(1,0),bottom=168,width=9,height=15)
        for points,states in zip(window.chunks,window.values):
            a=theta+points[:,0]/(radius+12)
            mapped=np.c_[cx+(radius+12)*np.cos(a),points[:,1],cz+(radius+12)*np.sin(a)]
            p.chunks.append(np.rint(mapped).astype(np.int32))
            p.values.append(states)

    p.box((-66,160,-122),(-64,165,-94),TILE)
    p.box((-66,166,-122),(-64,167,-94),PAVING)
    z,x=np.mgrid[-125:-90,-66:-64]
    height=np.rint(184+11*np.maximum(0,1-abs(z+108)/17)**1.5).astype(int)
    for depth in (0,-1):
        p.points(np.c_[x.ravel(),(height+depth).ravel(),z.ravel()],ROOF)
    rim=abs(z+108)>=16
    p.points(np.c_[x[rim],np.full(rim.sum(),182),z[rim]],FRAME)
    return model(p,['西廊保持原位置与廊宽，西后转角采用半径42格的连续四分之一圆弧。',
        '弧廊铺地、双侧立柱、外墙格窗与青灰曲檐逐格连续。',
        '弧廊由(-108,-66)接入西廊，在(-66,-108)转为向东短廊，接入主殿西后侧。'],
        ['G14','O08','O10','R2G05'],
        {'gallery':dict(label='西侧格扇长廊',center=[-108,177,-20],half=[22,25,60],direction=[1,.3,.8]),
         'connection':dict(label='西后弧形回廊',center=[-94,178,-94],half=[36,25,36],direction=[-1,.7,.8]),
         'curve_top':dict(label='弧廊逐格俯视',center=[-94,183,-94],half=[36,24,36],direction=[0,1,0])})


def build():
    return [original._temple(),_gallery(),original._censer(),original._lanterns()]
