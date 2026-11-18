# -*- coding: utf-8 -*-
"""I09–I15 控制器和接口融合候选，保留各机主体与来源材料。

【文件职责】输入当前已审查蓝图的深拷贝，拆除统一前排柜墙或门架挂盒，
把标记嵌入实际工艺设备；主任务负责 NBT、Schematic 和预览导出。
【变更记录 #1】2026-10-23 10:59:38（结构候选修订，不增加模组修订号）
- 删除：I09–I14 的独立主控盒、六个接口墩和废弃接口引管；I15 门架挂盒。
- 新增：逐台设备表面的标记坐标、局部壳体衬厚、来源与未验收边界。
- 修改：旧接口路线和检修路径指向当前设备，名称、尺寸、工艺主体不变。
- 用途：落实负责人已授权的结构修改；不写批准归档、正式资源或游戏实例。
【变更记录 #2】2026-10-23 11:08:00（静态操作路径自检修正）
- 新增：原设备间的贴地检修格栅、机器人基座踏步、回转庭入口踏步。
- 修改：I14尾液口下移至原冷却回收基座；不增加接口柜、立柱或材料。
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/controller-integration-rework-20261023'
PORT = 'hk3gtl:industrial_port_casing'
DIAMOND = 'minecraft:diamond_block'
GRATE = 'gtceu:assembly_line_grating'
POWER = 'gtceu:high_power_casing'
SOLID = 'gtceu:solid_machine_casing'
CLEAN = 'gtceu:clean_machine_casing'
FRAME = 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing'
PIPE_MATERIALS = {
    'gtceu:tungstensteel_pipe_casing', 'gtceu:ptfe_pipe_casing',
    'gtceu:advanced_computer_casing', POWER,
}

# 顺序与来源六接口相同；用途和朝向均沿用，不用集中牌面承载。
LAYOUTS = {
    'i09': {
        'controller': [24, 3, 14],
        'ports': [[4, 4, 25], [6, 4, 25], [39, 5, 16],
                  [25, 3, 14], [24, 5, 22], [6, 3, 32]],
        'surfaces': ['冷凝塔低位回流壳', '冷凝塔低位溶剂壳', '粉体计量驱动机座',
                     '釜体前承座功率节', '釜底锥形排放口', '分液缓冲罐北侧曲壁'],
        'control_surface': '釜体前承腿的实体功率承座',
        'principle': '曲面釜、冷凝塔、粉斗分别接收本工段接口；主控成为前承座的一部分。',
    },
    'i10': {
        'controller': [31, 2, 14],
        'ports': [[2, 4, 21], [2, 3, 21], [33, 2, 14],
                  [48, 4, 21], [39, 2, 18], [48, 3, 21]],
        'surfaces': ['进料分流端传动承座', '进料端模板定量承座', '第三夹环前鞍座',
                     '收集端传动承座', '末级夹环冷却鞍座', '收集端低位尾气回收面'],
        'control_surface': '最大共振夹环的宽实心前鞍座',
        'principle': '共轴设备的输入输出落在两端真实承座，控制和冷却进入夹环鞍座，保留轴向轮廓。',
    },
    'i11': {
        'controller': [12, 2, 10],
        'ports': [[11, 2, 10], [19, 3, 12], [7, 4, 12],
                  [35, 3, 12], [42, 2, 10], [47, 4, 12]],
        'surfaces': ['西侧送料轨端面', '本体定位工位基座', '西侧机器人肩轴基座',
                     '东侧检验工位基座', '东侧送料轨出件端面', '东侧机器人肩轴回收面'],
        'control_surface': '西侧U形送料轨的固定前端',
        'principle': '六台折肘工位和U形轨承接分布式接口；中央前场恢复为开放检修入口。',
    },
    'i12': {
        'controller': [22, 3, 18],
        'ports': [[5, 3, 11], [20, 3, 18], [24, 3, 18],
                  [39, 3, 11], [26, 3, 20], [39, 3, 19]],
        'surfaces': ['左翼模板数据仓', '晶舱低位进样壳', '晶舱低位功率壳',
                     '右翼并行数据仓', '晶舱东前侧成品壳', '右翼第二数据仓回写面'],
        'control_surface': '分面编程晶舱的八角固定基座',
        'principle': '数据口进入双翼低位数据仓，样本和成品进入晶舱自身的八角基座。',
    },
    'i13': {
        'controller': [26, 3, 8],
        'ports': [[24, 3, 8], [11, 4, 9], [9, 3, 18],
                  [45, 4, 15], [22, 4, 36], [12, 4, 30]],
        'surfaces': ['纵向载具床进样端', '膜料计量塔北壁', '包覆环前承重锚座',
                     '东侧换热器下端箱', '后段固化测厚门固定脚', '真空泵回收壳'],
        'control_surface': '纵向载具床的固定驱动端面',
        'principle': '从载具入口到测厚出件按工艺分散接口，绿白厚环前不再有白色柜墙。',
    },
    'i14': {
        'controller': [23, 3, 8],
        'ports': [[21, 3, 8], [5, 5, 20], [44, 3, 17],
                  [18, 3, 35], [41, 3, 29], [40, 3, 17]],
        'surfaces': ['预混送进床驱动端', '前驱液保温炉低位壳', '双联蓄压站宽基座',
                     '后向读出床侧箱', '冷却回收段宽基座回流端', '蓄压站维护基座'],
        'control_surface': '既有前送料滚床内部的低位驱动壳',
        'principle': '在现有滚床底部封成真实驱动腔，其他口分别进入保温、蓄压、出件和回收设备。',
    },
    'i15': {
        'controller': [20, 5, 7],
        'ports': [[11, 5, 7], [17, 5, 7], [39, 5, 7],
                  [45, 5, 7], [25, 5, 35], [31, 5, 35]],
        'surfaces': ['西北炉座原嵌壁接口', '西北炉座原嵌壁接口', '东北炉座原嵌壁接口',
                     '东北炉座原嵌壁接口', '南侧冷却炉座原嵌壁接口', '南侧冷却炉座原嵌壁接口'],
        'control_surface': '西北加热炉座朝北的固定罩壳裙座',
        'principle': '仅取消院门挂盒，主控进入加热炉座；三炉六个原生嵌壁接口全部原位保留。',
    },
}


def _cells(lo, hi):
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                yield x, y, z


def _inside(p, zone):
    return all(zone['min'][i] <= p[i] <= zone['max'][i] for i in range(3))


def _route_cells(route):
    for p, q in zip(route, route[1:]):
        length = max(abs(q[i] - p[i]) for i in range(3))
        for step in range(length + 1):
            yield tuple(round(p[i] + (q[i] - p[i]) * step / max(1, length)) for i in range(3))


def _remove_front(b, data):
    """仅拆旧统一柜体；地坪压平为检修格栅，不留下高出地面的基脚。"""
    center = data['controller'][0]
    boxes = [([center - 3, 0, 5], [center + 3, 5, 6])]
    for port in data['ports']:
        x = port['pos'][0]
        boxes.extend([([x - 1, 0, 5], [x + 1, 1, 7]),
                      ([x - 1, 2, 5], [x + 1, 4, 6])])
    for lo, hi in boxes:
        for p in _cells(lo, hi):
            if p[1] == 0:
                b[p] = GRATE
            else:
                b.pop(p, None)
    discarded_links = []
    retained_links = []
    for link in data.get('links', []):
        route = link.get('route', [])
        if route and any(p[2] <= 7 for p in route):
            discarded_links.append(link)
            for p in _route_cells(route):
                if not any(_inside(p, z) for z in data.get('zones', [])):
                    if b.get(p) in PIPE_MATERIALS:
                        b.pop(p)
        else:
            retained_links.append(link)
    # 共用低位回流排同样只为旧墩服务，清掉前场独立的管排残段。
    for p, state in list(b.items()):
        if 1 <= p[1] <= 3 and p[2] <= 9 and state in PIPE_MATERIALS:
            if not any(_inside(p, z) for z in data.get('zones', [])):
                b.pop(p)
    data['links'] = retained_links
    data['paths'] = [p for p in data.get('paths', []) if p.get('name') != '正面接口检修带']
    return [{'min': lo, 'max': hi} for lo, hi in boxes], len(discarded_links)


def _remove_i15_box(b):
    regions = [([26, 5, 3], [30, 8, 4]), ([27, 5, 2], [29, 7, 2]),
               ([27, 9, 3], [29, 9, 4])]
    for lo, hi in regions:
        for p in _cells(lo, hi):
            if p[1] == 9:
                b[p] = 'gtceu:stainless_steel_turbine_casing'
            else:
                b.pop(p, None)
    return [{'min': lo, 'max': hi} for lo, hi in regions]


def _prepare_equipment(b, key):
    """只在原设备包围内局部增厚，不增加独立接口载体。"""
    maintenance = []
    def service_floor(lo, hi, material, name):
        for p in _cells(lo, hi):
            b.setdefault(p, material)
        maintenance.append({'name': name, 'support_min': lo, 'support_max': hi,
                            'min': [lo[0], hi[1] + 1, lo[2]],
                            'max': [hi[0], hi[1] + 2, hi[2]]})
    if key == 'i09':
        # 釜底排放检修踏台连接原有前腿基础，可从地面连续步入。
        service_floor([22, 0, 9], [26, 0, 10], GRATE, '前场至釜前承座的贴地检修格栅')
        service_floor([22, 1, 17], [26, 1, 21], GRATE, '釜底锥形排放口检修踏台')
    if key == 'i10':
        service_floor([37, 0, 11], [41, 0, 17], GRATE, '夹环鞍座间低位检修格栅')
    if key == 'i11':
        service_floor([3, 1, 9], [4, 1, 10], GRATE, '西肩机器人基座检修踏步')
        service_floor([50, 1, 9], [51, 1, 10], GRATE, '东肩机器人基座检修踏步')
    if key == 'i12':
        service_floor([25, 0, 14], [27, 0, 19], GRATE, '晶舱东前角贴地检修连接')
        # 原八角基座高低错台：只声明实际可走的净空，不把整块铺装误写成空气框。
        maintenance[-1]['min'] = [26, 1, 14]
        maintenance[-1]['max'] = [26, 2, 16]
        maintenance.append({'name': '晶舱东前角既有基座抬高操作段',
                            'min': [26, 2, 17], 'max': [26, 3, 19]})
    if key == 'i13':
        service_floor([23, 0, 0], [29, 0, 1], GRATE, '厂界至原前场的贴地检修入口')
    if key == 'i14':
        # 原滚床底部是空腔，在既有床宽/床长内补出驱动外皮和端板。
        for p in _cells([20, 2, 8], [26, 4, 11]):
            x, y, z = p
            if x in (20, 26) or y in (2, 4) or z in (8, 11):
                b[p] = SOLID
        for p in _cells([22, 3, 9], [24, 3, 10]):
            b[p] = 'gtceu:tungstensteel_gearbox'
    if key == 'i15':
        service_floor([27, 1, 22], [29, 1, 22], 'gtceu:steel_brick_casing',
                      '北门主检修道接回转庭的一格踏步')
    return maintenance


def revise(data: dict) -> dict:
    """返回独立候选；越界、旧材料丢失或未嵌入设备时立即拒绝输出。"""
    result = deepcopy(data)
    key = result['key'].lower()
    if key not in LAYOUTS:
        raise ValueError('不属于本模块处理范围：' + key)
    plan = LAYOUTS[key]
    original = {tuple(row['pos']): row['state'] for row in result['blocks']}
    blocks = dict(original)
    source_materials = set(original.values())
    old_controller = list(result['controller'])
    old_ports = deepcopy(result['ports'])
    if key == 'i15':
        removed_regions, removed_links = _remove_i15_box(blocks), 0
    else:
        removed_regions, removed_links = _remove_front(blocks, result)
    maintenance = _prepare_equipment(blocks, key)
    if key == 'i15':
        # 原检修道末端变为一格踏步，平地净空范围相应止于踏步之前。
        for path in result.get('paths', []):
            if path['name'] == '北門至回轉庭的地面主檢修道':
                path['max'][2] = 21
    result.setdefault('paths', []).extend(maintenance)
    positions = [plan['controller']] + plan['ports']
    embedded = []
    for index, pos in enumerate(positions):
        p = tuple(pos)
        underlying = blocks.get(p)
        if underlying is None or underlying in (PORT, DIAMOND):
            if key == 'i15' and index > 0 and underlying == PORT:
                underlying = 'gtceu:stainless_steel_turbine_casing'
            else:
                raise ValueError(f'{key} 坐标不是实际设备壳面：{p}')
        front, back = (p[0], p[1], p[2] - 1), (p[0], p[1], p[2] + 1)
        if front in blocks:
            raise ValueError(f'{key} 北向操作面被挡住：{p} / {blocks[front]}')
        backing_added = back not in blocks
        if backing_added:
            # 内部补同材衬厚；不向外新增边框、牌面或落地柱。
            blocks[back] = underlying
        blocks[p] = DIAMOND if index == 0 else PORT
        embedded.append({'kind': '主控' if index == 0 else old_ports[index - 1]['id'],
                         'pos': list(p), 'face': 'north',
                         'surface': plan['control_surface'] if index == 0 else plan['surfaces'][index - 1],
                         'replaced_state': underlying, 'backing_added_inside_equipment': backing_added})
    result['controller'] = plan['controller'][:]
    result['controller_face'] = 'north'
    for index, port in enumerate(result['ports']):
        port['pos'] = plan['ports'][index][:]
        port['integration_surface'] = plan['surfaces'][index]
    for field in ('paste_anchor', 'core_marker'):
        if field in result and result[field] == old_controller:
            result[field] = result['controller'][:]
    for index, port in enumerate(result['ports']):
        x, y, z = port['pos']
        result.setdefault('links', []).append({
            'from': port['id'], 'to': plan['surfaces'][index],
            'embedded_surface': port['pos'][:],
            'relationship': '直接嵌入现有设备壳面，不新增外部接线柱',
        })
    result['name'] = result.get('name', key) + '-integration-v1'
    result['candidate_version'] = '控制器接口融合修订 V1，待审批'
    result['blocks'] = [{'pos': list(p), 'state': s} for p, s in sorted(blocks.items())]
    assert not (set(blocks.values()) - source_materials), '融合修订不得引入来源之外材料'
    assert len(set(tuple(p) for p in positions)) == 7, '标记坐标重复'
    assert sum(s == PORT for s in blocks.values()) == len(old_ports), '旧接口未清除或数量变化'
    assert tuple(old_controller) not in blocks or blocks[tuple(old_controller)] != DIAMOND
    assert all(blocks.get(tuple(p['pos'])) != PORT for p in old_ports) if key != 'i15' else True
    assert all(0 <= p[i] < result['size'][i] for p in blocks for i in range(3)), '坐标越界'
    for path in result.get('paths', []):
        assert not any(_inside(p, path) for p in blocks), '声明净空存在实体：' + path['name']
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    result['integration_revision'] = {
        'version': 1, 'recorded_at': now, 'status': '独立结构候选，未批准、未接入、未部署',
        'principle': plan['principle'], 'old_controller': old_controller,
        'old_ports': old_ports, 'removed_regions': removed_regions,
        'removed_obsolete_route_count': removed_links, 'embedded_surfaces': embedded,
        'maintenance_connections': maintenance,
        'deleted_blocks': sum(p not in blocks for p in original),
        'added_blocks': sum(p not in original for p in blocks),
        'replaced_blocks': sum(p in original and original[p] != s for p, s in blocks.items()),
        'unchanged_subject': '尺寸、正式名称与工艺主体保留；仅拆接口载体、修改操作壳面及必要检修踏台。',
        'voltage_boundary': 'I14/I15历史电压主壳映射缺口本轮不扩大；不新增电压机壳混用。',
        'unverified': ['外观待逐台评审', '正式控制器与Pattern', '仓室能力及配方运行', '材料阶段及生存可达', '游戏内成型'],
    }
    return result


def main():
    """从只读审查来源清单生成七份候选，来源文件不变。"""
    sources = json.loads((ROOT / 'logs/controller-integration-review-20261023/sources.json').read_text(encoding='utf-8-sig'))
    rules = []
    for p in sorted((ROOT / 'rule').iterdir()):
        if p.is_file():
            rules.append({'path': p.relative_to(ROOT).as_posix(),
                          'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                          'lines': len(p.read_text(encoding='utf-8').splitlines()), 'read_complete': True})
    for source in sources['items']:
        if source['key'] not in LAYOUTS:
            continue
        p = ROOT / source['source'] / 'blueprint.json'
        original = p.read_bytes()
        candidate = revise(json.loads(original.decode('utf-8-sig')))
        candidate['integration_revision'].update({'source_blueprint': p.relative_to(ROOT).as_posix(),
                                                'source_sha256': hashlib.sha256(original).hexdigest(),
                                                'rule_read_record': rules})
        destination = OUT / source['key'] / 'candidate.json'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(source['key'], len(candidate['blocks']), candidate['controller'])


if __name__ == '__main__':
    main()
