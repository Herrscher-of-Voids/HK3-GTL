# -*- coding: utf-8 -*-
"""以C6为运动基线，仅删除负责人圈定的星冠、天顶光柱和后部外伸节点。"""
import ast
import base64
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import gzip
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
STATIC = ROOT / 'deliveries/W03_C4_五环锁芯与立体晶云_20261108'
SOURCE = ROOT / 'deliveries/W03_C6_球形全动试转_20261108'
OUT = ROOT / 'deliveries/W03_C8_去星冠光柱与外伸节点_20261108'
LOG = ROOT / 'logs/w03-trim-c8-20261108'


def load(path): return json.loads(path.read_text('utf8'))
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def unpack(path): return json.loads(gzip.decompress(base64.b64decode(json.loads(path.read_text('utf8').split('=', 1)[1].strip().rstrip(';')))))
def packed(path, name, value):
    encoded = base64.b64encode(gzip.compress(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf8'), 6)).decode()
    path.write_text('window.' + name + '=' + json.dumps(encoded) + ';\n', 'utf8')


def base_without_rear_node():
    original = geometry.c2.original
    tree = ast.parse(Path(original.__file__).read_text('utf8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'build')
    lines = [ast.unparse(n) for n in function.body]
    first_anchor = lines.index('anchors = []')
    bridge = next(i for i, text in enumerate(lines) if text.startswith('box((324, 47, 0)'))
    rear = next(i for i, text in enumerate(lines) if text.startswith('beam([336, 15, 460]'))
    function.body = function.body[:first_anchor] + function.body[bridge:rear] + ast.parse('return c').body
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    env = dict(original.__dict__, IDS=geometry.IDS)
    exec(compile(module, str(original.__file__) + '（无后伸节点基座）', 'exec'), env)
    return env['build']()


def main():
    view = OUT / 'w03'; view.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    baseline = LOG / 'before'
    if not baseline.exists():
        for name in ['logs/beta5-completion-audit-20261030/index.html', 'logs/beta5-completion-audit-20261030/current-summary.json', 'rule/当前多方块设计规则.md', 'AGENTS.md']:
            dest = baseline / name; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / name, dest)
        preserved = {str(p.relative_to(ROOT)): sha(p) for folder in [STATIC, SOURCE, ROOT / 'deliveries/W03_C7_同步立体净空修订_20261108', ROOT / 'deliveries/W02_Gemini_十二翼重构船坞_V3_20261108'] for p in folder.rglob('*') if p.is_file()}
        save(LOG / 'preserved-files.json', preserved)
    source = load(STATIC / 'manifest.json'); payload = unpack(STATIC / 'w03/data.js'); config = unpack(SOURCE / 'w03/motion-data.js')
    states = payload['palette']; assert states == geometry.STATES
    w, h, d = source['size']; offset = np.array(source['blueprint_to_export_offset_xyz'])
    shape = (h, d, w)
    with gzip.open(STATIC / 'w03' / (source['name'] + '.schem'), 'rb') as handle:
        assert exact(handle, len(_headers(states, shape, source['blocks'])[1])) == _headers(states, shape, source['blocks'])[1]
        cube = np.frombuffer(exact(handle, w * h * d), np.uint8).copy().reshape(shape)
    original_cube = cube.copy(); bounds = source['clearance']['part_bounds_blueprint']
    raw = np.load(ROOT / 'logs/w03-clearance-c2-20261108/raw-circle.npz', allow_pickle=False)

    def original(name):
        p = raw[name + '__p'].copy(); p += np.array(bounds[name]['min']) - p.min(0)
        assert np.array_equal(p.max(0), bounds[name]['max']); return p

    removed = {}
    for name, points in [('top_crown', np.concatenate([original('crown:' + str(i)) for i in range(12)])),
                         ('orange_column', original('core')[original('core')[:, 1] > 424])]:
        at = points + offset; assert np.all(cube[at[:, 1], at[:, 2], at[:, 0]] > 0)
        cube[at[:, 1], at[:, 2], at[:, 0]] = 0
        removed[name] = dict(blocks=len(points), min_blueprint=points.min(0).tolist(), max_blueprint=points.max(0).tolist())
    # 只重建原生成器中的基座段，恢复外伸构件曾覆盖的底座；不改舰桥或池内设备。
    background = base_without_rear_node()
    lo, hi = np.array([332, 12, 457]), np.array([340, 42, 528])
    a, b = lo + offset, hi + offset
    target = cube[a[1]:b[1]+1, a[2]:b[2]+1, a[0]:b[0]+1]
    replacement = background[lo[1]:hi[1]+1, lo[2]:hi[2]+1, lo[0]:hi[0]+1]
    changed = target != replacement
    removed['rear_node'] = dict(blocks=int(np.count_nonzero(changed & (replacement == 0))),
        restored_background_blocks=int(np.count_nonzero(changed & (replacement > 0))),
        min_blueprint=lo.tolist(), max_blueprint=hi.tolist(), source='原V4后部汇流节点：斜梁、末端紫晶、根部散热块')
    allowed = np.zeros_like(cube, bool)
    for key in ['top_crown', 'orange_column']:
        info = removed[key]; p, q = np.array(info['min_blueprint']) + offset, np.array(info['max_blueprint']) + offset
        allowed[p[1]:q[1]+1, p[2]:q[2]+1, p[0]:q[0]+1] = True
    allowed[a[1]:b[1]+1, a[2]:b[2]+1, a[0]:b[0]+1] = True
    target[:] = replacement
    assert not np.any((cube != original_cube) & ~allowed)
    assert int(np.count_nonzero(original_cube)) == source['blocks']
    assert not np.any(cube[:, 521:, :]) and np.any(cube[:, 520, :])
    cube = cube[:, :521, :].copy(); del allowed, original_cube, background
    used = np.flatnonzero(np.bincount(cube.ravel(), minlength=len(states)+1)[1:])
    remap = np.zeros(len(states)+1, np.uint8); remap[used+1] = np.arange(1, len(used)+1)
    cube = remap[cube]; states = [states[i] for i in used]
    data = deepcopy(payload['data']); data.update(name='hk3gtl-w03-trim-c8', candidate_version='C8',
        title='空之律者 · 穹界·虚数锚定环 · C8去冠与外伸节点', size=[w, h, 521],
        description='以C6为基础删除顶部12星冠、橙色光柱和后部外伸汇流节点；其余独立球形运动不变。',
        purpose='负责人两张红圈截图的三处指定删除，不沿用C7方案。')
    data['blueprint_bounds_xyz']['max'][2] = 520
    data['clearance']['part_bounds_blueprint'] = {n: deepcopy(b) for n, b in bounds.items() if not n.startswith('crown:')}
    data['clearance']['part_count'] -= 12
    data['clearance']['part_bounds_blueprint']['core']['max'][1] = 424
    data['clearance']['part_bounds_blueprint']['base']['max'][2] = 489
    check = generic_audit(cube, data, states, dict(removals=removed, source_motion='C6', dynamic_clearance_fully_accepted=False))
    materials, resources, packs = resource_materials(states)
    resource_files = sorted({s.split('!/', 1)[0] for s in resources.values()})
    exported = export_dense(cube, states, data['name'], view)
    groups, lengths, merged = merge_surface_runs(exported['surface_groups'], data['size'])
    check.update(readback=exported['readback'], nbt_schem_sha256=exported['hashes'],
        source_instance=str(INSTANCE), instance_version='3.5', instance_version_source='负责人确认并已记录实例基线',
        material_resource_sources=resources, resource_file_sha256={s: sha(Path(s)) for s in resource_files},
        enabled_file_resource_packs=packs, resource_registration_verified=False,
        viewer_surface_merge=merged, viewer_surface_faces=merged['original_unit_faces'],
        viewer_rendered_quads=merged['rendered_quads'], material_complete_cube=True, viewer_payload_exact_cell_readback=True,
        only_requested_regions_changed=True, complete_geometry_not_clipped=True, desktop_used=False, game_started=False)
    save(OUT / 'verification.json', check)
    payload.update(data=data, palette=states, names={s: payload['names'][s] for s in states},
        surfaceGroups=groups, surfaceRunLengths=lengths, blockCount=check['blocks'], materials=materials, audit=check)
    packed(view / 'data.js', 'HK3_PAYLOAD', payload)
    components = [c for c in config['components'] if c['id'] != 'crown']
    owners = np.zeros_like(cube, np.uint8)
    local = np.array(list(geometry.c1.LOCAL), float); local_states = np.array([geometry.IDS[s] for s in geometry.c1.LOCAL.values()], np.uint8)
    for i, component in enumerate(components):
        name = component['id']
        if name.startswith('ring:'):
            info = next(r for r in source['rings'] if name == 'ring:' + str(r['radius_x']))
            part, _ = geometry.mobius(info['radius_x'], info['plane_tilt_from_XY_deg']); part.move(np.array(bounds[name]['min']) - part.bounds[0]); p = part.p
        elif name == 'outer_stars': p = np.concatenate([original('cannon:' + str(j)) for j in range(24)])
        elif name == 'core':
            p = original('core'); p = p[p[:, 1] <= 424]
        elif name == 'spears':
            pieces = []
            for info in source['spears']:
                v = np.array(info['tail_axis']); u = np.cross(v, [0., 1., 0.]); u /= np.linalg.norm(u); z = np.cross(v, u)
                pieces.append(geometry.unique_part('spear', np.array(info['tip']) + local[:, :1]*v + local[:, 1:2]*u + local[:, 2:3]*z, local_states).p)
            p = np.concatenate(pieces)
        else:
            j = int(name.split(':')[1]); part, info = geometry.crystal(j); part.move(np.array(source['cubes'][j]['center']) - info['center']); p = part.p
        assert len(p) == component['blocks']
        at = p + offset; assert np.all(owners[at[:, 1], at[:, 2], at[:, 0]] == 0)
        assert np.all(cube[at[:, 1], at[:, 2], at[:, 0]] > 0)
        owners[at[:, 1], at[:, 2], at[:, 0]] = i + 1
    owners = owners.ravel(); assignments = []; counts = np.zeros(len(components), np.int64)
    for material, faces in enumerate(groups):
        assigned = []
        for face, starts in enumerate(faces):
            starts = np.asarray(starts, np.int64); lens = np.asarray(lengths[material][face], np.int64); ids = owners[starts]
            expanded = np.concatenate([s + np.arange(n) * (w if face < 2 else 1) for s, n in zip(starts, lens)]) if len(starts) else np.array([], np.int64)
            assert np.array_equal(owners[expanded], np.repeat(ids, lens)), '合并表面跨运动组件'
            assigned.append([np.flatnonzero(ids == i + 1).tolist() for i in range(len(components))]); counts += np.bincount(ids, minlength=len(components)+1)[1:]
        assignments.append(assigned)
    raw.close()
    config.update(title=data['title'], components=components, assignments=assignments, moving_quads=counts.tolist(),
        static_parts=['基座', '八锚塔', '控制器与通用接口'],
        conservative_shell_overlaps=[x for x in config['conservative_shell_overlaps'] if x['other'] != 'crown'])
    config['totals'] = dict(quads=merged['rendered_quads'], faces=merged['original_unit_faces'])
    packed(view / 'motion-data.js', 'W03_MOTION', config)
    assert len(components) == 32 and np.all(counts > 0)
    old_by_id = {c['id']: c for c in unpack(SOURCE / 'w03/motion-data.js')['components']}
    assert all(c == old_by_id[c['id']] for c in components), '剩余运动参数不得改变'
    manifest = dict(data, blocks=check['blocks'], unique_materials=len(states), source_motion='C6',
        removals=removed, motion_components=32, moving_quads=counts.tolist(), moving_stars=24,
        remaining_component_motion_identical_to_c6=True, approved=False, installed=False, game_verified=False,
        dynamic_clearance_fully_accepted=False, status='指定删除后的C6衍生候选待审',
        generated_at=datetime.now(timezone(timedelta(hours=-5))).isoformat())
    save(OUT / 'manifest.json', manifest)
    page = (SOURCE / 'w03/三维评审.html').read_text('utf8').replace(unpack(SOURCE / 'w03/motion-data.js')['title'], data['title'])
    for name in ['viewer.bundle.js', 'boundary-review.js', 'c4-ready.js']:
        page = page.replace('src="' + name + '"', 'src="../../' + SOURCE.name + '/w03/' + name + '"')
    page = page.replace('../../' + STATIC.name + '/w03/' + source['name'], data['name'])
    page = page.replace('../../' + STATIC.name + '/verification.json', '../verification.json')
    page = page.replace('增强版3.0真实资源', '增强版3.5当前实例真实资源')
    page = page.replace('6,650,713实体方块', f'{check["blocks"]:,}实体方块').replace('609×529×636', '609×521×636')
    (view / '三维评审.html').write_text(page, 'utf8')
    (OUT / 'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 C8 · 去冠与外伸节点</title><style>body{max-width:1200px;margin:30px auto;padding:0 20px;background:#111827;color:#eee;font:17px/1.8 system-ui}a{color:#dfc4ff}img{width:100%}iframe{width:100%;height:78vh;border:1px solid #51445c}</style><h1>穹界·虚数锚定环 · C8</h1><p>在C6基础上删除核心上方橙色柱、整圈12星冠、底座后部外伸节点；接点恢复原有底座表面。其余五环、外侧24星、核心、六矛和24颗晶体的形状、位置与独立转动参数均保留。C7不作为基线。</p><p><a href="w03/三维评审.html">打开C8动态预览</a> · <a href="verification.json">指定删除与逐格回读核验</a> · <a href="manifest.json">蓝图与删除清单</a> · <a href="../W03_C6_球形全动试转_20261108/index.html">原C6对照</a></p><img src="三处删除演示.webp" alt="C8去除星冠、橙柱和后伸节点后的独立球形转动"><iframe src="w03/三维评审.html" title="C8完整动态预览"></iframe><p>静态NBT/Schematic与完整表面同步更新，当前3.5实例材质已重取；实际包围盒由完整保留构件计算，未按名义尺寸裁切。本次只落实指定删除，其他动态穿模仍待处理；未批准、未部署，游戏内成型和性能尚未验收。</p></html>''', 'utf8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True); shutil.copy2(__file__, scripts / Path(__file__).name)
    save(LOG / 'geometry-partition.json', dict(passed=True, removals=removed, original_blocks=source['blocks'],
        result_blocks=check['blocks'], retained_motion_identical=True, moving_components=32,
        merged_surface_membership_verified=True, material_instance='增强版3.5', source_files_unchanged=True))
    print(json.dumps(dict(passed=True, blocks=check['blocks'], removed=removed, materials=len(states), moving_components=32), ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
