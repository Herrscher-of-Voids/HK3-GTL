# -*- coding: utf-8 -*-
"""生成第四台MAX精密重构机独立候选，不修改前三台或游戏实例。"""
from build_max_structure_candidate import ROOT,generate
import mx_c04_reconstructor_geometry_v1_20261107 as geometry

if __name__=='__main__':
    generate(geometry,ROOT/'deliveries/MAX复制系统_重构机_四臂重构工坊_V1_20261107',
             ROOT/'logs/mx-c04-reconstructor-v1-20261107',__file__)
