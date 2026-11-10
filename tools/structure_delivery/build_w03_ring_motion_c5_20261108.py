# -*- coding: utf-8 -*-
"""复用C4完整表面，为四个内环制作独立矩阵动画预览。"""
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
OUT = ROOT / 'deliveries/W03_C5_四环绕核运动_20261108'
LOG = ROOT / 'logs/w03-ring-motion-c5-20261108'


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
        report = ROOT / 'logs/beta5-completion-audit-20261030'
        for name in ('index.html', 'current-summary.json'):
            shutil.copy2(report / name, baseline / name)
        save(baseline / 'sha256.json', {p.name: sha(p) for p in baseline.iterdir() if p.is_file()})
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    text = (SOURCE / 'w03/data.js').read_text('utf8')
    payload = json.loads(gzip.decompress(base64.b64decode(json.loads(text.split('=', 1)[1].strip().rstrip(';')))))
    width, height, depth = manifest['size']
    offset = np.array(manifest['blueprint_to_export_offset_xyz'])
    core = np.array(manifest['core_center_blueprint'], float)
    owners = np.zeros(width * height * depth, np.uint8)
    rings, parts = [], []
    for index, info in enumerate(manifest['rings']):
        part, _ = geometry.mobius(info['radius_x'], info['plane_tilt_from_XY_deg'])
        bounds = manifest['clearance']['part_bounds_blueprint'][part.name]
        shift = np.array(bounds['min']) - part.bounds[0]
        part.move(shift)
        assert np.array_equal(part.bounds[1], bounds['max'])
        exported = part.p + offset
        assert np.all(exported >= 0) and np.all(exported < [width, height, depth])
        linear = (exported[:, 1] * depth + exported[:, 2]) * width + exported[:, 0]
        assert not np.any(owners[linear])
        owners[linear] = index + 1
        parts.append(part)
        if index:
            tilt = math.radians(info['plane_tilt_from_XY_deg'])
            rings.append(dict(radius=info['radius_x'], axis=[0, -math.sin(tilt), math.cos(tilt)],
                              degrees_per_second=[3, -4, 5, -6][index - 1],
                              center_blueprint=(np.array(info['center_blueprint']) + shift).tolist(),
                              render_translation_xyz=(core - np.array(info['center_blueprint']) - shift).tolist(),
                              block_count=len(part.p), pivot_blueprint=core.tolist()))
    assignments, static_cells, moving_quads = [], [], [0] * 4
    totals = dict(quads=0, faces=0, moving_faces=0, outer_faces=0)
    for material, groups in enumerate(payload['surfaceGroups']):
        material_assignments = []
        for face, starts in enumerate(groups):
            starts = np.array(starts, np.int64)
            lengths = np.array(payload['surfaceRunLengths'][material][face], np.int64)
            ids = owners[starts]
            stride = width if face < 2 else 1
            # 合面不能跨构件；逐格重展核验，而非用包围盒猜环的归属。
            expanded = np.concatenate([s + np.arange(n) * stride for s, n in zip(starts, lengths)]) if len(starts) else np.array([], np.int64)
            assert np.array_equal(owners[expanded], np.repeat(ids, lengths))
            for index in range(5):
                selected = starts[ids == index + 1]
                if len(selected):
                    assert np.all(owners[selected] == index + 1)
            material_assignments.append([np.flatnonzero(ids == i + 2).tolist() for i in range(4)])
            for i in range(4):
                moving_quads[i] += int(np.sum(ids == i + 2))
            static_cells.append(expanded[owners[expanded] < 2])
            totals['quads'] += len(starts)
            totals['faces'] += int(lengths.sum())
            totals['moving_faces'] += int(lengths[ids >= 2].sum())
            totals['outer_faces'] += int(lengths[ids == 1].sum())
        assignments.append(material_assignments)
    assert all(moving_quads) and totals['outer_faces'] > 0
    # 筛查各环完整公转所占的保守圆柱环带；结果只作动态净空线索。
    cells = np.unique(np.concatenate(static_cells))
    xyz = np.c_[cells % width, cells // (width * depth), cells // width % depth].astype(float) - offset
    relative = xyz - core
    envelopes = []
    for info, part in zip(rings, parts[1:]):
        axis = np.array(info['axis'])
        p = part.p + np.array(info['render_translation_xyz']) - core
        axial = p @ axis
        radius = np.sqrt(np.maximum(0, np.sum(p * p, axis=1) - axial * axial))
        original_tilt = next(r['plane_tilt_from_XY_deg'] for r in manifest['rings'] if r['radius_x'] == info['radius'])
        for adjustment in [0] + [sign * degree for degree in range(1, 16) for sign in (1, -1)]:
            tilt = math.radians(original_tilt + adjustment)
            candidate_axis = np.array([0, -math.sin(tilt), math.cos(tilt)])
            a = relative @ candidate_axis
            r = np.sqrt(np.maximum(0, np.sum(relative * relative, axis=1) - a * a))
            possible = ((a >= axial.min() - 1.8) & (a <= axial.max() + 1.8) &
                        (r >= radius.min() - 1.8) & (r <= radius.max() + 1.8))
            if not possible.any():
                info.update(axis=candidate_axis.tolist(), initial_rotation_x_degrees=adjustment,
                            animation_plane_tilt_deg=original_tilt + adjustment)
                break
        else:
            raise AssertionError(('完整扫掠净空无解，需另行设计，不静默缩环', info['radius']))
        envelopes.append(dict(radius=info['radius'], axial_min=float(axial.min()), axial_max=float(axial.max()),
                              radial_min=float(radius.min()), radial_max=float(radius.max()),
                              initial_rotation_x_degrees=adjustment,
                              static_surface_cells_in_conservative_envelope=int(possible.sum())))
    config = dict(title='空之律者 · 穹界·虚数锚定环 · C5四环绕核运动',
                  pivot_export=(core + offset).tolist(), pivot_blueprint=core.tolist(),
                  rings=rings, assignments=assignments, cycle_seconds=360, frame_rate_limit=30,
                  maximum_ring_fixed=True, geometry_blocks_and_shape_unchanged=True,
                  inner_ring_centers_aligned_to_core=True, totals=totals,
                  moving_quads=moving_quads)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode('utf8'))).decode()
    (view / 'motion-data.js').write_text('window.W03_MOTION=' + json.dumps(encoded) + ';\n', 'utf8')
    for name in ('data.js', 'boundary-review.js', 'c4-ready.js', 'c4-aim.js', 'viewer.bundle.js'):
        shutil.copy2(SOURCE / 'w03' / name, view / name)
    page = (SOURCE / 'w03/三维评审.html').read_text('utf8')
    page = page.replace(manifest['title'], config['title'])
    page = page.replace('href="hk3gtl-w03-core-aim-c4.', 'href="../../W03_C4_五环锁芯与立体晶云_20261108/w03/hk3gtl-w03-core-aim-c4.')
    page = page.replace('href="../verification.json"', 'href="../../W03_C4_五环锁芯与立体晶云_20261108/verification.json"')
    page = page.replace('</html>', '<script src="motion-data.js"></script><script src="motion.bundle.js"></script></html>')
    (view / '三维评审.html').write_text(page, 'utf8')
    jars = Path(r'C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft/mods')
    research = dict(jar='gtladditions-3.3.1Custom.jar', sha256=sha(jars / 'gtladditions-3.3.1Custom.jar'),
                    source='本机增强版3.0已安装JAR的javap字节码，只研究实现原理；未复制第三方Java代码或素材。',
                    name='伪神之煅炉', registry='gtladditions:forge_of_the_antichrist',
                    methods=[dict(owner='AntichristRingTransforms', method='apply',
                                  finding='先平移至星体中心、按朝向旋转；工作时绕X轴按tick驱动，索引1反转，其余顺转，速度随索引增加并错开120度相位。'),
                             dict(owner='RingStructureVertexBuffer', method='ensureVanillaTerrainUploadedRings / renderTerrainBatched',
                                  finding='原版与着色器兼容两套已上传地形顶点缓存；首用构建，各环绘制前应用独立矩阵。'),
                             dict(owner='AntichristDeferredRenderer', method='renderRingEntryRelativeToCamera',
                                  finding='环进入延后绘制队列，按相机相对坐标绘制。'),
                             dict(owner='ForgeOfAntichristRenderer', method='getViewDistance', finding='此版本返回384格；不是无限视距。')])
    save(LOG / 'forge-research.json', research)
    evidence = dict(passed=True, base_geometry_sha256=sha(SOURCE / 'w03/data.js'),
                    base_geometry_copy_sha256=sha(view / 'data.js'),
                    original_c4_preserved=True, actual_voxel_membership=True,
                    merged_runs_expanded_and_partition_verified=True, totals=totals,
                    moving_quads=moving_quads, fixed_outer_ring_radius=210,
                    dynamic_ring_count=4, pivot_blueprint=core.tolist(), conservative_swept_envelopes=envelopes,
                    dynamic_clearance_fully_accepted=False, game_implemented=False, game_verified=False)
    save(LOG / 'geometry-partition.json', evidence)
    save(OUT / 'manifest.json', dict(title=config['title'], source=str(SOURCE.relative_to(ROOT)),
        source_geometry_sha256=evidence['base_geometry_sha256'], size_xyz=manifest['size'], blocks=manifest['blocks'],
        rings=rings, fixed_ring_radius=210, original_geometry_preserved=True,
        inner_ring_render_translation_xyz=[r['render_translation_xyz'] for r in rings],
        inner_ring_initial_rotation_x_degrees=[r['initial_rotation_x_degrees'] for r in rings],
        status='动态外观预览待审；静态文件仍引用C4，旋转并非NBT可保存的方块运动',
        approved=False, installed=False, game_verified=False, motion_cycle_seconds=360,
        conservative_swept_envelopes=envelopes))
    (OUT / 'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>W03 C5 · 四环绕核运动</title><style>body{max-width:1100px;margin:36px auto;padding:0 24px;background:#111827;color:#eee8fa;font:17px/1.8 system-ui}a{color:#e6c3ff}iframe{width:100%;height:75vh;border:1px solid #534562}p{max-width:950px}</style>
<h1>穹界·虚数锚定环 · C5四环绕核运动</h1>
<p>最大莫比乌斯环固定；四个内环以中央核心为旋转枢轴，按各自倾斜转轴错速、交替反转。C4环心比核心低11格，本候选将四个内环完整上移11格，使环心与核心重合；初始转轴只作有记录的净空修正，具体角度见运动参数。不改变环的尺寸、半扭转或材料。最大环、六矛、晶云与基座不动。</p>
<p><a href="w03/三维评审.html">打开动态预览</a> · <a href="manifest.json">运动参数</a> · <a href="../../logs/w03-ring-motion-c5-20261108/forge-research.json">伪神之煅炉实现核对</a> · <a href="../W03_C4_五环锁芯与立体晶云_20261108/index.html">C4静态原稿</a></p>
<iframe src="w03/三维评审.html" title="W03完整动态预览"></iframe>
<p>预览可暂停、复位和拖动360秒完整周期；隐藏页面暂停。静态景物缓存颜色和深度，动画帧只重绘四环；模型只拆分一次，四环每帧仅改旋转矩阵，最多30帧/秒。此上限是预览调度目标，不是游戏性能承诺。</p>
<p>仅离线动态候选，未批准、未部署。旋转全周期净空、游戏内方块隐藏与恢复、GT成型及客户端性能尚未验收；保守扫掠筛查见运动参数。W02由负责人决定重建，旧稿保留历史。</p></html>''', 'utf8')
    scripts = OUT / '生成脚本'
    scripts.mkdir(exist_ok=True)
    shutil.copy2(__file__, scripts / Path(__file__).name)
    print(json.dumps(dict(passed=True, moving_quads=moving_quads, envelopes=envelopes), ensure_ascii=False))


if __name__ == '__main__':
    main()
