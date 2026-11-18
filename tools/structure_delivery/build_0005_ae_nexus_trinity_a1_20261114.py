from collections import Counter
from datetime import datetime
from pathlib import Path
import base64
import gzip
import hashlib
import json
import re
import shutil

import nbtlib as nbt
import numpy as np
from material_resources import Resources

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_万象天枢_三位一体取形_A1_20261114'
LOG = ROOT / 'logs/0005-ae-nexus-appearance-20261114'
SHARED = ROOT / 'deliveries/I39_无人跨界航路中继站_偏馈碟阵与双轨整备站_V1_20261027/i39'
TITLE = '万象天枢 · 三位一体取形 A1'
STEM = '0005-ae-nexus-trinity-a1'
W, H, D = 35, 33, 35
STATES = ['ae2:sky_stone_block', 'minecraft:smooth_quartz', 'ae2:fluix_block',
          'gtceu:computer_casing', 'gtceu:computer_heat_vent',
          'hk3gtl:casing_colored_purple', 'hk3gtl:casing_colored_cyan',
          'hk3gtl:glass_honkai_stabilized', 'minecraft:sea_lantern', 'hk3gtl:ae_nexus']
NAMES = dict(zip(STATES, ['陨石', '平滑石英块', '福鲁伊克斯块', '计算机机壳', '计算机散热口',
                         '紫色机壳', '青色机壳', '稳定崩坏能玻璃', '海晶灯', '万象天枢主控']))
STONE, WHITE, FLUIX, CASE, VENT, PURPLE, CYAN, GLASS, LIGHT, CONTROL = range(1, 11)
CONTROLLER = [17, 3, 2]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def geometry():
    a = np.zeros((H, D, W), np.uint8)
    y, z, x = np.indices(a.shape)

    def box(lo, hi, material):
        xx, yy, zz = lo
        X, Y, Z = hi
        a[yy:Y + 1, zz:Z + 1, xx:X + 1] = material

    def line(p, q, radius, material):
        for t in np.linspace(0, 1, int(np.linalg.norm(np.array(q) - p) * 3) + 1):
            xx, yy, zz = np.rint(np.array(p) * (1 - t) + np.array(q) * t).astype(int)
            box((xx - radius, yy - radius, zz - radius), (xx + radius, yy + radius, zz + radius), material)

    def cabinet(lo, hi, side):
        xx, yy, zz = lo
        X, Y, Z = hi
        box(lo, hi, CASE)
        box((xx + 1, yy + 1, zz + 1), (X - 1, Y - 1, Z - 1), 0)
        for xx2 in (xx, X):
            box((xx2, yy, zz), (xx2, Y, zz), WHITE)
            box((xx2, yy, Z), (xx2, Y, Z), WHITE)
        box((xx, Y, zz), (X, Y, Z), WHITE)
        box((xx + 1, yy + 1, zz), (X - 1, Y - 1, zz), GLASS)
        for yy2 in range(yy + 1, Y, 2):
            box((xx + 1, yy2, zz + 2), (X - 1, yy2, Z - 1), FLUIX if side == 'storage' else CYAN)
        face = xx if side == 'storage' else X
        box((face, yy + 1, zz + 2), (face, Y - 1, Z - 2), VENT)
        box((xx, yy, zz), (X, yy, zz), PURPLE)

    base = np.abs(x - 17) + np.abs(z - 17) <= 28
    a[base & (y <= 1)] = STONE
    a[base & (y == 1) & ((x == 0) | (x == 34) | (z == 0) | (z == 34) |
       (np.abs(x - 17) + np.abs(z - 17) == 28))] = WHITE
    for xx in (10, 24):
        box((xx, 1, 5), (xx, 1, 29), FLUIX)
    box((5, 1, 9), (29, 1, 9), PURPLE)
    box((5, 1, 26), (29, 1, 26), PURPLE)
    for xx, zz in ((7, 7), (27, 7), (7, 27), (27, 27)):
        box((xx, 1, zz), (xx, 1, zz), LIGHT)

    cabinet((2, 2, 13), (7, 9, 24), 'storage')
    cabinet((27, 2, 13), (32, 9, 24), 'compute')
    box((3, 10, 15), (6, 10, 22), PURPLE)
    for zz in (15, 18, 21):
        box((28, 10, zz), (31, 10, zz + 1), VENT)
    box((11, 2, 28), (23, 7, 32), CASE)
    box((12, 3, 29), (22, 6, 31), 0)
    for xx in (11, 23):
        box((xx, 2, 28), (xx, 7, 32), WHITE)
    box((12, 3, 28), (22, 6, 28), GLASS)
    box((12, 3, 32), (22, 6, 32), GLASS)
    box((12, 7, 28), (22, 7, 32), WHITE)
    for xx in (13, 17, 21):
        box((xx, 3, 30), (xx, 5, 30), CYAN)
        box((xx - 1, 6, 30), (xx + 1, 6, 30), FLUIX)

    box((11, 2, 12), (23, 3, 24), WHITE)
    box((12, 4, 13), (22, 5, 23), PURPLE)
    box((14, 6, 15), (20, 6, 21), CASE)
    for xx in (12, 22):
        line((xx, 5, 13), (xx, 10, 16), 0, WHITE)
        line((xx, 5, 23), (xx, 10, 20), 0, WHITE)
    collar = np.maximum(np.abs(x - 17), np.abs(z - 18))
    a[(y == 10) & (collar == 5) & (np.abs(x - 17) + np.abs(z - 18) <= 8)] = WHITE
    a[(y == 10) & (collar == 4)] = FLUIX

    dx, dy, dz = x - 17, y - 18, z - 18
    main_radius = np.sqrt(dx * dx + dy * dy)
    a[(np.abs(main_radius - 13) < .72) & (np.abs(dz) <= 1)] = PURPLE
    a[(np.abs(main_radius - 13) < .72) & (dz == -1)] = FLUIX
    u, v = (dx + dz) / np.sqrt(2), (dx - dz) / np.sqrt(2)
    diagonal_radius = np.sqrt(u * u + dy * dy)
    a[(np.abs(diagonal_radius - 13.6) < .8) & (np.abs(v) < .8)] = WHITE
    a[(np.abs(diagonal_radius - 13.6) < .45) & (v >= .8) & (v < 1.6)] = CASE
    for xx in (4, 30):
        box((xx - 1, 2, 17), (xx + 1, 5, 19), WHITE)
        box((xx, 6, 18), (xx, 17, 18), CASE)

    sphere = np.sqrt(dx * dx + (y - 20) ** 2 + dz * dz)
    a[sphere <= 7.4] = STONE
    a[(sphere <= 7.4) & (np.isin(y, (15, 16, 19, 20, 23, 24)))] = CYAN
    a[(sphere <= 7.4) & (np.abs(dx) <= 1)] = FLUIX
    a[(sphere <= 7.4) & (np.abs(dz) <= 1)] = FLUIX
    a[(sphere >= 6.8) & (sphere <= 7.5) & (np.abs(dx) == np.abs(dz))] = WHITE
    box((15, 27, 16), (19, 27, 20), WHITE)
    box((16, 28, 17), (18, 28, 19), CYAN)
    box((17, 29, 18), (17, 29, 18), LIGHT)

    for xx in (7, 27):
        box((xx, 2, 23), (xx, 3, 29), CASE)
    box((7, 2, 28), (27, 3, 29), CASE)
    box((8, 3, 28), (26, 3, 28), FLUIX)
    box((12, 2, 2), (22, 3, 5), CASE)
    box((13, 4, 3), (21, 4, 5), WHITE)
    box((14, 3, 2), (20, 3, 2), CYAN)
    a[3, 2, 17] = CONTROL
    box((15, 1, 0), (19, 1, 1), WHITE)
    box((14, 1, 6), (20, 1, 9), WHITE)
    box((16, 1, 6), (18, 1, 9), FLUIX)
    return a


def export(a):
    palette = ['minecraft:air', *STATES]
    compound = nbt.Compound
    coords = [(xx, yy, zz) for yy in range(H) for zz in range(D) for xx in range(W)]
    file = nbt.File({'DataVersion': nbt.Int(3465), 'size': nbt.List[nbt.Int]([W, H, D]),
        'palette': nbt.List[compound]([compound({'Name': nbt.String(s)}) for s in palette]),
        'blocks': nbt.List[compound]([compound({'pos': nbt.List[nbt.Int](p),
            'state': nbt.Int(a[p[1], p[2], p[0]])}) for p in coords]),
        'entities': nbt.List[compound]()}, gzipped=True)
    file.save(OUT / (STEM + '.nbt'))
    file = nbt.File({'Version': nbt.Int(2), 'DataVersion': nbt.Int(3465),
        'Width': nbt.Short(W), 'Height': nbt.Short(H), 'Length': nbt.Short(D),
        'Offset': nbt.IntArray([0, 0, 0]), 'PaletteMax': nbt.Int(len(palette)),
        'Palette': compound({s: nbt.Int(i) for i, s in enumerate(palette)}),
        'BlockData': nbt.ByteArray(a.ravel().view(np.int8))}, root_name='Schematic', gzipped=True)
    file.save(OUT / (STEM + '.schem'))


def surfaces(a):
    groups = [[[] for _ in range(6)] for _ in STATES]
    for face, axis, sign in [(0, 2, 1), (1, 2, -1), (2, 1, 1), (3, 1, -1), (4, 0, -1), (5, 0, 1)]:
        neighbor = np.zeros_like(a)
        dest, source = [slice(None)] * 3, [slice(None)] * 3
        dest[axis], source[axis] = (slice(None, -1), slice(1, None)) if sign > 0 else (slice(1, None), slice(None, -1))
        neighbor[tuple(dest)] = a[tuple(source)]
        visible = (neighbor == 0) | ((neighbor == GLASS) & (a != GLASS))
        for m in range(1, len(STATES) + 1):
            groups[m - 1][face] = np.flatnonzero(((a == m) & visible).ravel()).tolist()
    return groups


class PreviewResources(Resources):
    def read(self, rel):
        if rel == 'assets/hk3gtl/blockstates/ae_nexus.json':
            return b'{"variants":{"":{"model":"hk3gtl:block/research_point_computer"}}}'
        return super().read(rel)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    a = geometry()
    counts = Counter({s: int((a == i).sum()) for i, s in enumerate(STATES, 1)})
    export(a)
    resources = PreviewResources(instance='C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft',
        client='C:/Users/OWNER/.gradle/caches/fabric-loom/1.20.1/minecraft-client.jar', project_resources=ROOT / 'src/main/resources')
    materials = [resources.material(s) for s in STATES]
    save(OUT / '材质来源.json', dict(resources=resources.sources,
        controller_adapter='仅预览将现有GT MachineRenderer的research_point_computer六面立方体模型绑定到ae_nexus；未修改游戏blockstate'))
    resources.close()
    zones = [dict(name='存储列阵', min=[2, 2, 13], max=[7, 10, 24], pos=[4, 11, 18]),
             dict(name='并行运算', min=[27, 2, 13], max=[32, 10, 24], pos=[30, 11, 18]),
             dict(name='内部合成', min=[11, 2, 28], max=[23, 7, 32], pos=[17, 8, 31]),
             dict(name='万象数据核心', min=[10, 13, 11], max=[24, 29, 25], pos=[17, 26, 18])]
    ports = [dict(id='后部ME接线候选面', pos=[17, 3, 32], face='south', purpose='几何接线建议；功能接口位置由0001接入时核定')]
    paths = [dict(name='正面操作通道', min=[12, 2, 0], max=[22, 4, 1]),
             dict(name='存储柜检修', min=[8, 2, 12], max=[10, 5, 25]),
             dict(name='运算柜检修', min=[24, 2, 12], max=[26, 5, 25]),
             dict(name='后侧接线净空', min=[10, 2, 33], max=[24, 5, 34])]
    manifest = dict(title=TITLE, candidate='A1', conversation='0005',
        conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e', created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        actual_size_wdh=[W, D, H], controller=CONTROLLER, controller_face='north', block_count=sum(counts.values()),
        material_counts=counts, zones=zones, suggested_clearance=paths,
        geometry='低矮八角机座；中央分层球形数据机阵；紫色竖环与白色斜环；左右低架机柜与后部玻璃合成舱；前置低主控台',
        reference=dict(repository='https://github.com/ModularMCLib/DataEnergistics', branch='1.21',
            commit='f825d9fbe5e79a0a7b6b27b28e865dae32a577c7', official_main_size_wdh=[27, 32, 28],
            source='../../logs/0005-ae-nexus-appearance-20261114/reference/',
            borrowed='抬高的近球形存储核心、大型环与弧架、扁平基座、白灰紫材质秩序',
            original='尺寸、双环角度、下层三舱合并布局、球体分层、主控台与本项目材料配置均为本候选设计',
            not_claimed='CPU与合成子结构相对主结构的官方摆位未确证；本候选左右机柜不是官方布局复刻'),
        design_constraints=dict(first_build='任务赠送，初建即开放规划的全部功能；不设置模块升级路线',
            power='没有新增能源缓冲或无线物流功能；紫环与母线为数据造型',
            scope='独立外观候选；保持ae_nexus现有注册、Pattern、配方与AE逻辑不变'),
        status=dict(appearance_approved=False, pattern_changed=False, jar_built=False, installed=False, game_verified=False),
        files={ext: dict(file=STEM + '.' + ext, sha256=hashlib.sha256((OUT / (STEM + '.' + ext)).read_bytes()).hexdigest())
               for ext in ('nbt', 'schem')})
    save(OUT / 'manifest.json', manifest)
    save(OUT / '材料清单.json', [dict(state=s, name=NAMES[s], count=n) for s, n in counts.items()])
    groups = surfaces(a)
    faces = sum(len(f) for g in groups for f in g)
    payload = dict(data=dict(key=STEM, name=STEM, title=TITLE, size=[W, H, D], controller=CONTROLLER,
        controller_face='north', ports=ports, paths=paths, zones=zones), palette=STATES, blockCount=sum(counts.values()),
        materials=materials, names=NAMES, surfaceGroups=groups,
        surfaceRunLengths=[[[1] * len(f) for f in g] for g in groups],
        audit=dict(palette=counts, checks=[], viewer_surface_faces=faces, viewer_rendered_quads=faces))
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False).encode(), mtime=0)).decode()
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', 'utf8')
    viewer = (SHARED / 'viewer.bundle.js').read_text('utf8')
    for old, new in [('钻石块标记', '万象天枢主控'), ('偏馈碟阵与双轨整备站V1', TITLE),
                     ('调度楼材质近景', '主控近景'), ('后侧天线与轴座', '后部内部合成舱'),
                     ('逐格回读与净空检查通过 · ', '独立外观候选 · '),
                     (' 个内嵌接口候选位 · 未游戏验收', ' 处接线建议 · 外观待评审')]:
        viewer = viewer.replace(old, new)
    viewer = viewer.replace('roughness:.78,metalness:.08,alphaTest:', 'roughness:.78,metalness:.08,transparent:t.transparent,depthWrite:!t.transparent,alphaTest:')
    viewer = viewer.replace('C.zoom=Math.min(28,_/20)', 'C.zoom=Math.min(28,Math.max(1,_/7))')
    viewer = viewer.replace('get(`view`)??`front`', 'get(`view`)??`right`')
    (OUT / 'viewer.bundle.js').write_text(viewer, 'utf8')
    shutil.copy2(SHARED / 'Three许可.txt', OUT / 'Three许可.txt')
    shutil.copy2(LOG / 'reference/official-main-coordinate-reference.png', OUT / '官方坐标参考.png')
    css = re.search(r'<style>(.*?)</style>', (SHARED / '三维评审.html').read_text('utf8'), re.S)[1]
    buttons = ''.join(f'<button data-view="{key}">{label}</button>' for key, label in
        [('front', '前左全景'), ('right', '前右全景'), ('back', '后侧'), ('top', '俯视'),
         ('inside', '逐层剖切'), ('orthofront', '正面'), ('orthoside', '侧面'), ('controller', '主控近景')])
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLE}</title><style>{css}</style>
<header><h1>{TITLE}</h1><div>0005外观候选 · 宽35×深35×高33 · {manifest['block_count']:,}方块 · 使用项目与整合包现有材质</div></header>
<main class="review"><section id="stage"><div id="loading">加载真实方块材质…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">中央分层数据球，紫色竖环与白色斜环交叉。左右存储／运算机柜、后部合成舱合在低矮八角基座上；前面是实际ae_nexus主控的既有模型。</div>
<div class="locator"><b>任务赠送，搭成即满功能</b><p>本版只定外观；不沿用旧中枢A1的MAX供电、八孔接口、后换模块升级方案。</p><button data-view="controller">定位主控 (17,3,2)</button></div>
<div>{buttons}</div><p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">32</b><input id="layer" type="range" min="0" max="32" value="32"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接线建议位置</label><label><input id="showPaths" type="checkbox">检修通道</label><label><input id="showZones" type="checkbox" checked>功能区域名称</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>外观与功能对应</summary><p>数据球：全网数据与调度的视觉主体。两侧机柜分别表现存储列阵与虚拟CPU／并行运算；后舱表现内部工作台合成。三舱是一体化外壳，不是三个待升级模块。</p><p>所有环架和光带均为静态方块；没有能源缓冲功能，也没有加入无线物流或替代真实GT加工。</p></details>
<details><summary>接线建议</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材料与用量</summary><div id="materials"></div></details><div id="checks"></div>
<details open><summary>参照与逐格文件</summary><p><a href="官方坐标参考.png">官方主结构坐标示意</a> · <a href="manifest.json">本候选设计记录</a> · <a href="材料清单.json">材料清单</a></p><p><a href="{STEM}.nbt">NBT</a> · <a href="{STEM}.schem">Schematic</a></p><p>NBT为外观方块模板，未包含可运行机器的AE／GT方块实体配置。正式Pattern未改、外观未批准、未构建或安装JAR、未游戏验收。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''
    (OUT / '三维评审.html').write_text(page, 'utf8')
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{TITLE}</title><style>body{{background:#121523;color:#e3e7f3;font:16px/1.8 "Microsoft YaHei";max-width:1300px;margin:30px auto;padding:20px}}a{{color:#a7caff}}img{{width:100%}}h2{{margin-top:40px}}</style><h1>{TITLE}</h1><p>宽35×深35×高33 · {manifest['block_count']:,}方块 · 任务赠送、初建满功能的独立外观候选。</p><p><a href="三维评审.html">打开交互三维预览</a> · <a href="manifest.json">设计记录</a> · <a href="材料清单.json">真实材料清单</a></p><img src="前右预览.png" alt="万象天枢A1真实方块预览"><p>中部数据球、交叉紫白环架、下层三舱与前置主控台。采用石英白、计算机深灰、福鲁伊克斯紫与少量青色。</p><h2>后部合成舱</h2><img src="后侧预览.png" alt="后部合成舱与交叉环架"><h2>官方取形依据</h2><img src="官方坐标参考.png" alt="依据官方指南坐标生成的主结构示意"><p>官方参照来自DataEnergistics 1.21指南模型：抬高存储球、外围环架和低机座。上图是坐标示意，非游戏截图；未把CPU／合成子结构未核实的相对摆位当作官方事实。</p><p>本候选未改ae_nexus注册、Pattern或AE逻辑；未批准、未打包、未安装或运行游戏。NBT／Schematic只交付外观方块，不代表可成型机器。</p></html>''', 'utf8')
    shutil.copy2(__file__, OUT / Path(__file__).name)
    save(LOG / 'appearance-a1.json', manifest)
    print(json.dumps(dict(output=str(OUT), size_wdh=[W, D, H], blocks=manifest['block_count']), ensure_ascii=True))


if __name__ == '__main__':
    main()
