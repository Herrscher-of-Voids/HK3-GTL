# -*- coding: utf-8 -*-
"""生成第三台MAX的图谱存储阵列候选，不改前两台或实例。"""
from build_max_structure_candidate import ROOT,generate
import mx_c03_atlas_geometry_v1_20261107 as geometry

if __name__=='__main__':
    generate(geometry,ROOT/'deliveries/MAX复制系统_图谱阵列_双翼图谱库_V1_20261107',
             ROOT/'logs/mx-c03-atlas-v1-20261107',__file__)
