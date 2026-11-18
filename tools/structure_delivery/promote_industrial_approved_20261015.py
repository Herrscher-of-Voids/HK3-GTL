#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将本轮已批准工业蓝图映射为正式资源；不修改批准建筑或旧交付文件。"""
import argparse
import hashlib
import json
from pathlib import Path
import nbtlib as nbt

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources/data/hk3gtl/approved_architecture'
LOG = ROOT / 'logs/approved-architecture-runtime'
PORTS = {
    'i01': 'INPUT:item_input COOLANT:fluid_input POWER:item OUTPUT:fluid_output RECOVERY:item_output RETURN:fluid',
    'i02': 'STANDARD:item_input SAMPLE:item_input REFERENCE:item_input DATA:item_output RETURN:item_output POWER:service',
    'i03': 'SOLVENT:fluid_input MOTHER_LIQUID:fluid_input POWER:item_input LIGHT_PHASE:fluid_output HEAVY_PHASE:fluid_output RESIDUE:item_output',
    'i04': 'WASH:fluid_input LIQUID_ENERGY:fluid_input STABILIZER:item_input STABLE_LIQUID:fluid_output COOLANT:fluid_output POWER:item_output',
    'i05': 'FEED:fluid_input FILTER:item_input POWER:service RESIDUE:item_output COOLANT:fluid_output PRODUCT:fluid_output',
    'i06': 'BASE:item_input MEDIUM:fluid_input POWER:service CATALYST:item_input FUEL:fluid_output RESIDUE:item_output',
    'i07': 'REFERENCE:item_input TEST_PIECE:item_input POWER:service READOUT:item_output PRODUCT:item_output REJECT:item_output',
    'i08': 'PRECURSOR:item_input MEDIUM:fluid_input POWER:service COOLANT:fluid_output CRYSTAL:item_output RESIDUE:fluid_output',
    'i09': 'WASH:fluid_input SOLVENT:fluid_input POWDER:item_input POWER:item_output PRECURSOR:fluid_output RECOVERY:fluid_output',
    'i10': 'PRECURSOR:fluid_input TEMPLATE:item_input POWER:service NANO_UNIT:item_output COOLANT:fluid_input TAIL_GAS:fluid_output',
    'i11': 'BODY:item_input CORE:item_input POWER:fluid_input MATERIAL:item_input ROBOT:item_output SCRAP:item_output',
    'i12': 'TEMPLATE:item_input SAMPLE:fluid_input POWER:service DATA:item_output NANITE:item_output RETURN:fluid_output',
    'i13': 'SWARM:item_input COATING:fluid_input POWER:service COOLANT:fluid_input PRODUCT:item_output REJECT:fluid_output',
}
MACHINES = {
    'i01': 'i01_honkai_collection_tower', 'i01_2': 'i01_2_honkai_collection_tower',
    'i01_3': 'i01_3_honkai_collection_tower', 'i01_4': 'i01_4_honkai_collection_tower',
    'i02': 'i02_spectrum_analysis_array', 'i03': 'liquid_honkai_fractionation_center',
    'i04': 'liquid_honkai_stabilization_tower', 'i05': 'stabilization_medium_regeneration_tower',
    'i06': 'honkai_fuel_blending_plant', 'i07': 'honkai_detector_calibration_bench',
    'i08': 'imitation_core_crystallization_chamber', 'i09': 'soulium_precursor_mixing_kettle',
    'i10': 'nano_basic_unit_synthesizer', 'i11': 'nanobot_assembly_array',
    'i12': 'nano_self_organizing_programming_chamber', 'i13': 'i13_honkai_resistant_coating_array',
}
ABILITIES = {
    'item_input': {'item_input'}, 'item_output': {'item_output'},
    'item': {'item_input', 'item_output'}, 'fluid_input': {'fluid_input'},
    'fluid_output': {'fluid_output'}, 'fluid': {'fluid_input', 'fluid_output'}, 'service': set(),
}
HATCH_BLOCKS = {'item_input': 'gtceu:max_input_bus', 'item_output': 'gtceu:max_output_bus',
                'fluid_input': 'gtceu:max_input_hatch', 'fluid_output': 'gtceu:max_output_hatch'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required(key):
    # 最低数量来自实际工艺方向；无线玩家电网不需要普通 GT 能源仓。
    if key == 'i01':
        return {'item_input', 'fluid_output'}
    if key in {'i02', 'i07'}:
        return {'item_input', 'item_output'}
    if key == 'i11':
        return {'item_input', 'item_output', 'fluid_input'}
    return {'item_input', 'item_output', 'fluid_input', 'fluid_output'}


def state_text(state):
    name = str(state['Name'])
    if state.get('Properties'):
        name += '[' + ','.join(f'{key}={value}' for key, value in sorted(state['Properties'].items())) + ']'
    return name


def template(source_path, key, data, resource):
    source_nbt = next(source_path.parent.glob('*.nbt'))
    structure = nbt.load(source_nbt)
    positions = {tuple(map(int, block['pos'])): block for block in structure['blocks']}
    approved = json.loads(source_path.read_text(encoding='utf-8'))
    old = {pos: state_text(structure['palette'][int(block['state'])]) for pos, block in positions.items()}
    assert old == {tuple(b['pos']): b['state'] for b in approved['blocks']}
    assert list(map(int, structure['size'])) == data['size']

    def index(name, facing='north'):
        value = nbt.Compound({'Name': nbt.String(name),
                              'Properties': nbt.Compound({'facing': nbt.String(facing)})})
        for i, state in enumerate(structure['palette']):
            if state == value:
                return i
        structure['palette'].append(value)
        return len(structure['palette']) - 1

    controller = tuple(data['controller'])
    positions[controller]['state'] = nbt.Int(index('hk3gtl:' + MACHINES[key]))
    # I01 第一阶预装四方向仓，后三阶无需更换任一既有接口方块。
    wanted = {'item_input', 'item_output', 'fluid_input', 'fluid_output'} if key.startswith('i01') else required(key)
    placed = {}
    for ability in sorted(wanted):
        port = next(port for port in data['ports'] if ability in ABILITIES[port['group']]
                    and port['id'] not in placed)
        placed[port['id']] = ability
        positions[tuple(port['pos'])]['state'] = nbt.Int(index(HATCH_BLOCKS[ability], port['face']))
    port_positions = {tuple(port['pos']) for port in data['ports']}
    actual = {pos: state_text(structure['palette'][int(block['state'])]) for pos, block in positions.items()}
    assert all(old[pos] == state for pos, state in actual.items() if pos != controller and pos not in port_positions)
    assert required(key) <= set(placed.values())
    target = ROOT / f'src/main/resources/data/hk3gtl/structures/approved/{key}.nbt'
    target.parent.mkdir(parents=True, exist_ok=True)
    structure.save(target, gzipped=True)
    loaded = nbt.load(target)
    decoded = {tuple(map(int, block['pos'])): state_text(loaded['palette'][int(block['state'])])
               for block in loaded['blocks']}
    assert decoded == actual
    assert all(decoded[tuple(port['pos'])].startswith(HATCH_BLOCKS[placed[port['id']]] + '[')
               if port['id'] in placed else decoded[tuple(port['pos'])] == 'hk3gtl:industrial_port_casing'
               for port in data['ports'])
    manifest = {'key': key, 'source': f'data/hk3gtl/approved_architecture/{key}.json',
                'machine': 'hk3gtl:' + MACHINES[key], 'sha256': sha(resource),
                'template_sha256': sha(target), 'approved_blueprint_sha256': sha(source_path),
                'approved_nbt_sha256': sha(source_nbt), 'review_snapshot': str(source_path.parent.parent.relative_to(ROOT)),
                'controller': list(controller), 'size_xyz': data['size'], 'blocks': len(actual),
                'required_abilities': sorted(required(key)), 'installed_hatches': placed,
                'geometry_changes': '仅主控和六接口处替换；其余批准块无变化', 'game_verified': False}
    target.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'template_sha256': sha(target), 'template_hatches': placed, 'template_other_changes': 0}


def promote(path, key, version):
    source = json.loads(path.read_text(encoding='utf-8'))
    source_cells = {tuple(b['pos']): b['state'] for b in source['blocks']}
    controller = tuple(source['controller'])
    assert len(source_cells) == len(source['blocks'])
    assert source_cells[controller] == 'minecraft:diamond_block'
    groups = dict(part.split(':', 1) for part in PORTS['i01' if key.startswith('i01') else key].split())
    assert set(groups) == {port['id'] for port in source['ports']}
    assert len(source['ports']) == 6
    for port in source['ports']:
        assert port['face'] == 'north' and tuple(port['pos']) != controller
        assert source_cells[tuple(port['pos'])] == 'hk3gtl:industrial_port_casing'
    # 枚举六个槽位的可选能力，确认全部必要方向可以同时占用不同真实仓。
    choices = [ABILITIES[groups[port['id']]] for port in source['ports']]
    def assign(pending, occupied):
        if not pending:
            return True
        ability, *rest = pending
        return any(ability in options and i not in occupied and assign(rest, occupied | {i})
                   for i, options in enumerate(choices))
    assert assign(sorted(required(key)), set()), f'{key} 无法同时安装必要真实仓'
    data = {'key': key, 'size': source['size'], 'controller': source['controller'],
            'title': source['title'], 'ports': [{**p, 'group': groups[p['id']]} for p in source['ports']],
            'blocks': [{'pos': b['pos'], 'state': 'hk3gtl:' + MACHINES[key] if tuple(b['pos']) == controller
                        else b['state']} for b in source['blocks']],
            'approved_source': {'version': version, 'blueprint': str(path.relative_to(ROOT)).replace('\\', '/'),
                                'sha256': sha(path), 'approval': '很好先把现在这些多方块结构实装'},
            'runtime_contract': {'controller': 'hk3gtl:' + MACHINES[key],
                                 'required_abilities': sorted(required(key)), 'energy': 'bound_player_wireless_eu',
                                 'empty_port_filler': 'hk3gtl:industrial_port_casing',
                                 'geometry_changes': '仅把指定钻石主控替换为实际控制器，全部其余状态和坐标保留'}}
    target = RES / f'{key}.json'
    target.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    reread = json.loads(target.read_text(encoding='utf-8'))
    formal = {tuple(b['pos']): b['state'] for b in reread['blocks']}
    assert source_cells.keys() == formal.keys()
    assert all(state == formal[pos] for pos, state in source_cells.items() if pos != controller)
    template_result = template(path, key, data, target)
    return {'key': key, 'machine': 'hk3gtl:' + MACHINES[key], 'size_xyz': data['size'], **template_result,
            'blocks': len(formal), 'non_controller_changes': 0, 'source_sha256': sha(path),
            'resource_sha256': sha(target), 'ports': data['ports'], 'required_abilities': sorted(required(key)),
            'source': data['approved_source']['blueprint'], 'version': version}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--i01-root', type=Path)
    parser.add_argument('--i02-i08-root', type=Path)
    parser.add_argument('--i09-i13-root', type=Path)
    args = parser.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    rows = []
    if args.i01_root:
        for stage in range(1, 5):
            key = 'i01' if stage == 1 else f'i01_{stage}'
            rows.append(promote(args.i01_root.resolve() / f'i01-{stage}/blueprint.json', key, 'V8'))
    for base, start, end, version in [(args.i02_i08_root, 2, 8, 'V7'), (args.i09_i13_root, 9, 13, 'V6')]:
        if base:
            for number in range(start, end + 1):
                key = f'i{number:02d}'
                rows.append(promote(base.resolve() / key / 'blueprint.json', key, version))
    output = LOG / 'industrial-promotion.json'
    existing = json.loads(output.read_text(encoding='utf-8')) if output.exists() else {'structures': []}
    merged = {row['key']: row for row in existing['structures']}
    merged.update({row['key']: row for row in rows})
    existing.update({'approval': '很好先把现在这些多方块结构实装', 'scope': '正式工业 Pattern 资源',
                     'structures': [merged[key] for key in sorted(merged)], 'game_verified': False})
    output.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps([{k: v for k, v in row.items() if k in {'key', 'size_xyz', 'blocks', 'non_controller_changes'}}
                      for row in rows], ensure_ascii=False))


if __name__ == '__main__':
    main()
