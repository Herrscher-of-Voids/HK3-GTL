"""I09 魂钢前驱体配制釜：开放式悬置核心与四向计量臂。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I09_魂钢前驱体配制釜_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'
FLOOR = 'ad_astra:ostrum_plating'
GLASS = 'gtlcore:rhenium_reinforced_energy_glass'

def build():
    brief = {'id': 'I09', 'title': '魂钢前驱体配制釜', 'minimum_wdh': [17, 21, 21], 'catalog_minimum_wdh': [17, 21, 21]}
    width, depth, height = 35, 35, 31
    a = Build(brief); a.w, a.d, a.h, a.cx, a.cz = width, depth, height, 17, 17
    a.box((0, 0, 0), (34, 0, 34), FLOOR)
    frame(a, 0, 34, 1, 0, 34, 'gtlcore:space_elevator_mechanical_casing')
    # Four separated pylons leave a readable maintenance void under the vessel.
    for x, z, mat in ((4, 4, 'hk3gtl:voltage_machine_casing_hdv'), (30, 4, 'hk3gtl:voltage_machine_casing_hcv'), (4, 30, 'hk3gtl:voltage_machine_casing_hbv'), (30, 30, 'hk3gtl:voltage_machine_casing_hrv')):
        a.box((x, 1, z), (x + 2, 21, z + 2), mat)
        a.box((x - 1, 5, z), (x + 3, 5, z + 2), 'gtceu:assembly_line_grating')
        a.box((x - 1, 12, z), (x + 3, 12, z + 2), 'gtceu:advanced_computer_casing')
        a.box((x - 1, 19, z), (x + 3, 19, z + 2), 'gtlcore:lafium_mechanical_casing')
    # Radial trusses physically tie each pylon into the lower containment rail.
    for x, z in ((5, 5), (31, 5), (5, 31), (31, 31)):
        a.line((x, 5, z), (17, 5, 17), 'gtlcore:lafium_mechanical_casing')
    # Three non-overlapping orbit rails show containment and mixing stages.
    for y, rx, rz, mat in ((5, 11, 9, 'gtlcore:graviton_field_constraint_casing'), (11, 9, 11, 'gtceu:high_power_casing'), (17, 11, 9, 'gtlcore:dimension_connection_casing')):
        a.box((17 - rx, y, 17 - rz), (17 + rx, y, 17 + rz), mat, True)
        a.box((17 - rx + 2, y, 17 - rz + 2), (17 + rx - 2, y, 17 + rz - 2), GLASS, True)
    # Suspended diamond precursor core; sparse so its windows stay visible.
    for y in range(7, 18):
        radius = 1 + min(y - 7, 17 - y) // 2
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                if abs(dx) + abs(dz) <= radius:
                    mat = 'hk3gtl:glass_honkai_stabilized' if (dx + dz + y) % 3 else 'kubejs:starmetal_coil_block[active=false]'
                    a.set(17 + dx, y, 17 + dz, mat)
    a.line((17, 6, 17), (17, 18, 17), 'gtlcore:advanced_stellar_containment_casing')
    # Central service spine connects the lower rail, core, and charging crown.
    a.line((17, 1, 17), (17, 22, 17), 'gtlcore:advanced_stellar_containment_casing')
    # Four functional arms: feed, return, medium and residue paths.
    for start, end, mat in [((6, 9, 17), (14, 9, 17), 'gtceu:titanium_pipe_casing'), ((28, 13, 17), (20, 13, 17), 'gtceu:tungstensteel_pipe_casing'), ((17, 9, 6), (17, 9, 14), 'gtlcore:dimension_injection_casing'), ((17, 15, 28), (17, 15, 20), 'gtlcore:dimension_connection_casing')]:
        a.line(start, end, mat); a.box((end[0] - 1, end[1] - 1, end[2] - 1), (end[0] + 1, end[1] + 1, end[2] + 1), 'gtceu:advanced_computer_casing')
    for start, end in [((6, 5, 17), (6, 9, 17)), ((28, 5, 17), (28, 13, 17)), ((17, 5, 6), (17, 9, 6)), ((17, 5, 28), (17, 15, 28))]:
        a.line(start, end, 'gtlcore:lafium_mechanical_casing')
    # Charging crown and paired heat-exchange fins.
    a.box((13, 22, 13), (21, 22, 21), 'gtceu:assembly_line_grating')
    for x, z in ((13, 13), (21, 13), (13, 21), (21, 21)): a.line((x, 22, z), (17, 29, 17), 'gtlcore:lafium_mechanical_casing')
    a.box((16, 29, 16), (18, 30, 18), 'gtceu:high_power_casing')
    for x in range(10, 26, 3):
        a.box((x, 23, 9), (x, 27, 9), 'gtceu:computer_heat_vent'); a.box((x, 23, 25), (x, 27, 25), 'gtceu:computer_heat_vent')
        a.line((x, 22, 9), (x, 27, 9), 'gtlcore:lafium_mechanical_casing'); a.line((x, 22, 25), (x, 27, 25), 'gtlcore:lafium_mechanical_casing')
        a.line((x, 22, 9), (x, 22, 13), 'gtlcore:lafium_mechanical_casing'); a.line((x, 22, 13), (13, 22, 13), 'gtlcore:lafium_mechanical_casing')
        a.line((x, 22, 25), (x, 22, 21), 'gtlcore:lafium_mechanical_casing'); a.line((x, 22, 21), (13, 22, 21), 'gtlcore:lafium_mechanical_casing')
    # Low front service apron, six sockets, and dedicated controller.
    a.box((5, 1, 1), (29, 3, 4), 'gtceu:advanced_computer_casing')
    a.box((9, 4, 1), (13, 7, 4), 'gtceu:sterilizing_filter_casing', True)
    a.box((21, 4, 1), (25, 7, 4), 'gtlcore:super_computation_component[active=false]', True)
    controller = [23, 6, 2]; a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [('SOULIUM_FEED', [6, 5, 1], 'north', '魂钢前驱体输入'), ('CATALYST', [10, 5, 1], 'north', '催化剂输入'), ('POWER', [14, 5, 1], 'north', '供能'), ('MEDIUM', [18, 5, 1], 'north', '配制介质输入'), ('PRECURSOR', [22, 5, 1], 'north', '魂钢前驱体输出'), ('RESIDUE', [26, 5, 1], 'north', '残液输出')]
    for _, pos, _, _ in ports:
        a.box((pos[0], 3, pos[2]), (pos[0], 4, pos[2] + 1), 'gtceu:advanced_computer_casing'); a.set(pos[0], 5, pos[2] + 1, 'gtceu:advanced_computer_casing'); a.set(*pos, PORT)
    return {'key': 'i09', 'name': 'i09-soulium-precursor-free', 'title': brief['title'], 'size': [width, height, depth], 'controller': controller,
        'ports': [{'id': key, 'pos': pos, 'face': face, 'purpose': purpose} for key, pos, face, purpose in ports], 'paths': [],
        'zones': [{'name': '悬置魂钢核心', 'kind': 'reactor', 'min': [10, 5, 10], 'max': [24, 20, 24], 'pos': [17, 14, 17], 'role': '前驱体混合与约束', 'service_face': '四周'}, {'name': '四向计量臂', 'kind': 'feed', 'min': [5, 8, 5], 'max': [29, 16, 29], 'pos': [17, 12, 17], 'role': '原料、介质与回流分路', 'service_face': '四向'}, {'name': '顶部充料冠架', 'kind': 'charging', 'min': [10, 22, 9], 'max': [25, 30, 25], 'pos': [17, 27, 17], 'role': '充料与热交换', 'service_face': '顶部'}, {'name': '前侧取样平台', 'kind': 'sampling', 'min': [5, 1, 1], 'max': [29, 7, 4], 'pos': [17, 6, 2], 'role': '取样、控制和产物确认', 'service_face': '北侧'}],
        'links': [{'from': '四向计量臂', 'to': '悬置魂钢核心', 'route': [[6, 9, 17], [14, 9, 17]]}, {'from': '悬置魂钢核心', 'to': '顶部充料冠架', 'route': [[17, 18, 17], [17, 27, 17]]}, {'from': '悬置魂钢核心', 'to': '前侧取样平台', 'route': [[17, 7, 17], [17, 5, 4]]}], 'brief': brief,
        'description': '开放式魂钢前驱体配制釜以悬置菱形核心为中心，四向计量臂接入分路原料，三道轨道环负责约束与混合，顶部冠架承担充料和热交换，前侧低位平台负责取样与控制。', 'role_materials': {key: sorted(value) for key, value in a.roles.items()}, 'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}

if __name__ == '__main__': package(build(), OUT, 'i09', ['保留17×21×21占地下限', '前驱体、介质、供能、产物与残液接口分离'])
