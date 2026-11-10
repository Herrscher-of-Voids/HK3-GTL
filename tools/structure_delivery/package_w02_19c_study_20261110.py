# -*- coding: utf-8 -*-
"""导出19C静态造型研究与可追溯的颜色、参考和完整体素证据。"""
import base64
from datetime import datetime, timezone, timedelta
import gzip
from html import escape
import hashlib
import io
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image, ImageStat
import w02_19c_study_20261110 as g
from build_i25_world_bubble_observatory_20261025 import resource_materials
from i34_open_observatory_export_20261027 import export_dense, surface_groups
from i37_surface_runs_20261027 import merge_surface_runs


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n','utf8')


def main():
    g.OUT.mkdir(exist_ok=True);g.LOG.mkdir(exist_ok=True)
    view=g.OUT/'w02';view.mkdir(exist_ok=True)
    scripts=g.OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    cube,data,parts=g.build()
    assert not data['animation_enabled'] and len(parts)==5
    assert data['controller'] is None and not data['matrix_layout_complete']
    assert all('翼' not in p.name for p in parts)
    counts=np.bincount(cube.ravel(),minlength=len(g.STATES)+1)
    used=[i for i in range(1,len(g.STATES)+1) if counts[i]]
    states=[g.STATES[i-1] for i in used]
    remap=np.zeros(len(g.STATES)+1,np.uint8)
    for new,old in enumerate(used,1):remap[old]=new
    cube=remap[cube]
    for part in parts:part.states=remap[part.states]
    offset=np.array(data['blueprint_to_export_offset_xyz']);size=np.array(data['size'])
    for p in parts:
        at=p.p+offset
        assert np.all(at>=0) and np.all(at<size)
    print('导出19C完整小样。',flush=True)
    exported=export_dense(cube,states,data['name'],view)
    materials,sources,packs=resource_materials(states)
    previews=[];quads=0
    for p in parts:
        low,high=p.p.min(0),p.p.max(0);extent=high-low+1
        local=np.zeros((extent[1],extent[2],extent[0]),np.uint8);at=p.p-low
        local[at[:,1],at[:,2],at[:,0]]=p.states
        groups,lengths,merged=merge_surface_runs(surface_groups(local,states),extent.tolist())
        quads+=merged['rendered_quads']
        previews.append(dict(id=p.name,origin=(low+offset).tolist(),size=extent.tolist(),
                             starts=groups,lengths=lengths,blocks=len(p.p)))
    audit=dict(passed=True,geometry_export_verified=True,no_nominal_clipping=True,
               animation_enabled=False,animation_loop_present=False,blocks=data['blocks'],
               original_components=len(parts),viewer_rendered_quads=quads,readback=exported['readback'],
               hashes=exported['hashes'],materials=states,material_resource_sources=sources,
               enabled_resource_packs=packs,instance_version='3.5',desktop_used=False,
               game_started=False,game_verified=False,reference_fidelity_verified=False,
               static_clearance_verified=False,matrix_layout_complete=False,
               claim_boundary='独立静态体素造型小样；非逐处还原验收、非完整W02、非实装测试。')
    data['generated_at']=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    payload=dict(data=data,audit=audit,materials=materials,parts=previews)
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode()
    (view/'data.js').write_text('window.W02_STATIC_PAYLOAD='+json.dumps(encoded)+';','utf8')
    source=(g.ROOT/'deliveries/W02_Gemini_半构造星核船坞_V4S_静态_20261109/生成脚本/w02_static_viewer_v4s_20261109.mjs').read_text('utf8')
    source=source.replace('[dictControl(),...data.ports]','[...(data.controller?[dictControl()]:[]),...data.ports]')
    source=source.replace("if(name==='side')direction.set(1,0,0);","if(name==='side')direction.set(1,0,0);\n    if(name==='back')direction.set(.7,.2,-1);")
    source=source.replace('new THREE.Vector3(0,148,0)','new THREE.Vector3(...data.center_blueprint)')
    source=source.replace("if(name==='controller')target.set(...data.controller);", "if(name==='controller'&&data.controller)target.set(...data.controller);")
    source=source.replace("name==='controller'?new THREE.Box3", "name==='controller'&&data.controller?new THREE.Box3")
    assert not any(s in source for s in ['requestAnimationFrame','setInterval','data.motions','function seek'])
    (scripts/'viewer.mjs').write_text(source,'utf8')
    options=''.join(f'<label><input type="checkbox" checked data-part="{escape(p.name)}">{escape(p.name)}</label>' for p in parts)
    buttons=''.join(f'<button data-view="{key}">{label}</button>' for key,label in [('front','全景'),('orthofront','正面'),('side','侧面'),('back','背面'),('top','俯视'),('core','胸甲')])
    (view/'三维评审.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W02 · 普通理之律者19C静态小样</title>
<style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#0b1624;color:#e8f6ff;font:14px/1.7 system-ui}}header{{padding:12px 20px}}h1{{font-size:20px;margin:0}}a{{color:#8fbcff}}main{{display:grid;grid-template-columns:minmax(0,1fr) 300px;height:calc(100vh - 94px)}}#stage{{position:relative;overflow:hidden}}canvas{{display:block}}aside{{padding:16px;overflow:auto;background:#102238}}button{{padding:7px 10px;margin:3px;border:1px solid #59728d;border-radius:5px;background:#19334c;color:white;cursor:pointer}}label{{display:block}}input[type=range]{{width:100%}}#loading{{position:absolute;inset:45% 10%;text-align:center}}#legend{{position:absolute;bottom:12px;left:12px;background:#0c1a2dde;padding:8px}}.note{{border-left:3px solid #428DFF;padding-left:10px}}@media(max-width:800px){{main{{display:block;height:auto}}#stage{{height:65vh}}}}</style>
<header><a href="../index.html">← 小样与参考说明</a><h1>理之律者 · 重装小兔19C</h1><span>V1 · 纯静态造型研究 · 完整{size[0]}×{size[2]}×{size[1]}（宽深高）</span></header>
<main><section id="stage"><div id="loading">准备完整静态构件…</div><div id="legend">构造蓝 #428DFF / 白装甲 / 深色机械骨架</div></section><aside><p class="note">普通理之律者19C。参考正面截图制作胸甲、分节双臂与机械手；顶部与背面资料尚不完整。</p><p>{buttons}</p><button id="reset">重置视角</button><label><input id="glass" type="checkbox" checked>显示玻璃</label><label hidden><input id="ports" type="checkbox">接口</label><label>剖切高度 <output id="layerLabel">{size[1]-1}</output><input id="layer" type="range" min="0" max="{size[1]-1}" value="{size[1]-1}"></label><p id="stats"></p><details open><summary>独立构件</summary>{options}</details><p>未接回649×493×303工业矩阵。没有控制器与接口占位，不代表机器成型或运行。</p><p><a href="../verification.json">核验</a> · <a href="../manifest.json">完整坐标与转译边界</a></p></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>''','utf8')
    palette=[]
    final_counts=np.bincount(cube.ravel(),minlength=len(states)+1)
    for material,count in zip(materials,final_counts[1:]):
        rgb=ImageStat.Stat(Image.open(io.BytesIO(base64.b64decode(material['faces']['up'].split(',')[1]))).convert('RGB')).mean
        palette.append(dict(state=material['state'],count=int(count),role=g.ROLES[material['state']],actual_texture_average_rgb=[round(v,1) for v in rgb]))
    save(g.OUT/'manifest.json',data);save(g.OUT/'verification.json',audit);save(g.OUT/'材料清单.json',palette)
    save(g.OUT/'参考与配色.json',dict(identity='普通理之律者，非羽化后的真理之律者',
        reference='https://honkaiimpact3.fandom.com/wiki/Herrscher_of_Reason/Outfit',
        reference_type='资料站所载游戏正面截图；不是完整官方模型多视图',
        color_source='deliveries/已完成多方块_电压与配色逐台核对_20261029/index.html#wonder-palette',
        palette_identity=data['palette_identity'],limitations=data['source_conflicts']))
    np.savez_compressed(g.LOG/'original-components.npz',**{p.name+'__'+k:v for p in parts for k,v in [('p',p.p),('states',p.states)]})
    notes=''.join('<li>'+escape(s)+'</li>' for s in data['source_conflicts'])
    swatches=''.join(f'<span style="display:inline-block;width:36px;height:36px;background:{c};border:1px solid #789;margin:4px" title="{c}"></span>' for c in ['#428DFF','#e8edf4','#171c29','#7ab8ef','#eb8f29'])
    (g.OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W02 · 理之律者19C静态造型研究</title><style>:root{{color-scheme:dark}}body{{max-width:1280px;margin:32px auto;padding:0 24px;background:#0c1828;color:#e5f5ff;font:16px/1.8 system-ui}}a{{color:#8fbcff}}img{{width:100%;display:block}}.note{{padding:16px;background:#19334c;border-left:3px solid #428DFF}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}@media(max-width:800px){{.grid{{display:block}}}}</style>
<h1>理之律者 · 重装小兔19C</h1><p>W02 · V1纯静态造型小样 · 2026-11-10</p><p class="note">按普通理之律者重新研究19C。参考正面白蓝胸甲、深色分节机械臂与机械手；本件不是完整工业矩阵，也尚未达到逐处复刻验收。</p>
<p><a href="w02/三维评审.html">打开静态三维小样</a> · <a href="参考与配色.json">参考与配色依据</a> · <a href="verification.json">离线核验</a></p><img src="完整预览.png" alt="19C体素造型小样"><div class="grid"><img src="正面.png" alt="19C正面"><img src="侧面.png" alt="19C侧面"></div>
<p>{swatches}<br>W02外观身份：HBV · 构造蓝 <b>#428DFF</b>；运行目标仍为WSV。现有蓝与浅蓝材质为颜色近似；白色装甲与深色内构件保留，橙色只点缀胸部晶核。未恢复指定机壳必须最多的旧规则。</p><p>完整小样{size[0]}×{size[2]}×{size[1]}（宽深高），{data['blocks']:,}实体方块，{len(parts)}个独立构件。无动画、时间轴或持续重绘；可转镜头、剖切与显隐。</p>
<p><a href="https://honkaiimpact3.fandom.com/wiki/Herrscher_of_Reason/Outfit">参考图来源：资料站所载游戏截图</a> · <a href="../已完成多方块_电压与配色逐台核对_20261029/index.html#wonder-palette">项目律者配色表</a></p><ul>{notes}</ul>
<p>原十二翼候选仅保留历史，本次不继承为当前造型基线。独立件接合体素如实记录于manifest，尚未逐处验收；未注册控制器、未搭建完整工业矩阵、未进行游戏成型或运行测试。</p>
<p><a href="w02/{data['name']}.nbt">NBT小样</a> · <a href="w02/{data['name']}.schem">Schematic小样</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p></html>''','utf8')
    for file in [Path(__file__),Path(g.__file__)]:shutil.copy2(file,scripts/file.name)
    print(json.dumps(dict(passed=True,blocks=data['blocks'],size_xyz=data['size'],quads=quads),ensure_ascii=False))


if __name__=='__main__':main()
