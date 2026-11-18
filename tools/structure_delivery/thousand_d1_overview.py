import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_千人人偶_独立像素模型_D1_20261117'
background = (21, 25, 34)
overview = Image.new('RGB', (1600, 1200), background)
draw = ImageDraw.Draw(overview)
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 23)
for file, box, label in [
    ('整体斜视.png', (20, 65, 615, 1180), '千人人偶 · 独立方块模型'),
    ('蒙眼额纹.png', (650, 65, 1580, 620), '双锥发髻、蒙眼与三叶额纹'),
    ('分节金手.png', (650, 680, 1580, 1180), '五指关节与黑金裙纹'),
]:
    source = Image.open(OUT/file).convert('RGB')
    bbox = ImageChops.difference(source, Image.new('RGB', source.size, background)).getbbox()
    source = source.crop(bbox)
    x1, y1, x2, y2 = box
    fit = ImageOps.contain(source, (x2-x1, y2-y1), Image.Resampling.NEAREST)
    overview.paste(fit, (x1+(x2-x1-fit.width)//2, y1+(y2-y1-fit.height)//2))
    draw.text((x1+10, y1-42), label, font=font, fill='#e7cb8b')
draw.line((630, 24, 630, 1180), fill='#4b4438', width=1)
overview.save(OUT/'细节总览.png')
record = json.loads((OUT/'manifest.json').read_text('utf8'))
record['visual_review'] = [
    '已查看完整正面、斜视、背面与左侧，头身及裙腿连续。',
    '已查看头脸、后脑、裙纹、金手和膝腿关节近景。',
    '嘴部细缝加粗后重新生成模型及全部11视角。',
    '关节保持独立构件；原始连接体积保存在VOX与独立关节构件.npz。',
]
record['files'] = {name: dict(bytes=(OUT/name).stat().st_size, sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest())
                   for name in ['千人人偶-独立方块模型-D1.vox', '完整整数格模型.npz', '独立关节构件.npz', '关节与提线.json', '细节总览.png', '预览记录.json']}
(ROOT/'logs/0005-thousand-d1-20261117/delivery.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf8')
for name in [Path(__file__).name, 'preview_0005_thousand_d1_20261117.mjs', 'thousand_d1_references.py']:
    shutil.copyfile(Path(__file__).with_name(name), OUT/'生成脚本'/name)
