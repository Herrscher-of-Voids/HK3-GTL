# -*- coding: utf-8 -*-
"""导出扫描仪完整结构、真实材质与离线三维评审；不改已确认供料机。"""
import base64
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil

import mx_c02_scanner_geometry_v1_20261107 as geometry
from build_i25_world_bubble_observatory_20261025 import INSTANCE,resource_materials
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/MAX复制系统_扫描仪_三环谱系扫描台_V1_20261107'
LOG=ROOT/'logs/mx-c02-scanner-v1-20261107'
SHARED=ROOT/'deliveries/I39_无人跨界航路中继站_偏馈碟阵与双轨整备站_V1_20261027/i39'


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def viewer(data,check):
    css=re.search(r'<style>([\s\S]*?)</style>',(SHARED/'三维评审.html').read_text(encoding='utf-8'))[1]
    buttons=''.join(f'<button data-view="{key}">{label}</button>' for key,label in [
        ('front','前左全景'),('right','前右全景'),('back','后侧分析模块'),('top','俯视'),
        ('inside','逐层剖切'),('orthofront','正前'),('orthoside','正侧'),('texture','材质近景')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MAX扫描仪 · 三环谱系扫描台 V1</title><style>{css}</style>
<header><a href="../index.html">← 候选总览</a><h1>{data['title']}</h1><div>MAX · 45×61×29（宽×深×高） · {check['blocks']:,}实体方块 · 14种材料 · 待审</div></header>
<main class="review"><section id="stage" aria-label="完整真实材质三维预览"><div id="loading">加载真实材质与完整表面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">既定四台MAX复制系统中的谱系扫描端，内部候选号MX-C02。本版为独立外观候选，名称与工艺尚未冻结；未批准、未实装。</div>
<div class="locator"><b>主控蓝图 [22, 2, 5]</b><p>北向，整宽第23格；钻石块占位。六处接口全部通用，不固定输入输出。</p><button data-view="controller">定位主控</button></div>
<div>{buttons}</div><p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">28</b><input id="layer" type="range" min="0" max="28" value="28"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>设备分区与职责</summary><p>{data['description']}</p><p>概念职责为分析已取得样本或已批准蓝图版本，建立物质图样与材料清单引用。样本台、轨道与透镜只表达建筑用途，不冒充已运行扫描、动画或样本实物。谱系规则、研究许可和生存成本仍待实现。</p></details>
<details open><summary>主控与通用接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>文件与验收边界</summary><a href="{data['name']}.nbt">完整NBT</a> · <a href="{data['name']}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>增强版3.0真实资源静态首帧，六路冷却管全部逐格核对指定两端设备。完整结构文件回读、外露面合并后重展一致；隐藏材质或剖切不补画内部切面。未批准、未接入正式Pattern、未部署；注册、生存获取、成型与运行另验。MAX在当前范围没有更低档比较对象，不虚报递增通过率。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''


def main():
    assert json.loads((INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']=='3.0'
    OUT.mkdir(exist_ok=True,parents=True);LOG.mkdir(exist_ok=True,parents=True)
    view=OUT/'mx-c02';view.mkdir(exist_ok=True)
    cube,data=geometry.build();check=geometry.audit(cube,data)
    materials,sources,packs=resource_materials(geometry.STATES)
    exported=export_dense(cube,geometry.STATES,data['name'],view)
    assert exported['block_count']==check['blocks']
    groups,lengths,merge=merge_surface_runs(exported['surface_groups'],data['size'])
    source_files=sorted({s.split('!/',1)[0] for s in sources.values()})
    check.update(readback=exported['readback'],nbt_schem_sha256=exported['hashes'],
        source_instance=str(INSTANCE),instance_version='3.0',material_resource_sources=sources,
        resource_file_sha256={s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in source_files},
        enabled_file_resource_packs=packs,material_complete_cube=True,resource_registration_verified=False,
        viewer_surface_faces=merge['original_unit_faces'],viewer_surface_merge=merge,
        viewer_rendered_quads=merge['rendered_quads'],viewer_payload_exact_cell_readback=True)
    payload=dict(data=data,palette=geometry.STATES,surfaceGroups=groups,surfaceRunLengths=lengths,
        blockCount=check['blocks'],materials=materials,audit=check,names=geometry.ROLES)
    packed=gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),6)
    (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(base64.b64encode(packed).decode())+';',encoding='utf-8')
    bundle=(SHARED/'viewer.bundle.js').read_text(encoding='utf-8').replace('调度楼材质近景','样本控制舱材质近景').replace('偏馈碟阵与双轨整备站V1','MAX三环谱系扫描台V1')
    (view/'viewer.bundle.js').write_text(bundle,encoding='utf-8')
    (view/'三维评审.html').write_text(viewer(data,check),encoding='utf-8')
    save(OUT/'manifest.json',dict(data,target_voltage='MAX',candidate_version='V1',
        blocks=check['blocks'],unique_materials=14,status='candidate_waiting_user_review',
        approved=False,installed=False,game_verified=False,
        generated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        claim_boundary='独立外观候选；内部需求号与暂名不是正式机器注册，工艺和生存获取未验收。'))
    save(OUT/'verification.json',check)
    save(OUT/'材料清单.json',[dict(state=s,count=check['palette'][s],role=geometry.ROLES[s],survival_stage_verified=False) for s in geometry.STATES])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{geometry.TITLE}</title>
<style>body{{max-width:1280px;margin:32px auto;padding:0 22px;background:#111c29;color:#e5edf3;font:16px/1.8 system-ui}}a{{color:#b4d6ee}}img{{width:100%}}.note{{padding:16px;border-left:3px solid #92b0ca;background:#233243}}</style>
<small>HK3GTL / 四台MAX复制系统 · 第二台独立外观候选 / 2026-11-07</small><h1>{geometry.TITLE}</h1>
<p class="note">45×61×29（宽深高） · {check['blocks']:,}实体方块 · 14种材料。待负责人审阅；未批准、未部署。</p>
<p><a href="mx-c02/三维评审.html">打开完整三维评审</a> · <a href="材料清单.json">材料清单</a> · <a href="verification.json">核验记录</a></p><img src="完整预览.png" alt="三环谱系扫描台完整真实材质预览">
<p>{data['description']}六处通用接口直接嵌入前端机体，五格接线净空；样本台两侧各保留两格宽检修通道。</p>
<p><a href="后侧分析.png">后侧分析与供电</a> · <a href="主控材质近景.png">主控与通用接口</a> · <a href="逐层剖切.png">内部剖切</a></p>
<p>职责方案：已取得样本／已批准蓝图版本＋研究许可→物质图样及材料清单引用。当前仅完成建筑表达，未实装扫描、动画、图样或免费复制能力；正式名称、研究与成本尚未冻结。</p>
<p>完整NBT与Schematic逐格回读一致，合并表面重展一致，主体连通与镜像、维护净空、六路冷却管的指定设备接点均通过离线检查。材质来自目标增强版3.0；静态资源核验不等于注册、生存获取或游戏成型验收。四台MAX无原69表尺寸基线，不虚报下限通过。</p>
<p>供料机MX-C01 V2外观确认继续有效，batch-11仍为1/5；本扫描仪待审，不计批准数。十周年预案、西瓜ARG与客户端实测暂停安排继续保留。</p></html>''',encoding='utf-8')
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for p in (Path(__file__),Path(geometry.__file__)):shutil.copy2(p,scripts/p.name)
    save(LOG/'package-status.json',dict(passed=True,approved=False,installed=False,system_completed=False,
        blocks=check['blocks'],size_xyz=data['size'],materials=14,pipe_routes=6,open_pipe_ends=0,hashes=exported['hashes']))
    print(json.dumps(dict(output=str(OUT),blocks=check['blocks'],materials=14,surface_quads=merge['rendered_quads']),ensure_ascii=False))


if __name__=='__main__':
    main()
