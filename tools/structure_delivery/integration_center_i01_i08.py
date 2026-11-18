# -*- coding: utf-8 -*-
"""I01四阶及I02–I08的主控宽度轴置中候选；不改写V1或正式资源。

【变更记录 #1】2026-10-23 11:44:30（主控置中融合V2，不增加模组修订号）
- 删除：I03、I05、I06偏置的钻石标记，原位置恢复其原设备表面。
- 新增：中心列核验、必要的内部背壳与逐格差异；保留V1完整修订历史。
- 修改：I03进入固定冷却分析座中央，I05沿塔裙座移一格，I06移到鞍座中心列。
- 用途：输入V1完整蓝图，深拷贝返回V2；接口完整对象、主配色与尺寸保持。

公开函数revise不读写输入文件；命令入口只写专项logs，默认逐台静态核验。
--render另生成草稿等轴与北立面供人工审视；图像不是游戏截图或外观批准。
I01四阶保留原signed控制点和同一粘贴锚，不重新归零或替换前阶材料。
"""
from collections import Counter, deque
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I01-I18_控制器接口融合修订_V1_20261023'
OUTPUT = ROOT / 'logs/controller-centering-rework-20261023'
KEYS = [f'i01-{n}' for n in range(1, 5)] + [f'i{n:02}' for n in range(2, 9)]
CONTROL = 'minecraft:diamond_block'
PLANS = {
    'i03': {'pos': [20, 3, 33], 'host': '固定低位轴承冷却分析座中央北壁',
            'summary': '由偏置飞轮轴承座迁入机器宽度中心列上的既有冷却分析座；分析机壳与顶部散热列保持，仅补内部背壳。'},
    'i05': {'pos': [21, 3, 16], 'host': '再生塔第一段固定下裙座中央北壁',
            'summary': '主控沿原再生塔裙座向右一格，落在整机宽度中心列；塔脚进料与冷凝、回收分区保持。'},
    'i06': {'pos': [27, 2, 17], 'host': '一级滚筒固定承重鞍座中心列北壁',
            'summary': '主控在同一滚筒承重鞍座内由X23移至整机中心X27；沿用完整耐热鞍座表面与内部背壳。'},
}


def now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def revise(data: dict) -> dict:
    """只移动主控标记；中心列若无既有表面或遇接口、前方障碍则拒绝生成。"""
    result = deepcopy(data)
    key = result['key']
    assert key in KEYS, key
    before = {tuple(b['pos']): b['state'] for b in data['blocks']}
    grid = dict(before)
    old = tuple(data['controller'])
    assert grid[old] == CONTROL
    center = (result['size'][0] - 1) // 2
    assert result['size'][0] % 2 == 1
    surfaces = deepcopy(data['integration_revision']['surfaces'])
    surface = next(s for s in surfaces if s['id'] == 'controller')
    plan = PLANS.get(key)
    target = tuple(plan['pos']) if plan else old
    assert target[0] == center
    restored, backing_added = None, []
    if target != old:
        restored = surface['replaced_surface_state']
        assert restored != CONTROL
        assert target in grid and grid[target] not in (CONTROL, 'hk3gtl:industrial_port_casing')
        target_state = grid[target]
        front, back = (target[0], target[1], target[2] - 1), (target[0], target[1], target[2] + 1)
        assert front not in grid
        grid[old] = restored
        grid[target] = CONTROL
        if back not in grid:
            grid[back] = target_state
            backing_added.append({'pos': list(back), 'state': target_state, '用途': '设备内部控制器实背壳'})
        surface.update({'pos': list(target), 'host': plan['host'], 'relation': plan['summary'],
                        'replaced_surface_state': target_state, 'backing': list(back), 'front_air': list(front)})
    summary = plan['summary'] if plan else '原主控已处于整台结构宽度中心列，保留原设备表面及全部接口；仅新增中心核验记录。'
    removed = [list(p) for p in before if p not in grid]
    added = [{'pos': list(p), 'state': s} for p, s in grid.items() if p not in before]
    changed = [{'pos': list(p), 'before': before[p], 'after': s} for p, s in grid.items() if p in before and before[p] != s]
    stamp = now()
    counts = {'before': len(before), 'after': len(grid), 'deleted': len(removed), 'changed': len(changed), 'added': len(added)}
    result['blocks'] = [{'pos': list(p), 'state': s} for p, s in sorted(grid.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))]
    result['name'] = key + '-controller-centered-v2'
    result['controller'] = list(target)
    result['block_count'] = len(grid)
    result['candidate_version'] = '控制器居中融合修订V2（待批准）'
    result['approval_status'] = '未批准、未接入正式资源或游戏实例'
    result['material_usage'] = dict(Counter(grid.values()))
    result['integration_revision_history'] = deepcopy(data.get('integration_revision_history', [])) + [deepcopy(data['integration_revision'])]
    result['integration_revision'] = {'version': 'V2', 'time': stamp, 'status': result['approval_status'],
        'source': '控制器接口融合V1候选', 'principle': summary, 'surfaces': surfaces,
        'deleted_positions': removed, 'changed_positions': changed, 'added_positions': added, 'counts': counts,
        'not_verified': ['新候选外观尚未由负责人批准', '未接入正式控制器、Pattern或真实仓室，未进行游戏与生存验收']}
    result['controller_centering'] = {'version': 'V2', 'recorded_at': stamp, 'summary': summary,
        'policy': '主控X=(sizeX-1)//2；以整台结构宽度为准，不能仅以局部设备中心代替',
        'width': result['size'][0], 'center_x_0based': center, 'center_column_1based': center + 1,
        'old_controller': list(old), 'new_controller': list(target), 'moved': target != old, 'passed': True,
        'host': surface['host'], 'restored_old_surface_state': restored, 'internal_backing_added': backing_added,
        'delta': counts, 'ports_unchanged': result['ports'] == data['ports'],
        'boundary': '几何候选；尚未获新版外观批准，未改正式资源或不可变归档'}
    result.setdefault('candidate_revision', {}).update({'revision': 'controller-centered-v2', 'time': stamp,
        'status': result['approval_status'], 'geometry_source': '控制器接口融合V1候选'})
    notes = result.setdefault('construction_notes', {})
    notes.update({'controller': surface['host'] + '；钻石为位置标记，正面朝北，整机宽度中心列。',
                  'status': result['approval_status'], 'recommended_controller_world_y': -60 + target[1]})
    if key.startswith('i01-'):
        assert result['fixed_signed_controller'] == [0, 3, -3]
        assert list(target) == [result['fixed_signed_controller'][i] + result['coordinate_shift'][i] for i in range(3)]
        assert result['paste_anchor'] == list(target)
        notes['paste_anchor'] = list(target)
        notes['schematic_offset'] = [-v for v in target]
    else:
        # V1顶层残留主控锚与实际零偏移不一致，V2统一为既有本地原点粘贴。
        result['paste_anchor'] = [0, 0, 0]
        notes.update({'paste_anchor': [0, 0, 0], 'schematic_offset': [0, 0, 0]})
    result.setdefault('_change_records', []).append({'record': len(result.get('_change_records', [])) + 1,
        'time': stamp, '删除': '偏置钻石标记恢复原设备材质；无主体拆除',
        '新增': '中心列核验与必要的设备内部背壳', '修改': summary,
        '用途': '生成独立V2候选，V1、接口合同、正式资源和实例保持不变'})
    assert result['ports'] == data['ports']
    assert result['title'] == data['title'] and result['size'] == data['size']
    assert set(grid.values()) <= set(before.values())
    return result


def connected(grid):
    remaining = set(grid)
    queue = deque([remaining.pop()])
    while queue:
        x, y, z = queue.popleft()
        for p in ((x+1, y, z), (x-1, y, z), (x, y+1, z), (x, y-1, z), (x, y, z+1), (x, y, z-1)):
            if p in remaining:
                remaining.remove(p)
                queue.append(p)
    return not remaining


def main():
    from build_integration_revision_20261023 import access, signed, load_payload
    from structure_size_baseline import require
    from review_controller_integration_20261023 import RULES, front_image
    from build_redesign69 import render
    parser = argparse.ArgumentParser(description='仅生成负责的11份置中融合V2候选')
    parser.add_argument('--source-root', type=Path, default=SOURCE)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    save(OUTPUT / 'rules-read-i01-i08.json', {'recorded_at': now(),
        '说明': '接续后已实际完整读取六份当前规则；本时间为读后身份记录，不冒充逐文件阅读起点。',
        'files': [{'path': 'rule/' + n, 'sha256': sha(ROOT / 'rule' / n)} for n in RULES]})
    report, previous = [], None
    for key in KEYS:
        source = args.source_root / key / 'blueprint.json'
        old = json.loads(source.read_text(encoding='utf-8'))
        original = deepcopy(old)
        data = revise(old)
        assert old == original, key + '输入被污染'
        data['controller_centering']['source_blueprint'] = str(source.relative_to(ROOT)).replace('\\', '/')
        data['controller_centering']['source_blueprint_sha256'] = sha(source)
        grid = {tuple(b['pos']): b['state'] for b in data['blocks']}
        reaches, baseline = access(data), require(data)
        assert all(x['front_clear'] and x['backing_solid'] and x['walk_access'] for x in reaches), (key, reaches)
        assert connected(grid), key + '实体出现脱离'
        for path in data.get('paths', []):
            assert not any(all(path['min'][i] <= p[i] <= path['max'][i] for i in range(3)) for p in grid), (key, path)
        inheritance = None
        if key.startswith('i01-'):
            current = signed(data)
            if previous:
                assert all(current.get(p) == s for p, s in previous.items()), key + '四阶继承覆盖'
                inheritance = {'preserved': len(previous), 'added': len(current)-len(previous), 'removed': 0, 'changed': 0}
            previous = current
        target = OUTPUT / key
        save(target / 'candidate.json', data)
        if args.render:
            materials = load_payload(args.source_root / key)['materials']
            render(data, materials, target)
            front_image(data, materials).save(target / '北立面草稿.png')
        report.append({'key': key, 'controller': data['controller'], 'delta': data['controller_centering']['delta'],
            'source_sha256': sha(source), 'candidate_sha256': sha(target / 'candidate.json'),
            'access': reaches, 'size_baseline': baseline, 'single_component': True, 'i01_inheritance': inheritance})
        print(key, 'controller', data['controller'], 'delta', data['controller_centering']['delta'], flush=True)
    save(OUTPUT / 'verification-i01-i08.json', {'recorded_at': now(), 'forms': len(report), 'items': report,
        'status': 'V2独立几何候选；待外观批准，未正式接入或部署'})


if __name__ == '__main__':
    main()
