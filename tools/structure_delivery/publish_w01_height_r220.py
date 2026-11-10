"""归档W01客户端建高与完整搭建实测，保留其他系统分数及设计状态。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
import nbtlib
from max_structure_review import publisher

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'logs/w01-terminal-bounds-20261108'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'


def read(p): return json.loads(p.read_text('utf8'))
def save(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    release, saved, start = [read(WORK / n) for n in ['release.json', 'saved-world-verification.json', 'start.json']]
    assert release['passed'] and saved['passed'] and saved['formed'] == 1
    assert saved['matching_noncontroller'] == 1932712 and saved['source_world_unchanged_files'] == 205
    target = Path(release['target'])
    assert sha(target) == sha(ROOT / 'build/libs/hk3gtl-0.5.0.jar') == release['sha256']
    game = target.parent.parent
    assert 'toggleCrouch:false' in (game / 'options.txt').read_text('utf8').splitlines()
    log = (game / 'logs/latest.log').read_text('utf8')
    rejected = next(x for x in log.splitlines() if '蓝图实际高度Y=-89～293' in x)
    assert '本维度允许Y=-64～1023' in rejected and '控制器放在Y=-35～670' in rejected
    assert '未放置方块，也未扣除材料' in rejected
    begin = next(x for x in log.splitlines() if '[CHAT] HK3GTL分批建造已启动' in x)
    end = next(x for x in log.splitlines() if '任务结束：hk3gtl:w01_origin_stellar_concert_court' in x)
    assert '处理1932713格，放置1932712格' in end
    parse_time = lambda line: datetime.strptime(line[1:line.index(']')], '%d%b%Y %H:%M:%S.%f')
    elapsed = (parse_time(end) - parse_time(begin)).total_seconds()
    assert 0 < elapsed < 300
    assert 'HK3GTL建造启动失败' not in log
    clone = Path(start['test_world'])
    forced_file = clone / 'data/chunks.dat'
    forced = nbtlib.load(forced_file)['data'].get('Forced', []) if forced_file.exists() else []
    assert len(forced) == 0
    shots = WORK / 'screenshots'; shots.mkdir(exist_ok=True)
    for name in ['2026-11-08_12.49.26.png', '2026-11-08_12.53.25.png', '2026-11-08_12.53.55.png']:
        shutil.copy2(game / 'screenshots' / name, shots / name)
    shutil.copy2(game / 'logs/latest.log', WORK / 'client-r220.log')
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    evidence = dict(passed=True, revision=220, updated_at=now, installed_sha256=release['sha256'],
        test_world=start['test_world'], source_world_unchanged_files=205, world_height=[-64, 1023],
        invalid_controller=[7, -60, -8], invalid_blueprint_height=[-89, 293], valid_controller_y=[-35, 670],
        actual_controller=[3000, -34, 0], actual_blueprint_height=[-63, 319],
        started=begin, completed=end, elapsed_seconds=elapsed, total_records=1932713, placed=1932712,
        creative_mode=True, complete_saved_geometry_verified=True, real_gt_gui_formed=True,
        forced_chunks_remaining=0, crouch_setting_restored=True, client_normally_exited=True,
        unchanged_system_scores=36, candidate_c4_installed=False,
        limitations=['本次验证创造终端完整搭建与结构成型，不等于生存扣料、工艺或毕业资格。',
                     '单机本次耗时不是低配／手机版性能保证；未作帧时间基准测试。',
                     '原AE测试世界未打开，本轮未新增AE订单或研究防绕过验收。'])
    save(WORK / 'client-verification.json', evidence)
    original = {p: p.read_bytes() for p in [REPORT / 'index.html', REPORT / 'current-summary.json']}
    history = WORK / 'before-report'; history.mkdir(exist_ok=False)
    for p, data in original.items(): (history / p.name).write_bytes(data)
    old = read(REPORT / 'current-summary.json'); data = deepcopy(old)
    state = ('r220客户端实测：W01控制器Y=-60使完整礼堂底部到Y=-89，越过世界下限。'
        '终端现按维度实际建高明确提示完整范围及合法控制器高度；增强版本世界为Y=-35～670。'
        f'在原世界副本Y=-34启动完整创造搭建，约{elapsed:.1f}秒处理1,932,713格，放置1,932,712格，GT界面显示已成型。'
        '正常保存后381区块逐格回读全部一致，成型状态已保存；原存档205份文件未变。'
        '生存扣料、工艺、毕业资格及低配帧时间未验收。')
    receipt = dict(evidence='logs/w01-terminal-bounds-20261108/client-verification.json',
        saved_geometry='logs/w01-terminal-bounds-20261108/saved-world-verification.json',
        release='logs/w01-terminal-bounds-20261108/release.json', state=state, updated_at=now)
    work = data['current_work']; work['state'] = state; work['w01_client_testing'] = receipt
    work['next_turn'] = '继续既有研究反绕过与AE真实订单产出链路；W03 C4仍待审，不自动部署。'
    row = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    prior = next(s for s in old['systems'] if s['id'] == 'multiblocks')
    row['coverage'] = state + ' W03最新外观为C4候选，未批准、未部署；批准57／正式52，既定74项不变。'
    row.update(updated_at=now, changed=True, w01_client_review=receipt)
    cap = row['capabilities'][-1]
    cap['reason'] += ' ' + state
    cap['evidence'] = list(dict.fromkeys(cap.get('evidence', []) + [receipt['evidence'], receipt['saved_geometry'], receipt['release']]))
    cap['updated'] = True
    data['report_updated_at'] = now; data['systems'].sort(key=lambda s: s['percent'])
    assert [(s['id'], s['earned'], s['possible'], s['percent']) for s in data['systems']] == [
        (s['id'], s['earned'], s['possible'], s['percent']) for s in old['systems']]
    assert data['overall_percent'] == old['overall_percent']
    assert all(s == next(p for p in old['systems'] if p['id'] == s['id']) for s in data['systems'] if s['id'] != 'multiblocks')
    for key in ['design_candidate', 'approved_structure_designs', 'structure_batch', 'ae_testing', 'antibypass_testing']:
        assert work[key] == old['current_work'][key]
    assert data['multiblock_scope'] == old['multiblock_scope']
    html = original[REPORT / 'index.html'].decode('utf8')
    anchor = '<main><h1>系统完成度 · 低到高 · 固定入口</h1>'; assert anchor in html
    html = html.replace(anchor, anchor + '<p class="notice" id="w01-height-r220">' + escape(state) +
        ' <a href="../w01-terminal-bounds-20261108/client-verification.json">客户端实测</a> · '
        '<a href="../w01-terminal-bounds-20261108/screenshots/2026-11-08_12.53.55.png">真实成型界面</a></p>', 1)
    card = re.search(r'<details class="system" data-id="multiblocks".*?</details>', html, re.S)[0]
    assert escape(prior['coverage']) in card and escape(prior['capabilities'][-1]['reason']) in card
    revised = card.replace(escape(prior['coverage']), escape(row['coverage']), 1)
    revised = revised.replace(escape(prior['capabilities'][-1]['reason']), escape(cap['reason']), 1)
    html = html.replace(card, revised, 1)
    html, n = re.subn(r'<p>更新 [^<]+</p>', '<p>更新 ' + now + ' · W01建高提示及完整客户端搭建</p>', html, count=1); assert n == 1
    html, n = re.subn(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _: json.dumps(data, ensure_ascii=False).replace('<', '\\u003c'), html, count=1, flags=re.S); assert n == 1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>', html, re.S)[1]) == data
    assert re.findall(r'<details class="system" data-id="([^"]+)"', html) == [s['id'] for s in data['systems']]
    publisher().publish_transaction({REPORT / 'index.html': html,
        REPORT / 'current-summary.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n'}, original)
    save(WORK / 'publication-verification.json', dict(passed=True, original_baseline_saved=True,
        unchanged_system_scores=36, other_systems_unchanged=35, ascending_order=True,
        overall_percent=data['overall_percent'], scope=74, approved=57, formal=52,
        candidate_c4_unchanged=True, audit_html_sha256=sha(REPORT / 'index.html'),
        audit_summary_sha256=sha(REPORT / 'current-summary.json')))
    print(json.dumps(dict(passed=True, elapsed_seconds=elapsed, saved_blocks=saved['matching_noncontroller'],
        overall_percent=data['overall_percent'], installed_sha256=release['sha256'])))


if __name__ == '__main__': main()
