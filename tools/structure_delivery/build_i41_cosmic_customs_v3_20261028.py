# -*- coding: utf-8 -*-
"""导出I41宇宙海关候选：真实材质、完整结构及独立HTML。

变更记录 #1（2026-10-28）：只新增V3候选，保留历史和游戏实例。
"""
import base64
import datetime as dt
import gzip
import html
import json
import shutil
import subprocess
import sys
import i41_cosmic_customs_geometry_v3_20261028 as geometry
import i41_fan_dispatch_audit_20261028 as checks
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT=geometry.ROOT
OUT=ROOT/'deliveries/I41_文明能源调度中枢_宇宙海关与十二港约束环城_V3_20261028'
LOG=ROOT/'logs/i41-cosmic-customs-v3-20261028'


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def report(data,check):
    esc=html.escape
    rows=''.join(f'<tr><td>{esc(state)}</td><td>{n:,}</td><td>{esc(geometry.ROLES[state])}</td></tr>' for state,n in check['palette'].items())
    p=check['voltage_progression']
    metrics=''.join(f'<tr><td>{name}</td><td>{p["metrics"][key]:,}</td><td>{p["lower_maxima"][key]["value"]:,}</td></tr>' for key,name in [('blocks','实体方块'),('materials','普通材料种类'),('volume','实体包围盒体积'),('height','高度')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I41 V3 · 宇宙海关与十二港约束环城</title><style>
body{{max-width:1320px;margin:32px auto;padding:0 24px;background:#111b28;color:#e5edf6;font:16px/1.8 system-ui}}h1{{line-height:1.3}}a{{color:#9adce4}}.note{{padding:16px;border-left:4px solid #bea97d;background:#27303d}}img{{width:100%;background:#111b28}}table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;border-bottom:1px solid #425466;padding:9px;overflow-wrap:anywhere}}.links{{display:flex;gap:18px;flex-wrap:wrap}}code{{overflow-wrap:anywhere}}</style>
<small>HK3GTL · I41 · IWV / V12 / tier26 · V3独立待审候选</small><h1>文明能源调度中枢<br>宇宙海关与十二港约束环城</h1>
<p class="note">按本轮“宇宙能源港＋调度法庭＋约束监狱＋熵债清算所”概念制作。529×529×289（宽×长×高），{check['blocks']:,}个真实实体方块，41种普通材料。十二个城区围绕中央黑色世界泡约束笼分层展开，能源廊连接上下配平与熵流环；主控嵌入正前方调度大厅的中轴外墙。</p>
<div class="links"><a href="i41/三维评审.html">打开真实MC材质三维评审</a><a href="完整预览.png">完整预览</a><a href="后部母线.png">后方环城</a><a href="主控材质近景.png">主控近景</a><a href="verification.json">静态核验</a></div><img src="完整预览.png" alt="I41宇宙海关环城完整MC材质预览">
<h2>从远景到近景</h2><p>外轮廓由十二片高低不同的舱室城区、上部相位配平环与斜向承力脊组成；中央保持贯通空腔。正球形黑色展示核由黑色纵栅、多层锁环和三道子午框约束，少量紫色节点强调相位。窄青色能源河道以铜护岸连接城区与约束笼，避免整圈建筑轮流换色。</p>
<p>调度法庭、接驳泊位、测控城区、熵流监测清算设施、跨维协议城区、无人维护港和回执档案馆承担不同造型职责；所有41种普通材料均用于实际构件，不循环摆放材料盒。IWV机壳是数量最多的单项材料。</p>
<h2>主控、接口与完整建筑</h2><p>主控原始XYZ为<code>{data['controller']}</code>，整宽第{data['controller'][0]+1}格。钻石块只标记主控，六处工业方块只标记计划接口；均齐平嵌入连续外墙，有内背板及外侧净空。整座六邻接连通；预览、NBT和Schematic来自同一份完整几何，逐格回读核对一致。</p>
<h2>电压递进核对</h2><table><tr><th>指标</th><th>I41 V3</th><th>较低电压已批准最大值</th></tr>{metrics}</table><p>42个较低阶现役形态的源文件身份按既有逐格审计证据复核；同阶I38与未批I37不混入下限，高阶已批准I40仍在四项指标上领先。高度来自连续配平环及承力系统，没有脱节增高塔。</p>
<h2>职责与验收边界</h2><p class="note">I41正式职责仍是授权负载登记、调度、历史与异常回执。宇宙展示核、约束笼、熵流池和清算法庭是本轮建筑隐喻，不新增捕获、能源生产、账户充值、熵债费用或容量／距离限制。12个内部建筑分区不等于新增12个正式控制器。未批准、未接入正式Pattern或游戏实例；I40仍为本批1/5，I37留最后。</p>
<p>渲染仅合并相同材质连续外露面，纹理逐格重复，使用实例真实材质；没有将建筑替换为纯色模型。浏览器预览不是游戏RAM验收，也没有实现新的分区检测或区块休眠。终极终端和8GB运行RAM优化仍按独立工程方案推进。</p>
<h2>实际材料与构件职责</h2><table><tr><th>方块状态</th><th>数量</th><th>构件职责</th></tr>{rows}</table>
<p><a href="../I41_文明能源调度中枢_铜母线与分区材质修订_V2_20261028/index.html">保留的V2</a> · <a href="../../doc/HK3GTL-内测5/完整对话归档/2026-10-28_22-58-06_I41宇宙能源港概念试作授权_55a71ae9d4.html">本轮原文</a></p>
<footer>变更记录 #1 · 2026-10-28：新增宇宙海关与十二港约束环城V3独立候选；保留V1/V2，未修改实例、存档或批准索引。</footer></html>'''


def main():
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
    view=OUT/'i41';view.mkdir(exist_ok=True)
    print('生成I41宇宙海关几何并检查连通性与递进…',flush=True)
    cube,data=geometry.build()
    checks.geometry=geometry
    check=checks.audit(cube,data)
    check['material_count_basis']='43种含主控与接口标记；普通材料41种。'
    check['checks']=[
        '十二港空心环城与中央约束笼为独立新几何，实际边界达到下限。',
        'IWV为最大单项；仅IWV机壳与工业接口两类项目自有建材。',
        '整座六邻接连通；主控居中、六接口齐平，有内背板及外侧净空。',
        '约束笼和清算设施仅建筑隐喻，不改变I41正式调度职责。']
    version=json.loads((resources.INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version=='2.9.2'
    materials,sources,packs=resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('真实材质及静态核验通过，导出完整结构…',flush=True)
    result=export_dense(cube,geometry.STATES,data['name'],view)
    assert result['block_count']==check['blocks']
    raw=result['surface_groups']
    check.update(nbt_schem_sha256=result['hashes'],readback=result['readback'],
        viewer_surface_faces=sum(len(f) for g in raw for f in g),source_instance=str(resources.INSTANCE),
        instance_version=version,material_resource_sources=sources,enabled_file_resource_packs=packs)
    print('逐格回读通过，合并连续外露面…',flush=True)
    groups,lengths,merged=merge_surface_runs(raw,data['size'])
    check.update(viewer_surface_merge=merged,viewer_rendered_quads=merged['rendered_quads'])
    check['ordinary_material_namespaces']={}
    for state,n in check['palette'].items():
        if state not in (geometry.material.CONTROL,geometry.material.PORT):
            ns=state.split(':')[0]
            check['ordinary_material_namespaces'][ns]=check['ordinary_material_namespaces'].get(ns,0)+n
    payload=dict(data=data,palette=geometry.STATES,surfaceGroups=groups,surfaceRunLengths=lengths,
        blockCount=check['blocks'],materials=materials,audit=check,names={s:s.split(':')[1] for s in geometry.STATES})
    compressed=gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),6)
    (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(base64.b64encode(compressed).decode('ascii'))+';',encoding='utf-8')
    check['viewer_payload_gzip_bytes']=len(compressed)
    save(OUT/'manifest.json',dict(data,approved=False,installed=False,game_verified=False,
        status='candidate_waiting_user_review',target_voltage='IWV',voltage_mapping='V12 / tier26',
        blocks=check['blocks'],unique_materials=43,ordinary_materials=41,source_instance=str(resources.INSTANCE),
        instance_version=version,generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT/'verification.json',check)
    save(OUT/'材料清单.json',[dict(state=m['state'],count=check['palette'][m['state']],role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'],source=sources.get(m['state'],{}),survival_stage_verified=False) for m in materials])
    save(LOG/'lower-voltage-evidence.json',check['voltage_progression'])
    (OUT/'index.html').write_text(report(data,check),encoding='utf-8')
    print('完整结构与材质载荷已生成。',flush=True)
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for name in ('i41_cosmic_customs_geometry_v3_20261028.py','build_i41_cosmic_customs_v3_20261028.py'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    save(LOG/'package-status.json',dict(passed=True,approved=False,installed=False,game_verified=False,
        output=str(OUT),size_xyz=data['size'],blocks=check['blocks'],materials=43,rendered_quads=merged['rendered_quads'],
        payload_bytes=len(compressed),nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT),blocks=check['blocks'],rendered_quads=merged['rendered_quads']),ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
