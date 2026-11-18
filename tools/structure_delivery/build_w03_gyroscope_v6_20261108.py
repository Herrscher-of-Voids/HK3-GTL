# -*- coding: utf-8 -*-
"""Claude八锚穹仪原案独立候选；坐标冲突保留，不静默裁边。"""
import hashlib,json,shutil
from pathlib import Path
import w03_gyroscope_geometry_v6_20261108 as geometry
from build_max_structure_candidate import generate,save
from build_wonder_boundary_repairs_20261108 import preview_page

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W03_穹界虚数锚定环_八锚穹仪_Claude原案_V6_20261108'
LOG=ROOT/'logs/w03-gyroscope-v6-20261108'
SOURCE=Path('C:/Users/OWNER/下載/空之律者·穹界·虚数锚定环 设计文档.md')


def main():
    generate(geometry,OUT,LOG,__file__)
    m=json.loads((OUT/'manifest.json').read_text('utf8'));v=json.loads((OUT/'verification.json').read_text('utf8'))
    m.update(candidate_version='V6',target_voltage='CIV',appearance_voltage='自由美观选材／紫黑暗金',generated_at='2026-11-08',
        source_author='Claude Opus 5.5（负责人转交署名）',source_document_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        claim_boundary='按原稿坐标转译静态实体；原有相交和超高保留。B1–B10专用方块及所有游戏动态效果尚未实装。')
    save(OUT/'manifest.json',m)
    description='Claude原案独立V6：十二级椭圆基台、八塔十六链、Y166水平主环与24扇菱形门、正交双纵环、六向支撑核心及Y230光环。保持作者坐标，名义673×529×321不作裁切窗；完整实体实为673×529×322。'
    preview_page(OUT,m,v,description)
    p=OUT/'index.html';s=p.read_text('utf8');s=s.replace('<p>保留原案的相交',
        '<p><a href="../W03_完整几何边界修复_20261108/index.html">W03旧候选完整边界修复与对照</a> · <a href="原稿.txt">负责人提供的Claude原稿</a> · <a href="原案转译记录.json">原案与实现边界</a></p><p>保留原案的相交')
    p.write_text(s,'utf8');shutil.copy2(SOURCE,OUT/'原稿.txt')
    save(OUT/'原案转译记录.json',dict(source_document=str(SOURCE),source_sha256=m['source_document_sha256'],
        geometry_preserved=['P1的12级、半轴336−4k／264−4k与Y23顶面',
            '八塔中心按275／205椭圆45度递增取整，Y24～260；16条链连Y230到Y182',
            '主环半轴230／170、Y166、33×33削角截面、72竖肋、内部9×9线圈、24个7.5+15n度菱形门',
            '双纵环中心[336,166,264]、半径148、13×13与每10度15×15金箍；两处25立方接合舱',
            '半径20正八面体核心、六根5×5梁、半径40的Y230光环与24根9格斜刺',
            '南向控制器[336,30,484]、61×41尖拱门、两侧7×7×35方尖碑'],
        conflicts_preserved=v['source_conflicts_preserved'],
        material_substitution=geometry.ROLES,not_implemented=v['not_verified'],
        engineering_notes='原稿的50万～80万块只是估算，实际以本版逐格统计为准。any()不等于免扫描、稀疏／分tick／局部重验与隐藏实体改BER均未接入游戏；未按原文假定现有框架已提供。',
        latest_owner_override='接口全部通用；尺寸不是裁切窗；原作者冲突不自行修正。'))
    for p in [ROOT/'tools/structure_delivery/build_wonder_boundary_repairs_20261108.py',ROOT/'tools/structure_delivery/audit_wonder_clipping_20261108.py']:
        shutil.copy2(p,OUT/'生成脚本'/p.name)


if __name__=='__main__':main()
