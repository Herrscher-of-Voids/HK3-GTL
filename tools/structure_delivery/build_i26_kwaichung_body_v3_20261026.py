# -*- coding: utf-8 -*-
"""构建I26无货柜左右对称主体候选及三维评审。"""
from __future__ import annotations

import array
import base64
import collections
import gzip
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'tools/structure_delivery').is_dir())
sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
import i26_kwaichung_geometry_v2 as source
import i26_kwaichung_body_v3_20261026 as geometry

V2_BUILDER = ROOT / 'deliveries/I26_世界泡无人采掘调度台_葵涌自动化码头_V2_20261026/生成脚本/build_i26_kwaichung_terminal_v2_20261026.py'
spec = importlib.util.spec_from_file_location('i26_terminal_builder_base', V2_BUILDER)
if spec is None or spec.loader is None:
    raise RuntimeError('无法载入I26已有交付工具')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)

OUT = ROOT / 'deliveries/I26_世界泡无人采掘调度台_葵涌码头主体左右对称_V3_20261026'
VIEW = OUT / 'i26'
NAME = 'hk3gtl-i26-kwaichung-symmetric-terminal-body-v3-20261026'
TITLE = '世界泡无人采掘调度台 · 葵涌码头主体左右对称版'
VERSION = 'V3'

base.ROOT = ROOT
base.VIEWER = ROOT / 'deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023/i22'
base.OUT = OUT
base.VIEW = VIEW
base.NAME = NAME
base.TITLE = TITLE
base.CELLS = geometry.CELLS
base.PORT_CELLS = geometry.CELLS
base.CONTAINER_COLORS = ()
base.VIEWER_BUILDER = ROOT / 'tools/structure_delivery/build_i26_terminal_viewer_v2_20261026.mjs'

_report_page = base.report_page
_viewer_page = base.viewer_page


def report_page(data: dict, check: dict) -> str:
    page = _report_page(data, check).replace('V2', VERSION)
    page = page.replace(f'href="{OUT.name}.zip"', f'href="../{OUT.name}.zip"')
    page = page.replace(
        '参考葵涌货柜码头的岸桥、堆场与闸口物流；中央只保留一条无人采掘目标航线。',
        '以钻石主控X=166为中轴，港池、岸桥、场桥、仓库与调度塔构成左右镜像主体；本版暂不放置集装箱。')
    page = page.replace(
        '形体参考葵涌码头的港池岸线、高密度多色货柜、岸桥与陆侧仓储：海侧保留单一装置泊位，场桥和六辆无人牵引车服务货柜巷道，两座装卸仓库把分拣与检疫设备收进完整建筑。',
        '形体参考葵涌码头的港池、岸桥、场桥和陆侧仓储：海侧保留中央单目标泊位，七座场桥、八台无人牵引头、双仓及调度塔围绕主控轴严格镜像。货柜箱体暂缓加入，以先审主体比例和结构节奏。')
    page = page.replace(
        '单一作业泊位朝向港池，四座岸桥沿岸线排列；箱垛、场桥、中央航务塔与分拣闸口组成一条自动化物流链。每座岸桥服务同一条目标航线，不表示多目标并行。',
        '单一作业泊位、四座岸桥、七座场桥、八台牵引头、两座仓库和中央航务塔均以X=166逐格镜像。本版不放置集装箱，先评审建筑主体。')
    page = page.replace(
        '候选仅完成结构文件、实际资源材质和建筑指标核验；实际EU额定、Pattern、端口能力、配方、游戏内成型与运行均未验证。本版待另一个我审阅，未批准、未归档确认版、未接入实例。',
        '候选仅完成结构文件、实际资源材质和建筑指标核验；实际EU额定、Pattern、端口能力、配方、游戏内成型与运行均未验证。本版待另一个我审阅，未批准、未归档确认版、未接入实例。')
    return page


def viewer_page(data: dict, check: dict) -> str:
    page = _viewer_page(data, check).replace('V2', VERSION)
    page = page.replace(
        '单一作业泊位朝向港池，四座岸桥沿岸线排列；箱垛、场桥、中央航务塔与分拣闸口组成一条自动化物流链。每座岸桥服务同一条目标航线，不表示多目标并行。',
        '四座岸桥、七座场桥、八台无人牵引头、双仓和中央调度塔以X=166逐格镜像。当前先审无货柜主体，箱体暂缓加入。')
    page = page.replace(
        'V2候选：葵涌码头式泊位、岸桥、堆场和调度塔；未获批准、未接入游戏。',
        'V3主体候选：控制器X=166为镜像轴，未放置货柜箱体；未获批准、未接入游戏。')
    return page


def update_static_images(data: dict, check: dict) -> None:
    iso_path = OUT / '等轴预览.png'
    image = Image.open(iso_path).convert('RGB')
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, 48), fill='#101720')
    draw.text((18, 10), 'I26 葵涌码头主体左右对称版 · V3', font=base.font(22), fill='#e7e5e0')
    draw.rectangle((0, image.height - 46, image.width, image.height), fill='#101720')
    draw.text((18, image.height - 37),
              f'{base.W} × {base.D} × {base.H} | {check["blocks"]:,} 方块 | X=166镜像核验通过 | 待审候选',
              font=base.font(19), fill='#d0d6d9')
    image.save(iso_path)

    top_path = OUT / '俯视布局.png'
    image = Image.open(top_path).convert('RGB')
    draw = ImageDraw.Draw(image)
    draw.rectangle((1065, 397, image.width - 8, 580), fill='#131b25')
    for index, text in enumerate((
        'X=166主控中轴 · 左右逐格镜像',
        '四座岸桥 · 七座场桥',
        '八台无人集卡 · 两座陆勤仓库',
        '无货柜箱体 · 连续作业坪',
    )):
        draw.text((1080, 408 + index * 39), text, font=base.font(19), fill='#cbd7df')
    image.save(top_path)


def main() -> None:
    identity_file = OUT / 'manifest.json'
    if OUT.exists() and any(OUT.iterdir()):
        existing_files = [path for path in OUT.rglob('*') if path.is_file()]
        if existing_files and not identity_file.is_file():
            raise FileExistsError(f'拒绝覆盖身份未知的I26交付：{OUT}')
        if identity_file.is_file():
            identity = json.loads(identity_file.read_text(encoding='utf-8'))
            if not (identity.get('key') == 'I26' and identity.get('candidate_version') == VERSION
                    and identity.get('status') == 'candidate_waiting_user_review'):
                raise FileExistsError(f'拒绝覆盖身份不匹配的I26交付：{OUT}')

    OUT.mkdir(parents=True, exist_ok=True)
    VIEW.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    data = geometry.build()
    body_count = geometry.assert_left_right_symmetry(data)
    check = base.audit(data)
    check['left_right_symmetry'] = {
        'axis_x': geometry.CX,
        'mirror_transform': 'x\' = 332 - x',
        'mismatched_voxels': 0,
        'symmetric_voxels_checked': body_count,
        'containers_included': 0,
    }
    check['composition'] = data['composition']
    check['checks'].append('按X=166逐格镜像核验，所有方块ID完全一致；本版货柜方块为0。')
    check['checks'] = [item.replace('7个工业接口候选', '8个成对工业接口候选') for item in check['checks']]

    counts = collections.Counter(block['state'] for block in data['blocks'])
    states = sorted(counts)
    cargo_palette = set(source.CONTAINER_COLORS) - {source.YELLOW}
    if cargo_palette.intersection(states):
        raise ValueError('V3材料表仍含货柜专用颜色方块')
    materials, sources, packs, instance_proof = base.resource_materials(states)
    states, groups, hashes = base.export(data, VIEW)
    check['nbt_schem_sha256'] = hashes
    check['source_instance'] = str(base.INSTANCE)
    check['instance_proof'] = instance_proof
    check['enabled_file_resource_packs'] = packs
    check['material_resource_sources'] = sources
    check['marker_textures_are_distinct'] = all(
        next(m for m in materials if m['state'] == marker)['faces'] !=
        next(m for m in materials if m['state'] == base.QAV)['faces']
        for marker in (base.PORT, base.CONTROL))
    payload_data = {key: value for key, value in data.items() if key not in ('blocks', 'zone_descriptions')}
    visible_groups = base.build_surface_groups(data, states)
    check['viewer_surface_faces'] = sum(len(face) for state in visible_groups for face in state)
    check['viewer_draw_triangles'] = check['viewer_surface_faces'] * 2
    check['viewer_instance_matrix_bytes'] = check['viewer_surface_faces'] * 16 * 4
    payload = {
        'data': payload_data, 'palette': states, 'surfaceGroups': visible_groups,
        'blockCount': len(data['blocks']), 'materials': materials, 'audit': check,
        'names': {state: state.split(':', 1)[1].replace('_', ' ') for state in states},
    }
    encoded = base64.b64encode(gzip.compress(
        json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), compresslevel=9)).decode('ascii')
    (VIEW / 'data.js').write_text('window.HK3_PAYLOAD="' + encoded + '";\n', encoding='utf-8')
    decoded = json.loads(gzip.decompress(base64.b64decode(encoded)))
    reconstructed = {
        ((index % base.W), (index // (base.W * base.D)), (index // base.W) % base.D): state
        for state, group in zip(states, groups) for index in group
    }
    expected = {tuple(block['pos']): block['state'] for block in data['blocks']}
    assert reconstructed == expected
    assert decoded['blockCount'] == len(data['blocks']) and decoded['surfaceGroups'] == visible_groups
    del decoded, reconstructed, groups, visible_groups
    check['viewer_payload_exact_cell_readback'] = True
    subprocess.run(['node', str(base.VIEWER_BUILDER), str(VIEW)], cwd=ROOT, check=True)
    base.render(data, materials, OUT)
    base.make_static_reports(data, materials, check)
    update_static_images(data, check)
    (VIEW / '三维评审.html').write_text(viewer_page(data, check), encoding='utf-8')
    (OUT / 'index.html').write_text(report_page(data, check), encoding='utf-8')

    base.write_json(OUT / '设计依据.json', [
        {'path': 'deliveries/I26_世界泡无人采掘调度台_葵涌自动化码头_V2_20261026/manifest.json',
         'fact': '仅复用已评审候选的功能分区与现行材质资源表；本版重新构建无货柜左右对称主体。'},
        {'path': 'rule/当前多方块设计规则.md',
         'fact': '执行QAV主机壳、居中钻石主控、接口自然融合和I26电压递增规则。'},
        {'path': 'https://www.hkmpdb.gov.hk/en/port.html',
         'fact': '港池岸线、岸桥和岸后堆场作为主体设计参照。'},
        {'path': 'https://www.hit.com.hk/en/Innovation/Improving-Efficiency.html',
         'fact': '远程吊机、场内车辆路线和自动化堆场作为主体设计参照。'},
    ])
    base.write_json(OUT / '设计与检查.json', {
        'design': {key: value for key, value in data.items() if key not in ('blocks', 'zone_descriptions')},
        'audit': check,
    })
    base.write_json(OUT / 'manifest.json', {
        'generator': Path(__file__).name, 'key': 'I26', 'title': TITLE, 'candidate_version': VERSION,
        'status': 'candidate_waiting_user_review', 'approved': False,
        'target_voltage': 'QAV', 'voltage_mapping': 'V08 / tier22',
        'size_xyz': [base.W, base.H, base.D], 'size_wdh': [base.W, base.D, base.H],
        'minimum_wdh': [49, 81, 37], 'blocks': check['blocks'],
        'unique_materials': check['unique_materials'], 'controller': data['controller'],
        'ports': data['ports'], 'composition': data['composition'],
        'left_right_symmetry': check['left_right_symmetry'],
        'source_instance': str(base.INSTANCE), 'source_instance_version': instance_proof['instance_version'],
        'nbt_sha256': hashes['nbt'], 'schem_sha256': hashes['schem'],
        'claim_boundary': '仅建筑候选；无货柜；未验证实际EU、正式Pattern、端口功能或游戏内运行。',
    })
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    shutil.copy2(Path(__file__).with_name('i26_kwaichung_body_v3_20261026.py'),
                 OUT / '生成脚本' / 'i26_kwaichung_body_v3_20261026.py')
    shutil.copy2(base.VIEWER_BUILDER, OUT / '生成脚本' / base.VIEWER_BUILDER.name)

    bundle = OUT.with_suffix('.zip')
    bundle_files = {bundle.name, bundle.with_suffix('.zip.sha256').name}
    files = {path.relative_to(OUT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(OUT.rglob('*')) if path.is_file() and path.name not in bundle_files | {'verification.json'}}
    check['files_sha256_before_verification'] = files
    base.write_json(OUT / 'verification.json', check)
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path.name not in bundle_files:
                archive.write(path, path.relative_to(OUT.parent).as_posix())
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        for path in OUT.rglob('*'):
            if path.is_file() and path.name not in bundle_files:
                assert archive.read(f'{OUT.name}/{path.relative_to(OUT).as_posix()}') == path.read_bytes()
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    bundle.with_suffix('.zip.sha256').write_text(digest + '\n', encoding='ascii')
    print(json.dumps({'output': str(OUT), 'blocks': check['blocks'], 'materials': check['unique_materials'],
                      'symmetry': check['left_right_symmetry'], 'composition': data['composition'],
                      'triangles': check['viewer_draw_triangles'], 'sha256': digest}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
