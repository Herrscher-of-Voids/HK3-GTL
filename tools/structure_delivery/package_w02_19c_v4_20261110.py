# -*- coding: utf-8 -*-
"""导出V4机甲兽候选与V3对照。"""
from pathlib import Path
import shutil
import w02_19c_geometry_v4_20261110 as geometry
import package_w02_19c_v3_20261110 as package


if __name__=='__main__':
    package.main(geometry)
    shutil.copy2(__file__,geometry.OUT/'生成脚本'/Path(__file__).name)
