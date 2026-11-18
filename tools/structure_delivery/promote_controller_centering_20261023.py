# -*- coding: utf-8 -*-
"""从批准快照接入I01–I13主控置中融合V2，按接口ID保留原有真实仓与能力合同。

【变更记录 #1】2026-10-23 13:31:29（内测5修订175）
- 删除：正式资源对旧独立面板和接口墩几何的引用；旧资源完整备份，源交付不改。
- 新增：批准清单SHA门禁、48资源暂存/回读、逐ID真实仓迁移与I01模板逐格继承。
- 修改：采用批准V2的全部几何和新控制点，控制器注册ID、接口能力及真实仓状态不变。
- 用途：让既有Pattern、JEI与放置命令共同读取本次确认结构；不构建、部署或改归档索引。

输入--source-root为完整21形态交付或不可变确认副本；--approval-manifest为外部批准清单。
默认仅生成logs暂存并验证，只有--apply且确认副本逐项匹配批准SHA时写正式48资源及测试。
失败先停止；应用前备份，复制失败恢复已处理文件。资源迁移不代表游戏成型或配方验收。

【变更记录 #2】2026-10-23 13:34:29（内测5修订175）
- 删除：共享测试仅21入口、固定六口与旧预览总数的限制，历史备注不删。
- 新增：I14–I18五形态测试数据、17口封装阵列与input/output择一分组检查。
- 修改：共享资源和预览测试随本入口暂存、备份与应用，新增五台业务回归由扩展入口负责。
- 用途：协同一次完整26形态资源验收；本脚本仍只迁移I01–I13的48正式资源。
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re
import shutil

import nbtlib as nbt
from build_integration_revision_20261023 import access
from promote_industrial_approved_20261015 import ABILITIES, HATCH_BLOCKS, MACHINES
from review_controller_integration_20261023 import RULES
from structure_size_baseline import require

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources/data/hk3gtl'
LOG = ROOT / 'logs/controller-centering-install-20261023'
STAGE = LOG / 'staging/i01-i13/data/hk3gtl'
SOURCE = ROOT / 'deliveries/I01-I18_控制器居中融合修订_V2_20261023'
TEST = ROOT / 'src/test/java/com/sirin/hk3gtl/test/industry/ApprovedArchitectureTest.java'
PREVIEW_TEST = TEST.with_name('ApprovedArchitecturePreviewTest.java')
KEYS = [(f'i01-{n}', 'i01' if n == 1 else f'i01_{n}') for n in range(1, 5)]
KEYS += [(f'i{n:02}', f'i{n:02}') for n in range(2, 14)]
PORT = 'hk3gtl:industrial_port_casing'


def now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2,
        separators=(',', ':') if compact else None) + '\n', encoding='utf-8')


def identity(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}


def relative_path(path):
    return path.relative_to(ROOT).as_posix()


def paths(key, root=RES):
    return [root / 'approved_architecture' / (key + '.json'),
            root / 'structures/approved' / (key + '.nbt'), root / 'structures/approved' / (key + '.json')]


def state_text(state):
    value = str(state['Name'])
    if state.get('Properties'):
        value += '[' + ','.join(f'{k}={v}' for k, v in sorted(state['Properties'].items())) + ']'
    return value


def decode(path):
    data = nbt.load(path)
    cells = {tuple(map(int, b['pos'])): state_text(data['palette'][int(b['state'])]) for b in data['blocks']}
    assert len(cells) == len(data['blocks']), str(path) + '重复坐标'
    return data, cells


def capability(state):
    block = state.split('[', 1)[0]
    if block == PORT:
        return None
    return next(k for k, v in HATCH_BLOCKS.items() if v == block)


def additive(before, after, a, b, label):
    source = {tuple(p[i]-a[i] for i in range(3)): s for p, s in before.items() if list(p) != a}
    target = {tuple(p[i]-b[i] for i in range(3)): s for p, s in after.items() if list(p) != b}
    assert source.items() <= target.items(), label + '拆除或覆盖前阶非主控'
    return {'transition': label, 'preserved': len(source), 'added': len(target)-len(source), 'removed': 0, 'changed': 0}


def prepare(source_root, approval_path):
    stamp = now()
    approved = read(approval_path) if approval_path else None
    approvals = {row['candidate_key']: row for row in approved['structures']} if approved else {}
    if approved:
        assert approved.get('approval_quote'), '批准原话缺失'
        assert approved.get('recorded_at'), '批准记录时间缺失'
    source_before = identity(source_root)
    records, inheritance, previous = [], [], None
    for candidate_key, key in KEYS:
        source = source_root / candidate_key / 'blueprint.json'
        bp = read(source)
        source_nbt = source.parent / (bp['name'] + '.nbt')
        structure, cells = decode(source_nbt)
        assert cells == {tuple(b['pos']): b['state'] for b in bp['blocks']}
        assert list(map(int, structure['size'])) == bp['size']
        assert int(structure['DataVersion']) == 3465
        assert bp['controller'][0] == (bp['size'][0]-1)//2
        assert cells[tuple(bp['controller'])] == 'minecraft:diamond_block'
        assert {tuple(p['pos']) for p in bp['ports']} == {p for p, s in cells.items() if s == PORT}
        require(bp)
        reaches = access(bp)
        assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in reaches), candidate_key
        if approved:
            confirmation = approvals[candidate_key]
            assert sha(source) == confirmation['source_blueprint_sha256'], candidate_key + '批准蓝图身份不匹配'
            assert sha(source_nbt) == confirmation['source_nbt_sha256'], candidate_key + '批准NBT身份不匹配'
        formal, template, sidecar = paths(key)
        old, meta = read(formal), read(sidecar)
        old_structure, old_template = decode(template)
        old_cells = {tuple(b['pos']): b['state'] for b in old['blocks']}
        ctrl = old['runtime_contract']['controller']
        assert ctrl == 'hk3gtl:' + MACHINES[key] == meta['machine'] == old_cells[tuple(old['controller'])]
        assert old_template[tuple(old['controller'])] == ctrl + '[facing=north]'
        old_ports = {p['id']: p for p in old['ports']}
        assert set(old_ports) == {p['id'] for p in bp['ports']} and len(old_ports) == 6
        migrated, port_states, installed = [], {}, {}
        for port in bp['ports']:
            original = old_ports[port['id']]
            assert port['purpose'] == original['purpose'] and port['face'] == original['face']
            migrated.append({**deepcopy(port), 'group': original['group']})
            state = old_template[tuple(original['pos'])]
            ability = capability(state)
            if ability:
                assert ability in ABILITIES[original['group']]
                assert state.endswith('[facing=' + port['face'] + ']')
                installed[port['id']] = ability
            port_states[port['id']] = state
        assert installed == meta['installed_hatches'], key + '原模板仓室合同不一致'
        assert set(old['runtime_contract']['required_abilities']) <= set(installed.values())
        data = deepcopy(old)
        data.update({'size': bp['size'], 'controller': bp['controller'], 'title': bp['title'], 'ports': migrated,
            'blocks': [{'pos': b['pos'], 'state': ctrl if b['pos'] == bp['controller'] else b['state']} for b in bp['blocks']]})
        data.setdefault('approved_source_history', []).append(deepcopy(old['approved_source']))
        data['approved_source'] = {'version': '主控居中融合V2已批准' if approved else '主控居中融合V2暂存待批准',
            'blueprint': relative_path(source), 'sha256': sha(source),
            'approval': approved['approval_quote'] if approved else None,
            'recorded_at': approved['recorded_at'] if approved else stamp,
            'approval_manifest': relative_path(approval_path) if approval_path else None,
            'approval_manifest_sha256': sha(approval_path) if approval_path else None,
            'original_message_time': '未知，采用批准记录时间'}
        change = {'record': len(data.get('_change_records', []))+1, 'time': stamp, 'revision': 175,
            'reason': '负责人明确批准当前主控置中融合V2并要求实装' if approved else '主控置中融合V2仅暂存核验',
            'deleted': '旧独立接口载体的正式几何引用；旧正式文件应用前完整备份',
            'added': '本次批准来源身份、新控制点及按ID迁移的接口布局',
            'modified': '几何逐格采用V2，注册ID、原接口能力合同与真实仓完整状态保持',
            'purpose': '既有Pattern与正式放置模板共用新坐标；游戏运行仍待实机验收'}
        data.setdefault('_change_records', []).append(change)
        if 'upgrade_contract' in bp:
            data['upgrade_contract'] = deepcopy(bp['upgrade_contract'])
        data['controller_centering'] = deepcopy(bp['controller_centering'])
        data['controller_centering']['source_status'] = '外部确认清单已批准' if approved else '候选暂存，未批准'
        data['paste_anchor'] = deepcopy(bp.get('paste_anchor', [0, 0, 0]))
        formal_new, template_new, sidecar_new = paths(key, STAGE)
        save(formal_new, data, compact=True)
        positions = {tuple(map(int, b['pos'])): b for b in structure['blocks']}
        replacements = {tuple(bp['controller']): old_structure['palette'][int(next(b['state'] for b in old_structure['blocks'] if list(map(int, b['pos'])) == old['controller']))]}
        for port in bp['ports']:
            old_pos = old_ports[port['id']]['pos']
            replacements[tuple(port['pos'])] = old_structure['palette'][int(next(b['state'] for b in old_structure['blocks'] if list(map(int, b['pos'])) == old_pos))]
        for pos, value in replacements.items():
            if value not in structure['palette']:
                structure['palette'].append(deepcopy(value))
            positions[pos]['state'] = nbt.Int(structure['palette'].index(value))
        template_new.parent.mkdir(parents=True, exist_ok=True)
        structure.save(template_new, gzipped=True)
        template_new.write_bytes(gzip.compress(gzip.decompress(template_new.read_bytes()), compresslevel=9, mtime=0))
        _, actual = decode(template_new)
        expected = dict(cells)
        expected[tuple(bp['controller'])] = ctrl + '[facing=north]'
        for port in bp['ports']:
            expected[tuple(port['pos'])] = port_states[port['id']]
        assert actual == expected
        formal_cells = {tuple(b['pos']): b['state'] for b in data['blocks']}
        assert formal_cells == {p: ctrl if list(p) == bp['controller'] else s for p, s in cells.items()}
        assert data['runtime_contract'] == old['runtime_contract']
        metadata = deepcopy(meta)
        metadata.update({'sha256': sha(formal_new), 'template_sha256': sha(template_new),
            'approved_blueprint_sha256': sha(source), 'approved_nbt_sha256': sha(source_nbt),
            'review_snapshot': relative_path(source_root.parent), 'controller': bp['controller'],
            'size_xyz': bp['size'], 'blocks': len(cells), 'approval_quote': approved['approval_quote'] if approved else None,
            'approval_manifest': relative_path(approval_path) if approval_path else None,
            'approval_manifest_sha256': sha(approval_path) if approval_path else None,
            'geometry_changes': '批准V2原几何；仅主控与六接口以原注册ID和原仓状态替换', 'game_verified': False,
            'paste_anchor': bp.get('paste_anchor', [0, 0, 0]),
            'controller_centering': deepcopy(data['controller_centering'])})
        change_meta = deepcopy(change)
        change_meta['record'] = len(metadata.get('_change_records', []))+1
        metadata.setdefault('_change_records', []).append(change_meta)
        save(sidecar_new, metadata)
        if candidate_key.startswith('i01-'):
            if previous:
                for label, before, after in [('Pattern', previous['formal'], formal_cells), ('真实仓NBT', previous['template'], actual)]:
                    inheritance.append(additive(before, after, previous['controller'], bp['controller'], previous['key']+'→'+key+' '+label))
            previous = {'key': key, 'formal': formal_cells, 'template': actual, 'controller': bp['controller']}
        records.append({'key': key, 'candidate_key': candidate_key, 'blocks': len(cells), 'controller': bp['controller'],
            'machine': ctrl, 'runtime_contract': deepcopy(data['runtime_contract']), 'ports': migrated,
            'installed_hatches': installed, 'port_states': port_states, 'source_blueprint': relative_path(source),
            'source_blueprint_sha256': sha(source), 'source_nbt_sha256': sha(source_nbt),
            'formal_sha256': {p.relative_to(STAGE).as_posix(): sha(p) for p in paths(key, STAGE)},
            'before_sha256': {p.relative_to(RES).as_posix(): sha(p) for p in paths(key)},
            'non_controller_and_port_changes_from_source': 0, 'access': reaches})
        print(key, len(cells), 'staged and verified', flush=True)
    assert identity(source_root) == source_before, '批准来源被改写'
    return {'recorded_at': stamp, 'revision': 175, 'forms': 16, 'formal_resource_count': 48,
        'source_root': relative_path(source_root), 'approval_manifest': relative_path(approval_path) if approval_path else None,
        'approval_manifest_sha256': sha(approval_path) if approval_path else None,
        'approval_quote': approved['approval_quote'] if approved else None, 'source_unchanged': True,
        'source_identity': source_before, 'structures': records, 'i01_inheritance': inheritance,
        'game_verified': False, 'deployed': False, 'applied': False}


def test_source(records, source_root):
    text = TEST.read_text(encoding='utf-8')
    for row in records:
        text, count = re.subn(r'Map\.entry\("' + re.escape(row['key']) + r'",\d+\)',
            f'Map.entry("{row["key"]}",{row["blocks"]})', text)
        assert count == 1, row['key'] + '测试计数位置不唯一'
    extra = [read(source_root / f'i{n:02}/blueprint.json') for n in range(14, 19)]
    size_entries = ',\n'.join('            Map.entry("' + d['key'] + '",new int[]{' + ','.join(map(str, d['size'])) + '})' for d in extra) + ',\n'
    count_entries = ','.join('Map.entry("' + d['key'] + '",' + str(len(d['blocks'])) + ')' for d in extra) + ',\n            '
    text = text.replace('            Map.entry("s01",new int[]{17,17,25})', size_entries+'            Map.entry("s01",new int[]{17,17,25})', 1)
    text = text.replace('Map.entry("s01",1930)', count_entries+'Map.entry("s01",1930)', 1)
    text = text.replace('Hk3ApprovedArchitecture.IDS.size()==21', 'Hk3ApprovedArchitecture.IDS.size()==26', 1)
    text = text.replace('check(data.ports().size()==6,"每台六接口："+id);', 'check(data.ports().size()==(id.equals("i18")?17:6),"接口数量："+id);', 1)
    text = text.replace('            case "service" -> Set.of();',
        '            case "input" -> Set.of("item_input","fluid_input");\n'
        '            case "output" -> Set.of("item_output","fluid_output");\n'
        '            case "service" -> Set.of();', 1)
    text = text.replace('Collections.nCopies(6,Set.of())', 'Collections.nCopies(data.ports().size(),Set.of())', 1)
    text = text.replace('case "gtceu:max_input_hatch" ->', 'case "gtceu:max_input_hatch", "gtceu:max_input_hatch_4x" ->', 1)
    text = text.replace('case "gtceu:max_output_hatch" ->', 'case "gtceu:max_output_hatch", "gtceu:max_output_hatch_4x" ->', 1)
    text = text.replace('||(port.group().equals("fluid")&&ability.startsWith("fluid_")),"模板接口组不匹配："+id);',
        '||(port.group().equals("fluid")&&ability.startsWith("fluid_"))\n'
        '                    ||(port.group().equals("input")&&ability.endsWith("_input"))\n'
        '                    ||(port.group().equals("output")&&ability.endsWith("_output")),"模板接口组不匹配："+id);', 1)
    note = ('/**\n * 【变更记录 #4】' + now() + '（第4次备注 · 内测5修订175）\n'
        ' * 删除：旧面板几何16项实体计数、21入口与固定六口的测试限制；历史备注保留。\n'
        ' * 新增：I14–I18五形态尺寸数量、17口、input/output择一组及工业主控宽度居中/净空/背壳断言。\n'
        ' * 修改：26形态与批准V2一致，原接口能力、真实仓模板及I01逐格继承回归继续执行。\n'
        ' * 用途：防止新坐标与Pattern/NBT脱节；不替代游戏成型、配方或生存验收。\n */\n')
    assert '【变更记录 #4】' not in text, '测试已更新，先核对既有接入收据'
    text = text.replace('public final class ApprovedArchitectureTest {', note+'public final class ApprovedArchitectureTest {', 1)
    old = '            check(cells.containsKey(key(data.controller())),"缺少主控方块："+id);'
    new = old + '\n            if(id.startsWith("i")) {\n' + '\n'.join([
        '                int[] control=data.controller();',
        '                check(control[0]==(data.size()[0]-1)/2,"工业主控宽度居中："+id);',
        '                check(!cells.containsKey(key(new int[]{control[0],control[1],control[2]-1})),"主控正面净空："+id);',
        '                check(cells.containsKey(key(new int[]{control[0],control[1],control[2]+1})),"主控实体背壳："+id);']) + '\n            }'
    assert old in text
    return text.replace(old, new, 1)


def preview_test_source(source_root):
    text = PREVIEW_TEST.read_text(encoding='utf-8')
    note = ('/**\n * 【变更记录 #2】' + now() + '（内测5修订175）\n'
        ' * 删除：21形态预览旧总数与仅固定物品/流体方向组的限制；保留损坏模板回归。\n'
        ' * 新增：26形态全体素回归，input/output接口组对真实仓方向的核验。\n'
        ' * 修改：总实体数采用批准V2及原研究所快照的独立预期；空气共享与全部坐标检查保持。\n'
        ' * 用途：确保新放置模板与JEI预览同源；不代表客户端或游戏运行验收。\n */\n')
    assert '【变更记录 #2】' not in text
    text = text.replace('public final class ApprovedArchitecturePreviewTest {', note+'public final class ApprovedArchitecturePreviewTest {', 1)
    blueprints = [read(source_root / key / 'blueprint.json') for key, _ in KEYS]
    blueprints += [read(source_root / f'i{n:02}/blueprint.json') for n in range(14, 19)]
    research = [read(RES / 'approved_architecture' / f's{n:02}.json') for n in range(1, 6)]
    all_data = blueprints + research
    volume = sum(d['size'][0]*d['size'][1]*d['size'][2] for d in all_data)
    solids = sum(len(d['blocks']) for d in all_data)
    text = text.replace('totalVolume == 3_278_810 && totalSolids == 360_827', f'totalVolume == {volume} && totalSolids == {solids}', 1)
    text = text.replace('21 个批准预览通过', '26 个批准预览通过', 1)
    text = text.replace('case "gtceu:max_input_hatch" ->', 'case "gtceu:max_input_hatch", "gtceu:max_input_hatch_4x" ->', 1)
    text = text.replace('case "gtceu:max_output_hatch" ->', 'case "gtceu:max_output_hatch", "gtceu:max_output_hatch_4x" ->', 1)
    text = text.replace('|| (port.group().equals("fluid") && ability.startsWith("fluid_")), "预览工作仓接口组：" + id);',
        '|| (port.group().equals("fluid") && ability.startsWith("fluid_"))\n'
        '                            || (port.group().equals("input") && ability.endsWith("_input"))\n'
        '                            || (port.group().equals("output") && ability.endsWith("_output")), "预览工作仓接口组：" + id);', 1)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=SOURCE)
    parser.add_argument('--approval-manifest', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    source = args.source_root.resolve()
    approval = args.approval_manifest.resolve() if args.approval_manifest else None
    receipt = LOG / 'i01-i13-receipt.json'
    if args.apply:
        assert approval and approval.exists(), '正式接入必须提供外部批准清单'
        assert (ROOT/'deliveries/多方块确认归档').resolve() in source.parents, '正式接入只读取不可变确认归档'
        assert not receipt.exists(), '已有接入收据；请核对现有结果，不重复覆盖'
    save(LOG/'rules-read-i01-i13.json', {'recorded_at': now(), 'files': [{'path':'rule/'+n, 'sha256':sha(ROOT/'rule'/n)} for n in RULES],
        'discussion_read':'doc/HK3GTL-内测5/讨论记录/2026-10-23_11-48-08_I01-I18主控制器宽度轴置中V2.html',
        'context_gatherer':'工具列表无此工具，未冒称调用；六规则本轮已完整实读'})
    report = prepare(source, approval)
    staged_test = LOG/'staging/i01-i13/ApprovedArchitectureTest.java'
    staged_preview = staged_test.with_name(PREVIEW_TEST.name)
    staged_test.write_text(test_source(report['structures'], source), encoding='utf-8')
    staged_preview.write_text(preview_test_source(source), encoding='utf-8')
    if args.apply:
        targets = [(p, RES/p.relative_to(STAGE)) for key in [k for _, k in KEYS] for p in paths(key, STAGE)] + [(staged_test, TEST), (staged_preview, PREVIEW_TEST)]
        backup = LOG/'previous-i01-i13'
        before = {}
        for staged, target in targets:
            saved = backup/target.relative_to(ROOT)
            assert not saved.exists(), str(saved)+'已有备份'
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
            before[relative_path(target)] = sha(target)
        applied = []
        try:
            for staged, target in targets:
                assert sha(target) == before[relative_path(target)], str(target)+'准备后被并行改写'
                applied.append(target)
                shutil.copy2(staged, target)
                assert sha(staged) == sha(target)
        except Exception:
            for target in applied:
                shutil.copy2(backup/target.relative_to(ROOT), target)
            raise
        assert identity(source) == report['source_identity']
        report.update({'applied':True, 'applied_at':now(), 'backup_root':relative_path(backup),
            'applied_files':{relative_path(target):sha(target) for _,target in targets},
            'tests_updated':[relative_path(TEST), relative_path(PREVIEW_TEST)], 'tests_run':'留根任务统一clean build及现有完整回归'})
        save(receipt, report)
    else:
        save(LOG/'i01-i13-dry-run.json', report)
    print('I01-I13', 'applied' if args.apply else 'dry-run only', len(report['structures']), flush=True)


if __name__ == '__main__':
    main()
