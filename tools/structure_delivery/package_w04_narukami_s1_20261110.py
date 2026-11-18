# -*- coding: utf-8 -*-
"""打包鸣雷见独立小样、静态完整表面与可对照参考的评审页。"""
from pathlib import Path
import base64
import gzip
import json
import shutil
import numpy as np
import w04_narukami_s1_20261110 as g
from build_i25_world_bubble_observatory_20261025 import resource_materials
from i34_open_observatory_export_20261027 import export_dense,surface_groups
from i37_surface_runs_20261027 import merge_surface_runs
from package_w04_gemini_b1_20261110 import hashes,save


def optical_surfaces(cube):
    """玻璃后方的晶核也要出面，不能套用不透明实体的遮面规则。"""
    groups=surface_groups(cube,g.STATES)
    transparent=np.isin(cube,[g.IDS[g.GLASS]])
    for face,axis,sign in [(0,2,1),(1,2,-1),(2,1,1),(3,1,-1),(4,0,-1),(5,0,1)]:
        neighbor=np.zeros_like(transparent);dst=[slice(None)]*3;src=[slice(None)]*3
        dst[axis]=slice(None,-1) if sign>0 else slice(1,None)
        src[axis]=slice(1,None) if sign>0 else slice(None,-1)
        neighbor[tuple(dst)]=transparent[tuple(src)]
        indices=np.flatnonzero((neighbor&(cube!=0)&~transparent).ravel());ids=cube.ravel()[indices]
        for i in range(len(g.STATES)):
            if len(indices[ids==i+1]):groups[i][face]=sorted(groups[i][face]+indices[ids==i+1].tolist())
    return groups


def main():
    before=hashes(g.PRIOR);save(g.LOG/'b2-before-hashes.json',before)
    view=g.OUT/'weapon';view.mkdir(exist_ok=True)
    scripts=g.OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    cube,data,parts=g.build();offset=np.array(data['blueprint_to_export_offset_xyz'])
    assert data['connectivity']['six_neighbor_components']==1
    exported=export_dense(cube,g.STATES,data['name'],view)
    materials,sources,packs=resource_materials(g.STATES)
    # 同格以合成体素的最终所属构件显示，避免部件接合处的共面闪烁。
    owner=np.zeros_like(cube)
    for i,p in enumerate(parts,1):
        at=p.p+offset;owner[at[:,1],at[:,2],at[:,0]]=i
    previews=[];quads=0
    for i,p in enumerate(parts,1):
        y,z,x=np.nonzero(owner==i);lo=np.array([x.min(),y.min(),z.min()]);hi=np.array([x.max(),y.max(),z.max()])
        size=hi-lo+1;local=np.zeros((size[1],size[2],size[0]),np.uint8)
        local[y-lo[1],z-lo[2],x-lo[0]]=cube[y,z,x]
        groups,lengths,proof=merge_surface_runs(optical_surfaces(local),size.tolist());quads+=proof['rendered_quads']
        previews.append(dict(id=p.name,origin=lo.tolist(),size=size.tolist(),starts=groups,lengths=lengths,blocks=len(x)))
    assert sum(p['blocks'] for p in previews)==data['blocks']
    audit=dict(passed=True,readback=exported['readback'],hashes=exported['hashes'],viewer_rendered_quads=quads,
        no_nominal_clipping=True,animation_enabled=False,material_resource_sources=sources,enabled_resource_packs=packs,
        connectivity=data['connectivity'],root_openings_preserved=True,b2_unchanged=before==hashes(g.PRIOR),
        reference_images=48,approved=False,installed=False,game_verified=False)
    assert audit['b2_unchanged']
    payload=dict(data=data,audit=audit,materials=materials,parts=previews)
    (view/'data.js').write_text('window.W04_STATIC_PAYLOAD='+json.dumps(base64.b64encode(gzip.compress(
        json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode())+';','utf8')
    source=(g.PRIOR/'生成脚本/viewer.mjs').read_text('utf8')
    source=source.replace("renderer.setClearColor('#18101c')","renderer.setClearColor('#171322')")
    source=source.replace('0xe8f4ff,1.1','0xe8f4ff,.8').replace('0xffffff,2','0xffffff,1.2').replace('0x8ed7ff,.9','0xd8c7ff,.45')
    source=source.replace("let direction=new THREE.Vector3(-1,.7,1.25)","let direction=new THREE.Vector3(-.35,.9,2.6)")
    source=source.replace("if(name==='back')direction.set(0,.15,-1);","if(name==='back')direction.set(0,0,-1);\n    if(name==='end')direction.set(-1,0,0);\n    if(name==='rearoblique')direction.set(.3,.8,-2.5);\n    if(['grip','tip','pommel'].includes(name))direction.set(0,.14,1);\n    if(name==='root')direction.set(-.2,.32,1.6);\n    if(name==='guard')direction.set(-.6,.3,1.4);\n    if(name==='guardend')direction.set(-1,.2,.15);")
    source=source.replace("document.getElementById('reset').onclick=()=>setView('front');","document.getElementById('reset').onclick=()=>setView('orthofront');")
    source=source.replace("resize();setView('front');","resize();setView('orthofront');")
    # 正反侧面按侧廓长宽拟合，端面与刃背保留真实厚度。
    source=source.replace("window.W04Static={config,scene", "window.W04Static={config,scene")
    (scripts/'viewer.mjs').write_text(source,'utf8')
    buttons=''.join(f'<button data-view="{key}">{name}</button>' for key,name in [
        ('orthofront','正面'),('back','背面'),('front','斜视'),('rearoblique','背斜视'),('top','刃背 / 厚度'),
        ('end','刀尖端向'),('tip','刀尖与骨白纹'),('root','不对称刃根'),('guard','环形刀镡'),('guardend','刀镡端面'),('grip','握柄'),('pommel','柄尾紫晶')])
    checks=''.join(f'<label><input type="checkbox" checked data-part="{p.name}">{p.name[3:]}</label>' for p in parts)
    (view/'三维评审.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title>
<style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#171322;color:#eee7f5;font:14px/1.65 system-ui}}header{{padding:16px 22px;background:#21182d}}h1{{font-size:23px;margin:5px 0}}a{{color:#e2adff}}button{{padding:8px 13px;margin:3px;background:#382446;border:1px solid #76508b;color:inherit;border-radius:6px;cursor:pointer}}#stage{{height:56vh;min-height:340px;width:100%;position:relative}}canvas{{display:block}}#loading{{position:absolute;top:20px;left:25px}}.tools{{padding:10px 22px}}label{{display:inline-block;margin-right:16px}}.reference{{margin:0 auto;max-width:1500px;padding:16px 35px;background:#262032}}.reference img{{width:100%;height:150px;object-fit:contain;image-rendering:auto}}p{{margin:6px 0}}.muted{{color:#b8abc8}}details{{margin:12px 0}}input[type=range]{{width:160px}}@media(max-width:750px){{#stage{{height:48vh}}.reference img{{height:100px}}}}</style>
<header><a href="../index.html">← 独立小样</a> · <a href="../参考图总览.html">48张参考</a><h1>{data['title']}</h1><p>弧形太刀 · 不对称镂空刃根 · 小环形刀镡 · 黑柄白缠带 · 尖叶紫晶柄尾</p><div>{buttons}<button id="reset">复位</button></div></header>
<div id="stage"><div id="loading">加载完整体素表面…</div></div><div class="tools"><p id="stats"></p><label><input id="glass" type="checkbox" checked>紫晶玻璃</label><label hidden><input id="ports" type="checkbox">接口</label><label>剖切高度 <input id="layer" type="range" min="0" max="{data['size'][1]-1}" value="{data['size'][1]-1}"><span id="layerLabel">{data['size'][1]-1}</span></label><details><summary>独立部件显隐</summary>{checks}</details></div>
<div class="reference"><b>同向侧面参考</b><img src="../轮廓取样源.png" alt="透明展示图转正后的真实侧廓"><p class="muted">参考原图545×320；转正与放大不增加细节。侧廓按图校准，厚度、背纹和遮挡连接按转台转译，尚未逐处复刻确认。拖动只改变相机；模型没有动画。</p></div>
<script src="data.js"></script><script src="viewer.bundle.js"></script></html>''','utf8')
    w,h,d=data['size']
    gallery=''.join(f'<figure><img src="{file}.png" alt="{name}"><figcaption>{name}</figcaption></figure>' for file,name in [
        ('正面','正面：参考轮廓校准'),('背面','背面：母纹转译，仍待核对'),('斜视','斜视：刃厚与环形刀镡'),('刃背','刃背：楔形厚度和圆柄'),
        ('刃根近景','不对称分叉与真实镂空'),('刀镡近景','小型环状刀镡'),('刀镡端面','刀镡端面与辐条连接'),('握柄近景','绕柄白色缠带'),('柄尾近景','尖叶镂空框与紫晶')])
    (g.OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title><style>:root{{color-scheme:dark}}body{{max-width:1550px;margin:28px auto;padding:0 25px;background:#171322;color:#eee7f5;font:16px/1.8 system-ui}}a{{color:#e2adff}}h1{{font-size:36px;margin:10px 0}}img{{width:100%;display:block}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0}}figcaption{{padding:8px}}.note{{border-left:3px solid #c980ef;padding:15px;background:#2a1d37}}.ref{{background:#282332;padding:20px}}@media(max-width:850px){{.grid{{display:block}}}}</style>
<p>W04 部件逐个制作 · 只制作超限鸣雷见 · 全静态</p><h1>涤罪七雷·鸣雷见<br>独立小样 S1</h1><p class="note">修正此前泛用大剑轮廓：弯太刀、上下不对称分叉、小型环状刀镡、黑色握柄与尖叶紫晶柄尾。武器依原型使用紫／红／黑／骨白，不强染整机绯雷红。</p>
<p><a href="weapon/三维评审.html">打开可旋转的静态三维预览</a> · <a href="参考图总览.html">48张专属参考</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p>
<img src="正面.png" alt="鸣雷见独立小样正面"><div class="ref"><b>同向侧面参考</b><img src="轮廓取样源.png" alt="真实参考侧廓"></div><p>独立细节比例：长{w} × 刀面跨度{h} × 最大厚度{d}格；{data['blocks']:,}实体方块，5个部件。尚未安放进W04，尺寸不代表整机最终比例。</p>
<p>48张参考＝同一转台一轮30个角度采样＋16张跨来源形态／握持辅助＋2张社区转存图；不是48个独立机位。<a href="参考图清单.json">来源、时间点与原始分辨率</a>均保留。</p>
<div class="grid">{gallery}</div><p class="note">侧廓与纹样位置有图可查；楔形刃厚、背面细纹与隐藏连接仍是参考转译，未宣称完全复刻。无动画，未批准、未注册、未进行游戏实装测试。旧B2保留历史，本轮不修改龙和W04整机。</p>
<p><a href="manifest.json">构件与边界</a> · <a href="verification.json">离线核验</a> · <a href="材料清单.json">材料</a> · <a href="weapon/{data['name']}.nbt">NBT</a> · <a href="weapon/{data['name']}.schem">Schematic</a></p></html>''','utf8')
    save(g.OUT/'manifest.json',data);save(g.OUT/'verification.json',audit)
    save(g.OUT/'材料清单.json',[dict(state=s,count=int(np.count_nonzero(cube==i+1)),role=g.ROLES[s]) for i,s in enumerate(g.STATES)])
    np.savez_compressed(g.LOG/'s1-components.npz',**{p.name+'__'+k:v for p in parts for k,v in [('p',p.p),('states',p.states)]})
    for file in [Path(__file__),Path(g.__file__),g.ROOT/'tools/structure_delivery/collect_narukami_study_20261110.py']:
        shutil.copy2(file,scripts/file.name)
    print(json.dumps(dict(passed=True,size=data['size'],blocks=data['blocks'],quads=quads,b2_unchanged=True)))


if __name__=='__main__':main()
