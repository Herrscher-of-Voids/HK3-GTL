# -*- coding: utf-8 -*-
"""I35独立候选：实体审计、真实材质、NBT/Schematic逐格导出及轻量评审。

变更记录 #1（2026-10-27）：新增四爪沉楔锚台候选，不改正式机器与实例。
"""
import base64
import datetime as dt
import gzip
import html
import json
import math
import shutil
import subprocess

import numpy as np
from scipy import ndimage

import i35_spatial_anchor_geometry_20261027 as geometry
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense, digest
from structure_size_baseline import baselines

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I35_虚数空间锚定阵列_四爪沉楔锚台_V1_20261027'
LOG = ROOT / 'logs/i35-spatial-anchor-v1-20261027'
BASE = ROOT / 'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/verification.json'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def audit(cube, data):
    h, d, w = cube.shape
    counts = np.bincount(cube.ravel(), minlength=len(geometry.STATES) + 1)
    assert np.all(counts[1:] > 0)
    palette = dict(sorted(zip(geometry.STATES, map(int, counts[1:])), key=lambda item: -item[1]))
    occupied = cube != 0
    low, high = [], []
    for axis in (2, 0, 1):
        positions = np.flatnonzero(np.any(occupied, axis=tuple(i for i in range(3) if i != axis)))
        low.append(int(positions[0])); high.append(int(positions[-1]))
    actual = [high[i] - low[i] + 1 for i in range(3)]
    assert low == [0, 0, 0] and actual == data['size'] == [w, h, d]
    minimum = baselines()['I35']['size']
    assert all(actual[i] >= minimum[j] for i, j in ((0, 0), (1, 2), (2, 1)))
    assert np.array_equal(cube, cube[:, :, ::-1]), '几何材质不对称'
    labels, components = ndimage.label(occupied)
    assert components == 1, ('实体没有连通', components)
    del labels, occupied
    assert counts[geometry.IDS[geometry.material.CONTROL]] == 1
    assert counts[geometry.IDS[geometry.material.PORT]] == len(data['ports']) == 10
    assert palette[geometry.material.IRV] == max(palette.values())
    assert {s for s in palette if s.startswith('hk3gtl:')} == {geometry.material.IRV, geometry.material.PORT}
    directions = dict(north=(0, 0, -1), south=(0, 0, 1), west=(-1, 0, 0), east=(1, 0, 0))
    marker_checks = []
    for marker in [dict(id='主控', pos=data['controller'], face='north')] + data['ports']:
        x, y, z = marker['pos']; dx, dy, dz = directions[marker['face']]
        state = geometry.material.CONTROL if marker['id'] == '主控' else geometry.material.PORT
        assert cube[y, z, x] == geometry.IDS[state]
        assert cube[y - dy, z - dz, x - dx]
        for step in range(1, 6):
            X, Y, Z = x + dx * step, y + dy * step, z + dz * step
            if 0 <= X < w and 0 <= Y < h and 0 <= Z < d:
                assert cube[Y, Z, X] == 0, ('接口外侧不净空', marker)
        tangent = ((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)) if dx else ((0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0))
        assert all(cube[y + b, z + c, x + a] for a, b, c in tangent), ('不连续接口', marker)
        span = cube[y, z - 4:z + 5, x] if dx else cube[y, z, x - 4:x + 5]
        assert np.all(span), ('独立面板', marker)
        marker_checks.append(dict(id=marker['id'], position=marker['pos'], face=marker['face'], outer_clear=5, inner_backed=True, flush_shell=True))
    assert data['controller'][0] == (w - 1) // 2
    for route in data['paths']:
        x, y, z = route['min']; X, Y, Z = route['max']
        assert not np.any(cube[y:Y + 1, z:Z + 1, x:X + 1])
    for zone in data['zones']:
        x, y, z = zone['pos']; assert cube[y, z, x], zone
    progression = json.loads(BASE.read_text(encoding='utf-8'))['voltage_progression']
    assert len(list((ROOT / progression['source']).glob('*.json'))) == 41
    sources = []
    for form in progression['lower_forms']:
        for key in ('metadata', 'blueprint'):
            actual_hash = digest(ROOT / form[key]); assert actual_hash == form[key + '_sha256']
            sources.append(dict(id=form['id'], path=form[key], sha256=actual_hash))
    metrics = dict(blocks=int(counts[1:].sum()), materials=len(palette), volume=math.prod(actual), height=h)
    passes = {key: value > progression['lower_maxima'][key]['value'] for key, value in metrics.items()}
    assert all(passes.values()), (metrics, progression['lower_maxima'])
    return dict(passed=True, geometry_passed=True, approved=False, installed=False, game_verified=False,
        size_xyz=actual, size_wdh=[w, d, h], bounds_xyz=dict(min=low, max=high), blocks=metrics['blocks'],
        unique_materials=len(palette), palette=palette, irv_casing_count=palette[geometry.material.IRV],
        bounding_box_volume=metrics['volume'], height=h, baseline_check=dict(passed=True, baseline_wdh=minimum),
        bilateral_symmetry=dict(passed=True, axis=f'X={(w - 1) // 2}'), connectivity=dict(passed=True, components=components),
        controller=dict(position=data['controller'], ordinal_from_left=data['controller'][0] + 1), port_checks=marker_checks,
        voltage_progression=dict(metrics=metrics, passes=passes, lower_maxima=progression['lower_maxima'],
            lower_form_count=37, formal_metadata_count=41, lower_sources_sha256=sources,
            comparison='I34与I35同为IRV，互不强制递增；37个正式低阶均须超过，本轮核对74份源哈希未变。'),
        checks=['逐格实体范围、数量、材料及高度四项递增100%通过。', '实体单连通，左右几何和材质完全对称。',
                'IRV主壳为最大单一材料，项目新增材料白名单通过。', '钻石主控居中；10接口齐平连续嵌入、有背板和五格净空。'],
        not_verified=['建筑外观尚待负责人批准；未接入实例，batch-09现有I34第1/5。',
                      '正式Pattern、控制器、真实仓室能力、配方、研究及生存获取链未在本轮验收。',
                      '锚定工况与游戏运行未验证；本机不新增传送能力。'])


def report(data, check):
    rows = ''.join(f'<tr><td>{name}</td><td>{check["voltage_progression"]["metrics"][key]:,}</td><td>{check["voltage_progression"]["lower_maxima"][key]["value"]:,}</td><td>通过</td></tr>'
        for key, name in [('blocks', '实体方块'), ('materials', '材料种类'), ('volume', '实体包围盒体积'), ('height', '实体高度')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I35虚数空间锚定阵列V1</title><style>
body{{max-width:1280px;margin:32px auto;padding:0 22px;background:#111c29;color:#e5edf3;font:16px/1.8 system-ui}}a{{color:#d2bd8b}}img{{max-width:100%}}.note{{padding:16px;border-left:3px solid #bc9a65;background:#263141}}td,th{{padding:10px;border-bottom:1px solid #415062;text-align:left}}table{{width:100%;border-collapse:collapse}}</style>
<small>HK3GTL / I35 / IRV · V11 / 建筑候选V1</small><h1>虚数空间锚定阵列 · 四爪沉楔锚台</h1><p class="note">{html.escape(data['description'])}</p>
<p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体方块 · {check['unique_materials']}种材料 · IRV主体{check['irv_casing_count']:,}块</p>
<p><a href="i35/三维评审.html">打开三维评审</a> · <a href="完整预览.png">完整画面</a> · <a href="材料清单.json">材料用量</a> · <a href="verification.json">实体核验</a></p><img src="完整预览.png" alt="I35四爪沉楔锚台完整预览">
<h2>实体锚定工程</h2><p>以十字反力基座传递负载，四向液压锁爪从低位铰座收拢，夹持带有多级锁头的八角沉楔。宽大的分段压套、承力肋和读出设备围绕受力路线布置，研究和冷却设备位于梁内检修层，避免外圈厂房重复。</p>
<p>输入真实魂钢锚件、I33空间核心组件、I34校准资料、能源及稳定介质；进行实体组件标定、稳定工况验证、维系负载复验和失效诊断。合格组件与锚定状态/记录分别交付，供I37世界维系试验使用。</p>
<p>RN-IAA开放本机；RN-ILE、RN-VCA及修订101接线中的RN-SPM、RN-DKE须按最终研究定义核验。首份实验使用I16制样、I33校准与I34真实初观证据，不能要求I35自产件或W03构成自锁。</p>
<h2>量化核验</h2><p>四项检查100%通过，主控与接口11处检查100%通过。I34与I35同阶，不强制按编号扩大；本机须超过全部37个正式低档形态，74份源文件哈希本轮核对不变。</p><table><tr><th>指标</th><th>I35</th><th>低档最大值</th><th>结果</th></tr>{rows}</table>
<p>主控蓝图{data['controller']}，从1起算为第{data['controller'][0]+1}格；接口以工业方块表示并齐平嵌入实际设备面。真实能力另按正式Pattern核验。</p>
<p class="note">仅建筑候选，尚未批准或实装。I34 V2已确认归入batch-09第1/5，本候选不计入批次。本机不凭报告生成实物、不新增传送能力，不替代I44/I45、不绕过终审维度禁行；外观不能代替游戏运行验收。</p></html>'''


def main():
    OUT.mkdir(exist_ok=True, parents=True); LOG.mkdir(exist_ok=True, parents=True)
    view = OUT / 'i35'; view.mkdir(exist_ok=True)
    print('生成I35新几何与实体核验…', flush=True)
    cube, data = geometry.build(); check = audit(cube, data)
    version = json.loads((resources.INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('流式导出并逐格回读结构…', flush=True)
    result = export_dense(cube, geometry.STATES, data['name'], view)
    assert result['block_count'] == check['blocks']
    groups = result['surface_groups']
    check.update(nbt_schem_sha256=result['hashes'], readback=result['readback'],
        viewer_surface_faces=sum(len(face) for group in groups for face in group),
        viewer_payload_exact_cell_readback=True, source_instance=str(resources.INSTANCE), instance_version=version,
        material_resource_sources=sources, enabled_file_resource_packs=packs)
    check['ordinary_material_namespaces'] = {}
    for state, count in check['palette'].items():
        if state not in (geometry.material.CONTROL, geometry.material.PORT):
            ns = state.split(':')[0]; check['ordinary_material_namespaces'][ns] = check['ordinary_material_namespaces'].get(ns, 0) + count
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, blockCount=check['blocks'], materials=materials,
                   audit=check, names={s: s.split(':')[1] for s in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    encoded = base64.b64encode(compressed).decode('ascii')
    (view / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    check.update(viewer_payload_gzip_bytes=len(compressed), viewer_payload_base64_bytes=len(encoded))
    manifest = dict(data, candidate_version='V1', status='candidate_waiting_user_review', approved=False, installed=False,
        target_voltage='IRV', voltage_mapping='V11 / tier25', blocks=check['blocks'], unique_materials=check['unique_materials'],
        geometry_passed=True, source_instance=str(resources.INSTANCE), instance_version=version,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds'))
    save(OUT / 'manifest.json', manifest); save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
                               complete_cube=m['complete_cube'], source=sources.get(m['state'], {})) for m in materials])
    (OUT / 'index.html').write_text(report(data, check), encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in ['build_i35_spatial_anchor_v1_20261027.py', 'i35_spatial_anchor_geometry_20261027.py',
                     'build_i35_spatial_anchor_viewer_v1_20261027.mjs', 'i34_open_observatory_export_20261027.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i35_spatial_anchor_viewer_v1_20261027.mjs'), str(OUT)], cwd=ROOT, check=True)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, blocks=check['blocks'], materials=check['unique_materials'],
        size_xyz=data['size'], surface_faces=check['viewer_surface_faces'], nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'], faces=check['viewer_surface_faces']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
