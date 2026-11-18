# -*- coding: utf-8 -*-
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl/textures/item'
OUT = ROOT / 'deliveries/0002贴图材质_审定重绘_R4_20261114'
REFERENCES = OUT / 'references'
IDS = ('honkai_fuel_rod', 'dense_honkai_fuel_rod', 'depleted_honkai_fuel_rod',
       'depleted_dense_honkai_fuel_rod', 'broken_honkai_fuel_rod', 'broken_dense_honkai_fuel_rod',
       'rejected_fuel_rod', 'fuel_encapsulation_part', 'recovered_fuel_casing_material',
       'inactive_fuel_residue', 'fuel_matrix', 'fuel_blending_residue')
NAMES = ('崩坏燃料棒', '浓缩崩坏燃料棒', '乏崩坏燃料棒', '乏浓缩崩坏燃料棒',
         '破损崩坏燃料棒', '破损浓缩崩坏燃料棒', '不合格燃料棒', '燃料封装组件',
         '回收燃料壳体材料', '失活燃料残渣', '崩坏燃料基质', '燃料调配尾料')


def mother(dense=False):
    name = 'dense_honkai_fuel_rod.png' if dense else 'honkai_fuel_rod.png'
    return Image.open(REFERENCES / name).convert('RGBA').resize((64, 64), Image.Resampling.NEAREST)


def spent(dense=False):
    im = mother(dense)
    for y in range(64):
        for x in range(64):
            r, g, b, a = im.getpixel((x, y))
            cx, cy = (34, 27) if dense else (31, 32)
            core = ((x - cx) / 11) ** 2 + ((y - cy) / 13) ** 2 < 1 and r > 150 and g > 105
            if core:
                l = (r + g + b) // 10
                im.putpixel((x, y), (l, l, l + 10, a))
            elif r > g * 1.15 and r > b * 1.12:
                l = (r * 2 + g * 3 + b) // 6
                im.putpixel((x, y), (l * 3 // 5, l * 3 // 5, min(255, l * 3 // 5 + 12), a))
    return im


def broken(dense=False):
    im = spent(dense)
    d = ImageDraw.Draw(im)
    points = [(7, 35), (19, 32), (28, 37), (36, 31), (44, 34), (56, 28)] if dense else [(17, 31), (24, 29), (30, 33), (36, 30), (43, 32)]
    d.line(points, fill='#171820', width=3)
    d.line([(x, y - 2) for x, y in points], fill='#b1aabd', width=1)
    d.line(points[1:4], fill=(0, 0, 0, 0), width=1)
    d.line((38, 34, 40, 42, 37, 46), fill='#24202e', width=2)
    return im


def rejected():
    im = Image.open(REFERENCES / 'honkai_fuel_rod_casing.png').convert('RGBA')
    top = im.crop((23, 2, 41, 14))
    ImageDraw.Draw(im).rectangle((23, 2, 41, 13), fill=(0, 0, 0, 0))
    im.alpha_composite(top, (26, 3))
    d = ImageDraw.Draw(im)
    d.line((28, 30, 31, 33, 29, 36, 33, 41), fill='#e0b0ec', width=1)
    d.line((30, 31, 33, 34, 31, 37), fill='#26152f', width=1)
    d.rectangle((35, 17, 37, 20), fill='#b07946')
    return im


def seals():
    im = Image.new('RGBA', (64, 64))
    cap = Image.open(REFERENCES / 'honkai_fuel_rod_casing.png').convert('RGBA').crop((24, 4, 40, 20))
    for y in range(16):
        for x in range(16):
            r, g, b, a = cap.getpixel((x, y))
            l = min(245, 110 + (r + g + b) // 3)
            cap.putpixel((x, y), (l, l + 3, min(255, l + 7), a))
    for x, y in [(10, 31), (27, 17), (38, 37)]:
        im.alpha_composite(cap, (x, y))
    return im


def recovered():
    casing = Image.open(REFERENCES / 'honkai_fuel_rod_casing.png').convert('RGBA')
    im = Image.new('RGBA', (64, 64))
    upper = casing.crop((24, 5, 40, 28)).rotate(38, expand=True, resample=Image.Resampling.NEAREST)
    lower = casing.crop((24, 30, 40, 59)).rotate(-48, expand=True, resample=Image.Resampling.NEAREST)
    im.alpha_composite(upper, (7, 17))
    im.alpha_composite(lower, (27, 22))
    d = ImageDraw.Draw(im)
    d.line((21, 29, 25, 26, 26, 28), fill='#e1dce8')
    d.line((32, 43, 37, 44, 40, 42), fill='#a39eb0')
    return im


def residue(blended=False):
    im = Image.new('RGBA', (64, 64))
    d = ImageDraw.Draw(im)
    pal = ('#292331', '#514257', '#796578', '#a08c9d') if blended else ('#24242b', '#42404c', '#646170', '#8b8792')
    for points in [[(8, 42), (14, 34), (24, 36), (29, 45), (21, 51), (10, 49)],
                   [(24, 36), (30, 24), (40, 28), (45, 41), (35, 49), (28, 45)],
                   [(41, 43), (48, 36), (55, 41), (54, 49), (46, 52)]]:
        d.polygon(points, fill=pal[1], outline=pal[0])
        d.line(points[:3], fill=pal[2])
    for x, y in [(14, 39), (18, 45), (30, 34), (35, 29), (37, 41), (48, 43)]:
        d.line((x, y, x + 3, y), fill=pal[3])
        d.point((x + 1, y + 2), fill=pal[0])
    if blended:
        d.line((30, 31, 33, 33, 35, 32), fill='#b48853')
        d.line((15, 43, 18, 42), fill='#b39765')
    return im


def matrix():
    im = Image.new('RGBA', (64, 64))
    d = ImageDraw.Draw(im)
    d.polygon([(11, 24), (29, 14), (53, 27), (35, 38)], fill='#969078', outline='#262d37')
    d.polygon([(11, 24), (35, 38), (35, 53), (11, 40)], fill='#525154', outline='#252a32')
    d.polygon([(35, 38), (53, 27), (53, 43), (35, 53)], fill='#353a43', outline='#1d2530')
    for x, y in [(18, 24), (27, 20), (35, 24), (43, 28)]:
        d.polygon([(x, y), (x + 4, y - 2), (x + 8, y), (x + 4, y + 3)], fill='#332e29', outline='#d7b878')
        d.line((x + 1, y, x + 4, y + 1), fill='#876b46')
    for y in [31, 36, 41]:
        d.line((15, y, 31, y + 9), fill='#b99a63', width=2)
        d.line((39, y + 9, 49, y + 3), fill='#8f9ca7')
    d.rectangle((26, 35, 30, 40), fill='#30263e', outline='#bdb5c6')
    return im


DRAW = dict(zip(IDS, [mother, lambda: mother(True), spent, lambda: spent(True), broken,
    lambda: broken(True), rejected, seals, recovered, residue, matrix, lambda: residue(True)]))


def draw(ident):
    return DRAW[ident]()


FACTS = [
    ('industrial_fuel_rod_encapsulation / hk3gtl_honkai_fuel_rod', '现有普通燃料棒；灌装棒壳、封装件与液态燃料，也有魂钢装配路线。', '恢复已有普通燃料棒源图，缩小到64，不另创棒体。', 'honkai_fuel_rod.png'),
    ('industrial_dense_rod_encapsulation / hk3gtl_dense_fuel_rod', '现有浓缩棒；封装用更多密封件与浓缩液态燃料，亦可由普通棒及压缩核心装配。', '恢复已有浓缩燃料棒源图，保留锁环、端盖、倾斜方向与浓缩舱体。', 'dense_honkai_fuel_rod.png'),
    ('industrial_reactor_i19 / industrial_spent_rod_reprocessing', '普通燃料棒发电后的乏棒，可再处理回收壳材与残渣。', '直接修改普通母图；仅降低燃料活性区明度和色度，壳体与方向不变。', 'honkai_fuel_rod.png'),
    ('industrial_reactor_i20 / industrial_dense_spent_rod_reprocessing', '浓缩棒发电后的乏棒；与普通乏棒分别处理。', '直接修改浓缩母图；失活内芯保留原有锁环、端盖与粗短外壳。', 'dense_honkai_fuel_rod.png'),
    ('industrial_spent_rod_casing_opening', '普通乏棒开壳后产生破损棒，后续回收壳材与失活残渣。', '从普通乏棒派生裂口与开壳切缝；沿用母图轮廓和内部零件。', 'honkai_fuel_rod.png'),
    ('industrial_dense_spent_rod_casing_opening', '浓缩乏棒开壳后产生破损浓缩棒。', '从浓缩乏棒派生开壳切缝与壳裂；保留浓缩母图的锁环身份。', 'dense_honkai_fuel_rod.png'),
    ('industrial_fuel_rod_isolation_experiment', '燃料封装样件经隔离检测后形成的不合格燃料棒。', '直接修改既有空壳，错位顶盖和细裂缝表示封装失败，不新建通用框架。', 'honkai_fuel_rod_casing.png'),
    ('industrial_fuel_encapsulation_part', 'PTFE板与铂箔制成的耐化学密封组件；用于棒壳灌装。', '直接沿用既有棒壳顶部截面的形状和像素轮廓，改为PTFE与铂箔内衬；不是另一种棒壳。', 'honkai_fuel_rod_casing.png'),
    ('industrial_spent_rod_reprocessing / industrial_recovery_fuel_casing', '乏棒或破损棒再处理得到的壳体材料，可重制空壳。', '直接裁取已有壳体的上下段，转为拆解金属段；沿用原有壁厚、颜色和端部。', 'honkai_fuel_rod_casing.png'),
    ('industrial_spent_rod_reprocessing', '再处理乏棒与破损棒后分离出的失活燃料残渣。', '灰紫失活颗粒团，保留金属与燃料分离后的非发光物态；不是另一种燃料棒。', ''),
    ('industrial_fuel_matrix', '钨钢板、PBI箔、场发生器和发射器装配，用于混合液态燃料。', '有分布空腔和褐色PBI绝缘层的钨钢承载块；与棒壳保持不同工艺身份。', ''),
    ('industrial_liquid_fuel_blending / industrial_liquid_fuel_concentration', '燃料调配后的固体尾料。', '带PBI薄片和低活性燃料颗粒的调配沉渣，颗粒和层片形态由副产工艺推导。', ''),
]


def main():
    REFERENCES.mkdir(parents=True, exist_ok=True)
    for name in ['honkai_fuel_rod.png', 'dense_honkai_fuel_rod.png']:
        shutil.copyfile(ASSETS / 'honkai' / name, REFERENCES / name)
    shutil.copyfile(ASSETS / 'honkai_fuel_rod_casing.png', REFERENCES / 'honkai_fuel_rod_casing.png')
    dst = OUT / 'textures/item'
    dst.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (1200, 630), '#19242c')
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 14)
    rows = []
    for i, (ident, name, (locator, fact, interpretation, reference)) in enumerate(zip(IDS, NAMES, FACTS)):
        im = draw(ident)
        im.save(ASSETS / (ident + '.png'), optimize=True)
        im.save(dst / (ident + '.png'), optimize=True)
        x, y = i % 6 * 200, (i // 6 + 1) * 210
        tile = im.resize((160, 160), Image.Resampling.NEAREST)
        sheet.paste(tile, (x + 20, y + 4), tile)
        d.text((x + 8, y + 177), name, font=font, fill='#e9e7de')
        rows.append(dict(id=ident, name=name, function_process_facts=fact,
            text_evidence_paths=['src/main/resources/data/hk3gtl/research/industrial_processes.json',
                'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/Hk3FuelRodBootstrapRecipes.java',
                'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/Hk3LiquidLineRecipes.java',
                'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/HonkaiMaterialRecipes.java'],
            text_evidence_locator=locator, new_visual_interpretation=interpretation,
            visual_reference=('references/' + reference) if reference else ''))
    for i, (name, label) in enumerate([('honkai_fuel_rod.png', '原有普通燃料母图'), ('dense_honkai_fuel_rod.png', '原有浓缩燃料母图'), ('honkai_fuel_rod_casing.png', '原有燃料棒壳体')]):
        im = Image.open(REFERENCES / name).convert('RGBA').resize((160, 160), Image.Resampling.NEAREST)
        sheet.paste(im, (i * 400 + 120, 5), im)
        d.text((i * 400 + 100, 178), label, font=font, fill='#d8be84')
    sheet.save(OUT / 'fuel-sheet.png')
    (OUT / 'design-fuel.json').write_text(json.dumps(dict(revision='R4', native_size=[64, 64],
        reference_policy='燃料族经负责人明确纠正，直接从原有两种燃料棒和壳体派生；高分辨率原图仅向下采样，绝不以16格放大。',
        items=rows), ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
