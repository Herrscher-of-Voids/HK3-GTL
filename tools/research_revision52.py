# -*- coding: utf-8 -*-
"""#1 2026-09-23: publish authored research chronicle and traceable revision52 docs.
从100段原创原稿生成游戏数据与HTML全集，验证课题顺序/覆盖；不更改玩家存档。
Build narrative data and HTML from the authored source, validating order and coverage; never edit player saves.
"""
from pathlib import Path
from datetime import datetime
import json, html
now=datetime.now(); stamp=now.strftime('%Y-%m-%d %H:%M:%S')
root=Path('src/main/resources')
costs=json.loads((root/'data/hk3gtl/research/research_costs.json').read_text(encoding='utf-8'))['topics']
chapters=[dict(id=line.split('|',1)[0],text=line.split('|',1)[1]) for line in Path('tools/research_story_100.txt').read_text(encoding='utf-8').splitlines() if line.strip()]
assert len(chapters)==100 and [c['id'] for c in chapters]==[t['id'] for t in costs]
assert len({c['text'] for c in chapters})==100 and all(len(c['text'])>=45 for c in chapters)
(root/'data/hk3gtl/research/research_story.json').write_text(json.dumps(dict(schema=1,language='zh_cn',_comment='Revision52 '+stamp+' Asia/Hong_Kong. 原创中文文明研究纪事；仅叙事，不授予任何知识。 Original narrative only, never grants progression.',chapters=chapters),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
style='<style>body{background:#101625;color:#e5eafa;max-width:1000px;margin:auto;padding:32px;font:17px/1.9 system-ui}h1,h2{color:#aeb2ff}small,a{color:#72dedc}article{padding:15px 0;border-bottom:1px solid #34405e}details{margin:16px 0}button{padding:10px;background:#293b54;color:white} @media print{body{background:white;color:black}}</style>'
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>文明研究纪事·一百章</title>'+style
page+='<h1>文明研究纪事 · 一百章</h1><p>变更记录 #1 · 修订52 · '+stamp+' Asia/Hong_Kong</p><p>作者按负责人授权编写的模组原创叙事，基于内测5研究目录及新树海设定。它是一篇文明发展纪事，不代表当前玩家已完成其中工程或审判；阅读不改变存档。</p><button onclick="window.print()">打印 / 保存PDF</button>'
for i,(c,t) in enumerate(zip(chapters,costs),1):
    page+=f'<article id="{c["id"]}"><small>{i:03d} / 100 · {c["id"]}</small><h2>{html.escape(t["title"])}</h2><p>{html.escape(c["text"])}</p></article>'
page+='<h2>依据与边界</h2><p>参考本项目：研究课题目录与前置树_v1、完整主线方案与树状图_v4、世界观角色事件与彩蛋、奥托第一封信事件规格。角色与背景沿用户设定；不引用第三方文本。研究说明只到终审资格道路，未预先授予二审或终审通过。原稿中文，英文客户端也显示该中文原稿；后续翻译不改变研究逻辑。</p></html>'
Path('doc/HK3GTL-内测5/04_研究系统/文明研究纪事_100章.html').write_text(page,encoding='utf-8')
strings={
'story':('文明研究纪事','Chronicle of Civilization'),
'block.lab':('研究所阶级不足：请在标题所示的S阶级或更高研究所开题。','Lab rank insufficient: use the required S-rank lab or higher.'),
'block.parents':('前置研究未完成：请向下滚动查看红色前置课题。','Prerequisite research incomplete: scroll down to see the red prerequisites.'),
'block.sampling':('缺少首次液态采样记录。取得奥托首信情报后，在已成型采集塔输入仓放入零阶试作探测器和3号GT编程电路，接好流体输出仓与玩家电网，成功产出100mB液态崩坏能（200tick/MAX EU/t）。旧粒子配方、背包持有样品均不算实验。','Missing liquid sampling evidence. After receiving Otto\'s data, run the formed tower with the prototype detector, programmed circuit 3, fluid output hatch and player-grid power. Successfully output 100 mB liquid Honkai energy (200 ticks at MAX EU/t). Legacy particle recipes and inventory samples do not count.'),
'block.adapter':('此课题缺少实验记录：当前版本尚未接入对应工业实验的记录入口，暂不能开题。不会扣费。','This topic has no evidence: its industrial experiment recorder is not yet implemented in this build. Research cannot start; nothing is charged.'),
}
for index,lang in enumerate(['zh_cn','en_us']):
    p=root/'assets/hk3gtl/lang'/f'{lang}.json'; data=json.loads(p.read_text(encoding='utf-8'))
    data.update({'hk3gtl.research.terminal.'+key:values[index] for key,values in strings.items()})
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'assets/hk3gtl/changelog.json'; data=json.loads(p.read_text(encoding='utf-8'))
data['entries']=[e for e in data['entries'] if e.get('revision')!=52]
data['entries'].insert(0,dict(version='0.4.0-beta.1',revision=52,codename='内测5研究诊断、百章故事与跨配方恢复',date=now.strftime('%Y-%m-%d'),time=now.strftime('%H:%M:%S'),summary='修复开题静默拦截，加入100段连续叙事，撤销制造类跨配方16条上限。',reason='负责人反馈两种开题均不可用，并要求研究叙事与原并行能力。',changes=['读取实际存档发现443研究点但没有实验凭据；保留实验条件，加入固定拒绝提示与聊天详细诊断','100段中文原创故事随课题详情展示，并生成HTML完整故事','制造类多配方候选不再人为截断为16条；研究槽保持已确认1/2/4/8/16','采集塔普通配方恢复跨配方；初采仍独立执行及结算','明确记录后续99项实验接入未完成，不以免费解锁掩盖缺口']))
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doc=Path('doc/HK3GTL-内测5/讨论记录')/(now.strftime('%Y-%m-%d_%H-%M')+'_研究开题诊断百章故事与并行核对.html')
doc.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8">'+style+'<h1>研究开题诊断、百章故事与并行核对</h1><p>变更记录#1 修订52 · '+stamp+' Asia/Hong_Kong</p><h2>负责人要求</h2><p>排查两种开题失败；每项研究加入一段故事，100段连成完整世界观故事；找回无限并行/跨配方，如无原代码才参考GTLsupb。</p><h2>调查证据与执行决定</h2><p>只读查看指定实例最新存档：443研究点，尚无实验凭据、在研任务。UI以canStart吞掉请求造成无反馈。恢复服务端诊断而不删去实验要求。第一项必须完成初采；代码检索只有RN-HED接入recordExperiment，后续99项入口缺失，明确列为未完成。</p><p>原Hk3MultiRecipeLogic及Hk3RecipeCalculationHelper仍在，制造类默认启用；无需重新复制第三方实现。实际存在16条候选截断，本次取消。底层并行仍有Integer.MAX_VALUE类型界限，受实际输入、输出和能量制约，并非数学无穷。采集塔普通配方恢复该路径，实验采样保持独立。研究所则依据已确认方案保留有限课题槽，不擅自改成无限研究。</p><h2>叙事与来源</h2><p>原创100章中文故事，按RN目录顺序，研究所和HTML全集共用。参考本项目内测5主线v4、研究目录、首信和新树海人物设定，无第三方文本复制。最后停在终审资格准备，不把研究完成当作终审通过。</p><h2>验收与风险</h2><p>需验证100项顺序、覆盖、唯一段落、数据加载、构建回归及实例部署。实际UI点击、初采成功结算、普通塔跨配方恢复仍需游戏内验证。取消候选上限可能增加大量配方目录扫描开销；不以恢复名义跳过资源验证。</p><h2>未决与后续</h2><p>99项工业实验的真实接入仍待逐设备实现，不能以持有材料或研究点代替实验；本批不宣称整个研究系统已可从头通关。故事原稿为中文，英文界面显示原文。涉及Java文件均追加双语历史备注并保留旧实现归档。</p></html>',encoding='utf-8')
print('Validated 100 unique chapters in exact research order.'); print(doc)

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
