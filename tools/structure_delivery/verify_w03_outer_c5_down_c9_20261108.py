# -*- coding: utf-8 -*-
"""C9连续净空：用包围所有旋转方块的壳层、圆柱和球证明全周期分离。"""
import gzip
import itertools
import json
import shutil
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from build_w03_outer_c5_down_c9_20261108 import ROOT, OUT, LOG, BASE, CORE, unpack, load, save, sha
from i34_open_observatory_export_20261027 import _headers, exact


def main():
    manifest=load(OUT/'manifest.json'); base=load(BASE/'manifest.json')
    payload=unpack(OUT/'w03/data.js'); config=unpack(OUT/'w03/motion-data.js')
    oldconfig=unpack(BASE/'w03/motion-data.js')
    parts=np.load(LOG/'moving-parts.npz',allow_pickle=False)
    components={c['id']:c for c in config['components']}
    corner=float(np.sqrt(3))  # 方块几何位于p+[0,1]^3；这个半径保守包住所有角点。
    w,h,d=manifest['size']; offset=np.array(manifest['blueprint_to_export_offset_xyz'])
    with gzip.open(OUT/'w03'/f"{manifest['name']}.schem",'rb') as f:
        header=_headers(payload['palette'],(h,d,w),manifest['blocks'])[1]
        assert exact(f,len(header))==header
        cube=np.frombuffer(exact(f,w*h*d),np.uint8).copy().reshape(h,d,w)
        assert exact(f,1)==b'\x00' and not f.read(1)
    assert int(np.count_nonzero(cube))==base['blocks']==manifest['blocks']
    shells={}; crystals={}; annuli={}; world={}
    for name in parts.files:
        p=parts[name].astype(float)+components[name]['render_translation_xyz']
        world[name]=p
        relative=p-CORE
        radial=np.linalg.norm(relative,axis=1)
        shells[name]=(float(radial.min()),float(radial.max()))
        if name.startswith('crystal:'):
            center=np.array(components[name]['pivot_blueprint'])
            crystals[name]=(center,float(np.linalg.norm(p-center,axis=1).max())+corner)
        if name in ['ring:210','outer_stars']:
            r=np.linalg.norm(relative[:,:2],axis=1)
            annuli[name]=(float(r.min()),float(r.max()),float(np.abs(relative[:,2]).max()))
        at=parts[name]+offset
        assert np.all(cube[at[:,1],at[:,2],at[:,0]]>0)
        cube[at[:,1],at[:,2],at[:,0]]=0

    records=[]
    def record(a,b,gap,method):
        assert gap>0,('连续包络不能证明净空',a,b,gap)
        records.append(dict(a=a,b=b,minimum_surface_gap_lower_bound=float(gap),method=method))

    rigid=[n for n in parts.files if not n.startswith('crystal:')]
    for a,b in itertools.combinations(rigid,2):
        ar,br=shells[a],shells[b]
        record(a,b,max(ar[0]-br[1],br[0]-ar[1])-2*corner,'以共同核心为球心的互不相交径向壳层')
    for name,(center,radius) in crystals.items():
        rel=center-CORE
        for other in rigid:
            if other in annuli:
                low,high,zmax=annuli[other]
                r=np.linalg.norm(rel[:2]); dr=max(0,low-r,r-high); dz=max(0,abs(rel[2])-zmax)
                gap=np.hypot(dr,dz)-radius-corner
                method='晶体全旋转包围球与外环/星阵绕Z旋转的完整环形圆柱包络'
            elif other=='spears':
                points=world[other]; cylindrical=np.c_[np.linalg.norm((points-CORE)[:,[0,2]],axis=1),points[:,1]]
                query=[np.linalg.norm(rel[[0,2]]),center[1]]
                gap=float(cKDTree(cylindrical).query(query)[0])-radius-corner
                method='晶体包围球与六矛绕Y公转的连续圆周并集'
            else:
                gap=np.linalg.norm(rel)-radius-shells[other][1]-corner
                method='晶体全旋转包围球与内环/核心全旋转外接球'
            record(name,other,gap,method)
    for a,b in itertools.combinations(crystals,2):
        ca,ra=crystals[a];cb,rb=crystals[b]
        record(a,b,np.linalg.norm(ca-cb)-ra-rb,'固定中心、独立任意旋转的两包围球')
    assert len(records)==32*31//2

    yy,zz,xx=np.nonzero(cube)
    static_max_y=float(yy.max()-offset[1])
    static_max_r=float(np.hypot(xx-offset[0]-CORE[0],zz-offset[2]-CORE[2]).max())
    del xx,yy,zz
    for name in parts.files:
        if name in crystals:
            center,radius=crystals[name]
            reach=radius+corner+12
            lower=np.maximum(np.floor(center+offset-reach).astype(int),0)
            upper=np.minimum(np.ceil(center+offset+reach).astype(int)+1,manifest['size'])
            sample=cube[lower[1]:upper[1],lower[2]:upper[2],lower[0]:upper[0]]
            y,z,x=np.nonzero(sample)
            gap=12.
            if len(x):
                points=np.c_[x,y,z]+lower-offset
                gap=min(gap,float(np.linalg.norm(points-center,axis=1).min())-radius-corner)
            record(name,'fixed_architecture',gap,'局部完整静态体素对晶体包围球的最近距离；窗口外距离另以12格下界覆盖')
        elif name=='spears':
            rel=world[name]-CORE
            dr=np.maximum(0,np.linalg.norm(rel[:,[0,2]],axis=1)-static_max_r)
            dy=np.maximum(0,world[name][:,1]-static_max_y)
            record(name,'fixed_architecture',float(np.hypot(dr,dy).min())-2*corner,'六矛每一体素的连续Y公转圆周与包含全部静态建筑的圆柱')
        else:
            record(name,'fixed_architecture',float(CORE[1]-shells[name][1]-static_max_y)-2*corner,'整个旋转球壳最低点高于完整静态建筑最高点')
    assert len(records)==528
    # 六柄矛共用一个刚体运动；确认模型内六矛初始也互不相交。
    spear=parts['spears']; lengths=[]
    import w03_eye_c3_20261108 as geometry
    local=np.array(list(geometry.c1.LOCAL),float)
    local_states=np.array([geometry.IDS[s] for s in geometry.c1.LOCAL.values()],np.uint8)
    pieces=[]
    for info in manifest['spears']:
        axis=np.array(info['tail_axis']);u=np.cross(axis,[0.,1.,0.]);u/=np.linalg.norm(u);z=np.cross(axis,u)
        p=geometry.unique_part('spear',np.array(info['tip'])+local[:,:1]*axis+local[:,1:2]*u+local[:,2:3]*z,local_states).p
        lengths.append(len(p));pieces.append(p)
        assert np.linalg.norm(np.cross(np.array(info['tip'])-CORE,np.array(info['tail'])-CORE))<1e-8
        assert info['tip'][1]<CORE[1] and info['tail'][1]<info['tip'][1]
    assert np.array_equal(np.concatenate(pieces),spear)
    spear_min=min(float(cKDTree(a).query(b,workers=1)[0].min())-2*corner for a,b in itertools.combinations(pieces,2))
    assert spear_min>0
    # 运动参数：只改外环/外星阵旋转；内四环与核心、六矛、晶体的原旋转保持。
    for c,old in zip(config['components'],oldconfig['components']):
        assert c['id']==old['id']
        if c['id'] in annuli: assert c['rotations']==[dict(axis=[0,0,1],degrees_per_second=3)]
        else: assert c['rotations']==old['rotations']
    assert all(v[0]==v[2]==0 and v[1]<=0 for v in manifest['crystal_shifts'].values())
    assert all(v[1]<0 for v in manifest['spear_shifts'])
    assert all(sha(ROOT/name)==expected for name,expected in load(LOG/'preserved-files.json').items())
    result=dict(passed=True,method='连续保守包络证明，非离散帧抽样',pair_count=528,
        conservative_corner_radius=corner,continuous_all_time=True,full_cycle_seconds=360,
        global_surface_clearance_lower_bound=min(r['minimum_surface_gap_lower_bound'] for r in records),
        moving_pair_minimum=min(r['minimum_surface_gap_lower_bound'] for r in records[:496]),
        six_spears_internal_minimum_lower_bound=spear_min,records=records,
        outer_ring_normal_fixed=True,inner_four_c6_rotations_preserved=True,
        all_spears_upward_and_target_core=True,crystals_only_moved_down=True,
        blocks_unchanged=manifest['blocks'],size_xyz=manifest['size'],
        old_candidates_unchanged=True,game_verified=False,
        limitation='证明对应当前候选预览的矩阵与方块几何；尚未实现游戏内运动、GT成型与3.5客户端性能验收。')
    save(LOG/'continuous-clearance.json',result)
    for path in [OUT/'verification.json',OUT/'manifest.json']:
        value=load(path);value['continuous_dynamic_clearance']=True
        value['dynamic_clearance_fully_accepted']=False
        value['continuous_clearance_proof']='../../logs/w03-c5-outer-down-c9-20261108/continuous-clearance.json'
        value['minimum_dynamic_surface_clearance_lower_bound']=result['global_surface_clearance_lower_bound']
        if path.name=='manifest.json':
            value['remaining_component_motion_identical_to_c6']=False
            value['inner_four_ring_motion_identical_to_c6']=True
            value['comparison']['code']='C9'
        save(path,value)
    shutil.copy2(__file__,OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=False))


if __name__=='__main__':main()
