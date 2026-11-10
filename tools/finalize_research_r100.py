"""修订100交付记录：只整理本次研究文件备注、发布说明和可核对的讨论记录。
不修改玩家存档，不构建或部署；验证结果由后续交付脚本追加。
"""
from pathlib import Path
from datetime import datetime
import json, re, hashlib, html

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-mainline-r100'
now=datetime.now().astimezone()
stamp=now.strftime('%Y-%m-%d %H:%M:%S')
descriptions={
 'Hk3Gtl.java':'初始化可选FTB研究团队桥接，保留其他系统注册。',
 'Hk3ResearchAccountCommands.java':'提供个人账本查询、原付款人取消、材料领取及原队管理者授权重绑入口。',
 'Hk3CommunicationData.java':'增加服务端账本读取入口，使已收观察资料不依赖玩家在线。',
 'Hk3ResearchTerminalWidget.java':'显示取消、领取和独立实验入口；按实际供电档位展示电流，新增区域沿用缩放逻辑。',
 'Hk3WorkableMultiblockMachine.java':'持久化独立研究团队归属；离队不迁移机器，重绑要求原队权限且无进行中的批次或研究。',
 'Hk3HonkaiAbsorptionMachine.java':'I01真实采样成功按固定团队记录证据，已收资料与绑定人离线分开判断。',
 'Hk3LiquidProcessMachine.java':'I03至I05真实输出结算按固定团队授权并记录来源，离线不伪造或漏记已完成实验。',
 'Hk3ResearchComputerMachine.java':'有电且区块加载时向绑定人的个人账户产点，不再要求本人在线。',
 'Hk3ResearchInstituteMachine.java':'团队共享任务、成员个人付款、全队离线暂停正式研究；实验固定速度续做，空闲不计算注视度。',
 'Hk3SpectrumAnalysisMachine.java':'I02真实光谱输出按固定团队记证据，离线读取既有观察资料。',
 'Hk3Network.java':'协议13升至14，避免旧客户端错用新增研究布局与供电字段。',
 'Hk3LiquidLineRecipes.java':'分析试剂、冷却剂和残液的扩展回收改由RN-SMR开放；基础再生保留原起步门槛。',
 'Hk3ResearchData.java':'同一SavedData保存团队知识、个人付款、任务及待领退款；完成成果迁移、在研不复制、解散退款。',
 'Hk3LabExperimentRules.java':'只定义获批ALE及ERM两阶段固定实验，不把缺完整生产账本的OPR作为已接通实验。',
 'Hk3LabExperimentService.java':'按获批样件与工装实际扣入托管，ALE使用MAX、ERM使用QSV，只有成功实验才记证据。',
 'Hk3MaterialAllocation.java':'保留最大流扣料分配，并返回逐需求分配以区分耗材与不消耗工装。',
 'Hk3RecipeAccess.java':'HK3归属机器的RN配方权限读取固定团队账本，绑定人离线不自动丢失已完成知识。',
 'Hk3ResearchManager.java':'RN研究判定和同步读取当前团队知识，保留未迁移旧研究分支。',
 'Hk3ResearchMaterialPayment.java':'独立实验统一分配实际物品与NBT，将耗材及工装区分存入支付快照。',
 'Hk3ResearchMath.java':'落实获批复合压力、三倍加速上限及逐材料敏感度；S01免压，额外材料向上取整。',
 'Hk3ResearchPlans.java':'加载100题实际EU/t及材料敏感度，校验数值，不以目录存在代替执行接线。',
 'Hk3ResearchStartService.java':'从个人账户付费给固定团队任务，使用批准EU/t并保存实际支付，不重算存量收据。',
 'Hk3ResearchTeams.java':'可选FTB团队事件触发重新对账；共享已完成知识与来源，原队待研任务不跟随付款人迁移。',
 'Hk3ResearchWorkQueue.java':'增加原任务取消及归属快照，正式课题与独立实验共享槽位、持久化进度和重复tick防护。',
 'LabExperimentTest.java':'验证固定实验离线续做、停电暂停、重启、防重复扣费及工装原NBT返还。',
 'ResearchExecutionTest.java':'验证批准压力公式、材料敏感度、100题与255750点总成本。',
 'ResearchTeamTest.java':'验证个人付款、离队与解散、完成后解锁、全队离线暂停及退款幂等和证据来源继承。',
}
changed=[]
for name,description in descriptions.items():
 matches=list((ROOT/'src').rglob(name))
 assert len(matches)==1,(name,matches)
 path=matches[0];text=path.read_text(encoding='utf-8')
 marker='R100_FINAL_RECORD'
 if marker not in text:
  numbers=[int(x) for x in re.findall(r'变更记录\s*#(\d+)',text)]
  number=max(numbers,default=0)+1
  comment=(f'\n/**\n * 【文件职责／本轮边界】{description}\n'
   f' * 【变更记录 #{number}】{stamp}（第 {number} 次编号备注 · 内测5修订100）\n'
   ' * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。\n'
   f' * 新增／修改：{description}\n'
   ' * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。\n'
   ' * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。\n'
   f' * 追溯：logs/research-mainline-r100；{marker}。\n */\n')
  pos=text.index('\n',text.index('package '))+1
  path.write_text(text[:pos]+comment+text[pos:],encoding='utf-8')
 changed.append(path.relative_to(ROOT).as_posix())

build=ROOT/'build.gradle';text=build.read_text(encoding='utf-8')
if 'R100_FINAL_RECORD' not in text:
 text+=f'\n// 变更记录 #20 · {stamp} · 内测5修订100 · R100_FINAL_RECORD。\n// 删除：无。新增：可选FTB编译接口及团队、实验两项检查。修改：纳入check；用途：验证真实账本，不更换实例依赖。\n'
 build.write_text(text,encoding='utf-8')
changed.append('build.gradle')

for lang in ('zh_cn','en_us'):
 path=ROOT/f'src/main/resources/assets/hk3gtl/lang/{lang}.json'
 data=json.loads(path.read_text(encoding='utf-8'))
 data['hk3gtl.welcome.release.0_5_0.1']=('修订100：研究采用团队知识与个人付款，新增取消退款、实验托管及离线产点。' if lang=='zh_cn' else 'Revision 100: shared team research, personal payments, cancellation refunds, experiment escrow and offline point production.')
 data['hk3gtl.welcome.release.0_5_0.2']=('100题费用已更新；后续真实实验、设备与高阶研究所仍未全部接通，不代表全研究链已完成。' if lang=='zh_cn' else 'Costs for 100 topics are updated. Later experiments, machines and higher institutes are still incomplete; the full research chain is not yet playable.')
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');changed.append(path.relative_to(ROOT).as_posix())

path=ROOT/'src/main/resources/assets/hk3gtl/changelog.json'
data=json.loads(path.read_text(encoding='utf-8'))
assert data['entries'][0]['revision'] in (99,100)
entry={'version':'0.5.0','revision':100,'codename':'HK3GTL-内测5','date':now.strftime('%Y-%m-%d'),'time':now.strftime('%H:%M:%S'),
 'reason':'集中推进已批准的研究主链，分离团队知识、个人支付和真实实验。',
 'changes':[
  '修改：100课题使用批准费用、EU/t与材料敏感度，总研究点255750；压力三公式与S01免压规则落地，已开任务保留原收据。',
  '新增：FTB团队知识、固定机器研究归属、个人付款；离队继承完成成果，任务留原队；解散自动退款。',
  '新增：原付款人取消及原样NBT材料待领账本；研究所界面与/hk3research提供查询、取消、领取和授权重绑。',
  '新增：ALE及ERM基线/辅助实验执行器、共享槽位、投入托管、断电续做、取消全退、成功返还工装；实验不直接完成课题。',
  '修改：I01至I05实际产出按绑定团队记证据；个人计算机离线可产点；正式研究全队离线暂停；RN-SMR开放扩展回收。',
  '修改：五阶研究所采用批准命名，前档供电界面同步；协议14要求客户端和服务端同版。',
  '边界：未新增高阶研究所结构；多数后续真实生产接线、OPR完整批次核验、锚覆盖及ERM/W13实际加速仍未完成。',
  '测试与部署另记；保留贸易撤销状态，不将本轮称为100课题全部可玩。']}
data['entries']=[entry]+[e for e in data['entries'] if e.get('revision')!=100]
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');changed.append(path.relative_to(ROOT).as_posix())
changed.append('src/main/resources/data/hk3gtl/research/research_costs.json')

record=ROOT/f'doc/HK3GTL-内测5/讨论记录/{now:%Y-%m-%d_%H-%M-%S}_研究主链修订100实现与未完成边界.html'
body=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>研究主链 · 修订100</title>
<style>body{{background:#101620;color:#e5edf8;font:16px/1.8 system-ui;max-width:1100px;margin:auto;padding:36px}}h1,h2{{color:#adceff}}a{{color:#a6dcff}}li{{margin:10px 0}}.warn{{border-left:4px solid #ffc46b;padding:16px;background:#29231d}}code{{color:#afdfc9}}small{{color:#a0b2c6}}</style>
<h1>研究主链 · 修订100实现记录</h1><p>{stamp}（Asia/Hong_Kong）｜用户要求：集中完成研究主链。</p>
<p class="warn">这是已接入代码的一批研究基础流程，不是100课题全链竣工报告。代码测试、真实机器生产、整包游戏验收分别统计；没有将目录、前端按钮或测试构造记录算作玩家实际完成。</p>
<h2>本轮落实</h2><ul>{''.join('<li>'+html.escape(x)+'</li>' for x in entry['changes'][:6])}</ul>
<h2>玩家入口与归属</h2><p>现有S01研究界面新增“取消本人任务”“领取材料退款”“启动独立实验”。只有原付款人能取消。离队后可用 <code>/hk3research account</code> 查看本人任务，再用 <code>/hk3research cancel 团队UUID 课题ID</code> 取消；<code>/hk3research claim</code> 领取材料。背包放不下的继续留账。</p>
<p><code>/hk3research bind x y z 玩家</code> 将机器研究归属绑定到指定在线玩家当前团队。操作者必须靠近控制器、具有原所属团队管理权限，且机器没有进行中的生产或研究。能源所有者不随之改变。</p>
<p>首次升级尚无研究归属字段的机器，首次服务端访问时绑定放置者当时团队。旧个人在研任务不自动挪入团队，也不重算已付费用；原付款人仍可通过个人账本查询并取消。原团队解散后的设施不会自动跟成员迁移。</p>
<h2>实际接线与明确缺口</h2><ul>
<li>I01—I05已有真实产出路径：这次修正团队归属、离线记账及SMR扩展回收门槛，并未凭此宣称后续机器已经存在。</li>
<li>ALE执行器已接入S01，但其已蚀刻电路层等样件仍依赖未完整接线的上游；不能据此称生存路线已打通。</li>
<li>ERM基线／辅助实验已实现执行与托管，但S02正式结构尚未获批和注册，因此没有供玩家使用的正式S02入口。</li>
<li>OPR必须核验I05介质、换热、废棒三类真实结算批次及完整收支；现有生产账本不足，暂不开放虚假实验，也未补造效率配方。</li>
<li>S02—S05的正式结构与多数后续课题生产者、机器／配方解锁仍未接齐。旧R门槛不能按名字批量替换，需按已审映射逐项处理。</li>
<li>锚的50%／75%有效覆盖、ERM每项1A QSV加速、W13授权16任务及1A WSV＋256HW/t成本尚未接入真实设施；本轮运行倍率没有凭空启用这些增益。</li>
<li>七类材料分支的具体未批配方不擅自定案。结构尺寸仍受69座表各轴下限约束。</li></ul>
<h2>验证</h2><p id="validation">费用、团队账本、实验托管专项检查已经执行；最终clean build与JAR核验结果将在交付时追加。没有启动两个整合包，没有进行游戏内/FCL验收。</p>
<h2>变更文件与可追溯依据</h2><p>费用依据：2026-09-28 22:23:43批准快照；原全系统审计保留为修改前基线。文件清单及哈希：<code>logs/research-mainline-r100/source-manifest.json</code>。</p><ul>{''.join('<li><code>'+html.escape(x)+'</code></li>' for x in changed)}</ul>
<h2>下一段研究接线顺序</h2><ol><li>先补S01工业链真实样件来源与实验生产结算，逐题验证证据—付款—完成—配方开放。</li><li>补OPR批次收支核验，不以虚构记录解锁。</li><li>高阶研究所正式结构批准后接入S02—S05，再逐段落地后续工艺和研究解锁；缺结构不算完成。</li><li>最后接入真实锚、侵蚀模块和W13授权加速，执行双底包与低内存游戏验收。</li></ol>
</html>'''
record.write_text(body,encoding='utf-8')
manifest={'revision':100,'time':now.isoformat(),'discussion':str(record),'files':[{ 'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in changed],
 'non_java_record':{'number':1,'timestamp':stamp,'deleted':'无无关资源删除','added':'团队及实验测试构建依赖、玩家说明与交付记录','modified':'批准费用、敏感度、语言名与界面提示','purpose':'费用及UI数据与服务端执行一致，不等同游戏验收'}}
(OUT/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'discussion':str(record),'files':len(changed),'timestamp':stamp},ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
