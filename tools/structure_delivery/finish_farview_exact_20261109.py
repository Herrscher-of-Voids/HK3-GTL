# -*- coding: utf-8 -*-
"""交付逐格远景修复，实例运行时保留原包；真实客户端画面验收不得由离屏回归替代。"""
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

LOG = ROOT / 'logs/farview-exact-r226-20261109'


def main():
    build = (LOG / 'build.log').read_text(encoding='utf8', errors='replace')
    tests = ['nativeFarExactTest', 'nativeFarViewTest', 'nativeFarViewMaskTest']
    assert 'BUILD SUCCESSFUL' in build and all('> Task :' + name in build for name in tests)
    graphics = json.loads((LOG / 'shader-gl-probe.json').read_text())
    assert graphics['passed'] and graphics['production_shader_compiled'] and not graphics['minecraft_client_test']
    source = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
    instance = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
    target = instance / 'mods/HK3GTL-内测5.jar'
    with zipfile.ZipFile(source) as new, zipfile.ZipFile(target) as old:
        assert new.testzip() is None
        assert json.loads(new.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 226
        assert 'client.Hk3FarProjectionMixin' in json.loads(new.read('hk3gtl.mixins.json'))['client']
        mappings = json.loads(new.read('hk3gtl-refmap.json'))['mappings']
        assert 'com/sirin/hk3gtl/mixin/client/Hk3FarProjectionMixin' in mappings
        shader = new.read('assets/hk3gtl/shaders/core/farview.fsh').decode()
        assert 'textureLod' in shader and 'NearLimit' in shader and 'Sampler1' in shader
        a = {p.filename: (p.CRC, p.file_size) for p in old.infolist()}
        b = {p.filename: (p.CRC, p.file_size) for p in new.infolist()}
        changed = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
        assert not set(a) - set(b)
        assert not any(k.startswith(('data/', 'assets/hk3gtl/models/', 'assets/hk3gtl/textures/')) for k in changed)
        package = dict(passed=True, changed=changed, added=sorted(set(b) - set(a)),
                       bytes=source.stat().st_size, sha256=sha(source), tests=tests,
                       unchanged_entries=sum(a[k] == b[k] for k in a.keys() & b.keys()))
    ready = LOG / 'HK3GTL-r226-ready.jar'
    if not ready.exists():
        shutil.copy2(source, ready)
    assert sha(ready) == package['sha256']
    write_json(LOG / 'package-verification.json', package)
    receipt = dict(revision=226, installed=False, target=str(target), ready=str(ready),
                   ready_sha256=package['sha256'], current_instance_sha256=sha(target))
    try:
        guard = target_process_guard()
    except RuntimeError as error:
        receipt['pending_reason'] = str(error)
    else:
        third = {p.name: sha(p) for p in target.parent.glob('*.jar') if p != target}
        backup = LOG / 'r225-before-r226.jar'
        if not backup.exists():
            shutil.copy2(target, backup)
        assert sha(backup) == sha(target), '回滚包与当前实例不同，禁止重复覆盖历史'
        try:
            final_guard = target_process_guard()
        except RuntimeError as error:
            receipt['pending_reason'] = str(error)
        else:
            temporary = target.with_suffix('.r226-install')
            shutil.copy2(ready, temporary)
            assert sha(temporary) == package['sha256']
            os.replace(temporary, target)
            assert sha(target) == package['sha256']
            assert third == {p.name: sha(p) for p in target.parent.glob('*.jar') if p != target}
            receipt.update(installed=True, installed_at=datetime.now(timezone.utc).isoformat(), guard=guard,
                           final_guard=final_guard, backup=str(backup), installed_sha256=sha(target),
                           third_party_unchanged=True, third_party_jar_hashes=third)
    write_json(LOG / 'deployment.json', receipt)

    report = ROOT / 'logs/beta5-completion-audit-20261030'
    paths = [report / 'index.html', report / 'current-summary.json']
    before = {p: p.read_bytes() for p in paths}
    now = datetime.now(timezone.utc)
    history = LOG / ('before-report-' + now.strftime('%Y%m%dT%H%M%S%fZ'))
    history.mkdir()
    for p, value in before.items():
        (history / p.name).write_bytes(value)
    data = json.loads(before[paths[1]])
    previous = deepcopy(data)
    installed = receipt['installed']
    status = 'r226构建、离线与离屏图形回归通过；已停机安装，客户端画面与整机仍待验' if installed else 'r226构建、离线与离屏图形回归通过；实例运行中，修复包已备妥，未替换当前JAR'
    evidence = dict(revision=226, updated_at=now.isoformat(), status=status,
        trigger='负责人提供两张客户端截图：粗块变形、材质色块和交叠闪烁；旧远景不能按验收通过处理。',
        user_screenshots=['logs/farview-exact-r226-20261109/user-rendering-issue-1.png',
                          'logs/farview-exact-r226-20261109/user-rendering-issue-2.png'],
        causes=['8格立方粗采样扩大薄壁并填平空隙。', '远景私有投影与真实方块共用深度缓冲导致深度值不一致。',
                '二维近景遮罩错误覆盖高处区域，跨分区重复面及缺少材质LOD可能加重边界和闪烁。'],
        changes=['16³逐格局部调色板缓存；完整立方体合面，其余读取真实静态烘焙面。',
                 '真实面材质图集与5级mipmap，玻璃独立透明通道；邻接区块剔除内部面。',
                 'GameRenderer.getDepthFar客户端Mixin统一原版/远景投影；交接深度偏移与三维近景范围。',
                 '单后台网格工作线程与一项等候队列；分帧上传、显存限额及较远缓存回收。',
                 '旧缓存只定位历史区域，每tick最多重读一个已加载分区，不强加载、不要求拆除重建。'],
        protocol_version=31, farview_distance_blocks=2048, gpu_vertex_budget_mib=32,
        static_material_atlas_mib_upper_bound=5.34, section_limit=8192,
        build_passed=True, offline_tests=tests, graphics_probe=graphics, installed=installed,
        ready_jar=str(ready), jar_bytes=package['bytes'], jar_sha256=package['sha256'],
        build_evidence='logs/farview-exact-r226-20261109/build.log',
        graphics_evidence='logs/farview-exact-r226-20261109/shader-gl-probe.json',
        deployment_evidence='logs/farview-exact-r226-20261109/deployment.json',
        game_farview_verified=False, game_performance_verified=False, game_formation_verified=False,
        implementation_test_passed=False,
        limitations=['静态远景不复制方块实体的动态内容或世界依赖的连接模型数据。',
                     '达到分区或显存限额时优先保留较近范围，不承诺所有巨构同时完整驻留。',
                     '离屏OpenGL只验证生产着色器，不替代增强版3.5客户端、低端设备、性能与整机验收。'],
        remaining='停机替换后在增强版3.5复核负责人两处视角、移动交接、旧缓存重读、完整巨构可见性及帧时间；系统分数与范围保留。')
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    system['farview_exact_surface_fix'] = deepcopy(evidence)
    system['updated_at'] = now.isoformat()
    data['current_work']['farview_exact_surface_fix'] = deepcopy(evidence)
    for container in (system, data['current_work']):
        if 'terminal_async_farview_fix' in container:
            container['terminal_async_farview_fix']['client_render_issue_reported'] = True
            container['terminal_async_farview_fix']['farview_followup_revision'] = 226
    data['systems'].sort(key=lambda s: s['percent'])
    data['report_updated_at'] = now.isoformat()
    assert data['overall_percent'] == previous['overall_percent']
    assert [(s['id'], s['percent']) for s in data['systems']] == [(s['id'], s['percent']) for s in previous['systems']]
    html = before[paths[0]].decode('utf8')
    notice = '<p class="notice" id="r226-exact-farview">2026-11-09 · r226：撤换8格粗采样，改逐格实际静态面/材质；统一投影深度，修复远近交叠与高处遮罩。' + status + '。负责人原图已归档，未通过客户端画面、性能或完整实装验收；系统分数保留。</p>'
    if 'id="r226-exact-farview"' in html:
        html, n = re.subn(r'<p class="notice" id="r226-exact-farview">.*?</p>', lambda _: notice, html, count=1, flags=re.S)
    else:
        html, n = re.subn(r'(</h1>)', lambda m: m[1] + notice, html, count=1)
    assert n == 1
    html, n = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + now.isoformat() + ' · 逐格真实表面远景修复</p>', html, count=1)
    assert n == 1
    html, n = re.subn(r'(?<=id="audit-data">).*?(?=</script>)', lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S)
    assert n == 1
    publisher().publish_transaction({paths[0]: html, paths[1]: json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, before)
    write_json(LOG / 'verification.json', evidence)
    print(status)


if __name__ == '__main__':
    main()
