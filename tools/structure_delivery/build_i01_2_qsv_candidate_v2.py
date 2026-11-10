from __future__ import annotations

import base64
import collections
import copy
import gzip
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import nbtlib


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'deliveries/多方块确认归档/20261025_230645_502584_I01-1_HBV液态采集塔V3_已确认'
SOURCE_DIR = ARCHIVE / 'I01-1'
SOURCE_NBT = SOURCE_DIR / 'i01-1-hbv-liquid-collector-v3-interface-ribs.nbt'
SOURCE_JSON = SOURCE_DIR / '设计与检查.json'
SOURCE_SHA256 = '2d42ff49231b53679ff779ab7b9e1d1b5956a5db9f221655e734c8606f0b7fd3'
OUT = ROOT / 'deliveries/I01-2_崩坏能采集塔固态_QSV主塔与晶体工段_V2_20261026'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
PORT = 'hk3gtl:industrial_port_casing'
DIAMOND = 'minecraft:diamond_block'
HBV = 'hk3gtl:voltage_machine_casing_hbv'
QSV = 'hk3gtl:voltage_machine_casing_qsv'
M = {
    'robust': 'gtceu:robust_machine_casing',
    'solid': 'gtceu:solid_machine_casing',
    'clean': 'gtceu:clean_machine_casing',
    'glass': 'gtceu:tempered_glass',
    'pipe': 'gtceu:steel_pipe_casing',
    'gear': 'gtceu:tungstensteel_gearbox',
    'grate': 'gtceu:assembly_line_grating',
    'vent': 'gtceu:computer_heat_vent',
    'power': 'gtceu:high_power_casing',
}

sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
sys.path.insert(1, str(ARCHIVE / '生成依赖'))
import build_redesign69 as legacy_builder
import structure_size_baseline as size_baseline
from material_resources import Resources

legacy_builder.ROOT = ROOT
size_baseline.SOURCE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html'


class Candidate:
    def __init__(self, blocks: dict[tuple[int, int, int], str], size: tuple[int, int, int]):
        self.blocks = blocks
        self.original = dict(blocks)
        self.size = size
        self.added: dict[tuple[int, int, int], str] = {}

    def put(self, x: int, y: int, z: int, state: str, mirrored: bool = False) -> None:
        positions = {(x, y, z)}
        if mirrored and x != 21:
            positions.add((42 - x, y, z))
        for pos in positions:
            if not all(0 <= pos[i] < self.size[i] for i in range(3)):
                raise ValueError(f'out of bounds: {pos} {state}')
            if pos in self.original:
                raise ValueError(f'predecessor collision: {pos} {self.original[pos]} -> {state}')
            old = self.added.get(pos)
            if old is not None and old != state:
                raise ValueError(f'new-block collision: {pos} {old} -> {state}')
            self.added[pos] = state
            self.blocks[pos] = state

    def line(self, a, b, state: str, mirrored: bool = False) -> None:
        x0, y0, z0 = a
        x1, y1, z1 = b
        steps = max(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
        for i in range(steps + 1):
            t = 0 if steps == 0 else i / steps
            self.put(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t),
                     round(z0 + (z1 - z0) * t), state, mirrored)

    def ring(self, x0, x1, z0, z1, y, state: str, mirrored: bool = False) -> None:
        for x in range(x0, x1 + 1):
            self.put(x, y, z0, state, mirrored)
            self.put(x, y, z1, state, mirrored)
        for z in range(z0 + 1, z1):
            self.put(x0, y, z, state, mirrored)
            self.put(x1, y, z, state, mirrored)

    def shell(self, x0, x1, y0, y1, z0, z1, state: str, mirrored: bool = False) -> None:
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                self.put(x, y0, z, state, mirrored)
                self.put(x, y1, z, state, mirrored)
        for y in range(y0 + 1, y1):
            for x in range(x0, x1 + 1):
                self.put(x, y, z0, state, mirrored)
                self.put(x, y, z1, state, mirrored)
            for z in range(z0 + 1, z1):
                self.put(x0, y, z, state, mirrored)
                self.put(x1, y, z, state, mirrored)


def state_name(block) -> str:
    name = str(block['Name'])
    props = block.get('Properties')
    if props:
        return name + '[' + ','.join(f'{k}={props[k]}' for k in sorted(props)) + ']'
    return name


def load_predecessor() -> tuple[dict, dict]:
    digest = hashlib.sha256(SOURCE_NBT.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(f'I01-1 V3 source hash changed: {digest}')
    nbt = nbtlib.load(SOURCE_NBT)
    size = tuple(map(int, nbt['size']))
    blocks = {}
    for block in nbt['blocks']:
        pos = tuple(map(int, block['pos']))
        if pos in blocks:
            raise ValueError(f'duplicate predecessor position: {pos}')
        blocks[pos] = state_name(nbt['palette'][int(block['state'])])
    return blocks, json.loads(SOURCE_JSON.read_text(encoding='utf-8'))['data']


def add_shoulder_cassettes(candidate: Candidate) -> None:
    for y in (8, 14, 22):
        candidate.ring(3, 11, 16, 28, y, QSV, mirrored=True)
    for x in (3, 11):
        for z in (16, 28):
            candidate.line((x, 9, z), (x, 21, z), QSV, mirrored=True)

    for x in range(4, 11):
        candidate.put(x, 9, 16, QSV, mirrored=True)
        candidate.put(x, 21, 16, QSV, mirrored=True)
        candidate.put(x, 9, 28, QSV, mirrored=True)
        candidate.put(x, 21, 28, QSV, mirrored=True)
    for y in range(10, 21):
        if y == 14:
            continue
        for x in (5, 6, 8, 9):
            candidate.put(x, y, 16, M['glass'], mirrored=True)
        candidate.put(7, y, 16, QSV, mirrored=True)

    for x in (5, 9):
        candidate.line((x, 10, 19), (x, 20, 19), M['pipe'], mirrored=True)
        candidate.line((x, 10, 25), (x, 20, 25), M['pipe'], mirrored=True)
        candidate.line((x, 10, 26), (x, 20, 26), M['pipe'], mirrored=True)
        candidate.put(x, 20, 27, M['pipe'], mirrored=True)
        candidate.line((x, 8, 28), (x, 22, 28), QSV, mirrored=True)
    for y in (11, 16, 20):
        for x in (6, 8):
            candidate.put(x, y, 22, M['grate'], mirrored=True)
        candidate.put(7, y, 23, M['gear'], mirrored=True)
    for y in (12, 17, 21):
        for x in (6, 8):
            candidate.put(x, y, 22, M['gear'], mirrored=True)
    for x in (5, 9):
        candidate.line((x, 10, 22), (x, 20, 22), QSV, mirrored=True)
    candidate.line((10, 9, 22), (10, 21, 22), QSV, mirrored=True)
    candidate.line((11, 9, 22), (11, 21, 22), QSV, mirrored=True)
    for y0, y1 in ((10, 11), (13, 16), (18, 20)):
        candidate.line((7, y0, 22), (7, y1, 22), M['pipe'], mirrored=True)
    for y in (12, 17):
        candidate.put(7, y, 22, M['gear'], mirrored=True)


def add_rear_hall(candidate: Candidate) -> None:
    x0, x1, z0, z1 = 3, 39, 41, 61
    for y in (3, 13, 27):
        candidate.ring(x0, x1, z0, z1, y, QSV)
    for x in (3, 39):
        for z in (41, 61):
            candidate.line((x, 4, z), (x, 26, z), QSV)
    for z in (42, 48, 54, 60):
        candidate.line((3, 4, z), (3, 26, z), QSV)
        candidate.line((39, 4, z), (39, 26, z), QSV)

    for x in (3, 39):
        for y in range(5, 26):
            if y == 13:
                continue
            for z in range(43, 60):
                if z in (48, 54):
                    continue
                observation_window = z in (45, 46, 56, 57) and (8 <= y <= 11 or 17 <= y <= 22)
                candidate.put(x, y, z, M['glass'] if observation_window else M['robust'])

    for x in range(4, 39):
        for y in range(4, 27):
            if y == 13:
                continue
            pipe_entry = x in (20, 21, 22) and 17 <= y <= 19
            if not pipe_entry and (x % 6 == 0 or x in (20, 22)):
                candidate.put(x, y, 41, M['robust'])
            if x % 6 == 0:
                candidate.put(x, y, 61, M['robust'])
    for x in range(4, 39):
        for y in range(6, 24):
            if y == 13:
                continue
            if x in (4, 10, 16, 26, 32, 38):
                candidate.put(x, y, 61, M['glass'])

    for x in range(4, 39):
        for z in range(42, 61):
            rib = z in (45, 51, 57) or x in (14, 28)
            skylight = ((8 <= x <= 12 or 30 <= x <= 34) and z in (43, 44, 46, 47, 49, 50)) or (
                18 <= x <= 24 and z in (52, 53, 55, 56, 58, 59))
            skylight_frame = not skylight and any(
                ((8 <= x + dx <= 12 or 30 <= x + dx <= 34) and z + dz in (43, 44, 46, 47, 49, 50)) or
                (18 <= x + dx <= 24 and z + dz in (52, 53, 55, 56, 58, 59))
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            state = QSV if rib or skylight_frame else M['glass'] if skylight else M['robust']
            candidate.put(x, 27, z, state)
    candidate.line((6, 28, 42), (6, 28, 60), QSV, mirrored=True)
    for z in (48, 54, 58):
        candidate.line((6, 28, z), (36, 28, z), QSV)
    candidate.line((21, 28, 42), (21, 28, 60), QSV)
    for x in (10, 32):
        candidate.put(x, 29, 58, M['vent'], mirrored=x == 10)

    for z in (47, 53, 59):
        for x in range(4, 39):
            candidate.put(x, 4, z, M['grate'])
        for x in (6, 14, 28, 36):
            candidate.line((x, 4, z - 2), (x, 26, z - 2), M['robust'])
    for z in (45, 47, 51, 53, 57, 59):
        for x in range(3, 40):
            candidate.put(x, 3, z, QSV)

    for lane_x in (10, 32):
        candidate.line((lane_x, 5, 45), (lane_x, 5, 58), QSV, mirrored=True)
        candidate.line((lane_x, 6, 45), (lane_x, 6, 58), M['pipe'], mirrored=True)
        for z in (47, 51, 55, 58):
            candidate.ring(lane_x - 2, lane_x + 2, z - 1, z + 1, 7, QSV, mirrored=True)
            candidate.put(lane_x, 7, z, QSV, mirrored=True)
            candidate.put(lane_x, 8, z, M['gear'], mirrored=True)
            candidate.put(lane_x, 9, z, M['vent'], mirrored=True)

    for x in range(18, 25):
        for z in range(43, 60):
            candidate.put(x, 4, z, M['grate'])
    for x in (18, 24):
        candidate.line((x, 4, 41), (x, 4, 42), M['robust'])
    for z in range(39, 47):
        for x in range(20, 23):
            candidate.put(x, 18, z, M['pipe'])
    for z in (40, 42, 44, 46):
        for x in (19, 23):
            candidate.put(x, 18, z, M['robust'])


def add_crown(candidate: Candidate) -> None:
    # Replace the flat cap with a tall QSV pressure body for the new stage.
    for x in range(14, 29):
        for z in range(14, 29):
            candidate.put(x, 55, z, QSV)
    for y in range(55, 79):
        casing = QSV if y in (55, 56, 60, 64, 68, 72, 76, 78) else M['robust']
        for offset in range(14, 29):
            for side in ('north', 'south', 'west', 'east'):
                if side == 'north':
                    pos = (offset, y, 14)
                elif side == 'south':
                    pos = (offset, y, 28)
                elif side == 'west':
                    pos = (14, y, offset)
                else:
                    pos = (28, y, offset)
                frame = offset in (14, 15, 16, 26, 27, 28)
                panel = y in (65, 66, 67, 69, 70, 71) and offset in (20, 21, 22)
                if panel:
                    state = M['vent'] if offset == 21 and y in (66, 70) else M['glass']
                else:
                    state = QSV if frame or casing == QSV else M['robust']
                candidate.put(*pos, state)

    candidate.ring(15, 27, 15, 27, 78, QSV)
    for offset in range(15, 28):
        candidate.put(offset, 78, 21, QSV)
        candidate.put(21, 78, offset, QSV)
    candidate.put(21, 79, 21, M['gear'])
    candidate.put(21, 80, 21, M['pipe'])


def connected_count(blocks: dict[tuple[int, int, int], str]) -> int:
    start = next(iter(blocks))
    seen = {start}
    queue = collections.deque([start])
    while queue:
        x, y, z = queue.popleft()
        for delta in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            pos = (x + delta[0], y + delta[1], z + delta[2])
            if pos in blocks and pos not in seen:
                seen.add(pos)
                queue.append(pos)
    return len(seen)


def write_bundle(data: dict, audit: dict, out: Path, states: list[str], groups: list[list[int]], materials: list[dict]) -> None:
    names = {
        PORT: '通用工业接口占位块', DIAMOND: '主控制器位置标记', HBV: 'HBV液态采集塔机壳',
        QSV: 'QSV固态采集机壳', M['robust']: '坚固机器外壳', M['solid']: '固体机器外壳',
        M['clean']: '洁净机器外壳', M['glass']: '耐热玻璃', M['pipe']: '钢管外壳',
        M['gear']: '钨钢齿轮箱', M['grate']: '装配线格栅', M['vent']: '计算机散热器',
        M['power']: '高功率外壳', 'gtceu:corrosion_proof_casing': '耐腐蚀机器外壳',
        'gtceu:bronze_machine_casing': '青铜机器外壳',
    }
    packed = {
        'data': {key: value for key, value in data.items() if key != 'blocks'},
        'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': names,
    }
    encoded = gzip.compress(json.dumps(packed, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)
    (out / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(base64.b64encode(encoded).decode('ascii')) + ';', encoding='utf-8')


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    predecessor, source_meta = load_predecessor()
    if len(predecessor) != 15321 or predecessor[(21, 5, 14)] != DIAMOND:
        raise ValueError('I01-1 V3 predecessor contract changed')
    if sum(state == PORT for state in predecessor.values()) != 6:
        raise ValueError('I01-1 V3 interface count changed')

    data = copy.deepcopy(source_meta)
    data.update({
        'key': 'I01-2',
        'name': 'i01-2-qsv-solid-collector-v2',
        'title': '2阶崩坏能采集塔·固态',
        'size': [43, 81, 62],
        'controller': [21, 5, 14],
        'paste_anchor': [21, 5, 14],
        'schematic_offset': [-21, -5, -14],
        'description': '保留HBV液态采集与六个原接口，在左右肩舱加入镜像结晶压榨盒并接入后置分选厂房；沿原塔轴新增高耸QSV固态结晶主塔，作为本阶段主体与整机视觉核心。',
        'brief': {
            'id': 'I01-2', 'title': '2阶崩坏能采集塔·固态',
            'minimum_wdh': [43, 62, 60],
            'form': '保留中心HBV液态塔；双侧结晶压榨盒、后置分选封装厂房与高耸QSV结晶主塔',
            'flow': 'HBV液态采集→肩舱内冷却结晶→后置压榨分选→封装输出',
        },
        'construction_notes': {
            'orientation': 'X向东、Y向上、Z向南；主控与继承接口朝北（-Z）。',
            'origin': [0, 0, 0], 'paste_anchor': [21, 5, 14],
            'schematic_offset': [-21, -5, -14],
            'stage_alignment': '主控世界坐标不动；完整继承I01-1 V3，QSV是新增阶段主体主机壳。',
            'status': '独立候选；未批准、未接入Pattern或实例。',
        },
        'zones': copy.deepcopy(source_meta['zones']) + [
            {'name': '左右肩舱内置QSV结晶压榨盒', 'kind': 'crystallizer',
             'min': [3, 8, 16], 'max': [11, 22, 28], 'pos': [7, 15, 22],
             'role': '在原冷凝肩舱空腔内分层冷却、压榨并析出固态崩坏能', 'service_face': '原肩舱观察窗'},
            {'name': '后置固态分选与封装厂房', 'kind': 'process',
             'min': [3, 3, 41], 'max': [39, 27, 61], 'pos': [21, 15, 51],
             'role': '固体结晶分选、转运、隔离封装与检修', 'service_face': '后侧及两侧玻璃墙'},
            {'name': 'QSV高位固态结晶主塔', 'kind': 'crystallizer',
             'min': [14, 55, 14], 'max': [28, 80, 28], 'pos': [21, 67, 21],
             'role': '新增固态阶段的主承压结晶腔与整机视觉核心，四面进气格栅围绕中央压榨轴布置',
             'service_face': '四面检修格栅与环形上层平台'},
        ],
        'paths': copy.deepcopy(source_meta['paths']) + [
            {'name': '后处理厂房中央格栅检修脊', 'min': [18, 4, 43], 'max': [24, 4, 59]},
        ],
        'links': copy.deepcopy(source_meta['links']) + [
            {'from': 'HBV后置回收泵房', 'to': 'QSV分选封装厂房', 'material': M['pipe'],
             'route': [[21, 18, 38], [21, 18, 45]]},
        ],
        'approval': '待负责人外观审核；不修改I01-1 V3确认归档，不替换正式Pattern或实例。',
    })
    data['ports'] = copy.deepcopy(source_meta['ports'])

    candidate = Candidate(dict(predecessor), tuple(data['size']))
    add_shoulder_cassettes(candidate)
    add_rear_hall(candidate)
    add_crown(candidate)

    blocks = [{'pos': list(pos), 'state': state} for pos, state in sorted(candidate.blocks.items())]
    data['blocks'] = blocks
    if not all(candidate.blocks.get(pos) == state for pos, state in predecessor.items()):
        raise AssertionError('inherited I01-1 V3 block changed')
    if candidate.blocks[(21, 5, 14)] != DIAMOND:
        raise AssertionError('controller marker moved or changed')
    if connected_count(candidate.blocks) != len(candidate.blocks):
        raise AssertionError(f'disconnected blocks: {connected_count(candidate.blocks)}/{len(candidate.blocks)}')

    mirror_errors = [(x, y, z, state, candidate.blocks.get((42 - x, y, z)))
                     for (x, y, z), state in candidate.blocks.items()
                     if candidate.blocks.get((42 - x, y, z)) != state]
    if mirror_errors:
        raise AssertionError(f'left-right symmetry failed: {mirror_errors[:5]}')
    for port in data['ports']:
        if candidate.blocks.get(tuple(port['pos'])) != PORT:
            raise AssertionError(f'inherited interface changed: {port}')

    data['role_materials'] = {state: [state] for state in sorted(set(candidate.blocks.values()))}
    size_check = size_baseline.require(data)
    counts = collections.Counter(candidate.blocks.values())
    states, groups, hashes = legacy_builder.export(data, OUT)
    schem_path = OUT / (data['name'] + '.schem')
    schem = nbtlib.load(schem_path)
    schem['Offset'] = nbtlib.IntArray([-21, -5, -14])
    schem.save(schem_path, gzipped=True)
    check_schem = nbtlib.load(schem_path)
    if list(map(int, check_schem['Offset'])) != [-21, -5, -14]:
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
    legacy_builder.render(data, materials, OUT)

    palette = dict(sorted(counts.items()))
    stage_counts = collections.Counter(candidate.added.values())
    if stage_counts[QSV] <= max(count for state, count in stage_counts.items() if state != QSV):
        raise AssertionError('QSV must be the most-used single material in the added I01-2 stage')
    bounds = [[min(pos[i] for pos in candidate.blocks), max(pos[i] for pos in candidate.blocks)] for i in range(3)]
    audit = {
        'source_predecessor': {
            'path': str(SOURCE_NBT.relative_to(ROOT)), 'sha256': SOURCE_SHA256,
            'blocks': len(predecessor), 'unchanged_blocks': len(predecessor),
            'controller': [21, 5, 14], 'ports': [p['pos'] for p in data['ports']],
        },
        'added_blocks': len(candidate.added),
        'block_count': len(blocks), 'unique_material_count': len(palette),
        'stage_primary_casing': {
            'voltage': 'QSV', 'block': QSV, 'added_count': stage_counts[QSV],
            'added_block_count': len(candidate.added),
            'added_share': round(stage_counts[QSV] / len(candidate.added), 4),
            'rank': 1, 'visual_identity': '新增高位QSV结晶主塔；前阶HBV塔与颜色保留',
        },
        'palette': palette, 'actual_bounds_xyz': bounds,
        'actual_size_wdh': size_check['actual_xyz'], 'actual_volume': __import__('math').prod(size_check['actual_xyz']),
        'size_baseline': size_check, 'connected_blocks': len(blocks),
        'controller_centering': {'width': data['size'][0], 'center_x_0based': 21, 'controller': [21, 5, 14], 'passed': True},
        'left_right_symmetry': {'axis': 'X=21', 'exact': True, 'mismatches': 0},
        'hashes': {'source_nbt': SOURCE_SHA256, **hashes},
        'asset_sources': asset_sources,
        'checks': [
            '以I01-1 V3确认NBT为基底；15,321个前阶实体块逐格原位、原状态保留。',
            '仅新增方块，不覆盖前阶壳体、主控标记及六个接口。',
            '主控仍在宽43的中心第22格，蓝图坐标[21,5,14]；控制器世界锚点不变。',
            '左右压榨盒、后处理厂房与塔冠关于X=21镜像；全结构六向连通。',
            'QSV机壳是新增阶段数量最多的单一材料，并构成高位结晶主塔；HBV前阶完整保留。',
            '实际外包范围逐轴达到69座规划下限。',
            'NBT/Sponge v2由同一逐格图导出；Sponge锚点偏移[-21,-5,-14]。',
            '所有材质来自指定增强版2.9.2实例及本项目资源，且模型为完整立方体。',
            '项目自有方块仅使用HBV/QSV电压机壳与工业接口占位块。',
        ],
        'not_verified': [
            '新候选外观待负责人审核。',
            '未接入正式Pattern、注册接口能力或配方。',
            '未进行游戏内成型、运行与生存获取验证。',
            'I26起的电压递增硬规则不作为I01-2返工门槛。',
            '工艺流线仅表达建筑分区，不证明游戏运行逻辑已接通。',
        ],
        'approval': data['approval'],
    }
    write_bundle(data, audit, OUT, states, groups, materials)
    (OUT / '设计与检查.json').write_text(json.dumps({'data': {k: v for k, v in data.items() if k != 'blocks'}, 'audit': audit},
        ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps({
        'id': 'I01-2', 'version': 'V2', 'status': 'candidate_pending_visual_approval',
        'title': data['title'], 'target_voltage': 'QSV', 'size_xyz': data['size'],
        'predecessor': str(SOURCE_NBT.relative_to(ROOT)), 'predecessor_sha256': SOURCE_SHA256,
        'controller': data['controller'], 'added_blocks': len(candidate.added),
        'blocks': len(blocks), 'palette_count': len(palette), 'hashes': hashes,
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    shutil.copy2(SOURCE_DIR / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (SOURCE_DIR / '三维评审.html').read_text(encoding='utf-8')
    page = re.sub(r'<title>.*?</title>', '<title>I01-2 固态崩坏能采集塔 · QSV主塔累计扩建候选 V2</title>', page, count=1)
    page = re.sub(r'<h1>.*?</h1>', '<h1>I01-2 · 崩坏能采集塔 · 固态</h1>', page, count=1)
    size_text = (f'{data["size"][0]}×{data["size"][2]}×{data["size"][1]}（宽×长×高） · '
                 f'{len(blocks):,}个实体块（含前阶） · 待审候选')
    page = re.sub(r'(<h1>.*?</h1><span>).*?(</span>)',
                  lambda match: match.group(1) + size_text + match.group(2), page, count=1)
    page = page.replace('id="layerValue">54', 'id="layerValue">80')
    page = page.replace('id="layer" type="range" min="0" max="54" value="54"',
                        'id="layer" type="range" min="0" max="80" value="80"')
    page = re.sub(r'<details open><summary>本机建筑概念</summary>.*?</details>',
        '<details open><summary>阶段扩建方案</summary>'
        '<p>完整保留I01-1 V3液态采集塔与六个接口；双侧结晶压榨盒嵌入肩舱，后置分选封装厂房接入回收泵房。沿原塔轴新增四面格栅的高位QSV结晶主塔，形成固态阶段承压腔与整机视觉核心。</p>'
        f'<p>本阶段新增{len(candidate.added):,}块中，QSV机壳{stage_counts[QSV]:,}块，为新增数量最多的单一材料；累计总量中的HBV与通用机壳不作为否决条件。主控仍在宽43第22格、蓝图坐标[21,5,14]。</p>'
        '<p class="muted">这是独立候选，待负责人审核。未替换正式Pattern或游戏实例；I26起规则不作为I01-2门槛。</p></details>', page, count=1)
    page = re.sub(r'<details open><summary>电压递增门槛</summary>.*?</details>',
        '<details open><summary>范围说明</summary><p>I01-2按前一阶段累计扩建；I26起的电压递增硬规则不追溯套用于本结构。</p></details>', page, count=1)
    page = page.replace('i01-1-hbv-liquid-collector-v3-interface-ribs.nbt', data['name'] + '.nbt')
    page = page.replace('i01-1-hbv-liquid-collector-v3-interface-ribs.schem', data['name'] + '.schem')
    page = page.replace('href="../../logs/i01-i24-redesign-plan-20261025/index.html"',
                        'href="../../logs/i01-i24-redesign-plan-20261025/index.html"')
    page = page.replace(' · <a href="北立面.png">北立面</a>', '')
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
