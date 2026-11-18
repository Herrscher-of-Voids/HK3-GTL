# -*- coding: utf-8 -*-
"""归档C9客户端实测证据，并核对原存档、第三方JAR及测试选项恢复。"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from deploy_industrial_build import target_process_guard


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    log = ROOT / 'logs/w03-c9-native-r221-20261108'
    assert not (log / 'client-verification.json').exists(), '实测证据已存在，禁止覆盖'
    guard = target_process_guard()
    deployment = json.loads((log / 'deployment-r223.json').read_text(encoding='utf8'))
    instance = Path(deployment['instance'])
    assert sha(Path(deployment['target'])) == deployment['installed_sha256']
    third = {p.name: sha(p) for p in (instance / 'mods').glob('*.jar') if p.name != 'HK3GTL-内测5.jar'}
    assert third == deployment['third_party_jar_hashes']
    start = json.loads((log / 'world-start.json').read_text(encoding='utf8'))
    source = Path(start['source_world'])
    current = {str(p.relative_to(source)): sha(p) for p in source.rglob('*') if p.is_file()}
    assert current == start['source_hashes'], '原存档发生变化'
    game_log = (instance / 'logs/latest.log').read_text(encoding='utf8', errors='replace')
    assert re.search(r'W03 C9 · 0/517262面 · 0批 · GPU 0MiB', game_log)
    assert re.search(r'C9真实尺寸特效开始分帧上传.*?W03 C9 · 517262/517262面 · 84批 · GPU 47MiB · 播放中', game_log, re.S)
    assert 'W03 C9特效显示失败' not in game_log
    assert 'W03 C9特效加载失败' not in game_log
    assert all(f'{t}.0秒定格' in game_log for t in (0, 47, 137))
    shutil.copy2(instance / 'logs/latest.log', log / 'r223-client-test.log')
    shutil.copy2(instance / 'screenshots/2026-11-08_22.34.32.png', log / 'game-c9-reloaded.png')
    evidence = ['game-c9-front-000.png', 'game-c9-front-047.png', 'game-c9-front-137.png', 'game-c9-reloaded.png']
    assert all((log / name).is_file() for name in evidence)
    audit = instance / 'logs/hk3gtl-research-audit/20261108-221950-8ae6c5e0-124c-4b0d-b352-2cc3540d3058'
    for name in ('report.json', 'manifest.json'):
        shutil.copy2(audit / name, log / ('r223-research-' + name))
    options = instance / 'options.txt'
    shutil.copy2(options, log / 'options-after-test-before-restore.txt')
    options.write_bytes((log / 'options-before.txt').read_bytes())
    assert options.read_bytes() == (log / 'options-before.txt').read_bytes()
    report = dict(
        passed=True, verified_at=datetime.now(timezone.utc).isoformat(), revision=223,
        pack_version='3.5', minecraft='1.20.1', forge='47.4.16',
        scope='增强版3.5客户端原生特效试装；未放置664万世界方块，未验GT整机成型或工艺。',
        full_model_quads=517262, voxel_count=6642464, groups=33, moving_groups=32,
        batches=84, gpu_vertex_bytes=49657152, gpu_mib_reported=47,
        actual_materials_verified=True, continuous_live_motion_observed=True,
        render_distance_chunks=4, simulation_distance_chunks=5,
        full_model_visible_beyond_loaded_chunks=True, pose_seconds=[0, 47, 137],
        screenshots=evidence, screenshot_sha256={name: sha(log / name) for name in evidence},
        hide_cache_zero=True, reload_complete=True, no_w03_renderer_error=True,
        build_and_native_matrix_test_passed=True,
        offline_360_second_clearance='logs/w03-c5-outer-down-c9-20261108/continuous-clearance.json',
        continuous_pair_proofs=528,
        original_world_unchanged=True, original_world_files=len(current),
        third_party_unchanged=True, options_restored=True, process_guard=guard,
        game_formation_verified=False, research_graduation_unmodified=True,
        limitations=['客户端检查包含连续播放和0、47、137秒姿态；不是360秒逐帧实机穷举。',
                     'GT正式Pattern、通用接口成型、生产配方及多人同步尚未验收。',
                     '本机观察不代表手机或低端设备性能验收。'],
        fixes=['r222移除增强版3.5已经删除的GTL旧配置字段读取。',
               'r223修复VertexBuffer绘制重设采样器导致的材质错误。'],
        next_focus='W02 Gemini 十二翼重构船坞V3；仍为未批准候选。')
    (log / 'client-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: report[k] for k in ('passed', 'revision', 'original_world_files', 'third_party_unchanged', 'options_restored', 'next_focus')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
