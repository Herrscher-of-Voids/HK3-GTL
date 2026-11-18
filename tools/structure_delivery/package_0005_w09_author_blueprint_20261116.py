import base64
from copy import copy
from datetime import datetime
import gzip
import hashlib
from html import escape
import json
import math
from pathlib import Path
import shutil
from zipfile import ZipFile

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
import w09_base_20261116 as base
import w09_landscape_20261116 as landscape
import w09_core_20261116 as core


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_作者蓝图原案_A1_20261116'
LOG = ROOT / 'logs/0005-w09-author-blueprint-a1-20261116'
SOURCE = Path('C:/Users/OWNER/下載/W09 识之律者·万象·文明共识矩阵 巨构工程蓝图.md')
FACES = ('east', 'west', 'south', 'north', 'down', 'up')


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            sha.update(block)
    return sha.hexdigest()


def materials():
    prior = ROOT / 'deliveries/0005_W12_三环翻转_A3_20261116/materials.json'
    result = json.loads(prior.read_text('utf8'))
    labels = ['纯黑水墨底色', '格雷黑色铆钉玄铁装甲', '赤金骨架与羽刃', '格雷无瑕白瓷装甲',
              '本模组识律红机壳', '格雷金色能量线圈', '阴鱼暗紫约束管', '水墨玄玉玻璃',
              '深色散热鳍片', '黑金鎏纹镶边', '绯红力场玻璃', '格雷赤脉发光工业灯',
              '本模组黑色重机壳', '唯一主控定位标记']
    for item, label in zip(result, labels):
        item.update(label=label, role=label)
    red = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/casings/casing_colored_red.png'
    png = red.read_bytes()
    result[4] = dict(state='hk3gtl:casing_colored_red', label=labels[4], role=labels[4],
        faces={face: 'data:image/png;base64,' + base64.b64encode(png).decode() for face in FACES},
        transparent=False, emissive=False, source=dict(file=str(red), png_sha256=digest(red),
            texture_mode='原生像素贴图，无额外染色'))
    vanilla = Path('E:/Prism/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar')
    gt = Path('E:/Prism/instances/GregTech Leisure-增强版/minecraft/mods/gtceu-1.20.1-1.4.4.jar')
    for index, state, archive, entry, transparent, emissive in [
        (7, 'minecraft:black_stained_glass', vanilla, 'assets/minecraft/textures/block/black_stained_glass.png', True, False),
        (11, 'gtceu:red_lamp[bloom=true,inverted=true,lit=true,powered=false]', gt, 'assets/gtceu/textures/block/lamps/red.png', False, True)]:
        with ZipFile(archive) as source:
            png = source.read(entry)
        result[index] = dict(state=state, label=labels[index], role=labels[index],
            faces={face: 'data:image/png;base64,' + base64.b64encode(png).decode() for face in FACES},
            transparent=transparent, emissive=emissive,
            source=dict(archive=str(archive), entry=entry, png_sha256=hashlib.sha256(png).hexdigest(),
                texture_mode='原生像素贴图，无额外染色'))
    save(OUT / 'materials.json', result)
    return result


def export_nbt(keys, states, size, palette):
    w, h, d = size
    header, _ = headers([item['state'] for item in palette], (h, d, w), len(keys))
    record = np.frombuffer(RECORD, np.uint8)
    with gzip.open(OUT / 'W09-文明共识矩阵-A1.nbt', 'wb', compresslevel=6) as handle:
        handle.write(header)
        for start in range(0, len(keys), 65536):
            current = keys[start:start + 65536]
            raw = np.tile(record, (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current // (w * d), current // w % d
            rows['state'] = states[start:start + 65536].astype(np.int32) - 1
            handle.write(raw.tobytes())
        handle.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, OUT / '原文.txt')
    source = dict(path=str(SOURCE), sha256=digest(SOURCE), bytes=SOURCE.stat().st_size)
    palette = materials()
    parts, notes = [], []
    for module in (base, landscape, core):
        current, sampling = module.build()
        parts.extend(current)
        notes.extend(sampling)
        print(f'{module.__name__}: {len(current)}构件，{sum(len(p.p) for p in current):,}构件占格', flush=True)
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    owner = np.zeros(w * h * d, np.uint16)
    state_cube = np.zeros(w * h * d, np.uint8)
    overlaps = []
    for index, part in enumerate(parts, 1):
        p = part.p.astype(np.int64) - low
        keys = (p[:, 1] * d + p[:, 2]) * w + p[:, 0]
        prior = owner[keys]
        hit = prior > 0
        ids, counts = np.unique(prior[hit], return_counts=True)
        overlaps.extend(dict(first=parts[int(i) - 1].name, later=part.name, coincident_voxels=int(n),
            includes_motion=bool(part.metadata.get('motion_speed') or parts[int(i) - 1].metadata.get('motion_speed')))
            for i, n in zip(ids, counts))
        owner[keys], state_cube[keys] = index, part.states
    keys = np.flatnonzero(owner)
    states, owners = state_cube[keys], owner[keys]
    del owner, state_cube
    archive, packed, quads = {}, [], 0
    for index, part in enumerate(parts, 1):
        archive[part.name + '_xyz'], archive[part.name + '_materials'] = part.p, part.states
        visible = copy(part)
        if not part.metadata.get('motion_speed'):
            current = keys[owners == index]
            visible.p = np.c_[current % w, current // (w * d), current // w % d].astype(np.int32) + low
            visible.states = states[owners == index]
        item, count = mesh_part(visible, palette)
        item['source_blocks'] = len(part.p)
        packed.append(item)
        quads += count
        print(f'表面 {index}/{len(parts)} {part.name} {count:,}', flush=True)
    views = {
        'front': dict(label='前斜全景', direction=[-.95, .8, -1.3]),
        'back': dict(label='后斜全景', direction=[.85, .8, 1.2]),
        'frontOrtho': dict(label='正面', direction=[0, .001, -1]),
        'side': dict(label='侧面', direction=[1, .001, 0]),
        'top': dict(label='俯视', direction=[0, 1, .001]),
        'core': dict(label='千羽万象核心', direction=[-.8, .5, -1.2], center=[487, 220, 500], half=[115, 115, 115]),
        'weapons': dict(label='三兵镇岳', direction=[-.7, .5, -1.4], center=[487, 166, 620], half=[350, 160, 290]),
        'mountain': dict(label='机械太虚山', direction=[-.7, .6, -1.2], center=[900, 143, 500], half=[80, 145, 80]),
        'chains': dict(label='实体交扣锁链', direction=[-.65, .7, -1], center=[710, 195, 515], half=[155, 85, 135]),
        'base': dict(label='立体阴阳八卦', direction=[-.65, 1.4, -.9], center=[487, 33, 500], half=[465, 55, 465]),
        'crown': dict(label='折扇与御座', direction=[-.55, .38, -1.2], center=[487, 255, 950], half=[255, 90, 95]),
        'entry': dict(label='天门与拜仙台', direction=[-.65, .8, -1.2], center=[487, 105, 150], half=[130, 100, 185]),
        'controller': dict(label='唯一主控位置', direction=[-.65, .8, -1], center=[487, 160, 260], half=[30, 18, 30]),
        'blocks': dict(label='像素方块近景', direction=[-.65, .7, -1], center=[487, 158, 255], half=[7, 6, 7]),
    }
    interface_rule = '仅主控固定，其余全部实体格可随时替换合法通用接口，位置与朝向由玩家选择。'
    notes.extend([
        '原文975×1025×317为名义宽深高；正文X0..975、Z0..1025、Y0..317为包含端点的坐标。先完整生成再求实际边界，不将名义尺寸当裁切窗口。',
        '正文核心明确坐标(X487,Y220,Z500)作为球心；方块字典的(487,500,220)沿用原文留档，按上下文视为交换Y/Z的顺序差异。',
        '原文前段主控分区Z0..150与具体主控Z260并存，本稿保留更精确主控(487,160,260)，神道延伸到拜仙台。',
        '三道羽环沿原文同直径180、不同倾角生成。转动件逐件保留完整表面及完整原始方块，参考姿态交叠另列，尚未做净空修订。',
        '专用机壳与流体为作者拟定名称；本轮以已存在的格雷、HK3GTL与少量原版同色方块预览，没有新增方块或流体注册。墨海、瀑布的动态流光和能量光带仅为网页特效。',
        '原文指定接口槽与副结构控制器建议服从负责人通用接口规则，本轮只保留唯一主控标记，实体构件不设置固定接口位置。',
        'NBT导出同格后写优先，原始NPZ保留全部独立构件。固定件网页使用相同覆盖归属，参考姿态统计包含正常嵌接、交扣与真实交叠，需结合空间位置判读。',
        '三环同半径来自原文；锁链与拜仙台、武器周边交叠包含本稿挂点、垂度和机械山位置取样，应在后续候选调整。当前零秒19号链与拜仙台重合111格，后匣与3号剑亭重合1806格。',
        '沿用已注册身份w09_civilization_consensus_matrix、CEV、RN-CKV；本轮仅外观候选、完整整数格与网页动态，不改正式蓝图、配方或电压。',
    ])
    streams = []
    for part in parts:
        if part.name.startswith('peak_waterfalls_'):
            heading = (part.metadata['peak_index'] - 1) * math.pi / 4 + math.pi
            inward = np.array([math.cos(heading), 0, math.sin(heading)])
            across = np.array([-inward[2], 0, inward[0]])
            mouth = np.array(part.metadata['exhaust_center_blueprint_xyz'], float)
            streams.extend(dict(top=(mouth + across * sign * 11 + inward * 5).tolist(), bottom_y=5,
                color='#e7293e' if sign == -1 else '#fff4db') for sign in (-1, 1))
    beam_origins = [[220, 225, 500], next(p for p in parts if p.name == 'spear_tower').metadata['beam_origin']]
    feather_emitters = []
    for index, part in enumerate(p for p in parts if p.name.startswith('feather_ring_')):
        normal = np.array(part.metadata['ring_normal'])
        u = np.cross(normal, [0, 1, 0])
        u /= np.linalg.norm(u)
        v = np.cross(normal, u)
        tips = [np.rint(np.array([487, 220, 500]) + 45 * (u * math.cos(a) + v * math.sin(a)))
                + .5 - [487, 220, 500] for a in np.arange(40) * math.pi / 20 + index * math.pi / 60]
        feather_emitters.append(dict(axis=part.metadata['motion_axis'], speed=part.metadata['motion_speed'],
            tips=[tip.tolist() for tip in tips]))
    data = dict(machine_id='W09', title='识之律者·万象·文明共识矩阵', candidate='A1', sizeXYZ=size, size=size,
        bounds=dict(min=low.tolist(), max=high.tolist()), blueprint_to_export_offset_xyz=(-low).tolist(),
        nominal_size_wdh=[975, 1025, 317], core_center=[487, 220, 500], views=views,
        interface_rule=interface_rule, controller_blueprint=[487, 160, 260], controller_status='原文指定位置预览标记',
        runtime_voltage='CEV', research='RN-CKV', effects=dict(beam_origins=beam_origins, waterfalls=streams,
            feather_emitters=feather_emitters))
    counts = {m['state']: int((states == i + 1).sum()) for i, m in enumerate(palette)}
    mod_count = sum(n for name, n in counts.items() if not name.startswith('minecraft:'))
    geometry = dict(candidate='A1', stage='作者原案完整方块预览待审', nominal_size_wdh=[975, 1025, 317],
        actual_size_xyz=size, actual_size_wdh=[w, d, h], bounds=data['bounds'], blocks=len(keys),
        footprint_area=w * d, bounding_box_volume=w * d * h, actual_height=h, unique_block_types=len(np.unique(states)),
        source_component_blocks=sum(len(p.p) for p in parts), overlap_extra_memberships=sum(len(p.p) for p in parts) - len(keys),
        surface_quads=quads, material_counts=counts, non_vanilla_blocks=mod_count, non_vanilla_percent=100 * mod_count / len(keys),
        components={p.name: dict(label=p.label, blocks=len(p.p), bounds=dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist()), metadata=p.metadata) for p in parts},
        interface_rule=interface_rule, controller_blueprint=[487, 160, 260], source=source, source_notes=notes,
        appearance_approved=False, game_code_modified=False, jar_built=False, installed=False, game_verified=False)
    payload = dict(data=data, audit=dict(viewer_rendered_quads=quads, blocks=len(keys)), materials=palette, parts=packed)
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT / 'data.js').write_text('window.W09_STATIC_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
    np.savez_compressed(OUT / '原案构件数据.npz', **archive)
    export_nbt(keys, states, size, palette)
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    save(OUT / 'conflicts.json', dict(source=source, notes=notes,
        method='按构件顺序记录新构件与此前最终归属构件的零秒同格重合，多重同格时只记录最近归属；运动全周期另待净空设计。',
        reference_pose_overlap_pairs=overlaps))
    rows = ''.join('<li>' + escape(note) + '</li>' for note in notes)
    (OUT / '原文与取样.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>W09原文与取样</title><style>body{max-width:1050px;margin:40px auto;background:#171116;color:#eee;font:15px/1.8 system-ui}a{color:#e2bc6b}li{margin:14px 0}pre{white-space:pre-wrap}</style><a href="index.html">返回预览</a><h1>W09原文与完整方块取样</h1><p>实际宽深高：' + '×'.join(map(str, [w, d, h])) + '。原文SHA256：' + source['sha256'] + '</p><ol>' + rows + '</ol><details><summary>附件全文</summary><pre>' + escape(SOURCE.read_text('utf-8-sig')) + '</pre></details>', 'utf8')
    for name in ['w09_common_20261116.py', 'w09_base_20261116.py', 'w09_landscape_20261116.py', 'w09_core_20261116.py', Path(__file__).name]:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    save(OUT / 'manifest.json', dict(machine='W09', candidate='A1', status=geometry['stage'],
        updated_at=datetime.now().astimezone().isoformat(), actual_size_wdh=[w, d, h], blocks=len(keys),
        files={p.name: dict(bytes=p.stat().st_size, sha256=digest(p)) for p in OUT.iterdir() if p.is_file() and p.name != 'manifest.json'}))
    print(json.dumps(dict(size_wdh=[w, d, h], parts=len(parts), blocks=len(keys), quads=quads)), flush=True)


if __name__ == '__main__':
    main()
