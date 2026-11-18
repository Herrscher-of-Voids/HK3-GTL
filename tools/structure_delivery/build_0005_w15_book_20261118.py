import base64
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from author_w05_shapes_20261115 import Part
from package_0005_w07_noah_n1_20261118 import mesh_part
from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W15_凌虛晴树海巨书_B1_20261118'
LOG = ROOT / 'logs/0005-w15-book-b1-20261118'
BLACK, STUDS, WHITE, CLEAN, SILVER, VENT, GOLD, LIGHT, CEV = range(1, 10)
CONTROLLER = [0, 153, 404]
GROUPS = [('cover', '黑金机械书封'), ('pages', '层叠白色书页'), ('spine', '中空机械书脊'),
          ('locks', '金属包角与扣带'), ('writing', '书页铭文与规则图'), ('ribbon', '垂落金色书签')]


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def materials():
    a = json.loads((ROOT / 'deliveries/0005_W14_原生维度地貌_E3_20261118/materials.json').read_text('utf8'))
    b = json.loads((ROOT / 'deliveries/0005_W11_千律机械剧场_作者蓝图_A1_20261117/materials.json').read_text('utf8'))
    states = ['gtceu:black_metal_sheet', 'gtceu:black_studs', 'gtceu:white_metal_sheet',
              'gtceu:clean_machine_casing', 'gtceu:light_gray_metal_sheet', 'gtceu:computer_heat_vent',
              'minecraft:gold_block', 'gtceu:yellow_borderless_lamp[bloom=true,inverted=true,lit=true,powered=false]',
              'hk3gtl:voltage_machine_casing_cev']
    labels = ['深黑书封装甲', '铆接书脊骨架', '白色书页面', '洁净机械页层', '银灰页缘',
              '书脊散热格栅', '亮金封边与铭文', '金色书写光路', '冠冕金机械节点']
    result = [deepcopy(next(m for m in a + b if m['state'] == state)) for state in states]
    for m, label in zip(result, labels):
        m['label'] = label
    return result


def page_height(x, z):
    return np.rint(185 + 88 * (np.abs(x) / 520) ** .76 + 7 * (np.abs(z) / 360) ** 6).astype(np.int32)


def surface(part, x, z, y, state):
    points = np.c_[np.ravel(x), np.broadcast_to(y, np.shape(x)).ravel(), np.ravel(z)].astype(np.int32)
    part.chunks.append(points)
    part.values.append(np.broadcast_to(state, np.shape(x)).ravel().astype(np.uint8))


def clipped_grid(x0, x1, z0, z1, chamfer):
    z, x = np.mgrid[z0:z1 + 1, x0:x1 + 1]
    mask = (x - x0 + np.minimum(z - z0, z1 - z) >= chamfer) & (x1 - x + np.minimum(z - z0, z1 - z) >= chamfer)
    return x[mask], z[mask]


def cover(side):
    part = Part('cover_' + str(side), '左侧书封' if side < 0 else '右侧书封', group='cover')
    x, z = clipped_grid(16, 544, -384, 384, 24)
    xx = x * side
    y = page_height(xx, z) - 54
    for dy in range(-10, 1):
        state = np.full(len(x), BLACK, np.uint8)
        frame = (x >= 538) | (np.abs(z) >= 378)
        state[frame] = GOLD if dy >= -3 or dy <= -8 else CEV
        state[(x < 537) & (x > 529) | ((np.abs(z) < 377) & (np.abs(z) > 369))] = STUDS
        if dy == -10:
            state[((x - 22) % 92 < 3) | ((z + 384) % 128 < 3)] = CEV
        surface(part, xx, z, y + dy, state)
    for x0 in [34, 164, 294, 424, 524]:
        for z0 in [-371, 371]:
            xg, zg = np.meshgrid(np.arange(x0, x0 + 5) * side, np.arange(z0 - 2, z0 + 3))
            surface(part, xg, zg, page_height(xg, zg) - 53, SILVER)
    return part.finish()


def pages(side):
    part = Part('pages_' + str(side), '左侧叠页' if side < 0 else '右侧叠页', group='pages')
    for layer in range(12):
        edge = 516 + layer
        end = 353 + layer
        x, z = clipped_grid(17, edge, -end, end, 17)
        if layer:
            rim = (x >= edge - 14) | (np.abs(z) >= end - 14) | (x <= 36)
            x, z = x[rim], z[rim]
        xx = x * side
        top = page_height(xx, z) - layer * 4
        for depth in range(4):
            state = np.full(len(x), WHITE if depth < 3 else SILVER, np.uint8)
            if layer == 0 and depth < 3:
                state[(x % 72 == 0) & (np.abs(z) < 326)] = CLEAN
            surface(part, xx, z, top - depth, state)
    return part.finish()


def spine():
    part = Part('spine', '贯穿书脊的双侧机械轨', group='spine')
    for side in [-1, 1]:
        part.box([side * 14, 126, -400], [side * 28, 178, 400], STUDS)
        part.box([side * 11, 178, -394], [side * 23, 183, 394], CEV)
        part.box([side * 12, 184, -394], [side * 15, 185, 394], LIGHT)
        for z in range(-368, 385, 64):
            part.box([side * 15, 137, z - 12], [side * 29, 164, z + 12], VENT)
            part.box([side * 25, 146, z - 5], [side * 31, 155, z + 5], GOLD)
    for z in [-401, 401]:
        part.box([-29, 126, z - 3], [29, 177, z + 3], CEV)
        part.box([-26, 174, z - 4], [26, 180, z + 4], GOLD)
    part.points([CONTROLLER], CEV)
    return part.finish()


def locks():
    part = Part('locks', '四角金属包角及机械扣带', group='locks')
    for side in [-1, 1]:
        for sign in [-1, 1]:
            x, z = np.meshgrid(np.arange(462, 539), np.arange(310, 379))
            mask = (x > 514) | (z > 354) | (x + z > 854)
            x, z = x[mask] * side, z[mask] * sign
            for dy in range(-3, 3):
                surface(part, x, z, page_height(x, z) + dy, GOLD if dy >= 0 else CEV)
            x, z = np.meshgrid(np.arange(502, 519), np.arange(348, 363))
            x, z = x * side, z * sign
            surface(part, x, z, page_height(x, z) + 4, CEV)
        for z0 in [-224, 224]:
            x, z = np.meshgrid(np.arange(496, 551), np.arange(z0 - 12, z0 + 13))
            xx = x * side
            for dy in range(-59, 5):
                boundary = (x >= 539) | (dy < -52) | (dy >= 0)
                surface(part, xx[boundary], z[boundary], page_height(xx[boundary], z[boundary]) + dy,
                        GOLD if dy >= 0 else CEV)
            x, z = np.meshgrid(np.arange(503, 538), np.arange(z0 - 7, z0 + 8))
            x *= side
            surface(part, x, z, page_height(x, z) + 5, BLACK)
            x, z = np.meshgrid(np.arange(510, 530), np.arange(z0 - 2, z0 + 3))
            x *= side
            surface(part, x, z, page_height(x, z) + 6, LIGHT)
    return part.finish()


def mark(part, x, z, state=GOLD, height=1):
    surface(part, np.asarray(x), np.asarray(z), page_height(x, z) + height, state)


def text(part, words, left, back, scale=2):
    image = Image.new('L', (len(words) * 35, 40))
    ImageDraw.Draw(image).text((0, -2), words, font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 32), fill=255)
    zz, xx = np.nonzero(np.asarray(image) > 150)
    for dx in range(scale):
        for dz in range(scale):
            mark(part, left + xx * scale + dx, back + zz * scale + dz, GOLD)


def writing():
    part = Part('writing', '虚数之树与量子之海标题及规则铭文', group='writing')
    text(part, '虚数之树', -394, -274)
    text(part, '量子之海', 136, -274)
    glyphs = [np.array([[0,1,0,1,0],[1,0,1,0,1],[0,1,1,1,0],[0,0,1,0,0],[1,1,1,1,1],[1,0,1,0,1],[0,0,1,0,0]]),
              np.array([[1,1,1,1,1],[0,0,1,0,0],[1,0,1,0,1],[1,1,1,1,1],[0,1,0,1,0],[1,0,1,0,1],[1,1,1,1,1]]),
              np.array([[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[1,1,1,1,1],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1]])]
    for side in [-1, 1]:
        for row, z0 in enumerate([-153, -105, -57, 80, 128, 176, 224, 272]):
            for col in range(12 - row % 3):
                zz, xx = np.nonzero(glyphs[(row + col) % len(glyphs)])
                x0 = side * (93 + col * 30)
                for dx in range(2):
                    for dz in range(2):
                        mark(part, x0 + (xx * 2 + dx) * side, z0 + zz * 2 + dz, CEV)
        xs = np.arange(78, 466) * side
        for z in [-185, 42, 319]:
            mark(part, xs, np.full(len(xs), z), GOLD)
        zs = np.arange(-309, 320)
        mark(part, np.full(len(zs), 66 * side), zs, GOLD)
        mark(part, np.full(len(zs), 477 * side), zs, GOLD)
    for side in [-1, 1]:
        t = np.arange(-35, 36)
        x = side * (265 + t)
        mark(part, x, -3 + np.abs(t), GOLD)
        mark(part, x, -3 - np.abs(t), GOLD)
        for r in [7, 17]:
            zz, xx = np.mgrid[-r:r + 1, -r:r + 1]
            mask = (xx * xx + zz * zz <= r * r) & (xx * xx + zz * zz >= (r - 2) ** 2)
            mark(part, 265 * side + xx[mask], -3 + zz[mask], LIGHT)
    return part.finish()


def ribbon():
    part = Part('ribbon', '书脊垂落的金色机械书签', group='ribbon')
    path = [(26, 171, 353), (34, 170, 399), (53, 151, 431), (68, 109, 457), (64, 78, 471)]
    for a, b in zip(path[:-1], path[1:]):
        a, b = np.asarray(a), np.asarray(b)
        steps = int(np.max(np.abs(b - a))) + 1
        for p in np.rint(np.linspace(a, b, steps)).astype(int):
            part.box(p + [-10, 0, 0], p + [10, 2, 1], GOLD)
            part.box(p + [-5, 3, 0], p + [5, 3, 1], CEV)
    return part.finish()


def export_nbt(keys, states, size, palette):
    w, h, d = size
    header, _ = headers([m['state'] for m in palette], (h, d, w), len(keys))
    target = OUT / 'W15-凌虛晴树海巨书-B1.nbt'
    with gzip.open(target, 'wb', compresslevel=6) as stream:
        stream.write(header)
        for offset in range(0, len(keys), 65536):
            current = keys[offset:offset + 65536]
            raw = np.tile(np.frombuffer(RECORD, np.uint8), (len(current), 1))
            records = raw.view(RECORD_DTYPE).reshape(-1)
            records['x'], records['y'], records['z'] = current % w, current // (w * d), current // w % d
            records['state'] = states[offset:offset + 65536].astype(np.int32) - 1
            stream.write(raw.tobytes())
        stream.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')
    return dict(file=target.name, bytes=target.stat().st_size, sha256=hashlib.sha256(target.read_bytes()).hexdigest())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    palette = materials()
    save(OUT / 'materials.json', palette)
    parts = []
    for side in [-1, 1]:
        print('生成书封与叠页', side, flush=True)
        parts.extend([cover(side), pages(side)])
    parts.extend([spine(), locks(), writing(), ribbon()])
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    states = np.concatenate([p.states for p in parts])
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(states) - chosen - 1
    states, owners = states[chosen], owners[chosen]
    xyz = np.c_[keys % w, keys // (w * d), keys // w % d].astype(np.int32)
    np.savez_compressed(OUT / '完整整数格模型.npz', xyz=xyz, states=states, origin=low, size=size, owners=owners)
    del xyz, chosen
    meshes, components, quad_count = [], [], 0
    for index, part in enumerate(parts):
        selected = owners == index
        current = keys[selected]
        part.p = np.c_[current % w, current // (w * d), current // w % d].astype(np.int32) + low
        part.states = states[selected]
        mesh, count = mesh_part(part, palette)
        mesh['modelId'] = part.metadata['group']
        meshes.append(mesh)
        components.append(dict(id=part.name, group=part.metadata['group'], blocks=len(current)))
        quad_count += count
        print('合并整数格表面', part.name, count, flush=True)
    data = dict(title='凌虛晴 · 树海巨书', candidate='B1', sizeXYZ=size,
                bounds=dict(min=low.tolist(), max=high.tolist()), blocks=len(keys),
                models=[dict(id=key, label=label) for key, label in GROUPS], controller=CONTROLLER,
                effect_bounds=dict(min=[-650, 10, -490], max=[650, 650, 490]))
    payload = json.dumps(dict(data=data, materials=palette, parts=meshes), ensure_ascii=False, separators=(',', ':')).encode()
    (OUT / 'data.js').write_text('window.W15_VOXEL_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(payload)).decode()) + ';\n', 'utf8')
    nbt = export_nbt(keys, states, size, palette)
    scripts = OUT / '生成脚本'
    scripts.mkdir(exist_ok=True)
    shutil.copy2(__file__, scripts / Path(__file__).name)
    manifest = dict(machine='W15', candidate='B1', generated_at=datetime.now(timezone.utc).isoformat(), state='外观待审',
                    actual_size_wdh=[w, d, h], blocks=len(keys), components=components, surface_quads=quad_count,
                    page_titles=dict(left='虚数之树', right='量子之海'),
                    palette=[dict(state=m['state'], label=m['label'], blocks=int(np.count_nonzero(states == i + 1))) for i, m in enumerate(palette)],
                    controller=dict(source=CONTROLLER, normalized=(np.array(CONTROLLER) - low).tolist(), facing='south',
                                    policy='唯一主控候选，其余实体格可自由替换合法通用接口'),
                    effects='金色虚数之树与世界叶片、蓝紫量子海、页内书写光带；网页演示，不计入实体NBT',
                    design='以悬空展开的巨书表达凌虛晴重建树海的设定，为本项目新创作的象征',
                    entities=0, nbt=nbt, appearance_approved=False, game_code_modified=False, jar_built=False, installed=False)
    save(OUT / 'manifest.json', manifest)
    save(LOG / 'generation.json', dict(output=str(OUT), size_wdh=[w, d, h], blocks=len(keys), quads=quad_count, nbt=nbt))
    print(json.dumps(dict(output=str(OUT), size_wdh=[w, d, h], blocks=len(keys), quads=quad_count)))


if __name__ == '__main__':
    main()
