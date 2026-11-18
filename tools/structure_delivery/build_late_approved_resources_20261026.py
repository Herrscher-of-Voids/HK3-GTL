"""稀疏提升 I05 V5、I19–I28 的批准 NBT；不修改 Java、实例或确认档案。"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone, timedelta
import gzip
import hashlib
import json
import os
from pathlib import Path
from project_paths import project_path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources/data/hk3gtl'
LOG = ROOT / 'logs/late-approved-resources-20261026'
INDEX = ROOT / 'logs/batch07-install-20261026/批准计数核对.json'
MACHINES = {
    'I05': ('stabilization_medium_regeneration_tower', 'HBV'),
    'I19': ('i19_small_honkai_reactor', 'HBV'),
    'I20': ('i20_medium_honkai_reactor', 'QSV'),
    'I21': ('i21_large_honkai_reactor', 'IMV'),
    'I22': ('i22_ultimate_honkai_reactor', 'WSV'),
    'I23': ('i23_honkai_phase_transition_generator', 'QCV'),
    'I24': ('i24_quantum_anomaly_observation_array', 'QEV'),
    'I25': ('i25_world_bubble_coordinate_analysis_center', 'QEV'),
    'I26': ('i26_world_bubble_unmanned_mining_dispatch', 'QAV'),
    'I27': ('i27_world_bubble_capture_array', 'IMV'),
    'I28': ('i28_world_bubble_termination_reclaimer', 'IMV'),
}
HATCHES = {'item_input':'gtceu:max_input_bus', 'item_output':'gtceu:max_output_bus',
           'fluid_input':'gtceu:max_input_hatch', 'fluid_output':'gtceu:max_output_hatch'}
GROUPS = {
    'I05': {'FEED':'fluid_input', 'FILTER':'item_input', 'POWER':'service', 'RESIDUE':'item_output', 'COOLANT':'fluid_input', 'PRODUCT':'fluid_output'},
    'I23': {'G-IN':'fluid_input', 'EU-IN':'energy_input', 'C-IN':'fluid_input', 'SOLID-OUT':'item_output', 'EU-OUT':'energy_output', 'HEAT-OUT':'fluid_output'},
    'I24': {'PROBE-IN':'item_input', 'DATA-IN':'item_input', 'OBSERVATION-OUT':'item_output', 'ENERGY-IN':'energy_input'},
    'I25': {'SPECTRA-IN':'item_input', 'REFERENCE-IN':'item_input', 'PHASE-IN':'item_input', 'VALID-OUT':'item_output', 'INVALID-OUT':'item_output'},
    'I26': {'无人装置与耗材输入':'item_input', '回收装置与磨损件输出':'item_output', '冷却介质输入':'fluid_input', '冷却介质回流':'fluid_output', '任务授权与坐标输入':'item_input', '供能输入':'energy_input', '远征记录接口':'item_input', '遗留档案输出':'item_output'},
    'I27': {'坐标数据输入':'item_input', '锁定与研究授权':'research', '西侧约束能源':'energy_input', '西侧维护':'maintenance', '东侧约束能源':'energy_input', '捕获异常与场衰减记录':'research', '空收容容器输入':'item_input', '封存世界泡输出':'item_output'},
    'I28': {'封存真实世界泡输入':'item_input', '终止耗材输入':'item_input', '西侧控制能源':'energy_input', '维护与隔离检查':'maintenance', '东侧控制能源':'energy_input', '研究与终止授权':'research', '物品资源分流':'item_output', '流体资源分流':'fluid_output', '遗留档案与状态记录':'research', '空容器残件输出':'item_output'},
}
I32 = struct.Struct('>i'); U16 = struct.Struct('>H')

def sha(path):
    h = hashlib.sha256()
    with project_path(path).open('rb') as f:
        for data in iter(lambda:f.read(1024 * 1024), b''): h.update(data)
    return h.hexdigest()

def text(raw, p):
    size = U16.unpack_from(raw, p)[0]; p += 2
    return raw[p:p+size].decode('utf-8'), p + size

def skip(raw, p, kind):
    if kind in (1,2,3,4,5,6): return p + {1:1,2:2,3:4,4:8,5:4,6:8}[kind]
    if kind == 8: return text(raw,p)[1]
    if kind in (7,11,12): return p + 4 + I32.unpack_from(raw,p)[0] * {7:1,11:4,12:8}[kind]
    if kind == 9:
        subtype,count=raw[p],I32.unpack_from(raw,p+1)[0]; p+=5
        if subtype in (1,2,3,4,5,6): return p+count*{1:1,2:2,3:4,4:8,5:4,6:8}[subtype]
        for _ in range(count): p=skip(raw,p,subtype)
        return p
    if kind == 10:
        while raw[p]: subtype=raw[p]; _,p=text(raw,p+1); p=skip(raw,p,subtype)
        return p+1
    raise ValueError(f'unknown NBT tag {kind}')

def top(raw):
    assert raw[0]==10; _,p=text(raw,1); fields={}
    while raw[p]:
        kind=raw[p]; name,payload=text(raw,p+1); end=skip(raw,payload,kind); fields[name]=(payload,end)
        p=end
    return fields

def palette(raw, bounds):
    p=bounds[0]; assert raw[p]==10; count=I32.unpack_from(raw,p+1)[0]; p+=5; result=[]
    for _ in range(count):
        name,props='',{}
        while raw[p]:
            kind=raw[p]; key,v=text(raw,p+1)
            if key=='Name': name,_=text(raw,v)
            elif key=='Properties':
                q=v
                while raw[q]: assert raw[q]==8; prop,q=text(raw,q+1); value,q=text(raw,q); props[prop]=value
            p=skip(raw,v,kind)
        p+=1; result.append(name+('['+','.join(k+'='+v for k,v in sorted(props.items()))+']' if props else ''))
    return result

def block(raw, p):
    start=p; pos=state=state_at=nbt=None
    while raw[p]:
        kind=raw[p]; name,v=text(raw,p+1)
        if name=='pos': assert kind==9 and raw[v]==3; pos=struct.unpack_from('>iii',raw,v+5)
        elif name=='state': assert kind==3; state_at=v; state=I32.unpack_from(raw,v)[0]
        elif name=='nbt': nbt=v
        p=skip(raw,v,kind)
    return start,p+1,pos,state,state_at,nbt

def string_tag(name,value):
    key,val=name.encode(),value.encode(); return b'\x08'+U16.pack(len(key))+key+U16.pack(len(val))+val

def palette_tag(state):
    name,_,props=state.partition('['); data=string_tag('Name',name)
    if props:
        data+=b'\x0a\x00\x0aProperties'
        for prop in props[:-1].split(','):
            key,value=prop.split('=',1); data+=string_tag(key,value)
        data+=b'\x00'
    return data+b'\x00'

def source_folder(ident):
    named={'I05':'deliveries/多方块确认归档/20261026_004242_968234_I05_V5_HBV_外观已确认未接入/I05_稳定介质再生塔_HBV塔冠内置反应段_滤芯接口移至X6_V5_20261026','I19':'deliveries/I19_小型崩坏能反应堆_单塔蓝湾独立候选_V3_20261023/i19','I20':'deliveries/I20_中型崩坏能反应堆_检修厂房与外围路修订_V3_20261023/i20','I21':'deliveries/I21_大型崩坏能反应堆_闭式三回路联合厂区候选_V1_20261023/i21'}
    if ident in named: return ROOT/named[ident]
    return project_path(json.loads(INDEX.read_text(encoding='utf-8'))['source_by_id'][ident]['archive'])

def metadata(folder):
    path=next(folder.rglob('设计与检查.json'),None)
    if path:
        data=json.loads(path.read_text(encoding='utf-8')); return data.get('data',data),path
    path=folder/'manifest.json'; return json.loads(path.read_text(encoding='utf-8')),path

def group(ident,port):
    if ident in ('I19','I20','I21','I22'):
        key=port['id']; num=int(key[1:])
        return 'energy_output' if key.startswith('E') else ('item_' if key.startswith('F') else 'fluid_')+('input' if num%2 else 'output')
    return GROUPS[ident][port['id']]

def build(ident):
    name,voltage=MACHINES[ident]; key=ident.lower(); machine='hk3gtl:'+name; folder=source_folder(ident); meta,metapath=metadata(folder)
    candidates=list(folder.rglob('*.nbt')); assert len(candidates)==1; source=candidates[0]; source_sha=sha(source); raw=gzip.decompress(source.read_bytes()); fields=top(raw)
    original_palette=palette(raw,fields['palette']); final_palette=original_palette.copy(); size=tuple(meta['size']); controller=tuple(meta['controller'])
    ports=[dict(p,group=group(ident,p)) for p in meta['ports']]; targets={controller:(machine,'north','controller')}
    for port in ports:
        pos=tuple(port['pos']); assert pos not in targets; targets[pos]=(HATCHES.get(port['group'],'hk3gtl:industrial_port_casing'),port['face'],port['id'])
    replacements={}
    for pos,(target,face,_) in targets.items():
        state=target+('[facing='+face+']' if target!='hk3gtl:industrial_port_casing' else '')
        if state not in final_palette: final_palette.append(state)
        replacements[pos]=final_palette.index(state)
    output=RES/'structures/approved'/f'{key}.nbt'; layout=RES/'approved_architecture'/f'{key}.json'; output.parent.mkdir(parents=True,exist_ok=True);layout.parent.mkdir(parents=True,exist_ok=True)
    nbt_tmp=output.with_suffix('.nbt.tasktmp'); json_tmp=layout.with_suffix('.json.tasktmp'); blocks_start,blocks_end=fields['blocks']; p=blocks_start; assert raw[p]==10; count=I32.unpack_from(raw,p+1)[0]; p+=5; counts=Counter(); changed=[]; found=set(); diamonds=0; seen=set()
    with gzip.open(nbt_tmp,'wb',compresslevel=6) as out, json_tmp.open('w',encoding='utf-8',newline='\n') as js:
        out.write(raw[:fields['palette'][0]]); out.write(b'\x0a'+I32.pack(len(final_palette)))
        for state in final_palette: out.write(palette_tag(state))
        out.write(raw[fields['palette'][1]:blocks_start]); out.write(raw[blocks_start:p]); js.write('{"key":'+json.dumps(key,ensure_ascii=False)+',"size":'+json.dumps(list(size))+',"controller":'+json.dumps(list(controller))+',"blocks":[\n')
        for i in range(count):
            a,b,pos,state,state_at,be=block(raw,p); p=b; original=original_palette[state]; assert pos not in seen; seen.add(pos); assert all(0<=pos[j]<size[j] for j in range(3)); counts[original]+=1; diamonds+=original=='minecraft:diamond_block'; json_state=machine if pos==controller else ('hk3gtl:industrial_port_casing' if pos in targets else original); js.write((',' if i else '')+json.dumps({'pos':pos,'state':json_state},ensure_ascii=False,separators=(',',':'))+'\n')
            if pos in targets:
                target,face,role=targets[pos]; found.add(pos); assert original==('minecraft:diamond_block' if pos==controller else 'hk3gtl:industrial_port_casing'); payload=bytearray(raw[a:b]); I32.pack_into(payload,state_at-a,replacements[pos])
                if target!='hk3gtl:industrial_port_casing': assert be is None; payload=payload[:-1]+b'\x0a\x00\x03nbt'+string_tag('id',target)+b'\x00\x00'
                out.write(payload); changed.append({'pos':list(pos),'role':role,'from':original,'to':final_palette[replacements[pos]],'block_entity_id':target})
            else: out.write(raw[a:b])
        assert p==blocks_end and found==set(targets); out.write(raw[blocks_end:]); js.write('],"ports":'+json.dumps(ports,ensure_ascii=False,separators=(',',':'))+'}')
    del seen
    final=gzip.decompress(nbt_tmp.read_bytes()); final_fields=top(final); final_states=palette(final,final_fields['palette']); q=final_fields['blocks'][0]+5; p=blocks_start+5
    with json_tmp.open(encoding='utf-8') as js:
        js.readline()
        for _ in range(count):
            _,p,pos,oldstate,_,_=block(raw,p); _,q,newpos,newstate,_,be=block(final,q); assert pos==newpos
            expected=final_palette[replacements[pos]] if pos in targets else original_palette[oldstate]; assert final_states[newstate]==expected
            row=json.loads(js.readline().lstrip(',')); expected_json=machine if pos==controller else ('hk3gtl:industrial_port_casing' if pos in targets else original_palette[oldstate]); assert tuple(row['pos'])==pos and row['state']==expected_json
            if pos in targets and targets[pos][0]!='hk3gtl:industrial_port_casing':
                assert be is not None and final[be]==8; assert text(final,text(final,be+1)[1])[0]==targets[pos][0]
        assert q==final_fields['blocks'][1]
    assert sha(source)==source_sha; os.replace(nbt_tmp,output); os.replace(json_tmp,layout)
    record={'key':key,'machine':machine,'source':f'data/hk3gtl/approved_architecture/{key}.json','sha256':sha(layout),'template_sha256':sha(output),'source_snapshot':str(folder),'source_metadata':str(metapath),'source_nbt':str(source),'source_nbt_sha256':source_sha,'controller':list(controller),'size_xyz':list(size),'blocks':count,'ports':ports,'target_voltage':voltage,'installed_hatches':{p['id']:p['group'] for p in ports if p['group'] in HATCHES},'required_abilities':sorted({p['group'] for p in ports if p['group'] in HATCHES}),'game_verified':False,'revision':177,'materials':len(counts),'source_diamond_count':diamonds,'preserved_other_diamonds':diamonds-1,'changes':changed,'geometry_nbt_json_per_block_verified':True,'all_other_cells_unchanged':True,'port_positions_faces_purposes_preserved':True,'dense_volume_materialized':False,'controller_nbt_blockentity_id':machine}
    output.with_suffix('.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); (LOG).mkdir(parents=True,exist_ok=True); (LOG/f'{key}-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'id':ident,'blocks':count,'ports':len(ports),'diamonds':diamonds,'changes':len(changed)},ensure_ascii=True),flush=True); return record

def main():
    if sys.argv[1:2] == ['--repair-layout-controllers']:
        for ident in (sys.argv[2:] or MACHINES): repair_layout_controller(ident)
        write_summary()
        return
    for ident in (sys.argv[1:] or MACHINES): build(ident)
    write_summary()

def repair_layout_controller(ident):
    """Repair only the authoritative controller cell; leave formal NBT untouched."""
    key=ident.lower(); layout=RES/'approved_architecture'/f'{key}.json'; manifest=RES/'structures/approved'/f'{key}.json'; output=manifest.with_suffix('.nbt')
    record=json.loads(manifest.read_text(encoding='utf-8')); machine=record['machine']; controller=tuple(record['controller']); prefix='{"pos":['+','.join(map(str,controller))+'],"state":'; tmp=layout.with_suffix('.json.tasktmp'); before_nbt=sha(output); count=found=changed=0
    with layout.open('r',encoding='utf-8',newline='') as source, tmp.open('w',encoding='utf-8',newline='') as target:
        for line in source:
            row=line.lstrip(',')
            if row.startswith('{"pos":'): count+=1
            if row.startswith(prefix):
                parsed=json.loads(row); assert tuple(parsed['pos'])==controller; found+=1; changed+=parsed['state']!=machine; parsed['state']=machine
                line=(',' if line.startswith(',') else '')+json.dumps(parsed,ensure_ascii=False,separators=(',',':'))+'\n'
            target.write(line)
    assert count==record['blocks'] and found==1; assert sha(output)==before_nbt; os.replace(tmp,layout)
    record.update(sha256=sha(layout),controller_json_state=machine,required_abilities=sorted({p['group'] for p in record['ports'] if p['group'] in HATCHES}))
    if ident=='I05': assert set(record['required_abilities'])==set(HATCHES)
    for destination in (manifest,LOG/f'{key}-verification.json'):
        destination.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'id':ident,'controller':controller,'state':machine,'changed':changed,'sha256':record['sha256'],'nbt_unchanged':True}),flush=True)

def write_summary():
    rows=[json.loads((LOG/f'{ident.lower()}-verification.json').read_text(encoding='utf-8')) for ident in MACHINES if (LOG/f'{ident.lower()}-verification.json').exists()]
    LOG.mkdir(parents=True,exist_ok=True); (LOG/'resource-generation.json').write_text(json.dumps({'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'revision':177,'status':'source_resources_passed_pending_runtime_acceptance','structures':rows,'java_or_instance_modified_by_this_script':False,'game_verified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
