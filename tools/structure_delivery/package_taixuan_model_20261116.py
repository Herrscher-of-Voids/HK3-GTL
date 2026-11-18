from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import base64
import gzip
import hashlib
import io
import json
import shutil

import numpy as np
from PIL import Image

from material_resources import Resources
from package_0005_w12_author_blueprint_20261116 import mesh_part
import package_senti_weapons_20261116 as nbt
from taixuan_common_20261116 import *
import taixuan_landscape_20261116 as landscape
import taixuan_architecture_20261116 as architecture


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def materials():
    resources = Resources(instance=Path('E:/Prism/instances/GregTech Leisure-增强版/minecraft'),
        client=Path('E:/Prism/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar'),
        project_resources=ROOT/'src/main/resources')
    textures = {1:'stone',2:'andesite',3:'polished_andesite',4:'moss_block',5:'green_terracotta',
        7:'spruce_planks',9:'gray_terracotta',11:'sandstone_top',12:'yellow_terracotta',
        14:'brown_terracotta',15:'black_concrete',16:'white_concrete',17:'spruce_log',
        18:'oak_leaves',19:'light_blue_stained_glass'}
    result=[]
    for i,(state,label) in enumerate(zip(STATES,LABELS),1):
        if i in textures:
            faces={}
            for face in ['east','west','north','south','up','down']:
                texture='spruce_log_top' if i==17 and face in ('up','down') else textures[i]
                path='assets/minecraft/textures/block/'+texture+'.png'
                raw=resources.read(path)
                if i==18:
                    picture=Image.open(io.BytesIO(raw)).convert('RGBA')
                    values=np.array(picture)
                    values[:,:,:3]=(values[:,:,:3].astype(float)*np.array([.39,.64,.25])).astype(np.uint8)
                    output=io.BytesIO();Image.fromarray(values).save(output,'PNG');raw=output.getvalue()
                faces[face]='data:image/png;base64,'+base64.b64encode(raw).decode()
            item=dict(state=state,faces=faces,transparent=i==19,source=dict(texture=textures[i]))
            if i==18:
                item['biome_tint']='#63a340'
        else:
            item=resources.material(state)
        item.update(label=label,emissive=False)
        result.append(item)
    save(OUT/'materials.json',result)
    save(OUT/'材质来源.json',dict(resources.sources))
    resources.close()
    return result


def main(revision='T1'):
    OUT.mkdir(exist_ok=True)
    (OUT/'NBT').mkdir(exist_ok=True)
    (OUT/'生成脚本').mkdir(exist_ok=True)
    palette=materials()
    refs=json.loads((REF/'参考清单.json').read_text('utf8'))['references']
    by_id={r['id']:r for r in refs}
    parts=landscape.build()+architecture.build()
    low=np.min([p.p.min(0) for p in parts],axis=0)
    high=np.max([p.p.max(0) for p in parts],axis=0)
    size=high-low+1
    w,h,d=map(int,size)
    keys=np.concatenate([((p.p[:,1].astype(np.int64)-low[1])*d+p.p[:,2]-low[2])*w+p.p[:,0]-low[0] for p in parts])
    states=np.concatenate([p.states for p in parts])
    owner=np.repeat(np.arange(len(parts),dtype=np.uint8),[len(p.p) for p in parts])
    keys,ix=np.unique(keys[::-1],return_index=True)
    ix=len(states)-1-ix
    states,owner=states[ix],owner[ix]
    xyz=np.c_[keys%w,keys//(w*d),keys//w%d].astype(np.int32)
    nbt.STATES=STATES
    file=f'NBT/太虚山-完整拂云观与云海山体-{revision}.nbt'
    nbt.export_nbt(OUT/file,xyz,states,size)
    np.savez_compressed(OUT/'完整整数格模型.npz',xyz=xyz,states=states,origin=low,size=size)
    mountain_names={p.name for p in parts[:9]}
    model_ids=['landscape','temple','gallery','censer','courtyard','mountain_path','trees','waterfall','lanterns']
    labels=['云海山体','重檐主殿','折廊格窗','塔式香炉','石坪八卦台','回折山径','古松草台','青岩瀑布','石灯']
    groups={k:[] for k in model_ids}
    packed=[]
    for i,p in enumerate(parts):
        chosen=owner==i
        current=xyz[chosen]+low
        visible=SimpleNamespace(name=p.name,label=p.label,p=current,states=states[chosen],metadata=p.metadata)
        mesh,quads=mesh_part(visible,palette)
        key='landscape' if p.name in mountain_names else p.name
        mesh['modelId']=key
        groups[key].append(visible)
        packed.append(mesh)
        print(p.name,len(current),quads,flush=True)
    models=[]
    for key,label in zip(model_ids,labels):
        ps=groups[key]
        a=np.min([p.p.min(0) for p in ps],axis=0)
        b=np.max([p.p.max(0) for p in ps],axis=0)
        reference_ids=list(dict.fromkeys(r for p in ps for r in p.metadata['references']))
        descriptions=[]
        for ref_id in reference_ids:
            ref=by_id[ref_id];base='../'+REF.name+'/'
            descriptions.append(dict(id=ref_id,thumbnail=base+ref['thumbnail'],file=base+ref['file'],
                source_url=ref['source_url'],label=ref['view'],kind=ref['kind']))
        models.append(dict(id=key,title=label,blocks=sum(len(p.p) for p in ps),sizeXYZ=(b-a+1).tolist(),
            origin=a.tolist(),features=list(dict.fromkeys(f for p in ps for f in p.metadata['features'])),
            references=descriptions,views={k:v for p in ps for k,v in p.metadata['views'].items()},
            construction_notes=[dict(id=p.name,**p.metadata) for p in ps]))
    data=dict(title='太虚山 · 完整拂云观与云海山体',created_at=datetime.now(timezone.utc).isoformat(),
        sizeXYZ=size.tolist(),bounds=dict(min=low.tolist(),max=high.tolist()),models=models,
        total_blocks=len(xyz),material_count=len(np.unique(states)),nbt=file,
        nbt_sha256=hashlib.sha256((OUT/file).read_bytes()).hexdigest(),source_coordinate_min=low.tolist(),
        export_offset=(-low).tolist(),coordinate_rule='Y160庭院地面，+Z为殿门朝向；NBT按实际包围盒平移。',
        status='独立方块外观候选，等待负责人评审。',
        method=f'按{len(refs)}张公开影像与插画中的可见构件建立整数格轮廓、截面、瓦檐与格扇。',
        reconstruction=['完整山势、峰间坐标、全山背面与回折山径属于场景复刻设计。',
            '庭院重檐立面与长格窗立面的建筑归属、背面和室内按构架延续补建。',
            '舰桥云海仅用于山体与云雾氛围；完整拂云观建筑以3.7训练场及历史夜景为主。',
            '石灯、石阶与栏杆以7.2细节补充。',
            '白瓷墙、墨色构架、青灰屋面及炉体机关使用GT与HK3GTL原生方块，同色替换。'],
        scope='本稿为独立太虚山外观模型，W09整机组合另行设计。')
    save(OUT/'manifest.json',data)
    save(OUT/'材料清单.json',[dict(state=state,label=label,blocks=int((states==i).sum()))
        for i,(state,label) in enumerate(zip(STATES,LABELS),1)])
    payload=dict(data=data,materials=palette,parts=packed)
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode()
    (OUT/'data.js').write_text('window.TAIXUAN_VOXEL_PAYLOAD='+json.dumps(encoded)+';','utf8')
    for source in [Path(__file__),Path(landscape.__file__),Path(architecture.__file__),ROOT/'tools/structure_delivery/taixuan_common_20261116.py']:
        shutil.copy2(source,OUT/'生成脚本'/source.name)
    print(json.dumps(dict(size=size.tolist(),blocks=len(xyz)),ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
