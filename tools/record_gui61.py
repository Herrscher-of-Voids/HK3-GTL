# -*- coding: utf-8 -*-
"""Change #1: record revision61, its tests and the pending I02 structure review.
记录实际范围与负责人决定；HTML审核稿不等同于NBT或GTCEu成型验收。
"""
from pathlib import Path
from datetime import datetime
import json, shutil

root=Path(__file__).resolve().parents[1]
now=datetime.now()
stamp=now.strftime('%Y-%m-%d %H:%M:%S')
archive=sorted((root/'archive').glob('gui61-*'))[-1]
def backup(p):
    dest=archive/p.relative_to(root)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists(): shutil.copy2(p,dest)

gradle=root/'build.gradle'
backup(gradle)
with gradle.open('a',encoding='utf-8') as f:
    f.write(f'''\n// 变更记录 #9 · {stamp} · 内测5修订61：新增GUI视窗与输入坐标回归，无旧任务删除。
// Add viewport and pointer-transform regression coverage without replacing existing verification.
tasks.register("runGuiFitTest", JavaExec) {{
    dependsOn("compileTestJava", "classes")
    group = "verification"
    classpath = sourceSets.test.runtimeClasspath
    mainClass = "com.sirin.hk3gtl.test.gui.GuiFitTest"
}}
tasks.named("check").configure {{ dependsOn("runGuiFitTest") }}
''')
p=root/'src/main/resources/assets/hk3gtl/changelog.json'
backup(p)
d=json.loads(p.read_text(encoding='utf-8'))
d['entries'].insert(0,dict(version='0.5.0',revision=61,codename='HK3GTL-内测5',date=now.strftime('%Y-%m-%d'),time=now.strftime('%H:%M:%S'),
    summary='研究终端与本模组独立界面适配小视窗。',reason='负责人反馈固定GUI尺寸遮挡小视窗；后续实验链须先审核新结构。',
    changes=['研究终端按当前窗口等比适配；绘制、裁剪、点击、拖动及悬停共用坐标变换',
    '信件、对话、档案、欢迎及旧研究界面加入统一适配层；不改全局GUI缩放',
    '旧研究界面resize后重新挂接按钮；对话resize保留当前段落',
    '新增八种视窗及支付按钮命中回归；旧源码归档',
    '研究启动、扣费及完成获负责人确认；实验链等待I02/I03/I04新结构审核，未新增凭据或绕过条件']))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

style='''body{background:#0d1422;color:#dce7f6;font:16px/1.8 system-ui;margin:auto;max-width:1120px;padding:28px}h1,h2{color:#82e5ea}section{background:#151f31;border:1px solid #34465d;border-radius:12px;padding:20px;margin:18px 0}a{color:#adbcff}strong{color:#ffdb8a}table{width:100%;border-collapse:collapse}td,th{border:1px solid #3a4e66;padding:10px;text-align:left}svg{width:100%;max-height:580px}button{background:#344267;color:white;padding:10px;border:1px solid #8090b0;cursor:pointer}.pending{color:#ffcf80}footer{color:#9dadc6}'''
def page(title,body):
    return f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{style}</style><h1>{title}</h1><p>{stamp} · Asia/Hong_Kong</p>{body}<footer>变更记录 #1 · {stamp} · 内测5修订61。审核图为原创设计示意，不是方块模型、NBT或成型证明。</footer></html>'

doc=root/'doc/HK3GTL-内测5/03_机器结构/I02样本光谱分析阵列_结构审核稿_v1.html'
doc.write_text(page('I02 · 样本光谱分析阵列 · 结构审核稿', '''
<p class="pending">待负责人审核：本稿确认建筑风格与空间分区。通过后才制作完整逐层建筑，实景审核通过后再迁移Pattern、连接实验链。旧I02占位文件不算已通过。</p>
<section><h2>沿用已定工业职责</h2><p>输入I01液态样本和分析耗材，输出成分谱图、分析后样本及废试剂。谱图送研究所S01与探测器校准I07，分析后样本继续进入I03。初始分析实验不能被RN-HSA自身锁住。</p><p>候选外包尺寸：<strong>宽17 × 长21 × 高17格，普通级</strong>。来源：<a href="../02_工业计划/HK3GTL工业计划树状图_v5.html">工业树v5的I02节点</a>；具体外形仍待审核。</p></section>
<section><h2>建议风格：天命精密实验设施</h2><p>冷白金属与深灰承重骨架为主，青色刻度光带、少量紫色样品指示光。主体为两条对称的光谱检测廊，中间是可见的玻璃样品舱，上方用三道有支撑的校准横架收束轮廓。前低后高，核心舱最高；不做全封闭方盒，也不使用终局熔炉式岩浆配色。</p><p>复杂度来自分层扫描环、成对仪器肋架、可追踪的管路、回收设施和检修走台。灯带服务于光路辨识，结构不是随意堆叠发光方块。</p></section>
<section><h2>分区示意 · 前侧在下方</h2><p>这是功能俯视图，非逐格建筑。点击按钮查看上层。</p><button onclick="document.getElementById('upper').style.display=document.getElementById('upper').style.display==='none'?'block':'none'">显示／隐藏上层光路</button>
<svg viewBox="0 0 640 650" role="img" aria-label="左右光谱廊、中央样品舱、侧面通道和前后接口的功能俯视图">
<rect x="90" y="20" width="460" height="590" fill="#202c40" stroke="#889ab4" stroke-width="3"/>
<g fill="#33435d" stroke="#6da8bb"><rect x="180" y="125" width="75" height="315" rx="16"/><rect x="385" y="125" width="75" height="315" rx="16"/></g>
<rect x="275" y="220" width="90" height="150" rx="30" fill="#604d80" stroke="#d2a9ff" stroke-width="3"/>
<g stroke="#80dfe1" fill="none" stroke-width="8"><path d="M130 545 V110 H510 V545"/><path d="M130 460 H510"/></g>
<g fill="#7c879f"><rect x="170" y="58" width="110" height="34"/><rect x="360" y="58" width="110" height="34"/><rect x="282" y="525" width="76" height="40"/></g>
<g fill="#edf5ff" font-size="16" text-anchor="middle"><text x="320" y="44">后侧能源／信号服务区</text><text x="220" y="180">参考光路</text><text x="420" y="180">样本光路</text><text x="320" y="278">中央</text><text x="320" y="308">样品舱</text><text x="320" y="490">横向检修联络道</text><text x="320" y="550">控制器</text><text x="200" y="595">输入侧</text><text x="440" y="595">回收／输出侧</text><text x="320" y="636">前侧入口 · 外侧青线为净空检修环路</text></g>
<g id="upper" style="display:none" stroke="#ffc983" stroke-width="7" fill="none"><path d="M180 140 H460 M180 290 H460 M180 420 H460"/><rect x="263" y="198" width="114" height="191" rx="30"/></g>
</svg></section>
<section><h2>高度与通行约束</h2><table><tr><th>层段</th><th>设计用途</th></tr><tr><td>Y0–2</td><td>承重底座、分开的供液与废试剂回流槽；交叉处上下分层。</td></tr><tr><td>Y3–5</td><td>前侧操作层与连续检修环路；通道目标净宽2格、净高3格，不能被端口和装饰堵住。</td></tr><tr><td>Y6–11</td><td>双光谱廊、扫描环、中央样品舱；左右骨架严格镜像，工艺接口按输入和回收职责区分。</td></tr><tr><td>Y12–16</td><td>校准光路、支撑横架与局部顶罩；保留观察核心的视线，不封成平顶盒。</td></tr></table><p>走台与梯道必须实际连通。逐层施工时检查净空、前后可达性及两侧对称性，不能只检查外包尺寸。</p></section>
<section><h2>方块选择原则</h2><table><tr><th>角色</th><th>选材方向</th></tr><tr><td>主机壳／承重</td><td>优先GTL／GTCEu在MAX已可制造的浅色金属机壳与深色框架。</td></tr><tr><td>光学舱／观察窗</td><td>透明或低遮挡的模组玻璃，保证能看见样品舱与扫描环。</td></tr><tr><td>仪器／连接</td><td>模组精密机械方块、管路及可明确识别的能源连接件；装饰不冒充真实仓口。</td></tr><tr><td>警示／照明</td><td>青色光带与少量紫光，普通方块可补充护栏、台阶与边缘细节。</td></tr></table><p class="pending">具体注册ID和获取配方须以目标实例核对后落表。当前不指定神之锻炉机壳、终局线圈等可能超出起步阶段的材料；不把材质存在误认为玩家能制造。</p></section>
<section><h2>审核后交付与验收</h2><ol><li>选定可达方块与方块状态，制作这一台完整结构；提供正面、背面、两侧、顶部及内部视角。</li><li>逐层核对净空、支撑、左右骨架、控制器朝向、物品／流体输入输出和维护路径。</li><li>负责人实景审核通过后，手动迁移GTCEu Pattern并检查成型；结构审核不等同于实验逻辑验收。</li><li>接入RN-HSA的真实输出凭据。输入不足、停机、模拟检查及输出堵塞不得授予实验。</li></ol><p><strong>本次需要审核：</strong>天命精密实验设施风格、双廊＋中央样品舱轮廓、17×21×17尺寸，以及连续检修环路。I03与I04随后逐台处理，不批量套用这一外形。</p></section>
'''),encoding='utf-8')

record=root/'doc/HK3GTL-内测5/讨论记录'/f'{now:%Y-%m-%d_%H-%M}_GUI自适应与实验链结构审核顺序.html'
record.write_text(page('GUI自适应与实验链结构审核顺序', '''
<section><h2>负责人要求与验收反馈</h2><p>研究所已能正常启动、扣费并完成。小视窗GUI过大，需要适应视窗。后续研究缺少实验入口。</p><h2>已确认结论</h2><p>负责人明确选择“先完成新结构审核，再接实验链”，并确认执行计划。先落实本模组GUI适配；从I02开始逐台结构审核，随后I03、I04。不得先借旧结构接实验链。</p><h2>本次实现范围</h2><p>研究终端、信件、对话、档案、欢迎及旧研究界面的显示与鼠标适配；不改变全局设置、不修改支付或实验权限。新增GUI坐标回归，保留归档旧源码。</p><h2>待确认与后续</h2><p>I02外观和空间方案待审；具体方块ID、获取配方、完整逐层结构及Pattern待后续落实。100项课题尚未全部连通，不得以GUI修复宣称研究全流程已完成。</p><h2>禁止采用</h2><p>不得用持有样品代替亲自完成实验，不得取消实验门槛或把旧占位预览视为通过，不得先接依赖未审核结构的实验链。</p><h2>来源与许可</h2><p>依据本轮对话、工业计划树v5、研究机制v2及项目已有代码。审核图原创，无新增第三方模型或纹理；本轮未调用建筑生成Skill。</p><h2>涉及文件与验收标准</h2><p>Hk3GuiFit、Hk3FittedScreen、Hk3ResearchTerminalWidget及五个独立Screen；GuiFitTest、build.gradle、changelog.json。小视窗应完整显示面板、支付按钮可点、文本可滚动，切换尺寸不丢操作；构建与坐标测试不替代游戏内验收。</p></section>
'''),encoding='utf-8')
report=root/'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html'
backup(report)
s=report.read_text(encoding='utf-8')
entry=f'<section><h2>修订61 · {stamp} · GUI适配与研究缺口</h2><p>负责人确认研究启动、扣费、完成正常。GUI适配新增研究终端及五类独立界面的缩放、输入及裁剪处理；验证见build-gui61-final.log。后续实验链仍待I02/I03/I04新结构逐台审核，不提前复用旧结构接入，也不自动授予实验。I02结构审核稿已整理，尚未批准。</p></section>'
s=s.replace('</body>',entry+'</body>') if '</body>' in s else s+entry
report.write_text(s,encoding='utf-8')
print(doc)
print(record)
