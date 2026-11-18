# -*- coding: utf-8 -*-
"""Gork四锚穹盖独立V7，沿用已有逐格导出与完整真实材质预览。"""
import json,shutil
from pathlib import Path
import w03_gork_geometry_v7_20261108 as geometry
from build_max_structure_candidate import generate,save
from build_wonder_boundary_repairs_20261108 import preview_page

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W03_穹界虚数锚定环_四锚穹盖_Gork原案_V7_20261108'
LOG=ROOT/'logs/w03-gork-v7-20261108'
V6='W03_穹界虚数锚定环_八锚穹仪_Claude原案_V6_20261108'


def main():
    generate(geometry,OUT,LOG,__file__)
    m=json.loads((OUT/'manifest.json').read_text('utf8'));v=json.loads((OUT/'verification.json').read_text('utf8'))
    m.update(candidate_version='V7',target_voltage='CIV',appearance_voltage='自由美观选材／深空黑与虚空紫',generated_at='2026-11-08',
        source_author='Gork（负责人本轮转交署名）',claim_boundary='原文近似尺寸的独立几何转译，具体标高和细节见记录。能流与旋转仅为可关闭的浏览器概念演示，未部署游戏。')
    save(OUT/'manifest.json',m)
    description='Gork原案独立V7：600×480椭圆主环、四向250格工形锚桩、280格断续蜂窝中轴与奇点薄环；四层辅助环和破损浅穹盖覆盖35格基础与观测防护壁。名义673×529×321作为最低参考，完整构件决定实际尺寸。'
    preview_page(OUT,m,v,description)
    p=OUT/'w03/三维评审.html';s=p.read_text('utf8')
    s=s.replace('<div id="viewName">','<label><input id="energyPreview" type="checkbox">播放能流、星空与光环（概念预览）</label><p id="energyState">静态完整实体；蓝图与导出文件保持原始姿态。</p><button id="coreView">能量与核心近景</button><div id="viewName">',1)
    s=s.replace('</body>','')
    s+='<script src="gork-review.bundle.js"></script>'
    s=s.replace('各路管道均核对指定两端设备；这不代表流体运行能力。','16条能量导管核对四节点与中轴的实际连接，均为外观构件，不宣称有流体运行能力。')
    p.write_text(s,'utf8')
    shutil.copy2(ROOT/'deliveries'/V6/'完整预览.png',OUT/'V6对照.png')
    interpretations=[
        '原文未给逐格坐标。中点沿用[336,166,264]；主环基准Y166并以7格正弦加3格二次谐波起伏。',
        '外椭圆600×480，内椭圆480×360；“外径600、内径480”按长轴解读，保留约60格管宽，不把椭圆改圆。',
        '中轴从Y35到314共280层；约40格黑柱外包12格晶格。核心中心Y166，三层薄环半径34／40／45。',
        '四锚桩轴心位于主环椭圆中线四极，Y35～284共250层；上下锚盘直径约100，四节点直径约80。',
        '四个辅助环半径150／200／200／150，基准Y86／120／220／255，保留上下各两层；“高度比主环低”解读为截面低于40格，不把上方辅助环移到下方。',
        '浅穹盖以Y315～355曲面为基准，两格薄板含上层；分12片并留中央孔和宽角隙，32条垂索接主环与轴。',
        '35格基础的椭圆半轴336／276，平台边缘自然超过主环；高35格观测防护壁。实际边界由实体测得，不按673×529×321裁切。',
        '球、圆盘的“约直径”采用方块中心取样，端点包含导致部分轴向实体跨度多一格；没有为了凑整数削边。',
        '原文的虚空腔体不在本轮修改世界地形；静态材质为已有真实方块代理，未注册虚空合金或星核材料。']
    save(OUT/'原案要点与转译.json',dict(source='负责人2026-11-08本轮提供的Gork文字原案',source_author='Gork（沿用负责人拼写）',
        original_major_dimensions=dict(minimum_wdh=[673,529,321],main_ellipse_axes=[600,480],main_inner_major=480,main_width=[50,60],main_height=40,
          axis_height=280,axis_diameter=40,lattice_thickness=12,core_diameter=90,conduit_diameter=[8,10],anchor_height=250,anchor_discs=100,
          auxiliary_diameters=[400,300],dome_height=[30,40],foundation_height=[30,40]),
        interpretations=interpretations,materials=geometry.ROLES,not_verified=v['not_verified'],
        preview_effects='所有导槽／管路／桥梁／垂索的能流路径均有移动光点；奇点三层薄环用独立材质暂隐后显示旋转线环；穹盖间隙另有480个闪烁星点和3个旋转浮游光环。关闭、剖切或材质筛选时恢复原静态实体。此效果不写入NBT／Schem，也不等于游戏BER实装。'))
    w,h,d=m['size']
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 · 四锚穹盖 · Gork V7</title>
<style>body{{max-width:1500px;margin:30px auto;padding:0 22px;background:#14111e;color:#eee5f7;font:16px/1.8 system-ui}}a{{color:#dbb2ff}}img{{width:100%;display:block}}.note{{padding:18px;border-left:3px solid #9c75cb;background:#2b2239}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}figure{{margin:0}}@media(max-width:850px){{.grid{{display:block}}}}</style>
<small>HK3GTL / W03西琳 / Gork原案 V7 / 2026-11-08</small><h1>穹界·虚数锚定环 · 四锚穹盖</h1>
<p class="note">{w}×{d}×{h}（宽×深×高） · {v['blocks']:,}实体方块 · {v['unique_materials']}种方块状态。保留V1～V6及完整边界修复，等待负责人选型；未批准、未部署。</p>
<p><a href="w03/三维评审.html">打开完整三维与能流演示</a> · <a href="原案要点与转译.json">原案参数与转译</a> · <a href="材料清单.json">材料用量</a> · <a href="verification.json">逐格与边界核验</a></p>
<img src="完整预览.png" alt="四锚、波浪主环、晶格中轴与破损穹顶完整实体"><p>{m['description']}</p>
<div class="grid"><figure><img src="能量演示.png" alt="核心近景与移动能流概念演示"><figcaption>可开关的浏览器概念演示：导槽和连接构件上的光点流动，奇点薄环旋转。静态实体默认完整显示；游戏效果未实装。</figcaption></figure><figure><img src="俯视布局.png" alt="十二片破损穹盖与环系布局"><figcaption>十二片浅弧形晶格板留宽角隙，32根悬索分别接环与中轴。</figcaption></figure><figure><img src="逐层剖切.png" alt="实际实体的逐层剖切"><figcaption>四层辅助环及上下四圈奇点汇聚导管；剖切只隐藏实际外表面，不补画切面。</figcaption></figure><figure><img src="主控材质近景.png" alt="南壁连续设备湾主控与通用接口"><figcaption>南壁设备湾八舱位与四节点各两舱位全通用，不限制输入输出。</figcaption></figure></div>
<p class="note">673×529×321为原文最低参考，完整边界由真实构件测得；不挪动、压扁或裁掉越界构件。该文未固定坐标，具体标高、辅助环层次、椭圆内径及薄板分片的转译均已列明。W01–W15以美观选材。</p>
<h2>与Claude V6分别保留</h2><div class="grid"><figure><a href="../{V6}/index.html"><img src="V6对照.png" alt="Claude V6八锚穹仪">V6 · 八锚穹仪</a></figure><figure><img src="完整预览.png" alt="Gork V7四锚穹盖">V7 · 四锚穹盖</figure></div>
<p><a href="../W03_完整几何边界修复_20261108/index.html">V2／V3／V4／V5完整边界修复与对照</a></p><p>完整NBT／Schematic逐格回读、表面合并重展、接口净空和16条能量管接续均离线核验。能流为预览叠加层，不改变导出方块。正式Pattern、工艺、研究、实体角色、游戏演出及8GB工况仍待验收。</p>
<p>既定74项、批准57／正式52、batch-12为0/5与系统分数保持；十周年派对预案及西瓜ARG原案保留。</p></html>''','utf8')
    for p in [ROOT/'tools/structure_delivery/build_wonder_boundary_repairs_20261108.py',ROOT/'tools/structure_delivery/audit_wonder_clipping_20261108.py',ROOT/'tools/structure_delivery/w03_gork_review_v7_20261108.mjs',ROOT/'tools/structure_delivery/build_w03_gork_preview_v7_20261108.mjs']:
        shutil.copy2(p,OUT/'生成脚本'/p.name)


if __name__=='__main__':main()
