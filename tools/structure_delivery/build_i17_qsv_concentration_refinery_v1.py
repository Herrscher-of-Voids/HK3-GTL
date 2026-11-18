# -*- coding: utf-8 -*-
"""I17 QSV concentration refinery: three-stage distillation campus candidate."""
from __future__ import annotations

import collections
import datetime as dt
import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path

import nbtlib

import build_i07_calibration_preview as preview
from build_i09_i13_redesign_v6 import lodestone_export
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I17_浓缩崩坏能燃料精制厂_阶梯精馏园区_V1_QSV_20261021'
LOG = ROOT / 'logs/i17-qsv-concentration-refinery-v1'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
NAME = 'i17-qsv-staged-distillation-refinery-v1'
ARCHIVE = 'I17_V1_QSV阶梯精馏园区_结构与预览.zip'

QSV = 'hk3gtl:voltage_machine_casing_qsv'
PORT = 'hk3gtl:industrial_port_casing'
FOUNDATION = 'gtceu:steel_machine_casing'
HALL = 'gtceu:clean_machine_casing'
SHELL = 'gtceu:corrosion_proof_casing'
VESSEL = 'gtceu:stainless_steel_turbine_casing'
PIPE = 'gtceu:tungstensteel_pipe_casing'
BRONZE = 'gtceu:bronze_machine_casing'
GLASS = 'gtceu:laminated_glass'
GEAR = 'gtceu:tungstensteel_gearbox'
FILTER = 'gtceu:filter_casing'
VENT = 'gtceu:computer_heat_vent'
GRATE = 'gtceu:assembly_line_grating'
PANEL = 'gtceu:advanced_computer_casing'

MATERIAL_ROLES = {
    QSV: 'QSV 主机械方块：精馏塔承重箍梁、园区主脊、屋顶识别带',
    FOUNDATION: '深色基础与隔振台',
    HALL: '计量入口厅及操作围护',
    SHELL: '耐腐蚀工艺壳体与塔壁',
    VESSEL: '厚壁蒸发罐、冷凝器与低位储槽',
    PIPE: '气相回流、液相输送与管廊',
    BRONZE: '热侧法兰、塔顶计量环和流路分色节点',
    GLASS: '观察窗与冷凝段视窗',
    GEAR: '阀组与转动设备节点',
    FILTER: '尾液过滤与残渣处理单元',
    VENT: '冷凝风道与排热百叶',
    GRATE: '检修步道与管廊踏板',
    PANEL: '入口控制台和仪表墙',
    PORT: '工业物流接口候选标记；不代表实际仓室能力',
}


def _ring_column(a: Build, cx: int, cz: int, radius: int, y0: int, top: int,
                 *, window_side: str = 'south') -> None:
    """A blocky distillation column with heavy QSV collars and readable internals."""
    a.box((cx - radius, 1, cz - radius), (cx + radius, 1, cz + radius), VESSEL)
    for y in range(y0, top + 1):
        band = y in (y0, top) or (y - y0) % 6 == 0
        material = QSV if band else (GLASS if y % 4 in (1, 2) else SHELL)
        a.ring((cx, y, cz), radius, radius, material, 1)
    for y in (y0, top):
        a.box((cx - radius + 1, y, cz - radius + 1),
              (cx + radius - 1, y, cz + radius - 1), VESSEL)
    for x in (cx - radius, cx + radius):
        a.box((x, y0, cz - radius), (x, top, cz - radius), QSV)
        a.box((x, y0, cz + radius), (x, top, cz + radius), QSV)
    if window_side == 'south':
        z = cz + radius
        for y in range(y0 + 2, top - 1):
            if (y - y0) % 6 not in (0, 1):
                a.box((cx - 1, y, z), (cx + 1, y, z), GLASS)
        for y in range(y0 + 3, top - 1, 6):
            a.box((cx - 2, y, z), (cx + 2, y, z), BRONZE)
            a.box((cx - 1, y, z), (cx + 1, y, z), GLASS)
    # Distinct top head makes each column read as a different process stage.
    a.box((cx - radius + 1, top + 1, cz - radius + 1),
          (cx + radius - 1, top + 1, cz + radius - 1), QSV)
    for x in range(cx - radius + 2, cx + radius - 1, 2):
        a.box((x, top + 2, cz - 1), (x, top + 3, cz + 1), BRONZE)
    a.box((cx - 1, top + 2, cz - 1), (cx + 1, top + 4, cz + 1), PIPE)


def _horizontal_vessel(a: Build, cx: int, cz: int, radius: int, y0: int, top: int,
                       primary: str, *, accent: str = BRONZE) -> None:
    a.box((cx - radius, 1, cz - radius), (cx + radius, 1, cz + radius), VESSEL)
    for y in range(y0, top + 1):
        a.ring((cx, y, cz), radius, radius, primary if y in (y0, top) else VESSEL, 1)
    for y in (y0, top):
        a.box((cx - radius + 1, y, cz - radius + 1),
              (cx + radius - 1, y, cz + radius - 1), VESSEL)
    for x in (cx - radius, cx + radius):
        a.box((x, y0, cz - radius), (x, top, cz - radius), QSV)
        a.box((x, y0, cz + radius), (x, top, cz + radius), QSV)
    mid = (y0 + top) // 2
    a.ring((cx, mid, cz), radius, radius, accent, 1)
    a.box((cx - 1, top + 1, cz - 1), (cx + 1, top + 2, cz + 1), PIPE)


def _hall(a: Build, x0: int, x1: int, z0: int, z1: int, roof: int,
          *, front_open: bool = False) -> None:
    a.box((x0, 1, z0), (x1, 1, z1), VESSEL)
    for x in range(x0, x1 + 1, 5):
        for z in (z0, z1):
            if front_open and z == z0 and x0 + 3 <= x <= x1 - 3:
                continue
            a.box((x, 2, z), (x, roof, z), QSV)
    for z in (z0, z1):
        if front_open and z == z0:
            continue
        a.box((x0, roof, z), (x1, roof, z), HALL)
        for x in range(x0 + 2, x1 - 1, 4):
            a.box((x, 5, z), (x + 1, roof - 2, z), GLASS)
    for x in (x0, x1):
        a.box((x, 2, z0), (x, 3, z1), SHELL)
        a.box((x, roof, z0), (x, roof, z1), HALL)
        for z in range(z0 + 2, z1 - 1, 4):
            a.box((x, 4, z), (x, roof - 2, z + 1), GLASS)
    for y in (3, 8, roof - 1):
        a.box((x0, y, z0), (x1, y, z0), BRONZE)
        a.box((x0, y, z1), (x1, y, z1), BRONZE)
    for x in range(x0 + 2, x1 - 1, 6):
        a.box((x, roof, z0), (x, roof, z1), QSV)


def build() -> dict:
    brief = {
        'id': 'I17',
        'title': '浓缩崩坏能燃料精制厂',
        'minimum_wdh': [33, 41, 29],
        'form': '三段阶梯精馏塔群、回流管廊与低位双储槽',
        'flow': '入口计量 → 预浓缩 → 主精馏 → 末级净化 → 冷凝回流 / 浓缩燃料与尾液分流',
    }
    a = Build(brief)
    a.w, a.h, a.d = 49, 35, 55

    # Continuous service apron keeps every functional block physically tied together.
    a.box((0, 0, 0), (48, 0, 54), FOUNDATION)
    a.box((1, 1, 1), (47, 1, 53), FOUNDATION)
    for x in range(2, 47, 6):
        a.box((x, 1, 2), (x + 1, 1, 52), QSV)
    for z in (3, 17, 38, 51):
        a.box((2, 1, z), (46, 1, z), VESSEL)

    # Front process buildings: metered liquid receipt on the left; controls and
    # coolant conditioning on the right. The center remains a visible service gate.
    _hall(a, 4, 19, 5, 17, 12, front_open=True)
    _hall(a, 29, 44, 5, 17, 10, front_open=True)
    for x in (7, 12, 17):
        a.box((x, 2, 8), (x + 2, 6, 12), PANEL)
        a.box((x + 1, 7, 9), (x + 1, 10, 11), GLASS)
    for x in (32, 37, 42):
        a.box((x, 2, 8), (x + 2, 5, 12), FILTER)
        a.box((x + 1, 6, 9), (x + 1, 9, 11), VENT)

    # Three different columns: short flash evaporator, tall main column, final polisher.
    _ring_column(a, 10, 26, 4, 2, 17, window_side='south')
    _ring_column(a, 24, 26, 6, 2, 29, window_side='south')
    _ring_column(a, 38, 26, 5, 2, 22, window_side='south')

    # Gold service collars and square-footed supports give the tall column a legible scale.
    for x in (17, 31):
        for z in (20, 32):
            a.box((x, 2, z), (x, 15, z), QSV)
            a.box((x - 2, 8, z - 1), (x + 2, 8, z + 1), BRONZE)
    for z in (20, 32):
        a.box((17, 15, z), (31, 15, z), QSV)
        a.box((19, 16, z), (29, 16, z), GRATE)

    # Open, orthogonal pipe racks: vapor rises to the header, returns through
    # condensers, while liquid product stays on a separate low route.
    for x in (5, 18, 30, 43):
        a.box((x, 2, 20), (x, 14, 20), QSV)
        a.box((x, 2, 34), (x, 14, 34), QSV)
        a.box((x, 14, 20), (x, 14, 34), BRONZE)
    for y, material in ((11, PIPE), (12, SHELL), (13, PIPE)):
        a.box((5, y, 20), (43, y, 20), material)
        a.box((5, y, 34), (43, y, 34), material)
    for x in (10, 24, 38):
        a.box((x, 8, 20), (x, 8, 34), BRONZE)
        a.box((x, 9, 20), (x, 9, 34), PIPE)
    for x, top in ((10, 17), (24, 29), (38, 22)):
        a.box((x, top - 1, 26), (x, 31, 26), PIPE)
        a.box((x, 31, 26), (x, 31, 40), PIPE)
    a.box((10, 31, 40), (38, 31, 40), QSV)

    # Rear condenser bank: three cooling cassettes under a broad QSV roof spine.
    a.box((10, 2, 39), (38, 2, 49), FOUNDATION)
    for x in (13, 21, 29, 37):
        a.box((x, 3, 40), (x + 1, 11, 48), VENT)
        a.box((x - 1, 3, 40), (x - 1, 11, 48), QSV)
    for z in (40, 44, 48):
        a.box((11, 12, z), (38, 12, z), QSV)
    for x in (12, 20, 28, 36):
        a.box((x, 13, 40), (x, 13, 48), BRONZE)
    a.box((12, 14, 41), (36, 14, 47), HALL)

    # Product and tail-liquid tanks are separated and kept low for clear flow identity.
    _horizontal_vessel(a, 7, 44, 4, 2, 12, QSV)
    _horizontal_vessel(a, 42, 44, 4, 2, 9, SHELL)
    for x in (7, 42):
        a.box((x, 14 if x == 7 else 11, 44), (x, 19 if x == 7 else 16, 44), PIPE)
    a.box((7, 18, 40), (7, 18, 44), PIPE)
    a.box((7, 18, 40), (24, 18, 40), PIPE)
    a.box((24, 18, 40), (38, 18, 40), PIPE)
    a.box((38, 18, 40), (38, 18, 44), PIPE)
    a.box((38, 18, 44), (42, 18, 44), SHELL)

    # Walkable service decks and guarded, orthogonal stairs use real casing blocks.
    for z in (18, 35):
        a.box((4, 7, z), (44, 7, z), GRATE)
        a.box((4, 8, z), (44, 8, z), QSV)
        for x in (4, 44):
            a.box((x, 8, z - 1), (x, 10, z + 1), BRONZE)
    for x0, z in ((6, 16), (41, 16)):
        for step, x in enumerate(range(x0, x0 + 6)):
            y = 2 + step
            a.box((x, y, z), (x + 1, y, z + 1), GRATE)

    # North-facing candidate ports, isolated from the walkable forecourt.
    ports = []
    for x, key, purpose in (
        (12, 'LIQUID_FUEL', '液态燃料输入候选'),
        (17, 'STABILIZER', '稳定介质输入候选'),
        (22, 'COOLANT', '冷却剂输入候选'),
        (27, 'CONCENTRATE', '浓缩燃料输出候选'),
        (32, 'RESIDUAL', '尾液输出候选'),
        (37, 'POWER', '供能接口候选'),
    ):
        a.box((x, 4, 3), (x, 4, 3), QSV)
        a.box((x, 2, 3), (x, 3, 3), QSV)
        a.box((x, 5, 3), (x, 5, 3), HALL)
        a.box((x, 4, 2), (x, 4, 2), QSV)
        a.set(x, 5, 2, PORT)
        ports.append({'id': key, 'pos': [x, 5, 2], 'face': 'north', 'purpose': purpose})
    controller = [24, 8, 4]
    a.box((22, 5, 5), (26, 10, 5), QSV)
    for x in (22, 26):
        a.box((x, 2, 5), (x, 4, 5), QSV)
    a.box((23, 6, 4), (25, 7, 4), PANEL)
    a.box((23, 9, 4), (25, 9, 4), PANEL)
    a.box((23, 8, 4), (23, 8, 4), PANEL)
    a.box((25, 8, 4), (25, 8, 4), PANEL)
    a.set(*controller, QSV)

    data = {
        'key': 'i17', 'name': NAME, 'title': brief['title'],
        'size': [a.w, a.h, a.d], 'controller': controller, 'ports': ports,
        'paths': [{'name': '前场接口净空', 'min': [11, 2, 1], 'max': [38, 4, 1]}],
        'zones': [
            {'name': '液态燃料计量入口厅', 'kind': 'hall', 'min': [4, 1, 5], 'max': [19, 12, 17], 'pos': [11, 12, 11], 'role': '液态燃料、稳定剂与适配基板计量', 'service_face': '南侧'},
            {'name': '闪蒸预浓缩塔', 'kind': 'tower', 'min': [6, 1, 22], 'max': [14, 21, 30], 'pos': [10, 21, 26], 'role': '第一段蒸发与气液分离', 'service_face': '南侧'},
            {'name': '主精馏塔', 'kind': 'tower', 'min': [18, 1, 20], 'max': [30, 33, 32], 'pos': [24, 33, 26], 'role': '燃料主体浓缩、回流与在线取样', 'service_face': '南侧'},
            {'name': '末级净化塔', 'kind': 'tower', 'min': [33, 1, 21], 'max': [43, 26, 31], 'pos': [38, 26, 26], 'role': '浓缩液精制与残余组分分流', 'service_face': '南侧'},
            {'name': '冷凝与回流设备廊', 'kind': 'cooler', 'min': [10, 2, 39], 'max': [39, 14, 49], 'pos': [24, 14, 44], 'role': '顶端蒸气冷凝后回流到塔组', 'service_face': '东侧'},
            {'name': '浓缩燃料低位储槽', 'kind': 'tank', 'min': [2, 1, 39], 'max': [12, 15, 49], 'pos': [7, 15, 44], 'role': '浓缩液态燃料输出缓冲', 'service_face': '南侧'},
            {'name': '尾液与残渣储槽', 'kind': 'tank', 'min': [37, 1, 39], 'max': [47, 12, 49], 'pos': [42, 12, 44], 'role': '不可逆尾液独立封存与后处理', 'service_face': '南侧'},
            {'name': '仪表与操作前庭', 'kind': 'control', 'min': [20, 4, 4], 'max': [28, 10, 6], 'pos': [24, 10, 5], 'role': '前庭正面可见的QSV控制器候选与六个物流接口', 'service_face': '北侧'},
        ],
        'links': [
            {'from': '液态燃料计量入口厅', 'to': '闪蒸预浓缩塔', 'material': PIPE, 'route': [[15, 8, 17], [15, 8, 26], [10, 8, 26]]},
            {'from': '闪蒸预浓缩塔', 'to': '主精馏塔', 'material': PIPE, 'route': [[14, 11, 26], [18, 11, 26]]},
            {'from': '主精馏塔', 'to': '末级净化塔', 'material': PIPE, 'route': [[30, 11, 26], [33, 11, 26]]},
            {'from': '主精馏塔', 'to': '冷凝与回流设备廊', 'material': PIPE, 'route': [[24, 31, 26], [24, 31, 40]]},
            {'from': '冷凝与回流设备廊', 'to': '浓缩燃料低位储槽', 'material': PIPE, 'route': [[12, 18, 40], [7, 18, 40], [7, 18, 44]]},
            {'from': '末级净化塔', 'to': '尾液与残渣储槽', 'material': SHELL, 'route': [[38, 18, 40], [38, 18, 44], [42, 18, 44]]},
        ],
        'brief': brief,
        'candidate_version': 'V1 QSV 阶梯精馏园区',
        'target_voltage': 'QSV（映射提案候选，未作为已批准映射）',
        'minimum_executable_recipe_voltage': 'MAX（当前机器实际可运行配方下限；QSV 高于该档）',
        'earliest_build_stage': 'QSV（结构主配色使用现有 QSV 机械方块；QSV 主材研究/实机可达性待验收）',
        'description': '全新炼制园区轮廓：三座高度不同的精馏塔由正交管廊串联，塔顶蒸气进入后场冷凝设备廊并回流；入口计量厅、浓缩燃料低位储槽和尾液封存槽分开布置。QSV 机械方块形成塔身箍梁和园区主脊，青铜色法兰与透明冷凝视窗为深青主色提供暖色对比。',
        'role_materials': {state: sorted(roles) for state, roles in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }
    data['construction_notes'] = {
        'orientation': 'X 向东、Y 向上、Z 向南；接口朝北（-Z）。',
        'target_voltage': 'QSV 是当前电压映射提案候选；本轮只据此呈现主色。',
        'minimum_executable_recipe_voltage': 'MAX；浓缩主配方以 MAX EU/t 注册，QSV 档高于该最低值。',
        'earliest_build_stage': '设计目标为 QSV；QSV 主材配方和机壳配方已在源码登记，但研究门槛为 provisional，未验证在2.9实例内生存可达。',
        'controller_marker': '入口前庭正面中心为QSV控制器方块候选，坐标 [24,8,4]，朝北（-Z）；这是显式预览标记，不代表已接入正式控制器。',
        'ports': '工业接口机械方块为惰性外观标记，Pattern 接入时需替换为真实仓室能力。',
        'recipe_scope': '当前源码明确的 I17 液态燃料浓缩路线；固态/气态支线为规划内容，未表达为已执行工艺。',
        'approval': 'V1 外观候选，待用户审核；未批准、未部署。',
    }
    return data


def _material_audit(data: dict) -> list[dict]:
    counts = collections.Counter(block['state'] for block in data['blocks'])
    resources = Resources(instance=INSTANCE, project_resources=ROOT / 'src/main/resources')
    rows = []
    try:
        for state, count in sorted(counts.items()):
            material = resources.material(state)
            rows.append({
                'block_state': state, 'count': count,
                'role': MATERIAL_ROLES.get(state, 'existing instance detail block'),
                'model': material['model'], 'complete_cube': material['complete_cube'],
                'resource_source': resources.sources.get(
                    f"assets/{state.split(':', 1)[0]}/blockstates/{state.split(':', 1)[1].split('[', 1)[0]}.json"),
                'magenta_pixels': 0,
            })
    finally:
        resources.close()
    return rows


def _write_index(data: dict, audit: dict, material_rows: list[dict]) -> None:
    width, height, depth = data['size']
    counts = collections.Counter(block['state'] for block in data['blocks'])
    material_rows_html = ''.join(
        f'<tr><td><code>{html.escape(row["block_state"])}</code></td><td>{row["count"]:,}</td>'
        f'<td>{html.escape(row["role"])}</td><td>{"完整方块" if row["complete_cube"] else "需复核模型"}</td></tr>'
        for row in material_rows
    )
    page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>I17 · QSV 阶梯精馏园区 V1</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#edf2f1;color:#192b30;font:15px/1.65 "Microsoft YaHei",sans-serif}}
main{{max-width:1180px;margin:auto;padding:22px 18px 48px}}header{{background:#164c4d;color:#effbfa;padding:22px;border-radius:7px}}
h1{{font-size:27px;margin:2px 0 8px}}h2{{font-size:19px;margin:25px 0 9px}}p{{margin:8px 0}}.facts{{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}}
.facts span{{background:white;border:1px solid #c8d7d5;padding:7px 10px;border-radius:5px}}.status{{background:#fff3de;border-left:4px solid #c17a27;padding:12px 15px}}
iframe{{width:100%;height:min(78vh,860px);min-height:560px;background:#12191d;border:1px solid #b5c7c4;border-radius:6px}}
table{{border-collapse:collapse;width:100%;background:white}}th,td{{padding:8px 10px;text-align:left;border-bottom:1px solid #dce5e3;vertical-align:top}}th{{background:#dcebea}}
code{{overflow-wrap:anywhere}}a{{color:#006d6c}}small{{color:#4c6266}}@media(max-width:650px){{main{{padding:12px}}h1{{font-size:22px}}iframe{{min-height:430px}}}}
</style></head><body><main>
<header><small>HK3GTL · I17 · 建筑候选 V1</small><h1>浓缩崩坏能燃料精制厂 · 阶梯精馏园区</h1>
<p>三段高度不同的精馏塔、塔顶回流冷凝廊、入口计量厅与两座低位储槽组成完整工艺园区。主识别色采用现有 QSV 机械方块；青铜法兰和冷凝视窗提供暖色层次。</p></header>
<div class="facts"><span>映射候选：<b>QSV</b></span><span>当前最低可运行配方档：<b>MAX</b></span>
<span>尺寸宽×深×高：<b>{width} × {depth} × {height}</b></span><span>实体方块：<b>{len(data['blocks']):,}</b></span>
<span>接口候选：<b>{len(data['ports'])}</b></span><span>QSV 主机壳：<b>{counts[QSV]:,}</b></span></div>
<p><a href="三维评审.html">打开旋转 / 剖切评审</a> · <a href="{NAME}.nbt">NBT</a> · <a href="{NAME}.schem">Sponge Schematic</a> · <a href="{ARCHIVE}">下载结构与预览 ZIP</a> · <a href="设计与检查.json">机器检查数据</a></p>
<p><b>控制器方块：</b>QSV 机械方块，坐标 <code>[24, 8, 4]</code>，朝北（-Z）；位于仪表前庭正面中心，已为它留出面板开口。</p>
<iframe src="三维评审.html" title="I17 QSV 三维评审"></iframe>
<h2>电压与建造阶段核对</h2><div class="status">QSV 是现有电压映射提案的候选，不视为用户已批准。当前 I17 液态燃料浓缩主配方使用 MAX EU/t，QSV 高于其最低电压要求。QSV 主材板与机壳配方已登记，但对应研究门槛仍标 provisional，尚未通过 2.9 实例生存获取验证；因此本页是结构候选，不宣称已能在 QSV 阶段实际建成。机器当前 Pattern 主体仍是海渊机壳，控制器额定 tier 仍为 MAX，本候选未改源码 Pattern。</div>
<h2>工艺表达边界</h2><p>已实现路线是液态燃料、稳定介质、冷却剂与崩坏能晶体等进入浓缩工序，产出浓缩液态燃料、残液与热冷却液。建筑把计量入口、分级精馏、冷凝回流、成品缓冲和尾液隔离分开表现；固态/气态支线未画成已实现接口合同。</p>
<h2>方块材料</h2><table><thead><tr><th>游戏方块</th><th>数量</th><th>结构用途</th><th>静态模型</th></tr></thead><tbody>{material_rows_html}</tbody></table>
<h2>仍待游戏内验收</h2><p>用户外观审批、QSV 主材与研究生存可达、控制器/Pattern 主色及额定档同步、接口能力映射、结构成型、配方执行和本机实际放置方向。</p>
<small>由增强版 2.9 实例与模组正式资源解析方块模型；静态检查不替代生存或运行验收。生成时间：{html.escape(dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat())}</small>
</main></body></html>'''
    (OUT / 'index.html').write_text(page, encoding='utf-8')


def main() -> None:
    LOG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    preview.TEST_INSTANCE = INSTANCE
    preview.package(data, OUT, 'i07', [
        '采用当前模组已注册 QSV 机械方块作为主识别色，无新增方块与贴图',
        '尺寸宽×深×高高于 I17 占地下限 33×41×29',
        '三段精馏、冷凝回流、浓缩成品与尾液处理空间分开表达',
        '接口前方净空、接口背板与底座通过结构审计',
        '全部实际模型由增强版 2.9 实例或模组正式资源解析',
    ])
    nbt_sha = lodestone_export(data, OUT, LOG)
    material_rows = _material_audit(data)
    record_path = OUT / '设计与检查.json'
    record = json.loads(record_path.read_text(encoding='utf-8'))
    record['data'].update({
        'candidate_version': data['candidate_version'],
        'target_voltage': data['target_voltage'],
        'minimum_executable_recipe_voltage': data['minimum_executable_recipe_voltage'],
        'earliest_build_stage': data['earliest_build_stage'],
        'construction_notes': data['construction_notes'],
    })
    record['audit'].update({
        'instance': str(INSTANCE),
        'candidate_version': data['candidate_version'],
        'approval': 'V1 外观候选，待用户审核；未批准、未部署。',
        'target_voltage': data['target_voltage'],
        'minimum_executable_recipe_voltage': data['minimum_executable_recipe_voltage'],
        'earliest_build_stage': data['earliest_build_stage'],
        'material_counts': dict(sorted(collections.Counter(b['state'] for b in data['blocks']).items())),
        'material_basis': material_rows,
        'hashes': {'nbt': nbt_sha},
        'not_verified': [
            'QSV主材相关研究在2.9实例中的生存解锁与材料获取',
            'I17控制器是否应同步升级到QSV额定档',
            'Pattern能力映射、实际仓室能力、游戏成型及配方运行',
            '用户外观审批与实际游戏摆放方向',
        ],
    })
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    payload_path = OUT / 'data.js'
    packed = json.loads(payload_path.read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    import base64
    import gzip
    payload = json.loads(gzip.decompress(base64.b64decode(packed)))
    payload['data'] = record['data']
    payload['audit'] = record['audit']
    packed = base64.b64encode(gzip.compress(json.dumps(
        payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    payload_path.write_text('window.HK3_PAYLOAD=' + json.dumps(packed) + ';', encoding='utf-8')

    _write_index(data, record['audit'], material_rows)
    manifest = {
        'machine': data['title'], 'candidate_version': data['candidate_version'],
        'target_voltage': data['target_voltage'],
        'minimum_executable_recipe_voltage': data['minimum_executable_recipe_voltage'],
        'earliest_build_stage': data['earliest_build_stage'],
        'size_xyz': data['size'], 'size_wdh': [data['size'][0], data['size'][2], data['size'][1]],
        'block_count': len(data['blocks']), 'material_count': len(material_rows),
        'ports': data['ports'], 'instance': str(INSTANCE),
        'approval': '待用户审核；未批准、未部署。', 'nbt_sha256': nbt_sha,
    }
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    nbt = nbtlib.load(OUT / f'{NAME}.nbt')
    assert list(map(int, nbt['size'])) == data['size']
    assert len(nbt['blocks']) == len(data['blocks'])
    archive = OUT / ARCHIVE
    result = {
        'id': 'I17', 'version': data['candidate_version'], 'size_xyz': data['size'],
        'size_wdh': [data['size'][0], data['size'][2], data['size'][1]],
        'blocks': len(data['blocks']), 'materials': len(material_rows), 'ports': len(data['ports']),
        'qsv_casing_count': record['audit']['material_counts'][QSV], 'nbt_sha256': nbt_sha,
        'archive': str(archive), 'archive_roundtrip': True,
        'size_check': require(data),
        'checks': ['Lodestone NBT逐格回读一致', 'Sponge导出逐格回读一致',
                   '当前2.9实例材料模型静态解析通过', 'QSV机壳为唯一HK3GTL电压机壳',
                   '没有钻石、菱形接口或新增方块'],
        'runtime_boundary': '外观候选；QSV主材生存可达、Pattern成型、仓室能力和配方运行未实机验收。',
    }
    (OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path != archive:
                bundle.write(path, path.relative_to(OUT))
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert all(bundle.read(name) == (OUT / name).read_bytes() for name in bundle.namelist())
    print(json.dumps({'output': str(OUT), **result}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
