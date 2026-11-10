"""I13 崩坏抗性包覆阵列：横向连续包覆工业线预览。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I13_崩坏抗性包覆阵列_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'


def build():
    brief = {
        'id': 'I13',
        'title': '崩坏抗性包覆阵列',
        'minimum_wdh': [25, 37, 29],
        'catalog_minimum_wdh': [25, 37, 29],
        'form': '横向连续包覆工业线',
        'flow': '基板预处理、崩坏能喷涂、等离子浸润、固化检测与成品分流',
    }
    width, height, depth = 47, 33, 43
    a = Build(brief)
    a.w, a.h, a.d = width, height, depth
    a.cx, a.cz = width // 2, depth // 2

    floor = 'ad_astra:ostrum_plating'
    foundation = 'gtlcore:space_elevator_mechanical_casing'
    frame_mat = 'gtlcore:lafium_mechanical_casing'
    shell = 'hk3gtl:voltage_machine_casing_hdv'
    shell_alt = 'hk3gtl:voltage_machine_casing_hcv'
    process = 'gtceu:corrosion_proof_casing'
    clean = 'gtceu:clean_machine_casing'
    panel = 'gtceu:advanced_computer_casing'
    glass = 'gtlcore:rhenium_reinforced_energy_glass'
    glass_alt = 'hk3gtl:glass_honkai_stabilized'
    rail = 'gtceu:assembly_line_grating'
    gear = 'gtceu:tungstensteel_gearbox'
    pipe = 'gtceu:tungstensteel_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    arm = 'gtlcore:manipulator'
    field = 'gtlcore:graviton_field_constraint_casing'
    injection = 'gtlcore:dimension_injection_casing'
    compute = 'gtlcore:super_computation_component[active=false]'
    precision = 'gtlcore:multi_functional_casing'

    # A complete foundation makes the machine read as one plant and anchors every bay.
    a.box((0, 0, 0), (width - 1, 0, depth - 1), floor)
    frame(a, 0, width - 1, 1, 0, depth - 1, foundation)
    a.box((2, 1, 6), (44, 2, 36), panel)
    a.box((3, 3, 9), (43, 4, 33), clean)

    # The main coating line: guarded conveyor, three spray/immersion bays, and a return rail.
    a.box((4, 3, 17), (42, 5, 25), rail)
    a.box((4, 3, 15), (42, 4, 15), shell)
    a.box((4, 3, 27), (42, 4, 27), shell_alt)
    for x in range(7, 43, 5):
        a.box((x, 4, 18), (x + 1, 4, 24), gear)
    for z in (15, 27):
        for x in range(6, 43, 6):
            a.box((x, 5, z), (x, 13, z), frame_mat)

    bays = [
        (10, process, glass),
        (23, shell_alt, glass_alt),
        (36, field, glass),
    ]
    for x, outer, inner in bays:
        # A framed hood exposes the luminous work zone without becoming a hollow shell.
        a.box((x - 4, 6, 12), (x + 4, 19, 12), outer)
        a.box((x - 4, 6, 30), (x + 4, 19, 30), outer)
        a.box((x - 4, 6, 12), (x - 4, 19, 30), outer)
        a.box((x + 4, 6, 12), (x + 4, 19, 30), outer)
        a.box((x - 3, 8, 13), (x + 3, 16, 13), inner)
        a.box((x - 3, 8, 29), (x + 3, 16, 29), inner)
        a.box((x - 2, 9, 17), (x + 2, 15, 25), glass_alt if inner != glass_alt else glass, True)
        a.box((x, 8, 18), (x, 17, 24), arm)
        a.box((x - 5, 11, 16), (x - 4, 15, 26), pipe)
        a.box((x + 4, 11, 16), (x + 5, 15, 26), pipe)
        for y in (7, 12, 17):
            a.box((x - 4, y, 14), (x + 4, y, 28), frame_mat)

    # The transfer corridor keeps all three bays tied to one visible industrial route.
    a.box((8, 20, 17), (39, 21, 25), rail)
    a.box((8, 22, 16), (39, 22, 16), pipe)
    a.box((8, 22, 26), (39, 22, 26), pipe)
    a.box((8, 21, 16), (39, 22, 17), pipe)
    a.box((8, 21, 25), (39, 22, 26), pipe)
    for x in (10, 23, 36):
        a.box((x, 20, 18), (x, 23, 24), injection)
        a.box((x - 2, 23, 19), (x + 2, 23, 23), arm)

    # Left pretreatment gallery: feed hoppers, wash manifold, and replaceable substrate racks.
    a.box((3, 6, 6), (12, 18, 10), process, True)
    a.box((4, 8, 7), (11, 15, 9), glass, True)
    a.box((4, 6, 5), (11, 7, 5), panel)
    for x in (5, 8, 11):
        a.box((x, 9, 5), (x, 17, 5), pipe)
        a.box((x, 17, 5), (x, 17, 10), gear)
    a.box((3, 19, 6), (12, 20, 10), rail)

    # Right solidification and metrology tower separates usable product from reject flow.
    a.box((37, 6, 31), (43, 22, 36), shell_alt, True)
    a.box((38, 8, 32), (42, 18, 35), glass, True)
    a.box((39, 9, 33), (41, 17, 34), precision)
    a.box((40, 8, 32), (40, 20, 35), vent)
    a.box((36, 20, 31), (44, 21, 36), rail)
    a.box((39, 22, 32), (41, 27, 35), compute)
    a.box((40, 23, 32), (40, 26, 35), glass_alt)

    # Upper maintenance bridge, cable tray, and suspended inspection head.
    a.box((5, 27, 10), (41, 27, 32), rail, True)
    a.box((5, 29, 10), (41, 29, 11), frame_mat)
    a.box((5, 29, 31), (41, 29, 32), frame_mat)
    for x in (7, 16, 25, 34, 40):
        a.box((x, 27, 11), (x, 30, 31), foundation)
    a.box((20, 30, 17), (26, 31, 25), panel)
    a.box((22, 31, 19), (24, 32, 23), glass)
    a.box((23, 30, 21), (23, 32, 21), arm)
    for z in range(13, 31, 4):
        a.box((12, 28, z), (36, 28, z), vent)

    # Grounded service columns make each elevated hood, tower, and bridge a
    # physically connected part of the same multiblock instead of a floating
    # decorative island in the exported voxel graph.
    for x in (6, 14, 19, 27, 32, 40):
        for z in (12, 30):
            a.box((x, 1, z), (x, 6, z), foundation)
    for x in (3, 12):
        for z in (6, 10):
            a.box((x, 1, z), (x, 6, z), foundation)
    for x in (37, 43):
        for z in (31, 36):
            a.box((x, 1, z), (x, 6, z), foundation)
    for x in (5, 16, 25, 34, 40):
        for z in (10, 32):
            a.box((x, 1, z), (x, 27, z), foundation)

    # Front operator apron. The controller and six unified ports all face the open forecourt.
    a.box((5, 1, 1), (41, 3, 4), panel)
    a.box((12, 4, 1), (17, 7, 4), shell_alt, True)
    a.box((29, 4, 1), (34, 7, 4), precision, True)
    controller = [23, 6, 2]
    a.box((23, 3, 2), (23, 5, 2), panel)
    a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [
        ('SUBSTRATE', [8, 5, 1], '基板与载体输入'),
        ('COATING', [13, 5, 1], '包覆介质输入'),
        ('POWER', [18, 5, 1], '供能'),
        ('PLASMA', [28, 5, 1], '等离子/能量输入'),
        ('PRODUCT', [33, 5, 1], '合格成品输出'),
        ('REJECT', [38, 5, 1], '不合格件与残液输出'),
    ]
    for _, pos, _ in ports:
        x, y, z = pos
        a.box((x, 3, z), (x, 4, z + 1), panel)
        a.set(x, 5, z + 1, panel)
        a.set(*pos, PORT)

    zones = [
        {'name': '基板预处理与上料廊', 'kind': 'pretreatment', 'min': [3, 3, 5], 'max': [12, 20, 10], 'pos': [8, 20, 8], 'role': '基板清洗、预热与上料', 'service_face': '前侧'},
        {'name': '三段连续包覆工位', 'kind': 'coating_bays', 'min': [6, 6, 12], 'max': [40, 23, 30], 'pos': [23, 23, 21], 'role': '喷涂、浸润与能量包覆', 'service_face': '前后两侧'},
        {'name': '转运与回流主线', 'kind': 'transfer_corridor', 'min': [8, 20, 16], 'max': [39, 23, 26], 'pos': [23, 23, 21], 'role': '载体连续转运与介质回流', 'service_face': '上下两侧'},
        {'name': '固化检测与分流塔', 'kind': 'curing_metrology', 'min': [36, 6, 31], 'max': [44, 27, 36], 'pos': [40, 27, 34], 'role': '固化、厚度检测与成品分流', 'service_face': '东侧'},
        {'name': '高位维护吊轨', 'kind': 'maintenance_bridge', 'min': [5, 27, 10], 'max': [41, 32, 32], 'pos': [23, 32, 21], 'role': '喷头更换、管线维护与吊运', 'service_face': '顶部'},
    ]
    links = [
        {'from': '基板预处理与上料廊', 'to': '三段连续包覆工位', 'route': [[12, 12, 8], [10, 12, 17]]},
        {'from': '三段连续包覆工位', 'to': '转运与回流主线', 'route': [[23, 19, 21], [23, 20, 21]]},
        {'from': '转运与回流主线', 'to': '固化检测与分流塔', 'route': [[39, 21, 21], [40, 22, 32]]},
        {'from': '三段连续包覆工位', 'to': '高位维护吊轨', 'route': [[23, 23, 21], [23, 27, 21]]},
    ]
    return {
        'key': 'i13', 'name': 'i13-coating-array-free', 'title': brief['title'],
        'size': [width, height, depth], 'controller': controller,
        'ports': [{'id': k, 'pos': p, 'face': 'north', 'purpose': q} for k, p, q in ports],
        'paths': [], 'zones': zones, 'links': links, 'brief': brief,
        'description': '崩坏抗性包覆阵列是一条横向连续工业线：左端完成基板清洗与预处理，中部三段包覆工位依次进行喷涂、浸润和能量约束，右端固化检测塔分流合格品与残液；顶部维护吊轨负责喷头、管线和检修吊运，前侧集中控制与六个工业接口。',
        'role_materials': {k: sorted(v) for k, v in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


if __name__ == '__main__':
    package(build(), OUT, 'i07', ['横向连续包覆线、三段工位、固化检测塔与高位维护吊轨', '端口前方保持开放净空'])
