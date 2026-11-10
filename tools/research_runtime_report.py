# -*- coding: utf-8 -*-
"""Generate an evidence-scoped HTML research report from actual logs; never changes game state.

Change #1 2026-09-22: retain failed attempts, distinguish core smoke checks from full-system acceptance,
and link each changed file. Running again refreshes the report without duplicating history sections.
"""
from pathlib import Path
from datetime import datetime
import html

ROOT = Path(__file__).resolve().parents[1]
def read_log(name):
    path = ROOT / name
    if not path.exists():
        return ''
    raw = path.read_bytes()
    return raw.decode('utf-16' if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else 'utf-8', errors='replace')

stamp = datetime.now()
logs = ['run-beta5-research-runtime.log', 'run-beta5-research-runtime-2.log']
evidence = []
for name in logs:
    lines = [line for line in read_log(name).splitlines() if '[HK3-RESEARCH-RUNTIME]' in line]
    evidence.append(f'<h3>{html.escape(name)}</h3><pre>{html.escape(chr(10).join(lines) or "尚无运行时结果")}</pre>')
build = read_log('build-beta5-research-runtime-2.log')
passed = 'PASS: actual sampling' in read_log(logs[-1])
files = [
    'src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3HonkaiAbsorptionMachine.java',
    'src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchInstituteMachine.java',
    'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchStartService.java',
    'src/main/java/com/sirin/hk3gtl/common/machine/Hk3MachinesImpl.java',
    'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/HonkaiRecipes.java',
    'src/main/java/com/sirin/hk3gtl/common/recipe/Hk3RecipeTypesImpl.java',
    'src/main/java/com/sirin/hk3gtl/common/command/Hk3ResearchRuntimeCheck.java',
    'src/main/java/com/sirin/hk3gtl/common/command/Hk3ResearchVerificationCommands.java',
    'src/main/resources/assets/hk3gtl/lang/zh_cn.json',
    'src/main/resources/assets/hk3gtl/lang/en_us.json',
    'src/main/resources/assets/hk3gtl/changelog.json',
    'tools/industrial_game_smoke.py', 'tools/research_runtime_notes.py',
    'tools/research_runtime_report.py',
]
links = ''.join(f'<li><a href="../../../../{html.escape(name)}">{html.escape(name)}</a></li>' for name in files)
source = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>研究系统游戏验收 · 批次8</title><style>body{{max-width:1120px;margin:auto;padding:28px;background:#0b1020;color:#edf2ff;font:16px/1.8 system-ui}}a{{color:#7ce4db}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#172237;padding:14px}}li{{margin:8px 0}}h2{{border-bottom:1px solid #344563}}</style>
<h1>研究系统游戏验收 · 批次8</h1><p>记录更新：{stamp:%Y-%m-%d %H:%M:%S} Asia/Hong_Kong。未发布。</p>
<p><strong>完整研究系统：未通过整体验收。</strong>首项实际采样与材料研究：{'运行时通过，范围见日志' if passed else '正在验收，尚未取得通过结果'}。</p>
<h2>本轮执行</h2><p>按负责人最新要求逐系统完成与游戏验收。旧代码保留或归档，最终多方块建筑仍需逐台审阅。本轮使用既有小型Pattern测试执行逻辑，不代表批准为内测5最终建筑。</p>
<p>首项RN-HED必须由已获奥托情报的在线所有者，使用编程电路3与零阶探测器实际完成200tick、100mB液态初采，成功输出后才记录实验。持有样本、中断、旧粒子配方不计入。采样不发点、不直接完成研究。</p>
<h2>发现与修正</h2><ul><li>已撤回背包晶体充当实验的早期尝试，历史源码归档。</li><li>GT的afterWorking在中断和实际输出之前都会调用；改为准确配方的成功OUT回调。</li><li>GT字符串配方构造器默认gtceu命名空间，导致与hk3gtl实验ID不匹配；初采配方改用显式ResourceLocation。</li><li>GT自动建造可全部填机壳，成型不代表具备可用仓口；测试塔装入真实LV输入总线与流体输出仓。</li><li>研究开题统一服务端校验，重复请求不扣费；界面显示进度、能耗与暂停信息。</li></ul>
<h2>验证与限制</h2><p>clean build --offline --console=plain：{'通过' if 'BUILD SUCCESSFUL' in build else '未取得成功记录'}。现有研究目录、付款、计算机计量、任务队列、存档等逻辑测试随构建执行；这些不能代替机器运行验收。</p>
<p>测试在开发客户端专用Registry-Smoke存档，创造模式供给材料和电量。测试命令只在开发环境注册；没有直接授予研究知识/实验，采集与研究使用实际服务器tick。第一封信测试沿真实MAX库存检查入口，但账号此前已有首信，因此不能据此宣称测试了全新账号首次投递。</p>
{''.join(evidence)}
<h2>整体验收尚缺</h2><ul><li>试作型探测器制造配方尚缺；旧采集塔控制器和机壳沿用GTL后期材料，生存起步可达性仍需核对。</li><li>目录共100课题，目前真实实验生产入口只接入RN-HED，其余99项及对应工艺效果尚未全部接通。</li><li>五阶研究所目前只绑定S01，其他四阶与最终建筑尚未完成。</li><li>团队知识继承、全队在线判定、取消与原支付账户退款待实现；不能用个人账户行为冒充团队支持。</li><li>计算机实际产点、点数支付路线、机器停服再恢复、原生界面交互仍需分别取得运行时证据。</li><li>现有测试模组环境报告5项KubeJS错误；不得将其描述为无错误整包。</li></ul>
<p>贴图：批次7除仿制理之律者核心以外均未获负责人认可，本轮没有改变这一状态。</p>
<h2>改动文件</h2><ul>{links}</ul><h2>来源与历史</h2><p>已确认研究机制v2、100课题目录、公式草案、GTCEu1.4.4源码及本地真实运行日志。没有引入新外部美术素材。</p>
<p>变更记录 #1 · {stamp:%Y-%m-%d %H:%M:%S}：汇总修订46–47的代码、资源与测试记录，包含失败与未完成项。本报告是语言文件和changelog等不支持注释资源的配套说明。</p></html>'''
report = ROOT/'doc/HK3GTL-内测5/09_测试发布/研究系统游戏验收_批次8.html'
report.write_text(source, encoding='utf-8')
print(report)

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
