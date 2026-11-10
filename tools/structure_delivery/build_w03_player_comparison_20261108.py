# -*- coding: utf-8 -*-
"""把五个 AI 的最新 W03 静态全景拼成可直接转发的反馈图。"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W03_五AI最新方案_玩家反馈对比_20261108'
BG, PANEL, LINE = '#0c1321', '#121b2b', '#35425a'
WHITE, MUTED, ACCENT = '#f2f5fa', '#b2bed1', '#c9b8ff'
FONTS = Path('C:/Windows/Fonts')
ENTRIES = [
    ('A', 'GPT / Codex', 'V1', '四极折界门庭', 'W03_穹界虚数锚定环_四极折界门庭_V1_20261107'),
    ('B', 'DeepSeek', 'V5 · 完整边界修复', '悬天瞳冠', 'W03_完整几何边界修复_20261108/V5'),
    ('C', 'Gemini', 'V4 · 完整边界修复', '曲翼深渊神殿', 'W03_完整几何边界修复_20261108/V4'),
    ('D', 'Claude Opus 5.5', 'V6', '八锚穹仪', 'W03_穹界虚数锚定环_八锚穹仪_Claude原案_V6_20261108'),
    ('E', 'Gork', 'V7', '四锚穹盖', 'W03_穹界虚数锚定环_四锚穹盖_Gork原案_V7_20261108'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ('msyhbd.ttc' if bold else 'msyh.ttc')), size)


def text(draw, xy, value, size, fill=WHITE, bold=False, max_width=None):
    face = font(size, bold)
    assert max_width is None or draw.textlength(value, font=face) <= max_width, value
    draw.text(xy, value, font=face, fill=fill)


def card(canvas, box, entry, source, crop):
    x, y, w, h = box
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((x, y, x+w, y+h), radius=24, fill=PANEL, outline=LINE, width=2)
    text(draw, (x+30, y+15), entry[0], 82, ACCENT, True)
    text(draw, (x+122, y+25), entry[1], 43, bold=True, max_width=w-150)
    text(draw, (x+124, y+86), entry[2], 28, MUTED, max_width=w-150)
    text(draw, (x+34, y+h-65), entry[3], 36, max_width=w-68)
    # 五张图使用同一个留白裁切框，仅移除背景，保留全部有色像素。
    image = ImageOps.contain(source.crop(crop), (w-36, h-218), Image.Resampling.LANCZOS)
    canvas.paste(image, (x+(w-image.width)//2, y+139+(h-218-image.height)//2))


def main():
    OUT.mkdir(exist_ok=False)
    images, records, bounds = [], [], []
    for letter, author, version, name, relative in ENTRIES:
        path = ROOT / 'deliveries' / relative / '完整预览.png'
        image = Image.open(path).convert('RGB')
        background = image.getpixel((0, 0))
        bbox = ImageChops.difference(image, Image.new('RGB', image.size, background)).getbbox()
        assert image.size == (2200, 1500) and bbox
        images.append(image)
        bounds.append(bbox)
        records.append(dict(letter=letter, author=author, version=version, name=name,
                            source=path.relative_to(ROOT).as_posix(), sha256=digest(path)))
    crop = (max(0, min(b[0] for b in bounds)-45), max(0, min(b[1] for b in bounds)-45),
            min(2200, max(b[2] for b in bounds)+45), min(1500, max(b[3] for b in bounds)+45))
    assert all(crop[0] <= b[0] and crop[1] <= b[1] and crop[2] >= b[2] and crop[3] >= b[3] for b in bounds)

    landscape = Image.new('RGB', (3840, 2320), BG)
    draw = ImageDraw.Draw(landscape)
    text(draw, (80, 36), 'HK3GTL  /  W03  建筑外观征集', 36, ACCENT, True)
    text(draw, (80, 96), '空之律者 · 穹界·虚数锚定环', 68, bold=True)
    text(draw, (84, 188), '五个 AI · 各自最新方案 · 统一静态全景', 32, MUTED)
    w, h, gap, top = 1204, 948, 32, 270
    for i, (entry, image) in enumerate(zip(ENTRIES, images)):
        card(landscape, (80+(i % 3)*(w+gap), top+(i//3)*(h+gap), w, h), entry, image, crop)
    x, y = 80+2*(w+gap), top+h+gap
    draw = ImageDraw.Draw(landscape)
    draw.rounded_rectangle((x, y, x+w, y+h), radius=24, fill=PANEL, outline=LINE, width=2)
    for dy, value, size, color, bold in [
        (64, '轮到你来挑了', 57, WHITE, True),
        (167, '最喜欢哪一个？', 45, WHITE, False),
        (249, 'A  /  B  /  C  /  D  /  E', 65, ACCENT, True),
        (392, '喜欢它的轮廓、配色，还是空间感？', 34, MUTED, False),
        (475, '最想修改哪一处？请直接指出。', 34, MUTED, False),
        (558, '也欢迎挑出想保留的局部。', 34, MUTED, False),
        (748, '全部为外观候选，尚未定稿。', 31, MUTED, False),
        (810, '静态预览，暂不比较运行特效。', 31, MUTED, False),
    ]:
        text(draw, (x+55, y+dy), value, size, color, bold, w-110)
    footer = '各 AI 方案由 Codex 转译为方块预览；各方案完整取景，非同尺度对照。'
    text(draw, (84, 2241), footer, 31, MUTED, max_width=3672)

    phone = Image.new('RGB', (1600, 6280), BG)
    draw = ImageDraw.Draw(phone)
    text(draw, (64, 36), 'HK3GTL / W03 · 建筑外观征集', 39, ACCENT, True)
    text(draw, (64, 108), '空之律者 · 穹界·虚数锚定环', 53, bold=True, max_width=1472)
    text(draw, (67, 193), '五个 AI 最新方案｜选 A～E，再说喜欢与想改的地方', 33, MUTED, max_width=1470)
    for i, (entry, image) in enumerate(zip(ENTRIES, images)):
        card(phone, (64, 280+i*1138, 1472, 1106), entry, image, crop)
    draw = ImageDraw.Draw(phone)
    text(draw, (67, 6010), '全部为外观候选，尚未定稿；统一采用静态全景。', 32, MUTED, max_width=1470)
    text(draw, (67, 6078), '各 AI 方案由 Codex 转译为方块预览。', 32, MUTED, max_width=1470)
    text(draw, (67, 6146), '各方案完整取景，非同尺度对照。', 32, MUTED, max_width=1470)

    outputs = []
    for name, image in [('W03_五AI最新方案_横版', landscape), ('W03_五AI最新方案_手机长图', phone)]:
        jpg = OUT / (name+'.jpg')
        image.save(jpg, quality=95, subsampling=0, optimize=True)
        outputs.append(dict(file=jpg.name, pixels=list(image.size), bytes=jpg.stat().st_size, sha256=digest(jpg)))
        if image is landscape:
            png = OUT / (name+'.png')
            image.save(png, optimize=True)
            outputs.append(dict(file=png.name, pixels=list(image.size), bytes=png.stat().st_size, sha256=digest(png)))
    for record in records:
        assert digest(ROOT / record['source']) == record['sha256']
    receipt = dict(passed=True, date='2026-11-08', candidates=records, common_background_crop=list(crop),
                   all_visible_source_pixels_preserved=True, source_images_unchanged=True,
                   static_only=True, approved=False, outputs=outputs)
    (OUT/'manifest.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(output=str(OUT), outputs=outputs), ensure_ascii=False))


if __name__ == '__main__':
    main()
