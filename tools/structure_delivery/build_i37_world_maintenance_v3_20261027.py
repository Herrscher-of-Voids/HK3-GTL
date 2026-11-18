# -*- coding: utf-8 -*-
"""I37 V3完整导出及真实材质HTML候选；旧V2、正式资源和实例只读。"""
import base64
import datetime as dt
import gzip
import html
import json
import hashlib
from pathlib import Path
import shutil
import subprocess

import i37_world_maintenance_geometry_v3_20261027 as geometry
from i37_world_maintenance_audit_v3_20261027 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I37_世界维系试验平台_恒界精密试验机_轻量机身与逐格材质_V3_20261027'
LOG = ROOT / 'logs/i37-world-maintenance-v3-20261027'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def source_state():
    old = ROOT / 'deliveries/I37_世界维系试验平台_恒界精密试验机_V2_20261027'
    paths = [path for path in old.rglob('*') if path.is_file()]
    paths += [ROOT / 'tools/structure_delivery' / name for name in [
        'build_i37_world_maintenance_v2_20261027.py', 'i37_world_maintenance_geometry_v2_20261027.py',
        'i37_world_maintenance_audit_v2_20261027.py', 'build_i37_world_maintenance_viewer_v2_20261027.mjs',
        'i34_open_observatory_export_20261027.py', 'i37_surface_runs_20261027.py']]
    for directory, pattern in [('structures/approved', '*'), ('approved_architecture', '*.json'),
                               ('structures/approved_preview', '*.bin.gz')]:
        paths += [path for path in (ROOT / 'src/main/resources/data/hk3gtl' / directory).glob(pattern) if path.is_file()]
    paths += [ROOT / 'deliveries/多方块确认归档/当前归档索引.json',
        ROOT / 'logs/batch09-install-20261027/deployment.json', resources.INSTANCE / 'mods/HK3GTL-内测5.jar']
    return {str(path): digest(path) for path in paths}


def deployment_contract():
    path = ROOT / 'logs/batch09-install-20261027/deployment.json'
    receipt = json.loads(path.read_text(encoding='utf-8'))
    assert receipt['status'] == 'installed' and receipt['revision'] == 181 and receipt['formal_shapes'] == 46
    assert digest(receipt['target']) == receipt['sha256']
    index = json.loads((ROOT / 'deliveries/多方块确认归档/当前归档索引.json').read_text(encoding='utf-8'))
    assert index['formal_structure_forms'] == 46
    assert index['pending_batch']['id'] == 'batch-10' and index['pending_batch']['count'] == 0
    assert not any(entry['id'] == 'I37' for entry in index['entries'])
    return dict(receipt=str(path.relative_to(ROOT)), receipt_sha256=digest(path), revision=181,
        instance_jar_sha256=receipt['sha256'], installed_at=receipt['installed_at_hong_kong'],
        formal_shapes=46, pending_batch='batch-10', pending_count=0, game_verified=receipt['game_verified'])


def report(data, check):
    progression = check['voltage_progression']
    rows = ''.join(f'<tr><td>{label}</td><td>{progression["metrics"][key]:,}</td><td>{progression["lower_maxima"][key]["value"]:,}</td><td>{"100%" if progression["passes"][key] else "0%"}</td></tr>'
        for key, label in [('blocks', '实际实体方块'), ('materials', '唯一材料'), ('volume', '实体包围盒体积'), ('height', '实际高度')])
    total = sum(check['ordinary_material_namespaces'].values())
    sources = '；'.join(f'{key} {value:,}块（{value / total:.2%}）' for key, value in check['ordinary_material_namespaces'].items())
    old = json.loads((ROOT / 'deliveries/I37_世界维系试验平台_恒界精密试验机_V2_20261027/verification.json').read_text(encoding='utf-8'))
    reduction = 1 - check['blocks'] / old['blocks']
    deployed = check['current_deployment']
    controller = data['controller']
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I37世界维系试验平台V3</title>
<style>body{{max-width:1280px;margin:32px auto;padding:0 22px;background:#111c29;color:#e5edf3;font:16px/1.8 system-ui}}a{{color:#ddbbcb}}img{{max-width:100%}}.note{{padding:16px;border-left:3px solid #b58a9e;background:#302a36}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #526072}}</style>
<small>HK3GTL / I37 / WFV · V13 · tier27 / 独立建筑候选V3</small><h1>世界维系试验平台 · 恒界精密试验机</h1>
<p class="note">{html.escape(data['description'])}</p><p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体方块 · {check['unique_materials']}种材料 · WFV主壳{check['wfv_casing_count']:,}块</p>
<p><a href="i37/三维评审.html">打开交互式三维评审</a> · <a href="材料清单.json">材料用量</a> · <a href="verification.json">实体核验</a></p>
<h2>精密试验设备的工程布局</h2><p>WFV主机壳构成纵向一体的机身，白色分块盖板对应可拆检修区，深色垫框包住实际观察玻璃。前端为双侧样件交换仓和中央测控单元，中央高机舱收纳两柱计量龙门、测量头、夹具及双轨移动试样台，后部较低机柜集中处理供能、介质回流与温控。箱式隔振床身承载整机，舱内两侧保留维护踏道。精密机床与EUV设备仅作为工程外观参考，本机职责仍是受控世界维系试验。</p>
<p>输入I35真实合格锚组件与状态证据、既有空间模块/试验样件、稳定介质及连续供能；I36现实稳定能力、I38供能和I41负载记录支撑试验。进行锚定与供能联合维系、不同负载持续性、停止/恢复及失效分析。合格样件、维系报告与用后介质分别交付，记录不能替代真实材料。</p>
<p>V3保留完整轮廓、试验设备与维护空间，削减无必要的内部实心填充。V2为{old['blocks']:,}块，本V3为{check['blocks']:,}块，减少{reduction:.1%}。此处为实体减材，不将HTML绘制优化当作FCL或游戏性能实测。</p>
<h2>逐格MC材质</h2><p>使用增强版2.9.2实际模型及纹理；外露面连续合并后仍逐格重复贴图，保持表面逐格等价，近景放大使用最近邻，远景使用MIP缩小及各向异性过滤缓解条纹。查看器静止按需重绘。全景受屏幕像素限制，近景用于检查单格纹理；隐藏材质与剖切不补绘内部截面。</p>
<h2>研究和运行边界</h2><p>RN-WME实际前置为RN-IAA、RN-CED、RN-RAT、RN-LTA、RN-DKE、RN-SWS；研究执行器为I33。I32模型分析后制备前级局部维系试件，首实验不能要求I37先运行或先取得奇观材料。成功证据需真实局部扰动响应、停止/恢复及输入/能流记录。</p>
<p>旧industrial_world_maintenance仍为provisional、tier24/ICV工单，不能据此把本轮WFV映射降档。现实维系运行事实和研究完成分开；建筑摆放不自动发world_maintenance事实，不自动完成二审、文明升级或I43工程验收。失败只反馈缺项或装置内试件失效，不破坏玩家世界，不制造世界、免费能源或维度通行。</p>
<h2>量化核验</h2><p>当前46种正式形态已部署，其中44种电压低于WFV；按实际电压比较实体数、材料种类、包围盒体积和高度，同阶与更高阶不按编号强行递增。结果来自本次实体审核，不能以HTML效果代替游戏验收。</p>
<table><tr><th>指标</th><th>I37</th><th>低阶最大值</th><th>结果</th></tr>{rows}</table>
<p>全体单连通且左右几何、材质严格镜像。主控{controller}北向、整宽第{controller[0]+1}格；10个工业接口占位齐平嵌入前端机身连续面，有内背板及五格外侧净空。推荐世界Y=-60，最高实体Y={-60+data['size'][1]-1}；最高处为主工作舱屋盖。</p>
<p>普通建材来源：{sources}。钻石主控1块、工业接口10块另列。实例增强版2.9.2的实际模型、完整立方体及材质已核验；材料及研究的完整生存获取链未在本轮验收。</p>
<p>本次仅新增V3；旧V2及正式资源保留原字节。候选尚未批准、未实装，不计入批准批次。</p><p class="note">第9批I34 V2、I35 V3、I36 V1、I38 V1、I39 V1已部署为r181，正式形态46种；新batch-10为0/5。真实部署收据：<a href="../../{Path(deployed['receipt']).as_posix()}">{Path(deployed['receipt']).as_posix()}</a>，实例JAR SHA256：{deployed['instance_jar_sha256']}。该部署的游戏运行仍未验收。正式控制器、Pattern、工艺、材料与研究完整生存链及FCL/电脑版三场景内存另验。</p></html>'''


def main():
    OUT.mkdir(exist_ok=True, parents=True); LOG.mkdir(exist_ok=True, parents=True)
    view = OUT / 'i37'; view.mkdir(exist_ok=True)
    viewer = ROOT / 'tools/structure_delivery/build_i37_world_maintenance_viewer_v3_20261027.mjs'
    assert viewer.is_file(), 'V3查看器未就绪，不开始完整生成'
    old_hash = source_state()
    save(LOG / 'source_state_old_hash.json', dict(scope='旧V2、共享工具、46正式结构与预览、批准索引和已部署实例', sha256=old_hash))
    deployed = deployment_contract()
    cube, data = geometry.build(); check = audit(cube, data)
    check.update(current_deployment=deployed, source_state_old_hash=old_hash)
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
    manifest = dict(data, candidate_version='V3', status='candidate_waiting_user_review', approved=False, installed=False,
        target_voltage='WFV', voltage_mapping='V13 / tier27', blocks=check['blocks'], unique_materials=check['unique_materials'],
        geometry_passed=True, source_instance=str(resources.INSTANCE), instance_version=version,
        current_deployment=deployed, source_state_old_hash=old_hash,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds'))
    save(OUT / 'manifest.json', manifest); save(OUT / 'verification.json', check)
    save(OUT / '资源来源.json', dict(instance=str(resources.INSTANCE), instance_version=version,
        project_resources='src/main/resources', resources=sources, enabled_packs=packs))
    save(OUT / '材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'], source=sources.get(m['state'], {}), survival_stage_verified=False) for m in materials])
    (OUT / 'index.html').write_text(report(data, check), encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in ['build_i37_world_maintenance_v3_20261027.py', 'i37_world_maintenance_geometry_v3_20261027.py',
        'i37_world_maintenance_audit_v3_20261027.py', 'build_i37_world_maintenance_viewer_v3_20261027.mjs',
        'i34_open_observatory_export_20261027.py', 'i37_surface_runs_20261027.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i37_world_maintenance_viewer_v3_20261027.mjs'), str(OUT)], cwd=ROOT, check=True)
    assert all(digest(path) == old_digest for path, old_digest in old_hash.items()), '旧候选或正式源状态被修改'
    save(LOG / 'source-state-verification.json', dict(passed=True, preserved_files=len(old_hash), all_old_hashes_unchanged=True))
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, blocks=check['blocks'],
        materials=check['unique_materials'], size_xyz=data['size'], surface_faces=check['viewer_surface_faces'],
        rendered_quads=check['viewer_rendered_quads'], nbt_schem_sha256=result['hashes'], current_deployment=deployed,
        source_state_unchanged=True, game_verified=False))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'], faces=check['viewer_surface_faces']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
