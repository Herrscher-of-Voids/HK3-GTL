import math

import numpy as np

from w09_common_20261116 import Part, ARMOR, DARK, GOLD, WHITE, RED, LIGHT, CRIMSON, HOT
from w08_common_20261116 import rod


def truss(part, start, end, side, width=6):
    a, b = np.asarray(start, float), np.asarray(end, float)
    offset = np.asarray(side, float) * width
    for sign in (-1, 1):
        rod(part, a + sign * offset, b + sign * offset, 3, ARMOR)
        rod(part, a + sign * offset + [0, 3, 0], b + sign * offset + [0, 3, 0], 1, GOLD)
    points = a + np.linspace(0, 1, 9)[:, None] * (b - a)
    for index, (c, d) in enumerate(zip(points[:-1], points[1:])):
        rod(part, c - offset, c + offset, 2, WHITE)
        rod(part, c + offset * (-1) ** index, d - offset * (-1) ** index, 1.5, RED)


def finish(part, features):
    part.metadata.update(features=features, exclusive_hatch_positions=[])
    return part.finish()


def matrix():
    parts = []
    angles = np.arange(8) * math.pi / 4
    outer = np.c_[410 * np.cos(angles), np.full(8, -363), 410 * np.sin(angles)]
    inner = np.c_[225 * np.cos(angles), np.full(8, -363), 225 * np.sin(angles)]
    for name, label, polygon in [('outer', '外', outer), ('inner', '内', inner)]:
        for index, (a, b) in enumerate(zip(polygon, np.roll(polygon, -1, axis=0)), 1):
            frame = Part(f'fusion_bagua_{name}_{index}', f'八卦矩阵{label}环第{index}段黑金桁架',
                         section='industry', outer_radius=420, central_open_radius=199)
            rod(frame, a, b, 8, ARMOR)
            rod(frame, a + [0, -39, 0], b + [0, -39, 0], 7, ARMOR)
            rod(frame, a + [0, 8, 0], b + [0, 8, 0], 2, GOLD)
            rod(frame, a + [0, -45, 0], b + [0, -45, 0], 2, GOLD)
            for t in np.linspace(0, 1, 6):
                p = a + (b - a) * t
                rod(frame, p + [0, -36, 0], p, 2.5, DARK)
            for index in range(5):
                a0 = a + (b - a) * index / 5
                b0 = a + (b - a) * (index + 1) / 5
                rod(frame, a0 + [0, -36 * (index % 2), 0],
                    b0 + [0, -36 * (1 - index % 2), 0], 2, WHITE)
            parts.append(finish(frame, ['双层八角梁以立柱和交错白瓷斜撑连接，梁间完全开放。']))
    for index, (angle, a, b) in enumerate(zip(angles, inner, outer), 1):
        frame = Part(f'fusion_bagua_radial_{index}', f'八卦矩阵第{index}道径向工艺桁架', section='industry')
        side = [-math.sin(angle), 0, math.cos(angle)]
        truss(frame, a + [0, -17, 0], b + [0, -17, 0], side, 9)
        for radius in (243, 320, 391):
            center = np.array([radius * math.cos(angle), -360, radius * math.sin(angle)])
            rod(frame, center - np.array(side) * 13, center + np.array(side) * 13, 3, GOLD)
        parts.append(finish(frame, ['双轨径向梁连接内外八角框，金色横夹分隔三段工位。']))
    trigrams = [[1, 1, 1], [0, 0, 0], [1, 0, 0], [0, 1, 1],
                [0, 1, 0], [1, 0, 1], [0, 0, 1], [1, 1, 0]]
    for index, (angle, lines) in enumerate(zip(angles, trigrams), 1):
        glyphs = Part(f'fusion_bagua_lines_{index}', f'第{index}组三爻机械导轨',
                      section='industry', trigram_inner_to_outer=lines)
        radial = np.array([math.cos(angle), 0, math.sin(angle)])
        tangent = np.array([-math.sin(angle), 0, math.cos(angle)])
        for row, solid in enumerate(lines):
            center = radial * (364 + row * 18) + [0, -344, 0]
            intervals = [(-41, 41)] if solid else [(-41, -10), (10, 41)]
            for start, end in intervals:
                rod(glyphs, center + tangent * start, center + tangent * end, 4, ARMOR)
                rod(glyphs, center + tangent * start + [0, 4, 0],
                    center + tangent * end + [0, 4, 0], 1.4, GOLD)
                for t in np.arange(start + 4, end, 12):
                    rod(glyphs, center + tangent * t - radial * 3,
                        center + tangent * t + radial * 3, 1, WHITE)
        parts.append(finish(glyphs, ['三爻由分段金边机械轨组成，断爻保留二十格中缝。']))
    return parts


def cognition_carriers():
    part = Part('fusion_cognition_carriers', '认知载体制备与陶瓷阵列装载轨', section='industry',
                process_role='认知载体', center=[-307, -367, 0], longitudinal_axis='Z')
    for x in (-349, -269):
        part.box([x - 5, -405, -141], [x + 5, -398, 141], ARMOR)
        part.box([x - 2, -397, -137], [x + 2, -395, 137], GOLD)
        part.box([x - 1, -394, -132], [x + 1, -393, 132], RED)
        for z in range(-126, 127, 28):
            part.box([x - 7, -405, z - 4], [x + 7, -388, z + 4], DARK)
            part.box([x - 8, -389, z - 4], [x + 8, -387, z + 4], WHITE)
    for z in range(-112, 113, 28):
        part.box([-345, -392, z - 10], [-273, -388, z + 10], ARMOR)
        part.box([-341, -387, z - 8], [-277, -386, z + 8], GOLD)
        for x in (-337, -281):
            part.box([x - 3, -386, z - 8], [x + 3, -329, z + 8], ARMOR)
            part.box([x - 4, -334, z - 9], [x + 4, -329, z + 9], WHITE)
        for y in range(-380, -337, 7):
            part.box([-332, y, z - 7], [-286, y + 2, z + 7], WHITE)
            part.box([-326, y + 3, z - 5], [-292, y + 3, z + 5], RED)
            part.box([-330, y + 1, z - 8], [-288, y + 1, z - 8], DARK)
        part.box([-322, -336, z - 6], [-296, -331, z + 6], DARK)
        part.box([-315, -330, z - 4], [-303, -329, z + 4], LIGHT)
    for z in range(-133, 134, 8):
        part.box([-364, -383, z], [-355, -341, z + 1], ARMOR)
        part.box([-363, -341, z], [-356, -339, z + 1], GOLD)
    return finish(part, ['九组陶瓷认知载体层架沿双轨送入装载工位，夹具与散热片开放可见。'])


def read_write_verification():
    part = Part('fusion_read_write_verification', '读写校验与双腔相位比对线', section='industry',
                process_role='读写校验', center=[0, -366, -309], longitudinal_axis='X')
    for z in (-349, -269):
        part.box([-148, -405, z - 5], [148, -398, z + 5], ARMOR)
        part.box([-144, -397, z - 1], [144, -395, z + 1], GOLD)
    for center_x in (-76, 76):
        a, b = center_x - 45, center_x + 45
        rod(part, [a, -364, -309], [b, -364, -309], 23, CRIMSON, inner=20)
        rod(part, [a, -364, -309], [b, -364, -309], 6, WHITE)
        for x in (a, b):
            part.ring([x, -364, -309], 30, 8, ARMOR, normal=[1, 0, 0], depth=7)
            part.ring([x, -364, -309], 30, 2, GOLD, normal=[1, 0, 0], depth=2)
            for z in (-333, -285):
                part.box([x - 5, -398, z - 5], [x + 5, -370, z + 5], WHITE)
        for x in range(a + 13, b, 13):
            part.ring([x, -364, -309], 27, 3, RED, normal=[1, 0, 0], depth=3)
        for x in range(a + 4, b, 8):
            part.box([x, -402, -365], [x + 1, -347, -355], ARMOR)
            part.box([x, -348, -365], [x + 1, -346, -355], GOLD)
    for x in (-18, 18):
        part.box([x - 4, -398, -343], [x + 4, -323, -335], ARMOR)
        part.box([x - 4, -398, -283], [x + 4, -323, -275], ARMOR)
        part.box([x - 5, -327, -343], [x + 5, -321, -275], WHITE)
        part.box([x - 2, -330, -331], [x + 2, -328, -287], RED)
    rod(part, [-27, -364, -309], [27, -364, -309], 3, HOT)
    return finish(part, ['双赤玻璃校验腔保留透明侧壁、六道线圈、独立支脚与中央读写横梁。'])


def consensus_collection():
    center = np.array([214, -374, 214])
    part = Part('fusion_consensus_collection', '共识汇聚与三路同步判读阵列', section='industry',
                process_role='共识汇聚', center=center.tolist(), clear_center_radius=29)
    for y, radius, thickness, state, depth in [(-404, 59, 11, ARMOR, 7),
            (-398, 60, 3, GOLD, 3), (-385, 48, 7, DARK, 5),
            (-341, 48, 7, ARMOR, 7), (-335, 49, 3, GOLD, 3)]:
        part.ring([214, y, 214], radius, thickness, state, depth=depth)
    rod(part, [214, -393, 214], [214, -346, 214], 34, CRIMSON, inner=30)
    for angle in np.arange(8) * math.pi / 4:
        offset = np.array([math.cos(angle), 0, math.sin(angle)])
        rod(part, [214, -397, 214] + offset * 45,
            [214, -335, 214] + offset * 45, 3, WHITE)
        rod(part, [214, -389, 214] + offset * 35,
            [214, -344, 214] + offset * 35, 1.5, RED)
        for distance in (50, 54, 58):
            a = [214, -389, 214] + offset * distance
            rod(part, a, a + np.array([0, 39, 0]), 1.3, ARMOR)
    for start in ([155, -397, 269], [269, -397, 155], [282, -397, 282]):
        end = center + (np.asarray(start) - [214, -397, 214]) * .52
        end[1] = -397
        truss(part, start, end, [0, 0, 1] if start[0] < 214 else [1, 0, 0], 5)
        rod(part, end, [214, -374, 214], 2, RED)
    part.ring([214, -365, 214], 14, 4, WHITE, depth=7)
    part.ring([214, -362, 214], 10, 3, HOT, depth=3)
    return finish(part, ['三条机械汇流轨送入贯通玻璃判读腔，白瓷立肋与分立散热鳍片环绕腔体。'])


def island_supports():
    parts = []
    starts = [[-300, -363, -265], [260, -363, -250], [-290, -363, 235], [290, -363, 235]]
    ends = [[-250, 8, -207], [198, 12, -192], [-257, 12, 158], [257, 19, 162]]
    for index, (start, end) in enumerate(zip(starts, ends), 1):
        part = Part(f'fusion_peripheral_support_{index}', f'第{index}根外围峰底细桁架',
                    section='industry', endpoint=end)
        radial = np.asarray([end[0], 0, end[2]], float)
        tangent = np.cross(radial / np.linalg.norm(radial), [0, 1, 0])
        truss(part, start, end, tangent, 6)
        part.ring(np.array(end) + [0, -4, 0], 12, 5, ARMOR, depth=5)
        part.ring(np.array(end) + [0, -1, 0], 12, 2, GOLD, depth=2)
        parts.append(finish(part, ['细桁架在外围峰底承托山体，中轴与核心上方空域保持开放。']))
    return parts


def weapon_cradles():
    parts = []
    for name, label, start, end in [('sword', '剑尖', [-355, -363, 205], [-440, -315, 230]),
                                   ('spear', '枪柄', [355, -363, 205], [400, -315, 170])]:
        part = Part(f'fusion_{name}_cradle', f'{label}短托与机械连接', section='industry',
                    anchor=(np.array(end) + [0, 15, 0]).tolist())
        truss(part, start, end, [0, 0, 1], 8)
        top = np.array(end) + [0, 15, 0]
        rod(part, end, top, 11, ARMOR, inner=6)
        part.ring(top + [0, -4, 0], 23, 7, ARMOR, depth=7)
        part.ring(top + [0, -1, 0], 23, 2, GOLD, depth=2)
        part.ring(top, 8, 8, WHITE, depth=7)
        for zsign in (-1, 1):
            rod(part, np.array(end) + [0, 2, zsign * 7],
                top + [0, 5, zsign * 15], 3, WHITE)
        parts.append(finish(part, ['短桁架从下层矩阵连接黑金环形承托，白瓷双爪抱住兵装根部。']))
    for index, x in enumerate((-100, 100), 1):
        part = Part(f'fusion_chain_cradle_{index}', f'链刃第{index}处叉托与机械连接',
                    section='industry', anchor=[x, -350, 450])
        truss(part, [x, -363, 370], [x, -355, 450], [1, 0, 0], 7)
        part.box([x - 13, -363, 433], [x + 13, -355, 467], ARMOR)
        part.box([x - 12, -354, 433], [x + 12, -351, 467], GOLD)
        for z in (433, 464):
            part.box([x - 10, -350, z], [x + 10, -340, z + 3], WHITE)
        for z in (438, 454):
            part.box([x - 17, -350, z], [x + 17, -345, z + 9], WHITE)
        parts.append(finish(part, ['短悬梁连接开放白瓷叉托，承托横卧链刃。']))
    for index, x in enumerate((-190, 190), 1):
        part = Part(f'fusion_case_cradle_{index}', f'兵匣第{index}处鞍座与后方升降桁架',
                    section='industry', anchor=[x, -63, -470])
        route = [[x, -363, -345], [x, -245, -435], [x, -70, -470]]
        for a, b in zip(route[:-1], route[1:]):
            truss(part, a, b, [1, 0, 0], 7)
        part.box([x - 15, -76, -494], [x + 15, -67, -446], ARMOR)
        part.box([x - 13, -66, -491], [x + 13, -63, -449], GOLD)
        for z in (-489, -455):
            part.box([x - 12, -62, z], [x + 12, -51, z + 4], WHITE)
        parts.append(finish(part, ['双折开放桁架升至后方鞍座，白瓷侧爪承托横卧兵匣。']))
    return parts


def build():
    parts = matrix() + [cognition_carriers(), read_write_verification(), consensus_collection()]
    parts += island_supports() + weapon_cradles()
    notes = [
        '下层工业矩阵采用外半径420附近的双层八角黑金梁、八道径向开放桁架和八组三爻导轨，中心贯通，不铺实体圆盘。',
        '认知载体、读写校验、共识汇聚分别以陶瓷层架双轨、赤玻璃双校验腔和三路汇聚判读腔呈现，为本次融合稿的工艺外观设计。',
        '三组工艺模块位于Y−410附近至Y−320附近；红色线圈、黑金散热片、白瓷骨架与纵向工艺轨道均由现有方块逐格构成。',
        '核心中心(0,−180,0)，三羽环含方块体积的保守球包络约166格；新增固定件位于外围，核心上方至T9岛底的中央空域保持开放。',
        '四根细支承在外围峰底接合，T9原始方块、前方石阶和东侧溪谷保留。',
        '兵装机械连接对准剑尖(−440,−300,230)、枪柄尾(400,−300,170)、链刃X±100/Y−350/Z450；兵匣X±190的鞍座顶面Y−63，贴合原兵匣截面底部Y−62。',
        '全部实体格沿用通用接口替换规则，本模块不设置专用输入输出槽位或主控。',
    ]
    return parts, notes
