from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山细节补全_T2_20261116'
REF=ROOT/'deliveries/0005_W09_太虚山多角度参考_R2_20261116'
LOG=ROOT/'logs/0005-w09-taixuan-t2-20261117'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    refs=json.loads((REF/'参考清单.json').read_text('utf8'))
    captures=json.loads((OUT/'预览记录.json').read_text('utf8'))
    w,h,d=manifest['sizeXYZ']
    item=dict(candidate='W09太虚山细节补全T2',updated_at=now,approved=False,
        preview=OUT.relative_to(ROOT).as_posix()+'/index.html',
        gallery=REF.relative_to(ROOT).as_posix()+'/index.html',
        references=refs['count'],new_references=refs['new_count'],
        source_videos=refs['source_video_count'],reference_sources=refs['source_counts_new'],
        excluded_references=len(refs['excluded_references']),missing_views=refs['missing_views'],
        size_xyz=manifest['sizeXYZ'],blocks=manifest['total_blocks'],
        nbt=manifest['nbt'],sha256=manifest['nbt_sha256'],
        integer_voxels=True,materials=manifest['material_count'],
        changes=manifest['detail_changes'],
        reconstruction='背面、内堂、峰间总平面、溪岸桥头、桥位与拱腹、山门位置和竹丛坐标包含项目补建；逐构件说明见manifest。',
        status='独立方块外观待审候选，W09整机组合后续设计。',
        evidence=LOG.relative_to(ROOT).as_posix()+'/completion.json')
    LOG.mkdir(exist_ok=True)
    history=LOG/('report-before-'+datetime.now().strftime('%H%M%S%f'))
    history.mkdir()
    for name in ['index.html','current-summary.json']:
        shutil.copy2(REPORT/name,history/name)
    summary=json.loads((REPORT/'current-summary.json').read_text('utf-8-sig'))
    summary['current_work']['w09_taixuan_t2_0005']=item
    system=next(s for s in summary['systems'] if s['id']=='multiblocks')
    system['w09_taixuan_t2_0005']=item
    system['updated_at']=now
    summary['report_updated_at']=now
    html=(REPORT/'index.html').read_text('utf8')
    notice=f'''<section class="notice" id="w09-taixuan-t2-0005"><h2>0005 · W09太虚山细节补全T2</h2><p>新增{refs['new_count']}幅参考，累计{refs['count']}幅，来自{refs['source_video_count']}段不同视频；重复图另行保留并剔除计数。补全回纹格窗、门扇金饰、檐下横楣、白腰带、灰石柱础、香炉腹带与斜格、暗灰石灯、三间山门、石桥及细竹。实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']:,}实体方块，{len(captures['captures'])}个三维视图已保存。</p><p><a href="../../{item['preview']}">打开T2方块模型</a> · <a href="../../{item['gallery']}">打开62幅参考图册</a> · <a href="../0005-w09-taixuan-t2-20261117/completion.json">交付回执</a></p><p>{item['reconstruction']} 独立外观待审，原评分与批准数量保持。</p></section>'''
    html=re.sub(r'<section class="notice" id="w09-taixuan-t2-0005">.*?</section>','',html,flags=re.S)
    html=html.replace('<body>','<body>'+notice,1)
    html=re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,flags=re.S)
    save(REPORT/'current-summary.json',summary)
    (REPORT/'index.html').write_text(html,'utf8')
    save(LOG/'completion.json',dict(updated_at=now,delivery=item,
        preview=dict(captures=len(captures['captures']),errors=captures['errors'],failed=captures['failed']),
        artifact_stage='多角度参考与独立方块细节候选',jar_built=False,installed=False,game_operated=False,
        scores_changed=False,approval_count_changed=False,overall_percent=summary['overall_percent'],
        report_history=history.relative_to(ROOT).as_posix()))
    block=f'''

## 2026-11-17 对话0005：W09太虚山参考R2与方块细节T2

- 负责人要求继续搜集几十幅不同角度清晰图片并补细节。R2新增{refs['new_count']}幅、累计{refs['count']}幅，来自{refs['source_video_count']}段不同视频；新增含1幅二维内堂背景，其余30幅为三维游戏或PV画面，5幅重复图另存并剔除计数。图册 `deliveries/{REF.name}/index.html` 保留逐图来源、秒码、分辨率、时期、可见细节与哈希。
- T2模型 `deliveries/{OUT.name}/index.html` 补回纹格窗、折线门棂与双框菱形金饰、檐下横楣、白腰带及灰石柱础；屋瓦统一青灰，香炉补深色腹带与斜交窗棂，小石灯改暗灰帽及短尖；新增四柱三间山门、起拱石桥与分节细竹。桥东端补接岸岩台与沿溪石路，两端加踏步。真实整数格、原生像素贴图及完整NBT，实际宽{w}×深{d}×高{h}格，{manifest['total_blocks']}实体方块。
- 完整殿后、正俯屋顶、三维内堂、全山背面、总平面与石桥拱腹仍缺清晰图证；溪岸桥头、桥位、跨径与拱腹、山门位置和背面、竹丛坐标均明确记录为项目补建。T1保留，T2为独立待审候选，W09整机组合后续设计。
- 回执 `logs/{LOG.name}/completion.json`；本轮无JAR、安装或游戏操作，评分及批准数量保持，W07继续停止。
'''
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:
        with (ROOT/name).open('a',encoding='utf8') as handle:
            handle.write(block)
    for name in [Path(__file__).name,'preview_taixuan_20261116.mjs']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    print(json.dumps(dict(references=refs['count'],new=refs['new_count'],
        source_videos=refs['source_video_count'],blocks=manifest['total_blocks'],
        overall_percent=summary['overall_percent']),ensure_ascii=False))


if __name__=='__main__':
    main()
