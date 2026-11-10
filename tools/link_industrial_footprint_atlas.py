# -*- coding: utf-8 -*-
"""变更记录 #1 · 2026-09-23 · 串联最新占地预览与三个历史文档。
只追加导航及独立讨论记录；旧工业尺寸作为历史证据保留。
"""
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'doc/HK3GTL-内测5'
ATLAS=BASE/'03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html'
now=datetime.now()
stamp=now.strftime('%Y-%m-%d %H:%M:%S')
assert ATLAS.exists()
entries={
BASE/'03_机器结构/多方块占地分级与全维度高度需求_v1.html':f'<section><h2>后续逐台重设占地 · {stamp}</h2><p>本页只定义已确认的占地等级，并记录69座旧尺寸统计。后续已新增<a href="内测5_69座多方块逐台占地规划与比例预览_v2.html">69座逐台新占地及离线比例预览 v2</a>：旧统计28/38/2/0/1是旧尺寸，不代表最新规划；新规划的12/22/12/7/16均为候选，结构需逐台审核。原高度技术边界仍有效，未实施无限建筑高度。</p><p>变更记录 #2 · {stamp} · 增加新逐台尺寸的入口和版本关系，不改原分类规则或历史数据。</p></section>',
BASE/'03_机器结构/结构视觉标准与预览使用_v1.html':f'<section><h2>最新占地预览与实体预览的区别 · {stamp}</h2><p><a href="内测5_69座多方块逐台占地规划与比例预览_v2.html">最新69座占地对比图</a>可直接双击HTML离线查看，不用起本地服务。旧W01–W15 NBT只作历史造型占位；新尺寸没有伪造同规格建筑NBT。已有的<a href="I02结构审核_v1/审核入口.html">I02完整建筑</a>另按逐格NBT审核。占地提案批准后仍要逐台做外观、材料、通道、控制器及Pattern。</p><p>变更记录 #2 · {stamp} · 补充最新占地规划链接，明确旧占位稿与新比例图性质。</p></section>',
BASE/'03_机器结构/机器与文明级奇观.html':f'<section><h2>69座最新占地候选 · {stamp}</h2><p>本页机器/奇观职责模板与性能约束继续生效；各台候选的新版宽×长×高以及旧新同比例俯视图已集中在<a href="内测5_69座多方块逐台占地规划与比例预览_v2.html">69座新占地方案</a>。W01–W15均按已确认规则提出最长边≥256格的方案。它们仍是建筑尺寸提案；未注册控制器、构建奇观或完成游戏性能验证。</p><p>变更记录 #1 · {stamp} · 追加候选规模的可视入口，不把旧候选清单提升为已完成机器。</p></section>',
BASE/'02_工业计划/HK3GTL工业计划树状图_v5.html':f'<section class="panel"><h2>工业树v5与新占地方案 · {stamp}</h2><p>本树各节点的<code>dimensions</code>与表格为2026-09-21历史候选，未覆盖以保留讨论记录。需看最新逐台宽×长×高及等比例预览请打开<a href="../03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html">69座逐台占地规划 v2</a>。新版仍是待评阅的建筑外包候选，不等于已经迁移Pattern。</p></section>',
BASE/'index.html':f'<section id="beta5-latest-footprints"><h2>最新69座多方块逐台占地预览 · {stamp}</h2><p><a href="03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html">直接打开离线等比例对照图与完整69台旧新尺寸</a>。这份才是更新后的尺寸方案；旧工业树和W01–W15尺寸占位NBT仍保留为历史。该页尺寸尚待各台建筑审核。</p><p>变更记录 #2 · {stamp} · 把最新逐台规划置于文档入口，不改变旧版内容。</p></section>',
ROOT/'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html':f'<section><h2>69座占地方案纠漏 · {stamp}</h2><p>负责人指出原占地分级规范仅按69座旧尺寸分类，没有重新确定W01–W15等建筑实际候选占地。已补<a href="../../HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html">逐台新占地比例预览</a>，其中65座提案尺寸变化、15座剧情奇观均达奇观级阈值。I01-1、I02、S01与休伯利安尺寸保留；新规划仍需逐台建筑设计及成型性能审核；无代码/NBT/存档变更。</p></section>',
}
for path,block in entries.items():
    text=path.read_text(encoding='utf-8')
    assert '内测5_69座多方块逐台占地规划与比例预览_v2.html' not in text, str(path)
    if '</main>' in text:
        text=text.replace('</main>',block+'</main>',1)
    elif '</body>' in text:
        text=text.replace('</body>',block+'</body>',1)
    else:
        raise RuntimeError(f'Missing main/body: {path}')
    path.write_text(text,encoding='utf-8')
record=BASE/'讨论记录'/f"{now.strftime('%Y-%m-%d_%H-%M')}_69座多方块占地重设与离线预览.html"
record.write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>69座多方块占地重设与离线预览</title><style>body{{max-width:1100px;margin:auto;padding:24px;background:#0b1020;color:#edf2ff;font:16px/1.8 system-ui}}a{{color:#82e9dc}}section{{border:1px solid #344563;border-radius:10px;padding:14px;margin:14px 0}}h1,h2{{color:#a9c5ff}}</style><h1>69座多方块占地重设与离线预览</h1><p>{stamp} Asia/Hong_Kong（UTC+08:00）</p><section><h2>负责人提出的要求</h2><p>负责人指出仅有已确认等级分级及旧尺寸分类表，没有重新指定69座建筑的新占地面积，也没有最新占地预览。要求针对引用的三份机器结构文档给出真正的新尺寸方案和预览。</p></section><section><h2>已确认设计边界</h2><p>沿用最长水平边分级：普通16–31，中型32–64，大型65–95，超大型96–255，文明奇观≥256；全维度扩高仍为未落实的技术目标。机器逐台设计，复杂、美观，通路与材料实际可达；建筑结构交负责人最终审核。休伯利安为额外旗舰，不算15座剧情奇观。先验收新结构再接实验链。</p></section><section><h2>本次新提出的候选尺寸</h2><p><a href="../03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html">查看69座完整新旧尺寸和等比例互动俯视图</a>。69座均逐台指定宽×长×高；4座保留既有实体或已做结构外包尺寸，其余65座调整；15座W奇观宽与长分别均≥257，按已确认的最长边规则全部达文明奇观级。按新候选统计为普通12、中型22、大型12、超大型7、奇观级16（15 W + H01）。这些具体数值<strong>待负责人审阅</strong>，不得记录为最终批准。</p></section><section><h2>明确不采用与不得推测</h2><p>不重写工业树v5旧尺寸或声称其NBT已更新，不用统一大方盒代替15座独特结构，不把占地外包图冒充完整建筑或可运行GTCEu Pattern；不把已建I02尺寸私自改大、不声称全维度扩高已完成、不据建筑规划解除研究实验凭据。</p></section><section><h2>尚未解决的问题、验收与后续</h2><p>新外包尺寸仍需逐台确定外观、逐层方块、控制器、设备舱、仓口、材料成本、真实空置区与完工条件。尤其W12长513、W15宽513、H01长536等巨构需要验证跨区块结构读取、分区检查、网络/渲染及存档重载，不能将整立方体一次性扫描。15座独立奇观不得同时以旧占位形体扩展冒充完成。只有建筑实景和运行规则确认后才接Pattern与生产链。</p></section><section><h2>涉及文件、作品及许可</h2><p>本次只增加一个完全离线的HTML比例预览及生成脚本，并在分级、高度、机器奇观、视觉标准、工业树、文档目录和系统分析报告中添加准确入口。旧尺寸取自本项目《HK3GTL工业计划树状图_v5.html》；分级取自《多方块占地分级与全维度高度需求_v1.html》；I02审核取自本地完整建筑稿。浏览器图形只用原生HTML/SVG/CSS，无外来建筑模型、纹理或新依赖，无第三方许可引入；未改游戏Java、资源、NBT或玩家世界。</p></section><footer>变更记录 #1 · {stamp} · 一次讨论对应本记录；新尺寸为待审提案。</footer></html>''',encoding='utf-8')
print('linked',len(entries),'records',record)

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
