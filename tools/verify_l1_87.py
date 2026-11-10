"""修订87数量审计：直接解析限定范围的Java配方，核算启动与批次库存；不代替运行时注册或游戏验收。"""
from pathlib import Path
from collections import Counter
from datetime import datetime
import re
import json
import hashlib
import math

# 变更记录 #2 2026-09-27 02:33:00（修订87）：新增实际配方输入输出上限及注册入口核验；不替代游戏注册测试。

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'src/main/java/com/sirin/hk3gtl'
LOG = ROOT / 'logs/revision87'
recipes = {}

def block(text, name):
    pos = text.index('"' + name + '"')
    return text[pos:text.index('.save(provider);', pos)]

def amounts(body):
    result = Counter()
    expressions = [
        (r'(?:item|betaItem|fluid)\("([^"]+)",\s*(\d+)\)', lambda m: (m[1], int(m[2]))),
        (r'GTMaterials\.(\w+)\.getFluid\((\d+)\)', lambda m: ('gt.fluid.' + m[1], int(m[2]))),
        (r'Hk3Materials\.(\w+)\.getFluid\((\d+)\)', lambda m: ('hk.' + m[1], int(m[2]))),
        (r'new ItemStack\(HonkaiMaterialItems\.(\w+)\.get\(\),\s*(\d+)\)', lambda m: ('hk.' + m[1], int(m[2]))),
        (r'TagPrefix\.(\w+),\s*GTMaterials\.(\w+),\s*(\d+)', lambda m: ('gt.' + m[1] + '.' + m[2], int(m[3]))),
        (r'CustomTags\.(\w+),\s*(\d+)', lambda m: ('gt.tag.' + m[1], int(m[2]))),
    ]
    for expression, read in expressions:
        for match in re.finditer(expression, body):
            key, count = read(match)
            result[key] += count
    return result

def parse(name, body):
    value = {'in': Counter(), 'out': Counter(), 'standard': Counter()}
    for match in re.finditer(r'\.(inputItems|outputItems|inputFluids|outputFluids|notConsumable)\(', body):
        start = match.end()
        depth, end = 1, start
        while depth:
            if body[end] == '(':
                depth += 1
            elif body[end] == ')':
                depth -= 1
            end += 1
        target = 'standard' if match[1] == 'notConsumable' else 'in' if match[1].startswith('input') else 'out'
        parsed = amounts(body[start:end-1])
        assert parsed, (name, body[start:end-1])
        value[target].update(parsed)
    recipes[name] = value

main = (BASE / 'common/recipe/honkai/Hk3LiquidLineRecipes.java').read_text(encoding='utf-8')
loop = (BASE / 'common/recipe/honkai/Hk3LiquidLoopRecipes.java').read_text(encoding='utf-8')
material = (BASE / 'common/recipe/honkai/HonkaiMaterialRecipes.java').read_text(encoding='utf-8')
for source, names in [(main, ['liquid_fractionation', 'liquid_purification', 'fresh_stabilization_medium',
        'fresh_honkai_coolant', 'liquid_stabilization', 'stabilization_medium_recovery',
        'analysis_reagent_recovery', 'coolant_reconditioning', 'lost_coolant_treatment',
        'effluent_solidification', 'tail_material_treatment', 'inert_residue_disposal']),
        (loop, ['fresh_analysis_reagent', 'liquid_fractionation_reflux', 'impurity_purge', 'separation_residue_purge']),
        (material, ['honkai_crystal_seed'])]:
    for name in names:
        parse(name, block(source, 'industrial_' + name))

residual = main[main.index('recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_recover_'):]
residual = residual[:residual.index('.save(provider);')]
parse('recover_crystallization', residual.replace('fluid(residual,', 'fluid("crystallization_residual_liquid",'))
purge = loop[loop.index('recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_purge_'):]
purge = purge[:purge.index('.save(provider);')]
for name in re.search(r'for \(String excess : new String\[\]\{(.*?)\}', loop, re.S)[1].split(','):
    name = name.strip().strip('"')
    parse('purge_' + name, purge.replace('fluid(excess,', 'fluid("' + name + '",'))

def amount(recipe, side, key):
    return recipes[recipe][side][key]

assert amount('liquid_fractionation', 'out', 'crude_honkai_energy') == 5000
assert amount('liquid_stabilization', 'out', 'stabilized_liquid_honkai_energy') == 800
assert 4 * amount('liquid_purification', 'out', 'hk.RAW_HONKAI_PARTICLE') == 10 * amount('honkai_crystal_seed', 'in', 'hk.RAW_HONKAI_PARTICLE')
assert 10 * amount('honkai_crystal_seed', 'out', 'honkai_crystal_seed') == 5 * amount('liquid_stabilization', 'in', 'honkai_crystal_seed')
fresh = recipes['liquid_fractionation']
reflux = recipes['liquid_fractionation_reflux']
assert fresh['out'] == reflux['out']
assert reflux['in']['hk.LIQUID_HONKAI_ENERGY'] > 0
assert fresh['in']['hk.LIQUID_HONKAI_ENERGY'] == reflux['in']['hk.LIQUID_HONKAI_ENERGY'] + reflux['in']['clarified_honkai_mother_liquor']
assert all(reflux['in'][k] == v for k, v in fresh['in'].items() if k != 'hk.LIQUID_HONKAI_ENERGY')
assert amount('liquid_purification', 'out', 'clarified_honkai_mother_liquor') == reflux['in']['clarified_honkai_mother_liquor']

# 外供仅限已存在MAX制造入口的三类耗材、GT原料和I01新采液；所有工艺中间物库存从零开始。
supplied = {'separation_filter', 'directional_crystallization_matrix', 'fuel_matrix', 'hk.LIQUID_HONKAI_ENERGY'}
for key in supplied - {'hk.LIQUID_HONKAI_ENERGY'}:
    assert '"industrial_' + key + '"' in material
    body = block(material, 'industrial_' + key)
    assert 'Hk3LiquidLineRecipes.fluid' not in body and 'RAW_HONKAI_PARTICLE' not in body
external = Counter()
inventory = Counter()
runs = Counter()
exports = Counter()

def run(name, times=1):
    for _ in range(times):
        recipe = recipes[name]
        for key, value in recipe['in'].items():
            if key.startswith('gt.') or key in supplied:
                external[key] += value
            else:
                assert inventory[key] >= value, (name, key, inventory[key], value)
                inventory[key] -= value
        inventory.update(recipe['out'])
        runs[name] += 1

def fill(key, required, recipe):
    while inventory[key] < required:
        run(recipe)

def consume_all(key, recipe):
    threshold = recipes[recipe]['in'][key]
    while inventory[key] >= threshold:
        run(recipe)

def production(fractionation):
    run(fractionation, 4)
    run('liquid_purification', 4)
    run('honkai_crystal_seed', 10)
    fill('honkai_stabilization_medium', 5000, 'fresh_stabilization_medium')
    fill('honkai_coolant', 2500, 'fresh_honkai_coolant')
    run('liquid_stabilization', 5)

production('liquid_fractionation')
startup = {'inventory': dict(inventory), 'external': dict(external), 'runs': dict(runs)}
assert inventory['stabilized_liquid_honkai_energy'] == 4000
assert not any(runs[x] for x in ['stabilization_medium_recovery', 'analysis_reagent_recovery'])

def recover():
    consume_all('spent_analysis_reagent', 'analysis_reagent_recovery')
    fill('honkai_analysis_reagent', 2500, 'fresh_analysis_reagent')
    run('stabilization_medium_recovery', 5)
    consume_all('crystallization_residual_liquid', 'recover_crystallization')
    consume_all('hot_honkai_coolant', 'coolant_reconditioning')
    consume_all('lost_coolant_residue', 'lost_coolant_treatment')
    consume_all('fuel_blending_residue', 'tail_material_treatment')
    consume_all('concentrated_honkai_impurity', 'impurity_purge')
    consume_all('separation_residue', 'separation_residue_purge')
    consume_all('honkai_separation_medium', 'purge_honkai_separation_medium')
    consume_all('unrecoverable_process_effluent', 'effluent_solidification')
    consume_all('inactive_fuel_residue', 'inert_residue_disposal')
    for key in ['stabilized_liquid_honkai_energy', 'hk.HONKAI_ENERGY_CRYSTAL', 'gt.dust.Ash', 'separation_filter']:
        exports[key] += inventory[key]
        inventory[key] = 0

recover()
samples = []
for cycle in range(1, 61):
    # 下批新介质会在稳定化前制造，先确保分离介质没有被排污到不足供给；本批净化自行补充4800mB。
    production('liquid_fractionation_reflux')
    recover()
    samples.append(dict(inventory))
assert inventory['clarified_honkai_mother_liquor'] == 2000
assert exports['stabilized_liquid_honkai_energy'] == 61 * 4000
limits = {'concentrated_honkai_impurity': 16, 'separation_residue': 16, 'honkai_separation_medium': 1000,
    'spent_analysis_reagent': 500, 'spent_honkai_stabilization_medium': 800, 'hot_honkai_coolant': 500,
    'crystallization_residual_liquid': 1000, 'lost_coolant_residue': 1000, 'fuel_blending_residue': 16,
    'inactive_fuel_residue': 16, 'unrecoverable_process_effluent': 1000,
    'honkai_analysis_reagent': 1000, 'honkai_stabilization_medium': 4500, 'honkai_coolant': 6500}
for snapshot in samples:
    for key, limit in limits.items():
        assert 0 <= snapshot.get(key, 0) < limit, (key, snapshot[key], limit)

collection_source = (BASE / 'common/recipe/honkai/HonkaiRecipes.java').read_text(encoding='utf-8')
# 注册门禁字符串也包含ID，因此从recipeBuilder之后定位。
collection = collection_source[collection_source.index('Hk3IndustrialRecipeTypes.COLLECTION.recipeBuilder', collection_source.index('// 一阶探测器')):]
collection = collection[:collection.index('.save(provider);')]
assert '.notConsumable(betaItem("honkai_reference_sample", 4))' in collection
assert '.inputItems(betaItem("honkai_reference_sample", 4))' not in collection
for name in ['industrial_prototype_detector_calibration', 'industrial_liquid_detector_calibration']:
    assert 'item("honkai_reference_sample",4)' in block(main, name)
    assert '.notConsumable' not in block(main, name)

fluids = (BASE / 'common/registration/Hk3IndustrialFluids.java').read_text(encoding='utf-8')
registered = set(re.findall(r'add\("([^"]+)"', fluids))
for source in [main, loop]:
    for fluid_id in re.findall(r'fluid\("([^"]+)"', source):
        assert fluid_id in registered, fluid_id
for lang in ['zh_cn', 'en_us']:
    data = json.loads((ROOT / f'src/main/resources/assets/hk3gtl/lang/{lang}.json').read_text(encoding='utf-8'))
    assert data['material.hk3gtl.clarified_honkai_mother_liquor']
assert 'RN-LSE' in block(loop, 'industrial_liquid_fractionation_reflux').split(')')[0]
assert '600,null,null)' in block(loop, 'industrial_fresh_analysis_reagent')

types = (BASE / 'common/recipe/Hk3IndustrialRecipeTypes.java').read_text(encoding='utf-8')
assert 'Hk3LiquidLoopRecipes.register(provider);' in main
assert main.count('Hk3LiquidLoopRecipes.register(provider);') == 1
assert 'Hk3LiquidLineRecipes.processing(provider);' in collection_source
fluid_keys = registered | {'hk.LIQUID_HONKAI_ENERGY'}
io_counts = {}
for name, entry in recipes.items():
    counts = []
    for side in ['in', 'out']:
        fluids_count = sum(key in fluid_keys or key.startswith('gt.fluid.') for key in entry[side])
        items_count = len(entry[side]) - fluids_count + (1 if side == 'in' else 0)
        counts.extend([items_count, fluids_count])
    # 物品输入含编程电路；这是配方种类数上限，不证明仓室容量及实际输出插入成功。
    bounds = [8, 4, 6, 4]
    if name.startswith('fresh_'):
        bounds = [6, 2, 1, 1]
    elif name == 'honkai_crystal_seed':
        counts[0] -= 1  # 既有晶种配方没有编程电路。
        bounds = [9, 1, 1, 0]
    elif name == 'inert_residue_disposal':
        bounds = [2, 1, 6, 6]
    assert all(a <= b for a, b in zip(counts, bounds)), (name, counts, bounds)
    io_counts[name] = counts
assert '.setMaxIOSize(8, 6, 4, 4)' in types

net = Counter()
for name, times in [('liquid_fractionation',4), ('liquid_purification',4), ('liquid_stabilization',5), ('stabilization_medium_recovery',5)]:
    for side, sign in [('in', -1), ('out', 1)]:
        for key, value in recipes[name][side].items():
            net[key] += sign * value * times
assert net['concentrated_honkai_impurity'] == 4 and net['separation_residue'] == 32
report = {'time': datetime.now().isoformat(), 'kind': '源码限定DSL解析及库存核算，不是游戏执行',
    'startup_without_recovery': startup, 'steady_macrobatches': 60, 'final_inventory': dict(inventory),
    'external_inputs': dict(external), 'exports': dict(exports), 'runs': dict(runs),
    'four_fractionations_five_stabilizations': {'impurity_surplus': net['concentrated_honkai_impurity'], 'residue_surplus': net['separation_residue'],
        'reagent_makeup_mB': 5*500-4*300, 'particles': 1280, 'seeds': 80},
    'sample_standard_count': 4, 'calibration_consumes_samples': True, 'recipes': recipes,
    'io_counts_itemIn_fluidIn_itemOut_fluidOut': io_counts,
    'game_tested': False}
LOG.mkdir(parents=True, exist_ok=True)
(LOG / 'material-balance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('通过：零回收库存启动、60组回流库存、粒子与晶种配平、试剂补充、余料处置、样本标准件及流体注册。')
print('外供耗材/GT材料的实际获得、研究执行和机器成型仍需游戏验收。')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
