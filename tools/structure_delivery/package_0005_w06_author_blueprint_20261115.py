import base64
from datetime import datetime
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
import author_w06_base_rings_20261115 as base_rings
import author_w06_core_20261115 as core_geometry
import package_0005_w05_author_blueprint_20261115 as shared

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W06_作者蓝图原案_20261115'
LOG=ROOT/'logs/0005-w06-author-blueprint-20261115'
TITLE='W06 · 冰之律者 · 安娜之冕·绝对零度圣枪阵列'
VIEWS={
    'front':dict(label='前左全景',center=[401,190,361],direction=[-1,.68,-1.3]),
    'right':dict(label='前右全景',center=[401,190,361],direction=[1,.68,-1.3]),
    'front_ortho':dict(label='正面投影',center=[401,190,361],direction=[0,.001,-1]),
    'side':dict(label='侧面投影',center=[401,190,361],direction=[1,0,0]),
    'back':dict(label='背面全景',center=[401,190,361],direction=[.8,.6,1.2]),
    'top':dict(label='俯视全景',center=[401,190,361],direction=[0,1,.0001]),
    'lotus':dict(label='十二瓣机械冰莲',center=[401,165,361],direction=[-1,.7,-1.2],half=[260,180,260]),
    'prism':dict(label='八面体棱镜与黑金律者核心',center=[401,180,361],direction=[-1,.7,-1.2],half=[100,100,100]),
    'rings':dict(label='三道暴风雪星环',center=[401,190,361],direction=[-.8,.6,-1.3],half=[410,260,410]),
    'crown':dict(label='倒置冰晶王冠与聚焦天柱',center=[401,320,361],direction=[-1,.7,-1.2],half=[190,120,190]),
    'spears':dict(label='十二座环绕冰枪',center=[401,318,361],direction=[-.8,.55,-1.3],half=[300,125,300]),
    'controller':dict(label='正南端主控观景台',center=[401,45,700],direction=[.2,.65,-1],half=[100,55,100]),
}

def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')

def payload(data,parts,materials):
    render_materials=[dict(m,texture='data:image/png;base64,'+base64.b64encode((OUT/m['texture']).read_bytes()).decode()) for m in materials]
    packed=gzip.compress(json.dumps(dict(data=data,parts=parts,materials=render_materials),ensure_ascii=False,separators=(',',':')).encode(),compresslevel=6,mtime=0)
    (OUT/'data.js').write_text('window.W06_AUTHOR_PAYLOAD='+json.dumps(base64.b64encode(packed).decode())+';','utf8')
    return len(packed)

def write_pages(data,parts,manifest,conflicts,interpretations,materials):
    buttons=''.join(f'<button data-view="{key}">{v["label"]}</button>' for key,v in VIEWS.items())
    part_rows=''.join(f'<label><input type="checkbox" checked data-part="{p["id"]}">{escape(p["label"])}<small>{p["blocks"]:,} 格</small></label>' for p in parts)
    mat_rows=''.join(f'<label class="material"><input type="checkbox" checked data-material="{i}"><img src="{m["texture"]}"><span>{escape(m["label"])}<small>{manifest["material_counts"][str(i+1)]:,} 构件内格</small></span></label>' for i,m in enumerate(materials))
    css='''*{box-sizing:border-box}body{margin:0;background:#101920;color:#e3edf1;font:14px/1.6 "Microsoft YaHei",sans-serif}a{color:#9de8f3}header{padding:12px 20px;border-bottom:1px solid #3e5662;background:#17242d}h1{font-size:21px;margin:2px 0 4px}header p{margin:2px 0;color:#adc1ca}.layout{display:grid;grid-template-columns:minmax(0,1fr) 360px;height:calc(100vh - 108px);min-height:650px}#stage{position:relative;min-width:0;overflow:hidden;background:#101920}canvas{display:block}#loading{position:absolute;inset:45% 8%;text-align:center;color:#c1f6ff;z-index:5}aside{padding:14px;overflow:auto;border-left:1px solid #3e5662;background:#17242d}button,select{background:#263a44;color:#e3f5fa;border:1px solid #4a6977;border-radius:4px;padding:7px 9px;margin:3px;cursor:pointer}button:hover,button.active{background:#385965;border-color:#9de8f3}select{width:100%}label{display:block;padding:4px 0}label small{display:block;color:#afc9d3;font-size:11px;margin-left:21px}input[type=checkbox],input[type=range]{accent-color:#82deeb}.notice{padding:10px;background:#203c47;border-left:3px solid #7cd7e5;font-size:12px;margin:9px 0}.warn{background:#42382c;border-color:#e2bd77}.toolbar{display:flex;flex-wrap:wrap;gap:0 9px;font-size:12px}details{border-top:1px solid #3e5662;padding:9px 0}summary{cursor:pointer;font-weight:600;color:#c5eff4}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.6 "Microsoft YaHei",sans-serif}.material{display:flex;align-items:center;gap:7px}.material img{width:38px;height:38px;image-rendering:pixelated}.material small{margin:0}.hint{font-size:11px;color:#a8c1cb}#viewName{font-size:17px;color:#d0f7fb;margin:0 0 8px}.badge{display:inline-block;font-size:11px;padding:2px 7px;border:1px solid #62838c;border-radius:3px;color:#c0ebf0}.gallery{max-width:1500px;margin:26px auto;padding:0 20px}.gallery img{width:100%;border:1px solid #3e5662}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0 0 16px}figcaption{padding:6px;color:#adc6cf}@media(max-width:950px){.layout{display:flex;flex-direction:column;height:auto}#stage{height:68vh}aside{max-height:none}.grid{grid-template-columns:1fr}}'''
    conflicts_html=escape(json.dumps(conflicts,ensure_ascii=False,indent=2))
    sampling_html=escape(json.dumps(interpretations,ensure_ascii=False,indent=2))
    notice='明确尺寸、位置、数量与材质外观按原文保留。原文未规定的曲线采样及互相冲突的数量／边界在记录中单列；几何未裁切、未移位。此为网页体素预览，不代表已注册八种游戏方块。'
    review=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>{TITLE} · 原文蓝图预览</title><style>{css}</style><header><span class="badge">0005 多方块设计 · 原文蓝图独立预览</span><h1>{TITLE}</h1><p>名义801×721×382 · 完整实际整数格边界 {manifest['size_wdh'][0]}×{manifest['size_wdh'][1]}×{manifest['size_wdh'][2]} · {len(parts)}个独立构件 · 8种专用预览材质</p><p><a href="index.html">静态图集</a> · <a href="原文与取样.html">原文冲突与取样</a> · <a href="manifest.json">构件和材料记录</a></p></header><main class="layout"><section id="stage"><div id="loading">载入完整原文蓝图…</div></section><aside><div id="viewName"></div><div class="notice">{notice}</div><select id="mode"><option value="idle">待机 · 冰晶与极光</option><option value="work">工作 · 通天光柱／金色星芒暴风雪</option></select><p id="modeName">待机 · 缓速运行</p><button id="pause">暂停动画</button><span id="timeValue">0.0 s</span><input id="time" type="range" min="0" max="60" step=".1" value="0"><div>{buttons}</div><p class="hint">左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 Y=<b id="layerValue">{data['bounds']['max'][1]}</b><input id="layer" type="range" min="{data['bounds']['min'][1]}" max="{data['bounds']['max'][1]}" value="{data['bounds']['max'][1]}"></label><div class="toolbar"><label><input id="effects" type="checkbox" checked>风雪与星芒</label><label><input id="bloom" type="checkbox" checked>Bloom</label><label><input id="showGrid" type="checkbox">坐标网格</label><label><input id="showBounds" type="checkbox">名义边界</label><label><input id="ports" type="checkbox">主控定位</label></div><button id="reset">复位全景</button><button id="saveImage">保存视角</button><button id="fullscreen">全屏</button><p id="counts" class="hint"></p><div class="notice warn">保留原文的越界和构件交叠，不以裁切、删件或挪位消除。显示范围根据完整实体边界取值；名义范围可另行显示对照。</div><details><summary>八种专用预览材质</summary>{mat_rows}<p class="hint">仅网页贴图；没有注册或新增游戏方块。</p></details><details open><summary>{len(parts)}个独立构件</summary><button id="allParts">全部显示</button>{part_rows}</details><details><summary>原文冲突／歧义</summary><pre>{conflicts_html}</pre></details><details><summary>离散化取样</summary><pre>{sampling_html}</pre></details><details><summary>坐标与边界</summary><pre>{escape(json.dumps(data['bounds'],ensure_ascii=False,indent=2))}</pre></details></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''
    (OUT/'三维评审.html').write_text(review,'utf8')
    filenames={key:f'{key}.png' for key in VIEWS}
    gallery=''.join(f'<figure><img loading="lazy" src="{filenames[k]}" alt="{v["label"]}"><figcaption>{v["label"]}</figcaption></figure>' for k,v in VIEWS.items() if k!='front')
    index=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>{TITLE}</title><style>{css}</style><div class="gallery"><span class="badge">0005 · 按原文完整转译 · 静态网页预览</span><h1>{TITLE}</h1><p>名义801×721×382；实际完整实体范围 {manifest['size_wdh'][0]}×{manifest['size_wdh'][1]}×{manifest['size_wdh'][2]}。{len(parts)}个构件，{manifest['source_component_voxels']:,}构件内格，{manifest['unique_occupied_voxels']:,}唯一占格。</p><p><a href="三维评审.html">打开可交互三维预览 · 待机／工作切换 · 分层剖切 →</a> · <a href="原文与取样.html">查看原文与取样记录</a></p><div class="notice">{notice} 八种专用材质是本预览的纹理，不是已注册的 Minecraft 方块。</div><figure><img src="front.png" alt="冰律毕业多方块整机全景"><figcaption>完整构图</figcaption></figure><div class="grid">{gallery}</div><p><a href="manifest.json">构件统计</a> · <a href="构件交叠记录.json">交叠记录</a> · <a href="材料清单.json">材料清单</a> · <a href="原文.md">原始方案文本</a></p><p class="hint">对话ID：01a1d6b8-bd81-79d3-a6f4-4f590806cc8e · 不修改A3候选、游戏源码或运行蓝图。</p></div></html>'''
    (OUT/'index.html').write_text(index,'utf8')
    source=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><link rel="icon" href="data:,"><title>W06原文与取样</title><style>{css}</style><div class="gallery"><p><a href="三维评审.html">返回三维预览</a></p><h1>原文、冲突与离散化取样</h1><div class="notice">用户提供的蓝图正文原样保存于 <a href="原文.md">原文.md</a>。以下记录明确分开原文事实与为渲染所需的整数格取样。</div><h2>原文内冲突</h2><pre>{conflicts_html}</pre><h2>离散化取样</h2><pre>{sampling_html}</pre><h2>实际实体范围</h2><pre>{escape(json.dumps(data['bounds'],ensure_ascii=False,indent=2))}</pre></div></html>'''
    (OUT/'原文与取样.html').write_text(source,'utf8')

def main():
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True);(OUT/'materials').mkdir(exist_ok=True);(OUT/'生成脚本').mkdir(exist_ok=True)
    source_text=(OUT/'原文.md').read_text('utf8')
    materials=json.loads((OUT/'materials/materials.json').read_text('utf8'))
    parts_a,conflicts_a=base_rings.build();parts_b,conflicts_b=core_geometry.build();parts=parts_a+parts_b
    low=np.min([p.p.min(0) for p in parts],axis=0);high=np.max([p.p.max(0) for p in parts],axis=0);w,h,d=map(int,high-low+1)
    owner=np.zeros(w*h*d,np.uint16);counts=np.zeros(9,np.int64);overlaps=[];archive={};preview=[];total_faces=total_quads=0
    for index,p in enumerate(parts,1):
        local=p.p-low;keys=(local[:,1]*d+local[:,2])*w+local[:,0];previous=owner[keys];hit=previous>0
        if hit.any():
            ids,n=np.unique(previous[hit],return_counts=True)
            overlaps.extend(dict(first_component=parts[int(j)-1].name,later_component=p.name,coincident_voxels=int(c)) for j,c in zip(ids,n))
        owner[keys[~hit]]=index;counts+=np.bincount(p.states,minlength=9);archive[p.name+'_xyz']=p.p;archive[p.name+'_materials']=p.states
        item,faces,quads=shared.mesh_part(p,materials);preview.append(item);total_faces+=faces;total_quads+=quads
        print(f'压缩表面 {index}/{len(parts)} {p.name} {quads:,}',flush=True)
    unique=int(np.count_nonzero(owner));del owner
    np.savez_compressed(OUT/'原始构件数据.npz',**archive)
    conflicts=conflicts_a+conflicts_b
    data=dict(title=TITLE,center=[401,0,361],bounds=dict(min=low.tolist(),max=high.tolist()),nominal_size_wdh=[801,721,382],nominal_bounds_xyz=dict(min=[1,0,1],max=[801,382,721]),controller=[401,45,700],views=VIEWS,
        interpretations=conflicts,material_scope='原文要求的八种专用外观材质，仅用于本网页；未注册为游戏方块。')
    packed_size=payload(data,preview,materials)
    components=[{k:v for k,v in p.items() if k not in ('starts','lengths')} for p in preview]
    manifest=dict(title=TITLE,candidate='用户原文完整几何转译独立预览',created_at=datetime.now().astimezone().isoformat(timespec='seconds'),conversation='0005',conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
        source='用户于2026-11-15直接提供的W06冰之律者毕业多方块完整蓝图文本：原文.md',source_sha256=hashlib.sha256(source_text.encode('utf8')).hexdigest(),nominal_size_wdh=[801,721,382],size_wdh=[w,d,h],occupied_bounds_xyz=data['bounds'],nominal_bounds_xyz=data['nominal_bounds_xyz'],coordinates_preserved=True,
        source_component_voxels=int(counts.sum()),unique_occupied_voxels=unique,overlap_extra_memberships=int(counts.sum())-unique,material_counts={str(i):int(counts[i]) for i in range(1,9)},material_count=8,components=components,
        preview=dict(integer_voxels=True,independent_parts=True,rendered_surface_faces=total_faces,merged_quads=total_quads,payload_gzip_bytes=packed_size,real_block_textures=False,idle_and_work_animations=True,effects_scope='网页演示；未注册方块或实现游戏BER、天气、天空盒'),
        geometry_constraints='按实际几何导出，不按名义边界裁切；原文坐标和构件交叠保留。',appearance_approved=False,runtime_blueprint_modified=False,game_code_modified=False,jar_built=False,installed=False,desktop_used=False,game_started=False,game_verified=False,automated_tests_run=False,acceptance_score_changed=False)
    save(OUT/'manifest.json',manifest);save(LOG/'generation.json',manifest)
    overlap_record=dict(unique_occupied_voxels=unique,extra_component_memberships=int(counts.sum())-unique,pairs=overlaps,note='各构件按原文设计独立保留；重合只是客观占格记录，不擅自判定为应删除或修复的穿模。')
    save(OUT/'构件交叠记录.json',overlap_record)
    save(OUT/'材料清单.json',dict(materials=materials,material_counts=manifest['material_counts'],new_game_materials_registered=0))
    write_pages(data,components,manifest,dict(source_conflicts=conflicts),conflicts,materials)
    for file in ['author_w06_base_rings_20261115.py','author_w06_core_20261115.py','author_w06_viewer_20261115.mjs','author_w06_effects_20261115.mjs','bundle_0005_w06_author_blueprint_20261115.mjs',Path(__file__).name]:
        shutil.copy2(ROOT/'tools/structure_delivery'/file,OUT/'生成脚本'/file)
    subprocess.run(['node',str(ROOT/'tools/structure_delivery/bundle_0005_w06_author_blueprint_20261115.mjs')],cwd=ROOT,check=True)
    print(json.dumps(dict(output=str(OUT),bounds=data['bounds'],size_wdh=manifest['size_wdh'],parts=len(parts),source_voxels=manifest['source_component_voxels'],unique_voxels=unique,overlap_pairs=len(overlaps)),ensure_ascii=False),flush=True)

if __name__=='__main__':main()
