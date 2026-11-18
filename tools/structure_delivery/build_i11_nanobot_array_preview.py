"""I11 纳米机器人装配阵列：三舱并列的机器人洁净装配阵列。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I11_纳米机器人装配阵列_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'

def build():
    brief = {'id': 'I11', 'title': '纳米机器人装配阵列', 'minimum_wdh': [25, 29, 21], 'catalog_minimum_wdh': [25, 29, 21]}
    width, depth, height = 41, 39, 27
    a = Build(brief); a.w, a.d, a.h, a.cx, a.cz = width, depth, height, 19, 16
    a.box((0, 0, 0), (40, 0, 38), 'ad_astra:ostrum_plating'); frame(a, 0, 40, 1, 0, 38, 'gtlcore:space_elevator_mechanical_casing')
    a.box((0, 1, 38), (40, 1, 38), 'gtlcore:lafium_mechanical_casing')
    # Three independent clean assembly cells, each visibly containing a robot arm.
    for cx, casing, window in ((8, 'hk3gtl:voltage_machine_casing_hdv', 'gtlcore:rhenium_reinforced_energy_glass'), (19, 'hk3gtl:voltage_machine_casing_hcv', 'hk3gtl:glass_honkai_stabilized'), (30, 'hk3gtl:voltage_machine_casing_hbv', 'gtlcore:rhenium_reinforced_energy_glass')):
        a.box((cx - 4, 1, 6), (cx + 4, 1, 26), casing); a.box((cx - 4, 1, 6), (cx + 4, 18, 6), casing); a.box((cx - 4, 1, 26), (cx + 4, 18, 26), casing)
        a.box((cx - 3, 4, 7), (cx + 3, 15, 7), window); a.box((cx - 3, 4, 25), (cx + 3, 15, 25), window)
        for y in (5, 11, 17):
            a.box((cx - 5, y, 6), (cx + 5, y, 6), 'gtceu:assembly_line_grating')
        # articulated vertical arm and horizontal gripper
        a.box((cx, 2, 15), (cx, 13, 15), 'gtlcore:manipulator'); a.box((cx - 3, 13, 15), (cx + 3, 13, 15), 'gtlcore:manipulator')
        a.box((cx - 1, 14, 14), (cx + 1, 16, 16), 'gtceu:advanced_computer_casing')
    # Central transfer spine joins the three cells and carries robot carriers.
    a.box((8, 19, 14), (30, 20, 18), 'gtceu:assembly_line_grating')
    for x in (8, 19, 30): a.box((x, 18, 14), (x, 22, 18), 'gtlcore:lafium_mechanical_casing')
    for x in (13, 19, 25): a.box((x, 20, 15), (x, 20, 17), 'gtceu:tungstensteel_pipe_casing')
    # Upper observation bridge, anchored by two end gantries.
    a.box((5, 21, 8), (33, 21, 24), 'gtceu:assembly_line_grating', True)
    for x in (5, 33): a.box((x, 1, 8), (x, 24, 8), 'gtlcore:lafium_mechanical_casing'); a.box((x, 1, 24), (x, 24, 24), 'gtlcore:lafium_mechanical_casing')
    a.box((17, 22, 14), (21, 23, 18), 'gtceu:high_power_casing')
    # Front control apron and six interfaces.
    a.box((4, 1, 1), (34, 3, 4), 'gtceu:advanced_computer_casing'); a.box((7, 4, 1), (13, 7, 4), 'gtceu:sterilizing_filter_casing', True); a.box((25, 4, 1), (31, 7, 4), 'gtlcore:super_computation_component[active=false]', True)
    controller = [28, 6, 2]; a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [('BODY', [7, 5, 1], 'north', '纳米机器人本体输入'), ('CORE', [12, 5, 1], 'north', '核心输入'), ('POWER', [17, 5, 1], 'north', '供能'), ('MATERIAL', [22, 5, 1], 'north', '装配材料输入'), ('ROBOT', [27, 5, 1], 'north', '成品机器人输出'), ('SCRAP', [32, 5, 1], 'north', '装配残余输出')]
    for _, pos, _, _ in ports:
        a.box((pos[0], 3, pos[2]), (pos[0], 4, pos[2] + 1), 'gtceu:advanced_computer_casing'); a.set(pos[0], 5, pos[2] + 1, 'gtceu:advanced_computer_casing'); a.set(*pos, PORT)
    return {'key': 'i11', 'name': 'i11-nanobot-array-free', 'title': brief['title'], 'size': [width, height, depth], 'controller': controller,
        'ports': [{'id': k, 'pos': p, 'face': f, 'purpose': q} for k, p, f, q in ports], 'paths': [], 'zones': [
        {'name': '三舱机器人阵列', 'kind': 'assembly', 'min': [4, 1, 6], 'max': [34, 18, 26], 'pos': [19, 10, 16], 'role': '纳米机器人分段装配', 'service_face': '前后两侧'},
        {'name': '中央转运脊', 'kind': 'transfer', 'min': [8, 18, 14], 'max': [30, 23, 18], 'pos': [19, 21, 16], 'role': '机器人载具转运', 'service_face': '上方'},
        {'name': '观测维护桥', 'kind': 'maintenance', 'min': [5, 21, 8], 'max': [33, 23, 24], 'pos': [19, 22, 16], 'role': '洁净维护和校准', 'service_face': '顶部'}],
        'links': [{'from': '三舱机器人阵列', 'to': '中央转运脊', 'route': [[19, 14, 15], [19, 20, 16]]}, {'from': '中央转运脊', 'to': '观测维护桥', 'route': [[19, 21, 16], [19, 22, 16]]}], 'brief': brief,
        'description': '纳米机器人装配阵列由三个并列洁净装配舱组成，每舱有独立机械臂和夹持台；中央转运脊在舱间搬运半成品，顶部观测桥用于维护与校准。', 'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}

if __name__ == '__main__': package(build(), OUT, 'i11', ['保留25×29×21占地下限', '三舱装配、中央转运与顶部维护分区'])
