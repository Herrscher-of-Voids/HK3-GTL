# -*- coding: utf-8 -*-
"""I26 V3：无货柜、以中央主控为轴的码头主体。"""
from __future__ import annotations

import i26_kwaichung_geometry_v2 as source

W, H, D = source.W, source.H, source.D
CX = W // 2
CELLS = source.CELLS
QAV, PORT, CONTROL = source.QAV, source.PORT, source.CONTROL


def open_yard_apron() -> None:
    """以连续作业坪暂代箱垛位置，保留车辆与场桥的承载面。"""
    for x in range(9, W - 8):
        mirrored_x = min(x, W - 1 - x)
        for z in range(114, 275):
            if (x, 12, z) in CELLS:
                continue
            state = QAV if mirrored_x % 36 in (0, 1) or z % 28 in (0, 1) else source.GRATE
            source.put(x, 12, z, state)


def raised_apron_truss() -> None:
    """在场桥作业坪下加入三层箱形支承梁，连接港区格构基础。"""
    for y, cross_state, long_state in (
        (5, source.ROBUST, QAV), (7, QAV, source.ROBUST), (9, QAV, QAV),
    ):
        for z in range(114, 275, 18):
            source.box((9, y, z), (W - 10, y + 1, z + 1), cross_state)
        for x in range(18, W - 18, 18):
            source.box((x, y, 114), (x + 1, y + 1, 274), long_state)


def mirror_about_controller_axis() -> None:
    """以X=166左半为准生成右半，避免两份旧布局互相覆盖。"""
    left = {pos: state for pos, state in CELLS.items() if pos[0] <= CX}
    CELLS.clear()
    CELLS.update(left)
    for (x, y, z), state in left.items():
        if x < CX:
            CELLS[(W - 1 - x, y, z)] = state


def connect_yard_gantry_trolleys() -> None:
    """把吊具上方承重轨接回场桥两侧支腿。"""
    spans = ((11, 109), (126, 207), (228, 331))
    for row_start in (116, 172, 228):
        for index, (x0, x1) in enumerate(spans):
            if row_start < 200 and index == 1:
                continue
            center_z = (row_start - 4 + row_start + 21) // 2
            source.beam((x0, 43, center_z), (x1, 43, center_z), source.ROBUST, 1)


def add_symmetric_markers(data: dict) -> None:
    data['controller'] = [CX, 76, 119]
    data['ports'] = [
        {'id': '无人装置与耗材输入', 'purpose': '西侧维护坞输入候选', 'pos': [0, 25, 144], 'face': 'west'},
        {'id': '回收装置与磨损件输出', 'purpose': '东侧维护坞输出候选', 'pos': [W - 1, 25, 144], 'face': 'east'},
        {'id': '冷却介质输入', 'purpose': '西侧冷却回路输入候选', 'pos': [0, 34, 184], 'face': 'west'},
        {'id': '冷却介质回流', 'purpose': '东侧冷却回路接口候选', 'pos': [W - 1, 34, 184], 'face': 'east'},
        {'id': '任务授权与坐标输入', 'purpose': '后侧调度接口候选', 'pos': [148, 29, D - 1], 'face': 'south'},
        {'id': '供能输入', 'purpose': '后侧高压母线接口候选；额定EU待核验', 'pos': [184, 29, D - 1], 'face': 'south'},
        {'id': '远征记录接口', 'purpose': '西侧任务记录接口候选', 'pos': [0, 28, 248], 'face': 'west'},
        {'id': '遗留档案输出', 'purpose': '东侧隔离档案出口候选', 'pos': [W - 1, 28, 248], 'face': 'east'},
    ]
    outward = {'south': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0)}
    for port in data['ports']:
        dx, dy, dz = outward[port['face']]
        x, y, z = port['pos']
        source.put(x - dx, y - dy, z - dz, QAV, replace=True)
        source.put(x, y, z, PORT, replace=True)
    source.put(*data['controller'], CONTROL, replace=True)


def build() -> dict:
    CELLS.clear()
    source.base_grid()
    source.quay_and_dispatch_berth()
    open_yard_apron()
    raised_apron_truss()
    source.four_quay_cranes()
    source.yard_gantry_cranes()
    connect_yard_gantry_trolleys()
    source.terminal_tractor_fleet()
    source.dispatch_control_tower()
    source.transfer_and_gate()
    source.service_blocks()
    source.logistics_warehouses()
    mirror_about_controller_axis()

    data = {
        'key': 'I26', 'id': 'I26',
        'name': 'hk3gtl-i26-kwaichung-symmetric-terminal-body-v3-20261026',
        'title': '世界泡无人采掘调度台 · 葵涌码头主体',
        'candidate_version': 'V3', 'size': [W, H, D],
        'controller': [], 'ports': [],
        'paths': [
            {'min': [140, 12, 18], 'max': [192, 26, 69]},
            {'min': [10, 12, 110], 'max': [322, 22, 113]},
        ],
        'zones': [
            {'name': '中央单目标泊位', 'pos': [CX, 22, 49]},
            {'name': '西侧岸桥作业线', 'pos': [82, 76, 88]},
            {'name': '东侧岸桥作业线', 'pos': [250, 76, 88]},
            {'name': '西侧空箱场桥作业坪', 'pos': [82, 30, 215]},
            {'name': '东侧空箱场桥作业坪', 'pos': [250, 30, 215]},
            {'name': '西侧无人集卡通道', 'pos': [58, 20, 138]},
            {'name': '东侧无人集卡通道', 'pos': [274, 20, 138]},
            {'name': '中央航务调度塔', 'pos': [CX, 112, 148]},
            {'name': '西侧陆勤仓库', 'pos': [58, 37, 289]},
            {'name': '东侧陆勤仓库', 'pos': [274, 37, 289]},
        ],
        'description': '无货柜主体候选：中央钻石主控塔为中轴，两侧岸桥、场桥、集卡通道、仓库和维护分拣设施严格镜像。',
        'composition': {'quay_cranes': 4, 'yard_gantry_cranes': 7,
                        'unmanned_tractor_heads': 8, 'warehouses': 2,
                        'underdeck_truss_layers': 3, 'container_blocks': 0},
        'zone_descriptions': [
            {'name': '中央单目标泊位', 'description': '港池侧单一出港航路落在主控中轴，门架与磁悬载台共同标示唯一目标通道。'},
            {'name': '双侧岸桥', 'description': '四座岸桥在中轴两侧成对布置，共用中央单目标航线。'},
            {'name': '空箱场桥作业坪', 'description': '暂不放置任何集装箱；连续作业坪、七座场桥和分隔标线先确定堆场主体轮廓。'},
            {'name': '无人集卡通道', 'description': '八台黄色牵引头沿中轴两侧成对布置，车辆下方有连续承载路面。'},
            {'name': '陆勤仓库', 'description': '两座封闭仓库在控制器轴两侧等距镜像，包含连续屋面、采光带与装卸门。'},
            {'name': '中央航务调度塔', 'description': '钻石主控位于宽333格的第167格（X=166），塔体、观测层与中继塔沿同一轴线。'},
            {'name': '成对维护与分拣设施', 'description': '左半模块作为几何母版镜像到右侧，保留设备舱、检疫和维护层级，不用异形侧翼破坏对称。'},
        ],
    }
    add_symmetric_markers(data)
    data['blocks'] = [
        {'pos': list(pos), 'state': state}
        for pos, state in sorted(CELLS.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))
    ]
    return data


def assert_left_right_symmetry(data: dict) -> int:
    by_pos = {tuple(block['pos']): block['state'] for block in data['blocks']}
    mismatches = []
    for (x, y, z), state in by_pos.items():
        if by_pos.get((W - 1 - x, y, z)) != state:
            mismatches.append((x, y, z, state, by_pos.get((W - 1 - x, y, z))))
    if mismatches:
        raise ValueError(f'左右镜像不一致：{mismatches[:8]}；共{len(mismatches)}处')
    if by_pos.get(tuple(data['controller'])) != CONTROL or data['controller'][0] != CX:
        raise ValueError('主控未落在实体镜像轴上')
    cargo_palette = set(source.CONTAINER_COLORS) - {source.YELLOW}
    if any(block['state'] in cargo_palette for block in data['blocks']):
        raise ValueError('无货柜主体误含货柜彩色混凝土')
    return len(by_pos)
