# -*- coding: utf-8 -*-
"""导出俱利伽罗独立小样与完整静态三维页，保留已交付七雷和旧B2。"""
from pathlib import Path
import base64,gzip,json,shutil
import numpy as np
from scipy.spatial import ConvexHull
import w04_kurikara_d2_20261110 as g
from build_i25_world_bubble_observatory_20261025 import resource_materials
from i34_open_observatory_export_20261027 import export_dense,surface_groups
from i37_surface_runs_20261027 import merge_surface_runs
from package_w04_gemini_b1_20261110 import hashes,save


def main():
    g.LOG.mkdir(exist_ok=True)
    history={p.name:hashes(p) for p in [g.PRIOR,g.SWORD]};save(g.LOG/'prior-before-hashes.json',history)
    cube,data,parts=g.build();assert data['connectivity']['six_neighbor_components']==1
    view=g.OUT/'dragon';view.mkdir(exist_ok=True);scripts=g.OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    exported=export_dense(cube,g.STATES,data['name'],view);print('导出回读一致',flush=True)
    materials,sources,packs=resource_materials(g.STATES)
    offset=np.array(data['blueprint_to_export_offset_xyz']);owner=np.zeros_like(cube)
    for i,p in enumerate(parts,1):
        at=p.p+offset;owner[at[:,1],at[:,2],at[:,0]]=i
    previews=[];quads=0
    for i,p in enumerate(parts,1):
        at=p.p+offset;chosen=owner[at[:,1],at[:,2],at[:,0]]==i;at=at[chosen]
        lo=at.min(0);hi=at.max(0);size=hi-lo+1;local=np.zeros((size[1],size[2],size[0]),np.uint8)
        q=at-lo;local[q[:,1],q[:,2],q[:,0]]=cube[at[:,1],at[:,2],at[:,0]]
        groups,lengths,proof=merge_surface_runs(surface_groups(local,g.STATES),size.tolist());quads+=proof['rendered_quads']
        previews.append(dict(id=p.name,origin=lo.tolist(),size=size.tolist(),starts=groups,lengths=lengths,blocks=len(at)))
        print('完整表面',p.name,proof['rendered_quads'],flush=True)
    assert sum(p['blocks'] for p in previews)==data['blocks']
    assert history=={p.name:hashes(p) for p in [g.PRIOR,g.SWORD]}
    audit=dict(passed=True,readback=exported['readback'],hashes=exported['hashes'],viewer_rendered_quads=quads,
        no_nominal_clipping=True,animation_enabled=False,material_resource_sources=sources,enabled_resource_packs=packs,
        connectivity=data['connectivity'],anatomy=data['anatomy'],d1_unchanged=True,sword_s1_unchanged=True,
        reference_images=57,approved=False,installed=False,game_verified=False)
    data['component_bounds_blueprint']={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist(),blocks=len(p.p)) for p in parts}
    points=np.vstack([p.p for p in parts]);data['fit_points']=(points[ConvexHull(points).vertices]+offset).tolist()
    payload=dict(data=data,audit=audit,materials=materials,parts=previews)
    (view/'data.js').write_text('window.W04_STATIC_PAYLOAD='+json.dumps(base64.b64encode(gzip.compress(
        json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode())+';','utf8')
    source=(g.ROOT/'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110/生成脚本/viewer.mjs').read_text('utf8')
    source=source.replace("renderer.setClearColor('#18101c')","renderer.setClearColor('#15131b')")
    source=source.replace('0xe8f4ff,1.1','0xe8f4ff,1.0').replace('0xffffff,2','0xffffff,1.8').replace('0x8ed7ff,.9','0xffdbed,.65')
    source=source.replace("if(name==='back')direction.set(0,.15,-1);","if(name==='back')direction.set(0,.15,-1);\n    if(name==='underside')direction.set(.5,-.8,1.1);\n    if(name==='headfront')direction.set(0,0,1);\n    if(name==='headside')direction.set(1,.05,.1);\n    if(name==='head')direction.set(-1,.35,1.6);\n    if(name==='wing')direction.set(-.1,.3,1.5);\n    if(name==='wingback')direction.set(.2,.5,-1.4);\n    if(name==='feet')direction.set(-.8,.1,1.4);\n    if(name==='feetfront')direction.set(0,0,1);\n    if(name==='feetside')direction.set(1,0,0);\n    if(name==='tail')direction.set(1,.5,.3);")
    source=source.replace("function setView(name) {","let currentView='front';\n  function applyIsolation(){\n    const isolate=document.getElementById('isolate').checked;\n    groups.forEach(g=>{const detail=currentView.startsWith('head')?'01_':currentView==='chest'?'02_':currentView==='tail'?'03_':currentView.startsWith('feet')?'06_':currentView.startsWith('wing')?'wing':null;\n      const match=detail==='wing'?(g.name.startsWith('04_')||g.name.startsWith('05_')):detail?g.name.startsWith(detail):true;\n      const box=document.querySelector('[data-part=\"'+g.name+'\"]');g.visible=(!isolate||match)&&box.checked;});draw();\n  }\n  document.getElementById('isolate').onchange=applyIsolation;\n  function setView(name) {\n    currentView=name;applyIsolation();")
    source=source.replace("window.W04Static={config,scene,camera,renderer,controls,groups,setView,","window.W04Static={config,scene,camera,renderer,controls,groups,setView,applyIsolation,")
    start=source.index('    let limit=0;')
    end=source.index('\n  function resize()',start)
    source=source[:start]+'''    const points=[];
    if(detail){
      for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z])points.push(new THREE.Vector3(x,y,z));
    }else{
      for(const p of data.fit_points)for(const x of [0,1])for(const y of [0,1])for(const z of [0,1])points.push(new THREE.Vector3(p[0]+x,p[1]+y,p[2]+z));
    }
    let xmin=Infinity,xmax=-Infinity,ymin=Infinity,ymax=-Infinity;
    for(const p of points){p.project(camera);xmin=Math.min(xmin,p.x);xmax=Math.max(xmax,p.x);ymin=Math.min(ymin,p.y);ymax=Math.max(ymax,p.y);}
    const right=new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld,0),up=new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld,1);
    const shift=right.multiplyScalar((xmin+xmax)*(camera.right-camera.left)/4).add(up.multiplyScalar((ymin+ymax)*(camera.top-camera.bottom)/4));
    camera.position.add(shift);controls.target.add(shift);controls.update();
    camera.zoom=.88/Math.max((xmax-xmin)/2,(ymax-ymin)/2,.01);camera.updateProjectionMatrix();draw();
  }
''' +source[end:]
    (scripts/'viewer.mjs').write_text(source,'utf8')
    buttons=''.join(f'<button data-view="{key}">{label}</button>' for key,label in [
        ('front','完整斜视'),('orthofront','正面'),('side','侧面'),('back','背面'),('top','俯视'),('underside','腹面'),
        ('head','龙首近景'),('headfront','龙首正面'),('headside','龙首侧面'),('chest','颈腹叠甲'),('wing','翼爪正面'),
        ('wingback','翼膜背面'),('feet','腿爪斜视'),('feetfront','腿爪正面'),('feetside','腿爪侧面'),('tail','尾部')])
    checks=''.join(f'<label><input type="checkbox" checked data-part="{p.name}">{p.name}</label>' for p in parts)
    h=data['size'][1]
    (view/'三维评审.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title><style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#15131b;color:#f1e7eb;font:14px/1.7 system-ui}}header{{padding:12px 22px;background:#251820}}h1{{font-size:22px;margin:4px 0}}a{{color:#f19eb1}}button{{padding:7px 11px;margin:3px;background:#3d2430;border:1px solid #805364;border-radius:6px;color:inherit;cursor:pointer}}#stage{{height:72vh;min-height:420px;position:relative}}canvas{{display:block}}#loading{{position:absolute;left:22px;top:22px}}.tools{{padding:10px 22px}}label{{display:inline-block;margin:4px 16px 4px 0}}.refs{{display:flex;gap:20px;background:#251b24;padding:16px 24px}}.refs img{{max-width:32%;height:250px;object-fit:contain}}.note{{color:#c5b1be}}input[type=range]{{width:160px}}@media(max-width:800px){{#stage{{height:58vh}}.refs img{{height:140px}}}}</style>
<header><a href="../index.html">← 独立小样</a> · <a href="../参考图总览.html">57张参考图集</a><h1>{data['title']}</h1><p>双侧刃状翼前肢＋一对后足 · 长角V形面甲 · 暗色颈腹叠甲 · 红脊白刺细尾 · 无动画</p><div>{buttons}<button id="reset">复位</button></div></header><div id="stage"><div id="loading">加载完整静态表面…</div></div>
<div class="tools"><p id="stats"></p><label><input id="isolate" type="checkbox">近景仅显示选中部位</label><label hidden><input id="glass" type="checkbox" checked>玻璃</label><label hidden><input id="ports" type="checkbox">接口</label><label>剖切高度 <input id="layer" type="range" min="0" max="{h-1}" value="{h-1}"><span id="layerLabel">{h-1}</span></label><details><summary>9个独立部件显隐</summary>{checks}</details><p class="note">左键转镜头、右键平移、滚轮缩放。镜头可转，模型保持静止。背部遮挡连接与精确比例仍待核对；没有官方三视尺寸图。</p></div>
<div class="refs"><img src="../参考_龙首正面.jpg" alt="官方教学龙首正面局部"><img src="../参考_翼爪.jpg" alt="官方翼爪局部"><img src="../参考_后足.jpg" alt="游戏后足局部"></div><script src="data.js"></script><script src="viewer.bundle.js"></script></html>''','utf8')
    gallery=''.join(f'<figure><img src="{file}.png" alt="{label}"><figcaption>{label}</figcaption></figure>' for file,label in [
        ('正面','正面：白色长角、V形面甲与翼前肢'),('侧面','侧面：前探弯颈、短躯与细尾'),('背面','背面：翼膜、肩甲与尾脊'),('俯视','俯视：翼刃错层与完整长尾'),
        ('龙首正面','龙首正面：角根、额冠与红面甲'),('龙首侧面','龙首侧面：颊环、狭眼与闭合尖颚'),
        ('翼爪近景','翼爪：分体宽刃、白色嵌片与拇爪'),('翼膜背面','翼膜：暗色薄膜与凹边'),('颈腹近景','颈腹：分节护甲与V形胸甲'),('后足近景','后足：厚腿甲、宽爪掌与向下钩爪'),('腿爪正面','腿爪正面：三趾扇形分离'),('腿爪侧面','腿爪侧面：反折关节与下钩爪尖'),('尾部近景','尾部：红脊、骨白尾刺与收细尾尖')])
    w,h,d=data['size']
    (g.OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title><style>:root{{color-scheme:dark}}body{{max-width:1500px;margin:28px auto;padding:0 24px;background:#15131b;color:#eee5eb;font:16px/1.8 system-ui}}a{{color:#f1a0b3}}h1{{font-size:36px;margin:10px 0}}img{{width:100%;display:block}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0}}figcaption{{padding:8px}}.note{{border-left:3px solid #C93F63;padding:16px;background:#2a1923}}.refs img{{height:450px;object-fit:contain}}@media(max-width:800px){{.grid{{display:block}}}}</style><p>W04 部件逐个制作 · 龙本体 · 全静态</p><h1>俱利伽罗<br>腿爪与叠甲细化 D2</h1><p class="note">白色长角与V形红面甲、短躯弯颈、暗灰颈腹、两侧刃状翼前肢、粗壮折腿与宽爪掌和红脊白刺细尾。采用半展开悬停姿态；不带骑乘者或W04工业场景。</p>
<p><a href="dragon/三维评审.html">打开完整静态三维预览</a> · <a href="参考图总览.html">57张专属参考</a> · <a href="../{g.SWORD.name}/index.html">保留的鸣雷见S1</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p>
<img src="完整预览.png" alt="俱利伽罗独立静态小样完整预览"><p>实际宽{w} × 深{d} × 高{h}格，{data['blocks']:,}实体，9个部件。先完整生成后求实际包围盒，未用W04名义尺寸裁切。该比例用于独立细节评审，尚未安放进整机。</p><div class="grid refs"><figure><img src="参考_龙首正面.jpg" alt="龙首参考"><figcaption>官方教学：白色长角、灰色额冠与红色V形面甲</figcaption></figure><figure><img src="参考图/Kurikara_(Profile).jpg" alt="完整前侧参考"><figcaption>社区转存游戏画面：双翼刃爪与暗色颈腹</figcaption></figure></div>
<p>57张参考＝34张官方教学原帧＋8张玩家游戏原帧＋1张社区图＋13张玩家三维展示＋1张作者使用的游戏图，包含同镜头相邻动作；不宣称57个独立机位。局部裁图不重复计数。<a href="参考图清单.json">来源、时间点与原始尺寸</a>均保留。</p><p class="note">官方公开雷律人物包尚未确认包含龙体。已查到 <a href="https://www.artstation.com/artwork/n0bPo1">Terence Chong 的俱利伽罗三维作品</a>，含正、侧、背面与线框；作者明确为写实改编，仅辅助判断体积，未使用其网格。腿爪与装甲细节以原版游戏画面为主。</p><img src="腿爪D1_D2对照.png" alt="D1与D2同机位腿爪对照"><img src="腿爪参考对照.jpg" alt="游戏原帧与D2腿爪"><div class="grid">{gallery}</div>
<p class="note">无动画。精确比例、背部骑乘位遮挡连接及部分翼膜背纹仍为参考转译，外观待评审；未注册、未在游戏搭建或验证成型／运行。D1与七雷S1保持原文件。</p><p><a href="manifest.json">几何与部件</a> · <a href="verification.json">离线核验</a> · <a href="材料清单.json">材料清单</a> · <a href="dragon/{data['name']}.nbt">NBT</a> · <a href="dragon/{data['name']}.schem">Schematic</a></p></html>''','utf8')
    save(g.OUT/'manifest.json',data);save(g.OUT/'verification.json',audit)
    save(g.OUT/'材料清单.json',[dict(state=s,count=int(np.count_nonzero(cube==i+1)),role=g.ROLES[s]) for i,s in enumerate(g.STATES)])
    np.savez_compressed(g.LOG/'components.npz',**{p.name+'__'+k:v for p in parts for k,v in [('p',p.p),('states',p.states)]})
    for file in [Path(__file__),Path(g.__file__),g.ROOT/'tools/structure_delivery/collect_kurikara_d2_20261110.py',g.ROOT/'tools/structure_delivery/w04_kurikara_d1_20261110.py',
        g.ROOT/'tools/structure_delivery/w04_kurikara_d1_parts_20261110.py',g.ROOT/'tools/structure_delivery/w04_kurikara_d1_head_wings_20261110.py',g.ROOT/'tools/structure_delivery/w04_kurikara_d1_body_20261110.py']:
        shutil.copy2(file,scripts/file.name)
    print(json.dumps(dict(passed=True,size=data['size'],blocks=data['blocks'],quads=quads,prior_unchanged=True)))


if __name__=='__main__':main()
