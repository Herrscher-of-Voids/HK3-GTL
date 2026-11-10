# -*- coding: utf-8 -*-
"""Build I16 V1: a twin-portal precision machining hall."""
from __future__ import annotations

import base64
import collections
import datetime as dt
import gzip
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import nbtlib
import numpy as np

import build_i07_calibration_preview as preview
from build_i09_i13_redesign_v6 import lodestone_export
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I16_魂钢精密加工中心_双龙门计量轴_V1_20261016'
LOG = ROOT / 'logs/i16-precision-center-v1'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版 2.7/minecraft'
NAME = 'i16-soulium-precision-machining-center-v1'
ARCHIVE = 'I16_V1_双龙门计量轴_结构与预览.zip'
PORT = 'hk3gtl:industrial_port_casing'
MARKERS = {PORT, 'minecraft:diamond_block'}

BASE = 'gtceu:steel_machine_casing'
FRAME = 'gtlcore:process_machine_casing'
HALL = 'gtceu:clean_machine_casing'
BED = 'gtceu:stainless_steel_turbine_casing'
RAIL = 'gtceu:tungstensteel_gearbox'
DRIVE = 'gtceu:stainless_steel_gearbox'
GLASS = 'gtceu:laminated_glass'
ACCENT = 'gtceu:uhv_machine_casing'
VENT = 'gtceu:computer_heat_vent'
FILTER = 'gtceu:filter_casing'
COOLANT = 'gtceu:corrosion_proof_casing'
METROLOGY = 'gtceu:sterilizing_filter_casing'

MATERIAL_ROLES = {
    BASE: '隔振基座、长向基准床身与工件托台',
    FRAME: '双龙门立柱、横梁节点与外部承载框架',
    HALL: '恒温精密厂房围护板与洁净操作间',
    BED: '粗加工机架、主梁与工件定位台',
    RAIL: 'Z向直线导轨、滚轮座与龙门滑座',
    DRIVE: '主轴箱、传动端和床身分段接头',
    GLASS: '计量室观察面与屋脊采光带',
    ACCENT: '高压直线驱动节点与测量基准标记',
    VENT: '恒温间送回风和主机热交换器',
    FILTER: '切屑雾化物过滤与切削液净化设备',
    COOLANT: '低位冷却介质总管和过滤回路外壳',
    METROLOGY: '洁净计量室的仪器台与隔离面板',
}


def _roof_level(x: int, cx: int) -> int:
    return 18 + max(0, 4 - abs(x - cx) // 4)


def _line_x(a: Build, x0: int, x1: int, y: int, z: int, state: str) -> None:
    a.box((x0, y, z), (x1, y, z), state)


def _line_z(a: Build, x: int, y: int, z0: int, z1: int, state: str) -> None:
    a.box((x, y, z0), (x, y, z1), state)


def _portal(a: Build, center_x: int, z: int, width: int, top: int, base_y: int,
            beam: str, name: str, stage: str, spindle_length: int) -> dict:
    x0, x1 = center_x - width // 2, center_x + width // 2
    for x in (x0, x1):
        a.box((x - 1, 3, z - 1), (x + 1, top - 3, z + 1), FRAME)
        a.box((x - 2, 1, z - 2), (x + 2, 3, z + 2), BASE)
        a.box((x - 2, top - 3, z - 1), (x + 2, top - 2, z + 1), beam)
    a.box((x0 - 1, top - 2, z - 1), (x1 + 1, top, z + 1), beam)
    a.box((x0, top + 1, z - 1), (x1, top + 1, z + 1), FRAME)

    # A bright, compact trolley sits on the bridge; the spindle reaches the bed.
    a.box((center_x - 3, top - 2, z - 2), (center_x + 3, top + 1, z + 2), RAIL)
    a.box((center_x - 2, top - 1, z - 3), (center_x + 2, top + 1, z + 3), ACCENT)
    a.box((center_x - 1, top - spindle_length, z - 1),
          (center_x + 1, top - 2, z + 1), DRIVE)
    a.box((center_x - 3, top - spindle_length - 2, z - 2),
          (center_x + 3, top - spindle_length, z + 2), METROLOGY if stage == '精加工' else BED)
    for side in (-1, 1):
        a.box((center_x + side * 4, top - 2, z - 1),
              (center_x + side * 4, top, z + 1), DRIVE)

    return {
        'name': name, 'kind': 'double_column_portal_machine',
        'min': [x0 - 2, 1, z - 2], 'max': [x1 + 2, top + 1, z + 2],
        'pos': [center_x, top, z], 'role': f'{stage}龙门跨越中央长床身，滑枕沿X向换位、工件沿Z向进给',
        'service_face': '两侧导轨与前方检修过道',
    }


def _annex(a: Build, x0: int, x1: int, z0: int, z1: int, roof: int,
           name: str, shell: str, window: str, vent_face: str) -> dict:
    a.box((x0, 1, z0), (x1, 1, z1), BASE)
    for x in range(x0, x1 + 1):
        for y in range(2, roof):
            for z in (z0, z1):
                if y in (6, 7, 8):
                    a.set(x, y, z, window)
                elif y % 4 == 0:
                    a.set(x, y, z, FRAME)
                else:
                    a.set(x, y, z, shell)
    for z in range(z0 + 1, z1):
        for y in range(2, roof):
            for x in (x0, x1):
                if y in (6, 7, 8):
                    a.set(x, y, z, window)
                elif z % 7 == 0:
                    a.set(x, y, z, FRAME)
                else:
                    a.set(x, y, z, shell)
    a.box((x0, roof, z0), (x1, roof, z1), shell)
    for x in range(x0 + 2, x1 - 1, 4):
        a.box((x, roof + 1, z0 + 1), (x, roof + 1, z1 - 1), FRAME)
    if vent_face == 'longitudinal':
        for z in range(z0 + 2, z1 - 1, 3):
            a.box((x0 + 1, 3, z), (x0 + 1, roof - 2, z), VENT)
    else:
        for x in range(x0 + 2, x1 - 1, 3):
            a.box((x, 3, z1 - 2), (x, roof - 2, z1 - 2), VENT)
    return {
        'name': name, 'kind': 'service_annex', 'min': [x0, 1, z0],
        'max': [x1, roof + 1, z1], 'pos': [(x0 + x1) // 2, roof, (z0 + z1) // 2],
        'role': '低矮附翼收納與主加工區分離的計量、冷卻或切屑回收設備',
        'service_face': '朝中央設備廊',
    }


def build() -> dict:
    brief = {
        'id': 'I16', 'title': '魂钢精密加工中心',
        'minimum_wdh': [33, 57, 29],
        'form': '长向恒温机加工厅，以双龙门计量轴构成主轮廓',
        'flow': '魂钢坯料入场、粗加工、精加工、恒温计量、切屑与冷却介质回收',
    }
    a = Build(brief)
    a.w, a.h, a.d = 49, 31, 57
    cx = 24

    # A full-width, low isolation raft anchors the hall and both utility wings.
    a.box((0, 0, 0), (48, 0, 56), BASE)
    a.box((0, 1, 0), (48, 1, 56), BASE)
    for x in range(2, 47, 4):
        a.box((x, 1, 2), (x + 1, 1, 54), HALL)

    # Main hall: broken glazing bands and an exposed truss roof keep both
    # portal machines visible from outside the review camera.
    x0, x1, z0, z1 = 8, 40, 4, 52
    for x in (x0, x1):
        a.box((x, 2, z0), (x, 5, z1), HALL)
        a.box((x, 15, z0), (x, 17, z1), HALL)
        for z in range(z0, z1 + 1, 8):
            a.box((x - 1, 2, z), (x + 1, 17, z), FRAME)
        for z in range(z0 + 2, z1 - 2, 8):
            a.box((x, 6, z), (x, 14, min(z + 4, z1 - 1)), GLASS)
        a.box((x, 18, z0), (x, 18, z1), FRAME)
    for z in (z0, z1):
        for x in range(x0, x1 + 1):
            if z == z0 and 20 <= x <= 28:
                continue
            a.box((x, 2, z), (x, 8, z), HALL)
            a.box((x, 9, z), (x, 14, z), GLASS)
            a.box((x, 15, z), (x, 18, z), HALL)
    for z in (z0, z0 + 8, z0 + 24, z0 + 40, z1):
        for x in range(x0, cx + 1):
            y = _roof_level(x, cx)
            a.box((x, 18, z - 1), (x, y, z + 1), FRAME)
        for x in range(cx, x1 + 1):
            y = _roof_level(x, cx)
            a.box((x, 18, z - 1), (x, y, z + 1), FRAME)
    a.box((cx, 22, z0), (cx, 22, z1), BED)
    a.box((cx - 2, 22, 26), (cx + 2, 22, 30), FRAME)
    a.box((cx - 2, 23, 26), (cx + 2, 27, 30), GLASS, True)
    a.box((cx - 1, 28, 27), (cx + 1, 28, 29), ACCENT)

    # The longitudinal hydrostatic bed and two guide rails tie the stations
    # together; isolated bed islands leave cross-aisles between work zones.
    a.box((13, 2, 8), (35, 3, 50), BASE)
    for x in (11, 12, 36, 37):
        a.box((x, 2, 8), (x, 7, 50), BED)
        for z in range(9, 51, 6):
            a.box((x - 1, 2, z), (x + 1, 4, z), DRIVE)
    for z0_table, z1_table, width in ((12, 24, 19), (30, 41, 15), (44, 49, 11)):
        half = width // 2
        a.box((cx - half, 4, z0_table), (cx + half, 5, z1_table), BED)
        for x in (cx - half + 1, cx + half - 1):
            a.box((x, 6, z0_table + 1), (x, 6, z1_table - 1), DRIVE)
        a.box((cx - 1, 6, z0_table + 1), (cx + 1, 7, z1_table - 1), ACCENT)

    # Two bridges of different span and height: the first removes bulk stock,
    # while the narrower second frame is paired with the metrology wing.
    zones = [
        _portal(a, cx, 19, 30, 22, 3, BED,
                '一号重载龙门・魂钢粗加工跨', '粗加工', 8),
        _portal(a, cx, 36, 22, 20, 3, FRAME,
                '二号恒温龙门・微通道与轮廓精加工跨', '精加工', 7),
    ]

    # The west wing is a low, vibration-isolated measurement suite rather
    # than the obsolete rear tower. An optical bridge floats over gauge tables.
    zones.append(_annex(a, 0, 14, 30, 51, 12,
                        '西翼恒温计量室・三坐标复核廊', HALL, GLASS, 'longitudinal'))
    a.box((1, 2, 34), (5, 3, 47), METROLOGY)
    for x in (2, 5):
        a.box((x, 4, 36), (x, 8, 36), DRIVE)
        a.box((x, 8, 36), (x, 8, 45), ACCENT)
    a.box((2, 8, 45), (5, 8, 45), METROLOGY)
    a.box((3, 4, 38), (4, 6, 43), ACCENT)
    a.box((1, 9, 37), (1, 9, 45), FRAME)

    # The east wing separates coolant polishing from chip mist and swarf sorting.
    zones.append(_annex(a, 34, 48, 7, 26, 13,
                        '东翼冷却过滤与切屑分级站', FRAME, GLASS, 'crosswise'))
    for x, top in ((37, 8), (41, 10), (45, 8)):
        a.box((x - 1, 2, 10), (x + 1, 4, 23), COOLANT)
        for z in (11, 16, 21):
            a.box((x - 2, 5, z), (x + 2, top, z), FILTER)
            a.box((x - 1, top + 1, z), (x + 1, top + 1, z), VENT)
    a.box((37, 4, 8), (45, 4, 9), DRIVE)
    a.box((36, 5, 24), (46, 6, 24), COOLANT)

    # Short service manifolds remain below the glazing and terminate at the wings.
    for z in range(9, 26):
        a.set(39, 6, z, COOLANT if z % 4 else FILTER)
    for z in range(29, 49):
        a.set(9, 5, z, VENT if z % 5 else DRIVE)

    # A shallow loading canopy and a clearly readable controller marker close
    # the north elevation without blocking the vehicle-width service aisle.
    a.box((19, 8, 2), (29, 9, 4), FRAME)
    for x in (19, 29):
        a.box((x, 2, 3), (x, 7, 4), BED)
    controller = [cx, 10, 4]
    a.set(*controller, 'minecraft:diamond_block')
    a.box((cx - 1, 9, 4), (cx + 1, 9, 4), ACCENT)

    port_specs = [
        ('BILLET', [9, 5, 4], '北侧装料闸：退火后魂钢坯料输入候选'),
        ('POWER', [13, 5, 4], '北侧装料廊：驱动供能输入候选'),
        ('COOLANT', [17, 5, 4], '北侧装料廊：精密切削冷却介质输入候选'),
        ('PRODUCT', [31, 5, 4], '北侧出料侧：精加工件输出候选'),
        ('DATA', [35, 5, 4], '北侧计量侧：尺寸/误差数据输出候选'),
        ('CHIPS', [39, 5, 4], '北侧回收侧：切屑与切削雾回收候选'),
    ]
    ports = []
    for key, pos, purpose in port_specs:
        a.set(pos[0], pos[1], pos[2] + 1, HALL)
        a.set(*pos, PORT)
        ports.append({'id': key, 'pos': pos, 'face': 'north', 'purpose': purpose})

    paths = [
        {'name': '北门装料与步行检修净空', 'min': [21, 2, 0], 'max': [27, 6, 7]},
        {'name': '西翼计量室入口净空', 'min': [7, 2, 33], 'max': [9, 4, 35]},
    ]
    # Keep a vehicle-width opening through the north wall and a flush entrance
    # from the main hall into the metrology wing.
    for x in range(20, 29):
        for y in range(2, 9):
            a.b.pop((x, y, 4), None)
    for y in range(2, 6):
        for z in range(33, 36):
            a.b.pop((14, y, z), None)
            a.b.pop((8, y, z), None)

    zones.extend([
        {'name': '长向隔振基准床身', 'kind': 'hydrostatic_reference_bed',
         'min': [11, 2, 8], 'max': [37, 7, 50], 'pos': [cx, 7, 29],
         'role': '沿Z向进给的长床身串起坯料、切削、计量和回收工位',
         'service_face': '东西两侧导轨与北门物流轴'},
        {'name': '屋脊恒温采光廊', 'kind': 'glazed_clerestory',
         'min': [22, 22, 4], 'max': [26, 27, 52], 'pos': [cx, 27, 28],
         'role': '低斜屋顶的连续采光脊，强调计量环境而不增加后置高塔',
         'service_face': '屋面检修方向'},
    ])
    a.links = [
        {'from': '北门坯料闸', 'to': '一号重载龙门・魂钢粗加工跨',
         'route': [[cx, 4, 10], [cx, 4, 19]]},
        {'from': '一号重载龙门・魂钢粗加工跨', 'to': '二号恒温龙门・微通道与轮廓精加工跨',
         'route': [[cx, 4, 25], [cx, 4, 36]]},
        {'from': '二号恒温龙门・微通道与轮廓精加工跨', 'to': '西翼恒温计量室・三坐标复核廊',
         'route': [[cx, 4, 42], [14, 4, 42], [11, 4, 42]]},
    ]
    a.zones, a.paths = zones, paths
    return {
        'key': 'i16', 'name': NAME, 'title': '魂钢精密加工中心',
        'candidate_version': 'V1 双龙门计量轴', 'size': [a.w, a.h, a.d],
        'core_marker': controller, 'controller': controller,
        'visual_core': [cx, 7, 29], 'ports': ports, 'paths': paths,
        'zones': zones, 'links': a.links, 'brief': brief,
        'description': (
            '把退火后的魂钢坯料送上长向隔振床身，依次经过两道不同尺度的龙门：'
            '第一跨以厚重双柱和大滑枕表达粗加工，第二跨更窄、更低，以洁净驱动节点标出微通道与轮廓精加工。'
            '西侧低矮恒温计量翼用连续玻璃带和光学横桥替代旧版后置高塔；东侧冷却过滤与切屑分级翼独立落地。'
            '厂房采用浅折线采光屋脊与宽门装料廊，远看是两道横向龙门压在一条长基准轴上，'
            '不沿用旧版并列加工床加后置测量塔的构图。所有工艺流向仅用于解释建筑造型。'
        ),
        'role_materials': {key: sorted(value) for key, value in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


def _state_name(state) -> str:
    name = str(state['Name'])
    properties = state.get('Properties')
    if properties:
        values = ','.join(f'{key}={value}' for key, value in sorted(properties.items()))
        return f'{name}[{values}]'
    return name


def _read_structure(path: Path) -> tuple[list[int], dict[tuple[int, int, int], str]]:
    nbt = nbtlib.load(path)
    palette = [_state_name(state) for state in nbt['palette']]
    blocks = {
        tuple(int(value) for value in block['pos']): palette[int(block['state'])]
        for block in nbt['blocks']
    }
    return [int(value) for value in nbt['size']], blocks


def _read_schematic(path: Path) -> tuple[list[int], dict[tuple[int, int, int], str]]:
    nbt = nbtlib.load(path)
    size = [int(nbt[key]) for key in ('Width', 'Height', 'Length')]
    width, height, depth = size
    palette = {int(index): str(state) for state, index in nbt['Palette'].items()}
    values = np.asarray(nbt['BlockData']).view(np.uint8)
    if len(values) != width * height * depth:
        raise AssertionError(f'invalid Sponge BlockData length: {len(values)} != {width * height * depth}')
    blocks = {}
    for index, value in enumerate(values):
        value = int(value)
        if value:
            state = palette[value]
            x = index % width
            z = (index // width) % depth
            y = index // (width * depth)
            blocks[(x, y, z)] = state
    return size, blocks


def _material_basis(counts: collections.Counter) -> dict:
    resources = Resources(instance=INSTANCE, project_resources=ROOT / 'src/main/resources')
    rows = []
    try:
        for state, count in sorted(counts.items()):
            if state in MARKERS:
                rows.append({'block_state': state, 'count': count,
                             'role': '项目规定的结构控制/接口标记', 'complete_cube': True,
                             'note': '接口为惰性外观占位；不提供仓室或供能能力。'})
                continue
            material = resources.material(state)
            ns, block = state.split(':', 1)
            block = block.split('[', 1)[0]
            rows.append({
                'block_state': state, 'count': count,
                'role': MATERIAL_ROLES.get(state, 'structure block'),
                'model': material['model'], 'complete_cube': material['complete_cube'],
                'resource_source': resources.sources.get(f'assets/{ns}/blockstates/{block}.json'),
                'survival_recipe_and_stage': 'not verified',
            })
    finally:
        resources.close()
    return {'target_instance': str(INSTANCE),
            'scope': '增强版 2.8 实例的静态模型与完整方块核验；未核验生存配方和阶段可达性。',
            'materials': rows}


def _write_reference() -> dict:
    return {
        'machine': 'I16 魂钢精密加工中心 · 双龙门计量轴 V1',
        'sources': [
            {'title': 'DMG MORI · Portal Series – 5 Axis Milling',
             'url': 'https://en.dmgmori.com/products/machines/milling/5-axis-milling/portal',
             'used_as': '大型稳定门式结构跨越加工区域的外形组织参考。'},
            {'title': 'Hexagon · Temperature-controlled metrology room case study',
             'url': 'https://hexagon.com/-/media/project/one-web/master-site/mi/products-mi/dea-alpha/zaigler-kulmbach_cs_en.pdf',
             'used_as': '独立恒温测量环境与设备间隔离关系参考。'},
        ],
        'original_translation': '两道龙门跨压一条长向隔振床身，西侧改为低矮恒温计量翼，东侧设置冷却和切屑处理翼；浅折线采光屋脊与双层横梁形成原创方块轮廓。',
        'boundary': '现实资料只作为建筑/设备空间关系参考；不代表 I16 的正式 Pattern、仓室能力、配方或运行逻辑已实现。',
    }


def _write_pages(data: dict, audit: dict) -> None:
    w, h, d = data['size']
    wdh = [w, d, h]
    baseline = audit['size_baseline']['baseline_wdh']
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I16 · 双龙门计量轴 V1</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#111a1d;color:#edf2ef;font:16px/1.7 "Microsoft YaHei",sans-serif}}a{{color:#9edbd9;text-decoration:none}}a:hover{{color:#fff}}main{{max-width:1440px;margin:auto;padding:30px clamp(18px,4vw,56px) 48px}}.tag{{color:#9db9b5;font-size:13px}}h1{{font-size:34px;line-height:1.25;margin:8px 0}}.lede{{max-width:980px;color:#c2cfcc;margin:0 0 20px}}nav{{display:flex;gap:20px;flex-wrap:wrap;margin:18px 0 22px}}nav a{{padding:8px 0;border-bottom:1px solid #628f8d}}.hero{{border-top:1px solid #405452;border-bottom:1px solid #405452;background:#192321;padding:10px}}.hero img{{display:block;width:100%;max-height:700px;object-fit:contain}}.facts{{display:flex;gap:24px;flex-wrap:wrap;color:#c5d2cf;margin:16px 0}}.facts b{{color:#e8d99f;font-weight:600}}.band{{border-top:1px solid #3c504d;margin-top:28px;padding-top:17px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}}h2{{font-size:18px;margin:0 0 6px}}.band p,.note{{color:#b8c8c4;margin:0}}.note{{font-size:14px;margin-top:24px;max-width:1050px}}@media(max-width:760px){{main{{padding-top:22px}}h1{{font-size:29px}}.band{{grid-template-columns:1fr;gap:16px}}}}</style></head><body><main>
<div class="tag">HK3GTL · I16 · 外观候选 V1</div><h1>魂钢精密加工中心 · 双龙门计量轴</h1>
<p class="lede">一条长向隔振床身串联坯料入口、粗加工、精加工和恒温计量；两道高低不同的龙门横跨主轴，西侧设低矮计量翼，东侧收纳冷却过滤与切屑分级设备。</p>
<nav><a href="三维评审.html">打开可旋转三维评审</a><a href="{NAME}.schem">下载 Sponge Schematic</a><a href="{NAME}.nbt">下载结构 NBT</a><a href="设计与检查.json">结构与审计记录</a><a href="材料依据.json">逐块材料依据</a><a href="设计参考.json">现实参照</a></nav>
<div class="hero"><img src="等轴预览.png" alt="魂钢精密加工中心双龙门计量轴 V1"></div>
<div class="facts"><span><b>{wdh[0]} × {wdh[1]} × {wdh[2]}</b> 方块（宽×深×高）</span><span><b>{len(data['blocks']):,}</b> 个实体方块</span><span><b>{len(data['zones'])}</b> 个建筑分区</span><span>{len(data['ports'])} 个接口候选</span><span>69 座规划下限：{baseline[0]} × {baseline[1]} × {baseline[2]}，通过</span></div>
<section class="band"><div><h2>双龙门主加工廊</h2><p>厚重一号跨承担粗加工意象；较窄的二号跨配置洁净滑枕与精加工台。导轨和支座从长床身连续读出进给轴。</p></div><div><h2>恒温计量翼</h2><p>西侧低翼以宽玻璃观察带、光学横桥和三坐标台表达测量复核，避开旧方案的后置高塔。</p></div><div><h2>冷却与切屑分流</h2><p>东翼把过滤器、冷却总管和切屑分级设备分层摆放，短管线回接主加工廊，保留明确检修面。</p></div></section>
<section class="band"><div><h2>现实设备参照</h2><p>参考大型门式五轴设备的横梁跨距，以及独立恒温测量室的环境分区。</p><p><a href="https://en.dmgmori.com/products/machines/milling/5-axis-milling/portal">DMG MORI · Portal Series ↗</a> · <a href="https://hexagon.com/-/media/project/one-web/master-site/mi/products-mi/dea-alpha/zaigler-kulmbach_cs_en.pdf">Hexagon · 测量室案例 ↗</a></p></div><div><h2>原创空间转译</h2><p>以双横向门架、屋脊采光廊和侧置计量翼形成新的长向厂房构图，不复用旧版并列加工床和后置塔。</p><p><a href="设计参考.json">查看参考与设计边界</a></p></div><div><h2>候选状态</h2><p>接口标记只是惰性外观占位；正式 Pattern、配方、仓室能力及游戏成型未验收。</p><p><a href="设计与检查.json">查看结构检查</a></p></div></section>
<p class="note">V1 待用户审阅。结构尺寸、连通性、端口背板与净空以及 2.8 实例普通方块模型已做静态检查；生存材料可达性、正式 Pattern、多人交互与游戏运行尚未验收。</p>
</main></body></html>'''
    (OUT / 'index.html').write_text(page, encoding='utf-8')

    # The shared reviewer provides real pack textures, layer slicing, and inspection.
    page_path = OUT / '三维评审.html'
    viewer = page_path.read_text(encoding='utf-8')
    viewer = viewer.replace('<title>探测器精密校准台 · 自由设计候选</title>',
                            '<title>I16 · 魂钢精密加工中心 · 双龙门计量轴 V1</title>')
    viewer = viewer.replace('<a href="设计与检查.json">← 设计与检查</a>',
                            '<a href="index.html">← I16 双龙门计量轴</a>')
    viewer = viewer.replace('<h1>探测器精密校准台</h1>', '<h1>魂钢精密加工中心 · 双龙门计量轴</h1>')
    viewer = viewer.replace('待审预览', 'V1 外观候选')
    viewer = viewer.replace('纵向四区连续退火厂：前端气闸上料，经四段梯度热处理后进入后端淬冷整形池，侧塔记录温度曲线并完成检测。', data['description'])
    viewer = viewer.replace('i07-honkai-detector-calibration-bench', NAME)
    viewer = viewer.replace('i07-detector-calibration-bench', NAME)
    viewer = viewer.replace('i07-soulsteel-precision-machining-center', NAME)
    viewer = viewer.replace('</style><header>',
        'header span{display:block;overflow-wrap:anywhere}aside>div{display:flex;flex-wrap:wrap}button{white-space:normal;max-width:100%}'
        '@media(max-width:600px){html,body{width:100%;max-width:100%;overflow-x:hidden}header{padding:12px}'
        'header h1{font-size:20px;overflow-wrap:anywhere}main.review{width:100%;min-width:0}'
        'aside{width:100%;max-width:100%;min-width:0;padding:12px;overflow-x:hidden;border-left:0}'
        'aside>div{display:grid;width:100%;min-width:0;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px}'
        'aside>div>button{width:100%;min-width:0;margin:0;padding:7px 4px;font-size:13px;overflow-wrap:anywhere}'
        '#stage{width:100%;max-width:100%;height:58vh;min-height:420px}}'
        '</style><header>')
    page_path.write_text(viewer, encoding='utf-8')


def _bundle() -> dict:
    target = OUT / ARCHIVE
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path != target:
                archive.write(path, path.relative_to(OUT))
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert all(archive.read(name) == (OUT / name).read_bytes() for name in archive.namelist())
    return {'file': target.name, 'bytes': target.stat().st_size,
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'entries_equal_disk': True}


def main() -> None:
    LOG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    data['construction_notes'] = {
        'origin': [0, 0, 0], 'paste_anchor': [0, 0, 0], 'schematic_offset': [0, 0, 0],
        'orientation': 'X 向东、Y 向上、Z 向南；接口朝北（-Z）。',
        'recommended_bottom_world_y': -60,
        'status': 'V1 外观候选，待用户审阅；未批准、未部署。',
        'controller_marker': '入口钻石块是项目结构识别标记，不代表控制器已接入。',
        'ports': 'industrial_port_casing 是惰性外观占位；Pattern 接入时需换成具备相应能力的真实仓室。',
        'recipe_boundary': '工艺分区仅表达建筑空间，不代表 I16 的正式配方或加工逻辑已实现。',
    }
    preview.TEST_INSTANCE = INSTANCE
    preview.package(data, OUT, 'i07', [
        '双龙门与长向隔振床身构成新主轮廓，不沿用旧版并列加工床和后置计量塔',
        '尺寸逐轴不低于69座规划下限，实际边界由实体方块达到',
        '构件均为完整方块；端口有背板和底座，北向净空与装料通道通过',
        '普通材料从当前增强版2.8实例解析，并核验完整方块模型',
    ])
    nbt_sha = lodestone_export(data, OUT, LOG)

    nbt_path = OUT / f'{NAME}.nbt'
    schem_path = OUT / f'{NAME}.schem'
    expected = {tuple(block['pos']): block['state'] for block in data['blocks']}
    nbt_size, nbt_blocks = _read_structure(nbt_path)
    schem_size, schem_blocks = _read_schematic(schem_path)
    if nbt_size != data['size'] or schem_size != data['size']:
        raise AssertionError({'nbt_size': nbt_size, 'schem_size': schem_size, 'expected': data['size']})
    if nbt_blocks != expected or schem_blocks != expected:
        raise AssertionError({'nbt_equal': nbt_blocks == expected, 'schem_equal': schem_blocks == expected})
    size_audit = require({'key': 'I16', 'size': nbt_size,
                          'blocks': [{'pos': list(pos)} for pos in nbt_blocks]})
    if len(data['ports']) != 6 or sum(state == PORT for state in nbt_blocks.values()) != 6:
        raise AssertionError('I16 must contain six inert port markers')

    record_path = OUT / '设计与检查.json'
    record = json.loads(record_path.read_text(encoding='utf-8'))
    audit = record['audit']
    counts = collections.Counter(block['state'] for block in data['blocks'])
    audit.update({
        'instance': str(INSTANCE), 'candidate_version': data['candidate_version'],
        'approval': 'V1 待用户审阅；未批准、未部署。',
        'size_baseline': size_audit,
        'hashes': {'nbt': nbt_sha, 'schem': hashlib.sha256(schem_path.read_bytes()).hexdigest()},
        'design_markers': {key: counts[key] for key in sorted(MARKERS)},
        'material_counts': dict(sorted(counts.items())),
        'checks': audit['checks'] + [
            'Minecraft Builder/Lodestone NBT 已重新导出并逐格回读一致',
            'Sponge Schematic 与 NBT、蓝图逐格坐标和方块状态一致',
            '入口检修通道和六个北向接口净空通过',
            '东侧冷却/切屑翼与西侧恒温计量翼由实体基础连接主厅',
        ],
        'not_verified': [
            '普通材料的配方、科技前置与生存阶段可达性',
            'I16 正式 Pattern、仓室能力与配方运行',
            'Minecraft 游戏内朝向、多人交互与实际成型',
            '用户对 V1 外观的最终批准',
        ],
    })
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / '材料依据.json').write_text(json.dumps(_material_basis(counts), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / '设计参考.json').write_text(json.dumps(_write_reference(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    payload_path = OUT / 'data.js'
    encoded = json.loads(payload_path.read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    payload['audit'] = audit
    payload['data'] = record['data']
    packed = base64.b64encode(gzip.compress(json.dumps(
        payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    payload_path.write_text('window.HK3_PAYLOAD=' + json.dumps(packed) + ';', encoding='utf-8')

    _write_pages(data, audit)
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)

    verification = {
        'passed': True,
        'id': 'I16', 'version': 'V1 双龙门计量轴',
        'size_xyz': nbt_size, 'size_wdh': [nbt_size[0], nbt_size[2], nbt_size[1]],
        'actual_xyz': size_audit['actual_xyz'], 'baseline_wdh': size_audit['baseline_wdh'],
        'blocks': len(nbt_blocks), 'materials': len(counts), 'zones': len(data['zones']),
        'ports': len(data['ports']), 'nbt_sha256': nbt_sha,
        'schem_sha256': hashlib.sha256(schem_path.read_bytes()).hexdigest(),
        'blueprint_sha256': hashlib.sha256((OUT / 'blueprint.json').read_bytes()).hexdigest(),
        'checks': ['NBT and Schematic equal source block map', 'size bounds and physical block bounds passed',
                   'geometry connected; ports, backing, base and route clearance passed',
                   'resource models resolved as full cubes'],
    }
    manifest = {
        'machine': data['title'], 'candidate_version': data['candidate_version'],
        'size_xyz': data['size'], 'size_wdh': [data['size'][0], data['size'][2], data['size'][1]],
        'blocks': len(data['blocks']), 'materials': len(counts), 'zones': len(data['zones']),
        'ports': len(data['ports']), 'size_baseline': size_audit,
        'instance_manifest_version': '2.8', 'approval': '待用户审阅；未批准、未部署。',
        'hashes': {'nbt': nbt_sha, 'schem': hashlib.sha256(schem_path.read_bytes()).hexdigest(),
                   'blueprint': hashlib.sha256((OUT / 'blueprint.json').read_bytes()).hexdigest()},
    }
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    bundle = _bundle()
    verification['checks'].append('delivery archive round-trip passed')
    verification['archive_roundtrip'] = True
    (OUT / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    bundle = _bundle()
    log_record = {**verification, 'archive': bundle}
    (LOG / 'verification.json').write_text(json.dumps(log_record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'delivery': str(OUT), 'blocks': len(data['blocks']),
                      'materials': len(counts), 'verification': log_record,
                      'archive': bundle}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
