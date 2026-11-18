import base64
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W08_三环分层扩径_A4_20261116'
OUT = ROOT / 'deliveries/0005_W08_双内环球面翻转_A5_20261116'
LOG = ROOT / 'logs/0005-w08-star-a5-20261116'
NBT_NAME = 'W08-恒星核心-A5.nbt'
CENTER = [489, 150, 460]


def save(file, data):
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def motion_bounds(geometry):
    components = {}
    for name, part in geometry['components'].items():
        static_cube_bounds = dict(min=part['bounds']['min'], max=[v + 1 for v in part['bounds']['max']])
        if name in ('star_ring_01', 'star_ring_02'):
            radius = part['cube_radial_envelope']['max']
            low, high = [v - radius for v in CENTER], [v + radius for v in CENTER]
            method = '以实际完整立方体最大球半径包围双轴球心翻转。'
        elif name == 'star_ring_03':
            mask = part['metadata']['effect_mask']
            radius = mask['radial_max']
            low = [CENTER[0] - radius, CENTER[1] - radius, CENTER[2] + mask['axial_min']]
            high = [CENTER[0] + radius, CENTER[1] + radius, CENTER[2] + mask['axial_max']]
            method = '外环保持Z法线自转，以实际平面最大半径及完整轴向厚度包围。'
        else:
            low, high = part['bounds']['min'], [v + 1 for v in part['bounds']['max']]
            method = '静态实体完整单位立方体包围盒。'
        components[name] = dict(static_cube_bounds=static_cube_bounds, bounds=dict(min=low, max=high), method=method)
    low = [min(item['bounds']['min'][axis] for item in components.values()) for axis in range(3)]
    high = [max(item['bounds']['max'][axis] for item in components.values()) for axis in range(3)]
    size = [b - a for a, b in zip(low, high)]
    grid_low, grid_high = [math.floor(v) for v in low], [math.ceil(v) - 1 for v in high]
    grid_size = [b - a + 1 for a, b in zip(grid_low, grid_high)]
    return dict(coordinates='原蓝图坐标；bounds.max为连续实体的上界，不是最后一格的基点。',
                scope='内两环采用完整立方体球包络，外环采用法线自转柱包络；太阳与碎片保持静态。',
                static_cube_bounds=dict(min=geometry['bounds']['min'], max=[v + 1 for v in geometry['bounds']['max']]),
                bounds=dict(min=low, max=high), size_xyz=size, size_wdh=[size[0], size[2], size[1]],
                integer_cover_bounds=dict(min=grid_low, max=grid_high),
                integer_cover_size_wdh=[grid_size[0], grid_size[2], grid_size[1]], components=components)


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    LOG.mkdir(exist_ok=True)
    for name in ['恒星核心构件数据.npz', 'materials.json', '径向净空.json']:
        shutil.copy2(SOURCE / name, OUT / name)
    shutil.copy2(SOURCE / 'W08-恒星核心-A4.nbt', OUT / NBT_NAME)
    for name in ['package_0005_w08_star_a4_20261116.py', 'w08_common_20261116.py', 'w08_sword_reactor_20261116.py']:
        shutil.copy2(SOURCE / '生成脚本' / name, OUT / '生成脚本' / name)
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    geometry = json.loads((SOURCE / 'geometry.json').read_text('utf8'))
    motion = dict(center_xyz=CENTER, theta=dict(idle_radians_per_second=.025, work_radians_per_second=.07),
                  rings=dict(star_ring_01=dict(quaternion='Rz(0.63*theta) * Rx(theta)', mode='双轴球心翻转'),
                             star_ring_02=dict(quaternion='Rz(0.47*theta) * Ry(-0.82*theta)', mode='双轴球心翻转'),
                             star_ring_03=dict(quaternion='Rz(theta)', mode='原Z法线自转')),
                  quaternion_order='右侧旋转先作用，所有旋转共用恒星球心。',
                  prominence_mask='每帧将各环原法线随同一刚体四元数旋转，日珥局部遮罩跟随当前环面。')
    geometry.update(candidate='A5', stage='两道内环球面翻转，外环保持原法线自转',
                    reference_size_wdh=geometry['actual_size_wdh'],
                    reference_size_scope='静态实体NBT、NPZ导出尺寸，所有方块逐格保持A4。', motion=motion)
    for name in motion['rings']:
        metadata = geometry['components'][name]['metadata']
        metadata['cube_sphere_radius'] = geometry['component_cube_radial_envelopes'][name]['max']
        metadata['rigid_sphere_radius'] = metadata['cube_sphere_radius']
        metadata['motion'] = motion['rings'][name]
    envelope = motion_bounds(geometry)
    geometry['motion_envelope'] = envelope
    geometry['clearance_rotation_basis'] = '完整单位立方体绕共同球心作任意刚体旋转，所有点到球心距离保持；A4四项球壳净空对A5两内环双轴翻转继续成立。'
    payload_text = (SOURCE / 'data.js').read_text('utf8')
    config = json.loads(gzip.decompress(base64.b64decode(json.loads(payload_text.split('=', 1)[1].rstrip(';\n')))))
    config['data'].update(candidate='A5', reference_size_wdh=geometry['reference_size_wdh'], motion=motion, motion_envelope=envelope)
    for part in config['parts']:
        if part['id'] in motion['rings']:
            part['metadata'].update(geometry['components'][part['id']]['metadata'])
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode())).decode()
    (OUT / 'data.js').write_text('window.W08_STATIC_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    decision = dict(direction='两道内环球面翻转，外环保留原转法，所有静态实体逐格沿用A4。',
                    geometry='太阳、三环与36片维度片坐标、材料、厚度及形状全部保持，NPZ与NBT直接复制A4。',
                    motion=motion, reference_size_wdh=geometry['reference_size_wdh'],
                    motion_envelope_bounds=envelope['bounds'], clearance_spherical_shells=geometry['clearance_spherical_shells'],
                    clearance_basis=geometry['clearance_rotation_basis'],
                    controller='主控仍未确定；前侧太阳表面锚点仅为提案，未加入定位方块。',
                    effects='随机日珥出生位置、方向、寿命和间隔保留，环面避让遮罩随当前法线旋转。',
                    export='NBT与NPZ保存A4参考姿态；双轴翻转及日珥为网页动态演示。')
    save(OUT / '修改记录.json', decision)
    print(json.dumps(dict(out=str(OUT), reference_size_wdh=geometry['reference_size_wdh'],
                          motion_envelope_bounds=envelope['bounds'], integer_cover_size_wdh=envelope['integer_cover_size_wdh'],
                          clearance=geometry['clearance_spherical_shells'], nbt=NBT_NAME,
                          nbt_sha256=hashlib.sha256((OUT / NBT_NAME).read_bytes()).hexdigest())), flush=True)


if __name__ == '__main__':
    main()
