# -*- coding: utf-8 -*-
"""I22 WSV V14候选的最终逐格核验、归档清单与讨论记录。

【文件职责】读取已经生成的I22候选，不改写I21来源、正式资源、配方或游戏实例；
核对累积继承、接口与核心、道路、NBT/Schematic、离线查看器载荷和ZIP字节。
【变更记录 #1】2026-10-23 21:30:00（候选最终核对脚本，不增加模组修订号）
删除：无。新增：WSV V14四堆隔离外场的逐格继承、导出回读、道路和接口审计。
修改：把I22的34口、8个钻石核心、402×250×346范围及WSV材料/研究缺口写入独立证据。
用途：形成可审阅的候选归档；不把静态建筑核验冒充Pattern成型、运行、批准或2.9.2兼容性。

【变更记录 #2】2026-10-24（候选外观差异与图像复核记录，不增加模组修订号）
删除：无。新增：内测5造型方向对照、用户当前请求原文和真实材质图人工复核结论。
修改：明确候选重新诠释了10月20日阶梯八角主塔、冷却塔/水池/隔离廊方向，仍待用户审阅。
用途：准确披露缓存候选与最新文字设计方向的差异，不暗示已经批准。
"""
import base64, datetime as dt, gzip, hashlib, json, re, shutil, zipfile
from pathlib import Path
import nbtlib
import numpy as np

from build_i22_wsv_ultimate_reactor_v1 import ROOT, OUT, LOG, BASE, BASE_SHA, NAME, W, H, D

def read(p): return json.loads(p.read_text('utf-8-sig'))
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()
def mapping(d): return {tuple(b['pos']):b['state'] for b in d['blocks']}
def records(o,key,value):
    if isinstance(o,dict):
        if o.get(key)==value: yield o
        for x in o.values(): yield from records(x,key,value)
    elif isinstance(o,list):
        for x in o: yield from records(x,key,value)

def check_paths(cells,paths):
    for p in paths:
        lo,hi=p['min'],p['max']
        assert not any(all(lo[i]<=pos[i]<=hi[i] for i in range(3)) for pos in cells), p

def main():
    stamp=now(); folder=OUT/'i22'; data=read(folder/'blueprint.json'); old=read(BASE)
    assert sha(BASE)==BASE_SHA
    cells=mapping(data); prior=mapping(old)
    assert data['size']==[W,H,D]==[402,250,346]
    assert len(cells)==data['block_count']==1408427
    assert all(cells.get(p)==s for p,s in prior.items())
    assert len(prior)==839950 and len(cells)-len(prior)==568477
    assert data['controller']==old['controller']==[95,3,20] and data['controller_face']=='north'
    assert data['ports'][:24]==old['ports'] and len(data['ports'])==34
    assert len({p['id'] for p in data['ports']})==34
    assert {tuple(p['pos']) for p in data['ports']}=={p for p,s in cells.items() if s=='hk3gtl:industrial_port_casing'}
    assert sum(s=='minecraft:diamond_block' for s in cells.values())==8
    check_paths(cells,data['paths'])
    # 新外围道路与维护带：地面承重，行走层保持四格净空。
    for x in range(397,402):
        for z in range(346):
            assert cells[(x,0,z)]=='gtceu:steel_machine_casing'
            assert all((x,y,z) not in cells for y in range(1,5))
    for x in range(402):
        for z in range(341,346):
            assert cells[(x,0,z)]=='gtceu:steel_machine_casing'
            assert all((x,y,z) not in cells for y in range(1,5))
    for x in range(6,397):
        for z in range(334,341):
            assert cells[(x,0,z)] in ('gtceu:assembly_line_grating','gtceu:steel_machine_casing')
            assert all((x,y,z) not in cells for y in range(1,5))
    assert json.loads((LOG/'geometry-preview.json').read_text('utf-8'))['components']==1
    # 标准NBT逐格状态回读。
    nbt=nbtlib.load(folder/(NAME+'.nbt')); assert list(map(int,nbt['size']))==data['size']; assert int(nbt['DataVersion'])==3465
    states=[]
    for b in nbt['palette']:
        s=str(b['Name']); props=b.get('Properties',{})
        if props: s+='['+','.join(str(k)+'='+str(v) for k,v in sorted(props.items()))+']'
        states.append(s)
    actual={tuple(map(int,b['pos'])):states[int(b['state'])] for b in nbt['blocks']}
    assert actual==cells; del nbt,actual,states
    schem=nbtlib.load(folder/(NAME+'.schem')); assert schem.root_name=='Schematic'; assert int(schem['Version'])==2 and int(schem['DataVersion'])==3465
    assert [int(schem[k]) for k in ('Width','Height','Length')]==data['size'] and list(map(int,schem['Offset']))==[0,0,0]
    ids={str(k):int(v) for k,v in schem['Palette'].items()}; assert ids['minecraft:air']==0 and max(ids.values())<128
    dense=np.zeros(W*H*D,dtype=np.uint8)
    for pos,s in cells.items(): x,y,z=pos; dense[(y*D+z)*W+x]=ids[s]
    assert np.array_equal(dense,np.asarray(schem['BlockData']).view(np.uint8)); del schem,dense
    # 查看器载荷与完整方块集合逐组一致，防止预览落后于导出。
    raw=(folder/'data.js').read_text('utf-8'); packed=re.search(r'window\.HK3_PAYLOAD\s*=\s*"([^"\n]+)"',raw)[1]
    payload=json.loads(gzip.decompress(base64.b64decode(packed)))
    assert payload['data']=={k:v for k,v in data.items() if k!='blocks'}
    indexes={s:i for i,s in enumerate(payload['palette'])}; expected=[set() for _ in payload['palette']]
    for (x,y,z),s in cells.items(): expected[indexes[s]].add((y*D+z)*W+x)
    assert len(expected)==len(payload['groups']) and all(set(g)==e for g,e in zip(payload['groups'],expected))
    # I21来源快照与本次保护清单不能被候选打包过程改写。
    protected=read(LOG/'protected-before.json'); old_workspace=ROOT.parent/'hk3gtm'; changed=[]; remapped=0
    for recorded,h in protected['files'].items():
        source=Path(recorded)
        try: relative=source.relative_to(old_workspace)
        except ValueError: current=source
        else: current=ROOT/relative; remapped+=1
        if not current.is_file() or sha(current)!=h: changed.append({'recorded_path':recorded,'current_path':str(current)})
    assert not changed,changed
    # 工业计划只记录实际存在的候选工单与研究状态。
    plan=next(records(read(ROOT/'src/main/resources/data/hk3gtl/research/industrial_processes.json'),'id','industrial_reactor_i22'))
    gates={rid:next(records(read(ROOT/'src/main/resources/data/hk3gtl/research/research_execution.json'),'id',rid)) for rid in ('RN-URE','RN-WME','RN-WMS')}
    assert plan['provisional'] and plan['energy_tier']==28 and plan['energy_direction']=='output'
    material=read(OUT/'材料阶段依据.json'); material.update(actual_i22_process_plan=plan,wsv_research_gates=gates,
        verification_boundary='WSV稳界约束壳材与RN-WME/RN-WMS工单均有源码/数据证据，但研究执行和I22独立Pattern仍未验收。')
    save(OUT/'材料阶段依据.json',material)
    audit=read(OUT/'verification.json'); audit.update(final_static_checks={'source_retained':len(prior),'added_blocks':len(cells)-len(prior),'removed_blocks':0,'replaced_blocks':0,
        'controller':data['controller'],'ports_old':24,'ports_new':10,'ports_total':34,'diamonds':8,'paths_checked':len(data['paths']),'paths_clear':True,
        'full_nbt_match':True,'full_sponge_including_air_match':True,'full_viewer_match':True,'roads_enclose_new_halls':True,'protected_files_unchanged':len(protected['files']),
        'visual_review':'主任务已直接查看全厂、四腔塔、燃料厅、冷凝阵列和透平厅真实材质图；只确认静态几何表达，不代替游戏截图。'},
        not_verified=['完整材料生存祖先链与RN-WME/RN-WMS研究首建','I22真实控制器/Pattern、端口能力、能源运行','游戏内成型/运行与2.9.2兼容性','用户外观批准'])
    save(OUT/'verification.json',audit)
    save(folder/'设计与检查.json',{'data':payload['data'],'audit':audit})
    (folder/'data.js').write_text('/* I22候选；建筑表达不等于真实能源能力。 */\nwindow.HK3_PAYLOAD='+json.dumps(base64.b64encode(gzip.compress(json.dumps({**payload,'audit':audit},ensure_ascii=False,separators=(',',':')).encode('utf-8'),9)).decode('ascii'))+';',encoding='utf-8')
    evidence=OUT/'评审依据'; evidence.mkdir(exist_ok=True)
    for name in ('rules-read.json','geometry-preview.json','static-access.json','materials.json'):
        if (LOG/name).exists(): shutil.copy2(LOG/name,evidence/name)
    save(evidence/'保护文件复核.json',{'time':stamp,'checked':len(protected['files']),'remapped_from_old_workspace':remapped,
        'old_workspace':str(old_workspace),'current_workspace':str(ROOT),'changed':changed})
    manifest=read(OUT/'manifest.json') if (OUT/'manifest.json').exists() else {}
    manifest.update(finalized_at=stamp,blueprint_sha256=sha(folder/'blueprint.json'),candidate_approved=False,deployment_eligible=False)
    save(OUT/'manifest.json',manifest)
    broken=[]
    for p in OUT.rglob('*.html'):
        content=p.read_text('utf-8'); assert 'undefined' not in content,p
        for link in re.findall(r'(?:href|src)="([^"]+)"',content):
            rel=link.split('#')[0].split('?')[0]
            if rel and '://' not in rel and not rel.endswith('.zip') and not (p.parent/rel).resolve().is_file(): broken.append([str(p),link])
    assert not broken,broken
    files={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='交付文件清单.json'}
    save(OUT/'交付文件清单.json',{'time':stamp,'approval':'待用户外观审批','deployment_eligible':False,'files':files})
    archive=OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(OUT))
    with zipfile.ZipFile(archive) as z: assert z.testzip() is None and all(z.read(n)==(OUT/n).read_bytes() for n in z.namelist())
    discussion=ROOT/'doc/HK3GTL-内测5/讨论记录'/(stamp[:19].replace('T','_').replace(':','-')+'_I22究极崩坏能反应堆候选.html')
    assert not discussion.exists()
    discussion.write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I22究极崩坏能反应堆候选</title><style>body{{max-width:1050px;margin:35px auto;font:16px/1.9 'Microsoft YaHei';color:#243c48}}code{{overflow-wrap:anywhere}}</style><h1>I22究极崩坏能反应堆 WSV V14 候选</h1><p>记录时间：{stamp}，Asia/Hong_Kong；用户原消息精确发送时间未知。</p><h2>用户要求与持续有效决定</h2><blockquote>帮我继续写i22，你应该会找到项目里有这玩意的缓存</blockquote><p>按用户要求从项目现有I22缓存续作；本轮不把“继续写I22”解释为候选批准，不计入batch-07。I19–I22沿用崩坏能反应堆主控[95,3,20]朝北，I22新增结构不得迁移主控。控制器与接口须嵌入实际设备表面，不另立突兀面板或异风格托柱。</p><h2>本轮实际完成</h2><p>I22 WSV V14候选为402×250×346（宽×高×深），{len(cells):,}实体块；完整保留I21的{len(prior):,}块，新增{len(cells)-len(prior):,}块，删除与替换均零。新区域包括四腔环箍屏蔽堆塔、六室冷凝阵列、燃料轮换厅、六列协同透平厅及两台稳界冷媒蓄能器。主控原位，原24口原位，新C7/C8、F7/F8、E13–E18共10口嵌在泵组、燃料设备和透平端壳，共34口；新增钻石核心4块，累计8块。</p><h2>已验证与未验收</h2><p>尺寸实际边界、单一连通、27条通道净空、东/南外围路和后墙维护带、I21逐格继承、完整NBT、Sponge含空气三维载荷、离线查看器逐组载荷、安装HK材质与模型来源均已静态核对；真实材质图由主任务直接查看。WSV材料路线和I22工单/研究状态已写入材料依据。材料主机壳映射为WSV V14；数据中的I22工单另列energy_tier=28且provisional=true。当前实例仍为2.9 HK修订175，本候选未实装、未改正式资源/配方/实例；真实Pattern、端口能力、能源运行、材料生存首建、游戏成型与2.9.2兼容性均未验收。</p><h2>下一步</h2><p>用户先审阅I22候选；只有明确批准才进入不可变确认归档。满足五台新的明确批准后，按负责人决定先接入2.9，负责人升级2.9.2后再做兼容性复核，不能自动升级或自动部署。</p><p><a href="../../../deliveries/{OUT.name}/index.html">I22候选交付页</a> · <a href="../../../logs/i22-wsv-ultimate-v1-20261023/final-static-review.json">静态核对</a> · <a href="2026-10-23_20-36-26_I21大型崩坏能反应堆闭式三回路候选.html">I21持续决定</a></p><p>变更#1：从已有WSV V14建筑缓存续作并形成候选导出、材质与研究边界记录；删除/替换前阶段方块零；用途为I22候选评审，不增加模组修订号。ZIP SHA256：<code>{sha(archive)}</code>。</p></html>''',encoding='utf-8')
    result={'time':stamp,'out':str(OUT),'blocks':len(cells),'size_xyz':data['size'],'source_retained':len(prior),'added_blocks':len(cells)-len(prior),'removed':0,'replaced':0,'controller':data['controller'],'ports':34,'diamonds':8,'blueprint_sha256':sha(folder/'blueprint.json'),'nbt_sha256':sha(folder/(NAME+'.nbt')),'schem_sha256':sha(folder/(NAME+'.schem')),'protected_files_unchanged':len(protected['files']),'zip':str(archive),'zip_sha256':sha(archive),'zip_all_bytes_verified':True,'discussion':str(discussion),'instance_changed':False,'formal_resources_changed':False,'candidate_approved':False}
    result['protected_paths_remapped_from_old_workspace']=remapped
    save(LOG/'final-static-review.json',result); print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    design_note='<h2>与内测5造型方向的差异，待用户审阅</h2><p>内测5 2026-10-20 22:10的最新文字方向为贯穿多层环形检修层的阶梯八角主塔，外围包含不同高度冷却塔、不对称辅助殿、管廊和分格水池。当前缓存V1将其重新诠释为环箍四腔主塔、六室冷凝阵列、燃料轮换厅、六列透平厅和稳界蓄能器；没有独立呈现传统塔形冷却塔、分格水池或隔离廊。该造型差异尚未获用户确认，需按候选审阅。</p><p>I21保护清单原记在旧HK3GTM工作区；将其中239条路径映射至当前HK3GTL根目录后，329项逐条SHA-256均匹配，0项变化或缺失。原始保护清单保留。</p>'
    discussion.write_text(discussion.read_text('utf-8').replace('<h2>本轮实际完成</h2>',design_note+'<h2>本轮实际完成</h2>'),encoding='utf-8')

if __name__=='__main__': main()
