"""I05 twin-column medium regeneration appearance preview."""
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

OUT = ROOT / 'deliveries/I05_稳定介质再生塔_自由设计预览'


def build():
    brief = {'id': 'I05', 'title': '稳定介质再生塔', 'minimum_wdh': [55, 45, 49]}
    a = Build(brief)
    base = 'ad_astra:ostrum_plating'
    shell = 'hk3gtl:voltage_machine_casing_hcv'
    rib = 'gtlcore:lafium_mechanical_casing'
    pipe = 'gtceu:ptfe_pipe_casing'
    vent = 'gtceu:computer_heat_vent'
    panel = 'gtlcore:multi_functional_casing'
    glass = 'gtceu:laminated_glass'
    energy = 'gtlcore:rhenium_reinforced_energy_glass'
    marker = 'gtlcore:advanced_stellar_containment_casing'
    port = 'hk3gtl:industrial_port_casing'

    # Offset foundations leave the central inspection lane open.
    for x0, x1, z0, z1 in ((2, 24, 13, 39), (31, 52, 18, 39), (12, 43, 2, 10)):
        a.box((x0, 0, z0), (x1, 1, z1), base)
        frame(a, x0, x1, 2, z0, z1, rib)
    for cx, cz, radius, top in ((13, 26, 8, 42), (42, 29, 7, 30)):
        for y in range(4, top + 1):
            belt = y in (4, top) or (y - 4) % 8 == 0
            body = shell if top == 42 else 'hk3gtl:voltage_machine_casing_hbv'
            circle(a, cx, cz, radius, y, rib if belt else body, 2)
            if not belt:
                for dx in (-2, -1, 0, 1, 2):
                    a.set(cx + dx, y, cz - radius, glass)
                    a.set(cx + dx, y, cz + radius, glass)
            circle(a, cx, cz, 3, y, 'gtceu:corrosion_proof_casing' if belt else energy)
            a.set(cx, y, cz, 'gtlcore:molecular_casing')
        for dx in (-radius, radius):
            a.box((cx + dx, 2, cz - 1), (cx + dx, top + 1, cz + 1), 'ad_astra:etrium_panel')
            for y in range(8, top, 8):
                a.box((cx + dx - 1, y, cz - 2), (cx + dx + 1, y + 1, cz + 2), rib)
        # Closed stepped caps, visibly different from I04's open crown.
        for step in range(4):
            r = radius - step * 2
            for x in range(cx - r, cx + r + 1):
                for z in range(cz - r, cz + r + 1):
                    if (x - cx) ** 2 + (z - cz) ** 2 <= r * r:
                        a.set(x, top + 1 + step, z, 'gtceu:stainless_evaporation_casing' if step % 2 else rib)
        a.box((cx - 1, top + 5, cz - 1), (cx + 1, top + 6, cz + 1), marker)

    # Service decks surround the pressure vessels, with outer stays and an
    # access spine; every deck is continuous enough to read as a catwalk.
    for cx, cz, radius, y in ((13, 26, 8, 20), (13, 26, 8, 34), (42, 29, 7, 18)):
        for x in range(cx - radius - 2, cx + radius + 3):
            for z in range(cz - radius - 2, cz + radius + 3):
                edge = radius <= max(abs(x - cx), abs(z - cz)) <= radius + 2
                if edge:
                    a.set(x, y, z, 'gtceu:assembly_line_grating')
        for x, z in ((cx - radius - 2, cz - radius - 2),
                     (cx + radius + 2, cz - radius - 2),
                     (cx - radius - 2, cz + radius + 2),
                     (cx + radius + 2, cz + radius + 2)):
            a.box((x, y - 2, z), (x, y, z), 'gtlcore:space_elevator_mechanical_casing')
    for y in range(3, 35):
        a.set(13, y, 38, 'ad_astra:steel_panel')
        if y % 3 == 0:
            a.set(13, y, 37, 'gtceu:assembly_line_grating')

    # The reboiler is a low horizontal tube bundle: it breaks up the twin-tower
    # silhouette and visually explains where regeneration heat enters.
    for cx in (10, 15, 20):
        a.box((cx - 1, 3, 39), (cx + 1, 7, 42), 'gtceu:heatproof_machine_casing', True)
        a.box((cx, 4, 40), (cx, 6, 41), 'gtceu:stainless_evaporation_casing')
    a.line((10, 5, 43), (20, 5, 43), 'gtceu:titanium_pipe_casing')
    a.line((13, 5, 38), (13, 5, 43), 'gtceu:titanium_pipe_casing')

    # Three cartridge racks at the front of the regeneration column.
    for z in (17, 25, 33):
        a.box((2, 5, z - 2), (5, 18, z + 2), 'gtlcore:law_filter_casing', True)
        for y in (7, 11, 15):
            a.box((2, y, z - 1), (3, y + 1, z + 1), 'gtceu:sterilizing_filter_casing')
        a.line((4, 19, z), (8, 19, z), pipe)

    # Elevated transfer gantry and a separate low return line.
    for y in (22, 26):
        a.line((21, y, 26), (35, y, 26), pipe)
        a.line((35, y, 26), (35, y, 29), pipe)
    a.box((23, 19, 23), (32, 20, 29), 'ad_astra:desh_panel')
    for z in (23, 29):
        a.line((23, 21, z), (32, 21, z), rib)
    for x in (23, 32):
        for z in (23, 29):
            a.box((x, 2, z), (x, 20, z), 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing')
    # Feed/product lines visibly terminate at the corresponding vessels.
    a.line((13, 5, 35), (13, 5, 41), pipe)
    a.line((13, 5, 41), (42, 5, 41), pipe)
    a.line((42, 5, 41), (42, 5, 36), pipe)
    a.line((18, 7, 10), (18, 7, 20), pipe)
    a.line((37, 7, 10), (37, 7, 25), pipe)

    # Condenser fins extend from the shorter column, with visible air gaps.
    for z in range(21, 38, 4):
        a.box((49, 5, z), (52, 25, z), 'gtlcore:cold_ice_casing')
        for y in (9, 15, 21):
            a.box((49, y, z), (53, y + 1, z), 'gtlcore:antifreeze_heatproof_machine_casing')
    a.line((51, 27, 21), (51, 27, 37), 'gtceu:titanium_pipe_casing')
    for z in (21, 25, 29, 33, 37):
        a.line((51, 25, z), (51, 27, z), 'gtceu:titanium_pipe_casing')
        a.line((49, 25, z), (51, 25, z), 'gtceu:ptfe_pipe_casing')

    # Low buffer vessels distinguish dirty feed from regenerated product.
    for cx in (18, 37):
        for y in range(3, 10):
            circle(a, cx, 6, 4, y, 'hk3gtl:voltage_machine_casing_hrv' if y in (3, 9) else 'hk3gtl:glass_honkai_stabilized')
        a.box((cx - 1, 4, 5), (cx + 1, 8, 7), energy)
        a.line((cx, 7, 10), (cx, 7, 17 if cx == 18 else 22), pipe)
    a.box((25, 2, 2), (30, 5, 4), 'gtceu:advanced_computer_casing')
    a.box((26, 3, 2), (28, 3, 2), 'gtceu:computer_casing')
    controller = [27, 4, 2]
    a.set(*controller, marker)
    a.line((4, 6, 35), (4, 6, 39), pipe)
    a.line((4, 2, 39), (4, 6, 39), base)
    ports = [('FEED', [18, 5, 2], 'north', '待再生介质输入候选'),
             ('PRODUCT', [37, 5, 2], 'north', '再生介质输出候选'),
             ('POWER', [30, 4, 2], 'north', '供能候选'),
             ('RESIDUE', [4, 6, 39], 'south', '残留物排出候选')]
    for _, pos, _, _ in ports:
        a.set(*pos, port)
    return {'key': 'i05', 'name': 'i05-regeneration-free', 'title': brief['title'],
            'size': [55, 49, 45], 'controller': controller,
            'ports': [{'id': key, 'pos': pos, 'face': face, 'purpose': purpose}
                      for key, pos, face, purpose in ports],
            'paths': [{'name': '中央维护通道', 'min': [25, 2, 11], 'max': [30, 5, 18]}],
            'zones': [
                {'name': '高位再生塔', 'kind': 'regeneration', 'min': [2, 0, 13], 'max': [24, 48, 39], 'pos': [13, 42, 26], 'role': '再生处理与过滤', 'service_face': '前侧与左侧'},
                {'name': '冷凝回收塔', 'kind': 'condenser', 'min': [31, 0, 18], 'max': [53, 36, 39], 'pos': [42, 30, 29], 'role': '冷凝回收', 'service_face': '右侧'},
                {'name': '双路缓冲罐', 'kind': 'buffer', 'min': [12, 0, 2], 'max': [43, 10, 10], 'pos': [27, 8, 6], 'role': '输入与输出缓冲', 'service_face': '前侧'},
                {'name': '管桥与回流', 'kind': 'return', 'min': [13, 2, 23], 'max': [42, 26, 41], 'pos': [27, 26, 26], 'role': '转移与回流', 'service_face': '中央与后侧'}],
            'links': [
                {'from': 'FEED', 'to': '高位再生塔', 'route': [[18, 5, 2], [18, 7, 20]]},
                {'from': '高位再生塔', 'to': '冷凝回收塔', 'route': [[21, 22, 26], [35, 22, 26]]},
                {'from': '冷凝回收塔', 'to': 'PRODUCT', 'route': [[37, 7, 25], [37, 7, 10]]},
                {'from': 'RESIDUE', 'to': '残留过滤舱', 'route': [[4, 6, 39], [4, 19, 35]]}], 'brief': brief,
            'description': '错高双塔组成介质再生回路：左侧高塔以装甲筒体和纵向观察窗包围再生核心，外侧设置三组可见过滤舱；右侧矮塔连接疏排冷凝翅片。高位管桥传输介质，低位管路回流，前方双缓冲罐分开接收待处理介质与再生产品。',
            'role_materials': {k: sorted(v) for k, v in a.roles.items()},
            'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())]}


def main():
    data = build()
    size_audit = require(data)
    occupied = {tuple(b['pos']) for b in data['blocks']}
    for path in data['paths']:
        lo, hi = path['min'], path['max']
        assert not any(tuple(p) in occupied for p in
                       __import__('itertools').product(*(range(lo[i], hi[i] + 1) for i in range(3))))
    counts = collections.Counter(b['state'] for b in data['blocks'])
    resources = Resources(instance=TEST_INSTANCE, project_resources=ROOT / 'src/main/resources')
    try:
        materials = [resources.material(state) for state in sorted(counts)]
    finally:
        resources.close()
    OUT.mkdir(parents=True, exist_ok=True)
    states, groups, hashes = export(data, OUT)
    render(data, materials, OUT)
    audit = {'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
             'instance': str(TEST_INSTANCE), 'palette': dict(counts), 'hashes': hashes,
             'project_resource_overlay': 'src/main/resources/assets/hk3gtl; instance files unchanged',
             'size_baseline': size_audit,
             'checks': ['正式名称保持稳定介质再生塔', '测试包真实方块模型与纹理解析', 'NBT与Sponge逐格回读', '尺寸下限与维护净空检查', '工业接口机械方块已用于全部接口位置'],
             'not_verified': ['待外观确认', '未接入正式Pattern与配方', '未实测浏览器交互与游戏运行', '生存材料可达性尚未核验']}
    meta = {k: v for k, v in data.items() if k != 'blocks'}
    payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    page = (SOURCE / 'i05/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="../index.html"', 'href="设计与检查.json"').replace('← 全部69座', '← 设计与检查')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>', '')
    page = page.replace('实体草稿01', '自由设计候选').replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    page = page.replace('hk3gtl-i05-redesign-01', data['name'])
    page = re.sub(r'\d+×\d+×\d+（宽×长×高） · [\d,]+个实体', f'55×45×49（宽×长×高） · {len(data["blocks"]):,}个实体', page)
    page = re.sub(r'id="layerValue">\d+', 'id="layerValue">48', page)
    page = re.sub(r'id="layer" type="range" min="0" max="\d+" value="\d+"', 'id="layer" type="range" min="0" max="48" value="48"', page)
    page = re.sub(r'(<summary>本机建筑概念</summary><p>).*?(</p>)', lambda m: m[1] + data['description'] + m[2], page)
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']), 'size_audit': size_audit}, ensure_ascii=True))


if __name__ == '__main__':
    main()
