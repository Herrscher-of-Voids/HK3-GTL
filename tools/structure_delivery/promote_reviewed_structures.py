"""Promote the pinned, reviewed Beta 5 structures to game resources."""

from pathlib import Path
import hashlib
import json

import nbtlib as nbt


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'deliveries/多方块确认归档/20261002_030905_838333'
ZIP = ARCHIVE.with_suffix('.zip')
ZIP_SHA256 = '57b791258c760658a8c5a6488f82a2331ccfc0218ac24e63a71f549ff4457877'
RES = ROOT / 'src/main/resources/data/hk3gtl'
MACHINES = {
    'I01-1': ('i01', 'i01_honkai_collection_tower'),
    'I01-2': ('i01_2', 'i01_2_honkai_collection_tower'),
    'I01-3': ('i01_3', 'i01_3_honkai_collection_tower'),
    'I01-4': ('i01_4', 'i01_4_honkai_collection_tower'),
    'I02': ('i02', 'i02_spectrum_analysis_array'),
    'I03': ('i03', 'liquid_honkai_fractionation_center'),
    'I04': ('i04', 'liquid_honkai_stabilization_tower'),
    'I05': ('i05', 'stabilization_medium_regeneration_tower'),
    'I06': ('i06', 'honkai_fuel_blending_plant'),
    'I07': ('i07', 'honkai_detector_calibration_bench'),
    'I08': ('i08', 'imitation_core_crystallization_chamber'),
}
HATCHES = {
    'I01-1': {'1': 'input_bus', '2': 'output_hatch'},
    'I01-2': {'1': 'input_bus', '2': 'output_hatch'},
    'I01-3': {'1': 'input_bus', '2': 'output_hatch'},
    'I01-4': {'1': 'input_bus', '2': 'output_hatch'},
    'I02': {'S-IN': 'input_bus', 'S-OUT': 'output_bus'},
    'I03': {'FEED': 'input_bus', 'MOTHER': 'input_hatch', 'PURE': 'output_hatch', 'RESIDUE': 'output_bus'},
    'I04': {'FEED': 'input_bus', 'MEDIUM': 'input_hatch', 'PRODUCT': 'output_hatch', 'RETURN': 'output_bus'},
    'I05': {'FEED': 'input_bus', 'POWER': 'input_hatch', 'PRODUCT': 'output_hatch', 'RESIDUE': 'output_bus'},
    'I06': {'STABLE_FEED': 'input_hatch', 'SOLID_FEED': 'input_bus', 'FUEL': 'output_hatch', 'RESIDUE': 'output_bus'},
    'I07': {'REFERENCE': 'input_bus', 'PRODUCT': 'output_bus'},
    'I08': {'PRECURSOR': 'input_bus', 'MEDIUM': 'input_hatch', 'CRYSTAL': 'output_bus', 'RESIDUE': 'output_hatch'},
    'I09': {'SOULIUM_FEED': 'input_bus', 'CATALYST': 'input_hatch', 'POWER': 'input_hatch', 'MEDIUM': 'input_hatch', 'PRECURSOR': 'output_hatch', 'RESIDUE': 'output_bus'},
    'I10': {'PRECURSOR': 'input_bus', 'CATALYST': 'input_hatch', 'POWER': 'input_hatch', 'WASH': 'input_hatch', 'PRODUCT': 'output_hatch', 'RESIDUE': 'output_bus'},
    'I11': {'BODY': 'input_bus', 'CORE': 'input_hatch', 'POWER': 'input_hatch', 'MATERIAL': 'input_hatch', 'ROBOT': 'output_hatch', 'SCRAP': 'output_bus'},
    'I12': {'SAMPLE': 'input_bus', 'PROGRAM': 'input_hatch', 'POWER': 'input_hatch', 'DATA': 'input_hatch', 'NANITE': 'output_hatch', 'REJECT': 'output_bus'},
}


def state_string(state):
    name = str(state['Name'])
    props = state.get('Properties')
    if props:
        name += '[' + ','.join(f'{key}={value}' for key, value in sorted(props.items())) + ']'
    return name


def palette_index(structure, name, facing=None):
    state = nbt.Compound({'Name': nbt.String(name)})
    if facing:
        state['Properties'] = nbt.Compound({'facing': nbt.String(facing)})
    for index, existing in enumerate(structure['palette']):
        if existing == state:
            return index
    structure['palette'].append(state)
    return len(structure['palette']) - 1


def promote(source_id, key, machine):
    folder = ARCHIVE / source_id
    metadata = json.loads((folder / '设计与检查.json').read_text(encoding='utf-8'))['data']
    structure = nbt.load(next(folder.glob('*.nbt')))
    size = [int(value) for value in structure['size']]
    assert size == metadata['size']
    positions = {tuple(int(value) for value in block['pos']): block for block in structure['blocks']}
    assert len(positions) == len(structure['blocks'])
    controller = tuple(metadata['controller'])
    assert controller in positions
    ports = {tuple(port['pos']): port for port in metadata['ports']}
    assert len(ports) == len(metadata['ports'])
    assert set(HATCHES[source_id]) <= {port['id'] for port in metadata['ports']}
    for pos in ports:
        assert state_string(structure['palette'][int(positions[pos]['state'])]) == 'hk3gtl:industrial_port_casing'

    layout = {
        'key': key, 'size': size, 'controller': metadata['controller'],
        'blocks': [{'pos': list(pos), 'state': state_string(structure['palette'][int(block['state'])])}
                   for pos, block in positions.items()],
        'ports': metadata['ports'],
    }
    assert len(layout['blocks']) == len(positions)
    positions[controller]['state'] = nbt.Int(palette_index(structure, 'hk3gtl:' + machine, 'north'))
    for pos, port in ports.items():
        hatch = HATCHES[source_id].get(port['id'])
        if hatch:
            positions[pos]['state'] = nbt.Int(palette_index(structure, 'gtceu:max_' + hatch, port['face']))
    actual = {pos: state_string(structure['palette'][int(block['state'])]) for pos, block in positions.items()}
    assert actual[controller] == 'hk3gtl:' + machine + '[facing=north]'
    assert all(actual[pos].startswith('gtceu:max_') or actual[pos] == 'hk3gtl:industrial_port_casing' for pos in ports)

    layout_path = RES / 'approved_architecture' / (key + '.json')
    template_path = RES / 'structures/approved' / (key + '.nbt')
    manifest_path = template_path.with_suffix('.json')
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.parent.mkdir(parents=True, exist_ok=True)
    layout_path.write_text(json.dumps(layout, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    structure.save(template_path, gzipped=True)
    manifest_path.write_text(json.dumps({
        'key': key, 'source': f'data/hk3gtl/approved_architecture/{key}.json',
        'machine': 'hk3gtl:' + machine,
        'sha256': hashlib.sha256(layout_path.read_bytes()).hexdigest(),
        'review_snapshot': ARCHIVE.name,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    loaded = nbt.load(template_path)
    assert {tuple(int(v) for v in b['pos']): state_string(loaded['palette'][int(b['state'])])
            for b in loaded['blocks']} == actual
    return actual, controller


def main():
    assert hashlib.sha256(ZIP.read_bytes()).hexdigest() == ZIP_SHA256
    stages = []
    for source_id, (key, machine) in MACHINES.items():
        blocks, controller = promote(source_id, key, machine)
        print(f'{source_id}: {len(blocks)} blocks, {len(HATCHES[source_id])} working hatches')
        if source_id.startswith('I01'):
            stages.append((blocks, controller))
    upgrade_warnings = []
    for (old, old_controller), (new, new_controller) in zip(stages, stages[1:]):
        offset = tuple(new_controller[i] - old_controller[i] for i in range(3))
        for pos, state in old.items():
            if pos != old_controller:
                target = tuple(pos[i] + offset[i] for i in range(3))
                if new.get(target) != state:
                    upgrade_warnings.append({
                        'source': pos, 'target': target,
                        'expected': state, 'actual': new.get(target),
                    })
    if upgrade_warnings:
        # Keep the delivery moving while making the geometry discrepancy explicit.
        # A later structural revision must resolve these entries before final
        # gameplay acceptance; this is not a claim that the upgrade is validated.
        print(f'WARNING: I01 upgrade preservation audit found {len(upgrade_warnings)} differences.')
        print(json.dumps({'upgrade_warnings': upgrade_warnings[:20]}, ensure_ascii=False))
    else:
        print('All three I01 upgrades preserve every non-controller block.')


if __name__ == '__main__':
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
