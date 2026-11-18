# -*- coding: utf-8 -*-
"""Change #1: append revision61 validation and deployment evidence to HTML records.
只追加已验证结果；游戏内显示与交互仍待负责人验收。
"""
from pathlib import Path
from datetime import datetime
import html
root=Path(__file__).resolve().parents[1]
stamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
files=[
'src/main/java/com/sirin/hk3gtl/common/gui/Hk3GuiFit.java',
'src/main/java/com/sirin/hk3gtl/common/gui/Hk3ResearchTerminalWidget.java',
'src/main/java/com/sirin/hk3gtl/client/gui/Hk3FittedScreen.java',
'src/main/java/com/sirin/hk3gtl/client/bootstrap/Hk3ModWelcomeScreen.java',
'src/main/java/com/sirin/hk3gtl/client/narrative/Hk3NarrativeCodexScreen.java',
'src/main/java/com/sirin/hk3gtl/client/communication/Hk3LetterScreen.java',
'src/main/java/com/sirin/hk3gtl/client/dialogue/Hk3DialogueScreen.java',
'src/main/java/com/sirin/hk3gtl/client/research/Hk3ResearchMatrixScreen.java',
'src/test/java/com/sirin/hk3gtl/test/gui/GuiFitTest.java',
'build.gradle','src/main/resources/assets/hk3gtl/changelog.json']
entry=f'''<section><h2>追加验证记录 #2 · {stamp}</h2><p>clean build --offline --console=plain：BUILD SUCCESSFUL，37秒，21个任务。新增GuiFitTest验证8种视窗、可见区域边界和按钮坐标往返。日志：build-gui61-final.log。</p>
<p>已在确认无javaw进程后替换指定Prism实例的hk3gtl-0.5.0.jar。SHA256：c997f5cd0b485f5b6f469dbcb905ce14a95a9ebda2a6f3b71aabf54fffda8509。旧包位于实例minecraft/hk3gtl-mod-backups/gui61-2026-09-23_12-12-55。</p>
<p><strong>未做本轮游戏内显示与交互验收。</strong>建议打开研究所后改变视窗尺寸与GUI缩放，核对搜索、课题选择、滚动条、支付按钮和悬停提示。新结构尚未批准，后续实验入口尚未接入。</p>
<h2>本轮源码、测试及配置文件</h2><ul>'''+''.join('<li><code>'+html.escape(p)+'</code></li>' for p in files)+'''</ul><p>旧文件完整归档在archive/gui61-2026-09-23_12-06-38；Java文件追加中英文变更备注，历史备注保留。另新增I02审核HTML及本轮执行／记录脚本。</p></section>'''
records=list((root/'doc/HK3GTL-内测5/讨论记录').glob('*_GUI自适应与实验链结构审核顺序.html'))
records.append(root/'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html')
for p in records:
    s=p.read_text(encoding='utf-8')
    if '</body>' in s: s=s.replace('</body>',entry+'</body>')
    else: s=s.replace('</html>',entry+'</html>')
    p.write_text(s,encoding='utf-8')
print('Validation and changed-file inventory appended.')
