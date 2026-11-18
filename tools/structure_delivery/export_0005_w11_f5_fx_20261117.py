import base64
import gzip
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'logs/0005-w11-f5-production-20261117'
ASSETS = ROOT/'src/main/resources/assets/hk3gtl'
SCENE = ASSETS/'models/scene'
FACES = ['east', 'west', 'south', 'north', 'down', 'up']


def dump(stream, value):
    json.dump(value, stream, ensure_ascii=False, separators=(',', ':'))


def part(rows, owner, group, materials, metadata):
    points = rows[:, 3:6].astype(np.int64)
    extent = np.ones_like(points)
    for face in range(6):
        selected = rows[:, 2] == face
        axis, cross = (2, 1) if face < 2 else (0, 1) if face < 4 else (0, 2)
        extent[selected, axis], extent[selected, cross] = rows[selected, 6], rows[selected, 7]
    origin = points.min(axis=0)
    size = (points+extent).max(axis=0)-origin
    points -= origin
    linear = (points[:, 1]*size[2]+points[:, 2])*size[0]+points[:, 0]
    starts = [[[] for _ in range(6)] for _ in range(materials)]
    lengths = [[[] for _ in range(6)] for _ in range(materials)]
    spans = [[[] for _ in range(6)] for _ in range(materials)]
    for material in np.unique(rows[:, 1]):
        for face in range(6):
            chosen = (rows[:, 1] == material)&(rows[:, 2] == face)
            starts[int(material)-1][face] = linear[chosen].tolist()
            lengths[int(material)-1][face] = rows[chosen, 6].tolist()
            spans[int(material)-1][face] = rows[chosen, 7].tolist()
    return dict(id=f'{owner}_{group}', origin=origin.tolist(), size=size.tolist(),
                starts=starts, lengths=lengths, spans=spans, metadata=metadata)


def main(source=SOURCE, assets=ASSETS):
    scene_dir = assets/'models/scene'
    geometry = json.loads((source/'geometry-scene.json').read_text('utf8'))
    materials = json.loads((source/'materials.json').read_text('utf8'))
    palette = geometry['palette']
    count = len(palette)
    columns, rows = 16, (count*6+15)//16
    textures = [[Image.open(io.BytesIO(base64.b64decode(m['faces'][name].split(',', 1)[1]))).convert('RGBA') for name in FACES] for m in materials]
    tile = max(max(texture.size) for faces in textures for texture in faces)
    atlas = Image.new('RGBA', (columns*tile, rows*tile))
    for index, material in enumerate(materials):
        for face, name in enumerate(FACES):
            texture = textures[index][face].resize((tile, tile), Image.Resampling.NEAREST)
            at = index*6+face
            atlas.paste(texture, (at%columns*tile, at//columns*tile))
    destination = assets/'textures/effect/w11_f5_atlas.png'
    destination.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(destination)
    low = np.array(geometry['low'], int)
    data = dict(sizeXYZ=geometry['sizeXYZ'], blueprint_to_export_offset_xyz=(-low).tolist(),
                controller_blueprint=geometry['controller_blueprint'], atlas_grid=[columns, rows], palette=palette,
                material_counts=geometry['material_counts'], rig=geometry['rig'])
    scene_dir.mkdir(parents=True, exist_ok=True)
    (scene_dir/'w11_f5_meta.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), 'utf8')
    material_data = [dict(transparent=m['transparent'], emissive=m['emissive']) for m in materials]
    material_data += [dict(transparent=False, emissive=False)]*(count-len(material_data))
    with np.load(source/'w11_f5_surfaces.npz') as archive:
        quads, layers = archive['quads'], archive['layers']
    group = quads[:, 0].astype(np.int64)*4096+(quads[:, 3]-low[0])//16
    order = np.argsort(group, kind='stable')
    sorted_groups = group[order]
    boundaries = np.r_[0, np.flatnonzero(np.diff(sorted_groups))+1, len(order)]
    totals = dict(parts=0, quads=len(quads), layer_rectangles=len(layers))
    with gzip.open(scene_dir/'w11_f5.json.gz', 'wt', encoding='utf8', compresslevel=6) as stream:
        stream.write('{"data":');dump(stream, data)
        stream.write(',"materials":');dump(stream, material_data)
        stream.write(',"parts":[')
        for start, end in zip(boundaries[:-1], boundaries[1:]):
            selected = quads[order[start:end]]
            owner = int(selected[0, 0]);code = int(sorted_groups[start]%4096)
            if totals['parts']:stream.write(',')
            dump(stream, part(selected, owner, code, count, geometry['owners'][str(owner)]))
            totals['parts'] += 1
        stream.write('],"layers":[')
        y_order = np.argsort(layers[:, 4], kind='stable')
        heights = layers[y_order, 4]
        for index, y in enumerate(range(int(low[1]), int(low[1])+data['sizeXYZ'][1])):
            if index:stream.write(',')
            start, end = np.searchsorted(heights, [y, y+1])
            selected = layers[y_order[start:end]]
            rectangles = selected[:, [1, 3, 5, 6, 7]].copy()
            rectangles[:, 0] -= 1
            dump(stream, dict(y=y, rectangles=rectangles.tolist()))
        stream.write(']}')
    (source/'fx-export.json').write_text(json.dumps(totals, ensure_ascii=False, indent=2)+'\n', 'utf8')
    print(json.dumps(totals), flush=True)


if __name__ == '__main__':
    main()
