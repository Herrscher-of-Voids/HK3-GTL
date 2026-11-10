# -*- coding: utf-8 -*-
"""Publish four W03 candidates without changing formal scope or system scores."""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile
from PIL import Image, ImageDraw, ImageFont
from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W03_C3_眼形莫比乌斯_四方案_20261108'
LOG = ROOT / 'logs/w03-eye-c3-20261108'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
CODES = ['3H', '3U', '5H', '5U']
LABELS = ['三环 · 水平亚空之矛', '三环 · 从下向上刺出', '五环 · 水平亚空之矛', '五环 · 从下向上刺出']


def load(p): return json.loads(p.read_text('utf8'))
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def gallery(manifests):
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 32)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
    for file, output in [('完整预览.png', '四方案对比.png'), ('正面眼形.png', '四方案正面对比.png')]:
        canvas = Image.new('RGB', (1880, 2080), '#101b2b'); draw = ImageDraw.Draw(canvas)
        draw.text((28, 18), '穹界·虚数锚定环  C3  /  三环与五环 × 水平与向上', font=font, fill='#f0e8ff')
        draw.text((28, 67), '两侧飘带与翼片已移除 · 180°莫比乌斯带 · 下方浓缩崩坏能晶体 · 待审候选', font=small, fill='#c8b4dd')
        for i, (code, label) in enumerate(zip(CODES, LABELS)):
            x, y = 20 + (i % 2) * 940, 116 + (i // 2) * 976
            draw.rounded_rectangle((x, y, x + 918, y + 956), radius=12, fill='#1d293b')
            draw.text((x + 18, y + 12), code + '  ' + label, font=font, fill='#f5ecff')
            picture = Image.open(OUT / code / file).convert('RGB').resize((900, 900), Image.Resampling.LANCZOS)
            canvas.paste(picture, (x + 9, y + 53))
        canvas.save(OUT / output, optimize=True)
    cards = []
    for code, label, m in zip(CODES, LABELS, manifests):
        cards.append(f'''<article><h2>{code} · {label}</h2><a class="picture" href="{code}/完整预览.png" target="_blank"><img src="{code}/完整预览.png" data-code="{code}" alt="{label}" width="1800" height="1800"></a><p>{m['blocks']:,} 方块 · 561×529×636（宽×深×高）</p><nav><a href="{code}/w03/三维评审.html">旋转查看完整三维</a><a href="{code}/index.html">本案资料与多视图</a><a href="{code}/w03/{m['name']}.nbt">NBT</a><a href="{code}/w03/{m['name']}.schem">Schematic</a></nav></article>''')
    text = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 C3 · 莫比乌斯眼形四方案</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101b2b;color:#eee9f8;font:16px/1.75 system-ui}main{max-width:1700px;margin:auto;padding:25px}h1{margin:5px 0}h2{font-size:21px;margin:0;padding:13px 17px}a{color:#d2b4ff;text-decoration:none}a:hover{text-decoration:underline}.note{border-left:3px solid #b999ec;background:#202c40;padding:14px 18px}.tools{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:22px 0}button{font:inherit;color:#ddd;background:#26364b;border:1px solid #54637b;border-radius:7px;padding:7px 20px;cursor:pointer}button[aria-pressed=true]{color:#171027;background:#cfb2f4;border-color:#cfb2f4}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}article{background:#19273b;border:1px solid #354257;border-radius:12px;overflow:hidden}article img{width:100%;height:auto;display:block;background:#111c2c}article p,article nav{padding:0 17px}article nav{display:flex;gap:18px;flex-wrap:wrap;padding-bottom:18px}.foot{margin:26px 0;color:#c0b6ce}small{color:#bda4df}@media(max-width:800px){.grid{grid-template-columns:1fr}main{padding:16px}h1{font-size:25px}}</style>
<main><small>HK3GTL / W03 / C3 / 2026-11-08</small><h1>穹界·虚数锚定环 · 莫比乌斯眼形</h1><p class="note">两侧飘带与翼片全部移除。环的中心线保持正圆，实体带面沿周长扭转180°；24颗晶体有8种大小，以8列×3行等间距、前后交错排列在外环下方三分之一。六柄黑白橙亚空之矛分别尝试水平向内与从下向上刺出。下方按环数分行、矛向分列，所有镜头与比例一致。</p>
<div class="tools" role="group" aria-label="同时切换四案视角"><button data-file="完整预览.png" aria-pressed="true">斜视整体</button><button data-file="正面眼形.png" aria-pressed="false">正面眼形</button><button data-file="侧面层次.png" aria-pressed="false">侧面层次</button><button data-file="环带近景.png" aria-pressed="false">扭转环带近景</button></div><section class="grid">CARDS</section>
<p class="foot"><a href="四方案对比.png">四案拼图</a> · <a href="四方案正面对比.png">正面拼图</a> · <a href="W03-C3-四方案离线包.zip">完整离线预览与结构下载</a> · <a href="设计核验.json">设计核验</a> · <a href="comparison.json">四案坐标与清单</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">内测5固定审计</a></p>
<p class="foot">四份NBT与Schematic逐格回读通过；环带为连续闭合实体，独立构件无重叠。全部模型按真实包围盒导出，未按名义673×529×321裁切。实际高度636格，超过普通主世界384格建高；本轮交付外观候选，未批准、未部署，未作客户端实测。C2历史原件保留，既定74项与系统完成度不变。</p></main>
<script>for(const b of document.querySelectorAll('[data-file]'))b.onclick=()=>{for(const x of document.querySelectorAll('[data-file]'))x.setAttribute('aria-pressed',String(x===b));for(const img of document.querySelectorAll('[data-code]')){const p=img.dataset.code+'/'+b.dataset.file;img.src=p;img.parentElement.href=p;}};</script></html>'''.replace('CARDS', ''.join(cards))
    (OUT / 'index.html').write_text(text, 'utf8')


def main():
    qa = load(LOG / 'viewer-qa.json'); assert qa['passed'] and len(qa['variants']) == 4
    connectivity = load(LOG / 'mobius-connectivity.json'); assert connectivity['passed']
    manifests = [load(OUT / code / 'manifest.json') for code in CODES]
    results = []
    for code, m in zip(CODES, manifests):
        v = load(OUT / code / 'verification.json')
        assert v['passed'] and v['readback']['geometry_nbt_schematic_per_block_equal']
        assert v['component_clearance']['intersection_pairs_after'] == 0
        for extension in ['nbt', 'schem']:
            assert sha(OUT / code / 'w03' / (m['name'] + '.' + extension)) == v['nbt_schem_sha256'][extension]
        bounds = m['clearance']['part_bounds_blueprint']
        low, high = bounds['ring:210']['min'][1], bounds['ring:210']['max'][1]
        band_top = low + (high - low) / 3
        crystals = [b for n, b in bounds.items() if n.startswith('crystal:')]
        assert all(low <= b['min'][1] <= b['max'][1] <= band_top for b in crystals)
        results.append(dict(code=code, blocks=m['blocks'], size_xyz=m['size'],
            rings=len(m['rings']), spear_direction=m['comparison']['spear_direction'],
            exports_sha256=v['nbt_schem_sha256'], independent_overlap_pairs=0,
            actual_outer_ring_lower_third_y_blueprint=[low, band_top],
            actual_crystal_y_blueprint=[min(b['min'][1] for b in crystals), max(b['max'][1] for b in crystals)],
            all_crystals_within_actual_lower_third=True, no_nominal_clipping=True))
    prior = ROOT / 'deliveries/W03_C方案_正圆与净空_C2_20261108'
    prior_m, prior_v = load(prior / 'manifest.json'), load(prior / 'verification.json')
    for extension in ['nbt', 'schem']:
        assert sha(prior / 'w03' / (prior_m['name'] + '.' + extension)) == prior_v['nbt_schem_sha256'][extension]
    receipt = dict(passed=True, variants=results, mobius_connectivity=connectivity,
        viewer=qa, old_c2_exports_unchanged=True, approved=False, installed=False,
        game_verified=False, desktop_used=False)
    save(OUT / '设计核验.json', receipt)
    gallery(manifests)
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for name in ['w03_eye_c3_20261108.py', 'build_w03_eye_c3_20261108.py',
                 'capture_w03_eye_c3_20261108.mjs', 'publish_w03_eye_c3_20261108.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, scripts / name)
    archive = OUT / 'W03-C3-四方案离线包.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file() and p != archive: z.write(p, p.relative_to(OUT).as_posix())
    with zipfile.ZipFile(archive) as z: assert z.testzip() is None
    baseline = LOG / 'before-report'; baseline.mkdir(exist_ok=False)
    original = {p: p.read_bytes() for p in [REPORT / 'index.html', REPORT / 'current-summary.json']}
    for p, value in original.items(): (baseline / p.name).write_bytes(value)
    old = load(REPORT / 'current-summary.json'); data = deepcopy(old)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    state = '2026-11-08 · W03 C3：移除左右飘带与翼刃，改为180°半扭转莫比乌斯眼形环系；三环／五环分别配水平／向上六矛，交付四份同镜头预览。24颗8种大小的浓缩崩坏能晶体等间距分布在环实际高度下方三分之一。四案均561×529×636格、约657万–666万方块；完整NBT／Schematic逐格回读、环带六邻接连续闭合及独立构件零重叠通过。636格高度超出普通主世界建高，仍为未批准、未部署的外观候选。'
    work = data['current_work']
    work['design_candidate_history'].append(deepcopy(work['design_candidate']))
    work['state'] = state
    work['next_turn'] = '由负责人比较C3三环／五环与水平／向上刺矛；选定后继续外观细化。普通主世界建高适配与游戏成型另行验收。'
    work['design_candidate'] = dict(id='W03', version='C3', title='莫比乌斯眼形四方案',
        status='candidate_waiting_user_review', approved=False, installed=False, game_verified=False,
        base_selected='C2 → 负责人五点外观修改', variants=results,
        preview=str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/'),
        receipt=str((OUT / '设计核验.json').relative_to(ROOT)).replace('\\', '/'),
        archive=str(archive.relative_to(ROOT)).replace('\\', '/'), archive_sha256=sha(archive),
        no_nominal_clipping=True, standard_overworld_build_height_exceeded=True, updated_at=now)
    data['report_updated_at'] = now
    data['systems'].sort(key=lambda s: s['percent'])
    assert data['systems'] == old['systems'] and data['overall_percent'] == old['overall_percent']
    assert data['multiblock_scope'] == old['multiblock_scope']
    for field in ['hyperion_performance', 'native_distance_and_package', 'approved_structure_designs', 'structure_batch']:
        assert work[field] == old['current_work'][field]
    html = original[REPORT / 'index.html'].decode('utf8')
    html, n = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + escape(now) + ' · W03 C3莫比乌斯眼形四方案</p>', html, count=1); assert n == 1
    anchor = '<main><h1>系统完成度 · 低到高 · 固定入口</h1>'; assert anchor in html
    html = html.replace(anchor, anchor + '<p class="notice" id="w03-c3-current">' + escape(state) + ' <a href="../../deliveries/W03_C3_眼形莫比乌斯_四方案_20261108/index.html">C3四方案对照预览</a></p>', 1)
    html, n = re.subn(r'(?<=id="audit-data">).*?(?=</script>)', lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S); assert n == 1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>', html, re.S)[1]) == data
    assert re.findall(r'<details class="system" data-id="([^"]+)"', html) == [s['id'] for s in data['systems']]
    publisher().publish_transaction({REPORT / 'index.html': html, REPORT / 'current-summary.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, original)
    rule = ROOT / 'rule/当前多方块设计规则.md'
    shutil.copy2(rule, LOG / 'rule-before-c3.backup')
    note = '''

## 2026-11-08 W03 C3莫比乌斯眼形四方案（负责人最新外观修改）

- 负责人要求移除左飘带与右翼片，让正面更像眼睛；环改为莫比乌斯带。六柄亚空之矛分别水平与从下向上刺出；三环与五环分别预览，本轮形成3H、3U、5H、5U四案，不代替负责人选择或批准。
- 保留C1黑白橙亚空之矛局部造型。每个实体环沿圆形中心线半扭转180°，接缝反转闭合；六邻接连通为一体。保留核心、基座、24枚外围浮游柱、天顶冠冕及八处通用接口；左右飘带与翼刃为本轮明确移除内容。
- 紫色立方体解释为能力下极度压缩的浓缩崩坏能晶体；24颗采用8种尺寸，8列×3行等间距、纵深交错。外环实际Y137–573，下方三分之一Y137–282⅓；全部晶体实际Y152–278，均在此范围。
- 四案均561×529×636（宽深高），约657万–666万实体方块，15种真实材料。完整导出，不裁切；独立构件体素中心至少8格距离，零重叠。NBT与Schematic逐格回读、20张离线图像及完整载荷核验通过；未操作游戏或桌面。
- 保留C2与r219部署；636格高的普通主世界适配未完成，本轮未批准、未部署、不计客户端成型或系统100%。固定74项、批准57／正式52、36系统原分与r219包体／远景证据不变。
- 四案入口：deliveries/W03_C3_眼形莫比乌斯_四方案_20261108/index.html。
'''
    rule.write_bytes(rule.read_bytes() + note.encode('utf8'))
    result = dict(passed=True, variants=4, screenshots=20, system_scores_unchanged=36,
        overall_percent=data['overall_percent'], ascending_order=True, formal_scope_unchanged=True,
        r219_and_approved_structures_unchanged=True, old_c2_exports_unchanged=True,
        archive_sha256=sha(archive), audit_html_sha256=sha(REPORT / 'index.html'),
        audit_summary_sha256=sha(REPORT / 'current-summary.json'))
    save(LOG / 'publication-verification.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
