from collections import Counter
from datetime import datetime
import hashlib
from html import escape
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_太虚山多角度参考_T1_20261116'
PARTS = {
    '山体与山路': ['O01', 'O04', 'O12', *[f'G{i:02}' for i in range(1, 10)]],
    '殿宇与回廊': ['O03', 'O05', 'O06', 'O08', 'O09', 'O10', 'G10', 'G13', 'G14', 'G15'],
    '庭院与香炉': ['O02', 'O07', 'O11', 'O14', 'G11'],
    '八卦练武台': ['O13', 'G12'],
    '台阶与围栏': ['A01'],
    '舰桥远景': ['O15'],
}


def load(folder):
    return json.loads((OUT / folder / 'references.json').read_text('utf8'))


def official_refs(source):
    return [dict(id=r['id'], subject=r['part'], view=r['angle'], note=r['visible_details'],
        source_url=r['source_url'], source_title=r['source_title'], seconds=r['time_seconds'],
        resolution=r['resolution'], kind=r['source_nature'],
        era='4.6版本太虚山舰桥' if r['id'] == 'O15' else
            '3.7版本二维宣传插画' if r['id'] == 'O03' else '3.7版本完整训练场',
        file='官方参考/' + r['file'], source_group='官方参考', source_channel=r['channel'])
        for r in source['references']]


def timecode(seconds):
    return f'{int(seconds // 60):02}:{seconds % 60:04.1f}'


def timed_url(ref):
    url = urlsplit(ref['source_url'])
    query = dict(parse_qsl(url.query))
    query['t'] = f"{ref['seconds']:g}s"
    return urlunsplit((url.scheme, url.netloc, url.path, urlencode(query), url.fragment))


def options(values):
    return ''.join(f'<option value="{escape(value)}">{escape(value)}</option>' for value in values)


def card(ref):
    label = f"{ref['id']} · {ref['subject']}"
    scope = f"<p class=scope>{escape(ref['scope'])}</p>" if 'scope' in ref else ''
    return f'''<article class="card" data-part="{escape(ref['part'])}" data-kind="{escape(ref['kind'])}" data-era="{escape(ref['era'])}">
<a class="image" href="{escape(ref['file'])}" target="_blank" rel="noopener"><img src="{escape(ref['thumbnail'])}" loading="lazy" alt="{escape(label + '，' + ref['view'])}"></a>
<div class="caption"><div class="tags"><span>{escape(ref['part'])}</span><span>{escape(ref['kind'])}</span></div>
<h2>{escape(label)}</h2><p class="angle">{escape(ref['view'])} · {ref['resolution'][0]} × {ref['resolution'][1]} · {timecode(ref['seconds'])}</p>
<p class="era">{escape(ref['era'])}</p><p>{escape(ref['note'])}</p>{scope}
<div class="links"><a href="{escape(ref['file'])}" target="_blank" rel="noopener">查看原图</a><a href="{escape(timed_url(ref))}" target="_blank" rel="noopener">来源 {timecode(ref['seconds'])}</a></div>
<p class="source">{escape(ref['source_title'])}</p><details><summary>文件与 SHA-256</summary><p>{escape(ref['file'])}</p><code>{ref['sha256']}</code></details></div></article>'''


def main():
    official = load('官方参考')
    refs = official_refs(official)
    refs.extend(dict(r, source_group='游戏场景') for r in load('游戏场景'))
    refs.extend(dict(r, source_group='建筑补充', era='7.2版本PV，太虚山训练场细节补充')
                for r in load('建筑补充'))
    thumbnails = OUT / '缩略图'
    thumbnails.mkdir(exist_ok=True)
    part_by_id = {ref_id: part for part, ids in PARTS.items() for ref_id in ids}
    for ref in refs:
        ref['part'] = part_by_id[ref['id']]
        ref['thumbnail'] = f"缩略图/{ref['id']}.jpg"
        source = OUT / ref['file']
        ref['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        with Image.open(source) as image:
            image = image.convert('RGB')
            image.thumbnail((640, 360), Image.Resampling.LANCZOS)
            image.save(OUT / ref['thumbnail'], quality=88, optimize=True)

    missing = ['主殿完整后立面', '屋顶完整俯视', '门内房间与通道平面', '山峰背面', '连续上山路径', '太虚山全局三维布局']
    notes = [*official['layout_notes'],
        'O03为二维插画，只用于可见侧楼与瀑布关系；O15为舰桥展示，分开记录。',
        'G01–G09为第20章入山关卡；G10–G15为500年前月夜回忆中的完整建筑局部，分开记录时代与照明。',
        'A01仅补充7.2版本PV中的石阶、围栏与石灯。各版本画面不拼作同一时刻的完整全景。']
    source_counts = Counter(r['source_group'] for r in refs)
    kind_counts = Counter(r['kind'] for r in refs)
    sources = list(dict.fromkeys((r['source_title'], urlsplit(r['source_url']).query.split('&')[0]) for r in refs))
    manifest = dict(updated_at=datetime.now().astimezone().isoformat(), count=len(refs),
        source_counts=dict(source_counts), kind_counts=dict(kind_counts), source_video_count=len(sources),
        counting='仅计31张独立选取原始帧；联系图、裁图与本页缩略图不重复计数。',
        layout_notes=notes, missing_views=missing, references=refs)
    (OUT / '参考清单.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', 'utf8')

    cards = '\n'.join(card(ref) for ref in refs)
    missing_html = '、'.join(missing)
    note_html = ''.join(f'<li>{escape(note)}</li>' for note in notes)
    html = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:,"><title>W09 · 太虚山多角度参考</title><style>
:root{color-scheme:dark;font-family:system-ui,"Microsoft YaHei",sans-serif;background:#111519;color:#e8ebed}*{box-sizing:border-box}body{margin:0}a{color:#cbb78b;text-underline-offset:3px}header,main{max-width:1560px;margin:auto;padding:26px 28px}header{padding-bottom:12px}.eyebrow{font-size:12px;letter-spacing:.16em;color:#acb5bd}h1{font-size:34px;font-weight:600;margin:12px 0}header p{color:#aeb9c1;line-height:1.7;margin:8px 0}.counts{display:flex;flex-wrap:wrap;gap:9px;margin:20px 0}.counts span{padding:6px 11px;border:1px solid #354149;border-radius:4px;font-size:13px}.notes{border-top:1px solid #303a42;padding-top:14px;line-height:1.7;color:#aeb9c1}.notes summary{cursor:pointer;color:#d7dfe4}.notes ul{padding-left:20px}.notes li{margin:7px 0}.missing{color:#c9b385}main{padding-top:10px}.filters{display:flex;flex-wrap:wrap;align-items:center;gap:14px;margin:0 0 22px;padding:15px 0;border-bottom:1px solid #303a42}label{display:flex;align-items:center;gap:8px;font-size:13px;color:#b7c2ca}select{font:inherit;padding:8px 10px;background:#1c242a;border:1px solid #3a4852;border-radius:4px;color:#e8ebed;max-width:340px}.filters output{margin-left:auto;color:#acb5bd;font-size:13px}.gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.card{border:1px solid #303c45;border-radius:6px;overflow:hidden;background:#182027;display:flex;flex-direction:column}.image{display:block;background:#0c1014;aspect-ratio:16/9}.image img{width:100%;height:100%;display:block;object-fit:contain}.caption{padding:16px;line-height:1.6;font-size:14px}.caption h2{font-size:17px;font-weight:600;margin:10px 0 5px}.caption p{margin:7px 0}.tags{display:flex;flex-wrap:wrap;gap:6px}.tags span{font-size:11px;color:#bcc9d1;background:#26343e;padding:2px 6px;border-radius:3px}.angle,.era{font-size:12px;color:#acbac3}.scope,.source{font-size:12px;color:#8fa0ab}.links{display:flex;gap:18px;margin-top:14px}.caption details{margin-top:12px;font-size:11px;color:#879ba8}.caption summary{cursor:pointer}.caption code{overflow-wrap:anywhere;font-size:10px}.caption details p{overflow-wrap:anywhere}[hidden]{display:none!important}footer{padding:26px 0;color:#8fa0ab;font-size:13px}@media(max-width:1120px){.gallery{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:700px){header,main{padding-left:16px;padding-right:16px}h1{font-size:27px}.gallery{grid-template-columns:1fr}.filters{align-items:flex-start}.filters label{width:100%;justify-content:space-between}.filters select{width:75%}.filters output{margin:0}}
</style></head><body><header><div class="eyebrow">0005 / W09 / 太虚山场景研究</div><h1>太虚山 · 多角度参考</h1>
<p>31张原始参考帧，按部位、来源与时代核对山体、殿宇和庭院细节。点击图片查看原图，来源链接定位对应秒码。</p>
<div class="counts"><span>官方参考 15</span><span>游戏关卡 15</span><span>建筑补充 1</span><span>来源视频 6</span></div>
<details class="notes" open><summary>场景版本与布局依据</summary><ul>__NOTES__</ul><p class="missing">缺失视面：__MISSING__。对应模型部分须标为项目补建设计。</p></details>
</header><main><div class="filters"><label>部位<select id="part"><option value="">全部部位</option>__PARTS__</select></label><label>来源类别<select id="kind"><option value="">全部类别</option>__KINDS__</select></label><label>时代与版本<select id="era"><option value="">全部时代</option>__ERAS__</select></label><output id="count">31 / 31 张</output></div>
<section class="gallery" aria-label="太虚山参考图册">__CARDS__</section><footer><a href="参考清单.json">完整参考清单与哈希</a> · 原图31张，缩略图与联系图分别保存。</footer></main>
<script>const filters=['part','kind','era'].map(id=>document.getElementById(id)),cards=[...document.querySelectorAll('.card')];function filter(){for(const card of cards)card.hidden=filters.some(input=>input.value&&card.dataset[input.id]!==input.value);document.getElementById('count').value=`${cards.filter(card=>!card.hidden).length} / ${cards.length} 张`;}for(const input of filters)input.addEventListener('change',filter);</script></body></html>'''
    for token, value in dict(NOTES=note_html, MISSING=escape(missing_html), PARTS=options(PARTS),
            KINDS=options(kind_counts), ERAS=options(dict.fromkeys(r['era'] for r in refs)), CARDS=cards).items():
        html = html.replace('__' + token + '__', value)
    (OUT / 'index.html').write_text(html, 'utf8')
    print(json.dumps(dict(images=len(refs), sources=dict(source_counts), thumbnails=str(thumbnails),
        index=str(OUT / 'index.html')), ensure_ascii=False))


if __name__ == '__main__':
    main()
