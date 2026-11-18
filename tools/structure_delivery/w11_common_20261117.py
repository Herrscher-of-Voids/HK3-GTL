import numpy as np

from author_w05_shapes_20261115 import Part
from w08_common_20261116 import rod


BLACK, STUDS, WHITE, GOLD, RED, MAGENTA, LIGHT, WHITE_LIGHT, GLASS, GRAY, HK, CONTROLLER = range(1, 13)
CX = CZ = -.5


def line(part, start, end, state):
    a, b = np.asarray(start, float), np.asarray(end, float)
    count = int(np.max(np.abs(b - a))) * 2 + 1
    part.points(np.linspace(a, b, count), state)
