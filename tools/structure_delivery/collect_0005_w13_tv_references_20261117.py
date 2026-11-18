from datetime import datetime, timezone
from html import escape
from pathlib import Path
import hashlib
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W13_侵蚀电视原作参考_R1_20261117'
CACHE = Path('C:/Users/OWNER/.cache/hk3gtl-w13-reference-videos')
VIDEO = 'RUe2BDz6RO4'
PICKS = [
    (42, '主体', '大电视与环境全景', '远处粉红巨眼屏幕、厚重横向机壳与下垂电缆共同构成主体；前景爱莉希雅提供体量参照。'),
    (40, '主体', '巨眼屏幕与前框', '矩形显示区、厚边框与粉红眼形图案；画面边缘的板状设备与残片遮住部分机壳。'),
    (44, '主体', '深机壳侧面近景', '侧面向后延伸，多层凸起板件与折角壳面清楚可见；左侧露出巨眼屏幕。'),
    (137, '主体', '前斜仰视与下方电缆', '可见显示区、侧面壳体、底部板件及多条粗电缆；人物位于左前方。'),
    (140, '主体', '巨眼完整显示图案', '中央同心圆眼、上下尖角及左右星芒；原片显示表面保留细密扫描纹理。'),
    (145, '主体', '屏幕与电缆透视', '人物及细电缆叠在眼形图案前方，可对照显示区与线束的空间层次。'),
    (38, '环境', '旧电视堆俯视', '多种尺寸的旧电视堆成不规则高塔，屏幕朝向各异；用于研究周边堆叠。'),
    (16, '环境', '周边旧显示器与旋钮', '局部显示器、圆旋钮、按键及机壳接缝；属于环境设备。'),
    (10, '环境', 'CRT雪花与圆角玻璃', '环境旧电视的弧形玻璃边缘、雪花和前方电线；用于玻璃与显示细节参考。'),
    (134, '环境', '旧电视墙正面', '大小不同的圆角屏、旋钮与厚壳逐层叠放，保留旧电视墙的杂乱结构。'),
    (135, '环境', '电缆束与电视墙', '多股线束从两侧伸出，人物被电缆围住，后方为旧电视墙。'),
    (180, '演出', '故障段落中的独立老电视', '黑白红故障演出中的旧电视：厚框、红色代码屏、侧格栅与上方设备；用于局部构造参考。'),
]


def main():
    (OUT / 'frames').mkdir(parents=True, exist_ok=True)
    (OUT / 'thumbnails').mkdir(exist_ok=True)
    info = json.loads((CACHE / f'{VIDEO}.info.json').read_text('utf8'))
    source = {k: info[k] for k in ['title', 'channel', 'channel_id', 'channel_is_verified', 'upload_date', 'duration']}
    source['url'] = f'https://www.youtube.com/watch?v={VIDEO}'
    refs = []
    for i, (seconds, group, title, note) in enumerate(PICKS, 1):
        rid = f'V{i:02d}'
        file = f'frames/{rid}-{seconds:03d}s.jpg'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(seconds),
                        '-i', str(CACHE / f'{VIDEO}.mp4'), '-frames:v', '1', '-q:v', '2', '-y', str(OUT / file)], check=True)
        im = Image.open(OUT / file).convert('RGB')
        resolution = list(im.size)
        im.thumbnail((640, 360), Image.Resampling.LANCZOS)
        thumb = f'thumbnails/{rid}.jpg'
        im.save(OUT / thumb, quality=92)
        refs.append(dict(id=rid, group=group, title=title, observations=note, seconds=seconds,
                         timecode=f'{seconds // 60:02d}:{seconds % 60:02d}', file=file, thumbnail=thumb,
                         source_url=source['url'] + f'&t={seconds}s', resolution=resolution,
                         sha256=hashlib.sha256((OUT / file).read_bytes()).hexdigest(), reviewed=True))
    findings = [
        '主体依据V01至V06：粉红眼形宽屏、厚前框、向后延伸的深机壳、侧面层叠板件、下方电缆。',
        '主体周边存在大量不同尺寸的旧电视；V07至V11用于环境与局部设备参考。',
        'V12来自黑白红故障演出，单独记录其厚框与格栅，不用该镜头判断正常照明下的配色。',
        '绿色环境照明、屏幕粉光及镜头透视均影响外观；实际比例在后续像素模型阶段继续校准。',
    ]
    manifest = dict(created_at=datetime.now(timezone.utc).isoformat(), count=len(refs),
                    status='原作截图参考', source=source, references=refs, findings=findings,
                    counting='12张选取原帧，来自同一官方短片；其中主体6张、环境5张、故障演出1张。缩略图与选览不另计数量。',
                    missing_views=['主体无遮挡正交背面', '主体顶部完整俯视', '内部结构与精确尺寸'],
                    model_status='本轮只收集原片参考，像素模型尚未制作。',
                    previous_candidate=dict(id='W13 A1', status='负责人否定并停用，历史文件保留'))
    (OUT / 'references.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
    sheet = Image.new('RGB', (1920, 400 * 4), '#15181f')
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(refs):
        x, y = i % 3 * 640, i // 3 * 400
        sheet.paste(Image.open(OUT / row['thumbnail']), (x, y))
        draw.text((x + 10, y + 367), f"{row['id']} {row['timecode']} · {row['title']}", fill='#eee8ef', font=font)
    sheet.save(OUT / '截图选览.jpg', quality=92)
    sections = []
    for group in ['主体', '环境', '演出']:
        cards = []
        for row in refs:
            if row['group'] == group:
                cards.append(f'<figure><a href="{row["file"]}" target="_blank"><img src="{row["thumbnail"]}" alt="{escape(row["title"])}" loading="lazy"></a>'
                             f'<figcaption><b>{row["id"]} · {row["timecode"]} · {escape(row["title"])}</b><p>{escape(row["observations"])}</p>'
                             f'<a href="{row["file"]}" target="_blank">1920×1080 原图</a> · <a href="{row["source_url"]}" target="_blank">官方视频对应时间</a></figcaption></figure>')
        sections.append(f'<section><h2>{group}</h2><div class="gallery">{"".join(cards)}</div></section>')
    html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>W13 · 侵蚀之律者老电视原作截图</title><style>
*{box-sizing:border-box}body{max-width:1600px;margin:28px auto;padding:0 24px;background:#12151b;color:#eee8ef;font:15px/1.7 system-ui}
a{color:#efa2cf}h1{font-size:27px}h2{font-size:21px;margin-top:32px}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:22px}
figure{margin:0;background:#1e222b;border:1px solid #4b3c49}figure img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain}figcaption{padding:16px}p{margin:8px 0}header{border-bottom:1px solid #55404f;padding-bottom:20px}
</style><header><h1>侵蚀之律者 · 老式大电视</h1>
<p>《因你而在的故事》官方动画原帧，12张，1920×1080。主体6张，环境5张，故障演出1张。</p>
<p><a href="https://www.youtube.com/watch?v=RUe2BDz6RO4" target="_blank">Honkai Impact 3rd 官方动画</a> · <a href="截图选览.jpg" target="_blank">全部截图选览</a> · <a href="references.json">来源、时间码与哈希</a></p>
<p>点击画面打开未经裁切、调色的原尺寸截图。镜头覆盖正面、侧面与前斜仰视；环境设备及黑白红故障段落分别标明。</p></header>'''
    html += ''.join(sections) + '<footer><h2>后续模型的形体依据</h2><ul>' + ''.join('<li>' + escape(s) + '</li>' for s in findings) + '</ul></footer></html>'
    (OUT / 'index.html').write_text(html, 'utf8')
    for p in (OUT / 'frames').glob('check-*.jpg'):
        p.unlink()
    print(json.dumps(dict(directory=str(OUT), count=len(refs), resolution=refs[0]['resolution']), ensure_ascii=False))


if __name__ == '__main__':
    main()
