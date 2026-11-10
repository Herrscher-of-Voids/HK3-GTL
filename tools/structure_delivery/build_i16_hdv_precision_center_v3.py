# -*- coding: utf-8 -*-
"""I16 V3 HDV palette candidate; V2 geometry is retained as layout reference."""
from __future__ import annotations

import collections
import base64
import gzip
import hashlib
import io
import json
import shutil
import zipfile
from pathlib import Path

import nbtlib
from PIL import Image

import build_i16_precision_center_v2_palette as base
import build_i07_calibration_preview as preview
from material_resources import Resources
from redesign69_geometry import ROOT


OUT = ROOT / 'deliveries/I16_魂钢精密加工中心_双门架定轴校准_V3_HDV_20261021'
LOG = ROOT / 'logs/i16-hdv-precision-center-v3'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
NAME = 'i16-soulium-precision-machining-center-v3-hdv'
ARCHIVE = 'I16_V3_HDV双门架定轴校准_结构与预览.zip'

PORT = 'hk3gtl:industrial_port_casing'
HDV = 'hk3gtl:voltage_machine_casing_hdv'
FORBIDDEN = {
    'minecraft:diamond_block',
    'hk3gtl:casing_colored_light_blue',
    'hk3gtl:casing_colored_yellow',
}

PALETTE = {
    'gtceu:steel_machine_casing': '深色隔振基座与低位支撑',
    HDV: 'HDV 主机械方块：双门架、屋脊基准线与结构识别色',
    'gtceu:clean_machine_casing': '洁净加工厅围护与设备间外墙',
    'gtceu:stainless_steel_turbine_casing': '重载床身与粗加工台',
    'gtceu:tungstensteel_gearbox': '直线导轨、滚轮座与滑台',
    'gtceu:stainless_steel_gearbox': '主轴箱、银灰校准节点、计量仪器台与驱动端',
    'gtceu:laminated_glass': '计量室观察窗与屋脊采光带',
    'gtceu:computer_heat_vent': '温控送回风与设备散热',
    'gtceu:filter_casing': '切屑雾与冷却介质过滤组',
    'gtceu:corrosion_proof_casing': '低位冷却介质总管',
    PORT: '本模组工业接口占位方块；仅作外观标记，不代表仓室能力',
}


def _state_name(state):
    name = str(state['Name'])
    properties = state.get('Properties', {})
    suffix = '[' + ','.join(f'{key}={value}' for key, value in sorted(properties.items())) + ']' if properties else ''
    return name + suffix


def _read_structure(path):
    nbt = nbtlib.load(path)
    palette = [_state_name(state) for state in nbt['palette']]
    blocks = {
        tuple(int(value) for value in block['pos']): palette[int(block['state'])]
        for block in nbt['blocks']
    }
    return [int(value) for value in nbt['size']], blocks


def build():
    base.OUT = OUT
    base.INSTANCE = INSTANCE
    base.NAME = NAME
    base.ARCHIVE = ARCHIVE
    base.PORT = PORT
    base.MARKERS = {PORT}
    base.BASE = 'gtceu:steel_machine_casing'
    base.FRAME = HDV
    base.HALL = 'gtceu:clean_machine_casing'
    base.BED = 'gtceu:stainless_steel_turbine_casing'
    base.RAIL = 'gtceu:tungstensteel_gearbox'
    base.DRIVE = 'gtceu:stainless_steel_gearbox'
    base.GLASS = 'gtceu:laminated_glass'
    base.ACCENT = 'gtceu:stainless_steel_gearbox'
    base.VENT = 'gtceu:computer_heat_vent'
    base.FILTER = 'gtceu:filter_casing'
    base.COOLANT = 'gtceu:corrosion_proof_casing'
    base.METROLOGY = 'gtceu:stainless_steel_gearbox'
    base.MATERIAL_ROLES = PALETTE

    data = base.build()
    data['size'] = [data['size'][0], max(block['pos'][1] for block in data['blocks']) + 1, data['size'][2]]
    for block in data['blocks']:
        if block['state'] == 'minecraft:diamond_block':
            block['state'] = HDV
    remapped_roles = {}
    for state, roles in data['role_materials'].items():
        state = HDV if state == 'minecraft:diamond_block' else state
        roles = [role for role in roles if role != 'minecraft:diamond_block']
        remapped_roles.setdefault(state, []).extend(roles)
    data['role_materials'] = {state: sorted(set(roles)) for state, roles in remapped_roles.items()}
    data['candidate_version'] = 'V3 HDV 双门架定轴校准'
    data['description'] = (
        '退火后的魂钢坯料沿隔振长床身通过两道不同跨距的加工门架：前段进行重载粗加工，'
        '后段完成微通道与轮廓精加工；西翼是低矮恒温计量室，东翼负责冷却过滤和切屑分流。'
        'HDV 致密压机械方块贯穿主门架与屋脊，深色钢制基座压低视觉重心，银灰传动件和洁净围护面'
        '衬出风息绿主结构。全部方块均取自当前增强版 2.9 实例或本模组已安装资源。'
    )
    data['construction_notes'] = {
        'origin': [0, 0, 0],
        'paste_anchor': [0, 0, 0],
        'schematic_offset': [0, 0, 0],
        'orientation': 'X 向东、Y 向上、Z 向南；接口朝北（-Z）。',
        'target_voltage': 'HDV',
        'earliest_build_stage': 'HDV',
        'build_stage_status': '设计目标为 HDV 阶段可建造；配方、研究与生存实机可达性待验收。',
        'controller_marker': '入口主框架位置使用 HDV 机械方块；这是未来控制器的坐标提示，不是已注册控制器。',
        'ports': '工业接口机械方块仅为惰性外观占位；Pattern 接入时需替换为具备能力的真实仓室。',
        'approval': 'V3 外观候选，待用户审核；未批准、未部署。',
    }
    return data


def _material_audit(counts):
    resources = Resources(instance=INSTANCE, project_resources=ROOT / 'src/main/resources')
    rows = []
    try:
        for state, count in sorted(counts.items()):
            if state in FORBIDDEN:
                raise AssertionError('forbidden state remains: ' + state)
            material = resources.material(state)
            magenta_pixels = 0
            for face in material['faces'].values():
                raw = base64.b64decode(face.split(',', 1)[1])
                image = Image.open(io.BytesIO(raw)).convert('RGBA')
                magenta_pixels += sum(
                    1 for red, green, blue, alpha in image.getdata()
                    if red > 180 and blue > 180 and green < 100 and alpha > 100
                )
            if magenta_pixels:
                raise AssertionError(f'{state} contains magenta texture pixels: {magenta_pixels}')
            block = state.split('[', 1)[0]
            namespace, name = block.split(':', 1)
            blockstate = f'assets/{namespace}/blockstates/{name}.json'
            rows.append({
                'block_state': state,
                'count': count,
                'role': PALETTE.get(state, 'existing GTCEu detail block'),
                'model': material['model'],
                'complete_cube': material['complete_cube'],
                'resource_source': resources.sources.get(blockstate),
                'magenta_pixels': magenta_pixels,
                'survival_recipe_and_stage': 'not verified',
            })
    finally:
        resources.close()
    return rows


def _write_html(data, audit):
    width, height, depth = data['size']
    page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>I16 · HDV 双门架定轴校准 V3</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#eff3f2;color:#182c30;font:16px/1.65 "Microsoft YaHei",sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 20px 50px}}header{{background:#123f3b;color:#eafff8;padding:24px;border-radius:8px}}
h1{{font-size:28px;margin:0 0 6px}}p{{margin:8px 0}}.summary{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}
.summary span{{background:white;border:1px solid #cbd8d6;border-radius:6px;padding:9px 12px}}
iframe{{width:100%;height:min(76vh,820px);min-height:560px;border:1px solid #b7c8c4;border-radius:6px;background:#172021}}
section{{border-top:1px solid #bdcfcb;padding-top:16px;margin-top:22px}}a{{color:#006d62}}.status{{background:#fff3df;border-left:4px solid #c27b24;padding:12px 16px}}
code{{overflow-wrap:anywhere}}@media(max-width:640px){{main{{padding:14px}}h1{{font-size:23px}}iframe{{height:68vh;min-height:440px}}}}
</style></head><body><main>
<header><div>HK3GTL · I16 · 外观候选 V3</div><h1>魂钢精密加工中心 · HDV 双门架定轴校准</h1>
<p>HDV 致密压机械方块作为主识别色。两道龙门跨越隔振长床身，连接粗加工、精加工、恒温计量、冷却过滤与切屑回收。</p></header>
<div class="summary"><span>目标建造阶段：<b>HDV</b></span><span>宽×深×高：<b>{width} × {depth} × {height}</b></span>
<span>实体方块：<b>{len(data['blocks']):,}</b></span><span>接口候选：<b>{len(data['ports'])}</b></span>
<span>HDV 主机壳：<b>{audit['material_counts'].get(HDV, 0):,}</b></span></div>
<p><a href="三维评审.html">打开完整三维剖切评审页</a> · <a href="{NAME}.nbt">NBT</a> · <a href="{NAME}.schem">Sponge Schematic</a> · <a href="设计与检查.json">检查记录</a> · <a href="材料依据.json">逐块材料依据</a></p>
<iframe src="三维评审.html" title="I16 HDV 三维评审"></iframe>
<section><h2>HDV 建造门槛</h2><div class="status">设计目标是玩家推进到 HDV 时就能完成这座机器。HDV 主机壳来自本模组已有方块；所有细节材质均为测试实例中已有 GTCEu 方块。当前报告只完成静态模型与 NBT 核验，主材研究、方块配方、材料生存可达性、I16 控制器与 Pattern 仍需游戏内验收。</div></section>
<section><h2>设计边界</h2><p>本候选只改 I16 的方块配色与标记：浅蓝/黄色机壳和钻石标记已移除；主框架采用现有 HDV 机械方块。接口方块仍只是惰性占位，不代表仓室能力已经实现。</p>
<p>已有 V2 的双龙门、长床身和侧翼功能布局仅作为几何参考。V3 尚未得到外观批准，也没有部署到游戏实例。</p></section>
<section><h2>输出文件</h2><p><a href="{ARCHIVE}">下载 V3 结构与预览包</a> · <a href="verification.json">自动核验结果</a></p></section>
</main></body></html>'''
    (OUT / 'index.html').write_text(page, encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    preview.TEST_INSTANCE = INSTANCE
    data = build()
    preview.package(data, OUT, 'i07', [
        '主框架使用 I16 对应的 HDV 机械方块；没有额外新造或改色方块',
        '浅蓝机壳、黄色机壳和钻石标记均已移除',
        '全部普通材质从增强版 2.9 实例解析并核验完整方块模型',
        '保留双门架长床身加工布局，新增颜色映射符合 HDV 目标阶段',
    ])
    base.lodestone_export(data, OUT, LOG)

    nbt_path = OUT / f'{NAME}.nbt'
    nbt_size, nbt_blocks = _read_structure(nbt_path)
    expected = {tuple(block['pos']): block['state'] for block in data['blocks']}
    if nbt_size != data['size'] or nbt_blocks != expected:
        raise AssertionError('Minecraft Builder NBT does not match the approved source block map')
    if any(state in FORBIDDEN for state in nbt_blocks.values()):
        raise AssertionError('forbidden palette marker remains in NBT')
    if sum(state == PORT for state in nbt_blocks.values()) != len(data['ports']):
        raise AssertionError('port marker count does not match port metadata')

    counts = collections.Counter(block['state'] for block in data['blocks'])
    tier_casings = [state for state in counts if state.startswith('hk3gtl:voltage_machine_casing_')]
    if tier_casings != [HDV]:
        raise AssertionError('I16 must use only its mapped HDV voltage casing')
    size_audit = base.require({'key': 'I16', 'size': nbt_size,
                               'blocks': [{'pos': list(pos)} for pos in nbt_blocks]})
    materials = _material_audit(counts)

    record_path = OUT / '设计与检查.json'
    record = json.loads(record_path.read_text(encoding='utf-8'))
    record['data'].update(data)
    record['audit'].update({
        'instance': str(INSTANCE),
        'candidate_version': data['candidate_version'],
        'approval': 'V3 候选，待用户审核；未批准、未部署。',
        'target_voltage': 'HDV',
        'minimum_executable_recipe_voltage': 'HDV（用户确认的设计基线；I16 正式执行配方尚未接入）',
        'earliest_build_stage': 'HDV',
        'build_stage_status': '静态方块清单符合 HDV 主机壳要求；材料/研究的生存可达性和实机搭建未验收。',
        'size_baseline': size_audit,
        'material_counts': dict(sorted(counts.items())),
        'hashes': {'nbt': hashlib.sha256(nbt_path.read_bytes()).hexdigest()},
        'checks': record['audit']['checks'] + [
            'Minecraft Builder Skill / Lodestone 输出 NBT 并逐格回读一致',
            'HDV 机械方块是唯一出现的本模组电压机壳，并用于门架主框架',
            '无钻石、浅蓝壳或黄色壳标记',
            '所有材质纹理与模型均从增强版 2.9 实例或本模组正式资源解析',
            '尺寸符合 I16 规划占地下限',
        ],
        'not_verified': [
            'HDV 主材研究、板材与机壳配方能否在玩家进入 HDV 前后稳定完成',
            '所有 GTCEu 细节方块的配方和生存模式阶段可达性',
            'I16 控制器、Pattern、实际仓室能力和配方执行',
            'Minecraft 内实际放置方向、结构成型与多人交互',
            '用户对 V3 外观候选的批准',
        ],
    })
    record['audit']['material_basis'] = materials
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    payload_path = OUT / 'data.js'
    encoded = json.loads(payload_path.read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    payload['audit'] = record['audit']
    payload['data'] = record['data']
    payload_path.write_text('window.HK3_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(
        json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9
    )).decode('ascii')) + ';', encoding='utf-8')
    (OUT / '材料依据.json').write_text(json.dumps({
        'scope': '增强版 2.9 实例材质模型与本模组已安装资源的静态解析；生存配方与阶段可达性未验证。',
        'target_voltage': 'HDV', 'earliest_build_stage': 'HDV', 'materials': materials,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    for filename, title in [('三维评审.html', 'I16 · 魂钢精密加工中心 · HDV 双门架定轴校准 V3'),
                            ('index.html', 'I16 · HDV 双门架定轴校准 V3')]:
        path = OUT / filename
        html = path.read_text(encoding='utf-8') if path.exists() else ''
        if filename == '三维评审.html':
            html = html.replace('<title>探测器精密校准台 · 自由设计候选</title>', f'<title>{title}</title>')
            html = html.replace('<h1>探测器精密校准台</h1>', '<h1>魂钢精密加工中心 · HDV 双门架定轴校准 V3</h1>')
            html = html.replace('自由设计候选', 'V3 外观候选')
            html = html.replace('待审预览', 'V3 外观候选')
            html = html.replace('全部69座', 'I16 检查记录')
            html = html.replace('href="设计与检查.json"', 'href="index.html"', 1)
            page_desc = data['description']
            import re
            html = re.sub(r'(<summary>本机建筑概念</summary><p>).*?(</p>)',
                          lambda match: match.group(1) + page_desc + match.group(2), html)
            path.write_text(html, encoding='utf-8')
        else:
            _write_html(data, record['audit'])

    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    manifest = {
        'machine': data['title'], 'candidate_version': data['candidate_version'],
        'target_voltage': 'HDV', 'earliest_build_stage': 'HDV',
        'size_xyz': nbt_size, 'size_wdh': [nbt_size[0], nbt_size[2], nbt_size[1]],
        'blocks': len(nbt_blocks), 'materials': len(counts), 'zones': len(data['zones']),
        'ports': len(data['ports']), 'instance': str(INSTANCE),
        'approval': '待用户审核；未批准、未部署。',
        'nbt_sha256': hashlib.sha256(nbt_path.read_bytes()).hexdigest(),
    }
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    verification = {
        'passed': True,
        'id': 'I16', 'version': data['candidate_version'],
        'target_voltage': 'HDV', 'earliest_build_stage': 'HDV',
        'size_xyz': nbt_size, 'size_wdh': [nbt_size[0], nbt_size[2], nbt_size[1]],
        'blocks': len(nbt_blocks), 'materials': len(counts), 'ports': len(data['ports']),
        'hdv_casing_count': counts[HDV], 'diamond_markers': counts['minecraft:diamond_block'],
        'checks': ['NBT and source block map match exactly', 'HDV casing is the only HK3GTL tier casing',
                   'no diamond/light-blue/yellow marker remains', '2.9 instance assets resolve'],
        'runtime_boundary': 'NBT/static texture checks only; survival stage access and in-game Pattern not tested.',
    }
    (OUT / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    archive_path = OUT / ARCHIVE
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path != archive_path:
                archive.write(path, path.relative_to(OUT))
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise AssertionError('archive validation failed')
    print(json.dumps({'output': str(OUT), 'blocks': len(nbt_blocks),
                      'materials': len(counts), 'hdv_casing_count': counts[HDV],
                      'size_wdh': manifest['size_wdh'], 'archive': str(archive_path),
                      'nbt_sha256': manifest['nbt_sha256']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
