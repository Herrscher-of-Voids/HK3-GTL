# -*- coding: utf-8 -*-
"""导出恢复背部与节链的V6静态候选及V5对照。"""
from pathlib import Path
import shutil
import w02_19c_geometry_v6_20261110 as geometry
import package_w02_19c_v3_20261110 as package


if __name__=='__main__':
    package.main(geometry)
    shutil.copy2(__file__,geometry.OUT/'生成脚本'/Path(__file__).name)
