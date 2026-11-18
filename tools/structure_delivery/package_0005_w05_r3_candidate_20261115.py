"""在增强版3.9冻结候选上叠加W05 R3资源与已编译方向绑定。"""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import re
import zipfile


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'deliveries/0000最终统合_终焉之茧R8接入_20261115/0000最终统合-0.5.0-enhanced39-r6-cocoon-r8.jar'
REMAP = ROOT / 'build/libs/0005多方块设计-0.5.0-W05R3-r1.jar'
DELIVERY = ROOT / 'deliveries/0005_W05_R3运行蓝图接入_20261115'
LOG = ROOT / 'logs/0005-w05-r3-runtime-20261115'
OUTPUT = DELIVERY / '0005多方块设计-0.5.0-W05R3-r1.jar'
VERSION = '0.5.0-W05R3-r1'
RESOURCES = ('data/hk3gtl/structures/w05_candidate.bin.gz',
    'data/hk3gtl/structures/w05_approved.json')
STEMS = (
    'com/sirin/hk3gtl/common/multiblock/pattern/Hk3SparsePreviewData',
    'com/sirin/hk3gtl/common/campus/Hk3CampusCatalog',
    'com/sirin/hk3gtl/common/machine/wonder/Hk3WonderMachines',
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    value = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def main():
    DELIVERY.mkdir(exist_ok=True)
    base_sha = file_digest(BASE)
    payload = {name: (ROOT / 'src/main/resources' / name).read_bytes() for name in RESOURCES}
    changed_classes = {}
    with zipfile.ZipFile(BASE) as base, zipfile.ZipFile(REMAP) as remap:
        old = set(base.namelist())
        for name in remap.namelist():
            if name.endswith('.class') and any(name == stem + '.class' or name.startswith(stem + '$') for stem in STEMS):
                data = remap.read(name)
                if name not in old or base.read(name) != data:
                    changed_classes[name] = data
        payload.update(changed_classes)
        version = re.sub(rb'(?m)^(\s*version\s*=\s*")[^"]*(")',
            lambda match: match[1] + VERSION.encode() + match[2], base.read('META-INF/mods.toml'), count=1)
        manifest = re.sub(rb'(?m)^(Implementation-Version: )[^\r\n]*',
            lambda match: match[1] + VERSION.encode(), base.read('META-INF/MANIFEST.MF'), count=1)
        payload['META-INF/mods.toml'] = version
        payload['META-INF/MANIFEST.MF'] = manifest
        temporary = OUTPUT.with_suffix('.jar.pending')
        with zipfile.ZipFile(temporary, 'w') as target:
            for entry in base.infolist():
                target.writestr(entry, payload.get(entry.filename, base.read(entry.filename)))
            for name in payload.keys() - old:
                target.writestr(name, payload[name], compress_type=zipfile.ZIP_DEFLATED)
    temporary.replace(OUTPUT)
    with zipfile.ZipFile(BASE) as base, zipfile.ZipFile(OUTPUT) as output:
        before = {name: digest(base.read(name)) for name in base.namelist()}
        after = {name: digest(output.read(name)) for name in output.namelist()}
        changed = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
        added = sorted(after.keys() - before.keys())
        removed = sorted(before.keys() - after.keys())
        expected = set(payload)
        unexpected = sorted(set(changed + added + removed) - expected)
        result = dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
            conversation='0005', conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
            version=VERSION, source_base=str(BASE.relative_to(ROOT)).replace('\\', '/'),
            base_sha256=base_sha, base_conversation='0000', base_version='0.5.0-enhanced39-r6-cocoon-r8',
            remapped_classes=str(REMAP.relative_to(ROOT)).replace('\\', '/'),
            changed_classes=sorted(changed_classes), resources=list(RESOURCES),
            changed_entries=changed, added_entries=added, removed_entries=removed,
            unexpected_entry_differences=unexpected,
            payload_sha256={name: digest(data) for name, data in payload.items()},
            artifact=str(OUTPUT.relative_to(ROOT)).replace('\\', '/'),
            artifact_sha256=file_digest(OUTPUT), bytes=OUTPUT.stat().st_size,
            static_blueprint_integrated=True, native_animation_integrated=False,
            installed=False, game_started=False, game_verified=False,
            parallel_scope='明确以0000 R8候选为冻结底包，仅叠本次W05资源、方向/标识类和版本元数据；不将冻结后的并行更新宣称为自动包含。')
        result['remap_result'] = '成功' if not unexpected else '存在意外条目差异'
        (DELIVERY / '构建与叠包回执.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf8')
        (LOG / 'package.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(dict(artifact=result['artifact'], sha256=result['artifact_sha256'],
        bytes=result['bytes'], changed_entries=result['changed_entries'],
        added_entries=result['added_entries'], unexpected=result['unexpected_entry_differences']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
