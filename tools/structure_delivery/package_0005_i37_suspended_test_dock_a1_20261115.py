from copy import deepcopy
from datetime import datetime
from html import escape
from pathlib import Path
import base64
import gzip
import hashlib
import json
import re
import shutil
import struct

import numpy as np

import geometry_0005_i37_suspended_test_dock_a1_20261115 as geometry
from material_resources import Resources


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_I37_世界维系试验平台_悬箱稳界试验坞_A1_20261115'
LOG = ROOT / 'logs/0005-i37-suspended-test-dock-a1-20261115'
SOURCE = ROOT / 'deliveries/0005_W04_七雷取能天枢_构图A3_20261114'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
CLIENT = Path('C:/Users/OWNER/.gradle/caches/fabric-loom/1.20.1/minecraft-client.jar')
VIEWS = [('front', '前左全景', '整体预览.png'), ('right', '前右全景', '前右预览.png'),
         ('orthofront', '正面', '正面预览.png'), ('side', '侧面', '侧面预览.png'),
         ('back', '背面', '背面预览.png'), ('top', '俯视', '俯视预览.png'),
         ('inside', '逐层剖切', '逐层剖切.png'), ('core', '悬箱与样件', '中心试验箱.png'),
         ('controller', '主控位置', '主控近景.png')]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def string(value):
    raw = value.encode('utf8')
    return struct.pack('>H', len(raw)) + raw


def tag(kind, name):
    return bytes([kind]) + string(name)


def integer(name, value):
    return tag(3, name) + struct.pack('>i', value)


def listint(name, values):
    return tag(9, name) + b'\x03' + struct.pack('>i', len(values)) + struct.pack('>' + 'i' * len(values), *values)


def palette_nbt(state):
    name, _, properties = state.partition('[')
    result = tag(8, 'Name') + string(name)
    if properties:
        result += tag(10, 'Properties')
        for item in properties[:-1].split(','):
            key, value = item.split('=')
            result += tag(8, key) + string(value)
        result += b'\x00'
    return result + b'\x00'


def headers(states, shape, count):
    h, d, w = shape
    nbt = tag(10, '') + integer('DataVersion', 3465) + listint('size', [w, h, d])
    nbt += tag(9, 'palette') + b'\x0a' + struct.pack('>i', len(states))
    nbt += b''.join(palette_nbt(state) for state in states)
    nbt += tag(9, 'blocks') + b'\x0a' + struct.pack('>i', count)
    schem = tag(10, 'Schematic') + integer('Version', 2) + integer('DataVersion', 3465)
    for key, value in zip(('Width', 'Height', 'Length'), (w, h, d)):
        schem += tag(2, key) + struct.pack('>h', value)
    schem += tag(11, 'Offset') + struct.pack('>i3i', 3, 0, 0, 0)
    schem += integer('PaletteMax', len(states) + 1) + tag(10, 'Palette') + integer('minecraft:air', 0)
    schem += b''.join(integer(state, index) for index, state in enumerate(states, 1))
    schem += b'\x00' + tag(7, 'BlockData') + struct.pack('>i', w * h * d)
    return nbt, schem


RECORD = listint('pos', [0, 0, 0]) + integer('state', 0) + b'\x00'
RECORD_DTYPE = np.dtype(dict(names=['x', 'y', 'z', 'state'], formats=['>i4'] * 4,
                            offsets=[11, 15, 19, 31], itemsize=36))


def export(cube, states, name, count):
    h, d, w = cube.shape
    flat = cube.ravel()
    nbt_header, schem_header = headers(states, cube.shape, count)
    record = np.frombuffer(RECORD, np.uint8)
    with gzip.open(OUT / (name + '.nbt'), 'wb', compresslevel=6) as handle:
        handle.write(nbt_header)
        for offset in range(0, flat.size, 1048576):
            indices = np.flatnonzero(flat[offset:offset + 1048576]) + offset
            for start in range(0, len(indices), 65536):
                current = indices[start:start + 65536]
                raw = np.tile(record, (len(current), 1))
                rows = raw.view(RECORD_DTYPE).reshape(-1)
                rows['x'] = current % w
                rows['y'] = current // (w * d)
                rows['z'] = current // w % d
                rows['state'] = flat[current].astype(np.int32) - 1
                handle.write(raw.tobytes())
        handle.write(tag(9, 'entities') + b'\x0a' + struct.pack('>i', 0) + b'\x00')
    with gzip.open(OUT / (name + '.schem'), 'wb', compresslevel=6) as handle:
        handle.write(schem_header)
        for start in range(0, flat.size, 1048576):
            handle.write(flat[start:start + 1048576].tobytes())
        handle.write(b'\x00')
    return {ext: dict(file=name + '.' + ext, bytes=(OUT / (name + '.' + ext)).stat().st_size,
                     sha256=hashlib.sha256((OUT / (name + '.' + ext)).read_bytes()).hexdigest())
            for ext in ('nbt', 'schem')}


def bounds(mask):
    x = np.flatnonzero(mask.any(axis=(0, 1)))
    y = np.flatnonzero(mask.any(axis=(1, 2)))
    z = np.flatnonzero(mask.any(axis=(0, 2)))
    return [int(x[0]), int(y[0]), int(z[0])], [int(x[-1]), int(y[-1]), int(z[-1])]


def runs(values, size, face):
    w, _, d = size
    y = values // (w * d)
    z = values // w % d
    x = values % w
    if face < 2:
        order = np.lexsort((z, x, y))
        values, x, y, z = values[order], x[order], y[order], z[order]
        boundary = np.r_[True, (y[1:] != y[:-1]) | (x[1:] != x[:-1]) | (z[1:] != z[:-1] + 1)]
    else:
        boundary = np.r_[True, (y[1:] != y[:-1]) | (z[1:] != z[:-1]) | (x[1:] != x[:-1] + 1)]
    first = np.flatnonzero(boundary)
    starts = values[first]
    lengths = np.diff(np.r_[first, len(values)])
    order = np.argsort(starts)
    return starts[order].tolist(), lengths[order].tolist()


def preview_parts(cube, owners, materials):
    h, d, w = cube.shape
    count = len(materials)
    occupied = cube != 0
    parts = []
    for index, item in enumerate(geometry.PARTS, 1):
        owned = (owners == index) & occupied
        low, high = bounds(owned)
        parts.append(dict(id=item['id'], label=item['name'], asset=item['id'], origin=low,
                          size=[b - a + 1 for a, b in zip(low, high)], blocks=int(owned.sum()),
                          starts=[[[] for _ in range(6)] for _ in materials],
                          lengths=[[[] for _ in range(6)] for _ in materials]))
        del owned
    transparent = np.array([False, *[bool(item['transparent']) for item in materials]])
    glass = transparent[cube]
    flat, owner_flat = cube.ravel(), owners.ravel()
    faces = quads = 0
    for face, axis, sign in [(0, 2, 1), (1, 2, -1), (2, 1, 1), (3, 1, -1), (4, 0, -1), (5, 0, 1)]:
        neighbor = np.zeros_like(cube)
        destination, source = [slice(None)] * 3, [slice(None)] * 3
        destination[axis], source[axis] = ((slice(None, -1), slice(1, None)) if sign > 0
                                         else (slice(1, None), slice(None, -1)))
        neighbor[tuple(destination)] = cube[tuple(source)]
        exposed = occupied & ((neighbor == 0) | (transparent[neighbor] & ~glass))
        indices = np.flatnonzero(exposed.ravel())
        del neighbor, exposed
        keys = (owner_flat[indices].astype(np.int32) - 1) * count + flat[indices].astype(np.int32) - 1
        order = np.argsort(keys, kind='stable')
        keys, indices = keys[order], indices[order]
        breaks = np.r_[0, np.flatnonzero(keys[1:] != keys[:-1]) + 1, len(keys)]
        for start, end in zip(breaks[:-1], breaks[1:]):
            part_index, material = divmod(int(keys[start]), count)
            part = parts[part_index]
            origin = part['origin']
            values = indices[start:end]
            x = values % w - origin[0]
            y = values // (w * d) - origin[1]
            z = values // w % d - origin[2]
            local = (y * part['size'][2] + z) * part['size'][0] + x
            starts, lengths = runs(local, part['size'], face)
            part['starts'][material][face] = starts
            part['lengths'][material][face] = lengths
            quads += len(starts)
        faces += len(indices)
        print('表面压缩', face, len(indices), quads, flush=True)
    return parts, faces, quads


def install_viewer(data, parts, materials, counts, quads):
    core = (SOURCE / '生成脚本/viewer.mjs').read_text('utf8').split('/* W04统一评审界面适配开始 */', 1)[0]
    core = core.replace('W04', 'I37')
    core = core.replace("new THREE.Vector3(-1,.7,1.25)", "new THREE.Vector3(-1,.7,-1.25)")
    core = core.replace("direction.set(0,0,1)", "direction.set(0,0,-1)")
    core = core.replace("direction.set(0,.15,-1)", "direction.set(0,.15,1)")
    core = core.replace("direction.set(0,.2,1)", "direction.set(0,.2,-1)")
    core = core.replace("controls.target.copy(target);camera.up.set", "if(detail?.position)direction.set(...detail.position).sub(new THREE.Vector3(...detail.center));\n    controls.target.copy(target);camera.up.set")
    core = core.replace("  if(renderedQuads!==audit.viewer_rendered_quads)throw new Error('完整表面数量不同');\n", '')
    adapter = (ROOT / 'tools/structure_delivery/w04_review_ui_20261110.mjs').read_text('utf8').replace('W04', 'I37')
    names = 'const names=' + json.dumps({key: label for key, label, _ in VIEWS}, ensure_ascii=False) + ';'
    adapter = re.sub(r'const names=\{.*?\};', lambda _: names, adapter, count=1, flags=re.S)
    adapter = adapter.replace("原评审界面 · 整机真实方块 · 全静态", "I37独立外观候选 · 真实方块 · 全静态")
    (OUT / '生成脚本/viewer.mjs').write_text(core + '\n' + adapter, 'utf8')
    metadata = dict(candidate=data['title'], source_voxels=sum(counts.values()),
                    whole_integer_voxel=True, materials=[dict(state=s, count=n, label=geometry.NAMES[s])
                                                        for s, n in counts.items()],
                    scope='分组、预览和完整结构文件共用同一整数格几何；红石块只标示主控位置。')
    save(OUT / 'review-ui.json', metadata)
    return metadata


def pages(data, parts, metadata, manifest):
    css = re.search(r'<style>(.*?)</style>', (SOURCE / '三维布局.html').read_text('utf8'), re.S)[1]
    title = escape(data['title'])
    w, h, d = data['size']
    buttons = ''.join(f'<button data-view="{key}">{label}</button>' for key, label, _ in VIEWS)
    part_rows = ''.join(f'<label class="asset-row"><input type="checkbox" checked data-part="{escape(p["id"])}">{escape(p["label"])} · {p["blocks"]:,}块</label>' for p in parts)
    material_rows = ''.join(f'<p><b>{escape(geometry.NAMES[s])}</b>：{escape(geometry.ROLES[s])}</p>' for s in manifest['material_counts'])
    meta_json = json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c')
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 三维评审</title><style>{css}</style>
<header><a href="index.html">← 候选总览</a><h1>{title}</h1><div>0005 · WFV · {w}×{d}×{h}（宽×深×高） · {manifest['block_count']:,}方块 · {manifest['material_count']}种现存材料</div></header>
<main class="review"><section id="stage"><div id="loading">加载完整静态构件与真实方块材质…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">以悬吊试件箱、双态样件、连续承力架和多向加载头组成世界维系试验坞。全部为整数格真实方块，当前只评审建筑外观。</div>
<div class="locator"><b>主控位置 {data['controller']}</b><p>红石块是主控位置标记；通用接口和正式Pattern未接入。</p><button data-view="controller">定位主控</button><label><input id="ports" type="checkbox">主控定位框</label></div>
<div>{buttons}</div><p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 Y=<b id="layerValue">{h}</b><output id="layerLabel">{h}</output><input id="layer" type="range" min="0" max="{h}" value="{h}"></label>
<label><input id="glass" type="checkbox" checked>显示玻璃</label><label><input id="showGrid" type="checkbox">参考网格</label><p><button id="reset">复位全景</button><button id="saveImage">保存视角</button><button id="fullscreen">全屏查看</button></p><p id="counts"></p><p id="stats"></p><p id="status"></p>
<details open><summary>构件分组</summary>{part_rows}</details><details><summary>真实材料筛选</summary><p id="materialCounts"></p><input id="materialSearch" type="search" placeholder="材料名或方块ID"><div id="materials"></div></details>
<details><summary>材料用途</summary>{material_rows}</details><details><summary>候选状态与文件</summary><p>{escape(metadata['scope'])}</p><p>外观未批准，未接入Pattern，未构建或安装JAR，未启动游戏或执行成型、运行验收；不增加验收分。剖切和隐藏材料不补画新的内部切面。</p><p><a href="{data['name']}.nbt">完整NBT</a> · <a href="{data['name']}.schem">完整Schematic</a> · <a href="材料清单.json">材料与用途</a> · <a href="材质来源.json">真实材质来源</a> · <a href="manifest.json">坐标与生成记录</a></p></details>
</aside></main><script id="reviewMetadata" type="application/json">{meta_json}</script><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''
    (OUT / '三维评审.html').write_text(page, 'utf8')
    gallery = ''.join(f'<figure><img src="{file}" alt="{label}"><figcaption>{label}</figcaption></figure>' for _, label, file in VIEWS)
    index = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{max-width:1500px;margin:30px auto;padding:0 22px;background:#121b2b;color:#e3edf5;font:16px/1.8 "Microsoft YaHei",sans-serif}}a{{color:#a9d3f0}}img{{width:100%}}.note{{padding:15px;border-left:3px solid #a49dc9;background:#263143}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}figure{{margin:0}}figcaption{{padding:7px}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}}}</style>
<p>0005 多方块设计 · I37 · WFV · 独立外观候选</p><h1>{title}</h1><p class="note">宽{w}×深{d}×高{h}格 · {manifest['block_count']:,}个方块 · {manifest['material_count']}种现存材料 · {len(parts)}个可独立显隐构件。</p>
<p><a href="三维评审.html">打开统一三维评审 →</a> · <a href="材料清单.json">真实材料与用途</a> · <a href="manifest.json">完整设计记录</a> · <a href="材质来源.json">材质来源</a></p>
<img src="整体预览.png" alt="悬箱稳界试验坞完整预览"><p>中央试件箱由双门承力加载架悬持；前后加载头与四组侧向加载器围绕参考态、扰动态样件布置，上置扫描桥负责测量表达，后侧独立布置介质调理和电源机组。床身、焊接箱梁、检修廊及主控台共同构成完整工业机体。</p>
<p class="note">本稿未获外观批准，未接入正式Pattern，未构建、安装或启动游戏。红石块仅为主控位置标记；静态构图、导出和截图不代替成型、运行或游戏性能验收，不增加验收分。</p><div class="grid">{gallery}</div>
<p><a href="{data['name']}.nbt">完整NBT</a> · <a href="{data['name']}.schem">完整Schematic</a> · <a href="review-ui.json">分组与材质元数据</a></p></html>'''
    (OUT / 'index.html').write_text(index, 'utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    cube, owners, original_data = geometry.build()
    data = deepcopy(original_data)
    h, d, w = cube.shape
    data['size'] = [w, h, d]
    low, high = bounds(cube != 0)
    tally = np.zeros(len(geometry.STATES) + 1, np.int64)
    for layer in cube:
        tally += np.bincount(layer.ravel(), minlength=len(tally))
    counts = {state: int(tally[index]) for index, state in enumerate(geometry.STATES, 1)}
    block_count = int(tally[1:].sum())
    print('导出完整结构', [w, h, d], block_count, flush=True)
    files = export(cube, geometry.STATES, data['name'], block_count)
    resources = Resources(instance=INSTANCE, client=CLIENT, project_resources=ROOT / 'src/main/resources')
    materials = [resources.material(state) for state in geometry.STATES]
    save(OUT / '材质来源.json', dict(instance=str(INSTANCE), client=str(CLIENT),
        project_resources='src/main/resources', resources=resources.sources,
        rendering='直接解析现有方块状态、父模型与六面PNG；动画贴图使用静态首帧。'))
    resources.close()
    parts, faces, quads = preview_parts(cube, owners, materials)
    details = {}
    zone = original_data['zones'][0]
    for item in original_data['detail_views']:
        details[item['id']] = dict(center=item['target'], position=item['position'],
                                  half=[max(abs(item['target'][i] - zone['min'][i]), abs(zone['max'][i] - item['target'][i])) * 1.12 for i in range(3)])
    details['core'].update(position=[520, 225, 340], half=[170, 115, 150])
    details['controller'] = dict(center=data['controller'], half=[48, 32, 38])
    data.update(blueprint_to_export_offset_xyz=[0, 0, 0],
                center_blueprint=[(low[i] + high[i]) / 2 for i in range(3)], detail_views=details)
    payload = dict(data=data, audit=dict(viewer_rendered_quads=quads), materials=materials, parts=parts)
    packed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6, mtime=0)
    (OUT / 'data.js').write_text('window.I37_STATIC_PAYLOAD=' + json.dumps(base64.b64encode(packed).decode()) + ';', 'utf8')
    manifest = dict(title=data['title'], name=data['name'], candidate='A1', machine='I37', target_voltage='WFV',
                    conversation='0005', conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
                    created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
                    size_xyz=[w, h, d], size_wdh=[w, d, h], occupied_bounds_xyz=dict(min=low, max=high),
                    occupied_size_xyz=[high[i] - low[i] + 1 for i in range(3)],
                    geometry_array_preserved=True, nominal_clipping=False, block_count=block_count,
                    material_count=int((tally[1:] > 0).sum()), material_counts=counts,
                    components=[{key: p[key] for key in ('id', 'label', 'origin', 'size', 'blocks')} for p in parts],
                    controller=data['controller'], controller_face=data['controller_face'],
                    controller_marker='minecraft:redstone_block', ports=data['ports'], zones=data['zones'],
                    detail_views=details, source_geometry=str(Path(geometry.__file__).relative_to(ROOT)).replace('\\', '/'),
                    files=files, preview=dict(unit_faces=faces, merged_quads=quads, payload_gzip_bytes=len(packed),
                                             static=True, real_block_textures=True),
                    appearance_approved=False, pattern_implemented=False, jar_built=False, installed=False,
                    game_started=False, game_verified=False, automated_tests_run=False, acceptance_score_changed=False)
    save(OUT / 'manifest.json', manifest)
    save(OUT / '材料清单.json', [dict(state=s, name=geometry.NAMES[s], role=geometry.ROLES[s], count=n) for s, n in counts.items()])
    metadata = install_viewer(data, parts, materials, counts, quads)
    pages(data, parts, metadata, manifest)
    shutil.copy2(Path('C:/Users/OWNER/.codex/skills/minecraft-builder-skill/node_modules/three/LICENSE'), OUT / 'Three许可.txt')
    for source in (Path(__file__), Path(geometry.__file__)):
        shutil.copy2(source, OUT / '生成脚本' / source.name)
    save(LOG / 'generation.json', manifest)
    print(json.dumps(dict(output=str(OUT), size_wdh=[w, d, h], blocks=block_count, materials=manifest['material_count'],
                          parts=len(parts), merged_quads=quads), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
