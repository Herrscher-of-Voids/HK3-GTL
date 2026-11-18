from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import base64
import gzip
import json
import re
import shutil

import numpy as np
from scipy.ndimage import affine_transform

from package_0005_w12_author_blueprint_20261116 import mesh_part


ROOT=Path(__file__).resolve().parents[2]
T9=ROOT/'deliveries/0005_W09_太虚山紫线岩岸轮廓_T9_20261117'
S1=ROOT/'deliveries/0005_W09_识律三兵方块复刻_S1_20261116'
OUT=ROOT/'deliveries/0005_W09_T9与S1融合摆位_F1_20261117'


def read(path):
    return json.loads(path.read_text('utf8'))


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


def rotate_z(degrees):
    a=np.deg2rad(degrees)
    return np.round([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]],12)


def placed(xyz,states,pivot,matrix,anchor):
    size=xyz.max(0)+1
    volume=np.zeros(tuple(size),np.uint8)
    volume[tuple(xyz.T)]=states
    corners=np.array(np.meshgrid(*[(0,n-1) for n in size],indexing='ij')).reshape(3,-1).T
    corners=(corners-pivot)@matrix.T
    low=np.floor(corners.min(0)).astype(int)
    high=np.ceil(corners.max(0)).astype(int)
    rotated=affine_transform(volume,matrix.T,offset=pivot+matrix.T@low,
        output_shape=tuple(high-low+1),order=0,mode='grid-constant',prefilter=False)
    points=np.argwhere(rotated)
    return points+low+anchor,rotated[tuple(points.T)]


def main():
    OUT.mkdir(exist_ok=True)
    scripts=OUT/'生成脚本'
    scripts.mkdir(exist_ok=True)
    encoded=json.loads((T9/'data.js').read_text('utf8').split('=',1)[1].rstrip(';\n'))
    payload=json.loads(gzip.decompress(base64.b64decode(encoded)))
    original=payload['data']
    palette=payload['materials']
    states=[m['state'] for m in palette]
    weapon_palette=read(S1/'materials.json')
    for material in weapon_palette:
        if material['state'] not in states:
            states.append(material['state'])
            palette.append(material)
    marker=next(m for m in read(ROOT/'deliveries/0005_W09_作者蓝图原案_A1_20261116/materials.json')
        if m['state']=='minecraft:redstone_block')
    states.append(marker['state'])
    marker['label']='唯一主控位置标记'
    palette.append(marker)
    remap=np.array([0]+[states.index(m['state'])+1 for m in weapon_palette],np.uint8)
    for part in payload['parts']:
        part['modelId']='taixuan'
        for key in ['starts','lengths','spans']:
            part[key].extend([[[] for _ in range(6)] for _ in range(len(palette)-len(part[key]))])
    models=[dict(id='taixuan',title='T9完整山观',origin=original['bounds']['min'],
        sizeXYZ=original['sizeXYZ'],blocks=original['total_blocks'],
        features=['T9已获负责人采用，原岩岸、殿宇、山门、院坪、远峰和水路逐格沿用。'],
        references=[],views={})]
    source=read(S1/'manifest.json')
    descriptions={m['id']:m for m in source['models']}
    archive=np.load(S1/'完整整数格模型.npz')
    placements=[
        ('sword','左前宝剑',[-280,45,310],20,False),
        ('spear','右前长枪',[280,65,310],-18,True),
        ('case','后方武器匣',[0,80,-435],0,False),
        ('chain','前方低位链刃',[0,110,420],-90,False)]
    recipe=[]
    transformed={}
    for name,title,anchor,angle,flip in placements:
        xyz=archive[name+'_xyz']
        material=remap[archive[name+'_materials']]
        size=np.array(descriptions[name]['sizeXYZ'])
        pivot=np.array([size[0]//2,size[1]-1 if flip else 0,size[2]//2])
        if name=='chain':
            pivot=size//2
        matrix=rotate_z(angle)@np.diag([1,-1,-1] if flip else [1,1,1])
        xyz,material=placed(xyz,material,pivot,matrix,np.array(anchor))
        part=SimpleNamespace(name=name,label=title,p=xyz,states=material,metadata={})
        mesh,_=mesh_part(part,palette)
        mesh['modelId']=name
        payload['parts'].append(mesh)
        low,high=xyz.min(0),xyz.max(0)
        models.append(dict(id=name,title=title,origin=low.tolist(),sizeXYZ=(high-low+1).tolist(),
            blocks=len(xyz),features=['S1原配色与完整轮廓，静态变换后重新量化为整数格。'],references=[],views={}))
        recipe.append(dict(id=name,anchor=anchor,pivot=pivot.tolist(),rotation_z=angle,
            reverse_y=flip,bounds=dict(min=low.tolist(),max=high.tolist()),blocks=len(xyz)))
        transformed[name+'_xyz']=xyz
        transformed[name+'_materials']=material
    controller=np.array([[0,163,138]])
    marker_part=SimpleNamespace(name='controller',label='主控建议位置',p=controller,
        states=np.array([len(palette)],np.uint8),metadata={})
    mesh,_=mesh_part(marker_part,palette)
    mesh['modelId']='controller'
    payload['parts'].append(mesh)
    models.append(dict(id='controller',title='唯一主控建议位置',origin=controller[0].tolist(),
        sizeXYZ=[1,1,1],blocks=1,features=['八卦台前缘(0,163,138)，红石仅标识主控建议位置。',
            '其余全部实体格可替换合法通用接口，由玩家选择位置与朝向。'],references=[],views={}))
    low=np.min([m['origin'] for m in models],axis=0)
    high=np.max([np.array(m['origin'])+m['sizeXYZ']-1 for m in models],axis=0)
    data=dict(title='W09 · T9与S1融合摆位研究 F1',created_at=datetime.now(timezone.utc).isoformat(),
        sizeXYZ=(high-low+1).tolist(),bounds=dict(min=low.tolist(),max=high.tolist()),models=models,
        total_blocks=sum(m['blocks'] for m in models),material_count=len(palette),
        status='组件融合摆位研究，工业层、全机尺度与运动后续设计。',
        component_approval=dict(T9=True,S1='本轮负责人指定融合来源'),
        sources=dict(T9='../'+T9.name+'/index.html',S1='../'+S1.name+'/index.html'),
        machine=dict(id='W09',voltage='CEV',research='RN-CKV',output='civilization_consensus_archive'),
        recipe=recipe,controller=[0,163,138],
        design=['T9承担上层完整山观与玩家动线，剑枪分立前侧，武器匣居后，链刃横置前方低云。',
            '后续在岛腹设计数据读写、认知载体制造与共识档案汇聚机械层，沿用现有真实工艺。',
            '机能、实体规模、穿模及动态作为整机设计继续处理，当前显示用于讨论组件比例与摆位。'],
        interface_rule='仅唯一主控固定，其余全部实体格可替换合法通用接口，朝向自选。')
    payload['data']=data
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode()
    (OUT/'data.js').write_text('window.TAIXUAN_VOXEL_PAYLOAD='+json.dumps(encoded)+';','utf8')
    save(OUT/'manifest.json',data)
    save(OUT/'materials.json',palette)
    np.savez_compressed(OUT/'组合武器整数格.npz',**transformed,controller_xyz=controller)
    html=(T9/'index.html').read_text('utf8')
    html=re.sub(r'<title>.*?</title>','<title>W09 · T9与S1融合摆位研究 F1</title>',html)
    html=re.sub(r'<h1>.*?</h1>','<h1>W09 · 太虚山与识律三兵</h1>',html)
    html=re.sub(r'<div class="eyebrow">.*?</div>','<div class="eyebrow">0005 / W09 / 组件融合摆位 F1</div>',html)
    html=re.sub(r'<p class="links">下载NBT：.*?</p>',
        '<p class="links"><a href="../'+T9.name+'/index.html">T9基线</a> · <a href="../'+S1.name+'/index.html">S1基线</a></p>',html)
    html=re.sub(r'<p class="links"><a href="NBT/.*?</p>',
        '<p class="links">完整山观与S1三兵同场摆位；岛腹工业层和正式规模继续设计。</p>',html)
    html=html.replace('31幅参考中的可见形制逐格重建；山势、背面、室内与连接路径包含补建设计。','T9完整沿用，S1静态变换后重新量化。')
    start=html.index('<section class="controls"><h2>')
    proposal='''<section class="controls"><h2>W09融合方向</h2><p>T9完整山观作为上层；S1剑枪分列前侧，武器匣居后，链刃放在前方低位。本页显示组件摆位与比例。</p><p>岛腹下一步设计数据读写、认知载体制造和共识档案汇聚机械层，将三兵与主工艺连接。</p><p>CEV正式规模、工艺结构及动态随整机继续设计。</p><p class="links"><a href="../'''+T9.name+'''/index.html">T9采用基线</a> · <a href="../'''+S1.name+'''/index.html">S1武器来源</a></p></section>'''
    html=html[:start]+proposal+html[start:]
    html=html.replace('href="材料清单.json"','href="materials.json"')
    (OUT/'index.html').write_text(html,'utf8')
    shutil.copy2(T9/'style.css',OUT/'style.css')
    js=(T9/'生成脚本/viewer.mjs').read_text('utf8')
    views="{...basicViews,court:{label:'院坪与主控',center:[0,181,99],half:[154,55,140],direction:[-.25,.6,1]},weapons:{label:'三兵与山观比例',center:[0,205,0],half:[440,235,470],direction:[-.65,.45,1.4]},entry:{label:'山门中轴',center:[0,190,-8],half:[230,115,225],direction:[0,.15,1]},controller:{label:'主控建议位置',center:[0,163,138],half:[16,12,18],direction:[-.4,.7,1]},creek:{label:'岩岸与窄瀑',center:[173,148,-85],half:[61,119,105],direction:[1,.65,1]}}"
    js=re.sub(r"function views\(\)\{.*?\}\n",'function views(){return activeModel===\'all\'?'+views+':{...basicViews,...modelById.get(activeModel).views};}\n',js,count=1)
    js=js.replace("'完整太虚山'","'W09融合摆位 F1'")
    js=js.replace("'完整拂云观、薄八卦台、分节青岩与回折山径。','山峰坐标和缺失视面按已见形制补建；逐图来源与补建范围保存在构件记录。'",','.join(json.dumps(v,ensure_ascii=False) for v in data['design']))
    js=js.replace('太虚山-${activeModel}-${activeView}-T9.png','W09-${activeModel}-${activeView}-F1.png')
    (scripts/'viewer.mjs').write_text(js,'utf8')
    shutil.copy2(Path(__file__),scripts/Path(__file__).name)
    print(json.dumps(dict(out=str(OUT),size_xyz=data['sizeXYZ'],blocks=data['total_blocks'],placements=recipe),ensure_ascii=False))


if __name__=='__main__':
    main()
