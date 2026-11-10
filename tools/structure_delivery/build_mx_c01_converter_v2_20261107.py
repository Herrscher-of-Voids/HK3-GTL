# -*- coding: utf-8 -*-
"""复用V1导出器生成独立V2，保留原候选及其交付包。"""
import json
from pathlib import Path
import shutil

import build_mx_c01_converter_v1_20261107 as previous
import mx_c01_converter_geometry_v2_20261107 as geometry


def main():
    previous.geometry = geometry
    previous.OUT = previous.ROOT/'deliveries/MAX复制系统_供料机_双罐脉冲转化厂_V2_20261107'
    previous.LOG = previous.ROOT/'logs/mx-c01-converter-v2-20261107'
    original_page = previous.page
    previous.page = lambda data,check: original_page(data,check).replace('转化厂 V1','转化厂 V2')
    previous.main()
    manifest_path = previous.OUT/'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest.update(candidate_version='V2',changes='双罐正面立管延伸并接回循环泵；新增逐管末端及泵罐路径检查。')
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for script in [Path(__file__),previous.ROOT/'tools/structure_delivery/mx_c01_converter_geometry_v1_20261107.py']:
        shutil.copy2(script,previous.OUT/'生成脚本'/script.name)


if __name__ == '__main__':
    main()
