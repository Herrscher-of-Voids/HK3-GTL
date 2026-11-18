# -*- coding: utf-8 -*-
"""对照原作正面与俯侧原帧制作尖楔龙首和回掠长角。"""
import numpy as np

from w04_kurikara_d1_parts_20261110 import hull, loft, facet, traced


def build(Part, palette):
    p = Part('dragon_01_原作尖楔面甲与后掠长角')
    black, dark, red, light, ivory, metal, glow = [palette[key] for key in
        ['black', 'dark', 'red', 'light', 'ivory', 'metal', 'glow']]

    loft(p, [np.array([[-w, bottom, z], [w, bottom, z], [w, top, z], [-w, top, z]])
             for z, w, bottom, top in [(101, 17, 244, 274), (123, 27, 250, 282),
                                      (149, 24, 249, 274), (177, 16, 247, 261),
                                      (199, 7, 245, 252), (212, .5, 245, 247)]], dark)
    loft(p, [np.array([[-w, bottom, z], [w, bottom, z], [w, top, z], [-w, top, z]])
             for z, w, bottom, top in [(119, 19, 241, 248), (143, 21, 236, 241),
                                      (172, 14, 236, 240), (195, 6, 240, 243),
                                      (208, .5, 243, 245)]], black)

    for side in [-1, 1]:
        facet(p, [[0, 285, 122], [side * 25, 277, 124], [side * 24, 270, 150],
                  [side * 14, 256, 187], [0, 246, 212], [0, 263, 174]],
              [side * .2, 1, .15], 4, red, peak=1)
        facet(p, [[side * 26, 273, 121], [side * 26, 260, 142],
                  [side * 19, 247, 176], [side * 12, 247, 194],
                  [side * 20, 263, 159]], [side, 0, .2], 3.5, red)
        facet(p, [[side * 25, 270, 124], [side * 25.8, 284, 99],
                  [side * 15, 280, 111], [side * 17, 274, 141]],
              [side * .5, .5, .2], 3, red)
        facet(p, [[side * 27, 264, 123], [side * 25, 249, 139],
                  [side * 21, 245, 151], [side * 23, 258, 138]],
              [side, 0, 0], 2, black)
        facet(p, [[side * 27.3, 260, 126], [side * 25.5, 250, 137],
                  [side * 23.5, 250, 139], [side * 25, 261, 127]],
              [side, 0, 0], 1, metal)
        facet(p, [[side * 23, 278, 127], [side * 21, 272, 148],
                  [side * 17, 266, 163], [side * 20, 274, 143]],
              [side * .2, 1, .15], 1.3, light)
        facet(p, [[side * 20, 240, 145], [side * 13, 239, 174],
                  [side * 5, 242, 198], [side * 15, 241, 171]],
              [side * .3, -1, .1], 1.6, dark)

    for side in [-1, 1]:
        facet(p, [[side * 12, 287, 119], [side * 3, 281, 132],
                  [0, 269, 170], [side * 10, 277, 148]],
              [0, 1, .25], 2.2, dark)
    hull(p, [[-4, 283, 117], [4, 283, 117], [0, 287, 119],
             [-3, 278, 140], [3, 278, 140], [0, 269, 170]], dark)
    traced(p, [[0, 287, 122], [0, 282, 137], [0, 272, 161]], 1.05, black)

    for side in [-1, 1]:
        path = np.array([[side * 17, 281, 123], [side * 22, 304, 109],
                         [side * 30, 329, 86], [side * 37, 350, 62],
                         [side * 39, 363, 44]], float)
        widths = [10, 9, 6.5, 3.2, .25]
        cross = np.array([0, .65, .76])
        sections = [np.array([center + [-width, 0, 0], center + cross * width * .55,
                              center + [width, 0, 0], center - cross * width * .55])
                    for center, width in zip(path, widths)]
        loft(p, sections, black)
        bone = [np.array([center + [side * width * .28 - width * .7, 0, 0],
                          center + [side * width * .28, 0, 0] + cross * width * .52,
                          center + [side * width * .28 + width * .7, 0, 0],
                          center + [side * width * .28, 0, 0] - cross * width * .4])
                for center, width in zip(path, widths)]
        loft(p, bone, ivory)
        inner = [np.array([center + [side * -width * .45 - width * .42, 0, .5],
                           center + [side * -width * .45, 0, .5] + cross * width * .3,
                           center + [side * -width * .45 + width * .42, 0, .5],
                           center + [side * -width * .45, 0, .5] - cross * width * .3])
                 for center, width in zip(path, widths)]
        loft(p, inner, red)
        facet(p, [[side * 12, 280, 129], [side * 21, 285, 120],
                  [side * 24, 300, 109], [side * 15, 288, 123]],
              [side * .5, .5, .5], 2, red)

    for side in [-1, 1]:
        traced(p, [[side * 25, 263, 141], [side * 22, 260, 154],
                   [side * 18, 256, 168]], 2.2, black)
        traced(p, [[side * 23.5, 260.8, 148], [side * 20.5, 258.5, 158]], 1.05, glow)
        traced(p, [[side * 12, 252, 188], [side * 5, 247, 205]], 1.05, black)
    return p.finish()
