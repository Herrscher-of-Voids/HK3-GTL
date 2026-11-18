import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .common import BLACK, BLUE, COPPER, GOLD, STEEL, WHITE, Pixel


ROOT = Path(__file__).resolve().parents[2]
ITEMS = ROOT / 'src/main/resources/assets/hk3gtl/textures/item'
DELIVERY = ROOT / 'deliveries/0002贴图材质_工艺重构_R3_20261114'
COPIES = DELIVERY / 'textures/item'
IDS = ('imitation_cosmic_juggernaut', 'imitation_star_of_eden',
       'imitation_oath_of_judah', 'divine_key_housing')
NAMES = ('仿制的千界一乘', '仿制的伊甸之星', '仿制的犹大的誓约', '神之键封装框架')


def cosmic_juggernaut():
    q = Pixel()
    d = q.d
    d.polygon([(6, 35), (35, 17), (48, 16), (58, 24), (56, 38), (24, 56), (9, 49)], fill=BLACK[0])
    q.plate([(8, 31), (35, 14), (47, 14), (54, 20), (23, 39)], BLACK, 1, 3)
    q.plate([(23, 39), (55, 21), (55, 36), (24, 53), (9, 47), (9, 31)], BLACK, 2, 11)
    q.plate([(12, 30), (25, 22), (36, 22), (24, 30)], STEEL, 1, 17)
    q.plate([(26, 21), (39, 14), (47, 14), (54, 20), (39, 29)], BLACK, 2, 23)
    d.polygon([(40, 27), (50, 20), (56, 24), (55, 35), (43, 42), (38, 37)], fill=BLACK[1])
    d.polygon([(48, 19), (54, 21), (56, 26), (53, 30), (47, 27)], fill=STEEL[2])
    d.line([(49, 20), (54, 22), (55, 25)], fill=WHITE[3])
    d.polygon([(50, 22), (53, 23), (54, 25), (51, 26), (49, 25)], fill=BLUE[3])
    for x, y in ((13, 35), (17, 33), (29, 26), (33, 24)):
        d.polygon([(x, y), (x + 3, y - 2), (x + 6, y - 2), (x + 3, y)], fill=BLUE[2])
        d.line((x + 1, y, x + 4, y - 2), fill=BLUE[4])
    d.line([(11, 40), (23, 46), (43, 35), (52, 30)], fill=GOLD[2], width=2)
    d.line([(15, 43), (22, 47), (28, 44)], fill=GOLD[4])
    d.line([(31, 39), (37, 36), (37, 39)], fill=COPPER[3])
    d.line([(39, 35), (44, 33)], fill=WHITE[3])
    d.line([(10, 46), (22, 52), (28, 49)], fill=STEEL[3])
    for x, y in ((14, 48), (30, 43), (45, 34)):
        d.ellipse((x - 3, y - 2, x + 3, y + 4), fill=BLACK[0], outline=STEEL[2])
        d.rectangle((x - 2, y, x + 2, y + 2), fill=STEEL[1])
        d.point((x, y), fill=GOLD[3])
    d.rectangle((19, 20, 21, 21), fill=GOLD[3])
    d.rectangle((37, 16, 39, 17), fill=GOLD[3])
    d.line([(15, 29), (24, 34), (34, 28)], fill=BLACK[3])
    d.line([(24, 34), (24, 42)], fill=BLACK[0])
    d.line([(37, 27), (37, 34)], fill=BLACK[0])
    q.bolt(25, 41, STEEL)
    q.bolt(42, 32, STEEL)
    return q.im


def star_of_eden():
    q = Pixel()
    d = q.d
    d.ellipse((16, 12, 59, 58), fill=BLACK[0])
    d.ellipse((19, 14, 57, 56), fill=BLACK[1])
    d.polygon([(47, 17), (54, 23), (57, 33), (56, 43), (51, 51), (46, 53),
               (49, 45), (51, 36), (50, 27)], fill=BLACK[2])
    d.line([(54, 27), (55, 34), (54, 41)], fill=BLACK[3])
    d.polygon([(26, 48), (37, 49), (49, 44), (53, 43), (49, 52), (41, 56),
               (31, 56), (24, 52)], fill=STEEL[1])
    d.line([(34, 55), (42, 54), (48, 50)], fill=STEEL[2])
    d.polygon([(14, 20), (22, 11), (39, 9), (50, 17), (54, 31), (47, 45),
               (39, 51), (22, 48), (12, 39), (9, 29)], fill=BLACK[0])
    q.plate([(18, 18), (24, 12), (39, 11), (47, 17), (43, 22), (26, 24)], STEEL, 2, 4)
    q.plate([(13, 22), (20, 20), (25, 25), (24, 39), (17, 40), (11, 34)], BLACK, 2, 9)
    q.plate([(43, 21), (51, 20), (53, 31), (47, 41), (40, 39), (39, 29)], BLACK, 2, 15)
    q.plate([(20, 40), (27, 42), (40, 39), (47, 44), (39, 50), (22, 47), (15, 41)], STEEL, 1, 21)
    d.ellipse((19, 18, 45, 43), fill=BLACK[0], outline=GOLD[2], width=2)
    d.ellipse((22, 20, 43, 41), fill=COPPER[1], outline=STEEL[3], width=2)
    d.ellipse((25, 23, 40, 38), fill='#721f36', outline=COPPER[3])
    d.ellipse((28, 25, 37, 35), fill='#b44858')
    d.arc((28, 24, 38, 35), 190, 320, fill='#f0a28a', width=2)
    d.rectangle((31, 27, 34, 32), fill='#302834')
    d.point((32, 27), fill='#ffe2a2')
    for x, y in ((16, 25), (45, 25), (16, 34), (45, 34)):
        d.rectangle((x, y, x + 3, y + 5), fill=GOLD[1])
        d.rectangle((x + 1, y + 1, x + 2, y + 3), fill=GOLD[4])
        d.point((x + 1, y + 4), fill=BLACK[0])
    d.line([(18, 17), (25, 10), (38, 8), (46, 13)], fill=GOLD[3], width=2)
    d.line([(17, 43), (24, 49), (39, 52), (48, 46)], fill=STEEL[3], width=2)
    d.line([(23, 14), (22, 17)], fill=WHITE[4])
    d.line([(41, 44), (44, 41), (47, 40)], fill=STEEL[4])
    for x, y in ((14, 20), (47, 17), (12, 37), (45, 44), (25, 46), (39, 13)):
        q.bolt(x, y, GOLD)
    d.line([(12, 28), (8, 31), (11, 35)], fill=GOLD[3], width=2)
    d.line([(50, 25), (56, 29), (53, 33)], fill=GOLD[3], width=2)
    d.rectangle((8, 29, 10, 32), fill=STEEL[1])
    d.rectangle((54, 28, 56, 31), fill=STEEL[1])
    d.line([(50, 39), (53, 37), (55, 32)], fill=BLACK[3])
    d.line([(47, 45), (50, 47), (51, 49)], fill=GOLD[2], width=2)
    return q.im


def oath_of_judah():
    q = Pixel()
    d = q.d
    d.polygon([(22, 5), (39, 5), (42, 9), (42, 18), (56, 18), (59, 22), (58, 31),
               (54, 34), (42, 34), (42, 52), (38, 59), (23, 58), (20, 54),
               (20, 34), (7, 34), (4, 30), (5, 21), (9, 18), (20, 18), (20, 9)], fill=GOLD[0])
    q.plate([(23, 7), (38, 7), (39, 10), (39, 20), (55, 20), (56, 23), (55, 30),
             (39, 31), (39, 53), (36, 56), (25, 56), (23, 52), (23, 31),
             (8, 30), (7, 24), (9, 21), (23, 21)], GOLD, 2, 5)
    q.plate([(26, 10), (35, 10), (35, 19), (26, 19)], WHITE, 2, 12)
    q.plate([(10, 23), (20, 23), (20, 28), (10, 28)], GOLD, 3, 18)
    q.plate([(42, 23), (53, 23), (53, 28), (42, 28)], GOLD, 3, 24)
    q.plate([(27, 34), (36, 34), (36, 51), (27, 51)], STEEL, 1, 30)
    d.rectangle((28, 35, 35, 49), fill=BLACK[0], outline=GOLD[4])
    d.rectangle((30, 37, 33, 47), fill='#276955')
    d.rectangle((31, 38, 32, 45), fill='#7fc9a3')
    d.line([(30, 40), (32, 38), (33, 40)], fill='#d2eac0')
    d.rectangle((29, 43, 34, 44), fill=GOLD[2])
    d.line([(25, 8), (25, 17)], fill=WHITE[4], width=2)
    d.line([(11, 22), (18, 22)], fill=WHITE[4])
    d.line([(43, 22), (51, 22)], fill=WHITE[4])
    d.line([(25, 32), (25, 50)], fill=GOLD[4])
    d.line([(38, 35), (38, 50)], fill=GOLD[1])
    for x, y in ((21, 10), (38, 11), (8, 25), (54, 25), (21, 29), (39, 29), (24, 50), (37, 51)):
        q.bolt(x, y, GOLD)
    d.rectangle((6, 18, 15, 20), fill=STEEL[1])
    d.rectangle((49, 18, 57, 20), fill=STEEL[1])
    d.rectangle((6, 31, 16, 33), fill=STEEL[1])
    d.rectangle((47, 31, 57, 33), fill=STEEL[1])
    d.line([(15, 19), (18, 21), (15, 23)], fill=COPPER[4])
    d.line([(49, 19), (46, 21), (49, 23)], fill=COPPER[4])
    d.line([(12, 34), (12, 42), (18, 47), (20, 47)], fill=BLACK[0], width=3)
    d.line([(13, 35), (13, 41), (18, 45), (20, 45)], fill=COPPER[2])
    d.line([(50, 34), (50, 42), (45, 46), (42, 46)], fill=BLACK[0], width=3)
    d.line([(49, 35), (49, 41), (45, 44), (42, 44)], fill=COPPER[2])
    for x in (12, 49):
        for y in (35, 38, 41):
            d.line((x, y, x + 1, y), fill=GOLD[4])
    for y in (12, 15, 45, 48):
        d.rectangle((21, y, 23, y + 1), fill=COPPER[2])
        d.rectangle((39, y, 41, y + 1), fill=COPPER[2])
    return q.im


def key_housing():
    q = Pixel()
    d = q.d
    d.polygon([(9, 21), (30, 8), (54, 20), (55, 43), (33, 57), (9, 45)], fill=BLACK[0])
    q.plate([(9, 20), (30, 7), (54, 19), (47, 24), (29, 15), (16, 24)], STEEL, 2, 2)
    q.plate([(9, 20), (16, 24), (16, 42), (10, 45)], BLACK, 2, 8)
    q.plate([(16, 42), (29, 35), (47, 43), (33, 52)], STEEL, 1, 14)
    q.plate([(47, 24), (54, 20), (55, 43), (47, 48)], BLACK, 2, 20)
    d.polygon([(18, 23), (29, 17), (46, 25), (46, 39), (32, 47), (18, 39)], fill=BLACK[0])
    d.polygon([(22, 24), (29, 20), (42, 26), (42, 37), (32, 43), (22, 37)], fill=BLUE[0])
    d.line([(22, 25), (29, 21), (40, 26)], fill=BLUE[2])
    d.line([(22, 29), (39, 37), (39, 39)], fill=BLUE[1])
    d.polygon([(24, 28), (30, 25), (40, 30), (40, 35), (32, 40), (24, 36)], fill=BLACK[1])
    for n in range(4):
        d.line([(24, 29 + n * 2), (31, 33 + n * 2), (39, 29 + n * 2)], fill=STEEL[2 if n % 2 else 3])
    for x in (27, 30, 33, 36):
        d.line((x, 24 + (x - 27) // 2, x, 26 + (x - 27) // 2), fill=GOLD[3])
    d.polygon([(13, 18), (29, 9), (35, 12), (19, 22)], fill=GOLD[1])
    d.line([(14, 18), (29, 10), (33, 12)], fill=GOLD[4], width=2)
    d.line([(18, 40), (18, 25)], fill=GOLD[2], width=2)
    d.line([(45, 26), (45, 39)], fill=GOLD[3], width=2)
    d.rectangle((19, 24, 22, 27), fill=GOLD[2])
    d.rectangle((42, 25, 46, 29), fill=GOLD[1])
    d.rectangle((42, 35, 46, 39), fill=GOLD[1])
    d.rectangle((19, 37, 23, 41), fill=GOLD[1])
    d.line([(22, 43), (30, 48), (33, 49), (42, 44)], fill=GOLD[3], width=2)
    for x in (24, 28, 32, 36, 40):
        d.rectangle((x, 44 + (x in (24, 40)), x + 1, 47 + (x in (24, 40))), fill=STEEL[0])
        d.point((x, 45 + (x in (24, 40))), fill=GOLD[4])
    for x, y in ((12, 22), (15, 42), (30, 12), (49, 22), (51, 40), (32, 52)):
        q.bolt(x, y, STEEL)
    d.rectangle((25, 5, 33, 8), fill=COPPER[1])
    d.rectangle((26, 4, 32, 6), fill=COPPER[3])
    d.rectangle((27, 5, 31, 5), fill=WHITE[4])
    return q.im


DRAWERS = dict(zip(IDS, (cosmic_juggernaut, star_of_eden, oath_of_judah, key_housing)))


def draw(ident):
    return DRAWERS[ident]()


def render():
    DELIVERY.mkdir(parents=True, exist_ok=True)
    COPIES.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (4 * 224, 232), '#3c454b')
    sd = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15)
    for n, (ident, name) in enumerate(zip(IDS, NAMES)):
        im = draw(ident)
        im.save(ITEMS / f'{ident}.png')
        shutil.copyfile(ITEMS / f'{ident}.png', COPIES / f'{ident}.png')
        x = n * 224
        for cy in range(8):
            for cx in range(8):
                c = '#505a61' if (cx + cy) % 2 else '#465159'
                sd.rectangle((x + 16 + cx * 24, 8 + cy * 24, x + 39 + cx * 24, 31 + cy * 24), fill=c)
        tile = im.resize((192, 192), Image.Resampling.NEAREST)
        sheet.paste(tile, (x + 16, 8), tile)
        sd.text((x + 16, 207), name, font=font, fill='#e8eadf')
    sheet.save(DELIVERY / 'keys-r3.png')


if __name__ == '__main__':
    render()
