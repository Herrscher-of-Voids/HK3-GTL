# -*- coding: utf-8 -*-
"""记录预览界面恢复；保留几何与原验收记录，系统分数不变。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import json,re,shutil
from restore_w04_review_ui_20261110 import ROOT,LOG,P1,P2,load,save,digest

REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def main():
    qa=load(LOG/'viewer-qa.json');baseline=load(LOG/'geometry-before.json')
    assert qa['passed'] and len(qa['results'])==2
    for folder in [P1,P2]:
        for name,value in baseline[folder.name].items():assert digest(folder/name)==value
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    history=LOG/('audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:shutil.copy2(ROOT/name,history/Path(name).name)
    before=load(history/'current-summary.json');data=deepcopy(before)
    item=dict(scope='W04 P1与P2预览器界面和操作恢复',
        template='W03 C9／休伯利安原统一评审界面',
        current_preview=(P2/'三维布局.html').relative_to(ROOT).as_posix(),
        evidence='logs/w04-review-ui-restore-20261110/viewer-qa.json',
        capabilities=['左侧大画面与右侧340px评审栏','镜头旋转平移缩放','全景／正侧俯视／主控定位',
            '逐层剖切（含草模）','材质搜索与显隐、源统计','玻璃与网格开关','场景及构件显隐','保存截图与全屏','窄屏布局'],
        geometry_and_placements_unchanged=True,previous_html_archived=True,
        candidate_approval_changed=False,game_verified=False,updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_preview_ui_restoration']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_preview_ui_restoration']=deepcopy(item);data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    scores=lambda d:{s['id']:(s['earned'],s['possible'],s['percent']) for s in d['systems']}
    assert scores(data)==scores(before) and data['overall_percent']==before['overall_percent']
    text=(history/'index.html').read_text('utf8');anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in text
    note=f'{now} · 负责人明确纠正预览器界面／操作被更换，非W04建筑布局。已将P1／P2接回W03 C9与休伯利安评审布局，恢复右侧栏、逐层、材质搜索显隐及源统计、截图、全屏与定位。两版文件URL保留，data.js／manifest.json／原verification.json哈希未变；旧界面已归档，控件与窄屏离线核验通过。未改变建筑、批准状态或游戏验收，分数不变。'
    text=re.sub(r'<p class="notice" id="w04-review-ui-current">.*?</p>','',text,flags=re.S)
    text=text.replace(anchor,anchor+'<p class="notice" id="w04-review-ui-current">'+escape(note)+
        ' <a href="../../'+item['current_preview']+'">恢复后的P2评审页</a></p>',1)
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04预览界面恢复</p>',text,count=1);assert n==1
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    note='\n\n## 2026-11-10 W04统一预览界面恢复\n\n'
    note+='- 负责人明确指出更换的是“预览器界面和操作”，不是要求改变W04建筑布局。P1／P2恢复W03 C9与休伯利安沿用的左大画面、右评审栏；保留材质搜索／显隐和源统计、逐层、玻璃、参考网格、主控定位、截图、全屏及分组显隐。后续W04候选沿用该界面，不擅自另换独立简化版。\n'
    note+='- 同URL更新界面并归档旧页；data.js、manifest.json及原verification.json哈希保持，建筑形体、尺寸、摆位、3组待协调交叠及待批准状态均未改变。P1／P2生成脚本接回统一界面，材料数明确为源体素统计，不把缩放刀或草模算成正式整机BOM。\n'
    note+='- 离线控件、静态、截图下载、全屏、镜头及窄屏核验见logs/w04-review-ui-restore-20261110/viewer-qa.json；本次没有新增游戏实测、实装或完成分。\n'
    for file in [ROOT/'AGENTS.md',ROOT/'rule/当前多方块设计规则.md']:
        content=file.read_text('utf8');marker='## 2026-11-10 W04统一预览界面恢复'
        content=re.sub(r'\n\n'+re.escape(marker)+r'.*?(?=\n\n## |\Z)',lambda _:note,content,flags=re.S) if marker in content else content+note
        file.write_text(content,'utf8')
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(text,'utf8')
    for folder in [P1,P2]:
        for name in ['w04_review_ui_20261110.mjs','restore_w04_review_ui_20261110.py','check_w04_review_ui_20261110.mjs',Path(__file__).name]:
            shutil.copy2(ROOT/'tools/structure_delivery'/name,folder/'生成脚本'/name)
    receipt=dict(passed=True,history=str(history),geometry_unchanged=True,systems=len(data['systems']),
        overall_percent=data['overall_percent'],scores_unchanged=True,html_json_synced=True,ascending_order=True,game_verified=False)
    save(LOG/'audit-update.json',receipt);print(json.dumps(receipt))


if __name__=='__main__':main()
