"""按正式结构生成多方块建材样板目录与 FTB 任务页。"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

import nbtlib
import numpy as np


PROJECT = Path(__file__).resolve().parents[1]
W11_RUN = np.dtype([('x', '>i4'), ('y', '>i4'), ('z', '>i4'),
                    ('count', 'u1'), ('state', '>u2')])


def blueprint_counts(path, controller=None, overrides=None):
    with gzip.open(path, 'rb') as source:
        magic, version = struct.unpack('>II', source.read(8))
        width, height, depth, cx, cy, cz, count = struct.unpack('>7i', source.read(28))
        runs = struct.unpack('>i', source.read(4))[0] if magic == 0x484B3357 else 0
        palette_size = struct.unpack('>H', source.read(2))[0]
        palette = [source.read(struct.unpack('>H', source.read(2))[0]).decode('utf-8')
                   for _ in range(palette_size)]
        counts = np.zeros(palette_size, dtype=np.int64)
        corrections = Counter()
        if magic == 0x57303141 and version == 1:
            remaining = count
            control = (cx << 20) | (cy << 10) | cz
            while remaining:
                size = min(remaining, 65536)
                cells = np.frombuffer(source.read(size * 8), dtype='>u8')
                states = cells & 65535
                at_controller = states[(cells >> 16) == control]
                if len(at_controller):
                    control_state = int(at_controller[0])
                counts += np.bincount(states.astype(np.int32), minlength=palette_size)
                remaining -= size
        elif magic == 0x484B3357 and version == 1:
            while runs:
                size = min(runs, 65536)
                rows = np.frombuffer(source.read(size * W11_RUN.itemsize), dtype=W11_RUN)
                counts += np.bincount(rows['state'], weights=rows['count'],
                                      minlength=palette_size).astype(np.int64)
                runs -= size
        elif magic == 0x484B3350 and version in (1, 2):
            record = struct.Struct('>iHi' if version == 1 else '>iiiHi')
            pending = {int(position): state for position, state in (overrides or {}).items()}
            if controller:
                pending[(cx * height + cy) * depth + cz] = controller
            remaining = count
            while remaining:
                values = record.unpack(source.read(record.size))
                start, step, length, state, entity_bytes = (values[0], 1, 1, values[1], values[2]) if version == 1 else values
                counts[state] += length
                if pending:
                    for position in tuple(pending):
                        offset = position - start
                        if offset == 0 or step and offset % step == 0 and 0 <= offset // step < length:
                            corrections[palette[state]] -= 1
                            corrections[pending.pop(position)] += 1
                source.read(entity_bytes)
                remaining -= length
            if pending:
                raise ValueError('结构替换坐标不存在：' + str(path))
        else:
            raise ValueError('未知的结构格式：' + str(path))
        if int(counts.sum()) != count or source.read(1):
            raise ValueError('结构方块数量或结尾不一致：' + str(path))
    result = Counter()
    for state, amount in zip(palette, counts):
        if amount:
            result[state] += int(amount)
    result.update(corrections)
    if controller and magic == 0x57303141:
        result[palette[control_state]] -= 1
        result[controller] += 1
    return +result


def nbt_counts(path):
    template = nbtlib.load(path)
    palette = []
    for state in template['palette']:
        properties = state.get('Properties', {})
        text = str(state['Name'])
        if properties:
            text += '[' + ','.join(f'{key}={properties[key]}' for key in sorted(properties)) + ']'
        palette.append(text)
    return Counter(palette[int(block['state'])] for block in template['blocks'])


def entries(resources):
    data = resources / 'data/hk3gtl'
    language = json.loads((resources / 'assets/hk3gtl/lang/zh_cn.json').read_text(encoding='utf-8'))
    result = []

    def add(key, controller, counts):
        result.append(dict(key=key, controller=controller,
            title=language['block.' + controller.replace(':', '.')],
            materials=[dict(state=state, count=count) for state, count in sorted(counts.items())]))

    metadata = sorted((data / 'compact_architecture').glob('*.json'))
    for path in metadata:
        entry = json.loads(path.read_text(encoding='utf-8'))
        key = path.stem
        add(key, entry['machine'], blueprint_counts(data / 'structures/compact' / (key + '.bin.gz'),
            entry['machine'], entry.get('layout_state_overrides')))

    source = (PROJECT / 'src/main/java/com/sirin/hk3gtl/common/machine/wonder/Hk3WonderCatalog.java').read_text(encoding='utf-8')
    for role, controller in re.findall(r'new Entry\("(W\d{2})", "([^"]+)"', source):
        key = role.lower()
        filename = {'W01': 'w01_hall', 'W02': 'w02_19c_a2', 'W03': 'w03_c9'}.get(role, key + '_candidate')
        controller = 'hk3gtl:' + controller
        add(key, controller, blueprint_counts(data / 'structures' / (filename + '.bin.gz'),
                                             controller if role == 'W01' else None))

    add('hyperion', 'hk3gtl:hyperion_flagship', blueprint_counts(data / 'structures/hyperion_construction.bin.gz'))
    add('ae_nexus', 'hk3gtl:ae_nexus', nbt_counts(data / 'structures/ae_nexus_a1.nbt'))
    add('network_injector', 'hk3gtl:honkai_network_injector', Counter())
    return result


def object_id(key, kind):
    return '4B6' + hashlib.sha256(('multiblock_patterns:' + kind + ':' + key).encode()).hexdigest()[:13].upper()


def chapter(entries):
    industrial = [entry for entry in entries if re.fullmatch(r'i\d+(?:_\d+)?', entry['key'])]
    industrial.sort(key=lambda entry: tuple(map(int, re.findall(r'\d+', entry['key']))))
    industrial += [entry for entry in entries if entry['key'] == 'network_injector']
    research = [entry for entry in entries if re.fullmatch(r's\d+', entry['key'])]
    collaboration = [entry for entry in entries if entry['key'] == 'ae_nexus']
    wonders = [entry for entry in entries if re.fullmatch(r'w\d+', entry['key']) or entry['key'] == 'hyperion']
    sections = [(industrial, '工业设备', 0, 0, 6), (research, '研究所', 28, 0, 5),
                (collaboration, 'AE 集成', 28, 8, 5), (wonders, '文明奇观与舰体', 28, 16, 4)]
    quests = []
    for group, title, x, y, columns in sections:
        for index, entry in enumerate(group):
            key, controller = entry['key'], entry['controller']
            quests.append(dict(id=object_id(key, 'quest'), title=entry['title'], subtitle=title + ' · 建材样板',
                description=['取得这台设备的控制器，即可领取填好建材与数量的 AE 样板。',
                             '将样板放入朝向独立备料容器的样板供应器，关闭供应器的自动扩大样板。每张下单 1 份，并持续腾出收料空间。',
                             '材料全部到齐后取消等待材料清单的订单，释放合成 CPU。备料容器不要接回同一 AE 库存。',
                             '样板包含主体建材；输入输出仓、能源仓等按实际工艺另配。控制器已经取得，不再重复计入。',
                             '样板只写入能够转成物品的建材；末地传送门、活塞头等无物品状态不会进入 AE 订单，门上半不重复计数，双层台阶按两块计算。',
                             '请按建材数量准备容量充足的备料容器，大型建筑需要存放数百万乃至更多方块。'],
                tasks=[dict(id=object_id(key, 'task'), type='item', item=controller, count=1, consume_items=False)],
                rewards=[dict(id=object_id(key, 'reward'), type='custom', title='预制建材样板', team_reward=False,
                              icon='ae2:processing_pattern', tags=['hk3gtl:multiblock_pattern:' + key])],
                icon=controller, x=x + index % columns * 4, y=y + index // columns * 4))
            if key == 'w01':
                quests[-1]['description'].append('庭内需要 4 个亮度为 15 的光源方块。用 1 个荧石块和 1 个玻璃合成 4 个，终极终端会按蓝图放置。')
    return dict(filename='hk3_multiblock_patterns', id=object_id('library', 'chapter'), title='HK3 多方块样板库',
        subtitle=['预制建材样板'], group='68CBF1606D696C68', order_index=32,
        icon='ae2:processing_pattern', default_quest_shape='rsquare', quests=quests)


def write(path, data, *, indent=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=indent,
                              separators=None if indent else (',', ':')) + '\n', encoding='utf-8')


def main():
    resources = Path(sys.argv[1])
    catalog = entries(resources)
    write(resources / 'data/hk3gtl/catalog/multiblock_pattern_library.json', catalog)
    write(resources / 'assets/hk3gtl/ftbquests/chapters/hk3_multiblock_patterns.snbt', chapter(catalog), indent=2)
    summary = dict(controllers=len(catalog), quests=len(catalog),
                   structure_blocks=sum(material['count'] for entry in catalog for material in entry['materials']))
    if len(sys.argv) > 2:
        write(Path(sys.argv[2]), summary, indent=2)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
