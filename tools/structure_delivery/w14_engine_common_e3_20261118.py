from io import BytesIO

from PIL import Image, ImageChops

from w14_engine_common_e2_20261117 import *
from w14_engine_common_e2_20261117 import materials as base_materials


OUT = ROOT / 'deliveries/0005_W14_原生维度地貌_E3_20261118'
LOG = ROOT / 'logs/0005-w14-native-dimensions-e3-20261118'
AD_ASTRA = Path('C:/Users/OWNER/.gradle/caches/modules-2/files-2.1/earth.terrarium.adastra/ad_astra-forge-1.20.1/1.15.20/537ac3e358a97efd7b03648a9bfd7b11f1ae7ff7/ad_astra-forge-1.20.1-1.15.20.jar')
MOON_STONE, MOON_SAND, MARS_STONE, MARS_SAND, VENUS_STONE, VENUS_SAND, GRASS_BLOCK, OAK_LEAVES, CRIMSON_NYLIUM, WARPED_NYLIUM, CRIMSON_STEM, WARPED_STEM, NETHER_WART_BLOCK, WARPED_WART_BLOCK, SHROOMLIGHT, SOUL_SAND, SOUL_SOIL, BLACKSTONE, GRAVEL, BONE_BLOCK, BEDROCK, IRON_BARS, END_PORTAL, CRYSTAL_WHITE, CRYSTAL_PINK = range(43, 68)
WALL_TORCH_EAST, WALL_TORCH_WEST, WALL_TORCH_SOUTH, WALL_TORCH_NORTH, NETHER_LAVA = range(68, 73)


def image_bytes(image):
    stream = BytesIO()
    image.save(stream, 'PNG')
    return stream.getvalue()


def first_frame(png):
    image = Image.open(BytesIO(png)).convert('RGBA')
    return image.crop((0, 0, image.width, image.width))


def colorize(image, color):
    colored = ImageChops.multiply(image.convert('RGB'), Image.new('RGB', image.size, color))
    colored.putalpha(image.getchannel('A'))
    return colored


def native_material(archive, archive_path, namespace, state, label, textures, transparent=False, emissive=False):
    entries = {face: f'assets/{namespace}/textures/{name}.png' for face, name in textures.items()}
    raw = {entry: archive.read(entry) for entry in set(entries.values())}
    images = {entry: image_bytes(first_frame(png)) for entry, png in raw.items()}
    source = dict(kind='ad_astra' if namespace == 'ad_astra' else 'mc', archive=str(archive_path), entries=entries,
                  original_png_sha256={entry: hashlib.sha256(png).hexdigest() for entry, png in raw.items()}, preview_frame=0)
    material = png_material(state, label, images[entries['east']], source, transparent, emissive)
    material['faces'] = {face: 'data:image/png;base64,' + base64.b64encode(images[entry]).decode() for face, entry in entries.items()}
    return material


def uniform(name):
    return {face: 'block/' + name for face in FACES}


def column(side, end):
    return {**uniform(side), 'up': 'block/' + end, 'down': 'block/' + end}


def materials():
    result = base_materials()
    mc = Path(result[17]['source']['archive'])
    with ZipFile(AD_ASTRA) as archive:
        for block, label in [('moon_stone', 'Ad Astra月球石'), ('moon_sand', 'Ad Astra月球砂'),
                             ('mars_stone', 'Ad Astra火星石'), ('mars_sand', 'Ad Astra火星砂'),
                             ('venus_stone', 'Ad Astra金星石'), ('venus_sand', 'Ad Astra金星砂')]:
            result.append(native_material(archive, AD_ASTRA, 'ad_astra', 'ad_astra:' + block, label, uniform(block)))
    with ZipFile(mc) as archive:
        grass_color = first_frame(archive.read('assets/minecraft/textures/colormap/grass.png')).getpixel((50, 173))[:3]
        leaf_color = first_frame(archive.read('assets/minecraft/textures/colormap/foliage.png')).getpixel((50, 173))[:3]
        grass = native_material(archive, mc, 'minecraft', 'minecraft:grass_block[snowy=false]', '原版草原草方块',
                                {**uniform('grass_block_side'), 'up': 'block/grass_block_top', 'down': 'block/dirt'})
        top = colorize(first_frame(archive.read('assets/minecraft/textures/block/grass_block_top.png')), grass_color)
        side = first_frame(archive.read('assets/minecraft/textures/block/grass_block_side.png'))
        overlay = colorize(first_frame(archive.read('assets/minecraft/textures/block/grass_block_side_overlay.png')), grass_color)
        side = Image.alpha_composite(side, overlay)
        for face in ['east', 'west', 'south', 'north']:
            grass['faces'][face] = 'data:image/png;base64,' + base64.b64encode(image_bytes(side)).decode()
        grass['faces']['up'] = 'data:image/png;base64,' + base64.b64encode(image_bytes(top)).decode()
        grass['source']['png_sha256'] = hashlib.sha256(image_bytes(side)).hexdigest()
        grass['source']['tint'] = dict(biome='minecraft:plains', temperature=.8, downfall=.4, rgb=grass_color,
                                     colormap='assets/minecraft/textures/colormap/grass.png', overlay='assets/minecraft/textures/block/grass_block_side_overlay.png')
        result.append(grass)
        leaves = native_material(archive, mc, 'minecraft', 'minecraft:oak_leaves[distance=1,persistent=true,waterlogged=false]', '原版草原橡树叶', uniform('oak_leaves'))
        png = image_bytes(colorize(first_frame(archive.read('assets/minecraft/textures/block/oak_leaves.png')), leaf_color))
        leaves['faces'] = {face: 'data:image/png;base64,' + base64.b64encode(png).decode() for face in FACES}
        leaves['source']['png_sha256'] = hashlib.sha256(png).hexdigest()
        leaves['source']['tint'] = dict(biome='minecraft:plains', temperature=.8, downfall=.4, rgb=leaf_color,
                                      colormap='assets/minecraft/textures/colormap/foliage.png')
        result.append(leaves)
        for block, label in [('crimson_nylium', '绯红菌岩'), ('warped_nylium', '诡异菌岩')]:
            result.append(native_material(archive, mc, 'minecraft', 'minecraft:' + block, label,
                {**uniform(block + '_side'), 'up': 'block/' + block, 'down': 'block/netherrack'}))
        for block, label in [('crimson_stem', '绯红菌柄'), ('warped_stem', '诡异菌柄')]:
            result.append(native_material(archive, mc, 'minecraft', 'minecraft:' + block + '[axis=y]', label, column(block, block + '_top')))
        for block, label in [('nether_wart_block', '下界疣块'), ('warped_wart_block', '诡异疣块'),
                             ('shroomlight', '菌光体'), ('soul_sand', '灵魂沙'), ('soul_soil', '灵魂土'),
                             ('blackstone', '黑石'), ('gravel', '砂砾')]:
            result.append(native_material(archive, mc, 'minecraft', 'minecraft:' + block, label, uniform(block), emissive=block == 'shroomlight'))
        result.append(native_material(archive, mc, 'minecraft', 'minecraft:bone_block[axis=y]', '灵魂沙峡谷骨块', column('bone_block_side', 'bone_block_top')))
        result.append(native_material(archive, mc, 'minecraft', 'minecraft:bedrock', '龙池与柱顶基岩', uniform('bedrock')))
        result.append(native_material(archive, mc, 'minecraft', 'minecraft:iron_bars[east=true,north=true,south=true,waterlogged=false,west=true]', '末影水晶铁栏杆笼', uniform('iron_bars'), transparent=True))
        result.append(native_material(archive, mc, 'minecraft', 'minecraft:obsidian', '龙池黑曜石池面', uniform('obsidian')))
        for block, label in [('white_stained_glass', '方块水晶浅色透明外框'), ('magenta_stained_glass', '方块水晶品红核心')]:
            result.append(native_material(archive, mc, 'minecraft', 'minecraft:' + block, label, uniform(block), transparent=True))
        for direction, label in [('east', '东向龙池火把'), ('west', '西向龙池火把'), ('south', '南向龙池火把'), ('north', '北向龙池火把')]:
            result.append(native_material(archive, mc, 'minecraft', f'minecraft:wall_torch[facing={direction}]', label, uniform('torch'), transparent=True, emissive=True))
        result.append(native_material(archive, mc, 'minecraft', 'minecraft:magma_block', '下界地貌岩浆块', uniform('magma'), emissive=True))
        result[LOG_BLOCK - 1] = native_material(archive, mc, 'minecraft', 'minecraft:oak_log[axis=y]', '原版橡木原木', column('oak_log', 'oak_log_top'))
        result[BASALT - 1] = native_material(archive, mc, 'minecraft', 'minecraft:basalt[axis=y]', '原版玄武岩', column('basalt_side', 'basalt_top'))
    gt = Path(result[0]['source']['archive'])
    with ZipFile(gt) as archive:
        entry = 'assets/gtceu/textures/block/lamps/magenta_borderless.png'
        result[CRYSTAL_PINK - 1] = png_material('gtceu:magenta_borderless_lamp[bloom=true,inverted=true,lit=true,powered=false]',
            '方块水晶品红发光核心', archive.read(entry), dict(kind='gt', archive=str(gt), entry=entry), emissive=True)
    return result
