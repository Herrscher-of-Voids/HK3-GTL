# -*- coding: utf-8 -*-
"""仅在目标实例停机且离线核验通过后安装积雪修复，保留回滚包及第三方内容。"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
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
    log = ROOT / 'logs/snow-clearance-r224-20261109'
    build = (log / 'build.log').read_text(encoding='utf8', errors='replace')
    assert 'BUILD SUCCESSFUL' in build and '> Task :snowClearanceTest' in build
    source = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
    instance = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
    target = instance / 'mods/HK3GTL-内测5.jar'
    guard = target_process_guard()
    with zipfile.ZipFile(source) as new, zipfile.ZipFile(target) as old:
        assert new.testzip() is None
        assert json.loads(new.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 224
        a = {p.filename:(p.CRC,p.file_size) for p in old.infolist()}
        b = {p.filename:(p.CRC,p.file_size) for p in new.infolist()}
        removed = sorted(set(a)-set(b))
        changed = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
        added = sorted(set(b)-set(a))
        assert not removed
        assert not any(k.startswith(('data/','assets/hk3gtl/models/scene/','assets/hk3gtl/textures/')) for k in changed)
        package = dict(passed=True, removed=removed, changed=changed, added=added,
                       unchanged_entries=sum(a[k]==b[k] for k in a.keys() & b.keys()),
                       bytes=source.stat().st_size, sha256=sha(source))
    third = {p.name:sha(p) for p in target.parent.glob('*.jar') if p != target}
    backup = log / 'r223-before-r224.jar'
    previous = sha(target)
    if not backup.exists():
        shutil.copy2(target,backup)
    assert sha(backup) == previous, '回滚包已存在且不匹配，停止重复安装'
    final_guard = target_process_guard()
    temporary = target.with_suffix('.r224-install')
    shutil.copy2(source,temporary)
    assert sha(temporary) == package['sha256']
    os.replace(temporary,target)
    assert sha(target) == package['sha256']
    assert third == {p.name:sha(p) for p in target.parent.glob('*.jar') if p != target}
    receipt = dict(installed=True, revision=224, installed_at=datetime.now(timezone.utc).isoformat(),
                   target=str(target), backup=str(backup), previous_sha256=previous,
                   installed_sha256=sha(target), guard=guard, final_guard=final_guard,
                   third_party_unchanged=True, third_party_jar_hashes=third,
                   game_formation_verified=False, cleanup_game_verified=False, implementation_test_passed=False)
    (log / 'package-verification.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (log / 'deployment.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:receipt[k] for k in ('installed','revision','installed_sha256','third_party_unchanged','implementation_test_passed')},ensure_ascii=False))


if __name__ == '__main__':
    main()
