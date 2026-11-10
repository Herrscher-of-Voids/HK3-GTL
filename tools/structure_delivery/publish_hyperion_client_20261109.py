"""同步休伯利安真实搭建、性能及成型复测证据，保留固定分母和历史。"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
import re

from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/build-client-r228-20261109'


def main():
    result = json.loads((LOG / 'client-results.json').read_text(encoding='utf8'))
    evidence = deepcopy(result)
    evidence['updated_at'] = datetime.now(timezone.utc).isoformat()
    evidence['evidence'] = 'logs/build-client-r228-20261109/client-results.json'
    report = ROOT / 'logs/beta5-completion-audit-20261030'
    paths = [report / 'index.html', report / 'current-summary.json']
    before = {p: p.read_bytes() for p in paths}
    history = LOG / ('before-report-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    history.mkdir()
    for p, content in before.items():
        (history / p.name).write_bytes(content)
    data = json.loads(before[paths[1]])
    old = deepcopy(data)
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    for container in (system, data['current_work']):
        container['hyperion_construction_client_test'] = deepcopy(evidence)
    system['updated_at'] = evidence['updated_at']
    data['report_updated_at'] = evidence['updated_at']
    data['systems'].sort(key=lambda s: s['percent'])
    assert data['overall_percent'] == old['overall_percent']
    assert [(s['id'], s['percent'], s['earned'], s['possible']) for s in data['systems']] == [(s['id'], s['percent'], s['earned'], s['possible']) for s in old['systems']]
    assert all(s == o for s, o in zip(data['systems'], old['systems']) if s['id'] != 'multiblocks')
    html = before[paths[0]].decode('utf8')
    notice = '<p class="notice" id="hyperion-live-client-20261109">2026-11-09 · ' + evidence['status'] + ' 系统分数、74项范围与批准台账保留。<a href="../build-client-r228-20261109/client-results.json">实测证据</a></p>'
    if 'id="hyperion-live-client-20261109"' in html:
        html, count = re.subn(r'<p class="notice" id="hyperion-live-client-20261109">.*?</p>', lambda _: notice, html, count=1, flags=re.S)
    else:
        html, count = re.subn(r'(</h1>)', lambda m: m[1] + notice, html, count=1)
    assert count == 1
    html, count = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + evidence['updated_at'] + ' · 休伯利安搭建及成型客户端复测</p>', html, count=1)
    assert count == 1
    html, count = re.subn(r'(?<=id="audit-data">).*?(?=</script>)', lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S)
    assert count == 1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>', html, flags=re.S)[1]) == data
    publisher().publish_transaction({paths[0]: html, paths[1]: json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, before)
    print(json.dumps(dict(status=evidence['status'], overall=data['overall_percent']), ensure_ascii=False))


if __name__ == '__main__':
    main()
