# -*- coding: utf-8 -*-
"""归档真实客户端证据，恢复选项并核对未触及的原存档和第三方包。"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from deploy_industrial_build import target_process_guard

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    folder = ROOT / 'logs/i34-native-fx-r234-20261109'
    base = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
    guard = target_process_guard()
    assert guard['target_replace_allowed'], '测试客户端必须正常关闭'
    deployment = json.loads((folder / 'deployment.json').read_text(encoding='utf8'))
    assert sha(base / 'mods/HK3GTL-内测5.jar') == deployment['sha256']
    others = {p.name: sha(p) for p in (base / 'mods').glob('*.jar') if p.name != 'HK3GTL-内测5.jar'}
    assert others == deployment['third_party_hashes']
    original = base / 'saves/HK3GTL_W03_C9_特效_r221'
    manifest = json.loads((ROOT / 'logs/w03-c9-controller-r231-20261109/original-world-manifest.json').read_text(encoding='utf8'))
    assert {str(p.relative_to(original)): sha(p) for p in original.rglob('*') if p.is_file()} == manifest
    shutil.copy2(base / 'logs/latest.log', folder / 'client-r234-completed.log')
    log = (folder / 'client-r234-completed.log').read_text(encoding='utf8')
    assert '11:32:51.205' in log and '7464621' in log and '803369' in log
    assert '树影绘制失败' not in log and '树影读取失败' not in log
    assert '11:46:53.776' in log and 'formed machine=hk3gtl:i34_imaginary_tree_observation_array' in log
    assert '11:50:42' in log or '未找到强制加载的区块' in log
    shots = {'2026-11-09_11.47.27.png': 'r234-gt-repaired.png', '2026-11-09_11.48.45.png': 'r234-tree-repaired.png'}
    for source, name in shots.items():
        shutil.copy2(base / 'screenshots' / source, folder / name)
    (folder / 'options-after-test.txt').write_bytes((base / 'options.txt').read_bytes())
    (base / 'options.txt').write_bytes((folder / 'options-before.txt').read_bytes())
    result = json.loads((folder / 'client-results.json').read_text(encoding='utf-8-sig'))
    result.update(
        status='r234真实GT成型、树影待机、创造运行光流、暂停恢复、关闭、拆块停效与修复恢复均已实测通过',
        updated_at=datetime.now(timezone.utc).isoformat(),
        gt_formation_verified=True, fx_idle_verified=True, fx_motion_verified=True,
        fx_pause_verified=True, fx_resume_verified=True, fx_off_verified=True,
        fx_break_verified=True, fx_repair_verified=True, fx_regression_verified=True,
        production_verified=False, implementation_test_passed=False, low_end_verified=False,
        test_world='HK3GTL_Farview_r226_ClientTest', test_world_only=True,
        old_structure_missing_blocks_rebuilt=803369, strict_build_cells_checked=7464621,
        fixture_forced_chunks=775, forced_chunks_baseline=0, forced_chunks_final=0,
        pause_seconds_apart=47, mutation_position=[-24,361,-450],
        mutation_original='hk3gtl:industrial_port_casing', mutation_restored=True,
        native_render_chunks=12, simulation_chunks=8,
        w03_current_source_verified=True, w03_new_client_test=False,
        w03_far_distance_config=2048, w03_client_cull_distance=2500,
        w03_previous_observed_distance=750,
        w03_prior_evidence='logs/w03-c9-controller-r231-20261109/client-results.json',
        client_exited_normally=True, original_world_unchanged=True,
        third_party_unchanged=True, options_restored=True,
        verification_scope='真实I34必须先GT成型；run/idle/off为创造视觉工况，不改变研究、配方或产出。暂停对照47秒；破坏与修复均由原GT检查联动。',
        remaining='I34生产配方、研究产出、多人、低端设备及自然区块卸载后的持续运行未验；本轮使用临时完整服务端区块加载，已清理。W03沿用r233的750格实测，2048为配置目标，非本轮新距离实测。',
        screenshots=sorted(p.name for p in folder.glob('r234-*.png')),
        completed_log='client-r234-completed.log', final_guard=guard)
    (folder / 'client-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print('I34特效实测证据已归档；原存档251文件、92第三方JAR未变；测试选项已恢复。')

if __name__ == '__main__':
    main()
