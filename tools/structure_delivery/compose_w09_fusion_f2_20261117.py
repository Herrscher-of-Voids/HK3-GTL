from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import base64
import gzip
import hashlib
import json
import re
import shutil

import numpy as np

from compose_w09_t9_s1_20261117 import placed, rotate_z
from package_0005_w12_author_blueprint_20261116 import mesh_part
from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
import w09_fusion_core_20261117 as core
import w09_fusion_industry_20261117 as industry


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_T9与S2山观兵装矩阵_F2_20261117'
T9=ROOT/'deliveries/0005_W09_太虚山紫线岩岸轮廓_T9_20261117'
S2=ROOT/'deliveries/0005_W09_识律武器细节复刻_S2_20261116'
A1=ROOT/'deliveries/0005_W09_作者蓝图原案_A1_20261116'
TITLE='W09 · 识之律者 · 山观兵装共识矩阵 F2'


def read(path):
    return json.loads(path.read_text('utf8'))


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(keys,states,low,size,palette):
    w,h,d=map(int,size)
    header,_=headers([m['state'] for m in palette],(h,d,w),len(keys))
    record=np.frombuffer(RECORD,np.uint8)
    target=OUT/'W09-山观兵装共识矩阵-F2.nbt'
    with gzip.open(target,'wb',compresslevel=6) as f:
        f.write(header)
        for start in range(0,len(keys),65536):
            k=keys[start:start+65536]
            raw=np.tile(record,(len(k),1))
            rows=raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'],rows['y'],rows['z']=k%w,k//(w*d),k//w%d
            rows['state']=states[start:start+65536].astype(np.int32)-1
            f.write(raw.tobytes())
        f.write(tag(9,'entities')+b'\x0a\x00\x00\x00\x00\x00')
    xyz=np.c_[keys%w,keys//(w*d),keys//w%d].astype(np.int32)
    np.savez_compressed(OUT/'完整整数格模型.npz',xyz=xyz,states=states,origin=low,size=size)
    return target


def main():
    OUT.mkdir(exist_ok=True)
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    encoded=json.loads((T9/'data.js').read_text('utf8').split('=',1)[1].rstrip(';\n'))
    payload=json.loads(gzip.decompress(base64.b64decode(encoded)))
    original=payload['data'];palette=payload['materials'];state_names=[m['state'] for m in palette]
    maps=[]
    for source in (S2,A1):
        materials=read(source/'materials.json')
        for m in materials:
            if m['state'] not in state_names:
                state_names.append(m['state']);palette.append(m)
        maps.append(np.array([0]+[state_names.index(m['state'])+1 for m in materials],np.uint8))
    weapon_map,machine_map=maps
    archive=np.load(S2/'完整整数格模型.npz')
    descriptions={m['id']:m for m in read(S2/'manifest.json')['models']}
    placements=[
        dict(id='sword',title='左前倒悬宝剑',anchor=[-440,-300,230],angle=15,flip=True,center=False),
        dict(id='spear',title='右侧外倾长枪',anchor=[400,-300,170],angle=-18,flip=False,center=False),
        dict(id='chain',title='前下方横置九段链刃',anchor=[0,-340,450],angle=-90,flip=False,center=True),
        dict(id='case',title='后下方横卧武器匣',anchor=[0,-20,-470],angle=-90,flip=False,center=True)]
    added=[]
    for p in placements:
        name=p['id'];size=np.array(descriptions[name]['sizeXYZ'])
        pivot=size//2 if p['center'] else np.array([size[0]//2,size[1]-1 if p['flip'] else 0,size[2]//2])
        matrix=rotate_z(p['angle'])@np.diag([1,-1,-1] if p['flip'] else [1,1,1])
        xyz,states=placed(archive[name+'_xyz'],weapon_map[archive[name+'_materials']],pivot,matrix,np.array(p['anchor']))
        item=SimpleNamespace(name='s2_'+name,label=p['title'],p=xyz,states=states,
            metadata=dict(section=name,source='S2',pivot=pivot.tolist(),matrix=matrix.tolist(),anchor=p['anchor']))
        p.update(pivot=pivot.tolist(),matrix=matrix.tolist(),bounds=dict(min=xyz.min(0).tolist(),max=xyz.max(0).tolist()),blocks=len(xyz))
        added.append(item)
    notes=[]
    for module in (industry,core):
        parts,changes=module.build();notes+=changes
        for p in parts:p.states=machine_map[p.states]
        added+=parts
        print(module.__name__,len(parts),sum(len(p.p) for p in parts),flush=True)
    from author_w05_shapes_20261115 import Part
    plinth=Part('controller_plinth','八卦台前缘主控石台',section='controller')
    plinth.box([-3,161,135],[3,161,142],int(machine_map[4]))
    plinth.box([-2,162,136],[2,162,140],int(machine_map[2]))
    plinth.box([-1,162,140],[1,162,140],int(machine_map[3]))
    added.append(plinth.finish())
    source=np.load(T9/'完整整数格模型.npz')
    mountain=SimpleNamespace(name='taixuan',label='T9完整山观',p=source['xyz']+source['origin'].astype(np.int32),
        states=source['states'],metadata=dict(section='taixuan',source='T9'))
    controller=[0,163,138]
    marker=SimpleNamespace(name='controller',label='唯一主控位置标记',p=np.array([controller]),
        states=np.array([int(machine_map[14])],np.uint8),metadata=dict(section='controller',preview_marker=True))
    all_parts=added+[mountain,marker]
    low=np.min([p.p.min(0) for p in all_parts],axis=0)
    high=np.max([p.p.max(0) for p in all_parts],axis=0);size=high-low+1;w,h,d=map(int,size)
    keys=np.concatenate([((p.p[:,1].astype(np.int64)-low[1])*d+p.p[:,2]-low[2])*w+p.p[:,0]-low[0] for p in all_parts])
    values=np.concatenate([p.states for p in all_parts])
    owners=np.repeat(np.arange(len(all_parts),dtype=np.uint16),[len(p.p) for p in all_parts])
    keys,chosen=np.unique(keys[::-1],return_index=True);chosen=len(values)-chosen-1
    values,owners=values[chosen],owners[chosen];del chosen
    target=export(keys,values,low,size,palette)
    print('完整NBT与NPZ',len(keys),size.tolist(),flush=True)
    models=[dict(id='taixuan',title='T9山观',origin=original['bounds']['min'],sizeXYZ=original['sizeXYZ'],
        blocks=len(mountain.p),features=['采用T9完整山观、紫线岩岸与集中窄瀑。'],references=[],views={})]
    for p in payload['parts']:
        p['modelId']='taixuan'
        for key in ('starts','lengths','spans'):p[key].extend([[[] for _ in range(6)] for _ in range(len(palette)-len(p[key]))])
    grouped={}
    for index,p in enumerate(all_parts):
        if p.name=='taixuan':continue
        selected=owners==index;k=keys[selected]
        if not len(k):continue
        q=np.c_[k%w,k//(w*d),k//w%d].astype(np.int32)+low
        visible=SimpleNamespace(name=p.name,label=p.label,p=q,states=values[selected],metadata=p.metadata)
        item,_=mesh_part(visible,palette)
        group=p.metadata['section']
        if group not in ('sword','spear','chain','case','controller','rear','core','core_frame','chains'):group='industry'
        if group=='core_frame' or group=='chains':group='core'
        item['modelId']=group;payload['parts'].append(item)
        grouped.setdefault(group,[]).append(visible)
        print('表面',index+1,len(all_parts),p.name,len(q),flush=True)
    labels=dict(sword='S2宝剑',spear='S2长枪',chain='S2链刃',case='S2兵匣',controller='主控石台',rear='后方折扇',core='羽刃与共识核心',industry='下层工业矩阵')
    for name,parts in grouped.items():
        lo=np.min([p.p.min(0) for p in parts],axis=0);hi=np.max([p.p.max(0) for p in parts],axis=0)
        models.append(dict(id=name,title=labels[name],origin=lo.tolist(),sizeXYZ=(hi-lo+1).tolist(),blocks=sum(len(p.p) for p in parts),features=[p.label for p in parts],references=[],views={}))
    material_counts=np.bincount(values,minlength=len(palette)+1)[1:]
    block_ids=sorted({m['state'].split('[',1)[0] for m,n in zip(palette,material_counts) if n})
    measured=dict(footprint=w*d,bounding_volume=w*h*d,height=h,solid_blocks=len(keys),unique_block_types=len(block_ids))
    baselines=dict(footprint=(900601,'W10'),bounding_volume=(441313404,'W03'),height=(636,'W03'),
        solid_blocks=(23541415,'W12'),unique_block_types=(58,'W01'))
    scale_comparison={key:dict(actual=measured[key],lower_voltage_maximum=maximum,source=source,
        strictly_larger=measured[key]>maximum,difference=measured[key]-maximum)
        for key,(maximum,source) in baselines.items()}
    data=dict(title=TITLE,created_at=datetime.now(timezone.utc).isoformat(),sizeXYZ=size.tolist(),
        bounds=dict(min=low.tolist(),max=high.tolist()),models=models,total_blocks=len(keys),
        part_block_sum=sum(len(p.p) for p in all_parts),material_count=int(np.count_nonzero(material_counts)),
        unique_block_types=len(block_ids),block_ids=block_ids,scale_comparison=scale_comparison,
        machine=dict(id='W09',controller='hk3gtl:w09_civilization_consensus_matrix',voltage='CEV',research='RN-CKV'),
        controller=controller,placements=placements,sources=dict(T9=str(T9.relative_to(ROOT)),S2=str(S2.relative_to(ROOT)),A1=str(A1.relative_to(ROOT))),
        design=['上层T9完整山观，外围S2三兵与横卧兵匣，下层镂空机械八卦矩阵。',
            '认知载体、读写校验与共识汇聚三组工艺外观连接中央羽刃核心，原CEV/RN-CKV工艺身份保持。',
            '第一稿静态排位；T9组件已采用，整机轮廓、运动及正式几何接入继续评审。'],
        notes=notes,parts=[dict(id=p.name,label=p.label,blocks=len(p.p),metadata=p.metadata) for p in all_parts],
        conflicts=dict(extra_memberships=sum(len(p.p) for p in all_parts)-len(keys),priority='T9原实体优先，唯一主控标记优先。其余交接采用后写构件。',
            pending=['整机外观与承托比例评审','全量接合与穿模细化','CEV五项规模中未超过低电压正式结构的项目待修订','运动与游戏几何接入']),
        interface_rule='仅主控位置固定，其余实体格可自由替换合法通用接口并自选朝向。',
        nbt=target.name,nbt_sha256=digest(target),status='W09融合第一稿，全整数格静态外观候选，待负责人评审。')
    save(OUT/'manifest.json',data);save(OUT/'materials.json',palette)
    save(OUT/'材料清单.json',[dict(state=m['state'],blocks=int(n)) for m,n in zip(palette,material_counts) if n])
    payload['data']=data
    packed=gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)
    (OUT/'data.js').write_text('window.TAIXUAN_VOXEL_PAYLOAD='+json.dumps(base64.b64encode(packed).decode())+';','utf8')
    html=(T9/'index.html').read_text('utf8')
    html=re.sub(r'<title>.*?</title>','<title>'+TITLE+'</title>',html)
    html=re.sub(r'<h1>.*?</h1>','<h1>'+TITLE+'</h1>',html)
    html=re.sub(r'<div class="eyebrow">.*?</div>','<div class="eyebrow">0005 / W09 / T9 + S2 融合第一稿 F2</div>',html)
    html=re.sub(r'<section class="controls"><h2>同源参考.*?</section>','<div id="references" hidden></div>',html)
    html=re.sub(r'<p class="links">62幅.*?</p>','<p class="links">T9完整山观与S2原比例兵装；新设计下层矩阵、核心分层、承托与后方折扇。</p>',html)
    html=re.sub(r'href="NBT/.*?\.nbt"','href="'+target.name+'"',html)
    html=html.replace('静态模型 · 每格为一个实际方块','静态融合稿 · 每格为一个实际方块')
    html=html.replace('<h2>观察构件</h2>','<h2>观察构件</h2><p>仅主控固定，其余实体方块自由替换合法通用接口。</p>')
    (OUT/'index.html').write_text(html,'utf8');shutil.copy2(T9/'style.css',OUT/'style.css')
    js=(T9/'生成脚本/viewer.mjs').read_text('utf8')
    views=dict(core=dict(label='岛腹共识核心',center=[0,-180,0],half=[220,195,220],direction=[-.6,.18,1]),
        industry=dict(label='机械八卦与工艺阵列',center=[0,-350,0],half=[460,95,490],direction=[-.65,.85,1]),
        court=dict(label='山观与主控',center=[0,185,30],half=[165,65,173],direction=[-.3,.65,1]),
        weapons=dict(label='三兵与山观比例',direction=[-.65,.4,1.4]),
        under=dict(label='岩腹与机械衔接',center=[0,-65,0],half=[300,275,310],direction=[.6,-.15,1]),
        fan=dict(label='后方兵匣与折扇',center=[0,100,-490],half=[390,310,175],direction=[.35,.35,-1]),
        controller=dict(label='唯一主控石台',center=controller,half=[13,12,15],direction=[-.4,.7,1]),
        creek=dict(label='T9岩岸与窄瀑',center=[173,148,-85],half=[61,119,105],direction=[1,.65,1]))
    js=re.sub(r'function views\(\)\{.*?\}\n',"function views(){return activeModel==='all'?{...basicViews,..."+json.dumps(views,ensure_ascii=False)+"}:{...basicViews,...modelById.get(activeModel).views};}\n",js,count=1)
    js=js.replace("all?'完整太虚山'","all?'W09山观兵装矩阵'")
    js=js.replace("all?data.models.reduce((sum,m)=>sum+m.blocks,0)","all?data.total_blocks")
    js=js.replace("['完整拂云观、薄八卦台、分节青岩与回折山径。','山峰坐标和缺失视面按已见形制补建；逐图来源与补建范围保存在构件记录。']",'data.design')
    js=js.replace('太虚山-${activeModel}-${activeView}-T9.png','W09-${activeModel}-${activeView}-F2.png')
    (scripts/'viewer.mjs').write_text(js,'utf8')
    for name in [Path(__file__).name,'w09_fusion_core_20261117.py','w09_fusion_industry_20261117.py']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    print(json.dumps(dict(out=str(OUT),size_xyz=size.tolist(),blocks=len(keys),materials=data['material_count']),ensure_ascii=False),flush=True)


if __name__=='__main__':main()
