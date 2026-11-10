# -*- coding: utf-8 -*-
"""I20 V2只修订系列主控，保留V1几何及未确认空区。

【文件职责】复用V1扩建定义，恢复I19主控语义，撤下新增仪控厅的重复主控标记。
【变更记录 #1】2026-10-23 19:41:07（候选修订，不增加模组修订号）
删除：新增仪控厅[135,3,184]的重复钻石主控标记，恢复QSV墙面。
新增：I19原位主控继承策略、南西侧空区的实际用途缺口说明。
修改：主控元数据回到[95,3,20]朝北；不再按扩建后的全宽重定位。
用途：保持同系列反应堆的原位升级体验；不擅自为用户询问的空地新增设备。
"""
import copy

from build_i20_qsv_second_unit_v1 import ROOT, BASE, W, H, D, STATES, QSV
from build_i20_qsv_second_unit_v1 import build as build_v1

OUT = ROOT / 'deliveries/I20_中型崩坏能反应堆_原位主控修订_V2_20261023'
LOG = ROOT / 'logs/i20-controller-inheritance-v2-20261023'
NAME = 'i20-qsv-inherited-controller-v2'


def build():
    data, geometry = build_v1()
    data = copy.deepcopy(data)
    found = 0
    for block in data['blocks']:
        if block['pos'] == [135, 3, 184]:
            assert block['state'] == 'minecraft:diamond_block'
            block['state'] = STATES[QSV]
            found += 1
    assert found == 1
    original_control = next(b for b in data['blocks'] if b['pos'] == [95, 3, 20])
    assert original_control['state'] == 'minecraft:diamond_block'
    data.update(name=NAME, candidate_version='原位主控修订V2・待审', controller=[95, 3, 20], controller_face='north')
    for zone in data['zones']:
        if zone['name'] == '两代机组联合仪控厅・主控第136格':
            zone['name'] = 'QSV扩建仪控厅・无新增主控'
    data['integration_revision']['principle'] = '系列主控继承I19原位，嵌原主厂房北墙；新旧接口仍分别融入各自工艺设备。'
    data['controller_centering'] = {
        'policy': '同系列累积扩建保留I19主控锚点，覆盖此前按I20全宽重定位的方案',
        'source_controller': [95, 3, 20], 'source_width': 191,
        'source_center_column_1based': 96, 'whole_i20_width_center_required': False,
        'summary': 'I19宽191的第96格；I20沿用该位置，不另立新主控。'}
    data['layout_gap'] = {
        'id': 'A', 'min_xz': [6, 184], 'max_xz': [107, 217], 'size_xz': [102, 34],
        'area_blocks': 3468, 'solid_blocks': 0,
        'actual_cause': 'V1南向扩建从X108开始布置仪控厅，西端仅围了道路，未给这块空区安排设备或明确用途。',
        'status': '已标出布局缺口；没有证据将其称为必需检修区、安全间距或后续阶段预留。',
        'action': '本轮回答留空原因，暂保留原几何；填入何种设施或缩改边界尚未确定。'}
    geometry.pop('controller_centered', None)
    geometry['controller_inherits_i19'] = True
    geometry['controller_policy'] = data['controller_centering']
    geometry['layout_gap'] = data['layout_gap']
    geometry['revision_from_v1'] = {'changed_blocks': 1, 'old_position': [135, 3, 184],
        'before': 'minecraft:diamond_block', 'after': STATES[QSV], 'added_blocks': 0, 'removed_blocks': 0}
    return data, geometry
