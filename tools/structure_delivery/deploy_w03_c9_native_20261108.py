# -*- coding: utf-8 -*-
"""停机备份后安装C9原生特效试装包，保留第三方模组与原存档。"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import argparse
import json
import os
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from deploy_industrial_build import target_process_guard


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', type=int, default=221)
    revision = parser.parse_args().revision
    assert revision in (221, 222, 223)
    log = ROOT / 'logs/w03-c9-native-r221-20261108'
    build_log = (log / ('build.log' if revision == 221 else f'build-r{revision}.log')).read_text(encoding='utf8', errors='replace')
    assert 'BUILD SUCCESSFUL' in build_log and '> Task :nativeW03EffectsTest' in build_log
    source = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
    instance = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
    target = instance / 'mods/HK3GTL-内测5.jar'
    required = ['com/sirin/hk3gtl/client/wonder/Hk3W03FxRenderer.class',
                'com/sirin/hk3gtl/client/wonder/Hk3W03FxCommands.class',
                'assets/hk3gtl/models/scene/w03_c9.bin.gz',
                'assets/hk3gtl/models/scene/w03_c9.json',
                'assets/hk3gtl/textures/effect/w03_c9_atlas.png',
                'assets/hk3gtl/shaders/core/w03_c9.json']
    with zipfile.ZipFile(source) as jar:
        assert jar.testzip() is None
        assert all(p in jar.namelist() for p in required)
        change = json.loads(jar.read('assets/hk3gtl/changelog.json'))
        assert change['entries'][0]['revision'] == revision and source.stat().st_size > 50_000_000
    guard = target_process_guard()
    third = {p.name: sha(p) for p in target.parent.glob('*.jar') if p != target}
    backup = log / ('r220-before.jar' if revision == 221 else f'r{revision-1}-before-r{revision}.jar')
    previous = sha(target)
    if not backup.exists():
        shutil.copy2(target, backup)
    assert sha(backup) == previous, '已存在不同回滚包，停止重复部署'
    guard_final = target_process_guard()
    temporary = target.with_suffix('.c9-install')
    shutil.copy2(source, temporary)
    assert sha(source) == sha(temporary)
    os.replace(temporary, target)
    assert third == {p.name: sha(p) for p in target.parent.glob('*.jar') if p != target}
    receipt = dict(passed=True, installed_at=datetime.now(timezone.utc).isoformat(), revision=revision,
                   instance=str(instance), source=str(source), target=str(target), backup=str(backup),
                   source_sha256=sha(source), installed_sha256=sha(target), previous_sha256=previous,
                   bytes=target.stat().st_size, required_entries=required, zip_crc_passed=True,
                   guard=guard, final_guard=guard_final, third_party_jar_hashes=third,
                   third_party_unchanged=True, native_fx_installed=True, gameplay_verified=False,
                   scope='C9客户端原生特效试装；未注册W03整机Pattern，不授予研究或毕业资格。')
    (log / ('deployment.json' if revision == 221 else f'deployment-r{revision}.json')).write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({k: receipt[k] for k in ('passed','revision','bytes','installed_sha256','third_party_unchanged')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
