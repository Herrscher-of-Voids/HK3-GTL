"""Publish the tested r219 receipt without changing system scores or approved designs."""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'logs/native-distance-package-r219-20261108'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'
OUT=ROOT/'deliveries/内测5_r219_原生远景与无损压缩_20261108'


def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def main():
    release=read(WORK/'release.json');runtime=read(WORK/'runtime-verification.json')
    package=read(WORK/'package-verification.json');resources=read(WORK/'compact-resource-verification.json')
    assert release['passed'] and runtime['passed'] and package['passed'] and len(resources['structures'])==52
    before=WORK/'before-report';before.mkdir(exist_ok=False)
    original={p:p.read_bytes() for p in [REPORT/'index.html',REPORT/'current-summary.json']}
    for p,b in original.items():(before/p.name).write_bytes(b)
    old=read(REPORT/'current-summary.json');data=deepcopy(old)
    updated=datetime.now(timezone(timedelta(hours=8))).isoformat()
    old_mib=package['previous_bytes']/1048576;new_mib=package['bytes']/1048576
    state=(f'r219：JAR从{old_mib:.1f}MiB压缩至{new_mib:.1f}MiB，减少{package["reduction_percent"]:.2f}%；'
           '52份建筑以共享游程编码保留全部坐标、状态顺序、通用接口差别及完整NBT。'
           '本模组原生巨构远景默认2048格、8格采样、32MiB顶点缓存上限，不扩大真实区块视距或增加模组依赖。'
           '真实搭建与舰体检查建立缓存；破坏、保存重进和维度切换均更新。'
           '独立专服整舰与隐藏OpenGL测试通过；实际游戏帧率及低配／手机版仍待验收。')
    receipt=dict(revision=219,updated_at=updated,state=state,installed=release['installed'],
        release='logs/native-distance-package-r219-20261108/release.json',
        runtime='logs/native-distance-package-r219-20261108/runtime-verification.json',
        package='logs/native-distance-package-r219-20261108/package-verification.json',
        shader='logs/native-distance-package-r219-20261108/shader-probe.json',
        source_records=resources['total_blocks'],source_architectures=52,bytes=package['bytes'],
        previous_bytes=package['previous_bytes'],external_mods_added=0,client_fps_verified=False,
        native_distance=2048,sample_blocks=8,gpu_vertex_cache_mib=32,
        existing_ship_activation='控制器→检查舰体；新终端搭建边建边记录。',
        limitations=['远景为静态外观采样，细节由近景真实方块显示；不绘制机器或实体运行。',
                     '客户端最多1024个64格区域，服务端每维度最多4096区域；全舰在默认容量内。',
                     '存档中未经本轮建造／检查的历史建筑尚无远景缓存；其他机器手工搭建不自动追溯。',
                     '实际客户端FPS、光影兼容和手机版未测；不保证某个帧率。'])
    data['current_work'].setdefault('performance_history',[]).append(deepcopy(old['current_work']['hyperion_performance']))
    data['current_work']['native_distance_and_package']=receipt
    data['current_work']['hyperion_performance']=deepcopy(receipt)
    data['current_work']['hyperion_performance']['external_lod']='负责人已否决新增LOD模组；旧预备包仅保留历史，未安装。'
    data['current_work']['hyperion_construction'].update(revision=219,state=state,runtime=receipt['runtime'],deployment=receipt['release'],client_fps_verified=False)
    data['report_updated_at']=updated
    row=next(s for s in data['systems'] if s['id']=='N16');prior=next(s for s in old['systems'] if s['id']=='N16')
    row.update(coverage=state,updated_at=updated,changed=True)
    row['remaining_gaps']=['r219实际客户端帧率、光影与低配／手机版未验收；远景是8格采样静态外观，不代表全部方块细节。',
        '未经本轮终端搭建或舰体检查的旧建筑没有远景缓存；其他机型手工搭建不自动追溯。',
        '其他朝向的整舰建造／成型与长期运行未完成实测。',
        '生存工程、供能、舰载工艺、移动及C7／终审工程证明仍未开放。']
    evidence=[receipt['runtime'],receipt['package'],receipt['shader'],receipt['release']]
    for cap in row['capabilities'][2:4]:
        cap['evidence']=list(dict.fromkeys(cap.get('evidence',[])+evidence));cap['reason']+=' r219补充：'+state
    row['runtime_review']['runtime'].append({'path':receipt['runtime'],'claim':'r219原生远景存读、实际变化更新、无目标区块加载及整舰成型回归；客户端FPS未验收。'})
    row['runtime_review']['gap']=' '.join(row['remaining_gaps'])
    # No new client acceptance and no system completion claim: preserve every score.
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in old['systems']]
    assert all(a==b for a,b in zip(data['systems'],old['systems']) if a['id']!='N16')
    html=original[REPORT/'index.html'].decode('utf-8')
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in html
    html=html.replace(anchor,anchor+'<p class="notice" id="native-distance-r219">'+escape(state)+
        ' <a href="../../deliveries/内测5_r219_原生远景与无损压缩_20261108/index.html">r219交付与核验</a></p>',1)
    card=re.search(r'<details class="system" data-id="N16".*?</details>',html,re.S)[0]
    revised=card.replace(escape(prior['coverage']),escape(state),1)
    for before_cap,after_cap in zip(prior['capabilities'][2:4],row['capabilities'][2:4]):
        assert escape(before_cap['reason']) in revised
        revised=revised.replace(escape(before_cap['reason']),escape(after_cap['reason']),1)
    revised,n=re.subn(r'(<h3>剩余差距</h3><ul>).*?(</ul>)',lambda m:m[1]+''.join('<li>'+escape(g)+'</li>' for g in row['remaining_gaps'])+m[2],revised,count=1,flags=re.S);assert n==1
    html=html.replace(card,revised,1)
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+updated+' · r219原生远景与无损压缩</p>',html,count=1);assert n==1
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in data['systems']]
    assert [s['percent'] for s in data['systems']]==sorted(s['percent'] for s in data['systems'])
    sys.path.insert(0,str(ROOT/'tools/structure_delivery'))
    from max_structure_review import publisher
    publisher().publish_transaction({REPORT/'index.html':html,REPORT/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n'},original)
    OUT.mkdir(exist_ok=True)
    for name in ['release.json','package-verification.json','runtime-verification.json','shader-probe.json','compact-resource-verification.json','saved-farview-verification.json']:
        shutil.copy2(WORK/name,OUT/name)
    checks=len(runtime['checks'])
    page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>内测5 r219 原生远景与无损压缩</title>
<style>body{{max-width:950px;margin:40px auto;padding:20px;background:#111b29;color:#e6edf5;font:17px/1.7 system-ui}}a{{color:#8fdaff}}li{{margin:10px 0}}</style>
<h1>内测5 r219 · 原生远景与无损压缩</h1><p>{escape(state)}</p>
<p><a href="HK3GTL-内测5-r219.jar">正式JAR（{new_mib:.1f}MiB）</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计入口</a></p>
<ul><li>已{'部署增强版3.0；下次启动生效' if release['installed'] else '生成交付；目标游戏正在运行，尚未替换实例'}。服务端与客户端须同时更新，协议30。</li>
<li>旧休伯利安：控制器→检查舰体。新终端搭建自动记录远景；无需提高原版真实视距。</li>
<li>设置文件：config/hk3gtl-farview-client.toml；enabled、distance、gpuMiB。默认2048格、32MiB，可关闭或降至8MiB。</li>
<li>无损对照：52份正式结构，{resources['total_blocks']:,}条坐标／状态／NBT记录；Java解码及独立原始JSON逐格对照通过。</li>
<li>隔离专服：87个第三方模组、30项服务器检查及1项停服存档独立回读，包括整舰搭建、GT成型、破坏失效、远景存读与无区块加载。着色器在隐藏OpenGL环境实际绘制并检查像素。核验插件最后统计调用的映射错误保留在收据中，以实际存档回读补证。</li>
<li>边界：8格采样远景有简化；最多1024个64格区域，服务端每维度4096区域。不追溯从未建造／检查的旧建筑。未实测游戏FPS、光影或手机版。</li>
<li>原始批准建筑、旧JAR与历史交付保留；本次压缩的是玩家安装JAR，不删除开发历史。</li></ul>
<p>SHA-256：<code>{package['sha256']}</code></p>
<p><a href="package-verification.json">包体核验</a> · <a href="compact-resource-verification.json">无损记录核验</a> · <a href="runtime-verification.json">隔离专服核验</a> · <a href="shader-probe.json">OpenGL核验</a> · <a href="release.json">部署收据</a></p></html>'''
    (OUT/'index.html').write_text(page,encoding='utf-8')
    save(WORK/'publication-verification.json',dict(passed=True,all_36_scores_unchanged=True,overall_percent=data['overall_percent'],
        approved_and_formal_scope_unchanged=True,ascending_order=True,previous_baseline_saved=True,report_sha256=sha(REPORT/'index.html')))
    print(json.dumps({'report_updated':True,'bytes':package['bytes'],'installed':release['installed'],'system_scores_unchanged':36}))


if __name__=='__main__':main()
