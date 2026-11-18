import math

import numpy as np

from author_w05_shapes_20261115 import Part, bezier, trace
from w08_common_20261116 import rod


DARK, ARMOR, GOLD, WHITE, RED, LIGHT, PURPLE, GLASS, STONE, GILDED, CRIMSON, HOT, VOID, CONTROL = range(1, 15)
CX, CZ = 487, 500
CENTER = np.array([CX, 220, CZ], float)
PEAKS = [(CX + 413 * math.cos(i * math.pi / 4), CZ + 413 * math.sin(i * math.pi / 4)) for i in range(8)]
