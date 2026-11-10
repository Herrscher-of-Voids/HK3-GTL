"""I11 纳米机器人装配阵列：低矮连续传输带工业线。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I11_纳米机器人装配阵列_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'

def build():
    brief = {'id': 'I11', 'title': '纳米机器人装配阵列', 'minimum_wdh': [25, 29, 21], 'catalog_minimum_wdh': [25, 29, 21]}
    width, depth, height = 45, 39, 27
    a = Build(brief); a.w, a.d, a.h, a.cx, a.cz = width, depth, height, 22, 19
    a.box((0, 0, 0), (44, 0, 38), 'ad_astra:ostrum_plating'); frame(a, 0, 44, 1, 0, 38, 'gtlcore:space_elevator_mechanical_casing')
    # Main conveyor: a long belt bed with rollers, side guards, and service lanes.
    a.box((3, 1, 14), (41, 3, 22), 'gtceu:assembly_line_grating')
    a.box((3, 4, 14), (41, 5, 14), 'hk3gtl:voltage_machine_casing_hdv'); a.box((3, 4, 22), (41, 5, 22), 'hk3gtl:voltage_machine_casing_hcv')
    for x in range(5, 41, 4): a.box((x, 4, 16), (x + 1, 4, 20), 'gtceu:tungstensteel_gearbox')
    a.box((3, 1, 10), (41, 1, 12), 'gtlcore:lafium_mechanical_casing'); a.box((3, 1, 24), (41, 1, 26), 'gtlcore:lafium_mechanical_casing')
    # Six production stations sit directly over the belt, each with a visible arm.
    stations = [(7, 'gtlcore:dimension_injection_casing'), (13, 'gtceu:high_power_casing'), (19, 'gtlcore:graviton_field_constraint_casing'), (25, 'gtlcore:dimension_connection_casing'), (31, 'gtceu:advanced_computer_casing'), (37, 'gtlcore:stellar_containment_casing')]
    for x, mat in stations:
        a.box((x - 2, 6, 15), (x + 2, 13, 21), mat, True)
        a.box((x - 1, 7, 16), (x + 1, 11, 20), 'gtlcore:rhenium_reinforced_energy_glass', True)
        a.box((x, 6, 17), (x, 12, 17), 'gtlcore:manipulator'); a.box((x - 2, 12, 16), (x + 2, 12, 18), 'gtlcore:manipulator')
        a.box((x - 3, 5, 14), (x + 3, 5, 22), 'gtceu:assembly_line_grating')
    # Overhead service rail follows the same line; supports are anchored to floor.
    a.box((5, 19, 11), (39, 19, 25), 'gtceu:assembly_line_grating', True)
    # High service truss keeps the line visually continuous and satisfies the machine's full height envelope.
    a.box((5, 23, 11), (39, 23, 12), 'gtlcore:dimension_connection_casing', True)
    a.box((5, 23, 24), (39, 23, 25), 'gtlcore:dimension_connection_casing', True)
    a.box((5, 25, 11), (39, 25, 12), 'gtlcore:dimension_connection_casing', True)
    a.box((5, 25, 24), (39, 25, 25), 'gtlcore:dimension_connection_casing', True)
    for x in range(7, 40, 8):
        a.box((x, 23, 12), (x, 25, 24), 'gtceu:assembly_line_grating', True)
    a.box((5, 24, 17), (39, 24, 19), 'gtceu:assembly_line_grating', True)
    for x in (5, 17, 29, 39):
        a.box((x, 1, 11), (x, 25, 11), 'gtlcore:lafium_mechanical_casing'); a.box((x, 1, 25), (x, 25, 25), 'gtlcore:lafium_mechanical_casing')
    a.box((20, 20, 17), (24, 22, 19), 'gtceu:high_power_casing')
    # Left loading hopper and right inspection/output tower.
    a.box((1, 5, 14), (5, 15, 22), 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing', True)
    a.box((39, 5, 14), (43, 15, 22), 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing', True)
    a.box((40, 7, 15), (42, 13, 21), 'gtlcore:rhenium_reinforced_energy_glass', True)
    # Front low control and interface rail.
    a.box((5, 1, 1), (39, 3, 4), 'gtceu:advanced_computer_casing'); a.box((11, 4, 1), (17, 7, 4), 'gtceu:sterilizing_filter_casing', True); a.box((29, 4, 1), (35, 7, 4), 'gtlcore:super_computation_component[active=false]', True)
    controller = [32, 6, 2]; a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [('BODY', [8, 5, 1], 'north', '纳米机器人本体输入'), ('CORE', [13, 5, 1], 'north', '核心输入'), ('POWER', [18, 5, 1], 'north', '供能'), ('MATERIAL', [23, 5, 1], 'north', '装配材料输入'), ('ROBOT', [28, 5, 1], 'north', '成品机器人输出'), ('SCRAP', [36, 5, 1], 'north', '装配残余输出')]
    for _, pos, _, _ in ports:
        a.box((pos[0], 3, pos[2]), (pos[0], 4, pos[2] + 1), 'gtceu:advanced_computer_casing'); a.set(pos[0], 5, pos[2] + 1, 'gtceu:advanced_computer_casing'); a.set(*pos, PORT)
    return {'key': 'i11', 'name': 'i11-nanobot-array-free', 'title': brief['title'], 'size': [width, height, depth], 'controller': controller,
        'ports': [{'id': k, 'pos': p, 'face': f, 'purpose': q} for k, p, f, q in ports], 'paths': [], 'zones': [
        {'name': '连续装配传输带', 'kind': 'conveyor', 'min': [3, 1, 10], 'max': [41, 5, 26], 'pos': [22, 4, 18], 'role': '纳米机器人载具连续输送', 'service_face': '前后两侧'},
        {'name': '六段机器人工位', 'kind': 'assembly', 'min': [4, 5, 14], 'max': [40, 13, 22], 'pos': [22, 10, 18], 'role': '连续装配、焊接与校准', 'service_face': '前侧'},
        {'name': '顶部维护轨', 'kind': 'maintenance', 'min': [5, 19, 11], 'max': [39, 22, 25], 'pos': [22, 20, 18], 'role': '机械臂维护和线缆转运', 'service_face': '顶部'},
        {'name': '出料检测塔', 'kind': 'inspection', 'min': [39, 5, 14], 'max': [43, 15, 22], 'pos': [41, 10, 18], 'role': '成品检测与残余分流', 'service_face': '东侧'}],
        'links': [{'from': '连续装配传输带', 'to': '六段机器人工位', 'route': [[10, 5, 18], [10, 9, 18]]}, {'from': '六段机器人工位', 'to': '顶部维护轨', 'route': [[22, 13, 18], [22, 20, 18]]}, {'from': '六段机器人工位', 'to': '出料检测塔', 'route': [[38, 9, 18], [41, 9, 18]]}], 'brief': brief,
        'description': '纳米机器人装配阵列采用横向连续传输带：左端上料，六段机器人在带上连续完成装配、焊接和校准，右端检测塔分流成品与残余；顶部维护轨承担机械臂和线缆维护。', 'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}

if __name__ == '__main__': package(build(), OUT, 'i11', ['保留25×29×21占地下限', '连续传输带、六段机器人、顶部维护轨与出料检测分区'])
