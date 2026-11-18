# -*- coding: utf-8 -*-
"""W05真实方块静态候选打包，沿用现有三维评审界面。"""
import base64
import gzip
import json
import re
import shutil
from html import escape
from pathlib import Path

import numpy as np
import w05_wind_circuit_a1_20261112 as g
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def viewer(scripts):
    original = g.ROOT / 'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110/生成脚本/viewer.mjs'
    source = original.read_text('utf-8').replace('W04', 'W05')
    source = source.replace("import * as THREE from 'three';", "import * as THREE from 'three';\nimport {attachReviewControls} from './w05-review-ui.mjs';")
    source = source.replace("renderer.setClearColor('#18101c')", "renderer.setClearColor('#0d1919')")
    source = source.replace("if(name==='orthofront'||name==='dragonfront')", "if(name==='orthofront')")
    source = source.replace("    if(name==='dragonside')direction.set(1,0,0);\n", '')
    source = source.replace('window.W05Static={config,scene,camera,renderer,controls,groups,setView,', 'window.W05Static={config,scene,camera,renderer,controls,groups,setView,draw,')
    source = source.replace('  window.W05_STATIC_READY=true;', '  attachReviewControls(window.W05Static);\n  window.__hk3Preview=window.W05Static;window.__hk3Preview.ready=true;\n  window.W05_STATIC_READY=true;')
    (scripts / 'viewer.mjs').write_text(source, encoding='utf-8')
    shutil.copy2(Path(__file__).with_name('w05_wind_circuit_review_ui_20261112.mjs'), scripts / 'w05-review-ui.mjs')


def review_page(data, parts, bom):
    w, h, d = data['size']
    template = (g.ROOT / 'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110/w04/三维评审.html').read_text('utf-8')
    style = re.search(r'<style>(.*?)</style>', template, re.S).group(1).replace('#C93F63', '#48C9A3').replace('#0b1624', '#0b1819').replace('#102238', '#102b2a')
    material_rows = ''.join(f'<label data-material-row><input type="checkbox" checked data-material="{i}"><code>{escape(row["state"])}</code><small>{row["count"]:,}块 · {escape(row["role"])}</small></label>' for i, row in enumerate(bom))
    part_rows = ''.join(f'<label><input type="checkbox" checked data-part="{escape(p.name)}">{escape(p.name)}</label>' for p in parts)
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W05 · 长风·理想流体环流阵 · A1</title>
<style>{style}a{{color:#8de1ca}}code{{overflow-wrap:anywhere;font-size:11px}}small{{display:block;color:#a8c9c5}}input[type=search]{{width:100%;margin:8px 0;padding:8px;background:#112a2a;border:1px solid #4d7870;color:inherit}}[data-material-row]{{margin:9px 0}}[hidden]{{display:none!important}}.control-row{{display:flex;flex-wrap:wrap}}header span{{color:#b6d5cd}}</style>
<header><a href="index.html">← W05方案与状态</a><h1>风之律者 · 长风·理想流体环流阵</h1><span>A1 · 双层闭合回流 · 完整{w}×{d}×{h}（宽深高）</span></header>
<main><section id="stage"><div id="loading">准备完整静态构件…</div><div id="legend">HDV 风息绿 #48C9A3 · 运行目标 WSV · 原创工业风洞</div></section>
<aside><p class="note">{escape(data['summary'])}</p><div class="control-row"><button data-view="front">前左全景</button><button data-view="orthofront">正面</button><button data-view="side">侧面</button><button data-view="back">背面</button><button data-view="top">俯视</button><button data-view="low">仰视</button><button data-view="core">整流核心</button><button data-view="controller">主控接口</button></div>
<div class="control-row"><button id="reset">重置视角</button><button id="screenshot">保存截图</button><button id="fullscreen">全屏</button></div>
<label><input id="glass" type="checkbox" checked>显示玻璃</label><label><input id="grid" type="checkbox">参考网格（约16格）</label><label><input id="ports" type="checkbox">标出主控</label>
<label>剖切高度 <output id="layerLabel">{h-1}</output><input id="layer" type="range" min="0" max="{h-1}" value="{h-1}"></label><p id="stats"></p>
<details open><summary>材料搜索与显隐 · 正式导出数量</summary><input id="materialSearch" type="search" placeholder="方块ID或用途">{material_rows}</details>
<details open><summary>独立构件</summary>{part_rows}</details>
<p class="note">主控红石块是未注册控制器的明确占位；玩家可自行选择实体建筑位置替换通用接口。此为静态外观候选，未批准、未安装，未验证成型或运行。</p>
<p>全部按真实方块及整数坐标展示。没有动画，只有镜头或控件改变时重绘；材料纹理复用仓库既有真实缓存。</p><p><a href="verification.json">离线导出核验</a> · <a href="manifest.json">完整坐标与状态</a> · <a href="材料清单.json">完整材料表</a></p></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''


def overview(data, count, parts):
    w, h, d = data['size']
    gallery = ''.join(f'<figure><img src="{file}" alt="{label}" loading="lazy"><figcaption>{label}</figcaption></figure>' for file, label in [('正面.png', '正面：双层流道与中央整流岛'), ('侧面.png', '侧面：高低流道及回流区'), ('背面.png', '背面：回流泵阵与检修结构'), ('俯视.png', '俯视：完整闭合回路'), ('核心近景.png', '整流核心与换热结构'), ('主控接口.png', '嵌墙主控占位')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W05 · 长风·理想流体环流阵 · A1</title>
<style>:root{{color-scheme:dark}}body{{max-width:1500px;margin:28px auto;padding:0 24px;background:#0c191a;color:#e2f2ee;font:16px/1.85 system-ui}}a{{color:#83dbc4}}h1{{font-size:34px}}img{{width:100%;display:block}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0}}figcaption{{padding:8px 0}}.note{{border-left:4px solid #48C9A3;padding:14px 18px;background:#142b28}}code{{overflow-wrap:anywhere}}@media(max-width:800px){{.grid{{display:block}}}}</style>
<p>W05 · 风之律者 · 首版静态候选</p><h1>长风·理想流体环流阵<br>双层闭合回流 · A1</h1><p class="note">{escape(data['summary'])}</p>
<p><a href="三维评审.html">打开完整三维评审</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p><p>宽{w} × 深{d} × 高{h} · {count:,}真实方块 · {len(parts)}构件 · 全静态</p><img src="完整预览.png" alt="W05双层回流阵前左全景">
<p>进流调理 → 双环流道 → 中央整流 → 分流端 → 回流泵阵。高低流道围绕中央设备形成完整回路，宽阔承托、检修桥和泵组共同表达极端流体输运与大规模换热职责。</p>
<p>HDV风息绿 <code>#48C9A3</code>承担律者颜色身份，白色装甲、黑色承托和金属设备提供层次；运行目标仍为WSV，外观色板不改机器运行电压。</p><div class="grid">{gallery}</div>
<p class="note">本项目原创工业风洞视觉，不宣称温蒂官方机械或模型复刻。名义尺寸不作为裁切窗口，完整生成后计算实际边界；7幅离线截图不能替代游戏测试。</p>
<p>W05控制器尚未注册：红石块标明主控候选位置，实体建筑位置由玩家自行选择通用接口。此包不授予研究、二审或毕业资格，未批准、未安装、未验证搭建成型与运行，正式配方和产物另定。</p>
<p>研究职责沿RN-IFF：可追溯真实输入输出、循环补液与换热结果，明确损耗；首机不用W05自产介质，不把理想流体解释为流体复制或零成本能源。</p>
<p>参考依据：<a href="../../doc/HK3GTL-内测5/03_机器结构/机器与文明级奇观.html">既定工序分区</a> · <a href="../已完成多方块_电压与配色逐台核对_20261029/index.html#wonder-palette">律者颜色身份</a>。建筑形体为本项目原创转译，非官方场景。</p>
<p><a href="manifest.json">构件、坐标与状态</a> · <a href="verification.json">离线核验</a> · <a href="材料清单.json">材料表</a> · <a href="w05/{data['name']}.nbt">完整NBT</a> · <a href="w05/{data['name']}.schem">完整Schematic</a></p></html>'''


def main():
    g.OUT.mkdir(parents=True, exist_ok=True)
    g.LOG.mkdir(parents=True, exist_ok=True)
    view = g.OUT / 'w05'
    view.mkdir(exist_ok=True)
    scripts = g.OUT / '生成脚本'
    scripts.mkdir(exist_ok=True)
    cube, data, parts = g.build()
    cache = json.loads((g.ROOT / 'logs/w05-wind-circuit-a1-20261112/material-cache.json').read_text('utf-8'))
    by_state = {m['state']: m for m in cache['materials']}
    materials = [by_state[state] for state in g.STATES]
    exported = export_dense(cube, g.STATES, data['name'], view)
    surfaces = exported.pop('surface_groups')
    offset = np.asarray(data['blueprint_to_export_offset_xyz'])
    owner = np.zeros_like(cube)
    for i, p in enumerate(parts, 1):
        at = p.p + offset
        owner[at[:, 1], at[:, 2], at[:, 0]] = i
    flat_owner = owner.ravel()
    owned_counts = np.bincount(flat_owner, minlength=len(parts)+1)
    _, depth, width = cube.shape
    previews, proofs = [], []
    for i, p in enumerate(parts, 1):
        low, high = p.p.min(0), p.p.max(0)
        size = high - low + 1
        origin = low + offset
        local_groups = []
        for material in surfaces:
            local_faces = []
            for face in material:
                indices = np.asarray(face, dtype=np.int64)
                indices = indices[flat_owner[indices] == i]
                local = ((indices // (width*depth) - origin[1]) * size[2]
                         + indices // width % depth - origin[2]) * size[0] + indices % width - origin[0]
                local_faces.append(local.tolist())
            local_groups.append(local_faces)
        groups, lengths, proof = merge_surface_runs(local_groups, size.tolist())
        previews.append(dict(id=p.name, origin=origin.tolist(), size=size.tolist(), starts=groups, lengths=lengths,
                             blocks=int(owned_counts[i]), source_blocks=len(p.p)))
        proofs.append(dict(component=p.name, **proof))
    count = exported['block_count']
    quads = sum(p['rendered_quads'] for p in proofs)
    whole_surface_faces = sum(len(face) for material in surfaces for face in material)
    assert sum(p['original_unit_faces'] for p in proofs) == whole_surface_faces
    data.update(machine_id='W05', blocks=count, animation_enabled=False, approved=False, installed=False, game_verified=False,
                controller_registered=False, controller_placeholder='minecraft:redstone_block', runtime_voltage='WSV')
    audit = dict(passed=exported['readback']['passed'], readback=exported['readback'], hashes=exported['hashes'],
                 viewer_rendered_quads=quads, surface_merge=proofs, animation_enabled=False, game_verified=False,
                 surface_scope='完整导出最终方块的外露面；隐藏构件不补内部表面',
                 whole_surface_faces=whole_surface_faces, surface_ownership_partition_equal=True,
                 no_nominal_clipping=True, material_resource_sources={s: cache['sources'][s] for s in g.STATES},
                 controller_registered=False, controller_marker_only=True, interface_count=len(data['ports']))
    payload = dict(data=data, audit=audit, materials=materials, parts=previews)
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    (g.OUT / 'data.js').write_text('window.W05_STATIC_PAYLOAD=' + json.dumps(base64.b64encode(compressed).decode()) + ';', encoding='utf-8')
    counts = np.bincount(cube.ravel(), minlength=len(g.STATES)+1)
    bom = [dict(state=s, count=int(counts[i+1]), role=g.ROLES[s]) for i, s in enumerate(g.STATES)]
    save(g.OUT / 'manifest.json', data)
    save(g.OUT / 'verification.json', audit)
    save(g.OUT / '材料清单.json', bom)
    np.savez_compressed(g.LOG / 'components.npz', **{p.name+'__'+key: value for p in parts for key, value in [('p', p.p), ('states', p.states)]})
    viewer(scripts)
    (g.OUT / '三维评审.html').write_text(review_page(data, parts, bom), encoding='utf-8')
    (g.OUT / 'index.html').write_text(overview(data, count, parts), encoding='utf-8')
    for source in [Path(__file__), Path(g.__file__)]:
        shutil.copy2(source, scripts / source.name)
    print(json.dumps(dict(passed=audit['passed'], size=data['size'], blocks=count, quads=quads), ensure_ascii=False))


if __name__ == '__main__':
    main()
