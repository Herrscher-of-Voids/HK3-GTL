from w14_engine_common_20261117 import *


OUT = ROOT / 'deliveries/0005_W14_行星发动机维度基座_E2_20261117'
LOG = ROOT / 'logs/0005-w14-dimension-engine-e2-20261117'
E1 = ROOT / 'deliveries/0005_W14_行星发动机基座_E1_20261117'
NETHERRACK, LAVA, BASALT, RED_SAND, RED_TERRACOTTA, YELLOW_TERRACOTTA, ORANGE_TERRACOTTA, CALCITE = range(35, 43)


def materials():
    result = json.loads((E1 / 'materials.json').read_text('utf8'))
    mc, gt = Path(result[17]['source']['archive']), Path(result[0]['source']['archive'])
    with ZipFile(mc) as archive, ZipFile(gt) as gt_archive:
        entry = 'assets/minecraft/textures/block/netherrack.png'
        result.append(png_material('minecraft:netherrack', '地狱岩', archive.read(entry), dict(kind='mc', archive=str(mc), entry=entry)))
        entry = 'assets/gtceu/textures/block/lamps/orange_borderless.png'
        result.append(png_material('gtceu:orange_borderless_lamp[bloom=true,inverted=true,lit=true,powered=false]',
            '静态熔岩橙色辉光', gt_archive.read(entry), dict(kind='gt', archive=str(gt), entry=entry), emissive=True))
        for block, texture, label in [('basalt', 'basalt_side', '暗灰玄武岩'), ('red_sand', 'red_sand', '火星红砂'),
                ('red_terracotta', 'red_terracotta', '火星红岩'), ('yellow_terracotta', 'yellow_terracotta', '金星黄褐岩'),
                ('orange_terracotta', 'orange_terracotta', '金星橙褐岩'), ('calcite', 'calcite', '浅色坑缘岩')]:
            entry = f'assets/minecraft/textures/block/{texture}.png'
            state = 'minecraft:' + block + ('[axis=y]' if block == 'basalt' else '')
            result.append(png_material(state, label, archive.read(entry), dict(kind='mc', archive=str(mc), entry=entry)))
    for index, label in [(GLASS, '维度观察球玻璃'), (STONE, '灰色岩层'), (MOSS, '主世界草地'), (DIRT, '主世界土壤'),
            (LOG_BLOCK, '主世界树干'), (LEAVES, '主世界树冠'), (WATER, '主世界水面'), (END_STONE, '末地石'),
            (GREEN_LIGHT, '主世界供料指示'), (RED_LIGHT, '地狱与行星供料指示')]:
        result[index - 1]['label'] = label
    return result
