from datetime import datetime
from io import BytesIO
from pathlib import Path
import base64
import gzip
import hashlib
import json
import math
import struct
import subprocess

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/0005-wonder-effects-repair-20261117/generated-resources'
RESOURCE = ROOT / 'src/main/resources'
SOURCES = {
    'w05_r3': ROOT / 'deliveries/0005_W05_七处穿模修订_R3_20261115',
    'w06_author': ROOT / 'deliveries/0005_W06_GTL现有方块保色_V1_20261115',
}
NODE = 'C:/Program Files/nodejs/node.exe'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def write_gzip(path, value):
    with gzip.GzipFile(filename='', fileobj=path.open('wb'), mode='wb', compresslevel=9, mtime=0) as stream:
        stream.write(value)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sample_paths(paths):
    code = '''
import * as THREE from 'three';
let input='';for await(const part of process.stdin)input+=part;
const paths=JSON.parse(input);
process.stdout.write(JSON.stringify(paths.map(points=>{
    const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)),false,'centripetal');
    return Array.from({length:257},(_,i)=>curve.getPointAt(i/256).toArray().map(v=>+v.toFixed(5)));
})));
'''
    result = subprocess.run([NODE, '--input-type=module', '-e', code], cwd=ROOT,
        input=json.dumps(paths), capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def w05_effects(parts):
    paths = [path if index == 0 else path[:len(path) // 2 + 1]
        for part in parts for index, path in enumerate(part['metadata'].get('flow_paths', []))]
    streams, phases = [], []
    for side in (-1, 1):
        wing_paths = [p for p in paths if np.sign(p[len(p) // 3][0]) == side]
        for i in range(10):
            angle, radius = i / 10 * math.tau, 12 + i % 3 * 9
            streams.append([[-radius * math.sin(angle), 160 + radius * math.cos(angle), -350],
                [radius * math.sin(angle), 160 + radius * math.cos(angle), -210], [0, 160, 0],
                *wing_paths[i % len(wing_paths)], [0, 160, 90],
                [radius * math.sin(angle), 160 + radius * math.cos(angle), 250],
                [radius * math.sin(angle) * 1.7, 160 + radius * math.cos(angle) * 1.7, 350]])
            phases.append(i * .017)
    effects = [p['metadata']['effect'] for p in parts if 'effect' in p['metadata']]
    return dict(center=[0, 160, 0], flow_paths=paths, stream_paths=sample_paths(streams),
        stream_phase_offsets=phases, stream_samples=257, flow_speed=.034, flow_beads_per_path=7,
        flow_bead_radii=[1.65, .95, .95], flow_color=0xccfff4, flow_tube_color=0x36f6c0,
        towers=[e for e in effects if e['kind'] == 'vortex_tower'], tower_speed=.25,
        tower_running_multiplier=2.5, tower_strands=3, tower_turns=2.7,
        lightning_origins=[e['origin'] for e in effects if e['kind'] == 'lightning'],
        lightning_target=[0, 160, 0], lightning_branches=4, lightning_samples=15,
        lightning_color=0x38ffb1, pulse_speed=5.5, pulse_phase_multiplier=2,
        pulse_visible_threshold=-.55, tail_ring_z=[295, 310, 325, 340], tail_ring_radii=[30, 25, 20, 15],
        tail_ring_radius=1, tail_color=0x79fbe9, tail_helix_start_z=[278, 301, 324],
        tail_helix_length=23, crown_center=[0, 160, 0], crown_y_range=[160, 290],
        crown_radius_range=[18, 124], crown_strands=24, crown_twist=.7,
        crowns=[dict(id=p['id'], pivot=p['metadata']['motion']['pivot'],
            motion_axis=p['metadata']['motion']['axis'], idle_speed=0, running_speed=1.75,
            accents=p['metadata']['accents'])
            for p in parts if p['id'].startswith('crown_')],
        tornado_speed=-.65, tornado_y_range=[8, 320], tornado_radius=35,
        tornado_turns=3.1, tornado_strands=6, refraction_speeds=[.4, -.4, .4],
        core_texture_scroll=[.025, .3, .06], core_running_white=True)


def w06_effects():
    return dict(center=[401, 0, 361], snow_count=620, snow_width=780, snow_depth=700,
        snow_height=382, snow_speed_range=[2, 7], snow_preview_step=.18,
        snow_wind_frequency=.55, snow_wind_particle_phase=.37, snow_wind_step=.13,
        snow_color=0xe5faff, snow_size=3.2, snow_opacity=.72, star_count=90,
        star_y_range=[24, 376], star_color=0xffd978, star_size=5,
        star_opacity=[.62, .18], star_frequency=2.6, aurora_count=4,
        aurora_width=1000, aurora_steps=72, aurora_y=420, aurora_y_step=15,
        aurora_y_amplitude=24, aurora_z_offset=-430, aurora_z_step=155,
        aurora_z_amplitude=38, aurora_y_extent=[-55, 105], aurora_color=0x398bbb,
        aurora_opacity=[.075, .025], aurora_frequency=.28, beam_height=382,
        beam_y_center=191, beam_radii=[7.5, .72, 2.5], beam_colors=[0xa7f4ff, 0xffd970, 0xe3fdff],
        beam_opacity=[.42, .92, .3], beam_opacity_amplitudes=[.1, 0, .13],
        beam_frequencies=[4, 0, 5.2], beam_phases=[0, 0, 1], beam_running_only=True,
        end_ring_y=[1, 381], end_ring_radius=11, end_ring_thickness=.7,
        end_ring_color=0xc4f8ff, end_ring_scale_amplitude=.08, end_ring_frequency=2.8,
        pool_texture_scroll=[.018, .23, .04])


def write_mask(name, parts, meta, source):
    size = np.array(meta['size_xyz'])
    low = np.array(meta['source_origin_xyz'])
    w, h, d = map(int, size)
    selected = {p['id'] for p in parts if 'motion' in p['metadata']}
    owner = np.zeros(w * h * d, np.bool_)
    with np.load(source / '原始构件数据.npz') as archive:
        for part in parts:
            p = archive[part['id'] + '_xyz'] - low
            linear = (p[:, 0].astype(np.int64) * h + p[:, 1]) * d + p[:, 2]
            owner[linear] = True if part['id'] in selected else (
                archive[part['id'] + '_materials'] == 8 if name == 'w06_author' else False)
    controller = np.array(meta['controller_xyz'])
    owner[(controller[0] * h + controller[1]) * d + controller[2]] = False
    positions = np.flatnonzero(owner)
    del owner
    nx, ny, nz = (size + 15) // 16
    rows = np.zeros((nx * ny * nz, 64), np.uint64)
    for start in range(0, len(positions), 262144):
        current = positions[start:start + 262144]
        x, y, z = current // (h * d), current // d % h, current % d
        section = ((x >> 4) * ny + (y >> 4)) * nz + (z >> 4)
        bit = (((y & 15) * 16 + (z & 15)) * 16 + (x & 15)).astype(np.uint64)
        np.bitwise_or.at(rows, (section, (bit >> 6).astype(np.int64)),
            np.left_shift(np.uint64(1), bit & 63))
    occupied = np.flatnonzero(np.any(rows, axis=1))
    sections = ((occupied // (ny * nz)) << 38) | ((occupied % nz) << 12) | (occupied // nz % ny)
    path = OUT / ('data/hk3gtl/structures/' + name + '_mask.bin.gz')
    with gzip.GzipFile(filename='', fileobj=path.open('wb'), mode='wb', compresslevel=9, mtime=0) as stream:
        stream.write(struct.pack('>2i', 0x5746584d, len(sections)))
        for index in np.argsort(sections):
            stream.write(struct.pack('>q', int(sections[index])))
            stream.write(rows[occupied[index]].astype('>u8').tobytes())
    return dict(blocks=len(positions), sections=len(sections), magic='0x5746584d',
        ownership='按完整蓝图构件顺序后写优先，仅遮盖最终属于动态构件或滚动材质的方块，保留主控。')


def export(name, source):
    payload = (source / 'data.js').read_text('utf8')
    config = json.loads(gzip.decompress(base64.b64decode(json.loads(payload.split('=', 1)[1].rstrip(';\n')))))
    role = name[:3]
    meta = json.loads((RESOURCE / ('data/hk3gtl/structures/' + role + '_approved.json')).read_text('utf8'))
    parts = config['parts']
    effects = w05_effects(parts) if role == 'w05' else w06_effects()
    dynamic = [part for part in parts if 'motion' in part['metadata']]
    idle_speeds = {'turbine': .12, 'gyro': .12, 'crown': 0, 'vortex': .22}
    running_speeds = {'turbine': .8, 'gyro': .12, 'crown': 1.75, 'vortex': .9}
    for part in dynamic:
        motion = part['metadata']['motion']
        kind, sign = motion.get('kind', 'halo'), motion.get('sign', 1)
        if kind == 'core':
            part['metadata'].update(motion_kind='bob', pivot=motion['pivot'], motion_axis=[0, 1, 0],
                idle_speed=0, running_speed=0, amplitude=1.2, frequency=.6)
        else:
            idle = motion.get('speed', .008 if role == 'w06' else idle_speeds[kind])
            running = motion.get('speed', .025 if role == 'w06' else running_speeds[kind])
            part['metadata'].update(motion_kind='rotation', pivot=motion['pivot'], motion_axis=motion['axis'],
                idle_speed=idle * sign, running_speed=running * sign)
        part['spans'] = [[[1] * len(face) for face in material] for material in part['starts']]
    if role == 'w06':
        for part in parts:
            if 'motion' in part['metadata'] or not any(part['starts'][7]):
                continue
            layer = dict(part, id=part['id'] + '_material_7', metadata=dict(part['metadata'],
                source_component=part['id'], motion_kind='material', pivot=[0, 0, 0],
                motion_axis=[0, 1, 0], idle_speed=0, running_speed=0))
            layer['starts'] = [[[] for _ in range(6)] for _ in config['materials']]
            layer['lengths'] = [[[] for _ in range(6)] for _ in config['materials']]
            layer['starts'][7], layer['lengths'][7] = part['starts'][7], part['lengths'][7]
            layer['spans'] = [[[1] * len(face) for face in material] for material in layer['starts']]
            dynamic.append(layer)
    data = dict(config['data'], controller_blueprint=meta['controller_source_xyz'],
        controller_export=meta['controller_xyz'], source_facing='north', sizeXYZ=meta['size_xyz'],
        blueprint_to_export_offset_xyz=[-n for n in meta['source_origin_xyz']],
        effects=effects, appearance_approved=True, native_dynamic_components_only=True)
    atlas = Image.new('RGBA', (1024, 512))
    materials = []
    for index, item in enumerate(config['materials']):
        image = Image.open(BytesIO(base64.b64decode(item['texture'].split(',', 1)[1])))
        image = image.convert('RGBA').resize((64, 64), Image.Resampling.NEAREST)
        for face in range(6):
            slot = index * 6 + face
            atlas.paste(image, (slot % 16 * 64, slot // 16 * 64))
        materials.append(dict(item, texture='', emissive=item['emissiveIntensity'] >= .2,
            emissive_color=item['emissive']))
    scene = dict(data=data, parts=dynamic, materials=materials)
    scene_path = OUT / ('assets/hk3gtl/models/scene/' + name + '.json.gz')
    atlas_path = OUT / ('assets/hk3gtl/textures/effect/' + name + '_atlas.png')
    write_gzip(scene_path, json.dumps(scene, ensure_ascii=False, separators=(',', ':')).encode('utf8'))
    atlas.save(atlas_path, optimize=True)
    geometry_source = ROOT / meta['source']
    mask = write_mask(name, parts, meta, geometry_source)
    save(OUT / (name + '_effects.json'), effects)
    return dict(role=role, source=str(source.relative_to(ROOT)).replace('\\', '/'),
        geometry_source=str(geometry_source.relative_to(ROOT)).replace('\\', '/'),
        source_payload_sha256=digest(source / 'data.js'),
        source_npz_sha256=digest(geometry_source / '原始构件数据.npz'),
        controller_blueprint=data['controller_blueprint'], controller_export=data['controller_export'],
        blueprint_to_export_offset_xyz=data['blueprint_to_export_offset_xyz'], sizeXYZ=data['sizeXYZ'],
        dynamic_component_count=len(dynamic), dynamic_components=[p['id'] for p in dynamic],
        material_count=len(materials), atlas_size=[1024, 512], atlas_grid=[16, 8], atlas_tile=64,
        quad_count=sum(len(face) for p in dynamic for material in p['starts'] for face in material),
        mask=mask)


def main():
    for folder in ('assets/hk3gtl/models/scene', 'assets/hk3gtl/textures/effect', 'data/hk3gtl/structures'):
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    records = [export(name, source) for name, source in SOURCES.items()]
    resources = {str(p.relative_to(OUT)).replace('\\', '/'): dict(bytes=p.stat().st_size, sha256=digest(p))
        for p in OUT.rglob('*') if p.is_file() and p.name != 'export-receipt.json'}
    save(OUT / 'export-receipt.json', dict(recorded_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        records=records, resources=resources, source_script_sha256=digest(Path(__file__)),
        installed=False, game_started=False))
    print(json.dumps(dict(records=records, resources=resources), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
