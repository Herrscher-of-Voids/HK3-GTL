import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_千人人偶_原作重建_D2_20261117'
SOURCE = OUT/'references/mesh'
HEIGHT = 384


def main():
    data = json.loads((SOURCE/'original-preview.json').read_text('utf8'))
    vertices = np.array([v['position'] for v in data['vertices']])
    uv = np.array([v['uv'] for v in data['vertices']])
    faces = np.array([f['indices'] for f in data['faces']])
    scale = (HEIGHT-1)/np.ptp(vertices[:, 1])
    vertices[:, 1] -= vertices[:, 1].min()
    vertices[:, 2] *= -1
    vertices *= scale
    origin = np.floor(vertices.min(0)).astype(int)-2
    size = np.floor(vertices.max(0)).astype(int)-origin+3
    vertices -= origin
    width, height, depth = map(int, size)
    scores = np.full(width*height*depth, np.inf, np.float32)
    colors = np.zeros((scores.size, 3), np.uint8)
    color_sum = np.zeros((scores.size, 3), np.uint32)
    sample_count = np.zeros(scores.size, np.uint32)
    source_material = np.zeros(scores.size, np.uint8)
    face_start = 0
    sampled = 0
    for material_id, material in enumerate(data['materials']):
        texture = np.array(Image.open(SOURCE/f'textures/texture_{material["textureIndex"]:02}.png').convert('RGBA'))
        th, tw = texture.shape[:2]
        for indices in faces[face_start:face_start+material['faceCount']]:
            tri, tex = vertices[indices], uv[indices]
            steps = max(1, int(np.ceil(np.linalg.norm(tri-np.roll(tri, 1, axis=0), axis=1).max()/.25)))
            a, b = np.meshgrid(np.arange(steps+1), np.arange(steps+1), indexing='ij')
            keep = a+b <= steps
            weights = np.c_[a[keep], b[keep]]/steps
            weights = np.c_[weights, 1-weights.sum(1)]
            samples = weights@tri
            xyz = np.floor(samples).astype(int)
            tex_uv = weights@tex
            tx = np.clip(np.floor(tex_uv[:, 0]*tw).astype(int), 0, tw-1)
            ty = np.clip(np.floor(tex_uv[:, 1]*th).astype(int), 0, th-1)
            rgba = texture[ty, tx]
            opaque = rgba[:, 3] >= 128
            xyz, samples, rgba = xyz[opaque], samples[opaque], rgba[opaque]
            keys = (xyz[:, 1]*depth+xyz[:, 2])*width+xyz[:, 0]
            np.add.at(color_sum, keys, rgba[:, :3])
            np.add.at(sample_count, keys, 1)
            distance = np.square(samples-xyz-.5).sum(1)
            order = np.lexsort((distance, keys))
            first = np.r_[True, np.diff(keys[order]) != 0]
            chosen = order[first]
            keys, distance, rgba = keys[chosen], distance[chosen], rgba[chosen]
            replace = distance < scores[keys]
            keys = keys[replace]
            scores[keys], colors[keys], source_material[keys] = distance[replace], rgba[replace, :3], material_id
            sampled += len(samples)
        face_start += material['faceCount']
        print(f'原材质 {material_id+1}/9，累计采样 {sampled:,}', flush=True)

    surface = np.isfinite(scores).reshape(height, depth, width)
    colors[surface.ravel()] = np.rint(color_sum[surface.ravel()]/sample_count[surface.ravel(), None]).astype(np.uint8)
    closed = ndimage.binary_closing(surface)
    solid = ndimage.binary_fill_holes(surface | closed)
    missing = solid & ~surface
    nearest = ndimage.distance_transform_edt(~surface, return_distances=False, return_indices=True)
    nearest_keys = (nearest[0][missing]*depth+nearest[1][missing])*width+nearest[2][missing]
    missing_keys = np.flatnonzero(missing)
    colors[missing_keys] = colors[nearest_keys]
    source_material[missing_keys] = source_material[nearest_keys]
    keys = np.flatnonzero(solid)
    xyz = np.c_[keys % width, keys//(width*depth), keys//width % depth].astype(np.int32)+origin
    rgb = colors[keys]
    quantized = Image.fromarray(rgb.reshape(1, -1, 3)).quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    states = np.array(quantized, np.uint8).ravel()+1
    palette = np.array(quantized.getpalette(), np.uint8).reshape(-1, 3)[:128]
    np.savez_compressed(OUT/'原网格整数体素.npz', xyz=xyz, states=states, material=source_material[keys], surface=surface.ravel()[keys])
    (OUT/'原贴图色板.json').write_text(json.dumps(palette.tolist())+'\n', 'utf8')
    record = dict(height=HEIGHT, scale=scale, source_vertices=len(vertices), source_triangles=len(faces),
                  surface_blocks=int(surface.sum()), filled_blocks=int(missing.sum()), total_blocks=len(xyz),
                  bounds=dict(min=xyz.min(0).tolist(), max=xyz.max(0).tolist()), source_pose='原作A姿态',
                  coordinates='X宽、Y高、+Z正面；原网格Z轴翻转；全体等比缩放',
                  color_source='按原UV以0.25格间距采样原贴图，同格多点平均覆盖细线，128色自适应量化', sampled_points=sampled,
                  source='references/mesh/source-receipt.json')
    (OUT/'体素转换记录.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf8')
    print(json.dumps(record, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
