# -*- coding: utf-8 -*-
"""恢复V3背部与节链，其余九个构件保持V5。"""
from copy import deepcopy
import numpy as np
import w02_19c_geometry_v5_20261110 as b
import w02_19c_geometry_v3_20261110 as original
from w02_19c_geometry_v5_20261110 import ROOT,STATES,IDS,ROLES,encode

OUT=ROOT/'deliveries/W02_理之律者19C_恢复原背部节链_V6_20261110'
LOG=ROOT/'logs/w02-19c-back-chain-restore-v6-20261110'
PRIOR=b.OUT
REFERENCE_BASE=b.REFERENCE_BASE
VERSION='V6'
PREVIOUS_VERSION='V5'
PRESENTATION_TITLE='恢复原背部节链V6'
POSE_NOTE='主躯干、背部轴系与节链恢复V3；轮组、双臂、机械手与双炮保持V4，不宣称官方精确待机或逐处复刻。'
CAMERA_VIEWS=deepcopy(b.CAMERA_VIEWS)
CAMERA_VIEWS['detail_back']=dict(label='恢复的背部与下垂节链',center=[0,145,-38],half=[60,140,44],direction=[.6,.2,-1.5],file='背部细节.png')


def build():
    _,prior,parts=b.build()
    parts[1],parts[-1]=original.back(),original.chain()
    changed={parts[1].name,parts[-1].name};restored={parts[0].name,*changed};proof=[]
    with np.load(b.LOG/'v5-original-components.npz') as v5,np.load(original.LOG/'v3-original-components.npz') as v3:
        for part in parts:
            if part.name in restored:
                assert np.array_equal(part.p,v3[part.name+'__p']) and np.array_equal(part.states,v3[part.name+'__states'])
            previous,states=v5[part.name+'__p'],v5[part.name+'__states']
            same=np.array_equal(part.p,previous) and np.array_equal(part.states,states)
            assert same==(part.name not in changed),'指定两处以外的构件发生变化'
            proof.append(dict(component=part.name,unchanged_from_v5=same,blocks=len(part.p),
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
    data=deepcopy(prior)
    for key in ['geometry_delta_vs_v4','other_components_unchanged_from_v4']:data.pop(key,None)
    data.update(name='hk3gtl-w02-19c-back-chain-restore-v6-20261110',title='理之律者 · 重装小兔19C · 恢复原背部节链V6',
        candidate_version='19C-V6恢复原背部节链',display_version=VERSION,size=size.tolist(),blocks=int(np.count_nonzero(cube)),
        blueprint_to_export_offset_xyz=(-low).tolist(),blueprint_bounds=dict(min=low.tolist(),max=high.tolist()),
        component_bounds_blueprint={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist()) for p in parts},
        component_overlaps=overlaps,geometry_delta_vs_v5=proof,restored_components_from_v3=sorted(restored),
        other_components_unchanged_from_v5=9,base_candidate=PRIOR.relative_to(ROOT).as_posix()+'/index.html',
        summary='背部轴系与散热脊柱、背下方弯曲节链逐格恢复V3；主躯干继续保持已恢复的V3状态，轮组、曲臂、机械手和双炮的位置及材质保持V5。')
    data['detail_changes']=[dict(component='背部轴系与散热脊柱',references=['R25','R27','R28','R59'],change='逐格恢复V3背部原始轴系、侧甲与散热脊柱。'),
        dict(component='背下方弯曲节链',references=['R25','R27','R59'],change='逐格恢复V3向下延伸的原节链，取消V4／V5向后的摆放。'),
        dict(component='其余九个构件',references=['R01','R04','R12','R32'],change='与V5逐格一致；主躯干保持V3，轮组、曲臂、机械手和双炮保留V4造型。')]
    data['source_conflicts'][2]=POSE_NOTE
    data['reference_correspondence'][3]['status']='背部轴系与节链逐格恢复V3；官方为主、二创补遮挡，未验收逐处复刻'
    return cube,data,parts
