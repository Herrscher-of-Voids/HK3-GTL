# -*- coding: utf-8 -*-
"""导出 I01–I18 宽度轴主控置中 V2，V1 原件与正式资源保持独立。

【变更记录 #1】2026-10-23 11:40:16（结构候选，不增加模组修订号）
- 删除：无；旧候选、批准归档、正式资源及游戏实例不由本入口改写。
- 新增：21形态的中心列断言、V1逐文件身份、同源结构与带中心线的立面。
- 修改：读取分组置中修订器结果，复用已有纹理、NBT/Sponge导出和静态可达检查。
- 用途：落实宽35放第18格的要求；中心列以1计数，蓝图坐标以0计数；失败即停止。
输入为V1交付及专项候选；输出为V2交付和专项日志。外观审批与游戏功能仍分别验收。
"""
from pathlib import Path
from collections import Counter
import base64
import datetime as dt
import gzip
import hashlib
import html
import json
import re
import shutil
import struct
import sys
import zipfile

import nbtlib
from PIL import Image, ImageDraw, ImageFont
from build_redesign69 import export, render
from build_integration_revision_20261023 import access, signed, load_payload
from review_controller_integration_20261023 import front_image, RULES
from structure_size_baseline import ROOT, require

SOURCE = ROOT / 'deliveries/I01-I18_控制器接口融合修订_V1_20261023'
OUT = ROOT / 'deliveries/I01-I18_控制器居中融合修订_V2_20261023'
LOG = ROOT / 'logs/controller-centering-rework-20261023'
FONT = 'C:/Windows/Fonts/msyh.ttc'
PORT, DIAMOND = 'hk3gtl:industrial_port_casing', 'minecraft:diamond_block'


def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def identities(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}


def checkpoint():
    if not (LOG / 'rules-read.json').exists():
        save(LOG / 'rules-read.json', {'recorded_at': now(),
             'note': '本轮与压缩接续后六规则已全文实际读取；聚合截断后按文件补读。本时间为读后身份记录。',
             'files': [{'path': 'rule/' + name, 'sha256': sha(ROOT / 'rule' / name)} for name in RULES]})
    if not (LOG / 'source-identity.json').exists():
        save(LOG / 'source-identity.json', {'recorded_at': now(), 'source': SOURCE.relative_to(ROOT).as_posix(),
             'files': identities(SOURCE), 'zip_sha256': sha(SOURCE.with_suffix('.zip'))})


def unchanged():
    original = read(LOG / 'source-identity.json')
    assert identities(SOURCE) == original['files'], 'V1交付被改写'
    assert sha(SOURCE.with_suffix('.zip')) == original['zip_sha256'], 'V1压缩包被改写'


def build():
    checkpoint()
    entries = read(SOURCE / 'manifest.json')['items']
    if len(sys.argv) > 2:
        entries = [x for x in entries if x['key'] in sys.argv[2:]]
    items, previous, inheritance = [], None, []
    for item in entries:
        key = item['key']
        old = read(SOURCE / key / 'blueprint.json')
        data = read(LOG / key / 'candidate.json')
        cells = {tuple(b['pos']): b['state'] for b in data['blocks']}
        before = {tuple(b['pos']): b['state'] for b in old['blocks']}
        assert len(cells) == len(data['blocks'])
        assert data['title'] == old['title'] and data['size'] == old['size']
        assert data['ports'] == old['ports'], key + '不应改变既有接口合同或位置'
        w, h, d = data['size']
        assert w % 2 == 1, key + '偶数宽需另行明确中心两列的选择'
        assert data['controller'][0] == (w - 1) // 2, key + '主控未置中'
        assert cells[tuple(data['controller'])] == DIAMOND
        expected_diamonds = {p for p, s in before.items() if s == DIAMOND}
        expected_diamonds.discard(tuple(old['controller']))
        expected_diamonds.add(tuple(data['controller']))
        assert {p for p, s in cells.items() if s == DIAMOND} == expected_diamonds, key + '主控或既有核心标记异常'
        assert {tuple(p['pos']) for p in data['ports']} == {p for p, s in cells.items() if s == PORT}
        assert set(cells.values()) <= set(before.values()), key + '新增普通材料'
        for path in data.get('paths', []):
            assert not any(all(path['min'][i] <= p[i] <= path['max'][i] for i in range(3)) for p in cells), (key, path)
        baseline, reaches = require(data), access(data)
        assert all(x['front_clear'] and x['backing_solid'] and x['walk_access'] for x in reaches), (key, reaches)
        changes = {'removed': sum(p not in cells for p in before), 'added': sum(p not in before for p in cells),
                   'replaced': sum(p in before and s != before[p] for p, s in cells.items())}
        data['name'] = key + '-controller-centered-v2'
        data['block_count'] = len(cells)
        data['candidate_version'] = '控制器居中融合修订V2（待批准）'
        data['approval_status'] = '主控宽度轴置中候选；尚待外观批准'
        center = data.setdefault('controller_centering', {})
        center.update({'width': w, 'center_column_1based': (w + 1) // 2, 'center_x_0based': (w - 1) // 2,
                       'old_controller': old['controller'], 'controller': data['controller'],
                       'moved': old['controller'] != data['controller'], 'passed': True})
        data.setdefault('construction_notes', {}).update({'recommended_controller_world_y': -60 + data['controller'][1]})
        data.setdefault('change_log', []).append({'number': len(data.get('change_log', [])) + 1, 'time': now(),
            '删除': '偏置主控标记恢复为设备壳面；详见controller_centering' if center['moved'] else '无；主控原本已在中心列',
            '新增': '宽度中心列定位与核验记录',
            '修改': changes, '用途': '主控置中且继续自然融合；只导出新候选'})
        target = OUT / key
        target.mkdir(parents=True, exist_ok=True)
        save(target / 'blueprint.json', data)
        states, groups, hashes = export(data, target)
        offset = [-v for v in data.get('paste_anchor', [0, 0, 0])] if key.startswith('i01-') else [0, 0, 0]
        if any(offset):
            path = target / (data['name'] + '.schem')
            raw = gzip.decompress(path.read_bytes())
            tag = b'\x0b\x00\x06Offset' + struct.pack('>i', 3)
            assert raw.count(tag + struct.pack('>3i', 0, 0, 0)) == 1
            raw = raw.replace(tag + struct.pack('>3i', 0, 0, 0), tag + struct.pack('>3i', *offset))
            path.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
            assert list(map(int, nbtlib.load(path)['Offset'])) == offset
            hashes['schem'] = sha(path)
        payload = load_payload(SOURCE / key)
        bank = {m['state']: m for m in payload['materials']}
        materials = [bank[s] for s in sorted(set(cells.values()))]
        assert all(m.get('complete_cube') for m in materials)
        audit = {'recorded_at': now(), 'hashes': hashes, 'size_baseline': baseline, 'changes_from_v1': changes,
                 'center': center, 'access': reaches, 'palette': dict(Counter(cells.values())),
                 'checks': ['主控X严格位于整台宽度的中间一格', '实际边界与69座逐轴尺寸下限通过',
                            'NBT和Sponge全部方块、状态、调色板及尺寸回读一致', '原接口编号、用途、坐标及朝向保持',
                            '主控及接口有正面净空、实体背壳和静态步行操作路径', '沿用V1有效完整方块材料'],
                 'not_verified': ['新候选外观待负责人批准', '正式控制器/Pattern、真实仓室、配方、生存研究与游戏运行未验收',
                                  'I14/I15历史电压映射缺口本轮未处理', '离线纹理投影；静态步行检查假设外围平地']}
        if key.startswith('i01-'):
            current = signed(data)
            if previous:
                assert all(current.get(p) == s for p, s in previous.items()), key + '四阶继承发生覆盖'
                inheritance.append({'to': key, 'preserved': len(previous), 'added': len(current) - len(previous), 'removed': 0, 'changed': 0})
            previous = current
        meta = {k: v for k, v in data.items() if k != 'blocks'}
        save(target / '设计与检查.json', {'data': meta, 'audit': audit})
        packed = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': payload['names']}
        encoded = base64.b64encode(gzip.compress(json.dumps(packed, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), compresslevel=9)).decode('ascii')
        (target / 'data.js').write_text('/* 变更记录#1 ' + now() + '：主控置中V2同源逐格数据。 */\nwindow.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
        render(data, materials, target)
        image = front_image(data, materials)
        draw = ImageDraw.Draw(image)
        cx = 35 + data['controller'][0] * 14 + 7
        for y in range(65, image.height - 40, 12):
            draw.line((cx, y, cx, min(y + 5, image.height - 40)), fill='#6ef5ed', width=1)
        draw.text((35, 36), f'宽{w}格 · 中间第{center["center_column_1based"]}格 · X={center["center_x_0based"]}', font=ImageFont.truetype(FONT, 16), fill='#6ef5ed')
        image.save(target / '北立面定位.png')
        shutil.copy2(SOURCE / key / '等轴预览.png', target / 'V1等轴.png')
        items.append({'key': key, 'title': data['title'], 'size': data['size'], 'blocks': len(cells), 'controller': data['controller'],
                      'center': center, 'changes_from_v1': changes, 'hashes': hashes, 'access': reaches,
                      'centering_revision': center, 'source': str((SOURCE / key).relative_to(ROOT))})
        print(key, '中心列', center['center_column_1based'], '导出及可达检查通过', flush=True)
    unchanged()
    result = {'recorded_at': now(), 'forms': len(items), 'items': items, 'i01_inheritance': inheritance,
              'moved_forms': sum(i['center']['moved'] for i in items), 'source_v1_unchanged': True,
              'status': 'V2置中融合新候选，未批准、未接入正式资源或游戏', 'game_tested': False, 'deployed': False}
    save(OUT / 'manifest.json', result)
    save(LOG / 'verification.json', result)


def report():
    result = read(LOG / 'verification.json')
    assert result['forms'] == 21
    rows = []
    for item in result['items']:
        key, center = item['key'], item['center']
        definition = read(OUT / key / 'blueprint.json')
        description = center.get('summary') or center.get('principle') or '原主控已位于中心列，保留设备布局。'
        rows.append(f'<article id="{key}"><h2>{key.upper()} · {html.escape(item["title"])}</h2>'
             f'<p class="center">宽{center["width"]}格 → 第{center["center_column_1based"]}格（X={center["center_x_0based"]}） · 主控 {item["controller"]}</p>'
             f'<p>{html.escape(description)}</p><div class="pair"><figure><figcaption>V1</figcaption><img loading="lazy" src="{key}/V1等轴.png"></figure>'
             f'<figure><figcaption>V2 主控置中</figcaption><a href="{key}/三维评审.html"><img loading="lazy" src="{key}/等轴预览.png"></a></figure></div>'
             f'<p><a href="{key}/三维评审.html">旋转查看／定位主控</a> · <a href="{key}/北立面定位.png">中心线立面</a> · '
             f'<a href="{key}/{definition["name"]}.nbt">NBT</a> · <a href="{key}/{definition["name"]}.schem">Schematic</a> · '
             f'<a href="{key}/设计与检查.json">坐标与检查</a></p></article>')
    nav = ' '.join(f'<a href="#{i["key"]}">{i["key"].upper()}</a>' for i in result['items'])
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I01–I18 主控置中融合 V2</title><style>body{margin:0;background:#101c28;color:#e2ebf0;font:16px/1.8 "Microsoft YaHei",sans-serif}header,main{max-width:1500px;margin:auto;padding:24px}a{color:#a6d8e7}nav{display:flex;flex-wrap:wrap;gap:12px}article{padding:20px;margin:24px 0;background:#1b2b3b;border:1px solid #344c5e}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0;background:#131a28}figcaption{padding:8px 14px}img{width:100%;height:440px;object-fit:contain}.center{color:#7df2df;font-weight:bold}@media(max-width:900px){.pair{grid-template-columns:1fr}img{height:350px}}</style><header><h1>I01–I18 · 主控制器置中融合 V2</h1>'
    page += f'<p>21形态全部按整台结构宽度置中。调整{result["moved_forms"]}形态，其余保留原中心位置。宽35格放第18格，对应本地 X=17。</p><p>主控继续嵌入机器设备；接口沿用V1布局。青色虚线标出宽度中心列。新候选待审，未替换正式资源。</p><p><a href="21形态主控中轴总览.png">中轴总览</a> · <a href="验证记录.json">验证记录</a> · <a href="人工审视.json">逐台审视</a></p><nav>{nav}</nav></header><main>' + ''.join(rows) + '</main><!-- 变更记录#1 ' + now() + '：新增主控置中V2评审。 --></html>'
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    sheet = Image.new('RGB', (1680, 7 * 390 + 65), '#131a28')
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 12), 'I01–I18 主控中轴总览 V2 · 青线为整台宽度中心列', font=ImageFont.truetype(FONT, 24), fill='#edf2ff')
    for i, item in enumerate(result['items']):
        image = Image.open(OUT / item['key'] / '北立面定位.png')
        image.thumbnail((550, 345))
        x, y = i % 3 * 560, 65 + i // 3 * 390
        sheet.paste(image, (x + (560 - image.width) // 2, y + 30))
        draw.text((x + 10, y), item['key'].upper() + ' · 第' + str(item['center']['center_column_1based']) + '格', font=ImageFont.truetype(FONT, 17), fill='#7df2df')
    sheet.save(OUT / '21形态主控中轴总览.png')
    save(OUT / '验证记录.json', result)
    save(OUT / '人工审视.json', {'recorded_at': now(), 'groups': [read(p) for p in sorted(LOG.glob('visual-*.json'))]})
    broken, links = [], 0
    for pagepath in [OUT / 'index.html', *OUT.glob('*/三维评审.html')]:
        for value in re.findall(r'(?:href|src)="([^"]+)"', pagepath.read_text(encoding='utf-8')):
            if value.startswith(('http:', 'https:', 'data:', '#')):
                continue
            links += 1
            if not (pagepath.parent / value.split('#')[0].split('?')[0]).exists():
                broken.append(str(pagepath.parent / value))
    assert not broken, broken
    save(LOG / 'delivery-links.json', {'recorded_at': now(), 'checked': links, 'broken': broken})


def finish():
    unchanged()
    result = read(LOG / 'verification.json')
    assert result['forms'] == 21
    stamp = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d_%H-%M-%S')
    discussion = ROOT / 'doc/HK3GTL-内测5/讨论记录' / (stamp + '_I01-I18主控制器宽度轴置中V2.html')
    assert not discussion.exists()
    discussion.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I01–I18主控宽度轴置中V2</title>'
        '<style>body{max-width:1050px;margin:30px auto;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#243b49}section{padding:18px;border:1px solid #bdd1d2;margin:15px 0}</style>'
        f'<h1>I01–I18主控制器宽度轴置中V2</h1><p>实际记录时间：{now()}，Asia/Hong_Kong（UTC+08:00）。原消息精确时间未知。</p>'
        '<section><h2>用户要求与确认边界</h2><p>负责人先说“继续下一步”。助手核查后用原生问题询问是否表示批准本版并归档接入。'
        '实际答复：“我的意思是新版结构那些控制器，那个控制器主方块最好还是置中，意思是如果宽是35，它是在第18格”。</p>'
        '<p>本次据该答复继续修改21形态；确认的是主控制器沿整台宽度轴置中，不是对V1的批准。'
        '按从1计数的第18格对应从0计数的X=17；各台均为奇数宽。控制器仍应自然融入本体，接口可以按工艺分布。</p>'
        '<p>接入准备调查已暂停；没有新增外观批准、推进批次、修改正式资源或替换游戏文件。旧批准归档及候选保留。</p></section>'
        f'<section><h2>已实施及验证</h2><p>21形态逐台置中核验，实际调整{result["moved_forms"]}个偏置主控，其余保留已置中的位置。'
        'I01四阶保持同一签名锚点及逐格累积扩建；I02–I18各按既有固定设备选择中心壳面。旧主控位置恢复材质，未重新外挂控制板或托柱。</p>'
        '<p>已导出新V2的蓝图、NBT、Sponge、等轴、带中轴的北立面及离线三维评审。'
        '已核对中心列、完整接口列表保持、69座逐轴尺寸、全部NBT/Sponge方块回读、正面净空/背壳及平地假设下静态步行操作路径。'
        'V1整目录及ZIP的SHA身份保持，I01逐格继承没有拆除或异材覆盖；造型审视另存专项日志。</p></section>'
        '<section><h2>待定与未验收</h2><p>V2外观仍待负责人审阅；未将任一结构候选自动计入批准批次。'
        '正式控制器/Pattern、真实仓室、配方运行、生存研究和实机建造未验收。I14/I15历史电压映射缺口没有因本次位置修订而闭合。'
        '整包内存优化继续后置。</p><p>本条在主控X位置上细化前轮融合修订，保留自然融合要求，V1源文件与历史记录不覆盖。</p></section>'
        '<p><a href="../../../deliveries/I01-I18_控制器居中融合修订_V2_20261023/index.html">V2全部结构</a> · '
        '<a href="2026-10-23_11-17-25_I01-I18控制器接口融合结构修订V1.html">V1历史交付</a> · '
        '<a href="../../../logs/controller-centering-rework-20261023/verification.json">验证记录</a></p>'
        f'<p>【变更记录 #1】{now()}：删除偏置主控标记并恢复原设备材质；新增中轴壳面控制器标记和定位检查；'
        '修改10形态主控位置及少量内部背壳/必要检修地面；用途为落实负责人宽度置中要求，仅新候选。</p></html>', encoding='utf-8')
    result['discussion'] = discussion.relative_to(ROOT).as_posix()
    result['visual_review_files'] = [p.name for p in sorted(LOG.glob('visual-*.json'))]
    save(LOG / 'verification.json', result)
    save(OUT / '验证记录.json', result)
    scripts = ['build_controller_centering_20261023.py', 'package_integration_review.mjs',
               'integration_center_i01_i08.py', 'integration_center_i09_i15.py', 'integration_center_i16_i18.py']
    folder = OUT / '生成脚本'
    folder.mkdir(exist_ok=True)
    for name in scripts:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, folder / name)
    save(folder / '脚本身份.json', {'recorded_at': now(), '说明': '生成入口快照，依赖原仓库V1蓝图及共享导出/材质工具。',
         'files': {name: sha(folder / name) for name in scripts}})
    archive = OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                package.write(p, p.relative_to(OUT.parent))
    with zipfile.ZipFile(archive) as package:
        assert package.testzip() is None
        for name in package.namelist():
            assert hashlib.sha256(package.read(name)).hexdigest() == sha(OUT.parent / name), name
        count = len(package.namelist())
    save(LOG / 'archive-identity.json', {'recorded_at': now(), 'path': str(archive.relative_to(ROOT)),
         'sha256': sha(archive), 'bytes': archive.stat().st_size, 'files': count, 'all_entries_match': True})


if __name__ == '__main__':
    {'--checkpoint': checkpoint, '--build': build, '--report': report, '--finish': finish}[sys.argv[1]]()
