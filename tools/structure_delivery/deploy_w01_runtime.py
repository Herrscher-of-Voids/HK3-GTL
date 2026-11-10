"""停妥目标实例后备份部署W01测试Jar与全新世界；不触碰其他玩家世界。"""
import hashlib
import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from deploy_industrial_build import target_process_guard

INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
OUT = ROOT / 'output/w01-runtime-20261029'
SOURCE = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
TARGET = INSTANCE / 'mods/HK3GTL-内测5.jar'
WORLD = INSTANCE / 'saves/hk3gtl-w01-azu-runtime-20261029'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'deployment.json').exists(), '已有部署收据，请检查实例当前状态，不能重复覆盖'
    assert TARGET.is_file() and SOURCE.is_file() and not WORLD.exists()
    exported = json.loads((OUT / 'world-export.json').read_text(encoding='utf-8'))
    assert exported['readback_passed'] and exported['blocks'] == 1933767
    guard = target_process_guard()
    assert guard['target_replace_allowed'], '目标增强版必须停止后再部署'
    with zipfile.ZipFile(SOURCE) as jar:
        assert 'com/sirin/hk3gtl/common/machine/Hk3W01Machines.class' in jar.namelist()
        assert 'data/hk3gtl/structures/w01_hall.bin.gz' in jar.namelist()
    others = {p.name: [p.stat().st_size, p.stat().st_mtime_ns] for p in TARGET.parent.iterdir() if p.is_file() and p != TARGET}
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = INSTANCE / 'hk3gtl-mod-backups' / (stamp + '_w01_azu_runtime')
    backup.mkdir(parents=True, exist_ok=False)
    shutil.copy2(TARGET, backup / TARGET.name)
    assert sha(backup / TARGET.name) == sha(TARGET)
    options = INSTANCE / 'options.txt'
    shutil.copy2(options, backup / 'options.txt')
    old_sha, new_sha = sha(TARGET), sha(SOURCE)
    guard_again = target_process_guard()
    assert guard_again['target_replace_allowed']
    shutil.copy2(SOURCE, TARGET)
    assert sha(TARGET) == new_sha
    shutil.copytree(OUT / 'world', WORLD)
    assert sha(WORLD / 'level.dat') == sha(OUT / 'world/level.dat')
    # 测试镜头只渲染附近区块；服务器实际检测区块由专用命令加载。
    values = {'renderDistance': '8', 'simulationDistance': '5', 'guiScale': '3', 'pauseOnLostFocus': 'false'}
    lines = options.read_text(encoding='utf-8').splitlines()
    lines = [key + ':' + values[key] if (key := line.split(':', 1)[0]) in values else line for line in lines]
    options.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    assert others == {p.name: [p.stat().st_size, p.stat().st_mtime_ns] for p in TARGET.parent.iterdir() if p.is_file() and p != TARGET}
    receipt = {'time_utc': datetime.now(timezone.utc).isoformat(), 'target': str(TARGET), 'backup': str(backup),
               'previous_jar_sha256': old_sha, 'installed_jar_sha256': new_sha, 'new_world': str(WORLD),
               'world_export_receipt': str(OUT / 'world-export.json'), 'third_party_jars_unchanged': True,
               'process_guards': [guard, guard_again], 'test_options': values, 'game_verified': False}
    (OUT / 'deployment.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
