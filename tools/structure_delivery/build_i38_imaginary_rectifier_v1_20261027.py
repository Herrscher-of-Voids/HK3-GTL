# -*- coding: utf-8 -*-
"""I38双极换流站：独立候选的完整实体、真实实例贴图和标准HTML交付。
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

import i38_imaginary_rectifier_geometry_v1_20261027 as geometry
from i38_imaginary_rectifier_audit_v1_20261027 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I38_虚数能量整流中枢_双极脉冲换流站_V1_20261027'
LOG = ROOT / 'logs/i38-imaginary-rectifier-v1-20261027'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def report(data, check):
    progress = check['voltage_progression']
    rows = ''.join(f'<tr><td>{label}</td><td>{progress["metrics"][key]:,}</td><td>{progress["lower_maxima"][key]["value"]:,}</td><td>100%</td></tr>'
        for key, label in [('blocks', '实际实体方块'), ('materials', '唯一材料'), ('volume', '实体包围盒体积'), ('height', '实际高度')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I38虚数能量整流中枢V1</title>
<style>body{{max-width:1280px;margin:32px auto;padding:0 22px;background:#111c29;color:#e5edf3;font:16px/1.8 system-ui}}a{{color:#b4d6ee}}img{{width:100%;border:1px solid #40566b}}.note{{padding:16px;border-left:3px solid #92b0ca;background:#233243}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #526072}}</style>
<small>HK3GTL / I38 / IWV · V12 · tier26 / 独立建筑候选V1</small><h1>虚数能量整流中枢 · 双极脉冲换流站</h1>
<p class="note">{html.escape(data['description'])}</p><p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体方块 · {check['unique_materials']}种材料 · IWV主壳{check['iwv_casing_count']:,}块</p>
<p><a href="i38/三维评审.html">打开三维评审</a> · <a href="完整预览.png">完整画面</a> · <a href="材料清单.json">材料用量</a> · <a href="verification.json">实体核验</a></p><img src="完整预览.png" alt="I38双极脉冲换流站完整MC材质预览">
<h2>两条阀列构成整流主体</h2><p>两极各六座串联阀塔，以分级绝缘盘、开敞阀室、冷却立管和检修托盘形成逐级换流设备。顶置母线由阀列本体支撑，前部变压机组承担输入整形的工程表达，后部低位机列组织热交换与回流；两条阀列之间保留贯通维护大道。前端控制室沿中轴嵌入钻石主控与工业接口，不另挂面板，不用四爪围住中央球体。</p>
<h2>正式职能与运行边界</h2><p>I38正式名称为虚数能量整流中枢，对应IWV。I01-4负责能量态崩坏能采集，I38负责HKE整流和合法记账，I41负责文明负载调度，三者职责分开。既有设计以能量态采集结果及调节部件进入整流工艺，交付可记账HKE和调节损耗产物；工艺消耗不能混作无线账户传输损耗，不能因摆好建筑自动获得HKE或免费EU。</p>
<p>RN-HER研究执行规约仍存在暂定内容；解锁不自动充值，不以I38先自充作为进入前提，不把HER完成直接当作全部无线余额可用性。正式供能合同、去重结算、合法来源、工艺材料和研究执行均与本轮建筑审阅分开。</p>
<h2>四项递增与实体核验</h2><p>按正式电压比较41种较低阶已批准形态（38正式＋I34/I35/I36待装），不是按机器编号递增。I37为更高WFV未批准候选，不列入IWV下限；没有要求翻倍。全体六邻接单连通，左右几何及材质严格镜像，主控和10处接口嵌入连续外墙，有背板与五格外侧净空。</p>
<table><tr><th>指标</th><th>I38实际</th><th>低阶最大值</th><th>核验通过率</th></tr>{rows}</table>
<p>主控蓝图[280,20,0]、从1起算格位[281,21,1]，北向/-Z；推荐世界Y=-60，最高实体Y=222。完整NBT和Sponge逐格回读一致；实际实例增强版{check['instance_version']}材料、模型和纹理核验，项目自有方块仅IWV机壳与工业接口占位。钻石主控仅供建筑预览定位，工业接口占位本身不提供物料或供能能力。</p>
<p class="note">建筑几何核验完成，不等于负责人批准或游戏验收；I38未实装，I37也不因继续下一台自动获批。batch-09仍为I34/I35/I36，3/5。全部结构完成后，再在FCL与电脑版分别测试空载、全部摆出、FTB Chunks强加载三场景；本轮没有性能实测。</p></html>'''


def main():
    OUT.mkdir(exist_ok=True, parents=True); LOG.mkdir(exist_ok=True, parents=True)
    view = OUT / 'i38'; view.mkdir(exist_ok=True)
    cube, data = geometry.build(); check = audit(cube, data)
    version = json.loads((resources.INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2', '实例版本变化，先复核资源合同'
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('I38实体及真实资源核验通过，导出完整NBT和Schematic…', flush=True)
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
        approved=False, installed=False, target_voltage='IWV', voltage_mapping='V12 / tier26', blocks=check['blocks'],
        unique_materials=check['unique_materials'], geometry_passed=True, source_instance=str(resources.INSTANCE),
        instance_version=version, generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'], source=sources.get(m['state'], {}), survival_stage_verified=False) for m in materials])
    (OUT / 'index.html').write_text(report(data, check), encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in ['build_i38_imaginary_rectifier_v1_20261027.py', 'i38_imaginary_rectifier_geometry_v1_20261027.py',
        'i38_imaginary_rectifier_audit_v1_20261027.py', 'i38_voltage_progression_20261027.py',
        'build_i38_imaginary_rectifier_viewer_v1_20261027.mjs', 'i34_open_observatory_export_20261027.py',
        'i37_surface_runs_20261027.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i38_imaginary_rectifier_viewer_v1_20261027.mjs'), str(OUT)], cwd=ROOT, check=True)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, blocks=check['blocks'],
        materials=check['unique_materials'], size_xyz=data['size'], surface_faces=check['viewer_surface_faces'],
        rendered_quads=check['viewer_rendered_quads'], nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'], faces=check['viewer_surface_faces']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
