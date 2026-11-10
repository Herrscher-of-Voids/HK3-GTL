# -*- coding: utf-8 -*-
"""I25 戴森天球解析中心：黑色世界泡与截角二十面体采样壳。"""
from __future__ import annotations

import collections
import itertools
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/structure_delivery"))
from structure_size_baseline import require

W, H, D = 251, 190, 251
CX, CZ = W // 2, D // 2
BUBBLE_RADIUS, DYSON_RADIUS = 42, 88
DYSON_FACE_THICKNESS = 5
QEV = "hk3gtl:voltage_machine_casing_qev"
PORT = "hk3gtl:industrial_port_casing"
CONTROL = "minecraft:diamond_block"
CLEAN = "gtceu:clean_machine_casing"
POWER = "gtceu:high_power_casing"
COMPUTER = "gtceu:advanced_computer_casing"
VENT = "gtceu:computer_heat_vent"
GRATE = "gtceu:assembly_line_grating"
ASSEMBLY = "gtceu:assembly_line_casing"
ATOMIC = "gtceu:atomic_casing"
ROBUST = "gtceu:robust_machine_casing"
SECURE = "gtceu:secure_maceration_casing"
TURBINE = "gtceu:stainless_steel_turbine_casing"
LASER = "gtceu:laser_safe_engraving_casing"
BLACK = "minecraft:black_concrete"
BLACK_GLASS = "minecraft:black_stained_glass"
CYAN = "minecraft:cyan_stained_glass"
ICE = "minecraft:light_blue_stained_glass"
PURPLE = "minecraft:purple_stained_glass"
AMETHYST = "minecraft:amethyst_block"
LIGHT = "minecraft:sea_lantern"
CELLS: dict[tuple[int, int, int], str] = {}


def put(x, y, z, state, replace=False):
    pos = (int(x), int(y), int(z))
    if not (0 <= pos[0] < W and 0 <= pos[1] < H and 0 <= pos[2] < D):
        raise ValueError(f"实体越界：{pos} {state}")
    if replace or pos not in CELLS:
        CELLS[pos] = state


def box(lo, hi, state, replace=False):
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                put(x, y, z, state, replace)


def beam(a, b, state, radius=0, replace=False):
    """用连续逐轴路径形成有实体厚度的梁。"""
    limits = (W, H, D)
    steps = max(abs(b[i] - a[i]) for i in range(3))
    last = tuple(a)
    for step in range(steps + 1):
        target = tuple(round(a[i] + (b[i] - a[i]) * step / max(1, steps)) for i in range(3))
        cursor = list(last)
        for axis in range(3):
            while cursor[axis] != target[axis]:
                cursor[axis] += 1 if target[axis] > cursor[axis] else -1
                lo = tuple(max(0, v - radius) for v in cursor)
                hi = tuple(min(limits[i] - 1, v + radius) for i, v in enumerate(cursor))
                box(lo, hi, state, replace)
        lo = tuple(max(0, v - radius) for v in target)
        hi = tuple(min(limits[i] - 1, v + radius) for i, v in enumerate(target))
        box(lo, hi, state, replace)
        last = target


def points(a, b):
    steps = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
    result = []
    for step in range(steps + 1):
        point = (round(a[0] + (b[0] - a[0]) * step / max(1, steps)),
                 round(a[1] + (b[1] - a[1]) * step / max(1, steps)))
        if not result or result[-1] != point:
            result.append(point)
    return result


def points3d(a, b):
    steps = max(abs(b[i] - a[i]) for i in range(3))
    result = [tuple(a)]
    last = tuple(a)
    for step in range(steps + 1):
        target = tuple(round(a[i] + (b[i] - a[i]) * step / max(1, steps)) for i in range(3))
        cursor = list(last)
        for axis in range(3):
            while cursor[axis] != target[axis]:
                cursor[axis] += 1 if target[axis] > cursor[axis] else -1
                result.append(tuple(cursor))
        last = target
    return result


def octagon(x0, x1, z0, z1, cut):
    return [(x0 + cut, z0), (x1 - cut, z0), (x1, z0 + cut), (x1, z1 - cut),
            (x1 - cut, z1), (x0 + cut, z1), (x0, z1 - cut), (x0, z0 + cut)]


def shrink(poly, amount):
    cx = sum(x for x, _ in poly) / len(poly)
    cz = sum(z for _, z in poly) / len(poly)
    return [(round(x + (cx - x) * amount / max(1, max(cx, cz))),
             round(z + (cz - z) * amount / max(1, max(cx, cz)))) for x, z in poly]


def inside(poly, x, z):
    hit = False
    j = len(poly) - 1
    for i, (xi, zi) in enumerate(poly):
        xj, zj = poly[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / ((zj - zi) or 1e-9) + xi:
            hit = not hit
        j = i
    return hit


def draw_polygon(poly, y, state, radius=0):
    for a, b in zip(poly, poly[1:] + poly[:1]):
        beam((a[0], y, a[1]), (b[0], y, b[1]), state, radius)


def fill_polygon(poly, y, state, edge_state=None):
    for x in range(min(p[0] for p in poly), max(p[0] for p in poly) + 1):
        for z in range(min(p[1] for p in poly), max(p[1] for p in poly) + 1):
            if inside(poly, x, z):
                if edge_state and any(abs(x - px) <= 1 and abs(z - pz) <= 1 for px, pz in poly):
                    put(x, y, z, edge_state)
                else:
                    put(x, y, z, state)


def regular_polygon(radius, sides, rotation=0):
    return [(round(CX + radius * math.cos(math.radians(rotation + 360 * i / sides))),
             round(CZ + radius * math.sin(math.radians(rotation + 360 * i / sides)))) for i in range(sides)]


def polygon_band(inner, outer, y, state, sides, rotation):
    outside = regular_polygon(outer, sides, rotation)
    inside_poly = regular_polygon(inner, sides, rotation)
    for x in range(min(p[0] for p in outside), max(p[0] for p in outside) + 1):
        for z in range(min(p[1] for p in outside), max(p[1] for p in outside) + 1):
            if inside(outside, x, z) and not inside(inside_poly, x, z):
                put(x, y, z, state, True)
    draw_polygon(outside, y, QEV)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def normalize(vector):
    length = math.sqrt(dot(vector, vector))
    return tuple(value / length for value in vector)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scale(vector, factor):
    return tuple(value * factor for value in vector)


def ordered_polygon(vertices, normal):
    center = tuple(sum(point[axis] for point in vertices) / len(vertices) for axis in range(3))
    normal = normalize(normal)
    reference = normalize(subtract(vertices[0], center))
    tangent = cross(normal, reference)
    ordered = sorted(vertices, key=lambda point: math.atan2(dot(subtract(point, center), tangent),
                                                            dot(subtract(point, center), reference)))
    if dot(cross(subtract(ordered[1], ordered[0]), subtract(ordered[2], ordered[1])), normal) < 0:
        ordered.reverse()
    return ordered, normal


def rotate_to(vector, source, target):
    source, target = normalize(source), normalize(target)
    axis = cross(source, target)
    sine = math.sqrt(dot(axis, axis))
    cosine = max(-1.0, min(1.0, dot(source, target)))
    if sine < 1e-9:
        if cosine > 0:
            return vector
        axis = normalize(cross(source, (1, 0, 0) if abs(source[0]) < 0.9 else (0, 1, 0)))
        return subtract(scale(axis, 2 * dot(axis, vector)), vector)
    axis = scale(axis, 1 / sine)
    return add(add(scale(vector, cosine), scale(cross(axis, vector), sine)),
               scale(axis, dot(axis, vector) * (1 - cosine)))


def truncated_icosahedron():
    """从正二十面体截去顶点三分之一，得到12五边形与20六边形。"""
    phi = (1 + math.sqrt(5)) / 2
    vertices = []
    for a, b in itertools.product((-1, 1), repeat=2):
        vertices.extend(((0, a, b * phi), (a, b * phi, 0), (b * phi, 0, a)))
    vertices = [normalize(vertex) for vertex in vertices]
    distances = {(i, j): dot(subtract(vertices[i], vertices[j]), subtract(vertices[i], vertices[j]))
                 for i in range(len(vertices)) for j in range(i + 1, len(vertices))}
    edge_sq = min(distances.values())
    triangles = [face for face in itertools.combinations(range(len(vertices)), 3)
                 if all(abs(distances[tuple(sorted(pair))] - edge_sq) < 1e-7
                        for pair in itertools.combinations(face, 2))]
    assert len(vertices) == 12 and len(triangles) == 20
    neighbors = {i: {j for pair in distances for j in pair if i in pair and j != i and
                     abs(distances[tuple(sorted((i, j)))] - edge_sq) < 1e-7}
                 for i in range(len(vertices))}
    directed = {(i, j): add(scale(vertices[i], 2 / 3), scale(vertices[j], 1 / 3))
                for i, j in distances if abs(distances[i, j] - edge_sq) < 1e-7
                for i, j in ((i, j), (j, i))}
    faces = []
    for i, adjacent in neighbors.items():
        points = [directed[i, j] for j in adjacent]
        polygon, normal = ordered_polygon(points, vertices[i])
        faces.append({"kind": "五边形", "vertices": polygon, "normal": normal})
    for triangle in triangles:
        center = tuple(sum(vertices[i][axis] for i in triangle) / 3 for axis in range(3))
        a, b, c = (vertices[i] for i in triangle)
        normal = cross(subtract(b, a), subtract(c, a))
        if dot(normal, center) < 0:
            normal = scale(normal, -1)
        points = [directed[i, j] for i, j in itertools.permutations(triangle, 2)]
        polygon, normal = ordered_polygon(points, normal)
        faces.append({"kind": "六边形", "vertices": polygon, "normal": normal})

    vertex_radius = math.sqrt(dot(faces[0]["vertices"][0], faces[0]["vertices"][0]))
    target = normalize((-1, 1, -1))
    source = faces[12]["normal"]
    for face in faces:
        face["normal"] = rotate_to(face["normal"], source, target)
        face["vertices"] = [scale(rotate_to(point, source, target), DYSON_RADIUS / vertex_radius)
                            for point in face["vertices"]]
    assert [sum(face["kind"] == kind for face in faces) for kind in ("五边形", "六边形")] == [12, 20]
    return faces


def fill_facet(vertices, normal, state, thickness):
    """将一个平面多边形面板体素化为实体厚板。"""
    normal = normalize(normal)
    origin = vertices[0]
    half = thickness / 2
    bounds = [(math.floor(min(point[axis] for point in vertices) - half - 1),
               math.ceil(max(point[axis] for point in vertices) + half + 1)) for axis in range(3)]
    edges = [(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]
    for x in range(bounds[0][0], bounds[0][1] + 1):
        for y in range(bounds[1][0], bounds[1][1] + 1):
            for z in range(bounds[2][0], bounds[2][1] + 1):
                point = (x, y, z)
                relative = subtract(point, origin)
                if abs(dot(relative, normal)) > half:
                    continue
                if all(dot(cross(subtract(b, a), subtract(point, a)), normal) >= -0.75
                       for a, b in edges):
                    put(round(CX + x), round(H // 2 + y), round(CZ + z), state)


def chamber(x0, x1, z0, z1, height, cut, tag):
    """错角舱体：厚边、玻璃观察带、分层顶盖与可见内仪器。"""
    poly = octagon(x0, x1, z0, z1, cut)
    draw_polygon(poly, 0, QEV)
    for x, z in poly:
        beam((x, 1, z), (x, height - 5, z), QEV)

    interior_x = (x0 + x1) // 2
    interior_z = (z0 + z1) // 2
    service_casing = {1: ASSEMBLY, 2: ATOMIC, 3: LASER, 4: TURBINE, 5: SECURE}[tag]
    if x1 - x0 > z1 - z0:
        beam((x0, 0, interior_z), (x1, 0, interior_z), GRATE, 1)
    else:
        beam((interior_x, 0, z0), (interior_x, 0, z1), GRATE, 1)

    for edge_index, (a, b) in enumerate(zip(poly, poly[1:] + poly[:1])):
        line = points(a, b)
        horizontal = a[1] == b[1]
        for index, (x, z) in enumerate(line):
            for y in range(1, height - 3):
                corner = index in (0, len(line) - 1)
                belt = y in (4, 5, 10, 11, height - 7)
                window = (4 <= y <= 8 or 13 <= y <= 17 or
                          (height > 27 and 21 <= y <= 24))
                if corner or belt or index % 11 == 0:
                    state = QEV if y % 3 else POWER
                    if belt and index % 11 == 0:
                        state = service_casing
                elif window and 2 <= index < len(line) - 2:
                    state = CYAN if (index + edge_index + tag) % 4 else ICE
                else:
                    state = CLEAN if (index + y + tag) % 3 else COMPUTER
                put(x, y, z, state)
                if horizontal:
                    interior = z + (1 if z == z0 else -1)
                    if 0 <= interior < D and index % 6 == 1:
                        put(x, y, interior, state)
                else:
                    interior = x + (1 if x == x0 else -1)
                    if 0 <= interior < W and index % 6 == 1:
                        put(interior, y, z, state)

    # 设备舱顶部改用错开的坐标梁与局部观察窗，不再铺成大片屋顶。
    for tier in range(3):
        roof_poly = poly if tier == 2 else shrink(poly, tier * 2)
        y = height - 3 + tier
        draw_polygon(roof_poly, y, QEV if tier != 1 else POWER)
    xmid = (x0 + x1) // 2
    zmid = (z0 + z1) // 2
    beam((x0, height - 1, zmid), (x1, height - 1, zmid), POWER)
    beam((xmid, height - 1, z0), (xmid, height - 1, z1), CYAN)

    # 内部计算柜靠近玻璃带布置，避免设备只剩外壳。
    for offset in (-6, 0, 6):
        x = interior_x + offset
        z = interior_z + (2 if tag % 2 else -2)
        if x - 1 >= x0 + 3 and x + 1 <= x1 - 3 and z - 1 >= z0 + 3 and z + 1 <= z1 - 3:
            if x1 - x0 > z1 - z0:
                beam((x, 0, z), (x, 0, interior_z), GRATE)
            else:
                beam((x, 0, z), (interior_x, 0, z), GRATE)
            beam((x, 0, z), (x, 2, z), COMPUTER)
            box((x - 1, 2, z - 1), (x + 1, min(11, height - 6), z + 1), service_casing)
            box((x - 1, min(12, height - 5), z - 1), (x + 1, min(12, height - 5), z + 1), VENT)


def world_bubble():
    """以等径黑色正球作为世界泡本体。"""
    cy, radius = H // 2, BUBBLE_RADIUS
    for x in range(CX - radius, CX + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            for z in range(CZ - radius, CZ + radius + 1):
                distance = (x - CX) ** 2 + (y - cy) ** 2 + (z - CZ) ** 2
                if (radius - 2.4) ** 2 <= distance <= radius ** 2:
                    put(x, y, z, BLACK_GLASS if distance > (radius - 0.8) ** 2 else BLACK, True)
    # 黑色球面保持完整，用背侧测量轴固定，正面只显露深色宇宙样本。


def suspend_world_bubble():
    """以背侧单轴承托世界泡，避免支架进入正面观测视线。"""
    center = (CX, H // 2, CZ)
    back = scale(normalize((-1, 1, -1)), -1)
    shell = []
    for pos, state in CELLS.items():
        relative = subtract(pos, center)
        distance = math.sqrt(dot(relative, relative))
        if 70 <= distance <= DYSON_RADIUS + 2 and dot(relative, back) > 70 and state in (QEV, ROBUST):
            shell.append(pos)
    target = max(shell, key=lambda pos: dot(subtract(pos, center), back))
    direction = normalize(subtract(target, center))
    surface = tuple(round(center[i] + direction[i] * BUBBLE_RADIUS) for i in range(3))
    beam(surface, target, QEV, 1, True)
    return list(target)


def outer_research_center():
    """实体化截角二十面体，并把采能节点接入多边形研究平台。"""
    center_y = H // 2
    faces = truncated_icosahedron()
    view = normalize((-1, 1, -1))
    aperture = {i for i, face in enumerate(faces) if dot(face["normal"], view) >= 0.7}
    assert len(faces) == 32 and len(aperture) == 7

    def world_point(point):
        return (round(CX + point[0]), round(center_y + point[1]), round(CZ + point[2]))

    shell_edges = set()
    for index, face in enumerate(faces):
        if index in aperture:
            continue
        vertices = face["vertices"]
        panel = ASSEMBLY if face["kind"] == "五边形" else ROBUST
        fill_facet(vertices, face["normal"], panel, DYSON_FACE_THICKNESS)
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            shell_edges.add(tuple(sorted((world_point(a), world_point(b)))))
    for a, b in shell_edges:
        beam(a, b, QEV, 1, True)

    energy_faces = [face for i, face in enumerate(faces)
                    if i not in aperture and face["kind"] == "五边形" and
                    abs(dot(face["normal"], view)) <= 0.25]
    assert len(energy_faces) == 6
    energy_nodes = []
    for face in energy_faces:
        vertices = face["vertices"]
        center = tuple(sum(point[axis] for point in vertices) / len(vertices) for axis in range(3))
        node = world_point(center)
        assert CELLS.get(node) == ASSEMBLY, node
        outside = world_point(add(center, scale(face["normal"], 3)))
        energy_nodes.append({"panel": list(node), "receiver": list(outside)})

    zenith = world_point(max((point for face in faces for point in face["vertices"]), key=lambda p: p[1]))
    beam(zenith, (zenith[0], H - 1, zenith[2]), QEV, 1)

    candidates = [(x, y, z) for x, y, z in CELLS
                  if 5 < y < center_y - 10 and BUBBLE_RADIUS + 10 <= math.hypot(x - CX, z - CZ) <= DYSON_RADIUS + 4]
    supports = []
    for angle in range(0, 360, 60):
        target = math.radians(angle)
        point = max(candidates, key=lambda p: (math.cos(math.atan2(p[2] - CZ, p[0] - CX) - target),
                                               -p[1]))
        candidates.remove(point)
        supports.append(point)

    # 六层十二边裙座接研究环廊；内侧六边承轴座沿同一组径向支柱落地。
    for y, inner, outer, material in ((0, 110, 125, QEV), (1, 110, 125, ASSEMBLY),
                                      (2, 110, 125, QEV), (3, 110, 125, ASSEMBLY),
                                      (4, 110, 125, ROBUST), (5, 110, 125, QEV),
                                      (2, 96, 110, QEV), (3, 82, 96, ROBUST),
                                      (4, 68, 82, QEV), (5, 54, 68, ASSEMBLY)):
        polygon_band(inner, outer, y, material, 12, 15)
    for y, inner, outer, material in ((6, 50, 62, QEV), (7, 50, 62, ASSEMBLY),
                                      (8, 40, 50, QEV), (9, 30, 40, ROBUST),
                                      (10, 20, 30, QEV), (11, 10, 20, ASSEMBLY)):
        polygon_band(inner, outer, y, material, 6, 0)
    for y in range(0, 19):
        fill_polygon(regular_polygon(10, 6), y, QEV)

    for x, y, z in supports:
        beam((CX, 5, CZ), (x, 5, z), QEV, 1)
        beam((x, 5, z), (x, y, z), QEV, 1)
    for angle, support in zip(range(0, 360, 60), supports):
        radians = math.radians(angle)
        station = (round(CX + 104 * math.cos(radians)), round(CZ + 104 * math.sin(radians)))
        beam((station[0], 2, station[1]), (support[0], 2, support[2]), QEV)
    return {"shape": "截角二十面体", "pentagonal_faces": 12, "hexagonal_faces": 20,
            "observation_aperture_faces": len(aperture), "panel_faces": len(faces) - len(aperture),
            "energy_nodes": energy_nodes, "support_points": [list(point) for point in supports],
            "research_platform": {"outer_sides": 12, "raised_outer_rim_layers": 6,
                                  "inner_bearing_sides": 6, "radial_supports": len(supports),
                                  "instrument_bays": 6, "instrument_bay_shape": "八边形"}}


def energy_transfer(nodes):
    """以青蓝玻璃整块导束静态表示世界泡能量进入六个采集节点。"""
    center = (CX, H // 2, CZ)
    channels = []
    for item in nodes:
        receiver = tuple(item["receiver"])
        direction = normalize(subtract(receiver, center))
        distance = math.sqrt(dot(subtract(receiver, center), subtract(receiver, center)))
        start = tuple(round(center[i] + direction[i] * (BUBBLE_RADIUS + 1)) for i in range(3))
        beam(start, receiver, CYAN, replace=True)
        points = points3d(start, receiver)
        for index, pos in enumerate(points):
            if index and index % 7 == 0:
                put(*pos, ICE, True)
        put(*receiver, LIGHT, True)
        channels.append({"start": list(start), "receiver": list(receiver), "blocks": len(points),
                         "ice_pulses": sum(index > 0 and index % 7 == 0 for index in range(len(points)))})
    return {"channels": channels, "count": len(channels), "effect": "static_cyan_to_ice_energy_guides"}


def cradle():
    """五座分析舱和六座八边仪器舱接入同一研究平台。"""
    for start, end in (((CX, 5, 5), (CX, 5, CZ - 80)),
                       ((12, 5, CZ), (CX - 80, 5, CZ)),
                       ((W - 13, 5, CZ), (CX + 80, 5, CZ)),
                       ((CX - 12, 5, D - 13), (CX - 12, 5, CZ + 80)),
                       ((CX + 12, 5, D - 13), (CX + 12, 5, CZ + 80))):
        beam(start, end, QEV, 1)
    for angle in range(0, 360, 60):
        radians = math.radians(angle)
        x, z = round(CX + 104 * math.cos(radians)), round(CZ + 104 * math.sin(radians))
        footprint = octagon(x - 5, x + 5, z - 5, z + 5, 3)
        fill_polygon(footprint, 2, ROBUST)
        draw_polygon(footprint, 2, QEV)
        for y in range(4, 9):
            draw_polygon(footprint, y, QEV if y in (4, 8) else ASSEMBLY)
        for px, pz in footprint:
            box((px - 1, 4, pz - 1), (px + 1, 9, pz + 1), ATOMIC)
        box((x - 1, 3, z - 1), (x + 1, 7, z + 1), COMPUTER, True)
        box((x - 2, 8, z - 2), (x + 2, 8, z + 2), ROBUST, True)
        put(x, 9, z, VENT, True)
        put(x, 10, z, LIGHT, True)


def socket(pos, face, marker):
    x, y, z = pos
    directions = {"north": (0, 0, -1), "south": (0, 0, 1),
                  "west": (-1, 0, 0), "east": (1, 0, 0)}
    dx, dy, dz = directions[face]
    if face in ("north", "south"):
        cross = [(x - 1, y, z), (x + 1, y, z), (x, y - 1, z), (x, y + 1, z)]
    else:
        cross = [(x, y - 1, z), (x, y + 1, z), (x, y, z - 1), (x, y, z + 1)]
    for p in cross:
        put(*p, QEV, True)
    put(x - dx, y - dy, z - dz, COMPUTER, True)
    put(x, y, z, marker, True)


def build():
    CELLS.clear()
    # 五座端舱接入球体采样、参照校验和坐标记录工位。
    chamber(CX - 8, CX + 8, 0, 7, 15, 3, 1)
    chamber(0, 16, CZ - 8, CZ + 8, 21, 4, 2)
    chamber(W - 17, W - 1, CZ - 8, CZ + 8, 27, 4, 3)
    chamber(CX - 24, CX - 8, D - 17, D - 1, 19, 4, 4)
    chamber(CX + 8, CX + 24, D - 17, D - 1, 19, 4, 5)
    world_bubble()
    dyson_geometry = outer_research_center()
    energy_extraction = energy_transfer(dyson_geometry["energy_nodes"])
    bubble_anchor = suspend_world_bubble()
    cradle()

    # 输入、校验、结果端口及主控均直接嵌入设备舱端壳。
    controller = [CX, 5, 0]
    socket(controller, "north", CONTROL)
    port_defs = [
        {"id": "SPECTRA-IN", "pos": [CX + 3, 5, 0], "face": "north", "purpose": "I24异常谱与观测载荷输入"},
        {"id": "REFERENCE-IN", "pos": [0, 10, CZ], "face": "west", "purpose": "参照样本与坐标漂移校准输入"},
        {"id": "PHASE-IN", "pos": [W - 1, 13, CZ], "face": "east", "purpose": "I44增强信号与相位拟合输入"},
        {"id": "VALID-OUT", "pos": [CX - 12, 8, D - 1], "face": "south", "purpose": "有效坐标记录输出"},
        {"id": "INVALID-OUT", "pos": [CX + 12, 8, D - 1], "face": "south", "purpose": "失效坐标与误差记录输出"},
    ]
    for port in port_defs:
        socket(port["pos"], port["face"], PORT)

    blocks = [{"pos": list(pos), "state": state}
              for pos, state in sorted(CELLS.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))]
    zones = [
        {"name": "黑色世界泡正球", "min": [CX - BUBBLE_RADIUS, H // 2 - BUBBLE_RADIUS, CZ - BUBBLE_RADIUS], "max": [CX + BUBBLE_RADIUS, H // 2 + BUBBLE_RADIUS, CZ + BUBBLE_RADIUS], "pos": [CX, H // 2, CZ],
         "description": "85×85×85等径黑色世界泡代表待分析的微型宇宙；深色实体内壳与黑玻璃表层共同形成完整球面。"},
        {"name": "截角二十面体戴森采样壳", "min": [CX - 89, H // 2 - 89, CZ - 89], "max": [CX + 89, H // 2 + 89, CZ + 89], "pos": [CX, H // 2, CZ],
         "description": "12个五边形测量节点与20个六边形屏蔽面组成截角二十面体；正面七面留作连续观测口，QEV铜色棱梁勾勒拼接，深钢灰五边形与浅钢灰六边形分担校准和屏蔽。"},
        {"name": "六边轴承座与十二边研究环廊", "min": [0, 0, 0], "max": [W - 1, 42, D - 1], "pos": [CX, 7, CZ],
         "description": "六边形分层轴承座承接六根外壳支柱；十二边形研究裙座与环廊形成承载平台，六座八边仪器舱及五座分析舱由短廊接入。"},
        {"name": "居中谱线入口与主控舱", "min": [CX - 8, 0, 0], "max": [CX + 8, 15, 7], "pos": [CX, 7, 4],
         "description": "窄入口舱锁定在整宽中线，主控与异常谱输入并列嵌在北向端壳。"},
        {"name": "西侧参照与漂移校准舱", "min": [0, 0, CZ - 8], "max": [16, 21, CZ + 8], "pos": [8, 10, CZ],
         "description": "参照样本和漂移档案位于西侧端舱，接口与维护廊壳面齐平。"},
        {"name": "东侧相位拟合舱", "min": [W - 17, 0, CZ - 8], "max": [W - 1, 27, CZ + 8], "pos": [W - 9, 13, CZ],
         "description": "相位拟合舱在东侧端舱独立布置，与参照输入分线校验。"},
        {"name": "南侧有效坐标记录舱", "min": [CX - 24, 0, D - 17], "max": [CX - 8, 19, D - 1], "pos": [CX - 16, 8, D - 9],
         "description": "有效坐标沿南侧西支舱单独记录并输出。"},
        {"name": "南侧失效与误差记录舱", "min": [CX + 8, 0, D - 17], "max": [CX + 24, 19, D - 1], "pos": [CX + 16, 8, D - 9],
         "description": "失效坐标与误差记录沿南侧东支舱单独输出。"},
    ]
    return {
        "key": "i25", "name": "hk3gtl-i25-world-bubble-singularity-cutaway-20261025",
        "title": "世界泡坐标解析中心·戴森天球解析仪",
        "candidate_version": "黑色世界泡与戴森天球重制候选・待审",
        "world_bubble_diameter": BUBBLE_RADIUS * 2 + 1,
        "dyson_shell_radius": DYSON_RADIUS,
        "dyson_shell_geometry": dyson_geometry,
        "world_bubble_anchor": bubble_anchor, "energy_extraction": energy_extraction,
        "size": [W, H, D], "blocks": blocks, "block_count": len(blocks),
        "controller": controller, "controller_face": "north", "controller_surface": QEV,
        "ports": port_defs, "zones": zones,
        "paths": [{"name": "十二边研究裙座、研究环廊与六向承轴通道", "min": [0, 0, 0], "max": [W - 1, 11, D - 1]}],
        "description": "黑色正球世界泡由背侧测量承轴悬于截角二十面体戴森采样壳中央；六条青蓝静态导束从球面延伸至五边形采集节点，12个五边形与20个六边形沿铜色棱梁拼接，六边轴承座、十二边研究环廊与五座分析舱构成同一设施。",
        "target_voltage_appearance": "QEV/V07，按电压映射方案制作。",
        "function_boundary": "I24异常谱与I44增强信号进入；I25只输出有效坐标记录或无效/误差记录，实际锁定仍由I44负责。",
    }


def audit(data):
    size = require(data)
    occupied = {tuple(block["pos"]): block["state"] for block in data["blocks"]}
    assert size["actual_xyz"] == data["size"] and size["min_pos"] == [0, 0, 0]
    geometry = data["dyson_shell_geometry"]
    assert (geometry["shape"], geometry["pentagonal_faces"], geometry["hexagonal_faces"],
            geometry["observation_aperture_faces"], geometry["panel_faces"]) == ("截角二十面体", 12, 20, 7, 25)
    assert geometry["support_points"] and len(geometry["support_points"]) == 6
    assert geometry["research_platform"] == {"outer_sides": 12, "raised_outer_rim_layers": 6,
                                               "inner_bearing_sides": 6, "radial_supports": 6,
                                               "instrument_bays": 6, "instrument_bay_shape": "八边形"}
    assert data["energy_extraction"]["count"] == 6
    for channel in data["energy_extraction"]["channels"]:
        points = points3d(tuple(channel["start"]), tuple(channel["receiver"]))
        assert occupied[tuple(channel["receiver"])] == LIGHT
        assert all(occupied.get(point) in (CYAN, ICE, LIGHT) for point in points), channel
    assert occupied[tuple(data["world_bubble_anchor"])] == QEV
    remain = set(occupied)
    components = []
    offsets = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    while remain:
        stack = [remain.pop()]
        count = 0
        while stack:
            x, y, z = stack.pop()
            count += 1
            for dx, dy, dz in offsets:
                pos = (x + dx, y + dy, z + dz)
                if pos in remain:
                    remain.remove(pos)
                    stack.append(pos)
        components.append(count)
    assert len(components) == 1, components
    faces = {"north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0)}
    marker_checks = []
    for item in [*data["ports"], {"id": "CONTROLLER", "pos": data["controller"], "face": "north"}]:
        x, y, z = item["pos"]
        dx, dy, dz = faces[item["face"]]
        if dz:
            neighbors = [(x + sx, y + sy, z) for sx, sy in ((-1, 0), (1, 0), (0, -1), (0, 1))]
        else:
            neighbors = [(x, y + sy, z + sz) for sy, sz in ((-1, 0), (1, 0), (0, -1), (0, 1))]
        assert sum(occupied.get(pos) == QEV for pos in neighbors) == 4, item
        inner = (x - dx, y - dy, z - dz)
        assert occupied.get(inner) in (COMPUTER, QEV), (item, inner, occupied.get(inner))
        for depth in range(1, 5):
            assert (x + dx * depth, y, z + dz * depth) not in occupied, (item, depth)
        marker_checks.append({"id": item["id"], "pos": item["pos"], "same_shell_neighbors": 4,
                              "inner_backed": True, "outside_clear_depth": 4})
    assert data["controller"][0] == CX and CX == W // 2
    counts = collections.Counter(occupied.values())
    assert counts[CONTROL] == 1 and counts[PORT] == 5
    casing_states = (CLEAN, POWER, COMPUTER, VENT, GRATE)
    assert counts[QEV] > max(counts[state] for state in casing_states)
    glass_states = (CYAN, ICE, PURPLE, BLACK_GLASS)
    glass_count = sum(counts[state] for state in glass_states)
    outer_qev_count = sum(state == QEV and (x - CX) ** 2 + (z - CZ) ** 2 >= 40 ** 2
                          for (x, y, z), state in occupied.items())
    assert outer_qev_count > glass_count, (outer_qev_count, glass_count)
    assert len(occupied) > 522531 and len(counts) > 18
    assert H > 155 and W * D * H > 271 * 233 * 155
    floor_ratio = sum(y == 0 for x, y, z in occupied) / (W * D)
    assert floor_ratio < 0.48
    bubble_shell = sum(1 for (x, y, z), state in occupied.items()
                       if state in (BLACK, BLACK_GLASS) and
                       (x - CX) ** 2 + (y - H // 2) ** 2 + (z - CZ) ** 2 <= BUBBLE_RADIUS ** 2)
    assert bubble_shell >= 5000, bubble_shell
    return {
        "passed": True, "blocks": len(occupied), "size_check": size, "component_count": 1,
        "palette": dict(counts.most_common()), "port_count": len(data["ports"]), "marker_checks": marker_checks,
        "dyson_shell_geometry": data["dyson_shell_geometry"],
        "world_bubble_anchor": data["world_bubble_anchor"],
        "controller_ordinal": CX + 1, "floor_coverage_ratio": round(floor_ratio, 4), "bubble_shell_blocks": bubble_shell,
        "glass_blocks": glass_count, "outer_qev_shell_blocks": outer_qev_count,
        "lower_tier_max_benchmark": {"structure": "I20 V05", "block_count": 522531,
                                     "materials": 14, "size_wdh": [271, 233, 155]},
        "checks": [
            "黑色正球由背侧QEV承轴悬接截角二十面体；六条青蓝静态导束连接球面与五边形采集节点，正面七面观测口保留视线。",
            "QEV外壳块数严格多于含黑玻璃在内的全部玻璃；四项量化规模超过全部较低阶结构。",
            "六层十二边研究裙座、六边轴承座、六座八边仪器舱与五座分析舱连续连接；主控位于整宽251的第126格，接口齐平嵌入端舱壳体。",
            "主控与接口四邻为原QEV壳、内侧有计算背板、外侧连续四格净空。",
            "只使用QEV主体、工业接口、钻石主控及已核对的整块辅助方块。",
        ],
        "not_verified": ["正式Controller/Pattern、实际电压能力、端口注册与配方。", "游戏内成型、运行、2.9.2兼容性。", "材料生存获取与研究解锁。"],
        "paste_y": -60, "highest_world_y": -60 + H - 1,
    }


if __name__ == "__main__":
    result = audit(build())
    print({"blocks": result["blocks"], "size": result["size_check"], "palette": result["palette"],
           "bubble_shell_blocks": result["bubble_shell_blocks"]})
