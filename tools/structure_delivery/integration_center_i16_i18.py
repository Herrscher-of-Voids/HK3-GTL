# -*- coding: utf-8 -*-
"""I16–I18 主控按整台宽度置中；仅输出独立V2候选。

输入为融合修订V1交付蓝图。公开revise深复制输入，恢复旧主控材料，
把钻石标记嵌入中心列既有设备壳面，保留全部接口、尺寸、材料和通道。
复用原融合工具的表面与静态可达检查；main不写V1、正式资源或实例。

【变更记录 #1】2026-10-23 11:43:10（主控置中候选，不增加模组修订号）
- 删除：I18仅为旧主控设置的内部单格背衬；旧标记恢复为原壳面。
- 新增：整台宽度中心列主控、设备内部必要密封背衬及差分/访问检查。
- 修改：主控转入I16床身北端、I17主塔低位外壳、I18热室中轴北墙。
- 用途：落实宽35放第18格的明确要求；保持自然融合，候选尚未批准。
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from integration_i16_i18 import CORE, PORT, _access, _now, _place, _reachable_operations

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I01-I18_控制器接口融合修订_V1_20261023'
OUT = ROOT / 'logs/controller-centering-rework-20261023'
HOSTS = {
    'i16': ([24, 3, 8], '长向隔振基准床身原有北端钢机壳；不占北门步行通道'),
    'i17': ([24, 3, 20], '主精馏塔原有中轴低位耐蚀外壳；不另设主控柱'),
    'i18': ([22, 4, 18], '蓝脊屏蔽热室原有中轴北墙HBV横带；维护接口保持下方原位'),
}
OLD_CONTROLLERS = {'i16': [29, 3, 3], 'i17': [29, 3, 5], 'i18': [29, 3, 7]}
OLD_PATHS = {'入口右门柱主控操作净空', '控制附房门柱主控操作净空', '检测闸室门柱主控操作净空'}


def revise(data: dict) -> dict:
    """保持接口合同和主体，仅在独立深复制中移动主控到宽度中间一格。"""
    result = copy.deepcopy(data)
    key = data.get('key')
    if key not in HOSTS or data['controller'] != OLD_CONTROLLERS[key]:
        raise ValueError('输入不是已核实的I16–I18融合V1蓝图')
    before = {tuple(b['pos']): b['state'] for b in data['blocks']}
    if len(before) != len(data['blocks']):
        raise ValueError('源数据存在重复方块坐标')
    blocks = dict(before)
    old = tuple(data['controller'])
    if blocks.get(old) != CORE:
        raise ValueError('旧主控标记不符')
    prior = copy.deepcopy(data['integration_revision'])
    old_surface = next(s for s in prior['new_surfaces'] if s['id'] == 'controller')
    if old_surface['pos'] != list(old):
        raise ValueError('旧主控的恢复材料记录与位置不符')
    old_material = old_surface['replaced_state']
    blocks[old] = old_material
    removed = []
    if old_surface.get('internal_backing_added'):
        back = (old[0], old[1], old[2] + 1)
        if blocks.get(back) != old_material:
            raise ValueError('旧主控单格背衬已经发生变化，禁止推测删除')
        del blocks[back]
        removed.append({'reason': '撤销仅服务旧主控的单格内部背衬，恢复闸室原空腔',
                        'bounds': {'min': list(back), 'max': list(back)}, 'blocks': 1})
    controller, host = copy.deepcopy(HOSTS[key])
    if data['size'][0] % 2 != 1 or controller[0] != (data['size'][0] - 1) // 2:
        raise ValueError('主控不在整台奇数宽度的中心列')
    surfaces = []
    _place(blocks, controller, CORE, host, 'controller', surfaces)
    result['controller'] = list(controller)
    result['core_marker'] = list(controller)
    result['controller_facing'] = 'north'
    result['name'] = key + '-controller-centered-v2'
    result['candidate_version'] = '控制器居中融合修订V2（待批准）'
    result['approval_status'] = '负责人未批准V1；本V2主控宽度置中候选待审，不接入'
    result['paths'] = [p for p in result.get('paths', []) if p.get('name') not in OLD_PATHS]
    result['paths'].append(_access(controller, '整台宽度中轴主控操作净空'))
    result['zones'] = [z for z in result.get('zones', []) if z.get('kind') != 'control']
    notes = result.setdefault('construction_notes', {})
    notes['controller_marker'] = f'钻石块{controller}为整台宽度中间一格的嵌壳主控标记，朝北；不是正式控制器。'
    notes['controller_host'] = host
    notes['approval'] = '仅授权修订主控位置；新候选待批准，旧版未被本次继续下一步批准，不部署。'
    result['description'] = {
        'i16': 'HDV双门架、恒温厂房与六个原北墙接口保持；主控嵌入整台宽度中心列的长床身北端，不另加面板。',
        'i17': 'QSV阶梯精馏塔群与六个工艺接口保持；主控嵌入整台宽度中心列的主精馏塔低位耐蚀壳面，旧附房门柱恢复。',
        'i18': 'HBV蓝脊热室与17个分布接口保持；主控嵌入整台宽度中心列的热室北墙横带，维护口仍在下方，旧检测闸室门柱恢复。',
    }[key]
    result['blocks'] = [{'pos': list(p), 'state': s} for p, s in sorted(blocks.items())]
    result['block_count'] = len(blocks)
    for path in result['paths']:
        if any(all(path['min'][i] <= p[i] <= path['max'][i] for i in range(3)) for p in blocks):
            raise ValueError('声明通道净空被实体占据：' + path['name'])
    if result['ports'] != data['ports']:
        raise ValueError('接口合同或坐标被改变')
    if {p for p, s in blocks.items() if s == CORE} != {tuple(controller)}:
        raise ValueError('主控标记残留或缺失')
    if {p for p, s in blocks.items() if s == PORT} != {tuple(p['pos']) for p in data['ports']}:
        raise ValueError('接口标记残留或缺失')
    if set(blocks.values()) - set(before.values()):
        raise ValueError('引入V1之外的材料')
    if not all(all(0 <= p[i] < data['size'][i] for i in range(3)) for p in blocks):
        raise ValueError('超出原尺寸')
    operations = _reachable_operations(blocks, data['size'], [('controller', controller)] + [(p['id'], p['pos']) for p in data['ports']])
    changes = {'removed': sum(p not in blocks for p in before), 'added': sum(p not in before for p in blocks),
               'replaced': sum(p in blocks and blocks[p] != s for p, s in before.items())}
    now = _now()
    delta = [{'pos': list(p), 'before': before.get(p, 'minecraft:air'), 'after': blocks.get(p, 'minecraft:air')}
             for p in sorted(set(before) | set(blocks)) if before.get(p) != blocks.get(p)]
    center = {'recorded_at': now, 'width': data['size'][0], 'center_column_1based': controller[0] + 1,
              'center_x_0based': controller[0], 'old_controller': list(old), 'controller': controller,
              'summary': host, 'host': host, 'restored_old_material': old_material,
              'new_surface': surfaces[0], 'removed_ranges': removed, 'changes_from_v1': changes,
              'delta': delta, 'operation_access': operations,
              'checks': {'full_width_centered': True, 'ports_identical': True, 'paths_clear': True,
                         'no_new_external_carrier': True, 'front_clear': True, 'backing_solid': True,
                         'reachable_operation_points_within_3_blocks': True},
              'unverified': ['本版外观审批', '正式控制器与Pattern', '实际仓室能力与配方', '生存研究与游戏内建造']}
    result['controller_centering'] = center
    result.setdefault('integration_revision_history', []).append(prior)
    revision = copy.deepcopy(prior)
    revision.update({'revision': 2, 'created_at': now, 'source_name': data['name'],
                     'source_controller': list(old), 'source_ports': copy.deepcopy(data['ports']),
                     'principle': host, 'removed_ranges': removed, 'operation_access': operations,
                     'actual_changes': changes, 'new_surfaces': [s for s in prior['new_surfaces'] if s['id'] != 'controller'] + surfaces})
    revision['material_counts'] = {s: sum(v == s for v in blocks.values()) for s in set(blocks.values())}
    revision['变更记录'].append({'序号': '#2', '时间': now, '删除': removed, '新增': surfaces,
                                 '修改': delta, '原因': '主控必须处于整台宽度中间一格', '用途': '独立V2候选评审'})
    result['integration_revision'] = revision
    result.setdefault('change_log', []).append({'number': len(result.get('change_log', [])) + 1, 'time': now,
        '删除': removed, '新增': surfaces, '修改': delta, '用途': '主控全宽置中；保留V1与正式资源，不部署'})
    return result


def main() -> None:
    for key in HOSTS:
        source = SOURCE / key / 'blueprint.json'
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        data = json.loads(source.read_text(encoding='utf-8-sig'))
        candidate = revise(data)
        candidate['controller_centering'].update({'source_blueprint': source.relative_to(ROOT).as_posix(), 'source_sha256': digest})
        candidate['integration_revision']['source_blueprint'] = source.relative_to(ROOT).as_posix()
        candidate['integration_revision']['source_sha256'] = digest
        destination = OUT / key / 'candidate.json'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(candidate, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
        if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise ValueError('来源V1身份变化')
        print(json.dumps({'key': key, 'controller': candidate['controller'], 'changes': candidate['controller_centering']['changes_from_v1']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
