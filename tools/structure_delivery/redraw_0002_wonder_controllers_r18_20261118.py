from pathlib import Path
from datetime import datetime, timezone, timedelta
import base64
import gzip
import hashlib
import html
import io
import json
import shutil
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import build_controller_texture_candidates_20261026 as faces
from w11_f5_controller import projected_surfaces
from wonder_controller_geometry_0002_r18 import scene_geometry

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0002贴图材质_奇观控制器_R18_20261118'
LOG = ROOT / 'logs/wonder-controller-textures-0002-r18-20261118'
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
STRUCTURES = ROOT / 'src/main/resources/data/hk3gtl/structures'
SCENES = {'W05': 'w05_r3', 'W06': 'w06_author', 'W07': 'w07_n2', 'W08': 'w08_a5',
          'W09': None, 'W10': 'w10_a3', 'W12': 'w12_a3', 'W13': 'w13_t2_m1',
          'W14': 'w14_e3', 'W15': 'w15_b1'}
TITLES = ['长风·理想流体环流阵', '永霜·极低温凝态工厂', '生息·物质再生方舟',
          '劫焰·恒星熔铸炉', '万象·文明共识矩阵', '坠星·引力奇点铸造井',
          '戒律·全域能量约束壁', '蚀界·自演算研究母机', '终序·世界泡轮回引擎', '凌霄·树海朝觐圣座']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')


def source_scene(stem, approved):
    if stem:
        source = ASSETS / 'models/scene' / (stem + '.json.gz')
        with gzip.open(source, 'rt', encoding='utf-8') as stream:
            scene = json.load(stream)
    if not stem or scene['data'].get('native_dynamic_components_only'):
        source = ROOT / approved['source'] / 'data.js'
        encoded = json.loads(source.read_text('utf-8').split('=', 1)[1].strip().rstrip(';'))
        scene = json.loads(gzip.decompress(base64.b64decode(encoded)))
    return scene, source


def tree_sea_surfaces():
    source = ASSETS / 'wonder/w15_book_fx.bin.gz'
    stream = io.BytesIO(gzip.decompress(source.read_bytes()))
    stream.read(4)
    surfaces = []
    view = np.asarray([1, .35, 1], dtype=np.float32)
    for width in [.32, .25, .35, .42]:
        count = struct.unpack('>i', stream.read(4))[0]
        data = np.frombuffer(stream.read(count * 16), dtype=[('pos', '>f4', 3), ('color', '>u4')])
        lines = data['pos'].astype(np.float32).reshape(-1, 2, 3)
        side = np.cross(lines[:, 1] - lines[:, 0], view)
        side *= (width / np.linalg.norm(side, axis=1))[:, None]
        surfaces.append(np.stack([lines[:, 0] - side, lines[:, 1] - side,
                                  lines[:, 1] + side, lines[:, 0] + side], axis=1))
    vertices = np.concatenate(surfaces)
    return vertices, dict(source=source.relative_to(ROOT).as_posix(), sha256=sha(source),
                          method='正式树枝、光根、菱形节点及海旋涡波纹线段的静态投影', surfaces=len(vertices))


def geometry_image(vertices, path):
    depth, valid, edge, ridges, *_ = projected_surfaces(vertices, 600, 420, 12)
    rgb = np.full((420, 600, 3), (9, 20, 33), dtype=np.uint8)
    values = depth[valid]
    t = (values - values.min()) / max(float(values.max() - values.min()), 1)
    rgb[valid] = np.stack((35 + t * 28, 80 + t * 57, 102 + t * 64), axis=1).astype(np.uint8)
    rgb[ridges], rgb[edge] = (103, 186, 199), (164, 223, 226)
    Image.fromarray(rgb).save(path)


def preview(entries):
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    sheet = Image.new('RGB', (1200, len(entries) * 240 + 58), '#101923')
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 12), '0002 · 奇观控制器 R18 · 整机投影 / 空闲 / 运行 / 暂停', font=font, fill='#e6eef4')
    rows = []
    for i, entry in enumerate(entries):
        y = 55 + i * 240
        draw.text((18, y), entry['role'] + '  ' + entry['name'], font=font, fill='#e6eef4')
        sheet.paste(Image.open(OUT / entry['geometry']).resize((285, 199)), (18, y + 30))
        cells = '<td><img class="geometry" src="' + entry['geometry'] + '"></td>'
        for j, state in enumerate(faces.STATE_SUFFIX):
            path = entry['textures'][state]['preview']
            sheet.paste(Image.open(OUT / path).convert('RGB').resize((192, 192), Image.Resampling.NEAREST), (330 + j * 280, y + 32))
            cells += '<td><img class="face" src="' + path + '"></td>'
        rows.append('<tr><th>' + html.escape(entry['role'] + ' · ' + entry['name']) + '<br><small>'
                    + html.escape(entry['version']) + '<br>' + ' × '.join(map(str, entry['size_xyz']))
                    + '<br>' + format(entry['blocks'], ',') + ' 方块</small></th>' + cells + '</tr>')
    sheet.save(OUT / 'overview.png')
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>0002 奇观控制器 R18</title><style>body{margin:24px;background:#101923;color:#e6eef4;font:15px/1.6 system-ui,"Microsoft YaHei",sans-serif}a{color:#8bdde5}table{border-collapse:collapse;width:100%;min-width:960px}th,td{border:1px solid #3c5062;padding:12px;text-align:center}th{font-weight:500}small{color:#a7becd}.geometry{width:300px;max-width:100%}.face{width:192px;image-rendering:pixelated}.scroll{overflow:auto}</style><h1>0002 · 奇观控制器 R18</h1><p>10台控制器按各自现行完整结构生成64×64三态面板，源码绑定已更新。整机栏显示相同几何的放大投影，供核对轮廓。贴图待负责人查看。</p><p>W07采用N2方舟，W09采用F2山观兵装矩阵，W13采用T2-M1电视山，W14采用E3行星发动机与七维度地貌，W15采用B1树海巨书。</p><p><a href="overview.png">贴图总览</a> · <a href="manifest.json">来源、绑定与哈希</a></p><div class="scroll"><table><thead><tr><th>奇观 / 结构</th><th>整机投影</th><th>空闲</th><th>运行</th><th>暂停</th></tr></thead><tbody>'''
    page += ''.join(rows) + '</tbody></table></div><p>2026-11-18 · 对话0002 · 01a1d68a-a994-7ac0-a48a-54c0f98fd54e · 源码接入，待后续正式构建交付。</p></html>'
    (OUT / 'index.html').write_text(page, 'utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    original_projection = faces.projected_geometry
    entries = []
    for (role, stem), title in zip(SCENES.items(), TITLES):
        metadata = STRUCTURES / (role.lower() + '_approved.json')
        approved = json.loads(metadata.read_text('utf-8'))
        scene, source = source_scene(stem, approved)
        vertices, controller = scene_geometry(scene)
        controller = approved['controller_source_xyz']
        del scene
        effects = None
        if role == 'W15':
            effect_vertices, effects = tree_sea_surfaces()
            vertices = np.concatenate([vertices, effect_vertices])
        folder = OUT / role.lower()
        target = ASSETS / 'textures/block/overlay' / (role.lower() + '_appearance_0002_r18')
        folder.mkdir(exist_ok=True)
        target.mkdir(exist_ok=True)
        geometry_image(vertices, folder / 'whole-machine.png')
        projected = projected_surfaces(vertices)
        faces.projected_geometry = lambda points, width, height, margin=1: projected
        textures = {}
        for state, suffix in faces.STATE_SUFFIX.items():
            image, pattern = faces.candidate_face(vertices.reshape(-1, 3), [], controller, state)
            path = target / ('overlay_front' + suffix + '.png')
            image.save(path)
            shutil.copy2(path, folder / path.name)
            textures[state] = dict(resource=path.relative_to(ROOT).as_posix(),
                                   preview=role.lower() + '/' + path.name, sha256=sha(path))
        faces.projected_geometry = original_projection
        entry = dict(role=role, name=title, machine=approved['controller'], version=approved['version'],
                     source=source.relative_to(ROOT).as_posix(), source_sha256=sha(source),
                     metadata=metadata.relative_to(ROOT).as_posix(), metadata_sha256=sha(metadata),
                     blueprint=approved['blueprint'], blueprint_sha256=sha(STRUCTURES / (role.lower() + '_candidate.bin.gz')),
                     size_xyz=approved['size_xyz'], blocks=approved['block_count'], surfaces=len(vertices),
                     controller_source_xyz=list(map(float, controller)), geometry=role.lower() + '/whole-machine.png',
                     overlay='hk3gtl:block/overlay/' + target.name, geometry_pattern_sha256=pattern, textures=textures)
        if effects:
            entry['effect_geometry'] = effects
        entries.append(entry)
        print(json.dumps(dict(role=role, surfaces=len(vertices), textures=3), ensure_ascii=False), flush=True)
        del vertices, projected
    manifest = dict(created_at=datetime.now(timezone(timedelta(hours=-5))).isoformat(), thread='0002贴图材质',
                    thread_id='01a1d68a-a994-7ac0-a48a-54c0f98fd54e', entries=entries,
                    method='完整现行整机合面填充投影，复用R7原生64×64金属面板及三态显示。',
                    art_status='待负责人查看', source_integration=True, jar_built=False, installed=False)
    save(OUT / 'manifest.json', manifest)
    preview(entries)
    save(LOG / 'textures.json', manifest)


if __name__ == '__main__':
    main()
