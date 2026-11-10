# -*- coding: utf-8 -*-
"""保留旧候选与全部系统原分，同步C2离线外观证据。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile
from max_structure_review import publisher

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W03_C方案_正圆与净空_C2_20261108'
LOG=ROOT/'logs/w03-clearance-c2-20261108'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'

def load(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')

def main():
    manifest=load(OUT/'manifest.json');verification=load(OUT/'verification.json');qa=load(LOG/'viewer-qa.json')
    assert verification['passed'] and qa['passed'] and qa['info']['intersections']==0
    clearance=manifest['clearance'];assert not clearance['after']
    assert manifest['rings'][0]['radius_x']==manifest['rings'][0]['radius_y']==210
    before_actual=sum(p['overlap_cells']>0 for p in clearance['before'])
    for name in ['build_w03_clearance_c2_20261108.py','w03_clearance_c2_20261108.py','capture_w03_clearance_c2_20261108.mjs']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    save(OUT/'构件净空核验.json',clearance)
    index=OUT/'index.html';text=index.read_text('utf8')
    text=text.replace('<p>本版为立式420格正圆', '<p><a href="W03-C2-完整预览与结构.zip">下载完整离线预览、NBT与Schematic</a> · <a href="构件净空核验.json">91个构件的净空明细</a></p><p>本版为立式420格正圆',1)
    text=text.replace('</html>','<h2>上一版 C1</h2><img src="上一版C1.png" alt="历史C1；本轮未覆盖原件"><p>体素检查覆盖本座C2。其他建筑尚未逐台完成同类复查；静态无重叠不等于游戏成型和性能验收。</p></html>')
    index.write_text(text,'utf8')
    archive=OUT/'W03-C2-完整预览与结构.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file() and p!=archive:z.write(p,p.relative_to(OUT).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    # 旧版的导出哈希是已保存的历史依据，本轮不能拿新C2当作旧版基线。
    prior_folder=ROOT/'deliveries/W03_C方案_亚空之矛优化_C1_20261108'
    prior_verification=load(prior_folder/'verification.json');prior_manifest=load(prior_folder/'manifest.json')
    for suffix,key in [('nbt','nbt'),('schem','schem')]:
        assert sha(prior_folder/'w03'/(prior_manifest['name']+'.'+suffix))==prior_verification['nbt_schem_sha256'][key]
    baseline=LOG/'before-report';baseline.mkdir(exist_ok=False)
    original={p:p.read_bytes() for p in [REPORT/'index.html',REPORT/'current-summary.json']}
    for p,value in original.items():(baseline/p.name).write_bytes(value)
    old=load(REPORT/'current-summary.json');data=deepcopy(old)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat()
    state=f'2026-11-08 · W03 C2：按负责人红圈反馈修正独立构件相交；C1检出{before_actual}对实际重叠，C2为零。外主环改为中心线直径420格立式正圆，装甲外径447×447；完整模型852×566×636格、7,179,802块、15种材料。七视角、完整NBT／Schematic回读与91构件净空核验通过；636格高超出普通主世界建高，仍为离线候选，未批准、未部署。'
    work=data['current_work'];work['design_candidate_history'].append(deepcopy(work['design_candidate']))
    work['state']=state;work['next_turn']='审阅C2正圆、构件净空和立式整体比例；普通主世界建高适配与其他建筑逐台检查未完成。'
    work['design_candidate']=dict(id='W03',version='C2',title=manifest['title'],status='candidate_waiting_user_review',
        approved=False,installed=False,game_verified=False,base_selected='C / Gemini V4完整边界版 → C1',
        size_xyz=manifest['size'],blocks=manifest['blocks'],materials=manifest['unique_materials'],
        preview=str((OUT/'index.html').relative_to(ROOT)).replace('\\','/'),receipt=str((OUT/'verification.json').relative_to(ROOT)).replace('\\','/'),
        archive=str(archive.relative_to(ROOT)).replace('\\','/'),archive_sha256=sha(archive),no_nominal_clipping=True,
        blueprint_bounds_xyz=manifest['blueprint_bounds_xyz'],blueprint_to_export_offset_xyz=manifest['blueprint_to_export_offset_xyz'],
        original_overlap_pairs=before_actual,independent_overlap_pairs=0,minimum_voxel_center_distance=8,ring_centerline_diameter=420,
        ring_armour_diameters=[447,447],standard_overworld_build_height_exceeded=True,updated_at=now)
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['systems']==old['systems'] and data['overall_percent']==old['overall_percent']
    assert data['multiblock_scope']==old['multiblock_scope'] and work['hyperion_performance']==old['current_work']['hyperion_performance']
    html=original[REPORT/'index.html'].decode('utf8')
    html,n=re.subn(r'<p>更新 [^<]+ · r218 休伯利安施工与成型修复</p>','<p>更新 '+escape(now)+' · W03 C2正圆与构件净空</p>',html,count=1);assert n==1
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in html
    html=html.replace(anchor,anchor+'<p class="notice" id="w03-c2-current">'+escape(state)+' <a href="../../deliveries/W03_C方案_正圆与净空_C2_20261108/index.html">C2交付与预览</a></p>',1)
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in data['systems']]
    publisher().publish_transaction({REPORT/'index.html':html,REPORT/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n'},original)
    rule=ROOT/'rule/当前多方块设计规则.md';backup=LOG/'rule-before-c2.backup';assert not backup.exists();shutil.copy2(rule,backup)
    note='''

## 2026-11-08 W03 C2正圆与独立构件净空

- 负责人以C1红圈指出多处穿模，并要求最外主环改为正圆。本轮明确授权C2调整相交关系；旧原案保留冲突的规则不禁止本次修订，C1与旧C原件继续保留。
- C2保留六柄C1黑白橙亚空之矛、十片曲翼、双飘带、24颗晶体和24枚浮游柱；调整六矛锥形朝向、翼刃纵深层次、飘带与晶体位置，外主环为中心线420格立式正圆，装甲横竖外径均447格。
- 91个独立构件按完整体素核验，普通独立组件至少8格体素中心距离；基座承重接合与核心内部接合单独声明。禁止用覆盖、删掉相交半件或仅调整镜头冒充几何修复。其他建筑尚未逐台复查，不宣称全库已无穿模。
- 实际852×566×636格，7,179,802实体方块、15种材料；不按名义673×529×321裁切。高度超过普通主世界384格建高，当前仅离线外观候选，未接入高建限维度、未批准、未部署，不因此改变运行或毕业条件。
- 固定审计保留全部36系统原分、既定74项、批准57／正式52与r218休伯利安证据。入口：deliveries/W03_C方案_正圆与净空_C2_20261108/index.html。
'''
    rule.write_bytes(rule.read_bytes()+note.encode('utf8'))
    result=dict(passed=True,systems_unchanged=36,overall_percent=data['overall_percent'],ascending_order=True,
        C1_exports_unchanged=True,hyperion_r218_preserved=True,scope_unchanged=True,archive_sha256=sha(archive),
        audit_html_sha256=sha(REPORT/'index.html'),audit_summary_sha256=sha(REPORT/'current-summary.json'),rule_before_sha256=sha(backup),rule_after_sha256=sha(rule))
    save(LOG/'publication-verification.json',result);print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
