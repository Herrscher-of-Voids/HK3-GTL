# -*- coding: utf-8 -*-
"""停机安装雾距修复，按独立客户端证据更新固定审计。"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import shutil
import zipfile

from finish_terminal_farview_20261109 import ROOT, sha, write_json, target_process_guard
from max_structure_review import publisher

LOG = ROOT / 'logs/farview-fog-r228-20261109'


def main():
    build = (LOG / 'build.log').read_text(encoding='utf8', errors='replace')
    assert 'BUILD SUCCESSFUL' in build
    source = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
    baseline = ROOT / 'logs/farview-batch-r227-20261109/HK3GTL-r227-ready.jar'
    ready = LOG / 'HK3GTL-r228-ready.jar'
    with zipfile.ZipFile(source) as new, zipfile.ZipFile(baseline) as old:
        assert new.testzip() is None
        assert json.loads(new.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 228
        a = {p.filename: (p.CRC, p.file_size) for p in old.infolist()}
        b = {p.filename: (p.CRC, p.file_size) for p in new.infolist()}
        changed = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
        assert not set(a) - set(b)
        assert not any(k.startswith(('data/', 'assets/hk3gtl/models/', 'assets/hk3gtl/textures/')) for k in changed)
    if not ready.exists():
        shutil.copy2(source, ready)
    assert sha(ready) == sha(source)
    write_json(LOG / 'package-verification.json', dict(passed=True, changed=changed,
        added=sorted(set(b) - set(a)), sha256=sha(ready), bytes=ready.stat().st_size))
    target = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/GregTech Leisure-增强版/minecraft/mods/HK3GTL-内测5.jar'
    receipt_path = LOG / 'deployment.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text(encoding='utf8'))
        assert receipt['installed_sha256'] == sha(target) == sha(ready)
    else:
        guard = target_process_guard()
        assert sha(target) == sha(baseline)
        third = {p.name: sha(p) for p in target.parent.glob('*.jar') if p != target}
        backup = LOG / 'r227-before-r228.jar'
        assert not backup.exists()
        shutil.copy2(target, backup)
        final_guard = target_process_guard()
        temporary = target.with_suffix('.r228-install')
        shutil.copy2(ready, temporary)
        assert sha(temporary) == sha(ready)
        os.replace(temporary, target)
        assert sha(target) == sha(ready)
        assert third == {p.name: sha(p) for p in target.parent.glob('*.jar') if p != target}
        receipt = dict(installed=True, revision=228, installed_at=datetime.now(timezone.utc).isoformat(),
            target=str(target), backup=str(backup), installed_sha256=sha(target), guard=guard,
            final_guard=final_guard, third_party_unchanged=True, third_party_jar_hashes=third)
        write_json(receipt_path, receipt)
    result_path = LOG / 'client-results.json'
    result = json.loads(result_path.read_text(encoding='utf8')) if result_path.exists() else {}
    evidence = dict(revision=228, updated_at=datetime.now(timezone.utc).isoformat(),
        build_passed=True, installed=True, source_world_modified=False,
        reason='r227在4区块真实客户端发现近景原版雾遮盖表面，远景受深度测试阻挡而不能补画。',
        defect_screenshot='logs/farview-fog-r228-20261109/client-before-fog-seam.png',
        changes=['只统一启用远景且有当前维度缓存时的普通地形雾距，不扩大加载或模拟距离。',
                 '保留水、岩浆、细雪、失明、黑暗、维度浓雾、Boss雾与其他已取消事件。'],
        client_results=result, game_farview_verified=result.get('visual_checks_passed', False),
        game_performance_verified=result.get('performance_checks_passed', False),
        game_formation_verified=False, implementation_test_passed=False,
        status=result.get('status', 'r228雾距修复构建通过并已停机安装，准备同机位4区块客户端复测。'),
        evidence='logs/farview-fog-r228-20261109/client-results.json',
        remaining=result.get('remaining', '同机位雾距交接、移动与重载待实测；低端设备、建造中性能及完整机器实装另验。'))
    write_json(LOG / 'verification.json', evidence)
    report = ROOT / 'logs/beta5-completion-audit-20261030'
    paths = [report / 'index.html', report / 'current-summary.json']
    before = {p: p.read_bytes() for p in paths}
    history = LOG / ('before-report-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    history.mkdir()
    for path, value in before.items():
        (history / path.name).write_bytes(value)
    data = json.loads(before[paths[1]])
    old = deepcopy(data)
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    for container in (system, data['current_work']):
        container['farview_fog_client_fix'] = deepcopy(evidence)
        container['farview_batch_client_fix']['fog_followup_revision'] = 228
        container['farview_batch_client_fix']['native_fog_seam_found'] = True
    system['updated_at'] = evidence['updated_at']
    data['report_updated_at'] = evidence['updated_at']
    data['systems'].sort(key=lambda s: s['percent'])
    assert data['overall_percent'] == old['overall_percent']
    assert [(s['id'], s['percent'], s['earned'], s['possible']) for s in data['systems']] == [(s['id'], s['percent'], s['earned'], s['possible']) for s in old['systems']]
    assert all(s == o for s, o in zip(data['systems'], old['systems']) if s['id'] != 'multiblocks')
    html = before[paths[0]].decode('utf8')
    notice = '<p class="notice" id="r228-fog-client">2026-11-09 · ' + evidence['status'] + ' 系统分数、74项范围与批准台账保留。</p>'
    if 'id="r228-fog-client"' in html:
        html, count = re.subn(r'<p class="notice" id="r228-fog-client">.*?</p>', lambda _: notice, html, count=1, flags=re.S)
    else:
        html, count = re.subn(r'(</h1>)', lambda m: m[1] + notice, html, count=1)
    assert count == 1
    html, count = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + evidence['updated_at'] + ' · 远景客户端画面与性能复查</p>', html, count=1)
    assert count == 1
    html, count = re.subn(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S)
    assert count == 1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>', html, flags=re.S)[1]) == data
    publisher().publish_transaction({paths[0]: html, paths[1]: json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, before)
    print(json.dumps(dict(status=evidence['status'], installed_sha256=sha(target)), ensure_ascii=False))


if __name__ == '__main__':
    main()
