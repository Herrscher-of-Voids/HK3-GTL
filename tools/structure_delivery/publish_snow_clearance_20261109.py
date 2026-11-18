# -*- coding: utf-8 -*-
"""同步积雪误报修复证据；离线核验不得计为完整实装测试。"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]


def main():
    log = ROOT / 'logs/snow-clearance-r224-20261109'
    build = (log / 'build.log').read_text(encoding='utf8', errors='replace')
    assert 'BUILD SUCCESSFUL' in build and '> Task :snowClearanceTest' in build
    jar = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
    deployment_path = log / 'deployment.json'
    deployment = json.loads(deployment_path.read_text(encoding='utf8')) if deployment_path.exists() else {}
    installed = deployment.get('installed') is True
    report = ROOT / 'logs/beta5-completion-audit-20261030'
    paths = [report / 'index.html', report / 'current-summary.json']
    before = {p: p.read_bytes() for p in paths}
    now = datetime.now(timezone.utc)
    backup = log / ('before-report-' + now.strftime('%Y%m%dT%H%M%S%fZ'))
    for p, value in before.items():
        q = backup / p.name
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_bytes(value)
    data = json.loads(before[paths[1]])
    previous = deepcopy(data)
    evidence = dict(revision=224, updated_at=now.isoformat(),
        status='代码修复与离线回归通过；r224已停机安装，尚未实装测试' if installed else '代码修复与离线回归通过；尚未替换实例JAR或实装测试',
        cause='共享净空规则只放行空气与AE线缆，自然雪层触发批准巨构空气区被占用。',
        fix='密集谓词与稀疏巨构统一允许原版雪层；实体材料、雪块、细雪、流体和其他障碍继续检查。',
        cleanup_command='/hk3structure clear-snow <控制器X> <控制器Y> <控制器Z>',
        cleanup_scope='创造模式OP显式启动；只清理批准建材暴露顶面的雪层，按tick预算执行，遵守破坏保护，跳过未加载区块。',
        build_passed=True, offline_regression_passed=True, installed=installed,
        deployment_evidence='logs/snow-clearance-r224-20261109/deployment.json' if installed else None,
        game_formation_verified=False, cleanup_game_verified=False, implementation_test_passed=False,
        jar=str(jar), jar_bytes=jar.stat().st_size, jar_sha256=hashlib.sha256(jar.read_bytes()).hexdigest(),
        build_evidence='logs/snow-clearance-r224-20261109/build.log',
        remaining='验证积雪前后真实成型、运行、破坏恢复及受保护/未加载区域除雪；本轮不改系统分数。')
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    system['snow_clearance_fix'] = evidence
    system['updated_at'] = now.isoformat()
    data['current_work']['snow_clearance_fix'] = deepcopy(evidence)
    data['systems'].sort(key=lambda s: s['percent'])
    data['report_updated_at'] = now.isoformat()
    assert data['overall_percent'] == previous['overall_percent']
    assert [(s['id'],s['percent']) for s in data['systems']] == [(s['id'],s['percent']) for s in previous['systems']]
    html = before[paths[0]].decode('utf8')
    install_status = 'r224已停机安装' if installed else '未替换实例JAR'
    notice = '<p class="notice" id="r224-snow-clearance">2026-11-09 · r224修复积雪导致的空气区误报，并新增定向分批除雪。构建及离线回归通过；'+install_status+'，未通过完整实装测试。原系统分数与范围保留。</p>'
    if 'id="r224-snow-clearance"' in html:
        html,n = re.subn(r'<p class="notice" id="r224-snow-clearance">.*?</p>',lambda _:notice,html,count=1,flags=re.S)
    else:
        html,n = re.subn(r'(</h1>)',lambda m:m[1]+notice,html,count=1)
    assert n == 1
    html,n = re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+now.isoformat()+' · 积雪误报修复</p>',html,count=1)
    assert n == 1
    html,n = re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S)
    assert n == 1
    publisher().publish_transaction({paths[0]:html,paths[1]:json.dumps(data,ensure_ascii=False,indent=2)+'\n'},before)
    (log / 'verification.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(evidence['status'])


if __name__ == '__main__':
    main()
