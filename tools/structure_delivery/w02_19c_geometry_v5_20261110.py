# -*- coding: utf-8 -*-
"""只恢复V3主躯干；其他十个构件逐格保持V4。"""
from copy import deepcopy
import numpy as np
import w02_19c_geometry_v4_20261110 as b
from w02_19c_geometry_v4_20261110 import ROOT,STATES,IDS,ROLES,encode

OUT=ROOT/'deliveries/W02_理之律者19C_恢复原躯干_V5_20261110'
LOG=ROOT/'logs/w02-19c-torso-restore-v5-20261110'
PRIOR=b.OUT
REFERENCE_BASE=b.REFERENCE_BASE
VERSION='V5'
PREVIOUS_VERSION='V4'
PRESENTATION_TITLE='恢复原躯干V5'
CAMERA_VIEWS=deepcopy(b.CAMERA_VIEWS)
CAMERA_VIEWS['detail_chest']=dict(label='恢复的V3躯干',center=[0,220,15],half=[54,80,45],direction=[-.5,.25,1.6],file='胸甲细节.png')


def build():
    _,prior,parts=b.build()
    parts[0]=b.b.torso()
    restored=parts[0]
    proof=[]
    with np.load(b.LOG/'v4-original-components.npz') as v4,np.load(b.b.LOG/'v3-original-components.npz') as v3:
        assert np.array_equal(restored.p,v3[restored.name+'__p'])
        assert np.array_equal(restored.states,v3[restored.name+'__states'])
        for part in parts:
            previous,states=v4[part.name+'__p'],v4[part.name+'__states']
            same=np.array_equal(part.p,previous) and np.array_equal(part.states,states)
            assert same==(part is not restored),'恢复躯干以外的构件发生变化'
            proof.append(dict(component=part.name,unchanged_from_v4=same,blocks=len(part.p),
                position_difference=len(np.setxor1d(encode(part.p),encode(previous)))))
    points=np.concatenate([p.p for p in parts]);low,high=points.min(0),points.max(0);size=high-low+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8);overlaps=[]
    for part in parts:
        at=part.p-low;cube[at[:,1],at[:,2],at[:,0]]=part.states
    for i,a in enumerate(parts):
        for c in parts[i+1:]:
            shared=len(np.intersect1d(encode(a.p),encode(c.p),assume_unique=True))
            if shared:overlaps.append(dict(first=a.name,second=c.name,shared_voxels=shared,
                classification='接合或待审干涉，不宣称全部无穿模'))
    assert not any(r['first'].startswith('06_') or r['second'].startswith('06_') for r in overlaps),'恢复后炮舱与其他构件干涉'
    data=deepcopy(prior);data.pop('geometry_delta_vs_v3',None)
    data.update(name='hk3gtl-w02-19c-torso-restore-v5-20261110',title='理之律者 · 重装小兔19C · 恢复原躯干V5',
        candidate_version='19C-V5恢复原躯干',display_version=VERSION,size=size.tolist(),blocks=int(np.count_nonzero(cube)),
        blueprint_to_export_offset_xyz=(-low).tolist(),blueprint_bounds=dict(min=low.tolist(),max=high.tolist()),
        component_bounds_blueprint={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist()) for p in parts},
        component_overlaps=overlaps,geometry_delta_vs_v4=proof,
        torso_restored_from_v3=True,other_components_unchanged_from_v4=10,
        base_candidate=PRIOR.relative_to(ROOT).as_posix()+'/index.html',center_blueprint=[0,220,15],
        summary='仅主躯干恢复为V3原来的轮廓、比例、橙色罩体与白蓝装甲；V4的背甲、轮组、曲臂、前爪、双炮和尾链共十个构件，坐标与材质逐格保留。')
    data['detail_changes']=[dict(component='主躯干恢复',references=['R01','R04','R10','R31'],
        change='恢复V3主躯干原始坐标与全部材质，不保留V4前倾压缩及额外下颌。'),
        dict(component='V4其余构件保留',references=['R05','R12','R25','R28','R32'],
        change='背甲、轮组、三段锐角臂甲、前爪、分叉双炮及后摆节链，共十个构件逐格保持V4。')]
    data['source_conflicts'][2]='V5按负责人要求仅恢复V3躯干，其余十个构件保持V4；屈臂、前爪及双炮错角仍是参考转译，不宣称官方精确待机或逐处复刻。'
    data['reference_correspondence'][0]['status']='主躯干逐格恢复V3原来的尖盾轮廓、橙色罩体与装甲细节'
    return cube,data,parts
