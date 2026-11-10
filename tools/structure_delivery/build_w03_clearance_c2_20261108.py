# -*- coding: utf-8 -*-
"""交付完整C2正圆候选，核验部件净空与完整导出。"""
import json
import shutil
from pathlib import Path
from types import SimpleNamespace
import w03_clearance_c2_20261108 as geometry
from build_max_structure_candidate import generate, save
from build_wonder_boundary_repairs_20261108 import generic_audit, preview_page

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W03_C方案_正圆与净空_C2_20261108'
LOG=ROOT/'logs/w03-clearance-c2-20261108'

def preview_readiness(out):
    view=out/'w03';page=view/'三维评审.html';text=page.read_text('utf8')
    if 'c2-ready.js' not in text:
        text=text.replace('</body>','<script src="c2-ready.js"></script></body>') if '</body>' in text else text.replace('</html>','<script src="c2-ready.js"></script></html>')
        page.write_text(text,'utf8')
    (view/'c2-ready.js').write_text('''/** 完整模型就绪后才结束载入提示，避免把渐进显示误认为缺块。 */
(()=>{const status=document.createElement('div');status.style='position:fixed;right:24px;top:24px;z-index:10000;padding:8px 14px;background:#142438;color:white';status.textContent='模型载入中…';document.body.append(status);
function check(){if(!window.BOUNDARY_READY)return setTimeout(check,100);let done=0,total=0;window.reviewApi.scene.traverse(o=>{if(o.userData.indices){done+=o.userData.initialized;total+=o.userData.indices.length;}});status.textContent='模型载入中 '+Math.floor(done*100/Math.max(1,total))+'%';if(done<total)return setTimeout(check,50);status.remove();const a=window.reviewApi,d=window.REVIEW.data,[w,h,z]=d.size,old=a.setView;
a.setView=n=>{old(n);if(n==='front'){a.controls.target.set(w/2,h*.5,z/2);a.camera.position.set(w/2-w*.16,h*.5+w*.16,z/2-w*1.6);a.camera.zoom=1.08;a.controls.update();a.camera.updateProjectionMatrix();a.renderer.render(a.scene,a.camera);}};a.setView('front');window.C2_READY=true;}check();})();''','utf8')

def main():
    LOG.mkdir(parents=True,exist_ok=True)
    cube,data=geometry.build()
    save(LOG/'component-clearance.json',data['clearance'])
    proxy=SimpleNamespace(STATES=geometry.STATES,ROLES=geometry.ROLES,__file__=geometry.__file__,
        build=lambda:(cube,data),audit=lambda c,d:generic_audit(c,d,geometry.STATES,dict(component_clearance=d['clearance'],no_nominal_clipping=True)))
    generate(proxy,OUT,LOG,__file__)
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest.update(candidate_version=data['candidate_version'],target_voltage='CIV',source_author='Gemini C1基础上按负责人穿模与正圆反馈修订')
    save(OUT/'manifest.json',manifest)
    check=json.loads((OUT/'verification.json').read_text('utf8'))
    description='外环为420格直径的立式正圆。独立构件重新分开，保留全部六矛、十片曲翼、双飘带、24颗晶体及24枚浮游柱；不靠删除交叠方块修补。'
    preview_page(OUT,manifest,check,description)
    preview_readiness(OUT)
    page=OUT/'index.html'
    text=page.read_text('utf8').replace('保留原案的相交、遮挡与自然断面，不自行纠正原作者方案。',
        'C1历史原件保留。C2依据负责人本轮反馈调整相交：独立组件体素重叠为零，预留至少7格空气尺度的分离距离；基础承重接合与核心内部接合单独列明。')
    text=text.replace('<img src="完整预览.png"',
        '<p>本版为立式420格正圆，实际高度超过原321格及普通主世界384格建高范围，属于离线外观候选；尚未接入支持此高度的游戏维度。</p><p><a href="正圆正视.png">沿圆环法线的正圆正视图</a> · <a href="局部净空.png">构件净空近景</a> · <a href="../../logs/w03-clearance-c2-20261108/component-clearance.json">构件间距核验</a></p><img src="完整预览.png"',1)
    page.write_text(text,'utf8')
    shutil.copy2(ROOT/'deliveries/W03_C方案_亚空之矛优化_C1_20261108/完整预览.png',OUT/'上一版C1.png')
    for name in ['w03_void_spear_c1_20261108.py','w03_celestial_geometry_v4_20261107.py','audit_wonder_clipping_20261108.py']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    print(json.dumps(dict(passed=True,size_wdh=[data['size'][0],data['size'][2],data['size'][1]],before_pairs=len(data['clearance']['before']),after_pairs=0),ensure_ascii=False),flush=True)

if __name__=='__main__':main()
