# -*- coding: utf-8 -*-
"""生成星门、电压任务及原版进度。"""
from pathlib import Path
import json

from quest_tutorial import CHAPTERS
from quest_approved import load_approved
from quest_text import clean_player_fields

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / 'src/main/resources/assets/hk3gtl/ftbquests/chapters'
ADVANCEMENT_DIR = ROOT / 'src/main/resources/data/hk3gtl/advancements/guide'


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def save(path, value):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean_player_fields(value), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def advancement_path(quest):
    kind = quest['kind']
    if kind == 'research':
        return 'research/' + quest['value'].lower()
    if kind == 'civilization':
        return 'civilization/c' + quest['value']
    if kind == 'review':
        return 'first_review' if quest['value'] == '1' else 'second_review'
    return 'finale'


icons = load('src/main/resources/data/hk3gtl/research/research_icons.json')['icons']
advancements = {}
translations = {'zh_cn': {}, 'en_us': {}}
CIVILIZATION_ADVANCEMENTS = [
    [
        "1",
        "崩坏识别",
        "空气中的异常已经得到识别，最初的研究留下了记录。",
        "Honkai Recognition",
        "The anomaly in the air has been identified and the first research recorded."
    ],
    [
        "2",
        "稳定工业",
        "发现得以稳定保存，工业开始拥有循环延续的基础。",
        "Stable Industry",
        "Stabilization and regeneration have given industry a lasting foundation."
    ],
    [
        "3",
        "材料与核心",
        "魂钢与结晶成为文明承载新力量的骨骼和心脏。",
        "Materials and Cores",
        "Soulium and crystals give civilization a foundation for new power."
    ],
    [
        "4",
        "量子航路",
        "文明越过熟悉世界的边界，远行带回了真实成果。",
        "Quantum Routes",
        "Civilization has crossed familiar boundaries and brought back real results."
    ],
    [
        "5",
        "虚数联系",
        "文明开始理解并参与世界的生灭与维系。",
        "Imaginary Connections",
        "Civilization begins to understand and influence the survival of worlds."
    ],
    [
        "6",
        "文明奇观",
        "第一座奇观留下了真实工程成果，构想终于有了回应。",
        "Civilization Wonders",
        "The first wonder has produced a genuine engineering achievement."
    ],
    [
        "7",
        "认知与审判准备",
        "知识与工程汇成完整答卷，个人最后的会面仍待亲历。",
        "Cognition and Judgment Readiness",
        "Knowledge and engineering form a complete record; the final meeting remains personal."
    ]
]


def add_advancement(path, quest, icon, parent=None):
    prefix = 'hk3gtl.guide.' + path.replace('/', '.')
    display = {
        'icon': {'item': icon},
        'title': {'translate': prefix + '.title'},
        'description': {'translate': prefix + '.description'},
        'frame': 'challenge' if path == 'finale' else 'task',
        'show_toast': False, 'announce_to_chat': False, 'hidden': False,
    }
    value = {
        'display': display,
        'criteria': {'verified': {'trigger': 'minecraft:impossible'}},
        'requirements': [['verified']],
    }
    if parent:
        value['parent'] = 'hk3gtl:guide/' + parent
    else:
        display['background'] = 'minecraft:textures/block/deepslate_tiles.png'
    advancements[path] = value
    translations['zh_cn'][prefix + '.title'] = quest['title']
    translations['zh_cn'][prefix + '.description'] = quest['description'][0]
    translations['en_us'][prefix + '.title'] = quest['title_en']
    translations['en_us'][prefix + '.description'] = quest['summary_en']


add_advancement('root', CHAPTERS[0]['quests'][0], CHAPTERS[0]['icon'])
for source in CHAPTERS:
    parent = 'root'
    for source_quest in source['quests']:
        kind = source_quest['kind']
        if kind == 'reading':
            continue
        value = source_quest['value']
        icon = icons[value] if kind == 'research' else source_quest.get('icon', source['icon'])
        path = advancement_path(source_quest)
        advancement_parent = ('root' if value == '1' else
                              'civilization/c' + str(int(value) - 1)) if kind == 'civilization' else parent
        add_advancement(path, source_quest, icon, advancement_parent)
        parent = path

for level, title, description, title_en, summary_en in CIVILIZATION_ADVANCEMENTS:
    quest = {'title': title, 'description': [description],
             'title_en': title_en, 'summary_en': summary_en}
    parent = 'root' if level == '1' else 'civilization/c' + str(int(level) - 1)
    add_advancement('civilization/c' + level, quest, 'minecraft:book', parent)

chapters, entries = load_approved()
for chapter in chapters:
    save(CHAPTER_DIR / (chapter['filename'] + '.snbt'), chapter)
for path, advancement in advancements.items():
    save(ADVANCEMENT_DIR / (path + '.json'), advancement)
for path in ADVANCEMENT_DIR.rglob('*.json'):
    if path.relative_to(ADVANCEMENT_DIR).with_suffix('').as_posix() not in advancements:
        path.unlink()
for locale, values in translations.items():
    path = 'src/main/resources/assets/hk3gtl/lang/' + locale + '.json'
    previous = load(path)
    current = {key: value for key, value in previous.items() if not key.startswith('hk3gtl.guide.')}
    current.update(values)
    save(path, current)

catalog = load('src/main/resources/data/hk3gtl/guide/quest_catalog.json')
catalog.pop('_comment', None)
catalog.pop('_changes', None)
catalog.update(schema=1, revision=282, layout='approved-stargate-and-voltage',
               chapters=[chapter['filename'] for chapter in chapters], entries=entries)
save('src/main/resources/data/hk3gtl/guide/quest_catalog.json', catalog)
print(json.dumps({'chapters': len(chapters), 'quests': sum(len(chapter['quests']) for chapter in chapters),
                  'catalog_entries': len(entries),
                  'automated': sum(entry['kind'] != 'reading' for entry in entries),
                  'reading': sum(entry['kind'] == 'reading' for entry in entries),
                  'advancements': len(advancements)}, ensure_ascii=False))
