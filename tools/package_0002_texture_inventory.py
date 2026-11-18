# -*- coding: utf-8 -*-
from collections import Counter, defaultdict
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo
import csv
import hashlib
import json
import os

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/textures-r10-adoption-inventory-0002-20261115'
FLUID_LOG = ROOT / 'logs/textures-fluid-redraw-0002-r11-20261115'
LATEST_LOG = ROOT / 'logs/textures-latest-adoption-0002-r12-20261115'
RUNTIME_LOG = ROOT / 'logs/textures-runtime-integration-0002-r13-20261115'
OUT = ROOT / 'deliveries/0002贴图材质_全库材质清单_R10采用_20261115'
TEXTURES = ROOT / 'src/main/resources/assets/hk3gtl/textures'
FONT = 'C:/Windows/Fonts/msyh.ttc'
NAME_SOURCES = {'direct_language_key': '直接语言键', 'model_binding': '模型绑定名称',
                'controller_directory_and_language': '控制器目录与语言键推导',
                'language_and_texture_role': '语言键与材质部位推导',
                'resource_role_description': '资源用途说明（非注册名）'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def link(path):
    return quote(os.path.relpath(path, OUT).replace('\\', '/'), safe='/.:')


PAGE = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>0002 · 全库材质清单 · 最新版材质已采用</title>
<style>
:root{color-scheme:dark;--bg:#11181e;--panel:#1b252e;--line:#34424f;--ink:#eef4f6;--muted:#aab9c4;--accent:#76d6c4}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 "Microsoft YaHei",sans-serif}main{max-width:1600px;margin:auto;padding:28px}h1{margin:0 0 8px;font-size:29px}h2{font-size:18px;margin:0}p{margin:8px 0}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}.muted,small{color:var(--muted)}code{font:12px/1.5 Consolas,monospace;overflow-wrap:anywhere}.intro{max-width:1100px}.stats{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0}.stat{border:1px solid var(--line);background:var(--panel);padding:12px 18px;min-width:145px}.stat b{font-size:26px;display:block;color:var(--accent)}
nav{display:flex;gap:18px;flex-wrap:wrap;margin:14px 0}.filters{position:sticky;top:0;z-index:2;display:flex;flex-wrap:wrap;gap:9px;padding:14px 0;background:var(--bg);border-bottom:1px solid var(--line)}input,select,button,textarea{font:inherit;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:4px;padding:9px}input[type=search]{flex:1;min-width:230px}button{cursor:pointer}button:hover{border-color:var(--accent)}button:disabled{opacity:.4;cursor:default}input[type=checkbox]{accent-color:var(--accent)}.resultbar,.paging{display:flex;justify-content:space-between;align-items:center;gap:14px;margin:15px 0;flex-wrap:wrap}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(235px,1fr));gap:14px}.card{min-width:0;border:1px solid var(--line);background:var(--panel);border-radius:5px;overflow:hidden}.preview{display:flex;align-items:center;justify-content:center;height:190px;background-color:#e5e9ed;background-image:linear-gradient(45deg,#c6cdd4 25%,transparent 25%),linear-gradient(-45deg,#c6cdd4 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#c6cdd4 75%),linear-gradient(-45deg,transparent 75%,#c6cdd4 75%);background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0}
.preview img{max-width:180px;max-height:180px;image-rendering:pixelated;object-fit:contain}.cardbody{padding:13px}.card h2{font-size:16px;line-height:1.45;min-height:46px}.path{display:block;min-height:38px;margin:7px 0}.tags{display:flex;flex-wrap:wrap;gap:5px;margin:8px 0}.tag{font-size:11px;border:1px solid var(--line);color:var(--muted);padding:1px 5px;border-radius:3px}.approved{color:#95dec8}.pending{color:#e7cb83}.chosen{display:flex;align-items:center;gap:8px;margin-top:10px;font-size:13px}.details{border-top:1px solid var(--line);padding-top:7px;font-size:12px;color:var(--muted)}.details p{overflow-wrap:anywhere}summary{cursor:pointer}footer{border-top:1px solid var(--line);margin-top:25px;padding-top:15px;color:var(--muted);font-size:13px}dialog{background:var(--bg);color:var(--ink);border:1px solid var(--line);width:min(900px,95vw)}dialog::backdrop{background:#000a}textarea{display:block;width:100%;height:50vh;margin:14px 0;resize:vertical}.empty{padding:60px;text-align:center;color:var(--muted)}@media(max-width:600px){main{padding:16px}h1{font-size:24px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.preview{height:145px}.preview img{max-width:135px;max-height:135px}.cardbody{padding:9px}.card h2{font-size:14px}.stat{min-width:120px;padding:9px 12px}.filters select{max-width:100%}}
</style></head><body><main>
<header><p class="muted">HK3GTL · 0002贴图材质 · 2026-11-15源码快照</p><h1>全库材质清单 · 最新版材质已采用</h1>
<p class="intro">负责人决定已绘制贴图全部采用各自最新版：R12物品与独立研究计算机已接入，R9剩余两项同步采用；R5燃料、R7控制器、R8r1工业物品、R10及R11流体保持当前最新版。55项旧贴图继续保留。</p>
<div class="stats"><div class="stat"><b>1633</b>全部PNG路径</div><div class="stat"><b>1594</b>除R10外</div><div class="stat"><b>18</b>资源分类</div><div class="stat"><b>163</b>动画PNG</div></div>
<nav><a href="../0002贴图材质_实例接入_R14_20261115/index.html">R14实际实例接入</a><a href="R13_LINK">R13全部接入与天枢</a><a href="../0002%E8%B4%B4%E5%9B%BE%E6%9D%90%E8%B4%A8_%E6%8C%87%E5%AE%9A%E7%89%A9%E5%93%81%E4%B8%8E%E7%A0%94%E7%A9%B6%E8%AE%A1%E7%AE%97%E6%9C%BA_R12_20261115/index.html">R12已采用物品与研究计算机</a><a href="R10_LINK">R10已采用的39张</a><a href="manifest.json">完整JSON</a><a href="textures.csv">完整CSV</a><a href="overview.png">分类总览</a><a href="REPORT_LINK">固定进度报告</a></nav>
<details class="muted"><summary>清点范围与状态说明</summary><p>按源码独立PNG路径计数，包含物品、方块、流体、实体、特效和界面。不同路径即使图像相同也逐项列出；动画条带按一张PNG计数，缩略图显示第一帧。仅清单缩略图缩小，源码与完整PNG保持原尺寸。</p><p>中文名优先取语言键与模型引用；推导名称会单独标注。模型JSON未发现引用不代表未使用，Java动态渲染、运行时染色及第三方模组材质不由此判断。第三方JAR或MC内置图片不计为本模组独立PNG。</p><p>“已认可”表示已有明确美术决定；“待审”表示已接入源码但未获逐项认可；“未逐项评审”表示本次没有找到明确批准记录。当前已绘制批次按负责人最新版决定标记已采用；没有独立新稿的历史资源继续保留原记录。R11为47种流体、94个PNG资源路径。R13天枢沿用R7整机几何投影，已接入、待负责人查看。</p><p>BUILD_STATUS。对话ID：01a1d68a-a994-7ac0-a48a-54c0f98fd54e。</p></details></header>
<section class="filters" aria-label="筛选材质"><input id="search" type="search" placeholder="搜索中文名、ID、路径或模型" aria-label="搜索材质">
<select id="scope" aria-label="范围"><option value="other">其余1594张</option><option value="all">全部1633张</option><option value="r10">已采用R10 · 39张</option><option value="selected">仅看已勾选</option></select>
<select id="group" aria-label="类别"><option value="all">全部类别</option></select>
<select id="status" aria-label="评审状态"><option value="all">全部状态</option><option value="approved">已认可</option><option value="pending">待审</option><option value="unknown">未逐项评审</option></select>
<button id="selection">整理已选（0）</button></section>
<div class="resultbar"><span id="count" class="muted"></span><span class="muted">勾选仅整理下一轮名单，不会改动资源</span></div>
<div id="grid" class="grid"></div><div class="paging"><button id="prev">上一页</button><span id="page" class="muted"></span><button id="next">下一页</button></div>
<footer>SNAPSHOT_TEXT<br>资源根：<code>src/main/resources/assets/hk3gtl/textures</code> · 完整资源以本轮清单与文件哈希为准。</footer>
<dialog id="dialog"><h2>下一轮候选名单</h2><p class="muted">可直接复制下面的名称与资源路径；勾选不会自动发起重画。</p><textarea id="selectionText" readonly aria-label="已选材质"></textarea><button id="close">关闭</button></dialog>
<script type="application/json" id="inventory-data">INVENTORY_DATA</script>
<script>
const data=JSON.parse(document.getElementById('inventory-data').textContent);
const $=id=>document.getElementById(id),selected=new Set();let page=0;const pageSize=72;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
data.groups.forEach(g=>{const o=document.createElement('option');o.value=g.key;o.textContent=g.label+'（'+g.count+'）';$('group').append(o)});
const searchText=r=>[r.name,r.textureId,r.path,...r.names,...r.modelRefs.map(m=>m.modelId)].join(' ').toLowerCase();
data.records.forEach(r=>r.search=searchText(r));
function filtered(){const q=$('search').value.trim().toLowerCase(),scope=$('scope').value,g=$('group').value,s=$('status').value;return data.records.filter(r=>(scope==='all'||scope==='other'&&!r.r10||scope==='r10'&&r.r10||scope==='selected'&&selected.has(r.path))&&(g==='all'||r.group===g)&&(s==='all'||r.statusKey===s)&&(!q||r.search.includes(q)))}
function card(r){return '<article class="card"><a class="preview" href="'+esc(r.sourceImage)+'" target="_blank" rel="noopener" title="打开完整PNG"><img loading="lazy" src="'+esc(r.thumbnail)+'" alt="'+esc(r.name)+'"></a><div class="cardbody"><h2>'+esc(r.name)+'</h2><code class="path">'+esc(r.textureId)+'</code><div class="tags"><span class="tag">'+r.size[0]+'×'+r.size[1]+'</span><span class="tag '+r.statusKey+'">'+esc(r.status)+'</span>'+(r.batch?'<span class="tag">'+esc(r.batch)+'</span>':'')+(r.animated?'<span class="tag">动画首帧</span>':'')+(r.sameImageCount>1?'<span class="tag">相同图像 '+r.sameImageCount+' 路径</span>':'')+'</div><small>'+esc(r.groupLabel)+'</small><label class="chosen"><input type="checkbox" data-path="'+esc(r.path)+'" '+(selected.has(r.path)?'checked':'')+'>加入下一轮名单</label><details class="details"><summary>名称、路径与引用</summary><p>名称来源：'+esc(r.nameSource)+'</p><p>'+esc(r.sourcePath)+'</p><p>'+esc(r.note)+'</p><p>模型引用：'+r.modelRefCount+' 份，仅显示前12份。</p>'+r.modelRefs.slice(0,12).map(m=>'<p><code>'+esc(m.modelId)+'</code></p>').join('')+'<p><a href="'+esc(r.sourceImage)+'" target="_blank" rel="noopener">完整PNG</a> · SHA256：<code>'+r.sha256+'</code></p></details></div></article>'}
function render(){const rows=filtered(),pages=Math.max(1,Math.ceil(rows.length/pageSize));page=Math.min(page,pages-1);$('grid').innerHTML=rows.slice(page*pageSize,(page+1)*pageSize).map(card).join('')||'<p class="empty">没有匹配的材质。</p>';$('count').textContent='匹配 '+rows.length+' 张 · 当前显示 '+(rows.length?page*pageSize+1:0)+'–'+Math.min((page+1)*pageSize,rows.length);$('page').textContent='第 '+(page+1)+' / '+pages+' 页';$('prev').disabled=page===0;$('next').disabled=page>=pages-1;$('selection').textContent='整理已选（'+selected.size+'）'}
['search','scope','group','status'].forEach(id=>$(id).addEventListener(id==='search'?'input':'change',()=>{page=0;render()}));
$('grid').addEventListener('change',e=>{const p=e.target.dataset.path;if(!p)return;e.target.checked?selected.add(p):selected.delete(p);$('selection').textContent='整理已选（'+selected.size+'）';if($('scope').value==='selected')render()});
$('prev').onclick=()=>{page--;render();$('count').scrollIntoView({block:'center'})};$('next').onclick=()=>{page++;render();$('count').scrollIntoView({block:'center'})};
$('selection').onclick=()=>{$('selectionText').value=data.records.filter(r=>selected.has(r.path)).map((r,i)=>(i+1)+'. '+r.name+'\n'+r.textureId+'\n'+r.sourcePath).join('\n\n');$('dialog').showModal();$('selectionText').select()};$('close').onclick=()=>$('dialog').close();render();
</script></main></body></html>'''


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / 'thumbnails').mkdir(exist_ok=True)
    names = read(LOG / 'names-and-model-refs.json')['records']
    provenance = read(LOG / 'provenance.json')['records']
    scope = read(LOG / 'scope-and-groups.json')
    adoption = read(LOG / 'art-adoption.json')
    fluid_scope = {fluid['id']: fluid for fluid in read(FLUID_LOG / 'fluid-scope.json')['fluids']}
    fluid_records = read(FLUID_LOG / 'manifest.json')['records']
    approval = read(FLUID_LOG / 'art-approval.json')
    hashes = read(ROOT / adoption['backup'] / 'all-texture-hashes.json')
    hashes.update({r['path']: r['sha256'] for r in adoption['records']})
    fluid_paths = set()
    for fluid in fluid_records:
        facts = fluid_scope[fluid['id']]
        for texture in fluid['textures']:
            source = texture['path']
            relative = Path(source).relative_to(TEXTURES.relative_to(ROOT)).as_posix()
            role = '流动帧带' if relative.endswith('_flow.png') else '静止帧带'
            display = facts['name'] + ' · ' + role
            names[source] = {'resource': texture['resource'], 'path': relative,
                             'displayName': display, 'nameSource': 'language_and_texture_role',
                             'names': [facts['name']], 'languageKeys': ['material.hk3gtl.' + fluid['id']],
                             'role': role, 'modelRefCount': 0, 'modelRefs': []}
            provenance[source] = {'name': display, 'batch': 'R11',
                                  'status': '已认可采用' if approval['artApproved'] else '待审',
                                  'artApproved': approval['artApproved'], 'family': facts['family'],
                                  'source': 'logs/textures-fluid-redraw-0002-r11-20261115/manifest.json',
                                  'note': ('负责人已认可R11全流体新绘；' if approval['artApproved'] else 'R11全流体新绘，待美术评审；') + facts['purpose']}
            hashes[source] = texture['sha256']
            fluid_paths.add(relative)
    fluid_group = next(group for group in scope['groups'] if group['key'] == 'fluids')
    fluid_group['paths'] = sorted(set(fluid_group['paths']) | fluid_paths)
    scope['animationPaths'] = sorted(set(scope['animationPaths']) | fluid_paths)
    latest = read(LATEST_LOG / 'art-adoption.json')
    for origin in provenance.values():
        origin.update(status='已认可采用', artApproved=True,
                      note='负责人决定所有贴图采用各自最新版。',
                      approvalReceipt='logs/textures-latest-adoption-0002-r12-20261115/art-adoption.json')
    for record in latest['records']:
        source, requested = record['path'], record['requestedPath']
        relative = Path(source).relative_to(TEXTURES.relative_to(ROOT)).as_posix()
        if source != requested:
            names[source] = {**names[requested], 'resource': 'hk3gtl:' + relative[:-4], 'path': relative,
                             'modelRefCount': 1, 'modelRefs': [{'modelId': 'hk3gtl:block/research_point_computer_r12'}]}
            old_relative = Path(requested).relative_to(TEXTURES.relative_to(ROOT)).as_posix()
            next(group for group in scope['groups'] if old_relative in group['paths'])['paths'].append(relative)
        provenance[source] = {'name': record['name'], 'batch': record['batch'], 'status': '已认可采用',
                              'artApproved': True, 'note': '负责人采用最新版；保留原尺寸。',
                              'source': 'logs/textures-latest-adoption-0002-r12-20261115/art-adoption.json'}
        hashes[source] = record['sha256']
    relative = 'block/ae_nexus_controller_r13/front.png'
    source = (TEXTURES / relative).relative_to(ROOT).as_posix()
    names[source] = {'resource': 'hk3gtl:' + relative[:-4], 'path': relative,
                     'displayName': '万象天枢控制器 · 正面', 'nameSource': 'model_binding',
                     'names': ['万象天枢控制器'], 'languageKeys': ['block.hk3gtl.ae_nexus'],
                     'role': '正面', 'modelRefCount': 1,
                     'modelRefs': [{'modelId': 'hk3gtl:block/ae_nexus_controller_r13',
                                    'modelPath': 'src/main/resources/assets/hk3gtl/models/block/ae_nexus_controller_r13.json',
                                    'slots': ['north'], 'kind': 'direct'}]}
    provenance[source] = {'name': '万象天枢控制器 · 正面', 'batch': 'R13',
                          'status': '已接入，待负责人查看', 'artApproved': False, 'sourceApplied': True,
                          'source': 'logs/textures-runtime-integration-0002-r13-20261115/nexus-texture.json',
                          'note': '沿用R7控制器流程，按正式A1完整NBT生成原生64×64整机几何投影。'}
    hashes[source] = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
    next(group for group in scope['groups'] if group['key'] == 'block_overlays')['paths'].append(relative)
    certificate = names['src/main/resources/assets/hk3gtl/textures/item/easter_egg/non_qiu_certificate.png']
    certificate.update(modelRefCount=1, modelRefs=[{
        'modelId': 'hk3gtl:item/non_qiu_certificate',
        'modelPath': 'src/main/resources/assets/hk3gtl/models/item/non_qiu_certificate.json',
        'slots': ['layer0'], 'kind': 'direct'}])
    bucket = names['src/main/resources/assets/hk3gtl/textures/item/honkai/liquid_honkai_energy_bucket.png']
    bucket['modelRefs'].append({'modelId': 'hk3gtl:item/liquid_honkai_energy_bucket',
                                'modelPath': 'src/main/resources/assets/hk3gtl/models/item/liquid_honkai_energy_bucket.json',
                                'slots': ['layer0'], 'kind': 'inherited'})
    bucket['modelRefCount'] = len(bucket['modelRefs'])
    paths = sorted(TEXTURES.rglob('*.png'))
    existing = {p.relative_to(TEXTURES).as_posix() for p in paths}
    hashes = {p.relative_to(ROOT).as_posix(): hashes[p.relative_to(ROOT).as_posix()] for p in paths}
    for group in scope['groups']:
        group['paths'] = [p for p in group['paths'] if p in existing]
        group['count'] = len(group['paths'])
    scope['animationPaths'] = [p for p in scope['animationPaths'] if p in existing]
    metadata_count = len(list(TEXTURES.rglob('*.mcmeta')))
    scope['notes'] = [note.replace('1633', str(len(paths))).replace('179', str(metadata_count)).replace('163份', str(len(scope['animationPaths']))+'份') for note in scope['notes']]
    r10 = {r['path'] for r in adoption['records']}
    group_by_path = {p: g for g in scope['groups'] for p in g['paths']}
    duplicate_paths = defaultdict(list)
    for path, digest in hashes.items():
        duplicate_paths[digest].append(path)
    records = []
    for path in paths:
        source = path.relative_to(ROOT).as_posix()
        relative = path.relative_to(TEXTURES).as_posix()
        name = names[source]
        origin = provenance.get(source, {})
        group = group_by_path[relative]
        digest = hashes[source]
        thumbnail = OUT / 'thumbnails' / (digest + '.png')
        animated = relative in scope['animationPaths']
        with Image.open(path) as image:
            size, mode = list(image.size), image.mode
            frame_size = size
            preview = image.convert('RGBA')
            if animated:
                animation = read(path.with_suffix('.png.mcmeta'))['animation']
                side = min(size)
                width, height = animation.get('width', side), animation.get('height', side)
                frames = animation.get('frames', [0])
                first = frames[0] if isinstance(frames[0], int) else frames[0]['index']
                x, y = first % (size[0] // width) * width, first // (size[0] // width) * height
                preview = preview.crop((x, y, x + width, y + height))
                frame_size = [width, height]
            scale = min(180 / preview.width, 180 / preview.height)
            preview.resize((round(preview.width * scale), round(preview.height * scale)), Image.Resampling.NEAREST).save(thumbnail)
        status_key = 'approved' if origin.get('artApproved') else 'pending' if origin else 'unknown'
        records.append({'name': origin.get('name') or name['displayName'], 'names': name['names'],
                        'textureId': name['resource'], 'path': relative, 'sourcePath': source,
                        'nameSource': NAME_SOURCES[name['nameSource']], 'nameSourceKey': name['nameSource'],
                        'group': group['key'], 'groupLabel': group['label'],
                        'topLevel': relative.split('/')[0], 'size': size, 'mode': mode,
                        'animated': animated, 'frameSize': frame_size, 'sha256': digest,
                        'sameImageCount': len(duplicate_paths[digest]), 'r10': source in r10,
                        'batch': origin.get('batch', ''), 'status': origin.get('status', '未逐项评审'),
                        'artApproved': origin.get('artApproved', False), 'family': origin.get('family', ''),
                        'statusKey': status_key, 'note': origin.get('note', '未找到明确逐项美术评审记录；不据此判断是否使用。'),
                        'modelRefCount': name['modelRefCount'], 'modelRefs': name['modelRefs'],
                        'thumbnail': link(thumbnail), 'sourceImage': link(path)})
    now = datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(timespec='seconds')
    manifest = {'updatedAt': now, 'conversation': '0002',
                'conversationId': '01a1d68a-a994-7ac0-a48a-54c0f98fd54e',
                'totalPngCount': len(records), 'r10AdoptedCount': len(r10), 'otherPngCount': len(records)-len(r10),
                'r11RedrawnFluidCount': len(fluid_records), 'r11PngCount': len(fluid_paths),
                'r11ArtApproved': approval['artApproved'],
                'r11ApprovedFluidCount': approval['approvedFluidCount'],
                'historicallyApprovedItemIdCount': approval['existingApprovedItemIdCount'],
                'latestAdoptionPathCount': len(latest['records']),
                'latestArtApprovalReceipt': 'logs/textures-latest-adoption-0002-r12-20261115/art-adoption.json',
                'r11ArtApprovalReceipt': 'logs/textures-fluid-redraw-0002-r11-20261115/art-approval.json',
                'topLevelCounts': dict(Counter(r['topLevel'] for r in records)),
                'statusCounts': dict(Counter(r['statusKey'] for r in records)),
                'uniqueImageCount': len(duplicate_paths), 'duplicateGroupCount': sum(len(p)>1 for p in duplicate_paths.values()),
                'animationCount': len(scope['animationPaths']),
                'groups': [{k: v for k, v in g.items() if k != 'paths'} for g in scope['groups']],
                'scopeNotes': scope['notes'], 'records': records}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    with (OUT / 'textures.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['名称', '纹理ID', '分类', '宽', '高', '模式', '动画', '批次', '评审状态', '名称来源', '模型引用数', '相同图像路径数', '源码路径', 'SHA256'])
        writer.writerows([r['name'], r['textureId'], r['groupLabel'], *r['size'], r['mode'], r['animated'], r['batch'], r['status'], r['nameSource'], r['modelRefCount'], r['sameImageCount'], r['sourcePath'], r['sha256']] for r in records)
    payload = json.dumps(manifest, ensure_ascii=False).replace('</', '<\/')
    completion_path = RUNTIME_LOG / 'completion.json'
    completion = read(completion_path) if completion_path.exists() else {}
    build_status = '本轮JAR已构建；未安装、未启动游戏' if completion.get('build', {}).get('success') else '构建待完成；未安装、未启动游戏'
    instance_receipt = ROOT / 'logs/textures-instance-adoption-0002-r14-20261115/installation.json'
    if instance_receipt.exists() and read(instance_receipt)['installed']:
        build_status = '最新版材质已安装到增强版3.9（0002 R14，基于AE R19）；尚未启动游戏验收'
    page = PAGE.replace('1633', str(len(records))).replace('1594', str(len(records)-len(r10))).replace('<b>163</b>', '<b>'+str(len(scope['animationPaths']))+'</b>')
    page = page.replace('R13_LINK', link(ROOT / 'deliveries/0002贴图材质_全部接入与天枢_R13_20261115/index.html')).replace('BUILD_STATUS', build_status)
    page = page.replace('INVENTORY_DATA', payload).replace('R10_LINK', link(ROOT / 'deliveries/0002贴图材质_R2R3全量试画_R10_20261115/index.html')).replace('REPORT_LINK', link(ROOT / 'logs/beta5-completion-audit-20261030/index.html')).replace('SNAPSHOT_TEXT', escape(now))
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    sheet = Image.new('RGB', (1500, 110 + len(scope['groups']) * 150), '#18232c')
    draw = ImageDraw.Draw(sheet)
    title_font, font = ImageFont.truetype(FONT, 28), ImageFont.truetype(FONT, 15)
    draw.text((24, 16), f'0002 · 全库{len(records)}张材质 · 18类索引', font=title_font, fill='#e8f3f3')
    draw.text((24, 62), f'55项删除已撤销；{len(fluid_records)}种流体{len(fluid_paths)}张已认可采用；本轮52条资源采用最新版。每行展示部分样本。', font=font, fill='#b3c6d0')
    for index, group in enumerate(scope['groups']):
        y = 108 + index * 150
        draw.text((24, y + 10), group['label'], font=font, fill='#e8f3f3')
        draw.text((24, y + 40), str(group['count']) + ' 张', font=font, fill='#76d6c4')
        for column, record in enumerate([r for r in records if r['group'] == group['key']][:8]):
            with Image.open(OUT / record['thumbnail']) as image:
                image.thumbnail((130, 130), Image.Resampling.NEAREST)
                tile = Image.new('RGB', (136, 136), '#d2dbe0')
                tile.paste(image, ((136-image.width)//2, (136-image.height)//2), image)
                sheet.paste(tile, (345 + column * 141, y))
    sheet.save(OUT / 'overview.png')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ['records', 'scopeNotes', 'groups']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
