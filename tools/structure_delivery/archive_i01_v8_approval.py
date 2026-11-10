# -*- coding: utf-8 -*-
"""按用户批准原字节归档 I01 V8 四阶，不部署游戏文件。

变更记录 #1 2026-10-14：保留完整交付、生成器和核验证据；四阶段算一台机器。
"""
import base64
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

import nbtlib

from build_i07_calibration_preview import audit_geometry
from redesign69_geometry import ROOT

SOURCE = ROOT / 'deliveries/I01_采集塔四阶_正交重设计_V8_20261014'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
LOG = ROOT / 'logs/i01-orthogonal-v8'
APPROVAL = '现在这几个可以'
KEYS = tuple(f'i01-{n}' for n in range(1, 5))
BUNDLE = 'I01_V8_四阶结构与预览.zip'
EXPECTED_BYTES = 2269669
EXPECTED_SHA = '573c9d4294d2ab7db01e865a216222fc4a84cb0a95ff25b4967721a6c79bd4ac'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def state_text(raw):
    props = raw.get('Properties', {})
    suffix = '[' + ','.join(f'{k}={v}' for k, v in sorted(props.items())) + ']' if props else ''
    return str(raw['Name']) + suffix


def decode_varints(raw):
    values, value, shift = [], 0, 0
    for part in raw:
        byte = int(part) & 255
        value |= (byte & 127) << shift
        if byte & 128:
            shift += 7
            assert shift <= 28, 'Schematic varint 过长'
        else:
            values.append(value)
            value, shift = 0, 0
    assert shift == 0, 'Schematic varint 被截断'
    return values


def inspect(entry, browser):
    key, name = entry['key'], entry['name']
    folder = SOURCE / key
    nbt_path, schem_path = (folder / (name + suffix) for suffix in ('.nbt', '.schem'))
    root = nbtlib.load(nbt_path)
    assert int(root['DataVersion']) == 3465 and not root.get('entities')
    size = list(map(int, root['size']))
    palette = [state_text(raw) for raw in root['palette']]
    blocks = [{'pos': list(map(int, raw['pos'])), 'state': palette[int(raw['state'])]}
              for raw in root['blocks']]
    states = {tuple(block['pos']): block['state'] for block in blocks}
    assert len(states) == len(blocks), 'NBT 坐标重复'
    record = json.loads((folder / '设计与检查.json').read_text(encoding='utf-8'))
    data, audit = record['data'], record['audit']
    blueprint = json.loads((folder / 'blueprint.json').read_text(encoding='utf-8'))
    assert size == entry['size'] == data['size'] == blueprint['size']
    assert states == {tuple(block['pos']): block['state'] for block in blueprint['blocks']}
    controller = tuple(data['controller'])
    assert controller == tuple(blueprint['controller']) == tuple(data['paste_anchor'])
    assert states[controller] == 'minecraft:diamond_block'
    assert sum(value == 'minecraft:diamond_block' for value in states.values()) == 1
    assert sum(value == 'hk3gtl:industrial_port_casing' for value in states.values()) == 6
    geometry = audit_geometry({**data, 'blocks': blocks})
    assert geometry['passed']
    assert audit['hashes'] == {'nbt': sha(nbt_path), 'schem': sha(schem_path)}
    assert entry['sha256_nbt'] == sha(nbt_path)
    complete = json.loads((folder / 'complete.json').read_text(encoding='utf-8'))
    assert complete['sha256_nbt'] == sha(nbt_path)
    encoded = json.loads((folder / 'data.js').read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    assert payload['data'] == data and payload['audit'] == audit
    assert sum(map(len, payload['groups'])) == len(blocks)
    assert all(material['complete_cube'] for material in payload['materials'])

    sponge = nbtlib.load(schem_path)
    assert sponge.root_name == 'Schematic'
    assert int(sponge['Version']) == 2 and int(sponge['DataVersion']) == 3465
    assert [int(sponge[k]) for k in ('Width', 'Height', 'Length')] == size
    offset = tuple(map(int, sponge['Offset']))
    assert offset == tuple(-part for part in controller), '主控粘贴锚点与偏移不一致'
    palette = {str(state): int(index) for state, index in sponge['Palette'].items()}
    assert palette['minecraft:air'] == 0
    assert int(sponge['PaletteMax']) == len(palette)
    assert set(palette.values()) == set(range(len(palette)))
    reverse = {index: state for state, index in palette.items()}
    indices = decode_varints(sponge['BlockData'])
    w, h, d = size
    assert len(indices) == w * h * d
    decoded = {}
    for index, value in enumerate(indices):
        assert value in reverse
        if value:
            decoded[index % w, index // (w * d), index // w % d] = reverse[value]
    assert decoded == states, 'NBT/Sponge 逐格不同'
    evidence = browser['machines'][key]
    assert evidence['sha256_nbt'] == sha(nbt_path)
    assert all(evidence[item] for item in ('loaded', 'rotation_checked', 'section_checked', 'panel_checked'))
    global_states = {tuple(pos[i] + offset[i] for i in range(3)): value
                     for pos, value in states.items()}
    return {'id': key.upper(), 'title': data['title'], 'size_xyz': size, 'blocks': len(blocks),
            'controller_local': list(controller), 'schematic_offset': list(offset),
            'ports': data['ports'], 'size_baseline': geometry,
            'nbt_sha256': sha(nbt_path), 'schem_sha256': sha(schem_path),
            'approved': True, 'approval_quote': APPROVAL,
            'formal_pattern_integrated': False, 'game_verified': False}, global_states


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d_%H%M%S_%f')
    final = json.loads((LOG / 'final-verification.json').read_text(encoding='utf-8'))
    browser = json.loads((LOG / 'browser-review.json').read_text(encoding='utf-8'))
    independent = json.loads((LOG / 'independent-review.json').read_text(encoding='utf-8'))
    assert final['passed'] and final['browser_review'] and independent['passed']
    assert sha(SOURCE / BUNDLE) == EXPECTED_SHA == final['archive_sha256']
    assert (SOURCE / BUNDLE).stat().st_size == EXPECTED_BYTES == final['archive_bytes']
    with zipfile.ZipFile(SOURCE / BUNDLE) as source_bundle:
        assert source_bundle.testzip() is None
        expected_names = {p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*')
                          if p.is_file() and p.name != BUNDLE}
        assert set(source_bundle.namelist()) == expected_names
        for name in expected_names:
            assert source_bundle.read(name) == (SOURCE / name).read_bytes(), name
    entries = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    assert tuple(entry['key'] for entry in entries) == KEYS
    checks, upgrades, previous = [], [], None
    for entry in entries:
        record, states = inspect(entry, browser)
        if previous is not None:
            differences = [pos for pos, value in previous.items()
                           if pos != (0, 0, 0) and states.get(pos) != value]
            assert not differences, f'升级移除或改写旧方块: {differences[:10]}'
            upgrades.append({'to': entry['key'], 'preserved_non_controller': len(previous) - 1,
                             'removed_or_changed': 0, 'same_world_anchor': True})
        checks.append(record)
        previous = states

    source_hashes = {p.relative_to(SOURCE).as_posix(): sha(p)
                     for p in sorted(SOURCE.rglob('*')) if p.is_file()}
    snapshot = ARCHIVES / f'{stamp}_I01_V8'
    snapshot.mkdir(parents=True, exist_ok=False)
    copied = snapshot / 'confirmed_v8'
    shutil.copytree(SOURCE, copied)
    assert source_hashes == {p.relative_to(copied).as_posix(): sha(p)
                             for p in sorted(copied.rglob('*')) if p.is_file()}
    evidence = snapshot / 'evidence'
    evidence.mkdir()
    for source in sorted(LOG.glob('*.json')):
        if source.name.startswith(('approval-', 'install-')):
            continue
        shutil.copy2(source, evidence / source.name)
        assert sha(source) == sha(evidence / source.name)
    rules = snapshot / 'rule_snapshot'
    rules.mkdir()
    for name in ('巨构提示词.txt', '当前多方块设计规则.md'):
        source = ROOT / 'rule' / name
        shutil.copy2(source, rules / name)
        assert sha(source) == sha(rules / name)
    # 本脚本只新增归档与记录；原确认版本和所有旧归档均不覆盖。
    shutil.copy2(Path(__file__), snapshot / Path(__file__).name)
    manifest = {'created_at': now.isoformat(), 'timezone': 'Asia/Hong_Kong',
                'status': 'approved_archived_not_installed', 'approval_quote': APPROVAL,
                'confirmation_scope': 'I01 V8 正交采集塔四阶段建筑外观与结构文件',
                'supersedes': '原交付内部待用户确认状态；候选文件内原文和旧归档保留',
                'machine_ids': ['I01'], 'unique_machines': 1, 'forms': 4,
                'batch_count_note': 'I01 四阶段属于同一台机器；不按四台或五台计算批次，不部署。',
                'source_delivery': str(SOURCE), 'archive': str(snapshot),
                'viewer': str(copied / 'index.html'), 'entries': checks, 'upgrades': upgrades,
                'source_zip_bytes': EXPECTED_BYTES, 'source_zip_sha256': EXPECTED_SHA,
                'preserved_source_file_sha256': source_hashes,
                'evidence_sha256': {p.name: sha(p) for p in sorted(evidence.iterdir())},
                'copy_rule': '复制并验证原压缩字节；未重新导出或重新压缩 NBT/Schematic。',
                'source_status_note': '原交付待确认字样按原字节保存；本清单记录用户批准。',
                'game_files_installed': False, 'formal_pattern_integrated': False,
                'recipe_or_machine_logic_changed': False, 'game_verified': False,
                'not_verified': ['Minecraft 实际成型与运行', '正式 Pattern 与端口能力', '生存材料完整可达性']}
    manifest_path = snapshot / '确认与校验清单.json'
    json_write(manifest_path, manifest)
    archived_hashes = {p.relative_to(snapshot).as_posix(): sha(p)
                       for p in sorted(snapshot.rglob('*')) if p.is_file()}
    target_zip = snapshot.with_suffix('.zip')
    with zipfile.ZipFile(target_zip, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in archived_hashes:
            archive.write(snapshot / name, name)
    with zipfile.ZipFile(target_zip) as archive:
        assert archive.testzip() is None and set(archive.namelist()) == set(archived_hashes)
        for name, expected in archived_hashes.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected, name
    assert source_hashes == {p.relative_to(SOURCE).as_posix(): sha(p)
                             for p in sorted(SOURCE.rglob('*')) if p.is_file()}
    result = {'time': now.isoformat(), 'approval_quote': APPROVAL, 'snapshot': str(snapshot),
              'zip': str(target_zip), 'zip_sha256': sha(target_zip), 'zip_bytes': target_zip.stat().st_size,
              'forms': 4, 'unique_machines': 1, 'archive_files': len(archived_hashes),
              'source_zip_sha256': EXPECTED_SHA, 'all_hashes_verified': True,
              'source_delivery_unchanged': True, 'game_files_installed': False,
              'formal_pattern_integrated': False, 'game_verified': False,
              'approval_manifest': str(manifest_path), 'upgrades': upgrades}
    log_path = LOG / f'approval-{stamp}.json'
    json_write(log_path, result)
    discussion = ROOT / 'doc/HK3GTL-内测5/讨论记录' / f'{now:%Y-%m-%d_%H-%M-%S}_I01_V8四阶确认归档.html'
    assert not discussion.exists()
    discussion.write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>I01 V8 四阶确认归档</title></head><body>
<h1>I01 V8 四阶确认归档</h1><p>记录时间：{now.isoformat()}，Asia/Hong_Kong。用户消息精确发送时间未另行核验。</p>
<p>用户已确认原话：「{APPROVAL}」。本轮界面为 I01 V8 第四阶，确认覆盖该正交四阶段候选的待批准状态。
该决定覆盖<a href="2026-10-14_17-59-59_I01四阶取消斜向并正交重设计.html">上轮记录</a>的待外观批准状态，不改其他机器决定。</p>
<p>已实施：完整交付、原 ZIP、真实纹理查看器、生成器和核验证据原字节独立归档于 {snapshot}；完整归档 ZIP 为 {target_zip}，SHA256：{result['zip_sha256']}。</p>
<p>已验证：NBT/Sponge/blueprint 逐格一致，粘贴 Offset 为各阶负主控坐标，四阶以同一世界主控锚点衔接，三次升级删除或改写旧非主控方块均为 0；尺寸、连通、接口净空、浏览器哈希、原交付和归档 ZIP 逐字节核对通过。</p>
<p>四个阶段归属 I01 一台机器，未按四台或五台计入部署批次；本次未写游戏实例、生产 Pattern、配方或机器逻辑。Minecraft 成型与运行尚未验收。</p>
<p>依据：rule/巨构提示词.txt、rule/当前多方块设计规则.md；批准与校验清单 {manifest_path}；日志 {log_path}。研究所重设计由主任务继续处理。</p>
</body></html>''', encoding='utf-8')
    result['discussion'] = str(discussion)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
