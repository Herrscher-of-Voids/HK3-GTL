# -*- coding: utf-8 -*-
"""修订87收尾记录：同步已有文档、端口备注和修改清单；不部署、不启动游戏。"""
from pathlib import Path
from datetime import datetime
import json
import hashlib
import shutil

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/revision87'
STAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
record = json.loads((LOG / 'application.json').read_text(encoding='utf-8'))

def save(rel, content):
    path = ROOT / rel
    backup = LOG / 'backup' / rel
    if path.exists() and not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    path.write_text(content, encoding='utf-8')
    if not any(e['path'] == rel for e in record['files']):
        record['files'].append({'path': rel, 'before': hashlib.sha256(backup.read_bytes()).hexdigest() if backup.exists() else None})

p = 'src/main/resources/assets/hk3gtl/changelog.json'
d = json.loads((ROOT / p).read_text(encoding='utf-8'))
assert d['entries'][0]['revision'] == 87
message = '修改：I04/I05同类槽位共享能力计数，每类至少一进一出；未批准或替换结构。旧实现是分组重复约束，并非允许全输入。'
if message not in d['entries'][0]['changes']:
    d['entries'][0]['changes'].append(message)
    d['entries'][0]['changes'].append('记录补充 #87.1 ' + STAMP + '：新增端口核对结论与L1文档同步；保留历史条目。')
save(p, json.dumps(d, ensure_ascii=False, indent=2) + '\n')

p = 'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告_v5.md'
s = (ROOT / p).read_text(encoding='utf-8')
if '修订87端口核对补记' not in s:
    s += f'''\n\n### 修订87端口核对补记\n\n【变更记录 #2】{STAMP}（内测5修订87）\n\n- 删除：无，不移除旧建筑或未获批准内容。\n- 修改：I04/I05的i/o共享一套物品谓词，u/v共享一套流体谓词，每种能力至少1个；预览2物品进/2出、4流体进/4出。其余机器不受本次端口修正影响。\n- 纠正：GT TraceabilityPredicate.setMinGlobalLimited会逐个设置合并的SimplePredicate，因此旧代码并非允许全输入；旧代码为每种布局字母重复创建计数，导致各分组都要求进出。本次修正为全机同类槽位共享计数。\n- 新增：源码数量核验覆盖零回收库存启动、60个回流宏批次、参考样本标准件、工艺输入输出种类上限和注册入口。\n- 用途：保证可选方向不受布局字母额外约束；仓室容量、多流体缓冲、实际插入输出仍需用户实测。I03六个流体槽推荐2进4出，或使用多流体输出仓，以容纳净化的四种流体输出；现有预览3进3出不等于强制布局。\n- 构建：第一次clean build于2026-09-27成功（44秒、23项任务），执行10个自定义测试入口；未执行独立研究图测试，未启动或部署游戏。资源记录补充后最终构建另见clean-build-final.log。\n- 待审：I04拟23×27×23中央稳定腔/三层约束/双侧冷却；I05拟27×19×23双塔再生/侧置冷却。只提交方案，审批前不生成或接入新结构。\n'''
save(p, s)

p = 'doc/HK3GTL-内测5/02_工业计划/HK3GTL工业计划树状图_v5.html'
s = (ROOT / p).read_text(encoding='utf-8')
marker = 'id="revision87-l1"'
if marker not in s:
    section = f'''\n<section id="revision87-l1"><h2>L1 实现补记 · 修订87</h2>
<p>变更记录 #1 {STAMP}：保留历史设计；新增本次已实施配方与待审批边界，不将规划文字改成游戏验收结论。</p>
<p>4批分馏仍产20000mB粗液；4批净化产1280粒子，制造80晶种，供5次稳定化得到4000mB稳定液。净化另出每批500mB除杂母液；回I03时用7500mB新采液加500mB除杂母液，碳、滤芯、基质、工时及电力照常投入。</p>
<p>再生每次耗8残渣、4杂质；一个上述宏批次含5次再生后，余4杂质、32残渣，各有独立处理。试剂回收1200mB，再生需2500mB，差额由前级GT混合机的蒸馏水、乙醇及氢氧化钠支线补足。多余介质可有损排污，经固化、离心转为灰。</p>
<p>I01高效采集保留4份参考样本作为不消耗标准件；I07校准仍消耗样本。首次研究、制造探测器和校准仍需谱图支线；取得标准件后的主采集不再逐批消耗样本。</p>
<p>I04/I05同类端口共享计数，至少一进一出；正式建筑待审批。I03净化输出4种流体，6个槽位可按2进4出配置，或使用多流体输出仓。静态数量检查与构建不能代替用户游戏验收。</p></section>\n'''
    assert '</body>' in s
    s = s.replace('</body>', section + '</body>', 1)
save(p, s)

p = 'src/main/java/com/sirin/hk3gtl/common/multiblock/pattern/Hk3LiquidLinePatterns.java'
# 时间校正为本轮实际写入时间，保留全部旧修订备注。
s = (ROOT / p).read_text(encoding='utf-8').replace('2026-09-27 02:31:30（第 4 次备注', '2026-09-27 02:30:55（第 4 次备注')
save(p, s)
for e in record['files']:
    e['after'] = hashlib.sha256((ROOT / e['path']).read_bytes()).hexdigest()
record['finalized_at'] = STAMP
record['structure_approval'] = 'I04/I05方案已提交，等待负责人回复'
(LOG / 'application.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'time': STAMP, 'files': len(record['files']), 'game_tested': False, 'deployed': False}, ensure_ascii=False))
