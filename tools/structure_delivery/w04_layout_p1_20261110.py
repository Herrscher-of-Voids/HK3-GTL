# -*- coding: utf-8 -*-
"""用已制作的龙与七雷表面生成静态整机摆位；工业设施仅为体量草模。"""
from pathlib import Path
import base64,gzip,json,hashlib,math,shutil
import numpy as np
import w04_kurikara_d4_20261110 as g
from package_w04_gemini_b1_20261110 import save,hashes

OUT=g.ROOT/'deliveries/W04_龙踞雷池七雷镇枢_组合布局_P1_20261110'
LOG=g.ROOT/'logs/w04-layout-p1-20261110'


def payload(path):
    text=path.read_text('utf8');return json.loads(gzip.decompress(base64.b64decode(json.loads(text.split('=',1)[1].rstrip(';')))))


def translation(p):
    m=np.eye(4);m[:3,3]=p;return m


def transform(points,m):
    return (np.c_[points,np.ones(len(points))]@m.T)[:,:3]


def hull_points(data):
    points=data.get('fit_points')
    if points is None:
        points=[[x,y,z] for x in [0,data['size'][0]] for y in [0,data['size'][1]] for z in [0,data['size'][2]]]
        return np.array(points,float)
    return np.array([np.array(p)+[x,y,z] for p in points for x in [0,1] for y in [0,1] for z in [0,1]])


def main():
    OUT.mkdir(exist_ok=True);LOG.mkdir(exist_ok=True);(OUT/'生成脚本').mkdir(exist_ok=True)
    dragon=payload(g.OUT/'dragon/data.js');sword=payload(g.SWORD/'weapon/data.js')
    sources={p.name:hashes(p) for p in [g.OUT,g.SWORD]};save(LOG/'sources-before.json',sources)
    dm=translation([0,100,-70])@translation(-np.array(dragon['data']['blueprint_to_export_offset_xyz']))
    rotation=np.eye(4);a=math.radians(120);rotation[:2,:2]=[[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]]
    scale=np.diag([.58,.58,.58,1])
    sm=translation([0,95,235])@rotation@scale@translation([-5,-53,0])@translation(-np.array(sword['data']['blueprint_to_export_offset_xyz']))
    dp=transform(hull_points(dragon['data']),dm);sp=transform(hull_points(sword['data']),sm)
    gap=float(sp[:,2].min()-dp[:,2].max());assert gap>65,'刀与龙前后净空不足'
    materials=dragon['materials']+sword['materials'];parts=[]
    for asset,config,m,first in [('dragon',dragon,dm,0),('sword',sword,sm,len(dragon['materials']))]:
        for raw in config['parts']:
            part=dict(raw);part['id']=asset+'_'+part['id'];part['asset']=asset
            for key in ['starts','lengths']:
                part[key]=[[[] for _ in range(6)] for _ in range(first)]+raw[key]+[[[] for _ in range(6)] for _ in range(len(materials)-first-len(config['materials']))]
            part['placement_matrix']=m.T.ravel().tolist();parts.append(part)
    # 草模占地由完整龙翼与尾部求得，不把名义尺寸作为裁切框。
    bounds=np.array([[-470,0,-470],[470,515,435]],float)
    points=np.vstack([dp,sp,np.array([[x,y,z] for x in bounds[:,0] for y in bounds[:,1] for z in bounds[:,2]])])
    lo=np.floor(points.min(0));hi=np.ceil(points.max(0));offset=-lo;size=(hi-lo).astype(int)
    for part in parts:
        m=np.array(part['placement_matrix']).reshape(4,4).T
        part['placement_matrix']=(translation(offset)@m).T.ravel().tolist()
    core=[0,55,235];controller=[0,18,419]
    ports=[dict(pos=[x,18+y,419]) for x in [-1,0,1] for y in [-1,0,1] if (x,y)!=(0,0)]
    views=dict(reactor=dict(center=[-40,90,235],half=[180,110,170]),
        dragon=dict(center=[0,295,-105],half=[465,210,310]),
        sword=dict(center=[-110,265,235],half=[165,205,55]))
    data=dict(name='hk3gtl-w04-layout-p1-20261110',title='W04 · 龙踞雷池·七雷镇枢 P1',size=size.tolist(),
        blueprint_to_export_offset_xyz=offset.tolist(),fit_points=(points+offset).tolist(),
        center_blueprint=core,detail_views=views,controller=(np.array(controller)+offset).tolist(),
        ports=[dict(pos=(np.array(i['pos'])+offset).tolist()) for i in ports])
    audit=dict(viewer_rendered_quads=dragon['audit']['viewer_rendered_quads']+sword['audit']['viewer_rendered_quads'])
    config=dict(data=data,audit=audit,materials=materials,parts=parts)
    (OUT/'data.js').write_text('window.W04_STATIC_PAYLOAD='+json.dumps(base64.b64encode(gzip.compress(json.dumps(config,ensure_ascii=False,separators=(',',':')).encode(),6)).decode())+';','utf8')
    source=(g.ROOT/'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110/生成脚本/viewer.mjs').read_text('utf8')
    source=source.replace('scene.add(group);groups.push(group);','group.applyMatrix4(new THREE.Matrix4().fromArray(part.placement_matrix));scene.add(group);groups.push(group);')
    source=source.replace("if(name==='back')direction.set(0,.15,-1);","if(name==='back')direction.set(0,.15,-1);\n    if(name==='sword')direction.set(-.55,.2,1.2);\n    if(name==='reactor')direction.set(-.6,.9,1.4);")
    scenery=(g.ROOT/'tools/structure_delivery/w04_layout_p1_scenery_20261110.mjs').read_text('utf8')
    source=source.replace('  const clippingPlane=',scenery+'\n  const clippingPlane=')
    source=source.replace("const box=new THREE.Box3(new THREE.Vector3(...item.pos).addScalar(-.8),new THREE.Vector3(...item.pos).addScalar(1.8));","const box=new THREE.Box3(new THREE.Vector3(...item.pos).addScalar(-.2),new THREE.Vector3(...item.pos).addScalar(1.2));")
    source=source.replace("let renderedQuads=0;","let renderedQuads=0;")
    source=source.replace('    let limit=0;','    let limit=0;')
    source=source.replace("  function resize()", "  function resize()")
    # 原始相机按完整包围盒取景；草模也在该边界内。
    source=source.replace('groups,setView,','groups,setView,sceneryGroups,')
    source=source.replace("  document.getElementById('reset').onclick", "  document.querySelectorAll('[data-asset]').forEach(e=>e.onchange=()=>{groups.filter(g=>g.name.startsWith(e.dataset.asset+'_')).forEach(g=>g.visible=e.checked);draw();});\n  document.querySelectorAll('[data-scenery]').forEach(e=>e.onchange=()=>{sceneryGroups[e.dataset.scenery].visible=e.checked;draw();});\n  document.getElementById('reset').onclick")
    (OUT/'生成脚本/viewer.mjs').write_text(source,'utf8')
    buttons=''.join(f'<button data-view="{key}">{label}</button>' for key,label in [('front','整体斜视'),('orthofront','正面'),('side','侧面'),('back','背面'),('top','俯视'),('reactor','雷池与刀尖'),('dragon','龙体'),('sword','七雷'),('controller','控制器位置')])
    (OUT/'三维布局.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title><style>:root{{color-scheme:dark}}body{{margin:0;color:#eadfe5;background:#18101c;font:15px/1.7 system-ui}}header,.tools{{padding:12px 22px}}h1{{font-size:25px;margin:4px 0}}a{{color:#f1a7bb}}button{{padding:7px 12px;margin:3px;background:#4c2034;border:1px solid #ad5572;color:inherit;border-radius:6px}}#stage{{height:75vh;position:relative;min-height:450px}}canvas{{display:block}}#loading{{position:absolute;top:20px;left:20px}}label{{margin-right:20px}}.note{{color:#c6b5c1}}</style><header><a href="index.html">← 组合说明</a><h1>{data['title']}</h1><p>龙在后上空；七雷斜悬前方，刀尖对准同一雷池。模型全静态，设施为摆位草模。</p>{buttons}<button id="reset">复位</button></header><div id="stage"><span id="loading">加载两个独立模型…</span></div><div class="tools"><p id="stats"></p><label><input type="checkbox" data-asset="dragon" checked>俱利伽罗D4</label><label><input type="checkbox" data-asset="sword" checked>鸣雷见S1（组合缩放58%）</label><label><input type="checkbox" data-scenery="base" checked>工业船坞草模</label><label><input type="checkbox" data-scenery="energy" checked>能量联系示意</label><label><input type="checkbox" data-scenery="labels" checked>部件标签</label><label><input id="ports" type="checkbox">主控与8接口框</label><label hidden><input id="glass" type="checkbox" checked>玻璃</label><label hidden>剖切<input id="layer" type="range" min="0" max="{size[1]}" value="{size[1]}"><span id="layerLabel">{size[1]}</span></label><p class="note">左键转镜头，右键平移，滚轮缩放。龙与刀保留既有形态，仅做整组摆位；无动画、无整机注册或游戏测试。工业装置与能量线尚为设计示意。</p></div><script src="data.js"></script><script src="viewer.bundle.js"></script></html>''','utf8')
    manifest=dict(name=data['name'],title=data['title'],nominal_size_xzy=[697,565,343],actual_scene_size_xyz=size.tolist(),
        bounds_world=dict(min=lo.tolist(),max=hi.tolist()),dragon_translation=[0,100,-70],dragon_scale=1,
        sword_scale=.58,sword_z_rotation_degrees=120,sword_blade_anchor_world=[0,95,235],
        dragon_sword_z_gap=gap,reactor_core_world=core,controller_world=controller,
        ports_world=[p['pos'] for p in ports],controller_registered=False,industrial_facilities='体量草模，非逐格多方块蓝图',
        effects='静态设计示意',source_files_unchanged=True,animation_enabled=False,approved=False,game_verified=False)
    save(OUT/'manifest.json',manifest)
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title><style>:root{{color-scheme:dark}}body{{max-width:1450px;margin:28px auto;padding:0 22px;background:#18101c;color:#ede1e9;font:17px/1.9 system-ui}}h1{{font-size:38px}}a{{color:#f3a4ba}}img{{width:100%;display:block}}.note{{padding:16px 20px;background:#321c29;border-left:3px solid #C93F63}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}@media(max-width:800px){{.grid{{display:block}}}}</style><p>W04 · 雷之律者 · 鸣霆·超导电磁天枢</p><h1>龙踞雷池 · 七雷镇枢<br>静态组合摆位 P1</h1><p class="note">建议把俱利伽罗作为后上方的主导流龙体，把超限七雷作为前方的终端磁约束刀。两者共同服务中央雷池：超导储能列 → 龙体导流 → 雷池约束 → 七雷汇聚。此为本模组机器机制的设计候选，不是官方设定，也未接入运行逻辑。</p><p><a href="三维布局.html">打开可转镜头的静态三维布局</a> · <a href="../{g.OUT.name}/index.html">D4龙体与同机位对照</a> · <a href="../{g.SWORD.name}/index.html">原始七雷S1</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p><img src="整体斜视.png" alt="龙与七雷组合斜视"><p>后上空保留完整展翼与厚尾；七雷斜悬前方，刀尖向下对准池心，与龙前后分层。龙体保持1:1，七雷仅在组合中等比缩至58%，源模型不改。龙与刀前后至少{gap:.1f}格净空；取景包含完整部件，未裁切到名义697×565×343。</p><div class="grid"><img src="正面.png" alt="组合正面"><img src="侧面.png" alt="组合侧面"><img src="俯视.png" alt="组合俯视"><img src="雷池与刀尖.png" alt="雷池刀尖关系"></div><p>低矮超导设备列和分流导槽铺在龙下方，保持龙首、胸腹与刀轮廓清楚。前庭用小型鸟居收口，控制器及周围同一平面3×3的8接口嵌入墙面；这里的控制器和接口仍是位置示意。</p><p class="note">设施为体量草模，尚未细化为完整方块结构；模型比例和刀的摆位待评审。无动画，未游戏实装、成型或运行验证，不替换旧整机候选，不增加完成度。</p><p><a href="manifest.json">摆位与尺寸记录</a> · <a href="verification.json">离线核验</a></p></html>''','utf8')
    assert sources=={p.name:hashes(p) for p in [g.OUT,g.SWORD]}
    for name in [Path(__file__).name,'w04_layout_p1_scenery_20261110.mjs']:shutil.copy2(g.ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    from restore_w04_review_ui_20261110 import install
    install(OUT)
    print(json.dumps(dict(passed=True,actual_scene_size_xyz=size.tolist(),dragon_sword_z_gap=gap)))


if __name__=='__main__':main()
