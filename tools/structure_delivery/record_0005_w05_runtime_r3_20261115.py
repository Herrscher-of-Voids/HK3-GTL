from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'src/main/resources/data/hk3gtl/structures'
DELIVERY=ROOT/'deliveries/0005_W05_R3_静态蓝图接入_20261115'
LOG=ROOT/'logs/0005-w05-r3-runtime-20261115'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'
JAR_NAME='0005多方块设计-0.5.0-W05R3-r1.jar'
now=datetime.now().astimezone().isoformat(timespec='seconds')
read=lambda path:json.loads(path.read_text('utf8'))
save=lambda path,value:path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
jar=DELIVERY/JAR_NAME
resources={'data/hk3gtl/structures/w05_candidate.bin.gz':SOURCE/'w05_candidate.bin.gz','data/hk3gtl/structures/w05_approved.json':SOURCE/'w05_approved.json'}
with zipfile.ZipFile(jar) as archive:
    names=archive.namelist()
    for name,source in resources.items():
        assert hashlib.sha256(archive.read(name)).digest()==hashlib.sha256(source.read_bytes()).digest()
    assert len(names)==len(set(names))
    classes=[name for name in names if name.endswith(('Hk3SparsePreviewData.class','Hk3CampusCatalog.class','Hk3WonderMachines.class'))]
meta=read(SOURCE/'w05_approved.json')
manifest=read(ROOT/'deliveries/0005_W05_七处穿模修订_R3_20261115/manifest.json')
receipt={'recorded_at':now,'machine':'W05','version':'R3','conversation':'0005','conversation_id':'01a1d6b8-bd81-79d3-a6f4-4f590806cc8e','status':'approved_static_blueprint_connected_candidate_jar_built_not_installed_game_unverified','approval_receipt':'logs/0005-w05-r3-runtime-20261115/approval.json','geometry':{'size_wdh':meta['size_wdh'],'blocks':meta['block_count'],'components':len(manifest['components']),'source_manifest_sha256':meta['source_manifest_sha256'],'source_npz_sha256':meta['source_npz_sha256'],'blueprint_sha256':meta['blueprint_sha256'],'runtime_metadata_sha256':hashlib.sha256(resources['data/hk3gtl/structures/w05_approved.json'].read_bytes()).hexdigest()},'controller':{'source_xyz':meta['controller_source_xyz'],'export_xyz':meta['controller_xyz'],'facing':meta['source_facing'],'id':meta['controller']},'runtime':{'target_voltage':meta['target_voltage'],'research':meta['research'],'production_recipe':meta['production_recipe'],'fixed_interfaces':meta['fixed_interface_positions'],'native_animation_integrated':False,'animation_scope':meta['animation_scope']},'build':{'result':'BUILD SUCCESSFUL','compile_log':'logs/0005-w05-r3-runtime-20261115/gradle-compile.log','remap_log':'logs/0005-w05-r3-runtime-20261115/gradle-remap.log','remapped_class_entries':classes},'jar':{'path':str(jar.relative_to(ROOT)).replace('\\','/'),'bytes':jar.stat().st_size,'sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'resources_verified_against_source':True,'base':'当前源码完整候选；仅补入跳过processResources后缺失的两项W05资源。'},'installed':False,'game_started':False,'desktop_used':False,'game_verified':False,'acceptance_score_changed':False,'tests_added':False,'tests_run':False}
save(DELIVERY/'接入回执.json',receipt)
save(LOG/'completion.json',receipt)
history=LOG/('report-before-'+datetime.now().strftime('%Y%m%d_%H%M%S'))
history.mkdir()
for path in (REPORT/'index.html',REPORT/'current-summary.json',ROOT/'AGENTS.md',ROOT/'rule/当前多方块设计规则.md'):
    target=history/path.relative_to(ROOT)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,target)
summary=read(REPORT/'current-summary.json')
system=next(item for item in summary['systems'] if item['id']=='multiblocks')
system['w05_0005_r3_runtime']=receipt
system['updated_at']=now
system['coverage']=system['coverage'].replace('W05当前采用已批准的0005 A4，完整蓝图资源叠包已安装，后续R16保留资源；本轮未实机验收，下一台W06。','W05的A4为历史运行蓝图；当前采用负责人批准的R3七处避让修订，静态完整蓝图已进入源码与0005独立候选JAR，未安装、未实机验收。主控位于(277,12,5)，朝北；动态演出仍仅网页预览。')
summary['w05_0005_r3_runtime_20261115_receipt']='logs/0005-w05-r3-runtime-20261115/completion.json'
summary['report_updated_at']=now
summary['systems']=sorted(summary['systems'],key=lambda item:item['percent'])
save(REPORT/'current-summary.json',summary)
html=(REPORT/'index.html').read_text('utf8')
html=html.replace('R3外观待评审，未改运行资源或进行游戏验收，37域分数与批准数量保持。','此处记录的是审批前预览状态；负责人随后批准R3并接入静态完整蓝图，当前构建与安装状态见本页顶部记录。',1)
section=f'<section class="notice" id="w05-r3-runtime-0005"><h2>0005 · W05 R3批准外观与静态蓝图接入</h2><p>完整555×701×321、6,646,726块蓝图已接入源码和独立候选JAR。主控为原生GT控制器，位于整机坐标(277,12,5)，朝北；WSV、RN-IFF、既有配方与自由通用接口保持。R3网页动态尚未接入游戏。</p><p>JAR内蓝图和元数据哈希均与源码一致。候选未安装，未启动游戏；成型、运行及游戏特效仍待实机验收，37域分数、分母与批准数量保持。</p><p>{now} · <a href="../../deliveries/0005_W05_R3_静态蓝图接入_20261115/{JAR_NAME}">0005独立候选JAR</a> · <a href="../../deliveries/0005_W05_七处穿模修订_R3_20261115/三维评审.html">R3三维预览</a> · <a href="../../deliveries/0005_W05_R3_静态蓝图接入_20261115/接入回执.json">接入回执</a></p></section>'
html=html.replace('<body>','<body>'+section,1)
embedded=json.dumps(summary,ensure_ascii=False,indent=2).replace('<','\\u003c')
html,count=re.subn(r'(<script type="application/json" id="audit-data">).*?(</script>)',lambda match:match[1]+'\n'+embedded+'\n'+match[2],html,count=1,flags=re.S)
assert count==1
(REPORT/'index.html').write_text(html,'utf8')
note=f'\n\n## 2026-11-15 对话0005：W05 R3批准与静态完整蓝图接入\n\n- 负责人原话：“可以就这台吧，接入吧，你主控打算放哪里”。W05 R3七处避让修订已获外观批准，完整静态蓝图进入源码与独立候选JAR `deliveries/0005_W05_R3_静态蓝图接入_20261115/{JAR_NAME}`；接入回执 `{LOG}/completion.json`。A4批准及旧安装记录保留历史，不覆盖其他对话候选。\n- 整机555×701×321格、6,646,726块、73构件；唯一原生GT主控在蓝图坐标(0,12,-345)，归一化整机坐标(277,12,5)，位于前方中线并朝北。保留WSV、RN-IFF、既有正式配方及自由通用接口。\n- 两项W05资源已逐哈希核对候选JAR与源码一致。仅接入静态方块蓝图；叶轮、陀螺与流场动画仍为网页演示。候选未安装，未启动游戏或操作存档；成型、运行和特效未实机验收，评分及分母保持。\n'
for path in (ROOT/'AGENTS.md',ROOT/'rule/当前多方块设计规则.md'):
    path.write_text(path.read_text('utf8')+note,'utf8')
save(LOG/'publication.json',{'recorded_at':now,'fixed_report':str(REPORT/'index.html'),'report_backup':str(history),'overall_percent':summary['overall_percent'],'domain_count':summary['domain_count'],'scores_changed':False,'approval_count_changed':False,'system_order':[item['id'] for item in summary['systems']]})
print(json.dumps({'jar':receipt['jar'],'controller':receipt['controller'],'report_backup':str(history)},ensure_ascii=False))
