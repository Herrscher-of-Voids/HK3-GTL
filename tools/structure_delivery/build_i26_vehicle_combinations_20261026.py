# -*- coding: utf-8 -*-
"""I26车辆外观组合：32种挂箱与4种空载，复用已交付真实方块样件。"""
import base64, gzip, hashlib, html, json, re, subprocess
from pathlib import Path
from urllib.parse import unquote
from PIL import Image, ImageDraw, ImageFont
import build_i26_samples_v1_20261026 as samples

ROOT = samples.ROOT
SOURCE = samples.OUT
OUT = ROOT / 'deliveries/I26_货车32种挂箱与4种空载_组合预览_V1_20261026'
TIERS = samples.TIERS

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def source_payload(kind):
    text = (SOURCE / kind / 'data.js').read_text(encoding='utf-8')
    encoded = json.loads(text.split('=', 1)[1].rstrip().rstrip(';'))
    return json.loads(gzip.decompress(base64.b64decode(encoded)))

def validate_sources():
    for kind, maker in [('tractor', samples.tractor), ('cargo', samples.container)]:
        data = json.loads((SOURCE / kind / '样件蓝图.json').read_text(encoding='utf-8'))
        cells = {tuple(b['pos']): b['state'] for b in data['blocks']}
        for item in data['samples']:
            ox, oy, oz = item['offset']; w, h, dep = item['size']
            local = {(x-ox, y-oy, z-oz): state for (x,y,z),state in cells.items()
                     if ox <= x < ox+w and oy <= y < oy+h and oz <= z < oz+dep}
            assert local == maker(item['id']), (kind, item['id'], '样件来源不一致')

def assemble(tractor_tier, cargo_tier):
    ox = 1 if cargo_tier else 0
    c = {(x+ox,y,z): state for (x,y,z),state in samples.tractor(tractor_tier).items()}
    original = dict(c)
    if cargo_tier:
        trailer = {}
        samples.box(trailer, (1,5,8), (7,5,30), samples.ROBUST)
        for x in (2,6):
            samples.box(trailer, (x,4,11), (x,4,30), samples.ROBUST)
        for z in (23,27):
            samples.box(trailer, (1,3,z), (7,3,z+2), samples.ROBUST)
            for x in (0,7):
                samples.box(trailer, (x,0,z), (x+1,2,z+2), samples.BLACK)
                trailer[x if x == 0 else 8,1,z+1] = samples.GEAR
        for x in (1,7): samples.box(trailer, (x,3,24), (x,5,24), samples.ROBUST)
        samples.box(trailer, (0,4,30), (8,4,30), samples.CLEAN)
        for x in (0,8): trailer[x,4,30] = samples.LIGHT
        for p, state in trailer.items(): c.setdefault(p, state)
        cargo = {(8-x,y+6,29-z): state for (x,y,z),state in samples.container(cargo_tier).items()}
        assert not (set(c) & set(cargo)), '箱体不得侵入拖头或底盘'
        c.update(cargo)
        assert all(c[p] == state for p,state in cargo.items())
    assert all(c[p] == state for p,state in original.items()), '原拖头不可被底盘覆盖'
    seen = {next(iter(c))}; todo = list(seen)
    while todo:
        x,y,z = todo.pop()
        for dx,dy,dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            p = (x+dx,y+dy,z+dz)
            if p in c and p not in seen: seen.add(p); todo.append(p)
    assert len(seen) == len(c), '整车必须由牵引盘、半挂底盘、轮组和箱体连续相接'
    return c

def main():
    validate_sources()
    OUT.mkdir(parents=True, exist_ok=True)
    render_dir = OUT / 'renders'; render_dir.mkdir(exist_ok=True)
    materials_by_state = {m['state']:m for kind in ('cargo','tractor') for m in source_payload(kind)['materials']}
    materials = [materials_by_state[s] for s in sorted(materials_by_state)]
    palette = [m['state'] for m in materials]
    variants = []; pictures = []; checks = []; geometry = {}
    for tractor_tier, tractor_color in TIERS[:4]:
        for cargo_tier, cargo_color in [('', '空载拖头'), *TIERS]:
            identity = tractor_tier + '-' + (cargo_tier or 'EMPTY')
            label = tractor_tier+' '+tractor_color+'拖头 × '+(cargo_tier+' '+cargo_color+'货柜' if cargo_tier else '空载')
            cells = assemble(tractor_tier, cargo_tier)
            data = samples.metadata(cells, label, identity, [])
            states = sorted(set(cells.values()))
            mats = [materials_by_state[state] for state in states]
            path = render_dir / identity.lower(); path.mkdir(exist_ok=True)
            picture = samples.base.render(data, mats, path)
            pictures.append(picture)
            groups = samples.base.build_surface_groups(data, palette)
            w,h,dep = data['size']
            visible = {(n%w,n//(w*dep),(n//w)%dep):state for state,faces in zip(palette,groups) for face in faces for n in face}
            assert all(cells[p] == state for p,state in visible.items())
            assert len(cells) == len(data['blocks'])
            assert all(0 <= p[i] < data['size'][i] for p in cells for i in range(3))
            tractor_positions = {(x+(1 if cargo_tier else 0),y,z) for x,y,z in samples.tractor(tractor_tier)}
            normalized = {p:('拖头主色' if state == samples.casing(tractor_tier) and p in tractor_positions
                             else '箱体主色' if cargo_tier and state == samples.casing(cargo_tier) else state) for p,state in cells.items()}
            shape_key = bool(cargo_tier)
            if shape_key in geometry: assert normalized == geometry[shape_key]
            else: geometry[shape_key] = normalized
            variants.append({'id':identity,'label':label,'tractor':tractor_tier,'cargo':cargo_tier or None,
                             'size':data['size'],'blockCount':len(cells),'surfaceGroups':groups,
                             'image':'renders/'+identity.lower()+'/等轴预览.png'})
            checks.append({'id':identity,'size_xyz':data['size'],'blocks':len(cells),
                           'surface_faces':sum(len(face) for state in groups for face in state),
                           'six_neighbor_components':1,'original_tractor_preserved':True,
                           'original_cargo_preserved':bool(cargo_tier),'shared_trailer':bool(cargo_tier)})
            print(identity, len(cells), flush=True)
    assert len(variants) == 36 and sum(bool(v['cargo']) for v in variants) == 32
    assert len({(v['tractor'],v['cargo']) for v in variants}) == 36
    payload = {'materials':materials,'palette':palette,'variants':variants}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),9)).decode('ascii')
    assert json.loads(gzip.decompress(base64.b64decode(encoded))) == payload
    (OUT/'data.js').write_text('window.HK3_COMBINATIONS='+json.dumps(encoded)+';',encoding='utf-8')
    for group, name, cols in [(list(range(36)), '36种车辆组合接触表.png',9),
                              *[(list(range(n*9,n*9+9)), tier+'拖头九种状态.png',3) for n,(tier,_) in enumerate(TIERS[:4])]]:
        cw,ch = 550,470; rows=(len(group)+cols-1)//cols
        sheet=Image.new('RGB',(cols*cw,rows*ch+112),'#111b28');draw=ImageDraw.Draw(sheet)
        font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
        draw.text((24,18),'I26 · 32种挂箱组合 + 4种空载拖头' if len(group)==36 else name.replace('.png',''),font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29),fill='#e5edf5')
        draw.text((24,66),'真实方块样件同源渲染；空载单列，不计入挂箱组合。',font=font,fill='#a7bbcc')
        for slot,index in enumerate(group):
            x=(slot%cols)*cw;y=112+(slot//cols)*ch
            picture=pictures[index].copy();picture.thumbnail((cw-16,ch-68),Image.Resampling.LANCZOS)
            sheet.paste(picture,(x+(cw-picture.width)//2,y+(ch-68-picture.height)//2))
            v=variants[index]
            draw.text((x+18,y+ch-59),v['id']+' · '+('空载拖头' if not v['cargo'] else '挂箱组合'),font=font,fill='#e5edf5')
            draw.text((x+18,y+ch-30),v['label'],font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17),fill='#acbecd')
        sheet.save(OUT/name)
    write_pages(variants)
    source_files=[SOURCE/'verification.json', *[SOURCE/k/f for k in ('cargo','tractor') for f in ('data.js','样件蓝图.json')]]
    write_json(OUT/'verification.json',{'passed':True,'kind':'appearance_samples_only','loaded_combinations':32,'empty_tractors':4,'total_previews':36,
      'same_geometry_with_color_substitution':True,'payload_roundtrip':True,'single_webgl_scene_at_a_time':True,
      'source_delivery':str(SOURCE),'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
      'source_resources':'复用独立样件V1内GTL增强版2.9.2及项目方块真实纹理快照；未改变贴图配色。',
      'assembly':'保留拖头/箱体原方块，箱体绕Y轴转180度后移至后方Y=6、Z=9，箱门朝车尾；补共用钢灰半挂底盘、接地后轮及连至承重底盘的轮架，通过原牵引盘连接。',
      'claim_boundary':'建筑外观样件，不是可驾驶实体；未摆回码头、未写入实例、未生成正式Pattern或确认蓝图。','variants':checks})
    subprocess.run(['node',str(ROOT/'tools/structure_delivery/build_i26_vehicle_combinations_viewer_20261026.mjs'),str(OUT)],cwd=ROOT,check=True)
    for page in OUT.glob('*.html'):
        text=page.read_text(encoding='utf-8')
        assert '\ufffd' not in text
        for target in re.findall(r'(?:src|href)="([^"]+)"',text):
            if target.startswith(('#','http:','https:','data:')): continue
            assert (page.parent/unquote(target.split('?')[0])).exists(), (page.name,target)
    assert len(list(render_dir.rglob('*.png'))) == 36
    print(json.dumps({'output':str(OUT),'local_links_passed':True,'render_count':36},ensure_ascii=True),flush=True)

def write_pages(variants):
    style='''*{box-sizing:border-box}body{margin:0;background:#111b28;color:#e4edf5;font:15px/1.65 system-ui,Microsoft YaHei,sans-serif}header{padding:20px 26px}h1{margin:0 0 12px;font-size:26px}a{color:#a6d8ea}button,select{font:inherit;background:#273f53;color:#edf5fa;border:1px solid #678195;padding:8px 12px;border-radius:4px;cursor:pointer}button[aria-pressed=true]{background:#536d82}small{color:#aac1d0}.note{padding:12px 16px;border-left:3px solid #b79c6b;background:#1b2b3b}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;padding:0 26px 28px}.card{background:#19293a;border:1px solid #345069;border-radius:6px;overflow:hidden}.card img{display:block;width:100%;height:auto}.card p{margin:9px 15px}.controls{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0}.review{display:grid;grid-template-columns:1fr 310px;height:calc(100vh - 130px);min-height:600px}#stage{position:relative;min-height:500px;overflow:hidden}#stage canvas{width:100%;height:100%;display:block}#loading{position:absolute;top:16px;left:16px;background:#2b4458;padding:10px;z-index:2}aside{background:#1a2b3c;padding:16px;overflow:auto}aside select{display:block;width:100%;margin:8px 0}#legend img{width:35px;height:35px;vertical-align:middle;margin-right:8px;image-rendering:pixelated}.overview{width:100%;height:auto}iframe{width:100%;height:800px;border:1px solid #536e86}iframe[hidden]{display:none}@media(max-width:800px){.review{display:block;height:auto}#stage{height:65vh}header{padding:16px}.grid{padding:0 16px 20px}}'''
    cards=''.join('<article class="card" data-tractor="'+v['tractor']+'" data-kind="'+('loaded' if v['cargo'] else 'empty')+'"><a href="'+v['image']+'"><img loading="lazy" src="'+v['image']+'" alt="'+html.escape(v['label'])+'"></a><p><b>'+v['id']+'</b> · '+html.escape(v['label'])+'</p><p><button data-variant="'+v['id']+'">查看这辆三维</button> · '+str(v['blockCount'])+' 方块</p></article>' for v in variants)
    data=json.dumps([{k:v[k] for k in ('id','tractor','cargo','label')} for v in variants],ensure_ascii=False)
    page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I26车辆36项组合预览</title><style>'''+style+'''</style></head><body><header><h1>I26 · 32种挂箱组合 + 4种空载拖头</h1><p class="note">4色拖头 × 8色货柜＝32种挂箱组合；另列4种空载拖头，共36项。只制作独立外观预览，尚未摆回码头。</p><p>箱体与拖头沿用上轮实际方块造型和纹理，新增共用钢灰半挂底盘、后轮与连接部件；箱体接在牵引盘后方，后轮接地。挂箱外廓9宽×31长×15高，空载原拖头保持7宽×13长×10高。</p><p><a href="../I26_货柜八色与拖头四色_独立样件_V1_20261026/index.html">原独立样件</a> · <a href="36种车辆组合接触表.png">36项总接触表</a> · <a href="verification.json">同源与装配核验</a></p><div class="controls"><button id="random">随机搭配（32种挂箱）</button><button id="close">关闭三维</button><span id="picked"></span></div><iframe id="viewer" title="单辆车辆组合三维预览" hidden></iframe><div class="controls" id="filters"><button data-filter="all" aria-pressed="true">全部36项</button><button data-filter="loaded">挂箱32项</button><button data-filter="empty">空载4项</button>'''+''.join('<button data-filter="'+tier+'">'+tier+' '+color+'拖头</button>' for tier,color in TIERS[:4])+'''</div><small id="shown">36项；静态图片无需运行WebGL。点击三维时只载入一辆。</small></header><main class="grid">'''+cards+'''</main><script>const variants='''+data+''';const frame=document.getElementById('viewer');function openVariant(id){frame.src='三维评审.html?variant='+encodeURIComponent(id);frame.hidden=false;document.getElementById('picked').textContent=variants.find(v=>v.id===id).label;frame.scrollIntoView({behavior:'smooth',block:'start'});}for(const b of document.querySelectorAll('[data-variant]'))b.onclick=()=>openVariant(b.dataset.variant);document.getElementById('random').onclick=()=>{const loaded=variants.filter(v=>v.cargo);openVariant(loaded[Math.floor(Math.random()*loaded.length)].id);};document.getElementById('close').onclick=()=>{frame.removeAttribute('src');frame.hidden=true;};for(const b of document.querySelectorAll('[data-filter]'))b.onclick=()=>{let n=0;for(const c of document.querySelectorAll('.card')){c.hidden=!(b.dataset.filter==='all'||c.dataset.tractor===b.dataset.filter||c.dataset.kind===b.dataset.filter);if(!c.hidden)n++;}for(const v of document.querySelectorAll('[data-filter]'))v.setAttribute('aria-pressed',String(v===b));document.getElementById('shown').textContent=n+'项；点击图片打开原图，点击三维只载入一辆。';};</script></body></html>'''
    (OUT/'index.html').write_text(page,encoding='utf-8')
    review='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I26单辆组合三维</title><style>'''+style+'''</style></head><body><header><a href="index.html">← 全部36项</a><h1 id="title">I26 · 单辆组合预览</h1><small>同一时刻仅绘制一辆；空载与32种挂箱组合分别标记。</small></header><main class="review"><section id="stage"><div id="loading">载入真实方块纹理…</div></section><aside><label>拖头配色<select id="tractor">'''+''.join('<option value="'+t+'">'+t+' · '+c+'</option>' for t,c in TIERS[:4])+'''</select></label><label>挂箱状态<select id="cargo"><option value="EMPTY">空载拖头</option>'''+''.join('<option value="'+t+'">'+t+' · '+c+'货柜</option>' for t,c in TIERS)+'''</select></label><div class="controls"><button id="random">随机挂箱搭配</button><button id="prev">上一辆</button><button id="next">下一辆</button></div><div class="controls"><button data-view="iso">等轴</button><button data-view="front">正面</button><button data-view="side">侧面</button><button data-view="top">俯视</button><button id="reset">重置视角</button></div><p>左键旋转 · 右键平移 · 滚轮缩放</p><p id="counts"></p><p id="status"></p><div id="legend"></div><p><a id="image" href="#" target="_blank">打开这辆的静态原图</a></p><p class="note">建筑外观样件；未导入码头或实例，不表示可驾驶车辆实体、运输容量或物流功能。</p></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>'''
    (OUT/'三维评审.html').write_text(review,encoding='utf-8')

if __name__ == '__main__': main()
