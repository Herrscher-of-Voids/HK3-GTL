"""修订163，2026-10-17 15:09:06：现行配方研究合同的正例与真正反例。

独立构造两条最小合同和临时导出，不改正式资源、不模拟实机完成。
真实 source_check 仍读取项目内完整104条独立合同，不接受缩减夹具替代。
"""
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import check_recipe_research_contract as checker

# 【变更记录 #1】2026-10-17 16:40:00（修订165）：新增授权组件重写的正例与五种恢复/遗漏/改料/随机产出反例；修改独立夹具不覆盖历史104条合同；用途：业务整族替换后仍严格检查权限和物料边界。


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def independent_payload_sha(row):
    # 独立计算预期，不调用被测检查器的 payload_sha 来自证。
    value = {key: entry for key, entry in row.items() if key != 'gates'}
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True,
                               separators=(',', ':')).encode('utf-8'))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def minimal_fixture():
    allowed = {'RN-ONE', 'RN-TWO', 'RN-THREE'}
    rows = [
        dict(id='gtceu:assembler/synthetic_one', type='gtceu:assembler',
             serializer='gtceu:gt_recipe_serializer', gates=['RN-ONE'],
             definition=dict(duration=200, inputs=dict(item=[dict(id='minecraft:iron_ingot', count=8)]),
                             outputs=dict(item=[dict(id='minecraft:iron_block', count=1)]))),
        dict(id='gtceu:assembler/synthetic_two', type='gtceu:assembler',
             serializer='gtceu:gt_recipe_serializer', gates=['RN-ONE', 'RN-TWO'],
             definition=dict(duration=400, inputs=dict(item=[dict(id='minecraft:gold_ingot', count=16)]),
                             outputs=dict(item=[dict(id='minecraft:gold_block', count=2)]))),
    ]
    migrations = [dict(id=row['id'], previous_requirements=['R-OLD-%03d' % (index + 1)],
                       requirements=list(row['gates']), reason='仅供合同回归的独立预期',
                       payload_sha256=independent_payload_sha(row))
                  for index, row in enumerate(rows)]
    return migrations, allowed, rows


def write_export(root, directory, migrations, allowed, rows, gates=None, report_overrides=None):
    # 这些根目录只存在于 TemporaryDirectory，不写项目正式合同或目录。
    write_json(root / checker.CONTRACT,
               dict(schema=1, before_export_sha256='0' * 64, migrations=migrations))
    write_json(root / checker.CATALOG,
               dict(schema=1, topics=[dict(id=entry) for entry in sorted(allowed)]))
    directory.mkdir(parents=True)
    write_json(directory / 'manifest.json', dict(schema=1, synthetic_test_only=True))
    write_json(directory / 'registries.json', dict(recipe_types=['gtceu:assembler']))
    (directory / 'recipes.jsonl').write_text(
        ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows), encoding='utf-8')
    if gates is None:
        effective = [dict(id=row['id'], requirements=list(row['gates']), invalid=[])
                     for row in rows if row.get('gates')]
        gates = dict(passed=True, snapshot_unchanged=True, invalid=[], orphan_bindings=[],
                     registered_gated_recipes=len(effective), recipes=effective)
    write_json(directory / 'research-gates.json', gates)
    report = dict(export_complete=True, recipe_snapshot_unchanged=True,
                  registered_recipe_export_complete=True, process_recipe_audit_pass=True,
                  research_gate_audit_pass=True)
    if report_overrides:
        report.update(report_overrides)
    report['sha256'] = {name: sha_bytes((directory / name).read_bytes())
                        for name in ('manifest.json', 'registries.json', 'recipes.jsonl',
                                     'research-gates.json')}
    write_json(directory / 'report.json', report)


def main():
    project_root = Path(__file__).resolve().parents[1]
    migrations, allowed, baseline = minimal_fixture()
    results = []

    def record(name, result, expected_pass, error_fragment=None):
        errors = result.get('errors', [])
        matched = result.get('passed') is expected_pass
        if error_fragment is not None:
            matched = matched and any(error_fragment in error for error in errors)
        results.append(dict(case=name, passed=matched, expected_pass=expected_pass,
                            observed_errors=errors))

    def rows_case(name, rows, expected_pass=False, error_fragment=None):
        result, _ = checker.check_rows(migrations, allowed, rows)
        record(name, result, expected_pass, error_fragment)

    rows_case('valid_independent_rows', deepcopy(baseline), True)
    reordered = deepcopy(baseline)
    reordered[1]['gates'].reverse()
    rows_case('valid_prerequisite_order_is_not_semantic', reordered, True)
    restored = deepcopy(baseline)
    restored[0]['gates'] = ['R-OLD-001']
    rows_case('reject_restored_legacy_gate', restored, error_fragment='非法研究门槛')
    missing_second = deepcopy(baseline)
    missing_second[1]['gates'] = ['RN-ONE']
    rows_case('reject_only_first_prerequisite', missing_second, error_fragment='独立合同不一致')
    changed_count = deepcopy(baseline)
    changed_count[0]['definition']['inputs']['item'][0]['count'] = 7
    rows_case('reject_changed_ingredient_count', changed_count, error_fragment='配方内容发生变化')
    changed_duration = deepcopy(baseline)
    changed_duration[1]['definition']['duration'] = 399
    rows_case('reject_changed_duration', changed_duration, error_fragment='配方内容发生变化')
    rows_case('reject_deleted_migrated_recipe', deepcopy(baseline[:1]), error_fragment='缺少迁移后的实际配方')
    rows_case('reject_duplicate_migrated_recipe', deepcopy(baseline + baseline[:1]),
              error_fragment='配方ID重复')
    illegal = deepcopy(baseline)
    illegal[1]['gates'] = ['RN-ONE', 'RN-UNKNOWN']
    rows_case('reject_unknown_current_gate', illegal, error_fragment='非法研究门槛')

    replacement = dict(retired_id=baseline[0]['id'], replacement_id='gtceu:assembler/new_component',
                       requirements=['RN-ONE'], output='hk3gtl:component_hcv',
                       previous_component='hk3gtl:component_hbv', material_input='hk3gtl:hcv_material_plate')
    def slot(item, count=1):
        return dict(alternatives=[dict(id=item, count=count)], chance=10000, max_chance=10000)
    new_row = dict(id=replacement['replacement_id'], gates=['RN-ONE'],
                   resolved_inputs=dict(items=[slot(replacement['previous_component'], 2), slot(replacement['material_input'], 4)]),
                   resolved_outputs=dict(items=[slot(replacement['output'])]))
    replacement_rows = [deepcopy(baseline[1]), new_row]
    def replacement_case(name, rows, expected_pass=False, error_fragment=None):
        outcome, _ = checker.check_rows(migrations, allowed, rows, [replacement])
        record(name, outcome, expected_pass, error_fragment)
    replacement_case('valid_authorized_material_replacement', deepcopy(replacement_rows), True)
    replacement_case('reject_old_component_side_route', deepcopy(replacement_rows + baseline[:1]), error_fragment='旧组件配方被恢复')
    replacement_case('reject_missing_replacement', deepcopy(replacement_rows[:1]), error_fragment='缺少主材替换')
    changed = deepcopy(replacement_rows)
    changed[-1]['gates'] = ['RN-TWO']
    replacement_case('reject_replacement_missing_research', changed, error_fragment='丢失研究前置')
    changed = deepcopy(replacement_rows)
    changed[-1]['resolved_inputs']['items'][1] = slot('minecraft:iron_ingot')
    replacement_case('reject_replacement_wrong_material', changed, error_fragment='未实际消耗')
    changed = deepcopy(replacement_rows)
    changed[-1]['resolved_outputs']['items'][0]['chance'] = 5000
    replacement_case('reject_replacement_chance_output', changed, error_fragment='没有确定产出')

    with tempfile.TemporaryDirectory(prefix='recipe-research-contract-synthetic-') as temporary:
        base = Path(temporary)
        fixture_root = base / 'root'

        def runtime_case(name, rows=None, gates=None, report=None, corrupt=None,
                         expected_pass=False, error_fragment=None):
            directory = base / name
            write_export(fixture_root, directory, migrations, allowed,
                         deepcopy(baseline) if rows is None else rows, gates, report)
            if corrupt is not None:
                # 报告产生后改实际文件，必须被文件完整性检查拒绝。
                with (directory / corrupt).open('a', encoding='utf-8') as stream:
                    stream.write('\n')
            outcome = checker.runtime_check(fixture_root, directory)
            record(name, outcome, expected_pass, error_fragment)

        runtime_case('valid_complete_export', expected_pass=True)
        runtime_case('valid_reordered_prerequisites_export', rows=reordered, expected_pass=True)
        for name in ('manifest.json', 'registries.json', 'recipes.jsonl', 'research-gates.json'):
            runtime_case('reject_tampered_' + name.replace('.', '_'), corrupt=name,
                         error_fragment='哈希错误')
        valid_gates = dict(passed=True, snapshot_unchanged=True, invalid=[], orphan_bindings=[],
                           registered_gated_recipes=2,
                           recipes=[dict(id=row['id'], requirements=list(row['gates']), invalid=[])
                                    for row in baseline])
        stale = deepcopy(valid_gates)
        stale['snapshot_unchanged'] = False
        runtime_case('reject_stale_gate_snapshot', gates=stale, error_fragment='快照变化')
        runtime_case('reject_failed_gate_export_protocol', report={'research_gate_audit_pass': False},
                     error_fragment='research_gate_audit_pass')
        invalid_metadata = deepcopy(valid_gates)
        invalid_metadata['invalid'] = [dict(id='hk3gtl:synthetic/metadata', reason='未知PLAN元数据')]
        runtime_case('reject_invalid_plan_metadata', gates=invalid_metadata,
                     error_fragment='非法条件')
        invalid_effective = deepcopy(valid_gates)
        invalid_effective['recipes'][1]['requirements'] = ['RN-ONE', 'RN-UNKNOWN']
        runtime_case('reject_invalid_effective_metadata_gate', gates=invalid_effective,
                     error_fragment='有效权限记录非法')
        omitted_effective = deepcopy(valid_gates)
        omitted_effective['recipes'][1]['requirements'] = ['RN-ONE']
        runtime_case('reject_effective_snapshot_only_first_prerequisite', gates=omitted_effective,
                     error_fragment='有效权限遗漏已注册前置')
        malformed_effective = deepcopy(valid_gates)
        malformed_effective['recipes'][1]['requirements'] = {'RN-ONE': True, 'RN-TWO': True}
        runtime_case('reject_non_list_effective_requirements', gates=malformed_effective,
                     error_fragment='有效权限记录非法')
        orphan = deepcopy(valid_gates)
        orphan['orphan_bindings'] = [dict(id='hk3gtl:synthetic/missing', requirements=['RN-ONE'])]
        runtime_case('reject_orphan_gate_binding', gates=orphan, error_fragment='孤立绑定')

    # 必须读取真实完整项目，不能把上面的两条临时合同冒充104条源合同。
    actual_source = checker.source_check(project_root)
    source_pass = (actual_source.get('passed') is True
                   and actual_source.get('migrated_recipe_count') == 104
                   and actual_source.get('scanned_java_files', 0) > 6)
    results.append(dict(case='real_source_contract_remains_104', passed=source_pass,
                        expected_pass=True, observed_errors=actual_source.get('errors', [])))
    result = dict(revision=165, checked_at=datetime.now().astimezone().isoformat(timespec='seconds'),
                  synthetic_tests_only=True, production_sources_modified=False,
                  production_runtime_verified=False, cases=len(results),
                  passed=all(row['passed'] for row in results), results=results)
    destination = project_root / 'logs/main-materials-r165/research-contract-negatives.json'
    write_json(destination, result)
    print(json.dumps(dict(passed=result['passed'], cases=len(results),
                          failed=[row['case'] for row in results if not row['passed']],
                          evidence=str(destination)), ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
