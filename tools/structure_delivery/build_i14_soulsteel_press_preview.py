# -*- coding: utf-8 -*-
"""I14 魂钢聚合压铸机：重型液压压铸线预览。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I14_魂钢聚合压铸机_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'


def build():
    brief = {'id': 'I14', 'title': '魂钢聚合压铸机',
             'minimum_wdh': [33, 37, 29], 'catalog_minimum_wdh': [33, 37, 29],
             'form': '重型液压压铸线',
             'flow': '魂钢熔料预热、真空聚合、液压压铸、冷却脱模与成品输出'}
    width, height, depth = 49, 33, 41
    a = Build(brief); a.w, a.h, a.d = width, height, depth; a.cx, a.cz = 24, 20
    floor = 'ad_astra:ostrum_plating'; base = 'gtlcore:space_elevator_mechanical_casing'
    rib = 'gtlcore:lafium_mechanical_casing'; shell = 'hk3gtl:voltage_machine_casing_hbv'
    heavy = 'gtceu:high_power_casing'; panel = 'gtceu:advanced_computer_casing'
    glass = 'gtlcore:rhenium_reinforced_energy_glass'; rail = 'gtceu:assembly_line_grating'
    gear = 'gtceu:tungstensteel_gearbox'; pipe = 'gtceu:tungstensteel_pipe_casing'
    press = 'gtlcore:graviton_field_constraint_casing'; coil = 'kubejs:titansteel_coil_block[active=false]'
    arm = 'gtlcore:manipulator'; vent = 'gtceu:computer_heat_vent'; cool = 'gtlcore:cold_ice_casing'
    a.box((0, 0, 0), (48, 0, 40), floor); frame(a, 0, 48, 1, 0, 40, base)
    a.box((2, 1, 5), (46, 2, 35), heavy)
    # Longitudinal die bed and two material rails.
    a.box((5, 3, 14), (43, 5, 26), rail)
    for z, mat in ((12, shell), (28, rib)):
        a.box((5, 3, z), (43, 4, z), mat)
        for x in range(8, 44, 6): a.box((x, 4, z), (x + 1, 4, z), gear)
    # Four hydraulic columns and the upper press crown.
    for x in (9, 39):
        for z in (10, 30):
            a.box((x, 3, z), (x + 2, 29, z + 2), heavy)
            a.box((x + 1, 7, z - 1), (x + 1, 25, z - 1), pipe)
    a.box((7, 28, 9), (41, 31, 31), heavy)
    a.box((12, 31, 13), (36, 32, 27), rail)
    # Central die chamber with a visible upper ram, coil jacket, and cooling gaps.
    a.box((16, 6, 12), (32, 25, 28), shell, True)
    a.box((18, 8, 14), (30, 22, 26), glass, True)
    a.box((20, 10, 16), (28, 20, 24), press, True)
    a.box((22, 11, 18), (26, 19, 22), coil, True)
    a.box((23, 8, 19), (25, 24, 21), arm)
    a.box((19, 23, 17), (29, 24, 23), heavy)
    for y in (8, 13, 18, 23):
        a.box((17, y, 13), (31, y, 27), rib)
    # Left melt preparation and vacuum feed train.
    a.box((3, 6, 6), (13, 20, 11), shell, True)
    a.box((5, 8, 7), (11, 17, 10), glass, True)
    a.box((4, 20, 7), (12, 21, 10), rail)
    for x in (5, 8, 11):
        a.box((x, 9, 5), (x, 18, 5), pipe); a.box((x, 18, 5), (x, 18, 10), gear)
    a.box((13, 12, 8), (18, 14, 8), pipe)
    # Right cooling and demoulding line.
    a.box((35, 6, 30), (45, 22, 35), cool, True)
    a.box((37, 8, 31), (43, 19, 34), glass, True)
    for z in (31, 34):
        a.box((36, 9, z), (44, 20, z), vent)
    a.box((34, 20, 29), (46, 21, 36), rail)
    a.box((38, 22, 29), (42, 27, 36), arm)
    # Service catwalk and cooling manifold.
    a.box((5, 24, 7), (43, 25, 9), rail); a.box((5, 24, 31), (43, 25, 33), rail)
    for x in (8, 18, 28, 38):
        a.box((x, 24, 8), (x, 30, 8), rib); a.box((x, 24, 32), (x, 30, 32), rib)
    a.box((8, 30, 8), (40, 30, 32), pipe)
    for x in range(12, 40, 7): a.box((x, 26, 8), (x, 26, 32), vent)
    # Front control apron, controller, and six ports.
    a.box((6, 1, 1), (42, 3, 4), panel)
    a.box((11, 4, 1), (16, 7, 4), shell, True); a.box((31, 4, 1), (36, 7, 4), cool, True)
    controller = [24, 6, 2]; a.box((24, 3, 2), (24, 5, 2), panel); a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [('INGOT', [8, 5, 1], '魂钢熔料输入'), ('BINDER', [13, 5, 1], '聚合粘结剂输入'), ('POWER', [18, 5, 1], '液压与供能'), ('COOLANT', [30, 5, 1], '冷却介质输入'), ('PRODUCT', [35, 5, 1], '压铸件输出'), ('SCRAP', [40, 5, 1], '浇口与废料输出')]
    for _, pos, _ in ports:
        x, y, z = pos; a.box((x, 3, z), (x, 4, z + 1), panel); a.set(x, 5, z + 1, panel); a.set(*pos, PORT)
    zones = [
        {'name': '魂钢熔料预处理舱', 'kind': 'melt_prep', 'min': [3, 3, 5], 'max': [13, 21, 11], 'pos': [8, 21, 8], 'role': '预热、抽真空与熔料计量', 'service_face': '前侧'},
        {'name': '中央真空压铸腔', 'kind': 'die_chamber', 'min': [16, 6, 12], 'max': [32, 25, 28], 'pos': [24, 25, 20], 'role': '魂钢聚合与液压压铸', 'service_face': '四周'},
        {'name': '液压立柱与压头冠', 'kind': 'hydraulic_crown', 'min': [7, 28, 9], 'max': [41, 32, 31], 'pos': [24, 32, 20], 'role': '压头下行、锁模与承载', 'service_face': '顶部'},
        {'name': '冷却脱模与检测线', 'kind': 'cooling_demould', 'min': [34, 6, 29], 'max': [46, 27, 36], 'pos': [40, 27, 33], 'role': '冷却、脱模与成品检测', 'service_face': '东侧'},
    ]
    links = [{'from': '魂钢熔料预处理舱', 'to': '中央真空压铸腔', 'route': [[13, 13, 8], [16, 13, 18]]}, {'from': '中央真空压铸腔', 'to': '冷却脱模与检测线', 'route': [[32, 18, 20], [35, 18, 33]]}, {'from': '中央真空压铸腔', 'to': '液压立柱与压头冠', 'route': [[24, 25, 20], [24, 28, 20]]}]
    return {'key': 'i14', 'name': 'i14-soulsteel-press-free', 'title': brief['title'], 'size': [width, height, depth], 'controller': controller, 'ports': [{'id': k, 'pos': p, 'face': 'north', 'purpose': q} for k, p, q in ports], 'paths': [], 'zones': zones, 'links': links, 'brief': brief, 'description': '魂钢聚合压铸机采用重型液压压铸线：左端熔料预处理与真空计量，中部透明真空压铸腔由四根液压立柱承载，顶部压头冠完成锁模和下行，右侧冷却脱模塔负责检测与分流；前侧集中控制与六个工业接口。', 'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}


if __name__ == '__main__':
    package(build(), OUT, 'i07', ['重型液压立柱、中央真空压铸腔、冷却脱模塔与顶部压头冠', '端口前方保持开放净空'])
