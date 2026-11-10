"""修订86：接入负责人确认的封装样件路线，备份改动文件并保留历史备注。"""
from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/revision86'
LOG.mkdir(exist_ok=True)
NOW = datetime.now()
STAMP = NOW.strftime('%Y-%m-%d %H:%M:%S')
changed = []

def put(rel, text):
    p = ROOT / rel
    if p.exists():
        backup = LOG / 'backup' / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(p, backup)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
    if rel not in changed:
        changed.append(rel)

def patch(rel, old, new):
    s = (ROOT / rel).read_text(encoding='utf-8')
    assert old in s, rel
    put(rel, s.replace(old, new, 1))

def block(desc):
    return ('/**\n * 【变更记录 #2】' + STAMP + '（第 2 次备注 · 内测5修订86）\n'
            ' * 删除：无，保留全部历史注册与工艺。\n * 新增：' + desc + '\n'
            ' * 修改：接入负责人确认的棒壳、封装样件与I02检测路线。\n'
            ' * 用途：补齐RN-FRP实验入口，不注册I18，不跳过研究支付或前置。\n */\n')

p = 'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/Hk3FuelRodBootstrapRecipes.java'
patch(p, '2026-09-27 01:55:00', STAMP)
p = 'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/HonkaiRecipes.java'
patch(p, 'public final class HonkaiRecipes', block('燃料封装起步配方注册委托，沿现有液态工艺入口调用。') + 'public final class HonkaiRecipes')
patch(p, 'Hk3LiquidLineRecipes.processing(provider);', 'Hk3LiquidLineRecipes.processing(provider);\n        Hk3FuelRodBootstrapRecipes.register(provider);')
p = 'src/main/java/com/sirin/hk3gtl/common/registration/Hk3IndustrialContent.java'
patch(p, 'public final class Hk3IndustrialContent', block('独立封装试验样件物品，仅用于破坏性隔离检测。') + 'public final class Hk3IndustrialContent')
patch(p, 'item("fuel_encapsulation_part", 64);', 'item("fuel_encapsulation_test_specimen", 64); // 仅供实验，不属于发电燃料棒标签。\n        item("fuel_encapsulation_part", 64);')
comment = '变更记录 #1 ' + STAMP + '（内测5修订86）：删除无；新增封装试验样件；复用已确认棒壳贴图，不新增美术候选。'
put('src/main/resources/assets/hk3gtl/models/item/fuel_encapsulation_test_specimen.json', json.dumps({'_comment': comment, 'parent': 'minecraft:item/generated', 'textures': {'layer0': 'hk3gtl:item/honkai_fuel_rod_casing'}}, ensure_ascii=False, indent=2) + '\n')
for lang, name in [('zh_cn', '燃料封装试验样件（仅供检测）'), ('en_us', 'Fuel Encapsulation Test Specimen (Testing Only)')]:
    p = f'src/main/resources/assets/hk3gtl/lang/{lang}.json'
    data = json.loads((ROOT / p).read_text(encoding='utf-8'))
    data['item.hk3gtl.fuel_encapsulation_test_specimen'] = name
    data['_comment_revision86'] = comment
    put(p, json.dumps(data, ensure_ascii=False, indent=2) + '\n')
for file in ['research_catalog.json', 'research_costs.json']:
    p = 'src/main/resources/data/hk3gtl/research/' + file
    data = json.loads((ROOT / p).read_text(encoding='utf-8'))
    topic = next(x for x in data['topics'] if x['id'] == 'RN-FRP')
    topic['evidence'] = '完成RN-HFB后，用前级GT设备制造钨钢棒壳与耐化学密封组件，灌装100mB普通液态燃料制成检测专用样件；I02光谱阵列完成破坏性隔离检测并输出不合格棒后记录实验证据。'
    topic['result'] = '确认普通燃料棒封装工艺；首次样件不要求魂钢。I18正式封装阵列与生产配方仍待结构审批及后续实现，本实验不产出可发电燃料棒。'
    data['_comment_revision86'] = '变更记录 #1 ' + STAMP + '（内测5修订86）：删除无；更新RN-FRP实验来源与未实现边界；研究前置、支付、等级和时间均保持不变。'
    put(p, json.dumps(data, ensure_ascii=False, indent=2) + '\n')
p = 'src/main/resources/assets/hk3gtl/changelog.json'
data = json.loads((ROOT / p).read_text(encoding='utf-8'))
assert data['entries'][0]['revision'] == 85
data['entries'].insert(0, {'version': '0.5.0', 'revision': 86, 'codename': 'HK3GTL-内测5', 'date': NOW.strftime('%Y-%m-%d'), 'time': NOW.strftime('%H:%M:%S'), 'reason': '落实负责人确认的燃料封装样件与现有I02检测路线；I18结构另审。', 'changes': ['变更记录 #86：删除无；保留旧工艺与历史记录，修改前备份。', '新增：钨钢棒壳、耐化学密封组件、100mB燃料试验样件及破坏性检测四道MAX工序。', '修改：工序门槛为RN-HFB；I02实际成功输出后记录RN-FRP实验，研究费用与前置不变。', '新增：独立检测专用物品，复用棒壳贴图；检测消耗样件并输出不合格棒，不返还燃料。', '边界：I18正式封装及反应堆尚未接通；本修订不代表整条燃料线完成。']})
put(p, json.dumps(data, ensure_ascii=False, indent=2) + '\n')
p = 'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告_v5.md'
put(p, (ROOT / p).read_text(encoding='utf-8') + '\n\n## 内测5修订86增补：燃料封装研究入口\n\n【变更记录 #1】' + STAMP + '（内测5修订86）\n\n- 删除：无，保留历史审查结论。\n- 新增：棒壳、封装组件、检测专用样件与I02破坏性检测四道工序；统一要求RN-HFB。\n- 修改：修复RN-FRP没有生产实验证据来源的代码缺口；沿成功输出回调记录实验，仍须研究前置、供电及点数或材料支付。\n- 用途：首份样件不依赖魂钢或I18，仅供检测，不是可发电燃料棒。\n- 边界：本条说明代码接入；构建结果单独记录于logs/revision86。未做游戏验收；I18结构、正式棒制造与反应堆循环尚未实现。\n')
(LOG / 'application.json').write_text(json.dumps({'time': STAMP, 'files': changed, 'game_tested': False, 'deployed': False}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'time': STAMP, 'files': changed}, ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
