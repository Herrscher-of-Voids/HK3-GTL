# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from pathlib import Path
import hashlib
from html import escape
import json
import re
import shutil


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_识律三兵方块复刻_S1_20261116'
LOG=ROOT/'logs/0005-w09-weapons-voxel-s1-20261116'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    LOG.mkdir(exist_ok=True)
    now=datetime.now(timezone.utc).isoformat()
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    preview=json.loads((OUT/'预览记录.json').read_text('utf8'))
    item=dict(candidate='W09识律三兵与武器匣方块复刻S1',preview=str((OUT/'index.html').relative_to(ROOT)).replace('\\','/'),
        models=[dict(id=m['id'],size_xyz=m['sizeXYZ'],blocks=m['blocks'],nbt=m['nbt'],sha256=m['sha256']) for m in manifest['models']],
        total_blocks=sum(m['blocks'] for m in manifest['models']),integer_voxels=True,static=True,
        method=manifest['modeling_method'],updated_at=now,approved=False,
        status='独立模型待外观评审，W09整机改造待后续设计。',
        evidence='logs/0005-w09-weapons-voxel-s1-20261116/completion.json')
    history=LOG/('report-before-'+datetime.now().strftime('%H%M%S'))
    history.mkdir()
    for name in ['index.html','current-summary.json']:
        shutil.copy2(REPORT/name,history/name)
    summary=json.loads((REPORT/'current-summary.json').read_text('utf-8-sig'))
    summary['current_work']['w09_weapons_voxel_s1_0005']=item
    system=next(s for s in summary['systems'] if s['id']=='multiblocks')
    system['w09_weapons_voxel_s1_0005']=item
    system['updated_at']=now
    summary['report_updated_at']=now
    html=(REPORT/'index.html').read_text('utf8')
    note=f'<section class="notice" id="w09-weapons-voxel-s1-0005"><h2>0005 · 识之律者武器方块复刻 S1</h2><p>宝剑、长枪、链刃与武器匣共4件独立整数格模型，{item["total_blocks"]:,}实体格；原生方块纹理、四件切换、厚度及细节视角、剖切和独立NBT已交付，外观待负责人评审。W09整机改造后续设计，系统评分及批准数量保持。</p><p><a href="../../{item["preview"]}">打开方块模型</a> · <a href="../0005-w09-weapons-voxel-s1-20261116/completion.json">交付回执</a></p></section>'
    html=re.sub(r'<section class="notice" id="w09-weapons-voxel-s1-0005">.*?</section>','',html,flags=re.S)
    html=html.replace('<body>','<body>'+note,1)
    html=re.sub(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,flags=re.S)
    save(REPORT/'current-summary.json',summary)
    (REPORT/'index.html').write_text(html,'utf8')
    record=dict(updated_at=now,delivery=item,preview_capture=dict(screenshots=len(preview['captures']),
        errors=preview['errors'],failed_resources=preview['failed']),
        scope='独立方块模型与NBT候选；未接入W09整机、未构建或安装JAR、未操作游戏或实例。',
        overall_percent=summary['overall_percent'],scores_changed=False,approval_count_changed=False,
        report_history=str(history),files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'NBT').glob('*.nbt')})
    save(LOG/'completion.json',record)
    block='''\n\n## 2026-11-16 对话0005：W09识律武器真实方块复刻S1\n\n- 负责人要求依照本轮武器图片复刻方块像素模型。独立入口 `deliveries/0005_W09_识律三兵方块复刻_S1_20261116/index.html`；宝剑、长枪、链刃与武器匣使用整数格实体及原生方块贴图，支持正背面、厚度、近景、剖切、参考原帧与独立NBT下载。\n- 武器匣宽80×深22×高355、231431格；宝剑56×13×324、36624格；长枪20×9×337、14303格；链刃73×23×368、52348格，总334706格。武器匣按官方转台取样宽面与云火纹，太极纹作逐格圆形校准；侧壁、隐藏背纹及三兵细节厚度按参考转译。未使用官方PMX网格或模型贴图。\n- 近景修订了骨白护手与深色三瓣、收薄枪头、链刃短接头与细连接段；20幅预览截图已记录，页面错误和资源失败均0。回执 `logs/0005-w09-weapons-voxel-s1-20261116/completion.json`。本轮外观待审，W09 A1整机保持历史，W07继续停止；JAR、实例、游戏验收、系统分数与批准数量保持。\n'''
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:
        with (ROOT/name).open('a',encoding='utf8') as handle:
            handle.write(block)
    for path in [Path(__file__),ROOT/'tools/structure_delivery/senti_weapon_viewer_20261116.py']:
        shutil.copy2(path,OUT/'生成脚本'/path.name)
    print(json.dumps(dict(models=4,blocks=item['total_blocks'],overall_percent=summary['overall_percent'])))


if __name__=='__main__':
    main()
