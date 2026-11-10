"""修订101：记录已授权的代码、暂定数值及真实缺口；不部署、不改存档。"""
from pathlib import Path
from datetime import datetime
import json,re,hashlib,html

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-mainline-r101'
BASE=ROOT/'src/main/resources/data/hk3gtl/research'
now=datetime.now().astimezone();stamp=now.strftime('%Y-%m-%d %H:%M:%S')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
E=read(BASE/'research_execution.json')['topics'];P=read(BASE/'industrial_processes.json')['recipes']
C={c['id']:c for c in read(BASE/'research_costs.json')['topics']}
assert len(E)==100 and len({p['id'] for p in P})==len(P)
descriptions={
 'Hk3FirstContactService.java':'真实回复与登录时已存回复核验接入交流前置，阅读本身不授予实验。',
 'Hk3CommunicationResearchProof.java':'仅以服务端已确认回信账本提供交流前置，追溯核验不补造历史时间、不直接完成课题。',
 'Hk3ResearchTeams.java':'换队重新核验本人已完成交流，原生产批次仍留原队。',
 'Hk3ResearchTerminalWidget.java':'展示经批准的证据来源与成功要求，区分未完成实验和未付款研究。',
 'Hk3MultiRecipeLogic.java':'多配方采用统一研究权限检查，修复离线绑定人导致的旧式阻塞。',
 'Hk3HonkaiAbsorptionMachine.java':'首次真实采样输出提交液态采集批次，不通过库存或旧研究ID授予。',
 'Hk3LiquidProcessMachine.java':'保留合并批次的全部权限与工艺回执，真实输出完成才结算研究实验及三类回收来源。',
 'Hk3ResearchInstituteMachine.java':'增加OPR入口、研究所课题权限与完整来源提示，保持未审批高阶结构不注册。',
 'Hk3ResearchProcessMachine.java':'提供后续工艺设备专用执行类；本轮未注册控制器或结构。',
 'Hk3IndustrialRecipeTypes.java':'在既有注册生命周期接入独立工艺类型。',
 'Hk3RecipeAdderImpl.java':'接入暂定工艺配方注册入口；不恢复贸易。',
 'Hk3ResearchProcessPlans.java':'验证暂定工艺的数据类型、研究条件、事实名称、实验契约和输入输出容量。',
 'Hk3ResearchProcessPorts.java':'集中定义已有及待接工艺类型的槽位容量，不等同物理端口审批。',
 'Hk3ResearchProcessRecipes.java':'注册暂定样件、检测和生产配方；按长整数电压计费，未知物料拒绝加载。',
 'Hk3ResearchProcessTypes.java':'注册待接设备的配方类型，保留合并工艺职责，不创建未经审批的机器。',
 'Hk3IndustrialContent.java':'注册检测专用样件及任务资料物品；持有这些物品不能完成课题。',
 'Hk3ResearchData.java':'保存三类回收回执与生产工况；OPR绑定开题时的真实批次快照，生产批次不随队员复制。',
 'Hk3LabExperimentRules.java':'加入S01的OPR固定实验，保持ALE和ERM规则。',
 'Hk3LabExperimentService.java':'OPR耗用三张纸并托管三类回收凭据，成功仅记实验证据，取消沿用原付款人退款。',
 'Hk3ProcessReceipts.java':'保留最终配方收支规格、批次身份与来源；不声称其记录了每个实际抽取槽的NBT。',
 'Hk3RecipeAccess.java':'校验全部前置研究，固定团队知识不依赖绑定人在线。',
 'Hk3RecipeResearchGate.java':'增加多前置绑定，保留旧单前置接口兼容。',
 'Hk3ResearchBatchProofs.java':'检查有效回执及三种互异回收批次，拒绝空数据或重复批次充数。',
 'Hk3ResearchExecutionContracts.java':'载入100题批准来源、真实工况、前置及解锁对象，拒绝漏题与目录内自锁。',
 'Hk3ResearchRecipeRuntime.java':'核对设备类型、工艺身份和全部证据，实际输出成功才记录实验，缺少真实事实时保持锁定。',
 'Hk3WorldBubbleData.java':'新增服务器线程的完成结算接口；尚无实际世界泡机器调用，不宣称物理任务已接通。',
 'Hk3WorldBubbleLedger.java':'模拟创建保留服务端来源回执，跨重启保留同批次身份。',
 'Hk3WorldBubbleResearch.java':'从有效结算事务投影同批次链与不同目标证据，不接受预留、取消、旧无来源记录。',
 'Hk3WorldMiningRewards.java':'保存首次资料与舰船档案20%/第五次保底计算；普通资源池和真实发货尚未接入。',
 'GTRecipeWidgetMixin.java':'JEI显示并校验全部研究前置，不只读第一条。',
 'LabExperimentTest.java':'回归OPR批次快照、托管、取消、重启、继承边界和原有两类实验。',
 'ResearchMainlineTest.java':'验证100题契约、付费状态机、真实批次格式、世界同批次规则和任务资料保证；夹具不等同游戏验收。',
}
changed=[]
for name,desc in descriptions.items():
 matches=list((ROOT/'src').rglob(name));assert len(matches)==1,(name,matches)
 p=matches[0];s=p.read_text(encoding='utf8');marker='R101_FINAL_RECORD'
 if marker not in s:
  n=max([int(x) for x in re.findall(r'变更记录\s*#(\d+)',s)],default=0)+1
  comment=f'\n/**\n * 【变更记录 #{n}】{stamp}（内测5修订101）\n * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。\n * 新增／修改：{desc}\n * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。\n * 追溯：logs/research-mainline-r101；{marker}。\n */\n'
  pos=re.search(r'(?m)^public (?:final |abstract )?(?:class|interface|enum)\b',s).start()
  p.write_text(s[:pos]+comment+s[pos:],encoding='utf8')
 else:
  # 将本轮新备注放在已有历史之后，不删除或改写旧备注内容。
  block=next(m for m in re.finditer(r'/\*\*[\s\S]*?\*/',s) if marker in m.group())
  comment=block.group();s=s[:block.start()]+s[block.end():]
  pos=re.search(r'(?m)^public (?:final |abstract )?(?:class|interface|enum)\b',s).start()
  p.write_text(s[:pos]+comment+'\n'+s[pos:],encoding='utf8')
 changed.append(p.relative_to(ROOT).as_posix())
for lang in ('zh_cn','en_us'):
 p=ROOT/f'src/main/resources/assets/hk3gtl/lang/{lang}.json';v=read(p)
 texts={
 'hk3gtl.research.terminal.experiment.opr':('OPR先核验I05的介质再生、换热、失活棒后处理三份不同成功回执，再投入3张纸，在S01以MAX供电完成90秒收支实验。成功后仍须正常付款研究。','OPR checks three distinct successful I05 receipts: medium regeneration, heat exchange and spent-rod reprocessing. Use 3 paper in S01 for a 90-second MAX-powered audit, then pay for the research separately.'),
 'hk3gtl.research.execution.source':('实验证据来源：%s','Experimental evidence source: %s'),
 'hk3gtl.research.execution.success':('有效完成条件：%s','Successful completion conditions: %s'),
 'hk3gtl.research.terminal.block.experiment':('尚未完成对应的真实实验，请查看证据来源。','Complete the required real experiment; see its evidence source.'),
 'hk3gtl.welcome.release.0_5_0.1':('修订101：补充研究工艺、三类回收核验和实验来源说明，完善团队与离线权限。','Revision 101: additional research processes, three recovery receipts, evidence descriptions and team permissions.'),
 'hk3gtl.welcome.release.0_5_0.2':('后续研究所、世界泡任务、能源调度和奇观验收仍在接入中，100课题尚未全部可玩。','Later institutes, world-bubble missions, energy dispatch and wonder acceptance are still being connected. The full 100-topic chain is not yet playable.')}
 for k,pair in texts.items():v[k]=pair[lang=='en_us']
 write(p,v);changed.append(p.relative_to(ROOT).as_posix())
changes=[
 '100课题执行契约已入代码：批准的证据来源、实验要求、研究前置、设备解锁对象集中校验；它们不是100条实际可玩路径的验收证明。',
 f'新增{len(P)}条明确标注暂定的工艺配方，覆盖制样、检测及部分生产；数量、物料、耗时、电压和副产物完整公开。',
 'OPR接入三类互异回收回执与投入托管；补充全部前置、合并批次、离线权限及已回信存档的前置核验。',
 '世界泡账本增加同批次链、不同目标来源及资料保底，但未接实际任务启动、普通资源池和交付执行器。',
 '高阶研究所和后续工业/奇观结构仍逐台审批；未注册临时结构。缺失HW工况、授权、工程验收等真实事实时保持锁定。',
 '没有恢复贸易；没有以目录、物品持有、旧研究ID或单元测试数据自动授予新研究。',
 '完整构建、游戏验收和部署结果单独记录。']
p=ROOT/'src/main/resources/assets/hk3gtl/changelog.json';v=read(p)
entry={'version':'0.5.0','revision':101,'codename':'HK3GTL-内测5','date':now.strftime('%Y-%m-%d'),'time':now.strftime('%H:%M:%S'),'reason':'落实不依赖未审批结构的研究代码及获准暂定数值，公开余下实际执行缺口。','changes':changes}
v['entries']=[entry]+[x for x in v['entries'] if x.get('revision')!=101];write(p,v);changed.append(p.relative_to(ROOT).as_posix())
build=ROOT/'build.gradle';s=build.read_text(encoding='utf8')
if 'R101_FINAL_RECORD' not in s:
 build.write_text(s+f'\n// 变更记录 #21 · {stamp} · 修订101 · R101_FINAL_RECORD。\n// 删除：无。新增：100题契约与批次检查。修改：加入check；用途：纯代码回归，不冒充实例验收。\n',encoding='utf8')
changed+=['build.gradle','src/main/resources/data/hk3gtl/research/research_execution.json','src/main/resources/data/hk3gtl/research/industrial_processes.json']
changed+=[p.relative_to(ROOT).as_posix() for p in (ROOT/'src/main/resources/assets/hk3gtl/models/item').glob('research_specimen_*.json')]
changed+=[f'src/main/resources/assets/hk3gtl/models/item/{x}.json' for x in ('world_mining_legacy_record','ship_engineering_archive')]
changed+=['tools/research_r101_contracts.py','tools/research_r101_recipes.py','tools/check_research_r101_dependencies.py','tools/finalize_research_r101.py']
e=lambda x:html.escape(str(x))
def table(headers,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(cell)+'</td>' for cell in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def joined(xs):return '<br>'.join(e(x) for x in xs) or '—'
def parts(xs,unit):return joined(f"{x['id']} × {x[unit]:,}"+(' mB' if unit=='amount' else '') for x in xs)
voltext=(ROOT/'src/main/java/com/sirin/hk3gtl/common/constants/Hk3ValuesImpl.java').read_text(encoding='utf8').split('long[] VA_LONG = {')[1].split('};')[0]
voltext=re.sub(r'//[^\n]*','',voltext);volt=[9223372036854775807 if 'Long.MAX_VALUE' in x else int(x.strip().rstrip('L')) for x in voltext.split(',') if x.strip()]
assert len(volt)==31
names=['ULV','LV','MV','HV','EV','IV','LuV','ZPM','UV','UHV','UEV','UIV','UXV','OpV','MAX','HBV','HCV','HRV','HDV','QSV','QCV','QEV','QAV','IMV','ICV','IRV','IWV','WFV','WSV','CIV','CEV']
by={p['id']:p for p in P};producers={f for p in P for f in p['facts']}
special={'liquid_collection','formal_communication','recovery_medium','recovery_heat','recovery_spent_rods'}
world={'first_mining_legacy','ship_archive','real_capture','real_termination','simulation_created','simulation_stabilized','simulation_full_chain','distinct_mining_routes','distinct_legacy_sources','drone_return'}
missing=sorted({f for t in E for f in t['facts']}-producers-special-world)
old={'RN-HED','RN-HSA','RN-LSE','RN-LES','RN-BCE','RN-DMT','RN-SMR','RN-HFB','RN-FRP','RN-CFR'}
topicrows=[]
for t in E:
 c=C[t['id']];p=by.get(t['recipe'])
 status='已有真实输出回调；本轮未做游戏验收' if t['id'] in old else ('独立实验执行器已接；上游/结构另查' if t['executor'].startswith('S') else ('事务投影已写，物理任务入口待接' if t['id']=='RN-SWS' else '暂定制样/检测配方已写，完整专用工况未逐项游戏验收'))
 waiting=[f for f in t['facts'] if f in missing];w=[f for f in t['facts'] if f in world]
 if waiting:status+='；缺工况：'+','.join(waiting)
 if w:status+='；依赖待接世界任务：'+','.join(w)
 if t['lab']>1:status+='；S02—S05结构未接'
 topicrows.append([f"<b id=\"{e(t['id'])}\">{e(t['id'])} · {e(t['title'])}</b><br>S{t['lab']:02d} / {e(t['executor'])}",
  e(t['source'])+'<hr>'+e(t['success']),joined(t['prerequisites'])+'<hr>工况：'+joined(t['facts']),
  f"{c['points']:,} 点<br>{c['ticks']:,} tick / {c['ticks']/20:g} 秒<br>{c['eut']:,} EU/t<br>材料替代支付："+joined(f"{m['tag']} × {m['count']}；敏感度 {m['sensitivity']}" for m in c['materials']),
  joined(t['unlocks'])+'<hr>'+e(t['benefit']),e(status)])
reciperows=[]
for p in P:
 eu=volt[p['energy_tier']];generation=p['role'] in ('I19','I20','I21','I22')
 reciperows.append([f"<b>{e(p['id'])}</b><br>{e(p['role'])}<br>暂定数值",joined(p['requirements']),
  parts(p['item_inputs'],'count')+'<hr>'+parts(p['fluid_inputs'],'amount'),parts(p['item_outputs'],'count')+'<hr>'+parts(p['fluid_outputs'],'amount'),
  f"{p['ticks']:,} tick<br>{p['ticks']/20:g} 秒<br>{names[p['energy_tier']]}<br>{'发电' if generation else '耗电'} {eu:,} EU/t<br>每批 {eu*p['ticks']:,} EU",joined(p['facts'])+'<hr>实验：'+e(p['experiment'] or '无')])
summary={'revision':101,'generated_at':now.isoformat(),'contracts':len(E),'provisional_recipes':len(P),'missing_fact_producers':missing,'world_machine_callbacks_connected':False,'structures_approved':False,'full_chain_playable':False,'gameplay_verified':False,'deployed':False}
write(OUT/'delivery-status.json',summary)
record=ROOT/'doc/HK3GTL-内测5/讨论记录/研究主链修订101_完整数值与接线清单.html'
style='body{background:#111824;color:#e3ecf6;font:15px/1.65 system-ui;margin:0;padding:28px}h1,h2{color:#a9cdff}a{color:#a9ddff}.warn{background:#342a20;border-left:4px solid #ffbd65;padding:18px}.scroll{overflow:auto;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border:1px solid #364455;padding:12px;vertical-align:top;min-width:160px}th{background:#213148}hr{border:0;border-top:1px solid #455064}input{padding:12px;background:#213148;color:white;border:1px solid #63768f;width:min(600px,85%)}nav{margin:20px 0}.sticky{position:sticky;top:0;background:#111824;padding:12px;z-index:3}.muted{color:#afbac8}'
body=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>研究主链修订101：完整数值与接线清单</title><style>{style}</style></head><body>
<h1>研究主链 · 修订101</h1><p>{stamp}（Asia/Hong_Kong）｜100课题执行契约 / {len(P)}条暂定工艺配方</p>
<div class="warn"><b>尚不能称为100题全部完成或全部可玩。</b>已实施代码与真实实例验收分开。用户确认：结构仍须逐台审批；可以实装暂定数量、耗时和能耗。本轮没有注册新结构，没有恢复贸易，也没有用持有物或旧研究ID直接完成新课题。</div>
<nav><a href="#implemented">已写入代码</a> · <a href="#missing">仍未完成</a> · <a href="#topics">100题</a> · <a href="#recipes">全部配方数值</a> · <a href="#validation">验证</a></nav>
<h2 id="implemented">本轮写入代码</h2><ul>{''.join('<li>'+e(x)+'</li>' for x in changes[:5])}</ul>
<p>OPR：S01共用实验槽，三种互异真实回收批次＋3张纸，1,800 tick（90秒）、MAX供电；开题时冻结回执与投入，停电/重启续做，原付款人取消返还投入，已耗电不退。成功仅取得实验来源，之后仍须支付研究费用。</p>
<p>世界泡资料暂定每个成功采掘任务给1份带来源遗留资料，首份必得；舰船档案20%提前发现，最迟第5次成功任务保底。原始普通资源池、实际机器结算和物品交付尚未接入，因此这不是可运行的无人采掘系统。</p>
<h2 id="missing">剩余实际工作</h2><ul><li>S02—S05及后续工业/奇观的正式结构和控制器接入必须逐台获批，不能用临时结构绕过。</li><li>世界泡目标授权、任务执行、4项物品/2项流体资源池、投入托管与实际交付仍未完成；已有事务投影及保底逻辑不能替代它们。</li><li>HW注入与真实负载、手动/自动能源调度、多机订单、舰船与奇观验收、跨域差异等仍缺对应生产事件；缺失时课题保持锁定。</li><li>部分检测配方当前采用统一制样模板；尚需逐项补足批准的温控、对照、前后响应、连续工况等专用行为，不能把检测耗电完成等同所有科学条件均被实现。</li><li>ERM/W13真实授权加速、锚覆盖、原版及增强版的实际注册/GUI/生存可达性验收未完成。</li></ul>
<p>没有生产者的工况：{joined(missing)}</p>
<div class="sticky"><label>筛选条目 <input id="filter" placeholder="课题ID、设备、物料ID、工况…"></label> <span id="count"></span></div>
<h2 id="topics">100课题：证据 → 付款 → 完成 → 开放</h2><p>下列研究费用沿用已批准成本，不是本轮新拟数值；点数与材料按既有支付选择使用，材料按批准的压力与敏感度计价。研究所结构、设备及事件未接入的条目不计为可玩完成。</p>
{table(['课题与设备','批准的来源与有效条件','全部前置/工况','基础研究费用与时间','研究后开放','代码及实际运行边界'],topicrows)}
<h2 id="recipes">{len(P)}条暂定配方：完整数量、耗时与能源</h2><p>本节来自游戏读取的同一JSON。配方电压采用当前16档新缩写；EU与HW不是同一账户。这250条普通配方不自动收费HW；需要HW的实际执行器尚未接通。每批总EU为基础值×基础时长，不含超频/并行。产物列保留副产物；未逐项完成元素/能量守恒及收益平衡审核。</p>
{table(['配方ID / 设备','研究门槛','物品与流体投入','物品与流体产出','基础时长与EU','成功工况 / 实验证据'],reciperows)}
<h2 id="validation">验证与部署</h2><div id="validation-result">专项回归已通过；最终clean build结果待追加。尚未启动游戏验收，尚未把本轮JAR覆盖到实例。</div>
<p class="muted">源码/数据清单与SHA256：logs/research-mainline-r101/source-manifest.json。已授权讨论记录保留；本页不会覆盖旧修订100结论。</p>
<script>const rows=[...document.querySelectorAll('tbody tr')];document.querySelector('#filter').addEventListener('input',event=>{{const q=event.target.value.trim().toLowerCase();let n=0;rows.forEach(row=>{{row.hidden=!row.textContent.toLowerCase().includes(q);if(!row.hidden)n++;}});document.querySelector('#count').textContent=n+' / '+rows.length;}});</script></body></html>'''
record.write_text(body,encoding='utf8')
discussion=ROOT/f'doc/HK3GTL-内测5/讨论记录/{now:%Y-%m-%d_%H-%M-%S}_研究主链修订101代码与暂定数值交付记录.html'
discussion.write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>研究主链修订101讨论记录</title><style>{style}</style><h1>研究主链修订101</h1><p>{stamp}（Asia/Hong_Kong）</p><p>用户已确认：仍须逐台审结构，先完成不依赖结构的研究代码；授权暂定数值实装并保留完整表供调整。本轮实际实现与未完成部分见<a href="{record.name}">完整数值与接线清单</a>。</p><p>100题尚未全部可玩；未冒称所有不依赖结构代码完成。已写代码不等同游戏验收。没有恢复贸易，没有注册新结构。</p>',encoding='utf8')
manifest={'revision':101,'timestamp':stamp,'review':str(record),'discussion':str(discussion),'files':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in sorted(set(changed))],
 'resource_record':{'timestamp':stamp,'deleted':'无无关资源删除','added':'执行契约、暂定配方、样件模型、语言及检查工具','modified':'研究来源提示和修订说明','purpose':'实际代码数据与可审核数字一致，不将定义当成实装验收'}}
write(OUT/'source-manifest.json',manifest)
print(json.dumps({'review':str(record),'discussion':str(discussion),'recipes':len(P),'missing_facts':missing},ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
