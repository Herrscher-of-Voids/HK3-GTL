# -*- coding: utf-8 -*-
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import w03_core_aim_c4_20261108 as geometry
from build_max_structure_candidate import generate, save
from build_wonder_boundary_repairs_20261108 import generic_audit, preview_page
from build_w03_eye_c3_20261108 import READY

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W03_C4_五环锁芯与立体晶云_20261108'
LOG = ROOT / 'logs/w03-core-aim-c4-20261108'

OVERLAY = '''/** Visualize the actual tip-tail axes; this is preview UI, not build geometry. */
(()=>{function boot(){if(!window.C3_READY)return setTimeout(boot,50);const a=window.reviewApi,d=window.REVIEW.data,o=d.blueprint_to_export_offset_xyz,old=a.setView;
a.setView=n=>{old(n);if(n==='front'||n==='orthoside'){const c=[336+o[0],295+o[1],264+o[2]];a.controls.target.set(...c);a.camera.position.set(c[0]+(n==='front'?-600:1800),c[1]+(n==='front'?350:0),c[2]+(n==='front'?-1400:0));a.camera.zoom=.96;a.controls.update();a.camera.updateProjectionMatrix();a.renderer.render(a.scene,a.camera);}};
const stage=document.getElementById('stage'),canvas=document.createElement('canvas');canvas.style='position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:30';stage.append(canvas);const ctx=canvas.getContext('2d');let enabled=false;
const button=document.createElement('button');button.type='button';button.textContent='显示六矛指向线';button.style='position:absolute;right:18px;bottom:20px;z-index:35;padding:9px 16px;color:#fff;background:#322342;border:1px solid #bc9cd8;border-radius:7px;cursor:pointer';stage.append(button);
function show(value){enabled=value;button.textContent=enabled?'隐藏六矛指向线':'显示六矛指向线';}button.onclick=()=>show(!enabled);window.C4AimOverlay={show};
const V=a.camera.position.constructor,colors=['#ff9e78','#86e6ff','#d3a2ff','#fff195','#8dffc8','#ff9fdf'];
function frame(){const r=stage.getBoundingClientRect();if(canvas.width!==Math.round(r.width)||canvas.height!==Math.round(r.height)){canvas.width=Math.round(r.width);canvas.height=Math.round(r.height);}ctx.clearRect(0,0,canvas.width,canvas.height);
if(enabled){const project=p=>{const v=new V(...p.map((n,i)=>n+o[i])).project(a.camera);return[(v.x+1)*canvas.width/2,(1-v.y)*canvas.height/2];};
d.spears.forEach((s,i)=>{const tail=project(s.tail),tip=project(s.tip),core=project(s.target_core);ctx.strokeStyle=colors[i];ctx.lineWidth=2;ctx.setLineDash([7,5]);ctx.beginPath();ctx.moveTo(...tail);ctx.lineTo(...core);ctx.stroke();ctx.setLineDash([]);ctx.fillStyle=colors[i];ctx.beginPath();ctx.arc(...tip,4,0,Math.PI*2);ctx.fill();});
const p=project(d.core_center_blueprint);ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.beginPath();ctx.arc(...p,9,0,Math.PI*2);ctx.stroke();ctx.font='15px system-ui';ctx.fillStyle='#fff';ctx.fillText('六矛共同目标：核心',p[0]+14,p[1]-12);}
requestAnimationFrame(frame);}frame();a.setView('front');window.C4_READY=true;}boot();})();'''


def audit(cube, data):
    for s in data['spears']:
        tip, tail, target = (np.array(s[k]) for k in ('tip', 'tail', 'target_core'))
        assert np.array_equal(np.cross(target - tip, tip - tail), [0, 0, 0])
        assert (target - tip) @ (tip - tail) > 0 and tip[1] > tail[1]
    cloud = data['crystal_cloud']
    assert cloud['lower_central_count'] >= 8 and cloud['unique_z_coordinates'] >= 20
    assert cloud['smallest_to_largest_eigenvalue_ratio'] > .15
    result = generic_audit(cube, data, geometry.STATES, dict(component_clearance=data['clearance'],
        aiming=data['aiming'], crystal_cloud=cloud, no_nominal_clipping=True,
        desktop_used=False, game_started=False))
    assert all(p['outer_clear'] == 5 for p in result['port_checks'])
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    cube, data = geometry.build()
    proxy = SimpleNamespace(STATES=geometry.STATES, ROLES=geometry.ROLES, __file__=geometry.__file__,
        build=lambda: (cube, data), audit=audit)
    generate(proxy, OUT, LOG, __file__)
    manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
    manifest.update(target_voltage='CIV', candidate_version=data['candidate_version'], source_author='负责人选择C3-5U方向后的三维指向与晶体布局修正')
    save(OUT / 'manifest.json', manifest)
    check = json.loads((OUT / 'verification.json').read_text('utf8'))
    preview_page(OUT, manifest, check, data['description'])
    view = OUT / 'w03'; page = view / '三维评审.html'
    page.write_text(page.read_text('utf8').replace('</html>', '<script src="c4-ready.js"></script><script src="c4-aim.js"></script></html>'), 'utf8')
    (view / 'c4-ready.js').write_text(READY, 'utf8')
    (view / 'c4-aim.js').write_text(OVERLAY, 'utf8')
    save(LOG / 'aim-and-cloud.json', dict(aiming=data['aiming'], spears=data['spears'], crystal_cloud=data['crystal_cloud'], crystals=data['cubes']))


if __name__ == '__main__': main()
