# -*- coding: utf-8 -*-
import gc
import json
from pathlib import Path
from types import SimpleNamespace
import w03_eye_c3_20261108 as geometry
from build_max_structure_candidate import generate, save
from build_wonder_boundary_repairs_20261108 import generic_audit, preview_page

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W03_C3_眼形莫比乌斯_四方案_20261108'
LOG = ROOT / 'logs/w03-eye-c3-20261108'

READY = '''/** Finish progressive voxel loading before displaying the completed model. */
(()=>{const s=document.createElement('div');s.style='position:fixed;right:24px;top:24px;z-index:10000;padding:8px 14px;background:#142438;color:white';s.textContent='完整模型载入中…';document.body.append(s);
function check(){if(!window.BOUNDARY_READY)return setTimeout(check,100);let done=0,total=0;window.reviewApi.scene.traverse(o=>{if(o.userData.indices){done+=o.userData.initialized;total+=o.userData.indices.length;}});s.textContent='完整模型载入中 '+Math.floor(done*100/Math.max(1,total))+'%';if(done<total)return setTimeout(check,50);s.remove();const a=window.reviewApi,d=window.REVIEW.data,o=d.blueprint_to_export_offset_xyz,old=a.setView;
a.setView=n=>{old(n);if(n==='front'||n==='orthofront'||n==='right'){const c=[336+o[0],295+o[1],264+o[2]];a.controls.target.set(...c);a.camera.position.set(c[0]+(n==='front'?-180:n==='right'?850:0),c[1]+(n==='front'?180:n==='right'?250:0),c[2]-1600);a.camera.zoom=.96;a.controls.update();a.camera.updateProjectionMatrix();a.renderer.render(a.scene,a.camera);}};a.setView('front');window.C3_READY=true;}check();})();'''


def audit(c, d):
    import numpy as np
    assert len(d['rings']) == d['comparison']['ring_count']
    assert all(r['half_twists'] == 1 and r['seam_closed_with_reversed_cross_section'] for r in d['rings'])
    assert d['ribbons'] == d['feathers'] == [] and len(d['cubes']) == 24 and len(d['spears']) == 6
    assert len(set(c['side_length'] for c in d['cubes'])) == 8
    assert len(d['ports']) == 8
    for p in d['spears']:
        assert p['point_direction'][1] > .6 if d['comparison']['spear_direction'] == 'upward' else p['point_direction'][1] == 0
    for name, bounds in d['clearance']['part_bounds_blueprint'].items():
        if name.startswith('crystal:'): assert 145 <= bounds['min'][1] <= bounds['max'][1] <= 285
    assert not d['clearance']['after']
    result = generic_audit(c, d, geometry.STATES, dict(component_clearance=d['clearance'],
        no_nominal_clipping=True, design_comparison=d['comparison'],
        half_twist_seam_verified=True, all_crystals_in_lower_third=True,
        old_c2_preserved=True, desktop_used=False, game_started=False))
    assert all(x['outer_clear'] == 5 for x in result['port_checks'])
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    results = []
    for code, rings, upward in geometry.VARIANTS:
        target, log = OUT / code, LOG / code
        if (target / 'verification.json').exists():
            results.append(json.loads((target / 'manifest.json').read_text('utf8'))); continue
        cube, data = geometry.build(rings, upward)
        proxy = SimpleNamespace(STATES=geometry.STATES, ROLES=geometry.ROLES, __file__=geometry.__file__,
            build=lambda: (cube, data), audit=audit)
        generate(proxy, target, log, __file__)
        manifest = json.loads((target / 'manifest.json').read_text('utf8'))
        manifest.update(target_voltage='CIV', candidate_version=data['candidate_version'],
                        source_author='C2基础上按负责人眼形、莫比乌斯、晶体与矛向反馈修订')
        save(target / 'manifest.json', manifest)
        check = json.loads((target / 'verification.json').read_text('utf8'))
        preview_page(target, manifest, check, data['description'])
        view = target / 'w03'; page = view / '三维评审.html'
        page.write_text(page.read_text('utf8').replace('</html>', '<script src="c3-ready.js"></script></html>'), 'utf8')
        (view / 'c3-ready.js').write_text(READY, 'utf8')
        index = target / 'index.html'
        text = index.read_text('utf8').replace('保留原案的相交、遮挡与自然断面，不自行纠正原作者方案。',
            '本轮按负责人要求改为莫比乌斯眼形候选；独立构件无重叠，保留完整几何。')
        text = text.replace('<img src="完整预览.png"',
            '<p><a href="正面眼形.png">正面眼形</a> · <a href="环带近景.png">半扭转环带近景</a> · <a href="../index.html">四方案比较</a></p><p>实际高度636格，超出普通主世界384格建高；本轮为外观预览，未实装。</p><img src="完整预览.png"', 1)
        index.write_text(text, 'utf8')
        save(log / 'component-clearance.json', data['clearance'])
        results.append(manifest)
        del cube, data, proxy; gc.collect()
    save(OUT / 'comparison.json', dict(version='C3', approved=False, installed=False,
        game_verified=False, variants=results, desktop_used=False))


if __name__ == '__main__': main()
