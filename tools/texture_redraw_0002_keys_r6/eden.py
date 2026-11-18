from pathlib import Path

from PIL import Image, ImageDraw


def draw():
    im = Image.new('RGBA', (64, 64))
    d = ImageDraw.Draw(im)
    ink = '#17131d'
    steel = '#292331'
    plate = '#3e3245'
    edge = '#695366'
    bronze = '#694330'
    gold = '#c38747'
    light = '#edbb70'
    glint = '#ffe3a5'
    red = '#b92d3f'
    dark_red = '#531b32'

    d.polygon([(26, 6), (31, 3), (38, 8), (43, 19), (38, 24), (31, 16)], fill=steel, outline=ink)
    d.polygon([(29, 6), (32, 5), (37, 10), (39, 16), (36, 18), (32, 12)], fill=plate)
    d.line([(28, 7), (31, 6), (34, 9)], fill=edge)
    d.line([(32, 12), (35, 15), (36, 20)], fill='#74586b')
    for x, y in ((30, 8), (34, 14), (38, 20)):
        d.line((x, y, x + 2, y + 1), fill=dark_red, width=2)
        d.point((x + 1, y), fill=red)
    d.polygon([(35, 13), (40, 12), (47, 18), (50, 29), (42, 36), (37, 27)], fill=steel, outline=ink)
    d.polygon([(39, 15), (43, 18), (47, 26), (44, 29), (41, 22)], fill=plate)
    d.line([(38, 14), (42, 15), (47, 24)], fill=edge)
    d.line([(40, 22), (44, 22)], fill=ink)
    d.line([(41, 27), (46, 28)], fill=ink)

    d.polygon([(25, 25), (35, 19), (44, 25), (52, 39), (43, 51), (32, 47), (23, 37)], fill=steel, outline=ink)
    d.polygon([(28, 26), (34, 23), (40, 27), (44, 38), (37, 43), (28, 36)], fill=plate)
    d.line([(28, 26), (34, 24), (38, 27)], fill=edge)
    d.line([(29, 31), (34, 35), (37, 42)], fill=ink, width=2)
    d.line([(32, 27), (37, 31)], fill=bronze)

    left_horn = [(28, 42), (34, 31), (39, 21), (39, 14), (37, 10),
                 (40, 10), (43, 14), (44, 23), (40, 34), (34, 45)]
    d.polygon(left_horn, fill=gold, outline=bronze)
    d.line([(29, 41), (35, 29), (40, 21), (40, 14), (38, 11)], fill=light)
    d.line([(34, 42), (39, 32), (43, 22)], fill='#9a5c38')
    right_horn = [(34, 45), (44, 33), (51, 22), (54, 14), (56, 15),
                  (58, 21), (56, 29), (48, 40), (41, 47)]
    d.polygon(right_horn, fill=gold, outline=bronze)
    d.line([(36, 44), (46, 32), (52, 22), (55, 16)], fill=light, width=2)
    d.line([(43, 44), (52, 34), (56, 25)], fill='#9a5737')
    d.line([(55, 16), (56, 20)], fill=glint)
    d.polygon([(30, 38), (35, 37), (41, 42), (41, 47), (36, 51), (29, 46)], fill=gold, outline=bronze)
    d.line([(31, 39), (35, 39), (39, 43), (39, 46), (35, 49)], fill=light)
    d.polygon([(32, 41), (35, 40), (38, 44), (35, 47), (32, 45)], fill=bronze)
    d.line([(33, 41), (35, 42), (36, 44)], fill=glint)

    d.ellipse((35, 29, 58, 52), fill=ink)
    d.ellipse((36, 30, 57, 51), fill=dark_red)
    d.ellipse((37, 30, 56, 48), fill=red)
    d.polygon([(38, 35), (42, 31), (48, 30), (53, 33), (53, 36), (47, 36), (43, 40), (39, 39)], fill='#e55256')
    d.line([(41, 33), (45, 32), (49, 32)], fill='#f58a72')
    d.arc((38, 31, 56, 49), 15, 96, fill='#8d263e', width=2)
    d.line([(48, 47), (53, 42), (56, 37)], fill='#762139', width=2)
    d.line([(39, 44), (44, 49), (49, 50)], fill='#43192d', width=2)

    d.polygon([(4, 11), (13, 15), (22, 22), (32, 31), (39, 41),
               (35, 45), (27, 41), (18, 31), (10, 21)], fill=steel, outline=ink)
    d.polygon([(8, 15), (17, 20), (26, 29), (34, 39), (28, 37), (18, 27)], fill='#332b37')
    d.polygon([(12, 20), (21, 25), (28, 32), (33, 40), (27, 36), (18, 27)], fill='#28232e')
    d.line([(4, 11), (11, 14), (20, 21), (29, 29), (36, 39)], fill=gold)
    d.line([(5, 12), (10, 14), (15, 18)], fill=light)
    d.line([(12, 21), (22, 30), (30, 39)], fill=ink)
    d.line([(22, 25), (27, 27), (30, 32)], fill=bronze)
    d.point((22, 24), fill=red)

    d.polygon([(7, 30), (17, 36), (27, 42), (38, 45), (43, 44),
               (40, 51), (34, 59), (28, 61), (21, 54), (14, 44)], fill=steel, outline=ink)
    d.polygon([(13, 36), (22, 42), (31, 47), (38, 47), (33, 55), (29, 57), (21, 49)], fill='#302833')
    d.polygon([(21, 44), (30, 49), (34, 49), (30, 56), (25, 52)], fill='#211e29')
    d.line([(8, 31), (17, 37), (27, 43), (37, 46), (42, 45)], fill=gold)
    d.line([(10, 33), (19, 39), (27, 44)], fill=light)
    d.line([(32, 58), (37, 51), (39, 48)], fill=bronze)
    d.line([(16, 43), (22, 50), (28, 56)], fill=ink)
    d.line([(27, 46), (31, 47)], fill=gold)
    d.polygon([(17, 34), (22, 34), (29, 40), (30, 44), (25, 45), (19, 41)], fill='#31252f', outline=ink)
    d.line([(19, 35), (23, 37), (27, 41)], fill=gold)
    d.line([(21, 38), (25, 42)], fill=light)
    d.polygon([(46, 46), (51, 45), (57, 39), (59, 41), (56, 48), (49, 52), (44, 51)], fill=steel, outline=ink)
    d.line([(48, 48), (53, 47), (57, 43)], fill='#7d3347')
    return im


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[2] / 'deliveries/0002贴图材质_神之键重绘_R6_20261114/textures/item/imitation_star_of_eden.png'
    target.parent.mkdir(parents=True, exist_ok=True)
    draw().save(target)
