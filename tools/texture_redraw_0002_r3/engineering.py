# -*- coding: utf-8 -*-
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .common import Pixel, STEEL, WHITE, GOLD, COPPER, VIOLET, BLUE, BLACK


def anchor():
    s = Pixel()
    s.plate([(9, 39), (31, 28), (55, 39), (33, 53)], BLACK)
    s.plate([(9, 39), (33, 51), (33, 57), (9, 45)], STEEL, 1)
    s.plate([(33, 51), (55, 39), (55, 45), (33, 57)], STEEL, 1)
    for points in [[(12, 36), (17, 34), (24, 43), (22, 48), (16, 46)],
                   [(42, 33), (49, 36), (47, 46), (41, 49), (38, 43)],
                   [(25, 18), (31, 15), (37, 19), (36, 32), (31, 36), (25, 32)]]:
        s.plate(points, STEEL, 2)
    s.cylinder((23, 28, 40, 45), BLACK)
    s.d.ellipse((25, 28, 38, 35), fill=GOLD[2], outline=GOLD[0])
    s.d.ellipse((28, 29, 35, 33), fill=VIOLET[1], outline=STEEL[4])
    for x, y in [(14, 40), (45, 40), (29, 20)]:
        s.bolt(x, y)
    s.d.line((21, 48, 28, 44, 28, 38), fill=GOLD[3])
    s.d.line((39, 47, 35, 44, 35, 38), fill=WHITE[3])
    for x in [26, 29, 32, 35]:
        s.d.line((x, 51, x, 53), fill=GOLD[3])
    return s.im


def offcut():
    s = Pixel()
    s.plate([(9, 38), (24, 26), (43, 38), (35, 40), (41, 44), (29, 54)], BLACK, 2)
    s.plate([(9, 38), (29, 50), (29, 54), (9, 42)], STEEL, 1)
    s.d.line((10, 40, 28, 51), fill=BLUE[2])
    s.d.line((13, 39, 29, 48), fill=COPPER[3])
    s.plate([(18, 20), (27, 12), (54, 28), (44, 36)], WHITE, 2)
    s.plate([(18, 20), (44, 36), (44, 41), (18, 25)], BLACK, 2)
    s.plate([(44, 36), (54, 28), (54, 32), (44, 41)], STEEL, 1)
    s.d.line((22, 20, 44, 33, 50, 29), fill=VIOLET[2], width=2)
    s.d.line((22, 23, 44, 36), fill=COPPER[2])
    for x, y in [(18, 25), (21, 27), (24, 29), (44, 40), (47, 37)]:
        s.d.line((x, y, x - 3, y + 4), fill=STEEL[3])
    s.plate([(45, 45), (53, 41), (57, 47), (49, 52)], VIOLET, 1)
    s.d.line((47, 46, 52, 44), fill=VIOLET[3])
    return s.im


def polarized():
    s = Pixel()
    for j in range(3):
        y = 29 - 5 * j
        s.plate([(10, y), (25, y - 10), (55, y + 6), (40, y + 17)], BLACK, 2)
        s.plate([(10, y), (40, y + 17), (40, y + 20), (10, y + 3)], STEEL, 2)
        s.plate([(40, y + 17), (55, y + 6), (55, y + 9), (40, y + 20)], BLUE, 1)
        for k in range(4):
            x = 15 + k * 6
            s.d.line((x, y - 2, x + 23, y + 11), fill=BLUE[2 + k % 2])
            s.d.point((x + 24, y + 11), fill=STEEL[4])
    s.plate([(19, 14), (23, 12), (48, 27), (44, 30)], WHITE, 3)
    s.plate([(19, 14), (23, 17), (23, 36), (19, 34)], WHITE, 2)
    s.plate([(44, 30), (48, 27), (48, 46), (44, 49)], WHITE, 1)
    s.d.line((26, 17, 40, 25), fill=GOLD[3])
    s.d.line((26, 19, 39, 27), fill=GOLD[1])
    return s.im


def cryogenic():
    s = Pixel()
    pal = ['#1b3646', '#3c657a', '#7aa2af', '#b1d1d6', '#edf4ed']
    s.plate([(12, 25), (31, 13), (53, 25), (34, 38)], pal, 3)
    s.plate([(12, 25), (34, 38), (34, 54), (13, 42)], pal, 2)
    s.plate([(34, 38), (53, 25), (52, 42), (34, 54)], pal, 1)
    for y in [30, 35, 40]:
        s.d.line((16, y, 31, y + 9), fill=pal[1])
        s.d.line((17, y, 30, y + 7), fill=pal[3])
    for x, y in [(17, 24), (24, 20), (34, 23), (42, 26), (36, 31), (18, 33), (25, 41), (37, 43), (47, 34)]:
        s.d.rectangle((x, y, x + 2, y + 1), fill=pal[4])
        s.d.point((x + 1, y - 1), fill=pal[3])
    s.d.line((22, 25, 31, 20, 44, 27), fill=pal[2])
    s.d.line((37, 39, 49, 31), fill=pal[3])
    s.plate([(15, 45), (23, 49), (23, 52), (15, 48)], STEEL, 1)
    return s.im


def casting():
    s = Pixel()
    pal = ['#302932', '#654047', '#9b635a', '#c89472', '#eed4a2']
    s.plate([(10, 29), (30, 17), (53, 30), (34, 42)], pal, 3)
    s.plate([(10, 29), (34, 42), (34, 53), (10, 40)], pal, 2)
    s.plate([(34, 42), (53, 30), (53, 41), (34, 53)], pal, 1)
    s.plate([(22, 15), (31, 10), (38, 14), (29, 20)], pal, 2)
    s.plate([(22, 15), (29, 20), (29, 29), (22, 25)], pal, 2)
    s.plate([(29, 20), (38, 14), (38, 23), (29, 29)], pal, 1)
    s.d.line((12, 35, 34, 47, 51, 36), fill=pal[0])
    s.d.line((13, 36, 33, 47), fill=pal[3])
    for x, y in [(17, 29), (22, 34), (39, 31), (43, 28), (18, 38), (39, 42)]:
        s.d.line((x, y, x + 3, y + 1), fill=pal[1])
        s.d.point((x + 1, y - 1), fill=pal[4])
    s.d.line((27, 13, 31, 12, 34, 14), fill=pal[4])
    return s.im


def singularity():
    s = Pixel()
    s.plate([(13, 36), (29, 27), (52, 39), (35, 51)], BLACK, 2)
    s.plate([(13, 36), (35, 49), (35, 55), (13, 43)], STEEL, 1)
    s.plate([(35, 49), (52, 39), (52, 45), (35, 55)], STEEL, 1)
    s.d.ellipse((17, 12, 47, 43), fill=STEEL[0], outline=GOLD[1], width=2)
    s.d.arc((19, 14, 45, 41), 185, 350, fill=WHITE[3], width=2)
    s.d.ellipse((23, 18, 41, 37), fill=VIOLET[1], outline=VIOLET[3])
    s.d.ellipse((27, 21, 37, 34), fill=BLACK[0], outline=VIOLET[4])
    s.d.line((27, 33, 30, 35, 36, 33), fill=BLUE[2])
    for a in [[(13, 19), (19, 16), (25, 23), (22, 28), (17, 26)],
              [(43, 16), (50, 22), (47, 29), (41, 27), (39, 22)],
              [(24, 39), (29, 35), (37, 37), (39, 44), (30, 48)]]:
        s.plate(a, WHITE, 2)
    for x, y in [(16, 21), (43, 22), (29, 41)]:
        s.bolt(x, y, GOLD)
    s.d.line((20, 44, 25, 47), fill=VIOLET[3], width=2)
    for x in [35, 39, 43]:
        s.d.line((x, 48 - (x - 35) // 2, x, 51 - (x - 35) // 2), fill=GOLD[3])
    return s.im


def impurity():
    s = Pixel()
    dust = ['#24262c', '#4b474b', '#72666b', '#9b8c88', '#c4b5a0']
    for points in [[(8, 43), (12, 36), (20, 36), (27, 43), (23, 50), (11, 49)],
                   [(22, 36), (27, 27), (37, 24), (46, 31), (45, 43), (32, 49)],
                   [(41, 42), (47, 36), (54, 39), (57, 47), (49, 51)]]:
        s.plate(points, dust, 2, 7)
    for x, y, c in [(15, 40, 3), (17, 45, 1), (27, 34, 3), (33, 29, 4), (38, 34, 1),
                    (31, 42, 1), (42, 38, 3), (47, 43, 3), (51, 46, 1), (24, 48, 4)]:
        s.d.rectangle((x, y, x + 2, y + 1), fill=dust[c])
    s.d.line((31, 35, 35, 37, 37, 34), fill=COPPER[2])
    s.d.line((16, 38, 19, 41), fill=STEEL[3])
    for x, y in [(9, 53), (29, 53), (43, 53), (54, 34), (20, 31)]:
        s.d.rectangle((x, y, x + 1, y + 1), fill=dust[2])
    return s.im


def blueprint():
    s = Pixel()
    paper = ['#18334b', '#29536b', '#457e93', '#87c1cb', '#d1e9df']
    s.plate([(11, 15), (43, 8), (53, 18), (53, 49), (20, 57), (11, 47)], paper, 1)
    s.plate([(43, 8), (43, 19), (53, 18)], paper, 3)
    s.d.line((15, 18, 39, 13), fill=paper[3])
    s.d.line((15, 21, 28, 18), fill=paper[2])
    s.d.line((17, 34, 29, 31, 40, 29, 49, 30, 43, 34, 22, 40, 17, 38, 17, 34), fill=paper[4])
    s.d.line((19, 36, 31, 33, 45, 31), fill=paper[3])
    s.d.line((24, 32, 24, 27, 29, 25, 32, 30, 38, 28, 40, 29), fill=paper[4])
    s.d.line((15, 34, 15, 38, 17, 38), fill=paper[3])
    for x, y in [(24, 35), (31, 33), (38, 31)]:
        s.d.line((x, y, x + 2, y + 2), fill=paper[3])
    s.d.line((19, 44, 46, 38), fill=paper[3])
    for x, y in [(19, 44), (46, 38)]:
        s.d.line((x, y - 2, x, y + 2), fill=paper[4])
    for y in range(46, 51, 2):
        s.d.line((27, y, 40, y - 3), fill=paper[2])
    s.cylinder((8, 16, 16, 49), WHITE)
    s.d.line((10, 22, 10, 44), fill=BLUE[2])
    s.d.line((48, 22, 48, 44), fill=paper[2])
    return s.im


def keel():
    s = Pixel()
    s.plate([(9, 41), (19, 31), (53, 13), (57, 21), (25, 41), (14, 50)], BLACK, 2)
    s.plate([(9, 41), (14, 50), (14, 55), (9, 47)], STEEL, 1)
    s.plate([(14, 50), (57, 21), (57, 27), (14, 55)], STEEL, 2)
    s.plate([(14, 40), (20, 34), (53, 17), (53, 21), (22, 39), (17, 45)], WHITE, 2)
    s.d.line((19, 47, 53, 25), fill=BLACK[0], width=2)
    for x, y in [(20, 40), (30, 33), (40, 26), (49, 21)]:
        s.plate([(x - 4, y - 6), (x, y - 9), (x + 7, y - 3), (x + 4, y + 1)], STEEL, 3)
        s.plate([(x + 4, y + 1), (x + 7, y - 3), (x + 7, y + 6), (x + 4, y + 9)], STEEL, 1)
        s.bolt(x + 4, y + 3)
    s.plate([(9, 38), (15, 34), (22, 39), (16, 44)], STEEL, 2)
    s.d.polygon([(13, 38), (15, 37), (18, 39), (16, 41)], fill=BLACK[0])
    s.d.line((25, 46, 29, 43), fill=GOLD[2])
    s.d.line((33, 41, 37, 38), fill=GOLD[2])
    return s.im


def bridge():
    s = Pixel()
    s.plate([(10, 37), (29, 27), (55, 39), (36, 51)], BLACK, 2)
    s.plate([(10, 37), (36, 51), (36, 57), (10, 44)], STEEL, 1)
    s.plate([(36, 51), (55, 39), (55, 46), (36, 57)], STEEL, 1)
    s.plate([(14, 17), (31, 9), (49, 19), (49, 38), (32, 46), (14, 36)], WHITE, 2)
    s.plate([(17, 20), (30, 14), (30, 31), (17, 36)], BLACK, 1)
    s.plate([(33, 14), (46, 21), (46, 36), (33, 30)], BLACK, 1)
    s.d.polygon([(19, 22), (28, 18), (28, 27), (19, 31)], fill=BLUE[1])
    s.d.line((20, 27, 23, 23, 27, 23), fill=BLUE[3])
    s.d.polygon([(35, 19), (44, 23), (44, 32), (35, 28)], fill=BLUE[1])
    s.d.line((36, 24, 42, 27), fill=BLUE[4])
    s.plate([(18, 37), (29, 32), (45, 39), (34, 46)], STEEL, 2)
    for x, y in [(23, 37), (28, 35), (29, 40), (34, 38)]:
        s.d.line((x, y, x + 3, y + 1), fill=WHITE[3])
    s.d.rectangle((39, 40, 41, 41), fill=VIOLET[3])
    for x, y in [(15, 43), (20, 46), (25, 49), (42, 49), (47, 46)]:
        s.d.line((x, y, x, y + 3), fill=GOLD[3])
    s.bolt(50, 41)
    return s.im


DRAW = {
    'soulium_anchor_component': anchor,
    'composite_offcut': offcut,
    'polarized_electromagnetic_material': polarized,
    'cryogenic_condensed_material': cryogenic,
    'extreme_casting_material': casting,
    'civilization_singularity': singularity,
    'process_gas_impurity': impurity,
    'imitation_hyperion_blueprint': blueprint,
    'hyperion_keel_segment': keel,
    'hyperion_bridge_module': bridge,
}


def draw(ident):
    return DRAW[ident]()


DESIGNS = [
    ('soulium_anchor_component', '魂钢锚定组件', 'industrial_anchor_component', '钨钢板、铂箔和适配电路基板装配；用于采集、虚数锚定和世界维系工艺。', '厚钨钢基座、三处夹持爪、铂触点及内嵌控制件；采用机械夹紧结构表达锚定。'),
    ('composite_offcut', '高维复合材料边角料', 'industrial_recovery_composite_offcut', '多类复材制造和预制的余料；经滤芯和分析试剂回收数据基板与残渣。', '不规则切割条与叠层碎片，断口露出导体、绝缘层和纤维；不是完整复材换色。'),
    ('polarized_electromagnetic_material', '极化电磁材料', 'industrial_dispatch_conductor / industrial_electromagnetic_worktest', '导能复材、数据基板和铌钛细线在雷核心催化与冷却条件下制得。', '多层平行导电带和两道白色约束卡箍，层间冷蓝细线与金属端面表达可装配的工程材料。'),
    ('cryogenic_condensed_material', '深冷凝聚材料', 'industrial_cryogenic_worktest / wonder_cryogenic_condensation_matrix', '冰核心工艺及凝聚矩阵产出的工程材料。', '致密规则凝聚坯，表面生长细霜和低温层理；浅青顶面、深色侧面表达实体体积。'),
    ('extreme_casting_material', '极限铸造材料', 'industrial_flame_worktest / wonder_stellar_forging_matrix', '炎核心工艺及恒星锻造矩阵产出的工程材料。', '保留冒口、分型线与氧化表面的厚铸坯，暖色金属表面表现热加工历史。'),
    ('civilization_singularity', '文明工程奇点', 'wonder_gravitational_singularity_matrix', '奇观预制件、约束复材、极限铸造材、深冷凝聚材和世界稳定介质在W10工艺中产出。', '高密度中心置于三向装甲夹持的约束封装内，底部设安装座和触点；封装形制为美术推导。'),
    ('process_gas_impurity', '工艺气体杂质', 'industrial_gas_purification', '滤芯处理废魂钢工艺气时分离出的杂质。', '过滤沉积的灰褐凝聚团、金属细屑与散落颗粒；以沉积物体积表达副产。'),
    ('imitation_hyperion_blueprint', '仿制休伯利安蓝图', 'industrial_ship_blueprint_analysis', '舰船工程档案、数据基板、纸和分析试剂生成蓝图，也可用作复制催化。', '卷边工程图纸，绘有长舰体侧剖、尺寸线和技术栏；布局与线条是本轮设计。'),
    ('hyperion_keel_segment', '仿制休伯利安龙骨段', 'industrial_ship_components', '数据基板、电路封装、涂层纳米群经冷却装配产出；用于H01舰船工程。', '斜置承力长梁、四道加强肋、螺栓接头与贯通槽；表现可拼装结构段。'),
    ('hyperion_bridge_module', '仿制休伯利安舰桥模块', 'industrial_ship_components', '与龙骨段等共享舰船组件装配工艺，用于H01舰船工程。', '双面电子显示与控制台装在白色背板上，底部连接器清晰；模块是装配件而非整舰缩略。'),
]


def main():
    root = Path(__file__).resolve().parents[2]
    out = root / 'deliveries/0002贴图材质_工艺重构_R3_20261114'
    dst = out / 'textures/item'
    dst.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
    sheet = Image.new('RGB', (1000, 410), '#1d232d')
    d = ImageDraw.Draw(sheet)
    rows = []
    for i, (ident, name, recipe, fact, interpretation) in enumerate(DESIGNS):
        im = draw(ident)
        im.save(root / f'src/main/resources/assets/hk3gtl/textures/item/{ident}.png', optimize=True)
        im.save(dst / f'{ident}.png', optimize=True)
        x, y = i % 5 * 200, i // 5 * 205
        d.rectangle((x + 4, y + 4, x + 195, y + 200), fill='#303946', outline='#5c6a7c')
        sheet.paste(im.resize((160, 160), Image.Resampling.NEAREST), (x + 20, y + 5), im.resize((160, 160), Image.Resampling.NEAREST))
        d.text((x + 9, y + 175), name, font=font, fill='#e2e8e8')
        rows.append(dict(id=ident, name=name, function_process_facts=fact,
                         text_evidence_paths=['src/main/resources/data/hk3gtl/research/industrial_processes.json',
                                              'src/main/resources/data/hk3gtl/research/wonder_processes.json'],
                         text_evidence_locator=recipe, new_visual_interpretation=interpretation))
    sheet.save(out / 'engineering-sheet.png')
    (out / 'design-engineering.json').write_text(json.dumps(dict(revision='R3', native_size=[64, 64],
        reference_policy='只依当前名称、用途及工艺文本设计；不读取旧贴图、截图或旧稿。代码事实与美术解释分栏。',
        items=rows), ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
