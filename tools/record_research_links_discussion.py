"""变更#1：2026-09-28，记录恢复研究讨论的用户决定及本轮源码核对；不改游戏。"""
from pathlib import Path
import datetime,json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
now=datetime.datetime.now().astimezone();stamp=now.strftime('%Y-%m-%d_%H-%M-%S')
report=ROOT/'logs/research-migration-20260928/evidence-links-20260928-035524.json'
a=json.loads(report.read_text(encoding='utf-8'));rows=a['rows'];reachable=set()
while True:
 before=len(reachable)
 for r in rows:
  if r['evidence_refs'] and set(r['prerequisites'])<=reachable:reachable.add(r['id'])
 if len(reachable)==before:break
assert len(rows)==100 and sum(bool(r['evidence_refs']) for r in rows)==10 and len(reachable)==9
for name,sha in a['source_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
for r in rows:
 for f in r['evidence_refs']+r['gate_refs']:
  assert 1<=f['line']<=len((ROOT/f['file']).read_text(encoding='utf-8').splitlines())
plan=ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
s=plan.read_text(encoding='utf-8');anchor='research-links-20260928-035524'
note='<p><b>不能把10个证据入口当成10个可完成课题：</b>仅按已定位证据与课题前置计算，9项形成前置闭包；RN-CFR还要求RN-SSC，而SSC证据入口未接。此计算未包含费用、设备、电压和物料可达性，9项也不是游戏通过数。</p>'
start=s.index('id="'+anchor+'"');end=s.index('</section>',start)
if note not in s:s=s[:end]+note+s[end:];plan.write_text(s,encoding='utf-8')
# 只提取本轮新增脚本做语法检查，不执行历史脚本。
section=s[start:s.index('</section>',start)]
assert section.count('class="research-links-row"')==100
script=re.search(r'</section><script>(.*?)</script>',s[start:],re.S)[1]
(report.parent/'evidence-links-filter.js').write_text('// 2026-09-28：本轮课题筛选脚本的语法检查副本。\n'+script,encoding='utf-8')
validation={'time':now.isoformat(),'topics':100,'evidence_topics':10,'catalog_evidence_closure':sorted(reachable),'source_hashes_unchanged':True,'source_reference_lines_valid':True,'discussion_only':True,'game_tested':False}
(report.parent/'evidence-links-validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
body=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>恢复研究讨论：100课题证据与解锁</title><style>body{{max-width:1120px;margin:35px auto;padding:20px;background:#111b29;color:#e3edf7;font:16px/1.8 'Microsoft YaHei'}}a{{color:#9adee2}}li{{margin:8px 0}}</style><h1>恢复研究讨论：100课题证据与解锁</h1><p>记录时间 {now.isoformat()}，Asia/Hong_Kong。用户消息原始精确时间未取得，记录时间不代替原消息时间。</p><h2>用户要求与范围</h2><blockquote>“我暂时放弃对于多方块结构样子的讨论，我们回去讨论刚刚剩下的研究系统吧。”随后确认：“从‘100课题的证据来源与解锁对象’继续”。</blockquote><p>已确认：暂停外观讨论、保留69座预览待审，回到研究设计收口。沿用先讨论清楚再修改生产代码的要求；本轮仅核对和补充现有计划页。</p><h2>接续依据</h2><p>已读9月22日研究首轮裁定和研究确认记录、9月28日三份研究决策JSON、100课题接线候选与数值候选；核对当前目录、配方注册、实验输出回调、研究开始检查和门槛查询。终端实际执行Get-Location成功。可用工具未发现context-gatherer，不冒称调用。</p><h2>当前源码观察</h2><ul><li>100课题分布：S01 25项，S02 28项，S03 19项，S04 21项，S05 7项。</li><li>10项存在生产证据入口：HED、HSA、LSE、LES、BCE、DMT、SMR、HFB、FRP、CFR；90项尚未定位。</li><li>7项定位到直接RN生产门槛：HSA、LSE、LES、BCE、DMT、HFB、RCA。研究前置收益单独存在，不能据此说其他93项全部无用。</li><li>现有证据＋研究前置仅形成9项闭包；CFR仍缺SSC前置证据。未证明9项物料、费用、电压或游戏可达。</li><li>FRP已有样件检测，正式I18封装收益未接；RCA已有部分重构门槛，缺自身证据；SMR当前基础和扩展回收都在BCE下，独立收益需区分；电路与部件仍可见旧R-*门槛，迁移尚未落实。</li><li>实验记录仍为个人UUID的课题字符串集合，在线玩家用于归属检查；无法满足已定固定团队、离线记账及原始来源要求。</li></ul><h2>历史范围纠正</h2><p>本轮先提出I46–I53保留独立或合并的问题；随后找到2026-09-21 23:32记录，明确此前暂按77座（69＋8）推进。已向用户补充说明：69座预览范围不能被解释为取消8台工艺，未收到明确改动前保留独立职责。</p><h2>本轮提问（截至记录时间未收到答复）</h2><ol><li>100课题引用I46～I53八台补充设备，保留独立设备还是先给合并方案？助手初荐合并，后补充既有77座暂定依据；初荐不视为用户决定。</li><li>SMR完成后解锁分析试剂、冷却剂及残液扩展回收，OPR提高效率，基础再生预先可用，是否采用？这是新收益划分提案，待用户答复。</li></ol><h2>已确认而不重复询问的规则</h2><p>个人点数、团队研究；真实实验后记录；固定机器团队归属及离线记账；完成证据继承并保留来源；研究点或材料二选一且开始扣费；仅原付款人取消，全额退款且材料待领取；不复制在研进度；前级专用试验样件避免自锁；舰船档案来自I26真实任务、I32解析。20%概率与第5次保底仍是助手数值候选。</p><h2>产物、检查与下一步</h2><p>追加现有计划页100项当前源码对照，保存JSON及输入源码哈希；检查覆盖100项、10个入口、7个门槛课题、引用行号有效，确认游戏源码及目录资源哈希未变。未编译、部署或游戏测试，未新增或删除研究ID。</p><p>下一步优先把S01的25课题逐项完成“前级输入→实际实验→证据→研究→正式收益”的设计收口，保留既有100项路线，集中讨论真正影响玩法的缺口；结构外观保持暂停。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">100课题当前对照</a> · <a href="2026-09-21_23-32_工业能力矩阵暂定推进.html">77座阶段性依据</a> · <a href="../../../logs/research-migration-20260928/evidence-links-20260928-035524.json">当前源码检查</a></p><footer>变更#1：新增本轮记录，删除无，保留历史；用途是记录已确认、提案、未实施和检查边界。</footer></html>'''
record=ROOT/'doc/HK3GTL-内测5/讨论记录'/(stamp+'_研究100课题证据与解锁复核.html')
with record.open('x',encoding='utf-8') as f:f.write(body)
print(str(record));print(json.dumps(validation,ensure_ascii=False))
