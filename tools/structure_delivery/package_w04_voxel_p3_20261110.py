# -*- coding: utf-8 -*-
"""P3整机使用同一份整数格数据生成预览、材料表与完整导出。"""
from pathlib import Path
from types import SimpleNamespace
import base64,gzip,json,shutil
import numpy as np
import w04_voxel_p3_parts_20261110 as g
from package_w04_gemini_b1_20261110 import save,hashes
from w02_bunny_dock_geometry_v3_20261108 import encode
from build_i25_world_bubble_observatory_20261025 import resource_materials
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT=g.dragon.ROOT
OUT=ROOT/'deliveries/W04_完整真实方块_露首环链修订_P3_20261110'
LOG=ROOT/'logs/w04-voxel-p3-20261110'
SOURCES=[g.dragon.OUT,g.dragon.SWORD,ROOT/'deliveries/W04_中轴七雷三巴纹磁环_组合布局_P2_20261110']


def load_parts():
    source=np.load(LOG/'components.npz')
    return [SimpleNamespace(name=k[:-3],p=source[k],states=source[k[:-3]+'__states']) for k in source.files if k.endswith('__p')]


def contact_reason(a,b):
    names={a.split('_')[0],b.split('_')[0]}
    if names in [{'dragon'},{'sword'}]:return '源模型部件接缝，源形状保留'
    if b.startswith('field_03') and a.startswith(('field_01_3','field_02')):return '链端与外环／塔头设计接合'
    if a.startswith('dragon') and b.startswith('field_04'):return '母线接入龙体的设计接合'
    if a.startswith(('dragon','sword')) and b.startswith('field_05'):return '龙口／刀尖静态导流接触，详见交叠范围'
    if a.startswith('base_01') and b.startswith(('base_02','base_03','base_04')):return '基座与设备基础的设计接合'
    if a.startswith('field_02') and b.startswith('base_01'):return '塔基与甲板的设计接合'
    if a.startswith('field_04') and b.startswith('base_03'):return '母线与储能列的设计接合'
    if a.startswith('field_05') and b.startswith('base_02'):return '静态导流束与池心的设计接合'
    return None


def intersections(parts):
    rows=[];bounds=[(p.p.min(0),p.p.max(0)) for p in parts]
    for i,a in enumerate(parts):
        for j in range(i+1,len(parts)):
            b=parts[j];lo=np.maximum(bounds[i][0],bounds[j][0]);hi=np.minimum(bounds[i][1],bounds[j][1])
            if np.any(lo>hi):continue
            aa=a.p[np.all((a.p>=lo)&(a.p<=hi),axis=1)];bb=b.p[np.all((b.p>=lo)&(b.p<=hi),axis=1)]
            common,ai,_=np.intersect1d(encode(aa),encode(bb),assume_unique=True,return_indices=True)
            if len(common):
                q=aa[ai];reason=contact_reason(a.name,b.name)
                rows.append(dict(a=a.name,b=b.name,overlapping_cells=len(common),expected=bool(reason),
                    classification=reason or '待协调交叠，完整保留坐标与构件',bounds=dict(min=q.min(0).tolist(),max=q.max(0).tolist())))
    pending=[r for r in rows if not r['expected']]
    critical=[r for r in rows if (r['a'].startswith('field_01') and r['b'].startswith('field_01')) or
        (r['a'].startswith('field_01_2') and r['b'].startswith('field_03'))]
    report=dict(pairs=rows,unexpected_pairs=len(pending),unexpected_shared_cells=sum(r['overlapping_cells'] for r in pending),
        ring_ring_or_middle_ring_chain_pairs=critical,scope='完整29构件，合并之前的全部整数格；预期接合也逐项保留。',
        resolution='未删除交叠方块；合并采用清单后者覆盖前者，同时保留全部独立部件NPZ。')
    save(OUT/'交叠记录.json',report);return report


def head_visibility(parts):
    head=next(p.p for p in parts if p.name.startswith('dragon_01'))
    foreground=np.vstack([p.p for p in parts if p.name.startswith(('sword','field_01'))])
    lo=head.min(0);size=head.max(0)-lo+1
    front=np.full((size[1],size[0]),-9999,int)
    np.maximum.at(front,(head[:,1]-lo[1],head[:,0]-lo[0]),head[:,2])
    mask=(foreground[:,0]>=lo[0])&(foreground[:,0]<lo[0]+size[0])&(foreground[:,1]>=lo[1])&(foreground[:,1]<lo[1]+size[1])
    q=foreground[mask];covered=np.zeros_like(front,dtype=bool)
    at=(q[:,1]-lo[1],q[:,0]-lo[0]);block=q[:,2]>front[at];covered[at[0][block],at[1][block]]=True
    valid=front>-9999
    return dict(view='沿+Z看向-Z的正面正交投影，仅比较龙首与前景刀／磁环',head_silhouette_cells=int(valid.sum()),
        obscured_cells=int((covered&valid).sum()),obscured_percent=round(float((covered&valid).sum()/valid.sum()*100),3))


def main():
    OUT.mkdir(exist_ok=True);(OUT/'生成脚本').mkdir(exist_ok=True)
    before={p.name:hashes(p) for p in SOURCES};save(LOG/'sources-before.json',before)
    parts=load_parts();assert len(parts)==29
    save(LOG/'component-build.json',dict(parts=[dict(id=p.name,blocks=len(p.p),min=p.p.min(0).tolist(),max=p.p.max(0).tolist()) for p in parts]))
    collision=intersections(parts);visibility=head_visibility(parts)
    low=np.min([p.p.min(0) for p in parts],axis=0);high=np.max([p.p.max(0) for p in parts],axis=0);size=high-low+1
    print('合并整机',size.tolist(),flush=True)
    cube=np.zeros((size[1],size[2],size[0]),np.uint8);owner=np.zeros_like(cube)
    for i,p in enumerate(parts,1):
        assert np.issubdtype(p.p.dtype,np.integer)
        at=p.p-low;cube[at[:,1],at[:,2],at[:,0]]=p.states;owner[at[:,1],at[:,2],at[:,0]]=i
    used=np.unique(cube);used=used[used>0];states=[g.STATES[i-1] for i in used]
    remap=np.zeros(len(g.STATES)+1,np.uint8);remap[used]=np.arange(1,len(used)+1)
    cube=remap[cube];counts=np.bincount(cube.ravel(),minlength=len(states)+1)
    materials,sources,packs=resource_materials(states)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    save(OUT/'材料清单.json',[dict(state=s,count=int(counts[i])) for i,s in enumerate(states,1)])
    name='hk3gtl-w04-full-voxel-p3-20261110'
    print('完整NBT与Schematic导出及逐格回读',int(counts[1:].sum()),flush=True)
    exported=export_dense(cube,states,name,OUT)
    # 从整机最终表面按归属拆分预览，避免两个部件占据同一格时重复绘面。
    surfaces=exported.pop('surface_groups');previews=[];quads=0
    for i,p in enumerate(parts,1):
        at=p.p-low;chosen=owner[at[:,1],at[:,2],at[:,0]]==i;world=p.p[chosen]
        if not len(world):raise ValueError('部件被完全覆盖：'+p.name)
        lo=world.min(0);extent=world.max(0)-lo+1;origin=lo-low
        localgroups=[[[] for _ in range(6)] for _ in states]
        for material,faces in enumerate(surfaces):
            for face,indices in enumerate(faces):
                idx=np.asarray(indices,dtype=np.int64);idx=idx[owner.ravel()[idx]==i]
                x=idx%size[0]-origin[0];y=idx//(size[0]*size[2])-origin[1];z=idx//size[0]%size[2]-origin[2]
                localgroups[material][face]=((y*extent[2]+z)*extent[0]+x).tolist()
        starts,lengths,proof=merge_surface_runs(localgroups,extent.tolist());quads+=proof['rendered_quads']
        previews.append(dict(id=p.name,asset=p.name.split('_')[0],origin=origin.tolist(),size=extent.tolist(),
            starts=starts,lengths=lengths,blocks=len(world)))
        print('完整方块表面',p.name,len(world),flush=True)
    assert sum(p['blocks'] for p in previews)==int(counts[1:].sum())
    controller=np.array([0,18,419]);ports=[controller+[x,y,0] for x in [-1,0,1] for y in [-1,0,1] if (x,y)!=(0,0)]
    assert states[cube[tuple((controller-low)[[1,2,0]])]-1]==g.CONTROLLER
    assert all(states[cube[tuple((p-low)[[1,2,0]])]-1]==g.INTERFACE for p in ports)
    for x in range(-2,3):
        for y in range(14,22):
            for z in range(420,441):assert cube[y-low[1],z-low[2],x-low[0]]==0,'主控正前检修通道被封堵'
    detail=dict(reactor=dict(center=[0,15,235],half=[205,95,205]),dragon=dict(center=[0,385,-115],half=[465,210,310]),
        sword=dict(center=[0,330,325],half=[85,250,155]),field=dict(center=[0,180,250],half=[400,230,175]),
        head=dict(center=[0,495,125],half=[72,100,95]),casing=dict(center=[333,104,249],half=[19,15,18]),
        torii=dict(center=[0,80,465],half=[150,85,100]),magnet=dict(center=[124,30,359],half=[32,40,30]),
        controller=dict(center=[0,18,419],half=[8,7,10]))
    data=dict(name=name,title='W04 · 整机真实方块 P3',size=size.tolist(),blueprint_to_export_offset_xyz=(-low).tolist(),
        center_blueprint=[0,180,235],detail_views=detail,controller=(controller-low).tolist(),ports=[dict(pos=(p-low).tolist()) for p in ports])
    config=dict(data=data,audit=dict(viewer_rendered_quads=quads),materials=materials,parts=previews)
    (OUT/'data.js').write_text('window.W04_STATIC_PAYLOAD='+json.dumps(base64.b64encode(gzip.compress(json.dumps(config,ensure_ascii=False,separators=(',',':')).encode(),6)).decode())+';','utf8')
    source=(ROOT/'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110/生成脚本/viewer.mjs').read_text('utf8')
    source=source.replace('groups,setView,','groups,sceneryGroups:{},setView,')
    source=source.replace('texture.minFilter=THREE.NearestFilter;','texture.minFilter=THREE.NearestMipmapLinearFilter;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());')
    source=source.replace("if(name==='controller'&&data.controller)target.set(...data.controller);", "if(name==='controller'&&data.controller){target.set(...data.controller);direction.set(0,.2,1);}")
    source=source.replace("if(name==='side')direction.set(1,0,0);", "if(name==='side')direction.set(1,0,0);\n    if(name==='magnet')direction.set(1,.65,-.7);")
    source=source.replace('.multiplyScalar(1800)',".multiplyScalar(name==='magnet'?100:1800)")
    (OUT/'生成脚本/viewer.mjs').write_text(source,'utf8')
    issues=['W04正式控制器尚未注册；(0,18,419)使用真实红石块作为明确占位，周围八格为真实wonder_thunder_interface外观方块，非已验收GT功能接口。',
        '机械鬼手尚未制作；未在没有独立参考校准时凭空补入。',
        '本候选为完整静态体素与离线导出，外观待评审；没有游戏搭建、成型、运行或性能实测。']
    if collision['unexpected_pairs']:issues.append(f"仍有{collision['unexpected_pairs']}组待协调交叠，共{collision['unexpected_shared_cells']}次共享格记录；完整保留，见交叠记录。")
    if visibility['obscured_cells']:issues.append(f"正面正交投影中，刀／磁环仍遮住龙首轮廓{visibility['obscured_percent']}%；几何净空不等于视觉无遮挡。")
    manifest=dict(name=name,title=data['title'],nominal_size_xzy=[697,565,343],actual_scene_size_xyz=size.tolist(),
        bounds_world=dict(min=low.tolist(),max=high.tolist()),blueprint_to_export_offset_xyz=(-low).tolist(),whole_integer_voxel=True,
        components=len(parts),block_count=int(counts[1:].sum()),palette_count=len(states),scenery_geometry_count=0,
        source_component_blocks=sum(len(p.p) for p in parts),merge_rule='清单后者覆盖前者；独立源部件保存在日志components.npz，交叠记录不省略。',
        dragon_translation=g.DRAGON_SHIFT.tolist(),dragon_scale=1,dragon_material_map=g.DRAGON_MAP,
        sword_scale_before_revoxelization=g.SWORD_SCALE,sword_rotation_z_degrees=90,sword_rotation_x_degrees=g.ANGLE,
        runtime_model_scale=[1,1,1],runtime_model_rotation=[0,0,0],sword_anchor_world=g.SWORD_TARGET.tolist(),
        rings=[dict(radius=r,tilt_x=a,center=[0,180,235]) for r,a in g.RINGS],chain_inner_anchors=[[s*198,180,235] for s in [-1,1]],
        controller_world=controller.tolist(),controller_placeholder_state=g.CONTROLLER,controller_registered=False,ports_world=[p.tolist() for p in ports],
        materials=dict(states=states,resource_sources=sources,enabled_resource_packs=packs),head_visibility=visibility,
        known_issues=issues,animation_enabled=False,approved=False,game_verified=False,source_models_unchanged=True)
    save(OUT/'manifest.json',manifest)
    qa=dict(passed=True,integer_voxel_coordinates=True,whole_integer_voxel=True,no_scenery_meshes=True,
        size_xyz=size.tolist(),block_count=manifest['block_count'],complete_cube_materials=True,material_resources=sources,
        export=exported,collision_report=collision,head_visibility=visibility,source_models_unchanged=True,game_verified=False)
    save(LOG/'geometry-qa.json',qa)
    gallery=''.join(f'<figure><img src="{file}.png" alt="{file}"><figcaption>{file}</figcaption></figure>' for file in ['正面','侧面','俯视','龙首近景','真实机壳近景','三进鸟居','磁轭近景','正面隐藏七雷'])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{data['title']}</title><style>:root{{color-scheme:dark}}body{{max-width:1480px;margin:28px auto;padding:0 24px;background:#121b2b;color:#e3ebf5;font:17px/1.8 system-ui}}a{{color:#ef9ab2}}h1{{font-size:38px}}img{{width:100%;display:block}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0}}.note{{padding:16px;border-left:3px solid #C93F63;background:#291f30}}@media(max-width:800px){{.grid{{display:block}}}}</style><p>W04 · 雷之律者 · 静态整机候选</p><h1>俱利伽罗 × 鸣雷见<br>完整真实方块 P3</h1><p class="note">底盘、下沉雷池、十座储能塔与三进鸟居全部换成真实方块；七雷在64%与前后倾转22°后重新体素化，预览的每格均为1×1×1。主甲使用HRV绯雷红机壳、黑石砖、深板岩与金属块，使用目标实例及项目真实模型／贴图资源。没有建筑草模或动画，继续沿用W03／休伯利安评审操作。</p><p><a href="三维布局.html">打开原版界面三维评审</a> · <a href="../{SOURCES[-1].name}/index.html">P2历史</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p><img src="整体斜视.png" alt="完整真实方块P3"><p>实际宽{size[0]}×深{size[2]}×高{size[1]}格，{manifest['block_count']:,}个真实方块，{len(states)}种真实材质，{len(parts)}个构件。边界按完整几何计算，名义697×565×343未用作裁切窗口。</p><p>龙整体抬高至平移(0,185,-40)，保留D4源形状；三环半径105／142／190，链内端外移至X=±198。正面龙首遮挡{visibility['obscured_percent']}%。环—环／中环—链端当前交叠{len(collision['ring_ring_or_middle_ring_chain_pairs'])}组，整机另有{collision['unexpected_pairs']}组待协调交叠。</p><div class="grid">{gallery}</div><div class="note">{''.join('<p>'+x+'</p>' for x in issues)}</div><p><a href="{name}.nbt">完整整机NBT</a> · <a href="{name}.schem">完整整机Schematic</a> · <a href="材料清单.json">完整材料清单</a> · <a href="manifest.json">坐标与材质来源</a> · <a href="交叠记录.json">完整交叠记录</a> · <a href="verification.json">离线核验</a></p></html>''','utf8')
    from restore_w04_review_ui_20261110 import install
    install(OUT)
    for file in [Path(__file__).name,'w04_voxel_p3_parts_20261110.py','restore_w04_review_ui_20261110.py','w04_review_ui_20261110.mjs']:
        shutil.copy2(ROOT/'tools/structure_delivery'/file,OUT/'生成脚本'/file)
    assert before=={p.name:hashes(p) for p in SOURCES}
    print(json.dumps(dict(passed=True,size_xyz=size.tolist(),blocks=manifest['block_count'],unexpected_pairs=collision['unexpected_pairs'],head_visibility=visibility),ensure_ascii=False),flush=True)


if __name__=='__main__':main()
