import math

import numpy as np

import author_w05_wings_20261115 as original
from author_w05_shapes_20261115 import Part, GLASS, COIL, FRAME, IMPELLER, ARMOR


def reroute(points):
    points = np.array(points, float, copy=True)
    for z in original.TOWER_Z:
        offset = points[:, [0, 2]] - [175, z]
        radius = np.linalg.norm(offset, axis=1)
        selected = radius < 88
        expanded = 55 + 33 * (radius[selected] / 88) ** (88 / 33)
        points[np.ix_(selected, [0, 2])] = [175, z] + offset[selected] * (expanded / radius[selected])[:, None]
    # 后塔外侧原本贴近翼尖弧刃，管束向内轻收八格，避免绕塔后新增穿插。
    window = np.ones(len(points))
    for axis, center, width in ((0, 251, 29), (2, 175, 65), (1, 215, 65)):
        window *= .5 * (1 + np.cos(math.pi * np.clip((points[:, axis] - center) / width, -1, 1)))
    points[:, 0] -= 8 * window
    return points


def route(u, central=False):
    angle = np.linspace(0, 2 * math.pi if central else 4 * math.pi, 1400 if central else 2800)
    return reroute(np.c_[171 + (80 + u * np.cos(angle / 2)) * np.cos(angle),
                        164 + 62 * np.sin(angle) + u * np.sin(angle / 2),
                        10 + (228 + u * np.cos(angle / 2)) * np.sin(angle)])


def finish(part, side):
    result = part.finish()
    result.p[:, 0] *= side
    return result


def mobius(side):
    name = 'left' if side < 0 else 'right'
    p = Part(f'wing_{name}_mobius_network', f'{"左" if side < 0 else "右"}翼半扭转莫比乌斯环流管网',
             source='R3：原11路半扭转管网局部绕塔，管箍、灯线、流光同步',
             ribbon_center=[side * 171, 164, 10], half_twist=True,
             tower_reroute=dict(influence_radius=88, minimum_mapping_radius=55, outer_blade_inward_bend=8))
    paths = []
    for lane, u in enumerate(np.linspace(0, 20, 11)):
        points = route(u, lane == 0)
        original.solid_route(p, points, 2.1, GLASS)
        original.solid_route(p, points, .85, COIL)
        for t in np.linspace(0, len(points) - 10, 18 if lane == 0 else 36).astype(int):
            p.ring(points[t + 4], 3.1, 1, FRAME, points[t + 8] - points[t], 1.7)
        if lane in (0, 5, 10):
            flow = points[::5].copy()
            flow[:, 0] *= side
            paths.append(flow.round(3).tolist())
    for u in (-22.5, 22.5):
        original.solid_route(p, route(u), 1.5, FRAME)
    p.metadata['flow_paths'] = paths
    return finish(p, side)


def guide_blades(side):
    name = 'left' if side < 0 else 'right'
    old = original.guide_blades(1)
    p = Part(f'wing_{name}_guide_vanes', f'{"左" if side < 0 else "右"}翼倾斜导流百叶与冷凝桁架',
             source='R3：24片百叶随局部绕行管线安装，冲突叶片切向避让，底部桁架保持', blade_count=24)
    for state in np.unique(old.states):
        p.points(old.p[(old.p[:, 1] < 80) & (old.states == state)], int(state))
    pipe_routes = np.concatenate([route(u, u == 0) for u in np.linspace(0, 20, 11)])
    records = []
    for index in range(24):
        theta = 2 * math.pi * index / 24
        old_center = np.array([171 + 76 * math.cos(theta), 164 + 62 * math.sin(theta), 10 + 213 * math.sin(theta)])
        center = reroute([old_center])[0]
        inward = np.array([-math.cos(theta), -.2, -math.sin(theta)])
        along = np.array([-math.sin(theta), .35, math.cos(theta)])
        nearest_z = min(original.TOWER_Z, key=lambda z: np.linalg.norm(center[[0, 2]] - [175, z]))
        radial = center[[0, 2]] - [175, nearest_z]
        corners = np.array([center + inward * u + along * v for u in (-6, 6) for v in (-13, 13)])
        turned = corners[:, 1].min() < 214 and np.linalg.norm(corners[:, [0, 2]] - [175, nearest_z], axis=1).min() < 51
        if turned:
            radial /= np.linalg.norm(radial)
            tangent = np.array([-radial[1], radial[0]])
            tangent *= 1 if tangent @ along[[0, 2]] >= 0 else -1
            inward = np.array([-radial[0], -.2, -radial[1]])
            along = np.array([tangent[0], .35, tangent[1]])
        vertices = [center + inward * u + along * v + [0, h, 0]
                    for u in (-6, 6) for v in (-13, 13) for h in (-1, 1)]
        p.hull(vertices, IMPELLER)
        p.beam(center + inward * 6 - along * 13 + [0, 2, 0],
               center + inward * 6 + along * 13 + [0, 2, 0], .8, ARMOR)
        if np.linalg.norm(center - old_center) > .2 or turned:
            root = center - inward * 6
            anchor = pipe_routes[np.argmin(np.linalg.norm(pipe_routes - root, axis=1))]
            original.solid_route(p, [root, [root[0], anchor[1], root[2]], anchor], 1.2, FRAME)
            records.append(dict(index=index + 1, center=center.round(3).tolist(), turned=bool(turned),
                                mount=anchor.round(3).tolist()))
    p.metadata['revised_vanes'] = records
    return finish(p, side)
