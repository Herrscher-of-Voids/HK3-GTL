from pathlib import Path
import json
import shutil

import package_taixuan_r2_20261116 as candidate
import taixuan_ground_r3_20261117 as ground


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山岩坪衔接_T3_20261117'


def main():
    candidate.OUT=OUT
    candidate.package.landscape=ground
    candidate.main('T3')
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['previous_candidate']='../0005_W09_太虚山细节补全_T2_20261116/index.html'
    manifest['detail_changes']+=['主台地上部取消斜顶，承岩顶面Y156逐格贴合院坪底面Y157。',
        '上部岩壁从既有Y107截面渐变至院坪真实轮廓，连接原下部山岩。',
        '山门与回折石阶下方补齐连续岩脊，接入既有山体。']
    candidate.package.save(OUT/'manifest.json',manifest)
    js=OUT/'生成脚本/viewer.mjs'
    presets="base_front:{label:'院坪承岩正面',center:[0,142,0],half:[164,42,158],direction:[.15,.02,1]},base_side:{label:'院坪承岩侧面',center:[0,142,0],half:[164,42,158],direction:[1,.02,.2]},base_under:{label:'院坪底面仰视',center:[0,141,-5],half:[155,30,150],direction:[.4,-.4,1]},"
    js.write_text(js.read_text('utf8').replace("court:{label:'庭院关系'",presets+"court:{label:'庭院关系'"),'utf8')
    html=OUT/'index.html'
    html.write_text(html.read_text('utf8').replace('细节补全 T3','岩坪衔接 T3'),'utf8')
    for source in [Path(__file__),Path(ground.__file__),Path(ground.landscape.__file__)]:
        shutil.copy2(source,OUT/'生成脚本'/source.name)


if __name__=='__main__':
    main()
