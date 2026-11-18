from pathlib import Path
import json
import random

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0002贴图材质_审定重绘_R4_20261114'
IDS = [
    'directional_crystallization_matrix', 'concentrated_honkai_impurity',
    'separation_residue', 'soulium_microstructure_template',
    'unprogrammed_nanobot', 'controlled_nano_swarm', 'inactive_nano_unit',
    'coated_nano_swarm', 'nano_assembly_scrap', 'soulium_casting_mold',
    'soulium_polymerization_residue', 'soulium_data_substrate',
    'honkai_energy_crystal', 'soulium_proto_mass', 'stabilized_soulium_proto_mass',
]
NAMES = [
    '定向结晶基质', '浓缩崩坏杂质', '分离残渣', '魂钢微结构模板',
    '未编程纳米机器人', '受控自组织纳米群', '失活纳米单元', '抗侵蚀涂层纳米群',
    '纳米装配废料', '魂钢聚合模具', '魂钢聚合残渣', '魂钢数据基板',
    '固态崩坏能结晶', '粗魂钢坯', '稳定魂钢坯',
]
INK = '#191b25'
STEEL = ['#343945', '#565d6a', '#7a8491', '#aab4bd', '#d6dde0', '#f0f1e8']
VIOLET = ['#30213f', '#503059', '#754383', '#a568b3', '#d9a2dd', '#f0d5ed']
GOLD = ['#675034', '#9e7844', '#d1ac64', '#ead79a']


def polygon(d, points, fill, outline=INK):
    d.polygon(points, fill=fill, outline=outline)


def bolt(d, x, y, bright=True):
    d.rectangle((x, y, x + 3, y + 3), fill=INK)
    d.rectangle((x, y, x + 2, y + 2), fill=STEEL[3 if bright else 1])
    d.point((x, y), fill=STEEL[5 if bright else 2])
    d.point((x + 1, y + 1), fill=STEEL[0])


def grain(im, points, colors, seed, count=60):
    mask = Image.new('1', im.size)
    ImageDraw.Draw(mask).polygon(points, fill=1)
    rng = random.Random(seed)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = mask.getbbox()
    for _ in range(count):
        x, y = rng.randrange(x0, x1), rng.randrange(y0, y1)
        if mask.getpixel((x, y)):
            d.point((x, y), fill=rng.choice(colors))


def rod(d, points, width=4, color=STEEL[2]):
    d.line(points, fill=INK, width=width + 2)
    d.line(points, fill=color, width=width)
    d.line([(x - 1, y - 1) for x, y in points], fill=STEEL[3], width=1)


def pod(d, x, y, armor=False):
    for sx, sy in [(-6, 1), (6, 1), (-4, 7), (4, 7)]:
        d.line((x + sx // 2, y + sy // 2, x + sx, y + sy), fill=INK, width=3)
        d.point((x + sx, y + sy - 1), fill=STEEL[3])
    polygon(d, [(x - 6, y - 3), (x - 2, y - 7), (x + 5, y - 6),
                (x + 8, y - 2), (x + 7, y + 5), (x + 1, y + 8),
                (x - 6, y + 5)], STEEL[1])
    polygon(d, [(x - 5, y - 3), (x - 1, y - 6), (x + 4, y - 5),
                (x + 6, y - 1), (x + 1, y + 2), (x - 5, y)], STEEL[3])
    d.line((x - 4, y + 2, x, y + 5, x + 5, y + 2), fill=STEEL[0], width=2)
    if armor:
        polygon(d, [(x - 5, y - 3), (x - 2, y - 6), (x + 2, y - 6),
                    (x + 1, y), (x - 4, y + 2)], '#e3e4d7')
        polygon(d, [(x + 3, y - 5), (x + 6, y - 2), (x + 6, y + 3),
                    (x + 2, y + 5), (x + 2, y)], '#bfc9c2')
        d.line((x - 4, y - 3, x - 2, y - 5, x, y - 5), fill='#ffffff')
        d.rectangle((x - 1, y, x + 1, y + 2), fill=VIOLET[3])
    else:
        d.rectangle((x - 2, y - 3, x + 2, y), fill=INK)
        d.line((x - 1, y - 2, x + 1, y - 2), fill=VIOLET[3])
        d.point((x + 4, y + 3), fill=GOLD[2])


def matrix(im, d):
    polygon(d, [(12, 48), (39, 42), (52, 49), (51, 55), (23, 60), (12, 55)], STEEL[0])
    polygon(d, [(12, 48), (39, 42), (52, 49), (23, 55)], STEEL[2])
    d.line((16, 49, 24, 52, 46, 48), fill=STEEL[4])
    rod(d, [(18, 47), (18, 17)], 4, STEEL[1])
    rod(d, [(47, 46), (47, 15)], 4, STEEL[0])
    for y in [12, 26, 40]:
        d.ellipse((12, y, 51, y + 16), outline=INK, width=5)
        d.arc((13, y + 1, 50, y + 15), 180, 360, fill=STEEL[3], width=3)
        d.arc((13, y + 1, 50, y + 15), 0, 180, fill=STEEL[1], width=3)
        d.arc((16, y + 3, 47, y + 12), 190, 330, fill='#bcb2cc', width=1)
    polygon(d, [(28, 12), (32, 7), (36, 11), (36, 42), (32, 49), (28, 45)], VIOLET[1])
    polygon(d, [(29, 13), (32, 9), (32, 44), (29, 42)], VIOLET[4])
    d.line((33, 13, 33, 43), fill=VIOLET[2], width=2)
    for y in [24, 38]:
        d.arc((13, y - 11, 50, y + 4), 9, 172, fill=INK, width=5)
        d.arc((13, y - 12, 50, y + 3), 10, 171, fill=STEEL[2], width=3)
        for x in [16, 20, 42, 46]:
            d.line((x, y - 1, x, y + 2), fill='#b7adca')
    rod(d, [(14, 48), (14, 19)], 3, STEEL[2])
    polygon(d, [(46, 19), (53, 17), (57, 21), (57, 28), (50, 31), (46, 27)], STEEL[0])
    polygon(d, [(48, 20), (53, 19), (55, 22), (50, 24)], STEEL[3])
    d.rectangle((50, 25, 53, 27), fill=VIOLET[3])
    bolt(d, 17, 49)
    bolt(d, 42, 48)


def impurity(im, d):
    shape = [(5, 42), (8, 29), (16, 25), (18, 16), (30, 10), (40, 14),
             (43, 23), (53, 26), (59, 40), (53, 51), (39, 57), (22, 55), (11, 50)]
    polygon(d, shape, '#37373e')
    polygon(d, [(9, 30), (19, 28), (21, 18), (30, 12), (34, 23), (28, 34), (13, 39)], '#68666b')
    polygon(d, [(30, 12), (39, 16), (41, 26), (52, 28), (46, 38), (28, 34), (34, 23)], '#514d59')
    polygon(d, [(13, 40), (28, 35), (39, 42), (34, 54), (23, 53), (12, 48)], '#4a4850')
    polygon(d, [(39, 41), (47, 36), (56, 39), (51, 49), (38, 54)], '#292b35')
    grain(im, shape, ['#44414a', '#79747a', '#282b31', '#5c565c'], 401, 155)
    for x, y in [(23, 21), (42, 29), (20, 42), (49, 43), (34, 48)]:
        polygon(d, [(x - 2, y), (x, y - 3), (x + 3, y - 2), (x + 2, y + 3)], VIOLET[0])
        d.line((x, y - 1, x + 1, y - 1), fill=VIOLET[3])
    for x, y in [(15, 34), (31, 30), (45, 35), (28, 45)]:
        d.rectangle((x, y, x + 2, y + 1), fill='#20222a')
        d.point((x, y + 2), fill='#6b656c')


def residue(im, d):
    pile = [(5, 45), (9, 38), (15, 37), (20, 29), (29, 27), (37, 32),
            (44, 30), (49, 38), (55, 40), (60, 48), (50, 54), (33, 56), (16, 53)]
    polygon(d, pile, '#625b53', '#333037')
    polygon(d, [(8, 44), (19, 39), (24, 31), (31, 30), (35, 37), (25, 43)], '#a49b88', '#817a6c')
    polygon(d, [(26, 44), (39, 36), (44, 33), (49, 42), (57, 47), (41, 50)], '#898272', '#6e665c')
    polygon(d, [(10, 47), (23, 45), (32, 50), (45, 51), (34, 54), (18, 51)], '#79705f', '#625b53')
    grain(im, pile, ['#b3aa96', '#514b46', '#948978', '#6d6558'], 402, 220)
    for x, y, c in [(4, 49, '#8b8172'), (11, 33, '#a49b88'), (51, 35, '#686057'),
                    (54, 55, '#938979'), (22, 57, '#5b554c'), (42, 26, '#a29885')]:
        d.rectangle((x, y, x + 1, y + 1), fill=c)
    d.line((19, 34, 22, 32), fill='#c1b6a0')


def template(im, d):
    polygon(d, [(9, 38), (30, 24), (46, 29), (26, 46), (13, 51), (7, 46)], STEEL[1])
    polygon(d, [(10, 37), (30, 23), (45, 27), (25, 44), (12, 49), (7, 44)], '#c4ccd0')
    polygon(d, [(12, 38), (30, 26), (40, 28), (24, 41), (12, 46), (10, 44)], '#e2e6de', '#9ba6b0')
    for x, y in [(15, 39), (22, 34), (29, 29)]:
        polygon(d, [(x, y), (x + 3, y - 2), (x + 6, y), (x + 3, y + 3)], '#343946', '#7f8c9b')
        d.line((x + 1, y, x + 3, y - 1, x + 5, y), fill='#1d2530')
    polygon(d, [(31, 14), (43, 9), (55, 15), (57, 31), (48, 39), (35, 34)], STEEL[1])
    d.ellipse((29, 10, 52, 36), fill='#a5b2bb', outline=INK, width=1)
    d.ellipse((31, 12, 50, 34), outline='#e7eae2', width=2)
    d.ellipse((34, 15, 48, 31), outline='#697781', width=2)
    d.ellipse((37, 18, 46, 28), fill='#343d48', outline='#d8dfdd', width=2)
    polygon(d, [(40, 20), (45, 18), (48, 21), (48, 25), (43, 28), (40, 25)], STEEL[2])
    d.line((43, 21, 46, 20, 47, 22), fill=STEEL[5])
    d.line((53, 17, 54, 28, 50, 34), fill=STEEL[0], width=2)
    d.line((14, 47, 26, 42, 33, 36), fill='#9a8caa')


def unprogrammed(im, d):
    for points in [[(25, 25), (20, 16), (13, 17), (12, 25)],
                   [(39, 25), (45, 16), (52, 20), (50, 29)]]:
        rod(d, points, 5, STEEL[2])
        bolt(d, points[1][0] - 1, points[1][1] - 1)
    polygon(d, [(19, 28), (26, 20), (38, 20), (46, 27), (43, 38),
                (32, 44), (21, 38)], STEEL[0])
    polygon(d, [(21, 27), (28, 22), (37, 22), (43, 27), (32, 34)], STEEL[4])
    polygon(d, [(21, 29), (31, 35), (31, 41), (23, 36)], STEEL[2])
    polygon(d, [(34, 35), (43, 29), (41, 36), (34, 40)], STEEL[1])
    polygon(d, [(27, 24), (33, 21), (38, 24), (32, 28)], '#20242e')
    d.line((29, 24, 33, 23, 35, 24), fill='#4c5360')
    for x, y in [(23, 28), (26, 30), (38, 29), (40, 27)]:
        d.rectangle((x, y, x + 1, y + 2), fill=GOLD[2])
    rod(d, [(23, 34), (13, 38), (10, 46), (15, 51)], 6, STEEL[2])
    rod(d, [(42, 34), (51, 38), (53, 46), (47, 52)], 6, STEEL[2])
    for x, y in [(13, 38), (50, 38)]:
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=STEEL[4], outline=INK)
        d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=STEEL[0])
    rod(d, [(15, 50), (22, 52), (27, 47)], 3, STEEL[3])
    rod(d, [(47, 51), (40, 54), (35, 49)], 3, STEEL[3])
    d.line((27, 34, 30, 36), fill=STEEL[5])


def swarm(im, d):
    centers = [(17, 44), (34, 45), (46, 32), (39, 17), (21, 18)]
    for a, b in zip(centers, centers[1:]):
        d.line((a, b), fill=INK, width=6)
        d.line((a, b), fill=GOLD[1], width=3)
        d.line((a, b), fill=GOLD[2], width=1)
    for x, y in reversed(centers):
        pod(d, x, y)
    d.line((10, 43, 7, 38, 11, 34), fill=STEEL[3], width=2)
    d.line((18, 12, 17, 8, 22, 7), fill=STEEL[2], width=2)


def inactive(im, d):
    rod(d, [(25, 25), (15, 28), (11, 42), (24, 49)], 6, STEEL[1])
    rod(d, [(39, 24), (49, 27), (53, 41), (41, 49)], 6, STEEL[0])
    polygon(d, [(23, 47), (20, 53), (30, 57), (41, 52), (40, 46)], STEEL[1])
    polygon(d, [(18, 24), (27, 17), (39, 18), (47, 26), (45, 39),
                (35, 47), (23, 43), (17, 34)], '#3c444e')
    polygon(d, [(19, 24), (28, 18), (38, 19), (45, 26), (38, 36),
                (26, 37), (19, 31)], '#879194')
    polygon(d, [(24, 26), (29, 22), (36, 22), (41, 27), (37, 32), (28, 33)], '#262d36')
    d.line((28, 26, 31, 24, 35, 24, 38, 27), fill='#535d66')
    d.line((26, 38, 28, 41, 35, 43, 40, 39), fill='#697780')
    polygon(d, [(17, 35), (23, 38), (22, 46), (18, 45), (14, 41)], '#5b686e')
    polygon(d, [(42, 36), (48, 33), (50, 40), (45, 45), (41, 44)], '#45535f')
    d.line((19, 37, 19, 42, 21, 43), fill='#a5b2b2')
    d.line((44, 38, 46, 37, 47, 40), fill='#78868c')
    bolt(d, 13, 31, False)
    bolt(d, 47, 29, False)


def coated(im, d):
    for a, b in [((19, 39), (27, 25)), ((27, 25), (42, 24)), ((42, 24), (45, 40))]:
        rod(d, [a, b], 5, '#9faea9')
        d.line((a, b), fill='#dbe2d3', width=2)
    for x, y in [(27, 25), (42, 24), (19, 39), (45, 40)]:
        pod(d, x, y, True)
    polygon(d, [(14, 38), (9, 34), (9, 28), (13, 26), (13, 32), (17, 34)], '#c9d5cc')
    polygon(d, [(48, 42), (54, 43), (57, 49), (53, 54), (52, 47), (47, 46)], '#b0c0b7')
    polygon(d, [(16, 45), (14, 52), (20, 57), (26, 53), (24, 48)], '#d2dccf')
    d.line((16, 51, 20, 55, 23, 53), fill='#ffffff')


def scrap(im, d):
    polygon(d, [(7, 47), (14, 35), (24, 34), (36, 37), (50, 35), (58, 46),
                (52, 53), (35, 57), (17, 54)], '#333840')
    polygon(d, [(11, 42), (16, 29), (23, 27), (28, 33), (24, 47), (17, 49)], STEEL[2])
    polygon(d, [(14, 40), (18, 31), (22, 30), (24, 34), (20, 42)], '#272c36')
    rod(d, [(24, 45), (31, 28), (39, 23), (43, 28)], 3, STEEL[3])
    rod(d, [(29, 48), (42, 44), (46, 32), (51, 35)], 4, STEEL[1])
    polygon(d, [(17, 46), (22, 40), (30, 41), (35, 48), (30, 55), (21, 55)], GOLD[1])
    d.arc((19, 42, 32, 55), 180, 520, fill=GOLD[3], width=2)
    d.arc((22, 45, 29, 52), 0, 320, fill=GOLD[0], width=2)
    polygon(d, [(38, 45), (48, 40), (55, 44), (48, 49), (39, 50)], '#aeb8b9')
    d.line((41, 46, 48, 43, 51, 44), fill=STEEL[5])
    for x, y in [(10, 51), (35, 52), (47, 53), (54, 49), (31, 36)]:
        d.rectangle((x, y, x + 2, y + 2), fill=STEEL[0])
        d.point((x, y), fill=STEEL[4])
    d.line((38, 32, 34, 36, 37, 41), fill=GOLD[2], width=2)


def mold(im, d):
    polygon(d, [(4, 31), (11, 26), (19, 29), (19, 39), (11, 43), (4, 39)], STEEL[1])
    polygon(d, [(47, 27), (55, 25), (61, 29), (61, 38), (53, 42), (47, 37)], STEEL[0])
    d.ellipse((9, 16, 55, 54), fill=INK)
    d.rectangle((9, 28, 55, 37), fill=INK)
    d.ellipse((10, 24, 54, 52), fill=STEEL[0])
    d.ellipse((10, 15, 54, 43), fill=STEEL[2], outline=INK)
    d.arc((11, 16, 53, 42), 180, 335, fill=STEEL[4], width=2)
    d.ellipse((18, 20, 47, 38), fill=STEEL[5], outline=STEEL[0], width=2)
    d.ellipse((22, 23, 44, 36), fill='#21232d', outline='#87939e', width=2)
    d.arc((23, 25, 43, 36), 8, 167, fill='#686171', width=2)
    d.line((12, 32, 20, 31), fill=INK, width=2)
    d.line((45, 31, 54, 33), fill=INK, width=2)
    d.line((32, 16, 32, 20), fill=INK, width=2)
    for x, y in [(14, 24), (46, 22), (30, 36), (7, 33), (55, 31)]:
        bolt(d, x, y)
    d.line((14, 43, 22, 47), fill=STEEL[1], width=2)
    d.line((44, 44, 50, 40), fill='#222733', width=3)


def polymer_residue(im, d):
    shape = [(7, 44), (10, 36), (17, 34), (18, 25), (27, 23), (33, 29),
             (39, 24), (47, 28), (49, 37), (56, 41), (57, 48), (49, 54), (34, 57), (18, 53)]
    polygon(d, shape, '#777e83')
    polygon(d, [(11, 36), (19, 36), (21, 27), (27, 25), (32, 32), (28, 42), (15, 44)], '#c2c7c4')
    polygon(d, [(30, 33), (40, 27), (46, 30), (45, 40), (53, 43), (46, 50), (34, 46)], '#a5afae')
    polygon(d, [(16, 46), (29, 40), (35, 48), (47, 51), (34, 55), (21, 51)], '#929ba0')
    grain(im, shape, ['#e0e0d5', '#afb7b6', '#5b636e', '#87909a', '#c4c2c9'], 411, 190)
    for x, y in [(16, 40), (24, 32), (39, 34), (31, 46), (45, 44)]:
        d.line((x - 3, y + 2, x - 1, y - 2, x + 3, y - 1), fill='#d6dbd4')
        d.line((x - 1, y + 3, x + 3, y + 1), fill='#555d69')
    d.line((33, 36, 36, 34, 39, 35), fill='#a28da7')
    d.point((43, 49), fill='#ae8cb4')


def substrate(im, d):
    d.ellipse((6, 20, 57, 55), fill=INK)
    d.rectangle((6, 30, 57, 36), fill=INK)
    d.ellipse((7, 18, 56, 49), fill='#555767')
    d.ellipse((7, 14, 56, 46), fill='#b6c2c6', outline=INK)
    d.arc((8, 15, 55, 45), 182, 334, fill='#edf0e8', width=2)
    d.arc((10, 17, 53, 43), 180, 350, fill='#808d99')
    d.line((15, 27, 24, 21, 36, 21, 42, 25, 49, 25), fill='#6a7c88')
    d.line((12, 33, 22, 33, 28, 28, 43, 28, 50, 32), fill=GOLD[1])
    d.line((19, 38, 28, 38, 35, 32, 43, 32), fill='#6a7c88')
    d.line((28, 18, 28, 23, 20, 29, 20, 32), fill='#e4dfcb')
    d.line((36, 25, 36, 28, 29, 34, 29, 37), fill='#dedace')
    d.line((39, 38, 45, 35, 50, 36), fill='#dedace')
    for x, y in [(15, 26), (24, 20), (42, 24), (43, 31), (19, 37), (48, 35)]:
        d.rectangle((x, y, x + 2, y + 1), fill=GOLD[2])
        d.point((x, y), fill=GOLD[3])
    polygon(d, [(48, 17), (54, 21), (51, 24), (47, 21)], '#1f2530')
    for x in range(17, 47, 5):
        d.line((x, 45 if x < 25 else 47, x + 1, 49 if x < 25 else 51), fill='#93849f')


def crystal(im, d):
    polygon(d, [(9, 34), (13, 19), (22, 24), (30, 46), (21, 55), (11, 47)], VIOLET[1])
    polygon(d, [(13, 21), (18, 27), (21, 49), (12, 44)], VIOLET[3])
    d.line((14, 23, 16, 30, 18, 42), fill=VIOLET[5], width=2)
    polygon(d, [(35, 34), (47, 13), (54, 26), (49, 48), (39, 55), (31, 47)], VIOLET[0])
    polygon(d, [(47, 15), (48, 29), (38, 51), (36, 42)], VIOLET[3])
    polygon(d, [(48, 29), (52, 26), (47, 46), (40, 52)], VIOLET[2])
    d.line((47, 17, 45, 26, 40, 37), fill=VIOLET[4])
    polygon(d, [(23, 19), (30, 5), (39, 19), (40, 43), (29, 58), (20, 45)], VIOLET[1])
    polygon(d, [(24, 20), (30, 7), (30, 40), (23, 50), (22, 43)], '#d18eda')
    polygon(d, [(31, 9), (37, 20), (38, 42), (31, 53), (31, 39)], '#9251a5')
    polygon(d, [(25, 22), (29, 12), (28, 32), (25, 39)], '#efc5e8', '#efc5e8')
    d.line((32, 42, 36, 35, 36, 22), fill='#b778c4')
    polygon(d, [(26, 48), (34, 44), (43, 49), (40, 56), (29, 59), (22, 55)], VIOLET[1])
    polygon(d, [(28, 48), (34, 46), (38, 49), (30, 54), (25, 53)], VIOLET[3])


def proto(im, d):
    shape = [(7, 35), (11, 25), (23, 20), (29, 12), (43, 13), (48, 21),
             (56, 26), (59, 39), (53, 49), (41, 55), (25, 53), (14, 48)]
    polygon(d, shape, '#4d535f')
    polygon(d, [(11, 26), (25, 23), (30, 15), (41, 16), (46, 23), (37, 31), (18, 35)], '#b2b7b9')
    polygon(d, [(18, 36), (37, 31), (48, 24), (54, 28), (53, 41), (39, 48), (25, 46)], '#858897')
    polygon(d, [(39, 48), (53, 41), (57, 36), (52, 47), (41, 53), (26, 51)], '#343a48')
    grain(im, shape, ['#c5c9c4', '#686a79', '#393f4c', '#92939e', '#7f748c'], 414, 130)
    for x, y in [(19, 29), (33, 23), (45, 31), (28, 40), (43, 43)]:
        d.line((x - 3, y, x - 1, y - 2, x + 2, y - 1), fill='#454854', width=2)
        d.line((x - 2, y + 2, x + 2, y + 1), fill='#b3b7b9')
    d.line((13, 37, 17, 39, 17, 43), fill='#b5b8b6')
    d.line((33, 15, 38, 17, 43, 17), fill='#dcddd1')


def stabilized(im, d):
    polygon(d, [(9, 34), (28, 18), (35, 11), (47, 11), (55, 19),
                (55, 31), (48, 39), (29, 55), (17, 55), (9, 47)], '#69717f')
    polygon(d, [(9, 34), (28, 18), (35, 11), (47, 11), (28, 27), (17, 27)], '#d0d5d3')
    polygon(d, [(28, 27), (47, 11), (55, 19), (36, 35)], '#a4adb5')
    polygon(d, [(36, 35), (55, 19), (55, 31), (36, 47)], '#626c7b')
    polygon(d, [(36, 47), (55, 31), (48, 39), (29, 55)], '#404954')
    polygon(d, [(9, 35), (17, 27), (28, 27), (36, 35), (36, 47),
                (28, 55), (17, 55), (9, 47)], '#a9b1b7')
    polygon(d, [(12, 36), (18, 30), (27, 30), (33, 36), (33, 46),
                (27, 52), (18, 52), (12, 46)], '#c8cdcc', '#858c9a')
    d.line((14, 37, 19, 32, 26, 32, 31, 37), fill='#ebede4')
    d.line((15, 41, 28, 41), fill='#b4b9bf')
    d.line((17, 45, 27, 45), fill='#daddd7')
    d.line((19, 50, 26, 50, 31, 45), fill='#9894a6')
    for coords, color in [((20, 25, 36, 12), '#f0f0e5'), ((27, 25, 42, 13), '#b0b4bd'),
                          ((34, 31, 49, 18), '#d1d5d4'), ((38, 35, 52, 23), '#7e8294'),
                          ((38, 43, 52, 31), '#9195a5')]:
        d.line(coords, fill=color)


ART = [matrix, impurity, residue, template, unprogrammed, swarm, inactive,
       coated, scrap, mold, polymer_residue, substrate, crystal, proto, stabilized]


def draw(ident):
    im = Image.new('RGBA', (64, 64))
    ART[IDS.index(ident)](im, ImageDraw.Draw(im))
    return im


PROCESS = 'src/main/resources/data/hk3gtl/research/industrial_processes.json'
MATERIAL = 'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/HonkaiMaterialRecipes.java'
LIQUID = 'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/Hk3LiquidLineRecipes.java'
DESIGNS = [
    ([MATERIAL, PROCESS], 'industrial_directional_crystallization_matrix；industrial_crystal_growth',
     '由MAX场发生器、传感器、钨钢板、铌钛细线及MAX电路制成；I08晶种培育消耗定向结晶基质。',
     '重新设计成带三层金属约束绕组、中心导向轴和侧置感测头的立体夹具；钨钢承力、浅铌钛色绕组与少量结晶紫属于美术材料解释。'),
    ([PROCESS, LIQUID], 'industrial_solid_collection；industrial_crystal_growth；industrial_liquid_fractionation',
     '固态采集、晶种培育和液态分馏均产生浓缩崩坏杂质；液态提纯与稳定过程也使用此物。',
     '致密多孔的暗色烧结团块，表面仅埋藏零星紫色夹杂；强调杂质凝聚体，避免画成可用的完整晶体。'),
    ([PROCESS, LIQUID], 'industrial_recovery_nano_scrap；industrial_liquid_fractionation',
     '纳米废料回收及多种其他回收、液态工艺产生分离残渣。',
     '低矮松散的灰褐细粉堆，颗粒、团聚层次与散落粉点体现分离副产物；粉末颜色和粒径为美术推导。'),
    ([PROCESS], 'industrial_soulium_template；industrial_soulium_precursor',
     '铂箔4、钨钢板2、晶种2制成微结构模板2；I09消耗模板1并返还模板1。',
     '以可复用的铂色精密镂空带卷和刚性芯轴表现模板，不使用通用电路板轮廓；卷绕与镂空形式属于拟定外观。'),
    ([PROCESS], 'industrial_nano_assembly；industrial_nano_control',
     '纳米构筑单元8、金箔4、适配电路基板1和焊料144产出机器人4、废料2；机器人随后进入控制工序。',
     '带粗壮关节、前端夹持器与金色触点的微装配机器人；顶部留暗色编程接口，区别已受控状态，不把外观接口当代码字段。'),
    ([PROCESS], 'industrial_nano_control',
     '未编程机器人4、重构规则载体1、工艺溶剂250产出受控自组织纳米群3、失活单元1及废溶剂。',
     '五个可辨金属单元借实体接触链弯曲成群，灰钢壳、金色连接件和少量紫色指示细节体现完成控制后的协同。'),
    ([PROCESS], 'industrial_nano_building；industrial_nano_control；industrial_nano_coating',
     '纳米构筑、控制与涂层工序均可产生失活纳米单元；配方未规定其必须破碎。',
     '收拢执行器、关闭工作光源的完整停用单元，低饱和灰钢与暗色中心表现失活，不添加破裂或报废叉号。'),
    ([PROCESS], 'industrial_nano_coating；industrial_soulium_polymerization',
     '受控纳米群3与抗侵蚀涂层250产出涂层纳米群2；I14再以其参与粗魂钢坯聚合。',
     '四只实体单元组成紧凑群，新增分瓣浅色防护壳与厚涂覆接头，轮廓区别于开放连接链；涂层颜色是美术选择。'),
    ([PROCESS], 'industrial_nano_assembly；industrial_recovery_nano_scrap',
     'I11装配过程产出纳米装配废料；废料8、滤芯1及分析试剂500可回收构筑单元2并产生残渣。',
     '塌折金属支架、卷曲金箔、废壳片及焊料珠构成实体废件堆，明确属于装配废料而非粉尘或失活整机。'),
    ([PROCESS], 'industrial_soulium_casting_mold',
     '钨钢板8、铂箔4及焊料288制成魂钢聚合模具1；当前工艺表只确认此合成产出，不宣称I14实际消耗模具。',
     '厚壁分瓣环模、两侧安装耳和铂色内腔表现工业模具，保留钨钢外壳的重体量；形状为美术推导。'),
    ([PROCESS], 'industrial_soulium_precursor',
     'I09由模板、钛粉、铂粉、稳定崩坏液及工艺溶剂制备魂钢前驱液时，同时产出魂钢聚合残渣1。',
     '灰银色沉积粉团与金属絮片，附极少淡紫沉积色；按I09液相制备副产物理解，不画成I14成型废块。'),
    ([PROCESS], 'industrial_soulium_data_substrate',
     'I16以魂钢板2、魂钢细线4、焊料144和冷却剂125制成魂钢数据基板1并产生热冷却剂。',
     '有明显厚度的银灰晶圆形基板，表面细线与金色焊盘呈现布线基材；未装成品芯片，圆片形制属于美术选择。'),
    ([LIQUID], 'industrial_liquid_stabilization',
     '粗崩坏能、稳定介质、冷却剂、铂箔、晶种、定向基质及浓缩杂质参与稳定工序，产出固态崩坏能结晶64等。',
     '不对称互生紫色晶簇，清晰硬边晶面、深色根部与左上高光；紫色表达崩坏能身份，晶簇形状为拟定外观。'),
    ([PROCESS], 'industrial_soulium_polymerization；industrial_soulium_reconstruction',
     'I14以涂层纳米群2、钨钢粉16、魂钢前驱液500产出粗魂钢坯8；随后进入I15重构。',
     '带皱皮、孔隙和毛边的冷灰金属聚合团坯，明确尚未定形，不做成精加工零件。'),
    ([PROCESS], 'industrial_soulium_reconstruction',
     'I15以粗魂钢坯8、重构规则载体1和稳定介质200产出稳定魂钢坯4及加工屑；之后仍有后续定向组件阶段。',
     '规则八角截面的短金属柱坯，均匀银灰与细微淡紫纵向金属纹体现致密化；仍保留原料坯身份，不绘成最终定向组件。'),
]


def main():
    target = ROOT / 'src/main/resources/assets/hk3gtl/textures/item'
    copies = OUT / 'textures/item'
    copies.mkdir(parents=True, exist_ok=True)
    items = []
    sheet = Image.new('RGB', (5 * 260, 3 * 290), '#181c25')
    label = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    small = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 11)
    sd = ImageDraw.Draw(sheet)
    for i, (ident, name, design) in enumerate(zip(IDS, NAMES, DESIGNS)):
        im = draw(ident)
        im.save(target / f'{ident}.png')
        im.save(copies / f'{ident}.png')
        x, y = i % 5 * 260, i // 5 * 290
        sd.rectangle((x + 10, y + 10, x + 249, y + 249), fill='#272c36')
        sheet.paste(im.resize((224, 224), Image.Resampling.NEAREST), (x + 18, y + 15), im.resize((224, 224), Image.Resampling.NEAREST))
        sd.text((x + 12, y + 249), name, fill='#e1e4e6', font=label)
        sd.text((x + 12, y + 275), ident, fill='#919ba8', font=small)
        paths, locator, facts, visual = design
        items.append({'id': ident, 'name': name, 'function_process_facts': facts,
                      'text_evidence_paths': paths, 'text_evidence_locator': locator,
                      'new_visual_interpretation': visual})
    sheet.save(OUT / 'process-r4-contact-sheet.png')
    (OUT / 'design-process.json').write_text(json.dumps({'revision': 'R4', 'items': items}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'revision': 'R4', 'count': len(IDS), 'directory': str(OUT)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
