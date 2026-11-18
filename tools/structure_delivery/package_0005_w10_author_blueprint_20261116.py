import base64
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
import sys
from zipfile import ZipFile

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
import w10_base_20261116 as base
import w10_core_20261116 as core
import w10_frame_20261116 as frame


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W10_引力奇点刑架_作者蓝图_A1_20261116'
LOG = ROOT / 'logs/0005-w10-author-blueprint-a1-20261116'
sys.path.insert(0, str(ROOT / 'deliveries/0005_W07_黑渊白花_斜悬方舟轮廓_F1_20261116/生成脚本'))
from build import mesh_part


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def make_materials():
    jar = Path('E:/Prism/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar')
    cached_path = ROOT / 'deliveries/0005_W08_薪炎恒星熔铸炉_作者蓝图_A1_20261116/materials.json'
    cached = json.loads(cached_path.read_text('utf8'))
    specs = [
        ('black_concrete', '深渊黑甲', False, False),
        ('polished_blackstone_bricks', '黑石工业装甲', False, False),
        ('gold_block', '黄金承力梁', False, False),
        ('gtceu:clean_machine_casing', '冷白承重机壳', False, False),
        ('yellow_concrete', '琥珀冷却介质', False, True),
        ('ochre_froglight', '金色发光线圈', False, True),
        ('purple_stained_glass', '紫黑引力束环', True, True),
        ('yellow_stained_glass', '透明液态星核管壁', True, True),
        ('deepslate_tiles', '星骸深板岩', False, False),
        ('gilded_blackstone', '镀金裂岩与机械肋', False, False),
        ('red_stained_glass', '暗红吸积盘外缘', True, True),
        ('sea_lantern', '白热视界', False, True),
    ]
    materials = []
    with ZipFile(jar) as archive:
        for block, label, transparent, emissive in specs:
            if block.startswith('gtceu:'):
                item = next(m.copy() for m in cached if m['state'] == block)
                item.update(label=label, role=label, texture_source=str(cached_path.relative_to(ROOT)))
                materials.append(item)
                continue
            faces, hashes = {}, {}
            for face in ('east', 'west', 'south', 'north', 'down', 'up'):
                texture = block
                if block == 'ochre_froglight':
                    texture += '_top' if face in ('up', 'down') else '_side'
                entry = f'assets/minecraft/textures/block/{texture}.png'
                png = archive.read(entry)
                faces[face] = 'data:image/png;base64,' + base64.b64encode(png).decode()
                hashes[entry] = hashlib.sha256(png).hexdigest()
            state = 'minecraft:' + block + ('[axis=y]' if block == 'ochre_froglight' else '')
            materials.append(dict(state=state, label=label, role=label, faces=faces,
                transparent=transparent, emissive=emissive,
                source=dict(archive=str(jar), png_sha256=hashes, texture_mode='原生PNG，逐格重复，无额外染色')))
    save(OUT / 'materials.json', materials)
    return materials


def export_nbt(keys, states, size, materials):
    w, h, d = size
    header, _ = headers([m['state'] for m in materials], (h, d, w), len(keys))
    record = np.frombuffer(RECORD, np.uint8)
    with gzip.open(OUT / 'W10-引力奇点刑架-A1.nbt', 'wb', compresslevel=6) as handle:
        handle.write(header)
        for start in range(0, len(keys), 65536):
            current = keys[start:start + 65536]
            raw = np.tile(record, (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current // (w * d), current // w % d
            rows['state'] = states[start:start + 65536].astype(np.int32) - 1
            handle.write(raw.tobytes())
        handle.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    materials = make_materials()
    parts, notes = [], []
    for module, section in ((base, 'base'), (frame, 'towers'), (core, 'core')):
        current, sampling = module.build()
        for part in current:
            part.metadata.setdefault('section', 'dome' if part.name.startswith(('dome_', 'zenith_', 'hammer_')) else section)
        parts.extend(current)
        notes.extend(sampling)
        print(f'{module.__name__}: {len(current)}构件，{sum(len(p.p) for p in current):,}构件占格', flush=True)

    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size

    def encode(points):
        return ((points[:, 1].astype(np.int64) - low[1]) * d + points[:, 2] - low[2]) * w + points[:, 0] - low[0]

    part_keys = [encode(p.p) for p in parts]
    all_keys = np.concatenate(part_keys)
    all_states = np.concatenate([p.states for p in parts])
    keys, chosen = np.unique(all_keys[::-1], return_index=True)
    states = all_states[len(all_states) - chosen - 1]
    del all_keys, all_states, chosen

    intersections = []
    for index, moving in enumerate(parts):
        if 'motion_speed' not in moving.metadata:
            continue
        lo, hi = moving.p.min(0), moving.p.max(0)
        for other_index, fixed in enumerate(parts):
            if index == other_index or ('motion_speed' in fixed.metadata and other_index < index):
                continue
            if np.any(fixed.p.max(0) < lo) or np.any(fixed.p.min(0) > hi):
                continue
            selected = np.all((fixed.p >= lo) & (fixed.p <= hi), axis=1)
            overlap = np.intersect1d(part_keys[index], part_keys[other_index][selected], assume_unique=True)
            if len(overlap):
                intersections.append(dict(moving=moving.name, other=fixed.name, reference_pose_blocks=len(overlap),
                    example_blueprint_xyz=[int(overlap[0] % w + low[0]), int(overlap[0] // (w * d) + low[1]), int(overlap[0] // w % d + low[2])]))
    del part_keys
    print(f'参考姿态运动构件交集：{len(intersections)}组', flush=True)

    archive, packed, quads = {}, [], 0
    for index, part in enumerate(parts):
        archive[part.name + '_xyz'], archive[part.name + '_materials'] = part.p, part.states
        item, count = mesh_part(part, materials)
        packed.append(item)
        quads += count
        print(f'表面 {index + 1}/{len(parts)} {part.name} {count:,}', flush=True)

    def view(label, direction, **options):
        return dict(label=label, direction=direction, **options)

    views = dict(
        front=view('整体前斜视', [-1, .8, -1.25]), back=view('整体后斜视', [1, .8, 1.25]),
        frontOrtho=view('正面', [0, .001, -1]), backOrtho=view('背面', [0, .001, 1]),
        side=view('侧面', [1, .001, 0]), top=view('俯视', [0, 1, .001]),
        core=view('奇点与双环', [-.8, .6, -1.2], center=[0, 215, 0], half=[355, 180, 355]),
        base=view('八角深井', [-.8, 1.3, -1.1], center=[0, 70, 0], half=[490, 100, 490]),
        towers=view('四象限塔桥', [-1, .65, -1.3], center=[0, 210, 0], half=[470, 155, 470]),
        dome=view('天穹与重锤', [-1, .35, -1.1], center=[0, 380, 0], half=[420, 100, 420]),
        blocks=view('逐格像素', [-.7, 1, -1], center=[32, 64, -350], half=[9, 8, 9]))
    interface_rule = '仅主控固定，其余全部实体方块可随时替换合法通用接口，位置与朝向由玩家选择。'
    data = dict(machine_id='W10', title='岩／星之律者·引力奇点刑架', candidate='A1',
        sizeXYZ=size, size=size, bounds=dict(min=low.tolist(), max=high.tolist()),
        blueprint_to_export_offset_xyz=(-low).tolist(), nominal_size_wdh=[949, 949, 444],
        core_center=[0, 222, 0], views=views, runtime_voltage='CIV', research='RN-GSF',
        interface_rule=interface_rule, controller_blueprint=None, controller_status='待指定',
        effects=dict(beam_origins=[[400, 180, 0], [0, 180, 400], [-400, 180, 0], [0, 180, -400]],
                     void_radius=25, void_floor_radius=24))
    notes.extend([
        '本轮依据负责人消息制作W10候选；MAX之后、VII型文明为设计阶段与叙事描述，现有运行身份w10_gravitational_singularity_forge、CIV、RN-GSF保持。',
        'X/Z=-474..474共有949格；Y=0..444包含445层。斜桩底箍和厚拱超出该端点范围，完整占格由实际包围盒计算。',
        '八桩精确示例中心(±440,±180)与互换坐标距中心约475.4格，与速查表半径440并存；本稿采用精确坐标。',
        '原文人物称谓尚未完成官方归属核验，本稿以岩／星、伊甸之星与引力拘束的视觉题材命名。',
        '原文四塔集中接口由负责人通用接口规则覆盖，未设置专用仓槽；本轮主控位置待指定。',
        '黑金60%、冷白25%、发光15%为原文目标比例；材料清单提供实际去重数量。新增注册方块与新画贴图均为0。',
        '独立构件完整保留。NBT同格按基座、外围、核心及各模块内部顺序后写覆盖；NPZ保留每件全部原始占格。',
        '运动构件交集为参考姿态整数坐标交集，完整旋转过程中仍可能相交；保留双环与桥梁原位供外观评审。',
        '网页引力透镜作用于星点背景，建筑方块未使用屏幕折射。网页特效与旋转均为演示，NBT保存参考姿态。',
    ])
    geometry = dict(candidate='A1', stage='作者蓝图完整方块预览待审',
        nominal_size_wdh=[949, 949, 444], actual_size_xyz=size, actual_size_wdh=[w, d, h], bounds=data['bounds'],
        blocks=len(keys), footprint_area=w * d, bounding_box_volume=w * d * h, actual_height=h,
        unique_block_types=len(np.unique(states)), source_component_blocks=sum(len(p.p) for p in parts),
        overlap_extra_memberships=sum(len(p.p) for p in parts) - len(keys), surface_quads=quads,
        interface_rule=interface_rule, controller_blueprint=None,
        material_counts={m['state']: int((states == i + 1).sum()) for i, m in enumerate(materials)},
        components={p.name: dict(label=p.label, blocks=len(p.p), bounds=dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist()), metadata=p.metadata) for p in parts},
        source_notes=notes, reference_pose_moving_intersections=intersections,
        instance_access=False, appearance_approved=False, game_code_modified=False, jar_built=False, game_verified=False)
    config = dict(data=data, audit=dict(viewer_rendered_quads=quads, blocks=len(keys)), materials=materials, parts=packed)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT / 'data.js').write_text('window.W10_STATIC_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
    np.savez_compressed(OUT / '原案构件数据.npz', **archive)
    export_nbt(keys, states, size, materials)
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    save(OUT / 'conflicts.json', dict(source='本轮负责人消息及完整方块取样', notes=notes, reference_pose_moving_intersections=intersections))
    rows = ''.join('<li>' + escape(note) + '</li>' for note in notes)
    (OUT / '原文与取样.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>W10坐标与取样</title><style>body{max-width:1000px;margin:40px auto;background:#13151c;color:#eee;font:16px/1.8 system-ui}a{color:#e2bc6b}li{margin:16px 0}</style><a href="index.html">返回预览</a><h1>W10坐标与取样</h1><p>来源为本轮负责人消息，以下为坐标摘录及整数格取样说明。实际宽深高：' + '×'.join(map(str, [w, d, h])) + '。</p><ol>' + rows + '</ol>', 'utf8')
    for name in ['w10_common_20261116.py', 'w10_base_20261116.py', 'w10_frame_20261116.py', 'w10_core_20261116.py', Path(__file__).name]:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    files = ['data.js', 'materials.json', 'geometry.json', 'conflicts.json', '原案构件数据.npz', 'W10-引力奇点刑架-A1.nbt']
    manifest = dict(machine='W10', candidate='A1', status='独立方块预览与NBT，外观待审', actual_size_wdh=[w, d, h], blocks=len(keys),
        files={name: dict(bytes=(OUT / name).stat().st_size, sha256=hashlib.sha256((OUT / name).read_bytes()).hexdigest()) for name in files})
    save(OUT / 'manifest.json', manifest)
    print(json.dumps(dict(size_wdh=[w, d, h], parts=len(parts), blocks=len(keys), quads=quads)), flush=True)


if __name__ == '__main__':
    main()
