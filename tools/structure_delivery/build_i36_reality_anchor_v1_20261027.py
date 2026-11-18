# -*- coding: utf-8 -*-
"""I36独立建筑候选：逐格核验、增强版真实材质与标准HTML交付。"""
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

import i36_reality_anchor_geometry_v1_20261027 as geometry
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense, digest
from structure_size_baseline import baselines

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I36_崩坏能现实稳定锚_双叉谐振稳相井_V1_20261027'
LOG = ROOT / 'logs/i36-reality-anchor-v1-20261027'
EVIDENCE = ROOT / 'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/verification.json'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def audit(cube, data):
    h, d, w = cube.shape
    counts = np.bincount(cube.ravel(), minlength=len(geometry.STATES) + 1)
    assert np.all(counts[1:] > 0)
    palette = dict(sorted(zip(geometry.STATES, map(int, counts[1:])), key=lambda p: -p[1]))
    occupied = cube != 0
    low, high = [], []
    for axis in (2, 0, 1):
        positions = np.flatnonzero(np.any(occupied, axis=tuple(i for i in range(3) if i != axis)))
        low.append(int(positions[0])); high.append(int(positions[-1]))
    actual = [high[i] - low[i] + 1 for i in range(3)]
    assert low == [0, 0, 0] and actual == data['size'] == [w, h, d]
    minimum = baselines()['I36']['size']
    assert all(actual[i] >= minimum[j] for i, j in ((0, 0), (1, 2), (2, 1)))
    assert np.array_equal(cube, cube[:, :, ::-1]), '几何材质不对称'
    labels, components = ndimage.label(occupied)
    assert components == 1, ('实体未连通', components)
    del labels, occupied
    assert counts[geometry.IDS[geometry.material.CONTROL]] == 1
    assert counts[geometry.IDS[geometry.material.PORT]] == len(data['ports']) == 8
    assert palette[geometry.material.QSV] == max(palette.values())
    assert {s for s in palette if s.startswith('hk3gtl:')} == {geometry.material.QSV, geometry.material.PORT}
    directions = dict(north=(0, 0, -1), south=(0, 0, 1), west=(-1, 0, 0), east=(1, 0, 0))
    markers = []
    for item in [dict(id='主控', pos=data['controller'], face='north')] + data['ports']:
        x, y, z = item['pos']; dx, dy, dz = directions[item['face']]
        state = geometry.material.CONTROL if item['id'] == '主控' else geometry.material.PORT
        assert cube[y, z, x] == geometry.IDS[state]
        assert cube[y - dy, z - dz, x - dx], ('缺少内背板', item)
        for k in range(1, 6):
            X, Y, Z = x + dx * k, y + dy * k, z + dz * k
            if 0 <= X < w and 0 <= Y < h and 0 <= Z < d:
                assert cube[Y, Z, X] == 0, ('接口外侧不净空', item, [X, Y, Z])
        tangent = ((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)) if dx else ((0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0))
        assert all(cube[y + b, z + c, x + a] for a, b, c in tangent), ('接口周边断面', item)
        span = cube[y, z - 4:z + 5, x] if dx else cube[y, z, x - 4:x + 5]
        assert np.all(span), ('接口未嵌入连续设备面', item)
        markers.append(dict(id=item['id'], position=item['pos'], face=item['face'], outer_clear=5, inner_backed=True, flush_shell=True))
    assert data['controller'][0] == (w - 1) // 2
    for route in data['paths']:
        x, y, z = route['min']; X, Y, Z = route['max']
        assert not np.any(cube[y:Y + 1, z:Z + 1, x:X + 1])
    for zone in data['zones']:
        x, y, z = zone['pos']; assert cube[y, z, x], zone
    # 比较电压而非机器编号；I34/I35的IRV高度不是QSV的递增下限。
    source = json.loads(EVIDENCE.read_text(encoding='utf-8'))['voltage_progression']
    assert len(list((ROOT / source['source']).glob('*.json'))) == 41
    forms = [f for f in source['lower_forms'] if f['tier'] < 19]
    assert len(forms) == 19
    for form in forms:
        for key in ('metadata', 'blueprint'):
            assert digest(ROOT / form[key]) == form[key + '_sha256']
    metrics = dict(blocks=int(counts[1:].sum()), materials=len(palette), volume=math.prod(actual), height=h)
    maxima = {k: dict(value=max(f['metrics'][k] for f in forms),
        ids=[f['id'] for f in forms if f['metrics'][k] == max(x['metrics'][k] for x in forms)]) for k in metrics}
    passes = {k: metrics[k] > maxima[k]['value'] for k in metrics}
    assert all(passes.values()), (metrics, maxima)
    assert -60 + h - 1 <= 236
    return dict(passed=True, geometry_passed=True, approved=False, installed=False, game_verified=False,
        size_xyz=actual, size_wdh=[w, d, h], bounds_xyz=dict(min=low, max=high), blocks=metrics['blocks'],
        unique_materials=len(palette), palette=palette, qsv_casing_count=palette[geometry.material.QSV],
        bounding_box_volume=metrics['volume'], height=h,
        baseline_check=dict(passed=True, baseline_wdh=minimum),
        bilateral_symmetry=dict(passed=True, axis=f'X={(w - 1) // 2}'), connectivity=dict(passed=True, components=1),
        controller=dict(position=data['controller'], ordinal_from_left=data['controller'][0] + 1), port_checks=markers,
        voltage_progression=dict(source=source['source'], formal_metadata_count=41, target_voltage='QSV', target_tier=19,
            lower_form_count=19, metrics=metrics, lower_maxima=maxima, passes=passes, lower_forms=forms,
            comparison='按目标电压严格超过19种正式低档形态，38份源文件SHA256均未变；同阶和高阶不作编号递增。'),
        checks=['实体数、材料数、包围盒体积及实际高度四项递增检查100%通过。',
            '全结构单连通，左右几何及材质严格镜像；QSV为最大单一材料。',
            '钻石主控居中，8接口嵌入标定室连续外壳，有背板与五格外侧净空。'],
        not_verified=['候选尚待负责人批准；未实装，当前batch-09仅I34与I35两台已确认。',
            '正式Pattern、真实供能与覆盖提供者、耗材扣除、工况和游戏运行未在本轮验收。',
            'QSV映射与基础型前期可建链存在历史衔接待验，不宣称生存可达已解决。'])


def report(data, check):
    metrics = check['voltage_progression']
    rows = ''.join(f'<tr><td>{label}</td><td>{metrics["metrics"][key]:,}</td><td>{metrics["lower_maxima"][key]["value"]:,}</td><td>通过</td></tr>'
        for key, label in [('blocks', '实体方块'), ('materials', '材料种类'), ('volume', '实体包围盒'), ('height', '实际高度')])
    total = sum(check['ordinary_material_namespaces'].values())
    sources = '；'.join(f'{key} {value:,}块（{value / total:.2%}）' for key, value in check['ordinary_material_namespaces'].items())
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I36崩坏能现实稳定锚V1</title>
<style>body{{max-width:1240px;margin:32px auto;padding:0 22px;background:#111c29;color:#e5edf3;font:16px/1.8 system-ui}}a{{color:#a4d9d8}}img{{max-width:100%}}.note{{padding:16px;border-left:3px solid #77a5ad;background:#22333e}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #43535f}}</style>
<small>HK3GTL / I36 / QSV · V05 · tier19 / 独立建筑候选V1</small><h1>崩坏能现实稳定锚 · 双叉谐振稳相井</h1>
<p class="note">{html.escape(data['description'])}</p><p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体方块 · {check['unique_materials']}种材料 · QSV主壳{check['qsv_casing_count']:,}块</p>
<p><a href="i36/三维评审.html">打开三维评审</a> · <a href="完整预览.png">完整画面</a> · <a href="材料清单.json">材料用量</a> · <a href="verification.json">实体核验</a></p><img src="完整预览.png" alt="I36双叉谐振稳相井完整预览">
<h2>稳定设备的轮廓</h2><p>开顶的双叉与下弧承座作为一个连续体，从开敞沉井升起。井内锚芯向下收尖，后倾阻尼撑杆连接独立预紧座；两侧低位循环机列持续散热，前端标定室接收耗材、维护覆盖状态。以青灰QSV外壳为主，银灰承力压边与内侧窄光尺形成克制的识别层次。</p>
<h2>工艺及研究边界</h2><p>职责是持续耗能与耗材的现实稳定覆盖服务：基础覆盖、强化覆盖、持续补给与负载核验。输入工业能量、稳定耗材及已解锁工况资料；交付覆盖状态、运行记录和用后耗材。不制造锚件、世界或免费能源。</p>
<p>RN-RAT由S01/I02承担，前置RN-HSA、RN-LES；首实验用前级GT制场响应试件在I02作干扰前后对照，不能要求I36先运行。RN-ERA由S02/I02承担，前置RN-RAT、RN-CCE，必须先有基础运行证据，不能预先使用待解锁强化模式。强化另按实际RN-JOK与工装核验。</p>
<p>既定机制的64/128格球形覆盖、0.50/0.75抑制与重叠取最大，均须由加载、同维度、同团队、成型、启用且先扣电的真实提供者实现；研究稳定量不等于直接降低注视度原值。本次建筑未实现或验收这些提供者，放置控制器不会因此自动生效。</p>
<p class="note">当前建筑映射遵从QSV/V05；历史前期基础型、MAX/HRV工况与QSV整机材料之间的首建衔接仍待验。本轮不擅改映射，也不把基础型反锁到强化核心。材料模型及材质已按增强版2.9.2核验；完整生存获取链未验收。</p>
<h2>量化核验</h2><p>与19种QSV以下正式形态比较；四项检查100%通过，主控和接口9处检查100%通过。I35为IRV，比I36高阶，不能按编号要求I36继续超过它的规模。38份低阶源文件哈希本轮核对不变。</p><table><tr><th>指标</th><th>I36</th><th>低阶最大值</th><th>结果</th></tr>{rows}</table>
<p>主控蓝图{data['controller']}，整宽第{data['controller'][0]+1}格，北向；8个接口齐平嵌入前端标定室。推荐世界Y=-60，最高实体Y=90，Schematic Offset不代表世界坐标。</p><p>普通建材来源：{sources}。钻石主控1块、工业接口8块另列。所有材质均为实际完整方块，空气不计用量。</p>
<p class="note">I35 V3已确认并独立归档，batch-09现为I34、I35两台，2/5。本I36为待审候选，未实装；结构外观不能代替正式控制器、Pattern、覆盖机制、研究、生存可达性和游戏运行验收。</p></html>'''


def main():
    OUT.mkdir(exist_ok=True, parents=True); LOG.mkdir(exist_ok=True, parents=True)
    view = OUT / 'i36'; view.mkdir(exist_ok=True)
    cube, data = geometry.build(); check = audit(cube, data)
    version = json.loads((resources.INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('I36实体核验通过，导出并逐格回读…', flush=True)
    result = export_dense(cube, geometry.STATES, data['name'], view)
    assert result['block_count'] == check['blocks']
    groups = result['surface_groups']
    check.update(nbt_schem_sha256=result['hashes'], readback=result['readback'],
        viewer_surface_faces=sum(len(face) for group in groups for face in group), viewer_payload_exact_cell_readback=True,
        source_instance=str(resources.INSTANCE), instance_version=version,
        material_resource_sources=sources, enabled_file_resource_packs=packs)
    check['ordinary_material_namespaces'] = {}
    for state, count in check['palette'].items():
        if state not in (geometry.material.CONTROL, geometry.material.PORT):
            ns = state.split(':')[0]
            check['ordinary_material_namespaces'][ns] = check['ordinary_material_namespaces'].get(ns, 0) + count
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, blockCount=check['blocks'], materials=materials,
        audit=check, names={s: s.split(':')[1] for s in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    encoded = base64.b64encode(compressed).decode('ascii')
    (view / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    check.update(viewer_payload_gzip_bytes=len(compressed), viewer_payload_base64_bytes=len(encoded))
    manifest = dict(data, candidate_version='V1', status='candidate_waiting_user_review', approved=False, installed=False,
        target_voltage='QSV', voltage_mapping='V05 / tier19', blocks=check['blocks'], unique_materials=check['unique_materials'],
        geometry_passed=True, source_instance=str(resources.INSTANCE), instance_version=version,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds'))
    save(OUT / 'manifest.json', manifest); save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'], source=sources.get(m['state'], {}), survival_stage_verified=False) for m in materials])
    (OUT / 'index.html').write_text(report(data, check), encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in ['build_i36_reality_anchor_v1_20261027.py', 'i36_reality_anchor_geometry_v1_20261027.py',
        'build_i36_reality_anchor_viewer_v1_20261027.mjs', 'i34_open_observatory_export_20261027.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i36_reality_anchor_viewer_v1_20261027.mjs'), str(OUT)], cwd=ROOT, check=True)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, blocks=check['blocks'],
        materials=check['unique_materials'], size_xyz=data['size'], surface_faces=check['viewer_surface_faces'], nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'], faces=check['viewer_surface_faces']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
