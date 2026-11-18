"""以R267为底定向叠加工艺、世界泡输出与配方状态生命周期修正。"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/industrial-finish-r268-20261113'
BASE = ROOT / 'logs/industrial-recipes-r267-20261113/HK3GTL-r266-industrial-recipes-r267.jar'
BUILT = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
CLASSES = [
    'common/recipe/Hk3ResearchProcessPlans',
    'common/research/Hk3ResearchRecipeRuntime',
    'common/registration/Hk3IndustrialDependencyAudit',
    'common/machine/research/Hk3LateIndustrialMachine',
    'common/worldbubble/Hk3WorldOutputPorts',
    'common/worldbubble/Hk3WorldResourceOutput',
    'common/worldbubble/Hk3WorldBubbleData',
    'data/Hk3RecipeDataProvider',
    'mixin/gtlcore/Hk3RecipeStatusLifecycleMixin',
]
RESOURCES = ['data/hk3gtl/research/' + name + '.json'
             for name in ['industrial_processes', 'research_execution']]
RESOURCES.append('hk3gtl.mixins.json')


def selected(name):
    return name.endswith('.class') and any(name == 'com/sirin/hk3gtl/' + root + '.class'
        or name.startswith('com/sirin/hk3gtl/' + root + '$') for root in CLASSES)


def digest(data):
    return sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    candidate = OUT / 'HK3GTL-r267-industrial-finish-r268.jar'
    temporary = candidate.with_suffix('.jar.tmp')
    with ZipFile(BASE) as previous, ZipFile(BUILT) as current:
        before = {entry.filename: previous.read(entry) for entry in previous.infolist()}
        replacements = {name: current.read(name) for name in current.namelist() if selected(name)}
        replacements.update({name: current.read(name) for name in RESOURCES})
        removed = {name for name in before if selected(name) and name not in replacements}
        with ZipFile(temporary, 'w') as result:
            for entry in previous.infolist():
                if entry.filename not in removed:
                    result.writestr(entry, replacements.get(entry.filename, before[entry.filename]))
            for name in sorted(replacements.keys() - before.keys()):
                result.writestr(current.getinfo(name), replacements[name])
    temporary.replace(candidate)
    after = {name: data for name, data in before.items() if name not in removed}
    after.update(replacements)
    changed = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
    added = sorted(after.keys() - before.keys())
    sources = [ROOT / 'src/main/java/com/sirin/hk3gtl' / (name + '.java') for name in CLASSES]
    sources += [ROOT / 'src/main/resources' / name for name in RESOURCES]
    receipt = dict(updated_at=datetime.now().astimezone().isoformat(), revision=268,
        status='R268电路解析重构及世界泡输出离线候选；未安装，未实机验收',
        candidate=candidate.relative_to(ROOT).as_posix(),
        base=BASE.relative_to(ROOT).as_posix(), base_sha256=digest(BASE.read_bytes()),
        source_jar=BUILT.relative_to(ROOT).as_posix(), source_jar_sha256=digest(BUILT.read_bytes()),
        sha256=digest(candidate.read_bytes()), bytes=candidate.stat().st_size,
        changed_entries=changed, added_entries=added, removed_entries=sorted(removed),
        source_classes=CLASSES, resource_paths=RESOURCES,
        source_sha256={path.relative_to(ROOT).as_posix(): digest(path.read_bytes()) for path in sources},
        entry_hashes={name: {'before': digest(before[name]) if name in before else None,
                             'after': digest(after[name]) if name in after else None}
                      for name in sorted(set(changed) | set(added) | removed)},
        package_script_sha256=digest(Path(__file__).read_bytes()),
        notes=['仅覆盖9个明确class根及其内部类、2个研究资源与Mixin配置；其他R267条目原样保留',
               '未混入未发布物品材质，不改变建筑批准与实机验收状态'],
        installed=False, game_desktop_instance_operations=False,
        client_formed_verified=False, client_running_verified=False, client_performance_verified=False)
    (OUT / 'packaging.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(dict(candidate=receipt['candidate'], sha256=receipt['sha256'],
                         changed=len(changed), added=len(added), removed=len(removed)), ensure_ascii=False))


if __name__ == '__main__':
    main()
