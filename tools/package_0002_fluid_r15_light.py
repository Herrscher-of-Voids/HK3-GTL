import hashlib
import json
import math
import random
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/textures-runtime-fixes-0002-r15-20261116'
DELIVERY = ROOT / 'deliveries/0002贴图材质_运行绑定与流体轻量_R15_20261116'
SOURCE = ROOT / 'logs/textures-fluid-redraw-0002-r11-20261115/manifest.json'
SCOPE = ROOT / 'logs/textures-fluid-redraw-0002-r11-20261115/fluid-scope.json'

DESIGNS = {
    'liquid_honkai_energy': ('energy', '#45235f', '#b78ce8'),
    'crude_honkai_energy': ('impure', '#63466d', '#b67fa2'),
    'clarified_honkai_mother_liquor': ('clean', '#665285', '#b7a5d1'),
    'honkai_mother_liquor': ('impure', '#635271', '#ac91b9'),
    'stabilized_liquid_honkai_energy': ('energy', '#473775', '#a9a0e8'),
    'honkai_separation_medium': ('clean', '#52748c', '#a8ccdb'),
    'honkai_stabilization_medium': ('clean', '#4d658c', '#bacce5'),
    'spent_honkai_stabilization_medium': ('dirty', '#686274', '#aaa0af'),
    'spent_analysis_reagent': ('dirty', '#7e6f57', '#b7ad8b'),
    'honkai_analysis_reagent': ('clean', '#568681', '#bad9c1'),
    'unrecoverable_process_effluent': ('dirty', '#4f4f48', '#8b896d'),
    'liquid_honkai_fuel': ('energy', '#286879', '#8ae0db'),
    'concentrated_liquid_honkai_fuel': ('energy', '#235b78', '#b9ebf2'),
    'fuel_refining_residual': ('dirty', '#64644c', '#a29f72'),
    'crystallization_residual_liquid': ('impure', '#7c6790', '#c4acd1'),
    'soulium_precursor_fluid': ('clean', '#657a89', '#c7d6dd'),
    'soulium_process_solvent': ('clean', '#728381', '#ccd7bf'),
    'spent_soulium_solvent': ('dirty', '#6d746a', '#abb3a2'),
    'nano_reaction_tail_liquid': ('dirty', '#60676f', '#a5b0b5'),
    'honkai_resistant_coating': ('viscous', '#b9bec1', '#e6e5dc'),
    'spent_resistant_coating': ('dirty', '#858582', '#c1b9a7'),
    'gaseous_honkai_energy': ('gas', '#7e689a', '#c3afdc'),
    'soulium_protective_gas': ('gas', '#81969e', '#d0e1df'),
    'spent_soulium_process_gas': ('gas', '#7a827c', '#bcc4ad'),
    'hot_soulium_exhaust': ('gas', '#9b7f64', '#dfc1a0'),
    'bubble_confinement_medium': ('world', '#3a5f89', '#a1c5e7'),
    'world_stabilization_medium': ('world', '#436f76', '#addbc7'),
    'spent_world_stabilization_medium': ('dirty', '#626e75', '#a4b4b4'),
    'honkai_coolant': ('clean', '#367c99', '#8fc9dc'),
    'hot_honkai_coolant': ('clean', '#7d538e', '#cc9ecb'),
    'lost_coolant_residue': ('dirty', '#657f7c', '#a8bbb0'),
    'fuel_waste_processing_fluid': ('dirty', '#686042', '#b09c65'),
    'circuit_growth_medium': ('clean', '#426e5b', '#a0c299'),
    'spent_circuit_growth_medium': ('dirty', '#5b6f4c', '#a1ad7f'),
    'honkai_circuit_etchant': ('clean', '#7a7540', '#c9c28a'),
    'spent_honkai_etchant': ('dirty', '#74633e', '#b39c65'),
    'stable_transport_medium': ('world', '#41568c', '#b0b6df'),
    'loaded_honkai_separation_medium': ('impure', '#70517f', '#bc98d4'),
    'spent_honkai_separation_medium': ('dirty', '#74666d', '#b19aa2'),
    'copper_electrolyte': ('clean', '#237898', '#94c7d4'),
    'contaminated_copper_electrolyte': ('dirty', '#4e7478', '#a2b4a5'),
    'secondary_heat_transfer_medium': ('clean', '#4c8198', '#a7c5d2'),
    'warm_secondary_heat_transfer_medium': ('clean', '#a78042', '#dfc486'),
    'hot_secondary_heat_transfer_medium': ('clean', '#b65839', '#e9ac6c'),
    'phase_modulation_medium': ('world', '#705f96', '#d0bce8'),
    'spent_phase_modulation_medium': ('dirty', '#6d687c', '#aaa2b6'),
    'soulium': ('metal', '#929ca8', '#e3e7ef'),
}

FAMILIES = {
    'clean': '洁净工艺液：低对比层叠液面与短横向反光，保持均匀的流体表面。',
    'dirty': '含杂及废液：浑浊块面、细碎悬浮颗粒及不规则暗色沉积。',
    'impure': '含能混合液：紫灰母液、少量矿物状悬浮颗粒及短促能量亮纹。',
    'energy': '崩坏能及燃料：深色液面与稀疏方折流脉，无环状中心或符号。',
    'viscous': '黏稠涂层液：银白宽色阶、细小皱褶与克制的高光。',
    'gas': '工业气体：半透明雾片、疏密色阶及细颗粒过渡，不绘制液面波纹。',
    'world': '世界与场相介质：蓝紫或青色平面干涉、错层短光带，不绘制球眼或同心环。',
    'metal': '熔融魂钢：银灰液态金属、宽流带和窄亮边，不画金属方块或面板。',
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def backup(relative):
    saved = LOG / 'before' / relative
    if not saved.exists():
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, saved)
    return saved


def mix(a, b, fraction):
    return tuple(round(x + (y - x) * fraction) for x, y in zip(a, b))


def noise_field(rng, count):
    lattice = [[rng.random() for _ in range(count)] for _ in range(count)]
    field = []
    for y in range(64):
        gy = y * count / 64
        iy, fy = int(gy), gy % 1
        fy = fy * fy * (3 - 2 * fy)
        row = []
        for x in range(64):
            gx = x * count / 64
            ix, fx = int(gx), gx % 1
            fx = fx * fx * (3 - 2 * fx)
            top = lattice[iy][ix] * (1 - fx) + lattice[iy][(ix + 1) % count] * fx
            bottom = lattice[(iy + 1) % count][ix] * (1 - fx) + lattice[(iy + 1) % count][(ix + 1) % count] * fx
            row.append(top * (1 - fy) + bottom * fy)
        field.append(row)
    return field


def wrapped_line(image, points, color, width=1):
    draw = ImageDraw.Draw(image)
    for dy in (-64, 0, 64):
        for dx in (-64, 0, 64):
            draw.line([(x + dx, y + dy) for x, y in points], fill=color, width=width)


def paint(fluid_id):
    family, body_hex, light_hex = DESIGNS[fluid_id]
    rng = random.Random(int(hashlib.sha256(fluid_id.encode()).hexdigest()[:16], 16))
    body, light = ImageColor.getrgb(body_hex), ImageColor.getrgb(light_hex)
    broad, fine = noise_field(rng, 8), noise_field(rng, 16)
    palette = [mix(body, (15, 20, 31), .2), body, mix(body, light, .18), mix(body, light, .36), mix(body, light, .57)]
    frame = Image.new('RGBA', (64, 64))
    pixels = frame.load()
    for y in range(64):
        for x in range(64):
            band = (math.sin(math.tau * (y * 2 + x + 5 * broad[y][x]) / 64) + 1) / 2
            value = .64 * broad[y][x] + .2 * fine[y][x] + .16 * band
            if family in ('metal', 'viscous'):
                value = .46 * broad[y][x] + .12 * fine[y][x] + .42 * band
            if family == 'world':
                value = .75 * broad[y][x] + .25 * band
            level = min(4, max(0, int(value * 6) - 1))
            alpha = 255
            if family == 'gas':
                level = min(4, int((.75 * broad[y][x] + .25 * fine[y][x]) * 6))
                alpha = (55, 73, 97, 124, 150)[level]
            pixels[x, y] = (*palette[level], alpha)
    if family == 'gas':
        return frame
    count = {'energy': 14, 'impure': 10, 'world': 15, 'metal': 24, 'viscous': 18}.get(family, 24)
    for _ in range(count):
        x, y = rng.randrange(64), rng.randrange(64)
        length = rng.randrange(3, 11)
        points = [(x, y), (x + length // 2, y), (x + length // 2 + 1, y - 1), (x + length, y - 1)]
        if family in ('energy', 'impure'):
            points += [(x + length + 2, y - 3), (x + length + 4, y - 3)]
        if family == 'world':
            points = [(x, y), (x + length, y), (x + length + 3, y + 2)]
        color = mix(body, light, rng.choice((.38, .5, .68)))
        wrapped_line(frame, points, (*color, 255))
    if family in ('dirty', 'impure'):
        for _ in range(42 if family == 'dirty' else 21):
            x, y = rng.randrange(64), rng.randrange(64)
            length = rng.randrange(1, 4)
            color = mix(body, (32, 35, 29), rng.choice((.24, .4, .55)))
            wrapped_line(frame, [(x, y), (x + length, y), (x + length, y + 1)], (*color, 255))
        for _ in range(16):
            pixels[rng.randrange(64), rng.randrange(64)] = (*mix(body, light, .45), 255)
    return frame


def write_texture(base, texture):
    size = 128 if texture['kind'] == 'flow' else 64
    strip = Image.new('RGBA', (size, size * 4))
    for index, offset in enumerate(((0, 0), (1, 1), (2, 0), (1, -1))):
        tile = ImageChops.offset(base, *offset)
        for y in range(0, size, 64):
            for x in range(0, size, 64):
                strip.paste(tile, (x, index * size + y))
    output = ROOT / texture['path']
    strip.save(output, optimize=True)
    animation = {'width': size, 'height': size, 'frametime': 6, 'interpolate': False, 'frames': [0, 1, 2, 3]}
    (ROOT / texture['metadataPath']).write_text(json.dumps({'animation': animation}, separators=(',', ':')) + '\n', encoding='utf-8')
    return {
        'size': list(strip.size), 'frameSize': [size, size], 'pixels': strip.width * strip.height,
        'bytes': output.stat().st_size, 'sha256': sha256(output), 'animation': animation,
    }


def overview(manifest):
    width, cell_w, cell_h = 1180, 232, 258
    sheet = Image.new('RGB', (width, 98 + math.ceil(len(manifest['records']) / 5) * cell_h), '#18202a')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15)
    draw.text((24, 16), 'R15 全流体新绘 · 原生64像素 · 47种独立配色与工艺表面', font=font, fill='#edf3ff')
    draw.text((24, 51), '静止64 / 流动128（2×2平铺） · 4帧 · 6tick/帧 · 无插值 · 无生图API', font=small, fill='#becfe3')
    for index, fluid in enumerate(manifest['records']):
        x, y = 20 + index % 5 * cell_w, 94 + index // 5 * cell_h
        tile = paint(fluid['id']).resize((192, 192), Image.Resampling.NEAREST)
        sheet.paste(tile, (x, y), tile)
        draw.text((x, y + 197), fluid['name'], font=small, fill='#edf3ff')
        draw.text((x, y + 219), FAMILIES[DESIGNS[fluid['id']][0]].split('：')[0], font=small, fill='#9dafc3')
    sheet.save(DELIVERY / 'fluid-overview.png')
    sheet.save(DELIVERY / 'fluid-comparison.png')


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    DELIVERY.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
    scope = {item['id']: item for item in json.loads(SCOPE.read_text(encoding='utf-8-sig'))['fluids']}
    records = []
    for fluid in manifest['records']:
        base = paint(fluid['id'])
        family = DESIGNS[fluid['id']][0]
        for texture in fluid['textures']:
            original = backup(texture['path'])
            metadata = backup(texture['metadataPath'])
            animation = json.loads(metadata.read_text(encoding='utf-8-sig'))['animation']
            with Image.open(original) as source:
                old_size = list(source.size)
            records.append({
                'id': fluid['id'], 'name': fluid['name'], 'kind': texture['kind'],
                'path': texture['path'], 'resource': texture['resource'], 'metadataPath': texture['metadataPath'],
                'designFamily': family, 'design': FAMILIES[family], 'purpose': scope[fluid['id']]['purpose'],
                'palette': list(DESIGNS[fluid['id']][1:]),
                'before': {
                    'size': old_size, 'pixels': old_size[0] * old_size[1],
                    'bytes': original.stat().st_size, 'sha256': sha256(original), 'animation': animation,
                },
                'after': write_texture(base, texture),
            })
    totals = {
        stage: {
            'pixels': sum(record[stage]['pixels'] for record in records),
            'pngBytes': sum(record[stage]['bytes'] for record in records),
            'rgbaFrameStorageBytes': sum(record[stage]['pixels'] * 4 for record in records),
        } for stage in ('before', 'after')
    }
    totals['remainingPixelRatio'] = totals['after']['pixels'] / totals['before']['pixels']
    totals['remainingPngRatio'] = totals['after']['pngBytes'] / totals['before']['pngBytes']
    receipt = {
        'revision': 'R15', 'conversation': '0002贴图材质',
        'sourceManifest': SOURCE.relative_to(ROOT).as_posix(),
        'scope': SCOPE.relative_to(ROOT).as_posix(),
        'fluidCount': len(manifest['records']), 'textureCount': len(records),
        'method': '依据物品名称与工艺重新程序绘制原生64像素流体；流动图按同一64图2×2平铺为128；4帧、6tick、关闭插值。没有读取旧图像素或缩小旧图。',
        'originalsPreserved': True, 'imageGenerationUsed': False, 'gameTested': False,
        'memoryMetric': 'RGBA各帧像素存储理论值；不含mipmap、图集和驱动开销，不代表实测显存或FPS。',
        'families': FAMILIES, 'totals': totals, 'records': records,
    }
    receipt_text = json.dumps(receipt, ensure_ascii=False, indent=2) + '\n'
    (LOG / 'fluid-lightening.json').write_text(receipt_text, encoding='utf-8')
    (DELIVERY / 'fluid-lightening.json').write_text(receipt_text, encoding='utf-8')
    overview(manifest)
    print(json.dumps(totals, indent=2), flush=True)


if __name__ == '__main__':
    main()
