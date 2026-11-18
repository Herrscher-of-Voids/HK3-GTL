from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil

from taixuan_common_20261116 import ROOT, OUT, REF


LOG=ROOT/'logs/0005-w09-taixuan-t1-20261116'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    LOG.mkdir(exist_ok=True)
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    refs=json.loads((REF/'参考清单.json').read_text('utf8'))
    captures=json.loads((OUT/'预览记录.json').read_text('utf8'))
    item=dict(candidate='W09完整拂云观与云海山体T1',updated_at=now,approved=False,
        preview=OUT.relative_to(ROOT).as_posix()+'/index.html',
        gallery=REF.relative_to(ROOT).as_posix()+'/index.html',
        references=refs['count'],reference_sources=refs['source_counts'],
        size_xyz=manifest['sizeXYZ'],blocks=manifest['total_blocks'],
        nbt=manifest['nbt'],sha256=manifest['nbt_sha256'],
        integer_voxels=True,materials=manifest['material_count'],
        visible_evidence='官方3.7完整训练场、角色指南、主线历史月夜、云海外景及7.2阶栏细节。',
        reconstruction=manifest['reconstruction'],
        status='独立外观待审候选，W09整机组合后续设计。',
        evidence=LOG.relative_to(ROOT).as_posix()+'/completion.json')
    history=LOG/('report-before-'+datetime.now().strftime('%H%M%S'))
    history.mkdir()
    for name in ['index.html','current-summary.json']:
        shutil.copy2(REPORT/name,history/name)
    summary=json.loads((REPORT/'current-summary.json').read_text('utf-8-sig'))
    summary['current_work']['w09_taixuan_t1_0005']=item
    system=next(s for s in summary['systems'] if s['id']=='multiblocks')
    system['w09_taixuan_t1_0005']=item
    system['updated_at']=now
    summary['report_updated_at']=now
    html=(REPORT/'index.html').read_text('utf8')
    w,h,d=manifest['sizeXYZ']
    notice=f'''<section class="notice" id="w09-taixuan-t1-0005"><h2>0005 · W09完整拂云观与云海山体T1</h2><p>依据负责人选择，筛选31幅公开参考，含官方15、游戏实景15及建筑细节1。重建重檐主殿、细木格窗、三足塔式香炉、薄八角练武台、青岩山峰、古松、山径与双段瀑布。实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']:,}实体方块；{len(captures['captures'])}个三维视图已保存。</p><p><a href="../../{item['preview']}">打开太虚山方块模型</a> · <a href="../../{item['gallery']}">打开31幅参考图册</a> · <a href="../0005-w09-taixuan-t1-20261116/completion.json">交付回执</a></p><p>可见形制与补建范围分别记录，完整背面、峰间坐标与山路连接含复刻推断。独立模型等待外观评审，W09整机组合后续设计；原评分与批准数量保持。</p></section>'''
    html=re.sub(r'<section class="notice" id="w09-taixuan-t1-0005">.*?</section>','',html,flags=re.S)
    html=html.replace('<body>','<body>'+notice,1)
    html=re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,flags=re.S)
    save(REPORT/'current-summary.json',summary)
    (REPORT/'index.html').write_text(html,'utf8')
    save(LOG/'completion.json',dict(updated_at=now,delivery=item,
        preview=dict(captures=len(captures['captures']),errors=captures['errors'],failed=captures['failed']),
        changes=['崖面改直立分节与倾斜草顶，撤去高对比白斑',
            '保留草地和石径，八卦台改薄八角土金边框',
            '主殿收细木棂、分窄门扇、保留通行，香炉改三足及铜绿金属八角塔檐',
            '古松改偏冠分枝，清出回折石阶，衔接瀑布与水道'],
        artifact_stage='参考与独立方块外观候选',jar_built=False,installed=False,game_operated=False,
        scores_changed=False,approval_count_changed=False,overall_percent=summary['overall_percent'],
        report_history=history.relative_to(ROOT).as_posix()))
    block=f'''\n\n## 2026-11-16 对话0005：W09完整拂云观与云海山体T1\n\n- 负责人要求武器之后按同样流程制作太虚山，并选择“完整拂云观与云海山体”。参考入口 `deliveries/{REF.name}/index.html`，31幅独立原始影像与插画，官方15、游戏实景15、建筑补充1；逐图保留来源、秒码、分辨率、场景时代与哈希，联系图和缩略图不重复计数。\n- 模型入口 `deliveries/{OUT.name}/index.html`；重建重檐主殿、细木格扇、窄门扇、三足圆腹香炉及铜绿八角塔檐、薄八角练武台、分节岩峰、偏冠古松、回折石阶和双段瀑布。使用真实整数格、原生Minecraft／GT／HK3GTL方块纹理，云海为可关闭的网页特效，完整实体已导出NBT。实际宽{w}×深{d}×高{h}格，{manifest['total_blocks']}实体方块。\n- 殿宇庭院以官方3.7训练场与历史月夜局部为主，舰桥画面用于云海山势，7.2画面补阶栏和石灯。主殿背面、内堂、峰间坐标、全山背面与连接山径包含复刻推断，记录于manifest；现有影像未提供完整总平面。\n- T1为独立外观待审候选，W09整机尺寸与组合后续确认，原作者机械山稿及武器S2保留历史；W07继续停止。回执 `logs/0005-w09-taixuan-t1-20261116/completion.json`。本轮无JAR、安装或游戏操作，评分与批准数量保持。\n'''
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:
        with (ROOT/name).open('a',encoding='utf8') as handle:
            handle.write(block)
    for name in [Path(__file__).name,'taixuan_viewer_20261116.py','preview_taixuan_20261116.mjs']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    print(json.dumps(dict(size=manifest['sizeXYZ'],blocks=manifest['total_blocks'],
        references=refs['count'],overall_percent=summary['overall_percent']),ensure_ascii=False))


if __name__=='__main__':
    main()
