from pathlib import Path
import json
import shutil

import package_taixuan_r6_20261117 as package
import taixuan_ground_r8_20261117 as ground
import taixuan_water_r8_20261117 as water


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山拐点直瀑与完整岩岸_T8_20261117'


def main():
    package.OUT=OUT
    package.PREVIOUS=ROOT/'deliveries/0005_W09_太虚山远峰弧廊与溪谷_T6_20261117'
    package.ground=ground
    package.main('T8','拐点直瀑与完整岩岸')
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['detail_changes']=[
        '紫色标记按负责人纠正解释为外围动线，恢复T6外围岩岸，撤销T7整片水帘和大范围削岸。',
        '水在河道开始兜回的拐点短跌，沿岩岸下方短洞穿出，接11格宽集中窄瀑；保留上部连续岩路。',
        '取消后段回弯和旧单口瀑布，原下游河床补回草岩；沿用T6建筑、远峰、树位和院坪。']
    manifest['water_parameters']=ground.water_parameters
    manifest['rejected_candidate']='../0005_W09_太虚山紫线直落瀑布_T7_20261117/index.html'
    package.candidate.package.save(OUT/'manifest.json',manifest)
    js=OUT/'生成脚本/viewer.mjs'
    source=js.read_text('utf8').replace("creek:{label:'自然溪谷',center:[177,182,-83],half:[68,95,109]",
        "creek:{label:'拐点窄瀑与完整岩岸',center:[173,148,-85],half:[61,119,105]")
    source=source.replace("pines:{label:'九棵古松'",
        "outlet:{label:'拐点出水近景',center:[173,146,-68],half:[30,33,30],direction:[1,.28,.65]},bank:{label:'连续外围岩路',center:[168,159,-78],half:[41,20,61],direction:[0,1,0]},pines:{label:'九棵古松'")
    js.write_text(source,'utf8')
    for source in [Path(__file__),Path(package.__file__),Path(ground.base.__file__),Path(water.__file__)]:
        shutil.copy2(source,OUT/'生成脚本'/source.name)


if __name__=='__main__':
    main()
