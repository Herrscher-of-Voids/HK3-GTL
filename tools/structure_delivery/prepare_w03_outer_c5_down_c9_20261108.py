# -*- coding: utf-8 -*-
"""复用已核验的C6/C8矩阵播放器，接入C9纯数据修改与连续净空证据。"""
import re
from pathlib import Path
from build_w03_outer_c5_down_c9_20261108 import ROOT, OUT, LOG, load, save, unpack, pack


def main():
    scripts=ROOT/'tools/structure_delivery'
    replacements={
        'W03_C8_去星冠光柱与外伸节点_20261108':OUT.name,
        'w03-trim-c8-20261108':LOG.name,
        'w03_trim_c8_20261108':'w03_outer_c5_down_c9_20261108',
        'C8_READY':'C9_READY',
    }
    for prefix in ['', 'bundle_', 'capture_']:
        text=(scripts/f'{prefix}w03_trim_c8_20261108.mjs').read_text('utf8')
        for a,b in replacements.items():text=text.replace(a,b)
        if prefix=='':
            text=text.replace('C8：指定删除后沿用C6独立运动矩阵。','C9：外环与外星阵自法向旋转，内四环沿用C6立体翻转。')
            text=text.replace('base_geometry_sha256_unchanged:true','c6_component_shapes_preserved:true')
            text=text.replace('五环立体翻转 · 星阵／核心／六矛／晶体全动','外环自转 · 内四环立体翻转 · 晶体与六矛下移')
            text=re.sub(r"note.textContent = '[^']*';", "note.textContent = 'C9：外环与外24星保持环面自转；内四环、核心继续立体翻转。9颗晶体按净空下移，六矛轴向下移后仍指向核心；连续包络核验通过，未部署。';",text)
            text=re.sub(r"document.querySelector\('header > div'\).textContent = '[^']*';", "document.querySelector('header > div').textContent = 'C6衍生候选 · 833×833×636 · 6,642,464方块 · 14材质 · 连续净空通过／游戏未验';",text)
        if prefix=='capture_':
            text=text.replace("check(spatial.normals.every(n=>n.absolute_dot<.995),'环面法向没有实际改变，仍是平面旋转');", "check(spatial.normals[0].absolute_dot>1-1e-9 && spatial.normals.slice(1).every(n=>n.absolute_dot<.995),'外环未保持朝向，或内四环失去立体翻转');")
            text=text.replace('multi_axis_normals_change:true','outer_normal_fixed_inner_four_normals_change:true')
            text=text.replace('i*2);','i*360/32);')
            text=text.replace('后侧去外伸节点.png','后侧净空.png').replace('侧面去外伸节点.png','侧面净空.png')
        if prefix=='bundle_':text=text.replace('C6动态脚本已打包','C9动态脚本已打包')
        (scripts/f'{prefix}w03_outer_c5_down_c9_20261108.mjs').write_text(text,'utf8')
    proof=load(LOG/'continuous-clearance.json')
    config=unpack(OUT/'w03/motion-data.js')
    if 'conservative_shell_overlaps' in config:
        config['historical_c6_conservative_shell_overlaps']=config.pop('conservative_shell_overlaps')
    config['continuous_c9_clearance']=dict(passed=True,pair_count=528,minimum_gap=proof['global_surface_clearance_lower_bound'])
    pack(OUT/'w03/motion-data.js','W03_MOTION',config)
    p=unpack(OUT/'w03/data.js')
    p['audit']=load(OUT/'verification.json')
    p['data']=load(OUT/'manifest.json')
    # C4静态间距留作来源，不冒充C9运动净空。
    for data in [p['data'],load(OUT/'manifest.json')]:
        clearance=data['clearance']
        clearance['historical_c4_static_clearance']={k:clearance.pop(k) for k in ['after','intersection_pairs_after','min_nonconnection_distance','gap_rule','part_count'] if k in clearance}
        clearance['continuous_c9']=dict(passed=True,minimum_surface_gap_lower_bound=proof['global_surface_clearance_lower_bound'],proof='logs/w03-c5-outer-down-c9-20261108/continuous-clearance.json')
        if data is not p['data']:save(OUT/'manifest.json',data)
    pack(OUT/'w03/data.js','HK3_PAYLOAD',p)
    page=(OUT/'w03/三维评审.html').read_text('utf8')
    page=re.sub(r'<title>.*?</title>','<title>穹界·虚数锚定环 · C9 外环自转与下移净空</title>',page)
    page=page.replace('C9C5','C9 · C5').replace('15种材料','14种材料')
    m=p['data'];controller=m['controller']
    page=page.replace('主控蓝图 [288, 27, 35]',f'主控导出坐标 {controller}')
    page=page.replace('整宽第289格',f'整宽第{controller[0]+1}格')
    (OUT/'w03/三维评审.html').write_text(page,'utf8')
    index=(OUT/'index.html').read_text('utf8')
    index=index.replace('24颗浓缩崩坏能晶体下移至第四层环的动态范围之外','24颗浓缩崩坏能晶体保留立体分布，其中9颗按运动净空下移')
    index=index.replace('当前只证明位移和归属，完整动态净空、游戏成型与性能仍待验收。','连续运动包络已核验528对构件关系，动态构件间净空下界6.07格，连同静态建筑的净空下界2.27格。游戏内运动、GT成型与3.5客户端性能尚未验收。')
    index=index.replace('<iframe src=', '<p><a href="../../logs/w03-c5-outer-down-c9-20261108/continuous-clearance.json">连续净空证明</a> · <a href="下移与转动演示.webp">完整运动周期演示</a></p><img src="初始全景.png" alt="C9初始全景"><iframe src=')
    index=index.replace('静态结构与当前增强版3.5材质同步更新','实际完整尺寸833×833×636；6,642,464方块、14材质。完整结构与当前增强版3.5材质同步更新')
    (OUT/'index.html').write_text(index,'utf8')
    print('C9 renderer, bundle, capture and proof-linked preview prepared')


if __name__=='__main__':main()
