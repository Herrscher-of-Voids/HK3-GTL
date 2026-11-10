# -*- coding: utf-8 -*-
"""复用静态导出，增加V3局部镜头及与V2的多视角对照。"""
from html import escape
import json
from pathlib import Path
import shutil
import w02_19c_geometry_v3_20261110 as g
import package_w02_19c_v2_20261110 as shared


def main(geometry=None):
    g=geometry or globals()['g']
    version=getattr(g,'VERSION','V3')
    g.OUT.mkdir(exist_ok=True);g.LOG.mkdir(exist_ok=True)
    prior=getattr(g,'PRIOR',None) or g.b.OUT;relative='../'+prior.name
    reference_base=getattr(g,'REFERENCE_BASE',prior);ref_relative='../'+reference_base.name
    previous_version=getattr(g,'PREVIOUS_VERSION','V3' if version=='V4' else 'V2')
    refs=json.loads((reference_base/'参考图清单.json').read_text('utf8'))
    refs['asset_root']=ref_relative+'/参考图'
    shared.save(g.OUT/'参考图清单.json',refs)
    gallery=(reference_base/'参考图总览.html').read_text('utf8')
    gallery=gallery.replace('"参考图/','"'+ref_relative+'/参考图/').replace('← 新版小样','← '+version+'候选')
    (g.OUT/'参考图总览.html').write_text(gallery,'utf8')
    shared.main(g)
    page=g.OUT/'w02/三维评审.html';source=g.OUT/'生成脚本/viewer.mjs'
    camera_views={
        'detail_chest':dict(label='胸甲细节',center=[0,234,15],half=[52,65,45],direction=[-.4,.1,1.6],file='胸甲细节.png'),
        'detail_wheel':dict(label='轮组细节',center=[64,227,-1],half=[34,40,39],direction=[1.7,.4,1],file='轮组细节.png'),
        'detail_hand':dict(label='机械手细节',center=[153,112,48],half=[37,42,30],direction=[.6,.15,1.6],file='机械手细节.png'),
        'detail_back':dict(label='背部细节',center=[0,216,-35],half=[53,57,25],direction=[.3,.1,-1.7],file='背部细节.png'),
        'detail_module':dict(label='双轨模块细节',center=[91,291,8],half=[20,22,73],direction=[1.3,.8,1.2],file='模块细节.png')}
    camera_views=getattr(g,'CAMERA_VIEWS',camera_views)
    text=source.read_text('utf8')
    text=text.replace('function setView(name) {','const focusViews='+json.dumps(camera_views,ensure_ascii=False)+';\n  function setView(name) {',1)
    anchor="controls.target.copy(target);camera.up.set(0,1,0);"
    assert anchor in text
    text=text.replace(anchor,"if(focusViews[name]){target.copy(offset).add(new THREE.Vector3(...focusViews[name].center));direction.set(...focusViews[name].direction);}\n    "+anchor,1)
    anchor="const bounds=name==='core'?"
    assert anchor in text
    text=text.replace(anchor,"const bounds=focusViews[name]?new THREE.Box3(target.clone().sub(new THREE.Vector3(...focusViews[name].half)),target.clone().add(new THREE.Vector3(...focusViews[name].half))):name==='core'?",1)
    source.write_text(text,'utf8')
    buttons=''.join('<button data-view="'+key+'">'+value['label']+'</button>' for key,value in camera_views.items())
    text=page.read_text('utf8').replace('<button data-view="low">仰视</button>','<button data-view="low">仰视</button>'+buttons,1)
    text=text.replace('60张参考：32张官方、28张二创结构辅助；11个完整静态构件。','沿用60张参考，细化11个完整静态构件；新增5个局部镜头。')
    page.write_text(text,'utf8')
    shared.save(g.OUT/'局部镜头.json',camera_views)
    manifest=json.loads((g.OUT/'manifest.json').read_text('utf8'))
    index=g.OUT/'index.html';text=index.read_text('utf8')
    start=text.index('<p class="note">');end=text.index('</p>',start)+4
    text=text[:start]+'<p class="note">'+escape(manifest['summary'])+' '+previous_version+'完整保留，'+version+'仍为未批准的独立静态造型候选。</p>'+text[end:]
    text=text.replace('src="参考图/','src="'+ref_relative+'/参考图/')
    comparison='<h2>同视角：左'+previous_version+'，右'+version+'</h2><p>镜头方向和完整取景规则一致；比例改变时完整取景缩放会相应改变。</p>'
    for file,label in [('完整预览.png','斜前全景'),('正面.png','正面'),('背面.png','背面'),('俯视.png','俯视')]:
        comparison+='<h3>'+label+'</h3><div class="grid"><img src="'+relative+'/'+file+'" alt="'+previous_version+' '+label+'"><img src="'+file+'" alt="'+version+' '+label+'"></div>'
    details='<h2>多视角细节</h2><ul>'+''.join('<li>'+escape(r['component'])+'：'+escape(r['change'])+'（'+escape('、'.join(r['references']))+'）</li>' for r in manifest['detail_changes'])+'</ul>'
    details+='<div class="grid">'+''.join('<figure><img src="'+value['file']+'" alt="'+value['label']+'"><figcaption>'+value['label']+'</figcaption></figure>' for value in camera_views.values())+'</div>'
    text=text.replace('<h2>正面轮廓对照</h2>',details+comparison+'<h2>官方正面轮廓对照</h2>',1)
    text=text.replace('<a href="参考图总览.html">查看60张参考与来源</a>','<a href="参考图总览.html">查看60张参考与来源</a> · <a href="'+relative+'/index.html">保留的'+previous_version+'</a>',1)
    if version=='V4':
        text=text.replace('参考为战斗展开姿态，候选选用双臂下垂姿态，不能按相同姿势宣称逐处还原。','参考为官方战斗展开姿态；候选按负责人反馈采用前探屈臂的机甲兽姿态，属于造型转译。')
        text=text.replace('多视角细化V4','机甲兽体态V4')
        page.write_text(page.read_text('utf8').replace('多视角细化V4','机甲兽体态V4'),'utf8')
    if version=='V5':
        text=text.replace('参考为战斗展开姿态，候选选用双臂下垂姿态，不能按相同姿势宣称逐处还原。','仅主躯干恢复V3，其余构件保持V4；与官方战斗展开姿态不同，不宣称逐处复刻。')
        text=text.replace('多视角细化V5',g.PRESENTATION_TITLE)
        page.write_text(page.read_text('utf8').replace('多视角细化V5',g.PRESENTATION_TITLE),'utf8')
    if version=='V6':
        text=text.replace('参考为战斗展开姿态，候选选用双臂下垂姿态，不能按相同姿势宣称逐处还原。',g.POSE_NOTE)
        text=text.replace('多视角细化V6',g.PRESENTATION_TITLE)
        page.write_text(page.read_text('utf8').replace('多视角细化V6',g.PRESENTATION_TITLE),'utf8')
    index.write_text(text,'utf8')
    shutil.copy2(__file__,g.OUT/'生成脚本'/Path(__file__).name)


if __name__=='__main__':main()
