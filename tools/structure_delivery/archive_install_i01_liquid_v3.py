# -*- coding: utf-8 -*-
"""封存并接入用户已确认的 I01-1 V3 Sponge；不改模组包、存档或旧版投影。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
from pathlib import Path
import shutil
import zipfile

import nbtlib

from redesign69_geometry import ROOT


SOURCE = ROOT / 'deliveries/I01-1_崩坏能采集塔液态_接口竖梁对位_V3_20261025'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版')
GAME = INSTANCE / 'minecraft'
SCHEM_FOLDER = 'HK3GTL_I01-1_V3_20261025'
SCHEM_NAME = 'i01-1-hbv-liquid-collector-v3-interface-ribs.schem'
APPROVAL = 'i01-1 V3 ok 接入实例 , next'
OLD_V2 = GAME / 'schematics/HK3GTL_centered_V2_20261023_r175/i01-1-controller-centered-v2.schem'


def now():
    return datetime.now(timezone(timedelta(hours=8)))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def html_table(rows):
    return ''.join('<tr><td><code>' + html.escape(name) + '</code></td><td><code>' + digest + '</code></td></tr>'
                   for name, digest in rows)


def main():
    report_path = SOURCE / '设计与检查.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    data, audit = report['data'], report['audit']
    nbt_path = SOURCE / (data['name'] + '.nbt')
    schem_path = SOURCE / SCHEM_NAME
    assert data['name'] == 'i01-1-hbv-liquid-collector-v3-interface-ribs'
    assert audit['approval'].startswith('待负责人外观审核')
    assert audit['left_right_symmetry']['exact'] is True
    assert audit['connected_blocks'] == audit['block_count']
    assert all(audit['voltage_thresholds_passed'].values())
    assert data['controller'] == [21, 5, 14]
    assert len(data['ports']) == 6
    assert audit['interface_ribs']['target_x'] == [5, 9, 33, 37]

    nbt = nbtlib.load(nbt_path)
    schem = nbtlib.load(schem_path)
    assert len(nbt['blocks']) == audit['block_count']
    assert list(map(int, nbt['size'])) == data['size']
    assert int(schem['Version']) == 2
    assert [int(schem[k]) for k in ('Width', 'Height', 'Length')] == data['size']
    assert list(map(int, schem['Offset'])) == [-p for p in data['controller']]
    assert sha(nbt_path) == audit['hashes']['nbt']
    assert sha(schem_path) == audit['hashes']['schem']

    target_index = json.loads((INSTANCE / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))
    instance_cfg = (INSTANCE / 'instance.cfg').read_text(encoding='utf-8-sig')
    assert target_index['name'] == 'GregTech Leisure-增强版'
    assert target_index['versionId'] == '2.9.2'
    assert 'name=GregTech Leisure-增强版' in instance_cfg
    assert GAME.is_dir()
    assert OLD_V2.is_file()
    old_v2_hash = sha(OLD_V2)

    name = now().strftime('%Y%m%d_%H%M%S_%f') + '_I01-1_HBV液态采集塔V3_已确认'
    snapshot = ARCHIVES / name
    bundle = ARCHIVES / (name + '.zip')
    record_log = ROOT / 'logs/i01-1-v3-instance-install-20261025'
    targets = [GAME / 'schematics' / SCHEM_FOLDER,
               GAME / 'config/worldedit/schematics' / SCHEM_FOLDER]
    stages = [target.with_name(target.name + '.pending') for target in targets]
    if snapshot.exists() or bundle.exists() or record_log.exists():
        raise FileExistsError('时间戳归档或接入记录目标已存在')
    if any(target.exists() for target in targets + stages):
        raise FileExistsError('V3投影目录或暂存目录已存在，拒绝覆盖')

    source_hashes = {p.relative_to(SOURCE).as_posix(): sha(p)
                     for p in SOURCE.rglob('*') if p.is_file()}
    snapshot.mkdir(parents=True, exist_ok=False)
    archived_delivery = snapshot / 'I01-1'
    shutil.copytree(SOURCE, archived_delivery)
    dependencies = snapshot / '生成依赖'
    dependencies.mkdir()
    for filename in ('archive_install_i01_liquid_v3.py', 'build_i01_liquid_redesign_v1.py',
                     'build_redesign69.py', 'material_resources.py', 'redesign69_geometry.py',
                     'structure_size_baseline.py', 'review_controller_integration_20261023.py'):
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, dependencies / filename)
    assert source_hashes == {p.relative_to(archived_delivery).as_posix(): sha(p)
                             for p in archived_delivery.rglob('*') if p.is_file()}

    archive_files = {p.relative_to(snapshot).as_posix(): sha(p)
                     for p in snapshot.rglob('*') if p.is_file()}
    manifest_rows = ''.join(f'<tr><td><code>{html.escape(path)}</code></td><td><code>{digest}</code></td></tr>'
                            for path, digest in sorted(archive_files.items()))
    (snapshot / '确认与校验清单.html').write_text(f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>I01-1 V3 确认归档</title><style>body{{max-width:1050px;margin:32px auto;padding:0 20px;background:#111923;color:#e8edf3;font:15px/1.7 system-ui,"Microsoft YaHei",sans-serif}}a{{color:#80d8d0}}table{{width:100%;border-collapse:collapse;overflow-wrap:anywhere}}td,th{{border:1px solid #42515e;padding:7px;text-align:left}}code{{font-size:12px;overflow-wrap:anywhere}}</style></head><body>
<h1>I01-1 崩坏能采集塔·液态 V3</h1><p>归档时间：{now().isoformat(timespec='seconds')}（Asia/Hong_Kong）</p>
<p>确认原话：<q>{html.escape(APPROVAL)}</q>。状态：外观与逐格结构已确认；实例投影仅接入Sponge文件。</p>
<p>结构：43×55×43，{audit['block_count']:,}块、{audit['unique_material_count']}种材料；中轴X=21精确镜像。四条北立面竖梁位于x=5、9、33、37，接口工业方块保留。</p>
<p>NBT与Sponge尺寸、DataVersion、哈希及NBT方块数已复核；归档副本与源交付逐文件SHA-256一致。Pattern、配方和游戏内成型/运行不在本次接入范围。</p>
<p>目标实例：<code>{html.escape(str(INSTANCE))}</code>，GTL增强版 2.9.2。接入目录：<code>{html.escape(str(targets[0]))}</code> 与 <code>{html.escape(str(targets[1]))}</code>。</p>
<h2>归档文件 SHA-256</h2><table><thead><tr><th>文件</th><th>SHA-256</th></tr></thead><tbody>{manifest_rows}</tbody></table></body></html>''', encoding='utf-8')

    archived_hashes = {p.relative_to(snapshot).as_posix(): sha(p)
                       for p in snapshot.rglob('*') if p.is_file()}
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in archived_hashes:
            archive.write(snapshot / relative, relative)
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(archived_hashes)
        assert all(hashlib.sha256(archive.read(path)).hexdigest() == digest
                   for path, digest in archived_hashes.items())
    bundle_hash = sha(bundle)
    archived_schem = archived_delivery / SCHEM_NAME
    schem_hash = sha(archived_schem)
    install_manifest = {
        'recorded_at': now().isoformat(timespec='seconds'),
        'target_instance': str(GAME), 'instance_version': target_index['versionId'],
        'structures': [{'key': 'i01-1', 'title': data['title'], 'controller': data['controller'],
                        'source_archive': str(archived_schem), 'name': SCHEM_NAME,
                        'sha256': schem_hash, 'archive_zip_sha256': bundle_hash}],
        'boundary': '仅登记已批准Sponge投影；不代表Pattern、配方或游戏内成型运行验收。',
    }

    created_stages = []
    committed = []
    try:
        for stage in stages:
            stage.mkdir(parents=True, exist_ok=False)
            created_stages.append(stage)
            shutil.copy2(archived_schem, stage / SCHEM_NAME)
            save_json(stage / 'manifest.json', install_manifest)
            assert sha(stage / SCHEM_NAME) == schem_hash
        for stage, target in zip(stages, targets):
            stage.rename(target)
            committed.append(target)
        for target in targets:
            assert sha(target / SCHEM_NAME) == schem_hash
            assert json.loads((target / 'manifest.json').read_text(encoding='utf-8')) == install_manifest
    except Exception:
        for folder in committed + created_stages:
            allowed_parents = {target.parent.resolve() for target in targets}
            allowed_names = {SCHEM_FOLDER, SCHEM_FOLDER + '.pending'}
            if (folder.exists() and folder.resolve().parent in allowed_parents
                    and folder.name in allowed_names):
                expected = {SCHEM_NAME, 'manifest.json'}
                entries = list(folder.iterdir())
                if {p.name for p in entries} == expected and all(p.is_file() for p in entries):
                    for item in entries:
                        item.unlink()
                    folder.rmdir()
        raise

    record_log.mkdir(parents=True, exist_ok=False)
    install_details = [(str(target / SCHEM_NAME), sha(target / SCHEM_NAME)) for target in targets]
    (record_log / '接入核验.html').write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I01-1 V3实例接入核验</title>
<style>body{{max-width:1000px;margin:32px auto;padding:0 20px;background:#111923;color:#e8edf3;font:15px/1.7 system-ui,"Microsoft YaHei",sans-serif}}code{{overflow-wrap:anywhere}}</style></head><body>
<h1>I01-1 V3 实例接入核验</h1><p>核验时间：{now().isoformat(timespec='seconds')}（Asia/Hong_Kong）</p><p>GTL增强版 2.9.2；Sponge v2文件已写入并复读SHA-256，两处内容一致。</p>
<p>批准归档：<code>{html.escape(str(snapshot))}</code><br>ZIP：<code>{html.escape(str(bundle))}</code><br>ZIP SHA-256：<code>{bundle_hash}</code></p>
<p>Sponge SHA-256：<code>{schem_hash}</code><br>V2旧Sponge保持原文件与哈希，未覆盖。</p>
<ul>{''.join('<li><code>'+html.escape(path)+'</code> SHA-256 <code>'+digest+'</code></li>' for path,digest in install_details)}</ul>
<p>仅接入结构投影文件；未改模组JAR、世界存档或正式Pattern，未启动游戏。游戏内成型与运行尚待实测。</p></body></html>''', encoding='utf-8')

    assert source_hashes == {p.relative_to(SOURCE).as_posix(): sha(p)
                             for p in SOURCE.rglob('*') if p.is_file()}
    assert sha(OLD_V2) == old_v2_hash
    print(json.dumps({'archive': str(snapshot), 'zip': str(bundle), 'zip_sha256': bundle_hash,
                      'schem_sha256': schem_hash, 'instance_version': target_index['versionId'],
                      'install_paths': [str(p / SCHEM_NAME) for p in targets],
                      'install_log': str(record_log / '接入核验.html')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
