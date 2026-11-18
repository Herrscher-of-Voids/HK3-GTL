import base64
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
import shutil

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
from w13_common_20261117 import ROOT, OUT, LOG, CORE, CONTROLLER, materials
from w13_base_20261117 import build_base, LASER_SOURCES
from w13_arms_core_20261117 import build_arms, build_rings, build_core
from w13_canopy_20261117 import build_canopy


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def export_nbt(keys, states, size, palette):
    w, h, d = size
    header, _ = headers([m['state'] for m in palette], (h, d, w), len(keys))
    with gzip.open(OUT / 'W13-蚀界研究母机-A1.nbt', 'wb', compresslevel=6) as stream:
        stream.write(header)
        for start in range(0, len(keys), 65536):
            current = keys[start:start + 65536]
            raw = np.tile(np.frombuffer(RECORD, np.uint8), (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current // (w * d), current // w % d
            rows['state'] = states[start:start + 65536].astype(np.int32) - 1
            stream.write(raw.tobytes())
        stream.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')
    return header


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    palette = materials()
    base = build_base()
    print(f'基座：{len(base)}件，{sum(len(p.p) for p in base):,}格', flush=True)
    arms, anchors = build_arms()
    print(f'六臂：{sum(len(p.p) for p in arms):,}格', flush=True)
    rings, ring_specs = build_rings()
    print(f'三环：{sum(len(p.p) for p in rings):,}格', flush=True)
    core, cube_spec = build_core(anchors)
    print(f'核心：{sum(len(p.p) for p in core):,}格', flush=True)
    canopy, rain = build_canopy()
    parts = base + arms + rings + core + canopy
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    values = np.concatenate([p.states for p in parts])
    source_blocks = len(keys)
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(values) - chosen - 1
    values, owners = values[chosen], owners[chosen]
    xyz = np.c_[keys % w, keys // (w * d), keys // w % d].astype(np.int32)
    np.savez_compressed(OUT / '完整整数格模型.npz', xyz=xyz, states=values, origin=low, size=size, owners=owners)
    source_parts = {}
    for part in parts:
        source_parts[part.name + '_xyz'] = part.p
        source_parts[part.name + '_states'] = part.states
    np.savez_compressed(OUT / '原始完整分件.npz', **source_parts)
    packed, quads, components = [], 0, []
    for i, part in enumerate(parts):
        selected = owners == i
        item, count = mesh_part(part, palette)
        item['blocks'] = int(selected.sum())
        item['source_blocks'] = len(part.p)
        item['modelId'] = part.metadata['group']
        packed.append(item)
        quads += count
        components.append(dict(id=part.name, label=part.label, source_blocks=len(part.p), blocks=int(selected.sum()), shared_cells_overwritten=int(len(part.p) - selected.sum()), metadata=part.metadata))
        print(f'表面{i + 1}/{len(parts)} {part.name}：{count:,}', flush=True)
    notes = [
        '采用作者黑、冷白、霓虹粉红配色，左三臂保留白金与蓝冷却管，右三臂为粉色结晶侵蚀。所有主体均为实际整数格和原生像素贴图。',
        '名义1035×966×332；完整220边长立方框采用体对角竖直、单角朝下姿态。环带、框角、鳍片与结晶不裁切，实际尺寸从完整实体坐标求得。',
        '四座黑盒各200×200×60，布置在四角安装井，真实对角开口露出红色电路与内部算力列；副塔形制为作者工业设计。',
        '六曲臂从Y20至Y240，220格为曲臂纵向跨度，下段嵌入底座；中层81..240是主要外露区域。八个裂开框角通过八条粉色能量链连接六臂。',
        '三环中心线直径750/600/450、中心Y120/160/200、倾角15/-25/40度，径向18格、轴向12格；外鳍片计入实际边界。',
        '南侧终端宽120、高40；唯一红石主控标记位于源坐标(0,47,470)，朝南。其余全部实体格均可自由替换合法接口，位置和朝向由玩家决定。',
        '13座倒碑、残缺蜂窝顶网、数据垂线为固定整数格。网页运行演示包括三环绕各自倾斜法线转动、晶花搏动、碑群浮动、四束绯红激光和数据雨。NBT保存零秒静态格。']
    views = dict(
        well=dict(label='深坑与四座黑盒', center=[0, 43, -.5], half=[520, 55, 485], direction=[-.65, 1.4, 1]),
        clean=dict(label='完整侧白金机械臂', center=[-330, 155, -.5], half=[180, 140, 365], direction=[-1, .45, .65]),
        corrupt=dict(label='侵蚀侧结晶机械臂', center=[355, 180, -.5], half=[210, 175, 365], direction=[1, .4, .7]),
        core=dict(label='单尖白金柜与晶花', center=CORE.tolist(), half=[190, 215, 205], direction=[-.7, .35, 1]),
        rings=dict(label='三道拓扑算力环', center=[0, 180, -.5], half=[395, 190, 395], direction=[-.8, .7, 1]),
        flower=dict(label='几何水晶曼陀罗', center=[0, 252, -.5], half=[105, 52, 105], direction=[-.5, .85, 1]),
        canopy=dict(label='十三倒碑与数据天幕', center=[0, 291, -.5], half=[465, 65, 430], direction=[-.7, 1.1, 1]),
        controller=dict(label='南侧唯一主控', center=CONTROLLER.tolist(), half=[66, 26, 30], direction=[-.3, .55, 1]),
        pixels=dict(label='白甲与冷却管像素近景', center=[-305, 165, -.5], half=[25, 24, 25], direction=[.8, .4, -1]))
    models = [dict(id=group, title=title, features=features, views=views) for group, title, features in [
        ('base', '黑盒深坑与工业基座', ['八角阶梯深坑、斜向液压肋骨、四黑盒真开口、八格流体主管。', notes[5]]),
        ('arms', '白金与侵蚀六翼', ['左三臂完整白金蓝，右三臂粉色棱柱侵蚀。', '六臂与八个破裂框角之间为真实粉色能量链。']),
        ('core', '三环与自演算心脏', [notes[4], '220边长白金框单尖朝下，D140黑球上方绽放D180几何晶花。']),
        ('canopy', '十三倒碑与蜂窝天幕', ['十三座20×20×70倒悬碑，顶网布置在900×850范围内。', '数据线长20..80格，动画脉冲和固定线分开保存。'])]]
    data = dict(title='W13 侵蚀之律者·蚀界·自演算研究母机', candidate='A1', bounds=dict(min=low.tolist(), max=high.tolist()),
        sizeXYZ=size, nominalSizeWDH=[1035, 966, 332], total_blocks=len(keys), models=models, views=views, design=notes,
        effects=dict(core=CORE.tolist(), laser_target=[0, 180, -.5], laser_sources=LASER_SOURCES, rain=rain))
    payload = json.dumps(dict(data=data, materials=palette, parts=packed), ensure_ascii=False, separators=(',', ':')).encode()
    (OUT / 'data.js').write_text('window.W13_VOXEL_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(payload, compresslevel=6)).decode()) + ';\n', 'utf8')
    counts = {m['state']: int((values == i + 1).sum()) for i, m in enumerate(palette)}
    baseline = dict(footprint_area=900601, bounding_box_volume=441313404, actual_height=636, blocks=23541415, unique_block_types=58)
    geometry = dict(machine='W13', candidate='A1', status='作者蓝图完整方块预览待审', recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        nominal_size_wdh=[1035, 966, 332], actual_size_wdh=[w, d, h], bounds=data['bounds'], blocks=len(keys), source_component_voxels=source_blocks,
        shared_component_cells=source_blocks - len(keys), surface_quads=quads, components=components, material_counts=counts,
        footprint_area=w * d, bounding_box_volume=w * d * h, actual_height=h, unique_block_types=int(len(np.unique(values))),
        non_vanilla_percent=100 * sum(n for state, n in counts.items() if not state.startswith('minecraft:')) / len(keys),
        controller=dict(source_xyz=CONTROLLER.tolist(), export_xyz=(CONTROLLER - low).tolist(), facing='south', preview_state='minecraft:redstone_block'),
        rings=ring_specs, cube_frame=cube_spec, obelisk_count=13, data_rain_lines=len(rain), source_notes=notes,
        runtime=dict(controller='hk3gtl:w13_self_computing_research_mother', tier='CEV', tier_index=30, research='RN-ASR', formal_blueprint_present=False),
        appearance_approved=False, game_code_modified=False, jar_built=False, installed=False, game_started=False, game_verified=False, scores_changed=False)
    geometry['scale_comparison'] = dict(source='既有W09 F2与W11 A1记录的CEV低阶比较baseline，保留原证据范围',
        coverage='已记录比较值；完整低阶批准材料清单待统一核对', metrics={k: dict(candidate=geometry[k], recorded_lower_tier_max=v, greater=geometry[k] > v) for k, v in baseline.items()},
        exception_approved=False, w09_w11_exceptions_apply=False)
    conflicts = dict(nominal_size_wdh=[1035, 966, 332], actual_size_wdh=[w, d, h],
        source='本轮负责人提供的W13作者设计，不标为崩坏3官方原型复刻',
        dimensional_notes=[
            '220边长立方框单角朝下时，本体竖向220√3≈381.05；无法同时满足直径260、Y140..290和全机高332。A1保留边长与单尖姿态，完整导出。',
            '三环按原半径和倾角后进入基座层，第三环高于332；框架和曲臂之间也需后续完整运动净空讨论。当前未以删格、移位或缩小处理。',
            '八个框角采用八条链连接六臂，其中两臂各连接两条，全部连接保留。',
            '顶层241..332解释为连续高度范围，整数碑群静态及±4格浮动按实际边界记录。'],
        actual_core_frame=geometry['cube_frame'], ring_specs=ring_specs, scale_comparison=geometry['scale_comparison'],
        interface_policy=notes[5], material_exception_approved=False,
        overlaps='NBT逐格合并采用后写构件优先；网页与原始完整分件NPZ保留各件全部整数格，使独立显示与转动连续。共享格包含正常机械连接，逐件记录覆盖数，穿模待后续处理。')
    for name, value in [('geometry.json', geometry), ('materials.json', palette), ('conflicts.json', conflicts), ('作者条目落实.json', dict(source_type='本轮用户消息', source_date='2026-11-17', notes=notes, rings=ring_specs, frame=cube_spec, nominal_size_wdh=[1035, 966, 332]))]:
        save(OUT / name, value)
    header = export_nbt(keys, values, size, palette)
    with gzip.open(OUT / 'W13-蚀界研究母机-A1.nbt', 'rb') as stream:
        header_equal = stream.read(len(header)) == header
        read_count, same = 0, True
        for start in range(0, len(keys), 65536):
            count = min(65536, len(keys) - start)
            rows = np.frombuffer(stream.read(count * RECORD_DTYPE.itemsize), RECORD_DTYPE)
            got = (rows['y'].astype(np.int64) * d + rows['z']) * w + rows['x']
            same = same and np.array_equal(got, keys[start:start + count]) and np.array_equal(rows['state'] + 1, values[start:start + count])
            read_count += len(rows)
        tail = stream.read()
    save(OUT / 'NBT回读.json', dict(header_equal=header_equal, nbt_blocks=read_count, coordinates_and_states_equal=same, expected_blocks=len(keys), trailing_entities_hex=tail.hex()))
    for name in ['w13_common_20261117.py', 'w13_base_20261117.py', 'w13_arms_core_20261117.py', 'w13_canopy_20261117.py', __file__.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]]:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    save(LOG / 'generation.json', geometry)
    files = [p for p in OUT.rglob('*') if p.is_file() and p.name != 'manifest.json']
    save(OUT / 'manifest.json', dict(machine='W13', candidate='A1', actual_size_wdh=[w, d, h], blocks=len(keys), appearance_approved=False,
        files={p.relative_to(OUT).as_posix(): dict(bytes=p.stat().st_size, sha256=digest(p)) for p in files}))
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), parts=len(parts), materials=geometry['unique_block_types'], quads=quads), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
