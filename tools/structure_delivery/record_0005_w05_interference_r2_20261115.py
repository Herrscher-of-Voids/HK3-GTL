from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[2]
DELIVERY = 'deliveries/0005_W05_部件穿模检查_R2_20261115'
LOG = 'logs/0005-w05-interference-r2-20261115'
SOURCE = 'deliveries/0005_W05_GTL现有方块近色替换_R2_20261115'
out, log = ROOT / DELIVERY, ROOT / LOG
now = datetime.now().astimezone().isoformat(timespec='seconds')
read = lambda p: json.loads(p.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


capture = read(log / 'inspection-capture.json')
motion = read(log / 'motion-review.json')
static = read(log / 'static-exact-pairs.json')
approval = dict(recorded_at=now, machine='W05', conversation='0005',
    conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
    user_quote='嗯，这个配色可以，那然后就是看一下不同的部件之间会不会有这个的穿模的现象',
    approved_scope='仅R2现有方块配色认可；整机几何与运动净空未批准', source_delivery=SOURCE,
    manifest_sha256=hashlib.sha256((ROOT / SOURCE / 'manifest.json').read_bytes()).hexdigest(),
    existing_blocks=5, new_game_blocks=0, new_game_textures=0)
save(log / 'material-approval.json', approval)
receipt = dict(recorded_at=now, machine='W05', conversation='0005', conversation_id=approval['conversation_id'],
    status='interference_found_geometry_unchanged', source_delivery=SOURCE,
    interactive_inspection=DELIVERY + '/部件穿模检查.html', completion_receipt=LOG + '/completion.json',
    palette_approved=True, material_approval=LOG + '/material-approval.json',
    inspected_components=73, inspected_moving_components=21, static_overlapping_pairs=len(static['pairs']),
    static_pair_memberships=static['total_pair_memberships'],
    static_count_note='64对与105102个成对共占格包括正常嵌接，不能当作64处缺陷；不同于首占归因105076。',
    sampled_modes=['idle', 'work'], sampled_range_s=[0, 60], sampled_step_s=.25, samples_per_mode=241,
    findings=[
        '左右管网与前副塔侧框各450共占格、与后副塔上口各1942共占格；其中上口包含实体机壳/装甲重合。',
        '百叶与前副塔上部左101/右109共占格，后副塔顶各另1格擦碰；已剔除正常基脚。',
        '左右前副塔叶轮转入管网。',
        '六副塔叶轮扫入塔内斜撑；框架alpha孔洞未作逐像素判定，结合定位截图保留方块/模型面干涉结论。',
        '六实体双螺旋海晶灯风柱与叶轮t0每对156共占格；不是纯特效。',
        '左右后副塔实体风柱运动时扫入管网。'],
    allowed_joints='底座、承重臂、前接口、塔基、八轨前后过渡、尾羽根嵌接单列；主涡轮中央轴/轮毂连接单列。',
    undecided_interface='管网与百叶每侧4051共占格，属于安装接口待确认，未直接判为缺陷。',
    continuous_clearance_blocks=motion['continuous_clearance_blocks'],
    crown_vs_all_stationary=motion['crown_vs_all_stationary'],
    evidence=[LOG + '/' + name for name in ['static-review.json', 'static-exact-pairs.json',
        'motion-review.json', 'motion-sampled-center-witnesses.json', 'inspection-cases.json', 'inspection-capture.json']],
    method_limit='单位方块包络检查；中心采样命中证实交叠，未命中不单独证明连续无穿模；框架透明孔洞未逐像素解析。核心/陀螺/王冠另有连续包络净空证明。',
    screenshots=capture['screenshots'], browser_errors=capture['errors'], failed_requests=capture['failed'],
    visual_reviewed_cases=7, diagnostic_colors_only=True, geometry_changed=False, animation_changed=False,
    game_code_modified=False, game_resources_modified=False, jar_built=False, installed=False,
    desktop_used=False, game_started=False, game_verified=False, automated_unit_tests_added=False,
    offline_geometry_inspection_run=True, acceptance_score_changed=False)
save(log / 'completion.json', receipt)
entry = f'''\n\n## 2026-11-15 对话0005：W05 R2配色认可与部件穿模检查

- 负责人认可R2现有方块配色；5种已有方块/零新增保持，只批准配色，不等于完整几何或游戏验收。批准来源与哈希：`{LOG}/material-approval.json`。
- 73构件参考姿态完整成对交集，21运动构件待机/工作0～60秒每0.25秒取样，并补核心/陀螺/王冠连续净空证明。明确问题集中于两翼副塔：管网穿前塔侧框与后塔上口、百叶局部碰塔、前叶轮碰管网、六叶轮扫斜撑、六实体风柱穿叶轮及后风柱扫管网。正常嵌接单列，管网与百叶安装接口待确认；64对交集不能当作64处缺陷。
- 定位页：`{DELIVERY}/部件穿模检查.html`，7处代表性复现与截图；红/蓝是检查叠加色，黄色是共占格或中心见证点。原R2材质/几何/动画均未改。7截图页面错误和请求失败0；未构建/安装JAR、运行游戏，不改变批准建筑数量、原验收分或37域总分。回执：`{LOG}/completion.json`。
'''
for p in (ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md'):
    with p.open('a', encoding='utf8', newline='') as stream:
        stream.write(entry)
audit = ROOT / 'logs/beta5-completion-audit-20261030'
history = log / ('audit-before-update-' + datetime.now().strftime('%H%M%S'))
history.mkdir()
for name in ('index.html', 'current-summary.json'):
    shutil.copy2(audit / name, history / name)
summary = read(audit / 'current-summary.json')
system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
system['w05_0005_r2_material_approval'] = approval
system['w05_0005_r2_interference_inspection'] = receipt
summary['report_updated_at'] = now
summary['systems'] = sorted(summary['systems'], key=lambda s: s['percent'])
save(audit / 'current-summary.json', summary)
html = (audit / 'index.html').read_text('utf8')
section = f'''<section class="notice" id="w05-r2-interference-0005"><h2>0005 · W05 R2配色认可；两翼副塔存在干涉</h2><p>负责人认可5种现有方块配色。73构件参考交集、21运动构件待机/工作各241帧与关键连续净空检查发现：管网穿前塔侧框和后塔上口、百叶局部碰塔、前叶轮碰管网、六叶轮扫斜撑、六实体风柱穿叶轮、两后风柱扫管网。正常嵌接单列。</p><p>核心、两陀螺及三王冠有连续净空；7处代表性复现与截图已定位。仅检查，不改几何/动画，不等同游戏成型运行验收；37域分数保持。</p><p>{now} · <a href="../../{DELIVERY}/部件穿模检查.html">穿模定位页</a> · <a href="../0005-w05-interference-r2-20261115/completion.json">检查回执</a></p></section>'''
html = html.replace('<body>', '<body>' + section, 1)
embedded = json.dumps(summary, ensure_ascii=False, indent=2).replace('<', '\\u003c')
html = re.sub(r'(<script type="application/json" id="audit-data">).*?(</script>)', lambda m: m[1] + '\n' + embedded + '\n' + m[2], html, count=1, flags=re.S)
(audit / 'index.html').write_text(html, 'utf8')
save(log / 'publication.json', dict(recorded_at=now, fixed_report=str(audit / 'index.html'),
    baseline_snapshot=str(history), overall_percent=summary['overall_percent'], domain_count=summary['domain_count'], scores_changed=False))
print(json.dumps(dict(palette_approved=True, interference_found=True, geometry_changed=False,
    screenshots=len(capture['screenshots']), browser_errors=capture['errors'], overall_percent=summary['overall_percent'])))
