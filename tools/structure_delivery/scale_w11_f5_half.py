"""从 F5 的完整实心切层生成半尺度 W11；每组八格保留占多数的非空气材质及其骨骼。"""
from datetime import datetime
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import export_0005_w11_f5_production_20261117 as f5
import export_0005_w11_f5_fx_20261117 as fx


SOURCE = f5.LOG
OUT = f5.ROOT/'logs/0000-w11-half-20261118'


def half_stripe(scene, x0, x1):
    lo = scene['low']*2
    size = (scene['high']-scene['low']+1)*2
    plane = np.zeros(((x1-x0)*2, size[1], size[2]), np.uint16)
    ranges = scene['rectangles']
    a, b = np.searchsorted(ranges[:, 3], [2*x0-15, 2*x1])
    for owner, material, _, x, y, z, width, depth in ranges[a:b].tolist():
        start, end = max(x, 2*x0), min(x+width, 2*x1)
        if start < end:
            plane[start-2*x0:end-2*x0, y-lo[1], z-lo[2]:z-lo[2]+depth] = owner*256+material
    samples = [plane[i::2,j::2,k::2] for i in range(2) for j in range(2) for k in range(2)]
    chosen = samples[0].copy()
    mixed = np.zeros(chosen.shape, bool)
    for sample in samples[1:]:
        mixed |= sample != chosen
    candidates = np.array([s[mixed] for s in samples]); best = np.zeros(candidates.shape[1], np.uint8)
    winner = np.zeros_like(candidates[0])
    for candidate in candidates:
        votes = (candidates == candidate).sum(axis=0, dtype=np.uint8)
        use = (candidate != 0) & (votes > best)
        winner[use], best[use] = candidate[use], votes[use]
    chosen[mixed] = winner
    return chosen.astype(np.uint8), (chosen >> 8).astype(np.uint8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    geo = json.loads((SOURCE/'geometry-scene.json').read_text('utf8'))
    receipt = json.loads((SOURCE/'资源导出回执.json').read_text('utf8'))
    with np.load(SOURCE/'w11_f5_surfaces.npz') as archive:
        rects = archive['layers']
    low, high = np.array(geo['low'])//2, np.array(geo['high'])//2
    control = np.array(geo['controller_blueprint'])//2
    materials = json.loads((SOURCE/'materials.json').read_text('utf8'))
    scene = dict(low=low, high=high, materials=materials, rectangles=rects[np.argsort(rects[:,3], kind='stable')]); del rects
    with TemporaryDirectory(dir=OUT) as temp:
        work = Path(temp)
        raw, qpath, lpath, low, high, counts = f5.write_raw(scene, half_stripe, control, work)
        size = high-low+1; palette = geo['palette']; bounds = dict(min=low.tolist(), max=high.tolist())
        geo.update(low=low.tolist(), high=high.tolist(), size_xyz=size.tolist(), sizeXYZ=size.tolist(),
                   controller_blueprint=control.tolist(), controller_xyz=(control-low).tolist(),
                   blueprint_to_export_offset_xyz=(-low).tolist(), material_counts=counts.tolist())
        geo['rig']['voxel_scale'] = 0.5
        f5.save(work/'geometry-scene.json', geo); f5.save(work/'materials.json', materials)
        q = np.fromfile(qpath, np.int32).reshape(-1,8); layers = np.fromfile(lpath, np.int32).reshape(-1,8)
        np.savez_compressed(work/'w11_f5_surfaces.npz', quads=q, layers=layers)
        mask = work/f5.MASK.name; bp = work/f5.BLUEPRINT.name
        mask_count, sections = f5.write_dynamic_mask(mask, layers, low)
        runs = f5.write_blueprint(raw, low, high, counts, palette, control, bp)
        meta = {k:v for k,v in receipt.items() if k not in ('resource_readback','exporter_sha256','metadata_sha256','geometry_sha256','surfaces_sha256')}
        meta.update(version='0000-W11-F5-half', conversation='0000', conversation_id='01a1d6a1-e812-7c21-b745-d9775cbc92cc',
            recorded_at=datetime.now().astimezone().isoformat(timespec='seconds'), source_bounds=bounds,
            source_origin_xyz=low.tolist(), size_xyz=size.tolist(), size_wdh=size[[0,2,1]].tolist(),
            blueprint_to_export_offset_xyz=(-low).tolist(), controller_source_xyz=control.tolist(), controller_xyz=(control-low).tolist(),
            controller_location='正面红毯入口中轴，朝南。', block_count=int(counts.sum()), material_counts=dict(zip(palette, counts.tolist())),
            used_palette_count=int(np.count_nonzero(counts)), unique_block_types=len({p.split('[')[0] for p,n in zip(palette,counts) if n}),
            rle_record_count=runs, blueprint_sha256=f5.digest(bp), blueprint_bytes=bp.stat().st_size,
            animation_mask_sha256=f5.digest(mask), animation_mask_sections=sections, animation_mask_blocks=mask_count,
            surface_geometry=dict(quads=len(q), layers=len(layers)), minimum_dimension_height=int(size[1]),
            scale=dict(linear=0.5, source_blocks=receipt['block_count'], source_dimensions=receipt['size_xyz'],
                       source_surfaces_sha256=f5.digest(SOURCE/'w11_f5_surfaces.npz'), method='2×2×2 格取非空气材质与骨骼的众数，保留薄片。'))
        meta['source_inputs'][Path(__file__).resolve().relative_to(f5.ROOT).as_posix()] = f5.digest(Path(__file__))
        assets = work/'assets'; fx.main(work, assets)
        for path in (assets/'models/scene').iterdir(): path.replace(fx.SCENE/path.name)
        bp.replace(f5.BLUEPRINT); mask.replace(f5.MASK); f5.save(f5.METADATA, meta)
        f5.save(OUT/'geometry-scene.json',geo); f5.save(OUT/'scale.json',meta)
        (work/'w11_f5_surfaces.npz').replace(OUT/'w11_f5_surfaces.npz')
        print(f"W11: {size.tolist()}, {int(counts.sum()):,} blocks",flush=True)


if __name__ == '__main__':
    main()
