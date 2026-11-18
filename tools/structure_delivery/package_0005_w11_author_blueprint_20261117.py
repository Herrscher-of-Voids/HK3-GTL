import base64
from copy import copy
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZipFile

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
from w11_foundation_20261117 import build_foundation
from w11_canopy_20261117 import build_canopy
from w11_theater_20261117 import build_theater, cabin_layout
from w11_puppet_20261117 import build_puppet


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W11_千律机械剧场_作者蓝图_A1_20261117'
LOG = ROOT / 'logs/0005-w11-author-blueprint-a1-20261117'
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
    gt = Path('C:/Users/OWNER/.gradle/caches/modules-2/files-2.1/com.gregtechceu.gtceu/gtceu-1.20.1/1.4.4/ac965814b9aa85fc60e688454d9bf07a1ea3f8f3/gtceu-1.20.1-1.4.4.jar')
    mc = Path('E:/Prism/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar')
    slots = [
        ('gtceu:black_metal_sheet', '剧场黑色金属主甲', gt, 'assets/gtceu/textures/block/decoration/metalsheet_black.png'),
        ('gtceu:black_studs', '铆接骨架与散热底板', gt, 'assets/gtceu/textures/block/decoration/studs_black.png'),
        ('gtceu:white_metal_sheet', '骨瓷白机械面具与装甲', gt, 'assets/gtceu/textures/block/decoration/metalsheet_white.png'),
        ('minecraft:gold_block', '辉金规则框架', mc, 'assets/minecraft/textures/block/gold_block.png'),
        ('gtceu:red_metal_sheet', '深红机构与帷幕饰板', gt, 'assets/gtceu/textures/block/decoration/metalsheet_red.png'),
        ('gtceu:magenta_metal_sheet', '品红眼部指示灯', gt, 'assets/gtceu/textures/block/decoration/metalsheet_magenta.png'),
        ('gtceu:yellow_borderless_lamp[bloom=true,inverted=true,lit=true,powered=false]', '支配金色提线与发光纹', gt, 'assets/gtceu/textures/block/lamps/yellow_borderless.png'),
        ('gtceu:white_lamp[bloom=true,inverted=true,lit=true,powered=false]', '白色核心与指示光', gt, 'assets/gtceu/textures/block/lamps/white.png'),
        ('minecraft:red_stained_glass', '深红冷却介质与核心晶体', mc, 'assets/minecraft/textures/block/red_stained_glass.png'),
        ('gtceu:gray_metal_sheet', '灰色液压活塞机构', gt, 'assets/gtceu/textures/block/decoration/metalsheet_gray.png'),
        ('hk3gtl:voltage_machine_casing_cev', 'CEV液压与统御节点机壳', None, 'src/main/resources/assets/hk3gtl/textures/block/voltage_casings/cev/casing.png'),
        ('minecraft:redstone_block', '唯一主控预览定位', mc, 'assets/minecraft/textures/block/redstone_block.png')]
    result = []
    for state, label, archive, entry in slots:
        if archive:
            with ZipFile(archive) as jar:
                png = jar.read(entry)
        else:
            png = (ROOT / entry).read_bytes()
        texture = 'data:image/png;base64,' + base64.b64encode(png).decode()
        result.append(dict(state=state, label=label, faces={face: texture for face in FACES},
            transparent='stained_glass' in state, emissive='lamp' in state or 'magenta' in state,
            source=dict(archive=str(archive) if archive else None, entry=entry, png_sha256=hashlib.sha256(png).hexdigest(), texture_mode='原生像素贴图，无额外染色')))
    return result


def export_nbt(keys, states, size, palette):
    w, h, d = size
    header, _ = headers([m['state'] for m in palette], (h, d, w), len(keys))
    record = np.frombuffer(RECORD, np.uint8)
    with gzip.open(OUT / 'W11-千律机械剧场-A1.nbt', 'wb', compresslevel=6) as handle:
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
    palette, parts = materials(), []
    for build in (build_foundation, build_theater, build_puppet, build_canopy):
        current = build()
        parts.extend(current)
        print(f'{build.__name__}: {len(current)}构件，{sum(len(p.p) for p in current):,}格', flush=True)
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    values = np.concatenate([p.states for p in parts])
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(values) - chosen - 1
    values, owners = values[chosen], owners[chosen]
    xyz = np.c_[keys % w, keys // (w * d), keys // w % d].astype(np.int32)
    np.savez_compressed(OUT / '完整整数格模型.npz', xyz=xyz, states=values, origin=low, size=size, owners=owners)
    packed, quads = [], 0
    for i, part in enumerate(parts):
        selected = owners == i
        visible = copy(part)
        visible.p, visible.states = xyz[selected] + low, values[selected]
        item, count = mesh_part(visible, palette)
        group = part.metadata.get('group', part.metadata.get('section', 'puppet'))
        item['modelId'] = 'puppet' if group == 'stage' else group
        packed.append(item)
        quads += count
        print(f'表面 {i + 1}/{len(parts)} {part.name}: {count:,}', flush=True)
    layout = cabin_layout()
    notes = [
        '作者名义宽深高1000×1000×311，采用X/Z=-500..499、Y=0..310；几何中心X/Z=-0.5。顶层261..310恰好50层。',
        '1000座实体机舱排为5层，每层三圈40/64/96座；舱底Y46/69/92/115/138，每舱15×15×20。原文三层指三道同心回廊，竖向5层为本稿排布取样。',
        'R200作为内回廊边缘，内圈机舱中心R212，另两圈R320/R440；半径200中央空域保留。',
        '八座150×150×45基座采用偏22.5度八向中心，以容纳R300..500环带。液压机械臂另向上延伸。',
        '1000条舱端提线独立向外短接后升至顶梁，各层独立外半径；750条红丝、250条金丝。红金粒子脉冲为网页演示。',
        '唯一主控定位(-1,190,-1)位于舞台中心，红石块代表待接入真实主控；其余全部实体格可自由替换合法通用接口，位置与朝向由玩家选择。',
        '1000舱代表本轮造型数量，工业能力读取现行机器实现。中央半身木偶、黑白甲、红金丝线与十字架均为作者工业演绎。',
        '使用现有GT/HK/原版12种方块原生贴图，专用方块概念映射到既有方块；新增注册与新绘材质均为0。',
        '本稿保留作者指定尺寸与配色，尺寸递增、材料种类和电压主甲规则的专项冲突单独记录，状态为待审候选。']
    views = dict(puppet=dict(label='中央六臂木偶', center=[-.5, 224, -.5], half=[90, 43, 40], direction=[-.35, .18, 1]),
        stage=dict(label='舞台与主控', center=[-.5, 184, -.5], half=[65, 28, 65], direction=[-.5, .7, 1]),
        cabins=dict(label='千面回廊近景', center=[150, 107, 150], half=[74, 65, 70], direction=[-1, .5, -1]),
        canopy=dict(label='十字天幕与汇线', center=[-.5, 279, -.5], half=[505, 43, 505], direction=[-.8, 1.2, 1]),
        well=dict(label='冷却井与八向基座', center=[-.5, 35, -.5], half=[460, 48, 460], direction=[-.7, 1.4, 1]),
        controller=dict(label='唯一主控位置', center=[-1, 190, -1], half=[10, 8, 10], direction=[-.2, .4, 1]),
        pixels=dict(label='原生像素方块', center=[157, 150, 143], half=[10, 10, 10], direction=[-1, .6, -1]))
    models = []
    for group, title in [('foundation', '深渊井与八向基座'), ('theater', '1000舱三重剧场'), ('puppet', '六臂木偶与主控舞台'), ('strings', '中央提线'), ('canopy', '十字控制架与天幕')]:
        subset = [p for p in packed if p['modelId'] == group]
        lo = np.min([p['origin'] for p in subset], axis=0)
        hi = np.max([np.array(p['origin']) + p['size'] for p in subset], axis=0)
        models.append(dict(id=group, title=title, origin=lo.tolist(), sizeXYZ=(hi - lo).tolist(), blocks=sum(p['blocks'] for p in subset), features=[title], references=[], views=views))
    data = dict(title='W11 支配之律者·千律·分布式工业统御阵', candidate='A1', bounds=dict(min=low.tolist(), max=high.tolist()),
        sizeXYZ=size, total_blocks=len(keys), models=models, views=views, design=notes[:6], cabins=layout)
    config = dict(data=data, materials=palette, parts=packed)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT / 'data.js').write_text('window.W11_VOXEL_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
    counts = {m['state']: int((values == i + 1).sum()) for i, m in enumerate(palette)}
    geometry = dict(machine='W11', candidate='A1', status='作者蓝图完整方块预览待审', generated_at=datetime.now().astimezone().isoformat(),
        actual_size_wdh=[w, d, h], bounds=data['bounds'], blocks=len(keys), unique_block_types=len(np.unique(values)),
        footprint_area=w * d, bounding_box_volume=w * d * h, actual_height=h, surface_quads=quads,
        components={p.name: dict(label=p.label, blocks=len(p.p), metadata=p.metadata) for p in parts}, material_counts=counts,
        non_vanilla_percent=100 * sum(n for state, n in counts.items() if not state.startswith('minecraft:')) / len(keys),
        cabin_count=len(layout), controller=dict(source_xyz=[-1, 190, -1], export_xyz=(np.array([-1, 190, -1]) - low).tolist(), preview_state='minecraft:redstone_block'),
        interface_rule=notes[5], source_notes=notes, appearance_approved=False, game_code_modified=False, jar_built=False, installed=False, game_verified=False)
    baseline = dict(footprint_area=900601, bounding_box_volume=441313404, actual_height=636, blocks=23541415, unique_block_types=58)
    geometry['scale_comparison'] = dict(runtime_tier='CEV / 30', metrics={key: dict(candidate=geometry[key], existing_recorded_max=value,
        strict_minimum=value + 1, greater=geometry[key] > value) for key, value in baseline.items()},
        source='deliveries/0005_W09_T9与S2山观兵装矩阵_F2_20261117/manifest.json:scale_comparison',
        status='占地高于既有比较值；包围盒、高度、实体数量、种类存在递增冲突，专项例外尚未批准',
        coverage='既有CEV比较baseline；全库低阶批准形态的逐项材料种类尚缺统一清单', w09_exception_applies=False)
    geometry['runtime'] = dict(controller='hk3gtl:w11_distributed_industrial_command', tier='CEV', tier_index=30, research='RN-DIO', formal_blueprint_present=False)
    conflicts = dict(notes=notes, scale_comparison=geometry['scale_comparison'], palette_rule='作者指定黑白金红；电压机壳主导规则的专项例外尚未批准')
    for name, value in [('geometry.json', geometry), ('materials.json', palette), ('舱室坐标.json', layout), ('conflicts.json', conflicts)]:
        save(OUT / name, value)
    save(LOG / 'generation.json', geometry)
    export_nbt(keys, values, size, palette)
    for name in ['w11_common_20261117.py', 'w11_foundation_20261117.py', 'w11_theater_20261117.py', 'w11_puppet_20261117.py', 'w11_canopy_20261117.py', Path(__file__).name]:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    files = ['data.js', 'geometry.json', 'materials.json', '舱室坐标.json', 'conflicts.json', '完整整数格模型.npz', 'W11-千律机械剧场-A1.nbt']
    save(OUT / 'manifest.json', dict(machine='W11', candidate='A1', actual_size_wdh=[w, d, h], blocks=len(keys), cabin_count=len(layout),
        files={name: dict(bytes=(OUT / name).stat().st_size, sha256=digest(OUT / name)) for name in files}))
    print(json.dumps(dict(size_wdh=[w, d, h], parts=len(parts), blocks=len(keys), quads=quads)), flush=True)


if __name__ == '__main__':
    main()
