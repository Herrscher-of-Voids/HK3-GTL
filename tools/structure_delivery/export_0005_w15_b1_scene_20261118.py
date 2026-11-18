import base64
import gzip
import io
import json
from pathlib import Path

from PIL import Image

import export_0005_w15_b1_production_blueprint_20261118 as blueprint


ROOT, SOURCE, LOG = blueprint.ROOT, blueprint.SOURCE, blueprint.LOG
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
FACES = ['east', 'west', 'south', 'north', 'down', 'up']


def remove_controller_face(parts, material):
    removed = 0
    controller = blueprint.CONTROLLER.tolist()
    for part in parts:
        w, _, d = part['size']
        for face in range(6):
            axis, cross = (2 if face < 2 else 0), (1 if face < 4 else 2)
            fixed = 3-axis-cross
            starts, lengths, spans = [], [], []

            def append(start, length, span):
                local = [value-base for value, base in zip(start, part['origin'])]
                starts.append((local[1]*d+local[2])*w+local[0])
                lengths.append(length)
                spans.append(span)

            for at, length, span in zip(part['starts'][material][face], part['lengths'][material][face], part['spans'][material][face]):
                start = [at % w+part['origin'][0], at // (w*d)+part['origin'][1], at // w % d+part['origin'][2]]
                a, b = controller[axis]-start[axis], controller[cross]-start[cross]
                if start[fixed] == controller[fixed] and 0 <= a < length and 0 <= b < span:
                    removed += 1
                    for da, db, width, height in [(0, 0, length, b), (0, b+1, length, span-b-1),
                                                  (0, b, a, 1), (a+1, b, length-a-1, 1)]:
                        if width and height:
                            piece = start.copy()
                            piece[axis] += da
                            piece[cross] += db
                            append(piece, width, height)
                else:
                    append(start, length, span)
            part['starts'][material][face] = starts
            part['lengths'][material][face] = lengths
            part['spans'][material][face] = spans
    return removed


def main():
    encoded = json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].strip().rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    approved = json.loads(blueprint.METADATA.read_text('utf8'))
    with gzip.open(blueprint.LAYERS, 'rt', encoding='utf8') as stream:
        layers = json.load(stream)
    materials = payload['materials']
    previous = approved['controller_previous_state']
    controller_material = next(i for i, material in enumerate(materials) if material['state'] == previous)
    removed_faces = remove_controller_face(payload['parts'], controller_material)
    for part in payload['parts']:
        for key in ['starts', 'lengths', 'spans']:
            part[key].append([[] for _ in FACES])
    textures = [[Image.open(io.BytesIO(base64.b64decode(material['faces'][face].split(',', 1)[1]))).convert('RGBA')
                 for face in FACES] for material in materials]
    tile = max(max(image.size) for faces in textures for image in faces)
    columns, rows = 16, (len(approved['palette'])*6+15)//16
    atlas = Image.new('RGBA', (columns*tile, rows*tile))
    for i, faces in enumerate(textures):
        for face, texture in enumerate(faces):
            at = i*6+face
            atlas.paste(texture.resize((tile, tile), Image.Resampling.NEAREST), (at % columns*tile, at // columns*tile))
    data = dict(sizeXYZ=approved['size_xyz'],
                blueprint_to_export_offset_xyz=approved['blueprint_to_export_offset_xyz'],
                controller_blueprint=blueprint.CONTROLLER.tolist(), atlas_grid=[columns, rows],
                palette=approved['palette'], material_counts=list(approved['material_counts'].values()),
                page_titles=approved['page_titles'], effect_bounds=payload['data']['effect_bounds'])
    scene = dict(data=data,
                 materials=[dict(transparent=m['transparent'], emissive=m['emissive']) for m in materials]
                           + [dict(transparent=False, emissive=False)],
                 parts=payload['parts'], layers=layers)
    directory = ASSETS / 'models/scene'
    directory.mkdir(parents=True, exist_ok=True)
    metadata = directory / 'w15_b1_meta.json'
    surfaces = directory / 'w15_b1.json.gz'
    texture = ASSETS / 'textures/effect/w15_b1_atlas.png'
    previous_files = blueprint.backup([metadata, surfaces, texture], 'before-scene-export')
    metadata.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), 'utf8')
    with surfaces.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', compresslevel=6, mtime=0) as stream:
        stream.write(json.dumps(scene, ensure_ascii=False, separators=(',', ':')).encode('utf8'))
    atlas.save(texture)
    receipt = dict(parts=len(scene['parts']), layers=len(layers), native_blocks=0,
                   source_surface_quads=318031,
                   surface_quads=sum(len(face) for part in scene['parts'] for material in part['starts'] for face in material),
                   controller_removed_surface_cells=removed_faces,
                   controller_rendering='唯一主控以原生模型显示，静态网格不覆盖该格。',
                   material_count_exception=approved['material_count_exception'],
                   source_materials=len(materials), palette_count=len(data['palette']), controller_palette_index=len(materials),
                   cells=sum(data['material_counts']), atlas_size=list(atlas.size), atlas_grid=[columns, rows],
                   source_palette_base=1, scene_palette_base=0, backup=previous_files,
                   files=[dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                               sha256=blueprint.shared.digest(p)) for p in [metadata, surfaces, texture]])
    blueprint.shared.save(LOG / 'client-scene.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
