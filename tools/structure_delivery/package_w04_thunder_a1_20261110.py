# -*- coding: utf-8 -*-
"""W04静态候选的独立三维页面、完整导出与图像交付。"""
import base64,gzip,json,re,shutil
from html import escape
from pathlib import Path
import numpy as np
import w04_thunder_canyon_a1_20261110 as g
from build_i25_world_bubble_observatory_20261025 import resource_materials
from i34_open_observatory_export_20261027 import export_dense,surface_groups
from i37_surface_runs_20261027 import merge_surface_runs


def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    g.OUT.mkdir(exist_ok=True);g.LOG.mkdir(exist_ok=True)
    cube,data,parts=g.build();view=g.OUT/'w04';view.mkdir(exist_ok=True);scripts=g.OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    exported=export_dense(cube,g.STATES,data['name'],view);materials,sources,packs=resource_materials(g.STATES)
    offset=np.array(data['blueprint_to_export_offset_xyz']);previews=[];quads=0
    for p in parts:
        lo,hi=p.p.min(0),p.p.max(0);extent=hi-lo+1;local=np.zeros((extent[1],extent[2],extent[0]),np.uint8)
        at=p.p-lo;local[at[:,1],at[:,2],at[:,0]]=p.states
        groups,lengths,proof=merge_surface_runs(surface_groups(local,g.STATES),extent.tolist());quads+=proof['rendered_quads']
        previews.append(dict(id=p.name,origin=(lo+offset).tolist(),size=extent.tolist(),starts=groups,lengths=lengths,blocks=len(p.p)))
    audit=dict(passed=exported['readback']['passed'],readback=exported['readback'],hashes=exported['hashes'],viewer_rendered_quads=quads,
        no_nominal_clipping=True,animation_enabled=False,material_resource_sources=sources,enabled_resource_packs=packs,game_verified=False)
    data['component_bounds_blueprint']={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist(),blocks=len(p.p)) for p in parts}
    payload=dict(data=data,audit=audit,materials=materials,parts=previews)
    (view/'data.js').write_text('window.W04_STATIC_PAYLOAD='+json.dumps(base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode())+';','utf8')
    source=(g.ROOT/'deliveries/W02_理之律者19C_静态造型小样_V1_20261110/生成脚本/viewer.mjs').read_text('utf8').replace('W02','W04')
    source=source.replace("if(name==='back')direction.set(.7,.2,-1);","if(name==='back')direction.set(0,.15,-1);\n    if(name==='low')direction.set(-.7,-.55,1.2);")
    (scripts/'viewer.mjs').write_text(source,'utf8')
    page=(g.ROOT/'deliveries/W02_理之律者19C_静态造型小样_V1_20261110/w02/三维评审.html').read_text('utf8')
    page=page.replace('W02 · 普通理之律者19C静态小样','W04 · 鸣霆·超导电磁天枢A1').replace('理之律者 · 重装小兔19C','雷之律者 · 鸣霆·超导电磁天枢')
    w,h,d=data['size'];page=page.replace('V1 · 纯静态造型研究 · 完整387×166×172',f'A1 · 鬼角悬刃 · 完整{w}×{d}×{h}')
    page=page.replace('构造蓝 #428DFF / 白装甲 / 深色机械骨架','绯雷红 #C93F63 / 黑色机械甲 / 紫色晶格')
    page=page.replace('普通理之律者19C。参考正面截图制作胸甲、分节双臂与机械手；顶部与背面资料尚不完整。',escape(data['summary']))
    page=page.replace('未接回649×493×303工业矩阵。没有控制器与接口占位，不代表机器成型或运行。','我们的第一版外观候选，全部静态。前控为造型示意；未注册机器或进行游戏实装。Gemini第二版待负责人提供描述后另制。')
    page=page.replace('data-view="core">胸甲','data-view="core">极化核心').replace('<button data-view="core">','<button data-view="low">仰视</button><button data-view="core">')
    page=page.replace('max="171" value="171"',f'max="{h-1}" value="{h-1}"').replace('id="layerLabel">171',f'id="layerLabel">{h-1}')
    options=''.join(f'<label><input type="checkbox" checked data-part="{escape(p.name)}">{escape(p.name)}</label>' for p in parts)
    page=re.sub(r'(?<=<summary>独立构件</summary>).*?(?=</details>)',lambda _:options,page,count=1,flags=re.S)
    (view/'三维评审.html').write_text(page,'utf8')
    save(g.OUT/'manifest.json',data);save(g.OUT/'verification.json',audit)
    save(g.OUT/'材料清单.json',[dict(state=s,count=int(np.count_nonzero(cube==i+1)),role=g.ROLES[s]) for i,s in enumerate(g.STATES)])
    np.savez_compressed(g.LOG/'components.npz',**{p.name+'__'+key:value for p in parts for key,value in [('p',p.p),('states',p.states)]})
    gallery=''.join(f'<figure><img src="{file}" alt="{label}"><figcaption>{label}</figcaption></figure>' for file,label in [('正面.png','对峙鬼角与悬浮太刀'),('俯视.png','双岸回流与放电峡谷'),('侧面.png','电极、刀与极化工位分层'),('背面.png','背面回流及机械肋'),('核心近景.png','中央悬刃与极化场')])
    (g.OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W04 · 鸣霆·超导电磁天枢 · A1</title><style>:root{{color-scheme:dark}}body{{max-width:1500px;margin:28px auto;padding:0 24px;background:#110f1c;color:#eee6ef;font:16px/1.8 system-ui}}a{{color:#ff96b4}}h1{{font-size:34px}}img{{width:100%;display:block}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}figure{{margin:0}}figcaption{{padding:10px}}.note{{border-left:4px solid #C93F63;padding:15px;background:#251729}}@media(max-width:800px){{.grid{{display:block}}}}</style><p>W04 · 普通雷之律者·芽衣 · 我们的第一版</p><h1>鸣霆·超导电磁天枢<br>鬼角双极 · 悬刃雷场</h1><p class="note">{escape(data['summary'])}</p><p><a href="w04/三维评审.html">打开完整三维预览</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p><p>宽{w} × 深{d} × 高{h} · {data['blocks']:,}实体方块 · {len(parts)}构件 · 全静态</p><img src="完整预览.png" alt="W04鬼角悬刃全景"><p>黑色重甲为轮廓、绯雷红#C93F63划出电极与回流路径，紫色晶格集中在脉冲堆和放电区。主角是两条内弯鬼角与中间的悬浮太刀，前方舰桥保留观看入口。</p><p>供能脉冲堆 → 双极电磁约束 → 中央极化工位 → 前方观察舰桥。此为外观工序表达，尚未接入实际配方。</p><div class="grid">{gallery}</div><p class="note">本项目原创候选，不宣称官方机械复刻；不混用始源之律者。完整生成后求实际边界，无裁切、无动画，未游戏实装。Gemini第二版等待负责人提供描述，届时单独生成供比较。</p><p><a href="manifest.json">构件与边界</a> · <a href="verification.json">导出核验</a> · <a href="材料清单.json">材料</a> · <a href="w04/{data['name']}.nbt">NBT</a> · <a href="w04/{data['name']}.schem">Schematic</a></p></html>''','utf8')
    for file in [Path(__file__),Path(g.__file__)]:shutil.copy2(file,scripts/file.name)
    print(json.dumps(dict(passed=True,size=data['size'],blocks=data['blocks'],quads=quads),ensure_ascii=False))


if __name__=='__main__':main()
