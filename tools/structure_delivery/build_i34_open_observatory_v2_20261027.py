# -*- coding: utf-8 -*-
"""I34开穹悬弦观测仪：独立候选打包、实体审计与真实材质预览。

变更记录 #1：2026-10-27，重设计建筑并组合已确认树影；未修改正式资源或实例。
"""
import base64
import datetime as dt
import gzip
import hashlib
import html
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
from scipy import ndimage

import i34_open_observatory_geometry_20261027 as geometry
from i34_open_observatory_export_20261027 import export_dense, digest
import build_i25_world_bubble_observatory_20261025 as resources
from structure_size_baseline import baselines

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I34_虚数之树观测阵列_开穹悬弦观测仪_V2_20261027'
LOG = ROOT / 'logs/i34-open-observatory-v2-20261027'
OLD = ROOT / 'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027'
PROJECTION = ROOT / 'deliveries/I34_虚数之树_动态投影研究_V1_20261027'


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
    minimum = baselines()['I34']['size']
    assert all(actual[i] >= minimum[j] for i, j in ((0, 0), (1, 2), (2, 1)))
    assert np.array_equal(cube, cube[:, :, ::-1]), '实体和材质未严格左右对称'
    labels, components = ndimage.label(occupied)
    if components != 1:
        sizes = np.bincount(labels.ravel()); sizes[0] = 0
        raise AssertionError(('存在未连接的实体', components, sorted(map(int, sizes[1:]), reverse=True)[:10]))
    del labels, occupied
    assert counts[geometry.IDS[geometry.palette.CONTROL]] == 1
    assert counts[geometry.IDS[geometry.palette.PORT]] == len(data['ports']) == 10
    assert palette[geometry.palette.IRV] == max(palette.values())
    assert {state for state in palette if state.startswith('hk3gtl:')} == {geometry.palette.IRV, geometry.palette.PORT}
    markers = [dict(id='主控', pos=data['controller'], face='north', state=geometry.palette.CONTROL)]
    markers += [dict(port, state=geometry.palette.PORT) for port in data['ports']]
    checks = []
    for item in markers:
        x, y, z = item['pos']; inward = 1 if item['face'] == 'north' else -1
        assert cube[y, z, x] == geometry.IDS[item['state']]
        assert cube[y, z + inward, x] != 0
        assert all(cube[y + dy, z, x + dx] for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)))
        assert all(cube[y, z - inward * step, x] == 0 for step in range(1, 6))
        # 接口属于已有连续设备立面，横向至少9格的外墙同平面保持连续。
        assert np.all(cube[y, z, x - 4:x + 5] != 0), ('接口成为突出面板', item)
        checks.append(dict(id=item['id'], position=item['pos'], face=item['face'], outer_clear=5, inner_backed=True, flush_shell=True))
    assert data['controller'][0] == (w - 1) // 2
    for route in data['paths']:
        x, y, z = route['min']; X, Y, Z = route['max']
        assert not np.any(cube[y:Y + 1, z:Z + 1, x:X + 1]), route
    for zone in data['zones']:
        if not zone.get('visual_only'):
            x, y, z = zone['pos']; assert cube[y, z, x], zone
    old = json.loads((OLD / 'verification.json').read_text(encoding='utf-8'))
    progression = old['voltage_progression']
    assert len(list((ROOT / progression['source']).glob('*.json'))) == 41
    source_hashes = []
    for form in progression['lower_forms']:
        for key in ('metadata', 'blueprint'):
            actual_hash = digest(ROOT / form[key])
            assert actual_hash == form[key + '_sha256'], ('低阶源变化，需要重读指标', form['id'], key)
            source_hashes.append(dict(id=form['id'], path=form[key], sha256=actual_hash))
    metrics = dict(blocks=int(counts[1:].sum()), materials=len(palette), volume=math.prod(actual), height=h)
    passes = {key: value > progression['lower_maxima'][key]['value'] for key, value in metrics.items()}
    assert all(passes.values()), ('电压递增不满足', metrics, progression['lower_maxima'])
    assert h - 1 - 60 <= 236
    projection = json.loads((PROJECTION / 'manifest.json').read_text(encoding='utf-8'))
    assert projection['approved'] and not projection['installed']
    assert digest(PROJECTION / 'index.html') == projection['approved_sha256']
    return dict(passed=True, geometry_passed=True, approved=False, installed=False, game_verified=False,
                size_xyz=actual, size_wdh=[w, d, h], bounds_xyz=dict(min=low, max=high),
                blocks=metrics['blocks'], unique_materials=len(palette), palette=palette,
                bounding_box_volume=metrics['volume'], height=h, irv_casing_count=palette[geometry.palette.IRV],
                bilateral_symmetry=dict(passed=True, axis=f'X={(w - 1) // 2}'), connectivity=dict(components=components, passed=True),
                baseline_check=dict(passed=True, baseline_wdh=minimum, actual_xyz=actual), port_checks=checks,
                controller=dict(position=data['controller'], ordinal_from_left=data['controller'][0] + 1),
                voltage_progression=dict(metrics=metrics, passes=passes, lower_maxima=progression['lower_maxima'],
                    lower_form_count=37, formal_metadata_count=41, lower_sources_sha256=source_hashes,
                    evidence='使用已逐格核验的37个低阶指标；本轮复核全部74份源文件SHA256不变，未重新解析不变蓝图。'),
                projection=dict(approved_effect=True, entity_blocks=0, excluded_from_pattern=True,
                                source_sha256=projection['approved_sha256'], approval_record=projection['approval_record']),
                checks=['真实实体宽、长、高及全部低阶递增四指标通过。', '全体实体六邻接单连通，实体与材质严格左右对称。',
                        '主控整宽居中；接口齐平嵌入连续设备立面，内有背板、外留五格净空。',
                        '项目专属方块仅IRV电压机壳与工业接口占位块；树影不计实体。'],
                not_verified=['I34新建筑外观尚待负责人批准；树影采用另行确认V1。',
                              '未接入游戏；正式控制器、Pattern、工艺、研究及生存获取链另行核验。',
                              '只观测联系和误差；不得以外观或投影声称制造/操纵虚数之树或真实初观成功。'])


def report(data, check):
    esc = html.escape
    rows = ''.join(f'<tr><td>{label}</td><td>{check["voltage_progression"]["metrics"][key]:,}</td><td>{check["voltage_progression"]["lower_maxima"][key]["value"]:,}</td><td>通过</td></tr>'
                   for key, label in [('blocks', '实体方块数'), ('materials', '材料种类'), ('volume', '实体包围盒体积'), ('height', '实体高度')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(data['title'])} V2</title><style>
body{{max-width:1250px;margin:32px auto;padding:0 24px;background:#101b29;color:#e6edf3;font:16px/1.8 system-ui}}a{{color:#d6bd83}}img{{width:100%;height:auto}}table{{border-collapse:collapse;width:100%}}td,th{{padding:10px;border-bottom:1px solid #3a4655;text-align:left}}.note{{padding:18px;background:#1b2938;border-left:3px solid #be985d}}.links{{display:flex;gap:24px;flex-wrap:wrap}}small{{color:#a7b5c4}}</style>
<small>HK3GTL / I34 / IRV · V11 / 独立建筑候选 V2</small><h1>开穹悬弦观测仪</h1><p class="note">{esc(data['description'])}</p>
<p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体方块 · {check['unique_materials']}种材料</p>
<p class="links"><a href="i34/三维评审.html">打开建筑与动态树影预览</a><a href="完整预览.png">完整画面</a><a href="verification.json">实体核验</a><a href="材料清单.json">材料用量</a><a href="manifest.json">候选清单</a></p>
<img src="完整预览.png" alt="I34新候选建筑与已确认树影的同场景完整预览">
<h2>独立的仪器轮廓</h2><p>前方开敞，后方双弦臂弯曲上扬；校准弦列和低矮后桥形成单侧观测背架。研究空间藏在透镜形基座的层间，通过带状窗与设备分隔辨认；顶部保留检修走台和相位光阑。主控位于北向鼻台的整宽中轴，接口融入前后实际交接设备。</p>
<p>沿用已确认的金白树影V1。树影属于非实体显示层，可以隐藏或暂停；NBT和Schematic仅包含实体设备，不含投影。预览里的光点和光脉不表示游戏功能已实现。</p>
<h2>职责与研究顺序</h2><p>输入世界泡对照档案、空间探针与能量，观测树与世界的联系和误差，输出联系图及虚数观测资料，供I35及S04使用。RN-IOP开放I34；首次真实初观成功支持RN-ILE，不能以前置I35或S04造成循环。</p>
<h2>IRV量化核验</h2><p>全部37个低电压正式形态作为比较对象，74份源文件SHA256本轮复核不变。四项实体指标检查100%通过；外观由负责人评审。</p><table><tr><th>指标</th><th>I34 V2</th><th>低阶最大值</th><th>结果</th></tr>{rows}</table>
<p class="note">建筑候选待审，未接入实例，batch-09仍0/5。投影V1的已确认状态不等于新建筑获批。Pattern、控制器、配方、生存可达性和游戏运行均未在本轮验收。</p></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    view = OUT / 'i34'; view.mkdir(exist_ok=True)
    print('生成全新实体几何…', flush=True)
    cube, data = geometry.build()
    print('核对实体、接口与低阶源文件…', flush=True)
    check = audit(cube, data)
    version = json.loads((resources.INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2', ('实例版本变化', version)
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('流式导出并逐格回读NBT、Schematic…', flush=True)
    exported = export_dense(cube, geometry.STATES, data['name'], view)
    assert exported['block_count'] == check['blocks']
    groups = exported['surface_groups']
    check.update(source_instance=str(resources.INSTANCE), instance_version=version, material_resource_sources=sources,
                 enabled_file_resource_packs=packs, nbt_schem_sha256=exported['hashes'], readback=exported['readback'],
                 viewer_surface_faces=sum(len(face) for group in groups for face in group),
                 viewer_payload_exact_cell_readback=True)
    check['ordinary_material_namespaces'] = {}
    for state, count in check['palette'].items():
        if state not in (geometry.palette.CONTROL, geometry.palette.PORT):
            ns = state.split(':')[0]
            check['ordinary_material_namespaces'][ns] = check['ordinary_material_namespaces'].get(ns, 0) + count
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, blockCount=check['blocks'],
                   materials=materials, audit=check, names={s: s.split(':')[1] for s in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    encoded = base64.b64encode(compressed).decode('ascii')
    (view / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    check.update(viewer_payload_gzip_bytes=len(compressed), viewer_payload_base64_bytes=len(encoded))
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')
    manifest = dict(data, candidate_version='V2', status='candidate_waiting_user_review', approved=False, installed=False,
                    target_voltage='IRV', voltage_mapping='V11 / tier25', blocks=check['blocks'],
                    unique_materials=check['unique_materials'], geometry_passed=True, instance_version=version, generated_at=now)
    save(OUT / 'manifest.json', manifest); save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']],
                                        role=geometry.ROLES[m['state']], complete_cube=m['complete_cube'],
                                        source=sources.get(m['state'], {})) for m in materials])
    (OUT / 'index.html').write_text(report(data, check), encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in [Path(__file__).name, 'i34_open_observatory_geometry_20261027.py',
                     'i34_open_observatory_export_20261027.py', 'build_i34_open_observatory_viewer_v2_20261027.mjs']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    print('构建建筑与已确认树影的组合三维预览…', flush=True)
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i34_open_observatory_viewer_v2_20261027.mjs'), str(OUT)], cwd=ROOT, check=True)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, blocks=check['blocks'],
         materials=check['unique_materials'], size_xyz=data['size'], surface_faces=check['viewer_surface_faces'], nbt_schem_sha256=exported['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'], faces=check['viewer_surface_faces']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
