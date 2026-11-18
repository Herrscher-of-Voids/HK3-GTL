# -*- coding: utf-8 -*-
"""I34 V2：透镜研究台、后掠双弦臂与开敞的非实体树影观测空间。

变更记录 #1：2026-10-27，从空白重画建筑，保留已确认树影，未改正式资源。
"""
import math
from pathlib import Path

import numpy as np
import i34_imaginary_tree_array_geometry_20261027 as palette

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 481, 251, 381
CX, CZ = 240, 190
NAME = 'hk3gtl-i34-open-observatory-v2-20261027'
TITLE = '虚数之树观测阵列 · 开穹悬弦观测仪'
STATES = sorted(palette.PALETTE_ROLES)
IDS = {state: i + 1 for i, state in enumerate(STATES)}
ROLES = dict(palette.PALETTE_ROLES)
ROLES.update({palette.IRV: '透镜研究台、后掠观测弦臂与相位读出架的主体',
              palette.ROBUST: '减振地基、楼层主梁与观测弦臂的连续内脊',
              palette.CLEAN: '弦臂包边、检修走台与研究台立面分层护边',
              palette.GLASS: '底座研究层的带状观察窗',
              palette.GOLD: '校准接点与弦列读出端的小量镀金接点'})


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)

    def box(lo, hi, state):
        x0, y0, z0 = lo; x1, y1, z1 = hi
        assert 0 <= x0 <= x1 < W and 0 <= y0 <= y1 < H and 0 <= z0 <= z1 < D, (lo, hi)
        cube[y0:y1 + 1, z0:z1 + 1, x0:x1 + 1] = IDS[state]

    def beam(a, b, state, r=1):
        steps = max(abs(b[i] - a[i]) for i in range(3))
        for k in range(steps + 1):
            p = [round(a[i] + (b[i] - a[i]) * k / max(steps, 1)) for i in range(3)]
            box(tuple(v - r for v in p), tuple(v + r for v in p), state)

    zz, xx = np.mgrid[:D, :W]
    # 四道结构楼板之间留出完整研究层；承重隔舱及设备脊形成可读的工程结构。
    for y in range(67):
        level = 0 if y < 18 else 1 if y < 39 else 2 if y < 60 else 3
        rx, rz = (240 - level * 8), (190 - level * 7)
        radius = ((xx - CX) / rx) ** 2 + ((zz - CZ) / rz) ** 2
        inside = radius <= 1
        skin = inside & (radius > ((rx - 5) / rx) ** 2)
        floor = y <= 10 or 18 <= y <= 25 or 39 <= y <= 46 or y >= 60
        if floor:
            cube[y, inside] = IDS[palette.IRV]
            if y in (10, 25, 46, 66):
                cube[y, inside & (radius < .89)] = IDS[palette.ASSEMBLY]
                cube[y, inside & (radius >= .89)] = IDS[palette.CLEAN]
                if y in (25, 46):
                    cube[y, inside & (radius < .85)] = IDS[palette.PLASCRETE]
        else:
            ribs = inside & ((abs(xx - CX) % 48 < 6) | (abs(zz - CZ) % 52 < 6))
            cube[y, ribs] = IDS[palette.IRV]
            cube[y, skin] = IDS[palette.IRV]
            windows = skin & (abs(xx - CX) % 48 > 11) & (abs(zz - CZ) % 52 > 11)
            if y in (*range(12, 17), *range(28, 36), *range(49, 57)):
                cube[y, windows] = IDS[palette.GLASS]
        if y in (0, 1, 2):
            cube[y, inside & (radius > .9)] = IDS[palette.ROBUST]
    # 低矮北向鼻台与地基连续；主控和档案接口嵌在鼻台自身正立面。
    for y in range(28, 61):
        half = 49 - max(0, y - 48)
        box((CX - half, y, 18), (CX + half, y, 91), palette.IRV)
        if y in (29, 57, 60):
            box((CX - half, y, 18), (CX + half, y, 20), palette.CLEAN)
    box((CX - 41, 36, 18), (CX + 41, 50, 18), palette.BLACK_GLASS)
    box((CX - 42, 35, 18), (CX + 42, 35, 18), palette.LIGHT)

    # 后掠弦臂采用不断变化的厚度与后退量，两只半月形承力壳承担整机实际高度。
    arm_centers = []
    for y in range(47, H):
        t = (y - 47) / (H - 1 - 47)
        left = round(50 - 36 * math.sin(t * math.pi) + 116 * t ** 2)
        zc = round(205 + 98 * t)
        halfx = round(28 - 10 * t)
        halfz = round(43 - 19 * t)
        arm_centers.append((left, y, zc, halfx, halfz))
        for x in (left, W - 1 - left):
            outer = (abs(xx - x) <= halfx) & (abs(zz - zc) <= halfz)
            # 内部沿垂直方向连续的检修井由壳体包围，臂内也保留检修空腔。
            inner = (abs(xx - x) < halfx - 9) & (abs(zz - zc) < halfz - 11)
            cube[y, outer] = IDS[palette.IRV]
            cube[y, inner] = 0
            rim = outer & ((abs(xx - x) >= halfx - 2) | (abs(zz - zc) >= halfz - 2))
            cube[y, rim] = IDS[palette.CLEAN]
            front = outer & (zz == zc - halfz) & (abs(xx - x) < halfx - 6)
            cube[y, front] = IDS[palette.BLACK_GLASS if y % 22 < 15 else palette.IRV]
            if y % 22 in (0, 1, 2):
                cube[y, outer & ~inner] = IDS[palette.IRV]
            if y % 22 == 3:
                cube[y, inner] = IDS[palette.GRATE]
            # 银边内侧窄导光槽，避免大面积异色拼接。
            for sx in (x - halfx + 4, x + halfx - 4):
                box((sx, y, zc - halfz), (sx + 1, y, zc - halfz + 1), palette.BLUE_GLASS)
    # 后方展开的双扇相位采样弦列，沿后掠弦臂和实体后桥承托，前半空间全部留空。
    box((97, 64, 303), (383, 73, 328), palette.IRV)
    box((99, 74, 304), (381, 75, 326), palette.GRATE)
    for x in range(106, 376, 24):
        top = round(244 - abs(x - CX) * .13)
        # 各弦柱直接落在同一条设备后桥上，而不是悬空的树枝或新加高塔。
        box((x - 3, 76, 310), (x + 3, top, 316), palette.IRV)
        box((x - 1, 78, 309), (x + 1, top - 3, 309), palette.BLACK_GLASS)
        for y in range(89, top - 2, 24):
            box((x - 5, y - 3, 307), (x + 5, y + 3, 318), palette.ATOMIC)
            box((x - 2, y - 1, 306), (x + 2, y + 1, 306), palette.GOLD)
        box((x - 2, 77, 308), (x + 2, 83, 308), palette.LASER)
        box((x - 3, 76, 317), (x + 3, top - 1, 317), palette.BLACK)
        # 有实体连接的顶部读出母线。
        for nx in (max(91, x - 12), min(389, x + 12)):
            beam((x, top, 313), (nx, top - 5, 313), palette.CLEAN, 2)
    # 两道前低后高的斜向测量轨，后端与主弦臂相接，形成清楚的张弦受力关系。
    for side in (-1, 1):
        for zoffset in (-15, 15):
            start = (CX + side * 155, 67, 102 + zoffset)
            end = (CX + side * 74, 226, 290 + zoffset)
            beam(start, end, palette.IRV, 5)
            beam((start[0], start[1] + 6, start[2]), (end[0], end[1] + 6, end[2]), palette.CLEAN, 1)
            for i in range(1, 6):
                t = i / 6
                p = tuple(round(start[j] + (end[j] - start[j]) * t) for j in range(3))
                beam((p[0] - 8, p[1], p[2]), (p[0] + 8, p[1], p[2]), palette.STRESS, 3)

    # 观测平面为分层光阑，根系在上方非实体展开，中心不放方块树或球体。
    radius = np.hypot(xx - CX, zz - 167)
    for y in range(67, 75):
        mask = (radius <= 111 - (y - 67) * 2) & (radius >= 42)
        cube[y, mask] = IDS[palette.IRV if y < 72 else palette.CLEAN]
    cube[75, (radius <= 99) & (radius >= 42)] = IDS[palette.IRV]
    for y, r in ((76, 93), (76, 78), (76, 64)):
        mask = (abs(radius - r) <= 2)
        cube[y, mask] = IDS[palette.LIGHT if r == 78 else palette.BLACK_GLASS]
    # 单道后半观测走台，不封闭前方，也不形成四座外圈厂房。
    for z in range(170, 282):
        half = round(math.sqrt(max(0, 136 ** 2 - (z - 170) ** 2)))
        for side in (-1, 1):
            x = CX + side * half
            box((x - 6, 81, z), (x + 6, 86, z), palette.IRV)
            box((x - 5, 87, z), (x + 5, 87, z), palette.GRATE)
            if z % 22 == 0:
                box((x - 3, 67, z - 2), (x + 3, 80, z + 2), palette.ROBUST)

    # 硬件全部收进研究台或弦臂根部：材料种类按设备用途配置，不用七彩外墙充数。
    equipment = [palette.COMPUTER, palette.POWER, palette.PROCESS, palette.DIMENSION,
                 palette.MULTI, palette.FILTER, palette.INERT, palette.HEATPROOF,
                 palette.INSULATE, palette.FROST, palette.STABLE, palette.INTAKE,
                 palette.MIXING, palette.LAFIUM, palette.TURBINE, palette.MACERATOR,
                 palette.VENT, palette.GEAR, palette.TUNG_PIPE, palette.STEEL_PIPE,
                 palette.IRIDIUM, palette.SOLID, palette.VIBRATION]
    for i, state in enumerate(equipment):
        z = 90 + (i % 8) * 28
        y = 27 if i < 8 else 48 if i < 16 else 67
        for side in (-1, 1):
            x = CX + side * (73 + (i // 8) * 33)
            box((x - 9, y, z - 8), (x + 9, y + 8, z + 8), state)
            box((x - 10, y - 1, z - 9), (x + 10, y - 1, z + 9), palette.VIBRATION)
            box((x - 9, y + 9, z - 8), (x + 9, y + 10, z + 8), palette.IRV)
    # 南向资料交接台完全低于主弦桥，接口属于实体档案层立面。
    box((CX - 65, 28, 325), (CX + 65, 59, 355), palette.IRV)
    box((CX - 62, 60, 325), (CX + 62, 62, 355), palette.CLEAN)
    # 最终统一镜像几何及材质；各侧接口可以承担不同工艺语义。
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]

    controller = [CX, 43, 18]
    ports = [dict(id='世界泡对照档案输入', pos=[CX - 24, 43, 18], face='north'),
             dict(id='空间探针输入', pos=[CX + 24, 43, 18], face='north'),
             dict(id='西侧观测供能', pos=[CX - 40, 43, 18], face='north'),
             dict(id='东侧观测供能', pos=[CX + 40, 43, 18], face='north'),
             dict(id='西侧冷却输入', pos=[CX - 48, 43, 355], face='south'),
             dict(id='东侧冷却回流', pos=[CX + 48, 43, 355], face='south'),
             dict(id='树与世界联系图输出', pos=[CX - 24, 43, 355], face='south'),
             dict(id='虚数观测资料输出', pos=[CX + 24, 43, 355], face='south'),
             dict(id='观测探针回收', pos=[CX - 60, 43, 355], face='south'),
             dict(id='复测档案交付', pos=[CX + 60, 43, 355], face='south')]
    for item in [dict(pos=controller, face='north')] + ports:
        x, y, z = item['pos']; inward = 1 if item['face'] == 'north' else -1
        # 只修整设备本身的连续立面，禁止在外侧添加独立接口板。
        box((x - 2, y - 2, min(z, z + inward)), (x + 2, y + 2, max(z, z + inward)), palette.IRV)
        cube[y, z, x] = IDS[palette.CONTROL if item['pos'] == controller else palette.PORT]
        for distance in range(1, 6):
            cube[y - 2:y + 3, z - inward * distance, x - 2:x + 3] = 0
        item['purpose'] = item.get('id', '主控') + '候选；实际能力按正式Pattern另验'
    # 不以未使用的旧材料充数，所有声明材料必须有实体。
    used = np.unique(cube)
    missing = [s for s, ident in IDS.items() if ident not in used]
    assert not missing, ('材料用途遗漏', missing)
    data = dict(key='i34', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
                controller_face='north', ports=ports,
                paths=[dict(name='北侧主控操作净空', min=[CX - 62, 40, 13], max=[CX + 62, 46, 17]),
                       dict(name='南侧资料交接净空', min=[CX - 65, 40, 356], max=[CX + 65, 46, 360])],
                zones=[dict(name='透镜形多层研究台', pos=[CX, 60, 60]),
                       dict(name='后掠半月承力弦臂', pos=[141, 235, 271]),
                       dict(name='开放相位采样弦列', pos=[202, 175, 310]),
                       dict(name='金白虚数之树投影 · 非实体', pos=[CX, 170, 167], visual_only=True),
                       dict(name='后半观测走台', pos=[112, 87, 212]),
                       dict(name='底座资料交接层', pos=[CX, 59, 350])],
                description='透镜形研究台将档案、相关运算及冷却设备收进分层基座；两道连续落地的后掠半月弦臂托起校准弦列，前半观测空间完全敞开。金白树影悬于中央光阑上方，构成仪器的观测对象。整机以青铜IRV、银灰护边与窄冰蓝光路形成统一风格。',
                projection=dict(source='I34_虚数之树_动态投影研究_V1_20261027', position=[CX, 92, 167], scale=.9,
                                approved=True, entity_blocks=0, included_in_pattern=False),
                construction_notes=dict(orientation='主控朝北/-Z，蓝图坐标从0起算。',
                                        anchor='推荐世界Y=-60，实体最高Y=190。',
                                        boundary='只观测树与世界联系及误差；不制造或操纵整棵虚数之树。RN-IOP开放，首次真实初观支持RN-ILE。',
                                        approval='建筑为新候选；树影采用单独已确认V1，未接入游戏。'))
    # 清空完整的操作通廊，不只清空接口前一格。
    for route in data['paths']:
        x0, y0, z0 = route['min']; x1, y1, z1 = route['max']
        cube[y0:y1 + 1, z0:z1 + 1, x0:x1 + 1] = 0
    return cube, data


if __name__ == '__main__':
    cube, data = build()
    print(dict(size=data['size'], blocks=int(np.count_nonzero(cube)),
               materials=len(np.unique(cube)) - 1,
               irv=int(np.count_nonzero(cube == IDS[palette.IRV]))), flush=True)
