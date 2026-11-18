"""研究讨论用源码对照，保留原100课题提案，追加当前证据与解锁观察。
变更#1：2026-09-28；新增只读扫描及计划页章节，不修改游戏源码、配方或研究数据。
范围：识别本项目实际采用的配方辅助调用；不是Java执行器，不声称整包可达性已证明。
"""
from pathlib import Path
import re,json,datetime,hashlib,html,collections
from audit_industrial_consistency import stripped

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-migration-20260928'
PLAN=ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
JAVA=ROOT/'src/main/java/com/sirin/hk3gtl'
catpath=ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json'
catalog=json.loads(catpath.read_text(encoding='utf-8'))['topics']
old={r['id']:r for r in json.loads((OUT/'evidence-plan-100.json').read_text(encoding='utf-8'))['rows']}
ids={r['id'] for r in catalog};assert len(ids)==100 and ids==set(old)
source={p:stripped(p.read_text(encoding='utf-8')) for p in JAVA.rglob('*.java')}
def ref(p,t,m,detail):return {'file':p.relative_to(ROOT).as_posix(),'line':t.count('\n',0,m.start())+1,'detail':detail}
evidence=collections.defaultdict(list);gates=collections.defaultdict(list);legacy=[]
def add(dest,key,p,t,m,detail):
 if key in ids:dest[key].append(ref(p,t,m,detail))
for p,t in source.items():
 if '/command/' in p.as_posix():continue
 for m in re.finditer(r'recordExperiment\([^;\n]*?"(RN-[A-Z]+)"',t):add(evidence,m[1],p,t,m,'真实输出回调中的固定课题记录')
 if '/recipe/' not in p.as_posix():continue
 for m in re.finditer(r'\.addData\(Hk3LiquidProcessMachine\.EXPERIMENT,\s*"(RN-[A-Z]+)"\)',t):add(evidence,m[1],p,t,m,'配方实验元数据，交由工业输出回调读取')
 # 已人工核对recipe辅助函数参数顺序：类型、ID、电路、时间、门槛、证据。
 if p.name in ('Hk3LiquidLineRecipes.java','Hk3LiquidLoopRecipes.java'):
  for m in re.finditer(r'\brecipe\([^\n]*?,\s*("RN-[A-Z]+"|null)\s*,\s*("RN-[A-Z]+"|null)\s*\)',t):
   detail=m[0].strip()
   if m[1]!='null':add(gates,m[1].strip('"'),p,t,m,detail)
   if m[2]!='null':add(evidence,m[2].strip('"'),p,t,m,detail)
 if p.name=='Hk3LiquidLineControllerRecipes.java':
  for m in re.finditer(r'controller\(provider,[^\n]+?"(RN-[A-Z]+)"\)',t):add(gates,m[1],p,t,m,m[0])
 for m in re.finditer(r'Hk3RecipeResearchGate\.bind\([^;]+?"(RN-[A-Z]+)"\s*\)',t):add(gates,m[1],p,t,m,m[0])
 for m in re.finditer(r'"(R-(?:AB|IM|QT|FN|GR)-\d+)"',t):legacy.append(ref(p,t,m,m[1]))
 # 两组动态门槛数组已沿注册函数核对，不将数组字面量误报为单一配方。
 if p.name in ('Hk3ElectronicRecipes.java','Hk3CircuitManufacturing.java'):
  for m in re.finditer(r'(?:GATES|gates)\s*=\s*\{[^}]+\}',t):
   if '"RN-BCE"' in m[0]:add(gates,'RN-BCE',p,t,m,'首平台电子部件／种子电路生成器的研究门槛；后续平台仍为旧R-*')
assert set(evidence)=={'RN-HED','RN-HSA','RN-LSE','RN-LES','RN-BCE','RN-DMT','RN-SMR','RN-HFB','RN-FRP','RN-CFR'},set(evidence)
special={
'RN-HED':'研究收益主要是开放HSA研究前置；I02初始实验自身当前没有HED配方门槛，证据可先取得但不能越过研究前置。',
'RN-SMR':'基础再生与扩展回收目前都锁在RN-BCE；没有定位到SMR自身的独立生产解锁。建议SMR开放扩展回收、OPR负责效率，待答复。',
'RN-FRP':'有试验样件和I02破坏性检测；未定位以FRP解锁I18正式封装的RN门槛。',
'RN-CFR':'当前浓缩工艺及注入门槛为HFB，CFR证据可提前取得；未定位CFR独立正式制造解锁，需接通后续浓缩燃料工艺。',
'RN-RCA':'已有理之重构控制器RN门槛；电路复制另查逐级技术与解析权限，不能由RCA直接获得全部电路。RCA实验入口尚未定位。',
'RN-ALE':'S02升级须在S01完成；研究定义正确，但未定位升级工程实验回调和相应RN控制器门槛。',
'RN-QLE':'S03升级须在S02完成；不得反用世界泡采掘成果起步。',
'RN-ILE':'S04升级须在S03完成；不得要求I35/I37先运行。',
'RN-CLE':'S05升级须在S04完成；不得要求W09先运行。',
'RN-HBD':'已定I26真实任务发现档案→I32解析。20%/第5次保底为已有助手数值候选，尚非用户确认或代码实现。'}
rows=[]
for n in catalog:
 key=n['id'];r=old[key]
 rows.append({**n,'proposal':r['proposed_route'],'route_kind':r['route_kind'],'evidence_refs':evidence[key],
  'evidence_status':'已定位生产入口，未运行验收' if evidence[key] else '未定位生产入口，仍为设计路线',
  'gate_refs':gates[key],'unlock_status':'定位到部分RN生产门槛；不等于所有设计收益已接通' if gates[key] else '未定位直接RN生产门槛；研究前置收益另计',
  'outside_69':[m for m in n['machines'] if re.fullmatch(r'I(?:4[6-9]|5[0-3])',m)],'review':special.get(key,'沿现有具体实验路线接线；核对前级材料、设备、研究门槛及正式收益，不以持有产物替代实验。')})
now=datetime.datetime.now().astimezone();stamp=now.strftime('%Y%m%d-%H%M%S')
summary={'topics':100,'evidence_topics':sum(bool(v) for v in evidence.values()),'missing_evidence_topics':100-sum(bool(v) for v in evidence.values()),
 'topics_with_located_RN_gates':sorted(k for k,v in gates.items() if v),'lab_distribution':dict(collections.Counter(n['lab'] for n in catalog)),
 'outside_69_topics':sum(bool(r['outside_69']) for r in rows),'legacy_recipe_literal_occurrences':len(legacy)}
result={'time':now.isoformat(),'summary':summary,'rows':rows,'legacy_recipe_references':legacy,
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [catpath,*source]},
 'limits':['未执行游戏和运行时配方注册；静态入口不等于可玩','未证明所有物料来源、整包KubeJS与电压可达性','前置树收益与生产解锁分开计数；未定位直接门槛不等于课题无任何作用','不将旧R-*字面量计作RN新门槛；未自动迁移旧研究完成状态']}
out=OUT/('evidence-links-'+stamp+'.json');out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
esc=lambda x:html.escape(str(x),quote=True)
section_id='research-links-'+stamp
parts=[f'<section id="{section_id}" class="panel"><h2>100课题证据来源与实际解锁 · 当前源码对照</h2><p>变更记录#接线复核1 · {esc(now.isoformat())}。只读复核并追加记录，未修改游戏代码。保留此前候选路线，不把候选写成完成。</p>',
 '<p><b>100项定义；10项定位到生产证据入口，90项尚未定位。全部实验目前仍存在个人在线归属限制。</b>现有RN生产门槛涉及7个课题：HSA、LSE、LES、BCE、DMT、HFB、RCA；其中RCA只有解锁端，没有实验入口。其他课题的前置研究作用独立存在。</p>',
 '<p>首先补真实完成→绑定团队证据账本→开始研究→具体生产门槛这条链。目录中的machines/result没有被运行代码自动解释为解锁。</p>',
 '<p>范围衔接：2026-09-21曾暂接受77座方案（原69＋I46–I53），当前69座预览未覆盖8台补充设备。12个课题仍关联它们。在明确修改之前保留独立职责；本次不设计外观。</p>',
 '<p>待讨论：SMR完成后的独立收益建议为扩展回收种类，OPR继续负责效率；基础再生保持研究前可执行。图纸20%/第5次保底沿用已有数值候选，不升级为已批准。</p>',
 '<label>筛选100课题 <input id="research-links-filter" placeholder="编号、名称、证据、机器"></label><p id="research-links-count">100项</p>']
for r in rows:
 parts.append(f'<details class="research-links-row"><summary>{esc(r["id"])} · {esc(r["title"])} · S0{r["lab"]} · {esc(r["evidence_status"])}</summary><div style="padding:12px">')
 for label,value in [('前置研究','、'.join(r['prerequisites']) or '无'),('目录证据',r['evidence']),('现有逐题接线候选',r['proposal']),('研究完成后的设计收益',r['result']),('关联设备（不是自动解锁表）','、'.join(r['machines'])),('当前解锁检查',r['unlock_status']),('需收口事项',r['review'])]:parts.append(f'<p><b>{label}：</b>{esc(value)}</p>')
 for label,refs in [('真实证据入口',r['evidence_refs']),('已定位生产门槛',r['gate_refs'])]:
  if refs:
   parts.append('<h4>'+label+'</h4>')
   for f in refs:parts.append(f'<p><code>{esc(f["file"])}:{f["line"]}</code><br>{esc(f["detail"])}</p>')
 parts.append('</div></details>')
parts.append(f'<p><a href="../../../{out.relative_to(ROOT).as_posix()}">完整源码索引、统计与输入哈希</a></p><p>未修改生产代码、未编译、未部署、未启动游戏。本轮是讨论前的源码对照，不是100课题验收。</p></section><script>document.getElementById("research-links-filter").oninput=function(){{let n=0;document.querySelectorAll(".research-links-row").forEach(e=>{{e.hidden=!e.textContent.toLowerCase().includes(this.value.toLowerCase());if(!e.hidden)n++}});document.getElementById("research-links-count").textContent=n+"项";}};</script>')
section='\n'.join(parts);before=PLAN.read_text(encoding='utf-8');assert '</body>' in before
after=before.replace('</body>',section+'\n</body>',1);assert after.replace(section+'\n','',1)==before
PLAN.write_text(after,encoding='utf-8')
assert len(re.findall('class="research-links-row"',section))==100
assert set(summary['topics_with_located_RN_gates'])=={'RN-HSA','RN-LSE','RN-LES','RN-BCE','RN-DMT','RN-HFB','RN-RCA'}
print(json.dumps({'summary':summary,'report':str(out),'anchor':section_id},ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
