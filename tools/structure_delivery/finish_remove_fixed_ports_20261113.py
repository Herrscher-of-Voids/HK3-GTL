from collections import Counter
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json
import re
import shutil

from finish_free_position_interfaces_20261113 import CLASSES as PREVIOUS_CLASSES

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/remove-fixed-ports-r266-20261113'
AUDIT = ROOT / 'logs/beta5-completion-audit-20261030'
BASE = ROOT / 'logs/free-position-interfaces-r265-20261113/HK3GTL-r264-free-position-interfaces-r265.jar'
BUILT = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
CLASSES = PREVIOUS_CLASSES + ['client/wonder/Hk3W03FxModel',
    'common/multiblock/pattern/Hk3LiquidLineLayout', 'common/machine/Hk3MachinesMaxStage',
    'common/command/Hk3ApprovedStructureRuntimeCheck', 'common/command/Hk3LiquidLineRuntimeCheck']
RESOURCES = ['data/hk3gtl/structures/w02_19c_a2.bin.gz',
    'data/hk3gtl/structures/w03_c9.bin.gz', 'data/hk3gtl/structures/hyperion_construction.bin.gz',
    'assets/hk3gtl/textures/effect/w03_c9_atlas.png']
RESOURCE_DIRS = ['data/hk3gtl/structures/compact/', 'data/hk3gtl/compact_architecture/',
    'data/hk3gtl/structures/approved/']
LANG_KEYS = ['hk3gtl.approved.update.U11.line.0', 'hk3gtl.preview.interfaces']


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def selected(name):
    return name.endswith('.class') and any(name == root + '.class' or name.startswith(root + '$')
        for root in ['com/sirin/hk3gtl/' + path for path in CLASSES])


def main():
    now = datetime.now().astimezone().isoformat()
    candidate = OUT / 'HK3GTL-r265-restored-architecture-r266.jar'
    with ZipFile(BASE) as previous, ZipFile(BUILT) as current:
        before = {entry.filename: previous.read(entry.filename) for entry in previous.infolist()}
        replacements = {name: current.read(name) for name in current.namelist()
            if selected(name) or name in RESOURCES or any(name.startswith(path) for path in RESOURCE_DIRS)}
        for language in ['zh_cn', 'en_us']:
            name = 'assets/hk3gtl/lang/' + language + '.json'
            original = json.loads(before[name])
            updated = json.loads(current.read(name))
            original.update({key: updated[key] for key in LANG_KEYS})
            replacements[name] = json.dumps(original, ensure_ascii=False, indent=2).encode('utf8')
        removed = {name for name in before if selected(name) and name not in replacements}
        with ZipFile(candidate, 'w') as result:
            for entry in previous.infolist():
                if entry.filename not in removed:
                    result.writestr(entry, replacements.get(entry.filename, before[entry.filename]))
            for name in sorted(replacements.keys() - before.keys()):
                result.writestr(current.getinfo(name), replacements[name])
    with ZipFile(candidate) as result:
        after = {name: result.read(name) for name in result.namelist()}
    changed = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
    for path in CLASSES:
        source = ROOT / 'src/main/java/com/sirin/hk3gtl' / (path + '.java')
        target = OUT / 'source' / (path + '.java')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    restored = []
    for name, path, key in [
        ('W02', 'logs/terminal-preview-r242-20261110/w02-export.json', 'substitutions'),
        ('Hyperion', 'logs/hyperion-construction-20261108/resource-verification.json', 'authorized_surface_substitutions')]:
        for cell in json.loads((ROOT / path).read_text('utf8'))[key]:
            if cell['after'] == 'hk3gtl:industrial_port_casing':
                restored.append(dict(machine=name, pos=cell['pos'], before=cell['after'],
                    after=cell['before'], source=path))
    save(OUT / 'w02-hyperion-restored-positions.json', restored)
    restoration = json.loads((ROOT / 'logs/default-port-removal-20261113/restoration-plan.json').read_text('utf8'))
    materials = Counter(cell['evidence']['kind'] for item in restoration for cell in item['changes'])
    build_log = (OUT / 'build.log').read_text('utf8')
    receipt = dict(updated_at=now, status='撤销固定接口 R266 离线候选；未安装，未实机验收',
        candidate=candidate.relative_to(ROOT).as_posix(), base=BASE.relative_to(ROOT).as_posix(),
        base_sha256=sha256(BASE.read_bytes()).hexdigest(),
        sha256=sha256(candidate.read_bytes()).hexdigest(), bytes=candidate.stat().st_size,
        changed_entries=changed, added_entries=sorted(after.keys() - before.keys()),
        removed_entries=sorted(before.keys() - after.keys()), source_classes=CLASSES,
        protocol_version=36, language_keys=LANG_KEYS,
        changes=['旧固定接口恢复对应建筑材料，主控位置不变；默认蓝图不再预设接口',
            '实体非主控位置继续允许玩家替换合法通用接口，必要工艺能力与仓数量限制保留',
            '结构判定、终端、JEI默认预览及材料统计统一使用恢复后的建筑源',
            'W03旧接口特效贴图恢复建筑材料，主控继续由真实模型显示',
            '候选以R265定向叠加，不带入其他未发布材质改动'],
        restored_positions=dict(industrial_and_research_shapes=len(restoration),
            industrial_and_research_cells=sum(len(item['changes']) for item in restoration),
            material_basis=dict(materials), w02_hyperion_cells=len(restored), w03_cells=8,
            injector_cells=8, unregistered_w04_w05_candidate_cells=16),
        limitations=['295格缺少覆盖前记录，按同面相邻表皮补全，逐位置依据已留存',
            '候选未安装，既有世界的方块没有自动改写',
            'W03自由接口与动态特效的遮挡、真实成型及运行仍待客户端验收',
            'W04、W05保持未注册设计候选，不因本轮修改成为正式机器'],
        evidence=['w02/w02-export.json', 'hyperion/resource-verification.json',
            'w02-hyperion-restored-positions.json', 'wonder-restoration.json',
            '../default-port-removal-20261113/restoration-plan.json',
            '../default-port-removal-20261113/applied.json', 'build.log'],
        build=next(line.strip() for line in build_log.splitlines() if 'BUILD SUCCESSFUL' in line),
        installed=False, game_desktop_instance_operations=False, client_formed_verified=False,
        client_running_verified=False, client_performance_verified=False, score_delta=0)
    save(OUT / 'completion.json', receipt)
    history = sorted(OUT.glob('audit-before-*'))[-1]
    summary = json.loads((history / 'current-summary.json').read_text('utf8'))
    system = next(item for item in summary['systems'] if item['id'] == 'multiblocks')
    system['removed_fixed_interfaces'] = receipt
    system['updated_at'] = now
    summary['current_work'].update(system='多方块旧固定接口撤销', state=receipt['status'],
        scope='仓库代码、建筑资源与离线构建；不安装、不操作游戏、桌面或活动存档。',
        next_turn='由负责人验收真实搭建、自由接口成型及画面；未新增客户端测试。',
        removed_fixed_interfaces=receipt)
    summary['report_updated_at'] = summary['updated_at'] = now
    summary['systems'].sort(key=lambda item: item['percent'])
    save(AUDIT / 'current-summary.json', summary)
    page = (history / 'index.html').read_text('utf8')
    notice = ('<section class="notice" id="remove-fixed-ports-r266"><h2>撤销旧固定接口 R266</h2>'
        '<p>默认蓝图的旧接口恢复对应建筑材料；玩家可自行替换实体非主控位置。'
        '结构判定、终端与JEI材料和预览同步；候选未安装，未实机验收，37域及原分数保持。</p>'
        '<p><a href="../remove-fixed-ports-r266-20261113/completion.json">代码、资源与构建回执</a></p></section>')
    page = page.replace('<body><main>', '<body><main>' + notice, 1)
    sections = re.findall(r'<details id="system-[^"]+".*?</details>', page, re.S)
    by_id = {re.search(r'id="system-([^"]+)"', section).group(1): section for section in sections}
    ordered = iter(by_id[item['id']] for item in summary['systems'])
    page = re.sub(r'<details id="system-[^"]+".*?</details>', lambda match: next(ordered), page, flags=re.S)
    page = re.sub(r'(<script type="application/json" id="audit-data">).*?(</script>)',
        lambda match: match[1] + json.dumps(summary, ensure_ascii=False, indent=2) + match[2],
        page, count=1, flags=re.S)
    (AUDIT / 'index.html').write_text(page, 'utf8')
    print(json.dumps({key: receipt[key] for key in ['candidate', 'sha256', 'build', 'installed']}, ensure_ascii=True))


if __name__ == '__main__':
    main()
