from pathlib import Path

from author_w05_shapes_20261115 import Part


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_太虚山方块复刻_T1_20261116'
REF = ROOT / 'deliveries/0005_W09_太虚山多角度参考_T1_20261116'
ROCK, ROCK_DARK, ROCK_PALE, MOSS, GRASS, FRAME, WOOD, ROOF, TILE, WHITE, PAVING, GOLD, BRONZE, BROWN, INK, SNOW, LOG, LEAF, WATER = range(1, 20)
PATINA = 20
COURT_Y = 160
STATES = ['minecraft:stone', 'minecraft:andesite', 'minecraft:polished_andesite',
    'minecraft:moss_block', 'minecraft:green_terracotta', 'hk3gtl:casing_colored_black',
    'minecraft:spruce_planks', 'hk3gtl:casing_colored_gray', 'minecraft:gray_terracotta',
    'gtceu:clean_machine_casing', 'minecraft:smooth_sandstone', 'minecraft:yellow_terracotta',
    'gtceu:bronze_gearbox', 'minecraft:brown_terracotta', 'minecraft:black_concrete',
    'minecraft:white_concrete', 'minecraft:spruce_log[axis=y]',
    'minecraft:oak_leaves[persistent=true,distance=1,waterlogged=false]',
    'minecraft:light_blue_stained_glass', 'hk3gtl:casing_colored_green']
LABELS = ['灰青岩层', '颗粒陡壁', '浅色切面', '草皮与苔台', '深绿草台',
    '本模组墨色构架', '深木板', '本模组青灰屋面', '灰褐瓦脊', '格雷白瓷墙板',
    '浅暖石坪', '青铜檐边', '格雷香炉机关', '褐铜炉腹', '太极墨色',
    '太极白色', '松木树干', '青绿树冠', '瀑布水色', '本模组铜绿金属']


def model(part, features, refs, views):
    part.metadata.update(features=features, references=refs, views=views)
    return part.finish()
