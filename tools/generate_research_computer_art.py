"""研究点计算机专用纹理 / Dedicated research computer textures.
变更记录 #1：2026-09-22 15:39:00，内测5批次5。
新增原创16×16机箱、屏幕、端口与散热面，写入方块模型；无随机数或外部图片。
Deterministic Pillow artwork and cube model; no borrowed placeholder textures or external images.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/research_computer'
MODEL = ROOT / 'src/main/resources/assets/hk3gtl/models/block/research_point_computer.json'


def panel(face):
    """绘制铆接深蓝机箱，各面保留可辨识设备用途。 / Draw riveted navy casing with function-specific faces."""
    image = Image.new('RGBA', (16, 16), '#1b263b')
    d = ImageDraw.Draw(image)
    d.rectangle((0, 0, 15, 15), outline='#101927')
    d.line([(1, 14), (1, 1), (14, 1)], fill='#60758e')
    d.line([(2, 14), (14, 14), (14, 2)], fill='#0f1826')
    for x, y in [(2, 2), (13, 2), (2, 13), (13, 13)]: d.point((x, y), fill='#c4cbd1')
    if face == 'front':
        d.rectangle((3, 3, 12, 9), fill='#081829', outline='#437591')
        d.line([(4, 7), (5, 7), (6, 5), (7, 8), (9, 4), (10, 6), (11, 6)], fill='#78ece2')
        d.line((4, 11, 10, 11), fill='#738ba9')
        d.point((12, 11), fill='#efc65f')
        d.line((4, 12, 8, 12), fill='#263e59')
    elif face == 'side':
        for y in range(4, 12, 2):
            d.line((4, y, 11, y), fill='#081321');d.line((4, y + 1, 11, y + 1), fill='#354964')
        d.point((12, 5), fill='#68b7ba')
    elif face == 'back':
        d.rectangle((4, 4, 11, 11), fill='#101927', outline='#c79b4a')
        d.rectangle((6, 6, 9, 9), fill='#447c90')
        d.point((7, 7), fill='#b8f6ef')
    else:
        d.rectangle((4, 4, 11, 11), outline='#455c76')
        d.line([(5, 9), (7, 9), (7, 6), (10, 6)], fill='#669ea8')
        d.rectangle((9, 5, 10, 6), fill='#c79b4a')
    return image


if __name__ == '__main__':
    TEXTURES.mkdir(parents=True, exist_ok=True)
    for face in ['front', 'side', 'back', 'top']: panel(face).save(TEXTURES / (face+'.png'))
    texture = lambda name: 'hk3gtl:block/research_computer/'+name
    model = {'_comment': 'Change #1 2026-09-22 15:39:00 beta5 batch5. Original Python-generated computer faces. / 原创计算机外观，无占位素材。',
             'parent': 'minecraft:block/cube',
             'textures': {'particle': texture('side'), 'north': texture('front'), 'south': texture('back'),
                          'east': texture('side'), 'west': texture('side'), 'up': texture('top'), 'down': texture('side')}}
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    MODEL.write_text(json.dumps(model, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Generated four original machine textures and block model.')
