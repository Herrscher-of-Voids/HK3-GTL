import numpy as np

from w14_engine_common_20261117 import Part, BLACK, STUDS, GRAY, SILVER, VENT, CLEAN, WHITE, YELLOW, BLUE, LIGHT, COMPUTER, WSV, CONTROL, BLUE_LIGHT, PURPLE_LIGHT, CONTROLLER, radial, radial_box, ring_slice


def foundation():
    parts = []
    for section in range(14):
        start, end = section * np.pi / 7, (section + 1) * np.pi / 7
        part = Part(f'dam-{section:02}', f'圆形坝体与承力底盘{section + 1}', group='engine')
        for y in range(5):
            ring_slice(part, y, 624, 82, BLACK if y < 3 else GRAY, start, end)
        for y in range(5, 44):
            outer = 624 - (y - 5) * .28
            state = SILVER if y in [5, 6, 37, 38, 42, 43] else WSV if y in [34, 35] else GRAY
            ring_slice(part, y, outer, outer - 17, state, start, end)
        for index in range(14):
            angle = start + (index + .5) * (end - start) / 14
            radial_box(part, 609, 624, -2, 2, 5, 33, angle, STUDS)
            radial_box(part, 597, 609, -3, 3, 38, 43, angle, SILVER)
        parts.append(part.finish())
    return parts


def core():
    parts = []
    levels = [0, 160, 196, 215, 225, 236, 246, 264, 272, 326, 330]
    radii = [94, 108, 125, 164, 196, 194, 172, 172, 158, 158, 162]
    for section in range(7):
        start, end = section * 2 * np.pi / 7, (section + 1) * 2 * np.pi / 7
        part = Part(f'core-{section:02}', f'中央叠层发射器{section + 1}', group='engine')
        for y in range(5, 331):
            outer = float(np.interp(y, levels, radii))
            inner = outer - (14 if y in range(214, 242) or y >= 325 else 7)
            state = SILVER if y in [110, 111, 196, 197, 224, 225, 235, 236, 264, 265, 277, 278, 329, 330] else GRAY
            if 250 <= y <= 252:
                state = WSV
            if 270 <= y <= 274:
                state = BLACK
            ring_slice(part, y, outer, inner, state, start, end)
            if 266 <= y < 325:
                ring_slice(part, y, 136, 131, VENT if y % 7 > 1 else SILVER, start, end)
        for y in range(214, 220):
            ring_slice(part, y, 192, 88, BLACK if y < 218 else SILVER, start, end)
        for y in range(325, 331):
            ring_slice(part, y, 162, 131, GRAY if y < 329 else SILVER, start, end)
        for index in range(12):
            angle = start + (index + .5) * (end - start) / 12
            radial_box(part, 157, 166, -2, 2, 280, 326, angle, SILVER if index % 3 == 0 else STUDS)
            radial_box(part, 166, 169, -2, 2, 310, 324, angle, GRAY)
        for index in range(5):
            angle = start + (index + .5) * (end - start) / 5
            radial_box(part, 104, 114, -4, 4, 37, 164, angle, STUDS)
            radial_box(part, 113, 117, -2, 2, 50, 151, angle, BLUE)
        angle = (start + end) / 2
        for a, b, radius, state in [([168, 240, -14], [229, 258, -14], 6, STUDS), ([168, 240, 14], [229, 258, 14], 6, STUDS),
                                     ([170, 223, -13], [222, 258, -13], 5, SILVER), ([170, 223, 13], [222, 258, 13], 5, SILVER)]:
            part.beam(radial(*a, angle), radial(*b, angle), radius, state)
        radial_box(part, 201, 252, -21, 21, 258, 267, angle, BLACK)
        radial_box(part, 203, 249, -18, 18, 267, 271, angle, GRAY)
        radial_box(part, 220, 239, -12, 12, 272, 280, angle, VENT)
        radial_box(part, 249, 253, -17, 17, 263, 271, angle, SILVER)
        radial_box(part, 243, 246, -12, 12, 272, 274, angle, BLUE_LIGHT)
        parts.append(part.finish())
    for index in range(7):
        angle = np.pi / 2 + index * 2 * np.pi / 7
        part = Part(f'nozzle-blade-{index}', f'喷口径向导流叶片{index + 1}', group='engine')
        q = np.arange(-136, 137)
        z, x = np.meshgrid(q, q)
        u, v = x * np.cos(angle) + z * np.sin(angle), -x * np.sin(angle) + z * np.cos(angle)
        mask = (u >= 15) & (u <= 130) & (abs(v) <= (u - 12) * .24)
        xx, zz, uu, vv = x[mask], z[mask], u[mask], v[mask]
        yy = np.rint(267 + uu * .25).astype(int)
        for thickness in range(5):
            part.points(np.c_[xx, yy - thickness, zz], GRAY)
        edge = abs(vv) >= (uu - 12) * .24 - 3
        part.points(np.c_[xx[edge], yy[edge] + 1, zz[edge]], SILVER)
        line = abs(vv) < 2
        part.points(np.c_[xx[line], yy[line] + 1, zz[line]], BLUE_LIGHT)
        parts.append(part.finish())
    part = Part('plasma-injector', '中央点火轴与深部反应辉光', group='engine')
    for y in range(4, 299):
        ring_slice(part, y, 16 if y < 286 else 12, 0, COMPUTER if y < 280 else LIGHT if y > 294 else BLUE_LIGHT)
    for y in [186, 222, 265, 290]:
        ring_slice(part, y, 86 if y < 265 else 22, 80 if y < 265 else 17, BLUE_LIGHT)
    parts.append(part.finish())
    return parts


def legs():
    parts = []
    nodes = [177, 230, 320, 430, 530, 600]
    tops = [219, 214, 172, 90, 45, 28]
    for index in range(7):
        angle = np.pi / 2 + index * 2 * np.pi / 7
        part = Part(f'leg-{index}', f'放射斜腿与镂空桁架{index + 1}', group='engine')
        corners = np.array([radial(u, 0, v, angle) for u in [173, 604] for v in [-58, 58]])
        lo, hi = np.floor(corners.min(0)).astype(int), np.ceil(corners.max(0)).astype(int)
        z, x = np.mgrid[lo[2]:hi[2] + 1, lo[0]:hi[0] + 1]
        u, v = x * np.cos(angle) + z * np.sin(angle), -x * np.sin(angle) + z * np.cos(angle)
        width = 53 - np.clip((u - 177) / 423, 0, 1) * 14
        mask = (u >= 177) & (u <= 600) & (abs(v) <= width)
        xx, zz, uu, vv, ww = [a[mask] for a in [x, z, u, v, width]]
        yy = np.rint(np.interp(uu, nodes, tops)).astype(int)
        for depth in range(11):
            part.points(np.c_[xx, yy - depth, zz], GRAY if depth < 6 else BLACK)
        for selected, state in [(abs(vv) >= ww - 4, SILVER), (abs(vv) <= 7, VENT), (np.mod(uu - 178, 44) < 3, BLACK),
                                ((abs(vv - 16) < 1.5) & (uu < 565), WSV)]:
            part.points(np.c_[xx[selected], yy[selected] + 1, zz[selected]], state)
        radial_box(part, 557, 614, -65, 65, 7, 23, angle, BLACK)
        radial_box(part, 561, 612, -61, 61, 24, 29, angle, GRAY)
        radial_box(part, 573, 608, -51, 51, 30, 32, angle, SILVER)
        stations = np.linspace(183, 583, 9)
        heights = np.interp(stations, nodes, tops)
        lower = np.maximum(heights - 31, 12)
        widths = 53 - (stations - 177) / 423 * 14
        for side in [-1, 1]:
            for j in range(len(stations) - 1):
                a = radial(stations[j], lower[j], side * (widths[j] - 3), angle)
                b = radial(stations[j + 1], lower[j + 1], side * (widths[j + 1] - 3), angle)
                part.beam(a, b, 5, STUDS)
                a = radial(stations[j], heights[j] - 10, side * (widths[j] - 3), angle)
                b = radial(stations[j + 1], lower[j + 1], side * (widths[j + 1] - 3), angle)
                part.beam(a, b, 3, SILVER)
                a = radial(stations[j], heights[j] + 8, side * 29, angle)
                b = radial(stations[j + 1], heights[j + 1] + 8, side * 29, angle)
                part.beam(a, b, 4, BLUE if side < 0 else SILVER)
            for u0 in [239, 327, 415, 503, 573]:
                y0 = int(np.interp(u0, nodes, tops))
                radial_box(part, u0 - 9, u0 + 9, side * 39 - 8, side * 39 + 8, y0 - 12, y0 + 13, angle, STUDS)
                radial_box(part, u0 - 6, u0 + 6, side * 39 - 5, side * 39 + 5, y0 + 14, y0 + 17, angle, VENT)
                radial_box(part, u0 - 2, u0 + 2, side * 39 - 2, side * 39 + 2, y0 + 18, y0 + 18, angle, YELLOW)
        for j, u0 in enumerate([274, 366, 458, 548]):
            y0 = int(np.interp(u0, nodes, tops))
            radial_box(part, u0 - 13, u0 + 13, -18, 18, y0 - 12, y0 + 10, angle, GRAY)
            radial_box(part, u0 - 10, u0 + 10, -15, 15, y0 + 11, y0 + 12, angle, COMPUTER if j % 2 else VENT)
            radial_box(part, u0 - 15, u0 - 13, -21, 21, y0 + 6, y0 + 13, angle, SILVER)
        parts.append(part.finish())
    return parts


def service():
    part = Part('front-control', '正面主控检修平台', group='engine')
    for step in range(12):
        y = 8 + step * 3
        z = 648 - step * 3
        part.box([-17, y - 3, z - 2], [17, y, z + 1], GRAY)
    part.box([-23, 38, 599], [23, 42, 617], SILVER)
    part.box([-8, 43, 606], [8, 46, 610], COMPUTER)
    part.box([-10, 43, 611], [10, 43, 616], WSV)
    part.box(CONTROLLER, CONTROLLER, CONTROL)
    return [part.finish()]


def build():
    result = foundation()
    print('七辐底盘与外坝生成完成', flush=True)
    result += legs()
    print('七条装甲斜腿与桁架生成完成', flush=True)
    result += core() + service()
    return result
