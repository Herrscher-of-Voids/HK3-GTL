"""I06 fuel blending plant: tank farm, metering gallery, and filling shed."""
import base64
import collections
import datetime
import gzip
import json
import re
import shutil

from build_i01_tidal_preview import SOURCE
from build_i03_centrifuge_preview import TEST_INSTANCE, circle, frame
from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I06_崩坏能燃料调配厂_自由设计预览'


def build():
    brief = {'id': 'I06', 'title': '崩坏能燃料调配厂', 'minimum_wdh': [65, 47, 39]}
    a = Build(brief)
    foundation = 'ad_astra:ostrum_plating'
    frame_block = 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing'
    catwalk = 'gtceu:assembly_line_grating'
    pipe = 'gtceu:ptfe_pipe_casing'
    manifold = 'gtceu:titanium_pipe_casing'
    port = 'hk3gtl:industrial_port_casing'

    # Separated spill-containment pads make the fuel path legible in plan view.
    for x0, x1, z0, z1 in ((2, 23, 10, 44), (25, 46, 9, 40), (48, 62, 3, 43)):
        a.box((x0, 0, z0), (x1, 1, z1), foundation)
        frame(a, x0, x1, 2, z0, z1, 'gtlcore:lafium_mechanical_casing')
    for x, z in ((23, 18), (47, 18), (23, 35), (47, 35)):
        a.box((x, 1, z), (x + 1, 4, z + 1), frame_block)
    a.box((22, 3, 18), (49, 4, 19), catwalk)
    a.box((22, 3, 34), (49, 4, 35), catwalk)

    # Three different storage vessels share a raised measuring header but
    # retain separate feed lines and recognizable service platforms.
    tanks = ((10, 20, 6, 21, 'hk3gtl:voltage_machine_casing_icv'),
             (17, 32, 5, 17, 'hk3gtl:voltage_machine_casing_imv'),
             (8, 39, 4, 13, 'hk3gtl:voltage_machine_casing_irv'))
    for cx, cz, radius, top, shell in tanks:
        for y in range(3, top + 1):
            belt = y in (3, top) or (y - 3) % 6 == 0
            circle(a, cx, cz, radius, y,
                   'gtceu:corrosion_proof_casing' if belt else shell, 2)
            if not belt:
                a.box((cx - 1, y, cz - radius), (cx + 1, y, cz - radius),
                      'gtceu:laminated_glass')
            a.set(cx, y, cz, 'gtlcore:rhenium_reinforced_energy_glass')
        a.set(cx, 2, cz, frame_block)
        circle(a, cx, cz, radius - 1, top + 1,
               'gtceu:stainless_evaporation_casing', radius - 1)
        a.box((cx - 1, top + 2, cz - 1), (cx + 1, top + 3, cz + 1),
              'gtceu:advanced_computer_casing')
        a.line((cx + radius, 5, cz), (24, 5, cz), pipe)
        for x in range(cx - radius - 1, cx + radius + 2):
            for z in range(cz - radius - 1, cz + radius + 2):
                if max(abs(x - cx), abs(z - cz)) == radius + 1:
                    a.set(x, min(top - 3, 13), z, catwalk)
    a.line((24, 6, 17), (24, 6, 40), manifold)
    for cz in (20, 32, 39):
        a.line((24, 5, cz), (24, 6, cz), manifold)

    # The central enclosed mixing shed has a tall central vessel, exposed
    # dosing skids, glazed bays, and a serviceable trussed roof.
    a.box((27, 3, 12), (44, 24, 36), frame_block, True)
    for z in range(13, 36, 5):
        for x in (27, 44):
            a.box((x, 5, z), (x, 20, z + 2), 'gtceu:fusion_glass')
            a.box((x, 5, z + 3), (x, 24, z + 3),
                  'gtlcore:space_elevator_mechanical_casing')
    for x in range(29, 44, 4):
        a.box((x, 8, 12), (x + 2, 19, 12), 'gtceu:laminated_glass')
        a.box((x, 8, 36), (x + 2, 19, 36), 'gtceu:laminated_glass')
    for y in range(5, 29):
        circle(a, 35, 25, 5, y,
               'gtlcore:multi_functional_casing' if y % 5 == 0
               else 'hk3gtl:voltage_machine_casing_civ', 2)
        circle(a, 35, 25, 2, y, 'gtlcore:rhenium_reinforced_energy_glass')
    for y in (10, 18, 25):
        circle(a, 35, 25, 7, y, catwalk, 3)
    for x in (30, 40):
        for z in (18, 31):
            a.box((x - 1, 5, z - 2), (x + 1, 9, z + 2),
                  'gtceu:sterilizing_filter_casing', True)
            a.box((x, 6, z), (x, 8, z), 'gtceu:computer_casing')
            a.line((x, 10, z), (35, 10, z), manifold)
    for z in range(12, 37, 4):
        a.box((27, 25, z), (44, 26, z),
              'gtlcore:lafium_mechanical_casing')
        a.box((29, 26, z + 1), (42, 26, z + 2),
              'ad_astra:etrium_panel')
    a.box((32, 29, 22), (38, 30, 28),
          'gtlcore:advanced_stellar_containment_casing', True)
    a.line((24, 13, 25), (28, 13, 25), manifold)
    a.line((43, 13, 25), (51, 13, 25), manifold)

    # A long filling canopy and two product tanks read like a loading rack,
    # rather than another vertical process tower.
    a.box((49, 3, 15), (61, 4, 41), 'ad_astra:desh_panel')
    for z in (17, 25, 33, 41):
        for x in (49, 61):
            a.box((x, 5, z), (x, 17, z), frame_block)
        a.box((49, 18, z), (61, 19, z),
              'gtlcore:lafium_mechanical_casing')
    a.box((49, 19, 17), (61, 20, 41), 'ad_astra:etrium_panel')
    for z in (21, 29, 37):
        a.box((50, 6, z - 1), (60, 7, z + 1), catwalk)
        a.box((53, 8, z), (57, 13, z),
              'gtlcore:antifreeze_heatproof_machine_casing', True)
        a.line((55, 14, z), (55, 17, z), manifold)
    a.line((55, 17, 18), (55, 17, 40), manifold)
    for cx in (51, 59):
        circle(a, cx, 8, 3, 2, frame_block, 2)
        for y in range(3, 11):
            circle(a, cx, 8, 3, y,
                   'hk3gtl:voltage_machine_casing_civ' if y in (3, 10)
                   else 'hk3gtl:glass_honkai_stabilized', 2)
        a.line((cx, 9, 11), (cx, 9, 18), pipe)

    # Forecourt routes access around the controller without crossing a tank.
    a.box((25, 1, 2), (45, 2, 8), 'ad_astra:steel_panel')
    a.box((25, 3, 2), (45, 7, 3), 'gtceu:advanced_computer_casing', True)
    a.box((26, 7, 2), (44, 7, 3), 'gtlcore:lafium_mechanical_casing')
    a.box((33, 4, 2), (37, 6, 2), 'gtceu:computer_casing')
    controller = [35, 5, 2]
    a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')
    a.box((49, 3, 14), (61, 8, 16), 'gtceu:advanced_computer_casing', True)
    a.box((50, 4, 15), (60, 6, 15), 'gtceu:advanced_computer_casing')
    a.box((49, 8, 14), (61, 8, 16), 'gtlcore:lafium_mechanical_casing')
    a.box((54, 5, 14), (56, 6, 14), 'gtceu:laminated_glass')
    ports = [('STABLE_FEED', [27, 5, 2], 'north', '稳定液态输入候选'),
             ('MEDIUM', [30, 5, 2], 'north', '稳定介质输入候选'),
             ('SOLID_FEED', [40, 5, 2], 'north', '燃料基质及晶体输入候选'),
             ('POWER', [43, 5, 2], 'north', '供能候选'),
             ('FUEL', [52, 5, 14], 'north', '液态燃料输出候选'),
             ('RESIDUE', [58, 5, 14], 'north', '残液和残渣输出候选')]
    for _, pos, _, _ in ports:
        a.set(*pos, port)
    return {
        'key': 'i06', 'name': 'i06-fuel-blending-free', 'title': brief['title'],
        'size': [65, 39, 47], 'controller': controller,
        'ports': [{'id': key, 'pos': pos, 'face': face, 'purpose': purpose}
                  for key, pos, face, purpose in ports],
        'paths': [{'name': '控制台前检修区', 'min': [33, 3, 4], 'max': [37, 6, 8]}],
        'zones': [
            {'name': '分隔原料罐区', 'kind': 'tank_farm', 'min': [2, 0, 10], 'max': [23, 25, 44], 'pos': [12, 21, 27], 'role': '原料储存', 'service_face': '东侧'},
            {'name': '封闭计量混合车间', 'kind': 'blending', 'min': [25, 0, 9], 'max': [46, 31, 40], 'pos': [35, 30, 25], 'role': '计量与调配', 'service_face': '前侧与两侧'},
            {'name': '成品缓冲与灌装棚', 'kind': 'filling', 'min': [48, 0, 3], 'max': [62, 21, 43], 'pos': [55, 20, 29], 'role': '成品输出', 'service_face': '前侧'}],
        'links': [
            {'from': '分隔原料罐区', 'to': '封闭计量混合车间', 'route': [[24, 13, 25], [28, 13, 25]]},
            {'from': '封闭计量混合车间', 'to': '成品缓冲与灌装棚', 'route': [[43, 13, 25], [51, 13, 25]]}],
        'brief': brief,
        'description': '以现实燃料调配厂的储罐围堰、计量泵组、封闭混合车间和灌装棚为布局参考。左侧三只独立原料罐通过高位计量总管进料；中央混合容器被操作层与仪表车间包围；右侧低矮灌装棚与双成品缓冲罐分开交付。',
        'role_materials': {key: sorted(value) for key, value in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


def main():
    data = build()
    size_audit = require(data)
    occupied = {tuple(block['pos']) for block in data['blocks']}
    states = {tuple(block['pos']): block['state'] for block in data['blocks']}
    assert all(all(0 <= pos[i] < data['size'][i] for i in range(3))
               for pos in occupied)
    connected = {next(iter(occupied))}
    frontier = list(connected)
    directions = ((1, 0, 0), (-1, 0, 0), (0, 1, 0),
                  (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for current in frontier:
        for delta in directions:
            neighbor = tuple(current[i] + delta[i] for i in range(3))
            if neighbor in occupied and neighbor not in connected:
                connected.add(neighbor)
                frontier.append(neighbor)
    assert connected == occupied, f'{len(occupied) - len(connected)} disconnected blocks'
    for port in data['ports']:
        x, y, z = port['pos']
        assert states[x, y, z] == 'hk3gtl:industrial_port_casing', port
        assert (x, y, z + 1) in occupied and (x, y - 1, z) in occupied, port
        assert (x, y, z - 1) not in occupied, port
    for path in data['paths']:
        lo, hi = path['min'], path['max']
        assert not any((x, y, z) in occupied
                       for x in range(lo[0], hi[0] + 1)
                       for y in range(lo[1], hi[1] + 1)
                       for z in range(lo[2], hi[2] + 1)), path
    counts = collections.Counter(block['state'] for block in data['blocks'])
    resources = Resources(instance=TEST_INSTANCE,
                          project_resources=ROOT / 'src/main/resources')
    try:
        materials = [resources.material(state) for state in sorted(counts)]
    finally:
        resources.close()
    OUT.mkdir(parents=True, exist_ok=True)
    states, groups, hashes = export(data, OUT)
    render(data, materials, OUT)
    audit = {
        'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'instance': str(TEST_INSTANCE), 'palette': dict(counts), 'hashes': hashes,
        'project_resource_overlay': 'src/main/resources/assets/hk3gtl; instance files unchanged',
        'size_baseline': size_audit,
        'checks': ['正式名称保持崩坏能燃料调配厂', '测试包真实方块模型与纹理解析',
                   'NBT与Sponge逐格回读', '尺寸下限与检修净空检查',
                   '所有方块在声明范围内且六面连通，无孤立方块',
                   '六个工业接口均有背板与底座，前方留空'],
        'not_verified': ['待外观确认', '未接入正式Pattern与配方',
                         '未实测浏览器交互与游戏运行', '生存材料可达性尚未核验'],
    }
    meta = {key: value for key, value in data.items() if key != 'blocks'}
    payload = {'data': meta, 'palette': states, 'groups': groups,
               'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(
        payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (SOURCE / 'i06/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('实体草稿01', '自由设计候选').replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace('hk3gtl-i06-redesign-01', data['name'])
    page = re.sub(r'\d+×\d+×\d+（宽×长×高） · [\d,]+个实体',
                  f'65×47×39（宽×长×高） · {len(data["blocks"]):,}个实体', page)
    page = re.sub(r'id="layerValue">\d+', 'id="layerValue">38', page)
    page = re.sub(r'id="layer" type="range" min="0" max="\d+" value="\d+"',
                  'id="layer" type="range" min="0" max="38" value="38"', page)
    page = re.sub(r'(<summary>本机建筑概念</summary><p>).*?(</p>)',
                  lambda match: match[1] + data['description'] + match[2], page)
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']),
                      'materials': len(counts), 'size_audit': size_audit}, ensure_ascii=False))


if __name__ == '__main__':
    main()
