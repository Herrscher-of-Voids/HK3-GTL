from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
from .common import Pixel, STEEL, WHITE, GOLD, VIOLET, BLUE, BLACK

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl/textures/item'
OUT = ROOT / 'logs/textures-redraw-0002-r3-20261114/process'
PBI = ['#322825', '#675037', '#957442', '#c2a369', '#e7cf90']
ASH = ['#24252b', '#45444b', '#6e6a70', '#989092', '#bcb4ac']
CAKE = ['#37352e', '#625c4e', '#8d8371', '#b6ad94', '#d5cdb0']
RECIPE = 'src/main/resources/data/hk3gtl/research/industrial_processes.json'
LIQUID = 'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/Hk3LiquidLineRecipes.java'
MAT = 'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/HonkaiMaterialRecipes.java'
BOOT = 'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/Hk3FuelRodBootstrapRecipes.java'
SPECTRUM = 'src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3SpectrumBootstrapRecipes.java'


def grain(p, points, pal, shade=2, offset=0):
    p.plate(points, pal, shade, offset)
    mask = Image.new('1', (64, 64))
    ImageDraw.Draw(mask).polygon(points, fill=1)
    for y in range(5, 60):
        for x in range(5, 60):
            cluster = (x // 2 * 13 + y // 2 * 29 + offset) % 31
            if mask.getpixel((x, y)) and cluster < 4:
                p.d.point((x, y), fill=pal[max(1, min(4, shade + (1 if cluster < 2 else -1)))])


def prism(p, points, center, pal=VIOLET):
    a, b, c, d, e, f = points
    p.d.polygon(points, fill=pal[0])
    p.d.polygon([a, b, center, f], fill=pal[3])
    p.d.polygon([b, c, d, center], fill=pal[2])
    p.d.polygon([d, e, f, center], fill=pal[1])
    p.d.line([f, a, b], fill=pal[4])
    p.d.line([a, center, d], fill=pal[2])
    p.d.line((center[0] + 1, center[1] + 2, center[0] + 2, center[1] + 5), fill=pal[3])


def analyzed():
    p = Pixel();d = p.d
    p.plate([(23, 9), (36, 9), (36, 20), (45, 30), (47, 46), (42, 53), (18, 53), (13, 46), (15, 31), (23, 21)], BLUE, 1)
    d.polygon([(18, 34), (28, 32), (34, 34), (43, 32), (45, 44), (40, 50), (20, 50), (16, 44)], fill=VIOLET[2])
    d.polygon([(18, 34), (28, 32), (34, 34), (43, 32), (42, 36), (32, 38), (23, 36)], fill=VIOLET[3])
    d.line([(18, 30), (18, 43), (21, 46)], fill=BLUE[3], width=2)
    d.line([(20, 28), (26, 22), (26, 15)], fill=BLUE[4])
    d.line((41, 28, 44, 42), fill=BLUE[2])
    p.box((21, 8, 38, 15), STEEL, 2)
    for x in (24, 29, 34):d.line((x, 10, x, 13), fill=STEEL[1])
    d.line((30, 17, 30, 26), fill=CAKE[1])
    p.plate([(29, 25), (47, 22), (54, 29), (49, 44), (31, 45)], CAKE, 3)
    d.line((34, 30, 46, 28), fill=CAKE[1]);d.line((34, 33, 42, 32), fill=CAKE[1])
    d.line([(34, 39), (37, 39), (39, 35), (41, 40), (44, 36), (48, 36)], fill=VIOLET[1])
    d.rectangle((33, 26, 35, 28), fill=STEEL[2])
    return p.im


def reference():
    p = Pixel();d = p.d
    p.plate([(9, 27), (17, 20), (47, 20), (55, 27), (55, 38), (47, 45), (17, 45), (9, 38)], BLUE, 1)
    d.polygon([(17, 23), (47, 23), (51, 28), (51, 37), (46, 42), (17, 42), (13, 37), (13, 28)], fill='#7394a0')
    d.polygon([(18, 31), (24, 26), (36, 25), (44, 31), (43, 37), (34, 40), (24, 39), (18, 36)], fill=VIOLET[0])
    prism(p, [(22, 27), (33, 24), (43, 29), (42, 37), (33, 41), (22, 36)], (32, 31))
    d.polygon([(24, 28), (30, 26), (32, 29), (29, 32), (25, 31)], fill=VIOLET[4])
    d.polygon([(33, 32), (37, 30), (40, 32), (38, 36), (34, 37)], fill=VIOLET[3])
    d.line([(25, 33), (29, 34), (31, 38)], fill=VIOLET[1])
    d.rectangle((35, 27, 36, 28), fill=WHITE[3]);d.rectangle((26, 35, 27, 36), fill=VIOLET[3])
    d.line([(18, 24), (24, 23), (44, 23)], fill=BLUE[4], width=2)
    d.line([(18, 40), (23, 42), (43, 42), (47, 39)], fill=BLUE[3])
    for x in (9, 47):
        p.plate([(x, 25), (x + 3, 19), (x + 7, 20), (x + 8, 25), (x + 8, 40), (x + 5, 46), (x + 1, 44), (x, 40)], WHITE, 2)
        d.line([(x + 2, 25), (x + 4, 21), (x + 5, 21)], fill=WHITE[4])
        d.line((x + 2, 27, x + 2, 38), fill=WHITE[3], width=2)
        d.line((x + 6, 26, x + 6, 40), fill=STEEL[1])
        p.bolt(x + 3, 30)
    d.line((20, 45, 27, 45), fill=STEEL[1]);d.line((37, 45, 44, 45), fill=STEEL[1])
    return p.im


def crystal_seed():
    p = Pixel()
    prism(p, [(17, 25), (28, 18), (38, 22), (36, 38), (27, 48), (17, 41)], (28, 31))
    prism(p, [(36, 36), (43, 33), (50, 38), (45, 48), (37, 50), (33, 45)], (41, 42))
    p.d.polygon([(18, 26), (22, 23), (23, 36), (19, 41), (18, 39)], fill=BLUE[3])
    p.d.line([(21, 25), (23, 24), (24, 31)], fill=WHITE[4])
    p.d.line([(27, 23), (30, 24), (29, 29)], fill=VIOLET[4])
    p.d.line([(27, 38), (30, 35), (32, 36)], fill=VIOLET[3])
    p.d.rectangle((41, 39, 42, 41), fill=VIOLET[4])
    return p.im


def directional_matrix():
    p = Pixel();d = p.d
    p.plate([(8, 16), (21, 10), (29, 17), (25, 25), (23, 41), (42, 45), (45, 25), (40, 19), (48, 14), (57, 22), (53, 53), (17, 52), (8, 43)], STEEL, 2)
    p.plate([(13, 18), (20, 15), (24, 19), (20, 43), (45, 48), (50, 22), (54, 24), (50, 51), (18, 48), (12, 41)], BLACK, 1)
    d.line([(13, 18), (19, 15), (23, 19)], fill=STEEL[4], width=2)
    d.line([(17, 43), (45, 49), (50, 24)], fill=STEEL[3])
    for y in range(23, 42, 4):
        d.line((10, y, 19, y + 2), fill=BLUE[2], width=2);d.line((48, y, 55, y + 1), fill=BLUE[3])
    for x in (26, 32, 38):
        d.line((x, 19, x - 2, 37), fill=STEEL[1], width=3)
        d.line((x, 20, x - 2, 36), fill=STEEL[4])
    p.box((25, 42, 41, 47), WHITE, 2)
    d.line([(30, 44), (33, 44), (33, 43), (36, 45), (33, 46)], fill=BLUE[1])
    p.bolt(17, 12);p.bolt(49, 17);p.bolt(15, 46);p.bolt(46, 49)
    return p.im


def impurity():
    p = Pixel();d = p.d
    grain(p, [(10, 27), (18, 17), (31, 21), (39, 14), (51, 20), (48, 31), (56, 38), (46, 50), (33, 48), (25, 54), (9, 45), (13, 37)], BLACK, 1, 17)
    p.plate([(12, 28), (19, 20), (29, 24), (27, 35), (17, 37)], ASH, 2)
    p.plate([(34, 24), (40, 17), (48, 22), (43, 32), (36, 34)], VIOLET, 1)
    d.line([(38, 23), (43, 21), (42, 28)], fill=VIOLET[2])
    p.plate([(28, 37), (40, 34), (48, 41), (42, 47), (31, 45)], ASH, 1)
    for x, y in [(18, 42), (31, 28), (43, 41), (26, 46), (48, 33)]:
        d.rectangle((x, y, x + 2, y + 1), fill=VIOLET[2]);d.point((x, y), fill=VIOLET[3])
    d.line([(12, 43), (20, 46), (23, 51)], fill=ASH[2])
    d.polygon([(22, 23), (28, 25), (25, 30), (23, 29)], fill=ASH[3])
    d.line([(37, 37), (42, 37), (45, 40)], fill=ASH[2])
    return p.im


def separation():
    p = Pixel();d = p.d
    grain(p, [(7, 35), (15, 25), (30, 27), (33, 36), (23, 44), (10, 42)], CAKE, 2, 3)
    grain(p, [(31, 18), (48, 21), (57, 32), (44, 35), (34, 30)], CAKE, 3, 12)
    grain(p, [(27, 40), (37, 36), (50, 41), (52, 50), (33, 54), (24, 49)], CAKE, 2, 22)
    for a in [[(10, 35), (22, 37), (29, 33)], [(34, 23), (44, 25), (50, 29)], [(29, 45), (38, 48), (47, 45)]]:d.line(a, fill=CAKE[4])
    for x, y in [(12, 45), (20, 21), (55, 38), (24, 55), (43, 56)]:d.rectangle((x, y, x + 2, y + 1), fill=CAKE[2])
    d.line((18, 31, 22, 31), fill=VIOLET[1]);d.rectangle((43, 44, 45, 45), fill=VIOLET[1])
    return p.im


def fuel_matrix():
    p = Pixel();d = p.d
    p.plate([(7, 26), (15, 18), (48, 18), (56, 25), (56, 42), (49, 49), (14, 49), (7, 42)], BLACK, 1)
    p.plate([(12, 26), (17, 22), (46, 22), (50, 26), (50, 39), (45, 43), (17, 43), (12, 39)], PBI, 2)
    for x in range(17, 48, 5):
        d.line((x, 23, x, 42), fill=PBI[0], width=2);d.line((x + 1, 24, x + 1, 41), fill=PBI[4])
    for y in (25, 38):
        p.box((7, y, 56, y + 5), STEEL, 2)
        d.line((12, y + 2, 48, y + 2), fill=STEEL[3])
    p.box((25, 23, 38, 43), BLACK, 1)
    for y in (27, 32, 37):
        d.rectangle((29, y, 34, y + 1), fill=VIOLET[1]);d.point((29, y), fill=VIOLET[3])
    for x, y in [(9, 22), (51, 22), (9, 43), (51, 43)]:p.bolt(x, y)
    return p.im


def blending_residue():
    p = Pixel();d = p.d
    grain(p, [(9, 36), (20, 27), (27, 30), (31, 19), (43, 22), (41, 34), (54, 38), (50, 48), (37, 52), (25, 47), (14, 50)], VIOLET, 1, 15)
    grain(p, [(14, 34), (21, 30), (29, 35), (26, 43), (17, 43)], PBI, 2, 8)
    d.polygon([(31, 23), (37, 22), (34, 36), (38, 40), (35, 46), (31, 41)], fill=PBI[1])
    d.line([(32, 24), (35, 23), (33, 36), (36, 40)], fill=PBI[3])
    d.line([(42, 38), (47, 40), (46, 44), (40, 46)], fill=VIOLET[2], width=2)
    d.polygon([(20, 42), (24, 41), (27, 44), (25, 47), (20, 46)], fill=VIOLET[2])
    d.line((40, 25, 39, 30), fill=VIOLET[3]);d.line((47, 44, 44, 47), fill=VIOLET[3])
    d.line((21, 47, 27, 45), fill=ASH[2]);d.rectangle((51, 53, 54, 54), fill=VIOLET[1])
    return p.im


def micro_template():
    p = Pixel();d = p.d
    p.plate([(9, 17), (40, 12), (47, 18), (44, 46), (13, 51), (8, 46)], STEEL, 1)
    p.plate([(16, 15), (47, 11), (54, 17), (49, 46), (20, 51), (14, 46)], WHITE, 2)
    d.line([(18, 17), (46, 13), (51, 17)], fill=WHITE[4])
    for x, y in [(24, 25), (39, 23), (22, 39), (37, 37)]:
        d.polygon([(x, y - 4), (x + 5, y), (x + 4, y + 5), (x, y + 7), (x - 4, y + 3), (x - 3, y - 2)], fill=BLACK[0])
        d.line([(x - 3, y - 1), (x, y - 3), (x + 3, y)], fill=VIOLET[2])
        d.line((x + 1, y + 5, x + 4, y + 3), fill=WHITE[3])
    d.line((30, 23, 28, 44), fill=STEEL[1]);d.line((33, 21, 31, 43), fill=WHITE[4])
    p.bolt(18, 20);p.bolt(46, 17);p.bolt(18, 45);p.bolt(43, 43)
    return p.im


def micro_unit(p, x, y, size=1, active=False, coating=False):
    d = p.d;pal = WHITE if coating else STEEL
    def at(points):return [(round(x + a * size), round(y + b * size)) for a, b in points]
    d.polygon(at([(-8, -3), (-2, -8), (7, -5), (9, 4), (3, 9), (-6, 5)]), fill=pal[0])
    d.polygon(at([(-7, -3), (-2, -7), (6, -4), (1, 1), (-6, 0)]), fill=pal[3])
    d.polygon(at([(-6, 1), (1, 2), (7, -3), (7, 3), (2, 7), (-5, 4)]), fill=pal[2])
    d.line(at([(-6, -3), (-2, -6), (4, -4)]), fill=pal[4])
    d.polygon(at([(-3, -3), (1, -5), (4, -3), (0, 0)]), fill=BLACK[0])
    if active:d.line(at([(-1, -3), (1, -3)]), fill=BLUE[3], width=max(1, round(size)))
    d.line(at([(-4, 1), (-1, 3), (3, 0)]), fill=GOLD[3] if not coating else VIOLET[2])
    for points in [[(-5, 3), (-9, 5), (-10, 9), (-7, 11)], [(5, 5), (7, 10), (12, 10), (13, 7)]]:
        d.line(at(points), fill=pal[0], width=max(2, round(size * 3)))
        d.line(at(points), fill=pal[3], width=max(1, round(size)))


def unprogrammed():
    p = Pixel();d = p.d
    micro_unit(p, 31, 29, 1.8)
    d.line([(20, 20), (17, 15), (21, 12)], fill=STEEL[0], width=3)
    d.line([(20, 19), (18, 15), (21, 13)], fill=GOLD[3])
    d.line([(34, 18), (39, 13), (43, 16)], fill=STEEL[1], width=3)
    d.line([(35, 17), (39, 14), (42, 16)], fill=GOLD[2])
    for x, y in [(22, 27), (27, 31), (33, 30)]:d.line((x, y, x + 2, y + 1), fill=GOLD[3])
    p.box((27, 32, 34, 39), BLACK, 1)
    d.rectangle((29, 34, 32, 37), fill=BLACK[0])
    return p.im


def swarm(coated=False):
    p = Pixel()
    for x, y, s in [(21, 15, .65), (43, 23, .75), (17, 35, .8), (36, 44, 1.02)]:
        if coated:
            def at(points):return [(round(x + a * s), round(y + b * s)) for a, b in points]
            p.d.polygon(at([(-12, -4), (-4, -11), (8, -8), (14, 0), (11, 9), (1, 13), (-10, 7)]), fill=VIOLET[0])
            p.d.polygon(at([(-11, -3), (-4, -10), (7, -7), (12, 0), (9, 8), (1, 11), (-9, 6)]), fill=WHITE[2])
            p.d.polygon(at([(-8, -2), (-3, -7), (5, -5), (9, 0), (6, 6), (0, 8), (-6, 4)]), fill=BLACK[0])
        micro_unit(p, x, y, s, True, coated)
        if coated:
            p.d.polygon(at([(-12, -3), (-8, -6), (-6, -2), (-7, 4), (-10, 6), (-12, 2)]), fill=WHITE[3])
            p.d.line(at([(-11, -3), (-8, -5), (-7, -3)]), fill=WHITE[4])
            p.d.polygon(at([(7, -5), (11, -2), (13, 3), (10, 8), (6, 8), (7, 3)]), fill=WHITE[2])
            p.d.line(at([(9, -1), (10, 2), (9, 5)]), fill=VIOLET[2], width=max(1, round(s)))
            p.d.line(at([(-4, -9), (1, -9), (6, -7)]), fill=WHITE[4], width=max(1, round(s)))
    return p.im


def inactive_nano():
    p = Pixel();d = p.d
    p.plate([(13, 22), (35, 15), (49, 27), (43, 46), (26, 51), (11, 38)], BLACK, 2)
    p.plate([(15, 22), (35, 17), (46, 27), (26, 35)], STEEL, 2)
    p.plate([(14, 25), (25, 36), (24, 47), (13, 37)], STEEL, 1)
    d.polygon([(23, 24), (33, 21), (39, 27), (29, 31)], fill=BLACK[0])
    d.polygon([(27, 24), (31, 23), (34, 26), (30, 28)], fill=ASH[1])
    for x in (29, 34, 39):d.line((x, 35, x - 2, 43), fill=GOLD[1], width=2)
    d.line((15, 24, 23, 31), fill=STEEL[3]);d.line((34, 18, 42, 25), fill=STEEL[3])
    p.bolt(17, 35);p.bolt(36, 43)
    return p.im


def nano_scrap():
    p = Pixel();d = p.d
    grain(p, [(8, 22), (26, 18), (34, 27), (29, 33), (20, 29), (13, 35), (8, 31)], GOLD, 2, 19)
    d.line([(11, 24), (24, 21), (29, 26), (24, 29)], fill=GOLD[4])
    p.plate([(29, 39), (41, 29), (51, 34), (44, 41), (49, 49), (36, 52), (26, 46)], STEEL, 1)
    for x, y in [(35, 38), (40, 43), (31, 45), (48, 21), (17, 43), (22, 50)]:
        p.box((x, y, x + 5, y + 4), BLACK, 1)
        d.line((x + 1, y - 1, x + 3, y - 1), fill=GOLD[3])
    d.line([(10, 45), (13, 49), (17, 48), (20, 53)], fill=GOLD[2], width=2)
    d.rectangle((52, 46, 55, 48), fill=STEEL[2])
    return p.im


def mold():
    p = Pixel();d = p.d
    for x, y in [(8, 15), (34, 22)]:
        p.plate([(x, y + 4), (x + 15, y), (x + 22, y + 5), (x + 19, y + 31), (x + 5, y + 35), (x, y + 29)], STEEL, 1)
        p.plate([(x + 1, y + 4), (x + 14, y + 1), (x + 19, y + 6), (x + 16, y + 27), (x + 5, y + 30), (x + 2, y + 26)], WHITE, 2)
        d.polygon([(x + 7, y + 8), (x + 13, y + 6), (x + 15, y + 9), (x + 12, y + 23), (x + 7, y + 25), (x + 5, y + 21)], fill=BLACK[0])
        d.line([(x + 7, y + 9), (x + 12, y + 8), (x + 13, y + 10)], fill=WHITE[3])
        d.line([(x + 6, y + 20), (x + 8, y + 22), (x + 11, y + 21)], fill=STEEL[1])
        p.bolt(x + 4, y + 5);p.bolt(x + 12, y + 26)
    d.line((26, 22, 32, 24), fill=STEEL[3], width=2)
    return p.im


def polymer_residue():
    p = Pixel();d = p.d
    grain(p, [(6, 30), (20, 19), (32, 22), (44, 17), (55, 29), (48, 39), (53, 44), (37, 50), (24, 44), (12, 48), (8, 40)], ASH, 2, 34)
    p.plate([(11, 30), (22, 23), (30, 26), (28, 35), (17, 39)], STEEL, 2)
    p.plate([(34, 27), (43, 22), (50, 28), (45, 36), (34, 38)], STEEL, 1)
    d.line([(12, 31), (21, 26), (28, 28)], fill=STEEL[3])
    d.line([(21, 39), (28, 37), (34, 40), (41, 38)], fill=VIOLET[1], width=3)
    d.line((24, 40, 27, 39), fill=VIOLET[2]);d.line((39, 45, 45, 43), fill=ASH[3])
    return p.im


def data_substrate():
    p = Pixel();d = p.d
    p.plate([(14, 9), (42, 9), (51, 17), (51, 48), (44, 55), (14, 55), (10, 50), (10, 14)], STEEL, 2)
    d.polygon([(16, 12), (40, 12), (47, 19), (47, 44), (16, 44)], fill=WHITE[2])
    d.line([(13, 48), (13, 14), (16, 11), (39, 11)], fill=WHITE[4])
    for y in range(17, 42, 5):
        d.line((18, y, 43, y), fill=STEEL[1]);d.line((18, y + 1, 43, y + 1), fill=WHITE[3])
    for x in range(20, 44, 5):d.line((x, 16, x, 42), fill=STEEL[2])
    for x in (18, 24, 30, 36, 42):
        d.rectangle((x, 46, x + 3, 52), fill=STEEL[1]);d.line((x, 46, x + 2, 46), fill=WHITE[4])
    d.line([(19, 22), (24, 22), (24, 32), (39, 32), (39, 37)], fill=BLUE[1])
    p.bolt(12, 12);p.bolt(44, 47)
    return p.im


def encapsulation():
    p = Pixel();d = p.d
    p.cylinder((10, 27, 38, 50), WHITE)
    d.ellipse((13, 29, 35, 36), fill=WHITE[0]);d.ellipse((16, 30, 32, 34), fill=BLACK[0])
    d.line((14, 31, 15, 32), fill=WHITE[4]);d.line((15, 39, 15, 45), fill=WHITE[4], width=2)
    d.ellipse((18, 13, 44, 24), fill=STEEL[3], outline=STEEL[0])
    d.ellipse((23, 16, 39, 21), fill=(0, 0, 0, 0), outline=STEEL[1])
    d.line((22, 15, 39, 15), fill=WHITE[4])
    p.plate([(42, 34), (54, 31), (57, 38), (53, 52), (41, 51), (45, 42)], WHITE, 3)
    d.line([(43, 35), (52, 33), (54, 38)], fill=WHITE[4]);d.line((45, 47, 51, 48), fill=STEEL[2])
    return p.im


def rejected_rod():
    p = Pixel();d = p.d
    p.plate([(9, 26), (15, 20), (49, 20), (56, 27), (56, 40), (50, 47), (15, 47), (9, 41)], STEEL, 1)
    p.box((17, 24, 47, 42), BLACK, 1)
    d.rectangle((19, 29, 44, 37), fill=VIOLET[1]);d.line((20, 29, 43, 29), fill=VIOLET[3])
    p.box((12, 21, 19, 45), WHITE, 2)
    p.plate([(47, 19), (52, 16), (57, 20), (58, 36), (54, 42), (48, 40)], WHITE, 2)
    d.line([(48, 20), (52, 18), (55, 21), (56, 32)], fill=WHITE[4], width=2)
    d.line((48, 24, 49, 37), fill=STEEL[1])
    d.line([(42, 23), (40, 28), (43, 32), (40, 37), (43, 43)], fill=BLACK[0], width=2)
    d.line([(41, 24), (39, 28), (41, 31)], fill=STEEL[3])
    d.line([(39, 37), (42, 43), (45, 44)], fill=STEEL[3])
    p.plate([(27, 13), (39, 13), (43, 18), (39, 31), (25, 29)], CAKE, 3)
    d.line((29, 17, 37, 18), fill='#8a4f48', width=2)
    d.line((29, 22, 37, 23), fill='#8a4f48', width=2)
    d.line((34, 30, 34, 43), fill=CAKE[1]);d.rectangle((30, 44, 38, 46), fill=STEEL[3])
    return p.im


def dense_rod(depleted=False):
    p = Pixel();d = p.d
    p.cylinder((19, 8, 45, 56), STEEL)
    d.rectangle((23, 17, 40, 48), fill=BLACK[0])
    core = ['#403c4a', '#665e74', '#8f8398', '#ada2ae'] if depleted else VIOLET[1:]
    d.rectangle((26, 19, 36, 47), fill=core[0]);d.rectangle((27, 20, 29, 46), fill=core[2])
    d.rectangle((32, 19, 35, 46), fill=core[1]);d.line((28, 22, 28, 39), fill=core[3])
    for y in (14, 46):
        p.box((17, y, 46, y + 7), WHITE, 2)
        d.rectangle((27, y + 2, 36, y + 5), fill=STEEL[2]);d.line((28, y + 2, 35, y + 2), fill=STEEL[4])
    for x in (21, 38):
        d.rectangle((x, 22, x + 3, 44), fill=STEEL[1]);d.line((x, 23, x, 42), fill=STEEL[3])
    p.box((25, 29, 38, 35), STEEL, 2)
    d.line((28, 31, 35, 31), fill=core[2]);d.line((28, 33, 31, 33), fill=core[1])
    for x, y in [(19, 17), (41, 17), (19, 48), (41, 48)]:p.bolt(x, y)
    if depleted:
        for x, y in [(24, 25), (35, 40), (30, 12), (39, 52)]:d.line((x, y, x + 2, y + 1), fill=ASH[1])
    return p.im


def broken_rod(dense=False):
    p = Pixel();d = p.d
    if dense:
        p.plate([(10, 17), (30, 14), (40, 22), (39, 48), (20, 55), (9, 46)], STEEL, 1)
        d.polygon([(15, 23), (29, 20), (34, 24), (33, 44), (21, 48), (15, 43)], fill=ASH[1])
        for x in (19, 25, 30):d.line((x, 26, x - 1, 43), fill=VIOLET[1], width=2)
        p.plate([(40, 20), (49, 15), (56, 24), (55, 47), (48, 52), (43, 47), (47, 37)], WHITE, 1)
        d.line([(43, 22), (49, 19), (53, 25), (52, 37)], fill=WHITE[3])
        for y in (18, 45):p.box((10, y, 36, y + 5), WHITE, 1)
        d.line([(17, 33), (24, 35), (29, 32), (36, 34)], fill=STEEL[0], width=2)
    else:
        p.cylinder((12, 13, 32, 53), STEEL)
        d.polygon([(17, 22), (27, 22), (28, 42), (23, 47), (17, 43)], fill=ASH[1])
        d.line([(19, 25), (21, 30), (19, 35), (23, 41)], fill=VIOLET[1], width=2)
        p.plate([(34, 23), (43, 18), (51, 25), (48, 48), (39, 51), (34, 43), (39, 38)], STEEL, 2)
        d.line([(36, 24), (43, 21), (48, 26)], fill=STEEL[4])
        d.line([(16, 20), (24, 18), (31, 22)], fill=WHITE[3], width=2)
        p.box((11, 46, 32, 51), WHITE, 1)
    for x, y in [(36, 53), (49, 56), (8, 55)]:d.rectangle((x, y, x + 2, y + 1), fill=ASH[2])
    return p.im


def recovered_casing():
    p = Pixel();d = p.d
    p.plate([(12, 15), (35, 14), (43, 21), (36, 28), (22, 29), (17, 36), (23, 42), (18, 48), (8, 40), (8, 29)], STEEL, 2)
    d.polygon([(15, 20), (31, 19), (35, 21), (30, 24), (20, 24), (14, 30), (13, 38), (11, 36), (12, 28)], fill=WHITE[3])
    d.line([(17, 35), (19, 32), (27, 31)], fill=STEEL[0])
    p.plate([(31, 37), (49, 29), (57, 36), (52, 42), (39, 44), (35, 51), (24, 53), (26, 46)], STEEL, 2)
    d.line([(32, 38), (49, 31), (54, 36)], fill=WHITE[4])
    d.line([(30, 47), (37, 40), (48, 39)], fill=WHITE[3])
    d.line((43, 46, 53, 47), fill=STEEL[1], width=2);p.bolt(22, 55)
    return p.im


def inactive_residue():
    p = Pixel();d = p.d
    for pts, sh, off in [([(8, 37), (24, 29), (31, 35), (27, 46), (12, 46)], 2, 1), ([(29, 35), (42, 29), (55, 39), (49, 49), (32, 49)], 1, 23), ([(18, 46), (32, 40), (43, 48), (39, 55), (23, 56)], 2, 9)]:grain(p, pts, ASH, sh, off)
    for x, y in [(6, 46), (12, 52), (20, 26), (47, 54), (56, 47), (31, 58)]:d.rectangle((x, y, x + 2, y + 1), fill=ASH[2])
    for x, y in [(21, 38), (36, 47), (46, 38)]:d.rectangle((x, y, x + 2, y + 1), fill=VIOLET[0])
    d.line((18, 33, 23, 31), fill=ASH[3]);d.line((36, 43, 42, 44), fill=ASH[2])
    return p.im


def energy_crystal():
    p = Pixel();d = p.d
    prism(p, [(9, 28), (25, 14), (44, 18), (56, 34), (39, 50), (18, 47)], (30, 32))
    d.polygon([(10, 29), (16, 23), (18, 34), (22, 37), (18, 43), (14, 39)], fill=VIOLET[2])
    d.polygon([(27, 18), (35, 20), (39, 30), (32, 29), (28, 26)], fill=VIOLET[4])
    d.polygon([(38, 34), (46, 29), (52, 34), (46, 42), (42, 42)], fill=VIOLET[3])
    d.line([(21, 27), (24, 29), (25, 36), (29, 39)], fill=VIOLET[1])
    d.line([(35, 36), (33, 43), (37, 47)], fill=VIOLET[2])
    d.polygon([(17, 32), (20, 30), (22, 33), (21, 36), (18, 35)], fill=VIOLET[3])
    d.polygon([(29, 20), (34, 22), (35, 25), (32, 25)], fill=VIOLET[3])
    d.polygon([(41, 23), (44, 26), (42, 30), (39, 28)], fill=VIOLET[1])
    d.line((15, 28, 18, 25), fill=VIOLET[4]);d.line((44, 36, 46, 35), fill=VIOLET[4])
    return p.im


def soulium_mass(stable=False):
    p = Pixel();d = p.d
    if stable:
        p.plate([(8, 33), (15, 22), (34, 17), (51, 23), (57, 34), (51, 45), (33, 51), (15, 46)], STEEL, 2)
        p.plate([(12, 31), (18, 24), (34, 20), (49, 25), (52, 31), (33, 38), (18, 36)], WHITE, 2)
        d.line([(13, 31), (20, 25), (34, 22), (44, 24)], fill=WHITE[4], width=2)
        d.line([(14, 39), (30, 45), (46, 41), (51, 36)], fill=STEEL[1])
        for x, y in [(23, 29), (30, 27), (37, 25), (31, 34), (39, 32), (46, 29)]:d.line((x, y, x + 3, y - 1), fill=WHITE[3])
        d.line([(23, 41), (30, 43), (35, 41)], fill=VIOLET[1])
    else:
        grain(p, [(7, 31), (17, 20), (26, 23), (36, 17), (49, 22), (46, 27), (57, 32), (52, 45), (38, 49), (28, 44), (16, 49), (8, 40)], STEEL, 2, 27)
        p.plate([(11, 29), (19, 23), (27, 27), (35, 22), (43, 25), (40, 33), (28, 36), (17, 34)], WHITE, 2)
        for x, y in [(19, 29), (30, 28), (40, 29), (24, 39), (42, 39), (15, 39), (49, 34)]:
            d.rectangle((x, y, x + 3, y + 2), fill=BLACK[1]);d.line((x, y + 3, x + 2, y + 3), fill=STEEL[3])
        d.line([(30, 33), (33, 37), (30, 41)], fill=VIOLET[1])
    return p.im


ART = {
    'analyzed_honkai_sample': analyzed, 'honkai_reference_sample': reference,
    'honkai_crystal_seed': crystal_seed, 'directional_crystallization_matrix': directional_matrix,
    'concentrated_honkai_impurity': impurity, 'separation_residue': separation,
    'fuel_matrix': fuel_matrix, 'fuel_blending_residue': blending_residue,
    'soulium_microstructure_template': micro_template, 'unprogrammed_nanobot': unprogrammed,
    'controlled_nano_swarm': swarm, 'inactive_nano_unit': inactive_nano,
    'coated_nano_swarm': lambda: swarm(True), 'nano_assembly_scrap': nano_scrap,
    'soulium_casting_mold': mold, 'soulium_polymerization_residue': polymer_residue,
    'soulium_data_substrate': data_substrate, 'fuel_encapsulation_part': encapsulation,
    'rejected_fuel_rod': rejected_rod, 'depleted_dense_honkai_fuel_rod': lambda: dense_rod(True),
    'broken_honkai_fuel_rod': broken_rod, 'broken_dense_honkai_fuel_rod': lambda: broken_rod(True),
    'recovered_fuel_casing_material': recovered_casing, 'inactive_fuel_residue': inactive_residue,
    'honkai_energy_crystal': energy_crystal, 'dense_honkai_fuel_rod': dense_rod,
    'soulium_proto_mass': soulium_mass, 'stabilized_soulium_proto_mass': lambda: soulium_mass(True),
}

DESIGNS = [
    ('analyzed_honkai_sample', '已分析崩坏能样本', 'I02由崩坏能分析样本与纸产出；用于标准样本、探测器校准等。', SPECTRUM, 'industrial_initial_spectrum', '玻璃取样瓶和随瓶纸标签；瓶底少量紫色样品，标签以谱线表达已分析。玻璃与纸来自投入，标签位置和谱线为拟定视觉。'),
    ('honkai_reference_sample', '崩坏能标准样本', '装配机消耗已分析样本、玻璃板、铂箔与MAX电路；标准样本用于采集、校准与调配。', MAT, 'industrial_honkai_reference_sample', '圆弧封装玻璃安瓿与铂色端盖，内置占据主画面的紫色样品切面、晶粒和包裹体；取消屏幕式底座。封装与样品切面为拟定视觉，不是配方限定物态。'),
    ('honkai_crystal_seed', '崩坏结晶晶种', '由原始粒子、钻石、不锈钢板和MAX电路制造；I08消耗晶种和定向基质进行增殖。', MAT, 'industrial_honkai_crystal_seed', '两枚小而完整的紫色籽晶，淡青钻石质边和锐利晶面，体量小于固态结晶。晶体形状与紫色分配为拟定视觉。'),
    ('directional_crystallization_matrix', '定向结晶基质', '场发生器、传感器、钨钢板、铌钛细线与MAX电路装配；参与分馏、稳定与晶体生长。', MAT, 'industrial_directional_crystallization_matrix', '有明确空槽和纵向导向轨的U形钨钢磁轭；两侧冷蓝线圈，底部感测头。构件布局与色彩为拟定视觉。'),
    ('concentrated_honkai_impurity', '浓缩崩坏杂质', '液态分馏、固态采集和晶体生长副产；也投入提纯和稳定工序。', LIQUID, 'industrial_liquid_fractionation', '一块不规则深色致密杂质，暴露少量暗紫夹杂面；与松散残渣区分。物态质感和夹杂位置为拟定视觉。'),
    ('separation_residue', '分离残渣', '液态分馏和多种回收工序副产；可再投入提纯、稳定与燃料调配。', LIQUID, 'industrial_liquid_fractionation', '三片断裂薄滤饼，灰褐粉粒断面、少量紫色夹点；以薄片而非矿石簇区分。滤饼形制为拟定视觉。'),
    ('fuel_matrix', '崩坏燃料基质', '由钨钢板、PBI箔、MAX场发生器、发射器与电路装配；用于燃料调配、浓缩及网络注入。', MAT, 'industrial_fuel_matrix', '横向开架约束组件，钨钢横梁、琥珀色PBI叠片和少量紫色状态槽；不能画成单纯粉末压块。具体形制和颜色为拟定视觉。'),
    ('fuel_blending_residue', '燃料调配尾料', '燃料调配、浓缩和稳定介质回收副产；加碳粉与水处理为失活残渣。', LIQUID, 'industrial_liquid_fuel_blending', '凝结暗紫尾料包覆撕裂琥珀绝缘薄片，保留黏结不均与无规则边缘。凝胶质感及露出的基质碎片为拟定视觉。'),
    ('soulium_microstructure_template', '魂钢微结构模板', '铂箔、钨钢板和晶种制得；I09返回模板，I10消耗模板制纳米单元。', RECIPE, 'industrial_soulium_template', '双层铂色精密负形样板，四个晶格形开孔和定位孔；表现模板而非成品电路。开孔图样与叠层为拟定视觉。'),
    ('unprogrammed_nanobot', '未编程纳米机器人', '纳米构筑单元、金箔、适配基板与焊料装配成机器人；等待重构规则编程。', RECIPE, 'industrial_nano_assembly', '单枚放大的微装配器，斜面金属壳、金色背触点、两只机械夹臂和空逻辑槽。外形为拟定视觉。'),
    ('controlled_nano_swarm', '受控自组织纳米群', 'I12消耗未编程机器人、重构规则载体及工艺溶剂产出；后续进入涂层工序。', RECIPE, 'industrial_nano_control', '四枚分离微装配器形成错落队列，各带青色工作灯，不以UI连线代替实体。数量与排列仅为拟定视觉，不代表配方计数。'),
    ('inactive_nano_unit', '失活纳米单元', '纳米构筑、控制与涂层步骤均可产生的失活副产。', RECIPE, 'industrial_nano_building', '无灯光的微型封装块，灰暗逻辑腔和氧化暗金触点；不默认失活就已机械破裂。形状和氧化表现为拟定视觉。'),
    ('coated_nano_swarm', '抗侵蚀涂层纳米群', 'I13用受控纳米群与抗侵蚀涂层制造；I14投入魂钢聚合。', RECIPE, 'industrial_nano_coating', '各微装配器增加分段外覆壳环与侧翼护壳，扩大实体外轮廓，白色板面、暗关节缝和紫色包边区别普通群。壳环外观与涂层色彩为拟定视觉，非新增配方材料。'),
    ('nano_assembly_scrap', '纳米装配废料', 'I11装配副产；I05可回收少量纳米构筑单元并产生分离残渣。', RECIPE, 'industrial_nano_assembly', '撕裂金箔微框、短导体与散落微封装碎片；用混合废件轮廓区别完整单元。断裂位置为拟定视觉。'),
    ('soulium_casting_mold', '魂钢聚合模具', '钨钢板、铂箔与焊料装配；名称注册在魂钢工艺组。', RECIPE, 'industrial_soulium_casting_mold', '一对打开的长条钨钢模瓣，铂色内衬和细长凹腔；不用黄铜内衬。分体结构和凹腔为拟定视觉。'),
    ('soulium_polymerization_residue', '魂钢聚合残渣', 'I09由钛粉、铂粉、稳定液与溶剂制前驱液时产生，模板返回。', RECIPE, 'industrial_soulium_precursor', '灰银薄片状沉积物，局部深紫胶结缝；不把I09副产冒充I14成型废块。沉积形制与色彩为拟定视觉。'),
    ('soulium_data_substrate', '魂钢数据基板', 'I16由魂钢板与魂钢细线加工，消耗焊料与冷却剂。', RECIPE, 'industrial_soulium_data_substrate', '竖置缺角魂钢基片，细密银色线网与下缘焊盘，保留大片裸基材；不画成装满芯片的成品电路。图样为拟定视觉。'),
    ('fuel_encapsulation_part', '燃料封装组件', '装配机投入PTFE板与铂箔；灌装样件及I18封棒消耗此组件。', BOOT, 'industrial_fuel_encapsulation_part', '白色PTFE短衬套、分离铂色垫圈与折叠密封片；不用没有材料依据的黄铜端盖。具体几何为拟定视觉。'),
    ('rejected_fuel_rod', '不合格燃料棒', 'I02隔离实验消耗封装试验样件、标准样本与纸，输出不合格棒并记录RN-FRP。', BOOT, 'industrial_fuel_rod_isolation_experiment', '短横置封装棒附试验纸签，端盖明显上移倾斜，侧壳有阶梯裂缝，使缺陷在不读纸签时也可辨。错位与裂缝为本轮美术辨识推导，配方未限定不合格原因。'),
    ('depleted_dense_honkai_fuel_rod', '乏浓缩崩坏燃料棒', 'I20/I21/I22消耗浓缩燃料棒发电，输出乏棒；可开壳与再处理。', RECIPE, 'industrial_reactor_i20', '与浓缩棒共用粗筒结构，内容变失色灰紫并有沉积斑；外壳完整。失色和斑纹为拟定视觉。'),
    ('broken_honkai_fuel_rod', '破损崩坏燃料棒', 'I05开壳工序把乏普通棒转为破损棒；再处理回收壳材与失活残渣。', RECIPE, 'industrial_spent_rod_casing_opening', '普通细筒侧板剥开、内腔失色，一片拆下的弯曲壳板在旁；不用活性发光断芯。拆口位置为拟定视觉。'),
    ('broken_dense_honkai_fuel_rod', '破损浓缩崩坏燃料棒', 'I05开浓缩乏棒壳得到；再处理产壳材与更多失活残渣。', RECIPE, 'industrial_dense_spent_rod_casing_opening', '更粗的多梁壳体打开，白衬分瓣和暗灰紫残留外露；区别普通细筒。拆解几何为拟定视觉。'),
    ('recovered_fuel_casing_material', '回收燃料壳体材料', '乏棒与破损棒再处理产物；四份壳材再制一份棒壳并产残渣。', RECIPE, 'industrial_dense_spent_rod_reprocessing', '卷曲冷灰薄壳、铂色内表面和折叠长条；不增加无依据的铜屑。卷曲位置为拟定视觉。'),
    ('inactive_fuel_residue', '失活燃料残渣', '乏棒再处理、尾料处理和废液固化产出；与水离心得灰烬。', LIQUID, 'industrial_effluent_solidification', '低矮细碎灰黑固化渣和少量暗紫夹点，无发光；灰分质感和轮廓为拟定视觉。'),
    ('honkai_energy_crystal', '固态崩坏能结晶', '液态稳定工序产出；用于调配燃料、浓缩核心及网络注入。', LIQUID, 'industrial_liquid_stabilization', '单块宽厚不对称晶体，清晰紫色分区晶面和少量内部解理；区别小籽晶。颜色与晶形为拟定视觉。'),
    ('dense_honkai_fuel_rod', '浓缩崩坏燃料棒', 'I18以棒壳、四个封装件、浓缩液态燃料及冷却剂封装；另有魂钢材料装配路线。', RECIPE, 'industrial_dense_rod_encapsulation', '竖置粗筒，铂灰纵梁与白色PTFE端衬，窗口显示密实紫色燃料；不用金帽。筒形与窗口布局为拟定视觉。'),
    ('soulium_proto_mass', '粗魂钢坯', 'I14由涂层纳米群、钨钢粉及魂钢前驱液聚合得到。', RECIPE, 'industrial_soulium_polymerization', '低矮多孔金属海绵团，灰银凝结皮与暗孔，非天然矿石。多孔形制与紫色缝为拟定视觉。'),
    ('stabilized_soulium_proto_mass', '稳定魂钢坯', 'I15消耗粗坯、规则载体和稳定介质，产稳定坯与加工屑；仍是后续定向组件原料。', RECIPE, 'industrial_soulium_reconstruction', '致密低矮圆钝金属团，排列整齐的晶粒高光和小量紫色接缝；不假定已铸成标准锭。轮廓与纹理为拟定视觉。'),
]


def draw(ident):
    return ART[ident]()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
    sheet = Image.new('RGB', (1000, 6 * 184), '#292d34');d = ImageDraw.Draw(sheet)
    records = []
    for i, (ident, name, function, path, recipe, design) in enumerate(DESIGNS):
        im = draw(ident)
        im.save(ASSETS / f'{ident}.png');im.save(OUT / f'{ident}.png')
        x, y = i % 5 * 200, i // 5 * 184
        d.rectangle((x + 4, y + 4, x + 195, y + 179), fill='#353a43')
        large = im.resize((128, 128), Image.Resampling.NEAREST)
        sheet.paste(large, (x + 36, y + 7), large)
        d.text((x + 8, y + 142), f'{i + 1:02} {name}', font=font, fill='#ebe7db')
        records.append({'id': ident, 'name': name, 'function': function, 'text_evidence': {'path': path, 'recipe': recipe}, 'design_inference': design, 'size': [64, 64]})
    sheet.save(OUT / 'process-r3-contact-sheet.png')
    (OUT / 'design-process.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('工艺组R3：28张；已保存新图、组图和独立设计依据。')


if __name__ == '__main__':
    main()
