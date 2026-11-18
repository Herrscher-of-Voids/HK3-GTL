# -*- coding: utf-8 -*-
"""C9：C8几何基础；外环改C5式自法向旋转，晶体与亚空之矛下移。"""
import base64
import gzip
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np

import w03_eye_c3_20261108 as geometry
from build_i25_world_bubble_observatory_20261025 import resource_materials, INSTANCE
from build_wonder_boundary_repairs_20261108 import generic_audit
from i34_open_observatory_export_20261027 import _headers, exact, export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'deliveries/W03_C8_去星冠光柱与外伸节点_20261108'
C6 = ROOT / 'deliveries/W03_C6_球形全动试转_20261108'
C4 = ROOT / 'deliveries/W03_C4_五环锁芯与立体晶云_20261108'
OUT = ROOT / 'deliveries/W03_C9_C5外环下移净空修订_20261108'
LOG = ROOT / 'logs/w03-c5-outer-down-c9-20261108'
CORE = np.array([336, 366, 264])
GAP = 6
VOXEL_RADIUS = np.sqrt(3)


def crystal_ring_gap(center, radius, motion_ranges):
    relative = center - CORE
    inner_max = max(v[1] for n, v in motion_ranges.items() if n.startswith('ring:') and n != 'ring:210')
    gaps = [np.linalg.norm(relative) - radius - inner_max - VOXEL_RADIUS]
    for name in ['ring:210', 'outer_stars']:
        radial_min, radial_max, axial = motion_ranges[name]
        radial = np.linalg.norm(relative[:2])
        dz = max(0, abs(relative[2]) - axial)
        dr = max(0, radial_min - radial, radial - radial_max)
        gaps.append(np.hypot(dz, dr) - radius - VOXEL_RADIUS)
    return float(min(gaps))


def load(path): return json.loads(path.read_text('utf8'))
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def unpack(path):
    raw = path.read_text('utf8').split('=', 1)[1].strip().rstrip(';')
    return json.loads(gzip.decompress(base64.b64decode(json.loads(raw))))
def pack(path, variable, value):
    raw = base64.b64encode(gzip.compress(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf8'), 6)).decode()
    path.write_text('window.' + variable + '=' + json.dumps(raw) + ';\n', 'utf8')


def main():
    view = OUT / 'w03'; view.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    if not (LOG / 'before').exists():
        for name in ['logs/beta5-completion-audit-20261030/index.html', 'logs/beta5-completion-audit-20261030/current-summary.json', 'rule/当前多方块设计规则.md', 'AGENTS.md']:
            target = LOG / 'before' / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / name, target)
        preserved = {str(p.relative_to(ROOT)): sha(p) for folder in [BASE, C6, C4, ROOT / 'deliveries/W03_C7_同步立体净空修订_20261108'] for p in folder.rglob('*') if p.is_file()}
        save(LOG / 'preserved-files.json', preserved)
    base_manifest = load(BASE / 'manifest.json'); data_payload = unpack(BASE / 'w03/data.js')
    motion = unpack(BASE / 'w03/motion-data.js'); states = list(data_payload['palette'])
    w, h, d = base_manifest['size']; offset = np.array(base_manifest['blueprint_to_export_offset_xyz'])
    with gzip.open(BASE / 'w03' / (base_manifest['name'] + '.schem'), 'rb') as handle:
        header = _headers(states, (h, d, w), base_manifest['blocks'])[1]
        assert exact(handle, len(header)) == header
        cube = np.frombuffer(exact(handle, w*h*d), np.uint8).copy().reshape((h, d, w))
        assert exact(handle, 1) == b'\x00' and not handle.read(1)
    original_cube = cube.copy()
    bounds = load(C4 / 'manifest.json')['clearance']['part_bounds_blueprint']
    raw = np.load(ROOT / 'logs/w03-clearance-c2-20261108/raw-circle.npz', allow_pickle=False)

    def original(name):
        p = raw[name + '__p'].copy(); p += np.array(bounds[name]['min']) - p.min(0)
        assert np.array_equal(p.max(0), bounds[name]['max']); return p

    moving = {}; spear_parts = []
    for c in motion['components']:
        name = c['id']
        if name.startswith('ring:'):
            info = next(r for r in base_manifest['rings'] if 'ring:' + str(r['radius_x']) == name)
            part, _ = geometry.mobius(info['radius_x'], info['plane_tilt_from_XY_deg']); part.move(np.array(bounds[name]['min']) - part.bounds[0]); moving[name] = part.p
        elif name == 'outer_stars': moving[name] = np.concatenate([original('cannon:' + str(i)) for i in range(24)])
        elif name == 'core': moving[name] = original('core')[original('core')[:, 1] <= 424]
        elif name == 'spears':
            local = np.array(list(geometry.c1.LOCAL), float); local_states = np.array([geometry.IDS[s] for s in geometry.c1.LOCAL.values()], np.uint8)
            pieces = []
            for info in base_manifest['spears']:
                v = np.array(info['tail_axis']); u = np.cross(v, [0., 1., 0.]); u /= np.linalg.norm(u); z = np.cross(v, u)
                pieces.append(geometry.unique_part('spear', np.array(info['tip']) + local[:, :1] * v + local[:, 1:2] * u + local[:, 2:3] * z, local_states).p)
            spear_parts = pieces
            moving[name] = np.concatenate(pieces)
        elif name.startswith('crystal:'):
            j = int(name.split(':')[1]); part, info = geometry.crystal(j); part.move(np.array(base_manifest['cubes'][j]['center']) - info['center']); moving[name] = part.p
        else: raise AssertionError(name)
    # 先清空待移动体素；目的地再统一检查，避免把旧自身当成静态障碍。
    for p in moving.values():
        at = p + offset; assert np.all(cube[at[:, 1], at[:, 2], at[:, 0]] > 0); cube[at[:, 1], at[:, 2], at[:, 0]] = 0
    ranges = {}
    for c in motion['components']:
        if c['id'].startswith('ring:') or c['id'] == 'outer_stars':
            p = moving[c['id']] + c['render_translation_xyz'] - CORE
            radial = np.linalg.norm(p, axis=1)
            ranges[c['id']] = [float(radial.min()), float(radial.max()), float(np.abs(p[:,2]).max())]
    new = {}; crystal_shifts = {}; spear_shifts = []
    for name, p in moving.items():
        if name.startswith('crystal:'):
            j = int(name.split(':')[1]); old_center = np.array(base_manifest['cubes'][j]['center'])
            radius = float(np.linalg.norm(p-old_center, axis=1).max()) + VOXEL_RADIUS
            for drop in range(241):
                delta = np.array([0, -drop, 0])
                if crystal_ring_gap(old_center+delta, radius, ranges) >= GAP: break
            else: raise AssertionError(('纯下移无法避开环系，不静默挪动横向位置', name))
            q = p + delta; crystal_shifts[name] = delta.tolist()
        elif name == 'spears':
            pieces = []
            for old_piece, info in zip(spear_parts, base_manifest['spears']):
                a = np.rint(np.array(info['tail_axis'])*41).astype(int)
                for k in range(16):
                    candidate = old_piece + k*a
                    if np.linalg.norm(candidate-CORE, axis=1).min() - max(v[1] for v in ranges.values()) - 2*VOXEL_RADIUS >= GAP: break
                else: raise AssertionError('完整亚空之矛的轴向下移无解')
                pieces.append(candidate); spear_shifts.append((k*a).tolist())
            q = np.concatenate(pieces)
        else: q = p
        new[name] = q
    # 下移沿矛轴带来横向扩展；先按完整目的几何扩域，禁止夹边或截断。
    y,z,x = np.nonzero(cube)
    static_lo = np.array([x.min(),y.min(),z.min()])-offset
    static_hi = np.array([x.max(),y.max(),z.max()])-offset
    lo = np.min([static_lo]+[p.min(0) for p in new.values()],axis=0)
    hi = np.max([static_hi]+[p.max(0) for p in new.values()],axis=0)
    size = hi-lo+1; new_offset=-lo
    result=np.zeros((size[1],size[2],size[0]),np.uint8)
    at=np.c_[x,y,z]-offset+new_offset;result[at[:,1],at[:,2],at[:,0]]=cube[y,z,x]
    del x,y,z,at
    for name, p in new.items():
        oldp = moving[name]; oldat = oldp + offset; newat = p + new_offset
        assert np.all(newat>=0) and np.all(newat<size),name
        assert np.all(result[newat[:,1],newat[:,2],newat[:,0]] == 0),('构件重叠',name)
        result[newat[:,1],newat[:,2],newat[:,0]]=original_cube[oldat[:,1],oldat[:,2],oldat[:,0]]
    cube=result;old_offset=offset;offset=new_offset;w,h,d=map(int,size)
    # 已知的删除候选继续保留；真实状态总数、空洞和目标偏移必须可回读。
    used = np.flatnonzero(np.bincount(cube.ravel(), minlength=len(states) + 1)[1:]); remap = np.zeros(len(states) + 1, np.uint8); remap[used + 1] = np.arange(1, len(used) + 1); cube = remap[cube]; new_states = [states[i] for i in used]
    data = deepcopy(data_payload['data']); data.update(name='hk3gtl-w03-c5-outer-down-c9', candidate_version='C9', title='空之律者 · 穹界·虚数锚定环 · C9 C5外环与下移净空', size=[w,h,d], blueprint_to_export_offset_xyz=offset.tolist(), blueprint_bounds_xyz=dict(min=lo.tolist(),max=hi.tolist()), source_motion='C6', description='以C6独立运动为基础，最外环改C5式绕自身法向旋转；浓缩崩坏能晶体与亚空之矛下移。', purpose='避开第四层环的动态范围，保留独立球形运动观感。')
    export_delta=offset-old_offset
    data['removals']=deepcopy(base_manifest['removals'])
    data['controller']=(np.array(data['controller'])+export_delta).tolist()
    for item in data['ports']:item['pos']=(np.array(item['pos'])+export_delta).tolist()
    for item in data['paths']:
        for key in ['min','max']:item[key]=(np.array(item[key])+export_delta).tolist()
    for item in data['zones']:item['pos']=(np.array(item['pos'])+export_delta).tolist()
    for item in data['pipe_routes']:
        for key in ['start','end','path']:item[key]=(np.array(item[key])+export_delta).tolist()
    for name,p in new.items():
        if name=='spears':continue
        if name in data['clearance']['part_bounds_blueprint']:data['clearance']['part_bounds_blueprint'][name]=dict(min=p.min(0).tolist(),max=p.max(0).tolist())
    data['cubes'] = deepcopy(base_manifest['cubes'])
    for j, delta in [(int(k.split(':')[1]), v) for k, v in crystal_shifts.items()]: data['cubes'][j]['center'] = (np.array(data['cubes'][j]['center']) + delta).tolist(); data['cubes'][j]['motion_translation_blueprint'] = delta
    data['spears'] = deepcopy(base_manifest['spears'])
    for i,(info,delta) in enumerate(zip(data['spears'],spear_shifts)):
        info['tip']=(np.array(info['tip'])+delta).tolist();info['tail']=(np.array(info['tail'])+delta).tolist();info['motion_translation_blueprint']=delta;info['tip_distance_to_core']=float(np.linalg.norm(np.array(info['tip'])-CORE));info['axis_position_multiplier']+=round(np.linalg.norm(delta)/41)
        p=spear_parts[i]+delta;data['clearance']['part_bounds_blueprint']['spear:'+str(i)]=dict(min=p.min(0).tolist(),max=p.max(0).tolist())
    materials, resources, packs = resource_materials(new_states)
    exported = export_dense(cube, new_states, data['name'], view); groups, lengths, merged = merge_surface_runs(exported['surface_groups'], data['size'])
    check = generic_audit(cube, data, new_states, dict(source_motion='C6', selected_motion_change='外环C5式自法向旋转', crystal_shifts=crystal_shifts, spear_shifts=spear_shifts, dynamic_clearance_fully_accepted=False))
    check.update(readback=exported['readback'], nbt_schem_sha256=exported['hashes'], source_instance=str(INSTANCE), instance_version='3.5', instance_version_source='负责人已确认并记录', material_resource_sources=resources, resource_file_sha256={s: sha(Path(s)) for s in sorted({x.split('!/', 1)[0] for x in resources.values()})}, enabled_file_resource_packs=packs, viewer_surface_merge=merged, viewer_surface_faces=merged['original_unit_faces'], viewer_rendered_quads=merged['rendered_quads'], material_complete_cube=True, viewer_payload_exact_cell_readback=True, complete_geometry_not_clipped=True, only_requested_regions_changed=True)
    save(OUT / 'verification.json', check)
    payload = deepcopy(data_payload); payload.update(data=data, palette=new_states, names={s: data_payload['names'][s] for s in new_states}, surfaceGroups=groups, surfaceRunLengths=lengths, blockCount=check['blocks'], materials=materials, audit=check); pack(view / 'data.js', 'HK3_PAYLOAD', payload)
    owners = np.zeros(cube.size, np.uint8); assignments=[]; counts=np.zeros(len(moving), np.int64); names=list(moving)
    for i, (name, p) in enumerate(new.items(), 1):
        at=p+offset; owners[(at[:,1]*d+at[:,2])*w+at[:,0]]=i
    for mid, faces in enumerate(groups):
        ma=[]
        for face, starts in enumerate(faces):
            starts=np.asarray(starts,np.int64); lens=np.asarray(lengths[mid][face],np.int64); ids=owners[starts]; stride=w if face<2 else 1; expanded=np.concatenate([s+np.arange(n)*stride for s,n in zip(starts,lens)]) if len(starts) else np.array([],np.int64); assert np.array_equal(owners[expanded],np.repeat(ids,lens)); ma.append([np.flatnonzero(ids==i+1).tolist() for i in range(len(names))]); counts+=np.bincount(ids,minlength=len(names)+1)[1:]
        assignments.append(ma)
    config=unpack(BASE/'w03/motion-data.js'); config.update(title=data['title'], components=deepcopy(config['components']), assignments=assignments, moving_quads=counts.tolist(), moving_component_ids=names, outer_ring_motion='C5 own-normal rotation', crystal_shifts=crystal_shifts, spear_shifts=spear_shifts, c6_component_shapes_preserved=True,export_offset=offset.tolist(),pivot_export=(CORE+offset).tolist(),spears=data['spears'])
    for c in config['components']:
        if c['id'] in ('ring:210','outer_stars'): c['rotations']=[{'axis':[0,0,1], 'degrees_per_second':3}]
        elif c['id'].startswith('crystal:'): c['pivot_blueprint']=(np.array(c['pivot_blueprint'])+np.array(crystal_shifts.get(c['id'],[0,0,0]))).tolist()
        elif c['id']=='spears': c['render_translation_xyz']=[0,0,0]
        c['pivot_export']=(np.array(c['pivot_blueprint'])+offset).tolist()
        p=new[c['id']];rel=p+c['render_translation_xyz']-c['pivot_blueprint'];radius=float(np.linalg.norm(rel,axis=1).max())+VOXEL_RADIUS
        if c['id']=='spears':
            radius=float(np.linalg.norm(rel[:,[0,2]],axis=1).max())+VOXEL_RADIUS
            lower=np.array(c['pivot_blueprint'])+[-radius,float(rel[:,1].min())-VOXEL_RADIUS,-radius];upper=np.array(c['pivot_blueprint'])+[radius,float(rel[:,1].max())+VOXEL_RADIUS,radius]
        else:lower=np.array(c['pivot_blueprint'])-radius;upper=np.array(c['pivot_blueprint'])+radius
        c['conservative_swept_bounds_blueprint']=dict(min=lower.tolist(),max=upper.tolist())
    config['conservative_swept_bounds_export']=dict(min=np.min([[0,0,0]]+[np.array(c['conservative_swept_bounds_blueprint']['min'])+offset for c in config['components']],axis=0).tolist(),max=np.max([size]+[np.array(c['conservative_swept_bounds_blueprint']['max'])+offset for c in config['components']],axis=0).tolist())
    config['components']=[c for c in config['components'] if c['id']!='crown']; assert len(config['components'])==32 and np.all(counts>0)
    pack(view/'motion-data.js','W03_MOTION',config)
    manifest=deepcopy(data); manifest.update(blocks=check['blocks'], unique_materials=len(new_states), moving_components=32, moving_quads=counts.tolist(), fixed_outer_ring=False, c5_outer_ring_rotation=True, crystal_shifts=crystal_shifts, spear_shifts=spear_shifts, c6_component_shapes_preserved=True, approved=False, installed=False, game_verified=False, dynamic_clearance_fully_accepted=False, generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(), status='C6衍生：C5式外环与下移净空候选待审')
    save(OUT/'manifest.json',manifest)
    page=(BASE/'w03/三维评审.html').read_text('utf8').replace('C8','C9').replace('去冠与外伸节点','C5外环与下移净空')
    page=page.replace(base_manifest['name'],data['name']).replace('609×521×636',f'{w}×{d}×{h}')
    np.savez_compressed(LOG/'moving-parts.npz',**new)
    save(LOG/'motion-envelopes.json',dict(ring_ranges=ranges,core=CORE.tolist(),crystal_shifts=crystal_shifts,spear_shifts=spear_shifts,voxel_radius=VOXEL_RADIUS))
    (view/'三维评审.html').write_text(page,'utf8')
    (OUT/'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 C9 · C5外环与下移净空</title><style>body{max-width:1200px;margin:30px auto;padding:0 20px;background:#111827;color:#eee;font:17px/1.8 system-ui}a{color:#dfc4ff}img{width:100%}iframe{width:100%;height:78vh;border:1px solid #51445c}</style><h1>穹界·虚数锚定环 · C9</h1><p>以C6为基线：最外环改为C5式绕自身法向旋转，外侧24星阵同步；24颗浓缩崩坏能晶体下移至第四层环的动态范围之外，六柄亚空之矛沿自身背离核心轴线下移，仍持续指向核心。C7不作为基线。</p><p><a href="w03/三维评审.html">打开C9动态预览</a> · <a href="verification.json">位移与逐格回读核验</a> · <a href="manifest.json">蓝图与运动参数</a> · <a href="../W03_C8_去星冠光柱与外伸节点_20261108/index.html">C8对照</a></p><iframe src="w03/三维评审.html" title="C9完整动态预览"></iframe><p>静态结构与当前增强版3.5材质同步更新，完整包围盒未裁切。外环只改用C5自法向旋转；其余C6独立运动保持。当前只证明位移和归属，完整动态净空、游戏成型与性能仍待验收。</p></html>''','utf8')
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True);shutil.copy2(__file__,scripts/Path(__file__).name)
    save(LOG/'geometry-partition.json',dict(passed=True,base='C6 via C8',c5_outer_ring_rotation=True,crystal_shifts=crystal_shifts,spear_shifts=spear_shifts,components=32,merged_surface_membership_verified=True,source_files_unchanged=True,material_instance='增强版3.5'))
    print(json.dumps(dict(passed=True,blocks=check['blocks'],crystals=crystal_shifts,spear_shifts=spear_shifts,moving_components=32,size=data['size']),ensure_ascii=False))


if __name__ == '__main__': main()
