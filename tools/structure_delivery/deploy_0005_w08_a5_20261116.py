from datetime import datetime
from hashlib import sha256
from pathlib import Path
from copy import copy
import json
import re
import shutil
import zipfile


ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w08-a5-runtime-20261116'
OUT = ROOT / 'deliveries/0005_W08_A5游戏接入_20261116'
INSTANCE = Path('E:/Prism/instances/GregTech Leisure-增强版/minecraft')
VERSION = '0.5.0-W08A5-r1'
NAME = '0005多方块设计-' + VERSION + '.jar'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def active_jars():
    result = []
    for path in (INSTANCE / 'mods').glob('*.jar'):
        with zipfile.ZipFile(path) as jar:
            if 'META-INF/mods.toml' not in jar.namelist():
                continue
            metadata = jar.read('META-INF/mods.toml').decode('utf8')
        records = [entry.split('[[')[0] for entry in metadata.split('[[mods]]')[1:]]
        if any(re.search(r'modId\s*=\s*["\x27]hk3gtl["\x27]', entry) for entry in records):
            result.append(path)
    return result


def main():
    OUT.mkdir(exist_ok=True)
    frozen = json.loads((LOG / 'frozen-base.json').read_text('utf8'))
    inputs = json.loads((LOG / 'integration-inputs.json').read_text('utf8'))
    current, = active_jars()
    if str(current) != frozen['path'] or digest(current) != frozen['sha256']:
        raise RuntimeError('现用主包已变化，请重新冻结实际基包后合入W08。')
    compiled = ROOT / 'build/libs' / NAME
    with zipfile.ZipFile(compiled) as jar:
        classes = [name for name in jar.namelist() if any(name == stem + '.class'
            or name.startswith(stem + '$') for stem in inputs['class_stems'])]
        updates = {name: jar.read(name) for name in classes + inputs['resources']}
    with zipfile.ZipFile(frozen['frozen']) as source:
        metadata = source.read('META-INF/mods.toml').decode('utf8')
        updates['META-INF/mods.toml'] = re.sub(r'(?m)^version\s*=.*$',
            'version = "' + VERSION + '"', metadata, count=1).encode('utf8')
        mixins = json.loads(source.read('hk3gtl.mixins.json'))
        for kind, names in inputs['mixin_additions'].items():
            mixins[kind].extend(name for name in names if name not in mixins[kind])
        updates['hk3gtl.mixins.json'] = (json.dumps(mixins, ensure_ascii=False, indent=2) + '\n').encode('utf8')
        artifact = OUT / NAME
        existing = set(source.namelist())
        with zipfile.ZipFile(artifact, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as target:
            for info in source.infolist():
                target.writestr(copy(info), updates[info.filename] if info.filename in updates else source.read(info.filename))
            for name in sorted(updates.keys() - existing):
                target.writestr(name, updates[name])
        changes = {name: dict(before=sha256(source.read(name)).hexdigest() if name in existing else None,
            after=sha256(value).hexdigest()) for name, value in updates.items()}
    now = datetime.now().astimezone()
    build = dict(created_at=now.isoformat(timespec='seconds'), conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
        authorization='可以，那就实装一下 A5，也就是 W08', version=VERSION,
        build_kind='实际r15现用主包增量合入W08编译及官方重映射class与原生资源；补齐共享源码已批准W06蓝图依赖',
        base=frozen, compiled_artifact=str(compiled), compiled_sha256=digest(compiled),
        artifact=str(artifact), sha256=digest(artifact), bytes=artifact.stat().st_size,
        changes=changes, preserved_base_entries=len(existing - updates.keys()),
        source_sha256={path: digest(ROOT / path) for path in inputs['sources']},
        compile_command=inputs['compile_command'], java_compilation_passed=True,
        resource_processing_passed=True, official_remap_passed=True,
        automated_tests_run=False, game_verified=False,
        parallel_scope='保留冻结r15全部非本次合入条目；其他对话后续改动以各自记录为准。')
    save(LOG / 'build.json', build)
    current_now, = active_jars()
    if current_now != current or digest(current_now) != frozen['sha256']:
        raise RuntimeError('合包期间现用主包已变化，请以新包重做W08合入。')
    backup = LOG / ('before-install-' + now.strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir()
    destination = INSTANCE / 'mods' / NAME
    pending = destination.with_suffix('.jar.pending')
    shutil.copy2(artifact, pending)
    shutil.move(str(current), str(backup / current.name))
    pending.replace(destination)
    installed_sha = digest(destination)
    if installed_sha != build['sha256']:
        raise RuntimeError('安装文件与已构建候选SHA256不一致。')
    receipt = dict(build, installed_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        instance=str(INSTANCE), instance_version='增强版3.9', target=str(destination),
        installed_sha256=installed_sha, installed=True, replaced_backup=str(backup / current.name),
        active_hk3gtl_jars=[str(path) for path in active_jars()],
        controller='hk3gtl:w08_stellar_casting_furnace', controller_source_xyz=[489, 150, 370],
        controller_xyz=[256, 238, 165], controller_facing='north',
        size_wdh=[512, 512, 477], dynamic_cover_wdh=[512, 512, 480], block_count=3854075,
        native_animation_integrated=True, appearance_approved=True,
        blueprint='data/hk3gtl/structures/w08_candidate.bin.gz',
        renderer='com.sirin.hk3gtl.client.wonder.Hk3W08FxRenderer',
        fixed_interface_positions=[], desktop_used=False, game_started=False, saves_modified=False,
        acceptance_score_changed=False, restart_required=True)
    save(LOG / 'installation.json', receipt)
    save(LOG / 'completion.json', receipt)
    save(OUT / '安装回执.json', receipt)
    shutil.copy2(ROOT / 'src/main/resources/data/hk3gtl/structures/w08_approved.json', OUT / 'W08蓝图绑定.json')
    print(json.dumps(dict(installed=str(destination), sha256=installed_sha,
        updated_entries=len(updates), preserved_base_entries=build['preserved_base_entries']), ensure_ascii=True))


if __name__ == '__main__':
    main()
