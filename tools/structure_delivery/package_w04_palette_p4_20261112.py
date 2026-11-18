# -*- coding: utf-8 -*-
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import base64, gzip, json, re, shutil
import numpy as np
from i34_open_observatory_export_20261027 import CHUNK, RECORD_DTYPE, _headers, digest, exact

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/W04_完整真实方块_露首环链修订_P3_20261110'
OUT = ROOT / 'logs/remove-fixed-ports-r266-20261113/w04'
NAME = 'hk3gtl-w04-existing-materials-p4-20261112-freeports-r266'
TITLE = 'W04 · 旧接口恢复 R266'
REPLACE = {
    'hk3gtl:wonder_thunder_casing': 'hk3gtl:voltage_machine_casing_hrv',
    'hk3gtl:wonder_thunder_interface': 'hk3gtl:voltage_machine_casing_hrv',
}
load = lambda p: json.loads(p.read_text('utf8'))
save = lambda p, value: p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def migrate_exports(old_states, states, lut, manifest):
    width, height, depth = manifest['actual_scene_size_xyz']
    count = manifest['block_count']
    old_headers = _headers(old_states, (height, depth, width), count)
    headers = _headers(states, (height, depth, width), count)
    source_name = manifest['name']
    counts = np.zeros(len(states), dtype=np.int64)
    for extension, old_header, header in zip(('nbt', 'schem'), old_headers, headers):
        remaining = count if extension == 'nbt' else width * height * depth
        step = CHUNK if extension == 'nbt' else 1024 * 1024
        with gzip.open(SOURCE / f'{source_name}.{extension}', 'rb') as original, gzip.open(OUT / f'{NAME}.{extension}', 'wb', compresslevel=6) as target:
            assert exact(original, len(old_header)) == old_header
            target.write(header)
            for start in range(0, remaining, step):
                n = min(step, remaining - start)
                if extension == 'nbt':
                    raw = bytearray(exact(original, n * RECORD_DTYPE.itemsize))
                    records = np.frombuffer(raw, dtype=RECORD_DTYPE)
                    records['state'] = lut[records['state']]
                    counts += np.bincount(records['state'], minlength=len(states))
                    target.write(raw)
                else:
                    old = np.frombuffer(exact(original, n), dtype=np.uint8)
                    schem_lut = np.concatenate(([0], lut + 1)).astype(np.uint8)
                    target.write(schem_lut[old].tobytes())
            target.write(original.read())
        print('导出', extension, flush=True)
    for extension, old_header, header in zip(('nbt', 'schem'), old_headers, headers):
        remaining = count if extension == 'nbt' else width * height * depth
        step = CHUNK if extension == 'nbt' else 1024 * 1024
        with gzip.open(SOURCE / f'{source_name}.{extension}', 'rb') as original, gzip.open(OUT / f'{NAME}.{extension}', 'rb') as target:
            assert exact(original, len(old_header)) == old_header
            assert exact(target, len(header)) == header
            for start in range(0, remaining, step):
                n = min(step, remaining - start)
                if extension == 'nbt':
                    raw = bytearray(exact(original, n * RECORD_DTYPE.itemsize))
                    expected = np.frombuffer(raw, dtype=RECORD_DTYPE)
                    expected['state'] = lut[expected['state']]
                    assert exact(target, len(raw)) == raw
                else:
                    expected = schem_lut[np.frombuffer(exact(original, n), dtype=np.uint8)]
                    assert exact(target, n) == expected.tobytes()
            assert target.read() == original.read()
        print('逐格回读', extension, flush=True)
    return counts


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    before = {str(p.relative_to(SOURCE)): digest(p) for p in SOURCE.rglob('*') if p.is_file()}
    manifest = load(SOURCE / 'manifest.json')
    payload = json.loads(gzip.decompress(base64.b64decode(json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].rstrip(';')))))
    old_states = [m['state'] for m in payload['materials']]
    states = list(dict.fromkeys(REPLACE.get(s, s) for s in old_states))
    lut = np.array([states.index(REPLACE.get(s, s)) for s in old_states], dtype=np.int32)
    removed = set(load(ROOT / 'logs/fluid-texture-refresh-20261112/deleted-block-assets.json')['registered_block_ids_removed'])
    removed_before = [s for s in old_states if s.split(':')[1] in removed]
    assert set(removed_before) == set(REPLACE)
    assert not any(s.split(':')[1] in removed for s in states)
    registrations = (ROOT / 'src/main/java/com/sirin/hk3gtl/common/registration/Hk3IndustrialContent.java').read_text('utf8')
    assert all(f'block("{s.split(":")[1]}")' in registrations for s in states if s.startswith('hk3gtl:'))
    counts = migrate_exports(old_states, states, lut, manifest)
    expected = Counter()
    for row in load(SOURCE / '材料清单.json'):
        expected[REPLACE.get(row['state'], row['state'])] += row['count']
    assert counts.tolist() == [expected[s] for s in states]
    save(OUT / '材料清单.json', [dict(state=s, count=int(n)) for s, n in zip(states, counts)])

    materials = {m['state']: m for m in payload['materials']}
    payload['materials'] = [materials[s] for s in states]
    for part in payload['parts']:
        for field in ('starts', 'lengths'):
            groups = [[[] for _ in range(6)] for _ in states]
            for old, faces in enumerate(part[field]):
                for face, values in enumerate(faces):
                    groups[lut[old]][face].extend(values)
            part[field] = groups
    payload['data'].update(name=NAME, title=TITLE, ports=[])
    (OUT / 'data.js').write_text('window.W04_STATIC_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6, mtime=0)).decode()) + ';', 'utf8')
    for name in ('viewer.bundle.js', '交叠记录.json'):
        shutil.copy2(SOURCE / name, OUT / name)
    shutil.copy2(SOURCE / '生成脚本/viewer.mjs', OUT / '生成脚本/viewer.mjs')
    shutil.copy2(__file__, OUT / '生成脚本' / Path(__file__).name)

    manifest.update(name=NAME, title=TITLE, palette_count=len(states), ports_world=[], source_candidate=str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
                    palette_migration=REPLACE, geometry_unchanged=True, ui_implementation_unchanged=True)
    manifest['dragon_material_map'] = {k: REPLACE.get(v, v) for k, v in manifest['dragon_material_map'].items()}
    resources = manifest['materials']['resource_sources']
    manifest['materials']['resource_sources'] = {k: v for k, v in resources.items() if not any(s.split(':')[1] in k for s in REPLACE)}
    manifest['materials'].update(states=states, resource_access='材质复用P3 data.js内嵌载荷；资源路径仅为P3历史来源，本轮未访问。')
    manifest['known_issues'][0] = 'W04正式控制器尚未注册；(0,18,419)继续使用红石块占位；实体建筑位置可由玩家自行选择通用接口，主控除外。'
    manifest['merge_rule'] += ' P4只迁移合并结果的材质索引，独立构件源NPZ仍引用P3历史。'
    save(OUT / 'manifest.json', manifest)
    metadata = load(SOURCE / 'review-ui.json')
    labels = {r['state']: r['label'] for r in metadata['materials']}
    metadata.update(candidate='W04 P4', materials=[dict(state=s, count=int(n), label=labels[s]) for s, n in zip(states, counts)])
    save(OUT / 'review-ui.json', metadata)
    html = (SOURCE / '三维布局.html').read_text('utf8').replace('W04 · 整机真实方块 P3', TITLE)
    html = html.replace('整座整数格真实方块候选，七雷已重新体素化。龙体抬高、三环间距与链端修订；交叠和遮挡见核验记录。', 'P4仅更新现存HRV材质；旧接口恢复为HRV机壳。完整几何、构件坐标与镜头保持。交叠和遮挡仍待协调。')
    html = html.replace('W04正式控制器尚未注册；(0,18,419)使用真实红石块作为明确占位，周围八格为真实wonder_thunder_interface外观方块，非已验收GT功能接口。', manifest['known_issues'][0])
    html = html.replace('原候选离线核验', '材质迁移离线核验')
    html = re.sub(r'(<script id="reviewMetadata" type="application/json">).*?(</script>)', lambda m: m[1] + json.dumps(metadata, ensure_ascii=False) + m[2], html, flags=re.S)
    (OUT / '三维布局.html').write_text(html, 'utf8')
    style = re.search(r'<style>(.*?)</style>', (SOURCE / 'index.html').read_text('utf8'), re.S)[1]
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLE}</title><style>{style}</style><p>W04 · 雷之律者 · 静态整机候选</p><h1>俱利伽罗 × 鸣雷见<br>现存材质与通用接口 P4</h1><p class="note">仅替换P3两种已删除方块：30,090格旧绯雷装饰机壳改用现存HRV机壳；旧接口恢复HRV机壳，玩家自行选择实体位置替换通用接口。几何、29个构件坐标、镜头与原统一评审操作保持。</p><p><a href="三维布局.html">打开原版界面三维评审</a> · <a href="../{SOURCE.name}/index.html">P3历史与原截图</a></p><p>实际宽941×深1056×高623格，17,440,898块、{len(states)}种材质。完整NBT／Schematic、预览表面和材料表已同步；主控(0,18,419)仍为红石块占位，未注册W04控制器。</p><p>三组待协调交叠共46,848次共享格、正面龙首遮挡14.083%、鬼手未制作，均继承P3。无动画、外观待评审，未游戏搭建、成型或运行验收。</p><p>本轮仅仓库材质与完整导出回读；P3截图和界面操作证据留在历史入口，未计作P4新截图或实测。</p><p><a href="{NAME}.nbt">完整整机NBT</a> · <a href="{NAME}.schem">完整整机Schematic</a> · <a href="材料清单.json">材料清单</a> · <a href="manifest.json">坐标与材质来源</a> · <a href="交叠记录.json">交叠记录</a> · <a href="verification.json">本轮离线核验</a></p></html>''', 'utf8')
    after = {str(p.relative_to(SOURCE)): digest(p) for p in SOURCE.rglob('*') if p.is_file()}
    assert before == after
    save(OUT / 'verification.json', dict(passed=True, scope='调色板迁移、完整导出逐格回读与现存ID核对',
        created_at=datetime.now(timezone.utc).isoformat(), geometry_readback=dict(passed=True, coordinates_equal_to_p3=True,
        mapped_states_per_block_equal=True, size_xyz=manifest['actual_scene_size_xyz'], blocks=manifest['block_count'], palette_count=len(states)),
        source_candidate=manifest['source_candidate'], source_hashes=before, source_unchanged=True,
        export_hashes={suffix: digest(OUT / f'{NAME}.{suffix}') for suffix in ('nbt', 'schem')},
        active_deleted_ids=[], removed_ids_found_in_p3=removed_before, palette_migration=REPLACE,
        parts=29, surface_quads=payload['audit']['viewer_rendered_quads'], ui_bundle_equal_to_p3=digest(OUT / 'viewer.bundle.js') == before['viewer.bundle.js'],
        collision_free=False, collision_report=load(OUT / '交叠记录.json'), head_visibility=manifest['head_visibility'],
        static=True, animation_enabled=False, screenshots=0, gui_test_performed=False,
        historical_ui_and_screenshot_evidence='../' + SOURCE.name + '/verification.json', controller_registered=False, game_verified=False))
    print(json.dumps(dict(passed=True, directory=str(OUT), blocks=int(counts.sum()), palette_count=len(states), source_unchanged=True), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
