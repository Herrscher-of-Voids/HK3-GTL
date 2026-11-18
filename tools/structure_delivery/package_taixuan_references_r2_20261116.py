from collections import Counter
from datetime import datetime
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
from urllib.parse import parse_qs, urlsplit

from PIL import Image

from package_taixuan_references_20261116 import card, options


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_太虚山多角度参考_R2_20261116'
OLD = ROOT / 'deliveries/0005_W09_太虚山多角度参考_T1_20261116'
EXCLUDED = {
    'R2G06': (['O10', 'O11'], '与旧图的反侧殿角及瀑布间隙覆盖近同，未增加可判读的独立几何细节。'),
    'R2G07': (['O08'], '同为侧殿正面四门扇立面；人物与照明变化不另计新视面。'),
    'R2G14': (['R2O02'], '与本轮阶顶草台取景近同，保留R2O02，不重复计数。'),
    'R2O06': (['G14'], '与旧图同为夜间沿殿墙走廊机位，不因录制来源和人物变化重复计数。'),
    'R2O07': (['G15'], '与旧图同为夜间近距门扇剧情机位，没有独立新增结构。'),
}
PARTS = {
    '台阶与围栏': ['R2G01', 'R2G08', 'V04'],
    '八卦练武台': ['R2G02'],
    '山体与山路': ['R2G03', 'R2G04', 'R2G12', 'R2G13', 'R2G14', 'R2O01', 'R2O02', 'R2O05'],
    '殿宇与回廊': ['R2G05', 'R2G06', 'R2G07', 'R2O06', 'R2O07', 'R2O08', 'V03'],
    '桥梁与栈道': ['R2G09', 'R2G10', 'R2G11', 'R2G15', 'R2O03', 'R2O04'],
    '溪谷与莲池': ['V01', 'V02'],
    '庭院与香炉': ['R2O13', 'R2O15'],
}


def load(path):
    return json.loads(path.read_text('utf8'))


def video_id(source_url):
    url = urlsplit(source_url)
    return parse_qs(url.query)['v'][0] if url.path == '/watch' else url.path.rsplit('/', 1)[-1]


def normalize(ref, folder, group):
    return dict(id=ref['id'], subject=ref['subject'], view=ref['view'], note=ref['note'],
        source_url=ref['source_url'], seconds=ref['seconds'], resolution=ref['resolution'],
        kind=ref['kind'], era=ref['era'], file=f"{folder}/{ref['file']}",
        source_group=group, part=ref['part'], thumbnail=f"缩略图/{ref['id']}.jpg",
        sha256=hashlib.sha256((OUT / folder / ref['file']).read_bytes()).hexdigest(),
        source_title=ref['source_title'], scope=ref.get('scope', ''), collection='new')


def main():
    old_manifest = load(OLD / '参考清单.json')
    old_refs = [dict(ref, file=f"../{OLD.name}/{ref['file']}",
        thumbnail=f"../{OLD.name}/{ref['thumbnail']}", collection='old')
        for ref in old_manifest['references']]
    part_by_id = {ref_id: part for part, ids in PARTS.items() for ref_id in ids}
    game = [dict(ref, part=part_by_id[ref['id']], kind='玩家录制的官方游戏场景')
        for ref in load(OUT / '游戏补充/references.json')]
    official_source = load(OUT / '官方补充/references.json')
    official = official_source['references']
    official = [dict(ref, subject=ref['part'], view=ref['angle'], note=ref['visible_details'],
        seconds=ref['time_seconds'], kind=ref['source_nature'],
        era=ref.get('era', ref['scene_state']), part=part_by_id.get(ref['id'],
            '溪谷与莲池' if ref['id'] in ['R2O09', 'R2O10'] else
            '台阶与围栏' if ref['id'] == 'R2O11' else '殿宇与回廊'))
        for ref in official]
    static = load(OUT / '静态高清/references.json')
    static_folder = OUT / '静态官方补充'
    static_folder.mkdir(exist_ok=True)
    for ref in static:
        shutil.copy2(OUT / '静态高清' / ref['file'], static_folder / ref['file'])
    (static_folder / 'references.json').write_text(json.dumps(static, ensure_ascii=False, indent=2) + '\n', 'utf8')
    candidates = [*[normalize(ref, '游戏补充', '游戏补充') for ref in game],
        *[normalize(ref, '官方补充', '关卡与教程补充') for ref in official],
        *[normalize(ref, '静态官方补充', '7.4官方预告补充') for ref in static]]
    new_refs, excluded = [], list(official_source['excluded_duplicates'])
    hashes = {ref['sha256']: ref['id'] for ref in old_refs}
    for ref in candidates:
        if ref['id'] in EXCLUDED:
            duplicate_of, reason = EXCLUDED[ref['id']]
            excluded.append(dict(ref, duplicate_of=duplicate_of, reason=reason))
        elif ref['sha256'] in hashes:
            excluded.append(dict(ref, duplicate_of=[hashes[ref['sha256']]], reason='原图SHA-256相同，不重复计数。'))
        else:
            new_refs.append(ref)
            hashes[ref['sha256']] = ref['id']
    thumbs = OUT / '缩略图'
    thumbs.mkdir(exist_ok=True)
    for ref in new_refs:
        with Image.open(OUT / ref['file']) as im:
            im = im.convert('RGB')
            im.thumbnail((640, 360), Image.Resampling.LANCZOS)
            im.save(OUT / ref['thumbnail'], quality=88, optimize=True)
    refs = new_refs + old_refs
    missing = ['主殿完整后立面', '屋顶完整俯视', '门内房间与通道平面', '山峰完整背面',
        '连续上山路径', '太虚山全局三维布局', '石拱桥完整侧立面与拱腹']
    notes = [
        '本轮逐图比较旧31张与新增候选；同机位的人物、字幕、照明、昼夜和录制来源变化不另计。',
        '同一构件只有明显改变视角或新增可判读的几何细节时才作为新增参考。排除原图保留，理由独立记录。',
        '第20章羽渡尘记忆/意识场景、500年前夜景、完整训练场、7.4服装预告及舰桥分别标注，不拼作同一时刻的完整实景。',
        '7.4官方预告只补充莲池、浅溪、临崖楼、双桥和牌楼的可见形制，不据此冻结原训练场平面。',
        'R2G05提供殿侧低机位与悬岩；R2G15提供近桥头方柱、压顶和桥面，仍不等于完整桥侧与拱腹图证。',
        '二维插画和室内剧情背景只作可见形制参考；不可见面、各局部的连接坐标与跨版本组合属于项目补建设计。',
    ]
    source_counts = Counter(ref['source_group'] for ref in refs)
    source_counts_new = Counter(ref['source_group'] for ref in new_refs)
    manifest = dict(updated_at=datetime.now().astimezone().isoformat(), count=len(refs), total_count=len(refs),
        new_count=len(new_refs), old_count=len(old_refs), source_counts=dict(source_counts),
        source_counts_new=dict(source_counts_new), kind_counts=dict(Counter(ref['kind'] for ref in refs)),
        source_video_count=len({video_id(ref['source_url']) for ref in refs}),
        counting='只计独立选取的原始参考图；联系图、裁图、缩略图和重复视面不重复计数。旧31张原图与缩略图以相对链接引用。',
        layout_notes=notes, missing_views=missing,
        new_details=[dict(id=ref['id'], subject=ref['subject'], detail=ref['note']) for ref in new_refs],
        references=refs, excluded_references=excluded)
    (OUT / '参考清单.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', 'utf8')
    (OUT / 'excluded_references.json').write_text(json.dumps(excluded, ensure_ascii=False, indent=2) + '\n', 'utf8')
    css = re.search(r'<style>(.*?)</style>', (OLD / 'index.html').read_text('utf8'), re.S).group(1)
    cards = '\n'.join(card(ref).replace('<article class="card"',
        f'<article class="card" data-collection="{ref["collection"]}" data-source="{escape(ref["source_group"])}"')
        for ref in refs)
    counts = ''.join(f'<span>{escape(group)} {count}</span>' for group, count in source_counts_new.items())
    note_html = ''.join(f'<li>{escape(note)}</li>' for note in notes)
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:,"><title>W09 · 太虚山参考 R2</title><style>{css}</style></head><body>
<header><div class="eyebrow">0005 / W09 / 太虚山场景研究 / R2</div><h1>太虚山 · 细节补充参考</h1>
<p>本轮新增 {len(new_refs)} 张，合并旧参考31张，共 {len(refs)} 张。默认展示新增；原图、来源秒码、版本和可见范围逐项保留。</p>
<div class="counts"><span>新增 {len(new_refs)}</span><span>累计 {len(refs)}</span>{counts}<span>排除重复 {len(excluded)}</span></div>
<details class="notes"><summary>去重、场景时期与缺失视面</summary><ul>{note_html}</ul>
<p class="missing">仍缺：{escape('、'.join(missing))}。这些范围不能宣称已有完整官方三维依据。</p></details></header>
<main><div class="filters"><label>范围<select id="collection"><option value="new">本轮新增</option><option value="">全部参考</option><option value="old">旧31张</option></select></label>
<label>部位<select id="part"><option value="">全部部位</option>{options(dict.fromkeys(ref['part'] for ref in refs))}</select></label>
<label>来源分组<select id="source"><option value="">全部来源</option>{options(source_counts)}</select></label>
<label>时期与版本<select id="era"><option value="">全部时期</option>{options(dict.fromkeys(ref['era'] for ref in refs))}</select></label>
<output id="count">{len(new_refs)} / {len(refs)} 张</output></div>
<section class="gallery" aria-label="太虚山R2参考图册">{cards}</section>
<footer><a href="参考清单.json">完整清单与SHA-256</a> · <a href="excluded_references.json">重复视面排除记录</a> ·
<a href="../{OLD.name}/index.html">旧31张参考图册</a><p>联系图与缩略图不计入原图数量。未覆盖的背面、拱腹与整体连接保留为项目补建设计。</p></footer></main>
<script>const filters=['collection','part','source','era'].map(id=>document.getElementById(id)),cards=[...document.querySelectorAll('.card')];function filter(){{for(const card of cards)card.hidden=filters.some(input=>input.value&&card.dataset[input.id]!==input.value);document.getElementById('count').value=`${{cards.filter(card=>!card.hidden).length}} / ${{cards.length}} 张`;}}for(const input of filters)input.addEventListener('change',filter);filter();</script></body></html>'''
    (OUT / 'index.html').write_text(html, 'utf8')
    print(json.dumps(dict(new_count=len(new_refs), count=len(refs), source_counts=dict(source_counts),
        excluded=len(excluded), index=str(OUT / 'index.html')), ensure_ascii=False))


if __name__ == '__main__':
    main()
