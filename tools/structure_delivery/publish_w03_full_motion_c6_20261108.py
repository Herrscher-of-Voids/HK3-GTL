# -*- coding: utf-8 -*-
"""归档C6全动试转证据；保留W02、客户端进度和全部系统分数。"""
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
OUT = ROOT / 'deliveries/W03_C6_球形全动试转_20261108'
LOG = ROOT / 'logs/w03-full-motion-c6-20261108'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'


def load(path): return json.loads(path.read_text('utf8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    qa, geometry, manifest = [load(p) for p in (LOG / 'viewer-qa.json', LOG / 'geometry-partition.json', OUT / 'manifest.json')]
    assert qa['passed'] and geometry['passed'] and qa['all_33_components_move']
    assert geometry['source_geometry_sha256'] == geometry['copied_geometry_sha256']
    assert all(sha(ROOT / path) == expected for path, expected in load(LOG / 'preserved-deliveries.json').items())
    with Image.open(OUT / '球形全动演示.webp') as animation:
        assert animation.n_frames == 32
        frames = animation.n_frames
    original = {REPORT / n: (LOG / 'report-baseline' / n).read_bytes() for n in ('index.html', 'current-summary.json')}
    assert all(path.read_bytes() == value for path, value in original.items()), '固定报告已有别的改动，须重新合并基线'
    old = json.loads(original[REPORT / 'current-summary.json']); data = deepcopy(old)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    receipt = dict(status='球形全动外观试转候选待审', approved=False, installed=False, game_verified=False,
        code='C6', source='C4完整几何；C5单独保留', moving_rings=5, maximum_ring_fixed=False,
        multi_axis_spherical_rotation=True, moving_components=33, moving_stars=36,
        rotating_core=True, moving_spears=6, self_rotating_crystals=24,
        all_spears_target_core=True, maximum_spear_axis_miss=qa['spatial']['maximum_spear_miss'],
        static_parts=manifest['static_parts'],
        pivot_blueprint=[336, 366, 264], ring_and_outer_star_translation=[0, 11, 0],
        c5_axis_adjustment_reused=False, base_voxel_shape_preserved=True,
        moving_quads=sum(geometry['moving_quads']), frame_rate_limit=30,
        full_cycle_seconds=360, animation_webp_frames=frames,
        conservative_swept_bounds_export=manifest['conservative_swept_bounds_export'],
        conservative_radial_overlap_pairs=len(manifest['conservative_shell_overlaps']),
        overlap_note='包络重叠只作候选风险记录；不等于确认穿模，也不代表完整动态净空通过。',
        preview=str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/'),
        verification=str((LOG / 'viewer-qa.json').relative_to(ROOT)).replace('\\', '/'),
        remaining='仅离线预览；完整动态净空、游戏内投影与显隐恢复、GT成型、实际客户端性能仍待实现或验收。',
        updated_at=now)
    work = data['current_work']
    work.setdefault('wonder_motion_history', []).append(deepcopy(work['wonder_motion']))
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
    state = ('2026-11-08 · W03 C6球形全动试转：五环多轴翻转、外24星跟随最大环、顶12星自转、核心立体自转、六矛绕芯公转、24晶体原位自转。'
        '33组完整运动组件与406,019合并表面核验通过，环面法向实际改变，六矛持续向上指芯；支持360秒周期、暂停／拖动／复位和随矛运动的指向线。'
        '保留C4体素形状；五环与外星阵显式上移11格对准核心，保守完整扫掠范围未按原尺寸裁切。'
        '20对保守径向包络重叠已记录，完整动态净空未通过；仅离线预览、未部署。C4/C5及W02 V3保留。'
        '36系统分数、总完成度77.49535072554875%、既定74项、批准57／正式52保持。')
    html = original[REPORT / 'index.html'].decode('utf8')
    html, count = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + escape(now) + ' · W03 C6球形全动试转</p>', html, count=1)
    assert count == 1
    anchor = '<main><h1>系统完成度 · 低到高 · 固定入口</h1>'; assert anchor in html
    notice = '<p class="notice" id="w03-c6-current">' + escape(state) + ' <a href="../../deliveries/W03_C6_球形全动试转_20261108/index.html">C6全动预览</a></p>'
    html = html.replace(anchor, anchor + notice, 1)
    section = '<details class="system" data-id="multiblocks"'
    start = html.index(section); end = html.index('<div class="table-wrap">', start)
    html = html[:end] + '<p class="evidence">' + escape(state) + ' <a href="../../deliveries/W03_C6_球形全动试转_20261108/index.html">C6预览与参数</a></p>' + html[end:]
    html, count = re.subn(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S)
    assert count == 1 and json.loads(re.search(r'id="audit-data">(.*?)</script>', html, re.S)[1]) == data
    assert re.findall(r'<details class="system" data-id="([^"]+)"', html) == [s['id'] for s in data['systems']]
    publisher().publish_transaction({REPORT / 'index.html': html,
        REPORT / 'current-summary.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, original)
    rule = ROOT / 'rule/当前多方块设计规则.md'
    assert rule.read_bytes() == (LOG / 'rule-before-c6.backup').read_bytes(), '规则已有别的改动，须重新合并'
    note = '''

## 2026-11-08 W03球形立体全动试转（负责人最新决定）

- 负责人澄清要球体式立体转动，并授权最大环、外圈星阵、核心顶部星阵和核心一同转动，要求“将能转的全转起来试下”。本决定更新C5“最大环固定”的试转限制，不自动批准或部署候选。
- C6独立保留C4/C5：五个莫比乌斯环绕实际核心(336,366,264)作Y轴／X轴／原法向的复合刚性旋转，环面法向持续变化；五环与外24星阵整体渲染上移11格对准核心，不沿用C5的178环初始3°修正。尺寸、半扭转、材料和体素形状均不改变；全扫掠范围自行扩展，不按原包围盒裁切。
- 外24星阵与最大环同步翻转；顶部12星冠冕绕自身中心Y轴转动；核心菱形及内层XYZ复合自转；六柄亚空之矛整组绕核心Y轴公转，真实尖尾轴持续指芯且向上；24颗浓缩崩坏能晶体绕各自原中心XY复合自转，保留中央坑与下方立体晶云分布。基座、八锚塔、主控、通用接口及天顶直光柱作为固定部分。
- 完整体素归属重建并逐格核验全部合并表面，共33组、406,019合并面；动画每帧只改变组矩阵，静态颜色与深度缓存，隐藏页面暂停，30帧/秒为预览调度上限。支持360秒完整周期、暂停／拖动／复位、随矛运动的指向线和剖切回到C4静态原位。
- 离线无界面浏览器确认33组全动、五环法向变化、周期闭合、六矛持续指芯、晶体中心保持、静态缓存复用，以及六种全景的保守扫掠完整取景。32帧加速WebP与4张全景归档。20对保守径向包络重叠只作候选线索，不能称为实际穿模证明或完整净空验收；没有游戏实测、游戏实现或部署。
- 入口：deliveries/W03_C6_球形全动试转_20261108/index.html；证据：logs/w03-full-motion-c6-20261108/。W02 V3、AE实测进度和其他系统证据不变，既定74项、批准57／正式52及全部36系统分数保持。
'''
    rule.write_bytes(rule.read_bytes() + note.encode('utf8'))
    for name in ('publish_w03_full_motion_c6_20261108.py', 'capture_w03_full_motion_c6_20261108.mjs'):
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    result = dict(passed=True, scores_unchanged=36, other_systems_unchanged=35,
        current_work_other_fields_preserved=True, ascending_order=True, scope_and_approval_counts_preserved=True,
        old_deliveries_sha256_verified=True, overall_percent=data['overall_percent'],
        embedded_json_equals_summary=True, animation_frames=frames, game_implemented=False, game_verified=False,
        audit_summary_sha256=sha(REPORT / 'current-summary.json'), audit_html_sha256=sha(REPORT / 'index.html'))
    save(LOG / 'publication-verification.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
