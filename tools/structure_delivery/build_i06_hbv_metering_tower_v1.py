# -*- coding: utf-8 -*-
"""I06 HBV 高位计量与分级混配塔 V1；仅生成独立审阅候选。"""
from __future__ import annotations

import base64
import collections
import datetime as dt
import gzip
import hashlib
import json
import re
import shutil
from pathlib import Path

from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import ROOT
from structure_size_baseline import require


SOURCE = (ROOT / 'deliveries/多方块确认归档/20261023_133546_133059_I01-I18_主控居中融合V2_已确认'
          / 'confirmed_v2/i06/blueprint.json')
SOURCE_SHA256 = '2efe1647b518c3f93e30560ee19c0a9fa4350b862179c3b08d8be865f1703d08'
SOURCE_REVIEW = SOURCE.parent / '三维评审.html'
VIEWER = SOURCE.parent / 'viewer.bundle.js'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
PACK_INDEX = INSTANCE.parent / 'mrpack/modrinth.index.json'
OUT = ROOT / 'deliveries/I06_崩坏能燃料调配厂_高位计量与分级混配塔_V1_20261026'
NAME = 'i06-hbv-metering-blending-tower-v1'
PORT = 'hk3gtl:industrial_port_casing'
HBV = 'hk3gtl:voltage_machine_casing_hbv'
ROBUST = 'gtceu:robust_machine_casing'
CORROSION = 'gtceu:corrosion_proof_casing'
HEATPROOF = 'gtceu:heatproof_machine_casing'
GLASS = 'gtceu:laminated_glass'
GEARBOX = 'gtceu:tungstensteel_gearbox'
VENT = 'gtceu:computer_heat_vent'
PTFE = 'gtceu:ptfe_pipe_casing'
TITANIUM = 'gtceu:titanium_pipe_casing'
GRATING = 'gtceu:assembly_line_grating'
EVAPORATION = 'gtceu:stainless_evaporation_casing'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def outline(x0: int, x1: int, z0: int, z1: int):
    for x in range(x0, x1 + 1):
        yield x, z0
        yield x, z1
    for z in range(z0 + 1, z1):
        yield x0, z
        yield x1, z


def build() -> tuple[dict, dict]:
    if digest(SOURCE) != SOURCE_SHA256:
        raise ValueError('确认版 I06 V2 蓝图哈希变化，拒绝以非确认来源派生。')
    source = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
    cells = {tuple(block['pos']): block['state'] for block in source['blocks']}
    if len(cells) != len(source['blocks']):
        raise ValueError('确认版蓝图存在重复坐标。')
    replacements = []
    additions = []

    def put(pos, state, *, replace=False, keep_existing=False):
        pos = tuple(pos)
        old = cells.get(pos)
        if old == state:
            return
        if old is not None:
            if keep_existing:
                return
            if not replace:
                raise ValueError(f'新几何与确认版重叠：{pos} {old} -> {state}')
            replacements.append({'pos': list(pos), 'before': old, 'after': state})
        else:
            additions.append(list(pos))
        cells[pos] = state

    def line(a, b, state):
        if sum(a[i] != b[i] for i in range(3)) != 1:
            raise ValueError('只支持轴向封闭输送线。')
        axis = next(i for i in range(3) if a[i] != b[i])
        step = 1 if b[axis] > a[axis] else -1
        pos = list(a)
        while True:
            put(pos, state, replace=True)
            if pos[axis] == b[axis]:
                return
            pos[axis] += step

    # 三座独立料仓沿原有阶梯基座向上延伸，分别承担计量、稳态介质与催化剂缓冲。
    silos = [
        {'id': 'BASE', 'center': [8, 17], 'base_top': 12, 'top': 32, 'route_y': 30},
        {'id': 'MEDIUM', 'center': [8, 25], 'base_top': 17, 'top': 38, 'route_y': 36},
        {'id': 'CATALYST', 'center': [8, 33], 'base_top': 22, 'top': 44, 'route_y': 42},
    ]
    for silo in silos:
        cx, cz = silo['center']
        start, top = silo['base_top'] + 1, silo['top']
        x0, x1, z0, z1 = cx - 3, cx + 3, cz - 3, cz + 3
        route_y = silo['route_y']
        for y in range(start, top + 1):
            collar = y in (start, top) or (y - start) % 6 == 0
            for x, z in outline(x0, x1, z0, z1):
                if x in (x0, x1) and z in (z0, z1):
                    state = ROBUST
                elif collar:
                    state = CORROSION
                else:
                    state = HBV
                if (z == z0 and x in (cx - 1, cx, cx + 1)
                        and start + 3 <= y <= top - 3 and (y - start) % 8 in (2, 3, 4)):
                    state = GLASS
                put((x, y, z), state)
            if y != route_y and (y - start) % 6 == 3:
                line((cx, y, cz), (x1, y, cz), HEATPROOF)
                put((cx, y, cz), GEARBOX, replace=True)
            elif y != route_y and (y - start) % 6 == 4:
                put((cx, y, cz), VENT)
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                put((x, top + 1, z), HEATPROOF)
        for x, z in outline(cx - 2, cx + 2, cz - 2, cz + 2):
            put((x, top + 2, z), EVAPORATION)
        put((cx, top + 2, cz), HEATPROOF)
        put((cx, top + 3, cz), VENT)

    # 中央塔以既有双轴混合床为承台，X=27严格落在整机55格宽度中线。
    tower = {'x0': 23, 'x1': 31, 'z0': 19, 'z1': 27, 'y0': 15, 'y1': 48}
    for x, z in outline(tower['x0'], tower['x1'], tower['z0'], tower['z1']):
        for y in range(tower['y0'], tower['y1'] + 1):
            collar = y in (15, 16, 21, 27, 33, 39, 45, 47, 48)
            corner = x in (tower['x0'], tower['x1']) and z in (tower['z0'], tower['z1'])
            state = ROBUST if corner else (CORROSION if collar else HBV)
            window_levels = set(range(23, 26)) | set(range(32, 35)) | set(range(41, 44))
            window = z == tower['z0'] and x in (26, 27, 28) and y in window_levels
            if window:
                state = GLASS
            put((x, y, z), state, replace=y in (15, 16))

    # 短支墩把塔裙座压回混配床；与原床表面相遇时复用原方块承载。
    for x, z in ((23, 19), (31, 19), (23, 27), (31, 27)):
        for y in range(11, 15):
            put((x, y, z), ROBUST, keep_existing=True)

    # 四道环形检修层围绕塔身，格栅层均可从外沿连续步行。
    for y in (21, 27, 33, 39, 45):
        for x, z in outline(22, 32, 18, 28):
            if (x, z) not in set(outline(tower['x0'], tower['x1'], tower['z0'], tower['z1'])):
                put((x, y, z), GRATING)
        for x, z in outline(22, 32, 18, 28):
            if (x, z) in ((22, 18), (22, 28), (32, 18), (32, 28)):
                put((x, y + 1, z), ROBUST)

    # 混配芯轴只在工艺节点布置齿轮箱与散热块，保留塔内可见空腔。
    route_levels = {silo['route_y'] for silo in silos}
    for y in range(18, 48):
        if y not in route_levels and y % 5 in (0, 1):
            line((27, y, 23), (31, y, 23), ROBUST)
            put((27, y, 23), GEARBOX if y % 5 == 0 else VENT, replace=(27, y, 23) in cells)
        if y % 6 == 0:
            line((27, y, 23), (31, y, 23), ROBUST)
            put((26, y, 23), VENT, replace=(26, y, 23) in cells)
            put((28, y, 23), VENT, replace=True)
    for x in range(24, 31):
        put((x, 47, 23), CORROSION)
    for z in range(20, 27):
        put((27, 47, z), CORROSION)
    put((27, 48, 23), EVAPORATION)

    # 三条独立封闭支线接入塔体不同高度；塔壁接头是管路的一部分，不是外置接口。
    routes = [
        {'id': 'BASE', 'level': 30, 'z': 17, 'path': [[8, 30, 17], [22, 30, 17], [22, 30, 23], [23, 30, 23]], 'state': PTFE},
        {'id': 'MEDIUM', 'level': 36, 'z': 25, 'path': [[8, 36, 25], [23, 36, 25]], 'state': TITANIUM},
        {'id': 'CATALYST', 'level': 42, 'z': 33, 'path': [[8, 42, 33], [22, 42, 33], [22, 42, 27], [27, 42, 27]], 'state': PTFE},
    ]
    for route in routes:
        for start, end in zip(route['path'], route['path'][1:]):
            line(start, end, route['state'])
        if route['id'] == 'BASE':
            line((23, 30, 23), (27, 30, 23), TITANIUM)
        elif route['id'] == 'MEDIUM':
            line((23, 36, 25), (27, 36, 25), TITANIUM)
        else:
            line((27, 42, 27), (27, 42, 23), TITANIUM)

    size = [55, 49, 41]
    blocks = [{'pos': list(pos), 'state': state} for pos, state in sorted(cells.items())]
    data = dict(source)
    data.update({
        'key': 'i06', 'name': NAME, 'title': '崩坏能燃料调配厂',
        'size': size, 'blocks': blocks, 'block_count': len(blocks),
        'controller': [27, 2, 17], 'controller_face': 'north',
        'target_voltage': 'HBV', 'target_casing': HBV,
        'candidate_version': '高位计量与分级混配塔 V1・待审',
        'approval_status': '待负责人审阅，未批准、未接入正式Pattern或实例',
        'brief': {'id': 'I06', 'title': '崩坏能燃料调配厂',
                  'minimum_wdh': [55, 41, 29],
                  'form': '三座阶梯计量仓、中心高位混配塔、三路密闭管廊与东侧低位灌装坞',
                  'flow': '三种原料分别从高位仓计量，经不同高度的封闭支线进入中心混配塔，再回落至双轴混合床与低位灌装线'},
        'zones': [
            {'name': '三段高位计量仓', 'min': [2, 0, 14], 'max': [14, 47, 36], 'pos': [8, 44, 25], 'role': '燃料基质、稳定介质、催化剂独立缓冲与计量', 'kind': 'metering_silos', 'service_face': '北侧接口与东侧计量观察面'},
            {'name': '双轴混配承台', 'min': [16, 0, 14], 'max': [42, 16, 36], 'pos': [29, 16, 25], 'role': '两级混合、转矩传递与塔体承载', 'kind': 'twin_drum_blending_bed', 'service_face': '四周维护'},
            {'name': '中心分级混配塔', 'min': [22, 15, 18], 'max': [32, 48, 28], 'pos': [27, 48, 23], 'role': '分层汇料、稳态调配与可观察混配芯轴', 'kind': 'staged_blending_tower', 'service_face': '西侧进料与环形检修层'},
            {'name': '三路高位密闭输送廊', 'min': [8, 30, 17], 'max': [27, 42, 33], 'pos': [21, 42, 25], 'role': '三类原料分层输送并接入混配塔', 'kind': 'enclosed_transfer_galleries', 'service_face': '顶部维护'},
            {'name': '后部热交换回路', 'min': [15, 1, 37], 'max': [43, 11, 40], 'pos': [29, 11, 38], 'role': '混配后调温与回热', 'kind': 'heat_exchange_wall', 'service_face': '南侧维护'},
            {'name': '东侧低位灌装坞', 'min': [44, 0, 10], 'max': [54, 13, 40], 'pos': [49, 13, 25], 'role': '产品缓冲、分流与灌装交付', 'kind': 'low_filling_dock', 'service_face': '北侧服务面'},
        ],
        'links': [
            {'from': '三段高位计量仓', 'to': '中心分级混配塔', 'route': [r['path'] for r in routes]},
            {'from': '中心分级混配塔', 'to': '双轴混配承台', 'route': [[27, 30, 23], [27, 18, 23]]},
            {'from': '双轴混配承台', 'to': '后部热交换回路', 'route': [[23, 11, 34], [23, 11, 38], [40, 11, 38], [40, 9, 34]]},
            {'from': '双轴混配承台', 'to': '东侧低位灌装坞', 'route': [[41, 9, 27], [46, 9, 27], [49, 9, 27], [49, 9, 25]]},
        ],
        'description': '把原来卧铺式混配床提升为三级计量—高位汇料—双轴调配的立体燃料厂。西侧三座原料仓由阶梯底仓向上延伸，分别以不同高度的封闭支线接入中线混配塔；塔裙座落在原双轴承台上，环形检修层围绕可观察的芯轴布置。后部温控墙与东侧低位灌装坞继续承担热交换和交付，主控留在X=27中线的原承重鞍座，六个接口坐标与朝向全部保留。',
        'role_materials': {'HBV主体': [HBV], '承载与塔裙': [ROBUST, HEATPROOF],
                           '耐腐蚀分区': [CORROSION, EVAPORATION], '观察与输送': [GLASS, PTFE, TITANIUM],
                           '传动与热管理': [GEARBOX, VENT], '维护层': [GRATING]},
        'material_usage': dict(collections.Counter(state for state in cells.values())),
        'source_identity': {'source_blueprint': str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
                            'source_sha256': SOURCE_SHA256, 'confirmed_source': True},
        'candidate_revision': {'revision': 'high-metering-mixing-tower-v1',
                               'created_at': dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
                               'status': '待审', 'target_voltage': 'HBV',
                               'source_revision': 'I01-I18 主控居中融合 V2',
                               'changed_existing_blocks': len(replacements),
                               'added_blocks': len(additions)},
        'change_log': [{'reason': '提高计量、混配与输送设备的纵向组织和现实工程层级',
                        'source': 'I06已确认V2，不覆盖历史文件',
                        'controller_and_ports': '主控[27,2,17]及六口保留'}],
        'construction_notes': {
            'orientation': 'X向东、Y向上、Z向南；主控正面朝-Z。',
            'origin': [0, 0, 0], 'paste_anchor': [0, 0, 0],
            'recommended_bottom_world_y': -60, 'world_height_range': [-60, -12],
            'controller': '主控位于宽55格的中心列X=27，嵌入双轴混配承重鞍座；坐标与接口沿用确认V2。',
            'status': '外观候选待审；未改正式Pattern、正式资源或游戏实例。',
        },
    })
    data['blocks'] = blocks
    data['source_replacements'] = replacements
    return data, {'additions': additions, 'replacements': replacements, 'silos': silos, 'routes': routes}


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f'候选输出目录已存在，拒绝覆盖：{OUT}')
    data, geometry = build()
    size_check = require(data)
    occupied = {tuple(block['pos']): block['state'] for block in data['blocks']}
    if len(occupied) != len(data['blocks']):
        raise ValueError('输出蓝图存在重复坐标。')
    controller = tuple(data['controller'])
    if controller[0] != (data['size'][0] - 1) // 2 or occupied.get(controller) != 'minecraft:diamond_block':
        raise ValueError('主控未落在整机中线，或钻石标记缺失。')
    if sum(state == 'minecraft:diamond_block' for state in occupied.values()) != 1:
        raise ValueError('主控钻石标记必须唯一。')
    if len(data['ports']) != 6:
        raise ValueError('I06 六个接口数量发生变化。')
    port_positions = {tuple(port['pos']) for port in data['ports']}
    actual_ports = {pos for pos, state in occupied.items() if state == PORT}
    if port_positions != actual_ports:
        raise ValueError('接口数量或坐标变化。')
    for port in data['ports']:
        x, y, z = port['pos']
        if occupied.get((x, y, z - 1)) is not None or occupied.get((x, y, z + 1)) is None:
            raise ValueError(f'接口正面净空或背壳不满足：{port["id"]}')
    project_states = {state for state in occupied.values() if state.startswith('hk3gtl:')}
    if project_states != {HBV, PORT}:
        raise ValueError(f'出现白名单外的HK3GTL方块：{sorted(project_states - {HBV, PORT})}')

    # 实例 2.9.2 只用于真实模型/贴图与完整立方体核验。
    pack = json.loads(PACK_INDEX.read_text(encoding='utf-8'))
    if pack.get('versionId') != '2.9.2':
        raise ValueError(f'目标实例版本不是规则记录的2.9.2：{pack.get("versionId")}')
    counts = collections.Counter(occupied.values())
    resources = Resources(instance=INSTANCE, project_resources=ROOT / 'src/main/resources')
    try:
        materials = [resources.material(state) for state in sorted(counts)]
    finally:
        resources.close()
    if any(not item.get('complete_cube') for item in materials):
        raise ValueError('材料库中存在未经证明的完整方块。')

    width, height, depth = data['size']
    bounds = [[min(pos[i] for pos in occupied), max(pos[i] for pos in occupied)] for i in range(3)]
    volume = (bounds[0][1] - bounds[0][0] + 1) * (bounds[1][1] - bounds[1][0] + 1) * (bounds[2][1] - bounds[2][0] + 1)
    baseline = {'machine': 'I04 MAX', 'blocks': 4005, 'materials': 11,
                'bbox_volume': 52675, 'height': 43}
    metrics = {'blocks': len(occupied), 'materials': len(counts), 'bbox_volume': volume,
               'actual_wdh': [bounds[0][1] - bounds[0][0] + 1,
                              bounds[2][1] - bounds[2][0] + 1,
                              bounds[1][1] - bounds[1][0] + 1]}
    if not (metrics['blocks'] > baseline['blocks'] and metrics['materials'] > baseline['materials']
            and volume > baseline['bbox_volume'] and metrics['actual_wdh'][2] > baseline['height']):
        raise ValueError('I06未严格超过较低电压锚点I04的四项量化门槛。')
    connected = {next(iter(occupied))}
    frontier = list(connected)
    while frontier:
        x, y, z = frontier.pop()
        for neighbor in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                         (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
            if neighbor in occupied and neighbor not in connected:
                connected.add(neighbor)
                frontier.append(neighbor)
    if len(connected) != len(occupied):
        raise ValueError(f'存在未连接方块：{len(occupied) - len(connected)}')

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    OUT.mkdir(parents=True)
    states, groups, hashes = export(data, OUT)
    render(data, materials, OUT)
    meta = {key: value for key, value in data.items() if key != 'blocks'}
    audit = {
        'time': now.isoformat(), 'instance': str(INSTANCE), 'instance_version': pack['versionId'],
        'source_blueprint_sha256': SOURCE_SHA256, 'palette': dict(counts), 'hashes': hashes,
        'project_resource_overlay': 'src/main/resources/assets/hk3gtl; 实例文件未改',
        'size_baseline': size_check, 'voltage_progression_baseline': baseline,
        'actual_metrics': metrics, 'bbox_xyz': bounds,
        'checks': ['确认V2蓝图哈希核验', '整机中线主控[27,2,17]及六接口坐标、朝向保留',
                   '69座占地总表宽、深、高下限与实际坐标边界通过',
                   'NBT、Sponge回读与蓝图逐格一致', '14种材料均从增强版2.9.2实例解析且为完整立方体',
                   '所有实体方块六向连通', '超过I04 MAX的方块数、材料种类、包围体积与实际高度'],
        'not_verified': ['14种普通材料的最低可达阶段配方链未逐项闭合；沿用确认V2材质不等于生存可制作验证',
                         '正式Controller tier、Pattern、接口真实能力、配方与游戏成型/运行未验收',
                         '静态预览不包含游戏光照、动画与运行状态',
                         '现实工程感仍需负责人目视审阅；此候选未获批准'],
    }
    payload = {'data': meta, 'palette': states, 'groups': groups,
               'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(
        payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), compresslevel=9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (OUT / 'blueprint.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit,
                                                    'geometry_delta': geometry}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(VIEWER, OUT / 'viewer.bundle.js')
    page = SOURCE_REVIEW.read_text(encoding='utf-8')
    page = page.replace('href="../index.html#i06"', 'href="设计与检查.json"')
    page = page.replace('← 全部21形态', '← 设计与检查')
    page = page.replace('主控置中融合修订V2', '高位计量与分级混配塔 V1 · 候选待审')
    page = page.replace('i06-controller-centered-v2.nbt', NAME + '.nbt')
    page = page.replace('i06-controller-centered-v2.schem', NAME + '.schem')
    page = page.replace('src="../data.js"', 'src="data.js"')
    page = page.replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = re.sub(r'\d+×\d+×\d+（宽深高） · [\d,]+方块',
                  f'{width}×{depth}×{height}（宽深高） · {len(occupied):,}方块', page)
    page = re.sub(r'id="layerValue">\d+', f'id="layerValue">{height - 1}', page)
    page = re.sub(r'id="layer" type="range" min="0" max="\d+" value="\d+"',
                  f'id="layer" type="range" min="0" max="{height - 1}" value="{height - 1}"', page)
    page = re.sub(r'新候选外观待负责人批准；正式控制器/Pattern、真实仓室、配方、生存研究与游戏运行未验收；I14/I15历史电压映射缺口本轮未处理；离线纹理投影；静态步行检查假设外围平地',
                  '本页为待审外观候选；正式Controller tier、Pattern、接口能力、配方、材料生存可达性与游戏运行未验收。', page)
    page = page.replace('以三段阶梯料仓、露天双轴混合床、窄跨维护桁架与东侧灌装坞',
                        '以三座阶梯计量仓、中心高位混配塔、封闭输送廊与低位灌装坞')
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    manifest = {'candidate': meta['candidate_version'], 'source': str(SOURCE),
                'source_sha256': SOURCE_SHA256, 'created_at': now.isoformat(),
                'target_instance': str(INSTANCE), 'target_instance_version': pack['versionId'],
                'size_xyz': data['size'], 'controller': data['controller'],
                'block_count': len(occupied), 'material_count': len(counts),
                'bbox_volume': volume, 'bbox_wdh': metrics['actual_wdh'],
                'added_blocks': len(geometry['additions']),
                'replaced_source_blocks': len(geometry['replacements']),
                'port_count': len(data['ports']), 'ports': data['ports'],
                'nbt_sha256': hashes['nbt'], 'schem_sha256': hashes['schem'],
                'approval_status': '待审；未更新正式Pattern或游戏实例',
                'not_verified': audit['not_verified']}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'instance_version': pack['versionId'],
                      'metrics': metrics, 'baseline': baseline,
                      'blocks': len(occupied), 'materials': len(counts),
                      'controller': data['controller'], 'ports': len(data['ports']),
                      'added': len(geometry['additions']), 'replaced': len(geometry['replacements']),
                      'hashes': hashes}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
