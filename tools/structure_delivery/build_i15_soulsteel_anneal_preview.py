# -*- coding: utf-8 -*-
"""I15 魂钢重构退火炉：纵向四区连续热处理厂。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I15_魂钢重构退火炉_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'


def build():
    brief = {
        'id': 'I15', 'title': '魂钢重构退火炉',
        'minimum_wdh': [29, 49, 27], 'catalog_minimum_wdh': [29, 49, 27],
        'form': '纵向四区连续热处理厂',
        'flow': '魂钢坯料进料、四段梯度退火、保护气氛淬冷、回火整形与成品检测',
    }
    width, height, depth = 47, 35, 53
    a = Build(brief); a.w, a.h, a.d = width, height, depth; a.cx, a.cz = 23, 26
    floor = 'ad_astra:ostrum_plating'; foundation = 'gtlcore:space_elevator_mechanical_casing'
    shell = 'hk3gtl:voltage_machine_casing_hbv'; shell2 = 'hk3gtl:voltage_machine_casing_hcv'
    heat = 'gtceu:high_power_casing'; panel = 'gtceu:advanced_computer_casing'
    glass = 'gtlcore:rhenium_reinforced_energy_glass'; rail = 'gtceu:assembly_line_grating'
    pipe = 'gtceu:tungstensteel_pipe_casing'; gear = 'gtceu:tungstensteel_gearbox'
    coil = 'kubejs:titansteel_coil_block[active=false]'; vent = 'gtceu:computer_heat_vent'
    cool = 'gtlcore:cold_ice_casing'; manip = 'gtlcore:manipulator'
    a.box((0, 0, 0), (46, 0, 52), floor); frame(a, 0, 46, 1, 0, 52, foundation)
    # Long furnace shell with four visually separated thermal zones.
    a.box((4, 2, 4), (42, 28, 48), heat)
    a.box((7, 5, 7), (39, 25, 45), shell, True)
    a.box((10, 7, 9), (36, 23, 43), glass, True)
    for z, mat in ((10, shell2), (19, shell), (28, shell2), (37, shell)):
        a.box((7, 4, z), (39, 26, z + 1), mat)
        a.box((8, 4, z + 2), (38, 4, z + 2), rail)
    # Central production rail and four heat-treatment chambers.
    a.box((20, 5, 5), (26, 7, 47), rail)
    a.box((22, 8, 6), (24, 22, 46), pipe)
    for z0, z1, chamber in ((8, 16, coil), (17, 25, heat), (26, 35, coil), (36, 43, cool)):
        a.box((12, 9, z0), (34, 22, z1), chamber, True)
        a.box((14, 10, z0), (32, 21, z0), glass)
        a.box((14, 10, z1), (32, 21, z1), glass)
        for x in (14, 31): a.box((x, 9, z0), (x, 22, z1), pipe)
    # Ribbed furnace roof and exhaust chimneys make the silhouette unmistakable.
    for z in (9, 18, 27, 36, 45):
        a.box((5, 28, z), (41, 30, z + 1), rail)
        a.box((8, 30, z), (12, 34, z + 1), pipe)
        a.box((34, 30, z), (38, 34, z + 1), pipe)
    for x in (10, 18, 28, 36):
        a.box((x, 30, 12), (x + 1, 34, 44), vent)
    # Side maintenance galleries and cross-braced catwalks.
    for x in (3, 43):
        a.box((x, 5, 6), (x + 1, 24, 47), shell2)
        a.box((x - 1 if x > 20 else x, 6, 7), (x + 1 if x > 20 else x + 2, 6, 47), rail)
        for z in range(10, 48, 8):
            a.box((x - 1 if x > 20 else x, 6, z), (x + 1 if x > 20 else x + 2, 7, z + 1), gear)
    for z in (14, 30, 46):
        a.box((4, 12, z), (42, 13, z + 1), rail)
        for x in range(8, 42, 6): a.set(x, 14, z, manip)
    # Front loading airlock, rear quench basin and inspection tower.
    a.box((12, 5, 3), (34, 22, 6), shell2, True)
    a.box((15, 8, 2), (31, 18, 3), glass)
    a.box((14, 7, 46), (32, 21, 50), cool, True)
    a.box((17, 9, 47), (29, 19, 48), glass, True)
    a.box((35, 7, 44), (41, 25, 49), panel)
    a.box((36, 9, 45), (40, 22, 47), glass, True)
    # Front control apron and six standardized ports.
    a.box((5, 1, 1), (41, 3, 4), panel)
    a.box((20, 3, 1), (26, 6, 4), shell)
    controller = [23, 6, 2]; a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [('BILLET', [8, 5, 1], '魂钢坯料输入'), ('GAS', [14, 5, 1], '保护气氛输入'), ('POWER', [20, 5, 1], '加热供能'), ('COOLANT', [27, 5, 1], '淬冷介质输入'), ('PRODUCT', [34, 5, 1], '退火件输出'), ('DATA', [40, 5, 1], '温度数据输出')]
    for _, pos, _ in ports:
        x, y, z = pos; a.box((x, 3, z), (x, 4, z + 1), panel); a.set(x, 5, z + 1, panel); a.set(*pos, PORT)
    zones = [
        {'name': '前端装料气闸', 'kind': 'loading_airlock', 'min': [12, 5, 3], 'max': [34, 22, 6], 'pos': [23, 22, 5], 'role': '坯料上料与保护气氛置换', 'service_face': '前侧'},
        {'name': '四段梯度退火炉膛', 'kind': 'anneal_chambers', 'min': [10, 7, 8], 'max': [36, 23, 43], 'pos': [23, 23, 26], 'role': '预热、重构退火、均热与回火', 'service_face': '两侧检修廊'},
        {'name': '后端淬冷整形池', 'kind': 'quench_basin', 'min': [14, 7, 44], 'max': [32, 21, 50], 'pos': [23, 21, 50], 'role': '快速淬冷与连续整形', 'service_face': '后侧'},
        {'name': '温度检测塔', 'kind': 'inspection_tower', 'min': [35, 7, 44], 'max': [41, 25, 49], 'pos': [38, 25, 47], 'role': '温度曲线记录与成品检测', 'service_face': '右侧'},
    ]
    links = [
        {'from': '前端装料气闸', 'to': '四段梯度退火炉膛', 'route': [[23, 14, 6], [23, 14, 8]]},
        {'from': '四段梯度退火炉膛', 'to': '后端淬冷整形池', 'route': [[23, 15, 43], [23, 15, 47]]},
        {'from': '后端淬冷整形池', 'to': '温度检测塔', 'route': [[32, 15, 47], [35, 15, 47]]},
    ]
    return {'key': 'i15', 'name': 'i15-soulsteel-anneal-free', 'title': brief['title'], 'size': [width, height, depth], 'controller': controller, 'ports': [{'id': k, 'pos': p, 'face': 'north', 'purpose': q} for k, p, q in ports], 'paths': [], 'zones': zones, 'links': links, 'brief': brief, 'description': '纵向四区连续退火厂：前端气闸上料，经四段梯度热处理后进入后端淬冷整形池，侧塔记录温度曲线并完成检测。', 'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}


if __name__ == '__main__':
    package(build(), OUT, 'i07', ['纵向四区连续退火炉膛、两侧维护廊、后端淬冷池与检测塔', '端口前方保持开放净空'])
