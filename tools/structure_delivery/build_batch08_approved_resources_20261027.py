# -*- coding: utf-8 -*-
"""修订180：从I29–I33不可变确认档案提升正式结构，并生成完整流式游戏预览。"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from project_paths import project_path
import subprocess
import sys

import build_late_approved_resources_20261026 as source
import build_compact_approved_previews_20261026 as previews

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/batch08-install-20261027'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
MACHINES = {
    'I29': ('i29_simulated_world_bubble_synthesizer', 'ICV'),
    'I30': ('i30_simulated_world_bubble_stabilizer', 'ICV'),
    'I31': ('i31_simulated_world_bubble_termination_reclaimer', 'ICV'),
    'I32': ('i32_relic_technology_reverse_laboratory', 'QAV'),
    'I33': ('i33_imitation_divine_key_assembly_center', 'QCV'),
}
GROUPS = {
    'I29': {'世界模型输入':'item_input', '真实种子输入':'item_input', '西翼物质输入':'item_input',
            '东翼耗材输入':'item_input', '西翼控制能源':'energy_input', '东翼冷却流体':'fluid_input',
            '未稳定批次输出':'item_output', '模型误差记录':'item_output'},
    'I30': {'未稳定模拟载体输入':'item_input', '模型与负载参数':'item_input', '西侧稳定介质输入':'fluid_input',
            '东侧稳定介质输入':'fluid_input', '西侧持续供能':'energy_input', '东侧持续供能':'energy_input',
            '可终止模拟载体输出':'item_output', '运行档案输出':'item_output', '废介质排出':'fluid_output', '热回流排出':'fluid_output'},
    'I31': {'稳定模拟批次输入':'item_input', '批次核验及许可':'item_input', '西侧终止供能':'energy_input',
            '东侧终止供能':'energy_input', '西侧流体回收':'fluid_output', '东侧流体回收':'fluid_output',
            '随机物品输出':'item_output', '模拟日志输出':'item_output', '残件交付':'item_output', '回收热流体排出':'fluid_output'},
    'I32': {'遗留技术残片输入':'item_input', '真实模拟日志输入':'item_input', '西侧实验供能':'energy_input',
            '东侧实验供能':'energy_input', '西侧试剂输入':'fluid_input', '东侧废试剂输出':'fluid_output',
            '逆向档案输出':'item_output', '复现样件输出':'item_output', '失败样件输出':'item_output', '实验材料输入':'item_input'},
    'I33': {'仿制核心输入':'item_input', '研究许可核验':'item_input', '西侧装配供能':'energy_input',
            '东侧装配供能':'energy_input', '西侧冷却输入':'fluid_input', '东侧冷却回流':'fluid_output',
            '仿制神之键交付':'item_output', '魂钢部件输入':'item_input', '列车信标组件交付':'item_output', '测试残件输出':'item_output'},
}


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def approved_source(ident):
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    rows = [entry for entry in index['entries'] if entry['id'] == ident]
    assert len(rows) == 1 and rows[0]['approved_version'] == 'V1', ('批准记录错误', ident)
    row = rows[0]
    assert row['source_candidate_approved_field'] and row['counts_as_new_machine']
    folder = project_path(row['archive'])
    approval_path = project_path(row['approval_manifest'])
    approval = json.loads(approval_path.read_text(encoding='utf-8'))
    for relative, digest in approval['source_files_sha256'].items():
        assert source.sha(folder / relative) == digest, ('不可变批准档案发生变化', ident, relative)
    assert source.sha(project_path(row['archive_zip'])) == row['archive_zip_sha256']
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['approved'] is True and manifest['target_voltage'] == MACHINES[ident][1]
    assert {p['id'] for p in manifest['ports']} == set(GROUPS[ident])
    return folder


def build(ident):
    LOG.mkdir(parents=True, exist_ok=True)
    source.MACHINES = MACHINES
    source.LOG = LOG / 'formal-resources'
    source.source_folder = approved_source
    source.group = lambda ident, port: GROUPS[ident][port['id']]
    record = source.build(ident)
    record['revision'] = 180
    record['process_scope'] = '正式建筑、控制器、原位仓室和完整预览接入；不开放暂定工艺或未实现的世界泡任务。'
    manifest_path = source.RES / 'structures/approved' / (ident.lower()+'.json')
    save(manifest_path, record)
    save(source.LOG / (ident.lower()+'-verification.json'), record)
    preview = previews.build(ident.lower())
    save(LOG / (ident.lower()+'-compact-preview.json'), preview)
    print(json.dumps(dict(id=ident, blocks=record['blocks'], preview_bytes=preview['compressed_bytes'], passed=True)), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', choices=MACHINES)
    args = parser.parse_args()
    if args.key:
        build(args.key)
        return
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    assert index['pending_batch']['id'] == 'batch-08'
    assert index['pending_batch']['approved_machine_ids'] == list(MACHINES)
    assert index['pending_batch']['count'] == 5 and index['pending_batch']['deployment_eligible']
    for ident in MACHINES:
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--key', ident], check=True, cwd=ROOT)
    rows = [json.loads((LOG / 'formal-resources' / (key.lower()+'-verification.json')).read_text(encoding='utf-8')) for key in MACHINES]
    save(LOG / 'resource-generation.json', dict(status='passed', revision=180,
        generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(), structures=rows,
        cells=sum(row['blocks'] for row in rows), existing_architecture_unchanged=True,
        game_verified=False, instance_modified_by_generator=False))


if __name__ == '__main__':
    main()
