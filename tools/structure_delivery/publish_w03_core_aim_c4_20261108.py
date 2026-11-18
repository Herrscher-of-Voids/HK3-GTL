# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile
from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W03_C4_五环锁芯与立体晶云_20261108'
LOG = ROOT / 'logs/w03-core-aim-c4-20261108'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'


def load(p): return json.loads(p.read_text('utf8'))
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    m, v, qa = load(OUT / 'manifest.json'), load(OUT / 'verification.json'), load(LOG / 'viewer-qa.json')
    assert v['passed'] and v['readback']['geometry_nbt_schematic_per_block_equal'] and qa['passed']
    assert v['component_clearance']['intersection_pairs_after'] == 0
    assert m['aiming']['maximum_miss_distance'] == 0 and m['crystal_cloud']['lower_central_count'] == 10
    history = ROOT / 'deliveries/W03_C3_眼形莫比乌斯_四方案_20261108'
    for folder in [OUT] + [history / code for code in ['3H', '3U', '5H', '5U']]:
        manifest, verification = load(folder / 'manifest.json'), load(folder / 'verification.json')
        for ext in ['nbt', 'schem']:
            assert sha(folder / 'w03' / (manifest['name'] + '.' + ext)) == verification['nbt_schem_sha256'][ext]
    save(OUT / '指向与分布核验.json', dict(passed=True, aiming=m['aiming'], spears=m['spears'],
        crystal_cloud=m['crystal_cloud'], crystals=m['cubes'], viewer_qa=qa,
        no_independent_component_overlap=True, historical_c3_exports_unchanged=True))
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 C4 · 五环锁芯与立体晶云</title>
<style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{background:#111c2c;color:#ece5f5;font:16px/1.8 system-ui;margin:0}}main{{max-width:1450px;padding:24px;margin:auto}}a{{color:#d6b9ff}}h1{{margin:6px 0}}.note{{padding:14px 18px;border-left:3px solid #bda0ed;background:#253046}}nav{{display:flex;gap:20px;flex-wrap:wrap;margin:20px 0}}img{{display:block;width:100%;height:auto}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}figure{{margin:0;background:#1e2a3c;border-radius:10px;overflow:hidden}}figcaption{{padding:10px 16px}}small{{color:#bca4dc}}@media(max-width:800px){{.grid{{grid-template-columns:1fr}}h1{{font-size:26px}}main{{padding:15px}}}}</style>
<main><small>HK3GTL / W03 / C4 / 2026-11-08</small><h1>穹界·虚数锚定环 · 五环锁芯与立体晶云</h1>
<p class="note">沿用五环向上方案。六柄亚空之矛从前后左右下方向同一核心汇聚，矛尖与矛尾的轴线均穿过核心。24颗不同大小的浓缩崩坏能晶体散布于环下方空间，其中10颗进入基座中央坑内及上空；前后左右、高低错落。</p>
<nav><a href="w03/三维评审.html">打开完整三维预览</a><a href="六矛指向.png">六矛共同指向核心</a><a href="侧面晶云.png">侧面晶体分布</a><a href="俯视分布.png">俯视晶体分布</a><a href="W03-C4-完整预览与结构.zip">下载完整离线包</a></nav>
<p>三维预览右下角可切换“显示六矛指向线”，从侧面、俯视核对共同目标。指向线是预览辅助，不加入建筑方块。</p>
<figure><img src="完整预览.png" alt="五环、指向核心的六矛和基座中央上空的立体晶云"><figcaption>实际609×529×636（宽×深×高），{m['blocks']:,}实体方块，15种材料。</figcaption></figure>
<section class="grid"><figure><img src="侧面晶云.png" alt="精确侧视：六矛向核心倾斜，晶体分散在中央纵深"><figcaption>精确侧面：晶体覆盖中央纵深与下部空腔。</figcaption></figure><figure><img src="俯视分布.png" alt="俯视：六矛和晶体均有前后左右分布"><figcaption>俯视：六矛围绕核心，晶体分散在三维空间。</figcaption></figure></section>
<figure><img src="六矛指向.png" alt="六条真实矛轴的延长线汇聚于核心"><figcaption>矛尖、矛尾与核心的三维共线核对。</figcaption></figure>
<nav><a href="正面眼形.png">正面眼形</a><a href="侧面指向.png">侧面指向核对</a><a href="指向与分布核验.json">指向与分布核验</a><a href="verification.json">NBT／Schematic逐格回读</a><a href="manifest.json">坐标与材料信息</a><a href="../W03_C3_眼形莫比乌斯_四方案_20261108/index.html">历史C3四案</a><a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></nav>
<p>完整生成后按真实边界导出，独立构件无重叠。仍为待审外观候选，未部署、未作客户端实测；636格高度的普通主世界建高适配另验。</p></main></html>''', 'utf8')
    scripts = OUT / '生成脚本'
    for name in ['w03_core_aim_c4_20261108.py', 'build_w03_core_aim_c4_20261108.py',
                 'capture_w03_core_aim_c4_20261108.mjs', 'publish_w03_core_aim_c4_20261108.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, scripts / name)
    archive = OUT / 'W03-C4-完整预览与结构.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file() and p != archive: z.write(p, p.relative_to(OUT).as_posix())
    with zipfile.ZipFile(archive) as z: assert z.testzip() is None
    baseline = LOG / 'before-report'; baseline.mkdir(exist_ok=False)
    original = {p: p.read_bytes() for p in [REPORT / 'index.html', REPORT / 'current-summary.json']}
    for p, value in original.items(): (baseline / p.name).write_bytes(value)
    old = load(REPORT / 'current-summary.json'); data = deepcopy(old)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    state = '2026-11-08 · W03 C4：沿用负责人选定的五环向上方向，修正C3矛轴未在三维中对准核心、晶体排成双平面的问题。六柄矛真实矛尖—矛尾轴线均精确穿过同一核心；24颗晶体散入环下方的三维体积，其中10颗进入基座中央坑及其上空。609×529×636格、6,650,713块、15种材料；六视图、完整NBT／Schematic回读、实际体素轴线与独立构件零重叠核验通过。仍为未批准、未部署的外观候选；普通主世界建高适配与客户端实测另验。'
    work = data['current_work']; work['design_candidate_history'].append(deepcopy(work['design_candidate']))
    work['state'] = state
    work['next_turn'] = '审阅C4五环向上锁芯的三维矛向与立体晶云；已选修订方向不等于批准部署。'
    work['design_candidate'] = dict(id='W03', version='C4', title=m['title'],
        status='candidate_waiting_user_review', base_selected='C3-5U', approved=False, installed=False,
        game_verified=False, size_xyz=m['size'], blocks=m['blocks'], materials=m['unique_materials'],
        aiming=m['aiming'], crystal_cloud=m['crystal_cloud'],
        preview=str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/'),
        receipt=str((OUT / '指向与分布核验.json').relative_to(ROOT)).replace('\\', '/'),
        archive=str(archive.relative_to(ROOT)).replace('\\', '/'), archive_sha256=sha(archive),
        no_nominal_clipping=True, independent_overlap_pairs=0,
        standard_overworld_build_height_exceeded=True, updated_at=now)
    data['report_updated_at'] = now; data['systems'].sort(key=lambda s: s['percent'])
    assert data['systems'] == old['systems'] and data['overall_percent'] == old['overall_percent']
    assert data['multiblock_scope'] == old['multiblock_scope']
    for key in ['hyperion_performance', 'native_distance_and_package', 'approved_structure_designs', 'structure_batch']:
        assert work[key] == old['current_work'][key]
    html = original[REPORT / 'index.html'].decode('utf8')
    html, n = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + escape(now) + ' · W03 C4三维锁芯与立体晶云</p>', html, count=1); assert n == 1
    anchor = '<main><h1>系统完成度 · 低到高 · 固定入口</h1>'; assert anchor in html
    html = html.replace(anchor, anchor + '<p class="notice" id="w03-c4-current">' + escape(state) + ' <a href="../../deliveries/W03_C4_五环锁芯与立体晶云_20261108/index.html">C4完整预览与侧面核对</a></p>', 1)
    html, n = re.subn(r'(?<=id="audit-data">).*?(?=</script>)', lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S); assert n == 1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>', html, re.S)[1]) == data
    assert re.findall(r'<details class="system" data-id="([^"]+)"', html) == [s['id'] for s in data['systems']]
    publisher().publish_transaction({REPORT / 'index.html': html, REPORT / 'current-summary.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, original)
    rule = ROOT / 'rule/当前多方块设计规则.md'; shutil.copy2(rule, LOG / 'rule-before-c4.backup')
    note = '''

## 2026-11-08 W03 C4三维锁芯与立体晶云（负责人最新纠正）

- 负责人选定“五环向上刺矛”作为继续修改方向，明确六柄亚空之矛必须在三维中指向中央核心；侧面正交截图也是验收依据，不能仅让正面投影看似向内。
- C4保留五个莫比乌斯环、核心、基座、外围浮游柱与冠冕。六柄完整黑白橙矛从不同方位的下方向上汇聚；实际矛尖、矛尾、核心三个整数体素坐标严格共线，目标在矛尖正前方。只沿各自轴线定位以保留净空，不作破坏瞄准关系的横移。
- 负责人否定晶体双平面排墙，要求使用环下方与基座中央坑上空的空间。本轮24颗、8种大小保留；其中10颗进入中央坑及上空，14颗散入环下方；中心Y32–252，23种不同Z坐标，三维散布，无两层墙及等高行列。此最新空间要求优先于上一轮全部晶体限定在外环下方三分之一的摆法。
- 实际609×529×636格、6,650,713方块、15种材料；六张离线图、完整NBT／Schematic逐格回读、真实端点指向与独立构件零重叠核验通过。预览中可开关六矛指向辅助线，该辅助线不属于结构方块。
- C3历史四案与r219保留；本轮只选修订方向，未批准或部署。636格建高适配、客户端成型和运行另验；既定74项、批准57／正式52与36系统原分不变。
- 入口：deliveries/W03_C4_五环锁芯与立体晶云_20261108/index.html。
'''
    rule.write_bytes(rule.read_bytes() + note.encode('utf8'))
    result = dict(passed=True, actual_voxel_axis_miss_distance=0, central_lower_crystals=10,
        crystal_spatial_rank=3, screenshots=6, old_c3_exports_unchanged=True,
        scores_unchanged=36, overall_percent=data['overall_percent'], ascending_order=True,
        scope_and_r219_unchanged=True, archive_sha256=sha(archive),
        audit_summary_sha256=sha(REPORT / 'current-summary.json'), audit_html_sha256=sha(REPORT / 'index.html'))
    save(LOG / 'publication-verification.json', result); print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
