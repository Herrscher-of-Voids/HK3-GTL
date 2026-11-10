"""I10 纳米基元合成器：横向洁净压合线，与 I09 的配制釜造型区分。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I10_纳米基元合成器_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'
FLOOR = 'ad_astra:ostrum_plating'

def build():
    brief = {'id': 'I10', 'title': '纳米基元合成器', 'minimum_wdh': [21, 25, 21], 'catalog_minimum_wdh': [21, 25, 21]}
    width, depth, height = 41, 29, 27
    a = Build(brief); a.w, a.d, a.h, a.cx, a.cz = width, depth, height, 20, 14
    a.box((0, 0, 0), (40, 0, 28), FLOOR); frame(a, 0, 40, 1, 0, 28, 'gtlcore:space_elevator_mechanical_casing')
    # Two parallel cleanroom rails make this a linear machine instead of a vessel.
    for z, mat in ((7, 'hk3gtl:voltage_machine_casing_hdv'), (21, 'hk3gtl:voltage_machine_casing_hcv')):
        a.box((3, 1, z), (37, 1, z + 1), mat)
        a.box((3, 2, z), (3, 21, z + 1), mat); a.box((37, 2, z), (37, 21, z + 1), mat)
        for x in (10, 20, 30): a.box((x, 2, z), (x, 2, z + 1), 'gtceu:assembly_line_grating')
    # Three sequential process bays: feed lattice, nano press, and classifier.
    for x, outer, inner in ((9, 'gtlcore:lafium_mechanical_casing', 'gtlcore:rhenium_reinforced_energy_glass'),
                            (20, 'gtceu:high_power_casing', 'hk3gtl:glass_honkai_stabilized'),
                            (31, 'gtlcore:dimension_connection_casing', 'gtlcore:rhenium_reinforced_energy_glass')):
        a.box((x - 4, 3, 5), (x + 4, 19, 5), outer); a.box((x - 4, 3, 23), (x + 4, 19, 23), outer)
        a.box((x - 4, 3, 5), (x - 4, 19, 23), outer); a.box((x + 4, 3, 5), (x + 4, 19, 23), outer)
        a.box((x - 3, 6, 6), (x + 3, 16, 6), inner); a.box((x - 3, 6, 22), (x + 3, 16, 22), inner)
        for y in (6, 12, 18): a.box((x - 5, y, 6), (x + 5, y, 6), 'gtceu:advanced_computer_casing')
    # Suspended nano lattice inside the central press bay, with piston-like jaws.
    for y in range(8, 17):
        r = 1 + min(y - 8, 16 - y) // 2
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if abs(dx) + abs(dz) <= r: a.set(20 + dx, y, 14 + dz, 'hk3gtl:glass_honkai_stabilized' if (dx + dz + y) % 2 else 'kubejs:starmetal_coil_block[active=false]')
    a.line((20, 6, 14), (20, 20, 14), 'gtlcore:advanced_stellar_containment_casing')
    for z in (9, 19):
        a.line((14, 11, z), (18, 11, z), 'gtlcore:manipulator'); a.line((22, 11, z), (26, 11, z), 'gtlcore:manipulator')
    # Overhead moving gantry spans all three bays and is visibly supported.
    a.box((5, 22, 5), (35, 22, 23), 'gtceu:assembly_line_grating', True)
    for x in (7, 20, 33):
        a.box((x, 1, 5), (x, 25, 5), 'gtlcore:lafium_mechanical_casing'); a.box((x, 1, 23), (x, 25, 23), 'gtlcore:lafium_mechanical_casing')
    a.box((18, 25, 12), (22, 26, 16), 'gtceu:high_power_casing')
    a.line((20, 25, 5), (20, 25, 12), 'gtlcore:lafium_mechanical_casing'); a.line((20, 25, 16), (20, 25, 23), 'gtlcore:lafium_mechanical_casing')
    # Rear classifier tower is a vertical stack, separate from the horizontal press.
    a.box((34, 3, 9), (39, 20, 19), 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing', True)
    for y in (6, 12, 18): a.box((35, y, 10), (38, y + 1, 18), 'gtlcore:rhenium_reinforced_energy_glass')
    # Front low operator apron and six interfaces, all anchored to the base.
    a.box((4, 1, 1), (35, 3, 4), 'gtceu:advanced_computer_casing')
    a.box((7, 4, 1), (12, 7, 4), 'gtceu:sterilizing_filter_casing', True); a.box((26, 4, 1), (31, 7, 4), 'gtlcore:super_computation_component[active=false]', True)
    controller = [28, 6, 2]; a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [('PRECURSOR', [7, 5, 1], 'north', '前驱体输入'), ('CATALYST', [12, 5, 1], 'north', '催化剂输入'), ('POWER', [17, 5, 1], 'north', '供能'), ('WASH', [22, 5, 1], 'north', '洗涤介质输入'), ('PRODUCT', [27, 5, 1], 'north', '纳米基元输出'), ('RESIDUE', [32, 5, 1], 'north', '筛分残余输出')]
    for _, pos, _, _ in ports:
        a.box((pos[0], 3, pos[2]), (pos[0], 4, pos[2] + 1), 'gtceu:advanced_computer_casing'); a.set(pos[0], 5, pos[2] + 1, 'gtceu:advanced_computer_casing'); a.set(*pos, PORT)
    return {'key': 'i10', 'name': 'i10-nano-synthesizer-free', 'title': brief['title'], 'size': [width, height, depth], 'controller': controller,
        'ports': [{'id': k, 'pos': p, 'face': f, 'purpose': q} for k, p, f, q in ports], 'paths': [], 'zones': [
        {'name': '进料洁净段', 'kind': 'feed', 'min': [5, 3, 5], 'max': [13, 21, 23], 'pos': [9, 12, 14], 'role': '前驱体与催化剂预处理', 'service_face': '前侧'},
        {'name': '纳米压合舱', 'kind': 'synthesis', 'min': [16, 3, 5], 'max': [24, 26, 23], 'pos': [20, 14, 14], 'role': '基元压合与合成', 'service_face': '四周'},
        {'name': '分级收集段', 'kind': 'collection', 'min': [27, 3, 5], 'max': [39, 20, 23], 'pos': [33, 12, 14], 'role': '产物分级和残余隔离', 'service_face': '后侧'},
        {'name': '顶部移动龙门', 'kind': 'gantry', 'min': [5, 22, 5], 'max': [35, 26, 23], 'pos': [20, 24, 14], 'role': '转运与洁净维护', 'service_face': '顶部'}],
        'links': [{'from': '进料洁净段', 'to': '纳米压合舱', 'route': [[13, 11, 14], [16, 11, 14]]}, {'from': '纳米压合舱', 'to': '分级收集段', 'route': [[24, 13, 14], [31, 13, 14]]}, {'from': '纳米压合舱', 'to': '顶部移动龙门', 'route': [[20, 18, 14], [20, 24, 14]]}], 'brief': brief,
        'description': '纳米基元合成器采用横向洁净压合线：左侧进料洁净段经过中央悬置纳米晶格压合舱，进入右侧分级收集段；顶部移动龙门负责转运与维护，前侧低位平台统一接入。', 'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}

if __name__ == '__main__': package(build(), OUT, 'i10', ['保留21×25×21占地下限', '横向进料、压合、分级收集与顶部转运分区'])
