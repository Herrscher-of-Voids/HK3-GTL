"""向固定审计同步首版W04及W01–W03实测收据；不以候选或调试增加系统分数。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import json,re,shutil

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'logs/beta5-completion-audit-20261030'
LOG=ROOT/'logs/w01-w03-implementation-20261110'
OUT=ROOT/'deliveries/W04_鸣霆超导电磁天枢_鬼角悬刃_A1_20261110'
def load(p):return json.loads(p.read_text('utf8'))
def main():
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    baseline=LOG/('audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));baseline.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,baseline/name)
    before=load(baseline/'current-summary.json');data=deepcopy(before)
    manifest=load(OUT/'manifest.json');qa=load(ROOT/'logs/w04-thunder-canyon-a1-20261110/viewer-qa.json')
    assert qa['passed'] and qa['screenshots']==7
    preview=dict(id='W04',candidate='鬼角双极·悬刃雷场A1',preview=str((OUT/'index.html').relative_to(ROOT)).replace('\\','/'),
        size_xyz=manifest['size'],blocks=manifest['blocks'],static=True,approved=False,installed=False,game_verified=False,
        offline_verification='logs/w04-thunder-canyon-a1-20261110/viewer-qa.json',updated_at=now)
    runtime=load(LOG/'client-results.json') if (LOG/'client-results.json').exists() else dict(
        status='W01/W02控制器、实体核验与创造巡检已接代码；构建与客户端验收进行中',
        runtime_scope='真实控制器、完整搭建、成型与运行；正式生产规则另定（负责人明确选择）',
        game_verified=False,production_verified=False,updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_first_preview']=deepcopy(preview);system['w01_w03_commission']=deepcopy(runtime);system['updated_at']=now
    data['current_work']['w04_first_preview']=deepcopy(preview)
    data['current_work']['w01_w03_commission']=deepcopy(runtime)
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent']
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in before['systems']]
    text=(baseline/'index.html').read_text('utf8')
    text=re.sub(r'<p class="notice" id="wonder-20261110-current">.*?</p>','',text,flags=re.S)
    note='W04首版「鬼角双极·悬刃雷场」：七视角、静态交互、导出回读通过，实际宽697×深565×高343；未批准或游戏实装。W01–W03本轮范围为真实控制器、完整搭建、成型与运行验证，正式工艺另定。'+runtime['status']+'。总分和批准数量保持原值。'
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in text
    text=text.replace(anchor,anchor+'<p class="notice" id="wonder-20261110-current">'+escape(now+' · '+note)+' <a href="../../'+preview['preview']+'">W04首版预览</a></p>',1)
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W01–W04进度</p>',text,count=1);assert n==1
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    (REPORT/'current-summary.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
    (REPORT/'index.html').write_text(text,'utf8')
    (LOG/'audit-update.json').write_text(json.dumps(dict(updated_at=now,history=str(baseline),scores_unchanged=36,
        overall_percent=data['overall_percent'],html_json_synced=True,ascending_order=True),ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(dict(passed=True,scores_unchanged=36,overall_percent=data['overall_percent'])))
if __name__=='__main__':main()
