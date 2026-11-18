# -*- coding: utf-8 -*-
"""修订180：按I29–I33批准V1几何制作独立三态主控，并补齐双语名称。

【变更记录 #1】2026-10-27
新增：五套几何轮廓面板及来源校验；保留先前36套全部像素和原有语言键值。
用途：新控制器与对应完整建筑同源，不能靠编号或换色冒充独立材质。
"""
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
from pathlib import Path
from project_paths import project_path
import shutil

import numpy as np
from PIL import Image, ImageDraw

import build_controller_texture_candidates_20261026 as faces

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
DATA = ROOT / 'src/main/resources/data/hk3gtl'
OUT = ROOT / 'logs/batch08-install-20261027'
MACHINES = {
    'i29': ('i29_simulated_world_bubble_synthesizer', '模拟世界泡构筑机', 'Simulated World Bubble Constructor', '双瓣造界工厂的对称工艺翼、中央造界腔和完整物料回路'),
    'i30': ('i30_simulated_world_bubble_stabilizer', '模拟世界泡稳定控制器', 'Simulated World Bubble Stability Controller', '六脊稳界深井、环状约束梁与向下收束的核心'),
    'i31': ('i31_simulated_world_bubble_termination_reclaimer', '模拟世界泡终止回收机', 'Simulated World Bubble Termination and Recovery Machine', '逆相沙漏回收庭的上下收束、腰部环梁与外围回收庭'),
    'i32': ('i32_relic_technology_reverse_laboratory', '遗留技术逆向实验室', 'Legacy Technology Reverse Engineering Laboratory', '遗构剖析院的中央剖析设备及分区研究建筑'),
    'i33': ('i33_imitation_divine_key_assembly_center', '仿制神之键装配中心', 'Imitation Divine Key Assembly Center', '圣匣铸键工坊的装配匣体、承重构架和分列工艺翼'),
}


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
    prior = load(ROOT / 'logs/controller-texture-candidates-20261026/application-r178.json')
    old_files = {row['target']: row['sha256'] for row in prior['copied_files']}
    old_files.update(prior['preserved_sha256'])
    assert len(old_files) == 108
    assert all(sha(path) == digest for path, digest in old_files.items())
    old_fronts = set(prior['front_sha256'].values())
    assert len(old_fronts) == 36
    index = {entry['key']: entry for entry in load(ROOT / 'deliveries/多方块确认归档/当前归档索引.json')['entries']}
    entries, patterns, new_fronts = [], set(), set()
    for key, (machine, name, _, motif) in MACHINES.items():
        row = index[key]
        assert row['approved_version'] == 'V1'
        archive = project_path(row['archive'])
        approval = load(row['approval_manifest'])
        assert all(sha(archive / relative) == digest for relative, digest in approval['source_files_sha256'].items())
        meta_path = DATA / 'structures/approved' / (key + '.json')
        meta = load(meta_path)
        layout = DATA / 'approved_architecture' / (key + '.json')
        assert project_path(meta['source_snapshot']) == archive
        assert meta['machine'] == 'hk3gtl:' + machine and meta['geometry_nbt_json_per_block_verified']
        assert sha(layout) == meta['sha256']
        assert sha(meta['source_nbt']) == meta['source_nbt_sha256']
        points = points_from_formal(layout, meta['blocks'])
        folder = ASSETS / 'textures/block/overlay' / (key + '_unique_r180')
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
                        'approved_version': 'V1', 'approval_manifest': row['approval_manifest'],
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
    manifest = {'status': 'generated_and_applied', 'revision': 180,
                'created_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
                'new_sets': 5, 'new_pngs': 15, 'unique_controller_fronts': 41,
                'old_controller_sets_unchanged': 36, 'old_controller_pngs_unchanged': len(old_files),
                'all_15_pngs_unique_and_distinct_from_existing': True,
                'old_controller_sha256': old_files, 'formal_instance_modified': False,
                'visual_method': '沿用批准的64像素金属边框；对应批准V1建筑逐格几何的轮廓、深度棱线、实际接口和主控位置构成独立图案。',
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
        cards.append(f'<article><h2>{entry["key"].upper()} · {html.escape(entry["name"])}</h2><p>{html.escape(entry["motif"])}</p><img class="geometry" src="{entry["geometry_preview"]}" alt="对应批准V1建筑的几何示意"><div class="faces">{pictures}</div><p class="meta">{entry["blocks"]:,}块 · {" × ".join(map(str, entry["size_xyz"]))}（X/Y/Z）<br>批准V1 · 既有36套材质原像素保留</p></article>')
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第8批正式主控材质 · I29–I33</title><style>body{margin:0;background:#0d1523;color:#e4edf4;font:16px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1600px;margin:auto;padding:30px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(370px,1fr));gap:20px}article{background:#17243a;border:1px solid #344960;border-radius:10px;padding:18px}h1{font-size:28px}h2{font-size:20px}.geometry{width:100%;aspect-ratio:10/7;object-fit:contain}.faces{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.faces figure{margin:0;text-align:center}.faces img{width:100%;image-rendering:pixelated}.meta{font-size:13px;color:#aac0ce}a{color:#89d9e4}</style><main><h1>第8批正式控制器 · I29–I33</h1><p>五台均采用负责人批准的V1建筑轮廓，独立图案含深度棱线与原位接口。共15张64×64三态贴图；现有36套108张控制器贴图保持原哈希。几何示意用于核对图案来源，不替代带材质三维评审。</p><p><a href="controller-textures.json">来源、文件与SHA256收据</a></p><div class="grid">' + ''.join(cards) + '</div></main></html>'
    (OUT / 'controller-textures.html').write_text(page, encoding='utf-8')
    print(json.dumps({'status': manifest['status'], 'new_sets': 5, 'new_pngs': 15,
                      'unique_controller_fronts': 41, 'old_pngs_unchanged': 108}, ensure_ascii=False))


if __name__ == '__main__':
    main()
