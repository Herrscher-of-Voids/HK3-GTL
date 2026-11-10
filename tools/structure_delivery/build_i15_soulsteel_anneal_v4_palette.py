# -*- coding: utf-8 -*-
"""I15 V4 palette revision: retain V3 geometry and restore a thermal color identity."""
import base64
import collections
import datetime
import gzip
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import nbtlib

import build_i07_calibration_preview as preview
from build_i09_i13_redesign_v6 import lodestone_export
from material_resources import Resources
from redesign69_geometry import Build, ROOT


OUT = ROOT / 'deliveries/I15_魂钢重构退火炉_三钟回转炉院_配色修订_V4_20261016'
LOG = ROOT / 'logs/i15-soulsteel-anneal-v4-palette'
ARCHIVE = 'I15_V4_三钟回转炉院_配色修订_结构与预览.zip'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版 2.7/minecraft'
PORT = 'hk3gtl:industrial_port_casing'
DIAMOND = 'minecraft:diamond_block'
MARKERS = {PORT, DIAMOND}

FOUNDATION = 'gtceu:steel_brick_casing'
FRAME = 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing'
HOOD = 'gtceu:stainless_steel_turbine_casing'
HOT = 'gtceu:high_temperature_smelting_casing'
COIL = 'gtceu:kanthal_coil_block[active=false]'
GLASS = 'gtceu:tempered_glass'
COLD = 'gtlcore:cold_ice_casing'
VENT = 'gtceu:computer_heat_vent'
GEAR = 'gtceu:stainless_steel_gearbox'
FILTER = 'gtceu:filter_casing'
DUCT = 'gtceu:corrosion_proof_casing'
CLEAN = 'gtceu:clean_machine_casing'
THERMAL_ORANGE = 'hk3gtl:casing_colored_orange'
QUENCH_BLUE = 'hk3gtl:casing_colored_light_blue'

MATERIAL_ROLES = {
    FOUNDATION: '炉院整块基础、三座炉台与低位设备基础',
    FRAME: '八角院墙、炉罩肋骨、排气管架与门架',
    HOOD: '三座退火罩的金属外壳与分段檐口',
    HOT: '双加热炉的内衬、炉床与高温烟道',
    COIL: '两座加热罩内可视的加热线圈意象',
    GLASS: '退火罩观察带与检修窗',
    COLD: '喷射冷却罩、冷却介质附房与低温管汇',
    VENT: '冷却罩散热片与换热附房风道',
    GEAR: '中央回转台、滚道与装料转运轴',
    FILTER: '两座加热罩的烟气过滤烟囱与净化附房',
    DUCT: '保护气氛及冷却水外露总管意象',
    CLEAN: '入口控制门架与维护节点',
    THERMAL_ORANGE: '两座加热钟罩连续的暖橙色外壳识别带',
    QUENCH_BLUE: '南侧喷射冷却钟罩连续的浅蓝色冷端外壳识别带',
}


def _inside_oct(dx, dz, r):
    if r <= 0:
        return dx == 0 and dz == 0
    return max(abs(dx), abs(dz)) <= r and abs(dx) + abs(dz) <= 2 * r - r // 3


def _fill_oct(a, cx, cz, r, y0, y1, material):
    for y in range(y0, y1 + 1):
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                if _inside_oct(x - cx, z - cz, r):
                    a.set(x, y, z, material)


def _oct_course(a, cx, cz, outer, inner, y, material):
    for x in range(cx - outer, cx + outer + 1):
        for z in range(cz - outer, cz + outer + 1):
            if _inside_oct(x - cx, z - cz, outer) and not _inside_oct(x - cx, z - cz, inner):
                a.set(x, y, z, material)


def _square_shell(a, x0, x1, z0, z1, y0, y1, material):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):
                    a.set(x, y, z, material)


def _bell(a, cx, cz, label, profile, hot=False):
    _fill_oct(a, cx, cz, 8, 2, 4, FOUNDATION)
    _oct_course(a, cx, cz, 8, 6, 4, FRAME)
    for y0, y1, radius in profile:
        for y in range(y0, y1 + 1):
            inner = max(0, radius - 2)
            skin = HOOD if y not in (9, 17, 25) else FRAME
            if hot and y in (25,):
                skin = HOT
            if hot and 6 <= y <= 24 and y not in (9, 17, 25):
                skin = THERMAL_ORANGE
            elif not hot and 9 <= y <= 16:
                skin = QUENCH_BLUE
            _oct_course(a, cx, cz, radius, inner, y, skin)

    # Broad, full-cube viewing bands distinguish each removable bell hood.
    window_top = min(18, profile[-1][1] - 2)
    for y in range(8, window_top + 1):
        radius = next(r for lo, hi, r in profile if lo <= y <= hi)
        for side in (-1, 1):
            x = cx + side * radius
            for dz in (-1, 0, 1):
                a.set(x, y, cz + dz, GLASS)

    if hot:
        _fill_oct(a, cx, cz, 3, 5, 6, HOT)
        for side in (-1, 1):
            for dz in (-2, 2):
                x = cx + side * 5
                a.box((x, 7, cz + dz), (x, 18, cz + dz), COIL)
                a.box((x, 7, cz + dz), (x, 7, cz + dz), HOT)
        for y in (8, 14, 20):
            _oct_course(a, cx, cz, 6, 5, y, HOT)
        _twin_flues(a, cx, cz, profile[-1][1], 49 if cx == 14 else 46)
    else:
        # Cooling hood: a lower, visibly ventilated cap with cold-colored ribs.
        for y in range(7, 17, 2):
            for side in (-1, 1):
                x = cx + side * 8
                for dz in (-2, -1, 0, 1, 2):
                    a.set(x, y, cz + dz, VENT)
        _fill_oct(a, cx, cz, 3, 5, 6, COLD)

    return {
        'name': label, 'kind': 'bell_annealing_station',
        'min': [cx - 8, 2, cz - 8],
        'max': [cx + 8, profile[-1][1], cz + 8],
        'pos': [cx, profile[-1][1], cz],
        'role': '罩式炉座；外壳分层、内衬和检修观察带表达工艺分区',
        'service_face': '北侧接口与东西两侧观察窗',
    }


def _twin_flues(a, cx, cz, roof_y, top_y):
    for fx in (cx - 2, cx + 2):
        # Repeated crossed shafts read as filtered exhaust stacks, not solid towers.
        for y in range(roof_y - 2, top_y):
            material = FILTER if y in (roof_y - 2, roof_y - 1) or y % 6 == 0 else DUCT
            for dx, dz in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                a.set(fx + dx, y, cz + dz, material)
        for dx, dz in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            a.set(fx + dx, top_y - 1, cz + dz, HOOD)


def _pavilion(a, x0, z0, width, depth, ytop, shell, trim, label, vent_face):
    x1, z1 = x0 + width - 1, z0 + depth - 1
    a.box((x0, 1, z0), (x1, 2, z1), FOUNDATION)
    _square_shell(a, x0, x1, z0, z1, 3, ytop, shell)
    for x in range(x0, x1 + 1, 3):
        a.box((x, ytop, z0), (x, ytop, z1), trim)
    for z in (z0, z1):
        a.box((x0, ytop, z), (x1, ytop, z), trim)
    if vent_face == 'west':
        for y in range(5, ytop - 1, 2):
            a.box((x0, y, z0 + 2), (x0, y, z1 - 2), VENT)
    else:
        for y in range(5, ytop - 1, 3):
            a.box((x0 + 2, y, z1), (x1 - 2, y, z1), GLASS)
    return {
        'name': label, 'kind': 'service_pavilion', 'min': [x0, 1, z0],
        'max': [x1, ytop, z1], 'pos': [(x0 + x1) // 2, ytop, (z0 + z1) // 2],
        'role': '獨立落地設備附房，造型表達煙氣淨化或冷卻介質循環',
        'service_face': '朝爐院內側',
    }


def _orthogonal_rail(a, points, y, material):
    for start, end in zip(points, points[1:]):
        x0, z0 = start
        x1, z1 = end
        if x0 != x1 and z0 != z1:
            raise ValueError(f'rail segment must be orthogonal: {start} -> {end}')
        if x0 == x1:
            for z in range(min(z0, z1), max(z0, z1) + 1):
                a.set(x0, y, z, material)
        else:
            for x in range(min(x0, x1), max(x0, x1) + 1):
                a.set(x, y, z0, material)


def build():
    brief = {
        'id': 'I15', 'title': '魂钢重构退火炉',
        'minimum_wdh': [29, 49, 27],
        'form': '三座罩式退火爐環抱中央回轉爐院',
        'flow': '雙加熱鐘罩、中心轉運庭、獨立噴射冷卻罩及煙氣/介質附房',
    }
    a = Build(brief)
    a.w, a.h, a.d = 57, 49, 57
    cx = cz = 28

    # One octagonal raft ties every station and service wing to the ground.
    _fill_oct(a, cx, cz, 28, 0, 0, FOUNDATION)
    _oct_course(a, cx, cz, 28, 26, 1, FRAME)
    _oct_course(a, cx, cz, 26, 24, 2, HOOD)
    for y in (3, 4, 5):
        for x in range(cx - 26, cx + 27):
            for z in range(cz - 26, cz + 27):
                if not (_inside_oct(x - cx, z - cz, 26) and
                        not _inside_oct(x - cx, z - cz, 24)):
                    continue
                # Four vehicle gates interrupt the low octagonal yard wall.
                north_gate = z == cz - 26 and 24 <= x <= 32
                south_gate = z == cz + 26 and 24 <= x <= 32
                west_gate = x == cx - 26 and 24 <= z <= 32
                east_gate = x == cx + 26 and 24 <= z <= 32
                if not (north_gate or south_gate or west_gate or east_gate):
                    a.set(x, y, z, FRAME if y in (3, 5) else HOOD)

    # Distinct process bells, arranged as a triangle instead of a linear kiln hall.
    zones = []
    zones.append(_bell(a, 14, 15, '西北加热钟罩・保护气氛退火座',
                       [(5, 8, 8), (9, 20, 8), (21, 24, 7), (25, 28, 6),
                        (29, 32, 5), (33, 35, 4), (36, 38, 3), (39, 39, 2), (40, 40, 1)], True))
    zones.append(_bell(a, 42, 15, '东北加热钟罩・均质重构座',
                       [(5, 8, 8), (9, 18, 8), (19, 22, 7), (23, 26, 6),
                        (27, 30, 5), (31, 33, 4), (34, 35, 3), (36, 36, 2), (37, 37, 1)], True))
    zones.append(_bell(a, 28, 43, '南侧喷射冷却钟罩',
                       [(5, 8, 8), (9, 12, 8), (13, 15, 7), (16, 16, 6),
                        (17, 17, 5), (18, 20, 4), (21, 21, 3),
                        (22, 23, 2), (24, 26, 1)], False))

    # A low octagonal rotary table remains the visual and material-transfer center.
    _fill_oct(a, cx, cz, 5, 1, 2, FOUNDATION)
    _oct_course(a, cx, cz, 6, 5, 2, FRAME)
    _oct_course(a, cx, cz, 4, 2, 3, GEAR)
    _fill_oct(a, cx, cz, 1, 3, 4, HOOD)
    for x0, x1, z0, z1 in ((cx - 3, cx + 3, cz - 1, cz + 1),
                           (cx - 1, cx + 1, cz - 3, cz + 3)):
        a.box((x0, 3, z0), (x1, 3, z1), GEAR)
    a.box((cx - 2, 4, cz - 2), (cx + 2, 5, cz + 2), HOOD, True)
    a.box((cx - 1, 3, cz - 1), (cx + 1, 6, cz + 1), GEAR)
    a.set(cx, 7, cz, HOOD)
    zones.append({
        'name': '八角回转装料庭', 'kind': 'rotary_transfer_court',
        'min': [cx - 6, 1, cz - 6], 'max': [cx + 6, 6, cz + 6],
        'pos': [cx, 7, cz], 'role': '低位轉台與三向地面轉運軸意象',
        'service_face': '三座罩式爐座',
    })

    # Three square-cornered roller ways meet the court without crossing the entry aisle.
    _orthogonal_rail(a, [(22, 15), (23, 15), (23, 22), (25, 22)], 2, GEAR)
    _orthogonal_rail(a, [(34, 15), (33, 15), (33, 22), (31, 22)], 2, GEAR)
    _orthogonal_rail(a, [(28, 35), (28, 34), (28, 33)], 2, GEAR)
    a.links = [
        {'from': zones[0]['name'], 'to': '八角回轉裝料庭', 'route': [[22, 2, 15], [23, 2, 15], [23, 2, 22], [25, 2, 22]]},
        {'from': zones[1]['name'], 'to': '八角回轉裝料庭', 'route': [[34, 2, 15], [33, 2, 15], [33, 2, 22], [31, 2, 22]]},
        {'from': zones[2]['name'], 'to': '八角回轉裝料庭', 'route': [[28, 2, 35], [28, 2, 34], [28, 2, 33]]},
    ]

    zones.append(_pavilion(a, 4, 24, 7, 9, 15, COLD, FRAME, '西侧冷却介质换热附房', 'west'))
    zones.append(_pavilion(a, 46, 24, 7, 9, 18, DUCT, FILTER, '东侧保护气氛净化附房', 'east'))
    # External utility headers use right-angle runs and stay below the bell windows.
    _orthogonal_rail(a, [(11, 28), (11, 21), (14, 21)], 6, DUCT)
    _orthogonal_rail(a, [(46, 28), (46, 21), (42, 21)], 6, DUCT)
    _orthogonal_rail(a, [(10, 28), (12, 28)], 6, VENT)

    # Low gantry piers and yard gates frame the approaches, not the furnace tops.
    for x in (24, 32):
        a.box((x, 2, 2), (x, 8, 4), FRAME)
        a.box((x, 2, 52), (x, 8, 54), FRAME)
    a.box((24, 9, 2), (32, 10, 4), HOOD)
    a.box((24, 9, 52), (32, 10, 54), HOOD)
    for z in (24, 32):
        a.box((2, 2, z), (4, 8, z), FRAME)
        a.box((52, 2, z), (54, 8, z), FRAME)
    a.box((2, 9, 24), (4, 10, 32), HOOD)
    a.box((52, 9, 24), (54, 10, 32), HOOD)

    # Front gate controller marker follows the project's existing visual convention.
    controller = [28, 6, 2]
    a.box((26, 5, 3), (30, 8, 4), CLEAN, True)
    for x in (27, 29):
        a.set(x, 6, 2, CLEAN)
    a.set(28, 5, 2, CLEAN)
    a.set(28, 7, 2, CLEAN)
    a.set(*controller, DIAMOND)
    a.box((27, 9, 3), (29, 9, 4), FRAME)

    port_specs = [
        ('BILLET', [11, 5, 7], '北側西爐座：魂鋼坯料輸入候選'),
        ('POWER', [17, 5, 7], '北側西爐座：加熱供能候選'),
        ('ATMOSPHERE', [39, 5, 7], '北側東爐座：保護氣氛輸入候選'),
        ('THERMAL_LOG', [45, 5, 7], '北側東爐座：熱史資料輸出候選'),
        ('COOLANT', [25, 5, 35], '南側冷卻爐座：冷卻介質輸入候選'),
        ('PRODUCT', [31, 5, 35], '南側冷卻爐座：成品輸出候選'),
    ]
    ports = []
    for key, pos, purpose in port_specs:
        a.set(*pos, PORT)
        ports.append({'id': key, 'pos': pos, 'face': 'north', 'purpose': purpose})

    paths = [
        {'name': '北門至回轉庭的地面主檢修道', 'min': [27, 1, 1], 'max': [29, 4, 22]},
    ]
    # Reopen the gate through both the perimeter wall and the court's low curb.
    for x in range(27, 30):
        for y in range(1, 5):
            for z in range(1, 23):
                a.b.pop((x, y, z), None)
    a.zones = zones
    a.paths = paths
    return {
        'key': 'i15', 'name': 'i15-soulsteel-anneal-furnace-v4',
        'title': '魂钢重构退火炉', 'candidate_version': 'V4 三钟回转炉院・暖橙热端与冷蓝淬冷配色修订',
        'size': [a.w, a.h, a.d], 'core_marker': controller,
        'visual_core': [cx, 7, cz], 'controller': controller,
        'ports': ports, 'paths': paths, 'zones': zones, 'links': a.links,
        'brief': brief,
        'description': (
            '三座彼此独立的罩式退火设备围成三角形：北侧两座较高的钟罩负责加热与均质意象，'
            '南侧较低的钟罩以冷色外壳和散热带表现喷射冷却。三向地面滚道汇入低矮八角回转庭，'
            '院墙、北门、烟气净化与冷却介质附房共同形成一座紧凑的工业炉院；不沿用 V2 的长向炉廊、'
            '中央高架格舱或偏置单塔。这是参照多炉座罩式退火设备后的原创方块化布局。'
        ),
        'role_materials': {key: sorted(value) for key, value in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


def _material_basis(states, counts):
    resources = Resources(instance=INSTANCE)
    rows = []
    try:
        for state in states:
            if state in MARKERS:
                rows.append({'block_state': state, 'count': counts[state],
                             'role': '项目规定的核心/接口标记', 'complete_cube': True,
                             'note': '接口为惰性外观占位；不代表任何仓室、供能或数据能力。'})
                continue
            material = resources.material(state)
            ns, block = state.split(':', 1)
            block = block.split('[', 1)[0]
            source = resources.sources.get(f'assets/{ns}/blockstates/{block}.json', 'resource source unavailable')
            rows.append({'block_state': state, 'count': counts[state],
                         'role': MATERIAL_ROLES.get(state, 'structure block'),
                         'model': material['model'], 'complete_cube': material['complete_cube'],
                         'resource_source': source,
                         'survival_recipe_and_stage': 'not verified'})
    finally:
        resources.close()
    return rows


def _write_reference():
    (OUT / '设计参考.json').write_text(json.dumps({
        'machine': 'I15 魂钢重构退火炉 · 三钟回转炉院 V4 配色修订',
        'sources': [{
            'title': 'Tenova · Two new HPH Bell-Type Furnaces for Wire Coils',
            'url': 'https://tenova.com/newsroom/latest-tenova/two-new-hphr-bell-type-furnaces-wire-coils',
            'used_as': '罩式退火設備的多爐座組織參照；該案例描述三個爐座、兩個加熱罩和一個噴射冷卻罩。',
        }, {
            'title': 'Tenova · Rotary Bell-Type Annealing Furnace (R-BAF)',
            'url': 'https://tenova.com/technologies/rotary-bell-type-annealing-furnace-r-baf-silicon-steel-strip',
            'used_as': '回轉罩式退火設備與爐院內轉運概念參照。',
        }],
        'original_translation': '將兩座加熱罩與一座噴射冷卻罩重新組成三角爐院；增加低位回轉庭、八角院牆及分置的煙氣淨化和冷卻介質附房。佈局與形體為原創轉譯，並非照搬現場設備。',
        'boundary': '現實設備資料只支持外觀組織參照，不代表遊戲配方、Pattern、倉室能力或運行邏輯已實現。',
    }, ensure_ascii=False, indent=2), encoding='utf-8')


def _write_pack_review():
    root = INSTANCE.parent
    manifest = json.loads((root / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))
    expected = [row for row in manifest['files'] if row['path'].startswith('mods/') and row['path'].endswith('.jar')]
    installed = {path.name: path for path in (INSTANCE / 'mods').glob('*.jar')}
    expected_names = {Path(row['path']).name for row in expected}
    unlisted = sorted(set(installed) - expected_names)
    hash_mismatch = sorted(
        Path(row['path']).name for row in expected
        if Path(row['path']).name in installed and row.get('hashes', {}).get('sha1') and
        hashlib.sha1(installed[Path(row['path']).name].read_bytes()).hexdigest() != row['hashes']['sha1']
    )
    (OUT / '2.8实例与崩溃复核.json').write_text(json.dumps({
        'manifest_version': manifest.get('versionId'),
        'minecraft': manifest.get('dependencies', {}).get('minecraft'),
        'forge': manifest.get('dependencies', {}).get('forge'),
        'manifest_jar_count': len(expected), 'installed_jar_count': len(installed),
        'missing_manifest_jars': sorted(expected_names - set(installed)),
        'manifest_hash_mismatch': hash_mismatch,
        'unlisted_local_jars': unlisted,
        'duplicate_jecharacters': sorted(name for name in installed if name.lower().startswith('jecharacters-')),
        'crash_report': 'crash-2026-10-16_00.29.18-fml.txt',
        'crash_finding': 'Forge 啟動期 ftb-ultimine-forge-2001.1.8 的客戶端按鍵映射註冊拋出 ArrayIndexOutOfBoundsException: Index 1 out of bounds for length 0；調用經 Architectury 9.2.14 KeyMappingRegistryImpl.register。',
        'crash_memory': {'used_mib': 521, 'max_mib': 8192, 'out_of_memory': False},
        'version_caveat': 'Prism 實例資料夾與 instance.cfg 仍稱 2.7；mrpack 清單 versionId 是 2.8。崩潰報告本身未嵌入可靠的整合包版本號。',
        'actions_taken': 'Modrinth 2.8 的 mrpack 清單與模組檔案未更動；為驗證啟動竞态，已備份 fml.toml 並暫設 maxThreads=1，客戶端已到標題介面，未載入世界。',
    }, ensure_ascii=False, indent=2), encoding='utf-8')


def _write_index(data, audit):
    w, h, d = data['size']
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I15 · 三鐘回轉爐院 V4 配色修訂</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#111816;color:#edf2ee;font:16px/1.7 "Microsoft YaHei",sans-serif}}a{{color:#9fd8d0;text-decoration:none}}a:hover{{color:#fff}}main{{max-width:1440px;margin:auto;padding:30px clamp(18px,4vw,56px) 48px}}.tag{{color:#a3c0b7;font-size:13px}}h1{{font-size:34px;line-height:1.25;margin:8px 0}}.lede{{max-width:920px;color:#c4d0ca;margin:0 0 20px}}nav{{display:flex;gap:20px;flex-wrap:wrap;margin:18px 0 22px}}nav a{{padding:8px 0;border-bottom:1px solid #668f84}}.hero{{border-top:1px solid #40524b;border-bottom:1px solid #40524b;background:#18211e;padding:10px}}.hero img{{display:block;width:100%;max-height:700px;object-fit:contain}}.facts{{display:flex;gap:24px;flex-wrap:wrap;color:#c2d1c9;margin:16px 0}}.facts b{{color:#f0d9a7;font-weight:600}}.band{{border-top:1px solid #3a4b44;margin-top:28px;padding-top:17px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}}h2{{font-size:18px;margin:0 0 6px}}.band p,.note{{color:#bcc9c2;margin:0}}.note{{font-size:14px;margin-top:24px;max-width:1050px}}@media(max-width:760px){{main{{padding-top:22px}}h1{{font-size:29px}}.band{{grid-template-columns:1fr;gap:16px}}}}</style></head><body><main>
<div class="tag">HK3GTL · I15 · 配色修订候选 V4</div><h1>魂钢重构退火炉 · 三钟回转炉院</h1>
<p class="lede">三座罩式退火炉围绕低位转运庭组成三角炉院：两座高热罩与一座喷射冷却罩构成清晰的高低关系，外围配有八角院墙、烟气净化和冷却介质附房。</p>
<nav><a href="三维评审.html">打开可旋转三维评审</a><a href="{data['name']}.schem">下载 Sponge Schematic</a><a href="{data['name']}.nbt">下载结构 NBT</a><a href="设计与检查.json">结构与审计记录</a><a href="材料依据.json">逐块材料依据</a><a href="设计参考.json">现实参照</a><a href="2.8实例与崩溃复核.json">2.8 实例与崩溃复核</a></nav>
<div class="hero"><img src="等轴预览.png" alt="魂钢重构退火炉三钟回转炉院 V4 配色修订"></div>
<div class="facts"><span><b>{w} × {d} × {h}</b> 方块（宽×深×高）</span><span><b>{len(data['blocks']):,}</b> 个实体方块</span><span><b>{len(data['zones'])}</b> 个建筑分区</span><span>69 座规划下限：29 × 49 × 27，通过</span></div>
<section class="band"><div><h2>双加热钟罩</h2><p>两个独立罩式炉座以不同高度的烟气净化烟囱标出热处理分区；观察带露出内部线圈与耐热炉床意象。</p></div><div><h2>八角回转庭</h2><p>三条直角滚道汇入低位回转台，北门留出连续步行检修道；入口钻石块沿用项目现行的结构识别约定。</p></div><div><h2>喷射冷却与介质附房</h2><p>南侧低罩以冷色外壳和散热片区别于热端，左右两侧把冷却介质换热与保护气氛净化分开布置。</p></div></section>
<section class="band"><div><h2>现实设备参照</h2><p>Tenova 的罩式退火设备案例展示三座炉座、两只加热罩和一只喷射冷却罩。</p><p><a href="https://tenova.com/newsroom/latest-tenova/two-new-hphr-bell-type-furnaces-wire-coils">Tenova · Bell-Type Furnaces ↗</a></p></div><div><h2>原创方块化布局</h2><p>把多炉座工艺组织重新组合为三角形炉群和回转庭，不复制现实厂房的尺寸或设备外形。</p><p><a href="设计参考.json">查看参照边界</a></p></div><div><h2>候选状态</h2><p>该版本只表达建筑外观。接口为惰性填充块，配方、仓室能力和正式 Pattern 尚未接入。</p><p><a href="2.8实例与崩溃复核.json">查看实例检查结果</a></p></div></section>
<p class="note">候选结构，待用户审阅。所有普通材料已按当前实例静态核验为完整方块模型；生存阶段可达性、正式 Pattern、接口能力、Minecraft 成型与运行均未验收。本轮未改动测试实例。</p>
</main></body></html>'''
    (OUT / 'index.html').write_text(page, encoding='utf-8')


def _bundle():
    target = OUT / ARCHIVE
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path != target:
                archive.write(path, path.relative_to(OUT))
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert all(archive.read(name) == (OUT / name).read_bytes() for name in archive.namelist())
    return {'file': target.name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'bytes': target.stat().st_size, 'entries_equal_disk': True}


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    data['construction_notes'] = {
        'origin': [0, 0, 0], 'paste_anchor': [0, 0, 0], 'schematic_offset': [0, 0, 0],
        'orientation': 'X 向東、Y 向上、Z 向南；接口朝北（-Z）。',
        'recommended_bottom_world_y': -60,
        'world_height_range': [-60, -60 + data['size'][1] - 1],
        'status': 'V4 配色修訂候選，幾何沿用已批准 V3；待用戶審閱，未部署。',
        'core_marker': '入口鑽石塊是項目既有結構識別標記，不代表遊戲控制器已接入。',
        'ports': 'industrial_port_casing 僅為惰性外觀占位，不具物品、流體或供能能力。',
        'recipe_boundary': '工藝分區是建築意象，不代表 I15 當前配方已覆蓋對應處理路線。',
    }
    preview.TEST_INSTANCE = INSTANCE
    preview.package(data, OUT, 'i07', [
        '三座罩式爐以三角形排布，與 V2 長向爐廊和高架核心輪廓不同',
        '尺寸逐軸不低於69座規劃下限，且外沿由實體方塊構成',
        '全部構件採水平/垂直網格完整方塊，接口前方保持淨空',
        '每種普通方塊均從 2.8 目標實例解析並核驗完整模型',
    ])
    nbt_sha = lodestone_export(data, OUT, LOG)
    schem = OUT / (data['name'] + '.schem')
    nbt = OUT / (data['name'] + '.nbt')
    structure = nbtlib.load(schem)
    structure['Offset'] = nbtlib.IntArray([0, 0, 0])
    structure.save(schem, gzipped=True)

    states = {tuple(row['pos']): row['state'] for row in data['blocks']}
    assert states[tuple(data['controller'])] == DIAMOND
    assert len(data['ports']) == 6 and sum(state == PORT for state in states.values()) == 6
    record_path = OUT / '设计与检查.json'
    record = json.loads(record_path.read_text(encoding='utf-8'))
    audit = record['audit']
    counts = collections.Counter(row['state'] for row in data['blocks'])
    audit.update({
        'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'instance': str(INSTANCE), 'candidate_version': data['candidate_version'],
        'approval': 'V4 配色修訂候選；幾何沿用已批准 V3，待用戶審閱，未部署。',
        'hashes': {'nbt': nbt_sha, 'schem': hashlib.sha256(schem.read_bytes()).hexdigest()},
        'design_markers': {key: counts[key] for key in MARKERS},
        'material_counts': dict(sorted(counts.items())),
        'material_basis': '材料依据.json',
        'checks': audit['checks'] + [
            'Minecraft Builder/Lodestone NBT 已重新導出並逐格回讀一致',
            'Schematic Offset 已設為 [0,0,0]',
            '三向滾道逐段檢查為直角路徑',
            '2.8 實例模組清單、實際 jar 數與崩潰報告分別記錄',
        ],
        'not_verified': [
            '普通材料的配方、科技前置與生存階段可達性',
            'I15 正式 Pattern、倉室能力與結構成型',
            'Minecraft 遊戲內朝向、多人交互與實際運行',
            '用戶對 V4 配色修訂的最終批准',
        ],
    })
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / '材料依据.json').write_text(json.dumps({
        'target_instance': str(INSTANCE),
        'scope': '靜態資源解析與完整模型核驗；不評估生存配方或階段可達性。',
        'materials': _material_basis(sorted(counts), counts),
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    _write_reference()
    _write_pack_review()

    payload_path = OUT / 'data.js'
    encoded = json.loads(payload_path.read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    payload['audit'] = audit
    payload['data'] = record['data']
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False,
        separators=(',', ':')).encode('utf-8'), compresslevel=9)).decode('ascii')
    payload_path.write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')

    page_path = OUT / '三维评审.html'
    page = page_path.read_text(encoding='utf-8')
    page = page.replace('<title>探测器精密校准台 · 自由设计候选</title>', '<title>I15 · 魂钢重构退火炉 · 三钟回转炉院 V4 配色修订</title>')
    page = page.replace('<a href="设计与检查.json">← 设计与检查</a>', '<a href="index.html">← 三钟回转炉院</a>')
    page = page.replace('<h1>探测器精密校准台</h1>', '<h1>魂钢重构退火炉 · 三钟回转炉院</h1>')
    page = page.replace('待审预览', 'V4 配色修订候选')
    page = page.replace('本机建筑概念</summary><p>', '三钟回转炉院概念</summary><p>')
    page = page.replace('纵向四区连续退火厂：前端气闸上料，经四段梯度热处理后进入后端淬冷整形池，侧塔记录温度曲线并完成检测。', data['description'])
    page = page.replace('i15-soulsteel-anneal-free.nbt', data['name'] + '.nbt')
    page = page.replace('i15-soulsteel-anneal-free.schem', data['name'] + '.schem')
    page = page.replace('未接入生产Pattern，未实测浏览器交互或游戏。此处为实际方块坐标与本地纹理渲染，首帧材质不代表全部动态效果。',
        'V4 配色修訂候選，幾何沿用已批准 V3。方塊資源模型已按 2.8 實例靜態核驗；正式 Pattern、配方、成型和遊戲運行尚未驗收。')
    page_path.write_text(page, encoding='utf-8')

    _write_index(data, audit)
    index_path = OUT / 'index.html'
    index_path.write_text(index_path.read_text(encoding='utf-8').replace(
        '三鐘回轉爐院', '三钟回转炉院'), encoding='utf-8')
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    shutil.copy2(Path(__file__).with_name('verify_i15_soulsteel_anneal_v4_palette.py'),
                 OUT / 'verify_i15_soulsteel_anneal_v4_palette.py')
    entry = {
        'machine': data['title'], 'candidate_version': data['candidate_version'],
        'size_xyz': data['size'], 'size_wdh': [data['size'][0], data['size'][2], data['size'][1]],
        'blocks': len(data['blocks']), 'materials': len(counts), 'zones': len(data['zones']),
        'ports': len(data['ports']), 'controller_marker': data['controller'],
        'visual_core': data['visual_core'], 'size_baseline': audit['size_baseline'],
        'instance': str(INSTANCE), 'approval': audit['approval'], 'hashes': audit['hashes'],
    }
    (OUT / 'manifest.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
    archive = _bundle()
    entry['archive'] = archive
    (LOG / 'final-verification.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(entry, ensure_ascii=False))


if __name__ == '__main__':
    main()
