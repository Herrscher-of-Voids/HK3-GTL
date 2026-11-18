# -*- coding: utf-8 -*-
"""扩充胸腹、肩背并向头颈平滑过渡，完整保留D3双翼和厚尾。"""
import json
import numpy as np
from scipy.ndimage import map_coordinates,distance_transform_edt
import w04_kurikara_d1_20261110 as base
import w04_kurikara_d2_20261110 as d2
import w04_kurikara_d3_20261110 as d3
from w04_kurikara_d1_parts_20261110 import *

PRIOR=d3.OUT
OUT=ROOT/'deliveries/W04_俱利伽罗_厚躯与肩背_D4_20261110'
LOG=ROOT/'logs/w04-kurikara-d4-20261110'
SWORD=d3.SWORD


def dimensions(y):
    t=np.clip((np.asarray(y)-207)/56,0,1)
    weight=1-t*t*(3-2*t)
    center=np.interp(y,[100,116,148,179,201,216,242,261,290],[-76,-69,-50,-20,13,48,91,129,150])
    return 1+.45*weight,1+.35*weight,center,weight


def map_body(points):
    points=np.asarray(points,float);result=points.copy()
    sx,sz,center,weight=dimensions(points[:,1])
    result[:,0]*=sx
    result[:,1]+=(points[:,1]-176)*.22*weight
    result[:,2]=center+(points[:,2]-center)*sz
    return result


def torso_neck():
    source=d2.torso_neck();mapped=map_body(source.p)
    low=source.p.min(0)-2;high=source.p.max(0)+2;size=high-low+1
    dense=np.zeros(tuple(size),np.uint8);dense[tuple((source.p-low).T)]=source.states
    occupied=(dense>0).astype(np.float32)
    nearest=distance_transform_edt(dense==0,return_distances=False,return_indices=True)
    nearest_material=dense[tuple(nearest)]
    lo=np.floor(mapped.min(0)-2).astype(int);hi=np.ceil(mapped.max(0)+2).astype(int)
    stations=np.linspace(low[1],high[1],4097)
    sample=np.c_[np.zeros(len(stations)),stations,np.zeros(len(stations))]
    mapped_y=map_body(sample)[:,1];assert np.all(np.diff(mapped_y)>0),'躯干映射必须单调，不能折叠'
    zz,xx=np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1]
    p=Part('02_加厚胸腹肩背与过渡颈甲')
    for y in range(lo[1],hi[1]+1):
        source_y=float(np.interp(y,mapped_y,stations));sx,sz,center,_=dimensions(source_y)
        original=np.c_[xx.ravel()/sx,np.full(xx.size,source_y),center+(zz.ravel()-center)/sz]-low
        keep=map_coordinates(occupied,original.T,order=1,mode='constant',cval=0,prefilter=False)>.22
        values=map_coordinates(nearest_material,original[keep].T,order=0,mode='nearest',prefilter=False)
        world=np.c_[xx.ravel(),np.full(xx.size,y),zz.ravel()][keep]
        for value in np.unique(values):p.points(world[values==value],STATES[int(value)-1])
    # 逐个保留源体素映射中心，薄甲细节不能因重采样被静默丢弃。
    for value in np.unique(source.states):p.points(mapped[source.states==value],STATES[int(value)-1])
    return p.finish()


def build():
    overrides=dict(hindleg=d2.hindleg,torso_neck=torso_neck,wing_arm=d3.wing_arm,
        wing_blades=d3.wing_blades,tail=d3.tail,LOG=LOG)
    saved={key:getattr(base,key) for key in overrides}
    for key,value in overrides.items():setattr(base,key,value)
    try:cube,data,parts=base.build()
    finally:
        for key,value in saved.items():setattr(base,key,value)
    old=json.loads((PRIOR/'manifest.json').read_text('utf8'))
    for key in ['reference_count','fan_model_images','official_model_found','source_mesh_used','fan_model_url','source_limits']:
        data[key]=old[key]
    data.update(name='hk3gtl-w04-kurikara-independent-d4-20261110',title='俱利伽罗 · 厚躯与肩背 D4',
        summary='加宽胸腹与肩背，增加腹部纵深；向头颈平滑收束，头部、双翼、厚尾与双腿爪保持D3。',
        detail_changes=['胸腹与肩背加厚，颈根平滑过渡'],
        unchanged_components=[name for name in old['component_bounds_blueprint'] if not name.startswith('02_')],
        proportion_revision=dict(official_exact_dimensions=False,only_torso_changed=True,
            torso_max_width_scale=1.45,torso_max_depth_scale=1.35,lower_torso_height_scale=1.22,
            head_attachment_anchored_above_y=263,source_voxel_centers_preserved=True))
    data['detail_views'].update(old['detail_views'])
    data['detail_views']['chest']=dict(center=[0,199,28],half=[105,107,134])
    return cube,data,parts


if __name__=='__main__':
    c,d,p=build();print(json.dumps(dict(size=d['size'],blocks=d['blocks'],connected=d['connectivity']['six_neighbor_components'])))
