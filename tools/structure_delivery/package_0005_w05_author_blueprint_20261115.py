import base64
from datetime import datetime
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import shutil

import numpy as np

import author_w05_axis_20261115 as axis
import author_w05_wings_20261115 as wings
from package_0005_i37_suspended_test_dock_a2_20261115 import runs


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W05_作者蓝图原案_20261115'
LOG=ROOT/'logs/0005-w05-author-blueprint-20261115'
TITLE='W05 · 风之律者 · 长风·理想流体环流阵'
VIEWS={
    'front':dict(label='前左全景',center=[0,160,0],direction=[-1,.72,-1.25]),
    'right':dict(label='前右全景',center=[0,160,0],direction=[1,.72,-1.25]),
    'orthofront':dict(label='正面投影',center=[0,160,0],direction=[0,.001,-1]),
    'side':dict(label='侧面投影',center=[0,160,0],direction=[1,0,0]),
    'back':dict(label='尾部全景',center=[0,160,0],direction=[.8,.6,1.2]),
    'top':dict(label='俯视全景',center=[0,160,0],direction=[0,1,.0001]),
    'intake':dict(label='三组反转涡轮',center=[0,160,-240],direction=[-.18,.23,-1],half=[104,103,126]),
    'core':dict(label='开放奇点与八轨',center=[0,160,0],direction=[-1,.5,-1.2],half=[102,94,126]),
    'wing':dict(label='莫比乌斯管网与三副塔',center=[-175,175,10],direction=[-1,1,-.75],half=[110,135,277]),
    'crown':dict(label='三层倾斜王冠',center=[0,290,0],direction=[-1,.9,-1],half=[143,48,143]),
    'exhaust':dict(label='十二瓣尾喷与机械羽',center=[0,160,240],direction=[.65,.46,1],half=[98,95,118]),
    'controller':dict(label='前主控与接口',center=[0,17,-333],direction=[.3,.8,-1],half=[184,36,49]),
}


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


def write_payload(data,parts,materials):
    render_materials=[dict(m,texture='data:image/png;base64,'+base64.b64encode((OUT/m['texture']).read_bytes()).decode()) for m in materials]
    payload=dict(data=data,parts=parts,materials=render_materials)
    packed=gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),compresslevel=6,mtime=0)
    (OUT/'data.js').write_text('window.W05_AUTHOR_PAYLOAD='+json.dumps(base64.b64encode(packed).decode())+';','utf8')
    return len(packed)


def mesh_part(p,materials):
    low,high=p.p.min(0),p.p.max(0)
    size=high-low+1
    w,h,d=map(int,size)
    cube=np.zeros((h,d,w),np.uint8)
    local=p.p-low
    cube[local[:,1],local[:,2],local[:,0]]=p.states
    occupied=cube>0
    transparent=np.array([False,*[m['transparent'] for m in materials]])
    glass=transparent[cube]
    starts=[[[] for _ in range(6)] for _ in materials]
    lengths=[[[] for _ in range(6)] for _ in materials]
    faces=quads=0
    for face,dim,sign in [(0,2,1),(1,2,-1),(2,1,1),(3,1,-1),(4,0,-1),(5,0,1)]:
        neighbor=np.zeros_like(cube)
        destination,source=[slice(None)]*3,[slice(None)]*3
        destination[dim],source[dim]=((slice(None,-1),slice(1,None)) if sign>0 else (slice(1,None),slice(None,-1)))
        neighbor[tuple(destination)]=cube[tuple(source)]
        visible=occupied&((neighbor==0)|(transparent[neighbor]&~glass))
        indices=np.flatnonzero(visible.ravel())
        values=cube.ravel()[indices]
        faces+=len(indices)
        for m in range(len(materials)):
            selected=indices[values==m+1]
            if len(selected):
                s,l=runs(selected,[w,h,d],face)
                starts[m][face],lengths[m][face]=s,l
                quads+=len(s)
    return dict(id=p.name,label=p.label,origin=low.tolist(),size=[w,h,d],blocks=len(p.p),
                metadata=p.metadata,starts=starts,lengths=lengths),faces,quads


def html_pages(data,parts,manifest,constraints,interpretations,materials):
    buttons=''.join(f'<button data-view="{key}">{v["label"]}</button>' for key,v in VIEWS.items())
    part_rows=''.join(f'<label><input type="checkbox" checked data-part="{p["id"]}">{escape(p["label"])}<small>{p["blocks"]:,} 格</small></label>' for p in parts)
    mat_rows=''.join(f'<label class="material"><input type="checkbox" checked data-material="{i}"><img src="{m["texture"]}"><span>{escape(m["label"])}<small>{manifest["material_counts"][str(i+1)]:,} 构件内方块</small></span></label>' for i,m in enumerate(materials))
    conflicts=escape(json.dumps(constraints['source_conflicts_and_ambiguities'],ensure_ascii=False,indent=2))
    sampling=escape(json.dumps(interpretations,ensure_ascii=False,indent=2))
    w,d,h=manifest['size_wdh']
    css='''*{box-sizing:border-box}body{margin:0;background:#0b161b;color:#dcece9;font:14px/1.65 "Microsoft YaHei",sans-serif}a{color:#80e6ca}header{padding:14px 24px;border-bottom:1px solid #274341;background:#111f24}h1{font-size:21px;margin:2px 0 5px}header p{margin:2px 0;color:#a5c3bd}.layout{display:grid;grid-template-columns:minmax(0,1fr) 355px;height:calc(100vh - 112px);min-height:700px}#stage{position:relative;min-width:0;overflow:hidden;background:#0b161b}canvas{display:block}#loading{position:absolute;inset:45% 10%;text-align:center;color:#8aedd2;z-index:5}aside{padding:16px;overflow:auto;border-left:1px solid #274341;background:#101f24}button,select{background:#1b3236;color:#d7f2ea;border:1px solid #345652;border-radius:4px;padding:7px 9px;margin:3px 3px 3px 0;cursor:pointer}button:hover,button.active{background:#285346;border-color:#5fc9a6}select{width:100%}label{display:block;padding:4px 0}label small{display:block;color:#82aaa0;font-size:11px;margin-left:21px}input[type=checkbox]{accent-color:#73e1bf}input[type=range]{width:100%;accent-color:#6fdabc}.notice{padding:11px;background:#173532;border-left:3px solid #66cba9;font-size:12px;margin:9px 0}.warn{background:#382f23;border-color:#d6ae6f}.toolbar{display:flex;flex-wrap:wrap;gap:0 9px;font-size:12px}details{border-top:1px solid #294541;padding:10px 0}summary{cursor:pointer;font-weight:600;color:#b4e4d6}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.65 "Microsoft YaHei",sans-serif}.material{display:flex;align-items:center;gap:7px}.material img{width:38px;height:38px;image-rendering:pixelated}.material small{margin:0}.hint{font-size:11px;color:#89aaa3}#viewName{font-size:17px;color:#a1efd7;margin:0 0 8px}.badge{display:inline-block;font-size:11px;letter-spacing:.08em;padding:2px 7px;border:1px solid #3d6d5f;border-radius:3px;color:#93d9c3}.inline{display:flex;gap:8px;align-items:center}.inline input{flex:1}.gallery{max-width:1500px;margin:30px auto;padding:0 20px}.gallery img{width:100%;border:1px solid #294541}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0 0 18px}figcaption{padding:6px;color:#9bbcb2}.source{padding:20px;max-width:1000px;margin:auto} @media(max-width:950px){.layout{display:flex;flex-direction:column;height:auto}#stage{height:68vh}aside{max-height:none}.grid{grid-template-columns:1fr}}'''
    review=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>{TITLE} · 作者蓝图预览</title><style>{css}</style>
<header><span class="badge">0005 多方块设计 · 作者原案独立预览</span><h1>{TITLE}</h1><p>名义555×700×320 · 原文坐标整数格包围盒 {w}×{d}×{h} · {len(parts)}构件 · 7种预览专用材质</p><p><a href="index.html">静态图集</a> · <a href="原文与取样.html">原文、冲突与取样参数</a> · <a href="manifest.json">完整构件记录</a></p></header>
<main class="layout"><section id="stage"><div id="loading">加载完整作者蓝图…</div></section><aside>
<div id="viewName"></div><div class="notice">按原文保留双翼莫比乌斯风洞、中轴风暴炉、480×680底座及指定主控坐标。原文没给出的曲线、角度与叶数属于预览取样，已逐项公开。</div>
<select id="mode"><option value="idle">待机 · 涡轮与核心陀螺仪缓转</option><option value="work">工作 · 流光回旋／白色风眼／王冠风柱</option></select><p id="modeName">待机 · 缓速运行</p><button id="pause">暂停动画</button><span id="timeValue">0.0 s</span><input id="time" type="range" min="0" max="60" step=".1" value="0"><div>{buttons}</div><p class="hint">左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 Y=<b id="layerValue">{data['bounds']['max'][1]}</b><input id="layer" type="range" min="0" max="{data['bounds']['max'][1]}" value="{data['bounds']['max'][1]}"></label>
<div class="toolbar"><label><input id="effects" type="checkbox" checked>光幕与流场</label><label><input id="bloom" type="checkbox" checked>Bloom</label><label><input id="showGrid" type="checkbox">坐标网格</label><label><input id="showBounds" type="checkbox">原文范围</label><label><input id="ports" type="checkbox">主控定位</label></div>
<button id="reset">复位全景</button><button id="saveImage">保存视角</button><button id="fullscreen">全屏</button><p id="counts" class="hint"></p>
<div class="notice warn">原文自身的尺寸差异与构件重合照实保留，未通过移位、删件或裁切处理。独立分组可逐一隐藏。重合记录包含正常连接，不能直接当作全部碰撞错误。</div>
<details><summary>七种专用预览材质</summary>{mat_rows}<p class="hint">材质贴图与动态均仅供本网页预览；尚未注册游戏方块或BER。</p></details>
<details open><summary>{len(parts)}个独立构件</summary><button id="allParts">全部显示</button>{part_rows}</details>
<details><summary>原文冲突与歧义</summary><pre>{conflicts}</pre></details><details><summary>原文未指定参数的预览取样</summary><pre>{sampling}</pre></details>
<details><summary>来源与状态</summary><p>原文SHA256：{constraints['source']['sha256']}</p><p>待机／工作为网页演示。未覆盖已批准W05 A4，未修改游戏代码，未构建、安装或运行JAR，不改变批准状态及验收分。</p><p><a href="作者原文.md">原始MD</a> · <a href="原始构件数据.npz">原始整数格构件</a> · <a href="原文落实记录.json">条目与构件映射</a> · <a href="构件重合记录.json">重合记录</a></p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''
    (OUT/'三维评审.html').write_text(review,'utf8')
    filenames={'front':'整体预览.png','right':'前右预览.png','orthofront':'正面预览.png','side':'侧面预览.png','back':'背面预览.png','top':'俯视预览.png',
               'intake':'进气口近景.png','core':'核心近景.png','wing':'双翼管网近景.png','crown':'王冠近景.png','exhaust':'尾喷近景.png','controller':'主控近景.png'}
    gallery=''.join(f'<figure><img loading="lazy" src="{filenames[k]}" alt="{v["label"]}"><figcaption>{v["label"]}</figcaption></figure>' for k,v in VIEWS.items() if k!='front')
    index=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>{TITLE}</title><style>{css}</style><div class="gallery"><span class="badge">0005 · 作者蓝图原案 · 独立预览</span><h1>{TITLE}</h1><p>名义宽555×深700×高320；完整整数格边界X{data['bounds']['min'][0]}..{data['bounds']['max'][0]}，Z{data['bounds']['min'][2]}..{data['bounds']['max'][2]}，Y{data['bounds']['min'][1]}..{data['bounds']['max'][1]}。{len(parts)}个独立构件，{manifest['source_component_voxels']:,}构件内方块（含不同构件重合）。</p><p><a href="三维评审.html">打开三维预览：待机／工作、分组与剖切 →</a> · <a href="原文与取样.html">查看原文与取样依据</a></p><div class="notice">原文坐标、数量、外观分区与七种材料身份保留。未明确给出的逐格曲线和倾角为可追溯预览取样；原文冲突未私自修正。没有覆盖既有W05 A4，也未进行游戏实装。</div><figure><img src="整体预览.png" alt="作者蓝图原案前左完整预览"><figcaption>完整构图 · 待机状态</figcaption></figure><figure><img src="满载工作预览.png" alt="MAX+满载工作演示"><figcaption>MAX+满载演示 · 中轴吸入 → 双翼管网 → 矢量尾喷，中央白色风眼与王冠风柱</figcaption></figure><div class="grid">{gallery}</div><p><a href="manifest.json">构件及材料统计</a> · <a href="原文落实记录.json">原文条目映射</a> · <a href="构件重合记录.json">原坐标重合记录</a> · <a href="原始构件数据.npz">原始整数格构件</a></p><p class="hint">对话ID：01a1d6b8-bd81-79d3-a6f4-4f590806cc8e · 本次没有构建、安装或运行JAR。</p></div></html>'''
    (OUT/'index.html').write_text(index,'utf8')
    source=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><link rel="icon" href="data:,"><title>W05作者原文与预览取样</title><style>{css}</style><div class="source"><p><a href="三维评审.html">返回三维预览</a></p><h1>原文冻结与实现边界</h1><p>SHA256：{constraints['source']['sha256']}</p><details open><summary>原文未指定参数的预览取样</summary><pre>{sampling}</pre></details><details><summary>原文冲突和歧义</summary><pre>{conflicts}</pre></details><h2>作者原文（原样显示）</h2><pre>{escape((OUT/'作者原文.md').read_text('utf8'))}</pre></div></html>'''
    (OUT/'原文与取样.html').write_text(source,'utf8')


def main():
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
    (OUT/'生成脚本').mkdir(exist_ok=True)
    materials=json.loads((OUT/'materials/materials.json').read_text('utf8'))
    constraints=json.loads((OUT/'constraints.json').read_text('utf8'))
    print('生成作者原案：底座与中轴',flush=True)
    parts,interpretations=axis.build()
    print('生成作者原案：双翼与王冠',flush=True)
    wing_parts,wing_interpretations=wings.build();parts+=wing_parts;interpretations+=wing_interpretations
    low=np.min([p.p.min(0) for p in parts],axis=0);high=np.max([p.p.max(0) for p in parts],axis=0)
    w,h,d=map(int,high-low+1)
    owner=np.zeros(w*h*d,np.uint8)
    overlaps=[];counts=np.zeros(8,np.int64);archive={};preview=[];total_faces=total_quads=0
    for i,p in enumerate(parts,1):
        q=p.p-low;keys=(q[:,1]*d+q[:,2])*w+q[:,0]
        previous=owner[keys];hit=previous>0
        if hit.any():
            ids,n=np.unique(previous[hit],return_counts=True)
            overlaps.extend(dict(first_component=parts[int(j)-1].name,later_component=p.name,coincident_voxels=int(c)) for j,c in zip(ids,n))
        owner[keys[~hit]]=i
        counts+=np.bincount(p.states,minlength=8)
        archive[p.name+'_xyz']=p.p;archive[p.name+'_materials']=p.states
        item,faces,quads=mesh_part(p,materials);preview.append(item);total_faces+=faces;total_quads+=quads
        print(f'压缩表面 {i}/{len(parts)} {p.name} {quads:,}',flush=True)
    unique=int(np.count_nonzero(owner));del owner
    np.savez_compressed(OUT/'原始构件数据.npz',**archive)
    data=dict(title=TITLE,bounds=dict(min=low.tolist(),max=high.tolist()),nominal_size_wdh=[555,700,320],controller=[0,12,-345],views=VIEWS,
              material_scope='七种作者指定的预览专用材质；未注册游戏资源。',source=constraints['source'],interpretations=interpretations)
    packed_bytes=write_payload(data,preview,materials)
    components=[{k:v for k,v in p.items() if k not in ('starts','lengths')} for p in preview]
    manifest=dict(title=TITLE,candidate='作者蓝图原案独立预览',created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        conversation='0005',conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',source=constraints['source'],
        nominal_size_wdh=[555,700,320],size_wdh=[w,d,h],occupied_bounds_xyz=data['bounds'],coordinates_preserved=True,
        source_component_voxels=int(counts.sum()),unique_occupied_voxels=unique,overlap_extra_memberships=int(counts.sum())-unique,
        material_counts={str(i):int(counts[i]) for i in range(1,8)},material_count=7,components=components,
        preview=dict(integer_voxels=True,independent_parts=True,rendered_surface_faces=total_faces,merged_quads=total_quads,
                     payload_gzip_bytes=packed_bytes,idle_and_work_animations=True,effects_scope='网页预览；未实现游戏BER。'),
        geometry_constraints='不按名义边界裁切；构件各自保留，不通过移位、删件或覆盖另一个构件来消解重合。',
        appearance_approved=False,existing_w05_a4_replaced=False,game_code_modified=False,jar_built=False,installed=False,
        desktop_used=False,game_started=False,game_verified=False,automated_tests_run=False,acceptance_score_changed=False)
    overlap_record=dict(note='按原坐标记录，不自动修正。包含正常连接；首占构件法只归因于该格最先出现的构件，不是全部成对交集或动态扫掠证明。',
                        unique_occupied_voxels=unique,extra_component_memberships=int(counts.sum())-unique,pairs=overlaps)
    mapping=dict(source=constraints['source'],components=components,interpretations=interpretations,
                 rendering=[dict(item='待机',implementation='三组相邻反转主涡轮；核心微浮与双陀螺仪自转。'),
                    dict(item='工作流线',implementation='前口至核心，沿真实双翼管网采样曲线绕行，再汇入尾部；速度仅作演示。'),
                    dict(item='核心工作态',implementation='纯白风眼与三道透明物理折射材质气旋；不是游戏Shader实现。'),
                    dict(item='王冠与风柱',implementation='三倾斜环加速，半透明光幕与至基座的青色龙卷。'),
                    dict(item='尾喷及翼尖',implementation='青白激波环与向中央的翠绿电弧；渲染曲线取样。')])
    save(OUT/'manifest.json',manifest);save(OUT/'构件重合记录.json',overlap_record);save(OUT/'原文落实记录.json',mapping)
    save(LOG/'generation.json',manifest)
    html_pages(data,preview,manifest,constraints,interpretations,materials)
    for name in ['author_w05_shapes_20261115.py','author_w05_axis_20261115.py','author_w05_wings_20261115.py',
                 'author_w05_effects_20261115.mjs','author_w05_viewer_20261115.mjs',Path(__file__).name]:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    shutil.copy2('C:/Users/OWNER/.codex/skills/minecraft-builder-skill/node_modules/three/LICENSE',OUT/'Three许可.txt')
    print(json.dumps(dict(output=str(OUT),size_wdh=[w,d,h],parts=len(parts),voxels=int(counts.sum()),unique=unique,quads=total_quads),ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
