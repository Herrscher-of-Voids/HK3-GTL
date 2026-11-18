from datetime import datetime
import json
from pathlib import Path
import shutil

from package_0005_w12_author_blueprint_20261116 import digest, save


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W12_三环分层扩腔_A2_20261116'
LOG = ROOT / 'logs/0005-w12-clearance-a2-20261116'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
now = datetime.now().astimezone().isoformat()
geometry = json.loads((OUT / 'geometry.json').read_text('utf8'))
clearance = json.loads((OUT / 'continuous-clearance.json').read_text('utf8'))
capture = json.loads((OUT / 'preview-capture.json').read_text('utf8'))
nbt = OUT / 'W12-全域能量约束壁-A2.nbt'
receipt_path = str((LOG / 'completion.json').relative_to(ROOT)).replace('\\', '/')
preview_path = str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/')
receipt = dict(updated_at=now, conversation='0005', conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
    candidate='W12 A2', status='三环分层扩腔候选待审', decision='保留三环转动，分层半径并扩大核心空腔',
    parent='deliveries/0005_W12_作者蓝图原案_A1_20261116', delivery=str(OUT),
    ring_radii=[25, 36, 47], cavity_nominal_diameter=110,
    physical_lance_radii=[55, 74], energy_lance_radii=[15.9, 55],
    actual_size_wdh=geometry['actual_size_wdh'], blocks=geometry['blocks'],
    source_component_blocks=geometry['source_component_blocks'], components=len(geometry['components']),
    changed_components=geometry['changed_components'], source_notes=geometry['source_notes'],
    non_vanilla_percent=geometry['non_vanilla_percent'],
    continuous_clearance=clearance['summary'],
    continuous_clearance_evidence=str((LOG / 'continuous-clearance.json').relative_to(ROOT)).replace('\\', '/'),
    preview=dict(screenshots=len(capture['views']) + 1, errors=capture['errors'], failed_requests=capture['failed'],
        visually_inspected=['整体', '三重十字与完整方块三环', '核心与邻件待机及37秒', '工作态能量矛', '原生像素近景']),
    remaining=['双长廊固定交叠与中央汇合', '核心以外锁链相交与穿廊', '冠环与四内塔及垂丝与墙塔', '占地递增少240格'],
    controller_blueprint=[531, 50, 10], interface_rule=geometry['interface_rule'],
    nbt=dict(path=str(nbt), bytes=nbt.stat().st_size, sha256=digest(nbt)),
    appearance_approved=False, whole_machine_clearance_approved=False,
    game_code_modified=False, jar_built=False, installed=False, desktop_used=False,
    game_verified=False, scores_changed=False, fixed_report=str(REPORT / 'index.html'))
save(LOG / 'completion.json', receipt)
save(OUT / 'completion.json', receipt)
backup = REPORT / ('history/before-0005-w12-a2-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
for name in ('index.html', 'current-summary.json'):
    shutil.copy2(REPORT / name, backup / name)
summary = json.loads((REPORT / 'current-summary.json').read_text('utf8'))
system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
system['w12_0005_clearance_a2'] = receipt
system['w12_current_design_stage'] = 'A2核心连续净空完成，外围固定交叠待修订，外观待审'
system['w12_current_design_candidate'] = preview_path
system['updated_at'] = now
system['capabilities'][3]['evidence'].append(receipt_path)
summary['w12_0005_clearance_a2_receipt'] = receipt_path
summary['report_updated_at'] = now
summary['systems'].sort(key=lambda s: s['percent'])
save(REPORT / 'current-summary.json', summary)
html = (REPORT / 'index.html').read_text('utf8')
start = html.index('</summary>', html.index('<details id="system-multiblocks"')) + len('</summary>')
notice = '<section class="notice"><h3>W12 A2：三环分层扩腔候选</h3><p>三环半径25/36/47，空腔名义直径110；十二实体矛外移，靠芯锁链移锚，长廊清出球形开口。完整原始方块的径向界证明核心全部相位分离。外围链廊、冠环塔与占地递增继续待修订。外观待审，原验收4/6、研发4/5及全库分数保持。</p><p><a href="../../' + preview_path + '">打开A2方块预览</a> · <a href="../../' + receipt_path + '">交付回执</a></p></section>'
html = html[:start] + notice + html[start:]
marker = '<script type="application/json" id="audit-data">'
start = html.index(marker) + len(marker)
end = html.index('</script>', start)
html = html[:start] + '\n' + json.dumps(summary, ensure_ascii=False, indent=2) + '\n' + html[end:]
(REPORT / 'index.html').write_text(html, 'utf8')
memory = f'''\n\n## 2026-11-16 对话0005：W12三环分层扩腔A2

- 负责人选择保留三环转动、分层半径并扩大核心空腔。独立候选`{preview_path}`；A1保留，A2外观待审。
- 三环名义半径25/36/47格，各自原法线与转速保留；三十字原臂端尺寸保留，按整数格原点半径55挖腔，名义直径110。十二实体矛沿原方向置于半径55至74，金色特效从15.9至55续接白洞。
- 靠芯锁链重接外侧十字臂锚点，双长廊清出球形核心开口。完整原始方块[p,p+(1,1,1)]逐件径向界见`logs/0005-w12-clearance-a2-20261116/continuous-clearance.json`，环间全相位净空下界{clearance['summary']['moving_pair_min_clearance_lower_bound']:.6f}格，运动件对所有固定件下界{clearance['summary']['fixed_min_clearance_lower_bound']:.6f}格。网页与NBT使用完整方块，净空证明采用覆盖前原始占格。
- 实际宽深高{'×'.join(map(str, geometry['actual_size_wdh']))}，{geometry['blocks']:,}去重实体格。主控(531,50,10)，其他实体格自由替换合法通用接口并自选朝向，配色保持。核心以外链链/链廊、冠环/塔及垂丝/墙塔静态交叠、占地比W10少240格继续待修订。
- 本轮交付预览、NBT与连续净空数据；未修改游戏源码、构建安装JAR或操作游戏。原验收、研发分数及批准数量保持。回执`{receipt_path}`，时间`{now}`。
'''
for name in ('AGENTS.md', 'rule/当前多方块设计规则.md'):
    with (ROOT / name).open('a', encoding='utf8') as handle:
        handle.write(memory)
for name in (Path(__file__).name, 'measure_0005_w12_clearance_a2_20261116.py', 'measure_0005_w12_core_a2_20261116.py'):
    shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
manifest['updated_at'] = now
manifest['files'] = {str(p.relative_to(OUT)).replace('\\', '/'): dict(bytes=p.stat().st_size, sha256=digest(p))
    for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'manifest.json'}
save(OUT / 'manifest.json', manifest)
save(LOG / 'record-update.json', dict(updated_at=now, report_backup=str(backup), scores_changed=False,
    overall_percent=summary['overall_percent'], domain_count=summary['domain_count']))
print(json.dumps(dict(receipt=receipt_path, overall_percent=summary['overall_percent'], **clearance['summary'])))
