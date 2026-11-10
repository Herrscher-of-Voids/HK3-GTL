"""2026-09-29：计算内测5完成度审计事实；不修改游戏代码。"""
from pathlib import Path
from structure_delivery.project_paths import project_path
from collections import Counter
import json, re, hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/beta5-completion-audit-20260929'
def read(p): return (ROOT/p).read_text(encoding='utf-8-sig')
def load(p): return json.loads(read(p))
facts={}
catalog=load('src/main/resources/data/hk3gtl/research/research_catalog.json')
costs=load('src/main/resources/data/hk3gtl/research/research_costs.json')['topics']
approved=load('logs/research-r03-r06-review/confirmed-decisions-20260928-222343.json')['approved_proposal']
facts['catalog_keys']=list(catalog)
facts['cost_topics']=len(costs)
facts['current_points_total']=sum(t['points'] for t in costs)
facts['approved_points_total']=approved['point_total']
byid={t['id']:t for t in costs}
facts['cost_point_mismatches']=[t['id'] for t in approved['topics'] if byid[t['id']]['points']!=t['candidate_points']]
evidence={'RN-HED','RN-HSA'}
liquid=read('src/main/java/com/sirin/hk3gtl/common/recipe/honkai/Hk3LiquidLineRecipes.java')
evidence.update(re.findall(r'"RN-[A-Z]+","(RN-[A-Z]+)"',liquid))
fuel=read('src/main/java/com/sirin/hk3gtl/common/recipe/honkai/Hk3FuelRodBootstrapRecipes.java')
evidence.update(re.findall(r'EXPERIMENT, *"(RN-[A-Z]+)"',fuel))
facts['production_evidence_topics']=sorted(evidence)
facts['no_production_evidence_found']=[t['id'] for t in costs if t['id'] not in evidence]
entries=load('src/main/resources/assets/hk3gtl/narrative/approved.json')['entries']
facts['prose_entries']=len(entries)
facts['prose_systems']=dict(Counter(t['system'] for t in entries))
facts['if_entries']=[{'id':t['id'],'lines':t['lineCount']} for t in entries if 'IF' in t['id']]
facts['architecture_resources']=[p.name for p in (ROOT/'src/main/resources/data/hk3gtl/approved_architecture').glob('*.json')]
failures=[];count=0
for p in (ROOT/'src/main/resources').rglob('*.json'):
    count+=1
    try:json.loads(p.read_text(encoding='utf-8-sig'))
    except Exception as exc:failures.append({'path':str(p.relative_to(ROOT)),'error':str(exc)})
facts['resource_json_checked']=count
facts['resource_json_parse_failures']=failures
facts['custom_test_tasks']=re.findall(r'^> Task :(run\w+)',read('logs/trade-removal-r99/final-build.log'),re.M)
facts['current_kubejs']=[str(p.relative_to(ROOT)) for p in (ROOT/'kubejs').rglob('*.js')]
delivery=load('logs/trade-removal-r99/delivery.json')
deployed={}
for name,info in delivery['instances'].items():
    jars=[p for p in (project_path(info['path'])/'mods').glob('*.jar') if 'hk3' in p.name.lower() or '崩坏' in p.name]
    deployed[name]=[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in jars]
facts['installed_current_hashes']=deployed
(OUT/'facts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(facts,ensure_ascii=False,indent=2))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
