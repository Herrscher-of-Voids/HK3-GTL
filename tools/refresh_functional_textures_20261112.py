"""重绘七件仍使用纯色占位的功能物品；保留既有模型与16格像素规格。"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
OUT = ROOT / 'logs/texture-refresh-20261112'
INK, DARK, STEEL, LIGHT = '#151e2d', '#29384b', '#596d86', '#bdcddd'
GOLD, GOLD_LIGHT, GOLD_DARK = '#bb8339', '#f4d27e', '#705132'
BLUE, CYAN, WHITE = '#428dff', '#57cddd', '#dcfcff'
PURPLE, LILAC = '#7957a9', '#b99ee1'


def canvas():
    image = Image.new('RGBA', (16, 16))
    return image, ImageDraw.Draw(image)


def modulator():
    im, d = canvas()
    d.polygon([(3, 2), (12, 2), (14, 4), (14, 12), (12, 14), (3, 14), (1, 12), (1, 4)], fill=INK)
    d.rectangle((3, 3, 12, 12), fill=DARK)
    d.line([(3, 11), (3, 3), (11, 3)], fill=STEEL)
    d.rectangle((5, 4, 10, 11), fill=GOLD_DARK)
    for y in (4, 6, 8, 10):
        d.line((4, y, 11, y), fill=GOLD)
        d.line((5, y, 10, y), fill=GOLD_LIGHT)
    d.rectangle((7, 4, 8, 11), fill=PURPLE)
    d.line((7, 5, 7, 10), fill=LILAC)
    for x in (3, 6, 9, 12):
        d.point((x, 1), fill=GOLD_LIGHT)
        d.point((x, 14), fill=GOLD)
    d.point((12, 12), fill=CYAN)
    return im


def data_core():
    im, d = canvas()
    d.polygon([(7, 1), (13, 4), (13, 11), (7, 15), (2, 12), (2, 4)], fill=INK)
    d.polygon([(7, 2), (12, 4), (7, 7), (3, 4)], fill=CYAN)
    d.polygon([(3, 5), (7, 8), (7, 13), (3, 11)], fill='#278b9d')
    d.polygon([(8, 8), (12, 5), (12, 10), (8, 13)], fill='#1f596e')
    d.line([(3, 4), (7, 2), (12, 4)], fill=WHITE)
    d.line((7, 8, 7, 13), fill=LIGHT)
    d.rectangle((5, 6, 9, 10), fill=DARK)
    d.rectangle((6, 6, 8, 9), fill=BLUE)
    d.line((6, 7, 6, 8), fill=WHITE)
    d.line((3, 9, 5, 10), fill=CYAN)
    d.line((10, 8, 12, 7), fill=CYAN)
    return im


def frame():
    im, d = canvas()
    d.polygon([(5, 1), (11, 1), (15, 5), (15, 10), (10, 15), (5, 15), (1, 11), (1, 5)], fill=INK)
    d.line([(5, 2), (10, 2), (13, 5), (13, 10), (9, 13), (5, 13), (2, 10), (2, 5), (5, 2)], fill=STEEL, width=2)
    d.polygon([(6, 4), (9, 4), (11, 6), (11, 9), (9, 11), (6, 11), (4, 9), (4, 6)], fill=(0, 0, 0, 0))
    for a, b in [((3, 4), (5, 6)), ((10, 4), (12, 6)), ((3, 10), (5, 12)), ((10, 12), (12, 10))]:
        d.line([a, b], fill=PURPLE, width=2)
    d.line((5, 2, 10, 2), fill=LIGHT)
    for p in [(5, 3), (12, 7), (7, 12), (3, 7)]:
        d.point(p, fill=LILAC)
    return im


def measurement():
    im, d = canvas()
    d.polygon([(2, 10), (10, 8), (14, 11), (6, 15), (1, 12)], fill=INK)
    d.polygon([(2, 10), (9, 9), (12, 11), (6, 13)], fill=STEEL)
    d.line((4, 12, 10, 10), fill=CYAN)
    d.rectangle((6, 5, 8, 10), fill=DARK)
    d.line((6, 5, 6, 9), fill=LIGHT)
    for x, y in [(1, 4), (6, 1), (10, 5)]:
        d.polygon([(x, y + 1), (x + 2, y), (x + 4, y + 2), (x + 4, y + 4), (x + 1, y + 4)], fill=INK)
        d.rectangle((x + 1, y + 1, x + 3, y + 3), fill='#297e79')
        d.line((x + 1, y + 1, x + 3, y + 1), fill='#85e4b0')
        d.point((x + 1, y + 2), fill=WHITE)
    return im


def stabilizer():
    im, d = canvas()
    d.ellipse((2, 2, 13, 13), fill=INK)
    d.ellipse((3, 3, 12, 12), fill=STEEL)
    d.ellipse((5, 5, 10, 10), fill=INK)
    for box in [(6, 0, 9, 4), (11, 6, 15, 9), (6, 11, 9, 15), (0, 6, 4, 9)]:
        d.rectangle(box, fill=DARK, outline=INK)
    for line in [(6, 1, 9, 1), (13, 6, 13, 9), (6, 13, 9, 13), (1, 6, 1, 9)]:
        d.line(line, fill=LIGHT)
    d.polygon([(7, 5), (10, 7), (8, 11), (5, 8)], fill=PURPLE)
    d.line([(7, 6), (8, 7), (7, 9)], fill=LILAC)
    d.point((8, 6), fill=WHITE)
    return im


def fragment():
    im, d = canvas()
    d.polygon([(3, 1), (12, 2), (14, 5), (12, 7), (13, 10), (10, 14), (5, 13), (3, 15), (1, 11), (2, 7), (1, 4)], fill=INK)
    d.polygon([(3, 2), (11, 3), (12, 5), (10, 7), (11, 10), (8, 12), (4, 11), (3, 8)], fill='#2d5074')
    d.line([(3, 3), (8, 4), (8, 6), (5, 6), (5, 9), (8, 10)], fill=GOLD)
    d.line([(10, 4), (9, 7), (11, 8)], fill=BLUE)
    d.rectangle((6, 7, 8, 9), fill=DARK)
    d.point((6, 7), fill=CYAN)
    d.line([(5, 12), (7, 11), (9, 13)], fill=STEEL)
    d.point((4, 3), fill=GOLD_LIGHT)
    return im


def bubble():
    im, d = canvas()
    d.ellipse((2, 1, 13, 12), fill=INK)
    d.ellipse((3, 2, 12, 11), fill='#244b7b')
    d.polygon([(4, 4), (7, 2), (10, 3), (7, 4), (5, 7), (3, 7)], fill=CYAN)
    d.polygon([(5, 8), (7, 6), (9, 7), (10, 10), (7, 11), (4, 9)], fill=PURPLE)
    d.line([(5, 8), (7, 7), (8, 8)], fill=LILAC)
    d.line([(5, 3), (4, 4), (4, 5)], fill=WHITE)
    d.point((10, 5), fill=CYAN)
    d.polygon([(1, 8), (3, 8), (5, 12), (10, 12), (12, 8), (14, 8), (12, 13), (10, 14), (5, 14), (3, 13)], fill=DARK, outline=INK)
    d.line([(2, 9), (4, 12), (6, 13)], fill=STEEL)
    d.line((6, 14, 9, 14), fill=CYAN)
    return im


DRAWINGS = {
    'abyss/abyss_energy_modulator': modulator,
    'abyss/abyss_data_core': data_core,
    'abyss/abyss_stable_frame': frame,
    'abyss/abyss_measurement_array': measurement,
    'abyss/reactor_stabilizer': stabilizer,
    'abyss/data_precivilization_fragment': fragment,
    'honkai/world_bubble_sample': bubble,
}


def main():
    records = []
    for name, draw in DRAWINGS.items():
        rel = Path('textures/item') / (name + '.png')
        path = ASSETS / rel
        backup = OUT / 'before/assets/hk3gtl' / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        draw().save(path, optimize=True)
        records.append({'path': rel.as_posix(), 'before_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
                        'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size': [16, 16]})
    (OUT / 'functional-manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print('功能物品纹理：7张，16×16，透明背景。')


if __name__ == '__main__':
    main()
