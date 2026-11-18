"""重画四件神之键模板，仿制虚空万藏沿用原图。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from item_texture_64 import canvas64, refine64
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
OUT = ROOT / 'logs/item-texture-refresh-20261112'
INK, DARK, MID, STEEL, SILVER = '#151828', '#303347', '#62687c', '#a4b1bf', '#e5eded'
GOLD, BRASS, LIGHT_GOLD = '#bf883b', '#73502d', '#ffe19b'


def canvas():
    return canvas64()


def flame_core():
    im, d = canvas()
    d.polygon([(8, 0), (9, 4), (12, 2), (13, 7), (11, 12), (7, 15), (3, 12), (2, 8), (5, 3), (5, 7)], fill='#381e31')
    d.polygon([(8, 2), (8, 6), (11, 4), (12, 8), (9, 12), (7, 14), (4, 11), (4, 8), (6, 5), (6, 9)], fill='#c3453d')
    d.polygon([(7, 6), (7, 10), (9, 8), (9, 11), (7, 13), (5, 11)], fill='#ee9444')
    d.line([(6, 8), (5, 10), (6, 11)], fill='#ffe3a5')
    d.point((10, 5), fill='#f16e47')
    d.point((2, 3), fill='#ee9444')
    return im


def ice_core():
    im, d = canvas()
    d.polygon([(7, 0), (11, 4), (10, 10), (7, 15), (3, 10), (3, 5)], fill='#153449')
    d.polygon([(7, 2), (7, 12), (4, 9), (4, 5)], fill='#82d9ed')
    d.polygon([(8, 3), (10, 5), (9, 10), (8, 12)], fill='#3f9cc0')
    d.line([(7, 3), (5, 6), (5, 8)], fill='#e4fdff')
    d.line((8, 7, 9, 6), fill='#c5f4ff')
    d.polygon([(2, 2), (3, 5), (1, 4)], fill='#559dbd')
    d.polygon([(12, 9), (14, 11), (11, 13)], fill='#559dbd')
    d.point((12, 10), fill='#c5f4ff')
    return im


def reason_core():
    im, d = canvas()
    d.polygon([(4, 2), (9, 0), (13, 4), (12, 10), (7, 15), (2, 11), (2, 5)], fill='#142840')
    d.polygon([(4, 3), (8, 2), (11, 4), (7, 6), (3, 5)], fill='#81b9ee')
    d.polygon([(3, 6), (7, 7), (7, 13), (3, 10)], fill='#428dff')
    d.polygon([(8, 7), (12, 5), (11, 10), (8, 13)], fill='#285596')
    d.line([(4, 7), (5, 8), (5, 10), (6, 11)], fill='#b9e5ff')
    d.line([(9, 8), (10, 7), (10, 9)], fill='#5bbcff')
    d.line((5, 3, 7, 2), fill='#ecfbff')
    d.point((9, 11), fill='#97d9fa')
    return im


def void_core():
    im, d = canvas()
    d.polygon([(8, 0), (13, 6), (11, 10), (7, 15), (3, 10), (2, 7)], fill='#422e30')
    d.polygon([(8, 2), (7, 12), (4, 9), (3, 7)], fill='#e9b74d')
    d.polygon([(9, 3), (12, 6), (10, 10), (8, 12)], fill='#a96e32')
    d.polygon([(7, 4), (6, 8), (7, 10), (9, 7)], fill='#f9dd8d')
    d.line((7, 4, 5, 6), fill='#fff5cf')
    d.point((1, 3), fill='#c8914d')
    d.point((13, 12), fill='#e9b74d')
    return im


def corruption_core():
    im, d = canvas()
    d.polygon([(5, 1), (10, 2), (10, 4), (13, 5), (12, 9), (10, 9), (10, 12), (5, 14), (3, 11), (4, 8), (2, 7), (3, 4)], fill='#2c1e3d')
    d.polygon([(5, 2), (8, 3), (7, 6), (10, 5), (12, 6), (10, 8), (8, 8), (9, 11), (6, 13), (4, 10), (6, 7), (4, 6)], fill='#714aaa')
    d.line([(5, 3), (5, 5), (7, 4), (8, 4)], fill='#c398ef')
    d.line([(9, 6), (8, 7), (7, 9), (7, 11)], fill='#a576d1')
    d.point((4, 2), fill='#ead3fa')
    d.point((12, 1), fill='#a576d1')
    d.point((1, 11), fill='#714aaa')
    d.point((13, 12), fill='#c398ef')
    return im


def rock_core():
    im, d = canvas()
    d.polygon([(5, 1), (9, 2), (13, 6), (14, 11), (9, 15), (3, 12), (1, 7)], fill='#2c2427')
    d.polygon([(5, 2), (9, 3), (11, 6), (6, 8), (2, 7)], fill='#bc8f48')
    d.polygon([(3, 8), (6, 9), (9, 13), (4, 11)], fill='#775132')
    d.polygon([(7, 8), (12, 7), (13, 10), (10, 13)], fill='#4e3930')
    d.line([(4, 4), (6, 3), (8, 4)], fill='#efd49a')
    d.line([(7, 6), (8, 8), (10, 9), (10, 11)], fill='#cb9f52')
    d.point((12, 10), fill='#b17a32')
    return im


def binding_core():
    im, d = canvas()
    d.polygon([(7, 0), (10, 3), (9, 5), (13, 5), (15, 7), (12, 10), (10, 9), (10, 12), (7, 15), (4, 12), (5, 9), (2, 10), (0, 7), (3, 5), (5, 5), (4, 3)], fill='#4a3c33')
    d.polygon([(7, 2), (9, 4), (8, 7), (11, 6), (13, 7), (11, 9), (8, 8), (9, 11), (7, 13), (5, 11), (6, 8), (3, 9), (2, 7), (5, 6), (6, 7), (5, 4)], fill='#d8bc78')
    d.polygon([(7, 3), (7, 7), (5, 5), (6, 4)], fill='#fff4d2')
    d.line((3, 7, 6, 7), fill='#fff4d2')
    d.line((7, 8, 7, 11), fill='#f4e3b0')
    d.point((10, 7), fill='#fff4d2')
    return im


def thunder_core():
    im, d = canvas()
    d.polygon([(9, 0), (12, 3), (10, 6), (14, 5), (11, 10), (10, 10), (6, 15), (5, 10), (2, 11), (4, 5)], fill='#391e35')
    d.polygon([(9, 2), (10, 3), (7, 8), (12, 7), (9, 10), (7, 13), (7, 8), (4, 9), (5, 6)], fill='#c93f63')
    d.line([(8, 3), (7, 5), (6, 6), (6, 8)], fill='#f2a5bb')
    d.line((9, 8, 8, 10), fill='#f2a5bb')
    d.point((11, 1), fill='#e16b96')
    d.point((2, 4), fill='#c93f63')
    return im


def wind_core():
    im, d = canvas()
    d.polygon([(8, 1), (13, 3), (13, 7), (10, 8), (11, 12), (7, 15), (3, 12), (3, 9), (0, 7), (2, 3), (5, 3)], fill='#173b3c')
    d.polygon([(8, 2), (12, 4), (11, 6), (7, 6), (5, 4)], fill='#74d9b5')
    d.polygon([(10, 8), (10, 11), (7, 13), (5, 11), (6, 8)], fill='#3eac98')
    d.polygon([(3, 4), (5, 5), (4, 9), (2, 7)], fill='#83dfc1')
    d.line([(8, 3), (10, 4), (8, 4)], fill='#d4fff1')
    d.line([(4, 5), (3, 6)], fill='#d4fff1')
    d.line((7, 9, 7, 11), fill='#9cebd2')
    return im


def void_archives():
    im, d = canvas()
    d.polygon([(7, 0), (14, 4), (14, 11), (8, 15), (1, 11), (1, 4)], fill=INK)
    d.polygon([(7, 1), (12, 4), (8, 7), (3, 4)], fill=LIGHT_GOLD)
    d.polygon([(2, 5), (7, 8), (7, 13), (2, 10)], fill=GOLD)
    d.polygon([(8, 8), (13, 5), (13, 10), (8, 13)], fill=BRASS)
    d.polygon([(7, 2), (10, 4), (8, 5), (5, 4)], fill=GOLD)
    d.line([(3, 6), (5, 7), (5, 10), (3, 9)], fill=BRASS)
    d.polygon([(9, 9), (11, 7), (12, 8), (10, 10)], fill='#90cce0')
    d.line((9, 11, 11, 10), fill=GOLD)
    d.point((8, 3), fill='#fff8dd')
    d.line((3, 10, 6, 12), fill=LIGHT_GOLD)
    return im


def cosmic_juggernaut():
    im, d = canvas()
    d.polygon([(1, 6), (4, 3), (12, 3), (15, 7), (13, 12), (3, 13), (0, 10)], fill=INK)
    d.polygon([(4, 4), (12, 4), (13, 6), (6, 6), (3, 7)], fill=LIGHT_GOLD)
    d.polygon([(2, 7), (4, 5), (6, 7), (5, 11), (2, 10)], fill=SILVER)
    d.polygon([(6, 7), (13, 7), (12, 10), (6, 11)], fill=STEEL)
    d.line((7, 7, 12, 7), fill=BRASS)
    d.rectangle((7, 8, 8, 9), fill='#3d798d')
    d.rectangle((10, 8, 11, 9), fill='#3d798d')
    d.line((4, 6, 5, 7), fill='#507d8b')
    d.line((2, 8, 3, 9), fill='#6396a1')
    d.line((5, 11, 12, 11), fill=GOLD)
    d.line((1, 14, 12, 13), fill=MID)
    for p in [(3, 12), (7, 12), (11, 12)]:
        d.point(p, fill=INK)
    d.point((2, 10), fill=LIGHT_GOLD)
    return im


def star_of_eden():
    im, d = canvas()
    d.ellipse((1, 1, 14, 14), fill=INK)
    d.ellipse((2, 2, 13, 13), fill=BRASS)
    d.ellipse((3, 3, 12, 12), fill='#292c3a')
    d.arc((3, 3, 11, 10), 150, 300, fill=LIGHT_GOLD, width=2)
    d.arc((5, 2, 10, 13), 290, 100, fill=GOLD)
    d.arc((2, 5, 13, 10), 0, 175, fill=GOLD, width=2)
    d.ellipse((5, 5, 10, 10), fill=INK)
    d.ellipse((6, 6, 9, 9), fill='#9b4550')
    d.point((6, 6), fill='#ffcfb2')
    d.line((4, 3, 6, 2), fill=LIGHT_GOLD)
    d.point((11, 11), fill=GOLD)
    d.point((8, 12), fill=LIGHT_GOLD)
    return im


def oath_of_judah():
    im, d = canvas()
    d.polygon([(5, 0), (10, 0), (10, 4), (14, 4), (15, 7), (11, 9), (10, 8), (10, 13), (8, 15), (5, 13), (5, 8), (4, 9), (0, 7), (1, 4), (5, 4)], fill=INK)
    d.rectangle((6, 1, 9, 12), fill=GOLD)
    d.rectangle((2, 5, 13, 6), fill=GOLD)
    d.line((6, 1, 8, 1), fill=LIGHT_GOLD)
    d.line((2, 5, 13, 5), fill=LIGHT_GOLD)
    d.line((6, 7, 6, 12), fill=LIGHT_GOLD)
    d.line((9, 8, 9, 12), fill=BRASS)
    d.rectangle((6, 4, 9, 7), fill=BRASS)
    d.rectangle((7, 4, 8, 6), fill='#79af92')
    d.point((7, 4), fill='#dbefbc')
    d.line((7, 9, 7, 12), fill=BRASS)
    d.point((7, 13), fill=LIGHT_GOLD)
    d.point((3, 7), fill=BRASS)
    d.point((12, 7), fill=BRASS)
    return im


def key_housing():
    im, d = canvas()
    d.polygon([(5, 0), (10, 0), (15, 5), (15, 10), (10, 15), (5, 15), (0, 10), (0, 5)], fill=INK)
    d.polygon([(5, 1), (10, 1), (14, 5), (14, 10), (10, 14), (5, 14), (1, 10), (1, 5)], fill=MID)
    d.polygon([(5, 3), (10, 3), (12, 5), (12, 10), (10, 12), (5, 12), (3, 10), (3, 5)], fill=INK)
    d.polygon([(6, 4), (9, 4), (11, 6), (11, 9), (9, 11), (6, 11), (4, 9), (4, 6)], fill=(0, 0, 0, 0))
    d.line([(5, 2), (9, 2), (12, 5)], fill=SILVER)
    d.line([(13, 6), (13, 9), (10, 13), (6, 13)], fill=STEEL)
    for x, y in [(2, 5), (10, 2), (13, 10), (5, 13)]:
        d.rectangle((x - 1, y - 1, x, y), fill=GOLD)
        d.point((x - 1, y - 1), fill=LIGHT_GOLD)
    return im


DRAWINGS = {
    'imitation_void_archives': (void_archives, '黄金立方盒、三面分色、立体雕纹与侧面青色嵌片。'),
    'imitation_cosmic_juggernaut': (cosmic_juggernaut, '金属列车器型、斜向车头与分段车厢窗口，保留轮组和轨道。'),
    'imitation_star_of_eden': (star_of_eden, '暗色球体、交错金色引力弧带与中心红色引力核。'),
    'imitation_oath_of_judah': (oath_of_judah, '纵长金色十字、宽横臂、中央绿色嵌石与下端尖角。'),
    'divine_key_housing': (key_housing, '空心八角机械封装框、四角金色锁扣，中央保持透明未装核心。'),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = json.loads((ASSETS / 'lang/zh_cn.json').read_text(encoding='utf-8-sig'))
    records = []
    sheet = Image.new('RGB', (1200, 5 * 216), '#121b2a')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
    for index, (ident, (paint, design)) in enumerate(DRAWINGS.items()):
        if ident == 'imitation_void_archives':
            continue
        rel = Path('textures/item') / (ident + '.png')
        path = ASSETS / rel
        backup = OUT / 'before/assets/hk3gtl' / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        painted = refine64(paint())
        painted.save(path, optimize=True)
        x, y = index % 3 * 400, index // 3 * 216
        draw.text((x + 16, y + 12), names['item.hk3gtl.' + ident], fill='#e5edf6', font=font)
        for dx, source in [(20, Image.open(backup).convert('RGBA')), (220, painted)]:
            checker = Image.new('RGBA', (64, 64), '#202c3d')
            pattern = ImageDraw.Draw(checker)
            for py in range(0, 64, 16):
                for px in range(0, 64, 16):
                    if (px + py) % 32:
                        pattern.rectangle((px, py, px + 15, py + 15), fill='#2a394e')
            checker.alpha_composite(source.resize((64, 64), Image.Resampling.NEAREST))
            sheet.paste(checker.resize((128, 128), Image.Resampling.NEAREST).convert('RGB'), (x + dx, y + 47))
        draw.text((x + 67, y + 181), '原图', fill='#a8bbd2', font=small)
        draw.text((x + 267, y + 181), '重画', fill='#8edcdb', font=small)
        records.append({'id': ident, 'name': names['item.hk3gtl.' + ident], 'path': rel.as_posix(),
                        'before_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
                        'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'size': [64, 64], 'design': design})
    (OUT / 'key-manifest.json').write_text(json.dumps({'changed': records, 'preserved': []}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sheet.save(OUT / '四件神之键材质新旧对照.png')
    print('四件神之键：4张64格静态透明贴图，仿制虚空万藏沿用原图。')


if __name__ == '__main__':
    main()
