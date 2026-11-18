"""Append traceable runtime corrections. Idempotent per revision; does not launch or edit saves.

Change #1 2026-09-22: record actual failed port setup and recipe-ID correction, with bilingual Java notes.
"""
from pathlib import Path
from datetime import datetime
import json

ROOT = Path(__file__).resolve().parents[1]
stamp = datetime.now()
base = ROOT / 'src/main/java/com/sirin/hk3gtl'
entries = {
    'common/recipe/honkai/HonkaiRecipes.java': (2,
        '删除：无旧配方删除。新增：初采配方显式hk3gtl命名空间。修改：GT字符串构造器原默认gtceu，与采样凭据ID不一致。用途：真实液体产出可被研究钩子准确识别。',
        'Use an explicit hk3gtl recipe namespace; the GT string builder defaults to gtceu and prevented evidence matching.'),
    'common/machine/research/Hk3HonkaiAbsorptionMachine.java': (3,
        '删除：旧配方固定单次限制。新增：按准确初采ID分流。修改：只有初采禁用超频并行，旧粒子配方恢复基类处理。用途：修复无关旧配方行为回退；完成仍只认成功OUT。',
        'Bound only bootstrap sampling; restore superclass OC/parallel processing for legacy recipes. Evidence still requires successful OUT.'),
    'common/command/Hk3ResearchRuntimeCheck.java': (2,
        '删除：直接写首信发现状态的测试路径。新增：真实输入/输出仓、MAX库存入口、缺探测器与中断检查、催化剂保留和重复扣费检查。修改：迁移至空白测试坐标；不覆盖上轮失败装置。用途：仅开发测试世界真实tick验收，不直接授予知识或凭据。',
        'Install real optional ports, use the MAX inventory service, verify absent catalysts/interruption/receipts/replay using actual ticks; preserve the failed fixture.'),
}
for rel, (number, cn, en) in entries.items():
    path = base / rel
    source = path.read_text(encoding='utf-8')
    marker = f'【变更记录 #{number}】'
    if marker in source:
        continue
    start = source.index('public ')
    # Insert before the class annotation when present, preserving all earlier comment blocks.
    annotation = source.rfind('@Mod.EventBusSubscriber', 0, start)
    if annotation >= 0:
        start = annotation
    note = f'/**\n * {marker}{stamp:%Y-%m-%d %H:%M:%S}（内测5研究验收修订47）\n * {cn}\n * {en}\n */\n'
    path.write_text(source[:start] + note + source[start:], encoding='utf-8')
path = ROOT / 'src/main/resources/assets/hk3gtl/changelog.json'
data = json.loads(path.read_text(encoding='utf-8'))
if not any(x.get('revision') == 47 for x in data['entries']):
    data['entries'].insert(0, dict(version='0.4.0-beta.1', revision=47,
        codename='内测5研究运行时修正（未发布）', date=f'{stamp:%Y-%m-%d}', time=f'{stamp:%H:%M:%S}',
        summary='修正初采配方ID并增强真实研究验收。',
        reason='游戏首轮验收失败：自动建造没有输入输出仓；源码追查发现GT默认配方命名空间不匹配。',
        changes=[x[1] for x in entries.values()]))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Recorded revision 47 at', stamp.isoformat(timespec='seconds'))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
