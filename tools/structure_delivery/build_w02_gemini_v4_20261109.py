# -*- coding: utf-8 -*-
"""导出组合结构与独立完整构件预览，使用当前3.5实例材质。"""
import base64
from datetime import datetime, timezone, timedelta
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
import numpy as np
import w02_gemini_geometry_v4_20261109 as g
from build_i25_world_bubble_observatory_20261025 import resource_materials, INSTANCE
from i34_open_observatory_export_20261027 import export_dense, surface_groups
from i37_surface_runs_20261027 import merge_surface_runs

ROOT, OUT, LOG = g.ROOT, g.OUT, g.LOG


def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def preview_page(data,check):
    options=''.join(f'<label><input type="checkbox" checked data-part="{escape(n)}">{escape(n)}</label>' for n in data['component_bounds_blueprint'])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W02 Gemini V4 · 动态原案预览</title>
<style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#0b1624;color:#e8f6ff;font:14px/1.6 system-ui}}header{{padding:12px 20px;border-bottom:1px solid #35506b}}h1{{font-size:19px;margin:0}}a{{color:#80ddff}}main{{display:grid;grid-template-columns:minmax(0,1fr) 300px;height:calc(100vh - 80px)}}#stage{{position:relative;min-height:400px;overflow:hidden}}canvas{{display:block;width:100%;height:100%}}aside{{padding:16px;overflow:auto;background:#102238}}button{{padding:7px 10px;margin:3px;border:1px solid #59728d;border-radius:5px;background:#19334c;color:white;cursor:pointer}}label{{display:block;margin:6px 0}}input[type=range]{{width:100%}}#loading{{position:absolute;inset:45% 10%;text-align:center;pointer-events:none}}#legend{{position:absolute;bottom:12px;left:12px;padding:8px 12px;background:#0c1a2dde;pointer-events:none}}.note{{border-left:2px solid #7adeff;padding-left:10px}}details{{margin:12px 0}}@media(max-width:800px){{main{{display:block;height:auto}}#stage{{height:65vh}}aside{{max-height:none}}}}</style>
<header><a href="../index.html">← V4总览</a><h1>理之律者 · 万象·自律工业矩阵</h1><span>Gemini 最新原案 V4 · {check['blocks']:,}实体方块 · 动画为网页试览</span></header>
<main><section id="stage"><div id="loading">准备完整构件与真实材质…</div><div id="legend">白瓷装甲 / 暗金骨架 / 冰蓝构造光路</div></section><aside>
<div class="note">四重力井 · 十二弯刀翼 · 半构造星核 · 三重冠冕。独立构件完整显示，原案相交照实保留。</div>
<p>{' '.join(f'<button data-view="{k}">{v}</button>' for k,v in [('front','全景'),('orthofront','正面'),('side','侧面'),('top','俯视'),('core','星核'),('controller','主控')])}</p>
<button id="play">播放原案动画</button><button id="reset">复位</button><label>演出时间 <output id="timeLabel">0.0 秒</output><input id="time" aria-label="演出时间" type="range" min="0" max="360" step="0.1" value="0"></label>
<label><input id="glass" type="checkbox" checked>显示玻璃</label><label><input id="ports" type="checkbox">接口定位框</label>
<label>剖切高度（自动暂停并回原位）<output id="layerLabel">{data['size'][1]-1}</output><input id="layer" aria-label="剖切高度" type="range" min="0" max="{data['size'][1]-1}" value="{data['size'][1]-1}"></label>
<p id="stats"></p><details><summary>独立构件显隐</summary>{options}</details>
<details open><summary>坐标与原案冲突</summary><p>名义649×493×303。实际{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽深高）。<a href="../原案参数与冲突.json">完整参数与转译</a>；动画扫掠单独扩展取景。</p></details>
<p>控制器蓝图(0,18,246)，朝南；钻石块仅外观占位，8处接口均通用。</p>
<p>网页动画未接入游戏；原案静态相交与运动干涉待协调。新机壳、CTM与Shader未注册。<a href="../verification.json">离线核验</a> · <a href="../manifest.json">完整蓝图</a></p>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''


def main():
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
    old=ROOT/'deliveries/W02_Gemini_十二翼重构船坞_V3_20261108'
    baseline=LOG/'report-baseline'
    if not baseline.exists():
        baseline.mkdir()
        for name in ('index.html','current-summary.json'):shutil.copy2(ROOT/'logs/beta5-completion-audit-20261030'/name,baseline/name)
        save(LOG/'old-v3-sha256.json',{str(p.relative_to(ROOT)):sha(p) for p in old.rglob('*') if p.is_file()})
    cube,data,parts=g.build();counts=np.bincount(cube.ravel(),minlength=len(g.STATES)+1)
    assert np.all(counts[1:]) and len(data['wells'])==4 and len(data['wings'])==12 and len(data['cables'])==8
    assert data['core']['vertices']==60 and data['core']['edges']==90 and len(data['crowns'])==3
    assert all(c['rails']==2 for c in data['crowns'])
    assert len({c['cage_vertex'] for c in data['cables']})==8
    for c in data['cables']:assert np.array_equal(c['end'],data['core']['cage_vertices'][c['cage_vertex']])
    assert data['controller_blueprint']==[0,18,246] and len(data['ports'])==8
    for side in (-1,1):assert [round(w['angle_degrees']) for w in data['wings'] if w['side']==side]==[-10,5,18,32,46,60]
    offset=np.array(data['blueprint_to_export_offset_xyz']);size=np.array(data['size']);portchecks=[]
    for item in [dict(id='主控',pos=data['controller'])]+data['ports']:
        at=np.array(item['pos']);inside=at-[0,0,1]
        assert cube[at[1],at[2],at[0]] and cube[inside[1],inside[2],inside[0]]
        for step in range(1,6):
            pos=at+[0,0,step]
            if np.all(pos<size):assert not cube[pos[1],pos[2],pos[0]],item
        portchecks.append(dict(id=item['id'],outer_clear=5,inner_backed=True))
    for p in parts:
        at=p.p+offset
        assert np.all(at>=0) and np.all(at<size),p.name
    check=dict(passed=True,geometry_passed=True,design_rules_passed=False,no_nominal_clipping=True,
        blocks=int(counts[1:].sum()),unique_materials=len(g.STATES),size_xyz=data['size'],
        palette=dict(zip(g.STATES,map(int,counts[1:]))),port_checks=portchecks,
        approved=False,installed=False,game_verified=False,dynamic_clearance_verified=False,
        source_instance=str(INSTANCE),instance_version='3.5',version_source='负责人确认与enhanced35-baseline记录',
        desktop_used=False,game_started=False,air_registered_as_required_structure=False,
        claim_boundary='独立候选与离线原案试览；未注册机器、未修改游戏文件、未进行实机成型或运行测试。')
    view=OUT/'w02';view.mkdir(exist_ok=True)
    print('几何完成，导出组合NBT与Schematic。',flush=True)
    exported=export_dense(cube,g.STATES,data['name'],view)
    check.update(readback=exported['readback'],nbt_schem_sha256=exported['hashes'])
    materials,sources,packs=resource_materials(g.STATES)
    check.update(material_resource_sources=sources,enabled_resource_packs=packs,resource_registration_verified=False)
    sources_files={s.split('!/',1)[0] for s in sources.values()}
    check['resource_file_sha256']={s:sha(Path(s)) for s in sorted(sources_files)}
    previews=[];quads=0
    for p in parts:
        lo,hi=p.p.min(0),p.p.max(0);extent=hi-lo+1
        local=np.zeros((extent[1],extent[2],extent[0]),np.uint8);at=p.p-lo
        local[at[:,1],at[:,2],at[:,0]]=p.states
        groups,lengths,merged=merge_surface_runs(surface_groups(local,g.STATES),extent.tolist())
        quads+=merged['rendered_quads']
        previews.append(dict(id=p.name,origin=(lo+offset).tolist(),size=extent.tolist(),
            starts=groups,lengths=lengths,blocks=len(p.p)))
    check.update(viewer_rendered_quads=quads,complete_original_component_preview=True,
        all_component_surface_runs_exact=True,overlap_pairs=len(data['component_overlaps']))
    data.update(blocks=check['blocks'],target_voltage='WSV',unique_materials=len(g.STATES),
        status='candidate_waiting_user_review',generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat())
    payload=dict(data=data,audit=check,materials=materials,parts=previews)
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode()
    (view/'data.js').write_text('window.W02_V4_PAYLOAD='+json.dumps(encoded)+';','utf8')
    (view/'三维评审.html').write_text(preview_page(data,check),'utf8')
    for filename,value in [('manifest.json',data),('verification.json',check),('原案参数与冲突.json',dict(
        source_conflicts=data['source_conflicts'],coordinate_interpretation=data['coordinate_interpretation'],
        component_overlaps=data['component_overlaps'],motions=data['motions'],cables=data['cables'],wings=data['wings']))]:save(OUT/filename,value)
    save(OUT/'材料清单.json',[dict(state=s,count=int(n),role=g.ROLES[s]) for s,n in zip(g.STATES,counts[1:])])
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for path in (Path(__file__),Path(g.__file__)):shutil.copy2(path,scripts/path.name)
    issues=''.join('<li>'+escape(v)+'</li>' for v in data['source_conflicts'])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W02 Gemini V4 · 半构造星核船坞</title><style>:root{{color-scheme:dark}}body{{max-width:1360px;margin:32px auto;padding:0 24px;background:#0c1828;color:#e5f5ff;font:16px/1.8 system-ui}}a{{color:#85ddff}}img{{width:100%;display:block}}.note{{padding:16px;background:#19334c;border-left:3px solid #78dcff}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}@media(max-width:800px){{.grid{{display:block}}}}</style>
<h1>理之律者 · 万象·自律工业矩阵</h1><p>Gemini 最新原案 V4 · 半构造星核船坞 · 2026-11-09</p>
<p class="note">四重力井、十二弯刀翼、双联轨道炮、半构造星核与三重演算星环。实际{size[0]}×{size[2]}×{size[1]}（宽×深×高），{check['blocks']:,}实体方块。先完整生成，再求包围盒。候选待审。</p>
<p><a href="w02/三维评审.html">打开可旋转的完整动态预览</a> · <a href="../W02_Gemini_十二翼重构船坞_V3_20261108/index.html">旧V3对照</a> · <a href="原案参数与冲突.json">原案参数与冲突</a> · <a href="verification.json">离线核验</a></p>
<img src="完整预览.png" alt="V4完整建筑全景"><div class="grid"><img src="正面十二翼.png" alt="V4正面"><img src="俯视布局.png" alt="四重力井与十字裂谷"></div>
<p>动画按钮可试览中内环立体翻转、星笼与构造体素转动、十二翼轻浮与四站扫描下行。默认暂停在原案初始状态；不是游戏运行录像。</p>
<div class="grid"><img src="半构造星核.png" alt="半构造天体核心"><img src="原案动画.webp" alt="原案网页动画试览"></div>
<details><summary>原文冲突与缺省转译</summary><ul>{issues}</ul></details>
<p>{len(data['component_overlaps'])}对静态构件共享体素，包含预期接合与待协调干涉。独立预览保留双方完整几何；组合NBT同格取后生成者，原坐标另存，不以回读通过冒充无穿模。</p>
<p>本页为离线候选。新材质、CTM及游戏Shader未注册；真实控制器、完整成型、运行与特效实测仍待完成。增强版3.5的当前资源只用于材质解析。</p>
<p><a href="w02/{data['name']}.nbt">组合NBT</a> · <a href="w02/{data['name']}.schem">Schematic</a> · <a href="材料清单.json">材料清单</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p></html>''','utf8')
    print(json.dumps(dict(passed=True,blocks=check['blocks'],size=data['size'],quads=quads,parts=len(parts)),ensure_ascii=False))


if __name__=='__main__':main()
