# -*- coding: utf-8 -*-
"""I37双腔差分场试验场：双环真空廊与中轴测量颈部。"""
from pathlib import Path
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX, CZ = 529, 285, 529, 264, 264
NAME = 'hk3gtl-i37-dual-field-range-20261028'
TITLE = '世界维系试验平台 · 双腔差分场试验场'


class Material:
    WFV = 'hk3gtl:voltage_machine_casing_wfv'
    PORT = 'hk3gtl:industrial_port_casing'
    CONTROL = 'minecraft:diamond_block'
    SMOOTH_STONE = 'minecraft:smooth_stone'
    STONE_BRICKS = 'minecraft:stone_bricks'
    CRACKED_STONE_BRICKS = 'minecraft:cracked_stone_bricks'
    CHISELED_STONE_BRICKS = 'minecraft:chiseled_stone_bricks'
    COBBLESTONE = 'minecraft:cobblestone'
    POLISHED_ANDESITE = 'minecraft:polished_andesite'
    POLISHED_DIORITE = 'minecraft:polished_diorite'
    POLISHED_DEEPSLATE = 'minecraft:polished_deepslate'
    DEEPSLATE_BRICKS = 'minecraft:deepslate_bricks'
    CRACKED_DEEPSLATE_BRICKS = 'minecraft:cracked_deepslate_bricks'
    DEEPSLATE_TILES = 'minecraft:deepslate_tiles'
    CRACKED_DEEPSLATE_TILES = 'minecraft:cracked_deepslate_tiles'
    BLACKSTONE = 'minecraft:blackstone'
    POLISHED_BLACKSTONE = 'minecraft:polished_blackstone'
    POLISHED_BLACKSTONE_BRICKS = 'minecraft:polished_blackstone_bricks'
    BASALT = 'minecraft:basalt[axis=y]'
    POLISHED_BASALT = 'minecraft:polished_basalt[axis=y]'
    SMOOTH_BASALT = 'minecraft:smooth_basalt'
    GRAY_CONCRETE = 'minecraft:gray_concrete'
    LIGHT_GRAY_CONCRETE = 'minecraft:light_gray_concrete'
    WHITE_CONCRETE = 'minecraft:white_concrete'
    NETHERITE_BLOCK = 'minecraft:netherite_block'
    GLASS = 'minecraft:glass'
    TINTED_GLASS = 'minecraft:tinted_glass'
    GRAY_STAINED_GLASS = 'minecraft:gray_stained_glass'
    WHITE_STAINED_GLASS = 'minecraft:white_stained_glass'
    QUARTZ_BLOCK = 'minecraft:quartz_block'
    SMOOTH_QUARTZ = 'minecraft:smooth_quartz'
    CALCITE = 'minecraft:calcite'
    SNOW_BLOCK = 'minecraft:snow_block'
    TUFF = 'minecraft:tuff'
    REINFORCED_DEEPSLATE = 'minecraft:reinforced_deepslate'
    END_STONE_BRICKS = 'minecraft:end_stone_bricks'
    END_STONE = 'minecraft:end_stone'
    POLISHED_MARBLE = 'gtceu:polished_marble'
    MARBLE_BRICKS = 'gtceu:marble_bricks'
    MARBLE_TILE = 'gtceu:marble_tile'
    CHISELED_MARBLE = 'gtceu:chiseled_marble'
    SMALL_MARBLE_BRICKS = 'gtceu:small_marble_bricks'
    POLISHED_LIGHT_CONCRETE = 'gtceu:polished_light_concrete'


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {state: i + 1 for i, state in enumerate(STATES)}
ROLES = {state: '差分试验场内可独立检修的测量、隔离或传输模块' for state in STATES}
ROLES.update({
    material.WFV: '双腔外壁、环形承力层架与上部闭合测量框的主体机壳',
    material.PORT: '中轴控制颈部连续外墙内齐平接口占位，不含真实仓室能力',
    material.CONTROL: '中轴控制颈部正中主控定位标记，仅供建筑预览',
    material.POLISHED_BASALT: '双腔边缘的介质导向槽与检修导轨',
    material.POLISHED_BLACKSTONE: '参考腔与扰动腔之间的场约束测量节点',
    material.TINTED_GLASS: '观察窗的遮光隔离层',
    material.GRAY_STAINED_GLASS: '双侧观察窗与端面校准窗',
    material.WHITE_STAINED_GLASS: '计量框内的漫反射标定面',
    material.REINFORCED_DEEPSLATE: '控制颈部的抗振锚座',
    material.QUARTZ_BLOCK: '中轴差分仪器基准台',
    material.SMOOTH_QUARTZ: '试验舱内的洁净计量基准面',
})

# 所有边界均从实际方块边界导出；环腔掩码避免实体填满中心试验空间。
_x = np.arange(W, dtype=np.int16)[None, :]
_z = np.arange(D, dtype=np.int16)[:, None]


def octagonal_ellipse(cx, cz, rx, rz):
    ux = np.abs(_x - cx) / rx
    uz = np.abs(_z - cz) / rz
    return (ux <= 1) & (uz <= 1) & (ux + uz <= 1.38)


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)

    def box(lo, hi, state):
        x, y, z = lo; X, Y, Z = hi
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (lo, hi)
        cube[y:Y + 1, z:Z + 1, x:X + 1] = IDS[state] if state else 0

    def mask_layers(mask, y0, y1, state):
        value = IDS[state] if state else 0
        for y in range(y0, y1 + 1):
            cube[y][mask] = value

    def shell(lo, hi, state, t=2):
        box(lo, hi, state)
        x, y, z = lo; X, Y, Z = hi
        if X - x > 2 * t and Y - y > 2 * t and Z - z > 2 * t:
            box((x + t, y + t, z + t), (X - t, Y - t, Z - t), None)

    def axis_bar(a, b, state, radius=1):
        count = max(abs(a[i] - b[i]) for i in range(3))
        for n in range(count + 1):
            point = [round(a[i] + (b[i] - a[i]) * n / max(1, count)) for i in range(3)]
            lo = tuple(max(0, v - radius) for v in point)
            hi = tuple(min(s - 1, v + radius) for v, s in zip(point, (W, H, D)))
            box(lo, hi, state)

    lobes = []
    for center_x in (132, 396):
        outer = octagonal_ellipse(center_x, CZ, 132, 264)
        inner = octagonal_ellipse(center_x, CZ, 90, 218)
        ring = outer & ~inner
        outer_core = octagonal_ellipse(center_x, CZ, 129, 261)
        inner_core = octagonal_ellipse(center_x, CZ, 93, 221)
        outer_skin = outer & ~outer_core
        inner_skin = inner_core & ~inner
        lobes.append((center_x, ring, outer_skin, inner_skin))

    # 两个同构环腔分别承担稳定参考态和局部扰动态；层架兼作承力梁与巡检层。
    for idx, (center_x, ring, outer_skin, inner_skin) in enumerate(lobes):
        mask_layers(ring, 7, 10, material.WFV)
        mask_layers(ring, 270, 273, material.WFV)
        mask_layers(outer_skin, 10, 273, material.WFV)
        mask_layers(inner_skin, 10, 273, material.POLISHED_DEEPSLATE)

        for level, y in enumerate(range(12, 270, 15)):
            floor = material.WFV if level % 3 else material.POLISHED_DEEPSLATE
            mask_layers(ring, y, y + 1, floor)
            # 将每层外环划成设备槽和检修带，局部色差标识真实功能，不形成彩色拼盘。
            mask_layers(outer_skin, y + 2, min(y + 3, 273),
                        material.DEEPSLATE_TILES if level % 4 == 0 else material.POLISHED_BLACKSTONE_BRICKS)

        # 24条径向承力/测量隔墙构成分舱，不用实心填满两座试验腔。
        for sector in range(24):
            angle = math.tau * sector / 24
            state = material.WFV if sector % 3 else material.POLISHED_BLACKSTONE
            for step in range(43):
                t = step / 42
                rx = 129 - (39 * t)
                rz = 261 - (43 * t)
                x = round(132 + rx * math.cos(angle))
                z = round(CZ + rz * math.sin(angle))
                mirrored_x = 528 - x
                for c in (x, mirrored_x):
                    box((c - 2, 10, z - 2), (c + 2, 273, z + 2), state)

        # 内侧每层设置贯通检修梁、温控/样件回路和小型监测台。
        for level, y in enumerate(range(24, 265, 30)):
            for dx in (-48, -24, 24, 48):
                x = center_x + dx
                box((x - 2, y, CZ - 185), (x + 2, y + 2, CZ + 185),
                    material.POLISHED_BASALT if dx % 2 == 0 else material.GRAY_CONCRETE)
                if abs(dx) == 24:
                    anchor_x = 178 if center_x < CX else 350
                    axis_bar((x, y, CZ - 185), (anchor_x, y, CZ - 185), material.WFV, 1)
            for z in (CZ - 205, CZ + 205):
                box((center_x - 70, y + 3, z - 2), (center_x + 70, y + 5, z + 2),
                    material.NETHERITE_BLOCK if level % 2 else material.CRACKED_DEEPSLATE_TILES)

        # 每腔放置独立的三轴矩形计量框，结构闭合、受力落地，不以爪形支架抓持试件。
        cx, cy, cz = center_x, 146, CZ
        for half_x, half_y, half_z, state in (
            (72, 68, 172, material.WFV),
            (62, 58, 152, material.POLISHED_BLACKSTONE_BRICKS),
        ):
            x0, x1 = cx - half_x, cx + half_x
            y0, y1 = cy - half_y, cy + half_y
            z0, z1 = cz - half_z, cz + half_z
            for z in (z0, z1):
                axis_bar((x0, y0, z), (x1, y0, z), state, 2)
                axis_bar((x0, y1, z), (x1, y1, z), state, 2)
            for x in (x0, x1):
                for z in (z0, z1):
                    axis_bar((x, y0, z), (x, y1, z), state, 2)
            for y in (y0, y1):
                axis_bar((x0, y, z0), (x0, y, z1), state, 2)
                axis_bar((x1, y, z0), (x1, y, z1), state, 2)

        # 双侧玻璃观察窄窗、排热片和端面校准窗嵌入外壁。
        zfront = 5
        box((center_x - 25, 58, zfront), (center_x + 25, 219, zfront + 2), material.TINTED_GLASS)
        box((center_x - 18, 75, zfront), (center_x + 18, 202, zfront + 2), material.GRAY_STAINED_GLASS)
        box((center_x - 12, 91, zfront + 1), (center_x + 12, 185, zfront + 2), material.GLASS)
        box((center_x - 25, 58, D - zfront - 3), (center_x + 25, 219, D - zfront - 1), material.TINTED_GLASS)
        box((center_x - 18, 75, D - zfront - 3), (center_x + 18, 202, D - zfront - 1), material.GRAY_STAINED_GLASS)
        box((center_x - 12, 91, D - zfront - 3), (center_x + 12, 185, D - zfront - 2), material.GLASS)

    # 中央控制颈部把双腔刚性闭合；主控和10接口在正中连续外墙内齐平布置。
    shell((178, 0, 12), (350, 76, 138), material.WFV, 3)
    box((184, 8, 18), (344, 10, 132), material.POLISHED_DEEPSLATE)
    box((184, 68, 18), (344, 70, 132), material.POLISHED_DEEPSLATE)
    box((184, 18, 42), (344, 19, 124), material.SMOOTH_QUARTZ)
    for x in (190, 198, 327, 335):
        box((x, 11, 30), (x + 3, 65, 116), material.DEEPSLATE_BRICKS)
    for x in (206, 316):
        state = material.POLISHED_BLACKSTONE
        box((x, 20, 63), (x + 6, 54, 94), state)
        box((min(x, CX), 38, 78), (max(x + 6, CX), 40, 80), material.POLISHED_BASALT)
    box((178, 38, 78), (350, 40, 80), material.POLISHED_BASALT)
    for lo, hi in (
        ((178, 68, 12), (350, 70, 21)),
        ((178, 68, 129), (350, 70, 138)),
        ((178, 68, 18), (184, 70, 132)),
        ((344, 68, 18), (350, 70, 132)),
    ):
        box(lo, hi, material.DEEPSLATE_TILES)

    controller = [CX, 22, 12]
    offsets = (12, 24, 36, 48, 60)
    ports = [dict(id=name, pos=[CX - dx, 22, 12], face='north')
             for dx, name in zip(offsets, ('参考腔锚定记录输入', '扰动腔锚定记录输入',
                 '稳定介质输入', '试件与校准资料输入', '能量合同凭据输入'))]
    ports += [dict(id=name, pos=[CX + dx, 22, 12], face='north')
              for dx, name in zip(offsets, ('参考态维系记录输出', '扰动态响应记录输出',
                  '合格试验样件输出', '用后介质回收输出', '失败分析与状态输出'))]

    # 接口功能舱使用左右镜像仪器托盘；各材料少量表达可更换的专用设备。
    detail_states = [state for state in STATES if state not in {
        material.WFV, material.PORT, material.CONTROL, material.SMOOTH_QUARTZ,
        material.POLISHED_DEEPSLATE, material.DEEPSLATE_BRICKS,
        material.POLISHED_BLACKSTONE, material.POLISHED_BLACKSTONE_BRICKS,
        material.POLISHED_BASALT,
        material.NETHERITE_BLOCK, material.CRACKED_DEEPSLATE_TILES,
        material.TINTED_GLASS, material.GRAY_STAINED_GLASS, material.GLASS,
    }]
    for i, state in enumerate(detail_states):
        row, col = divmod(i, 4)
        z = 42 + row * 9
        x = 208 + col * 13
        box((x, 24, z), (x + 4, 32, z + 4), state)
        box((x + 2, 11, z + 2), (x + 2, 23, z + 2), material.POLISHED_BLACKSTONE)
        mirrored = 528 - (x + 4)
        box((mirrored, 24, z), (mirrored + 4, 32, z + 4), state)
        box((mirrored + 2, 11, z + 2), (mirrored + 2, 23, z + 2), material.POLISHED_BLACKSTONE)

    for item in [dict(id='主控', pos=controller, face='north')] + ports:
        x, y, z = item['pos']
        cube[y, z, x] = IDS[material.CONTROL if item['id'] == '主控' else material.PORT]
        item['purpose'] = item['id'] + '候选；真实仓室能力与配方另验'

    # 上部闭合测量冠梁连接两座环腔顶层，避免悬空附塔。
    mask_layers(np.logical_or(lobes[0][1], lobes[1][1]), 276, 279, material.WFV)
    for z in (CZ - 190, CZ + 190):
        axis_bar((70, 280, z), (458, 280, z), material.WFV, 3)
    for x in (48, 264, 480):
        axis_bar((x, 274, 74), (x, 284, 454), material.POLISHED_BLACKSTONE_BRICKS, 3)

    # The whole silhouette is designed around the controller's X axis.
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]

    data = dict(key='i37', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
        controller_face='north', ports=ports,
        paths=[dict(name='双腔环形检修廊', min=[0, 8, 0], max=[528, 278, 528]),
               dict(name='中轴差分控制颈部', min=[178, 0, 12], max=[350, 76, 138])],
        zones=[dict(name='稳定参考腔', pos=[0, 260, 264]),
               dict(name='局部扰动试验腔', pos=[528, 260, 264]),
               dict(name='三轴矩形计量框', pos=[60, 214, 92]),
               dict(name='锚定/供能差分测量颈部', pos=[264, 70, 88]),
               dict(name='上部闭合承力冠梁', pos=[264, 280, 74])],
        description='世界维系试验以同构双腔作差分：一腔保留稳定参考态，另一腔接收局部扰动与锚定负载；两侧三轴矩形计量框在中轴控制颈部合束。多层环形承力廊同时容纳可更换仪器槽、介质回路、隔离层和检修通道；上部闭合冠梁与双腔外壁及落地计量框相连，构成完整受力路径。接口用于锚定记录、稳定介质、能量合同凭据、样件和实验记录的建筑表达，不代表传送、稳定场或HKE功能已实现。',
        construction_notes=dict(orientation='主控北向/-Z；蓝图坐标从0起算，X=264为整宽第265格。',
            anchor='结构实际边界529×529×285；粘贴高度须按目标维度可建Y范围另行选择。',
            boundary='只表达参考态/扰动态对照、锚定与供能的维系试验；不制造世界、不破坏玩家世界、不替代I43验收。',
            approval='全新建筑候选，未获批准、未进入正式结构索引、未实装。'))
    return cube, data
