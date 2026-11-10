# -*- coding: utf-8 -*-
"""I01-2 solid-state collector preview built around the accepted I01-1."""
import base64
import collections
import datetime
import gzip
import json
import shutil

from build_i01_tidal_preview import SOURCE, build as build_stage1
from build_redesign69 import export, render
from check_i01_upgrade import check_upgrade
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I01-2_2阶崩坏能采集塔_无拆除扩建预览'
SHIFT = (8, 0, 8)
CONTROLLER = [23, 4, 9]


class Extension(Build):
    def __init__(self, brief, inherited):
        super().__init__(brief)
        self.inherited = inherited
        self.skipped_overlaps = 0

    def set(self, x, y, z, material):
        pos = (round(x), round(y), round(z))
        if pos in self.inherited:
            self.skipped_overlaps += 1
            return
        super().set(*pos, material)


def build():
    first = build_stage1()
    inherited = {tuple(b['pos'][i] + SHIFT[i] for i in range(3)): b['state']
                 for b in first['blocks']}
    brief = {'id': 'I01-2', 'title': '2阶崩坏能采集塔 · 固态',
             'minimum_wdh': [47, 47, 48]}
    a = Extension(brief, inherited)
    dark = 'gtceu:robust_machine_casing'
    bronze = 'gtceu:bronze_machine_casing'
    steel = 'gtceu:steel_machine_casing'
    pipe = 'gtceu:steel_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    glass = 'gtceu:tempered_glass'
    energy = 'minecraft:purple_stained_glass'

    # Three external crystallizers are outside the old 31x31 footprint.
    for direction in ('west', 'east', 'south'):
        if direction == 'west':
            x0, x1, z0, z1 = 0, 6, 17, 29
            cx, cz = 3, 23
        elif direction == 'east':
            x0, x1, z0, z1 = 40, 46, 17, 29
            cx, cz = 43, 23
        else:
            x0, x1, z0, z1 = 17, 29, 40, 46
            cx, cz = 23, 43
        a.box((x0, 0, z0), (x1, 1, z1), dark)
        a.box((x0 + 1, 2, z0 + 1), (x1 - 1, 12, z1 - 1), steel, True)
        a.box((x0 + 1, 5, z0 + 1), (x1 - 1, 10, z1 - 1), glass, True)
        a.box((cx - 1, 6, cz - 1), (cx + 1, 9, cz + 1), energy, True)
        for y in (3, 11, 13):
            a.box((x0, y, z0), (x1, y, z1), bronze, True)
        for y in range(14, 38):
            a.box((cx - 1, y, cz - 1), (cx + 1, y, cz + 1), dark, True)
            if y in (21, 29, 37):
                a.box((cx - 2, y, cz - 2), (cx + 2, y, cz + 2), steel, True)
        a.box((cx - 1, 38, cz - 1), (cx + 1, 39, cz + 1), bronze)
        a.set(cx, 40, cz, glass)
        a.set(cx, 4, cz, 'hk3gtl:industrial_port_casing')

    # Raised containment hoop and three radial transfer routes.
    for y, radius, material in ((37, 17, dark), (38, 18, steel),
                                (39, 18, bronze), (40, 17, dark)):
        a.ring((23, y, 23), radius, radius, material)
    for x, z in ((3, 23), (43, 23), (23, 43)):
        a.line((x, 38, z), (23, 41, 23), pipe)
        a.line((x, 7, z), (23, 7, 23), pipe)
    for y, radius in ((40, 5), (41, 6), (42, 6), (43, 5)):
        a.ring((23, y, 23), radius, radius, glass if y in (41, 42) else bronze)
    a.box((22, 40, 22), (24, 46, 24), energy, True)
    a.set(23, 47, 23, glass)

    # Thin outer handling arms show where the new crystallizers feed the old core.
    for x0, x1, z0, z1 in ((6, 8, 21, 25), (38, 40, 21, 25), (21, 25, 38, 40)):
        a.box((x0, 2, z0), (x1, 3, z1), dark)
        a.box((x0, 4, z0), (x1, 4, z1), bronze, True)
        a.box((x0, 5, z0), (x1, 5, z1), vent, True)

    additions = dict(a.b)
    blocks = dict(inherited)
    blocks.update(additions)
    errors = check_upgrade(inherited, CONTROLLER, blocks, CONTROLLER)
    assert not errors, errors[:5]
    old_ports = [{**port, 'pos': [port['pos'][i] + SHIFT[i] for i in range(3)]}
                 for port in first['ports']]
    new_ports = [
        {'id': 'C-W', 'pos': [3, 4, 23], 'face': 'west', 'purpose': '固态结晶机组接口候选'},
        {'id': 'C-E', 'pos': [43, 4, 23], 'face': 'east', 'purpose': '固态结晶机组接口候选'},
        {'id': 'C-S', 'pos': [23, 4, 43], 'face': 'south', 'purpose': '固态结晶机组接口候选'},
    ]
    return {
        'key': 'i01-2', 'name': 'i01-2-solid-collector', 'title': brief['title'],
        'size': [47, 48, 47], 'controller': CONTROLLER,
        'upgrade_contract': {
            'family': 'I01', 'from': 'I01-1', 'previous_controller': CONTROLLER,
            'inherited_non_controller_blocks': len(inherited) - 1,
            'new_blocks': len(additions), 'unchanged_previous_blocks': True,
            'paste_alignment': 'Align I01-2 controller with the existing I01-1 controller in world coordinates.',
            'next_stages_verified': [],
        },
        'ports': old_ports + new_ports,
        'paths': [{'name': '原前侧检修道', 'min': [21, 3, 10], 'max': [25, 6, 17]}],
        'zones': [
            {'name': '保留的一阶潮汐采集场', 'kind': 'inherited', 'min': [8, 0, 8], 'max': [38, 34, 38], 'pos': [23, 24, 23], 'role': '液态采集基础', 'service_face': '原有接口'},
            {'name': '西固态结晶机组', 'kind': 'crystallizer', 'min': [0, 0, 17], 'max': [6, 40, 29], 'pos': [3, 27, 23], 'role': '固态析出', 'service_face': '西侧'},
            {'name': '东固态结晶机组', 'kind': 'crystallizer', 'min': [40, 0, 17], 'max': [46, 40, 29], 'pos': [43, 27, 23], 'role': '固态析出', 'service_face': '东侧'},
            {'name': '南固态结晶机组', 'kind': 'crystallizer', 'min': [17, 0, 40], 'max': [29, 40, 46], 'pos': [23, 27, 43], 'role': '固态析出', 'service_face': '南侧'},
            {'name': '上层结晶收束环', 'kind': 'collector', 'min': [5, 37, 5], 'max': [41, 47, 41], 'pos': [23, 42, 23], 'role': '场约束与结晶输送', 'service_face': '外侧'},
        ],
        'links': [],
        'description': '在一阶采集塔原有结构外围增加三座固态处理机组和高位收束环；旧结构原位保留。',
        'brief': brief,
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(blocks.items())],
        'new_block_positions': [list(pos) for pos in sorted(additions)],
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
        'size_baseline': size_audit, 'port_placeholder': 'hk3gtl:industrial_port_casing',
        'project_assets_saved': sorted(project_sources),
        'hashes': hashes,
        'checks': ['一阶3796个非控制器方块按控制器锚点逐格保留', 'NBT与Sponge逐格导出回读', '新增机组未覆盖旧结构'],
        'not_verified': ['未获外观确认', '未接入正式Pattern或配方', '未进行游戏成型与运行测试', '生存获取阶段尚未核验'],
    }
    meta = {k: v for k, v in data.items() if k not in ('blocks', 'new_block_positions')}
    payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (SOURCE / 'i01-2/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('实体草稿01', '自由设计候选')
    page = page.replace('25×25×37', '47×47×48')
    page = page.replace('4,645个实体', f'{len(data["blocks"]):,}个实体')
    page = page.replace('id="layerValue">36', 'id="layerValue">47')
    page = page.replace('id="layer" type="range" min="0" max="36" value="36"',
                        'id="layer" type="range" min="0" max="47" value="47"')
    page = page.replace('四瓣收集翼包围低位固化仓；捕集翼汇向沉降腔，封闭固化仓与颗粒出口串接，冷却管沿外缘返回', data['description'])
    page = page.replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace('hk3gtl-i01-2-redesign-01.nbt', data['name'] + '.nbt')
    page = page.replace('hk3gtl-i01-2-redesign-01.schem', data['name'] + '.schem')
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('未实测浏览器交互或游戏', '待浏览器交互复核，尚未进行游戏测试')
    page = page.replace('hk3gtl-i01-2-redesign-01', data['name'])
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']), 'new_blocks': data['upgrade_contract']['new_blocks'],
                      'skipped_overlaps': data['skipped_overlaps'], 'bounds': audit['actual_bounds_xyz']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
