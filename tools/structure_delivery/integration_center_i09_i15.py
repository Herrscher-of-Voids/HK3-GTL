# -*- coding: utf-8 -*-
"""I09–I15 主控沿整台宽度中心线的独立 V2 候选。

【文件职责】只读 V1 蓝图，返回深拷贝；恢复旧主控壳材，复用实际设备端面。
输入为融合 V1，输出为专项 candidate.json；总导出器负责结构文件和最终交付。
【变更记录 #1】2026-10-23 11:42:06（主控置中候选，不增加模组修订号）
- 删除：偏置主控钻石标记，恢复为原设备材质；不拆主体和既有接口。
- 新增：整机中心列、设备嵌入依据、逐格差异和可达性检查。
- 修改：I09/I10 嵌既有整体承重基座，I11 嵌校准转台，I15 嵌南炉北墙；
  I12/I13/I14 原位保留。I10 只补贴地检修格栅，不添加主控箱、面板或立柱。
- 用途：落实负责人宽35用第18格的要求；V1、批准归档、正式资源和游戏不改。
边界：接口完整列表不变，不重配色；失败立即停止，静态核查不代表实机验收。
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

from build_integration_revision_20261023 import access
from structure_size_baseline import require

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I01-I18_控制器接口融合修订_V1_20261023'
OUT = ROOT / 'logs/controller-centering-rework-20261023'
DIAMOND = 'minecraft:diamond_block'
PORT = 'hk3gtl:industrial_port_casing'
GRATE = 'gtceu:assembly_line_grating'

PLANS = {
    'i09': {
        'pos': [21, 1, 11],
        'surface': '釜前整块承重锚座朝北端面',
        'summary': '主控移到整机第22列，直接嵌入梨形釜既有前承重锚座端面。',
        'basis': '该锚座为既有宽幅两层承重基础，向后承接前釜腿；主控替换原基础壳面，背后仍为连续实壳，不新增低台、面板或托柱。',
    },
    'i10': {
        'pos': [25, 1, 20],
        'surface': '共轴反应管既有贯通承重梁北端面',
        'summary': '主控移到整机第26列，嵌入共轴设备现有贯通承重梁。',
        'basis': '所选壳面属于横贯各共振环的原有长承重梁，而非新增控制柜；只以贴地格栅接通原前侧检修长廊，梁宽、梁高与共轴设备均保留。',
    },
    'i11': {
        'pos': [27, 3, 29],
        'surface': '后方精密校准转台的固定驱动壳北面',
        'summary': '主控沿开放中央入口落在整机第28列，嵌入原校准转台驱动壳。',
        'basis': '操作点位于U形送料轨内部的真实校准工位，中央入口仍贯通；替换原功率壳一个方块，周围和背后均是原转台设备，不增加挡路设施。',
    },
    'i12': {
        'pos': [22, 3, 18],
        'surface': '分面编程晶舱既有八角基座北面',
        'summary': '原主控已在整机第23列，保留晶舱八角基座嵌入位置。',
        'basis': '原钻石标记已嵌于编程晶舱自身的低位八角基座，具有实体背壳和原检修路径；本轮不改任何方块。',
    },
    'i13': {
        'pos': [26, 3, 8],
        'surface': '纵向载具床既有固定驱动端面',
        'summary': '原主控已在整机第27列，保留载具床固定驱动端面。',
        'basis': '原钻石标记在纵向载具床低位驱动壳的几何中心，原内衬厚度和前场维护入口保留；本轮不改任何方块。',
    },
    'i14': {
        'pos': [23, 3, 8],
        'surface': '前送料滚床既有低位驱动壳北面',
        'summary': '原主控已在整机第24列，保留滚床内部的低位驱动壳。',
        'basis': '控制器与送料床和压铸工位共轴，位于V1已补全的真实驱动腔端面；本轮不增删实体，也不扩展历史电压映射问题。',
    },
    'i15': {
        'pos': [28, 5, 35],
        'surface': '南侧喷射冷却钟罩既有炉座北墙',
        'summary': '主控从西北炉座移到整机第29列，嵌入南侧冷却钟罩北墙。',
        'basis': '采用本来就在整机中心线的冷却炉座，标记与既有六个炉墙接口同高，面对回转装料庭且背后为原炉墙；原西北炉座恢复不锈钢壳，不新建面板和控制附房。',
    },
}


def now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')


def _inside(p, path):
    return all(path['min'][i] <= p[i] <= path['max'][i] for i in range(3))


def revise(data: dict) -> dict:
    """保留接口合同和设备材料；中心、净空、背壳、路径有任一失败即拒绝。"""
    result = deepcopy(data)
    key = result['key'].lower()
    if key not in PLANS:
        raise ValueError('不属于本模块处理范围：' + key)
    plan = PLANS[key]
    old = list(result['controller'])
    target = plan['pos'][:]
    center = (result['size'][0] - 1) // 2
    assert result['size'][0] % 2 == 1 and target[0] == center, '主控必须使用整机中间一列'
    before = {tuple(row['pos']): row['state'] for row in result['blocks']}
    cells = dict(before)
    assert len(cells) == len(result['blocks']), '输入存在重复坐标'
    assert cells[tuple(old)] == DIAMOND, '输入主控标记不对应蓝图'
    restored = None
    replaced = None
    added = []
    if old != target:
        record = next(row for row in result['integration_revision']['embedded_surfaces']
                      if row['kind'] == '主控' and row['pos'] == old)
        restored = record['replaced_state']
        cells[tuple(old)] = restored
        replaced = cells.get(tuple(target))
        assert replaced and replaced not in (DIAMOND, PORT), '中心落点必须是既有设备实体'
        cells[tuple(target)] = DIAMOND
    if key == 'i10':
        # 只连接原前廊与承重梁之间的地坪空隙；不抬高为新的接口载体。
        for x in range(24, 27):
            for z in range(12, 20):
                p = (x, 0, z)
                if p not in cells:
                    cells[p] = GRATE
                    added.append(list(p))
        result.setdefault('paths', []).append({
            'name': '共轴承重梁中心操作位的贴地检修连接',
            'support_min': [24, 0, 12], 'support_max': [26, 0, 19],
            'min': [24, 1, 12], 'max': [26, 2, 19],
        })
    result['controller'] = target
    result['controller_face'] = 'north'
    for field in ('core_marker', 'paste_anchor'):
        if result.get(field) == old:
            result[field] = target[:]
    result.setdefault('construction_notes', {})['recommended_controller_world_y'] = -60 + target[1]
    result['name'] = key + '-controller-centered-v2'
    result['candidate_version'] = '控制器居中融合修订V2（待批准）'
    result['approval_status'] = '主控宽度轴置中候选；尚待外观批准'
    result['blocks'] = [{'pos': list(p), 'state': s} for p, s in sorted(cells.items())]
    result['block_count'] = len(cells)
    assert result['ports'] == data['ports'], '接口列表必须完整不变'
    assert len({p['id'] for p in result['ports']}) == len(result['ports']), '接口ID重复'
    expected_cores = {p for p, s in before.items() if s == DIAMOND} - {tuple(old)}
    expected_cores.add(tuple(target))
    assert {p for p, s in cells.items() if s == DIAMOND} == expected_cores, '主控或原工艺核心标记变化'
    assert {p for p, s in cells.items() if s == PORT} == {tuple(p['pos']) for p in result['ports']}, '接口标记不一致'
    assert set(cells.values()) <= set(before.values()), '不得增加普通材料'
    for path in result.get('paths', []):
        assert not any(_inside(p, path) for p in cells), '声明净空存在实体：' + path['name']
    checks = access(result)
    assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in checks), checks
    baseline = require(result)
    changes = [{'pos': list(p), 'before': before.get(p), 'after': cells.get(p)}
               for p in sorted(set(before) | set(cells)) if before.get(p) != cells.get(p)]
    result['controller_centering'] = {
        'recorded_at': now(), 'version': 2, 'summary': plan['summary'],
        'equipment_surface': plan['surface'], 'equipment_integration_basis': plan['basis'],
        'width': result['size'][0], 'center_column_1based': center + 1, 'center_x_0based': center,
        'old_controller': old, 'controller': target, 'moved': old != target,
        'old_position_restored_state': restored, 'new_position_replaced_state': replaced,
        'maintenance_floor_added_cells': added,
        'delta': {'removed': sum(p not in cells for p in before),
                  'added': sum(p not in before for p in cells),
                  'replaced': sum(p in before and before[p] != s for p, s in cells.items())},
        'changed_cells': changes, 'ports_exactly_unchanged': True,
        'existing_internal_core_markers_preserved': [list(p) for p in sorted(expected_cores - {tuple(target)})],
        'size_baseline': baseline, 'access': checks, 'paths_have_no_solid_cells': True,
        'materials': '只复用本机V1材料；不改主体机壳、电压配色或I14/I15历史映射。',
        'status': '独立V2候选；未批准、未正式接入、未部署和未实机验收',
        'visual_review': '由专项视审记录逐台审视，静态核查不代替建筑外观批准。',
    }
    return result


def main():
    """生成七份独立候选；记录实际规则身份和输入身份，不写V1。"""
    rules = [{'path': p.relative_to(ROOT).as_posix(),
              'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
              'lines': len(p.read_text(encoding='utf-8').splitlines()), 'read_complete': True}
             for p in sorted((ROOT / 'rule').iterdir()) if p.is_file()]
    for key in PLANS:
        source = SOURCE / key / 'blueprint.json'
        raw = source.read_bytes()
        value = revise(json.loads(raw.decode('utf-8-sig')))
        value['controller_centering'].update({
            'source_blueprint': source.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(raw).hexdigest(), 'rule_read_record': rules,
        })
        dest = OUT / key / 'candidate.json'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(key, value['controller'], value['controller_centering']['delta'])


if __name__ == '__main__':
    main()
