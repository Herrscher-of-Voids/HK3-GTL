# -*- coding: utf-8 -*-
"""复用完整结构导出器和真实材质查看器，生成MAX独立外观候选。"""
import base64
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil

from build_i25_world_bubble_observatory_20261025 import INSTANCE,resource_materials
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT=Path(__file__).resolve().parents[2]
SHARED=ROOT/'deliveries/I39_无人跨界航路中继站_偏馈碟阵与双轨整备站_V1_20261027/i39'


def save(p,data):
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def page(data,check):
    w,h,d=data['size'];p=data['controller'];key=data['key'];count=check['unique_materials']
    css=re.search(r'<style>([\s\S]*?)</style>',(SHARED/'三维评审.html').read_text(encoding='utf-8'))[1]
    buttons=''.join(f'<button data-view="{key}">{name}</button>' for key,name in [('front','前左全景'),('right','前右全景'),('back','后侧'),('top','俯视'),('inside','逐层剖切'),('orthofront','正前'),('orthoside','正侧'),('texture','材质近景')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']} V1</title><style>{css}</style>
<header><a href="../index.html">← 候选总览</a><h1>{data['title']}</h1><div>MAX · {w}×{d}×{h}（宽×深×高） · {check['blocks']:,}实体方块 · {count}种材料 · 待审</div></header>
<main class="review"><section id="stage" aria-label="完整真实材质三维预览"><div id="loading">加载真实材质与完整表面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">既定四台MAX复制系统的独立外观候选，内部需求号{key.upper()}。名称与工艺尚未冻结，未批准、未实装。</div>
<div class="locator"><b>主控蓝图 {p}</b><p>北向，整宽第{p[0]+1}格；钻石块占位。六处接口全部通用，不固定输入输出。</p><button data-view="controller">定位主控</button></div>
<div>{buttons}</div><p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">{h-1}</b><input id="layer" type="range" min="0" max="{h-1}" value="{h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>设备分区与职责</summary><p>{data['description']}</p><p>{data['purpose']}</p></details>
<details open><summary>主控与通用接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>文件与验收边界</summary><a href="{data['name']}.nbt">完整NBT</a> · <a href="{data['name']}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>增强版3.0真实资源静态首帧，完整结构文件逐格回读一致，合并表面重展一致。隐藏材质或剖切不补画内部切面。各路管道均核对指定两端设备；这不代表流体运行能力。未批准、未接入正式Pattern、未部署；注册、生存获取、成型与运行另验。MAX在当前范围无更低档比较对象，不虚报递增通过率。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''


def generate(geometry,out,log,entry_script):
    assert json.loads((INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']=='3.0'
    out.mkdir(exist_ok=True,parents=True);log.mkdir(exist_ok=True,parents=True)
    cube,data=geometry.build();check=geometry.audit(cube,data)
    view=out/data['key'];view.mkdir(exist_ok=True)
    materials,sources,packs=resource_materials(geometry.STATES)
    exported=export_dense(cube,geometry.STATES,data['name'],view)
    assert exported['block_count']==check['blocks']
    groups,lengths,merged=merge_surface_runs(exported['surface_groups'],data['size'])
    source_files=sorted({s.split('!/',1)[0] for s in sources.values()})
    check.update(readback=exported['readback'],nbt_schem_sha256=exported['hashes'],
        source_instance=str(INSTANCE),instance_version='3.0',material_resource_sources=sources,
        resource_file_sha256={s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in source_files},
        enabled_file_resource_packs=packs,material_complete_cube=True,resource_registration_verified=False,
        viewer_surface_faces=merged['original_unit_faces'],viewer_surface_merge=merged,
        viewer_rendered_quads=merged['rendered_quads'],viewer_payload_exact_cell_readback=True)
    payload=dict(data=data,palette=geometry.STATES,surfaceGroups=groups,surfaceRunLengths=lengths,
        blockCount=check['blocks'],materials=materials,audit=check,names=geometry.ROLES)
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),6)).decode()
    (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(encoded)+';',encoding='utf-8')
    source=(SHARED/'viewer.bundle.js').read_text(encoding='utf-8').replace('调度楼材质近景','主控舱材质近景').replace('偏馈碟阵与双轨整备站V1',data['title']+'V1')
    (view/'viewer.bundle.js').write_text(source,encoding='utf-8')
    (view/'三维评审.html').write_text(page(data,check),encoding='utf-8')
    save(out/'manifest.json',dict(data,target_voltage='MAX',candidate_version='V1',blocks=check['blocks'],
        unique_materials=check['unique_materials'],status='candidate_waiting_user_review',approved=False,
        installed=False,game_verified=False,generated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        claim_boundary='仅建筑外观候选；内部需求号、暂名、静态模型不代表机器注册或工艺运行。'))
    save(out/'verification.json',check)
    save(out/'材料清单.json',[dict(state=s,count=check['palette'][s],role=geometry.ROLES[s],survival_stage_verified=False) for s in geometry.STATES])
    w,h,d=data['size']
    (out/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title>
<style>body{{max-width:1280px;margin:32px auto;padding:0 22px;background:#111c29;color:#e5edf3;font:16px/1.8 system-ui}}a{{color:#b4d6ee}}img{{width:100%}}.note{{padding:16px;border-left:3px solid #92b0ca;background:#233243}}</style>
<small>HK3GTL / 既定MAX复制系统 · {data['key'].upper()}独立外观候选 / 2026-11-07</small><h1>{data['title']}</h1>
<p class="note">{w}×{d}×{h}（宽深高） · {check['blocks']:,}实体方块 · {check['unique_materials']}种材料。待负责人审阅；未批准、未部署。</p>
<p><a href="{data['key']}/三维评审.html">打开完整三维评审</a> · <a href="材料清单.json">材料清单</a> · <a href="verification.json">核验记录</a></p><img src="完整预览.png" alt="完整真实材质预览">
<p>{data['description']}</p><p>{data['purpose']}</p>
<p><a href="后侧设备.png">后侧设备</a> · <a href="主控材质近景.png">主控与通用接口</a> · <a href="逐层剖切.png">设备剖切</a></p>
<p>六处通用接口嵌入前端连续机体，不固定输入输出，保留五格接线净空。全部实体、维护通道、指定设备管路和完整NBT/Schematic回读已离线核验；方块来自增强版3.0真实资源，静态材质完整不等于注册、生存获取或游戏成型通过。四台MAX不在原69项尺寸表中，不虚报尺寸下限通过。</p>
<p>十周年派对与临时银幕保留为预案；西瓜ARG独立保留。客户端实测及桌面操作继续暂停。</p></html>''',encoding='utf-8')
    scripts=out/'生成脚本';scripts.mkdir(exist_ok=True)
    for p in [Path(__file__),Path(geometry.__file__),Path(entry_script)]:shutil.copy2(p,scripts/p.name)
    save(log/'package-status.json',dict(passed=True,approved=False,installed=False,game_verified=False,
        system_completed=False,blocks=check['blocks'],size_xyz=data['size'],materials=check['unique_materials'],
        pipe_routes=check['pipe_routes_count'],open_pipe_ends=0,hashes=exported['hashes']))
    print(json.dumps(dict(output=str(out),blocks=check['blocks'],materials=check['unique_materials'],surface_quads=merged['rendered_quads']),ensure_ascii=False))
