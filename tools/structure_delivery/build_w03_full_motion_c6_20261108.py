# -*- coding: utf-8 -*-
"""C6全动候选：复用C4体素，按真实归属拆分刚性运动组件。"""
import base64
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import numpy as np
import w03_eye_c3_20261108 as geometry

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/W03_C4_五环锁芯与立体晶云_20261108'
OUT = ROOT / 'deliveries/W03_C6_球形全动试转_20261108'
LOG = ROOT / 'logs/w03-full-motion-c6-20261108'
CORE = np.array([336., 366., 264.])


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    view = OUT / 'w03'
    view.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    baseline = LOG / 'report-baseline'
    if not baseline.exists():
        baseline.mkdir()
        for name in ('index.html', 'current-summary.json'):
            shutil.copy2(ROOT / 'logs/beta5-completion-audit-20261030' / name, baseline / name)
        shutil.copy2(ROOT / 'rule/当前多方块设计规则.md', LOG / 'rule-before-c6.backup')
        preserved = {}
        for folder in ('W03_C4_五环锁芯与立体晶云_20261108', 'W03_C5_四环绕核运动_20261108', 'W02_Gemini_十二翼重构船坞_V3_20261108'):
            for p in (ROOT / 'deliveries' / folder).rglob('*'):
                if p.is_file(): preserved[str(p.relative_to(ROOT))] = sha(p)
        save(LOG / 'preserved-deliveries.json', preserved)
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    payload = json.loads(gzip.decompress(base64.b64decode(json.loads((SOURCE / 'w03/data.js').read_text('utf8').split('=', 1)[1].strip().rstrip(';')))))
    width, height, depth = manifest['size']
    offset = np.array(manifest['blueprint_to_export_offset_xyz'])
    bounds = manifest['clearance']['part_bounds_blueprint']
    components, points = [], []

    def component(name, label, coords, pivot, rotations, translation=(0, 0, 0)):
        p = np.asarray(coords, float)
        pivot = np.array(pivot, float)
        translation = np.array(translation, float)
        relative = p + translation - pivot
        half_block_radius = math.sqrt(3) / 2
        radial = np.linalg.norm(relative, axis=1)
        if len(rotations) == 1 and rotations[0]['axis'] == [0, 1, 0]:
            radius = np.linalg.norm(relative[:, [0, 2]], axis=1).max() + half_block_radius
            lo = pivot + [-radius, relative[:, 1].min() - .5, -radius]
            hi = pivot + [radius, relative[:, 1].max() + .5, radius]
        else:
            radius = radial.max() + half_block_radius
            lo, hi = pivot - radius, pivot + radius
        components.append(dict(id=name, label=label, pivot_blueprint=pivot.tolist(),
            pivot_export=(pivot + offset).tolist(), render_translation_xyz=translation.tolist(),
            rotations=rotations, blocks=len(p),
            conservative_swept_bounds_blueprint=dict(min=lo.tolist(), max=hi.tolist()),
            radial_interval_from_own_pivot=[float(radial.min()), float(radial.max())]))
        points.append(p.astype(np.int32))

    def rotation(axis, speed): return dict(axis=list(axis), degrees_per_second=speed)

    for i, info in enumerate(manifest['rings']):
        part, _ = geometry.mobius(info['radius_x'], info['plane_tilt_from_XY_deg'])
        shift = np.array(bounds[part.name]['min']) - part.bounds[0]
        part.move(shift)
        assert np.array_equal(part.bounds[1], bounds[part.name]['max'])
        tilt = math.radians(info['plane_tilt_from_XY_deg'])
        normal = [0, -math.sin(tilt), math.cos(tilt)]
        rotations = [rotation([0, 1, 0], 2 + i), rotation([1, 0, 0], (1 if i % 2 == 0 else -1) * (3 + i % 3)), rotation(normal, (1 if i % 2 == 0 else -1) * (3 + i))]
        component(part.name, f'第{i + 1}莫比乌斯环', part.p, CORE, rotations, CORE - np.array(info['center_blueprint']) - shift)
        components[-1]['initial_normal'] = normal
    with np.load(ROOT / 'logs/w03-clearance-c2-20261108/raw-circle.npz', allow_pickle=False) as raw:
        def original(name):
            p = raw[name + '__p'].copy()
            p += np.array(bounds[name]['min']) - p.min(0)
            assert np.array_equal(p.max(0), bounds[name]['max'])
            return p
        component('outer_stars', '外环外侧24星阵', np.concatenate([original('cannon:' + str(i)) for i in range(24)]), CORE,
                  components[0]['rotations'], [0, 11, 0])
        crown = np.concatenate([original('crown:' + str(i)) for i in range(12)])
        crown_center = (crown.min(0) + crown.max(0)) / 2
        component('crown', '核心上方12星冠冕', crown, crown_center, [rotation([0, 1, 0], -4)])
        core = original('core')
        body = core[core[:, 1] <= CORE[1] + 58]
        beam = core[core[:, 1] > CORE[1] + 58]
        assert len(body) + len(beam) == len(core) and beam[:, 1].min() == 425
        component('core', '中央律者核心', body, CORE, [rotation([0, 1, 0], 3), rotation([1, 0, 0], 2), rotation([0, 0, 1], 1)])
    local = np.array(list(geometry.c1.LOCAL), float)
    states = np.array([geometry.IDS[s] for s in geometry.c1.LOCAL.values()], np.uint8)
    spears = []
    for i, info in enumerate(manifest['spears']):
        v = np.array(info['tail_axis'])
        u = np.cross(v, [0., 1., 0.]); u /= np.linalg.norm(u)
        w = np.cross(v, u)
        p = geometry.unique_part('spear:' + str(i), np.array(info['tip']) + local[:, :1] * v + local[:, 1:2] * u + local[:, 2:3] * w, states)
        assert np.array_equal(p.bounds[0], bounds[p.name]['min']) and np.array_equal(p.bounds[1], bounds[p.name]['max'])
        spears.append(p.p)
    component('spears', '六矛锁芯公转阵列', np.concatenate(spears), CORE, [rotation([0, 1, 0], 2)])
    for i, info in enumerate(manifest['cubes']):
        part, original_info = geometry.crystal(i)
        part.move(np.array(info['center']) - np.array(original_info['center']))
        assert np.array_equal(part.bounds[0], bounds[part.name]['min']) and np.array_equal(part.bounds[1], bounds[part.name]['max'])
        component(part.name, f'浓缩崩坏能晶体{i + 1}', part.p, info['center'],
                  [rotation([0, 1, 0], 2 + i % 4), rotation([1, 0, 0], (1 if i % 2 else -1) * (1 + i % 3))])
    owners = np.zeros(width * height * depth, np.uint8)
    for i, p in enumerate(points):
        at = p + offset
        assert np.all(at >= 0) and np.all(at < [width, height, depth])
        linear = (at[:, 1] * depth + at[:, 2]) * width + at[:, 0]
        assert not np.any(owners[linear]), components[i]['id']
        owners[linear] = i + 1
    assignments, counts = [], np.zeros(len(components), np.int64)
    totals = dict(quads=0, faces=0, moving_faces=0, static_faces=0)
    for material, groups in enumerate(payload['surfaceGroups']):
        material_groups = []
        for face, starts in enumerate(groups):
            starts = np.array(starts, np.int64)
            lengths = np.array(payload['surfaceRunLengths'][material][face], np.int64)
            ids = owners[starts]
            stride = width if face < 2 else 1
            expanded = np.concatenate([s + np.arange(n) * stride for s, n in zip(starts, lengths)]) if len(starts) else np.array([], np.int64)
            assert np.array_equal(owners[expanded], np.repeat(ids, lengths)), ('合面跨运动组件', material, face)
            material_groups.append([np.flatnonzero(ids == i + 1).tolist() for i in range(len(components))])
            counts += np.bincount(ids, minlength=len(components) + 1)[1:]
            totals['quads'] += len(starts)
            totals['faces'] += int(lengths.sum())
            totals['moving_faces'] += int(lengths[ids > 0].sum())
            totals['static_faces'] += int(lengths[ids == 0].sum())
        assignments.append(material_groups)
    assert np.all(counts > 0) and len(components) == 33
    lo = np.min([[0, 0, 0]] + [(np.array(c['conservative_swept_bounds_blueprint']['min']) + offset).tolist() for c in components], axis=0)
    hi = np.max([[width, height, depth]] + [(np.array(c['conservative_swept_bounds_blueprint']['max']) + offset).tolist() for c in components], axis=0)
    # 只列保守径向包络重叠，不能将其当作实际碰撞或完整净空验收。
    shell_overlaps = []
    for ring, p in zip(components[:5], points[:5]):
        r = np.linalg.norm(p + np.array(ring['render_translation_xyz']) - CORE, axis=1)
        for c, q in zip(components[6:], points[6:]):
            d = np.linalg.norm(q - CORE, axis=1)
            if r.min() - 1.8 <= d.max() and d.min() <= r.max() + 1.8:
                shell_overlaps.append(dict(ring=ring['id'], other=c['id'], classification='保守径向包络重叠，非实际穿模结论'))
    config = dict(title='空之律者 · 穹界·虚数锚定环 · C6球形全动试转',
        components=components, assignments=assignments, moving_quads=counts.tolist(), totals=totals,
        pivot_export=(CORE + offset).tolist(), pivot_blueprint=CORE.tolist(),
        cycle_seconds=360, frame_rate_limit=30, spears=manifest['spears'], export_offset=offset.tolist(),
        maximum_ring_fixed=False, multi_axis_spherical_rotation=True,
        conservative_swept_bounds_export=dict(min=lo.tolist(), max=hi.tolist()),
        static_parts=['基座', '八锚塔', '控制器与通用接口', '天顶直光柱'],
        conservative_shell_overlaps=shell_overlaps)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode('utf8'))).decode()
    (view / 'motion-data.js').write_text('window.W03_MOTION=' + json.dumps(encoded) + ';\n', 'utf8')
    for name in ('data.js', 'boundary-review.js', 'c4-ready.js', 'viewer.bundle.js'):
        shutil.copy2(SOURCE / 'w03' / name, view / name)
    page = (SOURCE / 'w03/三维评审.html').read_text('utf8').replace(manifest['title'], config['title'])
    page = page.replace('<script src="c4-aim.js"></script>', '')
    page = page.replace('href="hk3gtl-w03-core-aim-c4.', 'href="../../W03_C4_五环锁芯与立体晶云_20261108/w03/hk3gtl-w03-core-aim-c4.')
    page = page.replace('href="../verification.json"', 'href="../../W03_C4_五环锁芯与立体晶云_20261108/verification.json"')
    page = page.replace('</html>', '<script src="motion-data.js"></script><script src="motion.bundle.js"></script></html>')
    (view / '三维评审.html').write_text(page, 'utf8')
    evidence = dict(passed=True, source_geometry_sha256=sha(SOURCE / 'w03/data.js'),
        copied_geometry_sha256=sha(view / 'data.js'), actual_voxel_membership=True,
        merged_runs_expanded_and_partition_verified=True, component_count=len(components),
        moving_quads=counts.tolist(), totals=totals, static_beam_voxels=len(beam),
        dynamic_clearance_fully_accepted=False, game_implemented=False, game_verified=False)
    save(LOG / 'geometry-partition.json', evidence)
    save(OUT / 'manifest.json', {k: v for k, v in config.items() if k != 'assignments'} | dict(
        source='W03 C4；C5保留对照', source_size_xyz=manifest['size'], source_blocks=manifest['blocks'],
        source_geometry_sha256=evidence['source_geometry_sha256'],
        ring_and_outer_star_translation_blueprint=[0, 11, 0],
        c5_initial_axis_adjustment_reused=False,
        motion_note='五环复合Y/X/原法向旋转；外星阵跟随最大环；顶星阵Y自转；核心XYZ复合自转；六矛整组Y公转且始终指芯；24晶体各自XY自转。直光柱作为固定轴保留。',
        status='全动外观试转候选；未批准、未部署，完整动态净空与游戏性能待验',
        approved=False, installed=False, game_verified=False))
    (OUT / 'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>W03 C6 · 球形全动试转</title><style>body{max-width:1200px;margin:30px auto;padding:0 22px;background:#111827;color:#eee8fa;font:17px/1.8 system-ui}a{color:#e6c3ff}iframe{width:100%;height:78vh;border:1px solid #534562}img{max-width:100%;width:900px}</style>
<h1>穹界·虚数锚定环 · C6球形全动试转</h1>
<p>五个莫比乌斯环绕核心作多轴立体翻转，环面朝向也持续改变。外侧24星跟随最大环翻转；核心上方12星自转，中央核心立体自转；六矛整组绕核心公转，矛尖始终朝向核心；24颗浓缩崩坏能晶体在原位各自转动。</p>
<p><a href="w03/三维评审.html">打开全动预览</a> · <a href="../W03_C5_四环绕核运动_20261108/index.html">C5平面旋转对照</a> · <a href="manifest.json">运动参数与扫掠范围</a></p>
<img src="球形全动演示.webp" alt="W03五环、星阵与核心多轴转动加速演示">
<iframe src="w03/三维评审.html" title="W03球形全动预览"></iframe>
<p>五环与外星阵显式上移11格，对准原核心中心；其余位置与所有体素形状、材料沿用C4。基座、八锚塔、控制器、通用接口及天顶直光柱固定。360秒周期可暂停、拖动、复位；球形翻转不以原稿尺寸裁切，完整显示保守扫掠范围。</p>
<p>本轮是“全动试试看”的离线候选；径向扫掠包络存在重叠，尚未通过完整动态净空验收。预览采用一次表面拆分、刚性矩阵更新和静态颜色／深度缓存，30帧/秒为调度上限，不是游戏性能承诺。NBT仍为C4静态原稿；没有改写游戏方块、成型或研究逻辑，未批准、未部署。</p></html>''', 'utf8')
    scripts = OUT / '生成脚本'
    scripts.mkdir(exist_ok=True)
    shutil.copy2(__file__, scripts / Path(__file__).name)
    print(json.dumps(dict(passed=True, moving_components=len(components), moving_quads=int(counts.sum()), conservative_shell_overlap_pairs=len(shell_overlaps)), ensure_ascii=False))


if __name__ == '__main__': main()
