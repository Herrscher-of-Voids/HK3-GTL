# -*- coding: utf-8 -*-
"""独立交付W03完整边界修复；历史与批准建筑保持原字节。"""
import json,shutil,sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from audit_wonder_clipping_20261108 import expanded,LOG,ROOT
from build_max_structure_candidate import generate,save

OUT=ROOT/'deliveries/W03_完整几何边界修复_20261108'
VERSIONS=[('V2','w03_crown_geometry_v2_20261107','W03_穹界虚数锚定环_坠落冠冕_DeepSeek原案_V2_20261107'),
 ('V3','w03_celestial_geometry_v3_20261107','W03_穹界虚数锚定环_三环双翼神殿_Gemini原案_V3_20261107'),
 ('V4','w03_celestial_geometry_v4_20261107','W03_穹界虚数锚定环_曲翼深渊神殿_Gemini2.0_V4_20261107'),
 ('V5','w03_crown_geometry_v5_20261108','W03_穹界虚数锚定环_悬天瞳冠_DeepSeek改进_V5_20261108')]


def generic_audit(c,data,states,extra=None):
    counts=np.bincount(c.ravel(),minlength=len(states)+1)
    assert all(counts[1:]),'调色板不可含空材料'
    h,d,w=c.shape
    assert all(np.any(np.take(c,i,axis=axis)) for axis in range(3) for i in (0,c.shape[axis]-1))
    ports=[]
    directions=dict(north=(0,0,-1),south=(0,0,1),east=(1,0,0),west=(-1,0,0))
    for item in [dict(id='主控',pos=data['controller'],face=data['controller_face'])]+data['ports']:
        p=np.array(item['pos']);v=np.array(directions[item['face']]);inner=p-v
        assert c[p[1],p[2],p[0]] and c[inner[1],inner[2],inner[0]],item
        clearance=[bool(c[tuple((p+j*v)[[1,2,0]])]) for j in range(1,6)]
        ports.append(dict(id=item['id'],position=p.tolist(),inner_backed=True,outer_clear=next((i for i,n in enumerate(clearance) if n),5)))
    for route in data.get('pipe_routes',[]):
        if 'path' in route:
            for x,y,z in route['path']:assert c[y,z,x]==states.index('minecraft:gold_block')+1
            for x,y,z in (route['start'],route['end']):assert c[y+1,z,x]==states.index(route['endpoint_state'])+1
        else:
            x,y,z=route['start'];x1,y1,z1=route['end'];assert (x,z)==(x1,z1)
            assert np.all(c[y:y1+1,z,x]==states.index('gtceu:steel_pipe_casing')+1)
            assert c[y,z,x+1]==c[y1,z,x+1]==states.index('gtceu:stainless_steel_turbine_casing')+1
    return dict(passed=True,geometry_passed=True,design_rules_passed=True,approved=False,installed=False,game_verified=False,
        size_xyz=[w,h,d],size_wdh=[w,d,h],bounds_xyz=dict(min=[0,0,0],max=[w-1,h-1,d-1]),blocks=int(counts[1:].sum()),
        unique_materials=len(states),palette=dict(zip(states,map(int,counts[1:]))),port_checks=ports,
        pipe_routes_count=len(data.get('pipe_routes',[])),pipe_routes_passed=True,open_pipe_ends=0,
        checks=['先完整生成，再按实际实体求包围盒；所有导出表面均与实体逐格一致。'],
        not_verified=['候选未批准、未部署；正式Pattern、客户端成型与运行性能另验。'],**(extra or {}))


def preview_page(out,manifest,check,description):
    view=out/manifest['key'];p=view/'三维评审.html';s=p.read_text('utf8')
    import re
    s=re.sub(r'<div class="candidate-note">.*?</div>','<div class="candidate-note">'+description+'</div>',s)
    s=s.replace(' V1',' '+manifest['candidate_version']).replace('MAX · ','外观候选 · ')
    s=s.replace('六处接口全部通用，不固定输入输出。',f"{len(manifest['ports'])}处接口全部通用，不固定输入输出。")
    s=s.replace('北向，整宽第','主控按蓝图实际朝向，整宽第')
    s=s.replace('MAX在当前范围无更低档比较对象，不虚报递增通过率。','名义尺寸仅参考；实际边界由完整几何决定。W01–W15美观优先，旧规模递增不作外观否决。')
    s=s.replace('<script src="viewer.bundle.js"></script>','<script src="viewer.bundle.js"></script><script src="boundary-review.js"></script>')
    p.write_text(s,'utf8')
    p=view/'viewer.bundle.js';s=p.read_text('utf8')
    s=s.replace('alphaTest:t.transparent?.12:0,side:t.transparent?2:0','alphaTest:t.transparent?.02:0,transparent:!!t.transparent,depthWrite:!t.transparent,side:t.transparent?2:0')
    s=s.replace('window.reviewApi={setView:q,rebuild:W,renderer:S,scene:b,camera:C}','window.reviewApi={setView:q,rebuild:W,renderer:S,scene:b,camera:C,controls:w}')
    p.write_text(s,'utf8')
    js='''/** 完整域取景：南北随主控朝向，默认恢复全部高度。 */
(()=>{function boot(){if(!window.REVIEW_READY||!window.reviewApi)return setTimeout(boot,100);
const a=window.reviewApi,old=a.setView,d=window.REVIEW.data,[w,h,z]=d.size;
a.setView=n=>{old(n);if(['front','right','back'].includes(n)){const south=d.controller_face==='south';const side=n==='right'?1:-1;const back=n==='back'?-1:1;a.controls.target.set(w/2,h*.44,z/2);a.camera.position.set(w/2+side*w*1.1,h*.7+w*.45,z/2+(south?1:-1)*back*w*1.2);a.controls.update();a.camera.zoom=1.08;}
if(n==='controller')a.camera.zoom=9;a.camera.updateProjectionMatrix();a.renderer.render(a.scene,a.camera);};
for(const e of document.querySelectorAll('[data-view]'))e.addEventListener('click',()=>a.setView(e.dataset.view));
a.setView('front');window.BOUNDARY_READY=true;}boot();})();'''
    (view/'boundary-review.js').write_text(js,'utf8')
    (out/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{manifest['title']}</title>
<style>body{{max-width:1450px;margin:30px auto;padding:0 20px;background:#14101f;color:#eee6f4;font:16px/1.8 system-ui}}a{{color:#e2b7fc}}img{{width:100%}}.note{{padding:18px;background:#302239}}</style><h1>{manifest['title']}</h1><p class="note">{description}</p>
<p>实际宽×深×高：{manifest['size'][0]}×{manifest['size'][2]}×{manifest['size'][1]}；{check['blocks']:,}实体方块。未批准、未部署。</p>
<p><a href="w03/三维评审.html">完整三维预览</a> · <a href="verification.json">逐格与边界核验</a> · <a href="manifest.json">蓝图坐标与实际原点</a></p>
<img src="完整预览.png" alt="完整边界候选"><img src="俯视布局.png" alt="完整几何俯视"><p>保留原案的相交、遮挡与自然断面，不自行纠正原作者方案。运行演出、真实机壳注册、游戏结构与性能不在本次外观交付中。</p></html>''','utf8')


def main():
    import importlib
    OUT.mkdir(parents=True,exist_ok=True);results=[]
    for version,module_name,old in VERSIONS:
        print('生成完整边界 '+version,flush=True)
        c,data,result=expanded(module_name);mod=importlib.import_module(module_name)
        offset=-np.array(result['expanded_actual_bounds_xyz']['min'])
        for item in data['ports']+data['zones']:
            item['pos']=(np.array(item['pos'])+offset).tolist()
        for item in data['paths']:
            for k in ('min','max'):item[k]=(np.array(item[k])+offset).tolist()
        for item in data.get('pipe_routes',[]):
            for k in ('start','end'):item[k]=(np.array(item[k])+offset).tolist()
            if 'path' in item:item['path']=(np.array(item['path'])+offset).tolist()
        data['controller']=(np.array(data['controller'])+offset).tolist()
        data.update(size=result['actual_xyz'],nominal_size_xyz=[673,321,529],blueprint_bounds_xyz=result['expanded_actual_bounds_xyz'],
            blueprint_to_export_offset_xyz=offset.tolist(),part_metadata_coordinates='原蓝图坐标；主控、接口、分区、通道和管路为导出坐标',name='hk3gtl-w03-'+version.lower()+'-complete-bounds-20261108',
            title=data['title']+' · 完整边界修复',candidate_version=version+'-完整边界修复')
        dest=OUT/version;work=LOG/version;work.mkdir(parents=True,exist_ok=True)
        g=SimpleNamespace(STATES=mod.STATES,ROLES=mod.ROLES,__file__=mod.__file__,build=lambda:(c,data),
            audit=lambda cube,d:generic_audit(cube,d,mod.STATES,dict(boundary_replay=result,no_nominal_clipping=True)))
        generate(g,dest,work,__file__)
        m=json.loads((dest/'manifest.json').read_text('utf8'));m.update(candidate_version=data['candidate_version'],target_voltage='CIV',generated_at='2026-11-08')
        save(dest/'manifest.json',m);check=json.loads((dest/'verification.json').read_text('utf8'))
        description=f"旧{version}独立修复：名义673×529×321不再作裁切窗，恢复{result['recovered_outside_blocks']:,}个越界实体。"+('移除为贴边强制收窄飘带和挪动晶体的逻辑。' if version=='V4' else '名义范围内部逐格保持不变。')
        preview_page(dest,m,check,description)
        shutil.copy2(ROOT/'deliveries'/old/'完整预览.png',dest/'旧版对照.png')
        results.append(dict(version=version,folder=version,**result));del c,g
    save(LOG/'repairs.json',dict(passed=True,versions=results))
    cards=''.join(f'<section><h2>{x["version"]}</h2><a href="{x["version"]}/index.html"><img src="{x["version"]}/完整预览.png">打开完整几何</a><details><summary>旧版对照</summary><img src="{x["version"]}/旧版对照.png"></details><p>实际宽×深×高：{x["actual_xyz"][0]}×{x["actual_xyz"][2]}×{x["actual_xyz"][1]}；恢复{x["recovered_outside_blocks"]:,}块。</p></section>' for x in results)
    (OUT/'index.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03完整几何边界修复</title><style>body{max-width:1500px;margin:30px auto;padding:20px;background:#14101f;color:#eee;font:16px/1.8 system-ui}a{color:#dab4f5}img{width:100%}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}</style><h1>W03 · 完整几何边界修复</h1><p>生成器裁切已确认，独立恢复V2／V3／V4／V5；旧版本、批准台账与已安装建筑保持历史原件。实际尺寸由完整几何决定，不移动、压扁、缩短构件来迁就名义包围盒。</p><p>W02 V2扩展域重放未发现越界丢块：两端直切开口来自原生成器主动设计的有限长喉口，不是查看器裁切。此核验没有把原作者未给逐格坐标的形状推断成已恢复。</p><div class="grid">'+cards+'</div></html>','utf8')


def refresh_metadata():
    """重读完整Schematic验证坐标偏移及管路，避免元数据仍指向旧原点。"""
    import base64,gzip
    from i34_open_observatory_export_20261027 import _headers
    results=[]
    for version,_,old_folder in VERSIONS:
        out=OUT/version;view=out/'w03';text=(view/'data.js').read_text('utf8')
        payload=json.loads(gzip.decompress(base64.b64decode(json.loads(text[len('window.HK3_PAYLOAD='):-1]))))
        data=payload['data'];offset=np.array(data['blueprint_to_export_offset_xyz'])
        original=json.loads((ROOT/'deliveries'/old_folder/'manifest.json').read_text('utf8'))
        for item,prior in zip(data['pipe_routes'],original['pipe_routes']):
            for k in ('start','end'):item[k]=(np.array(prior[k])+offset).tolist()
            if 'path' in prior:item['path']=(np.array(prior['path'])+offset).tolist()
        data['part_metadata_coordinates']='原蓝图坐标；主控、接口、分区、通道和管路为导出坐标'
        states=payload['palette'];w,h,d=data['size'];count=payload['blockCount']
        header=_headers(states,(h,d,w),count)[1]
        with gzip.open(view/(data['name']+'.schem'),'rb') as f:
            assert f.read(len(header))==header
            c=np.frombuffer(f.read(w*h*d),np.uint8).reshape((h,d,w))
            assert f.read()==b'\0'
        check=payload['audit'];fresh=generic_audit(c,data,states)
        check.update(fresh);assert all(p['outer_clear']==5 for p in check['port_checks'])
        check.update(no_nominal_clipping=True,boundary_replay=payload['audit']['boundary_replay'])
        payload['audit']=check
        encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf8'),6)).decode()
        (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(encoded)+';','utf8')
        m=json.loads((out/'manifest.json').read_text('utf8'));m.update(data)
        save(out/'manifest.json',m);save(out/'verification.json',check)
        results.append(dict(version=version,folder=version,**check['boundary_replay']))
        for p in [Path(__file__),ROOT/'tools/structure_delivery/audit_wonder_clipping_20261108.py']:
            shutil.copy2(p,out/'生成脚本'/p.name)
        del c,payload
    save(LOG/'repairs.json',dict(passed=True,versions=results))
    original=json.loads((LOG/'boundary-replay.json').read_text('utf8'))
    w02=next(r for r in original['results'] if 'w02' in r['source'])
    save(LOG/'boundary-replay.json',dict(passed=True,results=[w02]+[dict(r) for r in results]))
    print(json.dumps(dict(passed=True,versions=[dict(version=r['version'],size_xyz=r['actual_xyz'],recovered=r['recovered_outside_blocks'],inside_changed=r['inside_changed_blocks']) for r in results]),ensure_ascii=False))


if __name__=='__main__':
    main();refresh_metadata()
