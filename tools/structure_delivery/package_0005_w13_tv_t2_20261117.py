import base64
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
from zipfile import ZipFile

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
from w13_tv_common_20261117 import ROOT, EYE, CONTROLLER, materials
from w13_tv_mountain_20261117 import build_mountain


OUT = ROOT / 'deliveries/0005_W13_侵蚀之律者电视山_T2_20261117'
LOG = ROOT / 'logs/0005-w13-tv-t2-20261117'
T1 = ROOT / 'deliveries/0005_W13_侵蚀之律者电视本体_T1_20261117'
NBT_FILE = 'W13-侵蚀之律者电视山-T2.nbt'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def palette():
    result = materials()
    jar = Path('C:/Users/OWNER/.gradle/caches/modules-2/files-2.1/com.gregtechceu.gtceu/gtceu-1.20.1/1.4.4/ac965814b9aa85fc60e688454d9bf07a1ea3f8f3/gtceu-1.20.1-1.4.4.jar')
    with ZipFile(jar) as archive:
        for color, label in [('cyan', '旧电视青色扫描像素'), ('green', '旧电视绿色字符像素'), ('blue', '旧电视蓝色彩条像素')]:
            entry = f'assets/gtceu/textures/block/lamps/{color}_borderless.png'
            png = archive.read(entry)
            result.append(dict(state=f'gtceu:{color}_borderless_lamp[bloom=true,inverted=true,lit=true,powered=false]', label=label,
                faces={face: 'data:image/png;base64,' + base64.b64encode(png).decode() for face in result[0]['faces']},
                transparent=False, emissive=True, source=dict(kind='gt', archive=str(jar), entry=entry,
                png_sha256=hashlib.sha256(png).hexdigest(), texture_mode='原生像素贴图，无额外染色')))
    return result


def export_nbt(keys, states, size, block_palette):
    w, h, d = size
    header, _ = headers([m['state'] for m in block_palette], (h, d, w), len(keys))
    with gzip.open(OUT / NBT_FILE, 'wb', compresslevel=6) as stream:
        stream.write(header)
        for start in range(0, len(keys), 65536):
            current = keys[start:start + 65536]
            raw = np.tile(np.frombuffer(RECORD, np.uint8), (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current // (w * d), current // w % d
            rows['state'] = states[start:start + 65536].astype(np.int32) - 1
            stream.write(raw.tobytes())
        stream.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    block_palette = palette()
    previous = json.loads((T1 / 'geometry.json').read_text('utf8'))
    old_payload = (T1 / 'data.js').read_text('utf8').split('=', 1)[1].strip().rstrip(';')
    previous_meshes = json.loads(gzip.decompress(base64.b64decode(json.loads(old_payload))))['parts']
    mountain, televisions = build_mountain()
    with np.load(T1 / '原始完整分件.npz') as raw:
        original = [SimpleNamespace(name=c['id'], label=c['label'], metadata=c['metadata'],
            p=raw[c['id'] + '_xyz'], states=raw[c['id'] + '_states']) for c in previous['components']]
    parts = mountain + original
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    values = np.concatenate([p.states for p in parts])
    source_blocks = len(keys)
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(values) - chosen - 1
    values, owners = values[chosen], owners[chosen]
    del chosen
    xyz = np.c_[keys % w, keys // (w * d), keys // w % d].astype(np.int32)
    np.savez_compressed(OUT / '完整整数格模型.npz', xyz=xyz, states=values, origin=low, size=size, owners=owners)
    del xyz
    archive = {}
    for part in parts:
        archive[part.name + '_xyz'], archive[part.name + '_states'] = part.p, part.states
    np.savez_compressed(OUT / '原始完整分件.npz', **archive)
    del archive
    owner_counts = np.bincount(owners, minlength=len(parts))
    packed, components, quads = [], [], previous['surface_quads']
    for index, part in enumerate(parts):
        if index < len(mountain):
            item, count = mesh_part(part, block_palette)
            quads += count
            print(f'电视山表面{index + 1}/{len(mountain)}：{count:,}', flush=True)
        else:
            item = previous_meshes[index - len(mountain)]
            for name in ['starts', 'lengths', 'spans']:
                item[name] += [[[] for _ in range(6)] for _ in range(3)]
        blocks = int(owner_counts[index])
        item.update(blocks=blocks, source_blocks=len(part.p), modelId=part.metadata['group'])
        packed.append(item)
        components.append(dict(id=part.name, label=part.label, modelId=part.metadata['group'], source_blocks=len(part.p), blocks=blocks,
            shared_cells_overwritten=len(part.p) - blocks, bounds=dict(min=part.p.min(0).tolist(), max=part.p.max(0).tolist()), metadata=part.metadata))
    notes = [
        '官方短片42秒全景可见中央巨眼电视下方的连续旧电视山；左右远景独立电视塔与中央堆体分别处理。',
        f'下部由{len(televisions)}台大小不同的厚壳CRT逐格堆叠，形成错层山体与偏心顶部，夹入侧放、朝上和背壳外露的设备。',
        '旧电视保留收窄后壳、圆角厚框、鼓面屏、旋钮、按键、喇叭及散热格栅；黑屏为主，分散显示雪花、白青扫描、字符与彩条。',
        '电视山中央向上嵌入巨眼主机下方，垂挂机匣及粗电缆从堆体缝隙和前侧穿出。原片遮挡的接触点、底部与背侧属于本项目补全。',
        '主眼屏保留粉红眼环与四芒星。山体使用深色灰色机壳，青绿蓝只用于分散的小屏像素，粉色视觉重点保留在主眼屏。',
        '全部实体使用真实整数格与GT、HK3GTL及原版原生像素贴图；没有平滑曲面替代体素。',
        '唯一主控仍在前方电缆检修端子(0,16,472)，朝南；其余全部实体格可自由换成合法通用接口。',
        '网页运行只演示主眼屏亮度与局部故障条，电视山、主壳、机匣和电缆保持原位；NBT保存完整静态实体。',
        'T2为补全电视山的外观待审稿。整体尺寸按完整坐标生成，CEV规模与材料要求另行记录，原A1停用。',
    ]
    views = dict(eye=dict(label='眼屏近景', center=EYE.tolist(), half=[170, 105, 12], direction=[0, 0, 1]),
        shell=dict(label='深壳侧板', center=[420, 525, -5], half=[30, 150, 230], direction=[1, .2, .6]),
        pixels=dict(label='真实像素方块', center=CONTROLLER.tolist(), half=[4, 4, 4], direction=[-.4, .3, 1]),
        controller=dict(label='前端唯一主控', center=CONTROLLER.tolist(), half=[46, 30, 45], direction=[-.3, .55, 1]),
        cables=dict(label='下挂机匣与线缆', center=[0, 180, 20], half=[540, 210, 460], direction=[-.7, .35, 1]),
        mountain=dict(label='电视山全貌', direction=[-.8, .4, 1.35]),
        join=dict(label='主机与电视山衔接', center=[0, 270, 60], half=[470, 180, 370], direction=[-.4, .25, 1]),
        crt=dict(label='旧电视近景', center=televisions[0]['center'], half=[125, 105, 130], direction=[-.4, .25, 1]))
    models = [dict(id=group, label=title, title=title, features=features, views=views) for group, title, features in [
        ('tv', '巨眼电视深机壳', [notes[4], notes[5]]), ('screen', '粉红侵蚀眼屏', [notes[4], notes[7]]),
        ('cables', '垂挂机匣与粗缆', [notes[3], notes[6]]), ('mountain', '错层旧电视山', notes[:4])]]
    data = dict(title='W13 侵蚀之律者：巨眼电视与旧电视山', candidate='T2', nbt_file=NBT_FILE,
        bounds=dict(min=low.tolist(), max=high.tolist()), sizeXYZ=size, total_blocks=len(keys), models=models, views=views,
        design=notes, effects=dict(eye_center=EYE.tolist(), eye_radius=50))
    payload = json.dumps(dict(data=data, materials=block_palette, parts=packed), ensure_ascii=False, separators=(',', ':')).encode()
    (OUT / 'data.js').write_text('window.W13_VOXEL_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(payload, compresslevel=6)).decode()) + ';\n', 'utf8')
    totals = np.bincount(values, minlength=len(block_palette) + 1)
    counts = {m['state']: int(totals[index + 1]) for index, m in enumerate(block_palette)}
    sources = json.loads((T1 / 'sources.json').read_text('utf8'))
    sources.update(modeled_from=['V01', 'V02', 'V03', 'V04', 'V05', 'V06', 'V07', 'V08', 'V09', 'V10', 'V11'],
        correction='V01中央巨眼主机下方的电视堆纳入整体W13；V07至V11用于旧CRT形制与堆叠细节，远景独立塔不整体复制为本体。',
        completion='中央电视山上缘与主机下挂区重叠可见；逐块接触点、底部、背侧与全部尺寸按方块构图补全。')
    geometry = dict(machine='W13', candidate='T2', status='电视山补全外观待审', recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        actual_size_wdh=[w, d, h], bounds=data['bounds'], blocks=len(keys), source_component_voxels=source_blocks,
        shared_component_cells=source_blocks - len(keys), surface_quads=quads, components=components,
        television_count=len(televisions), material_counts=counts, footprint_area=w * d, bounding_box_volume=w * d * h,
        actual_height=h, palette_types=len(block_palette), unique_block_types=int(np.count_nonzero(totals[1:])),
        non_vanilla_percent=100 * sum(n for state, n in counts.items() if not state.startswith('minecraft:')) / len(keys),
        controller=dict(source_xyz=CONTROLLER.tolist(), export_xyz=(CONTROLLER - low).tolist(), facing='south', preview_state='minecraft:redstone_block'),
        screen=previous['screen'], source_notes=notes, runtime=previous['runtime'],
        overlap_policy='完整模型与NBT后写构件优先，T1主壳、机匣、电缆与唯一主控覆盖电视山共享格。网页保留各分件完整表面。',
        scale_comparison=dict(status='CEV材料种类要求待确认', exception_approved=False, w09_w11_exceptions_apply=False),
        shape_selection_approved=True, appearance_approved=False, game_code_modified=False, jar_built=False, installed=False,
        game_started=False, game_verified=False, scores_changed=False)
    baseline = dict(footprint_area=900601, bounding_box_volume=441313404, actual_height=636, blocks=23541415, unique_block_types=58)
    geometry['scale_comparison']['metrics'] = {key: dict(candidate=geometry[key], recorded_lower_tier_max=value, greater=geometry[key] > value) for key, value in baseline.items()}
    for name, value in [('geometry.json', geometry), ('materials.json', block_palette), ('sources.json', sources), ('televisions.json', televisions)]:
        save(OUT / name, value)
    print(f'导出NBT：{len(keys):,}格', flush=True)
    export_nbt(keys, values, size, block_palette)
    scripts = ['w13_tv_common_20261117.py', 'w13_tv_body_20261117.py', 'w13_tv_cables_20261117.py', 'w13_tv_crt_20261117.py', 'w13_tv_mountain_20261117.py', Path(__file__).name]
    for name in scripts:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    save(LOG / 'generation.json', dict(**geometry, input_files={name: digest(ROOT / 'tools/structure_delivery' / name) for name in scripts},
        reused_t1=dict(directory=str(T1), raw_sha256=digest(T1 / '原始完整分件.npz'), mesh_sha256=digest(T1 / 'data.js')),
        nbt=dict(file=NBT_FILE, bytes=(OUT / NBT_FILE).stat().st_size, sha256=digest(OUT / NBT_FILE))))
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), televisions=len(televisions), parts=len(parts), materials=geometry['unique_block_types'], quads=quads), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
