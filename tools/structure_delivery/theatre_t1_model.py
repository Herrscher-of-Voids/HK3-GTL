import base64
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from theatre_t1_floor import build_floor
from theatre_t1_walls import build_walls
from theatre_t1_window import build_window


ROOT = Path(__file__).resolve().parents[2]
MC = Path('E:/Prism/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar')
GT = Path('C:/Users/OWNER/.gradle/caches/modules-2/files-2.1/com.gregtechceu.gtceu/gtceu-1.20.1/1.4.4/ac965814b9aa85fc60e688454d9bf07a1ea3f8f3/gtceu-1.20.1-1.4.4.jar')
FACES = ('east', 'west', 'south', 'north', 'down', 'up')

MODEL_NOTES = [
    '以剧情大厅为主体：暗红中轴毯、宽直梯、向两侧展开的上层楼梯、冷灰紫厅壁与金框圆窗。',
    '窗外石框保持圆弧，内部泪滴金框围住淡紫眼纹，并连接上方长竖窗。',
    '双眼纹尖拱、束柱、柱头肋梁、矩形凹格顶棚与锥形灯按剧情截图重建。',
    '楼梯、上下层回廊与红毯接续。完整大厅围护和屋顶可切换显示；导出保留完整建筑。',
    '地面金缝、栏杆重复节奏和背面围护为本项目补全；比例按参考镜头推定。',
    '方块采用原生像素贴图，混合格雷金属板、工业灯、本模组黑色机壳与冷灰紫石材。',
    '中央保留乌合之众与两只提线人偶的演出位置，当前交付为独立建筑待审稿。',
]
VIEWS = {
    'axis': dict(label='红毯中轴', center=[0, 280, -120], half=[440, 310, 250], direction=[0, .045, 1]),
    'stairs': dict(label='双侧楼梯与回廊', center=[0, 200, -300], half=[480, 210, 230], direction=[-.14, .62, 1]),
    'window': dict(label='长竖圆窗', center=[0, 335, -449], half=[140, 265, 35], direction=[0, 0, 1]),
    'niche': dict(label='双眼尖拱壁龛', center=[465, 170, 80], half=[75, 160, 100], direction=[-1, .08, .35], distance=260),
    'carpet': dict(label='红毯与金缝地砖', center=[0, 22, 320], half=[170, 45, 150], direction=[-.4, 1, .8]),
    'voxel': dict(label='阶梯与像素近景', center=[225, 82, -42], half=[40, 40, 48], direction=[-1, .7, 1], distance=160),
    'ceiling': dict(label='顶部矩形梁格', center=[0, 560, 0], half=[500, 100, 500], direction=[-.3, -1, 1]),
}
ANCHORS = [
    dict(id='ensemble_center', label='乌合之众演出中心候选', position=[0, 21, 305], purpose='人物合并阶段按实际肢体外形调整'),
    dict(id='left_puppet', label='左侧提线人偶候选', position=[-260, 115, 350]),
    dict(id='right_puppet', label='右侧提线人偶候选', position=[260, 115, 350]),
    dict(id='entrance', label='大厅红毯入口', position=[0, 21, 495]),
    dict(id='upper_landing', label='圆窗前中层平台', position=[0, 89, -205]),
]


def make_palette():
    existing = json.loads((ROOT/'deliveries/0005_W11_千律机械剧场_作者蓝图_A1_20261117/materials.json').read_text('utf8'))
    cached = {m['state']: m for m in existing}
    specs = [
        ('minecraft:light_blue_terracotta', '冷灰紫厅壁石材', MC, 'light_blue_terracotta'),
        ('minecraft:blue_terracotta', '深灰紫地砖与壁龛', MC, 'blue_terracotta'),
        ('gtceu:clean_machine_casing', '格雷灰紫洁净机壳束柱与肋梁', GT, 'assets/gtceu/textures/block/casings/solid/machine_casing_clean_stainless_steel.png'),
        ('minecraft:gold_block', '细金窗棂与地砖接缝', None, None),
        ('gtceu:white_metal_sheet', '格雷象牙白圆饰与灯芯', None, None),
        ('minecraft:red_nether_bricks', '暗红织毯色块', MC, 'red_nether_bricks'),
        ('minecraft:smooth_sandstone', '象牙色红毯窄边', MC, 'sandstone_top'),
        ('gtceu:yellow_borderless_lamp[bloom=true,inverted=true,lit=true,powered=false]', '格雷暖金锥灯', None, None),
        ('minecraft:white_concrete', '奶白窗面', MC, 'white_concrete'),
        ('minecraft:purple_stained_glass', '淡紫圆眼', MC, 'purple_stained_glass'),
        ('hk3gtl:casing_colored_black', '本模组黑色地基机壳', ROOT, 'src/main/resources/assets/hk3gtl/textures/block/casings/casing_colored_black.png'),
        ('minecraft:brown_terracotta', '暗金凹槽与灯座', MC, 'brown_terracotta'),
    ]
    palette = []
    for state, label, archive, entry in specs:
        if archive is None:
            material = dict(cached[state], label=label)
        else:
            if archive == ROOT:
                png = (ROOT/entry).read_bytes()
            else:
                if archive == MC:
                    entry = f'assets/minecraft/textures/block/{entry}.png'
                with ZipFile(archive) as package:
                    png = package.read(entry)
            url = 'data:image/png;base64,'+base64.b64encode(png).decode()
            material = dict(state=state, label=label, faces={f: url for f in FACES}, transparent=False,
                            emissive=False, source=dict(archive=str(archive), entry=entry,
                            png_sha256=hashlib.sha256(png).hexdigest(), texture_mode='原生像素贴图，无额外染色'))
        material.update(color='#ffe9ba' if material['emissive'] else '#ffffff')
        if state == 'minecraft:white_concrete':
            material.update(emissive=True, color='#fff0d4')
        palette.append(material)
    return palette


def build_model():
    parts = []
    for build in (build_floor, build_walls, build_window):
        current = build()
        parts.extend(current)
        print(f'{build.__name__}: {sum(len(p.p) for p in current):,}方块', flush=True)
    return parts, make_palette()
