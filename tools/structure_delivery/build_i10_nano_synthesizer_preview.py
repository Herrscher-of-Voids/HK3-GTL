"""I10 纳米基元合成器：分层微反应架与封闭合成脊。"""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I10_纳米基元合成器_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'
FLOOR = 'ad_astra:ostrum_plating'
FRAME = 'gtlcore:lafium_mechanical_casing'
SHELL = 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing'
GLASS = 'gtlcore:rhenium_reinforced_energy_glass'
PIPE = 'gtceu:titanium_pipe_casing'


def ring(a, cx, cz, radius, y, block, thickness=1):
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            d = abs((x - cx) ** 2 + (z - cz) ** 2 - radius ** 2)
            if d <= radius * thickness * 2 + 1:
                a.set(x, y, z, block)


def build():
    brief = {'id': 'I10', 'title': '纳米基元合成器',
             'minimum_wdh': [35, 31, 27], 'catalog_minimum_wdh': [21, 25, 21]}
    a = Build(brief)
    width, depth, height = 35, 31, 27
    a.box((0, 0, 0), (width - 1, 0, depth - 1), FLOOR)
    frame(a, 0, width - 1, 1, 0, depth - 1, 'gtlcore:space_elevator_mechanical_casing')

    # A precision nano-lattice chamber: a suspended crystal core, four
    # orthogonal feed arms, and three thin control rings. This composition is
    # derived from the machine name rather than the retired layout draft.
    # Hollow pressure frame: no solid cube around the nano core.
    for z in (8, 22):
        a.box((10, 2, z), (24, 22, z), SHELL)
    for x in (10, 24):
        a.box((x, 2, 8), (x, 22, 22), SHELL)
    for y in (5, 11, 17):
        ring(a, 17, 15, 9, y, FRAME, 2)
        ring(a, 17, 15, 6, y, 'gtceu:high_power_casing', 1)
    for y in range(6, 18):
        ring(a, 17, 15, 7, y, GLASS, 2)
    for x, z in ((8, 15), (26, 15), (17, 6), (17, 24)):
        a.box((x, 5, z), (x, 19, z), FRAME)
        for y in (5, 11, 17):
            a.box((x - 1, y, z - 1), (x + 1, y + 1, z + 1), 'gtceu:advanced_computer_casing')
    # Inner lattice and suspended synthesis nucleus.
    a.box((14, 6, 12), (20, 18, 18), 'gtceu:advanced_computer_casing')
    for y in range(8, 17):
        a.box((15, y, 13), (19, y, 17), 'hk3gtl:glass_honkai_stabilized')
        a.box((16, y, 14), (18, y, 16), GLASS)
    for axis in range(13, 22, 4):
        a.box((axis, 4, 15), (axis, 20, 15), PIPE)
        a.box((17, 4, axis - 4), (17, 20, axis - 4), PIPE)
    # Independent collection tower and clean output rail on the rear side.
    a.box((27, 2, 7), (31, 22, 23), SHELL)
    for y in (5, 11, 17):
        a.box((28, y, 9), (30, y + 2, 21), GLASS)
        a.box((25, y + 1, 15), (29, y + 1, 15), PIPE)
    a.box((27, 2, 7), (31, 2, 23), FRAME)
    a.box((27, 22, 7), (31, 22, 23), FRAME)

    # Wash column and stepped sieve bank at the east end.
    for z, radius in ((7, 3), (14, 4), (21, 3)):
        a.box((z, 3, 23), (z, 20, 24), PIPE)
        for y in range(3, 20):
            a.box((z - radius, y, 25), (z + radius, y, 25), FRAME)
        a.box((z - radius + 1, 5, 26), (z + radius - 1, 17, 28), GLASS)
        a.box((z - radius, 4, 25), (z + radius, 4, 29), 'gtceu:advanced_computer_casing')
    frame(a, 4, 24, 22, 6, 23, 'gtceu:high_power_casing')
    for x in (7, 12, 17, 22):
        a.box((x, 21, 14), (x, 25, 14), PIPE)
    a.box((7, 20, 14), (22, 20, 14), PIPE)
    a.box((17, 22, 14), (17, 26, 14), PIPE)
    a.box((16, 26, 13), (18, 26, 15), 'gtceu:high_power_casing')

    # Front operator porch and six interfaces.
    a.box((2, 1, 2), (30, 2, 3), 'ad_astra:steel_panel')
    a.box((3, 3, 2), (31, 3, 4), 'gtceu:advanced_computer_casing')
    a.box((4, 4, 2), (29, 7, 4), 'gtceu:sterilizing_filter_casing')
    a.box((15, 5, 2), (19, 7, 4), 'gtlcore:super_computation_component[active=false]')
    controller = [17, 6, 2]
    a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    ports = [
        ('PRECURSOR', [5, 5, 1], 'north', '前驱体输入'),
        ('CATALYST', [9, 5, 1], 'north', '催化剂输入'),
        ('POWER', [13, 5, 1], 'north', '供能'),
        ('WASH', [21, 5, 1], 'north', '洗涤介质输入'),
        ('PRODUCT', [25, 5, 1], 'north', '纳米基元输出'),
        ('RESIDUE', [29, 5, 1], 'north', '筛分残余输出'),
    ]
    a.box((2, 1, 2), (31, 3, 3), 'gtceu:advanced_computer_casing')
    for _, (x, y, z), _, _ in ports:
        a.box((x - 1, 4, z + 1), (x + 1, 5, z + 2), 'gtceu:advanced_computer_casing')
        a.set(x, y - 1, z, 'gtceu:advanced_computer_casing')
        a.set(x, y, z, PORT)

    return {
        'key': 'i10', 'name': 'i10-nano-synthesizer-free', 'title': brief['title'],
        'size': [width, height, depth], 'controller': controller,
        'ports': [{'id': k, 'pos': p, 'face': f, 'purpose': q} for k, p, f, q in ports],
        'paths': [], 'zones': [
            {'name': '三层微反应架', 'kind': 'reaction', 'min': [4, 3, 5], 'max': [25, 20, 23], 'pos': [15, 15, 14], 'role': '基元串联反应', 'service_face': '前侧'},
            {'name': '封闭合成脊', 'kind': 'synthesis', 'min': [26, 2, 5], 'max': [31, 22, 23], 'pos': [28, 12, 14], 'role': '合成与转移', 'service_face': '后侧'},
            {'name': '洗涤柱', 'kind': 'wash', 'min': [4, 3, 22], 'max': [31, 20, 29], 'pos': [18, 15, 25], 'role': '洗涤分离', 'service_face': '东侧'},
            {'name': '筛分与产物仓', 'kind': 'filter', 'min': [4, 21, 6], 'max': [24, 25, 23], 'pos': [14, 25, 14], 'role': '筛分、收集与记录', 'service_face': '前侧'},
        ],
        'links': [
            {'from': '三层微反应架', 'to': '封闭合成脊', 'route': [[25, 5, 14], [27, 5, 14]]},
            {'from': '封闭合成脊', 'to': '洗涤柱', 'route': [[31, 10, 14], [31, 10, 25]]},
        ], 'brief': brief,
        'description': '纳米基元合成器以三层独立微反应架为前场，工艺桥逐层汇入后方封闭合成脊，再进入洗涤柱和阶梯筛分组；前侧接口集中在低位操作台。',
        'role_materials': {k: sorted(v) for k, v in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


if __name__ == '__main__':
    package(build(), OUT, 'i10', ['保留21×25×21占地下限', '三层微反应、封闭合成、洗涤与筛分分区'])
