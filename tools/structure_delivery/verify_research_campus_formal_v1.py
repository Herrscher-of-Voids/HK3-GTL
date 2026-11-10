# -*- coding: utf-8 -*-
"""只读验证批准院区、正式资源与五阶注册；只将验证报告写入任务日志。

【变更记录 #1】2026-10-15 01:06:24（内测5修订156）
删除：无。新增：独立NBT/JSON比对、接口和继承检查、注册与研究支付模型检查。
修改：验收以批准归档为基准，除真实主控替换外禁止改变任何普通方块或六接口。
用途：供构建部署前核对正式资源；通过不代表Minecraft游戏成型、运行或性能实測。
"""
import collections
import hashlib
import json
from pathlib import Path

import nbtlib

from structure_size_baseline import require

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT/'deliveries/多方块确认归档/20261015_005918_795325_batch-05_S01-S05_V1'
RESOURCE = ROOT/'src/main/resources/data/hk3gtl'
JAVA = ROOT/'src/main/java/com/sirin/hk3gtl'
LOG = ROOT/'logs/research-campus-formal-20261015'
IDS = {'s01': 'abyss_research_analysis_matrix',
       's02': 's02_matter_reconstruction_institute',
       's03': 's03_quantum_domain_institute',
       's04': 's04_world_maintenance_institute',
       's05': 's05_civilization_cognition_dome'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_nbt(path):
    root = nbtlib.load(path)
    assert int(root['DataVersion']) == 3465 and not root['entities']
    palette = []
    for entry in root['palette']:
        properties = tuple(sorted((str(k), str(v)) for k, v in entry.get('Properties', {}).items()))
        palette.append((str(entry['Name']), properties))
    result = {tuple(map(int, b['pos'])): palette[int(b['state'])] for b in root['blocks']}
    assert len(result) == len(root['blocks']), 'NBT坐标重复'
    return list(map(int, root['size'])), result


def main():
    manifest = json.loads((SNAPSHOT/'确认与校验清单.json').read_text(encoding='utf-8'))
    rows = {entry['id'].lower(): entry for entry in manifest['entries']}
    previous, summaries = None, []
    for key, machine in IDS.items():
        folder = SNAPSHOT/'confirmed_v1'/key
        record = rows[key]
        source_path = folder/record['nbt']
        assert sha(source_path) == record['nbt_sha256']
        source_size, original = read_nbt(source_path)
        formal_size, placed = read_nbt(RESOURCE/'structures/approved'/(key+'.nbt'))
        blueprint = json.loads((folder/'blueprint.json').read_text(encoding='utf-8'))
        layout = json.loads((RESOURCE/'approved_architecture'/(key+'.json')).read_text(encoding='utf-8'))
        metadata = json.loads((RESOURCE/'structures/approved'/(key+'.json')).read_text(encoding='utf-8'))
        assert source_size == formal_size == blueprint['size'] == layout['size']
        controller = tuple(record['controller'])
        assert controller == tuple(blueprint['controller']) == tuple(layout['controller'])
        assert original[controller] == ('minecraft:diamond_block', ())
        assert placed[controller] == ('hk3gtl:'+machine, (('facing', 'north'),))
        assert set(placed) == set(original)
        assert all(placed[p] == state for p, state in original.items() if p != controller)
        assert blueprint['blocks'] == layout['blocks']
        assert blueprint['paths'] == layout['paths'] and blueprint['zones'] == layout['zones']
        assert metadata['sha256'] == sha(RESOURCE/'approved_architecture'/(key+'.json'))
        assert metadata['template_sha256'] == sha(RESOURCE/'structures/approved'/(key+'.nbt'))
        assert metadata['machine'] == 'hk3gtl:'+machine and metadata['required_ability_counts'] == {}
        baseline = require(blueprint)
        assert baseline['actual_xyz'] == formal_size and baseline['min_pos'] == [0, 0, 0]
        ports = blueprint['ports']
        assert len(ports) == len(layout['ports']) == 6
        cx, cy, cz = controller
        assert all(placed[cx+dx, cy+dy, cz] == ('gtceu:clean_machine_casing', ())
            for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)
        for port, formal_port in zip(ports, layout['ports']):
            assert all(formal_port[field] == port[field] for field in ('id', 'pos', 'face'))
            x, y, z = port['pos']
            assert placed[x, y, z] == ('hk3gtl:industrial_port_casing', ())
            assert (x, y, z-1) not in placed and (x, y, z+1) in placed and (x, y-1, z) in placed
        protected = set()
        for path in blueprint['paths']:
            lo, hi = path['min'], path['max']
            assert hi[1]-lo[1]+1 >= 2
            for x in range(lo[0], hi[0]+1):
                for z in range(lo[2], hi[2]+1):
                    assert (x, lo[1]-1, z) in placed, '维护通道地板缺失'
                    for y in range(lo[1], hi[1]+1):
                        assert (x, y, z) not in placed, '维护通道被占用'
                        protected.add((x, y, z))
        relative = {tuple(p[i]-controller[i] for i in range(3)): state for p, state in placed.items()}
        removed = 0 if previous is None else sum(relative.get(p) != state
            for p, state in previous.items() if p != (0, 0, 0))
        assert removed == 0, '正式升级改变既有建筑'
        size = blueprint['size']
        volume = size[0]*size[1]*size[2]
        summaries.append({'key': key, 'machine': machine, 'blocks': len(placed), 'size_xyz': size,
            'strict_pattern_cells': volume, 'strict_air_cells': volume-len(placed),
            'path_air_cells': len(protected), 'inherited_non_controller': len(previous)-1 if previous else 0,
            'removed_or_changed': removed, 'controller_only_replacement': True, 'ports_unchanged': 6,
            'states_explicit_properties_in_source': sum(bool(state[1]) for state in original.values()),
            'ordinary_namespace_counts': dict(collections.Counter(state[0].split(':')[0]
                for p, state in original.items() if p != controller and state[0] != 'hk3gtl:industrial_port_casing')),
            'baseline': baseline['passed'], 'source_nbt_sha256': sha(source_path),
            'formal_template_sha256': metadata['template_sha256']})
        previous = relative

    registration = (JAVA/'common/machine/research/Hk3ResearchMachines.java').read_text(encoding='utf-8')
    common_registration = (JAVA/'common/machine/Hk3MachinesImpl.java').read_text(encoding='utf-8')
    assert all(f'"{machine}"' in registration for key, machine in IDS.items() if key != 's01')
    assert 'new Hk3ResearchInstituteMachine(holder, lab)' in registration
    assert 'Hk3ResearchMachines.initInstitutes(ABYSS_RESEARCH_ANALYSIS_MATRIX)' in common_registration
    pattern = (JAVA/'common/multiblock/pattern/Hk3ResearchInstitutePatterns.java').read_text(encoding='utf-8')
    assert 'FactoryBlockPattern.start(RIGHT, UP, BACK)' in pattern and "where('#', Predicates.air())" in pattern
    assert 'HONKAI_ENERGY_INPUT' in pattern and 'WIRELESS_HONKAI_INPUT' in pattern
    assert 'setMinGlobalLimited' not in pattern
    assert not any(f'PartAbility.{ability}' in pattern for ability in
        ('IMPORT_ITEMS', 'EXPORT_ITEMS', 'IMPORT_FLUIDS', 'EXPORT_FLUIDS', 'INPUT_ENERGY', 'PARALLEL_HATCH'))
    research = (JAVA/'common/machine/research/Hk3ResearchInstituteMachine.java').read_text(encoding='utf-8')
    assert 'getEnergyContainer()' in research and 'Hk3ResearchStartService.start' in research
    assert 'Hk3ResearchExecutionContracts' in research
    result = {'passed': True, 'research': summaries, 'source': str(SNAPSHOT),
        'research_payment_model': '沿用玩家背包付款、绑定玩家电网EU和既有研究授权',
        'required_ability_counts': {}, 'game_formation_verified': False, 'game_execution_verified': False,
        'game_performance_verified': False,
        'performance_note': 'S05常规GT严格空气Pattern扫描1747305格；使用资源加载避免Java64K常量，实际游戏耗时和内存待验。'}
    LOG.mkdir(parents=True, exist_ok=True)
    target = LOG/'independent-formal-verification.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'passed': True, 'machines': len(summaries), 'report': str(target)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
