"""以R266为底定向叠加工艺与主控代码，保留其他资源和未发布材质隔离。"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json
import re


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/industrial-recipes-r267-20261113'
BASE = ROOT / 'logs/remove-fixed-ports-r266-20261113/HK3GTL-r265-restored-architecture-r266.jar'
BUILT = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
CLASS_GROUPS = {
    'common/recipe': ['Hk3RecipeAdderImpl', 'Hk3ResearchProcessPlans', 'Hk3ResearchProcessRecipes',
        'Hk3ResearchProcessEnergy', 'Hk3ResearchProcessTypes', 'Hk3ResearchProcessPorts'],
    'common/recipe/machine': ['Hk3ControllerRecipes', 'Hk3FunctionalItemRecipes', 'Hk3IndustrialSupplyRecipes',
        'Hk3VoltageCasingRecipes'],
    'common/research': ['Hk3IndustrialExtensionPolicy', 'Hk3ResearchData', 'Hk3ResearchRecipeRuntime',
        'Hk3ResearchExecutionContracts'],
    'common/machine/research': ['Hk3LateIndustrialMachine', 'Hk3RealityStabilityAnchorMachine'],
    'common/machine': ['Hk3LateIndustrialMachines', 'Hk3MachinesImpl', 'Hk3CommissionMachine',
        'Hk3W01HallMachine', 'Hk3W01Machines'],
    'common/machine/wonder': ['Hk3WonderCatalog', 'Hk3WonderMachine', 'Hk3WonderMachines',
        'Hk3WonderPattern', 'Hk3WonderProductionMachine'],
    'common/multiblock/pattern': ['Hk3PendingStructurePattern', 'Hk3SparsePreviewData'],
    'common/item': ['Hk3WonderItems', 'Hk3Items'],
    'common/machine/w02': ['Hk3W02Machine', 'Hk3W02Machines'],
    'common/machine/w03': ['Hk3W03Machine', 'Hk3W03Machines'],
    'common/machine/hyperion': ['Hk3HyperionMachine', 'Hk3HyperionMachines'],
    'common/multiblock/build': ['Hk3BuildPlans'],
    'common/worldbubble': ['Hk3WorldTaskService', 'Hk3WorldBubbleLedger', 'Hk3WorldBubbleData', 'Hk3WorldMiningRewards',
        'Hk3WorldResourceOutput'],
    'common/civ': ['Hk3EngineeringFacts', 'Hk3CivilizationService'],
    'common/finale': ['Hk3FinaleAdmission', 'Hk3FinaleRequirements'],
}
CLASSES = [directory + '/' + name for directory, names in CLASS_GROUPS.items() for name in names]
JAVA = ROOT / 'src/main/java/com/sirin/hk3gtl'
CATALOG = JAVA / 'common/machine/wonder/Hk3WonderCatalog.java'
WONDERS = re.findall(r'new Entry\("W\d+", "([^"]+)", "[^"]+", "[^"]+", "([^"]+)", Hk3Tiers\.\w+\)',
                     CATALOG.read_text('utf8'))
ITEMS = [product for _, product in WONDERS] + ['wonder_prefabricated_component', 'cross_domain_validation_report']
RESOURCES = ['data/hk3gtl/research/' + name + '.json'
             for name in ['industrial_processes', 'research_execution', 'wonder_processes']]
RESOURCES += ['data/hk3gtl/structures/' + name + '.bin.gz' for name in ['w04_candidate', 'w05_candidate']]
RESOURCES += ['assets/hk3gtl/models/item/' + name + '.json' for name in ITEMS]
LANG_KEYS = ['block.hk3gtl.' + controller for controller, _ in WONDERS]
LANG_KEYS += ['item.hk3gtl.' + name for name in ITEMS]
LANG_KEYS += ['block.hk3gtl.i37_world_maintenance_trial_platform']
LANG_KEYS += ['hk3gtl.machine.late_industry.' + key
              for key in ['rated', 'process_rating', 'processes_available', 'grid_output']]


def selected(name):
    return name.endswith('.class') and any(name == 'com/sirin/hk3gtl/' + root + '.class'
        or name.startswith('com/sirin/hk3gtl/' + root + '$') for root in CLASSES)


def digest(data):
    return sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    candidate = OUT / 'HK3GTL-r266-industrial-recipes-r267.jar'
    temporary = candidate.with_suffix('.jar.tmp')
    language_merges = {}
    with ZipFile(BASE) as previous, ZipFile(BUILT) as current:
        before = {entry.filename: previous.read(entry) for entry in previous.infolist()}
        replacements = {name: current.read(name) for name in current.namelist() if selected(name)}
        replacements.update({name: current.read(name) for name in RESOURCES})
        for language in ['zh_cn', 'en_us']:
            name = 'assets/hk3gtl/lang/' + language + '.json'
            original = json.loads(before[name])
            updated = json.loads(current.read(name))
            language_merges[language] = {key: {'before': original.get(key), 'after': updated[key]}
                                        for key in LANG_KEYS}
            original.update({key: updated[key] for key in LANG_KEYS})
            replacements[name] = (json.dumps(original, ensure_ascii=False, indent=2) + '\n').encode('utf8')
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
    sources = [JAVA / (name + '.java') for name in CLASSES]
    sources += [ROOT / 'src/main/resources' / name for name in RESOURCES]
    sources += [ROOT / 'src/main/resources/assets/hk3gtl/lang' / (language + '.json')
                for language in ['zh_cn', 'en_us']]
    receipt = dict(updated_at=datetime.now().astimezone().isoformat(),
        status='R267工业工艺与真实主控离线候选；未安装，未实机验收',
        candidate=candidate.relative_to(ROOT).as_posix(),
        base=BASE.relative_to(ROOT).as_posix(), base_sha256=digest(BASE.read_bytes()),
        source_jar=BUILT.relative_to(ROOT).as_posix(), source_jar_sha256=digest(BUILT.read_bytes()),
        sha256=digest(candidate.read_bytes()), bytes=candidate.stat().st_size,
        changed_entries=changed, added_entries=added, removed_entries=sorted(removed),
        entry_hashes={name: {'before': digest(before[name]) if name in before else None,
                             'after': digest(after[name]) if name in after else None}
                      for name in sorted(set(changed) | set(added) | removed)},
        source_classes=CLASSES, resource_paths=RESOURCES, language_keys=LANG_KEYS,
        language_merges=language_merges,
        source_sha256={path.relative_to(ROOT).as_posix(): digest(path.read_bytes()) for path in sources},
        package_script_sha256=digest(Path(__file__).read_bytes()),
        notes=['仅覆盖明确列出的class及其内部类，删除这些根下已不存在的旧内部类',
               '保留R266其他类、资源、纹理和元信息；语言只合并本轮37个精确键',
               '缺少完整蓝图的真实主控仍拒绝成型；代码及候选打包不等于游戏验收'],
        installed=False, game_desktop_instance_operations=False,
        client_formed_verified=False, client_running_verified=False, client_performance_verified=False)
    (OUT / 'packaging.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(dict(candidate=receipt['candidate'], sha256=receipt['sha256'],
                         changed=len(changed), added=len(added), removed=len(removed)), ensure_ascii=False))


if __name__ == '__main__':
    main()
