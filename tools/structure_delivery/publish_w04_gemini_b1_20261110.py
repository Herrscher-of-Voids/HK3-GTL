"""把W04第二候选同步固定审计；先留历史，不修改任何系统分数或批准数量。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import json,re,shutil
import w04_gemini_dragon_b1_20261110 as g
from package_w04_gemini_b1_20261110 import hashes,A1

REPORT=g.ROOT/'logs/beta5-completion-audit-20261030'


def load(p):return json.loads(p.read_text('utf8'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    manifest=load(g.OUT/'manifest.json');qa=load(g.LOG/'viewer-qa.json');verification=load(g.OUT/'verification.json')
    assert qa['passed'] and qa['screenshots']==10 and verification['readback']['geometry_nbt_schematic_per_block_equal']
    assert hashes(A1)==load(g.LOG/'a1-before-hashes.json')
    history=g.LOG/('audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    rules=g.ROOT/'rule/当前多方块设计规则.md';rule_history=g.LOG/'before-design-rules.txt'
    if not rule_history.exists():shutil.copy2(rules,rule_history)
    text=rules.read_text('utf8')
    marker='## 2026-11-10 W04 Gemini俱利伽罗盘枢B1候选'
    if marker not in text:
        text+='\n\n'+marker+'\n\n'
        text+='- 负责人提供Gemini第二方案：托卡马克八角雷池、三重鸟居、倒悬涤罪七雷、三道三巴纹雷鼓、双侧五指机械鬼手及十道锁链、S形俱利伽罗和折角雷翼。按原文生成独立静态B1；A1不变，未替换或批准。\n'
        text+='- HRV绯雷红#C93F63为雷之律者身份色，运行目标WSV；不混用始源造型、不强制单一机壳。\n'
        text+=f"- 原文名义697×565×343不作裁切窗口；实际宽{manifest['size'][0]}×深{manifest['size'][2]}×高{manifest['size'][1]}，{manifest['blocks']:,}实体；龙躯中心线{manifest['dragon_centerline_length']:.1f}格。Y0～343端点、130格刀锷、260格斜塔、雷环外伸电极等冲突公开保留。\n"
        text+='- 逐格NBT／Schematic回读及十视角、静态、镜头与显隐剖切为离线证据；三张局部图单独显示构件。交叠记录含有意接合及待协调干涉，不宣称无穿模或官方逐处复刻。未注册W04控制器、未部署、未游戏实装，全部系统分数及批准数量保持。\n'
        text+='- 入口：deliveries/W04_Gemini_俱利伽罗盘枢_B1_20261110/index.html；证据：logs/w04-gemini-dragon-b1-20261110/。\n'
        rules.write_text(text,'utf8')
    before=load(history/'current-summary.json');data=deepcopy(before)
    item=dict(id='W04',candidate='Gemini俱利伽罗盘枢B1',preview=str((g.OUT/'index.html').relative_to(g.ROOT)).replace('\\','/'),
        size_xyz=manifest['size'],blocks=manifest['blocks'],static=True,approved=False,installed=False,game_verified=False,
        dragon_centerline_length=manifest['dragon_centerline_length'],source_conflicts=manifest['source_conflicts'],
        overlap_pairs=verification['overlap_pairs'],collision_free=False,offline_verification='logs/w04-gemini-dragon-b1-20261110/viewer-qa.json',
        a1_unchanged=True,updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_gemini_second_preview']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_gemini_second_preview']=deepcopy(item);data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent']
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in before['systems']]
    html=(history/'index.html').read_text('utf8')
    html=re.sub(r'<p class="notice" id="w04-gemini-b1-current">.*?</p>','',html,flags=re.S)
    note=f"{now} · W04 Gemini第二候选B1：完整静态{manifest['size'][0]}×{manifest['size'][2]}×{manifest['size'][1]}，{manifest['blocks']:,}实体；十视角与逐格导出回读通过。原案冲突及交叠保留，未批准或实装，A1及r242部署证据保持。"
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in html
    html=html.replace(anchor,anchor+'<p class="notice" id="w04-gemini-b1-current">'+escape(note)+' <a href="../../'+item['preview']+'">B1与A1对照</a></p>',1)
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04第二候选</p>',html,count=1);assert n==1
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in data['systems']]
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(html,'utf8')
    receipt=dict(passed=True,updated_at=now,history=str(history),scores_unchanged=len(data['systems']),
        overall_percent=data['overall_percent'],html_json_synced=True,ascending_order=True,a1_unchanged=True,game_verified=False)
    save(g.LOG/'audit-update.json',receipt)
    shutil.copy2(Path(__file__),g.OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(receipt,ensure_ascii=True))


if __name__=='__main__':main()
