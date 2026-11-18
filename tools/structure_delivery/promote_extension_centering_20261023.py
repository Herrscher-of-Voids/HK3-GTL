#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从不可变批准V2归档接入I14–I18正式Pattern与真实仓放置模板。

【变更记录 #1】2026-10-23 13:39:56（内测5修订175）
删除：I17活动模板对旧海渊材料的依赖；不删除或重写任何批准归档。
新增：五台精确资源、控制器替换、四方向真实仓与来源哈希清单。
修改：只允许指定主控和接口位置换为实际机器，其余坐标与状态逐格不变。
用途：正式接入已批准建筑；不新增配方或宣称生存、阶段及实机验收通过。
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import nbtlib as nbt

ROOT = Path(__file__).resolve().parents[2]
MACHINES = {
    'i14': 'soulium_polymerization_die_caster',
    'i15': 'soulium_reconstruction_annealing_furnace',
    'i16': 'soulium_precision_processing_center',
    'i17': 'honkai_fuel_concentration_plant',
    'i18': 'honkai_fuel_rod_encapsulation_array',
}
GROUPS = {
    'i14': 'NANO_GROUP:item_input PRECURSOR:fluid_input POWER:service PRODUCT:item_output TAIL_LIQUID:fluid_output UTILITY:service',
    'i15': 'BILLET:item_input POWER:service ATMOSPHERE:fluid_input THERMAL_LOG:item_output COOLANT:fluid PRODUCT:item_output',
    'i16': 'BILLET:item_input POWER:service COOLANT:fluid_input PRODUCT:item_output DATA:item_output CHIPS:output',
    'i17': 'LIQUID_FUEL:input STABILIZER:input COOLANT:input CONCENTRATE:output RESIDUAL:output POWER:service',
    'i18': 'P01:item_input P02:fluid_input P03:item_input P04:fluid_input P05:fluid_input P06:service P07:service P08:fluid_output P09:item_input P10:item_output P11:item_output P12:item_output P13:fluid_output P14:fluid_output P15:item_output P16:item P17:item',
}
# 四项能力必须安装在不同接口；四槽流体仓承载既有I17三种输入和三种输出。
PLACED = {
    'i14': {'NANO_GROUP': 'item_input', 'PRECURSOR': 'fluid_input', 'PRODUCT': 'item_output', 'TAIL_LIQUID': 'fluid_output'},
    'i15': {'BILLET': 'item_input', 'ATMOSPHERE': 'fluid_input', 'PRODUCT': 'item_output', 'COOLANT': 'fluid_output'},
    'i16': {'BILLET': 'item_input', 'COOLANT': 'fluid_input', 'PRODUCT': 'item_output', 'CHIPS': 'fluid_output'},
    'i17': {'LIQUID_FUEL': 'fluid_input', 'STABILIZER': 'item_input', 'CONCENTRATE': 'fluid_output', 'RESIDUAL': 'item_output'},
    'i18': {'P01': 'item_input', 'P02': 'fluid_input', 'P10': 'item_output', 'P13': 'fluid_output'},
}
HATCHES = {'item_input': 'gtceu:max_input_bus', 'item_output': 'gtceu:max_output_bus',
           'fluid_input': 'gtceu:max_input_hatch_4x', 'fluid_output': 'gtceu:max_output_hatch_4x'}
ABILITIES = {'item_input': {'item_input'}, 'item_output': {'item_output'},
             'fluid_input': {'fluid_input'}, 'fluid_output': {'fluid_output'},
             'item': {'item_input', 'item_output'}, 'fluid': {'fluid_input', 'fluid_output'},
             'input': {'item_input', 'fluid_input'}, 'output': {'item_output', 'fluid_output'}, 'service': set()}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def state_text(state):
    text = str(state['Name'])
    if state.get('Properties'):
        text += '[' + ','.join(f'{k}={v}' for k, v in sorted(state['Properties'].items())) + ']'
    return text


def promote(source_root, key, approval, timestamp):
    path = source_root / key / 'blueprint.json'
    original = json.loads(path.read_text(encoding='utf-8'))
    cells = {tuple(b['pos']): b['state'] for b in original['blocks']}
    control = tuple(original['controller'])
    assert len(cells) == len(original['blocks']) and cells[control] == 'minecraft:diamond_block'
    assert control[0] == (original['size'][0] - 1) // 2
    groups = dict(part.split(':', 1) for part in GROUPS[key].split())
    assert set(groups) == {p['id'] for p in original['ports']}
    assert len(original['ports']) == (17 if key == 'i18' else 6)
    for port in original['ports']:
        assert port['face'] == 'north' and cells[tuple(port['pos'])] == 'hk3gtl:industrial_port_casing'
    placed = PLACED[key]
    assert set(placed.values()) == set(HATCHES)
    assert all(ability in ABILITIES[groups[port]] for port, ability in placed.items())
    approved_nbt = next(path.parent.glob('*.nbt'))
    structure = nbt.load(approved_nbt)
    positions = {tuple(map(int, b['pos'])): b for b in structure['blocks']}
    assert {p: state_text(structure['palette'][int(b['state'])]) for p, b in positions.items()} == cells
    assert list(map(int, structure['size'])) == original['size']
    machine = 'hk3gtl:' + MACHINES[key]
    record = {'record': 1, 'time': timestamp, 'revision': 175,
              'reason': '负责人明确批准主控置中融合V2并要求实装',
              'deleted': 'I17旧海渊布局正式引用；批准归档无改动',
              'added': '五台正式入口、精确几何、真实仓模板和批准来源身份',
              'modified': '仅指定主控替换；模板仅另换声明接口为真实仓',
              'purpose': '保持批准造型；配方开放、生存获取和实机成型另行验收'}
    resource = {
        'key': key, 'title': original['title'], 'size': original['size'], 'controller': list(control),
        'ports': [{**p, 'group': groups[p['id']]} for p in original['ports']],
        'blocks': [{'pos': b['pos'], 'state': machine if tuple(b['pos']) == control else b['state']}
                   for b in original['blocks']],
        'approved_source': {'version': '主控居中融合V2已批准', 'blueprint': relative(path),
                            'sha256': sha(path), 'approval': '实装这一些吧',
                            'approval_manifest': relative(approval), 'approval_manifest_sha256': sha(approval)},
        'controller_centering': original.get('controller_centering', {}),
        'runtime_contract': {'controller': machine, 'required_abilities': sorted(HATCHES),
                             'energy': 'bound_player_wireless_eu', 'empty_port_filler': 'hk3gtl:industrial_port_casing',
                             'geometry_changes': '仅指定钻石主控替换，其他全部批准状态保留',
                             'recipe_policy': 'I17保持既有正式浓缩工艺；I14/I15/I16/I18不执行暂定计划',
                             'survival_verified': False, 'game_verified': False},
        '_change_records': [record]}
    if key == 'i16':
        resource['runtime_contract']['first_build_requirement'] = 'HDV最迟可建；获取链与研究仍未实机验收，不以注册MAX推定额定'
    if key in {'i14', 'i15'}:
        resource['runtime_contract']['voltage_mapping'] = '历史映射缺口保留；按批准几何接入，未据外观编造额定或重配色'
    if resource['controller_centering']:
        resource['controller_centering']['source_status'] = '外部确认清单已批准，原候选状态为来源历史'
    target = ROOT / f'src/main/resources/data/hk3gtl/approved_architecture/{key}.json'
    target.write_text(json.dumps(resource, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

    def index(name, facing='north'):
        state = nbt.Compound({'Name': nbt.String(name), 'Properties': nbt.Compound({'facing': nbt.String(facing)})})
        for i, existing in enumerate(structure['palette']):
            if existing == state:
                return i
        structure['palette'].append(state)
        return len(structure['palette']) - 1

    positions[control]['state'] = nbt.Int(index(machine))
    for port in resource['ports']:
        if port['id'] in placed:
            positions[tuple(port['pos'])]['state'] = nbt.Int(index(HATCHES[placed[port['id']]], port['face']))
    actual = {p: state_text(structure['palette'][int(b['state'])]) for p, b in positions.items()}
    allowed = {control} | {tuple(p['pos']) for p in original['ports']}
    assert all(actual[p] == state for p, state in cells.items() if p not in allowed)
    template = ROOT / f'src/main/resources/data/hk3gtl/structures/approved/{key}.nbt'
    structure.save(template, gzipped=True)
    decoded = nbt.load(template)
    assert {tuple(map(int, b['pos'])): state_text(decoded['palette'][int(b['state'])]) for b in decoded['blocks']} == actual
    manifest = {'key': key, 'source': f'data/hk3gtl/approved_architecture/{key}.json', 'machine': machine,
                'sha256': sha(target), 'template_sha256': sha(template), 'approved_blueprint_sha256': sha(path),
                'approved_nbt_sha256': sha(approved_nbt), 'review_snapshot': relative(source_root.parent),
                'approval_manifest': relative(approval), 'approval_manifest_sha256': sha(approval),
                'controller': list(control), 'size_xyz': original['size'], 'blocks': len(actual),
                'required_abilities': sorted(HATCHES), 'installed_hatches': placed,
                'installed_hatch_blocks': {port: HATCHES[ability] for port, ability in placed.items()},
                'geometry_changes': '仅指定主控与接口替换，全部其他批准方块无变化',
                'game_verified': False, '_change_records': [record]}
    template.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return {**manifest, 'formal_resource': relative(target), 'template': relative(template),
            'non_controller_resource_changes': 0, 'non_port_template_changes': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    source_root = args.archive.resolve()
    approval = source_root.parent / '确认与校验清单.json'
    assert approval.is_file()
    timestamp = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    before = {relative(p): sha(p) for p in source_root.rglob('*') if p.is_file()}
    rows = [promote(source_root, key, approval, timestamp) for key in MACHINES]
    assert before == {relative(p): sha(p) for p in source_root.rglob('*') if p.is_file()}
    output = ROOT / 'logs/controller-centering-install-20261023/extension-promotion.json'
    output.write_text(json.dumps({'recorded_at': timestamp, 'revision': 175, 'structures': rows,
                                 'archive_unchanged': True, 'game_verified': False}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps([{'key': r['key'], 'size_xyz': r['size_xyz'], 'blocks': r['blocks']} for r in rows]))


if __name__ == '__main__':
    main()
