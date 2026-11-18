import numpy as np

from w14_engine_common_e3_20261118 import Part, GRAY, BLACK, STUDS, SILVER, WSV, radial


NODES = [90, 177, 230, 320, 430, 530, 600, 614]
TOPS = [219, 219, 214, 172, 90, 45, 28, 28]


def leg_width(u):
    return 53 - np.clip((u - 177) / 423, 0, 1) * 14


def sector_mask(x, z, angle):
    u, v = x * np.cos(angle) + z * np.sin(angle), -x * np.sin(angle) + z * np.cos(angle)
    boundary_u = u * np.cos(np.pi / 7) + abs(v) * np.sin(np.pi / 7)
    clearance = u * np.sin(np.pi / 7) - abs(v) * np.cos(np.pi / 7)
    r2 = x * x + z * z
    mask = (r2 >= 90 ** 2) & (r2 <= 606 ** 2) & (clearance > leg_width(boundary_u))
    return mask, u, v


def build():
    result = []
    for index in range(7):
        angle = np.pi / 2 + index * 2 * np.pi / 7
        corners = np.array([radial(u, 0, v, angle) for u in [90, 614] for v in [-54, 54]])
        low, high = np.floor(corners.min(0)).astype(int), np.ceil(corners.max(0)).astype(int)
        z, x = np.mgrid[low[2]:high[2] + 1, low[0]:high[0] + 1]
        u, v = x * np.cos(angle) + z * np.sin(angle), -x * np.sin(angle) + z * np.cos(angle)
        width = leg_width(u)
        inside = (u >= 90) & (u <= 614) & (abs(v) <= width) & (x * x + z * z <= 614 ** 2)
        xx, zz, uu, vv, ww = [a[inside] for a in [x, z, u, v, width]]
        top = np.rint(np.interp(uu, NODES, TOPS)).astype(int) - 11
        wall = Part(f'leg-wall-{index}', f'斜腿到底隔墙{index + 1}', group='engine')
        for y in range(5, int(top.max()) + 1):
            keep = y <= top
            side = abs(vv[keep]) >= ww[keep] - 2
            states = np.full(keep.sum(), BLACK, np.uint8)
            states[side] = GRAY
            states[side & (np.mod(uu[keep] - 108, 44) < 3)] = STUDS
            states[side & (y % 28 < 2)] = SILVER
            states[side & (y == 35)] = WSV
            points = np.c_[xx[keep], np.full(keep.sum(), y), zz[keep]]
            for state in np.unique(states):
                wall.points(points[states == state], state)
        result.append(wall.finish())
        print(f'斜腿隔墙{index + 1}已从底盘封至桁架', flush=True)
    return result
