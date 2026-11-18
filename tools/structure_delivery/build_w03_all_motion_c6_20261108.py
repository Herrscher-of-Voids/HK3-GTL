# -*- coding: utf-8 -*-
"""C6复用C4完整体素，逐格拆分可动构件并记录完整运动包络。"""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
import w03_eye_c3_20261108 as geometry

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/W03_C4_五环锁芯与立体晶云_20261108'
OUT = ROOT / 'deliveries/W03_C6_立体全构件运动_20261108'
LOG = ROOT / 'logs/w03-all-motion-c6-20261108'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    view = OUT / 'w03'
    view.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    baseline = LOG / 'report-baseline'
    if not baseline.exists():
        baseline.mkdir()
        for name in ('index.html', 'current-summary.json'):
            shutil.copy2(ROOT / 'logs/beta5-completion-audit-20261030' / name, baseline / name)
        shutil.copy2(ROOT / 'rule/当前多方块设计规则.md', baseline / 'rule.backup')
        preserved = [ROOT / 'deliveries' / folder / file for folder, file in [
            ('W03_C4_五环锁芯与立体晶云_20261108', 'w03/data.js'),
            ('W03_C5_四环绕核运动_20261108', 'w03/data.js'),
            ('W03_C5_四环绕核运动_20261108', 'w03/motion.bundle.js'),
            ('W02_Gemini_十二翼重构船坞_V3_20261108', 'manifest.json')]]
        save(baseline / 'preserved-sha256.json', {str(p.relative_to(ROOT)): sha(p) for p in preserved})
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    text = (SOURCE / 'w03/data.js').read_text('utf8')
    payload = json.loads(gzip.decompress(base64.b64decode(json.loads(text.split('=', 1)[1].strip().rstrip(';')))))
    width, height, depth = manifest['size']
    offset = np.array(manifest['blueprint_to_export_offset_xyz'])
    core = np.array(manifest['core_center_blueprint'], float)
    owners = np.zeros(width * height * depth, np.uint8)
    bodies, local_points = [], []
    bounds = manifest['clearance']['part_bounds_blueprint']

    def add(name, category, points, pivot, rates, translation=(0, 0, 0), normal=(0, 0, 1)):
        exported = points + offset
        assert np.all(exported >= 0) and np.all(exported < [width, height, depth])
        linear = (exported[:, 1] * depth + exported[:, 2]) * width + exported[:, 0]
        assert not np.any(owners[linear]), ('可动构件归属重叠', name)
        owners[linear] = len(bodies) + 1
        relative = points + np.array(translation) - pivot
        radius = float(np.linalg.norm(relative, axis=1).max() + np.sqrt(3) / 2)
        bodies.append(dict(name=name, category=category, pivot_blueprint=np.asarray(pivot).tolist(),
            pivot_export=(pivot + offset).tolist(), degrees_per_second_xyz=rates,
            render_translation_xyz=list(translation), block_count=len(points),
            initial_normal=list(normal), bounding_sphere_radius=radius))
        local_points.append(relative)

    for i, info in enumerate(manifest['rings']):
        part, _ = geometry.mobius(info['radius_x'], info['plane_tilt_from_XY_deg'])
        part.move(np.array(bounds[part.name]['min']) - part.bounds[0])
        assert np.array_equal(part.bounds[1], bounds[part.name]['max'])
        angle = np.radians(info['plane_tilt_from_XY_deg'])
        add(part.name, 'rings', part.p, core,
            [[1, 1, 0], [3, 2, -1], [-2, 3, 1], [2, -3, 2], [-3, -2, 3]][i],
            (0, 11, 0), [0, -float(np.sin(angle)), float(np.cos(angle))])

    with np.load(ROOT / 'logs/w03-clearance-c2-20261108/raw-circle.npz', allow_pickle=False) as raw:
        def original(name):
            p = raw[name + '__p'].copy()
            p += np.array(bounds[name]['min']) - p.min(0)
            assert np.array_equal(p.max(0), bounds[name]['max'])
            return p
        add('外围24星阵', 'stars', np.concatenate([original('cannon:' + str(i)) for i in range(24)]),
            core, [1, 1, 0], (0, 11, 0))
        add('顶部12星冠', 'crown', np.concatenate([original('crown:' + str(i)) for i in range(12)]),
            np.array([336., 503., 264.]), [1, 3, 1], normal=(0, 1, 0))
        p = original('core')
        # 原稿将天顶光轴也命名为core；按原生成代码的核心顶点与光轴起点拆开。
        body = p[:, 1] <= 424
        add('律者核心', 'core', p[body], core, [1, -2, 3])
        static_beam = int((~body).sum())

    local = np.array(list(geometry.c1.LOCAL), float)
    materials = np.array([geometry.IDS[s] for s in geometry.c1.LOCAL.values()], np.uint8)
    spear_parts = []
    for i, info in enumerate(manifest['spears']):
        v = np.array(info['tail_axis'])
        u = np.cross(v, [0., 1, 0]); u /= np.linalg.norm(u)
        w = np.cross(v, u)
        part = geometry.unique_part('spear:' + str(i), np.array(info['tip']) +
            local[:, :1] * v + local[:, 1:2] * u + local[:, 2:3] * w, materials)
        assert np.array_equal(part.bounds[0], bounds[part.name]['min'])
        assert np.array_equal(part.bounds[1], bounds[part.name]['max'])
        spear_parts.append(part.p)
    add('六矛锁芯阵', 'spears', np.concatenate(spear_parts), core, [0, 1, 0])
    for i, info in enumerate(manifest['cubes']):
        part, old = geometry.crystal(i)
        part.move(np.rint(np.array(info['center']) - old['center']).astype(int))
        assert np.array_equal(part.bounds[0], bounds[part.name]['min'])
        assert np.array_equal(part.bounds[1], bounds[part.name]['max'])
        add(part.name, 'crystals', part.p, np.array(info['center'], float),
            [1 + i % 3, (-1 if i % 2 else 1) * (2 + i % 2), 1 + i % 2])

    assignments, moving_quads = [], [0] * len(bodies)
    totals = dict(quads=0, faces=0, moving_faces=0, static_faces=0)
    for material, groups in enumerate(payload['surfaceGroups']):
        material_assignments = []
        for face, starts in enumerate(groups):
            starts = np.array(starts, np.int64)
            lengths = np.array(payload['surfaceRunLengths'][material][face], np.int64)
            ids = owners[starts]
            stride = width if face < 2 else 1
            expanded = np.concatenate([s + np.arange(n) * stride for s, n in zip(starts, lengths)]) if len(starts) else np.array([], np.int64)
            assert np.array_equal(owners[expanded], np.repeat(ids, lengths)), '合并表面跨运动构件'
            material_assignments.append([np.flatnonzero(ids == i + 1).tolist() for i in range(len(bodies))])
            for i in range(len(bodies)):
                moving_quads[i] += int(np.sum(ids == i + 1))
            totals['quads'] += len(starts)
            totals['faces'] += int(lengths.sum())
            totals['moving_faces'] += int(lengths[ids > 0].sum())
            totals['static_faces'] += int(lengths[ids == 0].sum())
        assignments.append(material_assignments)
    assert all(moving_quads) and totals['faces'] == totals['moving_faces'] + totals['static_faces']
    low = np.min([np.array(b['pivot_blueprint']) - b['bounding_sphere_radius'] for b in bodies] + [np.array([86, 0, 0])], axis=0)
    high = np.max([np.array(b['pivot_blueprint']) + b['bounding_sphere_radius'] for b in bodies] + [np.array([586, 57, 528])], axis=0)
    config = dict(title='空之律者 · 穹界·虚数锚定环 · C6立体全构件运动',
        bodies=bodies, assignments=assignments, cycle_seconds=360, frame_rate_limit=30,
        rotation_order='Rx(t) * Ry(t) * Rz(t)，世界轴复合刚性旋转，不是固定平面自转',
        moving_quads=moving_quads, totals=totals, spears=manifest['spears'],
        core_center_blueprint=core.tolist(), blueprint_to_export_offset_xyz=offset.tolist(),
        dynamic_bounds_blueprint=dict(min=low.tolist(), max=high.tolist()),
        fixed_parts=['基座', '八锚塔', '控制器', '通用接口', '天顶光轴'], static_beam_blocks=static_beam)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode('utf8'))).decode()
    (view / 'motion-data.js').write_text('window.W03_MOTION=' + json.dumps(encoded) + ';\n', 'utf8')
    for name in ('data.js', 'boundary-review.js', 'c4-ready.js', 'c4-aim.js', 'viewer.bundle.js'):
        shutil.copy2(SOURCE / 'w03' / name, view / name)
    page = (SOURCE / 'w03/三维评审.html').read_text('utf8').replace(manifest['title'], config['title'])
    page = page.replace('href="hk3gtl-w03-core-aim-c4.', 'href="../../W03_C4_五环锁芯与立体晶云_20261108/w03/hk3gtl-w03-core-aim-c4.')
    page = page.replace('href="../verification.json"', 'href="../../W03_C4_五环锁芯与立体晶云_20261108/verification.json"')
    page = page.replace('</html>', '<script src="motion-data.js"></script><script src="motion.bundle.js"></script></html>')
    (view / '三维评审.html').write_text(page, 'utf8')
    save(LOG / 'geometry-partition.json', dict(passed=True, bodies=len(bodies),
        base_geometry_sha256=sha(SOURCE / 'w03/data.js'), copy_sha256=sha(view / 'data.js'),
        exact_voxel_membership=True, merged_runs_expanded_and_partition_verified=True,
        totals=totals, moving_quads=moving_quads, static_beam_blocks=static_beam,
        no_geometry_clipping=True, animation_bounds_expanded=True))
    # 球壳包络可证明部分构件始终分离；交叠只记录风险，不擅改原稿净空。
    shells = []
    for body, points in zip(bodies, local_points):
        radius = np.linalg.norm(points, axis=1)
        shells.append(dict(name=body['name'], min_radius=float(radius.min() - np.sqrt(3) / 2),
            max_radius=body['bounding_sphere_radius']))
    same_center = []
    for i, a in enumerate(bodies):
        for j, b in enumerate(bodies[:i]):
            if a['pivot_blueprint'] == b['pivot_blueprint']:
                separated = shells[i]['min_radius'] > shells[j]['max_radius'] or shells[j]['min_radius'] > shells[i]['max_radius']
                same_center.append(dict(a=a['name'], b=b['name'], separated_for_all_rigid_rotations=separated))
    np.savez_compressed(LOG / 'motion-samples.npz', **{str(i): p[::max(1, len(p) // 12000)] for i, p in enumerate(local_points)})
    save(LOG / 'swept-envelopes.json', dict(shells=shells, concentric_pairs=same_center,
        claim='球壳不交是保守全周期分离证明；包络交叠不等于实际穿模，需采样及游戏核验。',
        complete_dynamic_clearance_accepted=False))
    public = {k: v for k, v in config.items() if k != 'assignments'}
    public.update(source='C4完整静态体素；C5另行保留', static_size_xyz=manifest['size'], blocks=manifest['blocks'],
        approved=False, installed=False, game_verified=False, geometry_clipped=False,
        status='全动立体候选待审；姿态不改写NBT，动态净空尚未验收')
    save(OUT / 'manifest.json', public)
    (OUT / 'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>W03 C6 · 立体全构件运动</title><style>body{max-width:1200px;margin:30px auto;padding:0 22px;background:#111827;color:#eee8fa;font:17px/1.8 system-ui}a{color:#e6c3ff}iframe{width:100%;height:82vh;border:1px solid #534562}img{max-width:960px;width:100%}</style>
<h1>穹界·虚数锚定环 · C6立体全构件运动</h1>
<p>五个莫比乌斯环以中央核心为枢轴，绕多个世界轴错速翻转，环面朝向持续改变。最大环也转；外侧24星阵随最大环立体翻转，顶部12星冠独立翻转公转，核心多轴自转。六矛整体缓慢公转，矛尖始终锁定核心；24块晶体在各自原位立体自转，保留坑内与环下的空间分布。</p>
<p><a href="w03/三维评审.html">打开全动预览</a> · <a href="manifest.json">完整运动参数</a> · <a href="../W03_C5_四环绕核运动_20261108/index.html">C5固定平面版本</a> · <a href="../W03_C4_五环锁芯与立体晶云_20261108/index.html">C4静态原稿</a></p>
<img src="立体全动演示.webp" alt="五环、双星阵、核心、六矛与晶体立体运动的加速演示">
<iframe src="w03/三维评审.html" title="W03 C6立体全动"></iframe>
<p>支持分组开关、暂停、复位、360秒拖动与全景。分组关闭时冻结在初始姿态；剖切回到C4原始静态位置。五环及外围星阵整体上移11格以对准核心，未缩放、裁切或删除任何构件。原core分组内的709格天顶光轴单独固定，基座、八锚塔、控制器和接口不动。完整运动包络扩展显示，静态尺寸仍为609×529×636（宽×深×高）。</p>
<p>本版用于比较“全转起来”的观感，动态构件存在包络交叠，不能作为无穿模验收。环与核心各自球壳的保守分离及采样记录见核验文件；未为避碰擅自缩环或移矛。所有分组只上传一次实例矩阵，动画每帧只更新33组姿态；静态颜色与深度缓存，调度上限30帧/秒。网页核验不等于游戏帧率、成型或部署验收。</p>
<p><a href="../../logs/w03-all-motion-c6-20261108/viewer-qa.json">网页核验</a> · <a href="../../logs/w03-all-motion-c6-20261108/collision-samples.json">运动采样</a></p></html>''', 'utf8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    shutil.copy2(__file__, scripts / Path(__file__).name)
    print(json.dumps(dict(passed=True, bodies=len(bodies), moving_quads=sum(moving_quads), totals=totals), ensure_ascii=False))


if __name__ == '__main__':
    main()
