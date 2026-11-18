import base64
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
from w13_tv_common_20261117 import ROOT, OUT, LOG, EYE, CONTROLLER, materials
from w13_tv_body_20261117 import build_body, build_screen
from w13_tv_cables_20261117 import build_cables


NBT_FILE = 'W13-侵蚀之律者电视本体-T1.nbt'
REFERENCES = ROOT / 'deliveries/0005_W13_侵蚀电视原作参考_R1_20261117'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def export_nbt(keys, states, size, palette):
    w, h, d = size
    header, _ = headers([m['state'] for m in palette], (h, d, w), len(keys))
    with gzip.open(OUT / NBT_FILE, 'wb', compresslevel=6) as stream:
        stream.write(header)
        for start in range(0, len(keys), 65536):
            current = keys[start:start + 65536]
            raw = np.tile(np.frombuffer(RECORD, np.uint8), (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current // (w * d), current // w % d
            rows['state'] = states[start:start + 65536].astype(np.int32) - 1
            stream.write(raw.tobytes())
        stream.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    palette = materials()
    body, screen, cables = build_body(), build_screen(), build_cables()
    parts = body + screen + cables
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    values = np.concatenate([p.states for p in parts])
    source_blocks = len(keys)
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(values) - chosen - 1
    values, owners = values[chosen], owners[chosen]
    xyz = np.c_[keys % w, keys // (w * d), keys // w % d].astype(np.int32)
    np.savez_compressed(OUT / '完整整数格模型.npz', xyz=xyz, states=values, origin=low, size=size, owners=owners)
    source_parts = {}
    for part in parts:
        source_parts[part.name + '_xyz'] = part.p
        source_parts[part.name + '_states'] = part.states
    np.savez_compressed(OUT / '原始完整分件.npz', **source_parts)
    owner_counts = np.bincount(owners, minlength=len(parts))
    packed, components, quads = [], [], 0
    for index, part in enumerate(parts):
        item, count = mesh_part(part, palette)
        blocks = int(owner_counts[index])
        item.update(blocks=blocks, source_blocks=len(part.p), modelId=part.metadata['group'])
        packed.append(item)
        quads += count
        components.append(dict(id=part.name, label=part.label, modelId=part.metadata['group'],
            source_blocks=len(part.p), blocks=blocks, shared_cells_overwritten=len(part.p) - blocks,
            bounds=dict(min=part.p.min(0).tolist(), max=part.p.max(0).tolist()), metadata=part.metadata))
        print(f'表面{index + 1}/{len(parts)} {part.name}：{count:,}', flush=True)
    notes = [
        '主体以官方短片《因你而在的故事》的侵蚀之律者为依据：中央小眼屏、宽厚深机壳、侧面多层折板与下方错落垂挂机匣。',
        '屏幕保留粉红尖角眼形、同心圆与左右四芒星。巨眼为屏幕表面逐格图案；实际尺寸由完整实体坐标求得。',
        '粗黑电缆采用重力垂弧与回勾，插头用分节套圈收边。机匣、线缆和前端检修端子共同构成下方悬垂轮廓。',
        '正常机壳使用深色与灰色金属，粉红集中于显示像素和少量状态标记；原片绿色环境照明不作为整机固有涂装。',
        '全部实体为真实整数格，表面使用原生GT、HK3GTL与原版像素贴图。无遮挡背面、完整顶部与内部构造缺少原作画面，对应壳面按可见结构补全。',
        '唯一主控位于前端主缆检修端子，源坐标(0,16,472)，朝南；其余实体格均可由玩家自由替换为合法接口。',
        '网页运行演示仅表现屏幕亮度脉动与像素故障，外壳、下挂机匣及线缆位置固定；NBT保存静态完整实体。',
        '本轮为T1外观待审稿。负责人已选定原作整体形制，正式蓝图接入、CEV规模与材料种类要求另行确认。原A1方案停用，保留历史记录。',
    ]
    views = dict(
        eye=dict(label='眼屏近景', center=EYE.tolist(), half=[170, 105, 12], direction=[0, 0, 1]),
        shell=dict(label='深壳侧板', center=[420, 525, -5], half=[30, 150, 230], direction=[1, .2, .6]),
        pixels=dict(label='真实像素方块', center=[154, 530, 265], half=[20, 20, 20], direction=[-.4, .3, 1]),
        controller=dict(label='前端唯一主控', center=CONTROLLER.tolist(), half=[46, 30, 45], direction=[-.3, .55, 1]),
        cables=dict(label='下挂机匣与线缆', center=[0, 180, 20], half=[540, 210, 460], direction=[-.7, .35, 1]),
    )
    models = [dict(id=group, label=title, title=title, features=features, views=views) for group, title, features in [
        ('tv', '深机壳与层叠折板', [notes[0], notes[3], notes[4]]),
        ('screen', '粉红侵蚀眼屏', [notes[1], notes[6]]),
        ('cables', '悬垂机匣与主缆', [notes[2], notes[5]]),
    ]]
    data = dict(title='W13 侵蚀之律者电视本体', candidate='T1', nbt_file=NBT_FILE,
        bounds=dict(min=low.tolist(), max=high.tolist()), sizeXYZ=size, total_blocks=len(keys),
        models=models, views=views, design=notes, effects=dict(eye_center=EYE.tolist(), eye_radius=50))
    payload = json.dumps(dict(data=data, materials=palette, parts=packed), ensure_ascii=False, separators=(',', ':')).encode()
    (OUT / 'data.js').write_text('window.W13_VOXEL_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(payload, compresslevel=6)).decode()) + ';\n', 'utf8')
    material_totals = np.bincount(values, minlength=len(palette) + 1)
    counts = {m['state']: int(material_totals[index + 1]) for index, m in enumerate(palette)}
    reference_data = json.loads((REFERENCES / 'references.json').read_text('utf8'))
    sources = dict(reference_directory=str(REFERENCES), reference_index=str(REFERENCES / 'references.json'),
        source=reference_data['source'], references=reference_data['references'],
        counting=reference_data['counting'], missing_views=reference_data['missing_views'],
        modeled_from=['V01', 'V02', 'V03', 'V04', 'V05', 'V06'],
        completion='不可观察的背面、顶部与内部按可见厚壳和折板关系补全；具体尺寸为方块稿推定。',
        shape_selection_approved=True, appearance_approved=False,
        previous_candidate=dict(id='W13 A1', status='负责人否定并停用，历史文件保留'))
    geometry = dict(machine='W13', candidate='T1', status='原作整体形制已选定，电视本体外观待审',
        recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        actual_size_wdh=[w, d, h], bounds=data['bounds'], blocks=len(keys),
        source_component_voxels=source_blocks, shared_component_cells=source_blocks - len(keys),
        surface_quads=quads, components=components, material_counts=counts,
        footprint_area=w * d, bounding_box_volume=w * d * h, actual_height=h,
        palette_types=len(palette), unique_block_types=int(np.count_nonzero(material_totals[1:])),
        non_vanilla_percent=100 * sum(n for state, n in counts.items() if not state.startswith('minecraft:')) / len(keys),
        controller=dict(source_xyz=CONTROLLER.tolist(), export_xyz=(CONTROLLER - low).tolist(), facing='south', preview_state='minecraft:redstone_block'),
        screen=dict(center=EYE.tolist(), radius=50, effect_scope='网页屏幕演示'), source_notes=notes,
        overlap_policy='完整模型与NBT后写构件优先；原始分件和网页保留各件完整整数格。',
        runtime=dict(controller='hk3gtl:w13_self_computing_research_mother', tier='CEV', tier_index=30, research='RN-ASR', formal_blueprint_present=False),
        scale_comparison=dict(status='CEV递增规模与材料种类要求待确认', exception_approved=False, w09_w11_exceptions_apply=False),
        shape_selection_approved=True, appearance_approved=False, game_code_modified=False,
        jar_built=False, installed=False, game_started=False, game_verified=False, scores_changed=False)
    baseline = dict(footprint_area=900601, bounding_box_volume=441313404, actual_height=636, blocks=23541415, unique_block_types=58)
    geometry['scale_comparison'].update(source='项目既有CEV低阶比较记录', metrics={
        key: dict(candidate=geometry[key], recorded_lower_tier_max=value, greater=geometry[key] > value)
        for key, value in baseline.items()})
    for name, value in [('geometry.json', geometry), ('materials.json', palette), ('sources.json', sources)]:
        save(OUT / name, value)
    export_nbt(keys, values, size, palette)
    scripts = ['w13_tv_common_20261117.py', 'w13_tv_body_20261117.py', 'w13_tv_cables_20261117.py', Path(__file__).name]
    for name in scripts:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    save(LOG / 'generation.json', dict(**geometry, command=[sys.executable, str(Path(__file__))],
        input_files={name: digest(ROOT / 'tools/structure_delivery' / name) for name in scripts},
        reference_index_sha256=digest(REFERENCES / 'references.json'),
        nbt=dict(file=NBT_FILE, bytes=(OUT / NBT_FILE).stat().st_size, sha256=digest(OUT / NBT_FILE))))
    files = [p for p in OUT.rglob('*') if p.is_file() and p.name != 'manifest.json']
    save(OUT / 'manifest.json', dict(machine='W13', candidate='T1', actual_size_wdh=[w, d, h],
        blocks=len(keys), shape_selection_approved=True, appearance_approved=False,
        files={p.relative_to(OUT).as_posix(): dict(bytes=p.stat().st_size, sha256=digest(p)) for p in files}))
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), parts=len(parts),
        materials=geometry['unique_block_types'], quads=quads), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
