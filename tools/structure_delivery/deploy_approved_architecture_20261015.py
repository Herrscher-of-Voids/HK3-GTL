"""变更记录 #1 · 2026-10-15 01:26:00 · 内测5修订156。
职责：向负责人指定的GTL十一周目部署已清理构建的HK3GTL，保留原包备份和逐文件收据。
输入：build/libs已重映射JAR、正式21组资源和成功构建日志；失败前置检查不修改实例。
仅将字节完全相同的重复gtmthings移入备份，其他依赖不更换；异常回滚已移动文件。
不启动游戏、不修改存档；部署和静态验收不能替代实际成型与配方运行。
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
GAME = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/GTL十一周目/minecraft'
MODS = GAME / 'mods'
SOURCE = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
RESOURCE = ROOT / 'src/main/resources'
LOG = ROOT / 'logs/approved-architecture-20261015'
stamp = datetime.now(timezone(timedelta(hours=8)))
tag = stamp.strftime('%Y%m%d_%H%M%S')
BACKUP = GAME / 'hk3gtl-mod-backups' / (tag + '_approved_architecture_r156')
DELIVERY = ROOT / 'deliveries' / ('四包最新结构_正式实装_R156_' + tag)

def sha(path):
    with path.open('rb') as stream:
        digest = hashlib.sha256()
        for part in iter(lambda: stream.read(1024*1024), b''):
            digest.update(part)
        return digest.hexdigest()

def mod_ids(path):
    with zipfile.ZipFile(path) as archive:
        if 'META-INF/mods.toml' not in archive.namelist():
            return []
        text = archive.read('META-INF/mods.toml').decode('utf-8')
        sections = re.findall(r'^\s*\[\[mods\]\]([^\[]*)', text, re.M)
        return [match.group(1) for section in sections
                for match in [re.search(r'^\s*modId\s*=\s*[\"\']([^\"\']+)', section, re.M)] if match]

def no_game_running():
    script = "@(Get-CimInstance Win32_Process -Filter \"Name='java.exe' OR Name='javaw.exe'\" | Where-Object { $_.CommandLine -match 'net\\.minecraft\\.client|forgeclient|cpw\\.mods\\.modlauncher|org\\.multimc\\.EntryPoint' }).Count"
    result = subprocess.run(['powershell.exe', '-NoProfile', '-Command', script], capture_output=True, text=True, check=True)
    if result.stdout.strip() != '0':
        raise RuntimeError('游戏进程尚未退出，拒绝替换模组')

def main():
    assert MODS.is_dir() and GAME.resolve().name == 'minecraft'
    cfg = GAME.parent / 'instance.cfg'
    assert 'GTL十一周目' in cfg.read_text(encoding='utf-8-sig')
    no_game_running()
    build_log = LOG / 'clean-build-final.log'
    assert 'BUILD SUCCESSFUL' in build_log.read_text(encoding='utf-8', errors='replace')
    assert mod_ids(SOURCE) == ['hk3gtl']
    keys = sorted(p.stem for p in (RESOURCE/'data/hk3gtl/approved_architecture').glob('*.json'))
    assert len(keys) == 21 and 'i14' not in keys
    paths = ['assets/hk3gtl/lang/zh_cn.json', 'assets/hk3gtl/lang/en_us.json', 'assets/hk3gtl/changelog.json']
    paths += [f'data/hk3gtl/{folder}/{key}.{ext}' for key in keys for folder,ext in
              [('approved_architecture','json'),('structures/approved','nbt'),('structures/approved','json')]]
    with zipfile.ZipFile(SOURCE) as archive:
        assert archive.testzip() is None
        for name in paths:
            assert archive.read(name) == (RESOURCE/name).read_bytes(), f'包内资源过时：{name}'
        for cls in ('Hk3IndustrialApprovedPatterns','Hk3ResearchInstitutePatterns'):
            assert f'com/sirin/hk3gtl/common/multiblock/pattern/{cls}.class' in archive.namelist()
    before = {p.name:sha(p) for p in MODS.glob('*.jar')}
    hk3 = [p for p in MODS.glob('*.jar') if 'hk3gtl' in mod_ids(p)]
    assert len(hk3) == 1, f'当前启用HK3GTL数量异常：{len(hk3)}'
    duplicates = [p for p in MODS.glob('*.jar') if 'gtmthings' in mod_ids(p)]
    assert len(duplicates) in (1,2)
    redundant = []
    if len(duplicates) == 2:
        assert all(sha(p) == '8c17567cd4a0ca231cc2cd19877b3ebd14693bdaeb643ffcbf205c2b9b67be36' for p in duplicates)
        redundant = [p for p in duplicates if p.name != '[GTMT]gtmthings-1.3.5.fix.jar']
        assert len(redundant) == 1
    source_sha = sha(SOURCE)
    BACKUP.mkdir(parents=True, exist_ok=False)
    DELIVERY.mkdir(parents=True, exist_ok=False)
    # 先保留完整原包，再写同磁盘暂存文件；暂存后重复核对游戏退出状态。
    for path in hk3 + redundant:
        assert path.resolve().parent == MODS.resolve()
        shutil.copy2(path, BACKUP/path.name)
        assert sha(BACKUP/path.name) == before[path.name]
    target = MODS / 'HK3GTL-内测5.jar'
    pending = MODS / ('hk3gtl-r156-' + tag + '.pending')
    assert not pending.exists()
    assert not target.exists() or target in hk3
    shutil.copy2(SOURCE, pending)
    assert sha(pending) == source_sha
    no_game_running()
    removed = []
    try:
        for path in hk3 + redundant:
            assert sha(path) == before[path.name]
            path.unlink()
            removed.append(path)
        os.replace(pending, target)
        assert sha(target) == source_sha
        after = {p.name:sha(p) for p in MODS.glob('*.jar')}
        for name,digest in before.items():
            if name not in {p.name for p in removed}:
                assert after.get(name) == digest, f'无关模组发生变化：{name}'
        assert len([p for p in MODS.glob('*.jar') if 'hk3gtl' in mod_ids(p)]) == 1
        assert len([p for p in MODS.glob('*.jar') if 'gtmthings' in mod_ids(p)]) == 1
    except Exception:
        if target.exists() and sha(target) == source_sha:
            target.unlink()
        for path in removed:
            shutil.copy2(BACKUP/path.name,path)
        raise
    shutil.copy2(SOURCE, DELIVERY/target.name)
    structure_dir = DELIVERY/'正式放置模板'
    structure_dir.mkdir()
    for key in keys:
        for ext in ('nbt','json'):
            shutil.copy2(RESOURCE/f'data/hk3gtl/structures/approved/{key}.{ext}',structure_dir/f'{key}.{ext}')
    receipt = {
        'time':stamp.isoformat(), 'timezone':'Asia/Hong_Kong', 'revision':156,
        'target_instance':str(GAME), 'installed_jar':str(target), 'jar_bytes':target.stat().st_size,
        'jar_sha256':source_sha, 'backup_directory':str(BACKUP), 'release_directory':str(DELIVERY),
        'replaced_hk3gtl':[{'file':p.name,'sha256':before[p.name]} for p in hk3],
        'deduplicated_identical_dependency':[{'file':p.name,'sha256':before[p.name],'reason':'与保留gtmthings逐字节相同，备份后移出启用目录'} for p in redundant],
        'unrelated_active_jars_unchanged':True, 'resource_exact_matches':len(paths),
        'machine_families':18, 'approved_forms':21, 'resource_keys':keys,
        'versions':{'I01-1..4':'V8','I02..I08':'V7','I09..I13':'V6','S01..S05':'V1'},
        'clean_build':'BUILD SUCCESSFUL', 'game_processes_before_deployment':0,
        'game_launched':False, 'in_game_formation_verified':False,
        'game_saves_modified':False, 'i14_deployed':False,
        'known_runtime_boundary':'S05严格空气体积1747305格，游戏成型及扫描性能尚未实测',
        'creative_placement_example':'/hk3structure place s01 ~ 100 ~',
        'placement_note':'命令需OP与创造模式，并且整个放置包围盒为空；内置模板不依赖WorldEdit或投影模组。',
        'before_active_jars':before, 'after_active_jars':after,
    }
    for folder in (LOG,BACKUP,DELIVERY):
        (folder/'deployment-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('before_active_jars','after_active_jars')},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
