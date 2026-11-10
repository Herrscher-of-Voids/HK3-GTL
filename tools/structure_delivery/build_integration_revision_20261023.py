# -*- coding: utf-8 -*-
"""I01–I18融合修订统一导出、实际尺寸/接口/继承核查和图文交付。

【变更记录 #1】2026-10-23 10:58:47：删除无；新增21形态候选的同源NBT、Sponge、纹理预览、
步行可达性与旧归档身份检查；修改只发生在独立候选目录；用途为结构外观评审，不修改正式资源。
输入：三个逐台修订生成器的candidate.json与旧审查身份；输出：新交付目录及专项logs。
材料仅复用有效来源，接口保留编号和用途，失败时停止；建筑融合质量仍需人工逐台审视。
【变更记录 #2】2026-10-23 11:02:23：删除无；新增I01的Sponge负锚点写入及回读；
修改通用导出器的零偏移为候选明确粘贴锚点；用途为保证四阶在同一世界锚点原地扩建。
【变更记录 #3】2026-10-23 11:05:57：删除无；新增分组导出、声明通道净空断言及生成脚本随包；
修改摘要优先读取逐台设计原理，最终报告强制完整21形态；用途为并行修正后完整收口。
【变更记录 #4】2026-10-23 11:12:05：删除总览对包外旧日志的依赖链接；新增随包修改前图片、
验证和人工审视快照；修改总览为包内相对链接；用途为ZIP解压后直接查看前后对照。
"""
from pathlib import Path
import base64
from collections import Counter, deque
import datetime as dt
import gzip
import hashlib
import html
import json
import math
import os
import re
import shutil
import sys
import struct
import zipfile
import nbtlib
from PIL import Image, ImageDraw, ImageFont
from build_redesign69 import export, render
from structure_size_baseline import require
from review_controller_integration_20261023 import front_image, RULES

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/controller-integration-rework-20261023'
OUT = ROOT / 'deliveries/I01-I18_控制器接口融合修订_V1_20261023'
OLD = ROOT / 'logs/controller-integration-review-20261023'
PORT = 'hk3gtl:industrial_port_casing'
DIAMOND = 'minecraft:diamond_block'
DELTA = {'north': (0, 0, -1), 'south': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0)}
FONT = 'C:/Windows/Fonts/msyh.ttc'


def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def checkpoint():
    p = LOG / 'rules-read.json'
    if not p.exists():
        save(p, {'recorded_at': now(), 'note': '主任务在本轮及压缩接续后实际全文读取；聚合截断的文件已单独补读。时间为读后汇总时刻。',
                 'files': [{'path': 'rule/' + f, 'sha256': sha(ROOT / 'rule' / f),
                            'lines': len((ROOT / 'rule' / f).read_text(encoding='utf-8').splitlines())} for f in RULES]})


def load_payload(source):
    value = re.search(r'window\.HK3_PAYLOAD\s*=\s*"([^"]+)"', (source / 'data.js').read_text(encoding='utf-8'))
    return json.loads(gzip.decompress(base64.b64decode(value[1])))


def access(data):
    """以实心支持面、两格净高和一格跳升建立步行候选；只证明静态操作路径。"""
    cells = {tuple(b['pos']) for b in data['blocks']}
    w, h, d = data['size']
    stands = {(x, y + 1, z) for x, y, z in cells if (x, y + 1, z) not in cells and (x, y + 2, z) not in cells}
    # 外围测试地面与结构底面同高，表示粘贴在平坦地形上的接近路径。
    boundary = {(x, 1, z) for x in range(-1, w + 1) for z in (-1, d)}
    boundary |= {(x, 1, z) for x in (-1, w) for z in range(-1, d + 1)}
    stands |= boundary
    visited, queue = set(boundary), deque(boundary)
    while queue:
        x, y, z = queue.popleft()
        for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy, z + dz)
                if p in stands and p not in visited and not (dy == 1 and (x, y + 2, z) in cells):
                    visited.add(p)
                    queue.append(p)
    result = []
    markers = [{'id': '主控', 'pos': data['controller'], 'face': data.get('controller_face', 'north')}] + data['ports']
    for marker in markers:
        p, delta = marker['pos'], DELTA[marker['face']]
        front = tuple(p[i] + delta[i] for i in range(3))
        behind = tuple(p[i] - delta[i] for i in range(3))
        possible = []
        for q in visited:
            side = sum((q[i] - p[i]) * delta[i] for i in (0, 2))
            dist = math.sqrt((q[0] - p[0]) ** 2 + (q[2] - p[2]) ** 2 + (q[1] + 1.62 - p[1] - .5) ** 2)
            if .5 <= side <= 3 and dist <= 3.5:
                possible.append((dist, q))
        result.append({'id': marker['id'], 'pos': p, 'face': marker['face'], 'front_clear': front not in cells,
                       'backing_solid': behind in cells, 'walk_access': bool(possible),
                       'operation_stand': list(min(possible)[1]) if possible else None})
    return result


def signed(data):
    anchor = data.get('paste_anchor')
    if not anchor:
        anchor = data.get('anchor')
    if isinstance(anchor, dict):
        anchor = anchor.get('local') or anchor.get('pos')
    if not anchor:
        # 四阶原始蓝图的signed平移由控制轴与地盘半径确定。
        anchor = [data['size'][0] // 2, 0, data['size'][2] // 2]
    return {tuple(b['pos'][i] - anchor[i] for i in range(3)): b['state'] for b in data['blocks']}


def build():
    checkpoint()
    entries = read(OLD / 'review.json')['items']
    material_bank, names = {}, {}
    for item in entries:
        payload = load_payload(ROOT / item['source'])
        material_bank.update({m['state']: m for m in payload['materials']})
        names.update(payload.get('names', {}))
    if len(sys.argv) > 2:
        entries = [item for item in entries if item['key'] in sys.argv[2:]]
    manifest, inheritance, previous = [], [], None
    for item in entries:
        key, source = item['key'], ROOT / item['source']
        assert sha(source / 'blueprint.json') == item['sha256']['blueprint'], key + '原蓝图改变'
        assert sha(source / item['nbt']) == item['sha256']['nbt'], key + '原NBT改变'
        before = read(source / 'blueprint.json')
        data = read(LOG / key / 'candidate.json')
        assert data['key'].lower() == key and data['title'] == before['title']
        assert data['size'] == before['size']
        cells = {tuple(b['pos']): b['state'] for b in data['blocks']}
        old_cells = {tuple(b['pos']): b['state'] for b in before['blocks']}
        assert len(cells) == len(data['blocks']), key + '重复坐标'
        assert cells[tuple(data['controller'])] == DIAMOND
        assert {p['id']: (p['purpose'], p['face']) for p in data['ports']} == {p['id']: (p['purpose'], p['face']) for p in before['ports']}
        assert {tuple(p['pos']) for p in data['ports']} == {p for p, s in cells.items() if s == PORT}
        assert set(cells.values()) <= set(old_cells.values()) | {DIAMOND}, key + '新增普通材料'
        for path in data.get('paths', []):
            hits = [p for p in cells if all(path['min'][i] <= p[i] <= path['max'][i] for i in range(3))]
            assert not hits, (key, '声明通道内存在实体', path['name'], hits[:10])
        size_check = require(data)
        reaches = access(data)
        assert all(p['front_clear'] for p in reaches), (key, '正面遮挡', reaches)
        assert all(p['backing_solid'] for p in reaches), (key, '背面空悬', reaches)
        assert all(p['walk_access'] for p in reaches), (key, '不可步行接近', reaches)
        used, counts = sorted(set(cells.values())), Counter(cells.values())
        materials = [material_bank[s] for s in used]
        assert all(m.get('complete_cube') for m in materials), key + '完整方块元数据缺失'
        changed = {'removed': sum(p not in cells for p in old_cells), 'added': sum(p not in old_cells for p in cells),
                   'replaced': sum(p in old_cells and s != old_cells[p] for p, s in cells.items())}
        target = OUT / key
        target.mkdir(parents=True, exist_ok=True)
        data['candidate_version'] = '控制器接口融合修订V1（待批准）'
        data['block_count'] = len(cells)
        data['approval_status'] = '新修订候选；源结构的批准不自动继承'
        data['source_identity'] = {k: item[k] for k in ('source', 'sha256', 'status')}
        anchor = data.get('paste_anchor', [0, 0, 0]) if key.startswith('i01-') else [0, 0, 0]
        offset = [-v for v in anchor]
        data.setdefault('construction_notes', {}).update({'origin': [0, 0, 0], 'paste_anchor': anchor,
            'schematic_offset': offset, 'recommended_bottom_world_y': -60,
            'recommended_controller_world_y': -60 + data['controller'][1],
            'world_height_range': [-60, -60 + data['size'][1] - 1], 'status': data['approval_status']})
        data['change_log'] = data.get('change_log', []) + [{'number': len(data.get('change_log', [])) + 1,
            'time': now(), '删除': '原独立面板、专用接口墩及相关无效线路，详见integration_revision',
            '新增': '按现有设备表面布置的主控与接口位置及定位记录', '修改': changed,
            '用途': '结构自然融合候选；不改正式资源、配方或游戏实例'}]
        save(target / 'blueprint.json', data)
        states, groups, hashes = export(data, target)
        if any(offset):
            schem = target / (data['name'] + '.schem')
            raw = gzip.decompress(schem.read_bytes())
            prefix = b'\x0b\x00\x06Offset' + struct.pack('>i', 3)
            old_tag = prefix + struct.pack('>3i', 0, 0, 0)
            assert raw.count(old_tag) == 1
            raw = raw.replace(old_tag, prefix + struct.pack('>3i', *offset))
            schem.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
            assert list(map(int, nbtlib.load(schem)['Offset'])) == offset
            hashes['schem'] = sha(schem)
        namespaces = Counter()
        ordinary = sum(v for s, v in counts.items() if s not in (DIAMOND, PORT))
        for s, v in counts.items():
            if s not in (DIAMOND, PORT):
                namespaces[s.split(':')[0]] += v
        audit = {'recorded_at': now(), 'hashes': hashes, 'palette': dict(counts), 'size_baseline': size_check,
                 'changes': changed, 'access': reaches, 'source_unchanged': True,
                 'paste_anchor': anchor, 'schematic_offset': offset, 'recommended_bottom_y': -60,
                 'ordinary_material_namespaces': {s: {'count': v, 'percent': round(v / ordinary * 100, 2)} for s, v in namespaces.items()},
                 'markers': {DIAMOND: counts[DIAMOND], PORT: counts[PORT]},
                 'checks': ['声明尺寸与实际方块边界达到原69座总表逐轴下限', 'NBT与Sponge的全部位置、状态、尺寸及调色板回读一致',
                            '接口编号、用途、朝向与原版一致；所有接口为工业接口位置标记', '主控和接口正面无遮挡、背后为实壳；存在两格净高的静态步行操作路径',
                            '普通材料全部复用本机有效来源，沿用既有完整方块材质库', '原蓝图与NBT的SHA256保持一致'],
                 'not_verified': ['本版外观尚待用户批准；融合质量另行逐台人工审视', '正式控制器、Pattern、实际仓室能力与配方运行未验收',
                                  '生存获取、研究门槛和阶段闭环未在游戏中验收；I14/I15历史电压映射缺口本轮未改',
                                  '图像为实例纹理的离线投影，不模拟完整游戏光照和动画；步行检查假设外围平地']}
        if key.startswith('i01-'):
            current = signed(data)
            if previous:
                mismatch = [{'pos': list(p), 'old': s, 'new': current.get(p)} for p, s in previous.items() if current.get(p) != s]
                assert not mismatch, (key, '四阶继承覆盖', mismatch[:20])
                inheritance.append({'to': key, 'preserved': len(previous), 'added': len(current) - len(previous), 'removed': 0, 'changed': 0})
            previous = current
        meta = {k: v for k, v in data.items() if k != 'blocks'}
        save(target / '设计与检查.json', {'data': meta, 'audit': audit})
        payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': names}
        packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), compresslevel=9)).decode('ascii')
        (target / 'data.js').write_text('/* 融合修订V1；变更记录#1 ' + now() + '：仅新候选的同源逐格数据与离线纹理。 */\nwindow.HK3_PAYLOAD=' + json.dumps(packed) + ';', encoding='utf-8')
        render(data, materials, target)
        front_image(data, materials).save(target / '北立面定位.png')
        manifest.append({'key': key, 'title': data['title'], 'size': data['size'], 'blocks': len(cells), 'controller': data['controller'],
                         'ports': data['ports'], 'changes': changed, 'hashes': hashes, 'integration_revision': data['integration_revision'],
                         'source': item['source'], 'access': reaches, 'status': data['approval_status']})
        print(key, len(cells), '方块；导出、接口与尺寸检查通过', flush=True)
    save(OUT / 'manifest.json', {'recorded_at': now(), 'items': manifest, 'i01_inheritance': inheritance,
                               'status': '结构融合修订候选，待外观批准；未接入正式Pattern或游戏'})
    save(LOG / 'verification.json', {'recorded_at': now(), 'forms': len(manifest), 'items': manifest, 'i01_inheritance': inheritance,
                                    'source_blueprint_and_nbt_unchanged': True, 'game_tested': False, 'deployed': False})


def link(target, origin=OUT):
    return html.escape(os.path.relpath(target, origin).replace('\\', '/'), quote=True)


def report():
    manifest = read(OUT / 'manifest.json')
    assert len(manifest['items']) == 21, '分组导出不能作为最终完整交付'
    rows = []
    for item in manifest['items']:
        k, source = item['key'], ROOT / item['source']
        old_img = source / '等轴预览.png'
        shutil.copy2(old_img, OUT / k / '修改前等轴.png')
        revision = item['integration_revision']
        summary = revision.get('summary') or revision.get('principle') or revision.get('concept') or revision.get('description') or '主控与接口改为嵌入现有工艺设备。'
        changes = item['changes']
        rows.append(f'<article id="{k}"><h2>{k.upper()} · {html.escape(item["title"])}</h2><p>{html.escape(str(summary))}</p>'
                    f'<div class="pair"><figure><figcaption>修改前</figcaption><img loading="lazy" src="{k}/修改前等轴.png"></figure>'
                    f'<figure><figcaption>融合修订V1</figcaption><a href="{k}/三维评审.html"><img loading="lazy" src="{k}/等轴预览.png"></a></figure></div>'
                    f'<p>主控 [{", ".join(map(str,item["controller"]))}] · {len(item["ports"])} 个接口 · '
                    f'删除 {changes["removed"]}／新增 {changes["added"]}／替换 {changes["replaced"]} 方块</p>'
                    f'<p><a class="button" href="{k}/三维评审.html">旋转查看与逐口定位</a> '
                    f'<a href="{k}/北立面定位.png">北立面</a> · <a href="{k}/设计与检查.json">坐标与检查</a> · '
                    f'<a href="{k}/{read(OUT/k/"blueprint.json")["name"]}.nbt">NBT</a> · '
                    f'<a href="{k}/{read(OUT/k/"blueprint.json")["name"]}.schem">Schematic</a></p></article>')
    nav = ' '.join(f'<a href="#{x["key"]}">{x["key"].upper()}</a>' for x in manifest['items'])
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I01–I18 控制器接口融合修订V1</title><style>body{margin:0;background:#101c28;color:#e2ebf0;font:16px/1.8 "Microsoft YaHei",sans-serif}header,main{max-width:1500px;margin:auto;padding:24px}h1{font-size:30px;margin:0}h2{font-size:23px}a{color:#a6d8e7}nav{display:flex;flex-wrap:wrap;gap:8px}nav a,.button{display:inline-block;padding:6px 12px;border:1px solid #567080;text-decoration:none;border-radius:4px}article{padding:18px 24px;margin:28px 0;background:#1b2b3b;border:1px solid #344c5e;scroll-margin-top:15px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0;background:#131a28}figcaption{padding:8px 14px;color:#e9d89e}img{width:100%;height:440px;object-fit:contain}.note{padding:14px 20px;background:#30403d;border-left:4px solid #c5ba6a}@media(max-width:900px){.pair{grid-template-columns:1fr}img{height:360px}header,main{padding:14px}}</style><header><h1>I01–I18 · 控制器接口融合修订V1</h1><p>18台机器，共21形态。旧前置面板与接口托柱清除，接口按工艺用途嵌进既有设备本体。</p><p class="note">本轮已修改结构并导出完整NBT／Schematic；这是待外观批准的新候选。原批准归档保持原字节，正式Pattern与游戏实例未替换。图像是同源纹理投影。</p><p><a href="manifest.json">全部坐标及变更清单</a> · <a href="' + link(LOG/'verification.json') + '">验证记录</a> · <a href="' + link(OLD/'index.html') + '">修改前审查</a></p><nav>' + nav + '</nav></header><main>' + ''.join(rows) + '</main><!-- 变更记录#1 ' + now() + '：新增21形态结构融合修订前后对照；不改变原批准文件。 --></html>'
    review_paths = [LOG/'visual-i01-i08.json', LOG/'visual-i09-i15.json', LOG/'visual-i16-i18.json']
    save(OUT/'人工审视.json', {'recorded_at': now(), 'groups': [read(p) for p in review_paths]})
    save(OUT/'验证记录.json', read(LOG/'verification.json'))
    page = page.replace(link(LOG/'verification.json'), '验证记录.json')
    page = page.replace(link(OLD/'index.html'), '人工审视.json').replace('>修改前审查</a>', '>人工审视</a>')
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    sheet = Image.new('RGB', (1680, 7 * 370 + 70), '#131a28')
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 12), 'I01–I18 控制器接口融合修订V1 · 21形态', font=ImageFont.truetype(FONT, 24), fill='#edf2ff')
    for i, item in enumerate(manifest['items']):
        im = Image.open(OUT / item['key'] / '等轴预览.png')
        im.thumbnail((550, 330))
        x, y = (i % 3) * 560, 70 + (i // 3) * 370
        sheet.paste(im, (x + (560 - im.width) // 2, y + 30))
        draw.text((x + 15, y), item['key'].upper() + ' · 主控 ' + str(item['controller']), font=ImageFont.truetype(FONT, 16), fill='#e7dbac')
    sheet.save(OUT / '21形态总览.png')
    # 链接按实际文件逐一检查，避免候选交付目录改名导致相对路径失效。
    broken, links = [], 0
    for pagepath in [OUT/'index.html', *OUT.glob('*/三维评审.html')]:
        for value in re.findall(r'(?:href|src)="([^"]+)"', pagepath.read_text(encoding='utf-8')):
            if value.startswith(('http:', 'https:', 'data:', '#')):
                continue
            path = pagepath.parent / value.split('#')[0].split('?')[0]
            links += 1
            if not path.exists():
                broken.append(str(path))
    assert not broken, broken
    save(LOG/'delivery-links.json', {'recorded_at': now(), 'checked': links, 'broken': broken})
    print('图文交付页面与', links, '个本地链接检查通过', flush=True)


def finish():
    verification = read(LOG/'verification.json')
    assert verification['forms'] == 21
    scripts = ['build_integration_revision_20261023.py', 'package_integration_review.mjs',
               'integration_i01_i08.py', 'integration_i09_i15.py', 'integration_i16_i18.py']
    generator_folder = OUT / '生成脚本'
    generator_folder.mkdir(exist_ok=True)
    for name in scripts:
        shutil.copy2(ROOT/'tools/structure_delivery'/name, generator_folder/name)
    save(generator_folder/'脚本身份.json', {'recorded_at': now(), 'note': '这些是项目内生成入口的快照；依赖原仓库的有效源蓝图、共享导出器和材质查看器，不是独立安装工具。',
                                     'files': [{'path': name, 'sha256': sha(generator_folder/name)} for name in scripts]})
    stamp = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d_%H-%M-%S')
    discussion = ROOT / 'doc/HK3GTL-内测5/讨论记录' / (stamp + '_I01-I18控制器接口融合结构修订V1.html')
    old_discussion = discussion.parent/'2026-10-23_10-43-28_I01-I18控制器接口自然融合要求与逐台审查.html'
    text = f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I01–I18控制器接口融合结构修订V1</title><style>body{{max-width:1050px;margin:30px auto;font:16px/1.8 "Microsoft YaHei",sans-serif;background:#eef3f5;color:#243b49}}section,header{{padding:20px;background:white;margin:15px}}</style><header><h1>I01–I18控制器接口融合结构修订V1</h1><p>记录时间：{now()}，Asia/Hong_Kong（UTC+08:00）。用户消息精确时间未知，采用实际记录时间。</p></header><section><h2>用户要求与已确认</h2><p>在逐台审查后，负责人原话：“修改结构”。本次执行范围为I01四阶及I02–I18全部21形态，按控制器/接口自然融入机器的已明确要求修改；不重复询问已授权的制作。</p><p>该指令授权制作修订结构，不自动等同新候选外观批准或部署。旧“统一白框面板”解释由设计规则#9覆盖，已批准归档及历史讨论保留。</p></section><section><h2>已实施</h2><p>I01四阶去掉继承白框坞并统一融入固定塔裙座；I02–I14清除通用主控盒与六接口墩，接口按工艺分布于既有模块。I15主控嵌炉座；I16主控从雨棚下移到门架；I17取消独立小柱/主控架；I18取消前置长牌并分散至闸室、热室、实验翼及抽气设备。</p><p>完整21份新蓝图、NBT、Sponge、离线三维页、等轴/立面及接口坐标已另存新候选目录。未修改正式机器名、普通建材方案、源交付、不可变归档、正式Pattern、配方或游戏实例；未增加模组修订号。</p></section><section><h2>已验证与未验收</h2><p>逐轴基线和实际方块边界、NBT/Sponge全部方块位置及状态回读、接口编号/用途/朝向、主控钻石标记、接口工业标记、正面净空/背壳、外围平地假设下两格净高步行接近检查通过。I01四阶逐格继承校核为零拆除和零异材覆盖。21份源蓝图及NBT身份保持。</p><p>融合造型逐台人工审视记录另存专项logs；几何连通与步行检查不替代建筑质量评审。待定：用户对本版外观的批准；正式控制器/Pattern与实际仓室能力、配方运行、生存研究和阶段可达性、实机建造未验收。I14/I15原有电压映射缺口本轮未扩展处理。</p></section><section><h2>相关记录与下一步</h2><p><a href="{link(OUT/"index.html",discussion.parent)}">21形态前后对照及新结构</a> · <a href="{link(LOG/"verification.json",discussion.parent)}">验证记录</a> · <a href="{link(old_discussion,discussion.parent)}">前次审查及覆盖关系</a></p><p>下一步由负责人审阅融合修订外观；批准后按既有不可变归档和批次规则接入，当前不将候选计入新批准批次。完整整包内存优化仍后置。</p><p>【变更记录 #1】{now()}：删除旧独立接口载体（仅新候选）；新增设备壳面嵌口布局、21份结构及验证；修改结构几何与接口元数据；用途为落实负责人要求，未部署或冒充游戏验收。</p></section></html>'
    discussion.write_text(text, encoding='utf-8')
    verification['discussion'] = discussion.relative_to(ROOT).as_posix()
    verification['visual_review_files'] = [p.name for p in sorted(LOG.glob('visual-*.json'))]
    save(LOG/'verification.json', verification)
    save(OUT/'验证记录.json', verification)
    archive = OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(OUT.parent))
    save(LOG/'archive-identity.json', {'recorded_at': now(), 'path': archive.relative_to(ROOT).as_posix(), 'sha256': sha(archive), 'bytes': archive.stat().st_size})
    print('讨论及候选ZIP已保存：', archive.name, flush=True)


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else '--build'
    {'--checkpoint': checkpoint, '--build': build, '--report': report, '--finish': finish}[action]()
