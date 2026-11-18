import base64
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
import sys

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W08_薪炎恒星熔铸炉_作者蓝图_A1_20261116'
LOG = ROOT / 'logs/0005-w08-author-blueprint-a1-20261116'
sys.path.insert(0, str(ROOT / 'deliveries/0005_W07_黑渊白花_斜悬方舟轮廓_F1_20261116/生成脚本'))
from build import mesh_part
import w08_base_20261116 as base
import w08_sword_reactor_20261116 as core
import w08_wings_cloak_20261116 as wings


def save(target, value):
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def export_nbt(keys, states, size, materials):
    w, h, d = size
    header, _ = headers([m['state'] for m in materials], (h, d, w), len(keys))
    record = np.frombuffer(RECORD, np.uint8)
    with gzip.open(OUT / 'W08-薪炎恒星熔铸炉-A1.nbt', 'wb', compresslevel=6) as handle:
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
    materials = json.loads((OUT / 'materials.json').read_text('utf8'))
    parts, notes = [], []
    for module in (base, core, wings):
        current, sampling = module.build()
        parts.extend(current)
        notes.extend(json.dumps(note, ensure_ascii=False) if isinstance(note, dict) else note for note in sampling)
        print(f'{module.__name__}: {len(current)}构件 {sum(len(p.p) for p in current):,}构件占格', flush=True)
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    counts = [len(p.p) for p in parts]
    all_keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    all_states = np.concatenate([p.states for p in parts])
    keys, chosen = np.unique(all_keys[::-1], return_index=True)
    chosen = len(all_states) - chosen - 1
    states = all_states[chosen]
    del all_keys, all_states, chosen
    archive, packed, quads = {}, [], 0
    for index, part in enumerate(parts):
        archive[part.name + '_xyz'], archive[part.name + '_materials'] = part.p, part.states
        item, count = mesh_part(part, materials)
        packed.append(item)
        quads += count
        print(f'表面 {index + 1}/{len(parts)} {part.name} {count:,}', flush=True)
    v = lambda direction, **options: dict(direction=direction, **options)
    views = dict(front=v([-.95, .72, -1.45]), right=v([1, .65, -1.2]), orthofront=v([0, .001, -1]),
                 side=v([1, .01, 0]), back=v([.8, .65, 1.2]), top=v([0, 1, .001]),
                 core=v([-.75, .6, -1.2], center=[489, 150, 460], half=[185, 180, 185]),
                 sword=v([-.65, .4, -1.2], center=[489, 180, 510], half=[180, 190, 100]),
                 wings=v([0, .45, -1], center=[489, 220, 680], half=[520, 200, 280]),
                 cloak=v([-.7, .5, 1], center=[330, 120, 760], half=[250, 150, 220]),
                 base=v([-.8, 1.1, -1], center=[489, 25, 460], half=[510, 60, 480]),
                 controller=v([-.6, .7, -.9], center=[489, 46, 60], half=[50, 30, 80]),
                 blocks=v([-.8, .6, -.5], center=[460, 45, 60], half=[8, 8, 8]))
    labels = ['整体前左', '整体前右', '正面', '侧面', '背面', '俯视', '恒星与三环', '劫灭巨剑', '机械火翼', '火焰披风', '八芒星底盘', '主控舰桥', '逐格像素']
    for preset, label in zip(views.values(), labels):
        preset['label'] = label
    data = dict(machine_id='W08', title='炎之律者·劫焰·恒星熔铸炉', candidate='A1', size=size,
                nominal_size_wdh=[978, 921, 338], bounds=dict(min=low.tolist(), max=high.tolist()),
                blueprint_to_export_offset_xyz=(-low).tolist(), controller_blueprint=[489, 46, 10],
                axis_blueprint_xyz=dict(start=[489.5, .5, 460.5], end=[489.5, 338.5, 460.5 + 338 / np.tan(np.radians(75))]),
                views=views, runtime_voltage='CIV', research='RN-SFF',
                interface_rule='仅主控固定，其余全部实体方块可随时替换合法通用接口，位置与朝向由玩家选择。')
    config = dict(data=data, audit=dict(viewer_rendered_quads=quads), materials=materials, parts=packed)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT / 'data.js').write_text('window.W08_STATIC_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
    np.savez_compressed(OUT / '原案构件数据.npz', **archive)
    export_nbt(keys, states, size, materials)
    notes += [
        '原文的VII型文明、压缩超新星及因果律重工业是建筑叙事依据；现有W08运行CIV、研究RN-SFF保持，文档INF/HERRSCHER/FINALITY-PRE未转成游戏电压。',
        '文档中直径200、160的恒星描述并存；本次按详细分层直径160制作恒星本体，240为拘束环、280为空间壁范围，原文冲突保留。',
        '实际338格高度从世界Y=-64起时最高格为273，原文“捅穿320上限”不成立；此预览使用局部坐标，项目已有高度限制移除安排。',
        '原文6种专用方块属于材质建议。本次映射15种已有方块并使用原生像素贴图，新增注册方块和新画贴图均为0。',
        '正文的Blender、稀疏抽样成型与BER替换实体均为所附方案建议；本次输出完整整数格外观、分构件预览及NBT，成型逻辑沿既有系统另行接入。',
        '构件按原文独立保留，交叠保持原坐标；NBT同一格按后写构件材质导出，NPZ保留各构件完整占格。三环旋转与恒星脉冲、完成冲击波仅为网页演示。'
    ]
    notes += [
        '翼部原文另写500格深度；本次主翼从Z520后展至披风Z921，主体连续深度约401格，炮阵另向前延伸。500格未作为已满足的实体尺寸，保留该差异供作者修订。',
        '巨剑双侧剑刃最大整数格宽139、护手占格宽301；原文140与300为名义连续尺寸。对称坐标与完整端点保留。',
        '剑脊六道磁环与中子星物质瀑布当前为静态方块；本次网页运动覆盖三道圣痕拘束环、恒星脉冲与配方完成光束及冲击波。'
    ]
    geometry = dict(candidate='A1', stage='作者蓝图完整方块预览', nominal_size_wdh=[978, 921, 338],
                    actual_size_xyz=size, actual_size_wdh=[w, d, h], bounds=data['bounds'], blocks=len(keys),
                    source_component_blocks=sum(counts), overlap_extra_memberships=sum(counts) - len(keys),
                    surface_quads=quads, controller_blueprint=data['controller_blueprint'], interface_rule=data['interface_rule'],
                    materials=[m['state'] for m in materials], material_counts={materials[i - 1]['state']: int((states == i).sum()) for i in range(1, len(materials) + 1)},
                    components={p.name: dict(label=p.label, blocks=len(p.p), bounds=dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist()), metadata=p.metadata) for p in parts},
                    source_sha256=hashlib.sha256((OUT / '原文.md').read_bytes()).hexdigest(), instance_access=False,
                    appearance_approved=False, game_code_modified=False, jar_built=False, game_verified=False,
                    source_notes=notes, texture_source='已缓存原生贴图与Lodestone自带原版资源包')
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    save(OUT / '原文取样记录.json', notes)
    rows = ''.join('<li>' + escape(note) + '</li>' for note in notes)
    html = ('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>W08原文与整数格取样</title>'
            '<style>body{max-width:1000px;margin:40px auto;background:#11161e;color:#eee;font:16px/1.8 system-ui}'
            'a{color:#ffd688}li{margin:16px 0}</style><p><a href="index.html">返回预览</a> · '
            '<a href="原文.md">原文</a></p><h1>W08 原文与整数格取样</h1><p>名义978×921×338，实际'
            + '×'.join(map(str, [w, d, h])) + '。完整保留生成范围，构件位置冲突照实记录。</p><ol>' + rows + '</ol></html>')
    (OUT / '原文与取样.html').write_text(html, 'utf8')
    for name in ['w08_common_20261116.py', 'w08_base_20261116.py', 'w08_sword_reactor_20261116.py', 'w08_wings_cloak_20261116.py', Path(__file__).name]:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    print(json.dumps(dict(size_wdh=[w, d, h], parts=len(parts), blocks=len(keys), quads=quads)), flush=True)


if __name__ == '__main__':
    main()
