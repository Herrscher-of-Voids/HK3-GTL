import math

import numpy as np

from author_w05_shapes_20261115 import Part, bezier, trace
from w08_common_20261116 import rod


DARK, ARMOR, GOLD, WHITE, AMBER, LIGHT, PURPLE, GLASS, STONE, GILDED, RED, HOT, VOID, CONTROL = range(1, 15)
CX, CZ = 531, 423
CENTER = np.array([CX, 180, CZ], float)


def wall_z(x, side):
    front = 100 + 110 * ((x - CX) / 450) ** 2
    return front if side < 0 else 2 * CZ - front
