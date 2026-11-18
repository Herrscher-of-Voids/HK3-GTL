from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/free-position-interfaces-r265-20261113'
AUDIT = ROOT / 'logs/beta5-completion-audit-20261030'
BASE = ROOT / 'logs/world-farview-surface-r264-20261112/HK3GTL-r263-farview-surface-r264.jar'
BUILT = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
CLASSES = [
    'common/multiblock/pattern/' + name for name in [
        'Hk3InterfacePredicates', 'Hk3IndustrialApprovedPatterns', 'Hk3IndustrialExtensionPatterns',
        'Hk3LiquidLinePatterns', 'Hk3ResearchInstitutePatterns', 'Hk3ApprovedArchitecturePatterns',
        'Hk3LateIndustrialPatterns', 'Hk3LargeStructurePattern', 'Hk3W01HallPattern']
] + [
    'common/multiblock/build/' + name for name in [
        'Hk3BuildPlan', 'Hk3BuildPlans', 'Hk3UniversalTerminalBuilder', 'Hk3DismantleOperation',
        'Hk3IntegrityHost', 'Hk3HyperionIntegrityTask', 'Hk3InterfaceChunks']
] + [
    'common/machine/Hk3CommissionMachine',
    'common/machine/w02/Hk3W02Pattern', 'common/machine/w02/Hk3W02Machine',
    'common/machine/w03/Hk3W03Pattern', 'common/machine/w03/Hk3W03Machine',
    'common/machine/hyperion/Hk3HyperionConstructionPattern', 'common/machine/hyperion/Hk3HyperionMachine',
    'common/multiblock/export/PatternCodeWriter', 'client/wonder/Hk3W03FieldScenes',
    'client/farview/Hk3FarViewRenderer', 'client/farview/Hk3WorldFarTerrain',
    'client/preview/Hk3W01PreviewWidget', 'mixin/client/Hk3W03BlockRenderMixin',
    'mixin/client/Hk3W03EmbeddiumContext', 'mixin/client/Hk3W03EmbeddiumRenderMixin'
]
LANG_KEYS = ['hk3gtl.approved.update.U11.line.0', 'hk3gtl.w01.sparse', 'hk3gtl.hyperion.anchor',
             'hk3gtl.preview.interfaces', 'hk3gtl.w02.move_ports']


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def selected(name):
    return name.endswith('.class') and any(name == root + '.class' or name.startswith(root + '$')
                                          for root in ['com/sirin/hk3gtl/' + path for path in CLASSES])


def main():
    now = datetime.now().astimezone().isoformat()
    history = sorted(OUT.glob('audit-before-*'))[-1]
    candidate = OUT / 'HK3GTL-r264-free-position-interfaces-r265.jar'
    with ZipFile(BASE) as previous, ZipFile(BUILT) as current:
        replacements = {name: current.read(name) for name in current.namelist() if selected(name)}
        for language in ['zh_cn', 'en_us']:
            name = 'assets/hk3gtl/lang/' + language + '.json'
            original = json.loads(previous.read(name))
            updated = json.loads(current.read(name))
            original.update({key: updated[key] for key in LANG_KEYS})
            replacements[name] = json.dumps(original, ensure_ascii=False, indent=2).encode('utf8')
        refmap = json.loads(previous.read('hk3gtl-refmap.json'))
        updated = json.loads(current.read('hk3gtl-refmap.json'))
        for path in CLASSES:
            if not path.startswith('mixin/'):
                continue
            key = 'com/sirin/hk3gtl/' + path
            refmap['mappings'].pop(key, None)
            if key in updated['mappings']:
                refmap['mappings'][key] = updated['mappings'][key]
            for mappings in refmap['data'].values():
                mappings.pop(key, None)
            for context, mappings in updated['data'].items():
                if key in mappings:
                    refmap['data'].setdefault(context, {})[key] = mappings[key]
        replacements['hk3gtl-refmap.json'] = json.dumps(refmap, ensure_ascii=False, indent=2).encode('utf8')
        before = {entry.filename: previous.read(entry.filename) for entry in previous.infolist()}
        removed = {name for name in before if selected(name) and name not in replacements}
        removed.update(name for name in before if name.startswith(
            'com/sirin/hk3gtl/common/machine/w02/Hk3W02PortMigration'))
        with ZipFile(candidate, 'w') as result:
            for entry in previous.infolist():
                if entry.filename not in removed:
                    result.writestr(entry, replacements.get(entry.filename, before[entry.filename]))
            for name in sorted(replacements.keys() - before.keys()):
                result.writestr(current.getinfo(name), replacements[name])
    with ZipFile(candidate) as result:
        after = {name: result.read(name) for name in result.namelist()}
    changed = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
    source_dir = OUT / 'source'
    for path in CLASSES:
        source = ROOT / 'src/main/java/com/sirin/hk3gtl' / (path + '.java')
        target = source_dir / (path + '.java')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    build_log = OUT / 'build.log'
    receipt = dict(
        updated_at=now, status='自由接口 R265 离线候选；未安装，未实机验收',
        candidate=candidate.relative_to(ROOT).as_posix(), base=BASE.relative_to(ROOT).as_posix(),
        base_sha256=sha256(BASE.read_bytes()).hexdigest(),
        sha256=sha256(candidate.read_bytes()).hexdigest(), bytes=candidate.stat().st_size,
        changed_entries=changed, added_entries=sorted(after.keys() - before.keys()),
        removed_entries=sorted(before.keys() - after.keys()), protocol_version=36,
        language_keys=LANG_KEYS, source_classes=CLASSES,
        changes=['本模组蓝图实体非主控位置均可替换合法通用工业接口，空气仍按原规则处理',
                 '复用必要物品与流体能力计数，并行仓和维护仓全机各最多一个',
                 'W01、W02、W03及休伯利安分批完整性检查收集真实接口并接入GT能力',
                 '真实接口区块按需保留方块tick，填充壳不持票，失效或卸载释放',
                 '终端补建保留合法接口，拆除继续保护其他控制器仓和不拆仓设置',
                 'W03原版、Embeddium和远景遮罩保留实际接口可见',
                 'JEI标明自由接口规则及默认蓝图材料统计，导出器沿用同规则',
                 '仅覆盖本轮类和语言增量，保留R264远景及原建筑资源'],
        limitations=['主控与空气不能替换为接口；未知部件不作为通用接口',
                     'W04及后续未注册候选不因本轮规则自动成为可运行机器',
                     '真实成型、远端接口运行、W03画面及性能待负责人客户端验收'],
        build=next(line.strip() for line in build_log.read_text('utf8').splitlines() if 'BUILD SUCCESSFUL' in line),
        installed=False, game_desktop_instance_operations=False, client_formed_verified=False,
        client_running_verified=False, client_performance_verified=False, score_delta=0)
    save(OUT / 'completion.json', receipt)
    summary = json.loads((history / 'current-summary.json').read_text('utf8'))
    system = next(item for item in summary['systems'] if item['id'] == 'multiblocks')
    system['free_position_interfaces'] = receipt
    system['updated_at'] = now
    summary['current_work'].update(system='多方块自由接口位置', state=receipt['status'],
        scope='仓库开发与离线构建；不安装、不操作游戏、桌面或活动存档。',
        next_turn='由负责人验证真实成型与远端接口运行，按反馈处理；未完成实机验收。',
        free_position_interfaces=receipt)
    summary['report_updated_at'] = summary['updated_at'] = now
    summary['systems'].sort(key=lambda item: item['percent'])
    save(AUDIT / 'current-summary.json', summary)
    page = (history / 'index.html').read_text('utf8')
    notice = ('<section class="notice" id="free-position-interfaces-r265"><h2>自由接口位置 R265 离线候选</h2>'
              '<p>本模组蓝图实体非主控位置开放合法通用接口，保留能力与数量要求；同步终端、完整性核验、'
              'GT部件收集、JEI提示和W03可见性。候选未安装，未进行客户端成型、运行或性能验收；'
              '37域、原分母及研发／验收分数保持。</p>'
              '<p><a href="../free-position-interfaces-r265-20261113/completion.json">本轮代码与构建回执</a></p></section>')
    page = page.replace('<body><main>', '<body><main>' + notice, 1)
    sections = re.findall(r'<details id="system-[^"]+".*?</details>', page, re.S)
    by_id = {re.search(r'id="system-([^"]+)"', section).group(1): section for section in sections}
    if sections:
        page = page.replace(''.join(sections), ''.join(by_id[item['id']] for item in summary['systems']), 1)
    page = re.sub(r'(<script type="application/json" id="audit-data">).*?(</script>)',
                  lambda match: match[1] + json.dumps(summary, ensure_ascii=False, indent=2) + match[2],
                  page, count=1, flags=re.S)
    (AUDIT / 'index.html').write_text(page, 'utf8')
    print(json.dumps({key: receipt[key] for key in ['candidate', 'sha256', 'build', 'installed']}, ensure_ascii=True))


if __name__ == '__main__':
    main()
