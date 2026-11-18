from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil


ROOT=Path(__file__).resolve().parents[2]
DELIVERY='deliveries/0005_W05_作者蓝图原案_20261115'
LOG='logs/0005-w05-author-blueprint-20261115'
out,log=ROOT/DELIVERY,ROOT/LOG
now=datetime.now().astimezone().isoformat(timespec='seconds')
manifest=json.loads((out/'manifest.json').read_text('utf8'))
capture=json.loads((log/'preview-capture.json').read_text('utf8'))
receipt=dict(recorded_at=now,machine='W05',conversation='0005',conversation_id=manifest['conversation_id'],
    title=manifest['title'],status='author_blueprint_preview_only_unapproved',source=manifest['source'],
    preview=DELIVERY+'/index.html',interactive_preview=DELIVERY+'/三维评审.html',manifest=DELIVERY+'/manifest.json',
    completion_receipt=LOG+'/completion.json',nominal_size_wdh=[555,700,320],size_wdh=manifest['size_wdh'],
    bounds_xyz=manifest['occupied_bounds_xyz'],components=len(manifest['components']),materials=7,
    component_voxels=manifest['source_component_voxels'],unique_occupied_voxels=manifest['unique_occupied_voxels'],
    source_frozen=True,source_frozen_sha256=hashlib.sha256((out/'作者原文.md').read_bytes()).hexdigest(),
    coordinates_preserved=True,original_conflicts_preserved=True,undefined_parameters_recorded=True,
    overlap_record=DELIVERY+'/构件重合记录.json',overlap_extra_memberships=manifest['overlap_extra_memberships'],
    overlap_scope='构件原坐标首占统计，包含连接重合；没有宣称零穿模或动态扫掠验证。',
    original_geometry_archive=DELIVERY+'/原始构件数据.npz',rendered_surface_quads=manifest['preview']['merged_quads'],
    preview_modes=['待机','MAX+满载工作'],effects_scope='仅网页渲染，未实现游戏BER。',
    screenshots=len(capture['screenshots']),capture_transport=capture['transport'],browser_errors=capture['errors'],failed_requests=capture['failed'],
    visually_reviewed=['整体预览.png','俯视预览.png','背面预览.png','核心近景.png','双翼管网近景.png','评审界面.png','移动端评审.png'],
    appearance_approved=False,existing_w05_a4_replaced=False,game_code_modified=False,jar_built=False,installed=False,
    desktop_used=False,game_started=False,game_verified=False,automated_tests_run=False,acceptance_score_changed=False)


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


save(log/'completion.json',receipt)
entry=f'''

## 2026-11-15 对话0005：W05作者蓝图原案独立预览

- 负责人要求“完整按照文档里的说法去制作预览，不要有任何改动”。原样冻结《W05 · 风之律者 · 长风·理想流体环流阵 - 巨构工程设计蓝图.md》，SHA256 `{receipt['source_frozen_sha256']}`；本次只制作作者原案独立预览，不覆盖已批准、接入的温蒂风翼A4。
- 名义555×700×320，原坐标X[-277,277]、Z[-350,350]、Y[0,320]整数格含端点为555×701×321；保留约480×680八角阶梯基座、主控(0,12,-345)、三涡轮、八轨、直径50多面核心及双陀螺、十二片200轴向跨度尾瓣、十二空心翼梁、六座直径90贯通副塔、两侧200格高内向弧刃及260/180/100三倾斜王冠。85独立构件，7,111,995构件内方块，6,999,761唯一占格。
- 原文底座高度40/45、口径越出分区、端点计数及尾瓣长度等冲突原样记录；曲线控制点、塔中心、王冠倾角等原文未给参数明确列为预览取样，不冒充原作者逐格数据。各构件独立保存，112,234额外占格归属含正常连接重合，未通过移位、删件或裁切处理，不宣称零穿模。
- 七种专用64×64材质仅用于网页；待机涡轮反转、核心微浮及陀螺自转，工作光流沿双翼管网一周后至尾喷、白色风眼、三透明气旋及王冠风柱均为网页演示，不宣称游戏方块、CTM或BER已实现。15张headless截图完成，最终页面错误及请求失败均0，支持本地文件直接打开。
- 预览：`{DELIVERY}/三维评审.html`；原文、取样、构件重合及原始整数格数据均随附。回执：`{LOG}/completion.json`。外观待评审，未改游戏代码、构建或安装JAR、操作桌面/游戏/实例/存档；未新增或运行测试，未增加批准数量、验收分数或37域总分。
'''
for path in [ROOT/'AGENTS.md',ROOT/'rule/当前多方块设计规则.md']:
    with path.open('a',encoding='utf8',newline='') as f:
        f.write(entry)

audit=ROOT/'logs/beta5-completion-audit-20261030'
history=log/'audit-before-update';history.mkdir(exist_ok=True)
for name in ['index.html','current-summary.json']:
    shutil.copy2(audit/name,history/name)
summary=json.loads((audit/'current-summary.json').read_text('utf8'))
system=next(s for s in summary['systems'] if s['id']=='multiblocks')
system['w05_0005_author_blueprint_preview']=receipt
summary['w05_author_blueprint_0005_20261115_receipt']=LOG+'/completion.json'
summary['report_updated_at']=now
summary['systems']=sorted(summary['systems'],key=lambda s:s['percent'])
save(audit/'current-summary.json',summary)
html=(audit/'index.html').read_text('utf8')
section=f'''<section class="notice" id="w05-author-blueprint-0005"><h2>0005 · W05作者蓝图原案预览</h2><p>按负责人附件保留名义555×700×320、原坐标与全部指定构件；85独立构件、7种专用预览材质，整数格含端点555×701×321。原文冲突与未给参数公开，不通过移位、删件或裁切处理重合。</p><p>待机／满载网页动态与15张截图已交付，最终页面错误0。仅为独立预览；未替换已批准A4，未改游戏代码、构建或安装JAR、运行游戏。37域评分与分母保持。</p><p>{now} · <a href="../../{DELIVERY}/index.html">作者原案预览</a> · <a href="../0005-w05-author-blueprint-20261115/completion.json">本轮回执</a></p></section>'''
html=html.replace('<body>','<body>'+section,1)
embedded=json.dumps(summary,ensure_ascii=False,indent=2).replace('<','\\u003c')
html=re.sub(r'(<script type="application/json" id="audit-data">).*?(</script>)',lambda m:m[1]+'\n'+embedded+'\n'+m[2],html,count=1,flags=re.S)
(audit/'index.html').write_text(html,'utf8')
save(log/'publication.json',dict(recorded_at=now,receipt=LOG+'/completion.json',fixed_report=str(audit/'index.html'),
    baseline_snapshot=str(history),overall_percent=summary['overall_percent'],domain_count=summary['domain_count'],scores_changed=False))
shutil.copy2(Path(__file__),out/'生成脚本'/Path(__file__).name)
print(json.dumps(dict(receipt=LOG+'/completion.json',overall_percent=summary['overall_percent'],screenshots=receipt['screenshots']),ensure_ascii=False))
