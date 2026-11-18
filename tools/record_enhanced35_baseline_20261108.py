# -*- coding: utf-8 -*-
"""记录负责人确认的增强版3.5实例，磁盘核对不冒充客户端兼容验收。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
from max_structure_review import publisher

LOG = ROOT / 'logs/enhanced35-baseline-20261108'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
GAME = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/GregTech Leisure-增强版/minecraft'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text('utf8'))
def dump(value): return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def main():
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    tracked = [REPORT / 'index.html', REPORT / 'current-summary.json', ROOT / 'AGENTS.md', ROOT / 'rule/崩坏三-gtl (hk3gtl) 项目规则.md']
    original = {p: p.read_bytes() for p in tracked}
    before = LOG / 'before'
    if before.exists():
        before = LOG / ('refresh-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')) / 'before'
    before.mkdir(parents=True, exist_ok=False)
    snapshots = dict(original)
    for name in ('instance-inspection.json', 'publication-verification.json'):
        p = LOG / name
        if p.exists():
            snapshots[p] = p.read_bytes()
    for p, content in snapshots.items():
        target = before / p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    components = {c['uid']: c['version'] for c in load(GAME.parent / 'mmc-pack.json')['components']}
    assert components['net.minecraft'] == '1.20.1' and components['net.minecraftforge'] == '47.4.16'
    files = sorted((GAME / 'mods').glob('*.jar'))
    prefixes = ['gtceu-', 'gtlcore-', 'GTL-Enhancedcore-', 'gtladditions-', 'appliedenergistics2-',
                'ExtendedAE-', 'extendedae_plus-', 'extendedae_plus_gtladd-', 'HK3GTL-', 'Spear_of_Void-']
    selected = []
    for prefix in prefixes:
        matches = [p for p in files if p.name.startswith(prefix)]
        if prefix == 'extendedae_plus-':
            matches = [p for p in matches if not p.name.startswith('extendedae_plus_gtladd-')]
        assert len(matches) == 1, (prefix, [p.name for p in matches])
        p = matches[0]
        selected.append(dict(file=p.name, path=str(p), bytes=p.stat().st_size, sha256=sha(p)))
    installed = next(p for p in selected if p['file'].startswith('HK3GTL-'))
    release = load(ROOT / 'logs/w01-terminal-bounds-20261108/release.json')
    same_release = installed['sha256'] == release['sha256']
    previous_inspection = load(LOG / 'instance-inspection.json') if (LOG / 'instance-inspection.json').exists() else None
    changes = []
    if previous_inspection:
        previous_jars = previous_inspection['key_dependencies']
        for prefix, dependency in zip(prefixes, selected):
            old_dependency = next((p for p in previous_jars if p['file'].startswith(prefix)), None)
            if old_dependency and old_dependency['sha256'] != dependency['sha256']:
                changes.append(dict(previous=old_dependency, current=dependency))
    evidence = dict(checked_at=now, user_confirmed_pack_version='3.5',
        version_source='负责人本轮明确说明增强版已更新3.5并安装；启动器目录名称不含版本号。',
        game_directory=str(GAME), launcher_components=components,
        enabled_jar_count=len(files), key_dependencies=selected,
        installed_hk3gtl_revision=release['revision'] if same_release else None,
        installed_hk3gtl_matches_r220=same_release,
        previous_inspection_backup=str((before / (LOG / 'instance-inspection.json').relative_to(ROOT)).relative_to(ROOT)).replace('\\', '/') if previous_inspection else None,
        dependency_changes_since_previous=changes,
        inspection_scope='只读核对实例组件、JAR存在性和SHA256；未启动或操控游戏，未写入实例、模组或存档。',
        compatibility_accepted=False, client_tested=False)
    (LOG / 'instance-inspection.json').write_text(dump(evidence), 'utf8')
    old = json.loads(original[REPORT / 'current-summary.json']); data = deepcopy(old)
    target = dict(version='GTL增强版3.5', installed=True, game_directory=str(GAME),
        version_source='负责人确认升级至3.5；实例关键依赖离线核对',
        evidence=str((LOG / 'instance-inspection.json').relative_to(ROOT)).replace('\\', '/'),
        game_verified=False, runtime_memory_acceptance=False, terminal_dismantle_acceptance=False,
        game_verification_scope='3.5尚未进行客户端验收；3.0与更早版本的实测证据保留于history，不能自动转记。',
        history=deepcopy(old['target_instance'].get('history', {})) if old['target_instance'].get('version') == 'GTL增强版3.5' else deepcopy(old['target_instance']), updated_at=now)
    if same_release:
        target['revision'] = release['revision']
    data['target_instance'] = target
    data['current_work']['compatibility_target'] = dict(version='GTL增强版3.5',
        evidence=target['evidence'], state='后续兼容与实机测试目标；当前实例关键依赖已核对，升级后运行兼容尚未验收。',
        inspected_key_dependencies=[p['file'] for p in selected], updated_at=now)
    data['report_updated_at'] = now
    data['systems'].sort(key=lambda s: s['percent'])
    assert data['systems'] == old['systems'] and data['overall_percent'] == old['overall_percent']
    assert data['multiblock_scope'] == old['multiblock_scope']
    assert all(data['current_work'][k] == v for k, v in old['current_work'].items() if k != 'compatibility_target')
    state = ('2026-11-08 · 负责人确认增强版3.5已安装，后续测试以3.5为准。原实例路径沿用；只读核对MC 1.20.1／Forge 47.4.16及当前关键JAR的SHA256：'
             + '、'.join(p['file'] for p in selected[:4])
             + '；AE与样板总成相关依赖一并核对。旧基线已保存历史，3.0实测保留原版本来源；3.5兼容、成型、配方与性能尚未客户端验收。既有系统分数、完成度、74项范围与批准数量保持。')
    html = original[REPORT / 'index.html'].decode('utf8')
    html, count = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + now + ' · 增强版3.5测试基线</p>', html, count=1)
    assert count == 1
    anchor = '<main><h1>系统完成度 · 低到高 · 固定入口</h1>'
    assert anchor in html
    notice = '<p class="notice" id="enhanced35-target">' + state + '</p>'
    if 'id="enhanced35-target"' in html:
        html, count = re.subn(r'<p class="notice" id="enhanced35-target">.*?</p>', lambda _: notice, html, count=1, flags=re.S)
        assert count == 1
    else:
        html = html.replace(anchor, anchor + notice, 1)
    html, count = re.subn(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S)
    assert count == 1 and json.loads(re.search(r'id="audit-data">(.*?)</script>', html, re.S)[1]) == data
    assert re.findall(r'<details class="system" data-id="([^"]+)"', html) == [s['id'] for s in data['systems']]
    rule_note = '''

## 2026-11-08 测试实例更新至增强版3.5（负责人最新通知）

- 负责人明确说明“增强版更新到3.5了，已经安装到实例里了”；后续兼容检查、真实资源解析与实机测试以增强版3.5为目标，覆盖旧3.0目标版本安排，原历史记录不改写。
- 唯一目标实例路径继续为 `C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft`；本轮只读确认MC 1.20.1、Forge 47.4.16及GTCEu、GTL、AE和终极样板总成相关JAR。版本3.5依据负责人确认，证据为 `logs/enhanced35-baseline-20261108/instance-inspection.json`。
- 此次记录不等于3.5启动、成型、配方、研究门槛或性能验收；3.0实测继续保留原版本来源，不自动转记为3.5通过。W03 C7与W02 V3仍为各自候选状态，未因此批准或部署；现有系统分数、既定74项与批准／正式数量保持。
'''
    updates = {REPORT / 'index.html': html, REPORT / 'current-summary.json': dump(data)}
    for p in tracked[2:]:
        source = original[p].decode('utf8')
        updates[p] = source if '## 2026-11-08 测试实例更新至增强版3.5' in source else source + rule_note
    publisher().publish_transaction(updates, original)
    result = dict(passed=True, target_version='GTL增强版3.5', key_jars=len(selected),
        installed_hk3gtl_revision=target.get('revision'), all_36_system_scores_unchanged=True,
        overall_percent=data['overall_percent'], original_work_preserved=True,
        dependency_changes=len(changes), baseline_backup=str(before.relative_to(ROOT)).replace('\\', '/'),
        html_json_consistent=True, ascending_order=True, client_tested=False)
    (LOG / 'publication-verification.json').write_text(dump(result), 'utf8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
