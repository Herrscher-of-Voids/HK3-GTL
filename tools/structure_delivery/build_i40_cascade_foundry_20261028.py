# -*- coding: utf-8 -*-
"""I40标准HTML、真实MC材质与完整结构文件交付。
变更记录 #1（2026-10-28）：新增独立候选交付；不修改正式实例。
"""
import base64
import datetime as dt
import gzip
import html
import json
import shutil
import subprocess
import i40_cascade_foundry_geometry_20261028 as geometry
from i40_cascade_foundry_audit_20261028 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I40_文明奇观材料合成中心_四系贯流合成工场_V1_20261028'
LOG = ROOT / 'logs/i40-cascade-foundry-20261028'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def report(data, check):
    p = check['voltage_progression']
    rows = ''.join(f'<tr><td>{label}</td><td>{p["metrics"][key]:,}</td><td>{p["lower_maxima"][key]["value"]:,}</td><td>+{(p["metrics"][key]/p["lower_maxima"][key]["value"]-1)*100:.1f}%</td></tr>'
        for key, label in [('blocks', '实体方块'), ('materials', '普通材料种类'), ('volume', '实体包围盒体积'), ('height', '实际高度')])
    ports = ''.join(f'<tr><td>{html.escape(x["id"])}</td><td>{x["pos"]}</td><td>{x["face"]}</td></tr>' for x in data['ports'])
    ordinary = check['blocks']-13
    shares = ''.join(f'<li>{ns}：{n:,}块 / {n/ordinary*100:.2f}%</li>' for ns, n in check['ordinary_material_namespaces'].items())
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I40文明奇观材料合成中心</title>
<style>body{{max-width:1260px;margin:35px auto;padding:0 24px;background:#101a29;color:#e9edf5;font:16px/1.8 system-ui}}a{{color:#c9b5dc}}img{{width:100%;border:1px solid #4d405d}}.note{{padding:16px;border-left:3px solid #ac90b5;background:#2a2435}}table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;text-align:left;border-bottom:1px solid #454251}}</style>
<small>HK3GTL · I40 · WFV / V13 / tier27 · 外观候选 V1</small><h1>文明奇观材料合成中心<br>四系贯流合成工场</h1>
<p class="note">{html.escape(data['description'])}</p><p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体方块 · {check['ordinary_materials']}种普通材料，另有2种主控/接口标记 · WFV主体{check['wfv_casing_count']:,}块</p>
<p><a href="i40/三维评审.html">打开MC材质三维评审</a> · <a href="完整预览.png">完整预览图</a> · <a href="材料清单.json">材料清单</a> · <a href="verification.json">核验记录</a></p><img src="完整预览.png" alt="I40四系贯流合成工场完整结构MC材质预览">
<h2>四系分料，四线贯流</h2><p>导能线制造带材和晶片，约束线处理陶瓷与隔离件，重构线形成自组织复材和预制构件，认知线刻写信息载体与传感阵列。每条线分别表达备料、合成、稳定化、分级与按成分回流，只有检测采样可在前侧质检桥共享。认知材料不代表量产意识。</p>
<p>后部圆肩压力塔与八角处理塔采用三层分隔屏蔽和内衬，检修环、斜向加料桥接入炉颈；前部设备长廊以横向辊架、独立介质管与分段冷却罩表达连续生产。12处接口分散嵌入本系机匣和共享质检桥，主控位于整宽第301格，蓝图[300,27,0]。</p>
<h2>正式依据与未验收范围</h2><p>目标电压按已授权映射为WFV，占地表65×81×49为最低要求。RN-WMS起步试片由前级GT/I16制备、I32检测，不要求先用I40或奇观自产材料；I37材料工况记录、I15/I16魂钢及前级介质的正式依赖保持原规划。I37仅在外观制作顺序上留到最后，不移除工艺依赖。</p>
<p>旧provisional一锅四产工单不作为本候选工艺依据。当前只是建筑表达，四系配方、研究、生存获取链、成分回流及游戏运行尚未验收。</p>
<h2>全部较低电压形态的实际比较</h2><p>核对{p['lower_form_count']}种现役低阶形态；同阶与更高阶不强制排序，未批准I37不计入。四项实际指标严格递增：4/4，100%；下表百分比为相对低阶最大值的真实增幅，外观质量仍交由负责人审阅。</p>
<table><tr><th>指标</th><th>I40</th><th>低阶最大值</th><th>增幅</th></tr>{rows}</table>
<h2>实际建材来源</h2><ul>{shares}</ul><p>另计：钻石主控1块，工业接口12块。完整形体、状态与纹理来自GTL增强版{check['instance_version']}当前资源；实际生存获取链单列未验收。</p>
<h2>主控及工艺接口</h2><p>蓝图从0起算；方块格位从1起算。主控北向，正好位于601宽的中轴第301格。接口占位本身不具备真实物品、流体或供能功能。</p><table><tr><th>拟定用途</th><th>蓝图XYZ</th><th>外侧方向</th></tr>{ports}</table>
<p class="note">状态：待审，未批准、未实装。I37留最后；第10批当前0/5，I40未批准不计数。完整NBT与Schematic逐格回读一致，表面合并保留原始方块纹理；这些核验不代表FCL或电脑版运行性能已达标。三场景内存测试按负责人决定留至全部结构完成。</p></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    view = OUT / 'i40'; view.mkdir(exist_ok=True)
    cube, data = geometry.build()
    print('I40几何已生成，核对实体、接口及全部低阶证据…', flush=True)
    check = audit(cube, data)
    version = json.loads((resources.INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2', '实例版本已变化，先复核资源'
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('实体及真实MC资源通过，导出并逐格回读完整NBT/Schematic…', flush=True)
    result = export_dense(cube, geometry.STATES, data['name'], view)
    assert result['block_count'] == check['blocks']
    groups = result['surface_groups']
    check.update(nbt_schem_sha256=result['hashes'], readback=result['readback'],
        viewer_surface_faces=sum(len(face) for group in groups for face in group),
        source_instance=str(resources.INSTANCE), instance_version=version,
        material_resource_sources=sources, enabled_file_resource_packs=packs)
    groups, lengths, merged = merge_surface_runs(groups, data['size'])
    check.update(viewer_surface_merge=merged, viewer_rendered_quads=merged['rendered_quads'])
    check['ordinary_material_namespaces'] = {}
    for state, count in check['palette'].items():
        if state not in (geometry.material.CONTROL, geometry.material.PORT):
            ns = state.split(':')[0]
            check['ordinary_material_namespaces'][ns] = check['ordinary_material_namespaces'].get(ns, 0)+count
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, surfaceRunLengths=lengths,
        blockCount=check['blocks'], materials=materials, audit=check,
        names={s: s.split(':')[1] for s in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(base64.b64encode(compressed).decode('ascii'))+';', encoding='utf-8')
    check['viewer_payload_gzip_bytes'] = len(compressed)
    save(OUT/'manifest.json', dict(data, candidate_version='V1', status='candidate_waiting_user_review',
        approved=False, installed=False, game_verified=False, target_voltage='WFV', voltage_mapping='V13 / tier27',
        blocks=check['blocks'], unique_materials=check['unique_materials'], ordinary_materials=check['ordinary_materials'],
        source_instance=str(resources.INSTANCE), instance_version=version,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT/'verification.json', check)
    save(OUT/'材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'], source=sources.get(m['state'], {}), survival_stage_verified=False) for m in materials])
    save(LOG/'lower-voltage-evidence.json', check['voltage_progression'])
    (OUT/'index.html').write_text(report(data, check), encoding='utf-8')
    subprocess.run(['node', str(ROOT/'tools/structure_delivery/build_i40_cascade_foundry_viewer_20261028.mjs'), str(OUT)], cwd=ROOT, check=True)
    scripts = OUT/'生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in ('i40_cascade_foundry_geometry_20261028.py', 'i40_cascade_foundry_audit_20261028.py',
                     'i40_voltage_progression_20261028.py', 'build_i40_cascade_foundry_20261028.py',
                     'build_i40_cascade_foundry_viewer_20261028.mjs'):
        shutil.copy2(ROOT/'tools/structure_delivery'/filename, scripts/filename)
    save(LOG/'package-status.json', dict(passed=True, approved=False, installed=False, game_verified=False,
        output=str(OUT), size_xyz=data['size'], blocks=check['blocks'], materials=check['unique_materials'],
        surface_faces=check['viewer_surface_faces'], rendered_quads=check['viewer_rendered_quads'],
        payload_bytes=len(compressed), nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'],
        rendered_quads=check['viewer_rendered_quads'], payload_bytes=len(compressed)), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
