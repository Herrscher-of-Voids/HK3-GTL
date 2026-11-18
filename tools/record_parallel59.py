# -*- coding: utf-8 -*-
"""#1 2026-09-23 04:06:00 / revision59。
记录并行启动修复、证据和未完成的实机验收；不声称问题已在游戏验证。
Record startup fixes, evidence and pending runtime verification without overclaiming.
"""
from datetime import datetime
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
now=datetime.now()
log=root/'src/main/resources/assets/hk3gtl/changelog.json'
data=json.loads(log.read_text(encoding='utf-8'))
assert not any(e.get('version')=='0.5.0' and e.get('revision')==59 for e in data['entries'])
data['entries'].insert(0, dict(version='0.5.0',revision=59,codename='HK3GTL-内测5',
    date=now.strftime('%Y-%m-%d'),time=now.strftime('%H:%M:%S'),
    summary='修正跨配方启动扣料时机及采样输入匹配接口。',
    reason='用户反馈启用并行后停转；发现规划提前扣料与GTLCore批处理重复介入，初采仍使用原生匹配器。',
    changes=['合并规划保留完整输入，setupRecipe检查通过后才在IN入口提交一次',
             '合并计划不再由GTLCore二次扩批，完成后重新按实际资源规划',
             '初采统一使用GTLCore RecipeRunnerHelper匹配；保留归属、情报、催化剂和EU要求',
             '诊断区分原生与GTLCore匹配结果，记录规划通过但启动被拒的情况',
             '未关闭无限并行/跨配方；旧代码已归档，实际停转需部署后复测']))
log.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
body=f'''<section id="parallel59"><h2>修订59：并行启用后停转调查与修复</h2>
<p>{now:%Y-%m-%d %H:%M:%S}，Asia/Hong_Kong。负责人反馈增加无限并行与无限跨配方后机器不动。
已请求确认具体机器和界面停机原因，当前尚未收到答复，不将所有机器停转认定为已证实。</p>
<h3>调查证据</h3><p>当前实例日志03:53:27成功登记RN-HED；随后采集塔原生matchRecipe报缺物品，tick供电检查通过。
只读存档快照：塔已成型、IDLE、批处理关闭；输入仓有两个零阶探测器及3号电路，输出仓981500mB液态崩坏能。
存档快照与历史日志不是同一时刻的内存快照，因此不据此断言唯一根因。</p>
<h3>已实施代码修复</h3><p>Hk3MultiRecipeLogic原先在buildFinalNormalRecipe提前扣料、清空运行输入，之后setupRecipe才检查研究和beforeWorking，
并会再次经过GTLCore BatchProcessing。现规划只读并保留完整输入，正式IN入口复核条件/聚合I/O/tickI/O后提交一次，
已分配的组合绕过第二次扩批。完成时让父类处理输出与状态复位，同时标脏以重新规划下一轮。未取消资源限制。</p>
<p>Hk3HonkaiAbsorptionMachine的初采预检查从原生matchRecipe改为RecipeRunnerHelper，与当前GTLCore正式启动一致；
不修改配方产量、研究权限或初采独立运行设计。诊断增加coreMatch及启动失败日志。</p>
<h3>文件与验收</h3><ul><li>src/main/java/com/sirin/hk3gtl/common/machine/Hk3MultiRecipeLogic.java</li>
<li>src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3HonkaiAbsorptionMachine.java</li>
<li>src/main/resources/assets/hk3gtl/changelog.json</li><li>tools/record_parallel59.py及本记录</li></ul>
<p>原文件保留在archive/parallel-start59-2026-09-23_04-05-03。当前无第三方代码复制，仅依据本地依赖字节码核对接口。
构建结果见build-parallel59.log；运行时尚待部署和验收，不能把编译通过当作机器已恢复。</p>
<p>验收必须覆盖：单配方启动及连续运行；有材料但启动守卫拒绝时不扣料；不同配方共享材料时不过量承诺；
缺电/输出满时保持输入；运行完后重新分配；非消耗电路/探测器保留；初采完成与RN-HED登记。
不采用直接关闭并行、凭库存补发研究或放宽能源检查。GTLsupb Jade修订58候选仍为独立待部署项。</p></section>'''
record=root/'doc/HK3GTL-内测5/讨论记录'/f'{now:%Y-%m-%d_%H-%M}_并行停转调查与启动提交修复.html'
record.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>并行停转修复</title><body>'+body+'</body></html>',encoding='utf-8')
report=root/'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html'
report.write_text(report.read_text(encoding='utf-8').replace('</body>',body+'</body>'),encoding='utf-8')
print(record)
