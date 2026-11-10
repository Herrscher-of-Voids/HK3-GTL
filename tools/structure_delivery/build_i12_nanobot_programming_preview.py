"""I12 纳米自组织编程舱：连续数据脊、编程舱阵列与自组织核心。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I12_纳米自组织编程舱_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'


def build():
    brief = {'id': 'I12', 'title': '纳米自组织编程舱',
             'minimum_wdh': [21, 25, 25], 'catalog_minimum_wdh': [21, 25, 25]}
    width, height, depth = 43, 35, 35
    a = Build(brief)
    a.w, a.h, a.d = width, height, depth
    a.cx, a.cz = width // 2, depth // 2

    floor = 'ad_astra:ostrum_plating'
    frame_mat = 'gtlcore:space_elevator_mechanical_casing'
    spine = 'gtceu:advanced_computer_casing'
    spine_accent = 'gtlcore:dimension_connection_casing'
    shell_a = 'hk3gtl:voltage_machine_casing_hdv'
    shell_b = 'hk3gtl:voltage_machine_casing_hcv'
    shell_c = 'hk3gtl:voltage_machine_casing_hbv'
    glass = 'gtlcore:rhenium_reinforced_energy_glass'
    arm = 'gtlcore:manipulator'
    core = 'gtlcore:stellar_containment_casing'
    rail = 'gtceu:assembly_line_grating'
    gearbox = 'gtceu:tungstensteel_gearbox'
    panel = 'gtlcore:lafium_mechanical_casing'

    # Full foundation and a raised perimeter make the silhouette read as one machine.
    a.box((0, 0, 0), (width - 1, 0, depth - 1), floor)
    frame(a, 0, width - 1, 1, 0, depth - 1, frame_mat)
    a.box((2, 1, 7), (40, 2, 27), panel)
    a.box((4, 3, 15), (38, 4, 19), spine)
    a.box((4, 5, 15), (38, 6, 19), rail)
    a.box((4, 7, 16), (38, 8, 18), spine_accent)
    for x in range(6, 39, 4):
        a.box((x, 5, 16), (x + 1, 5, 18), gearbox)

    # Four programmable pods face the shared data spine, alternating voltage shells.
    pod_spec = [(6, shell_a), (15, shell_b), (24, shell_c), (33, shell_a)]
    for x, shell in pod_spec:
        # Grounded ribs connect each pod's rear edge to the raised service spine.
        a.box((x - 3, 2, 14), (x - 3, 9, 14), frame_mat)
        a.box((x + 3, 2, 14), (x + 3, 9, 14), frame_mat)
        a.box((x - 3, 2, 20), (x - 3, 9, 20), frame_mat)
        a.box((x + 3, 2, 20), (x + 3, 9, 20), frame_mat)
        a.box((x - 3, 9, 10), (x + 3, 20, 14), shell, True)
        a.box((x - 2, 10, 11), (x + 2, 18, 13), glass, True)
        a.box((x - 1, 12, 13), (x + 1, 16, 13), core)
        a.box((x, 10, 14), (x, 18, 16), arm)
        a.box((x - 2, 19, 11), (x + 2, 19, 13), rail)
        a.box((x - 1, 8, 11), (x + 1, 8, 14), spine_accent)
        a.box((x, 7, 14), (x, 9, 14), arm)

        a.box((x - 3, 9, 20), (x + 3, 20, 24), shell, True)
        a.box((x - 2, 10, 21), (x + 2, 18, 23), glass, True)
        a.box((x - 1, 12, 21), (x + 1, 16, 21), core)
        a.box((x, 10, 19), (x, 18, 21), arm)
        a.box((x - 2, 19, 21), (x + 2, 19, 23), rail)
        a.box((x - 1, 8, 20), (x + 1, 8, 23), spine_accent)
        a.box((x, 7, 20), (x, 9, 20), arm)

    # Central transparent chamber is the visual and functional heart of the array.
    a.box((17, 9, 14), (25, 24, 20), shell_c, True)
    a.box((18, 10, 15), (24, 22, 19), glass, True)
    a.box((20, 11, 17), (22, 21, 17), core)
    a.box((21, 12, 16), (21, 20, 18), arm)
    a.box((19, 23, 16), (23, 23, 18), rail)
    a.box((19, 8, 16), (23, 8, 18), spine_accent)

    # Open data halo: four-sided maintenance ring, supported down to the floor.
    a.box((10, 27, 8), (32, 27, 9), spine_accent)
    a.box((10, 27, 25), (32, 27, 26), spine_accent)
    a.box((10, 27, 9), (11, 27, 25), spine_accent)
    a.box((31, 27, 9), (32, 27, 25), spine_accent)
    a.box((12, 28, 10), (30, 28, 11), rail)
    a.box((12, 28, 23), (30, 28, 24), rail)
    a.box((12, 28, 11), (13, 28, 23), rail)
    a.box((29, 28, 11), (30, 28, 23), rail)
    a.box((13, 28, 17), (29, 28, 17), rail)
    for x, z in ((12, 10), (30, 10), (12, 24), (30, 24)):
        a.box((x, 27, z), (x, 28, z), spine_accent)
    for x, z in ((10, 8), (32, 8), (10, 26), (32, 26)):
        a.box((x, 2, z), (x, 27, z), frame_mat)
    for x in (14, 21, 28):
        a.box((x, 27, 8), (x, 30, 8), panel)
        a.box((x, 27, 26), (x, 30, 26), panel)
    a.box((20, 29, 15), (22, 32, 19), glass, True)
    a.box((21, 30, 16), (21, 33, 18), core)

    # Front control gallery and six unified industrial interfaces.
    a.box((5, 1, 1), (37, 3, 4), spine)
    a.box((12, 4, 1), (17, 7, 4), shell_b, True)
    a.box((25, 4, 1), (30, 7, 4), shell_c, True)
    controller = [21, 6, 2]
    a.box((21, 3, 2), (21, 5, 2), spine)
    a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [
        ('SAMPLE', [7, 5, 1], '纳米样本输入'),
        ('PROGRAM', [12, 5, 1], '程序模板输入'),
        ('POWER', [17, 5, 1], '供能'),
        ('DATA', [25, 5, 1], '编程数据输入'),
        ('NANITE', [30, 5, 1], '纳米单元输出'),
        ('REJECT', [35, 5, 1], '失配单元输出'),
    ]
    for _, pos, _ in ports:
        x, y, z = pos
        a.box((x, 3, z), (x, 4, z + 1), spine)
        a.set(x, 5, z + 1, spine)
        a.set(*pos, PORT)

    zones = [
        {'name': '连续数据供能主脊', 'kind': 'data_spine', 'min': [4, 3, 15], 'max': [38, 8, 19], 'pos': [21, 8, 17], 'role': '程序与能量分发', 'service_face': '前侧'},
        {'name': '四组纳米编程舱', 'kind': 'programming_pods', 'min': [3, 8, 10], 'max': [36, 20, 24], 'pos': [21, 20, 17], 'role': '单元编程与校准', 'service_face': '主脊侧'},
        {'name': '中央自组织核心室', 'kind': 'self_organization_core', 'min': [17, 8, 14], 'max': [25, 24, 20], 'pos': [21, 24, 17], 'role': '纳米群自组织', 'service_face': '前侧'},
        {'name': '高位数据维护环', 'kind': 'maintenance_halo', 'min': [10, 27, 8], 'max': [32, 33, 26], 'pos': [21, 33, 17], 'role': '程序回写与检修', 'service_face': '四周'},
    ]
    links = [
        {'from': '连续数据供能主脊', 'to': '四组纳米编程舱', 'route': [[21, 8, 17], [21, 12, 17]]},
        {'from': '四组纳米编程舱', 'to': '中央自组织核心室', 'route': [[21, 18, 17], [21, 22, 17]]},
        {'from': '中央自组织核心室', 'to': '高位数据维护环', 'route': [[21, 24, 17], [21, 29, 17]]},
    ]
    return {'key': 'i12', 'name': 'i12-nanobot-programming-free', 'title': brief['title'],
            'size': [width, height, depth], 'controller': controller,
            'ports': [{'id': key, 'pos': pos, 'face': 'north', 'purpose': purpose} for key, pos, purpose in ports],
            'paths': [], 'zones': zones, 'links': links, 'brief': brief,
            'description': '纳米自组织编程舱采用连续数据供能主脊串联四组编程舱，中央透明核心室完成纳米群自组织，高位开放数据环承担程序回写与维护；前侧集中控制与六个工业接口。',
            'role_materials': {k: sorted(v) for k, v in a.roles.items()},
            'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}


if __name__ == '__main__':
    package(build(), OUT, 'i12', ['连续数据主脊、四组编程舱、中央自组织核心与高位维护环'])
