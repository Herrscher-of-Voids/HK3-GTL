"""I08 imitation-core crystallization chamber with offset heat extraction."""
from build_i03_centrifuge_preview import circle, frame
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT


OUT = ROOT / 'deliveries/I08_仿制核心结晶反应室_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'
RIB = 'gtlcore:lafium_mechanical_casing'
COOL = 'gtlcore:cold_ice_casing'
PIPE = 'gtceu:ptfe_pipe_casing'


def build():
    brief = {'id': 'I08', 'title': '仿制核心结晶反应室',
             'minimum_wdh': [57, 57, 43]}
    a = Build(brief)
    a.box((0, 0, 0), (56, 0, 56), 'ad_astra:ostrum_plating')
    frame(a, 0, 56, 1, 0, 56, 'gtlcore:space_elevator_mechanical_casing')

    # Core plinth carries nested constraint shells; broad glazed sectors keep
    # the centered crystal visible from the operator side.
    a.box((14, 1, 16), (42, 2, 44), 'gtceu:high_power_casing')
    for y in range(3, 38):
        outer = RIB if y in (3, 37) or y % 7 == 0 else 'gtlcore:hsss_reinforced_borosilicate_glass'
        circle(a, 28, 30, 13, y, outer, 2)
        if y < 34:
            inner = ('gtlcore:graviton_field_constraint_casing' if y % 6 == 0
                     else 'gtlcore:rhenium_reinforced_energy_glass')
            circle(a, 28, 30, 8, y, inner, 1)
    for x, z in ((15, 30), (41, 30), (28, 17), (28, 43)):
        a.box((x, 3, z), (x, 39, z),
              'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing')
        for y in (9, 16, 23, 30, 37):
            a.box((x - 1, y, z - 1), (x + 1, y + 1, z + 1), RIB)
    for y in (11, 25, 36):
        circle(a, 28, 30, 15, y, 'gtceu:assembly_line_grating', 2)
        for x, z in ((13, 30), (43, 30), (28, 15), (28, 45)):
            a.box((x, y - 2, z), (x, y, z), RIB)
    for step in range(5):
        radius = 13 - step * 2
        circle(a, 28, 30, radius, 38 + step,
               'gtlcore:advanced_stellar_containment_casing' if step % 2
               else 'gtceu:corrosion_proof_casing', 2)
        if step:
            a.box((28 + radius, 37 + step, 30),
                  (28 + radius + 2, 37 + step, 30), RIB)

    # Central faceted core hangs inside an independent locator, not on the
    # outer cladding. Its pointed ends are built from descending cross-sections.
    a.box((26, 3, 28), (30, 12, 32),
          'gtlcore:multi_functional_casing')
    for y in range(13, 35):
        radius = max(0, 6 - abs(y - 24) // 2)
        for x in range(28 - radius, 29 + radius):
            for z in range(30 - radius, 31 + radius):
                if abs(x - 28) + abs(z - 30) <= radius:
                    a.set(x, y, z, 'gtlcore:rhenium_reinforced_energy_glass'
                          if (x + z + y) % 5 else 'hk3gtl:glass_honkai_stabilized')
    for x, z in ((23, 30), (33, 30), (28, 25), (28, 35)):
        a.box((x, 6, z), (x, 29, z),
              'gtlcore:graviton_field_constraint_casing')
    for y in (13, 24, 33):
        frame(a, 22, 34, y, 24, 36, 'gtlcore:dimension_connection_casing')
        a.box((22, y, 30), (28, y, 30),
              'gtlcore:graviton_field_constraint_casing')

    # West feed laboratory: staged reagent bins, metering manifold and one
    # high line entering the chamber. The roof is deliberately lower.
    a.box((2, 1, 19), (12, 2, 42), 'ad_astra:steel_panel')
    for z in (20, 30, 40):
        a.box((3, 3, z), (10, 11, z + 5),
              'gtceu:advanced_computer_casing', True)
        a.box((4, 4, z + 1), (9, 9, z + 4),
              'hk3gtl:voltage_machine_casing_imv')
        a.box((5, 12, z + 2), (8, 13, z + 3),
              'gtceu:stainless_evaporation_casing')
        a.box((10, 7, z + 2), (14, 7, z + 2), PIPE)
    a.box((12, 8, 22), (12, 8, 39), 'gtceu:titanium_pipe_casing')
    a.box((12, 8, 30), (16, 8, 30), 'gtceu:titanium_pipe_casing')
    for x in (2, 12):
        for z in (19, 42):
            a.box((x, 3, z), (x, 17, z), RIB)
    for z in (19, 42):
        a.box((2, 18, z), (12, 18, z), RIB)
    a.box((2, 19, 19), (12, 19, 42), 'ad_astra:desh_panel')
    for z in (23, 31, 39):
        a.box((2, 6, z), (2, 13, z + 2), 'gtceu:fusion_glass')

    # East heat-extraction arm physically contacts the chamber jacket. Fins
    # and a low return header make the cooling path distinct from the feed.
    a.box((42, 1, 20), (55, 2, 42), 'ad_astra:etrium_panel')
    for z in (22, 27, 32, 37, 42):
        a.box((43, 3, z), (54, 24, z), COOL)
        a.box((43, 8, z), (55, 9, z),
              'gtlcore:antifreeze_heatproof_machine_casing')
        a.box((43, 17, z), (55, 18, z),
              'gtlcore:antifreeze_heatproof_machine_casing')
        a.box((43, 25, z), (54, 25, z),
              'gtceu:computer_heat_vent')
    a.box((49, 26, 22), (49, 26, 42), 'gtceu:titanium_pipe_casing')
    a.box((42, 15, 30), (49, 15, 30),
          'gtlcore:advanced_stellar_containment_casing')
    a.box((49, 5, 20), (49, 5, 42), PIPE)
    a.box((40, 5, 30), (49, 5, 30), PIPE)
    for x in (43, 54):
        for z in (22, 42):
            a.box((x, 2, z), (x, 26, z), RIB)

    # Independent front sample enclosure and control desk.
    a.box((18, 1, 2), (38, 2, 12), 'ad_astra:steel_panel')
    a.box((20, 3, 5), (27, 11, 10),
          'gtceu:sterilizing_filter_casing', True)
    a.box((21, 5, 5), (26, 8, 5), 'gtceu:laminated_glass')
    a.box((24, 12, 6), (24, 12, 9),
          'gtlcore:multi_functional_casing')
    a.box((29, 3, 5), (36, 8, 10),
          'gtceu:advanced_computer_casing', True)
    a.box((30, 5, 5), (35, 7, 5), 'gtceu:computer_casing')
    a.box((31, 9, 6), (34, 9, 9),
          'gtlcore:super_computation_component[active=false]')
    a.box((24, 6, 10), (24, 6, 17), PIPE)
    a.box((28, 4, 10), (28, 4, 17), PIPE)
    controller = [33, 6, 5]
    a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')

    # Service sockets face north and sit in the grounded front apron.
    for x in (4, 8, 12, 20, 24, 29, 34):
        if x <= 12:
            a.box((x - 1, 1, 2), (x + 1, 2, 3),
                  'gtceu:high_power_casing')
        a.box((x - 1, 3, 2), (x + 1, 7, 3),
              'gtceu:advanced_computer_casing')
    ports = [
        ('PRECURSOR', [4, 5, 2], 'north', '核心前驱体输入候选'),
        ('MEDIUM', [8, 5, 2], 'north', '结晶介质输入候选'),
        ('POWER', [12, 5, 2], 'north', '供能候选'),
        ('CRYSTAL', [20, 5, 2], 'north', '结晶体输出候选'),
        ('SAMPLE', [24, 5, 2], 'north', '取样输出候选'),
        ('RESIDUE', [29, 5, 2], 'north', '废料输出候选'),
    ]
    for _, pos, _, _ in ports:
        a.set(*pos, PORT)

    return {
        'key': 'i08', 'name': 'i08-crystallization-free',
        'title': brief['title'], 'size': [57, 43, 57], 'controller': controller,
        'ports': [{'id': key, 'pos': pos, 'face': face, 'purpose': purpose}
                  for key, pos, face, purpose in ports],
        'paths': [],
        'zones': [
            {'name': '双层结晶舱', 'kind': 'reactor', 'min': [13, 1, 15], 'max': [43, 42, 45], 'pos': [28, 42, 30], 'role': '结晶与约束', 'service_face': '四周'},
            {'name': '前驱体准备区', 'kind': 'feed', 'min': [2, 1, 19], 'max': [14, 19, 42], 'pos': [7, 19, 30], 'role': '分路配料', 'service_face': '西侧'},
            {'name': '不对称冷却臂', 'kind': 'cooling', 'min': [42, 1, 20], 'max': [55, 26, 42], 'pos': [50, 26, 30], 'role': '夹套散热', 'service_face': '东侧'},
            {'name': '取样与读出台', 'kind': 'sampling', 'min': [18, 1, 2], 'max': [38, 12, 12], 'pos': [28, 12, 7], 'role': '成品检验', 'service_face': '前侧'},
        ],
        'links': [
            {'from': '前驱体准备区', 'to': '双层结晶舱', 'route': [[12, 8, 30], [16, 8, 30]]},
            {'from': '双层结晶舱', 'to': '不对称冷却臂', 'route': [[40, 15, 30], [49, 15, 30]]},
            {'from': '双层结晶舱', 'to': '取样与读出台', 'route': [[28, 4, 17], [28, 4, 10]]},
        ],
        'brief': brief,
        'description': '中央双层结晶夹套包围独立悬置的仿制核心；左侧三路前驱体计量仓送入舱体，右侧五片不对称冷却臂从夹套抽热，前方的封闭取样柜与读出台独立于原料区。',
        'role_materials': {key: sorted(value) for key, value in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


if __name__ == '__main__':
    package(build(), OUT, 'i08', ['原料、冷却与取样分区有独立位置'])
