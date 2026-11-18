from pathlib import Path
import json
import shutil

import package_taixuan_model_20261116 as package
import taixuan_architecture_r2_20261116 as architecture
import taixuan_detail_r2_20261116 as detail
import taixuan_viewer_20261116 as viewer


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/0005_W09_太虚山细节补全_T2_20261116'
REF=ROOT/'deliveries/0005_W09_太虚山多角度参考_R2_20261116'


def main(revision='T2'):
    package.OUT,package.REF=OUT,REF
    package.architecture=architecture
    original=package.landscape.build
    package.landscape.build=lambda:original()+detail.build()
    package.main(revision)
    viewer.OUT,viewer.REF=OUT,REF
    viewer.main()
    count=json.loads((REF/'参考清单.json').read_text('utf8'))['count']
    html=(OUT/'index.html').read_text('utf8').replace('独立复刻 T1','细节补全 '+revision).replace('-T1.nbt',f'-{revision}.nbt').replace('31幅参考',f'{count}幅参考')
    (OUT/'index.html').write_text(html,'utf8')
    js=OUT/'生成脚本/viewer.mjs'
    source=js.read_text('utf8').replace('-T1.png',f'-{revision}.png')
    source=source.replace("activeModel==='all'?{...basicViews,", "activeModel==='all'?{...basicViews,bridge:modelById.get('mountain_path').views.bridge,gate_detail:modelById.get('gallery').views.gate_detail,")
    js.write_text(source,'utf8')
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['revision']=revision
    manifest['previous_candidate']='../0005_W09_太虚山方块复刻_T1_20261116/index.html'
    manifest['detail_changes']=['按日景正侧面补窗棂回纹、门扇折线和双框菱形金饰。','补檐下回纹横楣、墙下白色腰带与灰石柱础。','屋瓦纵条统一青灰，曲脊用原有墨色构架。','观东水道加入起拱石桥、低实栏和方形栏柱；桥位与拱腹为项目补建。','依竹林石阶图补分节细竹、偏侧叶簇及阶边苔色；竹丛坐标沿现有山径补建。']
    manifest['detail_changes'].append('依R2O11补四柱三间牌楼、高中檐低侧檐及短椽；庭院入口坐标与背面为补建。')
    manifest['detail_changes'].append('依R2O15补香炉深色竖腹带，塔窗改为斜交木棂。')
    manifest['detail_changes'].append('依R2O13将小石灯灯帽、短塔尖与灯座统一暗灰，补斜格灯室。')
    manifest['detail_changes'].append('桥东端补接岸岩台和沿溪石路，桥两端加踏步；局部溪岸及桥头属于项目补建。')
    package.save(OUT/'manifest.json',manifest)
    for source in [Path(__file__),Path(detail.__file__),Path(viewer.__file__)]:
        shutil.copy2(source,OUT/'生成脚本'/source.name)


if __name__=='__main__':
    main()
