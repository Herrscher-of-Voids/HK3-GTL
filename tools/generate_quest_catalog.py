# -*- coding: utf-8 -*-
"""内测5修订129：从正式研究目录生成FTB教程/原版进度，稳定ID不随顺序改变；无物品奖励。"""
from pathlib import Path
import json,hashlib,re,datetime
from quest_tutorial import RESEARCH, TIER_INTROS, GUIDES
# 【变更记录 #2】2026-10-01 15:13:33（修订131）：17个电压页、玩家正文与分页备忘；旧任务ID及真实前置不变。
ROOT=Path(__file__).resolve().parents[1]
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def save(p,v):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ident(key):return '4B5'+hashlib.sha256(('hk3gtl-beta5-guide-v1:'+key).encode()).hexdigest()[:13].upper()
def tag(key):return 'hk3gtl_quest_'+key.lower().replace('-','_')
topics=load('src/main/resources/data/hk3gtl/research/research_catalog.json')['topics']
costs={x['id']:x for x in load('src/main/resources/data/hk3gtl/research/research_costs.json')['topics']}
execs={x['id']:x for x in load('src/main/resources/data/hk3gtl/research/research_execution.json')['topics']}
icons=load('src/main/resources/data/hk3gtl/research/research_icons.json')['icons']
assert len(topics)==100 and {x['id'] for x in topics}==costs.keys()==execs.keys()==icons.keys()
tiers=(ROOT/'src/main/java/com/sirin/hk3gtl/common/constants/Hk3TiersImpl.java').read_text(encoding='utf-8')
def array(name):return re.findall(r'"([^"]+)"',re.search(name+r'\s*=\s*\{([^}]+)',tiers)[1])
names=array('VOLTAGE_NAMES_ZH');symbols=array('VOLTAGE_SYMBOLS');assert len(names)==len(symbols)==16
voltage=['MAX']+[f'{s} · {n}' for s,n in zip(symbols,names)]
assert set(RESEARCH)=={t['id'] for t in topics} and len(TIER_INTROS)==17
bytopic={t['id']:t for t in topics}
readable=load('src/main/resources/data/hk3gtl/guide/tutorial_names.json')
def prose(value):
 value=re.sub(r'(?:I\d{2}(?:-\d)?|S0[1-5]|W\d{2}|H01)(?![A-Z0-9-])',lambda m:readable['machines'].get(m[0],m[0]),value)
 for t in sorted(topics,key=lambda t:-len(t['id'])):
  value=re.sub(r'(?<![A-Z])'+re.escape(t['id'][3:])+r'(?![A-Z])',t['title'],value)
 return value

primary={int(tier)-14:'hk3gtl:'+id for id,tier in re.findall(r'new Entry\("([^"\n]+)", (\d+), "[^"\n]+", \d+, true\)',(ROOT/'src/main/java/com/sirin/hk3gtl/common/item/Hk3CircuitCatalog.java').read_text(encoding='utf-8'))}
assert len(primary)==16
chapters=[];manifest=[]
for tier,label in enumerate(voltage):
 key=f'hk3_voltage_{tier:02}'
 icon='gtlcore:max_electric_motor' if tier==0 else 'hk3gtl:electric_motor_'+symbols[tier-1].lower()
 chapters.append({'_comment':'【变更记录 #1】'+NOW+'（修订131）：一电压一页，旧任务编号保留；生成源tools/generate_quest_catalog.py。','filename':key,'id':ident('chapter:'+key),'title':'HK3GTL · '+label,'subtitle':[f'Tier{tier+14} · '+TIER_INTROS[tier][0]],'group':'','order_index':14+tier,'icon':icon,'default_hide_dependency_lines':False,'default_quest_shape':'rsquare','quests':[],'quest_links':[]})

def add(ch,key,title,desc,kind='reading',value='',deps=(),icon='minecraft:book',x=None,y=None):
 chapter=chapters[ch-1];idx=len(chapter['quests']);q=ident('quest:'+key);t=ident('task:'+key)
 row={'id':q,'title':title,'icon':icon,'x':float((idx%4)*3 if x is None else x),'y':float((idx//4)*3 if y is None else y),'description':desc,'tasks':[{'id':t,'type':'checkmark' if kind=='reading' else 'custom','title':'读完这一页' if kind=='reading' else '完成这项研究' if kind=='research' else '达成这一里程碑','tags':[tag(key)]}]}
 if deps:row['dependencies']=[ident('quest:'+d) for d in deps]
 chapter['quests'].append(row);manifest.append({'key':key,'kind':kind,'value':value,'quest':q,'task':t,'chapter':chapter['filename']})
 return row

guide_titles={'guide-start':'从MAX出发','guide-letters':'五封来信','guide-sampling':'第一瓶样本','guide-research':'怎样开始研究','guide-power':'先检查电源','guide-pressure':'注视度与研究','guide-refund':'暂停与退款','guide-phone':'随身终端','guide-social':'聊一会儿','guide-blocked':'遇到卡点时','guide-civilization':'翻开文明档案','guide-finale':'最后的会面'}
for key,desc in GUIDES.items():
 if key in ('guide-civilization','guide-finale'):continue
 add(1,key,guide_titles[key],[v for i,p in enumerate(desc) for v in (['',p] if i else [p])])
for tier in range(17):
 title,first,second=TIER_INTROS[tier]
 if tier==0:continue
 add(tier+1,f'voltage-intro-{tier:02}',title,[first,'',second,'{@pagebreak}',f'本页是{voltage[tier]}的研究路线。先看连接线上的前置，再按需要安排并行分支。','研究所需要达到对应等级。部分高阶设备与正式结构仍待开放，遇到未开放的执行设备时请等待后续更新。'],icon=primary[tier])
 add(tier+1,f'voltage-parts-{tier:02}','电路与八大件',[f'进入{voltage[tier]}，先在JEI里查看本档电路与设备的配方需求。电路属于哪一档，以配方接受的电路标签为准。','', '电动马达、活塞、泵、传送带、机械臂、场发生器、发射器和传感器，是这一档设备会用到的八类部件。优先准备你下一台设备真正需要的种类，再考虑自动化备货。','{@pagebreak}', '马达与活塞用于运动，泵和传送带处理流体与物品，机械臂承担操作；场发生器、发射器与传感器则用于场控制与检测。具体数量和材料按JEI配方准备。','同档电路可能有不同系列和形态。先核对电路等级，不要只看名字中是否带“主机”。本节点是备料提示，读完不会替代制造或研究。'],icon=chapters[tier]['icon'])
def local_level(id):
 t=bytopic[id]
 return 1+max((local_level(p) for p in t['prerequisites'] if bytopic[p]['tier']==t['tier']),default=-1)
lanes={}
for t in sorted(topics,key=lambda t:(t['tier'],local_level(t['id']),t['id'])):
 id=t['id'];c=costs[id];e=execs[id];tier=t['tier'];d=local_level(id);lane=lanes.get((tier,d),0);lanes[(tier,d)]=lane+1
 prereqs='、'.join(bytopic[p]['title'] for p in t['prerequisites']) or '可以从这里开始'
 mats='；'.join(f"{m['count']} × {readable['materials'][m['tag']]}" for m in c['materials'])
 desc=[RESEARCH[id],'',prose(t['result']),'{@pagebreak}', '&b实验准备&r',prose(e['inputs'])+'。','',f"按JEI查找对应工艺，在{prose(e['executor'])}完成对应实验后，到S0{t['lab']}或更高等级研究所选择“{t['title']}”并开题。",'研究完成后，任务书会自动更新。','{@pagebreak}','&b开题备忘&r','先完成：'+prereqs+'。',f"基础研究费用：{c['points']}点；{mats}。",f"基础工期：{c['ticks']/1200:g}分钟；研究用电：{c['eut']:,} EU/t。",'以上是研究本身的基础消耗，实验配方另看JEI；最终报价以研究所界面为准。']
 row=add(tier+1,id,t['title'],desc,'research',id,t['prerequisites'],icons[id],d*3,lane*3)
 row['subtitle']=f"S0{t['lab']} · {id}"
 row['shape']='hexagon' if id in ['RN-BCE','RN-ALE','RN-QLE','RN-ILE','RN-CLE','RN-TAA'] else 'rsquare'
 if row['shape']=='hexagon':row['size']=1.3

civ=['崩坏识别','稳定工业','材料与核心','量子航路','虚数联系','文明奇观','认知与审判准备']
for i,name in enumerate(civ,1):
 add(17,f'civ-{i}',f'C{i} · {name}',['一路积累的成果，会逐步提升文明等级。','', '打开手机文明总览查看当前缺项，已有成果也可以在文明档案里回看。本节点会随文明等级自动更新。'],'civilization',str(i),[f'civ-{i-1}'] if i>1 else [])
add(17,'guide-civilization','翻开文明档案',[GUIDES['guide-civilization'][0],'',GUIDES['guide-civilization'][1]])
add(17,'review-1','第一次审查',['先准备好一审要求的研究与工况，再参加正式会面。','', '本节点显示本队获得的一审许可；你自己是否完成会面，可以在文明档案里查看。'],'review','1')
add(17,'review-2','第二次审查',['完成一审后，继续准备世界泡、无人采掘与维系方面的成果，再申请第二次会面。','', '本节点显示本队获得的二审许可。琪亚娜的认可之后，还有属于你们的工程与最后的会面。'],'review','2',['review-1'])
add(17,'guide-finale','最后的会面',[v for i,p in enumerate(GUIDES['guide-finale']) for v in (['',p] if i else [p])])
# 电压入口在上方，研究按本页前置从左向右；外页前置使用FTB原生任务链接。
entry_by_key={e['key']:e for e in manifest}
for tier,ch in enumerate(chapters):
 research=[q for q in ch['quests'] if q['id'] in {entry_by_key[t['id']]['quest'] for t in topics if t['tier']==tier}]
 bottom=max([q['y'] for q in research]+[0])+4
 side=0
 for q in ch['quests']:
  e=next(e for e in manifest if e['quest']==q['id']);key=e['key']
  if e['kind']=='research':continue
  if key=='guide-start' or key.startswith('voltage-intro-'):q.update(x=0.0,y=-4.0,size=2.0,shape='rsquare',icon=primary.get(tier,'gtlcore:max_electric_motor'))
  elif key.startswith('voltage-parts-'):q.update(x=-4.0,y=-4.0)
  else:q.update(x=float(side%4*3),y=float(bottom+side//4*3));side+=1
 external=sorted({p for t in topics if t['tier']==tier for p in t['prerequisites'] if bytopic[p]['tier']!=tier})
 for i,p in enumerate(external):ch['quest_links'].append({'id':ident('link:'+ch['filename']+':'+p),'linked_quest':entry_by_key[p]['quest'],'x':float(i%6*3),'y':float(-8-i//6*3)})
allids=[c['id'] for c in chapters]+[id for e in manifest for id in (e['quest'],e['task'])]+[x['id'] for c in chapters for x in c['quest_links']];assert len(allids)==len(set(allids))
for chapter in chapters:save('src/main/resources/assets/hk3gtl/ftbquests/chapters/'+chapter['filename']+'.snbt',chapter)
save('src/main/resources/data/hk3gtl/guide/quest_catalog.json',{'schema':1,'revision':131,'_comment':'【变更记录 #1】'+NOW+'（修订131）：17个电压页，153任务；现有任务ID、真实前置与完成来源不变。','chapters':[c['filename'] for c in chapters],'entries':manifest})

# 【变更记录 #2】2026-10-01 16:16:03（修订133）：删除活动生成器的132横向应用，完整草稿留存在logs/welcome-r133/before；新增暂停边界；恢复已部署131逻辑，不执行新任务生成或定案。
print(json.dumps({'chapters':len(chapters),'quests':len(manifest),'research':len(topics),'automated':sum(e['kind']!='reading' for e in manifest),'reading':sum(e['kind']=='reading' for e in manifest)},ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
