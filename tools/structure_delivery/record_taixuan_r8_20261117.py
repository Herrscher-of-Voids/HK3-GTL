from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil

from record_taixuan_r6_20261117 import ROOT, REPORT, save


OUT=ROOT/'deliveries/0005_W09_太虚山拐点直瀑与完整岩岸_T8_20261117'
LOG=ROOT/'logs/0005-w09-taixuan-t8-20261117'


def main():
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    captures=json.loads((OUT/'预览记录.json').read_text('utf8'))
    w,h,d=manifest['sizeXYZ']
    correction='T7将紫色外围动线误读为删除外岸并形成整片水帘；负责人明确要求保留岩岸，水在河道开始兜回的拐点集中下落。'
    item=dict(candidate='W09太虚山拐点直瀑与完整岩岸T8',updated_at=now,approved=False,
        preview=OUT.relative_to(ROOT).as_posix()+'/index.html',
        previous_candidate=manifest['previous_candidate'],size_xyz=manifest['sizeXYZ'],
        blocks=manifest['total_blocks'],nbt=manifest['nbt'],sha256=manifest['nbt_sha256'],
        integer_voxels=True,materials=manifest['material_count'],changes=manifest['detail_changes'],
        water_parameters=manifest['water_parameters'],peak_centers=manifest['peak_centers'],
        gate_center=manifest['gate_center'],route=manifest['route'],
        material_baseline='deliveries/0005_W09_太虚山远峰弧廊与溪谷_T6_20261117/materials.json',
        retained=['T6建筑','T6远峰','T6树位','T6院坪'],
        correction=correction,reconstruction='恢复完整外围岩岸与动线，撤销整片水帘，水道拐点采用集中窄瀑并取消后段回弯。',
        status='独立方块外观待审候选，W09整机组合后续设计。',
        evidence=LOG.relative_to(ROOT).as_posix()+'/completion.json')
    LOG.mkdir(exist_ok=True)
    history=LOG/('report-before-'+datetime.now().strftime('%H%M%S%f'))
    history.mkdir()
    for name in ['index.html','current-summary.json']:
        shutil.copy2(REPORT/name,history/name)
    summary=json.loads((REPORT/'current-summary.json').read_text('utf-8-sig'))
    system=next(s for s in summary['systems'] if s['id']=='multiblocks')
    for rejected in (summary['current_work']['w09_taixuan_t7_0005'],system['w09_taixuan_t7_0005']):
        rejected.update(status='rejected_by_user',rejected_by_user=True,replaced_by=item['preview'],
            replaced_at=now,rejection_reason=correction)
    summary['current_work']['w09_taixuan_t8_0005']=item
    system['w09_taixuan_t8_0005']=item
    system['updated_at']=now
    summary['report_updated_at']=now
    summary['systems'].sort(key=lambda s:s['percent'])
    html=(REPORT/'index.html').read_text('utf8')
    rejected_notice=f'''
<section class="notice" id="w09-taixuan-t7-0005">
<h2>0005 · W09太虚山T7已弃用</h2>
<p>{correction}T7原交付与回执保留历史，当前候选为T8。</p>
<p><a href="../../{item['preview']}">打开T8方块模型</a></p></section>
'''
    html=re.sub(r'<section class="notice" id="w09-taixuan-t7-0005">.*?</section>',
        lambda _:rejected_notice,html,flags=re.S)
    notice=f'''
<section class="notice" id="w09-taixuan-t8-0005">
<h2>0005 · W09太虚山拐点直瀑与完整岩岸T8</h2>
<p>恢复外围岩岸与动线，撤销T7整片水帘；在河道开始兜回的拐点设置集中窄瀑，取消后段回弯。
T6建筑、远峰、树位和院坪沿用。</p>
<p>实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']:,}实体方块，
保存{len(captures['captures'])}张预览；水道和直瀑参数读取候选manifest并记录于回执。</p>
<p><a href="../../{item['preview']}">打开T8方块模型</a> ·
<a href="../0005-w09-taixuan-t8-20261117/completion.json">交付回执</a></p>
<p>独立外观待审，原评分与批准数量保持。</p></section>
'''
    html=re.sub(r'<section class="notice" id="w09-taixuan-t8-0005">.*?</section>','',html,flags=re.S)
    html=html.replace('<body>','<body>'+notice,1)
    html=re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,flags=re.S)
    save(REPORT/'current-summary.json',summary)
    (REPORT/'index.html').write_text(html,'utf8')
    save(LOG/'completion.json',dict(updated_at=now,delivery=item,
        preview=dict(captures=len(captures['captures']),errors=captures['errors'],failed=captures['failed'],
            recorded=[capture['file'] for capture in captures['captures']]),
        artifact_stage='独立方块拐点直瀑与完整岩岸候选',jar_built=False,installed=False,game_operated=False,
        scores_changed=False,approval_count_changed=False,overall_percent=summary['overall_percent'],
        multiblocks_percent=system['percent'],report_history=history.relative_to(ROOT).as_posix()))
    block=f'''

## 2026-11-17 对话0005：W09太虚山拐点直瀑与完整岩岸T8

- 明确纠正T7记录：此前“负责人以紫线指定水道外沿直接垂入云海”为助手误读。负责人说明紫色表示外围动线，外围岩石与岸路应保留；水在“河道开始兜回的拐点”直接下落。
- T7因上述误读弃用，原交付与回执保留历史；固定报告中T7标记为`rejected_by_user`，由T8替代。
- T8恢复完整外围岩岸与动线，撤销整片水帘，在拐点建立集中窄瀑并取消后段回弯；实际水系参数及变更分别读取候选manifest的`water_parameters`和`detail_changes`，保存于回执。T6建筑、远峰、树位、院坪及原像素材质沿用。
- 入口 `deliveries/{OUT.name}/index.html`，真实整数格与完整NBT实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']}实体方块。
- T8独立待审。回执 `logs/{LOG.name}/completion.json`；无JAR、安装或游戏操作，原评分与批准数量保持，W07继续停止。
'''
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:
        with (ROOT/name).open('a',encoding='utf8') as handle:
            handle.write(block)
    shutil.copy2(Path(__file__),OUT/'生成脚本'/Path(__file__).name)
    shutil.copy2(ROOT/'tools/structure_delivery/record_taixuan_r6_20261117.py',
        OUT/'生成脚本/record_taixuan_r6_20261117.py')
    print(json.dumps(dict(preview=item['preview'],blocks=item['blocks'],size_xyz=item['size_xyz'],
        water_parameters=item['water_parameters'],overall_percent=summary['overall_percent'],
        multiblocks_percent=system['percent']),ensure_ascii=False))


if __name__=='__main__':
    main()
