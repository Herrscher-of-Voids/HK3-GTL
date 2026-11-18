# -*- coding: utf-8 -*-
"""I01-3 gas-state collector preview, extending the accepted first two stages."""
import base64
import collections
import datetime
import gzip
import json
import shutil

from build_i01_stage2_preview import Extension, build as build_stage2
from build_i01_tidal_preview import SOURCE
from build_redesign69 import export, render
from check_i01_upgrade import check_upgrade
from material_resources import Resources
from redesign69_geometry import ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I01-3_3阶崩坏能采集塔_无拆除扩建预览'
SHIFT = (8, 0, 8)
CONTROLLER = [31, 4, 17]


def square_frame(building, x0, x1, y, z0, z1, material):
    for start, end in (
        ((x0, y, z0), (x1, y, z0)),
        ((x0, y, z1), (x1, y, z1)),
        ((x0, y, z0), (x0, y, z1)),
        ((x1, y, z0), (x1, y, z1)),
    ):
        building.line(start, end, material)


def build():
    previous = build_stage2()
    inherited = {tuple(b['pos'][i] + SHIFT[i] for i in range(3)): b['state']
                 for b in previous['blocks']}
    brief = {'id': 'I01-3', 'title': '3阶崩坏能采集塔 · 气态',
             'minimum_wdh': [63, 63, 64]}
    a = Extension(brief, inherited)
    dark = 'gtceu:robust_machine_casing'
    bronze = 'gtceu:bronze_machine_casing'
    steel = 'gtceu:steel_machine_casing'
    pipe = 'gtceu:steel_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    glass = 'gtceu:tempered_glass'
    gas = 'minecraft:cyan_stained_glass'

    # The four gas separators occupy new diagonal ground, clear of old ports.
    corners = ((5, 5), (57, 5), (5, 57), (57, 57))
    for cx, cz in corners:
        a.box((cx - 4, 0, cz - 4), (cx + 4, 1, cz + 4), dark)
        for y in (2, 10, 20, 31, 43):
            for level in (y, y + 1):
                square_frame(a, cx - 3, cx + 3, level, cz - 3, cz + 3, bronze)
        for y in range(3, 48):
            square_frame(a, cx - 2, cx + 2, y, cz - 2, cz + 2, glass)
            a.set(cx, y, cz, gas if y % 5 else pipe)
            if y % 7 == 0:
                for dx, dz in ((-3, 0), (3, 0), (0, -3), (0, 3)):
                    a.set(cx + dx, y, cz + dz, vent)
        a.box((cx - 2, 48, cz - 2), (cx + 2, 49, cz + 2), steel)
        a.set(cx, 50, cz, glass)
        a.set(cx, 4, cz - (3 if cz < 31 else -3), 'hk3gtl:industrial_port_casing')

    # Upper circulation crown is a four-sided route, not another concentric hoop.
    for y, radius, material in ((49, 24, steel), (50, 25, dark),
                                (51, 25, bronze), (52, 24, steel)):
        square_frame(a, 31 - radius, 31 + radius, y,
                     31 - radius, 31 + radius, material)
    for cx, cz in corners:
        a.line((cx, 49, cz), (31, 55, 31), pipe)
        a.line((cx, 14, cz), (31, 17, 31), pipe)
    for y, radius in ((53, 8), (54, 9), (55, 9), (56, 8), (57, 6)):
        a.ring((31, y, 31), radius, radius, steel if y in (53, 57) else glass)
    for y in range(52, 62):
        a.box((30, y, 30), (32, y, 32), gas, True)
    a.box((29, 62, 29), (33, 62, 33), bronze, True)
    a.set(31, 63, 31, glass)

    # Elevated radial ducts join the separators to the circulation crown.
    for cx, cz in corners:
        inner_x = 31 + (19 if cx > 31 else -19)
        inner_z = 31 + (19 if cz > 31 else -19)
        a.line((cx, 39, cz), (inner_x, 49, inner_z), pipe)

    additions = dict(a.b)
    blocks = dict(inherited)
    blocks.update(additions)
    errors = check_upgrade(inherited, CONTROLLER, blocks, CONTROLLER)
    assert not errors, errors[:5]
    old_ports = [{**port, 'pos': [port['pos'][i] + SHIFT[i] for i in range(3)]}
                 for port in previous['ports']]
    new_ports = [
        {'id': f'G-{index}', 'pos': [cx, 4, cz - (3 if cz < 31 else -3)],
         'face': 'north' if cz < 31 else 'south', 'purpose': '气态分离机组接口候选'}
        for index, (cx, cz) in enumerate(corners, 1)
    ]
    zones = [
        {'name': '一、二阶既有采集结构', 'kind': 'inherited', 'min': [8, 0, 8], 'max': [54, 47, 54],
         'pos': [31, 26, 31], 'role': '液态与固态采集基础', 'service_face': '原有接口'},
        {'name': '四角气态分离塔', 'kind': 'separator', 'min': [1, 0, 1], 'max': [61, 50, 61],
         'pos': [5, 35, 5], 'role': '气态分离与上送', 'service_face': '外侧'},
        {'name': '高位循环冠架', 'kind': 'collector', 'min': [6, 49, 6], 'max': [56, 63, 56],
         'pos': [31, 55, 31], 'role': '气态收束与循环', 'service_face': '外侧'},
    ]
    return {
        'key': 'i01-3', 'name': 'i01-3-gas-collector', 'title': brief['title'],
        'size': [63, 64, 63], 'controller': CONTROLLER,
        'upgrade_contract': {
            'family': 'I01', 'from': 'I01-2', 'previous_controller': CONTROLLER,
            'inherited_non_controller_blocks': len(inherited) - 1,
            'new_blocks': len(additions), 'unchanged_previous_blocks': True,
            'paste_alignment': 'Align I01-3 controller with the existing I01-2 controller in world coordinates.',
            'next_stages_verified': [],
        },
        'ports': old_ports + new_ports,
        'paths': [{'name': '原前侧检修道', 'min': [29, 3, 18], 'max': [33, 6, 25]}],
        'zones': zones, 'links': [],
        'description': '在原有液态与固态采集结构外侧增设四座气态分离塔，上方构成开放循环冠架；旧结构原位保留。',
        'brief': brief,
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(blocks.items())],
        'skipped_overlaps': a.skipped_overlaps,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    size_audit = require(data)
    counts = collections.Counter(b['state'] for b in data['blocks'])
    resources = Resources(project_resources=ROOT / 'src/main/resources')
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
    audit = {
        'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'palette': dict(counts), 'namespace_counts': {
            ns: sum(n for state, n in counts.items() if state.startswith(ns + ':'))
            for ns in {s.split(':')[0] for s in counts}},
        'actual_bounds_xyz': [[min(b['pos'][i] for b in data['blocks']), max(b['pos'][i] for b in data['blocks'])]
                              for i in range(3)],
        'hashes': hashes, 'size_baseline': size_audit,
        'port_placeholder': 'hk3gtl:industrial_port_casing', 'project_assets_saved': sorted(project_sources),
        'checks': [f'二阶{len(data["blocks"])-data["upgrade_contract"]["new_blocks"]-1}个非控制器方块按控制器锚点逐格保留',
                   'NBT与Sponge逐格导出回读', '新增机组未覆盖旧结构'],
        'not_verified': ['未获外观确认', '未接入正式Pattern或配方', '未进行游戏成型与运行测试', '生存获取阶段尚未核验'],
    }
    meta = {k: v for k, v in data.items() if k != 'blocks'}
    payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (SOURCE / 'i01-3/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('实体草稿01', '自由设计候选')
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace('hk3gtl-i01-3-redesign-01.nbt', data['name'] + '.nbt')
    page = page.replace('hk3gtl-i01-3-redesign-01.schem', data['name'] + '.schem')
    page = page.replace('未实测浏览器交互或游戏', '待浏览器交互复核，尚未进行游戏测试')
    page = page.replace('hk3gtl-i01-3-redesign-01', data['name'])
    import re
    page = re.sub(r'\d+×\d+×\d+（宽×长×高） · [\d,]+个实体',
                  f'63×63×64（宽×长×高） · {len(data["blocks"]):,}个实体', page)
    page = re.sub(r'id="layerValue">\d+', 'id="layerValue">63', page)
    page = re.sub(r'id="layer" type="range" min="0" max="\d+" value="\d+"',
                  'id="layer" type="range" min="0" max="63" value="63"', page)
    page = re.sub(r'(<summary>本机建筑概念</summary><p>).*?(</p>)',
                  lambda match: match.group(1) + data['description'] + match.group(2), page)
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']),
                      'new_blocks': data['upgrade_contract']['new_blocks'],
                      'skipped_overlaps': data['skipped_overlaps'], 'bounds': audit['actual_bounds_xyz']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
