"""修订71：汇总当前结构材料的静态解析证据，不评判生存获取。"""
from pathlib import Path
from collections import Counter
import json
from material_resources import Resources

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/revision71'

def main():
    resources = Resources()
    structures = []
    states = set(resources.declarations)
    for rel in resources.index:
        parts = rel.split('/')
        if len(parts) == 4 and parts[0] == 'assets' and parts[1] in ('gtlcore', 'gtladd', 'gtladditions') and parts[2] == 'blockstates' and rel.endswith('.json'):
            block = parts[1] + ':' + parts[3][:-5]
            bs = json.loads(resources.read(rel))
            variants = bs.get('variants', {})
            for cond in variants:
                states.add(block + ('[' + cond + ']' if cond else ''))
            if not variants:
                states.add(block)
    for path in sorted((ROOT / 'src/main/resources/data/hk3gtl/approved_architecture').glob('*.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        counts = Counter(b.get('state', b.get('block')) for b in data['blocks'])
        states.update(counts)
        structures.append({'file': str(path.relative_to(ROOT)), 'materials': dict(counts)})
    for path in sorted((ROOT / 'doc/HK3GTL-内测5/03_机器结构').rglob('manifest.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, list):
            continue
        for entry in data:
            materials = entry.get('materials', [])
            if not isinstance(materials, list):
                continue
            counts = {m['id']: m.get('count', 0) for m in materials if isinstance(m, dict) and 'id' in m}
            if counts:
                states.update(counts)
                structures.append({'file': str(path.relative_to(ROOT)), 'key': entry.get('key', entry.get('file')), 'materials': counts})
    results = {}
    for state in sorted(states):
        try:
            result = resources.material(state)
            results[state] = {k: v for k, v in result.items() if k != 'faces'}
        except Exception as error:
            results[state] = {'state': state, 'complete_cube': False, 'reason': str(error)}
    for structure in structures:
        structure['unresolved'] = [s for s in structure['materials'] if not results[s]['complete_cube']]
    report = {'scope': '静态模型与纹理适配；生存获取不作为筛选条件；未代替运行时注册与成型验收',
        'materials': results, 'structures': structures, 'unresolved_scripts': resources.unresolved_scripts,
        'resource_sources': resources.sources}
    OUT.mkdir(exist_ok=True)
    (OUT / 'materials-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    summary = {'materials': len(results), 'complete': sum(r['complete_cube'] for r in results.values()),
        'namespaces': dict(Counter(s.split(':')[0] for s in results)), 'structures': len(structures),
        'structure_unresolved': [{'key': s.get('key', s['file']), 'states': s['unresolved']} for s in structures if s['unresolved']],
        'unresolved_scripts': resources.unresolved_scripts}
    print(json.dumps(summary, ensure_ascii=False))
    resources.close()

if __name__ == '__main__':
    main()
