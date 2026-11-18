from datetime import datetime
import json
from pathlib import Path
import shutil

from package_0005_w12_author_blueprint_20261116 import digest, save


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W12_三环翻转_A3_20261116'
LOG = ROOT / 'logs/0005-w12-flip-a3-20261116'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
now = datetime.now().astimezone().isoformat()
motion = json.loads((OUT / 'motion.json').read_text('utf8'))
capture = json.loads((OUT / 'preview-capture.json').read_text('utf8'))
clearance = json.loads((OUT / 'continuous-clearance.json').read_text('utf8'))
preview_path = str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/')
receipt_path = str((LOG / 'completion.json').relative_to(ROOT)).replace('\\', '/')
receipt = dict(candidate='W12 A3', updated_at=now, conversation='0005',
    status='三环绕球心翻转预览待审', decision='三环改翻转，取消环内自转',
    parent_candidate='deliveries/0005_W12_三环分层扩腔_A2_20261116', preview=preview_path,
    motion=motion, geometry_changed=False, radii=[25, 36, 47], cavity_nominal_diameter=110,
    actual_size_wdh=[1063, 847, 347], blocks=23541415,
    clearance=dict(inherited_from='A2完整方块径向证明，适用于任意过共同球心的转轴', **clearance['summary']),
    visual_review=dict(screenshots=len(capture['views']) + 1, errors=capture['errors'], failed_requests=capture['failed'],
        inspected=['核心零秒、15秒、30秒、60秒环面变化', '核心与邻件30秒', '工作态', '整体']),
    remaining='外围链廊、冠环与塔的固定交叠及占地递增沿用A2待修订记录。',
    nbt=dict(path=str(OUT / 'W12-全域能量约束壁-A3.nbt'), sha256=digest(OUT / 'W12-全域能量约束壁-A3.nbt'),
        static_pose='零秒姿态与A2相同'),
    appearance_approved=False, game_code_modified=False, jar_built=False, installed=False,
    desktop_used=False, game_verified=False, scores_changed=False)
for directory in (OUT, LOG):
    save(directory / 'completion.json', receipt)
backup = REPORT / ('history/before-0005-w12-flip-a3-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
for name in ('index.html', 'current-summary.json'):
    shutil.copy2(REPORT / name, backup / name)
summary = json.loads((REPORT / 'current-summary.json').read_text('utf8'))
system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
system.update(w12_0005_flip_a3=receipt, w12_current_design_stage='A3三环绕球心翻转，预览待审',
    w12_current_design_candidate=preview_path, updated_at=now)
summary['w12_0005_flip_a3_receipt'] = receipt_path
summary['report_updated_at'] = now
summary['systems'].sort(key=lambda s: s['percent'])
save(REPORT / 'current-summary.json', summary)
html = (REPORT / 'index.html').read_text('utf8')
start = html.index('</summary>', html.index('<details id="system-multiblocks"')) + len('</summary>')
notice = '<section class="notice"><h3>W12 A3：三环球心翻转</h3><p>三环分别绕球心Y、Z、X直径轴翻转，环面朝向持续变化。25/36/47半径及110格空腔保持，A2全相位净空下界3.271603/4.068534格继续成立。预览待审，外围固定交叠仍待修订，原分数保持。</p><p><a href="../../' + preview_path + '">打开翻转预览</a></p></section>'
html = html[:start] + notice + html[start:]
marker = '<script type="application/json" id="audit-data">'
start = html.index(marker) + len(marker)
end = html.index('</script>', start)
html = html[:start] + '\n' + json.dumps(summary, ensure_ascii=False, indent=2) + '\n' + html[end:]
(REPORT / 'index.html').write_text(html, 'utf8')
memory = f'''\n\n## 2026-11-16 对话0005：W12三环翻转A3

- 负责人要求核心三环改为翻转，取消原环内自转。独立预览`{preview_path}`，默认聚焦三重十字核心。
- 三环初始法线X/Y/Z，分别绕共同球心(531,180,423)的Y/Z/X直径轴持续翻转，转速0.055/-0.047/0.062弧度每秒，工作态乘1.8；无原法线自转叠加。半径25/36/47、名义空腔110、实体方块与配色沿用A2。
- A2完整方块径向证明适用于任意过共同球心转轴，全相位运动间净空下界3.271603格、运动对固定件下界4.068534格保持。7幅视角与界面已输出，页面错误{len(capture['errors'])}、资源失败{len(capture['failed'])}。外围静态交叠及占地递增待修订，外观待审。
- 回执`{receipt_path}`，时间`{now}`。本轮更新网页翻转与参数记录；游戏源码、JAR、安装及实机状态保持，原分数和批准数量保持。
'''
for name in ('AGENTS.md', 'rule/当前多方块设计规则.md'):
    with (ROOT / name).open('a', encoding='utf8') as handle:
        handle.write(memory)
shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
save(OUT / 'manifest.json', dict(machine='W12', candidate='A3', updated_at=now,
    status=receipt['status'], files={str(p.relative_to(OUT)).replace('\\', '/'): dict(bytes=p.stat().st_size,
        sha256=digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'manifest.json'}))
save(LOG / 'record-update.json', dict(updated_at=now, report_backup=str(backup), scores_changed=False,
    overall_percent=summary['overall_percent']))
print(json.dumps(dict(preview=preview_path, errors=capture['errors'], overall_percent=summary['overall_percent'])))
