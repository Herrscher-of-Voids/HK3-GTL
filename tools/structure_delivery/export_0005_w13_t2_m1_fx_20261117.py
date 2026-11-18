import base64
import gzip
import io
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'logs/0005-w13-t2-production-20261117'
ASSETS = ROOT/'src/main/resources/assets/hk3gtl'
FACES = ['east', 'west', 'south', 'north', 'down', 'up']


def main():
    with gzip.open(SOURCE/'client-surfaces.json.gz', 'rt', encoding='utf8') as stream:
        payload = json.load(stream)
    geometry = json.loads((ROOT/'deliveries/0005_W13_侵蚀之律者电视山_T2_20261117/geometry.json').read_text('utf8'))
    with gzip.open(SOURCE/'layers.json.gz', 'rt', encoding='utf8') as stream:
        layers = json.load(stream)
    materials = payload['materials']
    columns, rows = 16, (len(materials)*6+15)//16
    textures = [[Image.open(io.BytesIO(base64.b64decode(material['faces'][face].split(',', 1)[1]))).convert('RGBA') for face in FACES] for material in materials]
    tile = max(max(image.size) for faces in textures for image in faces)
    atlas = Image.new('RGBA', (columns*tile, rows*tile))
    for i, faces in enumerate(textures):
        for f, image in enumerate(faces):
            at = i*6+f
            atlas.paste(image.resize((tile, tile), Image.Resampling.NEAREST), (at%columns*tile, at//columns*tile))
    destination = ASSETS/'textures/effect/w13_t2_m1_atlas.png'
    destination.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(destination)
    palette = [material['state'] for material in materials]
    material_counts = [geometry['material_counts'][state] for state in palette]
    palette[23] = 'hk3gtl:w13_self_computing_research_mother'
    for part in payload['parts']:
        part['starts'][23] = [[] for _ in FACES]
        part['lengths'][23] = [[] for _ in FACES]
        part['spans'][23] = [[] for _ in FACES]
    data = dict(sizeXYZ=payload['data']['sizeXYZ'],
                blueprint_to_export_offset_xyz=[-v for v in geometry['bounds']['min']],
                controller_blueprint=[0, 16, 472], atlas_grid=[columns, rows], palette=palette,
                material_counts=material_counts, rig=payload['data']['rig'])
    scene = dict(data=data, materials=[dict(transparent=m['transparent'], emissive=m['emissive']) for m in materials], parts=payload['parts'], layers=layers)
    directory = ASSETS/'models/scene'
    directory.mkdir(parents=True, exist_ok=True)
    (directory/'w13_t2_m1_meta.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), 'utf8')
    with gzip.open(directory/'w13_t2_m1.json.gz', 'wt', encoding='utf8', compresslevel=6) as stream:
        json.dump(scene, stream, ensure_ascii=False, separators=(',', ':'))
    print(json.dumps(dict(parts=len(scene['parts']), layers=len(layers), atlas=atlas.size)), flush=True)


if __name__ == '__main__':
    main()
