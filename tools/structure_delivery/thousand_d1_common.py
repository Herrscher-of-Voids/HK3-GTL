import numpy as np

from author_w05_shapes_20261115 import Part, trace


BLACK, CLOTH, CLOTH_LIGHT, SEAM, WHITE, WHITE_SHADE, WHITE_LIGHT, GOLD, GOLD_LIGHT, GOLD_DARK, HAIR, HAIR_LIGHT, HAIR_SHADE = range(1, 14)
COLORS = [('黑色蒙眼', '#10111a'), ('深蓝黑衣料', '#20232e'), ('衣料折面', '#323642'),
          ('瓷面接缝', '#77707f'), ('白瓷', '#e9deeb'), ('白瓷暗面', '#bbb4ca'),
          ('白瓷亮面', '#faf1f2'), ('装饰金', '#c3a368'), ('金色亮面', '#e7cb8b'),
          ('金色凹槽', '#806344'), ('奶金发壳', '#c8bc8e'), ('发壳亮面', '#e5dfb6'),
          ('发壳片缝', '#96856b')]


def ellipsoid(part, center, radii, state, inner=0):
    c, r = np.asarray(center, float), np.asarray(radii, float)
    lo, hi = np.floor(c-r).astype(int), np.ceil(c+r).astype(int)
    z, x = np.mgrid[lo[2]:hi[2]+1, lo[0]:hi[0]+1]
    for y in range(lo[1], hi[1]+1):
        q = np.c_[x.ravel(), np.full(x.size, y), z.ravel()]
        d = np.linalg.norm((q-c)/r, axis=1)
        part.points(q[(d <= 1) & (d >= inner)], state)
