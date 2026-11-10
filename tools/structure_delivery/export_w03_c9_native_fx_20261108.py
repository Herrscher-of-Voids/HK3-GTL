# -*- coding: utf-8 -*-
"""C9完整合并面转为原生GPU静态网格；动画仅更新33组模型矩阵。"""
import base64
import gzip
import io
import json
from pathlib import Path
import struct
import numpy as np
from PIL import Image
from build_w03_outer_c5_down_c9_20261108 import ROOT,OUT,unpack,load,save,sha


def main():
    log=ROOT/'logs/w03-c9-native-r221-20261108';log.mkdir(exist_ok=True)
    before=log/'before'
    if not before.exists():
        for n in ['AGENTS.md','rule/当前多方块设计规则.md','logs/beta5-completion-audit-20261030/index.html','logs/beta5-completion-audit-20261030/current-summary.json','src/main/resources/assets/hk3gtl/changelog.json']:
            p=before/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
    p=unpack(OUT/'w03/data.js');motion=unpack(OUT/'w03/motion-data.js');w,h,d=p['data']['size']
    target=ROOT/'src/main/resources/assets/hk3gtl/models/scene';target.mkdir(parents=True,exist_ok=True)
    batches=[[] for _ in range(33)];decoded=0
    for material,faces in enumerate(p['surfaceGroups']):
        for face,starts in enumerate(faces):
            starts=np.asarray(starts,np.int64);lengths=p['surfaceRunLengths'][material][face]
            owners=np.zeros(len(starts),np.uint8)
            for group,indices in enumerate(motion['assignments'][material][face],1):
                assert np.all(owners[indices]==0);owners[indices]=group
            for i,start in enumerate(starts):
                y,z,x=int(start//(w*d)),int(start//w%d),int(start%w)
                assert 0<=x<w and 0<=y<h and 0<=z<d and 0<lengths[i]<2048
                batches[int(owners[i])].append(struct.pack('>HHHHBB',x,y,z,int(lengths[i]),material*6+face,face))
            decoded+=len(starts)
    count=sum(map(len,batches));assert count==p['audit']['viewer_rendered_quads']==decoded
    assert [len(b) for b in batches[1:]]==motion['moving_quads']
    binary=target/'w03_c9.bin.gz'
    with gzip.open(binary,'wb',compresslevel=9) as f:
        f.write(struct.pack('>III',0x57303346,1,len(batches)))
        for records in batches:f.write(struct.pack('>I',len(records)));f.write(b''.join(records))
    # 原实例逐面PNG组成单张图集，不以平均色替代方块纹理。
    names=['east','west','south','north','down','up'];images=[]
    for material in p['materials']:
        for name in names:images.append(Image.open(io.BytesIO(base64.b64decode(material['faces'][name].split(',',1)[1]))).convert('RGBA'))
    edge=max(max(im.size) for im in images);atlas=Image.new('RGBA',(16*edge,8*edge))
    for i,im in enumerate(images):atlas.paste(im.resize((edge,edge),Image.Resampling.NEAREST),(i%16*edge,i//16*edge))
    texture=ROOT/'src/main/resources/assets/hk3gtl/textures/effect/w03_c9_atlas.png';atlas.save(texture,optimize=True)
    components=[dict(id='static',pivot_export=[0,0,0],render_translation_xyz=[0,0,0],rotations=[])]+motion['components']
    metadata=dict(version=1,title='穹界·虚数锚定环 C9',controller=p['data']['controller'],size=p['data']['size'],
        components=components,quads=count,blocks=p['blockCount'],cycle_seconds=360,atlas_columns=16,atlas_rows=8,
        source_manifest_sha256=sha(OUT/'manifest.json'),source_motion_sha256=sha(OUT/'w03/motion-data.js'),
        approved_appearance=True,geometry_clearance_verified=True,game_formed_verified=False)
    save(target/'w03_c9.json',metadata)
    with gzip.open(binary,'rb') as f:
        assert struct.unpack('>III',f.read(12))==(0x57303346,1,33)
        for expected in batches:
            n=struct.unpack('>I',f.read(4))[0];assert n==len(expected)
            assert f.read(n*10)==b''.join(expected)
        assert not f.read(1)
    save(log/'native-export.json',dict(passed=True,quads=count,groups=33,moving_groups=32,voxels=p['blockCount'],
        merged_faces_exact=True,all_material_face_pngs_preserved=True,unit_surface_faces=p['audit']['viewer_surface_faces'],
        gpu_vertex_bytes=count*4*24,binary_bytes=binary.stat().st_size,texture_bytes=texture.stat().st_size,
        source_manifest_sha256=metadata['source_manifest_sha256'],mesh_sha256=sha(binary),atlas_sha256=sha(texture)))
    print(json.dumps(load(log/'native-export.json'),ensure_ascii=False))


if __name__=='__main__':main()
