from datetime import datetime
from hashlib import sha256
from pathlib import Path
import json
import re
import shutil
import zipfile


ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w05-a4-runtime-20261115'
OUT = ROOT / 'deliveries/0005_W05_A4游戏接入_20261115'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
NAME = '0005多方块设计-0.5.0-W05A4-r1.jar'
RESOURCES = ['data/hk3gtl/structures/w05_candidate.bin.gz',
    'data/hk3gtl/structures/w05_approved.json']
QUOTE = '就这个吧，先实装到游戏，下一台W06吧'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def active_jars():
    result = []
    for path in (INSTANCE / 'mods').glob('*.jar'):
        with zipfile.ZipFile(path) as jar:
            if 'META-INF/mods.toml' not in jar.namelist():
                continue
            metadata = jar.read('META-INF/mods.toml').decode('utf8')
        records = re.findall(r'^\[\[mods\]\]\s*(.*?)(?=^\[\[|\Z)', metadata, re.M | re.S)
        if any(re.search(r'^modId\s*=\s*[\"\x27]hk3gtl[\"\x27]', record, re.M) for record in records):
            result.append(path)
    return result


def main():
    now = datetime.now().astimezone()
    OUT.mkdir(exist_ok=True)
    frozen_dir = LOG / 'frozen-base'
    frozen_dir.mkdir(exist_ok=True)
    current, = active_jars()
    base = frozen_dir / current.name
    shutil.copy2(current, base)
    base_sha = digest(base)
    updates = {name: (ROOT / 'src/main/resources' / name).read_bytes() for name in RESOURCES}
    artifact = OUT / NAME
    with zipfile.ZipFile(base) as source, zipfile.ZipFile(artifact, 'w',
            compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        existing = set(source.namelist())
        for info in source.infolist():
            target.writestr(info, updates[info.filename] if info.filename in updates else source.read(info.filename))
        for name in updates.keys() - existing:
            target.writestr(name, updates[name])
    with zipfile.ZipFile(base) as source, zipfile.ZipFile(artifact) as target:
        changed = [name for name in source.namelist() if source.read(name) != target.read(name)]
        added = sorted(set(target.namelist()) - set(source.namelist()))
        unchanged = len(source.namelist()) - len(changed)
        if set(changed + added) != set(RESOURCES):
            raise RuntimeError('叠包条目与W05资源清单不符：' + str(changed + added))
        metadata_sha = sha256(target.read('META-INF/mods.toml')).hexdigest()
    build = dict(created_at=now.isoformat(timespec='seconds'), conversation='0005',
        conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e', authorization=QUOTE,
        build_kind='冻结实际现用主包，只叠加两份W05生产资源；没有Java变更，不重复编译或重映射',
        base=str(base), base_installed_path=str(current), base_sha256=base_sha,
        artifact=str(artifact), sha256=digest(artifact), bytes=artifact.stat().st_size,
        changed_entries=changed, added_entries=added, unchanged_base_entries=unchanged,
        preserved_metadata_sha256=metadata_sha,
        resource_sha256={name: sha256(value).hexdigest() for name, value in updates.items()},
        java_changed=False, java_compilation_run=False, full_gradle_build_run=False,
        automated_tests_run=False, game_verified=False,
        parallel_scope='保留冻结时实际已安装主包的全部非W05条目；不宣称合入冻结后的其他对话更新')
    (LOG / 'build.json').write_text(json.dumps(build, ensure_ascii=False, indent=2) + '\n', 'utf8')
    current_now, = active_jars()
    if current_now != current or digest(current_now) != base_sha:
        raise RuntimeError('安装期间现用主包已由并行对话更新，需以新包重做本次资源叠包')
    backup = LOG / ('before-install-' + now.strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir()
    destination = INSTANCE / 'mods' / NAME
    staged = destination.with_suffix('.jar.pending')
    shutil.copy2(artifact, staged)
    shutil.move(str(current), str(backup / current.name))
    staged.replace(destination)
    installed_sha = digest(destination)
    if installed_sha != build['sha256']:
        raise RuntimeError('安装副本SHA256与候选不同')
    receipt = dict(build, installed_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        instance=str(INSTANCE), instance_version='增强版3.9（沿用当前统合R5安装基线）',
        target=str(destination), installed_sha256=installed_sha,
        replaced=[dict(path=str(current), backup=str(backup / current.name), sha256=base_sha)],
        active_hk3gtl_jars=[str(path) for path in active_jars()],
        registered_controller='hk3gtl:w05_ideal_fluid_circulation_array',
        blueprint_export='logs/0005-w05-a4-runtime-20261115/blueprint-export.json',
        approval_receipt='logs/0005-w05-a4-approval-20261115/receipt.json',
        appearance_approved=True, runtime_blueprint_integrated=True, installed=True,
        desktop_used=False, game_started=False, saves_modified=False,
        acceptance_score_changed=False, restart_required=True)
    encoded = json.dumps(receipt, ensure_ascii=False, indent=2) + '\n'
    (LOG / 'installation.json').write_text(encoded, 'utf8')
    (OUT / '安装回执.json').write_text(encoded, 'utf8')
    shutil.copy2(ROOT / 'src/main/resources' / RESOURCES[1], OUT / 'W05蓝图绑定.json')
    print(json.dumps(dict(installed=str(destination), sha256=installed_sha,
        changed=changed, added=added, unchanged=unchanged), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
