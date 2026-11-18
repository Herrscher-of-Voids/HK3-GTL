# -*- coding: utf-8 -*-
"""I42完整结构、真实MC材质与独立HTML交付。

变更记录 #1（2026-10-28）：新增预制船坞候选，不修改正式资源或实例。
"""
import base64
import datetime as dt
import gzip
import html
import json
import shutil
import i42_prefabrication_geometry_v1_20261028 as geometry
from i42_prefabrication_audit_v1_20261028 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT=geometry.ROOT
OUT=ROOT/'deliveries/I42_奇观构件预制工厂_巨构龙骨与步进预制船坞_V1_20261028'
LOG=ROOT/'logs/i42-prefabrication-v1-20261028'


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def report(data,check):
    esc=html.escape
    material_rows=''.join(f'<tr><td><code>{esc(s)}</code></td><td>{n:,}</td><td>{esc(geometry.ROLES[s])}</td></tr>' for s,n in check['palette'].items())
    p=check['voltage_progression']
    rows=''.join(f'<tr><td>{label}</td><td>{p["metrics"][key]:,}</td><td>{p["lower_maxima"][key]["value"]:,}</td><td>+{(p["metrics"][key]/p["lower_maxima"][key]["value"]-1)*100:.2f}%</td></tr>' for key,label in [('blocks','实体方块'),('materials','普通材料种类'),('volume','实体包围盒体积'),('height','高度')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I42 · 巨构龙骨与步进预制船坞</title><style>
body{{max-width:1320px;margin:32px auto;padding:0 24px;background:#111b28;color:#e5edf6;font:16px/1.8 system-ui}}h1{{line-height:1.3}}a{{color:#9adce4}}.note{{padding:16px;border-left:4px solid #b5bfd5;background:#27303d}}img{{width:100%}}table{{width:100%;border-collapse:collapse}}td,th{{padding:9px;border-bottom:1px solid #425466;text-align:left;overflow-wrap:anywhere}}code{{overflow-wrap:anywhere}}.links{{display:flex;gap:18px;flex-wrap:wrap}}</style>
<small>HK3GTL · I42 · WFV / V13 / tier27 · V1独立待审候选</small><h1>奇观构件预制工厂<br>巨构龙骨与步进预制船坞</h1>
<p class="note">641×449×295（宽×长×高），{check['blocks']:,}个实体方块，42种普通建材。中央是一条由胎架承托、逐段长出承力肋与隔离壳的在制巨构龙骨；九组步进龙门吊共用轨道，两侧分层加工厂房与八类工位围绕真实构件交接组织。主控位于前端桥楼中轴，八接口嵌入连续外墙。</p>
<div class="links"><a href="i42/三维评审.html">打开真实MC材质三维评审</a><a href="完整预览.png">完整预览</a><a href="船坞后方.png">后方装配段</a><a href="船坞俯视.png">工艺俯视</a><a href="主控材质近景.png">主控近景</a><a href="verification.json">静态核验</a></div><img src="完整预览.png" alt="I42步进预制船坞完整MC材质预览">
<h2>从材料到专用大型构件</h2><p>GT基础件、I14/I16的魂钢先进坯和精密件、I40专用材料进入加工厂房；承力骨架、导能母排、隔离壁、重构工作腔、认知载体框、冷热隔热壳段、核心安装座与检修流体汇接八类工位，分别表达不同预制任务。中央龙骨只是一套在制构件的建筑展示，不代表一艘可生成飞船。</p>
<p>两侧厂房保留六层真实工艺空腔和维护空间；分段定位柱托住龙骨，吊索与上方小车实际相连。薄层甲板、条形基础和开放坞底避免用实心大底座填满场地。WFV机壳承担主体识别，钛色门架、铜色母排、黑色胎架和局部观察玻璃形成分工。</p>
<h2>居中主控与嵌入接口</h2><p>主控蓝图XYZ为<code>{data['controller']}</code>，整宽第321格。钻石块只标位置，八处工业方块只作计划接口；周围连续壳体、内背板和外侧净空分别核验。整座六邻接连通，全部方块从同一份几何导出NBT、Schematic和MC材质预览，逐格回读一致。</p>
<h2>全部较低电压的递进核对</h2><p>{p['lower_form_count']}个已批准较低阶形态＝{p['formal_lower_count']}个正式资源＋新批准待安装的I41 V3。后者按确认归档、ZIP、NBT/Schematic和逐格核验哈希核对，没有因为尚未部署而漏掉。I40与本机同为WFV，不强制按编号增大；未批I37排除。四项严格递增4/4（100%），造型仍待负责人审阅。</p><table><tr><th>指标</th><th>I42</th><th>低阶最大值</th><th>增幅</th></tr>{rows}</table>
<h2>工艺与研究边界</h2><p>RN-WPF开放预制方向，不自动开放全部W01–W15专项。各奇观按用途组合不同构件，不用一个万能零件替代。首机研究试件由前级I16制备、I32分析，不能先要求I42自产件；新建筑不把未冻结的provisional实验电压当正式额定电压，也不把工程证明制造成配方产物。</p>
<p class="note">本轮交付建筑外观与完整结构文件，未注册I42控制器、专用配方、研究或正式Pattern；不替玩家自动搭建奇观，不绕过对应专项研究、二审及真实材料消费。待审、未批准、未实装。I40与I41已批准，本批2/5；达到五台后先接入游戏。I37仍留最后。</p>
<h2>MC材质与运行RAM</h2><p>使用增强版2.9.2实例真实纹理，逐格重复、最近邻采样；外露面连续合并，初始化分帧、静止按需绘制。浏览器效果不代表游戏RAM或FCL达标。终极终端批量搭建、分区检测和8GB运行RAM工程仍按独立方案进行，完整结构并未用缩小模型替代。</p>
<details><summary>实际材料与构件职责</summary><table><tr><th>方块状态</th><th>数量</th><th>职责</th></tr>{material_rows}</table></details>
<p><a href="../多方块确认归档/当前归档索引.html">批准结构索引</a> · <a href="../../doc/HK3GTL-内测5/完整对话归档/2026-10-28_23-19-06_I41V3批准并制作I42_dea9f124a7.html">本轮真实对话</a></p><footer>变更记录 #1 · 2026-10-28：新增I42独立候选与完整导出，未改实例、正式资源或既有批准建筑。</footer></html>'''


def main():
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
    view=OUT/'i42';view.mkdir(exist_ok=True)
    print('生成I42预制船坞，核验实体、连通性及45个低阶形态…',flush=True)
    cube,data=geometry.build();check=audit(cube,data)
    version=json.loads((resources.INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version=='2.9.2'
    materials,sources,packs=resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('真实材质及静态核验通过，导出完整NBT/Schematic…',flush=True)
    result=export_dense(cube,geometry.STATES,data['name'],view)
    assert result['block_count']==check['blocks']
    raw=result['surface_groups']
    check.update(nbt_schem_sha256=result['hashes'],readback=result['readback'],
        viewer_surface_faces=sum(len(f) for g in raw for f in g),source_instance=str(resources.INSTANCE),
        instance_version=version,material_resource_sources=sources,enabled_file_resource_packs=packs)
    print('完整结构逐格回读通过，合并连续外露面…',flush=True)
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
        status='candidate_waiting_user_review',target_voltage='WFV',voltage_mapping='V13 / tier27',
        blocks=check['blocks'],unique_materials=44,ordinary_materials=42,source_instance=str(resources.INSTANCE),
        instance_version=version,generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT/'verification.json',check)
    save(OUT/'材料清单.json',[dict(state=m['state'],count=check['palette'][m['state']],role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'],source=sources.get(m['state'],{}),survival_stage_verified=False) for m in materials])
    save(LOG/'lower-voltage-evidence.json',check['voltage_progression'])
    (OUT/'index.html').write_text(report(data,check),encoding='utf-8')
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for name in ('i42_prefabrication_geometry_v1_20261028.py','i42_prefabrication_audit_v1_20261028.py',
                 'i42_voltage_progression_20261028.py','build_i42_prefabrication_v1_20261028.py'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    save(LOG/'package-status.json',dict(passed=True,approved=False,installed=False,game_verified=False,
        output=str(OUT),size_xyz=data['size'],blocks=check['blocks'],materials=44,rendered_quads=merged['rendered_quads'],
        payload_bytes=len(compressed),nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT),blocks=check['blocks'],rendered_quads=merged['rendered_quads']),ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
