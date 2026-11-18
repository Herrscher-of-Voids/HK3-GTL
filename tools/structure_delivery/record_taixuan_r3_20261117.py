from datetime import datetime, timezone
from pathlib import Path
import json
import re
import shutil


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山岩坪衔接_T3_20261117'
LOG=ROOT/'logs/0005-w09-taixuan-t3-20261117'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    captures=json.loads((OUT/'预览记录.json').read_text('utf8'))
    w,h,d=manifest['sizeXYZ']
    item=dict(candidate='W09太虚山岩坪衔接T3',updated_at=now,approved=False,
        preview=OUT.relative_to(ROOT).as_posix()+'/index.html',
        previous_candidate=manifest['previous_candidate'],
        size_xyz=manifest['sizeXYZ'],blocks=manifest['total_blocks'],
        nbt=manifest['nbt'],sha256=manifest['nbt_sha256'],
        integer_voxels=True,materials=manifest['material_count'],
        root_cause='主岩体斜顶与固定院坪高度不一致，边缘轮廓分别生成。',
        changes=manifest['detail_changes'][-3:],
        reconstruction='岩坪轮廓渐变、岩层及山径补岩属于项目地形衔接。',
        status='独立方块外观待审候选，W09整机组合后续设计。',
        evidence=LOG.relative_to(ROOT).as_posix()+'/completion.json')
    LOG.mkdir(exist_ok=True)
    history=LOG/('report-before-'+datetime.now().strftime('%H%M%S%f'))
    history.mkdir()
    for name in ['index.html','current-summary.json']:
        shutil.copy2(REPORT/name,history/name)
    summary=json.loads((REPORT/'current-summary.json').read_text('utf-8-sig'))
    summary['current_work']['w09_taixuan_t3_0005']=item
    system=next(s for s in summary['systems'] if s['id']=='multiblocks')
    system['w09_taixuan_t3_0005']=item
    system['updated_at']=now
    summary['report_updated_at']=now
    summary['systems'].sort(key=lambda s:s['percent'])
    html=(REPORT/'index.html').read_text('utf8')
    notice=f'''
<section class="notice" id="w09-taixuan-t3-0005">
<h2>0005 · W09太虚山岩坪衔接T3</h2>
<p>按院坪Y157实际底层轮廓重建承岩，岩顶Y156逐格相接；
上部岩壁从既有Y107截面渐变至院坪轮廓，门前和回折石阶下补连续岩脊。</p>
<p>实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']:,}实体方块，
已保存{len(captures['captures'])}张三维预览。岩层与轮廓过渡属于项目补建，T2保留历史。</p>
<p><a href="../../{item['preview']}">打开T3方块模型</a> ·
<a href="../0005-w09-taixuan-t3-20261117/completion.json">交付回执</a></p>
<p>独立外观待审，原评分与批准数量保持。</p></section>
'''
    html=re.sub(r'<section class="notice" id="w09-taixuan-t3-0005">.*?</section>','',html,flags=re.S)
    html=html.replace('<body>','<body>'+notice,1)
    html=re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,flags=re.S)
    save(REPORT/'current-summary.json',summary)
    (REPORT/'index.html').write_text(html,'utf8')
    save(LOG/'completion.json',dict(updated_at=now,delivery=item,
        preview=dict(captures=len(captures['captures']),errors=captures['errors'],failed=captures['failed'],
            inspected=['all-base_front.png','all-base_side.png','all-base_under.png',
                'all-top.png','all-route.png','all-oblique.png']),
        artifact_stage='独立方块岩坪衔接候选',jar_built=False,installed=False,game_operated=False,
        scores_changed=False,approval_count_changed=False,overall_percent=summary['overall_percent'],
        multiblocks_percent=system['percent'],report_history=history.relative_to(ROOT).as_posix()))
    block=f'''

## 2026-11-17 对话0005：W09太虚山岩坪衔接T3

- 负责人指出院坪、楼底与太虚山山岩脱节。根因为主岩体斜顶与固定Y157院坪底面高度不一致，边缘轮廓分别生成。
- T3保留Y108以下原主岩体，上部从Y107截面渐变到院坪真实底层轮廓；承岩顶面Y156与院坪底面Y157逐格相接。门前及回折石阶下补连续岩脊，缺同列下方岩体处以斜向岩肩连接相邻山岩。
- 模型 `deliveries/{OUT.name}/index.html` 使用真实整数格和原生像素贴图，完整NBT实际宽{w}×深{d}×高{h}格，共{manifest['total_blocks']}实体方块。新增岩肩使深度由580增至582格，导出按实际构件范围保留。共29张预览，已目视正面、侧面、仰视、俯视、山径及斜视。
- 岩坪轮廓渐变、岩层和山径补岩属于项目地形衔接。T2保留历史，T3为独立外观待审候选。回执 `logs/{LOG.name}/completion.json`；无JAR、安装或游戏操作，原评分、批准数量保持，W07继续停止。
'''
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:
        with (ROOT/name).open('a',encoding='utf8') as handle:
            handle.write(block)
    shutil.copy2(Path(__file__),OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(dict(preview=item['preview'],blocks=item['blocks'],size_xyz=item['size_xyz'],
        overall_percent=summary['overall_percent'],multiblocks_percent=system['percent']),ensure_ascii=False))


if __name__=='__main__':
    main()
