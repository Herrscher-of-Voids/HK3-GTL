"""只读核对三座奇观的完整世界实体；成型与运行另以客户端证据确认。"""
import gzip,io,json,struct,zlib
from pathlib import Path
import nbtlib
import numpy as np
from hall_azu_extract import decode_section,state_string

ROOT=Path(__file__).resolve().parents[2]
LOG=ROOT/'logs/w01-w03-implementation-20261110'
CASES={'W01':('w01_hall.bin.gz',(12288,209,0)),
       'W02':('w02_19c_a2.bin.gz',(16384,203,0)),
       'W03':('w03_c9.bin.gz',(8192,167,0))}

def blueprint(name):
    raw=gzip.decompress((ROOT/'src/main/resources/data/hk3gtl/structures'/CASES[name][0]).read_bytes())
    magic,version,w,h,d,cx,cy,cz,count,n=struct.unpack_from('>9iH',raw);at=38;palette=[]
    for _ in range(n):
        length=struct.unpack_from('>H',raw,at)[0];at+=2;palette.append(raw[at:at+length].decode());at+=length
    if magic==0x57303141:
        values=np.frombuffer(raw,dtype='>u8',offset=at,count=count);at+=count*8
        xyz=np.column_stack([values>>36,(values>>26)&1023,(values>>16)&1023]).astype(np.int32)
        states=(values&65535).astype(np.uint16)
    else:
        assert magic==0x484b3350 and version==2
        positions=np.empty(count,np.int32);states=np.empty(count,np.uint16);cursor=0
        while cursor<count:
            start,step,length,state,extra=struct.unpack_from('>iiiHi',raw,at);at+=18
            assert not extra
            positions[cursor:cursor+length]=start+np.arange(length,dtype=np.int32)*step
            states[cursor:cursor+length]=state;cursor+=length
        xyz=np.column_stack([positions//(h*d),(positions//d)%h,positions%d])
    assert at==len(raw) and len(states)==count
    xyz+=np.array(CASES[name][1])-np.array([cx,cy,cz])
    return xyz,states,palette

def canonical(text):
    name,_,tail=text.partition('[')
    props=dict(p.split('=',1) for p in tail.rstrip(']').split(',')) if tail else {}
    props.pop('server_tick',None)
    if name=='minecraft:daylight_detector':props.pop('power',None)
    return name+('['+','.join(k+'='+props[k] for k in sorted(props))+']' if props else '')

def verify(world,name):
    xyz,states,palette=blueprint(name);lookup={canonical(s):i for i,s in enumerate(palette)}
    columns=xyz[:,[0,2]]//16;keys=(columns[:,0].astype(np.int64)<<32)|(columns[:,1].astype(np.int64)&0xffffffff)
    order=np.argsort(keys,kind='stable');unique,starts=np.unique(keys[order],return_index=True)
    regions={};matched=0;missing=[];fail=[];control=None
    for j,key in enumerate(unique):
        ix=order[starts[j]:starts[j+1] if j+1<len(starts) else len(order)]
        cx,cz=map(int,columns[ix[0]]);region=(cx//32,cz//32)
        if region not in regions:regions[region]=(world/'region'/('r.%d.%d.mca'%region)).read_bytes()
        raw=regions[region];index=(cx%32)+32*(cz%32);at=int.from_bytes(raw[index*4:index*4+3],'big')*4096
        if not at:missing.append([cx,cz]);continue
        length=struct.unpack_from('>I',raw,at)[0];payload=raw[at+5:at+4+length]
        assert raw[at+4] in (1,2,3)
        chunk=nbtlib.File.parse(io.BytesIO(gzip.decompress(payload) if raw[at+4]==1 else zlib.decompress(payload) if raw[at+4]==2 else payload))
        sections={int(s['Y']):s for s in chunk['sections'] if 'block_states' in s}
        for sy in np.unique(xyz[ix,1]//16):
            selected=ix[xyz[ix,1]//16==sy];s=sections.get(int(sy))
            if s is None:fail.append({'section':[cx,int(sy),cz],'missing':len(selected)});continue
            bs=s['block_states'];values=decode_section(bs.get('data'),len(bs['palette']))
            ids=np.array([lookup.get(canonical(state_string(p)),-1) for p in bs['palette']])
            q=xyz[selected];local=q[:,0]%16+(q[:,2]%16)*16+(q[:,1]%16)*256
            actual=ids[values[local]];ok=actual==states[selected]
            controller=np.all(q==CASES[name][1],axis=1)
            for k in np.flatnonzero(controller):
                found=state_string(bs['palette'][int(values[local[k]])]);ok[k]=found.split('[')[0]=={'W01':'hk3gtl:w01_origin_stellar_concert_court','W02':'hk3gtl:omnia_autonomous_industrial_matrix','W03':'hk3gtl:void_anchor_ring'}[name]
            matched+=int(np.count_nonzero(ok))
            for k in np.flatnonzero(~ok)[:max(0,12-len(fail))]:fail.append({'pos':q[k].tolist(),'expected':palette[int(states[selected[k]])],'actual':state_string(bs['palette'][int(values[local[k]])])})
        for be in chunk.get('block_entities',[]):
            if tuple(int(be[k]) for k in ('x','y','z'))==CASES[name][1]:control=be.snbt()
    return dict(passed=matched==len(states) and not missing and not fail,entities=len(states),matched=matched,
                chunks=len(unique),missing_chunks=missing,mismatches=fail,controller_nbt=control,
                min_xyz=xyz.min(axis=0).tolist(),max_xyz=xyz.max(axis=0).tolist())

if __name__=='__main__':
    import sys
    if '--tiles' in sys.argv:
        for name in CASES:
            xyz,_,_=blueprint(name);print(name,len(xyz),'tiles',len(np.unique(xyz//16,axis=0)))
    else:
        sys.path.insert(0,str(ROOT/'tools'))
        from deploy_industrial_build import target_process_guard
        target_process_guard()
        world=Path(json.loads((LOG/'test-world-copy.json').read_text('utf8'))['target'])
        result={name:verify(world,name) for name in CASES}
        (LOG/'saved-world-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
        print(json.dumps({name:{k:v for k,v in row.items() if k!='controller_nbt'} for name,row in result.items()},ensure_ascii=True))
        assert all(row['passed'] for row in result.values())
