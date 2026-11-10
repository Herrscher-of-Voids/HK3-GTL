# -*- coding: utf-8 -*-
"""I27：从独立几何导出结构、真实材质图与轻量三维评审。"""
from __future__ import annotations

import base64
import collections
import datetime as dt
import gzip
import html
import json
import math
import re
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageChops

from build_redesign69 import export, render
from structure_size_baseline import require
import build_i25_world_bubble_observatory_20261025 as assets
import build_i26_kwaichung_terminal_v2_20261026 as shared
import i27_capture_array_geometry_20261026 as geometry

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I27_世界泡整体捕获阵列_锁界环形回收坞_V1_20261026'
VIEW = OUT / 'i27'
NAME, TITLE = geometry.NAME, geometry.TITLE
INSTANCE = assets.INSTANCE
PRIOR_VIEW = ROOT / 'deliveries/I26_葵涌码头_疏散货柜与随机集卡运营场景_V5_20261026/i26'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def progression(counts, size):
    source = ROOT / 'logs/i01-i25-voltage-progression-20261025/audit.json'
    lower = [form for form in json.loads(source.read_text(encoding='utf-8'))['forms'] if form['tier'] < 23]
    latest_i26 = ROOT / 'deliveries/I26_葵涌码头_疏散货柜与随机集卡运营场景_V5_20261026/verification.json'
    previous = json.loads(latest_i26.read_text(encoding='utf-8'))
    lower.append({'id': 'I26 V5', 'tier': 22, 'metrics': {'blocks': previous['blocks'],
                  'materials': previous['unique_materials'], 'volume': previous['bounding_box_volume'], 'height': previous['height']}})
    metrics = dict(blocks=sum(counts.values()), materials=len(counts), volume=math.prod(size), height=size[1])
    maxima = {key: {'value': max(form['metrics'][key] for form in lower),
                   'ids': [form['id'] for form in lower if form['metrics'][key] == max(item['metrics'][key] for item in lower)]}
              for key in metrics}
    passes = {key: value > maxima[key]['value'] for key, value in metrics.items()}
    result = dict(source=str(source.relative_to(ROOT)), current_i26_source=str(latest_i26.relative_to(ROOT)),
                  tier_rule='IMV/tier23与全部较低电压形态严格比较；同阶I21不纳入。',
                  lower_form_count=len(lower), metrics=metrics, lower_maxima=maxima, passes=passes)
    assert all(passes.values()), ('电压递增未满足', result)
    return result


def audit(data):
    cells = {tuple(block['pos']): block['state'] for block in data['blocks']}
    assert len(cells) == len(data['blocks']), '存在重复坐标'
    counts = collections.Counter(cells.values())
    low = [min(p[i] for p in cells) for i in range(3)]
    high = [max(p[i] for p in cells) for i in range(3)]
    actual = [high[i] - low[i] + 1 for i in range(3)]
    assert low == [0, 0, 0] and actual == list(data['size']) == [geometry.W, geometry.H, geometry.D]
    assert counts[geometry.CONTROL] == 1
    assert counts[geometry.IMV] > max(n for state, n in counts.items() if state != geometry.IMV)
    assert {state for state in counts if state.startswith('hk3gtl:')} == {geometry.IMV, geometry.PORT}
    assert data['controller'][0] == (geometry.W - 1) // 2
    direction = {'north': (0, 0, -1), 'south': (0, 0, 1), 'east': (1, 0, 0), 'west': (-1, 0, 0)}
    marker_checks = []
    markers = [dict(id='主控', pos=data['controller'], face='north', state=geometry.CONTROL)]
    markers += [dict(port, state=geometry.PORT) for port in data['ports']]
    for marker in markers:
        p = tuple(marker['pos']); vector = direction[marker['face']]
        assert cells.get(p) == marker['state'], ('标记位置不符', marker)
        assert all(tuple(p[i] + vector[i] * step for i in range(3)) not in cells for step in range(1, 5)), ('外侧净空', marker)
        assert tuple(p[i] - vector[i] for i in range(3)) in cells, ('缺内背板', marker)
        tangent = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)) if vector[2] else ((0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0))
        assert all(tuple(p[i] + v[i] for i in range(3)) in cells for v in tangent), ('周边外壳不连续', marker)
        marker_checks.append(dict(id=marker['id'], position=p, face=marker['face'], outer_clear=4, inner_backed=True, shell_neighbors=4))
    shared.W, shared.H, shared.D = data['size']
    connectivity = shared.connected_components(data)
    return dict(passed=True, geometry_passed=True, approved=False, blocks=len(cells), unique_materials=len(counts),
                palette=dict(counts.most_common()), bounds_xyz=dict(min=low, max=high), size_xyz=actual,
                size_wdh=[actual[0], actual[2], actual[1]], bounding_box_volume=math.prod(actual), height=actual[1],
                baseline_check=require(data), voltage_progression=progression(counts, actual), connectivity=connectivity,
                imv_casing_is_largest_single_material=True, imv_casing_count=counts[geometry.IMV],
                controller=dict(position=data['controller'], center_x_zero_based=geometry.CX, ordinal_from_left=geometry.CX + 1),
                port_checks=marker_checks, checks=[
                    '声明尺寸与实际实体边界一致，逐轴超过最新占地表下限。',
                    'IMV为最大单一材料；HK3GTL自有材料仅对应电压机壳及工业接口占位块。',
                    '实体方块数、材料种类、包围盒体积、实际高度均超过全部较低电压形态。',
                    '钻石主控位于整宽中轴；所有标记齐平嵌入连续设备表面，内有背板、外留四格净空。',
                    '六邻接遍历确认全体为单一连续组件。',
                    '资源读取增强版当前2.9.2实例及启用资源包，静态完整方块使用真实首帧贴图。'],
                not_verified=['实际Controller/Pattern、额定EU、正式仓室能力、配方与游戏内成型。',
                              '普通建材的最终有效配方、研究前置及生存获取链。',
                              '世界泡UUID与已采次数持久化、容器交接和异常恢复的游戏逻辑。',
                              '运行光照、动态材质、能量场与捕获动画；当前为静态建筑表达。'])


def build_viewer():
    source = (ROOT / 'tools/structure_delivery/build_i26_terminal_viewer_v2_20261026.mjs').read_text(encoding='utf-8')
    source = source.replace("const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');",
                            'const root = ' + json.dumps(ROOT.as_posix()) + ';')
    additions = r'''
source=source.replace("function setView(name){", "function setView(name){if(name==='controller'){focusPort({id:'主控',pos:data.controller,face:'north'});return;}");
source=source.replace("for(const button of document.querySelectorAll('[data-view]'))", `
function focusPort(port){
 const direction={north:[0,0,-1],south:[0,0,1],west:[-1,0,0],east:[1,0,0]}[port.face];
 const point=port.pos.map(v=>v+.5);camera.up.set(0,1,0);camera.position.set(...point.map((v,i)=>v+direction[i]*55+(i===1?6:0)));
 controls.target.set(...point);camera.zoom=Math.min(8,L/35);camera.updateProjectionMatrix();controls.update();
 document.getElementById('layer').value=H-1;document.getElementById('showGlass').checked=true;document.getElementById('showPorts').checked=true;
 document.getElementById('viewName').textContent=port.id+' · 蓝图['+port.pos.join(', ')+'] / 格位['+port.pos.map(v=>v+1).join(', ')+']';
 document.querySelectorAll('[data-view]').forEach(b=>b.classList.remove('active'));rebuild();
}
for(const button of document.querySelectorAll('[data-view]'))`);
source=source.replace("document.getElementById('ports').innerHTML=", `
document.getElementById('portButtons').innerHTML=data.ports.map((p,i)=>'<button data-port="'+i+'">'+p.id+'</button>').join('');
for(const button of document.querySelectorAll('[data-port]'))button.onclick=()=>focusPort(data.ports[+button.dataset.port]);
document.getElementById('ports').innerHTML=`);
source=source.replace(" 个正面接口候选位", " 个内嵌接口候选位");
source=source.replace("(${p.pos.join(', ')}) ·", "蓝图(${p.pos.join(', ')}) / 格位(${p.pos.map(v=>v+1).join(', ')}) ·");
source=source.replace("data.key+'-研究所候选02-三维结构预览.png'", "data.key+'-锁界环形回收坞V1-三维预览.png'");
'''
    source = source.replace('const oldHotPaths = ', additions + '\nconst oldHotPaths = ')
    source = source.replace('I26码头预览', 'I27捕获阵列预览').replace('virtual:i26-terminal', 'virtual:i27-capture')
    path = OUT / '生成脚本/build_i27_viewer_v1_20261026.mjs'
    path.write_text(source, encoding='utf-8')
    subprocess.run(['node', str(path), str(VIEW)], cwd=ROOT, check=True)


def viewer_page(data, check):
    css = re.search(r'<style>(.*?)</style>', (PRIOR_VIEW / '三维评审.html').read_text(encoding='utf-8'), re.S).group(1)
    w, h, d = data['size']; p = data['controller']; ordinal = [v + 1 for v in p]
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I27 · {TITLE} V1</title><style>{css}</style>
<header><a href="../index.html">← I27交付总览</a><h1>I27 · {TITLE} V1</h1><div>{w}×{d}×{h}（宽×长×高） · {check['blocks']:,}方块 · 独立结构候选</div></header>
<main class="review"><section id="stage"><div id="loading">加载真实材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="locator"><b>主控蓝图 {p}</b><p>从1起算格位 {ordinal}；整宽第{geometry.CX + 1}格，嵌入捕获指挥设施前脸。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后侧回收区</button><button data-view="top">俯视</button><button data-view="inside">剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">{h - 1}</b><input id="layer" type="range" min="0" max="{h - 1}" value="{h - 1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>整体捕获与封存</summary><p>中央捕获井、巨型锁定环、落地牵引支架、独立封存回收厅组成同一工程系统。IMV深紫外壳统领主体，银灰承重与冰蓝约束带支持功能分区。</p><p>容器可以制造，真实世界泡身份不能复制；捕获后保持UUID与已采次数。这里表达建筑职责，不表示游戏逻辑已接通。</p></details>
<details open><summary>主控与设备内嵌接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>结构文件与验收边界</summary><a href="{NAME}.nbt">NBT</a> · <a href="{NAME}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>候选尚未批准、未接入实例；Pattern、配方、生存获取与游戏内捕获尚未验收。</p></details></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''


def report_page(data, check):
    rows = ''.join(f'<tr><td>{label}</td><td>{check["voltage_progression"]["metrics"][key]:,}</td><td>{check["voltage_progression"]["lower_maxima"][key]["value"]:,}</td><td>通过</td></tr>'
                   for key, label in [('blocks', '实体方块数'), ('materials', '唯一材料数'), ('volume', '实体包围盒体积'), ('height', '实际高度')])
    zones = ''.join(f'<li>{html.escape(z["name"])}</li>' for z in data['zones'])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I27 · {TITLE} V1</title><style>
body{{max-width:1380px;margin:30px auto;padding:0 22px;background:#111b28;color:#e5edf5;font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}}a{{color:#b4dbe8}}img{{max-width:100%;height:auto}}.note{{padding:15px;background:#283044;border-left:3px solid #ac96c6}}table{{border-collapse:collapse;width:100%}}td,th{{padding:10px;border-bottom:1px solid #425065;text-align:left}}.links{{display:flex;gap:20px;flex-wrap:wrap}}small{{color:#aabbcc}}
</style><small>HK3GTL / I27 / IMV·V09 / 从零设计候选 V1</small><h1>{TITLE}</h1><p class="note">{html.escape(data.get('description', '以锁定环、捕获井和独立回收设施完成整个真实世界泡的捕获与封存。'))}</p>
<p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}个实体方块 · {check['unique_materials']}种真实材料 · IMV主体机壳{check['imv_casing_count']:,}块</p>
<p class="links"><a href="i27/三维评审.html">打开三维评审</a><a href="等轴预览.png">查看完整等轴图</a><a href="verification.json">静态核验</a><a href="材料清单.json">材料清单</a><a href="设计依据.json">设计依据</a></p><img src="等轴预览.png" alt="I27真实逐格材质完整等轴预览">
<h2>功能组织</h2><ul>{zones}</ul><p>输入I25有效坐标、I44锁定与正式空收容容器，以约束能量完成整体捕获、稳定封存及异常恢复。输出封存真实世界泡和场衰减记录，交接I28；不兼并I26采掘与I28终止结算。研究前置RN-WBC，不通过更换容器刷新世界泡身份或采掘次数。</p>
<h2>电压递增量化核验</h2><p>与全部较低电压形态比较，包含刚确认的I26 V5；同为IMV的I21不强制排序。高度由捕获装置本体形成，没有沿用I26的110格个案例外。</p><table><thead><tr><th>指标</th><th>I27实测</th><th>低阶最大值</th><th>量化结果</th></tr></thead><tbody>{rows}</tbody></table>
<h2>主控与接口</h2><p>钻石块仅标记主控；工业接口块仅表示正式Pattern可规划的仓室位置。主控整宽居中，全部接口齐平融入各自设备，外侧四格净空、内侧背板及周边外壳已检查。精确蓝图坐标及朝向见三维页。</p>
<p>三维仅提交{check['viewer_surface_faces']:,}片外露面；gzip载荷，按需重绘。隐藏材质不会挖开原有实心构件补画内部。</p>
<p class="note">外观候选尚未批准、未接入实例。静态几何与资源核验通过不代表Pattern、配方、研究与生存获取链、真实捕获逻辑或游戏成型通过；所有图像与三维均来自同一最终逐格数据。</p></html>'''


def material_records(materials, check, evidence):
    roles = {'IMV':'主承重环、捕获臂、设备廊与回收厅主体', 'PORT':'设备外墙的接口候选占位', 'CONTROL':'居中控制器位置标记',
             'ROBUST':'底部承重梁与锁定环接头', 'CLEAN':'捕获臂接头、设备外缘及控制厅外饰', 'ASSEMBLY':'环形基础与厅体结构连接',
             'COMPUTER':'调度、坐标与状态计算机组', 'ATOMIC':'极靴、约束发射端与捕获支点', 'POWER':'脉冲供能装置',
             'LASER':'牵引校准机组面板', 'TURBINE':'换热机组与低温设备顶盖', 'MACERATOR':'密闭机械维护设备',
             'VENT':'热交换设备的通风面', 'GEAR':'锁定环传动与检修机组', 'TUNG_PIPE':'高功率设备完整管路外壳',
             'STEEL_PIPE':'冷却机组连接与约束臂线路', 'GRATE':'维护地板、接口操作区与设备检修顶板',
             'IRIDIUM':'锁定环与封存设备的局部屏蔽构件', 'PROCESS':'封存及异常恢复工艺机组', 'DIMENSION':'目标边界耦合机组',
             'MULTI':'维护廊内综合设备模块', 'LAFIUM':'稳定器设备面板', 'GLASS':'密闭观测设备与封存观察窗',
             'FILTER':'场衰减记录机组与维护过滤设备', 'INERT':'隔离设备机壳', 'HEATPROOF':'散热及异常工况维护设备',
             'INSULATE':'绝缘机组与约束支撑', 'FROST':'低温循环设备与换热列', 'STABLE':'稳定场辅助设备',
             'SOLID':'基础设备外壳与机械检修机组', 'INTAKE':'低温设备静态进气格栅，active=false',
             'STRESS':'承压夹持与机械维护设备', 'MIXING':'密闭反应与异常恢复设备', 'BLUE_GLASS':'静态约束导束与观测带',
             'BLACK_GLASS':'黑色世界泡目标的正球外表层', 'BLACK':'世界泡示意壳内层，不作建筑填充', 'LIGHT':'设备及维护通道照明'}
    role_by_state = {getattr(geometry, key): value for key, value in roles.items()}
    history = evidence.get('historical_recipe_reference', [])
    history_map = {'FROST':0, 'STABLE':0, 'SOLID':0, 'HEATPROOF':0, 'CLEAN':0, 'INTAKE':1, 'INSULATE':2, 'MIXING':3, 'LASER':3, 'STRESS':4}
    history_by_state = {getattr(geometry,key): [history[index]] for key,index in history_map.items() if index < len(history)}
    result = []
    for m in materials:
        state = m['state']; base = state.split('[')[0]; ns, key = base.split(':')
        refs = [{k:v for k,v in item.items() if k != 'context'} for item in evidence.get('recipe_evidence', []) if base in item.get('states', [])]
        refs += [{k:v for k,v in item.items() if k != 'context'} for item in history_by_state.get(state, [])]
        if state == geometry.IMV:
            refs.append(dict(path='src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3VoltageCasingRecipes.java',
                             meaning='项目现行机壳注册入口；完整研究与主材首通链仍须游戏验收。'))
        resource = check['material_resource_sources'].get(f'assets/{ns}/blockstates/{key}.json')
        phase = '指定主控/接口位置标记，不作为普通建材核验。' if state in (geometry.CONTROL,geometry.PORT) else (
            '附静态配方/脚本引用；旧版参考与当前引用分别保留，最终有效获取链尚未验收。' if refs else '当前真实资源已核验；尚无本轮最终有效获取链证据。')
        result.append(dict(state=state, count=check['palette'][state], role=role_by_state[state], complete_cube=m['complete_cube'],
                           transparent=m['transparent'], resource_source=resource, recipe_evidence=refs, phase_verification=phase))
    return result


def render_previews(data, materials):
    render(data, materials, OUT, round_spheres=True)
    path = OUT / '等轴预览.png'
    image = Image.open(path).convert('RGB')
    occupied = ImageChops.difference(image, Image.new('RGB', image.size, (19, 26, 40))).getbbox()
    assert occupied, '等轴图为空'
    cropped = image.crop(occupied)
    framed = Image.new('RGB', (cropped.width + 240, cropped.height + 240), (19, 26, 40))
    framed.paste(cropped, (120, 120)); framed.save(path)


def main():
    if (OUT / 'manifest.json').exists():
        assert json.loads((OUT / 'manifest.json').read_text(encoding='utf-8')).get('approved') is False
    VIEW.mkdir(parents=True, exist_ok=True); (OUT / '生成脚本').mkdir(exist_ok=True)
    data = geometry.build(); check = audit(data)
    states = sorted(check['palette']); materials, sources, packs = assets.resource_materials(states)
    version = json.loads((INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2', ('当前实例版本已变化', version)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    states, groups, hashes = export(data, VIEW)
    check.update(source_instance=str(INSTANCE), instance_proof={'instance_version': version}, material_resource_sources=sources,
                 enabled_file_resource_packs=packs, nbt_schem_sha256=hashes)
    evidence_path = ROOT / 'logs/i27-capture-array-v1-20261026/material-extra-check.json'
    evidence = json.loads(evidence_path.read_text(encoding='utf-8')) if evidence_path.exists() else {}
    check['supplementary_material_evidence'] = str(evidence_path.relative_to(ROOT))
    ordinary = collections.Counter()
    for state, count in check['palette'].items():
        if state not in (geometry.PORT, geometry.CONTROL):
            ordinary[state.split(':')[0]] += count
    total = sum(ordinary.values())
    check['ordinary_material_namespaces'] = {key: dict(blocks=value, ratio=round(value / total, 5)) for key, value in ordinary.items()}
    check['marker_blocks'] = check['palette'][geometry.PORT] + check['palette'][geometry.CONTROL]
    reconstructed = {((index % geometry.W), (index // (geometry.W * geometry.D)), (index // geometry.W) % geometry.D): state
                     for state, group in zip(states, groups) for index in group}
    assert reconstructed == {tuple(b['pos']): b['state'] for b in data['blocks']}
    del reconstructed, groups
    surfaces = shared.build_surface_groups(data, states)
    check.update(viewer_surface_faces=sum(len(face) for group in surfaces for face in group), viewer_payload_exact_cell_readback=True)
    payload = dict(data={k: v for k, v in data.items() if k != 'blocks'}, palette=states, surfaceGroups=surfaces,
                   blockCount=len(data['blocks']), materials=materials, audit=check, names={state: state.split(':')[1] for state in states})
    payload = json.loads(json.dumps(payload, ensure_ascii=False))
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    assert json.loads(gzip.decompress(base64.b64decode(encoded))) == payload
    (VIEW / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    del payload, surfaces
    build_viewer(); render_previews(data, materials)
    (VIEW / '三维评审.html').write_text(viewer_page(data, check), encoding='utf-8')
    (OUT / 'index.html').write_text(report_page(data, check), encoding='utf-8')
    manifest = dict({k: v for k, v in data.items() if k != 'blocks'}, candidate_version='V1', status='candidate_waiting_user_review',
                    approved=False, target_voltage='IMV', voltage_mapping='V09 / tier23', blocks=check['blocks'], unique_materials=len(states),
                    geometry_passed=True, source_instance=str(INSTANCE), instance_version=version, generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds'))
    save(OUT / 'manifest.json', manifest); save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', material_records(materials, check, evidence))
    save(OUT / '设计依据.json', [
        dict(path='doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html', fact='I27最低宽长高129×129×81；环形观测外场、独立回收入口。'),
        dict(path='doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html', fact='I27为IMV/V09，主体使用IMV电压机壳。'),
        dict(path='doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json', fact='有效目标整体捕获、封存稳定与容器交接、捕获异常状态恢复；保持真实UUID和已采次数，不兼并I26/I28职责。'),
        dict(path='rule/当前多方块设计规则.md', fact='主控居中、接口嵌入设备主体、项目材料白名单、全部低阶量化比较。'),
        dict(path='doc/HK3GTL-内测5/讨论记录/2026-09-28_15-38-17_第三阶19课题及起步资料与模拟封存裁定.html', fact='RN-WBC捕获研究依赖RN-BCC与RN-UED，空载验证证据由I33取得。')])
    shutil.copy2(__file__, OUT / '生成脚本' / Path(__file__).name)
    shutil.copy2(geometry.__file__, OUT / '生成脚本' / Path(geometry.__file__).name)
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=len(states), size=data['size'], faces=check['viewer_surface_faces']), ensure_ascii=False))


if __name__ == '__main__':
    main()
