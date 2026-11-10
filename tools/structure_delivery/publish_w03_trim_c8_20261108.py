# -*- coding: utf-8 -*-
"""记录C6衍生的三处指定删除，不把外观修改记为动态净空或游戏通过。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import re
import shutil
from PIL import Image
from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W03_C8_去星冠光柱与外伸节点_20261108'
LOG = ROOT / 'logs/w03-trim-c8-20261108'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'


def load(path): return json.loads(path.read_text('utf8'))
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest, proof, partition, qa = [load(p) for p in [OUT / 'manifest.json', OUT / 'verification.json', LOG / 'geometry-partition.json', LOG / 'viewer-qa.json']]
    assert proof['passed'] and proof['readback']['geometry_nbt_schematic_per_block_equal'] and partition['passed'] and qa['passed']
    assert manifest['remaining_component_motion_identical_to_c6'] and manifest['motion_components'] == 32
    assert all(sha(ROOT / name) == expected for name, expected in load(LOG / 'preserved-files.json').items())
    with Image.open(OUT / '三处删除演示.webp') as animation:
        assert animation.n_frames == 32
    rule = ROOT / 'rule/当前多方块设计规则.md'
    paths = [REPORT / 'index.html', REPORT / 'current-summary.json', rule]
    original = {p: (LOG / 'before' / p.relative_to(ROOT)).read_bytes() for p in paths}
    assert all(p.read_bytes() == b for p, b in original.items()), '现有记录已变化，须重新合并'
    old = json.loads(original[REPORT / 'current-summary.json']); data = deepcopy(old)
    now = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    work = data['current_work']; assert work['wonder_motion']['code'] == 'C6'
    previous = deepcopy(work['wonder_motion']); previous['follow_up_status'] = 'C6原稿保留；三处指定删除形成C8衍生候选。'
    work['wonder_motion_history'].append(previous)
    receipt = dict(code='C8', source='C6', status='三处指定删除后的独立球形运动候选待审',
        approved=False, installed=False, game_verified=False, selected_as_edit_base=True,
        discarded_design_not_reused='C7', removals=manifest['removals'],
        blocks=manifest['blocks'], unique_materials=manifest['unique_materials'], size_xyz=manifest['size'],
        moving_components=32, moving_rings=5, moving_stars=24, moving_spears=6, self_rotating_crystals=24,
        rotating_core=True, multi_axis_spherical_rotation=True, coherent_rigid_assembly=False,
        original_c6_component_shapes_and_motion_preserved=True, full_cycle_seconds=360, frame_rate_limit=30,
        all_spears_target_core=True, maximum_spear_axis_miss=qa['spatial']['maximum_spear_miss'],
        source_instance_version='增强版3.5', material_resources_refreshed=True,
        nbt_schematic_and_preview_updated=True, complete_geometry_not_clipped=True,
        static_parts=['基座', '八锚塔', '控制器与通用接口'],
        continuous_dynamic_clearance=False, dynamic_clearance_fully_accepted=False,
        preview=str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/'),
        verification=str((OUT / 'verification.json').relative_to(ROOT)).replace('\\', '/'),
        remaining='仅落实圈定删除；其余动态穿模及完整净空仍待修正与核验，游戏内投影、GT成型与性能未验收。', updated_at=now)
    work['wonder_motion'] = receipt
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    system['wonder_motion_review'] = deepcopy(receipt); system['updated_at'] = now
    data['report_updated_at'] = now; data['systems'].sort(key=lambda s: s['percent'])
    assert [(s['id'], s['earned'], s['possible'], s['percent']) for s in data['systems']] == [(s['id'], s['earned'], s['possible'], s['percent']) for s in old['systems']]
    assert all(s == next(t for t in old['systems'] if t['id'] == s['id']) for s in data['systems'] if s['id'] != 'multiblocks')
    assert all(work[k] == v for k, v in old['current_work'].items() if k not in ['wonder_motion', 'wonder_motion_history'])
    assert data['target_instance'] == old['target_instance'] and data['overall_percent'] == old['overall_percent'] and data['multiblock_scope'] == old['multiblock_scope']
    state = ('2026-11-08 · W03 C8按两张红圈截图、以C6为基线删除橙色柱709格、顶部12星冠5,844格及后部外伸节点1,696格，恢复743格原底座表面。'
             '剩余32组独立运动的形状、位置、旋转轴与速度逐项保持C6；五环、外24星、核心、六矛及24晶体保留。'
             '完整NBT/Schematic与表面逐格回读通过；实际609×521×636、6,642,464格、14材质，3.5实例材质已重取。'
             'C7继续弃用；本轮仅完成指定删除，其他动态穿模、游戏成型与性能仍待验。既定74项、批准57／正式52及全部系统分数保持。')
    h = original[REPORT / 'index.html'].decode('utf8')
    h, n = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + now + ' · W03 C8三处指定删除</p>', h, count=1); assert n == 1
    h = h.replace('id="w03-c6-restored-current"', 'id="w03-c6-restored-history"', 1)
    anchor = '<main><h1>系统完成度 · 低到高 · 固定入口</h1>'; assert anchor in h
    link = '<a href="../../deliveries/W03_C8_去星冠光柱与外伸节点_20261108/index.html">C8三处删除预览</a>'
    h = h.replace(anchor, anchor + '<p class="notice" id="w03-c8-current">' + state + ' ' + link + '</p>', 1)
    start = h.index('<details class="system" data-id="multiblocks"'); end = h.index('<div class="table-wrap">', start)
    h = h[:end] + '<p class="evidence">' + state + ' ' + link + '</p>' + h[end:]
    h, n = re.subn(r'(?<=id="audit-data">).*?(?=</script>)', lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), h, count=1, flags=re.S); assert n == 1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>', h, re.S)[1]) == data
    assert re.findall(r'<details class="system" data-id="([^"]+)"', h) == [s['id'] for s in data['systems']]
    note = '''

## 2026-11-08 W03 C6基础的三处指定删除（C8候选）

- 负责人两张红圈截图明确要求删掉核心上方橙色柱、整圈顶部星冠，以及底座后部外伸构件。该指定删除覆盖原案保留规则中的对应三处，不扩大到其他构件。
- C8以C6为唯一运动基线：删除顶部12星冠5,844格、橙色柱709格及后部斜向汇流节点1,696格，并恢复它覆盖的743格原底座表面；主控、八处通用接口及四条池底导管保持。实际完整包围盒609×521×636，6,642,464格、14材质；末端范围自然缩短，不是裁切。
- 其余32组构件的形状、位置、运动枢轴、旋转轴与速度均保持C6，五环、外24星、核心、六矛、24颗晶体继续独立运动；不采用C7整套同步或上移64格方案。C6/C7原件与其他候选保留，C7仍弃用。
- 完整NBT、Schematic与预览同步删除，逐格回读与全部合并表面归属核验通过；材质从当前增强版3.5实例重新提取，原版本历史不改。该删除不等于解决其余动态穿模；完整动态净空、游戏投影、GT成型与性能仍待验收。未批准、未部署，所有系统分数和74项范围、批准／正式数量不变。
- 入口：deliveries/W03_C8_去星冠光柱与外伸节点_20261108/index.html；证据：logs/w03-trim-c8-20261108/。
'''
    publisher().publish_transaction({REPORT / 'index.html': h, REPORT / 'current-summary.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n', rule: original[rule].decode('utf8') + note}, original)
    scripts = OUT / '生成脚本'
    for name in [Path(__file__).name, 'capture_w03_trim_c8_20261108.mjs']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, scripts / name)
    save(LOG / 'publication-verification.json', dict(passed=True, current_candidate='C8', base='C6', c7_still_rejected=True,
        all_scores_and_scope_preserved=True, other_systems_unchanged=35, current_work_other_fields_preserved=True,
        ascending_order=True, html_json_consistent=True, original_candidates_unchanged=True,
        dynamic_clearance_accepted=False, game_implemented=False, game_verified=False))
    print(json.dumps(dict(passed=True, active='C8', base='C6', scores_unchanged=36, blocks=manifest['blocks']), ensure_ascii=False))


if __name__ == '__main__': main()
