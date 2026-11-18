import hashlib
import json
import pathlib
import re
from collections import Counter
from datetime import datetime


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'deliveries/0003_全剩余电压工业链与材质交接_20261116'
RESOURCE = ROOT / 'src/main/resources/data/hk3gtl/research/approved_industrial_processes.json'
RECEIPT = ROOT / 'logs/industrial-integration-0003-20261117/recipes.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


ALIASES = {
    'hk3gtl:soulium_ingot': 'material:soulium/ingot',
    'hk3gtl:soulium_plate': 'material:soulium/plate',
    'hk3gtl:soulium_fine_wire': 'material:soulium/fine_wire',
    'hk3gtl:fine_soulium_wire': 'material:soulium/fine_wire',
    'gtceu:spacetime_plate': 'gtceu:spacetime_ingot',
}
MACHINES = {
    '超时空装配线': 'GTL_SUPRACHRONAL_ASSEMBLY_LINE',
    '精密组装机': 'GTL_PRECISION_ASSEMBLER',
    '电路装配线': 'GTL_CIRCUIT_ASSEMBLY_LINE',
    'SPS': 'GTL_SPS', '超临界合成机': 'GTL_SPS', '超临界合成机 SPS': 'GTL_SPS',
    '激光刻蚀机': 'GT_LASER_ENGRAVER', '化学浸洗机': 'GT_CHEMICAL_BATH',
    '大型挤压机 · 成型压机模式': 'GT_FORMING_PRESS', '成型压机': 'GT_FORMING_PRESS',
    '成型机': 'GT_FORMING_PRESS', '大型搅拌罐 · 混合工艺': 'GT_MIXER',
    '混合机': 'GT_MIXER', '大型组装厂 · 组装工艺': 'GT_ASSEMBLER', '组装机': 'GT_ASSEMBLER',
    '大型化学反应釜': 'GT_LARGE_CHEMICAL', '切割机': 'GT_CUTTER',
    '装罐机': 'GT_CANNER', '灌装机': 'GT_CANNER', '流体固化机': 'GT_FLUID_SOLIDIFIER',
    '崩坏能网络注入器': 'NETWORK_INJECTION', 'I01 崩坏能采集塔': 'I01-1',
}
VA = [2013265920 * 4 ** i for i in range(16)] + [9223372036854775807]
EXPERIMENTS = {'HBV:R13': 'RN-HSA', 'HBV:R14': 'RN-LSE', 'HBV:R18': 'RN-LES'}
FACTS = {
    'HRV:S04': ['nano_coating'],
    'HRV:S09': ['soulium_polymerization'], 'HRV:S19': ['soulium_polymerization'],
    'HRV:S12': ['soulium_reconstruction'],
    'HRV:S16': ['soulium_processing'], 'HRV:S17': ['soulium_processing'],
    'HRV:S18': ['soulium_processing'],
    'HCV:E08': ['circuit_etching'], 'HCV:E09': ['circuit_packaging'],
    'QAV:G02': ['drone_assembly'], 'QAV:G03': ['drone_assembly'],
}


def normalized(value):
    return ALIASES.get(value, value)


def role(recipe):
    machine = recipe['machine'].strip()
    if machine.startswith('大型化学浸洗机'):
        return 'GT_CHEMICAL_BATH'
    if machine in MACHINES:
        return MACHINES[machine]
    return re.match(r'[IWHS]\d\d(?:-\d)?', machine)[0]


def values(entries, fluid=False):
    return [{'id': normalized(v['id']), 'amount' if fluid else 'count': int(v['amount'])}
            for v in entries]


def recipe_id(recipe):
    return 'approved_' + re.sub(r'[^a-z0-9]+', '_', recipe['uid'].lower()).strip('_')


def plan(recipe, original=None):
    eut = int(recipe['eu'])
    power_tier = recipe.get('powerTier', 14 + next(i for i, voltage in enumerate(VA) if voltage >= eut))
    tools = [v for v in recipe['tools'] if v['id'] != 'gtceu:programmed_circuit']
    circuits = [v for v in recipe['tools'] if v['id'] == 'gtceu:programmed_circuit']
    facts = list(recipe.get('facts', [])) + FACTS.get(recipe['uid'], [])
    if recipe.get('fact'):
        facts.append(recipe['fact'])
    required = list(recipe.get('requiredFacts', []))
    required += re.findall(r'([a-z_]+)真实生产事实', recipe['gate'])
    if original:
        facts += original.get('facts', [])
    result = {
        'id': original['id'] if original else recipe_id(recipe),
        'design_uid': recipe['uid'], 'title': recipe['title'], 'role': role(recipe),
        'requirements': list(dict.fromkeys(re.findall(r'RN-[A-Z0-9]+', recipe['gate']))),
        'item_inputs': values(recipe['items']),
        'item_outputs': values([v for v in recipe['outputs'] if v['kind'] != 'fluid' and not v.get('settlement')]),
        'fluid_inputs': values(recipe['fluids'], True),
        'fluid_outputs': values([v for v in recipe['outputs'] if v['kind'] == 'fluid' and not v.get('settlement')], True),
        'item_catalysts': values(tools),
        'ticks': round(float(recipe['seconds']) * 20), 'energy_tier': power_tier,
        'stage_tier': recipe['tier'], 'energy_direction': 'input', 'input_eut': eut,
        'input_hw': int(recipe['hw']), 'facts': list(dict.fromkeys(facts)),
        'required_facts': list(dict.fromkeys(required)),
        'experiment': recipe.get('experiment', EXPERIMENTS.get(recipe['uid'], '')), 'provisional': False,
        'network_credit': int(recipe.get('hwBatch', recipe.get('hwOutput', 0))),
        'circuit': int(circuits[0].get('configuration', 0)) if circuits else (original or {}).get('circuit', 0),
    }
    return result


def main():
    design = read(SOURCE / 'recipes.json')['recipes']
    existing = read(SOURCE / 'existing-processes.json')['recipes']
    approved = [r for r in design if r.get('energyDirection') != 'output' and r.get('execution') != 'lab_queue']
    old = {}
    for file in (ROOT / 'src/main/resources/data/hk3gtl/research').glob('*processes.json'):
        if file != RESOURCE:
            old.update((r['id'], r) for r in read(file).get('recipes', []))
    modifications = [r for r in existing if r['sourceStatus'] == '既有工艺联接修订']
    plans = [plan(r) for r in approved] + [plan(r, old[r['id']]) for r in modifications]
    superseded = set(r['id'] for r in modifications)
    for r in design:
        replacements = r.get('replaces', [])
        for value in replacements if isinstance(replacements, list) else [replacements]:
            superseded.add(value.split(':')[-1])
    experiments = {r['experiment'] for r in plans if r['experiment']}
    main_outputs = {normalized(r['outputs'][0]['id']) for r in approved if not r.get('experiment')}
    for r in existing:
        if r['machine'].strip().startswith(('W', 'H')):
            continue
        if r.get('energyDirection') == 'output' or r['sourceStatus'] == '基础燃烧时长与热工修订':
            continue
        if r.get('experiment'):
            if r['experiment'] in experiments:
                superseded.add(r['id'])
        elif r['outputs'] and normalized(r['outputs'][0]['id']) in main_outputs:
            superseded.add(r['id'])
    superseded.update({
        'personal_phone', 'industrial_prototype_honkai_detector', 'i01_collection_controller',
        'i02_spectrum_controller', 'industrial_honkai_sample_canning', 'industrial_initial_spectrum',
        'hk3gtl_industrial_port_casing', 'industrial_liquid_honkai_fractionation_controller',
        'industrial_liquid_honkai_stabilization_tower_controller',
        'industrial_stabilization_medium_regeneration_tower_controller',
        'industrial_honkai_fuel_blending_controller', 'industrial_honkai_detector_calibration_controller',
        'industrial_soulium_precursor_mixing_controller', 'industrial_nano_basic_unit_synthesizer_controller',
        'industrial_nanobot_assembly_array_controller', 'industrial_nano_programming_chamber_controller',
        'industrial_honkai_resistant_coating_array_controller', 'industrial_soulium_polymerization_controller',
        'industrial_soulium_reconstruction_controller', 'industrial_soulium_precision_controller',
        'hk3gtl_honkai_network_injector', 'industrial_liquid_fractionation', 'industrial_liquid_purification',
        'industrial_fresh_stabilization_medium', 'industrial_fresh_honkai_coolant',
        'industrial_liquid_stabilization', 'industrial_stabilization_medium_recovery',
        'industrial_liquid_fuel_blending', 'industrial_circuit_adaptation_experiment',
        'industrial_inject_liquid_honkai_fuel', 'industrial_inject_stabilized_honkai',
        'hk3gtl_electronic_growth_medium', 'hk3gtl_electronic_etchant',
        'hk3gtl_electronic_lithography_mask', 'hk3gtl_electronic_etched_layer',
        'hk3gtl_electronic_encapsulation',
    })
    output = {
        'schema': 1, 'source': str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        'recipes': plans, 'superseded_ids': sorted(superseded),
        'superseded_prefixes': ['main_material/'],
        'source_count': len(design), 'new_recipe_count': len(approved),
        'modified_recipe_count': len(modifications),
        'lab_queue': [r['uid'] for r in design if r.get('execution') == 'lab_queue'],
        'energy_runtime_count': sum(r.get('energyDirection') == 'output' for r in design),
    }
    RESOURCE.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    def excluded(identifier):
        return (identifier in superseded
                or any(identifier[index + 1:] in superseded for index, char in enumerate(identifier) if char == '/')
                or any(identifier.startswith(prefix) or '/' + prefix in identifier
                       for prefix in output['superseded_prefixes']))
    groups = ['industrial', 'wonder', 'wonder_w01_w05', 'wonder_w06_w10', 'wonder_w11_w15']
    groups += [f'wonder_expansion_w{i:02}' for i in range(1, 16)] + ['reactor_fuel']
    originals = [recipe for group in groups for recipe in
                 read(RESOURCE.parent / f'{group}_processes.json')['recipes']]
    retained = [r for r in originals if not excluded(r['id'])]
    merged = retained + plans
    ordinary = [r for r in merged if r['role'] not in {'I19', 'I20', 'I21', 'I22'}]
    reactors = read(RESOURCE.parent / 'reactor_fuel_processes.json')['reactor_recipes']
    replaced = [r for r in existing if excluded(r['id'])
                or r['machine'].strip().startswith(('I19 ', 'I20 ', 'I21 ', 'I22 '))]
    registry_path = ROOT / 'deliveries/0003_MAX全配方对照_20261116/evidence/registries.json'
    registry = read(registry_path)
    external = {}
    for kind, keys in [('items', ['item_inputs', 'item_outputs', 'item_catalysts']),
                       ('fluids', ['fluid_inputs', 'fluid_outputs'])]:
        ids = {entry['id'] for recipe in plans for key in keys for entry in recipe[key]
               if ':' in entry['id'] and not entry['id'].startswith(('hk3gtl:', 'material:', '#'))}
        registered = set(registry['items'] if kind == 'items' else [v['id'] for v in registry['fluids']])
        external[kind] = {'distinct_ids': len(ids), 'missing': sorted(ids - registered)}
    receipt = {
        'updated_at': datetime.now().astimezone().isoformat(), 'production_resource': str(RESOURCE.relative_to(ROOT)),
        'new_registered_plans': len(approved), 'modified_registered_plans': len(modifications),
        'total_registered_plans': len(plans), 'roles': dict(Counter(r['role'] for r in plans)),
        'superseded_ids': len(superseded), 'superseded_prefixes': output['superseded_prefixes'],
        'lab_queue': output['lab_queue'], 'energy_runtime_excluded': output['energy_runtime_count'],
        'aliases': ALIASES, 'source_hashes': {f: hashlib.sha256((SOURCE / f).read_bytes()).hexdigest()
            for f in ['recipes.json', 'existing-processes.json', 'research.json']},
        'experiments': {r['experiment']: {'recipe': r['id'], 'executor': r['role']}
            for r in plans if r['experiment']},
        'native_tag_inputs': sorted({v['id'] for r in plans for v in r['item_inputs'] if v['id'].startswith('#')}),
        'exact_hw_plans': sum(r['input_hw'] > 0 for r in plans),
        'fixed_duration_plans': len(plans),
        'existing_catalog': {'total': len(existing), 'replaced': len(replaced),
            'retained': len(existing) - len(replaced),
            'replaced_by_source': dict(Counter(r['sourceStatus'] for r in replaced))},
        'production_plan_load': {'original_resource_plans': len(originals),
            'original_resource_replaced': len(originals) - len(retained),
            'original_resource_retained': len(retained), 'approved_plans': len(plans),
            'before_reactor_expand': len(merged), 'old_reactor_plans_removed': len(merged) - len(ordinary),
            'reactor_runtime_plans': len(reactors), 'final_loaded_plans': len(ordinary) + len(reactors),
            's01_exclusive_lab_queue': output['lab_queue']},
        'external_registry': {'path': str(registry_path.relative_to(ROOT)),
            'sha256': hashlib.sha256(registry_path.read_bytes()).hexdigest(), **external},
        'form_mapping': {'design_uid': 'WFV:F01', 'original': 'gtceu:spacetime_plate',
            'production': 'gtceu:spacetime_ingot', 'count': 128,
            'reason': '原包没有时空板形态，以等体积时空锭投入I16加工为界面功能层；批准原文保留'},
        'build': '由根代理执行独立生产编译与资源处理',
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ['new_registered_plans', 'modified_registered_plans',
          'total_registered_plans', 'superseded_ids', 'lab_queue', 'exact_hw_plans']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
