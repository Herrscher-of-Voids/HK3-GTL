from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山远峰弧廊与溪谷_T6_20261117'
LOG=ROOT/'logs/0005-w09-taixuan-t6-20261117'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    captures=json.loads((OUT/'预览记录.json').read_text('utf8'))
    w,h,d=manifest['sizeXYZ']
    item=dict(candidate='W09太虚山远峰弧廊与溪谷T6',updated_at=now,approved=False,
        preview=OUT.relative_to(ROOT).as_posix()+'/index.html',
        previous_candidate=manifest['previous_candidate'],size_xyz=manifest['sizeXYZ'],
        blocks=manifest['total_blocks'],nbt=manifest['nbt'],sha256=manifest['nbt_sha256'],
        integer_voxels=True,materials=manifest['material_count'],changes=manifest['detail_changes'],
        peak_centers=manifest['peak_centers'],gate_center=manifest['gate_center'],route=manifest['route'],
        material_baseline='deliveries/0005_W09_太虚山中轴山门与松冠_T5_20261117/materials.json',
        reconstruction='远峰、弧廊和溪谷属于负责人标注后的项目改造。',
        status='独立方块外观待审候选，W09整机组合后续设计。',
        evidence=LOG.relative_to(ROOT).as_posix()+'/completion.json')
    LOG.mkdir(exist_ok=True)
    history=LOG/('report-before-'+datetime.now().strftime('%H%M%S%f'))
    history.mkdir()
    for name in ['index.html','current-summary.json']:
        shutil.copy2(REPORT/name,history/name)
    summary=json.loads((REPORT/'current-summary.json').read_text('utf-8-sig'))
    summary['current_work']['w09_taixuan_t6_0005']=item
    system=next(s for s in summary['systems'] if s['id']=='multiblocks')
    system['w09_taixuan_t6_0005']=item
    system['updated_at']=now
    summary['report_updated_at']=now
    summary['systems'].sort(key=lambda s:s['percent'])
    html=(REPORT/'index.html').read_text('utf8')
    notice=f'''
<section class="notice" id="w09-taixuan-t6-0005">
<h2>0005 · W09太虚山远峰弧廊与溪谷T6</h2>
<p>外围独立峰向外推开，错位岩肩与收尖峰顶替换等粗崖壁；瀑布峰经低岩肩、浅潭和弯溪接回主岛。
西后廊改为连续弧形，穿廊古松移到廊外，院坪按真实地板顶面清除高草岩。</p>
<p>实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']:,}实体方块，
保存{len(captures['captures'])}张预览；使用T5原像素材质。</p>
<p><a href="../../{item['preview']}">打开T6方块模型</a> ·
<a href="../0005-w09-taixuan-t6-20261117/completion.json">交付回执</a></p>
<p>独立外观待审，原评分与批准数量保持。</p></section>
'''
    html=re.sub(r'<section class="notice" id="w09-taixuan-t6-0005">.*?</section>','',html,flags=re.S)
    html=html.replace('<body>','<body>'+notice,1)
    html=re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,flags=re.S)
    save(REPORT/'current-summary.json',summary)
    (REPORT/'index.html').write_text(html,'utf8')
    save(LOG/'completion.json',dict(updated_at=now,delivery=item,
        preview=dict(captures=len(captures['captures']),errors=captures['errors'],failed=captures['failed'],
            inspected=['all-oblique.png','all-axis.png','all-arc.png','all-floor.png','all-creek.png',
                'all-peaks.png','gallery-connection.png','trees-pine.png','waterfall-fall.png']),
        artifact_stage='独立方块远峰弧廊与溪谷候选',jar_built=False,installed=False,game_operated=False,
        scores_changed=False,approval_count_changed=False,overall_percent=summary['overall_percent'],
        multiblocks_percent=system['percent'],report_history=history.relative_to(ROOT).as_posix()))
    block=f'''

## 2026-11-17 对话0005：W09太虚山远峰弧廊与溪谷T6

- 负责人标注外围山峰靠主岛过近而不相连、长段等粗崖壁、西廊穿树、后廊直角、水系生硬及门侧草岩侵入院坪地板，要求按标注修正。
- T6将六座独立外围峰向外推开留云隙，各峰补错位岩肩、变宽截面及收尖峰顶；瀑布峰外移后用低岩肩、山脚浅潭、弯曲溪谷和岛边下瀑接主岛，水床、岸坡和挖槽共用新水道。旧直槽及旧瀑布退出。
- 西后折廊改为半径42格连续弧廊，铺地、柱列、窗墙与曲檐一起转弯；西廊原松移至廊外草岩肩，东松移离主殿，五棵外峰松按新地表重新落根，九棵保留中央顶冠。
- 按院坪实际最高方块顶面压低地形，清除高草岩覆盖；原像素材质沿用T5。入口 `deliveries/{OUT.name}/index.html`，真实整数格与完整NBT实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']}实体方块。
- 本轮远峰、弧廊及溪谷为项目改造，T5保留历史，T6独立待审。回执 `logs/{LOG.name}/completion.json`；无JAR、安装或游戏操作，原评分与批准数量保持，W07继续停止。
'''
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:
        with (ROOT/name).open('a',encoding='utf8') as handle:
            handle.write(block)
    shutil.copy2(Path(__file__),OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(dict(preview=item['preview'],blocks=item['blocks'],size_xyz=item['size_xyz'],
        overall_percent=summary['overall_percent'],multiblocks_percent=system['percent']),ensure_ascii=False))


if __name__=='__main__':
    main()
