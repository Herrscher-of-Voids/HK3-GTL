# -*- coding: utf-8 -*-
"""W02完整候选、真实材质查看器与可追溯离线证据。"""
import base64
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import w02_matrix_geometry_v1_20261107 as geometry
from build_max_structure_candidate import SHARED,page,save
from build_i25_world_bubble_observatory_20261025 import INSTANCE,resource_materials
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W02_万象自律工业矩阵_六院构造中庭_V1_20261107'
LOG=ROOT/'logs/w02-matrix-v1-20261107'


def generate():
    assert json.loads((INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']=='3.0'
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
    cube,data=geometry.build();check=geometry.audit(cube,data)
    print('几何与53个低阶比较通过：'+str(check['blocks']),flush=True)
    view=OUT/'w02';view.mkdir(exist_ok=True)
    materials,sources,packs=resource_materials(geometry.STATES)
    exported=export_dense(cube,geometry.STATES,data['name'],view)
    assert exported['block_count']==check['blocks']
    print('完整NBT/Schematic逐格回读通过',flush=True)
    groups,lengths,merged=merge_surface_runs(exported['surface_groups'],data['size'])
    check.update(readback=exported['readback'],nbt_schem_sha256=exported['hashes'],source_instance=str(INSTANCE),
        instance_version='3.0',material_resource_sources=sources,enabled_file_resource_packs=packs,
        resource_file_sha256={s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in sorted({v.split('!/',1)[0] for v in sources.values()})},
        material_complete_cube=True,resource_registration_verified=False,viewer_surface_faces=merged['original_unit_faces'],
        viewer_surface_merge=merged,viewer_rendered_quads=merged['rendered_quads'],viewer_payload_exact_cell_readback=True)
    payload=dict(data=data,palette=geometry.STATES,surfaceGroups=groups,surfaceRunLengths=lengths,
        blockCount=check['blocks'],materials=materials,audit=check,names=geometry.ROLES)
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),6)).decode()
    (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(encoded)+';',encoding='utf-8')
    viewer=(SHARED/'viewer.bundle.js').read_text(encoding='utf-8').replace('调度楼材质近景','主控材质近景').replace('偏馈碟阵与双轨整备站V1',data['title']+'V1')
    (view/'viewer.bundle.js').write_text(viewer,encoding='utf-8')
    html=page(data,check)
    substitutions={
        'MAX · ':'运行WSV · HBV构造蓝外壳 · ',
        '既定四台MAX复制系统的独立外观候选，内部需求号W02。名称与工艺尚未冻结，未批准、未实装。':
            'W02既定文明奇观的独立外观候选；保留理之律者名称，不指定尚未核准的角色实体身份。未批准、未实装。',
        '六处接口':'八处接口',
        'MAX在当前范围无更低档比较对象，不虚报递增通过率。':
            '按运行WSV比较全部53个低阶批准形态：实体数、43种普通材料、包围盒体积与高度均严格递增。实际649×493×303超过257×321×97占地下限。'}
    for old,new in substitutions.items():assert old in html;html=html.replace(old,new)
    assert 'MAX' not in html
    (view/'三维评审.html').write_text(html,encoding='utf-8')
    save(OUT/'manifest.json',dict(data,candidate_version='V1',blocks=check['blocks'],unique_materials=len(geometry.STATES),
        ordinary_materials=check['ordinary_materials'],status='candidate_waiting_user_review',approved=False,installed=False,
        game_verified=False,generated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        claim_boundary='仅既定W02建筑外观候选；WSV运行与HBV外观分列，角色身份及运行能力另验。'))
    save(OUT/'verification.json',check)
    save(LOG/'voltage-progression.json',check['voltage_progression'])
    save(OUT/'材料清单.json',[dict(state=s,count=check['palette'][s],role=geometry.ROLES[s],survival_stage_verified=False) for s in geometry.STATES])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title>
<style>body{{max-width:1280px;margin:32px auto;padding:0 22px;background:#101d2d;color:#e2effa;font:16px/1.8 system-ui}}a{{color:#8bd2ff}}img{{width:100%}}.note{{padding:18px;border-left:3px solid #66adf5;background:#20334b}}</style>
<small>HK3GTL / W02既定文明奇观 / V1 / 2026-11-07</small><h1>{data['title']}</h1>
<p class="note">运行目标WSV；律者外观主机壳HBV构造蓝。649×493×303（宽×深×高），{check['blocks']:,}实体方块，45种材料（普通43种）。待负责人审阅；未批准、未部署。</p>
<p><a href="w02/三维评审.html">打开完整三维评审</a> · <a href="verification.json">核验记录</a> · <a href="材料清单.json">材料清单</a></p>
<img src="完整预览.png" alt="六院与中央矩阵完整真实材质预览"><p>{data['description']}</p><p>{data['purpose']}</p>
<p><a href="俯视布局.png">俯视布局</a> · <a href="后侧设备.png">后侧设备</a> · <a href="主控材质近景.png">主控与接口</a> · <a href="逐层剖切.png">逐层剖切</a></p>
<p>257×321×97为既定占地下限；实际包围盒逐轴超过。按WSV运行档位与全部53个已批准低阶形态比较，实体数、普通方块种类、包围盒体积、高度四项严格递增。HBV外观颜色不降低运行档位。</p>
<p>全部实体六邻接连通；北侧主控居中，八处通用接口有背板、齐平且有五格接线净空，不限定输入输出。六条冷却联络逐格检查指定两端设备，无悬空端点。完整NBT和Schematic逐格回读一致，查看器表面合并后重展一致。</p>
<p>增强版3.0真实模型与PNG静态首帧；隐藏材质和剖切不补画切面。资源存在不代表游戏注册或生存可获取。角色实体、研究、配方、成形、运行及8GB整世界目标另验。十周年彩蛋与西瓜ARG保留；客户端实测和桌面操作继续暂停。</p></html>''',encoding='utf-8')
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for name in ['build_w02_matrix_v1_20261107.py','w02_matrix_geometry_v1_20261107.py','w02_voltage_progression_20261107.py']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    save(LOG/'package-status.json',dict(passed=True,approved=False,installed=False,game_verified=False,system_completed=False,
        blocks=check['blocks'],size_xyz=data['size'],materials=len(geometry.STATES),ordinary_materials=43,
        pipe_routes=6,open_pipe_ends=0,voltage_progression_passed=True,lower_form_count=53,hashes=exported['hashes']))
    print(json.dumps(dict(output=str(OUT),blocks=check['blocks'],quads=merged['rendered_quads']),ensure_ascii=False),flush=True)


if __name__=='__main__':generate()
