# -*- coding: utf-8 -*-
"""I04 staged stabilization spire appearance candidate using the test pack."""
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


OUT = ROOT / 'deliveries/I04_液态崩坏能稳定塔_自由设计预览'


def octagon(a, cx, cz, radius, y, material):
    for x in range(-radius, radius + 1):
        for z in range(-radius, radius + 1):
            inside = max(abs(x), abs(z)) <= radius and abs(x) + abs(z) <= radius + radius // 2
            inner = max(abs(x), abs(z)) < radius and abs(x) + abs(z) < radius + radius // 2
            if inside and not inner:
                a.set(cx + x, y, cz + z, material)


def build():
    brief = {'id': 'I04', 'title': '液态崩坏能稳定塔', 'minimum_wdh': [53, 49, 61]}
    a = Build(brief)
    base = 'gtlcore:iridium_casing'
    shell = 'gtlcore:process_machine_casing'
    rib = 'gtceu:high_power_casing'
    pipe = 'gtceu:tungstensteel_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    panel = 'gtceu:advanced_computer_casing'
    glass = 'gtceu:fusion_glass'
    cold = 'gtlcore:hsss_reinforced_borosilicate_glass'
    energy = 'gtlcore:rhenium_reinforced_energy_glass'
    marker = 'gtlcore:advanced_stellar_containment_casing'

    # Separate foundations expose the service space below the suspended column.
    for x0, x1, z0, z1 in ((17, 35, 17, 35), (2, 12, 19, 34),
                           (40, 50, 19, 34), (18, 34, 39, 47)):
        a.box((x0, 0, z0), (x1, 1, z1), base)
        frame(a, x0, x1, 2, z0, z1, rib)
    for x in (19, 33):
        for z in (19, 33):
            a.box((x - 1, 2, z - 1), (x + 1, 8, z + 1), base)
            a.box((x, 9, z), (x, 49, z), shell)
            for y in (9, 22, 35, 48):
                a.box((x - 1, y, z - 1), (x + 1, y + 1, z + 1), rib)

    # Three faceted treatment stages narrow upward, with solid corner armour.
    for bottom, top, radius in ((9, 21, 8), (23, 34, 7), (36, 47, 6)):
        for y in range(bottom, top + 1):
            octagon(a, 26, 26, radius, y, rib if y in (bottom, top) else glass)
            for dx, dz in ((-radius, -2), (-radius, 2), (radius, -2), (radius, 2),
                           (-2, -radius), (2, -radius), (-2, radius), (2, radius)):
                a.set(26 + dx, y, 26 + dz, shell)
            circle(a, 26, 26, 3, y, pipe if y in (bottom, top) else energy)
            a.set(26, y, 26, panel)
        for y in (bottom + 3, top - 3):
            octagon(a, 26, 26, radius + 1, y, base)
        octagon(a, 26, 26, radius - 2, top, rib)
    for y in (22, 35, 48):
        circle(a, 26, 26, 5, y, shell, 2)
        a.set(26, y, 26, pipe)

    # A stepped crown terminates the column instead of forming another drum.
    for y, radius in ((49, 7), (50, 7), (51, 6), (52, 6), (53, 5),
                      (54, 5), (55, 4), (56, 4), (57, 3)):
        octagon(a, 26, 26, radius, y, rib if y % 2 else base)
    a.box((25, 49, 25), (27, 58, 27), energy)
    a.box((25, 59, 25), (27, 60, 27), marker)

    # Cooling wings have repeated open slots and different heights.
    wings = ((7, 26, 40, 'west'), (45, 26, 46, 'east'), (26, 43, 52, 'south'))
    for cx, cz, height, direction in wings:
        if direction == 'south':
            for dx in (-6, -3, 0, 3, 6):
                a.box((cx + dx, 3, cz - 2), (cx + dx, height - abs(dx), cz + 2), shell)
                a.box((cx + dx, 6, cz - 2), (cx + dx, height - abs(dx) - 2, cz - 2), cold)
            for y in range(8, height, 7):
                a.box((cx - 6, y, cz - 2), (cx + 6, y, cz + 2), vent)
            a.line((cx, 4, cz + 3), (cx, height, cz + 3), pipe)
        else:
            for dz in (-6, -3, 0, 3, 6):
                a.box((cx - 2, 3, cz + dz), (cx + 2, height - abs(dz), cz + dz), shell)
                a.box((cx - 2, 6, cz + dz), (cx - 2, height - abs(dz) - 2, cz + dz), cold)
            for y in range(8, height, 7):
                a.box((cx - 2, y, cz - 6), (cx + 2, y, cz + 6), vent)
            a.line((cx + 3, 4, cz), (cx + 3, height, cz), pipe)
        for y in (14, 28, 40):
            if y < height:
                target = (18, y, 26) if direction == 'west' else ((34, y, 26) if direction == 'east' else (26, y, 34))
                a.line((cx, y, cz), target, pipe)
        a.set(cx, height, cz, marker)

    # Front intake buffer and low, visibly distinct medium return manifold.
    a.box((17, 0, 2), (35, 1, 12), base)
    for cx in (21, 31):
        for y in range(3, 10):
            circle(a, cx, 8, 3, y, rib if y in (3, 9) else cold)
        a.box((cx - 1, 4, 7), (cx + 1, 8, 9), energy)
        a.line((cx, 7, 11), (cx, 9, 18), pipe)
    a.box((23, 2, 2), (29, 4, 3), panel)
    a.set(26, 4, 2, marker)
    for z in (19, 33):
        a.line((10, 4, z), (42, 4, z), pipe)
    a.line((42, 4, 19), (42, 4, 37), pipe)
    a.line((10, 4, 19), (10, 4, 37), pipe)
    a.box((37, 0, 36), (47, 1, 45), base)
    a.box((38, 2, 37), (46, 8, 44), panel, True)
    for z in (38, 41, 44):
        a.box((38, 9, z), (46, 9, z), vent)
    a.line((26, 8, 34), (42, 8, 38), pipe)
    ports = [('FEED', [21, 4, 4], 'north', '原液输入候选'),
             ('MEDIUM', [31, 4, 4], 'north', '稳定介质输入候选'),
             ('POWER', [29, 4, 2], 'north', '供能候选'),
             ('PRODUCT', [46, 4, 44], 'south', '稳定液输出候选'),
             ('RETURN', [39, 4, 44], 'south', '介质返回候选')]
    for _, pos, _, _ in ports:
        a.set(*pos, 'hk3gtl:industrial_port_casing')
    return {'key': 'i04', 'name': 'i04-stabilization-free', 'title': brief['title'],
            'size': [53, 61, 49], 'controller': [26, 4, 2],
            'ports': [{'id': key, 'pos': pos, 'face': face, 'purpose': purpose}
                      for key, pos, face, purpose in ports],
            'paths': [{'name': '前侧维护净空', 'min': [23, 2, 13], 'max': [29, 6, 16]}],
            'zones': [
                {'name': '进液缓冲', 'kind': 'buffer', 'min': [17, 0, 2], 'max': [35, 10, 12],
                 'pos': [26, 10, 8], 'role': '原液与介质接入', 'service_face': '前侧'},
                {'name': '三段稳定柱', 'kind': 'stabilizer', 'min': [17, 8, 17], 'max': [35, 60, 35],
                 'pos': [26, 58, 26], 'role': '分段处理与约束', 'service_face': '环周'},
                {'name': '三面冷却翼架', 'kind': 'cooling', 'min': [2, 2, 19], 'max': [50, 52, 47],
                 'pos': [7, 40, 26], 'role': '冷却与换热', 'service_face': '外侧'},
                {'name': '出液与回流柜', 'kind': 'return', 'min': [37, 0, 36], 'max': [47, 9, 45],
                 'pos': [42, 9, 41], 'role': '稳定液输出与介质回流', 'service_face': '后侧'}],
            'links': [], 'brief': brief,
            'description': '三段八角稳定腔逐层收窄，顶部约束冠收束能量；三面错高冷却翼架通过分层管道连到处理腔，前方双缓冲罐与后方回流柜组成低位液路。',
            'role_materials': {k: sorted(v) for k, v in a.roles.items()},
            'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    size_audit = require(data)
    counts = collections.Counter(b['state'] for b in data['blocks'])
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
    audit = {'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
             'instance': str(TEST_INSTANCE), 'palette': dict(counts), 'hashes': hashes,
             'actual_bounds_xyz': [[min(b['pos'][i] for b in data['blocks']), max(b['pos'][i] for b in data['blocks'])] for i in range(3)],
             'size_baseline': size_audit, 'port_placeholder': 'hk3gtl:industrial_port_casing',
             'project_assets_saved': sorted(project_sources),
             'checks': ['正式名称保持液态崩坏能稳定塔', '测试包实际完整立方体模型与纹理解析', 'NBT与Sponge逐格导出回读'],
             'not_verified': ['待外观确认', '未接入正式Pattern与配方', '未实测浏览器交互与游戏运行', '生存材料可达性尚未核验']}
    meta = {k: v for k, v in data.items() if k != 'blocks'}
    payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (SOURCE / 'i04/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('实体草稿01', '自由设计候选').replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace('hk3gtl-i04-redesign-01', data['name'])
    page = re.sub(r'\d+×\d+×\d+（宽×长×高） · [\d,]+个实体', f'53×49×61（宽×长×高） · {len(data["blocks"]):,}个实体', page)
    page = re.sub(r'id="layerValue">\d+', 'id="layerValue">60', page)
    page = re.sub(r'id="layer" type="range" min="0" max="\d+" value="\d+"', 'id="layer" type="range" min="0" max="60" value="60"', page)
    page = re.sub(r'(<summary>本机建筑概念</summary><p>).*?(</p>)', lambda m: m[1] + data['description'] + m[2], page)
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']), 'size': data['size'], 'palette': dict(counts)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
