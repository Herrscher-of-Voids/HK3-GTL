"""Verify retired recipe contracts in active Java and optional real runtime exports.

Revision 162, 2026-10-17 14:40:28 Asia/Hong_Kong. Read-only checks;
JSON output distinguishes source cleanup, runtime registration, and gameplay.
The runtime schema is the actual research audit export: manifest.json,
registries.json (items/fluids), recipes.jsonl, and report.json (schema 1).
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys


JAVA_TOKEN = re.compile(
    r'(?P<comment>//[^\r\n]*|/\*.*?\*/)'
    r'|(?P<text>""".*?""")'
    r'|(?P<string>"(?:\\.|[^"\\])*")'
    r"|(?P<char>'(?:\\.|[^'\\])*')"
    r'|(?P<identifier>[A-Za-z_$][A-Za-z0-9_$]*)', re.DOTALL)
JAVA_UNICODE = re.compile(r'\\u+([0-9a-fA-F]{4})')
INSTITUTE_ITEMS = (
    'hk3gtl:abyss_research_analysis_matrix',
    'hk3gtl:s02_matter_reconstruction_institute',
    'hk3gtl:s03_quantum_domain_institute',
    'hk3gtl:s04_world_maintenance_institute',
    'hk3gtl:s05_civilization_cognition_dome',
)
SOURCE_ROOTS = ('src/main/java', 'src/test/java')
PROCESS_PATH = 'src/main/resources/data/hk3gtl/research/industrial_processes.json'
TYPE_SOURCE = 'src/main/java/com/sirin/hk3gtl/common/recipe/Hk3IndustrialRecipeTypes.java'
ROLE_SOURCE = 'src/main/java/com/sirin/hk3gtl/common/recipe/Hk3ResearchProcessTypes.java'


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def java_tokens(source: str):
    """Skip comments and character literals; retain code and active strings.

    Java Unicode escapes are translated before lexical classification, just as
    the compiler does. A quoted field name in historical Javadoc is ignored;
    an active registration/gate string is checked by its exact identity.
    """
    source = JAVA_UNICODE.sub(lambda match: chr(int(match[1], 16)), source)
    for match in JAVA_TOKEN.finditer(source):
        kind = match.lastgroup
        if kind in ('comment', 'char'):
            continue
        value = match.group()
        if kind == 'string':
            value = value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
        elif kind == 'text':
            value = value[3:-3].strip()
        yield kind, value, source.count('\n', 0, match.start()) + 1


def token_contract_self_check() -> bool:
    sample = ('// OLD_FIELD "old_type"\n/* OLD_FIELD "old_type" */\n'
              'String unrelated = "OLD_FIELD"; char slash = \'/\';\n'
              'Object active = OLD_FIELD; register("old_type");')
    tokens = list(java_tokens(sample))
    return (sum(kind == 'identifier' and value == 'OLD_FIELD'
                for kind, value, _ in tokens) == 1
            and sum(kind == 'string' and value == 'old_type'
                    for kind, value, _ in tokens) == 1)


def recipe_type_string_context(text: str, line: int, path: str, retired_sources: set) -> bool:
    """Bare names can also be valid circuit families or machine identifiers.

    Only type registration, type gate, and recipe-type collection contexts make
    an unqualified name a retired *recipe-type* reference. Full gtceu IDs are
    always checked. Other name mentions remain visible as review information.
    """
    if path in retired_sources:
        return True
    cleaned = JAVA_TOKEN.sub(
        lambda match: re.sub(r'[^\n]', ' ', match.group())
        if match.lastgroup == 'comment' else match.group(), text)
    lines = cleaned.splitlines(keepends=True)
    line_start = sum(map(len, lines[:line - 1]))
    line_end = line_start + len(lines[line - 1]) if line <= len(lines) else len(cleaned)
    statement_start = cleaned.rfind(';', 0, line_start) + 1
    statement = cleaned[statement_start:line_end]
    return bool(re.search(
        r'GTRecipeTypes\s*\.\s*register|Hk3RecipeResearchGate\s*\.\s*bind'
        r'|\b\w*RECIPE_TYPES?\w*\b|\brecipeTypes?\s*\(', statement))


def source_check(root: Path, manifest: dict, expected_count: int) -> dict:
    errors, findings, files, other_name_mentions = [], [], [], []
    retired = manifest.get('types', [])
    fields = {entry['field'] for entry in retired}
    registry_strings = {entry['registry_name'] for entry in retired}
    registry_strings.update(entry['registry_id'] for entry in retired)
    full_registry_ids = {entry['registry_id'] for entry in retired}
    retired_sources = {entry['source'] for entry in retired}
    if len(retired) != 88 or manifest.get('count') != 88:
        errors.append('retired_manifest_count_must_be_88')
    if len(fields) != len(retired) or len({entry['registry_id'] for entry in retired}) != len(retired):
        errors.append('retired_manifest_identity_not_unique')
    if not token_contract_self_check():
        errors.append('java_token_contract_self_check')
    tokens_by_file = {}
    for relative in SOURCE_ROOTS:
        source_root = root / relative
        if not source_root.is_dir():
            errors.append('missing_source_root:' + relative)
            continue
        for path in sorted(source_root.rglob('*.java')):
            relative_path = path.relative_to(root).as_posix()
            files.append(relative_path)
            text = path.read_text(encoding='utf-8-sig')
            tokens = list(java_tokens(text))
            tokens_by_file[relative_path] = tokens
            for kind, value, line in tokens:
                if kind == 'identifier' and value in fields:
                    findings.append(dict(file=relative_path, line=line,
                                         kind='retired_field', value=value))
                elif kind in ('string', 'text') and value in registry_strings:
                    mention = dict(file=relative_path, line=line,
                                   kind='retired_registry_reference', value=value)
                    if value in full_registry_ids or recipe_type_string_context(
                            text, line, relative_path, retired_sources):
                        findings.append(mention)
                    else:
                        mention['kind'] = 'unqualified_name_other_context'
                        other_name_mentions.append(mention)
    if findings:
        errors.append('active_java_contains_retired_contracts')

    retained_checks = []
    for entry in manifest.get('retained', []):
        tokens = tokens_by_file.get(entry['source'], [])
        field_present = any(kind == 'identifier' and value == entry['field']
                            for kind, value, _ in tokens)
        registration_present = any(kind == 'string' and value == entry['registry_name']
                                   for kind, value, _ in tokens)
        bindings = []
        for path, file_tokens in tokens_by_file.items():
            if '/machine/' not in path:
                continue
            identifiers = [(value, line) for kind, value, line in file_tokens if kind == 'identifier']
            for index in range(len(identifiers) - 2):
                if [value for value, _ in identifiers[index:index + 3]] == [
                        'recipeType', 'Hk3RecipeTypes', entry['field']]:
                    bindings.append(dict(file=path, line=identifiers[index][1]))
        ok = field_present and registration_present and len(bindings) >= 2
        retained_checks.append(dict(field=entry['field'], registered_in_source=registration_present,
                                    declared_in_source=field_present, institute_bindings=bindings, passed=ok))
        if not ok:
            errors.append('retained_institute_contract:' + entry['field'])
    if not retained_checks:
        errors.append('missing_retained_institute_contract')

    processes = read_json(root / PROCESS_PATH)
    plans = [plan['id'] for plan in processes['recipes']]
    if len(plans) != expected_count or len(set(plans)) != expected_count:
        errors.append('current_process_source_identity_count')
    static_types = {value for kind, value, _ in java_tokens((root / TYPE_SOURCE).read_text(encoding='utf-8-sig'))
                    if kind == 'string' and value.startswith('industrial_')}
    role_source = (root / ROLE_SOURCE).read_text(encoding='utf-8-sig')
    if not re.search(r'for\s*\(\s*int\s+i\s*=\s*8\s*;\s*i\s*<=\s*45\s*;\s*i\+\+\s*\)\s*if\s*\(\s*i\s*!=\s*17\s*\)', role_source):
        errors.append('dynamic_role_contract_changed_review_required')
    roles = ['I01-2', 'I01-3', 'I01-4'] + ['I%02d' % value for value in range(8, 46) if value != 17]
    industrial_ids = sorted({'gtceu:' + name for name in static_types}
                            | {'gtceu:industrial_process_' + role.lower().replace('-', '_') for role in roles})
    if len(static_types) != 10 or len(industrial_ids) != 50:
        errors.append('current_industrial_type_identity_count')
    return dict(passed=not errors, scanned_java_files=len(files), source_roots=list(SOURCE_ROOTS),
                ignored='Java comments, character literals, archive/, build/, logs/; exact tokens avoid substring matches',
                retired_type_count=len(retired), findings=findings,
                unqualified_name_mentions_for_review=other_name_mentions, retained=retained_checks,
                current_industrial_type_ids=industrial_ids,
                current_process_count=len(plans), process_plan_ids=sorted(plans),
                process_source_sha256=sha256(root / PROCESS_PATH), errors=errors)


def runtime_check(directory: Path, manifest: dict, source: dict) -> dict:
    errors = []
    runtime_manifest = read_json(directory / 'manifest.json')
    report = read_json(directory / 'report.json')
    registries = read_json(directory / 'registries.json')
    if runtime_manifest.get('schema') != 1 or report.get('schema') != 1:
        errors.append('unsupported_runtime_export_schema')
    registry_sets = {}
    for registry in ('recipe_types', 'recipe_serializers'):
        values = registries.get(registry)
        if not isinstance(values, list) or not values or not all(isinstance(value, str) for value in values):
            errors.append('runtime_registry_not_exported:' + registry)
            values = []
        registry_sets[registry] = set(values)
    retired_ids = {entry['registry_id'] for entry in manifest['types']}
    retired_registered = sorted(retired_ids & registry_sets['recipe_types'])
    retired_serializer_ids = sorted(retired_ids & registry_sets['recipe_serializers'])
    if retired_registered:
        errors.append('runtime_retired_type_still_registered')
    if retired_serializer_ids:
        errors.append('runtime_retired_id_registered_as_serializer')
    retained_ids = {'gtceu:' + entry['registry_name'] for entry in manifest.get('retained', [])}
    missing_current_types = sorted(set(source['current_industrial_type_ids']) - registry_sets['recipe_types'])
    missing_retained_types = sorted(retained_ids - registry_sets['recipe_types'])
    if missing_current_types:
        errors.append('runtime_current_industrial_types_missing')
    if missing_retained_types:
        errors.append('runtime_institute_type_missing')
    # GTRecipeTypes.register registers a serializer under the same identifier.
    # The recipe snapshot's generic serializer label is not this registry key.
    missing_current_serializers = sorted(
        (set(source['current_industrial_type_ids']) | retained_ids) - registry_sets['recipe_serializers'])
    if missing_current_serializers:
        errors.append('runtime_current_type_serializers_missing')
    hashes = {}
    for name in ('manifest.json', 'registries.json', 'recipes.jsonl'):
        actual = sha256(directory / name)
        expected = report.get('sha256', {}).get(name)
        hashes[name] = dict(actual=actual, expected=expected, passed=actual == expected)
        if actual != expected:
            errors.append('export_sha256:' + name)
    for flag in ('export_complete', 'recipe_snapshot_unchanged', 'process_recipe_audit_pass',
                 'registered_recipe_export_complete'):
        if report.get(flag) is not True:
            errors.append('export_flag:' + flag)
    if report.get('export_errors'):
        errors.append('runtime_export_errors')
    expected_plans = set(source['process_plan_ids'])
    exported_plans = runtime_manifest.get('expected_process_plan_ids', [])
    if len(exported_plans) != len(expected_plans) or set(exported_plans) != expected_plans:
        errors.append('runtime_manifest_current_plan_identity')
    if (runtime_manifest.get('process_table_sha256') != source['process_source_sha256']
            or report.get('process_table_sha256') != source['process_source_sha256']):
        errors.append('runtime_current_process_source_hash')
    checks = report.get('checks', [])
    if len(checks) != len(expected_plans) or {check.get('plan') for check in checks} != expected_plans:
        errors.append('runtime_process_check_identity')
    expected_recipes = {}
    for check in checks:
        if check.get('failures') or check.get('audit_error'):
            errors.append('runtime_process_check:' + str(check.get('plan')))
        recipe = check.get('expected', {})
        if recipe.get('id'):
            expected_recipes[recipe['id']] = recipe.get('type')
    if len(expected_recipes) != len(expected_plans):
        errors.append('runtime_expected_recipe_identity')
    if (report.get('expected_process_recipes') != len(expected_plans)
            or report.get('passed_process_recipes') != len(expected_plans)):
        errors.append('runtime_passed_process_count')

    retired_hits, seen, found_processes, type_counts = [], set(), {}, Counter()
    recipe_count = 0
    with (directory / 'recipes.jsonl').open(encoding='utf-8-sig') as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            recipe = json.loads(line)
            recipe_count += 1
            recipe_id, recipe_type = recipe.get('id'), recipe.get('type')
            if not recipe_id or not recipe_type:
                errors.append('runtime_recipe_missing_identity:' + str(line_number))
            if recipe_id in seen:
                errors.append('runtime_duplicate_recipe:' + str(recipe_id))
            seen.add(recipe_id)
            type_counts[recipe_type] += 1
            serialized_type = recipe.get('definition', {}).get('type')
            if serialized_type and serialized_type != recipe_type:
                errors.append('runtime_type_mismatch:' + str(recipe_id))
            if recipe_type in retired_ids or serialized_type in retired_ids:
                retired_hits.append(dict(id=recipe_id, type=recipe_type, line=line_number))
            if recipe_id in expected_recipes:
                found_processes[recipe_id] = recipe_type
                if recipe_type != expected_recipes[recipe_id]:
                    errors.append('runtime_process_type:' + recipe_id)
    if retired_hits:
        errors.append('runtime_retired_recipe_types_present')
    missing = sorted(set(expected_recipes) - set(found_processes))
    if missing:
        errors.append('runtime_current_process_recipes_missing')
    if runtime_manifest.get('recipe_count') != recipe_count:
        errors.append('runtime_recipe_count_manifest')
    items = set(registries.get('items', []))
    missing_institutes = [item for item in INSTITUTE_ITEMS if item not in items]
    if missing_institutes:
        errors.append('runtime_institute_items_missing')
    return dict(passed=not errors, directory=str(directory),
                captured_at=runtime_manifest.get('captured_at'),
                exporter_revision=runtime_manifest.get('revision'),
                hashes=hashes, registered_recipe_count=recipe_count,
                recipe_type_registry_exported=bool(registry_sets['recipe_types']),
                recipe_serializer_registry_exported=bool(registry_sets['recipe_serializers']),
                retired_type_recipe_count=len(retired_hits), retired_type_recipes=retired_hits,
                retired_type_registered_count=(len(retired_registered) if registry_sets['recipe_types'] else None),
                retired_types_registered=retired_registered,
                retired_ids_registered_as_serializers=retired_serializer_ids,
                current_industrial_types_expected=len(source['current_industrial_type_ids']),
                missing_current_industrial_types=missing_current_types,
                missing_retained_institute_types=missing_retained_types,
                missing_current_type_serializers=missing_current_serializers,
                current_process_recipe_count=len(found_processes), missing_process_recipes=missing,
                institute_items_present=not missing_institutes, missing_institute_items=missing_institutes,
                retained_type_recipe_count={
                    entry['registry_name']: type_counts['gtceu:' + entry['registry_name']]
                    for entry in manifest.get('retained', [])},
                retained_type_runtime_registry_verified=not missing_retained_types,
                retained_type_boundary='The complete recipe-type and serializer registries are required. '
                    'Zero institute GT recipes is valid; its type and five institute items must remain registered.',
                errors=errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--retired-manifest', type=Path,
                        default=Path('src/test/resources/contracts/retired_recipe_types.json'))
    parser.add_argument('--runtime-dir', type=Path, help='Actual audit export directory; omit for source-only checks')
    # 修订213：新增魂钢基板与锭的正式工艺；退役检查仍要求准确数量和唯一身份。
    parser.add_argument('--expected-process-count', type=int, default=253)
    parser.add_argument('--output', type=Path, help='Optional JSON result file; stdout always receives JSON')
    args = parser.parse_args()
    root = args.project_root.resolve()
    manifest_path = args.retired_manifest
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    result = dict(revision=162, checked_at=datetime.now().astimezone().isoformat(),
                  project_root=str(root), retired_manifest=str(manifest_path),
                  gameplay_verified=False, survival_verified=False, multiplayer_verified=False,
                  boundary='Source retirement and runtime registration checks do not prove processing, '
                           'research progression, topology reachability, or 84/88 completed machines.')
    try:
        manifest = read_json(manifest_path)
        source = source_check(root, manifest, args.expected_process_count)
        result['source'] = source
        result['runtime'] = (runtime_check(args.runtime_dir.resolve(), manifest, source)
                             if args.runtime_dir else dict(status='NOT_REQUESTED', passed=None))
        result['passed'] = source['passed'] and (result['runtime']['passed'] is not False)
        result['scope'] = 'source_and_runtime' if args.runtime_dir else 'source_only'
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result.update(passed=False, error=type(exc).__name__ + ': ' + str(exc))
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + '\n', encoding='utf-8')
    print(rendered)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
