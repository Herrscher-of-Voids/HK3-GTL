# -*- coding: utf-8 -*-
"""生成ME一体化合成中枢的独立几何、功能机位合同与真实材质评审页。"""
from collections import Counter
from datetime import datetime, timedelta, timezone
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
OUT = ROOT / 'deliveries/0005_ME一体化合成中枢_三舱模块式_A1_20261114'
LOG = ROOT / 'logs/0005-me-crafting-hub-a1-20261114'
SHARED = ROOT / 'deliveries/I39_无人跨界航路中继站_偏馈碟阵与双轨整备站_V1_20261027/i39'
NAME = '0005-me-integrated-crafting-hub-a1'
TITLE = 'ME 一体化合成中枢 · 三舱模块式 A1'
STATES = ['gtceu:max_machine_casing', 'gtceu:computer_casing', 'gtceu:computer_heat_vent',
          'gtceu:tempered_glass', 'hk3gtl:industrial_port_casing']
NAMES = dict(zip(STATES, ['MAX机械方块', '计算机机壳', '计算机散热口', '钢化玻璃', '空余接口填充块']))
MAX, CASE, VENT, GLASS, PORT = range(1, 6)
W, H, D = 15, 8, 13


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def geometry():
    a = np.zeros((H, D, W), np.uint8)

    def box(lo, hi, material):
        x, y, z = lo
        X, Y, Z = hi
        a[y:Y + 1, z:Z + 1, x:X + 1] = material

    def cabinet(lo, hi):
        x, y, z = lo
        X, Y, Z = hi
        box(lo, hi, CASE)
        box((x + 1, y + 1, z + 1), (X - 1, Y - 1, Z - 1), 0)

    box((0, 0, 2), (14, 0, 12), CASE)
    box((4, 0, 0), (10, 0, 1), CASE)
    for x in (0, 14):
        box((x, 0, 2), (x, 0, 12), MAX)
    box((0, 0, 12), (14, 0, 12), MAX)
    cabinet((1, 1, 4), (4, 6, 9))
    for y in (1, 3, 6):
        box((1, y, 4), (4, y, 4), MAX)
        box((1, y, 9), (4, y, 9), MAX)
    box((2, 2, 4), (3, 5, 4), GLASS)
    box((1, 2, 5), (1, 5, 8), VENT)
    box((2, 7, 5), (3, 7, 8), VENT)
    cabinet((10, 1, 4), (13, 5, 9))
    box((11, 2, 4), (12, 4, 4), GLASS)
    for z in (4, 6, 8):
        box((10, 6, z), (13, 6, z), VENT)
    box((13, 2, 5), (13, 4, 8), VENT)
    box((10, 1, 4), (13, 1, 4), MAX)
    box((10, 5, 4), (13, 5, 4), MAX)
    cabinet((5, 1, 10), (9, 5, 12))
    box((6, 2, 10), (8, 4, 10), GLASS)
    box((6, 2, 12), (8, 4, 12), GLASS)
    box((6, 5, 10), (8, 5, 12), GLASS)
    for x in (5, 9):
        box((x, 1, 10), (x, 5, 12), MAX)
    box((6, 1, 12), (8, 1, 12), VENT)
    # 后置母线横梁联结三区，中央操作通道上方保持开敞。
    box((3, 6, 9), (11, 6, 9), CASE)
    for x in (3, 11):
        box((x, 1, 9), (x, 6, 9), MAX)
    box((5, 1, 1), (9, 4, 2), CASE)
    box((5, 4, 1), (9, 4, 2), GLASS)
    controller = [7, 2, 1]
    ports = []
    for y in range(1, 4):
        for x in range(6, 9):
            if [x, y, 1] == controller:
                continue
            a[y, 1, x] = PORT
            ports.append(dict(id=f'接口位{len(ports) + 1}', pos=[x, y, 1], face='north',
                              purpose='通用接口；未使用时安装填充块，不强制物品仓或流体仓'))
    slots = [
        dict(role='controller', name='主控制器', pos=controller, face='north', registered=False),
        dict(role='max_power', name='MAX电力接入', pos=[6, 1, 1], face='north', registered=True,
             existing_block='gtceu:max_energy_input_hatch', note='现成MAX 2A能源仓建议位；额定与兼容由0001核定'),
        dict(role='me_network', name='ME聚合网络接入', pos=[8, 1, 1], face='north', registered=False),
        dict(role='crafting_storage', name='合成存储模块', pos=[4, 3, 6], face='east', registered=False),
        dict(role='parallel_compute', name='并行运算模块', pos=[10, 3, 6], face='west', registered=False),
        dict(role='internal_crafting', name='内部合成模块', pos=[7, 3, 10], face='north', registered=False),
    ]
    for slot in slots:
        x, y, z = slot['pos']
        a[y, z, x] = 0
    ports[0]['purpose'] = '建议MAX电力接入；完整模板留槽，不能用填充块满足供电条件'
    ports[2]['purpose'] = '建议ME聚合网络接入；完整模板留槽，普通机壳和物料ME仓均不冒充该部件'
    # 北侧正视时+X在画面左侧，统一镜像实体与机位，保持左存储、右运算。
    for item in [*ports, *slots]:
        item['pos'] = [W - 1 - item['pos'][0], *item['pos'][1:]]
        item['face'] = {'east': 'west', 'west': 'east'}.get(item['face'], item['face'])
    return a[:, :, ::-1].copy(), controller, ports, slots


def export(cube, states, stem):
    palette = ['minecraft:air', *states]
    compound = nbt.Compound
    coordinates = [(x, y, z) for y in range(H) for z in range(D) for x in range(W)]
    structure = nbt.File({'DataVersion': nbt.Int(3465), 'size': nbt.List[nbt.Int]([W, H, D]),
        'palette': nbt.List[compound]([compound({'Name': nbt.String(s)}) for s in palette]),
        'blocks': nbt.List[compound]([compound({'pos': nbt.List[nbt.Int](p),
            'state': nbt.Int(cube[p[1], p[2], p[0]])}) for p in coordinates]),
        'entities': nbt.List[compound]()}, gzipped=True)
    structure.save(OUT / (stem + '.nbt'))
    schematic = nbt.File({'Version': nbt.Int(2), 'DataVersion': nbt.Int(3465),
        'Width': nbt.Short(W), 'Height': nbt.Short(H), 'Length': nbt.Short(D),
        'Offset': nbt.IntArray([0, 0, 0]), 'PaletteMax': nbt.Int(len(palette)),
        'Palette': compound({s: nbt.Int(i) for i, s in enumerate(palette)}),
        'BlockData': nbt.ByteArray(cube.ravel().view(np.int8))}, root_name='Schematic', gzipped=True)
    schematic.save(OUT / (stem + '.schem'))
    return {ext: dict(file=stem + '.' + ext, sha256=hashlib.sha256((OUT / (stem + '.' + ext)).read_bytes()).hexdigest())
            for ext in ['nbt', 'schem']}


def surfaces(cube):
    occupied = cube != 0
    groups = [[[] for _ in range(6)] for _ in STATES]
    for face, axis, sign in [(0, 2, 1), (1, 2, -1), (2, 1, 1), (3, 1, -1), (4, 0, -1), (5, 0, 1)]:
        neighbor = np.zeros_like(occupied)
        dest, source = [slice(None)] * 3, [slice(None)] * 3
        dest[axis], source[axis] = (slice(None, -1), slice(1, None)) if sign > 0 else (slice(1, None), slice(None, -1))
        neighbor[tuple(dest)] = occupied[tuple(source)]
        for m in range(1, len(STATES) + 1):
            groups[m - 1][face] = np.flatnonzero((occupied & ~neighbor & (cube == m)).ravel()).tolist()
    return groups


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    a, controller, ports, slots = geometry()
    counts = Counter({s: int((a == i).sum()) for i, s in enumerate(STATES, 1)})
    template = a.copy()
    for slot in slots:
        x, y, z = slot['pos']
        template[y, z, x] = len(STATES) + 1
    files = dict(shell=export(a, STATES, NAME + '-shell'),
                 template=export(template, [*STATES, 'minecraft:structure_void'], NAME + '-template'))
    paths = [dict(name='正面接线与操作', min=[5, 1, -2], max=[9, 4, 0]),
             dict(name='前横向检修通道', min=[1, 1, 3], max=[13, 4, 3]),
             dict(name='中央三舱检修通道', min=[5, 1, 4], max=[9, 4, 8]),
             dict(name='合成舱抽换空间', min=[6, 1, 9], max=[8, 4, 9]),
             dict(name='后部接线', min=[0, 1, 13], max=[14, 4, 14]),
             dict(name='左侧散热检修', min=[-2, 1, 2], max=[-1, 5, 12]),
             dict(name='右侧散热检修', min=[-2, 1, 2], max=[-1, 5, 12]),
             dict(name='顶部散热净空', min=[1, 8, 4], max=[13, 8, 9])]
    paths[5] = dict(name='左侧散热检修', min=[15, 1, 2], max=[16, 5, 12])
    cavities = [dict(name='存储舱内腔', min=[11, 2, 5], max=[12, 5, 8]),
                dict(name='运算舱内腔', min=[2, 2, 5], max=[3, 4, 8]),
                dict(name='合成舱内腔', min=[6, 2, 11], max=[8, 4, 11])]
    regions = [dict(role='crafting_storage', name='左侧高架存储舱', min=[10, 1, 4], max=[13, 7, 9], pos=[12, 6, 6]),
               dict(role='parallel_compute', name='右侧散热运算舱', min=[1, 1, 4], max=[4, 6, 9], pos=[2, 5, 6]),
               dict(role='internal_crafting', name='后部玻璃合成舱', min=[5, 1, 10], max=[9, 5, 12], pos=[7, 5, 11])]
    manifest = dict(key='me-integrated-crafting-hub', title=TITLE, candidate='A1', voltage='MAX',
        conversation='0005', conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
        created_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
        existing_machine_number=None, origin_xyz=[0, 0, 0], actual_size_wdh=[W, D, H],
        coordinate_system='零起算XYZ；原点为西北下角；+X向东、+Y向上、+Z向南／后方；正面北向-Z，从北侧正视时+X在画面左侧；两套NBT原点一致',
        controller=controller, controller_face='north', interface_plane_z=1, universal_interface_count=8,
        universal_interfaces=ports, functional_slots=slots, module_regions=regions,
        required_internal_air=[*paths[1:4], *cavities], external_clearance=[paths[0], *paths[4:]],
        required_air=[*paths, *cavities],
        placement_envelope_min=[-2, 0, -2], placement_envelope_max=[16, 8, 14],
        shell_blocks=sum(counts.values()), functional_slot_count=len(slots), template_marker='minecraft:structure_void',
        material_counts=counts, files=files, pattern_air_rule='列出的内部空腔与检修通道必须留空；外部净空建议安装合同由0001接入',
        shell_export='空腔和功能槽均为空气，结构边界内空气逐格写入；不应直接覆盖既有已装功能件',
        template_export='六处structure_void只标位置，导入时不会替你安装实际功能件；其余空域为明确空气',
        status=dict(appearance_approved=False, registered=False, functional_implemented=False, installed=False, game_verified=False),
        upgrade_contract='每类初建1组模块，每组1个功能锚点，外壳固定；停机后从通道原位更换，升阶不扩体积或增加海量功能块',
        slot_predicate='主控和三类模块锚点为专用功能位；其余实体壳体沿用合法通用接口替换规则，必要能力与数量由0001统一判定',
        responsibility=dict(geometry='0005', registration_ae_mixin_executor_recipes_balance='0001'),
        recipe_status='仅沿用负责人材料和成本方向，不冻结最终组件数量、容量、倍率、EU数值或配方机器')
    save(OUT / 'manifest.json', manifest)
    save(OUT / '逐格结构.json', dict(size_xyz=[W, H, D], axis_order='layers_y -> rows_z -> columns_x',
                                   palette=['minecraft:air', *STATES, 'minecraft:structure_void'], layers_y=template.tolist()))
    save(OUT / '材料清单.json', dict(shell=[dict(state=s, name=NAMES[s], count=n) for s, n in counts.items()],
         functional=[dict(name=s['name'], count=1, geometry_position=s['pos'], block_id=s.get('existing_block'),
                          registered=s['registered']) for s in slots],
         template_markers=dict(state='minecraft:structure_void', count=6, survival_material=False),
         note='真实外壳材料与必装功能件分列；六个填充块为空余接口。昂贵AE元件只计入控制器和三组模块配方，不按外观壳体重复收取。'))
    save(OUT / '交给0001_几何与功能合同.json', dict(design=manifest, requirements=dict(
        first_build='MAX前期，初建功能完整；不需崩坏能、魂钢、律者核心、后MAX电路、世界泡或本机专属产物',
        functionality=['计划与运行状态存储', '全局并行调度', '内部工作台合成', '主控样板槽与外部供应器',
                       '向真实GT机器派料并等待回网', 'AE终端下单、进度和取消', '现有大数、循环、倍增和限定概率订单'],
        integer_types='容量、并行和任务计数从底层使用BigInteger，初始数值和倍率由0001核定',
        power='GT EU；待机与负载分开按模块计算，MAX为额定电压，不恒定满功率',
        interfaces='八槽通用；至少一个MAX供能能力、一个真实ME聚合接入；其余可填充，不强制无用途仓室',
        modules='三类各一组；各一个功能锚点，升级更换该锚点模块；外部机壳只负责造型和结构',
        controller_recipe_draft={'gtceu:max_machine_casing': 1, '通用MAX电路': 4, 'AE工程处理器': 4,
                                 'MAX传感器': 2, 'MAX发射器': 2, '分子装配室': 1, '焊锡合金_mB': 1152},
        recipe_rule='使用本机以外的已有MAX组装设备，0001核定配方及三类模块成本；不据草案声称生存可达性已通过')))
    resources = Resources(instance='C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft',
                          client='C:/Users/OWNER/.gradle/caches/fabric-loom/1.20.1/minecraft-client.jar',
                          project_resources=ROOT / 'src/main/resources')
    materials = [resources.material(s) for s in STATES]
    save(OUT / '材质来源.json', resources.sources)
    resources.close()
    groups = surfaces(a)
    faces = sum(len(f) for g in groups for f in g)
    viewports = ports + [dict(id=s['name'] + '槽', pos=s['pos'], face=s['face'],
                             purpose='基础模块锚点，原位替换升级；仅定位标记，待0001注册') for s in slots[3:]]
    data = dict(key=manifest['key'], name=NAME, title=TITLE, size=[W, H, D], controller=controller,
                controller_face='north', ports=viewports, paths=paths, zones=regions)
    payload = dict(data=data, palette=STATES, blockCount=sum(counts.values()), materials=materials, names=NAMES,
                   surfaceGroups=groups, surfaceRunLengths=[[[1] * len(f) for f in g] for g in groups],
                   audit=dict(palette=counts, checks=[], viewer_surface_faces=faces, viewer_rendered_quads=faces))
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False).encode(), mtime=0)).decode()
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', 'utf8')
    viewer = (SHARED / 'viewer.bundle.js').read_text('utf8').replace('钻石块标记', '主控预留槽（未注册）')
    viewer = viewer.replace('偏馈碟阵与双轨整备站V1', TITLE).replace('调度楼材质近景', '接口机位近景')
    viewer = viewer.replace('后侧天线与轴座', '后侧玻璃合成舱')
    viewer = viewer.replace('roughness:.78,metalness:.08,alphaTest:', 'roughness:.78,metalness:.08,transparent:t.transparent,depthWrite:!t.transparent,alphaTest:')
    viewer = viewer.replace('逐格回读与净空检查通过 · ', '独立外观候选 · ')
    viewer = viewer.replace(' 个内嵌接口候选位 · 未游戏验收', ' 处接口／模块定位 · 功能待0001接入')
    viewer = viewer.replace('C.zoom=Math.min(28,_/20)', 'C.zoom=Math.min(28,Math.max(1,_/7))')
    (OUT / 'viewer.bundle.js').write_text(viewer, 'utf8')
    shutil.copy2(SHARED / 'Three许可.txt', OUT / 'Three许可.txt')
    write_page(manifest)
    save(LOG / 'generation.json', dict(manifest=manifest, exported=True, headless_capture='待生成',
         tests_run=False, game_started=False, instance_modified=False))
    shutil.copy2(__file__, OUT / Path(__file__).name)
    print(json.dumps(dict(output=str(OUT), size_wdh=[W, D, H], shell_blocks=sum(counts.values()), materials=counts), ensure_ascii=True))


def write_page(m):
    css = re.search(r'<style>(.*?)</style>', (SHARED / '三维评审.html').read_text('utf8'), re.S)[1]
    buttons = ''.join(f'<button data-view="{key}">{label}</button>' for key, label in
                      [('front', '前左全景'), ('right', '前右全景'), ('back', '后侧'), ('top', '俯视'),
                       ('inside', '逐层剖切'), ('orthofront', '正面'), ('orthoside', '侧面'), ('controller', '主控与接口')])
    links = ' · '.join(f'<a href="{NAME}-{stem}.{ext}">{label}{ext.upper()}</a>'
                       for stem, label in [('shell', '外壳净体'), ('template', '完整定位模板')] for ext in ['nbt', 'schem'])
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLE}</title><style>{css}</style>
<header><h1>{TITLE}</h1><div>0005几何候选 · 宽15×深13×高8 · {m['shell_blocks']}块真实外壳＋6处必装功能机位 · 未批准／未实现功能</div></header>
<main class="review"><section id="stage"><div id="loading">加载真实方块材质…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">初建完整功能、后续原位换模块。左侧高架存储柜，右侧散热运算柜，后部玻璃合成舱。三类各1组；柜体多块外壳不等于多套昂贵模块。</div>
<div class="locator"><b>主控 (7,2,1)，北向</b><p>正面宽度中线，同面3×3接口区：X6—8、Y1—3、Z1。黄色框仅作定位；主控、ME接入和模块尚未注册。</p><button data-view="controller">定位主控</button></div>
<div>{buttons}</div><p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">7</b><input id="layer" type="range" min="0" max="7" value="7"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口与模块定位</label><label><input id="showPaths" type="checkbox">接线与检修净空</label><label><input id="showZones" type="checkbox" checked>三区名称</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>功能边界与机位</summary><p>六处模板机位：主控1、MAX能源接入1、ME聚合网络接入1、存储／运算／合成模块各1。能源仓已有真实方块；其余由0001注册和接入。空余六接口填充，不强制无用途仓室。</p><p>0001负责AE逻辑、BigInteger、大数／循环／倍增／限定概率、配方和EU数值；本候选没有授予这些能力。</p></details>
<details><summary>接口及模块坐标</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实外壳材料与用量</summary><div id="materials"></div></details><div id="checks"></div>
<details open><summary>逐格文件与接入合同</summary><p>{links}</p><p><a href="manifest.json">原点、坐标与净空</a> · <a href="材料清单.json">完整材料清单</a> · <a href="逐格结构.json">逐格结构JSON</a> · <a href="交给0001_几何与功能合同.json">交给0001的合同</a></p><p>模板中structure_void是定位标记，不是生存材料或功能件；导入不会自动生成这些部件。外壳净体中机位为空气，勿覆盖已装好的部件。结构不占用I／W／H编号。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''
    (OUT / '三维评审.html').write_text(page, 'utf8')
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{TITLE}</title><style>body{{background:#121b2b;color:#e2edf5;font:16px/1.8 "Microsoft YaHei";max-width:1200px;margin:30px auto;padding:20px}}a{{color:#a8d9e9}}img{{width:100%}}</style><h1>{TITLE}</h1><p>MAX前期可量产工业设施 · 15×13×8（宽×深×高） · {m['shell_blocks']}真实外壳方块＋6个功能机位。</p><p><a href="三维评审.html">打开交互三维评审</a> · <a href="材料清单.json">完整材料清单</a> · <a href="manifest.json">坐标、净空与升级位置</a> · <a href="交给0001_几何与功能合同.json">0001接入合同</a></p><img src="整体预览.png" alt="真实材质三舱模块式中枢"><p>左侧存储、右侧运算、后部合成；初建各一组模块，换模块升级。正面居中主控和同面八接口，外部GT加工机器仍独立承担真实配方。</p><p>{links}</p><p>主控、ME聚合接入及三类模块待0001实现，structure_void只标机位。外观候选未批准，未注册、未打包、未安装或运行游戏。</p></html>''', 'utf8')


if __name__ == '__main__':
    main()
