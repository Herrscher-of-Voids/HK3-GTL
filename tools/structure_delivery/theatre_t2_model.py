import json

from theatre_t1_model import ANCHORS, ROOT, VIEWS as T1_VIEWS, make_palette as t1_palette
from theatre_t1_walls import build_walls
from theatre_t2_architecture import build_details
from theatre_t2_ceiling import build_ceiling_details
from theatre_t2_floor import build_floor
from theatre_t2_window import build_window


MODEL_NOTES = [
    '剧情大厅细节精修：冷灰紫厅壁、暗红毯和奶白金框圆窗沿用上一版形制。',
    '楼梯与回廊改为原作石质纺锤栏杆，锥形灯改为开口金属罩与独立白色灯芯。',
    '红毯连续卷叶纹穿过中央阶梯，并接续至中层平台、双侧楼梯与二层廊道。',
    '圆窗补上分层斜阶、放射砌缝、小三叶圆饰和更细的眼纹；长竖窗与内部泪滴依原图连接。',
    '柱础补入暗底饰牌、菱纹与细金线，双眼壁龛补入同心眼睑、瞳孔和中央冠饰。',
    '矩形凹顶补双层内收线脚、阶梯收边和梁交点嵌板。',
    '窗框、灯罩、栏杆及饰牌按剧情截图重建；具体重复数量、整数格厚度和背面固定件为本项目补全。',
    '全部可见曲线均由整数格方块形成，预览保留原生像素贴图，完整建筑可导出NBT。',
    '当前为独立剧场细节待审稿，中央演出位置供乌合之众与两只提线人偶后续合并使用。',
]
VIEWS = dict(T1_VIEWS)
VIEWS.update({
    'lantern': dict(label='开口灯罩与白色灯芯', center=[236, 66, 126], half=[26, 48, 28], direction=[-.9, .22, 1], distance=150),
    'balustrade': dict(label='纺锤栏杆与石扶手', center=[229, 70, 35], half=[18, 36, 65], direction=[-.9, .35, 1], distance=170),
    'window_eye': dict(label='圆窗眼纹与环周圆饰', center=[0, 215, -445], half=[125, 130, 32], direction=[.12, 0, 1], distance=400),
    'column_base': dict(label='柱础饰牌与分层石座', center=[375, 73, 180], half=[50, 62, 50], direction=[-.7, .13, 1], distance=200),
    'niche': dict(label='双眼尖拱壁龛', center=[465, 170, 300], half=[75, 160, 100], direction=[-1, .08, .05], distance=260),
    'niche_eye': dict(label='双眼浮雕与尖菱冠饰', center=[469, 165, 300], half=[28, 85, 93], direction=[-1, .03, 0], distance=220),
    'carpet': dict(label='连续红毯织纹', center=[0, 21, 255], half=[155, 20, 120], direction=[-.2, 1, .8]),
})


def make_palette():
    palette = t1_palette()
    original = json.loads((ROOT/'deliveries/0005_W11_千律机械剧场_作者蓝图_A1_20261117/materials.json').read_text('utf8'))
    lamp = next(m for m in original if m['state'].startswith('gtceu:white_lamp['))
    palette.append(dict(lamp, label='格雷白色工业灯芯', color='#fff0d8'))
    return palette


def build_model():
    parts = []
    for build in (build_floor, build_walls, build_window, build_details, build_ceiling_details):
        current = build()
        parts.extend(current)
        print(f'{build.__name__}: {sum(len(p.p) for p in current):,}方块', flush=True)
    return parts, make_palette()
