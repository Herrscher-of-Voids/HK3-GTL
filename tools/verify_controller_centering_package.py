# -*- coding: utf-8 -*-
"""核对修订175构建与批准原件，输出部署所需的独立包身份收据。

【变更记录 #1】2026-10-23 13:40:02（内测5修订175）
- 删除：无；旧核验入口与历史收据保留。
- 新增：26形态三类资源、21份批准几何、归档ZIP与原件身份交叉核验。
- 修改：只在clean build成功且最终JAR对应当前源码时生成passed收据。
- 用途：阻止旧包、未批几何或漏打包进入实例；不能代替实机成型和运行。

【变更记录 #2】2026-10-23 13:43:39（内测5修订175）
- 删除：对手工声明构建成功的依赖；新增：完整构建执行、日志与输入快照。
- 修改：构建期间源码、资源或构建参数变化时拒绝生成通过收据。
- 用途：避免协作修改导致最终包和源码不一致；失败时保留诊断。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import argparse
import json
import subprocess
import zipfile
from pathlib import Path
from structure_delivery.project_paths import project_path

import nbtlib

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'logs/controller-centering-install-20261023'
DATA = ROOT / 'src/main/resources/data/hk3gtl'
JAR = ROOT / 'build/libs/hk3gtl-0.5.0.jar'


def sha(path):
    return hashlib.sha256(project_path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(project_path(path).read_text(encoding='utf-8-sig'))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def decode(path):
    template = nbtlib.load(path)
    palette = [str(p['Name']) + ('[' + ','.join(f'{k}={v}' for k, v in sorted(p['Properties'].items())) + ']'
               if 'Properties' in p else '') for p in template['palette']]
    return {tuple(int(v) for v in b['pos']): palette[int(b['state'])] for b in template['blocks']}


def build():
    def inputs():
        paths = [p for p in (ROOT / 'src').rglob('*') if p.is_file()]
        paths += [ROOT / 'build.gradle', ROOT / 'gradle.properties']
        return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}
    started = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()
    before = inputs()
    write(LOGS / 'build-source-inputs.json', before)
    command = ['cmd.exe', '/d', '/c', 'gradlew.bat', 'clean', 'build', '--console=plain']
    with (LOGS / 'clean-build.log').open('w', encoding='utf-8') as output:
        code = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT).returncode
    after = inputs()
    receipt = {'status': 'passed' if code == 0 and before == after else 'failed', 'revision': 175,
               'started_at': started, 'finished_at': dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
               'exit_code': code, 'command': command, 'source_inputs_unchanged': before == after,
               'input_files': len(before), 'sha256': sha(JAR) if JAR.exists() else None,
               'log': str(LOGS / 'clean-build.log')}
    write(LOGS / 'build-verification.json', receipt)
    if receipt['status'] != 'passed':
        raise RuntimeError('完整构建失败或输入在构建中变化，请检查clean-build.log及构建收据。')


def main():
    parser = argparse.ArgumentParser(description='修订175完整构建与批准结构包验证')
    parser.add_argument('--build', action='store_true')
    args = parser.parse_args()
    if args.build:
        build()
    build_receipt = read(LOGS / 'build-verification.json')
    assert build_receipt['status'] == 'passed' and build_receipt['exit_code'] == 0 and build_receipt['revision'] == 175
    assert build_receipt['sha256'] == sha(JAR)
    approval_receipt = read(LOGS / 'approval-archive.json')
    manifest_path = project_path(approval_receipt['approval_manifest'])
    manifest = read(manifest_path)
    source = project_path(approval_receipt['source_root'])
    assert manifest['approval_quote'] == '实装这一些吧'
    assert sha(approval_receipt['zip']) == approval_receipt['zip_sha256']
    with zipfile.ZipFile(approval_receipt['zip']) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            if not name.endswith('/'):
                assert hashlib.sha256(archive.read(name)).hexdigest() == sha(source.parent / name), name
    for name, expected in manifest['source_files_sha256'].items():
        assert sha(source / name) == expected, name
        assert sha(project_path(manifest['source_root']) / name) == expected, name
    rows = []
    for item in manifest['structures']:
        key, candidate = item['key'], item['candidate_key']
        approved = read(source / candidate / 'blueprint.json')
        layout_path = DATA / f'approved_architecture/{key}.json'
        template_path = DATA / f'structures/approved/{key}.nbt'
        meta_path = DATA / f'structures/approved/{key}.json'
        layout, meta = read(layout_path), read(meta_path)
        assert meta['approved_blueprint_sha256'] == item['source_blueprint_sha256']
        assert meta['approved_nbt_sha256'] == item['source_nbt_sha256']
        assert meta['sha256'] == sha(layout_path) and meta['template_sha256'] == sha(template_path)
        assert approved['size'] == layout['size'] == meta['size_xyz']
        assert approved['controller'] == layout['controller'] == meta['controller']
        ctrl = tuple(layout['controller'])
        assert ctrl[0] * 2 == layout['size'][0] - 1
        assert [(p['id'], p['pos'], p['face']) for p in approved['ports']] == [
            (p['id'], p['pos'], p['face']) for p in layout['ports']]
        expected = {tuple(b['pos']): b['state'] for b in approved['blocks']}
        actual = {tuple(b['pos']): b['state'] for b in layout['blocks']}
        template = decode(template_path)
        assert set(actual) == set(expected) == set(template)
        ports = {tuple(p['pos']) for p in layout['ports']}
        assert len(ports) == len(layout['ports']) and ctrl not in ports
        for pos, state in expected.items():
            if pos == ctrl:
                assert actual[pos].split('[')[0] == meta['machine']
                assert template[pos] == meta['machine'] + '[facing=north]'
            elif pos in ports:
                assert actual[pos] == 'hk3gtl:industrial_port_casing'
                assert template[pos].startswith(('gtceu:', 'hk3gtl:industrial_port_casing'))
                assert 'creative' not in template[pos]
            else:
                assert actual[pos] == state == template[pos], (key, pos)
        rows.append({'key': key, 'controller': list(ctrl), 'size_xyz': layout['size'],
                     'blocks': len(actual), 'ports': len(ports), 'geometry_exact_outside_markers': True})
    expected_keys = {r['key'] for r in rows} | {f's{i:02}' for i in range(1, 6)}
    assert {p.stem for p in (DATA / 'approved_architecture').glob('*.json')} == expected_keys
    for key in sorted(k for k in expected_keys if k.startswith('s')):
        previous = source.parent / 'evidence/previous-formal-resources'
        for relative in [f'approved_architecture/{key}.json', f'structures/approved/{key}.json', f'structures/approved/{key}.nbt']:
            assert sha(DATA / relative) == sha(previous / relative), relative
    resources = {}
    with zipfile.ZipFile(JAR) as jar:
        assert jar.testzip() is None
        assert json.loads(jar.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 175
        for key in sorted(expected_keys):
            for relative in [f'approved_architecture/{key}.json', f'structures/approved/{key}.json', f'structures/approved/{key}.nbt']:
                archive_path = 'data/hk3gtl/' + relative
                expected = sha(DATA / relative)
                assert hashlib.sha256(jar.read(archive_path)).hexdigest() == expected, archive_path
                resources[archive_path] = expected
        for name in ['machine/Hk3IndustrialExtensionMachines', 'multiblock/pattern/Hk3IndustrialExtensionPatterns',
                     'research/Hk3IndustrialExtensionPolicy']:
            assert 'com/sirin/hk3gtl/common/' + name + '.class' in jar.namelist()
    receipt = {'status': 'passed', 'revision': 175, 'recorded_at': dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
               'jar': str(JAR), 'sha256': sha(JAR), 'approved_forms': len(rows), 'formal_forms': len(expected_keys),
               'formal_resource_files': len(resources), 'resources': resources, 'structures': rows,
               'approval_manifest': str(manifest_path), 'approval_manifest_sha256': sha(manifest_path),
               'approval_zip_sha256': approval_receipt['zip_sha256'], 'candidate_and_archive_unchanged': True,
               's01_s05_preserved': True, 'game_verified': False,
               'scope': '批准来源、正式几何、最终包和构建收据一致；游戏成型、配方运行与生存获取未验收。'}
    write(LOGS / 'package-verification.json', receipt)
    print(json.dumps({k: receipt[k] for k in ['status', 'revision', 'sha256', 'approved_forms', 'formal_forms', 'formal_resource_files']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
