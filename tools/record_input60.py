# -*- coding: utf-8 -*-
"""#1 2026-09-23 11:38:00 / revision60: 记录真实电路类型不兼容证据。
Record the observed circuit ingredient incompatibility and pending runtime acceptance.
不改存档、不发研究凭据；重复执行拒绝重复修订。No save edits or evidence grants; reject duplicates.
"""
from pathlib import Path
from datetime import datetime
import json

root=Path(__file__).resolve().parents[1]
now=datetime.now()
path=root/'src/main/resources/assets/hk3gtl/changelog.json'
data=json.loads(path.read_text(encoding='utf-8'))
assert not any(e.get('revision')==60 and e.get('version')=='0.5.0' for e in data['entries'])
data['entries'].insert(0,dict(version='0.5.0',revision=60,codename='HK3GTL-内测5',date=f'{now:%Y-%m-%d}',time=f'{now:%H:%M:%S}',
    summary='修复GTLAdditions3.3电路槽拒绝液态初采配方的输入条件。',
    reason='逐槽模拟证实探测器通过，电路NBTIngredient被拒；附属电路槽只识别IntCircuitIngredient。',
    changes=['初采改为circuitMeta(3)，生成非消耗IntCircuitIngredient；探测器、产量、耗电、时间不变',
             '纠正旧注释中circuitMeta仅写元数据的错误判断；保留历史并追加说明',
             '保留节流的逐输入模拟诊断，旧源码归档；并行功能未关闭',
             '此前修订59没有解决此电路类型错误；本次需部署后验证连续采样']))
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
section=f'''<section id="input60"><h2>修订60：液态初采输入不足的确定原因</h2><p>{now:%Y-%m-%d %H:%M:%S}，Asia/Hong_Kong。</p>
<p>要求：修复修订59后依旧显示输入材料不足。此次不再将构建成功视为运行验收。</p>
<p>证据：11:35:38与11:35:51实际实例逐槽模拟，prototype_honkai_detector在输入仓accepts=true；
3号电路条件为gtceu:sized包裹forge:nbt，电路槽accepts=false。输入仓存在探测器，专用槽存在编程电路。
GTLAdditions3.3的NotifiableCircuitItemStackHandlerMixin.gTLAdditions$getCircuit只支持IntCircuitIngredient及包裹该类型的SizedIngredient，其余返回-1。</p>
<p>根因：先前把初采的circuitMeta(3)改成notConsumable(IntCircuitBehaviour.stack(3))，生成了不受该电路槽支持的NBT条件。
无限并行不是本次初采拒绝的已证实原因；修订59的启动提交修改未解决此问题。</p>
<p>修复：HonkaiRecipes.java恢复circuitMeta(3)。GTCEu实际源码表明该方法返回notConsumable(IntCircuitIngredient.circuitInput(configuration))，
并非旧备注所称“仅元数据”。保留旧备注以供追溯，新增明确纠正。不消耗电路与探测器，不改100mB、200tick及MAX用电。</p>
<p>改动：HonkaiRecipes.java、Hk3MultiRecipeLogic.java（节流只读诊断）、changelog.json、tools/record_input60.py及此HTML。
原源码归档archive/input-diagnosis60。只参考本地依赖源码/字节码，无新增资源许可。</p>
<p>验收：build-input60-final.log；需确认修复实例中液体持续增长、催化剂保留，错编号或缺探测器仍拒绝。
当前记录时尚未部署最终修复。研究凭据不手动补发，未改变权限或禁用并行。</p></section>'''
p=root/'doc/HK3GTL-内测5/讨论记录'/f'{now:%Y-%m-%d_%H-%M}_液态初采电路类型兼容修复.html'
p.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>初采电路兼容修复</title><body>'+section+'</body></html>',encoding='utf-8')
report=root/'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html'
report.write_text(report.read_text(encoding='utf-8').replace('</body>',section+'</body>'),encoding='utf-8')
print(p)
