# -*- coding: utf-8 -*-
"""导出19C多视角重制，所有构件完整保留，参考页与静态预览同目录。"""
import base64
from datetime import datetime,timezone,timedelta
import gzip
from html import escape
import io
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image,ImageStat
import w02_19c_geometry_v2_20261110 as g
from build_i25_world_bubble_observatory_20261025 import resource_materials
from i34_open_observatory_export_20261027 import export_dense,surface_groups
from i37_surface_runs_20261027 import merge_surface_runs


def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


def main(geometry=None):
    g=geometry or globals()['g']
    refs=json.loads((g.OUT/'参考图清单.json').read_text('utf8'))
    assert refs['count']==60 and refs['official_count']==32
    cube,data,parts=g.build();assert len(parts)==getattr(g,'EXPECTED_PARTS',11) and not data['animation_enabled']
    counts=np.bincount(cube.ravel(),minlength=len(g.STATES)+1)
    assert np.all(counts[1:]),'所有列出的材质必须实际使用'
    offset=np.array(data['blueprint_to_export_offset_xyz']);size=np.array(data['size'])
    for p in parts:
        at=p.p+offset;assert np.all(at>=0) and np.all(at<size)
    view=g.OUT/'w02';view.mkdir(exist_ok=True)
    scripts=g.OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    print('导出多视角19C。',flush=True)
    exported=export_dense(cube,g.STATES,data['name'],view)
    materials,sources,packs=resource_materials(g.STATES)
    previews=[];quads=0
    for p in parts:
        lo,hi=p.p.min(0),p.p.max(0);extent=hi-lo+1
        local=np.zeros((extent[1],extent[2],extent[0]),np.uint8);at=p.p-lo;local[at[:,1],at[:,2],at[:,0]]=p.states
        groups,lengths,proof=merge_surface_runs(surface_groups(local,g.STATES),extent.tolist());quads+=proof['rendered_quads']
        previews.append(dict(id=p.name,origin=(lo+offset).tolist(),size=extent.tolist(),starts=groups,lengths=lengths,blocks=len(p.p)))
    audit=dict(passed=True,geometry_export_verified=True,no_nominal_clipping=True,
        animation_enabled=False,animation_loop_present=False,blocks=data['blocks'],original_components=len(parts),
        viewer_rendered_quads=quads,readback=exported['readback'],hashes=exported['hashes'],
        material_resource_sources=sources,enabled_resource_packs=packs,instance_version='3.5',desktop_used=False,
        game_started=False,game_verified=False,reference_fidelity_verified=False,static_clearance_verified=False,
        matrix_layout_complete=False,reference_images=60,official_reference_images=32,
        claim_boundary=getattr(g,'CLAIM_BOUNDARY','多视角重制的独立静态候选；非完整W02、非已验收逐处复刻、非实装测试。'))
    data['generated_at']=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    payload=dict(data=data,audit=audit,materials=materials,parts=previews)
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode()
    (view/'data.js').write_text('window.W02_STATIC_PAYLOAD='+json.dumps(encoded)+';','utf8')
    prior=g.ROOT/'deliveries/W02_理之律者19C_静态造型小样_V1_20261110'
    source=(prior/'生成脚本/viewer.mjs').read_text('utf8')
    assert all(token not in source for token in ['requestAnimationFrame','setInterval','function seek'])
    source=source.replace("if(name==='back')direction.set(.7,.2,-1);", "if(name==='back')direction.set(0,.12,-1);\n    if(name==='low')direction.set(-.8,-.7,1.2);")
    source=source.replace('new THREE.Vector3(-1,.7,1.25)','new THREE.Vector3(-.8,.35,1.5)')
    (scripts/'viewer.mjs').write_text(source,'utf8')
    page=(prior/'w02/三维评审.html').read_text('utf8')
    page=page.replace('V1 · 纯静态造型研究 · 完整387×166×172','V2 · 60张多视角参考 · 完整'+f'{size[0]}×{size[2]}×{size[1]}')
    page=page.replace('W02 · 普通理之律者19C静态小样','W02 · 理之律者19C多视角重制V2')
    page=page.replace('← 小样与参考说明','← V2总览与参考')
    page=page.replace('普通理之律者19C。参考正面截图制作胸甲、分节双臂与机械手；顶部与背面资料尚不完整。',
        '普通理之律者19C。60张参考：32张官方、28张二创结构辅助；11个完整静态构件。<br><a href="../参考图总览.html">打开参考图：来源／角度筛选</a>')
    page=page.replace('<button data-view="core">胸甲</button>','<button data-view="core">胸甲</button><button data-view="low">仰视</button>')
    page=page.replace('max="171" value="171"',f'max="{size[1]-1}" value="{size[1]-1}"').replace('id="layerLabel">171','id="layerLabel">'+str(size[1]-1))
    options=''.join(f'<label><input type="checkbox" checked data-part="{escape(p.name)}">{escape(p.name)}</label>' for p in parts)
    import re
    page=re.sub(r'(?<=<summary>独立构件</summary>).*?(?=</details>)',lambda _:options,page,count=1,flags=re.S)
    (view/'三维评审.html').write_text(page,'utf8')
    save(g.OUT/'manifest.json',data);save(g.OUT/'verification.json',audit)
    palette=[]
    for material,count in zip(materials,counts[1:]):
        rgb=ImageStat.Stat(Image.open(io.BytesIO(base64.b64decode(material['faces']['up'].split(',')[1]))).convert('RGB')).mean
        palette.append(dict(state=material['state'],count=int(count),role=g.ROLES[material['state']],texture_average_rgb=[round(v,1) for v in rgb]))
    save(g.OUT/'材料清单.json',palette)
    version=data.get('display_version','V2')
    np.savez_compressed(g.LOG/(version.lower()+'-original-components.npz'),**{p.name+'__'+k:v for p in parts for k,v in [('p',p.p),('states',p.states)]})
    notes=''.join('<li>'+escape(s)+'</li>' for s in data['source_conflicts'])
    (g.OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>重装小兔19C · 多视角重制V2</title><style>:root{{color-scheme:dark}}body{{max-width:1440px;margin:30px auto;padding:0 24px;background:#0b1624;color:#e4f0ff;font:16px/1.8 system-ui}}a{{color:#8bb9ff}}img{{width:100%;display:block}}.note{{padding:16px;background:#142b44;border-left:3px solid #428DFF}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}@media(max-width:850px){{.grid{{display:block}}}}</style><h1>普通理之律者 · 重装小兔19C</h1><p>多视角重制V2 · 纯静态 · 2026-11-10</p><p class="note">上一版参考不足、外形失真，退出当前修改基线。新候选以60张多视角参考重做窄长尖盾机体、橙色罩体、肩侧轮组、背部双轨模块、重型前臂、长指机械手和下垂节链。</p><p><a href="w02/三维评审.html">打开V2静态三维预览</a> · <a href="参考图总览.html">查看60张参考与来源</a> · <a href="参考图清单.json">参考清单</a> · <a href="verification.json">离线核验</a></p><img src="完整预览.png" alt="19C多视角重制V2"><div class="grid"><img src="正面.png" alt="V2正面"><img src="背面.png" alt="V2背面"></div><div class="grid"><img src="侧面.png" alt="V2侧面"><img src="俯视.png" alt="V2俯视"></div><p>参考32张官方原帧、28张二创结构辅助原帧，来自3段视频；包含不同角度、动作与局部特写，不宣称60个独立机位。二创改色与舞蹈姿态未作为官方颜色或待机设定。</p><p>实际{size[0]}×{size[2]}×{size[1]}（宽深高），{data['blocks']:,}实体方块，11个完整构件；先生成再求边界，无名义尺寸裁切。构造蓝#428DFF为身份基准；现有蓝、白、深灰材质近似，橙色罩体依据官方画面保留。</p><p>全部静态；可旋转镜头、剖切、显隐。NBT及Schematic均逐格回读，空闲不持续重绘。构件接合与可能干涉保留记录，未声称全部无穿模。</p><ul>{notes}</ul><p>尚未并入649×493×303工业矩阵，未注册控制器或进行游戏成型／运行验收。</p><p><a href="w02/{data['name']}.nbt">NBT</a> · <a href="w02/{data['name']}.schem">Schematic</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p></html>''','utf8')
    index=g.OUT/'index.html'
    comparisons='''<h2>正面轮廓对照</h2><p>左：官方教学R31（208秒）；右：V2正面。参考为战斗展开姿态，候选选用双臂下垂姿态，不能按相同姿势宣称逐处还原。</p><div class="grid"><a href="https://www.youtube.com/watch?v=sHqseNq6pdI&amp;t=208s"><img src="参考图/guide-208.jpg" alt="官方19C参考R31"></a><img src="正面.png" alt="V2正面轮廓"></div>'''
    correspondence='<h2>部件参考对应</h2><ul>'+''.join('<li>'+escape(r['component'])+'：'+escape('、'.join(r['references']))+'。'+escape(r['status'])+'</li>' for r in data['reference_correspondence'])+'</ul>'
    index.write_text(index.read_text('utf8').replace('<img src="完整预览.png"',comparisons+correspondence+'<img src="完整预览.png"',1),'utf8')
    if version!='V2':
        for file in [index,view/'三维评审.html']:
            file.write_text(file.read_text('utf8').replace('V2',version).replace('多视角重制'+version,'多视角细化'+version),'utf8')
    for file in [Path(__file__),Path(g.__file__),g.ROOT/'tools/structure_delivery/collect_19c_references_20261110.py']:
        shutil.copy2(file,scripts/file.name)
    print(json.dumps(dict(passed=True,blocks=data['blocks'],size_xyz=data['size'],quads=quads,parts=len(parts)),ensure_ascii=False))


if __name__=='__main__':main()
