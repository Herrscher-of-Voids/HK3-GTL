# -*- coding: utf-8 -*-
"""恢复W03／休伯利安评审布局，保留P1、P2几何与源文件历史。"""
from pathlib import Path
from collections import Counter
from datetime import datetime
from html import escape
import base64,gzip,json,re,shutil,hashlib
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'tools/structure_delivery'
P1=ROOT/'deliveries/W04_龙踞雷池七雷镇枢_组合布局_P1_20261110'
P2=ROOT/'deliveries/W04_中轴七雷三巴纹磁环_组合布局_P2_20261110'
LOG=ROOT/'logs/w04-review-ui-restore-20261110'
load=lambda p:json.loads(p.read_text('utf8'))
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def source_counts(folder):
    if (folder/'材料清单.json').is_file():
        return Counter({item['state']:item['count'] for item in load(folder/'材料清单.json')})
    result=Counter()
    for name in ['W04_俱利伽罗_厚躯与肩背_D4_20261110','W04_涤罪七雷鸣雷见_独立小样_S1_20261110']:
        for item in load(ROOT/'deliveries'/name/'材料清单.json'):result[item['state']]+=item['count']
    if folder==P2:
        manifest=load(folder/'manifest.json');data=np.load(ROOT/'logs/w04-layout-p2-20261110/components.npz')
        bounds=manifest['new_voxel_export']['bounds_blueprint'];low=np.array(bounds['min']);size=np.array(bounds['max'])-low+1
        cube=np.zeros((size[1],size[2],size[0]),np.uint8)
        for name in data.files:
            if not name.endswith('__p'):continue
            points=data[name]-low;cube[points[:,1],points[:,2],points[:,0]]=data[name[:-3]+'__states']
        counts=np.bincount(cube.ravel(),minlength=len(manifest['materials']['states'])+1)
        for i,state in enumerate(manifest['materials']['states'],1):result[state]+=int(counts[i])
        assert int(counts[1:].sum())==manifest['new_voxel_blocks']
    return result


def install(folder):
    manifest=load(folder/'manifest.json');is_p3=manifest.get('whole_integer_voxel',False);is_p2=folder==P2
    candidate='W04 P3' if is_p3 else 'W04 P2' if is_p2 else 'W04 P1'
    text=(folder/'data.js').read_text('utf8');payload=json.loads(gzip.decompress(base64.b64decode(json.loads(text.split('=',1)[1].rstrip(';')))))
    counts=source_counts(folder)
    labels={'black_concrete':'黑色混凝土','gray_concrete':'灰色混凝土','red_concrete':'红色混凝土','deepslate_tiles':'深板岩瓦',
        'gold_block':'金块导体','sea_lantern':'海晶灯','voltage_machine_casing_hrv':'HRV绯雷红机壳'}
    materials=[dict(state=s,count=n,label=labels.get(s.split(':')[-1],s.split(':')[-1])) for s,n in counts.items() if n]
    metadata=dict(candidate=candidate,ui_template='W03 C9／休伯利安新版评审',source_voxels=sum(counts.values()),materials=materials,
        scope='D4、S1与新增体素构件的源统计，不含Three.js草模；七雷组合缩放，非正式整机BOM',geometry_unchanged=True)
    if is_p3:metadata.update(whole_integer_voxel=True,scope='整座候选合并后的真实方块材料表，与完整NBT和Schematic一致；W04主控为红石块占位。')
    save(folder/'review-ui.json',metadata)
    template=(ROOT/'deliveries/W03_C9_C5外环下移净空修订_20261108/w03/三维评审.html').read_text('utf8')
    style=re.search(r'<style>(.*?)</style>',template,re.S)[1]
    style+='\n:root{color-scheme:dark}.material[hidden]{display:none}#materialSearch{width:100%;padding:8px;background:#172438;color:white;border:1px solid #51627b}.asset-row{display:block}#stage:fullscreen{width:100vw;height:100vh}#layerLabel{display:none}#stats{color:#afc3d1}.review{height:calc(100dvh - 105px)}'
    views=[('front','前左全景'),('right','前右全景'),('orthofront','正面'),('side','侧面'),('back','背面'),('top','俯视'),
        ('inside','逐层剖切'),('reactor','雷池'),('dragon','龙体'),('sword','七雷')]+([('field','环塔')] if is_p2 or is_p3 else [])
    if is_p3:views += [('head','龙首'),('casing','单格机壳'),('torii','鸟居'),('magnet','磁轭')]
    buttons=''.join(f'<button data-view="{key}">{label}</button>' for key,label in views)
    parts=''.join('<label class="asset-row"><input type="checkbox" checked data-part="'+escape(p['id'])+'">'+escape(p['id'].split('_',1)[1])+'</label>' for p in payload['parts'])
    assets='<label class="asset-row"><input type="checkbox" data-asset="dragon" checked>俱利伽罗 D4</label><label class="asset-row"><input type="checkbox" data-asset="sword" checked>涤罪七雷·鸣雷见 S1</label>'
    if is_p2 or is_p3:assets+='<label class="asset-row"><input type="checkbox" data-asset="field" checked>体素磁环／双塔／母线／电弧</label>'
    scenery='<label class="asset-row"><input type="checkbox" data-scenery="base" checked>工业底盘与设施草模</label><label class="asset-row"><input type="checkbox" data-scenery="energy" checked>静态能量示意</label><label class="asset-row"><input type="checkbox" data-scenery="labels" checked>部件标签</label>'
    if is_p3:
        assets+='<label class="asset-row"><input type="checkbox" data-asset="base" checked>真实方块底盘／雷池／储能列／鸟居</label>';scenery=''
    width,height,depth=manifest['actual_scene_size_xyz'];known=manifest.get('known_issues',[])
    note='中轴七雷与三巴纹环塔布局。底盘、低压塔与鸟居仍为草模；正面遮挡和交叠尚待评审。' if is_p2 else '龙居后上方，七雷斜悬前方。工业底盘、设施及鸟居仍为摆位草模。'
    if is_p3:note='整座整数格真实方块候选，七雷已重新体素化。龙体抬高、三环间距与链端修订；交叠和遮挡见核验记录。'
    (folder/'三维布局.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(payload['data']['title'])} · 统一三维评审</title><style>{style}</style>
<header><a href="index.html">← 候选总览</a><h1>{escape(payload['data']['title'])}</h1><div>{width}×{depth}×{height}（宽×深×高） · {len(payload['parts'])}个构件 · 全静态 · {'整机整数格真实方块' if is_p3 else '建筑数据与摆位未改'}</div></header>
<main class="review"><section id="stage" aria-label="W04完整静态三维评审"><div id="loading">加载完整构件与真实材质…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">{note}</div><div class="locator"><b>主控位置示意 (0,18,419)</b><p>同平面3×3周围8接口；尚未注册为游戏控制器。</p><button data-view="controller">定位主控与接口</button><label><input id="ports" type="checkbox">接口定位框</label></div>
<div>{buttons}</div><p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 Y=<b id="layerValue">{height}</b><output id="layerLabel">{height}</output><input id="layer" type="range" min="0" max="{height}" value="{height}"></label>
<label><input id="glass" type="checkbox" checked>显示玻璃</label><label><input id="showGrid" type="checkbox">参考网格</label><p><button id="reset">复位全景</button><button id="saveImage">保存视角</button><button id="fullscreen">全屏查看</button></p><p id="counts"></p><p id="stats"></p><p id="status"></p>
<details open><summary>场景分组</summary>{assets}{scenery}</details>
<details><summary>真实材质筛选与源体素统计</summary><p id="materialCounts"></p><input id="materialSearch" type="search" placeholder="材料名或方块ID" aria-label="搜索材料"><div id="materials"></div></details>
<details><summary>独立构件</summary>{parts}</details><details><summary>核验与显示边界</summary><p>{escape(metadata['scope'])}</p>{''.join('<p>'+escape(item)+'</p>' for item in known)}<p>无动画；未游戏搭建、成型或运行验收。</p><a href="verification.json">原候选离线核验</a> · <a href="manifest.json">原摆位与尺寸</a></details></aside></main><script id="reviewMetadata" type="application/json">{json.dumps(metadata,ensure_ascii=False).replace('<',chr(92)+'u003c')}</script><script src="data.js"></script><script src="viewer.bundle.js"></script></html>''','utf8')
    source=(folder/'生成脚本/viewer.mjs').read_text('utf8')
    source=source.split('/* W04统一评审界面适配开始 */',1)[0]
    source=source.replace("renderer.setClearColor('#18101c')","renderer.setClearColor('#121b2b')").replace("renderer.setClearColor('#15131b')","renderer.setClearColor('#121b2b')")
    source+='\n'+(TOOLS/'w04_review_ui_20261110.mjs').read_text('utf8')
    (folder/'生成脚本/viewer.mjs').write_text(source,'utf8')
    return metadata


def main():
    LOG.mkdir(exist_ok=True);history=LOG/('before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    baseline={}
    for folder in [P1,P2]:
        target=history/folder.name;target.mkdir()
        for name in ['三维布局.html','viewer.bundle.js','生成脚本/viewer.mjs']:
            path=target/name;path.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(folder/name,path)
        baseline[folder.name]={name:digest(folder/name) for name in ['data.js','manifest.json','verification.json']}
    save(LOG/'geometry-before.json',baseline)
    for folder in [P1,P2]:install(folder)
    after={folder.name:{name:digest(folder/name) for name in ['data.js','manifest.json','verification.json']} for folder in [P1,P2]}
    assert baseline==after
    save(LOG/'restoration.json',dict(passed=True,history=str(history),geometry_unchanged=True,source_hashes=after,
        game_verified=False,ui_template='W03 C9／休伯利安新版评审'))
    print(json.dumps(dict(passed=True,history=str(history),geometry_unchanged=True)))


if __name__=='__main__':main()
