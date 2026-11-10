# -*- coding: utf-8 -*-
"""归档r228真实复测，停机恢复原设置，核验原存档与部署身份。"""
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import zipfile

from finish_farview_batch_20261109 import profile
from finish_farview_fog_20261109 import LOG
from finish_terminal_farview_20261109 import ROOT, sha, write_json, target_process_guard


def main():
    guard = target_process_guard()
    prior = ROOT / 'logs/farview-exact-r226-20261109'
    instance = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
    manifest = json.loads((prior / 'source-world-manifest.json').read_text(encoding='utf8'))
    source = Path(manifest['source'])
    after = {str(p.relative_to(source)): sha(p) for p in source.rglob('*') if p.is_file()}
    assert after == manifest['files'], '原存档变化，禁止宣称未改动'
    target = instance / 'mods/HK3GTL-内测5.jar'
    deployment = json.loads((LOG / 'deployment.json').read_text(encoding='utf8'))
    assert sha(target) == sha(LOG / 'HK3GTL-r228-ready.jar') == deployment['installed_sha256']
    assert deployment['third_party_jar_hashes'] == {p.name: sha(p) for p in target.parent.glob('*.jar') if p != target}
    shutil.copy2(instance / 'logs/latest.log', LOG / 'client-session.log')
    screens = {'client-after-fog-debug.png': '2026-11-09_07.06.54.png',
               'client-after-fog-seam.png': '2026-11-09_07.07.32.png',
               'client-after-resource-reload.png': '2026-11-09_07.12.43.png',
               'client-side-transition.png': '2026-11-09_07.14.42.png',
               'client-far-4-native-zero.png': '2026-11-09_07.16.58.png'}
    for name, original in screens.items():
        shutil.copy2(instance / 'screenshots' / original, LOG / name)
    restored = {}
    for name, destination in [('options.txt', instance / 'options.txt'),
                               ('hk3gtl-farview-client.toml', instance / 'config/hk3gtl-farview-client.toml')]:
        backup = prior / 'client-settings-before' / name
        snapshot = LOG / ('client-tested-' + name)
        if not snapshot.exists():
            shutil.copy2(destination, snapshot)
        shutil.copy2(backup, destination)
        assert sha(destination) == sha(backup)
        restored[name] = dict(restored=True, sha256=sha(destination), source=str(backup.relative_to(ROOT)))
    samples = {name.replace('-', '_'): profile(LOG / 'client-profiles' / (name + '.zip'))
               for name in ['near-4-enabled', 'near-4-disabled']}
    cameras = []
    for name in ['near-4-enabled', 'near-4-disabled']:
        with zipfile.ZipFile(LOG / 'client-profiles' / (name + '.zip')) as archive:
            cameras.append(archive.read('server/levels/minecraft/overworld/entities.csv').decode())
    assert cameras[0] == cameras[1], '帧时间对照机位不一致'
    raw = (LOG / 'client-session.log').read_text(encoding='utf8', errors='replace')
    status_lines = [line for line in raw.splitlines() if '[CHAT]' in line and 'HK3GTL' in line
                    and any(marker in line for marker in ['远景', '分区'])]
    assert any('98批' in line and '2646' in line for line in status_lines)
    assert 'Reloading ResourceManager' in raw
    failures = [line for line in raw.splitlines() if 'HK3GTL真实表面远景批次构建失败' in line]
    assert not failures, '远景批次构建发生错误'
    result = dict(updated_at=datetime.now(timezone.utc).isoformat(), revision=228,
        status='r228实机复测：4区块远景、原版雾距缺口修复、侧面与资源重载通过；固定机位性能对照已归档，建造中性能另验。',
        world='HK3GTL_Farview_r226_ClientTest', instance_version='增强版3.5 / Minecraft 1.20.1 / Forge 47.4.16',
        original_world_unchanged=True, original_world_file_count=len(after), third_party_jars_unchanged=True,
        installed_sha256=sha(target), client_normally_closed=True, shutdown_guard=guard,
        settings_restored=restored,
        tested_settings=dict(render_distance_chunks=4, simulation_distance_chunks=8,
            far_distance_blocks=2048, gpu_vertex_budget_mib=32, vsync=False, display_pixels=[854, 480]),
        hardware=dict(cpu='Intel Core i5-14400F', gpu='NVIDIA GeForce RTX 5060 Ti', java='Microsoft 21.0.7', max_heap_mib=8192),
        same_position_in_profile_pair=True, camera_evidence=cameras[0], measured_profiles=samples,
        cache_sample=dict(exact_sections=2646, cached_regions=120, drawn_batches=98, vertex_gpu_kib=5879, limited=0),
        runtime_status_lines=status_lines,
        visual_checks_passed=True,
        visual_acceptance_scope='当前I34已建静态部分；同机位雾距缺口、4区块远景、侧面重定位及F3+T材质恢复。',
        native_rendered_chunks_at_far_camera=0, native_geometry_mib_at_far_camera=0,
        near_camera=[-1.5, 405, -394.5, -180, 22], side_camera=[-159.5, 405, -429.5, -150, 22],
        far_camera=[-1.5, 580, 120.5, -180, 18],
        resource_reload_observed=True, stationary_performance_sample_completed=True,
        continuous_movement_performance_verified=False, construction_performance_verified=False,
        performance_checks_passed=False, all_client_acceptance_passed=False,
        game_formation_verified=False, implementation_test_passed=False,
        screenshots=[str((LOG / name).relative_to(ROOT)) for name in screens],
        remaining='连续飞行/转头的透明排序、建造期间帧时间、低端设备及完整控制器成型运行仍待专项验收。当前机器只检查已建部分，不记全机成型；系统分数保持。',
        limits=['短时固定机位10秒，含原版分析器开销；昼夜、缓存补全与后台加载存在变化，不能推算所有配置帧率。',
                '开关或资源重载后GPU批次分帧重建，画面会短暂逐步出现；瞬移有加载卡顿，未当作连续移动流畅通过。',
                '当前测试只比较真实静态面与材质，第三方动态方块实体、世界依赖CTM及全部透明排序未验收。',
                '原版分析器导出多维度example_crash报告及短时服务器落后，未视为实际游戏崩溃。',
                '水下、失明、黑暗等特殊雾守卫已编译；本轮没有逐种客户端验证，不记实测通过。'])
    write_json(LOG / 'client-results.json', result)
    print(json.dumps(dict(source_unchanged=True, original_world_files=len(after), settings_restored=True,
                         profiles=samples), ensure_ascii=False))


if __name__ == '__main__':
    main()
