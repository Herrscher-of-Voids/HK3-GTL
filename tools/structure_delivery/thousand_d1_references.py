from html import escape
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_千人人偶_独立像素模型_D1_20261117'
refs = json.loads((OUT/'references/animation/references.json').read_text('utf8'))
study = json.loads((OUT/'references/animation/study.json').read_text('utf8'))
sections = []
for section in study['sections']:
    observations = ''.join('<li>'+escape(s)+'</li>' for s in section['observations'])
    sections.append('<section><h2>'+escape(section['label'])+'</h2><ul>'+observations+'</ul></section>')
frames = []
for frame in refs['references']:
    full = 'references/animation/'+frame['file']
    thumb = 'references/animation/'+frame['thumbnail']
    caption = escape('；'.join(frame['observations']))
    frames.append(f'<figure><a href="{full}" target="_blank"><img src="{thumb}" loading="lazy" alt="{caption}"></a>'
                  f'<figcaption><b>{frame["id"]} · {frame["time_seconds"]}秒 · {escape(frame["angle"])}</b><p>{caption}</p>'
                  f'<a href="{escape(frame["source_url"])}" target="_blank">官方动画对应时间</a></figcaption></figure>')
html = '''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>千人人偶 · 原作参考</title>
<style>
*{box-sizing:border-box}body{margin:28px auto;max-width:1600px;padding:0 24px;background:#151922;color:#ece5d6;font:14px/1.7 system-ui}
a{color:#e5c381}h1{font-size:24px}h2{font-size:17px}.study{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
.study section{border-top:1px solid #61523d}ul{padding-left:20px}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:22px}
figure{margin:0;background:#202430;border:1px solid #544838}figure img{width:100%;display:block}figcaption{padding:14px}p{margin:8px 0}
</style>
<a href="index.html">返回方块模型</a>
<h1>千人人偶 · 金发裙装形态</h1>
<p>主要依据为《薪炎永燃》官方动画，以下24张原帧来自同一视频的9个镜头窗口。细节裁切与连续帧不另计独立来源。</p>
<p><a href="https://www.youtube.com/watch?v=n1rjfW-5HAE" target="_blank">Honkai Impact 3rd · Everlasting Flames</a></p>
<div class="study">'''+''.join(sections)+'''</div>
<h2>多角度原帧</h2><div class="gallery">'''+''.join(frames)+'''</div>
<p><a href="references/animation/references.json">逐帧来源记录</a> · <a href="references/animation/study.json">形制观察</a></p>
</html>
'''
(OUT/'参考图册.html').write_text(html, 'utf8')
