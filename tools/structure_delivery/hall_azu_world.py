"""导出全新1.20.1礼堂测试世界；拒绝覆盖，绝不直接降级源1.20.4世界。"""
import argparse
import copy
import gzip
import hashlib
import io
import json
import math
import struct
import time
import zipfile
import zlib
from collections import defaultdict
from pathlib import Path

import nbtlib
import numpy as np
from nbtlib import Byte, Compound, Double, Float, Int, List, Long, LongArray, Short, String

from hall_azu_extract import decode_section, parse_nbt, state_string

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'output/hall-azu-analysis'
OUT = ROOT / 'output/w01-runtime-20261029/world'
TEMPLATE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft/saves/hk3gtl-controller-r178-review/level.dat')
SOURCE = Path('C:/Users/OWNER/下載/永恒的礼堂_Azu.zip')


def encode_nbt(tag):
    stream = io.BytesIO()
    nbtlib.File(tag).write(stream)
    return stream.getvalue()


def encode_states(states):
    used, inverse = np.unique(states, return_inverse=True)
    if len(used) == 1:
        return used.tolist(), None
    bits = max(4, (len(used) - 1).bit_length())
    per = 64 // bits
    padded = np.zeros(math.ceil(4096 / per) * per, dtype=np.uint64)
    padded[:4096] = inverse.astype(np.uint64)
    words = np.bitwise_or.reduce(padded.reshape(-1, per) << (np.arange(per, dtype=np.uint64) * bits), axis=1)
    assert np.array_equal(decode_section(words.view(np.int64), len(used)), inverse)
    return used.tolist(), LongArray(words.view(np.int64))


def state_tag(state):
    name, _, tail = state.partition('[')
    result = Compound({'Name': String(name)})
    if tail:
        result['Properties'] = Compound({p.split('=', 1)[0]: String(p.split('=', 1)[1]) for p in tail.rstrip(']').split(',')})
    return result


def source_signs(positions):
    """只保留主展区原有告示牌NBT；没有继承用户库存/UUID/实体。"""
    occupied = {tuple(int(v) for v in row) for row in positions}
    result = defaultdict(list)
    with zipfile.ZipFile(SOURCE) as archive:
        for row in archive.infolist():
            if '/region/' not in row.filename or not row.filename.endswith('.mca') or not row.file_size:
                continue
            data = archive.read(row)
            for i in range(1024):
                at = int.from_bytes(data[i * 4:i * 4 + 3], 'big') * 4096
                if not at:
                    continue
                length = struct.unpack_from('>I', data, at)[0]
                compression = data[at + 4]
                raw = data[at + 5:at + 4 + length]
                chunk = parse_nbt(gzip.decompress(raw) if compression == 1 else zlib.decompress(raw) if compression == 2 else raw)
                for entity in chunk.get('block_entities', []):
                    xyz = tuple(int(entity[k]) for k in ['x', 'y', 'z'])
                    if xyz in occupied:
                        assert str(entity['id']) == 'minecraft:sign', '未知源方块实体，须单独迁移：' + str(entity['id'])
                        result[(xyz[0] // 16, xyz[2] // 16)].append(copy.deepcopy(entity))
    return result


def level_data(spawn):
    template = parse_nbt(gzip.decompress(TEMPLATE.read_bytes()))['Data']
    assert int(template['DataVersion']) == 3465
    worldgen = copy.deepcopy(template['WorldGenSettings'])
    worldgen['seed'] = Long(0)
    worldgen['generate_features'] = Byte(0)
    worldgen['bonus_chest'] = Byte(0)
    worldgen['dimensions']['minecraft:overworld']['type'] = String('minecraft:overworld')
    worldgen['dimensions']['minecraft:overworld']['generator'] = Compound({
        'type': String('minecraft:flat'), 'settings': Compound({
            'features': Byte(0), 'lakes': Byte(0), 'layers': List[Compound]([Compound({'block': String('minecraft:air'), 'height': Int(1)})]),
            'structure_overrides': List[String](), 'biome': String('minecraft:plains')})})
    rules = {'doDaylightCycle': 'false', 'doWeatherCycle': 'false', 'doMobSpawning': 'false',
             'doPatrolSpawning': 'false', 'doTraderSpawning': 'false', 'doInsomnia': 'false',
             'doFireTick': 'false', 'randomTickSpeed': '0', 'spawnRadius': '0',
             'keepInventory': 'true', 'fallDamage': 'false', 'fireDamage': 'false',
             'drowningDamage': 'false', 'disableRaids': 'true', 'doTileDrops': 'false'}
    return Compound({'Data': Compound({
        'DataVersion': Int(3465), 'version': Int(19133), 'Version': copy.deepcopy(template['Version']),
        'LevelName': String('hk3gtl-w01-azu-runtime-20261029'), 'WorldGenSettings': worldgen,
        'DataPacks': copy.deepcopy(template['DataPacks']), 'GameType': Int(1), 'allowCommands': Byte(1),
        'hardcore': Byte(0), 'Difficulty': Byte(0), 'DifficultyLocked': Byte(1),
        'initialized': Byte(1), 'WasModded': Byte(1), 'LastPlayed': Long(int(time.time() * 1000)),
        'Time': Long(6000), 'DayTime': Long(6000), 'raining': Byte(0), 'thundering': Byte(0),
        'rainTime': Int(0), 'thunderTime': Int(0), 'clearWeatherTime': Int(2147483647),
        'SpawnX': Int(spawn[0]), 'SpawnY': Int(spawn[1]), 'SpawnZ': Int(spawn[2]),
        'GameRules': Compound({k: String(v) for k, v in rules.items()}),
        'Player': Compound({'Pos': List[Double]([Double(spawn[0] + .5), Double(spawn[1]), Double(spawn[2] + .5)]),
                            'Rotation': List[Float]([Float(0), Float(15)]),
                            'Dimension': String('minecraft:overworld'), 'playerGameType': Int(1),
                            'Health': Float(20), 'Air': Short(300), 'foodLevel': Int(20),
                            'Inventory': List[Compound](), 'EnderItems': List[Compound](),
                            'abilities': Compound({'invulnerable': Byte(1), 'flying': Byte(1), 'mayfly': Byte(1),
                                                   'instabuild': Byte(1), 'mayBuild': Byte(1),
                                                   'flySpeed': Float(.05), 'walkSpeed': Float(.1)})}),
        'ScheduledEvents': List[Compound](), 'confirmedExperimentalSettings': Byte(1)})})


def write_region(path, chunks):
    header = bytearray(8192)
    payload = []
    sector = 2
    for (cx, cz), raw in sorted(chunks.items()):
        compressed = zlib.compress(raw, level=6)
        count = math.ceil((len(compressed) + 5) / 4096)
        assert count < 256
        index = (cx % 32) + 32 * (cz % 32)
        header[index * 4:index * 4 + 4] = sector.to_bytes(3, 'big') + bytes([count])
        header[4096 + index * 4:4100 + index * 4] = int(time.time()).to_bytes(4, 'big')
        item = struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed
        payload.append(item + bytes(count * 4096 - len(item)))
        sector += count
    path.write_bytes(header + b''.join(payload))


def readback(world, palette):
    lookup = {state: n for n, state in enumerate(palette)}
    points, states = [], []
    for path in sorted((world / 'region').glob('*.mca')):
        data = path.read_bytes()
        for i in range(1024):
            at = int.from_bytes(data[i * 4:i * 4 + 3], 'big') * 4096
            if not at:
                continue
            length = struct.unpack_from('>I', data, at)[0]
            assert data[at + 4] == 2
            chunk = parse_nbt(zlib.decompress(data[at + 5:at + 4 + length]))
            assert int(chunk['DataVersion']) == 3465 and str(chunk['Status']) == 'minecraft:full'
            cx, cz = int(chunk['xPos']), int(chunk['zPos'])
            for section in chunk['sections']:
                bs = section['block_states']
                names = [state_string(p) for p in bs['palette']]
                values = decode_section(bs.get('data'), len(names))
                present = np.array([name != 'minecraft:air' for name in names])[values]
                indexes = np.flatnonzero(present)
                points.append(np.stack([indexes % 16 + cx * 16, indexes // 256 + int(section['Y']) * 16,
                                        (indexes // 16) % 16 + cz * 16], axis=1))
                states.append(np.array([lookup.get(name, -1) for name in names])[values[present]])
    return np.concatenate(points), np.concatenate(states)


def canonical_digest(points, states):
    order = np.lexsort((points[:, 2], points[:, 1], points[:, 0]))
    raw = np.column_stack([points[order], states[order]]).astype('<i4').tobytes()
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=OUT)
    parser.add_argument('--spawn', type=int, nargs=3, default=[7, -16, -21])
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.exists(), '拒绝覆盖已有世界：' + str(out)
    assert out.is_relative_to((ROOT / 'output').resolve()), '仅允许导出到本项目output新目录'
    out.mkdir(parents=True)
    (out / 'region').mkdir()
    scene = np.load(DATA / 'scene-main.npz')
    pos, states = scene['positions'], scene['states']
    palette = json.loads((DATA / 'palette.json').read_text(encoding='utf-8'))
    assert len(pos) == 1933767 and pos[:, 1].min() == -63 and pos[:, 1].max() == 319
    tags = [Compound({'Name': String('minecraft:air')}), *[state_tag(s) for s in palette]]
    signs = source_signs(pos)
    groups = defaultdict(list)
    for index, (x, y, z) in enumerate(pos):
        groups[(int(x) // 16, int(z) // 16)].append(index)
    regions = defaultdict(dict)
    for (cx, cz), indexes in groups.items():
        indexes = np.array(indexes)
        p, values = pos[indexes], states[indexes].astype(np.uint16) + 1
        sections = []
        for sy in sorted(set((p[:, 1] // 16).tolist())):
            take = p[:, 1] // 16 == sy
            local = p[take] % 16
            linear = local[:, 1] * 256 + local[:, 2] * 16 + local[:, 0]
            container = np.zeros(4096, dtype=np.uint16)
            container[linear] = values[take]
            selected, packed = encode_states(container)
            block_states = Compound({'palette': List[Compound]([tags[k] for k in selected])})
            if packed is not None:
                block_states['data'] = packed
            sections.append(Compound({'Y': Byte(sy), 'block_states': block_states,
                                     'biomes': Compound({'palette': List[String]([String('minecraft:plains')])})}))
        chunk = Compound({'DataVersion': Int(3465), 'xPos': Int(cx), 'zPos': Int(cz), 'yPos': Int(-4),
                          'Status': String('minecraft:full'), 'LastUpdate': Long(0), 'InhabitedTime': Long(0),
                          'isLightOn': Byte(0), 'sections': List[Compound](sections),
                          'block_entities': List[Compound](signs.get((cx, cz), [])),
                          'block_ticks': List[Compound](), 'fluid_ticks': List[Compound](),
                          'Heightmaps': Compound(), 'structures': Compound({'References': Compound(), 'starts': Compound()})})
        regions[(cx // 32, cz // 32)][(cx, cz)] = encode_nbt(chunk)
    for (rx, rz), chunks in regions.items():
        write_region(out / 'region' / f'r.{rx}.{rz}.mca', chunks)
    (out / 'level.dat').write_bytes(gzip.compress(encode_nbt(level_data(args.spawn)), mtime=0))
    check_pos, check_states = readback(out, palette)
    expected = canonical_digest(pos, states)
    actual = canonical_digest(check_pos, check_states)
    assert len(check_pos) == len(pos) and actual == expected, '世界读回与建筑原始坐标/状态不符'
    metadata = dict(output=str(out), world_name='hk3gtl-w01-azu-runtime-20261029', target_data_version=3465,
                    source_scene=str(DATA / 'scene-main.npz'), blocks=len(pos), chunks=len(groups), regions=len(regions),
                    min_xyz=pos.min(0).tolist(), max_xyz=pos.max(0).tolist(),
                    source_template=str(TEMPLATE), source_template_sha256=hashlib.sha256(TEMPLATE.read_bytes()).hexdigest(),
                    source_zip_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                    controller={'planned_world_xyz': [7, -16, -17], 'planned_id': 'hk3gtl:w01_origin_stellar_concert_court',
                                'planned_front': 'north', 'placed': False, 'source_state': 'minecraft:smooth_quartz'},
                    spawn_xyz=args.spawn, player_position=[args.spawn[0] + .5, args.spawn[1], args.spawn[2] + .5],
                    player_rotation_yaw_pitch=[0, 15], player_flying_creative=True,
                    imported_sign_block_entities=sum(len(v) for v in signs.values()),
                    readback_exact_state_coordinate_sha256=actual, readback_passed=True,
                    notes=['新世界仅导入主展区原坐标，未替换方块，未添加controller或接口。',
                           '源1.20.4世界没有直接降级；新Anvil和level.dat为1.20.1 DataVersion3465。',
                           '仅以目标1.20.1测试level.dat的世界生成/数据包设置为基础；未复制源Player、UUID、物品、进度、存档data或entities。新建无UUID空背包创造飞行Player，仅固定测试位置。',
                           '空Heightmaps与isLightOn=false要求游戏自行重建；未冒称已成功加载或成型。',
                           '未复制到游戏实例；没有修改现有世界或源ZIP。'])
    (out.parent / 'world-export.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(metadata, ensure_ascii=False))


if __name__ == '__main__':
    main()
