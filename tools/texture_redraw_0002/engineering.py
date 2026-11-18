from pathlib import Path
import json
import random

from PIL import Image, ImageDraw


STEEL = ['#30332f', '#525953', '#788079', '#a4aba0', '#dce0cc']
IRON = ['#222823', '#3c4840', '#647568', '#93a294', '#c1cebb']
IVORY = ['#57574a', '#898977', '#b5b59d', '#d5d4b7', '#f2edce']
COPPER = ['#4b3627', '#765237', '#a87545', '#cba25f', '#efd08e']
PURPLE = ['#2d2638', '#473959', '#70558c', '#a47bbe', '#d9bbec']
BLUE = ['#243840', '#37535d', '#587d88', '#8cbdc3', '#d0eee2']
GREEN = ['#243428', '#36513a', '#4e7150', '#7b9b66', '#b7cc90']
BLACK = ['#20221f', '#333832', '#495248', '#737d6b', '#a4ac96']


class Sprite:
    def __init__(self):
        self.im = Image.new('RGBA', (64, 64))
        self.d = ImageDraw.Draw(self.im)

    def face(self, points, palette=STEEL, seed=0):
        mask = Image.new('1', (64, 64))
        ImageDraw.Draw(mask).polygon(points, fill=1)
        self.d.polygon(points, fill=palette[2], outline=palette[0])
        rng = random.Random(seed)
        left, top, right, bottom = mask.getbbox()
        for y in range(top + 1, bottom - 1):
            for x in range(left + 1, right - 1):
                if mask.getpixel((x, y)) and mask.getpixel((x - 1, y)) and mask.getpixel((x + 1, y)):
                    if rng.randrange(17) == 0:
                        self.d.point((x, y), fill=palette[1 if y > (top + bottom) // 2 else 3])
        for i, start in enumerate(points):
            end = points[(i + 1) % len(points)]
            if end[0] > start[0]:
                self.d.line((start, end), fill=palette[3])

    def box(self, box, palette=STEEL, seed=0):
        x1, y1, x2, y2 = box
        self.face([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], palette, seed)
        self.d.line((x1 + 1, y1 + 1, x2 - 1, y1 + 1), fill=palette[4])
        self.d.line((x1 + 1, y1 + 2, x1 + 1, y2 - 1), fill=palette[3])
        self.d.line((x2 - 1, y1 + 2, x2 - 1, y2 - 1), fill=palette[1])
        self.d.line((x1 + 1, y2 - 1, x2 - 1, y2 - 1), fill=palette[0])

    def bolt(self, x, y, palette=STEEL):
        self.d.rectangle((x, y, x + 2, y + 2), fill=palette[0])
        self.d.line((x, y, x + 1, y), fill=palette[4])
        self.d.point((x + 1, y + 1), fill=palette[2])

    def trace(self, pts, color=COPPER[3], width=1):
        self.d.line(pts, fill=color, width=width)
        x, y = pts[-1]
        self.d.rectangle((x - 1, y - 1, x + 1, y + 1), outline=color)

    def slots(self, box, vertical=False):
        x1, y1, x2, y2 = box
        for t in range(x1 if vertical else y1, x2 if vertical else y2, 3):
            p = (t, y1, t, y2) if vertical else (x1, t, x2, t)
            self.d.line(p, fill=STEEL[0])
            q = tuple(v + (1 if (i % 2 == (0 if vertical else 1)) else 0) for i, v in enumerate(p))
            self.d.line(q, fill=STEEL[3])


def detector(n):
    s = Sprite(); d = s.d
    s.face([(11, 21), (46, 17), (52, 22), (51, 56), (17, 60), (10, 53)], IRON, 10)
    s.face([(46, 17), (52, 22), (51, 56), (45, 53)], BLACK, 11)
    s.box((13, 22, 45, 54), IVORY if n < 3 else STEEL, 20 + n)
    s.box((17, 26, 40, 40), BLACK, 30)
    d.rectangle((19, 28, 38, 37), fill=GREEN[0])
    for y in range(29, 37, 2):
        d.line((20, y, 37, y), fill=GREEN[1])
    d.line([(20, 34), (23, 34), (25, 30), (27, 36), (30, 32), (33, 32), (35, 30), (37, 30)], fill=GREEN[4])
    for x in [17, 23, 29]:
        s.box((x, 44, x + 3, 47), COPPER if x == 17 else STEEL)
    s.slots((17, 51, 29, 54))
    d.ellipse((34, 44, 40, 50), fill=BLACK[0], outline=STEEL[4])
    d.line((37, 45, 36, 48), fill=IVORY[3])
    for x, y in [(14, 23), (41, 23), (14, 50), (41, 50)]: s.bolt(x, y)
    s.box((22, 17, 36, 22), COPPER)
    if n == 0:
        s.box((10, 7, 23, 15), STEEL)
        d.line([(16, 16), (16, 20), (20, 21)], fill=COPPER[1], width=3)
        d.line((13, 9, 20, 9), fill=IVORY[4])
        d.rectangle((14, 11, 19, 12), fill=BLACK[0])
        d.line([(9, 14), (6, 17), (6, 36), (10, 40)], fill=BLACK[1], width=2)
    elif n == 1:
        s.box((25, 4, 33, 17), STEEL)
        d.rectangle((27, 7, 31, 14), fill=BLUE[1])
        d.rectangle((28, 11, 30, 14), fill=BLUE[3])
        d.line((28, 6, 28, 10), fill=BLUE[4])
        s.box((23, 2, 35, 5), COPPER)
    elif n == 2:
        s.box((18, 12, 39, 17), STEEL)
        s.face([(22, 12), (24, 5), (30, 2), (35, 8), (34, 13)], PURPLE, 50)
        d.line([(25, 6), (29, 4), (28, 11)], fill=PURPLE[4])
        s.box((18, 6, 21, 13), COPPER)
        s.box((36, 6, 39, 13), COPPER)
    elif n == 3:
        d.ellipse((17, 1, 41, 18), fill=BLACK[0], outline=STEEL[3], width=2)
        for x in range(21, 39, 4): d.line((x, 4, x, 14), fill=COPPER[3])
        d.line((20, 9, 39, 9), fill=STEEL[2])
        s.box((26, 16, 33, 21), STEEL)
    else:
        for x in [17, 37]:
            s.box((x, 4, x + 4, 17), COPPER)
            for y in range(6, 16, 3): d.line((x, y, x + 4, y), fill=IVORY[3])
        d.ellipse((23, 2, 35, 15), fill=PURPLE[0], outline=STEEL[3])
        d.line([(26, 5), (31, 5), (28, 8), (32, 9), (26, 13)], fill=PURPLE[4])
        s.box((23, 16, 35, 20), STEEL)
    return s.im


def circuit(ident):
    s = Sprite(); d = s.d
    if ident in ['process_gas_filter', 'depleted_gas_filter']:
        spent = ident.startswith('depleted')
        s.box((15, 11, 47, 52), STEEL, 70)
        d.ellipse((15, 6, 47, 17), fill=STEEL[2], outline=STEEL[0])
        d.ellipse((18, 8, 44, 14), fill=BLACK[1], outline=STEEL[4])
        d.ellipse((22, 9, 40, 13), fill=BLACK[0])
        s.box((18, 17, 44, 47), COPPER if spent else IVORY, 71)
        for x in range(20, 44, 3):
            d.line((x, 18, x, 46), fill=COPPER[0] if spent else STEEL[1])
            d.line((x + 1, 19, x + 1, 46), fill=COPPER[2] if spent else IVORY[4])
        if spent:
            for x, y in [(24, 24), (34, 35), (28, 40), (39, 28)]:
                d.rectangle((x, y, x + 4, y + 2), fill='#514531')
                d.point((x + 1, y), fill='#8d6840')
        s.box((14, 47, 48, 54), STEEL)
        for x in [18, 43]: s.bolt(x, 49)
        return s.im
    if ident == 'process_gas_impurity':
        for pts, seed in [([(10, 38), (18, 28), (26, 29), (28, 42), (20, 48)], 80),
                          ([(29, 20), (36, 10), (44, 17), (39, 29)], 81),
                          ([(34, 40), (46, 33), (55, 42), (48, 52), (36, 50)], 82)]:
            palette = COPPER if seed == 80 else STEEL
            s.face(pts, palette, seed)
            x, y = pts[1]
            s.face([(x, y), (x + 6, y + 2), (x + 3, y + 8), (x - 5, y + 6)],
                   [palette[0], palette[1], palette[3], palette[4], palette[4]], seed)
            d.line([(x - 5, y + 9), (x, y + 7), (x + 4, y + 11)], fill=palette[0])
            d.line([(x - 2, y + 11), (x + 2, y + 13), (x + 1, y + 16)], fill=palette[1], width=2)
            d.point((x - 3, y + 4), fill=palette[4])
            d.rectangle((x + 4, y + 8, x + 5, y + 9), fill=palette[0])
        for x, y in [(7, 31), (26, 53), (47, 28), (32, 32)]: d.rectangle((x, y, x + 1, y + 1), fill=STEEL[2])
        return s.im
    package = ident in ['circuit_encapsulation_part', 'rejected_circuit_package']
    mask = ident == 'circuit_lithography_mask'
    bad = ident in ['defective_circuit_substrate', 'failed_circuit_layer', 'rejected_circuit_package']
    if package:
        for x in range(14, 49, 5):
            s.box((x, 10, x + 2, 17), COPPER)
            s.box((x, 47, x + 2, 54 + (x % 3 if bad else 0)), COPPER)
        for y in range(20, 45, 5):
            s.box((6, y, 13, y + 2), COPPER)
            s.box((49, y, 57, y + 2), COPPER)
        s.box((12, 16, 50, 48), BLACK, 91)
        s.box((16, 20, 46, 44), STEEL, 93)
        d.rectangle((20, 24, 41, 40), fill=BLACK[1])
        for y in [27, 31, 35]: d.line((22, y, 37, y), fill=STEEL[2])
        d.rectangle((21, 25, 24, 28), fill=COPPER[3])
    else:
        s.face([(9, 13), (47, 8), (55, 47), (17, 55)], BLACK, 100)
        s.face([(11, 15), (45, 11), (52, 45), (19, 52)], BLUE if mask else GREEN, 101)
        for k in range(9):
            x, y = 20 + k * 3, 49 - k // 3
            d.line((x, y, x + 1, y + 3), fill=COPPER[3], width=2)
            d.point((x, y + 1), fill=COPPER[4])
        traces = [[(14, 22), (21, 21), (24, 24)], [(15, 28), (23, 27), (26, 31)],
                  [(21, 17), (23, 23)], [(32, 15), (32, 21)], [(40, 16), (39, 23)],
                  [(43, 28), (47, 28), (49, 33)], [(35, 41), (37, 45), (45, 43)],
                  [(19, 40), (23, 39), (25, 43)]]
        for path in traces: s.trace(path, BLUE[4] if mask else COPPER[3])
        if ident in ['etched_circuit_layer', 'failed_circuit_layer']:
            for n in range(4):
                s.trace([(20, 25 + n * 4), (36, 23 + n * 4), (43, 28 + n * 4)], COPPER[4])
        elif mask:
            d.polygon([(23, 22), (37, 20), (41, 38), (27, 40)], fill=BLUE[0], outline=BLUE[4])
            d.line([(28, 36), (27, 26), (35, 25), (37, 35), (31, 36), (30, 29)], fill=BLUE[3])
        else:
            s.box((25, 23, 38, 37), BLACK, 103)
            for x in [26, 30, 34, 37]:
                d.line((x, 20, x, 23), fill=STEEL[3]); d.line((x, 38, x, 41), fill=STEEL[3])
            d.rectangle((28, 26, 34, 32), fill=PURPLE[2])
            d.line((28, 26, 34, 26), fill=PURPLE[4])
        for x, y in [(13, 17), (43, 14), (20, 46), (48, 42)]: s.bolt(x, y, COPPER)
    if bad:
        d.line([(40, 15), (35, 23), (39, 28), (31, 34), (35, 41), (31, 47)], fill=BLACK[0], width=2)
        for x, y in [(35, 23), (31, 34), (35, 40)]:
            d.rectangle((x - 1, y, x + 2, y + 1), fill=COPPER[1])
            d.point((x + 2, y), fill=COPPER[4])
    return s.im


def component(ident):
    s = Sprite(); d = s.d
    if ident == 'soulium_anchor_component':
        s.box((25, 5, 37, 43), STEEL, 120)
        for y in range(10, 38, 6): s.box((22, y, 40, y + 3), COPPER)
        s.face([(25, 36), (19, 39), (11, 53), (16, 58), (28, 43)], STEEL, 121)
        s.face([(35, 37), (42, 40), (53, 50), (49, 56), (34, 46)], STEEL, 122)
        s.box((26, 20, 36, 31), BLACK)
        d.rectangle((29, 23, 33, 28), fill=PURPLE[3]);d.point((29, 23), fill=PURPLE[4])
        for x, y in [(27, 8), (29, 40), (15, 51), (46, 49)]: s.bolt(x, y)
    elif ident == 'spatial_calibration_module':
        s.face([(8, 47), (42, 42), (56, 48), (19, 56)], STEEL, 130)
        s.box((12, 44, 17, 51), BLACK);s.box((44, 40, 48, 48), BLACK)
        d.ellipse((14, 10, 48, 45), fill=BLACK[0], outline=STEEL[3], width=3)
        d.ellipse((18, 14, 44, 41), outline=COPPER[3], width=2)
        d.ellipse((22, 7, 39, 46), outline=STEEL[4], width=2)
        s.box((26, 22, 36, 32), BLUE)
        for x, y in [(15, 25), (42, 25), (28, 9), (29, 41)]: s.box((x, y, x + 4, y + 4), COPPER)
        d.line((10, 39, 24, 39), fill=STEEL[4]);s.bolt(19, 48)
    elif ident == 'world_maintenance_specimen':
        s.box((15, 9, 47, 54), STEEL, 140)
        s.box((20, 15, 42, 45), BLACK)
        d.ellipse((22, 19, 40, 40), fill=BLUE[0], outline=BLUE[3])
        s.face([(26, 23), (34, 21), (38, 29), (32, 36), (25, 32)], BLUE, 141)
        d.line((24, 17, 24, 33), fill=BLUE[4]);d.point((26, 18), fill=IVORY[4])
        for y in [12, 48]:
            s.box((11, y, 23, y + 5), COPPER);s.box((39, y, 51, y + 5), COPPER)
        for x, y in [(17, 12), (44, 12), (17, 49), (44, 49)]: s.bolt(x, y)
    elif ident in ['confining_composite', 'composite_offcut']:
        carbon = ['#20262c', '#303940', '#4e5960', '#7d8b92', '#bfccd0']
        shapes = [[(9, 24), (38, 12), (55, 27), (26, 43)], [(10, 30), (38, 18), (54, 33), (26, 49)]]
        if ident == 'composite_offcut': shapes = [[(8, 28), (23, 22), (29, 35), (15, 42)], [(35, 12), (51, 17), (44, 29), (32, 25)], [(35, 40), (47, 36), (56, 48), (41, 53)]]
        for i, pts in enumerate(reversed(shapes)):
            s.face([(x, y + 5) for x, y in pts], COPPER, 151 + i)
            d.line([(x, y + 3) for x, y in pts[1:]], fill=PURPLE[2])
            s.face(pts, carbon, 155 + i)
            mask = Image.new('1', (64, 64))
            ImageDraw.Draw(mask).polygon(pts, fill=1)
            for y in range(12, 54):
                for x in range(8, 57):
                    if mask.getpixel((x, y)) and mask.getpixel((x - 1, y)) and mask.getpixel((x + 1, y)):
                        if (x + y) % 6 == 0:
                            d.point((x, y), fill=carbon[3])
                        elif (x - y) % 6 == 0:
                            d.point((x, y), fill=carbon[1])
            left, top = pts[0]
            d.line((left + 2, top, left + 7, top - 2), fill=PURPLE[3])
    elif ident == 'polarized_electromagnetic_material':
        d.ellipse((8, 9, 54, 54), fill=STEEL[0], outline=STEEL[3], width=2)
        d.ellipse((11, 12, 51, 51), fill=COPPER[1], outline=COPPER[4], width=2)
        d.ellipse((23, 24, 40, 41), fill=(0, 0, 0, 0), outline=BLACK[0], width=3)
        for pts in [[(15, 18), (26, 27)], [(11, 27), (24, 31)], [(12, 37), (24, 36)], [(18, 46), (28, 39)], [(29, 50), (31, 41)], [(40, 47), (36, 40)], [(48, 39), (39, 35)], [(49, 27), (40, 31)], [(43, 17), (36, 26)], [(30, 13), (31, 24)]]:
            d.line(pts, fill=COPPER[0], width=3);d.line([(x - 1, y) for x, y in pts], fill=COPPER[3])
        s.box((10, 7, 20, 15), STEEL);s.box((42, 5, 51, 13), STEEL)
        d.rectangle((13, 8, 17, 10), fill='#a35b45');d.rectangle((44, 6, 48, 8), fill=BLUE[2])
    elif ident == 'cryogenic_condensed_material':
        s.face([(11, 30), (22, 13), (41, 9), (53, 29), (45, 51), (23, 56)], BLUE, 170)
        s.face([(22, 13), (35, 21), (30, 44), (11, 30)], [BLUE[0], BLUE[1], BLUE[3], BLUE[4], '#f2f6df'], 171)
        s.face([(35, 21), (41, 9), (53, 29), (45, 51), (30, 44)], BLUE, 172)
        d.line([(20, 22), (27, 28), (23, 32), (29, 38)], fill=BLUE[4])
        for x, y in [(17, 30), (26, 17), (37, 35), (41, 43), (32, 48)]:
            d.line((x - 2, y, x + 2, y), fill=BLUE[4]);d.line((x, y - 2, x, y + 2), fill=BLUE[4])
    elif ident == 'extreme_casting_material':
        s.face([(7, 32), (20, 18), (46, 20), (57, 34), (44, 48), (18, 50)], BLACK, 180)
        hot = ['#5c2922', '#9f4627', '#d77a32', '#eeb452', '#ffe3a0']
        s.face([(11, 30), (23, 21), (44, 24), (51, 34), (39, 41), (20, 41)], hot, 181)
        for pts in [[(15, 29), (26, 26), (34, 29), (45, 28)], [(17, 35), (27, 36), (37, 33), (45, 35)]]: d.line(pts, fill=hot[4])
        for x in [16, 26, 37, 47]: s.bolt(x, 43)
    elif ident == 'civilization_singularity':
        s.face([(17, 48), (44, 43), (56, 49), (28, 57), (9, 53)], STEEL, 190)
        for x in [14, 45]: s.box((x, 20, x + 5, 48), STEEL)
        s.box((16, 11, 48, 18), COPPER)
        d.ellipse((21, 17, 44, 43), fill=BLACK[0], outline=PURPLE[2], width=2)
        d.arc((15, 24, 50, 36), 175, 355, fill=COPPER[4], width=2)
        d.arc((15, 24, 50, 36), 0, 170, fill=STEEL[4])
        d.arc((22, 16, 43, 45), 185, 270, fill=PURPLE[4])
        for x, y in [(15, 20), (46, 20), (23, 49), (40, 47)]: s.bolt(x, y)
    return s.im


def ship(ident):
    s = Sprite(); d = s.d
    if ident == 'imitation_hyperion_blueprint':
        s.face([(10, 8), (46, 8), (55, 17), (53, 56), (9, 55)], COPPER, 210)
        s.box((12, 10, 45, 52), BLUE, 211)
        for x in range(16, 44, 5): d.line((x, 14, x, 48), fill=BLUE[1])
        for y in range(15, 50, 5): d.line((16, y, 43, y), fill=BLUE[1])
        d.polygon([(17, 33), (25, 28), (40, 27), (44, 31), (39, 34), (24, 35)], outline=BLUE[4])
        d.line((24, 29, 27, 23, 32, 22, 34, 28), fill=IVORY[3])
        d.line((21, 38, 42, 37), fill=BLUE[3]);d.line((19, 41, 19, 45, 39, 45), fill=BLUE[3])
        d.rectangle((16, 14, 25, 16), fill=IVORY[3]);s.face([(46, 9), (53, 17), (46, 17)], IVORY)
        s.box((7, 7, 10, 56), STEEL)
    elif ident == 'hyperion_keel_segment':
        s.face([(5, 39), (43, 9), (58, 19), (20, 52)], STEEL, 220)
        s.face([(7, 44), (45, 14), (56, 21), (18, 52)], BLACK, 221)
        d.line([(6, 38), (43, 8), (57, 17)], fill=IVORY[4], width=2)
        d.line([(17, 47), (53, 18)], fill=STEEL[3], width=2)
        for x, y in [(14, 36), (24, 28), (34, 20), (44, 12)]:
            s.face([(x, y), (x + 3, y - 2), (x + 11, y + 5), (x + 8, y + 7)], COPPER, x)
            s.bolt(x + 5, y + 1)
    elif ident == 'hyperion_navigation_module':
        s.box((9, 38, 53, 54), STEEL, 230)
        s.box((12, 41, 27, 49), BLACK)
        s.slots((31, 42, 48, 50))
        d.ellipse((18, 8, 47, 40), fill=BLACK[0], outline=STEEL[3], width=2)
        d.ellipse((22, 12, 43, 36), outline=COPPER[3], width=2)
        d.ellipse((27, 8, 38, 40), outline=STEEL[3])
        d.line((20, 24, 45, 24), fill=STEEL[4])
        s.box((29, 20, 35, 27), BLUE)
        s.box((17, 3, 21, 16), COPPER)
        d.rectangle((15, 44, 22, 46), fill=GREEN[3]);s.bolt(47, 41)
    else:
        s.face([(6, 29), (17, 18), (46, 16), (57, 26), (53, 46), (18, 54), (6, 44)], STEEL, 240)
        s.face([(7, 28), (19, 18), (44, 18), (54, 26), (39, 35), (18, 37)], IVORY, 241)
        s.face([(18, 37), (39, 35), (53, 28), (51, 43), (21, 50)], STEEL, 242)
        for pts in [[(18, 25), (25, 22), (31, 23), (29, 28), (21, 30)], [(33, 22), (42, 21), (46, 25), (38, 29), (32, 28)]]:
            s.face(pts, BLUE, 244)
            d.line((pts[0], pts[1]), fill=BLUE[4])
        s.box((25, 7, 39, 18), STEEL)
        d.line((30, 8, 30, 2, 43, 2), fill=STEEL[3]);d.rectangle((43, 2, 45, 3), fill='#a55540')
        s.slots((24, 41, 42, 46));s.bolt(11, 37);s.bolt(45, 34)
    return s.im


DETECTORS = ['prototype_honkai_detector', 'liquid_honkai_detector', 'solid_honkai_detector',
             'gaseous_honkai_detector', 'energy_honkai_detector']


def draw(ident):
    if ident in DETECTORS:
        return detector(DETECTORS.index(ident))
    if 'circuit' in ident or ident in ['process_gas_filter', 'depleted_gas_filter', 'process_gas_impurity']:
        return circuit(ident)
    if ident.startswith('hyperion_') or ident == 'imitation_hyperion_blueprint':
        return ship(ident)
    return component(ident)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / 'logs/item-texture-refresh-20261112/engineering-manifest.json').read_text(encoding='utf-8'))
    for row in manifest['changed']:
        draw(row['id']).save(root / 'src/main/resources/assets/hk3gtl' / row['path'], optimize=True)
