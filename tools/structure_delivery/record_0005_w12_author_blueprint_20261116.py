from datetime import datetime
from html import escape
import json
from pathlib import Path
import shutil

from package_0005_w12_author_blueprint_20261116 import OUT, LOG, ROOT, digest, save


now = datetime.now().astimezone().isoformat()
geometry = json.loads((OUT / 'geometry.json').read_text('utf8'))
capture = json.loads((OUT / 'preview-capture.json').read_text('utf8'))
nbt = OUT / 'W12-全域能量约束壁-A1.nbt'
receipt_path = str((LOG / 'completion.json').relative_to(ROOT)).replace('\\', '/')
preview_path = str((OUT / 'index.html').relative_to(ROOT)).replace('\\', '/')
report = ROOT / 'logs/beta5-completion-audit-20261030'
shutil.copy2(ROOT / 'tools/structure_delivery/capture_0005_w12_author_blueprint_20261116.mjs', OUT / '生成脚本/capture_0005_w12_author_blueprint_20261116.mjs')
shutil.copy2(ROOT / 'tools/structure_delivery/prepare_0005_w12_viewer_20261116.py', OUT / '生成脚本/prepare_0005_w12_viewer_20261116.py')
receipt = dict(updated_at=now, conversation='0005', conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
    candidate='W12 A1', status='作者原案完整方块预览与NBT，外观待审', delivery=str(OUT),
    actual_size_wdh=geometry['actual_size_wdh'], bounds=geometry['bounds'], blocks=geometry['blocks'],
    source_component_blocks=geometry['source_component_blocks'], overlap_extra_memberships=geometry['overlap_extra_memberships'],
    components=len(geometry['components']), surface_quads=geometry['surface_quads'],
    unique_block_types=geometry['unique_block_types'], non_vanilla_blocks=geometry['non_vanilla_blocks'],
    non_vanilla_percent=geometry['non_vanilla_percent'], footprint_area=geometry['footprint_area'],
    bounding_box_volume=geometry['bounding_box_volume'], actual_height=geometry['actual_height'],
    source=geometry['source'], preview=dict(screenshots=len(capture['views']) + 1,
        errors=capture['errors'], failed_requests=capture['failed'],
        visually_inspected=['整体前斜视', '三重十字与工作态', '32条实体链穿扣', '十字花窗', '蜂窝场工作', '原生像素近景']),
    controller_blueprint=[531, 50, 10], controller_export=[531, 69, 10], controller_status='附件原坐标，红石块仅定位',
    interface_rule=geometry['interface_rule'],
    source_conflicts=['名义1063×847占地900361，比已批准W10少240格，规模递增待修订',
        'Y0..327含328层，倾斜抱箍延伸至Y-19，完整实际高度347',
        '东西600格长廊在总宽1063内重叠137格',
        '原文数千柱及数千花窗与给定尺寸冲突，本稿480根柱、18花窗',
        '原文将Z10侧称南侧，坐标保留',
        '八塔顶Y327与光环顶同高，网页取塔顶至环冠的近水平光束'],
    dynamic_preview=dict(web_only=True, honeycomb_period_seconds=10, maximum_wave_radius=500,
        butterflies=320, controller_marker='minecraft:redstone_block',
        rendering='NBT同格覆盖结果分组显示；近景最近邻像素，远景使用标准纹理mipmap降低闪烁',
        butterfly_dissolve='按高度接近下部线圈层变金消散，网页未做逐线圈碰撞'),
    appearance_approved=False, game_code_modified=False, jar_built=False, installed=False,
    instance_access=False, desktop_used=False, game_verified=False, scores_changed=False,
    nbt=dict(path=str(nbt), bytes=nbt.stat().st_size, sha256=digest(nbt),
        readback_size_xyz=[1063, 347, 847], readback_blocks=23672824),
    fixed_report=str(report / 'index.html'))
save(LOG / 'completion.json', receipt)
save(OUT / 'completion.json', receipt)

snapshot = report / ('history/before-0005-w12-a1-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
snapshot.mkdir(parents=True)
for name in ('index.html', 'current-summary.json'):
    shutil.copy2(report / name, snapshot / name)
summary = json.loads((report / 'current-summary.json').read_text('utf8'))
system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
system['w12_0005_author_blueprint'] = receipt
system['w12_current_design_stage'] = '作者原案完整方块预览待审；尺寸递增与空间交叠留待修订'
system['w12_current_design_candidate'] = preview_path
system['updated_at'] = now
note = ' W12 A1已导出100构件、23672824实体格、1063×847×347的完整方块预览与NBT，32实体锁链、480约束柱和18十字窗；外观待审。名义占地比W10少240格，原案尺寸和交叠保留待修订。'
system['coverage'] += note
system['capabilities'][3]['reason'] += note
system['capabilities'][3]['evidence'].append(receipt_path)
summary['w12_0005_author_blueprint_receipt'] = receipt_path
summary['report_updated_at'] = now
summary['systems'].sort(key=lambda s: s['percent'])
save(report / 'current-summary.json', summary)
html = (report / 'index.html').read_text('utf8')
marker = '<details id="system-multiblocks"'
start = html.index('</summary>', html.index(marker)) + len('</summary>')
notice = '<section class="notice"><h3>W12 A1：作者原案方块预览待审</h3><p>' + escape(note.strip()) + '</p><p>真实搭建、GT成型、运行与原生特效保持未验收；原验收4/6、研发4/5及全库分数保持。</p><p><a href="../../' + preview_path + '">打开W12预览</a> · <a href="../../' + receipt_path + '">交付回执</a></p></section>'
html = html[:start] + notice + html[start:]
marker = '<script type="application/json" id="audit-data">'
start = html.index(marker) + len(marker)
end = html.index('</script>', start)
html = html[:start] + '\n' + json.dumps(summary, ensure_ascii=False, indent=2) + '\n' + html[end:]
(report / 'index.html').write_text(html, 'utf8')

memory = f'''\n\n## 2026-11-16 对话0005：W12作者原案方块预览A1

- 附件W12约束之律者·戒律·全域能量约束壁为本轮依据，消息中旧W08薪炎正文不作W12几何。当前独立入口`{preview_path}`，外观待审；W07继续停止。
- 完整100构件、23,672,824去重实体格、4,456,691合并表面，实际宽1063×深847×高347，源范围[0,-19,0]至[1062,327,846]；24内倾锚桩、32穿扣实体链、三重十字、12神恩矛、480约束柱、18花窗、双600格长廊、8尖塔、750名义直径天幕与320实体垂丝完整保留。9种实际方块，GT/HK占75.717%；原生像素贴图、完整NBT及分件NPZ已交付。
- 原文名义占地900361格比已批准W10少240格，规模递增待修订；600格双长廊重叠137格、含端点层数、数千柱数量冲突、主控Z10侧方向命名及塔顶托举光束矛盾均记录。原案坐标、完整厚度和越界端点保留，不自行移位删件消解。
- 唯一主控按原坐标(531,50,10)以红石块定位，导出坐标(531,69,10)；其余全部实体格自由替换合法接口、朝向自选。网页按NBT同格覆盖顺序显示以消除重叠表面闪烁；原始完整分件保存在NPZ。
- 16幅视角及评审界面渲染完成，页面错误0、请求失败0；蜂窝波、金色墙束、320像素蝴蝶与核心电弧仅网页演示。蝶粒子按高度接近下部线圈层变金消散，未做逐线圈碰撞。运行CIV、研究RN-ECB保持；未修改游戏源码资源、构建安装JAR或操作游戏、桌面、存档。原37域分数、能力分母、批准数与正式资源统计保持。回执`{receipt_path}`，记录时间`{now}`。
'''
for name in ('AGENTS.md', 'rule/当前多方块设计规则.md'):
    with (ROOT / name).open('a', encoding='utf8') as handle:
        handle.write(memory)
manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
manifest['updated_at'] = now
manifest['files'] = {str(p.relative_to(OUT)).replace('\\', '/'): dict(bytes=p.stat().st_size, sha256=digest(p))
                     for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'manifest.json'}
save(OUT / 'manifest.json', manifest)
save(LOG / 'record-update.json', dict(updated_at=now, report_backup=str(snapshot), receipt=receipt_path,
    overall_percent=summary['overall_percent'], domain_count=summary['domain_count'],
    acceptance=dict(earned=system['earned'], possible=system['possible']),
    development_metric=system['development_metric'], scores_changed=False))
print(json.dumps(dict(receipt=receipt_path, preview=preview_path, report=str(report / 'index.html'),
    blocks=receipt['blocks'], nbt_sha256=receipt['nbt']['sha256'], overall_percent=summary['overall_percent'])))
