# -*- coding: utf-8 -*-
"""归档r227真实近远景对照及低视距交接缺陷，保留中断历史。"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

from finish_farview_batch_20261109 import ROOT, LOG, PRIOR, profile, write_json


def main():
    instance = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
    manifest = json.loads((PRIOR / 'source-world-manifest.json').read_text(encoding='utf8'))
    source = Path(manifest['source'])
    after = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in source.rglob('*') if p.is_file()}
    assert after == manifest['files'], '原存档发生变化，不得宣称未改动'
    shutil.copy2(instance / 'logs/latest.log', LOG / 'client-session-resumed.log')
    enabled = profile(LOG / 'client-profiles/near-enabled.zip')
    disabled = profile(LOG / 'client-profiles/near-disabled.zip')
    cameras = []
    for name in ['near-enabled', 'near-disabled', 'far-4-enabled', 'far-4-disabled']:
        with zipfile.ZipFile(LOG / ('client-profiles/' + name + '.zip')) as archive:
            cameras.append(archive.read('server/levels/minecraft/overworld/entities.csv').decode())
    assert cameras[0] == cameras[1] and cameras[2] == cameras[3], '对照相机坐标不一致'
    raw = (LOG / 'client-session-resumed.log').read_text(encoding='utf8', errors='replace')
    status_lines = [line for line in raw.splitlines() if '[CHAT]' in line and 'HK3GTL' in line
                    and any(marker in line for marker in ['远景', '分区'])]
    assert any('88批' in line and '1768' in line for line in status_lines)
    assert any('已关闭' in line for line in status_lines)
    result = dict(updated_at=datetime.now(timezone.utc).isoformat(),
        status='r227近远景开关对照完成；4区块视距仍可见远景，但近景交接发现原版雾距缺口，交r228修复，未通过整体验收。',
        user_stopped_computer_use=False, computer_use_stopped=False,
        user_authorized_resume=True, computer_use_resume_succeeded=True,
        interrupted_history='先前物理Esc中断及恢复失败记录保存在client-results-before-resume.json；本轮恢复成功。',
        world='HK3GTL_Farview_r226_ClientTest', original_world_unchanged=True, original_world_file_count=len(after),
        camera_same_in_both_profiles=True, camera_evidence=cameras[0], far_camera_evidence=cameras[2],
        hardware=dict(cpu='Intel Core i5-14400F', gpu='NVIDIA GeForce RTX 5060 Ti',
                      display_pixels=[854, 480], java='Microsoft 21.0.7', max_heap_mib=8192),
        settings=dict(render_distance_chunks=12, simulation_distance_chunks=8, far_distance_blocks=2048,
                      gpu_vertex_budget_mib=32, vsync=False, effective_fps_limit='inf',
                      saved_options_maxFps=260, effective_limit_evidence='r226 F3实景显示inf；未修改原设置以强制解除上限。'),
        measured_profiles=dict(near_enabled=enabled, near_disabled=disabled,
            far_4_enabled=profile(LOG / 'client-profiles/far-4-enabled.zip'),
            far_4_disabled=profile(LOG / 'client-profiles/far-4-disabled.zip')),
        measured_draw_calls=dict(r226=1780, r227=88, reduction_percent=(1 - 88 / 1780) * 100),
        r227_cache=dict(exact_sections=1768, draw_batches_cached=78, vertex_gpu_kib=4676, limited=0),
        near_view_observed=True, near_material_gaps_observed=True,
        immediate_off_confirmed=True, current_farview_enabled=True, client_normally_closed=True,
        low_render_distance_chunks=4, low_render_far_visible=True, native_geometry_zero_far_visible=True,
        native_fog_seam_found=True, followup_revision=228,
        visual_checks_passed=False, performance_checks_passed=False, paired_near_performance_sample_completed=True,
        game_formation_verified=False, implementation_test_passed=False,
        screenshots=['logs/farview-batch-r227-20261109/client-near-enabled.png',
                     'logs/farview-exact-r226-20261109/client-near-debug.png',
                     'logs/farview-batch-r227-20261109/client-far-native-zero.png',
                     'logs/farview-batch-r227-20261109/client-far-4-debug.png',
                     'logs/farview-batch-r227-20261109/client-far-4-disabled.png',
                     'logs/farview-fog-r228-20261109/client-before-fog-seam.png'],
        runtime_status_lines=status_lines,
        limits=['仅在这台电脑854×480窗口、固定近景视角进行10秒采样，包含原版分析器开销。',
                'r226两轮处于缓存逐步补全期；r227测试读取已保存1768分区，跨版本数字不可当作普适提速倍率。',
                '游戏时段不同且加载后台有波动；样本仅作当前场景诊断，未验低端设备或建造期间帧率。',
                '4区块近景交接出现真实原版雾距缺口，不能因远处显示与性能对照通过就记画面整体通过。',
                '未完成连续移动、玻璃排序、资源重载与建造期间性能检查；已建部分远景不等于全机搭完。',
                '原版分析器生成多维度example_crash报告，日志出现Preparing crash report；客户端未退出，该导出不等于实际游戏崩溃。'],
        remaining='r228修复低视距近景雾与远景不一致后，以同机位客户端复测；继续检查移动交接和重载。低端硬件与建造期间性能、完整控制器成型运行另验；原配置最终停机后恢复。系统分数不变。')
    write_json(LOG / 'client-results.json', result)
    print(json.dumps(dict(source_unchanged=True, enabled=enabled, disabled=disabled, fog_seam_found=True), ensure_ascii=False))


if __name__ == '__main__':
    main()
