# -*- coding: utf-8 -*-
"""I26 八色货柜与四色拖头独立样件；不修改码头及实例。"""
import base64, collections, gzip, html, json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
import build_i26_kwaichung_body_v3_20261026 as delivery
base = delivery.base
OUT = ROOT / 'deliveries/I26_货柜八色与拖头四色_独立样件_V1_20261026'
TIERS = [('HBV','深蓝'),('HCV','赭金'),('HRV','酒红'),('HDV','青绿'),('QSV','灰青'),('QCV','靛蓝'),('QEV','锈橙'),('QAV','砖红棕')]
ROBUST,CLEAN,GEAR = 'gtceu:robust_machine_casing','gtceu:clean_machine_casing','gtceu:tungstensteel_gearbox'
GLASS,LIGHT,BLACK = 'minecraft:light_blue_stained_glass','minecraft:sea_lantern','minecraft:black_concrete'
def casing(tier): return 'hk3gtl:voltage_machine_casing_' + tier.lower()
def box(c,lo,hi,s):
    for x in range(lo[0],hi[0]+1):
        for y in range(lo[1],hi[1]+1):
            for z in range(lo[2],hi[2]+1): c[x,y,z]=s
def container(tier):
    c={}; main=casing(tier)
    for x in range(9):
        for y in range(9):
            for z in range(21):
                if x in (0,8) or y in (0,8) or z in (0,20): c[x,y,z]=main
    for x in (0,8):
        for z in (0,20): box(c,(x,0,z),(x,8,z),ROBUST)
    for y in (0,8): box(c,(0,y,0),(8,y,0),ROBUST)
    box(c,(4,1,0),(4,7,0),ROBUST)
    for x in (2,6): box(c,(x,2,0),(x,6,0),CLEAN)
    return c
def tractor(tier):
    c={}; main=casing(tier)
    box(c,(1,1,0),(5,2,12),ROBUST);box(c,(1,3,0),(5,4,11),main)
    for x in (0,5):
        for z in (2,9):
            box(c,(x,0,z),(x+1,2,z+2),BLACK);c[x if x==0 else 6,1,z+1]=GEAR
    box(c,(1,4,1),(5,8,5),main);box(c,(1,6,1),(5,7,1),GLASS)
    for x in (1,5): box(c,(x,6,2),(x,7,4),GLASS)
    box(c,(1,9,1),(5,9,5),CLEAN);box(c,(1,3,0),(5,3,0),CLEAN)
    for x in (1,5): c[x,4,0]=LIGHT
    box(c,(2,5,8),(4,5,10),GEAR);c[3,5,9]=BLACK
    box(c,(2,4,12),(4,4,12),CLEAN)
    return c
def metadata(c,title,name,samples):
    return {'key':'I26-SAMPLE','name':name,'title':title,'size':[max(p[i] for p in c)+1 for i in range(3)],'samples':samples,
            'blocks':[{'pos':list(p),'state':s} for p,s in sorted(c.items(),key=lambda v:(v[0][1],v[0][2],v[0][0]))]}
def gallery(kind):
    tiers=TIERS if kind=='cargo' else TIERS[:4]; whole={};items=[];shapes=[]
    for n,(tier,color) in enumerate(tiers):
        c=container(tier) if kind=='cargo' else tractor(tier)
        shapes.append({p:('主色' if s==casing(tier) else s) for p,s in c.items()})
        ox,oz=(n%4)*16+3,(n//4)*30+3
        whole.update({(x+ox,y,z+oz):s for (x,y,z),s in c.items()})
        items.append({'id':tier,'label':tier+' · '+color,'color':color,'state':casing(tier),'offset':[ox,0,oz],
                      'size':[9,9,21] if kind=='cargo' else [7,10,13],'blocks':len(c),'local_cells':c})
    assert all(s==shapes[0] for s in shapes),'换色样件必须逐格同构'
    assert len({v['state'] for v in items})==len(tiers)
    title='八色货柜样件' if kind=='cargo' else '四色无人集卡拖头样件'
    return metadata(whole,title,'i26-'+kind+'-samples-v1',[{k:v for k,v in a.items() if k!='local_cells'} for a in items]),items
def write_json(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
STYLE='*{box-sizing:border-box}body{margin:0;background:#121b2b;color:#e2edf5;font:15px/1.65 system-ui,Microsoft YaHei,sans-serif}a{color:#a8d9e9}header{padding:12px 20px}h1{font-size:24px;line-height:1.35}.review{display:grid;grid-template-columns:1fr 300px;height:calc(100vh - 110px);min-height:570px}#stage{position:relative;overflow:hidden;min-height:420px}#stage canvas{display:block;width:100%;height:100%}#loading{position:absolute;top:15px;left:15px;background:#263d50;padding:10px;z-index:2}aside{padding:18px;background:#19293a;overflow:auto}button,select{background:#2d455a;border:1px solid #647d8a;color:#ecf2f5;border-radius:4px;padding:7px;margin:3px;cursor:pointer}select{max-width:100%;width:100%}small{display:block;color:#afc3d1}#legend img{width:36px;height:36px;vertical-align:middle;image-rendering:pixelated;margin:5px}code{overflow-wrap:anywhere}#legend p{border-top:1px solid #384f63;padding-top:9px}@media(max-width:800px){.review{display:block;height:auto}#stage{height:65vh}aside{overflow:visible}}'
def review_html(kind,data):
    options=''.join('<option value="'+a['id']+'">'+html.escape(a['label'])+'</option>' for a in data['samples'])
    desc='箱体9宽×21长×9高；内部中空，尺寸不是存储容量。' if kind=='cargo' else '拖头7宽×13长×10高；四色共用同一底盘、轮组、驾驶室和牵引盘，没有挂车。'
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+data['title']+'</title><style>'+STYLE+'</style></head><body><header><a href="../index.html">← 方案与总览</a><h1>'+data['title']+'</h1><small>真实方块、真实贴图 · 独立样件；尚未放入码头</small></header><main class="review"><section id="stage"><div id="loading">载入实际方块纹理…</div></section><aside><label>聚焦样件<select id="sample"><option value="all">全部样件</option>'+options+'</select></label><div><button data-view="iso">等轴</button><button data-view="front">正面</button><button data-view="side">侧面</button><button data-view="top">俯视</button><button id="reset">重置</button></div><p>左键旋转 · 右键平移 · 滚轮缩放</p><p id="counts"></p><p id="status"></p><p>'+desc+'</p><p>仅检查造型与配色。未导入码头；未声明游戏成型、配方或运行能力。</p><div id="legend"></div></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>'
def contact_sheet(kind,items,materials):
    cw,ch=530,590 if kind=='cargo' else 510
    sheet=Image.new('RGB',(4*cw,((len(items)+3)//4)*ch+110),'#101924');d=ImageDraw.Draw(sheet)
    f=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    d.text((28,18),'I26 · 八色货柜：每箱一种主色' if kind=='cargo' else 'I26 · 四色拖头：同一车体，四种机壳',font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',31),fill='#e6edf4')
    d.text((28,67),'独立样件，不放入码头；实际方块纹理，非游戏截图。',font=small,fill='#aabacb')
    for n,item in enumerate(items):
        temp=OUT/kind/item['id'].lower();temp.mkdir(parents=True,exist_ok=True)
        data=metadata(item['local_cells'],item['label'],item['id'],[])
        mats=[m for m in materials if m['state'] in set(item['local_cells'].values())]
        picture=base.render(data,mats,temp);picture.thumbnail((cw-20,ch-120),Image.Resampling.LANCZOS)
        x,y=(n%4)*cw,110+(n//4)*ch
        sheet.paste(picture,(x+(cw-picture.width)//2,y+(ch-120-picture.height)//2))
        d.text((x+20,y+ch-110),item['label'],font=f,fill='#e5dfd2')
        d.text((x+20,y+ch-66),str(item['blocks'])+' 方块 · 同构换色样件',font=small,fill='#aabacb')
    sheet.save(OUT/('货柜八色接触表.png' if kind=='cargo' else '拖头四色接触表.png'))
def main():
    OUT.mkdir(parents=True,exist_ok=True);galleries={k:gallery(k) for k in ('cargo','tractor')}
    states_all=sorted({b['state'] for data,_ in galleries.values() for b in data['blocks']})
    materials,sources,packs,proof=base.resource_materials(sorted(set(states_all)|{base.QAV,base.PORT,base.CONTROL}))
    materials=[m for m in materials if m['state'] in states_all]
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    assert proof['instance_version']=='2.9.2'
    checks=[]
    for kind,(data,items) in galleries.items():
        path=OUT/kind;path.mkdir(exist_ok=True);states=sorted({b['state'] for b in data['blocks']})
        mats=[m for m in materials if m['state'] in states];counts=collections.Counter(b['state'] for b in data['blocks'])
        audit={'palette':dict(counts),'checks':['真实完整方块模型及当前实例纹理已读取','换色样件逐格同构，尺寸与材质统计来自同源数据'],'not_verified':['未摆入码头；无正式Pattern、配方或运行功能验收']}
        groups=base.build_surface_groups(data,states)
        payload={'data':{k:v for k,v in data.items() if k!='blocks'},'palette':states,'surfaceGroups':groups,'blockCount':len(data['blocks']),'materials':mats,'audit':audit,'names':{}}
        encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),compresslevel=9)).decode('ascii')
        decoded=json.loads(gzip.decompress(base64.b64decode(encoded)));assert decoded==payload
        w,h,dep=data['size'];expected={tuple(b['pos']):b['state'] for b in data['blocks']}
        exposed={((n%w),n//(w*dep),(n//w)%dep):state for state,faces in zip(states,decoded['surfaceGroups']) for face in faces for n in face}
        assert all(expected[p]==s for p,s in exposed.items())
        assert all(0<=b['pos'][i]<data['size'][i] for b in data['blocks'] for i in range(3))
        write_json(path/'样件蓝图.json',data);write_json(path/'材料统计.json',dict(counts))
        (path/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(encoded)+';',encoding='utf-8')
        (path/'三维评审.html').write_text(review_html(kind,data),encoding='utf-8')
        subprocess.run(['node',str(ROOT/'tools/structure_delivery/build_i26_samples_viewer_v1_20261026.mjs'),str(path)],cwd=ROOT,check=True)
        base.render(data,mats,path);contact_sheet(kind,items,mats)
        checks.append({'kind':kind,'size_xyz':data['size'],'blocks':len(data['blocks']),'items':data['samples'],'surface_faces':sum(len(f) for fs in groups for f in fs),'same_shape':True,'payload_roundtrip':True})
    write_json(OUT/'verification.json',{'passed':True,'instance':str(base.INSTANCE),'instance_proof':proof,'source_materials':sources,'enabled_resource_packs':packs,'samples':checks,'claim_boundary':'独立外观样件；未摆入码头，未生成正式Pattern，未写入实例，未验证运行功能。'})
    cards=''.join('<li><b>'+t+'</b> · '+c+' <code>'+casing(t)+'</code></li>' for t,c in TIERS)
    page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I26货柜与拖头独立样件方案</title><style>body{max-width:1180px;margin:30px auto;padding:0 22px;background:#111b28;color:#e6edf4;font:16px/1.75 system-ui,Microsoft YaHei,sans-serif}a{color:#a8d9e9}h1{line-height:1.35}img{width:100%;height:auto}li{margin:8px 0}code{font-size:13px;overflow-wrap:anywhere}.note{background:#203044;border-left:4px solid #bd9d67;padding:14px 18px}.buttons{display:flex;gap:16px;flex-wrap:wrap}iframe{display:block;width:100%;height:800px;border:1px solid #4a6176}button{font:inherit;background:#2d455a;color:#e6edf4;padding:8px 12px;border:1px solid #7790a0;cursor:pointer}#viewer[hidden]{display:none}@media(max-width:700px){iframe{height:900px}}</style></head><body><h1>I26 · 八色货柜与四色拖头</h1><p><a href="../I26_码头主体撤高塔与拖头_构图研究_V4_20261026/index.html">撤塔构图对照 V4（递增规则待定）</a></p><p class="note">先审独立样件。货柜和拖头均未放回码头，未实装游戏；本页使用GTL增强版2.9.2与项目内的真实方块材质。</p><h2>电压与选材方案</h2><p>QAV是本模组新增16阶中的第8阶：MAX(14)之后为 HBV、HCV、HRV、HDV、QSV、QCV、QEV、QAV(22)。ULV(0)至QAV(22)共23档；本方案从其中选用新增的前8种机械机壳，统一工业纹理并保留8种实际配色。</p><p>一只箱体只使用一种电压机壳作为主色，少量钢灰角件、门框和浅色门锁统一规格；不把八色混进同一货柜。八款箱体均为9宽×21长×9高，中空结构；尺寸仅为建筑比例，不代表物品存储容量。</p><ul>'''+cards+'''</ul><img src="货柜八色接触表.png" alt="八种电压机壳货柜同形换色对照"><h2>四色拖头</h2><p>采用HBV深蓝、HCV赭金、HRV酒红、HDV青绿四款。车身7宽×13长×10高，同一底盘、轮组、驾驶室、玻璃、灯组及后牵引盘；只替换主色机械机壳，不带挂车。</p><img src="拖头四色接触表.png" alt="四种配色的无人集卡拖头同形对照"><h2>独立三维评审</h2><p>点选后才载入一套三维场景，避免同时运行两套WebGL。进入后可聚焦单个颜色、旋转、平移与缩放。</p><div class="buttons"><button data-src="cargo/三维评审.html">八色货柜</button><button data-src="tractor/三维评审.html">四色拖头</button><button id="close">关闭三维</button><a href="cargo/三维评审.html">单独打开货柜</a><a href="tractor/三维评审.html">单独打开拖头</a></div><iframe id="viewer" title="独立样件三维评审" hidden></iframe><p><a href="verification.json">核验与材质来源</a></p><p class="note">实际贴图色彩偏工业暗色，颜色名称只便于识别；预览不人为给贴图染色或替换理想色卡。首帧静态材质不代表游戏光照和动态效果。无正式Pattern、配方、成型、物流或存储能力验收。</p><script>const frame=document.getElementById('viewer');for(const b of document.querySelectorAll('[data-src]'))b.onclick=()=>{frame.src=b.dataset.src;frame.hidden=false;frame.scrollIntoView({behavior:'smooth',block:'start'});};document.getElementById('close').onclick=()=>{frame.removeAttribute('src');frame.hidden=true;};</script></body></html>'''
    (OUT/'index.html').write_text(page,encoding='utf-8')
    print(json.dumps({'output':str(OUT),'galleries':checks},ensure_ascii=False))
if __name__=='__main__': main()
