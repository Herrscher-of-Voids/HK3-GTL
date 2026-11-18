from pathlib import Path

from PIL import Image, ImageDraw


def draw():
    im = Image.new('RGBA', (64, 64))
    d = ImageDraw.Draw(im)
    ink = '#2d2528'
    bronze = '#774225'
    shade = '#ab6e30'
    gold = '#dcaa4b'
    light = '#f8d57d'
    pale = '#ffe7a3'
    red = '#681f25'
    black = '#24202a'

    def pts(vertices, dx=0, dy=0):
        return [(round(34 + .65 * u + .76 * v) + dx,
                 round(28 - .76 * u + .65 * v) + dy) for u, v in vertices]

    def poly(vertices, fill, outline=ink):
        d.polygon(pts(vertices), fill=fill, outline=outline)

    def line(vertices, color, width=1):
        d.line(pts(vertices), fill=color, width=width)

    body = [(-36, 0), (-31, -5), (-25, -6), (13, -6), (21, -5),
            (25, 0), (21, 5), (13, 6), (-25, 6), (-31, 5)]
    arm = [(5, 5), (5, 11), (8, 18), (11, 23), (8, 26),
           (3, 27), (-2, 26), (-3, 23), (-1, 20), (-2, 15), (-5, 10), (-5, 5)]
    arms = [arm, [(u, -v) for u, v in arm]]
    curl = [(-24, 5), (-26, 10), (-24, 12), (-20, 12), (-19, 10),
            (-20, 8), (-22, 8), (-21, 10), (-24, 10), (-23, 7)]
    curls = [curl, [(u, -v) for u, v in curl]]
    for shape in [body, *arms, *curls]:
        d.polygon(pts(shape, 2, 3), fill=bronze, outline=ink)

    poly(body, gold)
    line([(-34, 0), (-30, -4), (-24, -5), (19, -4), (23, 0)], light)
    line([(-30, 4), (-23, 5), (20, 4)], shade, 2)
    poly([(-33, 0), (-29, -3), (-23, -4), (15, -4), (21, -3),
          (23, 0), (20, 3), (-24, 4), (-29, 3)], red, shade)
    poly([(-31, 0), (-27, -2), (-5, -3), (-5, 2), (-28, 2)], black, black)
    poly([(8, -3), (18, -3), (21, 0), (18, 2), (8, 3)], black, black)
    line([(-29, -4), (-20, -4), (-9, -4)], pale)
    line([(-25, 3), (-14, 2), (-5, 1)], '#a94832')
    line([(-25, -4), (-19, 0), (-10, 4)], gold)
    line([(-16, -4), (-22, 1), (-25, 4)], light)
    line([(10, -4), (15, 0), (20, 4)], gold)
    line([(10, 4), (17, -3)], light)
    line([(-35, 0), (-30, 2), (-28, 4)], shade)

    for sign in [-1, 1]:
        shape = [(u, v * sign) for u, v in arm]
        poly(shape, gold)
        poly([(u, v * sign) for u, v in [(3, 9), (4, 15), (7, 22),
              (7, 24), (3, 25), (-1, 24), (1, 20), (0, 15), (-3, 9)]], red, shade)
        poly([(u, v * sign) for u, v in [(3, 10), (5, 17), (7, 22),
              (3, 23), (2, 20), (1, 14)]], black, black)
        line([(u, v * sign) for u, v in [(5, 7), (6, 13), (9, 20),
              (10, 23), (7, 25), (3, 26)]], light)
        line([(u, v * sign) for u, v in [(-3, 9), (-1, 15),
              (1, 20), (-1, 24)]], shade)
        line([(u, v * sign) for u, v in [(1, 17), (5, 19), (8, 23)]], gold)
        line([(u, v * sign) for u, v in [(5, 18), (3, 23), (3, 25)]], light)

    for sign in [-1, 1]:
        poly([(u, v * sign) for u, v in curl], gold)
        line([(u, v * sign) for u, v in [(-25, 5), (-27, 9), (-26, 12),
              (-23, 14), (-20, 13), (-18, 10), (-19, 8), (-21, 7)]], bronze, 2)
        line([(u, v * sign) for u, v in [(-25, 5), (-26, 9), (-25, 12),
              (-22, 13), (-19, 11), (-19, 9), (-21, 8)]], light)
        line([(u, v * sign) for u, v in [(-24, 6), (-23, 9),
              (-21, 10), (-21, 9)]], shade)
        line([(u, v * sign) for u, v in [(-24, 5), (-27, 4), (-30, 4)]], light)

    shield = [(-8, -3), (-7, -7), (-3, -8), (0, -7), (4, -8),
              (8, -4), (7, 0), (8, 4), (4, 8), (0, 7), (-4, 8), (-8, 4)]
    d.polygon(pts(shield, 1, 2), fill=bronze, outline=ink)
    poly(shield, gold, bronze)
    line([(-7, -3), (-6, -6), (-3, -7), (0, -6), (4, -7), (7, -4)], pale)
    line([(-7, 3), (-3, 6), (0, 5), (4, 6), (6, 3)], shade, 2)
    poly([(-5, -2), (-3, -5), (0, -4), (3, -5), (5, -2),
          (4, 1), (2, 2), (0, 5), (-2, 2), (-4, 1)], '#e9b957', shade)
    line([(-5, -1), (-2, -2), (0, -4), (2, -2), (5, -1)], light)
    line([(-3, 0), (-1, 0), (0, 3), (1, 0), (3, 0)], bronze)
    line([(-3, -2), (-1, -1), (0, -2), (1, -1), (3, -2)], pale)
    line([(-5, 4), (-2, 3), (0, 5), (2, 3), (5, 4)], light)
    line([(-8, -4), (-9, -6), (-7, -9), (-4, -9)], light)
    line([(-8, 4), (-9, 6), (-7, 9), (-4, 9)], gold)
    line([(5, -6), (9, -8), (10, -6), (8, -4)], light)
    line([(5, 6), (9, 8), (10, 6), (8, 4)], light)

    line([(25, 0), (29, 0)], ink, 4)
    line([(27, -3), (27, 3)], bronze, 3)
    line([(24, 0), (29, 0)], gold, 2)
    line([(27, -3), (27, 3)], gold, 2)
    line([(25, 0), (29, 0)], pale)
    d.point(pts([(27, -2)])[0], fill=pale)
    return im


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[2] / 'deliveries/0002贴图材质_神之键重绘_R6_20261114/textures/item/imitation_oath_of_judah.png'
    target.parent.mkdir(parents=True, exist_ok=True)
    draw().save(target)
