# -*- coding: utf-8 -*-
"""I43完整结构、真实MC材质与纯HTML交付。

变更记录 #1（2026-10-28）：新增环境验收舱候选，不修改正式资源或实例。
"""
import base64
import datetime as dt
import gzip
import html
import json
import shutil
import i43_acceptance_geometry_v1_20261028 as geometry
from i43_acceptance_audit_v1_20261028 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT=geometry.ROOT
OUT=ROOT/'deliveries/I43_文明工程验收中心_开瓣环境穹舱与六轴验收台_V1_20261028'
LOG=ROOT/'logs/i43-environment-acceptance-v1-20261028'


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def report(data,check):
    esc=html.escape
    rows=''.join(f'<tr><td><code>{esc(s)}</code></td><td>{n:,}</td><td>{esc(geometry.ROLES[s])}</td></tr>' for s,n in check['palette'].items())
    ordinary_blocks=check['blocks']-check['palette'][geometry.material.CONTROL]-check['palette'][geometry.material.PORT]
    source_rows=''.join(f'<tr><td>{esc(name)}</td><td>{count:,}</td><td>{"标记单列" if name in ("主控标记","工业接口标记") else format(count/ordinary_blocks*100,".3f")+"%"}</td></tr>' for name,count in check['material_source_counts'].items())
    p=check['voltage_progression']
    comparisons=''.join(f'<tr><td>{label}</td><td>{p["metrics"][key]:,}</td><td>{p["lower_maxima"][key]["value"]:,}</td></tr>' for key,label in [('blocks','实体方块'),('materials','普通建材种类'),('volume','实际包围盒体积'),('height','实际高度')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I43 · 开瓣环境穹舱与六轴验收台</title><style>
body{{max-width:1320px;margin:32px auto;padding:0 24px;background:#111b28;color:#e5edf6;font:16px/1.8 system-ui}}h1{{line-height:1.3}}a{{color:#9adce4}}.note{{padding:16px;border-left:4px solid #b5bfd5;background:#27303d}}img{{width:100%}}table{{width:100%;border-collapse:collapse}}td,th{{padding:9px;border-bottom:1px solid #425466;text-align:left;overflow-wrap:anywhere}}code{{overflow-wrap:anywhere}}.links{{display:flex;gap:18px;flex-wrap:wrap}}</style>
<small>HK3GTL · I43 · WSV / V14 / tier28 · V1独立待审候选</small><h1>文明工程验收中心<br>开瓣环境穹舱与六轴验收台</h1>
<p class="note">641×481×297（宽×长×高），{check['blocks']:,}个实体方块，{check['ordinary_materials']}种普通建材。厚型试验门沿地轨展开，露出六轴加载台与框式受检样件；两侧计量廊独立隔振承载，外部阶梯机房组织冷热循环和测试介质。</p>
<div class="links"><a href="i43/三维评审.html">真实MC材质三维评审</a><a href="完整预览.png">完整预览</a><a href="试验舱后方.png">后方循环设备</a><a href="试验舱俯视.png">试验舱俯视</a><a href="主控材质近景.png">主控近景</a><a href="verification.json">完整核验</a></div><img src="完整预览.png" alt="I43开门环境试验舱完整MC材质预览">
<h2>工程到场，环境联试，独立测量</h2><p>主舱采用半圆承力拱壳、分层内衬与隔声尖劈；两扇展开门具有实体铰座、锁封、传动箱和落地导轨。中央六根加载支腿托住受检框式构件，前后光学门架建立测量基线。两侧洁净计量廊与加载台分开承载，舱后配置介质隔离柜、故障复测台和冷热循环设备。前厅将样件交接与记录复核接到同一工艺线。</p>
<p>WSV机壳主导环境壳、试验门与加载台；钛色承力环、暗色吸波/辐射内衬、洁净计量走廊与少量铜母排明确分工。保留双层舱底间的设备间隙；厂房空腔、门前空地与开敞舱口没有用实心方块填满。</p>
<h2>中轴主控与内嵌接口</h2><p>主控蓝图XYZ为<code>{data['controller']}</code>，整宽第321格。八处工业占位接口在前厅连续墙中齐平嵌入，逐个核对内背板和外侧净空。钻石块只标控制器位置，不把占位块当实际物品、流体或电力能力。建筑整体六邻接单连通。</p>
<h2>验收中心的职责边界</h2><p>I43接收工程样件、真实运行记录与测试介质，形成运行合格报告、故障清单及验收档案。研究节点RN-CEE与I32前级校准形成试验方法证据，不能替代奇观本体或既有仿制舰的真实运行证明；首机不能先验收自己。不合格工程应复测，不重复授予已经确认的成果。最终资格仍由W15汇总，I43不另设终审。</p>
<p>I40负责材料，I42负责专用构件预制；玩家仍须搭建并运行对应工程。I43不能用报告制造资源、自动搭建奇观、代替专项研究与二审，或以展示样件宣布工程已通过。</p>
<h2>全部较低电压的递进核对</h2><p>{p['lower_form_count']}个已批准低阶＝{p['formal_lower_count']}个正式资源＋I40 V1、I41 V3、I42 V1三个已批准待接入版本。按当次批准索引、归档、ZIP与逐格核验哈希核对；未批准I37排除，同阶I22不强制比较。四项严格递增4/4（100%），外观仍待负责人审阅。</p><table><tr><th>指标</th><th>I43</th><th>低阶最大值</th></tr>{comparisons}</table>
<h2>完整实体与浏览器预览</h2><p>同一份最终几何导出完整NBT、Schematic和三维数据，逐格回读一致；真实MC纹理取自增强版2.9.2，保持每格重复、最近邻采样。只合并外露连续面，未缩小建筑或用低精度模型冒充。静止按需绘制，初始化分帧。</p>
<p class="note">本轮只交付建筑候选及完整结构文件，未接入I43正式控制器、Pattern、专用配方或研究执行逻辑。I43待审未批准、未实装；I40/I41/I42已批准，本批3/5，五台后先接入。I37继续留最后。游戏及FCL运行RAM、终极终端批量搭建、强加载表现仍待全部结构完成后实测。</p>
<h2>实际建材来源数量</h2><p>由最终蓝图逐格统计；项目自有WSV主机壳独立列出。普通建材占比以扣除主控1格、接口8格后的 {ordinary_blocks:,} 为分母，标记另列数量。</p><table><tr><th>来源</th><th>数量</th><th>普通建材占比</th></tr>{source_rows}</table>
<details><summary>逐种材料与构件职责</summary><table><tr><th>方块状态</th><th>数量</th><th>职责</th></tr>{rows}</table></details>
<p><a href="../多方块确认归档/当前归档索引.html">批准结构索引</a> · <a href="../../doc/HK3GTL-内测5/完整对话归档/2026-10-28_23-51-56_I42V1批准并制作I43_b87a8e8087.html">本轮真实对话</a></p><footer>变更记录 #1 · 2026-10-28开始设计：I43独立候选及完整导出；实际生成时间见manifest，未改实例或既有批准建筑。</footer></html>'''


def main():
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
    view=OUT/'i43';view.mkdir(exist_ok=True)
    print('生成I43环境验收舱，核验实体、连通性及47个低阶形态…',flush=True)
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
    source_counts={'GTCEu':0,'GTL Core':0,'其他模组':0,'原版':0,'项目WSV主机壳':0,'主控标记':0,'工业接口标记':0}
    for state,count in check['palette'].items():
        if state==geometry.material.CONTROL: group='主控标记'
        elif state==geometry.material.PORT: group='工业接口标记'
        elif state==geometry.material.WSV: group='项目WSV主机壳'
        elif state.startswith('minecraft:'): group='原版'
        elif state.startswith('gtceu:'): group='GTCEu'
        elif state.startswith('gtlcore:'): group='GTL Core'
        elif state.startswith('hk3gtl:'): raise ValueError(('未列入白名单的项目方块',state))
        else: group='其他模组'
        source_counts[group]+=count
    check['material_source_counts']={key:value for key,value in source_counts.items() if value}
    payload=dict(data=data,palette=geometry.STATES,surfaceGroups=groups,surfaceRunLengths=lengths,
        blockCount=check['blocks'],materials=materials,audit=check,names={s:s.split(':')[1] for s in geometry.STATES})
    compressed=gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),6)
    (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(base64.b64encode(compressed).decode('ascii'))+';',encoding='utf-8')
    check['viewer_payload_gzip_bytes']=len(compressed)
    save(OUT/'manifest.json',dict(data,approved=False,installed=False,game_verified=False,
        status='candidate_waiting_user_review',target_voltage='WSV',voltage_mapping='V14 / tier28',
        blocks=check['blocks'],unique_materials=len(materials),ordinary_materials=check['ordinary_materials'],
        source_instance=str(resources.INSTANCE),instance_version=version,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT/'verification.json',check)
    save(OUT/'材料清单.json',[dict(state=m['state'],count=check['palette'][m['state']],role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'],source=sources.get(m['state'],{}),survival_stage_verified=False) for m in materials])
    save(LOG/'lower-voltage-evidence.json',check['voltage_progression'])
    (OUT/'index.html').write_text(report(data,check),encoding='utf-8')
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for name in ('i43_acceptance_geometry_v1_20261028.py','i43_acceptance_audit_v1_20261028.py',
                 'i43_voltage_progression_20261028.py','build_i43_acceptance_v1_20261028.py'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    save(LOG/'package-status.json',dict(passed=True,approved=False,installed=False,game_verified=False,
        output=str(OUT),size_xyz=data['size'],blocks=check['blocks'],materials=len(materials),
        rendered_quads=merged['rendered_quads'],payload_bytes=len(compressed),nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT),blocks=check['blocks'],rendered_quads=merged['rendered_quads']),ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
