# -*- coding: utf-8 -*-
"""导出W02递归构造环V2；沿用完整体素、真实资源和无损表面预览流程。"""
import base64
from datetime import datetime,timezone,timedelta
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import w02_matrix_geometry_v2_20261107 as geometry
from build_max_structure_candidate import SHARED,page,save
from build_i25_world_bubble_observatory_20261025 import INSTANCE,resource_materials
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W02_万象自律工业矩阵_递归构造环_V2_20261107'
LOG=ROOT/'logs/w02-matrix-v2-20261107'


def decorate():
    view=OUT/'w02';target=view/'三维评审.html'
    text=target.read_text(encoding='utf8')
    if 'recursiveView' not in text:
        text=text.replace('<div id="viewName">','<p><button id="recursiveView">查看递归内腔</button><button id="completeView">还原完整外观</button></p><div id="viewName">',1)
        text=text.replace('<script src="viewer.bundle.js"></script>','<script src="viewer.bundle.js"></script><script src="w02-review.js"></script>',1)
        target.write_text(text,encoding='utf8')
    source=ROOT/'tools/structure_delivery/w02_recursive_review_v2_20261107.js'
    shutil.copy2(source,view/'w02-review.js');shutil.copy2(source,OUT/'生成脚本'/source.name)
    shutil.copy2(Path(__file__),OUT/'生成脚本'/Path(__file__).name)
    target=OUT/'index.html';text=target.read_text(encoding='utf8')
    if '递归内腔.png' not in text:
        text=text.replace('<p>实际边界','<p><a href="递归内腔.png">查看真实递归内腔</a>（隐藏HBV主体与玻璃；不补画剖切面）。</p><p>实际边界',1)
        target.write_text(text,encoding='utf8')


def generate():
    assert json.loads((INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf8'))['versionId']=='3.0'
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
    cube,data=geometry.build();check=geometry.audit(cube,data)
    print('几何、六院递归与53个低阶比较通过：'+str(check['blocks']),flush=True)
    view=OUT/'w02';view.mkdir(exist_ok=True)
    materials,sources,packs=resource_materials(geometry.STATES)
    exported=export_dense(cube,geometry.STATES,data['name'],view)
    assert exported['block_count']==check['blocks']
    print('完整NBT与Schematic逐格回读通过',flush=True)
    groups,lengths,merged=merge_surface_runs(exported['surface_groups'],data['size'])
    check.update(readback=exported['readback'],nbt_schem_sha256=exported['hashes'],source_instance=str(INSTANCE),
        instance_version='3.0',material_resource_sources=sources,enabled_file_resource_packs=packs,
        resource_file_sha256={s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in sorted({v.split('!/',1)[0] for v in sources.values()})},
        material_complete_cube=True,resource_registration_verified=False,viewer_surface_faces=merged['original_unit_faces'],
        viewer_surface_merge=merged,viewer_rendered_quads=merged['rendered_quads'],viewer_payload_exact_cell_readback=True)
    payload=dict(data=data,palette=geometry.STATES,surfaceGroups=groups,surfaceRunLengths=lengths,
        blockCount=check['blocks'],materials=materials,audit=check,names=geometry.ROLES)
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf8'),6)).decode()
    (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(encoded)+';',encoding='utf8')
    viewer=(SHARED/'viewer.bundle.js').read_text(encoding='utf8').replace('调度楼材质近景','主控材质近景').replace('偏馈碟阵与双轨整备站V1',data['title']+'V2')
    (view/'viewer.bundle.js').write_text(viewer,encoding='utf8')
    html=page(data,check).replace(' V1',' V2')
    substitutions={
        'MAX · ':'运行WSV · HBV构造蓝外壳 · ',
        '既定四台MAX复制系统的独立外观候选，内部需求号W02。名称与工艺尚未冻结，未批准、未实装。':
            'W02递归构造环V2；保留理之律者与中央矩阵统合六院的职责。V1历史保留，本版未批准、未实装。',
        '六处接口':'八处接口',
        'MAX在当前范围无更低档比较对象，不虚报递增通过率。':
            '运行WSV，外观HBV。与全部53个已批准低阶形态比较，实体数、43种普通材料、包围盒体积与高度四项严格递增。'}
    for old,new in substitutions.items():assert old in html;html=html.replace(old,new)
    assert 'MAX' not in html
    (view/'三维评审.html').write_text(html,encoding='utf8')
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    save(OUT/'manifest.json',dict(data,candidate_version='V2',blocks=check['blocks'],unique_materials=len(geometry.STATES),
        ordinary_materials=check['ordinary_materials'],status='candidate_waiting_user_review',approved=False,installed=False,
        game_verified=False,generated_at=now,claim_boundary='仅W02建筑外观候选；不改变研究、配方、角色身份或毕业条件。'))
    save(OUT/'verification.json',check);save(LOG/'voltage-progression.json',check['voltage_progression'])
    save(OUT/'材料清单.json',[dict(state=s,count=check['palette'][s],role=geometry.ROLES[s],survival_stage_verified=False) for s in geometry.STATES])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']} V2</title>
<style>body{{max-width:1440px;margin:32px auto;padding:0 22px;background:#101d2d;color:#e2effa;font:16px/1.8 system-ui}}a{{color:#8bd2ff}}img{{width:100%;display:block}}.note{{padding:18px;border-left:3px solid #66adf5;background:#20334b}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}@media(max-width:800px){{.grid{{display:block}}}}</style>
<small>HK3GTL / W02既定文明奇观 / V2 / {now}</small><h1>{data['title']}</h1>
<p class="note">运行目标WSV；律者外观主机壳HBV构造蓝。649×493×303（宽×深×高），{check['blocks']:,}实体方块，45种材料（普通43种）。待审，未批准、未部署。</p>
<p><a href="w02/三维评审.html">打开完整三维评审</a> · <a href="verification.json">核验记录</a> · <a href="材料清单.json">材料清单</a> · <a href="../W02_万象自律工业矩阵_六院构造中庭_V1_20261107/index.html">V1历史对照</a></p>
<img src="完整预览.png" alt="不对称递归构造环完整真实材质预览"><p>{data['description']}</p><p>{data['purpose']}</p>
<div class="grid"><figure><img src="俯视布局.png" alt="中央意识与六院递归布局"><figcaption>中央意识＋六院；三处投影锚座承接主环。</figcaption></figure><figure><img src="后侧设备.png" alt="主环后侧与高位奇点"><figcaption>扭转脊线、不同口径喉口和高位信息锚点。</figcaption></figure><figure><img src="逐层剖切.png" alt="递归装配环与实际内部结构"><figcaption>实际表面剖切；查看器不补画剖切面。</figcaption></figure><figure><img src="主控材质近景.png" alt="中央意识舱主控与通用接口"><figcaption>主控在宽度中线；八个通用仓位不限制输入输出。</figcaption></figure></div>
<p>实际边界超过257×321×97下限；按WSV比较全部53个批准低阶形态，四项规模指标严格递增。HBV是最大单一材料。完整NBT和Schematic逐格回读一致；查看器表面合并后重展一致，沿用增强版3.0真实模型与贴图静态首帧。</p>
<p>六院各有三重微型环和发光核心。高位舱通过玻璃信息束连接，整体六邻接连通；“悬浮”“全息”“非欧”是造型叙事。六条桥内冷却联络检查指定两端设备；主控和接口有背板、齐平并保留五格接线净空。</p>
<p>本版不以成型直接发奖，不改变毕业条件；未接入正式Pattern，未进行游戏成型、仓室兼容、配方、生存获取或8GB全建筑运行验收。资源存在不代表游戏注册。批准56／正式52、74项范围和batch-11的4/5均保留；十周年预案及西瓜ARG原案不改。</p></html>''',encoding='utf8')
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for name in ['build_w02_matrix_v2_20261107.py','w02_matrix_geometry_v2_20261107.py','w02_matrix_geometry_v1_20261107.py','w02_voltage_progression_20261107.py']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    save(LOG/'package-status.json',dict(passed=True,approved=False,installed=False,game_verified=False,system_completed=False,
        blocks=check['blocks'],size_xyz=data['size'],materials=len(geometry.STATES),ordinary_materials=43,
        pipe_routes=6,open_pipe_ends=0,voltage_progression_passed=True,lower_form_count=53,hashes=exported['hashes']))
    decorate()
    print(json.dumps(dict(output=str(OUT),blocks=check['blocks'],quads=merged['rendered_quads']),ensure_ascii=False),flush=True)


if __name__=='__main__':generate()
