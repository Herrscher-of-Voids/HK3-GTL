# -*- coding: utf-8 -*-
"""从Java成型源导出注入器候选，保留既有评审界面和真实方块材质。"""
from pathlib import Path
from collections import Counter, deque
import base64
import gzip
import hashlib
import json
import re
import sys

from build_redesign69 import export, render
from i37_surface_runs_20261027 import merge_surface_runs
from material_resources import Resources

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/network-injector-rebuild-20261111'
OUT = ROOT / 'deliveries/崩坏能网络注入器_三段谐振入网站_V2_20261111'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
SOURCE = ROOT / 'deliveries/W03_C9_C5外环下移净空修订_20261108/w03/三维评审.html'
CONTROLLER = 'minecraft:diamond_block'
PORT = 'hk3gtl:industrial_port_casing'


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def verify(data):
    cells = {tuple(b['pos']): b['state'] for b in data['blocks']}
    assert len(cells) == len(data['blocks'])
    low = [min(p[i] for p in cells) for i in range(3)]
    high = [max(p[i] for p in cells) for i in range(3)]
    assert low == [0, 0, 0] and [v+1 for v in high] == data['size'] == [41, 33, 45]
    assert cells[(20, 2, 0)] == CONTROLLER
    assert len(data['ports']) == 8 and len({tuple(p['pos']) for p in data['ports']}) == 8
    for p in data['ports']:
        x, y, z = p['pos']
        assert z == 0 and abs(x-20) <= 1 and abs(y-2) <= 1 and (x, y) != (20, 2)
        assert cells[(x,y,z)] == PORT and cells[(x,y,1)] == 'gtceu:max_machine_casing'
    for x in (2,38):
        for z in range(7,41):
            if cells.get((x,5,z)) == 'gtceu:computer_heat_vent':
                assert all(cells.get((x,y,z)) == 'gtceu:max_machine_casing' for y in range(5)), (x,z)
    queue = deque([next(iter(cells))]); seen = set()
    while queue:
        p = queue.popleft()
        if p not in cells or p in seen:
            continue
        seen.add(p)
        for i in range(3):
            for sign in (-1, 1):
                q = list(p); q[i] += sign; queue.append(tuple(q))
    assert len(seen) == len(cells)
    assert all(p not in cells for p in [(x,y,z) for x in range(19,22) for y in range(1,4) for z in range(4,45)])
    counts = Counter(cells.values())
    assert counts['gtceu:max_machine_casing'] > len(cells)/2
    assert all(s.startswith('gtceu:') or s in (CONTROLLER,PORT) for s in counts)
    return dict(passed=True, size_xyz=data['size'], blocks=len(cells), ports=8, components=1,
                palette=dict(counts), no_clipping=True, controller_centered=True, port_backing=True,
                source='Hk3LiquidLineLayout.Kind.INJECTION', vent_columns_supported=True, game_verified=False,
                natural_zero_hw_bootstrap_verified=False)


def surface_payload(data, states):
    cells = {tuple(b['pos']): states.index(b['state']) for b in data['blocks']}
    w, _, d = data['size']
    faces = [[[] for _ in range(6)] for _ in states]
    directions = [(1,0,0),(-1,0,0),(0,0,1),(0,0,-1),(0,-1,0),(0,1,0)]
    glass = states.index('gtceu:tempered_glass')
    for (x,y,z), material in cells.items():
        for face, (dx,dy,dz) in enumerate(directions):
            neighbor = cells.get((x+dx,y+dy,z+dz))
            if neighbor is None or (neighbor == glass and material != glass):
                faces[material][face].append((y*d+z)*w+x)
    for group in faces:
        for face in group:
            face.sort()
    return merge_surface_runs(faces, data['size'])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads((LOG/'blueprint.json').read_text('utf8'))
    data.update(description='双侧进料罐 → 三段立式谐振门架 → 后部网络接收塔；正面集中主控及八接口。',
                purpose='沿用MAX/RN-HFB首充工艺；本轮只替换结构，不授予研究或HW。',
                zones=[dict(name='三段注入门架', pos=[20,30,27], min=[4,2,15], max=[36,30,39],
                            description='贯通玻璃注入通道，三道独立门架由实体梁柱支撑。')],
                paths=[dict(name='中央检修通道', min=[19,1,4], max=[21,3,44])], pipe_routes=[],
                target_voltage='MAX', status='源码已接入；外观待评审，未部署、未实机验收')
    check = verify(data)
    blocks = len(data['blocks'])
    casing_percent = check['palette']['gtceu:max_machine_casing']/blocks*100
    states, groups, hashes = export(data, OUT, validator=verify)
    surfaces, lengths, surface_check = surface_payload(data, states)
    check.update(viewer_rendered_quads=surface_check['rendered_quads'], surface_merge=surface_check,
                 checks=['41×45×33完整几何，无裁切', '主控同面居中、周围八接口均有背壳',
                         f'{blocks:,}实体六向连通，中央检修通道保留', 'NBT／Schematic全量回读一致',
                         f'原生MAX壳占{casing_percent:.2f}%，使用实例真实材质', '全部侧栏散热件逐柱承托到底座',
                         '源码候选；未部署、未实机验收'])
    resources = Resources(instance=INSTANCE, project_resources=ROOT/'src/main/resources')
    try:
        materials = []
        for state in states:
            material = resources.material(PORT if state == CONTROLLER else state)
            materials.append(dict(material, state=state))
        sources = dict(resources.sources)
    finally:
        resources.close()
    payload = dict(data={k:v for k,v in data.items() if k!='blocks'}, palette=states,
                   surfaceGroups=surfaces, surfaceRunLengths=lengths,
                   blockCount=len(data['blocks']), materials=materials, audit=check, names={})
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',',':')).encode('utf8'))).decode('ascii')
    (OUT/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(encoded)+';\n','utf8')
    page = SOURCE.read_text('utf8')
    page = re.sub(r'<title>.*?</title>', '<title>崩坏能网络注入器 · 三段谐振入网站 V2</title>',page)
    page = re.sub(r'<header>.*?</header>', f'<header><a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a><h1>崩坏能网络注入器 · 三段谐振入网站 V2</h1><div>41×45×33（宽×深×高） · {blocks:,}实体方块 · 静态候选</div></header>',page,flags=re.S)
    page = re.sub(r'<div class="candidate-note">.*?</div>', '<div class="candidate-note">'+data['description']+'</div>',page,flags=re.S)
    page = re.sub(r'<div class="locator">.*?</div>', '<div class="locator"><b>主控 [20,2,0]，朝北</b><p>同面3×3中央主控、周围八接口，有背壳；接口位置不限定仓型。</p><button data-view="controller">定位主控</button></div>',page,flags=re.S)
    page = page.replace('635','32')
    page = re.sub(r'<details open><summary>设备分区与职责</summary>.*?</details>', '<details open><summary>设备分区与职责</summary><p>'+data['description']+'</p><p>'+data['purpose']+'</p></details>',page,flags=re.S)
    page = re.sub(r'<details><summary>文件与验收边界</summary>.*?</details>', '<details><summary>文件与验收边界</summary><a href="'+data['name']+'.nbt">NBT</a> · <a href="'+data['name']+'.schem">Schematic</a> · <a href="verification.json">离线核验</a><p>钻石块是导出主控标记，按真实接口壳材质显示；游戏Pattern使用已注册注入器。源码已替换，未部署实例、未验收成型与运行。材料静态解析不代表自然首建及零HW首充通过。</p></details>',page,flags=re.S)
    page = re.sub(r'<script[^>]*>.*?</script>', '',page,flags=re.S)
    page = page.replace('</html>', '<script src="data.js"></script><script src="viewer.bundle.js"></script></html>')
    (OUT/'index.html').write_text(page,'utf8')
    engine = (ROOT/'deliveries/W03_C6_球形全动试转_20261108/w03/viewer.bundle.js').read_text('utf8')
    engine = engine.replace('-空之律者 · 穹界·虚数锚定环 · C4五环锁芯与立体晶云V1-三维预览.png',
                            '-崩坏能网络注入器V2-三维预览.png')
    engine = engine.replace('后侧天线与轴座', '后侧网络接收塔')
    (OUT/'viewer.bundle.js').write_text(engine,'utf8')
    render(data,materials,OUT)
    save(OUT/'manifest.json',dict(candidate='网络注入器V2',size_xyz=data['size'],blocks=len(data['blocks']),
         exported_hashes=hashes,approved=False,installed=False,game_verified=False,source=str((LOG/'blueprint.json').relative_to(ROOT))))
    save(OUT/'verification.json',dict(check,export_readback=True,resource_sources=sources))
    save(LOG/'structure-verification.json',dict(check,export_readback=True,exported_hashes=hashes,preview=str(OUT/'index.html')))
    print(json.dumps(dict(blocks=len(data['blocks']),passed=True,preview=str(OUT/'index.html')),ensure_ascii=False))


if __name__ == '__main__':
    main()
