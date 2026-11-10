# -*- coding: utf-8 -*-
"""I01-1 天命工业采集塔独立外观候选；不接入游戏 Pattern。"""
import base64
import collections
import datetime
import gzip
import json
import shutil
from pathlib import Path

from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import Build, ROOT


OUT = ROOT / 'deliveries/I01-1_天命工业采集塔_自由造型预览_v3'
SOURCE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/69座重设计_实体预览01'
BRIEFS = ROOT / 'logs/structure-redesign-20260928/briefs69.json'


def build():
    brief = dict(next(b for b in json.loads(BRIEFS.read_text(encoding='utf-8'))['briefs'] if b['id'] == 'I01-1'))
    brief['minimum_wdh'] = [25, 27, 45]
    a = Build(brief)
    white = 'gtceu:clean_machine_casing'
    gray = 'gtceu:solid_machine_casing'
    duct = 'gtceu:steel_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    glass = 'gtceu:tempered_glass'
    violet = 'minecraft:purple_stained_glass'

    # 四个承重基座和可进入的中轴检修桥，不使用满铺底板填尺寸。
    for x0, x1 in ((0, 7), (17, 24)):
        for z0, z1 in ((0, 6), (20, 26)):
            a.box((x0, 0, z0), (x1, 1, z1), gray)
            a.box((x0 + 1, 2, z0 + 1), (x1 - 1, 3, z1 - 1), white, True)
    a.box((9, 0, 2), (15, 1, 24), gray)
    a.box((10, 2, 2), (14, 2, 24), white)
    for z in (5, 10, 16, 22):
        a.box((9, 2, z), (15, 2, z), vent)

    # 中央下降干管分为四段，正面观察窗贯穿；侧翼只在关键高度与塔体相连。
    for y in range(4, 38):
        inset = 1 if y >= 30 else 0
        x0, x1 = 8 + inset, 16 - inset
        z0, z1 = 9 + inset, 17 - inset
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):
                    a.set(x, y, z, gray if y in (4, 11, 20, 29, 37) else white)
        a.box((12, y, 13), (12, y, 13), duct)
        if y in (8, 9, 15, 16, 23, 24, 32, 33):
            a.box((11, y, z0), (13, y, z0), violet)
        if y in (11, 20, 29):
            a.box((x0 - 1, y, z0 - 1), (x1 + 1, y, z1 + 1), gray, True)

    # 顶部是三翼采集头，白色机械叶片包围收束于中心的紫色采集腔。
    for y, radius in ((38, 5), (39, 6), (40, 8), (41, 9)):
        a.box((12 - radius, y, 13), (12 + radius, y, 13), white)
        a.box((12, y, 13 - radius), (12, y, 13 + radius), white)
    for x0, x1 in ((2, 8), (16, 22)):
        a.box((x0, 39, 11), (x1, 39, 15), gray, True)
        a.box((x0, 40, 12), (x1, 40, 14), white, True)
        for x in range(x0 + 1, x1, 2):
            a.set(x, 40, 13, violet)
    for z0, z1 in ((2, 8), (18, 24)):
        a.box((10, 39, z0), (14, 39, z1), gray, True)
        a.box((11, 40, z0), (13, 40, z1), white, True)
    a.box((10, 42, 11), (14, 43, 15), glass, True)
    a.box((11, 44, 12), (13, 44, 14), gray)
    a.set(12, 44, 13, violet)

    # 双侧低位冷凝舱：可见紫色液态观察带、顶端散热排和回流管。
    for left in (True, False):
        x0, x1 = (1, 7) if left else (17, 23)
        a.box((x0, 4, 11), (x1, 17, 21), white, True)
        for y in (4, 10, 17):
            a.box((x0, y, 11), (x1, y, 21), gray, True)
        face = x0 if left else x1
        for y in range(7, 15):
            for z in (14, 15, 17, 18):
                a.set(face, y, z, violet if y in (9, 10, 11, 12) else glass)
        for z in (12, 15, 18, 21):
            a.box((x0, 18, z), (x1, 18, z), vent)
        a.box((x1 if left else x0, 12, 15), (12, 12, 15), duct)
        a.box((x1 if left else x0, 5, 18), (12, 5, 18), duct)
        a.box((x0 + 1, 2, 21), (x1 - 1, 4, 21), gray)

    # 冷凝舱上方的斜撑承托采集翼，塔身开窗后可直接看见输送芯。
    for x in (4, 20):
        a.line((x, 18, 15), (9 if x < 12 else 15, 29, 15), gray)
        a.line((x, 18, 16), (9 if x < 12 else 15, 29, 16), white)
    for y in range(21, 29):
        for x in range(10, 15):
            a.b.pop((x, y, 9), None)
        a.box((10, y, 10), (14, y, 10), glass)
        a.box((11, y, 11), (13, y, 11), violet)
    for x0, x1 in ((2, 4), (20, 22)):
        a.box((x0, 41, 11), (x1, 41, 15), gray, True)
        a.box((x0 + 1, 42, 12), (x1 - 1, 42, 14), white)
    for z0, z1 in ((2, 4), (22, 24)):
        a.box((10, 41, z0), (14, 41, z1), gray, True)
        a.box((11, 42, z0 + 1), (13, 42, z1 - 1), white)

    # 前侧单独控制台和检修入口，标记仅表示未来控制器及接口候选位置。
    a.box((8, 2, 1), (16, 5, 1), white, True)
    a.set(12, 3, 1, 'minecraft:diamond_block')
    port_positions = [(9, 3, 1), (10, 3, 1), (14, 3, 1), (15, 3, 1),
                      (2, 4, 20), (22, 4, 20)]
    for x, y, z in port_positions:
        a.set(x, y, z, 'minecraft:diamond_ore')

    a.zones = [
        {'name': '四翼采集头', 'kind': 'collector', 'min': [2, 38, 2], 'max': [22, 44, 24], 'pos': [12, 42, 13], 'role': '采集与约束', 'service_face': '塔顶'},
        {'name': '中央下降干管', 'kind': 'downpipe', 'min': [8, 4, 9], 'max': [16, 37, 17], 'pos': [12, 26, 13], 'role': '液态输送', 'service_face': '正面'},
        {'name': '左冷凝舱', 'kind': 'condenser', 'min': [1, 4, 11], 'max': [7, 18, 21], 'pos': [4, 17, 16], 'role': '冷凝', 'service_face': '西侧'},
        {'name': '右冷凝舱', 'kind': 'condenser', 'min': [17, 4, 11], 'max': [23, 18, 21], 'pos': [20, 17, 16], 'role': '冷凝', 'service_face': '东侧'},
    ]
    a.links = [
        {'from': '四翼采集头', 'to': '中央下降干管', 'material': duct, 'route': [[12, 41, 13], [12, 26, 13], [12, 12, 13]]},
        {'from': '中央下降干管', 'to': '左冷凝舱', 'material': duct, 'route': [[12, 12, 15], [7, 12, 15]]},
        {'from': '中央下降干管', 'to': '右冷凝舱', 'material': duct, 'route': [[12, 12, 15], [17, 12, 15]]},
    ]
    a.paths = [{'name': '前侧中央检修桥', 'min': [10, 3, 2], 'max': [14, 6, 8]}]
    return {
        'key': 'i01-1', 'name': 'i01-1-tianming-collector-v3',
        'title': brief['title'], 'size': [25, 45, 27], 'controller': [12, 3, 1],
        'ports': [{'id': str(i + 1), 'pos': list(pos),
                   'face': 'north' if pos[2] == 1 else ('west' if pos[0] < 12 else 'east'),
                   'purpose': '接口候选；正式类型与数量待机器定义确认'}
                  for i, pos in enumerate(port_positions)],
        'paths': a.paths, 'zones': a.zones, 'links': a.links,
        'description': '天命工业采集塔：四翼采集头、开窗输送芯、斜撑双冷凝舱和独立检修桥。',
        'brief': brief, 'role_materials': {k: sorted(v) for k, v in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    bounds = [[min(b['pos'][axis] for b in data['blocks']), max(b['pos'][axis] for b in data['blocks'])]
              for axis in range(3)]
    assert bounds == [[0, 24], [0, 44], [0, 26]], bounds
    counts = collections.Counter(b['state'] for b in data['blocks'])
    resources = Resources()
    try:
        materials = [resources.material(s) for s in sorted(counts)]
    finally:
        resources.close()
    states, groups, hashes = export(data, OUT)
    render(data, materials, OUT)
    audit = {
        'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'palette': dict(counts), 'namespace_counts': dict(collections.Counter({
            ns: sum(n for state, n in counts.items() if state.startswith(ns + ':'))
            for ns in {s.split(':')[0] for s in counts}
        })),
        'actual_bounds_xyz': bounds, 'hashes': hashes,
        'checks': ['实体包围盒为25×27×45，尺寸由本次造型决定', 'NBT与Sponge逐格导出回读', '完整方块模型与实际贴图解析'],
        'not_verified': ['外观候选尚未经用户视觉确认', '未接入正式Pattern、端口能力或配方', '未做游戏成型与运行测试', '生存获取阶段尚未核验'],
    }
    meta = {k: v for k, v in data.items() if k != 'blocks'}
    payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (SOURCE / 'i01-1/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"')
    page = page.replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('实体草稿01', '自由造型候选 v3')
    page = page.replace('17×17×33', '25×27×45')
    page = page.replace('id="layerValue">32', 'id="layerValue">44')
    page = page.replace('id="layer" type="range" min="0" max="32" value="32"',
                        'id="layer" type="range" min="0" max="44" value="44"')
    page = page.replace('1,123个实体', f'{len(data["blocks"]):,}个实体')
    page = page.replace('竖向采集桅杆与低位冷凝肩舱；集流头经竖直干管落入侧置冷凝腔，检修道从另一侧绕柱到达仪表座', data['description'])
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('hk3gtl-i01-1-redesign-01', data['name'])
    page = page.replace('未实测浏览器交互或游戏', '浏览器交互已测试，尚未进行游戏测试')
    page = page.replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']), 'palette': dict(counts), 'bounds': bounds}, ensure_ascii=False))


if __name__ == '__main__':
    main()
