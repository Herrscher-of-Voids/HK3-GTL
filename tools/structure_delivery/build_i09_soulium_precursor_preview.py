"""I09 soulium precursor blending vessel: ring reactor with metering galleries."""
from build_i03_centrifuge_preview import frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

OUT = ROOT / 'deliveries/I09_魂钢前驱体配制釜_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'
FLOOR = 'ad_astra:ostrum_plating'
RIB = 'gtlcore:lafium_mechanical_casing'
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
    brief = {'id': 'I09', 'title': '魂钢前驱体配制釜',
             'minimum_wdh': [31, 29, 27], 'catalog_minimum_wdh': [17, 21, 21]}
    # Deliberately wider than the catalog minimum: the process needs separated
    # metering, reaction, sampling, and residue paths.
    a = Build(brief)
    width, depth, height = 31, 29, 27
    a.box((0, 0, 0), (width - 1, 0, depth - 1), FLOOR)
    frame(a, 0, width - 1, 1, 0, depth - 1, 'gtlcore:space_elevator_mechanical_casing')

    # Central jacketed vessel: a narrow vertical reactor with separated
    # inspection decks rather than a filled rectangular shell.
    for y in range(2, 23):
        if y in (2, 7, 13, 19, 22):
            ring(a, 15, 14, 9, y, RIB, 2)
            ring(a, 15, 14, 6, y, 'gtceu:high_power_casing', 1)
        else:
            ring(a, 15, 14, 8, y, GLASS, 2)
            ring(a, 15, 14, 5, y, 'hk3gtl:glass_honkai_stabilized', 1)
    for x, z in ((7, 14), (23, 14), (15, 6), (15, 22)):
        a.box((x, 2, z), (x, 22, z), RIB)
        for y in (7, 13, 19):
            a.box((x - 1, y, z - 1), (x + 1, y + 1, z + 1), 'gtceu:advanced_computer_casing')
    # Four short outriggers make the inspection rings visibly structural.
    for x0, x1, z in ((6, 9, 14), (21, 24, 14)):
        a.box((x0, 7, z - 1), (x1, 7, z + 1), 'gtceu:assembly_line_grating')
        a.box((x0, 13, z - 1), (x1, 13, z + 1), 'gtceu:assembly_line_grating')

    # Mixing rotor and suspended precursor core.
    a.box((13, 4, 12), (17, 19, 16), 'gtceu:advanced_computer_casing')
    for y in range(7, 18):
        radius = max(1, 4 - abs(y - 12) // 3)
        for x in range(15 - radius, 16 + radius):
            for z in range(14 - radius, 15 + radius):
                if abs(x - 15) + abs(z - 14) <= radius:
                    a.set(x, y, z, 'hk3gtl:glass_honkai_stabilized' if (x + y + z) % 4 else GLASS)
    for y in (6, 12, 18):
        ring(a, 15, 14, 6, y, 'gtlcore:graviton_field_constraint_casing', 1)

    # West and east metering towers: open frames around three independent
    # feed levels and a return line, leaving the reactor readable from outside.
    for x0, x1, casing in ((2, 6, 'hk3gtl:voltage_machine_casing_hdv'),
                            (24, 28, 'hk3gtl:voltage_machine_casing_hcv')):
        a.box((x0, 1, 6), (x1, 1, 22), casing)
        for x in (x0, x1):
            a.box((x, 2, 6), (x, 22, 6), casing)
            a.box((x, 2, 22), (x, 22, 22), casing)
        for z in (8, 13, 18):
            a.box((x0, 3, z), (x1, 3, z + 2), 'gtceu:advanced_computer_casing', True)
            a.box((x0, 10, z), (x1, 10, z + 2), RIB)
            a.box((x0 + 1, 5, z + 1), (x1 - 1, 8, z + 1), GLASS)
            a.box((x1 if x0 < 10 else x0, 6, z + 1), (15 if x0 < 10 else 15, 6, z + 1), PIPE)
        for z in (6, 22):
            a.box((x0, 3, z), (x1, 22, z), RIB)
        a.box((x0, 11, 7), (x1, 11, 21), 'gtceu:assembly_line_grating')

    # Top charging header and bottom drain manifold make the flow legible.
    frame(a, 10, 20, 23, 9, 19, 'gtceu:high_power_casing')
    for x in (11, 15, 19):
        a.box((x, 22, 12), (x, 25, 12), PIPE)
        a.box((x, 22, 16), (x, 25, 16), PIPE)
    a.box((15, 22, 14), (15, 26, 14), PIPE)
    a.box((15, 19, 14), (15, 22, 14), PIPE)
    a.box((11, 22, 12), (19, 22, 16), PIPE)
    # Crown cap completes the intended 27-block height while remaining tied
    # to the central charging riser.
    a.box((14, 26, 13), (16, 26, 15), 'gtceu:high_power_casing')
    a.box((10, 3, 10), (20, 3, 18), 'gtceu:stainless_evaporation_casing')
    for x in (11, 15, 19):
        a.box((x, 1, 10), (x, 5, 10), PIPE)

    # Front sampling cabinet and operator console.
    a.box((8, 1, 2), (22, 2, 4), 'ad_astra:steel_panel')
    a.box((9, 3, 1), (14, 8, 4), 'gtceu:sterilizing_filter_casing', True)
    a.box((10, 5, 1), (13, 7, 1), GLASS)
    a.box((16, 3, 1), (21, 8, 4), 'gtceu:advanced_computer_casing', True)
    a.box((17, 5, 1), (20, 7, 1), 'gtlcore:super_computation_component[active=false]')
    controller = [19, 6, 2]
    a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')

    ports = [
        ('SOULIUM_FEED', [4, 5, 1], 'north', '魂钢前驱体输入'),
        ('CATALYST', [8, 5, 1], 'north', '催化剂输入'),
        ('POWER', [12, 5, 1], 'north', '供能'),
        ('MEDIUM', [16, 5, 1], 'north', '配制介质输入'),
        ('PRECURSOR', [20, 5, 1], 'north', '魂钢前驱体输出'),
        ('RESIDUE', [24, 5, 1], 'north', '残液输出'),
    ]
    # Low front service plinth ties every socket into the two side galleries.
    a.box((2, 1, 2), (28, 3, 3), 'gtceu:advanced_computer_casing')
    for _, (x, y, z), _, _ in ports:
        a.box((x - 1, 4, z + 1), (x + 1, 5, z + 2), 'gtceu:advanced_computer_casing')
        a.set(x, y - 1, z, 'gtceu:advanced_computer_casing')
    for _, pos, _, _ in ports:
        a.set(*pos, PORT)

    return {
        'key': 'i09', 'name': 'i09-soulium-precursor-free',
        'title': brief['title'], 'size': [width, height, depth], 'controller': controller,
        'ports': [{'id': key, 'pos': pos, 'face': face, 'purpose': purpose}
                  for key, pos, face, purpose in ports],
        'paths': [],
        'zones': [
            {'name': '环形配制釜', 'kind': 'reactor', 'min': [7, 1, 5], 'max': [23, 25, 23], 'pos': [15, 24, 14], 'role': '前驱体混合与约束', 'service_face': '四周'},
            {'name': '西侧计量廊', 'kind': 'feed', 'min': [2, 1, 6], 'max': [6, 22, 22], 'pos': [4, 22, 14], 'role': '原料计量', 'service_face': '西侧'},
            {'name': '东侧回流廊', 'kind': 'return', 'min': [24, 1, 6], 'max': [28, 22, 22], 'pos': [26, 22, 14], 'role': '介质回流与残液隔离', 'service_face': '东侧'},
            {'name': '取样与控制台', 'kind': 'sampling', 'min': [8, 1, 1], 'max': [22, 8, 4], 'pos': [15, 8, 2], 'role': '取样、控制和产物确认', 'service_face': '北侧'},
        ],
        'links': [
            {'from': '西侧计量廊', 'to': '环形配制釜', 'route': [[7, 6, 9], [10, 6, 9]]},
            {'from': '环形配制釜', 'to': '东侧回流廊', 'route': [[22, 6, 19], [24, 6, 19]]},
            {'from': '环形配制釜', 'to': '取样与控制台', 'route': [[15, 4, 7], [15, 4, 4]]},
        ],
        'brief': brief,
        'description': '中央环形夹套配制釜以悬置的魂钢前驱体核心为中心；西侧计量廊分三路供料，东侧回流廊隔离介质与残液，北侧取样柜负责产物确认。',
        'role_materials': {key: sorted(value) for key, value in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


if __name__ == '__main__':
    package(build(), OUT, 'i09', ['保留17×21×21占地下限', '前驱体、介质、供能、产物与残液接口分离'])
