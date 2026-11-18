import base64
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import struct
import zipfile

import numpy as np
import package_0005_w05_author_blueprint_20261115 as shared
import package_0005_w06_author_blueprint_20261115 as author

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W06_作者蓝图原案_20261115'
OUT = ROOT / 'deliveries/0005_W06_GTL现有方块保色_V1_20261115'
LOG = ROOT / 'logs/0005-w06-existing-blocks-v1-20261115'
RESOURCE = ROOT / 'src/main/resources/data/hk3gtl/structures/w06_candidate.bin.gz'
METADATA = RESOURCE.with_name('w06_approved.json')
MACHINE = 'hk3gtl:w06_cryogenic_condensed_factory'
RUN = struct.Struct('>iiiHi')
GTL_JAR = Path(r'C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GregTech Leisure-增强版\minecraft\mods\gtlcore-1.2.3.3-fix4.jar')
MINECRAFT_JAR = Path(r'C:\Users\OWNER\AppData\Roaming\PrismLauncher\libraries\net\minecraft\client\1.20.1-20230612.114412\client-1.20.1-20230612.114412-extra.jar')

MATERIALS = [
    dict(label='永霜银白装甲 · gtlcore:iridium_casing', block_state='gtlcore:iridium_casing',
         texture='materials/01_iridium_casing.png', archive='gtl', entry='assets/gtlcore/textures/block/casings/iridium_casing.png',
         transparent=False, opacity=1, emissive='#000000', emissiveIntensity=0),
    dict(label='深渊暗蓝排热层 · gtlcore:dimensionally_transcendent_casing', block_state='gtlcore:dimensionally_transcendent_casing',
         texture='materials/02_dimensionally_transcendent_casing.png', archive='gtl', entry='assets/gtlcore/textures/block/casings/dimensionally_transcendent_casing.png',
         transparent=False, opacity=1, emissive='#030b16', emissiveIntensity=0.04),
    dict(label='冰晶棱镜 · minecraft:light_blue_stained_glass', block_state='minecraft:light_blue_stained_glass',
         texture='materials/03_light_blue_stained_glass.png', archive='minecraft', entry='assets/minecraft/textures/block/light_blue_stained_glass.png',
         transparent=True, opacity=0.72, emissive='#000000', emissiveIntensity=0),
    dict(label='金色律者饰面 · gtlcore:blaze_blast_furnace_casing', block_state='gtlcore:blaze_blast_furnace_casing',
         texture='materials/04_blaze_blast_furnace_casing.png', archive='gtl', entry='assets/gtlcore/textures/block/blaze_blast_furnace_casing.png',
         transparent=False, opacity=1, emissive='#281b08', emissiveIntensity=0.05),
    dict(label='超导线圈 · gtlcore:lafium_mechanical_casing', block_state='gtlcore:lafium_mechanical_casing',
         texture='materials/05_lafium_mechanical_casing.png', archive='gtl', entry='assets/gtlcore/textures/block/casings/lafium_mechanical_casing.png',
         transparent=False, opacity=1, emissive='#070a1d', emissiveIntensity=0.04),
    dict(label='黑色律者核心 · gtlcore:hyper_mechanical_casing', block_state='gtlcore:hyper_mechanical_casing',
         texture='materials/06_hyper_mechanical_casing.png', archive='gtl', entry='assets/gtlcore/textures/block/casings/hyper_mechanical_casing.png',
         transparent=False, opacity=1, emissive='#160e04', emissiveIntensity=0.03),
    dict(label='极光能量格栅 · minecraft:cyan_stained_glass', block_state='minecraft:cyan_stained_glass',
         texture='materials/07_cyan_stained_glass.png', archive='minecraft', entry='assets/minecraft/textures/block/cyan_stained_glass.png',
         transparent=True, opacity=0.72, emissive='#000000', emissiveIntensity=0),
    dict(label='零点能池 · minecraft:sea_lantern', block_state='minecraft:sea_lantern',
         texture='materials/08_sea_lantern.png', archive='minecraft', entry='assets/minecraft/textures/block/sea_lantern.png',
         transparent=False, opacity=1, emissive='#64cedb', emissiveIntensity=0.24),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def copy_textures():
    archives = {'gtl': GTL_JAR, 'minecraft': MINECRAFT_JAR}
    (OUT / 'materials').mkdir(parents=True, exist_ok=True)
    for material in MATERIALS:
        with zipfile.ZipFile(archives[material['archive']]) as archive:
            (OUT / material['texture']).write_bytes(archive.read(material['entry']))
    return {key: digest(path) for key, path in archives.items()}


def write_runtime(source_manifest):
    low = np.array(source_manifest['occupied_bounds_xyz']['min'])
    size = np.array(source_manifest['occupied_bounds_xyz']['max']) - low + 1
    w, h, d = map(int, size)
    cube = np.zeros(w * h * d, np.uint8)
    slots = np.arange(9, dtype=np.uint8)
    with np.load(SOURCE / '原始构件数据.npz') as archive:
        for part in source_manifest['components']:
            p = archive[part['id'] + '_xyz'] - low
            linear = (p[:, 0] * h + p[:, 1]) * d + p[:, 2]
            cube[linear] = slots[archive[part['id'] + '_materials']]

    source_controller = np.array([401, 45, 700])
    controller = source_controller - low
    cx, cy, cz = map(int, controller)
    controller_linear = (cx * h + cy) * d + cz
    previous_marker = MATERIALS[int(cube[controller_linear]) - 1]['block_state']
    palette = [material['block_state'] for material in MATERIALS]
    palette.append(MACHINE + '[facing=north]')
    cube[controller_linear] = len(palette)
    counts = np.bincount(cube, minlength=len(palette) + 1)[1:]
    block_count = int(counts.sum())
    entity_id = MACHINE.encode('utf8')
    entity = b'\x0a\x00\x00\x08\x00\x02id' + struct.pack('>H', len(entity_id)) + entity_id + b'\x00'
    RESOURCE.parent.mkdir(parents=True, exist_ok=True)
    temporary = RESOURCE.with_suffix('.gz.pending')
    runs = 0
    with temporary.open('wb') as output:
        with gzip.GzipFile(filename='', fileobj=output, mode='wb', compresslevel=9, mtime=0) as stream:
            stream.write(struct.pack('>9iH', 0x484b3350, 2, w, h, d, cx, cy, cz, block_count, len(palette)))
            for state in palette:
                encoded = state.encode('utf8')
                stream.write(struct.pack('>H', len(encoded)) + encoded)
            positions = np.flatnonzero(cube)
            states = cube[positions] - 1
            delta = np.diff(positions)
            changes = np.flatnonzero((states[1:] != states[:-1]) |
                (delta != np.r_[delta[:1], delta[:-1]])) + 1
            for start, end in zip(np.r_[0, changes], np.r_[changes, len(positions)]):
                count = int(end - start)
                state = int(states[start])
                step = int(positions[start + 1] - positions[start]) if count > 1 else 0
                tag = entity if state == len(palette) - 1 else b''
                stream.write(RUN.pack(int(positions[start]), step, count, state, len(tag)) + tag)
                runs += 1
    temporary.replace(RESOURCE)
    material_counts = {state: int(count) for state, count in zip(palette, counts) if count}
    metadata = dict(id='W06', version='0005-W06-A1', controller=MACHINE,
        blueprint='hk3gtl:structures/w06_candidate.bin.gz', conversation='0005',
        conversation_id=source_manifest['conversation_id'], appearance_approved=True,
        approval_basis='负责人：“可以就这台吧，接入吧”；随后要求使用GTL模组包已有方块并尽量保持配色。',
        source='deliveries/0005_W06_作者蓝图原案_20261115',
        source_manifest_sha256=digest(SOURCE / 'manifest.json'),
        source_npz_sha256=digest(SOURCE / '原始构件数据.npz'),
        source_blueprint_sha256=source_manifest['source_sha256'],
        size_xyz=[w, h, d], size_wdh=[w, d, h], source_origin_xyz=low.tolist(),
        controller_source_xyz=source_controller.tolist(), controller_xyz=controller.tolist(),
        source_facing='north', block_count=block_count, full_geometry=True,
        source_component_voxels=source_manifest['source_component_voxels'],
        unique_source_voxels=source_manifest['unique_occupied_voxels'],
        overlap_extra_memberships=source_manifest['overlap_extra_memberships'],
        overlap_material_policy='按原案构件顺序后者覆盖前者；只处理体素重合，不改任何构件坐标。',
        production_recipe='hk3gtl:wonder_cryogenic_condensation_matrix', target_voltage='WSV', research='RN-CCF',
        interface_policy='沿用现有自由通用接口规则；蓝图不预装固定仓室。',
        materials=MATERIALS, material_counts=material_counts,
        controller_previous_state=previous_marker, controller_state=palette[-1],
        controller_replacements=1,
        runtime_format='HK3P/2；完整稀疏方块坐标与等差游程；主控实体NBT。',
        rle_record_count=runs, blueprint_sha256=digest(RESOURCE),
        overworld_vertical_span=384, overworld_height_compatible=h <= 384,
        game_verified=False)
    save(METADATA, metadata)
    return metadata


def write_preview(source_manifest, jar_hashes):
    source_js = (SOURCE / 'data.js').read_text('utf8')
    packed = json.loads(source_js.split('=', 1)[1].strip().removesuffix(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(packed)))
    payload['data']['material_scope'] = '使用增强版3.9现有方块纹理；没有注册新方块或材质。'
    render_materials = []
    for material in MATERIALS:
        item = dict(material)
        item['texture'] = 'data:image/png;base64,' + base64.b64encode((OUT / material['texture']).read_bytes()).decode()
        render_materials.append(item)
    payload['materials'] = render_materials
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6, mtime=0)).decode()
    (OUT / 'data.js').write_text('window.W06_AUTHOR_PAYLOAD=' + json.dumps(encoded) + ';', 'utf8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', OUT / 'viewer.bundle.js')
    shutil.copy2(SOURCE / '原文.md', OUT / '原文.md')
    shutil.copy2(SOURCE / '构件交叠记录.json', OUT / '构件交叠记录.json')
    author.OUT = OUT
    author.write_pages(payload['data'], payload['parts'], source_manifest,
        {'source_conflicts': payload['data']['interpretations']},
        payload['data']['interpretations'], MATERIALS)
    replacements = {
        '8种专用预览材质': '8类整合包现有方块',
        '八种专用预览材质': 'GTL整合包现有方块',
        '此为网页体素预览，不代表已注册八种游戏方块。': '预览与运行蓝图均映射到增强版3.9现有方块；动态效果仍仅在网页演示。',
        '八种专用材质是本预览的纹理，不是已注册的 Minecraft 方块。': '预览材质来自增强版3.9现有方块；配色接近原案，局部纹样和透光效果依原生方块而变化。',
        '仅网页贴图；没有注册或新增游戏方块。': '使用增强版3.9现有方块；本候选不新增方块或材质。',
        '不修改A3候选、游戏源码或运行蓝图。': '几何沿用作者原案；A3候选保持独立。',
    }
    for name in ('index.html', '三维评审.html'):
        path = OUT / name
        page = path.read_text('utf8')
        for old, new in replacements.items():
            page = page.replace(old, new)
        path.write_text(page, 'utf8')
    manifest = dict(source_manifest)
    manifest.update(candidate='W06作者原案 · GTL现有方块保色映射V1', appearance_approved=True,
        source_preview='deliveries/0005_W06_作者蓝图原案_20261115',
        geometry_unchanged=True, new_game_blocks_registered=0, new_game_textures_added=0,
        material_map=MATERIALS, source_texture_archives=jar_hashes,
        runtime_blueprint='src/main/resources/data/hk3gtl/structures/w06_candidate.bin.gz',
        runtime_blueprint_modified=True, game_code_modified=True, jar_built=False,
        installed=False, game_started=False, game_verified=False, acceptance_score_changed=False)
    save(OUT / 'manifest.json', manifest)
    save(OUT / '材料清单.json', dict(materials=MATERIALS,
        source_material_counts=source_manifest['material_counts'],
        new_game_blocks_registered=0, new_game_textures_added=0,
        note='8项均复用整合包或Minecraft原有方块；不新增模组方块、注册ID或贴图。'))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    source_manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    assert source_manifest['size_wdh'] == [817, 761, 423]
    assert source_manifest['occupied_bounds_xyz']['min'] == [-7, -40, -19]
    assert source_manifest['occupied_bounds_xyz']['max'] == [809, 382, 741]
    jar_hashes = copy_textures()
    metadata = write_runtime(source_manifest)
    write_preview(source_manifest, jar_hashes)
    save(LOG / 'blueprint-export.json', dict(recorded_at=datetime.now().astimezone().isoformat(timespec='seconds'), **metadata,
        destination=str(RESOURCE.relative_to(ROOT)).replace('\\', '/'),
        destination_bytes=RESOURCE.stat().st_size, metadata_sha256=digest(METADATA),
        exporter_sha256=digest(Path(__file__)), jar_built=False, installed=False,
        game_started=False, automated_tests_run=False))
    shutil.copy2(Path(__file__), OUT / '生成脚本.py')
    shutil.copy2(ROOT / 'tools/structure_delivery/capture_0005_w06_existing_blocks_20261115.mjs', OUT / '生成截图.mjs')
    print(json.dumps(dict(preview=str(OUT / '三维评审.html'), size_wdh=metadata['size_wdh'],
        controller_xyz=metadata['controller_xyz'], blocks=metadata['block_count'],
        palette=metadata['material_counts'], runs=metadata['rle_record_count'],
        blueprint_bytes=RESOURCE.stat().st_size), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
