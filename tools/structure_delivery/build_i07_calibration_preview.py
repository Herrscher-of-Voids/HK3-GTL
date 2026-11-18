"""I07 precision detector calibration bench: paired shield rooms and metrology rail."""
import base64
import collections
import datetime
import gzip
import json
import re
import shutil

from build_i01_tidal_preview import SOURCE
from build_i03_centrifuge_preview import TEST_INSTANCE, frame
from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I07_探测器精密校准台_自由设计预览'
PORT = 'hk3gtl:industrial_port_casing'
FLOOR = 'ad_astra:ostrum_plating'
RIB = 'gtlcore:lafium_mechanical_casing'
SHIELD = 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing'
GLASS = 'gtceu:laminated_glass'
RAIL = 'gtceu:assembly_line_grating'


def chamber(a, x0, x1, active):
    """An RF shielded room with a test pedestal facing the shared axis."""
    shell = 'hk3gtl:voltage_machine_casing_hcv' if active else 'hk3gtl:voltage_machine_casing_civ'
    accent = 'gtlcore:rhenium_reinforced_energy_glass' if active else 'gtceu:fusion_glass'
    a.box((x0, 2, 13), (x1, 3, 31), SHIELD)
    frame(a, x0, x1, 4, 13, 31, RIB)
    for x in (x0, x1):
        for z in range(13, 32):
            for y in range(5, 20):
                a.set(x, y, z, RIB if z in (13, 31) or (z - 13) % 5 == 0 else shell)
        for z in range(16, 30, 5):
            a.box((x, 9, z), (x, 16, z + 2), GLASS)
    for z in (13, 31):
        a.box((x0, 5, z), (x1, 20, z), shell)
        for x in range(x0, x1 + 1, 4):
            a.box((x, 5, z), (x, 20, z), RIB)
    # The gap in the inner wall is the line-of-sight aperture, not a walkway.
    inner = x1 if x1 < 24 else x0
    for y in range(10, 15):
        for z in range(20, 25):
            a.set(inner, y, z, accent)
    for x in range(x0, x1 + 1, 4):
        a.box((x, 21, 13), (x, 21, 31), RIB)
    for z in (13, 19, 25, 31):
        a.box((x0, 21, z), (x1, 21, z), RIB)
    a.box((x0 + 1, 22, 14), (x1 - 1, 22, 30), 'ad_astra:etrium_panel')
    a.box((x0 + 3, 4, 19), (x1 - 3, 5, 25), 'gtceu:advanced_computer_casing')
    a.box((x0 + 5, 6, 20), (x1 - 5, 8, 24), 'gtlcore:multi_functional_casing')
    a.box((x0 + 6, 9, 21), (x1 - 6, 13, 23), accent)
    for z in (15, 29):
        a.box((x0 + 2, 4, z), (x0 + 4, 10, z + 1), 'gtceu:computer_casing')
        a.box((x1 - 4, 4, z), (x1 - 2, 10, z + 1), 'gtceu:advanced_computer_casing')
    return inner


def build():
    brief = {'id': 'I07', 'title': '探测器精密校准台', 'minimum_wdh': [49, 41, 33]}
    a = Build(brief)
    a.box((0, 0, 0), (48, 0, 40), FLOOR)
    frame(a, 0, 48, 1, 0, 40, 'gtlcore:space_elevator_mechanical_casing')
    for z in (12, 32):
        a.box((2, 1, z), (46, 1, z), RIB)
    for x in (2, 17, 31, 46):
        a.box((x, 1, 12), (x, 1, 32), RIB)
    for x0, x1, z0, z1 in ((3, 17, 13, 31), (31, 45, 13, 31),
                           (18, 30, 18, 27), (20, 28, 32, 38),
                           (18, 30, 2, 11), (3, 17, 8, 11),
                           (31, 45, 8, 11)):
        a.box((x0, 1, z0), (x1, 1, z1), SHIELD)

    left_inner = chamber(a, 3, 17, False)
    right_inner = chamber(a, 31, 45, True)

    # Alignment bench: three identical bridge stations expose the optical axis.
    a.box((18, 2, 18), (30, 3, 27), SHIELD)
    for x in (19, 24, 29):
        a.box((x, 4, 20), (x, 9, 25), 'gtceu:advanced_computer_casing', True)
        a.box((x, 7, 21), (x, 7, 24), 'gtlcore:multi_functional_casing')
        a.box((x, 10, 21), (x, 11, 24), RIB)
    for z in (20, 24):
        a.box((17, 12, z), (31, 12, z), 'gtlcore:echo_casing')
        a.box((18, 13, z), (30, 13, z), GLASS)
    for x in (17, 31):
        a.box((x, 4, 20), (x, 12, 20), 'gtlcore:graviton_field_constraint_casing')
        a.box((x, 4, 24), (x, 12, 24), 'gtlcore:graviton_field_constraint_casing')
    a.box((20, 5, 22), (28, 6, 22), 'gtceu:titanium_pipe_casing')
    a.box((23, 7, 22), (25, 9, 22), 'gtlcore:rhenium_reinforced_energy_glass')

    # A rear signal source feeds the axis, while separate reader racks face
    # the operator aisle. The rear mast gives a clear elevation silhouette.
    a.box((20, 2, 32), (28, 3, 38), 'gtceu:high_power_casing')
    for x in (20, 28):
        for z in (32, 38):
            a.box((x, 4, z), (x, 29, z), SHIELD)
    for y in (7, 13, 19, 25, 30):
        a.box((20, y, 32), (28, y, 38), RIB, True)
    a.box((22, 4, 34), (26, 27, 36), 'gtlcore:advanced_stellar_containment_casing')
    for y in range(6, 27, 3):
        a.box((21, y, 33), (27, y, 33), 'gtceu:computer_heat_vent')
        a.box((21, y, 37), (27, y, 37), 'gtceu:computer_heat_vent')
    a.box((23, 28, 33), (25, 31, 37), 'gtlcore:rhenium_reinforced_energy_glass')
    a.box((23, 5, 27), (25, 5, 34), 'gtceu:ptfe_pipe_casing')
    a.box((23, 6, 27), (25, 6, 27), RIB)

    # Front instrument gallery is low so both chamber fronts remain visible.
    a.box((18, 2, 2), (30, 3, 11), 'ad_astra:steel_panel')
    for x in (18, 30):
        a.box((x, 4, 2), (x, 12, 11), RIB, True)
    for z in (2, 11):
        a.box((18, 12, z), (30, 12, z), RIB)
    a.box((18, 13, 2), (30, 13, 11), 'ad_astra:desh_panel')
    for x in (20, 24, 28):
        a.box((x - 1, 4, 7), (x + 1, 8, 9), 'gtceu:advanced_computer_casing')
        a.box((x, 5, 7), (x, 7, 7), 'gtlcore:super_computation_component[active=false]')
    for x in (20, 28):
        a.box((x, 7, 10), (x, 7, 19), 'gtceu:ptfe_pipe_casing')
    controller = [24, 6, 2]
    a.box((24, 4, 2), (24, 5, 2), 'gtceu:advanced_computer_casing')
    a.set(*controller, 'gtlcore:advanced_stellar_containment_casing')

    # Interface sockets have a solid backplate and floor. All service faces
    # point into the open forecourt instead of scattering around the rear.
    for x in (6, 10, 14):
        a.box((x - 1, 3, 8), (x + 1, 7, 9), 'gtceu:advanced_computer_casing')
    for x in (34, 38, 42):
        a.box((x - 1, 3, 8), (x + 1, 7, 9), 'gtceu:advanced_computer_casing')
    a.box((3, 2, 9), (17, 3, 11), SHIELD)
    a.box((31, 2, 9), (45, 3, 11), SHIELD)
    ports = [
        ('REFERENCE', [6, 5, 8], 'north', '标准件输入候选'),
        ('TEST_PIECE', [10, 5, 8], 'north', '待测探测器输入候选'),
        ('POWER', [14, 5, 8], 'north', '供能候选'),
        ('READOUT', [34, 5, 8], 'north', '校准数据输出候选'),
        ('PRODUCT', [38, 5, 8], 'north', '已校准探测器输出候选'),
        ('REJECT', [42, 5, 8], 'north', '不合格件输出候选'),
    ]
    for _, pos, _, _ in ports:
        a.set(*pos, PORT)

    return {
        'key': 'i07', 'name': 'i07-precision-calibration-free',
        'title': brief['title'], 'size': [49, 33, 41], 'controller': controller,
        'ports': [{'id': key, 'pos': pos, 'face': face, 'purpose': purpose}
                  for key, pos, face, purpose in ports],
        'paths': [{'name': '正面维护通道', 'min': [20, 1, 14], 'max': [28, 1, 17]}],
        'zones': [
            {'name': '标准件屏蔽室', 'kind': 'reference', 'min': [3, 2, 13], 'max': [17, 22, 31], 'pos': [10, 22, 22], 'role': '基准样本', 'service_face': '前侧'},
            {'name': '中央标定轨道', 'kind': 'metrology', 'min': [17, 2, 18], 'max': [31, 13, 27], 'pos': [24, 13, 22], 'role': '共轴校准', 'service_face': '前侧'},
            {'name': '待测件屏蔽室', 'kind': 'test', 'min': [31, 2, 13], 'max': [45, 22, 31], 'pos': [38, 22, 22], 'role': '待测探测器', 'service_face': '前侧'},
            {'name': '信号源塔', 'kind': 'source', 'min': [20, 2, 32], 'max': [28, 31, 38], 'pos': [24, 31, 35], 'role': '可控激励', 'service_face': '后侧'},
            {'name': '读出控制台', 'kind': 'readout', 'min': [18, 2, 2], 'max': [30, 13, 11], 'pos': [24, 13, 7], 'role': '读出与调节', 'service_face': '前侧'},
        ],
        'links': [
            {'from': '标准件屏蔽室', 'to': '中央标定轨道', 'route': [[left_inner, 12, 22], [24, 12, 22]]},
            {'from': '中央标定轨道', 'to': '待测件屏蔽室', 'route': [[24, 12, 22], [right_inner, 12, 22]]},
            {'from': '信号源塔', 'to': '中央标定轨道', 'route': [[24, 5, 34], [24, 5, 27]]},
        ],
        'brief': brief,
        'description': '参考精密计量实验室与射频屏蔽室：左右两间封闭测试室分别放置标准件和待测探测器，透过同轴观察口对准中央三段标定轨道；后方信号源塔提供可辨认的激励路径，前方集中读出柜与六个工业接口。',
        'role_materials': {key: sorted(value) for key, value in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


def audit_geometry(data):
    occupied = {tuple(block['pos']) for block in data['blocks']}
    states = {tuple(block['pos']): block['state'] for block in data['blocks']}
    assert all(all(0 <= pos[i] < data['size'][i] for i in range(3)) for pos in occupied)
    connected = {next(iter(occupied))}
    frontier = list(connected)
    for current in frontier:
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            neighbor = (current[0] + dx, current[1] + dy, current[2] + dz)
            if neighbor in occupied and neighbor not in connected:
                connected.add(neighbor)
                frontier.append(neighbor)
    if connected != occupied:
        detached = occupied - connected
        sample = sorted(detached)[:12]
        raise AssertionError(f'{len(detached)} disconnected blocks; sample={sample}')
    for port in data['ports']:
        x, y, z = port['pos']
        assert states[x, y, z] == PORT, port
        assert (x, y, z + 1) in occupied and (x, y - 1, z) in occupied, port
        assert (x, y, z - 1) not in occupied, port
    for path in data['paths']:
        lo, hi = path['min'], path['max']
        assert not any((x, y, z) in occupied
                       for x in range(lo[0], hi[0] + 1)
                       for y in range(lo[1], hi[1] + 1)
                       for z in range(lo[2], hi[2] + 1)), path
    return require(data)


def package(data, out, source_key, checks):
    size_audit = audit_geometry(data)
    counts = collections.Counter(block['state'] for block in data['blocks'])
    resources = Resources(instance=TEST_INSTANCE, project_resources=ROOT / 'src/main/resources')
    try:
        materials = [resources.material(state) for state in sorted(counts)]
    finally:
        resources.close()
    out.mkdir(parents=True, exist_ok=True)
    states, groups, hashes = export(data, out)
    render(data, materials, out)
    audit = {
        'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'instance': str(TEST_INSTANCE), 'palette': dict(counts), 'hashes': hashes,
        'project_resource_overlay': 'src/main/resources/assets/hk3gtl; instance files unchanged',
        'size_baseline': size_audit,
        'checks': ['正式名称保持' + data['title'], '测试包真实方块模型与纹理解析',
                   'NBT与Sponge逐格回读', '实体尺寸不低于占地总表',
                   '方块六面连通且无孤立构件',
                   '工业接口前方留空且有背板与底座'] + checks,
        'not_verified': ['待外观确认', '未接入正式Pattern与配方',
                         '未实测浏览器交互与游戏运行', '生存材料可达性尚未核验'],
    }
    meta = {key: value for key, value in data.items() if key != 'blocks'}
    payload = {'data': meta, 'palette': states, 'groups': groups,
               'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(
        payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (out / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (out / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', out / 'viewer.bundle.js')
    page = (SOURCE / source_key / '三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('实体草稿01', '自由设计候选').replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace(f'hk3gtl-{source_key}-redesign-01', data['name'])
    width, height, depth = data['size']
    page = re.sub(r'\d+×\d+×\d+（宽×长×高） · [\d,]+个实体',
                  f'{width}×{depth}×{height}（宽×长×高） · {len(data["blocks"]):,}个实体', page)
    page = re.sub(r'id="layerValue">\d+', f'id="layerValue">{height - 1}', page)
    page = re.sub(r'id="layer" type="range" min="0" max="\d+" value="\d+"',
                  f'id="layer" type="range" min="0" max="{height - 1}" value="{height - 1}"', page)
    page = re.sub(r'(<summary>本机建筑概念</summary><p>).*?(</p>)',
                  lambda match: match[1] + data['description'] + match[2], page)
    (out / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(out), 'blocks': len(data['blocks']),
                      'materials': len(counts), 'size_audit': size_audit}, ensure_ascii=False))


def main():
    package(build(), OUT, 'i07', ['正面维护通道净空'])


if __name__ == '__main__':
    main()
