from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[2]
DELIVERY = 'deliveries/0005_W05_GTL现有方块近色替换_R2_20261115'
LOG = 'logs/0005-w05-existing-materials-r2-20261115'
out, log = ROOT / DELIVERY, ROOT / LOG
now = datetime.now().astimezone().isoformat(timespec='seconds')
read = lambda path: json.loads(path.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


manifest = read(out / 'manifest.json')
capture = read(log / 'preview-capture.json')
receipt = dict(recorded_at=now, machine='W05', conversation='0005', conversation_id=manifest['conversation_id'],
    status='R2_existing_blocks_material_preview_pending_review', user_request=manifest['revision']['user_request'],
    source_delivery=manifest['revision']['source_delivery'], preview=DELIVERY + '/index.html',
    interactive_preview=DELIVERY + '/三维评审.html', manifest=DELIVERY + '/manifest.json',
    completion_receipt=LOG + '/completion.json', material_mapping=read(out / '现有方块映射.json'),
    existing_block_types=5, material_slots=7, new_registered_blocks=0, new_game_textures=0,
    material_sources=DELIVERY + '/材质来源.json', active_resourcepacks=manifest['active_resourcepacks'],
    geometry_source='R1', retained_components=73, retained_components_payload_fields_unchanged=True,
    retained_npz_file_unchanged=True, npz_sha256=hashlib.sha256((out / '原始构件数据.npz').read_bytes()).hexdigest(),
    size_wdh=manifest['size_wdh'], occupied_bounds_xyz=manifest['occupied_bounds_xyz'],
    palette='深青灰、冷白、薄荷青绿；原生材质近色转译，非逐像素同色',
    visual_difference='原蜂窝玻璃用途改为铱框架镂空网面，纹样与透光方式有差异；海晶灯取动画首帧。',
    native_frame_model='gtceu:block/material_sets/dull/frame_gt',
    native_frame_tints=manifest['native_frame_tints'], native_ctm_previewed=False,
    effects_scope='流光、核心能量与工作白色风眼仅为原有网页机器特效，非防水机械方块原生发光。',
    screenshots=len(capture['screenshots']), browser_errors=capture['errors'], failed_requests=capture['failed'],
    visually_reviewed=['整体预览.png', '双翼管网近景.png', '满载工作预览.png', '评审界面.png'],
    previous_deliveries_preserved=True, geometry_baseline_changed=False, final_materials_approved=False,
    game_code_modified=False, game_resources_modified=False, existing_runtime_w05_a4_replaced=False,
    jar_built=False, installed=False, desktop_used=False, game_started=False, game_verified=False,
    automated_tests_run=False, acceptance_score_changed=False)
save(log / 'completion.json', receipt)
entry = f'''\n\n## 2026-11-15 对话0005：W05现有方块近色替换R2候选

- 负责人要求尽量改用GTL整合包已有方块、保持配色。原7项只是未注册的网页预览材质；R2用5种已有方块覆盖7个用途槽，零新增游戏方块或材质：防水机械方块、塑料混凝土、铱框架、海晶灯、不锈钢框架。
- 基于增强版3.9实际JAR与当前启用资源包读取原生贴图；铱框架主色#99FEDE、次色#6CD1CF还原原生双层镂空。深青灰、冷白、薄荷青绿为近色方向；蜂窝玻璃改为镂空框架，纹样、透光方式和局部色值有差异，不宣称完全同色或保留蜂窝纹。
- 独立候选：`{DELIVERY}/三维评审.html`。R1的73构件数据逐值相同、NPZ字节哈希相同，删梁几何基线不变；R2材料待负责人评审。15张headless截图、页面错误与请求失败均0；未替换游戏代码/资源、构建、安装或启动游戏，不改变批准数量与37域分数。回执：`{LOG}/completion.json`。
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
system['w05_0005_existing_blocks_r2_preview'] = receipt
summary['w05_existing_blocks_0005_r2_20261115_receipt'] = LOG + '/completion.json'
summary['report_updated_at'] = now
summary['systems'] = sorted(summary['systems'], key=lambda s: s['percent'])
save(audit / 'current-summary.json', summary)
html = (audit / 'index.html').read_text('utf8')
section = f'''<section class="notice" id="w05-existing-blocks-r2-0005"><h2>0005 · W05 R2：5种已有方块近色预览</h2><p>原7个用途槽替换为防水机械方块、塑料混凝土、铱框架、海晶灯和不锈钢框架，零新增游戏方块/材质。沿用深青灰、冷白、薄荷青绿方向；蜂窝玻璃转为铱框架镂空网面，纹样、透光方式及局部色值有差异。</p><p>R1删梁后的73构件及NPZ保持，R2材料候选待负责人评审。15张网页截图、页面错误0；未替换游戏代码/资源、构建或安装JAR，37域分数及批准数量不变。</p><p>{now} · <a href="../../{DELIVERY}/三维评审.html">R2三维预览</a> · <a href="../../{DELIVERY}/index.html">R2图集</a> · <a href="../0005-w05-existing-materials-r2-20261115/completion.json">材质回执</a></p></section>'''
html = html.replace('<body>', '<body>' + section, 1)
embedded = json.dumps(summary, ensure_ascii=False, indent=2).replace('<', '\\u003c')
html = re.sub(r'(<script type="application/json" id="audit-data">).*?(</script>)', lambda m: m[1] + '\n' + embedded + '\n' + m[2], html, count=1, flags=re.S)
(audit / 'index.html').write_text(html, 'utf8')
save(log / 'publication.json', dict(recorded_at=now, receipt=LOG + '/completion.json', fixed_report=str(audit / 'index.html'),
    baseline_snapshot=str(history), overall_percent=summary['overall_percent'], domain_count=summary['domain_count'], scores_changed=False))
shutil.copy2(Path(__file__), out / '生成脚本' / Path(__file__).name)
print(json.dumps(dict(existing_blocks=5, slots=7, new_blocks=0, screenshots=len(capture['screenshots']),
    browser_errors=capture['errors'], overall_percent=summary['overall_percent']), ensure_ascii=False))
