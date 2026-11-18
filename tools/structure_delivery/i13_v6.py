# -*- coding: utf-8 -*-
"""I13 立式磁控包覆环：透空环架、径向喷镀和纵向载具。

变更记录 2026-10-14：新增独立候选造型，保留名称与尺寸基线；不改机器定义。
"""
import math
from i09_i13_v6_common import start, zone, route, finish, PIPE, GEAR, GRATE, PANEL

SHELL = 'hk3gtl:voltage_machine_casing_hrv'
WHITE = 'gtceu:clean_machine_casing'
RIB = 'gtceu:solid_machine_casing'
VACUUM = 'gtceu:high_power_casing'
GLASS = 'gtceu:fusion_glass'
CHEMICAL = 'gtceu:corrosion_proof_casing'
EMITTER = 'gtlcore:multi_functional_casing'
VENT = 'gtceu:computer_heat_vent'


def octagon(a, cx, cy, z0, z1, outer, inner, mat):
    """以完整立方体组成连续八边环，每面厚度有实体连接。"""
    for x in range(cx-outer, cx+outer+1):
        for y in range(cy-outer, cy+outer+1):
            dx, dy = abs(x-cx), abs(y-cy)
            outside = max(dx, dy) <= outer and dx+dy <= round(outer*1.42)
            hole = max(dx, dy) < inner and dx+dy < round(inner*1.42)
            if outside and not hole:
                a.box((x, y, z0), (x, y, z1), mat)


def i13():
    a = start('i13', '崩坏抗性包覆阵列', (53, 45, 45), '立式八极磁控包覆环',
              '载具进样→真空定位→八极径向包覆→背侧固化测厚→成品出样')
    # 设备基础分为双环承台、两侧服务岛与纵向载具床；检修带沿真实工作面组织。
    a.box((5, 0, 18), (47, 2, 32), WHITE)
    a.box((1, 0, 8), (13, 0, 18), WHITE)
    a.box((40, 0, 8), (51, 0, 39), WHITE)
    a.box((20, 0, 7), (32, 1, 43), WHITE)
    a.box((4, 0, 7), (48, 0, 8), GRATE)
    for x in (13, 17, 21, 26, 31, 35, 39):
        a.box((x, 0, 5), (x, 0, 8), WHITE)
    for x in (4, 48):
        a.box((x, 0, 14), (x+1, 0, 39), GRATE)
    a.box((4, 0, 38), (49, 0, 39), GRATE)
    a.box((4, 0, 8), (5, 0, 14), GRATE)
    a.box((48, 0, 8), (49, 0, 14), GRATE)
    a.box((2, 0, 17), (4, 0, 39), GRATE)
    a.paths.extend([
        {'name': '西侧喷镀检修走道', 'min': [2, 1, 18], 'max': [3, 3, 37]},
        {'name': '背侧西段维护走道', 'min': [6, 1, 38], 'max': [19, 3, 39]},
        {'name': '背侧东段维护走道', 'min': [33, 1, 38], 'max': [39, 3, 39]},
    ])

    # 前后两道环梁形成真空壳的机械边界，浅色外缘与酒红主壳分出承重/工艺层。
    octagon(a, 26, 24, 20, 27, 19, 16, WHITE)
    octagon(a, 26, 24, 19, 20, 18, 15, SHELL)
    octagon(a, 26, 24, 27, 28, 18, 15, SHELL)
    octagon(a, 26, 24, 21, 26, 15, 14, GLASS)
    # 厚环的八个磁控单元与径向喷头都连接在真空壳上，中央仍保留可读空腔。
    for dx, dy in ((0, 16), (11, 11), (16, 0), (11, -11),
                   (0, -16), (-11, -11), (-16, 0), (-11, 11)):
        x, y = 26+dx, 24+dy
        a.box((x-1, y-1, 18), (x+1, y+1, 20), VACUUM)
        a.box((x-1, y-1, 27), (x+1, y+1, 29), GEAR)
        end = (26+round(dx*.76), 24+round(dy*.76), 30 if (dx, dy) == (0, -16) else 24)
        # 底极喷头后移六格，避开载具的升降支座，同时保留独立供膜通路。
        if (dx, dy) == (0, -16):
            a.line((x, y, 24), (x, y, 30), PIPE)
            a.line((x, y, 30), end, PIPE)
        else:
            a.line((x, y, 24), end, PIPE)
        a.box((end[0]-1, end[1]-1, end[2]-1), (end[0]+1, end[1]+1, end[2]+1), EMITTER)

    # 环架由四组外倾撑脚托住；支撑连接斜切边，底部不封住观察孔。
    for x, sign in ((9, -1), (43, 1)):
        for z in (19, 28):
            a.box((x-2, 3, z-1), (x+2, 4, z+1), VACUUM)
            a.box((x-1, 4, z), (x+1, 15, z+1), RIB)
            a.line((x, 5, z), (x-sign*6, 13, z), SHELL)
            a.box((x-1, 15, z), (x+1, 18, z+1), WHITE)
    # 顶冠是环架的电源/冷却分配梁，环外边缘散热片保持有序节奏。
    a.box((21, 42, 22), (31, 44, 25), VACUUM)
    a.box((23, 43, 21), (29, 43, 26), SHELL)
    for x in range(15, 38, 4):
        a.box((x, 38, 22), (x+1, 42, 25), VENT)
        a.line((x, 38, 23), (26, 40, 23), PIPE)

    # 纵向载具床经过环中心的下缘，工件由实心升降支座托举，透明定位舱可见内部。
    a.box((23, 2, 8), (29, 5, 41), VACUUM, True)
    for x in (23, 29):
        a.box((x, 6, 9), (x, 6, 41), GEAR)
    for z in range(9, 42, 4):
        a.box((24, 6, z), (28, 6, z+1), GRATE)
    a.box((24, 7, 21), (28, 12, 25), SHELL)
    a.box((25, 13, 22), (27, 20, 24), PIPE)
    for y in range(19, 30):
        radius = 5 if 21 <= y <= 27 else (3 if y in (20, 28) else 2)
        for dx in range(-radius, radius+1):
            for dz in range(-radius, radius+1):
                metric = abs(dx)+abs(dz)
                if max(0, radius-2) <= metric <= radius:
                    a.set(26+dx, y, 24+dz, GLASS)
        if y in (19, 29):
            a.box((24, y, 22), (28, y, 26), EMITTER)
    a.box((26, 20, 24), (26, 28, 24), EMITTER)
    a.box((25, 22, 24), (27, 26, 24), SHELL)
    # 膜料槽位于前西侧，与供料管分开；后西侧真空泵抽气至包覆环。
    for cx, height in ((5, 13), (11, 17)):
        for y in range(1, height+1):
            a.ring((cx, y, 12), 2, 3, CHEMICAL if y % 5 else SHELL)
        a.box((cx-1, height+1, 10), (cx+1, height+1, 14), GEAR)
        a.line((cx, height+1, 12), (cx, height+3, 12), PIPE)
    a.box((7, 3, 30), (16, 8, 35), VACUUM, True)
    for x in (9, 13):
        a.box((x, 4, 30), (x+1, 7, 30), GEAR)
    a.box((7, 0, 32), (16, 2, 36), WHITE)
    route(a, '膜料计量塔', '八极喷镀环', [(11, 11, 12), (16, 11, 12), (16, 11, 19), (18, 11, 19)])
    route(a, '真空泵组', '八极喷镀环', [(12, 8, 32), (12, 10, 32), (12, 10, 27), (15, 10, 27)])

    # 后东侧的薄片固化/测厚架与矩形换热器错落布置，不让辅机抢过主环的轮廓。
    a.box((41, 1, 15), (49, 5, 35), VACUUM, True)
    for z in range(16, 36, 3):
        a.box((42, 6, z), (48, 23, z), VENT)
        a.box((44, 24, z), (46, 26, z), SHELL)
    a.box((43, 6, 34), (47, 25, 35), PIPE)
    route(a, '八极喷镀环', '东侧换热器', [(43, 24, 25), (48, 24, 25), (48, 24, 34), (46, 24, 34)])
    for x in (21, 31):
        a.box((x, 2, 36), (x+1, 16, 37), SHELL)
    a.box((21, 15, 36), (32, 17, 37), PANEL)
    a.box((25, 13, 36), (28, 15, 37), EMITTER)
    route(a, '载具床', '固化测厚门', [(26, 6, 31), (26, 6, 36)], GRATE)
    # 接口后方低位管汇与设备基础连接，前侧无需跨越任何凸起构件。
    a.box((11, 0, 7), (41, 0, 8), WHITE)
    for x in (13, 17, 21, 31, 35, 39):
        a.line((x, 1, 7), (x, 1, 8), PIPE)

    zone(a, '立式八极包覆环', (7, 5, 18), (45, 44, 31), '八极磁控与真空约束；底极喷头后移避开升降支座', 'sputtering_ring')
    zone(a, '纵向载具与定位舱', (21, 2, 8), (32, 29, 41), '纳米群载具定位、进样和出样', 'transport')
    zone(a, '膜料计量塔', (2, 1, 9), (13, 20, 15), '包覆介质计量与喷镀供料', 'feed')
    zone(a, '真空泵组', (7, 0, 30), (16, 10, 36), '反应腔抽气与回收', 'vacuum')
    zone(a, '东侧换热器', (41, 1, 15), (49, 26, 35), '靶材冷却和工艺热回收', 'cooling')
    zone(a, '固化测厚门', (21, 2, 36), (32, 17, 37), '固化、厚度检测与出样', 'inspection')
    return finish(a, 'i13-coating-array-v6',
                  '一座酒红与银白的立式八极包覆环：前后厚环梁围出透明真空边界，八个径向喷镀单元面向中央定位舱；纵向载具床穿过环架下部，左侧计量与抽气，右侧片式换热，背侧独立固化测厚。透空主环与分开的承台让工艺路径可见。',
                  [('SWARM', '受控纳米群输入'), ('COATING', '抗性包覆介质输入'), ('POWER', '供能'),
                   ('COOLANT', '冷却回路候选'), ('PRODUCT', '包覆纳米群输出'), ('REJECT', '失活单元与回收液输出')],
                  WHITE, ['GTCEu ASSEMBLY_LINE（GTMachines.java:940）：连续工艺轴与不同进出料端',
                          'GTLCore PCB_FACTORY（AdvancedMultiBlockMachineStructureA.java:22）：侧置工艺槽与回流管网',
                          'GTLsupb MICROCOSM_FOUNDRY（MicrocosmPatternLayers.java）：弧形支架、独立核心与空气间隙'])
