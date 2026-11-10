# -*- coding: utf-8 -*-
"""完整A2外观转换为实际控制器与八通用舱位；不展开空气记录。"""
from pathlib import Path
import gzip,hashlib,json,struct
import nbtlib
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
LOG=ROOT/'logs/terminal-preview-r242-20261110'
SOURCE=ROOT/'deliveries/W02_19C自律构造船坞_双炮双掌聚焦_A2_20261110'


def main():
    LOG.mkdir(parents=True,exist_ok=True);m=json.loads((SOURCE/'manifest.json').read_text('utf8'))
    path=SOURCE/'w02'/f"{m['name']}.schem";f=nbtlib.load(str(path))
    w,h,d=map(int,(f['Width'],f['Height'],f['Length']));assert [w,h,d]==m['size']
    palette=['']*int(f['PaletteMax'])
    for k,v in f['Palette'].items():palette[int(v)]=k
    a=np.asarray(f['BlockData'],dtype=np.uint8).reshape(h,d,w).copy()
    before=int(np.count_nonzero(a));assert before==m['blocks'] and len(palette)<126
    cx,cy,cz=np.array(m['controller_visual_marker'])+m['blueprint_to_export_offset_xyz']
    ports=[];replaced=[]
    for x,y,z,state in [(cx,cy,cz,'hk3gtl:omnia_autonomous_industrial_matrix[facing=south]')]+[(cx+dx,cy+dy,cz,'hk3gtl:industrial_port_casing') for dy in [-1,0,1] for dx in [-1,0,1] if dx or dy]:
        old=palette[int(a[y,z,x])];replaced.append(dict(pos=[int(x),int(y),int(z)],before=old,after=state))
        assert old=='minecraft:sea_lantern',('主控及接口必须原位替换既有装甲',x,y,z,old)
        if state not in palette:palette.append(state)
        a[y,z,x]=palette.index(state)
        if state.endswith('port_casing'):ports.append([int(x),int(y),int(z)])
    count=int(np.count_nonzero(a));assert count==before
    destination=ROOT/'src/main/resources/data/hk3gtl/structures/w02_19c_a2.bin.gz'
    backup=LOG/'before-w02_19c_a2.bin.gz'
    if destination.exists() and not backup.exists():backup.write_bytes(destination.read_bytes())
    runs=written=0
    with gzip.GzipFile(filename=str(destination),mode='wb',compresslevel=9,mtime=0) as out:
        out.write(struct.pack('>9iH',0x484b3350,2,w,h,d,int(cx),int(cy),int(cz),count,len(palette)))
        for state in palette:
            b=state.encode('utf8');out.write(struct.pack('>H',len(b))+b)
        for x in range(w):
            for y in range(h):
                row=a[y,:,x];cuts=np.flatnonzero(np.r_[True,row[1:]!=row[:-1],True])
                for start,end in zip(cuts[:-1],cuts[1:]):
                    value=int(row[start])
                    if value:
                        n=int(end-start);out.write(struct.pack('>iiiHi',(x*h+y)*d+int(start),1,n,value,0));written+=n;runs+=1
    assert written==count
    result=dict(source=str(path),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),size_xyz=[w,h,d],
        source_blocks=before,blocks=count,controller=[int(cx),int(cy),int(cz)],facing='south',ports=ports,
        substitutions=replaced,air_records=0,runs=runs,geometry_outside_substitutions_preserved=True,
        bytes=destination.stat().st_size,sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),game_verified=False)
    (LOG/'w02-export.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(result,ensure_ascii=True))


if __name__=='__main__':main()
