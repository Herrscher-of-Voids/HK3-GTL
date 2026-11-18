# -*- coding: utf-8 -*-
"""按真实安装与客户端证据同步固定审计，整机成型状态独立保留。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import re
from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]


def main():
    log = ROOT / 'logs/w03-c9-native-r221-20261108'
    report = ROOT / 'logs/beta5-completion-audit-20261030'
    index_path = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
    paths = [report/'index.html', report/'current-summary.json', index_path]
    before = {p: p.read_bytes() for p in paths}
    stamp = datetime.now(timezone.utc)
    backup = log / ('before-status-' + stamp.strftime('%Y%m%dT%H%M%S%fZ'))
    for p, value in before.items():
        q = backup / p.relative_to(ROOT)
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_bytes(value)
    data = json.loads(before[paths[1]])
    original = deepcopy(data)
    index = json.loads(before[index_path])
    deployment = log / ('deployment-r223.json' if (log/'deployment-r223.json').exists() else 'deployment-r222.json')
    deployed = json.loads(deployment.read_text(encoding='utf8'))
    revision = deployed['revision']
    assert deployed['passed'] and revision in (222, 223)
    test_path = log/'client-verification.json'
    client = json.loads(test_path.read_text(encoding='utf8')) if test_path.exists() else {}
    passed = client.get('passed') is True
    when = stamp.isoformat()
    work = data['current_work']
    motion = work['wonder_motion']
    status = f'r{revision}仅客户端渲染试验通过；C9整机尚未实装' if passed else f'r{revision}特效已安装，客户端渲染试验中；C9整机尚未实装'
    remaining = 'C9控制器与正式Pattern尚未接入，未在世界搭建真实结构，未验证GT成型或成型联动特效；须先补齐，再返回W02。工艺、多人同步及低端性能仍待验。'
    scope = '通过客户端创造命令显示渲染模型；未放置真实建筑方块，不能证明搭建、成型或机器运行。'
    motion.update(status=status, native_fx_installed=True, native_fx_revision=revision,
                  native_fx_game_verified=passed, native_fx_build_passed=True,
                  native_fx_deployment='logs/w03-c9-native-r221-20261108/'+deployment.name,
                  native_fx_compatibility='logs/w03-c9-native-r221-20261108/enhanced35-compatibility.json',
                  native_fx_verification_scope=scope, controller_integrated=False,
                  world_structure_built=False, formation_verified=False,
                  formation_linked_fx_verified=False,
                  remaining=remaining, updated_at=when)
    if passed:
        assert client['revision'] == revision and client['full_model_quads'] == 517262
        motion['native_fx_client_evidence'] = 'logs/w03-c9-native-r221-20261108/client-verification.json'
        work['next_step'] = 'W03 C9实装缺口优先：真实控制器、搭建、GT成型及成型联动特效实测；完成后再返回W02 Gemini V3。'
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    system['wonder_motion_review'] = deepcopy(motion)
    system['updated_at'] = when
    entry = next(e for e in index['entries'] if e['id'] == 'W03')
    entry.update(status='appearance_approved_native_fx_verified' if passed else 'appearance_approved_native_fx_installed',
                 native_fx_installed=True, native_fx_revision=revision, native_fx_game_verified=passed,
                 native_fx_deployment=motion['native_fx_deployment'])
    if passed:
        entry['native_fx_client_evidence'] = motion['native_fx_client_evidence']
    entry.update(native_fx_verification_scope=scope, controller_integrated=False,
                 world_structure_built=False, formation_verified=False,
                 formation_linked_fx_verified=False)
    index['updated_at'] = when
    data['report_updated_at'] = when
    data['systems'].sort(key=lambda s: s['percent'])
    assert data['overall_percent'] == original['overall_percent']
    assert [(s['id'], s['percent']) for s in data['systems']] == [(s['id'], s['percent']) for s in original['systems']]
    date = stamp.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')
    notice = date + ' · W03 C9外观已批准；' + status + '。' + scope + '批准58／正式52，batch-12为1/5。' + remaining + '36系统分数与74项分母保持。'
    html = before[paths[0]].decode('utf8')
    html, n = re.subn(r'(<p class="notice" id="w03-c9-native-current">).*?(</p>)', lambda m:m[1]+notice+m[2], html, count=1, flags=re.S)
    assert n == 1
    html, n = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 '+when+' · W03 C9原生特效</p>', html, count=1)
    assert n == 1
    html, n = re.subn(r'(?<=id="audit-data">).*?(?=</script>)', lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'), html, count=1, flags=re.S)
    assert n == 1
    publisher().publish_transaction({paths[0]:html, paths[1]:json.dumps(data,ensure_ascii=False,indent=2)+'\n',
                                     index_path:json.dumps(index,ensure_ascii=False,indent=2)+'\n'}, before)
    print(notice)


if __name__ == '__main__':
    main()
