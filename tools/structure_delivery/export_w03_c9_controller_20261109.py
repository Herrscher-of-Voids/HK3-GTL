# -*- coding: utf-8 -*-
"""按批准C9原实体导出真实主控蓝图和稀疏客户端遮罩，不裁切、不改造型。"""
from pathlib import Path
import gzip, hashlib, json, struct
import nbtlib
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
LOG=ROOT/'logs/w03-c9-controller-r231-20261109'
OUT=ROOT/'src/main/resources/data/hk3gtl/structures'

def main():
    LOG.mkdir(exist_ok=True)
    folder=ROOT/'deliveries/W03_C9_C5外环下移净空修订_20261108'
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
    source=folder/'w03/hk3gtl-w03-c5-outer-down-c9.schem'
    f=nbtlib.load(str(source));w,h,d=map(int,(f['Width'],f['Height'],f['Length']))
    assert [w,h,d]==manifest['size']==[833,636,833]
    palette=['']*int(f['PaletteMax'])
    for k,v in f['Palette'].items():palette[int(v)]=k
    data=np.asarray(f['BlockData'],dtype=np.uint8).reshape(h,d,w)
    assert data.max()<128 and len(palette)==15
    count=int(np.count_nonzero(data));assert count==6642464
    cx,cy,cz=manifest['controller'];original=int(data[cy,cz,cx])
    assert palette[original]=='minecraft:diamond_block'
    data[cy,cz,cx]=len(palette);palette.append('hk3gtl:void_anchor_ring[facing=north]')
    for port in manifest['ports']:
        x,y,z=port['pos'];assert palette[int(data[y,z,x])]=='hk3gtl:industrial_port_casing'
    path=OUT/'w03_c9.bin.gz';runs=0;recount=0
    with gzip.open(path,'wb',compresslevel=9) as out:
        out.write(struct.pack('>9iH',0x484b3350,2,w,h,d,cx,cy,cz,count,len(palette)))
        for text in palette:
            raw=text.encode('utf8');out.write(struct.pack('>H',len(raw))+raw)
        for x in range(w):
            for y in range(h):
                row=data[y,:,x]
                cuts=np.flatnonzero(np.r_[True,row[1:]!=row[:-1],True])
                for a,b in zip(cuts[:-1],cuts[1:]):
                    state=int(row[a])
                    if state:
                        n=int(b-a);out.write(struct.pack('>iiiHi',(x*h+y)*d+int(a),1,n,state,0));runs+=1;recount+=n
    assert recount==count
    mask=OUT/'w03_c9_mask.bin.gz';tiles=[];bits_count=0
    for x in range(0,w,16):
        for y in range(0,h,16):
            for z in range(0,d,16):
                slab=data[y:y+16,z:z+16,x:x+16]
                if not np.any(slab):continue
                bits=np.zeros((16,16,16),dtype=np.bool_)
                bits[:slab.shape[0],:slab.shape[1],:slab.shape[2]]=slab!=0
                bits_count+=int(bits.sum())
                key=((x>>4)<<38)|((z>>4)<<12)|(y>>4)
                packed=np.packbits(bits.reshape(64,64),axis=1,bitorder='little')
                # Java每个long的位序与BitSet一致，流本身使用大端。
                values=packed.view('<u8').reshape(-1).astype('>u8').tobytes()
                tiles.append(struct.pack('>q',key)+values)
    assert bits_count==count
    with gzip.open(mask,'wb',compresslevel=9) as out:
        out.write(struct.pack('>ii',0x5730334d,len(tiles)))
        for tile in tiles:out.write(tile)
    result=dict(source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        size_xyz=[w,h,d],blocks=count,controller=[cx,cy,cz],ports=manifest['ports'],runs=runs,mask_tiles=len(tiles),
        mask_bits=bits_count,full_geometry_preserved=True,air_records=0,
        artifacts={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [path,mask]})
    (LOG/'export.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['ports','artifacts']},ensure_ascii=False))

if __name__=='__main__':main()
