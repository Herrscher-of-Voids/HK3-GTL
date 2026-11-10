"""I10 纳米基元合成器：悬置纳米晶格与分层合成环。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I10_纳米基元合成器_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'
FLOOR = 'ad_astra:ostrum_plating'
GLASS = 'gtlcore:rhenium_reinforced_energy_glass'

def build():
    brief = {'id': 'I10', 'title': '纳米基元合成器', 'minimum_wdh': [21, 25, 21], 'catalog_minimum_wdh': [21, 25, 21]}
    width, depth, height = 37, 35, 31
    a = Build(brief); a.w, a.d, a.h, a.cx, a.cz = width, depth, height, 18, 17
    a.box((0, 0, 0), (36, 0, 34), FLOOR); frame(a, 0, 36, 1, 0, 34, 'gtlcore:space_elevator_mechanical_casing')
    # Four tall nano-fabrication pylons, each using a different voltage casing.
    for x, z, mat in ((4, 4, 'hk3gtl:voltage_machine_casing_hdv'), (32, 4, 'hk3gtl:voltage_machine_casing_hcv'), (4, 30, 'hk3gtl:voltage_machine_casing_hbv'), (32, 30, 'hk3gtl:voltage_machine_casing_hrv')):
        a.box((x, 1, z), (x + 2, 24, z + 2), mat)
        for y, m in ((6, 'gtceu:assembly_line_grating'), (13, 'gtceu:advanced_computer_casing'), (20, 'gtlcore:lafium_mechanical_casing')):
            a.box((x - 1, y, z), (x + 3, y, z + 2), m)
    # Three nested square synthesis rings, intentionally open at the sides.
    for y, r, mat in ((6, 12, 'gtlcore:dimension_connection_casing'), (12, 10, 'gtceu:high_power_casing'), (18, 12, 'gtlcore:graviton_field_constraint_casing')):
        a.box((18 - r, y, 17 - r), (18 + r, y, 17 + r), mat, True)
        a.box((18 - r + 2, y, 17 - r + 2), (18 + r - 2, y, 17 + r - 2), GLASS, True)
    # Central nano-lattice: diamond layers around a vertical precision spine.
    for y in range(8, 18):
        r = 1 + min(y - 8, 17 - y) // 2
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if abs(dx) + abs(dz) <= r:
                    a.set(18 + dx, y, 17 + dz, 'hk3gtl:glass_honkai_stabilized' if (dx + dz + y) % 2 else 'kubejs:starmetal_coil_block[active=false]')
    a.line((18, 4, 17), (18, 22, 17), 'gtlcore:advanced_stellar_containment_casing')
    # Four micro-manipulator rails connect the rings to metering heads.
    for start, end, mat in [((6, 9, 17), (15, 9, 17), 'gtceu:titanium_pipe_casing'), ((30, 13, 17), (21, 13, 17), 'gtceu:tungstensteel_pipe_casing'), ((18, 9, 6), (18, 9, 14), 'gtlcore:dimension_injection_casing'), ((18, 15, 28), (18, 15, 20), 'gtlcore:dimension_connection_casing')]:
        a.line(start, end, mat); a.box((end[0] - 1, end[1] - 1, end[2] - 1), (end[0] + 1, end[1] + 1, end[2] + 1), 'gtlcore:manipulator')
    for start, end in [((6, 6, 17), (6, 9, 17)), ((30, 6, 17), (30, 13, 17)), ((18, 6, 6), (18, 9, 6)), ((18, 6, 28), (18, 15, 28))]: a.line(start, end, 'gtlcore:lafium_mechanical_casing')
    # Rear collection spine and a suspended sieve crown.
    a.box((28, 3, 10), (34, 23, 24), 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing', True)
    for y in (6, 12, 18):
        a.box((29, y, 12), (33, y + 2, 22), GLASS); a.line((27, y + 1, 17), (30, y + 1, 17), 'gtceu:tungstensteel_pipe_casing')
    a.box((12, 23, 11), (24, 23, 23), 'gtceu:assembly_line_grating')
    for x, z in ((12, 11), (24, 11), (12, 23), (24, 23)): a.line((x, 23, z), (18, 29, 17), 'gtlcore:lafium_mechanical_casing')
    a.box((17, 29, 16), (19, 30, 18), 'gtceu:high_power_casing')
    # Front low operation porch and six interfaces.
    a.box((5, 1, 1), (31, 3, 4), 'gtceu:advanced_computer_casing')
    a.box((9, 4, 1), (14, 7, 4), 'gtceu:sterilizing_filter_casing', True); a.box((22, 4, 1), (27, 7, 4), 'gtlcore:super_computation_component[active=false]', True)
    controller = [24, 6, 2]; a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [('PRECURSOR', [6, 5, 1], 'north', '前驱体输入'), ('CATALYST', [10, 5, 1], 'north', '催化剂输入'), ('POWER', [14, 5, 1], 'north', '供能'), ('WASH', [18, 5, 1], 'north', '洗涤介质输入'), ('PRODUCT', [22, 5, 1], 'north', '纳米基元输出'), ('RESIDUE', [26, 5, 1], 'north', '筛分残余输出')]
    for _, pos, _, _ in ports:
        a.box((pos[0], 3, pos[2]), (pos[0], 4, pos[2] + 1), 'gtceu:advanced_computer_casing'); a.set(pos[0], 5, pos[2] + 1, 'gtceu:advanced_computer_casing'); a.set(*pos, PORT)
    return {'key': 'i10', 'name': 'i10-nano-synthesizer-free', 'title': brief['title'], 'size': [width, height, depth], 'controller': controller,
        'ports': [{'id': k, 'pos': p, 'face': f, 'purpose': q} for k, p, f, q in ports], 'paths': [], 'zones': [
        {'name': '三层纳米合成环', 'kind': 'reaction', 'min': [6, 6, 5], 'max': [30, 18, 29], 'pos': [18, 12, 17], 'role': '基元分层反应', 'service_face': '四周'},
        {'name': '中央纳米晶格', 'kind': 'synthesis', 'min': [14, 4, 13], 'max': [22, 22, 21], 'pos': [18, 14, 17], 'role': '纳米基元合成', 'service_face': '四周'},
        {'name': '后侧收集脊', 'kind': 'collection', 'min': [28, 3, 10], 'max': [34, 23, 24], 'pos': [31, 13, 17], 'role': '产物收集与残余分离', 'service_face': '后侧'},
        {'name': '顶部筛分冠架', 'kind': 'filter', 'min': [12, 23, 11], 'max': [24, 30, 23], 'pos': [18, 27, 17], 'role': '洗涤、筛分与记录', 'service_face': '顶部'}],
        'links': [{'from': '三层纳米合成环', 'to': '中央纳米晶格', 'route': [[6, 9, 17], [15, 9, 17]]}, {'from': '中央纳米晶格', 'to': '后侧收集脊', 'route': [[21, 13, 17], [30, 13, 17]]}, {'from': '中央纳米晶格', 'to': '顶部筛分冠架', 'route': [[18, 18, 17], [18, 27, 17]]}], 'brief': brief,
        'description': '纳米基元合成器以中央悬置纳米晶格为核心，三层独立合成环提供微尺度反应，四向操纵臂搬运基元，后侧收集脊分离产物，顶部冠架负责洗涤筛分。', 'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}

if __name__ == '__main__': package(build(), OUT, 'i10', ['保留21×25×21占地下限', '纳米晶格、分层合成、收集与筛分分区'])
