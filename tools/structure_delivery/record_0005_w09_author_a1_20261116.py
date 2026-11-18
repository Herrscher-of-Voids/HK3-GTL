from datetime import datetime
import json
from pathlib import Path
import shutil

from package_0005_w09_author_blueprint_20261116 import digest, save


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_作者蓝图原案_A1_20261116'
LOG = ROOT / 'logs/0005-w09-author-blueprint-a1-20261116'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
now = datetime.now().astimezone().isoformat()
geometry = json.loads((OUT / 'geometry.json').read_text('utf8'))
capture = json.loads((OUT / 'preview-capture.json').read_text('utf8'))
preview_path = (OUT / 'index.html').relative_to(ROOT).as_posix()
receipt_path = (LOG / 'completion.json').relative_to(ROOT).as_posix()
comparison = []
for machine, directory in [('W08', '0005_W08_双内环球面翻转_A5_20261116'),
                           ('W10', '0005_W10_引力奇点刑架_净空修订_A3_20261116'),
                           ('W12', '0005_W12_三环翻转_A3_20261116')]:
    source = ROOT / 'deliveries' / directory / 'geometry.json'
    prior = json.loads(source.read_text('utf8'))
    w, d, h = prior['actual_size_wdh']
    metrics = dict(footprint_area=w*d, bounding_box_volume=w*d*h, actual_height=h, blocks=prior['blocks'])
    comparison.append(dict(machine=machine, voltage='CIV', source=source.relative_to(ROOT).as_posix(),
        metrics=metrics, w09_minus_baseline={key: geometry[key] - value for key, value in metrics.items()}))
receipt = dict(machine='W09', candidate='A1', updated_at=now, conversation='0005',
    conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
    status='作者蓝图完整方块预览待审', preview=preview_path,
    source=geometry['source'], actual_size_wdh=geometry['actual_size_wdh'],
    blocks=geometry['blocks'], components=len(geometry['components']),
    surface_quads=geometry['surface_quads'], unique_block_types=geometry['unique_block_types'],
    non_vanilla_percent=geometry['non_vanilla_percent'], runtime_voltage='CEV', research='RN-CKV',
    controller_blueprint=[487,160,260], controller_marker='minecraft:redstone_block',
    interface_rule=geometry['interface_rule'],
    visual_review=dict(screenshots=len(capture['views'])+1, errors=capture['errors'], failed_requests=capture['failed'],
        inspected=['整体前后斜视、正侧俯视', '千羽万象零秒与工作态', '八面体与黑球',
                   '三兵与蜂窝发射井', '机械山、飞瀑与剑亭', '折扇与御座', '交扣链', '拜仙台及真实像素近景']),
    remaining_geometry=[
        '三羽环同半径转动互穿，零秒羽环与八面体存在2格重合。',
        '19号锁链穿过拜仙台111格并与神道重合113格；后匣与3号剑亭重合1806格。链路、机械山位置与垂度包含本稿取样。',
        '18×11链环与7×7截面存在原文尺寸矛盾，本稿取约3×3杆体保留交扣孔。',
        '原文名义975×1025×317与包含端点的X0..975/Z0..1025/Y0..317分别记录，实际976×1026×318。',
        'CEV的W09当前高度低于CIV的W08/W10/W12；体积与方块数低于CIV的W10，方块数低于CIV的W12。规模递增待修订；本轮保留原文坐标完整预览。'],
    lower_voltage_comparison=dict(status='已查三台CIV既有候选，完整低电压对照待后续设计', comparisons=comparison),
    nbt=dict(path=(OUT/'W09-文明共识矩阵-A1.nbt').relative_to(ROOT).as_posix(),
        sha256=digest(OUT/'W09-文明共识矩阵-A1.nbt'), static_pose='零秒参考姿态，同格后写优先'),
    appearance_approved=False, formal_blueprint_connected=False, game_code_modified=False,
    jar_built=False, installed=False, desktop_used=False, game_verified=False,
    scores_changed=False, approval_counts_changed=False)
for directory in (OUT, LOG):
    save(directory/'completion.json', receipt)
backup = REPORT / ('history/before-0005-w09-author-a1-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
for name in ('index.html','current-summary.json'):
    shutil.copy2(REPORT/name, backup/name)
summary = json.loads((REPORT/'current-summary.json').read_text('utf8'))
system = next(s for s in summary['systems'] if s['id']=='multiblocks')
system.update(w09_0005_author_blueprint_a1=receipt, w09_current_design_stage=receipt['status'],
    w09_current_design_candidate=preview_path, updated_at=now)
summary['w09_0005_author_blueprint_receipt']=receipt_path
summary['report_updated_at']=now
summary['systems'].sort(key=lambda s:s['percent'])
save(REPORT/'current-summary.json',summary)
html=(REPORT/'index.html').read_text('utf8')
start=html.index('</summary>',html.index('<details id="system-multiblocks"'))+len('</summary>')
notice=f'<section class="notice"><h3>W09 A1：文明共识矩阵完整方块稿</h3><p>实际976×1026×318，{geometry["blocks"]:,}实体格、147构件、14种方块。八峰、三兵、32条链、三羽环与折扇完整生成。主控(487,160,260)，其余实体格自由替换合法接口。三环、链路、拜仙台等交叠及CEV规模递增待修订；外观待审，原分数与批准数保持。</p><p><a href="../../{preview_path}">打开W09预览</a></p></section>'
html=html[:start]+notice+html[start:]
marker='<script type="application/json" id="audit-data">'
start=html.index(marker)+len(marker)
end=html.index('</script>',start)
html=html[:start]+'\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n'+html[end:]
(REPORT/'index.html').write_text(html,'utf8')
memory=f'''

## 2026-11-16 对话0005：W09作者蓝图完整方块预览A1

- 负责人提供《W09 识之律者·万象·文明共识矩阵 巨构工程蓝图.md》，据此生成独立A1预览`{preview_path}`。W07继续停止；W09外观待审，注册身份沿用`w09_civilization_consensus_matrix`、CEV、RN-CKV。
- 原文名义975×1025×317，包含端点坐标完整生成后实际976×1026×318，占地1,001,376格、包围盒318,437,568格，{geometry['blocks']:,}去重实体格、147构件、14种方块，GT/HK实体占{geometry['non_vanilla_percent']:.6f}%。八峰、16飞瀑、八亭、三兵、32条661环实体链、三环120羽刃、红玻璃八面体、黑球、十八骨折扇及御座均保留。
- 唯一主控预览定位(487,160,260)，Y159为拜仙台踏面；其余全部实体格可替换合法通用接口、朝向自选。墨海Y5与黑球使用纯黑混凝土，白金飞瀑使用白瓷主体、金边。八面体表面汉字以楷体18×18像素拼块，原文未提供古篆笔形；120道羽刃电弧随对应羽环转动，另含金红莫比乌斯、墨波、漂浮汉字与剑枪脉冲等网页特效。
- 三道180格羽环同半径转动互穿；零秒与八面体另重合2格。19号链穿拜仙台111格及神道113格，后匣与3号剑亭重合1806格；链路和机械山位置含本稿挂点、垂度及方位取样。原文18×11链环与7×7截面矛盾，本稿约3×3杆体及完整参数均明记。交叠记录按后写归属统计，原始NPZ保留独立构件。
- CEV的W09高318格，低于既有CIV的W08/W10/W12；体积及实体数低于W10、实体数低于W12，规模递增待修订。原文核心字典Y/Z交换及前段Z150与主控Z260差异照实留档，本轮不裁切或私改原文确定坐标。
- 18幅界面与视角已保存，页面错误{len(capture['errors'])}、资源失败{len(capture['failed'])}。回执`{receipt_path}`，时间`{now}`。本轮生成完整NBT及网页候选，正式蓝图接入、JAR构建、安装和游戏验收状态未更新，原评分、分母及批准数保持。
'''
for name in ('AGENTS.md','rule/当前多方块设计规则.md'):
    with (ROOT/name).open('a',encoding='utf8') as handle:
        handle.write(memory)
for name in ('record_0005_w09_author_a1_20261116.py','prepare_0005_w09_viewer_20261116.py',
             'capture_0005_w09_author_blueprint_20261116.mjs','w09_effects_20261116.mjs'):
    shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
save(OUT/'manifest.json',dict(machine='W09',candidate='A1',updated_at=now,status=receipt['status'],
    files={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=digest(p))
           for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'}))
save(LOG/'record-update.json',dict(updated_at=now,report_backup=str(backup),scores_changed=False,
    approval_counts_changed=False,overall_percent=summary['overall_percent']))
print(json.dumps(dict(preview=preview_path,overall_percent=summary['overall_percent']),ensure_ascii=False))
