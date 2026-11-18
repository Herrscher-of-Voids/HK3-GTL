from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_T9与S1融合摆位_F1_20261117'
T9 = ROOT / 'deliveries/0005_W09_太虚山紫线岩岸轮廓_T9_20261117'
S1 = ROOT / 'deliveries/0005_W09_识律三兵方块复刻_S1_20261116'
LOG = ROOT / 'logs/0005-w09-fusion-f1-20261117'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
QUOTE = '可以就用 T9吧，那么我们要怎么将 T9和 S1 融合在一起呢？，别忘了，我们还要变成 W09'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    now = datetime.now(timezone.utc).isoformat()
    manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
    captures = json.loads((OUT / '预览记录.json').read_text('utf8'))
    t9 = json.loads((T9 / 'manifest.json').read_text('utf8'))
    LOG.mkdir(parents=True, exist_ok=True)
    history = LOG / ('report-before-' + datetime.now().strftime('%Y%m%d_%H%M%S%f') + '.zip')
    paths = [REPORT / 'index.html', REPORT / 'current-summary.json',
             ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md']
    previous = {path: path.read_bytes() for path in paths}
    with ZipFile(history, 'w', ZIP_DEFLATED, compresslevel=6) as archive:
        for path, content in previous.items():
            archive.writestr(path.relative_to(ROOT).as_posix(), content)
    with ZipFile(history) as archive:
        for name in archive.namelist():
            archive.read(name)
    backup = dict(path=history.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(history.read_bytes()).hexdigest(),
        original_bytes=sum(map(len, previous.values())), compressed_bytes=history.stat().st_size,
        files=[dict(path=path.relative_to(ROOT).as_posix(), bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest()) for path, content in previous.items()])
    approval_path = LOG / 't9-component-approval.json'
    approval = dict(recorded_at=now, conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
        user_quote=QUOTE, component='W09太虚山T9', approved=True,
        approval_scope='T9组件外观正式采用，作为W09融合来源',
        source_manifest=(T9 / 'manifest.json').relative_to(ROOT).as_posix(),
        source_preview=(T9 / 'index.html').relative_to(ROOT).as_posix(),
        nbt=(T9 / t9['nbt']).relative_to(ROOT).as_posix(),
        nbt_sha256=hashlib.sha256((T9 / t9['nbt']).read_bytes()).hexdigest(),
        size_xyz=t9['sizeXYZ'], blocks=t9['total_blocks'], materials=t9['material_count'],
        source_manifest_changed=False, s1_status='本轮负责人指定融合来源',
        whole_machine_approved=False, machine_approval_count_changed=False,
        formal_blueprint_status_changed=False,
        evidence=LOG.relative_to(ROOT).as_posix() + '/completion.json')
    item = dict(candidate='W09 T9与S1融合摆位研究F1', updated_at=now,
        approved=False, user_quote=QUOTE, machine=manifest['machine'],
        preview=OUT.relative_to(ROOT).as_posix() + '/index.html',
        source_manifest=OUT.relative_to(ROOT).as_posix() + '/manifest.json',
        sources=dict(T9=(T9 / 'manifest.json').relative_to(ROOT).as_posix(),
            S1=(S1 / 'manifest.json').relative_to(ROOT).as_posix()),
        component_approval=dict(T9=approval_path.relative_to(ROOT).as_posix(),
            S1='本轮负责人指定融合来源'),
        size_xyz=manifest['sizeXYZ'], bounds=manifest['bounds'],
        blocks=manifest['total_blocks'], block_count_scope='manifest各组件方块数合计',
        materials=manifest['material_count'], integer_voxels=True,
        models=manifest['models'], placement=manifest['recipe'],
        controller_proposal=manifest['controller'], interface_rule=manifest['interface_rule'],
        design=manifest['design'],
        status='组件比例与摆位研究，整机外观待设计',
        pending=['岛腹数据读写工业层', '认知载体制造工业层', '共识档案汇聚工业层',
                 '正式规模与电压递增核定', '整机穿模处理', '动态演出', '最终主控位置'],
        formal_blueprint_status_changed=False,
        evidence=LOG.relative_to(ROOT).as_posix() + '/completion.json')
    summary = json.loads(previous[REPORT / 'current-summary.json'].decode('utf-8-sig'))
    system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
    records = dict(w09_taixuan_t9_adoption_0005=approval, w09_fusion_f1_0005=item)
    summary['current_work'].update(records)
    system.update(records)
    system['updated_at'] = now
    summary['report_updated_at'] = now
    summary['systems'].sort(key=lambda s: s['percent'])
    w, h, d = manifest['sizeXYZ']
    notice = f'''
<section class="notice" id="w09-fusion-f1-0005">
<h2>0005 · T9组件采用与W09融合摆位F1</h2>
<p>负责人正式采用T9山体组件，并指定S1武器作为本轮融合来源。T9独立批准JSON记录原NBT的SHA-256，原候选manifest保留历史状态。</p>
<p>F1保留T9完整山观，剑枪分立前侧、武器匣居后、链刃横置前方低云。
实际宽{w}×深{d}×高{h}格，组件方块合计{manifest['total_blocks']:,}，{manifest['material_count']}种材质，保存{len(captures['captures'])}张预览。</p>
<p>本轮用于讨论组件比例与摆位。岛腹数据读写、认知载体制造、共识档案汇聚工业层、正式规模与动态尚未制作。
唯一主控建议位置为(0,163,138)，其余全部实体格可替换合法通用接口，朝向自选。</p>
<p><a href="../../{item['preview']}">打开F1融合摆位</a> ·
<a href="../{LOG.name}/t9-component-approval.json">T9组件批准</a> ·
<a href="../{LOG.name}/completion.json">本轮回执</a></p>
<p>CEV、RN-CKV与既有工艺沿用。F1处于整机设计阶段，原评分、机器批准计数与正式蓝图状态保持。</p></section>
'''
    html = previous[REPORT / 'index.html'].decode('utf8')
    html = re.sub(r'<section class="notice" id="w09-fusion-f1-0005">.*?</section>', '', html, flags=re.S)
    html = html.replace('<body>', '<body>' + notice, 1)
    html = re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _: json.dumps(summary, ensure_ascii=False).replace('<', '\\u003c'), html, flags=re.S)
    receipt = dict(updated_at=now, user_quote=QUOTE, t9_component_approval=approval,
        delivery=item, preview=dict(captures=len(captures['captures']),
            errors=captures['errors'], failed=captures['failed'],
            recorded=[capture['file'] for capture in captures['captures']],
            record=OUT.relative_to(ROOT).as_posix() + '/预览记录.json'),
        artifact_stage='T9与S1组件比例和摆位研究', report_backup=backup,
        jar_built=False, installed=False, instance_operated=False, desktop_operated=False,
        game_operated=False, scores_changed=False, machine_approval_count_changed=False,
        formal_blueprint_status_changed=False,
        overall_percent=summary['overall_percent'], multiblocks_percent=system['percent'])
    save(approval_path, approval)
    save(LOG / 'completion.json', receipt)
    save(REPORT / 'current-summary.json', summary)
    (REPORT / 'index.html').write_text(html, 'utf8')
    block = f'''

## 2026-11-17 对话0005：T9组件采用与W09融合摆位F1

- 负责人原话：“{QUOTE}”。T9组件外观正式采用，S1为本轮指定融合来源；W09整机外观与正式蓝图状态保持待设计。独立批准记录为`{approval_path.relative_to(ROOT).as_posix()}`，包含T9现有NBT的SHA-256；原T9与S1候选及manifest保留原样。
- 独立入口`{item['preview']}`，仅组合T9完整山观、S1剑枪、武器匣、低位横置链刃与主控标记，用于组件比例和摆位讨论。实际宽{w}×深{d}×高{h}格，组件方块合计{manifest['total_blocks']}，{manifest['material_count']}种材质；实际摆位、源坐标、变换与{len(captures['captures'])}张预览记录见`{LOG.relative_to(ROOT).as_posix()}/completion.json`。
- 岛腹的数据读写、认知载体制造与共识档案汇聚工业层、正式规模及动态尚未制作；CEV、RN-CKV和既有真实工艺沿用。F1不计作整机批准或正式蓝图接入。
- 唯一主控建议坐标为`[0,163,138]`，红石仅用于建议位置标记；其余全部实体格可由玩家替换合法通用接口，自选位置与朝向。
- 固定报告更新前保存启用压缩的ZIP备份，再合并本轮证据并按percent排序；原评分、机器批准计数与正式蓝图状态保持。本轮无JAR、安装、实例、桌面或游戏操作，W07继续停止。
'''
    for name in ['AGENTS.md', 'rule/当前多方块设计规则.md']:
        with (ROOT / name).open('a', encoding='utf8') as handle:
            handle.write(block)
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    print(json.dumps(dict(preview=item['preview'], receipt=item['evidence'],
        t9_approval=approval_path.relative_to(ROOT).as_posix()), ensure_ascii=False))


if __name__ == '__main__':
    main()
