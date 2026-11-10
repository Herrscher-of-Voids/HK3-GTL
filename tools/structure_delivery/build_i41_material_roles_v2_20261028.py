# -*- coding: utf-8 -*-
"""I41辅材与构件职责修订；保留V1，独立导出V2待审候选。"""
import hashlib
import html
import json
import shutil
import numpy as np
import build_i41_fan_dispatch_20261028 as delivery
import i41_fan_dispatch_audit_20261028 as checks
import i41_material_roles_geometry_v2_20261028 as geometry

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I41_文明能源调度中枢_铜母线与分区材质修订_V2_20261028'
LOG = ROOT / 'logs/i41-material-roles-v2-20261028'
PRIOR = ROOT / 'deliveries/I41_文明能源调度中枢_弧幕母线与扇形负载港_V1_20261028'
original_audit, original_report = checks.audit, delivery.report


def snapshot():
    return {p.relative_to(PRIOR).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in PRIOR.rglob('*') if p.is_file()}


def audit(cube, data):
    check = original_audit(cube, data)
    old = json.loads((PRIOR / 'verification.json').read_text(encoding='utf-8'))['palette']
    states, ids = geometry.STATES, geometry.IDS
    exposed = np.zeros(len(states)+1, dtype=np.int64)
    # 按真实外露面统计，空腔面计入；不把只藏在实心内部的材料称作视觉细节。
    for axis in range(3):
        a, b = [slice(None)]*3, [slice(None)]*3
        a[axis], b[axis] = slice(None, -1), slice(1, None)
        left, right = cube[tuple(a)], cube[tuple(b)]
        for face, neighbor in ((left, right), (right, left)):
            exposed += np.bincount(face[(face != 0) & (neighbor == 0)], minlength=len(exposed))
        for edge in (0, -1):
            face = np.take(cube, edge, axis=axis)
            exposed += np.bincount(face.ravel(), minlength=len(exposed))
    unused = [s for s in states if not exposed[ids[s]]]
    assert not unused, ('无外露面材料', unused)
    markers = {geometry.material.CONTROL, geometry.material.PORT}
    new = [s for s in states if s not in old and s not in markers]
    vanilla = sum(n for s, n in check['palette'].items() if s.startswith('minecraft:') and s not in markers)
    check['material_revision'] = dict(
        prior_version='V1', version='V2', main_voltage_unchanged='IWV',
        new_auxiliary_materials=new, new_auxiliary_count=len(new),
        ordinary_vanilla_blocks=vanilla, ordinary_vanilla_fraction=vanilla/(check['blocks']-7),
        exposed_faces_by_material={s: int(exposed[ids[s]]) for s in states},
        roles=geometry.ROLES, prior_same_size_detail_boxes_removed=True)
    assert len(new) >= 12, '未形成足够明确的辅材变化'
    check['checks'].append('所有材料至少具有真实外露面；V1同尺寸辅材盒改为用途明确的构件。')
    return check


def report(data, check):
    text = original_report(data, check)
    revision = check['material_revision']
    rows = ''.join(f'<tr><td><code>{html.escape(s)}</code></td><td>{n:,}</td><td>{html.escape(geometry.ROLES[s])}</td></tr>'
                   for s, n in check['palette'].items())
    section = f'''<h2>本轮材质修订</h2><p>V1有40种辅材与I40完全重合，并以同尺寸盒体填入26种材料；V2取消这组做法，按承重、铜母线、检修、测控和调度厅分别建模选材。IWV仍承担主识别，新增{revision['new_auxiliary_count']}种原V1未使用的辅材。原版普通建材占{revision['ordinary_vanilla_fraction']*100:.2f}%，不靠原版混凝土大面积换色。全部材料均有真实外露面；外观效果仍由负责人审阅。</p>
<p><a href="../{PRIOR.name}/i41/三维评审.html">保留的V1预览</a> · <a href="材质分工对照.html">逐项材质与用途</a></p>'''
    text = text.replace('<h2>从登记到回执的调度设施</h2>', section+'<h2>从登记到回执的调度设施</h2>')
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I41 V2材质分工</title><style>body{max-width:1200px;margin:32px auto;padding:0 24px;background:#121b28;color:#e7edf5;font:16px/1.8 system-ui}a{color:#9cdbdf}table{border-collapse:collapse;width:100%}td,th{padding:9px;text-align:left;border-bottom:1px solid #415163}code{overflow-wrap:anywhere}</style><h1>I41 V2 · 材质与构件职责</h1><p>以下为实际NBT/Schematic材料用量，不把方块种数当作艺术质量证明。各构件是建筑表达，未验收游戏运行。</p><p><a href="index.html">交付总览</a> · <a href="i41/三维评审.html">真实MC材质三维预览</a></p><table><tr><th>方块状态</th><th>用量</th><th>具体用途</th></tr>'+rows+'</table></html>'
    (OUT / '材质分工对照.html').write_text(page, encoding='utf-8')
    return text


def main():
    before = snapshot()
    checks.geometry = geometry
    delivery.geometry, delivery.audit, delivery.report = geometry, audit, report
    delivery.OUT, delivery.LOG = OUT, LOG
    delivery.main()
    assert snapshot() == before, 'V1历史候选被修改'
    scripts = OUT / '生成脚本'
    for filename in ('i41_material_roles_geometry_v2_20261028.py', 'build_i41_material_roles_v2_20261028.py',
                     'capture_i41_fan_dispatch_20261028.mjs'):
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    (LOG / 'v1-preservation.json').write_text(json.dumps(dict(passed=True, files=before), ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
