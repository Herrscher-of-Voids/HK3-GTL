# -*- coding: utf-8 -*-
"""将已确认的五阶院区快照接入正式资源；只替换主控，不改建筑和接口外观。

【变更记录 #1】2026-10-15 01:06:24（内测5修订156）
删除：无；不删除或改写批准快照与旧交付。
新增：批准ZIP/逐格源哈希固定检查、正式院区JSON及真实主控NBT导出、四次继承回读。
修改：仅钻石主控成为对应研究控制器，六个工业接口壳和全部普通建筑状态保持原样。
用途：为GT研究Pattern与游戏放置共享确认资源；输出限正式资源与任务日志，不写玩家存档。
"""
import collections
import gzip
import hashlib
import io
import json
from pathlib import Path

import nbtlib as nbt

from structure_size_baseline import require

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT/'deliveries/多方块确认归档/20261015_005918_795325_batch-05_S01-S05_V1'
SOURCE = SNAPSHOT/'confirmed_v1'
BUNDLE = SNAPSHOT.with_suffix('.zip')
BUNDLE_SHA256 = 'd814bf03ec7fbc1f1e4177a2828052308021afba9f06f7c373a1e49793660962'
RESOURCES = ROOT/'src/main/resources/data/hk3gtl'
LOG = ROOT/'logs/research-campus-formal-20261015'
MACHINES = {
    's01': 'abyss_research_analysis_matrix',
    's02': 's02_matter_reconstruction_institute',
    's03': 's03_quantum_domain_institute',
    's04': 's04_world_maintenance_institute',
    's05': 's05_civilization_cognition_dome',
}
PORT = 'hk3gtl:industrial_port_casing'
DIAMOND = 'minecraft:diamond_block'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def states(structure):
    palette = []
    for state in structure['palette']:
        name = str(state['Name'])
        props = state.get('Properties', {})
        if props:
            name += '['+','.join(f'{k}={v}' for k, v in sorted(props.items()))+']'
        palette.append(name)
    result = {tuple(map(int, q['pos'])): palette[int(q['state'])] for q in structure['blocks']}
    assert len(result) == len(structure['blocks']), 'NBT包含重复坐标'
    return result


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


def promote(key, machine, manifest):
    folder = SOURCE/key
    blueprint_path = folder/'blueprint.json'
    blueprint = json.loads(blueprint_path.read_text(encoding='utf-8'))
    record = manifest[key.upper()]
    source_nbt = folder/record['nbt']
    source_schem = folder/record['schem']
    assert digest(source_nbt) == record['nbt_sha256']
    assert digest(source_schem) == record['schem_sha256']
    assert digest(blueprint_path) == json.loads((SNAPSHOT/'确认与校验清单.json').read_text(
        encoding='utf-8'))['source_sha256'][key+'/blueprint.json']
    before = {p: digest(p) for p in (source_nbt, source_schem, blueprint_path)}
    original = nbt.load(source_nbt)
    approved = states(original)
    assert approved == {tuple(q['pos']): q['state'] for q in blueprint['blocks']}
    baseline = require(blueprint)
    controller = tuple(blueprint['controller'])
    ports = blueprint['ports']
    assert approved[controller] == DIAMOND
    assert sum(s == DIAMOND for s in approved.values()) == 1
    assert len(ports) == sum(s == PORT for s in approved.values()) == 6
    assert all(approved[tuple(p['pos'])] == PORT for p in ports)

    # 正式资源保留六格工业接口外观，不增设与玩家背包付款、电网扣电相冲突的仓室。
    formal_ports = [dict(p, group='研究所可选崩坏能接口',
        purpose='工业接口壳可封回；可选崩坏能部件。研究材料仍从玩家背包付款，EU仍由玩家电网扣除。')
        for p in ports]
    layout = {'key': key, 'size': blueprint['size'], 'controller': list(controller),
              '_change_record': '第1次备注；2026-10-15 01:06:24；内测5修订156；由批准院区生成；仅正式控制器替换，建筑与接口完整保留。',
              'blocks': blueprint['blocks'], 'ports': formal_ports,
              'paths': blueprint['paths'], 'zones': blueprint['zones'],
              'paste_anchor': blueprint['paste_anchor'],
              'upgrade_contract': blueprint['upgrade_contract'],
              'approved_snapshot': str(SNAPSHOT.relative_to(ROOT)).replace('\\', '/'),
              'source_nbt_sha256': record['nbt_sha256'],
              'source_blueprint_sha256': digest(blueprint_path)}
    layout_path = RESOURCES/'approved_architecture'/(key+'.json')
    write_json(layout_path, layout)
    controller_state = nbt.Compound({'Name': nbt.String('hk3gtl:'+machine),
        'Properties': nbt.Compound({'facing': nbt.String('north')})})
    original['palette'].append(controller_state)
    controller_index = len(original['palette'])-1
    for q in original['blocks']:
        if tuple(map(int, q['pos'])) == controller:
            q['state'] = nbt.Int(controller_index)
    output = RESOURCES/'structures/approved'/(key+'.nbt')
    output.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    original.write(buffer)
    output.write_bytes(gzip.compress(buffer.getvalue(), compresslevel=9, mtime=0))
    actual = states(nbt.load(output))
    assert actual[controller] == 'hk3gtl:'+machine+'[facing=north]'
    assert set(actual) == set(approved)
    assert all(actual[p] == state for p, state in approved.items() if p != controller)
    assert before == {p: digest(p) for p in before}, '批准快照被改动'
    metadata = {'key': key, 'machine': 'hk3gtl:'+machine, 'size': blueprint['size'],
                'controller': list(controller), 'paste_anchor': list(controller),
                'source': str(layout_path.relative_to(ROOT)).replace('\\', '/'),
                'sha256': digest(layout_path), 'template_sha256': digest(output),
                'review_snapshot': SNAPSHOT.name, 'approved_bundle_sha256': BUNDLE_SHA256,
                'source_nbt_sha256': record['nbt_sha256'],
                'required_ability_counts': {}, 'optional_abilities':
                ['honkai_energy_input', 'wireless_honkai_input'],
                'material_payment': '玩家背包和既有研究账本',
                'eu_payment': '绑定玩家或FTB队伍无线电网',
                'template_ports': '六个工业接口壳；默认没有实际仓室，不改变研究支付逻辑',
                'formal_geometry_installed': True, 'game_verified': False}
    write_json(output.with_suffix('.json'), metadata)
    return {'key': key, 'blocks': len(actual), 'changed_controller_only': True,
            'source_unchanged': True, 'size_baseline': baseline,
            'namespace_counts': dict(collections.Counter(s.split(':')[0] for s in approved.values()
                if s not in (DIAMOND, PORT))), 'controller': list(controller),
            'layout_sha256': digest(layout_path), 'template_sha256': digest(output)}, actual, controller


def main():
    assert digest(BUNDLE) == BUNDLE_SHA256, '批准归档ZIP哈希变化'
    manifest = json.loads((SNAPSHOT/'确认与校验清单.json').read_text(encoding='utf-8'))
    records = {entry['id']: entry for entry in manifest['entries']}
    assert manifest['batch'] == 'batch-05' and set(records) == {key.upper() for key in MACHINES}
    results, upgrades, previous = [], [], None
    for key, machine in MACHINES.items():
        result, placed, controller = promote(key, machine, records)
        relative = {tuple(p[i]-controller[i] for i in range(3)): state for p, state in placed.items()}
        if previous:
            changes = [p for p, state in previous.items() if p != (0, 0, 0) and relative.get(p) != state]
            assert not changes, (key, '升级改变旧建筑', changes[:5])
            upgrades.append({'to': key, 'preserved_non_controller': len(previous)-1,
                             'removed_or_changed': 0, 'anchor_stable': True})
        previous = relative
        results.append(result)
        print(f'{key}: {len(placed):,}方块；仅替换真实控制器；六接口和建筑保持原样', flush=True)
    LOG.mkdir(parents=True, exist_ok=True)
    write_json(LOG/'promotion-verification.json', {'passed': True, 'approved_snapshot': str(SNAPSHOT),
        'approved_bundle_sha256': BUNDLE_SHA256, 'research': results, 'upgrades': upgrades,
        'java_compile_verified': False, 'game_verified': False})


if __name__ == '__main__':
    main()
