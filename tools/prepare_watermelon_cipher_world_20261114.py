"""生成负责人亲自体验残页译码的独立存档，不读取或修改任何既有存档。"""
import json
import time
from pathlib import Path

import nbtlib as n


ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / 'deliveries/西瓜ARG_残页译码_玩家体验_R282_20261114/世界/西瓜来信_残页译码'
NAME = '西瓜来信 · 残页译码'
INTRO = '右键随身手机，打开「残页译码」。\n\n规则与线索都在程序里。\n\n不必一口气读完。离开后，回到同一存档，仍可接着读。\n\n档案室只提供纸、笔和安静。答案由你留下。'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def function(pack, name, commands):
    path = pack / 'data/hk3arg/functions' / (name + '.mcfunction')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(commands) + '\n', encoding='utf-8')


def main(world=WORLD, name=NAME, intro=INTRO, extra_items=()):
    pack = world / 'datapacks/hk3arg_reading_room'
    book = '{title:"致阅卷者",author:"档案室",pages:[' + json.dumps(json.dumps({'text': intro}, ensure_ascii=False), ensure_ascii=False) + ']}'
    world.mkdir(parents=True)
    (world / 'region').mkdir()
    dimensions = n.Compound({
        'minecraft:overworld': n.Compound({
            'type': n.String('minecraft:overworld'),
            'generator': n.Compound({
                'type': n.String('minecraft:flat'),
                'settings': n.Compound({
                    'biome': n.String('minecraft:plains'), 'features': n.Byte(0), 'lakes': n.Byte(0),
                    'structure_overrides': n.List[n.String](),
                    'layers': n.List[n.Compound]([
                        n.Compound({'block': n.String(block), 'height': n.Int(height)})
                        for block, height in [('minecraft:bedrock', 1), ('minecraft:stone', 60),
                                              ('minecraft:dirt', 2), ('minecraft:grass_block', 1)]
                    ])
                })
            })
        }),
        'minecraft:the_nether': n.Compound({
            'type': n.String('minecraft:the_nether'),
            'generator': n.Compound({'type': n.String('minecraft:noise'), 'settings': n.String('minecraft:nether'),
                                     'biome_source': n.Compound({'type': n.String('minecraft:multi_noise'), 'preset': n.String('minecraft:nether')})})
        }),
        'minecraft:the_end': n.Compound({
            'type': n.String('minecraft:the_end'),
            'generator': n.Compound({'type': n.String('minecraft:noise'), 'settings': n.String('minecraft:end'),
                                     'biome_source': n.Compound({'type': n.String('minecraft:the_end')})})
        })
    })
    rules = {'doDaylightCycle': 'false', 'doWeatherCycle': 'false', 'doMobSpawning': 'false',
             'doPatrolSpawning': 'false', 'doTraderSpawning': 'false', 'doInsomnia': 'false',
             'doFireTick': 'false', 'spawnRadius': '0', 'keepInventory': 'true'}
    data = n.Compound({
        'DataVersion': n.Int(3465), 'version': n.Int(19133),
        'Version': n.Compound({'Name': n.String('1.20.1'), 'Id': n.Int(3465), 'Series': n.String('main'), 'Snapshot': n.Byte(0)}),
        'LevelName': n.String(name),
        'WorldGenSettings': n.Compound({'seed': n.Long(20261114), 'generate_features': n.Byte(0),
                                        'bonus_chest': n.Byte(0), 'dimensions': dimensions}),
        'DataPacks': n.Compound({'Enabled': n.List[n.String]([n.String('vanilla'), n.String('mod:forge'), n.String('file/hk3arg_reading_room')]),
                                'Disabled': n.List[n.String]()}),
        'GameType': n.Int(0), 'allowCommands': n.Byte(0), 'hardcore': n.Byte(0),
        'Difficulty': n.Byte(0), 'DifficultyLocked': n.Byte(1), 'initialized': n.Byte(1), 'WasModded': n.Byte(1),
        'LastPlayed': n.Long(int(time.time() * 1000)), 'Time': n.Long(6000), 'DayTime': n.Long(6000),
        'raining': n.Byte(0), 'thundering': n.Byte(0), 'rainTime': n.Int(0), 'thunderTime': n.Int(0),
        'clearWeatherTime': n.Int(2147483647), 'SpawnX': n.Int(0), 'SpawnY': n.Int(1), 'SpawnZ': n.Int(4),
        'GameRules': n.Compound({key: n.String(value) for key, value in rules.items()}),
        'Player': n.Compound({
            'Pos': n.List[n.Double]([n.Double(0.5), n.Double(1), n.Double(4.5)]),
            'Rotation': n.List[n.Float]([n.Float(180), n.Float(0)]), 'Dimension': n.String('minecraft:overworld'),
            'playerGameType': n.Int(0), 'Health': n.Float(20), 'Air': n.Short(300), 'foodLevel': n.Int(20),
            'foodSaturationLevel': n.Float(5), 'SelectedItemSlot': n.Int(0),
            'Inventory': n.List[n.Compound](), 'EnderItems': n.List[n.Compound](),
            'abilities': n.Compound({'invulnerable': n.Byte(0), 'flying': n.Byte(0), 'mayfly': n.Byte(0),
                                    'instabuild': n.Byte(0), 'mayBuild': n.Byte(1),
                                    'flySpeed': n.Float(0.05), 'walkSpeed': n.Float(0.1)})
        }),
        'ScheduledEvents': n.List[n.Compound](), 'confirmedExperimentalSettings': n.Byte(1)
    })
    n.File({'Data': data}, gzipped=True).save(world / 'level.dat')
    write_json(pack / 'pack.mcmeta', {'pack': {'pack_format': 15, 'description': '西瓜来信：独立档案室与开场用品，不预设谜题进度。'}})
    write_json(pack / 'data/minecraft/tags/functions/tick.json', {'values': ['hk3arg:tick']})
    function(pack, 'tick', ['execute as @a[tag=!hk3arg_supplies] in minecraft:overworld at @s run function hk3arg:arrive'])
    function(pack, 'arrive', [
        'execute unless data storage hk3arg:scene {built:1b} run function hk3arg:room',
        'tp @s 0.5 1 4.5 180 0', 'spawnpoint @s 0 1 4',
        'give @s hk3gtl:personal_phone{Charge:128000L} 1',
        'give @s minecraft:written_book' + book + ' 1',
        'give @s minecraft:writable_book 1', 'give @s minecraft:paper 64',
        'give @s minecraft:cooked_beef 32', 'give @s minecraft:clock 1',
        *[f'give @s {item}{tag} {count}' for item, count, tag in extra_items],
        'tag @s add hk3arg_supplies',
        'tellraw @s {"text":"手机已备好。右键打开「残页译码」，从第一张残页开始。","color":"aqua"}'
    ])
    room = [
        'fill -9 0 -9 9 7 9 minecraft:air', 'fill -8 0 -8 8 0 8 minecraft:smooth_quartz',
        'fill -8 1 -8 8 5 -8 minecraft:spruce_planks', 'fill -8 1 8 8 5 8 minecraft:spruce_planks',
        'fill -8 1 -7 -8 5 7 minecraft:spruce_planks', 'fill 8 1 -7 8 5 7 minecraft:spruce_planks',
        'fill -8 6 -8 8 6 8 minecraft:stripped_spruce_log[axis=x]',
        'fill -8 2 -5 -8 4 5 minecraft:light_blue_stained_glass',
        'fill 8 2 -5 8 4 5 minecraft:light_blue_stained_glass',
        'fill -5 2 -8 5 4 -8 minecraft:light_blue_stained_glass',
        'fill -6 2 8 -3 4 8 minecraft:light_blue_stained_glass',
        'fill 3 2 8 6 4 8 minecraft:light_blue_stained_glass',
        'setblock 0 1 8 minecraft:spruce_door[half=lower,facing=north,hinge=left]',
        'setblock 0 2 8 minecraft:spruce_door[half=upper,facing=north,hinge=left]',
        'fill -6 1 -6 -5 3 -6 minecraft:bookshelf', 'fill 5 1 -6 6 3 -6 minecraft:bookshelf',
        'fill -3 1 -5 3 1 -5 minecraft:spruce_slab[type=top]',
        'setblock 0 1 -5 minecraft:lectern[facing=south,has_book=true]{Book:{id:"minecraft:written_book",Count:1b,tag:' + book + '},Page:0}',
        'setblock -3 1 -5 minecraft:crafting_table', 'setblock 3 1 -5 minecraft:barrel[facing=up]',
        'setblock 0 1 -3 minecraft:spruce_stairs[facing=north]',
        'setblock 6 1 1 minecraft:chest[facing=west]{Items:[{Slot:0b,id:"minecraft:paper",Count:64b},{Slot:1b,id:"minecraft:writable_book",Count:1b},{Slot:2b,id:"minecraft:cooked_beef",Count:32b}]}',
        'setblock -6 1 1 minecraft:spruce_fence', 'setblock -6 2 1 minecraft:lantern',
        'fill -1 1 -1 1 1 3 minecraft:green_carpet',
        'setblock -6 1 6 minecraft:potted_fern', 'setblock 6 1 6 minecraft:potted_fern',
        'fill -2 -1 9 2 -1 14 minecraft:polished_andesite',
        'fill -7 0 10 -5 0 12 minecraft:melon', 'fill 5 0 10 7 0 12 minecraft:melon'
    ]
    for x in (-4, 4):
        for z in (-4, 4):
            room.append(f'setblock {x} 5 {z} minecraft:lantern[hanging=true]')
    room.append('data modify storage hk3arg:scene built set value 1b')
    function(pack, 'room', room)
    manifest = {
        '名称': name, 'Minecraft': '1.20.1', 'Forge': '47.4.16', 'DataVersion': 3465,
        '世界目录': str(world.relative_to(ROOT)), '模式': '生存 / 和平',
        '地形': '原版平坦；64层底座，地表Y=-1，档案室地板Y=0',
        '场景': '首次进入自动布置17×17明亮档案室、书桌、讲台、书架、补给箱与装饰西瓜',
        '开场用品': {'hk3gtl:personal_phone': {'数量': 1, 'Charge': 128000},
                     'minecraft:written_book': 1, 'minecraft:writable_book': 1,
                     'minecraft:paper': 64, 'minecraft:cooked_beef': 32, 'minecraft:clock': 1},
        '状态边界': '仅新地图场景与用品领取标记；无安装、解题、收藏、研究、完成或奖励预置',
        '验证状态': '仅离线准备；未启动游戏、未安装JAR，待负责人亲自从首关完整解密验收'
    }
    if extra_items:
        manifest['额外探险补给'] = [{'物品': item, '数量': count, '物品标签': tag} for item, count, tag in extra_items]
    write_json(world / '离线准备清单.json', manifest)
    return manifest


if __name__ == '__main__':
    print(json.dumps(main(), ensure_ascii=False))
