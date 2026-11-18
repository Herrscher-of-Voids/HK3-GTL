import math

import numpy as np

from author_w05_shapes_20261115 import Part, bezier, trace
from w08_common_20261116 import rod


DARK, ARMOR, GOLD, WHITE, AMBER, LIGHT, PURPLE, GLASS, STONE, GILDED, RED, HOT = range(1, 13)
CENTER = np.array([0, 222, 0], float)


def turn(points, angle):
    points = np.asarray(points, float).copy()
    x, z = points[..., 0].copy(), points[..., 2].copy()
    points[..., 0] = x * math.cos(angle) - z * math.sin(angle)
    points[..., 2] = x * math.sin(angle) + z * math.cos(angle)
    return points
