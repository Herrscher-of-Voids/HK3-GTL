# -*- coding: utf-8 -*-
"""I45固定科技蒸汽列车：独立锅炉机车、煤水车与双节客车几何。"""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 121, 181, 821, 60
NAME = 'hk3gtl-i45-steam-train-v1-20261029'
TITLE = '仿制的千界一乘·列车 · 靛蓝蒸汽机车与双节旅客车'


class Material:
    QCV = 'hk3gtl:voltage_machine_casing_qcv'
    CONTROL = 'minecraft:diamond_block'
    PORT = 'hk3gtl:industrial_port_casing'
    CLEAN = 'gtceu:clean_machine_casing'
    FRAME = 'gtceu:robust_machine_casing'
    VIBRATION = 'gtceu:vibration_safe_casing'
    ASSEMBLY = 'gtceu:assembly_line_casing'
    VENT = 'gtceu:computer_heat_vent'
    INSULATE = 'gtceu:nonconducting_casing'
    GEAR = 'gtceu:tungstensteel_gearbox'
    PIPE = 'gtceu:steel_pipe_casing'
    GRATE = 'gtceu:assembly_line_grating'
    HOT_PIPE = 'gtceu:tungstensteel_pipe_casing'
    FROST = 'gtceu:frostproof_machine_casing'
    TURBINE = 'gtceu:stainless_steel_turbine_casing'
    POWER = 'gtceu:high_power_casing'
    INERT = 'gtceu:inert_machine_casing'
    STRESS = 'gtceu:stress_proof_casing'
    GLASS = 'gtlcore:hsss_reinforced_borosilicate_glass'
    COMPUTER = 'gtceu:advanced_computer_casing'
    LASER = 'gtceu:laser_safe_engraving_casing'
    BLUE_GLASS = 'minecraft:light_blue_stained_glass'
    BLACK_GLASS = 'minecraft:black_stained_glass'
    GOLD = 'minecraft:gold_block'
    LIGHT = 'minecraft:sea_lantern'
    COAL = 'minecraft:coal_block'


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {s: i + 1 for i, s in enumerate(STATES)}
ROLES = {getattr(material, k): v for k, v in dict(
    QCV='锅炉压力壳、驾驶室、煤水车和旅客车主车皮，最多单一材料',
    CONTROL='烟箱正前面整宽中线的唯一主控标记', PORT='真实车体外壁齐平内嵌的八处接口标记',
    CLEAN='少量锅炉箍带、车头细边和轮缘金属', FRAME='底架、轴毂和车钩承力节点',
    VIBRATION='驾驶室目的地仪表的少量隔振座', ASSEMBLY='固定钢轨及车体纵梁',
    VENT='驾驶室与车顶电气设备的局部散热格栅', INSULATE='传送供能柜隔离护套',
    GEAR='可见连杆、曲柄与驱动轴承', PIPE='锅炉侧管与注水管', GRATE='外侧踏板与车厢贯通道地板',
    HOT_PIPE='主蒸汽管和锅炉热端连接', FROST='煤水车水箱内壁和检修口',
    TURBINE='前部汽缸箱和蒸汽泵外壳', POWER='煤水车及车载传送供能接驳',
    INERT='黑色烟箱、短烟囱与车轮内衬', STRESS='动轮轮圈、转向架与底盘受力座',
    GLASS='驾驶室仪表防护窗与锅炉水位观察窗', COMPUTER='目的地授权和抵达确认记录柜',
    LASER='少量火箱热端内衬', BLUE_GLASS='目的地状态窗', BLACK_GLASS='驾驶室及旅客车深色窗',
    GOLD='细窄汽笛、把手和车头标志', LIGHT='车头灯与车厢低数量照明', COAL='煤水车开放煤仓中的真实煤堆'
).items()}


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)
    m = material

    def box(a, b, state):
        x0, y0, z0 = map(int, a); x1, y1, z1 = map(int, b)
        assert 0 <= x0 <= x1 < W and 0 <= y0 <= y1 < H and 0 <= z0 <= z1 < D, (a, b)
        cube[y0:y1+1, z0:z1+1, x0:x1+1] = 0 if state is None else IDS[state]

    def shell(a, b, state, thickness=3):
        box(a, b, state)
        if all(b[i]-a[i]+1 > thickness*2 for i in range(3)):
            box(tuple(v+thickness for v in a), tuple(v-thickness for v in b), None)

    def cylinder_z(z0, z1, y, radius, state, inner=-1):
        x0, x1 = CX-radius, CX+radius
        yy, xx = np.ogrid[y-radius:y+radius+1, x0:x1+1]
        radial = (xx-CX)**2 + (yy-y)**2
        mask = (radial <= radius**2) & (radial > inner**2 if inner >= 0 else True)
        block = cube[y-radius:y+radius+1, z0:z1+1, x0:x1+1]
        block[:] = np.where(mask[:, None, :], IDS[state], block)

    def chimney(z, y0, y1, radius, state, inner=-1):
        zz, xx = np.ogrid[z-radius:z+radius+1, CX-radius:CX+radius+1]
        r = (xx-CX)**2 + (zz-z)**2
        mask = (r <= radius**2) & (r > inner**2 if inner >= 0 else True)
        block = cube[y0:y1+1, z-radius:z+radius+1, CX-radius:CX+radius+1]
        block[:] = np.where(mask[None, :, :], IDS[state], block)

    def wheel(z, radius, y):
        yy, zz = np.ogrid[y-radius:y+radius+1, z-radius:z+radius+1]
        dy, dz = yy-y, zz-z
        radial = dy*dy + dz*dz
        ring = (radial <= radius**2) & (radial >= (radius-5)**2)
        spokes = (radial < (radius-5)**2) & ((abs(dy) <= 2) | (abs(dz) <= 2) | (abs(dy-dz) <= 3) | (abs(dy+dz) <= 3))
        for x0, x1 in ((20, 30), (90, 100)):
            block = cube[y-radius:y+radius+1, z-radius:z+radius+1, x0:x1+1]
            block[:] = np.where(ring[:, :, None], IDS[m.STRESS], block)
            block[:] = np.where(spokes[:, :, None], IDS[m.INERT], block)
            outer = x0 if x0 < CX else x1
            face = cube[y-radius:y+radius+1, z-radius:z+radius+1, outer]
            face[:] = np.where((radial <= radius**2) & (radial >= (radius-2)**2), IDS[m.CLEAN], face)
            box((x0, y-5, z-5), (x1, y+5, z+5), m.FRAME)
        box((20, y-3, z-3), (100, y+3, z+3), m.FRAME)

    # 轨枕直接承托钢轨，全部轮对落在同一轨顶，不铺无用途实心大底板。
    for z in range(0, D, 12):
        box((5, 0, z), (115, 1, min(D-1, z+4)), m.FRAME)
    for x in (23, 93):
        box((x, 2, 0), (x+4, 5, D-1), m.ASSEMBLY)

    # 压力壳、烟箱和驾驶室保持空心，细箍带不淹没靛蓝车皮。
    cylinder_z(0, 294, 108, 44, m.QCV, 37)
    cylinder_z(0, 7, 108, 44, m.INERT)
    cylinder_z(0, 2, 108, 44, m.CLEAN, 41)
    for z in (14, 77, 140, 203, 266):
        cylinder_z(z, z+1, 108, 45, m.CLEAN, 43)
    box((18, 62, 4), (102, 71, 348), m.QCV)
    for x in (17, 99):
        box((x, 51, 8), (x+4, 61, 346), m.ASSEMBLY)
    for x0, x1 in ((1, 15), (105, 119)):
        box((x0, 64, 18), (x1, 67, 349), m.GRATE)
    box((0, 18, 0), (120, 25, 11), m.FRAME)
    for x in range(8, 115, 12):
        box((x, 26, 0), (x+2, 42, 7), m.CLEAN)
    box((49, 140, 0), (71, 147, 4), m.GOLD)
    box((53, 142, 0), (67, 146, 0), m.LIGHT)
    for z in (84, 151, 218, 285):
        wheel(z, 34, 39)
    wheel(29, 19, 24); wheel(328, 19, 24)
    for x0, x1 in ((15, 19), (101, 105)):
        box((x0, 40, 79), (x1, 46, 290), m.GEAR)
        for z in (84, 151, 218, 285):
            box((x0, 34, z-5), (x1, 51, z+5), m.CLEAN)
    for x0, x1 in ((6, 22), (98, 114)):
        box((x0, 49, 32), (x1, 62, 69), m.TURBINE)
        box((x0+4, 57, 57), (x1-4, 64, 74), m.HOT_PIPE)
    for x in (12, 105):
        box((x, 84, 26), (x+3, 87, 270), m.PIPE)
        box((x, 97, 45), (x+3, 100, 250), m.HOT_PIPE)
    for z in (26, 88, 150, 212, 248):
        box((15, 85, z), (26, 86, z+2), m.FRAME)
        box((94, 85, z), (105, 86, z+2), m.FRAME)
    chimney(54, 147, 180, 10, m.INERT, 5)
    chimney(54, 175, 179, 13, m.CLEAN, 9)
    chimney(54, 147, 149, 11, m.INERT)
    chimney(126, 148, 161, 13, m.QCV)
    chimney(192, 148, 158, 11, m.QCV)
    box((58, 158, 196), (62, 171, 200), m.GOLD)
    box((56, 168, 194), (64, 171, 202), m.GOLD)
    shell((13, 66, 286), (107, 147, 349), m.QCV, 4)
    box((9, 148, 282), (111, 153, 353), m.QCV)
    for x in (13, 104):
        box((x, 101, 302), (x+3, 132, 334), m.BLACK_GLASS)
        box((x, 135, 301), (x+3, 138, 335), m.CLEAN)
    box((35, 105, 346), (51, 128, 349), m.GLASS)
    box((69, 105, 346), (85, 128, 349), m.GLASS)
    shell((39, 70, 278), (81, 107, 291), m.LASER, 3)
    box((38, 70, 307), (82, 72, 330), m.FRAME)
    box((38, 73, 307), (82, 76, 330), m.GRATE)
    box((44, 77, 309), (76, 83, 316), m.VIBRATION)
    box((44, 84, 309), (76, 101, 316), m.COMPUTER)
    box((48, 91, 306), (72, 98, 308), m.BLUE_GLASS)
    box((46, 150, 297), (74, 154, 316), m.VENT)
    for x in (5, 108):
        for step in range(4):
            box((x, 34+step*8, 336-step*5), (x+7, 37+step*8, 342-step*5), m.GRATE)
            box((x, 38+step*8, 338-step*5), (x+1, 64, 339-step*5), m.FRAME)

    # 煤水车：开放煤仓容纳实际煤堆，独立水箱仅保留壁体、内部梁与检修通道。
    tender0, tender1 = 369, 489
    box((13, 48, tender0), (107, 57, tender1), m.QCV)
    shell((13, 58, tender0), (107, 130, tender1), m.QCV, 5)
    box((18, 126, tender0+5), (102, 130, tender1-5), None)
    box((18, 58, 370), (102, 125, 410), m.FROST)
    box((23, 63, 375), (97, 120, 405), None)
    box((18, 58, 412), (102, 63, 484), m.FRAME)
    for x in range(20, 103, 16):
        box((x, 64, 416), (min(102, x+2), 108, 483), m.FRAME)
    for z in range(416, 484):
        mound = max(0, int(24*(1-((z-450)/40)**2)))
        box((20, 64, z), (100, 105+mound, z), m.COAL)
    for z in (392, 466): wheel(z, 19, 24)
    for x in (17, 99): box((x, 36, tender0+7), (x+4, 49, tender1-7), m.STRESS)
    shell((17, 61, 372), (33, 96, 405), m.POWER, 3)
    shell((87, 61, 372), (103, 96, 405), m.INSULATE, 3)
    box((53, 123, 382), (67, 132, 396), m.CLEAN)

    # 两节客车有可见窗带、座席与中间通道，固定车钩连接完整列车。
    for c0, c1 in ((508, 655), (674, 820)):
        shell((13, 54, c0), (107, 137, c1), m.QCV, 4)
        for y in range(138, 153):
            inset = (y-138)//3
            box((13+inset, y, c0), (107-inset, y, c1), m.QCV)
        box((20, 138, c0+4), (100, 146, c1-4), None)
        for side in (13, 104):
            for z in range(c0+15, c1-12, 25):
                box((side, 91, z), (side+3, 120, min(c1-10, z+15)), m.BLACK_GLASS)
            box((side, 125, c0+4), (side+3, 126, c1-4), m.GOLD)
        for x in (17, 99): box((x, 36, c0+12), (x+4, 54, c1-12), m.STRESS)
        for z in (c0+24, c1-24): wheel(z, 19, 24)
        box((48, 58, c0+4), (72, 60, c1-4), m.GRATE)
        for z in range(c0+16, c1-12, 22):
            for a, b in ((22, 44), (76, 98)):
                for x in (a+2, b-2):
                    box((x, 58, z+2), (x+1, 60, z+7), m.FRAME)
                box((a, 61, z), (b, 75, z+9), m.QCV)
                box((a, 76, z+7), (b, 88, z+10), m.QCV)
            box((57, 132, z), (63, 134, z+5), m.LIGHT)
        box((42, 150, c0+20), (78, 154, c0+35), m.VENT)
        box((47, 62, c0), (73, 91, c0+3), m.BLUE_GLASS)
    for a, b in ((350, 368), (490, 507), (656, 673)):
        box((49, 47, a), (71, 54, b), m.FRAME)
        box((43, 59, a), (77, 62, b), m.GRATE)

    controller = [CX, 108, 0]
    box(controller, controller, m.CONTROL)
    ports = []
    for pid, pos, face, role in (
        ('EU-IN', [13, 81, 385], 'west', '煤水车供能柜：传送能量输入'),
        ('COAL-IN', [107, 88, 444], 'east', '煤仓装载侧壁：蒸汽造型的燃料补给候选'),
        ('WATER-IN', [107, 81, 385], 'east', '水箱连续壁：注水补给候选'),
        ('STEAM-SERVICE', [13, 82, 320], 'west', '驾驶室侧壁：蒸汽设备维护候选'),
        ('COORD-IN', [13, 78, 528], 'west', '首节客车授权设备：接收I44有效坐标'),
        ('AUTH-IN', [107, 78, 528], 'east', '首节客车登记设备：旅行授权资料'),
        ('ARRIVAL-OUT', [13, 78, 700], 'west', '后节客车记录设备：抵达回执'),
        ('RECOVERY-OUT', [107, 78, 700], 'east', '后节客车恢复设备：失败与恢复记录'),
    ):
        box(pos, pos, m.PORT)
        ports.append(dict(id=pid, pos=pos, face=face, role=role))
    data = dict(key='i45', name=NAME, title=TITLE, candidate_version='V1', size=[W, H, D],
        controller=controller, controller_face='north', ports=ports,
        description='深靛蓝卧式锅炉蒸汽机车，四对辐条动轮与可见连杆，短烟囱、驾驶室、煤水车及两节旅客车组成固定旅行装置；不是可移动实体。',
        zones=[dict(id='steam', name='锅炉与四轴蒸汽机车', pos=[60, 152, 140]),
               dict(id='cab', name='驾驶室与目的地授权', pos=[60, 153, 310]),
               dict(id='tender', name='煤水与传送供能', pos=[60, 58, 405]),
               dict(id='passenger1', name='前节旅客车', pos=[60, 152, 570]),
               dict(id='passenger2', name='后节旅客车', pos=[60, 152, 745])],
        paths=[], railway=dict(rail_centers_x=[25, 95], gauge=70, rail_top_y=5, wheel_bottom_y=5,
            body_width=95, maximum_width=121, driving_wheel_radius=34, driving_wheel_centers_z=[84, 151, 218, 285]))
    return cube, data
