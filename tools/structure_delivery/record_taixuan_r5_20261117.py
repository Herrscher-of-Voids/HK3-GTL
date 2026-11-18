from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山中轴山门与松冠_T5_20261117'
LOG=ROOT/'logs/0005-w09-taixuan-t5-20261117'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    captures=json.loads((OUT/'预览记录.json').read_text('utf8'))
    w,h,d=manifest['sizeXYZ']
    item=dict(candidate='W09太虚山中轴山门与松冠T5',updated_at=now,approved=False,
        preview=OUT.relative_to(ROOT).as_posix()+'/index.html',
        previous_candidate=manifest['previous_candidate'],size_xyz=manifest['sizeXYZ'],
        blocks=manifest['total_blocks'],nbt=manifest['nbt'],sha256=manifest['nbt_sha256'],
        integer_voxels=True,materials=manifest['material_count'],changes=manifest['detail_changes'],
        gate_center=manifest['gate_center'],route=manifest['route'],pine_crowns_added=9,
        material_baseline='deliveries/0005_W09_太虚山扩岛嵌观_T4_20261117/materials.json',
        reconstruction='中轴山门、连接石径与岩脊属于负责人本轮要求的项目设计。',
        status='独立方块外观待审候选，W09整机组合后续设计。',
        evidence=LOG.relative_to(ROOT).as_posix()+'/completion.json')
    LOG.mkdir(exist_ok=True)
    history=LOG/('report-before-'+datetime.now().strftime('%H%M%S%f'))
    history.mkdir()
    for name in ['index.html','current-summary.json']:
        shutil.copy2(REPORT/name,history/name)
    summary=json.loads((REPORT/'current-summary.json').read_text('utf-8-sig'))
    summary['current_work']['w09_taixuan_t5_0005']=item
    system=next(s for s in summary['systems'] if s['id']=='multiblocks')
    system['w09_taixuan_t5_0005']=item
    system['updated_at']=now
    summary['report_updated_at']=now
    summary['systems'].sort(key=lambda s:s['percent'])
    html=(REPORT/'index.html').read_text('utf8')
    notice=f'''
<section class="notice" id="w09-taixuan-t5-0005">
<h2>0005 · W09太虚山中轴山门与松冠T5</h2>
<p>山门移至(0,160,164)，与主殿、八卦台同轴；补门前直行石径及折返山阶。
东侧断桥、人工桥头和沿溪断头石路已删除；九棵松树各补中央扁冠。</p>
<p>实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']:,}实体方块，
已保存{len(captures['captures'])}张方块预览，使用T4原像素材质。</p>
<p><a href="../../{item['preview']}">打开T5方块模型</a> ·
<a href="../0005-w09-taixuan-t5-20261117/completion.json">交付回执</a></p>
<p>独立外观待审，原评分与批准数量保持。</p></section>
'''
    html=re.sub(r'<section class="notice" id="w09-taixuan-t5-0005">.*?</section>','',html,flags=re.S)
    html=html.replace('<body>','<body>'+notice,1)
    html=re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,flags=re.S)
    save(REPORT/'current-summary.json',summary)
    (REPORT/'index.html').write_text(html,'utf8')
    save(LOG/'completion.json',dict(updated_at=now,delivery=item,
        preview=dict(captures=len(captures['captures']),errors=captures['errors'],failed=captures['failed'],
            inspected=['all-axis.png','all-gate_detail.png','all-route.png','all-creek.png',
                'trees-pine.png','trees-all_pines.png','trees-top.png','all-oblique.png']),
        artifact_stage='独立方块中轴山门与松冠候选',jar_built=False,installed=False,game_operated=False,
        scores_changed=False,approval_count_changed=False,overall_percent=summary['overall_percent'],
        multiblocks_percent=system['percent'],report_history=history.relative_to(ROOT).as_posix()))
    block=f'''

## 2026-11-17 对话0005：W09太虚山中轴山门与松冠T5

- 负责人指出山门斜放、偏离八卦台走线，东侧石桥断头及多棵松树缺树顶。明确要求山门摆至八卦台前中轴，找不到对岸依据可直接删桥，并补齐树冠。
- T5山门中心固定(0,160,164)，沿X展开，正对主殿与八卦台；八卦台前补短径，门前直行下坡后接折返山阶，上段岩脊随路重接。竹丛移至路外岩肩，按实际地形落根。
- 东侧桥体、人工桥头岩台及沿溪断头石路退出，保留水道和瀑布。九棵松树各补主干顶中央扁冠，覆盖裸露枝梢并接原叶簇。
- 入口 `deliveries/{OUT.name}/index.html`；真实整数格与完整NBT实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']}实体方块，沿用T4原像素材质。门位、路线和补冠属于项目设计，T4保留历史，T5独立待审。
- 回执 `logs/{LOG.name}/completion.json`；无JAR、安装或游戏操作，原评分与批准数量保持，W07继续停止。
'''
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:
        with (ROOT/name).open('a',encoding='utf8') as handle:
            handle.write(block)
    shutil.copy2(Path(__file__),OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(dict(preview=item['preview'],blocks=item['blocks'],size_xyz=item['size_xyz'],
        overall_percent=summary['overall_percent'],multiblocks_percent=system['percent']),ensure_ascii=False))


if __name__=='__main__':
    main()
