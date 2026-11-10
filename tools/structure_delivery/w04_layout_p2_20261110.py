# -*- coding: utf-8 -*-
"""中轴七雷与三巴纹环塔的P2摆位；底盘和鸟居保留P1草模。"""
from pathlib import Path
import base64,gzip,json,shutil
import numpy as np
import w04_kurikara_d4_20261110 as g
import w04_layout_p2_parts_20261110 as geom
from w04_layout_p1_20261110 import payload,translation,transform,hull_points
from w02_bunny_dock_geometry_v3_20261108 import encode
from build_i25_world_bubble_observatory_20261025 import resource_materials
from i34_open_observatory_export_20261027 import export_dense,surface_groups
from i37_surface_runs_20261027 import merge_surface_runs
from package_w04_gemini_b1_20261110 import save,hashes

P1=g.ROOT/'deliveries/W04_龙踞雷池七雷镇枢_组合布局_P1_20261110'
OUT=g.ROOT/'deliveries/W04_中轴七雷三巴纹磁环_组合布局_P2_20261110'
LOG=g.ROOT/'logs/w04-layout-p2-20261110'


def asset_cells(npz,asset):
    points=np.vstack([npz[k] for k in npz.files if k.endswith('__p')])
    if asset=='dragon':return points+np.array([0,100,-70])
    # 90度旋转和等比缩放后仍为轴对齐小方块，计算其覆盖的所有整数单元。
    center=points+.5
    x=(53-center[:,1])*.72;y=95+(center[:,0]-5)*.72;z=235+center[:,2]*.72
    center=np.c_[x,y,z];lo=np.floor(center-.36+1e-8).astype(int);hi=np.ceil(center+.36-1e-8).astype(int)-1
    chunks=[]
    for x in [0,1]:
        for y in [0,1]:
            for z in [0,1]:
                at=lo+[x,y,z];chunks.append(at[np.all(at<=hi,axis=1)])
    all_=np.vstack(chunks);_,index=np.unique(encode(all_),return_index=True)
    return all_[index]


def intersections(parts):
    assets={'dragon':asset_cells(np.load(g.LOG/'components.npz'),'dragon'),
        'sword':asset_cells(np.load(g.ROOT/'logs/w04-narukami-study-20261110/s1-components.npz'),'sword')}
    rows=[]
    def compare(a,b,an,bn,classification):
        lo=np.maximum(a.min(0),b.min(0));hi=np.minimum(a.max(0),b.max(0))
        if np.any(lo>hi):return
        aa=a[np.all((a>=lo)&(a<=hi),axis=1)];bb=b[np.all((b>=lo)&(b<=hi),axis=1)]
        common,ia,_=np.intersect1d(encode(aa),encode(bb),return_indices=True)
        if len(common):
            q=aa[ia];rows.append(dict(a=an,b=bn,overlapping_cells=len(common),classification=classification,
                bounds=dict(min=q.min(0).tolist(),max=q.max(0).tolist())))
    for name,points in assets.items():
        for p in parts:
            intended=p.name.startswith(('P2_04','P2_05'))
            compare(points,p.p,name,p.name,'设计导流接合，细部待评审' if intended else '待协调干涉，原坐标保留')
    for i,a in enumerate(parts):
        for b in parts[i+1:]:
            intended=(a.name.startswith(('P2_01_3','P2_02')) and b.name.startswith('P2_03')) or a.name.startswith('P2_04') and b.name.startswith('P2_05')
            compare(a.p,b.p,a.name,b.name,'链端与磁环／塔头预期接合' if intended else '待协调交叠，原坐标保留')
    result=dict(pairs=rows,unexpected_pairs=sum(r['classification'].startswith('待协调') for r in rows),
        scope='D4与S1及新增体素构件；P1非体素底盘、低压塔和鸟居未纳入逐格碰撞判定',
        resolution='保留全部构件与坐标，未为消除交叠而移动、缩短或删除。')
    save(OUT/'交叠记录.json',result);return result


def package_new_parts(parts):
    low=np.min([p.p.min(0) for p in parts],axis=0);high=np.max([p.p.max(0) for p in parts],axis=0);size=high-low+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8);owner=np.zeros_like(cube)
    for i,p in enumerate(parts,1):
        at=p.p-low;cube[at[:,1],at[:,2],at[:,0]]=p.states;owner[at[:,1],at[:,2],at[:,0]]=i
    view=OUT/'体素环塔';view.mkdir(exist_ok=True)
    used=np.unique(cube);used=used[used>0];export_states=[geom.STATES[i-1] for i in used]
    remap=np.zeros(len(geom.STATES)+1,np.uint8);remap[used]=np.arange(1,len(used)+1)
    exported=export_dense(remap[cube],export_states,'hk3gtl-w04-p2-field-components-20261110',view)
    materials,sources,packs=resource_materials(geom.STATES);previews=[];quads=0
    for i,p in enumerate(parts,1):
        at=p.p-low;chosen=owner[at[:,1],at[:,2],at[:,0]]==i;world=p.p[chosen];states=p.states[chosen]
        lo=world.min(0);extent=world.max(0)-lo+1;local=np.zeros((extent[1],extent[2],extent[0]),np.uint8)
        at=world-lo;local[at[:,1],at[:,2],at[:,0]]=states
        starts,lengths,proof=merge_surface_runs(surface_groups(local,geom.STATES),extent.tolist());quads+=proof['rendered_quads']
        previews.append(dict(id=p.name,origin=lo.tolist(),size=extent.tolist(),starts=starts,lengths=lengths,blocks=len(world)))
        print('新增体素表面',p.name,len(world),flush=True)
    np.savez_compressed(LOG/'components.npz',**{p.name+'__'+k:v for p in parts for k,v in [('p',p.p),('states',p.states)]})
    return dict(materials=materials,parts=previews,quads=quads,export=exported,
        size=size.tolist(),bounds=dict(min=low.tolist(),max=high.tolist()),blueprint_to_export_offset_xyz=(-low).tolist(),
        block_count=int(np.count_nonzero(cube)),material_resource_sources=sources,enabled_resource_packs=packs)


def main():
    OUT.mkdir(exist_ok=True);LOG.mkdir(exist_ok=True);(OUT/'生成脚本').mkdir(exist_ok=True)
    before={p.name:hashes(p) for p in [P1,g.OUT,g.SWORD]};save(LOG/'sources-before.json',before)
    parts=geom.build();collision=intersections(parts);new=package_new_parts(parts)
    dragon=payload(g.OUT/'dragon/data.js');sword=payload(g.SWORD/'weapon/data.js')
    dm=translation([0,100,-70])@translation(-np.array(dragon['data']['blueprint_to_export_offset_xyz']))
    rotation=np.array([[0,-1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]],float)
    sm=translation([0,95,235])@rotation@np.diag([.72,.72,.72,1])@translation([-5,-53,0])@translation(-np.array(sword['data']['blueprint_to_export_offset_xyz']))
    dp=transform(hull_points(dragon['data']),dm);sp=transform(hull_points(sword['data']),sm)
    gap=float(sp[:,2].min()-dp[:,2].max());assert gap>60
    # 新构件的边界与旧完整模型共同决定范围，禁止按名义尺寸截断。
    newpoints=np.vstack([p.p for p in parts]);nlo=newpoints.min(0);nhi=newpoints.max(0)+1
    corner=lambda lo,hi:np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]])
    points=np.vstack([dp,sp,corner(nlo,nhi),corner([-470,0,-470],[470,112,435])])
    low=np.floor(points.min(0));high=np.ceil(points.max(0));offset=-low;size=(high-low).astype(int)
    configs=[('dragon',dragon,dm),('sword',sword,sm),('field',new,np.eye(4))]
    materials=sum([c['materials'] for _,c,_ in configs],[]);previews=[];first=0
    for asset,config,matrix in configs:
        for raw in config['parts']:
            p=dict(raw);p['id']=asset+'_'+p['id'];p['asset']=asset
            for key in ['starts','lengths']:
                p[key]=[[[] for _ in range(6)] for _ in range(first)]+raw[key]+[[[] for _ in range(6)] for _ in range(len(materials)-first-len(config['materials']))]
            p['placement_matrix']=(translation(offset)@matrix).T.ravel().tolist();previews.append(p)
        first+=len(config['materials'])
    controller=[0,18,419];ports=[dict(pos=[x,18+y,419]) for x in [-1,0,1] for y in [-1,0,1] if (x,y)!=(0,0)]
    data=dict(name='hk3gtl-w04-layout-p2-20261110',title='W04 · 中轴七雷与三巴纹磁环 P2',size=size.tolist(),
        blueprint_to_export_offset_xyz=offset.tolist(),fit_points=(points+offset).tolist(),center_blueprint=[0,180,235],
        detail_views=dict(reactor=dict(center=[0,100,235],half=[210,145,180]),
            sword=dict(center=[0,355,235],half=[70,280,50]),field=dict(center=[0,180,250],half=[400,180,140]),
            dragon=dict(center=[0,295,-105],half=[465,210,310])),controller=(np.array(controller)+offset).tolist(),
        ports=[dict(pos=(np.array(p['pos'])+offset).tolist()) for p in ports])
    config=dict(data=data,audit=dict(viewer_rendered_quads=dragon['audit']['viewer_rendered_quads']+sword['audit']['viewer_rendered_quads']+new['quads']),
        materials=materials,parts=previews)
    (OUT/'data.js').write_text('window.W04_STATIC_PAYLOAD='+json.dumps(base64.b64encode(gzip.compress(json.dumps(config,ensure_ascii=False,separators=(',',':')).encode(),6)).decode())+';','utf8')
    source=(P1/'生成脚本/viewer.mjs').read_text('utf8')
    old=(g.ROOT/'tools/structure_delivery/w04_layout_p1_scenery_20261110.mjs').read_text('utf8');scenery=old
    start=scenery.index('  // 静态能量联系示意');end=scenery.index('  // 前庭控制器',start)
    scenery=scenery[:start]+scenery[end:]
    scenery=scenery.replace("    line([sign*95,37,250],[sign*105,38,300],3,colors.red);\n    line([sign*105,38,300],[0,48,235],3,colors.red);",'')
    scenery=scenery.replace("cylinder([0,32,235],17,40,colors.red,'energy');cylinder([0,54,235],9,6,colors.white,'energy');\n  line([0,58,235],[0,91,235],2,colors.light);", "cylinder([0,42,235],17,60,colors.red,'energy');cylinder([0,75,235],9,6,colors.white,'energy');")
    scenery=scenery.replace("label('鸣雷见：终端约束刀',[-255,382,262])","label('鸣雷见：中轴镇枢',[110,552,260])")
    scenery=scenery.replace("label('共同雷池',[175,69,290])","label('三巴纹雷鼓磁环',[205,350,295]);label('共同雷池',[175,69,290])")
    assert old in source;source=source.replace(old,scenery)
    source=source.replace("if(name==='sword')direction.set(-.55,.2,1.2);","if(name==='sword')direction.set(-.55,.2,1.2);\n    if(name==='field')direction.set(-.45,.3,1.2);")
    (OUT/'生成脚本/viewer.mjs').write_text(source,'utf8');(OUT/'生成脚本/scenery.mjs').write_text(scenery,'utf8')
    page=(P1/'三维布局.html').read_text('utf8').replace('龙踞雷池·七雷镇枢 P1','中轴七雷与三巴纹磁环 P2')
    page=page.replace('龙在后上空；七雷斜悬前方，刀尖对准同一雷池。模型全静态，设施为摆位草模。','七雷中轴倒悬；三巴纹磁环与双侧鬼角塔为真实体素。底盘与鸟居保留草模，无动画。')
    page=page.replace('组合缩放58%','组合缩放72%').replace('<button data-view="reactor">','<button data-view="field">环塔近景</button><button data-view="reactor">')
    page=page.replace('<label><input type="checkbox" data-scenery="base"','<label><input type="checkbox" data-asset="field" checked>体素环塔／母线／电弧</label><label><input type="checkbox" data-scenery="base"')
    page=page.replace('工业装置与能量线尚为设计示意。','新增环塔、母线与电弧已有体素局部导出；底盘、低压塔与鸟居仍为草模。正面中轴刀会遮挡部分龙首，保留原坐标待评审。')
    (OUT/'三维布局.html').write_text(page,'utf8')
    issues=['七雷中轴刀在纯正面投影中遮挡部分龙首及胸腹；前后净空不等于不遮挡。',
        '刀由58%提高到72%后高于龙角；实际高度超过343格，未裁切或压缩。',
        '底盘、低压电容列与鸟居仍为Three.js草模，不提供完整整机NBT。',
        '鬼胄巨手未制作；当前选择双侧鬼角电容塔候选。']
    manifest=dict(name=data['name'],title=data['title'],nominal_size_xzy=[697,565,343],actual_scene_size_xyz=size.tolist(),
        bounds_world=dict(min=low.tolist(),max=high.tolist()),dragon_translation=[0,100,-70],dragon_scale=1,sword_scale=.72,
        sword_z_rotation_degrees=90,sword_blade_anchor_world=[0,95,235],reactor_core_world=[0,75,235],
        rings=[dict(radius=r,tilt_x=a,center=geom.CENTER.tolist()) for r,a in geom.RINGS],
        dragon_sword_z_gap=gap,controller_world=controller,ports_world=[p['pos'] for p in ports],
        new_voxel_components=len(parts),new_voxel_blocks=new['block_count'],new_voxel_export=dict(size_xyz=new['size'],bounds_blueprint=new['bounds'],
            blueprint_to_export_offset_xyz=new['blueprint_to_export_offset_xyz'],scope='仅新增体素环塔、链环、母线和电弧，不含D4、S1或底座草模'),
        materials=dict(states=geom.STATES,resource_sources=new['material_resource_sources']),known_issues=issues,
        source_geometry_unchanged=True,animation_enabled=False,approved=False,game_verified=False)
    save(OUT/'manifest.json',manifest)
    save(LOG/'geometry-qa.json',dict(passed=True,actual_scene_size_xyz=size.tolist(),new_voxel_export=new['export']['readback'],
        new_voxel_export_hashes=new['export']['hashes'],new_voxel_blocks=new['block_count'],
        source_models_unchanged=True,dragon_sword_z_gap=gap,collision_report=collision,known_issues=issues))
    gallery=''.join(f'<img src="{file}.png" alt="{file}">' for file in ['正面','侧面','俯视','环塔近景','正面隐藏七雷','正面隐藏环塔'])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title><style>:root{{color-scheme:dark}}body{{max-width:1480px;margin:28px auto;padding:0 24px;background:#18101c;color:#eadfe6;font:17px/1.9 system-ui}}h1{{font-size:38px}}a{{color:#f2a1b7}}img{{width:100%;display:block}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.note{{padding:16px 20px;border-left:3px solid #C93F63;background:#321b28}}@media(max-width:800px){{.grid{{display:block}}}}</style><p>W04 · 雷之律者 · 静态组合候选</p><h1>中轴七雷 · 三巴纹磁环<br>环塔布局 P2</h1><p class="note">先确定中高空构图：鸣雷见72%中轴倒悬，刀尖对准(0,75,235)的雷池，三道倾斜双轨雷鼓环包围中下段；双侧鬼角电容塔以交替链环锁控外环。新增母线廊桥与螺旋电弧使用体素方块，替代P1细圆柱联系线；不改变D4龙体或S1刀的源形态。</p><p><a href="三维布局.html">打开静态三维布局</a> · <a href="../{P1.name}/index.html">P1原摆位</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p><img src="整体斜视.png" alt="中轴七雷与环塔完整预览"><p>完整场景宽{size[0]}×深{size[2]}×高{size[1]}格；龙保持1:1，原位(0,100,-70)。刀与龙前后净空{gap:.2f}格。三环中心(0,180,235)，半径110／145／175格，X倾角18°／−22°／35°；双侧鬼角电容塔最高303格。</p><p>新增{len(parts)}个体素构件，合并{new['block_count']:,}方块；真实材质包括HRV绯雷红机壳、深板岩瓦、黑色混凝土、少量金导体与灯芯玻璃。局部NBT及Schematic可逐格回读，不把纯色底盘草模算进真实方块量。</p><div class="grid">{gallery}</div><p class="note">纯正面视角中，中轴刀会遮挡部分龙首／胸腹；未擅自把龙移走。新增构件交叠{len(collision['pairs'])}对，其中{collision['unexpected_pairs']}对待协调，见完整交叠记录。底盘、低压塔、鸟居仍为草模，巨手尚未制作；当前不是完整整机体素蓝图，未注册或游戏实装。</p><p><a href="manifest.json">摆位／尺寸／待评审项</a> · <a href="交叠记录.json">完整交叠记录</a> · <a href="verification.json">离线核验</a> · <a href="体素环塔/hk3gtl-w04-p2-field-components-20261110.nbt">新增环塔局部NBT</a> · <a href="体素环塔/hk3gtl-w04-p2-field-components-20261110.schem">新增环塔局部Schematic</a></p></html>''','utf8')
    assert before=={p.name:hashes(p) for p in [P1,g.OUT,g.SWORD]}
    for name in [Path(__file__).name,'w04_layout_p2_parts_20261110.py']:shutil.copy2(g.ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    from restore_w04_review_ui_20261110 import install
    install(OUT)
    print(json.dumps(dict(size_xyz=size.tolist(),new_voxel_blocks=new['block_count'],new_parts=len(parts),collision_pairs=len(collision['pairs']),unexpected_pairs=collision['unexpected_pairs'])))


if __name__=='__main__':main()
