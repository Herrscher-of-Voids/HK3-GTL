import base64
import hashlib
import math
from pathlib import Path
from zipfile import ZipFile

import numpy as np

from author_w05_shapes_20261115 import Part
from w08_common_20261116 import rod


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W13_蚀界研究母机_作者蓝图_A1_20261117'
LOG = ROOT / 'logs/0005-w13-author-blueprint-a1-20261117'
BLACK, STUDS, GRAY, SILVER, HK_BLACK, HK_GRAY, PURPLE, VOID, OBSIDIAN, STONE, VENT, CLEAN, WHITE, WHITE_STUDS, HK_WHITE, PORCELAIN, QUARTZ, GOLD, GOLD_LIGHT, PINK, MAGENTA, RED, HK_PINK, HK_MAGENTA, PINK_GLASS, MAGENTA_GLASS, RED_GLASS, PINK_LIGHT, MAGENTA_LIGHT, RED_LIGHT, BLUE, BLUE_GLASS, WHITE_LIGHT, COMPUTER, ADVANCED, CONTROL = range(1, 37)
CORE = np.array([0., 210., -.5])
CONTROLLER = np.array([0, 47, 470])
FACES = ('east', 'west', 'south', 'north', 'down', 'up')


def materials():
    gt = Path('C:/Users/OWNER/.gradle/caches/modules-2/files-2.1/com.gregtechceu.gtceu/gtceu-1.20.1/1.4.4/ac965814b9aa85fc60e688454d9bf07a1ea3f8f3/gtceu-1.20.1-1.4.4.jar')
    mc = Path('E:/Prism/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar')
    slots = [
        ('gtceu:black_metal_sheet', '黑钛主甲与黑盒边框', 'gt', 'decoration/metalsheet_black.png'),
        ('gtceu:black_studs', '铆接支撑骨架', 'gt', 'decoration/studs_black.png'),
        ('gtceu:gray_metal_sheet', '液压活塞与裸露机构', 'gt', 'decoration/metalsheet_gray.png'),
        ('gtceu:light_gray_metal_sheet', '断口金属与活塞杆', 'gt', 'decoration/metalsheet_light_gray.png'),
        ('hk3gtl:casing_colored_black', '深坑内构与坍缩体素', 'hk', 'casings/casing_colored_black.png'),
        ('hk3gtl:casing_colored_gray', '分层机壳与设备安装井', 'hk', 'casings/casing_colored_gray.png'),
        ('hk3gtl:casing_colored_purple', '暗紫防辐射装甲细带', 'hk', 'casings/casing_colored_purple.png'),
        ('minecraft:black_concrete', '黑盒吸光表面', 'mc', 'black_concrete.png'),
        ('minecraft:obsidian', '剥离数据块与反应池', 'mc', 'obsidian.png'),
        ('minecraft:polished_blackstone', '深坑阶梯衬层', 'mc', 'polished_blackstone.png'),
        ('gtceu:computer_heat_vent', '散热格栅与环带鳍片', 'gt', 'casings/hpca/computer_heat_vent_side.png'),
        ('gtceu:clean_machine_casing', '完整侧洁净装甲', 'gt', 'casings/solid/machine_casing_clean_stainless_steel.png'),
        ('gtceu:white_metal_sheet', '白色曲臂与圣柜边梁', 'gt', 'decoration/metalsheet_white.png'),
        ('gtceu:white_studs', '白甲分节加强筋', 'gt', 'decoration/studs_white.png'),
        ('hk3gtl:casing_colored_white', '圣柜连接器与臂根', 'hk', 'casings/casing_colored_white.png'),
        ('minecraft:white_concrete', '白金拘束框架主梁', 'mc', 'white_concrete.png'),
        ('minecraft:quartz_block', '白梁浅纹端面', 'mc', 'quartz_block_side.png'),
        ('minecraft:gold_block', '超导金线与白柜镶边', 'mc', 'gold_block.png'),
        ('gtceu:yellow_borderless_lamp', '金色导光节点', 'gt', 'lamps/yellow_borderless.png'),
        ('gtceu:pink_metal_sheet', '晶根内部骨架', 'gt', 'decoration/metalsheet_pink.png'),
        ('gtceu:magenta_metal_sheet', '侵蚀电路与露出断口', 'gt', 'decoration/metalsheet_magenta.png'),
        ('gtceu:red_metal_sheet', '黑盒裂缝深红衬板', 'gt', 'decoration/metalsheet_red.png'),
        ('hk3gtl:casing_colored_pink', '浅粉病毒逻辑晶根', 'hk', 'casings/casing_colored_pink.png'),
        ('hk3gtl:casing_colored_magenta', '核心晶簇暗部', 'hk', 'casings/casing_colored_magenta.png'),
        ('minecraft:pink_stained_glass', '粉色晶瓣与能量链', 'mc', 'pink_stained_glass.png'),
        ('minecraft:magenta_stained_glass', '深粉棱柱晶面', 'mc', 'magenta_stained_glass.png'),
        ('minecraft:red_stained_glass', '红色流体主管与断口拉索', 'mc', 'red_stained_glass.png'),
        ('gtceu:pink_borderless_lamp', '晶核光柱与数据雨', 'gt', 'lamps/pink_borderless.png'),
        ('gtceu:magenta_borderless_lamp', '环内二进制与结晶裂纹', 'gt', 'lamps/magenta_borderless.png'),
        ('gtceu:red_borderless_lamp', '黑盒脉冲电路', 'gt', 'lamps/red_borderless.png'),
        ('gtceu:light_blue_metal_sheet', '完整侧冷却管壳', 'gt', 'decoration/metalsheet_light_blue.png'),
        ('minecraft:cyan_stained_glass', '完整侧冷却介质', 'mc', 'cyan_stained_glass.png'),
        ('gtceu:white_lamp', '指示灯与晶芯高亮', 'gt', 'lamps/white.png'),
        ('gtceu:computer_casing', '黑盒内部算力模组', 'gt', 'casings/hpca/computer_casing/side.png'),
        ('gtceu:advanced_computer_casing', '主终端与高阶运算列', 'gt', 'casings/hpca/advanced_computer_casing/side.png'),
        ('minecraft:redstone_block', '唯一主控预览定位', 'mc', 'redstone_block.png')]
    result = []
    for state, label, source, entry in slots:
        if 'lamp' in state:
            state += '[bloom=true,inverted=true,lit=true,powered=false]'
        overrides = {}
        if 'computer_heat_vent' in state:
            overrides = dict(up='casings/hpca/computer_heat_vent_top_bot.png', down='casings/hpca/computer_heat_vent_top_bot.png')
        if state == 'minecraft:quartz_block':
            overrides = dict(up='quartz_block_top.png', down='quartz_block_bottom.png')
        if state in ('gtceu:computer_casing', 'gtceu:advanced_computer_casing'):
            folder = entry.rsplit('/', 1)[0]
            overrides = {face: f'{folder}/{name}.png' for face, name in dict(north='front', south='back', up='top', down='bottom').items()}
        faces, sources = {}, {}
        for face in FACES:
            path = overrides.get(face, entry)
            if source == 'hk':
                filename = ROOT / 'src/main/resources/assets/hk3gtl/textures/block' / path
                png = filename.read_bytes()
                location = str(filename.relative_to(ROOT))
            else:
                location = f'assets/{"gtceu" if source == "gt" else "minecraft"}/textures/block/{path}'
                with ZipFile(gt if source == 'gt' else mc) as archive:
                    png = archive.read(location)
            faces[face] = 'data:image/png;base64,' + base64.b64encode(png).decode()
            sources[face] = dict(entry=location, png_sha256=hashlib.sha256(png).hexdigest())
        result.append(dict(state=state, label=label, faces=faces, transparent='stained_glass' in state,
            emissive='lamp' in state, source=dict(kind=source, archive=str(gt if source == 'gt' else mc) if source != 'hk' else None, faces=sources, texture_mode='原生像素贴图，无额外染色')))
    return result


def prism(part, start, end, radius, state, sides=6, tip=.18):
    a, b = np.asarray(start, float), np.asarray(end, float)
    axis = (b - a) / np.linalg.norm(b - a)
    u = np.cross(axis, [0, 0, 1] if abs(axis[2]) < .9 else [0, 1, 0])
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    ring = np.array([math.cos(t) * u + math.sin(t) * v for t in np.arange(sides) * math.tau / sides])
    shoulder = a * .2 + b * .8
    part.hull(np.r_[a[None, :] + ring * radius * .65, shoulder[None, :] + ring * radius, b[None, :] + ring * radius * tip], state)


def line(part, a, b, state):
    a, b = np.asarray(a, float), np.asarray(b, float)
    part.points(np.linspace(a, b, int(np.max(abs(b - a))) * 2 + 1), state)
