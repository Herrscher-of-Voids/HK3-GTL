"""#1 2026-09-23: bilingual terminal strings and revision51 record, UTF-8 without BOM.
研究终端语言/讨论记录维护；不复制参考作品的贴图或代码。 Original resources only.
"""
from pathlib import Path
import json
from datetime import datetime
now=datetime.now()
pairs={
'title':('文明认知 · 研究终端','Civilization Research Terminal'),
'search':('搜索课题 / 编号…','Search topics / ID…'),
'empty':('没有匹配的课题','No matching topics'),
'state.0':('研究锁定','Research locked'),
'state.1':('研究可用','Research available'),
'state.2':('研究进行中','Research in progress'),
'state.3':('研究已完成','Research complete'),
'cost':('研究费用：%s 点，或支付材料','Cost: %s points OR materials'),
'time':('基础耗时：%s 秒   功率：%s EU/t','Base time: %s s   Power: %s EU/t'),
'experiment':('实验凭据：%s','Experiment evidence: %s'),
'yes':('已取得','Acquired'), 'no':('未取得','Missing'),
'lab':('研究所 S%s · 槽位 %s/%s','Lab S%s · Slots %s/%s'),
'points':('研究点：%s','Research points: %s'),
'waiting':('等待服务端数据','Awaiting server'),
'unformed':('结构未成型','Structure unformed'),
'paused':('研究所已暂停','Lab paused'),
'remote':('课题在其他设施运行','Running at another lab'),
'power':('供电不足 · 已暂停','Insufficient power'),
'running':('研究运行中','Research running'),
'done':('课题已完成','Topic complete'),
'idle':('研究所待机','Lab idle'),
'materials':('材料费用 · 鼠标悬停查看详情','Materials · Hover for details'),
'materialsButton':('使用材料开题','Start with materials'),
'pause':('暂停研究所','Pause lab'), 'resume':('恢复研究所','Resume lab'),
'result':('研究成果：','Research result: '),
'evidence':('实验要求：','Experiment requirements: '),
'noPrerequisites':('前置研究：无','Prerequisite research: none'),
'remaining':('剩余基础时间：%s 秒','Remaining base time: %s s'),
'quantity':('背包持有 %s / 需要 %s（同标签可替代）','Inventory %s / Required %s (tag equivalents accepted)'),
}
# points按钮与余额使用不同键，避免把%s当成按钮文本。 Separate label and balance keys.
pairs['pointsButton']=('使用研究点开题','Start with points')
for index,lang in enumerate(['zh_cn','en_us']):
    p=Path('src/main/resources/assets/hk3gtl/lang')/(lang+'.json')
    data=json.loads(p.read_text(encoding='utf-8-sig'))
    data.update({'hk3gtl.research.terminal.'+k:v[index] for k,v in pairs.items()})
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('src/main/resources/assets/hk3gtl/changelog.json')
data=json.loads(p.read_text(encoding='utf-8-sig'))
data['entries']=[e for e in data['entries'] if e.get('revision')!=51]
data['entries'].insert(0,dict(version='0.4.0-beta.1',revision=51,codename='内测5 研究终端界面重做',date=now.strftime('%Y-%m-%d'),time=now.strftime('%H:%M:%S'),summary='按放大参考图重做研究卡片、详情、材料和固定操作区。',reason='旧文本配色界面不符合新星工程的布局参考。',changes=['原创深蓝黑底紫青工业终端；完整彩色状态卡片、搜索、滚动条','只读材料图标显示数量及背包持有量，前置、费用、功率独立排列','服务端展示快照及既有开题校验；补全研究所阶级锁定显示','旧研究所源码完整归档；未复制新星工程代码或贴图']))
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doc=Path('doc/HK3GTL-内测5/讨论记录')/(now.strftime('%Y-%m-%d_%H-%M')+'_研究终端参考图逐项重做.html')
doc.write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>研究终端参考图逐项重做</title>
<style>body{background:#111725;color:#e4e9f6;max-width:1000px;margin:auto;font:16px/1.8 sans-serif;padding:30px}h1,h2{color:#70e4ea}</style>
<h1>研究终端参考图逐项重做</h1><p>时间：STAMP，Asia/Hong_Kong。修订51，变更记录#1。</p>
<h2>要求与结论</h2><p>负责人要求逐张放大检查五张新星工程截图，参考其界面组织，改为HK3GTL自身的科幻风格，并明确继续执行。</p>
<p>参考图放大两倍核对：左侧搜索与整块带图标的彩色课题卡，右上大块正文、标题与技术等级，正文底部独立费用区，右下运行状态与物品格，底部固定操作。原纯文字变色方案不符合要求，撤下并归档。</p>
<h2>实现与文件</h2><p>Hk3ResearchInstituteMachine.java提供服务端只读NBT展示快照。新增Hk3ResearchTerminalWidget.java原创绘制深蓝黑底、紫青框线、整卡状态、图标、搜索与滚动。材料预览不支持取放；选择只传课题ID，开题仍按原服务端费用校验。中英语言和changelog同步维护。</p>
<p>旧实现归档：archive/research-terminal-2026-09-23_02-24-33。禁止删掉旧代码记录；本次不改变研究机制、配方或其他系统。</p>
<h2>来源与许可</h2><p>负责人提供E:\\photo\\螢幕擷取畫面下2026-04-14的231437、223017、231456、224226、225444五张截图，仅作布局参考；不复制新星工程资源、代码或文案。卡片图标采用当前模组包已注册材料模型，无新物品及临时物品贴图。</p>
<h2>验收与未决事项</h2><p>必须运行clean build --offline --console=plain；构建后部署到负责人指定PrismLauncher GregTech-Leisure-1.4.5.2实例，旧JAR移到mods目录外备份。实际游戏内视觉、不同GUI缩放、搜索/滚动/选题/材料提示及开题验收仍需运行确认，不能以构建通过代替。</p></html>'''.replace('STAMP',now.strftime('%Y-%m-%d %H:%M:%S')),encoding='utf-8')
print(doc)
