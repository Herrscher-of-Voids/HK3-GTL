# -*- coding: utf-8 -*-
"""I35 V3实体导出与界面效果打包；复用V2只读核验和材质流程。"""
import base64
import datetime as dt
import gzip
import json
import shutil
import subprocess

import numpy as np

import build_i35_suspension_v2_20261027 as common
import i35_threshold_geometry_v3_20261027 as geometry

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I35_虚数空间锚定阵列_越界悬索桥_V3_20261027'
LOG = ROOT / 'logs/i35-threshold-v3-20261027'
save = common.save


def main():
    OUT.mkdir(exist_ok=True, parents=True); LOG.mkdir(exist_ok=True, parents=True)
    view = OUT / 'i35'; view.mkdir(exist_ok=True)
    cube, data = geometry.build()
    # V2审计不写原交付，切换被核验的独立几何模块。
    common.geometry = geometry
    check = common.audit(cube, data)
    assert np.all(cube[98:101, 609:701, 192:209]), '桥面没有穿过界面'
    assert np.all(cube[140, 610, 180:221] == 0), '界面被实体背板堵住'
    assert not np.any(cube[150:, 500:550, 200]), '遗留第二索塔横梁'
    assert all(p['pos'][2] <= 97 for p in data['ports'])
    check['threshold_checks'] = dict(passed=True, physical_bridge_crosses_plane=True,
        clear_aperture=True, remote_bridgehead_removed=True, all_ports_in_home_dimension=True,
        visual_only=data['portal'], visual_effects_excluded_from_exports=True)
    version = json.loads((common.resources.INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    materials, sources, packs = common.resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('V3实体核验通过，导出并逐格回读…', flush=True)
    result = common.export_dense(cube, geometry.STATES, data['name'], view)
    assert result['block_count'] == check['blocks']
    groups = result['surface_groups']
    check.update(nbt_schem_sha256=result['hashes'], readback=result['readback'],
        viewer_surface_faces=sum(len(face) for group in groups for face in group),
        viewer_payload_exact_cell_readback=True, source_instance=str(common.resources.INSTANCE), instance_version=version,
        material_resource_sources=sources, enabled_file_resource_packs=packs)
    check['ordinary_material_namespaces'] = {}
    for state, count in check['palette'].items():
        if state not in (geometry.material.CONTROL, geometry.material.PORT):
            ns = state.split(':')[0]
            check['ordinary_material_namespaces'][ns] = check['ordinary_material_namespaces'].get(ns, 0) + count
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, blockCount=check['blocks'], materials=materials,
        audit=check, names={s: s.split(':')[1] for s in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    encoded = base64.b64encode(compressed).decode('ascii')
    (view / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    check.update(viewer_payload_gzip_bytes=len(compressed), viewer_payload_base64_bytes=len(encoded))
    manifest = dict(data, candidate_version='V3', status='candidate_waiting_user_review', approved=False, installed=False,
        target_voltage='IRV', voltage_mapping='V11 / tier25', blocks=check['blocks'], unique_materials=check['unique_materials'],
        geometry_passed=True, source_instance=str(common.resources.INSTANCE), instance_version=version,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds'))
    save(OUT / 'manifest.json', manifest); save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'], source=sources.get(m['state'], {})) for m in materials])
    page = common.report(data, check).replace('V2', 'V3').replace('悬索界桥', '越界悬索桥')
    start = page.index('<h2>实体锚定工程</h2>'); end = page.index('<p>输入真实魂钢锚件', start)
    page = page[:start] + '<h2>从本维度锚入虚数空间</h2><p>近端实体锚室、单站索塔与连续主缆托住长桥，八角承力框接住远端索鞍；桥面穿过界面，再伸入九十格纵深。远端桥头及第二站索塔撤去，成排锚桩保留在本维度工作区。全部十个接口位于近端锚室，主控仍在整宽中线。</p><p>门内黑金空间、纵深流纹和隐没桥影属于可关闭、可暂停的HTML动态效果，不计入实体数量、材料、NBT、Schematic或正式Pattern，也不代表真实传送功能。</p>' + page[end:]
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for filename in ['build_i35_threshold_v3_20261027.py', 'i35_threshold_geometry_v3_20261027.py',
        'build_i35_threshold_viewer_v3_20261027.mjs', 'i35_suspension_geometry_v2_20261027.py',
        'build_i35_suspension_v2_20261027.py', 'i34_open_observatory_export_20261027.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / filename, scripts / filename)
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/build_i35_threshold_viewer_v3_20261027.mjs'), str(OUT)], cwd=ROOT, check=True)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, blocks=check['blocks'],
        materials=check['unique_materials'], size_xyz=data['size'], surface_faces=check['viewer_surface_faces'], nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], materials=check['unique_materials'], faces=check['viewer_surface_faces']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
