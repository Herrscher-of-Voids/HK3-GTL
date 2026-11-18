from pathlib import Path
import json
import shutil

import package_taixuan_r6_20261117 as package
import taixuan_ground_r9_20261117 as ground


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山紫线岩岸轮廓_T9_20261117'


def main():
    package.OUT=OUT
    package.PREVIOUS=ROOT/'deliveries/0005_W09_太虚山拐点直瀑与完整岩岸_T8_20261117'
    package.ground=ground
    package.main('T9','紫线岩岸轮廓')
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['detail_changes']=[
        '岩岸按负责人紫线收整，上段保留沿溪窄岸，拐点以下接连续弧形外缘。',
        '移除旧回弯对主岛岩肩的生成影响，收回舌状岩台，岩腹截面随高度自然渐收。',
        '沿用T8水路、拐点短洞及集中窄瀑；建筑、远峰、树位、院坪和像素材质继续沿用。']
    manifest['water_parameters']=ground.water_parameters
    manifest['geometry_parameters']=ground.geometry_parameters
    package.candidate.package.save(OUT/'manifest.json',manifest)
    js=OUT/'生成脚本/viewer.mjs'
    source=js.read_text('utf8').replace("creek:{label:'自然溪谷',center:[177,182,-83],half:[68,95,109]",
        "creek:{label:'紫线岩岸与拐点窄瀑',center:[173,148,-85],half:[61,119,105]")
    source=source.replace("pines:{label:'九棵古松'",
        "outlet:{label:'拐点出水近景',center:[173,146,-68],half:[30,33,30],direction:[1,.28,.65]},bank:{label:'紫线岩岸俯视',center:[168,159,-57],half:[51,25,103],direction:[0,1,0]},pines:{label:'九棵古松'")
    js.write_text(source,'utf8')
    for source in [Path(__file__),Path(package.__file__),Path(ground.base.__file__),
            Path(ground.previous_ground.__file__),ROOT/'tools/structure_delivery/taixuan_water_r8_20261117.py']:
        shutil.copy2(source,OUT/'生成脚本'/source.name)


if __name__=='__main__':
    main()
