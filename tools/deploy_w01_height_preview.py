"""W01高度与JEI修复的停机部署；只选择独立测试档，保存整档回滚副本。

【变更记录 #1】2026-10-29 23:11:10（修订182）
删除：无；新增：包身份、完整测试档备份、配置精确名单及第三方JAR不变校验。
修改：只替换HK3GTL并将新世界模式改为全部启用；用途：部署不等于实机验收。
"""
import hashlib
import json
import os
import re
import shutil
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from deploy_industrial_build import target_process_guard

ROOT = Path(__file__).resolve().parents[1]
GAME = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
SOURCE = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
TARGET = GAME / 'mods/HK3GTL-内测5.jar'
CONFIG = GAME / 'config/hk3gtl-height-common.toml'
WORLD = GAME / 'saves/W01-Terminal-Void-1029'
OUTPUT = ROOT / 'logs/w01-height-jei-20261029/deployment.json'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def tree(path):
    files = list(path.rglob('*'))
    if any(item.is_symlink() for item in files):
        raise RuntimeError('测试档含符号链接，拒绝自动复制')
    return {item.relative_to(path).as_posix(): sha(item) for item in files if item.is_file()}


def main():
    guards = [target_process_guard()]
    assert json.loads((GAME.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId'] == '2.9.2'
    with zipfile.ZipFile(SOURCE) as jar:
        assert jar.testzip() is None
        assert json.loads(jar.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 182
        for name in ('common/dimension/height/Hk3HeightWorldUpgrade',
                     'common/multiblock/build/Hk3W01TerminalBuilder',
                     'client/preview/Hk3W01PreviewWorld'):
            assert 'com/sirin/hk3gtl/' + name + '.class' in jar.namelist(), name
        assert jar.read('data/hk3gtl/structures/w01_hall.bin.gz') == (ROOT / 'src/main/resources/data/hk3gtl/structures/w01_hall.bin.gz').read_bytes()
        for locale in ('zh_cn', 'en_us'):
            assert jar.read('assets/hk3gtl/lang/' + locale + '.json') == (ROOT / 'src/main/resources/assets/hk3gtl/lang' / (locale + '.json')).read_bytes()
    config = CONFIG.read_text(encoding='utf-8-sig')
    assert re.search(r'^topExclusive\s*=\s*1024\s*$', config, re.M)
    existing = re.search(r'^existingWorlds\s*=\s*(.*)$', config, re.M)
    assert existing is None or existing.group(1).strip() in ('[]', '["W01-Terminal-Void-1029"]')
    updated, count = re.subn(r'^newWorldMode\s*=.*$', 'newWorldMode = "ALL_NEW_WORLDS"', config, flags=re.M)
    assert count == 1
    if existing:
        updated = re.sub(r'^existingWorlds\s*=.*$', 'existingWorlds = ["W01-Terminal-Void-1029"]', updated, flags=re.M)
    else:
        updated += '\n# 仅选择本轮已授权的独立创造测试档；其他旧档不自动升级。\nexistingWorlds = ["W01-Terminal-Void-1029"]\n'
    now = datetime.now(timezone(timedelta(hours=8)))
    backup = GAME / 'hk3gtl-mod-backups' / (now.strftime('%Y%m%d_%H%M%S_%f') + '_w01_height_jei_r182')
    backup.mkdir(parents=True, exist_ok=False)
    before = {item.name: sha(item) for item in TARGET.parent.glob('*.jar')}
    world_before = tree(WORLD)
    shutil.copy2(TARGET, backup / TARGET.name)
    shutil.copy2(CONFIG, backup / CONFIG.name)
    shutil.copytree(WORLD, backup / WORLD.name)
    assert tree(backup / WORLD.name) == world_before == tree(WORLD)
    assert sha(backup / TARGET.name) == before[TARGET.name]
    assert sha(backup / CONFIG.name) == sha(CONFIG)
    pending = TARGET.with_suffix('.w01-height-pending')
    pending_config = CONFIG.with_suffix('.w01-height-pending')
    assert not pending.exists() and not pending_config.exists(), '存在未完成的部署，须先核对'
    shutil.copy2(SOURCE, pending)
    pending_config.write_text(updated, encoding='utf-8')
    expected = sha(SOURCE)
    assert sha(pending) == expected
    guards.append(target_process_guard())
    os.replace(pending, TARGET)
    os.replace(pending_config, CONFIG)
    after = {item.name: sha(item) for item in TARGET.parent.glob('*.jar')}
    assert after.keys() == before.keys()
    assert all(after[name] == digest for name, digest in before.items() if name != TARGET.name)
    assert sha(TARGET) == expected
    assert tree(WORLD) == world_before, '部署不得离线改写存档'
    receipt = dict(time=now.isoformat(), revision=182, target=str(TARGET), backup=str(backup),
                   sha256=expected, previous_sha256=before[TARGET.name], configuration=str(CONFIG),
                   configuration_sha256=sha(CONFIG), selected_existing_world=WORLD.name,
                   world_backup_files=len(world_before), world_unchanged_by_deployment=True,
                   third_party_jars_unchanged=True, process_guards=guards,
                   original_layout_changed=False, physics_changed=False, runtime_verified=False)
    OUTPUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
