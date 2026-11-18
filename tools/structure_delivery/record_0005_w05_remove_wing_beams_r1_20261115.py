from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[2]
DELIVERY = 'deliveries/0005_W05_移除双翼后掠主梁_R1_20261115'
LOG = 'logs/0005-w05-remove-wing-beams-r1-20261115'
out, log = ROOT / DELIVERY, ROOT / LOG
now = datetime.now().astimezone().isoformat(timespec='seconds')
read = lambda path: json.loads(path.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


manifest = read(out / 'manifest.json')
capture = read(log / 'preview-capture.json')
receipt = dict(recorded_at=now, machine='W05', conversation='0005', conversation_id=manifest['conversation_id'],
    status='R1_preview_requested_geometry_edit_completed', user_quote=manifest['revision']['user_quote'],
    source_delivery=manifest['revision']['source_delivery'],
    source_manifest_sha256=hashlib.sha256((ROOT / manifest['revision']['source_delivery'] / 'manifest.json').read_bytes()).hexdigest(),
    preview=DELIVERY + '/index.html', interactive_preview=DELIVERY + '/三维评审.html', manifest=DELIVERY + '/manifest.json',
    completion_receipt=LOG + '/completion.json', removed_components=manifest['revision']['removed_components'],
    removed_component_count=12, removed_component_voxels=322276, retained_component_count=len(manifest['components']),
    retained_components_payload_fields_unchanged=True, retained_npz_arrays_unchanged=True, material_files_unchanged=True,
    size_wdh=manifest['size_wdh'], occupied_bounds_xyz=manifest['occupied_bounds_xyz'],
    component_voxels=manifest['source_component_voxels'], unique_occupied_voxels=manifest['unique_occupied_voxels'],
    overlap_extra_memberships=manifest['overlap_extra_memberships'], rendered_surface_quads=manifest['preview']['merged_quads'],
    screenshots=len(capture['screenshots']), browser_errors=capture['errors'], failed_requests=capture['failed'],
    visually_reviewed=['整体预览.png', '俯视预览.png', '侧面预览.png', '双翼管网近景.png'],
    previous_delivery_preserved=True, selected_as_current_iteration=True, final_appearance_approved=False,
    existing_runtime_w05_a4_replaced=False, game_code_modified=False, jar_built=False, installed=False,
    desktop_used=False, game_started=False, game_verified=False, automated_tests_run=False, acceptance_score_changed=False)
save(log / 'completion.json', receipt)
baseline = dict(recorded_at=now, machine='W05', conversation='0005', conversation_id=manifest['conversation_id'],
    decision='current_design_iteration_after_requested_removal', baseline=DELIVERY,
    source_baseline=manifest['revision']['source_delivery'], interactive_preview=receipt['interactive_preview'],
    baseline_manifest_sha256=hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest(),
    requested_change='左右翼全部12根后掠空心主梁已删除；其余73构件逐值保持',
    geometry_changed=True, final_appearance_approved=False, existing_runtime_w05_a4_replaced=False,
    jar_built=False, installed=False, acceptance_score_changed=False)
save(log / 'design-baseline.json', baseline)
entry = f'''\n\n## 2026-11-15 对话0005：W05移除双翼后掠空心主梁R1

- 负责人要求“第一步，先将左翼、右翼的后掠空心主梁全删掉”。在已采用的作者原案上独立派生R1，准确删除 `wing_left_beam_1..6` 与 `wing_right_beam_1..6` 共12梁、322,276构件内方块；旧原案完整保留。
- 当前继续修改基线为 `{DELIVERY}/三维评审.html`。其余73构件的全部渲染字段、整数格坐标与材料数组逐值保持；7种材质、双翼管网、副塔、导流叶片、王冠、中轴和底座不变。实际包围盒仍555×701×321，6,789,719构件内方块、6,684,643唯一占格，1,344,605表面合并面。
- 15张headless预览截图完成，页面错误和请求失败均0；已查看整体、俯视、侧面与翼部近景。仅网页预览修订，未替换游戏A4资源、构建或安装JAR、操作桌面/游戏/实例/存档；未运行自动化测试，不改变外观批准数、既有验收分和37域总分。回执：`{LOG}/completion.json`。
'''
for path in (ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md'):
    with path.open('a', encoding='utf8', newline='') as stream:
        stream.write(entry)
audit = ROOT / 'logs/beta5-completion-audit-20261030'
history = log / 'audit-before-update'
history.mkdir(exist_ok=True)
for name in ('index.html', 'current-summary.json'):
    shutil.copy2(audit / name, history / name)
summary = read(audit / 'current-summary.json')
system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
system['w05_0005_remove_wing_beams_r1_preview'] = receipt
system['w05_0005_current_design_baseline'] = baseline
summary['w05_remove_wing_beams_0005_r1_20261115_receipt'] = LOG + '/completion.json'
summary['report_updated_at'] = now
summary['systems'] = sorted(summary['systems'], key=lambda s: s['percent'])
save(audit / 'current-summary.json', summary)
html = (audit / 'index.html').read_text('utf8')
section = f'''<section class="notice" id="w05-remove-wing-beams-r1-0005"><h2>0005 · W05 R1：双翼12根后掠空心主梁已删除</h2><p>按负责人第一步修改，准确删除左翼6梁与右翼6梁；其余73构件的几何、坐标、材质及动态参数逐值保持。原案保留，当前继续修改基线为R1；555×701×321实际范围不变。</p><p>15张网页截图，页面错误0；已查看整体、俯视、侧面及翼部近景。仅预览修订，未替换游戏资源、构建或安装JAR；批准数量、37域分数和分母保持。</p><p>{now} · <a href="../../{DELIVERY}/三维评审.html">R1三维预览</a> · <a href="../../{DELIVERY}/index.html">R1图集</a> · <a href="../0005-w05-remove-wing-beams-r1-20261115/completion.json">修订回执</a></p></section>'''
html = html.replace('<body>', '<body>' + section, 1)
html = html.replace('负责人已选定此原案为后续W05设计基线；继续在此基础上迭代，尚非最终外观定稿，运行中A4本轮未替换。',
                    '负责人已选定此原案为W05来源基线；当前迭代为顶部R1删梁版，尚非最终外观定稿，运行中A4未替换。', 1)
embedded = json.dumps(summary, ensure_ascii=False, indent=2).replace('<', '\\u003c')
html = re.sub(r'(<script type="application/json" id="audit-data">).*?(</script>)', lambda m: m[1] + '\n' + embedded + '\n' + m[2], html, count=1, flags=re.S)
(audit / 'index.html').write_text(html, 'utf8')
save(log / 'publication.json', dict(recorded_at=now, receipt=LOG + '/completion.json', fixed_report=str(audit / 'index.html'),
    baseline_snapshot=str(history), overall_percent=summary['overall_percent'], domain_count=summary['domain_count'], scores_changed=False))
shutil.copy2(Path(__file__), out / '生成脚本' / Path(__file__).name)
print(json.dumps(dict(parts=receipt['retained_component_count'], browser_errors=receipt['browser_errors'],
    overall_percent=summary['overall_percent']), ensure_ascii=False))
