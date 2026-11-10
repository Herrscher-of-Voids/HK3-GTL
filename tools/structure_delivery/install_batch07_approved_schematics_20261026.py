# -*- coding: utf-8 -*-
"""按确认归档向增强版2.9.2安装五台建筑投影，保留正式机器验收边界。"""
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
from pathlib import Path
from project_paths import project_path
import shutil
import sys
import zipfile

import nbtlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from deploy_industrial_build import target_process_guard

GAME = project_path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
LOG = ROOT / 'logs/batch07-install-20261026'
IDS = ['I22', 'I23', 'I24', 'I25', 'I26']
FOLDER = 'HK3GTL_batch07_I22-I26_20261026'
TARGETS = [GAME / 'schematics' / FOLDER, GAME / 'config/worldedit/schematics' / FOLDER]
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def verify_sources():
    identity = json.loads((GAME.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8-sig'))
    assert identity['name'] == 'GregTech Leisure-增强版' and identity['versionId'] == '2.9.2'
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    assert index['pending_batch']['id'] == 'batch-07'
    assert index['pending_batch']['approved_machine_ids'] == IDS, '须先纠正I25漏计与批次顺序'
    entries = {row['id']: row for row in index['entries']}
    rows = []
    for i, key in enumerate(IDS):
        entry = entries[key]
        folder, bundle = project_path(entry['archive']), project_path(entry['archive_zip'])
        assert folder.is_dir() and sha(bundle) == entry['archive_zip_sha256']
        matches = list(folder.rglob('*.schem'))
        assert len(matches) == 1, (key, matches)
        source = matches[0]
        with zipfile.ZipFile(bundle) as z:
            assert z.testzip() is None
            name = source.relative_to(project_path(entry['approval_manifest']).parent).as_posix()
            assert hashlib.sha256(z.read(name)).hexdigest() == sha(source), key
        schematic = nbtlib.load(source)
        size = [int(schematic[k]) for k in ('Width', 'Height', 'Length')]
        offset = list(map(int, schematic['Offset']))
        metadata = schematic.get('Metadata', {})
        assert int(schematic['Version']) == 2 and int(schematic['DataVersion']) == 3465
        assert offset == [0, 0, 0] and not any(k.startswith('WEOffset') for k in metadata), '本批角点锚点约定不符'
        assert int(schematic['Palette']['minecraft:air']) == 0
        assert -60 + size[1] - 1 <= 236
        filename = key.lower() + '-approved.schem'
        rows.append(dict(id=key, source_archive=str(folder), source=str(source),
                         approval_manifest=entry['approval_manifest'], archive_zip=str(bundle),
                         archive_zip_sha256=entry['archive_zip_sha256'], sha256=sha(source),
                         filename=filename, size_xyz=size, offset=offset,
                         anchor=[i * 2048, -60, 0], occupied_y=[-60, -60 + size[1] - 1],
                         worldedit_load='//schem load ' + FOLDER + '/' + filename + ' sponge'))
    return rows


def main():
    assert not (LOG / 'installation.json').exists(), '已有接入收据，拒绝重复安装'
    guard_before = target_process_guard()
    rows = verify_sources()
    hk3 = GAME / 'mods/HK3GTL-内测5.jar'
    jar_before = sha(hk3)
    stages = [p.with_name(p.name + '.pending') for p in TARGETS]
    assert not any(p.exists() for p in TARGETS + stages), '目标目录已存在，拒绝覆盖'
    old = {str(p): sha(p) for base in [p.parent for p in TARGETS] for p in base.rglob('*.schem')}
    manifest = dict(batch='batch-07', status='installed_verified',
                    recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
                    instance=str(GAME), instance_version='2.9.2', installed_machine_ids=IDS,
                    authorization_message_id='msg_01a17792-a5d9-7183-9eca-29381c6d9012',
                    boundary='确认版建筑Sponge安装；正式控制器、Pattern、配方及游戏成型运行未验收。',
                    i26_volume='保留已批准外观；体积11,025,630低于I25的11,970,190，未将偏差改写为通过。',
                    targets=list(map(str, TARGETS)), structures=rows,
                    game_verified=False, formal_pattern_installed=False, saves_modified=False,
                    hk3gtl_jar_sha256=jar_before)
    created = []
    try:
        for stage in stages:
            stage.mkdir(parents=True, exist_ok=False)
            created.append(stage)
            for row in rows:
                shutil.copy2(row['source'], stage / row['filename'])
                assert sha(stage / row['filename']) == row['sha256']
            save(stage / 'manifest.json', manifest)
        guard_commit = target_process_guard()
        for stage, target in zip(stages, TARGETS):
            stage.rename(target)
            created[created.index(stage)] = target
        for target in TARGETS:
            assert json.loads((target / 'manifest.json').read_text(encoding='utf-8')) == manifest
            assert all(sha(target / row['filename']) == row['sha256'] for row in rows)
        assert all(sha(project_path(path)) == digest for path, digest in old.items())
        assert sha(hk3) == jar_before
    except Exception:
        allowed = {p.resolve() for p in TARGETS + stages}
        filenames = {r['filename'] for r in rows} | {'manifest.json'}
        for folder in created:
            if folder.exists() and folder.resolve() in allowed:
                files = list(folder.iterdir())
                if all(p.is_file() and p.name in filenames for p in files):
                    for path in files:
                        path.unlink()
                    folder.rmdir()
        raise
    manifest.update(process_guard_before=guard_before, process_guard_commit=guard_commit,
                    previous_schematics_verified_unchanged=len(old), old_schematics_sha256=old,
                    target_files_verified=10, target_manifests_verified=2)
    save(LOG / 'installation.json', manifest)
    table = ''.join('<tr><td>' + r['id'] + '</td><td>' + '×'.join(map(str, r['size_xyz'])) +
                    '</td><td>' + str(r['occupied_y']) + '</td><td><code>' + r['sha256'] + '</code></td></tr>' for r in rows)
    commands = ''.join('<h3>' + r['id'] + '</h3><pre>' + html.escape(r['worldedit_load']) + '\n/tp @s ' +
                       ' '.join(map(str, r['anchor'])) + '\n//paste -a\n/tp @s ' + str(r['anchor'][0] - 16) +
                       ' ' + str(r['occupied_y'][1] + 30) + ' -16</pre>' for r in rows)
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>batch-07五台结构实例接入</title><style>body{{max-width:1100px;margin:32px auto;padding:0 22px;background:#111b29;color:#e5edf5;font:16px/1.8 system-ui}}a{{color:#91dfe8}}code,pre{{overflow-wrap:anywhere;white-space:pre-wrap}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #526079;padding:8px}}td:last-child{{font-size:12px}}</style></head><body>
<h1>batch-07：I22–I26五台结构已接入</h1><p>{manifest['recorded_at']}（Asia/Hong_Kong）。目标：GTL增强版2.9.2 / Minecraft1.20.1 / Forge47.4.16。</p>
<p>I25原确认于2026-10-25 20:38:13，先前漏计；本批按批准顺序纠正为I22、I23、I24、I25、I26。I27和I28为下一批2/5，未混入本批。</p>
<p>五份Sponge均从不可变确认归档读取，与批准ZIP逐文件SHA一致；两处安装共10份结构与2份manifest已复读。旧投影及HK3GTL JAR保持原字节。</p>
<ul>{''.join('<li><code>' + html.escape(str(p)) + '</code></li>' for p in TARGETS)}</ul>
<table><thead><tr><th>机器</th><th>尺寸X×Y×Z</th><th>默认占用世界Y</th><th>Sponge SHA256</th></tr></thead><tbody>{table}</tbody></table>
<h2>游戏内查看</h2><p>使用增强版2.9.2的允许作弊、创造模式、超平坦专用测试存档。Forgematica可从对应目录载入；WorldEdit命令如下，仅用于确认没有玩家建筑的空地。相邻样例相隔2048格，实际使用前核对现场。</p>
<p>本批Sponge的Offset均为[0,0,0]且没有WEOffset；粘贴位置为蓝图最小角，不是主控。默认底部Y=-60，最高均不超过236。大型结构粘贴可能耗时；完成后将玩家移出地基。</p>{commands}
<h2>验收范围</h2><p>已完成建筑结构文件接入和实例清单核对。未改世界存档或正式机器定义，未声称控制器、Pattern、配方、生存获取链或游戏运行已通过。I26沿用负责人批准外观，历史体积偏差保留为未满足项。</p>
<p><a href="installation.json">安装收据</a> · <a href="geometry-placement-verification.json">独立几何与放置核对</a> · <a href="dependency-installation.json">投影依赖安装核对</a> · <a href="../../doc/HK3GTL-内测5/讨论记录/2026-10-26_17-37-41_I28确认与五台批次实装纠正.html">本轮决定与原文</a></p></body></html>'''
    (LOG / 'index.html').write_text(page, encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ['status', 'installed_machine_ids', 'targets', 'target_files_verified']}, ensure_ascii=True))


if __name__ == '__main__':
    main()
