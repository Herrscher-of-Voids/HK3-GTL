"""修订101：审计新配方物料及设备的研究自锁，外部输入单列而不假定已实现。"""
import json,pathlib,collections
R=pathlib.Path(__file__).resolve().parents[1]
B=R/'src/main/resources/data/hk3gtl/research'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
C={c['id']:c for c in read(B/'research_catalog.json')['topics']}
E={c['id']:c for c in read(B/'research_execution.json')['topics']}
P=read(B/'industrial_processes.json')['recipes']
unlock={r:c['id'] for c in E.values() for r in c['unlocks']}
outputs=collections.defaultdict(list)
# 已存在源码中的新鲜起步路线，不能被本轮新增回收/扩产路线遮蔽。
baseline={'hk3gtl:honkai_crystal_seed':[], 'hk3gtl:honkai_adapted_circuit_substrate':['RN-LES'],
 'hk3gtl:separation_filter':[], 'hk3gtl:fuel_matrix':[], 'honkai_coolant':[],
 'honkai_stabilization_medium':['RN-HSA'],'hot_honkai_coolant':['RN-LSE'],
 'spent_honkai_stabilization_medium':['RN-LSE'],'spent_soulium_solvent':['RN-LES']}
for p in P:
 for f in ['item_outputs','fluid_outputs']:
  for x in p[f]:outputs[x['id']].append(p)
def blocked(req,target,seen=None):
 if req==target:return True
 seen=set() if seen is None else seen
 if req in seen:return False
 seen.add(req)
 return any(blocked(x,target,seen) for x in C[req]['prerequisites'])
def available(item,target,trail=()):
 if item in baseline and not any(blocked(x,target) for x in baseline[item]):return True
 if item not in outputs:return True
 if item in trail:return False
 for p in outputs[item]:
  gates=p['requirements']+([unlock[p['role']]] if p['role'] in unlock else [])
  if any(blocked(x,target) for x in gates):continue
  # 等量返还的模板仍需要首件；不能从自身返还制造起步来源。
  if all(available(x['id'],target,trail+(item,)) for f in ['item_inputs','fluid_inputs'] for x in p[f]):return True
 return False
fail=[]
for p in P:
 target=p['experiment']
 if not target:continue
 gates=p['requirements']+([unlock[p['role']]] if p['role'] in unlock else [])
 for gate in gates:
  if blocked(gate,target):fail.append([target,p['id'],'gate',gate])
 for f in ['item_inputs','fluid_inputs']:
  for x in p[f]:
   if not available(x['id'],target):fail.append([target,p['id'],'input',x['id']])
result={'scope':'新配方物料依赖；外部输入另列核验，不等同游戏可达性','self_locks':fail,
 'external_hk3_inputs':sorted({x['id'] for p in P for f in ['item_inputs','fluid_inputs'] for x in p[f] if x['id'] not in outputs and (x['id'].startswith('hk3gtl:') or ':' not in x['id'])})}
(R/'logs/research-mainline-r101/dependency-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(bool(fail))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
