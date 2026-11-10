# -*- coding: utf-8 -*-
"""I18崩坏能燃料棒封装阵列：蓝脊热室与并列封装线建筑候选。

【变更记录 #1】2026-10-22 22:35:10（结构设计候选，不增加模组修订）
删除：无。新增：独立逐格几何、HBV材料审计、同源NBT/Schematic与HTML交付。
修改：不修改旧交付、正式机器、配方、已批准归档或实例。用途：继续I17之后的建筑评审。
输入：当前实例模型、69座尺寸总表；输出：独立交付目录。模型缺失或净空失败时拒绝导出。
【变更记录 #2】2026-10-22 22:43:20（候选封闭性与材料证据补充）
删除：无。新增：有效配方快照依据、内部剖切图、浏览器协议拦截状态。
修改：屋脊相邻高差补齐四个方向；用途：确保采光齿面闭合，区分静态检查与实际交互。
"""
from __future__ import annotations

import base64
import collections
import datetime as dt
import gzip
import hashlib
import html
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

import build_i07_calibration_preview as preview
from build_i09_i13_redesign_v6 import lodestone_export
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from structure_size_baseline import require

OUT = ROOT / 'deliveries/I18_崩坏能燃料棒封装阵列_蓝脊热室与并列封装线_V1_HBV_20261022'
LOG = ROOT / 'logs/i18-hbv-fuel-rod-encapsulation-v1'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
NAME = 'i18-hbv-shielded-fuel-rod-encapsulation-v1'
ARCHIVE = 'I18_V1_HBV蓝脊热室与并列封装线_结构与预览.zip'
HBV = 'hk3gtl:voltage_machine_casing_hbv'
PORT = 'hk3gtl:industrial_port_casing'
CORE = 'minecraft:diamond_block'
WHITE = 'gtceu:clean_machine_casing'
STEEL = 'gtceu:steel_machine_casing'
VESSEL = 'gtceu:stainless_steel_turbine_casing'
GLASS = 'gtceu:laminated_glass'
PIPE = 'gtceu:titanium_pipe_casing'
GRATE = 'gtceu:assembly_line_grating'
VENT = 'gtceu:computer_heat_vent'
FILTER = 'gtceu:filter_casing'
PANEL = 'gtceu:advanced_computer_casing'
GEAR = 'gtceu:titanium_gearbox'
ROLES = {
    HBV: 'HBV蓝色主机壳：热室外墙、折面屋脊、承重门架及封闭转运塔',
    WHITE: '统一设备底板、热室白色腰线、主控白框与洁净操作间',
    STEEL: '设备隔振台与轨道基础', VESSEL: '包壳腔壁、封装设备与封闭转运筒',
    GLASS: '封闭观察窗、采光齿面与隔离视窗', PIPE: '惰性介质和抽气全方块管廊',
    GRATE: '检修平台与两列物流轨道', VENT: '排热百叶与检漏设备',
    FILTER: '抽气过滤柜', PANEL: '仪表柜与检验工位', GEAR: '夹持和转运机构',
    PORT: '惰性工业接口位置标记，不具备真实仓室能力', CORE: '主控坐标识别标记，不冒充已注册控制器',
}


def roof_height(x: int, z: int) -> int:
    """缓拱横截面叠加重复锯齿采光带，逐格补齐屋面避免斜接漏缝。"""
    return 23 + max(0, 4 - abs(x - 22) // 3) + ((z - 18) % 9) // 4


def room(a: Build, lo, hi, primary=HBV) -> None:
    a.box(lo, hi, primary, True)
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    for y in (y0 + 1, y1 - 2):
        a.box((x0, y, z0), (x1, y, z0), WHITE)
        a.box((x0, y, z1), (x1, y, z1), WHITE)
        a.box((x0, y, z0), (x0, y, z1), WHITE)
        a.box((x1, y, z0), (x1, y, z1), WHITE)
    for z in range(z0 + 2, z1 - 1, 4):
        for x in (x0, x1):
            a.box((x, y0 + 3, z), (x, min(y1 - 3, y0 + 6), z + 1), GLASS)


def build() -> dict:
    brief = {'id': 'I18', 'title': '崩坏能燃料棒封装阵列', 'minimum_wdh': [29, 49, 27],
             'form': '蓝色折脊屏蔽热室、双列封装工位与封闭立式转运库',
             'flow': '包壳与燃料入厂 → 计量装填 → 惰性气氛封口 → 检漏检测 → 转运缓冲；拒收件独立分流'}
    a = Build(brief)
    a.w, a.h, a.d = 45, 33, 65
    a.box((0, 0, 0), (44, 0, 64), WHITE)
    # 底座上的工艺支承有实物用途，外围留出连续检修通道。
    a.box((7, 1, 17), (37, 1, 57), STEEL)
    a.box((3, 1, 6), (41, 1, 15), STEEL)
    a.box((15, 1, 55), (29, 1, 62), STEEL)
    for x in (6, 38):
        a.box((x, 1, 17), (x, 1, 58), GRATE)
    a.box((6, 1, 58), (38, 1, 58), GRATE)

    # 屏蔽厂房：主体完整闭合，观察窗只通向封装设备，不是外露能量堆芯。
    for z in range(18, 57):
        for x in range(8, 37):
            top = roof_height(x, z)
            neighbors = [roof_height(max(8, x - 1), z), roof_height(min(36, x + 1), z),
                         roof_height(x, max(18, z - 1)), roof_height(x, min(56, z + 1))]
            material = WHITE if (z - 18) % 9 == 0 else HBV
            if 19 <= x <= 25 and (z - 18) % 9 in (6, 7):
                material = GLASS
            a.box((x, min([top, *neighbors]), z), (x, top, z), material)
            if (z - 18) % 9 == 8:
                a.box((x, min([top, *neighbors]), z), (x, top - 1, z), GLASS)
            if z in (18, 56):
                for y in range(2, top):
                    wall = HBV
                    if y in (3, 16, 20):
                        wall = WHITE
                    if 5 <= y <= 13 and x % 6 not in (2, 3):
                        wall = GLASS
                    a.set(x, y, z, wall)
        for x in (8, 36):
            for y in range(2, roof_height(x, z)):
                wall = WHITE if y in (3, 15, 20) else HBV
                if 6 <= y <= 12 and (z - 18) % 9 not in (0, 1):
                    wall = GLASS
                a.set(x, y, z, wall)
        # 周期门架是屋脊支承，落在设备基础上，不用非完整细框架。
        if (z - 18) % 9 == 0:
            for x in (10, 34):
                a.box((x, 2, z), (x, roof_height(x, z) - 1, z), HBV)
            a.box((10, 21, z), (34, 22, z), HBV)
            a.box((11, 20, z), (33, 20, z), WHITE)

    # 双列直线封装热室。两条线之间保留真实四格高净空；上层封闭转运梁跨接工位。
    for cx in (15, 29):
        a.box((cx - 2, 2, 21), (cx + 2, 3, 52), STEEL)
        for x in (cx - 2, cx + 2):
            a.box((x, 4, 21), (x, 4, 52), GRATE)
        for index, z in enumerate((23, 31, 39, 47)):
            a.box((cx - 3, 4, z - 2), (cx + 3, 11, z + 2), VESSEL, True)
            a.box((cx - 2, 6, z - 2), (cx + 2, 9, z - 2), GLASS)
            for x in (cx - 3, cx + 3):
                a.box((x, 5, z - 2), (x, 12, z + 2), HBV, True)
            a.box((cx - 3, 12, z - 2), (cx + 3, 12, z + 2), HBV)
            a.box((cx, 13, z), (cx, 17, z), PIPE)
            a.box((cx - 1, 10, z), (cx + 1, 11, z), (GEAR, VESSEL, VENT, PANEL)[index])
            a.box((cx - 1, 5, z), (cx + 1, 7, z), (VESSEL, GEAR, PANEL, VENT)[index])
        a.box((cx, 17, 21), (cx, 17, 53), PIPE)
    for z in (23, 31, 39, 47, 53):
        a.box((15, 18, z), (29, 18, z), HBV)
        a.box((16, 19, z), (28, 19, z), GRATE)

    # 前部双闸室：进入热室的路径由封闭通道连接，原料和成品分流。
    room(a, (5, 2, 7), (16, 10, 14))
    room(a, (28, 2, 7), (39, 10, 14))
    for x0, x1 in ((11, 16), (28, 33)):
        room(a, (x0, 2, 14), (x1, 9, 20))
    for x in (8, 12, 31, 35):
        a.box((x, 3, 9), (x + 1, 6, 12), PANEL)
        a.box((x, 7, 10), (x + 1, 8, 11), VESSEL)

    # 西侧抽气过滤长廊与东侧检漏实验翼，分别连接对应制造工位。
    room(a, (2, 2, 20), (6, 10, 54))
    for z in (25, 34, 43, 50):
        a.box((2, 11, z), (5, 12, z + 2), FILTER)
        a.box((3, 13, z), (4, 14, z + 2), VENT)
        a.box((4, 8, z), (15, 8, z), PIPE)
    room(a, (38, 2, 23), (42, 13, 49), WHITE)
    for z in (27, 35, 43):
        a.box((38, 14, z), (42, 14, z + 2), HBV)
        a.box((39, 15, z), (41, 15, z + 2), VENT)
        a.box((29, 9, z), (40, 9, z), PIPE)
        a.box((39, 3, z), (41, 7, z + 1), PANEL)

    # 立式密闭转运库兼作全厂高点：侧面窄窗可看见独立筒架，顶部为实壳。
    room(a, (16, 2, 55), (28, 30, 61))
    for y in (6, 13, 20, 27):
        a.box((16, y, 55), (28, y, 55), WHITE)
        a.box((16, y, 61), (28, y, 61), WHITE)
    for x in (18, 22, 26):
        a.box((x, 3, 57), (x, 27, 59), VESSEL)
        a.box((x, 5, 55), (x, 25, 55), GLASS)
        a.box((x, 31, 57), (x, 32, 59), VENT)
    a.box((17, 30, 56), (27, 30, 60), HBV)
    a.box((17, 28, 57), (27, 29, 59), GEAR)
    a.box((16, 2, 62), (28, 3, 62), HBV)
    for x in (12, 32):
        a.box((x, 2, 59), (x, 10, 59), HBV)
        a.box((x, 10, 53), (x, 10, 59), PIPE)
    a.box((12, 10, 59), (32, 10, 59), PIPE)

    # 正前中轴白框：18格内区＝主控标记1＋工业接口17，全部朝北可直接访问。
    controller = [22, 3, 3]
    ports = []
    purposes = ['包壳输入', '燃料输入', '密封件输入', '惰性介质输入', '冷却剂输入', '供能',
                '维护预留', '抽气', '检测件输入', '燃料棒输出', '废件输出', '回收件输出',
                '热冷却液输出', '废气输出', '检漏结果预留', '备用物流', '备用物流']
    for x in range(17, 28):
        for y in range(1, 6):
            a.set(x, y, 4, HBV)
            if x in (17, 27) or y in (1, 5):
                a.set(x, y, 3, WHITE)
    for y in (2, 3):
        for x in range(18, 27):
            if [x, y, 3] == controller:
                a.set(x, y, 3, CORE)
            else:
                purpose = purposes[len(ports)]
                a.set(x, y, 3, PORT)
                ports.append({'id': 'P%02d' % (len(ports) + 1), 'pos': [x, y, 3],
                              'face': 'north', 'purpose': purpose + '候选'})
    a.box((18, 4, 3), (26, 4, 3), WHITE)
    # 主控背后的仪表脊有真实支座，与前闸室侧梁连接。
    a.box((20, 2, 5), (24, 7, 7), PANEL, True)
    a.box((16, 6, 7), (28, 6, 7), HBV)

    zones = [
        ('正面主控与接口白框', [17, 1, 3], [27, 7, 7], 'control', '控制、输入输出预留'),
        ('原料计量与包壳闸室', [5, 2, 7], [16, 10, 20], 'hall', '原料接收和装填前缓冲'),
        ('检测与出厂闸室', [28, 2, 7], [39, 10, 20], 'hall', '检测件接收和成品分流'),
        ('蓝脊屏蔽热室', [8, 2, 18], [36, 29, 56], 'hall', '封闭屏蔽与连续屋脊'),
        ('西列封装线', [12, 2, 21], [18, 17, 52], 'bed', '装填、封口、检漏、质检四工位'),
        ('东列封装线', [26, 2, 21], [32, 17, 52], 'bed', '并行制造与拒收件分流'),
        ('抽气过滤长廊', [2, 2, 20], [6, 14, 54], 'cooler', '惰性环境与尾气过滤'),
        ('检漏实验翼', [38, 2, 23], [42, 15, 49], 'lab', '封口完整性与样品检测'),
        ('封闭立式转运库', [16, 2, 55], [28, 32, 62], 'archive', '封装筒架、提升转运和成品缓冲'),
    ]
    result = {'key': 'i18', 'name': NAME, 'title': brief['title'], 'size': [a.w, a.h, a.d],
              'brief': brief, 'controller': controller, 'ports': ports,
              'paths': [{'name': '主控前操作通道', 'min': [17, 1, 1], 'max': [27, 4, 2]},
                        {'name': '热室中部检修通道', 'min': [20, 2, 21], 'max': [24, 5, 52]}],
              'zones': [{'name': n, 'min': lo, 'max': hi, 'pos': [(lo[0] + hi[0]) // 2, hi[1], (lo[2] + hi[2]) // 2],
                         'kind': k, 'role': role, 'description': role, 'service_face': '北侧或外围检修环路'} for n, lo, hi, k, role in zones],
              'links': [], 'candidate_version': 'V1 HBV 蓝脊热室与并列封装线', 'target_voltage': 'HBV',
              'minimum_executable_recipe_voltage': None,
              'earliest_build_stage': '规划HBV；独立执行器与首建链未验收',
              'description': 'HBV深蓝机壳构成连续折脊和屏蔽外墙，白色腰线与锯齿采光带贯穿厂房。内部两列封装工位顺序完成装填、封口、检漏和质检；西侧抽气过滤廊、东侧检测翼与后部封闭立式转运库各有独立空间。正前中轴白框内的钻石块明确标出主控，17个工业接口围绕它布置。',
              'role_materials': {s: [ROLES[s]] for s in set(a.b.values())},
              'construction_notes': {
                  'orientation': 'X向东、Y向上、Z向南；主控和全部接口朝北（-Z）。',
                  'origin': [0, 0, 0], 'paste_anchor': [0, 0, 0], 'recommended_world_y': -60,
                  'world_height_range': [-60, -28],
                  'controller_marker': '钻石块[22,3,3]为明确可见的主控定位标记；I18没有正式控制器，不能把标记当可运行机器。',
                  'approval': '外观候选，未批准，未部署。',
                  'stage': '既定规划首次开放HBV；MAX普通/HBV浓缩工单为provisional，I18无绑定物理执行器，故真实最低可执行配方档暂缺。',
                  'materials': '现有游戏方块的静态模型已核对；动态最终配方、生存研究与控制器获取尚未闭合，不宣称可在HBV实际建成。',
              },
              'blocks': [{'pos': list(p), 'state': s} for p, s in sorted(a.b.items())]}
    assert a.b[tuple(controller)] == CORE
    assert len(ports) == 17
    # 主控正前无遮挡、白框清晰；不会被后续屋面或管线覆盖。
    assert all((22, 3, z) not in a.b for z in range(3))
    return result


def stage_evidence():
    """摘录本实例既有有效配方；保留其UNVERIFIED状态，不把历史快照升级成本轮验收。"""
    source = INSTANCE / 'logs/hk3gtl-research-audit/20261019-024300-8501afa8-c8f6-456d-be4c-0c858f6d37e1/recipes.jsonl'
    line_map = {8073: PANEL, 8436: WHITE, 8438: VESSEL, 8484: VENT, 10013: GEAR,
                23844: GLASS, 39877: GRATE, 39899: PIPE, 40745: FILTER, 44919: STEEL}
    rows = {}
    with source.open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            if number not in line_map:
                continue
            record = json.loads(line)
            outputs = record.get('resolved_outputs', {}).get('items', [])
            output_ids = {v['id'] for output in outputs for v in output['alternatives']}
            if 'result' in record:
                output_ids.add(record['result']['id'])
            state = line_map[number]
            assert state in output_ids, (number, state)
            assert not record['empty_ingredients'] and not record['gates']
            rows[state] = {'recipe_id': record['id'], 'snapshot_line': number,
                           'eu_per_tick': record.get('eu_in_per_tick'),
                           'resolved_inputs': record.get('resolved_inputs'),
                           'gates': record['gates'], 'survival_eligibility': record['survival_eligibility']}
    assert len(rows) == 10
    return {'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'snapshot_time': '2026-10-19 02:43（既有记录，非本轮启动）', 'materials': rows,
            'hbv_route': 'MAX三步SPS标准坯→MAX折弯HBV板→8同级板围圈合成机壳；MAX首制免研究，量产RN-NSP仍为provisional。',
            'hbv_sources': ['src/main/java/com/sirin/hk3gtl/common/recipe/main/Hk3MainMaterialProductionLower.java',
                            'src/main/java/com/sirin/hk3gtl/common/recipe/main/Hk3MainMaterialFormRecipes.java',
                            'src/main/java/com/sirin/hk3gtl/common/recipe/main/Hk3MainMaterialAccess.java',
                            'src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3VoltageCasingRecipes.java'],
            'boundary': '配方有效输出与首步输入已记录；祖先链、研究与完整HBV生存获取未实机验收。'}


def write_index(data, audit, basis):
    counts = audit['palette']
    rows = ''.join('<tr><td><code>%s</code></td><td>%s</td><td>%s</td></tr>' %
                   (html.escape(r['state']), f"{counts[r['state']]:,}", html.escape(ROLES[r['state']])) for r in basis)
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>I18 · 崩坏能燃料棒封装阵列 · HBV V1</title><style>
*{box-sizing:border-box}body{margin:0;background:#eef2f7;color:#172c43;font:15px/1.8 'Microsoft YaHei',sans-serif}main{max-width:1240px;margin:auto;padding:24px}header{padding:25px 30px;background:#183b69;color:white;border-radius:8px}h1{margin:0;font-size:28px}h2{font-size:20px;margin-top:28px}.facts{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.facts span{padding:8px 14px;background:white;border:1px solid #c3d0e1;border-radius:5px}.notice{background:#fff2de;padding:13px 18px;border-left:4px solid #b8742c}a{color:#1b5d99}iframe{display:block;width:100%;height:790px;border:1px solid #becddd;border-radius:6px;background:#121b2b}table{border-collapse:collapse;width:100%;background:white}th,td{text-align:left;vertical-align:top;padding:9px;border-bottom:1px solid #d0dce7}th{background:#dde8f3}code{overflow-wrap:anywhere}small{color:#506781}img{max-width:100%}@media(max-width:750px){main{padding:12px}header{padding:18px}h1{font-size:23px}iframe{height:660px}}
</style><main><header><small style="color:#cbdcf4">HK3GTL · I18 · 建筑候选 V1</small><h1>崩坏能燃料棒封装阵列</h1><p>蓝脊热室与并列封装线：连续深蓝折脊、封闭观察窗、双列四工位、侧置检测翼和后部立式转运库。</p></header>
<div class="facts"><span>规划电压：<b>HBV</b></span><span>宽×深×高：<b>45×65×33</b></span><span>尺寸下限：29×49×27</span><span>实体：<b>BLOCKS</b></span><span>HBV主机壳：<b>CASINGS</b></span></div>
<p><a href="三维评审.html">打开完整三维评审</a> · <a href="三维评审.html?view=controller">定位控制器</a> · <a href="NAME.nbt">NBT</a> · <a href="NAME.schem">Schematic</a> · <a href="ARCHIVE">下载完整ZIP</a></p>
<p><b>主控位在正面白框中央：[22, 3, 3]，朝北（-Z）。</b>预览和结构内均放置一个钻石块作可见标记；周围17格使用本模组工业接口方块。</p>
<iframe src="三维评审.html" title="I18三维结构评审"></iframe>
<h2>由工序决定空间</h2><p>前场两间闸室分开收料与检测件转运；中央热室容纳两列独立封装工位，保留中轴检修通道。厂房西侧连接抽气过滤廊，东侧接检漏实验翼，后部高位筒架库负责封装后的竖直转运。锯齿采光面与长向屋脊使它从外形就能读作连续制造设施。</p>
<h2>电压与实际实现</h2><div class="notice">既定计划为HBV首开，主机壳采用现有 <code>hk3gtl:voltage_machine_casing_hbv</code>。I18的普通MAX/浓缩HBV工单仍是provisional计划，虽然注册到工艺配方类型，但没有绑定独立物理控制器/Pattern，不能据此宣称存在最低可执行配方档。当前GT装配机燃料棒路线单独存在；本次不改变配方归属或解锁。建筑外观、材料生存可达、独立执行器与游戏成型分别验收。</div>
<h2>实际方块</h2><p>模型来自当前增强版实例与项目正式资源，全部解析为完整立方体；没有新增机壳或贴图。NAMESPACE。工业接口与钻石主控标记单列，不算普通建材。</p><table><thead><tr><th>方块ID</th><th>数量</th><th>用途</th></tr></thead><tbody>ROWS</tbody></table>
<p><a href="材料阶段依据.json">材料阶段依据</a>摘录增强版2.9既有运行快照的10条有效产出，保留其生存资格UNVERIFIED状态。HBV机壳的源码路线为MAX首制标准坯→板材→八板机壳，量产所需RN-NSP研究尚未验收。</p>
<h2>文件与检查</h2><p><a href="等轴预览.png">静态外观图</a> · <a href="内部剖切.png">双列封装线剖切图</a> · <a href="verification.json">导出校验</a> · <a href="设计与检查.json">完整坐标、材料依据与状态</a>。剖切图仅为隐藏围护后的建筑审视，不修改结构。结构以[0,0,0]为原点及粘贴锚点，建议底部Y=-60，最高Y=-28；Schematic Offset为零，不是世界绝对坐标。</p><p class="notice">本轮浏览器自动检查被本地file协议安全策略拦截，旋转、剖切按钮与控制器定位尚未实际交互验收。静态材质图、脚本编译和逐格结构检查已完成。</p><small>变更记录 #1 · TIME。新增I18独立建筑候选与交付；未改正式资源、配方及实例。生存材料获取、研究、Pattern与游戏运行待验收。</small></main></html>'''
    ordinary = {k: v for k, v in audit['namespace_counts'].items()}
    page = page.replace('BLOCKS', f"{len(data['blocks']):,}").replace('CASINGS', f"{counts[HBV]:,}")
    page = page.replace('NAMESPACE', '普通建材用量：' + '；'.join(f'{k} {v:,}（{audit["namespace_percent"][k]}%）' for k, v in ordinary.items()))
    page = page.replace('ROWS', rows).replace('ARCHIVE', ARCHIVE).replace('NAME', NAME).replace('TIME', audit['time'])
    (OUT / 'index.html').write_text(page, encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    data = build()
    evidence = stage_evidence()
    (OUT / '材料阶段依据.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    resources = Resources(instance=INSTANCE, project_resources=ROOT / 'src/main/resources')
    basis = []
    try:
        for state in sorted({b['state'] for b in data['blocks']}):
            material = resources.material(state)
            assert material['complete_cube'], state
            basis.append({'state': state, 'model': material['model'], 'complete_cube': True,
                          'role': ROLES[state], 'resource_source': resources.sources.get('assets/' + state.replace(':', '/blockstates/') + '.json'),
                          'effective_recipe_evidence': evidence['materials'].get(state),
                          'stage_verification': 'HBV机壳有源码板材配方；GT材料路线需结合最终脚本和运行时再次核验。指定标记不作建材阶段承诺。'})
    finally:
        resources.close()
    preview.TEST_INSTANCE = INSTANCE
    preview.package(data, OUT, 'i07', ['主体采用现有HBV机壳', '17个工业接口和钻石主控标记分开计数',
                                      '封闭热室、双列封装、侧置检测与立式转运分区', '实际模型全部完整立方体'])
    encoded = json.loads((OUT / 'data.js').read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    cut_data = {**data, 'blocks': [b for b in data['blocks'] if b['pos'][1] <= 19
                and 8 <= b['pos'][0] <= 36 and 18 <= b['pos'][2] <= 56
                and not (b['pos'][1] > 3 and (b['pos'][0] in (8, 36) or b['pos'][2] in (18, 56)))]}
    cut_dir = LOG / 'internal-render'
    cut_dir.mkdir(exist_ok=True)
    preview.render(cut_data, payload['materials'], cut_dir)
    shutil.copy2(cut_dir / '等轴预览.png', OUT / '内部剖切.png')
    nbt_sha = lodestone_export(data, OUT, LOG)
    record = json.loads((OUT / '设计与检查.json').read_text(encoding='utf-8'))
    audit = record['audit']
    markers = {CORE, PORT}
    ns = collections.Counter(b['state'].split(':')[0] for b in data['blocks'] if b['state'] not in markers)
    audit.update({'candidate_version': data['candidate_version'], 'target_voltage': 'HBV', 'approval': '待用户外观审批；未批准、未部署',
                  'minimum_executable_recipe_voltage': None, 'material_basis': basis, 'namespace_counts': dict(ns),
                  'namespace_percent': {k: round(100 * v / sum(ns.values()), 2) for k, v in ns.items()},
                  'design_markers': {CORE: 1, PORT: 17}, 'controller_facing': 'north',
                  'browser_review': {'verified': False, 'blocked_action': 'Computer Use打开本地file评审页', 'reason': '浏览器URL安全策略仅允许http/https；未使用替代路径绕过。'},
                  'hashes': {'nbt': nbt_sha, 'schem': hashlib.sha256((OUT / f'{NAME}.schem').read_bytes()).hexdigest()},
                  'not_verified': ['待用户外观审批', '独立I18控制器、Pattern、实际仓室能力及燃料工单执行',
                                   'HBV主材与研究及各建材最终生存获取路径', '游戏成型、运行与实际放置方向',
                                   '浏览器旋转、剖切和定位交互（本地file协议受安全策略限制）'],
                  'rule_read_record': str(LOG / 'rules-read.json')})
    audit['checks'].append('Lodestone NBT逐格状态回读与Sponge同源回读一致')
    (OUT / '设计与检查.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    encoded = json.loads((OUT / 'data.js').read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    payload['audit'] = audit
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')) + ';', encoding='utf-8')
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/package_i18_review.mjs'), str(OUT)], check=True)
    write_index(data, audit, basis)
    manifest = {'id': 'I18', 'title': data['title'], 'candidate_version': data['candidate_version'], 'target_voltage': 'HBV',
                'size_xyz': data['size'], 'size_wdh': [45, 65, 33], 'block_count': len(data['blocks']),
                'controller': data['controller'], 'controller_state': CORE, 'port_count': len(data['ports']),
                'approval': '待用户外观审批；未批准、未部署', 'hashes': audit['hashes'], 'generated_at': audit['time']}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    result = {**manifest, 'size_check': require(data), 'all_models_full_cubes': True,
              'hbv_count': audit['palette'][HBV], 'nbt_roundtrip': True, 'schem_roundtrip': True,
              'controller_visible_clearance': True, 'six_face_connected': True,
              'runtime_verified': False}
    (OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    scripts = OUT / '生成脚本'
    scripts.mkdir(exist_ok=True)
    shutil.copy2(__file__, scripts / Path(__file__).name)
    shutil.copy2(ROOT / 'tools/structure_delivery/package_i18_review.mjs', scripts / 'package_i18_review.mjs')
    shutil.copy2(Path.home() / '.codex/skills/minecraft-builder-skill/node_modules/three/LICENSE', OUT / 'Three许可.txt')
    with zipfile.ZipFile(OUT / ARCHIVE, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path.suffix != '.zip':
                bundle.write(path, path.relative_to(OUT))
    with zipfile.ZipFile(OUT / ARCHIVE) as bundle:
        assert bundle.testzip() is None
        assert all(bundle.read(n) == (OUT / n).read_bytes() for n in bundle.namelist())
    print(json.dumps({'output': str(OUT), **result}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
