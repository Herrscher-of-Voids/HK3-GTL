"""原创理之核心像素贴图 / Original procedural reason-core pixel texture.
变更记录 #1：2026-09-22 15:14:00，内测5批次4。
新增：Python/Pillow绘制16×16透明PNG，蓝白晶体、机械金环与悬浮碎片。
无外部图片输入、无随机数；相同脚本输出相同像素。替换原版紫水晶引用。
Deterministic RGBA pixels, no external artwork; replace the vanilla amethyst reference.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'src/main/resources/assets/hk3gtl/textures/item/imitation_reason_core.png'


def generate():
    """画透明底的可辨识核心轮廓；直接输出游戏纹理，无缩放滤波。
    Draw a readable transparent sprite at native resolution, without resampling.
    """
    image = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # 深蓝晶体外轮廓与分面，顶尖向上；蓝色象征理之权能。
    # Dark silhouette and asymmetric facets keep the blue crystal readable at 16 px.
    draw.polygon([(8, 0), (12, 5), (11, 11), (7, 15), (4, 10), (4, 5)], fill='#102d58')
    draw.polygon([(8, 1), (10, 5), (8, 8), (5, 5)], fill='#95f2fa')
    draw.polygon([(5, 6), (8, 9), (7, 13), (5, 10)], fill='#2b91d9')
    draw.polygon([(11, 6), (10, 10), (8, 13), (9, 8)], fill='#3655af')
    draw.line([(8, 2), (7, 5), (8, 8), (7, 12)], fill='#e5ffff', width=1)
    # 倾斜金色机械约束环，前后错层而非给宝石换色。
    # A tilted containment ring crosses the facets with front/back depth cues.
    draw.line([(1, 9), (2, 6), (5, 4), (7, 4)], fill='#69503c', width=1)
    draw.line([(9, 10), (12, 9), (14, 6), (13, 5)], fill='#69503c', width=2)
    draw.line([(1, 9), (4, 11), (8, 11), (12, 9), (14, 6)], fill='#e4b960', width=1)
    draw.point((4, 10), fill='#fff1af')
    draw.point((11, 9), fill='#fff1af')
    draw.rectangle((1, 3, 2, 4), fill='#3ca1cd')
    draw.point((1, 3), fill='#ccfcff')
    draw.rectangle((13, 12, 14, 13), fill='#3655af')
    draw.point((13, 12), fill='#95f2fa')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    return image


if __name__ == '__main__':
    result = generate()
    assert result.mode == 'RGBA' and result.size == (16, 16)
    assert result.getpixel((0, 0))[3] == 0
    print('Generated original 16x16 RGBA reason-core texture.')
