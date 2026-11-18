from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[2]
DELIVERY = 'deliveries/0005_W05_七处穿模修订_R3_20261115'
LOG = 'logs/0005-w05-clearance-r3-20261115'
out, log = ROOT / DELIVERY, ROOT / LOG
now = datetime.now().astimezone().isoformat(timespec='seconds')
read = lambda p: json.loads(p.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


manifest = read(out / 'manifest.json')
capture = read(log / 'preview-capture.json')
clearance = read(out / '净空检查.json')
receipt = dict(recorded_at=now, machine='W05', candidate='R3', conversation='0005',
    conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
    user_quote='可以，你给我一个预览看看吧', status='independent_preview_pending_appearance_review',
    source_delivery='deliveries/0005_W05_GTL现有方块近色替换_R2_20261115',
    interactive_preview=DELIVERY + '/三维评审.html', manifest_sha256=hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest(),
    size_wdh=manifest['size_wdh'], components=len(manifest['components']),
    modified_components=manifest['revision']['modified_components'],
    source_component_voxels=manifest['source_component_voxels'], unique_occupied_voxels=manifest['unique_occupied_voxels'],
    palette_approved=True, distinct_existing_blocks=5, new_game_blocks=0, new_game_textures=0,
    geometry_inspection=clearance, browser_errors=capture['errors'], failed_requests=capture['failed'],
    screenshots=capture['screenshots'], appearance_approved=False, game_code_modified=False,
    game_resources_modified=False, jar_built=False, installed=False, desktop_used=False,
    game_started=False, game_verified=False, automated_unit_tests_added=False,
    offline_geometry_inspection_run=True, acceptance_score_changed=False)
save(log / 'completion.json', receipt)
entry = f'''\n\n## 2026-11-15 对话0005：W05七处穿模修订R3预览

- 负责人批准七项修复方案并要求预览。独立候选：`{DELIVERY}/三维评审.html`；保持R2认可的5种现有方块、零新增材质、删梁状态，整机555×701×321格、73构件，22构件局部更新。
- 管网、卡箍、内灯线与流光共用绕塔路线；后塔外过刃区局部内收8格。百叶安装点跟随绕行，冲突片切向避让并保留24片与底部桁架。六叶轮半径38→35，跨盘斜撑贴壁外拱；实体双螺旋在叶轮上下分段收轴，以半径0.6的细光流穿既有轮毂孔。
- 完整几何、连续转动包络与正常嵌接分类见`{DELIVERY}/净空检查.json`；截图与浏览器记录见`{LOG}/preview-capture.json`。R3外观尚待负责人评审，离线检查不等于游戏成型运行验收。
- 未替换游戏资源、构建或安装JAR，未操作桌面/游戏/实例/存档；系统分数、37域分母与批准数量保持。回执：`{LOG}/completion.json`。
'''
for path in (ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md'):
    with path.open('a', encoding='utf8', newline='') as stream:
        stream.write(entry)
audit = ROOT / 'logs/beta5-completion-audit-20261030'
history = log / ('audit-before-update-' + datetime.now().strftime('%H%M%S'))
history.mkdir()
for name in ('index.html', 'current-summary.json'):
    shutil.copy2(audit / name, history / name)
summary = read(audit / 'current-summary.json')
system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
system['w05_0005_r3_clearance_preview'] = receipt
summary['report_updated_at'] = now
summary['systems'] = sorted(summary['systems'], key=lambda s: s['percent'])
save(audit / 'current-summary.json', summary)
html = (audit / 'index.html').read_text('utf8')
section = f'''<section class="notice" id="w05-r3-clearance-0005"><h2>0005 · W05 R3七处避让修订候选</h2><p>负责人批准修复方案后生成独立预览。555×701×321、73构件；管网局部绕塔、百叶避让、叶轮缩至半径35、斜撑外拱、实体风柱上下分段，中孔细光流接通。R2配色保持，5种已有方块、零新增游戏材质。</p><p>实际离线净空与正常连接分类详见检查记录。R3外观待评审，未改运行资源或进行游戏验收，37域分数与批准数量保持。</p><p>{now} · <a href="../../{DELIVERY}/三维评审.html">R3三维预览</a> · <a href="../../{DELIVERY}/净空检查.json">净空记录</a> · <a href="../0005-w05-clearance-r3-20261115/completion.json">回执</a></p></section>'''
html = html.replace('<body>', '<body>' + section, 1)
embedded = json.dumps(summary, ensure_ascii=False, indent=2).replace('<', '\\u003c')
html = re.sub(r'(<script type="application/json" id="audit-data">).*?(</script>)', lambda m: m[1] + '\n' + embedded + '\n' + m[2], html, count=1, flags=re.S)
(audit / 'index.html').write_text(html, 'utf8')
save(log / 'publication.json', dict(recorded_at=now, fixed_report=str(audit / 'index.html'),
    baseline_snapshot=str(history), overall_percent=summary['overall_percent'], domain_count=summary['domain_count'], scores_changed=False))
shutil.copy2(Path(__file__), out / '生成脚本' / Path(__file__).name)
print(json.dumps(dict(output=DELIVERY, images=len(capture['screenshots']), browser_errors=capture['errors'], scores_changed=False), ensure_ascii=False))
