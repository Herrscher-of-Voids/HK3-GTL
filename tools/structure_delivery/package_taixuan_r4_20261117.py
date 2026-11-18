from pathlib import Path
import json
import shutil

import package_taixuan_r2_20261116 as candidate
import taixuan_ground_r4_20261117 as ground


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山扩岛嵌观_T4_20261117'
PREVIOUS=ROOT/'deliveries/0005_W09_太虚山岩坪衔接_T3_20261117'


def materials():
    for name in ['materials.json','材质来源.json']:
        shutil.copy2(PREVIOUS/name,OUT/name)
    return json.loads((OUT/'materials.json').read_text('utf8'))


def main():
    candidate.OUT=OUT
    candidate.package.landscape=ground
    candidate.package.materials=materials
    candidate.main('T4')
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['previous_candidate']='../0005_W09_太虚山岩坪衔接_T3_20261117/index.html'
    manifest['detail_changes']+=['主岛向院坪四周扩出不规则草坡与岩肩，地台基础嵌入岛面。',
        '从Y58起同步加宽下部岩腹，宽岩肩自然收向原岛底。',
        '岛面沿山径逐级降低，石阶接入草岩缓坡。']
    candidate.package.save(OUT/'manifest.json',manifest)
    js=OUT/'生成脚本/viewer.mjs'
    presets="base_front:{label:'扩岛嵌观正面',center:[0,141,0],half:[215,52,210],direction:[.15,.1,1]},base_side:{label:'扩岛嵌观侧面',center:[0,141,0],half:[215,52,210],direction:[1,.08,.2]},base_under:{label:'岛底与岩肩仰视',center:[0,125,0],half:[205,60,205],direction:[.4,-.3,1]},"
    js.write_text(js.read_text('utf8').replace("court:{label:'庭院关系'",presets+"court:{label:'庭院关系'"),'utf8')
    html=OUT/'index.html'
    html.write_text(html.read_text('utf8').replace('细节补全 T4','扩岛嵌观 T4'),'utf8')
    for source in [Path(__file__),Path(ground.__file__),Path(ground.landscape.__file__),
            ROOT/'tools/structure_delivery/taixuan_ground_r3_20261117.py']:
        shutil.copy2(source,OUT/'生成脚本'/source.name)


if __name__=='__main__':
    main()
