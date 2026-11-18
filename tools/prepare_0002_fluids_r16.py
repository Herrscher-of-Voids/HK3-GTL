import hashlib
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFont

import package_0002_fluid_r15_light as r15


ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / 'deliveries/0002贴图材质_全电压产业_R16_20261116'
LOG = ROOT / 'logs/textures-industrial-handoff-0002-r16-20261116'
ASSETS = DELIVERY / 'candidate-assets'
CONTEXT = LOG / 'fluids-context.json'

DESIGNS = {
    'anchor_stress_transfer_grout': ('viscous', '#667c8b', '#c0cbd3', 'fiber_metal', '灰蓝稠浆以短切碳纤维和银灰金属细粒表现承压填料与锚索载荷传递。'),
    'constraint_ceramic_suspension': ('viscous', '#b3b0c0', '#e2e5e6', 'ceramic', '浅灰紫陶瓷浆中分布乳白颗粒与稀疏石墨薄片，保留适合流延的均匀稠度。'),
    'cryogenic_grid_infiltrant': ('clean', '#8ebac8', '#dfedf0', 'fine_ceramic', '淡青载液中分散细小乳白陶瓷相，以稀疏短反光表现低粘度浸润液。'),
    'fatigue_isolation_encapsulant': ('viscous', '#2f606b', '#83a5ad', 'damping_plate', '暗青粘弹液含深色片状阻尼填料，宽而短的流带表现封装材料的粘度。'),
    'gradient_fiber_sizing_bath': ('clean', '#66678c', '#b7b0d3', 'gradient_fiber', '青紫上浆浴含逐段变化的短纤维疏密，细线沿流向排列，体现梯度纤维处理。'),
    'honkai_interface_priming_liquid': ('clean', '#8476a3', '#c9c2df', 'primer', '淡紫底涂液含二氧化硅与氧化铪细颗粒，表面留有细长薄膜反光。'),
    'honkai_selective_extractant': ('impure', '#4f766e', '#9abfaf', 'extractant', '灰绿有机萃取相中布置炭黑载体、细碎铂色接点及少量紫色含能分散相。'),
    'impedance_matching_coupling_gel': ('viscous', '#625c9d', '#b7b3dc', 'graded_metal', '紫蓝凝胶内布置分级银金属薄片，大小差异对应阻抗梯度耦合填料。'),
    'low_volatility_lamination_resin': ('viscous', '#937b55', '#d2bd92', 'mica', '淡琥珀树脂内悬浮云母薄片、乳白陶瓷细粒与细暗碳相，保持宽缓流带。'),
    'multiaxial_cocure_infusion_resin': ('viscous', '#94725c', '#d1b499', 'multiaxial_fiber', '琥珀紫树脂中交错分布两方向增强短纤维，乳白散点对应陶瓷和硅质填料。'),
    'nano_barrier_ceramic_dispersion': ('viscous', '#7e8998', '#c8d0d6', 'barrier', '蓝灰分散液以细陶瓷颗粒、暗色片层和短桥接纤维呈现纳米阻隔组分。'),
    'nano_surface_passivation_liquid': ('clean', '#7a9b92', '#cbddd0', 'passivation', '浅绿灰洁净载液含稀疏铂色微粒和极薄石墨短片，反光细而克制。'),
    'nanocarbon_predispersion_slurry': ('dirty', '#343c49', '#7d8a99', 'carbon', '黑灰浆料以不同长度的碳纳米管短线、石墨烯薄片与细颗粒表现预分散状态。'),
    'paired_seed_growth_bath': ('world', '#514a86', '#aba1da', 'paired_seed', '蓝紫母液含成对平行短晶核，两个晶向交错分布，保持独立可辨的悬浮晶种。'),
    'phase_transfer_ceramic_sol': ('viscous', '#c7c3cd', '#f0eef2', 'violet_plate', '乳白溶胶含紫色片晶和灰紫细粒，连续浅色流带表现硅质溶胶网络。'),
    'quadrisystem_interface_couplant': ('clean', '#a89bbc', '#e1d7ed', 'quadriphase', '浅紫载液中均匀分散青、金、紫、银四种短片细相，各相保持独立。'),
    'reconstruction_composition_flux': ('energy', '#4c345e', '#aa84ba', 'flux_metal', '深紫流体含银灰和钛金色金属微粒，短折流脉表现受控重排介质。'),
    'resonance_growth_solution': ('world', '#586d96', '#aebfdd', 'lattice_seed', '蓝灰生长液中分散银白短晶核与少量金色取向颗粒，晶体以短直段表现。'),
    'reversible_service_bonding_medium': ('viscous', '#9c95b2', '#ddd9e7', 'microcapsule', '银紫粘接液中以微小方形胶囊和乳白陶瓷填料表现可解离维修层。'),
    'spent_constraint_ceramic_vehicle': ('dirty', '#8b8793', '#b8b3be', 'spent_ceramic', '沿用陶瓷悬浮液的灰紫色系，增加不均匀陶瓷团聚与石墨暗色沉积。'),
    'spent_honkai_interface_carrier': ('dirty', '#6f627b', '#a394b5', 'spent_primer', '沿用紫灰底涂载液，加入脱落薄膜碎片、金属暗粒和浑浊短流带。'),
    'spent_honkai_selective_extractant': ('dirty', '#55665b', '#909a7d', 'spent_extractant', '沿用灰绿萃取相，增加炭质沉积、吸附后紫灰团粒及少量金属细屑。'),
    'spent_lamination_resin': ('dirty', '#71654f', '#ab9a76', 'spent_mica', '沿用琥珀层合树脂色系，加入未固化树脂浑浊块、云母碎片与纤维碎屑。'),
    'spent_nano_passivation_liquid': ('dirty', '#667c71', '#a2b3a1', 'spent_passivation', '沿用绿灰钝化液，分散脱落保护薄片与灰黑颗粒，降低洁净液面的通透感。'),
    'spent_resonance_growth_solution': ('dirty', '#686b83', '#a4a2bc', 'spent_lattice', '沿用蓝灰生长液，保留断裂短晶核并增加失活颗粒和不规则晶屑沉积。'),
    'spent_stress_relief_conditioning_bath': ('dirty', '#626f7a', '#a4acb3', 'spent_conditioning', '沿用蓝灰应力调理液，加入脱落界面薄片与粉末沉积，流面更为浑浊。'),
    'stress_relief_conditioning_bath': ('clean', '#5b8195', '#a4c4d2', 'conditioning', '蓝灰调理液以宽缓平行短流带表现乙二醇载液，辅以微小PTFE浅色颗粒和石墨薄片。'),
    'zirconium_carbide_nano_sealing_liquid': ('viscous', '#626a75', '#b4bec8', 'sealing', '深钢灰封孔液含细小碳化锆角粒与短碳管网络，银灰反光表现成膜浸润相。'),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def polygon(image, points, color):
    draw = ImageDraw.Draw(image)
    for dy in (-64, 0, 64):
        for dx in (-64, 0, 64):
            draw.polygon([(x + dx, y + dy) for x, y in points], fill=(*color, 255))


def grains(image, rng, count, colors, size=2):
    for _ in range(count):
        x, y = rng.randrange(64), rng.randrange(64)
        w, h = rng.randrange(1, size + 1), rng.randrange(1, size + 1)
        color = rng.choice(colors)
        polygon(image, [(x, y), (x + w, y), (x + w, y + h - 1), (x, y + h - 1)], color)


def fibers(image, rng, count, colors, slopes=(1,), gradient=False):
    for _ in range(count):
        x, y = rng.randrange(64), rng.randrange(64)
        if gradient and rng.random() > .22 + .78 * (math.sin(math.tau * y / 64) + 1) / 2:
            continue
        length = rng.randrange(4, 13)
        slope = rng.choice(slopes)
        r15.wrapped_line(image, [(x, y), (x + length // 2, y + slope), (x + length, y + slope * 2)], (*rng.choice(colors), 255))


def flakes(image, rng, count, colors, sizes=(3, 7)):
    for _ in range(count):
        x, y = rng.randrange(64), rng.randrange(64)
        length = rng.randrange(*sizes)
        polygon(image, [(x, y), (x + length - 2, y), (x + length, y + 1), (x + 2, y + 2)], rng.choice(colors))


def draw_surface(fluid_id):
    family, body_hex, light_hex, motif, _ = DESIGNS[fluid_id]
    r15.DESIGNS[fluid_id] = family, body_hex, light_hex
    image = r15.paint(fluid_id)
    rng = random.Random(int(hashlib.sha256((fluid_id + ':r16').encode()).hexdigest()[:16], 16))
    body, light = ImageColor.getrgb(body_hex), ImageColor.getrgb(light_hex)
    dark = r15.mix(body, (21, 27, 37), .55)
    middle = r15.mix(body, light, .37)
    silver = r15.mix(light, (215, 224, 231), .55)
    violet = r15.mix(body, (145, 102, 183), .65)
    gold = r15.mix(body, (191, 168, 106), .65)
    if motif == 'fiber_metal':
        fibers(image, rng, 28, [dark, middle], (-1, 1))
        grains(image, rng, 34, [silver, middle])
    elif motif == 'ceramic':
        grains(image, rng, 62, [silver, light, middle], 2)
        flakes(image, rng, 12, [dark, middle], (2, 5))
    elif motif == 'fine_ceramic':
        grains(image, rng, 63, [silver, light, middle], 1)
        fibers(image, rng, 6, [light], (0,))
    elif motif == 'damping_plate':
        flakes(image, rng, 28, [dark, middle], (3, 8))
        fibers(image, rng, 8, [dark], (1,))
    elif motif == 'gradient_fiber':
        fibers(image, rng, 65, [dark, middle, light], (-1, 1), True)
        grains(image, rng, 16, [silver], 1)
    elif motif == 'primer':
        fibers(image, rng, 14, [light, middle], (0,))
        grains(image, rng, 42, [silver, middle], 1)
    elif motif == 'extractant':
        grains(image, rng, 35, [dark, violet, middle], 2)
        fibers(image, rng, 12, [dark], (-1, 1))
        grains(image, rng, 8, [silver], 1)
    elif motif == 'graded_metal':
        flakes(image, rng, 10, [silver, middle], (2, 4))
        flakes(image, rng, 8, [silver, gold], (4, 7))
        flakes(image, rng, 5, [middle, silver], (7, 10))
    elif motif == 'mica':
        flakes(image, rng, 25, [silver, gold, middle], (3, 7))
        grains(image, rng, 19, [light, dark], 1)
    elif motif == 'multiaxial_fiber':
        fibers(image, rng, 33, [dark, violet, middle], (-2, 2))
        grains(image, rng, 23, [silver, light], 1)
    elif motif == 'barrier':
        grains(image, rng, 38, [silver, middle], 2)
        flakes(image, rng, 15, [dark], (3, 6))
        fibers(image, rng, 9, [dark], (-1, 1))
    elif motif == 'passivation':
        grains(image, rng, 19, [silver, light], 1)
        flakes(image, rng, 10, [dark, middle], (2, 4))
    elif motif == 'carbon':
        fibers(image, rng, 34, [dark, middle], (-1, 1))
        flakes(image, rng, 22, [dark, middle], (2, 5))
        grains(image, rng, 28, [middle], 1)
    elif motif == 'paired_seed':
        for _ in range(18):
            x, y = rng.randrange(64), rng.randrange(64)
            length, slope = rng.randrange(3, 7), rng.choice((-1, 1))
            for offset in (0, 3):
                r15.wrapped_line(image, [(x, y + offset), (x + length, y + offset + slope * 2)], (*rng.choice([silver, middle]), 255))
        grains(image, rng, 11, [gold], 1)
    elif motif == 'violet_plate':
        flakes(image, rng, 27, [violet, middle], (3, 7))
        grains(image, rng, 22, [silver], 1)
    elif motif == 'quadriphase':
        for color in ('#75aaa9', '#bfa574', '#9971b5', '#d8dbe0'):
            flakes(image, rng, 8, [ImageColor.getrgb(color)], (2, 5))
    elif motif == 'flux_metal':
        grains(image, rng, 25, [silver, gold, middle], 2)
        fibers(image, rng, 10, [dark], (0, 1))
    elif motif == 'lattice_seed':
        fibers(image, rng, 24, [silver, middle], (-1, 1))
        grains(image, rng, 13, [gold, silver], 1)
    elif motif == 'microcapsule':
        for _ in range(26):
            x, y = rng.randrange(64), rng.randrange(64)
            polygon(image, [(x, y), (x + 2, y), (x + 2, y + 3), (x, y + 3)], middle)
            r15.wrapped_line(image, [(x, y), (x + 1, y)], (*silver, 255))
        grains(image, rng, 24, [silver, light], 1)
    elif motif == 'conditioning':
        fibers(image, rng, 14, [light, middle], (0,))
        flakes(image, rng, 9, [dark], (2, 4))
        grains(image, rng, 18, [silver], 1)
    elif motif == 'sealing':
        grains(image, rng, 48, [dark, middle, silver], 2)
        fibers(image, rng, 19, [dark, middle], (-1, 1))
    elif motif == 'spent_ceramic':
        grains(image, rng, 39, [dark, middle, silver], 3)
        flakes(image, rng, 15, [dark], (3, 6))
    elif motif == 'spent_primer':
        flakes(image, rng, 26, [dark, middle], (3, 8))
        grains(image, rng, 31, [dark, silver], 1)
    elif motif == 'spent_extractant':
        grains(image, rng, 45, [dark, violet, middle], 3)
        fibers(image, rng, 11, [dark], (-1, 1))
    elif motif == 'spent_mica':
        flakes(image, rng, 25, [dark, middle, gold], (3, 7))
        fibers(image, rng, 18, [dark], (-1, 1))
    elif motif == 'spent_passivation':
        flakes(image, rng, 20, [dark, middle], (2, 5))
        grains(image, rng, 33, [dark, silver], 2)
    elif motif == 'spent_lattice':
        fibers(image, rng, 18, [dark, middle, silver], (-1, 1))
        grains(image, rng, 36, [dark, middle], 2)
    elif motif == 'spent_conditioning':
        flakes(image, rng, 17, [dark, middle], (2, 6))
        grains(image, rng, 35, [dark, middle, silver], 2)
    return image


def save_texture(base, target, kind):
    relative = Path(target.removeprefix('src/main/resources/'))
    output = ASSETS / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    size = 128 if kind == 'flow' else 64
    strip = Image.new('RGBA', (size, size * 4))
    for index, offset in enumerate(((0, 0), (1, 1), (2, 0), (1, -1))):
        tile = ImageChops.offset(base, *offset)
        for y in range(0, size, 64):
            for x in range(0, size, 64):
                strip.paste(tile, (x, index * size + y))
    strip.save(output, optimize=True)
    animation = {'width': size, 'height': size, 'frametime': 6, 'interpolate': False, 'frames': [0, 1, 2, 3]}
    metadata = Path(str(output) + '.mcmeta')
    metadata.write_text(json.dumps({'animation': animation}, separators=(',', ':')) + '\n', encoding='utf-8')
    return {
        'kind': kind, 'image': output.relative_to(DELIVERY).as_posix(),
        'metadata': metadata.relative_to(DELIVERY).as_posix(), 'target': target,
        'metadataTarget': target + '.mcmeta', 'resource': 'hk3gtl:' + relative.as_posix().removeprefix('assets/hk3gtl/textures/').removesuffix('.png'),
        'size': list(strip.size), 'frameSize': [size, size], 'frames': 4,
        'sha256': digest(output), 'bytes': output.stat().st_size,
        'metadataSha256': digest(metadata), 'animation': animation,
        'rgbaFrameStorageBytes': strip.width * strip.height * 4,
    }


def preview(base, fluid_id):
    image = Image.new('RGB', (220, 220), '#5d6674')
    draw = ImageDraw.Draw(image)
    for y in range(0, 220, 10):
        for x in range(0, 220, 10):
            if (x // 10 + y // 10) % 2:
                draw.rectangle((x, y, x + 9, y + 9), fill='#707b8c')
    tile = base.resize((192, 192), Image.Resampling.NEAREST)
    image.paste(tile, (14, 14), tile)
    path = DELIVERY / 'fluid-previews' / (fluid_id + '.png')
    path.parent.mkdir(exist_ok=True)
    image.save(path, optimize=True)
    return path.relative_to(DELIVERY).as_posix()


def animation_preview(texture, fluid_id):
    frames = []
    with Image.open(DELIVERY / texture['image']) as strip:
        for index in range(4):
            frame = Image.new('RGB', (220, 220), '#5d6674')
            draw = ImageDraw.Draw(frame)
            for y in range(0, 220, 10):
                for x in range(0, 220, 10):
                    if (x // 10 + y // 10) % 2:
                        draw.rectangle((x, y, x + 9, y + 9), fill='#707b8c')
            tile = strip.crop((0, index * 64, 64, index * 64 + 64)).resize((192, 192), Image.Resampling.NEAREST)
            frame.paste(tile, (14, 14), tile)
            frames.append(frame)
    path = DELIVERY / 'fluid-previews' / (fluid_id + '.gif')
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=300, loop=0, disposal=2, optimize=True)
    return path.relative_to(DELIVERY).as_posix()


def overview(records):
    columns, cell_w, cell_h = 4, 300, 294
    image = Image.new('RGB', (1224, 98 + math.ceil(len(records) / columns) * cell_h), '#18202a')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    tiny = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
    draw.text((24, 15), 'R16 全电压工业链 · 28种流体候选', font=font, fill='#edf3ff')
    draw.text((24, 51), '原生64像素 · 静止64 / 流动128 · 4帧 · 6tick/帧 · 关闭插值', font=small, fill='#becfe3')
    for index, record in enumerate(records):
        x, y = 20 + index % columns * cell_w, 98 + index // columns * cell_h
        with Image.open(DELIVERY / record['staticPreview']) as tile:
            image.paste(tile, (x, y))
        draw.text((x, y + 226), record['name'], font=small, fill='#edf3ff')
        draw.text((x, y + 252), f"{index + 1:02} · {record['id'][:33]}", font=tiny, fill='#9dafc3')
    image.save(DELIVERY / 'fluid-overview.png', optimize=True)


def main():
    DELIVERY.mkdir(parents=True, exist_ok=True)
    records, resources = [], []
    for fluid in json.loads(CONTEXT.read_text(encoding='utf-8-sig')):
        fluid_id = fluid['id'].split(':')[1]
        base = draw_surface(fluid_id)
        textures = [save_texture(base, target, 'flow' if target.endswith('_flow.png') else 'still') for target in fluid['targets']]
        inputs = [entry for group in ('items', 'fluids') for entry in fluid['producerRecipes'][0].get(group, [])]
        facts = [fluid['role'], '配方来源：' + '、'.join(fluid['producers']), '首个生产配方投入：' + '、'.join(entry['name'] for entry in inputs)]
        static_preview = preview(base, fluid_id)
        records.append({
            'id': fluid_id, 'resourceId': fluid['id'], 'name': fluid['name'], 'kind': 'fluid',
            'status': '候选待审', 'facts': facts, 'purpose': fluid['role'], 'visualBasis': fluid['visualBasis'],
            'designZh': DESIGNS[fluid_id][4], 'palette': list(DESIGNS[fluid_id][1:3]),
            'surfaceMotif': DESIGNS[fluid_id][3], 'firstTier': fluid['firstTier'],
            'producerRecipes': [{'id': r['uid'], 'title': r['title']} for r in fluid['producerRecipes']],
            'consumers': fluid['consumers'],
            'preview': animation_preview(next(t for t in textures if t['kind'] == 'still'), fluid_id),
            'staticPreview': static_preview, 'textures': textures,
        })
        for texture in textures:
            resources.extend([
                {'id': fluid_id, 'kind': 'texture', 'file': texture['image'], 'target': texture['target'], 'sha256': texture['sha256']},
                {'id': fluid_id, 'kind': 'animation', 'file': texture['metadata'], 'target': texture['metadataTarget'], 'sha256': texture['metadataSha256']},
            ])
    manifest = {
        'revision': 'R16', 'conversation': '0002贴图材质', 'status': '候选待审',
        'sourceContext': CONTEXT.relative_to(ROOT).as_posix(),
        'method': '复用R15原生64像素周期噪声与流带函数，依据本轮配方和用途分别绘制分散相；静止64，流动按64图2×2平铺为128，4帧、6tick、关闭插值。',
        'imageGenerationUsed': False, 'sourceResourcesChanged': False,
        'fluidCount': len(records), 'pngCount': sum(len(r['textures']) for r in records),
        'metadataCount': sum(len(r['textures']) for r in records),
        'pngBytes': sum(t['bytes'] for r in records for t in r['textures']),
        'rgbaFrameStorageBytes': sum(t['rgbaFrameStorageBytes'] for r in records for t in r['textures']),
        'memoryMetric': 'RGBA全部动画帧的理论像素存储，不含mipmap、图集与驱动开销。',
        'records': records, 'resources': resources,
    }
    content = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    (DELIVERY / 'fluid-manifest.json').write_text(content, encoding='utf-8')
    (LOG / 'fluid-candidates.json').write_text(content, encoding='utf-8')
    overview(records)
    print(json.dumps({key: manifest[key] for key in ('fluidCount', 'pngCount', 'metadataCount', 'pngBytes', 'rgbaFrameStorageBytes')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
