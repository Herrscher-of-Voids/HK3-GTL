# -*- coding: utf-8 -*-
"""I26 V4：撤下高塔与拖头；高度获逐案例外，体积递增冲突保留。"""
from __future__ import annotations

import base64
import collections
import gzip
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw
import build_i26_kwaichung_body_v3_20261026 as prior

ROOT = prior.ROOT
OUT = ROOT / 'deliveries/I26_码头主体撤高塔与拖头_构图研究_V4_20261026'
VIEW = OUT / 'i26'
NAME = 'hk3gtl-i26-no-upper-tower-no-tractors-v4-20261026'
TITLE = '世界泡无人采掘调度台 · 撤高塔与拖头构图研究'
STATUS = 'composition_study_volume_conflict'
source, geometry, base = prior.source, prior.geometry, prior.base


def build() -> dict:
    old_tower, old_fleet = source.dispatch_control_tower, source.terminal_tractor_fleet

    def low_dispatch_building():
        shared = source.CELLS
        try:
            source.CELLS = {}
            old_tower()
            retained = {pos: state for pos, state in source.CELLS.items() if pos[1] <= 88}
        finally:
            source.CELLS = shared
        for pos, state in retained.items():
            source.put(*pos, state)
        source.box((139, 87, 119), (193, 88, 166), source.QAV, replace=True)
        source.box((163, 13, 143), (169, 86, 149), source.ROBUST, replace=True)

    try:
        source.dispatch_control_tower = low_dispatch_building
        source.terminal_tractor_fleet = lambda: None
        data = geometry.build()
    finally:
        source.dispatch_control_tower, source.terminal_tractor_fleet = old_tower, old_fleet
    data.update(name=NAME, title=TITLE, candidate_version='V4', size=[333, 110, 301])
    data['composition'].update(unmanned_tractor_heads=0, container_blocks=0, upper_dispatch_tower=0)
    data['description'] = '撤高位细长塔与全部拖头，保留低位航务楼、居中主控和对称港区。负责人批准高度例外；包围盒体积递增冲突保留。'
    for zone in data['zones']:
        if zone['name'] == '中央航务调度塔':
            zone.update(name='中央低位航务楼', pos=[166, 80, 148])
        zone['name'] = zone['name'].replace('无人集卡通道', '空置车辆通道')
    data['zone_descriptions'] = [
        {'name': '保留主体', 'description': '四岸桥、七场桥、双仓、港池及低位航务楼保持镜像。'},
        {'name': '暂不摆放', 'description': '集装箱与货车拖头均为零；独立样件另审。'},
        {'name': '撤去高塔', 'description': '观测舱之上的塔与层片全部撤除；低楼补连续屋面与贯穿承重芯。'},
    ]
    return data


def voltage_comparison(counts, actual):
    lower = json.loads((ROOT / 'logs/i01-i25-voltage-progression-20261025/audit.json').read_text(encoding='utf-8'))
    forms = [f for f in lower['forms'] if f['tier'] < 22]
    metrics = {'blocks': sum(counts.values()), 'materials': len(counts), 'volume': math.prod(actual), 'height': actual[1]}
    maxima = {}
    for key in metrics:
        value = max(form['metrics'][key] for form in forms)
        maxima[key] = {'value': value, 'ids': [f['id'] for f in forms if f['metrics'][key] == value]}
    return {'source': 'logs/i01-i25-voltage-progression-20261025/audit.json', 'lower_form_count': len(forms),
            'tier_rule': '按现行QAV递增规则逐项比较；负责人可单独批准实际高度例外，其他指标不随之豁免。', 'metrics': metrics, 'lower_maxima': maxima,
            'passes': {k: v > maxima[k]['value'] for k, v in metrics.items()}}


def report(data, check):
    v = check['voltage_progression']
    result_label = lambda key: '负责人例外' if key == 'height' and key in check.get('rule_exceptions', {}) else ('通过' if v['passes'][key] else '冲突')
    rows = ''.join(f'<tr><td>{label}</td><td>{v["metrics"][key]:,}</td><td>{v["lower_maxima"][key]["value"]:,}</td><td>{result_label(key)}</td></tr>'
                   for key, label in [('blocks', '实体方块数'), ('materials', '材料种类'), ('volume', '实体包围盒体积'), ('height', '实际高度')])
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I26 V4撤高塔主体研究</title>
<style>body{{max-width:1300px;margin:30px auto;padding:0 24px;background:#111927;color:#e5edf6;font:16px/1.8 system-ui,'Microsoft YaHei',sans-serif}}a{{color:#8ce0dc}}img{{max-width:100%;height:auto}}.warning{{border-left:4px solid #dcab61;background:#302a25;padding:16px}}table{{border-collapse:collapse;width:100%}}td,th{{padding:8px;border-bottom:1px solid #475268;text-align:left}}</style></head><body>
<h1>I26 V4 · 撤高塔与拖头的码头主体</h1><p>保留低位航务楼与[166,76,119]主控，撤除观测舱上方细长塔；集装箱、拖头均暂不摆放。四岸桥、七场桥、双仓及八个工业接口继续围绕X=166镜像。</p>
<p class="warning">负责人已批准实际高度110格低于I25的190格下限，避免为达数字硬加格格不入的高塔。包围盒体积仍低于I25，体积递增冲突尚未解决；这仍是未批准的构图研究，不得接入实例。</p>
<p><a href="i26/三维评审.html">打开三维评审</a> · <a href="../I26_货柜八色与拖头四色_独立样件_V1_20261026/index.html">八色货柜与四色拖头独立样件</a> · <a href="verification.json">逐项核验</a></p>
<img src="等轴预览.png" alt="撤高塔与拖头的I26对称主体"><p>333 × 301 × 110格；{check['blocks']:,}方块；{check['unique_materials']}种材料；镜像差异0；单一连通体。</p>
<h2>现行递增规则比较</h2><table><thead><tr><th>指标</th><th>本版</th><th>低阶最大值</th><th>结果</th></tr></thead><tbody>{rows}</tbody></table>
<p>几何净空、镜像与资源解析通过，不代表整体规则通过。游戏Pattern、EU、接口功能与真实帧率未验收；未修改游戏实例。</p></body></html>'''


def main():
    if OUT.exists() and any(OUT.iterdir()):
        identity = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
        if identity.get('status') not in (STATUS, 'composition_study_rule_conflict') or identity.get('approved') is not False:
            raise FileExistsError('拒绝覆盖身份不明或已批准交付')
    VIEW.mkdir(parents=True, exist_ok=True)
    data = build()
    checked = geometry.assert_left_right_symmetry(data)
    assert not any(b['state'] == source.YELLOW for b in data['blocks']), '仍存在拖头黄色块'
    assert not any(139 <= b['pos'][0] <= 193 and b['pos'][1] > 88 and 125 <= b['pos'][2] <= 170 for b in data['blocks']), '高塔仍存在'
    base.W, base.H, base.D = data['size']
    base.OUT, base.VIEW, base.NAME, base.TITLE = OUT, VIEW, NAME, TITLE
    base.CELLS = geometry.CELLS
    base.voltage_comparison = voltage_comparison
    check = base.audit(data)
    check.update(passed=False, geometry_passed=True, status=STATUS, approved=False, eligible_for_approval=False)
    check['checks'] = [item.replace('7个工业接口候选', '8个工业接口候选').replace('调度塔', '低位航务楼')
                       for item in check['checks'] if '均严格大于' not in item]
    check['checks'].append('高塔、全部拖头与货柜撤下；X=166逐格镜像差异0。')
    check['rule_exceptions'] = {'height': {'approved_by': '负责人', 'actual': check['height'], 'lower_tier_minimum': check['voltage_progression']['lower_maxima']['height']['value'], 'reason': '避免为满足高度数字硬加与港区主体风格脱节的塔；整体构图与功能协调优先。', 'scope': '仅豁免实际高度，不豁免包围盒体积、方块数、材料种类及其他规则。'}}
    check['rule_conflicts'] = [k for k, passed in check['voltage_progression']['passes'].items() if not passed and k not in check['rule_exceptions']]
    check['left_right_symmetry'] = {'axis_x': 166, 'mirror_transform': "x' = 332 - x", 'mismatched_voxels': 0, 'symmetric_voxels_checked': checked}
    check['composition'] = data['composition']
    assert check['connectivity']['components'] == 1
    assert check['height'] == 110 and 'height' not in check['rule_conflicts'] and 'volume' in check['rule_conflicts']
    counts = collections.Counter(b['state'] for b in data['blocks'])
    states = sorted(counts)
    materials, sources, packs, proof = base.resource_materials(states)
    states, groups, hashes = base.export(data, VIEW)
    check.update(source_instance=str(base.INSTANCE), instance_proof=proof, enabled_file_resource_packs=packs, material_resource_sources=sources, nbt_schem_sha256=hashes)
    surfaces = base.build_surface_groups(data, states)
    check['viewer_surface_faces'] = sum(len(face) for group in surfaces for face in group)
    check['viewer_draw_triangles'] = check['viewer_surface_faces'] * 2
    check['viewer_instance_matrix_bytes'] = check['viewer_surface_faces'] * 64
    readback = {((i % base.W), i // (base.W * base.D), (i // base.W) % base.D): state for state, group in zip(states, groups) for i in group}
    assert readback == {tuple(b['pos']): b['state'] for b in data['blocks']}
    check['viewer_payload_exact_cell_readback'] = True
    payload = {'data': {k: v for k, v in data.items() if k not in ('blocks', 'zone_descriptions')}, 'palette': states, 'surfaceGroups': surfaces,
               'blockCount': len(data['blocks']), 'materials': materials, 'audit': check, 'names': {state: state.split(':')[1] for state in states}}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), compresslevel=9)).decode('ascii')
    (VIEW / 'data.js').write_text('window.HK3_PAYLOAD="' + encoded + '";\n', encoding='utf-8')
    subprocess.run(['node', str(base.VIEWER_BUILDER), str(VIEW)], cwd=ROOT, check=True)
    bundle = VIEW / 'viewer.bundle.js'
    js = bundle.read_text(encoding='utf-8').replace('逐格回读与净空检查通过', '几何检查通过；高度获负责人例外，体积递增冲突待处理')
    bundle.write_text(js, encoding='utf-8')
    base.render(data, materials, OUT)
    image = Image.open(OUT / '等轴预览.png').convert('RGB'); draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, 48), fill='#101720')
    draw.text((18, 10), 'I26 V4 · 撤高塔与拖头 · 构图研究', font=base.font(22), fill='#e7e5e0')
    draw.rectangle((0, image.height - 46, image.width, image.height), fill='#101720')
    draw.text((18, image.height - 37), f'333 × 301 × 110 | {len(data["blocks"]):,}方块 | 镜像差异0 | 高度例外获批 · 体积仍冲突', font=base.font(19), fill='#ecc88d')
    image.save(OUT / '等轴预览.png')
    page = base.viewer_page(data, check).replace('V2', 'V4').replace('调度塔', '低位航务楼')
    page = re.sub(r'<details open><summary>设计构成</summary>.*?</details>', '<details open><summary>构图研究与规则核验</summary><p>高塔、货柜、拖头撤除，保留低位航务楼与钻石主控。主体镜像、净空和连通检查通过；负责人批准110格实际高度低于I25的190格下限，理由是避免破坏港区整体构图。体积11,025,630仍低于I25的11,970,190；体积规则冲突未豁免，当前不可批准接入。</p></details>', page, flags=re.S)
    page = page.replace('V4候选：葵涌码头式泊位、岸桥、堆场和低位航务楼；未获批准、未接入游戏。', 'V4构图研究：高度例外获负责人批准；体积递增冲突未解决，未获批准、未接入游戏。')
    (VIEW / '三维评审.html').write_text(page, encoding='utf-8')
    (OUT / 'index.html').write_text(report(data, check), encoding='utf-8')
    manifest = {'generator': Path(__file__).name, 'key': 'I26', 'title': TITLE, 'candidate_version': 'V4', 'status': STATUS, 'approved': False, 'eligible_for_approval': False,
                'size_xyz': data['size'], 'size_wdh': check['size_wdh'], 'blocks': check['blocks'], 'unique_materials': check['unique_materials'], 'controller': data['controller'], 'ports': data['ports'],
                'composition': data['composition'], 'left_right_symmetry': check['left_right_symmetry'], 'voltage_progression': check['voltage_progression'], 'rule_exceptions': check['rule_exceptions'], 'rule_conflicts': check['rule_conflicts'],
                'source_instance': str(base.INSTANCE), 'source_instance_version': proof['instance_version'], 'claim_boundary': '仅构图研究；高度获负责人逐案例外，包围盒体积递增冲突未解决。无货柜、拖头与高塔；未批准、未接入实例。'}
    base.write_json(OUT / 'manifest.json', manifest)
    base.write_json(OUT / 'verification.json', check)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    shutil.copy2(__file__, OUT / '生成脚本' / Path(__file__).name)
    print(json.dumps({'output': str(OUT), 'blocks': check['blocks'], 'materials': check['unique_materials'], 'height': check['height'], 'volume': check['bounding_box_volume'],
                      'components': check['connectivity']['components'], 'mirror_mismatches': 0, 'rule_conflicts': check['rule_conflicts'], 'surface_faces': check['viewer_surface_faces']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
