"""修订163：核对整套现行配方研究权限，使用独立迁移清单与真实导出，不授予任何研究。"""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from check_retired_recipe_contract import java_tokens

# 【变更记录 #1】2026-10-17 16:40:00（修订165）：保留104条历史内容合同；新增授权组件替换校验，旧路线必须消失、新路线必须保留权限并实际消耗同阶主材和前级组件；用途：重写业务后仍拒绝旧配方恢复、权限丢失和用料旁路。

CONTRACT = 'src/test/resources/contracts/current_recipe_research.json'
CATALOG = 'src/main/resources/data/hk3gtl/research/research_catalog.json'
TIERS = ('ulv', 'lv', 'mv', 'hv', 'ev', 'iv', 'luv', 'zpm', 'uv', 'uhv', 'uev', 'uiv', 'uxv', 'opv', 'max')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def payload_sha(row):
    payload = {key: value for key, value in row.items() if key != 'gates'}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def allowed_ids(root):
    topics = {entry['id'] for entry in read(root / CATALOG)['topics']}
    return topics | {'RN-RCA/circuit/' + tier for tier in TIERS}


def source_check(root):
    fixture = read(root / CONTRACT)
    migrations = fixture['migrations']
    allowed = allowed_ids(root)
    errors = []
    if len(migrations) != 104 or len({row['id'] for row in migrations}) != 104:
        errors.append('迁移合同必须独立覆盖104条唯一配方')
    for row in migrations:
        if not row['previous_requirements'] or not all(re.fullmatch(r'R-[A-Z]+-\d+', value) for value in row['previous_requirements']):
            errors.append('缺少原始旧门槛：' + row['id'])
        if not row['requirements'] or any(value not in allowed for value in row['requirements']):
            errors.append('迁移目标不是现行权限：' + row['id'])
        if len(set(row['requirements'])) != len(row['requirements']) or not re.fullmatch('[0-9a-f]{64}', row.get('payload_sha256', '')):
            errors.append('合同存在重复条件或无效原始内容哈希：' + row['id'])
    replacements = fixture.get('replacements', [])
    if replacements:
        previous = {row['id']: row for row in migrations}
        if len(replacements) != 88 or len({row['retired_id'] for row in replacements}) != 88:
            errors.append('主材重写必须精确替换88条已迁移组件路线')
        for row in replacements:
            if row['retired_id'] not in previous or row['requirements'] != previous[row['retired_id']]['requirements']:
                errors.append('组件替换不可丢失历史研究前置：' + row['retired_id'])
            if not row['replacement_id'].startswith('gtceu:assembler/hk3gtl_main_component_'):
                errors.append('替换路线必须使用集中主材消费者：' + row['replacement_id'])
    scanned = 0
    sources = list((root / 'src/main/java/com/sirin/hk3gtl/common/recipe').rglob('*.java'))
    sources.append(root / 'src/main/java/com/sirin/hk3gtl/common/research/Hk3RecipeResearchGate.java')
    for path in sources:
        scanned += 1
        for kind, token, line in java_tokens(path.read_text(encoding='utf-8-sig')):
            if kind == 'string' and re.fullmatch(r'R-[A-Z]+-\d+', token):
                errors.append(f'{path.relative_to(root)}:{line} 仍存在活动旧研究门槛 {token}')
            if path.name == 'Hk3RecipeResearchGate.java' and kind == 'identifier' and token in ('LEGACY_NODE_REDIRECT', 'Hk3ResearchNodes'):
                errors.append(f'现行配方注册不能回退旧研究：{token}')
    return dict(passed=not errors, migrated_recipe_count=len(migrations), scanned_java_files=scanned, errors=errors)


def check_rows(migrations, allowed, rows, replacements=()):
    retired = {row['retired_id'] for row in replacements}
    replacement_map = {row['replacement_id']: row for row in replacements}
    expected = {row['id']: row for row in migrations if row['id'] not in retired}
    seen = set()
    replacement_seen = set()
    errors = []
    count = gated = 0
    registered = {}
    for row in rows:
        count += 1
        recipe_id = row.get('id', '')
        gates = row.get('gates')
        if not isinstance(gates, list) or any(not isinstance(value, str) or value not in allowed for value in gates):
            errors.append('实际配方含非法研究门槛：' + recipe_id)
            continue
        if gates:
            gated += 1
            registered[recipe_id] = gates
        if recipe_id in retired:
            errors.append('已授权替换的旧组件配方被恢复：' + recipe_id)
        if recipe_id in replacement_map:
            contract = replacement_map[recipe_id]
            if recipe_id in replacement_seen:
                errors.append('实际替换配方ID重复：' + recipe_id)
            replacement_seen.add(recipe_id)
            if sorted(gates) != sorted(contract['requirements']):
                errors.append('替换配方丢失研究前置：' + recipe_id)
            inputs = row.get('resolved_inputs', {}).get('items', [])
            guaranteed = {slot['alternatives'][0]['id'] for slot in inputs
                          if len(slot.get('alternatives', [])) == 1
                          and slot.get('chance', 0) == slot.get('max_chance', 10000)
                          and slot['alternatives'][0].get('count', 0) > 0}
            if not {contract['previous_component'], contract['material_input']} <= guaranteed:
                errors.append('替换配方未实际消耗前级组件或本阶主材：' + recipe_id)
            outputs = row.get('resolved_outputs', {}).get('items', [])
            if not any(slot.get('alternatives') == [dict(id=contract['output'], count=1)]
                       and slot.get('chance', 0) == slot.get('max_chance', 10000) for slot in outputs):
                errors.append('替换配方没有确定产出一件本阶组件：' + recipe_id)
        if recipe_id not in expected:
            continue
        if recipe_id in seen:
            errors.append('实际配方ID重复：' + recipe_id)
        seen.add(recipe_id)
        contract = expected[recipe_id]
        if sorted(gates) != sorted(contract['requirements']):
            errors.append('实际门槛与独立合同不一致：' + recipe_id)
        if payload_sha(row) != contract['payload_sha256']:
            errors.append('门槛以外的配方内容发生变化：' + recipe_id)
    for recipe_id in expected.keys() - seen:
        errors.append('缺少迁移后的实际配方：' + recipe_id)
    for recipe_id in replacement_map.keys() - replacement_seen:
        errors.append('缺少主材替换后的实际配方：' + recipe_id)
    return dict(passed=not errors, recipe_count=count, registered_gated_recipes=gated,
                migrated_recipes_found=len(seen), replaced_recipes_found=len(replacement_seen), errors=errors), registered


def runtime_check(root, directory):
    errors = []
    report = read(directory / 'report.json')
    for key in ('export_complete', 'recipe_snapshot_unchanged', 'registered_recipe_export_complete', 'process_recipe_audit_pass', 'research_gate_audit_pass'):
        if report.get(key) is not True:
            errors.append('真实导出未通过：' + key)
    for name in ('manifest.json', 'registries.json', 'recipes.jsonl', 'research-gates.json'):
        path = directory / name
        if not path.is_file() or report.get('sha256', {}).get(name) != sha(path):
            errors.append('真实导出缺失或哈希错误：' + name)
    if errors:
        return dict(passed=False, errors=errors)
    allowed = allowed_ids(root)
    fixture = read(root / CONTRACT)
    with (directory / 'recipes.jsonl').open(encoding='utf-8-sig') as stream:
        result, registered = check_rows(fixture['migrations'], allowed, (json.loads(line) for line in stream if line.strip()), fixture.get('replacements', []))
    gate_report = read(directory / 'research-gates.json')
    if gate_report.get('passed') is not True or gate_report.get('snapshot_unchanged') is not True or gate_report.get('invalid') or gate_report.get('orphan_bindings'):
        errors.append('完整有效门槛核验存在非法条件、孤立绑定或快照变化')
    effective = {}
    for row in gate_report.get('recipes', []):
        if row['id'] in effective or row.get('invalid') or not isinstance(row.get('requirements'), list) or any(value not in allowed for value in row['requirements']):
            errors.append('实际有效权限记录非法：' + row['id'])
        effective[row['id']] = row.get('requirements', [])
    if gate_report.get('registered_gated_recipes') != len(effective):
        errors.append('完整有效门槛统计不一致')
    for recipe_id, gates in registered.items():
        if not set(gates).issubset(effective.get(recipe_id, [])):
            errors.append('有效权限遗漏已注册前置：' + recipe_id)
    errors += result['errors']
    return dict(passed=not errors, directory=str(directory), registered_recipe_count=result['recipe_count'],
                migrated_recipes_found=result['migrated_recipes_found'], registered_gated_recipes=result['registered_gated_recipes'],
                replaced_recipes_found=result['replaced_recipes_found'],
                effective_gated_recipes=len(effective), errors=errors)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = dict(revision=165, checked_at=datetime.now().astimezone().isoformat(), source=source_check(root),
                  gameplay_verified=False, multiplayer_verified=False,
                  boundary='保留104条历史权限合同，88条组件由独立主材替换表取代、其余16条仍保持原内容；未提供新运行导出时不能称实例配方通过。')
    if args.runtime:
        result['runtime'] = runtime_check(root, args.runtime)
    result['passed'] = result['source']['passed'] and result.get('runtime', {}).get('passed', True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
