# -*- coding: utf-8 -*-
"""I37完整实体导出、真实实例材质与标准HTML候选打包。"""
import base64
import datetime as dt
import gzip
import html
import json
import shutil
import subprocess

import i37_world_maintenance_geometry_v1_20261027 as geometry
from i37_world_maintenance_audit_v1_20261027 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I37_世界维系试验平台_开卷式层界负载台_V1_20261027'
LOG = ROOT / 'logs/i37-world-maintenance-v1-20261027'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def report(data, check):
    progression = check['voltage_progression']
    rows = ''.join(f'<tr><td>{label}</td><td>{progression["metrics"][key]:,}</td><td>{progression["lower_maxima"][key]["value"]:,}</td><td>通过</td></tr>'
        for key, label in [('blocks', '实际实体方块'), ('materials', '唯一材料'), ('volume', '实体包围盒体积'), ('height', '实际高度')])
    total = sum(check['ordinary_material_namespaces'].values())
    sources = '；'.join(f'{key} {value:,}块（{value / total:.2%}）' for key, value in check['ordinary_material_namespaces'].items())
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I37世界维系试验平台V1</title>
<style>body{{max-width:1280px;margin:32px auto;padding:0 22px;background:#111c29;color:#e5edf3;font:16px/1.8 system-ui}}a{{color:#ddbbcb}}img{{max-width:100%}}.note{{padding:16px;border-left:3px solid #b58a9e;background:#302a36}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #526072}}</style>
<small>HK3GTL / I37 / WFV · V13 · tier27 / 独立建筑候选V1</small><h1>世界维系试验平台 · 开卷式层界负载台</h1>
<p class="note">{html.escape(data['description'])}</p><p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体方块 · {check['unique_materials']}种材料 · WFV主壳{check['wfv_casing_count']:,}块</p>
<p><a href="i37/三维评审.html">打开三维评审</a> · <a href="完整预览.png">完整画面</a> · <a href="材料清单.json">材料用量</a> · <a href="verification.json">实体核验</a></p><img src="完整预览.png" alt="I37开卷式层界负载台完整预览">
<h2>受控世界样件的分层试验</h2><p>酒红灰WFV斜翼沿长轴分成隔离舱室，翼面保留试样窗口、细光尺与阶梯维护廊；翼背六组分段施载缸连接独立接地承座。中央隔离承力脊收纳供能、介质、失效隔离与测量设备，前端连续房体内交接真实样件、资料和报告。没有中央世界球体，整个装置的实验层本身构成主体轮廓。</p>
<p>输入I35真实合格锚组件与状态证据、既有空间模块/试验样件、稳定介质及连续供能；I36现实稳定能力、I38供能和I41负载记录支撑试验。进行锚定与供能联合维系、不同负载持续性、停止/恢复及失效分析。合格样件、维系报告与用后介质分别交付，记录不能替代真实材料。</p>
<h2>研究和运行边界</h2><p>RN-WME实际前置为RN-IAA、RN-CED、RN-RAT、RN-LTA、RN-DKE、RN-SWS；研究执行器为I33。I32模型分析后制备前级局部维系试件，首实验不能要求I37先运行或先取得奇观材料。成功证据需真实局部扰动响应、停止/恢复及输入/能流记录。</p>
<p>旧industrial_world_maintenance仍为provisional、tier24/ICV工单，不能据此把本轮WFV映射降档。现实维系运行事实和研究完成分开；建筑摆放不自动发world_maintenance事实，不自动完成二审、文明升级或I43工程验收。失败只反馈缺项或装置内试件失效，不破坏玩家世界，不制造世界、免费能源或维度通行。</p>
<h2>量化核验</h2><p>按电压比较39种正式低阶形态及I34/I35/I36三台已批准待装结构，共42种；四项递增检查100%通过，11处主控与接口检查100%通过。已批准待装结构仍纳入比较，不能以未实装为由忽略I35的高度及用量。</p>
<table><tr><th>指标</th><th>I37</th><th>低阶最大值</th><th>结果</th></tr>{rows}</table>
<p>全体单连通且左右几何、材质严格镜像。主控[300,24,8]北向、整宽第301格；10个工业接口占位齐平嵌入前端控制室，有内背板及五格外侧净空。推荐世界Y=-60，最高实体Y=230；高度由斜翼自然达到，无附加凑高塔。</p>
<p>普通建材来源：{sources}。钻石主控1块、工业接口10块另列。实例增强版2.9.2的实际模型、完整立方体及材质已核验；材料及研究的完整生存获取链未在本轮验收。</p>
<p class="note">I36 V1已确认归档，batch-09为I34、I35、I36，3/5，还差两台。未达到五台，不部署；本I37候选尚未批准，不计批次。正式已装41形态。正式控制器、Pattern、配方、工况、覆盖/能量衔接、研究及游戏运行另验。</p></html>'''


def main():
    OUT.mkdir(exist_ok=True, parents=True); LOG.mkdir(exist_ok=True, parents=True)
    view = OUT / 'i37'; view.mkdir(exist_ok=True)
    cube, data = geometry.build(); check = audit(cube, data)
    version = json.loads((resources.INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('I37实体核验通过，完整导出并逐格回读…', flush=True)
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
    groups, run_lengths, run_check = merge_surface_runs(groups, data['size'])
    check.update(viewer_surface_merge=run_check, viewer_rendered_quads=run_check['rendered_quads'])
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, surfaceRunLengths=run_lengths, blockCount=check['blocks'], materials=materials,
        audit=check, names={s: s.split(':')[1] for s in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    encoded = base64.b64encode(compressed).decode('ascii')
    (view / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    check.update(viewer_payload_gzip_bytes=len(compressed), viewer_payload_base64_bytes=len(encoded))
    manifest = dict(data, candidate_version='V1', status='candidate_waiting_user_review', approved=False, installed=False,
        target_voltage='WFV', voltage_mapping='V13 / tier27', blocks=check['blocks'], unique_materials=check['unique_materials'],
        geometry_passed=True, source_instance=str(resources.INSTANCE), instance_version=version,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds'))
    save(OUT / 'manifest.json', manifest); save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'], source=sources.get(m['state'], {}), survival_stage_verified=False) for m in materials])
    (OUT / 'index.html').write_text(report(data, check), encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in ['build_i37_world_maintenance_v1_20261027.py', 'i37_world_maintenance_geometry_v1_20261027.py',
        'i37_world_maintenance_audit_v1_20261027.py', 'build_i37_world_maintenance_viewer_v1_20261027.mjs',
        'i34_open_observatory_export_20261027.py', 'i37_surface_runs_20261027.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i37_world_maintenance_viewer_v1_20261027.mjs'), str(OUT)], cwd=ROOT, check=True)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, blocks=check['blocks'],
        materials=check['unique_materials'], size_xyz=data['size'], surface_faces=check['viewer_surface_faces'], nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'], faces=check['viewer_surface_faces']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
