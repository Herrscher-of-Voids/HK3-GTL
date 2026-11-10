# -*- coding: utf-8 -*-
"""I01-1 开放式潮汐采集场外观候选；不接入游戏 Pattern。"""
import base64
import collections
import datetime
import gzip
import hashlib
import json
import shutil

from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I01-1_潮汐采集场_自由设计预览'
SOURCE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/69座重设计_实体预览01'


def build():
    brief = {'id': 'I01-1', 'title': '1阶崩坏能采集塔 · 液态', 'minimum_wdh': [31, 31, 35]}
    a = Build(brief)
    dark = 'gtceu:robust_machine_casing'
    bronze = 'gtceu:bronze_machine_casing'
    pipe = 'gtceu:steel_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    glass = 'gtceu:tempered_glass'
    energy = 'minecraft:purple_stained_glass'

    # 三个分离的锚台留下中央设备空间，支柱承托三角形采集框。
    anchors = [(5, 5), (25, 5), (15, 27)]
    for cx, cz in anchors:
        a.box((cx - 3, 0, cz - 3), (cx + 3, 1, cz + 3), dark)
        a.box((cx - 2, 2, cz - 2), (cx + 2, 3, cz + 2), bronze, True)
        for y in range(4, 28):
            a.box((cx - 1, y, cz - 1), (cx + 1, y, cz + 1), dark, True)
            if y in (10, 18, 26):
                a.box((cx - 2, y, cz - 2), (cx + 2, y, cz + 2), bronze, True)
        a.box((cx - 1, 28, cz - 1), (cx + 1, 29, cz + 1), bronze)
        a.set(cx, 30, cz, energy)
    for i, p in enumerate(anchors):
        q = anchors[(i + 1) % 3]
        a.line((p[0], 28, p[1]), (q[0], 28, q[1]), dark)
        a.line((p[0], 29, p[1]), (q[0], 29, q[1]), bronze)

    # 三条斜向集流臂汇入高处的开放式收束腔。
    for cx, cz in anchors:
        a.line((cx, 25, cz), (15, 32, 14), pipe)
    for y, radius in ((29, 4), (30, 5), (31, 5), (32, 4), (33, 3)):
        a.ring((15, y, 14), radius, radius, bronze if y in (29, 33) else dark)
    a.box((14, 29, 13), (16, 33, 15), energy, True)
    a.set(15, 34, 14, glass)

    # 中央透明处理腔悬在支撑架内，液态能量沿内管向下回流。
    for y in range(9, 23):
        radius = 5 if 12 <= y <= 19 else 4
        a.ring((15, y, 15), radius, radius,
               bronze if y in (9, 12, 19, 22) else glass)
        a.set(15, y, 15, pipe if y in (9, 22) else energy)
    for x, z in ((11, 15), (19, 15), (15, 11), (15, 19)):
        a.box((x, 5, z), (x, 9, z), dark)
    a.box((10, 3, 10), (20, 4, 20), dark, True)
    a.box((12, 5, 12), (18, 5, 18), bronze, True)

    # 两只低位冷凝机组只通过实际可见的回流干管连接中央处理腔。
    for x0, x1 in ((0, 8), (22, 30)):
        a.box((x0, 0, 15), (x1, 1, 25), dark)
        a.box((x0 + 1, 2, 16), (x1 - 1, 9, 24), dark, True)
        a.box((x0 + 2, 4, 16), (x1 - 2, 7, 16), glass)
        a.box((x0 + 2, 5, 16), (x1 - 2, 6, 16), energy)
        for z in (17, 19, 21, 23):
            a.box((x0 + 1, 10, z), (x1 - 1, 10, z), vent)
        a.line((x1 if x0 == 0 else x0, 7, 19), (15, 7, 19), pipe)
    a.box((12, 0, 0), (18, 1, 10), dark)
    a.box((13, 2, 1), (17, 2, 9), bronze)
    a.box((13, 3, 1), (17, 5, 1), dark, True)
    a.set(15, 4, 1, 'minecraft:diamond_block')
    port_positions = [(13, 4, 1), (17, 4, 1), (1, 4, 20), (29, 4, 20)]
    for pos in port_positions:
        a.set(*pos, 'hk3gtl:industrial_port_casing')

    zones = [
        {'name': '三角采集框', 'kind': 'collector', 'min': [2, 4, 2], 'max': [28, 34, 30], 'pos': [15, 30, 14], 'role': '采集与汇流', 'service_face': '外侧'},
        {'name': '透明处理腔', 'kind': 'chamber', 'min': [10, 9, 10], 'max': [20, 22, 20], 'pos': [15, 20, 15], 'role': '液态崩坏能处理', 'service_face': '环形维护区'},
        {'name': '左冷凝机组', 'kind': 'condenser', 'min': [0, 0, 15], 'max': [8, 10, 25], 'pos': [4, 9, 20], 'role': '冷凝', 'service_face': '西侧'},
        {'name': '右冷凝机组', 'kind': 'condenser', 'min': [22, 0, 15], 'max': [30, 10, 25], 'pos': [26, 9, 20], 'role': '冷凝', 'service_face': '东侧'},
    ]
    links = [
        {'from': '三角采集框', 'to': '透明处理腔', 'material': pipe, 'route': [[15, 32, 14], [15, 22, 15]]},
        {'from': '透明处理腔', 'to': '左冷凝机组', 'material': pipe, 'route': [[15, 7, 19], [8, 7, 19]]},
        {'from': '透明处理腔', 'to': '右冷凝机组', 'material': pipe, 'route': [[15, 7, 19], [22, 7, 19]]},
    ]
    controller = [15, 4, 1]
    preserved = [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())
                 if list(pos) != controller]
    fingerprint = hashlib.sha256(json.dumps(preserved, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
    return {
        'key': 'i01-1', 'name': 'i01-1-tidal-collector', 'title': brief['title'],
        'size': [31, 35, 31], 'controller': controller,
        'upgrade_contract': {
            'family': 'I01', 'stages': ['I01-1', 'I01-2', 'I01-3', 'I01-4'],
            'world_anchor': 'controller position', 'replaceable_positions': [controller],
            'rule': 'Every previous non-controller block keeps its world position and exact state; only the controller is replaced, and higher stages add blocks in empty space.',
            'preserved_blocks': len(preserved), 'preserved_sha256': fingerprint,
            'next_stages_verified': [],
        },
        'ports': [{'id': str(i + 1), 'pos': list(pos),
                   'face': 'north' if pos[2] == 1 else ('west' if pos[0] < 15 else 'east'),
                   'purpose': '接口候选；具体能力待正式机器定义'}
                  for i, pos in enumerate(port_positions)],
        'paths': [{'name': '前侧检修道', 'min': [13, 3, 2], 'max': [17, 6, 9]}],
        'zones': zones, 'links': links, 'description': '三座外缘锚塔以斜向集流臂围成开放采集场，中央透明处理腔向两侧冷凝机组回流。',
        'brief': brief, 'role_materials': {k: sorted(v) for k, v in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    size_audit = require(data)
    bounds = [[min(b['pos'][axis] for b in data['blocks']), max(b['pos'][axis] for b in data['blocks'])]
              for axis in range(3)]
    assert bounds == [[0, 30], [0, 34], [0, 30]], bounds
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
        'actual_bounds_xyz': bounds, 'hashes': hashes, 'size_baseline': size_audit,
        'port_placeholder': 'hk3gtl:industrial_port_casing', 'project_assets_saved': sorted(project_sources),
        'checks': ['实体包围盒31×31×35；不采用旧占地下限', 'NBT与Sponge逐格导出回读', '方块材质由本机资源解析',
                   '记录I01-1至I01-4原方块保留契约及控制器锚点'],
        'not_verified': ['未获外观确认', 'I01-2至I01-4尚未逐格验证', '未接入正式Pattern或配方', '未进行游戏成型与运行测试', '生存获取阶段尚未核验'],
    }
    meta = {k: v for k, v in data.items() if k != 'blocks'}
    payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (SOURCE / 'i01-1/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('实体草稿01', '自由设计候选')
    page = page.replace('17×17×33', '31×31×35').replace('1,123个实体', f'{len(data["blocks"]):,}个实体')
    page = page.replace('id="layerValue">32', 'id="layerValue">34')
    page = page.replace('id="layer" type="range" min="0" max="32" value="32"',
                        'id="layer" type="range" min="0" max="34" value="34"')
    page = page.replace('竖向采集桅杆与低位冷凝肩舱；集流头经竖直干管落入侧置冷凝腔，检修道从另一侧绕柱到达仪表座', data['description'])
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('hk3gtl-i01-1-redesign-01', data['name'])
    page = page.replace('未实测浏览器交互或游戏', '浏览器交互已测试，尚未进行游戏测试')
    page = page.replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace('i01-1-redesign-01.nbt', data['name'] + '.nbt')
    page = page.replace('i01-1-redesign-01.schem', data['name'] + '.schem')
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']), 'palette': dict(counts), 'bounds': bounds}, ensure_ascii=False))


if __name__ == '__main__':
    main()
