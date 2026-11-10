"""变更#1：2026-09-28，细化S01的25课题实验/解锁合同；仅追加讨论设计，不注册游戏内容。
实验名称为设计描述，不冒称已有物品。复用当前真实入口及已确认SMR/OPR分工。
"""
from pathlib import Path
import json,datetime,html,hashlib
ROOT=Path(__file__).resolve().parents[1]
now=datetime.datetime.now().astimezone();stamp=now.strftime('%Y%m%d-%H%M%S')
catpath=ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json'
catalog=json.loads(catpath.read_text(encoding='utf-8'))['topics'];cat={n['id']:n for n in catalog}
audit=json.loads((ROOT/'logs/research-migration-20260928/evidence-links-20260928-035524.json').read_text(encoding='utf-8'))
auditrows={r['id']:r for r in audit['rows']}
# 编号|实验输入来源|制样及验证设施|真实成功条件|研究后正式对象|必须避免的反向依赖
raw='''
HED|奥托首信观察资料、零阶探测器、MAX阶段可得采样耗材|I01-1首次液态采样|采样实际消耗与液体输出提交成功；不要求同意合作|开放HSA研究资格；不重复锁住起步I01/I02|首次采样不能要求HED研究完成
HSA|I01液态样本经GT灌装机封瓶、纸|I02初始光谱实验|实际输出分析样本，保留采样和分析批次来源|I03控制器与初次分馏；标准样本分析|研究前允许初始光谱实验，持有或购买分析样本不能伪造本队证据
LSE|初采液、碳、前级MAX制造滤芯与结晶基质|I03首次分馏|粗液、母液、试剂及杂质全部真实提交；输出阻塞不记账|母液净化、回流、新鲜介质和I04稳定化路线|第一批滤芯不可依赖净化产物；基础介质不能依赖回收废液
LES|I03粗液、净化产物制晶种、新鲜稳定介质与冷却剂|I04稳定化|稳定液、结晶、用后介质和热冷却剂完成真实输出|适配基板制造及I02兼容性实验|研究LES前可执行稳定化实验；初次稳定化不依赖再生介质
BCE|LES后适配基板、MAX电路、纸、MAX传感器|I02现有电路兼容试验|输入提交且对应样件与分析结果真实输出|I05/I06/I07起步控制器及工艺；前级种子电子制造的保留入口|BCE试验不得使用BCE解锁后的CPU/RAM或新级电路
DMT|零阶探测器、参考样本、分析样本、纸与铂箔|I07现有对照校准|输出校准报告并返回原探测器；不是单纯取走探测器|一阶液态探测器制造及高效采集|研究付款不得吞掉唯一升级用报告；采集参考样本按已定规则不消耗
SMR|I04用后稳定介质、已有试剂和残渣|I05基础稳定介质再生|实际完成800mB用后介质的基础回收批次；以真实配方回执为准|扩展分析试剂、分析线冷却剂和其他残液回收|基础再生提前开放；一般排污出口不能全部被SMR锁住
HFB|I04稳定液、稳定介质、燃料基质、结晶与样本|I06已有液态燃料调配|液态燃料与副产物完成结算|液态燃料网络注入、浓缩起步、FRP试验准备|不得用正式燃料棒当作调配实验的第一份投入
FRP|HFB后GT制造棒壳与密封件；100mB液态燃料灌成试验件|GT组装/灌装→I02破坏性隔离检测|消耗试验件并产出不合格棒；现有配方已采用这一路线|I18正式封装工艺与普通可用燃料棒|试验件不可发电；首批壳体不要求魂钢；正式I18不参与自身起步证据
SRE|FRP后可得壳体、密封件、冷却剂与前级绝缘工装|前级GT制安全试件→I02检测|封装冷却相容性与绝缘检测真实完成；取得一份专用安全试验记录|I19控制器、普通燃料棒发电工况及对应冷却/失活棒输出|不要求I19先发电；先用新鲜冷却剂启动，热液和失活棒可暂存
HLC|I19真实生成热冷却剂、前级换热工装与补充冷却介质|前级GT小批换热→I02分析密封取样件|记录一次真实冷热介质交换及损耗；不能只读罐内库存|I05反应堆热循环工况（I46合并候选）|区别SMR的分析线冷却剂净化；不得要求HLC已开放的正式闭环
SFR|I19真实生成失活棒、前级屏蔽拆解工装|前级GT屏蔽拆解样件→I02检验|失活棒被实际处理；仅输出试验残渣与检测件，不作为正式回收批次|I05屏蔽拆解、有限材料回收和残渣处置（I47合并候选）|不要求I16魂钢加工；试验与正式回收不能给同一根棒重复返还材料
RAT|HSA/LES后液态样本、MAX场控制器件、普通屏蔽基材|前级GT制场响应试件→I02干扰对照|同一试件的干扰前后读数形成有效检测回执|I36基础现实稳定锚控制器及基础工况|不要求仿制核心、虚数材料或先运行稳定锚；S01本身仍免受注视度影响
SSP|稳定介质、前级可得金属基材与化工试剂|前级GT微量前驱试样→I02分析|微量试样实际制作并检测；试样不能输入正式纳米群量产配方|I09魂钢前驱液生产|不得用魂钢、I09正式前驱液或待研究新材料制造第一份样件
NBS|I09正式前驱液、前级精细金属与已有分离介质|前级GT小批反应/分离→I02基元检测|试制微结构样件的形态与组分检测成功；不产出可直接用于量产的基元|I10纳米基元合成|试样不能要求I10先合成正式纳米基元
NRA|I10纳米基元、前级电路与驱动材料|前级GT组装台架→I02驱动检测|微执行器完成可启动/停止的真实台架工序；样件只用于检测|I11未编程纳米单元制造|不要求I11正式单元、受控纳米群或未生产的新级电路
NSP|I11未编程纳米单元、前级控制电路和隔离载体|前级GT封装隔离测试载体→I02执行控制对照|实际验证启动、执行与停止指令；测试单元不能当作受控纳米群投入生产|I12受控纳米群制造与控制工况|不得用I12通用受控纳米群证明自己；无自动增长或复制物品机制
CBS|I12受控纳米群、稳定介质、MAX可得载体|前级GT制生长试片→I02检测|试片沉积与绝缘检测真实完成；仅输出检测用试片|I12基础基板生长工况（I48合并候选）|不要求魂钢；BCE早期适配基板路线保留，不回锁起步电子部件
HRC|I12受控纳米群、已有涂覆材料与对照载体|前级GT涂覆试片→I02侵蚀前后对照|包覆层耐受检测完成，残余样件不能代替正式抗性纳米群|I13崩坏抗性包覆工艺|不得消耗未开放的I13正式包覆群制作首个试片
SPC|I13包覆群、前阶模具和压制载体|前级GT压制致密化试件→I02结构检测|试件真实压制并检测；仅为非量产材料样件|I14粗魂钢聚合压铸|不要求粗魂钢或后级魂钢模具，试件不能绕过I14当作魂钢材料
SRA|I14粗魂钢、已有热处理与冷却介质|前级GT热处理试件→I02缺陷检测|退火试件完成热处理和缺陷检验；只作为检测件|I15稳定魂钢退火工艺|不先消耗稳定魂钢；旧直接凝锭路线须在新链落地时逐项迁移，不能绕过整条链
SPM|I15稳定魂钢、前级刀具和夹具|前级GT机床加工试件→I02公差检测|实际加工的公差试件检测成功；不充当正式精密部件|I16魂钢精密加工与后续掩模/导体制造基础|首次刀具和机床不得依赖I16正式精密件
MCE|CBS基础基板、SPM可得导体和掩模|前级GT蚀刻试片→I02绝缘与层间检测|已加工多层试片完成层间连通/绝缘检测，不凭库存授予|I16正式多层电路蚀刻（I49合并候选）及前级可达的种子封装路线|不要求I50/CPT或S02先开放；七条专用电路材料支线仍未定稿
ALE|SPM精密件、MCE电路层及其真实检测记录|S01独立工程试验任务|在现有S01实际耗电运行设施负载试验并输出工程证据，不能点击直接授予|S02控制器及必要功能件；仍需支付研究费用并完成研究|实验在S01完成且单独执行，不能要求S02自证；正式名称与外观仍未确定
OPR|I05介质回收、HLC换热和SFR后处理的真实批次回执|S01独立收支核验任务|至少各一种有效成功批次，核对实际输入输出及损耗；同批重复回调不增加计数|经配平的高效回收配方，基础与SMR扩展路线继续可用|只持有残渣不足以证明收支；不采用统一效率倍率或无损/净产能回收
'''
rows=[]
for line in raw.strip().splitlines():
 short,inputs,facility,success,unlock,guard=line.split('|');key='RN-'+short;n=cat[key];assert n['lab']==1
 rows.append({**n,'inputs':inputs,'experiment_facility':facility,'success':success,'formal_unlock':unlock,'no_self_lock':guard,
  'experiment_recipe_requirements':n['prerequisites'],
  'current_evidence_refs':auditrows[key]['evidence_refs'],'new_names_are_descriptions':True,
  'status':'已有入口待归属/收益修正' if auditrows[key]['evidence_refs'] else '具体实验接线候选，未实现'})
assert len(rows)==25 and {r['id'] for r in rows}=={n['id'] for n in catalog if n['lab']==1}
for r in rows:assert r['id'] not in r['experiment_recipe_requirements']
global_rules=[
 '现有生产配方真实结算已能产生证据的，沿用该入口；不强制再造一份重复实验。',
 '新增试样名称只是设计描述，后续注册时优先复用已有合适物品；不让试样满足正式材料标签或发电/装配配方。',
 'I02只承担本批小型样件检测，不把正式加工转进I02。涉及流体先由前级工序封装取样，保持起步纯物品实验可用；最终仍逐配方核对槽位与供电。',
 '新实验配方最多要求已经完成的前置课题，不要求将被授予证据的课题或其后继。',
 '生产输出实际提交成功才记实验；中断、模拟匹配、输出堵塞及复制报告不记账。重复成功回调以批次唯一键去重。',
 '保存原团队、机器身份、配方/实验类型、成功批次标识、世界时间及必要实际收支。知识继承不重置来源、不复制资源。',
 'ALE工程试验与OPR收支核验是研究前的独立任务，使用S01的现有供电/槽位排程候选；通过后仍需正常支付研究费用，不能直接完成课题。',
 '当前费用与工作量候选保持原状。课题tier不是已经证明可供电；首台设备、能源仓和首枚电路仍需随配方核对。',
 '八台设备合并目前仍为待确认分配；本稿对应合并位置是候选，不自动修改100课题资源里的machines/result。']
out={'time':now.isoformat(),'status':'第一阶25课题接线讨论稿','confirmed_SMR_OPR':True,'rows':rows,'global_rules':global_rules,
 'open_decisions':['八项设备具体合并分配待答复','ALE/OPR独立工程试验使用S01现有研究槽位排程属于本轮提案','七条电路材料支线、全部精确实验消耗与新配方电压尚未定稿'],
 'source_hashes':{str(catpath.relative_to(ROOT)):hashlib.sha256(catpath.read_bytes()).hexdigest()},'game_changed':False}
log=ROOT/'logs/research-migration-20260928'/('s01-experiment-contracts-'+stamp+'.json')
log.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
esc=lambda v:html.escape(str(v),quote=True);anchor='research-s01-'+stamp
parts=[f'<section id="{anchor}" class="panel"><h2>S01第一阶25课题：实验与解锁施工清单</h2><p>变更#第一阶接线1 · {esc(now.isoformat())}。细化既有课题，不新增/删除课题；未修改游戏。SMR/OPR收益分工已确认，其余新工序、设备合并和参数按标注保留待审。</p><ul>']
parts += ['<li>'+esc(x)+'</li>' for x in global_rules];parts+=['</ul>']
for r in rows:
 parts.append(f'<details><summary>{r["id"]} {esc(r["title"])} · {esc(r["status"])}</summary><div style="padding:12px">')
 for label,value in [('实验前研究要求','、'.join(r['experiment_recipe_requirements']) or '无；保留首信观察资料要求'),('投入来源',r['inputs']),('实际执行设施',r['experiment_facility']),('取得证据的成功事件',r['success']),('研究后具体开放',r['formal_unlock']),('自锁/绕过防线',r['no_self_lock'])]:parts.append(f'<p><b>{label}：</b>{esc(value)}</p>')
 parts.append('</div></details>')
parts.append('<p>检查：25项完全覆盖S01，无自身课题作为实验研究门槛；现有入口状态来自本轮源码对照。此检查不是材料、电压、前级机器及整包配方闭合证明。</p></section>')
section='\n'.join(parts);plan=ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
before=plan.read_text(encoding='utf-8');after=before.replace('</body>',section+'\n</body>',1);assert after.replace(section+'\n','',1)==before
plan.write_text(after,encoding='utf-8')
print(json.dumps({'count':len(rows),'existing_evidence':sum(bool(r['current_evidence_refs']) for r in rows),'anchor':anchor,'log':str(log)},ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
