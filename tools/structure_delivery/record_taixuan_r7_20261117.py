from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil

from record_taixuan_r6_20261117 import ROOT, REPORT, save


OUT=ROOT/'deliveries/0005_W09_太虚山紫线直落瀑布_T7_20261117'
LOG=ROOT/'logs/0005-w09-taixuan-t7-20261117'


def main():
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    captures=json.loads((OUT/'预览记录.json').read_text('utf8'))
    w,h,d=manifest['sizeXYZ']
    item=dict(candidate='W09太虚山紫线直落瀑布T7',updated_at=now,approved=False,
        preview=OUT.relative_to(ROOT).as_posix()+'/index.html',
        previous_candidate=manifest['previous_candidate'],size_xyz=manifest['sizeXYZ'],
        blocks=manifest['total_blocks'],nbt=manifest['nbt'],sha256=manifest['nbt_sha256'],
        integer_voxels=True,materials=manifest['material_count'],changes=manifest['detail_changes'],
        water_parameters=manifest['water_parameters'],peak_centers=manifest['peak_centers'],
        gate_center=manifest['gate_center'],route=manifest['route'],
        material_baseline='deliveries/0005_W09_太虚山远峰弧廊与溪谷_T6_20261117/materials.json',
        retained=['T6建筑','T6远峰','T6树位','T6院坪'],
        reconstruction='紫线跌瀑边及配套岩床岸坡属于负责人标注后的项目改造。',
        status='独立方块外观待审候选，W09整机组合后续设计。',
        evidence=LOG.relative_to(ROOT).as_posix()+'/completion.json')
    LOG.mkdir(exist_ok=True)
    history=LOG/('report-before-'+datetime.now().strftime('%H%M%S%f'))
    history.mkdir()
    for name in ['index.html','current-summary.json']:
        shutil.copy2(REPORT/name,history/name)
    summary=json.loads((REPORT/'current-summary.json').read_text('utf-8-sig'))
    summary['current_work']['w09_taixuan_t7_0005']=item
    system=next(s for s in summary['systems'] if s['id']=='multiblocks')
    system['w09_taixuan_t7_0005']=item
    system['updated_at']=now
    summary['report_updated_at']=now
    summary['systems'].sort(key=lambda s:s['percent'])
    html=(REPORT/'index.html').read_text('utf8')
    notice=f'''
<section class="notice" id="w09-taixuan-t7-0005">
<h2>0005 · W09太虚山紫线直落瀑布T7</h2>
<p>按负责人紫线，将水道外沿改为直接垂入云海的跌瀑边；取消下游回弯及原X204、Z-8单口瀑布，
岩床与岸坡按新水道重建。T6建筑、远峰、树位和院坪沿用。</p>
<p>实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']:,}实体方块，
保存{len(captures['captures'])}张预览；上瀑、短溪节点及跌瀑边实际参数见回执。</p>
<p><a href="../../{item['preview']}">打开T7方块模型</a> ·
<a href="../0005-w09-taixuan-t7-20261117/completion.json">交付回执</a></p>
<p>独立外观待审，原评分与批准数量保持。</p></section>
'''
    html=re.sub(r'<section class="notice" id="w09-taixuan-t7-0005">.*?</section>','',html,flags=re.S)
    html=html.replace('<body>','<body>'+notice,1)
    html=re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,flags=re.S)
    save(REPORT/'current-summary.json',summary)
    (REPORT/'index.html').write_text(html,'utf8')
    save(LOG/'completion.json',dict(updated_at=now,delivery=item,
        preview=dict(captures=len(captures['captures']),errors=captures['errors'],failed=captures['failed'],
            recorded=[capture['file'] for capture in captures['captures']]),
        artifact_stage='独立方块紫线直落瀑布候选',jar_built=False,installed=False,game_operated=False,
        scores_changed=False,approval_count_changed=False,overall_percent=summary['overall_percent'],
        multiblocks_percent=system['percent'],report_history=history.relative_to(ROOT).as_posix()))
    block=f'''

## 2026-11-17 对话0005：W09太虚山紫线直落瀑布T7

- 负责人以紫线指定水道外沿直接垂入云海，T7据此建立连续跌瀑边，取消下游回弯及原X204、Z-8单口瀑布。
- 岩床与岸坡随新水道重建；上瀑、短溪节点和跌瀑边参数读取候选manifest的`water_parameters`，完整记录于交付回执。T6建筑、远峰、树位、院坪及原像素材质沿用。
- 入口 `deliveries/{OUT.name}/index.html`，真实整数格与完整NBT实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']}实体方块。
- T6保留历史，T7独立待审。回执 `logs/{LOG.name}/completion.json`；无JAR、安装或游戏操作，原评分与批准数量保持，W07继续停止。
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
