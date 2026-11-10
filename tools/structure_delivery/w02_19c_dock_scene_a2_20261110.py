# -*- coding: utf-8 -*-
"""双炮对准构造核心，双掌绕腕转向核心，光束从掌心炮口发射。"""
from copy import deepcopy
import json
import numpy as np
import w02_19c_dock_scene_a1_20261110 as prior
from w02_19c_geometry_v4_20261110 import cannon,transformed
from w02_19c_dock_scene_a1_20261110 import Part,STATES,IDS,ROLES,encode,annulus,GLASS,BLUE,WHITE,BLACK

ROOT=prior.ROOT
PRIOR=prior.OUT
OUT=ROOT/'deliveries/W02_19C自律构造船坞_双炮双掌聚焦_A2_20261110'
LOG=ROOT/'logs/w02-19c-dock-focus-a2-20261110'
REFERENCE_BASE=prior.REFERENCE_BASE
VERSION='A2'
PREVIOUS_VERSION='A1'
EXPECTED_PARTS=26
CLAIM_BOUNDARY='双炮与双掌指向核心的静态候选；离线预览，不代表游戏实装测试。'
TARGET=np.array([0.,211.,68.])
CAMERA_VIEWS=deepcopy(prior.CAMERA_VIEWS)
CAMERA_VIEWS['detail_chest']=dict(label='掌心炮口与构造核心',center=[0,215,51],half=[168,68,85],direction=[-.15,.45,1.7],file='双手构造场.png')
CAMERA_VIEWS['detail_module']=dict(label='双炮聚焦核心',center=[0,268,-26],half=[123,100,136],direction=[-.8,.7,1.6],file='双炮工序.png')


def unit(v):
    v=np.asarray(v,float);return v/np.linalg.norm(v)


def rotation(a,b):
    a,b=unit(a),unit(b);v=np.cross(a,b);c=a@b
    assert c>-.999999,'当前腕部转角不能使用反向退化解'
    x,y,z=v;k=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    r=np.eye(3)+k+k@k/(1+c)
    assert np.allclose(r.T@r,np.eye(3)) and np.isclose(np.linalg.det(r),1)
    return r


def hand_focus(source,side):
    wrist=np.array([side*145.,225.,18.])
    port=np.array([side*145.,219.5,35.])
    normal=unit([0,.55,.65]);offset=port-wrist;destination=TARGET-wrist
    t=-offset@normal+np.sqrt((offset@normal)**2+destination@destination-offset@offset)
    r=rotation(offset+t*normal,destination)
    aimed=transformed(source,r,wrist-r@wrist)
    outlet=r@offset+wrist;axis=r@normal
    assert np.linalg.norm(outlet+axis*t-TARGET)<1e-8
    assert np.dot(axis,[-side,0,0])>.8,'掌心没有朝内'
    return aimed,dict(component=source.name,wrist=wrist.tolist(),port=outlet.tolist(),axis=axis.tolist(),
        target=TARGET.tolist(),rotation=r.tolist(),axis_miss=float(np.linalg.norm(np.cross(TARGET-outlet,axis))))


def ray(start,end,radius=.8):
    p=Part('检测线');p.beam(start,end,radius,GLASS);return p.finish().p


def build():
    data=json.loads((PRIOR/'manifest.json').read_text('utf8'));parts=[]
    with np.load(prior.LOG/'a1-original-components.npz') as source:
        for name in data['component_bounds_blueprint']:
            p=Part(name);p.p=source[name+'__p'].copy();p.states=source[name+'__states'].copy();parts.append(p)
    original={p.name:p for p in parts};proof=[];hands=[];guns=[]
    for i,p in enumerate(parts):
        if p.name.startswith('05_'):
            side=-1 if '_-1_' in p.name else 1
            parts[i],record=hand_focus(p,side);hands.append(record)
        if p.name.startswith('06_'):
            side=-1 if '_-1_' in p.name else 1
            origin=np.array([side*92.,346+(7 if side>0 else -2),-57.])
            parts[i]=cannon(side,target=TARGET,origin=origin);axis=unit(TARGET-origin)
            guns.append(dict(component=p.name,origin=origin.tolist(),translation_from_a1=[0,20,60],axis=axis.tolist(),
                muzzle=(origin+axis*147).tolist(),target=TARGET.tolist(),axis_miss=float(np.linalg.norm(np.cross(TARGET-origin,axis)))))
    # 取消旧的朝外靶台；同一构件改为新炮轴上的准直环及静态射线。
    guides=Part('15_双炮前方材料处理靶台')
    for record in guns:
        origin,axis=np.array(record['origin']),np.array(record['axis'])
        c=origin+axis*171
        annulus(guides,c,axis,10,8,3,BLACK);annulus(guides,c+axis*2,axis,9,8,1,WHITE)
        annulus(guides,c+axis*3,axis,8,7,1,BLUE)
        guides.beam(origin+axis*147,TARGET-axis*43,.8,GLASS)
    lines=Part('16_双掌构造线与下方扫描框')
    for record in hands:
        port,axis=np.array(record['port']),np.array(record['axis'])
        lines.beam(port+axis*1.5,TARGET-axis*42,.85,GLASS)
    for s in [-1,1]:
        lines.beam([s*55,145,17],[s*55,156,17],1.5,BLUE)
        lines.beam([s*55,156,17],[s*55,156,114],1,GLASS)
    lines.beam([-55,156,114],[55,156,114],1,GLASS)
    replacements={guides.name:guides.finish(),lines.name:lines.finish()}
    parts=[replacements.get(p.name,p) for p in parts]
    changed={p.name for p in parts if not (np.array_equal(p.p,original[p.name].p) and np.array_equal(p.states,original[p.name].states))}
    assert len(changed)==6 and len(parts)==EXPECTED_PARTS
    for p in parts:
        proof.append(dict(component=p.name,unchanged=p.name not in changed,blocks=len(p.p)))
    # 对改动构件查共享体素；掌与对应腕甲允许原有连接，其余干涉必须显式报告。
    overlaps=[];rays=[]
    for p in parts:
        if not p.name.startswith(('05_','06_')):continue
        keys=encode(p.p)
        for other in parts:
            if other.name==p.name or other.name.startswith(('15_','16_')):continue
            shared=len(np.intersect1d(keys,encode(other.p),assume_unique=True))
            if shared:overlaps.append(dict(first=p.name,second=other.name,shared_voxels=shared,
                wrist_junction=p.name.startswith('05_') and other.name.startswith('04_') and p.name[3:5]==other.name[3:5]))
    for record in guns+hands:
        start=np.array(record.get('muzzle',record.get('port')));axis=np.array(record['axis'])
        keys=encode(ray(start+axis*2,TARGET-axis*45))
        blocked=[]
        for p in parts:
            if p.name==record['component'] or p.name.startswith(('12_','15_','16_')):continue
            n=len(np.intersect1d(keys,encode(p.p),assume_unique=True))
            if n:blocked.append(dict(component=p.name,shared_voxels=n))
        rays.append(dict(component=record['component'],blocked=blocked))
    unexpected=[r for r in overlaps if not r['wrist_junction']]
    check=dict(passed=not unexpected and not any(r['blocked'] for r in rays),target=TARGET.tolist(),
        hands=hands,cannons=guns,changed_components=sorted(changed),unchanged_components=20,
        component_checks=proof,changed_component_overlaps=overlaps,unexpected_overlaps=unexpected,ray_checks=rays)
    LOG.mkdir(exist_ok=True);(LOG/'aim-and-clearance.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n','utf8')
    assert check['passed'],json.dumps(dict(overlaps=unexpected,rays=rays),ensure_ascii=False)
    points=np.concatenate([p.p for p in parts]);lo,hi=points.min(0),points.max(0);size=hi-lo+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    for p in parts:
        at=p.p-lo;cube[at[:,1],at[:,2],at[:,0]]=p.states
    data.update(name='hk3gtl-w02-19c-dock-focus-a2-20261110',title='理之律者 · 19C构造船坞 · 双炮双掌聚焦A2',
        candidate_version='W02-19C构造船坞-A2',display_version=VERSION,size=size.tolist(),blocks=int(np.count_nonzero(cube)),
        blueprint_bounds=dict(min=lo.tolist(),max=hi.tolist()),blueprint_to_export_offset_xyz=(-lo).tolist(),
        component_bounds_blueprint={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist()) for p in parts},
        base_candidate=PRIOR.relative_to(ROOT).as_posix()+'/index.html',robot_geometry_preserved=False,
        robot_components_preserved=7,unchanged_components_from_a1=20,aim_and_clearance=check,
        original_robot_component_overlaps_retained=False,
        summary='双炮向内俯射，双掌绕腕转向同一个半成品核心；四条静态构造线分别从炮轴与掌心炮口出发。躯干、背部、节链、双臂及船坞其他20构件逐格保持A1。')
    data['component_overlaps']=[r for r in data['component_overlaps'] if not r['first'].startswith(('05_','06_')) and not r['second'].startswith(('05_','06_'))]+overlaps
    data['detail_changes']=[dict(component='双炮内指',references=['负责人本轮要求'],change='保持原分叉炮型与长度；原位内转撞肩轮，因此炮座前移60格、抬高20格，炮轴交汇于(0,211,68)。'),
        dict(component='掌心朝内',references=['负责人本轮要求'],change='绕各自腕部转动完整手掌，保留长指与掌心炮；构造线从真实掌心炮口发射。'),
        dict(component='瞄准导流',references=['本轮组合设计'],change='旧朝外靶台改为核心前方准直环，双炮与双掌静态光线均止于核心外壳。'),
        dict(component='其他20构件',references=['A1'],change='躯干、背部轴系、下垂节链、双臂、轮组及其余船坞设施逐格保持A1。')]
    data['source_conflicts']=[s for s in data['source_conflicts'] if '只整体平移' not in s and '无共享体素' not in s]
    data['source_conflicts']+=['A2仅修改双炮、双掌与对应静态构造线／准直环；不是官方姿态复刻。',
        '新双炮与非对应构件无共享体素，双掌只允许与同侧腕部接合；四条轴线到核心前的净空单独核验。']
    return cube,data,parts


if __name__=='__main__':
    _,data,_=build();print(json.dumps(dict(size=data['size'],blocks=data['blocks'],check=LOG.as_posix()),ensure_ascii=False))
