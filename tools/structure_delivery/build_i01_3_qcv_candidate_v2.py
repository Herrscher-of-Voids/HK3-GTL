from __future__ import annotations

import collections
import copy
import hashlib
import importlib
import json
import math
import re
import shutil
import sys
from pathlib import Path

import nbtlib


ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = ROOT / 'deliveries/I01-2_崩坏能采集塔固态_QSV主塔与晶体工段_V2_20261026'
SOURCE_NBT = PREVIOUS / 'i01-2-qsv-solid-collector-v2.nbt'
SOURCE_JSON = PREVIOUS / '设计与检查.json'
OUT = ROOT / 'deliveries/I01-3_崩坏能采集塔气态_QCV四向吸气与中央集流塔_V2_20261026'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
import build_i01_2_qsv_candidate as previous_builder
from material_resources import Resources

PREVIOUS_SHA256 = hashlib.sha256(SOURCE_NBT.read_bytes()).hexdigest()
previous_builder.SOURCE_NBT = SOURCE_NBT
previous_builder.SOURCE_JSON = SOURCE_JSON
previous_builder.SOURCE_SHA256 = PREVIOUS_SHA256
QCV = 'hk3gtl:voltage_machine_casing_qcv'
M = previous_builder.M


def add_qcv_collector(candidate) -> None:
    # A broad QCV plenum rises directly from the new QSV tower's roof.
    for x in range(11, 32):
        for z in range(11, 32):
            candidate.put(x, 81, z, QCV)
    for y in range(82, 103):
        casing = QCV if y in (84, 88, 92, 96, 100, 102) else M['robust']
        for offset in range(11, 32):
            for side in ('north', 'south', 'west', 'east'):
                if side == 'north':
                    pos = (offset, y, 11)
                elif side == 'south':
                    pos = (offset, y, 31)
                elif side == 'west':
                    pos = (11, y, offset)
                else:
                    pos = (31, y, offset)
                frame = offset in (11, 12, 13, 14, 15, 16, 26, 27, 28, 29, 30, 31)
                panel = 89 <= y <= 97 and 18 <= offset <= 24
                if panel:
                    state = M['vent'] if offset == 21 and y in (91, 95) else M['glass']
                else:
                    state = QCV if frame or casing == QCV else M['robust']
                candidate.put(*pos, state)

    candidate.ring(10, 32, 10, 32, 103, QCV)
    candidate.ring(11, 31, 11, 31, 103, QCV)
    for offset in range(10, 33):
        candidate.put(offset, 103, 21, QCV)
        candidate.put(21, 103, offset, QCV)
    for y in range(82, 103):
        candidate.put(20, y, 21, M['pipe'])
        candidate.put(22, y, 21, M['pipe'])
    for y in (88, 96, 102):
        candidate.put(21, y, 21, M['gear'])
    candidate.put(21, 104, 21, M['vent'])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    predecessor, source_meta = previous_builder.load_predecessor()
    if len(predecessor) != 21030 or predecessor.get((21, 5, 14)) != previous_builder.DIAMOND:
        raise ValueError('I01-2 V2 candidate base contract changed')
    if sum(state == previous_builder.PORT for state in predecessor.values()) != 6:
        raise ValueError('I01-2 V2 candidate interface count changed')

    data = copy.deepcopy(source_meta)
    data.update({
        'key': 'I01-3',
        'name': 'i01-3-qcv-gas-collector-v2',
        'title': '3阶崩坏能采集塔·气态',
        'size': [43, 105, 62],
        'controller': [21, 5, 14],
        'paste_anchor': [21, 5, 14],
        'schematic_offset': [-21, -5, -14],
        'description': '完整承接I01-2 V2液态塔、QSV结晶主塔、肩舱和后处理厂房；在QSV主塔上方新增四面进气的QCV高压集流舱，形成更高一级的气态处理主体。',
        'brief': {
            'id': 'I01-3', 'title': '3阶崩坏能采集塔·气态',
            'minimum_wdh': [37, 37, 45],
            'form': 'HBV液态采集塔、QSV高位结晶主塔与后处理厂房；其上承接四面吸气的QCV气态集流舱',
            'flow': '液态凝结→固态压榨分选→四向气态吸入→中央高位集流',
        },
        'construction_notes': {
            'orientation': 'X向东、Y向上、Z向南；主控与继承接口朝北（-Z）。',
            'origin': [0, 0, 0], 'paste_anchor': [21, 5, 14],
            'schematic_offset': [-21, -5, -14],
            'stage_alignment': '以I01-2 V2候选坐标为暂定工作底图；完整继承前阶实体，主控世界锚点不变。此继承不代表I01-2候选已获批准。',
            'status': '独立候选；待负责人审核；未批准、未接入Pattern或实例。',
        },
        'zones': copy.deepcopy(source_meta['zones']) + [
            {'name': '四面百叶吸气与QCV中央集流头', 'kind': 'gas_collector',
             'min': [10, 81, 10], 'max': [32, 104, 32], 'pos': [21, 92, 21],
             'role': '四向百叶吸入气态崩坏能，在原中央竖轴内压送并完成高位集流',
             'service_face': '集流头四面检修百叶'},
        ],
        'paths': copy.deepcopy(source_meta['paths']) + [
            {'name': 'QCV集流舱环形检修步道', 'min': [12, 83, 12], 'max': [30, 83, 30]},
        ],
        'links': copy.deepcopy(source_meta['links']) + [
            {'from': '四面百叶气态吸口', 'to': '中央高位集流轴', 'material': M['pipe'],
             'route': [[21, 82, 11], [21, 92, 21]]},
        ],
        'approval': 'V2独立候选待负责人审核；基于未批准的I01-2 V2制作，不代表I01-2已获批准；未接入正式Pattern或实例。',
    })
    data['ports'] = copy.deepcopy(source_meta['ports'])

    candidate = previous_builder.Candidate(dict(predecessor), tuple(data['size']))
    add_qcv_collector(candidate)
    blocks = [{'pos': list(pos), 'state': state} for pos, state in sorted(candidate.blocks.items())]
    data['blocks'] = blocks
    if any(candidate.blocks.get(pos) != state for pos, state in predecessor.items()):
        raise AssertionError('inherited I01-2 V2 candidate block changed')
    if candidate.blocks[(21, 5, 14)] != previous_builder.DIAMOND:
        raise AssertionError('controller marker moved or changed')
    if previous_builder.connected_count(candidate.blocks) != len(candidate.blocks):
        raise AssertionError('candidate structure is not six-way connected')
    for port in data['ports']:
        if candidate.blocks.get(tuple(port['pos'])) != previous_builder.PORT:
            raise AssertionError(f'inherited interface changed: {port}')

    mirror_errors = [(x, y, z, state, candidate.blocks.get((42 - x, y, z)))
                     for (x, y, z), state in candidate.blocks.items()
                     if candidate.blocks.get((42 - x, y, z)) != state]
    if mirror_errors:
        raise AssertionError(f'left-right symmetry failed: {mirror_errors[:5]}')

    data['role_materials'] = {state: [state] for state in sorted(set(candidate.blocks.values()))}
    size_check = previous_builder.size_baseline.require(data)
    counts = collections.Counter(candidate.blocks.values())
    stage_counts = collections.Counter(candidate.added.values())
    if stage_counts[QCV] <= max(count for state, count in stage_counts.items() if state != QCV):
        raise AssertionError('QCV must be the most-used single material in the added I01-3 stage')
    states, groups, hashes = previous_builder.legacy_builder.export(data, OUT)
    schem_path = OUT / (data['name'] + '.schem')
    schem = nbtlib.load(schem_path)
    schem['Offset'] = nbtlib.IntArray([-21, -5, -14])
    schem.save(schem_path, gzipped=True)
    if list(map(int, nbtlib.load(schem_path)['Offset'])) != [-21, -5, -14]:
        raise AssertionError('Sponge v2 anchor offset roundtrip failed')
    hashes['schem'] = hashlib.sha256(schem_path.read_bytes()).hexdigest()

    resources = Resources(instance=INSTANCE, project_resources=ROOT / 'src/main/resources')
    try:
        materials = [resources.material(state) for state in states]
        if not all(material.get('complete_cube') for material in materials):
            raise AssertionError('one or more selected materials are not full cubes')
        asset_sources = dict(resources.sources)
    finally:
        resources.close()
    previous_builder.legacy_builder.render(data, materials, OUT)

    palette = dict(sorted(counts.items()))
    bounds = [[min(pos[i] for pos in candidate.blocks), max(pos[i] for pos in candidate.blocks)] for i in range(3)]
    audit = {
        'source_predecessor': {
            'path': str(SOURCE_NBT.relative_to(ROOT)), 'sha256': PREVIOUS_SHA256,
            'blocks': len(predecessor), 'unchanged_blocks': len(predecessor),
            'controller': [21, 5, 14], 'ports': [p['pos'] for p in data['ports']],
            'approval_state': 'I01-2 V2 remains unapproved; inherited here only as a reversible working candidate.',
        },
        'added_blocks': len(candidate.added), 'block_count': len(blocks),
        'unique_material_count': len(palette), 'palette': palette,
        'stage_primary_casing': {
            'voltage': 'QCV', 'block': QCV, 'added_count': stage_counts[QCV],
            'added_block_count': len(candidate.added),
            'added_share': round(stage_counts[QCV] / len(candidate.added), 4),
            'rank': 1, 'visual_identity': 'QSV结晶主塔上方的四面QCV气态集流舱',
        },
        'actual_bounds_xyz': bounds, 'actual_size_wdh': size_check['actual_xyz'],
        'actual_volume': math.prod(size_check['actual_xyz']), 'size_baseline': size_check,
        'connected_blocks': len(blocks),
        'controller_centering': {'width': 43, 'center_x_0based': 21, 'controller': [21, 5, 14], 'passed': True},
        'left_right_symmetry': {'axis': 'X=21', 'exact': True, 'mismatches': 0},
        'hashes': {'source_nbt': PREVIOUS_SHA256, **hashes}, 'asset_sources': asset_sources,
        'checks': [
            'I01-2 V2工作底图全部方块、位置与状态原样保留；该底图仍待负责人批准。',
            'QCV机壳是新增阶段数量最多的单一材料，构成QSV结晶主塔上方的气态集流主体。',
            '只在既有QSV塔冠上方新增QCV高位气态集流舱，不移动主控或六个接口。',
            '主控仍在宽43的中心第22格，蓝图坐标[21,5,14]。',
            '新增集流头关于X=21镜像，全部方块六向连通。',
            '实际包围盒逐轴达到I01-3的规划下限。',
            'NBT与Sponge v2逐格导出一致；粘贴锚点偏移[-21,-5,-14]。',
            '全部材料来自指定增强版实例与项目资源，且解析为完整立方体。',
            '新增项目自有方块仅使用QCV电压机壳。',
        ],
        'not_verified': [
            'I01-3 V2外观待负责人审核。',
            'I01-2底图本身未获批准；I01-3候选不得视作替代批准。',
            '未接入正式Pattern、注册接口能力或配方；未进行游戏内成型、运行与生存获取验证。',
            'I26起电压递增硬规则不追溯作为I01-3规模门槛。',
            '工艺流线仅表达建筑分区，不证明游戏运行逻辑已接通。',
        ],
        'approval': data['approval'],
    }
    previous_builder.write_bundle(data, audit, OUT, states, groups, materials)
    (OUT / '设计与检查.json').write_text(json.dumps({'data': {k: v for k, v in data.items() if k != 'blocks'}, 'audit': audit},
        ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps({
        'id': 'I01-3', 'version': 'V2', 'status': 'candidate_pending_visual_approval',
        'title': data['title'], 'target_voltage': 'QCV', 'size_xyz': data['size'],
        'predecessor': str(SOURCE_NBT.relative_to(ROOT)), 'predecessor_sha256': PREVIOUS_SHA256,
        'predecessor_approval': 'pending', 'controller': data['controller'],
        'added_blocks': len(candidate.added), 'blocks': len(blocks),
        'palette_count': len(palette), 'hashes': hashes,
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    shutil.copy2(PREVIOUS / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (PREVIOUS / '三维评审.html').read_text(encoding='utf-8')
    page = re.sub(r'<title>.*?</title>', '<title>I01-3 气态崩坏能采集塔 · QCV集流舱候选 V2</title>', page, count=1)
    page = re.sub(r'<h1>.*?</h1>', '<h1>I01-3 · 崩坏能采集塔 · 气态</h1>', page, count=1)
    size_text = (f'{data["size"][0]}×{data["size"][2]}×{data["size"][1]}（宽×长×高） · '
                 f'{len(blocks):,}个实体块（含前阶） · 待审候选')
    page = re.sub(r'(<h1>.*?</h1><span>).*?(</span>)',
                  lambda match: match.group(1) + size_text + match.group(2), page, count=1)
    page = page.replace('id="layerValue">80', 'id="layerValue">104')
    page = page.replace('id="layer" type="range" min="0" max="80" value="80"',
                        'id="layer" type="range" min="0" max="104" value="104"')
    page = re.sub(r'<details open><summary>阶段扩建方案</summary>.*?</details>',
        '<details open><summary>气态阶段扩建方案</summary>'
        '<p>完整承接I01-2 V2的HBV液态塔、QSV高位结晶主塔、双侧肩舱与后处理厂房。在QSV塔冠上增设四面格栅进气的QCV高压集流舱；双路压送管沿舱体内壁汇入中央压缩节点，四面吸口与承压框架属于同一主体。</p>'
        '<p>结构宽度维持43格，主控为中心第22格，蓝图坐标[21,5,14]；前阶主控标记、六接口及所有建筑方块保持原位。</p>'
        f'<p>本阶段新增{len(candidate.added):,}块中，QCV机壳{stage_counts[QCV]:,}块，为新增数量最多的单一材料；它承担整机最高阶段的视觉识别。主控仍位于第22格、蓝图坐标[21,5,14]，六接口与所有前阶方块保持原位。</p>'
        '<p class="muted">这是基于未批准I01-2 V2的可回退候选；不代表I01-2或I01-3获批。未替换正式Pattern或游戏实例。</p></details>', page, count=1)
    page = re.sub(r'<details open><summary>范围说明</summary>.*?</details>',
        '<details open><summary>范围说明</summary><p>I01-3按I01四阶段累计扩建；I26起的电压递增硬规则不追溯套用于本结构。I01-2底图尚待负责人批准。</p></details>', page, count=1)
    page = page.replace('i01-2-qsv-solid-collector-v2.nbt', data['name'] + '.nbt')
    page = page.replace('i01-2-qsv-solid-collector-v2.schem', data['name'] + '.schem')
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    shutil.copy2(OUT / '三维评审.html', OUT / '设计说明.html')

    print(json.dumps({
        'out': str(OUT), 'blocks': len(blocks), 'added_blocks': len(candidate.added),
        'materials': len(palette), 'bounds_xyz': size_check['actual_xyz'],
        'volume': audit['actual_volume'], 'connected': audit['connected_blocks'],
        'controller': data['controller'], 'ports': len(data['ports']), 'hashes': hashes,
        'preview': str(OUT / '三维评审.html'), 'image': str(OUT / '等轴预览.png'),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
