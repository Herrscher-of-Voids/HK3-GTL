from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山扩岛嵌观_T4_20261117'
LOG=ROOT/'logs/0005-w09-taixuan-t4-20261117'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    captures=json.loads((OUT/'预览记录.json').read_text('utf8'))
    w,h,d=manifest['sizeXYZ']
    item=dict(candidate='W09太虚山扩岛嵌观T4',updated_at=now,approved=False,
        preview=OUT.relative_to(ROOT).as_posix()+'/index.html',
        previous_candidate=manifest['previous_candidate'],
        size_xyz=manifest['sizeXYZ'],blocks=manifest['total_blocks'],
        nbt=manifest['nbt'],sha256=manifest['nbt_sha256'],
        integer_voxels=True,materials=manifest['material_count'],
        changes=manifest['detail_changes'][-3:],
        material_baseline='deliveries/0005_W09_太虚山岩坪衔接_T3_20261117/materials.json',
        reconstruction='主岛外扩、草坡、岩肩与嵌地形态为负责人本轮要求的项目设计。',
        status='独立方块外观待审候选，W09整机组合后续设计。',
        evidence=LOG.relative_to(ROOT).as_posix()+'/completion.json')
    LOG.mkdir(exist_ok=True)
    history=LOG/('report-before-'+datetime.now().strftime('%H%M%S%f'))
    history.mkdir()
    for name in ['index.html','current-summary.json']:
        shutil.copy2(REPORT/name,history/name)
    summary=json.loads((REPORT/'current-summary.json').read_text('utf-8-sig'))
    summary['current_work']['w09_taixuan_t4_0005']=item
    system=next(s for s in summary['systems'] if s['id']=='multiblocks')
    system['w09_taixuan_t4_0005']=item
    system['updated_at']=now
    summary['report_updated_at']=now
    summary['systems'].sort(key=lambda s:s['percent'])
    html=(REPORT/'index.html').read_text('utf8')
    notice=f'''
<section class="notice" id="w09-taixuan-t4-0005">
<h2>0005 · W09太虚山扩岛嵌观T4</h2>
<p>按负责人要求扩大主岛，院坪外留不规则草坡与岩肩，浅色地台基础嵌入岛面。
从Y58起同步加宽岩腹，向原岛底渐收；水道、瀑布出口与上山石阶保留通行空间。</p>
<p>实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']:,}实体方块，
已保存{len(captures['captures'])}张三维预览。建筑原坐标及T3像素材质沿用。</p>
<p><a href="../../{item['preview']}">打开T4方块模型</a> ·
<a href="../0005-w09-taixuan-t4-20261117/completion.json">交付回执</a></p>
<p>独立外观待审，原评分与批准数量保持。</p></section>
'''
    html=re.sub(r'<section class="notice" id="w09-taixuan-t4-0005">.*?</section>','',html,flags=re.S)
    html=html.replace('<body>','<body>'+notice,1)
    html=re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,flags=re.S)
    save(REPORT/'current-summary.json',summary)
    (REPORT/'index.html').write_text(html,'utf8')
    save(LOG/'completion.json',dict(updated_at=now,delivery=item,
        preview=dict(captures=len(captures['captures']),errors=captures['errors'],failed=captures['failed'],
            inspected=['all-oblique.png','all-top.png','all-base_front.png','all-base_side.png',
                'all-court.png','all-bridge.png','all-gate_detail.png']),
        artifact_stage='独立方块扩岛嵌观候选',jar_built=False,installed=False,game_operated=False,
        scores_changed=False,approval_count_changed=False,overall_percent=summary['overall_percent'],
        multiblocks_percent=system['percent'],report_history=history.relative_to(ROOT).as_posix()))
    block=f'''

## 2026-11-17 对话0005：W09太虚山扩岛嵌观T4

- 负责人确认T3空层已接好，继续指出院坪比下部岩体大、贴边切崖生硬；明确要求扩大岛体，将建筑嵌到岛上。
- T4扩展主岛的不规则草岩肩，院坪基础埋入岛面；侧后坡局部起伏，岩腹从Y58起同步加宽，渐收回原岛底。上山路径按原路高留低鞍，河道削至水面以下，东侧瀑布另留向外开放的崖湾。主殿、庭院及其他既有建筑坐标沿用，方块材质直接复用T3原像素材质。
- 入口 `deliveries/{OUT.name}/index.html`；真实整数格及完整NBT实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']}实体方块。29张预览已保存，已目视斜视、俯视、正侧面、庭院、溪桥和山门衔接。
- 扩岛与嵌地为负责人本轮要求的项目设计，T3保留历史，T4独立待审。回执 `logs/{LOG.name}/completion.json`；无JAR、安装或游戏操作，原评分与批准数量保持，W07继续停止。
'''
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:
        with (ROOT/name).open('a',encoding='utf8') as handle:
            handle.write(block)
    shutil.copy2(Path(__file__),OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(dict(preview=item['preview'],blocks=item['blocks'],size_xyz=item['size_xyz'],
        overall_percent=summary['overall_percent'],multiblocks_percent=system['percent']),ensure_ascii=False))


if __name__=='__main__':
    main()
