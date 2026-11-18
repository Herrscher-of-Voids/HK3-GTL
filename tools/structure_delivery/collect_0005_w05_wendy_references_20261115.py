from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html import escape
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w05-wendy-reference-study-20261115'
OUT = ROOT / 'deliveries/0005_W05_温蒂游戏翼形参考校准_20261115'
CACHE = Path('C:/Users/OWNER/.cache/hk3gtl-w05-reference-videos')
SOURCES = {
    'DuosaVLkT-g': dict(title='Honkai Impact 3rd - Wendy boss 0 hit taken',
        kind='Boss三维实录', movie='DuosaVLkT-g.mp4'),
    'EbbIwbPZOw0': dict(title="[1440p60fps] Wendy's Vengeance [Honkai Impact 3 ASIA]",
        kind='Boss三维实录', movie='EbbIwbPZOw0-clean.mp4'),
    'mkzUClgwHeQ': dict(title='Honkai Impact 3rd - Boss Fight #31 (Umbral Rose Vs. Wendy)',
        kind='Boss三维实录', movie='mkzUClgwHeQ.mp4'),
    'ChF4eAhFIMU': dict(title='Wendy chapter 3 boss fight | Honkai Impact 3rd',
        kind='游戏内剧情CG', folder='scout-story'),
    'PaTCNDTgO00': dict(title='Honkai Impact 3rd Main Story Chapter 3 CG Cutscenes',
        kind='游戏内剧情CG', folder='scout-cg'),
    'cypcVgaysTU': dict(title='Wendy becomes the 4th Herrscher',
        kind='游戏内剧情CG', folder='scout-cg'),
}
SELECTION = {
    'DuosaVLkT-g': [18, 20, 24, 28, 40, 56, 60, 92, 104, 124],
    'EbbIwbPZOw0': [137, 149, 151, 197, 233, 241, 245, 257, 289, 293],
    'mkzUClgwHeQ': [65, 75, 85, 105, 125, 145, 165, 175],
    'ChF4eAhFIMU': [315, 327, 331],
    'cypcVgaysTU': [52.5],
}
EXCLUDED = [
    dict(video='DuosaVLkT-g', seconds=68, reason='翼面太小，不增加有效形体信息。'),
    dict(video='DuosaVLkT-g', seconds=132, reason='翼尖出画且强特效遮挡。'),
    dict(video='EbbIwbPZOw0', seconds=143, reason='强攻击特效遮挡。'),
    dict(video='EbbIwbPZOw0', seconds=249, reason='强攻击特效遮挡。'),
    dict(video='mkzUClgwHeQ', seconds=205, reason='旋风及攻击遮挡，不保留。'),
    dict(video='PaTCNDTgO00', seconds=102, reason='与ChF4eAhFIMU的315秒为同一剧情构图。'),
    dict(video='PaTCNDTgO00', seconds=106, reason='与前一剧情构图相同，仅背景变色。'),
    dict(video='PaTCNDTgO00', seconds=113.3, reason='与ChF4eAhFIMU的331秒为同一剧情构图。'),
]
FINDINGS = [
    'A2/A3现有翼部属于原创工业转译，不能作为温蒂游戏内翅膀的复刻；十四片等距独立羽板没有本轮画面依据。',
    'Boss实录中的青绿翼面从腰背附近集中向两侧展开，呈宽薄、扫掠、分叉轮廓，长短与尖齿间距并不整齐。',
    '青绿发光面、蓝青边缘和暗色内轮廓应从原帧取形；原稿银白厚包边、环形轴座与粗立柱属于工业增设。',
    '剧情CG能辅助辨认尖齿与薄面，但它不是可自由旋转的Boss三维转台，不能用它独自补全背部体积。',
    '下一版应先重画成对整体翼面与集中翼根，再把承力设施放到独立后方；扩展基座本轮保持。',
]
LIMITS = [
    '初选40张已逐张查看，剔除5张遮挡或出画和3张同剧情重复，保留32张；不同动作与局部不等于32个独立机位。',
    '六个公开上传来源均为玩家转录或剪辑，本轮未将其标为官方账号发布；画面内容与上传者身份分别记录。',
    '保留28张Boss三维实录、4张剧情CG，来自5个上传；另1个来源的3张重复CG剔除。mkzUClgwHeQ仅640×360，原尺寸保留，只辅助动作与方向。',
    '战斗中存在遮挡、运动模糊和特效，不能据此硬数固定羽片数量；干净背面转台与可确证的原生模型源尚缺。',
    '本轮仅校准参考，没有改建筑几何、运行蓝图、JAR或游戏实例，也没有新增游戏验收。',
]


def collect(item):
    index, video, seconds = item
    source = SOURCES[video]
    stem = f'{video}-{seconds:g}'
    target = OUT / '参考原帧' / f'{stem}.jpg'
    if 'movie' in source:
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(seconds),
            '-i', str(CACHE / source['movie']), '-frames:v', '1', '-pix_fmt', 'yuvj420p',
            '-q:v', '2', '-threads', '1', '-y', str(target)], check=True)
    else:
        original = (LOG / source['folder'] / f'{video}-{seconds:03g}.jpg'
            if video == 'ChF4eAhFIMU' else
            LOG / source['folder'] / f'{video}-t{int(seconds * 1000):06d}.png')
        target = target.with_suffix(original.suffix)
        shutil.copy2(original, target)
    with Image.open(target) as im:
        resolution = list(im.size)
    return dict(id=f'R{index:02d}', video_id=video, seconds=seconds,
        kind=source['kind'], title=source['title'], label='战斗姿态与翼面' if index <= 28 else '剧情翼形辅助',
        source_url=f'https://www.youtube.com/watch?v={video}&t={seconds:g}s',
        file=str(target.relative_to(OUT)).replace('\\', '/'), resolution=resolution,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        limitation='原画面存在战斗遮挡，动作辅助，不单独判定精确翼片数。' if index <= 28 else
            '剧情CG，不是Boss三维模型转台；相同剧情在不同上传中可能重复。')


def main():
    (OUT / '参考原帧').mkdir(parents=True, exist_ok=True)
    work = [(i, video, seconds) for i, (video, seconds) in enumerate(
        ((v, t) for v, times in SELECTION.items() for t in times), 1)]
    with ThreadPoolExecutor(4) as pool:
        rows = list(pool.map(collect, work))
    excluded_folder = LOG / '剔除原帧'
    excluded_folder.mkdir(exist_ok=True)
    retained_files = {r['file'] for r in rows}
    for path in (OUT / '参考原帧').iterdir():
        if str(path.relative_to(OUT)).replace('\\', '/') not in retained_files:
            shutil.move(path, excluded_folder / path.name)
    shutil.copy2(ROOT / 'deliveries/0005_W05_温蒂风翼渴望之心_A3扩展基座_20261115/风翼近景.png',
        OUT / 'A3待修正翼部.png')
    manifest = dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        conversation='0005', conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
        image_count=len(rows), boss_frames=28, story_cg_frames=4, source_videos=5,
        initially_reviewed_frames=40, excluded=EXCLUDED,
        visual_reviewed=True, sources=SOURCES, findings=FINDINGS, limitations=LIMITS, images=rows,
        building_geometry_modified=False, jar_built=False, installed=False, game_verified=False)
    for path in [OUT / '参考清单.json', LOG / 'reference-manifest.json']:
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', 'utf8')
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 19)
    for start in range(0, len(rows), 8):
        sheet = Image.new('RGB', (1920, 1340), '#101f27')
        draw = ImageDraw.Draw(sheet)
        for i, row in enumerate(rows[start:start + 8]):
            with Image.open(OUT / row['file']) as original:
                im = original.convert('RGB')
            im.thumbnail((960, 270))
            x, y = i % 2 * 960, i // 2 * 335
            sheet.paste(im, (x + (960 - im.width) // 2, y))
            draw.text((x + 16, y + 275), f'{row["id"]} · {row["video_id"]} · {row["seconds"]:g}秒 · {row["kind"]}',
                font=font, fill='white')
            draw.text((x + 16, y + 303), f'原帧 {row["resolution"][0]}×{row["resolution"][1]}；点击图集可查原图与来源',
                font=font, fill='#a8c1c8')
        sheet.save(OUT / f'原帧总览{start // 8 + 1}.jpg', quality=94)
    selected = [rows[i - 1] for i in [2, 12, 24, 28, 30, 32]]
    board = Image.new('RGB', (1800, 1170), '#101f27')
    draw = ImageDraw.Draw(board)
    for i, row in enumerate(selected):
        with Image.open(OUT / row['file']) as original:
            im = original.convert('RGB')
        im.thumbnail((900, 335))
        x, y = i % 2 * 900, i // 2 * 390
        board.paste(im, (x + (900 - im.width) // 2, y))
        draw.text((x + 15, y + 343), f'{row["id"]} · {row["kind"]} · {row["seconds"]:g}秒', font=font, fill='white')
    board.save(OUT / '翼形关键参考.jpg', quality=94)
    cards = ''.join(f'<article data-kind="{r["kind"]}" data-source="{r["video_id"]}"><a href="{r["file"]}" target="_blank"><img loading="lazy" src="{r["file"]}" alt="{r["id"]} {r["kind"]}"></a><h3>{r["id"]} · {r["seconds"]:g}秒 · {r["kind"]}</h3><p>原帧 {r["resolution"][0]}×{r["resolution"][1]}</p><p>{r["limitation"]}</p><a href="{escape(r["source_url"])}" target="_blank">{escape(r["title"])} · 对应时间点 ↗</a></article>' for r in rows)
    findings = ''.join(f'<li>{escape(t)}</li>' for t in FINDINGS)
    limits = ''.join(f'<li>{escape(t)}</li>' for t in LIMITS)
    options = ''.join(f'<option value="{video}">{escape(SOURCES[video]["title"])}</option>' for video in SELECTION)
    html = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>0005 W05 · 温蒂原作翼形校准</title><style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{background:#0c171f;color:#e6f2f1;font:15px/1.7 system-ui;margin:24px auto;max-width:1720px;padding:0 24px}}a{{color:#7de7d5}}h1{{margin-bottom:4px}}h2{{font-size:21px}}h3{{font-size:16px;margin:8px 0}}p{{margin:5px 0}}.note,article,.summary{{background:#152832;border:1px solid #28444c;border-radius:8px;padding:16px}}.summary{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.summary img{{width:100%;height:350px;object-fit:contain;background:#0c141b}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:16px}}article img{{width:100%;aspect-ratio:16/9;object-fit:contain;background:#050c10}}article p{{color:#adc6cc}}select,button{{padding:9px;background:#18343c;color:#e6f2f1;border:1px solid #3a626a;border-radius:4px}}.filters{{position:sticky;top:0;background:#0c171ff5;padding:12px 0;z-index:2;display:flex;gap:12px;flex-wrap:wrap}}[hidden]{{display:none}}@media(max-width:800px){{.summary{{grid-template-columns:1fr}}.grid{{grid-template-columns:1fr}}}}</style><header><p>0005 多方块设计 · W05 · 2026-11-15</p><h1>温蒂的游戏翅膀，重新按原画面看清</h1><p>40张原帧：33张Boss三维实录 + 7张游戏内剧情CG。六个公开视频，保留时间与原始分辨率。</p></header><section class="summary"><div><h2>A3现有翼部：需重做</h2><img src="A3待修正翼部.png" alt="A3工业羽片候选"><p>十四片等距独立羽板、白色包边、环形轴座：本项目增设，不能当作温蒂原生翼型。</p></div><div><h2>游戏原帧：先校准轮廓与翼根</h2><a href="参考原帧/DuosaVLkT-g-20.jpg" target="_blank"><img src="参考原帧/DuosaVLkT-g-20.jpg" alt="游戏内Boss正面原帧"></a><p>R02：Boss三维模型的登场正面；本轮未把剧情插画冒充模型转台。</p></div></section><h2>本轮结论</h2><ul>{findings}</ul><details class="note" open><summary>数量、来源与缺证范围</summary><ul>{limits}</ul><a href="参考清单.json">逐帧来源、时间、分辨率与SHA256</a></details><div class="filters"><select id="kind"><option value="">全部画面</option><option>Boss三维实录</option><option>游戏内剧情CG</option></select><select id="source"><option value="">全部来源</option>{options}</select><button id="reset">重置</button><span id="count">40张</span></div><section class="grid">{cards}</section><script>const kind=document.getElementById('kind'),source=document.getElementById('source');function filter(){{let n=0;document.querySelectorAll('article').forEach(e=>{{e.hidden=(kind.value&&e.dataset.kind!==kind.value)||(source.value&&e.dataset.source!==source.value);if(!e.hidden)n++;}});document.getElementById('count').textContent=n+'张';}}kind.onchange=source.onchange=filter;document.getElementById('reset').onclick=()=>{{kind.value=source.value='';filter();}};</script></html>'''
    html = html.replace('40张原帧：33张Boss三维实录 + 7张游戏内剧情CG。六个公开视频',
        '32张保留原帧：28张Boss三维实录 + 4张游戏内剧情CG。五个公开视频')
    html = html.replace('>40张</span>', '>32张</span>')
    (OUT / 'index.html').write_text(html, 'utf8')
    print(json.dumps(dict(output=str(OUT), images=len(rows), boss_frames=28, cg_frames=4), ensure_ascii=False))


if __name__ == '__main__':
    main()
