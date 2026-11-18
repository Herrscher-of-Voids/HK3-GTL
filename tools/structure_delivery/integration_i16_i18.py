# -*- coding: utf-8 -*-
"""I16–I18 控制器与接口融合修订：只输出独立候选，不写正式结构。

职责：接收既有 blueprint 字典，以原主体的门柱、设备前脸、储槽端壁及
工艺附房外墙承载标记。公开 revise 返回深复制，保持名称、电压、尺寸和
接口身份；main 从专项审查 sources.json 读取三个原件，仅写日志候选。
边界：不注册方块、配方、控制器或 Pattern；钻石块和接口块均为预览标记。
调用：主任务的统一导出器调用 revise，再统一制作 NBT、Schematic 与材质预览。

【变更记录 #1】2026-10-23 10:56:30（融合修订候选，不增加模组修订号）
- 删除：I16 雨棚顶旧主控；I17 六根接口小柱及独立主控架；I18 集中白框、背箱和专用连梁。
- 新增：按工艺分配的嵌入式表面标记、访问净空、来源身份和规则读取记录。
- 修改：仅调整独立候选中的控制器/接口坐标及相关说明，不覆盖任何原件或批准状态。
- 用途：落实负责人已授权的结构修改，防止用同色、底板连通代替真实融合。

【变更记录 #2】2026-10-23 11:00:16（既有空腔设备的接口密封背衬）
- 删除：无。
- 新增：单层罐壁和闸室墙在标记背面向设备内部加厚一格，材料沿用该处原壳体。
- 修改：区分设备内部密封背衬和外部专用支承，不把内部加厚写成完全零新增方块。
- 用途：使未来仓室位置背后有实体承接，保持外轮廓不变且不留下悬空接口。

【变更记录 #3】2026-10-23 11:01:33（静态操作可达性检查）
- 删除：无。
- 新增：从外围搜索有实体地面、两格净高、单格高差的可步行网格，以眼高检查3格内操作点。
- 修改：逐标记记录可达站位，避免把I16脚坐标至高位接口的距离误当玩家视线距离。
- 用途：交付前发现被前栏、设备或死角阻挡的操作点；静态网格不冒充实机路径验收。
"""
from __future__ import annotations

import collections
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/controller-integration-rework-20261023'
SOURCES = ROOT / 'logs/controller-integration-review-20261023/sources.json'
CORE = 'minecraft:diamond_block'
PORT = 'hk3gtl:industrial_port_casing'
STEPS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def _now() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')


def _bounds(points) -> dict:
    points = list(points)
    return {'min': [min(p[i] for p in points) for i in range(3)],
            'max': [max(p[i] for p in points) for i in range(3)]}


def _cut_box(blocks, lo, hi, reason, removed) -> None:
    selected = {p for p in blocks if all(lo[i] <= p[i] <= hi[i] for i in range(3))}
    if selected:
        removed.append({'reason': reason, 'bounds': _bounds(selected), 'blocks': len(selected)})
        for p in selected:
            del blocks[p]


def _cut_component(blocks, seed, reason, removed) -> None:
    """只删已核实的地板以上小附件；意外连入主体时立即失败。"""
    seed = tuple(seed)
    if seed not in blocks:
        raise ValueError(f'旧附件种子不存在：{seed}')
    selected, queue = {seed}, [seed]
    while queue:
        p = queue.pop()
        for step in STEPS:
            q = tuple(p[i] + step[i] for i in range(3))
            if q[1] > 1 and q in blocks and q not in selected:
                selected.add(q)
                queue.append(q)
                if len(selected) > 128:
                    raise ValueError(f'附件与主体连接，禁止扩大删除：{reason}')
    removed.append({'reason': reason, 'bounds': _bounds(selected), 'blocks': len(selected)})
    for p in selected:
        del blocks[p]


def _place(blocks, pos, material, host, marker_id, surfaces) -> None:
    """标记只能替换现有实体表面，不能在空气中新增托块或牌面。"""
    pos = tuple(pos)
    old = blocks.get(pos)
    if old is None or old in (PORT, CORE):
        raise ValueError(f'目标不是可替换的既有表面：{marker_id} {pos}')
    x, y, z = pos
    if any((x, y, z - depth) in blocks for depth in (1, 2)):
        raise ValueError(f'北侧操作面有遮挡：{marker_id} {pos}')
    neighbors = [tuple(pos[i] + step[i] for i in range(3)) for step in STEPS]
    occupied = [p for p in neighbors if p in blocks]
    if len(occupied) < 3:
        raise ValueError(f'目标缺少主体包围关系：{marker_id} {pos}')
    back = (x, y, z + 1)
    backing_added = back not in blocks
    if backing_added:
        blocks[back] = old
    blocks[pos] = material
    surfaces.append({'id': marker_id, 'pos': list(pos), 'face': 'north', 'host': host,
                     'replaced_state': old, 'existing_neighbors': len(occupied),
                     'new_support_blocks': 0,
                     'internal_backing_added': int(backing_added)})


def _access(pos, name) -> dict:
    x, y, z = pos
    return {'name': name, 'min': [x, y - 1, z - 2], 'max': [x, y, z - 1]}


def _reachable_operations(blocks, size, markers) -> list:
    """按两格高站立体和一步高差核查外围至操作点的连通，不模拟游戏AI。"""
    width, _, depth = size
    top = max(pos[1] for _, pos in markers) + 1

    def walkable(x, y, z):
        return (0 <= x < width and 0 <= z < depth and 1 <= y <= top
                and (x, y, z) not in blocks and (x, y + 1, z) not in blocks
                and (x, y - 1, z) in blocks)

    seen = {(x, y, z) for x in range(width) for z in range(depth)
            if x in (0, width - 1) or z in (0, depth - 1)
            for y in range(1, top + 1) if walkable(x, y, z)}
    queue = collections.deque(seen)
    while queue:
        x, y, z = queue.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for dy in (-1, 0, 1):
                nxt = (x + dx, y + dy, z + dz)
                if nxt in seen or not walkable(*nxt):
                    continue
                if dy == 1 and (x, y + 2, z) in blocks:
                    continue
                seen.add(nxt)
                queue.append(nxt)
    records = []
    for marker_id, (x, y, z) in markers:
        candidates = []
        for px, py, pz in seen:
            if pz >= z:
                continue
            # 眼睛取脚底以上1.62格，目标取北面中心；未做射线遮挡结论。
            distance2 = ((px + .5) - (x + .5)) ** 2 + ((py + 1.62) - (y + .5)) ** 2 + ((pz + .5) - z) ** 2
            if distance2 <= 9:
                candidates.append((distance2, (px, py, pz)))
        if not candidates:
            raise ValueError(f'外围无可达的三格内操作站位：{marker_id}')
        distance2, standing = min(candidates)
        records.append({'id': marker_id, 'standing_cell': list(standing),
                        'eye_to_face_distance': round(distance2 ** .5, 3),
                        'walk_model': '两格净高、实体地面、单格高差；实机与视线另验收'})
    return records


def _i16(data, blocks, removed, surfaces) -> dict:
    old = tuple(data['controller'])
    if old != (24, 10, 4):
        raise ValueError('I16 来源不是已核实的 V3 HDV')
    _cut_box(blocks, old, old, '移除雨棚顶单块旧主控，保留雨棚及横梁', removed)
    controller = [29, 3, 3]
    _place(blocks, controller, CORE, '既有装料入口右门柱北表面，沿用柱身和背柱',
           'controller', surfaces)
    for port in data['ports']:
        surfaces.append({'id': port['id'], 'pos': port['pos'], 'face': port['face'],
                         'host': '既有主厅北墙，保持原嵌墙接口', 'new_support_blocks': 0})
    data['paths'].append(_access(controller, '入口右门柱主控操作净空'))
    return {'controller': controller,
            'principle': '保留已经融合的北墙六接口；主控由雨棚顶下移到人可接近的门柱表面，不另立控制盒。',
            'description': 'HDV双门架、恒温厂房和侧翼保持原设计；六接口仍嵌北立面，主控定位标记嵌入入口右门柱。'}


def _i17(data, blocks, removed, surfaces) -> dict:
    if tuple(data['controller']) != (24, 8, 4):
        raise ValueError('I17 来源不是已核实的 V1 QSV')
    for port in data['ports']:
        _cut_component(blocks, port['pos'], f'拆除{port["id"]}独立接口小柱', removed)
    _cut_component(blocks, data['controller'], '拆除独立主控仪表牌架及双脚', removed)
    # 计量柜和冷却柜在开敞厅内；只打开其前方原有单格高横杆的步行入口。
    for x0 in (7, 12, 32):
        _cut_box(blocks, (x0, 3, 5), (x0 + 2, 3, 5), '打开既有设备厅前栏的局部操作入口', removed)
    placements = {
        'LIQUID_FUEL': ([8, 3, 8], '左侧液态燃料计量柜原有北前脸'),
        'STABILIZER': ([13, 3, 8], '左侧稳定介质计量柜原有北前脸'),
        'COOLANT': ([33, 3, 8], '右侧冷却调节过滤设备原有北前脸'),
        'CONCENTRATE': ([7, 3, 40], '后场浓缩燃料低位储槽原有北端壁'),
        'RESIDUAL': ([42, 3, 40], '后场尾液储槽原有北端壁'),
        'POWER': ([44, 3, 5], '右侧控制与冷却厅原有北向外侧角柱'),
    }
    for port in data['ports']:
        pos, host = placements[port['id']]
        _place(blocks, pos, PORT, host, port['id'], surfaces)
        port['pos'] = pos
        port['integration_host'] = host
    controller = [29, 3, 5]
    _place(blocks, controller, CORE, '右侧控制附房入口原有内侧门柱', 'controller', surfaces)
    data['paths'] = [{'name': '北侧连续物流与检修前庭', 'min': [2, 2, 2], 'max': [46, 4, 4]}]
    for port in data['ports']:
        data['paths'].append(_access(port['pos'], port['id'] + '设备表面操作净空'))
    data['paths'].append(_access(controller, '控制附房门柱主控操作净空'))
    data['zones'] = [z for z in data['zones'] if z.get('kind') != 'control']
    data['zones'].append({'name': '控制与冷却调节附房原位操作区', 'kind': 'control',
                          'min': [29, 1, 5], 'max': [44, 10, 17], 'pos': controller,
                          'role': '原有附房门柱主控、冷却柜及角柱供能，不设专用接口载体',
                          'service_face': '北侧'})
    return {'controller': controller,
            'principle': '按计量、冷却、浓缩成品和尾液分流布置接口，所有标记直接替换既有设备或附房表面。',
            'description': 'QSV阶梯精馏塔群与管廊保持原设计；北场六根接口柱及主控架已拆，计量和冷却输入入柜，输出入对应储槽，主控及供能归入控制附房。'}


def _i18(data, blocks, removed, surfaces) -> dict:
    if tuple(data['controller']) != (22, 3, 3):
        raise ValueError('I18 来源不是已核实的 V1 HBV')
    _cut_box(blocks, (17, 1, 3), (27, 5, 4), '拆除11×5白框集中面板及HBV背板', removed)
    _cut_box(blocks, (20, 2, 5), (24, 7, 7), '拆除仅为外挂面板服务的仪表背箱', removed)
    _cut_box(blocks, (17, 6, 7), (27, 6, 7), '拆除背箱专用横梁，保留左右闸室原有边墙', removed)
    placements = {
        'P01': ([7, 3, 7], '原料计量与包壳闸室北墙：包壳接收'),
        'P02': ([10, 3, 7], '原料计量与包壳闸室北墙：燃料接收'),
        'P03': ([13, 3, 7], '原料计量与包壳闸室北墙：密封件接收'),
        'P04': ([2, 3, 20], '抽气过滤廊北端壁：惰性介质处理'),
        'P05': ([34, 3, 18], '热室原有东部门架北表面：冷却介质进入'),
        'P06': ([10, 3, 18], '热室原有西部门架北表面：工艺供能'),
        'P07': ([22, 3, 18], '热室中轴北墙：屏蔽维护'),
        'P08': ([4, 3, 20], '抽气过滤廊北端壁：抽气'),
        'P09': ([39, 3, 23], '检漏实验翼北端壁：检测件接收'),
        'P10': ([31, 3, 7], '检测与出厂闸室北墙：燃料棒出厂'),
        'P11': ([34, 3, 7], '检测与出厂闸室北墙：废件拒收'),
        'P12': ([37, 3, 7], '检测与出厂闸室北墙：回收件分流'),
        'P13': ([35, 3, 18], '热室东部北墙：热冷却液返回'),
        'P14': ([6, 3, 20], '抽气过滤廊北端壁：废气排出'),
        'P15': ([41, 3, 23], '检漏实验翼北端壁：检漏结果'),
        'P16': ([15, 4, 7], '原料闸室内侧北墙：原料侧备用物流'),
        'P17': ([38, 4, 7], '出厂闸室北墙：成品侧备用物流'),
    }
    for port in data['ports']:
        pos, host = placements[port['id']]
        _place(blocks, pos, PORT, host, port['id'], surfaces)
        port['pos'] = pos
        port['integration_host'] = host
    controller = [29, 3, 7]
    _place(blocks, controller, CORE, '既有检测与出厂闸室内侧北向门柱', 'controller', surfaces)
    data['paths'] = [p for p in data['paths'] if p['name'] != '主控前操作通道']
    for port in data['ports']:
        data['paths'].append(_access(port['pos'], port['id'] + '工艺设施表面操作净空'))
    data['paths'].append(_access(controller, '检测闸室门柱主控操作净空'))
    data['zones'] = [z for z in data['zones'] if z.get('kind') != 'control']
    data['zones'].append({'name': '检测闸室原位操作区', 'kind': 'control',
                          'min': [28, 2, 7], 'max': [39, 10, 14], 'pos': controller,
                          'role': '主控直接融入既有检测闸室门柱，接口随工艺设施分布',
                          'service_face': '北侧'})
    return {'controller': controller,
            'principle': '拆除外挂白框及专用支承，把17口分别归入原料、出厂、热室、抽气及检漏设施的既有表面。',
            'description': 'HBV蓝脊热室与并列封装线保留；取消独立白框板、仪表背箱及其横梁。主控嵌入检测闸室门柱，17口按物料、冷却、气路、检测和维护职责进入对应墙面。'}


def revise(data: dict) -> dict:
    """返回独立修订候选；输入数据和原文件保持不变，异常时不输出半成品。"""
    result = copy.deepcopy(data)
    key = result.get('key')
    if key not in ('i16', 'i17', 'i18'):
        raise ValueError(f'只接受 I16–I18：{key}')
    before = {tuple(b['pos']): b['state'] for b in data['blocks']}
    if len(before) != len(data['blocks']):
        raise ValueError('源数据包含重复坐标')
    blocks = dict(before)
    removed, surfaces = [], []
    details = {'i16': _i16, 'i17': _i17, 'i18': _i18}[key](result, blocks, removed, surfaces)
    controller = details['controller']
    result['controller'] = result['core_marker'] = controller
    result['controller_facing'] = 'north'
    result['name'] = data['name'] + '-integration-v1'
    result['candidate_version'] = data.get('candidate_version', '') + ' · 控制器接口融合修订 V1'
    result['description'] = details['description']
    notes = result.setdefault('construction_notes', {})
    notes['controller_marker'] = f'钻石块{controller}为嵌入既有工艺设施表面的主控定位标记，朝北；不是正式控制器。'
    notes['orientation'] = 'X向东、Y向上、Z向南；主控和所有接口朝北（-Z），位置随实际工艺设施分布。'
    notes['approval'] = '结构修改已授权；本融合修订为独立待审候选，不继承旧外观批准，不部署。'
    notes['ports'] = '工业接口方块为惰性位置标记；仅改变外观位置，真实仓室能力与Pattern另验收。'
    result['blocks'] = [{'pos': list(p), 'state': state} for p, state in sorted(blocks.items())]
    intended = {tuple(p['pos']) for p in result['ports']}
    if intended != {p for p, state in blocks.items() if state == PORT}:
        raise ValueError('接口标记存在旧位残留或缺失')
    if {p for p, state in blocks.items() if state == CORE} != {tuple(controller)}:
        raise ValueError('主控标记数量或坐标不符')
    for original, changed in zip(data['ports'], result['ports']):
        if any(original[field] != changed[field] for field in ('id', 'face', 'purpose')):
            raise ValueError('接口身份、方向或原定用途被改变')
    for p in blocks:
        if not all(0 <= p[i] < data['size'][i] for i in range(3)):
            raise ValueError('修订超出原尺寸')
    original_materials = set(before.values())
    if set(blocks.values()) - original_materials - {CORE}:
        raise ValueError('引入了原件之外的普通建材')
    for path in result.get('paths', []):
        lo, hi = path['min'], path['max']
        hit = [p for p in blocks if all(lo[i] <= p[i] <= hi[i] for i in range(3))]
        if hit:
            raise ValueError(f'操作净空被实体占据：{path["name"]} {hit[:4]}')
    markers = [('controller', controller)] + [(p['id'], p['pos']) for p in result['ports']]
    operation_checks = _reachable_operations(blocks, data['size'], markers)
    now = _now()
    result['integration_revision'] = {
        'revision': 1, 'created_at': now, 'timezone': 'Asia/Hong_Kong',
        'source_name': data['name'], 'source_controller': data['controller'],
        'source_ports': copy.deepcopy(data['ports']), 'principle': details['principle'],
        'removed_ranges': removed, 'new_surfaces': surfaces,
        'operation_access': operation_checks,
        'actual_changes': {'removed': sum(p not in blocks for p in before),
                           'replaced': sum(p in blocks and blocks[p] != v for p, v in before.items()),
                           'added': sum(p not in before for p in blocks)},
        'material_counts': dict(collections.Counter(blocks.values())),
        'checks': {'interface_identity_preserved': True, 'size_preserved': True,
                   'no_new_detached_carriers': True, 'no_stale_markers': True,
                   'no_new_ordinary_material': True, 'declared_path_clearance': True,
                   'reachable_operation_points_within_3_blocks': True},
        'unverified': ['新候选外观审批', '正式控制器与Pattern', '真实仓室能力',
                       '配方、生存首建和游戏内可达性', '统一导出及材质预览由主任务继续验收'],
        '变更记录': [{'序号': '#1', '时间': now, '删除': removed, '新增': surfaces,
                   '修改': '仅独立候选的标记坐标、操作净空与说明',
                   '原因': '控制器和接口自然融入工艺主体', '用途': '供统一导出及用户评审'}],
    }
    return result


def main() -> None:
    source_index = json.loads(SOURCES.read_text(encoding='utf-8-sig'))
    for item in source_index['items']:
        if item['key'] not in ('i16', 'i17', 'i18'):
            continue
        source = ROOT / item['source'] / 'blueprint.json'
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != item['sha256']['blueprint']:
            raise ValueError(f'原件身份变化：{source}')
        data = json.loads(source.read_text(encoding='utf-8-sig'))
        candidate = revise(data)
        meta = candidate['integration_revision']
        meta['source_blueprint'] = source.relative_to(ROOT).as_posix()
        meta['source_sha256'] = digest
        meta['rule_read_record'] = [
            {'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
             'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'read_completed_at': _now()}
            for p in sorted((ROOT / 'rule').iterdir()) if p.is_file()
        ]
        destination = OUT / item['key'] / 'candidate.json'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(candidate, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
        print(json.dumps({'key': item['key'], 'path': str(destination),
                          'changes': meta['actual_changes']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
