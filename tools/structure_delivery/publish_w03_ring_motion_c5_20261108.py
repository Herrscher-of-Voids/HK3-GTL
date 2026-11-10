# -*- coding: utf-8 -*-
"""归档W03动态候选与W02重建决定；不变更验收分数和正式范围。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W03_C5_四环绕核运动_20261108'
LOG = ROOT / 'logs/w03-ring-motion-c5-20261108'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'


def load(path): return json.loads(path.read_text('utf8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    qa, geometry, manifest = [load(p) for p in (LOG / 'viewer-qa.json', LOG / 'geometry-partition.json', OUT / 'manifest.json')]
    assert qa['passed'] and geometry['passed']
    assert geometry['base_geometry_sha256'] == geometry['base_geometry_copy_sha256']
    assert all(e['static_surface_cells_in_conservative_envelope'] == 0 for e in geometry['conservative_swept_envelopes'])
    assert manifest['inner_ring_initial_rotation_x_degrees'] == [3, 0, 0, 0]
    assert manifest['inner_ring_render_translation_xyz'] == [[0, 11, 0]] * 4
    original = {REPORT / n: (LOG / 'report-baseline' / n).read_bytes() for n in ('index.html', 'current-summary.json')}
    assert all(path.read_bytes() == value for path, value in original.items()), '固定报告已另有改动，需以新基线合并'
    old = json.loads(original[REPORT / 'current-summary.json']); data = deepcopy(old)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    receipt = dict(status='动态外观候选待审', approved=False, installed=False, game_verified=False,
                   code='C5', source='C4', moving_inner_rings=4, fixed_outer_ring_radius=210,
                   pivot_blueprint=[336, 366, 264], inner_ring_translation_xyz=[0, 11, 0],
                   initial_axis_adjustment_degrees=[3, 0, 0, 0],
                   degrees_per_second=[3, -4, 5, -6], frame_rate_limit=30,
                   base_voxel_shape_preserved=True, preview=str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/'),
                   implementation_reference=str((LOG / 'forge-research.json').relative_to(ROOT)).replace('\\', '/'),
                   verification=str((LOG / 'viewer-qa.json').relative_to(ROOT)).replace('\\', '/'),
                   remaining='游戏内旋转投影、源方块显隐与恢复、完整动态净空、GT成型及实际客户端性能仍待实现或验收。',
                   updated_at=now)
    work = data['current_work']
    work['wonder_motion'] = receipt
    work['w02_rebuild'] = dict(decision='负责人决定W02重建；新方案未提供，旧批准版本只保留历史。',
                               previous_approval_preserved=True, replacement_approved=False, updated_at=now)
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    system['wonder_motion_review'] = deepcopy(receipt); system['updated_at'] = now
    data['report_updated_at'] = now; data['systems'].sort(key=lambda s: s['percent'])
    assert [(s['id'], s['earned'], s['possible'], s['percent']) for s in old['systems']] == [
        (s['id'], s['earned'], s['possible'], s['percent']) for s in data['systems']]
    assert all(s == next(o for o in old['systems'] if o['id'] == s['id']) for s in data['systems'] if s['id'] != 'multiblocks')
    assert data['overall_percent'] == old['overall_percent'] and data['multiblock_scope'] == old['multiblock_scope']
    for key in old['current_work']:
        assert work[key] == old['current_work'][key], key
    state = ('2026-11-08 · W03 C5四环绕核运动：最大环固定，四个内环围绕实际核心按3／-4／5／-6度每秒旋转；'
             '完整保留C4各环形状与材质，内环渲染位置统一上移11格、半径178环初始转轴修正3°。'
             '已核对本机gtladditions-3.3.1Custom的伪神之煅炉：顶点缓冲缓存与按tick变换是独立实现参考。'
             '四环逐面分组、全周期闭合、固定核心枢轴、暂停／拖动／复位、剖切回退与静态缓存核验通过；'
             '保守扫掠包络未发现静态表面相交，不替代完整游戏净空及性能验收。W02按负责人决定重建，旧批准历史保留。'
             '本轮仅离线预览，未部署；36系统分数及既定74项、批准57／正式52保持。')
    html = original[REPORT / 'index.html'].decode('utf8')
    html, count = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + escape(now) + ' · W03 C5四环动态预览</p>', html, count=1)
    assert count == 1
    anchor = '<main><h1>系统完成度 · 低到高 · 固定入口</h1>'; assert anchor in html
    html = html.replace(anchor, anchor + '<p class="notice" id="w03-c5-current">' + escape(state) +
        ' <a href="../../deliveries/W03_C5_四环绕核运动_20261108/index.html">C5动态预览</a></p>', 1)
    html, count = re.subn(r'(?<=id="audit-data">).*?(?=</script>)',
                          lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S)
    assert count == 1 and json.loads(re.search(r'id="audit-data">(.*?)</script>', html, re.S)[1]) == data
    assert re.findall(r'<details class="system" data-id="([^"]+)"', html) == [s['id'] for s in data['systems']]
    publisher().publish_transaction({REPORT / 'index.html': html,
        REPORT / 'current-summary.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, original)
    rule = ROOT / 'rule/当前多方块设计规则.md'
    shutil.copy2(rule, LOG / 'rule-before-c5.backup')
    note = '''

## 2026-11-08 W02重建与W03四环绕核运动（负责人最新决定）

- 负责人决定W02将重建；暂不为旧矩阵方案推进特效。新外观尚未给出，不改历史批准记录或57／52统计，不自行将旧版撤批、删除或替换正式建筑。
- W03最大环保持固定，其他四环要围绕中央核心转动；负责人要求参考GTL整合包“伪神的锻炉”的特效实现。本机增强版3.0实际对应gtladditions-3.3.1Custom.jar的“伪神之煅炉”，注册ID为gtladditions:forge_of_the_antichrist。
- 已核对该JAR的AntichristRingTransforms、RingStructureVertexBuffer与AntichristDeferredRenderer字节码：环按星体中心平移及独立矩阵旋转，工作时tick驱动、错速反转，原版与着色器兼容顶点缓冲分别缓存。仅借鉴原理，不复制第三方Java实现或新增依赖；该版本视距返回384格，不宣称无限距离或零性能开销。
- C5为可播放的独立动态候选：最大210格半径环固定；178／146／114／82格内环绕实际核心(336,366,264)以3／-4／5／-6度每秒转动。C4原环心为Y355，本候选四内环整体上移11格；178环初始转轴从-25°调整至-22°，其余倾角不变。上述为显式刚性变换，不裁切、缩环或改方块形状；C4原稿保留。
- 四环共86,884个合并表面逐格归属核验通过；静态颜色与深度缓存，动画只改四组矩阵，最多30帧/秒，隐藏页面暂停。最大环、六柄向核心的矛、立体晶云、基座与通用接口不动。支持暂停、360秒完整周期拖动、复位及剖切回到C4原位。
- 保守完整扫掠环带加1.8格半径后未发现静态表面候选相交；这只是离线筛查，不替代完整方块体积、游戏显隐恢复、成型及客户端性能验收。无界面网页核验不算游戏实测，内环动画不意味着NBT方块能自行旋转。
- 入口：deliveries/W03_C5_四环绕核运动_20261108/index.html；实现核对与核验：logs/w03-ring-motion-c5-20261108/。本轮未批准或部署，不改变系统分数、既定74项、批准57／正式52，也不启动封存的十周年派对预案。
'''
    rule.write_bytes(rule.read_bytes() + note.encode('utf8'))
    page = OUT / 'index.html'; content = page.read_text('utf8')
    content = content.replace('<iframe ', '<p>加速演示：</p><img src="四环转动演示.webp" alt="四个内环围绕核心旋转" style="max-width:840px;width:100%"><iframe ', 1)
    page.write_text(content, 'utf8')
    for name in ['publish_w03_ring_motion_c5_20261108.py', 'capture_w03_ring_motion_c5_20261108.mjs']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    result = dict(passed=True, scores_unchanged=36, other_systems_unchanged=35,
                  existing_current_work_fields_preserved=True, ascending_order=True,
                  scope_and_approval_counts_preserved=True, overall_percent=data['overall_percent'],
                  embedded_json_equals_summary=True, c4_data_sha256=sha(ROOT / 'deliveries/W03_C4_五环锁芯与立体晶云_20261108/w03/data.js'),
                  c5_data_sha256=sha(OUT / 'w03/data.js'),
                  audit_summary_sha256=sha(REPORT / 'current-summary.json'), audit_html_sha256=sha(REPORT / 'index.html'))
    assert result['c4_data_sha256'] == result['c5_data_sha256'] == geometry['base_geometry_sha256']
    save(LOG / 'publication-verification.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
