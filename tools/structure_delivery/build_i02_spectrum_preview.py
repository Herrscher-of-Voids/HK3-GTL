# -*- coding: utf-8 -*-
"""Independent I02 sample-spectrum array appearance candidate."""
import base64
import collections
import datetime
import gzip
import json
import re
import shutil
from pathlib import Path

from build_i01_tidal_preview import SOURCE
from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I02_样本光谱分析阵列_自由设计预览'
TEST_INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'


def frame(a, x0, x1, y, z0, z1, material):
    for start, end in (
        ((x0, y, z0), (x1, y, z0)),
        ((x0, y, z1), (x1, y, z1)),
        ((x0, y, z0), (x0, y, z1)),
        ((x1, y, z0), (x1, y, z1)),
    ):
        a.line(start, end, material)


def build():
    brief = {'id': 'I02', 'title': '样本光谱分析阵列',
             'minimum_wdh': [63, 57, 28]}
    a = Build(brief)
    dark = 'gtlcore:iridium_casing'
    steel = 'gtlcore:process_machine_casing'
    bronze = 'gtceu:high_power_casing'
    pipe = 'gtceu:tungstensteel_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    computer = 'gtceu:advanced_computer_casing'
    glass = 'gtceu:fusion_glass'
    violet = 'gtlcore:rhenium_reinforced_energy_glass'
    cyan = 'gtlcore:hsss_reinforced_borosilicate_glass'

    # An open optical spine is supported by two separated service rails.
    for x0, x1 in ((19, 24), (38, 43)):
        a.box((x0, 0, 3), (x1, 1, 53), dark)
        for z in range(6, 53, 7):
            a.box((x0, 2, z), (x1, 5, z + 1), steel)
            a.box((x0, 6, z), (x1, 6, z + 1), bronze)
        a.box((x0, 7, 7), (x1, 7, 51), pipe)
    for z in (8, 15, 22, 41, 49):
        a.box((24, 1, z), (38, 2, z + 2), dark)
        a.box((26, 3, z), (36, 3, z + 2), steel)

    # The sample lock is deliberately lower than the central prism chamber.
    a.box((25, 0, 5), (37, 1, 20), dark)
    for y in (3, 4, 10, 11):
        frame(a, 25, 37, y, 8, 18, bronze if y in (3, 11) else steel)
    for y in range(5, 10):
        for x in (25, 37):
            a.line((x, y, 8), (x, y, 18), glass)
        a.line((26, y, 18), (36, y, 18), glass)
    a.box((29, 5, 10), (33, 7, 14), violet, True)
    a.box((28, 2, 16), (34, 4, 18), computer, True)
    a.line((31, 7, 18), (31, 13, 25), pipe)

    # The central chamber is a faceted prism carried by four compact feet.
    for x in (23, 39):
        for z in (24, 38):
            a.box((x, 0, z), (x + 1, 8, z + 1), dark)
            a.box((x - 1, 8, z - 1), (x + 2, 9, z + 2), bronze)
    for y, inset in ((10, 3), (11, 2), (12, 1), (13, 0),
                     (14, 0), (15, 0), (16, 1), (17, 2), (18, 3)):
        material = dark if y in (10, 18) else glass
        frame(a, 23 + inset, 40 - inset, y, 23 + inset, 39 - inset, material)
    for y in range(11, 18):
        a.line((31, y, 25), (31, y, 37), violet if y % 3 == 0 else cyan)
    for z in (25, 30, 37):
        a.box((28, 11, z), (34, 11, z), bronze)
    for x in (24, 39):
        a.line((x, 13, 25), (x, 13, 37), steel)

    # Four splayed detector wings translate the split spectrum into a wide profile.
    detectors = ((10, 21), (5, 40), (52, 21), (57, 40))
    for cx, cz in detectors:
        edge = 23 if cx < 31 else 40
        a.line((edge, 14, 31), (cx, 12, cz), pipe)
        a.line((edge, 16, 31), (cx, 19, cz), bronze)
        a.box((cx - 4, 0, cz - 5), (cx + 4, 1, cz + 5), dark)
        a.box((cx - 3, 2, cz - 4), (cx + 3, 4, cz + 4), steel, True)
        for y in (5, 12, 19, 20):
            frame(a, cx - 3, cx + 3, y, cz - 4, cz + 4, bronze)
        for y in range(6, 19):
            a.line((cx - 2, y, cz - 3), (cx - 2, y, cz + 3), glass)
            a.line((cx + 2, y, cz - 3), (cx + 2, y, cz + 3), glass)
            a.set(cx, y, cz, cyan if cx < 31 else violet)
        for z in (cz - 3, cz, cz + 3):
            a.box((cx - 3, 21, z), (cx + 3, 21, z), vent)
        a.set(cx, 4, cz - 4, 'hk3gtl:industrial_port_casing')

    # Rear calibration source and data racks close the visible optical path.
    a.box((24, 0, 45), (38, 1, 56), dark)
    for y in (2, 10, 18):
        frame(a, 24, 38, y, 47, 56, steel)
    for x in (25, 28, 34, 37):
        a.box((x, 3, 55), (x, 17, 56), computer)
        for y in (5, 8, 11, 14):
            a.box((x, y, 54), (x, y, 54), vent)
    a.box((28, 8, 47), (34, 15, 51), glass, True)
    a.box((30, 10, 48), (32, 13, 50), violet)
    a.line((31, 13, 39), (31, 13, 48), pipe)

    # A raised pair of broken light baffles, not a roof, marks the analysis axis.
    for z in (13, 25, 38, 49):
        for x in (20, 42):
            a.box((x, 8, z), (x, 25, z + 1), dark)
            a.box((x - 1, 21, z), (x + 1, 21, z + 1), bronze)
        a.line((20, 25, z), (26, 27, z), steel)
        a.line((36, 27, z), (42, 25, z), steel)
        a.box((26, 27, z), (29, 27, z + 1), glass)
        a.box((33, 27, z), (36, 27, z + 1), glass)

    a.box((27, 0, 0), (35, 1, 5), dark)
    a.box((27, 2, 1), (35, 4, 1), steel, True)
    a.set(31, 4, 1, 'gtlcore:advanced_stellar_containment_casing')
    for x in (28, 34):
        a.set(x, 4, 1, 'hk3gtl:industrial_port_casing')
    a.set(31, 4, 55, 'hk3gtl:industrial_port_casing')

    return {
        'key': 'i02', 'name': 'i02-spectrum-array-free', 'title': brief['title'],
        'size': [63, 28, 57], 'controller': [31, 4, 1],
        'ports': [
            {'id': 'S-IN', 'pos': [28, 4, 1], 'face': 'north', 'purpose': '样本输入候选'},
            {'id': 'S-OUT', 'pos': [34, 4, 1], 'face': 'north', 'purpose': '报告输出候选'},
            {'id': 'CAL', 'pos': [31, 4, 55], 'face': 'south', 'purpose': '基准源与校验接口候选'},
            *[{'id': f'D-{i}', 'pos': [x, 4, z - 4],
               'face': 'north', 'purpose': '分波探测翼接口候选'}
              for i, (x, z) in enumerate(detectors, 1)],
        ],
        'paths': [{'name': '中央检修通道', 'min': [27, 2, 19], 'max': [35, 7, 22]}],
        'zones': [
            {'name': '前部进样锁', 'kind': 'sample', 'min': [25, 0, 5],
             'max': [37, 11, 20], 'pos': [31, 10, 13], 'role': '样本输入', 'service_face': '前侧'},
            {'name': '中央棱镜腔', 'kind': 'prism', 'min': [23, 8, 23],
             'max': [40, 18, 39], 'pos': [31, 18, 31], 'role': '光谱分解', 'service_face': '四侧'},
            {'name': '四片分波探测翼', 'kind': 'detector', 'min': [1, 0, 16],
             'max': [61, 21, 45], 'pos': [10, 19, 21], 'role': '光谱探测', 'service_face': '外侧'},
            {'name': '后部基准源与记录柜', 'kind': 'archive', 'min': [24, 0, 45],
             'max': [38, 18, 56], 'pos': [31, 18, 52], 'role': '校准与记录', 'service_face': '后侧'},
        ],
        'links': [],
        'description': '前部进样锁与后部基准源沿纵向光路相对，中央棱镜腔把光谱分至四片外展探测翼；维护通道与分析轴分开。',
        'brief': brief, 'role_materials': {key: sorted(value) for key, value in a.roles.items()},
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
    }


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
    bounds = [[min(b['pos'][i] for b in data['blocks']),
               max(b['pos'][i] for b in data['blocks'])] for i in range(3)]
    audit = {
        'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'palette': dict(counts),
        'namespace_counts': {ns: sum(n for state, n in counts.items() if state.startswith(ns + ':'))
                             for ns in {s.split(':')[0] for s in counts}},
        'actual_bounds_xyz': bounds, 'hashes': hashes, 'size_baseline': size_audit,
        'port_placeholder': 'hk3gtl:industrial_port_casing', 'project_assets_saved': sorted(project_sources),
        'checks': ['正式名称保持样本光谱分析阵列', '完整立方体建材',
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
    page = (SOURCE / 'i02/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('实体草稿01', '自由设计候选')
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace('hk3gtl-i02-redesign-01', data['name'])
    page = page.replace('未实测浏览器交互或游戏', '待浏览器交互复核，尚未进行游戏测试')
    page = re.sub(r'\d+×\d+×\d+（宽×长×高） · [\d,]+个实体',
                  f'63×57×28（宽×长×高） · {len(data["blocks"]):,}个实体', page)
    page = re.sub(r'id="layerValue">\d+', 'id="layerValue">27', page)
    page = re.sub(r'id="layer" type="range" min="0" max="\d+" value="\d+"',
                  'id="layer" type="range" min="0" max="27" value="27"', page)
    page = re.sub(r'(<summary>本机建筑概念</summary><p>).*?(</p>)',
                  lambda match: match.group(1) + data['description'] + match.group(2), page)
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']),
                      'bounds': bounds, 'palette': dict(counts)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
