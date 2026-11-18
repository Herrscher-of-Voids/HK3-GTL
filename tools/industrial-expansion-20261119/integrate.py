import hashlib
import json
import re
from html import unescape
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources'
DATA = RES / 'data/hk3gtl'
ART = RES / 'assets/hk3gtl'
OUT = ROOT / 'deliveries/0003_40台工业内容补全_20261119'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def ident(value):
    return value if ':' in value else 'hk3gtl:' + value


def hexid(value):
    return '4B5' + hashlib.sha256(value.encode()).hexdigest()[:13].upper()


approved = read(DATA / 'research/approved_industrial_processes.json')
base = {}
groups = ['industrial', 'wonder', 'reactor_fuel', 'wonder_w01_w05', 'wonder_w06_w10', 'wonder_w11_w15']
groups += [f'wonder_expansion_w{i:02}' for i in range(1, 16)]
for group in groups:
    for recipe in read(DATA / f'research/{group}_processes.json')['recipes']:
        rid = recipe['id']
        if rid not in approved['superseded_ids'] and not any(rid.startswith(p) for p in approved['superseded_prefixes']):
            base[rid] = recipe
base.update({r['id']: r for r in approved['recipes']})
original = deepcopy(base)
baseline = list(original.values())

support = read(DATA / 'research/industrial_support_processes.json')
expansions = []
items, fluids, links = [], [], []
for section in ['early', 'world', 'late']:
    data = read(DATA / f'research/industrial_expansion_{section}_processes.json')
    section_links = read(OUT / f'{section}-links.json')
    extra = defaultdict(lambda: defaultdict(list))
    for link in section_links:
        for key in ['item_inputs', 'fluid_inputs', 'item_catalysts']:
            extra[link['recipe_id']][key].extend(link.get(key, []))
    data['additional_inputs'] = extra
    save(DATA / f'research/industrial_expansion_{section}_processes.json', data)
    expansions.append(data)
    assets = read(OUT / f'{section}-assets.json')
    items.extend(assets['items'])
    fluids.extend(assets['fluids'])
    links.extend(section_links)

for data in [support] + expansions:
    base.update({r['id']: json.loads(json.dumps(r)) for r in data['recipes']})
for data in [support] + expansions:
    for rid, extra in data['additional_inputs'].items():
        for key, entries in extra.items():
            base[rid].setdefault(key, []).extend(entries)
plans = list(base.values())
fields = ('item_inputs', 'fluid_inputs', 'item_catalysts')
reasons = defaultdict(list)
for link in links:
    reasons[link['recipe_id']].append(link['reason'])
links = []
for rid, old in original.items():
    new = base[rid]
    added = {k:new.get(k, [])[len(old.get(k, [])):] for k in fields}
    if any(added.values()):
        links.append(dict(recipe_id=rid, role=new['role'], title=new.get('title',rid), **added,
                          before={k:old.get(k,[]) for k in fields}, after={k:new.get(k,[]) for k in fields},
                          reason='；'.join(dict.fromkeys(reasons[rid])) or '支线制造的工件或工装用于这道既有工序。'))
new_plans = [base[r['id']] for data in [support] + expansions for r in data['recipes']]
languages = {lang: read(ART / f'lang/{lang}.json') for lang in ['zh_cn', 'en_us']}

support_ids = read(DATA / 'catalog/industrial_support_items.json')
known_items = set(support_ids)
new_items = {x['id']: x for x in items if x['id'] not in known_items}
java_fluids = (ROOT / 'src/main/java/com/sirin/hk3gtl/common/registration/Hk3IndustrialFluids.java').read_text(encoding='utf-8')
known_fluids = set(re.findall(r'add\("([a-z0-9_]+)"', java_fluids))
new_fluids = {x['id']: x for x in fluids if x['id'] not in known_fluids}
save(DATA / 'catalog/industrial_expansion_items.json', sorted(new_items))
fluid_catalog = []
for value in new_fluids.values():
    value['gas'] = value.get('gas', any(word in value['id'] for word in ['_gas', '_air', '_vapor']))
    color = value['color']
    fluid_catalog.append(dict(id=value['id'], color=int(color, 16) if isinstance(color, str) else color,
                              temperature=value['temperature'], gas=value['gas']))
save(DATA / 'catalog/industrial_expansion_fluids.json', fluid_catalog)

sources, uses = defaultdict(list), defaultdict(list)
for recipe in plans:
    for key in ['item_outputs', 'fluid_outputs']:
        for output in recipe[key]:
            sources[ident(output['id'])].append(recipe['id'])
    for key in ['item_inputs', 'fluid_inputs', 'item_catalysts']:
        for entry in recipe.get(key, []):
            uses[ident(entry['id'])].append(recipe['id'])

manifest = []
for item_id in support_ids:
    key = 'item.hk3gtl.' + item_id
    appearance = '按当前名称与实际材料绘制可辨认的实体形状；金属部件保留紧固与接口，光学部件显示光路，滤材显示孔隙，工装显示定位面。'
    manifest.append(dict(id=item_id, kind='item', zh=languages['zh_cn'][key], en=languages['en_us'][key],
                         family='existing_support', appearance=appearance, purpose='已接入的工业支线实体组件或可重复使用工装。'))
for kind, values in [('item', new_items.values()), ('fluid', new_fluids.values())]:
    for value in values:
        entry = dict(value, kind=kind)
        manifest.append(entry)
        for lang, field in [('zh_cn', 'zh'), ('en_us', 'en')]:
            prefix = 'item' if kind == 'item' else 'material'
            languages[lang][f'{prefix}.hk3gtl.{value["id"]}'] = value[field]
            if kind == 'fluid':
                languages[lang][f'fluid.hk3gtl.{value["id"]}'] = value[field]

for entry in manifest:
    item_id = entry['id']
    entry['registry_id'] = 'hk3gtl:' + item_id
    entry['sources'] = sources[entry['registry_id']]
    entry['uses'] = uses[entry['registry_id']]
    entry['raw_materials'] = [x for rid in entry['sources'][:1] for key in ['item_inputs', 'fluid_inputs'] for x in base[rid][key]]
    if entry['kind'] == 'item':
        entry['model'] = f'assets/hk3gtl/models/item/{item_id}.json'
        entry['textures'] = [f'assets/hk3gtl/textures/item/{item_id}.png']
        if not (RES / entry['model']).exists() or not (RES / entry['textures'][0]).exists():
            save(RES / entry['model'], {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'hk3gtl:item/' + item_id}})
    else:
        entry['textures'] = [f'assets/hk3gtl/textures/block/fluids/fluid.{item_id}{suffix}.png' for suffix in ['', '_flow']]
    entry['missing_png'] = [name for name in entry['textures'] if not (RES / name).is_file()]
    entry['texture_status'] = '待0002绘制' if entry['missing_png'] else '源码已有独立贴图'
    entry['art_rule'] = '独立透明像素材质；按名称、物料和用途设计，不画纯色方块，不借用已有物品贴图；流体分别提供静止、流动与动画元数据。'

for lang, language in languages.items():
    zh = lang == 'zh_cn'
    language['hk3gtl.recipe.world_mining.package'] = '每批随机 %1$s 物品＋%2$s 流体' if zh else 'Random package: %1$s items + %2$s fluids'
    language['hk3gtl.recipe.world_mining.route'] = '每批消耗 1 个世界泡；每泡只能采一次' if zh else 'Consumes 1 bubble; each target can be mined once'
    language['hk3gtl.recipe.world_mining.archive'] = '舰船档案：每批独立 1％' if zh else 'Ship archive: independent 1％ per run'
    for role in ['I25', 'I26', 'I27', 'I28', 'I29', 'I30', 'I31', 'I36']:
        language['gtceu.industrial_fabrication_' + role.lower()] = f'{role} 辅助制造' if zh else f'{role} Component Fabrication'
    save(ART / f'lang/{lang}.json', language)

catalog = read(DATA / 'guide/quest_catalog.json')
catalog['entries'] = [x for x in catalog['entries'] if not x['key'].startswith('expansion-')]
chapter_titles = [('early', '采集与材料工艺'), ('world', '燃料与世界泡工程'), ('late', '虚数与跨界工程')]
quest_total = 0
for order, (section, title) in enumerate(chapter_titles, 40):
    chapter = 'hk3_industrial_' + section
    recipes = [r for r in new_plans if ('early' if int(r['role'][1:3]) <= 16 else 'world' if int(r['role'][1:3]) <= 33 else 'late') == section]
    role_rows = defaultdict(list)
    for recipe in recipes:
        role_rows[recipe['role']].append(recipe)
    quests = []
    for role_index, (role, rows) in enumerate(role_rows.items()):
        output_quest = {}
        for index, recipe in enumerate(rows):
            rid = recipe['id']
            qid, tid = hexid('quest/' + rid), hexid('task/' + rid)
            outputs = recipe['item_outputs'] + recipe['fluid_outputs']
            icon = ident(outputs[0]['id']) if outputs else 'gtceu:energy_crystal'
            if outputs and not recipe['item_outputs']:
                icon = {'minecraft:water':'minecraft:water_bucket','minecraft:lava':'minecraft:lava_bucket'}.get(icon, icon + '_bucket')
            if icon.startswith('material:soulium/'):
                icon = 'gtceu:' + icon.split('/')[-1] + '_of_soulium' if icon.endswith('/fine_wire') else 'gtceu:soulium_' + icon.split('/')[-1]
            parents = []
            for key in ['item_inputs', 'fluid_inputs']:
                for entry in recipe[key]:
                    previous = output_quest.get(entry['id'])
                    if previous and previous not in parents:
                        parents.append(previous)
            out_names = []
            for entry in outputs:
                key = entry['id'].replace(':', '.')
                name = languages['zh_cn'].get('item.' + key, languages['zh_cn'].get('material.' + key, entry['id']))
                out_names.append(name)
            consumer_titles = list(dict.fromkeys(base[c].get('title', c) for entry in outputs for c in uses[ident(entry['id'])] if c != rid))
            desc = ['在本队工业设备上实际完成这项工艺后记录进度。', '产物：' + '、'.join(out_names) + '。']
            if consumer_titles:
                desc.append('用于：' + '、'.join(consumer_titles[:5]) + '。')
            key = 'expansion-' + rid
            quests.append(dict(id=qid, title=recipe['title'], subtitle=role + ' 工艺支线', description=desc,
                               tasks=[dict(id=tid, type='custom', title='完成一次实际工艺', tags=['hk3gtl_quest_' + key.replace('-', '_')])],
                               dependencies=parents[:3], icon=icon, optional=True,
                               x=(role_index % 3) * 30 + index % 5 * 5, y=(role_index // 3) * 36 + index // 5 * 5))
            catalog['entries'].append(dict(key=key, kind='process', value=rid, quest=qid, task=tid, chapter=chapter))
            for entry in outputs:
                output_quest.setdefault(entry['id'], qid)
    save(ART / f'ftbquests/chapters/{chapter}.snbt', dict(filename=chapter, id=hexid('chapter/' + chapter), title=title,
         group='68CBF1606D696C68', order_index=order, default_quest_shape='rsquare', icon='hk3gtl:industrial_port_casing', quests=quests))
    if chapter not in catalog['chapters']:
        catalog['chapters'].append(chapter)
    quest_total += len(quests)
changed_quests = defaultdict(lambda: defaultdict(list))
links_by_id = {row['recipe_id']:row for row in links}
for entry in catalog['entries']:
    if entry['kind'] == 'process':
        for rid in entry['value'].split('|'):
            if rid in links_by_id:
                changed_quests[entry['chapter']][entry['quest']].append(links_by_id[rid])
for path in sorted((ART / 'ftbquests/chapters').glob('hk3_voltage_*.snbt')):
    changes = changed_quests.get(path.stem, {})
    existing = read(path)
    dirty = False
    for quest in existing['quests']:
        text = [v for v in quest.get('description',[]) if not v.startswith('工业修订：')]
        if quest['id'] not in changes and text == quest.get('description',[]): continue
        dirty = True
        for row in changes.get(quest['id'], []):
            details = []
            for k,label in zip(fields,['耗材','流体','不消耗工装']):
                if row[k]:
                    vals = []
                    for x in row[k]:
                        key = ident(x['id']).replace(':','.')
                        name = languages['zh_cn'].get('item.'+key, languages['zh_cn'].get('material.'+key, x['id']))
                        vals.append(f"{name} ×{x.get('count',x.get('amount'))}" + (' mB' if k=='fluid_inputs' else ''))
                    details.append(label+'：'+'、'.join(vals))
            text.append('工业修订：'+row['title']+'；'+'；'.join(details)+'。')
        quest['description'] = text
    if dirty: save(path, existing)
catalog['revision'] = 283
save(DATA / 'guide/quest_catalog.json', catalog)

counts = defaultdict(lambda: dict(before=0, support=0, added=0, production=0))
for key, rows in [('before', baseline), ('support', support['recipes']), ('added', [r for d in expansions for r in d['recipes']])]:
    for recipe in rows:
        if recipe['role'].startswith('I'):
            counts[recipe['role']][key] += 1
for recipe in plans:
    if recipe['role'].startswith('I') and not recipe['experiment'] and not recipe['provisional']:
        counts[recipe['role']]['production'] += 1
reactors = read(DATA / 'research/reactor_fuel_processes.json')['reactor_recipes']
for role in {r['role'] for r in reactors}:
    counts[role]['production'] = sum(r['role']==role for r in reactors)
audit = (ROOT / 'deliveries/0003_Multiblock_Recipe_Audit_20261118/index.html').read_text(encoding='utf8')
roles = {role:unescape(name) for role,name in re.findall(r'<tr[^>]*><td>(I[0-9-]+)</td><td>([^<>]+)</td>',audit)}
for r in new_plans + [base[row['recipe_id']] for row in links]:
    r['display_eut'] = str(r.get('output_eut') or r.get('input_eut') or (30 * 4**(r['energy_tier']-1)))
    r['display_hw'] = str(r['input_hw']) if r.get('input_hw',-1)>=0 else '按设备规则'
payload = dict(role_names=roles, owner='0003工业链', thread='01a1d689-c9b4-7b71-bffe-bc0eafa300d8', date='2026-11-19',
               plans=new_plans, counts=counts, assets=manifest, links=links, quests=quest_total, revised_quests=sum(len(v) for v in changed_quests.values()),
               related=[base[l['recipe_id']] for l in links],
               pending_art={k:sum(a['kind']==kind and bool(a['missing_png']) for a in manifest) for k,kind in [('items','item'),('fluids','fluid')]},
               names=languages['zh_cn'])
save(OUT / 'content.json', payload)
save(OUT / '0002-material-handoff.json', dict(owner=payload['owner'], thread=payload['thread'], assets=manifest))
save(OUT / 'old-recipe-changes.json', links)
template = Path(__file__).with_name('review.html').read_text(encoding='utf-8')
(OUT / 'index.html').write_text(template.replace('__CONTENT__', json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')), encoding='utf-8')
(OUT / 'textures.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=index.html#assets"><title>0002 材质交接</title><a href="index.html#assets">打开逐项材质交接清单</a></html>', encoding='utf8')
print(json.dumps(dict(recipes=len(new_plans), items=len(new_items), fluids=len(new_fluids), pending_art=payload['pending_art'],
                      links=len(links), quests=quest_total), ensure_ascii=False))
