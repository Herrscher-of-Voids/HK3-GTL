# -*- coding: utf-8 -*-
from pathlib import Path
import re
import shutil

import package_senti_weapons_20261116 as package
import senti_case_s2_20261116 as case
import senti_chain_s2_20261116 as chain
import senti_sword_spear_s2_20261116 as blades
import senti_weapon_viewer_20261116 as viewer

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_识律武器细节复刻_S2_20261116'
REF = ROOT / 'deliveries/0005_W09_识律武器补充参考_R2_20261116'


def main():
    package.OUT, package.REF, package.VERSION = OUT, REF, 'S2'
    package.METHOD = '依据官方公开MMD的正、背、侧观察截图逐格重建轮廓、色区和截面，使用原生方块纹理；四件按约25.2格/MMD单位保持默认静态相对比例。'
    package.case, package.blades, package.chain = case, blades, chain
    package.STATES += ['minecraft:gray_concrete', 'minecraft:blue_terracotta']
    package.LABELS += ['灰黑刃片', '灰紫壳体']
    models = case.build() + blades.build() + chain.build()
    for model in models:
        model['references'] = [ref.replace('R2-M-', 'MMD-') for ref in model['references']
            if not re.fullmatch(r'R\d+', ref)]
    package.main(models)
    viewer.OUT = OUT
    viewer.HTML = viewer.HTML.replace('S1', 'S2').replace(
        '0005_W09_识律武器多角度参考_20261116', REF.name).replace(
        '完整整数格实体 · 原生像素材质 ·', '官方公开模型正背侧细节依据 · 完整整数格实体 ·')
    viewer.main()
    for name in ['senti_sword_spear_20261116.py', 'senti_weapon_viewer_20261116.py',
            'package_senti_weapons_20261116.py', Path(__file__).name]:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)


if __name__ == '__main__':
    main()
