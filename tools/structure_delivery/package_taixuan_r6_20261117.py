from pathlib import Path
import json
import shutil

import package_taixuan_r2_20261116 as candidate
import taixuan_ground_r6_20261117 as ground
import taixuan_architecture_r6_20261117 as architecture


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山远峰弧廊与溪谷_T6_20261117'
PREVIOUS=ROOT/'deliveries/0005_W09_太虚山中轴山门与松冠_T5_20261117'


def materials():
    for name in ['materials.json','材质来源.json']:
        shutil.copy2(PREVIOUS/name,OUT/name)
    return json.loads((OUT/'materials.json').read_text('utf8'))


def main(revision='T6',title='远峰弧廊与溪谷'):
    candidate.OUT=OUT
    candidate.architecture=architecture
    candidate.package.landscape=ground
    candidate.package.materials=materials
    candidate.detail.build=lambda:[]
    candidate.main(revision)
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['previous_candidate']='../'+PREVIOUS.name+'/index.html'
    manifest['detail_changes']=[
        '外围六座独立山峰外移，留出云隙；各峰以偏移岩肩、变宽截面和收尖山顶替换长段等粗崖壁。',
        '瀑布峰外移后，用低岩肩承接山脚浅潭、弯曲溪谷及岛边下瀑，旧直槽退出。',
        '西廊原松移到廊外草岩肩，东松移离殿檐；外峰树随山体重新落根，九棵保留完整顶冠。',
        '西后折廊重建为连续弧廊，铺地、立柱、窗墙与曲檐一起转弯。',
        '按院坪实际顶面压低地形，清除侵入八卦台周围铺地的草皮与高岩。']
    manifest['peak_centers']={n:list(c) for n,_,c,_,_ in ground.PEAKS}
    manifest['gate_center']=[0,160,164]
    manifest['route']=ground.ROUTE.astype(int).tolist()
    candidate.package.save(OUT/'manifest.json',manifest)
    js=OUT/'生成脚本/viewer.mjs'
    source=js.read_text('utf8').replace("bridge:modelById.get('mountain_path').views.bridge,",'')
    presets="axis:{label:'院坪与弧廊俯视',center:[0,173,16],half:[188,75,198],direction:[0,1,0]},creek:{label:'自然溪谷',center:[177,182,-83],half:[68,95,109],direction:[1,.65,1]},pines:{label:'九棵古松',center:[0,260,-50],half:[390,116,300],direction:[-.6,.7,1]},arc:{label:'西后弧廊',center:[-101,179,-81],half:[48,30,71],direction:[-.6,.9,.7]},floor:{label:'完整八卦台铺地',center:[-25,161,137],half:[49,14,35],direction:[-.5,1,1]},peaks:{label:'远峰与云隙',center:[0,202,-64],half:[401,191,325],direction:[-.8,.7,1.3]},base_front:{label:'主岛正面',center:[0,141,0],half:[235,52,230],direction:[.15,.1,1]},base_side:{label:'主岛侧面',center:[0,141,0],half:[235,52,230],direction:[1,.08,.2]},base_under:{label:'主岛岩腹',center:[0,125,0],half:[225,60,225],direction:[.4,-.3,1]},"
    js.write_text(source.replace("court:{label:'庭院关系'",presets+"court:{label:'庭院关系'"),'utf8')
    html=OUT/'index.html'
    html.write_text(html.read_text('utf8').replace('细节补全 '+revision,title+' '+revision),'utf8')
    for source in [Path(__file__),Path(ground.__file__),Path(architecture.__file__),Path(architecture.original.__file__),
            ROOT/'tools/structure_delivery/taixuan_water_r6_20261117.py',Path(ground.landscape.__file__),
            Path(ground.previous.__file__),Path(ground.previous.ground.__file__),
            ROOT/'tools/structure_delivery/taixuan_ground_r3_20261117.py']:
        shutil.copy2(source,OUT/'生成脚本'/source.name)


if __name__=='__main__':
    main()
