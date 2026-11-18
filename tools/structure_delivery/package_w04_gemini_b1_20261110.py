# -*- coding: utf-8 -*-
"""独立打包W04 Gemini B1；保留原案冲突、所有构件与A1历史，不接入游戏。"""
import base64,gzip,json,re,shutil,hashlib
from html import escape
from pathlib import Path
import numpy as np
import w04_gemini_dragon_b1_20261110 as g
from build_i25_world_bubble_observatory_20261025 import resource_materials
from i34_open_observatory_export_20261027 import export_dense,surface_groups,digest
from i37_surface_runs_20261027 import merge_surface_runs

A1=g.ROOT/'deliveries/W04_鸣霆超导电磁天枢_鬼角悬刃_A1_20261110'


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


def hashes(folder):
    return {str(p.relative_to(folder)):digest(p) for p in folder.rglob('*') if p.is_file()}


def overlaps(parts):
    from w02_bunny_dock_geometry_v3_20261108 import encode
    result=[]
    bounds=[(p.p.min(0),p.p.max(0)) for p in parts]
    for i,a in enumerate(parts):
        for j in range(i+1,len(parts)):
            b=parts[j];lo=np.maximum(bounds[i][0],bounds[j][0]);hi=np.minimum(bounds[i][1],bounds[j][1])
            if np.any(lo>hi):continue
            ma=np.all((a.p>=lo)&(a.p<=hi),axis=1);mb=np.all((b.p>=lo)&(b.p<=hi),axis=1)
            ia=np.flatnonzero(ma);ib=np.flatnonzero(mb)
            common,ai,bi=np.intersect1d(encode(a.p[ia]),encode(b.p[ib]),assume_unique=True,return_indices=True)
            if not len(common):continue
            intended=((i==0 and b.name.startswith(('02','05'))) or
                ('俱利伽罗' in a.name and '俱利伽罗' in b.name) or
                ('锁链' in a.name and '雷鼓磁环' in b.name) or ('雷鼓磁环' in a.name and ('锁链' in b.name or '前爪' in b.name)))
            q=a.p[ia[ai]]
            result.append(dict(a=a.name,b=b.name,shared_voxels=len(common),
                differing_materials=int(np.count_nonzero(a.states[ia[ai]]!=b.states[ib[bi]])),
                bounds=dict(min=q.min(0).tolist(),max=q.max(0).tolist()),
                classification='原案预期接合，细部仍需评审' if intended else '原案与转译的待协调交叠，原坐标保留'))
    return result


def main():
    g.OUT.mkdir(exist_ok=True);g.LOG.mkdir(exist_ok=True)
    before=hashes(A1);save(g.LOG/'a1-before-hashes.json',before)
    cube,data,parts=g.build();view=g.OUT/'w04';view.mkdir(exist_ok=True)
    scripts=g.OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    print('完整几何',data['size'],data['blocks'],flush=True)
    overlap=overlaps(parts);save(g.OUT/'原案冲突与交叠.json',dict(source_conflicts=data['source_conflicts'],pairs=overlap,
        resolution='不移动、不缩短、不删除；独立构件保留原坐标，复合体素同格按构件列表后者覆盖；此项不等于无穿模证明。'))
    print('独立构件相交',len(overlap),flush=True)
    exported=export_dense(cube,g.STATES,data['name'],view)
    print('NBT与Schematic逐格回读通过',flush=True)
    materials,sources,packs=resource_materials(g.STATES)
    offset=np.array(data['blueprint_to_export_offset_xyz']);previews=[];quads=0
    for p in parts:
        lo,hi=p.p.min(0),p.p.max(0);extent=hi-lo+1;local=np.zeros((extent[1],extent[2],extent[0]),np.uint8)
        at=p.p-lo;local[at[:,1],at[:,2],at[:,0]]=p.states
        groups,lengths,proof=merge_surface_runs(surface_groups(local,g.STATES),extent.tolist());quads+=proof['rendered_quads']
        previews.append(dict(id=p.name,origin=(lo+offset).tolist(),size=extent.tolist(),starts=groups,lengths=lengths,blocks=len(p.p)))
        print('完整表面',p.name,proof['rendered_quads'],flush=True)
    assert before==hashes(A1),'A1历史被改写'
    audit=dict(passed=exported['readback']['passed'],readback=exported['readback'],hashes=exported['hashes'],
        viewer_rendered_quads=quads,no_nominal_clipping=True,animation_enabled=False,
        material_resource_sources=sources,enabled_resource_packs=packs,game_verified=False,a1_unchanged=True,
        overlap_pairs=len(overlap),collision_free=False)
    data['component_bounds_blueprint']={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist(),blocks=len(p.p)) for p in parts}
    payload=dict(data=data,audit=audit,materials=materials,parts=previews)
    (view/'data.js').write_text('window.W04_STATIC_PAYLOAD='+json.dumps(base64.b64encode(gzip.compress(
        json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode())+';','utf8')
    source=(A1/'生成脚本/viewer.mjs').read_text('utf8')
    source=source.replace("if(name==='core')target.copy(offset).add(new THREE.Vector3(...data.center_blueprint));",
        "if(name==='core')target.copy(offset).add(new THREE.Vector3(...data.center_blueprint));\n    const detail=data.detail_views?.[name];if(detail)target.copy(offset).add(new THREE.Vector3(...detail.center));")
    source=source.replace("const bounds=name==='core'?", "const bounds=detail?new THREE.Box3(target.clone().sub(new THREE.Vector3(...detail.half)),target.clone().add(new THREE.Vector3(...detail.half))):name==='core'?")
    source=source.replace("renderer.setClearColor('#0b1624')","renderer.setClearColor('#18101c')")
    (scripts/'viewer.mjs').write_text(source,'utf8')
    w,h,d=data['size'];controls=''.join(f'<label><input type="checkbox" checked data-part="{escape(p.name)}">{escape(p.name)}</label>' for p in parts)
    page=(A1/'w04/三维评审.html').read_text('utf8')
    page=page.replace('鸣霆·超导电磁天枢A1','鸣霆·超导电磁天枢 · Gemini B1')
    page=re.sub(r'A1 · 鬼角悬刃 · 完整\d+×\d+×\d+',f'B1 · 俱利伽罗盘枢 · 完整{w}×{d}×{h}',page)
    page=page.replace('绯雷红 #C93F63 / 黑色机械甲 / 紫色晶格','绯雷红 #C93F63 / 玄黑骨甲 / 暗金导体')
    page=re.sub(r'<p class="note">.*?</p>','<p class="note">'+escape(data['summary'])+'</p>',page,count=1)
    page=page.replace('data-view="core">极化核心','data-view="core">盘枢核心')
    page=page.replace('</button></p><button id="reset">','</button><button data-view="dragon">龙首近景</button><button data-view="hand">鬼手近景</button><button data-view="sword">巨刃近景</button></p><button id="reset">',1)
    page=page.replace('max="342" value="342"',f'max="{h-1}" value="{h-1}"').replace('id="layerLabel">342',f'id="layerLabel">{h-1}')
    page=re.sub(r'(?<=<summary>独立构件</summary>).*?(?=</details>)',lambda _:controls,page,count=1,flags=re.S)
    page=page.replace('我们的第一版外观候选，全部静态。前控为造型示意；未注册机器或进行游戏实装。Gemini第二版待负责人提供描述后另制。',
        'Gemini第二候选，全部静态。前控与接口为外观示意；未注册、未实装。原文相交照实保留，可单独隐藏构件检查。')
    page=page.replace('← 小样与参考说明','← B1与A1对照').replace('#428DFF','#C93F63')
    (view/'三维评审.html').write_text(page,'utf8')
    save(g.OUT/'manifest.json',data);save(g.OUT/'verification.json',audit)
    save(g.OUT/'材料清单.json',[dict(state=s,count=int(np.count_nonzero(cube==i+1)),role=g.ROLES[s]) for i,s in enumerate(g.STATES)])
    np.savez_compressed(g.LOG/'components.npz',**{p.name+'__'+k:v for p in parts for k,v in [('p',p.p),('states',p.states)]})
    conflicts=''.join('<li>'+escape(s)+'</li>' for s in data['source_conflicts'])
    gallery=''.join(f'<figure><img src="{file}" alt="{label}"><figcaption>{label}</figcaption></figure>' for file,label in [
        ('正面.png','正面：三重鸟居、倒悬太刀与盘枢龙首'),('俯视.png','俯视：托卡马克雷池与完整S形龙躯'),
        ('侧面.png','侧面：巨刃、雷环与分节龙甲'),('背面.png','背面：机甲雷翼、龙脊与双塔'),
        ('龙首近景.png','龙首独立显示：张开双颚与长角'),('鬼手近景.png','鬼手独立显示：机械五指、指节与赤金锁链')])
    (g.OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W04 · Gemini俱利伽罗盘枢B1</title>
<style>:root{{color-scheme:dark}}body{{max-width:1550px;margin:25px auto;padding:0 25px;background:#140e19;color:#eee4ec;font:16px/1.8 system-ui}}a{{color:#f79ab7}}h1{{font-size:36px}}img{{width:100%;display:block}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0}}figcaption{{padding:10px}}.note{{border-left:4px solid #C93F63;padding:15px;background:#291622}}@media(max-width:850px){{.grid{{display:block}}}}</style>
<p>W04 · 普通雷之律者 · Gemini第二候选 · 全静态</p><h1>鸣霆·超导电磁天枢<br>俱利伽罗 · 盘枢B1</h1><p class="note">{escape(data['summary'])}</p>
<p><a href="w04/三维评审.html">打开完整三维预览</a> · <a href="../{A1.name}/index.html">打开我们的A1</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p>
<p>实际宽{w} × 深{d} × 高{h} · {data['blocks']:,}实体方块 · {len(parts)}独立构件 · 龙躯中心线{data['dragon_centerline_length']:.1f}格</p>
<img src="完整预览.png" alt="W04 Gemini B1完整预览"><div class="grid"><figure><img src="../{A1.name}/完整预览.png" alt="A1"><figcaption>我们的A1：鬼角双极、悬刃与放电峡谷</figcaption></figure><figure><img src="完整预览.png" alt="B1"><figcaption>Gemini B1：鬼手锁三环、倒悬巨刃、俱利伽罗盘枢</figcaption></figure></div>
<p>HRV绯雷红#C93F63、玄黑骨甲与金色导体；供电目标仍WSV。真实资源材质按当前增强版3.5实例解析；未引入始源粉白造型。</p><div class="grid">{gallery}</div>
<details><summary>原案尺寸冲突与公开转译</summary><ul>{conflicts}</ul><p>检测到{len(overlap)}对独立构件共享体素；含有意接合及待协调干涉。保留原方案，不能视作无穿模验收。</p></details>
<p class="note">独立候选；未批准、未注册W04控制器、未搭建游戏结构或验收成型／运行。动画关闭。A1全部原文件保持不变。</p>
<p><a href="manifest.json">完整构件与边界</a> · <a href="原案冲突与交叠.json">交叠记录</a> · <a href="verification.json">导出核验</a> · <a href="材料清单.json">材料</a> · <a href="w04/{data['name']}.nbt">NBT</a> · <a href="w04/{data['name']}.schem">Schematic</a></p></html>''','utf8')
    for file in [Path(__file__),Path(g.__file__)]:shutil.copy2(file,scripts/file.name)
    save(g.LOG/'packaging.json',dict(passed=True,size=data['size'],blocks=data['blocks'],quads=quads,
        dragon_centerline_length=data['dragon_centerline_length'],a1_unchanged=True,overlap_pairs=len(overlap),game_verified=False))
    print(json.dumps(dict(passed=True,size=data['size'],blocks=data['blocks'],quads=quads),ensure_ascii=False))


if __name__=='__main__':main()
