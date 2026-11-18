import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFont

import package_0002_fluid_r15_light as r15
import prepare_0002_fluids_r16 as r16


ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / 'deliveries/0002贴图材质_发电补充_R17_20261116'
LOG = ROOT / 'logs/textures-energy-handoff-0002-r17-20261116'
CONTEXT = LOG / 'fluids-context.json'
ASSETS = DELIVERY / 'candidate-assets'

DESIGNS = {
    'resonance_activated_honkai_fuel': (
        'world', '#414e7d', '#a6c9e0',
        '紫蓝燃料中分布青白短晶点与成对短波纹，晶点轻微迁移，波纹亮度随四帧循环。',
    ),
    'supercritical_honkai_fuel': (
        'viscous', '#35315a', '#a194be',
        '深靛稠密燃料含银白微囊，细小紫红压力缝在四帧中交替变亮，表现受控承压分散相。',
    ),
    'imaginary_coupled_honkai_fuel': (
        'world', '#4c326a', '#ac9ed0',
        '深紫载液中悬浮金白陶瓷薄壳，两组偏折蓝紫细流交错，体现隔离和相位耦合。',
    ),
    'continuity_confined_honkai_fuel': (
        'energy', '#2a203e', '#8b76a2',
        '绀黑暗紫分层液相含银白短纤维与细小金紫闭合折纹，分区缓慢迁移，亮纹保持闭合并周期脉动。',
    ),
}


def frames(fluid_id, kind):
    family, body_hex, light_hex, _ = DESIGNS[fluid_id]
    r15.DESIGNS[fluid_id] = family, body_hex, light_hex
    base = r15.paint(fluid_id)
    body, light = ImageColor.getrgb(body_hex), ImageColor.getrgb(light_hex)
    result = []
    for phase in range(4):
        image = base.copy()
        rng = random.Random(int(hashlib.sha256((fluid_id + ':r17').encode()).hexdigest()[:16], 16))
        pulse = (0, .4, 1, .4)[phase]
        if fluid_id == 'resonance_activated_honkai_fuel':
            crystal = r15.mix((125, 189, 205), (225, 242, 240), .35 + pulse * .25)
            r16.grains(image, rng, 31, [crystal, (142, 190, 212)], 1)
            for _ in range(15):
                x, y = rng.randrange(64), rng.randrange(64)
                for dy, length in ((0, 4), (3, 6)):
                    r15.wrapped_line(image, [(x, y + dy), (x + length, y + dy), (x + length + 1, y + dy - 1)], (*r15.mix(body, crystal, .32 + pulse * .25), 255))
        elif fluid_id == 'supercritical_honkai_fuel':
            for _ in range(42):
                x, y = rng.randrange(64), rng.randrange(64)
                r16.polygon(image, [(x, y), (x + 2, y), (x + 3, y + 1), (x + 2, y + 2), (x, y + 2)], r15.mix(body, light, .52))
                r15.wrapped_line(image, [(x + 1, y + 1), (x + 2, y + 1)], (*r15.mix(body, (215, 219, 230), .64), 255))
            for _ in range(17):
                x, y = rng.randrange(64), rng.randrange(64)
                r15.wrapped_line(image, [(x, y), (x + 3, y), (x + 4, y - 2), (x + 6, y - 2)], (*r15.mix(body, (177, 83, 133), .44 + pulse * .42), 255))
        elif fluid_id == 'imaginary_coupled_honkai_fuel':
            r16.flakes(image, rng, 22, [(179, 172, 175), (205, 194, 161), (221, 218, 221)], (2, 5))
            r16.fibers(image, rng, 16, [(101, 116, 169), (143, 125, 190)], (-1,))
            r16.fibers(image, rng, 15, [r15.mix(body, (167, 160, 212), .45 + pulse * .32)], (1,))
        else:
            r16.fibers(image, rng, 19, [(164, 170, 190), (119, 123, 149)], (-1, 1))
            for index in range(12):
                x, y = rng.randrange(64), rng.randrange(64)
                w, h = rng.randrange(3, 6), rng.randrange(2, 4)
                color = (184, 157, 101) if index % 3 == 0 else (147, 111, 177)
                points = [(x + 1, y), (x + w - 1, y), (x + w, y + 1), (x + w, y + h - 1), (x + w - 1, y + h), (x + 1, y + h), (x, y + h - 1), (x, y + 1), (x + 1, y)]
                r15.wrapped_line(image, points, (*r15.mix(body, color, .52 + pulse * .3), 255))
        offset = ((0, 0), (1, 1), (2, 0), (1, -1))[phase] if kind == 'still' else ((0, 0), (0, 1), (0, 2), (0, 1))[phase]
        result.append(ImageChops.offset(image, *offset))
    return result


def save_texture(fluid_id, target, kind):
    relative = Path(target.removeprefix('src/main/resources/'))
    output = ASSETS / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    size = 128 if kind == 'flow' else 64
    strip = Image.new('RGBA', (size, size * 4))
    for index, tile in enumerate(frames(fluid_id, kind)):
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
        'metadataTarget': target + '.mcmeta',
        'resource': 'hk3gtl:' + relative.as_posix().removeprefix('assets/hk3gtl/textures/').removesuffix('.png'),
        'size': list(strip.size), 'frameSize': [size, size], 'frames': 4,
        'sha256': r16.digest(output), 'bytes': output.stat().st_size,
        'metadataSha256': r16.digest(metadata), 'metadataBytes': metadata.stat().st_size,
        'animation': animation, 'rgbaFrameStorageBytes': strip.width * strip.height * 4,
    }


def overview(records):
    sheet = Image.new('RGB', (1224, 480), '#18202a')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
    draw.text((24, 16), 'R17 发电补充 · 四种分级崩坏燃料流体候选', font=font, fill='#edf3ff')
    draw.text((24, 53), '原生64像素 · 静止64 / 流动128 · 4帧 · 6tick/帧 · 关闭插值', font=small, fill='#becfe3')
    for index, record in enumerate(records):
        x, y = 20 + index * 300, 100
        with Image.open(DELIVERY / record['staticPreview']) as tile:
            sheet.paste(tile, (x, y))
        draw.text((x, y + 227), record['name'], font=small, fill='#edf3ff')
        draw.text((x, y + 256), f"Tier {record['firstTier']}", font=small, fill='#9dafc3')
        draw.text((x, y + 283), {'resonance_activated_honkai_fuel': '青白晶点与短波纹', 'supercritical_honkai_fuel': '稠密微囊与压力细缝', 'imaginary_coupled_honkai_fuel': '陶瓷薄壳与交错细流', 'continuity_confined_honkai_fuel': '银白短纤与金紫闭合折纹'}[record['id']], font=small, fill='#9dafc3')
    sheet.save(DELIVERY / 'fluid-overview.png', optimize=True)
    sheet = Image.new('RGB', (1120, 280 * len(records)), '#18202a')
    draw = ImageDraw.Draw(sheet)
    for row, record in enumerate(records):
        y = row * 280
        draw.text((24, y + 8), record['name'] + ' · 四帧静止图', font=font, fill='#edf3ff')
        for phase, tile in enumerate(frames(record['id'], 'still')):
            sheet.paste(tile.resize((220, 220), Image.Resampling.NEAREST), (24 + phase * 274, y + 45))
    sheet.save(DELIVERY / 'fluid-frames.png', optimize=True)


def main():
    DELIVERY.mkdir(parents=True, exist_ok=True)
    (DELIVERY / 'fluid-previews').mkdir(exist_ok=True)
    r16.DELIVERY = DELIVERY
    records, resources = [], []
    for fluid in sorted(json.loads(CONTEXT.read_text(encoding='utf-8-sig')), key=lambda item: item['firstTier']):
        fluid_id = fluid['id'].split(':')[1]
        textures = [save_texture(fluid_id, target, 'flow' if target.endswith('_flow.png') else 'still') for target in fluid['targets'] if target.endswith('.png')]
        inputs = [item for group in ('items', 'fluids') for item in fluid['producerRecipes'][0][group]]
        record = {
            'id': fluid_id, 'resourceId': fluid['id'], 'name': fluid['name'], 'kind': 'fluid',
            'status': '候选待审', 'facts': [fluid['role'], '配方来源：' + '、'.join(fluid['producers']), '生产投入：' + '、'.join(item['name'] for item in inputs)],
            'purpose': fluid['role'], 'visualBasis': fluid['visualBasis'], 'designZh': DESIGNS[fluid_id][3],
            'firstTier': fluid['firstTier'], 'palette': list(DESIGNS[fluid_id][1:3]),
            'producerRecipes': [{'id': recipe['uid'], 'title': recipe['title']} for recipe in fluid['producerRecipes']],
            'consumers': fluid['consumers'], 'targets': fluid['targets'], 'textures': textures,
            'preview': r16.animation_preview(textures[0], fluid_id),
            'staticPreview': r16.preview(frames(fluid_id, 'still')[0], fluid_id), 'image': textures[0]['image'],
            'artApproved': False, 'sourceApplied': False,
        }
        records.append(record)
        for texture in textures:
            for kind, file, target, digest in (
                ('texture', texture['image'], texture['target'], texture['sha256']),
                ('animation', texture['metadata'], texture['metadataTarget'], texture['metadataSha256']),
            ):
                resources.append({'id': fluid_id, 'kind': kind, 'file': file, 'target': target, 'source_path': (DELIVERY / file).relative_to(ROOT).as_posix(), 'jar_entry': target.removeprefix('src/main/resources/'), 'sha256': digest})
    manifest = {
        'revision': 'R17', 'conversation': '0002贴图材质', 'status': '候选待审',
        'sourceContext': CONTEXT.relative_to(ROOT).as_posix(),
        'method': '复用R15原生64像素周期液面与R16分散相绘制，依据燃料工艺分别增加晶点、微囊、陶瓷薄壳与短纤；静止64，流动按64图2×2平铺为128，4帧、6tick、关闭插值。',
        'imageGenerationUsed': False, 'sourceResourcesChanged': False,
        'fluidCount': len(records), 'pngCount': 8, 'metadataCount': 8,
        'pngBytes': sum(texture['bytes'] for record in records for texture in record['textures']),
        'metadataBytes': sum(texture['metadataBytes'] for record in records for texture in record['textures']),
        'rgbaFrameStorageBytes': sum(texture['rgbaFrameStorageBytes'] for record in records for texture in record['textures']),
        'memoryMetric': 'RGBA全部动画帧的理论像素存储，不含mipmap、图集与驱动开销。',
        'records': records, 'resources': resources,
    }
    content = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    (DELIVERY / 'fluid-manifest.json').write_text(content, encoding='utf-8')
    (LOG / 'fluid-candidates.json').write_text(content, encoding='utf-8')
    overview(records)
    print(json.dumps({key: manifest[key] for key in ('fluidCount', 'pngCount', 'metadataCount', 'pngBytes', 'metadataBytes', 'rgbaFrameStorageBytes')}))


if __name__ == '__main__':
    main()
