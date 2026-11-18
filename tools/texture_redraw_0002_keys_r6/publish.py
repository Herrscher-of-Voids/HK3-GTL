import hashlib
import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / 'deliveries/0002贴图材质_神之键重绘_R6_20261114'
CHAT_ID = '01a1d68a-a994-7ac0-a48a-54c0f98fd54e'
DESIGNS = [
    ('imitation_star_of_eden', '仿制的伊甸之星', 'eden',
     '黑紫展翼炮甲与金色刃线包住炮身，前置红色重力核心；金色护爪位于核心后方，保留机械分件和侧厚。',
     'references/eden/original-game-weapon-biligame.jpg',
     'references/eden/eden-actual-game-angles-6-8-10-12s.png',
     [('社区BWIKI原版武器图', 'https://wiki.biligame.com/bh3/伊甸之星'),
      ('2018年玩家实机转角：约6、8、10、12秒', 'https://www.youtube.com/watch?v=kk_6o3jN4JM')]),
    ('imitation_oath_of_judah', '仿制的犹大的誓约', 'judah',
     '金色厚框、黑红嵌面的长十字匣，弯曲卷饰横臂、交叉嵌条、小十字尖与中央金色浮雕；不使用绿色宝石。',
     'references/judah/official-weapon.png', 'references/judah/angle-evidence.png',
     [('米哈游官方武器资料', 'https://bh3.mihoyo.com/gl/equip/weapon/598'),
      ('官方武器转角：约1、2、3秒', 'https://www.youtube.com/watch?v=-q8GRHEGKjA'),
      ('官方v5.4预告：约90–92秒展开形态辅助', 'https://www.youtube.com/watch?v=E606Ez4X5_g')]),
]


def contact_sheet(items):
    sheet = Image.new('RGB', (960, 630), '#1b2029')
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15)
    d.text((32, 16), '0002 · 神之键重绘 R6 · 两张候选待评审', font=font, fill='#eee6cf')
    for n, item in enumerate(items):
        x, y = 48 + n * 480, 66
        for cy in range(12):
            for cx in range(12):
                d.rectangle((x + cx * 32, y + cy * 32, x + cx * 32 + 31, y + cy * 32 + 31),
                            fill='#41434b' if (cx + cy) % 2 else '#31343c')
        with Image.open(DELIVERY / item['image']) as im:
            enlarged = im.resize((384, 384), Image.Resampling.NEAREST)
            sheet.paste(enlarged, (x, y), enlarged)
            sheet.paste(im, (x, 500), im)
        d.text((x, 464), item['name'], font=font, fill='#eee6cf')
        d.text((x + 78, 516), '左：原生64×64\n上：6倍最近邻预览', font=small, fill='#bbc2cc')
    d.text((32, 592), '独立像素重绘 · 透明PNG · 66张认可图保持 · 未打包／安装', font=small, fill='#bbc2cc')
    sheet.save(DELIVERY / 'contact-sheet.png')


def publish():
    items, cards = [], []
    for ident, name, group, design, reference, angles, sources in DESIGNS:
        path = DELIVERY / f'textures/item/{ident}.png'
        with Image.open(path) as im:
            size, mode, bounds = list(im.size), im.mode, list(im.getbbox())
        item = {'id': ident, 'name': name, 'image': path.relative_to(DELIVERY).as_posix(),
                'native_size': size, 'mode': mode, 'bbox': bounds,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'design': design, 'art_approved': False,
                'sources_file': f'references/{group}/sources.json'}
        items.append(item)
        links = ''.join(f'<li><a href="{html.escape(url)}" target="_blank" rel="noreferrer">{html.escape(label)}</a></li>'
                        for label, url in sources)
        cards.append(f'''<article><h2>{name}</h2><div class="stage"><img class="pixel" src="{item['image']}" alt="{name} R6"></div>
<p>{design}</p><p class="muted">原生64×64 · RGBA透明 · 待负责人评审</p>
<p><a href="{item['image']}" download>保存PNG</a> · <a href="{item['sources_file']}">来源与核对限制</a></p>
<details><summary>查看原作图片、多角度证据与来源</summary>
<img class="reference" src="{reference}" alt="原作参考"><ul>{links}</ul>
<img class="angles" src="{angles}" alt="原作多角度分镜">
<p class="muted">视频分镜原帧160×90，只核对轮廓、侧厚与前后关系。未确认的完整背面细纹不作精确复刻承诺。伊甸视频为玩家上传，犹大视频为官方发布。</p></details></article>''')
    manifest = {'revision': 'R6', 'date': '2026-11-14', 'conversation_number': '0002',
                'conversation_id': CHAT_ID, 'candidate_count': 2, 'art_approved': False,
                'accepted_total_unchanged': 66, 'jar_built': False, 'installed': False,
                'game_tested': False, 'reference_policy': '仅本轮两件经负责人授权使用原作网上图片和实际视频转角；不读取旧被否定候选作为设计参考。',
                'authoring': 'Pillow原生64×64坐标逐像素绘制；没有把参考图缩小为贴图，没有生成式图像API调用。',
                'scope': '仅两张物品材质及生成、评审入口；注册、配方与模型不变。',
                'items': items}
    (DELIVERY / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>0002 神之键材质 R6</title><style>
:root{color-scheme:dark;--zoom:4}*{box-sizing:border-box}body{margin:0;background:#151923;color:#e4e4e9;font:16px/1.7 "Microsoft YaHei",sans-serif}main{max-width:1180px;margin:auto;padding:28px}h1{font-size:30px;margin:8px 0}h2{font-size:22px}a{color:#e6be70}header,article{padding:24px;border:1px solid #3f414a;border-radius:12px;background:#202530}header{margin-bottom:22px}header p{margin:6px 0}.muted{color:#b9bfcb;font-size:14px}.controls{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin-top:18px}select{font:inherit;padding:4px 8px}section{display:grid;grid-template-columns:1fr 1fr;gap:22px}article{min-width:0}.stage{min-height:300px;overflow:auto;display:flex;align-items:center;justify-content:center;background-color:#31343c;background-image:conic-gradient(#41434b 25%,transparent 0 50%,#41434b 0 75%,transparent 0);background-size:32px 32px;border-radius:8px;padding:20px}.pixel{width:calc(64px * var(--zoom));height:calc(64px * var(--zoom));image-rendering:pixelated;flex-shrink:0}details{border-top:1px solid #494b55;padding-top:12px}summary{cursor:pointer}.reference{max-width:100%;max-height:320px;display:block;margin:16px auto}.angles{width:100%;display:block}li{margin:6px 0}footer{padding:24px 0;font-size:13px;color:#b9bfcb;word-break:break-all}@media(max-width:800px){section{grid-template-columns:1fr}main{padding:14px}header,article{padding:18px}}
</style><main><header><p class="muted">对话2 · 0002贴图材质 · R6 · 2026-11-14</p><h1>伊甸之星与犹大的誓约</h1>
<p>按《崩坏3》原版武器图与游戏转角重新绘制，采用清晰像素轮廓、分段金属明暗和原作配色。</p>
<p>两张新候选待评审；此前66张认可贴图保持。燃料R5独立待审。</p>
<div class="controls"><label>像素预览 <select id="zoom"><option>1</option><option>2</option><option selected>4</option><option>6</option><option>8</option></select> 倍</label>
<a href="contact-sheet.png">两张总览</a><a href="manifest.json">材质清单</a>
<a href="../0002贴图材质_审定重绘_R4_20261114/index.html">R4历史评审</a><a href="../0002贴图材质_燃料棒_R5_20261114/index.html">燃料R5</a></div></header><section>__CARDS__</section>
<footer>对话ID：__CHAT__<br>仅资源候选，未构建JAR、未安装、未操作游戏或存档；不计作游戏验收，不增加完成分。</footer></main>
<script>document.getElementById('zoom').onchange=e=>document.documentElement.style.setProperty('--zoom',e.target.value)</script></html>'''
    (DELIVERY / 'index.html').write_text(page.replace('__CARDS__', ''.join(cards)).replace('__CHAT__', CHAT_ID), encoding='utf-8')
    contact_sheet(items)
    return {'gallery': str(DELIVERY / 'index.html'), 'items': items}


if __name__ == '__main__':
    print(json.dumps(publish(), ensure_ascii=False))
