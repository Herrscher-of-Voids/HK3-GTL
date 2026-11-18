# -*- coding: utf-8 -*-
"""I21候选最终核对、不可变前版保护、ZIP逐字节回读及本轮讨论落盘。

【变更记录 #1】2026-10-23 20:34:51（建筑候选封装，不增加模组修订号）
删除：无。新增：完整前阶段差异、导出与预览同源核对、工位通行和外围道路检查。
修改：把实际I21临时供能工单与研究缺口写入材料依据，不把候选视为批准。
用途：完成可审阅的累积建筑交付；不写正式资源、注册、配方或游戏实例。
"""
import base64
import datetime as dt
import gzip
import hashlib
import html
import json
import re
import shutil
import zipfile
from pathlib import Path

import nbtlib
import numpy as np

from build_i21_imv_cogeneration_v1 import ROOT,OUT,LOG,BASE,BASE_SHA,NAME,W,H,D
from build_integration_revision_20261023 import access


def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mapping(d):return {tuple(b['pos']):b['state'] for b in d['blocks']}
def records(o,key,value):
    if isinstance(o,dict):
        if o.get(key)==value:yield o
        else:
            for x in o.values():yield from records(x,key,value)
    elif isinstance(o,list):
        for x in o:yield from records(x,key,value)


def main():
    now=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)));folder=OUT/'i21'
    assert sha(BASE)==BASE_SHA
    data=read(folder/'blueprint.json');old=read(BASE);cells=mapping(data);prior=mapping(old)
    assert len(cells)==len(data['blocks'])==data['block_count']
    assert data['size']==[W,H,D]==[326,194,286]
    assert all(cells.get(p)==s for p,s in prior.items())
    assert len(prior)==522531 and len(cells)>len(prior)
    assert data['controller']==old['controller']==[95,3,20] and data['controller_face']=='north'
    assert data['ports'][:16]==old['ports'] and len(data['ports'])==24
    assert len({p['id'] for p in data['ports']})==24
    assert {tuple(p['pos']) for p in data['ports']}=={p for p,s in cells.items() if s=='hk3gtl:industrial_port_casing'}
    assert sum(s=='minecraft:diamond_block' for s in cells.values())==4
    # 逐条通道检查实体净空，并核对外围道路有地面、无低位遮挡和连续转角。
    for path in data['paths']:
        assert not any(all(path['min'][i]<=p[i]<=path['max'][i] for i in range(3)) for p in cells),path
    for x in range(W):
        for z in range(281,286):
            assert cells[(x,0,z)]=='gtceu:steel_machine_casing'
            assert all((x,y,z) not in cells for y in range(1,5))
    for x in range(321,326):
        for z in range(D):
            assert cells[(x,0,z)]=='gtceu:steel_machine_casing'
            assert all((x,y,z) not in cells for y in range(1,5))
    for x in range(6,321):
        for z in range(274,281):
            assert cells[(x,0,z)]=='gtceu:assembly_line_grating'
            assert all((x,y,z) not in cells for y in range(1,5))
    probes=[{'id':'燃料分类工位','pos':[19,4,256],'face':'west'},
            {'id':'透平西侧检修位','pos':[118,3,257],'face':'west'},
            {'id':'卧式换热器端部','pos':[284,6,201],'face':'west'},
            {'id':'核岛压力容器检修面','pos':[287,6,126],'face':'west'}]
    work=access({**data,'ports':probes})[1:]
    assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in work),work
    save(LOG/'workstation-access.json',work)
    nbt=nbtlib.load(folder/(NAME+'.nbt'));palette=[]
    assert list(map(int,nbt['size']))==data['size'] and int(nbt['DataVersion'])==3465
    for b in nbt['palette']:
        state=str(b['Name']);props=b.get('Properties',{})
        if props:state+='['+','.join(str(k)+'='+str(v) for k,v in sorted(props.items()))+']'
        palette.append(state)
    stored={tuple(map(int,b['pos'])):palette[int(b['state'])] for b in nbt['blocks']}
    assert len(nbt['blocks'])==len(cells) and stored==cells
    del nbt,stored
    schem=nbtlib.load(folder/(NAME+'.schem'))
    assert schem.root_name=='Schematic' and int(schem['Version'])==2 and int(schem['DataVersion'])==3465
    assert [int(schem[k]) for k in ('Width','Height','Length')]==data['size']
    assert list(map(int,schem['Offset']))==[0,0,0]
    ids={str(k):int(v) for k,v in schem['Palette'].items()}
    assert ids['minecraft:air']==0 and int(schem['PaletteMax'])==len(ids) and max(ids.values())<128
    dense=np.zeros(W*H*D,dtype=np.uint8)
    for (x,y,z),s in cells.items():dense[(y*D+z)*W+x]=ids[s]
    assert np.array_equal(dense,np.asarray(schem['BlockData']).view(np.uint8))
    del schem,dense
    payload=json.loads(gzip.decompress(base64.b64decode(re.search(r'window.HK3_PAYLOAD\s*=\s*"([^"\n]+)"',(folder/'data.js').read_text('utf-8'))[1])))
    assert payload['data']=={k:v for k,v in data.items() if k!='blocks'}
    expected=[set() for _ in payload['palette']];indices={s:i for i,s in enumerate(payload['palette'])}
    for (x,y,z),s in cells.items():expected[indices[s]].add((y*D+z)*W+x)
    assert len(payload['groups'])==len(expected)
    assert all(set(g)==e and len(g)==len(e) for g,e in zip(payload['groups'],expected))
    protected=read(LOG/'protected-before.json')
    changed=[p for p,h in protected['files'].items() if not Path(p).is_file() or sha(Path(p))!=h]
    assert not changed,changed
    audit=read(OUT/'verification.json')
    assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in audit['access'])
    assert sha(folder/(NAME+'.nbt'))==audit['hashes']['nbt'] and sha(folder/(NAME+'.schem'))==audit['hashes']['schem']
    material=read(OUT/'材料阶段依据.json')
    plan=next(records(read(ROOT/'src/main/resources/data/hk3gtl/research/industrial_processes.json'),'id','industrial_reactor_i21'))
    gate=next(records(read(ROOT/'src/main/resources/data/hk3gtl/research/research_execution.json'),'id','RN-SSQ'))
    reactor_gate=next(records(read(ROOT/'src/main/resources/data/hk3gtl/research/research_execution.json'),'id','RN-LRE'))
    assert plan['provisional'] and plan['energy_tier']==23 and plan['energy_direction']=='output'
    material.update(actual_i21_process_plan=plan,imv_material_research=gate,i21_reactor_research=reactor_gate)
    material['power_boundary']='IMV23为既定设计档；工业能源工单仍provisional并绑定RN-LRE，未接可运行独立I21。IMV主材工序首制电压为QAV22，研究RN-SSQ existing:false/provisional:true，不能据此宣称首建闭环。'
    save(OUT/'材料阶段依据.json',material)
    review={'time':now.isoformat(),'blocks':len(cells),'source_retained':len(prior),'added_blocks':len(cells)-len(prior),
            'removed_blocks':0,'replaced_blocks':0,'controller':data['controller'],'old_ports_unchanged':16,'new_ports':8,
            'full_nbt_match':True,'full_sponge_including_air_match':True,'full_viewer_match':True,
            'workstation_access':work,'paths_checked':len(data['paths']),'roads_enclose_all_halls':True,
            'protected_files_unchanged':len(protected['files']),
            'reviewer':'主任务实际查看真实材质俯视、全厂等轴、四列透平、分类厅及换热厅内部图；子代理请求失败，未声称独立复核。',
            'visual_findings':'三代主体颜色可辨，原位主控保留；新增接口嵌设备端壳；管线接实际设备、跨路有支撑与净高；全体后墙在新外围路之内。',
            'identified_geometry_issues_remaining':[],
            'requirements_status':{'有效文件与逐格数据':'已验证','逐轴实际尺寸':'已验证','完整立方体与实际HK材质':'已验证',
                '接口标记及旧块继承':'已验证','建筑配色与设备用途':'主任务已直接审视，待用户外观审批',
                '完整材料生存祖先链及研究':'未完整验收','真实控制器Pattern及能源功能':'未实现本轮接入','游戏与2.9.2':'未验收'},
            'boundary':'仅建筑候选文件与静态几何，不等于批准、实装、运行或生存首建通过'}
    save(LOG/'final-review.json',review);audit['final_review']=review;save(OUT/'verification.json',audit)
    save(folder/'设计与检查.json',{'data':payload['data'],'audit':audit})
    payload['audit']=audit
    packed=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),9)).decode('ascii')
    (folder/'data.js').write_text('/* I21候选；建筑表达不等于实际能源功能。 */\nwindow.HK3_PAYLOAD='+json.dumps(packed)+';',encoding='utf-8')
    evidence=OUT/'评审依据';evidence.mkdir(exist_ok=True)
    for name in ('rules-read.json','final-review.json','workstation-access.json','static-access.json','i21-lodestone.json'):
        shutil.copy2(LOG/name,evidence/name)
    save(evidence/'保护文件复核.json',{'time':now.isoformat(),'checked':len(protected['files']),'changed':changed})
    scripts=OUT/'生成脚本'
    for name in ('build_i21_imv_cogeneration_v1.py','package_i21_imv_candidate_v1_20261023.py','finalize_i21_imv_candidate_v1_20261023.py','package_integration_review.mjs'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    manifest=read(OUT/'manifest.json');manifest.update(finalized_at=now.isoformat(),blueprint_sha256=sha(folder/'blueprint.json'),final_review=review)
    save(OUT/'manifest.json',manifest)
    broken=[]
    for p in OUT.rglob('*.html'):
        content=p.read_text('utf-8');assert 'undefined' not in content,p
        for link in re.findall(r'(?:href|src)="([^"]+)"',content):
            relative=link.split('#')[0].split('?')[0]
            if relative and '://' not in relative and not relative.endswith('.zip') and not (p.parent/relative).resolve().is_file():broken.append([str(p),link])
    assert not broken,broken
    save(OUT/'交付文件清单.json',{'time':now.isoformat(),'approval':'待用户外观审批','deployment_eligible':False,
        'files':{p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='交付文件清单.json'}})
    archive=OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(OUT))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(z.read(n)==(OUT/n).read_bytes() for n in z.namelist())
    topic='I21大型崩坏能反应堆闭式三回路候选'
    discussion=ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_'+topic+'.html')
    assert not discussion.exists()
    discussion.write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{topic}</title><style>body{{max-width:1050px;margin:35px auto;font:16px/1.9 'Microsoft YaHei';color:#243c48}}code{{overflow-wrap:anywhere}}</style><h1>{topic}</h1><p>记录时间：{now.isoformat()}，Asia/Hong_Kong；用户原消息精确时间未知。</p>
<h2>用户要求与持续有效决定</h2><blockquote>下一台吧</blockquote><p>用户在I20检修厂房与外围路V3页面后要求继续下一台，故制作I21大型崩坏能反应堆候选。沿用I19主控[95,3,20]朝北、前阶段块与颜色原位继承、接口自然嵌入实际设备、外围道路完整包住建筑。I19/I20/I21/I22的HBV/QSV/IMV/WSV映射不改。</p>
<h2>本轮实际完成</h2><p>新增I21 IMV23建筑候选，XYZ326×194×286（宽深高326×286×194），{len(cells):,}实体块。完整保留I20 V3的522,531块，新增{len(cells)-len(prior):,}，删除与替换均零。主控及原16口原位；新增2燃料、2冷却、4能源接口标记，共24口，分别嵌分类设备、泵及一体发电机端壳。</p><p>东侧新增双筒闭式散热塔楼、分区双腔核岛与再生换热厅；南侧为燃料分配/乏棒分类厅与四列长跨透平发电厅。旧I20后路保留成内部横路，新南路Z281–285、东路X321–325，最南后墙Z273、墙外七格维护带。</p>
<h2>已经验证与未验收</h2><p>全部I20旧块原位逐格一致；20条声明通道净空，主控/24口及4个内部工位静态步行可达；单一六面连通；NBT、Sponge含空气和三维载荷全量逐格一致；实际完整方块与安装HK材质逐字节核对。主任务直接查看真实纹理布局与内外图；子代理工具报错，未声称独立审查。{len(protected['files'])}份旧交付/正式资源/实例文件身份保持，ZIP全文件字节复核。</p><p>本版尚待用户外观审批；“下一台”不改写为对I20或I21整版的批准，不自动计入batch-07。真实控制器/Pattern、I21能源工况、RN-LRE与IMV材料RN-SSQ、生存祖先链、游戏运行及2.9.2兼容性未验收。材料/工业工单仍有provisional缺口，没有新增EU/HKE转换能力。</p><p>当前实际实例元数据仍2.9、HK修订175包身份未变。本轮未实装、未改正式资源、配方或实例，也未增加模组修订号。满五台明确批准后先装2.9；用户升级后再验2.9.2的部署决定保留。</p>
<h2>相关文件及下一步</h2><p><a href="../../../deliveries/{OUT.name}/index.html">I21候选与三维评审</a> · <a href="../../../logs/i21-imv-cogeneration-v1-20261023/final-review.json">实际检查记录</a> · <a href="2026-10-23_20-03-04_I20补建检修厂房与南侧外围路后退.html">I20上一轮持续决定</a>。下一步由用户审阅候选并提出修改或明确批准，未提前接入。</p><p>变更#1：新增IMV阶段结构、同源导出与预览；删除/替换前阶段块零；用途为完成下一台候选。ZIP SHA256：<code>{sha(archive)}</code>。</p></html>''',encoding='utf-8')
    result={'time':now.isoformat(),'out':str(OUT),'blocks':len(cells),'size_xyz':data['size'],'source_retained':len(prior),
        'added_blocks':len(cells)-len(prior),'removed':0,'replaced':0,'controller':data['controller'],'ports':24,
        'blueprint_sha256':sha(folder/'blueprint.json'),'nbt_sha256':sha(folder/(NAME+'.nbt')),'schem_sha256':sha(folder/(NAME+'.schem')),
        'protected_files_unchanged':len(protected['files']),'zip':str(archive),'zip_sha256':sha(archive),'zip_all_bytes_verified':True,
        'discussion':str(discussion),'instance_changed':False,'formal_resources_changed':False,'candidate_approved':False}
    save(LOG/'final-verification.json',result);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
