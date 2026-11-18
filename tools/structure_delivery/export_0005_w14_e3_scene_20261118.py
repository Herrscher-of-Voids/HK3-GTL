# -*- coding: utf-8 -*-
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W14_原生维度地貌_E3_20261118'
LOG = ROOT / 'logs/0005-w14-e3-production-20261118'
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
FACES = ['east', 'west', 'south', 'north', 'down', 'up']


def main():
    encoded = json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].strip().rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    with gzip.open(LOG / 'layers.json.gz', 'rt', encoding='utf8') as stream:
        layers = json.load(stream)
    materials = payload['materials']
    controller = next(i for i, material in enumerate(materials) if material['state'] == 'minecraft:redstone_block')
    native_states = {block['state'] - 1 for block in payload['data']['native_blocks']}
    for part in payload['parts']:
        for key in ['starts', 'lengths', 'spans']:
            for material in native_states | {controller}:
                part[key][material] = [[] for _ in FACES]
    for layer in layers:
        layer['rectangles'] = [r for r in layer['rectangles'] if r[0] not in native_states | {controller}]
    textures = [[Image.open(io.BytesIO(base64.b64decode(material['faces'][face].split(',', 1)[1]))).convert('RGBA')
                 for face in FACES] for material in materials]
    tile = max(max(image.size) for faces in textures for image in faces)
    columns, rows = 16, (len(materials) * 6 + 15) // 16
    atlas = Image.new('RGBA', (columns * tile, rows * tile))
    for i, faces in enumerate(textures):
        for face, image in enumerate(faces):
            at = i * 6 + face
            atlas.paste(image.resize((tile, tile), Image.Resampling.NEAREST), (at % columns * tile, at // columns * tile))
    palette = [material['state'] for material in materials]
    palette[controller] = 'hk3gtl:w14_world_bubble_recurrence_engine[facing=south]'
    data = dict(sizeXYZ=payload['data']['sizeXYZ'],
                blueprint_to_export_offset_xyz=[-value for value in payload['data']['bounds']['min']],
                controller_blueprint=[0, 44, 610], atlas_grid=[columns, rows], palette=palette,
                material_counts=[material['blocks'] for material in manifest['material_counts']],
                native_blocks=payload['data']['native_blocks'])
    scene = dict(data=data, materials=[dict(transparent=m['transparent'], emissive=m['emissive']) for m in materials],
                 parts=payload['parts'], layers=layers)
    directory = ASSETS / 'models/scene'
    directory.mkdir(parents=True, exist_ok=True)
    metadata = directory / 'w14_e3_meta.json'
    surfaces = directory / 'w14_e3.json.gz'
    texture = ASSETS / 'textures/effect/w14_e3_atlas.png'
    metadata.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), 'utf8')
    with gzip.open(surfaces, 'wt', encoding='utf8', compresslevel=6) as stream:
        json.dump(scene, stream, ensure_ascii=False, separators=(',', ':'))
    atlas.save(texture)
    receipt = dict(parts=len(scene['parts']), layers=len(layers), native_blocks=len(data['native_blocks']),
                   cells=sum(data['material_counts']), atlas_size=list(atlas.size),
                   source_palette_base=1, scene_palette_base=0,
                   files=[dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                               sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [metadata, surfaces, texture]])
    (LOG / 'client-scene.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
