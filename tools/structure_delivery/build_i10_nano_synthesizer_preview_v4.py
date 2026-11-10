"""I10 纳米基元合成器：垂直纳米反应井与分层约束环。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I10_纳米基元合成器_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'


def build():
    brief = {'id': 'I10', 'title': '纳米基元合成器', 'minimum_wdh': [21, 25, 21], 'catalog_minimum_wdh': [21, 25, 21],
             'form': '垂直纳米反应井', 'flow': '前驱体洁净进料、分层纳米压合、侧舱分级收集'}
    width, height, depth = 37, 35, 37
    a = Build(brief); a.w, a.h, a.d = width, height, depth; a.cx, a.cz = 18, 18
    floor = 'ad_astra:ostrum_plating'; shell = 'hk3gtl:voltage_machine_casing_hdv'
    shell_hi = 'hk3gtl:voltage_machine_casing_hcv'; heavy = 'gtceu:high_power_casing'
    glass = 'gtlcore:rhenium_reinforced_energy_glass'; rail = 'gtceu:assembly_line_grating'
    core = 'gtlcore:advanced_stellar_containment_casing'; crystal = 'hk3gtl:glass_honkai_stabilized'
    pipe = 'gtceu:tungstensteel_pipe_casing'; manip = 'gtlcore:manipulator'
    a.box((0, 0, 0), (36, 0, 36), floor); frame(a, 0, 36, 1, 0, 36, 'gtlcore:space_elevator_mechanical_casing')

    # Four separated legs support the vertical reactor and leave sight lines through the machine.
    for x, z in ((3, 3), (31, 3), (3, 31), (31, 31)):
        a.box((x, 1, z), (x + 2, 28, z + 2), shell)
        a.box((x - 1, 1, z - 1), (x + 3, 2, z + 3), heavy)
        for y in (8, 16, 24): a.box((x - 1, y, z - 1), (x + 3, y + 1, z + 3), pipe)

    # Central reaction well: glass walls, open viewing gaps, and a luminous suspended lattice.
    a.box((11, 2, 11), (25, 31, 25), shell_hi, True)
    a.box((13, 3, 13), (23, 30, 23), glass, True)
    a.box((15, 4, 15), (21, 29, 21), crystal, True)
    a.box((18, 4, 18), (18, 30, 18), core)
    for y in (7, 14, 21, 28):
        # Concentric rings are deliberately broken on the front to keep the chamber readable.
        for x in range(13, 24):
            for z in (13, 23):
                if not (z == 13 and x in (13, 14, 22, 23)): a.set(x, y, z, rail)
        for z in range(14, 23):
            for x in (13, 23):
                if not (x == 13 and z < 17): a.set(x, y, z, rail)
        a.box((16, y, 16), (20, y, 20), crystal, True)
        a.set(18, y, 15, core); a.set(18, y, 21, core)

    # Side洁净舱s are different heights and attach to the well instead of forming another full box.
    for x0, z0, x1, z1, mat in ((4, 10, 10, 26, shell), (26, 10, 32, 26, shell_hi),
                                 (10, 4, 26, 10, heavy), (10, 26, 26, 32, heavy)):
        a.box((x0, 4, z0), (x1, 18, z1), mat, True)
        a.box((x0 + 1, 7, z0 + 1), (x1 - 1, 15, z1 - 1), glass, True)
    for x, z in ((7, 18), (29, 18), (18, 7), (18, 29)):
        a.box((x - 1, 6, z - 1), (x + 1, 23, z + 1), manip)
        a.set(x, 15, z, core)

    # Top crown and three offset maintenance bridges give the structure a vertical silhouette.
    a.box((8, 30, 8), (28, 32, 28), rail, True)
    a.box((13, 33, 13), (23, 34, 23), heavy, True)
    a.box((16, 34, 16), (20, 34, 20), crystal, True)
    for x0, z0, x1, z1 in ((5, 17, 12, 19), (24, 17, 31, 19), (17, 5, 19, 12)):
        a.box((x0, 24, z0), (x1, 25, z1), rail)
        a.box((x0, 25, z0), (x0, 29, z0), pipe)

    # Front interface plinth: all interfaces use the approved industrial port casing.
    a.box((5, 1, 1), (31, 3, 5), 'gtceu:advanced_computer_casing')
    controller = [18, 6, 2]; a.box((17, 3, 2), (19, 5, 5), heavy); a.set(*controller, PORT)
    ports = [('PRECURSOR', [7, 5, 1], '前驱体输入'), ('CATALYST', [12, 5, 1], '催化剂输入'),
             ('POWER', [17, 5, 1], '供能'), ('WASH', [22, 5, 1], '洗涤介质输入'),
             ('PRODUCT', [27, 5, 1], '纳米基元输出')]
    for _, pos, _ in ports:
        x, y, z = pos
        a.box((x, 3, z), (x, 4, z + 1), heavy)
        a.set(x, y, z + 1, heavy)
        a.set(*pos, PORT)
    return {'key': 'i10', 'name': 'i10-nano-synthesizer-free', 'title': brief['title'],
            'size': [width, height, depth], 'controller': controller,
            'ports': [{'id': k, 'pos': p, 'face': 'north', 'purpose': q} for k, p, q in ports], 'paths': [],
            'zones': [{'name': '中央纳米反应井', 'kind': 'reaction_well', 'min': [11, 2, 11], 'max': [25, 34, 25], 'pos': [18, 18, 18], 'role': '分层纳米压合与合成', 'service_face': '四周'},
                      {'name': '侧向洁净进料舱', 'kind': 'feed_cleanroom', 'min': [4, 4, 10], 'max': [32, 18, 26], 'pos': [18, 12, 18], 'role': '前驱体、催化剂和洗涤介质预处理', 'service_face': '四侧'},
                      {'name': '顶部维护冠层', 'kind': 'maintenance_crown', 'min': [8, 24, 8], 'max': [28, 34, 28], 'pos': [18, 30, 18], 'role': '转运、校准和洁净维护', 'service_face': '顶部'}],
            'links': [{'from': '侧向洁净进料舱', 'to': '中央纳米反应井', 'route': [[10, 12, 18], [13, 12, 18]]},
                      {'from': '中央纳米反应井', 'to': '顶部维护冠层', 'route': [[18, 28, 18], [18, 31, 18]]}],
            'brief': brief, 'description': '垂直纳米反应井由四角承重腿、中央分层约束环、侧向洁净舱和顶部维护冠层组成；前侧低位端口负责进料、供能与成品输出。',
            'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}


if __name__ == '__main__': package(build(), OUT, 'i10', ['垂直反应井、分层约束环、侧向洁净舱与顶部维护冠层', '保留21×25×21占地下限', '接口统一使用industrial_port_casing'])
