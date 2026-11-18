# -*- coding: utf-8 -*-
"""修订181：从第九批不可变批准档案提升完整建筑，保留原位接口与全部高度。"""
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
LOG = ROOT / 'logs/batch09-install-20261027'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
MACHINES = {
    'I34': ('i34_imaginary_tree_observation_array', 'IRV'),
    'I35': ('i35_imaginary_space_anchoring_array', 'IRV'),
    'I36': ('i36_honkai_reality_stability_anchor', 'QSV'),
    'I38': ('i38_imaginary_energy_rectification_hub', 'IWV'),
    'I39': ('i39_unmanned_cross_boundary_route_relay', 'ICV'),
}
VERSIONS = {'I34': 'V2', 'I35': 'V3', 'I36': 'V1', 'I38': 'V1', 'I39': 'V1'}
GROUPS = {
    'I34': {'世界泡对照档案输入':'item_input', '空间探针输入':'item_input',
        '西侧观测供能':'energy_input', '东侧观测供能':'energy_input', '西侧冷却输入':'fluid_input',
        '东侧冷却回流':'fluid_output', '树与世界联系图输出':'item_output', '虚数观测资料输出':'item_output',
        '观测探针回收':'item_output', '复测档案交付':'item_output'},
    'I35': {'魂钢锚件输入':'item_input', '空间核心组件输入':'item_input', 'I34校准资料输入':'item_input',
        '锚定验证资料输入':'item_input', '西侧锚定供能':'energy_input', '东侧锚定供能':'energy_input',
        '西侧稳定介质':'fluid_input', '东侧介质回流':'fluid_output', '合格锚定组件输出':'item_output',
        '锚定状态与记录输出':'item_output'},
    'I36': {'基础稳定耗材补充':'item_input', '用后耗材回收':'item_output',
        '标定与工况资料输入':'item_input', '覆盖状态与记录输出':'item_output', '西侧持续供能':'energy_input',
        '东侧持续供能':'energy_input', '稳定介质补给':'fluid_input', '用后介质回流':'fluid_output'},
    'I38': {'西侧能量态崩坏能输入':'honkai_input', '东侧能量态崩坏能输入':'honkai_input',
        '稳定介质供给':'fluid_input', '用后介质回流':'fluid_output', '整流参数与来源凭据输入':'item_input',
        '合法记账与测量记录输出':'item_output', '西侧已整流HKE交付':'honkai_output', '东侧已整流HKE交付':'honkai_output',
        '辅助供能西端':'energy_input', '辅助供能东端':'energy_input'},
    'I39': {'发射任务输入':'item_input', '信标坐标输入':'item_input', '无人设备送入':'item_input',
        '维护物资补给':'item_input', '辅助供能输入':'energy_input', '返航装置交接':'item_output',
        '任务状态回执':'item_output', '异常维护处置':'maintenance', '用后材料输出':'item_output',
        '辅助供能回路':'energy_input'},
}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def approved_source(ident):
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    rows = [entry for entry in index['entries'] if entry['id'] == ident]
    assert len(rows) == 1 and rows[0]['approved_version'] == VERSIONS[ident], ('批准版本错误', ident)
    row = rows[0]
    assert row['counts_as_new_machine'] and (row['source_candidate_approved_field'] or row.get('external_approval_is_authoritative'))
    folder = project_path(row['archive'])
    approval = json.loads(project_path(row['approval_manifest']).read_text(encoding='utf-8'))
    for relative, digest in approval['source_files_sha256'].items():
        assert source.sha(folder / relative) == digest, ('不可变批准档案发生变化', ident, relative)
    assert source.sha(project_path(row['archive_zip'])) == row['archive_zip_sha256']
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    assert (manifest['approved'] or row.get('external_approval_is_authoritative')) and manifest['target_voltage'] == MACHINES[ident][1]
    assert {p['id'] for p in manifest['ports']} == set(GROUPS[ident])
    return folder


def build(ident):
    LOG.mkdir(parents=True, exist_ok=True)
    source.MACHINES = MACHINES
    source.LOG = LOG / 'formal-resources'
    source.source_folder = approved_source
    source.group = lambda ident, port: GROUPS[ident][port['id']]
    record = source.build(ident)
    record.update(revision=181, approved_version=VERSIONS[ident], external_approval_is_authoritative=True,
        source_manifest_approved_field_preserved=True,
        process_scope='正式建筑、控制器、原位物品流体仓及完整预览；崩坏能、能源与维护接口允许位置保留，不虚称未实现能力或工艺已运行。')
    save(source.RES / 'structures/approved' / (ident.lower()+'.json'), record)
    save(source.LOG / (ident.lower()+'-verification.json'), record)
    preview = previews.build(ident.lower())
    assert preview['size_xyz'] == record['size_xyz'] and preview['blocks'] == record['blocks']
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
    assert index['pending_batch']['id'] == 'batch-09'
    assert index['pending_batch']['approved_machine_ids'] == list(MACHINES)
    assert index['pending_batch']['count'] == 5 and index['pending_batch']['deployment_eligible']
    old = {}
    for metadata in (source.RES / 'structures/approved').glob('*.json'):
        if metadata.stem.upper() in MACHINES:
            continue
        for path in (metadata, metadata.with_suffix('.nbt'), source.RES / 'approved_architecture' / metadata.name,
                     source.RES / 'structures/approved_preview' / (metadata.stem + '.bin.gz')):
            if path.is_file():
                old[str(path)] = source.sha(path)
    assert len(old) >= 41 * 3
    for ident in MACHINES:
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--key', ident], check=True, cwd=ROOT)
    assert all(source.sha(path) == digest for path, digest in old.items()), '既有41形态发生变化'
    rows = [json.loads((LOG / 'formal-resources' / (key.lower()+'-verification.json')).read_text(encoding='utf-8')) for key in MACHINES]
    save(LOG / 'resource-generation.json', dict(status='passed', revision=181,
        generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(), structures=rows,
        cells=sum(row['blocks'] for row in rows), existing_architecture_unchanged=True,
        existing_resource_sha256=old, existing_structure_forms_unchanged=41,
        complete_height_preserved=True, approved_versions=VERSIONS,
        game_verified=False, instance_modified_by_generator=False))


if __name__ == '__main__':
    main()
