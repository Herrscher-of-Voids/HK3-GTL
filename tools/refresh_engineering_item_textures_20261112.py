"""重画探测器、工业模块、电路工艺件与舰体组件的旧通用像素图。"""
from pathlib import Path
from PIL import Image, ImageDraw
from item_texture_64 import canvas64, refine64
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
LOG = ROOT / 'logs/item-texture-refresh-20261112'
INK, DARK, STEEL, LIGHT = '#141c2b', '#29384d', '#657e98', '#cbdce7'
CYAN, WHITE, BLUE = '#52d9e4', '#e8feff', '#428dff'
GOLD, BRASS, PURPLE, RED = '#efc976', '#977045', '#ae7bd5', '#c93f63'


def detector(n):
    im, d = canvas64()
    d.rounded_rectangle((3, 5, 12, 14), 2, fill=INK)
    d.rectangle((4, 6, 11, 12), fill=STEEL)
    d.rectangle((5, 7, 10, 10), fill=DARK)
    d.line((5, 9, 6, 8, 7, 9, 9, 7), fill=CYAN)
    d.point((5, 12), fill=GOLD)
    d.line((8, 12, 10, 12), fill=LIGHT)
    if n == 0:
        d.line((4, 6, 1, 6, 1, 2, 4, 2), fill=BRASS)
        d.line((4, 0, 4, 3), fill=LIGHT)
        d.rectangle((7, 2, 10, 4), fill=DARK)
        d.point((8, 2), fill=GOLD)
    elif n == 1:
        d.line((8, 5, 8, 1, 12, 1), fill=LIGHT, width=2)
        d.polygon([(13, 1), (11, 4), (12, 6), (14, 6), (15, 4)], fill=CYAN)
        d.point((12, 4), fill=WHITE)
    elif n == 2:
        d.polygon([(3, 5), (6, 1), (10, 1), (13, 5)], fill=INK)
        d.line((3, 4, 6, 0, 10, 0, 13, 4), fill=LIGHT)
        d.polygon([(8, 1), (10, 3), (8, 5), (6, 3)], fill=PURPLE)
        d.point((8, 2), fill=WHITE)
    elif n == 3:
        d.ellipse((4, 0, 11, 6), fill=INK, outline=LIGHT)
        for x in (6, 8, 10):
            d.line((x, 1, x, 5), fill=CYAN)
        d.line((5, 3, 11, 3), fill=STEEL)
    else:
        d.line((3, 6, 1, 3, 2, 0), fill=GOLD, width=2)
        d.line((12, 6, 14, 3, 13, 0), fill=GOLD, width=2)
        d.ellipse((5, 0, 10, 5), outline=PURPLE)
        d.polygon([(8, 0), (6, 3), (9, 2), (7, 5)], fill=WHITE)
        d.line((4, 14, 11, 14), fill=PURPLE)
    return im


def component(ident):
    im, d = canvas64()
    if ident == 'soulium_anchor_component':
        d.polygon([(7, 1), (10, 2), (10, 7), (14, 10), (13, 14), (9, 12), (7, 15), (4, 12), (1, 13), (2, 9), (6, 7)], fill=INK)
        d.line((7, 2, 7, 10, 3, 12), fill=LIGHT, width=2)
        d.line((8, 10, 12, 12), fill=STEEL, width=2)
        d.rectangle((6, 5, 9, 7), fill=PURPLE)
        d.point((6, 5), fill=WHITE)
    elif ident == 'spatial_calibration_module':
        d.ellipse((1, 4, 14, 11), outline=INK, width=3)
        d.ellipse((2, 5, 13, 10), outline=GOLD)
        d.ellipse((5, 1, 10, 14), outline=STEEL, width=2)
        d.rectangle((6, 6, 9, 9), fill=BLUE)
        d.point((6, 6), fill=WHITE)
        for p in ((1, 7), (7, 1), (14, 7), (7, 14)):
            d.point(p, fill=CYAN)
    elif ident == 'world_maintenance_specimen':
        d.ellipse((4, 3, 11, 10), fill=INK, outline=CYAN)
        d.polygon([(7, 4), (10, 6), (8, 9), (5, 8)], fill=BLUE)
        d.line((2, 3, 2, 12, 12, 12, 12, 3), fill=STEEL, width=2)
        d.line((4, 14, 11, 14), fill=LIGHT)
        d.line((2, 5, 5, 6), fill=GOLD)
        d.line((10, 6, 13, 5), fill=GOLD)
    elif ident == 'confining_composite':
        d.polygon([(2, 3), (6, 1), (12, 3), (14, 7), (12, 13), (8, 15), (2, 12)], fill=INK)
        d.polygon([(3, 4), (6, 2), (11, 4), (12, 7), (10, 12), (7, 13), (3, 11)], fill=STEEL)
        d.polygon([(6, 5), (9, 5), (10, 8), (8, 11), (5, 9)], fill=DARK)
        d.line((4, 4, 4, 10, 7, 12), fill=GOLD)
        d.line((10, 5, 11, 8, 9, 11), fill=PURPLE)
    elif ident == 'composite_offcut':
        for poly in ([(1, 8), (5, 4), (7, 7), (4, 11)], [(8, 2), (12, 3), (11, 8), (8, 6)], [(8, 10), (13, 8), (14, 12), (11, 14)]):
            d.polygon(poly, fill=INK, outline=STEEL)
        d.line((2, 8, 5, 5), fill=LIGHT)
        d.line((9, 3, 11, 4), fill=PURPLE)
        d.line((9, 11, 12, 10), fill=GOLD)
    elif ident == 'polarized_electromagnetic_material':
        d.ellipse((2, 2, 13, 13), fill=INK, outline=STEEL)
        d.ellipse((5, 5, 10, 10), fill=(0, 0, 0, 0))
        for line in ((3, 4, 6, 3), (2, 7, 5, 6), (3, 10, 5, 9), (7, 12, 8, 10), (11, 11, 10, 9), (12, 7, 10, 6)):
            d.line(line, fill=GOLD, width=2)
        d.rectangle((2, 0, 5, 2), fill=RED)
        d.rectangle((10, 0, 13, 2), fill=BLUE)
    elif ident == 'cryogenic_condensed_material':
        d.polygon([(7, 1), (13, 5), (12, 12), (6, 15), (2, 10), (2, 4)], fill=INK)
        d.polygon([(7, 2), (12, 5), (7, 8), (3, 5)], fill=WHITE)
        d.polygon([(3, 6), (6, 8), (6, 13), (3, 10)], fill=CYAN)
        d.polygon([(7, 9), (12, 6), (11, 11), (7, 13)], fill=BLUE)
        d.line((4, 5, 7, 5, 9, 3), fill=STEEL)
        d.line((8, 9, 10, 10, 9, 12), fill=WHITE)
    elif ident == 'extreme_casting_material':
        d.polygon([(1, 8), (7, 3), (14, 5), (14, 10), (8, 14), (1, 12)], fill=INK)
        d.polygon([(2, 8), (7, 4), (13, 6), (8, 10)], fill=LIGHT)
        d.polygon([(2, 9), (7, 11), (7, 13), (2, 11)], fill=STEEL)
        d.polygon([(8, 11), (13, 7), (13, 10), (8, 13)], fill=DARK)
        d.line((5, 7, 7, 8, 10, 6), fill='#ffac54', width=2)
        d.point((7, 7), fill=WHITE)
    else:
        d.ellipse((1, 3, 14, 12), outline=GOLD)
        d.ellipse((4, 0, 11, 15), outline=PURPLE)
        d.ellipse((4, 4, 11, 11), fill=INK, outline=CYAN)
        d.polygon([(7, 4), (9, 7), (11, 8), (8, 9), (7, 12), (6, 9), (3, 8), (6, 7)], fill=WHITE)
        d.point((7, 8), fill=BLUE)
    return im


def circuit(ident):
    im, d = canvas64()
    bad = ident.startswith(('defective', 'failed', 'rejected', 'depleted'))
    if ident in ('process_gas_filter', 'depleted_gas_filter'):
        d.ellipse((3, 1, 12, 5), fill=LIGHT, outline=INK)
        d.rectangle((3, 3, 12, 12), fill=STEEL, outline=INK)
        for x in (4, 6, 8, 10):
            d.line((x, 4, x, 11), fill=BRASS if bad else DARK)
        d.ellipse((3, 10, 12, 14), fill=DARK, outline=STEEL)
        d.line((5, 2, 10, 2), fill=GOLD if bad else CYAN)
        if bad:
            d.line((5, 6, 10, 10), fill=RED, width=2)
    elif ident == 'process_gas_impurity':
        for x, y, color in ((2, 9, BRASS), (6, 4, STEEL), (10, 8, DARK), (7, 11, PURPLE)):
            d.polygon([(x, y), (x + 2, y - 2), (x + 4, y + 1), (x + 1, y + 3)], fill=color, outline=INK)
        for point in ((2, 3), (12, 2), (6, 1), (14, 12)):
            d.point(point, fill=LIGHT)
    elif ident in ('circuit_encapsulation_part', 'rejected_circuit_package'):
        d.rectangle((3, 3, 12, 12), fill=INK)
        d.rectangle((4, 4, 11, 11), fill=STEEL)
        d.rectangle((6, 6, 9, 9), fill=DARK)
        d.line((4, 4, 10, 4), fill=LIGHT)
        for p in (4, 7, 10):
            d.line((p, 1, p, 3), fill=GOLD)
            d.line((p, 12, p, 14), fill=GOLD)
            d.line((1, p, 3, p), fill=GOLD)
            d.line((12, p, 14, p), fill=GOLD)
        if bad:
            d.polygon([(9, 3), (12, 3), (12, 7)], fill=(0, 0, 0, 0))
            d.line((6, 6, 9, 9), fill=RED)
    else:
        mask = ident == 'circuit_lithography_mask'
        etched = 'layer' in ident
        fill = '#292839' if mask else '#324c65' if etched else '#214b43'
        d.polygon([(2, 3), (10, 1), (14, 4), (13, 12), (5, 15), (1, 11)], fill=INK)
        d.polygon([(3, 4), (10, 2), (13, 5), (12, 11), (5, 13), (2, 10)], fill=fill)
        d.line((3, 4, 10, 2, 13, 5), fill=LIGHT)
        color = CYAN if mask else PURPLE if etched else GOLD
        d.line((4, 5, 6, 5, 6, 8, 10, 8, 10, 5, 12, 5), fill=color)
        d.line((4, 10, 8, 10, 8, 12), fill=color)
        d.rectangle((7, 5, 8, 6), fill=(0, 0, 0, 0) if mask else WHITE)
        if bad:
            d.line((8, 2, 7, 6, 9, 8, 6, 12), fill=INK)
            d.point((9, 7), fill=RED)
    return im


def ship(ident):
    im, d = canvas64()
    if ident == 'imitation_hyperion_blueprint':
        d.rectangle((2, 1, 13, 14), fill=INK)
        d.rectangle((3, 2, 12, 13), fill='#244875')
        d.line((3, 2, 12, 2), fill=LIGHT)
        d.polygon([(4, 8), (10, 4), (11, 6), (9, 9), (5, 11)], outline=CYAN)
        d.line((4, 12, 9, 12), fill=LIGHT)
        d.rectangle((1, 1, 2, 13), fill=STEEL)
    elif ident == 'hyperion_keel_segment':
        d.polygon([(1, 10), (11, 1), (15, 4), (5, 14), (1, 13)], fill=INK)
        d.line((2, 10, 12, 2), fill=LIGHT, width=2)
        d.line((4, 13, 14, 4), fill=STEEL, width=2)
        for x, y in ((4, 9), (7, 6), (10, 3)):
            d.line((x, y, x + 2, y + 2), fill=GOLD, width=2)
    elif ident == 'hyperion_navigation_module':
        d.polygon([(1, 11), (8, 8), (14, 11), (14, 14), (4, 15), (1, 13)], fill=INK)
        d.line((3, 12, 10, 11, 12, 12), fill=STEEL)
        d.ellipse((3, 0, 12, 10), fill=DARK, outline=LIGHT)
        d.ellipse((5, 2, 10, 8), outline=CYAN)
        d.line((8, 2, 8, 5, 11, 5), fill=GOLD)
        d.point((6, 6), fill=WHITE)
    else:
        d.polygon([(1, 8), (5, 4), (11, 4), (14, 8), (13, 13), (4, 14), (1, 11)], fill=INK)
        d.polygon([(2, 8), (5, 5), (10, 5), (12, 7), (7, 10)], fill=LIGHT)
        d.polygon([(3, 9), (7, 11), (12, 8), (12, 11), (7, 13), (3, 11)], fill=STEEL)
        d.line((5, 7, 10, 6), fill=CYAN, width=2)
        d.line((8, 4, 8, 1, 12, 1), fill=STEEL)
        d.point((12, 0), fill=RED)
    return im


def main():
    scope = json.loads((LOG / 'scope-review.json').read_text(encoding='utf-8'))
    rows = [r for r in scope['generic_items'] if r['family'] in ('detector', 'component', 'circuit', 'ship')]
    drawings = {'component': component, 'circuit': circuit, 'ship': ship}
    detector_ids = [r['id'] for r in rows if r['family'] == 'detector']
    records = []
    for row in rows:
        path = ROOT / row['texture']
        rel = path.relative_to(ASSETS)
        backup = LOG / 'before/assets/hk3gtl' / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists(): backup.write_bytes(path.read_bytes())
        image = detector(detector_ids.index(row['id'])) if row['family'] == 'detector' else drawings[row['family']](row['id'])
        refine64(image).save(path, optimize=True)
        records.append({'id': row['id'], 'name': row['name'], 'family': row['family'], 'path': rel.as_posix(),
                        'before_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
                        'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size': [64, 64],
                        'design': '按真实工艺区分器型、结构状态及语义配色，使用64格透明像素。'})
    (LOG / 'engineering-manifest.json').write_text(json.dumps({'changed': records, 'preserved': []}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('工业模块与舰体组件：' + str(len(records)))


if __name__ == '__main__':
    main()
