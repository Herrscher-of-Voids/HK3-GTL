# -*- coding: utf-8 -*-
"""修订181：按I34/I35/I36/I38/I39批准版本几何制作独立三态主控，并补齐双语名称。

【变更记录 #1】2026-10-27
新增：五套几何轮廓面板及来源校验；保留先前41套全部像素和原有语言键值。
用途：新控制器与对应完整建筑同源，不能靠编号或换色冒充独立材质。
"""
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
from pathlib import Path
from project_paths import project_path
import shutil
import time

import numpy as np
from PIL import Image, ImageDraw

import build_controller_texture_candidates_20261026 as faces

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
DATA = ROOT / 'src/main/resources/data/hk3gtl'
OUT = ROOT / 'logs/batch09-install-20261027'
MACHINES = {
    'i34': ('i34_imaginary_tree_observation_array', '虚数之树观测阵列', 'Imaginary Tree Observation Array', '开穹悬弦观测仪的悬弦弧架、开敞观测腔与落地结构'),
    'i35': ('i35_imaginary_space_anchoring_array', '虚数空间锚定阵列', 'Imaginary Space Anchoring Array', '越界悬索桥的本维度桥台、桥索与贯穿门框的桥面'),
    'i36': ('i36_honkai_reality_stability_anchor', '崩坏能现实稳定锚', 'Honkai Reality Stabilization Anchor', '双叉谐振稳相井的成对谐振叉与下沉稳相井'),
    'i38': ('i38_imaginary_energy_rectification_hub', '虚数能量整流中枢', 'Imaginary Energy Rectification Hub', '双极脉冲换流站的高低压阀组、母线与分列整流设备'),
    'i39': ('i39_unmanned_cross_boundary_route_relay', '无人跨界航路中继站', 'Unmanned Cross-World Route Relay Station', '偏馈抛物碟面、落地轴座与双轨整备库'),
}
VERSIONS = {'i34':'V2', 'i35':'V3', 'i36':'V1', 'i38':'V1', 'i39':'V1'}


def sha(path):
    digest = hashlib.sha256()
    with project_path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load(path):
    return json.loads(project_path(path).read_text(encoding='utf-8'))


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def points_from_formal(layout, count):
    # 正式布局每个实体一行；只保留连续坐标数组，不展开数百万方块字典。
    points = np.empty((count, 3), dtype=np.float32)
    with layout.open(encoding='utf-8') as stream:
        assert stream.readline().endswith('"blocks":[\n')
        for index in range(count):
            row = json.loads(stream.readline().lstrip(','))
            points[index] = row['pos']
        assert stream.readline().startswith('],"ports":')
        assert not stream.read()
    return points


def add_names():
    records = []
    for language, column in (('zh_cn', 1), ('en_us', 2)):
        path = ASSETS / 'lang' / (language + '.json')
        old = load(path)
        updated = dict(old)
        added = []
        for key, machine in MACHINES.items():
            for name in ('block.hk3gtl.' + machine[0], 'gtceu.industrial_process_' + key):
                value = machine[column]
                if name in updated:
                    assert updated[name] == value, ('既有语言键口径不同，不得覆盖', name, updated[name], value)
                else:
                    updated[name] = value
                    added.append(name)
        assert all(updated[name] == value for name, value in old.items())
        save(path, updated)
        assert all(load(path)[name] == value for name, value in old.items())
        records.append({'language': language, 'added_keys': added,
                        'ensured_names': ['block.hk3gtl.' + machine[0] for machine in MACHINES.values()],
                        'existing_values_unchanged': True, 'sha256': sha(path)})
    return records


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prior = load(ROOT / 'logs/batch08-install-20261027/controller-textures.json')
    old_files = dict(prior['old_controller_sha256'])
    for entry in prior['entries']:
        for texture in entry['textures'].values():
            old_files[texture['target']] = texture['sha256']
    assert len(old_files) == 123
    assert all(sha(path) == digest for path, digest in old_files.items())
    old_fronts = {digest for path, digest in old_files.items() if project_path(path).name == 'overlay_front.png'}
    assert len(old_fronts) == 41
    index = {entry['key']: entry for entry in load(ROOT / 'deliveries/多方块确认归档/当前归档索引.json')['entries']}
    entries, patterns, new_fronts = [], set(), set()
    for key, (machine, name, _, motif) in MACHINES.items():
        row = index[key]
        assert row['approved_version'] == VERSIONS[key]
        assert row.get('external_approval_is_authoritative') or row['source_candidate_approved_field']
        archive = project_path(row['archive'])
        approval = load(row['approval_manifest'])
        assert all(sha(archive / relative) == digest for relative, digest in approval['source_files_sha256'].items())
        meta_path = DATA / 'structures/approved' / (key + '.json')
        # 正式资源逐台提交后即可制作贴图，避免五台全部完成后再次串行等待。
        deadline = time.monotonic() + 3600
        while not meta_path.is_file():
            if time.monotonic() > deadline:
                raise TimeoutError('正式资源未完成：' + key)
            time.sleep(2)
        meta = load(meta_path)
        layout = DATA / 'approved_architecture' / (key + '.json')
        assert project_path(meta['source_snapshot']) == archive
        assert meta['machine'] == 'hk3gtl:' + machine and meta['geometry_nbt_json_per_block_verified']
        assert sha(layout) == meta['sha256']
        assert sha(meta['source_nbt']) == meta['source_nbt_sha256']
        points = points_from_formal(layout, meta['blocks'])
        folder = ASSETS / 'textures/block/overlay' / (key + '_unique_r181')
        folder.mkdir(parents=True, exist_ok=True)
        log_folder = OUT / 'controller-texture-images' / key
        log_folder.mkdir(parents=True, exist_ok=True)
        faces.geometry_image(points, log_folder / 'approved-geometry.png')
        textures = {}
        for state, suffix in faces.STATE_SUFFIX.items():
            image, pattern = faces.candidate_face(points, meta['ports'], meta['controller'], state)
            assert image.size == (64, 64)
            target = folder / ('overlay_front' + suffix + '.png')
            image.save(target)
            assert Image.open(target).size == (64, 64)
            digest = sha(target)
            copy = log_folder / target.name
            shutil.copyfile(target, copy)
            textures[state] = {'target': str(target), 'sha256': digest,
                               'preview': copy.relative_to(OUT).as_posix()}
        assert pattern not in patterns
        patterns.add(pattern)
        digest = textures['idle']['sha256']
        assert digest not in old_fronts and digest not in new_fronts
        new_fronts.add(digest)
        assert len({texture['sha256'] for texture in textures.values()}) == 3
        entries.append({'key': key, 'machine': 'hk3gtl:' + machine, 'name': name, 'motif': motif,
                        'blocks': meta['blocks'], 'size_xyz': meta['size_xyz'], 'controller': meta['controller'],
                        'approved_version': VERSIONS[key], 'approval_manifest': row['approval_manifest'],
                        'approval_manifest_sha256': sha(row['approval_manifest']),
                        'approved_archive': str(archive), 'source_nbt': meta['source_nbt'],
                        'source_nbt_sha256': meta['source_nbt_sha256'], 'formal_layout_sha256': meta['sha256'],
                        'geometry_pattern_sha256': pattern, 'textures': textures,
                        'geometry_preview': (log_folder / 'approved-geometry.png').relative_to(OUT).as_posix()})
        del points
        print(json.dumps({'key': key, 'blocks': meta['blocks'], 'states': 3, 'unique_geometry': True}), flush=True)
    assert len(patterns) == len(new_fronts) == 5
    new_hashes = [texture['sha256'] for entry in entries for texture in entry['textures'].values()]
    assert len(set(new_hashes)) == 15 and not set(new_hashes).intersection(old_files.values())
    assert all(sha(path) == digest for path, digest in old_files.items())
    languages = add_names()
    manifest = {'status': 'generated_and_applied', 'revision': 181,
                'created_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
                'new_sets': 5, 'new_pngs': 15, 'unique_controller_fronts': 46,
                'old_controller_sets_unchanged': 41, 'old_controller_pngs_unchanged': len(old_files),
                'all_15_pngs_unique_and_distinct_from_existing': True,
                'old_controller_sha256': old_files, 'formal_instance_modified': False,
                'visual_method': '沿用批准的64像素金属边框；对应批准版本建筑逐格几何的轮廓、深度棱线、实际接口和主控位置构成独立图案。',
                'languages': languages, 'entries': entries}
    save(OUT / 'controller-textures.json', manifest)
    sheet = Image.new('RGB', (1200, 320), '#101827')
    draw = ImageDraw.Draw(sheet)
    for position, entry in enumerate(entries):
        draw.text((position * 240 + 15, 8), entry['key'].upper(), fill='white')
        face = Image.open(entry['textures']['idle']['target']).convert('RGB')
        sheet.paste(face.resize((224, 224), Image.Resampling.NEAREST), (position * 240 + 8, 40))
    sheet.save(OUT / 'controller-texture-overview.png')
    cards = []
    for entry in entries:
        pictures = ''.join(f'<figure><img src="{texture["preview"]}" alt="{html.escape(entry["name"])}{faces.STATE_CN[state]}"><figcaption>{faces.STATE_CN[state]}</figcaption></figure>'
                           for state, texture in entry['textures'].items())
        cards.append(f'<article><h2>{entry["key"].upper()} · {html.escape(entry["name"])}</h2><p>{html.escape(entry["motif"])}</p><img class="geometry" src="{entry["geometry_preview"]}" alt="对应批准版本建筑的几何示意"><div class="faces">{pictures}</div><p class="meta">{entry["blocks"]:,}块 · {" × ".join(map(str, entry["size_xyz"]))}（X/Y/Z）<br>批准版本 · 既有41套材质原像素保留</p></article>')
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第9批正式主控材质 · I34/I35/I36/I38/I39</title><style>body{margin:0;background:#0d1523;color:#e4edf4;font:16px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1600px;margin:auto;padding:30px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(370px,1fr));gap:20px}article{background:#17243a;border:1px solid #344960;border-radius:10px;padding:18px}h1{font-size:28px}h2{font-size:20px}.geometry{width:100%;aspect-ratio:10/7;object-fit:contain}.faces{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.faces figure{margin:0;text-align:center}.faces img{width:100%;image-rendering:pixelated}.meta{font-size:13px;color:#aac0ce}a{color:#89d9e4}</style><main><h1>第9批正式控制器 · I34/I35/I36/I38/I39</h1><p>五台均采用负责人批准的对应版本建筑轮廓，独立图案含深度棱线与原位接口。共15张64×64三态贴图；现有41套123张控制器贴图保持原哈希。几何示意用于核对图案来源，不替代带材质三维评审。</p><p><a href="controller-textures.json">来源、文件与SHA256收据</a></p><div class="grid">' + ''.join(cards) + '</div></main></html>'
    (OUT / 'controller-textures.html').write_text(page, encoding='utf-8')
    print(json.dumps({'status': manifest['status'], 'new_sets': 5, 'new_pngs': 15,
                      'unique_controller_fronts': 46, 'old_pngs_unchanged': 123}, ensure_ascii=False))


if __name__ == '__main__':
    main()
