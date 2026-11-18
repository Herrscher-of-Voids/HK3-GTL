from pathlib import Path
import json
import shutil

import package_taixuan_r6_20261117 as package
import taixuan_ground_r7_20261117 as ground
import taixuan_water_r7_20261117 as water


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山紫线直落瀑布_T7_20261117'


def main():
    package.OUT=OUT
    package.PREVIOUS=ROOT/'deliveries/0005_W09_太虚山远峰弧廊与溪谷_T6_20261117'
    package.ground=ground
    package.main('T7','紫线直落瀑布')
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['detail_changes']=[
        '按负责人紫线降低水道云海外岸，浅潭与贴山短溪沿外缘直接垂落为两格厚弧形水帘。',
        '取消下游回弯、旧单口凿槽与X204/Z-8水柱，原下游水道恢复草岩岸坡。',
        '沿用T6远峰、弧廊、树位、中轴山门、完整院坪与同色像素材质。']
    manifest['water_parameters']=ground.water_parameters
    package.candidate.package.save(OUT/'manifest.json',manifest)
    js=OUT/'生成脚本/viewer.mjs'
    js.write_text(js.read_text('utf8').replace("creek:{label:'自然溪谷',center:[177,182,-83],half:[68,95,109]",
        "creek:{label:'紫线外沿直落瀑布',center:[181,168,-119],half:[61,115,82]"),'utf8')
    for source in [Path(__file__),Path(package.__file__),Path(ground.base.__file__),Path(water.__file__)]:
        shutil.copy2(source,OUT/'生成脚本'/source.name)


if __name__=='__main__':
    main()
