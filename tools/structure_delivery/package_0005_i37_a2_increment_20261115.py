from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-i37-a2-runtime-20261115'
BASE = ROOT / 'deliveries/0000最终统合_增强版3.9启动修复_R2_20261115/0000最终统合-0.5.0-enhanced39-r2.jar'
REMAP = ROOT / 'build/libs/0005多方块设计-0.5.0-I37A2-r1.jar'
DELIVERY = ROOT / 'deliveries/0005_I37_A2接入_20261115'
OUTPUT = DELIVERY / '0005多方块设计-0.5.0-I37A2-r1.jar'
VERSION = '0.5.0-I37A2-r1'
STEMS = (
    'com/sirin/hk3gtl/common/machine/Hk3LateIndustrialMachines',
    'com/sirin/hk3gtl/common/multiblock/pattern/Hk3ApprovedArchitecture',
    'com/sirin/hk3gtl/common/multiblock/pattern/Hk3LateIndustrialPatterns',
)
RESOURCES = ('data/hk3gtl/compact_architecture/i37.json', 'data/hk3gtl/structures/compact/i37.bin.gz')
BUILD_COMMAND = "& .\\gradlew.bat build -x check -x test -x renameToChinese '-Parchives_base_name=0005多方块设计' '-Pmod_version=0.5.0-I37A2-r1' --console=plain"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def family(name):
    return name.endswith('.class') and any(name == stem + '.class' or name.startswith(stem + '$') for stem in STEMS)


def main():
    DELIVERY.mkdir(parents=True, exist_ok=True)
    with ZipFile(BASE) as base, ZipFile(REMAP) as remap:
        base_names = set(base.namelist())
        classes = {name: remap.read(name) for name in remap.namelist() if family(name)}
        retained_inner = [name for name, data in classes.items() if '$' in name and name in base_names and base.read(name) == data]
        payload = {name: data for name, data in classes.items() if name not in retained_inner}
        payload.update({name: remap.read(name) for name in RESOURCES})
        source_kind = {name: '官方Loom重映射产物' for name in payload}
        data = base.read('META-INF/mods.toml').decode('utf8')
        payload['META-INF/mods.toml'] = re.sub(r'(?m)^(\s*version\s*=\s*")[^"]*(")',
            lambda match: match[1] + VERSION + match[2], data, count=1).encode('utf8')
        data = base.read('META-INF/MANIFEST.MF').decode('utf8')
        payload['META-INF/MANIFEST.MF'] = re.sub(r'(?m)^(Implementation-Version: )[^\r\n]*',
            lambda match: match[1] + VERSION, data, count=1).encode('utf8')
        source_kind.update({name: 'R2原元数据仅更新版本号' for name in ('META-INF/mods.toml', 'META-INF/MANIFEST.MF')})
        temporary = OUTPUT.with_suffix('.jar.tasktmp')
        with ZipFile(temporary, 'w', ZIP_DEFLATED) as output:
            for entry in base.infolist():
                if entry.filename not in payload:
                    output.writestr(entry, base.read(entry.filename))
            for name, data in payload.items():
                output.writestr(name, data)
    temporary.replace(OUTPUT)
    with ZipFile(BASE) as base, ZipFile(OUTPUT) as output:
        before = {name: sha(base.read(name)) for name in base.namelist()}
        after = {name: sha(output.read(name)) for name in output.namelist()}
        different = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
        added = sorted(after.keys() - before.keys())
        removed = sorted(before.keys() - after.keys())
        unexpected = sorted(set(different + added + removed) - payload.keys())
        refmap = json.loads(base.read('hk3gtl.mixins.json'))['refmap']
        protected = ['hk3gtl.mixins.json', refmap, 'com/sirin/hk3gtl/mixin/gtlcore/Hk3EggBindingMixin.class']
        inventory = dict(base=str(BASE), base_sha256=file_sha(BASE), official_remap=str(REMAP),
            official_remap_sha256=file_sha(REMAP), class_stems=list(STEMS),
            retained_unchanged_inner_classes=sorted(retained_inner),
            payload=[dict(path=name, source=source_kind[name], source_sha256=sha(payload[name]),
                          base_sha256=before.get(name), delivered_sha256=after[name]) for name in sorted(payload)],
            changed_base_entries=different, added_entries=added, removed_entries=removed,
            unexpected_entry_differences=unexpected,
            nonpayload_base_entries_preserved=not unexpected,
            protected_entries={name: dict(base_sha256=before[name], delivered_sha256=after[name],
                                         byte_identical=before[name] == after[name]) for name in protected},
            payload_matches_source=all(after[name] == sha(data) for name, data in payload.items()),
            base_entries=len(before), delivered_entries=len(after),
            all_other_ae_mixins_refmap_resources_preserved=not unexpected)
    save(LOG / 'package-inventory.json', inventory)
    source_paths = [Path('src/main/java') / (stem + '.java') for stem in STEMS]
    source_paths += [Path('src/main/resources') / name for name in RESOURCES]
    source_paths += [Path('tools/structure_delivery/integrate_0005_i37_suspended_test_dock_a2_20261115.py'),
                     Path(__file__).relative_to(ROOT)]
    source_manifest = DELIVERY / 'source-increment-sha256.json'
    save(source_manifest, dict(scope='I37 A2三份Java、两份正式资源及集成与打包脚本；不包含其他系统源码。',
         files=[dict(path=path.as_posix(), bytes=(ROOT / path).stat().st_size,
                     sha256=file_sha(ROOT / path)) for path in source_paths]))
    source_zip = DELIVERY / '0005多方块设计-0.5.0-I37A2-r1-源码增量.zip'
    with ZipFile(source_zip, 'w', ZIP_DEFLATED) as packed:
        for path in source_paths:
            packed.write(ROOT / path, path.as_posix())
        packed.write(source_manifest, source_manifest.name)
    completion = dict(recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        conversation='0005', conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
        status='基于0000 R2最小移植I37 A2原生GT完整蓝图，独立交付候选；未安装或进行游戏验收。',
        artifact=dict(path=str(OUTPUT), version=VERSION, bytes=OUTPUT.stat().st_size, sha256=file_sha(OUTPUT)),
        base=dict(path=str(BASE), sha256=inventory['base_sha256']),
        official_remap=dict(path=str(REMAP), sha256=inventory['official_remap_sha256']),
        build=dict(command=BUILD_COMMAND, log=str(LOG / 'gradle-build.log'),
                   result=None, exit_code=None, result_recorded_by='由主流程确认实际Gradle日志后填写。'),
        source_increment=dict(path=str(source_zip), bytes=source_zip.stat().st_size,
                              sha256=file_sha(source_zip), source_file_count=len(source_paths),
                              manifest=str(source_manifest), manifest_sha256=file_sha(source_manifest)),
        packaging=dict(script=str(Path(__file__)), inventory=str(LOG / 'package-inventory.json'),
                       class_count=sum(name.endswith('.class') for name in payload),
                       resource_count=len(RESOURCES), metadata_count=2,
                       unexpected_entry_differences=unexpected,
                       preserved_r2_nonpayload=not unexpected),
        structure=dict(key='i37', approved_version='A2', blocks=18445378, size_xyz=[561, 321, 681],
                       controller=[280, 42, 17], integration_receipt=str(LOG / 'integration.json')),
        compatibility=str(LOG / 'base-compatibility.json'),
        installed=False, game_started=False, game_verified=False, active_instance_modified=False,
        active_saves_modified=False, automated_tests_added=False, automated_tests_run=False,
        acceptance_score_changed=False)
    save(DELIVERY / 'completion.json', completion)
    save(LOG / 'package-completion.json', completion)
    print(json.dumps(completion['artifact'], ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
