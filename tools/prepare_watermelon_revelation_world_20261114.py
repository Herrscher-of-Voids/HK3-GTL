"""从增强版原生空岛模板准备独立籽海解谜存档。"""
import hashlib
import json
import random
import shutil
import time
from pathlib import Path

import nbtlib as n


ROOT = Path(__file__).resolve().parents[1]
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
DELIVERY = ROOT / 'deliveries/籽海_ARG_玩家体验_D4_20261114'
WORLD = DELIVERY / '世界/籽海_玩家解谜_D4'
TEMPLATE = INSTANCE / 'config/skyblockbuilder/templates/skyword.nbt'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def item(item_id, count=1, tag=None):
    value = n.Compound({'id': n.String(item_id), 'Count': n.Byte(count)})
    if tag:
        value['tag'] = tag
    return value


def inventory(items):
    rows = n.List[n.Compound]()
    for slot, entry in enumerate(items):
        row = entry.copy()
        row['Slot'] = n.Byte(slot)
        rows.append(row)
    return rows


def box(color, title, items):
    return item('minecraft:' + color + '_shulker_box', tag=n.Compound({
        'display': n.Compound({'Name': n.String(json.dumps({'text': title}, ensure_ascii=False))}),
        'BlockEntityTag': n.Compound({'Items': inventory(items)})
    }))


def pattern():
    slots = [item('minecraft:oak_planks') if i in (0, 1, 3, 4) else n.Compound() for i in range(9)]
    return item('ae2:crafting_pattern', tag=n.Compound({
        'in': n.List[n.Compound](slots), 'out': item('minecraft:crafting_table'),
        'recipe': n.String('minecraft:crafting_table'),
        'substitute': n.Byte(0), 'substituteFluids': n.Byte(0)
    }))


def supplies():
    specimens = [item('hk3gtl:' + name) for name in (
        'world_bubble_sample', 'data_precivilization_fragment', 'phase_transfer_mirror',
        'ancient_legacy', 'prototype_honkai_detector')]
    specimens += [
        item('ae2:memory_card', tag=n.Compound({'Config': n.String('block.ae2.drive'),
                                             'Data': n.Compound({'priority': n.Int(0)})})),
        pattern(), item('ae2:singularity'),
        item('ae2:quantum_entangled_singularity', 2, n.Compound({'freq': n.Long(int(time.time() * 100000))})),
        item('gtceu:programmed_circuit', tag=n.Compound({'Configuration': n.Int(0)})),
        item('gtceu:data_stick'), item('gtceu:data_orb'),
        item('ae2:memory_card'), item('ae2:blank_pattern', 8), item('ae2:fluix_crystal', 8),
        item('ae2:certus_quartz_crystal', 8), item('ae2:logic_processor', 8),
        item('ae2:engineering_processor', 8), item('ae2:calculation_processor', 8),
        item('gtceu:quartzite_dust', 8), item('gtceu:silicon_plate', 8),
        item('gtceu:tungsten_steel_plate', 8), item('minecraft:quartz', 8), item('minecraft:clock')
    ]
    random.SystemRandom().shuffle(specimens)
    metal = [item('sgjourney:naquadah_alloy', 64) for _ in range(8)]
    metal += [item('sgjourney:refined_naquadah', 64) for _ in range(4)]
    metal += [item('sgjourney:naquadah', 64), item('minecraft:blaze_powder', 64),
              item('minecraft:diamond', 32), item('minecraft:redstone', 64),
              item('minecraft:iron_ingot', 64), item('minecraft:copper_ingot', 64),
              item('minecraft:gold_ingot', 64), item('minecraft:stone_button', 32),
              item('minecraft:stone', 64), item('minecraft:oak_planks', 64)]
    crystals = [item('sgjourney:' + name + '_crystal', 32) for name in
                ('transfer', 'communication', 'control', 'energy', 'materialization')]
    crystals += [item('sgjourney:large_control_crystal', 2)]
    crystals += [item('sgjourney:naquadah_rod', 64), item('sgjourney:naquadah_wire', 64)]
    crystals += [item('sgjourney:liquid_naquadah_bucket') for _ in range(8)]
    energy = [item('sgjourney:zpm_hub'), item('sgjourney:large_naquadah_cable', 16)]
    energy += [item('sgjourney:zero_point_module', tag=n.Compound({
        'Energy': n.Long(100000000000), 'Entropy': n.Int(998)})) for _ in range(3)]
    intro = ('右键手机，打开「残页译码」。\n\n潜影盒内混放了实物、资料与备用材料。'
             '取出你认为有关的物件，亲自校读。\n\n原生星门的制造、搭建、供能与拨号由你完成。'
             '纸笔、工具和旅途补给已经备好。')
    book = item('minecraft:written_book', tag=n.Compound({
        'title': n.String('致阅卷者'), 'author': n.String('留信人'),
        'pages': n.List[n.String]([n.String(json.dumps({'text': intro}, ensure_ascii=False))])
    }))
    return [
        item('hk3gtl:personal_phone', tag=n.Compound({'Charge': n.Long(128000)})), book,
        item('minecraft:writable_book'), item('minecraft:paper', 64),
        item('minecraft:iron_pickaxe'), item('minecraft:iron_axe'),
        item('minecraft:torch', 64), item('minecraft:ladder', 64),
        item('minecraft:cooked_beef', 64), item('minecraft:compass'), item('minecraft:spyglass'),
        item('minecraft:crafting_table'), item('minecraft:white_bed'), item('minecraft:water_bucket'),
        item('minecraft:cobblestone', 64),
        box('cyan', '随行样品', specimens), box('gray', '制造材料', metal),
        box('blue', '晶体与燃料材料', crystals), box('yellow', '旅途能源器材', energy)
    ]


def generator(dimension, settings, biome_source, kind='skyblockbuilder:noise_based'):
    return n.Compound({'type': n.String(kind), 'settings': n.String(settings),
                       'biome_source': biome_source, 'dimension': n.String(dimension),
                       'layers': n.List[n.Compound]()})


def main():
    WORLD.mkdir(parents=True)
    (WORLD / 'data').mkdir()
    template = n.load(TEMPLATE)
    configured = n.Compound({
        'Template': n.Compound(template), 'Name': n.String('skyword'), 'Desc': n.String('增强版原生预设空岛'),
        'Spawns': n.List[n.Compound]([n.Compound({'posX': n.Int(26), 'posY': n.Int(10),
                                               'posZ': n.Int(25), 'Direction': n.String('NORTH')})]),
        'OffsetX': n.Int(0), 'OffsetY': n.Int(0), 'OffsetZ': n.Int(0),
        'SurroundingMargin': n.Int(0), 'SurroundingBlocks': n.List[n.String](),
        'Spreads': n.List[n.Compound]()
    })
    n.File({'DataVersion': n.Int(3465), 'data': configured}, gzipped=True).save(WORLD / 'data/skyblock_template.dat')
    dimensions = n.Compound()
    for dimension, settings in [('minecraft:overworld', 'minecraft:overworld'), ('minecraft:the_nether', 'minecraft:nether')]:
        biomes = n.Compound({'type': n.String('minecraft:multi_noise'), 'preset': n.String(settings)})
        dimensions[dimension] = n.Compound({'type': n.String(dimension), 'generator': generator(dimension, settings, biomes)})
    dimensions['minecraft:the_end'] = n.Compound({'type': n.String('minecraft:the_end'), 'generator': generator(
        'minecraft:the_end', 'minecraft:end', n.Compound({'type': n.String('minecraft:the_end')}), 'skyblockbuilder:the_end')})
    rules = {'doMobSpawning': 'false', 'keepInventory': 'true', 'spawnRadius': '0', 'doFireTick': 'false'}
    data = n.Compound({
        'DataVersion': n.Int(3465), 'version': n.Int(19133),
        'Version': n.Compound({'Name': n.String('1.20.1'), 'Id': n.Int(3465), 'Series': n.String('main'), 'Snapshot': n.Byte(0)}),
        'LevelName': n.String('籽海 · 玩家解谜 D4'),
        'WorldGenSettings': n.Compound({'seed': n.Long(random.SystemRandom().randrange(1 << 63)),
                                      'generate_features': n.Byte(1), 'bonus_chest': n.Byte(0), 'dimensions': dimensions}),
        'DataPacks': n.Compound({'Enabled': n.List[n.String]([n.String('vanilla'), n.String('mod:forge'), n.String('file/hk3arg_d4_supplies')]),
                                'Disabled': n.List[n.String]()}),
        'GameType': n.Int(0), 'allowCommands': n.Byte(0), 'hardcore': n.Byte(0),
        'Difficulty': n.Byte(0), 'DifficultyLocked': n.Byte(1), 'initialized': n.Byte(1), 'WasModded': n.Byte(1),
        'LastPlayed': n.Long(int(time.time() * 1000)), 'Time': n.Long(0), 'DayTime': n.Long(6000),
        'SpawnX': n.Int(26), 'SpawnY': n.Int(74), 'SpawnZ': n.Int(25),
        'GameRules': n.Compound({key: n.String(value) for key, value in rules.items()}),
        'ScheduledEvents': n.List[n.Compound](), 'confirmedExperimentalSettings': n.Byte(1)
    })
    n.File({'Data': data}, gzipped=True).save(WORLD / 'level.dat')
    pack = WORLD / 'datapacks/hk3arg_d4_supplies'
    write_json(pack / 'pack.mcmeta', {'pack': {'pack_format': 15, 'description': '籽海解谜体验用品；不预设解谜或研究进度。'}})
    write_json(pack / 'data/minecraft/tags/functions/tick.json', {'values': ['hk3arg_d4:tick']})
    functions = pack / 'data/hk3arg_d4/functions'
    functions.mkdir(parents=True)
    (functions / 'tick.mcfunction').write_text('execute as @a[tag=!hk3arg_d4_supplies] at @s run function hk3arg_d4:supplies\n', encoding='utf-8')
    entries = supplies()
    commands = [f"give @s {entry['id']}{entry['tag'].snbt() if 'tag' in entry else ''} {int(entry['Count'])}" for entry in entries]
    commands += ['tag @s add hk3arg_d4_supplies', 'tellraw @s {"text":"随行用品已送达。右键手机，打开「残页译码」。","color":"aqua"}']
    (functions / 'supplies.mcfunction').write_text('\n'.join(commands) + '\n', encoding='utf-8')
    archive = Path(shutil.make_archive(str(DELIVERY / WORLD.name), 'zip', root_dir=WORLD.parent, base_dir=WORLD.name))
    receipt = {
        '准备时间': time.strftime('%Y-%m-%dT%H:%M:%S%z'), '地图': str(WORLD), '地图ZIP': str(archive),
        'ZIP_SHA256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        '地图类型': '增强版原生SkyblockBuilder空岛生成器；非原版平坦或自然地形世界',
        '干净模板': str(TEMPLATE), '模板SHA256': hashlib.sha256(TEMPLATE.read_bytes()).hexdigest(),
        '模板尺寸': list(map(int, template['size'])), '模板实际方块': len(template['blocks']),
        '模板接入': '完整结构及原出生配置写入原生skyblock_template.dat，首次启动由原生SkyblockBuilder生成；未更改实例配置。',
        '用品': '全12候选与AE/GT普通干扰品混装；GT电路初始0可自行调整；含已保存设置卡、已编码工作台样板和关联奇点。',
        '星门用品': '星门主体制造原料、2枚大控制晶体及有限燃料原料；空普通ZPM Hub、16根大型硅岩电缆及3个普通有限ZPM作为本次体验器材供应。玩家自行放置、接线、插模块、开关及拨号；无星门本体、预建出发门、预充能或代拨号。',
        '能源器材状态': {'sgjourney:zero_point_module': {'数量': 3, 'Energy': 100000000000, 'Entropy': 998},
                         'sgjourney:zpm_hub': '空普通器材；原版无配方，本次直接供应，不宣称工业取得。',
                         'sgjourney:large_naquadah_cable': '16根；目标配置支持零点能传输；每tick传输上限100000000000。'},
        '准入与进度': '没有解谜、毕业、研究或终点完成状态；没有生成门址题单。',
        '用户存档读取': False, '安装JAR': False, '导入活动实例': False, '启动游戏': False, '玩家解密验收': '尚未执行'
    }
    write_json(DELIVERY / '地图准备回执.json', receipt)
    print(json.dumps({'world': str(WORLD), 'zip': str(archive), 'bytes': archive.stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    main()
