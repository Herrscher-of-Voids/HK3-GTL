"""Small synthetic negative tests for the retirement runtime contract.

Revision 162, 2026-10-17. Temporary fixtures are never production exports or
runtime evidence. No project Java/resources or actual game exports are changed.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import check_retired_recipe_contract as contract


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_export(directory, data):
    directory.mkdir()
    for name in ('manifest', 'registries'):
        (directory / (name + '.json')).write_text(json.dumps(data[name]), encoding='utf-8')
    (directory / 'recipes.jsonl').write_text(
        ''.join(json.dumps(recipe) + '\n' for recipe in data['recipes']), encoding='utf-8')
    report = deepcopy(data['report'])
    report['sha256'] = {name: digest(directory / name)
                        for name in ('manifest.json', 'registries.json', 'recipes.jsonl')}
    (directory / 'report.json').write_text(json.dumps(report), encoding='utf-8')


def fixture(retired):
    # Three recipes exercise identity coverage without copying the game dump.
    types = ['gtceu:industrial_synthetic_%02d' % index for index in range(50)]
    plans = ['synthetic_plan_%d' % index for index in range(3)]
    source = dict(process_plan_ids=plans, current_industrial_type_ids=types,
                  process_source_sha256=hashlib.sha256(b'synthetic plan source').hexdigest())
    retained = ['gtceu:' + entry['registry_name'] for entry in retired['retained']]
    recipes = [dict(id='hk3gtl:synthetic/' + plan, type=types[index],
                    definition=dict(type=types[index])) for index, plan in enumerate(plans)]
    data = dict(
        manifest=dict(schema=1, revision=108, captured_at='SYNTHETIC-TEST-ONLY', recipe_count=3,
                      process_table_sha256=source['process_source_sha256'], expected_process_plan_ids=plans),
        registries=dict(items=list(contract.INSTITUTE_ITEMS), fluids=[],
                        recipe_types=types + retained, recipe_serializers=types + retained),
        recipes=recipes,
        report=dict(schema=1, revision=108, export_complete=True, recipe_snapshot_unchanged=True,
                    process_recipe_audit_pass=True, registered_recipe_export_complete=True,
                    expected_process_recipes=3, passed_process_recipes=3,
                    process_table_sha256=source['process_source_sha256'], export_errors=[],
                    checks=[dict(plan=plan, failures=[], expected=recipe)
                            for plan, recipe in zip(plans, recipes)]))
    return source, data


def main():
    root = Path(__file__).resolve().parents[1]
    retired = contract.read_json(root / 'src/test/resources/contracts/retired_recipe_types.json')
    source, baseline = fixture(retired)
    old_id = retired['types'][0]['registry_id']
    results = []
    with tempfile.TemporaryDirectory(prefix='retired-contract-synthetic-') as temporary:
        base = Path(temporary)
        write_export(base / 'valid', baseline)
        valid = contract.runtime_check(base / 'valid', retired, source)
        if not valid['passed']:
            raise AssertionError('Synthetic valid baseline rejected: ' + repr(valid['errors']))

        def reject(name, data, expected_error, corrupt_hash=False):
            directory = base / name
            write_export(directory, data)
            if corrupt_hash:
                with (directory / 'recipes.jsonl').open('a', encoding='utf-8') as stream:
                    stream.write('\n')
            outcome = contract.runtime_check(directory, retired, source)
            passed = outcome['passed'] is False and expected_error in outcome['errors']
            results.append(dict(case=name, passed=passed, expected_error=expected_error,
                                observed_errors=outcome['errors']))

        restored = deepcopy(baseline)
        restored['registries']['recipe_types'].append(old_id)
        restored['registries']['recipe_serializers'].append(old_id)
        reject('restored_retired_type', restored, 'runtime_retired_type_still_registered')

        old_recipe = deepcopy(baseline)
        old_recipe['recipes'].append(dict(id='hk3gtl:synthetic/retired_recipe', type=old_id,
                                           definition=dict(type=old_id)))
        old_recipe['manifest']['recipe_count'] += 1
        reject('restored_retired_recipe', old_recipe, 'runtime_retired_recipe_types_present')

        for registry, expected_error in (
                ('recipe_types', 'runtime_current_industrial_types_missing'),
                ('recipe_serializers', 'runtime_current_type_serializers_missing')):
            missing = deepcopy(baseline)
            missing['registries'][registry].remove(source['current_industrial_type_ids'][0])
            reject('missing_current_' + registry, missing, expected_error)

        missing_plan = deepcopy(baseline)
        missing_plan['recipes'].pop()
        missing_plan['manifest']['recipe_count'] -= 1
        reject('deleted_current_process', missing_plan, 'runtime_current_process_recipes_missing')

        reject('corrupted_export_hash', baseline, 'export_sha256:recipes.jsonl', corrupt_hash=True)

    result = dict(synthetic_tests_only=True, production_sources_modified=False,
                  production_runtime_verified=False, valid_baseline_passed=True,
                  cases=len(results), passed=all(case['passed'] for case in results), results=results)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
