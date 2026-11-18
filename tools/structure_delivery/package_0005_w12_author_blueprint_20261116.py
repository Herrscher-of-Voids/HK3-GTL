import base64
from copy import copy
from datetime import datetime
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
from zipfile import ZipFile

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w05_author_blueprint_20261115 import mesh_part as strip_mesh
import w12_base_20261116 as base
import w12_frame_20261116 as frame
import w12_core_20261116 as core
from w12_common_20261116 import CX, CZ, wall_z


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W12_作者蓝图原案_A1_20261116'
LOG = ROOT / 'logs/0005-w12-author-blueprint-a1-20261116'
SOURCE = Path('C:/Users/OWNER/下載/W12 约束之律者·戒律·全域能量约束壁 - 多方块结构建造与渲染设计规范.md')


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            sha.update(block)
    return sha.hexdigest()


def make_materials():
    cached = ROOT / 'deliveries/0005_W10_引力奇点刑架_净空修订_A3_20261116/materials.json'
    materials = json.loads(cached.read_text('utf8'))
    labels = ['纯黑绝缘底色', '格雷黑色铆钉装甲', '黄金约束骨架', '格雷洁净白机壳', '琥珀冷却介质',
              '格雷圣金无框工业灯', '紫罗兰能量玻璃', '琥珀防爆透光地板', '深色散热鳍片',
              '黑金机械镶边', '血色十字屏障', '格雷白色工业灯', '本模组黑色重机壳']
    for material, label in zip(materials, labels):
        material.update(label=label, role=label, texture_source=str(cached.relative_to(ROOT)))
    jar = Path('E:/Prism/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar')
    with ZipFile(jar) as archive:
        png = archive.read('assets/minecraft/textures/block/redstone_block.png')
    materials.append(dict(state='minecraft:redstone_block', label='唯一主控定位标记', role='预览主控定位',
        faces={face: 'data:image/png;base64,' + base64.b64encode(png).decode() for face in ('east', 'west', 'south', 'north', 'down', 'up')},
        transparent=False, emissive=False, source=dict(archive=str(jar), png_sha256=hashlib.sha256(png).hexdigest())))
    save(OUT / 'materials.json', materials)
    return materials


def mesh_part(part, materials):
    item, _, _ = strip_mesh(part, materials)
    item['spans'] = [[[] for _ in range(6)] for _ in materials]
    w, _, d = item['size']
    quads = 0
    for material in range(len(materials)):
        for face in range(6):
            starts = np.array(item['starts'][material][face], np.int64)
            if not len(starts):
                continue
            lengths = np.array(item['lengths'][material][face])
            x, y, z = starts % w, starts // (w * d), starts // w % d
            plane, row, column = (x, y, z) if face < 2 else (z, y, x) if face < 4 else (y, z, x)
            order = np.lexsort((row, lengths, column, plane))
            plane, row, column, lengths, starts = [a[order] for a in (plane, row, column, lengths, starts)]
            breaks = np.r_[True, (plane[1:] != plane[:-1]) | (column[1:] != column[:-1]) |
                           (lengths[1:] != lengths[:-1]) | (row[1:] != row[:-1] + 1)]
            first = np.flatnonzero(breaks)
            item['starts'][material][face] = starts[first].tolist()
            item['lengths'][material][face] = lengths[first].tolist()
            item['spans'][material][face] = np.diff(np.r_[first, len(starts)]).tolist()
            quads += len(first)
    return item, quads


def export_nbt(keys, states, size, materials):
    w, h, d = size
    header, _ = headers([m['state'] for m in materials], (h, d, w), len(keys))
    record = np.frombuffer(RECORD, np.uint8)
    with gzip.open(OUT / 'W12-全域能量约束壁-A1.nbt', 'wb', compresslevel=6) as handle:
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
    materials = make_materials()
    parts, notes = [], []
    for module in (base, frame, core):
        current, sampling = module.build()
        parts.extend(current)
        notes.extend(sampling)
        print(f'{module.__name__}: {len(current)}构件，{sum(len(p.p) for p in current):,}构件占格', flush=True)
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    all_states = np.concatenate([p.states for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(all_states) - chosen - 1
    states = all_states[chosen]
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])[chosen]
    del all_states, chosen
    archive, packed, quads = {}, [], 0
    for index, part in enumerate(parts):
        archive[part.name + '_xyz'], archive[part.name + '_materials'] = part.p, part.states
        current = keys[owners == index]
        visible = copy(part)
        visible.p = np.c_[current % w, current // (w * d), current // w % d].astype(np.int32) + low
        visible.states = states[owners == index]
        item, count = mesh_part(visible, materials)
        item['source_blocks'] = len(part.p)
        packed.append(item)
        quads += count
        print(f'表面 {index + 1}/{len(parts)} {part.name} {count:,}', flush=True)
    views = {
        'front': dict(label='整体前斜视', direction=[-.85, .74, -1.2]),
        'back': dict(label='整体后斜视', direction=[.85, .74, 1.2]),
        'frontOrtho': dict(label='正面', direction=[0, .001, -1]),
        'side': dict(label='侧面', direction=[1, .001, 0]),
        'top': dict(label='俯视', direction=[0, 1, .001]),
        'ground': dict(label='主控台仰视', direction=[0, .08, -1], center=[531, 168, 430], half=[285, 175, 310]),
        'core': dict(label='三重十字与白洞', direction=[-.8, .48, -1.2], center=[531, 180, 423], half=[125, 135, 125]),
        'chains': dict(label='实体穿扣锁链', direction=[-.8, .7, -1.1], center=[350, 220, 290], half=[180, 90, 150]),
        'wall': dict(label='管风琴与十字花窗', direction=[-.45, .3, -1], center=[331, 158, wall_z(331, -1)], half=[150, 125, 65]),
        'wings': dict(label='双翼加速长廊', direction=[-.8, .65, -1], center=[275, 120, 423], half=[315, 110, 110]),
        'base': dict(label='深井与散热阵列', direction=[-.75, 1.15, -1], center=[531, 40, 423], half=[540, 70, 435]),
        'crown': dict(label='戒律光环与垂丝', direction=[-.65, .65, -1], center=[531, 288, 423], half=[395, 98, 395]),
        'controller': dict(label='唯一主控位置', direction=[-.6, .8, -1], center=[531, 50, 10], half=[26, 16, 30]),
        'blocks': dict(label='原生像素近景', direction=[-.65, .7, -1], center=[531, 48, 15], half=[7, 6, 7]),
    }
    interface_rule = '仅主控固定，其余全部实体方块可随时替换合法通用接口，位置与朝向由玩家选择。'
    notes.extend([
        '本轮以W12附件为依据；消息正文为旧W08薪炎方案，不用于本稿几何。附件逐字节归档为原文.txt。',
        '机械圣堂采用约束、犹大与阿波尼亚混合美术参考；文档中的角色归属作为作者设计描述保存。',
        'Y0至327的整数端点共有328层，名义327高与实际完整包围盒分别记录。1063×847的名义占地900361格，比已批准W10的949×949少240格；本轮保留作者尺寸，规模递增待修订。',
        '原文主控坐标(531,50,10)保留；该侧通常是Minecraft的负Z侧，原文将其称南侧的方向命名差异保留说明。红石块仅为唯一主控预览定位。',
        '原文长廊固定输入输出仓要求由负责人通用接口规则覆盖；除主控外没有指定接口位置。',
        '独立构件按基座、外围、核心顺序生成。NBT同格后写覆盖，NPZ保留每件完整原始占格；网页按相同覆盖结果分组，避免重叠表面闪烁。原案连接与交叠未私自移位消解。',
        '所有实体由整数格及原生像素贴图构成。网页蜂窝波、墙束、蝴蝶、托举光束为独立动态演示，NBT保存完整静态实体。',
        '沿用已注册运行身份w12_global_energy_constraint_wall、CIV、RN-ECB；本轮为外观预览，未修改正式蓝图、配方或电压。',
    ])
    beam_origins = [[x, 177, wall_z(x, side)] for side in (-1, 1) for x in range(131, 981, 100)]
    towers = [[x, 327, wall_z(x, side)] for side in (-1, 1) for x in (81, 381, 681, 980)]
    data = dict(machine_id='W12', title='约束之律者·戒律·全域能量约束壁', candidate='A1', sizeXYZ=size, size=size,
        bounds=dict(min=low.tolist(), max=high.tolist()), blueprint_to_export_offset_xyz=(-low).tolist(),
        nominal_size_wdh=[1063, 847, 327], core_center=[531, 180, 423], views=views,
        interface_rule=interface_rule, controller_blueprint=[531, 50, 10], controller_status='原文坐标预览定位',
        runtime_voltage='CIV', research='RN-ECB', effects=dict(beam_origins=beam_origins, tower_origins=towers))
    counts = {m['state']: int((states == i + 1).sum()) for i, m in enumerate(materials)}
    mod_count = sum(v for k, v in counts.items() if not k.startswith('minecraft:'))
    geometry = dict(candidate='A1', stage='作者原案完整方块预览待审', nominal_size_wdh=[1063, 847, 327],
        actual_size_xyz=size, actual_size_wdh=[w, d, h], bounds=data['bounds'], blocks=len(keys),
        footprint_area=w * d, bounding_box_volume=w * d * h, actual_height=h, unique_block_types=len(np.unique(states)),
        source_component_blocks=sum(len(p.p) for p in parts), overlap_extra_memberships=sum(len(p.p) for p in parts) - len(keys),
        surface_quads=quads, material_counts=counts, non_vanilla_blocks=mod_count, non_vanilla_percent=100 * mod_count / len(keys),
        components={p.name: dict(label=p.label, blocks=len(p.p), bounds=dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist()), metadata=p.metadata) for p in parts},
        interface_rule=interface_rule, controller_blueprint=[531, 50, 10], source=source, source_notes=notes,
        instance_access=False, appearance_approved=False, game_code_modified=False, jar_built=False, game_verified=False)
    config = dict(data=data, audit=dict(viewer_rendered_quads=quads, blocks=len(keys)), materials=materials, parts=packed)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT / 'data.js').write_text('window.W12_STATIC_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
    np.savez_compressed(OUT / '原案构件数据.npz', **archive)
    export_nbt(keys, states, size, materials)
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    save(OUT / 'conflicts.json', dict(source=source, notes=notes))
    rows = ''.join('<li>' + escape(note) + '</li>' for note in notes)
    (OUT / '原文与取样.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>W12原文与取样</title><style>body{max-width:1050px;margin:40px auto;background:#13151c;color:#eee;font:15px/1.8 system-ui}a{color:#e2bc6b}li{margin:14px 0}pre{white-space:pre-wrap}</style><a href="index.html">返回预览</a><h1>W12原文与完整方块取样</h1><p>实际宽深高：' + '×'.join(map(str, [w, d, h])) + '。原文SHA256：' + source['sha256'] + '</p><ol>' + rows + '</ol><details><summary>附件全文</summary><pre>' + escape(SOURCE.read_text('utf-8-sig')) + '</pre></details>', 'utf8')
    for name in ['w12_common_20261116.py', 'w12_base_20261116.py', 'w12_frame_20261116.py', 'w12_core_20261116.py', Path(__file__).name]:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    files = ['data.js', 'materials.json', 'geometry.json', 'conflicts.json', '原文.txt', '原案构件数据.npz', 'W12-全域能量约束壁-A1.nbt']
    save(OUT / 'manifest.json', dict(machine='W12', candidate='A1', status='完整方块预览与NBT，外观待审',
        updated_at=datetime.now().astimezone().isoformat(), actual_size_wdh=[w, d, h], blocks=len(keys),
        files={name: dict(bytes=(OUT / name).stat().st_size, sha256=digest(OUT / name)) for name in files}))
    print(json.dumps(dict(size_wdh=[w, d, h], parts=len(parts), blocks=len(keys), quads=quads)), flush=True)


if __name__ == '__main__':
    main()
