# -*- coding: utf-8 -*-
"""核验r225产物，停机时安装，并将事实同步到固定审计入口。"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile

from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from deploy_industrial_build import target_process_guard

LOG = ROOT / 'logs/terminal-async-farview-r225-20261109'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    build = (LOG / 'build.log').read_text(encoding='utf8', errors='replace')
    assert 'BUILD SUCCESSFUL' in build
    tests = ['asyncBuildPreparationTest', 'nativeFarViewMaskTest', 'nativeFarViewTest', 'runUniversalBuildOrderTest']
    assert all('> Task :' + name in build for name in tests)
    source = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
    instance = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
    target = instance / 'mods/HK3GTL-内测5.jar'
    with zipfile.ZipFile(source) as new, zipfile.ZipFile(target) as old:
        assert new.testzip() is None
        assert json.loads(new.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 225
        hooks = json.loads(new.read('hk3gtl-refmap.json'))['mappings']['com/sirin/hk3gtl/mixin/gtceu/Hk3HyperionHullChangeMixin']
        assert any('LevelChunk;m_6978_' in value for value in hooks.values())
        a = {p.filename: (p.CRC, p.file_size) for p in old.infolist()}
        b = {p.filename: (p.CRC, p.file_size) for p in new.infolist()}
        changed = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
        assert not set(a) - set(b)
        assert not any(k.startswith(('data/', 'assets/hk3gtl/models/', 'assets/hk3gtl/textures/')) for k in changed)
        package = dict(passed=True, changed=changed, added=sorted(set(b) - set(a)),
                       unchanged_entries=sum(a[k] == b[k] for k in a.keys() & b.keys()),
                       bytes=source.stat().st_size, sha256=sha(source), tests=tests)
    write_json(LOG / 'package-verification.json', package)
    receipt = dict(installed=False, revision=225, target=str(target), source_sha256=package['sha256'])
    try:
        guard = target_process_guard()
    except RuntimeError as error:
        receipt['pending_reason'] = str(error)
    else:
        third = {p.name: sha(p) for p in target.parent.glob('*.jar') if p != target}
        backup = LOG / 'r224-before-r225.jar'
        previous = sha(target)
        if not backup.exists():
            shutil.copy2(target, backup)
        assert sha(backup) == previous, '既有回滚包与待替换版本不符，禁止覆盖历史'
        try:
            final_guard = target_process_guard()
        except RuntimeError as error:
            receipt['pending_reason'] = str(error)
        else:
            temporary = target.with_suffix('.r225-install')
            shutil.copy2(source, temporary)
            assert sha(temporary) == package['sha256']
            os.replace(temporary, target)
            assert sha(target) == package['sha256']
            assert third == {p.name: sha(p) for p in target.parent.glob('*.jar') if p != target}
            receipt.update(installed=True, installed_at=datetime.now(timezone.utc).isoformat(), backup=str(backup),
                           previous_sha256=previous, installed_sha256=sha(target), guard=guard,
                           final_guard=final_guard, third_party_unchanged=True, third_party_jar_hashes=third)
    write_json(LOG / 'deployment.json', receipt)

    report = ROOT / 'logs/beta5-completion-audit-20261030'
    paths = [report / 'index.html', report / 'current-summary.json']
    before = {p: p.read_bytes() for p in paths}
    now = datetime.now(timezone.utc)
    backup = LOG / ('before-report-' + now.strftime('%Y%m%dT%H%M%S%fZ'))
    backup.mkdir()
    for p, value in before.items():
        (backup / p.name).write_bytes(value)
    data = json.loads(before[paths[1]])
    previous = deepcopy(data)
    installed = receipt['installed']
    status = 'r225代码与离线回归通过；已停机安装，重启生效，客户端实测待验' if installed else 'r225代码与离线回归通过；实例运行或身份不明，尚未安装与实测'
    evidence = dict(revision=225, updated_at=now.isoformat(), status=status,
        threads='有界2线程/4排队任务；解码和稳定排序在后台，世界读写/保护/材料事务仍在主线程。',
        lifecycle='完成交接前独占蓝图，取消不阻塞主线程、不并发关闭输入；清理后才发布完成结果。',
        chunk_prefetch='二分定位阶段/区块边界，最多4个FULL区块票据，不强加载整舰。',
        farview_fix='RenderSystem绑定遮罩槽，避免VertexBuffer覆盖；只遮蔽实际绘制半径内的已加载区块。',
        farview_distance_blocks=2048, farview_gpu_budget_mib=32, farview_status_command='/hk3farview status',
        farview_scope='本模组已实读的静态建筑外观；不扩大地形模拟距离，不渲染未知蓝图，不加入其他模组。',
        daylight_fix='仅忽略日光探测器POWER自然变化；INVERTED、其他方块状态及材料继续精确核验。',
        build_passed=True, offline_regression_passed=True, tests=tests, installed=installed,
        build_evidence='logs/terminal-async-farview-r225-20261109/build.log',
        deployment_evidence='logs/terminal-async-farview-r225-20261109/deployment.json',
        jar_sha256=package['sha256'], jar_bytes=package['bytes'],
        game_build_speed_verified=False, game_farview_verified=False, game_formation_verified=False,
        implementation_test_passed=False,
        remaining='增强版3.5重启后核验真实整舰扫描、日光变化前后成型、远景画面和建造耗时/帧时间；不改既定系统分数与范围。')
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    system['terminal_async_farview_fix'] = deepcopy(evidence)
    system['updated_at'] = now.isoformat()
    data['current_work']['terminal_async_farview_fix'] = deepcopy(evidence)
    data['systems'].sort(key=lambda s: s['percent'])
    data['report_updated_at'] = now.isoformat()
    assert data['overall_percent'] == previous['overall_percent']
    assert [(s['id'], s['percent']) for s in data['systems']] == [(s['id'], s['percent']) for s in previous['systems']]
    html = before[paths[0]].decode('utf8')
    notice = '<p class="notice" id="r225-terminal-farview">2026-11-09 · r225：终端后台解码/排序、有限区块预取提速、原生2048格巨构远景遮罩修复及日光探测器亮度误报修复。' + status + '。完整实装测试尚未通过，系统分数与既定范围保留。</p>'
    if 'id="r225-terminal-farview"' in html:
        html, n = re.subn(r'<p class="notice" id="r225-terminal-farview">.*?</p>', lambda _: notice, html, count=1, flags=re.S)
    else:
        html, n = re.subn(r'(</h1>)', lambda m: m[1] + notice, html, count=1)
    assert n == 1
    html, n = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + now.isoformat() + ' · 终端线程与原生远景修复</p>', html, count=1)
    assert n == 1
    html, n = re.subn(r'(?<=id="audit-data">).*?(?=</script>)', lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S)
    assert n == 1
    publisher().publish_transaction({paths[0]: html, paths[1]: json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, before)
    write_json(LOG / 'verification.json', evidence)
    print(status)


if __name__ == '__main__':
    main()
