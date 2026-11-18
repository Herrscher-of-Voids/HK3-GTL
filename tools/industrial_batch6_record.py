"""批次6记录 / Batch 6 records.
变更记录 #1：2026-09-22 16:04:00，新增研究所接入的中英文界面、变更清单与验收证据。
默认只运行一次；--verified核对真实构建后追加，不执行游戏验收或部署。
Run once for records; --verified checks real build artifacts without game launch or deployment.
"""
from pathlib import Path
from datetime import datetime
import json, html, os, hashlib, sys, zipfile

ROOT=Path(__file__).resolve().parents[1]
STAMP=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
REPORT=ROOT/'doc/HK3GTL-内测5/09_测试发布/研究所入口与材料支付_批次6.html'
PROGRESS=ROOT/'doc/HK3GTL-内测5/09_测试发布/代码落实进度与旧实现归档.html'
ANALYSIS=ROOT/'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html'
FILES={
 'src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchInstituteMachine.java':'新增：五阶行为类、一阶实际接入、分页原生UI、主背包材料/点数支付、本机队列运行及所有权复核。',
 'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchPlans.java':'新增：100课题费用、材料、耗时和展示资料加载。',
 'src/main/java/com/sirin/hk3gtl/common/research/Hk3MaterialAllocation.java':'新增：确定性最大流，处理物品标签重叠，不重复计算同一堆材料。',
 'src/main/java/com/sirin/hk3gtl/common/research/Hk3InventoryDebit.java':'新增：生产共用库存快照提交、重复保护、异常回滚组件。',
 'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchMaterialPayment.java':'新增：真实ItemStack适配、36主背包槽与完整NBT付款凭据。',
 'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchData.java':'追加实验记录与按设施获取在研任务，不将支付当作实验完成。',
 'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchWorkQueue.java':'新增不可变设施任务快照。',
 'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchManager.java':'旧右键界面不再拦截新版研究所实例。',
 'src/main/java/com/sirin/hk3gtl/common/machine/Hk3MachinesImpl.java':'原控制器接一阶研究所行为；Pattern不改，旧类保留。',
 'src/main/java/com/sirin/hk3gtl/common/recipe/Hk3RecipeAdderImpl.java':'研究控制器配方改用MAX已有材料/电压，去除崩坏研究产物的起步循环依赖。',
 'src/test/java/com/sirin/hk3gtl/test/research/ResearchMaterialTest.java':'新增1000例分配穷举对照、费用完整性、实验记录、库存事务/NBT/回滚测试。',
 'build.gradle':'新增runResearchMaterialTest并接入check。',
 'src/main/resources/data/hk3gtl/research/research_costs.json':'100课题首轮授权平衡数据，不自动授予实验或知识。',
 'src/main/resources/assets/hk3gtl/lang/zh_cn.json':'新增100课题名称及新版研究所中文界面。',
 'src/main/resources/assets/hk3gtl/lang/en_us.json':'新增100课题英文名称及英文界面标签。',
 'src/main/resources/assets/hk3gtl/changelog.json':'追加revision44。',
 'tools/research_costs.py':'费用数据与课题名称生成脚本。',
 'tools/industrial_batch6_record.py':'本批记录、中英界面标签及验证脚本。',
}
LABELS={
 'header':('研究所 S%s · 并行槽 %s · 研究点 %s','Institute S%s | Slots %s | Points %s'),
 'denied':('无法操作此研究所：请检查归属与距离。','Cannot access this institute: check ownership and distance.'),
 'unformed':('结构未成型：可以查看，不能开题或推进。','Structure not formed: browsing only.'),
 'previous':('上一页','Previous page'), 'next':('下一页','Next page'),
 'done':(' 已完成',' Complete'), 'ready':('已取得','Recorded'), 'missing':('未满足','Missing'),
 'cost':('费用：%s点 或 下列材料；基础耗时：%s秒；需要 S%s','Cost: %s points OR materials below; base time: %s seconds; requires S%s'),
 'evidence':('实验凭据：%s','Experimental evidence: %s'),
 'prerequisite':('前置：%s · %s','Prerequisite: %s | %s'),
 'material':('材料：%s × %s（兼容同标签物品）','Material: %s x %s (equivalent tagged items accepted)'),
 'unavailable_material':('当前整合包没有可用材料','No matching material in this pack'),
 'pay_points':('使用研究点开题','Start with points'), 'pay_materials':('使用背包材料开题','Start with inventory materials'),
 'locked':('尚未满足结构、研究所阶级、知识或实验前置。','Structure, institute level, knowledge or experiment prerequisites are missing.'),
 'insufficient':('主背包中的所需材料不足。','Insufficient materials in main inventory.'),
 'started':('开题成功，费用已扣除。停机保留进度。','Research started and paid. Stopping preserves progress.'),
 'rejected':('未开题也未扣费：请检查余额、空闲槽位及是否已在研或完成。','No charge: check funds, slots and existing/completed research.'),
 'tooltip':('一阶研究所：1项并行，开题扣研究点或背包材料；一阶免受注视减益，实验仍需完成。','S01 institute: 1 topic, pay points or inventory materials at start; immune to gaze penalties, experiments still required.'),
}

def page(title,body):
 return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>'+title+'</title><style>body{max-width:1100px;margin:auto;padding:28px;background:#101526;color:#edf2ff;font:16px/1.8 system-ui}a{color:#9cdedc}td,th{border:1px solid #506079;padding:8px}table{border-collapse:collapse}</style><body><h1>'+title+'</h1><p>'+STAMP+' Asia/Hong_Kong</p>'+body+'</body></html>'

def append(path,body):
 text=path.read_text(encoding='utf-8'); assert '</body>' in text
 path.write_text(text.replace('</body>',body+'</body>'),encoding='utf-8')

def record():
 for index,lang in enumerate(['zh_cn','en_us']):
  p=ROOT/f'src/main/resources/assets/hk3gtl/lang/{lang}.json'; data=json.loads(p.read_text(encoding='utf-8'))
  for key,values in LABELS.items(): data['hk3gtl.research.lab.'+key]=values[index]
  data['block.hk3gtl.abyss_research_analysis_matrix']=['一阶研究所','S01 Research Institute'][index]
  p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 changes=['现有研究控制器接入S01新版行为，旧研究矩阵类及旧UI保留；Pattern未改，其他四阶结构注册后置。',
  '分页UI由GT/LDLib绑定操作者，服务端复核距离、控制器身份、所有者、成型、知识、实验和费用。',
  '100课题有首轮点数/材料费用和耗时；从主背包36槽支付，不扣装备/副手；材料乘数开题锁定，记录实际ItemStack NBT。',
  '确定性最大流处理标签重叠，付款前复核全部库存；共用提交组件防重复并在异常时回滚。',
  '控制器制造改为MAX材料与电压，避免先有魂钢/崩坏晶体才能建第一座研究所；旧配方已归档。',
  '实验记录独立持久化，生产实验的自动记录尚待接入；不开放无凭据研究。团队、退款及更高阶建筑仍待完成。']
 p=ROOT/'src/main/resources/assets/hk3gtl/changelog.json'; data=json.loads(p.read_text(encoding='utf-8')); assert not any(e.get('revision')==44 for e in data['entries'])
 data['entries'].insert(0,dict(version='0.4.0-beta.1',revision=44,codename='内测5开发批次6（未发布）',date=STAMP[:10],time=STAMP[11:],summary='研究所开题界面、材料支付与起步配方迁移。',reason='继续接通研究实际操作，保留旧实现并统一后置游戏验收。',changes=changes))
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 rows=[]
 for file,desc in FILES.items():
  assert (ROOT/file).is_file(),file
  link=os.path.relpath(ROOT/file,REPORT.parent).replace('\\','/')
  rows.append('<tr><td><a href="'+html.escape(link)+'">'+html.escape(file)+'</a></td><td>'+desc+'</td></tr>')
 body='<h2>本批已接入</h2><ul>'+''.join('<li>'+x+'</li>' for x in changes)+'</ul><h2>完整修改清单</h2><table><tr><th>文件</th><th>变化</th></tr>'+''.join(rows)+'</table>'
 body+='<h2>授权下的首轮实现取舍</h2><p>费用为20×(电压窗口+1)²×研究所最低阶级点数；基础耗时600×(窗口+1)×最低阶级tick。材料使用前级电路和分阶段金属板，数量由数据定义。均为负责人授权助手决定后的首轮平衡，不称为负责人逐项指定。S01控制器制造只用MAX已有钨钢板、铂导线、MAX电路、传感器与发射器，1200tick、MAX EU/t。</p><p>付款采用背包36主槽；保持无输入仓旧Pattern直到建筑最终工作。页面一次8课题，每10tick刷新；不发送客户端自定义报价。当前只接S01控制器，不能用未注册的S02–S05冒充完成。</p>'
 body+='<h2>测试结果与边界</h2><p>材料专项通过1000例独立穷举对照、100项计划完整性、NBT库存快照、重复付款拒绝、库存变更拒绝及写入异常回滚。真实ItemStack测试尝试因独立JVM缺少Forge变换失败，原测试已归档；改测生产共用事务组件，不将其称为实物适配验收。完整构建结果待补记。</p><p>各真实实验的自动证据记录尚未接通，因此正常新档暂不能开始首课题；界面如实显示缺失凭据，不伪造实验。更高阶注册、团队、取消退款、核心制造及样本分析仍待后续。旧在研任务不自动兑换新研究；旧来源保留备查。电网/背包/世界文件不保证断电原子事务。</p>'
 body+='<h2>来源、备注与后续</h2><p>依据研究机制v2、100课题目录、已确认公式、01:50研究确认、02:13剩余实现授权及15:28统一验收顺序。GTCEu/LDLib仅本地API核对，无外部代码复制。GT金属板标签按TagPrefix的plates/%s路径构造，整包加载后是否存在全部标签留统一游戏验收。中文实验叙述来自设计目录，界面标签与课题名已配英文；实验叙述完整英译仍待补充。</p><p>所有修改Java追加编号及中英文说明，旧备注保留；资源由脚本、本报告及revision44追踪。游戏验收统一留到代码全部接通后，不安装到运行中实例。</p>'
 REPORT.write_text(page('研究所入口与材料支付 · 批次6',body),encoding='utf-8')
 record_path=ROOT/'doc/HK3GTL-内测5/讨论记录'/(datetime.now().strftime('%Y-%m-%d_%H-%M')+'_研究所入口与材料支付执行记录.html')
 record_path.write_text(page('研究所入口与材料支付执行记录','<p>负责人授权继续下一步代码。本记录追踪已授权实施，非新增待批准讨论。</p><ul>'+''.join('<li>'+x+'</li>' for x in changes)+'</ul><p>执行细节和完整清单见09_测试发布/研究所入口与材料支付_批次6.html。来源为已确认研究v2/目录/公式及剩余实现授权。禁止跳过实验、伪造已完成、更改建筑后置顺序。未决与待办为真实实验记录、团队/退款、高阶结构和统一实机验收。</p>'),encoding='utf-8')
 for path in (PROGRESS,ANALYSIS):
  link=os.path.relpath(REPORT,path.parent).replace('\\','/')
  append(path,'<section><h2>批次6：研究所入口与材料支付</h2><p>'+STAMP+'：S01行为与界面、双路线开题、材料快照及起步配方迁移已接入。未知实验不放行；并非完整可玩研究系统。材料核心测试通过，游戏验收继续后置。</p><a href="'+link+'">完整文件清单、风险与验收</a><p>追加记录：批次6/revision44，保留历史。</p></section>')
 arc=ROOT/'archive/beta5-batch6-before'
 entries=['<li>'+p.name+' SHA256 '+hashlib.sha256(p.read_bytes()).hexdigest()+'</li>' for p in sorted(arc.iterdir()) if p.suffix in ['.zip','.java']]
 (arc/'index.html').write_text(page('批次6修改前归档','<p>ZIP中使用项目相对路径，附加Java原件单独保留；bootstrap-attempt为本批失败的测试尝试，不是旧发布代码。旧研究类仍保留源码。</p><ul>'+''.join(entries)+'</ul>'),encoding='utf-8')
 print('Recorded revision44, bilingual UI, file inventory and explicit pending work.')

def verify():
 raw=(ROOT/'build-beta5-batch6.log').read_bytes();log=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8',errors='replace')
 for token in ['BUILD SUCCESSFUL','Research materials:','Research computer:','Research execution:','Beta5 research:','First contact:','Quest migration:']: assert token in log,token
 jars=[p for p in (ROOT/'build/libs').glob('*.jar') if 'sources' not in p.name and 'dev' not in p.name];assert jars
 for jar in jars:
  with zipfile.ZipFile(jar) as z:
   assert json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==44
   assert len(json.loads(z.read('data/hk3gtl/research/research_costs.json'))['topics'])==100
   for file in FILES:
    if file.startswith('src/main/resources/'):assert z.read(file[len('src/main/resources/'):])==(ROOT/file).read_bytes(),file
   assert 'com/sirin/hk3gtl/common/machine/research/Hk3ResearchInstituteMachine.class' in z.namelist()
   assert not any(n.startswith('archive/') for n in z.namelist())
 section='<section><h2>批次6完整构建补记</h2><p>'+STAMP+'：clean build --offline成功；材料支付、研究点计算机、任务执行、研究目录、首信、注视度及任务迁移测试通过。产物已核对100课题费用、研究所类、语言和revision44；不含archive。91项弃用警告尚在。未启动游戏或安装实例，实物适配/交互验收按负责人要求统一后置。</p></section>'
 for path in (REPORT,PROGRESS,ANALYSIS):append(path,section)
 print('Verified build and packaged batch6 resources; in-game acceptance remains deferred.')

if __name__=='__main__': verify() if '--verified' in sys.argv else record()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
