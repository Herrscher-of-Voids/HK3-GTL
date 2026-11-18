# -*- coding: utf-8 -*-
"""复用真实资源导出与逐格查看器，制作MAX供料机候选，不写入实例。"""
import base64
import datetime as dt
import gzip
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import zipfile

import mx_c01_converter_geometry_v1_20261107 as geometry
from build_i25_world_bubble_observatory_20261025 import resource_materials, INSTANCE
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/MAX复制系统_供料机_双罐脉冲转化厂_V1_20261107'
LOG = ROOT / 'logs/mx-c01-converter-v1-20261107'
PREVIOUS = ROOT / 'deliveries/I39_无人跨界航路中继站_偏馈碟阵与双轨整备站_V1_20261027/i39'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def page(data, check):
    old = (PREVIOUS/'三维评审.html').read_text(encoding='utf-8')
    css = re.search(r'<style>([\s\S]*?)</style>',old)[1]
    buttons = ''.join(f'<button data-view="{key}">{label}</button>' for key,label in [
        ('front','前左全景'),('right','前右全景'),('back','后侧冷却'),('top','俯视'),
        ('inside','逐层剖切'),('orthofront','正前'),('orthoside','正侧'),('texture','材质近景')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAX供料机 · 双罐脉冲转化厂 V1</title><style>{css}</style>
<header><a href="../index.html">← 候选总览</a><h1>{data['title']}</h1><div>MAX · 41×53×31（宽×深×高） · {check['blocks']:,}实体方块 · 13种材料 · 待审</div></header>
<main class="review"><section id="stage" aria-label="完整真实材质三维预览"><div id="loading">加载真实材质与完整表面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">四台MAX复制系统中的供料端，内部候选号MX-C01。名称、介质与工艺参数尚未冻结；本版仅供审阅建筑外观。</div>
<div class="locator"><b>主控蓝图 [20, 2, 5]</b><p>北向，整宽第21格；钻石块标记。六处接口全部通用，不指定物品／流体输入输出位置。</p><button data-view="controller">定位主控</button></div>
<div>{buttons}</div><p>左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 <b id="layerValue">30</b><input id="layer" type="range" min="0" max="30" value="30"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>设备分区</summary><p>{data['description']}</p><p>前端计量舱→中轴卧式转化腔，左右独立储罐汇流，后端冷却。绝缘环、鞍座、母线和检修路均属于完整实体结构。管线为工程表达，未赋予未注册介质或工艺运行能力。</p></details>
<details open><summary>主控与通用接口</summary><div id="portButtons"></div><div id="ports"></div></details>
<details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>文件与验收边界</summary><a href="{data['name']}.nbt">完整NBT</a> · <a href="{data['name']}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>增强版3.0现有资源，静态首帧预览。完整结构逐格回读，表面合并后重展一致；隐藏材质或剖切不补画内部切面。未批准、未接入正式Pattern、未部署；注册状态、生存获取和游戏成型仍需分别验收。MAX在当前比较范围内没有更低档结构，递增项不计通过率。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''


def main():
    assert json.loads((INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId'] == '3.0'
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    view = OUT/'mx-c01';view.mkdir(exist_ok=True)
    cube,data=geometry.build();check=geometry.audit(cube,data)
    materials,sources,packs=resource_materials(geometry.STATES)
    exported=export_dense(cube,geometry.STATES,data['name'],view)
    assert exported['block_count']==check['blocks']
    groups,lengths,merged=merge_surface_runs(exported['surface_groups'],data['size'])
    source_files=sorted({s.split('!/',1)[0] for s in sources.values()})
    resource_hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in source_files}
    check.update(readback=exported['readback'],nbt_schem_sha256=exported['hashes'],
                 source_instance=str(INSTANCE),instance_version='3.0',
                 material_resource_sources=sources,resource_file_sha256=resource_hashes,
                 enabled_file_resource_packs=packs,material_complete_cube=True,
                 resource_registration_verified=False,
                 viewer_surface_faces=merged['original_unit_faces'],viewer_surface_merge=merged,
                 viewer_rendered_quads=merged['rendered_quads'],viewer_payload_exact_cell_readback=True)
    payload=dict(data=data,palette=geometry.STATES,surfaceGroups=groups,surfaceRunLengths=lengths,
                 blockCount=check['blocks'],materials=materials,audit=check,names=geometry.ROLES)
    packed=gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),6)
    (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(base64.b64encode(packed).decode())+';',encoding='utf-8')
    bundle=(PREVIOUS/'viewer.bundle.js').read_text(encoding='utf-8')
    bundle=bundle.replace('调度楼材质近景','控制舱材质近景').replace('偏馈碟阵与双轨整备站V1','MAX双罐脉冲转化厂V1')
    (view/'viewer.bundle.js').write_text(bundle,encoding='utf-8')
    (view/'三维评审.html').write_text(page(data,check),encoding='utf-8')
    manifest=dict(data,blocks=check['blocks'],unique_materials=check['unique_materials'],
                  target_voltage='MAX',candidate_version='V1',status='candidate_waiting_user_review',
                  approved=False,installed=False,game_verified=False,
                  generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=-5))).isoformat(timespec='seconds'),
                  claim_boundary='仅独立外观候选；正式名称、介质和参数尚未冻结。')
    save(OUT/'manifest.json',manifest);save(OUT/'verification.json',check)
    save(OUT/'材料清单.json',[dict(state=s,count=check['palette'][s],role=geometry.ROLES[s],survival_stage_verified=False) for s in geometry.STATES])
    title=html.escape(data['title'])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{max-width:1280px;margin:32px auto;padding:0 22px;background:#111c29;color:#e5edf3;font:16px/1.8 system-ui}}a{{color:#b4d6ee}}img{{width:100%}}.note{{padding:16px;border-left:3px solid #92b0ca;background:#233243}}</style>
<small>HK3GTL / 四台MAX复制系统 · 第一台外观候选 / 2026-11-07</small><h1>{title}</h1>
<p class="note">41×53×31（宽深高） · {check['blocks']:,}实体方块 · 13种材料。待负责人审阅；未批准、未部署。</p>
<p><a href="mx-c01/三维评审.html">打开完整三维评审</a> · <a href="材料清单.json">材料清单</a> · <a href="verification.json">核验记录</a></p><img src="完整预览.png" alt="双罐脉冲转化厂完整真实材质预览">
<p>{data['description']}六个通用接口都在前端连续机体外墙，保持五格接线净空；不设固定输入输出位置。</p>
<p><a href="后侧冷却.png">后侧冷却与回路</a> · <a href="主控材质近景.png">主控与接口近景</a> · <a href="逐层剖切.png">设备剖切</a></p>
<p>既定职责方向：MAX可达崩坏能与运行EU→可计量的重构介质，为复制系统供料。名称、介质、成本与配方仍是方案，未注册或定标；不声称可免费造物。与谱系扫描、图谱存储、精密重构三台需求分开。</p>
<p>MAX采用整合包原生材料，不新增自定义MAX机壳。四台不在原69项尺寸表中，本版不虚报既有尺寸下限通过。主体最大单材、真实边界、单连通、镜像、主控与接口净空、NBT/Schematic逐格回读及表面重展已离线核验。静态资源完整不等于注册、生存获取或游戏成型通过。</p>
<p>十周年派对与临时剧情银幕已立为预案；西瓜维度ARG单独保留。本候选不增加毕业前置或媒体依赖。</p></html>''',encoding='utf-8')
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for p in (Path(__file__),Path(geometry.__file__)):
        shutil.copy2(p,scripts/p.name)
    save(LOG/'package-status.json',dict(passed=True,approved=False,installed=False,blocks=check['blocks'],size_xyz=data['size'],hashes=exported['hashes']))
    print(json.dumps(dict(output=str(OUT),blocks=check['blocks'],materials=check['unique_materials'],surface_quads=merged['rendered_quads']),ensure_ascii=False))


if __name__=='__main__':
    main()
