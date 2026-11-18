import hashlib
import math

import numpy as np
from scipy.ndimage import distance_transform_cdt, label
from scipy.spatial import cKDTree

import geometry_0005_w05_wendy_wings_a2_20261115 as a2
import geometry_0005_w05_wendy_wings_a3_20261115 as a3
from geometry_0005_w05_wendy_wings_a2_20261115 import STATES, NAMES


PARTS = []
ROLES = dict(a2.ROLES)
ROLES[a2.GREEN] = '原有工业机壳、翼根后置投射座和局部翼根暗纹'
ROLES[a2.WHITE] = '原有承台、机组及约束轨收边；新翼面不用白色厚边框'
ROLES[a2.CYAN] = '成对宽薄分叉能量翼面、原有导流光带与观察层'
ROLES[a2.GLASS] = '原有渴望晶体外层与新翼根的薄层青绿过渡'
OUTLINE = np.array([(56, 252), (80, 276), (135, 292), (218, 300),
    (360, 296), (405, 280), (265, 266), (368, 239), (382, 212),
    (238, 239), (315, 176), (310, 147), (190, 210), (232, 137),
    (212, 119), (126, 204), (80, 220), (56, 237)])


def wing(side):
    p = a2.Part('energy_wing_' + ('left' if side < 0 else 'right'))
    a2.panel(p, OUTLINE, -3, 3, a2.CYAN, 0)
    p.box([381, 212, -3], [381, 212, 3], a2.CYAN)
    a2.panel(p, [(56, 242), (78, 269), (132, 283), (193, 286),
        (135, 269), (99, 245), (79, 224)], -2, 1, a2.GLASS, 0)
    a2.panel(p, [(57, 243), (77, 266), (121, 276), (99, 256),
        (82, 228), (65, 234)], -3, -2, a2.GREEN, 0)
    for route in [
        [(72, 253, 0), (139, 279, 0), (248, 287, 0), (355, 285, 0)],
        [(77, 248, 0), (136, 249, 0), (211, 251, 0), (325, 239, 0)],
        [(77, 245, 0), (119, 224, 0), (168, 195, 0), (212, 145, 0)],
    ]:
        a2.trace(p, np.asarray(route), .8, a2.LIGHT)
    p = p.finish()
    p.p[:, 2] += np.rint(-145 - (p.p[:, 0] - 56) * .088).astype(np.int32)
    p.p[:, 0] *= side
    return p


def root_projector(side):
    p = a2.Part('wing_root_' + ('left' if side < 0 else 'right'))
    p.box([45, 12, -257], [85, 23, -211], a2.BLACK)
    p.box([49, 24, -253], [81, 28, -215], a2.GREEN)
    a2.trace(p, np.array([[65, 34, -237], [65, 142, -232],
        [65, 229, -218], [65, 248, -204]]), 5, a2.BLACK)
    a2.trace(p, np.array([[65, 34, -231], [65, 142, -226],
        [65, 231, -211]]), 1.5, a2.GREEN)
    a2.hull(p, [(x, y, z) for x, y in [(43, 237), (53, 264),
        (75, 270), (91, 250), (78, 225), (52, 226)] for z in (-215, -183)], a2.GREEN)
    a2.panel(p, [(49, 239), (57, 259), (74, 263), (84, 248),
        (74, 231), (56, 232)], -182, -179, a2.BLACK, 0)
    a2.panel(p, [(58, 240), (61, 253), (72, 256), (77, 246),
        (70, 237), (61, 236)], -178, -176, a2.LIGHT, 0)
    p = p.finish()
    p.p[:, 0] *= side
    return p


def build():
    entries = [(a3.deck(), '扩展三层承托基座'), (a2.collector(), '中央分级集流座'),
        (a2.crystal(), '渴望之心悬浮晶体')]
    for side, name in [(-1, '左'), (1, '右')]:
        entries += [(a2.constraint(side), name + '侧开口约束轨'),
            (root_projector(side), name + '翼集中翼根后置投射座'),
            (wing(side), name + '侧整体分叉薄翼面'),
            (a2.flow_channel(side), name + '侧低位回流槽'),
            (a2.pump(side, -1), name + '后换热泵'),
            (a2.pump(side, 1), name + '前换热泵'),
            (a2.ribbon(side), name + '侧静态导流光带')]
    entries += [(a2.badge(), '前庭风车外圈轮毂与支架')]
    entries += [(a2.badge_sail(i), '风车独立叶片' + str(i + 1)) for i in range(4)]
    entries += [(a2.control(), '前控台与主控定位')]
    PARTS[:] = [dict(id=p.name, name=name) for p, name in entries]
    parts = [p for p, _ in entries]
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = high - low + 1
    cube = np.zeros((size[1], size[2], size[0]), np.uint8)
    owners = np.zeros_like(cube)
    contacts = []
    for index, p in enumerate(parts, 1):
        q = p.p - low
        occupied = owners[q[:, 1], q[:, 2], q[:, 0]]
        counts = np.bincount(occupied, minlength=len(parts) + 1)
        contacts += [dict(first=parts[i - 1].name, second=p.name, voxels=int(counts[i]))
            for i in np.flatnonzero(counts[1:]) + 1]
        owners[q[:, 1], q[:, 2], q[:, 0]] = index
        cube[q[:, 1], q[:, 2], q[:, 0]] = p.states
    if contacts:
        raise ValueError('独立构件交叠：' + str(contacts))
    named = {p.name: p for p in parts}
    pairs = [('gem', 'constraint_left'), ('gem', 'constraint_right'),
        ('gem', 'collector'), ('gem', 'ribbon_left'), ('gem', 'ribbon_right')]
    pairs += [('badge', 'badge_sail_' + str(i)) for i in range(1, 5)]
    for side in ['left', 'right']:
        pairs += [('energy_wing_' + side, other) for other in
            ['wing_root_' + side, 'constraint_' + side, 'gem', 'collector',
             side + '_pump_rear', 'ribbon_' + side]]
    pairs += [('energy_wing_left', 'energy_wing_right')]
    distances = []
    for first, second in pairs:
        distance = float(cKDTree(named[first].p).query(named[second].p,
            k=1, p=np.inf, workers=-1)[0].min())
        distances.append(dict(first=first, second=second,
            minimum_center_chebyshev=distance,
            surface_gap_voxel_lower_bound=max(0, math.floor(distance) - 1)))
    wings = []
    for side in ['left', 'right']:
        p = named['energy_wing_' + side]
        q = p.p - p.p.min(0)
        solid = np.zeros(tuple(q.max(0) + 1), bool)
        solid[q[:, 0], q[:, 1], q[:, 2]] = True
        _, components = label(solid)
        wings.append(dict(id=p.name, blocks=len(p.p), six_connected_components=int(components),
            blueprint_bounds=dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist()),
            thickness_before_sweep=7, outline_xy=(OUTLINE * [(-1 if side == 'left' else 1), 1]).tolist()))
    footprint = owners[11 - low[1]] == 1
    projection = (owners > 1).any(axis=0)
    outside = int(np.count_nonzero(projection & ~footprint))
    margin = int(distance_transform_cdt(footprint, metric='chessboard')[projection].min()) - 1
    if outside:
        raise ValueError('上部投影超出顶层底座：' + str(outside))
    preserved = [dict(id=p.name, coordinate_state_sha256=hashlib.sha256(
        p.p.tobytes() + p.states.tobytes()).hexdigest()) for p in parts
        if not p.name.startswith(('energy_wing_', 'wing_root_'))]
    clearance = dict(method='所有独立构件在合并前按整数格坐标查重；交叠即停止，不覆盖消解、不裁切。净距为最近切比雪夫中心距减一的表面间隔下界。',
        independent_components=len(parts), checked_component_pairs=len(parts) * (len(parts) - 1) // 2,
        cross_component_overlapping_voxels=0, overlap_pairs=[], critical_clearances=distances,
        all_static=True, runtime_animation=False, wings=wings,
        intentional_joins='承台顶面Y=11，落地构件从Y=12起相接；每侧薄翼为一个连续体，投射座与翼面留空气隙。单一构件内材质分区允许覆写。',
        base_projection=dict(bottom_size_wd=[1001, 841], middle_size_wd=[971, 811],
            top_size_wd=[941, 781], outside_top_deck_columns=outside,
            minimum_projected_border_margin_voxels=margin),
        preserved_components=preserved,
        scope='静态完整方块几何；不代替GT成型、运行及特效实机验收。')
    def detail(center, half, position):
        return dict(center=(np.array(center) - low).tolist(), half=half,
            position=(np.array(position) - low).tolist())
    data = dict(title='风之律者 · 长风 · 温蒂风翼与渴望之心 A4 · 原作翼形重构',
        name='0005-w05-wendy-wings-a4', size=size.tolist(),
        controller=(np.array([0, 34, 310]) - low).tolist(), controller_face='south', ports=[],
        summary='保留1001×841三层基座与原位宝石、风车和工业机组；移除十四片独立白边羽板及粗翼骨，重做集中翼根、后掠凹轮廓与成对青绿宽薄能量翼面，后置投射座与翼面留空。全静态。',
        detail_views=dict(core=detail([0, 257, 55], [147, 129, 100], [370, 315, 510]),
            wing=detail([-230, 218, -161], [190, 105, 26], [-440, 257, 520]),
            wingroot=detail([65, 247, -170], [60, 61, 65], [260, 297, 50])),
        palette_identity=dict(tier='HDV', name='风息绿', color='#48C9A3', runtime_voltage='WSV'),
        source_blueprint_bounds=dict(min=low.tolist(), max=high.tolist()),
        source_blueprint_to_export=(-low).tolist(), nominal_clipping=False,
        geometry_clearance=clearance,
        original_translation='翼面轮廓参考游戏Boss实录R01/R02/R07/R12/R24/R28；剧情CG仅辅助宽薄分叉印象。具体方块比例、尖齿分段、发光细线及后置投射座均为建筑转译，不宣称原生模型逐顶点复刻。',
        reference_study='deliveries/0005_W05_温蒂游戏翼形参考校准_20261115/参考清单.json',
        animation_enabled=False, approved=False, installed=False, game_verified=False)
    print('A4几何完成', size.tolist(), int(np.count_nonzero(cube)), len(parts),
        '构件交叠0，基座外投影', outside, '最小外沿', margin,
        '翼面连通分量', [w['six_connected_components'] for w in wings], flush=True)
    return cube, owners, data
