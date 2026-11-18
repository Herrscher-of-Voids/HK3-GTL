# -*- coding: utf-8 -*-
"""生成I37三轴世界线干涉测量台独立实体候选与真实材质预览。"""
from __future__ import annotations

import base64
import datetime as dt
import gzip
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
import i37_triaxial_worldline_geometry_20261028 as geometry
from i37_triaxial_worldline_audit_20261028 import audit
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs
from build_i25_world_bubble_observatory_20261025 import (
    INSTANCE, resource_materials,
)

OUT = ROOT / 'deliveries/I37_世界维系试验平台_三轴世界线干涉测量台_白纸重设计_20261028'
VIEW = OUT / 'i37'
LOG = ROOT / 'logs/i37-triaxial-worldline-20261028'
FONT = Path('C:/Windows/Fonts/msyh.ttc')


def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def report(data, check, image=''):
    metrics = check['voltage_progression']
    rows = ''.join(
        f'<tr><td>{label}</td><td>{metrics["metrics"][key]:,}</td>'
        f'<td>{metrics["baseline"][key]:,}</td>'
        f'<td>+{(metrics["metrics"][key] / metrics["baseline"][key] - 1) * 100:.1f}%</td></tr>'
        for key, label in (('blocks', '实际实体方块'), ('materials', '材料种类'),
                           ('volume', '实体包围盒体积'), ('height', '实际高度')))
    image_markup = f'<img src="完整预览.png" alt="I37三轴世界线干涉测量台真实MC材质全景" />' if image else ''
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I37 · 世界维系试验平台 · 三轴世界线干涉测量台</title>
<style>body{{max-width:1320px;margin:28px auto;padding:0 22px;background:#111922;color:#e5ecef;font:16px/1.75 system-ui,"Microsoft YaHei",sans-serif}}a{{color:#a9d8e5}}h1{{line-height:1.2}}img{{width:100%;border:1px solid #425360}}.note{{padding:14px 18px;border-left:3px solid #967887;background:#25242b}}table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;text-align:left;border-bottom:1px solid #44515b}}code{{background:#1b2932;padding:2px 5px}}.files a{{margin-right:14px}}</style>
<small>HK3GTL / I37 / WFV · V13 / tier27 · 白纸新构型</small><h1>世界维系试验平台 · 三轴世界线干涉测量台</h1>
<p class="note">本方案依据正式功能重新构思。三条正交测量基线由同一轨床汇入中央零位井，分别承担锚定、参考态对照、扰动态测量与维系记录采集；高架计量框与主体梁床闭合承力。</p>
<p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体方块 · {check['materials']}种材料 · WFV主壳{check['wfv_casing_count']:,}块</p>
<p class="files"><a href="i37/三维评审.html">打开交互三维评审</a><a href="完整预览.png">完整画面</a><a href="材料清单.json">材料用量</a><a href="{data['name']}.nbt">NBT</a><a href="{data['name']}.schem">Sponge结构</a><a href="verification.json">逐格核验</a></p>{image_markup}
<h2>构型</h2><p>主体由三条正交、尺度不同的开敞测量轴组成。纵向基线承担锚定输入和维系记录，左右横向基线分别布置参考态与扰动态；中央零位测量井汇合三轴读数。高架计量框使用同一组连续梁柱，刻度、滑台、绝缘件和隔振托座沿测量轴布置，形成精密干涉仪器阵列的轮廓。</p>
<p>主控蓝图坐标 {check['controller']['position']}，位于整宽第{check['controller']['ordinal_from_left']}格。控制器候选与10个接口标记嵌入正面设备梁，接口有背板且外侧留有装配净空。</p>
<h2>正式职能边界</h2><p>RN-WME将I37定义为世界维系试验工况；需要I35锚定能力、I36稳定场及I38合同供能与稳定介质的实际记录，运行后产出世界维系报告。不要求I37先行运行，不破坏玩家真实世界制造试验事件，起步试件不使用奇观材料。当前建筑仅为工艺造型表达，不宣称正式Pattern、配方、研究或运行报告已实现。</p>
<h2>电压递增审计</h2><p>以已批准并实装的I38（IWV）为比较基准。I37对应WFV/V13，以下四项均严格超过I38；不以空白导出尺寸计数。</p><table><tr><th>指标</th><th>I37实际值</th><th>I38已批准基线</th><th>超出基线</th></tr>{rows}</table>
<p>左右镜像差异0格；六向连通分量1；43种实际建材均来自增强版2.9.2实例已解析的完整方块模型，钻石主控及工业接口标记另计。HTML贴图预览不代替游戏成型与运行验收。</p>
<p class="note">状态：待负责人审阅，未批准、未接入实例。FCL与电脑版三场景内存测试依既定顺序待全部结构完成后执行。</p></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    VIEW.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    version_file = INSTANCE.parent / 'mrpack/modrinth.index.json'
    version = json.loads(version_file.read_text(encoding='utf-8'))['versionId']
    if version != '2.9.2':
        raise RuntimeError(f'增强版实例版本为{version}，预期2.9.2；先复核资源再继续')
    grid, data = geometry.build()
    check = audit(grid, data)
    materials, sources, packs = resource_materials(geometry.STATES)
    if len(materials) != len(geometry.STATES) or not all(m['complete_cube'] and not m['tinted'] for m in materials):
        raise ValueError('存在不完整或带色调材质，拒绝导出')

    print('三轴构型通过规则审计；导出标准NBT和Sponge并逐格回读…', flush=True)
    exported = export_dense(grid, geometry.STATES, data['name'], VIEW)
    if exported['block_count'] != check['blocks']:
        raise ValueError('结构导出实体数与体素源不同')
    groups = exported['surface_groups']
    check.update(
        nbt_schem_sha256=exported['hashes'], readback=exported['readback'],
        viewer_surface_faces=sum(len(face) for group in groups for face in group),
        viewer_payload_exact_cell_readback=True,
        source_instance=str(INSTANCE), instance_version=version,
        material_resource_sources=sources, enabled_file_resource_packs=packs,
    )
    check['ordinary_material_namespaces'] = {}
    for state, count in check['palette'].items():
        if state in (geometry.M.PORT, geometry.M.CONTROL):
            continue
        namespace = state.split(':', 1)[0]
        check['ordinary_material_namespaces'][namespace] = check['ordinary_material_namespaces'].get(namespace, 0) + count
    merged_groups, run_lengths, merge_audit = merge_surface_runs(groups, data['size'])
    check.update(viewer_surface_merge=merge_audit, viewer_rendered_quads=merge_audit['rendered_quads'])
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=merged_groups,
                   surfaceRunLengths=run_lengths, blockCount=check['blocks'],
                   materials=materials, audit=check,
                   names={state: state.split(':', 1)[1] for state in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    encoded = base64.b64encode(compressed).decode('ascii')
    (VIEW / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    check.update(viewer_payload_gzip_bytes=len(compressed), viewer_payload_base64_bytes=len(encoded))

    generated = now()
    manifest = dict(
        machine='I37', title=geometry.TITLE, design='三轴世界线干涉测量台',
        target_voltage='WFV', voltage_mapping='V13 / tier27', status='candidate_waiting_user_review',
        approved=False, installed=False, game_verified=False,
        size_xyz=data['size'], size_wdh=[data['size'][0], data['size'][2], data['size'][1]],
        blocks=check['blocks'], unique_materials=check['materials'],
        bounding_box_volume=check['volume'], height=check['height'],
        source_instance=str(INSTANCE), instance_version=version, generated_at=generated,
    )
    check['manifest_status'] = manifest['status']
    save(OUT / 'manifest.json', manifest)
    save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [
        dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
             complete_cube=m['complete_cube'], source=sources.get(m['state'], {}), survival_stage_verified=False)
        for m in materials
    ])
    (OUT / 'index.html').write_text(report(data, check, image=True), encoding='utf-8')
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i37_triaxial_worldline_viewer_20261028.mjs'), str(OUT)],
                   cwd=ROOT, check=True)
    for filename in (
        'build_i37_triaxial_worldline_20261028.py',
        'build_i37_triaxial_worldline_viewer_20261028.mjs',
        'i37_triaxial_worldline_geometry_20261028.py',
        'i37_triaxial_worldline_audit_20261028.py',
        'i34_open_observatory_export_20261027.py',
        'i37_surface_runs_20261027.py',
        'build_i25_world_bubble_observatory_20261025.py',
    ):
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, OUT / filename)
    license_file = ROOT / 'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/i37/Three许可.txt'
    if not license_file.exists():
        license_file = ROOT / 'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/i34/Three许可.txt'
    if license_file.exists():
        shutil.copy2(license_file, OUT / 'Three许可.txt')
    save(LOG / 'package-status.json', dict(
        passed=True, approved=False, installed=False, game_verified=False,
        blocks=check['blocks'], materials=check['materials'], size_xyz=data['size'],
        surface_faces=check['viewer_surface_faces'], rendered_quads=check['viewer_rendered_quads'],
        nbt_schem_sha256=exported['hashes'], generated_at=generated,
    ))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['materials'],
                          size_xyz=data['size'], faces=check['viewer_surface_faces'],
                          quads=check['viewer_rendered_quads']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
