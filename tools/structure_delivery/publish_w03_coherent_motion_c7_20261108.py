# -*- coding: utf-8 -*-
"""归档C7连续净空修订；保留历史候选、W02、客户端证据与系统分数。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
from PIL import Image
from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W03_C7_同步立体净空修订_20261108'
LOG = ROOT / 'logs/w03-coherent-motion-c7-20261108'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'


def load(path): return json.loads(path.read_text('utf8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    qa, geometry, manifest, proof = [load(p) for p in (LOG / 'viewer-qa.json', LOG / 'geometry-partition.json', OUT / 'manifest.json', OUT / 'verification.json')]
    assert qa['passed'] and geometry['passed'] and qa['all_33_components_move']
    assert geometry['source_geometry_sha256'] == geometry['referenced_geometry_sha256']
    assert proof['passed'] and proof['continuous_dynamic_clearance'] and proof['all_frames_and_between_frames']
    assert all(sha(ROOT / path) == expected for path, expected in load(LOG / 'preserved-deliveries.json').items())
    with Image.open(OUT / '同步立体演示.webp') as animation:
        assert animation.n_frames == 32
        frames = animation.n_frames
    original = {REPORT / n: (LOG / 'report-baseline' / n).read_bytes() for n in ('index.html', 'current-summary.json')}
    current = load(REPORT / 'current-summary.json')
    already = current['current_work'].get('wonder_motion', {}).get('code') == 'C7'
    if not already:
        assert all(path.read_bytes() == value for path, value in original.items()), '固定报告已有别的改动，须重新合并基线'
    rule = ROOT / 'rule/当前多方块设计规则.md'
    assert rule.read_bytes() == (LOG / 'rule-before-c7.backup').read_bytes(), '规则已有别的改动，须重新合并'
    old = json.loads(original[REPORT / 'current-summary.json']); data = deepcopy(old)
    now = current['report_updated_at'] if already else datetime.now(timezone(timedelta(hours=8))).isoformat()
    receipt = dict(status='连续动态净空核验通过的同步立体候选待审', approved=False, installed=False, game_verified=False,
        code='C7', source='C4完整几何；C5/C6保留对照', moving_rings=5, maximum_ring_fixed=False,
        multi_axis_spherical_rotation=True, moving_components=33, moving_stars=36,
        rotating_core=True, moving_spears=6, orbiting_crystals=24, coherent_rigid_assembly=True,
        all_spears_target_core=True, maximum_spear_axis_miss=qa['spatial']['maximum_spear_miss'],
        static_parts=manifest['static_parts'],
        pivot_blueprint=manifest['pivot_blueprint'], all_floating_parts_translation=[0, 64, 0],
        c5_axis_adjustment_reused=False, base_voxel_shape_preserved=True,
        moving_quads=sum(geometry['moving_quads']), frame_rate_limit=30,
        full_cycle_seconds=360, animation_webp_frames=frames,
        conservative_swept_bounds_export=manifest['conservative_swept_bounds_export'],
        continuous_dynamic_clearance=True, component_pair_checks=proof['independent_component_pairs'],
        guaranteed_internal_surface_gap=proof['guaranteed_internal_surface_gap'],
        guaranteed_static_vertical_gap=proof['guaranteed_static_vertical_gap'],
        c6_confirmed_collision=proof['c6_confirmed_collision_regression'],
        motion_note='全部浮空构件共用Y公转与X/Z各±8°摆转；原有相对布局不变；整套显式上移64格。取消独立多轴互切。',
        preview=str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/'),
        verification=str((LOG / 'viewer-qa.json').relative_to(ROOT)).replace('\\', '/'),
        remaining='离线候选连续净空已通过；美术批准、游戏内投影与显隐恢复、GT成型、实际客户端性能仍待实现或验收。',
        updated_at=now)
    work = data['current_work']
    previous = deepcopy(work['wonder_motion'])
    previous['follow_up_status'] = '负责人反馈穿模；离线复现82环与固定光柱相交，C7作为独立修订候选。'
    work.setdefault('wonder_motion_history', []).append(previous)
    work['wonder_motion'] = receipt
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    system['wonder_motion_review'] = deepcopy(receipt); system['updated_at'] = now
    data['report_updated_at'] = now
    data['systems'].sort(key=lambda s: s['percent'])
    assert [(s['id'], s['earned'], s['possible'], s['percent']) for s in old['systems']] == [
        (s['id'], s['earned'], s['possible'], s['percent']) for s in data['systems']]
    assert all(s == next(o for o in old['systems'] if o['id'] == s['id']) for s in data['systems'] if s['id'] != 'multiblocks')
    assert data['overall_percent'] == old['overall_percent'] and data['multiblock_scope'] == old['multiblock_scope']
    for key in old['current_work']:
        if key not in ('wonder_motion', 'wonder_motion_history'):
            assert work[key] == old['current_work'][key], key
    state = ('2026-11-08 · W03 C7同步立体净空修订：C6独立翻转穿模已复现；完整浮空总成共用Y公转与X/Z各±8°摆转，保持C4相对布局，整体显式上移64格避开底座。'
        '33组／406,338合并表面完整，完整光柱随核心运动；528组间距与连续角度上界核验通过，部件间实体净空至少6.2679格、对固定基座与八锚塔至少11.0871格，覆盖帧间运动。'
        '五环法向持续改变、六矛持续向上指芯，完整扫掠取景无裁切；支持360秒周期、暂停／拖动／复位与指向线。'
        'C4/C5/C6与W02 V3保留；候选未批准、未部署，游戏内成型与性能待验。'
        '36系统分数、总完成度77.49535072554875%、既定74项、批准57／正式52保持。')
    html = original[REPORT / 'index.html'].decode('utf8')
    html, count = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + escape(now) + ' · W03 C7同步立体净空修订</p>', html, count=1)
    assert count == 1
    anchor = '<main><h1>系统完成度 · 低到高 · 固定入口</h1>'; assert anchor in html
    notice = '<p class="notice" id="w03-c7-current">' + escape(state) + ' <a href="../../deliveries/W03_C7_同步立体净空修订_20261108/index.html">C7净空修订预览</a></p>'
    html = html.replace(anchor, anchor + notice, 1)
    section = '<details class="system" data-id="multiblocks"'
    start = html.index(section); end = html.index('<div class="table-wrap">', start)
    html = html[:end] + '<p class="evidence">' + escape(state) + ' <a href="../../deliveries/W03_C7_同步立体净空修订_20261108/index.html">C7预览与参数</a></p>' + html[end:]
    html, count = re.subn(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S)
    assert count == 1 and json.loads(re.search(r'id="audit-data">(.*?)</script>', html, re.S)[1]) == data
    assert re.findall(r'<details class="system" data-id="([^"]+)"', html) == [s['id'] for s in data['systems']]
    if already:
        assert current == data and (REPORT / 'index.html').read_text('utf8') == html, '已有C7记录与预期不一致'
    else:
        publisher().publish_transaction({REPORT / 'index.html': html,
            REPORT / 'current-summary.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, original)
    rule = ROOT / 'rule/当前多方块设计规则.md'
    assert rule.read_bytes() == (LOG / 'rule-before-c7.backup').read_bytes(), '规则已有别的改动，须重新合并'
    note = '''

## 2026-11-08 W03动态穿模修订C7（负责人反馈）

- 负责人反馈“W03转起来之后……都穿模了”。离线复现C6第40秒82环与固定天顶光柱实体相交；此前仅记录包络风险不构成动态净空通过。保留C4/C5/C6作历史，不修改旧候选。
- C7取消独立多轴翻转与五环单独上移11格，恢复C4全部相对布局；五环、36星、核心与完整光柱、六矛及24晶体共用绕核心Y轴2°/秒公转，并叠加X/Z各±8°、180/90秒周期摆转。浮空总成整体显式上移64格，新运动枢轴(336,430,264)；未删除、缩短或裁切构件。晶云保持分散立体布局并随总成公转；六矛连续向上指芯。基座、八锚塔、控制器与通用接口固定。
- 完整体素归属与406,338合并表面逐格核验；528组部件对保持至少8格中心切比雪夫距离，共同刚体变换使完整单位立方体表面间距至少8−√3=6.267949格。X/Z总偏角连续上界16°；完整浮空实体最低Y≥88.087114、固定建筑最高Y≤77，至少11.087114格竖直净空。证明覆盖全周期与帧间运动，721个矩阵时刻及浏览器一致性另作回归核验。
- 完整扫掠包络扩展、五环法向变化、360秒闭合、指向线、暂停／拖动／复位／剖切、静态深度缓存及无逐帧几何重传均作离线核验。32帧完整周期加速WebP与4张全景归档；复用C4大资源，避免重复数据。
- 入口：deliveries/W03_C7_同步立体净空修订_20261108/index.html；证明：同目录verification.json；证据：logs/w03-coherent-motion-c7-20261108/。这是新的外观修订候选，尚未批准、实装或游戏实测；游戏投影、GT成型及性能继续保留差距。W02 V3、AE进度、既定74项、批准57／正式52及36系统分数不变。
'''
    rule.write_bytes(rule.read_bytes() + note.encode('utf8'))
    for name in ('publish_w03_coherent_motion_c7_20261108.py', 'capture_w03_coherent_motion_c7_20261108.mjs'):
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    result = dict(passed=True, scores_unchanged=36, other_systems_unchanged=35,
        current_work_other_fields_preserved=True, ascending_order=True, scope_and_approval_counts_preserved=True,
        old_deliveries_sha256_verified=True, overall_percent=data['overall_percent'],
        embedded_json_equals_summary=True, animation_frames=frames, continuous_dynamic_clearance=True,
        game_implemented=False, game_verified=False,
        audit_summary_sha256=sha(REPORT / 'current-summary.json'), audit_html_sha256=sha(REPORT / 'index.html'))
    save(LOG / 'publication-verification.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
