# -*- coding: utf-8 -*-
"""记录预览更新及历史入口切换，不增加舰船系统验收分数。"""
from pathlib import Path
from html import escape
import json
import re
import shutil
import sys
from build_hyperion_modern_preview_20261108 import ROOT, OUT, LOG, OLD, read, save, digest
from max_structure_review import publisher


def main():
    assert read(LOG/'viewer-qa.json')['passed']
    before = LOG/'before-legacy-entry'; before.mkdir(exist_ok=False)
    starter = ROOT/'logs/hyperion-preview-20260929/start_preview.mjs'
    shutil.copy2(starter,before/starter.name)
    old_server = starter.parent/'server.json'
    if old_server.exists(): shutil.copy2(old_server,before/old_server.name)
    starter.write_text('/** 原预览启动入口沿用；旧实现已保存在本轮历史备份。 */\nawait import(\'../../tools/structure_delivery/serve_hyperion_modern_preview_20261108.mjs\');\n',encoding='utf-8')
    scripts = OUT/'生成脚本'; scripts.mkdir(exist_ok=True)
    names = ['build_hyperion_modern_preview_20261108.py','hyperion_model_templates_20261108.mjs',
             'hyperion_modern_viewer_20261108.mjs','package_hyperion_modern_preview_20261108.mjs',
             'check_hyperion_modern_preview_20261108.mjs','serve_hyperion_modern_preview_20261108.mjs',Path(__file__).name]
    for name in names: shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    for p in ['viewer-qa.json','source-verification.json']: shutil.copy2(LOG/p,OUT/p)
    verification = read(OUT/'verification.json'); verification['viewer_qa_passed']=True; verification['visual_review_passed']=True
    save(OUT/'verification.json',verification)
    report = ROOT/'logs/beta5-completion-audit-20261030'
    originals={p:p.read_bytes() for p in [report/'index.html',report/'current-summary.json']}
    history=LOG/'before-report';history.mkdir(exist_ok=False)
    for p,content in originals.items():(history/p.name).write_bytes(content)
    summary=read(report/'current-summary.json');old=read(history/'current-summary.json')
    row=next(s for s in summary['systems'] if s['id']=='N16')
    state='2026-11-08：指定1145格舰体已迁移至最新版离线预览，保留完整方块状态与实体；正式工程仍未验收。'
    row.update(coverage=state,updated_at='2026-11-08')
    cap=row['capabilities'][3]
    detail=' 2026-11-08新增原稿新版评审预览：147万方块逐格对比、3402条实体一致；原版模型含非完整形体与状态旋转、材质筛选和剖切、五视图及手机布局离线通过。576130片完整立方体合并面与28933个带状态或特殊模型方块分开绘制；未把浏览器预览记作游戏预算扫描、成型或运行性能。'
    cap['reason']+=detail
    refs=['logs/hyperion-modern-preview-20261108/source-verification.json','logs/hyperion-modern-preview-20261108/viewer-qa.json','deliveries/'+OUT.name+'/index.html']
    cap['evidence']=list(dict.fromkeys(cap.get('evidence',[])+refs))
    summary['current_work']['hyperion_preview']=dict(updated_at='2026-11-08',state=state,preview=refs[-1],blocks=1469258,size_xyz=[1145,240,549],block_entities=3402,game_verified=False)
    summary['report_updated_at']='2026-11-08';summary['systems'].sort(key=lambda s:s['percent'])
    assert [(s['id'],s['percent'],s['earned'],s['possible']) for s in summary['systems']]==[(s['id'],s['percent'],s['earned'],s['possible']) for s in old['systems']]
    assert all(s==o for s,o in zip(summary['systems'],old['systems']) if s['id']!='N16')
    assert summary['overall_percent']==old['overall_percent'] and summary['multiblock_scope']==old['multiblock_scope']
    html=originals[report/'index.html'].decode('utf-8');card=re.search(r'<details class="system" data-id="N16".*?</details>',html,re.S).group()
    changed,n=re.subn(r'(<div class="bar">.*?</div><p>).*?(</p>)',lambda m:m[1]+escape(state)+m[2],card,count=1,flags=re.S);assert n==1
    pattern=r'(<tr><td>'+re.escape(escape(cap['claim']))+r'</td><td>)(.*?)(</td><td>).*?(</td></tr>)'
    links=' · '.join('<a href="'+escape((ROOT/p).as_uri(),quote=True)+'">'+escape(p.split('/')[-1])+'</a>' for p in cap['evidence'])
    changed,n=re.subn(pattern,lambda m:m[1]+m[2]+m[3]+escape(cap['reason'])+'<p class="evidence">'+links+'</p>'+m[4],changed,count=1,flags=re.S);assert n==1
    html=html.replace(card,changed,1)
    notice='<p class="notice" id="hyperion-modern-preview">'+escape(state)+' <a href="../../'+refs[-1]+'">打开新版全舰预览</a>。N16保持25%（1.5/6）；批准57／正式52，既定74项范围不变。</p>'
    anchor='<p class="notice" id="mx-c01-design">';assert anchor in html;html=html.replace(anchor,notice+anchor,1)
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==summary
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in summary['systems']]
    publisher().publish_transaction({report/'index.html':html,report/'current-summary.json':json.dumps(summary,ensure_ascii=False,indent=2)+'\n'},originals)
    for p,h in read(LOG/'immutable-inputs.json').items(): assert digest(Path(p))==h,p
    save(LOG/'report-publication.json',dict(passed=True,system='N16',percent=25,earned=1.5,possible=6,other_systems_unchanged=35,scores_unchanged=True,ascending_order=True,overall_percent=summary['overall_percent'],legacy_entry_updated=True,original_ship_and_old_preview_unchanged=True))
    print('新版预览入口及固定审计已同步；N16分数25%，其他35个系统原分保持。')


def redirect_legacy():
    server=read(LOG/'server.json');target=server['url']
    assert target in ['http://127.0.0.1:5199/','http://127.0.0.1:5200/']
    backup=LOG/'before-legacy-entry/old-index.html'
    if target.endswith(':5200/'):
        assert not backup.exists()
        shutil.copy2(OLD/'index.html',backup)
        (OLD/'index.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url='+target+'"><title>休伯利安新版预览</title><body style="background:#121b2b;color:#eee;font:18px system-ui;padding:40px"><p>休伯利安预览已迁移至新版界面。</p><a style="color:#c9b8ff" href="'+target+'">进入新版全舰预览</a></body></html>',encoding='utf-8')
    for p,h in read(LOG/'immutable-inputs.json').items():
        file=Path(p)
        assert digest(backup if file==OLD/'index.html' and backup.exists() else file)==h,p
    publication=read(LOG/'report-publication.json');publication.pop('original_ship_and_old_preview_unchanged',None)
    publication.update(original_ship_unchanged=True,old_preview_assets_retained=True,legacy_index_redirected=backup.exists(),url=target)
    save(LOG/'report-publication.json',publication)
    for name in ['serve_hyperion_modern_preview_20261108.mjs',Path(__file__).name]:shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    print('原5199入口已接入新版；原页面和旧启动器均有历史备份。')


if __name__=='__main__':
    redirect_legacy() if len(sys.argv)>1 and sys.argv[1]=='redirect' else main()
