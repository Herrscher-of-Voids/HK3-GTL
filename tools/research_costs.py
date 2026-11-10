"""内测5研究费用首轮数据 / Initial beta5 research costs.
变更记录 #1：2026-09-22 15:50:00，批次6。按负责人剩余实现授权生成，不冒充逐项定稿数值。
研究目录提供课题身份与实验要求；本工具只确定首轮费用/耗时，不授予实验成果。
Generate balance data from the accepted catalog; never grant experimental evidence.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'src/main/resources'
catalog = json.loads((BASE / 'data/hk3gtl/research/research_catalog.json').read_text(encoding='utf-8'))
rows = []
tiers = [f'{phase}_{level}' for phase in ['abyss', 'imaginary', 'quantum', 'finality'] for level in range(1, 5)]
plates = ['steel', 'tungsten_steel', 'naquadah_alloy', 'neutronium', 'tritanium']
for node in catalog['topics']:
    rank, lab = node['tier'], node['lab']
    # 种子课题只用前级电路；第一批MAX课题继续用MAX，避免研究解锁自身材料。
    # Seed research uses preceding-tier circuits, avoiding a self-unlock circuit requirement.
    circuit = 'gtceu:circuits/max' if rank <= 1 else 'forge:circuits/'+tiers[rank-2]
    rows.append(dict(id=node['id'], title=node['title'], english=node['english'], evidence=node['evidence'], result=node['result'],
                     points=20*(rank+1)**2*lab, ticks=600*(rank+1)*lab,
                     materials=[dict(tag=circuit, count=2*lab), dict(tag='forge:plates/'+plates[lab-1], count=16+8*rank)]))
assert len(rows) == 100
output = BASE / 'data/hk3gtl/research/research_costs.json'
output.write_text(json.dumps(dict(schema=1, _comment='Change #1 2026-09-22 15:50:00 batch6. Initial authorized balance, pending unified game acceptance. / 首轮授权平衡数据，实验前置不可被支付替代。', topics=rows), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
for locale in ['zh_cn', 'en_us']:
    path = BASE / f'assets/hk3gtl/lang/{locale}.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    for row in rows:
        data['hk3gtl.research.topic.'+row['id'].lower()] = row['title' if locale == 'zh_cn' else 'english']
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Generated 100 cost records and localized topic names.')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
