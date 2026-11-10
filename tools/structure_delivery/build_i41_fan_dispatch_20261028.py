# -*- coding: utf-8 -*-
"""I41标准HTML、真实MC材质与完整结构文件交付。
变更记录 #1（2026-10-28）：新增独立候选交付；不修改正式实例。
"""
import base64
import datetime as dt
import gzip
import html
import json
import shutil
import subprocess
import i41_fan_dispatch_geometry_20261028 as geometry
from i41_fan_dispatch_audit_20261028 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I41_文明能源调度中枢_弧幕母线与扇形负载港_V1_20261028'
LOG = ROOT / 'logs/i41-fan-dispatch-20261028'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def report(data, check):
    p = check['voltage_progression']
    rows = ''.join(f'<tr><td>{label}</td><td>{p["metrics"][key]:,}</td><td>{p["lower_maxima"][key]["value"]:,}</td><td>+{(p["metrics"][key]/p["lower_maxima"][key]["value"]-1)*100:.2f}%</td></tr>'
        for key, label in [('blocks','实际实体'),('materials','普通材料种类'),('volume','实体包围盒体积'),('height','实际高度')])
    ports = ''.join(f'<tr><td>{html.escape(x["id"])}</td><td>{x["pos"]}</td><td>{x["face"]}</td></tr>' for x in data['ports'])
    shares = ''.join(f'<li>{ns}：{n:,}块 / {n/(check["blocks"]-7)*100:.2f}%</li>' for ns,n in check['ordinary_material_namespaces'].items())
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I41文明能源调度中枢</title>
<style>body{{max-width:1280px;margin:36px auto;padding:0 24px;background:#111b28;color:#e6edf5;font:16px/1.8 system-ui}}a{{color:#a8d2e9}}img{{width:100%;border:1px solid #4a5566}}.note{{padding:16px;background:#213344;border-left:3px solid #90b8c8}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #465568}}</style>
<small>HK3GTL · I41 · IWV / V12 / tier26 · 独立外观候选{data.get('candidate_version', 'V1')}</small><h1>文明能源调度中枢<br>{html.escape(data['title'].split(' · ', 1)[-1])}</h1>
<p class="note">{html.escape(data['description'])}</p><p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}实体 · {check['ordinary_materials']}种普通材料，另有主控/接口2种标记 · IWV主壳{check['iwv_casing_count']:,}块</p>
<p><a href="i41/三维评审.html">打开MC材质三维评审</a> · <a href="完整预览.png">完整画面</a> · <a href="后部母线.png">后部母线</a> · <a href="主控材质近景.png">居中主控近景</a> · <a href="verification.json">核验记录</a></p><img src="完整预览.png" alt="I41弧幕母线与扇形负载港完整MC材质预览">
<h2>从登记到回执的调度设施</h2><p>六路测控廊呈扇形接入后部弧幕主脊，廊内设负载状态机架、隔离保护及维护空间；弧幕由多层屏蔽、测控设备与连续检修层组成。前侧调度大厅承接登记、查看、授权手动开停，主控齐平嵌入整宽中轴第296格，蓝图[295,27,0]。建筑中的母线表达设备拓扑，不代表所有无线用能必须经过本机。</p>
<p>不设置世界泡、四爪托举或孤立增高塔。实际285格高度来自连续弧幕主脊；宽591、长471来自真实设备与设备基础，不扩张空气范围。</p>
<h2>职责、授权与研究边界</h2><p>I01-4负责能量态采集，I38负责HKE整流与合法记账，I41只负责文明负载调度。输入真实I38入账记录、已可用HW负载与绑定人授权；输出调度/运行回执、历史与异常记录。I41不造能源、不为账户充值、不重复结算、不接管未授权机器，也不新增传输距离、容量或吞吐限制。</p>
<p>RN-CED只开放基础登记、查看、授权手动开停。RN-ELC并以CED与WME为前置后，才开放优先级和告警；不能让首机默认具备自动排程。个人UUID账本不会因团队研究合并，研究许可不等于账户/机器授权。完整运行、研究与生存获取均须后续独立验收。</p>
<h2>按电压比较全部低阶</h2><p>42种IWV以下已批准现役形态重新核对源文件SHA256；复用I40本轮已逐格统计的实体证据。I38与I01-4同为IWV，不强制编号递增；I40为WFV，排除于下限比较，并确认本机四项指标仍低于其已批准值。未批准I37不计入。四项数值严格递增4/4，100%；外观质量由负责人审阅。</p><table><tr><th>指标</th><th>I41</th><th>低阶最大值</th><th>增幅</th></tr>{rows}</table>
<h2>建材与接口</h2><ul>{shares}</ul><p>另计钻石主控1块、工业接口6块。材料来自当前增强版{check['instance_version']}，模型、完整形体、状态与纹理已核对；未将它们的完整生存获取链标为通过。主控与接口嵌入调度大厅连续外墙，具备内背板和5格外侧净空；占位块没有真实仓室功能。</p><table><tr><th>拟定用途</th><th>蓝图XYZ</th><th>外侧方向</th></tr>{ports}</table>
<p class="note">I40 V1已批准并归入batch-10第1/5台，未满批未部署。I41为待审候选，未批准、未实装，不计入批准数量。I37继续最后制作。完整NBT/Schematic逐格回读一致；全部结构完成后再开展FCL和电脑版空载、全部摆出、FTB Chunks强加载三场景内存测试。</p></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    view = OUT / 'i41'; view.mkdir(exist_ok=True)
    cube, data = geometry.build()
    print('I41几何已生成，核对实体、接口及全部低阶证据…', flush=True)
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
    save(OUT/'manifest.json', dict(data, candidate_version=data.get('candidate_version', 'V1'), status='candidate_waiting_user_review',
        approved=False, installed=False, game_verified=False, target_voltage='IWV', voltage_mapping='V12 / tier26',
        blocks=check['blocks'], unique_materials=check['unique_materials'], ordinary_materials=check['ordinary_materials'],
        source_instance=str(resources.INSTANCE), instance_version=version,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT/'verification.json', check)
    save(OUT/'材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'], source=sources.get(m['state'], {}), survival_stage_verified=False) for m in materials])
    save(LOG/'lower-voltage-evidence.json', check['voltage_progression'])
    (OUT/'index.html').write_text(report(data, check), encoding='utf-8')
    subprocess.run(['node', str(ROOT/'tools/structure_delivery/build_i41_fan_dispatch_viewer_20261028.mjs'), str(OUT)], cwd=ROOT, check=True)
    scripts = OUT/'生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in ('i41_fan_dispatch_geometry_20261028.py', 'i41_fan_dispatch_audit_20261028.py',
                     'i41_voltage_progression_20261028.py', 'build_i41_fan_dispatch_20261028.py',
                     'build_i41_fan_dispatch_viewer_20261028.mjs'):
        shutil.copy2(ROOT/'tools/structure_delivery'/filename, scripts/filename)
    save(LOG/'package-status.json', dict(passed=True, approved=False, installed=False, game_verified=False,
        output=str(OUT), size_xyz=data['size'], blocks=check['blocks'], materials=check['unique_materials'],
        surface_faces=check['viewer_surface_faces'], rendered_quads=check['viewer_rendered_quads'],
        payload_bytes=len(compressed), nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'],
        rendered_quads=check['viewer_rendered_quads'], payload_bytes=len(compressed)), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
