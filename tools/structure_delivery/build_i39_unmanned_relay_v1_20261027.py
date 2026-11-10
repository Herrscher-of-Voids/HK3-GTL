# -*- coding: utf-8 -*-
"""I39无人航路中继站：独立候选的完整实体、真实实例贴图和标准HTML交付。
变更记录 #1（2026-10-27）：删除无；新增独立制作及逐格回读；修改无；
用途：供负责人审阅，不改变批准索引、正式控制器、实例或存档。
"""
import base64
import datetime as dt
import gzip
import html
import json
import shutil
import subprocess

import i39_unmanned_relay_geometry_v1_20261027 as geometry
from i39_unmanned_relay_audit_v1_20261027 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I39_无人跨界航路中继站_偏馈碟阵与双轨整备站_V1_20261027'
LOG = ROOT / 'logs/i39-unmanned-relay-v1-20261027'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def report(data, check):
    progress = check['voltage_progression']
    rows = ''.join(f'<tr><td>{label}</td><td>{progress["metrics"][key]:,}</td><td>{progress["lower_maxima"][key]["value"]:,}</td><td>100%</td></tr>'
        for key, label in [('blocks', '实际实体方块'), ('materials', '唯一材料'), ('volume', '实体包围盒体积'), ('height', '实际高度')])
    p = data['controller']
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I39无人跨界航路中继站V1</title>
<style>body{{max-width:1280px;margin:32px auto;padding:0 22px;background:#111c29;color:#e5edf3;font:16px/1.8 system-ui}}a{{color:#b4d6ee}}img{{width:100%;border:1px solid #40566b}}.note{{padding:16px;border-left:3px solid #92b0ca;background:#233243}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #526072}}</style>
<small>HK3GTL / I39 / ICV · V10 · tier24 / 独立建筑候选V1</small><h1>无人跨界航路中继站 · 偏馈碟阵与双轨整备站</h1>
<p class="note">{html.escape(data['description'])}</p><p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体方块 · {check['unique_materials']}种材料 · ICV主壳{check['icv_casing_count']:,}块</p>
<p><a href="i39/三维评审.html">打开三维评审</a> · <a href="完整预览.png">完整画面</a> · <a href="材料清单.json">材料用量</a> · <a href="verification.json">实体核验</a></p><img src="完整预览.png" alt="I39偏馈碟阵与双轨整备站完整MC材质预览">
<p><a href="背面支撑预览.png">背面轴座与支撑</a> · <a href="主控材质近景.png">居中主控与真实MC材质近景</a></p>
<h2>碟面、轴座与发射返航轨道</h2><p>后部倾斜抛物面天线由弧形加强肋、落地轴座和偏馈支臂形成独立通信轮廓；前场分设发射与返航设备轨道，低位整备库、维护管线与中轴调度楼形成运行分区。以ICV机壳主导主体，金属碟面与绝缘端子分别表达信号反射和设备隔离，主控接口直接嵌入建筑外墙。</p>
<h2>正式职能与边界</h2><p>负责多目标无人任务排程、跨界装置返航交接、航路维护和异常恢复；扩展I26既有调度能力，I26首轮任务不依赖I39。输入已授权的目标信标、装置任务及维护物资，交付任务状态、返航装置及维护产物；不能凭中继站额外增加资源倍率、接管别队装置、刷新目标计数或凭空获得物资。</p>
<p>ICV映射不是免费调度权限。持续供能、服务端团队授权、幂等请求、离线和重启恢复、失效处理及生存获取须在正式逻辑中单独验收。天线和轨道为建筑表达，不以HTML效果冒充实际传送或运行。</p>
<h2>按电压核验四项递增</h2><p>比较35种ICV以下已批准形态；同阶与高阶不作编号递增，I38的IWV规模不是本机下限。全部六邻接单连通、左右几何和材料镜像，主控和10处接口具备连续外墙、内背板与五格外侧净空。</p>
<table><tr><th>指标</th><th>I39实际</th><th>低阶最大值</th><th>核验通过率</th></tr>{rows}</table>
<p>主控蓝图{p}、从1起算格位{[n+1 for n in p]}，北向/-Z，整宽第{p[0]+1}格。完整NBT和Schematic逐格回读一致；实际增强版{check['instance_version']}材料、模型和纹理已核验。钻石标主控，通用工业块标接口，均不代替正式控制器和仓室能力。</p>
<p class="note">I38 V1已批准归档，batch-09为I34 V2、I35 V3、I36 V1、I38 V1，4/5；I37未批准。本I39待审未实装，获批准后才满足五台接入条件。全部结构完成后再开展FCL与电脑版空载、全部摆出、FTB Chunks强加载三场景实测，本轮没有性能实测。</p></html>'''


def main():
    OUT.mkdir(exist_ok=True, parents=True); LOG.mkdir(exist_ok=True, parents=True)
    view = OUT / 'i39'; view.mkdir(exist_ok=True)
    cube, data = geometry.build(); check = audit(cube, data)
    version = json.loads((resources.INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2', '实例版本变化，先复核资源合同'
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('I39实体及真实资源核验通过，导出完整NBT和Schematic…', flush=True)
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
    groups, lengths, merged = merge_surface_runs(groups, data['size'])
    check.update(viewer_surface_merge=merged, viewer_rendered_quads=merged['rendered_quads'])
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, surfaceRunLengths=lengths,
        blockCount=check['blocks'], materials=materials, audit=check, names={s: s.split(':')[1] for s in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    encoded = base64.b64encode(compressed).decode('ascii')
    (view / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    check.update(viewer_payload_gzip_bytes=len(compressed), viewer_payload_base64_bytes=len(encoded))
    save(OUT / 'manifest.json', dict(data, candidate_version='V1', status='candidate_waiting_user_review',
        approved=False, installed=False, target_voltage='ICV', voltage_mapping='V10 / tier24', blocks=check['blocks'],
        unique_materials=check['unique_materials'], geometry_passed=True, source_instance=str(resources.INSTANCE),
        instance_version=version, generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'], source=sources.get(m['state'], {}), survival_stage_verified=False) for m in materials])
    (OUT / 'index.html').write_text(report(data, check), encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in ['build_i39_unmanned_relay_v1_20261027.py', 'i39_unmanned_relay_geometry_v1_20261027.py',
        'i39_unmanned_relay_audit_v1_20261027.py', 'i39_voltage_progression_20261027.py',
        'build_i39_unmanned_relay_viewer_v1_20261027.mjs', 'i34_open_observatory_export_20261027.py',
        'i37_surface_runs_20261027.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i39_unmanned_relay_viewer_v1_20261027.mjs'), str(OUT)], cwd=ROOT, check=True)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, blocks=check['blocks'],
        materials=check['unique_materials'], size_xyz=data['size'], surface_faces=check['viewer_surface_faces'],
        rendered_quads=check['viewer_rendered_quads'], nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'], faces=check['viewer_surface_faces']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
