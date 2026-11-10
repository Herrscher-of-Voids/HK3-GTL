# -*- coding: utf-8 -*-
"""I32：从独立几何导出结构、真实材质图与轻量三维评审。"""
from __future__ import annotations

import base64
import collections
import datetime as dt
import gzip
import hashlib
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
import i32_relic_reverse_lab_geometry_20261027 as geometry

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I32_遗留技术逆向实验室_遗构剖析院_V1_20261027'
VIEW = OUT / 'i32'
NAME, TITLE = geometry.NAME, geometry.TITLE
INSTANCE = assets.INSTANCE
PRIOR_VIEW = ROOT / 'deliveries/I26_葵涌码头_疏散货柜与随机集卡运营场景_V5_20261026/i26'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def progression(counts, size):
    from audit_i01_i25_voltage_progression_20261025 import voltage_mapping
    tiers = {name: 14 + i for i, name in enumerate('MAX HBV HCV HRV HDV QSV QCV QEV QAV IMV ICV IRV IWV WFV WSV CIV CEV'.split())}
    mapping = voltage_mapping()
    source = ROOT / 'src/main/resources/data/hk3gtl/structures/approved'
    lower = []
    metadata_paths = sorted(source.glob('*.json'))
    assert metadata_paths, '当前正式结构元数据为空'
    all_forms = []
    for metadata_path in metadata_paths:
        metadata_bytes = metadata_path.read_bytes()
        metadata = json.loads(metadata_bytes)
        key = metadata['key']
        mapping_key = 'I01-1' if key == 'i01' else key.upper().replace('_', '-')
        voltage = metadata.get('target_voltage', mapping.get(mapping_key)).upper()
        assert mapping_key not in mapping or mapping[mapping_key] == voltage, ('正式元数据与指定电压映射不同', key)
        all_forms.append(dict(id=mapping_key, voltage=voltage, tier=tiers[voltage]))
        if tiers[voltage] >= tiers['QAV']:
            continue
        blueprint_path = ROOT / 'src/main/resources/data/hk3gtl/approved_architecture' / (key + '.json')
        blueprint_bytes = blueprint_path.read_bytes()
        blueprint = json.loads(blueprint_bytes)
        blocks = blueprint['blocks']
        positions = [block['pos'] for block in blocks]
        low = [min(p[axis] for p in positions) for axis in range(3)]
        high = [max(p[axis] for p in positions) for axis in range(3)]
        actual = [high[axis] - low[axis] + 1 for axis in range(3)]
        controller = tuple(blueprint['controller'])
        ports = {tuple(p['pos']) for p in blueprint.get('ports', [])}
        normalized = collections.Counter(geometry.CONTROL if tuple(block['pos']) == controller else
                                         geometry.PORT if tuple(block['pos']) in ports else block['state'] for block in blocks)
        assert metadata.get('blocks', len(blocks)) == len(blocks), ('正式统计与逐格蓝图不同', key)
        assert list(metadata.get('size_xyz', metadata.get('size'))) == list(blueprint['size']), key
        lower.append(dict(id=mapping_key, voltage=voltage, tier=tiers[voltage], metrics=dict(
            blocks=len(blocks), materials=len({state.split('[')[0] for state in normalized}),
            volume=math.prod(actual), height=actual[1]), actual_xyz=actual,
            metadata=str(metadata_path.relative_to(ROOT)), metadata_sha256=hashlib.sha256(metadata_bytes).hexdigest(),
            blueprint=str(blueprint_path.relative_to(ROOT)), blueprint_sha256=hashlib.sha256(blueprint_bytes).hexdigest()))
        del blueprint, blocks, positions, blueprint_bytes
    assert {'S01', 'S02', 'S03', 'I05', 'I25'} <= {form['id'] for form in lower}
    assert not {'I26', 'I27', 'I28', 'I29', 'I30', 'I31'} & {form['id'] for form in lower}
    assert len(all_forms) == len({form['id'] for form in all_forms}), '正式结构编号重复'
    assert len(lower) == 28, ('QAV低阶比较对象变化，需复核', len(lower))
    assert next(form for form in lower if form['id'] == 'I05')['metrics']['blocks'] == 7519
    metrics = dict(blocks=sum(counts.values()), materials=len({state.split('[')[0] for state in counts}),
                   volume=math.prod(size), height=size[1])
    maxima = {key: {'value': max(form['metrics'][key] for form in lower),
                   'ids': [form['id'] for form in lower if form['metrics'][key] == max(item['metrics'][key] for item in lower)]}
              for key in metrics}
    passes = {key: value > maxima[key]['value'] for key, value in metrics.items()}
    result = dict(source=str(source.relative_to(ROOT)), formal_metadata_count=len(metadata_paths), all_forms=all_forms,
                  tier_rule='QAV/V08/tier22与当前全部正式低阶形态严格比较，包含S01–S03及I05正式V5；同阶与高阶不纳入。',
                  material_count_rule='按非空气方块ID去重，主控/接口规范回钻石/工业接口标记；状态朝向不增加种类。',
                  lower_form_count=len(lower), lower_forms=lower, metrics=metrics, lower_maxima=maxima, passes=passes)
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
    assert counts[geometry.QAV] > max(n for state, n in counts.items() if state != geometry.QAV)
    assert {state for state in counts if state.startswith('hk3gtl:')} == {geometry.QAV, geometry.PORT}
    assert data['controller'][0] == (geometry.W - 1) // 2
    assert all(cells.get((geometry.W - 1 - x, y, z)) == state for (x, y, z), state in cells.items()), '建筑实体未严格左右对称'
    assert data['key'] == 'i32'
    assert len({p['id'] for p in data['ports']}) == len(data['ports']), '接口标识重复'
    assert len({tuple(p['pos']) for p in data['ports']}) == len(data['ports']), '接口坐标重复'
    assert data['zones'] and len({zone['name'] for zone in data['zones']}) == len(data['zones']), '分区名称缺失或重复'
    assert all(tuple(zone['pos']) in cells for zone in data['zones']), '核心设备/功能区标记缺失'
    direction = {'north': (0, 0, -1), 'south': (0, 0, 1), 'east': (1, 0, 0), 'west': (-1, 0, 0)}
    marker_checks = []
    markers = [dict(id='主控', pos=data['controller'], face=data.get('controller_face', 'north'), state=geometry.CONTROL)]
    markers += [dict(port, state=geometry.PORT) for port in data['ports']]
    for marker in markers:
        p = tuple(marker['pos']); vector = direction[marker['face']]
        assert cells.get(p) == marker['state'], ('标记位置不符', marker)
        assert all(tuple(p[i] + vector[i] * step for i in range(3)) not in cells for step in range(1, 5)), ('外侧净空', marker)
        assert tuple(p[i] - vector[i] for i in range(3)) in cells, ('缺内背板', marker)
        tangent = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)) if vector[2] else ((0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0))
        assert all(tuple(p[i] + v[i] for i in range(3)) in cells for v in tangent), ('周边外壳不连续', marker)
        marker_checks.append(dict(id=marker['id'], position=p, face=marker['face'], outer_clear=4, inner_backed=True, shell_neighbors=4))
    path_checks = []
    for route in data['paths']:
        low_path, high_path = route['min'], route['max']
        blocked = [(x,y,z) for x in range(low_path[0],high_path[0]+1) for y in range(low_path[1],high_path[1]+1)
                   for z in range(low_path[2],high_path[2]+1) if (x,y,z) in cells]
        assert not blocked, ('操作通道被占用',route['name'],blocked[:5])
        path_checks.append(dict(name=route['name'],min=low_path,max=high_path,occupied_blocks=0))
    shared.W, shared.H, shared.D = data['size']
    connectivity = shared.connected_components(data)
    unique_materials = len({state.split('[')[0] for state in counts})
    return dict(passed=True, geometry_passed=True, approved=False, blocks=len(cells), unique_materials=unique_materials,
                palette=dict(counts.most_common()), unique_material_ids=sorted({state.split('[')[0] for state in counts}),
                bounds_xyz=dict(min=low, max=high), size_xyz=actual,
                size_wdh=[actual[0], actual[2], actual[1]], bounding_box_volume=math.prod(actual), height=actual[1],
                baseline_check=require(data), voltage_progression=progression(counts, actual), connectivity=connectivity,
                qav_casing_is_largest_single_material=True, qav_casing_count=counts[geometry.QAV],
                bilateral_symmetry=dict(passed=True, axis=f'X={geometry.CX}', mirrored_cells=len(cells) - sum(1 for x, _, _ in cells if x == geometry.CX)),
                controller=dict(position=data['controller'], center_x_zero_based=geometry.CX, ordinal_from_left=geometry.CX + 1),
                port_checks=marker_checks, path_checks=path_checks, checks=[
                    '声明尺寸与实际实体边界一致，逐轴超过最新占地表下限。',
                    'QAV为最大单一材料；HK3GTL自有材料仅对应电压机壳及工业接口占位块。',
                    '实体方块数、材料种类、包围盒体积、实际高度均超过全部较低电压形态。',
                    '钻石主控位于整宽中轴；所有标记齐平嵌入连续设备表面，内有背板、外留四格净空。',
                    '主控操作区与后侧交接操作区逐格检查无占用。',
                    '六邻接遍历确认全体为单一连续组件。',
                    '资源读取增强版当前2.9.2实例及启用资源包，静态完整方块使用真实首帧贴图。'],
                not_verified=['实际Controller/Pattern、额定EU、正式仓室能力、工艺配方与游戏内成型。',
                              '普通建材的最终有效配方、研究前置及生存获取链。',
                              '真实/模拟日志、技术残片与实验材料接入，以及逆向档案、可复现样件和失败样件交付逻辑。',
                              '档案证据与研究许可联动、耗料复现及既有舰船蓝图解析/授权复制的游戏逻辑。',
                              '43条静态源配方的最终执行绑定和逐项运行验收；源配方计数不是运行完成率。',
                              '运行光照、动态材质、扫描与检修行车动画；当前为静态建筑表达。'])


def build_viewer():
    source = (ROOT / 'tools/structure_delivery/build_i26_terminal_viewer_v2_20261026.mjs').read_text(encoding='utf-8')
    source = source.replace("const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');",
                            'const root = ' + json.dumps(ROOT.as_posix()) + ';')
    source = source.replace('const matrix=new THREE.Matrix4(),quaternions=',
                            'const matrix=new THREE.Matrix4(),position=new THREE.Vector3(),scale=new THREE.Vector3(1,1,1),quaternions=')
    source = source.replace('mesh.castShadow=false;', 'mesh.frustumCulled=false;mesh.castShadow=false;')
    source = source.replace('let rebuildQueued=false;\nfunction scheduleRebuild',
                            'let rebuildQueued=false,initScheduled=false;\nconst initQueue=new Set();\nfunction scheduleRebuild')
    source = source.replace('function rebuild(){\n  const layer=', '''function scheduleMatrixInit(){if(initScheduled)return;initScheduled=true;requestAnimationFrame(initializeMatrixChunk);}
function initializeMatrixChunk(){
  initScheduled=false;let budget=40000,changed=false;
  for(const mesh of initQueue){
    const {indices,face}=mesh.userData,start=mesh.userData.initialized,target=mesh.userData.targetCount;
    if(target<=start){mesh.count=target;initQueue.delete(mesh);continue;}
    const end=Math.min(target,start+budget);
    for(let i=start;i<end;i++){
      const index=indices[i],y=Math.floor(index/(W*D)),z=Math.floor(index/W)%D,x=index%W;
      let px=x+.5,py=y+.5,pz=z+.5;
      if(face===0)px=x+1;else if(face===1)px=x;
      else if(face===2)pz=z+1;else if(face===3)pz=z;
      else if(face===4)py=y;else py=y+1;
      position.set(px,py,pz);matrix.compose(position,quaternions[face],scale);mesh.setMatrixAt(i,matrix);
    }
    mesh.userData.initialized=end;mesh.count=end;
    const attribute=mesh.instanceMatrix;attribute.clearUpdateRanges();attribute.addUpdateRange(start*16,(end-start)*16);attribute.needsUpdate=true;
    if(end&&!mesh.userData.boundsReady){mesh.computeBoundingSphere();mesh.userData.boundsReady=true;}
    if(end>=target)initQueue.delete(mesh);
    budget-=end-start;changed=true;if(budget<=0)break;
  }
  if(changed){updateVisibility();document.getElementById('status').textContent=initQueue.size?'正在逐帧建立三维表面… '+stateMeshes.reduce((sum,m)=>sum+m.userData.initialized,0).toLocaleString()+' / '+audit.viewer_surface_faces.toLocaleString()+' 片':'三维表面已就绪。';}
  if(initQueue.size)scheduleMatrixInit();
}
function rebuild(){\n  const layer=''')
    source = source.replace('''    if(n>mesh.userData.initialized){
      for(let i=mesh.userData.initialized;i<n;i++){
        const index=indices[i],y=Math.floor(index/(W*D)),z=Math.floor(index/W)%D,x=index%W;
        let px=x+.5,py=y+.5,pz=z+.5;
        if(face===0)px=x+1;else if(face===1)px=x;
        else if(face===2)pz=z+1;else if(face===3)pz=z;
        else if(face===4)py=y;else py=y+1;
        matrix.compose(new THREE.Vector3(px,py,pz),quaternions[face],new THREE.Vector3(1,1,1));
        mesh.setMatrixAt(i,matrix);
      }
      mesh.userData.initialized=n;mesh.instanceMatrix.needsUpdate=true;
    }
    mesh.count=n;
    if(n&&!mesh.userData.boundsReady){mesh.computeBoundingSphere();mesh.userData.boundsReady=true;}''', '''    mesh.userData.targetCount=n;
    if(n>mesh.userData.initialized){mesh.count=mesh.userData.initialized;initQueue.add(mesh);}
    else{mesh.count=n;initQueue.delete(mesh);}''')
    source = source.replace('  requestRender();\n}\nfunction updateVisibility(){',
                            '  requestRender();\n  if(initQueue.size)scheduleMatrixInit();\n}\nfunction updateVisibility(){')
    additions = r'''
source=source.replace(/const views=\{[\s\S]*?\n\};\nfunction setView/, `const views={
panel:{pos:[cx,data.controller[1]+6,-L],target:[...data.controller],name:'主控接口'},
front:{pos:[cx-L*1.1,H*.7+L*.45,cz-L*1.2],target:[cx,H*.43,cz],name:'前左整体'},
right:{pos:[cx+L*1.1,H*.7+L*.45,cz-L*1.2],target:[cx,H*.43,cz],name:'前右整体'},
back:{pos:[cx-L*1.1,H*.7+L*.45,cz+L*1.2],target:[cx,H*.43,cz],name:'后侧样件与档案交接'},
top:{pos:[cx,H+L,cz],target:[cx,0,cz],name:'正俯视 · 占地与通道'},
inside:{pos:[cx+L*.95,H*.6+L*.6,cz-L*1.1],target:[cx,H*.25,cz],name:'分层剖面 · 玻璃隐藏'},
orthofront:{pos:[cx,H*.5,-L*1.2],target:[cx,H*.5,cz],name:'正前投影'},
orthoside:{pos:[-L*1.2,H*.5,cz],target:[cx,H*.5,cz],name:'正侧投影'}
};
function setView`);
if(source.includes('H*.85+24'))throw new Error('大型结构相机预设替换失败');
source=source.replace('const half=L*.72','const half=L*.62');
source=source.replace("camera.zoom=name==='panel'?L/12:1;",'camera.zoom=1;');
source=source.replace("function setView(name){", "function setView(name){if(name==='controller'||name==='panel'){focusPort({id:'主控',pos:data.controller,face:data.controller_face??'north'});return;}");
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
source=source.replace("data.key+'-研究所候选02-三维结构预览.png'", "data.key+'-遗构剖析院V1-三维预览.png'");
'''
    source = source.replace('const oldHotPaths = ', additions + '\nconst oldHotPaths = ')
    source = source.replace('I26码头预览', 'I32逆向实验预览').replace('virtual:i26-terminal', 'virtual:i32-reverse-lab')
    required = ['scheduleMatrixInit(){', 'attribute.addUpdateRange(start*16,(end-start)*16)', 'initQueue.add(mesh)']
    if not all(token in source for token in required):
        raise RuntimeError('I32逐帧实例初始化补丁未完整应用')
    path = OUT / '生成脚本/build_i32_viewer_v1_20261027.mjs'
    path.write_text(source, encoding='utf-8')
    subprocess.run(['node', str(path), str(VIEW)], cwd=ROOT, check=True)


def viewer_page(data, check):
    css = re.search(r'<style>(.*?)</style>', (PRIOR_VIEW / '三维评审.html').read_text(encoding='utf-8'), re.S).group(1)
    w, h, d = data['size']; p = data['controller']; ordinal = [v + 1 for v in p]
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I32 · {TITLE} V1</title><style>{css}</style>
<header><a href="../index.html">← I32交付总览</a><h1>I32 · {TITLE} V1</h1><div>{w}×{d}×{h}（宽×长×高） · {check['blocks']:,}方块 · 独立结构候选</div></header>
<main class="review"><section id="stage"><div id="loading">加载真实材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="locator"><b>主控蓝图 {p}</b><p>从1起算格位 {ordinal}；整宽第{geometry.CX + 1}格，齐平嵌入实验室控制设施表面。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后侧交接区</button><button data-view="top">俯视</button><button data-view="inside">剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">{h - 1}</b><input id="layer" type="range" min="0" max="{h - 1}" value="{h - 1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>遗构剖析院</summary><p>三道高跨扫描拱围住拆解中的遗留装置，两侧分层样本实验室与档案比对区并行展开；检修行车、拆解地轨连接洁净制样和失败样件交接。锈红QAV机壳统领主体，银灰结构与冰蓝观察带划分工位。</p><p>I32接收真实/模拟日志、技术残片与实验材料，计划输出逆向档案、可复现样件和失败样件。档案只提供研究证据，复现仍须耗料；当前为结构候选，正式工艺尚未接通。</p></details>
<details open><summary>主控与设备内嵌接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>结构文件与验收边界</summary><a href="{NAME}.nbt">NBT</a> · <a href="{NAME}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>候选尚未批准、未接入实例；Pattern、正式控制器、配方、生存获取与游戏内逆向实验均未验收。分层与隐藏材质仅调整原有外露面，不补画原来被遮挡的面。</p></details></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''


def report_page(data, check):
    rows = ''.join(f'<tr><td>{label}</td><td>{check["voltage_progression"]["metrics"][key]:,}</td><td>{check["voltage_progression"]["lower_maxima"][key]["value"]:,}</td><td>通过</td></tr>'
                   for key, label in [('blocks', '实体方块数'), ('materials', '唯一材料数'), ('volume', '实体包围盒体积'), ('height', '实际高度')])
    zones = ''.join(f'<li>{html.escape(z["name"])}</li>' for z in data['zones'])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I32 · {TITLE} V1</title><style>
body{{max-width:1380px;margin:30px auto;padding:0 22px;background:#111b28;color:#e5edf5;font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}}a{{color:#b4dbe8}}img{{max-width:100%;height:auto}}.note{{padding:15px;background:#283044;border-left:3px solid #ac96c6}}table{{border-collapse:collapse;width:100%}}td,th{{padding:10px;border-bottom:1px solid #425065;text-align:left}}.links{{display:flex;gap:20px;flex-wrap:wrap}}small{{color:#aabbcc}}
</style><small>HK3GTL / I32 / QAV·V08 / 遗构剖析院候选 V1</small><h1>{TITLE}</h1><p class="note">{html.escape(data['description'])}</p>
<p>{data['size'][0]}×{data['size'][2]}×{data['size'][1]}（宽×长×高） · {check['blocks']:,}个实体方块 · {check['unique_materials']}种真实材料 · QAV主体机壳{check['qav_casing_count']:,}块</p>
<p class="links"><a href="i32/三维评审.html">打开三维评审</a><a href="等轴预览.png">查看完整等轴图</a><a href="verification.json">静态核验</a><a href="材料清单.json">材料清单</a><a href="设计依据.json">设计依据</a></p><img src="等轴预览.png" alt="I32真实逐格材质完整等轴预览">
<h2>功能组织</h2><ul>{zones}</ul><p>三道高跨扫描拱围住遗留装置拆解工位；双侧分层样本实验室与档案比对区，配合检修行车、拆解地轨、洁净制样及失败样件交接。输入真实/模拟日志、技术残片和实验材料，计划输出逆向档案、可复现样件和失败样件。档案提供证据，研究系统判定许可；复现必须耗料，既有舰船蓝图仅按授权解析与复制。普通化工和部件量产交GT及现有工厂。</p>
<h2>电压递增量化核验</h2><p>逐格读取当前28个正式低阶蓝图，包含I01冻结V2、I05正式V5与S01–S03。同阶I26及更高阶I27–I31不纳入递增比较。高度由高跨扫描拱及实验设施本体形成。四项量化检查为100%；华丽度、功能可读性与风格仍待负责人评审。</p><table><thead><tr><th>指标</th><th>I32实测</th><th>低阶最大值</th><th>量化结果</th></tr></thead><tbody>{rows}</tbody></table>
<h2>主控与接口</h2><p>钻石块仅标记主控；工业接口块仅表示正式Pattern可规划的仓室位置。主控整宽居中，全部接口齐平融入各自设备，外侧四格净空、内侧背板及周边外壳已检查。精确蓝图坐标及朝向见三维页。</p>
<p>三维仅提交{check['viewer_surface_faces']:,}片外露面；gzip载荷，按需重绘。隐藏材质不会挖开原有实心构件补画内部。</p>
<p class="note">外观候选尚未批准、未接入实例。静态几何与资源核验通过不代表Pattern、正式控制器、配方、研究与生存获取链、逆向实验逻辑或游戏成型通过；所有图像与三维均来自同一最终逐格数据。</p></html>'''


def material_records(materials, check, evidence):
    role_by_state = geometry.PALETTE_ROLES
    result = []
    for m in materials:
        state = m['state']; base = state.split('[')[0]; ns, key = base.split(':')
        refs = [{k:v for k,v in item.items() if k != 'context'} for item in evidence.get('recipe_evidence', []) if base in item.get('states', [])]
        if state == geometry.QAV:
            refs.append(dict(path='src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3VoltageCasingRecipes.java',
                             meaning='项目现行机壳注册入口；完整研究与主材首通链仍须游戏验收。'))
        resource = check['material_resource_sources'].get(f'assets/{ns}/blockstates/{key}.json')
        phase = '指定主控/接口位置标记，不作为普通建材核验。' if state in (geometry.CONTROL,geometry.PORT) else (
            '附静态配方/脚本引用；旧版参考与当前引用分别保留，最终有效获取链尚未验收。' if refs else '当前真实资源已核验；尚无本轮最终有效获取链证据。')
        role = role_by_state.get(state, role_by_state.get(base))
        assert role, ('材质用途未定义', state)
        result.append(dict(state=state, count=check['palette'][state], role=role, complete_cube=m['complete_cube'],
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
    evidence = {}
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
    raw_payload = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    zipped_payload = gzip.compress(raw_payload, 9)
    encoded = base64.b64encode(zipped_payload).decode('ascii')
    check.update(viewer_payload_gzip_bytes=len(zipped_payload), viewer_payload_base64_bytes=len(encoded),
                 viewer_material_face_count=sum(len(m['faces']) for m in materials),
                 viewer_texture_png_bytes=sum(((len(face.split(',', 1)[1]) * 3) // 4) - (face.split(',', 1)[1].count('=') if '=' in face else 0)
                                              for m in materials for face in m['faces'].values()))
    assert json.loads(gzip.decompress(base64.b64decode(encoded))) == payload
    (VIEW / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    del payload, surfaces
    build_viewer(); render_previews(data, materials)
    (VIEW / '三维评审.html').write_text(viewer_page(data, check), encoding='utf-8')
    (OUT / 'index.html').write_text(report_page(data, check), encoding='utf-8')
    manifest = dict({k: v for k, v in data.items() if k != 'blocks'}, candidate_version='V1', status='candidate_waiting_user_review',
                    approved=False, target_voltage='QAV', voltage_mapping='V08 / tier22', blocks=check['blocks'], unique_materials=check['unique_materials'],
                    geometry_passed=True, source_instance=str(INSTANCE), instance_version=version, generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds'))
    save(OUT / 'manifest.json', manifest); save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', material_records(materials, check, evidence))
    save(OUT / '设计依据.json', [
        dict(path='doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html', fact='I32最低宽长高41×49×37；尺寸为下限，不限制工程扩展。'),
        dict(path='doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html', line=130, fact='I32为QAV/V08/tier22，主体使用QAV电压机壳；同阶I26及更高电压形态不纳入递增比较。'),
        dict(path='doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json', lines=[1949, 2968], fact='I32输入真实/模拟日志、技术残片与实验材料，输出逆向档案、可复现样件和失败样件；职责包含遗留装置拆解、档案交叉验证、既有舰船蓝图解析及授权复制。'),
        dict(path='rule/当前多方块设计规则.md', fact='主控居中、接口嵌入设备主体、项目材料白名单、全部低阶量化比较。'),
        dict(path='doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json', lines=[1949, 2968], fact='解析档案不自动解锁研究，复现样件必须耗料；普通化工与部件量产返回GT和现有工厂。43为静态源配方计数：13实验、29制样和1其他，不代表运行完成率。')])
    shutil.copy2(__file__, OUT / '生成脚本' / 'build_i32_relic_reverse_lab_v1_20261027.py')
    shutil.copy2(geometry.__file__, OUT / '生成脚本' / Path(geometry.__file__).name)
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'], size=data['size'], faces=check['viewer_surface_faces']), ensure_ascii=False))


if __name__ == '__main__':
    main()
