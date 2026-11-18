# -*- coding: utf-8 -*-
"""组合独立俱利伽罗静态小样；完整生成后计算实际边界。"""
import json
import numpy as np
from scipy.ndimage import label,generate_binary_structure,find_objects
from w04_kurikara_d1_parts_20261110 import *
from w04_kurikara_d1_head_wings_20261110 import head,wing_arm,wing_blades
from w04_kurikara_d1_body_20261110 import torso_neck,hindleg,tail

PRIOR=ROOT/'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110'
SWORD=ROOT/'deliveries/W04_涤罪七雷鸣雷见_独立小样_S1_20261110'


def build():
    tail_part,length=tail()
    parts=[tail_part]
    for builder in [head,torso_neck,lambda:wing_arm(-1),lambda:wing_arm(1),lambda:wing_blades(-1),lambda:wing_blades(1),lambda:hindleg(-1),lambda:hindleg(1)]:
        part=builder();parts.append(part);print(part.name,len(part.p),flush=True)
    parts.sort(key=lambda p:p.name)
    low=np.min([p.p.min(0) for p in parts],axis=0);high=np.max([p.p.max(0) for p in parts],axis=0);size=high-low+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    owner=np.zeros_like(cube)
    for i,p in enumerate(parts,1):
        at=p.p-low;cube[at[:,1],at[:,2],at[:,0]]=p.states;owner[at[:,1],at[:,2],at[:,0]]=i
    assert all(np.count_nonzero(cube==i+1)>0 for i in range(len(STATES)))
    connected,n=label(cube>0,generate_binary_structure(3,1));counts=np.bincount(connected.ravel());counts[0]=0
    original_regions=int(n);stitched=[]
    # 薄甲角点体素会仅以棱角相接；保留原点并补最短面接，不删除边缘。
    largest=int(counts.argmax());extra={i:[] for i in range(len(parts))}
    for i,box in enumerate(find_objects(connected),1):
        if box is None or i==largest:continue
        assert counts[i]<=4,('出现整块悬空构件，不能用角点补接掩盖',int(counts[i]),[(s.start,s.stop) for s in box],low.tolist())
        origin=np.array([s.start for s in box]);points=np.argwhere(connected[box]==i)+origin;options=[]
        for at in points:
            lo=np.maximum(at-1,0);hi=np.minimum(at+2,cube.shape)
            candidates=np.argwhere(connected[tuple(slice(a,b) for a,b in zip(lo,hi))]==largest)+lo
            options.extend((int(np.abs(c-at).sum()),at,c) for c in candidates)
        assert options,'孤点不是贴邻角接，需检查原几何'
        _,at,target=min(options,key=lambda item:item[0])
        value=int(cube[tuple(at)]);part_id=int(owner[tuple(at)])-1
        current=at.copy()
        for axis in np.flatnonzero(target!=current):
            current[axis]=target[axis]
            if cube[tuple(current)]==0:
                cube[tuple(current)]=value;owner[tuple(current)]=part_id+1
                point=np.array([current[2],current[0],current[1]])+low
                extra[part_id].append((point,value));stitched.append(point.tolist())
    for i,items in extra.items():
        if not items:continue
        p=parts[i];new=Part(p.name)
        for value in np.unique(p.states):new.points(p.p[p.states==value],STATES[int(value)-1])
        for point,value in items:new.points([point],STATES[value-1])
        parts[i]=new.finish()
    connected,n=label(cube>0,generate_binary_structure(3,1));counts=np.bincount(connected.ravel());counts[0]=0
    regions=[]
    for i,box in enumerate(find_objects(connected),1):
        if box is None:continue
        y,z,x=box;regions.append(dict(blocks=int(counts[i]),min=(np.array([x.start,y.start,z.start])+low).tolist(),
            max=(np.array([x.stop-1,y.stop-1,z.stop-1])+low).tolist()))
    data=dict(name='hk3gtl-w04-kurikara-independent-d1-20261110',title='俱利伽罗 · 独立静态小样 D1',
        size=size.tolist(),blocks=int(np.count_nonzero(cube)),bounds_blueprint=dict(min=low.tolist(),max=high.tolist()),
        blueprint_to_export_offset_xyz=(-low).tolist(),center_blueprint=[0,195,-45],ports=[],
        reference_count=43,official_frames=34,player_frames=8,community_stills=1,tail_centerline_length=length,
        summary='依据43张分源参考制作龙本体：长白角与红色V形面甲、短躯弯颈、暗色分节颈腹、双侧刃状翼前肢、收拢后足及红脊白刺细尾。独立静态，不带整机场景。',
        anatomy=dict(wing_forelimbs=2,hindlegs=2,extra_grasping_forelimbs=0,wing_blades_per_side=4),
        detail_views={name:dict(center=center,half=half) for name,center,half in [
            ('head',[0,308,161],[63,100,71]),('headfront',[0,308,161],[63,100,71]),
            ('headside',[0,308,161],[63,100,71]),('chest',[0,205,41],[76,96,103]),
            ('wing',[211,268,12],[129,103,113]),('wingback',[-211,268,12],[129,103,113]),
            ('feet',[0,84,15],[63,67,91]),('tail',[20,103,-219],[76,65,165])]},
        connectivity=dict(six_neighbor_components=int(n),regions=sorted(regions,key=lambda r:-r['blocks']),
            original_components=original_regions,corner_contact_stitches=stitched,removed_voxels=0),
        static=True,animation_enabled=False,approved=False,game_verified=False,
        source_limits=['无官方三视尺寸图，具体比例为多角度轮廓转译。',
            '飞行和伏低画面用于同一常态模型交叉核对，最终采用翼刃半展开的悬停姿态。',
            '背部骑乘座下方与部分翼膜背纹被遮挡，只保留简化连接。',
            '不使用B2盘环长躯、额外扣环前爪、吐息光束、骑乘者或工业连接。'])
    LOG.mkdir(exist_ok=True)
    return cube,data,parts


if __name__=='__main__':
    c,d,p=build();print(json.dumps(dict(size=d['size'],blocks=d['blocks'],regions=d['connectivity']['six_neighbor_components'],largest=d['connectivity']['regions'][:12]),ensure_ascii=False))
