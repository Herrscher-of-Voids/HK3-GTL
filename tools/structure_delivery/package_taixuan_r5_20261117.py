from pathlib import Path
import json
import shutil

import package_taixuan_r2_20261116 as candidate
import taixuan_ground_r5_20261117 as ground


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山中轴山门与松冠_T5_20261117'
PREVIOUS=ROOT/'deliveries/0005_W09_太虚山扩岛嵌观_T4_20261117'


def materials():
    for name in ['materials.json','材质来源.json']:
        shutil.copy2(PREVIOUS/name,OUT/name)
    return json.loads((OUT/'materials.json').read_text('utf8'))


def main():
    candidate.OUT=OUT
    candidate.package.landscape=ground
    candidate.package.materials=materials
    candidate.detail.build=lambda:[]
    candidate.main('T5')
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['previous_candidate']='../'+PREVIOUS.name+'/index.html'
    manifest['detail_changes']=[
        '山门中心移至(0,160,164)，沿X展开，正对主殿和八卦台中轴。',
        '八卦台前补中轴短径，门前先直行下坡，再接折返山阶；上段岩脊随路重接。',
        '删除东侧石桥、人工桥头岩台与沿溪断头石路，水道与瀑布保留。',
        '九棵松树主干顶各补中央扁冠，覆盖露木枝梢，与原分簇树冠相接。',
        '竹丛随新路移至路外岩肩，按实际岩面落根。']
    manifest['gate_center']=[0,160,164]
    manifest['route']=ground.ROUTE.astype(int).tolist()
    manifest['pine_crowns_added']=9
    candidate.package.save(OUT/'manifest.json',manifest)
    js=OUT/'生成脚本/viewer.mjs'
    source=js.read_text('utf8').replace("bridge:modelById.get('mountain_path').views.bridge,",'')
    presets="axis:{label:'中轴俯视',center:[0,170,26],half:[147,70,193],direction:[0,1,0]},creek:{label:'撤桥后的溪岸',center:[142,168,-47],half:[55,27,64],direction:[1,.65,1]},pines:{label:'九棵松树冠',center:[0,260,-38],half:[315,116,250],direction:[-.6,.7,1]},base_front:{label:'嵌观正面',center:[0,141,0],half:[215,52,210],direction:[.15,.1,1]},base_side:{label:'嵌观侧面',center:[0,141,0],half:[215,52,210],direction:[1,.08,.2]},base_under:{label:'岛底与岩肩',center:[0,125,0],half:[205,60,205],direction:[.4,-.3,1]},"
    js.write_text(source.replace("court:{label:'庭院关系'",presets+"court:{label:'庭院关系'"),'utf8')
    html=OUT/'index.html'
    html.write_text(html.read_text('utf8').replace('细节补全 T5','中轴山门与松冠 T5'),'utf8')
    for source in [Path(__file__),Path(ground.__file__),Path(ground.landscape.__file__),
            Path(ground.ground.__file__),ROOT/'tools/structure_delivery/taixuan_ground_r3_20261117.py']:
        shutil.copy2(source,OUT/'生成脚本'/source.name)


if __name__=='__main__':
    main()
