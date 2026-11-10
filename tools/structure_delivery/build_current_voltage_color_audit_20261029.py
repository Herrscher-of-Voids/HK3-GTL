# -*- coding: utf-8 -*-
"""按现行批准索引和实际材料统计生成离线 HTML；不修改建筑或电压。

变更记录 #2（2026-10-29）：补齐逐台名称、当前版本实图及三维入口；缩略图内嵌并延迟显示。
变更记录 #3（2026-10-29）：补齐69项目录、11个待命名席位及4台MAX复制系统需求；不虚构建筑或编号。
变更记录 #4（2026-10-29）：十五座文明奇观保留运行电压，外观主机壳按对应律者选色。
"""
import base64
import hashlib
import io
import json
import os
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone, timedelta
from html import escape, unescape
from pathlib import Path
from project_paths import project_path
from urllib.parse import quote

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/multiblock-voltage-colors-20261029'
OUT = ROOT / 'deliveries/已完成多方块_电压与配色逐台核对_20261029'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
MAP = ROOT / 'doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html'
BASE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html'
PALETTE = ROOT / 'src/main/resources/data/hk3gtl/catalog/voltage_palette.json'
NETWORK = ROOT / 'doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json'
MAX_PLAN = ROOT / 'doc/HK3GTL-内测5/09_测试发布/千万亿级巨构工程优化与四台MAX机器方案_20261028.html'
WONDER_CASINGS = {'W01': 'WFV', 'W02': 'HBV', 'W03': 'HCV', 'W04': 'HRV', 'W05': 'HDV',
                  'W06': 'QSV', 'W07': 'QCV', 'W08': 'QEV', 'W09': 'QAV', 'W10': 'IMV',
                  'W11': 'ICV', 'W12': 'IRV', 'W13': 'IWV', 'W14': 'WSV', 'W15': 'CEV'}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def local_path(value):
    return project_path(value)


def rel(path):
    return str(path.relative_to(ROOT)).replace('\\', '/')


def href(path):
    return quote(os.path.relpath(path, OUT).replace('\\', '/'), safe='/')


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def texture_data(path):
    with Image.open(path) as image:
        image = image.convert('RGBA')
        tile = image.crop((0, 0, image.width, image.width))
        buffer = io.BytesIO()
        tile.save(buffer, 'PNG')
        pixels = [p for p in tile.getdata() if p[3]]
        mean = tuple(round(sum(p[c] for p in pixels) / len(pixels)) for c in range(3))
    return 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode(), '#%02X%02X%02X' % mean


def build_image(preview):
    for folder in [preview.parent, preview.parent.parent]:
        for name in ['完整预览.png', '整座I26完整全景.png', '等轴预览.png']:
            path = folder / name
            if path.is_file():
                with Image.open(path) as original:
                    image = original.convert('RGBA')
                    image.thumbnail((640, 480), Image.Resampling.LANCZOS)
                    background = Image.new('RGBA', image.size, '#111824')
                    background.alpha_composite(image)
                    buffer = io.BytesIO()
                    background.convert('RGB').save(buffer, 'JPEG', quality=86, optimize=True)
                return path, 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode()
    raise FileNotFoundError('当前预览缺少结构截图：' + str(preview))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    index = load(INDEX)
    material_data = load(LOG / 'material-audit.json')
    material_rows = material_data if isinstance(material_data, list) else material_data['rows']
    counts_by_key = {row['key']: row for row in material_rows}
    text = BASE.read_text(encoding='utf-8').split('const machines=', 1)[1].lstrip()
    base_catalog = json.JSONDecoder().raw_decode(text)[0]
    names = {row['id']: row['name'] for row in base_catalog}
    language = load(ROOT / 'src/main/resources/assets/hk3gtl/lang/zh_cn.json')
    names['I02'] = language['block.hk3gtl.i02_spectrum_analysis_array']
    for machine, name in {'S01': '崩坏现象研究所', 'S02': '物质重构研究所', 'S03': '量子域研究所', 'S04': '世界维系研究所', 'S05': '文明认知穹顶'}.items():
        assert name in language.values(), name
        names[machine] = name + ' · 第' + '一二三四五'[int(machine[-1]) - 1] + '阶'
    gtjar = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/GregTech Leisure-增强版/minecraft/mods/gtceu-1.20.1-1.4.4.jar'
    native_path = LOG / 'max-machine-casing-side.png'
    with zipfile.ZipFile(gtjar) as archive:
        native_path.write_bytes(archive.read('assets/gtceu/textures/block/casings/voltage/max/side.png'))
    native_texture, native_mean = texture_data(native_path)
    tiers = {'MAX': {'key': 'MAX', 'name': 'GTL 原生 MAX（原图首帧）', 'role': 'GTL 原生电压', 'main': None,
                     'texture': native_texture, 'mean': native_mean, 'texture_source': rel(native_path)}}
    for row in load(PALETTE)['palettes']:
        row = dict(row)
        path = ROOT / f"src/main/resources/assets/hk3gtl/textures/block/voltage_casings/{row['key'].lower()}/casing.png"
        row['texture'], row['mean'] = texture_data(path)
        row['texture_source'] = rel(path)
        tiers[row['key']] = row
    expected = {}
    tier_order = []
    for tr in re.findall(r'<tr>(.*?)</tr>', MAP.read_text(encoding='utf-8'), re.S):
        match = re.search(r'<td class="tier">([A-Z]+)<br>', tr)
        if match:
            tier = match.group(1)
            tier_order.append(tier)
            for machine in re.findall(r'<span class="chip">([ISWH]\d+(?:-\d+)?)\s', tr):
                expected[machine] = tier
    assert len(tier_order) == 17 and len(expected) == 69
    entries = {row['key']: row for row in index['entries']}
    for key, pattern in [('i43', 'I43_*_V1_20261028'), ('i44', 'I44_*_V2_20261029'), ('i45', 'I45_*_V2_20261029')]:
        paths = [p for p in (ROOT / 'deliveries').glob(pattern) if p.is_dir()]
        assert len(paths) == 1, (key, paths)
        entries[key] = {'key': key, 'id': key.upper(), 'source': str(paths[0]), 'status': 'candidate_unapproved'}
    rows = []
    thumbnails = {}
    for key, entry in entries.items():
        stats = counts_by_key[key]
        machine = entry['id']
        target = expected[machine]
        counts = Counter(stats['counts'])
        total = sum(counts.values())
        assert total == stats['total'] and total > 0, key
        own = {state.rsplit('_', 1)[-1].upper(): count for state, count in counts.items() if state.startswith('hk3gtl:voltage_machine_casing_')}
        target_state = 'gtceu:max_machine_casing' if target == 'MAX' else 'hk3gtl:voltage_machine_casing_' + target.lower()
        target_count = counts.get(target_state, 0)
        source = local_path(entry.get('source') or entry['archive'])
        preview_options = [source / '三维评审.html', source / key.replace('_', '-') / '三维评审.html', source / key / '三维评审.html', source / 'index.html']
        preview = next((p for p in preview_options if p.is_file()), None)
        assert preview, machine
        image_path, thumbnails[machine] = build_image(preview)
        case_top = max(own, key=own.get) if own else None
        controller_tier = stats.get('controller_voltage')
        if not controller_tier and isinstance(stats.get('controller_tier'), str):
            controller_tier = stats['controller_tier']
        formal = key in index['formal_keys']
        if formal:
            assert controller_tier, key
        source_tier_mismatch = bool(formal and controller_tier != target)
        notes = []
        if machine == 'I45':
            notes.append('负责人专项例外：QCV 电压保持，黑色车体＋细金边；不要求 QCV 机壳为主材。')
        elif machine.startswith('I01-') or machine.startswith('S') or machine in ['I20', 'I21', 'I22']:
            notes.append('累积升阶结构保留前阶方块与配色；出现多档机壳本身不等于错档。')
        if not target_count:
            notes.append('未检出目标档对应机壳，需核对；本页不替换任何材料。')
        elif target != 'MAX' and case_top != target and machine != 'I45':
            notes.append('累计数量最多的电压机壳并非目标档；需结合前阶保留和新增主体判断。')
        if source_tier_mismatch:
            notes.append('Controller 注册 tier 仍为 MAX，与目标映射未同步；不能据此断言实际 EU 工况错误。')
        version = entry.get('approved_version') or entry.get('candidate_version')
        if not version:
            match = re.search(r'(?:^|_)V(\d+)(?:_|$)', source.name)
            version = 'V' + match.group(1) if match else '现行归档'
        if machine.startswith('I01-'):
            version = '居中融合 V2（已恢复）'
        elif machine == 'I05':
            version = '滤芯移至 X6 · V5'
        elif machine.startswith('S'):
            version = '原地扩建 V1／R172 配色'
        if not formal and entry['status'] != 'candidate_unapproved':
            state = '外观已批准 · 待满批接入'
        elif formal:
            state = '正式资源已接入 · 游戏运行未验收'
        else:
            state = '候选已制作 · 未批准未接入'
        rows.append({'id': machine, 'key': key, 'name': names[machine], 'target': target,
                     'controller_tier': controller_tier, 'mismatch': source_tier_mismatch,
                     'formal': formal, 'candidate': entry['status'] == 'candidate_unapproved',
                     'status': state, 'version': str(version), 'total': total, 'casings': own,
                     'target_state': target_state, 'target_count': target_count,
                     'top_materials': counts.most_common(3), 'notes': notes,
                     'source': stats['source'], 'source_sha256': stats['source_sha256'],
                     'preview': href(preview), 'image_source': rel(image_path),
                     'image_sha256': sha(image_path), 'image_original': href(image_path)})
    rows.sort(key=lambda row: (row['id'][0] != 'I', int(re.search(r'\d+', row['id']).group()), int(row['id'].split('-')[-1]) if '-' in row['id'] else 0))
    assert len(rows) == 52 and sum(row['formal'] for row in rows) == 46
    assert sum(row['mismatch'] for row in rows) == 22 and sum(row['candidate'] for row in rows) == 3
    assert len(entries) == index['approved_structure_forms'] + 3
    made_ids = {row['id'] for row in rows}
    planning_rows = []
    for item in base_catalog:
        machine = item['id']
        if machine in made_ids:
            continue
        deferred = machine == 'I37'
        planning_rows.append({'id': machine, 'key': machine.lower(), 'name': names[machine],
                              'target': expected[machine], 'category': 'deferred' if deferred else 'planned',
                              'status': '延期 · 最后重做' if deferred else '已有名称与电压规划 · 当前建筑未定稿',
                              'version': '不采用旧稿' if deferred else '无现行批准建筑版本',
                              'preview': None, 'image_source': None, 'total': None,
                              'notes': ['负责人已延期；旧稿不作为现行结构预览。'] if deferred else
                                       ['名称和目标电压来自现行目录及映射；历史比例草图不冒充定稿建筑。'],
                              'source': rel(BASE)})
    requested_slots = []
    max_suggestions = [('MX-C01', '崩坏能物质转化器'), ('MX-C02', '物质谱系扫描仪'),
                       ('MX-C03', '构建图谱存储阵列'), ('MX-C04', '崩坏能精密重构机')]
    for group, count, tier, label in [('unnamed', 11, None, '待命名多方块席位'),
                                     ('replication', 4, 'MAX', '崩坏能复制系统需求席位')]:
        for number in range(1, count + 1):
            requested_slots.append({'id': None, 'key': f'{group}-{number:02d}',
                                    'display_id': f'{label} {number:02d}', 'name': '正式名称待定',
                                    'target': tier, 'category': group,
                                    'status': '需求已提出 · 名称、编号与建筑待设计',
                                    'version': '尚无建筑版本', 'preview': None, 'image_source': None, 'total': None,
                                    'notes': ['负责人本轮指定11台；电压、职责、名称及正式编号尚未确定。'] if group == 'unnamed' else
                                             ['参考旧IC2 UU物质复制体系，以崩坏能构建物品乃至多方块；四台各自职责、正式名称与编号尚未确定。'],
                                    'source': '负责人本轮需求' if group == 'unnamed' else rel(MAX_PLAN)})
            if group == 'replication':
                request_id, suggested_name = max_suggestions[number - 1]
                requested_slots[-1].update({'suggested_name': suggested_name, 'request_id': request_id})
    for row in rows:
        row['category'] = 'candidate' if row['candidate'] else 'approved'
    catalog = rows + planning_rows + requested_slots
    wonders = []
    for row in catalog:
        appearance = WONDER_CASINGS.get(row['id'])
        row['appearance_casing'] = appearance
        row['appearance_exception'] = bool(appearance)
        if appearance:
            row['appearance_casing_state'] = 'hk3gtl:voltage_machine_casing_' + appearance.lower()
            row['appearance_role'] = tiers[appearance]['role']
            row['notes'].append('负责人专项例外：运行电压保留' + row['target'] + '；主体改用' +
                                appearance + ' ' + tiers[appearance]['name'] + '机壳，按律者身份取色，不作运行改档。')
            wonders.append(row)
    assert len(wonders) == 15 and all(row['preview'] is None for row in wonders)
    assert len(planning_rows) == 17 and len(requested_slots) == 15 and len(catalog) == 84
    assert len({row['id'] for row in rows + planning_rows}) == 69
    assert [row['id'] for row in planning_rows if row['category'] == 'deferred'] == ['I37']
    assert all(row['preview'] is None and row['total'] is None for row in planning_rows + requested_slots)
    summary = {tier: [row['id'] for row in rows if row['target'] == tier] for tier in tier_order}
    planning_summary = {tier: {'named_catalog': sum(expected[item['id']] == tier for item in base_catalog),
                               'listed_requests': sum(row['target'] == tier for row in catalog),
                               'made': sum(row['target'] == tier for row in rows)} for tier in tier_order}
    custom_tier_gaps = {tier: max(0, 5 - planning_summary[tier]['named_catalog']) for tier in tier_order if tier != 'MAX'}
    assert sum(custom_tier_gaps.values()) == 19
    groups = []
    for tier in tier_order + [None]:
        p = tiers[tier] if tier else {'texture': None, 'main': None}
        tile = f'<img class="tile" src="{p["texture"]}" alt="{tier} 实际机壳纹理">' if p['texture'] else '<span class="tile native">待定</span>'
        subtitle = (f'{p["role"]} · {p["name"]}' if p['main'] else 'GTL 原生档 · 不属于新增十六色') if tier else '11个待命名席位 · 尚未分配电压和配色'
        cards = []
        for row in catalog:
            if row['target'] != tier:
                continue
            if not row.get('preview'):
                key = row['key']
                label = row.get('id') or row['display_id']
                title = f'{label} · {row["name"]}'
                reason = '已延期，旧稿不展示' if row['category'] == 'deferred' else '尚无现行定稿结构预览'
                suggestion = f'<small>助手建议名：{escape(row["suggested_name"])}</small><small>内部需求号 {row["request_id"]} · 非正式编号</small>' if row.get('suggested_name') else ''
                source_link = f'<a href="{href(ROOT / row["source"])}" target="_blank" rel="noopener">查看规划依据</a>' if row['source'] != '负责人本轮需求' else ''
                appearance_html = ''
                if row['appearance_exception']:
                    ap = tiers[row['appearance_casing']]
                    appearance_html = (f'<div class="appearance-casing"><img class="tile" src="{ap["texture"]}" alt="{escape(ap["role"])} {ap["name"]}真实机壳">'
                                       f'<div><b>外观主机壳：{row["appearance_casing"]} · {ap["name"]}</b><small>{escape(ap["role"])} · 运行电压仍为 {row["target"]}</small>'
                                       f'<code>{row["appearance_casing_state"]}</code></div></div>')
                cards.append(f'<section class="machine-card planning-card" id="preview-{key}" data-card="{key}">'
                             f'<div class="preview-placeholder"><strong>{escape(label)}</strong><span>{reason}</span></div>'
                             f'<div class="card-text"><b>{escape(title)}</b><small>{escape(row["status"])}</small>{suggestion}'
                             f'{appearance_html}<p class="muted">{escape(" ".join(row["notes"]))}</p><div class="preview-links">{source_link}</div></div></section>')
                continue
            cards.append(f'<section class="machine-card" id="preview-{row["id"]}" data-card="{row["id"]}">'
                         f'<a class="preview-picture" href="{row["preview"]}" target="_blank" rel="noopener" aria-label="打开 {row["id"]} {escape(row["name"], quote=True)} 的三维预览">'
                         f'<img class="build-preview" src="{thumbnails[row["id"]]}" loading="lazy" decoding="async" width="640" height="480" alt="{row["id"]} {escape(row["name"], quote=True)} 当前版本结构预览"></a>'
                         f'<div class="card-text"><b>{row["id"]} · {escape(row["name"])}</b><small>{escape(row["version"])}</small><small>{escape(row["status"])}</small>'
                         f'<div class="preview-links"><a href="{row["preview"]}" target="_blank" rel="noopener">打开三维预览</a>'
                         f'<a href="{row["image_original"]}" target="_blank" rel="noopener">查看原图</a><a href="#detail-{row["id"]}">核对用料</a></div></div></section>')
        gallery = '<div class="machine-gallery">' + ''.join(cards) + '</div>' if cards else '<p class="muted">当前已制作清单没有该档</p>'
        color = f'<code>{p["main"]}</code><small>纹理平均色 {p["mean"]}</small>' if p['main'] else ''
        group_count = f'<small>本页列明 {len(cards)} 项；按运行电压分组，奇观外观以卡片为准</small>'
        groups.append(f'<article class="tier" data-tier="{tier or "unassigned"}"><header>{tile}<div><b>{tier or "电压待定"}</b><small>{escape(subtitle)}</small>{color}{group_count}</div></header>{gallery}</article>')
    stamp = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    wonder_table = []
    for row in wonders:
        ap = tiers[row['appearance_casing']]
        wonder_table.append(f'<tr data-wonder="{row["id"]}"><td><b>{row["id"]}</b> · {escape(row["name"])}</td>'
                            f'<td><b>{row["target"]}</b><small>现行编排保留</small></td>'
                            f'<td><div class="appearance-casing"><img class="tile" src="{ap["texture"]}" alt="{ap["name"]}真实机壳">'
                            f'<div><b>{row["appearance_casing"]} · {ap["name"]}</b><small>{escape(ap["role"])} · {ap["main"]}</small>'
                            f'<code>{row["appearance_casing_state"]}</code></div></div></td></tr>')
    payload = json.dumps({'rows': rows, 'catalog': catalog, 'tiers': tiers}, ensure_ascii=False).replace('<', '\\u003c')
    html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>多方块全规划 · 名称、电压、配色与制作状态</title>
<style>*{box-sizing:border-box}body{margin:0;background:#111824;color:#e5eaf2;font:15px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1580px;margin:auto;padding:30px}h1{font-size:28px;line-height:1.3;margin:8px 0 16px}h2{font-size:20px;margin:32px 0 14px}p{margin:8px 0}small,.muted{color:#aebbd0}small{display:block}a{color:#b6d5ff}code{font:12px/1.5 ui-monospace,monospace;overflow-wrap:anywhere}.facts{display:flex;gap:30px;flex-wrap:wrap;border-block:1px solid #344153;padding:16px 0;margin:22px 0}.facts b{font-size:25px;display:block}.finding{border-left:3px solid #e4b974;padding:10px 18px;background:#1c2430;margin:14px 0}.tiers{display:grid;grid-template-columns:repeat(4,1fr);gap:0 24px}.tier{display:flex;gap:16px;padding:15px 0;border-bottom:1px solid #344153}.tier>div{flex:0 0 105px}.tier b{display:block}.tier p{margin:0;overflow-wrap:anywhere}.tile{width:54px;height:54px;image-rendering:pixelated;display:block;border:1px solid #586478}.native{display:grid;place-items:center;background:#28323f;font-size:12px}.tools{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:18px 0}input,select,button{font:inherit;background:#1d2938;color:inherit;padding:8px 10px;border:1px solid #50627b;border-radius:3px}input{min-width:220px;flex:1}button{cursor:pointer}.table-scroll{overflow:auto}table{border-collapse:collapse;width:100%;min-width:1150px}th,td{padding:13px 12px;border-bottom:1px solid #344153;vertical-align:top;text-align:left}thead th{position:sticky;top:0;background:#202b3b;font-weight:600}td:first-child{width:230px}td:nth-child(2){width:145px}td:nth-child(3){width:250px}.name{font-weight:600}.id{font-size:17px;font-weight:700}.muted{font-size:13px}.warn{color:#ffd08a}.good{color:#abcebd}.casing{display:flex;align-items:center;gap:8px;margin-bottom:6px}.casing img{width:30px;height:30px;image-rendering:pixelated}.casing small{font-size:12px}.swatch{display:inline-block;width:13px;height:13px;border:1px solid #9ba6b9;margin-right:5px}.source{margin-top:12px}details{font-size:13px;margin-top:7px}summary{cursor:pointer}footer{margin-top:28px;padding-top:18px;border-top:1px solid #344153}.empty{padding:24px;color:#ffd08a}[hidden]{display:none!important}@media(max-width:1000px){.tiers{grid-template-columns:repeat(2,1fr)}main{padding:20px}}@media(max-width:550px){.tiers{grid-template-columns:1fr}h1{font-size:23px}.facts{gap:18px}.tools>*{width:100%}.tier>div{flex-basis:115px}}@media print{body{background:white;color:black}main{padding:0}.tools{display:none}.table-scroll{overflow:visible}table{min-width:0;font-size:10px}th,td{padding:6px}thead th{position:static;background:#eee}.muted,small{color:#444}.finding{background:#fafafa}.warn{color:#9b4500}.tiers{grid-template-columns:repeat(3,1fr)}a{color:#123c77}}
</style><style>
.tiers{display:block}.tier{display:block;padding:22px 0}.tier>header{display:flex;align-items:center;gap:14px;margin-bottom:15px}.tier>header>div{display:flex;flex-wrap:wrap;align-items:center;gap:4px 18px}.tier>header b{font-size:21px}.tier>header small{max-width:290px}.machine-gallery{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}.machine-card{min-width:0;background:#172130;border:1px solid #344153;scroll-margin-top:16px}.preview-picture{display:block;background:#111824}.build-preview{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:contain}.card-text{padding:12px 14px}.card-text>b{line-height:1.5;min-height:45px}.preview-links{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:8px;font-size:13px}.table-scroll tr{scroll-margin-top:16px}@media(max-width:1150px){.machine-gallery{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:850px){.machine-gallery{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:550px){.machine-gallery{grid-template-columns:1fr}.tier>header{align-items:flex-start}.tier>header>div{display:block}.card-text>b{min-height:0}}@media print{.machine-gallery{grid-template-columns:repeat(3,minmax(0,1fr))}.machine-card{break-inside:avoid;background:white}.preview-links{display:none}.tier{break-inside:auto}.tier>header{break-after:avoid}}
</style><style>.preview-placeholder{aspect-ratio:4/3;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:10px;padding:20px;text-align:center;background:#131c29;border-bottom:1px dashed #45556b;color:#adbbce}.preview-placeholder strong{font-size:22px;color:#d5deea}.coverage{display:flex;flex-wrap:wrap;gap:8px}.coverage span{background:#202c3d;padding:4px 10px;border:1px solid #3c4e66}.jump-links{display:flex;flex-wrap:wrap;gap:8px 20px;margin:18px 0}</style><main>
<p class="muted">HK3GTL · __STAMP__ · Asia/Hong_Kong · 只读核对快照</p><h1>多方块全规划：名称、电压、配色与制作状态</h1>
<p>电压按负责人指定的映射方案；建筑以当前批准索引为准，I01 四阶采用已恢复的居中融合 V2。候选 I43–I45 单独标记，I37 延期且不读取旧稿。</p>
<div class="facts"><div><b>69</b>已有名称的目录形态</div><div><b>49</b>建筑外观已批准</div><div><b>3</b>已制作候选 I43–I45</div><div><b>17</b>具名但无现行定稿建筑</div><div><b>11</b>待命名规划席位</div><div><b>4</b>MAX崩坏能复制系统需求</div></div>
<p>已批准49项中：46项正式资源已接入，I40–I42共3项已批待满批接入。现有52张实图保持对应当前版本；其余项显示规划卡，不用旧稿或比例示意图充当定稿预览。</p>
<div class="finding"><b>本轮列明84项＝69个具名目录形态＋11个待命名席位＋4台MAX复制系统需求。</b>这不是84台已完成。原88台保守规划与各电压覆盖仍需对齐：保留原映射时，16个自定义电压各至少5台尚需补19个席位；新增MAX机器不能填这些自定义电压缺口。11个席位尚未分档，本页不擅定总目标或再造正式编号。</div>
<details><summary>查看84／88与分电压覆盖的计数依据</summary><p>原84下限＝4台MAX＋16档×5台；旧69目录含4台MAX与65个自定义电压形态。保持既有映射时，须补齐各档缺口19项，得到原88保守目标。若四台MAX复制系统全部额外新增且19个缺口仍保留，条件总数会是92；这只是条件测算，尚非负责人决定的新目标。</p><p class="muted">下列为69目录现行映射的逐档待补数量；11个未分档席位尚未抵扣：</p><div class="coverage">__GAPS__</div><p>I46–I53八个历史候选不在69目录中，本页不把它们擅自当作11个待命名席位。<a href="__NETWORK__">工业网络v6规划依据</a> · <a href="__MAX_PLAN__">四台MAX复制系统方案（含助手建议名）</a></p></details>
<nav class="jump-links"><a href="#wonder-palette">十五座奇观律者配色</a><a href="#gallery">名称与预览卡片</a><a href="#planning-detail">未定稿与待命名清单</a><a href="#material-detail">已制作结构用料核对</a></nav>
<style>.appearance-casing{display:flex;align-items:center;gap:10px;margin:10px 0}.appearance-casing .tile{flex:0 0 46px;width:46px;height:46px}.appearance-casing>div{min-width:0}.appearance-casing code{font-size:11px}.wonder-table{min-width:850px}.wonder-table td:first-child{width:38%}.wonder-table td:nth-child(2){width:17%}.wonder-table td:nth-child(3){width:45%}</style>
<h2 id="wonder-palette">十五座文明奇观：运行电压保留，主机壳按律者配色</h2><p>负责人已确认范围为W01–W15。下表左列运行电压沿用现行编排，右列才是今后建筑的主体机壳；机壳档名不改变机器供电、职责或进度。主体机壳须承担最多单一材料与视觉主材，不只作色带。此项改变设计规则，尚未生成或实装十五座建筑。</p><div class="table-scroll"><table class="wonder-table"><thead><tr><th>文明奇观</th><th>运行目标电压</th><th>律者外观主机壳 · 真实纹理</th></tr></thead><tbody>__WONDER_TABLE__</tbody></table></div><p class="muted">W01始源／人使用WFV水晶粉；W15凌虛晴使用CEV冠冕金。CIV龙鳞青对应贝拉，但现行15座名单没有贝拉奇观，H01休伯利安亦不并入。<a href="__DESIGN_RULES__">专项规则#29</a></p>
<div class="finding"><b>确实存在一处口径不同：</b>I01 四阶、I05–I18、S02–S05 的 Controller 注册 tier 仍为 MAX，目标映射已经是自定义电压。表格把两项分开；本次没有修改，也不把注册 tier 差异直接写成实际 EU 运行故障。</div>
<div class="finding"><b>建筑材料也有两处不符：</b>I14 目标 HDV，但现役正式蓝图使用 HCV 机壳 499 格、CIV 机壳 34 格，HDV 为 0；I15 目标 HDV，但现役正式蓝图没有任何新增电压机壳。这两台属于已冻结建筑，本页只标出，不擅自重做或换色。</div>
<p>色块是现有 PNG 的真实纹理；MAX 为目标实例 GT 原图首帧，未模拟动态染色、资源包或光影。HEX 是换色用的主色；“纹理平均色”只是纹理像素统计，不能当作新的批准色值。底图明暗使机壳比色卡更深，辅材和保留的前阶建筑还会改变整机观感。</p>
<h2 id="gallery">按目标电压查看全部名称与结构状态</h2><p>52个已制作形态可点击图片打开三维评审或原图。具名未定稿项保留目录名称与目标配色；11个待命名席位集中在“电压待定”，4台崩坏能复制系统集中在MAX。四台的既有助手建议名及内部需求号不视为正式命名、注册或建筑批准。</p>
<div class="tools"><input id="search" aria-label="搜索编号或名称" placeholder="搜索编号、名称、配色、材料或复制系统"><select id="tier" aria-label="目标电压"><option value="">全部电压</option>__OPTIONS__<option value="unassigned">电压待定（11）</option></select><select id="status" aria-label="状态筛选"><option value="">全部状态（84）</option><option value="approved">已批准（49）</option><option value="candidate">已制作候选（3）</option><option value="unfinalized">全部未定稿／需求（35）</option><option value="planned">具名建筑未定稿（16）</option><option value="deferred">延期重做（1）</option><option value="unnamed">待命名席位（11）</option><option value="replication">MAX复制系统（4）</option><option value="made">已有结构实图（52）</option><option value="mismatch">注册档未同步（22）</option></select><button type="button" id="print">打印 / 存为 PDF</button><span id="resultCount" aria-live="polite"></span></div>
<p id="empty" class="empty" hidden>没有符合筛选条件的机器。</p><section class="tiers">__GROUPS__</section>
<h2 id="planning-detail">32项未定稿建筑与待命名需求</h2><p>17个具名目录形态＋11个待命名席位＋4台MAX复制系统需求。I43–I45已有候选实图，列在前方卡片及后方52项用料表。下表没有现行建筑数量可统计，统一标明待定。</p><div class="table-scroll"><table><thead><tr><th>目录名称／需求席位</th><th>运行电压／外观主机壳</th><th>当前状态</th><th>预览／数量与依据</th></tr></thead><tbody id="planningRows"></tbody></table></div><p id="planning-empty" class="muted" hidden>当前筛选没有未定稿建筑或待命名需求。</p>
<h2 id="material-detail">52 个已制作形态的用料详细清单</h2><p class="muted">每行列出实际机壳数量及整机前三材料。累计数量不是“新增阶段主导”的判定；升级系列不能仅凭总量把前阶机壳当作错误。I45 黑金主材有负责人专项例外。</p>
<div class="table-scroll"><table><thead><tr><th>机器 / 当前版本</th><th>方案目标电压与配色</th><th>建筑实际电压机壳</th><th>整机前三材料</th><th>Controller 注册档与说明</th></tr></thead><tbody id="rows"></tbody></table></div>
<h2>当前不能混在一起的状态</h2><ul><li>I40、I41、I42：外观已批准，batch-10 为 3/5，尚未接入正式注册。</li><li>I43、I44、I45：候选已制作；尚未获得整机批准，不能记为已实装。</li><li>I37：负责人要求最后制作；本次不读取、不采用旧稿。</li><li>运行验收、配方最高电压、真实供能行为及安装 JAR 本轮未重新测试；此表对照的是当前源代码、批准建筑与实际材料统计。</li></ul>
<footer><b>核对依据</b><p><a href="__MAP__">负责人指定电压映射方案</a> · <a href="__INDEX__">当前批准归档索引</a> · <a href="__CODE__">旧控制器注册代码</a> · <a href="__LATE__">I19 以后注册代码</a> · <a href="__DATA__">本页逐台数据与校验身份</a></p><p class="muted">本轮新增十五座奇观的外观选材例外与逐台对照；未修改源贴图、实际结构、运行电压、建筑批准状态或游戏实例。材料统计来自各行列出的正式蓝图或当前材料清单；Controller 注册档由当前源码核查。</p></footer>
<script id="audit-data" type="application/json">__DATA_JSON__</script><script>
const {rows,catalog,tiers}=JSON.parse(document.getElementById('audit-data').textContent);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>n.toLocaleString('zh-CN');
const texture=t=>tiers[t]?.texture?`<img class="tile" src="${tiers[t].texture}" alt="${esc(t)}实际纹理">`:'';
function selection(){const q=document.getElementById('search').value.trim().toLowerCase(),tier=document.getElementById('tier').value,status=document.getElementById('status').value;
return catalog.filter(r=>(!tier||(r.target||'unassigned')===tier)&&(!status||r.category===status||status==='made'&&!!r.preview||status==='mismatch'&&r.mismatch||status==='unfinalized'&&r.category!=='approved')&&(!q||JSON.stringify(r).toLowerCase().includes(q)||JSON.stringify(tiers[r.target]||{}).toLowerCase().includes(q)||JSON.stringify(tiers[r.appearance_casing]||{}).toLowerCase().includes(q)));}
function renderMaterials(){let shown=0;const selected=selection(),filtered=selected.filter(r=>r.preview);
const visible=new Set(selected.map(r=>r.preview?r.id:r.key));document.querySelectorAll('[data-card]').forEach(card=>card.hidden=!visible.has(card.dataset.card));document.querySelectorAll('[data-tier]').forEach(group=>group.hidden=!selected.some(r=>(r.target||'unassigned')===group.dataset.tier));
document.getElementById('rows').innerHTML=filtered.map(r=>{shown++;const t=tiers[r.target];
const shells=Object.entries(r.casings).sort((a,b)=>b[1]-a[1]).map(([k,n])=>`<div class="casing">${texture(k)}<span><b>${esc(k)}</b> ${fmt(n)}<small>${esc(tiers[k]?.name||'')} · 占整机 ${(100*n/r.total).toFixed(1)}%</small></span></div>`).join('')||'<span class="muted">无新增十六色机壳</span>';
const target=texture(r.target)+`<b>${r.target}</b><small>${esc(t.name)}</small>`+(t.main?`<code><i class="swatch" style="background:${t.main}"></i>${t.main}</code>`:'');
const materials=r.top_materials.map(([s,n])=>`<div><code>${esc(s)}</code><small>${fmt(n)} · ${(100*n/r.total).toFixed(1)}%</small></div>`).join('');
const ctrl=r.controller_tier?`<b class="${r.mismatch?'warn':'good'}">${esc(r.controller_tier)}</b>${r.mismatch?'<small class="warn">与目标档未同步</small>':''}`:'<span class="muted">未正式注册</span>';
return `<tr id="detail-${r.id}" data-machine="${r.id}"><td><div class="id">${r.id}</div><div class="name">${esc(r.name)}</div><small>${esc(r.version)}</small><small>${esc(r.status)}</small><small>实体方块 ${fmt(r.total)}</small><a href="#preview-${r.id}">查看结构图片</a> · <a href="${r.preview}" target="_blank" rel="noopener">打开三维预览</a></td><td>${target}</td><td>${shells}<small>目标机壳 ${fmt(r.target_count)}</small></td><td>${materials}</td><td>${ctrl}${r.notes.map(n=>`<p class="muted">${esc(n)}</p>`).join('')}<details><summary>材料来源与哈希</summary><code>${esc(r.source)}</code><br><code>SHA256 ${r.source_sha256}</code></details></td></tr>`;}).join('');document.getElementById('resultCount').textContent=shown+' / 52';document.getElementById('empty').hidden=shown>0;}
function render(){renderMaterials();const selected=selection(),planned=selected.filter(r=>!r.preview);
document.getElementById('planningRows').innerHTML=planned.map(r=>{const label=r.id||r.display_id,t=r.appearance_exception?'<b>运行电压：'+esc(r.target)+'</b><small>现行编排保留</small><div class="appearance-casing">'+texture(r.appearance_casing)+'<div><b>外观：'+esc(r.appearance_casing)+'</b><small>'+esc(tiers[r.appearance_casing].name)+' · '+esc(r.appearance_role)+'</small><code>'+esc(r.appearance_casing_state)+'</code></div></div>':r.target?texture(r.target)+'<b>'+esc(r.target)+'</b><small>'+esc(tiers[r.target].name)+'</small>':'<span class="muted">电压与配色待定</span>';
const suggestion=r.suggested_name?'<small>助手建议名：'+esc(r.suggested_name)+'</small><small>'+esc(r.request_id)+'仅内部需求号</small>':'';
const source=r.source==='负责人本轮需求'?'<small>依据：负责人本轮需求</small>':'<a href="'+encodeURI('../../'+r.source)+'" target="_blank" rel="noopener">规划依据</a>';
return '<tr data-planning="'+r.key+'"><td><b>'+esc(label)+'</b><div>'+esc(r.name)+'</div>'+suggestion+'</td><td>'+t+'</td><td>'+esc(r.status)+'<p class="muted">'+r.notes.map(esc).join(' ')+'</p></td><td>无现行定稿预览；实体方块数待统计。<br>'+source+'</td></tr>';}).join('');
document.getElementById('planning-empty').hidden=planned.length>0;document.getElementById('resultCount').textContent=selected.length+' / '+catalog.length+' 项（实图 '+selected.filter(r=>r.preview).length+'）';document.getElementById('empty').hidden=selected.length>0;}
['search','tier','status'].forEach(id=>document.getElementById(id).addEventListener(id==='search'?'input':'change',render));document.getElementById('print').addEventListener('click',()=>print());render();window.AUDIT_READY=true;
</script></main></html>'''
    replacements = {'__STAMP__': stamp, '__GROUPS__': ''.join(groups), '__OPTIONS__': ''.join(f'<option>{tier}</option>' for tier in tier_order),
                    '__MAP__': href(MAP), '__INDEX__': href(INDEX.with_suffix('.html')),
                    '__CODE__': href(ROOT / 'src/main/java/com/sirin/hk3gtl/common/machine/Hk3MachinesImpl.java'),
                    '__LATE__': href(ROOT / 'src/main/java/com/sirin/hk3gtl/common/machine/Hk3LateIndustrialMachines.java'),
                    '__DATA__': href(LOG / 'audit-data.json'), '__DATA_JSON__': payload,
                    '__NETWORK__': href(NETWORK.with_suffix('.html')), '__MAX_PLAN__': href(MAX_PLAN),
                    '__WONDER_TABLE__': ''.join(wonder_table), '__DESIGN_RULES__': href(ROOT / 'rule/当前多方块设计规则.md'),
                    '__GAPS__': ''.join(f'<span>{tier}：{gap}</span>' for tier, gap in custom_tier_gaps.items())}
    for marker, replacement in replacements.items():
        html = html.replace(marker, replacement)
    assert not re.search(r'__[A-Z_]+__', html)
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    report = {'created_at': stamp, 'approved_forms': 49, 'formal_forms': 46, 'pending_approved': 3, 'candidates': 3,
              'controller_tier_mismatches': [row['id'] for row in rows if row['mismatch']], 'by_target_voltage': summary,
              'rows': rows, 'catalog': catalog, 'named_catalog_count': 69, 'planning_without_current_build': planning_rows,
              'unnamed_requests': 11, 'max_replication_requests': 4, 'listed_items': len(catalog),
              'original_conservative_target': load(NETWORK)['baseline']['structure_conservative_target'],
              'custom_voltage_gaps_before_unassigned_requests': custom_tier_gaps, 'planning_by_target_voltage': planning_summary,
              'wonder_appearance_casings': {row['id']: {'operating_voltage': row['target'], 'appearance_casing': row['appearance_casing'], 'state': row['appearance_casing_state'], 'role': row['appearance_role']} for row in wonders},
              'source_hashes': {rel(p): sha(p) for p in [INDEX, MAP, BASE, NETWORK, MAX_PLAN, PALETTE, ROOT / 'rule/当前多方块设计规则.md', LOG / 'material-audit.json']},
              'scope': '同步十五座奇观外观主机壳规则；未修改实体结构、源贴图、运行电压、建筑批准索引或实例。'}
    (LOG / 'audit-data.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': rel(OUT / 'index.html'), 'rows': len(rows), 'tier_mismatches': len(report['controller_tier_mismatches']),
                      'missing_target_casing': [row['id'] for row in rows if not row['target_count']],
                      'different_largest_voltage_casing': [row['id'] for row in rows if row['casings'] and max(row['casings'], key=row['casings'].get) != row['target']]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
