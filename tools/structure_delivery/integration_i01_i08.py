# -*- coding: utf-8 -*-
"""I01四阶及I02–I08的控制器、接口融合候选生成器。

【变更记录 #1】2026-10-23 11:04:15（融合修订候选V1，不增加模组修订号）
删除：旧独立主控面板、六接口矮墩及失去端点的前庭专用管路。
新增：逐台设备表面的嵌入位置、原位扩建继承检查和候选变更数据。
修改：从既有批准蓝图深拷贝，保持主体、电压主色、名称及逐轴尺寸；
      I01以新的固定冷凝塔裙座为四阶共同基准，不改旧确认归档。
用途：供主交付脚本导出候选NBT、Schematic和预览；不修改正式资源或实例。

公开入口revise只返回新字典。原生成器仅用于精确回退被旧接口线路覆盖的
设备表面；临时替换通过上下文管理器恢复，不执行旧生成器的文件交付入口。
接口继续使用指定占位块，钻石仍是控制器位置标记；不代表真实仓室功能。
"""
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/多方块确认归档/20261020_005209_151059_21形态_电压主色修订_已确认/confirmed_voltage_r172'
OUTPUT = ROOT / 'logs/controller-integration-rework-20261023'
PORT = 'hk3gtl:industrial_port_casing'
CONTROL = 'minecraft:diamond_block'
GRATE = 'gtceu:assembly_line_grating'
BASE = 'gtceu:solid_machine_casing'
HBV = 'hk3gtl:voltage_machine_casing_hbv'
KEYS = [f'i01-{n}' for n in range(1, 5)] + [f'i{n:02}' for n in range(2, 9)]
TIME = lambda: datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')

# 坐标来自现有设备实体。每项依次为新位置、所属设备、工艺关系。
PLANS = {
    'i02': {'controller': (19, 3, 12), 'controller_host': '样本棱镜台北端圆形承台',
            'ports': {
                'STANDARD': ((16, 3, 13), '样本棱镜台', '标准件进入同一进样承台'),
                'SAMPLE': ((22, 3, 13), '样本棱镜台', '待测件由承台另一侧进样'),
                'REFERENCE': ((34, 3, 10), '偏心基准光源驱动座', '介质进入光源驱动座'),
                'DATA': ((19, 3, 32), '中央探测鳍固定分析座', '检测数据从弧形分析背脊读出'),
                'RETURN': ((23, 3, 14), '样本棱镜台东北切角', '样本由同一承台前侧回收'),
                'POWER': ((36, 3, 10), '偏心基准光源驱动座', '供能进入固定光源机座')},
            'entry': (19, 11),
            'principle': '保留七鳍扇阵与光路，把主控、样本、基准和读出分配到真实承台与分析座；取消前置围墙。'},
    'i03': {'controller': (7, 3, 18), 'controller_host': '飞轮前轴承固定承座',
            'ports': {
                'SOLVENT': ((16, 3, 33), '低位轴承冷却器端面', '清洗溶剂进入固定辅助回路'),
                'MOTHER_LIQUID': ((34, 3, 32), '母液缓冲计量箱北壁', '母液直接进入缓冲箱'),
                'POWER': ((3, 3, 21), '飞轮驱动机固定外壳', '供能进入驱动电机'),
                'LIGHT_PHASE': ((34, 2, 15), '轻相集液筒承台北端', '轻相从独立集液筒下端输出'),
                'HEAVY_PHASE': ((30, 3, 29), '重相缓冲箱北壁', '重相从尾端低位缓冲箱输出'),
                'RESIDUE': ((33, 3, 22), '尾部固定排料鞍座', '固相在尾锥下方的固定排料座转出')},
            'entry': (7, 17),
            'principle': '主控进入固定轴承而非旋转飞轮；进出料分别进入缓冲箱和尾部集液座，不在转鼓上贴接口板。'},
    'i04': {'controller': (17, 3, 10), 'controller_host': '低位换热梳中央固定齿座',
            'ports': {
                'WASH': ((15, 3, 20), '稳定脊固定下裙座', '清洗介质进入处理脊基座'),
                'LIQUID_ENERGY': ((19, 3, 20), '稳定脊固定下裙座', '原液由处理脊基座进料'),
                'STABILIZER': ((17, 3, 30), '后侧稳定液缓冲筒', '稳定剂进入缓冲筒'),
                'STABLE_LIQUID': ((16, 3, 31), '后侧稳定液缓冲筒斜切侧缘', '稳定液在缓冲筒下端输出'),
                'COOLANT': ((9, 3, 10), '换热梳左端齿座', '冷却回路直接进入换热列'),
                'POWER': ((29, 3, 10), '换热梳右端齿座', '供能进入循环泵与换热控制座')},
            'entry': (17, 9),
            'principle': '以既有低位换热梳作为操作面，工艺接口进入稳定脊与缓冲筒；承压叉臂和观察空腔保持。'},
    'i05': {'controller': (20, 3, 16), 'controller_host': '再生塔第一段固定下裙座',
            'ports': {
                'FEED': ((16, 3, 16), '再生塔下裙座', '待再生介质由塔脚进料'),
                'FILTER': ((14, 3, 16), '再生塔滤芯输送下端', '替换滤材从塔脚进入内部滤芯提升路线'),
                'POWER': ((24, 3, 16), '再生塔下裙座', '回热与再生供能进入固定塔脚'),
                'RESIDUE': ((21, 3, 33), '后侧屏蔽回收坞北壁', '残留物直接从回收坞输出'),
                'COOLANT': ((33, 4, 15), '回热冷凝器固定北端封头', '冷却介质进入冷凝器端头'),
                'PRODUCT': ((37, 4, 15), '回热冷凝器固定北端封头', '再生介质从同一冷凝端分流输出')},
            'entry': (20, 15),
            'principle': '保留收肩塔、侧抽盒及回热器的完整分区，主控嵌入塔脚；接口落在塔脚、冷凝封头和回收坞本体。'},
    'i06': {'controller': (23, 2, 17), 'controller_host': '一级滚筒固定承重鞍座',
            'ports': {
                'BASE': ((5, 3, 14), '第一原料计量仓北壁', '燃料基质进入第一计量仓'),
                'MEDIUM': ((5, 3, 22), '第二原料计量仓北壁', '稳定介质进入第二计量仓'),
                'POWER': ((18, 3, 17), '一级滚筒固定承重鞍座', '供能进入固定传动床'),
                'CATALYST': ((5, 3, 30), '第三原料计量仓北壁', '催化剂进入第三计量仓'),
                'FUEL': ((49, 3, 13), '连续灌装导向床北端', '成品沿灌装床输出'),
                'RESIDUE': ((49, 5, 32), '末段灌装服务头北面', '残余物从灌装末段分流')},
            'entry': (23, 16),
            'principle': '控制器进入滚筒鞍座，三类原料分别进入已有计量仓，产品接口进入连续灌装床，露天双轴轮廓保持。'},
    'i07': {'controller': (22, 3, 15), 'controller_host': '光学标定床固定前端',
            'ports': {
                'REFERENCE': ((5, 3, 15), '标准件架第一段北端', '标准件直接进入基准架'),
                'TEST_PIECE': ((20, 3, 15), '标定床前端', '待测件进入固定定位床'),
                'POWER': ((24, 3, 15), '标定床前端', '信号源供能进入标定床固定机座'),
                'READOUT': ((38, 3, 15), '读出架第一段北端', '校准数据从第一读出模块输出'),
                'PRODUCT': ((38, 3, 23), '读出架第二段北端', '合格件从中段分流'),
                'REJECT': ((38, 3, 31), '读出架第三段北端', '不合格件从末段分流')},
            'entry': (22, 14),
            'principle': '主控与待测件入口进入纵向标定床，左右基准架及读出架各承担对应接口，光轴和八角光阑不变。'},
    'i08': {'controller': (22, 3, 9), 'controller_host': '取晶床固定前端',
            'ports': {
                'PRECURSOR': ((4, 3, 14), '第一前驱体计量器北壁', '前驱体进入低位计量器'),
                'MEDIUM': ((4, 3, 27), '第二前驱体计量器北壁', '结晶介质进入第二计量器'),
                'POWER': ((24, 3, 9), '取晶床固定前端', '供能沿取晶床固定外壳进入种晶座'),
                'COOLANT': ((39, 3, 18), '冷却片组第一段固定下端', '冷却回路进入现有片组集管区'),
                'CRYSTAL': ((20, 3, 9), '取晶床固定前端', '晶体沿窄取晶床输出'),
                'RESIDUE': ((21, 3, 35), '母液回收泵北壁', '母液与副产物在后泵分流')},
            'entry': (22, 8),
            'principle': '主控进入既有取晶床；计量、冷却、取晶和母液接口分散到对应设备本体，不改棱晶与四爪夹架。'}
}


def _grid(data):
    return {tuple(b['pos']): b['state'] for b in data['blocks']}


def _box(grid, lo, hi, state):
    for x in range(lo[0], hi[0]+1):
        for y in range(lo[1], hi[1]+1):
            for z in range(lo[2], hi[2]+1):
                grid[x, y, z] = state


def _body(data):
    """仅移除旧接口专用构件，保留被覆盖之前的真实设备表面。"""
    key = data['key']
    if key.startswith('i01-'):
        module = importlib.import_module('i01_chain_v8')
        method = key.replace('-', '_')
    else:
        module = importlib.import_module('i02_i04_v7' if key <= 'i04' else 'i05_i07_v7' if key <= 'i07' else 'i08_v7')
        method = key
    original = getattr(module, method)()
    with ExitStack() as stack:
        if key.startswith('i01-'):
            old_route = module.SignedBuild.route
            def routed(a, source, target, points, material=module.PIPE):
                if source != '固定控制坞':
                    old_route(a, source, target, points, material)
            stack.enter_context(patch.object(module, 'dock', lambda a: None))
            stack.enter_context(patch.object(module.SignedBuild, 'route', routed))
        else:
            common = importlib.import_module('i09_i13_v6_common')
            stack.enter_context(patch.object(common, 'interfaces', lambda a, purposes, shell: ([a.w//2, 3, 5], [])))
            old_route = module.route
            def routed(a, source, target, points, *material):
                if '接口' not in source and source != '正面接口坞':
                    old_route(a, source, target, points, *material)
            stack.enter_context(patch.object(module, 'route', routed))
            if key <= 'i04':
                stack.enter_context(patch.object(module, 'common_ground', lambda a: None))
            elif key <= 'i07':
                stack.enter_context(patch.object(module, '_front', lambda a: None))
        clean = getattr(module, method)()
    # I01的原始生成器按实际包围盒重新归零，必须先还原signed，再映回输入原点。
    def signed_grid(d):
        origin = d.get('signed_origin', [0, 0, 0])
        return {tuple(b['pos'][i]+origin[i] for i in range(3)): b['state'] for b in d['blocks']}
    old, raw, source = signed_grid(original), signed_grid(clean), signed_grid(data)
    assert old.keys() == source.keys(), (key, '原几何生成器与批准来源不一致')
    mapping = data.get('candidate_revision', {}).get('state_mapping', {})
    result = {}
    origin = data.get('signed_origin', [0, 0, 0])
    for pos, state in raw.items():
        state = source[pos] if old.get(pos) == state else mapping.get(state, state)
        result[tuple(pos[i]-origin[i] for i in range(3))] = state
    for field in ('paths', 'links', 'zones'):
        collection = deepcopy(clean[field])
        delta = [clean.get('signed_origin', [0, 0, 0])[i]-origin[i] for i in range(3)]
        for entry in collection:
            for field2 in ('min', 'max', 'pos'):
                if field2 in entry:
                    entry[field2] = [entry[field2][i]+delta[i] for i in range(3)]
            if 'route' in entry:
                entry['route'] = [[p[i]+delta[i] for i in range(3)] for p in entry['route']]
        data[field] = collection
    return result


def _i01(data, grid):
    shift = data['coordinate_shift']
    local = lambda p: tuple(p[i]+shift[i] for i in range(3))
    # 连续切角裙座与原塔的三格半径体形一致，顶部直接承接现有塔壳。
    for y in range(2, 5):
        for x in range(-3, 4):
            for z in range(-3, 4):
                if abs(x)+abs(z) <= 5 and (y == 2 or max(abs(x), abs(z)) == 3):
                    grid[local((x, y, z))] = HBV
    # U形维护环服务塔脚及回流泵，北侧短入口通向实际操作位置。
    for lo, hi in [((-8, 0, -3), (-6, 0, 8)), ((6, 0, -3), (8, 0, 8)),
                   ((-8, 0, 6), (8, 0, 8)), ((-3, 0, -8), (3, 0, -4))]:
        _box(grid, local(lo), local(hi), GRATE)
    ports = {
        'INPUT': ((-2, 3, -3), '中央冷凝塔固定裙座', '采集介质直接进入塔脚'),
        'COOLANT': ((4, 3, 1), '既有回流分离泵北面', '冷却介质进入回流泵'),
        'POWER': ((-2, 2, -3), '中央冷凝塔固定裙座', '供能进入固定下裙座'),
        'OUTPUT': ((2, 3, -3), '中央冷凝塔固定裙座', '当阶采集物经共用下裙座输出'),
        'RECOVERY': ((6, 3, 1), '既有回流分离泵北面', '回收介质在分离泵下端分流'),
        'RETURN': ((5, 2, 1), '既有回流分离泵北面', '旁路回流进入原泵座')}
    return {'controller': local((0, 3, -3)), 'controller_host': '中央冷凝塔切角固定裙座',
            'ports': {k: (local(v[0]), v[1], v[2]) for k, v in ports.items()},
            'principle': '删除第一阶的前置白框坞，主控及主进出料嵌入与塔体连续的固定切角裙座，冷却与回流嵌入既有泵；四阶重复同一signed局部修订并逐格继承。',
            'entry': None}


def revise(source: dict) -> dict:
    """只返回独立融合候选；名称、端口标识与工艺用途不擅自更改。"""
    data = deepcopy(source)
    key = data['key']
    if key not in KEYS:
        raise ValueError('本生成器不负责该机器：'+key)
    before = _grid(data)
    grid = _body(data)
    plan = _i01(data, grid) if key.startswith('i01-') else deepcopy(PLANS[key])
    if plan['entry']:
        x, end = plan['entry']
        _box(grid, (x-2, 0, 0), (x+2, 0, end), GRATE)
        clear_end = {'i04': 8, 'i06': 14}.get(key, end)
        data['paths'].append({'name': '融合修订：北侧操作入口', 'min': [x-1, 1, 0], 'max': [x+1, 2, clear_end]})
    if key == 'i03':
        # 将原有外围检修带接至轻相筒前与低位冷却器北侧，接口仍在设备原表面。
        for lo, hi in [((31, 0, 13), (40, 0, 14)), ((13, 0, 31), (27, 0, 32)),
                       ((26, 0, 32), (27, 0, 34))]:
            _box(grid, lo, hi, GRATE)
    if key == 'i05':
        # 一条连续横廊接通原左右检修回廊与塔后回收坞，不给残渣口另建托架。
        _box(grid, (10, 0, 32), (32, 0, 32), GRATE)
    if key == 'i06':
        # 灌装床前缘的一层连续踏步，供三段现有压头与整条导向床共同维护。
        _box(grid, (48, 2, 12), (50, 2, 12), GRATE)
        # 三段压头横封床轴，沿既有灌装基础的东缘补连续踏面，避免翻越压头。
        _box(grid, (53, 2, 13), (53, 2, 37), GRATE)
    if key == 'i08':
        # 计量器、冷却片与后泵的外缘维护步道恢复原逐轴占地，保留中央露天空隙。
        for lo, hi in [((0, 0, 13), (1, 0, 32)), ((43, 0, 16), (44, 0, 35)),
                       ((15, 0, 41), (30, 0, 42)), ((0, 0, 11), (8, 0, 12)),
                       ((0, 0, 24), (8, 0, 25)), ((2, 1, 12), (7, 1, 12)),
                       ((2, 1, 25), (7, 1, 25)), ((36, 0, 13), (44, 0, 15)),
                       ((37, 1, 15), (42, 1, 15)), ((13, 0, 9), (14, 0, 16))]:
            _box(grid, lo, hi, GRATE)
    data['controller'] = list(plan['controller'])
    data['controller_face'] = 'north'
    placements = [('controller', plan['controller'], plan['controller_host'], '整机操作', CONTROL)]
    for port in data['ports']:
        pos, host, relation = plan['ports'][port['id']]
        port['pos'] = list(pos)
        port['integration_host'] = host
        placements.append((port['id'], pos, host, relation, PORT))
    surface_records = []
    for identity, pos, host, relation, marker in placements:
        pos = tuple(pos)
        assert pos in grid, (key, identity, pos, '接口必须嵌入真实设备表面')
        previous = grid[pos]
        assert previous not in (PORT, CONTROL), (key, identity, '重复标记')
        assert (pos[0], pos[1], pos[2]-1) not in grid, (key, identity, pos, '正面被遮挡')
        back = (pos[0], pos[1], pos[2]+1)
        # 薄壳内部补同材背衬，全部位于原有设备包围体内部，不另建外置承载箱。
        if back not in grid:
            grid[back] = previous
        grid[pos] = marker
        surface_records.append({'id': identity, 'pos': list(pos), 'face': 'north', 'host': host,
                                'relation': relation, 'replaced_surface_state': previous,
                                'backing': list(back), 'front_air': [pos[0], pos[1], pos[2]-1]})
    assert sum(s == PORT for s in grid.values()) == 6
    assert sum(s == CONTROL for s in grid.values()) == 1
    assert set(grid.values()) <= set(before.values()), (key, '不得引入未核对的新材料')
    # 旧标记全部位于已删除的外挂坞；删除、改色、添加均在候选身份中真实列出。
    deleted = [list(p) for p in before if p not in grid]
    changed = [{'pos': list(p), 'before': before[p], 'after': grid[p]}
               for p in before.keys() & grid.keys() if before[p] != grid[p]]
    added = [list(p) for p in grid if p not in before]
    size = [max(p[i] for p in grid)-min(p[i] for p in grid)+1 for i in range(3)]
    assert size == data['size'] and all(min(p[i] for p in grid) == 0 for i in range(3)), (key, size, data['size'])
    data['blocks'] = [{'pos': list(p), 'state': s} for p, s in sorted(grid.items())]
    data['name'] = source['name']+'-integration-v1'
    data['description'] = plan['principle']
    data['material_usage'] = dict(Counter(grid.values()))
    data['role_materials'] = {s: [s] for s in sorted(set(grid.values()))}
    data['paste_anchor'] = data['controller']
    if key.startswith('i01-'):
        data['fixed_signed_controller'] = [0, 3, -3]
        relative = {tuple(p[i]-data['controller'][i] for i in range(3)): state
                    for p, state in grid.items() if list(p) != data['controller']}
        previous_key = f'i01-{int(key[-1])-1}' if key != 'i01-1' else None
        previous = revise(json.loads((SOURCE/previous_key/'blueprint.json').read_text(encoding='utf-8'))) if previous_key else None
        previous_relative = {tuple(b['pos'][i]-previous['controller'][i] for i in range(3)): b['state']
                             for b in previous['blocks'] if b['pos'] != previous['controller']} if previous else {}
        mismatches = [p for p, state in previous_relative.items() if relative.get(p) != state]
        assert not mismatches, (key, '融合四阶继承失败', mismatches[:5])
        signed_non_controller = [(tuple(p[i]+data['signed_origin'][i] for i in range(3)), state)
                                 for p, state in sorted(grid.items()) if list(p) != data['controller']]
        data['upgrade_contract'] = {'previous': previous_key,
            'preserved_non_controller_blocks': len(previous_relative),
            'added_blocks': len(grid)-(len(previous['blocks']) if previous else 0),
            'added_non_controller_blocks': len(relative)-len(previous_relative),
            'coordinate_shift': data['coordinate_shift'], 'signed_origin': data['signed_origin'],
            'relative_local_shift': [data['coordinate_shift'][i]-(previous['coordinate_shift'][i] if previous else 0) for i in range(3)],
            'fixed_signed_controller': [0, 3, -3],
            'inheritance_basis': '新融合候选四阶按signed坐标保留前阶全部非主控方块及颜色；与旧归档比较属于重设计。',
            'signed_non_controller_sha256': hashlib.sha256(json.dumps(signed_non_controller, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest(),
            'anchor_relative_non_controller_sha256': hashlib.sha256(json.dumps(sorted(relative.items()), ensure_ascii=False, separators=(',', ':')).encode()).hexdigest(),
            'passed': True, 'integration_inheritance_passed': True}
    data['construction_notes'].update({'paste_anchor': data['controller'],
        'schematic_offset': [-p for p in data['controller']], 'status': '融合修订V1候选；未获新版外观批准，未正式接入或游戏验收。',
        'controller': plan['controller_host']+'；钻石为指定位置标记，正面朝北。'})
    source_revision = deepcopy(data.get('candidate_revision', {}))
    data['source_revision_history'] = {'voltage_revision_metadata': source_revision,
        'original_geometry_description': data.pop('original_description', source['description']),
        'note': '历史来源字段，仅用于追溯；本候选的几何、接口与继承结果以integration_revision、upgrade_contract为准。'}
    source_path = str((SOURCE/key/'blueprint.json').relative_to(ROOT))
    source_hash = hashlib.sha256((SOURCE/key/'blueprint.json').read_bytes()).hexdigest()
    data['candidate_revision'] = {'revision': 'integration-v1', 'time': TIME(), 'status': '融合几何候选，未批准、未实装',
        'source_blueprint': source_path, 'source_sha256': source_hash,
        'target_voltage': source_revision.get('target_voltage'), 'state_mapping': source_revision.get('state_mapping', {}),
        'voltage_basis': '2026-10-20负责人采用整批21形态电压主色；本次仅继承该主色，未据此声称新版几何已批准。',
        'inheritance': deepcopy(data.get('upgrade_contract', {'previous': None, 'scope': '单台局部修订'}))}
    removed_geometry = ('旧固定白框主控坞、北侧旧坞地坪和固定控制坞专用汇流线；真实塔脚、回流泵和新增工段保持。'
                        if key.startswith('i01-') else
                        '旧独立白框主控坞、六接口矮墩、专用汇流线路及其无用途前庭支座；设备本体和工艺连接保留。')
    data['integration_revision'] = {'version': 'V1', 'time': TIME(), 'status': '候选，未批准、未实装',
        'source_blueprint': source_path, 'source_sha256': source_hash,
        'principle': plan['principle'], 'removed_geometry': removed_geometry,
        'deleted_bounding_box': {'min': [min(p[i] for p in deleted) for i in range(3)],
                                 'max': [max(p[i] for p in deleted) for i in range(3)]} if deleted else None,
        'surfaces': surface_records, 'deleted_positions': deleted, 'changed_positions': changed,
        'added_positions': added, 'counts': {'before': len(before), 'after': len(grid),
                                             'deleted': len(deleted), 'changed': len(changed), 'added': len(added)},
        'not_verified': ['新版整体视觉仍待负责人审阅', '未进行正式Pattern、实际仓室能力、配方、生存可达性或游戏内成型验收',
                         '新增背衬位于已有设备内部，不能据此声称工艺运行已接通']}
    data['_change_records'] = data.get('_change_records', []) + [{'record': 1, 'time': TIME(),
        'reason': '负责人明确要求修改结构并自然融合控制器接口', 'deleted': data['integration_revision']['removed_geometry'],
        'added': '既有设备表面的控制器接口、必要内衬及实际操作入口',
        'modified': plan['principle'], 'purpose': '独立候选几何供审阅，不改确认归档与正式游戏资源'}]
    return data


def main():
    for key in KEYS:
        source = json.loads((SOURCE/key/'blueprint.json').read_text(encoding='utf-8'))
        data = revise(source)
        folder = OUTPUT/key
        folder.mkdir(parents=True, exist_ok=True)
        (folder/'candidate.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(key, len(data['blocks']), '主控', data['controller'], flush=True)


if __name__ == '__main__':
    main()
