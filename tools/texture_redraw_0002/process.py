from pathlib import Path
import hashlib
import json
import random

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl/textures/item'
OUT = ROOT / 'logs/textures-redraw-0002-v2-20261114/process'
METAL = ['#252a32', '#3e4751', '#64727d', '#8e9fa7', '#c0cdd0', '#e8eeeb']
GOLD = ['#4f3b29', '#7e5d36', '#aa8246', '#c9a967', '#ede0a1']
PURPLE = ['#35233f', '#583461', '#80488c', '#aa5bbc', '#d187d8', '#f2bce9']
CYAN = ['#244554', '#387282', '#63b6c3', '#b8e3df']
INK = '#232631'


def canvas():
    im = Image.new('RGBA', (64, 64))
    return im, ImageDraw.Draw(im)


def surface(im, points, palette=METAL, light=2, seed=0):
    mask = Image.new('L', (64, 64))
    ImageDraw.Draw(mask).polygon(points, fill=255)
    px, mp = im.load(), mask.load()
    rng = random.Random(seed)
    grain = [[rng.choice((-1, 0, 0, 0, 1)) for x in range(32)] for y in range(32)]
    for y in range(64):
        for x in range(64):
            if mp[x, y]:
                band = light + grain[y // 2][x // 2]
                px[x, y] = (*tuple(bytes.fromhex(palette[max(0, min(len(palette) - 1, band))][1:])), 255)
    ImageDraw.Draw(im).line(points + [points[0]], fill=palette[0])


def bolt(d, x, y, warm=False):
    p = GOLD if warm else METAL
    d.rectangle((x, y, x + 3, y + 3), fill=p[0])
    d.line((x, y, x + 2, y), fill=p[-2])
    d.point((x + 1, y + 1), fill=p[2])
    d.point((x + 2, y + 2), fill=p[1])


def glint(d, x, y, color='#f0e8f0'):
    d.line((x - 2, y, x + 1, y), fill=color)
    d.line((x, y - 2, x, y + 1), fill=color)


def crystal(im, x, y, w, h, seed=0, pale=False):
    d = ImageDraw.Draw(im)
    p = ['#283c48', '#416473', '#6b94a5', '#a4ccd4', '#dcece9', '#f3f3dd'] if pale else PURPLE
    pts = [(x + w // 2, y), (x + w - 2, y + h // 4), (x + w, y + h * 3 // 4), (x + w // 2, y + h), (x, y + h * 3 // 4), (x + 1, y + h // 3)]
    surface(im, pts, p, 2, seed)
    d.polygon([pts[0], (x + w // 2 - 1, y + h * 2 // 3), pts[4], pts[5]], fill=p[3])
    d.polygon([pts[0], pts[1], (x + w * 3 // 4, y + h * 2 // 3), (x + w // 2 - 1, y + h * 2 // 3)], fill=p[4])
    d.polygon([(x + w // 2 - 1, y + h * 2 // 3), (x + w * 3 // 4, y + h * 2 // 3), pts[3]], fill=p[2])
    d.polygon([(x + w // 3, y + h // 4), (x + w // 3 + 2, y + h // 4 - 2), (x + w // 3 + 1, y + h // 2), (x + w // 4, y + h * 3 // 5)], fill=p[4])
    d.polygon([(x + w * 3 // 4, y + h // 3), (x + w - 2, y + h // 2), (x + w - 1, y + h * 2 // 3), (x + w * 3 // 4, y + h * 3 // 4)], fill=p[3])
    d.line([(x + w // 3, y + h * 3 // 4), (x + w // 2 - 1, y + h * 2 // 3), (x + w // 2 + 2, y + h * 2 // 3)], fill=p[4])
    d.line((x + w // 2 + 2, y + h * 4 // 5, x + w // 2 + 1, y + h - 4), fill=p[1])
    for dx, dy in [(w // 3, h // 2 + 3), (w * 2 // 3, h // 3), (w // 2 + 1, h // 2 + 5)]:
        d.rectangle((x + dx, y + dy, x + dx + 1, y + dy + 2), fill=p[3])
    d.line([pts[0], pts[5], (x + 2, y + h // 2)], fill=p[5])
    d.line((x + w // 2 - 1, y + 5, x + w // 2 - 1, y + h // 2), fill=p[5])
    d.line((x + w - 2, y + h // 3, x + w - 1, y + h * 2 // 3), fill=p[1])
    d.point((x + w // 2 + 2, y + h - 5), fill=p[4])


def ore(im, x, y, w, h, palette, seed=0):
    rng = random.Random(seed)
    d = ImageDraw.Draw(im)
    pts = [(x + 2, y + h // 3), (x + w // 3, y), (x + w * 2 // 3, y + 1), (x + w - 2, y + h // 3), (x + w, y + h * 3 // 4), (x + w * 2 // 3, y + h), (x + 3, y + h - 2), (x, y + h * 2 // 3)]
    surface(im, pts, palette, 2, seed)
    d.polygon([pts[1], pts[2], (x + w * 2 // 3 - 2, y + h // 3), (x + w // 3, y + h // 2), pts[0]], fill=palette[3])
    d.line([pts[0], pts[1], (x + w * 2 // 3 - 2, y)], fill=palette[-1])
    d.line([(x + w // 3, y + h // 2), (x + w // 2, y + h * 2 // 3), (x + w // 2 - 1, y + h - 2)], fill=palette[0])
    for _ in range(7):
        px, py = x + rng.randrange(3, max(4, w - 3)), y + rng.randrange(3, max(4, h - 3))
        if im.getpixel((px, py))[3]:
            d.rectangle((px, py, px + 1, py + 1), fill=rng.choice(palette[1:4]))


def dust(kind):
    im, d = canvas()
    palettes = {
        'ash': ['#343034', '#58504a', '#817367', '#a19681', '#c0b89c'],
        'inactive': ['#302e35', '#514851', '#746a73', '#9a909b', '#bdb3b8'],
        'blend': ['#332a36', '#58434d', '#81616d', '#a68587', '#c4a69c'],
    }
    p = palettes[kind]
    for i, (x, y, w, h) in enumerate([(19, 29, 17, 16), (30, 32, 18, 17), (12, 38, 16, 15), (40, 39, 13, 13), (23, 39, 20, 15), (6, 47, 9, 7), (46, 48, 12, 8), (16, 50, 15, 7)]):
        ore(im, x, y, w, h, p, i + 23)
    rng = random.Random(25)
    for _ in range(33):
        x, y = rng.randrange(6, 58), rng.randrange(37, 58)
        if im.getpixel((x, y))[3]:
            d.rectangle((x, y, x + 1, y + 1), fill=p[rng.randrange(1, 5)])
    for x, y in [(7, 54), (12, 58), (32, 58), (55, 43), (49, 56), (4, 48)]:
        d.rectangle((x, y, x + 2, y + 1), fill=p[2])
    if kind == 'blend':
        d.polygon([(17, 30), (27, 24), (33, 28), (23, 35), (25, 39), (18, 36)], fill=GOLD[1])
        d.line([(18, 30), (27, 25), (31, 27), (22, 33)], fill=GOLD[3])
        d.line((38, 39, 43, 35), fill=PURPLE[3], width=2)
    if kind == 'ash':
        for x, y in [(22, 36), (36, 46), (44, 42), (15, 48)]:
            d.line((x, y, x + 2, y - 1), fill=PURPLE[2])
    return im


def analyzed():
    im, d = canvas()
    surface(im, [(6, 29), (40, 9), (57, 23), (23, 54), (6, 41)], METAL, 2, 4)
    d.polygon([(9, 30), (40, 12), (53, 23), (23, 49), (9, 40)], fill='#536775')
    d.polygon([(11, 30), (40, 14), (49, 23), (23, 46), (11, 39)], fill='#85a0a8')
    d.polygon([(15, 32), (38, 18), (44, 23), (24, 41), (17, 38)], fill='#435367')
    d.polygon([(20, 30), (29, 24), (35, 24), (40, 28), (29, 38), (23, 37)], fill=PURPLE[1])
    d.polygon([(22, 30), (30, 26), (34, 26), (34, 30), (27, 35), (24, 34)], fill=PURPLE[3])
    d.line([(23, 31), (28, 28), (31, 28)], fill=PURPLE[5])
    d.rectangle((31, 29, 33, 31), fill=PURPLE[4])
    d.line([(9, 29), (40, 11), (51, 21)], fill=METAL[5])
    d.line([(9, 39), (23, 51), (55, 23)], fill=METAL[1])
    d.polygon([(11, 31), (16, 28), (23, 34), (18, 39), (11, 35)], fill='#dbded1')
    d.line((14, 32, 17, 30), fill='#5c6868')
    d.line((15, 35, 20, 32), fill='#7b8580')
    d.polygon([(37, 37), (45, 30), (51, 35), (44, 43)], fill=METAL[0])
    d.line([(40, 36), (43, 38), (47, 33)], fill=CYAN[2], width=2)
    return im


def reference():
    im, d = canvas()
    d.polygon([(14, 16), (18, 13), (20, 18), (20, 47), (46, 47), (46, 18), (49, 15), (51, 19), (51, 52), (14, 52)], fill=GOLD[0])
    d.line([(16, 19), (16, 49), (49, 49), (49, 20)], fill=GOLD[2], width=2)
    surface(im, [(23, 11), (40, 11), (44, 16), (44, 44), (40, 49), (23, 49), (19, 44), (19, 16)], METAL, 1, 2)
    d.rectangle((23, 17, 40, 42), fill='#314252')
    d.rectangle((25, 21, 38, 42), fill=PURPLE[1])
    d.polygon([(25, 28), (31, 25), (38, 28), (38, 40), (25, 40)], fill=PURPLE[2])
    d.polygon([(26, 31), (30, 28), (32, 31), (30, 37), (26, 36)], fill=PURPLE[4])
    d.polygon([(33, 35), (36, 31), (38, 34), (36, 40), (33, 40)], fill=PURPLE[3])
    d.line((23, 19, 23, 39), fill='#c4dfdf', width=2)
    d.line((26, 19, 26, 24), fill='#7dabb8')
    d.line((40, 19, 40, 38), fill='#496773')
    d.rectangle((20, 11, 43, 17), fill=METAL[2]);d.line((22, 11, 41, 11), fill=METAL[5])
    d.rectangle((23, 7, 40, 11), fill=METAL[1]);d.line((24, 7, 38, 7), fill=METAL[4])
    for x in (25, 29, 33, 37):d.line((x, 12, x, 15), fill=METAL[4])
    d.rectangle((20, 41, 43, 46), fill=METAL[2]);d.line((22, 41, 41, 41), fill=METAL[4])
    d.rectangle((28, 42, 37, 45), fill='#d8d5b7');d.line((30, 43, 34, 43), fill='#70664c')
    for y in (23, 28, 33, 38):d.line((43, y, 46, y), fill=GOLD[4])
    bolt(d, 15, 47, True);bolt(d, 47, 47, True)
    return im


def seed():
    im, d = canvas()
    crystal(im, 23, 7, 20, 33)
    surface(im, [(10, 31), (15, 29), (22, 39), (35, 44), (44, 34), (49, 32), (53, 35), (44, 51), (34, 56), (19, 49), (9, 38)], METAL, 2, 4)
    d.line([(12, 33), (22, 45), (34, 50), (44, 43), (50, 35)], fill=METAL[4], width=2)
    d.line([(14, 32), (23, 42), (28, 43)], fill=METAL[5])
    d.line([(30, 47), (34, 48), (41, 43)], fill=GOLD[3], width=2)
    d.line([(22, 39), (22, 34), (19, 32)], fill=GOLD[1], width=3)
    d.line([(41, 39), (43, 32), (46, 30)], fill=GOLD[2], width=3)
    bolt(d, 18, 44);bolt(d, 39, 46)
    return im


def matrix():
    im, d = canvas()
    surface(im, [(7, 25), (34, 8), (57, 25), (57, 39), (30, 57), (7, 41)], METAL, 1, 9)
    surface(im, [(8, 24), (34, 9), (55, 24), (29, 43)], METAL, 3, 12)
    d.line([(8, 25), (29, 43), (55, 25)], fill=METAL[5])
    for k in range(4):
        x, y = 16 + k * 6, 23 - k * 3
        d.line([(x, y), (x + 16, y + 11), (x + 18, y + 9)], fill=METAL[0], width=3)
        d.line([(x, y - 1), (x + 16, y + 10)], fill=GOLD[3])
    for k in range(3):
        d.line([(15 + k * 5, 28 + k * 4), (39 + k * 5, 15 + k * 4)], fill=METAL[1], width=2)
    crystal(im, 26, 20, 11, 17)
    d.line([(12, 39), (29, 51), (52, 36)], fill=METAL[3])
    for x, y in [(11, 25), (32, 12), (49, 25), (28, 37)]:bolt(d, x, y)
    return im


def impurity():
    im, d = canvas()
    p = ['#25232c', '#39343d', '#514752', '#6b5d6b', '#8c7a88']
    for i, a in enumerate([(11, 24, 24, 22), (26, 10, 23, 31), (29, 31, 25, 23), (7, 39, 23, 15)]):ore(im, *a, p, i + 5)
    for pts in [[(31, 15), (35, 22), (31, 28), (35, 35)], [(16, 30), (21, 34), (26, 31)], [(39, 37), (43, 41), (41, 48)]]:
        d.line(pts, fill=PURPLE[1], width=3);d.line(pts, fill=PURPLE[3])
    for x, y in [(23, 21), (17, 40), (45, 31), (49, 51)]:d.rectangle((x, y, x + 2, y + 1), fill=PURPLE[2])
    d.rectangle((7, 54, 11, 56), fill=p[2]);d.rectangle((52, 47, 55, 49), fill=p[1])
    return im


def fuel_matrix():
    im, d = canvas()
    p = ['#282831', '#41404a', '#5a5663', '#7b7282', '#a79aab']
    surface(im, [(10, 24), (33, 11), (54, 23), (54, 43), (32, 56), (10, 43)], p, 1, 4)
    surface(im, [(11, 23), (33, 11), (53, 23), (31, 37)], p, 2, 8)
    d.line([(11, 24), (31, 37), (53, 24)], fill=p[4])
    d.line([(11, 32), (31, 45), (53, 32)], fill=p[0], width=2)
    d.line([(11, 39), (31, 52), (53, 39)], fill=p[0], width=2)
    for x, y in [(23, 23), (32, 17), (40, 23), (29, 29), (18, 26), (36, 28)]:
        d.polygon([(x, y), (x + 3, y - 1), (x + 5, y + 2), (x + 2, y + 4), (x, y + 2)], fill=p[0])
        d.line((x + 1, y + 2, x + 3, y + 2), fill=PURPLE[3])
    d.line([(15, 29), (22, 34), (22, 37)], fill=PURPLE[2]);d.line((37, 43, 47, 37), fill=PURPLE[2])
    return im


def template():
    im, d = canvas()
    surface(im, [(8, 19), (45, 10), (56, 19), (49, 48), (16, 55), (7, 47)], METAL, 1, 8)
    surface(im, [(11, 20), (44, 13), (52, 20), (46, 45), (17, 51), (11, 45)], METAL, 3, 16)
    d.polygon([(17, 23), (43, 17), (47, 22), (42, 41), (20, 46), (16, 41)], fill='#384c58')
    for k in range(4):
        d.line([(20 + k * 6, 23 - k), (18 + k * 6, 38 - k), (22 + k * 6, 41 - k)], fill=GOLD[2])
        d.line([(20 + k * 6, 26 - k), (27 + k * 4, 34 - k), (26 + k * 4, 39 - k)], fill=GOLD[3])
    for x, y in [(22, 29), (30, 25), (37, 32), (28, 39)]:
        d.rectangle((x, y, x + 2, y + 2), fill=CYAN[1]);d.point((x, y), fill=CYAN[3])
    d.line([(12, 19), (44, 12), (52, 19)], fill=METAL[5])
    for x, y in [(11, 22), (46, 20), (16, 46), (44, 43)]:bolt(d, x, y)
    d.line((22, 49, 35, 46), fill=GOLD[4])
    return im


def bot(im, x, y, s=1, coated=False, dead=False, active=False):
    d = ImageDraw.Draw(im)
    p = ['#34303b', '#61586f', '#9b95aa', '#d2cdda', '#ece7e8', '#f8f2e1'] if coated else METAL
    def pts(a):return [(round(x + u * s), round(y + v * s)) for u, v in a]
    for a in [[(-5, -4), (-9, -7), (-9, -11)], [(5, -4), (9, -7), (10, -11)], [(-6, 0), (-11, 0), (-13, 3)], [(6, 0), (11, 0), (13, 3)], [(-5, 5), (-9, 8), (-9, 12)], [(5, 5), (9, 8), (10, 12)]]:
        if dead and a == [(5, -4), (9, -7), (10, -11)]:continue
        d.line(pts(a), fill=p[0], width=max(2, round(3 * s)))
        d.line(pts(a), fill=p[3], width=max(1, round(s)))
        u, v = pts(a)[-1];d.point((u - 1, v - 1), fill=p[5])
        u, v = pts(a)[1];d.rectangle((u, v, u + 1, v + 1), fill=p[1])
    d.polygon(pts([(-6, -5), (-3, -8), (3, -8), (7, -3), (6, 5), (2, 9), (-3, 8), (-7, 3)]), fill=p[0])
    d.polygon(pts([(-5, -4), (-2, -7), (3, -6), (5, -2), (4, 5), (1, 7), (-3, 6), (-5, 2)]), fill=p[3])
    d.line(pts([(-5, -3), (-2, -6), (2, -6)]), fill=p[5], width=max(1, round(s)))
    d.polygon(pts([(-3, -2), (3, -2), (3, 4), (-3, 4)]), fill=p[0])
    d.polygon(pts([(-5, -3), (-3, -5), (-3, 3), (-5, 2)]), fill=p[4])
    d.polygon(pts([(4, -3), (5, -1), (4, 4), (3, 5), (3, -2)]), fill=p[1])
    d.line(pts([(-1, -1), (1, -1), (1, 2)]), fill=('#66545d' if dead else CYAN[2] if coated or active else GOLD[3]), width=max(1, round(s)))
    for u, v in [(-2, -4), (0, -4), (2, -4), (-2, 5), (0, 5), (2, 5)]:
        ax, ay = pts([(u, v)])[0];d.point((ax, ay), fill=GOLD[3])
    d.line(pts([(4, 2), (3, 5), (0, 7)]), fill=p[1], width=max(1, round(s)))


def nano(single=False, coated=False, dead=False):
    im, d = canvas()
    if single:
        bot(im, 32, 30, 1.7, dead=dead)
        if dead:
            d.line([(38, 17), (35, 27), (40, 35), (33, 41)], fill=METAL[0], width=2)
            d.line([(47, 15), (52, 19), (54, 26)], fill=METAL[2], width=2)
            d.rectangle((13, 49, 16, 51), fill=METAL[2])
        else:
            d.rectangle((26, 25, 36, 34), fill=METAL[0]);d.rectangle((28, 26, 34, 32), fill='#45525e')
            d.line((28, 26, 33, 26), fill=METAL[4]);d.line((30, 29, 32, 29), fill=GOLD[3])
    else:
        d.line([(19, 19), (44, 25), (30, 46), (19, 19)], fill=METAL[0], width=3)
        d.line([(19, 19), (44, 25), (30, 46), (19, 19)], fill=CYAN[1])
        for x, y in [(19, 19), (44, 25), (30, 46)]:bot(im, x, y, .85, coated=coated, active=True)
        for x, y in [(31, 21), (38, 35), (24, 33)]:d.rectangle((x, y, x + 1, y + 1), fill=CYAN[3])
    return im


def nano_scrap():
    im, d = canvas()
    surface(im, [(8, 22), (31, 11), (42, 19), (37, 25), (42, 30), (31, 41), (10, 32)], METAL, 2, 4)
    d.polygon([(12, 23), (31, 15), (37, 20), (31, 24), (35, 30), (29, 35), (14, 29)], fill='#3c5b58')
    for points in [[(17, 23), (23, 20), (26, 22), (33, 18)], [(16, 27), (24, 29), (29, 26), (33, 29)]]:d.line(points, fill=GOLD[3])
    d.polygon([(23, 22), (29, 20), (33, 24), (28, 29), (24, 27)], fill=METAL[0]);d.line((25, 23, 29, 22), fill=METAL[3])
    bot(im, 43, 42, .74, dead=True)
    d.line([(12, 40), (18, 37), (24, 41), (22, 46), (30, 49)], fill=GOLD[1], width=3)
    d.line([(12, 39), (18, 36), (24, 40)], fill=GOLD[3])
    d.polygon([(9, 49), (16, 45), (19, 48), (16, 55)], fill=METAL[2]);d.line((10, 49, 15, 46), fill=METAL[4])
    bolt(d, 31, 52);d.rectangle((50, 53, 54, 55), fill=GOLD[2])
    return im


def mold():
    im, d = canvas()
    surface(im, [(5, 29), (30, 12), (58, 26), (58, 43), (32, 57), (5, 43)], METAL, 1, 6)
    surface(im, [(5, 27), (30, 11), (58, 25), (32, 44)], METAL, 3, 12)
    d.polygon([(14, 27), (31, 17), (48, 26), (32, 37)], fill=METAL[0])
    d.polygon([(16, 27), (31, 19), (45, 26), (32, 34)], fill='#57525a')
    d.polygon([(19, 28), (32, 21), (42, 26), (31, 32)], fill='#34333c')
    d.line([(15, 27), (31, 17), (47, 25)], fill=GOLD[1], width=2)
    d.line([(16, 26), (31, 18), (43, 24)], fill=GOLD[3])
    d.line([(7, 28), (32, 44), (56, 27)], fill=METAL[5])
    d.line([(10, 39), (30, 51), (30, 46)], fill=METAL[3])
    d.line((36, 47, 52, 37), fill=METAL[2])
    for x, y in [(9, 28), (29, 13), (49, 25), (30, 39)]:bolt(d, x, y)
    return im


def soulium(residue=False, stable=False):
    im, d = canvas()
    p = ['#30323b', '#505562', '#7c8794', '#a8b7bf', '#d7e0df', '#f0eee0']
    if stable:
        surface(im, [(6, 32), (38, 14), (58, 26), (58, 37), (27, 55), (6, 43)], p, 2, 8)
        d.polygon([(6, 31), (38, 13), (58, 25), (27, 44)], fill=p[3])
        d.polygon([(11, 30), (38, 15), (52, 24), (25, 40)], fill=p[4])
        d.polygon([(14, 31), (39, 17), (44, 20), (18, 34)], fill=p[5])
        d.line([(8, 32), (27, 44), (56, 27)], fill=p[5])
        d.line([(8, 39), (26, 50), (26, 53)], fill=p[1])
        for pts in [[(30, 21), (35, 23), (41, 20)], [(29, 34), (38, 29)], [(34, 39), (49, 30)], [(34, 47), (50, 38)]]:d.line(pts, fill=p[2])
        d.polygon([(8, 32), (12, 29), (17, 32), (14, 35), (14, 45), (10, 46), (8, 43)], fill=GOLD[1])
        d.line([(9, 32), (12, 30), (15, 32)], fill=GOLD[4])
        d.polygon([(45, 18), (49, 20), (49, 23), (53, 25), (53, 37), (49, 39), (49, 28), (45, 26)], fill=GOLD[2])
        d.line([(46, 19), (48, 21), (48, 24), (52, 26)], fill=GOLD[4])
        d.line([(26, 26), (30, 23), (34, 26), (30, 29), (26, 26)], fill=CYAN[1]);d.line((28, 26, 30, 25), fill=CYAN[3])
    elif residue:
        for i, a in enumerate([(12, 28, 21, 22), (27, 18, 19, 24), (28, 35, 26, 19), (6, 43, 16, 10)]):ore(im, *a, p, i + 13)
        d.line([(17, 35), (22, 39), (29, 35), (36, 38)], fill=PURPLE[1], width=2)
        d.line([(40, 41), (44, 45), (41, 49)], fill=PURPLE[2])
        d.rectangle((23, 52, 27, 56), fill=p[2]);d.line((24, 52, 27, 52), fill=p[4])
    else:
        for i, a in enumerate([(9, 27, 27, 22), (28, 13, 22, 25), (28, 34, 28, 20)]):ore(im, *a, p, i + 3)
        d.line([(29, 22), (33, 29), (29, 33), (32, 39)], fill=PURPLE[1], width=2)
        d.line([(14, 37), (22, 41), (26, 39)], fill=p[1])
        d.line((39, 43, 47, 40), fill=PURPLE[2])
    return im


def substrate():
    im, d = canvas()
    surface(im, [(7, 26), (37, 8), (57, 22), (57, 37), (27, 56), (7, 42)], METAL, 1, 10)
    surface(im, [(7, 25), (37, 8), (57, 22), (27, 43)], METAL, 4, 4)
    d.polygon([(14, 25), (37, 12), (49, 22), (27, 37)], fill='#425562')
    for x, y in [(19, 24), (30, 18), (29, 29), (40, 23)]:
        d.polygon([(x, y), (x + 5, y - 3), (x + 9, y), (x + 4, y + 4)], fill=METAL[0])
        d.line([(x + 1, y), (x + 5, y - 2), (x + 7, y)], fill=METAL[3])
    for pts in [[(12, 25), (18, 29), (27, 24)], [(23, 16), (28, 20), (35, 16)], [(29, 35), (38, 30), (44, 34)], [(44, 17), (48, 20), (43, 24)]]:d.line(pts, fill=GOLD[3])
    for i in range(5):
        x, y = 14 + 4 * i, 34 + 3 * i
        d.line((x, y, x, y + 6), fill=GOLD[2], width=2);d.point((x, y), fill=GOLD[4])
    d.line([(9, 25), (36, 9), (53, 20)], fill=METAL[5])
    bolt(d, 9, 26);bolt(d, 35, 10);bolt(d, 50, 22)
    return im


def capsule_parts():
    im, d = canvas()
    surface(im, [(7, 20), (17, 13), (28, 19), (28, 27), (18, 35), (7, 28)], METAL, 2, 9)
    d.polygon([(8, 20), (17, 14), (27, 19), (18, 26)], fill=METAL[4])
    d.polygon([(13, 20), (18, 17), (23, 20), (18, 23)], fill=METAL[0])
    d.line([(10, 22), (18, 28), (25, 23)], fill=GOLD[2], width=2)
    surface(im, [(33, 37), (44, 29), (57, 36), (57, 45), (46, 53), (33, 46)], METAL, 2, 4)
    d.polygon([(34, 37), (44, 30), (56, 36), (46, 44)], fill=GOLD[3])
    d.polygon([(39, 37), (45, 33), (51, 36), (45, 40)], fill=METAL[0])
    d.line([(33, 44), (46, 51), (55, 44)], fill=METAL[3])
    for x, y in [(15, 42), (23, 39)]:
        d.polygon([(x, y), (x + 3, y - 2), (x + 15, y + 7), (x + 12, y + 10)], fill=METAL[1])
        d.line((x, y, x + 12, y + 9), fill=METAL[4], width=2)
    bolt(d, 8, 25);bolt(d, 50, 44)
    return im


def rod_base(mode='dense'):
    im, d = canvas()
    dense = mode in ('dense', 'depleted', 'broken_dense')
    p = GOLD if dense else METAL
    # 燃料组件沿对角线布置，封环和纵向夹轨分别绘制。
    surface(im, [(10, 42), (39, 9), (52, 21), (24, 55), (13, 53)], METAL, 1, 3)
    d.polygon([(16, 41), (40, 15), (47, 22), (24, 49)], fill='#3d2e4d' if mode != 'depleted' else '#3d3a48')
    core = ['#62536b', '#85738e', '#b1a1b7'] if mode == 'depleted' else [PURPLE[2], PURPLE[4], PURPLE[5]]
    for i in range(3):
        d.line((20 + i * 3, 42 + i * 2, 39 + i * 3, 19 + i * 2), fill=core[i % 2], width=2)
    d.line((21, 40, 35, 24), fill=core[2]);d.line((28, 42, 42, 26), fill=core[1])
    d.line((14, 42, 40, 12), fill=METAL[4], width=2)
    d.line((26, 52, 51, 22), fill=METAL[2], width=2)
    for x, y in [(10, 42), (34, 14)]:
        d.polygon([(x, y), (x + 6, y - 6), (x + 18, y + 5), (x + 13, y + 12)], fill=p[0])
        d.polygon([(x + 1, y), (x + 6, y - 4), (x + 16, y + 5), (x + 12, y + 9)], fill=p[2])
        d.line([(x + 2, y), (x + 6, y - 3), (x + 15, y + 5)], fill=p[-1])
        d.line((x + 3, y + 4, x + 11, y + 10), fill=p[1], width=2)
    if dense:
        d.polygon([(22, 29), (25, 26), (38, 38), (35, 41)], fill=GOLD[1])
        d.line((24, 28, 36, 39), fill=GOLD[3], width=2)
        d.line((26, 28, 37, 38), fill=GOLD[4])
    if mode == 'depleted':
        for x, y in [(17, 46), (39, 19), (34, 38)]:d.rectangle((x, y, x + 2, y + 2), fill='#74513c')
        d.line((24, 35, 29, 29), fill='#a5a5a5')
    if mode == 'rejected':
        d.line([(35, 19), (31, 26), (33, 31), (28, 38), (29, 44)], fill=METAL[0], width=2)
        d.polygon([(29, 33), (35, 29), (42, 36), (36, 43), (29, 37)], fill='#8e3c3d')
        d.line((32, 34, 37, 38), fill='#ead6b5', width=2);d.line((36, 33, 33, 39), fill='#ead6b5')
    return im


def broken(dense=False):
    src = rod_base('dense' if dense else 'normal')
    im, d = canvas()
    a = Image.new('RGBA', (64, 64));a.paste(src, (0, 0))
    p = a.load()
    for y in range(64):
        for x in range(64):
            if y > 30:p[x, y] = (0, 0, 0, 0)
    im.alpha_composite(a, (4, -2))
    a = src.copy();p = a.load()
    for y in range(64):
        for x in range(64):
            if y < 35:p[x, y] = (0, 0, 0, 0)
    im.alpha_composite(a, (-3, 1))
    d = ImageDraw.Draw(im)
    for pts in [[(32, 29), (30, 33), (33, 36)], [(37, 28), (37, 32), (34, 33)], [(24, 36), (26, 32), (29, 31)]]:
        d.line(pts, fill=GOLD[3] if dense else METAL[3])
    for x, y in [(40, 33), (42, 38), (35, 43)]:
        d.rectangle((x, y, x + 2, y + 2), fill=PURPLE[2]);d.point((x, y), fill=PURPLE[4])
    return im


def casing_scrap():
    im, d = canvas()
    surface(im, [(7, 25), (25, 15), (35, 19), (29, 25), (15, 32), (18, 39), (12, 43), (7, 35)], METAL, 3, 9)
    d.line([(8, 26), (25, 16), (31, 18)], fill=METAL[5])
    d.line([(13, 33), (15, 39), (12, 42)], fill=METAL[1], width=2)
    surface(im, [(26, 41), (43, 26), (54, 31), (57, 40), (49, 47), (45, 41), (33, 53), (24, 50)], METAL, 2, 13)
    d.line([(27, 42), (43, 28), (52, 32), (53, 38)], fill=METAL[5])
    d.line([(33, 45), (43, 36), (47, 38)], fill=METAL[1], width=2)
    d.polygon([(12, 50), (18, 44), (24, 48), (23, 54), (18, 57)], fill=GOLD[1])
    d.line([(13, 50), (18, 46), (22, 49)], fill=GOLD[3]);bolt(d, 45, 15)
    return im


def energy_crystal():
    im, d = canvas()
    crystal(im, 39, 23, 15, 31, 4)
    crystal(im, 9, 30, 20, 26, 5)
    crystal(im, 23, 5, 24, 51, 6)
    crystal(im, 29, 36, 15, 23, 7)
    d.line([(29, 12), (27, 16), (27, 27)], fill='#f9d1ef')
    d.line([(36, 44), (39, 40), (41, 40)], fill=PURPLE[5])
    glint(d, 29, 17);d.rectangle((17, 43, 18, 45), fill=PURPLE[5])
    return im


def codex():
    im, d = canvas()
    d.polygon([(15, 10), (46, 10), (49, 14), (47, 22), (47, 47), (44, 52), (16, 52), (13, 48), (15, 40)], fill='#554a3a')
    surface(im, [(17, 13), (43, 13), (45, 17), (43, 25), (44, 44), (41, 48), (17, 48), (18, 38)], ['#77654b', '#a58c5c', '#c5ad74', '#dac88f', '#eddeb0'], 3, 24)
    d.line((19, 15, 40, 15), fill='#f1e5b7');d.line((43, 28, 43, 43), fill='#9e8556')
    for y in (23, 27, 31, 39):
        d.line((22, y, 37 if y != 31 else 30, y), fill='#8d805f')
    d.line([(22, 35), (25, 34), (28, 37), (31, 34), (36, 35)], fill='#647d7b')
    d.line([(24, 20), (27, 19), (30, 21), (33, 19), (38, 20)], fill='#846d4f')
    for y in (9, 46):
        d.rectangle((12, y, 48, y + 7), fill=METAL[0])
        d.rectangle((15, y + 1, 46, y + 5), fill=GOLD[2])
        d.line((16, y + 1, 45, y + 1), fill=GOLD[4])
        d.line((16, y + 5, 45, y + 5), fill=GOLD[1])
        for x in (12, 45):
            d.rectangle((x, y - 1, x + 4, y + 8), fill=METAL[1]);d.line((x, y - 1, x + 3, y - 1), fill=METAL[4])
    d.polygon([(34, 40), (40, 40), (40, 59), (37, 56), (34, 59)], fill='#70334b')
    d.polygon([(33, 36), (37, 33), (42, 36), (42, 41), (37, 44), (33, 41)], fill=GOLD[1])
    d.polygon([(34, 37), (37, 35), (40, 37), (40, 40), (37, 42), (34, 40)], fill=PURPLE[2])
    d.line([(37, 36), (36, 38), (38, 40)], fill=PURPLE[5])
    return im


IMAGES = {
    'analyzed_honkai_sample': analyzed(),
    'honkai_reference_sample': reference(),
    'honkai_crystal_seed': seed(),
    'directional_crystallization_matrix': matrix(),
    'concentrated_honkai_impurity': impurity(),
    'separation_residue': dust('ash'),
    'fuel_matrix': fuel_matrix(),
    'fuel_blending_residue': dust('blend'),
    'soulium_microstructure_template': template(),
    'unprogrammed_nanobot': nano(single=True),
    'controlled_nano_swarm': nano(),
    'inactive_nano_unit': nano(single=True, dead=True),
    'coated_nano_swarm': nano(coated=True),
    'nano_assembly_scrap': nano_scrap(),
    'soulium_casting_mold': mold(),
    'soulium_polymerization_residue': soulium(residue=True),
    'soulium_data_substrate': substrate(),
    'fuel_encapsulation_part': capsule_parts(),
    'rejected_fuel_rod': rod_base('rejected'),
    'depleted_dense_honkai_fuel_rod': rod_base('depleted'),
    'broken_honkai_fuel_rod': broken(),
    'broken_dense_honkai_fuel_rod': broken(dense=True),
    'recovered_fuel_casing_material': casing_scrap(),
    'inactive_fuel_residue': dust('inactive'),
    'honkai_energy_crystal': energy_crystal(),
    'dense_honkai_fuel_rod': rod_base(),
    'soulium_proto_mass': soulium(),
    'stabilized_soulium_proto_mass': soulium(stable=True),
    'narrative_codex': codex(),
}

def draw(ident):
    return IMAGES[ident]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / 'logs/item-texture-refresh-20261112/process-manifest.json').read_text(encoding='utf-8'))
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
    sheet = Image.new('RGB', (1000, 6 * 184), '#242931')
    d = ImageDraw.Draw(sheet)
    report = []
    for i, entry in enumerate(manifest):
        name = entry['id']
        im = draw(name)
        im.save(ASSETS / (name + '.png'))
        im.save(OUT / (name + '.png'))
        x, y = (i % 5) * 200, (i // 5) * 184
        d.rectangle((x + 4, y + 4, x + 195, y + 179), fill='#303741')
        enlarged = im.resize((128, 128), Image.Resampling.NEAREST)
        sheet.paste(enlarged, (x + 36, y + 8), enlarged)
        d.text((x + 9, y + 142), f'{i + 1:02}  {entry["name"]}', font=font, fill='#e8e5d8')
        report.append({'id': name, 'name': entry['name'], 'size': [64, 64], 'sha256': hashlib.sha256((ASSETS / (name + '.png')).read_bytes()).hexdigest()})
    sheet.save(OUT / 'process-contact-sheet.png')
    (OUT / 'process-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'已重绘 {len(report)} 张；预览 {OUT / "process-contact-sheet.png"}')


if __name__ == '__main__':
    main()
