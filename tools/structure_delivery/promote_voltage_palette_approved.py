# -*- coding: utf-8 -*-
"""将负责人批准的21形态电压主色快照接入正式建筑资源，保留旧归档与全部审批原件。

【变更记录 #1】2026-10-20 00:44:14（香港时间 · 已批准电压改色接入）
删除：无；不删除旧归档、候选、旧索引或旧正式资源备份。
新增：来源SHA前置核对、全体素双格式核验、不可变确认归档、63资源暂存及回滚。
修改：用批准候选替换21份正式建筑；沿用旧控制器、真实仓室和接口能力合同。
用途：把明确批准的配色接入已有Pattern读取路径；不启动游戏、构建、部署或改贴图。
边界：审批时间未知，记录实际执行时间；候选原有待审文字作为历史字节完整保留。

【变更记录 #2】2026-10-20 00:49:45（香港时间 · 接入前置核验校正）
删除：导出空白边界必须等于实体边界的过强断言；新增：实体逐轴总表下限检查。
修改：允许原批准I08/I13保留原有导出边距；正式63文件使用统一相对路径及完整SHA。
用途：不更改已批准几何，核验真实实体尺寸与源记录一致；补充固定收据入口。
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import copy
import hashlib
import html
import json
import os
import shutil
import zipfile
import nbtlib as nbt

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / 'deliveries/21形态_电压主色修订候选_R172_20261019'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
RES = ROOT / 'src/main/resources/data/hk3gtl'
LOG = ROOT / 'logs/voltage-architecture-approved-20261020'
RULES = ['rules.md', '系统角色设定.md', '崩坏三-gtl (hk3gtl) 项目规则.md',
         'hk3gtl java文件变更备注规范.md', '当前多方块设计规则.md', '巨构提示词.txt']
QUOTE = '采用整批21形态新配色'
EXPECTED_ZIP = '5dd32253ae44d3c0290e71835479b707ee47b3a46817f933c08cebf0de61ab46'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2,
                              separators=(',', ':') if compact else None) + '\n', encoding='utf-8')


def inventory(folder):
    return {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
            for p in sorted(folder.rglob('*')) if p.is_file()}


def state_text(state):
    value = str(state['Name'])
    if state.get('Properties'):
        value += '[' + ','.join(f'{k}={v}' for k, v in sorted(state['Properties'].items())) + ']'
    return value


def decode(path):
    data = nbt.load(path)
    result = {tuple(map(int, b['pos'])): state_text(data['palette'][int(b['state'])])
              for b in data['blocks']}
    assert len(result) == len(data['blocks']), f'重复坐标：{path}'
    return data, result


def verify_sponge(path, blueprint):
    data = nbt.load(path)
    w, h, length = blueprint['size']
    assert data.root_name == 'Schematic' and int(data['Version']) == 2
    assert int(data['DataVersion']) == 3465
    assert [int(data[k]) for k in ('Width', 'Height', 'Length')] == [w, h, length]
    assert list(map(int, data['Offset'])) == [-v for v in blueprint.get('paste_anchor', blueprint['controller'])]
    palette = {int(v): str(k) for k, v in data['Palette'].items()}
    assert int(data['Palette']['minecraft:air']) == 0 and int(data['PaletteMax']) == len(palette)
    raw = [int(v) & 255 for v in data['BlockData']]
    values, current, shift = [], 0, 0
    for value in raw:
        current |= (value & 127) << shift
        if value & 128:
            shift += 7
            assert shift <= 28
        else:
            values.append(current)
            current = shift = 0
    assert shift == 0 and len(values) == w * h * length
    actual = {(i % w, i // (w * length), (i // w) % length): palette[v]
              for i, v in enumerate(values) if palette[v] != 'minecraft:air'}
    assert actual == {tuple(b['pos']): b['state'] for b in blueprint['blocks']}


def relative(blocks, anchor, controller):
    return {tuple(p[i] - anchor[i] for i in range(3)): state
            for p, state in blocks.items() if list(p) != controller}


def formal_paths(key):
    return [RES / 'approved_architecture' / (key + '.json'),
            RES / 'structures/approved' / (key + '.nbt'),
            RES / 'structures/approved' / (key + '.json')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='写入批准归档及正式资源；省略时只核验来源')
    args = parser.parse_args()
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp, iso = now.strftime('%Y%m%d_%H%M%S_%f'), now.isoformat(timespec='seconds')
    LOG.mkdir(parents=True, exist_ok=True)
    if (LOG / '接入收据.json').exists() and args.apply:
        raise RuntimeError('已存在接入收据；请先核对该收据，不重复生成批准归档')
    manifest = read(CANDIDATE / 'manifest.json')
    source_zip = CANDIDATE / '21形态_电压主色修订候选_R172_结构与预览.zip'
    assert sha(source_zip) == EXPECTED_ZIP
    with zipfile.ZipFile(source_zip) as archive:
        assert archive.testzip() is None
    assert len(manifest['machines']) == 21
    old_index = read(INDEX)
    old_archive_hashes = inventory(ARCHIVES)
    candidate_hashes = inventory(CANDIDATE)
    entries, inherited = [], []
    blueprints = {}
    for entry in manifest['machines']:
        key = 'i01' if entry['key'] == 'i01-1' else entry['key'].replace('i01-', 'i01_')
        folder = CANDIDATE / entry['folder']
        bp = read(folder / 'blueprint.json')
        source_nbt, source_schem = folder / (entry['name'] + '.nbt'), folder / (entry['name'] + '.schem')
        assert sha(source_nbt) == entry['hashes']['nbt'] and sha(source_schem) == entry['hashes']['schem']
        structure, cells = decode(source_nbt)
        assert cells == {tuple(b['pos']): b['state'] for b in bp['blocks']}
        assert list(map(int, structure['size'])) == bp['size'] == entry['size_xyz']
        assert cells[tuple(bp['controller'])] == 'minecraft:diamond_block'
        assert len(cells) == entry['blocks'] and len(bp['ports']) == 6
        verify_sponge(source_schem, bp)
        formal, template, meta = formal_paths(key)
        old, old_meta = read(formal), read(meta)
        old_structure, old_cells = decode(template)
        assert old['size'] == bp['size'] and old['controller'] == bp['controller']
        assert set(cells) == {tuple(b['pos']) for b in old['blocks']} == set(old_cells)
        assert {(p['id'], tuple(p['pos']), p['face']) for p in bp['ports']} == {
            (p['id'], tuple(p['pos']), p['face']) for p in old['ports']}
        assert all(cells[tuple(p['pos'])] == 'hk3gtl:industrial_port_casing' for p in bp['ports'])
        bounds = [[min(p[i] for p in cells), max(p[i] for p in cells)] for i in range(3)]
        audit = read(folder / '设计与检查.json')['audit']['size_baseline']
        actual_xyz = [hi - lo + 1 for lo, hi in bounds]
        baseline_xyz = [audit['baseline_wdh'][i] for i in (0, 2, 1)]
        assert actual_xyz == audit['actual_xyz']
        assert all(actual_xyz[i] >= baseline_xyz[i] for i in range(3))
        assert all(0 <= lo <= hi < bp['size'][i] for i, (lo, hi) in enumerate(bounds))
        previous = entry['inheritance']['previous']
        if previous:
            prior, prior_cells = blueprints[previous]
            before = relative(prior_cells, prior.get('paste_anchor', prior['controller']), prior['controller'])
            after = relative(cells, bp.get('paste_anchor', bp['controller']), bp['controller'])
            assert before.items() <= after.items()
            inherited.append({'from': previous, 'to': entry['key'], 'preserved': len(before), 'passed': True})
        blueprints[entry['key']] = (bp, cells)
        entries.append((entry, key, bp, cells, old, old_meta, old_structure, old_cells))
    assert len(inherited) == 7
    if not args.apply:
        print(json.dumps({'shapes': len(entries), 'inheritance_checks': inherited, 'write': False}, ensure_ascii=False))
        return
    archive_dir = ARCHIVES / (stamp + '_21形态_电压主色修订_已确认')
    archive_dir.mkdir(exist_ok=False)
    approved = archive_dir / 'confirmed_voltage_r172'
    shutil.copytree(CANDIDATE, approved)
    evidence = archive_dir / 'evidence'
    evidence.mkdir()
    shutil.copy2(INDEX, evidence / 'previous-current-index.json')
    save(evidence / '候选原件身份.json', candidate_hashes)
    save(evidence / '接续六规则身份.json', {'read_at': iso, 'timezone': 'Asia/Hong_Kong',
         'rules': [{'path': 'rule/' + name, 'sha256': sha(ROOT / 'rule' / name)} for name in RULES],
         'discussion_read': 'doc/HK3GTL-内测5/讨论记录/2026-10-19_14-16-06_能源工艺与21形态改色候选整批交付.html',
         'context_gatherer': '当前工具列表无该工具，未冒称调用'})
    staged, backups = archive_dir / 'formal_resources', evidence / 'previous_formal_resources'
    staged.mkdir()
    rows = []
    change = {'record': 1, 'time': iso, 'reason': '负责人明确采用整批21形态新配色',
              'deleted': '无；旧归档、候选原件与旧正式资源快照保留',
              'added': '明确目标电压、新批准来源与本次修改身份',
              'modified': '主体配色采用已批候选，控制器/仓室与能力合同沿用原正式实现',
              'purpose': '使已有Pattern和放置模板读取批准配色；游戏成型与运行仍待验收'}
    for entry, key, bp, cells, old, old_meta, old_structure, old_cells in entries:
        for path in formal_paths(key):
            target = backups / path.relative_to(RES)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        source = approved / entry['folder'] / 'blueprint.json'
        source_nbt = source.parent / (entry['name'] + '.nbt')
        target_json = staged / 'approved_architecture' / (key + '.json')
        target_nbt = staged / 'structures/approved' / (key + '.nbt')
        target_meta = target_nbt.with_suffix('.json')
        data = copy.deepcopy(old)
        controller = tuple(bp['controller'])
        old_arch_cells = {tuple(b['pos']): b['state'] for b in old['blocks']}
        data['blocks'] = [{'pos': b['pos'], 'state': old_arch_cells[controller] if tuple(b['pos']) == controller else b['state']}
                          for b in bp['blocks']]
        source_record = {'version': '电压主色修订R172已批准', 'blueprint': str(source.relative_to(ROOT)).replace('\\', '/'),
                         'sha256': sha(source), 'approval': QUOTE, 'recorded_at': iso, 'original_message_time': '未知'}
        if 'approved_source' in data:
            data.setdefault('approved_source_history', []).append(data['approved_source'])
        data['approved_source'] = source_record
        data['target_voltage'], data['target_casing'] = entry['target_voltage'], entry['target_casing']
        data.setdefault('_change_records', []).append(change)
        if 'approved_snapshot' in data:
            data['approved_snapshot'] = str(archive_dir.relative_to(ROOT)).replace('\\', '/')
        for name in ('source_nbt_sha256', 'source_blueprint_sha256'):
            if name in data:
                data[name] = sha(source_nbt if name == 'source_nbt_sha256' else source)
        if 'upgrade_contract' in data:
            data['upgrade_contract'] = bp['upgrade_contract']
        save(target_json, data, compact=True)
        structure = nbt.load(source_nbt)
        positions = {tuple(map(int, b['pos'])): b for b in structure['blocks']}
        old_positions = {tuple(map(int, b['pos'])): b for b in old_structure['blocks']}
        replacements = {controller} | {tuple(p['pos']) for p in bp['ports']}
        for pos in replacements:
            value = old_structure['palette'][int(old_positions[pos]['state'])]
            if value not in structure['palette']:
                structure['palette'].append(copy.deepcopy(value))
            positions[pos]['state'] = nbt.Int(structure['palette'].index(value))
        target_nbt.parent.mkdir(parents=True, exist_ok=True)
        structure.save(target_nbt, gzipped=True)
        _, decoded = decode(target_nbt)
        assert all(decoded[p] == (old_cells[p] if p in replacements else state) for p, state in cells.items())
        meta = copy.deepcopy(old_meta)
        meta.update({'sha256': sha(target_json), 'template_sha256': sha(target_nbt),
                     'approved_blueprint_sha256': sha(source), 'approved_nbt_sha256': sha(source_nbt),
                     'review_snapshot': str(archive_dir.relative_to(ROOT)).replace('\\', '/'),
                     'target_voltage': entry['target_voltage'], 'target_casing': entry['target_casing'],
                     'approval_quote': QUOTE, 'game_verified': False})
        if 'source_nbt_sha256' in meta:
            meta['source_nbt_sha256'] = sha(source_nbt)
        if 'approved_bundle_sha256' in meta:
            meta['approved_bundle_sha256'] = EXPECTED_ZIP
        meta.setdefault('_change_records', []).append(change)
        save(target_meta, meta)
        rows.append({'key': key, 'candidate_key': entry['key'], 'size_xyz': bp['size'], 'blocks': len(cells),
                     'voltage': entry['target_voltage'], 'casing': entry['target_casing'],
                     'actual_xyz': [max(p[i] for p in cells) - min(p[i] for p in cells) + 1 for i in range(3)],
                     'source_blueprint': str(source.relative_to(ROOT)).replace('\\', '/'),
                     'source_blueprint_sha256': sha(source),
                     'source_nbt': str(source_nbt), 'source_nbt_sha256': sha(source_nbt),
                     'source_schem': str(source.parent / (entry['name'] + '.schem')),
                     'source_schem_sha256': sha(source.parent / (entry['name'] + '.schem')),
                     'formal_sha256': {str(p.relative_to(staged)).replace('\\', '/'): sha(p) for p in (target_json, target_nbt, target_meta)},
                     'previous_formal_sha256': {str(p.relative_to(RES)).replace('\\', '/'): sha(p) for p in formal_paths(key)},
                     'previous_approved_source': old.get('approved_source', {'snapshot': old.get('approved_snapshot'), 'nbt_sha256': old.get('source_nbt_sha256')}),
                     'controller_and_six_port_positions_unchanged': True, 'other_cells_exact_candidate': True})
    confirmation = {'time': iso, 'timezone': 'Asia/Hong_Kong', 'approval_quote': QUOTE,
                    'approval_message_time': '未知；此处为实际接入记录时间', 'shape_count': 21,
                    'candidate_zip_sha256': EXPECTED_ZIP, 'candidate_files_unchanged': True,
                    'candidate_manifest_sha256': sha(approved / 'manifest.json'),
                    'inheritance_checks': inherited, 'structures': rows,
                    'game_launched': False, 'game_verified': False, 'build_or_deploy_performed': False,
                    'notes': '旧候选待审字段是历史原件；审批效力由本外部确认清单给出。R172仅源候选标签。'}
    save(archive_dir / '确认与校验清单.json', confirmation)
    html_rows = ''.join('<tr><td>' + html.escape(r['candidate_key'].upper()) + '</td><td>' + r['voltage'] + '</td><td>' +
                        '×'.join(map(str, r['size_xyz'])) + '</td><td>' + str(r['blocks']) + '</td></tr>' for r in rows)
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>21形态新配色确认接入</title><style>body{max-width:1100px;margin:30px auto;font:16px/1.8 system-ui}td,th{border:1px solid #ccd;padding:8px}table{border-collapse:collapse}</style><h1>21形态新配色确认接入</h1><p>' + iso + ' Asia/Hong_Kong</p><blockquote>' + QUOTE + '</blockquote><p>已按批准候选接入正式建筑资源。旧归档与候选原字节保留；已有控制器、接口能力及仓室类型沿用，未进行构建、部署或游戏成型验收。R172为候选来源标签，不代表本轮构建修订。</p><p><a href="confirmed_voltage_r172/index.html">批准原件评审总览</a> · <a href="确认与校验清单.json">逐项来源与正式SHA</a></p><table><tr><th>形态</th><th>电压</th><th>宽高深</th><th>实体块</th></tr>' + html_rows + '</table><p>7组原地扩建逐格继承保持；21份Schematic保存在批准原件中，正式游戏路径沿用NBT与JSON。原候选中的未批准文字保留为历史，不代表当前审批状态。</p><p>【记录 #1】' + iso + '：删除无；新增明确批准、归档及正式资源身份；修改正式配色来源；用途为接续审计。未新增方块、未改燃料贴图、未改变I14/I15待满批状态。</p></html>'
    (archive_dir / '确认接入.html').write_text(page, encoding='utf-8')
    archive_zip = archive_dir.with_suffix('.zip')
    with zipfile.ZipFile(archive_zip, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(archive_dir.rglob('*')):
            if path.is_file():
                z.write(path, path.relative_to(archive_dir))
    with zipfile.ZipFile(archive_zip) as z:
        assert z.testzip() is None
    updated = copy.deepcopy(old_index)
    indexed = {entry['key']: entry for entry in updated['entries']}
    for row in rows:
        entry = indexed[row['key']]
        entry.setdefault('previous_approved_versions', []).append(copy.deepcopy({k: v for k, v in entry.items() if k != 'previous_approved_versions'}))
        entry.update({'status': 'approved_formal_resource_present_not_deployed', 'archive': str(approved / row['candidate_key']),
                      'approved_nbt': row['source_nbt'], 'approved_nbt_sha256': row['source_nbt_sha256'],
                      'approval_quote': QUOTE, 'approval_manifest': str(archive_dir / '确认与校验清单.json'),
                      'archive_zip': str(archive_zip), 'archive_zip_sha256': sha(archive_zip),
                      'target_voltage': row['voltage'], 'target_casing': row['casing'],
                      'formal_metadata_sha256': row['formal_sha256']['structures/approved/' + row['key'] + '.json'],
                      'game_files_installed': False, 'game_verified': False})
    updated.update({'updated_at': iso, 'snapshot': str(archive_dir), 'zip': str(archive_zip), 'zip_sha256': sha(archive_zip),
                    'target_instance': 'C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft',
                    'target_pack_version': '2.9', 'previous_index': {'preserved_copy': str(evidence / 'previous-current-index.json'), 'sha256': sha(INDEX)},
                    'scope': '21种既有正式形态采用批准电压改色；待满5台的新结构批次仍独立保留'})
    updated.setdefault('_change_records', []).append(change)
    changed = []
    try:
        for path in sorted(staged.rglob('*')):
            if path.is_file():
                target = RES / path.relative_to(staged)
                assert sha(target) == sha(backups / path.relative_to(staged))
                shutil.copy2(path, target)
                changed.append(target)
                assert sha(target) == sha(path)
        save(INDEX, updated)
        assert inventory(CANDIDATE) == candidate_hashes
        assert all(sha(ROOT / path) == digest for path, digest in old_archive_hashes.items() if ROOT / path != INDEX)
        assert all(sha(ROOT / 'deliveries/多方块确认归档' / archive_dir.name / 'confirmed_voltage_r172' / Path(path).relative_to(CANDIDATE.relative_to(ROOT))) == digest for path, digest in candidate_hashes.items())
    except Exception:
        for target in changed:
            shutil.copy2(backups / target.relative_to(RES), target)
        shutil.copy2(evidence / 'previous-current-index.json', INDEX)
        raise
    receipt = {**confirmation, 'status': '正式63资源和索引接入通过，尚未构建部署',
               'archive_directory': str(archive_dir), 'archive_zip': str(archive_zip), 'archive_zip_sha256': sha(archive_zip),
               'approval_manifest': str(archive_dir / '确认与校验清单.json'),
               'approval_manifest_sha256': sha(archive_dir / '确认与校验清单.json'),
               'frozen_formal_resource_root': str(staged),
               'archive_file_hashes': inventory(archive_dir), 'formal_files_written': len(changed),
               'old_archive_files_checked': len(old_archive_hashes) - 1, 'old_archives_unchanged': True,
               'candidate_file_hashes': candidate_hashes, 'current_index_sha256': sha(INDEX)}
    save(LOG / '接入收据.json', receipt)
    save(ROOT / 'logs/voltage-architecture-r172/formal-installation.json', receipt)
    discussion = ROOT / 'doc/HK3GTL-内测5/讨论记录' / (now.strftime('%Y-%m-%d_%H-%M-%S') + '_21形态电压新配色明确批准与正式接入.html')
    discussion.write_text(page.replace('href="confirmed_voltage_r172/index.html"', 'href="../../../' + str(approved.relative_to(ROOT)).replace('\\', '/') + '/index.html"').replace('href="确认与校验清单.json"', 'href="../../../' + str((archive_dir / '确认与校验清单.json').relative_to(ROOT)).replace('\\', '/') + '"'), encoding='utf-8')
    print(json.dumps({'archive': str(archive_dir), 'zip_sha256': sha(archive_zip), 'formal_files': len(changed), 'discussion': str(discussion), 'passed': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
