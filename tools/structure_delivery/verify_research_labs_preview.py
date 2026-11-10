# -*- coding: utf-8 -*-
"""候选02打包与静态交付核对，旧候选保留并显著标记失效。
变更#1 2026-09-28 02:55:00：新增页面引用、数据与尺寸校验，不进行浏览器或游戏测试。
"""
from pathlib import Path
import json,re,subprocess,datetime,hashlib
from urllib.parse import unquote
from structure_size_baseline import ROOT,SOURCE,check,require,baselines

def main():
    parent=ROOT/'doc/HK3GTL-内测5/03_机器结构'
    old=parent/'研究所S02-S05_材质候选01'
    base=parent/'研究所S02-S05_材质候选02'
    log=ROOT/'logs/research-labs-preview-20260928/candidate02'
    packager=ROOT/'tools/structure_delivery/package_research_labs_preview.mjs'
    source=packager.read_text(encoding='utf-8')
    if '材质候选01' in source:
        source=source.replace('材质候选01','材质候选02').replace('研究所候选01','研究所候选02')
        source=source.replace('research-labs-preview-20260928/viewer-source.mjs','research-labs-preview-20260928/candidate02/viewer-source.mjs')
        source=source.replace("data.size.join(' × ')","[data.size[0],data.size[2],data.size[1]].join(' × ')")
        source=source.replace("e.size.join(' × ')","[e.size[0],e.size[2],e.size[1]].join(' × ')")
        source=source.replace('（宽×高×深）','（宽×长×高）')
        source=source.replace('精密实验工厂 →','按69座总表逐轴校验，尺寸均为宽×长×高。精密实验工厂 →')
        source=source.replace('所有页面离线打包','总表下限与实际方块范围检查通过。所有页面离线打包')
        source='// 变更#2 '+datetime.datetime.now().astimezone().isoformat()+'：候选02独立交付，尺寸按宽长高显示，旧候选不覆盖。\n'+source
        packager.write_text(source,encoding='utf-8')
    subprocess.run(['node',str(packager)],check=True)
    old_checks=[];new_checks=[]
    for key in ('s02','s03','s04','s05'):
        old_checks.append(check(json.loads((old/key/'blueprint.json').read_text(encoding='utf-8'))))
        data=json.loads((base/key/'blueprint.json').read_text(encoding='utf-8'))
        new_checks.append(require(data))
        html=(base/key/'三维评审.html').read_text(encoding='utf-8')
        payload=json.loads(re.search(r'window.REVIEW=(.*?);</script>',html,re.S).group(1))
        assert payload['data']==data
        states={b['state'] for b in data['blocks']}
        materials=json.loads((base/key/'materials.json').read_text(encoding='utf-8'))
        assert payload['materials']==materials
        assert len(states)==len(materials)
        assert len({tuple(b['pos']) for b in data['blocks']})==len(data['blocks'])
    assert all(not r['passed'] for r in old_checks)
    for page in [old/'index.html']+[old/k/'三维评审.html' for k in ('s02','s03','s04','s05')]:
        html=page.read_text(encoding='utf-8')
        if 'id="size-baseline-invalid"' not in html:
            href=('../' if page.parent==old else '../../')+'研究所S02-S05_材质候选02/index.html'
            banner='<div id="size-baseline-invalid" style="position:relative;z-index:99;padding:20px;background:#692b27;color:white;font:18px sans-serif">尺寸不合格：此候选低于69座总表，停止审批与接入。历史内容保留。 <a style="color:white" href="'+href+'">打开尺寸已修正的候选02</a></div>'
            html=html.replace('</style>','</style>'+banner,1)
            html+='\n<!-- 变更#2 '+datetime.datetime.now().astimezone().isoformat()+'：新增尺寸失效提示和新版入口，保留旧几何与检查记录。 -->'
            page.write_text(html,encoding='utf-8')
    checked=[]
    for page in [base/'index.html']+[base/k/'三维评审.html' for k in ('s02','s03','s04','s05')]:
        html=page.read_text(encoding='utf-8')
        for url in re.findall(r'(?:href|src)="([^"]+)"',html):
            if url.startswith(('data:','https:','http:','#')):continue
            target=page.parent/unquote(url.split('#')[0])
            assert target.is_file(),(page,url)
        checked.append(str(page.relative_to(ROOT)))
    for script in (packager,base/'viewer.bundle.js',log/'viewer-source.mjs'):
        subprocess.run(['node','--check',str(script)],check=True,capture_output=True)
    dual=json.loads((log/'materials-dual-pack.json').read_text(encoding='utf-8'))
    report={'time':datetime.datetime.now().astimezone().isoformat(),
        'baseline_count':len(baselines()),'baseline_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'invalid_candidate01':old_checks,'candidate02':new_checks,'html_links_checked':checked,
        'javascript_syntax':True,'inline_payload_matches_blueprint':True,
        'dual_pack_material_count':len(dual),'dual_pack_faces_equal':all(x['same_preview_faces'] for x in dual),
        'browser_interaction_tested':False,'game_tested':False,
        'scope':'实际核对S02至S05；69项下限已加载，不代表其他65项结构已完成审核'}
    (log/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
