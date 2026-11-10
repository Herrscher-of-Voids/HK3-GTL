# -*- coding: utf-8 -*-
"""I01-4 energy-state collector preview, extending all accepted lower stages."""
import base64
import collections
import datetime
import gzip
import json
import re
import shutil

from build_i01_stage2_preview import Extension
from build_i01_stage3_preview import build as build_stage3, square_frame
from build_i01_tidal_preview import SOURCE
from build_redesign69 import export, render
from check_i01_upgrade import check_upgrade
from material_resources import Resources
from redesign69_geometry import ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I01-4_4阶崩坏能采集塔_无拆除扩建预览'
SHIFT = (12, 0, 12)
CONTROLLER = [43, 4, 29]


def build():
    previous = build_stage3()
    inherited = {tuple(b['pos'][i] + SHIFT[i] for i in range(3)): b['state']
                 for b in previous['blocks']}
    brief = {'id': 'I01-4', 'title': '4阶崩坏能采集塔 · 能量态',
             'minimum_wdh': [87, 87, 88]}
    a = Extension(brief, inherited)
    dark = 'gtceu:robust_machine_casing'
    bronze = 'gtceu:bronze_machine_casing'
    steel = 'gtceu:steel_machine_casing'
    pipe = 'gtceu:steel_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    glass = 'gtceu:tempered_glass'
    energy = 'minecraft:purple_stained_glass'
    flash = 'minecraft:magenta_stained_glass'

    # Four new cardinal gantries stand outside the inherited 63x63 envelope.
    stations = ((43, 5), (81, 43), (43, 81), (5, 43))
    for cx, cz in stations:
        a.box((cx - 5, 0, cz - 5), (cx + 5, 1, cz + 5), dark)
        for y in (2, 13, 26, 39, 52, 63):
            square_frame(a, cx - 4, cx + 4, y, cz - 4, cz + 4, bronze)
            square_frame(a, cx - 4, cx + 4, y + 1, cz - 4, cz + 4, steel)
        for y in range(3, 69):
            for dx, dz in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
                a.set(cx + dx, y, cz + dz, steel)
            a.set(cx, y, cz, flash if y % 9 in (0, 1) else energy)
            if y % 8 == 0:
                for dx, dz in ((-4, 0), (4, 0), (0, -4), (0, 4)):
                    a.set(cx + dx, y, cz + dz, vent)
        for y in range(65, 70):
            square_frame(a, cx - 3, cx + 3, y, cz - 3, cz + 3, glass)
        a.box((cx - 3, 70, cz - 3), (cx + 3, 71, cz + 3), dark)
        a.set(cx, 4, cz, 'hk3gtl:industrial_port_casing')

    # Two separated circular collectors leave the stage-three square crown visible.
    for y, radius, material in ((68, 35, dark), (69, 36, bronze),
                                (70, 36, glass), (71, 35, steel),
                                (76, 27, steel), (77, 28, glass)):
        a.ring((43, y, 43), radius, radius, material)
    for cx, cz in stations:
        a.line((cx, 70, cz), (43, 78, 43), pipe)
        a.line((cx, 37, cz), (43, 49, 43), pipe)

    # A faceted suspended core reads as an energy-state apparatus, not a solid roof.
    for y, radius in ((72, 8), (73, 10), (74, 12), (75, 13),
                      (76, 14), (77, 14), (78, 13), (79, 12),
                      (80, 10), (81, 8)):
        a.ring((43, y, 43), radius, radius,
               dark if y in (72, 81) else (glass if y % 2 else bronze))
    for y in range(72, 86):
        a.box((42, y, 42), (44, y, 44), flash if y % 3 == 0 else energy, True)
    for y, radius in ((82, 6), (83, 7), (84, 7), (85, 5)):
        a.ring((43, y, 43), radius, radius, glass if y in (83, 84) else steel)
    a.set(43, 87, 43, glass)

    additions = dict(a.b)
    blocks = dict(inherited)
    blocks.update(additions)
    errors = check_upgrade(inherited, CONTROLLER, blocks, CONTROLLER)
    assert not errors, errors[:5]
    old_ports = [{**port, 'pos': [port['pos'][i] + SHIFT[i] for i in range(3)]}
                 for port in previous['ports']]
    new_ports = [{'id': f'E-{index}', 'pos': [cx, 4, cz],
                  'face': face, 'purpose': '能量态约束门架接口候选'}
                 for index, ((cx, cz), face) in enumerate(zip(
                     stations, ('north', 'east', 'south', 'west')), 1)]
    return {
        'key': 'i01-4', 'name': 'i01-4-energy-collector', 'title': brief['title'],
        'size': [87, 88, 87], 'controller': CONTROLLER,
        'upgrade_contract': {
            'family': 'I01', 'from': 'I01-3', 'previous_controller': CONTROLLER,
            'inherited_non_controller_blocks': len(inherited) - 1,
            'new_blocks': len(additions), 'unchanged_previous_blocks': True,
            'paste_alignment': 'Align I01-4 controller with the existing I01-3 controller in world coordinates.',
        },
        'ports': old_ports + new_ports,
        'paths': [{'name': '原前侧检修道', 'min': [41, 3, 30], 'max': [45, 6, 37]}],
        'zones': [
            {'name': '一至三阶既有采集结构', 'kind': 'inherited',
             'min': [12, 0, 12], 'max': [74, 63, 74], 'pos': [43, 40, 43],
             'role': '液态、固态与气态采集基础', 'service_face': '原有接口'},
            {'name': '四向能量约束门架', 'kind': 'gantry',
             'min': [0, 0, 0], 'max': [86, 71, 86], 'pos': [43, 55, 5],
             'role': '能量态收束与输送', 'service_face': '外侧'},
            {'name': '悬置能量核心', 'kind': 'collector',
             'min': [29, 68, 29], 'max': [57, 87, 57], 'pos': [43, 80, 43],
             'role': '高位约束与转换', 'service_face': '四向门架'},
        ],
        'links': [],
        'description': '在前三阶采集结构外围新建四向能量门架，并在原气态冠架上方悬置能量核心；旧结构按原位置完整保留。',
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
        'palette': dict(counts),
        'namespace_counts': {ns: sum(n for state, n in counts.items() if state.startswith(ns + ':'))
                             for ns in {s.split(':')[0] for s in counts}},
        'actual_bounds_xyz': [[min(b['pos'][i] for b in data['blocks']),
                               max(b['pos'][i] for b in data['blocks'])] for i in range(3)],
        'hashes': hashes, 'size_baseline': size_audit,
        'port_placeholder': 'hk3gtl:industrial_port_casing', 'project_assets_saved': sorted(project_sources),
        'checks': [f'三阶{data["upgrade_contract"]["inherited_non_controller_blocks"]}个非控制器方块按控制器锚点逐格保留',
                   'NBT与Sponge逐格导出回读', '新增机组未覆盖旧结构'],
        'not_verified': ['未获外观确认', '未接入正式Pattern或配方',
                         '未进行游戏成型与运行测试', '生存获取阶段尚未核验'],
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
    page = (SOURCE / 'i01-4/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('实体草稿01', '自由设计候选')
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace('hk3gtl-i01-4-redesign-01', data['name'])
    page = page.replace('未实测浏览器交互或游戏', '待浏览器交互复核，尚未进行游戏测试')
    page = re.sub(r'\d+×\d+×\d+（宽×长×高） · [\d,]+个实体',
                  f'87×87×88（宽×长×高） · {len(data["blocks"]):,}个实体', page)
    page = re.sub(r'id="layerValue">\d+', 'id="layerValue">87', page)
    page = re.sub(r'id="layer" type="range" min="0" max="\d+" value="\d+"',
                  'id="layer" type="range" min="0" max="87" value="87"', page)
    page = re.sub(r'(<summary>本机建筑概念</summary><p>).*?(</p>)',
                  lambda match: match.group(1) + data['description'] + match.group(2), page)
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']),
                      'new_blocks': data['upgrade_contract']['new_blocks'],
                      'skipped_overlaps': data['skipped_overlaps'],
                      'bounds': audit['actual_bounds_xyz']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
