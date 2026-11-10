# -*- coding: utf-8 -*-
"""Build a fresh I37 block candidate with real instance textures and HTML review."""
from __future__ import annotations

import base64
import datetime as dt
import gzip
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
import i37_dual_field_range_geometry_20261028 as geometry
from i37_dual_field_range_audit_20261028 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

OUT = ROOT / 'deliveries/I37_世界维系试验平台_双腔差分场试验场_白纸重设计_20261028'
VIEW = OUT / 'i37'
LOG = ROOT / 'logs/i37-dual-field-range-20261028'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def page(data, check):
    rows = ''.join(
        f'<tr><td>{label}</td><td>{check["voltage_comparison"]["metrics"][key]:,}</td>'
        f'<td>{limit:,}</td><td>+{check["voltage_comparison"]["metrics"][key] - limit:,}</td></tr>'
        for key, label, limit in (
            ('blocks', '实际实体方块', check['voltage_comparison']['lower_voltage_maxima']['blocks']),
            ('materials', '实际材质种类', check['voltage_comparison']['lower_voltage_maxima']['materials']),
            ('volume', '实体包围盒体积', check['voltage_comparison']['lower_voltage_maxima']['volume']),
            ('height', '实体高度', check['voltage_comparison']['lower_voltage_maxima']['height']),
        ))
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I37 世界维系试验平台 · 双腔差分场试验场</title>
<style>body{{max-width:1360px;margin:30px auto;padding:0 20px;background:#121a25;color:#e8edf1;font:16px/1.75 system-ui,"Microsoft YaHei",sans-serif}}a{{color:#b9d7e7}}h1{{margin:.2em 0}}h2{{margin-top:30px}}.lead{{color:#a9bdc9}}.note{{padding:14px 17px;border-left:3px solid #967e8b;background:#282633}}.metrics{{display:flex;flex-wrap:wrap;gap:22px;padding:10px 0}}.metrics b{{color:#e5d9df}}img{{width:100%;height:auto;border:1px solid #495361;background:#111b28}}table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;text-align:left;border-bottom:1px solid #38434d}}small{{color:#a8b5be}}</style>
<small>HK3GTL · I37 · WFV / V13 / tier27 · 全新候选</small><h1>世界维系试验平台</h1><p class="lead">双腔差分场试验场 · 开放式环腔、三轴计量框与中轴控制颈部</p>
<p class="note">这是从零构建的新构型，采用双腔差分测量与闭合承力环架。当前交付为待审建筑候选：已生成真实方块结构和实例原始 Minecraft 材质预览；未批准、未进入正式结构索引、未接入实例。</p>
<div class="metrics"><span>{check['blocks']:,} 格实体</span><span>{check['unique_materials']} 种实际材质</span><span>{data['size'][0]} × {data['size'][2]} × {data['size'][1]}（宽×长×高）</span><span>WFV主机壳 {check['wfv_casing_count']:,} 格</span></div>
<p><a href="i37/三维评审.html">打开可交互 MC 材质三维评审</a> · <a href="i37/{data['name']}.nbt">NBT</a> · <a href="i37/{data['name']}.schem">Sponge结构</a> · <a href="材料清单.json">材料清单</a> · <a href="verification.json">实体核验</a></p>
<img src="完整预览.png" alt="I37世界维系试验平台双腔差分场试验场完整MC材质预览">
<h2>结构概念</h2><p>{data['description']}</p><p>两座同构环腔左右对称，一侧承担稳定参考态，另一侧表达局部扰动态。双层环形机壳既围出开放试验空间，也串接检修层与矩形测量框；短导梁锚回内壁，中轴颈部承担主控和十个齐平接口，上部闭合冠梁把两腔的承力路径收成一体。</p>
<h2>尺寸与递增核验</h2><p>当前较低电压最大值以现行已批准、已实装的 I38 IWV 结构为准。四项均严格高于该基线；这只是结构候选验收，不代表游戏功能或FCL性能已经验证。</p>
<table><tr><th>指标</th><th>I37候选</th><th>较低电压最大值</th><th>高出</th></tr>{rows}</table>
<p>实际边界 X=0..528、Y=0..284、Z=0..528；主控蓝图坐标 [{','.join(map(str, data['controller']))}]，宽529格的正中第265格。结构为六向单连通，X=264镜像差异0；WFV主壳是最大单一材料，占主体识别。</p>
<h2>边界</h2><p>输入输出暂按 I35 锚定能力、I36 稳定场、I38供能与稳定介质合同表达。研究门槛、正式配方、完整控制器资源、游戏内成型及实际功能另行核验。FCL与电脑版的空载、全部摆出、FTB Chunks强加载三种内存测试留待结构批次完成后进行；本轮未进行性能实测。</p></html>'''


def main():
    if OUT.exists():
        raise FileExistsError(f'拒绝覆盖已有交付目录: {OUT}')
    version_file = resources.INSTANCE.parent / 'mrpack/modrinth.index.json'
    if not version_file.is_file():
        raise FileNotFoundError(f'找不到目标增强版实例: {resources.INSTANCE}')
    version = json.loads(version_file.read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2', f'实例版本变化为{version}，先复核资源合同'

    OUT.mkdir(parents=True)
    VIEW.mkdir(parents=True)
    LOG.mkdir(parents=True)
    cube, data = geometry.build()
    check = audit(cube, data)
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert len(materials) == check['unique_materials'] == 43
    assert all(item['complete_cube'] and not item['tinted'] for item in materials)

    result = export_dense(cube, geometry.STATES, data['name'], VIEW)
    assert result['block_count'] == check['blocks']
    groups = result['surface_groups']
    check.update(nbt_schem_sha256=result['hashes'], readback=result['readback'],
        viewer_surface_faces=sum(len(face) for group in groups for face in group),
        viewer_payload_exact_cell_readback=True, source_instance=str(resources.INSTANCE),
        instance_version=version, material_resource_sources=sources, enabled_file_resource_packs=packs)
    check['ordinary_material_namespaces'] = {}
    for state, count in check['palette'].items():
        if state not in (geometry.material.CONTROL, geometry.material.PORT):
            namespace = state.split(':')[0]
            check['ordinary_material_namespaces'][namespace] = check['ordinary_material_namespaces'].get(namespace, 0) + count
    groups, lengths, merged = merge_surface_runs(groups, data['size'])
    check.update(viewer_surface_merge=merged, viewer_rendered_quads=merged['rendered_quads'])
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, surfaceRunLengths=lengths,
        blockCount=check['blocks'], materials=materials, audit=check,
        names={state: state.split(':')[1] for state in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    encoded = base64.b64encode(compressed).decode('ascii')
    (VIEW / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    check.update(viewer_payload_gzip_bytes=len(compressed), viewer_payload_base64_bytes=len(encoded))

    save(OUT / 'manifest.json', dict(data, candidate_version='fresh-redesign-20261028',
        status='candidate_waiting_user_review', approved=False, installed=False,
        target_voltage='WFV', voltage_mapping='V13 / tier27', blocks=check['blocks'],
        unique_materials=check['unique_materials'], geometry_passed=True, source_instance=str(resources.INSTANCE),
        instance_version=version, generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [dict(state=item['state'], count=check['palette'][item['state']],
        role=geometry.ROLES[item['state']], complete_cube=item['complete_cube'],
        source=sources.get(item['state'], {}), survival_stage_verified=False) for item in materials])
    (OUT / 'index.html').write_text(page(data, check), encoding='utf-8')
    scripts = OUT / '生成脚本'
    scripts.mkdir()
    for filename in ('build_i37_dual_field_range_20261028.py', 'i37_dual_field_range_geometry_20261028.py',
        'i37_dual_field_range_audit_20261028.py', 'build_i37_dual_field_range_viewer_20261028.mjs',
        'i34_open_observatory_export_20261027.py', 'i37_surface_runs_20261027.py'):
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i37_dual_field_range_viewer_20261028.mjs'), str(OUT)],
        cwd=ROOT, check=True)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False,
        blocks=check['blocks'], materials=check['unique_materials'], size_xyz=data['size'],
        connected_components=check['connectivity']['components'], symmetry=check['bilateral_symmetry'],
        viewer_surface_faces=check['viewer_surface_faces'], rendered_quads=check['viewer_rendered_quads'],
        nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'],
        size=data['size'], viewer_faces=check['viewer_surface_faces'], quads=check['viewer_rendered_quads']),
        ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
