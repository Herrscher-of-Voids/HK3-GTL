# -*- coding: utf-8 -*-
"""原字节归档已批准 I09–I13 V6，并只安装建筑结构文件。

变更记录 #1 2026-10-14：读取已有 NBT/Schematic 校验并复制，禁止重新导出。
不修改生产源码、模组、存档、KubeJS、配方或正式机器定义。
"""
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

import nbtlib

from build_i07_calibration_preview import audit_geometry
from redesign69_geometry import ROOT
from structure_size_baseline import SOURCE as SIZE_SOURCE

SOURCE = ROOT / 'deliveries/I09-I13_重设计_V6_20261014'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
LOG = ROOT / 'logs/i09-i13-redesign-v6'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GTL十一周目/minecraft'
APPROVAL = '到 i13我个人觉得可以，就保留现在这个结构吧'
KEYS = ('i09', 'i10', 'i11', 'i12', 'i13')
DEPENDENCIES = (
    'build_i09_i13_redesign_v6.py', 'i09_i10_v6.py', 'i11_i12_v6.py', 'i13_v6.py',
    'i09_i13_v6_common.py', 'build_i07_calibration_preview.py',
    'build_i01_tidal_preview.py', 'build_i03_centrifuge_preview.py',
    'build_redesign69.py', 'redesign69_geometry.py', 'material_resources.py',
    'structure_size_baseline.py', 'package_l1_review89.py', 'l1-review89-recipe.mjs',
    'archive_install_i09_i13_v6.py',
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def state_text(raw):
    props = raw.get('Properties', {})
    suffix = '['+','.join(f'{k}={v}' for k, v in sorted(props.items()))+']' if props else ''
    return str(raw['Name'])+suffix


def decode_varints(values):
    result, value, shift = [], 0, 0
    for raw in values:
        byte = int(raw) & 255
        value |= (byte & 127) << shift
        if byte & 128:
            shift += 7
            assert shift < 35, 'Schematic varint 过长'
        else:
            result.append(value)
            value, shift = 0, 0
    assert shift == 0, 'Schematic varint 被截断'
    return result


def inspect(key):
    folder = SOURCE/key
    nbts, schems = list(folder.glob('*.nbt')), list(folder.glob('*.schem'))
    assert len(nbts) == len(schems) == 1, folder
    nbt_path, schem_path = nbts[0], schems[0]
    structure = nbtlib.load(nbt_path)
    assert int(structure['DataVersion']) == 3465
    size = [int(v) for v in structure['size']]
    palette = [state_text(p) for p in structure['palette']]
    blocks = [{'pos': [int(v) for v in b['pos']], 'state': palette[int(b['state'])]}
              for b in structure['blocks']]
    states = {tuple(b['pos']): b['state'] for b in blocks}
    assert len(states) == len(blocks), 'NBT 重复方块坐标'
    assert not structure.get('entities'), '结构不得包含实体标签'
    record = json.loads((folder/'设计与检查.json').read_text(encoding='utf-8'))
    metadata = record['data']
    assert metadata['key'] == key and metadata['size'] == size
    blueprint = json.loads((folder/'blueprint.json').read_text(encoding='utf-8'))
    assert states == {tuple(b['pos']): b['state'] for b in blueprint['blocks']}
    geometry = audit_geometry({**metadata, 'blocks': blocks})
    assert states[tuple(metadata['controller'])] == 'minecraft:diamond_block'
    # 部分 V6 结构把中央核心以多块钻石块表达；控制器坐标必须仍是钻石块，数量按原始字节保留。
    assert sum(s == 'minecraft:diamond_block' for s in states.values()) >= 1
    assert len(metadata['ports']) == 6
    complete = json.loads((folder/'complete.json').read_text(encoding='utf-8'))
    assert complete['sha256_nbt'] == sha(nbt_path)
    assert record['audit']['hashes']['nbt'] == sha(nbt_path)
    assert record['audit']['hashes']['schem'] == sha(schem_path)

    schematic = nbtlib.load(schem_path)
    assert schematic.root_name == 'Schematic'
    assert int(schematic['Version']) == 2 and int(schematic['DataVersion']) == 3465
    assert [int(schematic[k]) for k in ('Width', 'Height', 'Length')] == size
    assert list(map(int, schematic['Offset'])) == [0, 0, 0]
    spalette = {str(s): int(i) for s, i in schematic['Palette'].items()}
    assert spalette['minecraft:air'] == 0
    assert int(schematic['PaletteMax']) == len(spalette)
    assert set(spalette.values()) == set(range(len(spalette)))
    reverse = {i: s for s, i in spalette.items()}
    values = decode_varints(schematic['BlockData'])
    w, h, d = size
    assert len(values) == w*h*d
    decoded = {}
    for index, value in enumerate(values):
        assert value in reverse
        if value:
            pos = (index % w, index // (w*d), index // w % d)
            decoded[pos] = reverse[value]
    assert decoded == states, 'Schematic 与确认 NBT 逐格不一致'
    return {'id': key.upper(), 'title': metadata['title'], 'confirmed_version': 'V6-20261014',
            'confirmation_status': 'approved', 'approval_quote': APPROVAL,
            'size_xyz': size, 'size_baseline': geometry, 'blocks': len(blocks),
            'controller': metadata['controller'], 'ports': metadata['ports'],
            'nbt_name': nbt_path.name, 'schem_name': schem_path.name,
            'nbt_sha256': sha(nbt_path), 'schem_sha256': sha(schem_path),
            'checks': ['原始 NBT 可解析', '原始 Sponge v2 可解析', 'NBT/蓝图/Schematic 逐格一致',
                       '实体尺寸与总表逐轴下限核对', '六面连通', '主控标记、六接口与声明通道核对'],
            'source': str(folder)}


def copy_verified(source, target):
    assert source.is_file() and not target.exists(), target
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    assert sha(source) == sha(target), target


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d_%H%M%S_%f')
    # 先验证全部批准文件及目标实例，之后才开始复制。
    entries = [inspect(key) for key in KEYS]
    research = json.loads((LOG/'reference-study.json').read_text(encoding='utf-8'))
    instance_identity = []
    for jar in research['已核对JAR']:
        path = INSTANCE/'mods'/jar['file']
        assert path.is_file() and sha(path) == jar['sha256'], path
        instance_identity.append({'file': str(path), 'sha256': sha(path)})
    source_hashes = {p.relative_to(SOURCE).as_posix(): sha(p)
                     for p in sorted(SOURCE.rglob('*')) if p.is_file()}
    numbers = [int(match[1]) for p in ARCHIVES.glob('*')
               if p.is_dir() and (match := re.search(r'_batch-(\d+)', p.name))]
    batch = f'batch-{max(numbers, default=0)+1:02d}'
    snapshot = ARCHIVES/f'{stamp}_{batch}_I09-I13_V6'
    snapshot.mkdir(parents=True, exist_ok=False)
    copied_source = snapshot/'confirmed_v6'
    shutil.copytree(SOURCE, copied_source)
    for rel, expected in source_hashes.items():
        assert sha(copied_source/rel) == expected

    dependencies = snapshot/'generator_dependencies'
    dependencies.mkdir()
    for name in DEPENDENCIES:
        copy_verified(ROOT/'tools/structure_delivery'/name, dependencies/name)
    for path in (SIZE_SOURCE, ROOT/'rule/当前多方块设计规则.md', ROOT/'rule/巨构提示词.txt'):
        copy_verified(path, dependencies/path.name)
    evidence = snapshot/'evidence'
    evidence.mkdir()
    for name in ('reference-study.json', 'browser-review.json', 'final-verification.json'):
        path = LOG/name
        if path.exists():
            copy_verified(path, evidence/name)

    # 仅写 config 下的唯一批次路径和唯一码文件名，已有玩家文件不会覆盖。
    schem_root = INSTANCE/'config/worldedit/schematics'
    nbt_root = INSTANCE/'config/hk3gtl/approved_structures'/snapshot.name
    assert not nbt_root.exists(), nbt_root
    nbt_root.mkdir(parents=True, exist_ok=False)
    installed = []
    for key, entry in zip(KEYS, entries):
        entry['archive'] = str(copied_source/key)
        schem_target = schem_root/f'hk3gtl_{key}_v6_{stamp}.schem'
        nbt_target = nbt_root/key/entry['nbt_name']
        copy_verified(copied_source/key/entry['schem_name'], schem_target)
        copy_verified(copied_source/key/entry['nbt_name'], nbt_target)
        for kind, target, expected in (('schem', schem_target, entry['schem_sha256']),
                                      ('nbt', nbt_target, entry['nbt_sha256'])):
            assert sha(target) == expected
            installed.append({'id': key.upper(), 'kind': kind, 'path': str(target), 'sha256': expected})
        entry['installed_schem'] = str(schem_target)
        entry['installed_nbt'] = str(nbt_target)
    manifest = {'batch': batch, 'snapshot': snapshot.name, 'created_at': now.isoformat(),
                'timezone': 'Asia/Hong_Kong', 'approval_quote': APPROVAL,
                'confirmation_scope': 'I09–I13 当前 V6 的建筑外观与结构文件；五台一起保留',
                'status': 'approved_archived_structure_files_installed',
                'source_delivery': str(SOURCE), 'archive': str(snapshot),
                'viewer': str(copied_source/'index.html'), 'instance': str(INSTANCE),
                'instance_identity': instance_identity, 'entries': entries,
                'preserved_source_file_sha256': source_hashes,
                'generator_dependencies_sha256': {p.name: sha(p) for p in sorted(dependencies.iterdir())},
                'installed_files': installed,
                'copy_rule': '复制原始压缩字节并核对 SHA256；未调用生成器或重新压缩 NBT/Schematic。',
                'source_status_note': '原交付内部待确认字样按原字节保存；本清单是该版本已获批准的状态依据。',
                'integration_scope': '只安装 WorldEdit 建筑 schem，以及 HK3GTL config 归档 NBT 和清单。',
                'formal_pattern_integrated': False, 'recipe_or_machine_logic_changed': False,
                'game_verified': False, 'not_verified': ['正式 Pattern 与接口能力映射', 'Minecraft 成型与运行',
                                                       '生存材料完整可达性'],
                'unchanged_scope': ['生产源码', 'mods', '玩家存档/world', 'KubeJS', '配方和机器定义', 'V6 源交付']}
    manifest_path = snapshot/'确认与校验清单.json'
    json_write(manifest_path, manifest)
    copy_verified(manifest_path, nbt_root/'确认与校验清单.json')
    copy_verified(copied_source/'manifest.json', nbt_root/'source_manifest.json')
    # 完整归档保留共享查看器、纹理载荷、依赖与原交付文件。
    bundle = snapshot.with_suffix('.zip')
    archived_hashes = {p.relative_to(snapshot).as_posix(): sha(p)
                       for p in sorted(snapshot.rglob('*')) if p.is_file()}
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel in archived_hashes:
            archive.write(snapshot/rel, rel)
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(archived_hashes)
        for rel, expected in archived_hashes.items():
            assert hashlib.sha256(archive.read(rel)).hexdigest() == expected, rel
    assert source_hashes == {p.relative_to(SOURCE).as_posix(): sha(p)
                             for p in sorted(SOURCE.rglob('*')) if p.is_file()}
    result = {'batch': batch, 'snapshot': str(snapshot), 'zip': str(bundle), 'zip_sha256': sha(bundle),
              'approval_manifest': str(manifest_path), 'viewer': str(copied_source/'index.html'),
              'instance': str(INSTANCE), 'instance_nbt_directory': str(nbt_root),
              'structures': 5, 'installed_structure_files': 10, 'installed_manifest_files': 2,
              'installed_files': installed, 'archive_files': len(archived_hashes),
              'all_hashes_verified': True, 'source_delivery_unchanged': True,
              'formal_pattern_integrated': False, 'game_verified': False}
    json_write(LOG/f'approval-{stamp}.json', {'time': now.isoformat(), 'approval_quote': APPROVAL,
                                           'approved_ids': [k.upper() for k in KEYS], 'result': result})
    json_write(LOG/f'install-{stamp}.json', result)
    # 新批准索引独立命名，历史当前索引与历史批次记录均保留。
    json_write(ARCHIVES/f'{stamp}_{batch}_批次索引.json', result)
    discussion = ROOT/'doc/HK3GTL-内测5/讨论记录'/f'{now.strftime("%Y-%m-%d_%H-%M-%S")}_I09-I13_V6确认归档与建筑文件安装.html'
    assert not discussion.exists(), discussion
    discussion.write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>I09–I13 V6 确认归档与建筑文件安装</title></head><body>
<h1>I09–I13 V6 确认归档与建筑文件安装</h1><p>{now.isoformat()}，Asia/Hong_Kong。</p>
<p>用户已确认原话：「{APPROVAL}」。适用于本轮 I09–I13 V6 五台当前结构，覆盖先前待外观确认状态；历史候选文件与讨论保留。</p>
<p>已实施：五台原始 NBT/Schematic 保压缩字节归档至 {snapshot}；共享查看器、生成器依赖与批准/哈希清单一同保存，ZIP 为 {bundle}。</p>
<p>已实施：仅将五个唯一命名 schem 复制到 GTL十一周目 config/worldedit/schematics；NBT 与清单复制到 {nbt_root}。</p>
<p>已验证：三模组 JAR 身份、原始文件回读与逐格一致、总表尺寸下限、六面连通、主控与接口位置、声明通道、归档/ZIP/实例逐文件 SHA256；V6 源交付保持原字节。</p>
<p>本次只安装建筑结构文件，未接入正式 Pattern、配方或机器逻辑，未进行游戏成型、运行或生存材料可达性验收。生产源码、mods、玩家存档与 KubeJS 均未修改。</p>
<p>依据：rule/当前多方块设计规则.md、rule/巨构提示词.txt；详情见 {manifest_path}。下一步由用户实际测试建筑，正式机器功能另行验收。</p>
</body></html>''', encoding='utf-8')
    result['discussion'] = str(discussion)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
