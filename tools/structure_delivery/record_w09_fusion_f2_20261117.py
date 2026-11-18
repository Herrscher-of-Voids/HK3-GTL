from datetime import datetime, timezone
from html import escape
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_T9与S2山观兵装矩阵_F2_20261117'
LOG = ROOT / 'logs/0005-w09-fusion-f2-20261117'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    now = datetime.now(timezone.utc).isoformat()
    manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
    captures = json.loads((OUT / '预览记录.json').read_text('utf8'))
    LOG.mkdir(parents=True, exist_ok=True)
    paths = [REPORT / 'index.html', REPORT / 'current-summary.json',
             ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md']
    previous = {p: p.read_bytes() for p in paths}
    history = LOG / ('report-before-' + datetime.now().strftime('%Y%m%d_%H%M%S%f') + '.zip')
    with ZipFile(history, 'w', ZIP_DEFLATED, compresslevel=6) as archive:
        for path, content in previous.items():
            archive.writestr(path.relative_to(ROOT).as_posix(), content)
    with ZipFile(history) as archive:
        restored = {path: archive.read(path.relative_to(ROOT).as_posix()) for path in paths}
    if any(previous[path] != restored[path] for path in paths):
        raise IOError('固定报告与规则ZIP备份回读不一致')
    backup = dict(path=history.relative_to(ROOT).as_posix(), compression='ZIP_DEFLATED',
        sha256=hashlib.sha256(history.read_bytes()).hexdigest(), bytes=history.stat().st_size,
        original_bytes=sum(map(len, previous.values())), readback_confirmed=True,
        files=[dict(path=p.relative_to(ROOT).as_posix(), bytes=len(previous[p]),
            sha256=hashlib.sha256(previous[p]).hexdigest(),
            readback_sha256=hashlib.sha256(restored[p]).hexdigest()) for p in paths])
    item = {key: manifest[key] for key in ['sizeXYZ', 'bounds', 'total_blocks',
        'part_block_sum', 'material_count', 'unique_block_types', 'scale_comparison', 'nbt', 'nbt_sha256', 'machine', 'controller', 'placements',
        'sources', 'design', 'conflicts', 'parts']}
    item.update(candidate='W09 T9与S2山观兵装矩阵F2', updated_at=now, approved=False,
        authorization='负责人：try it',
        component_status=dict(T9='组件外观已采用', S2='本轮指定融合来源'),
        preview=OUT.relative_to(ROOT).as_posix() + '/index.html',
        manifest=OUT.relative_to(ROOT).as_posix() + '/manifest.json',
        integer_voxels=True, block_count_scope='total_blocks为去重实体格，part_block_sum为分件数量合计',
        status='独立全整数格外观候选，W09整机外观待审，正式几何待接入',
        production='沿用W09的CEV、RN-CKV与现有真实工艺',
        interface_rule='仅唯一主控固定，其余全部实体格可替换合法通用接口，朝向自选',
        visual_review=dict(views=['oblique','front','core','industry','fan','court','controller','creek'],
            findings=['四处岛撑接触T9岩体，剑枪、链刃与兵匣承托已按S2实际截面补接。',
                '核心固定排位与山腹、约束圈及下层矩阵分离；未来运动按约166格完整方块球包络规划。',
                '五项规模中四项超过低电压正式结构；方块种类34，需达到59及以上。']),
        source_manifests_changed=False, formal_geometry_integrated=False,
        evidence=LOG.relative_to(ROOT).as_posix() + '/completion.json')
    summary = json.loads(previous[REPORT / 'current-summary.json'].decode('utf-8-sig'))
    system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
    summary['current_work']['w09_fusion_f2_0005'] = item
    system['w09_fusion_f2_0005'] = item
    system['updated_at'] = now
    summary['report_updated_at'] = now
    summary['systems'].sort(key=lambda s: s['percent'])
    w, h, d = manifest['sizeXYZ']
    notice = f'''
<section class="notice" id="w09-fusion-f2-0005">
<h2>0005 · W09 T9与S2山观兵装矩阵F2</h2>
<p>负责人以try it授权制作第一稿。T9组件外观已采用，S2为指定兵装来源；F2为独立全整数格外观候选。</p>
<p>实际宽{w}×深{d}×高{h}格，{manifest['total_blocks']:,}去重实体格，
分件合计{manifest['part_block_sum']:,}格，{manifest['unique_block_types']}种方块ID／{manifest['material_count']}种状态，{len(manifest['parts'])}构件，
保存{len(captures['captures'])}张预览。摆位、来源和已知待审冲突均按最新manifest记录。</p>
<p>五项规模中四项超过低电压正式结构；当前34种方块ID，种类递增要求为59种及以上，列为待修订项。</p>
<p>主控方案：<code>{escape(json.dumps(manifest['controller'], ensure_ascii=False))}</code>。
其余全部实体格可替换合法通用接口，朝向自选。CEV、RN-CKV及现有工艺沿用，正式几何尚未接入。</p>
<p><a href="../../{item['preview']}">打开F2方块候选</a> ·
<a href="../../{item['manifest']}">来源与冲突记录</a> ·
<a href="../{LOG.name}/completion.json">本轮回执</a></p>
<p>原评分、机器批准计数与正式结构数量保持。</p></section>
'''
    html = previous[REPORT / 'index.html'].decode('utf8')
    html = re.sub(r'<section class="notice" id="w09-fusion-f2-0005">.*?</section>', '', html, flags=re.S)
    html = html.replace('<body>', '<body>' + notice, 1)
    html = re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _: json.dumps(summary, ensure_ascii=False).replace('<', '\\u003c'), html, flags=re.S)
    save(LOG / 'completion.json', dict(updated_at=now, delivery=item, report_backup=backup,
        preview=dict(captures=len(captures['captures']), errors=captures['errors'],
            failed=captures['failed'], recorded=[c['file'] for c in captures['captures']],
            record=OUT.relative_to(ROOT).as_posix() + '/预览记录.json'),
        jar_built=False, installed=False, instance_operated=False, desktop_operated=False,
        game_operated=False, scores_changed=False, approval_count_changed=False,
        formal_structure_count_changed=False, formal_geometry_integrated=False,
        overall_percent=summary['overall_percent'], multiblocks_percent=system['percent']))
    save(REPORT / 'current-summary.json', summary)
    (REPORT / 'index.html').write_text(html, 'utf8')
    block = f'''

## 2026-11-17 对话0005：W09 T9与S2山观兵装矩阵F2

- 负责人以“try it”授权制作W09融合第一稿。T9组件外观已采用，S2为本轮指定兵装来源；原T9与S2来源保留原样。
- F2为独立全整数格外观待审候选，入口`{item['preview']}`。实际宽{w}×深{d}×高{h}格，{manifest['total_blocks']}去重实体格、分件合计{manifest['part_block_sum']}格、{manifest['unique_block_types']}种方块ID／{manifest['material_count']}种状态、{len(manifest['parts'])}构件，保存{len(captures['captures'])}张预览；五项规模实际比较保存在manifest。
- 摆位、主控方案、来源、设计与已知待审冲突读取最新manifest，完整回执为`{item['evidence']}`。W09沿用CEV、RN-CKV及现有真实工艺；正式几何尚未接入，F2不计作整机批准或新增正式结构。
- 仅唯一主控位置固定，其余全部实体格可替换合法通用接口，位置与朝向由玩家选择。固定报告及两份规则更新前已直接ZIP压缩备份并回读确认，原文件和ZIP的大小、SHA-256记录于回执。
- 固定报告合并本轮证据并按percent排序；原评分、批准计数、正式结构数量与其他对话记录保持。本轮无JAR、安装、实例、桌面或游戏操作，W07继续停止。
'''
    for name in ['AGENTS.md', 'rule/当前多方块设计规则.md']:
        with (ROOT / name).open('a', encoding='utf8') as handle:
            handle.write(block)
    print(json.dumps(dict(preview=item['preview'], receipt=item['evidence']), ensure_ascii=False))


if __name__ == '__main__':
    main()
