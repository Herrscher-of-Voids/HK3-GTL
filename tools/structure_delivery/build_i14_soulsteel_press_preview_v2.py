# -*- coding: utf-8 -*-
"""I14 魂钢聚合压铸机：开放式双跨压铸厂房。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I14_魂钢聚合压铸机_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'


def build():
    brief = {
        'id': 'I14', 'title': '魂钢聚合压铸机',
        'minimum_wdh': [33, 37, 29], 'catalog_minimum_wdh': [33, 37, 29],
        'form': '开放式双跨压铸厂房',
        'flow': '魂钢熔料预热、双工位真空聚合、液压压铸、冷却脱模与成品分流',
    }
    width, height, depth = 53, 35, 47
    a = Build(brief); a.w, a.h, a.d = width, height, depth; a.cx, a.cz = 26, 23
    floor = 'ad_astra:ostrum_plating'; foundation = 'gtlcore:space_elevator_mechanical_casing'
    shell = 'hk3gtl:voltage_machine_casing_hbv'; shell2 = 'hk3gtl:voltage_machine_casing_hcv'
    heavy = 'gtceu:high_power_casing'; panel = 'gtceu:advanced_computer_casing'
    glass = 'gtlcore:rhenium_reinforced_energy_glass'; rail = 'gtceu:assembly_line_grating'
    gear = 'gtceu:tungstensteel_gearbox'; pipe = 'gtceu:tungstensteel_pipe_casing'
    press = 'gtlcore:graviton_field_constraint_casing'; cool = 'gtlcore:cold_ice_casing'
    vent = 'gtceu:computer_heat_vent'; arm = 'gtlcore:manipulator'
    coil = 'kubejs:titansteel_coil_block[active=false]'
    a.box((0, 0, 0), (52, 0, 46), floor); frame(a, 0, 52, 1, 0, 46, foundation)
    # Two open production bays, separated by a central logistics spine.
    for x0, x1 in ((3, 22), (30, 49)):
        a.box((x0, 1, 5), (x1, 2, 41), heavy)
        a.box((x0, 3, 7), (x0 + 1, 27, 39), shell)
        a.box((x1 - 1, 3, 7), (x1, 27, 39), shell2)
        a.box((x0 + 2, 3, 7), (x1 - 2, 4, 39), rail)
        for z in (10, 18, 26, 34):
            a.box((x0 + 2, 5, z), (x1 - 2, 6, z + 1), pipe)
            for x in range(x0 + 4, x1 - 2, 5): a.set(x, 6, z, gear)
        # Tall gate frames make the two bays visually distinct from a sealed cube.
        for x in (x0 + 4, x1 - 4):
            a.box((x, 5, 12), (x + 2, 28, 14), heavy)
            a.box((x, 5, 30), (x + 2, 28, 32), heavy)
        a.box((x0 + 3, 27, 10), (x1 - 3, 30, 34), heavy)
        a.box((x0 + 6, 29, 14), (x1 - 6, 30, 30), rail)
    # Central transfer spine and two independent vacuum die cells.
    a.box((23, 3, 4), (29, 8, 42), shell2)
    a.box((24, 5, 6), (28, 7, 40), glass)
    for z in range(9, 40, 6):
        a.box((23, 4, z), (29, 4, z + 1), rail)
        a.set(26, 8, z, gear)
    for x0, x1 in ((7, 18), (35, 46)):
        # Structural feet tie each suspended die cell into its bay floor.
        for x in (x0, x1):
            a.box((x, 3, 16), (x, 8, 30), heavy)
        a.box((x0, 8, 16), (x1, 23, 30), glass, True)
        a.box((x0 + 2, 10, 18), (x1 - 2, 21, 28), press, True)
        a.box((x0 + 4, 12, 20), (x1 - 4, 19, 26), coil, True)
        # Internal service lattice keeps the layered die package one connected machine.
        for x in range(x0, x1 + 1, 3): a.box((x, 8, 20), (x, 23, 20), heavy)
        for y in range(8, 24, 3): a.box((x0, y, 16), (x1, y, 16), heavy)
        a.box((x0 + 1, 23, 17), (x1 - 1, 24, 29), heavy)
        for x in (x0 + 1, x1 - 1): a.box((x, 9, 15), (x, 26, 31), pipe)
    # Overhead gantry crane with offset maintenance walkway.
    a.box((4, 30, 8), (48, 31, 38), rail)
    a.box((8, 32, 10), (44, 33, 12), heavy)
    a.box((10, 33, 10), (10, 34, 38), pipe); a.box((42, 33, 10), (42, 34, 38), pipe)
    for z in (12, 22, 32):
        a.box((10, 31, z), (42, 32, z + 1), arm)
        a.box((25, 29, z), (28, 34, z + 1), arm)
    for z in (14, 24, 34): a.box((16, 31, z), (36, 31, z), vent)
    # Rear cooling towers and demoulding conveyors.
    for x0 in (5, 38):
        a.box((x0, 7, 39), (x0 + 9, 23, 44), cool, True)
        a.box((x0 + 2, 9, 40), (x0 + 7, 20, 43), glass, True)
        a.box((x0 - 1, 22, 39), (x0 + 10, 24, 44), vent)
        a.box((x0 + 1, 24, 40), (x0 + 8, 26, 43), rail)
    # Front apron, controller and six ports.
    a.box((5, 1, 1), (47, 3, 4), panel)
    a.box((22, 3, 1), (30, 6, 4), shell)
    controller = [26, 6, 2]; a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [('INGOT', [8, 5, 1], '魂钢熔料输入'), ('BINDER', [14, 5, 1], '聚合粘结剂输入'), ('POWER', [20, 5, 1], '双工位供能'), ('COOLANT', [32, 5, 1], '冷却介质输入'), ('PRODUCT', [38, 5, 1], '压铸件输出'), ('SCRAP', [44, 5, 1], '浇口废料输出')]
    for _, pos, _ in ports:
        x, y, z = pos; a.box((x, 3, z), (x, 4, z + 1), panel); a.set(x, 5, z + 1, panel); a.set(*pos, PORT)
    zones = [
        {'name': '左跨真空压铸工位', 'kind': 'left_die_bay', 'min': [7, 8, 16], 'max': [18, 24, 30], 'pos': [12, 24, 23], 'role': '第一工位聚合与压铸', 'service_face': '西侧'},
        {'name': '右跨真空压铸工位', 'kind': 'right_die_bay', 'min': [35, 8, 16], 'max': [46, 24, 30], 'pos': [40, 24, 23], 'role': '第二工位并行压铸与换模', 'service_face': '东侧'},
        {'name': '中央熔料输送廊', 'kind': 'transfer_spine', 'min': [23, 3, 4], 'max': [29, 8, 42], 'pos': [26, 8, 23], 'role': '真空计量、分流与回流', 'service_face': '前后贯通'},
        {'name': '后侧冷却脱模塔', 'kind': 'cooling_towers', 'min': [4, 7, 39], 'max': [47, 26, 44], 'pos': [26, 26, 42], 'role': '淬冷、脱模、检测与分流', 'service_face': '后侧'},
    ]
    links = [
        {'from': '中央熔料输送廊', 'to': '左跨真空压铸工位', 'route': [[23, 12, 23], [18, 12, 23]]},
        {'from': '中央熔料输送廊', 'to': '右跨真空压铸工位', 'route': [[29, 16, 23], [35, 16, 23]]},
        {'from': '左跨真空压铸工位', 'to': '后侧冷却脱模塔', 'route': [[12, 23, 30], [12, 23, 39]]},
    ]
    return {'key': 'i14', 'name': 'i14-soulsteel-press-free', 'title': brief['title'], 'size': [width, height, depth], 'controller': controller, 'ports': [{'id': k, 'pos': p, 'face': 'north', 'purpose': q} for k, p, q in ports], 'paths': [], 'zones': zones, 'links': links, 'brief': brief, 'description': '开放式双跨压铸厂房：左右两条独立真空压铸工位由中央熔料输送廊分流，顶部悬臂吊负责换模，后侧冷却脱模塔完成出料。', 'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}


if __name__ == '__main__':
    package(build(), OUT, 'i07', ['开放式双跨压铸厂房、中央输送廊、后侧冷却脱模塔', '端口前方保持开放净空'])
