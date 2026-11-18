# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import base64
import gzip
import hashlib
import json
import shutil

import numpy as np

from material_resources import Resources
from package_0005_i37_suspended_test_dock_a2_20261115 import headers, tag, RECORD, RECORD_DTYPE
from package_0005_w12_author_blueprint_20261116 import mesh_part
import senti_case_20261116 as case
import senti_sword_spear_20261116 as blades
import senti_chain_20261116 as chain


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_识律三兵方块复刻_S1_20261116'
REF = ROOT / 'deliveries/0005_W09_识律武器多角度参考_20261116'
VERSION = 'S1'
METHOD = '依据官方画面手工重建整数格轮廓与截面；武器匣宽面按官方转台图逐格采样，原生方块纹理逐格重复。'
STATES = ['minecraft:black_concrete','hk3gtl:casing_colored_black','minecraft:white_concrete',
    'gtceu:clean_machine_casing','minecraft:red_concrete','minecraft:nether_wart_block',
    'gtceu:bronze_gearbox','minecraft:yellow_terracotta','minecraft:black_terracotta','minecraft:sea_lantern',
    'minecraft:orange_concrete']
LABELS = ['墨黑宽面','本模组黑色边框','骨白云火纹','格雷白瓷金属','朱红刃芯',
    '暗红侧壁','格雷青铜机关','哑光金细纹','暖黑握柄','白色亮纹','橙红圆晶']
DETAIL_LABELS = dict(taiji='太极纹与冠口',tip='弯曲匣尖',rim='匣体侧壁',guard='宝剑卷形护手',
    grip='红白缠柄',blade='剑脊与刃面',head='长枪枪头',shaft='圆杆缠纹',cap='长枪尾帽',
    chain='链刃展开',chain_tip='分叉杆刃',chain_links='交扣连接节',chain_grip='圆筒握段')


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def export_nbt(path, xyz, states, size):
    w,h,d = map(int,size)
    header,_ = headers(STATES,(h,d,w),len(xyz))
    with gzip.open(path,'wb',compresslevel=6) as handle:
        handle.write(header)
        for start in range(0,len(xyz),65536):
            p=xyz[start:start+65536]
            raw=np.tile(np.frombuffer(RECORD,np.uint8),(len(p),1))
            rows=raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'],rows['y'],rows['z']=p[:,0],p[:,1],p[:,2]
            rows['state']=states[start:start+65536].astype(np.int32)-1
            handle.write(raw.tobytes())
        handle.write(tag(9,'entities')+b'\x0a\x00\x00\x00\x00\x00')


def materials():
    resources=Resources(instance=Path('E:/Prism/instances/GregTech Leisure-增强版/minecraft'),
        client=Path('E:/Prism/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar'),
        project_resources=ROOT/'src/main/resources')
    result=[]
    for state,label in zip(STATES,LABELS):
        item=resources.material(state)
        item.update(label=label,emissive=False)
        result.append(item)
    sources=dict(resources.sources)
    resources.close()
    save(OUT/'materials.json',result)
    save(OUT/'材质来源.json',sources)
    return result


def main(models=None):
    OUT.mkdir(exist_ok=True)
    (OUT/'NBT').mkdir(exist_ok=True)
    scripts=OUT/'生成脚本'; scripts.mkdir(exist_ok=True)
    palette=materials()
    references=json.loads((REF/'参考清单.json').read_text('utf8'))
    ref_by_id={r['id']:r for r in references['references']}
    models=case.build()+blades.build()+chain.build() if models is None else models
    packed,descriptions,archive=[],[],{}
    next_x=0
    for model in models:
        xyz=np.asarray(list(model['voxels']),np.int32)
        states=np.fromiter(model['voxels'].values(),np.uint8)
        low,high=xyz.min(0),xyz.max(0)
        size=high-low+1
        offset=np.array([next_x,0,0])-low
        points=xyz+offset
        origin=(low+offset).tolist()
        part=SimpleNamespace(name=model['id'],label=model['title'],p=points,states=states,metadata={})
        mesh,quads=mesh_part(part,palette)
        packed.append(mesh)
        file='NBT/识律-'+model['id']+'-方块模型-'+VERSION+'.nbt'
        export_nbt(OUT/file,xyz-low,states,size)
        archive[model['id']+'_xyz']=xyz-low
        archive[model['id']+'_materials']=states
        views={key:dict(label=DETAIL_LABELS[key],center=(np.array(v['target'])+offset).tolist(),
            half=[v['radius']]*3,direction=[.36,.17,1]) for key,v in model['views'].items()}
        refs=[]
        for ref_id in model['references']:
            ref=ref_by_id[ref_id]
            base='../'+REF.name+'/'
            refs.append(dict(id=ref_id,thumbnail=base+ref['thumbnail'],file=base+ref['file'],
                source_url=ref['source_url'],label=ref['view'],kind=ref['kind']))
        descriptions.append(dict(id=model['id'],title=model['title'],blocks=len(xyz),sizeXYZ=size.tolist(),
            origin=origin,features=model['features'],references=refs,views=views,nbt=file,
            source_coordinate_min=low.tolist(),preview_offset=offset.tolist(),rendered_quads=quads,
            sha256=hashlib.sha256((OUT/file).read_bytes()).hexdigest(),
            materials=[dict(state=STATES[i-1],blocks=int(n)) for i,n in zip(*np.unique(states,return_counts=True))]))
        print(model['id'],len(xyz),size.tolist(),quads,flush=True)
        next_x+=int(size[0])+45
    low=np.min([p['origin'] for p in packed],axis=0)
    high=np.max([np.array(p['origin'])+p['size']-1 for p in packed],axis=0)
    data=dict(title='识之律者 · 三兵与武器匣 · 方块复刻 '+VERSION,sizeXYZ=(high-low+1).tolist(),
        bounds=dict(min=low.tolist(),max=high.tolist()),models=descriptions,
        created_at=datetime.now(timezone.utc).isoformat(),
        modeling_method=METHOD,
        status='独立方块外观候选，等待负责人评审。',
        scope='宝剑、长枪、链刃与武器匣独立模型。W09整机布局另行调整。')
    payload=dict(data=data,materials=palette,parts=packed)
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf8'),6)).decode()
    (OUT/'data.js').write_text('window.SENTI_VOXEL_PAYLOAD='+json.dumps(encoded)+';','utf8')
    save(OUT/'manifest.json',data)
    save(OUT/'材料清单.json',[dict(state=state,label=label,
        blocks=sum(next((m['blocks'] for m in model['materials'] if m['state']==state),0) for model in descriptions))
        for state,label in zip(STATES,LABELS)])
    np.savez_compressed(OUT/'完整整数格模型.npz',**archive)
    for source in [Path(__file__),Path(case.__file__),Path(blades.__file__),Path(chain.__file__)]:
        shutil.copy2(source,scripts/source.name)


if __name__ == '__main__':
    main()
