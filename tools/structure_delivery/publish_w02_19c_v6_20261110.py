# -*- coding: utf-8 -*-
"""发布恢复背部与节链的V6，分数与其他构件保持。"""
from pathlib import Path
import shutil
import w02_19c_geometry_v6_20261110 as geometry
from publish_w02_19c_v4_20261110 import main


if __name__=='__main__':
    main(geometry)
    shutil.copy2(__file__,geometry.OUT/'生成脚本'/Path(__file__).name)
