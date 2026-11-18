# -*- coding: utf-8 -*-
"""直接读取69座占地总表，防止候选与正式导出缩小既定尺寸。
变更#1 2026-09-28 02:50:25：新增逐轴及实体范围检查，无删除；供结构生成器复用。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html'

def baselines():
    text = SOURCE.read_text(encoding='utf-8')
    rows, _ = json.JSONDecoder().raw_decode(text.split('const machines=', 1)[1].lstrip())
    result = {r['id']: r for r in rows}
    assert len(rows) == len(result) == 69, '占地总表数量或唯一编号变化，需要复核'
    return result

def check(data):
    row = baselines()[data['key'].upper()]
    w, d, h = row['size']
    minimum = [w, h, d]
    blocks = data['blocks']
    low = [min(b['pos'][i] for b in blocks) for i in range(3)]
    high = [max(b['pos'][i] for b in blocks) for i in range(3)]
    actual = [high[i]-low[i]+1 for i in range(3)]
    return {'id': row['id'], 'baseline_wdh': row['size'], 'declared_xyz': data['size'],
            'actual_xyz': actual, 'min_pos': low, 'max_pos': high,
            'passed': all(data['size'][i] >= minimum[i] and actual[i] >= minimum[i] for i in range(3)),
            'source': str(SOURCE.relative_to(ROOT)), 'axis_order': '总表宽长高；候选及实际范围宽高深'}

def require(data):
    result = check(data)
    if not result['passed']:
        raise ValueError('结构尺寸低于总表，拒绝导出：' + json.dumps(result, ensure_ascii=False))
    return result
