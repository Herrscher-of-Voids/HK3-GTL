"""变更#1：2026-09-28，按用户最新答复记录SMR/OPR分工，提出八台补充设备职责合并。
仅追加讨论与计划页；不修改机器注册、配方、结构、费用或课题资源。
"""
from pathlib import Path
import datetime,json,html
ROOT=Path(__file__).resolve().parents[1]
now=datetime.datetime.now().astimezone();stamp=now.strftime('%Y-%m-%d_%H-%M-%S')
topics={n['id']:n for n in json.loads((ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json').read_text(encoding='utf-8'))['topics']}
def ancestors(k):
 a=set(topics[k]['prerequisites'])
 for p in list(a):a.update(ancestors(p))
 return a
rows=[
('I46','换热与冷却循环','RN-HLC',['I05'],['RN-BCE'],
 'I05增设热交换工况；保留原有介质再生，反应堆热冷却剂走独立配方组。',
 'I19实际产出热冷却剂→前级GT换热试验→取得HLC证据；不要求先有正式闭环。',
 'HLC开放反应堆冷却闭环，带损耗与补液；SMR仅开放分析线冷却剂净化，两者不能混成一个收益。起步I19必须能靠新鲜冷却剂及热液暂存运行。'),
('I47','失活燃料后处理','RN-SFR',['I05'],['RN-BCE'],
 'I05增设屏蔽拆解、分离与废液固化工况；各步保留不同输入输出，不合成一条万能回收配方。',
 'I19真实产出失活棒→前级GT制作并检测屏蔽拆解试件→取得SFR证据。',
 'SFR开放棒壳与有限材料回收及残渣处置；不恢复原燃料全能量，不依赖尚未研究的I16魂钢机床。'),
('I48','基础基板制造','RN-CBS',['I12'],['RN-NSP'],
 'I12以受控纳米群进行定向生长和基板沉积；保留其纳米群编程职责，新增受研究控制的基板工况。',
 'NSP开放受控纳米群→前级GT载体上制生长试片→已有分析工序检测→取得CBS证据。',
 'CBS开放基础载体基板量产；早期BCE适配基板保留，不改为必须依赖新基板，首批也不要求魂钢。'),
('I49','多层电路蚀刻','RN-MCE',['I16'],['RN-SPM'],
 'I16增设掩模加工、导体布线与多层蚀刻工况。需要扩展相应配方类型和流体能力，现有端口是否足够尚未认定。',
 'CBS基础基板＋SPM可得导体和掩模→前级GT蚀刻试片→检测→取得MCE证据。',
 'MCE开放正式多层电路层；第一枚种子电路继续走前级可达GT/GTL封装路径，不依赖CPT。具体七条电路材料支线仍独立待定。'),
('I50','电路封装与工况测试','RN-CPT',['I16'],['RN-SPM'],
 'I16增设精密封装和电气终检，两道工序分开；与机械加工、蚀刻共用机器但各有课题门槛。',
 '前序电路层＋魂钢载体→已可用GT/GTL封装试件→温度及绝缘工况检测→取得CPT证据。',
 'CPT开放专用封装与终检流程，CQS后续扩展高阶工况；首机和第一枚新级电路不得消耗尚未制造的新级电路。'),
('I51','无人作业装置装配与返修','RN-UAA',['I11'],['RN-NRA'],
 'I11增设探针/无人作业装置精密装配，I16供给魂钢机械件；执行任务仍归I26，装配与任务结算分开。',
 '魂钢机械件＋已掌握电路和驱动件→前级GT台架试验→导航/执行器检测→取得UAA证据；不依赖世界泡采掘残片。',
 'UAA开放装置制造；RN-UPR才开放磨损装置返修，不在UAA一并赠送维修收益。返修消耗旧件并保留装置来源，不同时返还新旧两件。'),
('I52','气体净化与过滤介质回用','RN-GPR',['I05'],['RN-BCE'],
 'I05增设气液洗涤、过滤介质再生工况；与液态介质再生分配独立配方，不改变采集塔职责。',
 '三阶塔气态样本＋既有过滤材料→前级GT小批洗涤对照→气体成分检测→取得GPR证据。',
 'GPR开放气体净化和对应耗材回用；第一轮气态生产允许新鲜气体启动，不依赖自己的回收产物。'),
('I53','世界泡约束容器制造','RN-BCC',['I16','I33'],['RN-SPM','RN-DKE'],
 'I16制造魂钢空壳与精密接口；I33负责空间/约束组件装配、密封及场稳定校准。',
 '已解锁空间/约束组件＋空壳试件→I33仅进行空载密封与约束测试→取得BCC证据；试验件不能装真实世界泡。',
 'BCC开放正式空容器；后续WBC才开放捕获，不要求先捕获世界泡制造容器。I33已由JOK前置链上的DKE开放。')]
result=[]
for old,name,topic,machines,required,design,evidence,unlock in rows:
 parents=ancestors(topic);assert set(required)<=parents,(topic,required,parents)
 result.append(dict(old_machine=old,function=name,topic=topic,receiving_machines=machines,receiving_unlocks=required,design=design,evidence=evidence,unlock=unlock,prerequisite_check='接收设备的设计解锁课题均为本课题祖先；不等于其代码或物料已经可达'))
record={'time':now.isoformat(),'confirmed':{'merging':'保留工艺，先给逐台合并方案；未批准八项具体映射','SMR':'扩展回收种类','OPR':'提升回收效率'},'proposal':result,'code_changed':False}
out=ROOT/'logs/research-migration-20260928'/('machine-merge-proposal-'+stamp+'.json')
out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
esc=lambda x:html.escape(str(x),quote=True)
anchor='research-merge-'+now.strftime('%Y%m%d-%H%M%S')
parts=[f'<section id="{anchor}" class="panel"><h2>八台补充设备的工艺合并方案</h2><p>{esc(now.isoformat())}。用户已确认保留工艺并先看逐台合并方案；以下映射全部是待审提案，尚未修改注册、结构或配方。</p><p><b>已确认：SMR扩展回收种类，OPR提升效率。</b>基础介质再生在SMR研究前可用；SMR开放分析试剂、分析线冷却剂与残液回收。HLC保留反应堆热循环的独立作用，SFR保留失活棒处理，GPR保留气态洗涤与过滤回用。</p>']
for r in result:
 parts.append(f'<article><h3>{r["old_machine"]} {esc(r["function"])} → {"＋".join(r["receiving_machines"])}</h3><p>{esc(r["design"])}</p><p><b>{r["topic"]}证据：</b>{esc(r["evidence"])}</p><p><b>研究后收益：</b>{esc(r["unlock"])}</p><p><b>前置校验：</b>{"、".join(r["receiving_unlocks"])}均在本课题祖先中。该检查仅针对设计前置，不代表接收设备及升级工况已实现。</p></article>')
parts.append('<p>合并后这些工艺集中到I05、I11、I12、I16、I33五座既有机器，不删除课题或压缩工序。I05承担多种回收、I16承担精密制造，因此必须分配配方类型、独立门槛及清楚的界面分类，不能变成无差别万能机器。</p><p>八项具体分配、工况区分及必要功能改造仍待用户审阅。尺寸和外观暂停讨论，不把旧结构直接认定为满足新端口能力。</p><p>变更#合并提案1：追加方案，保留旧77座记录；无生产代码修改。</p></section>')
plan=ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
before=plan.read_text(encoding='utf-8');section='\n'.join(parts);after=before.replace('</body>',section+'\n</body>',1)
assert after.replace(section+'\n','',1)==before;plan.write_text(after,encoding='utf-8')
discussion=ROOT/'doc/HK3GTL-内测5/讨论记录'/(stamp+'_八台补充设备工艺合并提案与回收研究裁定.html')
body=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>八台设备合并提案与回收研究裁定</title><body><h1>八台设备合并提案与回收研究裁定</h1><p>记录时间{now.isoformat()}，Asia/Hong_Kong，原消息精确时间未知。</p><h2>用户答复</h2><p>问题一：I46–I53保留独立或合并？答：“保留工艺，先给我逐台合并方案（推荐）”。问题二：SMR扩种类、OPR提效率？答：“采用：SMR 扩展回收种类，OPR 提升效率（推荐）”。</p><h2>决定与覆盖关系</h2><p>已确认SMR/OPR收益分工。用户要求提出合并方案，允许从9月21日暂定77座方向讨论合并；不等于已经批准具体映射或删除8台。<a href="2026-09-28_03-57-53_研究100课题证据与解锁复核.html">上一条记录</a>的两项待答状态由本条答复补全，其余历史保留。</p>{section}<h2>实际执行与下一步</h2><p>已生成8项映射和独立证据/收益方案，验证接收设备的设计解锁均为对应课题祖先。追加现有计划页，未改游戏代码、资源、配方、注册或存档，未删除或归档。待用户审阅具体分配，再衔接100课题对应关系；继续暂停外观讨论。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">计划页中的完整方案</a></p></body></html>'''
with discussion.open('x',encoding='utf-8') as f:f.write(body)
print(json.dumps({'anchor':anchor,'record':str(discussion),'proposals':len(result),'design_ancestor_checks':8},ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
