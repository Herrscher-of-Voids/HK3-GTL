# -*- coding: utf-8 -*-
"""I44双楔准星与轴向观测坞：独立几何，非原作信标形状的复刻。"""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 241, 177, 281, 120
NAME = 'hk3gtl-i44-beacon-v1-20261029'
TITLE = '仿制的千界一乘·信标 · 双楔准星与轴向观测坞'


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


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {s: i + 1 for i, s in enumerate(STATES)}
ROLES = {getattr(material, k): v for k, v in dict(
    QCV='观测主腔、双楔准星承力体、贴体机舱和联锁交接室的主体',
    CONTROL='整宽中线、前端观测座连续外壁的唯一主控预览标记',
    PORT='贴体机舱前侧齐平内嵌的八处候选接口，不提供实际能力',
    CLEAN='光学口径外圈、维护廊和透镜座的洁净金属边框',
    FRAME='双楔根部、下承梁、轴向观测坞的结构框架',
    VIBRATION='光学读出与复测基准座的少量隔振支座',
    ASSEMBLY='光学组件装卸导轨与后部短交接工位',
    VENT='两侧贴体冷却设备与数据记录室散热顶盖',
    INSULATE='准星导能窄槽与供能设备隔离层',
    GEAR='准星俯仰锁定关节及观测口径调节箱',
    PIPE='沿机舱与观测腔下侧的冷却支路',
    GRATE='双侧轴向维护栈道与设备顶层检修网格',
    HOT_PIPE='沿准星根部的隔离回路主管',
    FROST='后侧冷却与测温机组的低温隔离层',
    TURBINE='可见换热机组与循环设备罩壳',
    POWER='能源接入与功率整形柜外壳；不代表新增能源系统',
    INERT='后部坐标交接设备的环境隔离内衬',
    STRESS='双楔斜向主脊及关节承压段',
    GLASS='观测口径保护窗与后部记录观察窗',
    COMPUTER='复测、失效坐标标记与目的地联锁记录机架',
    LASER='轴向校准读出头；酒红护罩只用于局部光学工位',
    BLUE_GLASS='少量受约束的瞄准光脉表现；非传送通道',
    BLACK_GLASS='坐标记录暗屏与光学遮光基准',
    GOLD='少量光学定位锁销及校准接点',
    LIGHT='维护照明和准星窄缝读出光窗'
).items()}


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)
    m = material

    def box(a, b, state):
        x, y, z = map(int, a); X, Y, Z = map(int, b)
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (a, b)
        cube[y:Y + 1, z:Z + 1, x:X + 1] = IDS[state] if state else 0

    def shell(a, b, state, t=4):
        box(a, b, state)
        if all(b[k] - a[k] + 1 > 2 * t for k in range(3)):
            box(tuple(v + t for v in a), tuple(v - t for v in b), None)

    def beam(a, b, state, r=2):
        n = max(abs(b[i] - a[i]) for i in range(3))
        for j in range(n + 1):
            p = [round(a[i] + (b[i] - a[i]) * j / max(1, n)) for i in range(3)]
            box(tuple(max(0, v - r) for v in p), tuple(min(s - 1, v + r) for v, s in zip(p, (W, H, D))), state)

    # 贴合设备的分立条形基础，保留中央下方、外侧场地和机舱间的空气。
    for a, b in (((0, 0, 25), (70, 9, 264)), ((170, 0, 25), (240, 9, 264)),
                 ((66, 0, 8), (174, 10, 260)), ((75, 0, 252), (165, 9, 280))):
        box(a, b, m.FRAME)
    for z in (40, 117, 204, 252):
        box((24, 8, z), (216, 16, z + 12), m.QCV)
    for x in (84, 144):
        box((x, 11, 9), (x + 12, 26, 256), m.FRAME)
        box((x + 3, 27, 12), (x + 9, 30, 253), m.ASSEMBLY)

    # 两侧是与主腔相连的机舱，端部各有一组真实可维护设备；不围成工厂城。
    for left, right in ((5, 66), (174, 235)):
        shell((left, 10, 32), (right, 59, 261), m.QCV, 5)
        box((left + 5, 30, 39), (right - 5, 34, 254), m.QCV)
        for z in range(45, 249, 34):
            box((left, 39, z), (left + 1, 48, z + 22), m.GLASS)
            box((right - 1, 39, z), (right, 48, z + 22), m.GLASS)
            shell((left + 9, 60, z), (right - 9, 73, z + 20), m.TURBINE, 3)
            box((left + 12, 74, z + 3), (right - 12, 77, z + 17), m.VENT)
        for z in (57, 159):
            shell((left + 10, 15, z), (right - 10, 28, z + 28), m.POWER, 3)
            box((left + 15, 16, z - 1), (right - 15, 23, z), m.INSULATE)
        box((left + 5, 52, 36), (left + 9, 56, 257), m.PIPE)
        box((right - 9, 52, 36), (right - 5, 56, 257), m.HOT_PIPE)
        box((left + 5, 60, 35), (left + 9, 62, 259), m.GRATE)
        box((right - 9, 60, 35), (right - 5, 62, 259), m.GRATE)

    # 纵轴观测腔：八角口径与厚壁空腔形成真正的内部光路，而非机车锅炉。
    yy, xx = np.ogrid[:H, :W]

    def octagon(rx, ry):
        a = np.abs(xx - CX) / rx; b = np.abs(yy - 78) / ry
        return (a <= 1) & (b <= 1) & (a + b <= 1.52)

    outer, inner = octagon(63, 48), octagon(51, 37)
    wall = outer & ~inner
    for z in range(18, 249):
        cube[:, z, :][wall] = IDS[m.QCV]
    ring = octagon(66, 51) & ~octagon(57, 42)
    for z in (18, 55, 94, 133, 172, 211, 244):
        for Z in range(z, min(z + 5, 249)):
            cube[:, Z, :][ring] = IDS[m.CLEAN]
    lining = octagon(52, 38) & ~octagon(48, 34)
    for z in range(28, 242):
        cube[:, z, :][lining] = IDS[m.INSULATE]
    # 前口径保护窗、分离的读出刻度和后端复测机，保持可视但不冒充旅行门。
    window = octagon(47, 33)
    for z in (22, 23):
        cube[:, z, :][window] = IDS[m.GLASS]
    for z in (35, 228):
        for x in (82, 153):
            shell((x, 50, z), (x + 5, 105, z + 7), m.LASER, 2)
            box((x + 1, 64, z - 1), (x + 4, 92, z), m.BLUE_GLASS)
        for y in (49, 102):
            box((99, y, z), (141, y + 3, z + 6), m.COMPUTER)
        for x in (96, 140):
            box((x, 43, z), (x + 4, 114, z + 6), m.CLEAN)
        box((96, 111, z), (144, 115, z + 6), m.CLEAN)
    for dx in (-32, -16, 0, 16, 32):
        box((CX + dx - 1, 111, 17), (CX + dx + 1, 114, 22), m.GOLD)
        box((CX + dx - 1, 41, 17), (CX + dx + 1, 44, 22), m.GOLD)
    # 双侧落地支撑承接整个长腔；带检修道和可见隔振座。
    for z in (28, 111, 195, 238):
        for x in (72, 156):
            box((x, 15, z), (x + 12, 33, z + 12), m.FRAME)
            box((x + 2, 34, z + 2), (x + 10, 38, z + 10), m.VIBRATION)
            box((x + 3, 39, z + 3), (x + 9, 45, z + 9), m.QCV)
    for x in (67, 167):
        box((x, 36, 29), (x + 6, 40, 246), m.GRATE)
        for z in range(36, 240, 22):
            box((x + 2, 41, z), (x + 4, 43, z + 2), m.LIGHT)

    # 侧根部渐倾的双楔准星，根部接机舱和横向承台；顶部自然形成整机高度。
    for sign in (-1, 1):
        for y in range(57, H):
            t = (y - 57) / (H - 1 - 57)
            center = CX + sign * round(87 - 56 * t)
            half = round(29 - 15 * t)
            z0, z1 = round(68 + 30 * t), round(218 - 38 * t)
            box((center - half, y, z0), (center + half, y, z1), m.QCV)
            # 双层薄壳之间留可维护的空腔，外壳的用途是准星读出与基准隔离。
            if y < H - 7 and z1 - z0 > 20:
                box((center - half + 7, y, z0 + 7), (center + half - 7, y, z1 - 7), None)
            if y % 22 < 5:
                box((center - half, y, z0), (center + half, y, z0 + 4), m.FRAME)
            if y % 22 in (0, 1):
                box((center - half, y, z1 - 3), (center + half, y, z1), m.STRESS)
            # 朝内的瞄准刻线只占窄缝；深靛蓝仍统领主立面。
            edge = center - sign * half
            box((edge, y, z0 + 9), (edge, y, z0 + 14), m.INSULATE)
            if 64 <= y <= 166:
                box((edge, y, z0 + 10), (edge, y, z0 + 12), m.LIGHT)
        base_x = 33 if sign < 0 else 207
        box((base_x - 18, 47, 68), (base_x + 18, 69, 218), m.QCV)
        for z in (82, 194):
            box((base_x - 21, 52, z), (base_x + 21, 72, z + 13), m.GEAR)
            beam((base_x, 63, z + 4), (CX + sign * 59, 121, z + 4), m.STRESS, 5)
        for y in (83, 127, 162):
            center = CX + sign * round(87 - 56 * (y - 57) / (H - 1 - 57))
            t = (y - 57) / (H - 1 - 57)
            box((center - 10, y, round(68 + 30 * t)),
                (center + 10, y + 3, round(218 - 38 * t)), m.CLEAN)

    # 后部联锁舱沿轴向接主腔：校验/记录目的地，不铺轨、不运人。
    shell((77, 11, 246), (163, 73, 280), m.QCV, 5)
    box((82, 74, 250), (158, 77, 277), m.GRATE)
    for x in (88, 109, 130):
        box((x, 15, 253), (x + 16, 19, 272), m.FRAME)
        shell((x, 19, 253), (x + 16, 50, 272), m.INERT, 3)
        box((x + 2, 26, 252), (x + 14, 40, 253), m.COMPUTER)
    for x in (86, 133):
        box((x, 53, 279), (x + 21, 65, 280), m.BLACK_GLASS)
    for x in (79, 155):
        box((x, 28, 280), (x + 6, 45, 280), m.GLASS)
    for left in (22, 185):
        shell((left, 15, 224), (left + 32, 43, 250), m.FROST, 4)
        box((left + 4, 22, 223), (left + 28, 36, 224), m.BLUE_GLASS)

    # 中央光学基座直接承托前口径；主控在它的连续外壁，而非外挂面板。
    shell((89, 11, 0), (151, 36, 29), m.QCV, 5)
    for x in (94, 137):
        box((x, 37, 12), (x + 9, 48, 29), m.FRAME)
    box((105, 31, 0), (135, 34, 2), m.CLEAN)
    box((CX - 3, 19, 0), (CX + 3, 25, 4), m.QCV)
    box((CX, 22, 0), (CX, 22, 0), m.CONTROL)
    labels = ('坐标与观测数据交接', '目的地锁定复测', '观测组件维护', '能源接入候选',
              '冷却介质输入', '冷却介质返回', '无人任务目标交接', 'I45目的地联锁交接')
    ports = []
    for i, (x, y) in enumerate(((22, 22), (48, 22), (22, 44), (48, 44),
                               (192, 22), (218, 22), (192, 44), (218, 44))):
        box((x - 2, y - 2, 32), (x + 2, y + 2, 36), m.QCV)
        box((x, y, 32), (x, y, 32), m.PORT)
        ports.append(dict(id=labels[i], pos=[x, y, 32], face='north',
                          purpose='仅工艺位置建议；实际数据交接和仓室能力按正式执行合同另验'))
    zones = [dict(name='轴向坐标观测与复测主腔', pos=[CX, 125, 120]),
             dict(name='落地双楔准星与锁定机构', pos=[33, 60, 120]),
             dict(name='供能冷却与维护机舱', pos=[20, 12, 110]),
             dict(name='目的地联锁与交接记录', pos=[CX, 73, 262]),
             dict(name='光学基座主控', pos=[CX, 13, 12])]
    data = dict(key='i44', name=NAME, title=TITLE, candidate_version='V1', size=[W, H, D],
        controller=[CX, 22, 0], controller_face='north', ports=ports, paths=[], zones=zones,
        description='两片从贴体机舱渐倾上升的深靛蓝准星楔壳，夹出开放的指向性轮廓；下方八角口径的卧式观测腔沿纵轴组织坐标输入、复测与后部目的地联锁。主控嵌于前端光学基座，接口位于两侧实际供能和维护机舱。',
        original_reference=dict(source='https://comic.bh3.com/book/1021',
            confirmed='参考第二神之键的空间观测与引导语义；原作车头身份不移植为I44信标本体。',
            limit='未取得可明确指认的原作信标外形；双楔准星与轴向观测坞是本项目工业化演绎，非原作造型复刻。'),
        construction_notes=dict(materials='QCV深靛蓝主体；洁净银色边框和少量冷光区分测量基准；颜色按现有贴图。',
            function='I44锁定复测、加强观测并交接目的地；I45独立固定列车才执行获准旅行。',
            boundary='不新增目标、神之键或维度，不解除终审维度限制；候选不代表已注册配方或能力。'))
    return cube, data


if __name__ == '__main__':
    cube, data = build()
    counts = np.bincount(cube.ravel(), minlength=len(STATES) + 1)
    print(dict(size=data['size'], blocks=int(counts[1:].sum()), materials=len(STATES),
        qcv=int(counts[IDS[material.QCV]]), unused=[s for s in STATES if not counts[IDS[s]]]), flush=True)
