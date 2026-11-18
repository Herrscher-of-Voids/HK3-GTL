import math

import numpy as np

from author_w05_shapes_20261115 import Part, bezier, trace


ARMOR, DARK, GOLD, RED, ORANGE, YELLOW, LIGHT, COOL, GLASS, VOID, METAL, GRATE, CONTROL, RED_GLASS, MAGMA = range(1, 16)
CX, CZ = 489, 460
STAR_CENTER = np.array([CX, 150, CZ], float)


def rod(part, start, end, radius, state, inner=0):
    a, b = np.asarray(start, float), np.asarray(end, float)
    axis = b - a
    length = np.linalg.norm(axis)
    axis /= length
    reference = [0, 0, 1] if abs(axis[2]) < .9 else [0, 1, 0]
    u = np.cross(axis, reference)
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    q = np.arange(-math.ceil(radius), math.ceil(radius) + 1)
    uu, vv = np.meshgrid(q, q, indexing='ij')
    squared = uu * uu + vv * vv
    mask = (squared <= radius * radius) & (squared >= inner * inner)
    offsets = uu[mask, None] * u + vv[mask, None] * v
    centers = a + np.linspace(0, length, math.ceil(length / .75) + 1)[:, None] * axis
    for chunk in np.array_split(centers, max(1, math.ceil(len(centers) / 128))):
        part.points((chunk[:, None, :] + offsets[None, :, :]).reshape(-1, 3), state)
