from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'deliveries/0006文案设计_FTB逐章审核_20261116'
PRODUCTION = ROOT / 'src/main/resources/data/hk3gtl/research/approved_industrial_processes.json'


def use_product_task(quest, task, recipe):
    if not recipe or recipe['network_credit'] or recipe['energy_direction'] == 'output':
        return False
    item = quest['icon']
    recipe_item = 'material:soulium/ingot' if item == 'hk3gtl:soulium_ingot' else item
    outputs = {stack['id'] for stack in recipe['item_outputs']}
    inputs = {stack['id'] for field in ('item_inputs', 'item_catalysts') for stack in recipe[field]}
    if recipe_item not in outputs or recipe_item in inputs:
        return False
    task.pop('title', None)
    task.update(type='item', item=item, count=1, consume_items=False, only_from_crafting=False)
    return True


def load_approved():
    manifest = json.loads((SOURCE / 'all-chapters.manifest.json').read_text(encoding='utf-8'))
    recipes = json.loads(PRODUCTION.read_text(encoding='utf-8'))['recipes']
    by_recipe = {recipe['id']: recipe for recipe in recipes}
    fluid_icons = {stack['id'] for recipe in recipes for field in ('fluid_inputs', 'fluid_outputs')
                   for stack in recipe[field] if 'id' in stack}
    files = [('hk3_stargate.snbt', 'chapter-stargate.review.json'),
             ('hk3_voltage_01.snbt', 'chapter-15-hbv.review.json'),
             ('hk3_voltage_02.snbt', 'chapter-16-hcv.review.json'),
             ('hk3_voltage_03.snbt', 'chapter-17-hrv.review.json')]
    files.extend((chapter['snbt'], chapter['review']) for chapter in manifest['chapters'])
    approved, additions = [], []
    for filename, review_file in files:
        chapter = json.loads((SOURCE / filename).read_text(encoding='utf-8'))
        review = json.loads((SOURCE / review_file).read_text(encoding='utf-8'))
        prefix = 'stargate' if filename == 'hk3_stargate.snbt' else chapter['subtitle'][0].split('-')[-1].lower()
        plan = json.loads((SOURCE / (prefix + '-detection.plan.json')).read_text(encoding='utf-8'))
        by_key = {q['key']: q for q in review['quests']}
        by_id = {entry['quest']: by_key[entry['key']] for entry in plan['entries']}
        for quest in chapter['quests']:
            if quest['icon'] in fluid_icons or any(task.get('fluid') == quest['icon'] for task in quest['tasks']):
                quest['icon'] += '_bucket'
            source = by_id[quest['id']]
            custom_count = sum(task['type'] == 'custom' for task in quest['tasks'])
            for index, (task, detection) in enumerate(zip(quest['tasks'], source['detection'])):
                if task['type'] not in ('custom', 'checkmark'):
                    continue
                key = source['key'] + ('-task-' + str(index + 1) if custom_count > 1 else '')
                if detection['type'] == 'event':
                    kind = 'player_event' if filename == 'hk3_stargate.snbt' else 'process'
                    value = '|'.join(detection.get('alternatives', [detection['target']]))
                    if kind == 'process' and use_product_task(quest, task, by_recipe.get(value)):
                        continue
                else:
                    kind = 'research' if detection['type'] == 'research' else 'reading'
                    value = detection['target'] if kind == 'research' else ''
                tag = 'hk3gtl_quest_' + key.lower().replace('-', '_')
                task['tags'] = list(dict.fromkeys(task.get('tags', []) + [tag]))
                if task['type'] == 'custom':
                    task['title'] = detection['label']
                additions.append(dict(key=key, kind=kind, value=value, quest=quest['id'],
                                      task=task['id'], chapter=chapter['filename']))
        approved.append(chapter)
    return approved, additions
