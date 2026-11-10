# -*- coding: utf-8 -*-
"""Independent I03 centrifugal separation center appearance candidate."""
import base64
import collections
import datetime
import gzip
import json
import math
import re
import shutil
from pathlib import Path

from build_i01_tidal_preview import SOURCE
from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I03_崩坏能离心分离中心_自由设计预览'
TEST_INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'


def circle(a, cx, cz, radius, y, material, thickness=1):
    inner = radius - thickness
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            d = math.hypot(x - cx, z - cz)
            if inner < d <= radius:
                a.set(x, y, z, material)


def frame(a, x0, x1, y, z0, z1, material):
    for z in (z0, z1):
        a.line((x0, y, z), (x1, y, z), material)
    for x in (x0, x1):
        a.line((x, y, z0), (x, y, z1), material)


def build():
    brief = {'id': 'I03', 'title': '崩坏能离心分离中心',
             'minimum_wdh': [65, 55, 40]}
    a = Build(brief)
    foundation = 'gtlcore:iridium_casing'
    shell = 'gtlcore:process_machine_casing'
    rib = 'gtceu:high_power_casing'
    pipe = 'gtceu:tungstensteel_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    panel = 'gtceu:advanced_computer_casing'
    glass = 'gtceu:fusion_glass'
    blue = 'gtlcore:hsss_reinforced_borosilicate_glass'
    violet = 'gtlcore:rhenium_reinforced_energy_glass'

    # Separated radial foundations leave walkable ground around both drums.
    for cx, cz, r in ((24, 29, 14), (48, 24, 10)):
        for x in range(cx-r, cx+r+1):
            for z in range(cz-r, cz+r+1):
                if math.hypot(x-cx, z-cz) <= r:
                    a.set(x, 0, z, foundation)
        circle(a, cx, cz, r, 1, rib)
        circle(a, cx, cz, r-3, 1, pipe)
    a.box((20, 0, 1), (28, 1, 16), foundation)
    a.box((20, 0, 40), (28, 1, 53), foundation)
    a.box((34, 0, 20), (39, 1, 31), foundation)
    for z in (5, 11, 46, 51):
        a.box((18, 0, z), (30, 0, z+1), rib)

    # Main centrifuge: a heavy outer cage contains a visibly layered rotor.
    for y in range(5, 36):
        outer = 12 if 8 <= y <= 31 else (10 if y in (6, 7, 32, 33) else 7)
        mat = rib if y in (5, 8, 15, 22, 29, 33, 35) else glass
        circle(a, 24, 29, outer, y, mat, 2 if y in (8, 15, 22, 29, 33) else 1)
        if 8 <= y <= 31:
            for x, z in ((12, 29), (36, 29), (24, 17), (24, 41)):
                a.set(x, y, z, shell)
        if 10 <= y <= 29:
            circle(a, 24, 29, 7, y, pipe if y % 6 == 0 else violet)
            if y % 4 == 0:
                circle(a, 24, 29, 4, y, rib)
            a.set(24, y, 29, panel)
    for y in (9, 16, 23, 30):
        circle(a, 24, 29, 13, y, foundation)
    for x, z in ((12, 29), (36, 29), (24, 17), (24, 41)):
        a.box((x-1, 1, z-1), (x+1, 5, z+1), foundation)
    for y in (36, 39):
        circle(a, 24, 29, 8 if y == 36 else 5, y, shell, 2)
    a.box((22, 37, 27), (26, 38, 31), panel, True)
    a.line((24, 34, 29), (24, 39, 29), pipe)

    # A smaller auxiliary drum visibly receives the upper fraction.
    for y in range(5, 26):
        radius = 8 if 7 <= y <= 22 else 6
        mat = rib if y in (5, 7, 12, 17, 22, 25) else glass
        circle(a, 48, 24, radius, y, mat, 2 if y in (7, 12, 17, 22) else 1)
        if 8 <= y <= 21:
            circle(a, 48, 24, 4, y, blue if y % 3 else pipe)
            a.set(48, y, 24, panel)
    for x, z in ((40, 24), (56, 24), (48, 16), (48, 32)):
        a.box((x, 1, z), (x, 22, z), shell)
        for y in (7, 12, 17, 22):
            a.set(x, y, z, rib)
    circle(a, 48, 24, 6, 26, shell, 2)
    a.box((46, 27, 22), (50, 28, 26), vent)

    # High transfer gantry; the lower crossing is a distinct return line.
    for y in (25, 28):
        a.box((36, y, 27), (40, y, 29), rib)
        a.box((40, y, 24), (41, y, 29), rib)
    a.box((37, 26, 28), (40, 27, 28), glass)
    a.box((40, 26, 24), (41, 27, 28), blue)
    for y in (5, 7):
        a.box((36, y, 34), (48, y, 34), pipe)
    for x in (38, 42, 46):
        a.box((x, 2, 34), (x, 5, 34), shell)
    a.box((37, 8, 34), (47, 8, 34), vent)

    # Intake manifold, three differentiated fractions, and service cabinets.
    a.box((19, 2, 3), (29, 3, 14), shell, True)
    for z in (5, 9, 13):
        frame(a, 20, 28, 5, z, z+1, rib)
        a.box((21, 4, z), (27, 4, z+1), pipe)
    a.line((24, 5, 14), (24, 11, 20), pipe)
    for x0, x1, role in ((16, 19, '净化液输出'),
                         (22, 26, '载能母液回流'), (29, 32, '分离残渣输出')):
        a.box((x0, 2, 44), (x1, 8, 51), shell, True)
        for y in (3, 6):
            frame(a, x0, x1, y, 44, 51, rib)
        a.box((x0, 5, 44), (x1, 5, 44), vent)
        a.line(((x0+x1)//2, 7, 42), ((x0+x1)//2, 7, 44), pipe)
    for z in (18, 21, 24):
        a.box((58, 2, z), (61, 10, z+1), panel)
        a.box((58, 11, z), (61, 11, z+1), vent)
        a.line((56, 6, z), (58, 6, z), pipe)

    a.box((28, 2, 1), (36, 3, 4), shell, True)
    a.set(32, 4, 1, 'gtlcore:advanced_stellar_containment_casing')
    ports = [
        ('FEED', (29, 4, 1), 'north', '原液输入候选'),
        ('POWER', (35, 4, 1), 'north', '供能候选'),
        ('PURE', (17, 4, 51), 'south', '净化液输出候选'),
        ('MOTHER', (24, 4, 51), 'south', '载能母液回流候选'),
        ('RESIDUE', (30, 4, 51), 'south', '分离残渣输出候选'),
    ]
    for _, pos, _, _ in ports:
        a.set(*pos, 'hk3gtl:industrial_port_casing')
    return {
        'key': 'i03', 'name': 'i03-centrifuge-free', 'title': brief['title'],
        'size': [65, 40, 55], 'controller': [32, 4, 1],
        'ports': [{'id': name, 'pos': list(pos), 'face': face, 'purpose': purpose}
                  for name, pos, face, purpose in ports],
        'paths': [],
        'zones': [
            {'name': '进样管汇', 'kind': 'intake', 'min': [19, 0, 1], 'max': [29, 11, 20],
             'pos': [24, 10, 9], 'role': '原液送入主鼓', 'service_face': '前侧'},
            {'name': '主离心鼓', 'kind': 'centrifuge', 'min': [11, 0, 16], 'max': [37, 39, 42],
             'pos': [24, 39, 29], 'role': '多级离心分层', 'service_face': '环周'},
            {'name': '副分离鼓', 'kind': 'polisher', 'min': [40, 0, 16], 'max': [56, 28, 32],
             'pos': [48, 28, 24], 'role': '二次分离', 'service_face': '东侧'},
            {'name': '三路出料', 'kind': 'outputs', 'min': [16, 0, 42], 'max': [32, 8, 51],
             'pos': [24, 8, 48], 'role': '净化液、母液、残渣', 'service_face': '后侧'},
        ],
        'links': [],
        'description': '主离心鼓的分层转子与副分离鼓由高位输送架相连；低位回流管和后三路出料区分别表达母液回流、净化液与残渣。',
        'brief': brief, 'role_materials': {k: sorted(v) for k, v in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    size_audit = require(data)
    counts = collections.Counter(block['state'] for block in data['blocks'])
    resources = Resources(instance=TEST_INSTANCE, project_resources=ROOT / 'src/main/resources')
    try:
        materials = [resources.material(state) for state in sorted(counts)]
        project_sources = {rel: source for rel, source in resources.sources.items() if source.startswith(str(ROOT / 'src/main/resources'))}
    finally:
        resources.close()
    for rel, source in project_sources.items():
        target = OUT / 'project_resources' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    states, groups, hashes = export(data, OUT)
    render(data, materials, OUT)
    bounds = [[min(b['pos'][i] for b in data['blocks']),
               max(b['pos'][i] for b in data['blocks'])] for i in range(3)]
    audit = {
        'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'palette': dict(counts),
        'namespace_counts': {ns: sum(n for state, n in counts.items() if state.startswith(ns + ':'))
                             for ns in {s.split(':')[0] for s in counts}},
        'actual_bounds_xyz': bounds, 'hashes': hashes, 'size_baseline': size_audit,
        'port_placeholder': 'hk3gtl:industrial_port_casing', 'project_assets_saved': sorted(project_sources),
        'checks': ['正式名称保持崩坏能离心分离中心', '完整立方体建材',
                   'NBT与Sponge逐格导出回读', '方块材质由当前GTL增强版实例资源解析'],
        'not_verified': ['未获外观确认', '未接入正式Pattern或配方',
                         '未进行游戏成型与运行测试', '生存材料可达性尚未核验'],
    }
    meta = {key: value for key, value in data.items() if key != 'blocks'}
    payload = {'data': meta, 'palette': states, 'groups': groups,
               'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(
        payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps(
        {'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (SOURCE / 'i03/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('实体草稿01', '自由设计候选')
    page = page.replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace('hk3gtl-i03-redesign-01', data['name'])
    page = page.replace('未实测浏览器交互或游戏', '待浏览器交互复核，尚未进行游戏测试')
    page = re.sub(r'\d+×\d+×\d+（宽×长×高） · [\d,]+个实体',
                  f'65×55×40（宽×长×高） · {len(data["blocks"]):,}个实体', page)
    page = re.sub(r'id="layerValue">\d+', 'id="layerValue">39', page)
    page = re.sub(r'id="layer" type="range" min="0" max="\d+" value="\d+"',
                  'id="layer" type="range" min="0" max="39" value="39"', page)
    page = re.sub(r'(<summary>本机建筑概念</summary><p>).*?(</p>)',
                  lambda match: match.group(1) + data['description'] + match.group(2), page)
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']),
                      'bounds': bounds, 'palette': dict(counts)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
