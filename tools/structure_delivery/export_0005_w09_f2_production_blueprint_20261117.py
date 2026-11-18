from datetime import datetime
from pathlib import Path
import json

import numpy as np

import export_0005_w10_a3_production_blueprint_20261116 as shared


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W09_T9与S2山观兵装矩阵_F2_20261117'
BLUEPRINT = ROOT / 'src/main/resources/data/hk3gtl/structures/w09_candidate.bin.gz'
METADATA = BLUEPRINT.with_name('w09_approved.json')
MACHINE = 'hk3gtl:w09_civilization_consensus_matrix'
CONTROLLER = np.array([0, 163, 138])
APPROVAL_QUOTE = '可以，没问题，但是你控制器打算放哪，那就实装一下 F2，也就是 W09'
MATERIAL_EXCEPTION_QUOTE = '按批准的 F2 原样实装，34种作为 W09 专项例外（推荐）'


def main():
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    materials = json.loads((SOURCE / 'materials.json').read_text('utf8'))
    palette = [material['state'] for material in materials]
    with np.load(SOURCE / '完整整数格模型.npz') as archive:
        xyz, states = archive['xyz'], archive['states']
        origin, size = archive['origin'], archive['size']
    w, h, d = map(int, size)
    positions = (xyz[:, 0].astype(np.int64) * h + xyz[:, 1]) * d + xyz[:, 2]
    del xyz
    order = np.argsort(positions)
    positions, states = positions[order], states[order]
    del order
    controller = CONTROLLER - origin
    control_linear = int((controller[0] * h + controller[1]) * d + controller[2])
    control_index = int(np.searchsorted(positions, control_linear))
    previous_state = palette[int(states[control_index]) - 1]
    palette.append(MACHINE + '[facing=south]')
    states[control_index] = len(palette)
    counts = np.bincount(states, minlength=len(palette) + 1)[1:]
    shared.BLUEPRINT, shared.MACHINE = BLUEPRINT, MACHINE
    print(f'完整蓝图：{len(positions):,}格，主控{controller.tolist()}，朝南', flush=True)
    runs = shared.write_blueprint(positions, states, palette, [w, h, d], controller)
    metadata = dict(id='W09', version='0005-W09-F2', controller=MACHINE,
        recorded_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        blueprint='hk3gtl:structures/w09_candidate.bin.gz', conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', appearance_approved=True,
        approval_basis='负责人批准F2原样实装，34种方块作为W09专项例外。',
        approval_quote=APPROVAL_QUOTE, material_exception_approval_quote=MATERIAL_EXCEPTION_QUOTE,
        source=str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        source_manifest_sha256=shared.digest(SOURCE / 'manifest.json'),
        source_npz_sha256=shared.digest(SOURCE / '完整整数格模型.npz'),
        source_materials_sha256=shared.digest(SOURCE / 'materials.json'),
        source_nbt=manifest['nbt'], source_nbt_sha256=manifest['nbt_sha256'],
        source_approval_fields_preserved=True, external_approval_is_authoritative=True,
        size_xyz=[w, h, d], size_wdh=[w, d, h], source_bounds=manifest['bounds'],
        source_origin_xyz=origin.tolist(), blueprint_to_export_offset_xyz=(-origin).tolist(),
        controller_source_xyz=CONTROLLER.tolist(), controller_xyz=controller.tolist(), source_facing='south',
        controller_location='八卦台前缘主控石台，原坐标(0,163,138)，正面朝外侧+Z。',
        controller_previous_state=previous_state, controller_state=palette[-1],
        controller_nbt_blockentity_id=MACHINE, controller_replacements=1,
        block_count=len(positions), source_block_count=manifest['total_blocks'],
        component_count=len(manifest['parts']), source_component_voxels=manifest['part_block_sum'],
        overlap_extra_memberships=manifest['conflicts']['extra_memberships'], full_geometry=True,
        geometry_source='F2完整整数格NPZ，沿用既有归一化坐标，仅重排HK3P线性索引并替换唯一主控标记。',
        merge_priority=manifest['conflicts']['priority'],
        fixed_interface_positions=[], interface_policy='除主控外，全部实体格均可替换合法通用接口，朝向自选。',
        target_voltage='CEV', research='RN-CKV', product='hk3gtl:civilization_consensus_archive',
        palette=palette, palette_count=len(palette), used_palette_count=int(np.count_nonzero(counts)),
        unique_block_types=len({state.split('[', 1)[0] for state, count in zip(palette, counts) if count}),
        material_counts={state: int(count) for state, count in zip(palette, counts)},
        source_scale_comparison=manifest['scale_comparison'],
        material_count_exception=dict(approved=True, scope='仅W09 F2', unique_block_types=34,
            approval_quote=MATERIAL_EXCEPTION_QUOTE),
        runtime_format='HK3P/2；Z最快线性坐标全局升序等差游程；主控原生方块实体NBT。',
        blueprint_linear_index='(x*sizeY+y)*sizeZ+z', rle_record_count=runs,
        blueprint_sha256=shared.digest(BLUEPRINT), blueprint_bytes=BLUEPRINT.stat().st_size,
        minimum_dimension_height=h, dimension_requirement='完整高度801格，须在可容纳整座结构的维度中建造。',
        overworld_vertical_span=384, overworld_height_compatible=False,
        animation_state='F2完整静态实体蓝图，沿用批准参考姿态。',
        game_verified=False)
    shared.save(METADATA, metadata)
    print(json.dumps(dict(block_count=len(positions), palette_count=len(palette),
        used_palette_count=metadata['used_palette_count'], unique_block_types=metadata['unique_block_types'],
        controller=controller.tolist(), facing='south', runs=runs,
        blueprint_bytes=metadata['blueprint_bytes'], blueprint_sha256=metadata['blueprint_sha256'],
        metadata_sha256=shared.digest(METADATA)), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
