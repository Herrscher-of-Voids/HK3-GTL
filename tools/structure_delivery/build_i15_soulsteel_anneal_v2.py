# -*- coding: utf-8 -*-
"""I15「炉序织衡」独立外观候选：纵向热史廊与组织重构舱。"""
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


OUT = ROOT / 'deliveries/I15_魂钢重构退火炉_炉序织衡_V2_20261016'
LOG = ROOT / 'logs/i15-soulsteel-anneal-v2'
ARCHIVE = 'I15_V2_结构与预览.zip'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版 2.7/minecraft'
BASELINE = [29, 49, 27]  # 规划表为宽、深、高手序；Build 使用 X、Y、Z。

PORT = 'hk3gtl:industrial_port_casing'
FRAME = 'gtlcore:lafium_mechanical_casing'
SHELL = 'gtceu:heatproof_machine_casing'
HOT = 'gtceu:high_power_casing'
PANEL = 'gtceu:advanced_computer_casing'
GLASS = 'gtceu:laminated_glass'
CORE_GLASS = 'gtlcore:rhenium_reinforced_energy_glass'
COIL = 'kubejs:titansteel_coil_block[active=false]'
DUCT = 'gtceu:ptfe_pipe_casing'
VENT = 'gtceu:computer_heat_vent'
COLD = 'gtlcore:cold_ice_casing'
GUIDE = 'gtceu:tungstensteel_gearbox'
MARKERS = {'minecraft:diamond_block', PORT}

MATERIAL_ROLES = {
    FRAME: '承重梁、端框与落地支柱',
    SHELL: '进料气锁和前后炉节的保温外壁',
    HOT: '组织重构热区、炉脊与热回收塔主骨架',
    PANEL: '前端接口背板与控制设备护墙',
    GLASS: '四个热处理区的侧向观察窗',
    CORE_GLASS: '中央组织重构舱的观察层',
    COIL: '分区热带与中央组织重构舱的加热线圈意象',
    DUCT: '低位保护气体及热交换连接总管意象',
    VENT: '冷却段与热回收塔的换热鳍面',
    COLD: '均匀缓冷与末端淬冷段的隔热壳',
    GUIDE: '贯穿五段工序的地面导料脊',
}


def _open_tunnel(a, z0, z1):
    for z in (z0, z1):
        for x in range(24, 29):
            for y in range(11, 16):
                a.b.pop((x, y, z), None)


def _thermal_cell(a, name, kind, z0, z1, roof_y, shell, role, work):
    x0, x1, y0 = 13, 39, 5
    # 低位长炉采用侧墙、檐梁和离散横向拱肋，区段之间保留可读的空气缝。
    side_top = max(12, roof_y - 3)
    a.box((x0, y0, z0), (x0, side_top, z1), shell)
    a.box((x1, y0, z0), (x1, side_top, z1), shell)
    a.box((x0 + 1, y0, z0), (x1 - 1, y0, z1), shell)
    a.box((x0, y0, z0), (x1, y0, z0), FRAME)
    a.box((x0, y0, z1), (x1, y0, z1), FRAME)
    window_top = min(14, side_top - 1)
    if window_top >= 9:
        a.box((x0, 9, z0 + 1), (x0, window_top, z1 - 1), GLASS)
        a.box((x1, 9, z0 + 1), (x1, window_top, z1 - 1), GLASS)

    # 每三格一道拱肋；轮廓在两侧收低，中部抬高，但不再封成整块屋顶。
    rib_zs = sorted(set(list(range(z0, z1 + 1, 4)) + [z1]))
    for z in rib_zs:
        previous_y = None
        for x in range(x0, x1 + 1):
            edge = min(x - x0, x1 - x)
            drop = 3 if edge == 0 else 2 if edge <= 2 else 1 if edge <= 5 else 0
            y = roof_y - drop
            a.set(x, y, z, FRAME)
            if previous_y is not None and previous_y != y:
                a.box((x, min(previous_y, y), z), (x, max(previous_y, y), z), FRAME)
            previous_y = y
        a.set((x0 + x1) // 2, roof_y, z, COIL if kind != 'equalize' else VENT)
    a.box((x0, roof_y - 3, z0), (x0, roof_y - 3, z1), FRAME)
    a.box((x1, roof_y - 3, z0), (x1, roof_y - 3, z1), FRAME)
    a.box((x0 + 1, 3, z0 + 1), (x1 - 1, 4, z1 - 1), HOT if kind == 'reconstruction' else FRAME)

    cx = (x0 + x1) // 2
    if kind in ('preheat', 'strain_relief', 'reconstruction', 'equalize'):
        band_y = min(15, roof_y - 4)
        a.box((x0 + 3, band_y, z0 + 2), (x0 + 3, band_y + 1, z1 - 2), COIL)
        a.box((x1 - 3, band_y, z0 + 2), (x1 - 3, band_y + 1, z1 - 2), COIL)
        a.box((x0, band_y, z0 + 2), (x0 + 3, band_y, z1 - 2), HOT)
        a.box((x1 - 3, band_y, z0 + 2), (x1, band_y, z1 - 2), HOT)
    a.box((cx - 2, 6, z0 + 1), (cx + 2, 7, z1 - 1), GUIDE)
    # 密闭内炉位于开放检修拱架下方；中间五格为连续坯料通道。
    a.box((22, 8, z0), (30, 8, z1), shell)
    a.box((22, 9, z0), (22, 15, z1), shell)
    a.box((30, 9, z0), (30, 15, z1), shell)
    a.box((23, 15, z0), (29, 15, z1), shell)
    a.box((22, 11, z0 + 1), (22, 13, z1 - 1), GLASS)
    a.box((30, 11, z0 + 1), (30, 13, z1 - 1), GLASS)
    _open_tunnel(a, z0, z1)
    work.append({'name': name, 'kind': kind, 'min': [x0, y0, z0],
                 'max': [x1, roof_y, z1], 'pos': [cx, roof_y, (z0 + z1) // 2],
                 'role': role, 'service_face': '东西两侧观察与检修廊'})


def build():
    brief = {
        'id': 'I15', 'title': '魂钢重构退火炉',
        'minimum_wdh': BASELINE,
        'form': '纵向五区连续退火厂与中央组织重构舱',
        'flow': '坯料气锁、预热、消应力、组织重构、均质缓冷、淬冷检测与出料',
    }
    a = Build(brief)
    a.w, a.h, a.d = 53, 39, 61
    a.cx, a.cz = 26, 30

    # A narrow perimeter and three equipment aprons give each area its own footing.
    a.box((0, 0, 0), (52, 0, 1), FRAME)
    a.box((0, 0, 59), (52, 0, 60), FRAME)
    a.box((0, 0, 1), (1, 0, 59), FRAME)
    a.box((51, 0, 1), (52, 0, 59), FRAME)
    a.box((4, 0, 2), (9, 0, 58), SHELL)
    a.box((43, 0, 2), (46, 0, 58), SHELL)
    for z0, z1, _ in ((4, 10, SHELL), (11, 18, SHELL), (20, 28, HOT),
                      (30, 40, HOT), (42, 49, COLD), (51, 57, COLD)):
        a.box((12, 0, z0), (40, 0, z1), _)
    a.box((23, 0, 2), (29, 0, 58), HOT)
    a.box((47, 0, 43), (52, 0, 58), FRAME)

    # The loading airlock and four separately legible furnace cells.
    a.box((18, 5, 4), (34, 17, 10), SHELL, True)
    for x in (18, 34):
        for z in (4, 10):
            a.box((x, 1, z), (x, 18, z), FRAME)
    a.box((18, 10, 5), (18, 14, 9), GLASS)
    a.box((34, 10, 5), (34, 14, 9), GLASS)
    for x0, x1 in ((14, 17), (35, 38)):
        a.box((x0, 5, 5), (x1, 10, 9), SHELL, True)
        a.box((x0, 9, 5), (x1, 10, 5), VENT)
    for x0, x1 in ((20, 22), (30, 32)):
        a.box((x0, 9, 4), (x1, 14, 4), GLASS)
    for x in (23, 29):
        a.box((x, 6, 3), (x, 16, 3), HOT)
    a.box((23, 16, 3), (29, 16, 3), HOT)
    a.box((19, 18, 5), (33, 18, 9), SHELL)
    a.box((24, 6, 3), (28, 7, 11), GUIDE)
    for z in (4, 10):
        for x in range(24, 29):
            for y in range(9, 16):
                a.b.pop((x, y, z), None)

    zones = []
    _thermal_cell(a, '預熱與保護氣氛鎖', 'preheat', 11, 18, 21, SHELL,
                  '封閉氣氛中的坯料升溫意象', zones)
    _thermal_cell(a, '殘餘應力釋放段', 'strain_relief', 20, 28, 22, SHELL,
                  '分段保溫與熱史調節意象', zones)
    _thermal_cell(a, '魂鋼組織重構主爐', 'reconstruction', 30, 40, 25, HOT,
                  '中央重構舱與均勻熱場意象', zones)
    _thermal_cell(a, '均質與受控緩冷段', 'equalize', 42, 49, 21, COLD,
                  '均溫穩定及熱梯度收斂意象', zones)

    # The central raised lattice is the visual heart, not an implemented controller.
    # 四根主柱和三层水平环围住开放的高位重构舱，不封成厂房。
    for x in (18, 34):
        for z in (27, 43):
            a.box((x, 20, z), (x, 38, z), FRAME)
    for x in (18, 34):
        for z in (27, 43):
            a.box((x, 1, z), (x, 20, z), FRAME)
    a.box((20, 23, 27), (32, 33, 27), CORE_GLASS)
    a.box((20, 23, 43), (32, 33, 43), CORE_GLASS)
    for y in (22, 28, 35):
        for x in (18, 34):
            a.box((x, y, 27), (x, y, 43), HOT)
        for z in (27, 43):
            a.box((18, y, z), (34, y, z), HOT)
    for z in (29, 32, 35, 38, 41):
        a.box((18, 36, z), (34, 36, z), COIL)
    for x in (18, 34):
        a.box((x, 36, 27), (x, 36, 43), FRAME)
    core = [26, 30, 35]
    # 两根落在内炉顶的支座托住重构核心，避免拆除整层顶板后悬空。
    for x in (23, 29):
        a.box((x, 16, 35), (x, 26, 35), HOT)
    a.box((23, 26, 32), (29, 32, 38), COIL, True)
    a.box((25, 25, 34), (27, 26, 36), FRAME)
    a.box((24, 29, 33), (28, 31, 37), CORE_GLASS, True)
    for x in (21, 31):
        a.box((x, 25, 30), (x, 34, 40), COIL)
        a.box((min(x, 23), 26, 32), (max(x, 29), 26, 38), HOT)
    zones.append({'name': '魂鋼組織重構觀察舱', 'kind': 'lattice_core',
                  'min': [18, 20, 27], 'max': [34, 38, 43], 'pos': core,
                  'role': '中心識別標記與組織重構意象', 'service_face': '前後觀察窗'})

    # 开口淬冷槽：底板、侧墙和低矮端墙保留介质边界，顶部完全敞开。
    a.box((16, 5, 52), (36, 5, 56), COLD)
    a.box((14, 5, 51), (14, 11, 57), COLD)
    a.box((38, 5, 51), (38, 11, 57), COLD)
    a.box((15, 5, 51), (37, 7, 51), COLD)
    a.box((15, 5, 57), (37, 7, 57), COLD)
    for x in (14, 38):
        for z in (51, 57):
            a.box((x, 1, z), (x, 4, z), FRAME)
    a.box((17, 8, 51), (35, 10, 51), CORE_GLASS)
    a.box((17, 8, 57), (35, 10, 57), CORE_GLASS)
    a.box((24, 6, 50), (28, 7, 59), GUIDE)
    for z in (51, 57):
        for x in range(24, 29):
            for y in range(11, 15):
                a.b.pop((x, y, z), None)
    zones.append({'name': '緩冷、淬冷與檢測出料段', 'kind': 'quench_inspection',
                  'min': [14, 5, 51], 'max': [38, 11, 57], 'pos': [26, 11, 54],
                  'role': '冷卻介質與成品檢測意象', 'service_face': '後側'})

    # Side galleries remain walkable; the off-axis tower is grounded and ducted to the cold end.
    for x in (11, 41):
        for z in (9, 19, 29, 41, 50, 54):
            a.box((x, 1, z), (x, 19, z), FRAME)
        for y in (5, 11, 17):
            a.box((x, y, 9), (x, y, 54), SHELL)
        for z in (11, 20, 40, 49, 51):
            a.box((min(x, 13 if x == 11 else 39), 5, z),
                  (max(x, 13 if x == 11 else 39), 5, z), FRAME)
    a.box((39, 19, 45), (49, 22, 48), DUCT)
    # 三格宽的落地换热塔：立柱、稀疏鳍片和开放式冠部，避免第二个实心高炉。
    for x in (49, 51):
        for z in (47, 55):
            a.box((x, 1, z), (x, 10, z), FRAME)
            a.box((x, 10, z), (x, 32, z), HOT)
    for z in (48, 51, 54):
        a.box((49, 12, z), (51, 30, z), VENT)
    for y in (12, 21, 30):
        a.box((49, y, 47), (51, y, 55), FRAME)
    for z in (47, 55):
        a.box((49, 33, z), (51, 35, z), SHELL)
    a.box((49, 33, 47), (49, 35, 55), SHELL)
    a.box((51, 33, 47), (51, 35, 55), SHELL)
    zones.append({'name': '逆流熱回收塔', 'kind': 'heat_recovery',
                  'min': [49, 10, 47], 'max': [51, 35, 55], 'pos': [50, 35, 51],
                  'role': '高位換熱鳍面與循環管匯意象', 'service_face': '東側'})

    # Symmetric front service panel. Ports are inert placeholders pending a formal pattern.
    a.box((5, 1, 2), (47, 2, 4), PANEL)
    a.box((6, 3, 2), (46, 3, 4), FRAME)
    port_specs = [
        ('BILLET', 7, '魂鋼坯料輸入候選'),
        ('ATMOSPHERE', 15, '保護氣氛輸入候選'),
        ('POWER', 23, '加熱供能候選'),
        ('COOLANT', 30, '冷卻介質輸入候選'),
        ('PRODUCT', 38, '成品輸出候選'),
        ('THERMAL_LOG', 46, '熱史資料輸出候選'),
    ]
    ports = []
    for key, x, purpose in port_specs:
        a.box((x - 1, 3, 1), (x + 1, 3, 1), PANEL)
        a.box((x, 3, 2), (x, 4, 3), FRAME)
        a.set(x, 4, 1, PORT)
        ports.append({'id': key, 'pos': [x, 4, 1], 'face': 'north', 'purpose': purpose})
    controller = [26, 5, 1]
    a.box((25, 1, 1), (27, 3, 2), PANEL)
    a.box((25, 4, 2), (27, 6, 2), PANEL)
    a.box((25, 4, 1), (27, 6, 1), 'gtceu:clean_machine_casing')
    a.set(*controller, 'minecraft:diamond_block')

    paths = [
        {'name': '西側地面檢修廊', 'min': [4, 1, 9], 'max': [9, 5, 54]},
        {'name': '東側地面檢修廊', 'min': [43, 1, 9], 'max': [46, 5, 54]},
    ]
    links = [
        {'from': '前端裝料氣鎖', 'to': '四個退火工段', 'route': [[26, 13, 9], [26, 13, 11]]},
        {'from': '四個退火工段', 'to': '末端緩冷淬冷段', 'route': [[26, 13, 49], [26, 13, 51]]},
        {'from': '末端冷卻段', 'to': '逆流熱回收塔', 'route': [[38, 18, 47], [48, 20, 47]]},
    ]
    a.zones = zones
    a.paths = paths
    a.links = links
    description = (
        '「爐序織衡」以一條平直、逐段收束的熱處理廊承接壓鑄粗坯。'
        '前端雙層氣鎖後，坯料依次通過預熱、消應力、中央魂鋼組織重構、均質緩冷與末端淬冷檢測；'
        '中部抬升的觀察舱把組織重構作為全廠焦點，東側落地熱回收塔以換熱鳍片收束輪廓。'
        '長向物料軸、重複保溫節與冷端材質對比，讓它和 I14 的四柱壓鑄機明確分開。'
    )
    return {
        'key': 'i15', 'name': 'i15-soulsteel-anneal-furnace-v2',
        'title': '魂钢重构退火炉', 'candidate_version': 'V2 炉序织衡',
        'size': [a.w, a.h, a.d], 'core_marker': controller, 'visual_core': core,
        'controller': controller,
        'ports': ports, 'paths': paths, 'zones': zones, 'links': links,
        'brief': brief, 'description': description,
        'role_materials': {key: sorted(value) for key, value in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


def _write_material_basis(states, counts):
    resources = Resources(instance=INSTANCE)
    rows = []
    try:
        for state in states:
            if state in MARKERS:
                rows.append({'方块状态': state, '实际数量': counts[state],
                             '用途': '项目规定的核心/接口标记',
                             '资源与完整形体': '由项目结构规则指定；接口仅为空白填充，不代表能力',
                             '阶段与生存获取': '不作普通建材阶段声明'})
                continue
            material = resources.material(state)
            ns, block = state.split(':', 1)
            block = block.split('[', 1)[0]
            source = resources.sources.get(f'assets/{ns}/blockstates/{block}.json', '资源读取来源未记录')
            rows.append({'方块状态': state, '实际数量': counts[state],
                         '用途': MATERIAL_ROLES.get(state, '结构构件'),
                         '模型': material['model'], '目标实例资源来源': source,
                         '完整方块核验': material['complete_cube'],
                         '阶段与生存获取': '未核验配方、科技前置与实际可达阶段'})
    finally:
        resources.close()
    return rows


def _write_index(data, audit):
    w, h, d = data['size']
    blocks = len(data['blocks'])
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I15 · 炉序织衡</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#111814;color:#edf2e9;font:16px/1.75 "Microsoft YaHei",sans-serif}}a{{color:#e5c58e;text-decoration:none}}a:hover{{color:#fff}}main{{max-width:1440px;margin:auto;padding:32px clamp(18px,4vw,56px) 54px}}.tag{{color:#8db5a6;font-size:13px;letter-spacing:1px}}h1{{font-size:34px;line-height:1.25;margin:9px 0 10px}}.lede{{max-width:900px;color:#cad3ca;margin:0 0 22px}}nav{{display:flex;gap:18px;flex-wrap:wrap;margin:18px 0 24px}}nav a{{padding:8px 0;border-bottom:1px solid #95744d}}.hero{{border-top:1px solid #526052;border-bottom:1px solid #526052;background:#1b241e;padding:12px}}.hero img{{display:block;width:100%;max-height:700px;object-fit:contain}}.facts{{display:flex;gap:28px;flex-wrap:wrap;color:#c0cbbd;margin:18px 0}}.facts b{{color:#f1d2a0;font-weight:600}}.band{{border-top:1px solid #36463a;margin-top:30px;padding-top:18px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px}}h2{{font-size:18px;margin:0 0 6px}}.band p,.note{{color:#b9c6bb;margin:0}}.note{{font-size:14px;margin-top:25px;max-width:1100px}}@media(max-width:760px){{main{{padding-top:24px}}h1{{font-size:29px}}.band{{grid-template-columns:1fr;gap:18px}}}}</style></head><body><main>
<div class="tag">HK3GTL · I15 · 外观候选 V2</div><h1>魂钢重构退火炉 · 炉序织衡</h1>
<p class="lede">让材料经历可读的“热史”：从密闭进料、逐段均温，到魂钢组织重构，再经缓冷与末端淬冷。建筑沿直线工艺轴展开，以一座抬升的观察舱作为视觉中心。</p>
<nav><a href="三维评审.html">打开可旋转三维评审</a><a href="{data['name']}.schem">下载 Sponge Schematic</a><a href="{data['name']}.nbt">下载结构 NBT</a><a href="设计与检查.json">结构与审计记录</a><a href="材料依据.json">逐块材料依据</a><a href="设计参考.json">设计参照</a></nav>
<div class="hero"><img src="等轴预览.png" alt="魂钢重构退火炉炉序织衡外观预览"></div>
<div class="facts"><span><b>{w} × {d} × {h}</b> 方块（宽×深×高）</span><span><b>{blocks:,}</b> 个实体方块</span><span><b>{len(data['zones'])}</b> 个建筑分区</span><span>69座下限：29 × 49 × 27，通过</span></div>
<section class="band"><div><h2>热史廊</h2><p>四段可见的退火炉节沿长轴排列；前端气锁、地面导料脊与各区观察窗建立进料方向。</p></div><div><h2>组织重构舱</h2><p>中段抬升的玻璃格舱把重构核心提到视觉中心；钻石块仅作结构识别标记。</p></div><div><h2>冷端与热回收</h2><p>缓冷、淬冷和逆流换热塔落在后端与东侧，冷材质和密集鳍面收住长炉的尾部。</p></div></section>
<section class="band"><div><h2>连续炉体</h2><p>Tenova 的连续退火设备资料呈现长向炉体、保护气氛、分区加热与冷却。</p><p><a href="https://tenova.com/technologies/continuous-annealing-furnace-long-products">Tenova · Continuous Annealing Furnace ↗</a></p></div><div><h2>分区节拍</h2><p>Primetals 的连续线资料提供预热、辐射加热、均热与快速冷却的工序序列。</p><p><a href="https://www.primetals.com/en/metals-magazine/cgl-value-added-strip-for-the-automotive-market/">Primetals · Continuous Galvanizing Line ↗</a></p></div><div><h2>原创转译</h2><p>本稿把分区炉节、观察舱和热回收塔转成 Minecraft 完整方块构件；不复刻现实设备尺寸，也不代表已实现配方或机器功能。</p><p><a href="设计参考.json">查看参照说明与边界</a></p></div></section>
<p class="note">候选结构，不是用户批准版本。当前只核实方块资源与完整立方体模型；配方前置、生存阶段可达性、正式 Pattern、接口能力、Minecraft 成型与运行均未验收。本轮未改配方或测试实例。</p>
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
    data = build()
    data['construction_notes'] = {
        'origin': [0, 0, 0], 'paste_anchor': [0, 0, 0], 'schematic_offset': [0, 0, 0],
        'orientation': 'X向东、Y向上、Z向南；六个接口候选面朝北（-Z）。',
        'recommended_bottom_world_y': -60,
        'world_height_range': [-60, -60 + data['size'][1] - 1],
        'status': 'V2外观候选，待用户审阅；未批准、未部署。',
        'core_marker': '钻石块沿用本项目既有约定，标在前端控制锚点；中央组织重构舱是视觉核心。标记不代表已接入实际控制器或功能方块。',
        'ports': 'industrial_port_casing 仅为空白接口候选，不具物品、流体或供能能力。',
        'recipe_boundary': '建筑表达工艺意象；不证明 I15 当前 provisional 配方已覆盖这些处理路线。',
    }
    preview.TEST_INSTANCE = INSTANCE
    preview.package(data, OUT, 'i07', [
        '五段纵向炉序、中央组织重构舱、末端淬冷与偏置热回收塔形成独立轮廓',
        '所有实体材料均通过目标实例完整立方体模型核验',
        '两侧检修廊与六个接口候选的服务面保持净空',
        '几何只使用水平和垂直网格，不含斜向构件',
    ])
    block_states = {tuple(q['pos']): q['state'] for q in data['blocks']}
    assert block_states[tuple(data['core_marker'])] == 'minecraft:diamond_block'
    assert data['core_marker'] == data['controller']
    assert data['visual_core'] == [26, 30, 35]

    # 用 Minecraft Builder/Lodestone 重新导出 NBT，并检查每个方块坐标与状态。
    nbt_sha = lodestone_export(data, OUT, LOG)
    schem = OUT / (data['name'] + '.schem')
    nbt = OUT / (data['name'] + '.nbt')
    structure = nbtlib.load(schem)
    structure['Offset'] = nbtlib.IntArray([0, 0, 0])
    structure.save(schem, gzipped=True)
    assert [int(v) for v in nbtlib.load(schem)['Offset']] == [0, 0, 0]

    record_path = OUT / '设计与检查.json'
    record = json.loads(record_path.read_text(encoding='utf-8'))
    audit = record['audit']
    counts = collections.Counter(block['state'] for block in data['blocks'])
    ordinary = collections.Counter()
    for state, count in counts.items():
        if state not in MARKERS:
            ordinary[state.split(':', 1)[0]] += count
    ordinary_total = sum(ordinary.values())
    audit.update({
        'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'instance': str(INSTANCE),
        'approval': 'V2待用户审阅；未批准、未部署，不计入 batch-06。',
        'hashes': {'nbt': nbt_sha, 'schem': hashlib.sha256(schem.read_bytes()).hexdigest()},
        'design_markers': {state: counts[state] for state in counts if state in MARKERS},
        'ordinary_namespace_counts': dict(ordinary),
        'ordinary_namespace_percent': {ns: round(n / ordinary_total * 100, 2) for ns, n in ordinary.items()},
        'material_basis': '材料依据.json',
        'checks': audit['checks'] + [
            'Minecraft Builder/Lodestone NBT重新导出且逐格回读一致',
            '前端钻石控制锚点、中央视觉核心与六个工业接口填充候选分别核对',
            f"高度锚定 -60 时实体范围为 -60 至 {-60 + data['size'][1] - 1}，低于 Y=236",
        ],
        'not_verified': [
            '普通建材的最终配方、科技前置和阶段可达性',
            'I15正式Pattern、仓室能力与结构成型',
            'Minecraft运行、游戏内朝向与玩家交互',
            '最终审核前的用户外观批准',
        ],
    })
    assert audit['design_markers'] == {'minecraft:diamond_block': 1, PORT: 6}
    audit['size_baseline']['reference_note'] = '按当前规则指定的69座规划 HTML；structure_catalog.json 为旧值，不作为本次下限。'
    audit['material_counts'] = {state: counts[state] for state in sorted(counts)}
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')

    basis = _write_material_basis(sorted(counts), counts)
    (OUT / '材料依据.json').write_text(json.dumps({
        '目标实例': str(INSTANCE), '用途说明': '方块资源与完整形体已按目标实例静态资源解析；生存获取和阶段前置不在本报告结论内。',
        '材料': basis,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    references = {
        'machine': 'I15 魂钢重构退火炉 · 炉序织衡 V2',
        'sources': [
            {
                'title': 'Tenova · Continuous Annealing Furnace for Long Products',
                'url': 'https://tenova.com/technologies/continuous-annealing-furnace-long-products',
                'used_as': '长向连续炉体、保护气氛、分区加热与冷却、余热回收的造型参照。',
            },
            {
                'title': 'Primetals Technologies · CGL: Value-Added Strip for the Automotive Market',
                'url': 'https://www.primetals.com/en/metals-magazine/cgl-value-added-strip-for-the-automotive-market/',
                'used_as': '预热、辐射加热、均热、快速冷却等连续热处理工序顺序的参照。',
            },
        ],
        'original_translation': '本稿改为水平分段炉廊、中央抬升观察舱、末端淬冷区和偏置落地热回收塔；只借鉴工业分区关系，不复制设备尺寸。',
        'boundary': '工艺说明属于建筑表达，不证明 I15 配方、Pattern、仓室能力或游戏内运行已实现。',
    }
    (OUT / '设计参考.json').write_text(json.dumps(references, ensure_ascii=False, indent=2), encoding='utf-8')

    # 同步最新审计信息到交互预览载荷。
    payload_file = OUT / 'data.js'
    encoded = json.loads(payload_file.read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    payload['audit'] = audit
    payload['data'] = record['data']
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False,
        separators=(',', ':')).encode('utf-8'), compresslevel=9)).decode('ascii')
    payload_file.write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')

    page_path = OUT / '三维评审.html'
    page = page_path.read_text(encoding='utf-8')
    page = page.replace('<title>探测器精密校准台 · 自由设计候选</title>', '<title>I15 · 魂钢重构退火炉 · 炉序织衡 V2</title>')
    page = page.replace('<a href="设计与检查.json">← 设计与检查</a>', '<a href="index.html">← 炉序织衡</a>')
    page = page.replace('<h1>探测器精密校准台</h1>', '<h1>魂钢重构退火炉 · 炉序织衡</h1>')
    page = page.replace('自由设计候选', 'V2 外观候选')
    page = page.replace('本机建筑概念</summary><p>', '炉序织衡概念</summary><p>')
    page = page.replace('纵向四区连续退火厂：前端气闸上料，经四段梯度热处理后进入后端淬冷整形池，侧塔记录温度曲线并完成检测。', data['description'])
    page = page.replace('未接入生产Pattern，未实测浏览器交互或游戏。此处为实际方块坐标与本地纹理渲染，首帧材质不代表全部动态效果。',
        '外观候选，不代表正式 Pattern 或配方已接通。当前逐种方块资源与完整立方体模型已核验；阶段可达性、游戏成型和实际运行尚未验收。')
    page = page.replace('i15-soulsteel-anneal-free.nbt', data['name'] + '.nbt')
    page = page.replace('i15-soulsteel-anneal-free.schem', data['name'] + '.schem')
    page = page.replace('<script src="data.js"></script>', '<script src="data.js"></script>')
    page_path.write_text(page, encoding='utf-8')
    _write_index(data, audit)

    script_dir = OUT / '生成脚本'
    script_dir.mkdir(exist_ok=True)
    for source_name in (Path(__file__).name, 'verify_i15_soulsteel_anneal_v2.py'):
        shutil.copy2(Path(__file__).with_name(source_name), script_dir / source_name)
    entry = {
        'key': data['key'], 'title': data['title'], 'candidate_version': data['candidate_version'],
        'size_xyz': data['size'], 'size_wdh': [data['size'][0], data['size'][2], data['size'][1]],
        'blocks': len(data['blocks']), 'materials': len(counts), 'zones': len(data['zones']),
        'core_marker': data['core_marker'], 'visual_core': data['visual_core'],
        'size_baseline': audit['size_baseline'], 'design_markers': audit['design_markers'],
        'status': audit['approval'], 'instance': str(INSTANCE),
        'hashes': audit['hashes'],
    }
    (OUT / 'manifest.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
    archive = _bundle()
    entry['archive'] = archive
    (LOG / 'final-verification.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(entry, ensure_ascii=False))


if __name__ == '__main__':
    main()
